# ood_quijotelike-fastpm_charm6_rebin_abacus1gpch-custom_hodz_gridnoise_rebin
**Date**: 2026-06-24
**Type**: Abacus OOD inference
**Train**: quijotelike/fastpm_charm6_rebin
**Test**: abacus1gpch/custom_hodz_gridnoise_rebin
**Tracer**: galaxy
**Summaries**: zPk0+zPk2+zPk4, zPk0+zPk2+zPk4+zBk0, zPk0+zPk2+zPk4+zEqBk0
**kmax**: 0.2, 0.3, 0.4, 0.5, 0.6
**Notes**: rebinned variant; zPk0 only at kmax=0.2, 0.3, 0.5, 0.6 (kmax=0.4 missing); bispectrum cells only at kmax=0.2, 0.3, 0.4

## Overview

- The global z-score summary (`lcdm_z_global.png`) shows that zPk0 and zPk024 cells recover LCDM Mnu=0 cosmologies within z<2 at kmax=0.2 and kmax=0.3. Performance degrades at kmax≥0.5 for zPk0, and at kmax≥0.4 for zPk024, where z-scores exceed 2 across most of the noise grid.
- For zPk024, the rightmost column of the noise grid (highest σ_tran) remains green (well-recovered) even at high kmax, indicating that heavy transverse noise suppresses the bias. The bias concentrates at low to moderate σ_tran.
- Both bispectrum summary types (zPk024+zBk0, zPk024+zEqBk0) show substantially elevated z-scores relative to zPk024 alone at the same kmax values. The zPk024+zBk0 cell at kmax=0.4 is nearly uniformly red across the noise grid. The zPk024+zEqBk0 cells are moderately biased at kmax=0.3–0.4, with z-scores in the orange range over most of the noise grid.
- Ωm predictions are broadly unbiased across all summary and kmax combinations: true-vs-pred panels show all cosmology classes tracking the diagonal without systematic offset.
- σ8 is systematically overpredicted (predicted above diagonal) for LCDM Mnu>0 (orange triangles) and non-LCDM (green squares) cosmologies. LCDM Mnu=0 (blue circles) σ8 predictions are generally closer to the diagonal, especially at kmax=0.2–0.3 with zPk024.
- The σ8 overprediction worsens with increasing kmax and with inclusion of bispectrum summaries. At kmax=0.4 with zPk024+zBk0, σ8 residuals for Mnu>0 points are strongly positive across the full noise range (residuals plot shows 9.3% within-1σ fraction for OOD vs 51.7% for self-consistent), indicating severe σ8 bias.
- The zPk0-only cells show large scatter in σ8 across all noise configurations, with Mnu>0 and non-LCDM points scattered widely above and below the diagonal; Ωm predictions are noisier relative to zPk024 but remain unbiased.
- At the representative noise index n24 (σ_rad=2.26, σ_tran=2.26), Ωm residuals for all cosmology classes are approximately centered on zero for zPk024 and zPk024+zBk0 cells. σ8 residuals are shifted positively for Mnu>0 and non-LCDM points, with the OOD residual histogram strongly skewed to positive values compared to the self-consistent histogram.
- These results are qualitatively consistent with the earlier non-rebinned Abacus OOD test (2026-06-17): σ8 overprediction for Mnu>0 and non-LCDM cosmologies is reproduced with the rebinned summaries, and the LCDM Mnu=0 recovery at kmax=0.2–0.3 with zPk024 is similar. The CHARM devoxelization bias seen in the Quijote OOD rebin test does not appear to strongly affect LCDM Mnu=0 Ωm recovery here.

## Figures

### Global z-score summary

<img width="900" src="figures/lcdm_z_global.png" />

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

### zPk0+zPk2+zPk4, kmax=0.4

<table>
<tr>
<td><img width="400" src="figures/zPk0_zPk2_zPk4_kmin-0.0_kmax-0.4/pred_Om.jpg" /></td>
<td><img width="400" src="figures/zPk0_zPk2_zPk4_kmin-0.0_kmax-0.4/pred_s8.jpg" /></td>
</tr>
<tr>
<td><img width="400" src="figures/zPk0_zPk2_zPk4_kmin-0.0_kmax-0.4/lcdm_z_heatmap.png" /></td>
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

### zPk0+zPk2+zPk4+zBk0, kmax=0.4

<table>
<tr>
<td><img width="400" src="figures/zPk0_zPk2_zPk4_zBk0_kmin-0.0_kmax-0.4/pred_Om.jpg" /></td>
<td><img width="400" src="figures/zPk0_zPk2_zPk4_zBk0_kmin-0.0_kmax-0.4/pred_s8.jpg" /></td>
</tr>
<tr>
<td><img width="400" src="figures/zPk0_zPk2_zPk4_zBk0_kmin-0.0_kmax-0.4/lcdm_z_heatmap.png" /></td>
</tr>
</table>

### zPk0+zPk2+zPk4+zEqBk0, kmax=0.2

<table>
<tr>
<td><img width="400" src="figures/zPk0_zPk2_zPk4_zEqBk0_kmin-0.0_kmax-0.2/pred_Om.jpg" /></td>
<td><img width="400" src="figures/zPk0_zPk2_zPk4_zEqBk0_kmin-0.0_kmax-0.2/pred_s8.jpg" /></td>
</tr>
</table>

### zPk0+zPk2+zPk4+zEqBk0, kmax=0.4

<table>
<tr>
<td><img width="400" src="figures/zPk0_zPk2_zPk4_zEqBk0_kmin-0.0_kmax-0.4/pred_Om.jpg" /></td>
<td><img width="400" src="figures/zPk0_zPk2_zPk4_zEqBk0_kmin-0.0_kmax-0.4/pred_s8.jpg" /></td>
</tr>
<tr>
<td><img width="400" src="figures/zPk0_zPk2_zPk4_zEqBk0_kmin-0.0_kmax-0.4/lcdm_z_heatmap.png" /></td>
</tr>
</table>
