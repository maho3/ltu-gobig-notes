# 2026-06-15_ood_quijotelike-fastpm_charm6_quijote-nbody_hodz_gridnoise
**Date**: 2026-06-15
**Type**: OOD inference
**Train**: quijotelike/fastpm_charm6
**Test**: quijote/nbody_hodz_gridnoise
**Tracer**: galaxy
**Summaries**: zPk0+zPk2+zPk4, zPk0+zPk2+zPk4+zBk0, zPk0+zPk2+zPk4+zEqBk0
**kmax**: 0.2, 0.3, 0.4
**Notes**: 

## Overview
- Ωm is strongly biased low (deep red) at k<0.1 across all summaries and noise configurations; at kmax=0.2/0.3/0.4 Ωm coverage is largely near 0.5, with mild red at low-noise corners that does not rise to a consistent grid-wide bias.
- σ8 is biased high (overcoverage, blue) across the grid for nearly all (summary, kmax) combinations with kmax≥0.2; the bias intensifies with increasing kmax and with summary richness — zPk024+zBk0 and zPk024+zEqBk0 at kmax=0.3 and 0.4 show very strong overcoverage.
- Zoom-ins confirm σ8 overcoverage is systematic: coverage PIT curves lie above the diagonal and pred_s8 scatter shows predicted σ8 values shifted high relative to truth; the bias is present at low noise for all flagged cells and diminishes but does not vanish at high noise for most cells. Ωm is well-calibrated in all flagged zoom-in cells except zPk024+zEqBk0 at kmax=0.4, where mild Ωm undercoverage appears.
- For zPk024+zBk0 at kmax=0.4, σ8 posteriors collapse at the highest noise levels (large σ_rad, σ_tran), with coverage curves flattening; this is distinct from the overcoverage pattern at lower noise.

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
<summary>zPk024_kmax0.3 — σ8 biased high</summary>

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
<summary>zPk024_kmax0.4 — σ8 biased high</summary>

<table>
<tr>
<td><img width="400" src="figures/zPk0_zPk2_zPk4_kmin-0.0_kmax-0.4/coverage_Om.jpg" /></td>
<td><img width="400" src="figures/zPk0_zPk2_zPk4_kmin-0.0_kmax-0.4/coverage_s8.jpg" /></td>
</tr>
<tr>
<td><img width="400" src="figures/zPk0_zPk2_zPk4_kmin-0.0_kmax-0.4/pred_Om.jpg" /></td>
<td><img width="400" src="figures/zPk0_zPk2_zPk4_kmin-0.0_kmax-0.4/pred_s8.jpg" /></td>
</tr>
</table>

</details>

<details>
<summary>zPk024+zBk0_kmax0.2 — σ8 biased high</summary>

<table>
<tr>
<td><img width="400" src="figures/zPk0_zPk2_zPk4_zBk0_kmin-0.0_kmax-0.2/coverage_Om.jpg" /></td>
<td><img width="400" src="figures/zPk0_zPk2_zPk4_zBk0_kmin-0.0_kmax-0.2/coverage_s8.jpg" /></td>
</tr>
<tr>
<td><img width="400" src="figures/zPk0_zPk2_zPk4_zBk0_kmin-0.0_kmax-0.2/pred_Om.jpg" /></td>
<td><img width="400" src="figures/zPk0_zPk2_zPk4_zBk0_kmin-0.0_kmax-0.2/pred_s8.jpg" /></td>
</tr>
</table>

</details>

<details>
<summary>zPk024+zBk0_kmax0.3 — σ8 biased high</summary>

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
<summary>zPk024+zBk0_kmax0.4 — σ8 biased high, posterior collapse at high noise</summary>

<table>
<tr>
<td><img width="400" src="figures/zPk0_zPk2_zPk4_zBk0_kmin-0.0_kmax-0.4/coverage_Om.jpg" /></td>
<td><img width="400" src="figures/zPk0_zPk2_zPk4_zBk0_kmin-0.0_kmax-0.4/coverage_s8.jpg" /></td>
</tr>
<tr>
<td><img width="400" src="figures/zPk0_zPk2_zPk4_zBk0_kmin-0.0_kmax-0.4/pred_Om.jpg" /></td>
<td><img width="400" src="figures/zPk0_zPk2_zPk4_zBk0_kmin-0.0_kmax-0.4/pred_s8.jpg" /></td>
</tr>
</table>

</details>

<details>
<summary>zPk024+zEqBk0_kmax0.2 — σ8 biased high</summary>

<table>
<tr>
<td><img width="400" src="figures/zPk0_zPk2_zPk4_zEqBk0_kmin-0.0_kmax-0.2/coverage_Om.jpg" /></td>
<td><img width="400" src="figures/zPk0_zPk2_zPk4_zEqBk0_kmin-0.0_kmax-0.2/coverage_s8.jpg" /></td>
</tr>
<tr>
<td><img width="400" src="figures/zPk0_zPk2_zPk4_zEqBk0_kmin-0.0_kmax-0.2/pred_Om.jpg" /></td>
<td><img width="400" src="figures/zPk0_zPk2_zPk4_zEqBk0_kmin-0.0_kmax-0.2/pred_s8.jpg" /></td>
</tr>
</table>

</details>

<details>
<summary>zPk024+zEqBk0_kmax0.3 — σ8 biased high</summary>

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

<details>
<summary>zPk024+zEqBk0_kmax0.4 — σ8 biased high, Ωm mild undercoverage</summary>

<table>
<tr>
<td><img width="400" src="figures/zPk0_zPk2_zPk4_zEqBk0_kmin-0.0_kmax-0.4/coverage_Om.jpg" /></td>
<td><img width="400" src="figures/zPk0_zPk2_zPk4_zEqBk0_kmin-0.0_kmax-0.4/coverage_s8.jpg" /></td>
</tr>
<tr>
<td><img width="400" src="figures/zPk0_zPk2_zPk4_zEqBk0_kmin-0.0_kmax-0.4/pred_Om.jpg" /></td>
<td><img width="400" src="figures/zPk0_zPk2_zPk4_zEqBk0_kmin-0.0_kmax-0.4/pred_s8.jpg" /></td>
</tr>
</table>

</details>
