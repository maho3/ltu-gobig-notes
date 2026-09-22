"""
Figure 5 — marginal (PIT) coverage of Omega_m and sigma_8 for the OOD test.

Train quijotelike/fastpm_charm7_cosmo, test quijote/nbody_mixk_gridnoise,
summary zPk024+zBk0 at zPk<0.4, zBk<0.2.

The OOD curve is taken at the least-biased noise configuration (the same one
figure 4 uses). The self-consistent curve is the in-distribution test set of
the training suite, which spans the whole noise prior rather than one bin, so
it is a reference for the achievable calibration of this estimator, not a
noise-matched control.

Diagonal = perfectly calibrated. Below the diagonal = the truth falls too high
in the posterior, i.e. the estimator under-predicts; above = over-predicts.
Bands are binomial errors on the coverage estimate.

    python fig5_ood_quijote_coverage.py
"""

import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import numpy as np

from talk_style import apply_style, save, COLORS
import ood_io as O

TAG = 'quijote'
PARAMS = [O.OM, O.S8]


def main():
    apply_style()
    d = O.load(TAG)
    ng = O.noises()
    n = O.GOOD_NOISE[TAG]
    names = [str(v) for v in d['names']]
    sel = d['noiseidx'] == n

    # square panels (the diagonal must read as 45 deg), so the figure is
    # sized to them: same 7in width as figs 1-2, just shorter
    fig, axs = plt.subplots(1, 2, figsize=(7.0, 4.3))

    print(f'{TAG} coverage  noise {n}: sig_rad={ng[n,0]:.2f} '
          f'sig_tran={ng[n,1]:.2f}  n_ood={sel.sum()} '
          f'n_self={len(d["ranks_self"])}')
    for j, p in enumerate(PARAMS):
        ax = axs[j]
        ax.plot([0, 1], [0, 1], ls='--', color=COLORS['ideal'], lw=1.8,
                zorder=1)

        x, y, e = O.marginal_coverage(d['ranks'][sel, p])
        ax.plot(x, y, color=COLORS['primary'], zorder=3, label='OOD')
        ax.fill_between(x, y - e, y + e, color=COLORS['primary'], alpha=0.25,
                        lw=0, zorder=2)

        xs, ys, es = O.marginal_coverage(d['ranks_self'][:, p])
        ax.plot(xs, ys, color=COLORS['accent'], lw=1.8, zorder=3,
                label='self-consistent')
        ax.fill_between(xs, ys - es, ys + es, color=COLORS['accent'],
                        alpha=0.2, lw=0, zorder=2)

        ax.set_xlim(0, 1)
        ax.set_ylim(0, 1)
        ax.set_aspect('equal')
        ax.set_xlabel('credibility level')
        ax.set_ylabel('empirical coverage')
        ax.set_title(O.label(names[p]), pad=8)

        dev = np.max(np.abs(y - x))
        print(f'  {names[p]:8s} max |coverage - diagonal| OOD {dev:.3f}  '
              f'self {np.max(np.abs(ys - xs)):.3f}')

    axs[0].legend(loc='upper left', fontsize=11, labelspacing=0.3,
                  handletextpad=0.5)

    axs[1].annotate(rf'$\sigma_{{\rm rad}}={ng[n,0]:.2f}$' '\n'
                    rf'$\sigma_{{\rm tran}}={ng[n,1]:.2f}$',
                    xy=(0.96, 0.04), xycoords='axes fraction',
                    ha='right', va='bottom', fontsize=11, color='0.4')
    fig.suptitle('OOD calibration: quijote N-body', y=1.01)
    fig.tight_layout()
    save(fig, 'fig5_ood_quijote_coverage')


if __name__ == '__main__':
    main()
