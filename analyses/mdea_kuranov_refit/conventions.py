"""Issue #126 convention diagnosis: which declaration or evaluation convention makes Uyan 2015 reproduce its Kuranov
ARD on this Engine, and does it carry to Wangler 2018?  Each variant names its declared changes from a base model.

Usage: python conventions.py [variant name or index ...]   (default: every variant, one process each, at most 16)
Writes results/runs/conventions/<variant>.json (ignored scratch) and, when every variant ran, results/conventions.json.
Variants marked "local diagnostic" emulate a convention the Engine cannot declare (a ln K shift per reaction, or Uyan
Eq. 5 recomputed per state); they must not feed adopted results.
"""
from __future__ import annotations

import hashlib
import json
import math
import sys
from concurrent.futures import ProcessPoolExecutor
from math import comb

import epcsaft
from epcsaft import equilibrium

import diagnose
import model
import score

W, MDEA, CO2, MDEAH, HCO3, CO3, H, OH = model.SPECIES
CL = "chloride-anion"
RUNS = score.RESULTS / "runs" / "conventions"
UYAN, WANGLER = model.UYAN, model.WANGLER


def about_298_15(coefficients, t0):
    """Re-express sum a_k (T - t0)^k exactly as a polynomial in T - 298.15 K (the document's reference)."""
    d = model.T_REF - t0
    return tuple(sum(a * comb(k, j) * d ** (k - j) for k, a in enumerate(coefficients) if k >= j)
                 for j in range(len(coefficients)))


UYAN_EQ26 = about_298_15((-2.2e-2, 4.2e-4, -1.7e-6), 298.0)  # Uyan Eq. 26 (p. 96), k(CO2-water), T+ = 298 K
UYAN_EQ27 = about_298_15((-1.5275e-2, -5.24e-5, 7.9e-6), 298.0)  # Uyan Eq. 27 (p. 96), k(MDEA-water), T+ = 298 K
UYAN_KIJ = {
    (W, MDEA): (UYAN_EQ27, f"{UYAN} Eq. 27, Table 5"),
    (W, CO2): (UYAN_EQ26, f"{UYAN} Eq. 26, Table 5"),
    (W, H): ((0.25,), f"{UYAN} Table 5"), (W, OH): ((-0.25,), f"{UYAN} Table 5"),
    (W, CO3): ((-0.25,), f"{UYAN} Table 5"),  # HCO3-/water is '-' in Table 5: zero
    (W, MDEAH): (UYAN_EQ27, f"{UYAN} Table 5 'Eq. (27)'; section 4.3.2 'inherited from MDEA/water'"),
}


def uyan(mdeah_kij=True):
    """Uyan 2015 as printed: Tables 1, 3-5, Eqs. 26-27, k_hb(water-MDEA) = 0.015 (Table 5 footnote a), no correction on
    the water-MDEAH+ and MDEA-MDEAH+ edges.  mdeah_kij=False takes section 4.2.1 ('set to zero') instead of Table 5."""
    kij = dict(UYAN_KIJ)
    if not mdeah_kij:
        kij.pop((W, MDEAH))
    doc = model.document(kij)
    for edge in doc["topology"]["edges"]:
        identity = edge.get("volume_correction", {}).get("identity", "")
        if identity == f"association/{W}/{MDEA}/volume_correction":
            edge["volume_correction"] = model._law(identity, (0.015,))
        elif identity:
            del edge["volume_correction"]
    doc["document_id"], doc["purpose"] = "mdea-uyan-2015-reproduction", "Fixed published Uyan 2015 model (issue #126)"
    return doc


BASES = {"uyan": uyan, "uyan-k0": lambda: uyan(False), "wangler": model.document}


# --- single changes to a parameter document: f(doc, T, m_mdea) -> doc ------------------------------------------------
def charges(doc):
    return {c["component_id"]: c["fixed"]["charge_number"]["value"]["magnitude"] for c in doc["components"]}


def coefficient(doc, cid, family):
    comp = next(c for c in doc["components"] if c["component_id"] == cid)
    return next(c for c in comp["coefficients"] if c["family"] == family)["value"]


SUPPRESS = 1e-8  # u_i -> u_i * SUPPRESS removes ion i's self-dispersion; every k_ij of i is rescaled to keep u_ij exact


def self_dispersion(*keep):
    """Dispersion between two ions of the same species kept for `keep` (all ions if empty); every unlike same-sign pair
    stays excluded.  Declared exactly: Engine all-ion-pairs, k_ij = 1 on unlike same-sign pairs, and for every other ion
    u_i scaled by 1e-8 with each of its k_ij rescaled so sqrt(u_i u_j)(1 - k_ij) is unchanged."""
    def apply(doc, T, m_mdea):
        next(f for f in doc["model_families"] if f["kind"] == "electrolyte")["ionic_dispersion"] = "all-ion-pairs"
        z = charges(doc)
        ions = [c for c in z if z[c]]
        doc["pairs"] += [{"component_id_a": a, "component_id_b": b, "provenance": "diagnostic: no unlike same-sign dispersion",
                          "coefficients": [{"family": "k_ij", "identity": f"pair/{a}/{b}/k_ij",
                                            "value": {"magnitude": 1.0, "unit": "dimensionless"}}]}
                         for k, a in enumerate(ions) for b in ions[k + 1:] if z[a] * z[b] > 0]
        scale = 1 / math.sqrt(SUPPRESS)
        for ion in ions:
            if keep and ion not in keep:
                coefficient(doc, ion, "dispersion_energy_over_k")["magnitude"] *= SUPPRESS
                for pair in doc["pairs"]:
                    if ion in (pair["component_id_a"], pair["component_id_b"]):
                        k = pair["coefficients"][0]
                        terms = (((t["power"], t["coefficient"]["value"]) for t in k["temperature_law"]["terms"])
                                 if "temperature_law" in k else [(0, k["value"])])
                        for power, v in terms:
                            v["magnitude"] = 1 - scale * (1 - v["magnitude"]) if power == 0 else scale * v["magnitude"]
        return doc
    return apply


def check_self_dispersion(T=313.15):
    """Self-check: suppressing every ion's self-dispersion through all-ion-pairs reproduces exclude-same-sign-ion-pairs,
    so the rescaled k_ij keep every cross term (temperature laws included)."""
    x = [0.86, 0.06, 0.01, 0.03, 0.028, 0.001, 1e-9, 1e-9]
    x = [v / sum(x) for v in x]
    for base in (uyan, model.document):
        a, b = (epcsaft.Mixture(epcsaft.Parameters.from_mapping(d)).state(T, P=2e5, x=x, phase="liquid").log_fugacity_coefficient
                for d in (base(), self_dispersion("no-such-ion")(base(), T, 0.0)))
        assert max(abs(u - v) for u, v in zip(a, b)) < 1e-6, (a, b)


def eq11_diameter(*ions):
    """Packing diameter of the named ions from Uyan Eq. 11 / Wangler Eq. 6, sigma (1 - 0.12 exp(-3u/kT)), instead of
    Eq. 10 / Eq. 7 (0.88 sigma)."""
    def apply(doc, T, m_mdea):
        for ion in ions:
            sigma, u = model.COMPONENTS[ion][3], model.COMPONENTS[ion][4]
            coefficient(doc, ion, "packing_diameter")["magnitude"] = sigma * (1 - 0.12 * math.exp(-3 * u / T))
        return doc
    return apply


charged_mdea_diameter = eq11_diameter(MDEAH)


def mdeah_volume_correction(value):
    """k_hb on the water-MDEAH+ association edges (Uyan Table 5 footnote a applies 0.015 to MDEA/water only)."""
    def apply(doc, T, m_mdea):
        for edge in doc["topology"]["edges"]:
            if {edge["endpoint_a"]["component_id"], edge["endpoint_b"]["component_id"]} == {W, MDEAH}:
                edge["volume_correction"] = model._law(f"association/{W}/{MDEAH}/volume_correction", (value,))
        return doc
    return apply


def non_associating_mdeah(doc, T, m_mdea):
    """Bulow 2021a (text after Eq. 18): charged species non-associating."""
    topo = doc["topology"]
    topo["sites"] = [s for s in topo["sites"] if s["component_id"] != MDEAH]
    topo["edges"] = [e for e in topo["edges"] if MDEAH not in (e["endpoint_a"]["component_id"], e["endpoint_b"]["component_id"])]
    return doc


def spherical(doc, T, m_mdea):
    return model.spherical_mdeah(doc)


def initial_permittivity(doc, T, m_mdea):
    """Local diagnostic: Uyan Eq. 5 on the initial CO2-free solvent (model.initial_solvent_permittivity)."""
    return model.initial_solvent_permittivity(doc, T, m_mdea)


def water_permittivity(doc, T, m_mdea):
    """Pure-water permittivity at T (the convention of Uyan's ion-parameter source, section 2), not Eq. 5."""
    return model.initial_solvent_permittivity(doc, T, 0.0)


# --- reaction-reference conventions: options(row) -> extra model.bubble_problem keywords -------------------------------
def pure_reference(*species):
    """gamma0 (pure component at T, p; Uyan Eq. 22) instead of gamma* for the named species, declared in the Engine."""
    reference = equilibrium.NeutralReference(
        solvent=W, standard_molality_mol_per_kg=model.NEUTRAL_REFERENCE.standard_molality_mol_per_kg,
        solute_molality_ratios=model.NEUTRAL_REFERENCE.solute_molality_ratios,
        species_reference={s: equilibrium.SpeciesReference.PureLiquid for s in species})
    return lambda doc_of_row: (lambda r: {"neutral_reference": reference})


def molality_constants(doc_of_row):
    """Uyan Table 1 constants read as molality-based: ln K_x = ln K_m + (sum of solute nu) ln M_w."""
    lnmw = math.log(model.COMPONENTS[W][0])
    shift = {r: lnmw * sum(v for i, v in nu.items() if i != W) for r, (nu, _) in model.REACTIONS.items()}
    return lambda r: {"shift": shift}


def initial_solvent_reference(doc_of_row):
    """Local diagnostic: CO2 and ions referenced to infinite dilution in the initial CO2-free water/MDEA solvent instead
    of pure water (MDEA keeps infinite dilution in water), as a ln K shift evaluated at the measured pressure."""
    def options(r):
        mix = epcsaft.Mixture(epcsaft.Parameters.from_mapping(doc_of_row(r)))
        n_w = 1 / model.COMPONENTS[W][0]
        solvent = {W: n_w / (n_w + r["m_mdea"]), MDEA: r["m_mdea"] / (n_w + r["m_mdea"])}
        ref, water = (dict(zip(model.SPECIES, mix.state(r["T"], P=r["p_exp"], x=dilute(s), phase="liquid").log_fugacity_coefficient))
                      for s in (solvent, {W: 1.0}))
        return {"shift": {name: sum(v * (ref[i] - water[i]) for i, v in nu.items() if i not in (W, MDEA))
                          for name, (nu, _) in model.REACTIONS.items()}}
    return options


def dilute(solvent, e=1e-12):
    x = {s: e for s in model.SPECIES} | {CO3: e / 2, OH: e / 2} | solvent
    return [x[s] / sum(x.values()) for s in model.SPECIES]


NONE = lambda doc_of_row: (lambda r: {})  # noqa: E731
U, WG = f"{UYAN}", f"{WANGLER}"
CHARGED_MDEA = (self_dispersion(MDEAH), charged_mdea_diameter)
CHARGED = f"MDEAH+ = charged MDEA: MDEA's self-dispersion and Eq. 11 diameter ({U} section 4.1)"
VARIANTS = {  # name: (base, document changes, reaction-reference convention, change and locator)
    "uyan": ("uyan", (), NONE, f"base: {U} as printed; MDEAH+ = MDEA segment number 3.675 (section 4.1, Table 4 note a)"),
    "uyan, k(water-MDEAH+) = 0": ("uyan-k0", (), NONE, f"{U} section 4.2.1 instead of Table 5 / section 4.3.2"),
    "uyan, gamma0 CO2": ("uyan", (), pure_reference(CO2), f"{U} Eq. 18 as printed (p. 94): pure-CO2 reference"),
    "uyan, gamma0 MDEA": ("uyan", (), pure_reference(MDEA), "pure-MDEA reference (the misuse Bulow 2021a names before Eq. 12)"),
    "uyan, molality-basis K": ("uyan", (), molality_constants, f"{U} Table 1 constants read as molality-based"),
    "uyan, mixed-solvent solute reference": ("uyan", (), initial_solvent_reference, "local diagnostic: Eq. 23 limit in the water/MDEA solvent"),
    "uyan, initial-solvent permittivity": ("uyan", (initial_permittivity,), NONE, f"local diagnostic: {U} Eq. 5 on the initial solvent"),
    "uyan, MDEAH+ non-associating": ("uyan", (non_associating_mdeah,), NONE, "Bulow 2021a text after Eq. 18"),
    "uyan, spherical MDEAH+": ("uyan", (spherical,), NONE, "Bulow 2021a Table 2 (segment number 1)"),
    "uyan, MDEAH+ self-dispersion": ("uyan", (self_dispersion(MDEAH),), NONE,
                                     f"{U} section 4.1 'inherited from MDEA'; {WG} section 3 excludes only 'cross dispersion'"),
    "uyan, all-ion self-dispersion": ("uyan", (self_dispersion(),), NONE, "side-effect bound: every ion keeps its self-dispersion"),
    "uyan, MDEAH+ Eq. 11 diameter": ("uyan", (charged_mdea_diameter,), NONE, f"{U} Eq. 11 instead of Eq. 10 for MDEAH+"),
    "uyan, MDEAH+ as charged MDEA": ("uyan", CHARGED_MDEA, NONE, CHARGED),
    "uyan, MDEAH+ as charged MDEA, k(water-MDEAH+) = 0": ("uyan-k0", CHARGED_MDEA, NONE, f"{CHARGED}; section 4.2.1"),
    "uyan, MDEAH+ as charged MDEA, initial-solvent permittivity": ("uyan", CHARGED_MDEA + (initial_permittivity,), NONE,
                                                                  f"{CHARGED}; Eq. 5 on the initial solvent"),
    "uyan, MDEAH+ self-dispersion, initial-solvent permittivity": ("uyan", (self_dispersion(MDEAH), initial_permittivity), NONE,
                                                                   "self-dispersion and Eq. 5 on the initial solvent"),
    "uyan, MDEAH+ as charged MDEA, k_hb(water-MDEAH+) = 0.015": ("uyan", CHARGED_MDEA + (mdeah_volume_correction(0.015),), NONE,
                                                                  f"{CHARGED}; MDEA's k_hb also inherited"),
    "uyan, every ion as a charged molecule": ("uyan", (self_dispersion(), eq11_diameter(MDEAH, HCO3, CO3, H, OH)), NONE,
                                              "no ion-specific rule: self-dispersion and Eq. 11 diameter for every ion"),
    "uyan, MDEAH+ as charged MDEA, water permittivity": ("uyan", CHARGED_MDEA + (water_permittivity,), NONE,
                                                         f"{CHARGED}; pure-water permittivity instead of Eq. 5"),
    "wangler": ("wangler", (), NONE, f"base: {WG} as printed (score.py 'as-printed')"),
    "wangler, MDEAH+ as charged MDEA, water permittivity": ("wangler", CHARGED_MDEA + (water_permittivity,), NONE,
                                                            f"{CHARGED}; pure-water permittivity instead of Eq. 5"),
    "wangler, every ion as a charged molecule": ("wangler", (self_dispersion(), eq11_diameter(MDEAH, HCO3, CO3, H, OH)), NONE,
                                                 "no ion-specific rule: self-dispersion and Eq. 11 diameter for every ion"),
    "wangler, gamma0 CO2": ("wangler", (), pure_reference(CO2), "pure-CO2 reference (not Wangler Eq. 15)"),
    "wangler, MDEAH+ self-dispersion": ("wangler", (self_dispersion(MDEAH),), NONE, "self-dispersion only"),
    "wangler, MDEAH+ Eq. 11 diameter": ("wangler", (charged_mdea_diameter,), NONE, "Eq. 6 instead of Eq. 7 for MDEAH+"),
    "wangler, MDEAH+ as charged MDEA": ("wangler", CHARGED_MDEA, NONE, CHARGED),
    "wangler, MDEAH+ as charged MDEA, initial-solvent permittivity": ("wangler", CHARGED_MDEA + (initial_permittivity,), NONE,
                                                                     f"{CHARGED}; Eq. 5 on the initial solvent"),
}
PUBLISHED = {"uyan": {"published (Uyan Table 6)": 22.9, "re-determined (Wangler Table 11 note b)": 34.4,
                      "19 mass %": "19.82 (abstract) or 19.22 (section 4.3.2, 0.01 < alpha)", "32 mass %": 25.91},
             "wangler": {"published (Wangler Table 11)": 19.7, "32 mass % (Fig. 11)": 19.44}}


def doc_function(name):
    base, changes, _, _ = VARIANTS[name]

    def doc_of_row(r):
        doc = BASES[base]()
        for change in changes:
            doc = change(doc, r["T"], r["m_mdea"])
        return doc
    return doc_of_row


def osmotic_check(name):
    """MDEAH+Cl- osmotic coefficients (Wangler Tables 8-9; Wangler's fit reached 5.05 %, Fig. 10) under the variant's
    document changes.  Reference-state free, so it isolates the EOS treatment of MDEAH+."""
    base, changes, _, _ = VARIANTS[name]
    rows = []
    for T, m, phi in diagnose.MDEAHCL:
        doc = diagnose.add_ion(BASES[base](), CL, 0.035453, -1, 2.7560, 170.0, {W: -0.25})  # Held 2014 Cl-; k(MDEAH+-Cl-) = 0
        for change in changes:
            doc = change(doc, T, 0.0)
        rows.append({"T": T, "m": m, "phi_exp": phi, "phi_calc": diagnose.osmotic(doc, MDEAH, CL, T, m)})
    return {"rows": rows, "ARD_percent": 100 * sum(abs(1 - r["phi_calc"] / r["phi_exp"]) for r in rows) / len(rows)}


T_SPEC, M_SPEC = 313.15, 0.23 / (0.77 * model.COMPONENTS[MDEA][0])  # Uyan Fig. 4 and Wangler section 6.2: 313 K, w_MDEA 0.23
# Uyan Fig. 4 (p. 97) model lines for x_CO2, read from the 600 dpi page with axis ticks as calibration (+-5 %):
# full line = ePC-SAFT with activity coefficients, dashed = ideal (all gamma = 1).
UYAN_FIG4_X_CO2 = {0.2: (6.6e-6, 2.50e-5), 0.4: (3.58e-5, 1.32e-4), 0.6: (1.59e-4, 4.34e-4), 0.75: (4.50e-4, 9.96e-4)}
WANGLER_6_2 = {0.02: {H: 3.80e-11, MDEAH: 9.80e-4}, 1.4: {H: 3.32e-9, MDEAH: 3.37e-2}}  # Wangler section 6.2 text


# Uyan Fig. 5 (p. 97) model lines, w_MDEA 0.19: total pressure (bar) at (T, alpha), read from the 600 dpi page with the axis
# ticks as calibration (+-0.3 bar), at loadings away from the plotted markers.
UYAN_FIG5_BAR = {413.15: {0.4: 16.29}, 393.15: {0.4: 6.80, 0.6: 15.25, 0.8: 30.68}, 373.15: {0.6: 7.46, 0.9: 26.35},
                 333.15: {1.0: 14.05, 1.2: 33.63}, 313.15: {1.1: 14.13, 1.2: 22.20, 1.3: 31.42}}


def fig5_check(name):
    """Engine bubble pressures at the Uyan Fig. 5 points (w_MDEA 0.19): our evaluation against Uyan's own model lines."""
    m, out = 0.19 / (0.81 * model.COMPONENTS[MDEA][0]), []
    doc_of_row = doc_function(name)
    for T, points in UYAN_FIG5_BAR.items():
        r = {"T": T, "m_mdea": m, "p_exp": 1e5}
        mix = epcsaft.Mixture(epcsaft.Parameters.from_mapping(doc_of_row(r)))
        options, guess = VARIANTS[name][2](doc_of_row)(r), (None, None)
        for alpha in sorted({round(0.1 * k, 1) for k in range(1, 14)} | set(points)):  # warm-started loading sweep
            if alpha > max(points):
                break
            for start in (guess, (None, None)):
                result = equilibrium.solve_equilibrium(mix, model.bubble_problem(T, m, alpha * m, 1e6, *start, **options))
                if result.success:
                    guess = (dict(zip(model.SPECIES, result.phase_mole_fractions(0))),
                             dict(zip(model.NEUTRAL, result.phase_mole_fractions(1)[:3])))
                    break
            if alpha in points:
                out.append({"T": T, "alpha": alpha, "p_Uyan_line_bar": points[alpha],
                            "p_calc_bar": result.pressure[0] / 1e5 if result.success else None})
    ratios = [math.log(o["p_calc_bar"] / o["p_Uyan_line_bar"]) for o in out if o["p_calc_bar"]]
    return {"points": out, "mean_ln_ratio_to_Uyan_line": sum(ratios) / len(ratios)}


def speciation(name):
    """Liquid speciation at 313.15 K, w_MDEA 0.23 along a warm-started loading sweep (Engine bubble points)."""
    base, changes, convention, _ = VARIANTS[name]
    targets = UYAN_FIG4_X_CO2 if base.startswith("uyan") else WANGLER_6_2
    alphas = sorted(set(targets) | {0.02, 0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.75, 0.8, 0.9, 1.0, 1.1, 1.2, 1.3, 1.4})
    alphas = [a for a in alphas if a <= max(targets)]
    r = {"T": T_SPEC, "m_mdea": M_SPEC, "p_exp": 1e5}
    doc_of_row = doc_function(name)
    mix = epcsaft.Mixture(epcsaft.Parameters.from_mapping(doc_of_row(r)))
    options, guess, out = convention(doc_of_row)(r), (None, None), {}
    for alpha in alphas:
        for p0 in (1e4, 1e5, 1e6, 1e7):
            result = equilibrium.solve_equilibrium(mix, model.bubble_problem(T_SPEC, M_SPEC, alpha * M_SPEC, p0, *guess, **options))
            if result.success:
                break
        if not result.success:
            out[alpha] = {"success": False, "message": result.message}
            continue
        x = dict(zip(model.SPECIES, result.phase_mole_fractions(0)))
        guess = (x, dict(zip(model.NEUTRAL, result.phase_mole_fractions(1)[:3])))
        if alpha in targets:
            out[alpha] = {"P_Pa": result.pressure[0], **x}
    return out


def mass_action(T, m, alpha, ln_gamma):
    """Uyan Eqs. 16-24 at fixed activity coefficients (mole-fraction basis, Table 1): one stoichiometric liquid with
    m mol MDEA and alpha*m mol CO2 per kg water.  Returns mole fractions (local diagnostic, no EOS)."""
    from scipy.optimize import brentq
    n_w0, c = 1 / model.COMPONENTS[W][0], alpha * m
    lnk = {name: c1 + c2 / T + c3 * math.log(T) + c4 * T - sum(v * ln_gamma[i] for i, v in nu.items())
           for name, (nu, (c1, c2, c3, c4)) in model.REACTIONS.items()}  # mole-fraction products after the gammas

    def species(h):  # every amount from n_H+ through the four laws; water and total amount by fixed point
        n, water = n_w0 + m + c, n_w0
        for _ in range(100):
            xh, xw = h / n, water / n
            r2, r3, r4 = math.exp(lnk["R2"]) * xw / xh, math.exp(lnk["R3"]) / xh, math.exp(lnk["R4"]) / xh
            co2 = c / (1 + r2 + r2 * r3)
            mdeah = m / (1 + r4)
            amounts = {W: water, MDEA: m - mdeah, CO2: co2, MDEAH: mdeah, HCO3: co2 * r2, CO3: co2 * r2 * r3, H: h,
                       OH: math.exp(lnk["R1"]) * xw / xh * n}
            water = n_w0 - amounts[OH] - amounts[HCO3] - amounts[CO3]  # water consumed by R1 and R2
            n = sum(amounts.values())
        return amounts, n

    def charge(lnh):
        a, _ = species(math.exp(lnh))
        return a[H] + a[MDEAH] - a[HCO3] - 2 * a[CO3] - a[OH]
    a, n = species(math.exp(brentq(charge, math.log(1e-14), math.log(1e-2), xtol=1e-14)))
    return [a[s] / n for s in model.SPECIES]


def kvalue_speciation(doc, alpha, T=T_SPEC, m=M_SPEC, P=1e5):
    """Uyan's K-value method (section 3, steps 1-4): ideal speciation, then activity coefficients at that composition,
    repeated to a fixed point.  doc None: no activity coefficients (the Fig. 4 dashed line).  Otherwise the Engine's
    ln phi with water pure liquid and every other species at infinite dilution in pure water.  Local diagnostic.
    (Eq. 23 read as x_i -> 0 in the current mixture cannot be evaluated for an ion: the Engine refuses the resulting
    non-electroneutral state.)"""
    mix = epcsaft.Mixture(epcsaft.Parameters.from_mapping(doc)) if doc else None
    ln_gamma = dict.fromkeys(model.SPECIES, 0.0)
    for _ in range(300):
        x = mass_action(T, m, alpha, ln_gamma)
        if mix is None:
            return dict(zip(model.SPECIES, x))
        lnphi = mix.state(T, P=P, x=x, phase="liquid").log_fugacity_coefficient
        ref = mix.state(T, P=P, x=dilute({W: 1.0}), phase="liquid").log_fugacity_coefficient
        new = {s: lnphi[k] - ref[k] for k, s in enumerate(model.SPECIES)}
        change = max(abs(new[s] - ln_gamma[s]) for s in model.SPECIES)
        ln_gamma = {s: 0.5 * (ln_gamma[s] + new[s]) for s in model.SPECIES}  # damped fixed point
        if change < 1e-9:
            return dict(zip(model.SPECIES, x)) | {"ln_gamma_star": new}
    raise RuntimeError(f"K-value iteration did not converge (last change {change:.2e})")


def kvalue_checks():
    """(1) Ideal speciation against the Fig. 4 dashed line checks Table 1, its basis and the loading definition.
    (2) The K-value method with the Engine's activity coefficients against the Engine's own bubble-point speciation
    checks that the Engine solves Uyan Eqs. 17-23.  (3) ln gamma* at Uyan's state for the two leading readings."""
    out = {"ideal_vs_Fig4_dashed": {a: {"x_CO2": kvalue_speciation(None, a)[CO2], "Fig4_dashed": dashed}
                                    for a, (_, dashed) in UYAN_FIG4_X_CO2.items()}}
    for name in ("uyan", "uyan, MDEAH+ as charged MDEA"):
        doc = doc_function(name)({"T": T_SPEC, "m_mdea": M_SPEC})
        out[name] = {a: (lambda kv: {"x_CO2": kv[CO2], "Fig4_full": full, "ln_gamma_star": kv["ln_gamma_star"],
                                     "overall_activity_term": sum(v * kv["ln_gamma_star"][i] for i, v in
                                                                  {MDEAH: 1, HCO3: 1, MDEA: -1, CO2: -1, W: -1}.items())})(
            kvalue_speciation(doc, a)) for a, (full, _) in UYAN_FIG4_X_CO2.items()}
    return out


def ard(rows, solved, keep):
    dev = [abs(1 - solved[r["row"]]["p_calc"] / r["p_exp"]) for r in rows if keep(r)]
    return 100 * sum(dev) / len(dev)


def run(name):
    base, changes, convention, change = VARIANTS[name]
    doc_of_row = doc_function(name)
    rows = score.kuranov_rows()
    solved = score.solve_rows(doc_of_row if changes else BASES[base](), rows, convention(doc_of_row))
    out = {"variant": name, "change": change, **score.summary(rows, solved), "speciation_313K_w0.23": speciation(name),
           "ARD_percent_19_mass_percent_loaded_rows": ard(rows, solved, lambda r: r["m_mdea"] < 3 and r["m_co2"] > 0),
           "ARD_percent_loading_at_most_1.2": ard(rows, solved, lambda r: r["m_co2"] <= 1.2 * r["m_mdea"]),
           "osmotic_MDEAH+Cl-": osmotic_check(name),
           "Uyan_Fig5_lines": fig5_check(name) if base.startswith("uyan") else None,
           "rows": {r["row"]: {"p_exp_Pa": r["p_exp"], "p_calc_Pa": solved[r["row"]]["p_calc"],
                               "message": solved[r["row"]]["message"]} for r in rows}}
    RUNS.mkdir(parents=True, exist_ok=True)
    (RUNS / f"{name}.json").write_text(json.dumps(out, indent=1) + "\n")
    osm = out["osmotic_MDEAH+Cl-"]
    print(f"{name}: ARD {out['ARD_percent_solved_rows']:.1f} % ({out['solved']}/82), by MDEA "
          f"{[round(v, 1) for v in out['ARD_percent_by_MDEA_molality'].values()]}, mean ln(p_calc/p_exp) "
          f"{out['mean_ln_ratio']:+.2f}, osmotic ARD {osm['ARD_percent']:.1f} %"
          + (f", ln(p/Uyan Fig. 5 line) {out['Uyan_Fig5_lines']['mean_ln_ratio_to_Uyan_line']:+.2f}" if out["Uyan_Fig5_lines"] else ""),
          flush=True)
    return out


def collect():
    report = {name: json.loads((RUNS / f"{name}.json").read_text()) for name in VARIANTS}
    report["published"] = PUBLISHED
    report["kvalue_checks"] = kvalue_checks()
    report["provenance"] = {"engine_wheel_sha256": score.WHEEL_SHA256,
                            "kuranov_csv_sha256": hashlib.sha256(score.KURANOV.read_bytes()).hexdigest(),
                            "scripts_sha256": {p: hashlib.sha256((model.HERE / p).read_bytes()).hexdigest()
                                               for p in ("model.py", "score.py", "diagnose.py", "conventions.py")}}
    (score.RESULTS / "conventions.json").write_text(json.dumps(report, indent=1) + "\n")


if __name__ == "__main__":
    assert epcsaft.provenance()[1] == score.WHEEL_SHA256, "installed Engine wheel is not the pinned 21e761c3 wheel"
    check_self_dispersion()
    names = [list(VARIANTS)[int(a)] if a.isdigit() else a for a in sys.argv[1:]] or list(VARIANTS)  # name or index
    with ProcessPoolExecutor(min(16, len(names))) as pool:  # run with OMP_NUM_THREADS=1
        list(pool.map(run, names))
    if not sys.argv[1:]:
        collect()
