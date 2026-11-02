# Draft experiment: do MEA shared-species parameters transfer to aqueous PZ?

Parent: [#220](https://github.com/tannerpolley/Amine-Thermodynamics/issues/220). Research and design delivery: [#237](https://github.com/tannerpolley/Amine-Thermodynamics/issues/237). It follows the [AMP draft](../amp_pz_scoping/design-draft-amp.md) and reuses its frozen inputs, numerical checks, phase gate and evidence standard. Only what PZ changes is written here. **This is a draft that needs owner decisions and an independent readiness review. No fitting is authorized.** Readiness verdict: **Block for numerical Build**, for the reasons in the table below.

## Question and intended use

With every shared-species quantity fixed at the selected MEA record, can the adopted MEA ePC-SAFT formulation, extended by PZ, its four ions and the zwitterion, describe aqueous PZ CO2 pressure and NMR speciation inside the liquid window? The result would be a bounded single-amine transfer assessment and a PZ parameter record to seed the AMP/PZ blend. It would not qualify a rate-based absorber, solid-phase predictions, or states outside the declared liquid window.

## Model and frozen inputs

As in the AMP draft: the MEA hard-chain, dispersion, association, Debye–Hückel and SSM+DS Born formulation with the adopted permittivity law. Freeze H2O, CO2, H3O+, OH−, HCO3−, CO3²− and all shared–shared interactions from `analyses/mea_parameter_bundle/results/selected-current-best-parameters.json` (SHA-256 `00e77608a8489fc9e03a7d2a86c08cb5ff782bb441368a62fa6390b8bfe9cc91`). Freeze R1–R3, including the MEA R2 enthalpy shift. Bind the then-approved merged-main Engine wheel by commit and SHA-256 before any calculation; none is adopted here.

## Chemistry

Twelve liquid species, five PZ reactions P1–P5, vapor H2O/CO2/PZ: see [chemistry](chemistry.md). Source laws:

- P1/P2 from Hamborg 2009 Table 16 (293–353 K), mapped by numerical anchor. Hamborg's labels "first/second" are reversed between its theory section and its tables.
- P3–P5 from Ermatchkov 2003 Table 5 (283–333 K), reversed into hydrolysis form.

The Engine's `ReactionLogPolynomial` (ln K = a + b/T + c ln(T/Tref) + d T + e/T² + f T²) holds all three source forms:

- Hamborg's A/T + B + C ln T, with C ln Tref absorbed into a;
- Hetzer's log10 law with a linear T term, multiplied by ln 10;
- Ermatchkov's A + B/T, multiplied by ln 10 and negated for reversal.

Choose one route for the molality standard: either declare the source `standard_state_id` and a `ReactionReference` and let native code convert it, or convert by hand (ln K_x = ln K_m − 4.0165 for Δν = +1). **Never both.** Check one reference value per law, and the reciprocal for each reversal, before binding.

Analytical feed: one mole of PZ, the source amount of water, and the CO2 added. **Loading internally is mol CO2 per mol PZ.** Hilliard, Dugas, Freeman and Xu report mol CO2 per mol alkalinity = per 2 mol PZ. Bishnoi uses per mol PZ. Ermatchkov reports molalities. Convert explicitly in preparation and retain the source basis in each row's `source` metadata.

## Pure PZ and ion representations

The only published PZ PC-SAFT set is Razavi 2019 Table 1 (2B, σ³ prefactor), recorded in [pure-pz-pcsaft.md](sources/pure-pz-pcsaft.md). It was fitted to handbook and databank correlations, and its liquid density starts at 420 K. Numerical use is blocked until the reproduction check passes and the owner accepts subcooled-liquid extrapolation down to 313 K.

Candidate representations, following the AMP A/B comparison:

| Species | A: single sphere (MEA convention) | B: charged molecule |
|---|---|---|
| PZH+, PZH2²+ | m = 1, 0.88σ packing, fitted σ, u/k, Born diameter | m and sites from neutral PZ, zero self-association energy |
| PZCOO−, PZ(COO)2²− | one fixed representation in both variants, so A/B compares cations only | — |
| HPZCOO (zwitterion) | neutral, no Debye–Hückel or Born term, needs its own m, σ, u/k | — |

No published ePC-SAFT parameters exist for any PZ ion or for the zwitterion. That makes the zwitterion and the doubly charged ions the largest identifiability risk in this draft.

## Candidate coordinates (count not settled)

Listed so their size is visible; this is **not** an approved fit:

| Quantity | Count |
|---|---:|
| PZ–water k at 313.15 K and slope (from Hilliard D.2) | 2 |
| PZH+–water k; PZH+–HCO3− k | 2 |
| PZH+ σ, u/k, Born diameter (A) | 3 |
| PZCOO− σ, u/k, Born diameter | 3 |
| PZCOO−–water k | 1 |
| HPZCOO σ, u/k (m fixed) | 2 |
| PZ(COO)2²− σ, u/k, Born diameter | 3 |
| Carbamate law offsets for P3, P4, P5 (reaction coordinates) | 3 |
| PZH2²+ quantities | fixed/tied, not fitted |
| Total | 19 |

Nineteen coordinates against 62 + 121 + 46 calibration rows is not evidence of identifiability. Several carbamate species appear only lumped in NMR sums. Before any joint fit, compute scaled sensitivity rank on calibration data at the declared starts. Then tie or fix quantities on source evidence until the set is identifiable: candidate ties are a shared σ/u/k for PZCOO− and PZ(COO)2²−, or fixing the P4 offset. Do not add pair coefficients to cure a pressure residual. Bounds follow the AMP proposal; zwitterion and −2/+2 ion bounds need owner approval.

## Data roles and falsifier

Use the roles in the [data map](data-map.md#proposed-roles-not-frozen): calibration on Hilliard D.2, Hilliard D.5 and Ermatchkov 2003 NMR; Ermatchkov 2006 as the whole-campaign primary hold-out; Dugas 80/100 °C, Xu Pt and Bishnoi as secondary comparisons. The carbamate laws are fitted to the NMR rows, so **NMR agreement is calibration, not validation**. The pressure hold-out is the test.

Proposed pre-registered falsifier, needing owner approval of the metric and the limit: the CO2 partial-pressure log-ratio residuals on Ermatchkov 2006 rows at 313 and 353 K. Use the source uncertainty Δp = Δp* + 0.02p as the scale (p.1789). The 393 K rows are reported separately as extrapolation beyond the 333 K carbamate-law domain. No numerical limit is adopted. The MEA 24.2 % limit is not transferred.

## Liquid window and phase gate

The AMP phase gate applies (tangent-plane search, dense/gas classifier, unresolved trials block selection). PZ adds a solid gate (see [solid-phase.md](sources/solid-phase.md)):

- Exclude every row the source marks as precipitating, and every row inside the unloaded hexahydrate liquidus (Hilliard I.1) or outside Freeman's loaded envelope, before fitting.
- Report no prediction for a state outside the window.
- The Engine has only liquid and vapor phases, so a passing liquid calculation there is not evidence that the state is liquid.

## Driver gaps for PZ (#228/#233 code at `ec5e48a`)

| Need | Present driver | Gap |
|---|---|---|
| 12 species, 6 new | Components come from the endpoint parameter document. Charge is checked against the formula (`src/MEA/solvent_specification.py:111`). Species without an ideal-gas record must appear in a reaction (lines 113–117). | Not a code gap: all six PZ species appear in P1–P5. Neutral PZ needs an ideal-gas Cp record before any caloric claim. Native admission of twelve species with −2 and +2 charges and a neutral zwitterion is unqualified. |
| Diamine stoichiometry (two carbons in PZ(COO)2²−, two protonation steps) | Element and charge balance checked per reaction (lines 127–136) | None found in the code; unqualified numerically. |
| Lumped NMR groups | `amount_ratio` and `mole_fraction` accept species lists and denominator lists (MEA uses them) | None. Use two nonredundant ratios per row over all six PZ species. |
| Loading per molecule vs per alkalinity | Phase-state rows hard-code `T, P, water, alpha, amine` (line 78); dataset columns bind any names | Convert source α to per-molecule in preparation; single PZ fits the `amine` scalar. The blend still needs the row-expansion change named in the AMP draft. |
| Carbamate offsets | `reaction_coordinate` and `reaction_enthalpy_shift` are implemented (lines 221–236) | Three offsets are possible; their identifiability is unknown. |
| Solid phase | The phase test builds only liquid and vapor trials (lines 331–334); the Engine `PhaseKind` is `{Liquid, Vapor}` | **Gap.** Without an Engine solid capability, only a declared domain restriction is possible. Any hexahydrate model needs an Engine issue with this repository's use case; none is opened by #237. |
| Fitted-parameter hand-off | Blocked by ePC-SAFT#928, as for AMP | Unchanged |

## Sequence, stop conditions and owner decisions

Order: AMP remains first ([#227](https://github.com/tannerpolley/Amine-Thermodynamics/issues/227)/[#229](https://github.com/tannerpolley/Amine-Thermodynamics/issues/229) gates still open), then PZ, then the blend. PZ source preparation can run in parallel, because it touches no AMP input.

Stop for:

- an unresolved source basis or the D2O question;
- circular use of the NMR rows;
- a failed pure-PZ reproduction;
- native refusal of twelve species;
- weak identifiability or active arbitrary bounds;
- an unresolved phase or solid state in the window;
- hold-out failure.

Failures return to Design. Do not retune on the hold-out.

| Open decision | Recommendation | Effect |
|---|---|---|
| P1/P2 law | Authorize transcription and fit of Hamborg Table 16 to Eq.21, with uncertainty; Hetzer as cross-check | Covers 293–353 K; Hetzer alone stops at 323 K |
| Carbamate laws | Map Ermatchkov laws as the starting values; allow at most the identifiable offsets, fitted to NMR; score pressure only on the hold-out | Avoids claiming NMR as validation |
| D2O | Accept Ermatchkov's H2O treatment for now; record isotope bias as unquantified | Flags a possible systematic error in the speciation calibration |
| PZH2²+ | Keep it (P2 is sourced and adds no coordinate) | Hilliard's omission becomes a testable reduction |
| Zwitterion | Neutral, liquid-only, its own m, σ, u/k | No 10⁻⁵-charge workaround |
| Pure PZ | Run the Razavi reproduction first; refit only if it fails or the subcooled extrapolation is rejected | Settles neutral inputs before any ion fit |
| Ion convention | A and B side by side for the cations; one carbamate representation | As for AMP |
| Primary hold-out | Ermatchkov 2006, whole campaign, 393 K reported separately | Different lab from the pressure calibration |
| Solid handling | Domain restriction now; decide later whether to request an Engine solid capability | Liquid claims only |
| Wiley PDFs | Owner opens Kamps 2003 and Derks 2005 through the hand-off links | Needed before choosing between Kamps and Ermatchkov 2006 as hold-out, and to identify its precipitation rows |
| Loaded SLE boundary | Read the Freeman 2011 dissertation and the SINTEF crystallization work before using the rich-side limit; digitizing Freeman Fig.1 needs a separate authorization | Fixes the liquid window |

This draft contains no fitted value, Engine result or adopted parameter.
