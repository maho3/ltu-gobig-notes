"""Load the fiducial-stdev cache written by build_cache.py, plus talk labels."""

import json
from os.path import join, dirname, abspath

CACHEDIR = join(dirname(dirname(abspath(__file__))), 'cache')

# Slide-friendly summary labels. Everything here is redshift-space; say so in
# the axis label or caption rather than carrying a 'z' on every symbol.
LABEL = {
    'zPk0':                   r'$P_0$',
    'zPk0+zPk2+zPk4':         r'$P_{0,2,4}$',
    'zPk0+zPk2+zPk4+zEqBk0':  r'$P_{0,2,4}+B_0^{\rm eq}$',
    'zPk0+zPk2+zPk4+zSqBk0':  r'$P_{0,2,4}+B_0^{\rm sq}$',
    'zPk0+zPk2+zPk4+zBk0':    r'$P_{0,2,4}+B_0$',
}
# Compact form for categorical axes, where the common prefix is redundant.
LABEL_SHORT = {
    'zPk0':                   r'$P_0$',
    'zPk0+zPk2+zPk4':         r'$P_{0,2,4}$',
    'zPk0+zPk2+zPk4+zEqBk0':  r'$+\,B_0^{\rm eq}$',
    'zPk0+zPk2+zPk4+zSqBk0':  r'$+\,B_0^{\rm sq}$',
    'zPk0+zPk2+zPk4+zBk0':    r'$+\,B_0$',
}
SUBLABEL = {
    'zPk0':                   'monopole',
    'zPk0+zPk2+zPk4':         'multipoles',
    'zPk0+zPk2+zPk4+zEqBk0':  'equilateral',
    'zPk0+zPk2+zPk4+zSqBk0':  'squeezed',
    'zPk0+zPk2+zPk4+zBk0':    'full bispec.',
}
# Order of increasing spectral information, as used by the notes' feature sweep.
FEAT_ORDER = ['zPk0', 'zPk0+zPk2+zPk4', 'zPk0+zPk2+zPk4+zEqBk0',
              'zPk0+zPk2+zPk4+zSqBk0', 'zPk0+zPk2+zPk4+zBk0']


def load(nbody, sim):
    with open(join(CACHEDIR, f'{nbody}__{sim}.json')) as f:
        return json.load(f)


def entries(nbody, sim, summary=None):
    """Cache entries, optionally filtered to one summary, ordered by k-cut
    granularity (increasing Pk cut, then increasing Bk cut)."""
    e = load(nbody, sim)['entries']
    if summary is not None:
        e = [x for x in e if x['summary'] == summary]
    return sorted(e, key=lambda x: (x['pk_kmax'], x['bk_kmax'] or 0.0))


def select(nbody, sim, summary, ref_pk_kmax):
    """Entry whose Pk kmax is closest to ref_pk_kmax, ties broken toward the
    smaller Bk cut — same rule as kcut_utils.select_kcut."""
    e = entries(nbody, sim, summary)
    if not e:
        return None
    return min(e, key=lambda x: (abs(x['pk_kmax'] - ref_pk_kmax),
                                 x['pk_kmax'], x['bk_kmax'] or 0.0))


def yerr(entry, p):
    """(lower, upper) error-bar lengths for param index p."""
    q = entry['params'][str(p)]
    return q['med'] - q['lo'], q['hi'] - q['med']


def med(entry, p):
    return entry['params'][str(p)]['med']
