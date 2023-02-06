import os.path
from pathlib import Path

import pytest
import sympy

from pharmpy.internals.fs.cwd import chdir
from pharmpy.modeling import (
    convert_model,
    copy_model,
    create_joint_distribution,
    fix_parameters,
    generate_model_code,
    get_config_path,
    get_model_covariates,
    load_example_model,
    read_model,
    read_model_from_string,
    remove_unused_parameters_and_rvs,
    set_name,
    write_model,
)


def test_get_config_path():
    with pytest.warns(UserWarning):
        assert get_config_path() is None


def test_read_model_path(testdata):
    path = testdata / 'nonmem' / 'minimal.mod'
    model = read_model(path)
    assert model.parameters['THETA_1'].init == 0.1


def test_read_model_str(testdata):
    path = str(testdata / 'nonmem' / 'minimal.mod')
    model = read_model(path)
    assert model.parameters['THETA_1'].init == 0.1


def test_read_model_expanduser(testdata):
    model_path = testdata / "nonmem" / "minimal.mod"
    model_path_relative_to_home = ''
    try:
        model_path_relative_to_home = model_path.relative_to(Path.home())
    except ValueError:
        pytest.skip(f'{model_path} is not a descendant of home directory ({Path.home()})')
    path = os.path.join('~', model_path_relative_to_home)
    model = read_model(path)
    assert model.parameters['THETA_1'].init == 0.1


def test_read_model_from_string():
    model = read_model_from_string(
        """$PROBLEM base model
$INPUT ID DV TIME
$DATA file.csv IGNORE=@

$PRED
Y = THETA(1) + ETA(1) + ERR(1)

$THETA 0.1
$OMEGA 0.01
$SIGMA 1
$ESTIMATION METHOD=1 INTER MAXEVALS=9990 PRINT=2 POSTHOC
"""
    )
    assert model.parameters['THETA_1'].init == 0.1


def test_write_model(testdata, load_model_for_test, tmp_path):
    model = load_model_for_test(testdata / 'nonmem' / 'minimal.mod')
    with chdir(tmp_path):
        write_model(model, tmp_path / 'run1.mod')
        assert Path(tmp_path / 'run1.mod').is_file()


def test_generate_model_code(testdata, load_model_for_test):
    model = load_model_for_test(testdata / 'nonmem' / 'minimal.mod')
    fix_parameters(model, ['THETA_1'])
    assert generate_model_code(model).split('\n')[7] == '$THETA 0.1 FIX'


def test_load_example_model():
    model = load_example_model("pheno")
    assert len(model.parameters) == 6
    assert len(model.modelfit_results.parameter_estimates) == 6

    model = load_example_model("moxo")
    assert len(model.parameters) == 11

    with pytest.raises(ValueError):
        load_example_model("grekztalb23=")


def test_get_model_covariates(pheno, testdata, load_model_for_test):
    assert set(get_model_covariates(pheno)) == {
        sympy.Symbol('APGR'),
        sympy.Symbol('WGT'),
    }
    minimal = load_model_for_test(testdata / 'nonmem' / 'minimal.mod')
    assert set(get_model_covariates(minimal)) == set()


def test_set_name(pheno):
    model = pheno.copy()
    set_name(model, "run1")
    assert model.name == "run1"


def test_copy_model(pheno):
    run1 = copy_model(pheno)
    assert id(pheno) != id(run1)
    assert id(pheno.parameters) == id(run1.parameters)
    run2 = copy_model(run1, "run2")
    assert run2.name == "run2"
    assert run2.parent_model == "pheno_real"


def test_convert_model():
    model = load_example_model("pheno")

    run1 = convert_model(model, "nlmixr")
    assert model.name == run1.name
    assert model == run1

    run2 = convert_model(run1, "nonmem")
    assert model.name == run2.name == run1.name
    assert model == run2 == run1


def test_remove_unused_parameters_and_rvs(pheno):
    model = pheno.copy()
    remove_unused_parameters_and_rvs(model)
    create_joint_distribution(
        model, individual_estimates=model.modelfit_results.individual_estimates
    )
    statements = model.statements
    i = statements.index(statements.find_assignment('CL'))
    model.statements = model.statements[0:i] + model.statements[i + 1 :]
    remove_unused_parameters_and_rvs(model)
    assert len(model.random_variables['ETA_2'].names) == 1
