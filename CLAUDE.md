# ltu-gobig-notes — CLAUDE.md

This repo stores research experiment logs for the `ltu-cmass` SBI pipeline.
Each experiment lives under `experiments/<dir>/` and contains:
- `config.md` — experiment configuration (suite, simulator, summaries, kmax)
- `figures/` — output plots from analysis scripts
- `update.md` — generated research log entry

**Directory naming convention**:
- OOD: `YYYY-MM-DD_ood_<train-suite>-<train-sim>_<test-suite>-<test-sim>`
  e.g. `2026-06-12_ood_quijotelike-fastpm_charm6_quijote-nbody_hodz_gridnoise`
- Self-consistent: `YYYY-MM-DD_self_<suite>-<sim>`
  e.g. `2026-06-12_self_quijotelike-fastpm_charm6`

**After writing `update.md`**: add a row to `experiments/README.md` with
Date, Type, Train, Test, Notes, and a relative link to the update.

When asked to generate an update for an experiment, follow the instructions
in this file exactly.

---

## Sub-agent model

Use `claude-haiku-4-5-20251001` for all sub-agents.

---

## Project context

**Goal**: infer cosmological parameters (primarily Ωm, σ8) from galaxy
clustering summary statistics using simulation-based inference (SBI / NPE).

**Pipeline**:
1. Run N-body or emulated simulations (FastPM + CHARM, Quijote, Abacus, etc.)
2. Populate galaxies via HOD
3. Compute summary statistics: redshift-space power spectrum multipoles
   (zPk0, zPk2, zPk4), bispectrum (zBk0), equilateral bispectrum (zEqBk0)
4. Train a neural posterior estimator (NPE) on one simulation suite
5. Evaluate on same suite (self-consistent) or a different suite (OOD)

**Key parameters**:
- Ωm (param index 0), σ8 (param index 4) are the primary inference targets
- `kmax` — maximum wavenumber used in inference [h/Mpc]
- `σ_rad`, `σ_tran` — radial (LOS) and transverse positional noise applied
  to galaxies; experiments may use a grid of these values
- Summary shorthand: zPk024 = zPk0+zPk2+zPk4; Bk0 = zBk0

**What good looks like**:
- Coverage (PIT) curves: diagonal = well-calibrated; below = overconfident;
  above = underconfident
- Median coverage heatmaps: centered at 0.5 = unbiased; blue (>0.5) =
  over-predicting (posteriors too wide or biased high); red (<0.5) =
  under-predicting (posteriors too narrow or biased low)
- Posterior stdev: lower is better, but only if calibration holds
- Calibration fractions: median ~0.50, 68% interval fraction ~0.68

**Known pathology**: CHARM devoxelization bias manifests as Ωm biased low
and σ8 biased high, especially at low noise. Name it explicitly if seen.

**Bias flagging threshold**: Only flag a parameter as biased if the deviation
from 0.5 is clear and consistent across the noise grid. A cell is OK if at
least one noise configuration shows coverage within uncertainty of 0.5,
especially when compared to the self-consistent calibration baseline.
Borderline or noisy deviations should not be flagged.

---

## Experiment types

### 1. OOD inference

**Setup**: NPE trained on one suite (e.g. CHARM-based), tested on a different
suite (e.g. Quijote N-body, Abacus) across a noise grid of (σ_rad, σ_tran).

**Expected figures** (check `figures/` for what is actually present):
- Overview: per-parameter median coverage heatmap grids across all
  (summary, kmax) combinations
- Zoom-in: per-(summary, kmax) folder with heatmap, PIT curves, true vs
  predicted, scatter and residual plots at a representative noise index

**Folder naming**: zoom-in folders use underscores in place of `+`, e.g.
`zPk0_zPk2_zPk4_kmin-0.0_kmax-0.2`. Scan the actual `figures/` directory
to get the correct folder names rather than constructing them from summary
strings.

**Analysis procedure**:

Pass 1 — read all overview figures (run as main agent):
0. Read `config.md` in the experiment directory and use it to populate the
   update.md header fields (Train, Test, Summaries, kmax, Notes, etc.)
1. Identify the overview heatmap figures and read them
2. For each (summary, kmax) cell, assess deviation from 0.5
3. Flag cells as: OK, biased-high, biased-low, or missing
4. Note systematic patterns: does bias grow with kmax? differ by summary?
   consistent across Ωm and σ8?

Pass 2 — zoom in on flagged cells (spawn one Haiku sub-agent per flagged
cell; see "Sub-agent model" above for how to get the model string):
- Read available zoom-in figures for that (summary, kmax) — skip the heatmap
  (redundant with the overview); focus on true/pred and coverage plots
- Identify which noise configurations drive the bias; note directionality
- Return 2-3 bullets per flagged cell

**Writing the update**:
- Findings go in a single flat Overview bullet list — no per-cell subsections
- Describe what the figures show; do not draw causal conclusions or infer
  underlying physics mechanisms
- Figure blocks for flagged cells: show true/pred and coverage side by side;
  do not include the per-cell heatmap panel

Use the template at `templates/ood_update.md`.

---

### 2. Self-consistent diagnostics

**Setup**: NPE trained and tested on the same suite. Sweeps over kmax
(fixed summary) and summary complexity (fixed kmax).

**Expected figures** (check `figures/` for what is actually present):
- Overview: `kmax_scaling.png`, `calibration.png`,
  `feature_length_scaling.png`
- Zoom-in: `stdev_vs_theta.png`, `fiducial_stdev.png`,
  `optuna_history.png` (per sweep subdirectory)

**Analysis procedure**:

Pass 1 — read overview figures (run as main agent):
0. Read `config.md` in the experiment directory and use it to populate the
   update.md header fields (Suite, Summaries, kmax, Notes, etc.)
1. Read `kmax_scaling.png`, `calibration.png`, `feature_length_scaling.png`
2. Assess: does stdev decrease with kmax or plateau?
3. Assess: does calibration hold across kmax and summary complexity?
4. Assess: does adding more summaries (longer feature vector) improve constraints?
5. Flag sweeps where calibration breaks, stdev plateaus early, or feature
   scaling is non-monotonic

Pass 2 — zoom in on flagged sweeps (spawn Haiku sub-agents):
- Read `stdev_vs_theta.png`, `fiducial_stdev.png`, `optuna_history.png`
- Identify: cosmology-dependent issues? Optuna convergence? training
  instability?
- Return 2-3 bullets per flagged sweep

Use the template at `templates/selfconsistent_update.md`.

---

## General rules

- Do not re-run scripts or modify figure files
- Do not invent findings not visible in the figures
- Check what figures actually exist in `figures/` before analysis — do not
  assume a fixed directory structure
- If a figure is missing or unreadable, note it as "missing" in the update
- Write `update.md` only after both passes are complete
- If only overview figures are present, write from Pass 1 only and note
  zoom-ins are unavailable
- Describe observations only — do not infer causal mechanisms or draw
  conclusions about underlying physics beyond what the figures directly show
