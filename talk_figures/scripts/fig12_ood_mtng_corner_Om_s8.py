"""
Figure 12 — Omega_m / sigma_8 corners for the 3 Gpc/h OOD test, one per
summary, for the same test point as the full corners in figure 11.

Train mtnglike/fastpm_charm7, test quijote3gpch/nbody, all at k_P < 0.4:
  12a  zPk0     12b  zPk0+zPk2+zPk4     12c  zPk0+zPk2+zPk4+zBk0 (zBk < 0.2)

Test point, noise bin and data loading are imported from figure 11 so the two
sets cannot drift apart. Styling follows figure 10. Each figure keeps its own
axis ranges (widened to always include the truth), so the zPk0 contours are
not directly size-comparable with the other two by eye.

    python fig12_ood_mtng_corner_Om_s8.py
"""

import matplotlib
matplotlib.use('Agg')
import corner
import numpy as np

from talk_style import apply_style, save, COLORS
import ood_io as O
from fig11_ood_mtng_corner import (CELLS, NOISE_BIN, SELECT_ON, P, NAMES,
                                   load_cell, joint_z)


def main():
    apply_style()
    ng = O.noises()
    cells = {s: load_cell(s, k) for s, k, _, _ in CELLS}

    theta, noiseidx, ids, samp_sel = cells[SELECT_ON]
    rows = np.flatnonzero(noiseidx == NOISE_BIN)
    zs = np.array([joint_z(theta[i], samp_sel[:, i]) for i in rows])
    i = rows[np.argsort(zs)[len(zs) // 2]]
    truth = theta[i][P]
    print(f'test row {i}, lhid {ids[i]}, noise bin {NOISE_BIN} '
          f'(sig_rad={ng[NOISE_BIN,0]:.2f}, sig_tran={ng[NOISE_BIN,1]:.2f})')

    for summary, kcut, pretty, fname in CELLS:
        samples = cells[summary][3][:, i, :][:, P]
        z = joint_z(theta[i], cells[summary][3][:, i, :])
        print(f'  {summary:24s} joint z {z:.2f}')

        fig = corner.corner(
            samples, labels=[O.label(NAMES[p]) for p in P], truths=truth,
            range=O.corner_range(samples, truth),
            truth_color=COLORS['accent'], color=COLORS['primary'],
            show_titles=True, title_fmt='.3f',
            plot_datapoints=False, fill_contours=True,
            levels=(0.68, 0.95), bins=30, smooth=1.0, smooth1d=1.0,
            max_n_ticks=4,
            hist_kwargs={'lw': 1.8},
            contour_kwargs={'linewidths': 1.1},
            label_kwargs={'fontsize': 17},
            title_kwargs={'fontsize': 14},
        )
        fig.set_size_inches(6.6, 6.6)
        for ax in fig.get_axes():
            ax.tick_params(labelsize=12)
            ax.grid(False)
            ax.xaxis.labelpad = 10
            ax.yaxis.labelpad = 10

        fig.suptitle(rf'3 Gpc/$h$ OOD, lhid {ids[i]}:  {pretty}, '
                     r'$k_{\max}^{P}<0.4$' '\n'
                     rf'$\sigma_{{\rm rad}}=\sigma_{{\rm tran}}={ng[NOISE_BIN,0]:.2f}$'
                     rf'   ·   joint $z={z:.1f}$   ·   red = truth',
                     fontsize=14, y=1.10)
        save(fig, fname.replace('fig11', 'fig12').replace('corner', 'corner_Om_s8'))


if __name__ == '__main__':
    main()
