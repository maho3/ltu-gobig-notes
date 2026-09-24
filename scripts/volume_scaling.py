"""
Volume scaling: self-consistent constraining power (fiducial stdev on Om, s8)
vs simulation box volume, compared across suites that differ only in box size
(same pipeline, same tracer).

Tests whether posterior stdev shrinks as ~ V^-1/2, the scaling expected from
a volume-limited Gaussian-information argument. For each summary in SUMMARIES,
k-cuts present in every suite are matched by directory name (suites share the
same pipeline, so the k-cut grid is identical) and plotted as one row per
k-cut, columns [Om, s8], stdev vs volume on log-log axes, with a V^-1/2
reference line anchored to the first suite's point and the empirical log-log
slope annotated.

Edit the SUITES/SUMMARIES config block below, then run:

    python scripts/volume_scaling.py

Figures are saved to <outdir>/<summary>_volume_scaling.jpg.
"""

import argparse
import matplotlib
import matplotlib.pyplot as plt
import numpy as np
import os
import sys
from os.path import join, dirname, abspath

sys.path.insert(0, dirname(abspath(__file__)))
from kcut_utils import (  # noqa: E402
    discover_kcuts, granularity, kcut_label, pk_kmax, simple)
import model_scaling_diagnostics as MSD  # noqa: E402
from model_scaling_diagnostics import (  # noqa: E402
    summary_dir, fiducial_stdev, PARAM_IDXS, PARAM_NAMES)

# ── Configuration ───────────────────────────────────────────────────────────

_DEFAULT_WDIR = '/work/hdd/bdne/maho3/cmass-ili'
_DEFAULT_TRACER = 'galaxy'

# Suites to compare. L is the box side length in Mpc/h; volume is (L/1000)^3
# in (Gpc/h)^3. Suites must share the same k-cut grid (same pipeline `sim`).
SUITES = [
    {'nbody': 'quijotelike', 'sim': 'fastpm_charm7_cosmoHOD',
     'label': 'quijotelike (L=1 Gpc/h)', 'L': 1000},
    {'nbody': 'abacuslike', 'sim': 'fastpm_charm7_cosmoHOD',
     'label': 'abacuslike (L=2 Gpc/h)', 'L': 2000},
    {'nbody': 'mtnglike', 'sim': 'fastpm_charm7',
     'label': 'mtnglike (L=3 Gpc/h)', 'L': 3000},
]

SUMMARIES = ['zPk0', 'zPk0+zPk2+zPk4', 'zPk0+zPk2+zPk4+zEqBk0',
             'zPk0+zPk2+zPk4+zSqBk0', 'zPk0+zPk2+zPk4+zBk0']

# Reference power-spectrum kmax for the all-summary overlay figure.
REF_KMAX = 0.4

# Marker/colour per summary in the overlay figure.
_SUMMARY_COLORS = ['#1f77b4', '#ff7f0e', '#2ca02c', '#d62728', '#9467bd']
_SUMMARY_MARKERS = ['o', 's', '^', 'D', 'v']

matplotlib.use('Agg')
matplotlib.rcParams.update({
    'font.size': 13,
    'axes.titlesize': 11,
    'axes.labelsize': 13,
    'xtick.labelsize': 11,
    'ytick.labelsize': 11,
    'legend.fontsize': 10,
})


def _parse_args():
    p = argparse.ArgumentParser()
    p.add_argument('--wdir', default=_DEFAULT_WDIR)
    p.add_argument('--tracer', default=_DEFAULT_TRACER)
    p.add_argument('--outdir', default=None)
    p.add_argument('--ref-kmax', type=float, default=REF_KMAX,
                   help='Power-spectrum kmax held fixed in the all-summary '
                        'overlay figure (default 0.4).')
    p.add_argument('--nbar-lo', type=float, default=1.0e-4,
                   help='Lower edge of the fiducial-point nbar band.')
    p.add_argument('--nbar-hi', type=float, default=5.0e-4,
                   help='Upper edge of the fiducial-point nbar band.')
    return p.parse_args()


def volume(L):
    """Box volume in (Gpc/h)^3."""
    return (L / 1000.0) ** 3


def shared_kcuts(suites, summary, tracer, wdir):
    """k-cut dirnames present for every suite, ordered by increasing
    granularity (order taken from the first suite)."""
    per_suite = [
        {d for d, _, _ in discover_kcuts(
            summary_dir(s['nbody'], s['sim'], tracer, summary, wdir))}
        for s in suites
    ]
    common = set.intersection(*per_suite) if per_suite else set()
    ordered = discover_kcuts(
        summary_dir(suites[0]['nbody'], suites[0]['sim'], tracer, summary, wdir))
    return [(d, kmin, kmax) for d, kmin, kmax in ordered if d in common]


def plot_volume_scaling(suites, summary, tracer, wdir, outdir):
    kcuts = shared_kcuts(suites, summary, tracer, wdir)
    if not kcuts:
        print(f'  SKIP {summary} (no k-cut shared across all suites)')
        return

    Vs = np.array([volume(s['L']) for s in suites])
    nrows = len(kcuts)
    f, axs = plt.subplots(nrows, 2, figsize=(9, 2.7 * nrows + 0.6),
                          squeeze=False)

    for r, (dname, kmin, kmax) in enumerate(kcuts):
        stdevs = [fiducial_stdev(join(summary_dir(
            s['nbody'], s['sim'], tracer, summary, wdir), dname))
            for s in suites]

        for j, p in enumerate(PARAM_IDXS):
            ax = axs[r, j]
            xs, ys, ylo, yhi = [], [], [], []
            for V, sd in zip(Vs, stdevs):
                if sd is None:
                    continue
                perc = np.percentile(sd[:, p], [50, 16, 84])
                xs.append(V)
                ys.append(perc[0])
                ylo.append(perc[0] - perc[1])
                yhi.append(perc[2] - perc[0])

            if len(xs) < 2:
                ax.text(0.5, 0.5, 'insufficient data', ha='center',
                        va='center', transform=ax.transAxes, fontsize=9)
            else:
                xs, ys = np.array(xs), np.array(ys)
                order = np.argsort(xs)
                xs, ys = xs[order], ys[order]
                ylo = np.array(ylo)[order]
                yhi = np.array(yhi)[order]

                ax.errorbar(xs, ys, yerr=[ylo, yhi], fmt='o', color='C0',
                            capsize=4, zorder=3, label='measured')

                x0, y0 = xs[0], ys[0]
                xref = np.geomspace(xs.min() * 0.7, xs.max() * 1.4, 50)
                ax.plot(xref, y0 * (xref / x0) ** -0.5, ls='--',
                        color='gray', zorder=1, label=r'$\propto V^{-1/2}$')

                logx, logy = np.log(xs), np.log(ys)
                if len(xs) > 2:
                    slope = np.polyfit(logx, logy, 1)[0]
                else:
                    slope = (logy[-1] - logy[0]) / (logx[-1] - logx[0])
                ax.set_title(f'slope = {slope:.2f}  (expect -0.50)',
                             fontsize=10)

            ax.set_xscale('log')
            ax.set_yscale('log')
            ylabel = fr'$\Delta {PARAM_NAMES[p]}$'
            if j == 0:
                ylabel = f'{kcut_label(kmin, kmax, multiline=False)}\n' + ylabel
            ax.set(ylabel=ylabel)
            if r == nrows - 1:
                ax.set_xlabel(r'Volume $[(\mathrm{Gpc}/h)^3]$')
            ax.grid(True, which='both', alpha=0.3)

    axs[0, 1].legend(fontsize=8, loc='best')
    labels_str = ' vs '.join(s['label'] for s in suites)
    f.suptitle(f'{labels_str}\n{simple(summary)}: constraining power vs volume')
    plt.tight_layout()

    fpath = join(outdir, f"{summary.replace('+', '_')}_volume_scaling.jpg")
    f.savefig(fpath, dpi=100, bbox_inches='tight')
    plt.close(f)
    print(f'  Saved {fpath}')


def select_shared_kcut(suites, summary, tracer, wdir, ref_kmax):
    """Shared k-cut whose power-spectrum kmax is closest to ``ref_kmax``.

    Ties break toward the lower-granularity cut (smaller bispectrum kmax), so a
    summary with both zBk<0.2 and zBk<0.4 at the same zPk cut resolves
    deterministically. Returns ``(dirname, kmin, kmax)`` or None.
    """
    kcuts = shared_kcuts(suites, summary, tracer, wdir)
    if not kcuts:
        return None
    return min(kcuts, key=lambda t: (abs(pk_kmax(t[2]) - ref_kmax),
                                     granularity(t[1], t[2])))


def _slope(xs, ys):
    """Log-log slope of ys vs xs (least squares for >2 points, secant for 2)."""
    logx, logy = np.log(xs), np.log(ys)
    if len(xs) > 2:
        return float(np.polyfit(logx, logy, 1)[0])
    return float((logy[-1] - logy[0]) / (logx[-1] - logx[0]))


def plot_volume_scaling_summaries(suites, summaries, tracer, wdir, outdir,
                                  ref_kmax=REF_KMAX,
                                  fname='all_summaries_volume_scaling.jpg'):
    """Constraining power vs volume for every summary at one reference kmax.

    Volume on x, posterior stdev on y, both log, one line per summary across
    the box-size ladder. This is the direct read of how much each summary gains
    from a bigger box, against the V^-1/2 expectation.
    """
    # Gather one (x, stdev-array) series per summary, all at the same Pk cut.
    series = []  # (summary, klabel, xs, [stdev arrays aligned to xs])
    for summary in summaries:
        sel = select_shared_kcut(suites, summary, tracer, wdir, ref_kmax)
        if sel is None:
            print(f'  SKIP overlay {summary} (no shared k-cut)')
            continue
        dname, kmin, kmax = sel
        xs, sds = [], []
        for suite in suites:
            sd = fiducial_stdev(join(summary_dir(
                suite['nbody'], suite['sim'], tracer, summary, wdir), dname))
            if sd is None:
                print(f'  SKIP overlay {summary} @ {suite["label"]} (no data)')
                continue
            xs.append(volume(suite['L']))
            sds.append(sd)
        if len(xs) < 2:
            print(f'  SKIP overlay {summary} (fewer than 2 volumes)')
            continue
        order = np.argsort(xs)
        series.append((summary, kcut_label(kmin, kmax, multiline=False),
                       np.array(xs)[order], [sds[i] for i in order]))

    if not series:
        print('  SKIP all-summary overlay (no data)')
        return

    f, axs = plt.subplots(1, 2, figsize=(11, 4.8))
    for j, p in enumerate(PARAM_IDXS):
        ax = axs[j]
        curves = []  # (x, median) for the reference-line anchor
        for i, (summary, klabel, xs, sds) in enumerate(series):
            percs = np.array([np.percentile(sd[:, p], [50, 16, 84])
                              for sd in sds])
            med = percs[:, 0]
            yerr = [med - percs[:, 1], percs[:, 2] - med]
            ax.errorbar(xs, med, yerr=yerr,
                        color=_SUMMARY_COLORS[i % len(_SUMMARY_COLORS)],
                        marker=_SUMMARY_MARKERS[i % len(_SUMMARY_MARKERS)],
                        capsize=4, zorder=3,
                        label=f'{simple(summary)} [{klabel}]  '
                              f'slope {_slope(xs, med):+.2f}')
            curves.append((xs, med))

        # One V^-1/2 guide, anchored to the tightest posterior at the smallest
        # volume so it sits among the curves rather than above all of them.
        x0 = min(x[0] for x, _ in curves)
        y0 = min(m[0] for x, m in curves if x[0] == x0)
        xlo = min(x.min() for x, _ in curves) * 0.7
        xhi = max(x.max() for x, _ in curves) * 1.4
        xref = np.geomspace(xlo, xhi, 50)
        ax.plot(xref, y0 * (xref / x0) ** -0.5, ls='--', color='gray',
                zorder=1, label=r'$\propto V^{-1/2}$')

        ax.set(xscale='log', yscale='log',
               xlabel=r'Volume $[(\mathrm{Gpc}/h)^3]$',
               ylabel=fr'$\Delta {PARAM_NAMES[p]}$')
        ax.grid(True, which='both', alpha=0.3)
        ax.legend(fontsize=7, loc='best')

    labels_str = ' vs '.join(s['label'] for s in suites)
    f.suptitle(f'{labels_str}\nConstraining power vs volume at '
               fr'$k_{{\max}}^{{P}}\approx{ref_kmax:g}$')
    plt.tight_layout()
    fpath = join(outdir, fname)
    f.savefig(fpath, dpi=100, bbox_inches='tight')
    plt.close(f)
    print(f'  Saved {fpath}')


def run(suites, summaries, tracer, wdir, outdir=None,
        ref_kmax=REF_KMAX):
    if outdir is None:
        outdir = join(dirname(abspath(__file__)), 'figures', 'volume_scaling')
    os.makedirs(outdir, exist_ok=True)
    plot_volume_scaling_summaries(suites, summaries, tracer, wdir, outdir,
                                  ref_kmax=ref_kmax)
    for summary in summaries:
        plot_volume_scaling(suites, summary, tracer, wdir, outdir)


if __name__ == '__main__':
    _args = _parse_args()
    # fiducial_stdev reads this band from the model_scaling_diagnostics module.
    MSD.NBAR_LO = np.log10(_args.nbar_lo)
    MSD.NBAR_HI = np.log10(_args.nbar_hi)
    print(f'Fiducial nbar band: [{_args.nbar_lo:.1e}, {_args.nbar_hi:.1e}]')
    run(SUITES, SUMMARIES, _args.tracer, _args.wdir, _args.outdir,
        ref_kmax=_args.ref_kmax)
