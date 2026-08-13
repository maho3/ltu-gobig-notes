# Lossless HDF5 Compression Rollout — Running Report

Track: **lossless only**, `SHUFFLE + GZIP=4` (bit-exact). Companion to
`compression_benchmark_findings.md` (the lossy SOFF track). All work read-only
against `/ocean/projects/phy240015p/mho1/cmass-ili/` so far; nothing in the
live tree modified. Scratch: `/ocean/projects/phy240015p/mho1/compression_scratch/`
(outside the cmass-ili tree).

Started 2026-07-28.

---

## Step 0 — Compressor availability  ✅

- Host: `br014` (Bridges2 login). `h5repack`/`h5dump` = HDF5 **1.12.1**
  (anaconda3-2024.10). `h5py` in `cmass` env = HDF5 1.14.4.
- **GZIP + SHUFFLE**: built into libhdf5, available everywhere with zero config.
- **ZSTD / LZ4 / Blosc / Bitshuffle**: available *only* via the `hdf5plugin`
  5.0.0 package in the `cmass` conda env
  (`.../site-packages/hdf5plugin/plugins/`). Confirmed working: `h5py` reads
  them after `import hdf5plugin`; system `h5repack` applies them via
  `HDF5_PLUGIN_PATH` (verified FILTER_ID 32015 zstd on a test file).
- **Deployment risk (decisive):** the `ltu-cmass` codebase never imports
  `hdf5plugin` and never sets `HDF5_PLUGIN_PATH` (grep of all `.py/.sh/.yaml`
  = 0 hits). A ZSTD-compressed file would be **unreadable** by every current
  reader (the SBI pipeline, `h5dump`, collaborators) unless they add that
  dependency — HDF5 raises "filter not available" rather than degrading.
- **Decision (confirmed with user): use `SHUFFLE + GZIP=4`.** No plugin
  dependency, reads everywhere.

### h5repack syntax gotcha (important for all later steps)
A **global** `-f GZIP=4` combined with **per-object** `-l CHUNK=` silently
**no-ops the GZIP filter** in h5repack 1.12.1 (SHUFFLE still applied; output
came out *larger*, ran in 0.3s = no deflate). Fix: specify filters **per
object**, matching the findings-doc examples:
```
h5repack -f "GRP/rho:SHUF" -f "GRP/rho:GZIP=4" -l "GRP/rho:CHUNK=..." src dst
```
Always verify with `h5dump -p -H | grep -A6 DATASET` that BOTH
`PREPROCESSING SHUFFLE` and `COMPRESSION DEFLATE { LEVEL 4 }` appear.

---

## Step 1 — Lossless ratio estimate (manifest-weighted)  ✅

Re-ran `SHUFFLE+GZIP4` over 18 representative files (one per suite; large
multi-snapshot lightcones sampled at one snapshot near a=0.6667, matching the
original methodology). Per-file ratios track the findings-doc `shuf+gzip4`
predictions closely.

### Per-file sweep

| suite | kind | orig(full) | ratio | repack s |
|---|---|---|---|---|
| abacus/custom | halos | 238 MB | 1.283 | 9.9 |
| abacus/fastpm | nbody | 268 MB | 1.203 | 11.3 |
| abacus/nbody | halos | 125 MB | 1.279 | 4.7 |
| abacus1gpch/custom | halos | 31 MB | 1.266 | 2.0 |
| abacus1gpch/nbody | halos | 16 MB | 1.261 | 1.0 |
| abacuslike/fastpm | nbody | 2.5 GB | 1.193 | 10.6 (1 snap) |
| abacuslike/pinocchio | halos | 3.0 GB | 1.614 | 12.2 (1 snap) |
| for_sammy/pinocchio | nbody | 34 MB | 1.203 | 1.3 |
| mtnglike/fastpm | nbody | 8.4 GB | 1.220 | 43.2 (1 snap) |
| quijote/nbody | halos | 27 MB | 1.359 | 2.0 |
| quijote/nbody_fof | halos | 45 MB | 1.423 | 2.7 |
| quijote3gpch/fastpm | nbody | 906 MB | 1.203 | 61.0 |
| quijote3gpch/nbody | halos | 551 MB | 1.408 | 21.7 |
| quijotelike-fid/fastpm | nbody | 34 MB | 1.200 | 1.4 |
| quijotelike/fastpm | nbody | 34 MB | 1.195 | 1.3 |
| quijotelike/fastpm_CAMELS | nbody | 34 MB | 1.211 | 1.3 |
| quijotelike/pinocchio | halos | 41 MB | 1.597 | 3.5 |
| quijotelike_nophase/fastpm | nbody | 34 MB | 1.195 | 1.4 |

### Manifest-weighted total (Bridges lhid counts × representative size × ratio)

**Overall lossless ratio ≈ 1.31x (~24% smaller, ~67 TB saved of ~281 TB).**

| suite | lhids | ratio | orig TB | saved TB |
|---|---|---|---|---|
| abacuslike/pinocchio | 29991 | 1.614 | 88.8 | **33.8** |
| mtnglike/fastpm | 14146 | 1.220 | 116.6 | **21.0** |
| abacuslike/fastpm | 29848 | 1.193 | 72.9 | **11.8** |
| quijotelike/pinocchio | 14017 | 1.597 | 0.5 | 0.2 |
| (all others) | — | — | ~2.3 | ~0.4 |
| **TOTAL** | | **1.314** | **~281** | **~67** |

Savings are ~99% concentrated in the top three suites. (This is a bit above
the ~1.2-1.25x guessed in CLAUDE.md, because abacuslike/pinocchio halos
compress at 1.61x lossless.) Same order-of-magnitude caveats as the SOFF
estimate apply (one representative file per suite; lightcone ratio from one
snapshot extrapolated to the full file).

---

## Step 2 — Read/write timing  (see below, filled after run)

Read access pattern in `ltu-cmass`: **whole-dataset reads, one snapshot group
at a time** — `group['rho'][...]`, `group['fvel'][...]`, `group['pos'][...]`,
etc. (`bias/rho_to_halo.py:load_snapshot`, `bias/apply_hod.py:load_snapshot`,
`summary/tools.py`). No sub-dataset striding anywhere; the only "partial" read
is selecting one of ~10 snapshot groups in a lightcone file. So the read-cost
question reduces to whole-array decompression cost.

Ran on login node br014 (user waived compute-node requirement). Warm-cache
reads (both orig-copy and compressed on the same FS, read 5x, min reported) —
this isolates **decompression CPU cost**, the conservative "does compression
slow reads" test. Cold/Lustre reads only shift things toward compression by
the 1.2-1.6x-fewer-bytes it pulls.

| case | file | MB | repack s | 1-group read (min) | read MB/s |
|---|---|---|---|---|---|
| small_halos | orig | 27.0 | — | 0.019 | 1442 |
| small_halos | comp | 19.9 | 1.0 | 0.112 | 240 |
| mid_nbody | orig | 268 | — | 0.177 | 1516 |
| mid_nbody | comp | 223 | 9.5 | 1.006 | 267 |
| large_lc (1 group) | orig | 9060 | — | 1.005 | 901 |
| large_lc (1 group) | comp | 7427 | **547** | 3.937 | 230 |

Full-file sequential read of the 9 GB lightcone: **orig 23.5 s → comp 130 s**.

**Verdict: on Ocean, SHUFFLE+GZIP4 is a net read-time LOSS.** Reads are
**~4-6x slower** because gzip decompression is single-threaded and tops out at
~230-270 MB/s decompressed, while the Lustre FS already delivers ~900-1500 MB/s
uncompressed — so I/O is not the bottleneck and the decompress CPU dominates.
Compression only wins reads when the FS is slower than the decompressor
(~230 MB/s), which Ocean is not.

Write/repack cost is also large: **~547 s (~9 min) to repack one 9 GB
lightcone** single-threaded. Rollout of a 14k-lhid lightcone suite is therefore
a multi-CPU-week repack job — must be parallelized across many files/cores, not
run serially.

This is a **pure storage-vs-speed tradeoff**: ~24% less disk, paid for with
4-6x slower reads and a heavy one-time repack. (ZSTD decompresses ~3-5x faster
than gzip and would soften the read penalty, but was ruled out for the
plugin-dependency reason in Step 0.) Whether it's worth it depends on how
read-bound the SBI pipeline is — flagging for your call before rollout.

---

## Step 3 — Safety infrastructure

### Second-copy status (from data_accounting/manifest.tsv DELTA/ANVIL cols)

**⚠️ FLAG:** the three suites that dominate savings are effectively
**single-copy on Bridges**:

| suite | Bridges lhids | 2nd copy? |
|---|---|---|
| **abacuslike/pinocchio** (33.8 TB saved) | 29991 | **NONE** |
| **mtnglike/fastpm** (21 TB saved) | 14146 | **NONE** |
| abacuslike/fastpm (11.8 TB saved) | 29848 | partial (1884/29848 on Anvil) |
| for_sammy/pinocchio | 20021 | NONE |
| quijotelike/pinocchio | 14017 | NONE |
| quijotelike-fid/fastpm, quijotelike_nophase/fastpm | ~10k each | NONE |
| **quijote/nbody** (canary candidate) | 4000 | YES (Delta 14027, Anvil 2000) |
| quijotelike/fastpm | 12000 | YES (Delta+Anvil) |
| quijotelike/fastpm_CAMELS | 10004 | YES (Delta) |

Per ground rule 3, do NOT proceed on any single-copy suite until discussed.

- sha256 checksums: to be generated for the canary suite immediately before
  its repack (stored here, outside cmass-ili).

---

## Step 4 — Canary: quijotelike_nophase/fastpm  ✅ (repack+verify)

User-selected canary (note: **single-copy** on Bridges — flagged; canary is
non-destructive so this is fine until the delete stage, which stays gated).
Manifest lists 9998 lhids but only **1999** `nbody.h5` exist on disk (flagged
discrepancy). Ran parallel (32 cores, RM-small node r001) via SLURM.

**Result: 1999/1999 PASS, 0 FAIL** in 115 s. Per file, all verified:
- filters present on every dataset (`h5dump -p -H`: SHUFFLE + DEFLATE-4),
- **bit-exact** `np.array_equal` on every dataset (rho, fvel) + dtype match,
- HDF5 attributes identical,
- sha256 of every source recorded (`canary_progress.jsonl`).

| metric | value |
|---|---|
| files | 1999 (all PASS) |
| original | 67.08 GB |
| compressed | 55.68 GB |
| **saved** | **11.40 GB** |
| ratio | **1.205x** (min 1.190 / median 1.202 / max 1.252) |
| repack wall (32 cores) | 115 s |

Pipeline read-path check: exercised the pipeline's own
`cmass.bias.rho_to_halo.load_snapshot` on 25 random lhids, orig vs repacked —
arrays bit-identical and a P(k) density summary matched to **max|Δ| = 0.0**.
Confirms the SHUFFLE+GZIP4 files load through real pipeline code with only
built-in gzip (no hdf5plugin) and produce identical science outputs.

### Part A — replace canary originals (user-approved, IRREVERSIBLE)  ✅

After user sign-off, replaced all 1999 originals with their verified compressed
copies. Per-file final gate BEFORE each atomic replace: (1) original sha256 ==
value recorded at canary time (no drift), (2) filters present on the compressed
copy, (3) bit-exact `np.array_equal` re-verify, (4) attrs + dtypes preserved;
then `os.replace(comp, orig)` — atomic rename on the same Lustre mount — then a
post-replace sha256 + filter re-check.

**Result: 1999/1999 REPLACED, 0 FAIL, 11.40 GB freed** (67.08 → 55.68 GB), 62 s
on 32 cores. Spot-checked 3 in-place files: filters present, sha256 == the
verified compressed sha, and `load_snapshot` reads them. All scratch copies
consumed by the move (0 left).

---

## In-place compress→bit-check→replace tool (for low-overhead suites)

`compress_inplace.py`. Motivation: only ~3.8 TB free on Ocean (97% full), far
less than a full 2nd copy of big suites like `mtnglike/fastpm`. So instead of
copy-all-then-replace, it works **one file at a time**: repack original → temp
in the *same directory* → verify (filters + bit-exact arrays + dtypes + attrs)
→ atomic `os.replace` → post-check. Peak extra space = one temp per worker
(~tens of MB here), and space is *freed* as it goes.

**Safety validated before any real single-copy data was touched:**
- happy path: compresses copies in place, filters present, bit-verified;
- resumable: a re-run reports every file `ALREADY` (skips files that already
  carry SHUFFLE+DEFLATE);
- **abort-safety (the critical one):** with a forced bit-check failure, the
  original's sha256 was **unchanged**, it stayed uncompressed, no temp was left
  behind, and the run aborts on first failure (ground rule 4). The original is
  never removed unless a bit-identical verified temp already exists.

### Part B — run in-place tool on quijotelike-fid/fastpm  (single-copy)  ✅

1991 `.h5` (66.82 GB). **Result: 1991/1991 COMPRESSED in place, 0 FAIL, 11.18 GB
freed** (→ 55.64 GB, ratio 1.201), 114 s on 32 cores (RM-small). Independent
post-run checks: file count still 1991 (nothing lost), **0 stray temp files**,
sampled files carry SHUFFLE+DEFLATE, sha256 matches the log, and `load_snapshot`
reads them. Every COMPRESSED record has a recorded compressed sha256.

This proves the low-overhead in-place path end-to-end on real single-copy data:
no full 2nd copy was ever held, peak extra space ≈ one temp per worker.

---

## Status / what's next

Done: canary (`quijotelike_nophase/fastpm`, replaced in place) and the in-place
tool tested on `quijotelike-fid/fastpm`. Two suites now losslessly compressed
in place, ~22.6 GB freed total, all bit-exact.

---

## Rollout progress (in-place, verify-before-replace)

Note: on-disk sizes are far below the manifest estimate — snapshot counts were
trimmed. Actual: pinocchio 2000×halos ≈3.16 TB (not 88 TB); mtnglike 3852×nbody
≈29.65 TB. Rollout sized from disk, not manifest.

| suite | files | result | orig→comp | freed | ratio | verify |
|---|---|---|---|---|---|---|
| quijotelike_nophase/fastpm (canary) | 1999 | ✅ replaced | 67.1→55.7 GB | 11.4 GB | 1.205 | array_equal+attrs+sha |
| quijotelike-fid/fastpm | 1991 | ✅ in-place | 66.8→55.6 GB | 11.2 GB | 1.201 | array_equal+attrs+sha |
| **abacuslike/pinocchio** | 2000 | ✅ in-place | 3.16→1.95 TB | **1.21 TB** | 1.620 | array_equal+attrs+sha; count intact, 0 stray temp, filters+slice-read spot-checked |
| **mtnglike/fastpm** | 3999 (+1 EMPTY skipped) | ✅ in-place | ~34 TB | ~6 TB | 1.205 | array_equal+attrs+sha + **h5diff** (2nd verifier) |

### Tool hardening (`compress_inplace.py`)
- Bit-check: `np.array_equal` per dataset (± shape/dtype guards). The float
  edge cases (±0.0, NaN) can't occur under a byte-lossless filter.
- **Independent 2nd verifier** `VERIFY_H5DIFF=1` (HDF5's own `h5diff`) — enabled
  for the big single-copy suites (pinocchio ran before this flag; mtnglike uses it).
- `VERIFY_SHA` gate (default on) to trade sha I/O when needed.
- Pre-scan (`prescan_mtnglike.py`) quarantines EMPTY/UNOPENABLE/ALREADY files so
  the run never trips on a bad input; tool also self-guards (`EMPTY_SKIP`).
- Job-array **sharding** (NSHARD/SHARD strided) for multi-node on huge suites;
  arrays freed before the h5diff subprocess to bound per-worker memory.
- Abort-safety re-proven after every change: forced mismatch → FAIL, original
  sha unchanged, no stray temp.

### Empty/failed file flagged
`mtnglike/fastpm/L3000-N384/400/nbody.h5` — 800-byte empty HDF5 (0 datasets),
excluded from compression. Likely a failed sim output; worth investigating.

### mtnglike/fastpm — notes (multi-pass)
- Run 1 (job 42806533): 2885/3851 done; shards 0,2 aborted from a **cross-shard
  temp-cleanup race** (each shard's startup deleted *all* temps, incl. other
  running shards' in-flight temps). No data loss — verify-then-atomic-replace
  means a lost temp only causes a spurious abort. Fix: cleanup scoped to each
  shard's own files (verified).
- Mid-way, a **misplaced Globus sync** was found under `L3000-N384/1335/<lhid>/`
  (500 files, 2.88 TB) — 148 new lhids (3811–3990) + 352 dupes of existing.
  Relocated by user to `L3000-N384/<lhid>/` (overwriting, incl. compressed→
  uncompressed) via `relocate_1335.py`. Suite then = 4000 lhids (0–3999).
- Run 2 (job 43160986): rebuilt remaining list from a **fresh disk scan** (1376
  uncompressed), h5diff+sha on, race-fixed tool → 1376/1376, 0 FAIL, all shards
  exit 0:0. **Final scan: 3999 compressed, 0 uncompressed, 0 partial, 0 temps.**
- Lesson: build the work list from a live disk scan, not run logs — the suite
  was a moving target (Globus sync landing during the run).

### Remaining big single-copy suite
`abacuslike/fastpm` (~29.8k lhids in manifest; check disk) — same in-place tool
when you're ready.
