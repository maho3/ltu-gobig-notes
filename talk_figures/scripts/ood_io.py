"""Loader and shared helpers for the OOD talk figures."""

import numpy as np
import pandas as pd
from os.path import join, dirname, abspath

CACHEDIR = join(dirname(dirname(abspath(__file__))), 'cache')
NOISE_PATH = '/work/hdd/bdne/maho3/cmass-ili/noise_priors/noisegrid.csv'
COSM_TABLE = '/work/hdd/bdne/maho3/cmass-ili/scratch/abacus_custom_table.csv'

# Least-biased noise configuration in each grid, chosen as the bin minimising
# |median coverage - 0.5| summed over Omega_m and sigma_8. See pick_noise().
GOOD_NOISE = {'quijote': 27, 'abacus': 22}

PARAM_LABEL = {
    'Omega_m': r'$\Omega_m$', 'Omega_b': r'$\Omega_b$', 'h': r'$h$',
    'n_s': r'$n_s$', 'sigma8': r'$\sigma_8$',
    'sig_rad': r'$\sigma_{\rm rad}$', 'sig_tran': r'$\sigma_{\rm tran}$',
    'alpha': r'$\alpha$', 'conc_gal_bias_satellites': r'$c_{\rm sat}$',
    'eta_vb_centrals': r'$\eta_{vb}^{\rm cen}$',
    'eta_vb_satellites': r'$\eta_{vb}^{\rm sat}$',
    'logM0': r'$\log M_0$', 'logM1': r'$\log M_1$',
    'logMmin': r'$\log M_{\rm min}$',
    'assembias_cen': r'$A_{\rm cen}$', 'assembias_sat': r'$A_{\rm sat}$',
    'sigma_logM': r'$\sigma_{\log M}$',
}
COSMO_IDX = [0, 1, 2, 3, 4]
OM, S8 = 0, 4


def load(tag):
    """Cache dict for 'quijote' or 'abacus'."""
    d = np.load(join(CACHEDIR, f'ood_{tag}.npz'), allow_pickle=True)
    return {k: d[k] for k in d.files}


def noises():
    """(49, 2) array of (sigma_rad, sigma_tran)."""
    return np.loadtxt(NOISE_PATH, delimiter=',')


def label(name):
    return PARAM_LABEL.get(str(name), str(name))


def pick_noise(d, params=(OM, S8)):
    """Rank noise bins by |median coverage - 0.5| summed over `params`.
    Returns a list of (score, n, sig_rad, sig_tran), best first."""
    ng = noises()
    med, th, ni = d['percs'][0], d['theta'], d['noiseidx']
    out = []
    for n in range(len(ng)):
        m = ni == n
        if not m.any():
            continue
        score = sum(abs((th[m, p] < med[m, p]).mean() - 0.5) for p in params)
        out.append((score, n, ng[n, 0], ng[n, 1]))
    return sorted(out)


def marginal_coverage(ranks, nbins=20):
    """Expected-coverage curve from cached PIT ranks, with binomial errors.

    Matches `marginal_coverage` in ltu-gobig-notes/scripts/ood_noise_inference.py.
    """
    centers = 0.5 * (np.linspace(0, 1, nbins + 1)[:-1]
                     + np.linspace(0, 1, nbins + 1)[1:])
    cov = (ranks[None, :] <= centers[:, None]).mean(axis=1)
    err = np.sqrt(cov * (1 - cov) / len(ranks))
    return centers, cov, err


def coverage_bias(theta, med, noiseidx, p, n_noise=49):
    """Per-noise-bin signed calibration bias of parameter `p`, on [-1, 1].

    cell = 2 * (median coverage - 0.5), where median coverage is the statistic
    used by the notes' heatmaps (scripts/noise_calibration_all.py): the fraction
    of test points whose truth lies below the posterior median. Rescaling puts
    0 at unbiased and +/-1 at 'every test point on one side'; positive means the
    posterior median sits above the truth, i.e. the parameter is over-predicted.
    """
    out = {}
    for n in range(n_noise):
        m = noiseidx == n
        if m.any():
            out[n] = 2.0 * ((theta[m, p] < med[m, p]).mean() - 0.5)
    return out


def noise_grid(values, ng):
    """Pivot a per-noise-bin quantity onto the (sigma_tran, sigma_rad) grid."""
    rad = np.sort(np.unique(ng[:, 0]))
    tran = np.sort(np.unique(ng[:, 1]))
    grid = np.full((len(tran), len(rad)), np.nan)
    for n, v in values.items():
        i = np.searchsorted(tran, ng[n, 1])
        j = np.searchsorted(rad, ng[n, 0])
        grid[i, j] = v
    return grid, rad, tran


def cosm_classes(ids):
    """Abacus cosmology-class boolean masks aligned to `ids`.

    Three disjoint classes: LCDM without massive neutrinos, LCDM with massive
    neutrinos, and everything else. Note this differs slightly from
    scripts/ood_abacus_inference.py, whose 'mnu' mask is every massive-neutrino
    sim including non-LCDM ones, so its masks overlap and a non-LCDM sim with
    massive neutrinos is drawn twice. Here each test point belongs to exactly
    one class.
    """
    cosm = pd.read_csv(COSM_TABLE)
    idx_lcdm = set(np.argwhere(cosm['LCDM'] == 'y').flatten().tolist())
    idx_mnu = set(np.argwhere(cosm['Massive Neutrinos'] == 'y').flatten().tolist())
    i = ids.astype(int)
    is_lcdm = np.array([v in idx_lcdm for v in i])
    has_mnu = np.array([v in idx_mnu for v in i])
    return {
        'simple':   is_lcdm & ~has_mnu,
        'mnu':      is_lcdm & has_mnu,
        'non_lcdm': ~is_lcdm,
    }


# ── shared drawing helper ─────────────────────────────────────────────────────

def draw_error_heatmap(fig, ax, grid, rad, tran, cbar_label,
                       vmin=None, vmax=None, fmt='{:+.2f}'):
    """Noise-grid heatmap of a signed error on a linear diverging scale.

    The norm is linear and symmetric about zero so that colorbar tick positions
    correspond to the colours they sit next to. (An earlier TwoSlopeNorm here
    used the full colour range on one-signed data, but made the mapping
    piecewise-linear, which desynchronised the colorbar labels and saturated
    near-zero cells of the minority sign.)

    Pass vmin/vmax to fix the scale; otherwise it is +/- max|grid|.
    """
    import matplotlib.colors as mcolors

    if vmin is None or vmax is None:
        lim = float(np.nanmax(np.abs(grid)))
        vmin, vmax = -lim, lim
    norm = mcolors.Normalize(vmin=vmin, vmax=vmax)
    im = ax.imshow(grid, cmap='RdBu', norm=norm, origin='upper')

    for i in range(grid.shape[0]):
        for j in range(grid.shape[1]):
            if np.isnan(grid[i, j]):
                continue
            rgba = im.cmap(norm(grid[i, j]))
            lum = 0.299 * rgba[0] + 0.587 * rgba[1] + 0.114 * rgba[2]
            ax.text(j, i, fmt.format(grid[i, j]), ha='center', va='center',
                    fontsize=10, color='w' if lum < 0.5 else '0.15')

    ax.set_xticks(range(len(rad)))
    ax.set_xticklabels([f'{v:.2f}' for v in rad])
    ax.set_yticks(range(len(tran)))
    ax.set_yticklabels([f'{v:.2f}' for v in tran])
    ax.set_xlabel(r'$\sigma_{\rm rad}$')
    ax.set_ylabel(r'$\sigma_{\rm tran}$')
    ax.grid(False)
    ax.tick_params(which='minor', bottom=False, left=False, top=False,
                   right=False)

    cb = fig.colorbar(im, ax=ax, fraction=0.046, pad=0.03)
    cb.set_label(cbar_label)
    return im


# Colorbar label shared by the sigma_8 bias heatmaps (figs 6 and 8), so the two
# figures carry identical axes and legend text.
BIAS_LABEL = r'$2\,($median coverage$\,-\,0.5)$'


def corner_range(samples, truth, q=(0.5, 99.5), pad=0.06):
    """Per-parameter axis ranges for corner.corner that always contain the
    truth. corner's default range comes from the samples alone, so a truth
    outside the posterior bulk is silently clipped out of its row and column.
    """
    out = []
    for k in range(samples.shape[1]):
        lo, hi = np.percentile(samples[:, k], q)
        lo, hi = min(lo, truth[k]), max(hi, truth[k])
        w = (hi - lo) or abs(hi) or 1.0
        out.append((lo - pad * w, hi + pad * w))
    return out
