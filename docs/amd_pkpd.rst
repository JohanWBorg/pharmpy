.. _amd_pkpd:

==========
AMD - PKPD
==========

Will create the best PKPD model based on a PK model. The AMD workflow for PKPD models depends on the selected :ref:`strategy<strategy_amd>`.

The principle behind the PKPD model developement follows PPP&D, which initially will fixate the PK part of the model and only develope the PD part.

A complete PKPD workflow is hence currently only possible by first filtering the model dataset for PK information and running AMD for a 'basic_pk'
modeltype. Then, given the resulting model from that workflow, the original dataset can be attached and another AMD run with modeltype 'PKPD' can 
be run. This can be done using :py:func:`pharmpy.modeling.set_dataset`. 



.. graphviz::

    digraph BST {
            node [fontname="Arial",shape="rect"];
            rankdir="LR";
            base [label="Input PK model / dataset", shape="oval"]
            s0 [label="AMD - basic_pk"]
            s1 [label="Final model"]
            s2 [label="Final model + pkpd dataset"]
            s3 [label="AMD - pkpd"]
            base -> s0
            s0 -> s1
            s1 -> s2
            s2 -> s3
        }



Regarding the dataset, two DVIDs are mandatory.

+------+--------------------------------+
| DVID | Description                    |
+======+================================+
|  1   | Assumed to be connected to the |
|      | **PK** part of the model       |
+------+--------------------------------+
|  2   | Assumed to be connected to the |
|      | **PD** part of the model       |
+------+--------------------------------+

.. note::
    Please note that it is only possible to run the AMD tool for the PD part of PKPD models. The tool
    expects a fully build PK model as input.
    If a dataset is inputed, a basic PK model is created and used as input, which is not recommended

~~~~~~~
Running
~~~~~~~

The code to initiate the AMD tool for a PKPD model:

.. pharmpy-code::

    from pharmpy.modeling import read_model
    from pharmpy.tools read_model, run_amd

    start_model = read_model('path/to/model')

    res = run_amd(
                modeltype='pkpd',
                input=start_model,
                search_space='DIRECTEFFECT(*)',
                b_init=0.1,
                emax_init=1.0,
                ec50_init=0.1,
                met_init=0.4,
                )

Arguments
~~~~~~~~~

.. _amd_pkpd_args:

The AMD arguments used for PKPD models can be seen below. Some are mandatory for this type of model building while others can are optional, and some AMD arguments are
not used for this modeltype. If any of the mandatory arguments is missing, the program till raise an error.

Mandatory
---------

+---------------------------------------------------+-----------------------------------------------------------------------------------------------------------------+
| Argument                                          | Description                                                                                                     |
+===================================================+=================================================================================================================+
| ``input``                                         | Start model object. See :ref:`input in amd<input_amd>`                                                          |
+---------------------------------------------------+-----------------------------------------------------------------------------------------------------------------+
| ``modeltype``                                     | Set to 'pkpd' for this modeltype.                                                                               |
+---------------------------------------------------+-----------------------------------------------------------------------------------------------------------------+
| ``b_init``                                        | Initial estimate for the baseline effect                                                                        |
+---------------------------------------------------+-----------------------------------------------------------------------------------------------------------------+
| ``emax_init``                                     | Initial estimate for the Emax                                                                                   |
+---------------------------------------------------+-----------------------------------------------------------------------------------------------------------------+
| ``ec50_init``                                     | Initial estimate for the EC50                                                                                   |
+---------------------------------------------------+-----------------------------------------------------------------------------------------------------------------+
| ``met_init``                                      | Initial estimate for the mean equilibration time                                                                |
+---------------------------------------------------+-----------------------------------------------------------------------------------------------------------------+

.. note::
    In addition to these arguments, :ref:`common arguments<amd_args_common>` can be added.

~~~~~~~~~~~~~~
Strategy parts
~~~~~~~~~~~~~~

How the AMD tool is run is defined using the ``strategy`` argument as explained in :ref:`Strategy<strategy_amd>`. How exactly the different parts of each respective
strategy are run for a PKPD model can be seen below.

Structural
~~~~~~~~~~

.. graphviz::

    digraph BST {
            node [fontname="Arial",shape="rect"];
            rankdir="LR";
            base [label="Input", shape="oval"]
            s0 [label="structural covariates"]
            s1 [label="structsearch"]

            base -> s0
            s0 -> s1
        }


**Structural covariates**

The structural covariates are added directly to the starting model. If these cannot be added here (due to missing 
parameters for instance) they will be tested once more at the start of the next covsearch run.

Note that all structural covariates are added all at once without any test or search.

These are given within the search space by specifying them as mechanistic covariates in the following way:

.. code-block::

    COVARIATE(SLOPE, WGT, POW)
    COVARIATE?(@PD_IIV, @CATEGORICAL, *)

In this search space, the power covariate effect of WGT on SLOPE is interpreted as a structural covariate (due to the missing "?")
while the other statement would be explored in a later COVSearch run.

There is no default structural covariates to run if not specified by the user.

**Structsearch**

For a PKPD model, structsearch is run to determine the best structural model. All input arguments are specified by
the user when initializing AMD. For more information regarding how the search space is used in structsearch, please see 
:ref:`structsearch tool<the search space pkpd>`

+---------------+----------------------------------------------------------------------------------------------------+
| Argument      | Setting                                                                                            |
+===============+====================================================================================================+
| search_space  | ``search_space`` (As defined in :ref:`AMD input<amd_pkpd_args>`)                                   |
+---------------+----------------------------------------------------------------------------------------------------+
| modeltype     | 'pkpd'                                                                                             |
+---------------+----------------------------------------------------------------------------------------------------+
| b_init        | ``'b_init'`` (As defined in :ref:`AMD input<amd_pkpd_args>`)                                       |
+---------------+----------------------------------------------------------------------------------------------------+
| emax_init     | ``'emax_init'`` (As defined in :ref:`AMD input<amd_pkpd_args>`)                                    |
+---------------+----------------------------------------------------------------------------------------------------+
| ec50_init     | ``'ec50_init'``  (As defined in :ref:`AMD input<amd_pkpd_args>`)                                   |
+---------------+----------------------------------------------------------------------------------------------------+
| met_init      | ``met_init`` (As defined in :ref:`AMD input<amd_pkpd_args>`)                                       |
+---------------+----------------------------------------------------------------------------------------------------+
| strictness    | ``strictness`` (As defined in :ref:`AMD input<amd_pkpd_args>`)                                     |
+---------------+----------------------------------------------------------------------------------------------------+

If no searchspace is given for the structsearch tool, then a default will be set to :

.. code-block::

    DIRECTEFFECT(*)
    EFFECTCOMP(*)
    INDIRECTEFFECT(*,*)

IIVSearch
~~~~~~~~~

The settings that the AMD tool uses for this subtool can be seen in the table below.

+---------------+---------------------------+------------------------------------------------------------------------+
| Argument      | Setting                   |   Setting (rerun)                                                      |
+===============+===========================+========================================================================+
| algorithm     | ``'top_down_exhaustive'`` |  ``'top_down_exhaustive'``                                             |
+---------------+---------------------------+------------------------------------------------------------------------+
| iiv_strategy  | ``'pd_fullblock'``        |  ``'no_add'``                                                          |
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
| dv            | ``2``                                                                                              |
+---------------+----------------------------------------------------------------------------------------------------+
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
| column              | ``occasion`` (As defined in :ref:`AMD options<amd_pkpd_args>`)                               |
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

Allometry is completely skipped when running AMD with a modeltype of 'pkpd'

COVSearch
~~~~~~~~~

The settings that the AMD tool uses for this subtool can be seen in the table below. The effects are extracted from the
search space.

+---------------+----------------------------------------------------------------------------------------------------+
| Argument      | Setting                                                                                            |
+===============+====================================================================================================+
| effects       | ``search_space`` (As defined in :ref:`AMD options<amd_pkpd_args>`)                                 |
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

    COVARIATE?(@PD_IIV, @CONTINUOUS, exp, *)
    COVARIATE?(@PD_IIV, @CATEGORICAL, cat, *)



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

    mechanistic_covariates = [AGE, (SLOPE,WGT)]

    COVARIATE?([SLOPE,EMAX], [AGE, WGT], *)
    COVARIATE?(EC50, WGT, *)

In the above case, the mechanistic/exploratory search spaces would be the following:

Mechanistic

.. code-block::

    COVARIATE?([SLOPE,EMAX], AGE, *)
    COVARIATE?(SLOPE, WGT, *)

Exploratory

.. code-block::

    COVARIATE?([EMAX,EC50], WGT, *)

~~~~~~~~
Examples
~~~~~~~~

Minimum
~~~~~~~

A minimum example for running AMD with modeltype PKPD:

.. pharmpy-code::

    from pharmpy.tools import run_amd

    start_model = read_model('path/to/model')

    res = run_amd(
                modeltype='pkpd',
                input=start_model,
                b_init=2.0,
                emax_init=1.0,
                ec50=0.1,
                met_init=2.1
                )

Specifying search space
~~~~~~~~~~~~~~~~~~~~~~~

.. pharmpy-code::

    from pharmpy.tools import run_amd

    start_model = read_model('path/to/model')

    res = run_amd(
                modeltype='pkpd',
                input=start_model,
                search_space = "DIRECTEFFECT(linear)",
                b_init=2.0,
                emax_init=1.0,
                ec50=0.1,
                met_init=2.1
                )

