**Script**: model_scaling_diagnostics.py (multisim mode), volume_scaling.py
**Tracer**: galaxy
**Model 1**: quijotelike/fastpm_charm7_cosmoHOD (L=1 Gpc/h)
**Model 2**: abacuslike/fastpm_charm7_cosmoHOD (L=2 Gpc/h)
**Model 3**: mtnglike/fastpm_charm7 (L=3 Gpc/h)
**kmax sweep summary**: Pk0+Pk2+Pk4 (prefix auto-detected from the model tree; its k-cuts auto-discovered)
**Feature sweep reference kmax**: 0.4 (per-summary k-cut with closest Pk kmax)
**Feature sweep summaries**: Pk0, Pk0+Pk2+Pk4, Pk0+Pk2+Pk4+EqBk0, Pk0+Pk2+Pk4+SqBk0, Pk0+Pk2+Pk4+Bk0 (with the tree's z-prefix where it has one)
**Fiducial nbar band**: 1e-4 to 5e-4
**Volume-scaling reference kmax**: 0.4 (per-summary shared k-cut with closest Pk kmax)
**Notes**: Box-size ladder at matched pipeline and tracer: all three infer the same 17-parameter theta (5 cosmology + 10 HOD + 2 noise) over the same 5 summaries and the same k-cut grid.
