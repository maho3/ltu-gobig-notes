"""
Out-of-distribution inference on the quijote3gpch test suite.

An NPE trained on mtnglike/fastpm_charm7 (galaxy tracer, L=3 Gpc/h) is
evaluated on a single Quijote N-body realisation at the fiducial cosmology
(lhid 2000, L=3 Gpc/h). Because the suite holds one cosmology rather than a
prior-sampled population, coverage and calibration statistics are not
meaningful and are not produced; the output products are corner plots against
the known truth. See ood_corner.py for the plotting machinery.

Note on coverage: this test set currently spans only 3 of the 49 noise-grid
configurations, and all three lie on the sigma_rad = sigma_tran diagonal
(0.75, 1.50, 2.26), with 5 HOD realisations each. There is therefore no
sigma_rad vs sigma_tran contrast available. The noise-selection logic is
general, so this script picks up the rest automatically if they are generated.

Usage:
    python scripts/ood_quijote3gpch_inference.py [--basedir ...] [--testdir ...]
                                                 [--noises-path ...] [--outdir ...]
"""

import argparse
import os
import sys
from os.path import join, dirname, abspath

sys.path.insert(0, dirname(abspath(__file__)))
from ood_corner import run  # noqa: E402

_WDIR = '/work/hdd/bdne/maho3/cmass-ili'
_DEFAULT_BASEDIR = f'{_WDIR}/mtnglike/fastpm_charm7/models/galaxy'
_DEFAULT_TESTDIR = f'{_WDIR}/quijote3gpch/nbody/models/galaxy'
_DEFAULT_NOISES_PATH = f'{_WDIR}/noise_priors/noisegrid.csv'

# Subdirectory under <cell>/testing/ holding this suite's posterior samples.
TEST_TAG = 'quijote3gpch_nbody'


def _parse_args():
    p = argparse.ArgumentParser()
    p.add_argument('--basedir',     default=_DEFAULT_BASEDIR)
    p.add_argument('--testdir',     default=_DEFAULT_TESTDIR)
    p.add_argument('--noises-path', default=_DEFAULT_NOISES_PATH)
    p.add_argument('--test-tag',    default=TEST_TAG)
    p.add_argument('--n-random', type=int, default=3,
                   help='Noise configs to plot at random, on top of the '
                        'z-minimising one. All are used if fewer exist.')
    p.add_argument('--outdir', default=join(
        os.path.dirname(os.path.abspath(__file__)), 'figures'))
    return p.parse_args()


if __name__ == '__main__':
    a = _parse_args()
    run(a.basedir, a.testdir, a.test_tag, a.noises_path, a.outdir,
        n_random=a.n_random)
