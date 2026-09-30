"""#121 binary salt-water models: the base record (probe.RECORD) plus Held 2014 Na+ and Cl-.

Every binary calculation uses the base record's water, HCO3- and MEAH+ unchanged (0.88 sigma Debye-Hueckel
diameter), and Na+/Cl- in Held's convention (packing 0.88 sigma, Debye-Hueckel and Born sigma; Held 2014
Tables 2-3, Held 2008 Sec. 2 Eqs. 2-3). Salt-water pairs are fixed here; the fitted ion-water pairs are
passed as overrides. Compositions use the record's water molar mass, so Engine molalities and the
bubble-point liquid are the same solution (E2).
"""
import copy
import math
import sys
from pathlib import Path

HERE = Path(__file__).parent
sys.path.insert(0, str(HERE.parent / 'calibration-misfit'))
import probe  # noqa: E402

s, epcsaft = probe.shared, probe.epcsaft
from epcsaft import equilibrium as eq  # noqa: E402

W, NA, CL = 'water', 'sodium-cation', 'chloride-anion'
HCO3, MEAH = 'bicarbonate-anion', 'protonated-monoethanolamine'
R = epcsaft.GAS_CONSTANT_J_PER_MOL_K
HELD_SOURCE = {'source_id': 'held-2014', 'locator': 'Held 2014 Tables 2 (strategy 2) and 3; Held 2008 Sec. 2 Eqs. 2-3'}
# Held 2014 Table 2: sigma (angstrom), u/k (K); Table 3 and footnote a: k_ij.
IONS = {NA: (2.8232, 230.0, +1, 0.02298977), CL: (2.7560, 170.0, -1, 0.035453)}
NA_WATER_T_REF = 298.15
PAIRS = {  # (a, b): (k_ij, slope b in K or None, T_ref)
    (NA, W): (2.37999 - 0.007981 * NA_WATER_T_REF, 0.007981 * NA_WATER_T_REF ** 2, NA_WATER_T_REF),  # 1/T tangent
    (CL, W): (-0.25, None, None), (CL, NA): (0.317, None, None), (HCO3, NA): (-0.514, None, None),
    (CL, MEAH): (0.0, None, None),  # Wangler 2018 Sec. 6.1.4 set MDEAH+-Cl- to 0
}
SLOPE = '/k_ij/reciprocal_temperature_slope'


def _pair_id(a, b):
    a, b = sorted((a, b))
    return f'pair/{a}/{b}/k_ij'


_BASE_PAIRS = [c for p in s.parameter_mapping(probe.RECORD)['pairs'] for c in p['coefficients']]
_TEMPLATE = {f: next(c for c in _BASE_PAIRS if c['family'] == f) for f in ('k_ij', 'k_ij_reciprocal_temperature_slope')}


def _slope_node(ident, value, t_ref, source):
    node = copy.deepcopy(_TEMPLATE['k_ij_reciprocal_temperature_slope'])
    node.update({'identity': ident, 'value': {'magnitude': value, 'unit': 'kelvin'},
                 'reference_temperature': {'magnitude': t_ref, 'unit': 'kelvin'}})
    node['provenance'] = {**node['provenance'], **source}
    return node


def _set_pair(mapping, a, b, k, slope=None, t_ref=None, source=HELD_SOURCE):
    """Set (or add) the k_ij of a pair and, when given, its 1/T slope with its own reference temperature."""
    ident = _pair_id(a, b)
    _, x, y, _ = ident.split('/')
    pair = next((p for p in mapping['pairs'] if {p['component_id_a'], p['component_id_b']} == {x, y}), None)
    template = copy.deepcopy(_TEMPLATE['k_ij'])
    if pair is None:
        pair = {'component_id_a': x, 'component_id_b': y, 'coefficients': []}
        mapping['pairs'].append(pair)
    pair['coefficients'] = [c for c in pair['coefficients'] if c['identity'] not in (ident, ident + '/reciprocal_temperature_slope')]
    template.update({'identity': ident, 'value': {'magnitude': k, 'unit': 'dimensionless'}})
    template['provenance'] = {**template['provenance'], **source}
    pair['coefficients'].append(template)
    if slope is not None:
        pair['coefficients'].append(_slope_node(ident + '/reciprocal_temperature_slope', slope, t_ref, source))


def document(salt, pairs=(), born=True):
    """The base record reduced to water and one salt (cation, anion), with Na+ and Cl- added as Held gives them.

    Only the solution's species are kept: absent species would leave null directions in the bubble-point solve.
    ``pairs``: (a, b, k, slope or None, T_ref or None) overrides; ``born=False`` selects the Debye-Hueckel-only
    electrolyte family (the E3 invariant)."""
    mapping = copy.deepcopy(s.parameter_mapping(probe.RECORD))
    template = next(c for c in mapping['components'] if c['component_id'] == HCO3)
    for ion, (sigma, u, z, molar_mass) in IONS.items():
        c = copy.deepcopy(template)
        c.update({'component_id': ion, 'name': ion, 'aliases': [ion]})
        c['fixed']['charge_number']['value']['magnitude'] = z
        c['fixed']['molar_mass']['value']['magnitude'] = molar_mass
        for field in c['fixed'].values():
            field['provenance'] = {**field['provenance'], **HELD_SOURCE}
        values = {'segment_count': 1.0, 'segment_diameter': sigma, 'dispersion_energy_over_k': u,
                  'packing_diameter': 0.88 * sigma, 'debye_huckel_diameter': sigma, 'born_diameter': sigma,
                  'solvation_factor': 1.0}
        for node in c['coefficients']:
            node['identity'] = f"component/{ion}/{node['family']}"
            node['value'] = {**node['value'], 'magnitude': values[node['family']]}
            node['provenance'] = {**node['provenance'], **HELD_SOURCE}
        mapping['components'].append(c)
    keep = {W, *salt}
    mapping['components'] = [c for c in mapping['components'] if c['component_id'] in keep]
    mapping['pairs'] = [p for p in mapping['pairs'] if {p['component_id_a'], p['component_id_b']} <= keep]
    mapping['correlations'] = [c for c in mapping['correlations'] if c['component_id'] in keep]
    topology = mapping['topology']
    topology['sites'] = [x for x in topology['sites'] if x['component_id'] in keep]
    topology['edges'] = [e for e in topology['edges']
                         if {e['endpoint_a']['component_id'], e['endpoint_b']['component_id']} <= keep]
    for (a, b), (k, slope, t_ref) in PAIRS.items():
        if {a, b} <= keep:
            _set_pair(mapping, a, b, k, slope, t_ref)
    for a, b, k, slope, t_ref in pairs:
        _set_pair(mapping, a, b, k, slope, t_ref, {'source_id': 'mea-121-binary', 'locator': 'model-d/binary.py'})
    if not born:  # the Born-only inputs are then unconsumed, which the Engine refuses
        family = next(f for f in mapping['model_families'] if f['kind'] == 'electrolyte')
        family['choice'] = 'fully-dissociated-debye-huckel'
        for key in ('c_shell', 'c_dielectric'):
            family.pop(key, None)
        for c in mapping['components']:
            c['coefficients'] = [x for x in c['coefficients'] if x['family'] not in ('solvation_factor', 'born_diameter')]
        mapping['model_coefficients'] = [x for x in mapping['model_coefficients']
                                         if x['family'] != 'ionic_region_relative_permittivity']
    return mapping


def parameters(salt, pairs=(), born=True):
    return epcsaft.Parameters.from_mapping(document(salt, pairs, born))


M_W = next(c for c in s.parameter_mapping(probe.RECORD)['components']
           if c['component_id'] == W)['fixed']['molar_mass']['value']['magnitude']  # 0.01801528 kg/mol, the record's


def pure_water(model):
    return [1.0 if c == W else 0.0 for c in model.component_ids]


def composition(model, m):
    """E2: mole fractions of the model's fully dissociated 1:1 salt at molality m (mol/kg water)."""
    total = 1.0 / M_W + 2.0 * m
    return [(1.0 / M_W) / total if c == W else m / total for c in model.component_ids]


def polished_state(model, T, P, x, phase):
    """The phase's root at (T, P, x) with the density polished until P(rho) = P: the Engine's liquid root leaves
    P(rho) about 1e-8 (relative) off P at a few kPa, which moves ln phi_L by about 1e-8."""
    state = model.state(T, P=P, x=x, phase=phase)
    rho = state.molar_density
    for _ in range(4):
        rho -= (state.pressure - P) / state.pressure_density_derivative
        state = model.state(T, rho=rho, x=x)
    return state


def pure_state(model, T, P, phase):
    return polished_state(model, T, P, pure_water(model), phase)


def mixture_ln_aw(model, T, P, m):
    """ln a_w = ln x_w + ln phi_w(T, P, x) - ln phi_w^L,pure(T, P), from polished liquid roots (E2)."""
    x, iw = composition(model, m), model.component_ids.index(W)
    return (math.log(x[iw]) + polished_state(model, T, P, x, 'liquid').log_fugacity_coefficient[iw]
            - ln_phi_pure(model, T, P, 'liquid'))


def ln_phi_pure(model, T, P, phase):
    return pure_state(model, T, P, phase).log_fugacity_coefficient[model.component_ids.index(W)]


def identity_ln_aw(model, T, P):
    """E4: ln phi_w^V,pure - ln phi_w^L,pure at (T, P); equals the model's ln a_w at its bubble pressure."""
    return ln_phi_pure(model, T, P, 'vapor') - ln_phi_pure(model, T, P, 'liquid')


def target_pressure(model, T, ln_aw, guess):
    """E4: the pressure p* at which the pure-water identity equals ln_aw (Newton in ln p; d g/d ln p = Z_V - Z_L)."""
    iw, ln_p = model.component_ids.index(W), math.log(guess)
    for _ in range(60):
        p = math.exp(ln_p)
        v, l = (pure_state(model, T, p, ph) for ph in ('vapor', 'liquid'))
        g = v.log_fugacity_coefficient[iw] - l.log_fugacity_coefficient[iw] - ln_aw
        step = g / (v.compressibility_factor - l.compressibility_factor)
        ln_p -= step
        if abs(step) < 5e-9:  # the polished pure-water ln phi difference still varies by ~1e-9
            return math.exp(ln_p)
    raise RuntimeError(f'target pressure did not converge at T={T}, ln a_w={ln_aw}')


def ions(model):
    return tuple(c for c in model.component_ids if c != W)


def activity(model, T, P, m):
    """Engine infinite-dilution reference: (osmotic coefficient, ln a_w = -2 m M_w phi)."""
    cation, anion = sorted(ions(model), key=lambda c: c not in (NA, MEAH))
    ref = model.reference(T, P, solvent_fractions=pure_water(model), ions=(cation, anion), stoichiometry=(1, 1))
    phi = ref.activity(m).osmotic_coefficient
    return phi, -2.0 * m * M_W * phi


def bubble_problem(model, T, m, guess):
    """Bubble point of the salt solution with the vapor limited to water (E4)."""
    x = composition(model, m)
    return eq.Problem(
        phases=[eq.Phase('L', kind='liquid', support=list(model.component_ids), composition_guess=x),
                eq.Phase('V', kind='vapor', support=[W], amount=eq.Pinned(0.0), composition_guess=[1.0])],
        T=T, P=eq.Free(guess), feed=eq.Amounts(dict(zip(model.component_ids, x))))


def bubble(model, T, m, guess):
    result = eq.solve_equilibrium(model, bubble_problem(model, T, m, guess))
    if not result.success:
        raise RuntimeError(f'bubble point failed at T={T} m={m}: {result.message}')
    return result


def saturation_pressure(model, T):
    return target_pressure(model, T, 0.0, 3000.0 * math.exp(5200 * (1 / 298.15 - 1 / T)))
