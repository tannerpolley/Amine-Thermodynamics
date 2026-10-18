# #170 amendment 5: the ion model form for MEAH⁺ and carbamate

Design draft, 18 October 2026, first written on MEA `main` at `96e5124`;
revised the same day from `main` at `adcefdf` after an independent readiness
review (**Ready with corrections**; all eight corrections applied). Starting
stage:
`cse:design`, because amendment 4 placed the bound activity in the ion
description but left open which ion form to test and what result would decide
it; `cse:research` supplied the sources in §3.

**Nothing was fitted, built or evaluated with the Engine in this task.** The
numbers in §2 and §5 (diameter factors, volumes, dispersion weights) are
arithmetic on declared parameters and can be checked by hand; the reviewer's
arithmetic quoted below was rechecked here. Every choice is a reversible
orchestrator-side proposal made while the owner is away (§14). Publication on
#170 and any Engine comment belong to the orchestrator. Abbreviations: DH =
Debye–Hückel; GN = Gauss–Newton (the linearized least-squares step); A4 =
amendment 4.

## 1. Question and intended use

**Question.** Every A4 reacting fit ends with the same five ion coordinates on
bounds: both ion segment diameters at 5.8 Å, both Born diameters at 5.0 Å, and
carbamate–MEAH⁺ k_ij at −1 (`amendment-4/README.md` "Outcome";
`matched-larger-dV/README.md`; `matched-smaller-dV/README.md`). The CO₂–MEA
neutral pair is not the cause (C166 ×1.00059 on both branches). Is this bound
activity caused by representing MEAH⁺ and carbamate as one-segment spheres
under the inorganic-ion rules, and does a charged-molecule form remove it
without a loss of fit? A0 answers the second part. It separates the chain form
from "the sphere box was too small" only weakly (§5.4).

**Intended use.** Choose the ion form for the remaining #170 stages and
decide whether MEA needs the Engine capability already described on
ePC-SAFT #499. The result is a model-form screen on the A4 205-row objective.
It does not adopt parameters, determine single-ion properties or validate the
model physically.

**Out of scope.** New data or observation kinds; the inorganic ions'
parameters; the dielectric model; the CO₂–MEA pair; the reaction set;
stages 5–7. The Xu result now on #170 (comment 6252469842: the 16 Xu rows meet
B1, Xu stays comparison-only, the Hartono-only neutral fit is kept) does not
touch A5. The 205-row objective has no N₂O-analogy rows, and CO₂–MEA stays
at (0, 0).

## 2. Prior evidence

**The current ion form**, read from
`amendment-4/matched-larger-dV/control-start-parameters.json`
(SHA-256 `e01e1142…4337d`) and `control-fit-spec.json` (`c138ff13…6a2f`):

| Ion | m | σ, Å | u/k, K | Packing and DH diameters | Born, Å | Self-dispersion |
|---|---:|---:|---:|---|---:|---|
| MEAH⁺ | 1 | 3.563 | 228.71 | 0.88σ = 3.13544 | 3.563 | none (`exclude-same-sign-ion-pairs`) |
| Carbamate | 1 | 3.5605 | 533.11 | 0.88σ = 3.13324 | 3.5605 | none |

Each size coordinate moves σ with packing and DH diameters tied at 0.88σ.

**Where the seeds come from.** The MEAH⁺ seed equals the MDEAH⁺ row of
Bülow 2021a Table 2 (m = 1, σ 3.5630 Å, u 228.71 K): MDEA's σ and u from
Uyan 2015 Tables 3–4, on a single sphere. The component audit
(`docs/ePC-SAFT/full-component-parameter-source-audit.md`, row MEAH⁺)
attributes the lineage to Uyan and Wangler, whose MDEAH⁺ is not spherical
(§3). The carbamate seed's σ and u equal the acetate anion [Ac]⁻ of Ji & Held
2016 Table 3 (σ 3.5605 Å, u 533.1138 K), whose published segment number is
**3.7266**; the repository uses m = 1. The audit (row MEACOO⁻) prints no
literature source for these values, and amendment 3 calls them an acetate
analog. Neither ion has an MEA-specific parameterization; the audit records
the May 2026 local fit that started from these seeds.

**Bound history.** No ion form tried so far has produced an interior ion
block:

| Record | Ion-related active bounds |
|---|---|
| #172 interim campaign | carbamate Born 2 Å (lower); free rank 4/7 |
| Route 1 precursor, iteration 40 (`amendment-2/route1/precursor/README.md`) | both σ 5.8 Å; both Born 1 Å (lower) |
| Route 2, 81-iteration partial | carbamate σ; MEAH⁺ Born; carbamate–MEAH⁺ k |
| Route 2b (`amendment-2/route2b/README.md`) | carbamate–MEAH⁺ k −1 (gradient +2.44 per unit k); both Born 5.0 Å; MEAH⁺ u 950 K |
| Model D S1, original Born (`model-d/README.md`) | carbamate–MEAH⁺ k −1 |
| A4, all four arms | both σ 5.8 Å; both Born 5.0 Å; carbamate–MEAH⁺ k −1 |

The carbamate–MEAH⁺ k sits at −1 under both Born forms. The Born diameters
reach a bound in every run, but at opposite ends under different objectives.
That pattern marks a weakly determined, compensating direction, not a missing
range.

**What the size bound mimics.** This is inference from the declared
parameters. Hard-core volume uses Σm·d³ (the packing moment). Ion–water
dispersion weight uses m·σ_iw³, with σ_iw = (σ_i + σ_w)/2 and σ_w ≈ 2.78 Å
(the water correlation's constant term).

| Representation | m·d³, Å³ | m·σ_iw³, Å³ |
|---|---:|---:|
| Current seeds, one sphere, d = 0.88σ | 30.8 | 31.9 |
| A4 endpoint, one sphere at σ = 5.8 Å | 133.0 | 79.0 |
| MEA chain (m 3.0353, σ 3.0435, d from Eq. A5-2 at 313.15 K) | 83.4 | 74.9 |
| [Ac]⁻ chain (m 3.7266, σ 3.5605, Eq. A5-2) | 167.8 | 118.7 |

The opposite-ion weight m₊m₋σ±³ is 45.2 Å³ at the seeds, 195.1 at the A4
endpoint, and 407.2 for the two parent chains. At the bound, the fit has
inflated each sphere toward the volume and ion–water dispersion of the
molecules the seeds came from. It has pushed the cation–anion attraction to
the edge of its box (k = −1 doubles u_ij). This fits the hypothesis below but
does not prove it.

**The MDEA lead (#126).** `analyses/mdea_kuranov_refit/README.md`, "Convention
diagnosis", and Engine comment 6252262739 on ePC-SAFT #499 report one reading,
(A). In it MDEAH⁺ keeps MDEA's self-dispersion and the neutral
temperature-dependent diameter. Under (A) the printed Wangler 2018 model goes
from 1036 % to 17.6 % ARD on Kuranov (published 19.7 %). (A) is also the only
reading tested that reproduces Uyan's speciation. The support is numerical and
contradicts the papers' stated ion rules. The same reading does not reproduce
Uyan's pressures, Wangler's MDEA·HCl osmotic coefficients or his x(H⁺).

**What A4 does not establish.** The endpoint free block has condition 3.7e4
(6.2e4 for all 14 columns). The weakest direction is 97 % bicarbonate–water k.
Fixed-step derivatives missed at the two ion dispersion energies (h²
truncation, error ratio 4.0). The projected gradient, 0.008–0.010, sits above
1e-8 because the fits stopped on the 1e-6 function tolerance; the GN step
predicts at most 3.6e-4 further decrease. The 12 loaded-density rows and the
per-row heat and heat-capacity assessments were not run at the A4 endpoints.

## 3. What the literature does for MEAH⁺ and carbamate

**Search coverage.** I checked the shelf (80 files) and the Zotero Companion,
project and global queries on MEAH⁺/carbamate/ePC-SAFT/protonated-amine terms.
Two web searches (standard and extended) found only this project's own
manuscript releases. **No explicit-ion ePC-SAFT parameterization of
MEAH⁺ or carbamate was found.** This is a bounded search, not proof that none
exists. The closest MEA papers (Baygi 2015, PC-SAFT; Nasrifar 2010; Najafloo
2018, SAFT-HR) treat the ions only through ideal chemistry and give them no
equation-of-state parameters. The nearest practice is the protonated tertiary
amine MDEAH⁺ from the Held/Sadowski group. Every shelf copy below matches its
indexed hash and its current Zotero source file.

| Source (Zotero key) | Passages read | What it does |
|---|---|---|
| Uyan et al. 2015, FPE, doi:10.1016/j.fluid.2015.02.026 (GSLTFVDM) | §2: like-ion dispersion; Eqs. 10–11 and the sentence after Eq. 11; DH "distance of closest approach σ_ion". §4.1: Tables 3–4, Table 4 note a, inheritance text. §4.2.1 | MDEAH⁺ "inherited from the parameters of MDEA except self-association". Table 4 prints σ 3.5630 Å and u 228.71 K; the segment number is implied by "inherited", not printed. MDEAH⁺ cross-associates (ε = 0, κ inherited). Stated rules: no like-ion dispersion; Eq. 10, d = 0.88σ, "for all ions". No MDEAH⁺ salt data exist (§4.1). |
| Wangler et al. 2018, FPE, doi:10.1016/j.fluid.2017.12.033 (ZILDPWWE) | §3: Eqs. 6–7 and the species text. §6.1, Table 5. §6.1.4 | Eq. 6 "for all non-charged components"; Eq. 7, d = 0.88σ, "for ions". Inorganic ions are spherical and non-associating; "MDEAH⁺ and HS⁻ were regarded as non-spherical species". MDEAH⁺ cross-associates; ions of equal sign have no cross dispersion. Water–MDEAH⁺ k and l_hb are fitted to water–MDEA–HCl osmotic coefficients (§6.1.4). |
| Cleeton et al. 2020, FPE, doi:10.1016/j.fluid.2019.112453 (MMI98GID) | §2.1; §3.1, Table 1 and note b | Ions are spherical and non-associating, m = 1, with a temperature-independent solvated diameter. MDEAH⁺ has m = 1, σ 3.3474 Å, u 237.19 K, "transferred from MDEA" (4C). |
| Bülow et al. 2021a, IECR, doi:10.1021/acs.iecr.1c00176 (B74UQB9E) | Theory: text after Eq. 18; Eq. 20 and the sentence after it. Results: Table 2. Conclusions | "Charged species are assumed to be nonassociative, and dispersive cation−cation and anion−anion interactions are neglected". The Born a_i is the DH diameter, "similar to the ePC-SAFT segment diameter". Table 2: MDEAH⁺ m 1, 3.5630 Å, 228.71 K; [Ac]⁻ m 3.7266, 3.5605 Å, 533.11 K. Conclusions: high-loading gas solubility is overestimated through overpredicted ion–solvent interactions. |
| Ji & Held 2016, FPE, doi:10.1016/j.fluid.2015.11.014 (C2KASLZ6; Companion attachment HXLPS4LT, lines 56–60, 232, 373) | §2; Table 3; [Ac]⁻ paragraph | Each IL ion is "non-spherical"; "dispersion among all IL-ions was allowed"; ε = 1; no binary parameters. The parameters are fitted to pure-IL densities. [Ac]⁻: m 3.7266, σ 3.5605 Å, u 533.1138 K. |
| Held et al. 2014, ChERD, doi:10.1016/j.cherd.2014.05.017 (3DIW87Q5) | §2.1 (ions are spherical); §2.3; §2.4: Eqs. 21–22 and the sentence after Eq. 22; the 400 K paragraph; Table 2, Ac⁻ row | Solvated-ion diameters are temperature-independent. Table 2, strategy 2, aqueous acetate: σ 3.9328 Å, u 150.00 K, k with water −0.23, fitted to aqueous densities and osmotic coefficients at 298.15 K. **Eq. 21 (0.88σ) "differ[s]" from Eq. 22 because like-ion dispersion is zero, "resulting in a zero u_i/k_B value in Eq. (22)".** Ion u was capped at 400 K in screening, because very high values can cause spurious liquid–liquid demixing. |
| Held, Cameretti & Sadowski 2008, FPE, doi:10.1016/j.fluid.2008.06.010 (D6FBI6FG) | §2, Eqs. 2–3 | The DH closest-approach distance a_j "is equivalent to the ion diameter σ_j". |
| Cameretti et al. 2005, IECR (CNAR9DGU) | §2, Eqs. 9–14; §3, the strong-electrolyte paragraph | Ions are charged hard spheres with diameter σ_j equal to a_j. Dispersion acts only water–water and water–ion. |
| Figiel, Yu & Held 2025, IECR, doi:10.1021/acs.iecr.5c00475 (YEENX35P) | ePC-SAFT section, Eq. 4; Born-term section; Model Parameters | d_ion = 0.88σ. "In all former ePC-SAFT modeling approaches, d_Born was set to σ_i". The Born diameter "is not well-defined". It is fitted to infinite-dilution solvation Gibbs energies of inorganic ions: 1.218–4.985 Å, Table 3, as recorded in amendment 3 §2. |
| Bülow, Ascani & Held, FPE 535 (2021) 112967 (L79J5R52) | Conclusions | Unified ion diameters for DH and the Born term are "apparently feasible". |
| Fakouri Baygi & Pahlavanzadeh 2015, ChERD, doi:10.1016/j.cherd.2014.07.017 (B8EJJPCJ) | Abstract; §1 and Fig. 1. §3.3 as recorded in amendment 3 §2 | PC-SAFT physical absorption with ideal Smith–Missen chemistry; the ions carry no equation-of-state parameters. |

**What the practice amounts to.**

1. *Published convention.* Protonated amines are represented two ways within
   the same group: as charged copies of the amine (Uyan, Wangler), or as
   one-segment spheres carrying the amine's σ and u (Cleeton, Bülow 2021a). All
   four papers state that like-ion dispersion is excluded and that d = 0.88σ
   for ions.
2. *Textual basis for the diameter.* Held 2014 (after Eq. 22) and Uyan (after
   Eq. 11) derive 0.88σ from the zero self-dispersion. An ion that keeps its
   self-dispersion is therefore consistent only with Eq. 22. This does not rest
   on the MDEA numerical inference.
3. *Carbamate has no published ePC-SAFT parameters.* The only organic-anion
   *chain* parameters in the group's work read here are the IL [Ac]⁻ values
   (Ji & Held 2016 Table 3, reused in Bülow 2021a Table 2), used with their
   published m = 3.7266. They are not the only acetate parameters: Held 2014
   Table 2 (strategy 2) has an aqueous acetate sphere (m = 1, σ 3.9328 Å,
   u 150 K, k with water −0.23).
4. *DH distance.* The printed DH distance is σ (Held 2008, Cameretti, Uyan).
   This repository declares 0.88σ for every ion, the inorganic ions included
   (for example HCO₃⁻ 2.578048 = 0.88 × 2.9296). That convention traces only to
   the retired Phase-2 artifact locator. Whether it is deliberate is not
   established (§15).

## 4. The four suggested options, judged

| Option | Disposition | Reason |
|---|---|---|
| (i) MEAH⁺ and carbamate as charged molecules | **Candidate A, primary** | Literature practice for the protonated amine (Uyan, Wangler). Held 2014's own derivation of the diameter rule supports it. The MDEA numerical lead and the §2 volume inference point the same way. |
| (ii) Untie the 0.88 packing/DH ties | **Probe P only, no fit** | Untying adds four columns to a block already at condition 3.7e4. P (§10, step 1) splits the A4 size gradient into its σ, packing and DH parts. If all three point outward, untying would send each to its own bound, and (ii) is dropped. If they disagree in sign, (ii) is kept as a fallback for a later amendment. |
| (iii) Born-diameter treatment | **Candidate B, conditional** | Run only if A leaves a Born diameter on a bound. The diameters are fixed at a declared molecular size rather than widened, because they swing bound to bound (§2). |
| (iv) Wider bounds | **Not proposed** | *Sizes:* 5.8 Å already exceeds every Held 2008 Table 2 ion except choline (5.9216 Å; amendment 3 §2). A larger sphere would stand in for a molecular volume, which is the form question. *k = −1:* this matches the most negative printed opposite-ion values (Held 2014 Table 3, ±1). No source read supports u_ij > 2√(u_i u_j). *Born:* handled by B. |

## 5. Candidate A: MEAH⁺ and carbamate as charged molecules

### 5.1 Model form

The dispersion pair energy is the Engine's `same_sign_ionic_dispersion`
(`engine/native/contributions/helmholtz.hpp` ≈ 474–486 at Engine `21e761c3`).
Self pairs i = j fall inside the sum, so same-sign exclusion also removes ion
self-dispersion:

$$
\epsilon_{ij}=\begin{cases}\sqrt{u_iu_j}\,(1-k_{ij}), & z_iz_j\le 0\ \text{or all ion pairs}\\ 0, & z_iz_j>0\ \text{under same-sign exclusion.}\end{cases}
\tag{A5-1}
$$

Candidate A keeps ε_ii = u_i for i ∈ {MEAH⁺, carbamate}, with k_ii = 0. It
keeps ε_ij = 0 for unlike same-sign ion pairs and leaves the inorganic ions
unchanged. The two MEA ions take their parent molecules' segment numbers:
MEA (m 3.0353, σ 3.0435 Å, u 277.174 K, the repository's MEA record) for
MEAH⁺, and [Ac]⁻ (m 3.7266, σ 3.5605 Å, u 533.11 K) for carbamate. The MEA
ions are non-associating, as in Bülow 2021a and Cleeton.

Because self-dispersion is kept, the hard-chain diameter follows the neutral
rule (Held 2014 Eq. 22; Uyan Eq. 11; Wangler Eq. 6):

$$
d_i(T)=\sigma_i\left[1-0.12\exp\!\left(-\frac{3u_i}{kT}\right)\right].
\tag{A5-2}
$$

The DH closest-approach distance is σ (Held 2008 Eqs. 2–3; Cameretti §3;
Uyan §2):

$$
a_i=\sigma_i .
\tag{A5-3}
$$

The Born diameter stays a separate SSM+DS coordinate (Figiel 2025), unchanged
from A4.

### 5.2 Engine-free construction (A0, the screen)

The pinned Engine `21e761c3` accepts ion segment counts other than 1 and
accepts `segment_count`, `packing_diameter` and `debye_huckel_diameter` as
coordinate targets (`engine/src/epcsaft/regression.py` lines 21–37). It
requires a declared, temperature-independent packing diameter for ions
(`helmholtz.hpp` ≈ 165–185; `parameter_builder.cpp` ≈ 491). It rejects a
self-pair k_ii (`pair_index`, ≈ 102–112) and requires an explicit k_ij on every
pair it does not exclude (≈ 528–534). A0 therefore uses:

- **The exact self-dispersion workaround from #126.** Set
  `ionic_dispersion = all-ion-pairs` and k_ij = 1 on the seven unlike same-sign
  ion pairs (MEAH⁺–H₃O⁺; carbamate–HCO₃⁻, –CO₃²⁻, –OH⁻; HCO₃⁻–CO₃²⁻, –OH⁻;
  CO₃²⁻–OH⁻). For each inorganic ion, set u_i′ = 10⁻⁸u_i and rescale every one
  of its k_ij so that u_ij is unchanged:

  $$
  1-k'_{ij}=(1-k_{ij})\sqrt{\frac{u_iu_j}{u'_iu'_j}} .
  \tag{A5-4}
  $$

  The free HCO₃⁻–water coordinate becomes k′ = 1 − 10⁴(1 − k), with bounds
  [−14 999, 1] and scale 100. That is the same optimizer coordinate; reports
  back-transform it. The declared inorganic u/k values change, so A0 documents
  cannot be adopted.

  A5-4 must hold at every temperature, so every term of a rescaled pair's
  k_ij law is rescaled. MEAH⁺–water carries `k_ij_reciprocal_temperature_slope`
  (−112.568 K at the start, +35.46 K at the A4 endpoint; reference 313.15 K),
  the only ion pair in the A4 documents with a second term. Whenever MEAH⁺
  is suppressed (document X, check 10), set b′ = 10⁴·b together with
  1 − k′ = 10⁴(1 − k). The #126 helper reads only `pair["coefficients"][0]`,
  so the construction must rescale every term, or assert that none exists.
  A0 itself is unaffected: MEAH⁺ keeps its self-dispersion, and no inorganic
  ion pair carries a slope.
- **Ion u fixed at the parent values (inherited, as in Uyan §4.1 and Wangler
  Table 5).** Eq. A5-2 then becomes a fixed linear tie of packing to σ at the
  pivot 313.15 K: f₊ = 0.991567 for MEAH⁺ and f₋ = 0.999274 for carbamate
  (declared at full double precision). **This is the one approximation.**
  Over the ion-bearing row temperatures, 293.15–353.15 K, the exact factor
  differs from the pivot by at most 0.30 % (MEAH⁺) and 0.057 % (carbamate);
  check 7 brackets this. The temperature derivative ∂d/∂T is dropped in the
  8 heat and 4 heat-capacity rows; check 8 is only a scoring sensitivity for
  it. The 39 Kiepe rows contain no ions. Carbamate's inherited u is the weak
  point of this choice (§5.4) and an owner decision (§14).

### 5.3 Exact form (A1, adoption grade)

A1 frees both ion u again (14 coordinates, matched to the A4 control). This
needs the Engine declaration described on #499 (§12): a per-ion
"charged-molecule" flag that keeps the self pair, excludes unlike same-sign
pairs, and supplies Eq. A5-2 with exact T and u derivatives. A1 then needs no
workaround and no pivot tie. It runs from two starts on both dielectric
branches. A1 is admitted only after A0 is positive, or negative only at
inherited u (§9), and after the owner's budget decision.

### 5.4 A0 coordinates, bounds, scales and starts

There are 12 free coordinates, in A4 order, with the two ion dispersion
energies removed. The start is the A4 larger-d_V control start, with only the
ion form changed.

| # | Coordinate | A0 start | Bounds | Scale | Change from A4 |
|---|---|---|---|---|---|
| 1–3, 5 | carbamate–water k, MEAH⁺–water k, HCO₃⁻–water k, MEAH⁺–water reciprocal-T slope | A4 control start | A4 | A4 | HCO₃⁻–water carried in the A5-4 form |
| 4 | carbamate–MEAH⁺ k | A4 control start | [−1, 1] | 0.01 | none |
| 6 | MEAH⁺ size: σ ×1, packing ×0.991567, DH ×1 | σ = 3.0435 Å | [2, 5.8] Å | 0.1 Å | was 3.563 Å with ties 0.88/0.88; m 1 → 3.0353 |
| 7 | carbamate size: σ ×1, packing ×0.999274, DH ×1 | σ = 3.5605 Å | [2, 5.8] Å | 0.1 Å | ties 0.88/0.88 → as listed; m 1 → 3.7266 |
| 8–9 | MEAH⁺ and carbamate Born diameters | 3.563, 3.5605 Å | [2, 5] Å | 0.1 Å | none |
| 10–12 | R5 a_k; R2 and R5 enthalpy shifts | A4 | A4 | A4 | none |
| fixed | MEAH⁺ u 277.174 K; carbamate u 533.11 K | — | — | — | were free (A4 endpoint 241.97 and 210.98 K) |

**Tied start values.** Engine coordinate targets are proportional: each
target is coefficient × q (`engine/native/regression/coordinates.cpp:164`).
The start check requires each stored tied value to equal coefficient × q
within 8 ulp (`:132–150`). The A0 start document's packing diameters must
therefore be written as exactly the spec's tie factor × σ, using the same
double. Any document whose diameters break the A0 ties (checks 7 and 10)
needs a spec with matching factors or with no tied ion coordinate (§11).

**The box is kept in σ only, so a positive result is nearly built in.** In
the quantities the bound stands in for (§2), the A0 box is far larger than
A4's (reviewer arithmetic, rechecked). At σ = 5.8 Å, m·d³ reaches 577 Å³
(MEAH⁺) and 726 Å³ (carbamate), against 133 Å³ at the A4 bound (4.3× and
5.5×). The opposite-ion weight m₊m₋σ±³ reaches 2,207 Å³ against 195 Å³ (11×).
The A4 endpoint volume maps to σ ≈ 3.56 Å (MEAH⁺) and 3.29 Å (carbamate),
well inside the box. The A4 cation–anion dispersion strength maps to
k ≈ +0.44 at the parent σ. So an interior endpoint does not separate "chain
form" from "the sphere box was too small". The optional equal-volume sphere
evaluation in check 10 is cheap evidence on that question; it does not decide
it.

**Carbamate u is fixed at 533.11 K.** This is the IL acetate value, fitted
to neat-liquid densities with dielectric constant 1 (Ji & Held 2016). It lies
above Held 2014 §2.4's 400 K screening cap, and A4 moved it to 211 K. Keeping
the A4 carbamate–water dispersion strength at the parent σ needs k ≈ 0.56
(reviewer arithmetic, rechecked), outside [−0.5, 0.5]. The likely outcome is
carbamate–water k at +0.5; §9 states in advance how that bound is read.

CO₂–MEA stays at (0, 0), matching the control. The neutral pair was
cost-neutral in A4.

## 6. Candidate B (conditional): Born diameters fixed at a declared molecular size

B runs only if A0 is positive (§9) but a Born diameter ends at 5.0 Å. Remove
the two Born coordinates (10 free). Fix each Born diameter at the
equivalent-sphere diameter of the ion's declared hard core:

$$
d^{\mathrm{Born}}_i=\big(m_i\,d_i^3\big)^{1/3}\;\Rightarrow\; 4.369\ \text{Å (MEAH⁺)},\quad 5.516\ \text{Å (carbamate)},
\tag{A5-5}
$$

evaluated at the parent σ before any fit. This is engineering judgment. Figiel
2025 fits Born diameters to solvation Gibbs energies, and the repository holds
no such data for MEA ions. Bülow 2021a sets Born equal to the DH diameter, but
for a chain ion that is the segment size (3.04/3.56 Å), not the ion's size.
Everything else is identical to the A0 endpoint run, except that B's
coordinate order keeps R5 a_k at index 9 (§11).

## 7. Rows, weights and the control

Reuse the A4 larger-d_V control objective unchanged: `control-fit-spec.json`
observations and direct rows, λ = 0, 205 positive-weight rows. These are 47
common pressures (weight 1/0.3²), 94 common species, 8 Vinjarapu heats,
7 restored species, 6 pooled Jakobsen ratios, 39 Kiepe pressures (weight 1/39)
and 4 Hilliard heat capacities. The 12 Amundsen loaded densities keep zero
weight and are reported only. A new form does not justify new weights.

Cost partitions are C = ½Σr²: **C166** (all but Kiepe), **C149** (common) and
**C154** (C166 without the 12 caloric rows, used only as a robustness check).
The control is the A4 larger-d_V control endpoint (`control/native.json`
`ad235fe6…`; endpoint document `control/usable-budget-endpoint.json`
`365758b8…`). Its values are **C166 = 39.6902, C149 = 24.5609,
C154 = 36.7524**: 39.6902 − 0.6898 (heats) − 2.2480 (heat capacity), from
`matched-checks.json`. It is reused as it stands; no control is rerun.

## 8. Numerical checks, with the amendment-4 lessons

1. **Start release test (existing guard).** All 205 rows available at the A0
   start. The mandatory free block has full rank and condition ≤ 1e4. On the
   existing guard, A0's last two columns (the R2 and R5 enthalpy shifts) take
   the place of A4's two optional columns, so all 12 free columns must also
   have condition ≤ 1e4 (§11). The A4 start passed at 3.45e3 (mandatory) and
   6.39e3 (all free columns). Failure stops before the fit.
2. **Workaround exactness.** Document X is the A4 control start with A5-4
   applied to all six ions, the MEAH⁺–water slope included (§5.2), and k = 1
   on the seven unlike same-sign pairs. It must reproduce the control start's
   weighted residuals on all 205 rows within 1e-8; #126 measured about 5e-10.
   Failure means a construction defect: stop.
3. **Endpoint completeness and replay.** Converged within 100 iterations at
   function tolerance 1e-6 (as the control). All 205 rows available; rank 12.
   Cold replay of the written endpoint document ≤ 1e-8 per weighted row and in
   relative cost. Kiepe invariance ≤ 1e-8.
4. **Stationarity replaces the 1e-8 projected-gradient limit.** *Lesson: a
   1e-6 function tolerance cannot reach a 1e-8 projected gradient.* Require
   the GN step on the free columns to predict a decrease ≤ 1e-4 × C166
   (≈ 0.004, about 1/500 of the 5 % band). A4 reached 2.4–3.6e-4 absolute
   (6–9e-6 relative). Every held coordinate's gradient must point outward.
5. **Derivatives: A4's every-step rule, or clean order 2.** *Lesson:
   fixed-step misses came from h² truncation.* Centered differences at
   optimizer steps 0.01 and 0.005 (the existing checker), against 1e-8
   absolute or 1e-5 relative per row. A column passes if both steps meet the
   tolerance. Failing that, it passes on clean order-2 convergence: the
   ratio of the per-column maximum absolute errors at the two steps (the
   maxima the checker records, not per-row errors) lies in [3.5, 4.5]. The
   multi-target size columns are included. A4's misses were on the two
   u columns (ratio 4.0), which A0 drops. A failure that shows neither is a
   stop.
6. **Conditioning governs parameter claims, not the decision.** *Lesson: the
   3.7e4 endpoint condition lay along bicarbonate–water k and could not move
   the cost.* Report the free-block singular values and the near-null
   subspace N: the span of the right singular vectors whose singular values
   are below σ₁/1e4. A4's 14 endpoint columns had three such values (1.2e-3,
   1.0e-3, 2.8e-4, against σ₁ = 17.4). Above condition 1e4, make no claim
   that an individual value is determined. The interior status of σ₊, σ₋ and
   k counts toward the decision only if the free-block condition is ≤ 1e4, or
   if each of their unit vectors projects onto N with norm below 0.5.
7. **Pivot-diameter bracket.** Evaluate the endpoint again with both ion
   packing diameters at f(293.15 K)σ and at f(353.15 K)σ. These are exact for
   rows at those temperatures. Bound |C_exact − C_pivot| by
   Σ_r max(|c_r(293.15) − c_r(313.15)|, |c_r(353.15) − c_r(313.15)|). The bound
   must be ≤ 1 % of C166. These documents break the A0 ties, so they use the
   evaluation spec (§11).
8. **Caloric scoring sensitivity.** The §9 verdict must be the same with C154
   as with C166. This is a scoring sensitivity, not a bracket on the dropped
   ∂d/∂T. The fit still uses the 12 caloric rows, and the free R2 and R5
   enthalpy shifts can absorb part of the error (reviewer's rough estimate:
   a few kJ/mol CO₂ per heat row).
9. **Release of u (interpretation of a negative).** A column "u ×1, packing
   ×σ·f′(u)" cannot be declared: it would set packing ≈ 0.07 Å and fail the
   start check (§5.4). Instead, evaluate the Jacobian at the A0 endpoint with
   the probe-P layout (untied σ, packing, DH, segment count, Born and u per MEA
   ion, so no slot is targeted twice). Combine the columns offline in physical
   units: the tied size column is J_σ + f·J_packing + J_DH, and the u column is
   J_u + σf′·J_packing, with f′ = ∂f/∂u = 8.079e-5 K⁻¹ (MEAH⁺) and
   6.958e-6 K⁻¹ (carbamate) at the pivot. Report ΔC_u, the extra GN-predicted
   decrease from adding the two u columns to the A0 free block, ignoring their
   bounds. It is a local linear estimate, not a bound, and can under-predict a
   move as large as A4's 533 → 211 K.
10. **Attribution (interpretation; sets the scope of the Engine request).**
    Make three single evaluations at the A0 endpoint: MEA-ion DH back to
    0.88σ; MEA-ion self-dispersion removed (A5-4 applied to them, with
    b′ = 10⁴·b on MEAH⁺–water); MEA-ion packing back to 0.88σ. *Optional, same
    cost:* one equal-volume one-sphere evaluation (m = 1; packing and DH
    diameters (m·d³)^{1/3} at the endpoint; σ = that/0.88; no self-dispersion;
    A4 electrolyte rules). Report ΔC166 for each. All use the evaluation spec
    (§11).
11. **Densities (report only).** Report signed errors on the 12 loaded
    Amundsen densities at the control endpoint (probe P) and at the A0
    endpoint (the check-9 call). The stage-7 owner target of ≤ 2 kg/m³ is the
    reference, not a gate.

## 9. Falsifier and decision rule

**Hypothesis H5.** At the inherited parent parameters, the charged-molecule
form (A5-1 to A5-3) removes the A4 bound activity of the two ion sizes and of
carbamate–MEAH⁺ k without a material loss of fit. The A0 box is far larger
than A4's in molecular volume and dispersion weight (§5.4). A positive result
therefore shows that the bounds go away at the parents' declared volume and
dispersion. It does not show that the chain form, rather than a larger
sphere, is needed; the optional sphere evaluation (check 10) is the only
evidence on that.

The thresholds are engineering judgment. 5 % is the cost accepted for
removing these bound directions and two free coordinates. It is about 40
times the largest A4 arm or branch difference (0.12 %). 10 % mirrors the
decision size used in amendments 3 and 4. With the control values:
1.05 × C166 = **41.67**, 1.05 × C149 = **25.79**, 1.05 × C154 = **38.59**,
1.10 × C166 = **43.66**, and 0.05 × C166 = **1.98** (the threshold for ΔC_u).
The endpoint is **valid** when checks 3, 4, 5 and 7 pass. A positive result
also requires checks 6 and 8.

| Outcome | Conditions at a valid A0 endpoint | Next action |
|---|---|---|
| **Positive** | σ₊, σ₋ and carbamate–MEAH⁺ k each at least one scale unit inside their bounds, with check 6 satisfied; no other non-Born coordinate on a bound; C166, C149 and C154 within 1.05 × control | Smaller-d_V A0. B if any Born diameter is on a bound. The orchestrator adds #170's use case on Engine #499. A1 after the capability; then stages 5–7 on the new form, as the owner decides |
| **Negative** | σ₊, σ₋ and k all still on a bound (the A4 pattern), and ΔC_u < 1.98 | This form, at the inherited parents, does not remove the A4 pattern at inherited u, nor at released u to linear order. No B; #170 adds no use case to #499. *Optional before declaring it:* a second A0 start. The owner chooses between a Born-treatment design and accepting the bounds |
| **Negative at inherited u only** | As Negative, but ΔC_u ≥ 1.98 | Inconclusive for the form; A1 (Engine) decides |
| **Mixed** | One or two of σ₊, σ₋, k interior; or all three interior but C166 > 43.66; or all three interior within the 5 % band but another non-Born coordinate on a bound. *Stated in advance:* carbamate–water k on a bound is read through check 9, as a sign of the inherited carbamate u (§5.4); ΔC_u ≥ 1.98 there points to the u choice, not the form | Report which coordinates moved, with checks 9 and 10. No B; no use case on #499 yet. Owner, starting with the carbamate parent and u (§14) when check 9 points there |
| **Inconclusive** | Anything else: all three interior with a cost between the bands; check 6, 7 or 8 failing | Report; owner |

**B's rule.** Measured against the A0 endpoint (or A1, when B follows A1).
*Positive:* valid, no new active bound, C166 and C149 within 1.05 × A. Then
the data do not determine the Born diameters beyond the declared size, and
they stay fixed, labelled as declared. *Negative:* C166 > 1.10 × A. The data
need Born diameters outside the declared size, and no MEA-ion solvation data
exist here; the owner decides. *Inconclusive:* anything else.

## 10. Sequence, compute and stops

Run on the pinned wheel `main-21e761c3` (SHA-256 `d2f61e3a…0357`), verifying
the installed bytes and every input hash first. Launch with `nice -n 10`, one
native pool of 32 workers and single-threaded BLAS. Calls run in sequence.
Expected times use the A4 ledger: information calls about 36 s and 36 CPU-s;
reactive fits 202–225 s and 2,991–3,247 CPU-s; endpoint checks about 171 s
and 3,700 CPU-s for two arms of 56 derivative evaluations each (so about
1,850 CPU-s per arm).

| Step | Work | Expected wall / CPU | Per-call limit |
|---|---|---|---|
| 1 | **Probe P** at the A4 control endpoint: untied columns per MEA ion (σ only, packing, DH, segment count, Born, u) plus the other 8 coordinates, as an information spec with `information_density_weights: []`; g = Jᵀr per column. Recomposed tied gradient = A4 tied column within 1e-8 relative; densities | ≈ 40 s / 40 | 180 s |
| 2 | Check 2 (document X, evaluation spec) and check 1 (A0 start release) | ≈ 80 s / 80 | 180 s each |
| 3 | **A0 fit**, larger d_V, ≤ 100 iterations | ≈ 230 s / 3,300 | 600 s native + 120 s backstop + ≤ 60 s teardown; 12,000 CPU-s post-call stop |
| 4 | Checks 3 and 5 with the existing checker, A0 as its "variant" (48 derivative evaluations, plus 56 for the re-evaluated control, 28 processes); checks 7, 9, 10 and the optional sphere (≤ 7 information calls); decision | ≈ 420 s / 3,700 | checker under `timeout 600`; 180 s each otherwise |
| — | **Required subtotal** | **≈ 770 s / 7,100 CPU-s** | |
| 5 | If positive: smaller-d_V A0 (check 1, fit, checks 3–8) | ≈ 500 s / 6,900 | as steps 2–4 |
| 6 | If positive with a Born bound: B, larger d_V | ≈ 490 s / 6,600 | as steps 2–4 |
| — | Optional, before a Negative: a second A0 start (check 1, fit, checker) | ≈ 430 s / 6,800 | as steps 2–4 |

**Proposed allowance:** 3,000 compute-s and 30,000 CPU-s. The code admits a
fit only if ≥ 720 s (600 s native + 120 s backstop; the teardown is outside
the guard) and ≥ 12,000 CPU-s remain in both the spec's allowance and the
program. The entry ledger is 10,532 of 21,600 compute-s and 93,620 of 144,000
CPU-s, with the 1,950.38 s check reserve held. Even if the whole allowance is
used, at least 6,118 s (net of the reserve) and 20,380 CPU-s remain. A1 is not
inside this allowance (§12).

**Spec details that differ from the A4 files.**

- Wheel: `build/engine-wheels/main-21e761c318c2ac5b555a245365c844d38a93e4cb/epcsaft-0.2.0.dev0-cp313-cp313-manylinux_2_39_x86_64.whl`
  (SHA-256 `d2f61e3a…0357`, checked). A4's `wheel_path` under
  `tmp/amendment-4-21e761c3/` no longer exists. Paths resolve against the
  root of the checkout that runs the campaign; a task worktree has no
  `build/`.
- `program_prior_cpu_s` and `program_prior_wall_s` come from the current
  ledger, 93,619.61 CPU-s and 10,532 s (the A4 specs carry 72,638.61 and
  9,210), and each later spec adds the calls before it.
- The checker has no time limit of its own; run it under `timeout 600`.

**Program note for the owner.** Stage 6 as designed (16 F1 fits and up to
20 F2–F6 fits) needs about 108,000–117,000 CPU-s at the measured λ = 0 cost on
this wheel, plus density-weighted fits that have not been timed. That exceeds
the 50,380 CPU-s now left, with or without amendment 5. The program CPU cap
needs a decision before stage 6.

**Stops.** Each of the following stops the run and is reported:

- an unavailable row at a start or endpoint (no row is dropped);
- failure of check 1 or check 2;
- a fit not converged within its limits (a time-limited vector is not an
  endpoint);
- a failure of cold replay or Kiepe invariance (diagnose before deciding);
- a derivative failure under check 5;
- an inadmissible next call;
- any spurious phase behavior seen in a row solve. Held 2014 §2.4 warns of
  this for high ion dispersion energies; it bears on carbamate, now a chain
  with u = 533.11 K and self-dispersion.

None of these stops is evidence that the model cannot fit MEA.

## 11. Code and ownership

Campaign code stands at **1,000 of 1,000** lines, counted as non-blank,
non-comment executable lines against base
`6c8d20073fd0e5fda8dd323a51f55551d12b7486` (`amendment-4/compute-ledger.json`).
Specs, start documents and coordinate declarations are JSON and are not
counted. **A0, B and probe P need no new campaign code.** This holds if the
owner ratifies the exclusion of uncounted scratch that the ledger already
lists as pending (§14, decision 2). The existing routes:

| Need | Existing route |
|---|---|
| A0 start, X, B and the check-7/9/10 documents | One recorded one-off command (disclosed scratch; its text kept with the results) calling #126's `conventions.self_dispersion` (`analyses/mdea_kuranov_refit/conventions.py`) and `shared_evaluation.with_parameter_values`. The helper rescales only `pair["coefficients"][0]`. The command therefore rescales the MEAH⁺–water slope by hand for X and check 10, and asserts that no other rescaled pair has a second term |
| A0 fit and check 1 | A 12-coordinate JSON spec on the existing stage-6 path. The release test treats the last two columns as optional; in A0 these are the R2 and R5 enthalpy shifts, so the test is strict but its `dispersion_release_passed` field is mislabelled. R5 a_k stays at zero-based index 9 (row 10 in §5.4) with scale 80, because `fit_campaign.py:562` hard-codes both. B's 10 columns are reordered for the same reason (…, R2 shift, R5 shift, R5 a_k) |
| Probe P and check 9 (Jacobians) | Information specs with `information_density_weights: []` (the release test is skipped), with untied ion columns |
| X and checks 7 and 10 (costs only) | The **evaluation spec**: the same, but with only the three reaction coordinates (R5 a_k, R2 and R5 shifts). Diameters, energies and k values that no longer match the ties or bounds then cannot fail the start check |
| Checks 3 and 5 | `check_matched_co2_mea.py` unchanged, run in a directory with the A4 control as "control" and A0 as "variant". It re-evaluates the control too (≈ 1,850 CPU-s). Its `decision` and `checks_passed` fields apply A4's rules and are not read |
| Checks 4, 6, 8 and 9, the §9 decision, the HCO₃⁻–water back-transform | Disclosed scratch post-processing of the written native results |

If the owner declines the exclusion, the counted route needs about 15 lines
(reviewer estimate), not the 54 estimated in the first draft.

**One owner for the workaround.** A0 imports #126's `self_dispersion` rather
than copying it. **Retirement:** once the Engine flag is pinned (A1), the
A0 documents and the one-off command are superseded; #126 keeps its own
helper. **Evidence that must survive:** the check-2 exactness result and the
A1 Engine acceptance reproducing the A0 documents.

## 12. Engine dependency

**A0, B and probe P need no Engine change.**

**A1 needs the capability described in Engine comment 6252262739 on
ePC-SAFT #499.** This repository already filed that use case through #126
(MDEA). It is not yet an accepted Engine issue; the Engine orchestrator owns
its body and build. A0 decides only whether #170 adds the MEA use case below
by comment (the orchestrator posts it, after a positive A0):

- **Declaration.** Flag MEAH⁺ and carbamate as charged molecules. The self
  pair is kept (k_ii = 0) and unlike same-sign pairs stay excluded under
  `exclude-same-sign-ion-pairs`. The packing diameter is Eq. A5-2 rather than
  a declared `packing_diameter`. DH and Born diameters stay declared.
- **Quantities consumed.** All 205 A4 rows plus the 12 densities. This needs
  exact `regression.fit` derivatives in σ and u (including the diameter
  coupling), and exact temperature derivatives of the ion diameter inside
  addition-enthalpy and equilibrium heat-capacity observations.
- **Acceptance.** Flagged documents reproduce A0-construction documents with
  packing at f(T)σ within 1e-10 in ln φ and Z at 293.15, 313.15 and
  353.15 K, at several compositions. Existing documents give byte-identical
  results. Centered differences in σ, u and T, the latter including heat
  capacity, agree within 1e-5 relative. The MDEA criteria on #499 still hold.

A new wheel must come from merged Engine `main`, be pinned by SHA-256, and be
requalified: frozen records replay within 1e-8 before A1. Estimated cost of
A1 is about 1,000 s and 12,000 CPU-s per branch including requalification,
admitted by the owner.

## 13. Claim limits

- A0 screens a declared form: inherited parent segment numbers and dispersion
  energies, a packing diameter frozen at 313.15 K (values bracketed by check 7;
  ∂d/∂T dropped, with check 8 only a scoring sensitivity), and an exact
  algebraic workaround
  that changes the declared inorganic u/k values. It runs on one start and one
  dielectric branch. It is not adoptable.
- The parents are analogs. MEA stands in for MEAH⁺, as MDEA did for MDEAH⁺.
  The IL anion [Ac]⁻ (fitted to neat-IL densities at ε = 1) stands in for
  carbamate. An interior fitted σ is a conditional effective size, not a
  measured ion property. No MEAH⁺/carbamate salt osmotic, density or solvation
  data are used.
- The MDEA lead is numerical inference about published implementations, not a
  stated convention. MEAH⁺ association (Uyan, Wangler) is not represented.
  The inorganic ions keep the repository's DH = 0.88σ.
- A positive A0 motivates the Engine request and A1. It is neither A1 nor
  adoption. Because the A0 box is far larger than A4's in volume and
  dispersion weight (§5.4), a positive A0 does not show that the chain form is
  needed rather than a larger sphere; the optional equal-volume sphere is a
  single evaluation, not a fit. A negative A0 shows only that this form, on
  this objective, does not remove the bounds. It does not show an
  equation-of-state limitation. A mixed result is attributed only as far as
  checks 9 and 10 allow.
- Phase stability under the new form is not assessed here; the stage-7 flash
  family covers it. The densities are report-only comparisons.

## 14. Proposals taken while the owner is away, and open owner decisions

**Reversible proposals in this design.**

1. A is the primary candidate; B is conditional; (ii) is handled by probe P;
   (iv) is declined.
2. A0 inherits m and u from the parents (carbamate's parent and u: decision 3
   below).
3. The MEA ions use DH = σ.
4. MEAH⁺ is non-associating.
5. CO₂–MEA stays at (0, 0).
6. Larger d_V runs first; smaller d_V only on a positive result.
7. Function tolerance 1e-6. The stationarity, derivative and conditioning
   rules of §8 replace the A4 fixed limits for the decision.
8. The 5 % and 10 % bands, and the §9 reading of a carbamate–water bound.
9. B fixes Born at the hard-core equivalent sphere.
10. The 3,000 s and 30,000 CPU-s allowance.
11. The zero-new-code route of §11, including the evaluation spec.

**Open owner decisions.**

1. **Direction after A4 (still open from the A4 result comment):** revisit the
   ion model form, or accept the bounds and proceed. The orchestrator chose
   "revisit the ion model form" while the owner was away; this design follows
   that default.
2. **Code ceiling:** ratify the exclusion of uncounted scratch already listed
   as pending in `amendment-4/compute-ledger.json` (the 17-line figure script
   and the ignored diagnostics in `tmp/`). A0 then needs no new campaign code
   (§11). Otherwise about 15 counted lines and a ceiling raise.
3. **Carbamate parent and fixed u:** the default is the IL [Ac]⁻ chain
   (m 3.7266, σ 3.5605 Å, u 533.11 K). Its weaknesses are in §5.4. Held 2014's
   aqueous acetate sphere is the only other published acetate set read here
   (§3).
4. **Engine use case:** the MDEA use case is already on #499 (comment
   6252262739, via #126). A0 decides only whether #170 adds the MEA use case.
   Run A0 now with the temporary workaround (recommended: about
   13 compute-minutes), or wait for the #499 flag. Posting stays with the
   orchestrator.
5. **Program CPU cap before stage 6** (§10 note).
6. **Scope:** should the inorganic ions' DH diameter follow its source
   convention (σ) rather than 0.88σ?
7. **Carried from A4:** the neutral pair or (0, 0) for later stages;
   ratification of the Peng–Robinson residual as a disclosed limitation; the
   Xu role (orchestrator default: B1-qualified, comparison-only, with the
   Hartono-only neutral fit kept).

## 15. Sources read, and what could not be established

**Read for this design.** The #170 body, design parts 1 and 2, and the last
four comments. The A4 READMEs and design. `matched-*` specs, start documents,
native results, checks and release tests. The A4 notebook section. The
Route 1, Route 2 and Route 2b READMEs and the Model D README. The #126
"Convention diagnosis" and its `model.py`/`conventions.py` declarations.
Engine comment 6252262739 and the #499 body. Engine source and the equation
document at `21e761c3` (upstream `main` ref): the sections cited in §5 and
`equations.md` `ionic_packing_diameter` and `same_sign_ionic_dispersion`. The
§3 papers. The amendment-3 design §2 supplied the Held 2008/2014 table ranges,
Figiel Table 3 and the Nasrifar/Najafloo summaries; those were not reread here.
**Read for the revision:** the readiness review; the #170 Xu comment;
`amendment-4/compute-ledger.json`; the A4 control spec, start and endpoint
documents, release tests and `matched-checks.json`; `fit_campaign.py`
(the stage-6 path, the release test, the 720 s guard, line 562);
`check_matched_co2_mea.py`; `conventions.self_dispersion`;
`shared_evaluation.with_parameter_values`; Engine `coordinates.cpp:132–164`
and `helmholtz.hpp` 166–185 and 466–487 at `21e761c3`; Held 2014 §2.1 and
Table 2 (shelf copy hash equal to the Zotero file).

**Not established.**

- Whether an explicit-ion ePC-SAFT MEA paper exists outside the searched
  corpus.
- Any carbamate ePC-SAFT parameters, or MEAH⁺/carbamate salt or solvation
  data in the repository.
- The hard-chain diameter rule Ji & Held 2016 used for IL ions: §2 refers to
  another paper.
- The MDEAH⁺ segment number as printed by Uyan: Table 4 omits it.
- Whether the repository's DH = 0.88σ was a deliberate choice: it traces only
  to a retired artifact locator.
- The size of the dropped ∂d/∂T in the caloric rows; check 8 is a scoring
  sensitivity and does not measure it.
- Whether the Engine accepts two coordinates targeting the same slot; the
  design avoids it (check 9 uses untied columns).
- Phase stability of the chain-ion form.
- The Engine timeline for #499.
