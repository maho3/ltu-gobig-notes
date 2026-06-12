# OOD Inference: CHARM-trained vs. Quijote Test

**Date**: 2026-06-12
**Type**: OOD inference
**Train**: quijotelike/fastpm_charm6
**Test**: quijote/nbody_hodz_gridnoise
**Tracer**: galaxy
**Summaries**: zPk0+zPk2+zPk4, zPk0+zPk2+zPk4+zBk0, zPk0+zPk2+zPk4+zEqBk0
**kmax**: 0.2, 0.3, 0.4
**Notes**: 

## Overview

- **CHARM devoxelization bias dominates the OOD inference.** Ωm is systematically underestimated and overconfident at low noise (median coverage ~0.1–0.4 at kmax=0.1–0.2), while σ8 is consistently overestimated and overconfident across all noise levels (median coverage 0.65–0.95 at kmax≥0.3). This is the classic signature of training-test mismatch between the CHARM mock catalog (used for training) and true N-body Quijote structure.

- **Ωm bias is noise-dependent and partially correctable.** Low-noise configurations (σ_rad ≤ 0.56, σ_tran ≤ 0.01) show severe Ωm underestimation (predicted values biased ~+0.05 above true, posterior too narrow); calibration improves substantially with increased observational noise (reaching ~50% coverage at σ_rad=σ_tran=2.26). This indicates the model exploits spurious low-noise correlations from CHARM that do not generalize to Quijote. Increasing kmax from 0.1 to 0.4 improves Ωm calibration (median coverage shifts from ~0.2 to ~0.45), suggesting higher-k modes contain information that compensates for the domain shift.

- **σ8 bias is noise-independent and worsens with kmax.** At kmax=0.4 with zBk0, σ8 PIT curves are uniformly above diagonal across the entire (σ_rad, σ_tran) grid, indicating overconfident overestimation (median coverage 0.8–0.95). Predicted σ8 values are systematically biased high by ~0.03–0.05 at all noise levels; adding zBk0 or zEqBk0 to the feature set does not reduce this bias, and kmax=0.4 cases are worse than kmax=0.2. The bias originates from fundamental train-test physics mismatch rather than noise-dependent artifacts, as noise injection does not recover diagonal coverage.

- **Summary complexity (zBk0, zEqBk0) does not improve inference and may degrade σ8 calibration.** Median coverage heatmaps show broadly consistent Ωm patterns across all three summary sets, but σ8 overconfidence is no less pronounced with zBk0 or zEqBk0 than with zPk024 alone. The additional information does not compensate for the CHARM-Quijote mismatch.

## Figures

### Overview

<details>
<summary>Median coverage — Ωm</summary>

<img width="900" src="figures/median_coverage_p0.png" />

</details>

<details>
<summary>Median coverage — σ8</summary>

<img width="900" src="figures/median_coverage_p4.png" />

</details>

### Flagged cells

<details>
<summary>zPk0+zPk2+zPk4, kmax=0.1 (strongest Ωm bias)</summary>

<table>
<tr>
<td><img width="400" src="figures/zPk0_zPk2_zPk4_kmin-0.0_kmax-0.1/coverage_Om.png" /></td>
<td><img width="400" src="figures/zPk0_zPk2_zPk4_kmin-0.0_kmax-0.1/coverage_s8.png" /></td>
</tr>
<tr>
<td><img width="400" src="figures/zPk0_zPk2_zPk4_kmin-0.0_kmax-0.1/pred_Om.png" /></td>
<td><img width="400" src="figures/zPk0_zPk2_zPk4_kmin-0.0_kmax-0.1/pred_s8.png" /></td>
</tr>
</table>

</details>

<details>
<summary>zPk0+zPk2+zPk4, kmax=0.2 (moderate Ωm bias, representative pattern)</summary>

<table>
<tr>
<td><img width="400" src="figures/zPk0_zPk2_zPk4_kmin-0.0_kmax-0.2/coverage_Om.png" /></td>
<td><img width="400" src="figures/zPk0_zPk2_zPk4_kmin-0.0_kmax-0.2/coverage_s8.png" /></td>
</tr>
<tr>
<td><img width="400" src="figures/zPk0_zPk2_zPk4_kmin-0.0_kmax-0.2/pred_Om.png" /></td>
<td><img width="400" src="figures/zPk0_zPk2_zPk4_kmin-0.0_kmax-0.2/pred_s8.png" /></td>
</tr>
</table>

</details>

<details>
<summary>zPk0+zPk2+zPk4+zBk0, kmax=0.3 (σ8 bias with higher-order summaries)</summary>

<table>
<tr>
<td><img width="400" src="figures/zPk0_zPk2_zPk4_zBk0_kmin-0.0_kmax-0.3/coverage_Om.png" /></td>
<td><img width="400" src="figures/zPk0_zPk2_zPk4_zBk0_kmin-0.0_kmax-0.3/coverage_s8.png" /></td>
</tr>
<tr>
<td><img width="400" src="figures/zPk0_zPk2_zPk4_zBk0_kmin-0.0_kmax-0.3/pred_Om.png" /></td>
<td><img width="400" src="figures/zPk0_zPk2_zPk4_zBk0_kmin-0.0_kmax-0.3/pred_s8.png" /></td>
</tr>
</table>

</details>

<details>
<summary>zPk0+zPk2+zPk4+zBk0, kmax=0.4 (strongest σ8 bias)</summary>

<table>
<tr>
<td><img width="400" src="figures/zPk0_zPk2_zPk4_zBk0_kmin-0.0_kmax-0.4/coverage_Om.png" /></td>
<td><img width="400" src="figures/zPk0_zPk2_zPk4_zBk0_kmin-0.0_kmax-0.4/coverage_s8.png" /></td>
</tr>
<tr>
<td><img width="400" src="figures/zPk0_zPk2_zPk4_zBk0_kmin-0.0_kmax-0.4/pred_Om.png" /></td>
<td><img width="400" src="figures/zPk0_zPk2_zPk4_zBk0_kmin-0.0_kmax-0.4/pred_s8.png" /></td>
</tr>
</table>

</details>
