"""
Figure 11 — full posterior corner plots for the 3 Gpc/h OOD test:
train mtnglike/fastpm_charm7 (L=3 Gpc/h, cosmology + HOD inference),
test quijote3gpch/nbody.

One figure per summary, all at k_P < 0.4:
  11a  zPk0
  11b  zPk0+zPk2+zPk4
  11c  zPk0+zPk2+zPk4+zBk0   (zBk < 0.2)

The test set is small: one simulation (lhid 2000, Quijote fiducial cosmology)
x 3 noise configurations x 5 HOD realisations = 15 points. The noise bin is
the one with the lowest mean joint Mahalanobis z over (Om, s8), summed across
both summaries: sigma_rad = sigma_tran = 2.26. Note that no bin is unbiased
here: sigma_8 is under-predicted by ~3 posterior sigma at every noise level,
and the bin choice changes mean z only from ~2.6-3.3 to ~2.6-3.1.

Within that bin, the test point is the one with the median joint z (under the
zPk024+zBk0 posterior), so it is representative rather than best-case. All
three figures use the same test point -- the cells' theta/ids/noiseid arrays
are verified identical -- so they compare the summaries on the same data.

    python fig11_ood_mtng_corner.py
"""

import matplotlib
matplotlib.use('Agg')
import corner
import numpy as np
from os.path import join

from talk_style import apply_style, save, COLORS
import ood_io as O

WDIR = '/work/hdd/bdne/maho3/cmass-ili'
BASE = f'{WDIR}/mtnglike/fastpm_charm7/models/galaxy'
TEST = f'{WDIR}/quijote3gpch/nbody/models/galaxy'
SIM = 'quijote3gpch_nbody'
NOISE_BIN = 24                                  # sigma_rad = sigma_tran = 2.26
SELECT_ON = 'zPk0+zPk2+zPk4+zBk0'
P = [0, 4]

CELLS = [
    ('zPk0', 'kmin-0.0_kmax-0.4',
     r'$zP_{0}$', 'fig11a_ood_mtng_corner_Pk0'),
    ('zPk0+zPk2+zPk4', 'kmin-0.0_kmax-0.4',
     r'$zP_{0,2,4}$', 'fig11b_ood_mtng_corner_Pk024'),
    ('zPk0+zPk2+zPk4+zBk0', 'kmin-0.0_kmax-zBk=0.2__zPk=0.4',
     r'$zP_{0,2,4}+B_0$', 'fig11c_ood_mtng_corner_Pk024_Bk0'),
]
NAMES = (['Omega_m', 'Omega_b', 'h', 'n_s', 'sigma8']
         + ['alpha', 'conc_gal_bias_satellites', 'eta_vb_centrals',
            'eta_vb_satellites', 'logM0', 'logM1', 'logMmin',
            'assembias_cen', 'assembias_sat', 'sigma_logM']
         + ['sig_rad', 'sig_tran'])


def load_cell(summary, kcut):
    tl = join(TEST, summary, kcut)
    theta = np.load(join(tl, 'theta_test.npy'))
    noiseidx = np.load(join(tl, 'noiseid_test.npy'))[:, 0]
    ids = np.load(join(tl, 'ids_test.npy'))
    samples = np.load(join(BASE, summary, kcut, 'testing', SIM,
                           'posterior_samples.npy'))
    return theta, noiseidx, ids, samples


def joint_z(theta_row, draws):
    """Joint Mahalanobis z over (Om, s8) with full covariance, as in
    scripts/ood_abacus_inference.py::_compute_lcdm_z."""
    d = theta_row[P] - np.median(draws[:, P], axis=0)
    C = np.cov(draws[:, P], rowvar=False)
    return float(np.sqrt(d @ np.linalg.inv(C) @ d))


def main():
    apply_style()
    ng = O.noises()
    cells = {s: load_cell(s, k) for s, k, _, _ in CELLS}

    ref = cells[CELLS[0][0]]
    for s, _, _, _ in CELLS[1:]:
        for a, b in zip(ref[:3], cells[s][:3]):
            if not np.array_equal(a, b):
                raise ValueError(f'test rows differ between cells ({s})')

    theta, noiseidx, ids, samp_sel = cells[SELECT_ON]
    rows = np.flatnonzero(noiseidx == NOISE_BIN)
    zs = np.array([joint_z(theta[i], samp_sel[:, i]) for i in rows])
    i = rows[np.argsort(zs)[len(zs) // 2]]
    print(f'noise bin {NOISE_BIN} (sig_rad={ng[NOISE_BIN,0]:.2f}, '
          f'sig_tran={ng[NOISE_BIN,1]:.2f}): rows {rows.tolist()}  '
          f'joint z {np.round(zs, 2).tolist()}  -> test row {i}, lhid {ids[i]}')

    truth = theta[i]
    labels = [O.label(n) for n in NAMES]
    for summary, kcut, pretty, fname in CELLS:
        samples = cells[summary][3][:, i, :]
        z = joint_z(truth, samples)
        print(f'  {summary:24s} joint z = {z:.2f}')
        for p in P:
            q = np.percentile(samples[:, p], [16, 50, 84])
            print(f'    {NAMES[p]:8s} true {truth[p]:.4f}  '
                  f'post {q[1]:.4f} -{q[1]-q[0]:.4f} +{q[2]-q[1]:.4f}  '
                  f'pull {(q[1]-truth[p])/np.std(samples[:, p]):+.2f}')

        fig = corner.corner(
            samples, labels=labels, truths=truth,
            range=O.corner_range(samples, truth),
            truth_color=COLORS['accent'], color=COLORS['primary'],
            show_titles=False, plot_datapoints=False, fill_contours=True,
            levels=(0.68, 0.95), bins=30, smooth=1.0, smooth1d=1.0,
            max_n_ticks=3,
            hist_kwargs={'lw': 1.4},
            contour_kwargs={'linewidths': 0.9},
            label_kwargs={'fontsize': 15},
        )
        fig.set_size_inches(17, 17)
        for ax in fig.get_axes():
            ax.tick_params(labelsize=9, pad=1.5)
            ax.grid(False)
            ax.xaxis.labelpad = 12
            ax.yaxis.labelpad = 26
            for lab in ax.get_xticklabels():
                lab.set_rotation(45)
                lab.set_ha('right')
            for lab in ax.get_yticklabels():
                lab.set_rotation(45)

        fig.suptitle(
            r'3 Gpc/$h$ OOD: mtnglike (CHARM) $\rightarrow$ quijote3gpch N-body, '
            rf'lhid {ids[i]}' '\n'
            rf'{pretty}, $k_{{\max}}^{{P}}<0.4$   ·   '
            rf'$\sigma_{{\rm rad}}={ng[NOISE_BIN,0]:.2f}$, '
            rf'$\sigma_{{\rm tran}}={ng[NOISE_BIN,1]:.2f}$   ·   '
            rf'joint $z={z:.1f}$   ·   red = truth',
            fontsize=22, y=0.98)
        save(fig, fname, dpi=150)


if __name__ == '__main__':
    main()
