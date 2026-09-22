"""
Figure 2 — summary-complexity sweep at fixed k_max^P = 0.4,
abacuslike/fastpm_charm7_cosmoHOD.

Same statistic, panel layout and aspect as figure 1, but with the summary on a
categorical x-axis instead of the raw feature-vector length: at slide scale the
summary identity is the thing the audience needs to read, and the four
bispectrum summaries sit within ~20 features of each other, so a numeric x
crowds them into an unreadable clump. Feature length is kept as a sub-label.

For each summary the k-cut whose Pk cut is closest to 0.4 is used (ties broken
toward the smaller Bk cut), matching kcut_utils.select_kcut. That means the
bispectrum summaries are evaluated at zPk<0.4, zBk<0.2.

    python fig2_feature_sweep.py
"""

import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import matplotlib.ticker as ticker
import numpy as np

from talk_style import apply_style, save, CYCLE, FIGSIZE
import cache_io as C

NBODY, SIM = 'abacuslike', 'fastpm_charm7_cosmoHOD'
REF_KMAX = 0.4
PARAMS = [0, 4]
YLABEL = {0: r'$\Delta \Omega_m$', 4: r'$\Delta \sigma_8$'}


def main():
    apply_style()

    picks = []
    for s in C.FEAT_ORDER:
        e = C.select(NBODY, SIM, s, REF_KMAX)
        if e is None:
            print(f'  MISSING {s}')
            continue
        picks.append(e)

    x = np.arange(len(picks))
    fig, axs = plt.subplots(1, 2, figsize=FIGSIZE)

    print(f'{NBODY}/{SIM}  feature sweep at k_P ~ {REF_KMAX}')
    for j, p in enumerate(PARAMS):
        ax = axs[j]
        for i, e in enumerate(picks):
            lo, hi = C.yerr(e, p)
            ax.errorbar(x[i], C.med(e, p), yerr=[[lo], [hi]],
                        fmt='o', color=CYCLE[i % len(CYCLE)],
                        markersize=10, capsize=5, zorder=3)
            if j == 0:
                bk = e['bk_kmax']
                print(f"  {e['summary']:24s} k_P<{e['pk_kmax']:g}"
                      f"{'' if bk is None else f', k_B<{bk:g}'}"
                      f"  x_len={e['x_len']:3d}  n_fid={e['n_fid']}"
                      f"  dOm={C.med(e,0):.4f}  ds8={C.med(e,4):.4f}")

        ax.set_xticks(x)
        # five categories in a half-slide-wide panel: rotate or they collide
        ax.set_xticklabels([C.LABEL_SHORT[e['summary']] for e in picks],
                           rotation=45, ha='right', rotation_mode='anchor')
        ax.yaxis.set_major_locator(ticker.MaxNLocator(6))
        ax.set_xlim(-0.5, len(picks) - 0.5)
        ax.set_ylim(0, None)
        ax.set_ylabel(YLABEL[p])
        ax.grid(axis='x', alpha=0.0)   # categorical axis: horizontal grid only

        # Feature-vector length, in place of the numeric x-axis the notes'
        # version used. It sits inside the axes along the bottom, which is
        # empty here because the y-axis is anchored at zero.
        for i, e in enumerate(picks):
            ax.annotate(str(e['x_len']), xy=(x[i], 0.015),
                        xycoords=('data', 'axes fraction'),
                        ha='center', va='bottom', fontsize=10, color='0.45')
        ax.annotate('features', xy=(0.5, 0.075), xycoords='axes fraction',
                    ha='center', va='bottom', fontsize=10, color='0.45')

    axs[1].set_ylim(0, 0.105)

    # The bispectrum cut is common to the three right-hand points; noting it
    # inside the axes keeps the suptitle the same width as figure 1's.
    axs[1].annotate(r'all $B_0$ at $k_{\max}^{B}<0.2$',
                    xy=(0.97, 0.93), xycoords='axes fraction',
                    ha='right', va='top', fontsize=12, color='0.45')

    fig.suptitle('abacuslike ($L=2\\,$Gpc/$h$)\n'
                 r'redshift-space summaries at $k_{\max}^{P}<0.4$', y=1.005)
    fig.tight_layout()
    save(fig, 'fig2_feature_sweep_kmax0.4')


if __name__ == '__main__':
    main()
