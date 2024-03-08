.. _amd_pk:

========
AMD - PK
========

Will create a PK only model based on a model or dataset input. The given workflow is based on the given :ref:`strategy<strategy_amd>`.

~~~~~~~
Running
~~~~~~~

The code to initiate the AMD tool for a PK model:

.. pharmpy-code::

    from pharmpy.tools import run_amd

    dataset_path = 'path/to/dataset'
    strategy = 'default'
    res = run_amd(input=dataset_path,
                  modeltype='basic_pk',
                  administration='oral',
                  strategy=strategy,
                  search_space='ABSORPTION(FO);ELIMINATION(ZO)',
                  allometric_variable='WGT',
                  occasion='VISI')

Arguments
~~~~~~~~~

.. _amd_pk_args:

The arguments used in PK models can be seen below. Some are mandatory for this type of model building while others can are optional, and some AMD arguments are
not used for this modeltype. If any of the mandatory arguments are missing, the model will not be run. The only exception being for ``mat_init`` which is only
mandatory for 'oral' administration.

Mandatory
---------

+---------------------------------------------------+-----------------------------------------------------------------------------------------------------------------+
| Argument                                          | Description                                                                                                     |
+===================================================+=================================================================================================================+
| ``input``                                         | Path to a dataset or start model object. See :ref:`input in amd<input_amd>`                                     |
+---------------------------------------------------+-----------------------------------------------------------------------------------------------------------------+
| ``modeltype``                                     | Set to 'basic_pk' for this modeltype.                                                                           |
+---------------------------------------------------+-----------------------------------------------------------------------------------------------------------------+
| ``cl_init``                                       | Initial estimate for the population clearance                                                                   |
+---------------------------------------------------+-----------------------------------------------------------------------------------------------------------------+
| ``vc_init``                                       | Initial estimate for the central compartment population volume                                                  |
+---------------------------------------------------+-----------------------------------------------------------------------------------------------------------------+
| ``mat_init``                                      | Initial estimate for the mean absorption time (only for oral models)                                            |
+---------------------------------------------------+-----------------------------------------------------------------------------------------------------------------+

Optional
--------

+---------------------------------------------------+-----------------------------------------------------------------------------------------------------------------+
| Argument                                          | Description                                                                                                     |
+===================================================+=================================================================================================================+
| ``administration``                                | Route of administration. One of 'iv', 'oral' or 'ivoral'. Default is 'oral'                                     |
+---------------------------------------------------+-----------------------------------------------------------------------------------------------------------------+
| ``strategy``                                      | :ref:`Strategy<strategy_amd>` defining run order of the different subtools. Default is 'default'                |
+---------------------------------------------------+-----------------------------------------------------------------------------------------------------------------+
| ``results``                                       | ModelfitResults if input is a model                                                                             |
+---------------------------------------------------+-----------------------------------------------------------------------------------------------------------------+
| ``search_space``                                  | MFL for :ref:`search space<search_space_amd>` of structural and covariate models                                |
|                                                   | (default depends on ``modeltype`` and ``administration``)                                                       |
+---------------------------------------------------+-----------------------------------------------------------------------------------------------------------------+
| ``lloq_limit``                                    | Lower limit of quantification.                                                                                  |
+---------------------------------------------------+-----------------------------------------------------------------------------------------------------------------+
| ``lloq_method``                                   | Method to use for handling lower limit of quantification. See :py:func:`pharmpy.modeling.transform_blq`.        |
+---------------------------------------------------+-----------------------------------------------------------------------------------------------------------------+
| ``strategy``                                      | :ref:`Strategy<strategy_amd>` defining run order of the different subtools valid arguments are 'default'        |
|                                                   | (deafult) and 'reevaluation'                                                                                    |
+---------------------------------------------------+-----------------------------------------------------------------------------------------------------------------+
| ``allometric_variable``                           | Variable to use for allometry (default is name of column described as body weight)                              |
+---------------------------------------------------+-----------------------------------------------------------------------------------------------------------------+
| ``occasion``                                      | Name of occasion column                                                                                         |
+---------------------------------------------------+-----------------------------------------------------------------------------------------------------------------+
| ``strictness``                                    | :ref:`Strictness<strictness>` criteria for model selection.                                                     |
|                                                   | Default is "minimization_successful or                                                                          |
|                                                   | (rounding_errors and sigdigs>= 0.1)"                                                                            |
|                                                   | If ``strictness`` is set to ``None`` no strictness                                                              |
|                                                   | criteria are applied                                                                                            |
+---------------------------------------------------+-----------------------------------------------------------------------------------------------------------------+
| ``mechanistic_covariates``                        | List of covariates or covariate/parameter combinations to run in a separate prioritized covsearch run. Allowed  |
|                                                   | elements in the list are strings of covariates or tuples with one covariate and parameter each, e.g ["AGE",     |
|                                                   | ("WGT", "CL")]. The associated effects are extracted from the given search space.                               |
+---------------------------------------------------+-----------------------------------------------------------------------------------------------------------------+
| ``retries_strategy``                              | Decide how to use the retries tool. Valid options are 'skip', 'all_final' or 'final'. Default is 'all_final'    |
+---------------------------------------------------+-----------------------------------------------------------------------------------------------------------------+
| ``seed``                                          | A random number generator or seed to use for steps with random sampling.                                        |
+---------------------------------------------------+-----------------------------------------------------------------------------------------------------------------+
| ``parameter_uncertainty_method``                  | Parameter uncertainty method to use. Currently implemented methods are: 'SANDWICH', 'SMAT', 'RMAT' and 'EFIM'.  |
|                                                   | For more information about these methods see                                                                    |
|                                                   | :py:func:`here<pharmpy.model.EstimationStep.parameter_uncertainty_method>`.                                     |
+---------------------------------------------------+-----------------------------------------------------------------------------------------------------------------+
| ``ignore_datainfo_fallback``                      | Decide wether or not to use connected datainfo object to infer information about the model. If True, all        |
|                                                   | information regarding the model must be given explicitly by the user, such as the allometric varible. If False, |
|                                                   | such information is extracted using the datainfo, in the absence of arguments given by the user. Default        |
|                                                   | is False.                                                                                                       |
+---------------------------------------------------+-----------------------------------------------------------------------------------------------------------------+


~~~~~~~~~~~~~~
Strategy parts
~~~~~~~~~~~~~~

How the AMD tool is run is defined using the ``strategy`` argument as explained in :ref:`Strategy<strategy_amd>`. How exactly the different parts of each respective
strategy is run for a PK model can be seen below.

Structural
~~~~~~~~~~

.. graphviz::

    digraph BST {
            node [fontname="Arial",shape="rect"];
            rankdir="LR";
            base [label="Input", shape="oval"]
            s0 [label="structural covariates"]
            s1 [label="modelsearch"]

            base -> s0
            s0 -> s1
        }


**Structural covariates**

The structural covariates are added directly to the starting model. If these cannot be added here (due to missing 
parameters for instance) they will be tested once more at the start of the next covsearch run.

Note that all structural covariates are added all at once without any test or search.

These are given within the search space by specifying them as mechanistic covariates in the following way:

.. code-block::

    COVARIATE(CL, WGT, POW)
    COVARIATE?(@IIV, @CATEGORICAL, *)

In this search space, the power covariate effect of WGT on CL is interpreted as a structural covariate (due to the missing "?")
while the other statement would be explored in a later COVSearch run.

There is no default structural covariates to run if not specified by the user.

**Modelsearch**

The settings that the AMD tool uses for the modelsearch subtool can be seen in the table below.

+---------------+----------------------------------------------------------------------------------------------------+
| Argument      | Setting                                                                                            |
+===============+====================================================================================================+
| search_space  | ``search_space`` (As defined in :ref:`AMD options<amd_pk_args>`)                                   |
+---------------+----------------------------------------------------------------------------------------------------+
| algorithm     | ``'reduced_stepwise'``                                                                             |
+---------------+----------------------------------------------------------------------------------------------------+
| iiv_strategy  | ``'absorption_delay'``                                                                             |
+---------------+----------------------------------------------------------------------------------------------------+
| rank_type     | ``'bic'`` (type: mixed)                                                                            |
+---------------+----------------------------------------------------------------------------------------------------+
| cutoff        | ``None``                                                                                           |
+---------------+----------------------------------------------------------------------------------------------------+

If no search space is given by the user, the default search space is dependent on the ``administration`` argument

**PK Oral**

.. code-block::

    ABSORPTION([FO,ZO,SEQ-ZO-FO])
    ELIMINATION(FO)
    LAGTIME([OFF,ON])
    TRANSITS([0,1,3,10],*)
    PERIPHERALS(0,1)

**PK IV**

.. code-block::

    ELIMINATION(FO)
    PERIPHERALS([0,1,2])
    
**PK IV+ORAL**

.. code-block::

    ABSORPTION([FO,ZO,SEQ-ZO-FO])
    ELIMINATION(FO)
    LAGTIME([OFF,ON])
    TRANSITS([0,1,3,10],*)
    PERIPHERALS([0,1,2])

IIVSearch
~~~~~~~~~

The settings that the AMD tool uses for this subtool can be seen in the table below.

+---------------+---------------------------+------------------------------------------------------------------------+
| Argument      | Setting                   |   Setting (rerun)                                                      |
+===============+===========================+========================================================================+
| algorithm     | ``'top_down_exhaustive'`` |  ``'top_down_exhaustive'``                                             |
+---------------+---------------------------+------------------------------------------------------------------------+
| iiv_strategy  | ``'fullblock'``           |  ``'no_add'``                                                          |
+---------------+---------------------------+------------------------------------------------------------------------+
| rank_type     | ``'bic'`` (type: iiv)     |  ``'bic'`` (type: iiv)                                                 |
+---------------+---------------------------+------------------------------------------------------------------------+
| cutoff        | ``None``                  |  ``None``                                                              |
+---------------+---------------------------+------------------------------------------------------------------------+

Residual
~~~~~~~~

The settings that the AMD tool uses for this subtool can be seen in the table below. When re-running the tool, the
settings remain the same.

+---------------+----------------------------------------------------------------------------------------------------+
| Argument      | Setting                                                                                            |
+===============+====================================================================================================+
| groups        | ``4``                                                                                              |
+---------------+----------------------------------------------------------------------------------------------------+
| p_value       | ``0.05``                                                                                           |
+---------------+----------------------------------------------------------------------------------------------------+
| skip          | ``None``                                                                                           |
+---------------+----------------------------------------------------------------------------------------------------+

IOVSearch
~~~~~~~~~

The settings that the AMD tool uses for this subtool can be seen in the table below. 

+---------------------+----------------------------------------------------------------------------------------------+
| Argument            | Setting                                                                                      |
+=====================+==============================================================================================+
| column              | ``occasion`` (As defined in :ref:`AMD options<amd_pk_args>`)                                 |
+---------------------+----------------------------------------------------------------------------------------------+
| list_of_parameters  | ``None``                                                                                     |
+---------------------+----------------------------------------------------------------------------------------------+
| rank_type           | ``'bic'`` (type: random)                                                                     |
+---------------------+----------------------------------------------------------------------------------------------+
| cutoff              | ``None``                                                                                     |
+---------------------+----------------------------------------------------------------------------------------------+
| distribution        | ``'same-as-iiv'``                                                                            |
+---------------------+----------------------------------------------------------------------------------------------+

Allometry
~~~~~~~~~

The settings that the AMD tool uses for this subtool can be seen in the table below.

+----------------------+---------------------------------------------------------------------------------------------+
| Argument             | Setting                                                                                     |
+======================+=============================================================================================+
| allometric_variable  | ``allometric_variable`` (As defined in :ref:`AMD options<amd_pk_args>`)                     |
+----------------------+---------------------------------------------------------------------------------------------+
| reference_value      | ``70``                                                                                      |
+----------------------+---------------------------------------------------------------------------------------------+
| parameters           | ``None``                                                                                    |
+----------------------+---------------------------------------------------------------------------------------------+
| initials             | ``None``                                                                                    |
+----------------------+---------------------------------------------------------------------------------------------+
| lower_bounds         | ``None``                                                                                    |
+----------------------+---------------------------------------------------------------------------------------------+
| upper_bounds         | ``None``                                                                                    |
+----------------------+---------------------------------------------------------------------------------------------+
| fixed                | ``None``                                                                                    |
+----------------------+---------------------------------------------------------------------------------------------+

COVSearch
~~~~~~~~~

The settings that the AMD tool uses for this subtool can be seen in the table below. The effects are extracted from the
search space.

+---------------+----------------------------------------------------------------------------------------------------+
| Argument      | Setting                                                                                            |
+===============+====================================================================================================+
| effects       | ``search_space`` (As defined in :ref:`AMD options<amd_pk_args>`)                                   |
+---------------+----------------------------------------------------------------------------------------------------+
| p_forward     | ``0.05``                                                                                           |
+---------------+----------------------------------------------------------------------------------------------------+
| p_backward    | ``0.01``                                                                                           |
+---------------+----------------------------------------------------------------------------------------------------+
| max_steps     | ``-1``                                                                                             |
+---------------+----------------------------------------------------------------------------------------------------+
| algorithm     | ``'scm-forward-then-backward'``                                                                    |
+---------------+----------------------------------------------------------------------------------------------------+

If no search space for this tool is given, the following default will be used:

.. code-block::

    COVARIATE?(@IIV, @CONTINUOUS, exp, *)
    COVARIATE?(@IIV, @CATEGORICAL, cat, *)



.. graphviz::

    digraph BST {
            node [fontname="Arial",shape="rect"];
            rankdir="LR";
            base [label="Input", shape="oval"]
            s0 [label="mechanistic covariates"]
            s1 [label="exploratory covariates"]

            base -> s0
            s0 -> s1
        }



**Mechanisitic covariates**

If any mechanistic covariates have been given as input to the AMD tool, the specified covariate effects for these
covariates is run in a separate initial covsearch run when adding covariates. These covariate effects are extracted
from the given search space

**Exploratory covariates**

The covariate effects remaining in the search space after having run potentially both structural and mechanistic covariates
are now run in an exploratory search.

**Examples**

.. code-block::

    mechanistic_covariates = [AGE, (CL,WGT)]

    COVARIATE?([CL,V], [AGE, WGT], *)
    COVARIATE?(Q, WGT, *)

In the above case, the mechanistic/exploratory search spaces would be the following:

Mechanistic

.. code-block::

    COVARIATE?([CL,V], AGE, *)
    COVARIATE?(CL, WGT, *)

Exploratory

.. code-block::

    COVARIATE?([V,Q], WGT, *)

~~~~~~~~
Examples
~~~~~~~~

Minimum
~~~~~~~

A minimum example for running AMD with modeltype PK:

.. pharmpy-code::

    from pharmpy.tools import run_amd

    dataset_path = 'path/to/dataset'

    res = run_amd(
                dataset_path,
                modeltype="basic_pk",
                administration="iv",
                cl_init=2.0,
                vc_init=5.0
                )

Model input and search space
~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Specifying input model and search space:

.. pharmpy-code::

    from pharmpy.tools import run_amd

    start_model = read_model('path/to/model')

    res = run_amd(
                input=start_model,
                modeltype='basic_pk',
                administration='iv'
                search_space='ABSORPTION(FO);ELIMINATION(ZO);COVARIATE(CL, WGT, POW)',
                cl_init=2.0,
                vc_init=5.0,
                )
