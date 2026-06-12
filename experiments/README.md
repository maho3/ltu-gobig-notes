# Experiments

| Date | Type | Train | Test | Notes | Update |
|------|------|-------|------|-------|--------|
| 2026-06-12 | OOD inference | quijotelike/fastpm_charm6 | quijote/nbody_hodz_gridnoise | CHARM devoxelization bias: Ωm underestimated (coverage 0.1–0.4 at kmax≤0.2), σ8 overestimated (coverage 0.65–0.95 at kmax≥0.3); Ωm improves with kmax and noise; σ8 bias noise-independent and worsens with kmax | [update.md](2026-06-12_ood_quijotelike-fastpm_charm6_quijote-nbody_hodz_gridnoise/update.md) |
| 2026-06-12 | Self-consistent | quijotelike/fastpm_charm6 | quijotelike/fastpm_charm6 | kmax sweep (0.1–0.4) and feature sweep with zPk024, Bk0, EqBk0; kmax sweep well-calibrated; feature sweep shows training convergence issues with EqBk0 | [update.md](2026-06-12_self_quijotelike-fastpm_charm6/update.md) |
