# ltu-gobig-notes — CLAUDE.md

This repo stores research experiment logs for the `ltu-cmass` SBI pipeline.
Each experiment lives under `experiments/<dir>/` and contains:
- `config.md` — experiment configuration (suite, simulator, summaries, kmax)
- `figures/` — output plots from analysis scripts
- `update.md` — generated research log entry

---

## General rules

- Do not re-run scripts or modify figure files
- Do not invent findings not visible in the figures
- Check what figures actually exist in `figures/` before analysis — do not assume a fixed directory structure
- If a figure is missing or unreadable, note it as "missing" in the update
- Write `update.md` only after both passes are complete
- If only overview figures are present, write from Pass 1 only and note zoom-ins are unavailable
- Describe observations only — do not infer causal mechanisms or draw conclusions about underlying physics beyond what the figures directly show
- Be concise. Avoid subtitle-style bullet points.

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

---

## Experiment types

### 1. OOD inference

**Setup**: NPE trained on one suite (e.g. CHARM-based), tested on a different
suite (e.g. Quijote N-body, Abacus) across a noise grid of (σ_rad, σ_tran).

**Expected figures** (check `figures/` for what is actually present):
- Overview: per-parameter median coverage heatmap grids across all (summary, kmax) combinations
- Zoom-in: per-(summary, kmax) folder with PIT curves, true vs predicted, scatter and residual plots at a representative noise index

**Zoom-in folder naming**: folders use underscores in place of `+`, e.g.
`zPk0_zPk2_zPk4_kmin-0.0_kmax-0.2`. Scan the actual `figures/` directory to get correct folder names — do not construct them from summary strings.

---

#### OOD — execution order

1. Read `config.md` → populate header fields (Train, Test, Summaries, kmax, Notes)
2. Scan `figures/` → enumerate all overview heatmap paths and zoom-in folder paths
3. **Pass 1** (main agent): read all overview heatmap figures; apply flagging criteria and figure interpretation below; produce flagged cell list
4. **Pass 2** (sub-agents): for each flagged cell, spawn one Haiku sub-agent per the dispatch spec below
5. Collect sub-agent bullets
6. Write `update.md` using template at `templates/ood_update.md` (see Template instructions below)
7. Add a row to `experiments/README.md` with: Date, Type, Train, Test, Notes, relative link to update — insert in ascending date order

---

#### Flagging criteria (OOD)

A (summary, kmax) cell is **flagged** if the median coverage deviates from 0.5 by more than ±0.1 consistently across the noise grid (i.e., the deviation is not confined to one or two isolated noise configurations).

Mark a cell **OK** if the deviations are within ±0.1 of 0.5, or if they are inconsistent across the noise grid.

**Interpreting overview heatmaps (Pass 1)**:
- Centered at 0.5 = unbiased; blue (>0.5) = over-predicting (posteriors biased high); red (<0.5) = under-predicting (posteriors biased low)
- Calibration fractions: median ~0.50, 68% interval fraction ~0.68
- Note whether bias patterns are consistent across both Ωm and σ8, or vary with kmax or summary type
- Known pathology: CHARM devoxelization bias manifests as consistent Ωm and σ8 bias, especially at low noise. Name it explicitly if seen.

---

#### Pass 2 sub-agent dispatch (OOD)

For each flagged cell, spawn one sub-agent using model `claude-haiku-4-5-20251001`.

Provide the sub-agent with:
- The experiment directory path
- The flagged cell identifier: (summary, kmax)
- The zoom-in folder path (from the `figures/` scan in step 2)

Sub-agent instruction:

> You are analyzing a flagged (summary, kmax) cell from an OOD SBI inference experiment.
> The zoom-in folder path is: `<path>`.
>
> Steps:
> 1. List files in the zoom-in folder.
> 2. Read all available figures except any heatmap figure — skip those.
>    Focus on: true/pred plots, coverage (PIT) curves, scatter and residual plots.
> 3. Return 2–3 concise bullets describing:
>    - Which noise configurations (σ_rad, σ_tran) drive the bias
>    - The directionality of the bias (high or low coverage, which parameter)
>    - Any other pattern visible in the figures
>
> What good looks like:
> - Coverage (PIT) curves: diagonal = well-calibrated; below diagonal = underpredicting; above diagonal = overpredicting
> - OOD coverage curves (blue) should be assessed relative to their uncertainty error bars and also relative to the self-consistent coverage curves (orange). If the deviation from diagonal is within the range of the uncertainty or the self-consistent deviation, it is acceptable.
> - Calibration fractions: median ~0.50, 68% interval fraction ~0.68
> - Known pathology: CHARM devoxelization bias manifests as consistent Ωm and σ8 bias, especially at low noise. Name it explicitly if seen.
>
> Success criteria:
> - Bullets describe only what is directly visible in the figures
> - Do not infer causal mechanisms or draw conclusions about underlying physics
> - Do not include the heatmap in your analysis
> - If a figure is missing or unreadable, note it as "missing" rather than skipping silently

---

#### Template instructions (OOD)

Use `templates/ood_update.md`. Populate fields as follows:
- **Date, Type, Train, Test**: parse from the experiment directory name
- **Summaries, kmax**: from `config.md`
- **Overview bullets**: synthesize Pass 1 findings and Pass 2 sub-agent bullets into a single flat bullet list — no per-cell subsections
- **Figure blocks**: for each flagged cell, include true/pred and coverage figures side by side; do not include the per-cell heatmap panel

---

### 2. Self-consistent diagnostics

**Setup**: NPE trained and tested on the same suite. Sweeps over kmax
(fixed summary) and summary complexity (fixed kmax).

**Expected figures** (check `figures/` for what is actually present):
- Overview: `kmax_scaling.png`, `calibration.png`, `feature_length_scaling.png`
- Zoom-in: `stdev_vs_theta.png`, `fiducial_stdev.png`, `optuna_history.png` (per sweep subdirectory)

---

#### Self-consistent — execution order

1. Read `config.md` → populate header fields (Suite, Summaries, kmax, Notes)
2. Scan `figures/` → enumerate overview figure paths and sweep subdirectory paths
3. **Pass 1** (main agent): read `kmax_scaling.png`, `calibration.png`, `feature_length_scaling.png`; apply flagging criteria and figure interpretation below; produce flagged sweep list
4. **Pass 2** (sub-agents): for each flagged sweep, spawn one Haiku sub-agent per the dispatch spec below
5. Collect sub-agent bullets
6. Write `update.md` using template at `templates/selfconsistent_update.md` (see Template instructions below)
7. Add a row to `experiments/README.md` with: Date, Type, Train, Test, Notes, relative link to update — insert in ascending date order

---

#### Flagging criteria (self-consistent)

Flag a sweep if any of the following hold:
- Calibration breaks: median coverage deviates from 0.5 by more than ±0.1 consistently across the sweep
- Posterior stdev plateaus early with increasing kmax (no improvement beyond an early kmax value)
- Feature length scaling is non-monotonic (stdev increases when adding more summaries)

Mark a sweep **OK** if calibration holds within ±0.1 and stdev trends are monotonically improving or flat within measurement uncertainty.

**Interpreting overview figures (Pass 1)**:
- Posterior stdev: lower is better (more constraining power); should decrease with increasing kmax and increasing feature length
- Assess differences in stdev relative to measurement uncertainty — if a difference is within uncertainty bounds, it is acceptable
- Known pathology: increasing feature length can increase posterior stdev if the inference is not training properly and not extracting information effectively

---

#### Pass 2 sub-agent dispatch (self-consistent)

For each flagged sweep, spawn one sub-agent using model `claude-haiku-4-5-20251001`.

Provide the sub-agent with:
- The experiment directory path
- The flagged sweep identifier
- The sweep subdirectory path (from the `figures/` scan in step 2)

Sub-agent instruction:

> You are analyzing a flagged sweep from a self-consistent SBI diagnostics experiment.
> The sweep subdirectory path is: `<path>`.
>
> Steps:
> 1. List files in the sweep subdirectory.
> 2. Read all available figures: `stdev_vs_theta.png`, `fiducial_stdev.png`, `optuna_history.png`.
>    If any are missing, note them as "missing".
> 3. Return 2–3 concise bullets describing:
>    - Whether stdev shows cosmology-dependent trends across parameter space
>    - Whether Optuna optimization converged or shows instability
>    - Any signs of training instability or miscalibration
>
> What good looks like:
> - Posterior stdev should be lower rather than higher (more constraining power)
> - Stdev should decrease monotonically with increasing kmax and feature length; a plateau or increase is a problem
> - Assess differences in stdev relative to their measurement uncertainty — within-uncertainty differences are acceptable
> - Known pathology: increasing feature length can increase posterior stdev if training is not properly maximizing information extraction
>
> Success criteria:
> - Bullets describe only what is directly visible in the figures
> - Do not infer causal mechanisms or draw conclusions about underlying physics
> - If a figure is missing or unreadable, note it as "missing" rather than skipping silently

---

#### Template instructions (self-consistent)

Use `templates/selfconsistent_update.md`. Populate fields as follows:
- **Date, Type, Suite**: parse from the experiment directory name
- **Summaries, kmax**: from `config.md`
- **Overview bullets**: synthesize Pass 1 findings and Pass 2 sub-agent bullets into a single flat bullet list — no per-sweep subsections
- **Figure blocks**: for each flagged sweep, include stdev and calibration figures; do not include overview figures again

---

---

### 3. Abacus OOD inference

**Setup**: NPE trained on one suite (e.g. CHARM-based), tested on the Abacus
simulation suite. Abacus differs from standard OOD (Quijote) in two important
ways:

1. **Non-uniform prior**: Abacus cosmologies are not drawn from a consistent
   Latin-hypercube prior, so coverage/calibration statistics are not meaningful.
   Coverage and heatmap plots are omitted entirely.
2. **Mixed cosmology types**: Not all Abacus simulations are ΛCDM with Mnu = 0.
   Test points are classified into three groups and color-coded in all figures:
   - **LCDM Mnu=0** (blue circles) — standard ΛCDM, massless neutrinos
   - **LCDM Mnu>0** (orange triangles) — ΛCDM with massive neutrinos
   - **non-LCDM** (green squares) — beyond-ΛCDM cosmologies (e.g. wCDM)

   Cosmology type is determined from `abacus_custom_table.csv` via `ids_test.npy`.

**Script**: `scripts/ood_abacus_inference.py`
**Job**: `jobs/run_abacus_experiment.sh`

**Expected figures** (check `figures/` for what is actually present):
- Per-(summary, kmax) folder, same naming convention as OOD
- `pred_Om.jpg`, `pred_s8.jpg` — grid of true-vs-pred across all noise configs, points colored by cosmology type
- `scatter_n{N}.jpg` — true-vs-pred at a representative noise index, with self-consistent comparison in grey
- `residuals_n{N}.jpg` — residual plots at a representative noise index

---

#### Abacus OOD — execution order

1. Read `config.md` → populate header fields (Train, Test, Summaries, kmax, Notes)
2. Scan `figures/` → enumerate per-(summary, kmax) subdirectory paths
3. **Single pass** (main agent): read all available figures in each subdirectory; no flagging or Pass 2 sub-agents needed
4. Write `update.md` using the OOD template at `templates/ood_update.md` with the following adaptations:
   - Omit any mention of coverage or calibration (no such figures exist)
   - Note which cosmology classes (Mnu>0, non-LCDM) show visible bias relative to LCDM Mnu=0 points
   - Include `pred_Om.jpg` / `pred_s8.jpg` as the primary diagnostic figures
5. Add a row to `experiments/README.md`

---

#### Interpreting Abacus OOD figures

- **True-vs-pred grids**: points colored by cosmology class. Look for systematic offsets between classes at the same true parameter value.
- **Mnu>0 bias**: massive-neutrino cosmologies often share the same Ωm as ΛCDM phases but differ in σ8 (via σ8_cb vs σ8_m); offsets in predicted σ8 for orange triangles relative to blue circles are expected and worth noting.
- **non-LCDM bias**: green squares span a wider range of cosmologies; large scatter or systematic offset indicates the NPE does not generalise to non-ΛCDM models.
- **Self vs OOD**: grey points in scatter/residual plots show self-consistent performance on the training suite. The spread of OOD points around the diagonal relative to the grey points quantifies the OOD penalty.
- A small x-jitter is applied to all points so stacked cosmologies (many Abacus phases share the same true Ωm) remain individually visible.

---

---
 
### 4. Miscellaneous
 
**Setup**: A free-form experiment where the user has already written a draft `update.md` brain-dump and placed figures in `figures/`. Your job is to formalize and polish the draft, linking figures to findings. There are no fixed figure names or analysis passes — work from what is present.
 
---
 
#### Miscellaneous — execution order
 
1. Read the draft `update.md` in the experiment directory
2. Scan `figures/` → list all available figures
3. Read every figure
4. Rewrite `update.md` per the editing rules below
5. Add a row to `experiments/README.md` with: Date, Type, Notes, relative link to update
---
 
#### Editing rules
 
**Preserve intent**: do not change the substance of the user's findings. Every claim in the draft must survive into the final version. You may reorder, tighten, and clarify, but do not drop findings or add new ones not present in the draft.
 
**Formalize prose**:
- Rewrite in plain scientific prose: concise, no filler, no em-dashes
- Convert informal shorthand or incomplete sentences into full observations
- Remove hedging language that isn't scientifically warranted ("seems like", "maybe", "I think")
- Preserve hedging that reflects genuine uncertainty ("suggests", "consistent with")
**Link figures to findings**:
- For each finding in the draft, identify which figure(s) in `figures/` best support it
- Embed those figures inline adjacent to the finding they support
- If a finding has no supporting figure, leave it as text only — do not invent a figure link
- If a figure exists but is not referenced in the draft, append it at the end under a section called `## Additional figures` with a one-sentence caption describing what it shows
**Format**:
- Findings go in a single flat bullet list under `## Overview`
- No per-finding subsections or subtitles within bullets
- Figure blocks follow the bullet they support, not grouped at the end (except `## Additional figures`)