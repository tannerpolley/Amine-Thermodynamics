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

Table 10 p.1046 lists measured liquid saturation densities for other compounds, not PZ. Table 9 gives PZ cell densities and transition temperatures near the critical region; these are not saturated-liquid density observations. The p.1047 discussion explicitly notes absence of measured PZ densities and use of estimates. Thus the **pure-liquid density check remains blocked**: neither these cell densities, Hartono's infinite-dilution aqueous volume, nor an estimated density supplies the missing reference with source uncertainty. No physical failure of the Razavi set has been demonstrated.

### Unverified Nguyen dissertation

Live Zotero searches for Nguyen and volatility found the 2010 article `62762ZRK`, not the 2013 dissertation. The institutional [Nguyen dissertation PDF](https://sites.utexas.edu/rochelle/files/2015/02/Nguyen-2013-Amine-Volatility-in-CO2-Capture.pdf) was identified as an acquisition candidate. Companion acquisition returned `no Zotero translator for this page (login, check page or unsupported)`, no parent and no attachment, with that URL as its handoff. No repeat acquisition after this handoff was attempted. Tables 3.3.1 and 5.3.3 are not admitted: exact values, units, temperature ranges, loading and uncertainty remain unverified against a Zotero PDF. Keep this aqueous comparison blocked. An institutional source link does not replace the requested Zotero verification. Once acquired, classify unloaded versus loaded rows and check overlap with Hilliard/Nguyen 2010 before assigning comparison roles; neither aqueous block is a pure-liquid reference.

The earlier Razavi/Esmaeili source identities remain `FEVGI4LK`/`4L3HXHTI` and `DTTAZ8N3`/`WTWA3L4H`. PDF hashes, including the new readings, are in `pdf-identities.json`. Verification here concerns source transcription and phase interpretation, not EOS numerical verification or physical validation.
