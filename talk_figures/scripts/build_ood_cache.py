"""
Cache the OOD test-set posterior summaries needed by the OOD talk figures.

The raw posterior_samples.npy files are 1-1.5 GB each, so this reads each one
once and stores only what the plots need:

  theta, ids, noiseidx        the test set
  percs (3, n_test, n_param)  posterior median and 16/84 percentiles
  ranks (n_test, n_param)     PIT rank of the truth, for marginal coverage

The self-consistent (in-distribution) posteriors from the training suite are
cached the same way, as the reference curve for coverage plots.

    python build_ood_cache.py
"""

import numpy as np
import os
from os.path import join, exists, dirname, abspath

WDIR = '/work/hdd/bdne/maho3/cmass-ili'
CACHEDIR = join(dirname(dirname(abspath(__file__))), 'cache')

SUMMARY = 'zPk0+zPk2+zPk4+zBk0'
KCUT = 'kmin-0.0_kmax-zBk=0.2__zPk=0.4'   # zPk<0.4, zBk<0.2

# theta column names, in the order preprocess.py writes them:
# 5 cosmology, then the HOD block in hodprior.csv order, then the 2 noise widths
COSMO = ['Omega_m', 'Omega_b', 'h', 'n_s', 'sigma8']
HOD = ['alpha', 'conc_gal_bias_satellites', 'eta_vb_centrals',
       'eta_vb_satellites', 'logM0', 'logM1', 'logMmin',
       'assembias_cen', 'assembias_sat', 'sigma_logM']
NOISE = ['sig_rad', 'sig_tran']

CASES = {
    'quijote': dict(
        base=f'{WDIR}/quijotelike/fastpm_charm7_cosmo/models/galaxy',
        test=f'{WDIR}/quijote/nbody_mixk_gridnoise/models/galaxy',
        sim='quijote_nbody_mixk_gridnoise',
        names=COSMO + NOISE),
    'abacus': dict(
        base=f'{WDIR}/abacuslike/fastpm_charm7_cosmoHOD/models/galaxy',
        test=f'{WDIR}/abacus/nbody_comp_gridnoise/models/galaxy',
        sim='abacus_nbody_comp_gridnoise',
        names=COSMO + HOD + NOISE),
}


def summarise(samples, theta):
    """Posterior median / 16 / 84 percentiles, and the PIT rank of the truth."""
    percs = np.percentile(samples, [50, 16, 84], axis=0).astype(np.float32)
    ranks = (samples < theta[None, :, :]).mean(axis=0).astype(np.float32)
    return percs, ranks


def build(tag, case):
    out = {'names': np.array(case['names']), 'summary': SUMMARY, 'kcut': KCUT}

    # ── OOD side ──────────────────────────────────────────────────────────
    tl = join(case['test'], SUMMARY, KCUT)
    theta = np.load(join(tl, 'theta_test.npy'))
    ids = np.load(join(tl, 'ids_test.npy'))
    nid = join(tl, 'noiseid_test.npy')
    if not exists(nid):
        nid = join(tl, 'noiseids_test.npy')
    noiseidx = np.load(nid)[:, 0]

    sp = join(case['base'], SUMMARY, KCUT, 'testing', case['sim'],
              'posterior_samples.npy')
    print(f'  reading {sp}', flush=True)
    samples = np.load(sp)
    if not (len(ids) == len(noiseidx) == samples.shape[1] == len(theta)):
        raise ValueError(f'{tag}: inconsistent test-set sizes')
    percs, ranks = summarise(samples, theta)
    del samples
    out.update(theta=theta, ids=ids, noiseidx=noiseidx,
               percs=percs, ranks=ranks)
    print(f'  OOD  n_test={len(theta)} n_param={theta.shape[1]} '
          f'n_noise={noiseidx.max() + 1}', flush=True)

    # ── self-consistent side (coverage reference) ─────────────────────────
    ml = join(case['base'], SUMMARY, KCUT)
    theta_self = np.load(join(ml, 'theta_test.npy'))
    print(f'  reading {join(ml, "posterior_samples.npy")}', flush=True)
    samples_self = np.load(join(ml, 'posterior_samples.npy'))
    percs_self, ranks_self = summarise(samples_self, theta_self)
    del samples_self
    out.update(theta_self=theta_self, percs_self=percs_self,
               ranks_self=ranks_self)
    print(f'  self n_test={len(theta_self)}', flush=True)

    os.makedirs(CACHEDIR, exist_ok=True)
    path = join(CACHEDIR, f'ood_{tag}.npz')
    np.savez_compressed(path, **out)
    print(f'  wrote {path} ({os.path.getsize(path) / 1e6:.1f} MB)', flush=True)


if __name__ == '__main__':
    for tag, case in CASES.items():
        print(f'=== {tag}', flush=True)
        build(tag, case)
