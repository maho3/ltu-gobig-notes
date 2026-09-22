"""
Draw a large posterior sample for the chosen MTNG-lightcone test point.

validate.py stores only 2000 draws per test point, which makes 2D contours
wobbly. This reloads each summary's saved ensemble
(testing/mtng_nbody/posterior.pkl, the object validate.py sampled from) and
draws N_DRAWS samples for the one test row the lightcone figures use, then
checks the new draws against the saved 2000 before caching them.

torch is pinned to a few threads: its default of one thread per core (128)
stalls completely on a shared login node.

    python build_lightcone_resample.py
"""

import os
os.environ.setdefault('OMP_NUM_THREADS', '4')
os.environ.setdefault('MKL_NUM_THREADS', '4')

import sys
import time
import warnings
import numpy as np
import torch
from os.path import join, dirname, abspath

torch.set_num_threads(4)
warnings.filterwarnings('ignore')
sys.path.insert(0, '/u/maho3/git/ltu-cmass')
from cmass.infer.tools import load_posterior  # noqa: E402
from fig13_ood_mtng_lightcone_corners import (  # noqa: E402
    CELLS, BASE, TEST, SIM, NOISE_BIN)

N_DRAWS = 100_000
SEED = 0
CACHEDIR = join(dirname(dirname(abspath(__file__))), 'cache')


def main():
    torch.manual_seed(SEED)
    noiseidx = np.load(join(TEST, CELLS[0][0], CELLS[0][1], 'noiseid_test.npy'))[:, 0]
    rows = np.flatnonzero(noiseidx == NOISE_BIN)
    if len(rows) != 1:
        raise ValueError(f'expected one row at noise bin {NOISE_BIN}')
    row = int(rows[0])

    out = {'row': row, 'noise_bin': NOISE_BIN, 'n_draws': N_DRAWS}
    for s, kc, _, tag in CELLS:
        ens = load_posterior(join(BASE, s, kc, 'testing', SIM, 'posterior.pkl'), 'cpu')
        x = torch.Tensor(np.load(join(TEST, s, kc, 'x_test.npy'))[row])
        t = time.time()
        with torch.no_grad():
            draws = ens.sample((N_DRAWS,), x, show_progress_bars=False).cpu().numpy()
        saved = np.load(join(BASE, s, kc, 'testing', SIM, 'posterior_samples.npy'),
                        mmap_mode='r')[:, row, :]
        print(f'{tag:10s} {len(ens.posteriors)} nets  {N_DRAWS} draws in '
              f'{time.time() - t:.0f}s', flush=True)
        for p, n in [(0, 'Om'), (4, 's8')]:
            qs = np.percentile(saved[:, p], [16, 50, 84])
            qn = np.percentile(draws[:, p], [16, 50, 84])
            # the saved 2k median has a sampling error of ~1.25 sigma/sqrt(2000)
            err = 1.25 * np.std(draws[:, p]) / np.sqrt(len(saved))
            flag = 'ok' if abs(qn[1] - qs[1]) < 4 * err else 'MISMATCH'
            print(f'   {n}: saved {qs[1]:.4f} [{qs[0]:.4f},{qs[2]:.4f}]  '
                  f'new {qn[1]:.4f} [{qn[0]:.4f},{qn[2]:.4f}]  '
                  f'median diff {qn[1] - qs[1]:+.4f} ({flag})', flush=True)
            if flag != 'ok':
                raise ValueError(f'{tag}: resampled posterior disagrees with saved samples')
        out[tag] = draws.astype(np.float32)

    os.makedirs(CACHEDIR, exist_ok=True)
    path = join(CACHEDIR, f'lightcone_resample_row{row}.npz')
    np.savez_compressed(path, **out)
    print(f'wrote {path} ({os.path.getsize(path) / 1e6:.1f} MB)')


if __name__ == '__main__':
    main()
