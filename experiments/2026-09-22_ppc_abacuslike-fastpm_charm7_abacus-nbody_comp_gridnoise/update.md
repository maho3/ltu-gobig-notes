# Posterior predictive check: `abacuslike/fastpm_charm7_cosmoHOD` against an Abacus N-body observation (zPk024, kmax=0.4)

**Date**: 2026-09-22
**Type**: Miscellaneous / posterior predictive check
**Train**: abacuslike fastpm_charm7_cosmoHOD, L=2000 Mpc/h, N=256, z=0.5 (a=0.66666); posterior and forward chain both from this suite
**Test**: abacus nbody_comp_gridnoise, lhid 38 = `AbacusSummit_base_c018_ph000` ("MultiDark Planck"), LCDM with Mnu=0, L=2000 Mpc/h, `hod00001_noise000008.h5` (σ_rad = σ_tran = 0.75175)
**Notes**: Out-of-distribution: only the observation moves, the posterior, the forward chain and the quantile reference pool stay the training suite's. 100 joint draws from q(θ|x_obs), all 100 collected with cosmology, HOD and noise verified against the draw to 1e-5. Residuals are element-wise between resimulated and observed feature vectors. Same train/test pair as the 2026-08-20 OOD inference run.

---

## Setup

- Posterior: 10-net lampe/NPE ensemble at
  `abacuslike/fastpm_charm7_cosmoHOD/models/galaxy/zPk0+zPk2+zPk4/kmin-0.0_kmax-0.4`,
  `include_hod=True`, `include_noise=True`, `correct_shot=True`. 17 parameters
  (5 cosmology, 10 HOD, 2 noise); x is 117-dimensional (3 blocks of 39 k bins).
- Observed cosmology [0.30709, 0.04821, 0.6777, 0.96, 0.81971]. x_obs is
  preprocessed by the Abacus suite's own run; the k-grid, shot correction and
  log-linear settings match the training suite.
- One draw = one FastPM box (L=2000, N=256) through CHARM charm7, `apply_hod`
  and `cmass.diagnostics.summ`, with its own IC phase. No draw was rejected or
  dropped.

## Data-space bands

<img width="900" src="figures/ppc_bands.png" />

Fraction of bins where the observed value falls outside the predictive
interval. Bins within a summary are strongly correlated, so these are a
description of the figure rather than a test; median |z| is the median
residual in units of the 68% half-width.

| Block | Bins | Outside 68% | Outside 95% | Median (PPC − obs) | Median \|z\| |
|---|---|---|---|---|---|
| zPk0 (inference) | 39 | 54% | 36% | +0.009 | 1.23 |
| zPk2 (inference) | 39 | 18% | 3% | −0.005 | 0.59 |
| zPk4 (inference) | 39 | 31% | 8% | +0.004 | 0.64 |
| zBk0 (held out) | 125 | 70% | 46% | +0.019 | 1.33 |
| zEqBk0 (held out) | 10 | 70% | 50% | +0.023 | 1.47 |
| zSqBk0 (held out) | 45 | 80% | 42% | +0.019 | 1.33 |
| zBk2 (held out) | 125 | 63% | 37% | +0.024 | 1.42 |
| zQk0 (held out) | 125 | 83% | 68% | −0.003 | 3.10 |
| zQk2 (held out) | 125 | 63% | 37% | +0.024 | 1.42 |

- The predictive ensemble sits systematically above the observed zPk0 at every
  k: median offset +0.009 in signed log10 P0, i.e. the predicted P0 is high by
  +1.5% to +3.4% over 0.1 < k < 0.35 and by +4.8% at the lowest bin (k=0.016).
  The offset is worst over 0.2 < k < 0.3, where all 10 bins fall outside the
  68% band at a median 2.3σ; it relaxes to 1.1σ over 0.3 < k < 0.4 and to
  0.3σ over 0.05 < k < 0.1. The 68% half-width at k=0.2 is 0.007 dex, so the
  bands are tight enough that a sub-percent systematic exceeds them.
- zPk2 is the best-recovered conditioned block (median |z| = 0.59, no bin
  beyond 1.6σ). The largest single residual is −0.104 in P2/P0 at the lowest
  bin, k=0.016, where the band is ~0.11 wide (0.9σ).
- zPk4 agrees within 0.4σ over k > 0.2 but runs high at low k: +0.059 median
  residual in P4/P0 over k < 0.05, peaking at +0.125 (1.6σ) at k=0.026.
- The held-out bispectra all run high by a similar amount to zPk0 and more
  consistently: zBk0 +4.5% in B0 (median over 125 triangles, range −2% to
  +13%), zEqBk0 +5.5%, zSqBk0 +4.5%. The offset grows with triangle index
  across zBk0 and zSqBk0 — near zero for the first ~20 triangles, ~+0.04 dex
  by index 100 — and with k in zEqBk0, from ~0 at k=0.05 to +0.05 at k=0.27.
- zBk2 sits +0.024 above the observed B2/B0 across the triangle set, with a
  +0.13 spike at the first triangle index; 63% of bins are outside 68%.
  `zQk2` is numerically identical to `zBk2` (Q2/Q0 ≡ B2/B0), so that panel is
  a duplicate rather than an independent check.
- zQk0 is the tightest block and the most-exceeded one: the residual is only
  −0.003 dex (−0.7% in Q0) but the 68% half-width is 0.0009 dex, so 83% of
  bins land outside 68% and 68% outside 95%, at a median 3.1σ and up to 13σ.
  It is the one block where the PPC is systematically low rather than high.
- The predictive bands are far narrower than the training pool's 95% range on
  all three conditioned blocks: at k=0.4 the pool spans ~1.5 in P2/P0 and
  ~1.6 in P4/P0, against ~0.03 and ~0.04 for the predictive 68% band.

## Formal p-values

Added 2026-09-24 after the matched leave-one-out tests were implemented (see `ltu-cmass/ppc/README.md`). The null hypothesis is that x_obs is a draw from the posterior predictive; p is floored at 1/(N+1) = 0.0099 for N = 100, so a value at the floor means only "more extreme than every draw". Inference blocks reuse x_obs for fitting, so their p is conservative; held-out blocks are a clean test.

<img width="900" src="figures/ppc_pcapvalue.png" />

- In the top-10 PCA space the conditioned vector passes (p = 0.67 ± 0.05, Hotelling p_F = 0.81) but the held-out vector fails (p = 0.020 ± 0.010, p_F = 2.1e-3). All 555 held-out features together, and every held-out block individually, sit at p = 0.0099-0.020 (zBk0, zQk0, zEqBk0, zSqBk0 at the floor; zBk2 and zQk2 at 0.020). Hotelling p_F ranges from 1.3e-3 (zBk2, zQk2) to 5e-11 (zBk0) and 2e-10 (zQk0); it is a Gaussian extrapolation and ranks the failures only.
- Among the conditioned blocks, zPk0 fails on its own (p = 0.020, p_F = 0.017), while zPk2 (0.96) and zPk4 (0.55) pass. The zPk0 deviation orthogonal to the top-10 PCs is at the floor (0.0099), as are those of zBk0, zQk0, zSqBk0 and the held-out vector as a whole (0.020).
- The all-feature Ledoit-Wolf test fails the conditioned vector at the floor (p = 0.0099) although the PCA test gives 0.67. x_obs is therefore in a direction the posterior draws do not reach, while lying inside the cloud along the directions they do vary in. Every held-out block is also at 0.0099-0.020 in Ledoit-Wolf.
- Panel (e) shows the held-out verdicts are not tuned to k = 10: zBk0, zSqBk0 and zEqBk0 are at or near the floor from k ≈ 3 PCs kept, and zBk2/zQk2 from k ≈ 7-9, and they stay there out to k = 30. The zPk0 verdict reaches the floor for k ≥ 11.

<img width="900" src="figures/ppc_kbinpvalue.png" />

- In k-bin subsets the failure builds with kmax in zPk0: the cumulative p is 0.16 at kmax = 0.16, 0.09 at 0.20, and at the floor for every kmax ≥ 0.24. The combined P(k) vector reaches p ≈ 0.07 at kmax = 0.24, ≈ 0.2 at 0.28-0.32 and the floor at 0.36 and 0.40. zPk2 stays at p ≥ 0.9 throughout and zPk4 at p ≥ 0.15.
- Sliding windows on zPk0 peak at p ≈ 0.02 (0.19 ≤ k < 0.25) and the combined multipoles at p ≈ 0.03 (most OOD window: p = 0.030 ± 0.014); the windowed P(k) tests do not reach the floor, unlike the cumulative ones.
- The per-bin deviation (x_obs − mean)/σ on zPk0 is −0.5σ to −1σ for k < 0.15, sits at −1.5σ to −2.8σ over 0.16 < k < 0.32 (worst −2.8σ near k = 0.24) and returns to ~−0.5σ at k = 0.4. zPk2 runs +0.5σ to +1.5σ above k = 0.15. zPk4 has isolated bins at −2.0σ (k ≈ 0.1) and −2.4σ (k ≈ 0.19). The sign of zPk0 is that seen in the band figure, the predictive ensemble sitting above x_obs.
- The bispectra reach the floor at small subsets: zQk0 in the cumulative scan by kmax ≈ 0.15 (13 triangles), zBk0, zEqBk0 and zSqBk0 by kmax = 0.20 (22 triangles, 5 and 10 bins respectively). zBk0 and zQk0 are not tested beyond kmax = 0.3 because d exceeds N/2 = 50. This is consistent with the "systematically high, more consistently than zPk0" reading of the bispectrum bands above.

## Parameter space

The drawn parameters are direct posterior samples by construction, so these
figures check the campaign bookkeeping rather than the model.

<img width="900" src="figures/ppc_corner.png" />

- The 100 simulated vectors tile the direct 5000-sample posterior in all 17
  parameters with no visible offset in any 1D or 2D projection, so nothing
  drifted between drawing and simulating.
- Against the true values of the Abacus point, Ωm and σ8 are recovered
  (z = −0.2 and +1.2 on the marginals); the largest cosmology offset is h,
  0.613 (+0.096/−0.081) against 0.678. HOD offsets are larger, logMmin
  11.97 (+0.34/−0.26) against 12.73 being the most discrepant. The two noise
  parameters are recovered high (noise_transverse 1.61 ± 0.06 against 0.752),
  as expected when the training and testing suites carry different intrinsic
  noise in their forward models.

<img width="700" src="figures/ppc_logprob.png" />

- The log-posterior-density histogram of the 100 simulated vectors overlaps
  the direct 5000-sample histogram. The ESS and max-weight annotations and the
  "importance-sampled data" legend label are inherited from the
  importance-sampling figure this reuses and are vacuous for an unweighted
  ensemble (ESS = N, max weight = 1/N by construction).
