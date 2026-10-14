# Posterior predictive check: `abacuslike/fastpm_charm7_cosmoHOD_reparam` against a noise-free Abacus observation, seven inference configurations

**Date**: 2026-10-02
**Type**: Miscellaneous / posterior predictive check
**Train**: abacuslike fastpm_charm7_cosmoHOD_reparam (`infer.reparam_degeneracy=True`), L=2000 Mpc/h, N=256, z=0.5; 10-net lampe/NPE ensembles; posterior, forward chain and quantile reference pool all from this suite
**Test**: abacus nbody_comp_gridnoise_reparam, lhid 38 = `AbacusSummit_base_c018_ph000` (LCDM, Mν=0), `hod00001_noise000000.h5`, i.e. σ_rad = σ_tran = 0. True [Ωm, Ωb, h, n_s, σ8] = [0.3071, 0.0482, 0.6777, 0.960, 0.8197]
**Notes**: Out-of-distribution. Seven campaigns, one per inference configuration, each with 50 joint draws from q(θ|x_obs), resimulated through FastPM → CHARM charm7 (`charm_joint_v19.pth`, on DeltaAI) → `apply_hod` → `cmass.diagnostics.summ`. All 7 × 50 draws were collected, with cosmology, HOD and noise verified against the draw. Two zPk024 kmax=0.3 draws (ids 34, 35) had their stage-C jobs cancelled by SLURM and were rerun. With N = 50 the p-value floor is 1/(N+1) = 0.020, and the Monte Carlo error is ±0.06–0.07 near p = 0.5. The draws were inverted from (degen_r, degen_phi) to physical (eta_vb_centrals, noise_radial) before simulation; 4 zPk0 kmax=0.3 draws were rejected for falling outside the physical prior box and redrawn. x_obs comes from the Abacus suite re-preprocessed with `reparam_degeneracy=True`, `test_frac=1` (see the 2026-10-01 OOD note). Same observed lhid as the 2026-09-22 PPC, but at noise (0, 0) instead of (0.75, 0.75).

---

## Setup

| Campaign | Conditioned on | Cut | D (cond.) | D (held out) |
|---|---|---|---|---|
| zPk0k02 | zPk0 | k<0.2 | 19 | 141 |
| zPk0k03 | zPk0 | k<0.3 | 29 | 286 |
| zPk024k02 | zPk0+zPk2+zPk4 | k<0.2 | 57 | 103 |
| zPk024k03 | zPk0+zPk2+zPk4 | k<0.3 | 87 | 228 |
| zPk024k04 | zPk0+zPk2+zPk4 | k<0.4 | 117 | 555 |
| zPk024zBk0k02 | zPk0+zPk2+zPk4+zBk0 | zPk<0.2, zBk<0.2 | 79 | 81 |
| zPk024zBk0k03 | zPk0+zPk2+zPk4+zBk0 | zPk<0.3, zBk<0.3 | 137 | 178 |

Held-out blocks are cut at the campaign's own kmax (the zBk cut where one exists), so the held-out bispectrum has 22 triangles at 0.2, 50 at 0.3 and 125 at 0.4. The kmax=0.3 models were trained with fewer Optuna trials than the others (~57–77 against ~170; see the 2026-10-01 OOD note).

## Overview

| Campaign | cond. PCA | cond. Ledoit-Wolf | held-out PCA | held-out Ledoit-Wolf | held-out blocks at the PCA floor |
|---|---|---|---|---|---|
| zPk0k02 | 0.73 | 1.00 | 0.63 | 0.20 | none (lowest zQk0 0.06) |
| zPk0k03 | 0.94 | 1.00 | 0.41 | 0.43 | none (lowest zQk0 0.16) |
| zPk024k02 | 0.82 | 0.96 | 0.57 | 0.39 | none (lowest zQk0 0.10) |
| zPk024k03 | 0.75 | 0.78 | 0.10 | **0.020** | zBk0, zQk0, zSqBk0 |
| zPk024k04 | 0.75 | **0.039** | **0.020** | **0.020** | all six |
| zPk024zBk0k02 | 0.76 | 0.20 | 0.39 | 0.08 | zSqBk0 |
| zPk024zBk0k03 | 0.69 | 0.14 | 0.31 | 0.039 | zQk0, zSqBk0 |

- The P(k)-only posteriors at kmax 0.2, and zPk0 at 0.3, pass every test. Conditioned PCA p is 0.73–0.94 with Ledoit-Wolf 0.96–1.00. Held-out PCA p is 0.41–0.63, and no individual block falls below 0.06. Their held-out Ledoit-Wolf p is 0.20–0.43.

- zPk024 at kmax 0.4 fails as in the 2026-09-22 PPC, although the observation is now noise-free:
  - The conditioned vector passes in PCA (0.75) but fails Ledoit-Wolf (0.039). zPk0 alone, and its deviation orthogonal to the top-10 PCs, are at the floor (0.020).
  - Every held-out block is at the floor in PCA, Ledoit-Wolf and the orthogonal residual. Hotelling p_F ranges from 3e-3 (zBk2) to 1.2e-7 (zQk0) and 4e-7 (zBk0).
  - Panel (e) shows the held-out failure holds from k ≈ 3 PCs kept onward.

<img width="900" src="figures/zPk024k04/ppc_pcapvalue.png" />

- In the cumulative k-bin scan, the kmax=0.4 posterior fails on zPk0 for every kmax ≥ 0.24 (p at the floor). The zPk024 kmax=0.3 posterior does not fail on the same scales: zPk0 p = 0.24 at kmax 0.32, and the combined multipoles 0.65.
  - For the kmax 0.4 campaign, zPk0 has per-bin deviations (x_obs − mean)/σ of −1.5σ to −3σ over 0.17 < k < 0.32. The predictive median sits above x_obs, by +0.013 dex (+3.0%) in P0 over 0.2 < k < 0.3.
  - The same P0 offset is +1.1% for the zPk024 kmax 0.3 posterior and +0.1% for zPk0 at 0.3.

<img width="900" src="figures/zPk024k04/ppc_kbinpvalue.png" />

<img width="900" src="figures/zPk024k03/ppc_kbinpvalue.png" />

- zPk024 at kmax 0.3 passes on the conditioned P(k) but fails on the held-out bispectrum, in zBk0 (PCA 0.020, p_F = 0.018), zQk0 (p_F = 1.7e-4) and zSqBk0. Its cumulative scans show the failure only at the 22-triangle step (zQk0 at kmax 0.2: p = 0.020). The equilateral and B2 blocks pass (0.27 and 0.55).

- Tested on the same 22 triangles (the cumulative scan's zBk ≤ 0.2 step), the held-out bispectrum fails only for zPk024 at kmax 0.4 and, partly, zPk024 at 0.3:

  | 22-triangle cumulative p (k ≤ 0.2) | zPk0k02 | zPk0k03 | zPk024k02 | zPk024k03 | zPk024k04 |
  |---|---|---|---|---|---|
  | zBk0 | 0.18 | 0.35 | 0.12 | 0.20 | 0.020 |
  | zQk0 | 0.08 | 0.16 | 0.10 | 0.020 | 0.020 |
  | zSqBk0 (10 triangles) | 0.10 | 0.35 | 0.12 | 0.08 | 0.020 |

  For the P(k)-only campaigns, the held-out bispectrum fails at a fixed triangle set as the conditioned zPk024 cut grows from 0.3 to 0.4, but not as zPk0's cut grows from 0.2 to 0.3.

- Conditioning on zBk0 does not make the bispectrum fit:
  - zBk0 itself is at the Ledoit-Wolf floor at {0.2, 0.2}, and at the PCA, Ledoit-Wolf and residual floors at {0.3, 0.3} (p_F = 1.3e-3).
  - The held-out zSqBk0 is at or near the floor in both (PCA 0.020, p_F = 0.002 and 0.006), and zQk0 joins it at {0.3, 0.3}.
  - In the {0.3, 0.3} bands, the predictive B0 sits above x_obs everywhere, by a median +0.026 dex, rising with triangle index to ~+0.05 dex. 58% of zBk0 bins and 67% of zSqBk0 bins lie outside the 68% band. P0 is high by +2.5% over 0.2 < k < 0.3.

<img width="900" src="figures/zPk024zBk0k03/ppc_bands.png" />

- The direction of the bispectrum mismatch is the same in all seven campaigns and matches the 2026-09-22 note. The predictive median sits above the observed B0 by +0.012 to +0.028 dex (zBk0) and +0.016 to +0.039 dex (zEqBk0), growing with k or triangle index. It sits below the observed Q0 by −0.001 to −0.004 dex, against a 68% half-width of only ~0.002–0.003 dex. These offsets exceed the bands (fails the tests) only at the larger cuts.

<img width="900" src="figures/zPk024k04/ppc_bands.png" />

- zPk2 passes in every campaign, whether conditioned or held out (PCA 0.86–0.98). zPk4 passes too (0.41–0.92), with its largest residual at k < 0.05 (median +0.006 to +0.023 in P4/P0).

## Parameter space

<img width="900" src="figures/zPk024k04/ppc_corner.png" />

- In every corner plot the 50 simulated parameter vectors fall inside the direct 5000-sample posterior. Nothing drifted between drawing and simulating.
- Cosmology is recovered within ~1σ of the draw spread in Ωm: medians 0.299–0.310, against 0.307. σ8 medians are 0.832–0.849 (spread 0.017–0.077), +0.4 to +1.3σ above the true 0.820, except zPk0 at 0.3 (0.915 ± 0.074).
- h is lowest for zPk024 at kmax 0.4: 0.555 ± 0.059 against 0.678. The other campaigns give 0.651–0.726.
- logMmin is recovered by the P(k)-only posteriors at 0.2 and 0.3 (12.55–12.72 against 12.73). It is pulled low when the posterior is conditioned on zPk at 0.4 (12.11) or on zBk0 (12.24 and 11.97). The 2026-09-28 note traces a similar low logMmin to CHARM's mass function near its 10^12.7 floor.
- noise_transverse is inferred at 1.46–1.88 (spread 0.04–0.19) for every zPk024 posterior, against a true 0. That is consistent with the ~1.41 Mpc/h CHARM offset in the 2026-09-28 note. For zPk0 alone it is 1.19–1.80, with spreads of 0.7–1.0.

<img width="700" src="figures/zPk024k04/ppc_logprob.png" />

- The log-posterior-density histograms of the 50 resimulated vectors overlap the direct-sample histograms. The ESS, max-weight and "importance-sampled data" annotations are inherited from the importance-sampling figure and hold trivially for an unweighted ensemble (ESS = N, max weight = 1/N).

## Caveats

- This is a single observation, one Abacus box at one noise level. The 2026-09-22 PPC used the same box at noise (0.75, 0.75), a non-reparam posterior and N = 100. The kmax=0.4 failure pattern agrees between the two, but the observation, the posterior and N all differ.
- Held-out blocks are tested at each campaign's own cut, so the held-out vectors have very different sizes (81–555 features). The 22-triangle cumulative table above is the like-for-like comparison.
- The kmax=0.3 models had fewer Optuna trials than the others (~57–77 completed against ~170), and their Abacus posteriors are wider in Ωm (2026-10-01 note). Some of the zPk024 kmax=0.3 pass may come from that extra width.
- With N = 50, p differences below ~0.07 are not significant, and p at 0.020 means only "more extreme than all 50 draws".

## Additional figures

Remaining figures per campaign: bands, corner, logprob and both p-value figures.

<details>
<summary>zPk0, k&lt;0.2</summary>

<img width="900" src="figures/zPk0k02/ppc_bands.png" />
<img width="900" src="figures/zPk0k02/ppc_pcapvalue.png" />
<img width="900" src="figures/zPk0k02/ppc_kbinpvalue.png" />
<img width="700" src="figures/zPk0k02/ppc_corner.png" />
<img width="500" src="figures/zPk0k02/ppc_logprob.png" />

</details>

<details>
<summary>zPk0, k&lt;0.3</summary>

<img width="900" src="figures/zPk0k03/ppc_bands.png" />
<img width="900" src="figures/zPk0k03/ppc_pcapvalue.png" />
<img width="900" src="figures/zPk0k03/ppc_kbinpvalue.png" />
<img width="700" src="figures/zPk0k03/ppc_corner.png" />
<img width="500" src="figures/zPk0k03/ppc_logprob.png" />

</details>

<details>
<summary>zPk024, k&lt;0.2</summary>

<img width="900" src="figures/zPk024k02/ppc_bands.png" />
<img width="900" src="figures/zPk024k02/ppc_pcapvalue.png" />
<img width="900" src="figures/zPk024k02/ppc_kbinpvalue.png" />
<img width="700" src="figures/zPk024k02/ppc_corner.png" />
<img width="500" src="figures/zPk024k02/ppc_logprob.png" />

</details>

<details>
<summary>zPk024, k&lt;0.3</summary>

<img width="900" src="figures/zPk024k03/ppc_bands.png" />
<img width="900" src="figures/zPk024k03/ppc_pcapvalue.png" />
<img width="700" src="figures/zPk024k03/ppc_corner.png" />
<img width="500" src="figures/zPk024k03/ppc_logprob.png" />

</details>

<details>
<summary>zPk024+zBk0, zPk&lt;0.2, zBk&lt;0.2</summary>

<img width="900" src="figures/zPk024zBk0k02/ppc_bands.png" />
<img width="900" src="figures/zPk024zBk0k02/ppc_pcapvalue.png" />
<img width="900" src="figures/zPk024zBk0k02/ppc_kbinpvalue.png" />
<img width="700" src="figures/zPk024zBk0k02/ppc_corner.png" />
<img width="500" src="figures/zPk024zBk0k02/ppc_logprob.png" />

</details>

<details>
<summary>zPk024+zBk0, zPk&lt;0.3, zBk&lt;0.3</summary>

<img width="900" src="figures/zPk024zBk0k03/ppc_pcapvalue.png" />
<img width="900" src="figures/zPk024zBk0k03/ppc_kbinpvalue.png" />
<img width="700" src="figures/zPk024zBk0k03/ppc_corner.png" />
<img width="500" src="figures/zPk024zBk0k03/ppc_logprob.png" />

</details>
