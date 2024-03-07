.. _amd_tmdd:

========
AMD - TMDD
========

WRITE A FEW LINES OF DESCRIPTION HERE
- What kind of model
- What kind of input

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
                  search_space='LET(CATEGORICAL, [SEX]); LET(CONTINUOUS, [AGE])',
                  allometric_variable='WGT',
                  occasion='VISI')

Arguments
~~~~~~~~~
The arguments used in PK models are the following

WRITE SOMETHING ABOUT INPUT

Mandatory
---------

+-------------------------------------------------+-----------------------------------------------------------------------------------------+
| Argument                                        | Description                                                                             |
+=================================================+=========================================================================================+
| ``modeltype``                                   | Type of model. In this case "tmdd".                                                     |
+-------------------------------------------------+-----------------------------------------------------------------------------------------+

Optional
--------

+-------------------------------------------------+-----------------------------------------------------------------------------------------+
| Argument                                        | Description                                                                             |
+=================================================+=========================================================================================+
| ``cl_init``                                     | Initial estimate for the population clearance (default is 0.01)                         |
+-------------------------------------------------+-----------------------------------------------------------------------------------------+


.. _models:

~~~~~~~~~~~~~~
Strategy parts
~~~~~~~~~~~~~~

Refer to AMD strategy explanation to see how the different parts are connected

Structural
~~~~~~~~~~

Structural covariates
=====================

Modelsearch
===========


IIVSearch
~~~~~~~~~


Residual
~~~~~~~~


IOVSearch
~~~~~~~~~


Allometry
~~~~~~~~~


COVSearch
~~~~~~~~~

Mechanisitic covariates
=======================


Exploratory covariates
======================



~~~~~~~~
Examples
~~~~~~~~

A minimum example for running AMD with modeltype PK:

.. pharmpy-code::

    from pharmpy.tools import run_amd

    start_model = read_model('path/to/model')

    res = run_amd(
                modeltype='basic_pk',
                input=start_model,
                search_space='ABSORPTION(FO)',
                )

Specifying initial parameters:

.. pharmpy-code::

    from pharmpy.tools import run_amd

    start_model = read_model('path/to/model')

    res = run_amd(
                modeltype='basic_pk',
                input=start_model,
                search_space='ABSORPTION(FO)',
                cl_init=2.0,
                vc_init=5.0,
                )

