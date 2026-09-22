"""
Figure 4 — OOD true vs predicted for all five cosmology parameters.

Train: quijotelike/fastpm_charm7_cosmo (CHARM-based emulation, cosmology-only
inference). Test: quijote/nbody_mixk_gridnoise. Summary zPk024+zBk0 at
zPk<0.4, zBk<0.2.

Shown at one noise configuration, the least biased in the grid (see
ood_io.pick_noise): sigma_rad = 4.51, sigma_tran = 2.26. Restricting to a
single noise bin leaves ~207 test points, few enough to plot individually with
68% posterior intervals, so no subsampling is needed.

    python fig4_ood_quijote_truepred.py
"""

import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import numpy as np

from talk_style import apply_style, save, COLORS
import ood_io as O

TAG = 'quijote'
MAXPTS = 250        # subsample only if a noise bin is unexpectedly large
SEED = 42


def main():
    apply_style()
    d = O.load(TAG)
    ng = O.noises()
    n = O.GOOD_NOISE[TAG]
    names = [str(v) for v in d['names']]

    sel = np.flatnonzero(d['noiseidx'] == n)
    if len(sel) > MAXPTS:
        sel = np.random.default_rng(SEED).choice(sel, MAXPTS, replace=False)
    th, pc = d['theta'][sel], d['percs'][:, sel]

    fig, axs = plt.subplots(2, 3, figsize=(11.0, 7.0))
    axs = axs.ravel()

    print(f'{TAG} OOD  noise {n}: sig_rad={ng[n,0]:.2f} sig_tran={ng[n,1]:.2f}'
          f'  n_points={len(sel)}')
    for k, p in enumerate(O.COSMO_IDX):
        ax = axs[k]
        lo = pc[0, :, p] - pc[1, :, p]
        hi = pc[2, :, p] - pc[0, :, p]
        ax.errorbar(th[:, p], pc[0, :, p], yerr=[lo, hi], fmt='o', ms=3.5,
                    lw=0.8, elinewidth=0.8, alpha=0.55,
                    color=COLORS['primary'], zorder=2)

        span = [th[:, p].min(), th[:, p].max()]
        pad = 0.04 * (span[1] - span[0])
        ref = [span[0] - pad, span[1] + pad]
        ax.plot(ref, ref, ls='--', color=COLORS['ideal'], lw=1.8, zorder=3)
        ax.set_xlim(*ref)
        ax.set_ylim(*ref)

        ax.set_xlabel(f'true {O.label(names[p])}')
        ax.set_ylabel(f'predicted {O.label(names[p])}')

        resid = pc[0, :, p] - th[:, p]
        cov = (th[:, p] < pc[0, :, p]).mean()
        print(f'  {names[p]:8s} median resid {np.median(resid):+.4f}  '
              f'rms {np.std(resid):.4f}  median coverage {cov:.3f}')

    # last cell carries the run description instead of a sixth panel
    axs[-1].axis('off')
    axs[-1].text(
        0.0, 0.72,
        'train  quijotelike / CHARM\n'
        'test   quijote N-body\n\n'
        r'$zP_{0,2,4}+B_0$' '\n'
        r'$k_{\max}^{P}<0.4$, $k_{\max}^{B}<0.2$' '\n\n'
        rf'$\sigma_{{\rm rad}}={ng[n,0]:.2f}$, $\sigma_{{\rm tran}}={ng[n,1]:.2f}$'
        '\n' rf'{len(sel)} test points',
        transform=axs[-1].transAxes, ha='left', va='top', fontsize=13,
        color='0.3', linespacing=1.5)

    fig.suptitle('out-of-distribution recovery of the cosmology parameters',
                 y=1.005)
    fig.tight_layout()
    save(fig, 'fig4_ood_quijote_true_vs_pred')


if __name__ == '__main__':
    main()
