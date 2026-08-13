#!/bin/bash
# In-place lossless compression of mtnglike/fastpm (3851 GOOD nbody.h5, ~29.6 TB).
# SLURM JOB ARRAY: each array task = one node, handling a disjoint strided shard
# of the pre-scanned good-file list. NSHARD/SHARD come from the array so the
# array size and the sharding always agree. Resumable + abort-safe per file.
#
# Tune: --array (0-(N-1)) sets node count; -c sets cores/node; -t walltime.
# Keep --array count == desired NSHARD (handled automatically below).
#SBATCH -J inplace_mtng_resume
#SBATCH -p RM-small
#SBATCH -N 1
#SBATCH --ntasks-per-node=1
#SBATCH -c 64
#SBATCH -t 08:00:00
#SBATCH -A phy240015p
#SBATCH --array=0-3
#SBATCH -o /ocean/projects/phy240015p/mho1/compression_scratch/inplace_mtng_slurm_%A_%a.out
#SBATCH -e /ocean/projects/phy240015p/mho1/compression_scratch/inplace_mtng_slurm_%A_%a.err
set -uo pipefail
export NPROC=64
export SUITE_ROOT=/ocean/projects/phy240015p/mho1/cmass-ili/mtnglike/fastpm
export FILELIST=/ocean/projects/phy240015p/mho1/compression_scratch/mtnglike_remaining2_good.txt
export VERIFY_H5DIFF=1      # independent 2nd verifier (user requested for big suites)
export VERIFY_SHA=1         # sha256 audit + post-replace integrity (set 0 to cut ~28% I/O)
export SHARD=${SLURM_ARRAY_TASK_ID}
export NSHARD=${SLURM_ARRAY_TASK_COUNT}
export PATH=/opt/packages/anaconda3-2024.10-1/bin:$PATH
PY=/jet/home/mho1/.conda/envs/cmass/bin/python
echo "array task SHARD=$SHARD NSHARD=$NSHARD on $(hostname) start=$(date)"
df -h /ocean/projects/phy240015p/mho1 | tail -1
$PY /ocean/projects/phy240015p/mho1/compression_scratch/compress_inplace.py
echo "exit=$? end=$(date)"
df -h /ocean/projects/phy240015p/mho1 | tail -1
