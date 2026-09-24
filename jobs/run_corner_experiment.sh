#!/bin/bash
#SBATCH --job-name=corner_experiment
#SBATCH --nodes=1
#SBATCH --ntasks=8
#SBATCH --time=4:00:00
#SBATCH --partition=cpu
#SBATCH --account=bdne-delta-cpu
#SBATCH --output=/work/hdd/bdne/maho3/jobout/%x_%j.out
#SBATCH --error=/work/hdd/bdne/maho3/jobout/%x_%j.out

# OOD inference on a single-cosmology test suite, reported as corner plots.
# Submit once per suite:
#   sbatch --export=ALL,SUITE=quijote3gpch jobs/run_corner_experiment.sh
#   sbatch --export=ALL,SUITE=mtng         jobs/run_corner_experiment.sh

# ── Configuration ─────────────────────────────────────────────────────────────

SUITE=${SUITE:-quijote3gpch}

TRAIN_NBODY=mtnglike
TRAIN_SIM=fastpm_charm7

if [ "$SUITE" = "quijote3gpch" ]; then
    SCRIPT=ood_quijote3gpch_inference.py
    TRACER=galaxy
    TEST_NBODY=quijote3gpch
    NOTES="Single Quijote N-body realisation at the fiducial cosmology (lhid 2000, L=3 Gpc/h). Test set covers only 3 of 49 noise configurations, all on the sigma_rad = sigma_tran diagonal (0.75, 1.50, 2.26), with 5 HOD realisations each; no sigma_rad vs sigma_tran contrast is available."
elif [ "$SUITE" = "mtng" ]; then
    SCRIPT=ood_mtng_inference.py
    TRACER=mtng_lightcone
    TEST_NBODY=mtng
    NOTES="MillenniumTNG lightcone at its own cosmology. Test set covers all 49 noise configurations, one test point each."
else
    echo "Unknown SUITE=$SUITE (expected quijote3gpch or mtng)"; exit 1
fi

TEST_SIM=nbody

# Noise configs plotted at random, on top of the z-minimising one
N_RANDOM=3

WDIR=/work/hdd/bdne/maho3/cmass-ili

# ── Derived paths ─────────────────────────────────────────────────────────────

REPO=/u/maho3/git/ltu-gobig-notes
SCRIPTS=$REPO/scripts

BASEDIR=$WDIR/$TRAIN_NBODY/$TRAIN_SIM/models/$TRACER
TESTDIR=$WDIR/$TEST_NBODY/$TEST_SIM/models/$TRACER
NOISES=$WDIR/noise_priors/noisegrid.csv

DATE=$(date +%Y-%m-%d)
EXPNAME="${DATE}_ood_${TRAIN_NBODY}-${TRAIN_SIM}_${TEST_NBODY}-${TEST_SIM}"
EXPDIR=$REPO/experiments/$EXPNAME
FIGDIR=$EXPDIR/figures

mkdir -p "$FIGDIR"

# ── Write config.md ───────────────────────────────────────────────────────────

cat > "$EXPDIR/config.md" <<EOF
**Script**: $SCRIPT (via ood_corner.py)
**Train**: $TRAIN_NBODY/$TRAIN_SIM
**Test**: $TEST_NBODY/$TEST_SIM
**Tracer**: $TRACER
**Test Noise**: noisegrid.csv
**Summaries**: auto-discovered from model tree
**kmax**: auto-discovered per summary (supports dynamic per-observable cuts)
**Noise configs plotted**: z-minimising config plus $N_RANDOM at random, per cell
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

echo "Running $SCRIPT..."
python "$SCRIPT" \
    --basedir     "$BASEDIR" \
    --testdir     "$TESTDIR" \
    --noises-path "$NOISES" \
    --n-random    "$N_RANDOM" \
    --outdir      "$FIGDIR"

echo "Done. Figures in $FIGDIR"
