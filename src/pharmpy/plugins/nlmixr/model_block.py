import re

import pharmpy.model
from pharmpy.deps import sympy, sympy_printing
from pharmpy.internals.code_generator import CodeGenerator
from pharmpy.model import Assignment

from .error_model import add_error_model, add_error_relation, convert_piecewise, find_term
from .name_mangle import name_mangle


class ExpressionPrinter(sympy_printing.str.StrPrinter):
    def __init__(self, amounts):
        self.amounts = amounts
        super().__init__()

    def _print_Symbol(self, expr):
        return name_mangle(expr.name)

    def _print_Derivative(self, expr):
        fn = expr.args[0]
        return f'd/dt({fn.name})'

    def _print_Function(self, expr):
        name = expr.func.__name__
        if name in self.amounts:
            return expr.func.__name__
        else:
            return expr.func.__name__ + f'({self.stringify(expr.args, ", ")})'

def new_add_statements(model, cg, statements, only_piecewise, dependencies = None, res_alias = None):
    
    dv = list(model.dependent_variables.keys())[0]
        
    for s in statements:
        if isinstance(s, Assignment):
            if s.symbol == dv and not s.expression.is_Piecewise:

                # FIXME : Find another way to assert that a sigma exist
                sigma = None
                for dist in model.random_variables.epsilons:
                    sigma = dist.variance
                assert sigma is not None
                
                if not only_piecewise:
                    from .error_model import res_error_term
                    test = res_error_term(model, s.expression)
                    res = test.res
                    if len(dependencies) != 0:
                        cg.add(f'{s.symbol} <- {res}')
                        cg.add(f'{s.symbol} ~ add(add_error) + prop(prop_error)')
                        
                        # remove SIGMA definition due to redundancy
                        from pharmpy.modeling import get_sigmas
                        if test.add.sigma_alias or test.prop.sigma_alias:
                            pass
                        else:
                            for sigma in get_sigmas(model):
                                cg.remove(f"{sigma.name} <- fixed({sigma.init})")
                        
                    else:
                        cg.add(f'{s.symbol} <- {res}')
                        e = ""
                        first = True
                        if test.add.expr != None:
                            e += f'add({test.add.expr})'
                            first = False
                        if test.prop.expr != None:
                            if not first:
                                e += " + "
                            e += f'prop({test.prop.expr})'
                        cg.add(f'{s.symbol} ~ {e}')
                else:
                    # Extract the res and error term using res_error_term
                    # Add a new res term and separate error terms
                    # Add the final Y = RES and Y ~ add() + prop() in the end
                    # ... AFTER the LAST dv has been handled
                    pass

            else:
                expr = s.expression
                if expr.is_Piecewise:
                    first = True
                    for value, cond in expr.args:
                        if cond is not sympy.S.true:
                            if cond.atoms(sympy.Eq):
                                cond = convert_eq(cond)
                            if first:
                                cg.add(f'if ({cond}) {{')
                                first = False
                            else:
                                cg.add(f'}} else if ({cond}) {{')
                        else:
                            cg.add('} else {')
                            if "NEWIND" in [t.name for t in expr.free_symbols] and value == 0:
                                largest_value = expr.args[0].expr
                                largest_cond = expr.args[0].cond
                                for value, cond in expr.args[1:]:
                                    if cond is not sympy.S.true:
                                        if cond.rhs > largest_cond.rhs:
                                            largest_value = value
                                            largest_cond = cond
                                        elif cond.rhs == largest_cond.rhs:
                                            if not isinstance(cond, sympy.LessThan) and isinstance(
                                                largest_cond, sympy.LessThan
                                            ):
                                                largest_value = value
                                                largest_cond = cond
                                value = largest_value
                        cg.indent()
                        
                        if not only_piecewise:
                            cg.add(f'{s.symbol.name} <- {value}')
                            
                            if s.symbol in dependencies:
                                if not value.is_constant() and not isinstance(value, sympy.Symbol):
                                    add, prop = extract_add_prop(value, res_alias, model)
                                    cg.add(f'add_error <- {add}')
                                    cg.add(f'prop_error <- {prop}')
                        else:
                            from .error_model import res_error_term
                            if not value.is_constant() and not isinstance(value, sympy.Symbol):
                                t = res_error_term(model, value)
                                cg.add(f"res <- {t.res}")
                                cg.add(f'add_error <- {t.add.expr}')
                                cg.add(f'prop_error <- {t.prop.expr}')
                            else:
                                cg.add(f'{s.symbol.name} <- {value}')
                                
                        cg.dedent()
                    cg.add('}')
                elif s.symbol in dependencies:
                    add, prop = extract_add_prop(s, res_alias, model)
                    cg.add(f'{s.symbol.name} <- {expr}') #TODO : Remove ?
                    cg.add(f'add_error <- {add}')
                    cg.add(f'prop_error <- {prop}')
                else:
                    cg.add(f'{s.symbol.name} <- {expr}')
    
    if only_piecewise:
        cg.add(f'{dv} <- res')
        cg.add(f'{dv} ~ add(add_error) + prop(prop_error)')
        

def extract_add_prop(s, res_alias, model):
    if isinstance(s, sympy.Pow):
        terms = sympy.Add.make_args(s.args[0])
    else:
        terms = sympy.Add.make_args(s.expression)
    assert(len(terms) <= 2)
    
    prop = 0
    add = 0
    prop_found = False
    for term in terms:
        for symbol in term.free_symbols:
            if symbol in res_alias:
                if prop_found is False:
                    term = term.subs(symbol, 1)
                    prop = list(term.free_symbols)[0]
                    prop_found = True
        if prop_found is False:
            add = list(term.free_symbols)[0]
    
    return add, prop
        

                    
def add_statements(
    model: pharmpy.model.Model, cg: CodeGenerator, statements: pharmpy.model.statements
) -> None:
    """
    Add statements to generated code generator. The statements should be before
    or after the ODEs.

    Parameters
    ----------
    model : pharmpy.model.Model
        A pharmpy model object to add statements to.
    cg : CodeGenerator
        Codegenerator object holding the code to be added to.
    statements : pharmpy.model.statements
        Statements to be added to the code generator.
    """
    # FIXME: handle other DVs?
    dv = list(model.dependent_variables.keys())[0]

    error_model_found = False
    dv_found = False

    for s in statements:
        if isinstance(s, Assignment):
            if s.symbol == dv:
                dv_found = True

                # FIXME : Find another way to assert that a sigma exist
                sigma = None
                for dist in model.random_variables.epsilons:
                    sigma = dist.variance
                assert sigma is not None

                if s.expression.is_Piecewise:
                    convert_piecewise(s, cg, model)
                else:
                    expr, error = find_term(model, s.expression, cg)
                    add_error_model(model, cg, expr, error, s.symbol.name)
                    add_error_relation(cg, error, s.symbol)
                    error_model_found = True

            else:
                expr = s.expression
                if expr.is_Piecewise:
                    first = True
                    for value, cond in expr.args:
                        if cond is not sympy.S.true:
                            if cond.atoms(sympy.Eq):
                                cond = convert_eq(cond)
                            if first:
                                cg.add(f'if ({cond}) {{')
                                first = False
                            else:
                                cg.add(f'}} else if ({cond}) {{')
                        else:
                            cg.add('} else {')
                            if "NEWIND" in [t.name for t in expr.free_symbols] and value == 0:
                                largest_value = expr.args[0].expr
                                largest_cond = expr.args[0].cond
                                for value, cond in expr.args[1:]:
                                    if cond is not sympy.S.true:
                                        if cond.rhs > largest_cond.rhs:
                                            largest_value = value
                                            largest_cond = cond
                                        elif cond.rhs == largest_cond.rhs:
                                            if not isinstance(cond, sympy.LessThan) and isinstance(
                                                largest_cond, sympy.LessThan
                                            ):
                                                largest_value = value
                                                largest_cond = cond
                                value = largest_value
                        cg.indent()
                        cg.add(f'{s.symbol.name} <- {value}')
                        cg.dedent()
                    cg.add('}')
                else:
                    cg.add(f'{s.symbol.name} <- {expr}')

    if dv_found and not error_model_found:
        error = {"add": None, "prop": None}
        add_error_relation(cg, error, dv)


def add_ode(model: pharmpy.model.Model, cg: CodeGenerator) -> None:
    """
    Add the ODEs from a model to a code generator

    Parameters
    ----------
    model : pharmpy.model.Model
        A pharmpy model object to add ODEs to.
    cg : CodeGenerator
        Codegenerator object holding the code to be added to.
    """
    amounts = [am.name for am in list(model.statements.ode_system.amounts)]
    printer = ExpressionPrinter(amounts)

    des = model.internals.DES
    statements = []
    if des:
        pattern = re.compile(r"DADT\(\d*\)")
        for s in des.statements:
            if not pattern.match(s.symbol.name):
                statements.append(s)
        add_statements(model, cg, statements)
    for eq in model.statements.ode_system.eqs:
        # Should remove piecewise from these equations in nlmixr
        if eq.atoms(sympy.Piecewise):
            lhs = remove_piecewise(printer.doprint(eq.lhs))
            rhs = remove_piecewise(printer.doprint(eq.rhs))

            cg.add(f'{lhs} = {rhs}')
        else:
            cg.add(f'{printer.doprint(eq.lhs)} = {printer.doprint(eq.rhs)}')


def remove_piecewise(expr: str) -> str:
    """
    Return an expression without Piecewise statements

    Parameters
    ----------
    expr : str
        A sympy expression, given as a string

    Returns
    -------
    str
        Return given expression but without Piecewise statements

    """
    all_piecewise = find_piecewise(expr)
    # Go into each piecewise found
    for p in all_piecewise:
        expr = piecewise_replace(expr, p, "")
    return expr


def find_piecewise(expr: str) -> list:
    """
    Locate all Piecewise statements in an expression and return them as a list

    Parameters
    ----------
    expr : str
        A sympy expression in string form

    Returns
    -------
    list
        A list of all piecewise statements found in the expression

    """
    d = find_parentheses(expr)

    piecewise_start = [m.start() + len("Piecewise") for m in re.finditer("Piecewise", expr)]

    all_piecewise = []
    for p in piecewise_start:
        if p in d:
            all_piecewise.append(expr[p + 1 : d[p]])
    return all_piecewise


def find_parentheses(s: str) -> dict:
    """
    Find all matching parenthesis in a given string

    Parameters
    ----------
    s : str
        Any string

    Returns
    -------
    dict
        A dictionary with keys corresponding to positions of the opening
        parenthesis and value being the position of the closing parenthesis.

    """
    start = []  # all opening parentheses
    d = {}

    for i, c in enumerate(s):
        if c == '(':
            start.append(i)
        if c == ')':
            try:
                d[start.pop()] = i
            except IndexError:
                print('Too many closing parentheses')
    if start:  # check if stack is empty afterwards
        print('Too many opening parentheses')

    return d


def piecewise_replace(expr: str, piecewise: sympy.Piecewise, s: str) -> str:
    """
    Will replace a given piecewise expression with wanted string, s

    Parameters
    ----------
    expr : str
        A string representive a sympy expression
    piecewise : sympy.Piecewise
        A sympy Piecewise statement to be changed
    s : str
        A string with wanted information to change piecewise to

    Returns
    -------
    str
        Expression with replaced piecewise expressions.

    """
    if s == "":
        expr = re.sub(r'([\+\-\/\*]\s*)(Piecewise)', r'\2', expr)
        return expr.replace(f'Piecewise({piecewise})', s)
    else:
        return expr.replace(f'Piecewise({piecewise})', s)


def convert_eq(cond: sympy.Eq) -> str:
    """
    Convert a sympy equal statement to R syntax

    Parameters
    ----------
    cond : sympy.Eq
        Sympy equals statement

    Returns
    -------
    str
        A string with R format for the same statement

    """
    cond = sympy.pretty(cond)
    cond = cond.replace("=", "==")
    cond = cond.replace("∧", "&")
    cond = cond.replace("∨", "|")
    cond = re.sub(r'(ID\s*==\s*)(\d+)', r"\1'\2'", cond)
    return cond
