"""
Figure 9 — full posterior corner plot for one Abacus OOD test point.

All 17 inferred parameters (5 cosmology, 10 HOD, 2 positional-noise widths) for
a single test point, with that point's true values marked in every 1D and 2D
panel.

The example is a LCDM, Mnu=0 Abacus simulation at the least-biased noise
configuration (sigma_rad = 0.75, sigma_tran = 2.26). Among that group it is the
one whose joint (Omega_m, sigma_8) error is the median, so it is representative
of the class rather than the best or worst case.

Unlike the other figures this reads the full posterior array directly (via
mmap, one test point's column), since the cache stores only percentiles.

    python fig9_ood_abacus_corner.py
"""

import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import corner
import numpy as np
from os.path import join

from talk_style import apply_style, save, COLORS
import ood_io as O

TAG = 'abacus'
SAMPLES_PATH = (
    '/work/hdd/bdne/maho3/cmass-ili/abacuslike/fastpm_charm7_cosmoHOD/models/'
    'galaxy/zPk0+zPk2+zPk4+zBk0/kmin-0.0_kmax-zBk=0.2__zPk=0.4/testing/'
    'abacus_nbody_comp_gridnoise/posterior_samples.npy')


def pick_point(d, n):
    """Index of the median-error LCDM Mnu=0 test point at noise bin n."""
    sel = (d['noiseidx'] == n) & O.cosm_classes(d['ids'])['simple']
    idx = np.flatnonzero(sel)
    th, med = d['theta'], d['percs'][0]
    # error in each parameter scaled by that parameter's posterior width, so
    # Omega_m and sigma_8 contribute comparably
    err = 0.0
    for p in (O.OM, O.S8):
        width = d['percs'][2][idx, p] - d['percs'][1][idx, p]
        err = err + ((med[idx, p] - th[idx, p]) / width) ** 2
    order = np.argsort(np.sqrt(err))
    return idx[order[len(order) // 2]]


def main():
    apply_style()
    d = O.load(TAG)
    ng = O.noises()
    n = O.GOOD_NOISE[TAG]
    names = [str(v) for v in d['names']]

    i = pick_point(d, n)
    truth = d['theta'][i]
    print(f'{TAG} corner: test index {i}  lhid/sim id {d["ids"][i]}  '
          f'noise {n} (sig_rad={ng[n,0]:.2f}, sig_tran={ng[n,1]:.2f})')

    samples = np.asarray(np.load(SAMPLES_PATH, mmap_mode='r')[:, i, :])
    print(f'  posterior samples {samples.shape}')
    for p in (O.OM, O.S8):
        q = np.percentile(samples[:, p], [16, 50, 84])
        print(f'  {names[p]:8s} true {truth[p]:.4f}  '
              f'post {q[1]:.4f} -{q[1]-q[0]:.4f} +{q[2]-q[1]:.4f}')

    labels = [O.label(v) for v in names]
    fig = corner.corner(
        samples, labels=labels, truths=truth,
        range=O.corner_range(samples, truth),
        truth_color=COLORS['accent'],
        color=COLORS['primary'],
        show_titles=False,
        plot_datapoints=False, fill_contours=True,
        levels=(0.68, 0.95), bins=30,
        smooth=1.0, smooth1d=1.0, max_n_ticks=3,
        hist_kwargs={'lw': 1.4},
        contour_kwargs={'linewidths': 0.9},
        label_kwargs={'fontsize': 15},
    )
    fig.set_size_inches(17, 17)
    for ax in fig.get_axes():
        ax.tick_params(labelsize=9, pad=1.5)
        ax.grid(False)
        # corner sets labels tight against the ticks; push them clear so the
        # parameter name does not sit on top of the tick numbers
        ax.xaxis.labelpad = 12
        ax.yaxis.labelpad = 26
        for lab in ax.get_xticklabels():
            lab.set_rotation(45)
            lab.set_ha('right')
        for lab in ax.get_yticklabels():
            lab.set_rotation(45)

    fig.suptitle(
        'Abacus OOD posterior, one test point '
        rf'(LCDM $M_\nu=0$, sim {d["ids"][i]})' '\n'
        r'$zP_{0,2,4}+B_0$, $k_{\max}^{P}<0.4$   ·   '
        rf'$\sigma_{{\rm rad}}={ng[n,0]:.2f}$, $\sigma_{{\rm tran}}={ng[n,1]:.2f}$'
        '   ·   red = truth',
        fontsize=22, y=0.98)
    # 17x17 panels at 300 dpi would be a ~26 Mpx file; 150 is ample for a slide
    save(fig, 'fig9_ood_abacus_corner', dpi=150)


if __name__ == '__main__':
    main()
