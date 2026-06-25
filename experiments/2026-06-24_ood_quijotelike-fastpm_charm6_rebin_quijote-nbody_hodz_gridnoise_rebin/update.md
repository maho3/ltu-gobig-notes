# ood_quijotelike-fastpm_charm6_rebin_quijote-nbody_hodz_gridnoise_rebin
**Date**: 2026-06-24
**Type**: OOD inference
**Train**: quijotelike/fastpm_charm6_rebin
**Test**: quijote/nbody_hodz_gridnoise_rebin
**Tracer**: galaxy
**Summaries**: zPk0+zPk2+zPk4, zPk0+zPk2+zPk4+zBk0, zPk0+zPk2+zPk4+zEqBk0
**kmax**: 0.2, 0.3, 0.4, 0.5, 0.6
**Notes**: quijotelike-fastpm_charm6_rebin is a rebinned variant of the quijotelike suite

## Overview

- Ωm median coverage is consistently below 0.5 (light red) across all summary types, kmax values, and noise configurations, indicating systematic underprediction of Ωm coverage throughout the full noise grid.
- σ8 median coverage is consistently above 0.5 (blue) across all cells, with the most extreme overprediction at low noise (σ_rad, σ_tran ≈ 0) and at higher kmax; the zPk024+zBk0 row reaches near-saturation (coverage ≈ 1.0) at kmax=0.3 and 0.4.
- The simultaneous Ωm underprediction and σ8 overprediction pattern across all noise configurations is consistent with CHARM devoxelization bias.
- Zoom-in at zPk024, kmax=0.3 confirms that σ8 OOD coverage curves (blue) lie above the diagonal across virtually all noise bins, while Ωm curves also show above-diagonal deviation; both biases persist at high noise, indicating the penalty is not reduced by positional noise.
- Zoom-in at zPk024+zBk0, kmax=0.3 shows the most severe σ8 bias: OOD calibration fraction for σ8 reaches approximately 14% at moderate noise (n24), far below the expected 50%, while Ωm calibration is closer to acceptable except at the lowest noise bins where weak underprediction is visible.
- Zoom-in at zPk024+zEqBk0, kmax=0.3 shows the same pattern: σ8 OOD coverage fraction (~26%) is substantially below the 50% expectation while Ωm remains within or near the ±0.1 tolerance for most noise configurations; the EqBk0 summary does not substantially mitigate the σ8 bias relative to zBk0.
- Adding bispectrum information (zBk0 or zEqBk0) amplifies the σ8 overprediction relative to power spectrum multipoles alone, suggesting additional summary statistics increase the OOD penalty for σ8 in the CHARM-to-Quijote transfer.
- Self-consistent curves (orange) in scatter and residual plots track the diagonal closely for both parameters, confirming the bias is specific to the OOD transfer and not a training failure.

## Figures

### Overview

<details>
<summary>Median coverage — Ωm</summary>

<img width="900" src="figures/median_coverage_p0.jpg" />

</details>

<details>
<summary>Median coverage — σ8</summary>

<img width="900" src="figures/median_coverage_p4.jpg" />

</details>

### Flagged cells

<details>
<summary>zPk024_kmax0.3</summary>

<table>
<tr>
<td><img width="400" src="figures/zPk0_zPk2_zPk4_kmin-0.0_kmax-0.3/coverage_Om.jpg" /></td>
<td><img width="400" src="figures/zPk0_zPk2_zPk4_kmin-0.0_kmax-0.3/coverage_s8.jpg" /></td>
</tr>
<tr>
<td><img width="400" src="figures/zPk0_zPk2_zPk4_kmin-0.0_kmax-0.3/pred_Om.jpg" /></td>
<td><img width="400" src="figures/zPk0_zPk2_zPk4_kmin-0.0_kmax-0.3/pred_s8.jpg" /></td>
</tr>
</table>

</details>

<details>
<summary>zPk024_zBk0_kmax0.3</summary>

<table>
<tr>
<td><img width="400" src="figures/zPk0_zPk2_zPk4_zBk0_kmin-0.0_kmax-0.3/coverage_Om.jpg" /></td>
<td><img width="400" src="figures/zPk0_zPk2_zPk4_zBk0_kmin-0.0_kmax-0.3/coverage_s8.jpg" /></td>
</tr>
<tr>
<td><img width="400" src="figures/zPk0_zPk2_zPk4_zBk0_kmin-0.0_kmax-0.3/pred_Om.jpg" /></td>
<td><img width="400" src="figures/zPk0_zPk2_zPk4_zBk0_kmin-0.0_kmax-0.3/pred_s8.jpg" /></td>
</tr>
</table>

</details>

<details>
<summary>zPk024_zEqBk0_kmax0.3</summary>

<table>
<tr>
<td><img width="400" src="figures/zPk0_zPk2_zPk4_zEqBk0_kmin-0.0_kmax-0.3/coverage_Om.jpg" /></td>
<td><img width="400" src="figures/zPk0_zPk2_zPk4_zEqBk0_kmin-0.0_kmax-0.3/coverage_s8.jpg" /></td>
</tr>
<tr>
<td><img width="400" src="figures/zPk0_zPk2_zPk4_zEqBk0_kmin-0.0_kmax-0.3/pred_Om.jpg" /></td>
<td><img width="400" src="figures/zPk0_zPk2_zPk4_zEqBk0_kmin-0.0_kmax-0.3/pred_s8.jpg" /></td>
</tr>
</table>

</details>
