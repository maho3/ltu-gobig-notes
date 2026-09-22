"""
Figure 8b — per-parameter z over the noise grid, OOD Abacus test.

Companion to figure 8. That figure plots the notes' statistic exactly: one
*joint* Mahalanobis z over (Omega_m, sigma_8), using the full 2x2 posterior
covariance including their correlation. A joint z is a single number, so it
cannot be split per parameter.

This figure instead shows the 1D marginal z of each parameter separately,

    z_p = | theta_true,p - posterior median_p | / sqrt(C_pp)

averaged over the LCDM Mnu=0 test points in each noise bin. This is the
diagonal (per-parameter) version of the same quantity: it drops the Om-s8
correlation, so it is not the notes' statistic and the two will not agree
numerically -- z_joint accounts for the degeneracy direction, z_p does not.

Everything else follows the notes' Abacus convention: x = sigma_tran,
y = sigma_rad, origin='lower', RdYlGn_r on 0-4, black contour at z = 2.

    python fig8b_ood_abacus_z_per_param.py
"""

import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import numpy as np

from talk_style import apply_style, save
import ood_io as O
from fig8_ood_abacus_lcdm_z_heatmap import (
    PARAM_INDICES, SAMPLES_PATH, VMAX, noise_pivot)

TAG = 'abacus'
LABEL = {0: r'$\Omega_m$', 4: r'$\sigma_8$'}


def compute_z_per_param(theta, samples_sub, sub_idx, noiseidx, n_noise,
                        simple_mask):
    """Mean |d_p| / sqrt(C_pp) per noise bin, for each of PARAM_INDICES."""
    pos = {t: k for k, t in enumerate(sub_idx)}
    out = np.full((len(PARAM_INDICES), n_noise), np.nan)
    for i in range(n_noise):
        sel = np.where(noiseidx == i)[0]
        sel_s = sel[simple_mask[sel]]
        if len(sel_s) == 0:
            continue
        acc = [[] for _ in PARAM_INDICES]
        for pt in sel_s:
            draws = samples_sub[:, pos[pt], :]
            d = theta[pt, PARAM_INDICES] - np.median(draws, axis=0)
            sd = np.std(draws, axis=0)
            for k in range(len(PARAM_INDICES)):
                acc[k].append(abs(d[k]) / sd[k])
        for k in range(len(PARAM_INDICES)):
            out[k, i] = np.mean(acc[k])
    return out


def main():
    apply_style()
    d = O.load(TAG)
    ng = O.noises()
    theta, noiseidx = d['theta'], d['noiseidx']
    simple = O.cosm_classes(d['ids'])['simple']

    sub_idx = np.flatnonzero(simple)
    mm = np.load(SAMPLES_PATH, mmap_mode='r')
    samples_sub = np.asarray(mm[:, sub_idx, :])[:, :, PARAM_INDICES]
    print(f'{TAG}: {len(sub_idx)} LCDM Mnu=0 points, samples {samples_sub.shape}')

    zs = compute_z_per_param(theta, samples_sub, sub_idx, noiseidx,
                             len(ng), simple)

    fig, axs = plt.subplots(1, 2, figsize=(12.5, 5.2))
    im = None
    for k, p in enumerate(PARAM_INDICES):
        ax = axs[k]
        grid, rad_vals, tran_vals = noise_pivot(ng, zs[k])
        ext = [-0.5, len(tran_vals) - 0.5, -0.5, len(rad_vals) - 0.5]
        im = ax.imshow(grid, aspect='auto', origin='lower', vmin=0, vmax=VMAX,
                       cmap='RdYlGn_r', extent=ext)
        if not np.all(np.isnan(grid)):
            ax.contour(grid, levels=[2.0], colors='k', linewidths=1.6,
                       extent=ext)
        for i in range(grid.shape[0]):
            for j in range(grid.shape[1]):
                if not np.isnan(grid[i, j]):
                    ax.text(j, i, f'{grid[i, j]:.1f}', ha='center',
                            va='center', fontsize=9, color='0.15')

        ax.set_xticks(range(len(tran_vals)))
        ax.set_xticklabels([f'{v:.2f}' for v in tran_vals])
        ax.set_yticks(range(len(rad_vals)))
        ax.set_yticklabels([f'{v:.2f}' for v in rad_vals])
        ax.set_xlabel(r'$\sigma_{\rm tran}$')
        ax.set_ylabel(r'$\sigma_{\rm rad}$')
        ax.set_title(LABEL[p], pad=8)
        ax.grid(False)
        ax.tick_params(which='minor', bottom=False, left=False, top=False,
                       right=False)
        print(f'  {LABEL[p]:12s} zbar min {np.nanmin(grid):.2f}  '
              f'max {np.nanmax(grid):.2f}  '
              f'cells < 2: {int((grid < 2).sum())}/{grid.size}')

    cb = fig.colorbar(im, ax=axs, fraction=0.030, pad=0.02)
    cb.set_label(r'$\bar{z}$   (black contour: $\bar{z}=2$)')

    fig.suptitle(r'Abacus OOD: per-parameter $\bar{z}$ '
                 r'($\Lambda$CDM $M_\nu=0$)   ·   '
                 r'$zP_{0,2,4}+B_0$, $k_{\max}^{P}<0.4$', y=1.0)
    save(fig, 'fig8b_ood_abacus_z_per_param')


if __name__ == '__main__':
    main()
