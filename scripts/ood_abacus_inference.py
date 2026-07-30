"""
Out-of-distribution inference evaluation on the Abacus test set.

Unlike the standard OOD script, this variant:
  - Skips coverage / heatmap plots (Abacus priors are non-uniform)
  - Colors true-vs-pred points by cosmology type:
      simple   — LCDM, Mnu = 0
      mnu      — LCDM, Mnu > 0
      non_lcdm — not LCDM
  - Reads cosmology metadata from abacus_custom_table.csv

Usage:
    python scripts/ood_abacus_inference.py [--basedir ...] [--testdir ...]
                                           [--noises-path ...] [--outdir ...]
                                           [--cosm-table ...]
"""

import argparse
import matplotlib.pyplot as plt
import matplotlib
import numpy as np
import os
import sys
import pandas as pd
from os.path import join, dirname, abspath

sys.path.insert(0, dirname(abspath(__file__)))
from kcut_utils import (  # noqa: E402
    discover_summaries, discover_kcuts, pk_kmax, kcut_label)

# ── Configuration (defaults; overridden by CLI args) ──────────────────────────

_WDIR = '/work/hdd/bdne/maho3/cmass-ili'
_DEFAULT_BASEDIR = f'{_WDIR}/quijotelike/fastpm_charm6/models/galaxy'
_DEFAULT_TESTDIR = f'{_WDIR}/abacus1gpch/custom_hodz_gridnoise/models/galaxy'
_DEFAULT_NOISES_PATH = f'{_WDIR}/noise_priors/noisegrid.csv'
_DEFAULT_COSM_TABLE = f'{_WDIR}/scratch/abacus_custom_table.csv'


def _parse_args():
    p = argparse.ArgumentParser()
    p.add_argument('--basedir',     default=_DEFAULT_BASEDIR)
    p.add_argument('--testdir',     default=_DEFAULT_TESTDIR)
    p.add_argument('--noises-path', default=_DEFAULT_NOISES_PATH)
    p.add_argument('--cosm-table',  default=_DEFAULT_COSM_TABLE)
    p.add_argument(
        '--outdir', default=join(os.path.dirname(os.path.abspath(__file__)), 'figures'))
    return p.parse_args()

# ──────────────────────────────────────────────────────────────────────────────


matplotlib.use('Agg')
matplotlib.rcParams.update({
    'font.size': 13,
    'axes.titlesize': 13,
    'axes.labelsize': 13,
    'xtick.labelsize': 11,
    'ytick.labelsize': 11,
    'legend.fontsize': 11,
})

PARAM_NAMES = [r'\Omega_m', r'\Omega_b', r'h', r'n_s', r'\sigma_8']
PARAM_INDICES = [0, 4]  # Omega_m and sigma_8

# Mahalanobis metric used for the LCDM z-heatmaps (rendered on the figures).
_Z_EQUATION = (r'$z=\sqrt{\mathbf{d}^{\mathsf{T}}\,\mathbf{C}^{-1}\,\mathbf{d}}$,  '
               r'$\mathbf{d}=\theta_{\rm true}-\hat{\theta}$,  '
               r'$\mathbf{C}=\mathrm{Cov}(\Omega_m,\sigma_8)$')

# Cosmology class styles: (color, marker, label)
# Plot order: non-LCDM, Mnu>0, simple — so the rarest classes land on top
COSM_STYLES = [
    ('non_lcdm', '#2ca02c', 's', 'non-LCDM'),   # green square
    ('mnu',      '#ff7f0e', '^', 'LCDM Mnu>0'),  # orange triangle
    ('simple',   '#1f77b4', 'o', 'LCDM Mnu=0'),  # blue circle
]


def _cosm_classes(cosm_table_path, ids_test):
    """Return dict of bool masks aligned to ids_test, keyed by class name."""
    cosm = pd.read_csv(cosm_table_path)
    idx_lcdm   = np.argwhere(cosm['LCDM'] == 'y').flatten().tolist()
    idx_mnu    = np.argwhere(cosm['Massive Neutrinos'] == 'y').flatten().tolist()
    idx_simple = list(set(idx_lcdm) - set(idx_mnu))

    # ids_test are stored as strings in the .npy file; cast to int before lookup
    ids_int = ids_test.astype(int)

    return {
        'simple':   np.array([i in idx_simple   for i in ids_int]),
        'mnu':      np.array([i in idx_mnu       for i in ids_int]),
        'non_lcdm': np.array([i not in idx_lcdm  for i in ids_int]),
    }


def _jitter(x, scale=0.002, seed=0):
    rng = np.random.default_rng(seed)
    return x + rng.uniform(-scale, scale, size=x.shape)


def load_data(basedir, testdir, s, kstr, cosm_table_path):
    """Load theta, noiseidx, OOD samples, self-consistent samples, and cosm masks."""
    sim = '_'.join(testdir.rstrip('/').split('/')[-4:-2])

    theta = np.load(join(testdir, s, kstr, 'theta_test.npy'))
    ids   = np.load(join(testdir, s, kstr, 'ids_test.npy'))

    noiseid_path = join(testdir, s, kstr, 'noiseid_test.npy')
    if not os.path.exists(noiseid_path):
        noiseid_path = join(testdir, s, kstr, 'noiseids_test.npy')
    noiseidx = np.load(noiseid_path)[:, 0]

    samples_path = join(basedir, s, kstr, 'testing', sim, 'posterior_samples.npy')
    samples = np.load(samples_path)

    percs = np.percentile(samples, q=[50, 16, 84], axis=0)
    percs[1] = percs[0] - percs[1]
    percs[2] = percs[2] - percs[0]

    theta_self   = np.load(join(basedir, s, kstr, 'theta_test.npy'))
    samples_self = np.load(join(basedir, s, kstr, 'posterior_samples.npy'))
    percs_self   = np.percentile(samples_self, q=[50, 16, 84], axis=0)
    percs_self[1] = percs_self[0] - percs_self[1]
    percs_self[2] = percs_self[2] - percs_self[0]

    masks = _cosm_classes(cosm_table_path, ids)

    return (theta, noiseidx, ids, samples, percs,
            theta_self, samples_self, percs_self, masks)


def _scatter_cosm(ax, theta_x, pred_y, yerr_lo, yerr_hi, masks,
                  jitter_scale=0.002, ms=4):
    """Plot errorbar points colored/shaped by cosmology class onto ax."""
    for key, color, marker, label in COSM_STYLES:
        sel = masks[key]
        if not sel.any():
            continue
        x = _jitter(theta_x[sel], scale=jitter_scale)
        ax.errorbar(x, pred_y[sel],
                    yerr=[yerr_lo[sel], yerr_hi[sel]],
                    fmt=marker, color=color, label=label,
                    ms=ms, mew=1.2, alpha=0.8,
                    elinewidth=0.8, capsize=0)


def plot_all_noise_true_vs_pred(theta, percs, noiseidx, noises, masks, p, s, figdir):
    """Grid of true-vs-pred across all noise configs, colored by cosm class."""
    n_noise = len(noises)
    ncols = int(np.round(np.sqrt(n_noise)))
    nrows = int(np.ceil(n_noise / ncols))

    minmax = np.array([theta.min(axis=0), theta.max(axis=0)])
    # jitter scale relative to param range
    jitter_scale = (minmax[1, p] - minmax[0, p]) * 0.01

    f, axs = plt.subplots(nrows, ncols, figsize=(3*ncols, 3*nrows),
                          sharex=True, sharey=True)
    axs = axs.flatten()

    for i in range(n_noise):
        idx_all = np.argwhere(noiseidx == i).flatten()
        ax = axs[i]
        if len(idx_all) == 0:
            ax.set_visible(False)
            continue

        np.random.seed(42)
        idx = np.random.choice(idx_all, min(50, len(idx_all)), replace=False)

        ax.plot(minmax[:, p], minmax[:, p], 'k--', lw=1)

        # sub-masks restricted to this noise bin
        sub_masks = {k: v[idx] for k, v in masks.items()}
        _scatter_cosm(ax,
                      theta[idx, p], percs[0][idx, p],
                      percs[1][idx, p], percs[2][idx, p],
                      sub_masks, jitter_scale=jitter_scale, ms=3)

        ax.set_title(f'$\\sigma_r={noises[i,0]:.2f}$ $\\sigma_t={noises[i,1]:.2f}$',
                     fontsize=9)
        if i % ncols == 0:
            ax.set_ylabel(f'Pred ${PARAM_NAMES[p]}$')
        if i // ncols == nrows - 1:
            ax.set_xlabel(f'True ${PARAM_NAMES[p]}$')

    for i in range(n_noise, len(axs)):
        axs[i].set_visible(False)

    handles = [
        plt.Line2D([0], [0], marker=mk, color='w', markerfacecolor=col,
                   markeredgecolor=col, markersize=6, label=lbl)
        for _, col, mk, lbl in COSM_STYLES
    ]
    axs[0].legend(handles=handles, fontsize=7, loc='upper left')

    f.suptitle(f'{s}  ${PARAM_NAMES[p]}$', fontsize=16)
    plt.tight_layout()
    pname = 'Om' if p == 0 else 's8'
    fname = join(figdir, f'pred_{pname}.jpg')
    f.savefig(fname, dpi=100, bbox_inches='tight')
    plt.close(f)
    print(f'  Saved {fname}')


def plot_single_noise_scatter(theta, percs, theta_self, percs_self, masks,
                               noiseidx, noises, n, s, figdir):
    """True vs predicted scatter at one noise index, colored by cosm class."""
    idx_all = np.argwhere(noiseidx == n).flatten()
    Nplot = min(50, len(idx_all))
    np.random.seed(42)
    idx = np.random.choice(idx_all, Nplot, replace=False)
    idx_self = np.random.choice(len(theta_self), Nplot, replace=False)

    minmax = np.array([theta.min(axis=0), theta.max(axis=0)])

    f, axs = plt.subplots(1, 2, figsize=(10, 5))
    for i, j in enumerate(PARAM_INDICES):
        ax = axs[i]
        ax.plot(minmax[:, j], minmax[:, j], 'k--')

        jitter_scale = (minmax[1, j] - minmax[0, j]) * 0.01

        # Self-consistent in grey behind everything
        ax.errorbar(theta_self[idx_self, j], percs_self[0][idx_self, j],
                    yerr=[percs_self[1][idx_self, j], percs_self[2][idx_self, j]],
                    fmt='o', color='grey', alpha=0.4, label='Self', ms=4,
                    elinewidth=0.8, capsize=0)

        sub_masks = {k: v[idx] for k, v in masks.items()}
        _scatter_cosm(ax,
                      theta[idx, j], percs[0][idx, j],
                      percs[1][idx, j], percs[2][idx, j],
                      sub_masks, jitter_scale=jitter_scale, ms=5)

        ax.set(xlabel=f'True ${PARAM_NAMES[j]}$',
               ylabel=f'Predicted ${PARAM_NAMES[j]}$')

        handles = [plt.Line2D([0], [0], marker='o', color='w',
                               markerfacecolor='grey', markersize=6, label='Self')]
        handles += [
            plt.Line2D([0], [0], marker=mk, color='w', markerfacecolor=col,
                       markeredgecolor=col, markersize=6, label=lbl)
            for _, col, mk, lbl in COSM_STYLES
        ]
        ax.legend(handles=handles, fontsize=9)

    f.suptitle(
        f'{s}\n'
        f'$\\sigma_{{\\rm rad}}={noises[n,0]:.2f}$  '
        f'$\\sigma_{{\\rm tran}}={noises[n,1]:.2f}$'
    )
    plt.tight_layout()
    fname = join(figdir, f'scatter_n{n}.jpg')
    f.savefig(fname, dpi=100, bbox_inches='tight')
    plt.close(f)
    print(f'  Saved {fname}')


def plot_residuals(theta, percs, theta_self, percs_self, masks,
                   noiseidx, noises, n, s, figdir):
    """Residual plots at one noise index, colored by cosm class."""
    idx_all = np.argwhere(noiseidx == n).flatten()
    np.random.seed(42)
    idx_plot = np.random.choice(idx_all, min(100, len(idx_all)), replace=False)
    idx_self_all  = np.arange(len(theta_self))
    idx_self_plot = np.random.choice(idx_self_all, min(len(idx_all), len(idx_self_all)),
                                     replace=False)

    fig, axs = plt.subplots(2, 2, figsize=(11, 8),
                            gridspec_kw={'width_ratios': [3, 1]},
                            sharey='row')
    for i, j in enumerate(PARAM_INDICES):
        residuals_all  = percs[0][idx_all, j]  - theta[idx_all, j]
        residuals_self = percs_self[0][idx_self_all, j] - theta_self[idx_self_all, j]

        minmax_j = theta[:, j].max() - theta[:, j].min()
        jitter_scale = minmax_j * 0.01

        ax = axs[i, 0]
        ax.axhline(0, c='k', ls='--')

        ax.errorbar(theta_self[idx_self_plot, j],
                    percs_self[0][idx_self_plot, j] - theta_self[idx_self_plot, j],
                    yerr=[percs_self[1][idx_self_plot, j], percs_self[2][idx_self_plot, j]],
                    fmt='o', color='grey', alpha=0.4, label='Self', ms=3,
                    elinewidth=0.8, capsize=0)

        sub_masks = {k: v[idx_plot] for k, v in masks.items()}
        _scatter_cosm(ax,
                      theta[idx_plot, j],
                      percs[0][idx_plot, j] - theta[idx_plot, j],
                      percs[1][idx_plot, j], percs[2][idx_plot, j],
                      sub_masks, jitter_scale=jitter_scale, ms=4)

        ax.set(xlabel=f'True ${PARAM_NAMES[j]}$',
               ylabel=f'Predicted - True ${PARAM_NAMES[j]}$')

        handles = [plt.Line2D([0], [0], marker='o', color='w',
                               markerfacecolor='grey', markersize=6, label='Self')]
        handles += [
            plt.Line2D([0], [0], marker=mk, color='w', markerfacecolor=col,
                       markeredgecolor=col, markersize=6, label=lbl)
            for _, col, mk, lbl in COSM_STYLES
        ]
        ax.legend(handles=handles, fontsize=8)

        ax_hist = axs[i, 1]
        ax_hist.hist(residuals_all,  bins=15, orientation='horizontal',
                     alpha=0.5, label='OOD',  density=True)
        ax_hist.hist(residuals_self, bins=15, orientation='horizontal',
                     alpha=0.5, label='Self', density=True)
        ax_hist.axhline(0, c='k', ls='--')
        ax_hist.set_xlabel('Count')
        ax_hist.tick_params(labelleft=False)
        medcov      = np.sum(residuals_all  < 0) / len(residuals_all)
        medcov_self = np.sum(residuals_self < 0) / len(residuals_self)
        ax_hist.set_title(f'{medcov*100:.1f}% / {medcov_self*100:.1f}%')
        ax_hist.legend(fontsize=8)

        ylim = 0.15 if i == 0 else 0.25
        ax.set_ylim(-ylim, ylim)

    fig.suptitle(
        f'{s}\n'
        f'$\\sigma_{{\\rm rad}}={noises[n,0]:.2f}$  '
        f'$\\sigma_{{\\rm tran}}={noises[n,1]:.2f}$'
    )
    plt.tight_layout()
    fname = join(figdir, f'residuals_n{n}.jpg')
    fig.savefig(fname, dpi=100, bbox_inches='tight')
    plt.close(fig)
    print(f'  Saved {fname}')


def _compute_lcdm_z(theta, percs, samples, noiseidx, n_noise, masks):
    """Mean joint Mahalanobis distance for LCDM Mnu=0 cosmologies per noise bin.

    For each test point, z = sqrt( d^T C^-1 d ), where d = theta_true - median
    over (Omega_m, sigma_8) and C is the 2x2 posterior covariance of those two
    parameters estimated from the samples. This uses the full covariance,
    including the Omega_m-sigma_8 correlation, rather than assuming a diagonal
    (per-parameter) covariance. Returns array of shape (n_noise,), NaN where no
    LCDM Mnu=0 points exist.
    """
    simple_mask = masks['simple']
    z_per_noise = np.full(n_noise, np.nan)
    for i in range(n_noise):
        sel = np.where(noiseidx == i)[0]
        sel_s = sel[simple_mask[sel]]
        if len(sel_s) == 0:
            continue
        zvals = []
        for pt in sel_s:
            d = theta[pt, PARAM_INDICES] - percs[0][pt, PARAM_INDICES]
            # samples: (n_draws, n_test, n_params) -> (n_draws, 2) for this point
            cov = np.cov(samples[:, pt][:, PARAM_INDICES], rowvar=False)
            try:
                cinv = np.linalg.inv(cov)
            except np.linalg.LinAlgError:
                cinv = np.linalg.pinv(cov)
            zvals.append(np.sqrt(d @ cinv @ d))
        z_per_noise[i] = np.mean(zvals)
    return z_per_noise


def _noise_pivot(noises, values):
    """Reshape flat (n_noise,) values into a 2D grid keyed by (σ_rad, σ_tran).

    Returns (grid, rad_vals, tran_vals) where grid[i, j] corresponds to
    rad_vals[i] and tran_vals[j].
    """
    rad_vals  = np.unique(noises[:, 0])
    tran_vals = np.unique(noises[:, 1])
    grid = np.full((len(rad_vals), len(tran_vals)), np.nan)
    for k, (r, t) in enumerate(noises):
        i = np.searchsorted(rad_vals,  r)
        j = np.searchsorted(tran_vals, t)
        grid[i, j] = values[k]
    return grid, rad_vals, tran_vals


def _draw_z_heatmap(ax, grid, rad_vals, tran_vals, vmax=4.0):
    """Draw a z-score noise-grid heatmap onto ax. Returns the image artist."""
    im = ax.imshow(grid, aspect='auto', origin='lower',
                   vmin=0, vmax=vmax, cmap='RdYlGn_r',
                   extent=[-0.5, len(tran_vals) - 0.5,
                            -0.5, len(rad_vals)  - 0.5])
    # mark the 2-sigma boundary
    if not np.all(np.isnan(grid)):
        try:
            ax.contour(grid, levels=[2.0], colors='k', linewidths=1.2)
        except Exception:
            pass
    return im


def plot_lcdm_z_heatmap(z_per_noise, noises, s, kstr, figdir):
    """Per-noise-config heatmap of mean LCDM Mnu=0 joint z-score."""
    grid, rad_vals, tran_vals = _noise_pivot(noises, z_per_noise)

    fig, ax = plt.subplots(figsize=(max(4, len(tran_vals) * 0.6 + 1.5),
                                    max(3, len(rad_vals)  * 0.6 + 1.5)))
    im = _draw_z_heatmap(ax, grid, rad_vals, tran_vals)

    ax.set_xticks(range(len(tran_vals)))
    ax.set_xticklabels([f'{v:.2f}' for v in tran_vals], rotation=45, ha='right')
    ax.set_yticks(range(len(rad_vals)))
    ax.set_yticklabels([f'{v:.2f}' for v in rad_vals])
    ax.set_xlabel(r'$\sigma_{\rm tran}$')
    ax.set_ylabel(r'$\sigma_{\rm rad}$')
    ax.set_title(f'Mahalanobis $\\bar{{z}}$ (LCDM $M_\\nu=0$)\n{s}  {kstr}\n'
                 f'{_Z_EQUATION}', fontsize=9)

    plt.colorbar(im, ax=ax, label=r'$\bar{z}$')
    plt.tight_layout()
    fname = join(figdir, 'lcdm_z_heatmap.png')
    fig.savefig(fname, dpi=100, bbox_inches='tight')
    plt.close(fig)
    print(f'  Saved {fname}')


def plot_global_z_heatmap(results, kcuts_by_summary, noises, figroot):
    """Global multi-panel z-score heatmap: rows=summaries, cols=k-cuts.

    Columns are grouped by Pk cut so the Pk kmax aligns vertically across rows.
    Within a Pk group, one sub-column per k-cut (ordered by Bk cut); rows with
    fewer cuts at a given Pk (e.g. no Bk variants) leave the extra sub-columns
    blank, so every column holds a single Pk cut. Each cell is the noise-grid
    heatmap of mean LCDM Mnu=0 z-score, with a black contour at z=2.
    """
    _, rad_vals, tran_vals = _noise_pivot(noises, np.zeros(len(noises)))
    present_summ = [s for s, kcuts in kcuts_by_summary.items()
                    if any((s, kc[0]) in results for kc in kcuts)]
    if not present_summ:
        return

    # Pk-aligned column layout (see noise_calibration_all.py for the same
    # scheme): group columns by Pk cut, one sub-column per Bk variant.
    pk_slots, row_by_pk = {}, {}
    for s in present_summ:
        by_pk = {}
        for kc in kcuts_by_summary[s]:
            if (s, kc[0]) not in results:
                continue
            by_pk.setdefault(pk_kmax(kc[2]), []).append(kc)
        row_by_pk[s] = by_pk
        for pk, lst in by_pk.items():
            pk_slots[pk] = max(pk_slots.get(pk, 0), len(lst))

    col_base, c = {}, 0
    for pk in sorted(pk_slots):
        col_base[pk] = c
        c += pk_slots[pk]
    n_k = c

    col_of = {}  # summary -> {col index: (kcut, kmin, kmax)}
    for s in present_summ:
        m = {}
        for pk, lst in row_by_pk[s].items():
            for i, kc in enumerate(lst):
                m[col_base[pk] + i] = kc
        col_of[s] = m

    n_s = len(present_summ)
    fig, axs = plt.subplots(n_s, n_k,
                             figsize=(max(2.0, len(tran_vals) * 0.45 + 0.5) * n_k,
                                      max(1.7, len(rad_vals)  * 0.45 + 0.7) * n_s),
                             squeeze=False)

    vmax = 4.0
    for i, s in enumerate(present_summ):
        colmap = col_of[s]
        first_col = min(colmap) if colmap else 0
        short = s.replace('zPk0+zPk2+zPk4', 'zPk024')
        for j in range(n_k):
            ax = axs[i, j]
            if j not in colmap:
                ax.axis('off')
                continue
            kcut, kmin, kmax = colmap[j]
            grid, _, _ = _noise_pivot(noises, results[(s, kcut)])
            _draw_z_heatmap(ax, grid, rad_vals, tran_vals, vmax=vmax)
            ax.set_title(kcut_label(kmin, kmax, multiline=False), fontsize=8)
            if j == first_col:
                ax.set_ylabel(short, fontsize=8)
            ax.set_xticks([])
            ax.set_yticks([])

    fig.suptitle(
        r'Mahalanobis $\bar{z}$ (LCDM $M_\nu=0$)  |  black contour = $\bar{z}=2$'
        '\n' + _Z_EQUATION,
        fontsize=12, y=1.03)
    sm = plt.cm.ScalarMappable(
        cmap='RdYlGn_r', norm=plt.Normalize(0, vmax))
    sm.set_array([])
    cbar = fig.colorbar(sm, ax=axs, location='right', shrink=0.8, pad=0.02)
    cbar.set_label(r'$\bar{z}$')

    fname = join(figroot, 'lcdm_z_global.png')
    fig.savefig(fname, dpi=100, bbox_inches='tight')
    plt.close(fig)
    print(f'Saved global z-heatmap: {fname}')


def run(basedir, testdir, noises_path, cosm_table_path, figroot=None):
    np.random.seed(42)
    if figroot is None:
        figroot = join(os.path.dirname(os.path.abspath(__file__)), 'figures')
    os.makedirs(figroot, exist_ok=True)

    noises  = np.loadtxt(noises_path, delimiter=',')
    n_noise = len(noises)

    z_results = {}          # (summary, kcut) -> z_per_noise array
    kcuts_by_summary = {}   # summary -> ordered list of (kcut, kmin, kmax)

    # Discover which (summary, k-cut) combinations are present on the train side.
    for s in discover_summaries(basedir):
        kcuts = discover_kcuts(join(basedir, s))
        kcuts_by_summary[s] = kcuts
        for kstr, kmin, kmax in kcuts:
            label = f"{s.replace('+', '_')}_{kstr}"
            figdir = join(figroot, label)
            klab = kcut_label(kmin, kmax, multiline=False)
            stitle = f'{s}  ({klab})'

            print(f'\n=== {s}  {kstr} ===')

            try:
                (theta, noiseidx, ids, samples, percs,
                 theta_self, samples_self, percs_self, masks) = load_data(
                    basedir, testdir, s, kstr, cosm_table_path)
            except FileNotFoundError as e:
                print(f'  SKIP (missing file): {e}')
                continue

            # Only create the output directory once data is confirmed to exist
            os.makedirs(figdir, exist_ok=True)

            n_rep = n_noise // 2

            plot_single_noise_scatter(
                theta, percs, theta_self, percs_self, masks,
                noiseidx, noises, n_rep, stitle, figdir)

            plot_residuals(
                theta, percs, theta_self, percs_self, masks,
                noiseidx, noises, n_rep, stitle, figdir)

            for p in PARAM_INDICES:
                plot_all_noise_true_vs_pred(
                    theta, percs, noiseidx, noises, masks, p, stitle, figdir)

            z_scores = _compute_lcdm_z(
                theta, percs, samples, noiseidx, n_noise, masks)
            z_results[(s, kstr)] = z_scores
            plot_lcdm_z_heatmap(z_scores, noises, stitle, kstr, figdir)

    plot_global_z_heatmap(z_results, kcuts_by_summary, noises, figroot)


if __name__ == '__main__':
    _args = _parse_args()
    run(_args.basedir, _args.testdir, _args.noises_path, _args.cosm_table,
        figroot=_args.outdir)