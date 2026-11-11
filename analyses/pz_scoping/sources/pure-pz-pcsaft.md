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
- **Phase of the fitted states.** Anhydrous PZ is solid at absorber temperatures. Hilliard 2008, Table 7.3-3 (PDF p.208), uses DIPPR solid Cp for PZ up to 106.0 °C. Freeman et al. 2010, p.119, gives the normal boiling point as 146.5 °C. Razavi's P_sat range starts at 323 K, below that solid range. The 323–379 K "vapor pressures" are then either sublimation pressures or extrapolated subcooled-liquid values; the paper does not say which. Liquid density starts at 420 K. Owner-authorized aqueous use at 283–393 K therefore depends on subcooled-liquid extrapolation of both properties.
- No binary PZ–water, CO2 or ion parameters are given. Razavi's binary systems are heterocycle–organic mixtures.

## Reproduction check (defined, not executed)

1. Bind the five values, two 2B sites, the σ³ prefactor (Eq.7), and the temperature-dependent segment diameter of Gross & Sadowski 2001.
2. Regenerate pressure from refs.100/136 and density from ref.130, retaining their separate source identities. Obtain the actual coefficients, equation form, units, phase, valid range and exact fitting temperature grid before execution. Compare aggregate AARD with the reported 0.33 % and 1.65 %, retaining per-point errors separately; those aggregate fit errors are not pointwise uncertainty limits. This verifies the numerical convention; it is not physical validation.
3. Separately compare P_sat against an independent primary measurement in the liquid range (379–419 K) if one is found. The 323–379 K values must be classified as sublimation or subcooled-liquid before use.

The owner accepted reproduction first and subcooled extrapolation down to 283 K (#308, amended 11 November). This does not supply the missing reference inputs or authorize an unexamined substitute/refit.

## Revision for #308: reference binding and remaining stop

Razavi Table 1 p.11040 and reference list pp.11056–11057 were re-read in the current Zotero PDF `4L3HXHTI`; SHA-256 matches `pdf-identities.json`. The source assignment above replaces the earlier density attribution error. Ref.100 is Yaws & Satyro 2015 Chapter 1 pp.1–314; ref.136 is Aspen HYSYS V9 (2017). Ref.130 is the Yaws 2014 density chapter. The paper prints neither the PZ correlation coefficients nor the sampled fitting temperatures/weights. Naming a book does not bind a usable correlation.

Live Zotero search for Yaws returned no item; the existing PZ corpus and local shelf contain no coefficient row or HYSYS export. Publisher book identities were checked at [Yaws 2014](https://www.sciencedirect.com/science/book/9780323286596) and [Yaws 2015](https://www.sciencedirect.com/book/9780128029992/the-yaws-handbook-of-vapor-pressure). Approved `cse-zotero acquire` attempts for each book returned `Remote HTTP 400: INVALID_INPUT - No resource identifier provided; no retry`, no item and no PDF. These are acquisition gaps, not negative scientific findings. No unauthorized mirror was used. **Actual coefficient binding is unresolved and blocks stage 1.**

Required retained reference packet before reproduction: edition/chapter/PZ CAS 110-85-0 row locator, coefficients with units and logarithm basis, phase classification (especially below melting), source range, pressure reference, original grids and weights if available, file hashes and transcribed values checked visually. Use the quoted parameter precision and sigma-cubed 2B convention. Compute AARD=100 mean(abs(calc/ref−1)) separately for pressure 323–630 K and density 420–570 K. If the exact grid/weights are recovered, judge reproduction by rounding to 0.33 and 1.65 at the printed precision and retain solver numerical error separately. If they cannot be recovered, the new grid is only a diagnostic comparison and cannot establish exact reproduction. Report discrepancy and near-miss size; the owner decides continuation. No AARD is treated as measurement uncertainty, and no new percentage tolerance is invented.

Zotero: Razavi parent `FEVGI4LK`, PDF `4L3HXHTI`; Esmaeili parent `DTTAZ8N3`, PDF `WTWA3L4H`. Exact pure-reference acquisition and classification remain open; no Engine reproduction was run.
