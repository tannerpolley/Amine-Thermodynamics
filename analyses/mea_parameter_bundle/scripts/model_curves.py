"""Continuous model curves for the reported MEA parameter set (#202); fixed parameters, no fit. Each state uses the call behind
the retained point predictions (probe.evaluate on source_feed_request feeds, the assessment density path, unloaded_density_problem,
heat_items/predict, stage2_rows). Writes results/model-curves/; run with `nice -n 10`."""
import concurrent.futures as cf, csv, json, math, multiprocessing, os, sys
from pathlib import Path
import numpy as np
BUNDLE = Path(__file__).resolve().parents[1]
sys.path[:0] = [str(BUNDLE / 'calibration-misfit'), str(BUNDLE.parents[1] / 'src')]
import final_evidence as fe  # one BLAS/OpenMP thread; probe and the corrected packet
import shared_evaluation as s, fit_observations as fo, heat_evidence_170 as he, probe, epcsaft
from epcsaft import equilibrium as eq, regression as reg
OUT, RUNS, EVIDENCE = BUNDLE / 'results/model-curves', BUNDLE / 'results/runs/model-curves', BUNDLE / 'results/a7-paper-evidence'
SPEC = fo.load('analyses/mea_parameter_bundle/results/joint-recalibration-170/amendment-7/restricted-2/fit-spec.json')
MAPPING = s.parameter_mapping()
PARAMS, (PACKET, GROUPS) = epcsaft.Parameters.from_mapping(MAPPING), fe.observations()
MODEL = epcsaft.Mixture(PARAMS, thermochemistry=he.vrc.record())
fe.binding('Held', str(s.PARAMETERS))
first_start = s.attempt_plan  # this analysis keeps only the declared first start; a failure there stays unavailable
s.attempt_plan = lambda *state: first_start(*state)[:1]
TEMPLATE, HEAT_REQUEST, IDENTITY = PACKET[0]['request'], he.request(MAPPING, 313.15, .11), dict(parameter_sha256=s.sha256(s.PARAMETERS), engine_wheel_sha256=s.ENGINE_WHEEL_SHA256)
CARBON, NITROGEN, CHARGE = (1, 0, 0, 0, 1, 1, 1, 0, 0), (0, 1, 0, 1, 1, 0, 0, 0, 0), TEMPLATE['reaction_system']['charges']
SPECIES = {'MEA': (1,), 'MEAH+': (3,), 'MEACOO-': (4,), 'HCO3-': (5,), 'CO3^2-': (6,), 'CO2': (0,), 'MEA + MEAH+': (1, 3), 'HCO3- + CO3^2-': (5, 6)}
QUANTITIES = {'pressure': {'CO2 partial pressure': 'Pa'}, 'species': {k: 'mole fraction' for k in SPECIES}, 'heat': {'integral heat of absorption': 'kJ/mol CO2'},
              'density': {'liquid density': 'kg/m3'}, 'mea-water': {'bubble temperature': 'K', 'vapor water mole fraction': 'mole fraction'}}
IMBALANCES = ('max_scaled_residual', 'carbon_imbalance_relative', 'nitrogen_imbalance_relative', 'charge_imbalance_relative')
# Check 1 references: each isotherm and Wagner, each species panel (both aggregates, 31 wt%), Matin's MEA and MEAH+,
# each heat condition, both density pressures and zero loading, and both Cai isobars.
REFERENCES = {'canonical:vle_obs_0163', 'canonical:vle_obs_0055', 'canonical:vle_obs_0066', 'canonical:vle_obs_0217', 'canonical:vle_obs_0255', 'Wagner2013:csv-row-37', 'Bottinger2008_state_030',
              'Bottinger2008_state_049', 'Bottinger2008_state_058', 'Bottinger2008_state_067', 'Matin2012_state_001', 'vinjarapu2024_source_table4_01', '10.1021/je2002946/table5/T322.5K/p0.51MPa/row01',
              '10.1021/je2002946/table5/T322.5K/p1.03MPa/row01', 'Han2012_density_40C_alpha0.10', 'Han2012_density_100C_alpha0.10', 'Amundsen2009_state_002', 'cai1996_10133_008', 'cai1996_06666_008'}
CAI = [r for r in fo.load(SPEC['stage2_rows_path'])['F1'] if r['id'].startswith('cai')]
# Pressure: geometric below 0.2 (log pressure nearly linear in log loading), 0.01 steps above (check 3 refinement).
GRIDS = {'pressure': [dict(T=T, w=.3, a=a) for T in (313.15, 333.15, 353.15, 373.15, 393.15) for a in [*np.geomspace(.003, .2, 24), *np.linspace(.2, .69, 50)[1:]]],
         'species': [dict(T=T, w=.31 if T > 350 else .3, P=101325., a=a) for T in (293.15, 313.15, 333.15, 353.15) for a in [*np.linspace(0, .55, 32), *np.linspace(.55, .6, 4)[1:]]],  # #205: to 0.6
         'heat': [dict(T=T, P=P, a=a) for T, P in ((313.15, 1734000.), (322.5, 510000.), (322.5, 1030000.)) for a in np.linspace(.01, .55, 28)],
         'density': [dict(T=T, w=.3, P=7e5 if T > 364 else 1e5, a=a) for T in (298.15, 313.15, 333.15, 353.15, 373.15, 393.15) for a in np.linspace(0, .56, 22)],
         'mea-water': [dict(P=P, x=x) for P in (101330., 66660.) for x in np.linspace(*(f(r['feed']['monoethanolamine'] for r in CAI if r['P_Pa'] == P) for f in (min, max)), 32)]}

def closure(n, feed):
    """Largest carbon, nitrogen and charge imbalance of solved amounts n against the analytical feed."""
    dot = lambda a, v: math.fsum(i * j for i, j in zip(a, v))
    carbon, nitrogen = dot(CARBON, feed), dot(NITROGEN, feed)  # zero-carbon states are scaled by nitrogen
    return dict(carbon_imbalance_relative=abs(dot(CARBON, n) - carbon) / (carbon or nitrogen),
                nitrogen_imbalance_relative=abs(dot(NITROGEN, n) - nitrogen) / nitrogen, charge_imbalance_relative=abs(dot(CHARGE, n)) / nitrogen)

def solved(problem, model=MODEL, feed=None):
    result = eq.solve_equilibrium(model, problem)
    if not result.success:
        raise RuntimeError(result.message)
    n = [math.fsum(result.amounts[i] * result.mole_fractions[9 * i + c] for i in range(result.phase_count)) for c in range(9)]  # full-width phase fractions
    values = problem.feed.values  # a component dict, or a list in component order for a compiled problem
    feed = feed or (values if isinstance(values, list) else [values.get(c, 0.) for c in s.COMPONENT_IDS])
    return result, dict(max_scaled_residual=max(map(abs, result.residuals)), requested_tolerance_met=result.requested_tolerance_met, start='direct', **closure(n, feed))

def evaluated(T, a, w, species):
    """probe.evaluate's call (selected record, no anchors) on a source_feed_request feed, keeping its attempt record."""
    kind = [o for o in PACKET if (o['identity'].startswith('Bottinger') if species else o['request']['pressure']['role'] == 'solved')]
    template = min(kind, key=lambda o: (abs(round(o['request']['temperature']['value'] - T)), abs(o['request']['reaction_system']['feed_amounts_mol'][0] - a)))
    request = s.source_feed_request(template['request'], dict(source_key='model-curve', CO2_loading=a, MEA_weight_fraction=w, temperature_reported_C=T - 273.15))
    record = s.evaluate_state(probe._base_model(), request, probe.reactions(), 'model-curve', [], budget_s=90, model_fingerprint=probe._BASE['fingerprint'])
    if record['status'] != 'evaluated':
        raise RuntimeError(f"{record['failure_code']}: {record['failure_diagnostic']}")
    n = [math.fsum(p['amount_mol'] * dict(zip(p['support'], p['mole_fractions'])).get(c, 0.) for p in record['phases']) for c in s.COMPONENT_IDS]
    evidence = dict(record['evidence'])
    return record, dict(max_scaled_residual=max(map(abs, evidence['residuals'])), requested_tolerance_met=evidence['requested_tolerance_met'], start=record['attempts'][-1]['kind'],
                        **closure(n, request['reaction_system']['analytical_feed_contract']['neutral_analytical_amounts_mol']))

def bubble(state):
    record, diagnostics = evaluated(state['T'], state['a'], state['w'], False)
    return {'CO2 partial pressure': record['predictions']['co2-partial-pressure']}, dict(diagnostics, pressure_Pa=record['predictions']['system-pressure'])

def bubble_pressure(T, a, w):  # total bubble pressure of the same analytical feed; zero carbon adds an incipient MEA-water vapor
    if a:
        return bubble(dict(T=T, a=a, w=w))[1]['pressure_Pa']
    problem = s.unloaded_density_problem(MAPPING, TEMPLATE, dict(T_K=T, P_Pa=1e4, MEA_weight_fraction=w))
    problem.phases = [problem.phases[0], eq.Phase('V', kind='vapor', support=('monoethanolamine', 'water'), amount=eq.Pinned(0.), composition_guess=(.01, .99))]
    problem.P = eq.Free(1e4)
    return solved(problem)[0].pressure

def species(state):
    if state['a']:
        record, diagnostics = evaluated(state['T'], state['a'], state['w'], True)
        x = dict(zip(record['phases'][0]['support'], record['phases'][0]['mole_fractions']))
    else:
        result, diagnostics = solved(s.unloaded_density_problem(MAPPING, TEMPLATE, dict(T_K=state['T'], P_Pa=state['P'], MEA_weight_fraction=state['w'])))
        x = dict(zip(s.COMPONENT_IDS, result.mole_fractions[:9]))
    return {k: math.fsum(x[s.COMPONENT_IDS[i]] for i in v) for k, v in SPECIES.items()}, diagnostics

def density(state):
    T, a, w, P = (state[k] for k in 'TawP')
    if a:
        request = s.source_feed_request(he.request(MAPPING, T, a, density=True), dict(source_key='Amundsen2009', CO2_loading=a, temperature_reported_C=T - 273.15, MEA_weight_fraction=w))
        problem = s._problem_from_request(s.corrected_request(request, s.reaction_values(MAPPING)))
        problem.P = P
    else:
        problem = s.unloaded_density_problem(MAPPING, TEMPLATE, dict(T_K=T, P_Pa=P, MEA_weight_fraction=w))
    value = fo.predict(MAPPING, [reg.observation(PARAMS, 'phase_density', problem, observed=1000., form='difference', scale=1., phase=problem.phases[0].name, mass_basis=True)])[0].value
    # source_feed_request seeds balanced extents; balances are against its analytical amounts
    return {'liquid density': value}, solved(problem, feed=a and request['reaction_system']['analytical_feed_contract']['neutral_analytical_amounts_mol'])[1]

def heat(state):
    row = dict(temperature_K=state['T'], system_pressure_Pa=state['P'], alpha_final=state['a'], observed_addition_enthalpy_J_per_mol_CO2=0., uH_J_per_mol_CO2=1000.)
    item = fo.heat_items(MAPPING, PARAMS, [row], HEAT_REQUEST)[0]
    both = [solved(p)[1] for p in (item.problem, item.final_problem)]  # zero-loading and loaded liquids
    worst = dict(both[1], **{k: max(d[k] for d in both) for k in IMBALANCES}, requested_tolerance_met=all(d['requested_tolerance_met'] for d in both))
    return {'integral heat of absorption': fo.predict(MAPPING, [item])[0].value / 1000}, worst

def mea_water(state):  # neutral MEA-water bubble state at fixed pressure through stage2_rows; a Cai declaration passes unchanged
    rows = [r for r in CAI if r['state_id'] == state.get('declared')]
    if not rows:  # temperature and vapor starts interpolated from the Cai rows of this isobar
        cai = sorted((r['feed']['monoethanolamine'], r['T_K'], r['vapor_guess']['water']) for r in CAI if r['P_Pa'] == state['P'])
        guess, y = (float(np.interp(state['x'], [c[0] for c in cai], [c[i] for c in cai])) for i in (1, 2))
        base = dict(state_id='curve', T_K=guess, P_Pa=state['P'], feed=dict(water=1 - state['x'], monoethanolamine=state['x']), vapor_guess=dict(water=y, monoethanolamine=1 - y), weight=1, form='difference')
        rows = [dict(base, id='T', quantity='temperature', observed=guess, scale=1.), dict(base, id='y', quantity='mole_fraction', observed=y, scale=.01)]
    s.write_json(path := RUNS / f'mea-water-{os.getpid()}.json', {'F1': rows})
    params, items = fo.stage2_rows(dict(SPEC, stage2_rows_path=str(path)), MAPPING, SPEC['cases'][0])
    model, values = epcsaft.Mixture(params, thermochemistry=he.vrc.record()), {}
    for row, item, _ in items:
        if (value := reg.predict(model, item)).status.name != 'Available':
            raise RuntimeError(value.message)
        values['bubble temperature' if row['quantity'] == 'temperature' else 'vapor water mole fraction'] = value.value
    result, diagnostics = solved(items[0][2], model)
    return values, dict(diagnostics, temperature_K=result.temperature)

def run(family, state):
    s.RUNS = RUNS / f'worker-{os.getpid()}'
    curve = f"{state['P']/1e3:g} kPa" if family == 'mea-water' else f"{state['T']:g} K" + (f", {state['P']/1e6:g} MPa" if family == 'heat' else '')
    row = {k: v for k, v in dict(curve=curve, sampling=state.get('sampling', 'grid'), temperature_K=state.get('T'), pressure_Pa=state.get('P'), analytical_loading=state.get('a'),
                                  mea_mass_fraction=state.get('w'), liquid_mea_mole_fraction=state.get('x')).items() if v is not None}
    try:
        values, updates = {'pressure': bubble, 'species': species, 'heat': heat, 'density': density, 'mea-water': mea_water}[family](state)
        row.update(updates, status='available', cause='')
        if max(row[k] for k in IMBALANCES) > 1e-10 or not row['requested_tolerance_met']:
            row.update(status='unavailable', cause='scaled residual or balance above 1e-10')
    except Exception as exc:
        values, row = {}, dict(row, status='unavailable', cause=f'{type(exc).__name__}: {exc}'[:300])
    if family in ('species', 'density'):  # imposed single liquid against the total bubble pressure of the same feed
        try:
            row.update(bubble_pressure_Pa=(total := bubble_pressure(state['T'], state['a'], state['w'])), below_bubble_pressure=state['P'] < total)
        except Exception as exc:
            row.update(below_bubble_pressure='unavailable', bubble_pressure_cause=f'{type(exc).__name__}: {exc}'[:300])
    return [dict(row, quantity=q, value=values.get(q), unit=u, **IDENTITY) for q, u in QUANTITIES[family].items()]

def references(families):  # check 1: the curve calls at each reference's source declaration against its retained prediction
    E = {n: list(csv.DictReader((EVIDENCE / f'{n}.csv').open())) for n in ('canonical-pressure', 'wagner-pressure', 'species-figure-data', 'heat', 'density', 'fitted-rows')}
    o = {o['identity']: o for o in PACKET + GROUPS['canonical'] + GROUPS['wagner']}
    m = {r['state_id']: dict(MEA_weight_fraction=r['mea_mass_fraction'], CO2_loading=r['co2_loading_mol_per_mol_mea'])
         for r in csv.DictReader((BUNDLE.parents[1] / 'data/reference/MEA/manifests/speciation_target_membership.csv').open())}
    c = lambda i: o[i]['request']['reaction_system'].get('analytical_feed_contract', {}).get('source_coordinates') or m[i]  # Matin requests carry no feed contract
    declared = lambda i, **k: dict(T=o[i]['request']['temperature']['value'], w=float(c(i)['MEA_weight_fraction']), a=float(c(i)['CO2_loading']), **k)
    cases = [('pressure', declared(r['identity']), 'CO2 partial pressure', r['identity'], r['predicted']) for r in E['canonical-pressure'] + E['wagner-pressure'] if r['identity'] in REFERENCES]
    cases += [('species', declared(r['identity'], P=101325.), {'HCO3-': 'HCO3- + CO3^2-'}.get(r['species'], r['species']), r['target'], r['predicted'])
              for r in {r['target']: r for r in E['species-figure-data']}.values() if r['identity'] in REFERENCES]
    cases += [('heat', dict(T=float(r['T_K']), P=float(r['P_Pa']), a=float(r['loading'])), 'integral heat of absorption', r['id'], r['predicted_kJ_mol']) for r in E['heat'] if r['id'] in REFERENCES]
    cases += [('density', dict(T=float(r['T_K']), w=float(r['mea_mass_fraction']), P=float(r['P_Pa']), a=float(r['loading'])), 'liquid density', r['id'], r['predicted_kg_m3'])
              for r in E['density'] if r['id'] in REFERENCES]
    cases += [('mea-water', dict(declared=i, P=next(x['P_Pa'] for x in CAI if x['state_id'] == i)), 'bubble temperature' if q == 'temperature' else 'vapor water mole fraction', r['id'], r['predicted'])
              for r in E['fitted-rows'] for i, q in [r['id'].rpartition('-')[::2]] if i in REFERENCES]
    out = []
    for family, state, quantity, identity, retained in (c for c in cases if c[0] in families):  # heat: absolute kJ/mol CO2; otherwise relative
        new, retained = next(r['value'] for r in run(family, state) if r['quantity'] == quantity), float(retained)
        difference = math.inf if new is None else abs(new - retained) / (1. if family == 'heat' else max(abs(new), abs(retained), 1e-300))
        out.append(dict(family=family, identity=identity, quantity=quantity, retained=retained, replayed=new, difference=difference, passed=difference <= (1e-3 if family == 'heat' else 1e-6)))
    return out

def delta(new, old):  # #203 relative difference; equal within 1e-300 counts as zero
    new, old = float(new), float(old)
    return 0. if abs(new - old) <= 1e-300 else abs(new - old) / max(abs(new), abs(old))

def main(families=tuple(GRIDS)):  # a family subset refreshes only its own summary entries
    workers = max(1, min(os.cpu_count(), int(next(x for x in open('/proc/meminfo') if x.startswith('MemAvailable')).split()[1]) // 1_000_000))  # ~1 GB per worker
    summary = dict(IDENTITY, engine_commit=s.ENGINE_COMMIT, workers=workers, check_1_reference_replay=references(families), families={})
    tables = {}  # written only after every requested family reproduces
    with cf.ProcessPoolExecutor(workers, mp_context=multiprocessing.get_context('fork')) as pool:
        for family, states in ((f, GRIDS[f]) for f in families):
            axis = 'liquid_mea_mole_fraction' if family == 'mea-water' else 'analytical_loading'
            rows, picks = [r for rr in pool.map(run, [family] * len(states), states) for r in rr], []
            # retained grid rows must reproduce (#203 gate) before the family file is replaced
            old = {(r['curve'], float(r[axis]), r['quantity']): r for r in csv.DictReader(path.open()) if r['sampling'] == 'grid'} if (path := OUT / f'{family}.csv').exists() else {}
            pairs = [(r, old[k]) for r in rows if r['sampling'] == 'grid' and (k := (r['curve'], r[axis], r['quantity'])) in old]
            d = [(delta(r[k], o[k]), r['curve'], r[axis], r['quantity'], k) for r, o in pairs for k in ('value', 'bubble_pressure_Pa') if o.get(k) and r.get(k) is not None]
            worst = max(d, default=(0.,))
            reproduction = dict(retained_rows=len(old), compared_rows=len(pairs), worst_delta=worst[0],
                                passed=len(pairs) == len(old) and all(r['status'] == o['status'] for r, o in pairs) and worst[0] <= 1e-10)
            if not reproduction['passed']:  # nothing has been written yet: every retained CSV and summary.json stay as they were
                sys.exit(f"{family}: retained grid rows do not reproduce; no file replaced. {reproduction}; worst comparison (curve, {axis}, quantity, column): {worst[1:]}; "
                         f"status changes: {[(r['curve'], r[axis], r['quantity'], o['status'], r['status']) for r, o in pairs if r['status'] != o['status']]}")
            for key in dict.fromkeys((r['curve'], r['quantity']) for r in rows):  # check 3: largest absolute second differences
                part = sorted((r for r in rows if (r['curve'], r['quantity']) == key and r['status'] == 'available'), key=lambda r: r[axis])
                y = [math.log(r['value']) if family == 'pressure' else r['value'] for r in part]
                d2 = [0., *(abs(y[i - 1] - 2 * y[i] + y[i + 1]) for i in range(1, len(y) - 1)), 0.]
                picks += [(part[i], part[i + 1]) for i in sorted(range(len(y) - 1), key=lambda i: -max(d2[i], d2[i + 1]))[:3]]
            mids = {(lo['curve'], (lo[axis] + hi[axis]) / 2): dict(T=lo.get('temperature_K'), w=lo.get('mea_mass_fraction'), P=lo['pressure_Pa'], sampling='midpoint',
                                                                   **{'x' if family == 'mea-water' else 'a': (lo[axis] + hi[axis]) / 2}) for lo, hi in picks}
            rows += [r for rr in pool.map(run, [family] * len(mids), mids.values()) for r in rr]
            sampling = []
            for lo, hi in picks:  # issue #202 check 3 tolerances, in the quantity's unit
                direct = next(r for r in rows if r['sampling'] == 'midpoint' and (r['curve'], r['quantity']) == (lo['curve'], lo['quantity']) and r[axis] == (lo[axis] + hi[axis]) / 2)
                interpolated = math.sqrt(lo['value'] * hi['value']) if family == 'pressure' else (lo['value'] + hi['value']) / 2
                value = direct['value']
                tolerance = {'pressure': .01 * (value or 0), 'species': max(.01 * (value or 0), 1e-4)}.get(family, .005 if 'vapor' in lo['quantity'] else .2)
                sampling.append(dict(curve=lo['curve'], quantity=lo['quantity'], interval=[lo[axis], hi[axis]], direct=value, interpolated=interpolated,
                                     tolerance=tolerance, passed=value is not None and abs(value - interpolated) <= tolerance))
            tables[family], curves = rows, {}
            for c in dict.fromkeys(r['curve'] for r in rows):
                states = list({(r[axis], r['sampling']): r for r in rows if r['curve'] == c}.values())
                fine = [r for r in states if r['status'] == 'available']
                passed = all(x['passed'] for x in sampling + summary['check_1_reference_replay'] if x.get('curve', c) == c and x.get('family', family) == family)
                curves[c] = dict(states=len(states), failed=len(states) - len(fine), causes=sorted({r['cause'] for r in states if r['status'] != 'available'}),
                                 **{k: max(r[k] for r in fine) for k in IMBALANCES}, checks_1_and_3_passed=passed, usable=passed and len(fine) >= .9 * len(states))
            summary['families'][family] = dict(engine_commit=s.ENGINE_COMMIT, engine_wheel_sha256=s.ENGINE_WHEEL_SHA256, workers=workers, csv_sha256=None,
                                               curves=curves, check_3_sampling=sampling, retained_grid_reproduction=reproduction)
    for family, rows in tables.items():
        he.table(OUT / f'{family}.csv', rows)
        summary['families'][family]['csv_sha256'] = s.sha256(OUT / f'{family}.csv')
    value = {(float(r['temperature_K']), float(r['analytical_loading'])): float(r['value']) for r in csv.DictReader((OUT / 'pressure.csv').open()) if r['status'] == 'available' and r['sampling'] == 'grid'}
    Ts, alphas = sorted({k[0] for k in value}), sorted({k[1] for k in value})  # exceptions: [T, loading, next loading] and [loading, T, next T]
    summary['check_4_physical_direction'] = dict(loading=[[T, a, b] for T in Ts for a, b in zip(alphas, alphas[1:]) if (T, a) in value and (T, b) in value and value[T, b] <= value[T, a]],
        temperature=[[a, T, U] for a in alphas for T, U in zip(Ts, Ts[1:]) if (T, a) in value and (U, a) in value and value[U, a] <= value[T, a]])
    if set(families) != set(GRIDS):  # the other families keep their retained record and run identity
        old = json.loads((OUT / 'summary.json').read_text())
        summary = dict(old, families={**old['families'], **summary['families']}, check_4_physical_direction=summary['check_4_physical_direction'],
                       check_1_reference_replay=[r for r in old['check_1_reference_replay'] if r['family'] not in families] + summary['check_1_reference_replay'])
    s.write_json(OUT / 'summary.json', summary)

if __name__ == '__main__':
    main(sys.argv[1:] or tuple(GRIDS))
