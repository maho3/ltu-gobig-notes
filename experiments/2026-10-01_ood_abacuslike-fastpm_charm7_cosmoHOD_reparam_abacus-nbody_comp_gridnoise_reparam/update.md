# ood_abacuslike-fastpm_charm7_cosmoHOD_reparam_abacus-nbody_comp_gridnoise_reparam
**Date**: 2026-10-01
**Type**: Abacus OOD inference
**Train**: abacuslike/fastpm_charm7_cosmoHOD_reparam
**Test**: abacus/nbody_comp_gridnoise_reparam
**Tracer**: galaxy
**Summaries**: zPk0; zPk0+zPk2+zPk4; zPk0+zPk2+zPk4+zBk0; zPk0+zPk2+zPk4+zEqBk0; zPk0+zPk2+zPk4+zSqBk0
**kmax**: zPk0 and zPk024: 0.2, 0.4, 0.6 (scalar); zPk024+{zBk0,zEqBk0,zSqBk0}: zBk<0.2 with zPk<0.2/0.4/0.6, and zBk<0.4 with zPk<0.4. The kmax=0.3 models (zPk0, zPk024, zPk024+zBk0 at zPk=zBk=0.3) are still training and are skipped here.
**Notes**: Models trained with `infer.reparam_degeneracy=True`, i.e. the flow samples (degen_r, degen_phi) in place of (eta_vb_centrals, noise_radial); Ωm and σ8 are unaffected by the reparameterization. The Abacus N-body test suite (same halos and diag files as `nbody_comp_gridnoise`, 5732 rows over 119 lhids × 49 noise configs) was re-preprocessed with `reparam_degeneracy=True`, `val_frac=0`, `test_frac=1` so that theta_test is in the model's coordinates. The comparison "non-reparam" numbers below are the sibling `fastpm_charm7_cosmoHOD` models on `abacus/nbody_comp_gridnoise` (17 of 18 cells; its zPk0 kmax=0.4 cell has no OOD samples). The bias table was computed from the same `posterior_samples.npy` files the figures are built from (script and CSV: `cmass-ili/scratch/reparam_ood_table/`). In every heatmap the x-axis is σ_tran and the y-axis σ_rad, both 0 to 4.51 Mpc/h.

## Overview

- Ωm is recovered in every cell with zPk kmax ≤ 0.4. Over the LCDM Mν=0 points (σ_tran < 4.51), the mean (median − truth)/std is 0.03–0.19 for zPk0, 0.19 and 0.67 for zPk024 at kmax 0.2 and 0.4, and 0.18–0.58 for the bispectrum cells. The mean offset is ≤ 0.01 against a posterior std of ~0.015. True-vs-pred for all three cosmology classes tracks the diagonal at every noise level except σ_tran = 4.51 (`pred_Om.jpg`). At zPk kmax = 0.6 the Ωm z rises to 0.9–1.0, except zPk0 alone (−0.05).

- σ8 is biased high, and the bias does not decrease monotonically with kmax. LCDM Mν=0 mean z (σ_tran < 4.51) is:
  - zPk0: +0.19 at kmax 0.2, +0.16 at 0.4, +1.57 at 0.6. The posterior std is 0.11, so the low-kmax cells are uninformative rather than unbiased.
  - zPk024: +1.10 at 0.2 (Δσ8 = +0.047), +0.73 at 0.4 (+0.028), +2.90 at 0.6 (+0.098).
  - +zBk0/+zEqBk0/+zSqBk0 at zPk<0.2, zBk<0.2: +0.76 to +0.81 (Δσ8 ≈ +0.028).
  - The four cells with zPk<0.4: +0.24 to +0.40 (Δσ8 = +0.014 to +0.021). These are the best-recovered σ8 cells in the grid.
  - zPk<0.6, zBk<0.2: +2.2 to +2.9.

<img width="900" src="figures/lcdm_z_global.png" />

- In the global joint-z grid, the zPk ≤ 0.4 cells stay at z ≈ 1–2 except zPk024 at k<0.4. That cell has a band with z > 2, rising to ~3.3 at (σ_rad = 4.51, σ_tran = 0), bounded by the z = 2 contour that runs diagonally from (σ_rad 0.75, σ_tran 0) to (σ_rad 4.51, σ_tran 3.76). All zPk<0.6 cells exceed z = 2 for σ_tran ≤ 1.5–2.26, saturating at z = 4 for zPk024 and the +zBk0/+zEqBk0/+zSqBk0 cells.

- At zPk kmax = 0.6, the σ8 pathology from the 2026-08-20 note is present unchanged. At σ_tran ≤ 0.75 nearly every Abacus point, of every class, is predicted at σ8 ≈ 0.95–1.0, the top of the prior, regardless of the true value (0.68–0.94). The predictions move back toward the diagonal only for σ_tran ≥ 2.26, and for zPk0 alone they stay above 0.9 out to σ_tran = 1.5.

<table>
<tr>
<td><img width="450" src="figures/zPk0_zPk2_zPk4_kmin-0.0_kmax-0.6/pred_s8.jpg" /></td>
<td><img width="450" src="figures/zPk0_kmin-0.0_kmax-0.6/pred_s8.jpg" /></td>
</tr>
</table>

- The σ_tran = 4.51 column, the upper edge of the noise prior, is uniformly green in every heatmap. Only there do the posteriors widen to span most of the prior, Ωm ≈ 0.15–0.43 and σ8 ≈ 0.65–0.95, centred near the prior middle. The low z there reflects the wide posteriors, not good recovery; the 2026-09-28 note describes this as a prior-boundary failure. The bias numbers above exclude this column.

<table>
<tr>
<td><img width="450" src="figures/zPk0_zPk2_zPk4_kmin-0.0_kmax-0.4/pred_Om.jpg" /></td>
<td><img width="450" src="figures/zPk0_zPk2_zPk4_kmin-0.0_kmax-0.4/pred_s8.jpg" /></td>
</tr>
</table>

- The bias is class-dependent at zPk024 kmax 0.4 (n24, σ_rad = σ_tran = 2.26). LCDM Mν=0 points (blue) sit above the diagonal in σ8, at residuals of +0.02 to +0.12. LCDM Mν>0 points (orange) scatter on both sides, most below it, down to about −0.15. The grey self-consistent points have about half the σ8 scatter of the Abacus points. Ωm residuals of all classes stay within about ±0.04 and overlap the self-consistent spread. Holding zPk<0.4 and adding zBk0 (zBk<0.4) tightens the Abacus σ8 scatter around the diagonal at the same noise level.

<table>
<tr>
<td><img width="450" src="figures/zPk0_zPk2_zPk4_kmin-0.0_kmax-0.4/scatter_n24.jpg" /></td>
<td><img width="450" src="figures/zPk0_zPk2_zPk4_kmin-0.0_kmax-0.4/residuals_n24.jpg" /></td>
</tr>
<tr>
<td><img width="450" src="figures/zPk0_zPk2_zPk4_zBk0_kmin-0.0_kmax-zBk=0.4__zPk=0.4/scatter_n24.jpg" /></td>
<td></td>
</tr>
</table>

- At the noise-free row (σ_rad = σ_tran = 0, 9 LCDM Mν=0 points), σ8 is closer to truth at zPk024 kmax 0.4 than when averaged over the noise grid: z = +0.12, against +0.73 over all σ_tran < 4.51. The same holds for the three zPk<0.4, zBk<0.2 bispectrum cells (−0.09 to +0.03). At zPk024 kmax 0.2 it stays at +0.86, and at zPk<0.2, zBk<0.2 at +0.75 to +0.80. This is the noise row used for the 2026-10-01 PPC campaigns.

- The reparameterization does not change cosmology recovery relative to the non-reparam sibling `fastpm_charm7_cosmoHOD`. Cell by cell, the LCDM Mν=0 mean z differs by at most ~0.2 in Ωm and ~0.7 in σ8. The largest σ8 differences are at zPk<0.6 (+zEqBk0 +2.89 vs +2.11; zPk024 +2.90 vs +2.20). Elsewhere, the reparam σ8 z is within ±0.26, slightly higher in most cells: zPk024 kmax 0.2 +1.10 vs +1.02, kmax 0.4 +0.73 vs +0.65. Posterior widths agree to ≲ 0.003 in both parameters.

| Cell (LCDM Mν=0, σ_tran < 4.51) | z Ωm reparam / non-reparam | z σ8 reparam / non-reparam | std σ8 reparam |
|---|---|---|---|
| zPk0 k<0.2 | 0.03 / 0.04 | 0.19 / 0.16 | 0.112 |
| zPk0 k<0.4 | 0.19 / — | 0.16 / — | 0.106 |
| zPk0 k<0.6 | −0.05 / 0.02 | 1.57 / 1.40 | 0.089 |
| zPk024 k<0.2 | 0.19 / 0.07 | 1.10 / 1.02 | 0.049 |
| zPk024 k<0.4 | 0.67 / 0.67 | 0.73 / 0.65 | 0.034 |
| zPk024 k<0.6 | 0.91 / 0.86 | 2.90 / 2.20 | 0.039 |
| +zBk0 zPk<0.2, zBk<0.2 | 0.29 / 0.16 | 0.81 / 0.89 | 0.041 |
| +zBk0 zPk<0.4, zBk<0.2 | 0.53 / 0.55 | 0.24 / 0.25 | 0.031 |
| +zBk0 zPk<0.4, zBk<0.4 | 0.57 / 0.49 | 0.40 / 0.14 | 0.034 |
| +zBk0 zPk<0.6, zBk<0.2 | 0.97 / 0.93 | 2.23 / 2.49 | 0.040 |
| +zEqBk0 zPk<0.2, zBk<0.2 | 0.18 / 0.27 | 0.78 / 0.87 | 0.042 |
| +zEqBk0 zPk<0.4, zBk<0.2 | 0.52 / 0.57 | 0.25 / 0.35 | 0.033 |
| +zEqBk0 zPk<0.4, zBk<0.4 | 0.58 / 0.50 | 0.39 / 0.31 | 0.032 |
| +zEqBk0 zPk<0.6, zBk<0.2 | 0.89 / 0.79 | 2.89 / 2.11 | 0.039 |
| +zSqBk0 zPk<0.2, zBk<0.2 | 0.30 / 0.20 | 0.76 / 0.86 | 0.043 |
| +zSqBk0 zPk<0.4, zBk<0.2 | 0.43 / 0.40 | 0.31 / 0.24 | 0.034 |
| +zSqBk0 zPk<0.4, zBk<0.4 | 0.48 / 0.38 | 0.30 / 0.08 | 0.031 |
| +zSqBk0 zPk<0.6, zBk<0.2 | 0.97 / 1.03 | 2.60 / 2.35 | 0.039 |

## Figures

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
<tr>
<td><img width="400" src="figures/zPk0_kmin-0.0_kmax-0.4/scatter_n24.jpg" /></td>
<td><img width="400" src="figures/zPk0_kmin-0.0_kmax-0.4/residuals_n24.jpg" /></td>
</tr>
<tr>
<td><img width="400" src="figures/zPk0_kmin-0.0_kmax-0.4/lcdm_z_heatmap.png" /></td>
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
<td><img width="400" src="figures/zPk0_zPk2_zPk4_kmin-0.0_kmax-0.4/lcdm_z_heatmap.png" /></td>
</tr>
</table>

</details>

<details>
<summary>zPk024 kmax=0.6</summary>

<table>
<tr>
<td><img width="400" src="figures/zPk0_zPk2_zPk4_kmin-0.0_kmax-0.6/pred_Om.jpg" /></td>
<td><img width="400" src="figures/zPk0_zPk2_zPk4_kmin-0.0_kmax-0.6/scatter_n24.jpg" /></td>
</tr>
<tr>
<td><img width="400" src="figures/zPk0_zPk2_zPk4_kmin-0.0_kmax-0.6/residuals_n24.jpg" /></td>
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

<details>
<summary>zPk024+zBk0: zPk&lt;0.6, zBk&lt;0.2</summary>

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

<details>
<summary>zPk024+zSqBk0: zPk&lt;0.6, zBk&lt;0.2</summary>

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
