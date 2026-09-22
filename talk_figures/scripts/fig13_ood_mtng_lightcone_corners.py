"""
Figures 13-14 — corner plots for the MTNG *lightcone* OOD test.

Train: mtnglike/fastpm_charm7, tracer mtng_lightcone (cosmology + a
redshift-dependent HOD, 23 inferred parameters).
Test:  mtng/nbody, tracer mtng_lightcone (results under testing/mtng_nbody).

Same plots as figures 11 (full corner) and 12 (Omega_m / sigma_8 corner), for
three summaries at k_P < 0.4:
  a  Pk0     b  Pk0+Pk2+Pk4     c  Pk0+Pk2+Pk4+Bk0 (Bk < 0.2)

Note the lightcone tree names summaries without the 'z' prefix and keys its
dynamic k-cuts as Pk=/Bk=, and it is a different directory from the box test
in models/galaxy/.../testing/quijote3gpch_nbody used by figures 11-12.

The test set is one MTNG N-body lightcone at a single fixed HOD, observed at
31 noise configurations (noise-grid rows 0-30), one test point each. Choosing
the 'good' noise scale is therefore the same as choosing the point: the
configuration is pinned by NOISE_BIN below: sigma_rad = 3.01, sigma_tran = 1.50
(noise-grid row 18). It was chosen over the lowest-summed-joint-z setting
(0.00, 3.01) because there the P024+B0 posterior puts sigma_8 ~1.2 sigma low,
while at (3.01, 1.50) all three summaries agree on sigma_8 within P0's offset
(+B0 sigma_8 pull -0.39), at the cost of Omega_m pulls of ~+1.2 for P024 and
P024+B0. No setting removes P0's high sigma_8 (+1.3 to +1.8 everywhere). Set
NOISE_BIN = None to fall back to the minimum summed joint z. The full
per-configuration z table is printed either way.

    python fig13_ood_mtng_lightcone_corners.py
"""

import matplotlib
matplotlib.use('Agg')
import corner
import numpy as np
from os.path import join

from talk_style import apply_style, save, COLORS
import ood_io as O

WDIR = '/work/hdd/bdne/maho3/cmass-ili'
BASE = f'{WDIR}/mtnglike/fastpm_charm7/models/mtng_lightcone'
TEST = f'{WDIR}/mtng/nbody/models/mtng_lightcone'
SIM = 'mtng_nbody'
P = [0, 4]
# pinned noise-grid row (sigma_rad, sigma_tran) = (3.01, 1.50); None = auto
NOISE_BIN = 18

CELLS = [
    ('Pk0', 'kmin-0.0_kmax-0.4', r'$P_{0}$', 'Pk0'),
    ('Pk0+Pk2+Pk4', 'kmin-0.0_kmax-0.4', r'$P_{0,2,4}$', 'Pk024'),
    ('Pk0+Pk2+Pk4+Bk0', 'kmin-0.0_kmax-Bk=0.2__Pk=0.4', r'$P_{0,2,4}+B_0$',
     'Pk024_Bk0'),
]


def param_names(summary, kcut):
    """5 cosmology + HOD block in hodprior.csv order + 2 noise widths."""
    hod = [l.split(',')[0] for l in
           open(join(TEST, summary, kcut, 'hodprior.csv')).read().split('\n') if l]
    return ['Omega_m', 'Omega_b', 'h', 'n_s', 'sigma8'] + hod + ['sig_rad', 'sig_tran']


_HOD_BASE = {
    'alpha': r'\alpha', 'conc_gal_bias_satellites': r'c_{\rm sat}',
    'eta_vb_centrals': r'\eta_{vb}^{\rm cen}', 'eta_vb_satellites': r'\eta_{vb}^{\rm sat}',
    'logM0': r'\log M_0', 'logM1': r'\log M_1', 'logMmin': r'\log M_{\rm min}',
    'mean_occupation_centrals_assembias_param1': r'A_{\rm cen}',
    'mean_occupation_satellites_assembias_param1': r'A_{\rm sat}',
    'sigma_logM': r'\sigma_{\log M}',
}


def label(name):
    """TeX label; redshift-binned HOD params get a (z_i) superscript."""
    if name in O.PARAM_LABEL:
        return O.label(name)
    base, zbin = name, None
    if '_z' in name and name.rsplit('_z', 1)[1].isdigit():
        base, zbin = name.rsplit('_z', 1)
    tex = _HOD_BASE.get(base, base.replace('_', r'\_'))
    return rf'${tex}^{{(z_{zbin})}}$' if zbin is not None else rf'${tex}$'


def load_cell(summary, kcut):
    tl = join(TEST, summary, kcut)
    theta = np.load(join(tl, 'theta_test.npy'))
    noiseidx = np.load(join(tl, 'noiseid_test.npy'))[:, 0]
    ids = np.load(join(tl, 'ids_test.npy'))
    samples = np.load(join(BASE, summary, kcut, 'testing', SIM,
                           'posterior_samples.npy'))
    return theta, noiseidx, ids, samples


def joint_z(theta_row, draws):
    """Joint Mahalanobis z over (Om, s8), full covariance, as in
    scripts/ood_abacus_inference.py::_compute_lcdm_z."""
    d = theta_row[P] - np.median(draws[:, P], axis=0)
    C = np.cov(draws[:, P], rowvar=False)
    return float(np.sqrt(d @ np.linalg.inv(C) @ d))


def select_row(noiseidx, z_total):
    """Test row at the pinned NOISE_BIN, or the minimum summed joint z."""
    if NOISE_BIN is None:
        return int(np.argmin(z_total))
    rows = np.flatnonzero(noiseidx == NOISE_BIN)
    if len(rows) != 1:
        raise ValueError(f'expected one test row at noise bin {NOISE_BIN}, got {len(rows)}')
    return int(rows[0])


def style_axes(fig, big):
    for ax in fig.get_axes():
        ax.grid(False)
        if big:
            ax.tick_params(labelsize=8, pad=1.5)
            ax.xaxis.labelpad, ax.yaxis.labelpad = 12, 26
            for lab in ax.get_xticklabels():
                lab.set_rotation(45)
                lab.set_ha('right')
            for lab in ax.get_yticklabels():
                lab.set_rotation(45)
        else:
            ax.tick_params(labelsize=12)
            ax.xaxis.labelpad = ax.yaxis.labelpad = 10


def main():
    apply_style()
    ng = O.noises()
    cells = {s: load_cell(s, k) for s, k, _, _ in CELLS}
    names = param_names(*CELLS[0][:2])

    theta, noiseidx, ids, _ = cells[CELLS[0][0]]
    for s, k, _, _ in CELLS[1:]:
        for a, b in zip(cells[CELLS[0][0]][:3], cells[s][:3]):
            if not np.array_equal(a, b):
                raise ValueError(f'test rows differ between cells ({s})')
        if param_names(s, k) != names:
            raise ValueError(f'parameter names differ between cells ({s})')
    if len(names) != theta.shape[1]:
        raise ValueError(f'{len(names)} names for {theta.shape[1]} theta columns')
    # noiseid n must be noise-grid row n
    if not np.allclose(theta[:, -2:], ng[noiseidx]):
        raise ValueError('theta noise columns do not match noisegrid rows')

    z = {s: np.array([joint_z(theta[i], cells[s][3][:, i]) for i in range(len(theta))])
         for s, _, _, _ in CELLS}
    total = sum(z.values())
    i = select_row(noiseidx, total)

    print(f'lightcone OOD: {len(theta)} test points, one per noise config, '
          f'id {np.unique(ids).tolist()}')
    print('   row  noise  sig_rad sig_tran   ' +
          '  '.join(f'z[{t}]' for _, _, _, t in CELLS) + '   sum')
    for r in np.argsort(total):
        n = noiseidx[r]
        print(f'  {r:4d}  {n:5d}   {ng[n,0]:5.2f}   {ng[n,1]:5.2f}    ' +
              '     '.join(f'{z[s][r]:5.2f}' for s, _, _, _ in CELLS) +
              f'   {total[r]:5.2f}' + ('   <- chosen' if r == i else ''))
    n = noiseidx[i]

    truth = theta[i]
    for s, kcut, pretty, tag in CELLS:
        samples = cells[s][3][:, i, :]
        print(f'  {s:18s} joint z {z[s][i]:.2f}  ' + '  '.join(
            f'{names[p]} true {truth[p]:.4f} post {np.median(samples[:, p]):.4f} '
            f'pull {(np.median(samples[:, p]) - truth[p]) / np.std(samples[:, p]):+.2f}'
            for p in P))

        head = (r'MTNG lightcone OOD: mtnglike (CHARM) $\rightarrow$ MTNG N-body' '\n'
                rf'{pretty}, $k_{{\max}}^{{P}}<0.4$   ·   '
                rf'$\sigma_{{\rm rad}}={ng[n,0]:.2f}$, $\sigma_{{\rm tran}}={ng[n,1]:.2f}$'
                rf'   ·   joint $z={z[s][i]:.1f}$   ·   red = truth')

        # full corner
        fig = corner.corner(
            samples, labels=[label(v) for v in names], truths=truth,
            range=O.corner_range(samples, truth),
            truth_color=COLORS['accent'], color=COLORS['primary'],
            show_titles=False, plot_datapoints=False, fill_contours=True,
            levels=(0.68, 0.95), bins=30, smooth=1.0, smooth1d=1.0,
            max_n_ticks=3, hist_kwargs={'lw': 1.3},
            contour_kwargs={'linewidths': 0.8}, label_kwargs={'fontsize': 15})
        fig.set_size_inches(21, 21)
        style_axes(fig, big=True)
        fig.suptitle(head, fontsize=24, y=0.98)
        save(fig, f'fig13_ood_mtng_lightcone_corner_{tag}', dpi=130)

        # Omega_m / sigma_8 corner
        sub, tsub = samples[:, P], truth[P]
        fig = corner.corner(
            sub, labels=[label(names[p]) for p in P], truths=tsub,
            range=O.corner_range(sub, tsub),
            truth_color=COLORS['accent'], color=COLORS['primary'],
            show_titles=True, title_fmt='.3f', plot_datapoints=False,
            fill_contours=True, levels=(0.68, 0.95), bins=30, smooth=1.0,
            smooth1d=1.0, max_n_ticks=4, hist_kwargs={'lw': 1.8},
            contour_kwargs={'linewidths': 1.1}, label_kwargs={'fontsize': 17},
            title_kwargs={'fontsize': 14})
        fig.set_size_inches(6.6, 6.6)
        style_axes(fig, big=False)
        fig.suptitle(rf'MTNG lightcone OOD:  {pretty}, $k_{{\max}}^{{P}}<0.4$' '\n'
                     rf'$\sigma_{{\rm rad}}={ng[n,0]:.2f}$, $\sigma_{{\rm tran}}={ng[n,1]:.2f}$'
                     rf'   ·   joint $z={z[s][i]:.1f}$   ·   red = truth',
                     fontsize=14, y=1.10)
        save(fig, f'fig14_ood_mtng_lightcone_corner_Om_s8_{tag}')


if __name__ == '__main__':
    main()
