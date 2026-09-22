"""
Figure 8 — sigma_8 calibration bias across the noise grid, OOD Abacus test.

Identical statistic, axes and colour scale to figure 6: 2 * (median coverage -
0.5) for sigma_8 per (sigma_rad, sigma_tran) bin, on a fixed [-1, 1] scale, for
zPk024+zBk0 at zPk<0.4, zBk<0.2. The two figures are directly comparable.

The grid is taken over all Abacus test points regardless of cosmology class.
The LCDM-Mnu=0-only version is printed to stdout for comparison, since that
subset is the one the notes' Mahalanobis heatmaps use.

    python fig8_ood_abacus_s8_heatmap.py
"""

import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import numpy as np

from talk_style import apply_style, save
import ood_io as O

TAG = 'abacus'
P = O.S8


def main():
    apply_style()
    d = O.load(TAG)
    ng = O.noises()
    th, med, ni = d['theta'], d['percs'][0], d['noiseidx']
    simple = O.cosm_classes(d['ids'])['simple']

    vals = O.coverage_bias(th, med, ni, P, len(ng))
    # same statistic restricted to the LCDM Mnu=0 subset, for the printout
    lcdm_ni = np.where(simple, ni, -1)
    vals_lcdm = O.coverage_bias(th, med, lcdm_ni, P, len(ng))
    grid, rad, tran = O.noise_grid(vals, ng)

    fig, ax = plt.subplots(figsize=(7.2, 5.4))
    O.draw_error_heatmap(fig, ax, grid, rad, tran, O.BIAS_LABEL,
                         vmin=-1, vmax=1)

    n_best = O.GOOD_NOISE[TAG]
    g2 = np.array(list(vals_lcdm.values()))
    print(f'{TAG} sigma_8 coverage bias (all classes): '
          f'min {np.nanmin(grid):+.3f}  max {np.nanmax(grid):+.3f}  '
          f'at chosen noise {n_best}: {vals[n_best]:+.3f}')
    print(f'  LCDM Mnu=0 only ({int(simple.sum())} pts): '
          f'min {g2.min():+.3f}  max {g2.max():+.3f}  '
          f'at chosen noise {n_best}: {vals_lcdm[n_best]:+.3f}')

    fig.suptitle(r'OOD $\sigma_8$ bias: Abacus'
                 '\n' r'$zP_{0,2,4}+B_0$, $k_{\max}^{P}<0.4$', y=1.0)
    fig.tight_layout()
    save(fig, 'fig8_ood_abacus_s8_bias_heatmap')


if __name__ == '__main__':
    main()
