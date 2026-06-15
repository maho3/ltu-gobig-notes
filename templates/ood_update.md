# <experiment tag>
**Date**: <YYYY-MM-DD>
**Type**: OOD inference
**Train**: <from config.md>
**Test**: <from config.md>
**Tracer**: <from config.md>
**Summaries**: <from config.md>
**kmax**: <from config.md>
**Notes**: <from config.md>

## Overview
- <high-level bullet: what works, what doesn't, dominant pattern>
- <bullet: which parameters are biased in which cells, and at what noise scales>
- <bullet: patterns across kmax or summary richness>
- ...

## Figures

### Overview

<details>
<summary>Median coverage — Ωm</summary>

<img width="900" src="figures/<filename>" />

</details>

<details>
<summary>Median coverage — σ8</summary>

<img width="900" src="figures/<filename>" />

</details>

### Flagged cells

<details>
<summary><label, e.g. zPk024_kmax0.4></summary>

<table>
<tr>
<td><img width="400" src="figures/<label>/coverage_Om.png" /></td>
<td><img width="400" src="figures/<label>/coverage_s8.png" /></td>
</tr>
<tr>
<td><img width="400" src="figures/<label>/pred_Om.png" /></td>
<td><img width="400" src="figures/<label>/pred_s8.png" /></td>
</tr>
</table>

</details>