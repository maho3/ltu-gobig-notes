# Lossless in-place HDF5 compression of the cmass-ili database (Bridges2)

**Date**: 2026-08-12
**Type**: Miscellaneous / data operation
**Scope**: `/ocean/projects/phy240015p/mho1/cmass-ili/` on Bridges2. Four suites
recompressed in place so far: `quijotelike_nophase/fastpm`,
`quijotelike-fid/fastpm`, `abacuslike/pinocchio`, `mtnglike/fastpm`.
**Notes**: Scratch/tooling lived in `/ocean/projects/phy240015p/mho1/compression_scratch/`,
which may be deleted. The scripts referenced here are copied into `scripts/`
alongside this note; the full running report is `scripts/rollout_report_full.md`.
No figures (data operation, not an analysis run).

**TL;DR:** Applied lossless `SHUFFLE + GZIP=4` to the large simulation suites,
in place, one file at a time (repack to a temp in the same directory, verify
bit-exact, then atomic rename over the original). Bit-exactness is checked with
`np.array_equal` on every dataset plus HDF5's own `h5diff` as an independent
second verifier, plus dtype/shape/attribute checks and a post-replace sha256.
Achieved ~1.20x on the FastPM `nbody.h5` grids (rho+fvel) and ~1.62x on the
Pinocchio `halos.h5` catalogs. Four suites done so far: **33.79 TB -> 27.37 TB,
6.42 TB freed**, all bit-exact, no data lost. Chosen over the higher-ratio
`SCALEOFFSET` path because that one is lossy, and over ZSTD because ZSTD is a
non-default plugin the readers do not load. Two operational notes worth keeping:
the compression is a net read-time *loss* on Ocean (gzip decompress is CPU-bound
below Lustre's read speed), and the work list must be built from a live disk
scan, not from run logs, because the suite was a moving target (a Globus sync
landed mid-run).

## Setup

- Filter: `SHUFFLE + GZIP=4`, bit-exact. Rejected alternatives: `SCALEOFFSET`
  (SOFF=2,DS)+GZIP4 gives ~1.9-2.2x but is lossy (fixed absolute decimal
  precision; it silently destroys fields with small dynamic range such as
  Pinocchio `rho`); ZSTD/LZ4 compress and decompress faster but are dynamically
  loaded HDF5 plugins (via the `hdf5plugin` package), and the `ltu-cmass`
  readers never `import hdf5plugin` nor set `HDF5_PLUGIN_PATH`, so a
  ZSTD-compressed file would raise "filter not available" on read. GZIP+SHUFFLE
  are built into libhdf5 and read everywhere with no configuration.
- Tools: system `h5repack`/`h5dump` (HDF5 1.12.1, `anaconda3-2024.10`) for the
  repack and filter inspection; `h5py` (HDF5 1.14.4, the `cmass` conda env) for
  the in-process bit-check and for driving everything.
- Chunking (per the earlier benchmark convention, ~N/4 on grid axes, 65536 rows
  on catalogs, capped to dataset dims): rho `{N,N,N}` -> `N/4` cubed; fvel
  `{N,N,N,3}` -> `N/4` cubed x3; 1D/2D catalogs (`mass`, `pos`, `vel`) ->
  `min(65536, Nrow)` (x3). For L3000-N384 that is 96^3 and 96^3x3.
- **h5repack gotcha (important):** a global `-f GZIP=4` combined with per-object
  `-l CHUNK=...` silently no-ops the GZIP filter in h5repack 1.12.1 (SHUFFLE
  still applies, output comes out the same size, run finishes in a fraction of a
  second because deflate never ran). Filters must be specified per object:
  `-f "GRP/rho:SHUF" -f "GRP/rho:GZIP=4" -l "GRP/rho:CHUNK=..."`. Always confirm
  with `h5dump -p -H` that both `PREPROCESSING SHUFFLE` and
  `COMPRESSION DEFLATE { LEVEL 4 }` appear on every dataset.

## In-place algorithm (why and how)

Free space on Ocean was only ~4 TB against multi-TB suites, so a
copy-all-then-swap approach was impossible. The tool (`scripts/compress_inplace.py`)
works one file at a time and never holds more than one temp per worker:

1. skip if the file already carries SHUFFLE+DEFLATE (resumable) or has 0
   datasets (empty/failed file, left untouched);
2. `h5repack` original -> `<orig>.tmp_compress` in the same directory;
3. verify: filters present on every dataset; `np.array_equal` of every dataset
   (decompressed) against the original; dtype and shape preserved; all
   file/group/dataset attributes preserved; optionally `h5diff -q` as an
   independent second verifier;
4. `os.replace(tmp, orig)`: atomic rename on the same filesystem (instant, no
   data copy);
5. post-replace: sha256 of the in-place file matches the temp's, filters
   present.

The ordering is the safety guarantee: the original is never removed until a
bit-identical verified temp exists, and the replace is atomic, so any failure
(or a killed job) can only leave the original intact plus an orphan temp. Any
per-file verification failure aborts the run and leaves that original untouched.
This was checked by fault injection (force `array_equal` to return False: the
original's sha256 was unchanged, it stayed uncompressed, no temp left behind).

Verification knobs (env): `VERIFY_H5DIFF=1` adds the independent h5diff pass
(used on the big single-copy suites; roughly doubles read I/O); `VERIFY_SHA=1`
(default) computes the sha256 audit fingerprints and post-replace check.
`array_equal`'s only blind spots (-0.0 vs +0.0, and same-bit NaN) cannot occur
under a byte-preserving lossless filter, so it is sufficient; h5diff is kept as
belt-and-suspenders on the irreplaceable suites.

## Parallelism / SLURM

h5repack is single-threaded per file, so throughput scales with cores. The tool
uses a `multiprocessing.Pool` (NPROC workers per node) and supports SLURM job
arrays via `NSHARD`/`SHARD` (strided disjoint subsets:
`allfiles[SHARD::NSHARD]`), so one suite spreads across nodes. Runs used RM-small
(shared, 128-core nodes) or RM-shared; a per-user QOS limit caps concurrent
array tasks at 2, and RM-small caps walltime at 8h. Per-node memory during
verification is bounded by freeing the compared arrays before the h5diff
subprocess. Small suites ran on a single 32-core node in ~2 min; the 8 GB
lightcone suite needed a 4-shard array and about 3-6 h per shard.

## Results

| suite | file | files | orig | compressed | freed | ratio |
|---|---|---|---|---|---|---|
| quijotelike_nophase/fastpm (canary) | nbody.h5 | 1999 | 62.5 GB | 51.9 GB | 10.6 GB | 1.205 |
| quijotelike-fid/fastpm | nbody.h5 | 1991 | 62.2 GB | 51.8 GB | 10.4 GB | 1.201 |
| abacuslike/pinocchio | halos.h5 | 2000 | 3.16 TB | 1.95 TB | 1.21 TB | 1.620 |
| mtnglike/fastpm | nbody.h5 | 3999 | 30.51 TB | 25.32 TB | 5.19 TB | 1.205 |
| **total** | | **9989** | **33.79 TB** | **27.37 TB** | **6.42 TB** | **1.234** |

- FastPM `nbody.h5` (rho + fvel) compresses at ~1.20x; the fields are close to
  incompressible so the shuffle+gzip gain is modest but consistent
  (min/median/max across files ~1.19/1.20/1.25).
- Pinocchio `halos.h5` (mass, pos, vel) compresses at ~1.62x, the best of the
  set. Lossless, so the Pinocchio-`rho` dynamic-range problem that broke the
  lossy SOFF path does not arise (and these halo files carry no `rho`).
- Every suite verified: final per-suite disk scans show all real files
  compressed, 0 partial/half-compressed, 0 unopenable, 0 stray temps; spot
  reads through the pipeline's own `load_snapshot` succeed.

## Read/write cost (measured, not assumed)

The `ltu-cmass` read path is whole-dataset reads of one snapshot group at a time
(`group['rho'][...]`, `group['pos'][...]`), no sub-dataset striding. Warm-cache
timings on Ocean:

| case | orig read | compressed read | slowdown |
|---|---|---|---|
| mid nbody (268 MB) | 0.18 s | 1.01 s | 5.7x |
| 9 GB lightcone, full sequential | 23.5 s | 130 s | 5.5x |

Compression is a net read-time *loss* here: gzip decompress is single-threaded
and tops out at ~230-270 MB/s, while Lustre already serves ~900-1500 MB/s, so
decompression CPU dominates and reads run ~4-6x slower. Repack is also heavy
(~9 min for a 9 GB file single-threaded). This is a pure disk-space-for-read-speed
trade: ~20-38% smaller on disk, paid for in read latency. ZSTD would soften the
read penalty (it decompresses several times faster than gzip) but was ruled out
for the plugin-availability reason above.

## Incidents (and how they were resolved)

- **Cross-shard temp-cleanup race (mtnglike run 1).** The tool's startup
  "remove stray temps" step globbed *all* `*.tmp_compress` under the suite. With
  array tasks starting staggered (2-at-a-time QOS), a newly starting shard
  deleted the in-flight temps of an already-running shard, causing two shards to
  abort (errors "temp file not found" and "filters missing"). No data was lost
  (the verify-then-atomic-replace ordering means a lost temp only causes a
  spurious abort; both failed originals were confirmed intact). Fixed by scoping
  the startup cleanup to this shard's own file list only
  (`for f in files: remove f+TMPSUF`), verified in a test that one shard's
  cleanup leaves another shard's temps untouched.
- **Misplaced Globus sync.** Mid-operation, ~500 `nbody.h5` (+`config.yaml`),
  2.88 TB, appeared under a nested path `L3000-N384/1335/<lhid>/nbody.h5`
  (one directory too deep; a Globus sync of another DB version landed under the
  legitimate lhid `1335` instead of its parent). Of the 500: 352 duplicated
  existing lhids (262 already compressed), 148 were new lhids 3811-3990. None
  were newer than their correct-location counterparts. Relocated to
  `L3000-N384/<lhid>/`, overwriting (including compressed -> uncompressed), with
  `scripts/relocate_1335.py` (dry-run by default, atomic same-FS renames,
  audit-logged). The overwritten lhids were then recompressed in a second pass.
- **Lesson:** build the work list from a live per-file disk scan
  (`scripts/prescan_mtnglike.py`, classifies GOOD/ALREADY/EMPTY/UNOPENABLE/
  PARTIAL), not from run logs. The metadata scan is what caught the 500 extra
  files the log-derived list missed; logs describe what a run did, not the
  current disk state, and the suite was changing under us.

## Reproducing

Scripts are in `scripts/` (copied out of the now-transient `compression_scratch`).
General flow to compress a suite in place:

```bash
export PATH=/opt/packages/anaconda3-2024.10-1/bin:$PATH   # system h5repack/h5dump
PY=/jet/home/mho1/.conda/envs/cmass/bin/python

# 1. classify current disk state -> writes <OUTBASE>_good.txt (uncompressed) + report
SUITE_ROOT=/ocean/projects/phy240015p/mho1/cmass-ili/<suite> GLOB=nbody.h5 NPROC=48 \
  OUTBASE=/path/scan  $PY prescan_<suite>.py     # prescan_mtnglike.py generalizes via SUITE_ROOT/GLOB/OUTBASE

# 2. compress in place (single node); or submit the job array in scripts/inplace_suite.sbatch
SUITE_ROOT=<suite> FILELIST=/path/scan_good.txt NPROC=64 VERIFY_H5DIFF=1 VERIFY_SHA=1 \
  $PY compress_inplace.py
#   job array: sbatch scripts/inplace_suite.sbatch   (NSHARD/SHARD auto-derive from --array)

# 3. confirm complete: rerun prescan -> expect ALREADY=all, GOOD=0, PARTIAL=0, UNOPENABLE=0
```

- Per-file audit logs (status, orig/comp bytes, sha256) are the
  `inplace_<suite>.jsonl` / `.shardXofN.jsonl` files the tool writes.
- `compress_inplace.py` is idempotent/resumable (skips already-filtered files),
  and aborts on the first genuine verification failure, leaving that original
  intact.
- Remaining big single-copy suite not yet done: `abacuslike/fastpm`. Same
  procedure.
