import pytest

from pharmpy.internals.fs.cwd import chdir
from pharmpy.modeling import set_bolus_absorption
from pharmpy.results import ModelfitResults
from pharmpy.tools import read_results
from pharmpy.workflows import Task, Workflow, execute_workflow


@pytest.mark.filterwarnings("ignore:.*Port .* is already in use.:UserWarning")
def test_execute_workflow_constant(tmp_path):
    a = lambda: 1  # noqa E731
    t1 = Task('t1', a)
    wf = Workflow([t1])

    with chdir(tmp_path):
        res = execute_workflow(wf)

    assert res == a()


@pytest.mark.filterwarnings("ignore:.*Port .* is already in use.:UserWarning")
def test_execute_workflow_unary(tmp_path):
    a = lambda: 2  # noqa E731
    f = lambda x: x**2  # noqa E731
    t1 = Task('t1', a)
    t2 = Task('t2', f)
    wf = Workflow([t1])
    wf.add_task(t2, predecessors=[t1])

    with chdir(tmp_path):
        res = execute_workflow(wf)

    assert res == f(a())


@pytest.mark.filterwarnings("ignore:.*Port .* is already in use.:UserWarning")
def test_execute_workflow_binary(tmp_path):
    a = lambda: 1  # noqa E731
    b = lambda: 2  # noqa E731
    f = lambda x, y: x + y  # noqa E731
    t1 = Task('t1', a)
    t2 = Task('t2', b)
    t3 = Task('t3', f)
    wf = Workflow([t1, t2])
    wf.add_task(t3, predecessors=[t1, t2])

    with chdir(tmp_path):
        res = execute_workflow(wf)

    assert res == f(a(), b())


@pytest.mark.filterwarnings("ignore:.*Port .* is already in use.:UserWarning")
def test_execute_workflow_parallel(tmp_path):
    n = 10
    f = lambda x: x**2  # noqa E731
    layer1 = list(map(lambda i: Task(f'x{i}', lambda: i), range(n)))
    layer2 = list(map(lambda i: Task(f'f{i}', f), range(n)))
    wf = Workflow(layer1)
    wf.insert_workflow(Workflow(layer2))
    wf.add_task(Task('g', lambda *y: y), predecessors=wf.output_tasks)

    with chdir(tmp_path):
        res = execute_workflow(wf)

    assert res == tuple(map(f, range(n)))


@pytest.mark.filterwarnings("ignore:.*Port .* is already in use.:UserWarning")
def test_execute_workflow_set_bolus_absorption(load_model_for_test, testdata, tmp_path):
    model1 = load_model_for_test(testdata / 'nonmem' / 'modeling' / 'pheno_advan1.mod')
    model2 = load_model_for_test(testdata / 'nonmem' / 'modeling' / 'pheno_advan2.mod')
    advan1_before = model1.model_code

    t1 = Task('init', lambda x: x.copy(), model2)
    t2 = Task('update', set_bolus_absorption)
    t3 = Task('postprocess', lambda x: x)
    wf = Workflow([t1])
    wf.insert_workflow(Workflow([t2]))
    wf.insert_workflow(Workflow([t3]))

    with chdir(tmp_path):
        res = execute_workflow(wf)

    assert res.model_code == advan1_before


@pytest.mark.filterwarnings("ignore:.*Port .* is already in use.:UserWarning")
def test_execute_workflow_fit_mock(load_model_for_test, testdata, tmp_path):
    models = (
        load_model_for_test(testdata / 'nonmem' / 'modeling' / 'pheno_advan1.mod'),
        load_model_for_test(testdata / 'nonmem' / 'modeling' / 'pheno_advan2.mod'),
    )
    indices = range(len(models))
    ofvs = [(-17 + x) ** 2 - x + 3 for x in indices]

    def fit(ofv, m):
        m.modelfit_results = ModelfitResults(ofv=ofv)
        return m

    init = map(lambda i: Task(f'init_{i}', lambda x: x.copy(), models[i]), indices)
    process = map(lambda i: Task(f'fit{i}', fit, ofvs[i]), indices)
    wf = Workflow(init)
    wf.insert_workflow(Workflow(process))
    gather = Task('gather', lambda *x: x)
    wf.insert_workflow(Workflow([gather]))

    with chdir(tmp_path):
        res = execute_workflow(wf)

    for orig, fitted, ofv in zip(models, res, ofvs):
        assert orig.modelfit_results.ofv == ofv
        assert fitted.modelfit_results.ofv == ofv
        assert orig.modelfit_results == fitted.modelfit_results


@pytest.mark.filterwarnings("ignore:.*Port .* is already in use.:UserWarning")
def test_execute_workflow_results(tmp_path):
    ofv = 3
    mfr = ModelfitResults(ofv=ofv)

    wf = Workflow([Task('result', lambda: mfr)])

    with chdir(tmp_path):
        res = execute_workflow(wf)

    assert res.ofv == ofv
    assert not hasattr(res, 'tool_database')


@pytest.mark.filterwarnings("ignore:.*Port .* is already in use.:UserWarning")
def test_execute_workflow_results_with_tool_database(tmp_path):
    ofv = 3
    mfr = ModelfitResults(ofv=ofv)
    mfr.tool_database = None

    wf = Workflow([Task('result', lambda: mfr)])

    with chdir(tmp_path):
        res = execute_workflow(wf)
        assert res.tool_database is not None

    assert res.ofv == ofv


@pytest.mark.filterwarnings("ignore:.*Port .* is already in use.:UserWarning")
def test_execute_workflow_results_with_report(testdata, tmp_path):
    mfr = read_results(testdata / 'frem' / 'results.json')
    mfr.tool_database = None

    wf = Workflow([Task('result', lambda: mfr)])

    with chdir(tmp_path):
        with pytest.warns(UserWarning, match=".*unexpected keyword argument 'tool_database'.*"):
            res = execute_workflow(wf)
        html = res.tool_database.path / 'results.html'
        assert html.is_file()
        assert html.stat().st_size > 500000