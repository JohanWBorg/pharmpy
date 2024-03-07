.. _amd_pkpd:

========
AMD - PKPD
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
                  modeltype='pkpd',
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
| ``modeltype``                                   | Type of model. In this case "pkpd".                                                     |
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

.. graphviz::

    digraph BST {
            node [fontname="Arial",shape="rect"];
            rankdir="LR";
            base [label="Input", shape="oval"]
            s0 [label="structural covariates"]
            s1 [label="modelsearch"]
            s2 [label="structsearch"]

            base -> s0
            s0 -> s1
            s1 -> s2
        }

Structural covariates
=====================

Modelsearch
===========

Structsearch
============
.. note::
    Please note that it is only possible to run the AMD tool for the PD part of PKPD models. The tool
    expects a fully build PK model as input. 


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

A minimum example for running AMD with modeltype PKPD:

.. pharmpy-code::

    from pharmpy.tools import run_amd

    start_model = read_model('path/to/model')

    res = run_amd(
                modeltype='pkpd',
                input=start_model,
                search_space='ABSORPTION(FO)',
                )

Specifying initial parameters:

.. pharmpy-code::

    from pharmpy.tools import run_amd

    start_model = read_model('path/to/model')

    res = run_amd(
                modeltype='pkpd',
                input=start_model,
                search_space='ABSORPTION(FO)',
                cl_init=2.0,
                vc_init=5.0,
                )

