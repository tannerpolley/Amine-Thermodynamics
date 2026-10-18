"""#161: nominally unloaded 30 wt% MEA Cp at 353.15 K on the pinned Engine wheel.

Admission is verify_temperature_reference.solve unchanged (success and max |raw residual| <= 1e-9).
Cp is the #124 producer: (n dH/dT + H dn/dT) / feed mass, checked against centered re-solved
enthalpies at 0.1 and 0.05 K. Feed mass is reported on both bases in use: MEA's
verify_solution_heat_capacity.MOLAR_MASS and the request's molar_masses_kg_per_mol (Engine #261 test).
"""
import hashlib
import math
import sys
import time
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parents[1] / 'scripts'))
import fit_campaign as fc  # noqa: E402  (sets one numerical-library thread)
import shared_evaluation as s  # noqa: E402
import verify_reference_calorics as vrc  # noqa: E402
import verify_solution_heat_capacity as hc  # noqa: E402
import verify_temperature_reference as vt  # noqa: E402
import epcsaft  # noqa: E402

T, P, STEPS = 353.15, 101325., (0.1, 0.05)
BUNDLE = 'analyses/mea_parameter_bundle/results/'
REQUEST = BUNDLE + 'density-cp-160/cp-124-assessment/solution-request-0.0.json'
RECORDS = {
    '124-record-756fec50': (BUNDLE + 'density-cp-160/D1-evidence/F1-double-prime-candidate-parameters.json',
                            '756fec502d3a1433d538abb073c4caeabf91902013ab7e27d5459ce70396543b'),
    'selected-current-7b0b4bb5': (BUNDLE + 'selected-current-best-parameters.json',
                                  '7b0b4bb5669c1b2061fd7ec26e5fb4c8491005bdb5ba8f9e22e4c0b0b4b84308'),
}
SPEC = dict(
    inputs=[dict(path=REQUEST, sha256='bc8a03e13efab9a9675a63121c12538dbb9f42a18dbe4ddc7fe6742b6ab6da61'),
            dict(path='data/reference/MEA/thermal/physical-ideal-gas-calorics.json',
                 sha256='c94d504e68c6dc6e85d3d950cc51422499846729b1a06994b362040be991924a'),
            *(dict(path=p, sha256=h) for p, h in RECORDS.values())],
    engine=dict(wheel_path='build/engine-wheels/main-21e761c318c2ac5b555a245365c844d38a93e4cb/'
                           'epcsaft-0.2.0.dev0-cp313-cp313-manylinux_2_39_x86_64.whl',
                wheel_sha256=s.ENGINE_WHEEL_SHA256, packages=dict(numpy='2.4.4', scipy='1.17.1')))
# kJ/(kg K). Engine: ePC-SAFT #261 delivery (PR #263, 9c31cb9a) on record 756fec50.
# MEA: unloaded = #161 scratch replay on wheel 36485a88 (#124 design comment); loaded =
# density-cp-160/cp-124-assessment/loaded-80C-decomposition.json (wheel 48a639e7).
# Hilliard 2008 App. G.2 p. 937 (7 mol MEA/kg water; +/-2 %).
COMPARE = {1e-5: dict(engine=3.8436879, mea_prior=3.843630799, hilliard=3.8566),
           .358: dict(engine=3.3147698, mea_prior=3.3147180836891086, hilliard=3.4707)}


def request(mapping, loading, temperature=T):
    """The #124 evaluate.py solution_state generator (7 mol MEA/kg water, seed scale 0.01 below 1e-4)."""
    template = next(o['request'] for o in s.load_state_packet()['observations']
                    if o['identity'] == 'Bottinger2008_state_046')
    req = s.source_feed_request(template, dict(source_key='Amundsen2009', CO2_loading=loading,
        temperature_reported_C=temperature-273.15, MEA_weight_fraction=7*.0610831/(1+7*.0610831)))
    if loading < 1e-4:
        system = req['reaction_system']
        analytical = system['analytical_feed_contract']['neutral_analytical_amounts_mol']
        system['feed_amounts_mol'] = [a+.01*(v-a) for a, v in zip(analytical, system['feed_amounts_mol'], strict=True)]
        system.pop('analytical_feed_contract')
        req['feed'] = dict(basis='7 mol MEA/kg water', proxy_loading=loading, numerical_seed_scale=.01)
    return s.corrected_request(vt.request_at(req, temperature, P, liquid_only=True), s.reaction_values(mapping))


def enthalpy(model, problem, result):
    (h, dh), (n, dn) = vrc.first_actions(model, problem, result, [
        vrc.observable('PhaseProperty', 0, prop=epcsaft.PropertyObservable.TotalEnthalpy),
        vrc.observable('PhaseAmount', 0)], [(1., 0., None)])[0]
    return h*n, n*dh+h*dn, n


def state(model, build):
    req = build(T)
    row = dict(gate='verify_temperature_reference.solve: success and max|raw residual| <= 1e-9')
    try:
        problem, result = vt.solve(model, req)
    except RuntimeError as error:
        problem = s._problem_from_request(req)
        result = epcsaft.equilibrium.solve_equilibrium(model, problem)
        return dict(row, admitted=False, refusal=str(error), raw_residual_max=max(map(abs, result.residuals)),
                    termination=result.message)
    raw = list(result.residuals)
    recomputed = epcsaft.equilibrium.compile_problem(model, problem).evaluate(result.coordinates).values
    system = req['reaction_system']
    masses = dict(mea_basis=math.fsum(problem.feed.values[c]*m for c, m in zip(s.COMPONENT_IDS, hc.MOLAR_MASS))/1e3,
                  request_basis=math.fsum(n*m for n, m in zip(system['feed_amounts_mol'], system['molar_masses_kg_per_mol'])))
    _, dH, n = enthalpy(model, problem, result)
    Q = epcsaft.PropertyObservable
    frozen = [v*n/masses['mea_basis']/1e3 for v, _ in vrc.first_actions(model, problem, result, [
        vrc.observable('PhaseProperty', 0, prop=q) for q in (Q.IdealIsobaricHeatCapacity,
        Q.ResidualIsobaricHeatCapacity, Q.TotalIsobaricHeatCapacity)], [(0., 0., None)])[0]]
    cp = dH/masses['mea_basis']/1e3
    row.update(admitted=True, raw_residual_max=max(map(abs, raw)), raw_residual_recomputed_max=max(map(abs, recomputed)),
               classified_residual=result.convergence.residual, iterations=result.convergence.iterations,
               termination=result.message, feed_mass_kg=masses,
               mass_ratio_mea_over_request=masses['mea_basis']/masses['request_basis'],
               equilibrium_cp_kJ_kg_K=dict(mea_basis=cp, request_basis=dH/masses['request_basis']/1e3),
               frozen_cp_kJ_kg_K=dict(zip(('ideal', 'residual', 'total'), frozen)),
               reaction_response_kJ_kg_K=cp-frozen[2],
               liquid_composition=list(result.mole_fractions[:len(s.COMPONENT_IDS)]), resolve=[])
    for step in STEPS:
        ends = [enthalpy(model, *vt.solve(model, build(T+d*step)))[0] for d in (-1, 1)]
        fd = (ends[1]-ends[0])/(2*step)/masses['mea_basis']/1e3
        row['resolve'].append(dict(step_K=step, cp_kJ_kg_K=fd, relative_difference=abs(fd/cp-1)))
    coarse, fine = (r['relative_difference'] for r in row['resolve'])
    row['cp_numerically_verified'] = fine <= 1e-6 and fine < coarse
    row['cp_verified_with_half_error_rule'] = fine <= 1e-6 and fine <= coarse/2
    return row


def main():
    started = time.monotonic()
    out = dict(question='#161: does the #124 nominally unloaded 30 wt% MEA state pass the unchanged 1e-9 raw gate '
                        'on the pinned wheel, and what is its equilibrium Cp?',
               conditions=dict(T_K=T, P_Pa=P, mea_mol_per_kg_water=7., unloaded_proxy_loading=1e-5,
                               phases='one nine-species liquid', reactions='R1-R5 of each record'),
               verification=fc.verify(SPEC), states=[])
    archived = fc.load(fc.ROOT/REQUEST)
    for label, (path, _) in RECORDS.items():
        mapping = s.parameter_mapping(fc.ROOT/path)
        if 'no_cross_association' not in mapping['topology']:
            # Wheel 21e761c3 requires the #191 declaration; add it in memory exactly as in the selected record.
            edges = {tuple(sorted((e['endpoint_a']['component_id'], e['endpoint_b']['component_id'])))
                     for e in mapping['topology']['edges']}
            assert ('carbon-dioxide', 'monoethanolamine') not in edges
            mapping['topology']['no_cross_association'] = [dict(
                component_id_a='carbon-dioxide', component_id_b='monoethanolamine', provenance=dict(
                    locator=f'{path}: topology.edges has no carbon-dioxide/monoethanolamine edge; '
                            'existing model kept; declared in memory for #161 (#191 form)',
                    source_id=mapping['document_id']))]
            out['declared_in_memory'] = {label: 'topology.no_cross_association carbon-dioxide/monoethanolamine (#191)'}
        model = epcsaft.Mixture(epcsaft.Parameters.from_mapping(mapping), thermochemistry=vrc.record())
        for loading in COMPARE:
            req = request(mapping, loading)
            if label.startswith('124') and loading < 1e-4:
                assert req == archived, 'rebuilt #124 request differs from archived bc8a03e1'
            row = dict(record=label, nominal_loading=0. if loading < 1e-4 else loading, model_loading=loading,
                       request_rebuilt_equals_archived=(req == archived) if loading < 1e-4 else None, **state(model, lambda t: request(mapping, loading, t)))
            if row['admitted']:
                cp = row['equilibrium_cp_kJ_kg_K']
                ref = COMPARE[loading]
                row['comparison'] = dict(
                    hilliard_kJ_kg_K=ref['hilliard'], model_minus_hilliard_relative=cp['mea_basis']/ref['hilliard']-1,
                    **(dict(engine_kJ_kg_K=ref['engine'], mea_prior_kJ_kg_K=ref['mea_prior'],
                            mea_basis_minus_engine_relative=cp['mea_basis']/ref['engine']-1,
                            request_basis_minus_engine_relative=cp['request_basis']/ref['engine']-1,
                            mea_basis_minus_mea_prior_relative=cp['mea_basis']/ref['mea_prior']-1)
                       if label.startswith('124') else {}))
            out['states'].append(row)
            print(label, loading, row.get('raw_residual_max'), row.get('equilibrium_cp_kJ_kg_K'), flush=True)
    out['wall_s'] = time.monotonic()-started
    out['producer_sha256'] = hashlib.sha256(Path(__file__).read_bytes()).hexdigest()
    out['claim_limit'] = ('Numerical verification of admission and the equilibrium Cp action at one temperature; '
                          'Hilliard comparison is conditional prediction for these records, not physical validation. '
                          'Loading 1e-5 is a numerical proxy for zero; no proxy-convergence, temperature sweep, '
                          'parameter change or C5 replay is performed here.')
    fc.write(HERE/'summary.json', out)


if __name__ == '__main__':
    main()
