"""
Figure 10 — Omega_m / sigma_8 corner for the same Abacus OOD test point as
figure 9, with the truth marked in every panel.

Same test point, same posterior, same styling as the full 17-parameter corner;
only the parameter set is reduced, so the two figures can be shown together
(full corner for completeness, this one for the slide that needs to be read).

    python fig10_ood_abacus_corner_Om_s8.py
"""

import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import corner
import numpy as np

from talk_style import apply_style, save, COLORS
import ood_io as O
from fig9_ood_abacus_corner import SAMPLES_PATH, pick_point

TAG = 'abacus'
PARAMS = [O.OM, O.S8]


def main():
    apply_style()
    d = O.load(TAG)
    ng = O.noises()
    n = O.GOOD_NOISE[TAG]
    names = [str(v) for v in d['names']]

    i = pick_point(d, n)          # identical selection rule to figure 9
    truth = d['theta'][i][PARAMS]
    samples = np.asarray(np.load(SAMPLES_PATH, mmap_mode='r')[:, i, :])[:, PARAMS]
    print(f'{TAG} corner (Om, s8): test index {i}  sim {d["ids"][i]}  '
          f'noise {n} (sig_rad={ng[n,0]:.2f}, sig_tran={ng[n,1]:.2f})')
    for k, p in enumerate(PARAMS):
        q = np.percentile(samples[:, k], [16, 50, 84])
        print(f'  {names[p]:8s} true {truth[k]:.4f}  '
              f'post {q[1]:.4f} -{q[1]-q[0]:.4f} +{q[2]-q[1]:.4f}')

    fig = corner.corner(
        samples, labels=[O.label(names[p]) for p in PARAMS], truths=truth,
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

    # show_titles puts a title on the top-left panel, so the suptitle has to
    # clear it rather than sit at the usual y
    fig.suptitle(rf'Abacus OOD posterior, sim {d["ids"][i]} '
                 r'($\Lambda$CDM $M_\nu=0$)   ·   red = truth',
                 fontsize=15, y=1.07)
    save(fig, 'fig10_ood_abacus_corner_Om_s8')


if __name__ == '__main__':
    main()
