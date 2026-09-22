"""
Figure 8 — mean joint Mahalanobis z over the noise grid, OOD Abacus test.

This reproduces the statistic and grid layout of `_compute_lcdm_z`,
`_noise_pivot` and `_draw_z_heatmap` in
ltu-gobig-notes/scripts/ood_abacus_inference.py exactly, restyled for a slide.

Abacus cosmologies are not drawn from the training prior, so coverage-style
calibration statistics are not meaningful for this suite and the notes omit
them. The notes use instead, per LCDM Mnu=0 test point,

    z = sqrt( d^T C^-1 d ),  d = theta_true - posterior median over (Om, s8),
    C = the 2x2 posterior covariance of those two parameters (full covariance,
        including the Om-s8 correlation)

averaged over the LCDM Mnu=0 points in each noise bin. Green = recovered,
red = biased; the black contour marks z = 2.

Note the axis convention differs from figure 6 and follows the notes' Abacus
script: x = sigma_tran, y = sigma_rad, origin='lower'. That is the orientation
`_noise_pivot` produces, and it is transposed relative to the coverage heatmaps
in noise_calibration_all.py.

Needs the full posterior samples (the cache stores only percentiles), so it
reads the LCDM Mnu=0 columns of the OOD posterior file via mmap.

    python fig8_ood_abacus_lcdm_z_heatmap.py
"""

import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import numpy as np

from talk_style import apply_style, save
import ood_io as O

TAG = 'abacus'
PARAM_INDICES = [0, 4]        # Omega_m, sigma_8 — as in the notes' script
VMAX = 4.0
SAMPLES_PATH = (
    '/work/hdd/bdne/maho3/cmass-ili/abacuslike/fastpm_charm7_cosmoHOD/models/'
    'galaxy/zPk0+zPk2+zPk4+zBk0/kmin-0.0_kmax-zBk=0.2__zPk=0.4/testing/'
    'abacus_nbody_comp_gridnoise/posterior_samples.npy')


def compute_lcdm_z(theta, samples_sub, sub_idx, noiseidx, n_noise, simple_mask):
    """Mean joint Mahalanobis z per noise bin — verbatim logic from
    `_compute_lcdm_z` in scripts/ood_abacus_inference.py, but indexing a
    pre-sliced samples array holding only the LCDM Mnu=0 test points."""
    pos = {t: k for k, t in enumerate(sub_idx)}
    z_per_noise = np.full(n_noise, np.nan)
    for i in range(n_noise):
        sel = np.where(noiseidx == i)[0]
        sel_s = sel[simple_mask[sel]]
        if len(sel_s) == 0:
            continue
        zvals = []
        for pt in sel_s:
            draws = samples_sub[:, pos[pt], :]           # (n_draw, 2)
            d = theta[pt, PARAM_INDICES] - np.median(draws, axis=0)
            cov = np.cov(draws, rowvar=False)
            try:
                cinv = np.linalg.inv(cov)
            except np.linalg.LinAlgError:
                cinv = np.linalg.pinv(cov)
            zvals.append(np.sqrt(d @ cinv @ d))
        z_per_noise[i] = np.mean(zvals)
    return z_per_noise


def noise_pivot(noises, values):
    """grid[i, j] with i indexed by sigma_rad and j by sigma_tran — the
    orientation of `_noise_pivot` in the notes' Abacus script."""
    rad_vals = np.unique(noises[:, 0])
    tran_vals = np.unique(noises[:, 1])
    grid = np.full((len(rad_vals), len(tran_vals)), np.nan)
    for k, (r, t) in enumerate(noises):
        grid[np.searchsorted(rad_vals, r), np.searchsorted(tran_vals, t)] = values[k]
    return grid, rad_vals, tran_vals


def main():
    apply_style()
    d = O.load(TAG)
    ng = O.noises()
    theta, noiseidx = d['theta'], d['noiseidx']
    simple = O.cosm_classes(d['ids'])['simple']

    sub_idx = np.flatnonzero(simple)
    print(f'{TAG}: {len(sub_idx)} LCDM Mnu=0 test points; reading their columns')
    mm = np.load(SAMPLES_PATH, mmap_mode='r')
    samples_sub = np.asarray(mm[:, sub_idx, :])[:, :, PARAM_INDICES]
    print(f'  samples subset {samples_sub.shape}')

    z = compute_lcdm_z(theta, samples_sub, sub_idx, noiseidx, len(ng), simple)
    grid, rad_vals, tran_vals = noise_pivot(ng, z)

    fig, ax = plt.subplots(figsize=(7.2, 5.6))
    im = ax.imshow(grid, aspect='auto', origin='lower',
                   vmin=0, vmax=VMAX, cmap='RdYlGn_r',
                   extent=[-0.5, len(tran_vals) - 0.5,
                           -0.5, len(rad_vals) - 0.5])
    if not np.all(np.isnan(grid)):
        ax.contour(grid, levels=[2.0], colors='k', linewidths=1.6,
                   extent=[-0.5, len(tran_vals) - 0.5,
                           -0.5, len(rad_vals) - 0.5])

    for i in range(grid.shape[0]):
        for j in range(grid.shape[1]):
            if np.isnan(grid[i, j]):
                continue
            ax.text(j, i, f'{grid[i, j]:.1f}', ha='center', va='center',
                    fontsize=10, color='0.15')

    ax.set_xticks(range(len(tran_vals)))
    ax.set_xticklabels([f'{v:.2f}' for v in tran_vals])
    ax.set_yticks(range(len(rad_vals)))
    ax.set_yticklabels([f'{v:.2f}' for v in rad_vals])
    ax.set_xlabel(r'$\sigma_{\rm tran}$')
    ax.set_ylabel(r'$\sigma_{\rm rad}$')
    ax.grid(False)
    ax.tick_params(which='minor', bottom=False, left=False, top=False,
                   right=False)

    cb = fig.colorbar(im, ax=ax, fraction=0.046, pad=0.03)
    cb.set_label(r'$\bar{z}$   (black contour: $\bar{z}=2$)')

    n_best = O.GOOD_NOISE[TAG]
    print(f'  zbar: min {np.nanmin(grid):.2f}  max {np.nanmax(grid):.2f}  '
          f'at noise {n_best}: {z[n_best]:.2f}')
    print(f'  cells within 2 sigma: {int((grid < 2).sum())} of {grid.size}')

    fig.suptitle(r'Abacus OOD: Mahalanobis $\bar{z}$ ($\Lambda$CDM $M_\nu=0$)'
                 '\n' r'$zP_{0,2,4}+B_0$, $k_{\max}^{P}<0.4$', y=1.0)
    fig.tight_layout()
    save(fig, 'fig8_ood_abacus_lcdm_z_heatmap')


if __name__ == '__main__':
    main()
