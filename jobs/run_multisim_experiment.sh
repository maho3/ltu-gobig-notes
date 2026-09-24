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
# Compares constraining power between two or three model dirs (same tracer) as
# a function of summary and kmax. Each entry carries its own nbody suite, so
# this covers both same-suite comparisons (e.g. with vs without HOD posterior
# inference) and cross-suite ones (e.g. a box-size ladder).

TRACER=galaxy

NBODY1=quijotelike
SIM1=fastpm_charm7_cosmoHOD
LABEL1="L=1 Gpc/h"

NBODY2=abacuslike
SIM2=fastpm_charm7_cosmoHOD
LABEL2="L=2 Gpc/h"

# Third model dir is optional; leave SIM3 empty for a two-way comparison.
NBODY3=mtnglike
SIM3=fastpm_charm7
LABEL3="L=3 Gpc/h"

# Fiducial-point nbar band [h/Mpc]^-3. All three entries here are cubic-box
# galaxy tracers, which sit in 1e-4..5e-4.
NBAR_LO=1e-4
NBAR_HI=5e-4

# Working directory containing all suite data
WDIR=/work/hdd/bdne/maho3/cmass-ili

# Notes to record in config.md (optional)
NOTES="Box-size ladder at matched pipeline and tracer: all three infer the same 17-parameter theta (5 cosmology + 10 HOD + 2 noise) over the same 5 summaries and the same k-cut grid."

# ── Derived paths ─────────────────────────────────────────────────────────────

REPO=/u/maho3/git/ltu-gobig-notes
SCRIPTS=$REPO/scripts

DATE=$(date +%Y-%m-%d)
EXPNAME="${DATE}_multisim_${NBODY1}-${SIM1}_vs_${NBODY2}-${SIM2}"
if [ -n "$SIM3" ]; then
    EXPNAME="${EXPNAME}_vs_${NBODY3}-${SIM3}"
fi
EXPDIR=$REPO/experiments/$EXPNAME
FIGDIR=$EXPDIR/figures

mkdir -p "$FIGDIR"

# ── Write config.md ───────────────────────────────────────────────────────────

cat > "$EXPDIR/config.md" <<EOF
**Script**: model_scaling_diagnostics.py (multisim mode), volume_scaling.py
**Tracer**: $TRACER
**Model 1**: $NBODY1/$SIM1 ($LABEL1)
**Model 2**: $NBODY2/$SIM2 ($LABEL2)
**Model 3**: $NBODY3/$SIM3 ($LABEL3)
**kmax sweep summary**: Pk0+Pk2+Pk4 (prefix auto-detected from the model tree; its k-cuts auto-discovered)
**Feature sweep reference kmax**: 0.4 (per-summary k-cut with closest Pk kmax)
**Feature sweep summaries**: Pk0, Pk0+Pk2+Pk4, Pk0+Pk2+Pk4+EqBk0, Pk0+Pk2+Pk4+SqBk0, Pk0+Pk2+Pk4+Bk0 (with the tree's z-prefix where it has one)
**Fiducial nbar band**: $NBAR_LO to $NBAR_HI
**Volume-scaling reference kmax**: 0.4 (per-summary shared k-cut with closest Pk kmax)
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

ARGS=(
    --wdir   "$WDIR"
    --tracer "$TRACER"
    --nbody  "$NBODY1" --sim  "$SIM1" --label1 "$LABEL1"
    --nbody2 "$NBODY2" --sim2 "$SIM2" --label2 "$LABEL2"
    --nbar-lo "$NBAR_LO" --nbar-hi "$NBAR_HI"
    --outdir "$FIGDIR/model_scaling"
)
if [ -n "$SIM3" ]; then
    ARGS+=(--nbody3 "$NBODY3" --sim3 "$SIM3" --label3 "$LABEL3")
fi

echo "Running model_scaling_diagnostics.py (multisim)..."
python model_scaling_diagnostics.py "${ARGS[@]}"

# Volume scaling reads its suite list (with each box's L) from the SUITES block
# in the script itself, since box size is not something the multisim CLI knows.
# Keep that block in step with the NBODY/SIM settings above.
echo "Running volume_scaling.py..."
python volume_scaling.py \
    --wdir     "$WDIR" \
    --tracer   "$TRACER" \
    --ref-kmax 0.4 \
    --nbar-lo  "$NBAR_LO" \
    --nbar-hi  "$NBAR_HI" \
    --outdir   "$FIGDIR/volume_scaling"

echo "Done. Figures in $FIGDIR"
