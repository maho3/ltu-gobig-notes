# ood_abacuslike-fastpm_charm6_comp_abacus-custom_comp_gridnoise
**Date**: 2026-07-13
**Type**: Abacus OOD inference
**Train**: abacuslike/fastpm_charm6_comp
**Test**: abacus/custom_comp_gridnoise
**Tracer**: galaxy
**Summaries**: zPk0, zPk0+zPk2+zPk4, zPk0+zPk2+zPk4+zBk0, zPk0+zPk2+zPk4+zEqBk0
**kmax**: 0.2, 0.3, 0.4 (all summaries); 0.5, 0.6 (zPk0, zPk024 only)
**Notes**: abacuslike CHARM run (wider "comp" HOD prior) tested on Abacus with the same wider HOD, aligning the training and test HOD priors more closely than in the previous abacus-custom_hodz_gridnoise comparison

## Overview

- Ωm is well-recovered for all three cosmology classes across all summaries and kmax values: true-vs-pred points track the diagonal tightly for LCDM Mnu=0, Mnu>0, and non-LCDM alike, with no visible class-dependent offset. Residuals at n24 (σ_rad=σ_tran=2.26) are tightly clustered near zero and comparable in spread to the self-consistent distribution.
- σ8 shows a regression-to-the-mean pattern rather than a clean directional bias: at n24, predictions for high true σ8 are biased low and predictions for low true σ8 are biased high, for all three cosmology classes together, indicating a shrinkage effect from the training prior rather than a class-specific offset.
- For zPk0 alone, the LCDM Mnu=0 mean joint z-score stays low and uniform (near 0) across the noise grid at kmax=0.2-0.4. At kmax=0.5 an orange/red patch appears at low σ_rad, and at kmax=0.6 a large red region (z near the colorbar max of 4) covers most of the low-to-mid σ_rad range, indicating recovery breaks down at high kmax.
- zPk024 follows the same pattern as zPk0 but is more robust: kmax=0.2-0.4 remain uniformly low-z (green), kmax=0.5 shows a mild yellow/orange patch confined to a narrow strip, and only kmax=0.6 develops a severe red region at low-to-mid σ_rad.
- zPk024+zEqBk0 and zPk024+zBk0 (only available up to kmax=0.4) both stay in the low-z (green to pale yellow) regime at kmax=0.2-0.3. At kmax=0.4, both shift uniformly to pale yellow (z~1.5-2) across nearly the entire noise grid rather than localizing to a corner; zPk024+zBk0 is mildly worse than zPk024+zEqBk0, with a small orange patch (z~2.5) at low-to-mid σ_tran, mid-to-high σ_rad. Neither reaches the severe z>3 levels seen for zPk0/zPk024 at kmax=0.5-0.6.
- The rightmost column of the noise grid (highest σ_tran) is consistently the lowest-z (best-recovered) column across all summaries and kmax, matching the pattern seen in the previous abacus-custom_hodz_gridnoise comparison.
- Compared to the earlier abacus-custom_hodz_gridnoise run (Mnu>0 σ8 overpredicted, driven by the narrower training HOD not spanning the test HOD), the wider "comp" HOD used for both training and test here removes that clean class-dependent σ8 offset; the residual σ8 error at moderate noise is dominated by the shrinkage pattern described above rather than a Mnu>0-specific bias.

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
<summary>zPk0 kmax=0.5</summary>

<table>
<tr>
<td><img width="400" src="figures/zPk0_kmin-0.0_kmax-0.5/pred_Om.jpg" /></td>
<td><img width="400" src="figures/zPk0_kmin-0.0_kmax-0.5/pred_s8.jpg" /></td>
</tr>
<tr>
<td><img width="400" src="figures/zPk0_kmin-0.0_kmax-0.5/lcdm_z_heatmap.png" /></td>
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
<summary>zPk024 kmax=0.6</summary>

<table>
<tr>
<td><img width="400" src="figures/zPk0_zPk2_zPk4_kmin-0.0_kmax-0.6/pred_Om.jpg" /></td>
<td><img width="400" src="figures/zPk0_zPk2_zPk4_kmin-0.0_kmax-0.6/pred_s8.jpg" /></td>
</tr>
<tr>
<td><img width="400" src="figures/zPk0_zPk2_zPk4_kmin-0.0_kmax-0.6/lcdm_z_heatmap.png" /></td>
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
