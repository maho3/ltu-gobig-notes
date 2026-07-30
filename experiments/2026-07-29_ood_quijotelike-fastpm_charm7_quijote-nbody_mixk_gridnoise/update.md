# quijotelike_fastpm_charm7 → quijote_nbody_mixk_gridnoise
**Date**: 2026-07-29
**Type**: OOD inference
**Train**: quijotelike/fastpm_charm7
**Test**: quijote/nbody_mixk_gridnoise
**Tracer**: galaxy
**Summaries**: zPk0, zPk0+zPk2+zPk4, zPk0+zPk2+zPk4+zBk0, zPk0+zPk2+zPk4+zEqBk0, zPk0+zPk2+zPk4+zSqBk0
**kmax**: scalar cuts k<0.2/0.4/0.6 (zPk0, zPk0+zPk2+zPk4); dynamic cuts zPk<0.2/0.4/0.6 paired with zBk<0.2/0.4 (bispectrum-family summaries)
**Notes**: —

## Overview
- Bias direction flips with kmax across nearly every summary: low-kmax cells (k<0.2, zPk<0.2) systematically underpredict σ8 (coverage curves above diagonal, ~0.3–0.4 median vs 0.5), while the highest-kmax cells (k<0.6, zPk<0.6) systematically overpredict both σ8 and, to a lesser extent, Ωm (coverage ~0.65–0.9). The bispectrum-augmented summaries (+zBk0, +zEqBk0, +zSqBk0) show the same pattern, generally strongest at the zPk=0.6/zBk=0.2 corner.
- Across flagged cells the bias is driven predominantly by low-noise configurations (σ_rad, σ_tran ≲ 1.5), where positional noise is smallest and posterior predictions carry the most leverage; several sub-agents describe this pattern as consistent with CHARM devoxelization bias, since it is most pronounced at low noise and attenuates as noise increases. A subset of cells (zPk0+zPk2+zPk4 at k<0.6, zPk0+zPk2+zPk4+zEqBk0 at zPk<0.4/zBk<0.4) instead show an opposite-sign, roughly noise-independent offset (Ωm under-, σ8 over-predicted) that persists across the full noise grid rather than concentrating at low noise.
- Ωm calibration is consistently more robust than σ8 across all cells: Ωm coverage stays within or near tolerance except at the highest kmax, where it drifts upward together with σ8. σ8 shows the largest and most persistent deviations in essentially every flagged cell.
- Increasing feature richness (adding zBk0/zEqBk0/zSqBk0 to zPk0+zPk2+zPk4) does not resolve the bias; the zPk<0.6/zBk<0.2 corner remains strongly biased in every bispectrum-augmented summary, and the +zEqBk0 summary shows the widest OOD–self divergence (up to ~0.9 median σ8 coverage).
- Sub-agent notes flag several cells (zPk0+zPk2+zPk4+B0 at zPk=0.6, zPk0+zPk2+zPk4+SqB0 at zPk=0.6) as consistent with the known CHARM devoxelization pathology (Ωm+σ8 bias concentrated at low noise); other cells show noise-independent or intermediate-noise-driven offsets that do not match this pattern as cleanly.

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
<summary>zPk0, k&lt;0.6</summary>

<table>
<tr>
<td><img width="400" src="figures/zPk0_kmin-0.0_kmax-0.6/coverage_Om.jpg" /></td>
<td><img width="400" src="figures/zPk0_kmin-0.0_kmax-0.6/coverage_s8.jpg" /></td>
</tr>
<tr>
<td><img width="400" src="figures/zPk0_kmin-0.0_kmax-0.6/pred_Om.jpg" /></td>
<td><img width="400" src="figures/zPk0_kmin-0.0_kmax-0.6/pred_s8.jpg" /></td>
</tr>
</table>

σ8 shows pervasive underpredicting/overly-narrow coverage across the entire noise grid (curves consistently below diagonal, calibration fraction ~28% at moderate noise vs 50% expected), with OOD error bars 2–3× wider than self-consistent. Ωm remains near 50% except a mild, non-severe deviation at the lowest noise.

</details>

<details>
<summary>zPk0+zPk2+zPk4, k&lt;0.2</summary>

<table>
<tr>
<td><img width="400" src="figures/zPk0_zPk2_zPk4_kmin-0.0_kmax-0.2/coverage_Om.jpg" /></td>
<td><img width="400" src="figures/zPk0_zPk2_zPk4_kmin-0.0_kmax-0.2/coverage_s8.jpg" /></td>
</tr>
<tr>
<td><img width="400" src="figures/zPk0_zPk2_zPk4_kmin-0.0_kmax-0.2/pred_Om.jpg" /></td>
<td><img width="400" src="figures/zPk0_zPk2_zPk4_kmin-0.0_kmax-0.2/pred_s8.jpg" /></td>
</tr>
</table>

At lowest noise, both Ωm and σ8 coverage curves sit above the diagonal (overprediction); bias diminishes rapidly with increasing noise and converges to self-consistent behavior by high noise. The symmetric, noise-dependent pattern is distinct from CHARM devoxelization bias, which would be expected to persist across noise levels.

</details>

<details>
<summary>zPk0+zPk2+zPk4, k&lt;0.4</summary>

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

At low noise (σ_rad=0, σ_tran≤1.5), Ωm is overpredicted while σ8 is underpredicted — opposite-sign biases localized to the low-noise region and not present at higher noise. At n24 (moderate noise), median coverage is 44.9% for Ωm and 59.4% for σ8, both diverging from well-calibrated self-consistent performance.

</details>

<details>
<summary>zPk0+zPk2+zPk4, k&lt;0.6</summary>

<table>
<tr>
<td><img width="400" src="figures/zPk0_zPk2_zPk4_kmin-0.0_kmax-0.6/coverage_Om.jpg" /></td>
<td><img width="400" src="figures/zPk0_zPk2_zPk4_kmin-0.0_kmax-0.6/coverage_s8.jpg" /></td>
</tr>
<tr>
<td><img width="400" src="figures/zPk0_zPk2_zPk4_kmin-0.0_kmax-0.6/pred_Om.jpg" /></td>
<td><img width="400" src="figures/zPk0_zPk2_zPk4_kmin-0.0_kmax-0.6/pred_s8.jpg" /></td>
</tr>
</table>

Systematic opposite-direction bias across the entire noise grid: Ωm consistently underpredicted (coverage ~40%) and σ8 consistently overpredicted (coverage ~10%), persisting uniformly from zero noise through the highest noise bin. Self-consistent residuals remain centered at zero, indicating a noise-independent train/test offset rather than noise-driven miscalibration.

</details>

<details>
<summary>zPk0+zPk2+zPk4+zBk0, zPk&lt;0.2/zBk&lt;0.2</summary>

<table>
<tr>
<td><img width="400" src="figures/zPk0_zPk2_zPk4_zBk0_kmin-0.0_kmax-zBk=0.2__zPk=0.2/coverage_Om.jpg" /></td>
<td><img width="400" src="figures/zPk0_zPk2_zPk4_zBk0_kmin-0.0_kmax-zBk=0.2__zPk=0.2/coverage_s8.jpg" /></td>
</tr>
<tr>
<td><img width="400" src="figures/zPk0_zPk2_zPk4_zBk0_kmin-0.0_kmax-zBk=0.2__zPk=0.2/pred_Om.jpg" /></td>
<td><img width="400" src="figures/zPk0_zPk2_zPk4_zBk0_kmin-0.0_kmax-zBk=0.2__zPk=0.2/pred_s8.jpg" /></td>
</tr>
</table>

Low-noise configurations (σ_rad, σ_tran < 1.5) drive systematic overprediction in both Ωm and σ8, Ωm more strongly and persistently than σ8, peaking at zero noise — consistent with CHARM devoxelization bias. Bias decreases monotonically with noise; by n24 coverage fractions are near nominal, and OOD tracks or falls below self-consistent at higher noise.

</details>

<details>
<summary>zPk0+zPk2+zPk4+zBk0, zPk&lt;0.4/zBk&lt;0.2</summary>

<table>
<tr>
<td><img width="400" src="figures/zPk0_zPk2_zPk4_zBk0_kmin-0.0_kmax-zBk=0.2__zPk=0.4/coverage_Om.jpg" /></td>
<td><img width="400" src="figures/zPk0_zPk2_zPk4_zBk0_kmin-0.0_kmax-zBk=0.2__zPk=0.4/coverage_s8.jpg" /></td>
</tr>
<tr>
<td><img width="400" src="figures/zPk0_zPk2_zPk4_zBk0_kmin-0.0_kmax-zBk=0.2__zPk=0.4/pred_Om.jpg" /></td>
<td><img width="400" src="figures/zPk0_zPk2_zPk4_zBk0_kmin-0.0_kmax-zBk=0.2__zPk=0.4/pred_s8.jpg" /></td>
</tr>
</table>

σ8 is systematically overpredicted at low noise (σ_rad, σ_tran ≤ 1.5), with Ωm remaining better calibrated across the grid (mild underprediction only at lowest noise). Bias attenuates and OOD aligns with self-consistent at σ_rad, σ_tran ≥ 1.5, a pattern consistent with CHARM devoxelization bias amplified at low noise.

</details>

<details>
<summary>zPk0+zPk2+zPk4+zBk0, zPk&lt;0.6/zBk&lt;0.2</summary>

<table>
<tr>
<td><img width="400" src="figures/zPk0_zPk2_zPk4_zBk0_kmin-0.0_kmax-zBk=0.2__zPk=0.6/coverage_Om.jpg" /></td>
<td><img width="400" src="figures/zPk0_zPk2_zPk4_zBk0_kmin-0.0_kmax-zBk=0.2__zPk=0.6/coverage_s8.jpg" /></td>
</tr>
<tr>
<td><img width="400" src="figures/zPk0_zPk2_zPk4_zBk0_kmin-0.0_kmax-zBk=0.2__zPk=0.6/pred_Om.jpg" /></td>
<td><img width="400" src="figures/zPk0_zPk2_zPk4_zBk0_kmin-0.0_kmax-zBk=0.2__zPk=0.6/pred_s8.jpg" /></td>
</tr>
</table>

σ8 is persistently overpredicted across the whole noise grid, most severe at low noise (coverage approaching 1.0 at zero noise). Ωm shows small deviation at zero noise that converges to the diagonal at higher noise. The strong low-noise concentration of σ8 bias with weaker Ωm involvement is described as consistent with CHARM devoxelization bias.

</details>

<details>
<summary>zPk0+zPk2+zPk4+zEqBk0, zPk&lt;0.2/zBk&lt;0.2</summary>

<table>
<tr>
<td><img width="400" src="figures/zPk0_zPk2_zPk4_zEqBk0_kmin-0.0_kmax-zBk=0.2__zPk=0.2/coverage_Om.jpg" /></td>
<td><img width="400" src="figures/zPk0_zPk2_zPk4_zEqBk0_kmin-0.0_kmax-zBk=0.2__zPk=0.2/coverage_s8.jpg" /></td>
</tr>
<tr>
<td><img width="400" src="figures/zPk0_zPk2_zPk4_zEqBk0_kmin-0.0_kmax-zBk=0.2__zPk=0.2/pred_Om.jpg" /></td>
<td><img width="400" src="figures/zPk0_zPk2_zPk4_zEqBk0_kmin-0.0_kmax-zBk=0.2__zPk=0.2/pred_s8.jpg" /></td>
</tr>
</table>

Overprediction increases with transverse noise (σ_tran) for both parameters, strongest in σ8 (deviation exceeding tolerance at σ_tran ≥ 2.26; median coverage 62.8% vs 50.1% self-consistent at σ_rad=σ_tran=2.26). Ωm stays closer to the diagonal but still drifts upward at high σ_tran. Radial noise has little effect; the trend is driven by the transverse component.

</details>

<details>
<summary>zPk0+zPk2+zPk4+zEqBk0, zPk&lt;0.4/zBk&lt;0.2</summary>

<table>
<tr>
<td><img width="400" src="figures/zPk0_zPk2_zPk4_zEqBk0_kmin-0.0_kmax-zBk=0.2__zPk=0.4/coverage_Om.jpg" /></td>
<td><img width="400" src="figures/zPk0_zPk2_zPk4_zEqBk0_kmin-0.0_kmax-zBk=0.2__zPk=0.4/coverage_s8.jpg" /></td>
</tr>
<tr>
<td><img width="400" src="figures/zPk0_zPk2_zPk4_zEqBk0_kmin-0.0_kmax-zBk=0.2__zPk=0.4/pred_Om.jpg" /></td>
<td><img width="400" src="figures/zPk0_zPk2_zPk4_zEqBk0_kmin-0.0_kmax-zBk=0.2__zPk=0.4/pred_s8.jpg" /></td>
</tr>
</table>

σ8 is underpredicted (coverage curves above diagonal) at low-to-moderate noise (σ_rad ≤ 2.26), with OOD coverage 58.9% vs 53.1% self-consistent at the representative noise bin; Ωm remains well-calibrated throughout. The bias attenuates at high noise (σ_rad ≥ 3.0) as posteriors widen, though the coverage-curve offset persists.

</details>

<details>
<summary>zPk0+zPk2+zPk4+zEqBk0, zPk&lt;0.4/zBk&lt;0.4</summary>

<table>
<tr>
<td><img width="400" src="figures/zPk0_zPk2_zPk4_zEqBk0_kmin-0.0_kmax-zBk=0.4__zPk=0.4/coverage_Om.jpg" /></td>
<td><img width="400" src="figures/zPk0_zPk2_zPk4_zEqBk0_kmin-0.0_kmax-zBk=0.4__zPk=0.4/coverage_s8.jpg" /></td>
</tr>
<tr>
<td><img width="400" src="figures/zPk0_zPk2_zPk4_zEqBk0_kmin-0.0_kmax-zBk=0.4__zPk=0.4/pred_Om.jpg" /></td>
<td><img width="400" src="figures/zPk0_zPk2_zPk4_zEqBk0_kmin-0.0_kmax-zBk=0.4__zPk=0.4/pred_s8.jpg" /></td>
</tr>
</table>

Intermediate noise (σ_rad, σ_tran ~ 1.5–2.26) drives the strongest bias: Ωm underpredicted (median coverage 46.4% at σ_rad=σ_tran=2.26), σ8 overpredicted (58.5%), with both deviations exceeding tolerance and persisting across several intermediate noise pairs. OOD curves deviate from self-consistent curves by more than the OOD uncertainty bands, indicating a genuine OOD penalty rather than sampling variance.

</details>

<details>
<summary>zPk0+zPk2+zPk4+zEqBk0, zPk&lt;0.6/zBk&lt;0.2</summary>

<table>
<tr>
<td><img width="400" src="figures/zPk0_zPk2_zPk4_zEqBk0_kmin-0.0_kmax-zBk=0.2__zPk=0.6/coverage_Om.jpg" /></td>
<td><img width="400" src="figures/zPk0_zPk2_zPk4_zEqBk0_kmin-0.0_kmax-zBk=0.2__zPk=0.6/coverage_s8.jpg" /></td>
</tr>
<tr>
<td><img width="400" src="figures/zPk0_zPk2_zPk4_zEqBk0_kmin-0.0_kmax-zBk=0.2__zPk=0.6/pred_Om.jpg" /></td>
<td><img width="400" src="figures/zPk0_zPk2_zPk4_zEqBk0_kmin-0.0_kmax-zBk=0.2__zPk=0.6/pred_s8.jpg" /></td>
</tr>
</table>

σ8 underprediction (coverage curves above diagonal) is consistent across the entire noise grid, most pronounced at low-to-mid noise; at moderate noise only 7.2% of OOD residuals fall within threshold vs 52.7% self-consistent. Ωm calibration remains acceptable (deviations within tolerance) except a mild drift at the lowest noise. The persistence across the whole grid indicates a systematic domain-transfer effect rather than a noise-specific one.

</details>

<details>
<summary>zPk0+zPk2+zPk4+zSqBk0, zPk&lt;0.2/zBk&lt;0.2</summary>

<table>
<tr>
<td><img width="400" src="figures/zPk0_zPk2_zPk4_zSqBk0_kmin-0.0_kmax-zBk=0.2__zPk=0.2/coverage_Om.jpg" /></td>
<td><img width="400" src="figures/zPk0_zPk2_zPk4_zSqBk0_kmin-0.0_kmax-zBk=0.2__zPk=0.2/coverage_s8.jpg" /></td>
</tr>
<tr>
<td><img width="400" src="figures/zPk0_zPk2_zPk4_zSqBk0_kmin-0.0_kmax-zBk=0.2__zPk=0.2/pred_Om.jpg" /></td>
<td><img width="400" src="figures/zPk0_zPk2_zPk4_zSqBk0_kmin-0.0_kmax-zBk=0.2__zPk=0.2/pred_s8.jpg" /></td>
</tr>
</table>

σ8 underprediction (coverage above diagonal, ~58.5% at σ_rad=σ_tran=2.26) is present across most noise, strongest at high transverse noise (σ_tran > 0.75). Ωm stays near nominal across the same range but shows overprediction inverting to a mild deviation at the highest noise corner (σ_rad ≥ 3.76). σ8 bias exceeds self-consistent bias across intermediate-to-high noise.

</details>

<details>
<summary>zPk0+zPk2+zPk4+zSqBk0, zPk&lt;0.4/zBk&lt;0.2</summary>

<table>
<tr>
<td><img width="400" src="figures/zPk0_zPk2_zPk4_zSqBk0_kmin-0.0_kmax-zBk=0.2__zPk=0.4/coverage_Om.jpg" /></td>
<td><img width="400" src="figures/zPk0_zPk2_zPk4_zSqBk0_kmin-0.0_kmax-zBk=0.2__zPk=0.4/coverage_s8.jpg" /></td>
</tr>
<tr>
<td><img width="400" src="figures/zPk0_zPk2_zPk4_zSqBk0_kmin-0.0_kmax-zBk=0.2__zPk=0.4/pred_Om.jpg" /></td>
<td><img width="400" src="figures/zPk0_zPk2_zPk4_zSqBk0_kmin-0.0_kmax-zBk=0.2__zPk=0.4/pred_s8.jpg" /></td>
</tr>
</table>

σ8 is overpredicted across the noise grid (coverage ~60–62% vs 50% expected), driven mainly by low-to-moderate noise (σ_rad ≤ 2.26); Ωm remains near nominal. The OOD–self gap is much wider for σ8 (62% vs 53% self-consistent) than Ωm (47% vs 51%) at moderate noise, and the bias persists from zero noise through the full grid with no immune configuration.

</details>

<details>
<summary>zPk0+zPk2+zPk4+zSqBk0, zPk&lt;0.6/zBk&lt;0.2</summary>

<table>
<tr>
<td><img width="400" src="figures/zPk0_zPk2_zPk4_zSqBk0_kmin-0.0_kmax-zBk=0.2__zPk=0.6/coverage_Om.jpg" /></td>
<td><img width="400" src="figures/zPk0_zPk2_zPk4_zSqBk0_kmin-0.0_kmax-zBk=0.2__zPk=0.6/coverage_s8.jpg" /></td>
</tr>
<tr>
<td><img width="400" src="figures/zPk0_zPk2_zPk4_zSqBk0_kmin-0.0_kmax-zBk=0.2__zPk=0.6/pred_Om.jpg" /></td>
<td><img width="400" src="figures/zPk0_zPk2_zPk4_zSqBk0_kmin-0.0_kmax-zBk=0.2__zPk=0.6/pred_s8.jpg" /></td>
</tr>
</table>

σ8 is severely overpredicted at every noise level (residual mean ≈ +0.08 at n24), with wide error bars but a bias that does not shrink with noise, indicating an OOD generalization issue rather than a noise-driven effect. Ωm is mildly underpredicted at low noise, consistent with CHARM devoxelization bias, and resolves by σ_rad/σ_tran ≥ 2.26.

</details>
