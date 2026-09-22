"""
Cache fiducial posterior stdevs for the self-consistent model trees.

Reproduces `fiducial_stdev` from ltu-gobig-notes/scripts/model_scaling_diagnostics.py
(median posterior stdev over test points near the fiducial cosmology) but reads
posterior_samples.npy via mmap and pulls only the fiducial columns, so the whole
sweep costs ~10 MB of I/O per model instead of ~500 MB.

Writes one JSON per (nbody, sim) to ../cache/.

    python build_cache.py abacuslike/fastpm_charm7_cosmoHOD quijotelike/fastpm_charm7_cosmoHOD
"""

import json
import os
import sys
import numpy as np
from os.path import join, exists, dirname, abspath

sys.path.insert(0, '/u/maho3/git/ltu-gobig-notes/scripts')
from kcut_utils import discover_summaries, discover_kcuts, pk_kmax, resolve_kmax  # noqa: E402

WDIR = '/work/hdd/bdne/maho3/cmass-ili'
TRACER = 'galaxy'
CACHEDIR = join(dirname(dirname(abspath(__file__))), 'cache')

# Fiducial selection — identical to model_scaling_diagnostics.py
THETAFID = np.array([0.3, 0.5, 0.7, 1.0, 0.8])
PARAM_IDXS = [0, 4]
NBAR_LO, NBAR_HI = np.log10(1.0e-4), np.log10(5.0e-4)
RTOL = 0.1


def fiducial_stdev(mdir):
    """(stdev[n_fid, n_param], n_fid) near fiducial cosmology, or None."""
    sp = join(mdir, 'posterior_samples.npy')
    if not exists(sp):
        return None
    theta = np.load(join(mdir, 'theta_test.npy'))
    nbar_path = join(mdir, 'nbar_test.npy')
    if exists(nbar_path):
        nbar = np.load(nbar_path)
    else:
        nbar = np.load(join(mdir, 'x_test.npy'), mmap_mode='r')[:, -1]
    nbar = np.asarray(nbar)
    if nbar.ndim > 1:
        nbar = nbar.mean(axis=1)

    mask = np.all(np.isclose(theta[:, PARAM_IDXS], THETAFID[PARAM_IDXS],
                             rtol=RTOL), axis=1)
    mask &= (nbar > NBAR_LO) & (nbar < NBAR_HI)
    if not mask.any():
        return None

    idx = np.flatnonzero(mask)
    samples = np.load(sp, mmap_mode='r')          # (n_draw, n_test, n_param)
    sub = np.asarray(samples[:, idx, :])          # only the fiducial columns
    return np.std(sub, axis=0), len(idx)


def percentiles(stdev, p):
    """median and 16/84 spread across fiducial test points, for param index p."""
    q = np.percentile(stdev[:, p], [50, 16, 84])
    return dict(med=q[0], lo=q[1], hi=q[2])


def build(nbody, sim):
    root = join(WDIR, nbody, sim, 'models', TRACER)
    out = {'nbody': nbody, 'sim': sim, 'tracer': TRACER, 'entries': []}
    for s in discover_summaries(root):
        sdir = join(root, s)
        for dname, kmin, kmax in discover_kcuts(sdir):
            mdir = join(sdir, dname)
            res = fiducial_stdev(mdir)
            if res is None:
                print(f'  SKIP (no posteriors) {s} {dname}')
                continue
            stdev, nfid = res
            xlen = int(np.load(join(mdir, 'x_test.npy'), mmap_mode='r').shape[-1])
            entry = {
                'summary': s, 'kcut': dname, 'kmin': kmin,
                'kmax': kmax if isinstance(kmax, dict) else float(kmax),
                'pk_kmax': float(pk_kmax(kmax)),
                'bk_kmax': (float(resolve_kmax(kmax, 'zBk0'))
                            if any('Bk' in p for p in s.split('+')) else None),
                'n_fid': int(nfid), 'x_len': xlen,
                'params': {str(p): percentiles(stdev, p) for p in PARAM_IDXS},
            }
            out['entries'].append(entry)
            print(f'  {s:26s} {dname:34s} n_fid={nfid:3d} xlen={xlen:4d} '
                  f"dOm={entry['params']['0']['med']:.4f} "
                  f"ds8={entry['params']['4']['med']:.4f}", flush=True)
    os.makedirs(CACHEDIR, exist_ok=True)
    path = join(CACHEDIR, f'{nbody}__{sim}.json')
    with open(path, 'w') as f:
        json.dump(out, f, indent=1)
    print(f'wrote {path}  ({len(out["entries"])} entries)')


if __name__ == '__main__':
    for spec in sys.argv[1:]:
        nbody, sim = spec.split('/')
        print(f'=== {nbody}/{sim}', flush=True)
        build(nbody, sim)
