# 2026-06-17 OOD — quijotelike/fastpm_charm6 → abacus1gpch/custom_hodz_gridnoise
**Date**: 2026-06-17
**Type**: Abacus OOD inference
**Train**: quijotelike/fastpm_charm6
**Test**: abacus1gpch/custom_hodz_gridnoise
**Tracer**: galaxy
**Summaries**: zPk0, zPk0+zPk2+zPk4, zPk0+zPk2+zPk4+zBk0, zPk0+zPk2+zPk4+zEqBk0
**kmax**: 0.2, 0.3, 0.4
**Notes**: Figures exist for zPk0 (monopole only), which is not listed in config.md. Config lists kmax up to 0.6 but figures are only available for kmax 0.2–0.4.

## Overview

- σ8 is systematically overpredicted (predicted > true) for OOD Abacus points across all summaries and all kmax values, with the OOD residual distribution shifted strongly positive relative to both the self-consistent baseline and the diagonal. The bias is driven primarily by LCDM Mnu>0 (orange) and non-LCDM (green) cosmologies; LCDM Mnu=0 (blue) points also sit above the diagonal but less severely.

- The σ8 overprediction worsens markedly with increasing kmax and with bispectrum summaries. For zPk024 at kmax=0.4, only 13.4% of OOD σ8 residuals are negative; adding Bk0 or EqBk0 at kmax=0.3–0.4 pushes this to 1.7–4.2%, meaning nearly all Abacus predictions overestimate σ8. The zPk0-only monopole shows the weakest σ8 bias (~26–30% negative fraction across kmax 0.2–0.4) and the least kmax dependence.

- Ωm predictions are more nearly unbiased and improve with summary richness and kmax. The monopole-only case shows a moderate positive Ωm bias (~34% negative fraction). Adding higher multipoles reduces the bias substantially: zPk024 at kmax=0.4 reaches 49.6% negative fraction, essentially unbiased. Bispectrum summaries do not further improve Ωm OOD accuracy and in some cases worsen it (zPk024+Bk0 kmax=0.3–0.4 drops to 31–34%).

- Non-LCDM (green squares) show high scatter in both Ωm and σ8 across all cells, indicating poor generalisation beyond ΛCDM. Their σ8 values are broadly overpredicted, consistent with the rest of the OOD population.

- At the highest noise configurations (last rows of the pred grids, σ_rad = σ_tran ≈ 4.3), predictions for both Ωm and σ8 become nearly uninformative, approaching the prior range, as expected.

## Figures

### zPk0, kmax=0.2

<table>
<tr>
<td><img width="400" src="figures/zPk0_kmin-0.0_kmax-0.2/pred_Om.jpg" /></td>
<td><img width="400" src="figures/zPk0_kmin-0.0_kmax-0.2/pred_s8.jpg" /></td>
</tr>
<tr>
<td><img width="400" src="figures/zPk0_kmin-0.0_kmax-0.2/scatter_n24.jpg" /></td>
<td><img width="400" src="figures/zPk0_kmin-0.0_kmax-0.2/residuals_n24.jpg" /></td>
</tr>
</table>

### zPk0, kmax=0.3

<table>
<tr>
<td><img width="400" src="figures/zPk0_kmin-0.0_kmax-0.3/pred_Om.jpg" /></td>
<td><img width="400" src="figures/zPk0_kmin-0.0_kmax-0.3/pred_s8.jpg" /></td>
</tr>
<tr>
<td><img width="400" src="figures/zPk0_kmin-0.0_kmax-0.3/scatter_n24.jpg" /></td>
<td><img width="400" src="figures/zPk0_kmin-0.0_kmax-0.3/residuals_n24.jpg" /></td>
</tr>
</table>

### zPk0, kmax=0.4

<table>
<tr>
<td><img width="400" src="figures/zPk0_kmin-0.0_kmax-0.4/pred_Om.jpg" /></td>
<td><img width="400" src="figures/zPk0_kmin-0.0_kmax-0.4/pred_s8.jpg" /></td>
</tr>
<tr>
<td><img width="400" src="figures/zPk0_kmin-0.0_kmax-0.4/scatter_n24.jpg" /></td>
<td><img width="400" src="figures/zPk0_kmin-0.0_kmax-0.4/residuals_n24.jpg" /></td>
</tr>
</table>

### zPk0+zPk2+zPk4, kmax=0.2

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

### zPk0+zPk2+zPk4, kmax=0.3

<table>
<tr>
<td><img width="400" src="figures/zPk0_zPk2_zPk4_kmin-0.0_kmax-0.3/pred_Om.jpg" /></td>
<td><img width="400" src="figures/zPk0_zPk2_zPk4_kmin-0.0_kmax-0.3/pred_s8.jpg" /></td>
</tr>
<tr>
<td><img width="400" src="figures/zPk0_zPk2_zPk4_kmin-0.0_kmax-0.3/scatter_n24.jpg" /></td>
<td><img width="400" src="figures/zPk0_zPk2_zPk4_kmin-0.0_kmax-0.3/residuals_n24.jpg" /></td>
</tr>
</table>

### zPk0+zPk2+zPk4, kmax=0.4

<table>
<tr>
<td><img width="400" src="figures/zPk0_zPk2_zPk4_kmin-0.0_kmax-0.4/pred_Om.jpg" /></td>
<td><img width="400" src="figures/zPk0_zPk2_zPk4_kmin-0.0_kmax-0.4/pred_s8.jpg" /></td>
</tr>
<tr>
<td><img width="400" src="figures/zPk0_zPk2_zPk4_kmin-0.0_kmax-0.4/scatter_n24.jpg" /></td>
<td><img width="400" src="figures/zPk0_zPk2_zPk4_kmin-0.0_kmax-0.4/residuals_n24.jpg" /></td>
</tr>
</table>

### zPk0+zPk2+zPk4+zBk0, kmax=0.2

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

### zPk0+zPk2+zPk4+zBk0, kmax=0.3

<table>
<tr>
<td><img width="400" src="figures/zPk0_zPk2_zPk4_zBk0_kmin-0.0_kmax-0.3/pred_Om.jpg" /></td>
<td><img width="400" src="figures/zPk0_zPk2_zPk4_zBk0_kmin-0.0_kmax-0.3/pred_s8.jpg" /></td>
</tr>
<tr>
<td><img width="400" src="figures/zPk0_zPk2_zPk4_zBk0_kmin-0.0_kmax-0.3/scatter_n24.jpg" /></td>
<td><img width="400" src="figures/zPk0_zPk2_zPk4_zBk0_kmin-0.0_kmax-0.3/residuals_n24.jpg" /></td>
</tr>
</table>

### zPk0+zPk2+zPk4+zBk0, kmax=0.4

<table>
<tr>
<td><img width="400" src="figures/zPk0_zPk2_zPk4_zBk0_kmin-0.0_kmax-0.4/pred_Om.jpg" /></td>
<td><img width="400" src="figures/zPk0_zPk2_zPk4_zBk0_kmin-0.0_kmax-0.4/pred_s8.jpg" /></td>
</tr>
<tr>
<td><img width="400" src="figures/zPk0_zPk2_zPk4_zBk0_kmin-0.0_kmax-0.4/scatter_n24.jpg" /></td>
<td><img width="400" src="figures/zPk0_zPk2_zPk4_zBk0_kmin-0.0_kmax-0.4/residuals_n24.jpg" /></td>
</tr>
</table>

### zPk0+zPk2+zPk4+zEqBk0, kmax=0.2

<table>
<tr>
<td><img width="400" src="figures/zPk0_zPk2_zPk4_zEqBk0_kmin-0.0_kmax-0.2/pred_Om.jpg" /></td>
<td><img width="400" src="figures/zPk0_zPk2_zPk4_zEqBk0_kmin-0.0_kmax-0.2/pred_s8.jpg" /></td>
</tr>
<tr>
<td><img width="400" src="figures/zPk0_zPk2_zPk4_zEqBk0_kmin-0.0_kmax-0.2/scatter_n24.jpg" /></td>
<td><img width="400" src="figures/zPk0_zPk2_zPk4_zEqBk0_kmin-0.0_kmax-0.2/residuals_n24.jpg" /></td>
</tr>
</table>

### zPk0+zPk2+zPk4+zEqBk0, kmax=0.3

<table>
<tr>
<td><img width="400" src="figures/zPk0_zPk2_zPk4_zEqBk0_kmin-0.0_kmax-0.3/pred_Om.jpg" /></td>
<td><img width="400" src="figures/zPk0_zPk2_zPk4_zEqBk0_kmin-0.0_kmax-0.3/pred_s8.jpg" /></td>
</tr>
<tr>
<td><img width="400" src="figures/zPk0_zPk2_zPk4_zEqBk0_kmin-0.0_kmax-0.3/scatter_n24.jpg" /></td>
<td><img width="400" src="figures/zPk0_zPk2_zPk4_zEqBk0_kmin-0.0_kmax-0.3/residuals_n24.jpg" /></td>
</tr>
</table>

### zPk0+zPk2+zPk4+zEqBk0, kmax=0.4

<table>
<tr>
<td><img width="400" src="figures/zPk0_zPk2_zPk4_zEqBk0_kmin-0.0_kmax-0.4/pred_Om.jpg" /></td>
<td><img width="400" src="figures/zPk0_zPk2_zPk4_zEqBk0_kmin-0.0_kmax-0.4/pred_s8.jpg" /></td>
</tr>
<tr>
<td><img width="400" src="figures/zPk0_zPk2_zPk4_zEqBk0_kmin-0.0_kmax-0.4/scatter_n24.jpg" /></td>
<td><img width="400" src="figures/zPk0_zPk2_zPk4_zEqBk0_kmin-0.0_kmax-0.4/residuals_n24.jpg" /></td>
</tr>
</table>