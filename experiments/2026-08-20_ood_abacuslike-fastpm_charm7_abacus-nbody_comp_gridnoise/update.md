# ood_abacuslike-fastpm_charm7_abacus-nbody_comp_gridnoise
**Date**: 2026-08-20
**Type**: Abacus OOD inference
**Train**: abacuslike/fastpm_charm7
**Test**: abacus/nbody_comp_gridnoise
**Tracer**: galaxy
**Summaries**: zPk0; zPk0+zPk2+zPk4; zPk0+zPk2+zPk4+zBk0; zPk0+zPk2+zPk4+zEqBk0; zPk0+zPk2+zPk4+zSqBk0
**kmax**: zPk0: 0.2, 0.6 (scalar); zPk0+zPk2+zPk4: 0.2, 0.4, 0.6 (scalar); zPk0+zPk2+zPk4+{zBk0,zEqBk0,zSqBk0}: dynamic cuts zBk<0.2 with zPk<0.2/0.4/0.6, and zBk<0.4 with zPk<0.4
**Notes**: CHARM7 abacuslike training suite tested on the Abacus N-body suite ("comp" HOD) across the noise grid

## Overview

- Ωm is well recovered across all summaries, kmax values, and cosmology classes: true-vs-pred points for LCDM Mnu=0, Mnu>0, and non-LCDM all track the diagonal tightly at low-to-moderate noise, with no visible class-dependent offset. Error bars widen substantially at the highest noise levels (σ_rad ≳ 3.0, σ_tran ≲ 0.75) and again at the top noise corner (σ_rad=σ_tran=4.51), most noticeably once kmax reaches 0.6.
- σ8 recovery degrades monotonically with increasing zPk kmax, for every summary that includes zPk. At kmax=0.2, σ8 shows a mild regression-to-the-mean pattern (predictions for high true σ8 biased low, predictions for low true σ8 biased high) similar across all three cosmology classes. At kmax=0.4 this shifts toward a net high bias at low noise. At kmax=0.6 the bias becomes severe: predicted σ8 clusters near the top of the prior (~0.95-1.0) for most points at low-to-moderate noise, regardless of true value, only relaxing toward the diagonal as noise increases toward σ_rad~4.5.
- The Mahalanobis z global grid (`lcdm_z_global.png`) shows this pattern directly: zPk0 alone stays uniformly low-z (green, z<1.5) at kmax=0.2 but develops a red patch (z up to ~4) at low σ_tran once kmax=0.6. zPk0+zPk2+zPk4 follows the same trend but more gradually, with a mild orange patch appearing already at kmax=0.4 before turning mostly red at kmax=0.6.
- Adding a bispectrum-family observable at a shallow cut (zBk<0.2) does not prevent this degradation once the zPk cut reaches 0.6: zPk024+zBk0 and zPk024+zSqBk0 both turn deep red (z near the colorbar max of 4) across nearly the entire noise grid except the highest-σ_tran column; zPk024+zEqBk0 is comparably worse than zPk024 alone but stays orange (z~3) rather than saturating red.
- In contrast, holding the zPk cut at 0.4 while increasing the zBk cut to 0.4 (the zPk<0.4, zBk<0.4 cells) keeps recovery good for all three bispectrum flavors: the z-heatmaps stay in the uniform light-green/yellow range (z~1-2), comparable to the zPk<0.2 cells, and the n24 residual scatter for σ8 tracks the diagonal about as well as the self-consistent (grey) points. This indicates the degradation tracks the zPk kmax specifically rather than the presence or kmax of the bispectrum term.
- Across all summaries, the rightmost column of the noise grid (highest σ_tran, σ_tran=4.51) is consistently the best-recovered (lowest z) region regardless of kmax, and Ωm error bars are also most stable there; the left-most columns (low σ_tran) are where the σ8 bias and the largest Ωm error bars concentrate.
- No systematic offset between cosmology classes (LCDM Mnu=0 vs Mnu>0 vs non-LCDM) is visible in the true-vs-pred or residual panels at any kmax: all three classes shift together with the same high-σ8-bias direction as kmax increases, though the non-LCDM (green) and Mnu>0 (orange) classes are more numerous and so trace the bias pattern more clearly than the sparser Mnu=0 (blue) points.

## Figures

### Global summary

<details>
<summary>LCDM Mnu=0 mean joint z-score — all (summary, kmax) cells</summary>

<img width="900" src="figures/lcdm_z_global.png" />

</details>

### zPk0

<details>
<summary>zPk0 kmax=0.2</summary>

<table>
<tr>
<td><img width="400" src="figures/zPk0_kmin-0.0_kmax-0.2/pred_Om.jpg" /></td>
<td><img width="400" src="figures/zPk0_kmin-0.0_kmax-0.2/pred_s8.jpg" /></td>
</tr>
<tr>
<td><img width="400" src="figures/zPk0_kmin-0.0_kmax-0.2/scatter_n24.jpg" /></td>
<td><img width="400" src="figures/zPk0_kmin-0.0_kmax-0.2/residuals_n24.jpg" /></td>
</tr>
<tr>
<td><img width="400" src="figures/zPk0_kmin-0.0_kmax-0.2/lcdm_z_heatmap.png" /></td>
</tr>
</table>

</details>

<details>
<summary>zPk0 kmax=0.6</summary>

<table>
<tr>
<td><img width="400" src="figures/zPk0_kmin-0.0_kmax-0.6/pred_Om.jpg" /></td>
<td><img width="400" src="figures/zPk0_kmin-0.0_kmax-0.6/pred_s8.jpg" /></td>
</tr>
<tr>
<td><img width="400" src="figures/zPk0_kmin-0.0_kmax-0.6/scatter_n24.jpg" /></td>
<td><img width="400" src="figures/zPk0_kmin-0.0_kmax-0.6/residuals_n24.jpg" /></td>
</tr>
<tr>
<td><img width="400" src="figures/zPk0_kmin-0.0_kmax-0.6/lcdm_z_heatmap.png" /></td>
</tr>
</table>

</details>

### zPk024

<details>
<summary>zPk024 kmax=0.2</summary>

<table>
<tr>
<td><img width="400" src="figures/zPk0_zPk2_zPk4_kmin-0.0_kmax-0.2/pred_Om.jpg" /></td>
<td><img width="400" src="figures/zPk0_zPk2_zPk4_kmin-0.0_kmax-0.2/pred_s8.jpg" /></td>
</tr>
<tr>
<td><img width="400" src="figures/zPk0_zPk2_zPk4_kmin-0.0_kmax-0.2/scatter_n24.jpg" /></td>
<td><img width="400" src="figures/zPk0_zPk2_zPk4_kmin-0.0_kmax-0.2/residuals_n24.jpg" /></td>
</tr>
<tr>
<td><img width="400" src="figures/zPk0_zPk2_zPk4_kmin-0.0_kmax-0.2/lcdm_z_heatmap.png" /></td>
</tr>
</table>

</details>

<details>
<summary>zPk024 kmax=0.4</summary>

<table>
<tr>
<td><img width="400" src="figures/zPk0_zPk2_zPk4_kmin-0.0_kmax-0.4/pred_Om.jpg" /></td>
<td><img width="400" src="figures/zPk0_zPk2_zPk4_kmin-0.0_kmax-0.4/pred_s8.jpg" /></td>
</tr>
<tr>
<td><img width="400" src="figures/zPk0_zPk2_zPk4_kmin-0.0_kmax-0.4/scatter_n24.jpg" /></td>
<td><img width="400" src="figures/zPk0_zPk2_zPk4_kmin-0.0_kmax-0.4/residuals_n24.jpg" /></td>
</tr>
<tr>
<td><img width="400" src="figures/zPk0_zPk2_zPk4_kmin-0.0_kmax-0.4/lcdm_z_heatmap.png" /></td>
</tr>
</table>

</details>

<details>
<summary>zPk024 kmax=0.6</summary>

<table>
<tr>
<td><img width="400" src="figures/zPk0_zPk2_zPk4_kmin-0.0_kmax-0.6/pred_Om.jpg" /></td>
<td><img width="400" src="figures/zPk0_zPk2_zPk4_kmin-0.0_kmax-0.6/pred_s8.jpg" /></td>
</tr>
<tr>
<td><img width="400" src="figures/zPk0_zPk2_zPk4_kmin-0.0_kmax-0.6/scatter_n24.jpg" /></td>
<td><img width="400" src="figures/zPk0_zPk2_zPk4_kmin-0.0_kmax-0.6/residuals_n24.jpg" /></td>
</tr>
<tr>
<td><img width="400" src="figures/zPk0_zPk2_zPk4_kmin-0.0_kmax-0.6/lcdm_z_heatmap.png" /></td>
</tr>
</table>

</details>

### zPk024+zBk0

<details>
<summary>zPk024+zBk0: zPk&lt;0.2, zBk&lt;0.2</summary>

<table>
<tr>
<td><img width="400" src="figures/zPk0_zPk2_zPk4_zBk0_kmin-0.0_kmax-zBk=0.2__zPk=0.2/pred_Om.jpg" /></td>
<td><img width="400" src="figures/zPk0_zPk2_zPk4_zBk0_kmin-0.0_kmax-zBk=0.2__zPk=0.2/pred_s8.jpg" /></td>
</tr>
<tr>
<td><img width="400" src="figures/zPk0_zPk2_zPk4_zBk0_kmin-0.0_kmax-zBk=0.2__zPk=0.2/scatter_n24.jpg" /></td>
<td><img width="400" src="figures/zPk0_zPk2_zPk4_zBk0_kmin-0.0_kmax-zBk=0.2__zPk=0.2/residuals_n24.jpg" /></td>
</tr>
<tr>
<td><img width="400" src="figures/zPk0_zPk2_zPk4_zBk0_kmin-0.0_kmax-zBk=0.2__zPk=0.2/lcdm_z_heatmap.png" /></td>
</tr>
</table>

</details>

<details>
<summary>zPk024+zBk0: zPk&lt;0.4, zBk&lt;0.2</summary>

<table>
<tr>
<td><img width="400" src="figures/zPk0_zPk2_zPk4_zBk0_kmin-0.0_kmax-zBk=0.2__zPk=0.4/pred_Om.jpg" /></td>
<td><img width="400" src="figures/zPk0_zPk2_zPk4_zBk0_kmin-0.0_kmax-zBk=0.2__zPk=0.4/pred_s8.jpg" /></td>
</tr>
<tr>
<td><img width="400" src="figures/zPk0_zPk2_zPk4_zBk0_kmin-0.0_kmax-zBk=0.2__zPk=0.4/scatter_n24.jpg" /></td>
<td><img width="400" src="figures/zPk0_zPk2_zPk4_zBk0_kmin-0.0_kmax-zBk=0.2__zPk=0.4/residuals_n24.jpg" /></td>
</tr>
<tr>
<td><img width="400" src="figures/zPk0_zPk2_zPk4_zBk0_kmin-0.0_kmax-zBk=0.2__zPk=0.4/lcdm_z_heatmap.png" /></td>
</tr>
</table>

</details>

<details>
<summary>zPk024+zBk0: zPk&lt;0.6, zBk&lt;0.2 (worst-recovered cell)</summary>

<table>
<tr>
<td><img width="400" src="figures/zPk0_zPk2_zPk4_zBk0_kmin-0.0_kmax-zBk=0.2__zPk=0.6/pred_Om.jpg" /></td>
<td><img width="400" src="figures/zPk0_zPk2_zPk4_zBk0_kmin-0.0_kmax-zBk=0.2__zPk=0.6/pred_s8.jpg" /></td>
</tr>
<tr>
<td><img width="400" src="figures/zPk0_zPk2_zPk4_zBk0_kmin-0.0_kmax-zBk=0.2__zPk=0.6/scatter_n24.jpg" /></td>
<td><img width="400" src="figures/zPk0_zPk2_zPk4_zBk0_kmin-0.0_kmax-zBk=0.2__zPk=0.6/residuals_n24.jpg" /></td>
</tr>
<tr>
<td><img width="400" src="figures/zPk0_zPk2_zPk4_zBk0_kmin-0.0_kmax-zBk=0.2__zPk=0.6/lcdm_z_heatmap.png" /></td>
</tr>
</table>

</details>

<details>
<summary>zPk024+zBk0: zPk&lt;0.4, zBk&lt;0.4</summary>

<table>
<tr>
<td><img width="400" src="figures/zPk0_zPk2_zPk4_zBk0_kmin-0.0_kmax-zBk=0.4__zPk=0.4/pred_Om.jpg" /></td>
<td><img width="400" src="figures/zPk0_zPk2_zPk4_zBk0_kmin-0.0_kmax-zBk=0.4__zPk=0.4/pred_s8.jpg" /></td>
</tr>
<tr>
<td><img width="400" src="figures/zPk0_zPk2_zPk4_zBk0_kmin-0.0_kmax-zBk=0.4__zPk=0.4/scatter_n24.jpg" /></td>
<td><img width="400" src="figures/zPk0_zPk2_zPk4_zBk0_kmin-0.0_kmax-zBk=0.4__zPk=0.4/residuals_n24.jpg" /></td>
</tr>
<tr>
<td><img width="400" src="figures/zPk0_zPk2_zPk4_zBk0_kmin-0.0_kmax-zBk=0.4__zPk=0.4/lcdm_z_heatmap.png" /></td>
</tr>
</table>

</details>

### zPk024+zEqBk0

<details>
<summary>zPk024+zEqBk0: zPk&lt;0.2, zBk&lt;0.2</summary>

<table>
<tr>
<td><img width="400" src="figures/zPk0_zPk2_zPk4_zEqBk0_kmin-0.0_kmax-zBk=0.2__zPk=0.2/pred_Om.jpg" /></td>
<td><img width="400" src="figures/zPk0_zPk2_zPk4_zEqBk0_kmin-0.0_kmax-zBk=0.2__zPk=0.2/pred_s8.jpg" /></td>
</tr>
<tr>
<td><img width="400" src="figures/zPk0_zPk2_zPk4_zEqBk0_kmin-0.0_kmax-zBk=0.2__zPk=0.2/scatter_n24.jpg" /></td>
<td><img width="400" src="figures/zPk0_zPk2_zPk4_zEqBk0_kmin-0.0_kmax-zBk=0.2__zPk=0.2/residuals_n24.jpg" /></td>
</tr>
<tr>
<td><img width="400" src="figures/zPk0_zPk2_zPk4_zEqBk0_kmin-0.0_kmax-zBk=0.2__zPk=0.2/lcdm_z_heatmap.png" /></td>
</tr>
</table>

</details>

<details>
<summary>zPk024+zEqBk0: zPk&lt;0.4, zBk&lt;0.2</summary>

<table>
<tr>
<td><img width="400" src="figures/zPk0_zPk2_zPk4_zEqBk0_kmin-0.0_kmax-zBk=0.2__zPk=0.4/pred_Om.jpg" /></td>
<td><img width="400" src="figures/zPk0_zPk2_zPk4_zEqBk0_kmin-0.0_kmax-zBk=0.2__zPk=0.4/pred_s8.jpg" /></td>
</tr>
<tr>
<td><img width="400" src="figures/zPk0_zPk2_zPk4_zEqBk0_kmin-0.0_kmax-zBk=0.2__zPk=0.4/scatter_n24.jpg" /></td>
<td><img width="400" src="figures/zPk0_zPk2_zPk4_zEqBk0_kmin-0.0_kmax-zBk=0.2__zPk=0.4/residuals_n24.jpg" /></td>
</tr>
<tr>
<td><img width="400" src="figures/zPk0_zPk2_zPk4_zEqBk0_kmin-0.0_kmax-zBk=0.2__zPk=0.4/lcdm_z_heatmap.png" /></td>
</tr>
</table>

</details>

<details>
<summary>zPk024+zEqBk0: zPk&lt;0.6, zBk&lt;0.2</summary>

<table>
<tr>
<td><img width="400" src="figures/zPk0_zPk2_zPk4_zEqBk0_kmin-0.0_kmax-zBk=0.2__zPk=0.6/pred_Om.jpg" /></td>
<td><img width="400" src="figures/zPk0_zPk2_zPk4_zEqBk0_kmin-0.0_kmax-zBk=0.2__zPk=0.6/pred_s8.jpg" /></td>
</tr>
<tr>
<td><img width="400" src="figures/zPk0_zPk2_zPk4_zEqBk0_kmin-0.0_kmax-zBk=0.2__zPk=0.6/scatter_n24.jpg" /></td>
<td><img width="400" src="figures/zPk0_zPk2_zPk4_zEqBk0_kmin-0.0_kmax-zBk=0.2__zPk=0.6/residuals_n24.jpg" /></td>
</tr>
<tr>
<td><img width="400" src="figures/zPk0_zPk2_zPk4_zEqBk0_kmin-0.0_kmax-zBk=0.2__zPk=0.6/lcdm_z_heatmap.png" /></td>
</tr>
</table>

</details>

<details>
<summary>zPk024+zEqBk0: zPk&lt;0.4, zBk&lt;0.4</summary>

<table>
<tr>
<td><img width="400" src="figures/zPk0_zPk2_zPk4_zEqBk0_kmin-0.0_kmax-zBk=0.4__zPk=0.4/pred_Om.jpg" /></td>
<td><img width="400" src="figures/zPk0_zPk2_zPk4_zEqBk0_kmin-0.0_kmax-zBk=0.4__zPk=0.4/pred_s8.jpg" /></td>
</tr>
<tr>
<td><img width="400" src="figures/zPk0_zPk2_zPk4_zEqBk0_kmin-0.0_kmax-zBk=0.4__zPk=0.4/scatter_n24.jpg" /></td>
<td><img width="400" src="figures/zPk0_zPk2_zPk4_zEqBk0_kmin-0.0_kmax-zBk=0.4__zPk=0.4/residuals_n24.jpg" /></td>
</tr>
<tr>
<td><img width="400" src="figures/zPk0_zPk2_zPk4_zEqBk0_kmin-0.0_kmax-zBk=0.4__zPk=0.4/lcdm_z_heatmap.png" /></td>
</tr>
</table>

</details>

### zPk024+zSqBk0

<details>
<summary>zPk024+zSqBk0: zPk&lt;0.2, zBk&lt;0.2</summary>

<table>
<tr>
<td><img width="400" src="figures/zPk0_zPk2_zPk4_zSqBk0_kmin-0.0_kmax-zBk=0.2__zPk=0.2/pred_Om.jpg" /></td>
<td><img width="400" src="figures/zPk0_zPk2_zPk4_zSqBk0_kmin-0.0_kmax-zBk=0.2__zPk=0.2/pred_s8.jpg" /></td>
</tr>
<tr>
<td><img width="400" src="figures/zPk0_zPk2_zPk4_zSqBk0_kmin-0.0_kmax-zBk=0.2__zPk=0.2/scatter_n24.jpg" /></td>
<td><img width="400" src="figures/zPk0_zPk2_zPk4_zSqBk0_kmin-0.0_kmax-zBk=0.2__zPk=0.2/residuals_n24.jpg" /></td>
</tr>
<tr>
<td><img width="400" src="figures/zPk0_zPk2_zPk4_zSqBk0_kmin-0.0_kmax-zBk=0.2__zPk=0.2/lcdm_z_heatmap.png" /></td>
</tr>
</table>

</details>

<details>
<summary>zPk024+zSqBk0: zPk&lt;0.4, zBk&lt;0.2</summary>

<table>
<tr>
<td><img width="400" src="figures/zPk0_zPk2_zPk4_zSqBk0_kmin-0.0_kmax-zBk=0.2__zPk=0.4/pred_Om.jpg" /></td>
<td><img width="400" src="figures/zPk0_zPk2_zPk4_zSqBk0_kmin-0.0_kmax-zBk=0.2__zPk=0.4/pred_s8.jpg" /></td>
</tr>
<tr>
<td><img width="400" src="figures/zPk0_zPk2_zPk4_zSqBk0_kmin-0.0_kmax-zBk=0.2__zPk=0.4/scatter_n24.jpg" /></td>
<td><img width="400" src="figures/zPk0_zPk2_zPk4_zSqBk0_kmin-0.0_kmax-zBk=0.2__zPk=0.4/residuals_n24.jpg" /></td>
</tr>
<tr>
<td><img width="400" src="figures/zPk0_zPk2_zPk4_zSqBk0_kmin-0.0_kmax-zBk=0.2__zPk=0.4/lcdm_z_heatmap.png" /></td>
</tr>
</table>

</details>

<details>
<summary>zPk024+zSqBk0: zPk&lt;0.6, zBk&lt;0.2 (worst-recovered cell)</summary>

<table>
<tr>
<td><img width="400" src="figures/zPk0_zPk2_zPk4_zSqBk0_kmin-0.0_kmax-zBk=0.2__zPk=0.6/pred_Om.jpg" /></td>
<td><img width="400" src="figures/zPk0_zPk2_zPk4_zSqBk0_kmin-0.0_kmax-zBk=0.2__zPk=0.6/pred_s8.jpg" /></td>
</tr>
<tr>
<td><img width="400" src="figures/zPk0_zPk2_zPk4_zSqBk0_kmin-0.0_kmax-zBk=0.2__zPk=0.6/scatter_n24.jpg" /></td>
<td><img width="400" src="figures/zPk0_zPk2_zPk4_zSqBk0_kmin-0.0_kmax-zBk=0.2__zPk=0.6/residuals_n24.jpg" /></td>
</tr>
<tr>
<td><img width="400" src="figures/zPk0_zPk2_zPk4_zSqBk0_kmin-0.0_kmax-zBk=0.2__zPk=0.6/lcdm_z_heatmap.png" /></td>
</tr>
</table>

</details>

<details>
<summary>zPk024+zSqBk0: zPk&lt;0.4, zBk&lt;0.4</summary>

<table>
<tr>
<td><img width="400" src="figures/zPk0_zPk2_zPk4_zSqBk0_kmin-0.0_kmax-zBk=0.4__zPk=0.4/pred_Om.jpg" /></td>
<td><img width="400" src="figures/zPk0_zPk2_zPk4_zSqBk0_kmin-0.0_kmax-zBk=0.4__zPk=0.4/pred_s8.jpg" /></td>
</tr>
<tr>
<td><img width="400" src="figures/zPk0_zPk2_zPk4_zSqBk0_kmin-0.0_kmax-zBk=0.4__zPk=0.4/scatter_n24.jpg" /></td>
<td><img width="400" src="figures/zPk0_zPk2_zPk4_zSqBk0_kmin-0.0_kmax-zBk=0.4__zPk=0.4/residuals_n24.jpg" /></td>
</tr>
<tr>
<td><img width="400" src="figures/zPk0_zPk2_zPk4_zSqBk0_kmin-0.0_kmax-zBk=0.4__zPk=0.4/lcdm_z_heatmap.png" /></td>
</tr>
</table>

</details>
