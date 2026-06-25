#!/bin/bash
#SBATCH --job-name=abacus_experiment
#SBATCH --nodes=1
#SBATCH --ntasks=8
#SBATCH --time=4:00:00
#SBATCH --partition=cpu
#SBATCH --account=bdne-delta-cpu
#SBATCH --output=/work/hdd/bdne/maho3/jobout/%x_%j.out
#SBATCH --error=/work/hdd/bdne/maho3/jobout/%x_%j.out

# ── Configuration ─────────────────────────────────────────────────────────────

# Training suite
TRAIN_NBODY=quijotelike
TRAIN_SIM=fastpm_charm6_comp
TRACER=galaxy

# Abacus test suite
TEST_NBODY=abacus
TEST_SIM=custom_hodz_gridnoise

# Working directory containing all suite data
WDIR=/work/hdd/bdne/maho3/cmass-ili

# Notes to record in config.md (optional)
NOTES=""

# ── Derived paths ─────────────────────────────────────────────────────────────

REPO=/u/maho3/git/ltu-gobig-notes
SCRIPTS=$REPO/scripts

BASEDIR=$WDIR/$TRAIN_NBODY/$TRAIN_SIM/models/$TRACER
TESTDIR=$WDIR/$TEST_NBODY/$TEST_SIM/models/$TRACER
NOISES=$WDIR/noise_priors/noisegrid.csv
COSM_TABLE=$WDIR/scratch/abacus_custom_table.csv

DATE=$(date +%Y-%m-%d)
EXPNAME="${DATE}_ood_${TRAIN_NBODY}-${TRAIN_SIM}_${TEST_NBODY}-${TEST_SIM}"
EXPDIR=$REPO/experiments/$EXPNAME
FIGDIR=$EXPDIR/figures

mkdir -p "$FIGDIR"

# ── Write config.md ───────────────────────────────────────────────────────────

cat > "$EXPDIR/config.md" <<EOF
**Script**: ood_abacus_inference.py
**Train**: $TRAIN_NBODY/$TRAIN_SIM
**Test**: $TEST_NBODY/$TEST_SIM
**Tracer**: $TRACER
**Test Noise**: noisegrid.csv
**Summaries**: zPk0+zPk2+zPk4, zPk0+zPk2+zPk4+zBk0, zPk0+zPk2+zPk4+zEqBk0
**kmax**: 0.2, 0.3, 0.4, 0.5, 0.6
**Notes**: $NOTES
EOF

echo "Experiment: $EXPNAME"
echo "Output:     $EXPDIR"

# ── Environment ───────────────────────────────────────────────────────────────

source ~/.bashrc
conda activate cmass

export TQDM_DISABLE=0

cd "$SCRIPTS"

# ── Run script ────────────────────────────────────────────────────────────────

echo "Running ood_abacus_inference.py..."
python ood_abacus_inference.py \
    --basedir     "$BASEDIR" \
    --testdir     "$TESTDIR" \
    --noises-path "$NOISES" \
    --cosm-table  "$COSM_TABLE" \
    --outdir      "$FIGDIR"

echo "Done. Figures in $FIGDIR"
