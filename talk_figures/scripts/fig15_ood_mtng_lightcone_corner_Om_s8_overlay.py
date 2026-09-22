"""
Figure 15 — the three Omega_m / sigma_8 lightcone corners of figure 14 overlaid
on one plot with transparent filled contours.

Same test point and noise configuration as figures 13-14 (selection imported
from that script). The axes span the cosmology prior (the 'quijote' prior used in training), and
the three summaries share identical histogram bins, so contour
sizes and 1D peak heights are directly comparable: every posterior has the same
number of draws, so a lower 1D peak means a wider posterior.

If cache/lightcone_resample_row<row>.npz exists (build_lightcone_resample.py),
the contours use its 100k resampled draws instead of the 2000 saved by
validate.py, which makes the 68/95% contours much less noisy. The quoted joint
z is recomputed from whichever draws are plotted.

Colours: P0 orange, P024 green, P024+B0 blue (Okabe-Ito); truth black.
68% regions are solid outlines with a light fill, 95% dashed with a faint fill.

    python fig15_ood_mtng_lightcone_corner_Om_s8_overlay.py
"""

import matplotlib
matplotlib.use('Agg')
import corner
import os
import numpy as np
from matplotlib.colors import to_rgba
from matplotlib.lines import Line2D
from matplotlib.patches import Patch

from talk_style import apply_style, save, COLORS, CYCLE
import ood_io as O
from fig13_ood_mtng_lightcone_corners import (CELLS, P, load_cell, joint_z,
                                             param_names, label, select_row)

# Overlap-legible styling, shared with figure 16. Okabe-Ito colourblind-safe
# hues that stay distinguishable where they overlap (the earlier blue/green/
# purple mixed into one grey-blue); the tightest posterior (P024+B0) gets the
# strongest colour. Truth is black so it does not compete with the palette.
COLOR = {'Pk0': '#E69F00', 'Pk024': '#009E73', 'Pk024_Bk0': '#0072B2'}
TRUTH_COLOR = 'k'
# fill alpha for the 95% and 68% bands
# A light but visible 95% fill and a darker 68% fill, so both regions read
# as filled areas while three stacked layers stay see-through.
ALPHA_95, ALPHA_68 = 0.16, 0.40
LW_68, LW_95 = 2.0, 1.4
LS_68, LS_95 = '-', '--'
BINS = 50          # histogram bins per axis over the prior range

# 'quijote' cosmology prior, ltu-cmass/cmass/infer/train.py::prepare_prior
PRIOR = {0: (0.1, 0.5), 1: (0.03, 0.07), 2: (0.5, 0.9), 3: (0.8, 1.2), 4: (0.6, 1.0)}


def main():
    apply_style()
    ng = O.noises()
    cells = {s: load_cell(s, k) for s, k, _, _ in CELLS}
    names = param_names(*CELLS[0][:2])
    theta, noiseidx, _, _ = cells[CELLS[0][0]]

    # identical selection rule to figures 13-14
    z = {s: np.array([joint_z(theta[r], cells[s][3][:, r]) for r in range(len(theta))])
         for s, _, _, _ in CELLS}
    i = select_row(noiseidx, sum(z.values()))
    n = noiseidx[i]
    truth = theta[i][P]
    subs = {s: cells[s][3][:, i, :] for s, _, _, _ in CELLS}
    rs_path = os.path.join(O.CACHEDIR, f'lightcone_resample_row{i}.npz')
    if os.path.exists(rs_path):
        rs = np.load(rs_path)
        subs = {s: rs[tag] for s, _, _, tag in CELLS}
        print(f'using {int(rs["n_draws"])} resampled draws from {rs_path}')
    else:
        print('no resample cache: using the 2000 saved draws')
    z = {s: {i: joint_z(theta[i], subs[s])} for s, _, _, _ in CELLS}
    subs = {s: subs[s][:, P] for s in subs}
    print(f'test row {i}, noise {n} (sig_rad={ng[n,0]:.2f}, sig_tran={ng[n,1]:.2f})')

    # axes span the cosmology prior. Values are the 'quijote' prior limits in
    # ltu-cmass/cmass/infer/train.py::prepare_prior (the models' infer.prior).
    rng = [PRIOR[p] for p in P]
    for k, p in enumerate(P):
        if not rng[k][0] <= truth[k] <= rng[k][1]:
            raise ValueError(f'truth for {names[p]} outside the prior')

    fig = None
    handles = []
    for s, _, pretty, tag in CELLS:
        c = COLOR[tag]
        fig = corner.corner(
            subs[s], fig=fig, range=rng, color=c,
            labels=[label(names[p]) for p in P],
            plot_datapoints=False, plot_density=False, fill_contours=True,
            levels=(0.68, 0.95), bins=BINS, smooth=1.0, smooth1d=1.0,
            max_n_ticks=4,
            hist_kwargs={'lw': 2.2, 'color': c},
            # corner draws the 95% level first, then 68%
            contour_kwargs={'colors': [c], 'linewidths': [LW_95, LW_68],
                            'linestyles': [LS_95, LS_68]},
            # corner fills three bands: outside-95%, 95-68%, inside-68%. The
            # outer band must be fully transparent or it tints the whole panel,
            # which is what a single global alpha does.
            contourf_kwargs={'colors': [(1, 1, 1, 0), to_rgba(c, ALPHA_95),
                                        to_rgba(c, ALPHA_68)]},
            label_kwargs={'fontsize': 18},
        )
        handles.append(Patch(facecolor=to_rgba(c, ALPHA_68), edgecolor=c, lw=LW_68,
                             label=rf'{pretty}   ($z={z[s][i]:.1f}$)'))
        for k, p in enumerate(P):
            q = np.percentile(subs[s][:, k], [16, 50, 84])
            print(f'  {s:18s} {names[p]:8s} {q[1]:.4f} -{q[1]-q[0]:.4f} +{q[2]-q[1]:.4f}')

    corner.overplot_lines(fig, truth, color=TRUTH_COLOR, lw=1.6)
    corner.overplot_points(fig, truth[None], marker='s', color=TRUTH_COLOR, ms=6)
    handles.append(Line2D([], [], color=TRUTH_COLOR, lw=1.6, label='truth'))
    handles.append(Line2D([], [], color='0.4', lw=LW_68, ls=LS_68, label='68%'))
    handles.append(Line2D([], [], color='0.4', lw=LW_95, ls=LS_95, label='95%'))

    fig.set_size_inches(7.2, 7.2)
    for ax in fig.get_axes():
        ax.tick_params(labelsize=12)
        ax.grid(False)
        ax.xaxis.labelpad = ax.yaxis.labelpad = 10
    fig.legend(handles=handles, loc='upper right', bbox_to_anchor=(0.97, 0.95),
               fontsize=13, frameon=False, handlelength=1.6)
    fig.suptitle(r'MTNG lightcone OOD, $k_{\max}^{P}<0.4$' '\n'
                 rf'$\sigma_{{\rm rad}}={ng[n,0]:.2f}$, $\sigma_{{\rm tran}}={ng[n,1]:.2f}$',
                 fontsize=15, y=1.04)
    save(fig, 'fig15_ood_mtng_lightcone_corner_Om_s8_overlay')


if __name__ == '__main__':
    main()
