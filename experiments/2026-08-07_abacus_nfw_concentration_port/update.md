# AbacusSummit CompaSO halo port: NFW-fit concentration replaces a buggy SO_radius/Vmax estimator

**Date**: 2026-08-07
**Type**: Miscellaneous / decision
**Suite**: AbacusSummit `base` (z=0.500, L=2000 Mpc/h, 6912 PPD), 114 cosmologies
(`AbacusSummit_base_c001_ph000` ... `c181_ph000`), cleaned CompaSO halos at z=0.5,
ported into the `ltu-cmass` `halos.h5` format used by the Quijote (`port_quijote.ipynb`)
and FastPM+CHARM suites.
**Notes**: Numbers below are read directly off the production `halos.h5` outputs
(`/anvil/scratch/x-mho1/cmass-ili/abacus/{custom,nbodyconc}/L2000-N256/6`, cosmology
`c001_ph000`, Ωm=0.276126) and the completed SLURM array logs (job 19727045,
`/anvil/scratch/x-mho1/jobout/portabacus_19727045_*.out`). The plotting/decomposition
scripts that produced the original bimodality figures (`abacus_conc_decomp.py`,
`abacus_conc_benchmark.py`, `nfw_sanity_plots.py`, `fig1-fig6` in
`abacus_sanity_figs/`) were exploratory scratch and were removed once the pipeline
landed; where a number came only from those figures and can't be re-derived from
what's still on disk, that's called out explicitly below rather than requoted from
memory.

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
- The `fig1-fig6` sanity-check figures (old-vs-new position/mass agreement,
  Abacus-vs-Quijote concentration PDFs, the bimodality decomposition, and the
  NFW-vs-colossus speed benchmark) that this validation was built on are no longer on
  disk; the counts and percentiles above were recomputed directly from the current
  `halos.h5` files rather than read off those figures.

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

# full grid
sbatch run_array.sh                 # --array=0-118%8
sbatch --array=6 run_array.sh       # single-lhid validation
```

Output: `/anvil/scratch/x-mho1/cmass-ili/abacus/nbodyconc/L2000-N256/{lhid}/halos.h5`,
group `0.666667`, datasets `pos`/`vel`/`mass`/`concentration`.
