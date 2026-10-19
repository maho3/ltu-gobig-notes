**Script**: ltu-cmass `scripts/noise_inflation.py` (job `jobs/slurm_noise_inflation.sh`)
**Suite**: abacuslike, L=2000 Mpc/h, N=256, z=0.5, fastpm_charm7 halos, galaxy tracer, `bias=zheng_composite` (ngc prior), 5 HODs per lhid
**Cases**:
- `fastpm_charm7_noisefix`: σ_rad = σ_tran = 1.5 Mpc/h, both fixed (`noise=fixed`); trained with `include_noise=False`
- `fastpm_charm7_noisetrans`: σ_rad = 1.5 fixed, σ_tran ~ logU(0.1, 4.51) (`noise=reciprocaltransverse`, new); trained with σ_tran as the only noise parameter
- `fastpm_charm7_cosmoHOD_reparam`: σ_rad, σ_tran ~ logU(0.1, 4.51), existing reparam models
- `fastpm_charm7_cosmoHOD`: same data, existing non-reparam models (no kmax=0.3 cuts)
**Summaries**: zPk0; zPk0+zPk2+zPk4; zPk0+zPk2+zPk4+zBk0
**kmax**: zPk0, zPk024: 0.2, 0.3, 0.4, 0.6; +zBk0: (zPk, zBk) = (0.2, 0.2), (0.4, 0.2), (0.6, 0.2), (0.3, 0.3), (0.4, 0.4) — `infer=noisetest`
**Fiducial selection**: test rows with Ωm, σ8 within 10% of (0.3, 0.8) and 1e-4 < nbar < 5e-4 (as `fiducial_stdev`): 78 rows from 24 lhids, the same rows in every case
**Notes**: All models include HOD parameters (`include_hod=True`). The two new suites reuse the fastpm_charm7 halos and the same per-(lhid, hod) HOD draws as cosmoHOD; noisetrans also has the identical σ_tran draw per (lhid, hod), so its only difference from cosmoHOD is σ_rad. Train/val/test splits are identical across suites (per-lhid hash). New models: 128–163 Optuna trials per cut; the reparam kmax=0.3 cuts had only 57–77.
