"""
Figure 6 — sigma_8 calibration bias across the noise grid, OOD quijote test.

Each cell is 2 * (median coverage - 0.5) for sigma_8 over the test points at
that (sigma_rad, sigma_tran), for zPk024+zBk0 at zPk<0.4, zBk<0.2. Median
coverage is the statistic the notes' heatmaps use
(scripts/noise_calibration_all.py): the fraction of truths below the posterior
median. Rescaling puts 0 at unbiased on a fixed [-1, 1] scale, so this figure
and figure 8 share one colour scale and one set of axes.

Blue (positive) = sigma_8 over-predicted, red (negative) = under-predicted.

    python fig6_ood_quijote_s8_heatmap.py
"""

import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import numpy as np

from talk_style import apply_style, save
import ood_io as O

TAG = 'quijote'
P = O.S8


def main():
    apply_style()
    d = O.load(TAG)
    ng = O.noises()
    th, med, ni = d['theta'], d['percs'][0], d['noiseidx']

    vals = O.coverage_bias(th, med, ni, P, len(ng))
    grid, rad, tran = O.noise_grid(vals, ng)

    fig, ax = plt.subplots(figsize=(7.2, 5.4))
    O.draw_error_heatmap(fig, ax, grid, rad, tran, O.BIAS_LABEL,
                         vmin=-1, vmax=1)

    n_best = O.GOOD_NOISE[TAG]
    print(f'{TAG} sigma_8 coverage bias: min {np.nanmin(grid):+.3f}  '
          f'max {np.nanmax(grid):+.3f}  '
          f'at chosen noise {n_best}: {vals[n_best]:+.3f}')

    fig.suptitle(r'OOD $\sigma_8$ bias: quijote N-body'
                 '\n' r'$zP_{0,2,4}+B_0$, $k_{\max}^{P}<0.4$', y=1.0)
    fig.tight_layout()
    save(fig, 'fig6_ood_quijote_s8_bias_heatmap')


if __name__ == '__main__':
    main()
