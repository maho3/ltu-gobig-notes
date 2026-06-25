# ood_abacuslike-fastpm_charm6_abacus-custom_hodz_gridnoise
**Date**: 2026-06-24
**Type**: Abacus OOD inference
**Train**: abacuslike/fastpm_charm6
**Test**: abacus/custom_hodz_gridnoise
**Tracer**: galaxy
**Summaries**: zPk0+zPk2+zPk4, zPk0+zPk2+zPk4+zBk0, zPk0+zPk2+zPk4+zEqBk0
**kmax**: 0.2, 0.3, 0.4, 0.5, 0.6
**Notes**: 2 Gpc/h abacuslike CHARM run tested on Abacus custom HOD with noise grid

## Overview

- Ωm is well-recovered across all summary and kmax combinations for LCDM Mnu=0 cosmologies: true-vs-pred points track the diagonal tightly with small residuals across the full noise grid.
- σ8 is systematically overpredicted for LCDM Mnu>0 (orange triangles) relative to LCDM Mnu=0 (blue circles) at the same true σ8 values; this offset is visible across all summaries and kmax values and is most pronounced at low noise (σ_tran < 1.5).
- Non-LCDM cosmologies (green squares) show larger scatter in σ8 predictions but do not exhibit a consistent directional offset, consistent with the wider cosmology range spanned by this class.
- For zPk0 alone, LCDM Mnu=0 mean joint z-scores remain below 2 at kmax ≤ 0.4 across most of the noise grid; at kmax = 0.5 and 0.6, z-scores exceed 2 in the low-σ_tran regime, indicating the model breaks down for zPk0 at high kmax.
- For zPk024, LCDM Mnu=0 recovery is good (z < 2) at kmax ≤ 0.4 except in the high-σ_rad, low-σ_tran corner; at kmax = 0.5–0.6 large fractions of the noise grid exceed z = 2, driven primarily by σ8 bias.
- Adding zEqBk0 substantially improves LCDM Mnu=0 recovery relative to zPk024: at kmax = 0.2–0.4 the z < 2 region covers nearly the full noise grid (excluding the highest σ_tran column), and mean z-scores are noticeably lower than zPk024 at the same kmax.
- Adding zBk0 does not improve LCDM Mnu=0 recovery; instead it degrades it significantly relative to zPk024 and zEqBk0. At kmax = 0.3–0.4 the entire noise grid (excluding the highest σ_tran column) exceeds z = 2, with z-scores reaching the colorbar maximum of 4.
- The rightmost column of the noise grid (σ_tran ≈ 4.51) consistently shows z ≈ 0 across all cells, indicating near-zero signal at maximum transverse noise; this pattern is present for all summaries and kmax values.
- At representative noise n=24 (σ_rad = 2.26, σ_tran = 2.26), σ8 residuals for OOD Abacus points are positively biased relative to the self-consistent grey distribution, consistent with the Mnu>0 upward offset visible in the true-vs-pred plots. Ωm residuals are centered near zero for OOD points, matching the self-consistent distribution well.
- The global z-score panel confirms that zPk0 at kmax ≤ 0.4 and zPk024+zEqBk0 at kmax ≤ 0.4 are the best-performing configurations for recovering LCDM Mnu=0 Abacus cosmologies.

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
<summary>zPk0 kmax=0.4</summary>

<table>
<tr>
<td><img width="400" src="figures/zPk0_kmin-0.0_kmax-0.4/pred_Om.jpg" /></td>
<td><img width="400" src="figures/zPk0_kmin-0.0_kmax-0.4/pred_s8.jpg" /></td>
</tr>
</table>

</details>

<details>
<summary>zPk0 kmax=0.5</summary>

<table>
<tr>
<td><img width="400" src="figures/zPk0_kmin-0.0_kmax-0.5/pred_Om.jpg" /></td>
<td><img width="400" src="figures/zPk0_kmin-0.0_kmax-0.5/pred_s8.jpg" /></td>
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
<td><img width="400" src="figures/zPk0_zPk2_zPk4_kmin-0.0_kmax-0.4/lcdm_z_heatmap.png" /></td>
</tr>
</table>

</details>

<details>
<summary>zPk024 kmax=0.5</summary>

<table>
<tr>
<td><img width="400" src="figures/zPk0_zPk2_zPk4_kmin-0.0_kmax-0.5/pred_Om.jpg" /></td>
<td><img width="400" src="figures/zPk0_zPk2_zPk4_kmin-0.0_kmax-0.5/pred_s8.jpg" /></td>
</tr>
<tr>
<td><img width="400" src="figures/zPk0_zPk2_zPk4_kmin-0.0_kmax-0.5/lcdm_z_heatmap.png" /></td>
</tr>
</table>

</details>

### zPk024+zEqBk0

<details>
<summary>zPk024+zEqBk0 kmax=0.2</summary>

<table>
<tr>
<td><img width="400" src="figures/zPk0_zPk2_zPk4_zEqBk0_kmin-0.0_kmax-0.2/pred_Om.jpg" /></td>
<td><img width="400" src="figures/zPk0_zPk2_zPk4_zEqBk0_kmin-0.0_kmax-0.2/pred_s8.jpg" /></td>
</tr>
<tr>
<td><img width="400" src="figures/zPk0_zPk2_zPk4_zEqBk0_kmin-0.0_kmax-0.2/scatter_n24.jpg" /></td>
<td><img width="400" src="figures/zPk0_zPk2_zPk4_zEqBk0_kmin-0.0_kmax-0.2/residuals_n24.jpg" /></td>
</tr>
<tr>
<td><img width="400" src="figures/zPk0_zPk2_zPk4_zEqBk0_kmin-0.0_kmax-0.2/lcdm_z_heatmap.png" /></td>
</tr>
</table>

</details>

<details>
<summary>zPk024+zEqBk0 kmax=0.3</summary>

<table>
<tr>
<td><img width="400" src="figures/zPk0_zPk2_zPk4_zEqBk0_kmin-0.0_kmax-0.3/pred_Om.jpg" /></td>
<td><img width="400" src="figures/zPk0_zPk2_zPk4_zEqBk0_kmin-0.0_kmax-0.3/pred_s8.jpg" /></td>
</tr>
<tr>
<td><img width="400" src="figures/zPk0_zPk2_zPk4_zEqBk0_kmin-0.0_kmax-0.3/lcdm_z_heatmap.png" /></td>
</tr>
</table>

</details>

<details>
<summary>zPk024+zEqBk0 kmax=0.4</summary>

<table>
<tr>
<td><img width="400" src="figures/zPk0_zPk2_zPk4_zEqBk0_kmin-0.0_kmax-0.4/pred_Om.jpg" /></td>
<td><img width="400" src="figures/zPk0_zPk2_zPk4_zEqBk0_kmin-0.0_kmax-0.4/pred_s8.jpg" /></td>
</tr>
<tr>
<td><img width="400" src="figures/zPk0_zPk2_zPk4_zEqBk0_kmin-0.0_kmax-0.4/lcdm_z_heatmap.png" /></td>
</tr>
</table>

</details>

### zPk024+zBk0

<details>
<summary>zPk024+zBk0 kmax=0.2</summary>

<table>
<tr>
<td><img width="400" src="figures/zPk0_zPk2_zPk4_zBk0_kmin-0.0_kmax-0.2/pred_Om.jpg" /></td>
<td><img width="400" src="figures/zPk0_zPk2_zPk4_zBk0_kmin-0.0_kmax-0.2/pred_s8.jpg" /></td>
</tr>
<tr>
<td><img width="400" src="figures/zPk0_zPk2_zPk4_zBk0_kmin-0.0_kmax-0.2/scatter_n24.jpg" /></td>
<td><img width="400" src="figures/zPk0_zPk2_zPk4_zBk0_kmin-0.0_kmax-0.2/residuals_n24.jpg" /></td>
</tr>
</table>

</details>

<details>
<summary>zPk024+zBk0 kmax=0.3</summary>

<table>
<tr>
<td><img width="400" src="figures/zPk0_zPk2_zPk4_zBk0_kmin-0.0_kmax-0.3/pred_Om.jpg" /></td>
<td><img width="400" src="figures/zPk0_zPk2_zPk4_zBk0_kmin-0.0_kmax-0.3/pred_s8.jpg" /></td>
</tr>
<tr>
<td><img width="400" src="figures/zPk0_zPk2_zPk4_zBk0_kmin-0.0_kmax-0.3/lcdm_z_heatmap.png" /></td>
</tr>
</table>

</details>

<details>
<summary>zPk024+zBk0 kmax=0.4</summary>

<table>
<tr>
<td><img width="400" src="figures/zPk0_zPk2_zPk4_zBk0_kmin-0.0_kmax-0.4/pred_Om.jpg" /></td>
<td><img width="400" src="figures/zPk0_zPk2_zPk4_zBk0_kmin-0.0_kmax-0.4/pred_s8.jpg" /></td>
</tr>
<tr>
<td><img width="400" src="figures/zPk0_zPk2_zPk4_zBk0_kmin-0.0_kmax-0.4/lcdm_z_heatmap.png" /></td>
</tr>
</table>

</details>
