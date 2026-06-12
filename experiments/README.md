# Experiments

| Date | Type | Train | Test | Notes | Update |
|------|------|-------|------|-------|--------|
| 2026-06-12 | OOD inference | quijotelike/fastpm_charm6 | quijote/nbody_hodz_gridnoise | CHARM devoxelization bias signature: Ωm biased-low at kmax=0.2 (zPk024 only, low noise); σ8 biased-high at kmax≥0.3 for bispectrum summaries; zPk024 most stable across grid | [update.md](2026-06-12_ood_quijotelike-fastpm_charm6_quijote-nbody_hodz_gridnoise/update.md) |
| 2026-06-12 | Self-consistent | quijotelike/fastpm_charm6 | — | Calibration holds across all kmax and summaries; Ωm stdev saturates by kmax=0.2; σ8 improves monotonically with bispectrum features (~3× from zPk0 to zPk024+EqBk0); Ωm feature scaling non-monotonic | [update.md](2026-06-12_self_quijotelike-fastpm_charm6/update.md) |
