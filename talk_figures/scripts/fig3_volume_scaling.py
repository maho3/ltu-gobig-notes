"""
Figure 3 — self-consistent fiducial constraining power vs box volume,
quijotelike/fastpm_charm7_cosmoHOD (L=1 Gpc/h) vs
abacuslike/fastpm_charm7_cosmoHOD (L=2 Gpc/h).

Both sides are cosmoHOD (HOD parameters inferred), unlike the earlier
volume-scaling figure in experiments/2026-08-19_self_abacuslike-fastpm_charm7,
which compared a cosmo-only quijotelike against a cosmoHOD abacuslike.

Each summary is evaluated at its k-cut nearest k_P = 0.4. Points sharing a
volume are offset slightly along the (logarithmic) x-axis so their error bars
stay separable. The dashed guide has the expected slope -1/2 and is anchored at
the geometric midpoint of the two volumes, at the geometric mean of every
plotted median in that panel — so it runs through the centre of the data and
only its slope, not its offset, carries meaning.

Both suites share mass resolution (L/N = 7.8 Mpc/h), so this is a volume
comparison rather than a resolution one.

    python fig3_volume_scaling.py
"""

import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import matplotlib.ticker as ticker
import numpy as np

from talk_style import apply_style, save, CYCLE, FIGSIZE_WIDE
import cache_io as C

SUITES = [
    {'nbody': 'quijotelike', 'sim': 'fastpm_charm7_cosmoHOD',
     'L': 1000, 'label': 'quijotelike'},
    {'nbody': 'abacuslike',  'sim': 'fastpm_charm7_cosmoHOD',
     'L': 2000, 'label': 'abacuslike'},
]
SUMMARIES = ['zPk0', 'zPk0+zPk2+zPk4', 'zPk0+zPk2+zPk4+zBk0']
REF_KMAX = 0.4
PARAMS = [0, 4]
YLABEL = {0: r'$\Delta \Omega_m$', 4: r'$\Delta \sigma_8$'}

XTICKS = [1, 2, 4, 8]
OFFSET = 1.085          # multiplicative x-offset between adjacent summaries


def volume(L):
    """Box volume in (Gpc/h)^3."""
    return (L / 1000.0) ** 3


def log_axis(ax, xlim):
    """A conventional log x-axis: labelled major ticks at XTICKS, unlabelled
    minor ticks at the usual decade subdivisions."""
    ax.set_xscale('log')
    ax.set_xlim(*xlim)
    ax.xaxis.set_major_locator(ticker.FixedLocator(XTICKS))
    ax.xaxis.set_major_formatter(ticker.FuncFormatter(lambda v, _: f'{v:g}'))
    subs = [v * 10 ** e for e in (-1, 0) for v in range(1, 10)]
    minors = [v for v in subs if xlim[0] < v < xlim[1] and v not in XTICKS]
    ax.xaxis.set_minor_locator(ticker.FixedLocator(minors))
    ax.xaxis.set_minor_formatter(ticker.NullFormatter())


def main():
    apply_style()
    V = np.array([volume(s['L']) for s in SUITES])

    rows = []
    for s in SUMMARIES:
        picks = [C.select(su['nbody'], su['sim'], s, REF_KMAX) for su in SUITES]
        if any(p is None for p in picks):
            print(f'  SKIP {s} (missing in one suite)')
            continue
        rows.append((s, picks))

    # symmetric multiplicative offsets about each volume
    n = len(rows)
    shifts = OFFSET ** (np.arange(n) - (n - 1) / 2)
    xlim = (V[0] / 1.9, V[1] * 1.9)

    fig, axs = plt.subplots(1, 2, figsize=FIGSIZE_WIDE)

    print(f'volume scaling at k_P ~ {REF_KMAX}   V = {V.tolist()} (Gpc/h)^3')
    for j, p in enumerate(PARAMS):
        ax = axs[j]
        all_y = []
        for i, (s, picks) in enumerate(rows):
            y = np.array([C.med(e, p) for e in picks])
            lo, hi = zip(*[C.yerr(e, p) for e in picks])
            all_y.extend(y)
            slope = np.log(y[1] / y[0]) / np.log(V[1] / V[0])
            # colour keyed to the summary's place in the full feature order, so
            # a summary keeps its colour across figures 2 and 3
            color = CYCLE[C.FEAT_ORDER.index(s) % len(CYCLE)]
            ax.errorbar(V * shifts[i], y, yerr=[lo, hi], color=color,
                        marker='o', markersize=7, capsize=4, zorder=3,
                        label=rf'{C.LABEL_SHORT[s]}  ({slope:+.2f})')
            print(f'  {s:24s} {"dOm" if p == 0 else "ds8"} '
                  f'{y[0]:.4f} -> {y[1]:.4f}  slope={slope:+.3f}')

        # y-range from the data (incl. error bars) before the guide is drawn,
        # so the guide is clipped to the data rather than stretching the axis
        lo_all = [C.med(e, p) - C.yerr(e, p)[0] for _, pk in rows for e in pk]
        hi_all = [C.med(e, p) + C.yerr(e, p)[1] for _, pk in rows for e in pk]
        ylim = (min(lo_all) / 1.18, max(hi_all) * 1.18)

        # slope -1/2 guide through the centre of the data
        x_mid = float(np.sqrt(V[0] * V[1]))
        y_mid = float(np.exp(np.mean(np.log(all_y))))
        xg = np.array(xlim)
        ax.plot(xg, y_mid * (xg / x_mid) ** -0.5, ls='--', color='0.45',
                lw=1.8, zorder=1, label=r'$\propto V^{-1/2}$')
        ax.set_ylim(*ylim)
        print(f'    guide anchored at V={x_mid:.2f}, '
              f'{"dOm" if p == 0 else "ds8"}={y_mid:.4f}')

        ax.set_yscale('log')
        # plain decimal tick labels read better on a slide than 4x10^-2
        ax.yaxis.set_major_locator(ticker.LogLocator(base=10, subs=(1, 2, 3, 4, 6, 8)))
        ax.yaxis.set_major_formatter(ticker.FuncFormatter(lambda v, _: f'{v:g}'))
        ax.yaxis.set_minor_formatter(ticker.NullFormatter())
        log_axis(ax, xlim)
        ax.set_xlabel(r'$V\ [(\mathrm{Gpc}/h)^3]$')
        ax.set_ylabel(YLABEL[p])
        ax.grid(True, which='major', alpha=0.3)

        # name the suite sitting at each volume
        for v, su in zip(V, SUITES):
            ax.annotate(su['label'], xy=(v, 1.0), xycoords=('data', 'axes fraction'),
                        xytext=(0, 3), textcoords='offset points',
                        ha='center', va='bottom', fontsize=10, color='0.45')

    axs[0].legend(loc='lower left', fontsize=11, labelspacing=0.3,
                  handletextpad=0.5, borderpad=0.4)

    fig.suptitle('self-consistent constraining power vs volume  '
                 r'($k_{\max}^{P}<0.4$, cosmo+HOD inference)', y=1.02)
    fig.tight_layout()
    save(fig, 'fig3_volume_scaling_kmax0.4')


if __name__ == '__main__':
    main()
