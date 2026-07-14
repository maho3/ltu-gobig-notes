#!/bin/bash
#SBATCH --job-name=multisim_experiment
#SBATCH --nodes=1
#SBATCH --ntasks=8
#SBATCH --time=4:00:00
#SBATCH --partition=cpu
#SBATCH --account=bdne-delta-cpu
#SBATCH --output=/work/hdd/bdne/maho3/jobout/%x_%j.out
#SBATCH --error=/work/hdd/bdne/maho3/jobout/%x_%j.out

# ── Configuration ─────────────────────────────────────────────────────────────
# Compares constraining power between two model dirs (same nbody/tracer) as a
# function of summary and kmax, e.g. with vs without HOD posterior inference.

NBODY=abacuslike
TRACER=galaxy

SIM1=fastpm_charm6_comp
LABEL1="just cosmo"

SIM2=fastpm_charm6_inferhod
LABEL2="cosmo+HOD"

# Working directory containing all suite data
WDIR=/work/hdd/bdne/maho3/cmass-ili

# Notes to record in config.md (optional)
NOTES=""

# ── Derived paths ─────────────────────────────────────────────────────────────

REPO=/u/maho3/git/ltu-gobig-notes
SCRIPTS=$REPO/scripts

DATE=$(date +%Y-%m-%d)
EXPNAME="${DATE}_multisim_${NBODY}-${SIM1}_vs_${SIM2}"
EXPDIR=$REPO/experiments/$EXPNAME
FIGDIR=$EXPDIR/figures

mkdir -p "$FIGDIR"

# ── Write config.md ───────────────────────────────────────────────────────────

cat > "$EXPDIR/config.md" <<EOF
**Script**: model_scaling_diagnostics.py (--sim2 multisim mode)
**Suite**: $NBODY
**Tracer**: $TRACER
**Model 1**: $SIM1 ($LABEL1)
**Model 2**: $SIM2 ($LABEL2)
**kmax sweep summary**: zPk0+zPk2+zPk4
**kmax values**: 0.1, 0.2, 0.3, 0.4, 0.5, 0.6
**Feature sweep kmax**: 0.4
**Feature sweep summaries**: zPk0, zPk0+zPk2+zPk4, zPk0+zPk2+zPk4+zEqBk0, zPk0+zPk2+zPk4+zSqBk0, zPk0+zPk2+zPk4+zBk0
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

echo "Running model_scaling_diagnostics.py (multisim)..."
python model_scaling_diagnostics.py \
    --wdir   "$WDIR" \
    --nbody  "$NBODY" \
    --tracer "$TRACER" \
    --sim    "$SIM1" \
    --sim2   "$SIM2" \
    --label1 "$LABEL1" \
    --label2 "$LABEL2" \
    --outdir "$FIGDIR/model_scaling"

echo "Done. Figures in $FIGDIR"
