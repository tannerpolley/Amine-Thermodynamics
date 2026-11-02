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
| Data references | refs.100, 136 | — |

Esmaeili et al. (2020), *Process Saf. Environ. Prot.* 141, 95–109, DOI 10.1016/j.psep.2020.05.010, Table 1, p.97, prints m = 2.652, σ = 3.713 Å, ε/kB = 274.1 K, εAB/kB = 1923 K and κAB = 0.07275. Those are the Razavi values rounded, and its caption cites Razavi et al. 2019. Esmaeili uses PC-SAFT for **vapor-phase fugacities only**; the liquid is eNRTL (§2.1, p.97). It is therefore not evidence that this set works in an aqueous liquid. It is the same set, not a second one.

## Association scheme and convention

Razavi p.11046 (§ on heterocycles with –NH groups): "two association sites are considered per each molecule as type 2B in the terminology of Huang and Radosz". PZ has two N–H groups, yet the model uses one effective donor–acceptor pair, as for AMP. Razavi Eq.7, p.11045, prints the association strength as

Δ^{AiBj} = g_ij^hs(d_ij) [exp(ε^{AiBj}/kBT) − 1] σ_ij³ κ^{AiBj}.

So the volume prefactor uses **σ³**, not d(T)³. That settles for PZ the convention question #229 left open for AMP. It still has to match the Engine's association expression before the values are bound.

## Limits found by reading the source

- **The fitting data are compiled correlations, not primary measurements.** Ref.100 is Yaws & Satyro, *The Yaws Handbook of Vapor Pressure* (2015). Ref.136 is the Aspen HYSYS V9 databank (2017). Razavi's abstract calls them "experimental data". Neither the handbook values nor their primary origin were inspected here.
- **Phase of the fitted states.** Anhydrous PZ is solid at absorber temperatures. Hilliard 2008, Table 7.3-3 (PDF p.208), uses DIPPR solid Cp for PZ up to 106.0 °C. Freeman et al. 2010, p.119, gives the normal boiling point as 146.5 °C. Razavi's P_sat range starts at 323 K, below that solid range. The 323–379 K "vapor pressures" are then either sublimation pressures or extrapolated subcooled-liquid values; the paper does not say which. Liquid density starts at 420 K. Aqueous use at 313–393 K therefore depends on subcooled-liquid extrapolation of both properties.
- No binary PZ–water, CO2 or ion parameters are given. Razavi's binary systems are heterocycle–organic mixtures.

## Reproduction check (defined, not executed)

1. Bind the five values, two 2B sites, the σ³ prefactor (Eq.7), and the temperature-dependent segment diameter of Gross & Sadowski 2001.
2. Regenerate the Yaws P_sat and HYSYS ρL values at Razavi's stated temperatures from the cited references. Compare per-point residuals with the reported AARD (0.33 %, 1.65 %). This verifies the numerical convention; it is not physical validation.
3. Separately compare P_sat against an independent primary measurement in the liquid range (379–419 K) if one is found. The 323–379 K values must be classified as sublimation or subcooled-liquid before use.

The owner must choose: adopt this set after step 2; or authorize a neutral PZ refit to primary pure data plus Hilliard App. D.2 binary volatility. No parameter is adopted here.

Zotero: Razavi parent `FEVGI4LK`, PDF `4L3HXHTI` (22 pages); Esmaeili parent `DTTAZ8N3`, PDF `WTWA3L4H` (15 pages). Both were added under #237.
