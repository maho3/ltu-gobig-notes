"""
Figure 16 — Gaussian-approximation version of figure 15.

Each summary's (Omega_m, sigma_8) posterior is replaced by a 2D Gaussian with
the sample mean and covariance of its draws, and drawn as filled 1-sigma and
2-sigma ellipses, with Gaussian 1D marginals on the diagonal.

"1 sigma / 2 sigma" follows the usual 2D-contour convention: the ellipses enclose
68.3% and 95.4% of the 2D Gaussian (Delta chi^2 = 2.30 and 6.18), matching the
68/95% levels of figure 15 -- not Mahalanobis radius 1 and 2, which would
enclose only 39% and 86%.

This deliberately ignores non-Gaussian structure (the P024 Omega_m posterior
piling against the 0.5 prior edge, P0's double peak) and the prior truncation:
the moments are taken from prior-bounded draws, and the ellipses can extend
past the prior box, where they are clipped by the axes.

Draws, test point and axes are identical to figure 15 (100k resampled draws
from cache/lightcone_resample_row<row>.npz; axes = cosmology prior).

    python fig16_ood_mtng_lightcone_gaussian_ellipses.py
"""

import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import numpy as np
from matplotlib.colors import to_rgba
from matplotlib.lines import Line2D
from matplotlib.patches import Ellipse, Patch
from os.path import join
from scipy.stats import chi2, norm

from talk_style import apply_style, save, COLORS
import ood_io as O
from fig13_ood_mtng_lightcone_corners import CELLS, P, TEST, NOISE_BIN, label
from fig15_ood_mtng_lightcone_corner_Om_s8_overlay import (
    COLOR, PRIOR, TRUTH_COLOR, ALPHA_95, ALPHA_68, LW_68, LW_95, LS_68, LS_95)

# 2D enclosed probability of 1 and 2 sigma
LEVELS = {1: 0.6827, 2: 0.9545}


def ellipse(mean, cov, prob, **kw):
    """Ellipse enclosing `prob` of a 2D Gaussian."""
    vals, vecs = np.linalg.eigh(cov)          # ascending: vals[1] is the major axis
    scale = np.sqrt(chi2.ppf(prob, df=2))
    # Ellipse's width lies along `angle`, so width must be the major axis
    width, height = 2 * scale * np.sqrt(vals[1]), 2 * scale * np.sqrt(vals[0])
    angle = np.degrees(np.arctan2(vecs[1, 1], vecs[0, 1]))
    return Ellipse(mean, width, height, angle=angle, **kw)


def main():
    apply_style()
    ng = O.noises()
    rs = np.load(join(O.CACHEDIR, f'lightcone_resample_row*.npz'.replace('*', '18')))
    row = int(rs['row'])
    if NOISE_BIN is not None and int(rs['noise_bin']) != NOISE_BIN:
        raise ValueError('resample cache is for a different noise bin')
    n = int(rs['noise_bin'])
    theta = np.load(join(TEST, CELLS[0][0], CELLS[0][1], 'theta_test.npy'))
    truth = theta[row][P]

    fig, axs = plt.subplots(2, 2, figsize=(7.2, 7.2))
    ax1, ax2, ax2d = axs[0, 0], axs[1, 1], axs[1, 0]
    axs[0, 1].axis('off')
    lim = [PRIOR[p] for p in P]
    xs = [np.linspace(*lim[k], 600) for k in range(2)]

    handles = []
    print(f'row {row}, noise {n} (sig_rad={ng[n,0]:.2f}, sig_tran={ng[n,1]:.2f}), '
          f'{int(rs["n_draws"])} draws')
    for s, _, pretty, tag in CELLS:
        c = COLOR[tag]
        d = rs[tag][:, P].astype(float)
        mu, cov = d.mean(axis=0), np.cov(d, rowvar=False)
        sd = np.sqrt(np.diag(cov))
        rho = cov[0, 1] / (sd[0] * sd[1])
        diff = truth - mu
        z = float(np.sqrt(diff @ np.linalg.inv(cov) @ diff))

        for sig, alpha, lw, ls in ((2, ALPHA_95, LW_95, LS_95),
                                   (1, ALPHA_68, LW_68, LS_68)):
            ax2d.add_patch(ellipse(mu, cov, LEVELS[sig], facecolor=to_rgba(c, alpha),
                                   edgecolor='none', zorder=2))
            ax2d.add_patch(ellipse(mu, cov, LEVELS[sig], facecolor='none',
                                   edgecolor=c, lw=lw, ls=ls, zorder=3))
        ax1.plot(xs[0], norm.pdf(xs[0], mu[0], sd[0]), color=c, lw=2.2)
        ax2.plot(xs[1], norm.pdf(xs[1], mu[1], sd[1]), color=c, lw=2.2)

        handles.append(Patch(facecolor=to_rgba(c, ALPHA_68), edgecolor=c, lw=LW_68,
                             label=rf'{pretty}   ($z={z:.1f}$)'))
        print(f'  {s:18s} mean Om {mu[0]:.4f} +/- {sd[0]:.4f}   s8 {mu[1]:.4f} '
              f'+/- {sd[1]:.4f}   rho {rho:+.2f}   Gaussian z {z:.2f}')

    for ax, k in ((ax1, 0), (ax2, 1)):
        ax.axvline(truth[k], color=TRUTH_COLOR, lw=1.6, zorder=4)
        ax.set_xlim(*lim[k])
        ax.set_ylim(0, None)
        ax.set_yticks([])
        ax.grid(False)
    ax2d.axvline(truth[0], color=TRUTH_COLOR, lw=1.6, zorder=4)
    ax2d.axhline(truth[1], color=TRUTH_COLOR, lw=1.6, zorder=4)
    ax2d.plot(*truth, 's', color=TRUTH_COLOR, ms=6, zorder=5)
    ax2d.set_xlim(*lim[0])
    ax2d.set_ylim(*lim[1])
    ax2d.grid(False)

    ticks_om, ticks_s8 = [0.1, 0.2, 0.3, 0.4, 0.5], [0.6, 0.7, 0.8, 0.9, 1.0]
    for ax in (ax1, ax2d):
        ax.set_xticks(ticks_om)
    ax2d.set_yticks(ticks_s8)
    ax2.set_xticks(ticks_s8[1:])      # drop 0.6: it collides with the 0.5 beside it
    ax1.set_xticklabels([])
    ax2d.set_xlabel(label('Omega_m'), fontsize=18)
    ax2d.set_ylabel(label('sigma8'), fontsize=18)
    ax2.set_xlabel(label('sigma8'), fontsize=18)
    for ax in (ax1, ax2, ax2d):
        ax.tick_params(labelsize=12)
        for lab in ax.get_xticklabels():
            lab.set_rotation(45)
    for lab in ax2d.get_yticklabels():
        lab.set_rotation(45)
    ax1.spines['left'].set_visible(True)

    handles.append(Line2D([], [], color=TRUTH_COLOR, lw=1.6, label='truth'))
    handles.append(Line2D([], [], color='0.4', lw=LW_68, ls=LS_68, label=r'$1\sigma$'))
    handles.append(Line2D([], [], color='0.4', lw=LW_95, ls=LS_95, label=r'$2\sigma$'))
    fig.legend(handles=handles, loc='upper right', bbox_to_anchor=(0.97, 0.95),
               fontsize=13, frameon=False, handlelength=1.6,
               title='Gaussian approximation', title_fontsize=12)
    fig.subplots_adjust(wspace=0.05, hspace=0.05)
    fig.suptitle(r'MTNG lightcone OOD, $k_{\max}^{P}<0.4$' '\n'
                 rf'$\sigma_{{\rm rad}}={ng[n,0]:.2f}$, $\sigma_{{\rm tran}}={ng[n,1]:.2f}$',
                 fontsize=15, y=1.0)
    save(fig, 'fig16_ood_mtng_lightcone_gaussian_ellipses')


if __name__ == '__main__':
    main()
