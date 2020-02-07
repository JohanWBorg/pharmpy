import sympy
import sympy.stats as stats
from sympy.stats.rv import RandomSymbol

from .data_structures import OrderedSet


class JointDistributionSeparate(RandomSymbol):
    """One random variable in a joint distribution

       sympy can currently only represent the random variables in a joint distribution
       as one single indexed variable that cannot be separately named. This class
       makes separation possible.

       This class can probably not solve all issues with joint rvs, but it can at least
       handle seprate symbols, pass as a random variable for random_variables and lead back
       to its pspace.
    """
    def __new__(cls, name, joint_symbol):
        return super().__new__(cls, sympy.Symbol(name), joint_symbol.pspace)


def JointNormalSeparate(names, mean, cov):
    """Conveniently create a joint normal distribution and create separate random variables
    """
    x = stats.Normal('__DUMMY__', mean, cov)
    rvs = [JointDistributionSeparate(name, x) for name in names]
    return rvs


class RandomVariables(OrderedSet):
    """A set of random variables

       currently separately named jointrvs are not supported in sympy
       (i.e. it is not possible to do [eta1, eta2] = Normal(...))
       Current workaround for this is to put the same vectorized rv in
       multiple assignments so that the RandomVariables list would contain
       Assignment('ETA(1)', X[0])
       Assignment('ETA(2)', X[1])
    """
    @staticmethod
    def _rv_definition_string(rv):
        """ Return a pretty string of the definition of a random variable
        This should ideally be available from sympy.
        Currently supports Normal and JointNormal
        """
        dist = rv.pspace.distribution
        if isinstance(dist, stats.crv_types.NormalDistribution):
            return [f'{sympy.pretty(rv)} ~ 𝓝({sympy.pretty(dist.mean)}, '
                    f'{sympy.pretty(dist.std**2)})']
        elif isinstance(dist, stats.joint_rv_types.MultivariateNormalDistribution):
            mu_strings = sympy.pretty(dist.mu).split('\n')
            sigma_strings = sympy.pretty(dist.sigma).split('\n')
            mu_height = len(mu_strings)
            sigma_height = len(sigma_strings)
            max_height = max(mu_height, sigma_height)

            # Pad the smaller of the matrices
            if mu_height != sigma_height:
                to_pad = mu_strings if mu_strings < sigma_strings else sigma_strings
                num_lines = abs(mu_height - sigma_height)
                padding = ' ' * len(to_pad[0])
                for i in range(0, num_lines):
                    if i // 2 == 0:
                        to_pad.append(padding)
                    else:
                        to_pad.insert(0, padding)

            central_index = max_height // 2
            res = []
            symbol_padding = ' ' * len(f'{sympy.pretty(rv)} ~ ')
            for i, (mu_line, sigma_line) in enumerate(zip(mu_strings, sigma_strings)):
                if i == central_index:
                    res.append(f'{sympy.pretty(rv)} ~ 𝓝\N{SIX-PER-EM SPACE}(' +
                               mu_line + ', ' + sigma_line + ')')
                else:
                    res.append(symbol_padding + '    ' + mu_line + '  ' + sigma_line + ' ')

            return res

    def __getitem__(self, index):
        for e in self:
            if e == index or e.name == index:
                return e
        raise KeyError(f'Random variable "{index}" does not exist')

    def __repr__(self):
        """ Give a nicely formatted view of the definitions of all
            random variables.
        """
        res = ''
        for rv in self:
            lines = RandomVariables._rv_definition_string(rv)
            res += '\n'.join(lines) + '\n'
        return res
