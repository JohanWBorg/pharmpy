from dataclasses import dataclass
from typing import Optional, Union

import pharmpy.tools.modelsearch.algorithms as algorithms
from pharmpy.deps import pandas as pd
from pharmpy.internals.fn.signature import with_same_arguments_as
from pharmpy.internals.fn.type import with_runtime_arguments_type_check
from pharmpy.model import Model
from pharmpy.results import ModelfitResults
from pharmpy.tools import get_model_features, summarize_modelfit_results
from pharmpy.tools.common import RANK_TYPES, ToolResults, create_results
from pharmpy.tools.mfl.parse import ModelFeatures
from pharmpy.tools.modelfit import create_fit_workflow
from pharmpy.workflows import Task, Workflow, WorkflowBuilder, call_workflow

from ..mfl.filter import modelsearch_statement_types
from ..mfl.parse import parse as mfl_parse


def create_workflow(
    search_space: Union[str, ModelFeatures],
    algorithm: str,
    iiv_strategy: str = 'absorption_delay',
    rank_type: str = 'bic',
    cutoff: Optional[Union[float, int]] = None,
    results: Optional[ModelfitResults] = None,
    model: Optional[Model] = None,
):
    """Run Modelsearch tool. For more details, see :ref:`modelsearch`.

    Parameters
    ----------
    search_space : str, ModelFeatures
        Search space to test. Either as a string or a ModelFeatures object.
    algorithm : str
        Algorithm to use (e.g. exhaustive)
    iiv_strategy : str
        If/how IIV should be added to candidate models. Possible strategies are 'no_add',
        'add_diagonal', 'fullblock', or 'absorption_delay'. Default is 'absorption_delay'
    rank_type : str
        Which ranking type should be used (OFV, AIC, BIC, mBIC). Default is BIC
    cutoff : float
        Cutoff for which value of the ranking function that is considered significant. Default
        is None (all models will be ranked)
    results : ModelfitResults
        Results for model
    model : Model
        Pharmpy model

    Returns
    -------
    ModelSearchResults
        Modelsearch tool result object

    Examples
    --------
    >>> from pharmpy.modeling import load_example_model
    >>> from pharmpy.tools import run_modelsearch, load_example_modelfit_results
    >>> model = load_example_model("pheno")
    >>> results = load_example_modelfit_results("pheno")
    >>> run_modelsearch('ABSORPTION(ZO);PERIPHERALS(1)', 'exhaustive', results=results, model=model) # doctest: +SKIP

    """
    wb = WorkflowBuilder(name='modelsearch')
    start_task = Task(
        'start_modelsearch',
        start,
        search_space,
        algorithm,
        iiv_strategy,
        rank_type,
        cutoff,
        results,
        model,
    )
    wb.add_task(start_task)
    task_results = Task('results', _results)
    wb.add_task(task_results, predecessors=[start_task])
    return Workflow(wb)


def start(
    context,
    search_space,
    algorithm,
    iiv_strategy,
    rank_type,
    cutoff,
    results,
    model,
):
    wb = WorkflowBuilder()

    start_task = Task('start_modelsearch', _start, model)
    wb.add_task(start_task)

    algorithm_func = getattr(algorithms, algorithm)

    if isinstance(search_space, str):
        mfl_statements = mfl_parse(search_space, mfl_class=True)
    else:
        mfl_statements = search_space

    # Add base model task
    model_mfl = get_model_features(model, supress_warnings=True)
    model_mfl = ModelFeatures.create_from_mfl_string(model_mfl)
    if not mfl_statements.contain_subset(model_mfl):
        base_task = Task("create_base_model", create_base_model, mfl_statements)
        wb.add_task(base_task, predecessors=start_task)

        base_fit = create_fit_workflow(n=1)
        wb.insert_workflow(base_fit, predecessors=base_task)
        base_fit = base_fit.output_tasks
    else:
        # Always create base, even if same as input for proper
        # post-process behaviour.
        base_fit = start_task

    task_result = Task(
        'results',
        post_process,
        rank_type,
        cutoff,
    )

    # Filter the mfl_statements from base model attributes
    mfl_funcs = filter_mfl_statements(mfl_statements, create_base_model(mfl_statements, model))

    # TODO : Implement task for filtering the search space instead
    wf_search, candidate_model_tasks = algorithm_func(mfl_funcs, iiv_strategy)
    if candidate_model_tasks:
        # Clear base description to not interfere with candidate models
        base_clear_task = Task("Clear_base_description", clear_description)
        wb.add_task(base_clear_task, predecessors=base_fit)

        wb.insert_workflow(wf_search, predecessors=base_clear_task)

        if base_fit != start_task:
            wb.add_task(task_result, predecessors=[start_task] + base_fit + candidate_model_tasks)
        else:
            wb.add_task(task_result, predecessors=[start_task] + candidate_model_tasks)
    else:
        if base_fit != start_task:
            wb.add_task(task_result, predecessors=[start_task] + base_fit + candidate_model_tasks)
        else:
            wb.add_task(task_result, predecessors=[start_task] + candidate_model_tasks)

    res = call_workflow(wb, 'run_candidate_models', context)

    return res


def _start(model):
    return model


def _results(res):
    return res


def clear_description(model):
    return model.replace(description="")


def filter_mfl_statements(mfl_statements: ModelFeatures, model: Model):
    ss_funcs = mfl_statements.convert_to_funcs()
    model_mfl = ModelFeatures.create_from_mfl_string(get_model_features(model))
    model_funcs = model_mfl.convert_to_funcs()
    res = {k: ss_funcs[k] for k in set(ss_funcs) - set(model_funcs)}
    return {k: v for k, v in sorted(res.items(), key=lambda x: (x[0][0], x[0][1]))}


def _update_results(base):
    """
    Changes the name and description of the connected ModelfitResults object
    to match the one found in the model object"""
    base_results = base.modelfit_results
    # Workaround due to not having a replace method
    return base.replace(
        modelfit_results=ModelfitResults(
            name=base.name,
            description=base.description,
            ofv=base_results.ofv,
            ofv_iterations=base_results.ofv_iterations,
            parameter_estimates=base_results.parameter_estimates,
            parameter_estimates_sdcorr=base_results.parameter_estimates_sdcorr,
            parameter_estimates_iterations=base_results.parameter_estimates_iterations,
            covariance_matrix=base_results.covariance_matrix,
            correlation_matrix=base_results.correlation_matrix,
            precision_matrix=base_results.precision_matrix,
            standard_errors=base_results.standard_errors,
            standard_errors_sdcorr=base_results.standard_errors_sdcorr,
            relative_standard_errors=base_results.relative_standard_errors,
            minimization_successful=base_results.minimization_successful,
            minimization_successful_iterations=base_results.minimization_successful_iterations,
            estimation_runtime=base_results.estimation_runtime,
            estimation_runtime_iterations=base_results.estimation_runtime_iterations,
            individual_ofv=base_results.individual_ofv,
            individual_estimates=base_results.individual_estimates,
            individual_estimates_covariance=base_results.individual_estimates_covariance,
            residuals=base_results.residuals,
            predictions=base_results.predictions,
            runtime_total=base_results.runtime_total,
            termination_cause=base_results.termination_cause,
            termination_cause_iterations=base_results.termination_cause,
            function_evaluations=base_results.function_evaluations,
            function_evaluations_iterations=base_results.function_evaluations_iterations,
            significant_digits=base_results.significant_digits,
            significant_digits_iterations=base_results.significant_digits_iterations,
            log_likelihood=base_results.log_likelihood,
            log=base_results.log,
            evaluation=base_results.evaluation,
        )
    )


def create_base_model(ss, model):
    base = model

    model_mfl = get_model_features(model, supress_warnings=True)
    model_mfl = ModelFeatures.create_from_mfl_string(model_mfl)
    added_features = ""
    lnt = model_mfl.least_number_of_transformations(ss)
    for name, func in lnt.items():
        base = func(base)
        added_features += f';{name[0]}({name[1]})'
    # UPDATE_DESCRIPTION
    # FIXME : Need to be its own parent if the input model shouldn't be ranked with the others
    base = base.replace(name="BASE", description=added_features[1:], parent_model="BASE")

    return base


def post_process(rank_type, cutoff, *models):
    res_models = []
    input_model = None
    base_model = False
    for model in models:
        if not model.name.startswith('modelsearch_run') and model.name == "BASE":
            base_model = True
            input_model = model
            base_model = model
        elif not model.name.startswith('modelsearch_run') and model.name != "BASE":
            user_input_model = model
        else:
            res_models.append(model)
    if not base_model:
        input_model = user_input_model
        base_model = user_input_model
    if not input_model:
        raise ValueError('Error in workflow: No input model')

    summary_user_input = summarize_modelfit_results(user_input_model.modelfit_results)
    if user_input_model != base_model:
        summary_base = summarize_modelfit_results(base_model.modelfit_results)
        summary_models = [summary_user_input, summary_base]
        keys = [0, 1]
    else:
        summary_models = [summary_user_input]
        keys = [0]

    if res_models:
        summary_candidates = summarize_modelfit_results(
            [model.modelfit_results for model in res_models]
        )
        summary_models = pd.concat(
            summary_models + [summary_candidates], keys=keys + [keys[-1] + 1], names=['step']
        )
    else:
        summary_models = pd.concat(summary_models, keys=keys + [keys[-1] + 1], names=['step'])

    return create_results(
        ModelSearchResults,
        input_model,
        base_model,
        res_models,
        rank_type,
        cutoff,
        summary_models=summary_models,
    )


@with_runtime_arguments_type_check
@with_same_arguments_as(create_workflow)
def validate_input(
    search_space,
    algorithm,
    iiv_strategy,
    rank_type,
    model,
):
    if not hasattr(algorithms, algorithm):
        raise ValueError(
            f'Invalid `algorithm`: got `{algorithm}`, must be one of {sorted(dir(algorithms))}.'
        )

    if rank_type not in RANK_TYPES:
        raise ValueError(
            f'Invalid `rank_type`: got `{rank_type}`, must be one of {sorted(RANK_TYPES)}.'
        )

    if iiv_strategy not in algorithms.IIV_STRATEGIES:
        raise ValueError(
            f'Invalid `iiv_strategy`: got `{iiv_strategy}`,'
            f' must be one of {sorted(algorithms.IIV_STRATEGIES)}.'
        )

    try:
        statements = mfl_parse(search_space)
    except:  # noqa E722
        raise ValueError(f'Invalid `search_space`, could not be parsed: "{search_space}"')

    bad_statements = list(
        filter(lambda statement: not isinstance(statement, modelsearch_statement_types), statements)
    )

    if bad_statements:
        raise ValueError(
            f'Invalid `search_space`: found unknown statement of type {type(bad_statements[0]).__name__}.'
        )


@dataclass(frozen=True)
class ModelSearchResults(ToolResults):
    pass
