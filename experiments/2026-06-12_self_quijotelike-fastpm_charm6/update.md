# 2026-06-12_self_quijotelike-fastpm_charm6
**Date**: 2026-06-12
**Type**: Self-consistent
**Suite**: quijotelike/fastpm_charm6
**Tracer**: galaxy
**kmax sweep summary**: zPk0+zPk2+zPk4
**kmax values**: 0.1, 0.2, 0.3, 0.4
**Feature sweep kmax**: 0.4
**Feature sweep summaries**: zPk0, zPk0+zPk2+zPk4, zPk0+zPk2+zPk4+zBk0, zPk0+zPk2+zPk4+zEqBk0
**Notes**: 

## Overview
- kmax sweep shows well-calibrated posteriors (median coverage ~0.50 for both parameters) across all kmax values with continuous stdev improvement as kmax increases; no plateau observed.
- Feature sweep reveals training convergence issues: adding equilateral bispectrum (EqBk0) to the feature set causes σ8 stdev to degrade (~0.024 → ~0.035) despite higher feature dimensionality, driven by sub-optimal optuna training (lower final log-prob vs. zBk0 model).
- Ωm constraints improve monotonically with kmax; σ8 shows larger stdev overall but remains well-calibrated throughout both sweeps.

## Findings

### kmax sweep — zPk0+zPk2+zPk4
- Stdev for Ωm decreases monotonically from ~0.026 (kmax=0.1) to ~0.015 (kmax=0.4); σ8 decreases from ~0.095 to ~0.025 over the same range. No plateau detected; constraining power continues to improve at kmax=0.4.
- Calibration holds: Median coverage fraction (true fraction in 50% credible interval) stays centered near 0.50 for both parameters across all kmax values. 68% coverage fraction (16–84th percentile) hovers near 0.70, consistent with well-calibrated posteriors.
- No evidence of stdev saturation or calibration breakdown across the kmax range.

### Feature sweep — kmax=0.4
- Adding zPk2+zPk4 to zPk0 improves both Ωm (0.0195 → 0.0145) and σ8 (0.070 → 0.050) stdev. Further addition of zBk0 yields additional gains: Ωm ~0.0135, σ8 ~0.024. Adding zEqBk0 instead reverses gains for σ8, increasing from ~0.024 to ~0.035, while Ωm shows marginal degradation (0.0135 → 0.0175).
- The σ8 stdev degradation with zEqBk0 is **not** information saturation but rather a **training convergence failure**: optuna optimization for the zEqBk0 model reaches a plateau at lower validation log-probability (~10.6) compared to zBk0 (~11.0), indicating the optimizer struggled to find as good a solution in the higher-dimensional feature space.
- Stdev scatter across cosmology parameter space (stdev_vs_theta.png) shows the σ8 broadening is uniform across all tested σ8 values (0.65–0.95), ruling out localized cosmology-dependent effects and supporting the hypothesis of a general optimization or feature conditioning issue.

## Figures

### kmax sweep

<details>
<summary>kmax scaling</summary>

<img width="900" src="figures/model_scaling/kmax_sweep/kmax_scaling.png" />

</details>

<details>
<summary>Calibration</summary>

<img width="900" src="figures/model_scaling/kmax_sweep/calibration.png" />

</details>

### Feature sweep

<details>
<summary>Feature length scaling</summary>

<img width="900" src="figures/model_scaling/feature_sweep/feature_length_scaling.png" />

</details>

<details>
<summary>Calibration</summary>

<img width="900" src="figures/model_scaling/feature_sweep/calibration.png" />

</details>

### Zoom-ins

<details>
<summary>feature_sweep</summary>

<table>
<tr>
<td><img width="400" src="figures/model_scaling/feature_sweep/stdev_vs_theta.png" /></td>
<td><img width="400" src="figures/model_scaling/feature_sweep/fiducial_stdev.png" /></td>
</tr>
<tr>
<td><img width="400" src="figures/model_scaling/feature_sweep/optuna_history.png" /></td>
<td></td>
</tr>
</table>

</details>
