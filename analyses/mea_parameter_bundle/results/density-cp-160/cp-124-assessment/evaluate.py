"""Fixed-record #124 assessment using accepted IAPWS-95 and native Engine calls."""
import csv
import hashlib
import importlib.metadata
import json
import math
from pathlib import Path
import sys
import time

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[4]
BUNDLE = ROOT / 'analyses/mea_parameter_bundle'
PRIMARY = [298.15 + 5*i for i in range(20)]
STAGGERED = [300.65 + 5*i for i in range(19)]
CONTROLS = [298.15, 318.15, 353.15]


def digest(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def retain(name, value):
    with (HERE / name).open('x') as stream:
        json.dump(value, stream, indent=2, sort_keys=True, allow_nan=False)
        stream.write('\n')


def table(name, rows):
    fields = list(dict.fromkeys(k for row in rows for k in row))
    with (HERE / name).open('x', newline='') as stream:
        writer = csv.DictWriter(stream, fields, lineterminator='\n')
        writer.writeheader()
        writer.writerows(rows)


def reference():
    from chemicals import iapws
    assert importlib.metadata.version('chemicals') == '1.5.2'
    rows = []
    for grid, temperatures, pressure in [('primary', PRIMARY, 300000.),
                                         ('staggered', STAGGERED, 300000.),
                                         ('atmospheric-controls', CONTROLS, 101325.)]:
        for T in temperatures:
            values = iapws.iapws95_properties(T, pressure)
            rows.append(dict(grid=grid, T_K=T, P_Pa=pressure, rho_kg_m3=values[0],
                cp_kJ_kg_K=values[5]/1000, psat_Pa=iapws.iapws95_Psat(T),
                saturated_liquid_rho_kg_m3=iapws.iapws95_rhol_sat(T)))
    table('iapws95-reference.csv', rows)
    engine = Path('/home/tnnrpolley21/Workspaces/Engineering/ePC-SAFT')
    retained = engine / 'analyses/2026-heat-capacity-fitting'
    retain('reference-provenance.json', dict(source='IAPWS R6-95(2018)', zotero_key='Y3FU9CXJ',
        release_url='https://iapws.org/technical-guidance/release/IAPWS-95',
        implementation='chemicals 1.5.2', module_path=iapws.__file__, module_sha256=digest(iapws.__file__),
        interpreter=sys.executable, producer_sha256=digest(__file__),
        prior_verification_summary=json.loads((retained/'results/reference-summary.json').read_text()),
        prior_verification_csv_sha256=digest(retained/'results/reference-verification.csv'),
        prior_reference_source_sha256=digest(retained/'inputs/source.json'),
        reference_sha256=digest(HERE/'iapws95-reference.csv'),
        source_class='Evaluated reference; prior 59 checks verify implementation, not physical uncertainty.'))


def models():
    started = time.monotonic()
    sys.path.insert(0, str(BUNDLE / 'scripts'))
    import density_cp_160 as d
    import epcsaft
    from epcsaft import equilibrium as eq
    Q, e = epcsaft.PropertyObservable, epcsaft.eos
    wheel = Path(json.loads(importlib.metadata.distribution('epcsaft').read_text('direct_url.json'))['url'][7:])
    assert digest(wheel) == '48a639e78d00ef88a2f7e66ed1e3d89831ca0ad5267322330d44f48c34926060'
    paths = {'original': HERE/'original-record.json',
             'adopted': BUNDLE/'results/density-cp-160/D1-evidence/F1-double-prime-candidate-parameters.json'}
    assert digest(paths['original']) == '9055458d8b7cd767a0d08e9f37e4fd28631e29c363364d7b842ebade645cb241'
    assert digest(paths['adopted']) == '756fec502d3a1433d538abb073c4caeabf91902013ab7e27d5459ce70396543b'
    water = d.vrc.CALORICS['components']['water']; p0 = d.vrc.CALORICS['reference_pressure_pa']
    thermal = e.ThermochemistryRecord(p0, [[e.IdealInterval(*water['range_k'], True, True,
        e.IdealCorrelation(e.IdealShomate(tuple(water['coefficients']),
            water['formation_enthalpy_j_per_mol']), p0))]])
    references = list(csv.DictReader((HERE/'iapws95-reference.csv').open()))
    rows = []
    for label, path in paths.items():
        mapping = d.s.parameter_mapping(path)
        model = epcsaft.Pure(epcsaft.Parameters.from_mapping(mapping, components=['water']), thermochemistry=thermal)
        for ref in references:
            T, P = float(ref['T_K']), float(ref['P_Pa'])
            row = dict(record=label, grid=ref['grid'], T_K=T, P_Pa=P)
            try:
                state = model.state(T, P=P, phase='liquid')
                cp, rho = state.total_isobaric_heat_capacity/.01801528/1000, state.molar_density*.01801528
                row.update(cp_kJ_kg_K=cp, rho_kg_m3=rho,
                    cp_reference_kJ_kg_K=float(ref['cp_kJ_kg_K']), rho_reference_kg_m3=float(ref['rho_kg_m3']),
                    cp_error_relative=cp/float(ref['cp_kJ_kg_K'])-1,
                    rho_error_relative=rho/float(ref['rho_kg_m3'])-1,
                    dP_drho=state.pressure_density_derivative, density_termination=state.density_convergence)
                for step, name in [(.1, 'coarse'), (.05, 'fine')]:
                    fd = (model.state(T+step, P=P, phase='liquid').total_enthalpy
                          - model.state(T-step, P=P, phase='liquid').total_enthalpy)/(2*step)/.01801528/1000
                    row[name+'_enthalpy_cp_kJ_kg_K'] = fd
                    row[name+'_error_relative'] = abs(fd/cp-1)
                row['cp_numerically_verified'] = (row['fine_error_relative'] <= 1e-6
                    and row['fine_error_relative'] <= row['coarse_error_relative']/2 and row['dP_drho'] > 0)
                if ref['grid'] != 'atmospheric-controls':
                    prob = eq.Problem(T=T, P=eq.Free(float(ref['psat_Pa'])), feed=eq.Amounts({'water': 1.}),
                        phases=[eq.Phase('L', kind='liquid', amount=eq.Free(), composition_guess=(1.,)),
                                eq.Phase('V', kind='vapor', amount=eq.Pinned(0.), composition_guess=(1.,))],
                        row_tolerance=1e-10)
                    result = eq.solve_equilibrium(model, prob)
                    row.update(saturation_termination=result.message,
                        saturation_max_abs_residual=max(map(abs, result.residuals)))
                    if not result.success or row['saturation_max_abs_residual'] > 1e-9:
                        raise RuntimeError(result.message)
                    psat, rhosat = result.pressure[0], result.molar_densities[0]*.01801528
                    row.update(psat_Pa=psat, saturated_liquid_rho_kg_m3=rhosat,
                        psat_reference_Pa=float(ref['psat_Pa']), saturated_liquid_rho_reference_kg_m3=float(ref['saturated_liquid_rho_kg_m3']),
                        psat_error_relative=psat/float(ref['psat_Pa'])-1,
                        saturated_liquid_rho_error_relative=rhosat/float(ref['saturated_liquid_rho_kg_m3'])-1)
                row['evaluated'] = True
            except Exception as error:
                row.update(evaluated=False, failure=f'{type(error).__name__}: {error}')
            rows.append(row)
    table('water.csv', rows)

    mapping = d.s.parameter_mapping(paths['adopted'])
    model = epcsaft.Mixture(epcsaft.Parameters.from_mapping(mapping), thermochemistry=d.vrc.record())
    template = next(o['request'] for o in d.s.load_state_packet()['observations'] if o['identity']=='Bottinger2008_state_046')
    w = 7*.0610831/(1+7*.0610831)
    def solution_state(T, alpha):
        req = d.s.source_feed_request(template, dict(source_key='Amundsen2009', CO2_loading=alpha,
            temperature_reported_C=T-273.15, MEA_weight_fraction=w))
        if alpha < .0001:
            system = req['reaction_system']; analytical = system['analytical_feed_contract']['neutral_analytical_amounts_mol']
            system['feed_amounts_mol'] = [a+.01*(v-a) for a, v in zip(analytical, system['feed_amounts_mol'], strict=True)]
            system.pop('analytical_feed_contract')
            req['feed'] = dict(basis='7 mol MEA/kg water', proxy_loading=alpha, numerical_seed_scale=.01)
        req = d.s.corrected_request(d.vt.request_at(req, T, 101325., liquid_only=True), d.s.reaction_values(mapping))
        problem, result = d.vt.solve(model, req)
        return req, problem, result
    hobs = [d.vrc.observable('PhaseProperty', 0, prop=Q.TotalEnthalpy), d.vrc.observable('PhaseAmount', 0)]
    solution = []
    for nominal_alpha, observed in [(0., 3.8566), (.358, 3.4707)]:
        alpha = max(nominal_alpha, 1e-5); req, problem, result = solution_state(353.15, alpha)
        mass = sum(problem.feed.values.get(c, 0.)*m for c, m in zip(d.s.COMPONENT_IDS, d.hc.MOLAR_MASS))/1000
        (h, dh), (n, dn) = d.vrc.first_actions(model, problem, result, hobs, [(1., 0., None)])[0]
        cp = (n*dh+h*dn)/mass/1000
        props = [d.vrc.observable('PhaseProperty', 0, prop=q) for q in
                 [Q.IdealIsobaricHeatCapacity, Q.ResidualIsobaricHeatCapacity, Q.TotalIsobaricHeatCapacity]]
        frozen = [item[0]*n/mass/1000 for item in d.vrc.first_actions(model, problem, result, props, [(0., 0., None)])[0]]
        row = dict(T_K=353.15, P_Pa=101325., mea_mol_kg_water=7., nominal_alpha=nominal_alpha,
            model_alpha=alpha, observed_kJ_kg_K=observed, equilibrium_cp_kJ_kg_K=cp,
            error_relative=cp/observed-1, ideal_frozen_cp_kJ_kg_K=frozen[0], residual_frozen_cp_kJ_kg_K=frozen[1],
            frozen_cp_kJ_kg_K=frozen[2], reaction_response_kJ_kg_K=cp-frozen[2],
            frozen_sum_error_kJ_kg_K=frozen[0]+frozen[1]-frozen[2],
            max_abs_residual=max(map(abs, result.residuals)), termination=result.message)
        for step, name in [(.1, 'coarse'), (.05, 'fine')]:
            enthalpies = []
            for T in [353.15-step, 353.15+step]:
                _, pr, rs = solution_state(T, alpha)
                (hs, _), (ns, _) = d.vrc.first_actions(model, pr, rs, hobs, [(0., 0., None)])[0]
                enthalpies.append(hs*ns)
            fd = (enthalpies[1]-enthalpies[0])/(2*step)/mass/1000
            row[name+'_enthalpy_cp_kJ_kg_K'] = fd; row[name+'_error_relative'] = abs(fd/cp-1)
        row['cp_numerically_verified'] = (row['fine_error_relative'] <= 1e-6
            and row['fine_error_relative'] <= row['coarse_error_relative']/2 and row['max_abs_residual'] <= 1e-9)
        solution.append(row)
        retain('solution-request-'+str(nominal_alpha)+'.json', req)
    table('solution-80C.csv', solution)
    provenance = dict(wall_s=time.monotonic()-started, engine_wheel_sha256=digest(wheel), wheel_path=str(wheel),
        installed_module=epcsaft.__file__, interpreter=sys.executable, producer_sha256=digest(__file__),
        original_source_commit='e80ef4e', parameter_files={k:dict(path=str(p.relative_to(ROOT)), sha256=digest(p)) for k,p in paths.items()},
        physical_ideal_calorics_sha256=digest(d.vrc.PHYSICAL_CALORICS),
        producers={str(p.relative_to(ROOT)):digest(p) for p in [Path(d.__file__), Path(d.s.__file__), Path(d.vrc.__file__), Path(d.vt.__file__)]},
        water_ideal_calorics='Existing NIST Shomate; extrapolated below 500 K; same fixed ideal contribution in both records.',
        density_translation_applied=False, tolerance_cp_relative=.03, nonworsening_slack_absolute_relative=1e-6,
        hilliard_pdf_sha256=digest(next(Path('/home/tnnrpolley21/Zotero/storage/LB7LUETY').glob('*.pdf'))),
        hilliard_locator='Appendix G.2, printed p.937 (PDF p.994); procedure §§4.6–4.8, pp.74–83; accuracy ±2%, reproducibility 1%.',
        solution_claim_limit='Own Amine producer, not authoritative absorber C5; no parameter change, attribution of physical cause, physical validation or EOS-impossibility claim.')
    retain('model-provenance.json', provenance)
    print(json.dumps(dict(water_rows=len(rows), failures=[r for r in rows if not r['evaluated']], solution=solution,
                         wall_s=provenance['wall_s']), indent=2))


if __name__ == '__main__':
    {'reference': reference, 'models': models}[sys.argv[1]]()
