# Published neutral PZ PC-SAFT set

Checked 2026-11-02 for #237. One published PC-SAFT set for pure piperazine was found. It traces to a single original paper. It is a candidate only: it has not been reproduced, and its use in the aqueous reactive model is not qualified.

## The candidate and its origin

Razavi, Khoshsima & Shahriari (2019), *Ind. Eng. Chem. Res.* 58, 11038–11059, DOI [10.1021/acs.iecr.9b01429](https://doi.org/10.1021/acs.iecr.9b01429), Table 1, p.11040 (PDF page 3), row "piperazine":

| Quantity | Value | Units |
|---|---:|---|
| M | 86.13 | g/mol |
| m | 2.6519 | dimensionless |
| σ | 3.7136 | Å |
| ε/kB | 274.10 | K |
| εAB/kB | 1923.25 | K |
| κAB | 0.07275 | dimensionless |
| Fitted P_sat range | 323–630 | K |
| Fitted ρL range | 420–570 | K |
| Reported AARD | P_sat 0.33 %, ρL 1.65 % | — |
| Vapor-pressure references | refs.100, 136 | — |
| Liquid-density reference | ref.130 (Yaws 2014) | — |

Esmaeili et al. (2020), *Process Saf. Environ. Prot.* 141, 95–109, DOI 10.1016/j.psep.2020.05.010, Table 1, p.97, prints m = 2.652, σ = 3.713 Å, ε/kB = 274.1 K, εAB/kB = 1923 K and κAB = 0.07275. Those are the Razavi values rounded, and its caption cites Razavi et al. 2019. Esmaeili uses PC-SAFT for **vapor-phase fugacities only**; the liquid is eNRTL (§2.1, p.97). It is therefore not evidence that this set works in an aqueous liquid. It is the same set, not a second one.

## Association scheme and convention

Razavi p.11046 (§ on heterocycles with –NH groups): "two association sites are considered per each molecule as type 2B in the terminology of Huang and Radosz". PZ has two N–H groups, yet the model uses one effective donor–acceptor pair, as for AMP. Razavi Eq.7, p.11045, prints the association strength as

Δ^{AiBj} = g_ij^hs(d_ij) [exp(ε^{AiBj}/kBT) − 1] σ_ij³ κ^{AiBj}.

So the volume prefactor uses **σ³**, not d(T)³. That settles for PZ the convention question #229 left open for AMP. It still has to match the Engine's association expression before the values are bound.

## Limits found by reading the source

- **The fitting data are compiled correlations, not primary measurements.** Ref.100 is Yaws & Satyro, *The Yaws Handbook of Vapor Pressure* (2015). Ref.136 is the Aspen HYSYS V9 databank (2017). Razavi's abstract calls them "experimental data". Ref.130 is Yaws, *Thermophysical Properties of Chemicals and Hydrocarbons*, 2nd ed. (2014), Chapter 3, “Density of Liquid – Organic Compounds”, pp.133–256. Neither the handbook coefficient rows nor the HYSYS export have been obtained; their primary origin remains unverified.
- **Phase of the fitted states.** Steele 1997 Table 8 p.1045 gives anhydrous PZ melting at 384.6 K. Razavi's pressure range starts at 323 K, below melting; it does not identify the reference branch there as solid-vapor or subcooled-liquid. Liquid density starts at 420 K. Owner-authorized aqueous use at 283–393 K therefore includes pure-property extrapolation; neither the original fit nor the verified liquid measurements physically validates subcooled PZ at 283 K.
- No binary PZ–water, CO2 or ion parameters are given. Razavi's binary systems are heterocycle–organic mixtures.

## Published-property check for #308 (11 November amendment)

The [owner amendment](https://github.com/tannerpolley/Amine-Thermodynamics/issues/308#issuecomment-6808046541) replaces exact reproduction with a check against published pure-PZ property sources. Yaws 2014/HYSYS V9 remain unavailable; their exact coefficient/grid recovery is no longer the prerequisite. No fitting or Engine calculation was performed. The [design](../design-draft-pz.md#pure-pz-property-check-and-dielectric-inputs) owns the comparison procedure and continuation decisions.

### Verified Hartono 2021 correlation

Hartono, Rafiq, Gondal & Svendsen, *Fluid Phase Equilibria* 538 (2021) 112992, DOI [10.1016/j.fluid.2021.112992](https://doi.org/10.1016/j.fluid.2021.112992), Zotero `NVDXQ5NY` / `L5BIJ5I8`. Read §§2.2, 5.1–5.2, Tables 1, 8, 10–11, Fig.1 caption and relevant references from the current PDF. Table 8 row 3 p.7 and Table 11 method 3 p.7 verify

$$\log_{10}(P_{PZ}^{sat}/\mathrm{kPa})=5.9832-\frac{1215.77}{T/\mathrm{K}-113.56}.$$

The base-10 interpretation follows the printed log form and coefficient magnitude; unlike ln in adjacent rows. Table 8 explicitly specifies kPa although general Eq.1 p.2 labels saturation pressure Pa. Bind Table 8's units; do not multiply/divide the exponent by 1000. §5.1 p.6 says pure saturation and binary interaction parameters were fitted simultaneously; method 3 also uses calorimetric data. The reported 8.8% pure-pressure AARD is a fit deviation, not source uncertainty or an acceptance limit. No coefficient covariance or explicit valid temperature interval is provided. Table 1 p.2 lists pure sources across 288.5–655.0 K, but the low-temperature points require original phase verification. That compilation span is not an established liquid-validity interval. Restrict the supporting comparison here to the verified Steele liquid span below. Do not combine source-fit residuals and measurement residuals as independent evidence.

### Verified original liquid measurements

Steele et al. (1997), *J. Chem. Eng. Data* 42, 1037–1052, DOI [10.1021/je9700986](https://doi.org/10.1021/je9700986), acquired into Zotero collection `8RZP275E`: parent `G7NHDTGD`, PDF `JFSXIVZH`. Read experimental vapor-pressure/DSC/densitometry methods pp.1042–1043; PZ blocks and footnotes of Tables 7–11 pp.1044–1047; density discussion p.1047 and PZ discussion p.1050.

Table 7 p.1044 gives eight PZ liquid vapor pressures, 417.997–460.477 K, 90.976–269.97 kPa. Its sigma column is propagated pressure error, 0.004–0.01 kPa; the footnote p.1045 defines it using the two temperature derivatives for the ebulliometer. Delta p is observed minus the source fitted pressure, and Delta T is boiling minus condensation temperature. Neither is an additional uncertainty contribution. Retain the printed eight rows and sigma in any later authorized calculation, checked visually against this table. No measurement CSV is transcribed in this design revision.

Table 8 p.1045 gives melting at 384.6 K and fusion enthalpy 26.7±0.3 kJ/mol. This directly classifies the eight Table 7 PZ points as liquid; replace the approximate 379 K boundary inferred from Hilliard when classifying these pure measurements. Pure liquid extrapolation below 384.6 K must remain labeled subcooled. Sublimation pressures require a solid chemical potential and cannot test liquid saturation directly.

Table 10 p.1046 lists measured liquid saturation densities for other compounds, not PZ. Table 9 gives PZ cell densities and transition temperatures near the critical region; these are not saturated-liquid density observations. The p.1047 discussion explicitly notes absence of measured PZ densities and use of estimates. Thus pure-liquid density remains **unverified, a limitation rather than a stage prerequisite** under the latest owner decision: neither these cell densities, Hartono's infinite-dilution aqueous volume, nor an estimated density supplies the missing reference with source uncertainty. No physical failure of the Razavi set has been demonstrated.

### Unverified Nguyen dissertation

Live Zotero searches for Nguyen and volatility found the 2010 article `62762ZRK`, not the 2013 dissertation. The institutional [Nguyen dissertation PDF](https://sites.utexas.edu/rochelle/files/2015/02/Nguyen-2013-Amine-Volatility-in-CO2-Capture.pdf) was identified as an acquisition candidate. Companion acquisition returned `no Zotero translator for this page (login, check page or unsupported)`, no parent and no attachment, with that URL as its handoff. No repeat acquisition after this handoff was attempted. Tables 3.3.1 and 5.3.3 are pending additional aqueous comparisons, admitted after the owner adds the Zotero item/PDF and verification is complete: exact values, units, temperature ranges, loading and uncertainty remain unverified against a Zotero PDF. Their absence blocks no stage; do not use unverified values. An institutional source link does not replace the requested Zotero verification. Once acquired, classify unloaded versus loaded rows and check overlap with Hilliard/Nguyen 2010 before assigning comparison roles; neither aqueous block is a pure-liquid reference.

The earlier Razavi/Esmaeili source identities remain `FEVGI4LK`/`4L3HXHTI` and `DTTAZ8N3`/`WTWA3L4H`. PDF hashes, including the new readings, are in `pdf-identities.json`. Verification here concerns source transcription and phase interpretation, not EOS numerical verification or physical validation.

## Extended density search for #308 (11 November 2026)

**Outcome: no primary measured molten-PZ density has yet been verified with temperature, pressure basis and uncertainty. A specific original-report lead was found; “no density source exists” is no longer a justified statement.** The [SAFT/CPA survey](saft-pz-literature.md) records models, fitted data and comparison limits.

### Pure-liquid candidates and exclusions

| Source trail | What was actually read | Phase, pressure and uncertainty admission |
|---|---|---|
| Pereira, Llovell & Vega 2018, §§3.5/4.1.2 pp.694–696; ref.137 p.702 | Current Zotero PDF `AY49SC85/BZBCETDT`. Ref.137 is K. Moerke and T. Roscher, *Determination of the density of liquid diethylenediamine*, Leuna-Protokoll (1982), p./report 9102. Section 3.5 identifies it as the sparse pure-PZ density input. | **New original-report lead, not verified data.** Report not recovered by exact-title, author and report-number searches. Temperature range, composition/purity, saturation versus imposed pressure, measurement method and uncertainty remain unknown. Do not assume it lies above 384.6 K or transcribe modeled curves as its measurements. |
| Mota 2010, §2 pp.77–78, Tables 1–2, ref.32 | Current Zotero PDF `D63RCLN9/9BEG572M`. CPA coefficients fitted to DIPPR vapor-pressure and liquid-density data at reduced temperatures 0.45–0.85. | DIPPR compilation, not the primary measurement. No original PZ density reference or uncertainty recovered. The CPA fit's 1.6% density AAD is not an uncertainty. |
| Perdomo 2021, Table 5, §§4.2.1/4.4 | Indexed publisher HTML excerpts only, PDF acquisition handoff. Reports 24 PZ saturation-liquid density points at 384–620 K and 0.02% AAD. | Saturation basis claimed by the paper; provenance, experimental status and uncertainty not verified. Slightly sub-melting lower endpoint cannot be silently admitted. Source-reference numbering differs between indexed versions. |
| Razavi 2019 Table 1/ref.130 | Current PDF confirms Yaws 2014 Chapter 3, “Density of Liquid – Organic Compounds”, pp.133–256. | Yaws coefficient row and its original reference list still unavailable. Neither the 420–570 K fit range nor 1.65% fit AARD identifies measurement pressure or uncertainty. |
| Steele 1997 Tables 9–10 and density discussion p.1047 | Current PDF; no PZ saturation-density rows. | Near-critical cell densities and estimated density are excluded as saturated-liquid density measurements. Its historical absence statement is not a claim about literature published since 1997. |
| PubChem PZ §3.2.9, PAC database entry “1.45 @ 113°C” | Discovery entry only, [PubChem](https://pubchem.ncbi.nlm.nih.gov/compound/Piperazine). Other entries are room-temperature solid density. | The nominal 113°C is above melting, but no primary experiment, units/basis verification, pressure or uncertainty was recovered. Quarantined lead; not an admitted molten-density datum. |

This search traced a DIPPR-based CPA paper and a soft-SAFT primary-report citation. It did not access the licensed DIPPR source record or recover Yaws's coefficient/reference row. Consequently it cannot determine whether these compilations share Moerke–Roscher data, contain estimates, or use another measurement. No original-report acquisition URL was identified for Leuna-Protokoll 9102; no Zotero key or hash is invented for it.

### Indirect density checks

These are measured mixture densities, not pure-liquid PZ observations. Their use with frozen Razavi coefficients also tests PZ–water interactions and, for loaded solutions, speciation/ionic volume. They cannot identify the neutral set alone.

| Source | Conditions and locators | Evidence and limits |
|---|---|---|
| Concepción et al. 2020, [10.1016/j.jct.2019.105960](https://doi.org/10.1016/j.jct.2019.105960), §§2–3, Table 2 pp.2–3 | Unloaded PZ–water, PZ mass fraction 0.1, six temperatures 293.15–393.15 K; imposed pressure 0.1–140 MPa. Separate ternary blend has PZ 0.1 and DMAE 0.3. | **Verified PDF** `74AKMKUY/JTC62NGI`, acquired for this task. Vibrating-tube densimeter, expanded density uncertainty <0.7 kg/m³, coverage factor k=2 (§2 p.2). Table 2's 0.1 MPa rows provide a first aqueous comparison with a stated uncertainty. Admit only source-liquid rows inside the existing PZ domain; no table transcribed here. |
| Friis et al. 2025, [10.1016/j.jece.2025.115464](https://doi.org/10.1016/j.jece.2025.115464), §§2.2–2.4, 3.1, 4.1, Table 3 | Unloaded aqueous PZ up to 65 wt%, 293.15–343.15 K, atmospheric pressure. Table 3 explicitly marks precipitated states. At ≤30°C only ≤13.04 wt% considered; 20 wt% starts at 40°C; ≥30 wt% starts at 50°C (§2.2). | **Verified PDF** `TFW8Q7AC/MIDQZGU7`, acquired. DMA4500; three repeats, titrated concentration deviations ±1% (§§2.3–2.4). Table 3 prints per-point ± values; their statistical definition and a full propagated density uncertainty were not established by the methods read. Preserve those printed values without interpreting them as expanded uncertainty. Abstract's 0.03% model RAD is a fit deviation, not measurement uncertainty. Pure-PZ volume is expressly hypothetical (§3.1); does not fill the molten gap. |
| Stec et al. 2016, [10.1080/00319104.2015.1115328](https://doi.org/10.1080/00319104.2015.1115328), title/abstract only | Unloaded and CO2-loaded PZ, AMP and their mixtures, 293.15–333.15 K. | Zotero parent `JSR2A5AR`, **no PDF**; acquisition returned publisher access page. Composition, loading, pressure and uncertainty remain unverified; not admitted for scoring. This is the direct loaded-PZ candidate, distinct from an AMP/PZ blend. |
| Samanta & Bandyopadhyay 2006, [10.1021/je050378i](https://doi.org/10.1021/je050378i), Pereira ref.138; Friis Table 1 | Unloaded aqueous PZ density/viscosity, title gives 298–333 K. | **Verified PDF** `ZPBGA7G4/FYB2FPNI`, acquired and read: Experimental Section p.467 and Table 1 p.468. Unloaded PZ 1.74–6.88 wt%, eight temperatures 298–333 K; Gay-Lussac pycnometer, average of at least five measurements, reported probable density uncertainty ±4.5×10⁻⁵ g/cm³ and bath control ±0.1 K. Pressure is not quantified in the methods; ambient-pressure interpretation remains an assumption. Used in Pereira parameter estimation, so cannot independently validate that soft-SAFT set. |

For loaded solutions, no binary **anhydrous PZ + CO2** density experiment was verified. “Loaded PZ” in the aqueous candidates means **PZ + H2O + CO2**, not the water-free binary. Blend measurements also cannot be relabeled pure aqueous PZ.

### Nguyen 2013 access follow-up

The UT Austin [dissertation list](https://sites.utexas.edu/rochelle/dissertations-and-theses/), entry “Nguyen, Bich-Thu N.”, confirms the dissertation and links its institutional PDF. Searches of the UT repository by exact title and author did not recover an item landing page; opening the repository returned HTTP 403. The earlier `/files/2015/02/` acquisition had no translator. The newly requested follow-up tried the list's distinct `/wp-content/uploads/sites/3310/2015/02/` PDF location through Companion; it returned “no Zotero translator for this page (login, check page or unsupported)”, with no parent or attachment. The institutional PDF URL remains the acquisition handoff. No direct-library write bypass or manually invented thesis metadata was used. The owner will add the PDF manually; Tables 3.3.1 and 5.3.3 remain pending nonblocking additional comparisons until that Zotero item exists and is verified. Neither table would replace a pure-PZ density measurement.

### Adopted stage-1 scope

The [owner decision](https://github.com/tannerpolley/Amine-Thermodynamics/issues/308#issuecomment-6808482072) adopts the narrower stage 1: frozen Razavi pressure check against Steele, with Hartono as a separate supporting correlation. Pure-liquid density is a stated limitation; the prerequisite is removed. Moerke & Roscher 1982 remains an unrecovered lead, not an input required for continuation. After binary calibration, compare Concepción Table 2's 0.1 MPa rows and Friis Table 3's source-liquid states separately, without fitting density. Preserve the source uncertainty limits and report near-misses without a new percentage threshold. The [design](../design-draft-pz.md) owns the comparison procedure and stage sequence.

A real misfit, after numerical and convention diagnosis, returns to the owner for refitting pure PZ versus continuation with a stated limit. No pure-liquid physical validation is claimed. Replacing Razavi with another EOS's parameters requires a separate model decision; this amendment authorizes no fitting in the present task.
