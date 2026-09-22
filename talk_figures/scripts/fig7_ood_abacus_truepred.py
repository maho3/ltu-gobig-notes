"""
Figure 7 — OOD true vs predicted Omega_m and sigma_8 on the Abacus test set,
split by cosmology class.

Train: abacuslike/fastpm_charm7_cosmoHOD (cosmology + HOD inference).
Test: abacus/nbody_comp_gridnoise. Summary zPk024+zBk0 at zPk<0.4, zBk<0.2.

Abacus test points are not drawn from the training prior, and not all are LCDM
with massless neutrinos, so they are split into three disjoint classes and
coloured accordingly. Shown at the least-biased noise configuration in the grid
(ood_io.pick_noise): sigma_rad = 0.75, sigma_tran = 2.26.

Many Abacus phases share the same cosmology, so a small horizontal jitter is
applied to separate points that would otherwise stack exactly.

    python fig7_ood_abacus_truepred.py
"""

import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import numpy as np

from talk_style import apply_style, save, COLORS, COSM
import ood_io as O

TAG = 'abacus'
PARAMS = [O.OM, O.S8]
JITTER = {O.OM: 0.0016, O.S8: 0.0024}
ORDER = ['simple', 'mnu', 'non_lcdm']
SEED = 7


def main():
    apply_style()
    d = O.load(TAG)
    ng = O.noises()
    n = O.GOOD_NOISE[TAG]
    names = [str(v) for v in d['names']]

    sel = d['noiseidx'] == n
    masks = {k: v & sel for k, v in O.cosm_classes(d['ids']).items()}
    th, med = d['theta'], d['percs'][0]
    lo, hi = d['percs'][0] - d['percs'][1], d['percs'][2] - d['percs'][0]
    rng = np.random.default_rng(SEED)

    # square panels, so the figure is sized wide enough to hold two of them
    # side by side without tight_layout squeezing them
    fig, axs = plt.subplots(1, 2, figsize=(10.5, 6.0))

    print(f'{TAG} OOD  noise {n}: sig_rad={ng[n,0]:.2f} sig_tran={ng[n,1]:.2f}')
    for j, p in enumerate(PARAMS):
        ax = axs[j]
        for key in ORDER:
            m = masks[key]
            if not m.any():
                continue
            color, marker, lab = COSM[key]
            x = th[m, p] + rng.uniform(-JITTER[p], JITTER[p], m.sum())
            ax.errorbar(x, med[m, p], yerr=[lo[m, p], hi[m, p]],
                        fmt=marker, ms=5, lw=0.8, elinewidth=0.9, alpha=0.75,
                        color=color, label=f'{lab}  ({m.sum()})', zorder=3)
            resid = med[m, p] - th[m, p]
            print(f'  {names[p]:7s} {key:9s} n={m.sum():3d}  '
                  f'median resid {np.median(resid):+.4f}  rms {np.std(resid):.4f}')

        span = [th[sel, p].min(), th[sel, p].max()]
        pad = 0.06 * (span[1] - span[0])
        ref = [span[0] - pad, span[1] + pad]
        ax.plot(ref, ref, ls='--', color=COLORS['ideal'], lw=1.8, zorder=1)
        ax.set_xlim(*ref)
        ax.set_ylim(*ref)
        # identical x and y ranges, so an equal aspect makes each panel square
        # and puts the 1:1 line at 45 degrees
        ax.set_aspect('equal', adjustable='box')
        ax.set_xlabel(f'true {O.label(names[p])}')
        ax.set_ylabel(f'predicted {O.label(names[p])}')

    axs[0].legend(loc='upper left', fontsize=10, labelspacing=0.3,
                  handletextpad=0.4, borderpad=0.3)

    fig.suptitle('OOD recovery on Abacus, by cosmology class  '
                 rf'($\sigma_{{\rm rad}}={ng[n,0]:.2f}$, '
                 rf'$\sigma_{{\rm tran}}={ng[n,1]:.2f}$)', y=1.0)
    fig.tight_layout()
    save(fig, 'fig7_ood_abacus_true_vs_pred')


if __name__ == '__main__':
    main()
