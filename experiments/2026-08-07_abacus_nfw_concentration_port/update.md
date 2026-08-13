# AbacusSummit CompaSO halo port: NFW-fit concentration replaces a buggy SO_radius/Vmax estimator

**Date**: 2026-08-07
**Type**: Miscellaneous / decision
**Suite**: AbacusSummit `base` (z=0.500, L=2000 Mpc/h, 6912 PPD), 114 cosmologies
(`AbacusSummit_base_c001_ph000` ... `c181_ph000`), cleaned CompaSO halos at z=0.5,
ported into the `ltu-cmass` `halos.h5` format used by the Quijote (`port_quijote.ipynb`)
and FastPM+CHARM suites.
**Notes**: Numbers below are read directly off the production `halos.h5` outputs
(`/anvil/scratch/x-mho1/cmass-ili/abacus/{custom,nbodyall}/L2000-N256/6`, cosmology
`c001_ph000`, Ωm=0.276126) and the completed SLURM array logs (job 19727045,
`/anvil/scratch/x-mho1/jobout/portabacus_19727045_*.out`). The output directory that
was called `nbodyconc` while this port was being built has since been renamed to
`nbodyall` (its lhid ordering is the custom-table one, originally 0-118); a *new*
`nbodyconc` now holds full copies of the same halo catalogs (not symlinks -- it's meant
to stand on its own) using the **same lhid as `abacus/custom`** (both derive from
`abacus_custom_table.csv`) -- a drop-in companion to `custom` that adds the NFW-fit
concentration field, not a different indexing scheme (an earlier version of this
mirror used `abacus/nbody`'s cosmology-number lhid ordering instead; that was replaced
once it became clear `custom`'s ordering was the intended target). A 25-phase `c000`
archive (`z0.500_base_c000.tar`) was transferred and ported afterward (see the c000
section below), extending `abacus_custom_table.csv` to 138 rows (0-137) and `nbodyall`/
`nbodyconc` to 138 lhids; the port pipeline (`port_abacus_lib.py`) was generalized to
read from either tar. The plotting/decomposition scripts that produced the original
bimodality figures (`abacus_conc_decomp.py`, `abacus_conc_benchmark.py`,
`nfw_sanity_plots.py`, `fig1-fig6` in `abacus_sanity_figs/`) were exploratory scratch
and were removed once the pipeline landed; where a number came only from those figures
and can't be re-derived from what's still on disk, that's called out explicitly below
rather than requoted from memory. A combined old-vs-new validation figure and a c000
phase-variance check were regenerated afterward and are included below.

---

## TL;DR

AbacusSummit's CompaSO halo finder does not report a concentration, and the
CompaSO-recommended proxy `c ≈ 2.1626·SO_radius/rvcirc_max` turned out to produce a
visibly bimodal concentration distribution when applied to the cleaned halos: it
mixes a radius defined about the whole-L1 halo (`SO_radius`, all particles including
substructure) with a radius defined about the L2 "core" (`rvcirc_max_L2com`), so halos
split into two populations depending on how much of their mass sits in substructure
outside the L2 core. A first attempt to fix this via `colossus`-based mass-definition
conversion (starting from `SO_L2max_radius`, the L2 core's own SO radius, and
extrapolating out to Δ=200c) did not fix the bimodality — it replaced it with a
*different* spurious bimodal artifact, because the extrapolation from the dense L2
core out to the much lower 200c threshold saturates for a large fraction of halos.
The adopted fix fits an NFW profile directly to each halo's enclosed-mass curve
(`r10...r98_L2com`, all defined consistently about the L2 center) in log-space, and
solves for R200c from the fitted NFW density profile. This is unimodal (median
c200c ≈ 4.9 for `c001_ph000` at z=0.5, no visible second peak), all 4.6M halos in the
test sim get a finite value, and it comes out in the same range as Quijote's
Rockstar-based `R200c/Rs` at comparable cosmology (median ≈ 4.3 at Ωm=0.271, ≈ 3.0 at
Ωm=0.176 — the same z=0.5, Ωm-driven trend as the Abacus fit). Full production run:
114 cosmologies, 112 completed (6 lhids absent from the archive, 1 already done),
mean ≈ 17.7 min/sim, ≈ 655M halos total.

---

## Setup

- Source data: `/anvil/scratch/x-mho1/abacus/z0.500_base.tar`, a 15 TB HTAR archive of
  the 114 `base`-resolution (`6912^3` particle, L=2000 Mpc/h) AbacusSummit cosmologies
  used by this project's custom LHID table (`abacus_custom_table.csv`). Both
  `SimName/halos/z0.500/halo_info/` (base per-snapshot L1 catalog) and
  `cleaning/SimName/z0.500/cleaned_halo_info/` (post-hoc cleaned fields,
  merger-tree-informed) are present per sim; `CompaSOHaloCatalog(..., cleaned=True)`
  auto-detects and merges the two.
- The archive's `.idx` offsets are HTAR-internal logical block counts, not seekable
  byte offsets, so random access goes through Python's `tarfile` in `'r'` mode
  directly against the tar. On Lustre, a bare header-scan of the tar drags the
  default ~10 MB/seek readahead across the wire; `get_index()`
  (`port_abacus_lib.py`) disables readahead (`POSIX_FADV_RANDOM`) for the one-time
  scan that builds a `{member name: TarInfo}` index, caches it as a 2.2 MB pickle
  (`z0.500_base.index.pkl`), then reopens the tar normally (readahead on) for the
  actual slab extraction, which is sequential and benefits from it.
- Output: `pos` (comoving Mpc/h), `vel` (physical km/s), `mass` (log10 Msun/h,
  `N*Mpart`), `concentration` (c200c), same `halos.h5`/`{a:.6f}` group layout as
  `port_quijote.ipynb`. Mass cut at `M ≥ 5e12 Msun/h` (CHARM cut, identical to the
  Quijote port).

---

## CompaSO catalog structure

CompaSO reports two centers per L1 halo: `x_com` (center of mass of every particle
assigned to the L1 group, including substructure and tidal debris) and `x_L2com`
(center of mass of the L2 "core" subset — the dense central subhalo found by a second
group-finding pass). It also reports two SO radii: `SO_radius` (the L1 group's own
spherical-overdensity radius, computed about `x_com`, at the group's default
overdensity threshold `SODensityL1`) and `SO_L2max_radius` (the SO radius of the
*largest* L2 subhalo, i.e. the core, computed about its own center at a separate,
denser threshold). For a relaxed, substructure-poor halo these track each other
reasonably well; for a halo with significant substructure they diverge, because
`SO_radius` includes mass the L2 core doesn't. CompaSO additionally reports a set of
enclosed-mass radii about the L2 center, `r{10,25,33,50,67,75,90,95,98}_L2com` — the
radius containing that percentage of the L2-assigned mass — which is what the adopted
fit uses (`RFIELDS` in `port_abacus_lib.py`), since every one of them is defined
consistently about the same center.

`SODensityL1` is cosmology- and redshift-dependent (not a fixed 200 or 500): CompaSO
scales the Bryan & Norman (1998) virial-overdensity fit,

```
Δ_BN(z) = 18π² + 82x − 39x²,   x = Ωm(z) − 1        (relative to ρ_crit(z))
```

converts it to units of the mean matter density (`Δ_m(z) = Δ_BN(z)/Ωm(z)`), then
rescales by `200/(18π²)` so it reduces to exactly 200 in the Einstein-de Sitter limit
(Ωm→1, x→0, Δ_BN→18π²). Plugging in `c001_ph000`'s cosmology (Ωm0 = 0.276126, the
same flat-ΛCDM `E(z)² = Ωm0(1+z)³+(1−Ωm0)` used in `fit_c200c`) at z=0.5 gives
Ωm(z) = 0.5628, Δ_BN(z) = 134.35, Δ_m(z) = 238.71, and `238.71 × 200/(18π²) = 268.7` —
matching the `SODensityL1 ≈ 268.7` value noted during the investigation (not present
in any file still on disk; this is an independent re-derivation from the cosmology
parameters and the formula, not a re-read of a stored header value).

---

## The concentration bug: mixing the L1 whole-halo radius with the L2 core

The CompaSO-suggested concentration proxy is the "Vmax method"
(Klypin et al. 2011 / Prada et al. 2012 style estimator): for an NFW profile, the
radius of maximum circular velocity satisfies `r_max = x*·rs` where `x*` solves
`(2x²+x)/(1+x)² = ln(1+x)`; numerically `x* = 2.162582` (verified directly by
root-finding, not just quoted). So `rs ≈ r_vmax/2.1626`, and if `R_Δ` is a halo's
outer radius at the overdensity of interest, `c = R_Δ/rs ≈ 2.1626·R_Δ/r_vmax`. Applied
naively to CompaSO's fields, `R_Δ → SO_radius` (about `x_com`) and
`r_vmax → rvcirc_max_L2com` (about `x_L2com`) — two different centers and particle
selections plugged into one ratio.

Decomposing halos by their L2-core mass fraction showed this is exactly what drives
the bimodality: halos with a large gap between the L1 group's total SO mass and its
L2 core (substantial substructure/tidal mass outside the core) sit on one branch of
the `SO_radius`/`rvcirc_max_L2com` ratio, and substructure-poor, more relaxed halos
sit on another. The two branches are populous enough to show up as two separate modes
in the concentration histogram rather than a smooth tail. The exact peak locations
from that decomposition figure aren't recoverable now (the script and figure were
cleaned up as exploratory scratch after the pipeline was finalized), but the
mechanism — inconsistent center/selection between numerator and denominator, gated by
substructure fraction — reproduced cleanly across the sim it was tested on.

---

## First fix attempt: colossus mass-definition conversion — rejected

The natural fix, mirroring how `port_quijote.ipynb` gets its concentration (Rockstar
already reports `M200c` and `Rs` directly; `colossus.halo.mass_so.M_to_R` is only used
there to convert `M200c` to a comoving `R200c` in the right units, not to extrapolate
a profile), was to take a CompaSO radius defined consistently about the L2 core
(`SO_L2max_radius`) and use `colossus`'s mass-definition-change machinery to convert
it out to Δ=200c, then take `c = R200c/R_{L2core}`-type ratios.

This does **not** eliminate the bimodality — it manufactures a *new* one. The L2 core
sits at a much higher effective overdensity than 200c, so converting outward is a
large extrapolation of an assumed density profile shape rather than an interpolation
between two enclosed-mass points that were actually measured. For a substantial
fraction of halos this extrapolation saturates (the assumed profile's mass-definition
mapping flattens out before reaching the target overdensity), and the saturated
subpopulation shows up as its own mode, distinct from the non-saturated one. This is
a different failure mode from the original bug — not two centers mixed together, but
a profile-shape assumption being pushed well outside the radius range it was
constrained by — and it was rejected for the same reason as the original estimator:
a spurious second mode with no corresponding physical explanation.

---

## The adopted fix: NFW profile fit in log-space

`fit_c200c` (`port_abacus_lib.py`) fits `M(<r) = A·μ(r/rs)`,
`μ(x) = ln(1+x) − x/(1+x)`, to the nine enclosed-mass points
`(r10...r98_L2com, frac·N·Mpart)` per halo, in log space (equal weight per point,
not weighted by mass), via a grid search over `rs` (500 points, geometric in
`[3e-3, 2.0]` comoving Mpc/h). For each trial `rs` it solves the best-fit
normalization `A` in closed form (mean of the log-residuals) and keeps the `rs` with
lowest sum-of-squared log-residuals, vectorized across all halos in a slab
simultaneously (`(Nh, 9)` arrays, one loop over the 500 `rs` grid points rather than
one fit per halo). From the fitted `(A, rs)` it gets `ρ_s = A/(4π·rs³)`, solves the
overdensity condition `200·ρ_crit(z)·a³ = 3·ρ_s/μ(y)·y³`-type equation
(`_mu(y)/y³` inverted via lookup on a 6000-point grid) for `y = R200c/rs`, and reports
`c200c = y`. Every radius that goes into the fit (`r10...r98_L2com`) is defined about
the same L2 center, so there's no center-mixing left to produce a spurious mode.

On the test sim (`c001_ph000`, lhid 6, 4,625,357 halos above the mass cut),
`concentration` is finite for 100% of halos (no NaN/inf from failed fits), with
`min/median/max ≈ 0.30 / 4.90 / 14.97` and 1st/25th/75th/99th percentiles
`≈ 1.75 / 3.82 / 5.88 / 8.28`. The minimum sits exactly at the `rs` grid floor
(3e-3 Mpc/h), i.e. the grid search saturates for a small number of very compact/poorly
resolved halos rather than returning a genuinely unconstrained value — worth knowing
if very low concentrations get used downstream.

---

## Validation against the old port and against Quijote

- **Old vs new halo counts (`c001_ph000`, lhid 6)**: the old `custom` port (no
  concentration field at all) has 4,627,304 halos above the same mass cut; the new
  NFW-fit port has 4,625,357 — a 0.04% difference, consistent with the new pipeline's
  extra `R > 0` selection on all nine `RFIELDS` dropping a small number of edge cases
  that the old port didn't filter on. Mass ranges match to five significant figures
  (`logM` min/median/max 12.699/12.950/15.369 in both), so the position/velocity/mass
  columns are unaffected by the concentration rewrite.
- **Against Quijote at matched-ish cosmology**: Quijote lhid 884 (Ωm=0.2713, close to
  `c001_ph000`'s Ωm=0.2761) has median concentration 4.30 (IQR 3.00-5.85) from
  Rockstar's `R200c/Rs`, vs the Abacus NFW fit's median 4.90 (IQR 3.82-5.88) — same
  order, same spread, no second mode in either. Quijote lhid 0 (low Ωm=0.1755) has
  median concentration 2.99, lower than both of the Ωm≈0.27-0.28 catalogs, the same
  direction the Abacus fit's own Ωm dependence would predict. (Halo counts aren't
  directly comparable across these three: Quijote boxes are L=1000 Mpc/h vs Abacus's
  L=2000 Mpc/h, an 8x volume difference, and the two suites are different N-body
  codes at different resolution, so only the concentration distributions — not
  abundances — were used as the comparison here.)
- The original `fig1-fig6` sanity-check figures (old-vs-new position/mass agreement,
  Abacus-vs-Quijote concentration PDFs, the bimodality decomposition, and the
  NFW-vs-colossus speed benchmark) that this validation was built on are no longer on
  disk; the counts and percentiles above were recomputed directly from the current
  `halos.h5` files rather than read off those figures. A single combined figure
  covering the same old-vs-new comparison was regenerated afterward — see below.

---

## Final validation: combined old-vs-new comparison

A single figure combining position, mass function, velocity, power spectrum, and
concentration was regenerated for `c001_ph000` (lhid 6) to have one place that shows
the old and new ports agree, now that the original `fig1-fig6` set is gone. The power
spectrum panel was later upgraded to a finer mesh (N=512, voxel sidelength
2000/512=3.9062 Mpc/h, half the original 7.8125 Mpc/h voxel) and measured in
**redshift-space** (line-of-sight displacement via `redshift_space_library`, the same
convention `cmass.diagnostics.calculations.MAz` uses, with H(z)/h from a flat-ΛCDM
astropy cosmology at the sim's own Ωm, h) to resolve any small-scale (high-k)
difference between the two ports that the original N=256 real-space mesh could have
masked.

![Old vs new: positions, mass function, halo speed, power spectrum, concentration](figures/old_vs_new_c001.png)

- Positions (40 Mpc/h slab, logM>13.3) overlay pixel-for-pixel between old and new —
  no visible offset or missing/extra structure.
- Mass function: old (N=4,627,304) and new (N=4,625,357) overlay across the full
  12.7-15.4 logM range; the 0.04% count difference noted above doesn't show up as any
  visible shape difference.
- Halo speed |v|: medians 447.4 km/s (old) vs 451.2 km/s (new), distributions overlay.
- Power spectrum (halo field, redshift-space, CIC, N=512 mesh, voxel=3.9062 Mpc/h):
  new/old ratio is flat at 1.00 across the full k range shown (k~0.005 up to the
  N=512 mesh corner, ~1.4 h/Mpc), including the small scales the finer mesh newly
  resolves — no small-scale discrepancy appears; P_zspace(k=0.1) = 16232 (old) vs
  16202 (new) (Mpc/h)^3 (higher than the earlier real-space N=256 values, 13162/13165,
  as expected from the redshift-space Kaiser boost).
- Concentration (new only — the old port has no concentration field): unimodal,
  median 4.90, IQR [3.82, 5.88], 100% finite — matches the numbers quoted above.

---

## c000 phase variance: is the emulator-grid phase (ph0) typical?

The emulator grid (`c001_ph000` ... `c181_ph000`) uses phase 000 for every
cosmology. AbacusSummit's fiducial cosmology `c000` has many phases (independent
realizations of the same cosmology, different initial random seed) available for
cosmic-variance testing, which lets us ask whether ph000 happens to be a typical
realization or an outlier.

### Preliminary check: HOD galaxy mocks (superseded by the halo-level check below)

The `c000` *halo* catalogs analogous to the emulator-grid port were not downloaded
at first (would have required a new ~540 GB fetch), so this check originally used an
existing 25-phase set of **HOD galaxy mocks** at the same cosmology and box
(`/anvil/projects/x-phy240043/cuesta/abacushod/abacus_c0_ph{0..24}.hdf5`, same L=2000
Mpc/h box, fixed HOD: logM_cut=12.66, logM1=13.6662, alpha=1.3452, ~10.70M galaxies
per phase) as a proxy — checking galaxy-clustering-level phase variance, not
halo-level mass/concentration/velocity variance directly. Phase 19's file is empty (a
group with no `pos` dataset, 2.6 KB vs ~770 MB for the others) and was excluded,
leaving 24 usable phases.

![c000 fiducial cosmology: P(k) phase-to-phase scatter, 24 phases, ph0 highlighted](figures/c000_phase_variance.png)

- P(k) (real-space, CIC, N=256 mesh) for ph0 sits inside the phase-to-phase envelope
  of the other 23 phases across the full k range plotted (k~0.005-0.5 h/Mpc); no
  visible discontinuity or shape mismatch against the 24-phase median.
- At k=0.05 h/Mpc, ph0/median = 1.025, ranking 21st of 23 (91st percentile) — on the
  high side but within the ~0.95-1.06 phase-to-phase scatter band at that k.
- At k=0.10 h/Mpc, ph0/median = 0.996, ranking 10th of 23 (43rd percentile) — squarely
  typical.
- At k=0.20 h/Mpc, ph0/median = 1.011, the highest of the 24 phases (100th
  percentile) — but the phase-to-phase scatter band itself is only about
  0.995-1.015 at that k, so in absolute terms this is a ~1% high fluctuation, not a
  large outlier.
- Galaxy counts per phase range 10,698,544-10,707,913 (ph0: 10,698,680), a <0.1%
  spread, consistent across all 24 phases.

### Direct check: real c000 halo catalogs, all 25 phases

A 3.56 TB HTAR archive of all 25 `AbacusSummit_base_c000_ph{000..024}` phases
(`z0.500_base_c000.tar`, same `halo_info`/`cleaned_halo_info` layout as the main
114-cosmology archive) was transferred separately and ported with the same pipeline
used for the emulator grid (`port_abacus_lib.py` generalized to read from either tar;
`abacus_custom_table.csv` extended with 19 new rows for ph006-ph024, appended as
lhid 119-137 so the existing 0-118 lhid identities were undisturbed). All 25 phases
ported cleanly (0 failures), each in 978-1662s, ~5.84M halos per phase (range
5,839,091-5,846,433, a <0.13% spread) — this is the direct, apples-to-apples version
of the check above, using the same mass/concentration/position fields as the rest of
this port rather than a galaxy-mock proxy.

P(k) here is measured in **redshift-space** on an **N=512 mesh** (voxel sidelength
2000/512=3.9062 Mpc/h, half the original 7.8125 Mpc/h voxel used for a first pass of
this check), the same upgrade applied to the old-vs-new comparison above, to resolve
any small-scale phase dependence a coarser real-space mesh might have hidden. Mass
function and concentration are shown as **overlapping histograms across all 25
phases** (panels d, e) rather than one median bar per phase, so the full
per-halo distributions — not just their medians — can be compared directly.

![c000 fiducial cosmology: real halo catalogs, 25 phases, ph0 highlighted](figures/c000_halo_phase_variance.png)

- Halo P(k) (redshift-space, N=512) for ph0 tracks the 25-phase median closely
  through the bulk of the k range (panel a), with the largest excursions at the
  lowest k (k<0.01 h/Mpc, few Fourier modes per bin) where every phase shows large
  scatter, ph0 included; at high k (approaching the N=512 mesh corner, ~k>1 h/Mpc)
  all 25 phases converge tightly, so the finer mesh does not reveal any small-scale
  phase-specific discrepancy for ph0.
- At k=0.05 h/Mpc, ph0/median = 1.021, ranking 22nd of 24 (92nd percentile), within a
  visible scatter band of roughly 0.94-1.05.
- At k=0.10 h/Mpc, ph0/median = 1.000, ranking 12th of 24 (50th percentile) — exactly
  the median phase at this scale.
- At k=0.20 h/Mpc, ph0/median = 1.010, the highest of the 25 phases (100th
  percentile), within a ~0.98-1.02 scatter band — a shift from the real-space,
  N=256 pass (96th percentile at this k), but still only a ~1% high fluctuation in
  absolute terms.
- ph0's rank varies by scale and statistic (92nd/50th/100th percentile at
  k=0.05/0.10/0.20) but stays inside the visible phase-to-phase scatter cloud at
  every k checked, not detached from it as an outlier would be.
- Mass function (panel d) and concentration pdf (panel e) overlay almost perfectly
  across all 25 phases, ph0 included — no visible phase-to-phase spread at all at
  this resolution. Numerically: N halos 5,839,091-5,846,433 (ph0: 5,840,860, close to
  the median 5,842,866), median c200c 5.27 for every phase to 2 decimal places,
  median logM 12.9585-12.9589 (ph0: 12.9587) — these bulk statistics, averaged over
  ~5.8M halos each, are effectively phase-independent, as expected.

---

## Production run

Full grid: `sbatch run_array.sh` (`--array=0-118%8`, `phy240043`, `shared`, one lhid
per SLURM array task, resumable — skips any lhid whose `halos.h5` already exists). Job
19727045: of 119 array tasks, 112 completed (`done`), 6 reported `missing` (lhids
whose SimName isn't present in the tar — the table includes some phases, e.g. certain
`c000` entries, that were never in this archive), 1 `skip` (lhid 6, already produced
by the interactive test above). Per-sim wall time (extract from tar + slab-by-slab
cleaned read + NFW fit + write, all included) ranged 768-1589 s, mean 1059 s
(≈17.7 min), median 1053 s. Halo counts per sim ranged 4.12M-7.81M (mean 5.85M);
summed over the 112 completed sims, ≈655.3M halos ported. Each task holds roughly
90 GB of extracted `halo_info` slabs at a time (deleted on completion), which is why
concurrency is capped at 8 concurrent tasks rather than running the whole grid at
once. Wall time is dominated by tar extraction and slab I/O, not by the fit itself
(the fit is a vectorized numpy grid-search over the whole slab at once); a standalone
timing comparison of the fit against a per-halo `colossus` call was run
(`abacus_conc_benchmark.py`, since removed) but the specific numbers from it aren't
recoverable from what's currently on disk, so they're not repeated here.

---

## Recommendation

Adopted: the NFW-profile-fit `c200c` in `port_abacus_lib.py`/`fit_c200c`, run via
`sbatch run_array.sh` for the full 114-cosmology grid. Do not resurrect the
`2.1626·SO_radius/rvcirc_max` estimator (mixes L1/L2 centers, bimodal) or a
`colossus`-based conversion anchored on `SO_L2max_radius` (saturating extrapolation
from the L2 core out to 200c, a different bimodal artifact). Any future halo
definition change for Abacus should keep all radii used in a single fit/ratio defined
about the same center (`_L2com`), which is what made the adopted fit unimodal.

## Reproducing

```bash
conda activate /anvil/scratch/x-mho1/envs/abacusport   # kernel: abacusport
cd /home/x-mho1/git/ltu-cmass/notebooks

# one-time tar index (builds z0.500_base.index.pkl if not already cached)
python -c "from port_abacus_lib import get_index; get_index()"

# single sim (interactive / notebook front-end): port_abacus.ipynb, or
python port_abacus_one.py 6 --overwrite

# full grid (main 114-cosmology tar + the c000 25-phase tar, both in TARS)
sbatch run_array.sh                 # --array=0-118%8
sbatch --array=6 run_array.sh       # single-lhid validation
sbatch --array=1-5,119-137%8 run_array.sh   # c000 phases (lhid 0 done as part of validation)

# also written per lhid: config.yaml (meta+nbody provenance only) via write_config()
python backfill_config.py           # backfills config.yaml into already-ported lhids

# after the grid: copy into abacus/custom's lhid ordering (same table, same keys)
python mirror_custom_ordering.py
```

Output: `/anvil/scratch/x-mho1/cmass-ili/abacus/nbodyall/L2000-N256/{lhid}/halos.h5`,
group `0.666667`, datasets `pos`/`vel`/`mass`/`concentration`, plus `config.yaml`.
`abacus/nbodyconc/L2000-N256/{lhid}/` holds full copies of the same files under the
identical lhid `abacus/custom` uses (both index off `abacus_custom_table.csv`), so
it's a drop-in, same-lhid companion to `custom` with concentration added.
