"""
Figure 1 — kmax scaling for the zPk024+zBk0 summary, abacuslike/fastpm_charm7_cosmoHOD.

Self-consistent fiducial posterior stdev vs power-spectrum kmax. The summary has
four k-cuts: three sharing k_B < 0.2 (a line across k_P) plus one at k_B < 0.4,
which is plotted as its own series so the dynamic cut stays distinguishable.

    python fig1_kmax_scaling_Bk0.py
"""

import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import matplotlib.ticker as ticker
import numpy as np

from talk_style import apply_style, save, COLORS, PARAM, FIGSIZE
import cache_io as C

NBODY, SIM = 'abacuslike', 'fastpm_charm7_cosmoHOD'
SUMMARY = 'zPk0+zPk2+zPk4+zBk0'
PARAMS = [0, 4]

# bk cut -> (color, marker, label, x-offset). The offset only separates the two
# series where they share a k_P, so the k_B<0.4 point stays readable.
SERIES = {
    0.2: (COLORS['primary'], 'o', r'$k_{\max}^{B} < 0.2$',  0.000),
    0.4: (COLORS['accent'],  'D', r'$k_{\max}^{B} < 0.4$',  0.018),
}


def main():
    apply_style()
    ent = C.entries(NBODY, SIM, SUMMARY)

    by_bk = {}
    for e in ent:
        by_bk.setdefault(e['bk_kmax'], []).append(e)

    fig, axs = plt.subplots(1, 2, figsize=FIGSIZE)

    print(f'{NBODY}/{SIM}  {SUMMARY}')
    for j, p in enumerate(PARAMS):
        ax = axs[j]
        for bk in sorted(by_bk):
            pts = sorted(by_bk[bk], key=lambda x: x['pk_kmax'])
            color, marker, lab, dx = SERIES[bk]
            x = [e['pk_kmax'] + dx for e in pts]
            y = [C.med(e, p) for e in pts]
            lo, hi = zip(*[C.yerr(e, p) for e in pts])
            # A single-point series gets no connecting line.
            ax.errorbar(x, y, yerr=[lo, hi], color=color, marker=marker,
                        linestyle='-' if len(x) > 1 else 'none',
                        capsize=4, markersize=8, label=lab, zorder=3)
            if j == 0:
                for e in pts:
                    print(f"  k_B<{bk:g}  k_P<{e['pk_kmax']:g}  "
                          f"x_len={e['x_len']:3d}  n_fid={e['n_fid']}  "
                          f"dOm={C.med(e,0):.4f}  ds8={C.med(e,4):.4f}")

        ax.set_xlabel(r'$k_{\max}^{P}\ \ [h\,\mathrm{Mpc}^{-1}]$')
        ax.set_ylabel(rf'$\Delta${PARAM[p]}'.replace('$$', ''))
        ax.set_ylim(0, None)
        ax.set_xlim(0.13, 0.67)
        ax.set_xticks([0.2, 0.3, 0.4, 0.5, 0.6])
        ax.yaxis.set_major_locator(ticker.MaxNLocator(6))

    axs[0].set_ylabel(r'$\Delta \Omega_m$')
    axs[1].set_ylabel(r'$\Delta \sigma_8$')
    # data sits in the upper half (y starts at zero), so the legend goes low
    axs[1].legend(loc='lower left', labelspacing=0.3, handletextpad=0.5)

    fig.suptitle('abacuslike ($L=2\\,$Gpc/$h$)\n'
                 r'redshift-space $P_{0,2,4}+B_0$', y=1.005)
    fig.tight_layout()
    save(fig, 'fig1_kmax_scaling_Pk024_Bk0')


if __name__ == '__main__':
    main()
