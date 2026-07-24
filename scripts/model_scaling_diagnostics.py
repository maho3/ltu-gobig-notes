"""
Model scaling diagnostics: kmax and feature-length sweeps.

Replicates the 'Compare models' section of matts_tests/test_toy_noised.ipynb.
Generates two sets of plots:
  1. kmax scaling   — fixed summary, increasing kmax (its k-cuts, ordered by
     granularity)
  2. feature scaling — fixed reference kmax, increasing feature length (more
     summary types)

k-cuts are discovered from the model tree and support dynamic per-observable
cuts (e.g. kmin-0.0_kmax-zBk=0.2__zPk=0.4) as well as legacy scalar cuts. Since
every summary here contains the power spectrum, the power-spectrum kmax is used
as the common numeric axis for the kmax sweep, and to hold a reference cut fixed
while varying summary complexity.

Edit the CONFIG block below, then run:

    python scripts/model_scaling_diagnostics.py

Figures are saved to scripts/figures/model_scaling/.
"""

import argparse
import matplotlib
import matplotlib.pyplot as plt
import numpy as np
import os
import sys
import optuna
from os.path import join, exists, dirname, abspath

sys.path.insert(0, dirname(abspath(__file__)))
from kcut_utils import (  # noqa: E402
    discover_kcuts, select_kcut, pk_kmax, kcut_label, simple)

# ── Configuration (defaults; overridden by CLI args) ──────────────────────────

_DEFAULT_WDIR = '/work/hdd/bdne/maho3/cmass-ili'
_DEFAULT_NBODY = 'quijotelike'
_DEFAULT_SIM = 'fastpm_charm6'
_DEFAULT_TRACER = 'galaxy'
Z = 'z'


def _parse_args():
    p = argparse.ArgumentParser()
    p.add_argument('--wdir',   default=_DEFAULT_WDIR)
    p.add_argument('--nbody',  default=_DEFAULT_NBODY)
    p.add_argument('--sim',    default=_DEFAULT_SIM)
    p.add_argument('--tracer', default=_DEFAULT_TRACER)
    p.add_argument('--outdir', default=None,
                   help='Root output dir; figures saved to <outdir>/kmax_sweep/ and <outdir>/feature_sweep/')
    p.add_argument('--sim2', default=None,
                   help='If set, run multi-sim comparison mode: --sim vs --sim2 '
                        '(same nbody/tracer), overlaying kmax/feature scaling. '
                        'Also runs the normal single-sim diagnostics for each.')
    p.add_argument('--label1', default=None,
                   help='Legend label for --sim (multisim mode). Defaults to --sim value.')
    p.add_argument('--label2', default=None,
                   help='Legend label for --sim2 (multisim mode). Defaults to --sim2 value.')
    return p.parse_args()


# kmax sweep: fix one summary, sweep its k-cuts (discovered from disk)
KMAX_SUMMARY = f'{Z}Pk0+{Z}Pk2+{Z}Pk4'

# feature sweep: fix a reference power-spectrum kmax, vary summary complexity.
# For each summary the k-cut whose Pk kmax is closest to FEAT_KMAX is used.
FEAT_KMAX = 0.4
FEAT_SUMMARIES = [
    f'{Z}Pk0',
    f'{Z}Pk0+{Z}Pk2+{Z}Pk4',
    f'{Z}Pk0+{Z}Pk2+{Z}Pk4+{Z}EqBk0',
    f'{Z}Pk0+{Z}Pk2+{Z}Pk4+{Z}SqBk0',
    f'{Z}Pk0+{Z}Pk2+{Z}Pk4+{Z}Bk0',
]

# Fiducial cosmology for filtering test points
THETAFID = np.array([0.3, 0.5, 0.7, 1.0, 0.8])
NBAR_LO = np.log10(1.0e-4)
NBAR_HI = np.log10(5.0e-4)
NBAR_RTOL = 0.1  # relative tolerance on theta for fiducial match

PARAM_NAMES = [r'\Omega_m', r'\Omega_b', r'h', r'n_s', r'\sigma_8']
PARAM_IDXS = [0, 4]

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


# ── Data helpers ───────────────────────────────────────────────────────────────

def summary_dir(nbody, sim, tracer, summary, wdir=_DEFAULT_WDIR):
    """Directory holding all k-cuts for one summary."""
    return join(wdir, nbody, sim, 'models', tracer, summary)


def load_samples(mdir):
    """Return (samples, theta, nbar) or raise FileNotFoundError."""
    samples = np.load(join(mdir, 'posterior_samples.npy'))
    theta = np.load(join(mdir, 'theta_test.npy'))
    nbar_path = join(mdir, 'nbar_test.npy')
    if exists(nbar_path):
        nbar = np.load(nbar_path)
    else:
        x = np.load(join(mdir, 'x_test.npy'))
        nbar = x[:, -1]
    if nbar.ndim > 1:
        nbar = nbar.mean(axis=1)
    return samples, theta, nbar


def feature_length(mdir):
    x = np.load(join(mdir, 'x_test.npy'))
    return x.shape[-1]


def fiducial_stdev(mdir):
    """Median posterior stdev near fiducial cosmology; returns (stdev array, count) or None."""
    if not exists(join(mdir, 'posterior_samples.npy')):
        return None
    try:
        samples, theta, nbar = load_samples(mdir)
    except (OSError, ValueError):
        return None
    mask = np.all(np.isclose(theta[:, PARAM_IDXS],
                             THETAFID[PARAM_IDXS], rtol=NBAR_RTOL), axis=1)
    mask &= (nbar > NBAR_LO) & (nbar < NBAR_HI)
    if not mask.any():
        return None
    return np.std(samples[:, mask], axis=0)


# ── Plot functions ─────────────────────────────────────────────────────────────

def plot_optuna_history(modeldirs, labels, title, figdir, fname='optuna_history.jpg'):
    """Best validation log-prob vs Optuna trial number for each model."""
    f, ax = plt.subplots(figsize=(8, 4))
    for i, (mdir, lab) in enumerate(zip(modeldirs, labels)):
        db = join(mdir, 'optuna_study.db')
        if not exists(db):
            print(f'  SKIP optuna (no db): {mdir}')
            continue
        study_name = mdir.rstrip('/').split('/')[-2]
        try:
            study = optuna.load_study(study_name=study_name,
                                      storage=f'sqlite:///{db}')
        except Exception as e:
            print(f'  SKIP optuna ({e}): {mdir}')
            continue
        trials = [t for t in study.trials if t.value is not None]
        if not trials:
            continue
        nums = [t.number for t in trials]
        vals = [t.value for t in trials]
        best = np.maximum.accumulate(vals)
        ax.plot(nums, best, label=lab, color=f'C{i}')

    ax.set(xlabel='Optuna trial number', ylabel='Best validation_log_prob')
    ax.legend(fontsize=9, ncol=2)
    ax.grid(True)
    ax.set_title(title)
    plt.tight_layout()
    fpath = join(figdir, fname)
    f.savefig(fpath, dpi=100, bbox_inches='tight')
    plt.close(f)
    print(f'  Saved {fpath}')


def plot_stdev_vs_theta(modeldirs, labels, title, figdir, fname='stdev_vs_theta.jpg'):
    """Median posterior stdev in bins of true parameter value."""
    Nbins = 4
    f, axs = plt.subplots(1, 2, figsize=(10, 5))
    for i, (mdir, lab) in enumerate(zip(modeldirs, labels)):
        if not exists(join(mdir, 'posterior_samples.npy')):
            continue
        try:
            samples, theta, _ = load_samples(mdir)
        except (OSError, ValueError):
            continue
        stdev = samples.std(axis=0)
        off = (i - (len(modeldirs) - 1) / 2) * 0.02
        fmt = ['o', 's', '*', 'D', '^'][i % 5]
        for j, p in enumerate(PARAM_IDXS):
            ax = axs[j]
            lo, hi = theta[:, p].min(), theta[:, p].max()
            edges = np.linspace(lo, hi, Nbins + 1)
            centers = 0.5 * (edges[:-1] + edges[1:])
            ys = []
            for k in range(Nbins):
                mask = (theta[:, p] >= edges[k]) & (theta[:, p] < edges[k + 1])
                ys.append(np.percentile(stdev[mask, p], [50, 16, 84]))
            ys = np.array(ys)
            ax.errorbar(centers + off * (hi - lo), ys[:, 0],
                        yerr=[ys[:, 0] - ys[:, 1], ys[:, 2] - ys[:, 0]],
                        fmt=fmt, color=f'C{i}', label=lab, capsize=3)
            ax.set(xlabel=f'True ${PARAM_NAMES[p]}$',
                   ylabel=fr'$\Delta {PARAM_NAMES[p]}$')
            ax.set_ylim(0)
            ax.grid(True)

    axs[1].legend(fontsize=8, ncol=2, loc='upper right')
    f.suptitle(title)
    plt.tight_layout()
    fpath = join(figdir, fname)
    f.savefig(fpath, dpi=100, bbox_inches='tight')
    plt.close(f)
    print(f'  Saved {fpath}')


def plot_aggregate_calibration(modeldirs, labels, title, figdir,
                               fname='calibration.jpg'):
    """Fraction of test points below median and within 16–84th percentile."""
    import matplotlib.lines as mlines
    color_med = 'tab:blue'
    color_68 = 'tab:orange'

    f, axs = plt.subplots(1, 2, figsize=(8, 4))
    for i, (mdir, _) in enumerate(zip(modeldirs, labels)):
        if not exists(join(mdir, 'posterior_samples.npy')):
            continue
        try:
            samples, theta, _ = load_samples(mdir)
        except (OSError, ValueError):
            continue
        p16, p50, p84 = np.percentile(samples, [16, 50, 84], axis=0)
        N = len(theta)
        Nhods = 5
        err_med = np.sqrt(0.25 * Nhods / N)
        err_68 = np.sqrt(0.68 * 0.32 * Nhods / N)
        for j, p in enumerate(PARAM_IDXS):
            ax = axs[j]
            y_med = np.mean(theta[:, p] < p50[:, p])
            y_68 = np.mean((theta[:, p] >= p16[:, p]) &
                           (theta[:, p] <= p84[:, p]))
            ax.errorbar(i, y_med, yerr=err_med,
                        marker='o', color=color_med, linestyle='none')
            ax.errorbar(i, y_68, yerr=err_68,
                        marker='^', color=color_68, linestyle='none')
            ax.set_title(f'${PARAM_NAMES[p]}$')
            ax.set_ylabel('True fraction in range')
            if i == 0:
                ax.axhline(0.50, color=color_med, ls=':', alpha=0.6)
                ax.axhline(0.68, color=color_68, ls=':', alpha=0.6)

    handles = [
        mlines.Line2D([], [], color=color_med, marker='o',
                      linestyle='none', label='Median (50%)'),
        mlines.Line2D([], [], color=color_68, marker='^',
                      linestyle='none', label='16–84th (68%)'),
    ]
    axs[0].legend(handles=handles, fontsize=9)
    for ax in axs:
        ax.set_xticks(range(len(labels)))
        ax.set_xticklabels(simple(labels), rotation=45, ha='right')
        ax.grid(True, axis='y')

    f.suptitle(title)
    plt.tight_layout()
    fpath = join(figdir, fname)
    f.savefig(fpath, dpi=100, bbox_inches='tight')
    plt.close(f)
    print(f'  Saved {fpath}')


def plot_fiducial_stdev_bar(modeldirs, labels, title, figdir,
                            fname='fiducial_stdev.jpg'):
    """Median ± 16/84th stdev at fiducial cosmology, categorical x-axis."""
    f, axs = plt.subplots(1, 2, figsize=(8, 4), sharex=True)
    valid_labels = []
    x_idx = 0
    for i, (mdir, lab) in enumerate(zip(modeldirs, labels)):
        stdev = fiducial_stdev(mdir)
        if stdev is None:
            print(f'  SKIP fiducial_stdev (no data): {mdir}')
            continue
        fmt = ['o', 's', '*', 'D', '^'][i % 5]
        for j, p in enumerate(PARAM_IDXS):
            ax = axs[j]
            perc = np.percentile(stdev[:, p], [50, 16, 84])
            ax.errorbar(x_idx, perc[0],
                        yerr=[[perc[0] - perc[1]], [perc[2] - perc[0]]],
                        fmt=fmt, color=f'C{i}', capsize=4)
            ax.set_ylabel(fr'$\Delta {PARAM_NAMES[p]}$')
            ax.set_ylim(0)
            ax.grid(True, axis='y')
        valid_labels.append(lab)
        x_idx += 1

    for ax in axs:
        ax.set_xticks(range(len(valid_labels)))
        ax.set_xticklabels(simple(valid_labels), rotation=45, ha='right')

    f.suptitle(title)
    plt.tight_layout()
    fpath = join(figdir, fname)
    f.savefig(fpath, dpi=100, bbox_inches='tight')
    plt.close(f)
    print(f'  Saved {fpath}')


def _kcut_stdev_points(sdir):
    """For every k-cut under a summary dir, return sorted lists of
    (pk_kmax, [percentiles per PARAM_IDX]) using the fiducial stdev."""
    pts = []
    for dirname, kmin, kmax in discover_kcuts(sdir):
        stdev = fiducial_stdev(join(sdir, dirname))
        if stdev is None:
            print(f'  SKIP (no data): {join(sdir, dirname)}')
            continue
        percs = [np.percentile(stdev[:, p], [50, 16, 84]) for p in PARAM_IDXS]
        pts.append((pk_kmax(kmax), percs))
    pts.sort(key=lambda t: t[0])
    return pts


def plot_kmax_scaling(summaries, nbody, sim, tracer,
                      title, figdir, wdir=_DEFAULT_WDIR, fname='kmax_scaling.jpg'):
    """Fiducial stdev vs power-spectrum kmax for each summary (line plot).

    x is the Pk-family kmax of each discovered k-cut, so both scalar and dynamic
    cuts land on a common numeric axis of increasing granularity."""
    markers = ['o', 's', '*', 'D', '^', 'v']

    f, axs = plt.subplots(1, 2, figsize=(10, 5), sharex=True)
    for g, s in enumerate(summaries):
        pts = _kcut_stdev_points(summary_dir(nbody, sim, tracer, s, wdir))
        if not pts:
            continue
        off = (g - (len(summaries) - 1) / 2) * 0.005
        xs = [p[0] + off for p in pts]
        for j, p in enumerate(PARAM_IDXS):
            perc = np.array([pt[1][j] for pt in pts])
            axs[j].errorbar(
                xs, perc[:, 0],
                yerr=[perc[:, 0] - perc[:, 1], perc[:, 2] - perc[:, 0]],
                label=simple(s), color=f'C{g}',
                marker=markers[g % len(markers)], linestyle='-', capsize=3)
            axs[j].set(xlabel=r'$k_{\max}^{P}\ [h/\mathrm{Mpc}]$',
                       ylabel=fr'$\Delta {PARAM_NAMES[p]}$',
                       ylim=(0, None))
            axs[j].grid(True)

    axs[1].legend(fontsize=9, loc='upper right', ncol=1)
    f.suptitle(title)
    plt.tight_layout()
    fpath = join(figdir, fname)
    f.savefig(fpath, dpi=100, bbox_inches='tight')
    plt.close(f)
    print(f'  Saved {fpath}')


def plot_feature_length_scaling(summaries, ref_kmax, nbody, sim, tracer,
                                title, figdir, wdir=_DEFAULT_WDIR,
                                fname='feature_length_scaling.jpg'):
    """Fiducial stdev vs feature vector length (x_len) at a reference kmax.

    For each summary, the k-cut whose Pk kmax is closest to ref_kmax is used."""
    f, axs = plt.subplots(1, 2, figsize=(10, 5))
    xlens, stdevs, labels_valid = [], [], []
    for i, s in enumerate(summaries):
        sdir = summary_dir(nbody, sim, tracer, s, wdir)
        sel = select_kcut(sdir, ref_kmax)
        if sel is None:
            print(f'  SKIP feature_scaling (no k-cut): {sdir}')
            continue
        mdir = join(sdir, sel[0])
        if not exists(join(mdir, 'x_test.npy')):
            print(f'  SKIP feature_scaling (no x_test): {mdir}')
            continue
        stdev = fiducial_stdev(mdir)
        if stdev is None:
            print(f'  SKIP feature_scaling (no stdev): {mdir}')
            continue
        xlens.append(feature_length(mdir))
        stdevs.append(stdev)
        labels_valid.append(s)

    for j, p in enumerate(PARAM_IDXS):
        ax = axs[j]
        for i, (xl, stdev, lab) in enumerate(zip(xlens, stdevs, labels_valid)):
            perc = np.percentile(stdev[:, p], [50, 16, 84])
            ax.errorbar(xl, perc[0],
                        yerr=[[perc[0] - perc[1]], [perc[2] - perc[0]]],
                        fmt='o', color=f'C{i}', label=simple(lab), capsize=4)
        ax.set(xlabel='Feature vector length',
               ylabel=fr'$\Delta {PARAM_NAMES[p]}$',
               ylim=(0, None))
        ax.grid(True)

    axs[1].legend(fontsize=9, loc='upper right')
    f.suptitle(title)
    plt.tight_layout()
    fpath = join(figdir, fname)
    f.savefig(fpath, dpi=100, bbox_inches='tight')
    plt.close(f)
    print(f'  Saved {fpath}')


def plot_kmax_scaling_multisim(summaries, sim_configs, tracer,
                               title, figdir, fname='kmax_scaling_multisim.jpg'):
    """Fiducial stdev vs Pk kmax, overlaying multiple sims. Color = summary,
    linestyle = sim."""
    markers = ['o', 's', '*', 'D', '^', 'v']
    linestyles = ['-', '--', ':', '-.']

    f, axs = plt.subplots(1, 2, figsize=(10, 5), sharex=True)
    for g, s in enumerate(summaries):
        for si, cfg in enumerate(sim_configs):
            pts = _kcut_stdev_points(
                summary_dir(cfg['nbody'], cfg['sim'], tracer, s, cfg['wdir']))
            if not pts:
                continue
            off = (g - (len(summaries) - 1) / 2) * 0.005
            xs = [p[0] + off for p in pts]
            for j, p in enumerate(PARAM_IDXS):
                perc = np.array([pt[1][j] for pt in pts])
                axs[j].errorbar(
                    xs, perc[:, 0],
                    yerr=[perc[:, 0] - perc[:, 1], perc[:, 2] - perc[:, 0]],
                    label=f"{simple(s)} ({cfg['label']})", color=f'C{g}',
                    marker=markers[g % len(markers)],
                    linestyle=linestyles[si % len(linestyles)], capsize=3)
                axs[j].set(xlabel=r'$k_{\max}^{P}\ [h/\mathrm{Mpc}]$',
                           ylabel=fr'$\Delta {PARAM_NAMES[p]}$',
                           ylim=(0, None))
                axs[j].grid(True)

    axs[1].legend(fontsize=8, loc='upper right', ncol=1)
    f.suptitle(title)
    plt.tight_layout()
    fpath = join(figdir, fname)
    f.savefig(fpath, dpi=100, bbox_inches='tight')
    plt.close(f)
    print(f'  Saved {fpath}')


def plot_feature_length_scaling_multisim(summaries, ref_kmax, sim_configs, tracer,
                                          title, figdir,
                                          fname='feature_length_scaling_multisim.jpg'):
    """Fiducial stdev vs feature vector length, overlaying multiple sims at a
    reference kmax."""
    markers = ['o', 's', '*', 'D', '^', 'v']

    f, axs = plt.subplots(1, 2, figsize=(10, 5))

    # First pass: gather data for all sims so offsets can be computed consistently.
    per_sim = []
    all_xlens = []
    for cfg in sim_configs:
        xlens, stdevs, labels_valid = [], [], []
        for s in summaries:
            sdir = summary_dir(cfg['nbody'], cfg['sim'], tracer, s, cfg['wdir'])
            sel = select_kcut(sdir, ref_kmax)
            if sel is None:
                print(f'  SKIP feature_scaling_multisim (no k-cut): {sdir}')
                continue
            mdir = join(sdir, sel[0])
            if not exists(join(mdir, 'x_test.npy')):
                print(f'  SKIP feature_scaling_multisim (no x_test): {mdir}')
                continue
            stdev = fiducial_stdev(mdir)
            if stdev is None:
                print(f'  SKIP feature_scaling_multisim (no stdev): {mdir}')
                continue
            xlens.append(feature_length(mdir))
            stdevs.append(stdev)
            labels_valid.append(s)
        per_sim.append((xlens, stdevs, labels_valid))
        all_xlens.extend(xlens)

    xspan = (max(all_xlens) - min(all_xlens)) if len(set(all_xlens)) > 1 else 1

    for si, (cfg, (xlens, stdevs, labels_valid)) in enumerate(zip(sim_configs, per_sim)):
        off = (si - (len(sim_configs) - 1) / 2) * 0.08 * xspan
        for j, p in enumerate(PARAM_IDXS):
            ax = axs[j]
            for i, (xl, stdev, lab) in enumerate(zip(xlens, stdevs, labels_valid)):
                perc = np.percentile(stdev[:, p], [50, 16, 84])
                ax.errorbar(xl + off, perc[0],
                            yerr=[[perc[0] - perc[1]], [perc[2] - perc[0]]],
                            fmt=markers[i % len(markers)], color=f'C{i}',
                            markerfacecolor=('none' if si else f'C{i}'),
                            label=f"{simple(lab)} ({cfg['label']})", capsize=4)
            ax.set(xlabel='Feature vector length',
                   ylabel=fr'$\Delta {PARAM_NAMES[p]}$',
                   ylim=(0, None))
            ax.grid(True)

    axs[1].legend(fontsize=7, loc='upper right', ncol=1)
    f.suptitle(title)
    plt.tight_layout()
    fpath = join(figdir, fname)
    f.savefig(fpath, dpi=100, bbox_inches='tight')
    plt.close(f)
    print(f'  Saved {fpath}')


# ── Multi-sim comparison ────────────────────────────────────────────────────────

def run_multisim(sim_configs, tracer,
                 kmax_summary, feat_kmax, feat_summaries,
                 figroot=None, run_individual=True):
    """Compare constraining power across multiple (nbody, sim) model dirs
    (e.g. same sim with/without HOD posterior inference) as a function of
    summary and kmax.

    sim_configs: list of dicts with keys 'wdir', 'nbody', 'sim', 'label'.
    """
    if figroot is None:
        figroot = join(os.path.dirname(os.path.abspath(__file__)),
                       'figures', 'model_scaling')
    os.makedirs(figroot, exist_ok=True)

    if run_individual:
        for cfg in sim_configs:
            print(f"\n### Individual diagnostics: {cfg['label']} "
                  f"({cfg['nbody']}/{cfg['sim']}) ###")
            run(wdir=cfg['wdir'], nbody=cfg['nbody'], sim=cfg['sim'],
                tracer=tracer, kmax_summary=kmax_summary,
                feat_kmax=feat_kmax, feat_summaries=feat_summaries,
                figroot=join(figroot, cfg['label']))

    print('\n=== multi-sim comparison ===')
    comp_dir = join(figroot, 'comparison')
    os.makedirs(comp_dir, exist_ok=True)

    labels_str = ' vs '.join(cfg['label'] for cfg in sim_configs)
    kmax_title = f'{labels_str}\n{simple(kmax_summary)}: varying kmax'
    plot_kmax_scaling_multisim(feat_summaries, sim_configs, tracer,
                               kmax_title, comp_dir)

    feat_title = f'{labels_str}\nkmax~{feat_kmax}: varying summary'
    plot_feature_length_scaling_multisim(feat_summaries, feat_kmax, sim_configs,
                                         tracer, feat_title, comp_dir)


# ── Main ───────────────────────────────────────────────────────────────────────

def run(wdir, nbody, sim, tracer,
        kmax_summary, feat_kmax, feat_summaries,
        figroot=None):
    np.random.seed(42)
    if figroot is None:
        figroot = join(os.path.dirname(os.path.abspath(__file__)),
                       'figures', 'model_scaling')
    os.makedirs(figroot, exist_ok=True)

    base_title = f'{nbody} / {sim} / {tracer}'

    # ── 1. kmax sweep ──────────────────────────────────────────────────────────
    print('\n=== kmax sweep ===')
    kmax_dir = join(figroot, 'kmax_sweep')
    os.makedirs(kmax_dir, exist_ok=True)

    sdir = summary_dir(nbody, sim, tracer, kmax_summary, wdir)
    kcuts = discover_kcuts(sdir)  # ordered by increasing granularity
    kmax_mdirs = [join(sdir, d) for d, _, _ in kcuts]
    kmax_labels = [kcut_label(kmin, kmax, multiline=False)
                   for _, kmin, kmax in kcuts]
    kmax_title = f'{base_title}\n{simple(kmax_summary)}: varying kmax'

    if kmax_mdirs:
        plot_optuna_history(kmax_mdirs, kmax_labels, kmax_title, kmax_dir)
        plot_stdev_vs_theta(kmax_mdirs, kmax_labels, kmax_title, kmax_dir)
        plot_aggregate_calibration(kmax_mdirs, kmax_labels, kmax_title, kmax_dir)
        plot_fiducial_stdev_bar(kmax_mdirs, kmax_labels, kmax_title, kmax_dir)
    else:
        print(f'  No k-cuts found for {kmax_summary} under {sdir}')

    # Line-plot version of kmax scaling across all feat_summaries
    plot_kmax_scaling(feat_summaries, nbody, sim, tracer,
                      f'{base_title}\nkmax scaling', kmax_dir, wdir)

    # ── 2. Feature-length sweep ────────────────────────────────────────────────
    print('\n=== feature-length sweep ===')
    feat_dir = join(figroot, 'feature_sweep')
    os.makedirs(feat_dir, exist_ok=True)

    feat_mdirs, feat_labels = [], []
    for s in feat_summaries:
        sel = select_kcut(summary_dir(nbody, sim, tracer, s, wdir), feat_kmax)
        if sel is None:
            print(f'  SKIP feature sweep (no k-cut): {s}')
            continue
        feat_mdirs.append(join(summary_dir(nbody, sim, tracer, s, wdir), sel[0]))
        feat_labels.append(s)
    feat_title = f'{base_title}\nkmax~{feat_kmax}: varying summary'

    if feat_mdirs:
        plot_optuna_history(feat_mdirs, feat_labels, feat_title, feat_dir)
        plot_stdev_vs_theta(feat_mdirs, feat_labels, feat_title, feat_dir)
        plot_aggregate_calibration(feat_mdirs, feat_labels, feat_title, feat_dir)
        plot_fiducial_stdev_bar(feat_mdirs, feat_labels, feat_title, feat_dir)
    plot_feature_length_scaling(feat_summaries, feat_kmax, nbody, sim, tracer,
                                feat_title, feat_dir, wdir)


if __name__ == '__main__':
    _args = _parse_args()
    if _args.sim2 is not None:
        _sim_configs = [
            {'wdir': _args.wdir, 'nbody': _args.nbody, 'sim': _args.sim,
             'label': _args.label1 or _args.sim},
            {'wdir': _args.wdir, 'nbody': _args.nbody, 'sim': _args.sim2,
             'label': _args.label2 or _args.sim2},
        ]
        run_multisim(
            sim_configs=_sim_configs,
            tracer=_args.tracer,
            kmax_summary=KMAX_SUMMARY,
            feat_kmax=FEAT_KMAX,
            feat_summaries=FEAT_SUMMARIES,
            figroot=_args.outdir,
        )
    else:
        run(
            wdir=_args.wdir,
            nbody=_args.nbody,
            sim=_args.sim,
            tracer=_args.tracer,
            kmax_summary=KMAX_SUMMARY,
            feat_kmax=FEAT_KMAX,
            feat_summaries=FEAT_SUMMARIES,
            figroot=_args.outdir,
        )
