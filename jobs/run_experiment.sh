#!/bin/bash
#SBATCH --job-name=experiment
#SBATCH --nodes=1
#SBATCH --ntasks=8
#SBATCH --time=4:00:00
#SBATCH --partition=cpu
#SBATCH --account=bdne-delta-cpu
#SBATCH --output=/work/hdd/bdne/maho3/jobout/%x_%j.out
#SBATCH --error=/work/hdd/bdne/maho3/jobout/%x_%j.out

# ── Configuration ─────────────────────────────────────────────────────────────
# TYPE: "ood" or "self"
TYPE=ood

# Training suite
TRAIN_NBODY=quijotelike
TRAIN_SIM=fastpm_charm6
TRACER=galaxy

# Test suite (OOD only; ignored for TYPE=self)
TEST_NBODY=quijote
TEST_SIM=nbody_hodz_gridnoise

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

DATE=$(date +%Y-%m-%d)

if [ "$TYPE" = "ood" ]; then
    EXPNAME="${DATE}_ood_${TRAIN_NBODY}-${TRAIN_SIM}_${TEST_NBODY}-${TEST_SIM}"
else
    EXPNAME="${DATE}_self_${TRAIN_NBODY}-${TRAIN_SIM}"
fi

EXPDIR=$REPO/experiments/$EXPNAME
FIGDIR=$EXPDIR/figures

mkdir -p "$FIGDIR"

# ── Write config.md ───────────────────────────────────────────────────────────

if [ "$TYPE" = "ood" ]; then
cat > "$EXPDIR/config.md" <<EOF
**Script**: noise_calibration_all.py, ood_noise_inference.py
**Train**: $TRAIN_NBODY/$TRAIN_SIM
**Test**: $TEST_NBODY/$TEST_SIM
**Tracer**: $TRACER
**Test Noise**: noisegrid.csv
**Summaries**: zPk0+zPk2+zPk4, zPk0+zPk2+zPk4+zBk0, zPk0+zPk2+zPk4+zEqBk0
**kmax**: 0.2, 0.3, 0.4
**Notes**: $NOTES
EOF
else
cat > "$EXPDIR/config.md" <<EOF
**Script**: model_scaling_diagnostics.py
**Suite**: $TRAIN_NBODY/$TRAIN_SIM
**Tracer**: $TRACER
**kmax sweep summary**: zPk0+zPk2+zPk4
**kmax values**: 0.1, 0.2, 0.3, 0.4
**Feature sweep kmax**: 0.4
**Feature sweep summaries**: zPk0, zPk0+zPk2+zPk4, zPk0+zPk2+zPk4+zBk0, zPk0+zPk2+zPk4+zEqBk0
**Notes**: $NOTES
EOF
fi

echo "Experiment: $EXPNAME"
echo "Output:     $EXPDIR"

# ── Environment ───────────────────────────────────────────────────────────────

source ~/.bashrc
conda activate cmass

export TQDM_DISABLE=0

cd "$SCRIPTS"

# ── Run scripts ───────────────────────────────────────────────────────────────

if [ "$TYPE" = "ood" ]; then
    echo "Running noise_calibration_all.py..."
    python noise_calibration_all.py \
        --basedir "$BASEDIR" \
        --testdir "$TESTDIR" \
        --noises-path "$NOISES" \
        --outdir "$FIGDIR"

    echo "Running ood_noise_inference.py..."
    python ood_noise_inference.py \
        --basedir "$BASEDIR" \
        --testdir "$TESTDIR" \
        --noises-path "$NOISES" \
        --outdir "$FIGDIR"

else
    echo "Running model_scaling_diagnostics.py..."
    python model_scaling_diagnostics.py \
        --wdir "$WDIR" \
        --nbody "$TRAIN_NBODY" \
        --sim "$TRAIN_SIM" \
        --tracer "$TRACER" \
        --outdir "$FIGDIR/model_scaling"
fi

echo "Done. Figures in $FIGDIR"
