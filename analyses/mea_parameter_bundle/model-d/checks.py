"""#121 checks N1 and N2 on the binary NaCl-water model (binary.py). Writes n1-nacl.csv and n2-nacl.csv.

N1: NaCl osmotic coefficient at 298.15 K, 0.101325 MPa, against Hamer & Wu 1972 Table 16 (0.1-5 mol/kg;
hamer-wu-1972-nacl-osmotic.csv), ARD <= 3.5 %; invariant: Born on and off agree to 1e-10 (E3).
Variants: the base record's electrolyte family as loaded (born-as-loaded: c_shell, c_dielectric = 1, 1),
Born off (Debye-Hueckel only), and born-0-0 (c_shell = c_dielectric = 0, the form #121 describes; diagnostic).
N2 (base model as loaded; NaCl 1 and 3 mol/kg at 298.15 and 318.15 K): (i) exact identity within 1e-8 (with ln a_w also from the
mixture's own fugacity coefficient on polished roots, diagnostic), (ii) pressure transfer <= 1e-5, (iii) Approximation B correction terms and the B_w gate against IAPWS G11-15
Eq. (5) at 298.15, 318.15, 333.15 K, (iv) pressure Jacobian in k(Cl--water) and its 1/T slope (T_ref 298.15 K,
value 0) against central differences (steps 1e-4, 10 K) within 1e-5 relative, at 318.15 K.
"""
import copy
import csv
import math
import sys

import binary as b
from epcsaft import regression

T25, P_ATM = 298.15, 101325.0
M_IAPWS = 0.018015268  # kg/mol, IAPWS G11-15 p. 6
# Standard liquid-water densities (kg/m^3) at 0.1 MPa; #121 Approximation B quotes 997.05 and 983.20.
RHO_L = {298.15: 997.05, 318.15: 990.21, 333.15: 983.20}


def b_ww_iapws(T):
    """IAPWS G11-15 Eq. (5) (p. 6), coefficients Tables 1-2 (p. 5); m^3/mol. Reproduces Table 7 within 7e-10."""
    t1 = {1: (-0.5, 0.12533547935523e-1), 2: (0.875, 0.78957634722828e1), 3: (1, -0.87803203303561e1),
          8: (4, -0.66856572307965), 9: (6, 0.20433810950965), 10: (12, -0.66212605039687e-4),
          23: (7, -0.10793600908932)}
    t2 = [(0.85, 0.2, -0.14874640856724, 28, 700, 0.32), (0.95, 0.2, 0.31806110878444, 32, 800, 0.32)]
    tau = 647.096 / T
    total = sum(n * tau ** t for t, n in t1.values())
    for bi, big_b, n, c, d, a in t2:
        total += n * ((1 - tau + a) ** 2 + big_b) ** bi * math.exp(-c - d * (tau - 1) ** 2)
    return M_IAPWS / 322.0 * total


def write(name, rows):
    with (b.HERE / name).open('w', newline='') as h:
        w = csv.DictWriter(h, list(rows[0]), lineterminator='\n')
        w.writeheader()
        w.writerows(rows)


def n1():
    ref = list(csv.DictReader((b.HERE / 'hamer-wu-1972-nacl-osmotic.csv').open()))
    zero = b.document((b.NA, b.CL))
    family = next(f for f in zero['model_families'] if f['kind'] == 'electrolyte')
    family.update(c_shell=0.0, c_dielectric=0.0)
    models = {'born-as-loaded': b.epcsaft.Mixture(b.parameters((b.NA, b.CL))),
              'born-off': b.epcsaft.Mixture(b.parameters((b.NA, b.CL), born=False)),
              'born-0-0': b.epcsaft.Mixture(b.epcsaft.Parameters.from_mapping(zero))}
    rows = []
    for r in ref:
        m = float(r['molality_mol_per_kg'])
        phi = {k: b.activity(model, T25, P_ATM, m)[0] for k, model in models.items()}
        rows.append({'molality_mol_per_kg': m, 'phi_hamer_wu': float(r['osmotic_coefficient']),
                     **{f'phi_{k}': v for k, v in phi.items()}})
    for k in models:
        ard = 100 * sum(abs(x[f'phi_{k}'] / x['phi_hamer_wu'] - 1) for x in rows) / len(rows)
        print(f'N1 {k}: NaCl phi ARD {ard:.3f} % (limit 3.5 %)')
    for k in ('born-as-loaded', 'born-0-0'):
        print(f'N1 invariant {k} vs born-off: max |d phi| {max(abs(x[f"phi_{k}"] - x["phi_born-off"]) for x in rows):.3e} (limit 1e-10)')
    write('n1-nacl.csv', rows)


def n2():
    model = b.epcsaft.Mixture(b.parameters((b.NA, b.CL)))
    rows = []
    for T in (298.15, 318.15):
        psat = b.saturation_pressure(model, T)
        for m in (1.0, 3.0):
            p_b = b.bubble(model, T, m, 0.97 * psat).pressure[0]
            ln_aw = b.activity(model, T, p_b, m)[1]
            ln_aw_atm = b.activity(model, T, P_ATM, m)[1]
            identity = b.identity_ln_aw(model, T, p_b)
            v_l = 1.0 / b.pure_state(model, T, psat, 'liquid').molar_density
            correction = (b.ln_phi_pure(model, T, p_b, 'vapor') - b.ln_phi_pure(model, T, psat, 'vapor')
                          - v_l * (p_b - psat) / (b.R * T))
            rows.append({'check': 'N2(i)(ii)(iii)', 'T_K': T, 'molality': m, 'p_bubble_pa': p_b, 'p_sat_model_pa': psat,
                         'ln_aw_activity': ln_aw, 'ln_aw_identity': identity, 'i_abs_difference': abs(ln_aw - identity),
                         'ln_aw_mixture_fugacity': b.mixture_ln_aw(model, T, p_b, m),
                         'identity_minus_mixture_fugacity': identity - b.mixture_ln_aw(model, T, p_b, m),
                         'i_pass': abs(ln_aw - identity) <= 1e-8, 'ii_abs_transfer': abs(ln_aw - ln_aw_atm),
                         'ii_pass': abs(ln_aw - ln_aw_atm) <= 1e-5, 'iii_correction': correction,
                         'iii_correction_per_molality': correction / m})
    for T in (298.15, 318.15, 333.15):
        b_model = {p: b.ln_phi_pure(model, T, p, 'vapor') * b.R * T / p for p in (1.0, 10.0, 100.0)}
        b_ref, v_l = b_ww_iapws(T), M_IAPWS / RHO_L[T]
        rows.append({'check': 'N2(iii) B_w gate', 'T_K': T, 'B_model_m3_per_mol_at_1pa': b_model[1.0],
                     'B_model_m3_per_mol_at_10pa': b_model[10.0], 'B_model_m3_per_mol_at_100pa': b_model[100.0],
                     'B_ref_iapws_m3_per_mol': b_ref, 'v_l_m3_per_mol': v_l,
                     'iii_ratio': abs(b_model[1.0] - b_ref) / abs(b_ref - v_l),
                     'iii_pass': abs(b_model[1.0] - b_ref) <= 0.3 * abs(b_ref - v_l)})
    rows += derivative_rows()
    for r in rows:
        print({k: v for k, v in r.items()})
    fields = list(dict.fromkeys(k for r in rows for k in r))
    write('n2-nacl.csv', [{k: r.get(k, '') for k in fields} for r in rows])


def derivative_rows(T=318.15):
    """N2(iv): exact implicit pressure derivatives against central differences."""
    rows = []
    pair = (b.CL, b.W)
    for m in (1.0, 3.0):
        def params(dk=0.0, db=0.0):
            return b.parameters((b.NA, b.CL), [(*pair, -0.25 + dk, 0.0 + db, 298.15)])
        base = params()
        psat = b.saturation_pressure(b.epcsaft.Mixture(base), T)
        problem = b.bubble_problem(b.epcsaft.Mixture(base), T, m, 0.97 * psat)
        ids = base.component_ids
        i, j = sorted((ids.index(b.CL), ids.index(b.W)))
        slots = [i * len(ids) + j, j * len(ids) + i]
        active = [b.epcsaft.ActiveParameter(b.epcsaft.ParameterFamily.Kij, slots),
                  b.epcsaft.ActiveParameter(b.epcsaft.ParameterFamily.KijReciprocalTemperatureSlope, slots)]
        model = b.epcsaft.Mixture(base, active_parameters=active)
        item = regression.observation(base, 'pressure', problem, observed=psat, form='log_ratio', mass_basis=False)
        centre = regression.predict(model, item)
        exact = regression.differentiate(model, item).value

        def value(p):
            obs = regression.observation(p, 'pressure', problem, observed=psat, form='log_ratio', mass_basis=False)
            return regression.predict(b.epcsaft.Mixture(p), obs).value
        central = [(value(params(dk=1e-4)) - value(params(dk=-1e-4))) / 2e-4,
                   (value(params(db=10.0)) - value(params(db=-10.0))) / 20.0]
        for name, e, c in zip(('k_ij', 'k_ij_reciprocal_temperature_slope'), exact, central):
            rows.append({'check': 'N2(iv)', 'T_K': T, 'molality': m, 'p_bubble_pa': centre.value, 'coordinate': name,
                         'exact_dp_dtheta': e, 'central_dp_dtheta': c, 'iv_relative_difference': abs(e / c - 1),
                         'iv_pass': abs(e / c - 1) <= 1e-5, 'solve_residual': centre.convergence.residual,
                         'requested_tolerance_met': centre.requested_tolerance_met})
    return rows


if __name__ == '__main__':
    {'n1': n1, 'n2': n2}[sys.argv[1]]()
