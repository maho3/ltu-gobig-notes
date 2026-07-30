"""
Median-coverage heatmap grids for SBI posterior estimators across summaries
and k-cuts.

Produces one figure per parameter:
  - Rows = summaries (increasing feature complexity, top to bottom)
  - Cols = k-cuts for that summary, ordered left-to-right by increasing
    granularity (spectral information). Each row keeps its own k-cuts, so the
    columns are not shared across rows; every cell is titled with its own k-cut.
  - Each cell is a heatmap of median coverage over the (sigma_rad, sigma_tran)
    noise grid.

Summaries and k-cuts (including dynamic per-observable kmax cuts such as
kmin-0.0_kmax-zBk=0.2__zPk=0.4) are discovered from the model tree, so the
figure adapts to whatever combinations have been saved.

Figures are saved to FIG_DIR.
"""
import argparse
import os
import sys
from collections import defaultdict
from os.path import join, exists, dirname, abspath

import matplotlib as mpl
import matplotlib.pyplot as plt
import numpy as np
from tqdm import tqdm

sys.path.insert(0, dirname(abspath(__file__)))
from kcut_utils import (  # noqa: E402
    discover_summaries, discover_kcuts, pk_kmax, kcut_label, simple)

_STYLE = join(dirname(abspath(__file__)), 'style.mcstyle')
try:
    mpl.style.use(_STYLE)
except OSError:
    pass

# ---------------------------------------------------------------------------
# Configuration (defaults; overridden by CLI args)
# ---------------------------------------------------------------------------
WDIR = '/work/hdd/bdne/maho3/cmass-ili'
_DEFAULT_BASEDIR = f'{WDIR}/quijotelike/fastpm_charm6/models/galaxy'
_DEFAULT_TESTDIR = f'{WDIR}/quijote/nbody_hodz_gridnoise/models/galaxy'
_DEFAULT_NOISES = f'{WDIR}/noise_priors/noisegrid.csv'


def _parse_args():
    p = argparse.ArgumentParser()
    p.add_argument('--basedir', default=_DEFAULT_BASEDIR)
    p.add_argument('--testdir', default=_DEFAULT_TESTDIR)
    p.add_argument('--noises-path', default=_DEFAULT_NOISES)
    p.add_argument('--outdir', default='./figures')
    return p.parse_args()


PARAM_NAMES = [r'\Omega_m', r'\Omega_b', r'h', r'n_s', r'\sigma_8']
PARAM_IDXS = [0, 4]

_args = _parse_args()
BASEDIR = _args.basedir
TESTDIR_BASE = _args.testdir
NOISE_GRID_PATH = _args.noises_path
FIG_DIR = _args.outdir
SIM_TEST = '_'.join(
    [p for p in TESTDIR_BASE.rstrip('/').split('/') if p][-4:-2])

os.makedirs(FIG_DIR, exist_ok=True)

noises = np.loadtxt(NOISE_GRID_PATH, delimiter=',')
SIG_RAD = np.unique(noises[:, 0])
SIG_TRAN = np.unique(noises[:, 1])
N_RAD, N_TRAN = len(SIG_RAD), len(SIG_TRAN)


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------
def model_paths(s, kcut):
    train = join(BASEDIR, s, kcut)
    test = join(TESTDIR_BASE, s, kcut)
    return {
        'ood_samples': join(train, 'testing', SIM_TEST, 'posterior_samples.npy'),
        'theta_ood': join(test, 'theta_test.npy'),
        'noiseid_ood': join(test, 'noiseid_test.npy'),
    }


def median_coverage(samples, trues):
    """Fraction of trues below the posterior median."""
    medians = np.median(samples, axis=0)
    return (trues < medians).mean()


# ---------------------------------------------------------------------------
# Loader: per-(summary, kcut), compute a noise-grid heatmap for all params
# ---------------------------------------------------------------------------
def load_heatmaps(s, kcut, p_list):
    """Return dict[p] -> (N_TRAN, N_RAD) median-coverage heatmap, or None."""
    paths = model_paths(s, kcut)
    if not all(exists(paths[k]) for k in paths):
        return None
    try:
        samples = np.load(paths['ood_samples'])
        theta = np.load(paths['theta_ood'])
        noiseidx = np.load(paths['noiseid_ood'])[:, 0]
    except (OSError, ValueError, IndexError) as e:
        print(f'Error loading data for {s}, {kcut}: {e}')
        return None

    out = {p: np.full((N_TRAN, N_RAD), np.nan) for p in p_list}

    for n in range(len(noises)):
        idx = np.flatnonzero(noiseidx == n)
        if len(idx) == 0:
            continue
        ir = np.searchsorted(SIG_RAD, noises[n, 0])
        it = np.searchsorted(SIG_TRAN, noises[n, 1])
        # Pull the slice once per noise level, then index params from RAM
        s_ood = np.asarray(samples[:, idx, :])
        for p in p_list:
            out[p][it, ir] = median_coverage(s_ood[:, :, p], theta[idx, p])

    return out


# ---------------------------------------------------------------------------
# Discover summaries and their k-cuts from the model tree
# ---------------------------------------------------------------------------
SUMMARY_NAMES = discover_summaries(BASEDIR)
# per summary: ordered list of (kcut_dirname, kmin, kmax)
KCUTS = {s: discover_kcuts(join(BASEDIR, s)) for s in SUMMARY_NAMES}
SUMMARY_NAMES = [s for s in SUMMARY_NAMES if KCUTS[s]]

if not SUMMARY_NAMES:
    print(f'No summaries with k-cuts found under {BASEDIR}')
    sys.exit(0)

# Column layout: group columns by Pk cut so the Pk kmax aligns vertically across
# rows. Within a Pk group, one sub-column per k-cut (ordered by Bk cut, since
# KCUTS is granularity-sorted). Rows with fewer cuts at a given Pk (e.g. no Bk
# variants) leave the extra sub-columns blank, so every column holds a single
# Pk cut. COL_OF[s] maps a column index to that summary's k-cut for that column.
_pk_slots = {}                 # Pk cut -> max number of k-cuts at that Pk
_row_by_pk = {}                # summary -> {Pk cut: [(kcut, kmin, kmax), ...]}
for s in SUMMARY_NAMES:
    by_pk = defaultdict(list)
    for kcut, kmin, kmax in KCUTS[s]:
        by_pk[pk_kmax(kmax)].append((kcut, kmin, kmax))
    _row_by_pk[s] = by_pk
    for pk, lst in by_pk.items():
        _pk_slots[pk] = max(_pk_slots.get(pk, 0), len(lst))

_col_base, _c = {}, 0
for pk in sorted(_pk_slots):
    _col_base[pk] = _c
    _c += _pk_slots[pk]
NCOLS = _c

COL_OF = {}                    # summary -> {col index: (kcut, kmin, kmax)}
for s in SUMMARY_NAMES:
    m = {}
    for pk, lst in _row_by_pk[s].items():
        for i, item in enumerate(lst):
            m[_col_base[pk] + i] = item
    COL_OF[s] = m

# For labelling: first present column per row, and lowest present row per column.
FIRST_COL = {s: min(COL_OF[s]) for s in SUMMARY_NAMES}
LAST_ROW_OF_COL = {}
for r, s in enumerate(SUMMARY_NAMES):
    for c in COL_OF[s]:
        LAST_ROW_OF_COL[c] = r

print(f'Discovered {len(SUMMARY_NAMES)} summaries; {NCOLS} Pk-aligned columns.')

# ---------------------------------------------------------------------------
# Build cache once: (summary, kcut) -> {p: heatmap} or None
# ---------------------------------------------------------------------------
print('Loading all (summary, k-cut) combinations...')
cache = {}
for s in tqdm(SUMMARY_NAMES):
    for kcut, _, _ in KCUTS[s]:
        cache[(s, kcut)] = load_heatmaps(s, kcut, PARAM_IDXS)


# ---------------------------------------------------------------------------
# Plot: Median-coverage heatmap grids
# ---------------------------------------------------------------------------
_rad_ticks = [0, N_RAD // 2, N_RAD - 1] if N_RAD > 2 else list(range(N_RAD))
_tran_ticks = [0, N_TRAN // 2, N_TRAN - 1] if N_TRAN > 2 else list(range(N_TRAN))

for p_idx in PARAM_IDXS:
    nrows = len(SUMMARY_NAMES)
    fig, axs = plt.subplots(nrows, NCOLS,
                            figsize=(2.5 * NCOLS, 2.5 * nrows),
                            squeeze=False)
    im = None
    for r, s in enumerate(SUMMARY_NAMES):
        colmap = COL_OF[s]
        for c in range(NCOLS):
            ax = axs[r, c]
            if c not in colmap:
                ax.set_visible(False)
                continue
            kcut, kmin, kmax = colmap[c]
            res = cache.get((s, kcut))
            hm = res[p_idx] if (res is not None and p_idx in res) else None

            if hm is None or np.all(np.isnan(hm)):
                print(f'No valid data for {s}, {kcut}')
                ax.text(0.5, 0.5, 'N/A', ha='center', va='center',
                        transform=ax.transAxes)
                ax.set_xticks([])
                ax.set_yticks([])
            else:
                im = ax.imshow(hm, vmin=0, vmax=1, cmap='RdBu', origin='upper')
                ax.set_xticks(_rad_ticks)
                ax.set_yticks(_tran_ticks)
                ax.set_xticklabels([f'{SIG_RAD[i]:.2f}' for i in _rad_ticks],
                                   fontsize=7)
                ax.set_yticklabels([f'{SIG_TRAN[i]:.2f}' for i in _tran_ticks],
                                   fontsize=7)

            ax.set_title(kcut_label(kmin, kmax, multiline=False), fontsize=8)
            if c == FIRST_COL[s]:
                ax.set_ylabel(simple(s) + '\n' + r'$\sigma_{\rm tran}$',
                              fontsize=9)
            if r == LAST_ROW_OF_COL[c]:
                ax.set_xlabel(r'$\sigma_{\rm rad}$', fontsize=9)

    if im is not None:
        fig.colorbar(
            im, ax=axs,
            label=f'Median coverage (${PARAM_NAMES[p_idx]}$)',
            fraction=0.02, pad=0.02)
    fig.suptitle(f'Median coverage — ${PARAM_NAMES[p_idx]}$', fontsize=14)
    fname = join(FIG_DIR, f'median_coverage_p{p_idx}.jpg')
    fig.savefig(fname, dpi=100, bbox_inches='tight')
    print(f'Saved {fname}')

plt.show()
