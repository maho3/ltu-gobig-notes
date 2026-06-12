# <experiment tag>
**Date**: <YYYY-MM-DD>
**Type**: Self-consistent
**Suite**: <from config.md>
**Tracer**: <from config.md>
**kmax sweep summary**: <from config.md>
**kmax values**: <from config.md>
**Feature sweep kmax**: <from config.md>
**Feature sweep summaries**: <from config.md>
**Notes**: <from config.md>

## Overview
- <high-level bullet: constraining power trend, calibration status>
- <bullet>
- ...

## Findings

### kmax sweep — <summary label>
- <specific finding: where stdev plateaus, calibration breaks, etc.>
- <bullet>

### Feature sweep — kmax=<value>
- <specific finding: which summaries help, diminishing returns, etc.>
- <bullet>

### <flagged sweep if zoom-in warranted>
- ...

## Figures

### kmax sweep

<details>
<summary>kmax scaling</summary>

<img width="900" src="figures/model_scaling/kmax_sweep/kmax_scaling.png" />

</details>

<details>
<summary>Calibration</summary>

<img width="900" src="figures/model_scaling/kmax_sweep/calibration.png" />

</details>

### Feature sweep

<details>
<summary>Feature length scaling</summary>

<img width="900" src="figures/model_scaling/feature_sweep/feature_length_scaling.png" />

</details>

<details>
<summary>Calibration</summary>

<img width="900" src="figures/model_scaling/feature_sweep/calibration.png" />

</details>

### Zoom-ins

<details>
<summary><sweep label, e.g. kmax_sweep></summary>

<table>
<tr>
<td><img width="400" src="figures/model_scaling/<sweep>/stdev_vs_theta.png" /></td>
<td><img width="400" src="figures/model_scaling/<sweep>/fiducial_stdev.png" /></td>
</tr>
<tr>
<td><img width="400" src="figures/model_scaling/<sweep>/optuna_history.png" /></td>
<td></td>
</tr>
</table>

</details>
