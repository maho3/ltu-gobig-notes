"""
Shared machinery for single-cosmology OOD corner-plot experiments.

Unlike the noise-grid OOD scripts, the quijote3gpch and mtng test suites each
contain a single 'true' cosmology, so coverage and heatmap statistics over a
population of cosmologies are not available. What is available is the posterior
itself, at each noise configuration, against a known truth. So the output
products are corner plots:

  - ``corner_full_n<N>.jpg``   all inferred parameters (cosmology + HOD + noise)
  - ``corner_cosmo_n<N>.jpg``  the 5 cosmological parameters
  - ``corner_Om_s8_n<N>.jpg``  Omega_m and sigma_8 only

Noise configurations are selected per cell: a few at random, plus the one that
minimises the mean joint Mahalanobis z-score on (Omega_m, sigma_8). The
z-minimising config is always included and is labelled as such.

Where a noise configuration holds several test points (e.g. several HOD
realisations of the same cosmology), the cosmology-only and Omega_m-sigma_8
corners overlay every point, since they share a truth. The full corner shows
only the lowest-z point of the group, because each point has its own HOD truth
and overlaying them would put several different truth lines on one panel.

No self-consistent reference is drawn; the truth line is the only reference.
"""

import csv
import os
import sys
import numpy as np
import matplotlib
import matplotlib.pyplot as plt
import matplotlib.lines as mlines
import corner
from os.path import join, exists, dirname, abspath

sys.path.insert(0, dirname(abspath(__file__)))
from kcut_utils import (  # noqa: E402
    discover_summaries, discover_kcuts, granularity, kcut_label, simple)

matplotlib.use('Agg')
matplotlib.rcParams.update({
    'font.size': 12,
    'axes.titlesize': 12,
    'axes.labelsize': 12,
    'xtick.labelsize': 9,
    'ytick.labelsize': 9,
    'legend.fontsize': 10,
})

COSMO_LABELS = [r'$\Omega_m$', r'$\Omega_b$', r'$h$', r'$n_s$', r'$\sigma_8$']
NOISE_LABELS = [r'$\sigma_{\rm rad}$', r'$\sigma_{\rm tran}$']
PARAM_IDXS = [0, 4]          # Omega_m, sigma_8
COSMO_IDXS = [0, 1, 2, 3, 4]

# Contour colours for overlaid posteriors within one panel.
_OVERLAY_COLORS = ['#1f77b4', '#ff7f0e', '#2ca02c', '#d62728',
                   '#9467bd', '#8c564b', '#e377c2']
_TRUTH_COLOR = '#000000'


# ── labels ────────────────────────────────────────────────────────────────────

def _shorten_hod(name):
    """Compact a hodprior.csv parameter name for a corner-plot axis label."""
    name = name.replace('mean_occupation_', '')
    name = name.replace('_assembias_param1', '_ab')
    name = name.replace('conc_gal_bias_satellites', 'c_sat')
    name = name.replace('centrals', 'cen').replace('satellites', 'sat')
    name = name.replace('sigma_logM', r'$\sigma_{\log M}$')
    name = name.replace('alpha', r'$\alpha$')
    return name


def param_labels(model_dir, n_params):
    """Build axis labels for a theta vector: cosmology, HOD, then noise.

    HOD names come from the cell's hodprior.csv, so this adapts to tracers with
    different HOD parameterisations (10 for the cubic-box galaxy tracer, 16 for
    the redshift-binned lightcone tracer).
    """
    hod = []
    hp = join(model_dir, 'hodprior.csv')
    if exists(hp):
        with open(hp) as fh:
            hod = [_shorten_hod(row[0]) for row in csv.reader(fh) if row]
    labels = COSMO_LABELS + hod + NOISE_LABELS
    if len(labels) != n_params:
        # Fall back to generic names rather than mislabelling axes.
        print(f'  WARNING: built {len(labels)} labels for {n_params} params in '
              f'{model_dir}; falling back to generic HOD names')
        n_hod = n_params - len(COSMO_LABELS) - len(NOISE_LABELS)
        labels = (COSMO_LABELS + [f'hod{i}' for i in range(max(0, n_hod))]
                  + NOISE_LABELS)
        labels = labels[:n_params]
    return labels


# ── data ──────────────────────────────────────────────────────────────────────

def load_cell(basedir, testdir, summary, kcut, test_tag):
    """Load (theta, noiseidx, samples) for one (summary, k-cut) cell.

    ``samples`` has shape (n_draws, n_test, n_params); theta and noiseidx are
    aligned along n_test.
    """
    tdir = join(testdir, summary, kcut)
    theta = np.load(join(tdir, 'theta_test.npy'))

    nid_path = join(tdir, 'noiseid_test.npy')
    if not exists(nid_path):
        nid_path = join(tdir, 'noiseids_test.npy')
    noiseidx = np.load(nid_path)
    noiseidx = noiseidx[:, 0] if noiseidx.ndim > 1 else noiseidx

    samples = np.load(
        join(basedir, summary, kcut, 'testing', test_tag,
             'posterior_samples.npy'))

    if samples.shape[1] != theta.shape[0]:
        raise ValueError(
            f'sample/theta mismatch in {summary}/{kcut}: '
            f'samples={samples.shape}, theta={theta.shape}')
    if noiseidx.shape[0] != theta.shape[0]:
        raise ValueError(
            f'noiseid/theta mismatch in {summary}/{kcut}: '
            f'noiseidx={noiseidx.shape}, theta={theta.shape}')
    return theta, noiseidx, samples


def joint_z(theta, samples, point, idxs=PARAM_IDXS):
    """Joint Mahalanobis distance on ``idxs`` for one test point.

    z = sqrt(d^T C^-1 d), d = theta_true - posterior median, C the posterior
    covariance of those parameters (full, including their correlation).
    """
    draws = samples[:, point][:, idxs]
    med = np.median(draws, axis=0)
    d = theta[point, idxs] - med
    cov = np.cov(draws, rowvar=False)
    try:
        cinv = np.linalg.inv(cov)
    except np.linalg.LinAlgError:
        cinv = np.linalg.pinv(cov)
    return float(np.sqrt(d @ cinv @ d))


def z_by_noise(theta, noiseidx, samples):
    """Mean joint z per noise id -> {noise_id: (mean_z, [point indices])}."""
    out = {}
    for nid in sorted(set(noiseidx.tolist())):
        pts = np.where(noiseidx == nid)[0]
        zs = [joint_z(theta, samples, p) for p in pts]
        out[int(nid)] = (float(np.mean(zs)), pts, zs)
    return out


def select_noise(zmap, n_random, seed=42):
    """Pick the z-minimising noise id plus ``n_random`` others.

    Returns an ordered list of (noise_id, is_best). The best config always comes
    first so it is easy to find among the outputs.
    """
    ids = sorted(zmap)
    best = min(ids, key=lambda n: zmap[n][0])
    rest = [n for n in ids if n != best]
    rng = np.random.default_rng(seed)
    if len(rest) > n_random:
        rest = sorted(rng.choice(rest, n_random, replace=False).tolist())
    return [(best, True)] + [(n, False) for n in rest]


# ── plotting ──────────────────────────────────────────────────────────────────

def _ranges(draws_list, truth, pad=0.15):
    """Common axis ranges spanning every overlaid posterior and the truth."""
    allm = np.concatenate(draws_list, axis=0)
    lo = np.minimum(allm.min(axis=0), truth)
    hi = np.maximum(allm.max(axis=0), truth)
    span = np.where(hi - lo > 0, hi - lo, 1.0)
    return list(zip(lo - pad * span, hi + pad * span))


def _corner_overlay(draws_list, labels, truth, titles, out_path, suptitle):
    """Overlay several posteriors on one corner grid with a shared truth."""
    rng = _ranges(draws_list, truth)
    fig = None
    for i, draws in enumerate(draws_list):
        color = _OVERLAY_COLORS[i % len(_OVERLAY_COLORS)]
        fig = corner.corner(
            draws, labels=labels, fig=fig, color=color, range=rng,
            truths=truth if i == 0 else None,
            truth_color=_TRUTH_COLOR,
            plot_datapoints=False, plot_density=False, fill_contours=False,
            levels=(0.68, 0.95), smooth=1.0,
            hist_kwargs={'density': True},
        )
    handles = [mlines.Line2D([], [], color=_OVERLAY_COLORS[i % len(_OVERLAY_COLORS)],
                             label=t) for i, t in enumerate(titles)]
    handles.append(mlines.Line2D([], [], color=_TRUTH_COLOR, ls='-', label='truth'))
    # Anchored outside the axes: a 2x2 Om-s8 grid has no free upper-right
    # panel, so an inside legend lands on top of the title.
    fig.legend(handles=handles, loc='upper left',
               bbox_to_anchor=(1.01, 0.98), frameon=False)
    fig.suptitle(suptitle, fontsize=13, y=1.01)
    fig.savefig(out_path, dpi=100, bbox_inches='tight')
    plt.close(fig)
    print(f'    Saved {out_path}')


def plot_cell_noise(theta, samples, labels, pts, zs, nid, noises,
                    cell_title, figdir):
    """Full / cosmology-only / Omega_m-sigma_8 corners at one noise config."""
    order = np.argsort(zs)
    pts_sorted = [pts[i] for i in order]
    zs_sorted = [zs[i] for i in order]
    ntag = f'n{nid}'
    noise_str = (rf'$\sigma_{{\rm rad}}={noises[nid, 0]:.2f}$, '
                 rf'$\sigma_{{\rm tran}}={noises[nid, 1]:.2f}$')
    base_title = f'{cell_title}\n{noise_str}'

    # Full corner: lowest-z point only, since each point has its own HOD truth.
    p0 = pts_sorted[0]
    _corner_overlay(
        [samples[:, p0]], labels, theta[p0],
        [f'test point {p0} (z={zs_sorted[0]:.2f})'],
        join(figdir, f'corner_full_{ntag}.jpg'),
        base_title + '  |  all parameters')

    # Cosmology-only and Om-s8: overlay every point at this noise config, which
    # share a cosmological truth.
    truth_c = theta[pts_sorted[0], COSMO_IDXS]
    for other in pts_sorted[1:]:
        if not np.allclose(theta[other, COSMO_IDXS], truth_c):
            raise ValueError(
                f'points at noise {nid} disagree on cosmology; cannot share a '
                f'truth line in {cell_title}')

    titles = [f'point {p} (z={z:.2f})' for p, z in zip(pts_sorted, zs_sorted)]
    _corner_overlay(
        [samples[:, p][:, COSMO_IDXS] for p in pts_sorted],
        [labels[i] for i in COSMO_IDXS], truth_c, titles,
        join(figdir, f'corner_cosmo_{ntag}.jpg'),
        base_title + '  |  cosmology')

    _corner_overlay(
        [samples[:, p][:, PARAM_IDXS] for p in pts_sorted],
        [labels[i] for i in PARAM_IDXS], theta[pts_sorted[0], PARAM_IDXS],
        titles, join(figdir, f'corner_Om_s8_{ntag}.jpg'),
        base_title + r'  |  $\Omega_m$-$\sigma_8$')


def plot_global_om_s8(results, noises, figroot):
    """One panel per summary: Omega_m-sigma_8 68% contours, k-cuts overlaid.

    Each cell contributes its z-minimising noise configuration, so the panel
    shows each k-cut at its own best-recovered noise level.
    """
    summaries = sorted({s for s, _ in results}, key=lambda s: (len(s.split('+')), s))
    if not summaries:
        return
    ncol = len(summaries)
    fig, axs = plt.subplots(1, ncol, figsize=(4.2 * ncol, 4.2), squeeze=False)
    for j, s in enumerate(summaries):
        ax = axs[0, j]
        entries = [(k, v) for (ss, k), v in results.items() if ss == s]
        entries.sort(key=lambda t: t[1]['granularity'])
        for i, (k, v) in enumerate(entries):
            color = _OVERLAY_COLORS[i % len(_OVERLAY_COLORS)]
            corner.hist2d(v['draws'][:, 0], v['draws'][:, 1], ax=ax,
                          levels=(0.68,), color=color, smooth=1.0,
                          plot_datapoints=False, plot_density=False,
                          fill_contours=False,
                          contour_kwargs={'linewidths': 1.4})
            ax.plot([], [], color=color,
                    label=f"{v['klabel']} (z={v['z']:.2f}, n{v['nid']})")
        truth = v['truth']
        ax.axvline(truth[0], color=_TRUTH_COLOR, ls='--', lw=1)
        ax.axhline(truth[1], color=_TRUTH_COLOR, ls='--', lw=1)
        ax.plot(truth[0], truth[1], '*', color=_TRUTH_COLOR, ms=12)
        ax.set(xlabel=r'$\Omega_m$', ylabel=r'$\sigma_8$' if j == 0 else None)
        ax.set_title(simple(s), fontsize=11)
        ax.legend(fontsize=7, loc='best')
        ax.grid(True, alpha=0.3)
    fig.suptitle(r'$\Omega_m$-$\sigma_8$ 68% contours at each cell'
                 "'s z-minimising noise configuration", fontsize=13, y=1.04)
    plt.tight_layout()
    fname = join(figroot, 'global_Om_s8.jpg')
    fig.savefig(fname, dpi=100, bbox_inches='tight')
    plt.close(fig)
    print(f'Saved global figure: {fname}')


# ── driver ────────────────────────────────────────────────────────────────────

def run(basedir, testdir, test_tag, noises_path, figroot, n_random=3, seed=42):
    np.random.seed(seed)
    os.makedirs(figroot, exist_ok=True)
    noises = np.loadtxt(noises_path, delimiter=',')

    global_results = {}
    z_rows = []

    for s in discover_summaries(basedir):
        for kcut, kmin, kmax in discover_kcuts(join(basedir, s)):
            print(f'\n=== {s}  {kcut} ===')
            try:
                theta, noiseidx, samples = load_cell(
                    basedir, testdir, s, kcut, test_tag)
            except FileNotFoundError as e:
                print(f'  SKIP (missing file): {e}')
                continue
            except (EOFError, ValueError, OSError) as e:
                print(f'  SKIP (unreadable or inconsistent): {e}')
                continue

            figdir = join(figroot, f"{s.replace('+', '_')}_{kcut}")
            os.makedirs(figdir, exist_ok=True)

            labels = param_labels(join(basedir, s, kcut), theta.shape[1])
            klabel = kcut_label(kmin, kmax, multiline=False)
            cell_title = f'{s}  ({klabel})'

            zmap = z_by_noise(theta, noiseidx, samples)
            selected = select_noise(zmap, n_random, seed=seed)
            print(f'  {len(zmap)} noise configs; plotting '
                  f'{[n for n, _ in selected]} (best={selected[0][0]})')

            for nid, is_best in selected:
                mean_z, pts, zs = zmap[nid]
                tag = ' [z-best]' if is_best else ''
                plot_cell_noise(theta, samples, labels, pts, zs, nid, noises,
                                cell_title + tag, figdir)

            for nid, (mean_z, pts, zs) in sorted(zmap.items()):
                z_rows.append({
                    'summary': s, 'kcut': kcut, 'klabel': klabel,
                    'noise_id': nid,
                    'sigma_rad': noises[nid, 0], 'sigma_tran': noises[nid, 1],
                    'n_points': len(pts), 'mean_z': mean_z,
                    'min_z': min(zs), 'max_z': max(zs),
                })

            best_nid = selected[0][0]
            _, best_pts, best_zs = zmap[best_nid]
            p0 = best_pts[int(np.argmin(best_zs))]
            global_results[(s, kcut)] = {
                'draws': samples[:, p0][:, PARAM_IDXS],
                'truth': theta[p0, PARAM_IDXS],
                'z': min(best_zs), 'nid': best_nid, 'klabel': klabel,
                'granularity': granularity(kmin, kmax),
            }

    plot_global_om_s8(global_results, noises, figroot)

    if z_rows:
        zpath = join(figroot, 'z_summary.csv')
        with open(zpath, 'w', newline='') as fh:
            w = csv.DictWriter(fh, fieldnames=list(z_rows[0]))
            w.writeheader()
            w.writerows(z_rows)
        print(f'Saved z summary: {zpath}')
