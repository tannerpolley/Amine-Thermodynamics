"""Shared-ion and electrostatic sensitivities from issue #423."""
# ruff: noqa: E402 -- use the existing analysis producers from their script directories.
import math
import sys
from pathlib import Path

ANALYSES = Path(__file__).resolve().parents[2]
sys.path[:0] = [str(ANALYSES / p) for p in ('', 'mdea_mea_workflow/scripts', 'permittivity_temperature_loading')]
import shared_bicarbonate_417 as reuse
import carbonate_ions_282 as salt
import stripper_temperature_409 as bands
from dielectric_volume import verify_wheel
import born_diameter_sensitivity as born

f, r, s = reuse.f, reuse.r, reuse.s
BASE, RECORD = reuse.BASE, bands.F2
OUT = r.B / 'results/shared-ion-electrostatics-423' / reuse.SHA / bands.RECORD_SHA
NAMES = {'NaHCO3', 'Na2CO3', 'mixed'}
ION_PAIR = 'pair/bicarbonate-anion/water/k_ij'
REPLAY_LIMIT = 1e-10  # #341
HISTORICAL_SALT = '8b9609d4c8908d9397833988158f525c92dd28e3bcf7333f4c3b33c48db99069'
HISTORICAL_SALT_ENGINE = 'bc7794731e94be961d16028d3f4880c6718a93ad'


def write(path, value):
    s.write_json(OUT / path, value)


def absolute_shares(rows):
    ratios = [x['value'] / x['observed'] for x in rows if x['status'] == 'Available']
    return dict(n=len(ratios), status='available' if ratios else 'unavailable',
                geometric_mean=math.exp(math.fsum(map(math.log, ratios)) / len(ratios)) if ratios else None,
                aard_percent=100 * math.fsum(abs(v-1) for v in ratios) / len(ratios) if ratios else None,
                minimum=min(ratios, default=None), maximum=max(ratios, default=None))


def objective(label, mapping, reference):
    rows, ok, cost = r.replay(mapping)
    write(f'{label}/parameters.json', mapping)
    write(f'{label}/replay.json', dict(rows=rows, available=ok, cost=cost))
    assert ok and len(rows) == 307, label
    assert [(x['identity'], x['group'], x['row']) for x in rows] == [
        (x['identity'], x['group'], x['row']) for x in reference['rows']]
    retained = r.read(OUT / label / 'replay.json')
    assert math.isclose(cost, math.fsum(.5 * x['weighted_residual']**2 for x in retained['rows']), rel_tol=REPLAY_LIMIT)
    return cost, r.metrics(retained['rows'])


def salt_rows(document, names):
    return salt.predict(document, salt.carbonate_rows(r.epcsaft.Parameters.from_mapping(document), names))


def controls():
    receipt = r.read(salt.OUT / 'salt/summary.json')
    assert receipt['wheel_sha256'] == HISTORICAL_SALT
    assert f'`{HISTORICAL_SALT_ENGINE}`, wheel SHA-256 `{HISTORICAL_SALT}`' in (salt.OUT / 'README.md').read_text()
    assert s.sha256(RECORD) == bands.RECORD_SHA == born.RECORD_SHA
    fitted_laws = {k: (v['a0'], v['a1']) for k, v in receipt['result']['laws'].items()}
    assert all(v['t_ref'] == salt.T_SALT for v in receipt['result']['laws'].values())
    reuse.bind_wheel()
    s.verify_wheel()
    verify_wheel(s.installed_wheel(), reuse.SHA)
    mapping = s.parameter_mapping(RECORD)
    reference = r.read(reuse.paper.OUT / 'candidate/replay.json')
    cost, metrics = objective('P0', mapping, reference)
    control = r.read(reuse.OUT / 'control-readback.json')['MEA']
    assert f.a.relative(cost, control['replay_cost']) <= REPLAY_LIMIT
    new = r.read(OUT / 'P0/replay.json')
    reuse.compare_rows(new['rows'], reference['rows'], ('identity', 'group', 'status', 'observed', 'row'), REPLAY_LIMIT)
    parents = dict.fromkeys(salt.CARBONATE_IDS)
    shares = salt.pool_and_shares(mapping, parents=parents)
    historical = {x['id']: x for x in bands.rows(bands.EV / 'carbonate-share.csv')}
    write('P0/carbonate-share.json', dict(rows=shares, summary=absolute_shares(shares)))
    assert all(f.a.relative(x['value'], float(historical[x['state']]['predicted_share'])) <= REPLAY_LIMIT for x in shares)
    historical = r.read(BASE / 'salt-replay.json')
    document = salt.salt_document(fitted_laws)
    rows = {name: salt_rows(document, {name}) for name in ('NaHCO3', 'Na2CO3')}
    difference = max(f.a.relative(x['value'], y['value']) for name in rows
                     for x, y in zip(rows[name], historical['rows'][name], strict=True))
    scores = {name: salt.aard(values) for name, values in rows.items()}
    write('controls.json', dict(cost=cost, groups=metrics, carbonate=absolute_shares(shares),
                                historical_salt_wheel=HISTORICAL_SALT, historical_salt_engine=HISTORICAL_SALT_ENGINE,
                                salt=scores, salt_rows=rows,
                                salt_max_relative_difference=difference))
    assert difference <= 1e-8 and all(f.a.relative(x['aard_percent'], historical['scores'][k]['aard_percent']) <= 1e-8
                                      for k, x in scores.items())
    print('F2 and salt controls passed', cost, scores, flush=True)
    return mapping, reference, fitted_laws



def salt_cases(mapping, fitted):
    na, hco3, co3 = salt.NA, salt.HCO3, salt.CO3
    shared = {k: (s.parameter_values(mapping)[salt.LAWS[k]], 0.) for k in (hco3, co3)}
    assert shared == {hco3: (reuse.K0, 0.), co3: (-.25, 0.)}
    before = salt.salt_document({na: fitted[na]})
    after = salt.salt_document({na: fitted[na]}, RECORD)
    salt.set_pair(after, hco3, salt.W, next(p['coefficients'][0] for p in before['pairs']
                                            if {p['component_id_a'], p['component_id_b']} == {hco3, salt.W}))
    assert {k: v for k, v in after.items() if k != 'purpose'} == {k: v for k, v in before.items() if k != 'purpose'}
    sets = {'F2': shared, 'Held': {hco3: (0., 0.), co3: (-.25, 0.)},
            'salt-fitted': {k: fitted[k] for k in (hco3, co3)}}
    for sodium, law in {'N1': fitted[na], 'N2': (salt.HELD_A0[na], salt.NA_SLOPE)}.items():
        for label, laws in sets.items():
            document = salt.salt_document({na: law, **laws}, RECORD)
            rows = salt_rows(document, NAMES)
            for row in rows:
                row.setdefault('status', 'Unavailable')
                row.update(source_id=f"Peiper–Pitzer 1982 Table 6 / {row['T']} K / {row['salt']} / {row['m']} mol/kg",
                           observed_unit='dimensionless', pressure_Pa=salt.P_SALT)
            write(f'{sodium}/{label}/osmotic.json', rows)
            rows = r.read(OUT / sodium / label / 'osmotic.json')
            groups = []
            for name in sorted(NAMES):
                for T in (None, *sorted({x['T'] for x in rows})):
                    group = [x for x in rows if x['salt'] == name and (T is None or x['T'] == T)]
                    errors = [100 * (x['value'] / x['observed'] - 1) for x in group if x.get('status') == 'Available']
                    groups.append(dict(salt=name, temperature_K=T, total=len(group), available=len(errors),
                                       aard_percent=sum(map(abs, errors))/len(errors) if errors else None,
                                       max_percent=max(map(abs, errors), default=None),
                                       signed_bias_percent=sum(errors)/len(errors) if errors else None))
            assert [g['available'] for g in groups if g['temperature_K'] is None] == [45, 45, 39]
            write(f'{sodium}/{label}/summary.json', groups)
    print('Osmotic coefficient cases reduced', flush=True)
    return sets


def records(mapping):
    dea = ANALYSES / 'dea_transfer'
    amp = ANALYSES / 'amp_transfer/results/retransfer-412-f2-05e94210/slope-150'
    return {
        'monoethanolamine': (None, {'parameters': mapping}, RECORD),
        'diethanolamine': (dea / 'inputs/part-ii-346/f2-carbamate-413-route.json',
                          r.read(dea / 'results/refit-413/selection.json')['chosen']['parameters'],
                          dea / 'results/refit-413/selection.json'),
        'methyldiethanolamine': (reuse.DECLARATION, r.read(reuse.RESULTS / 'endpoint.json'), reuse.RESULTS / 'endpoint.json'),
        'aminomethylpropanol': (None, r.read(amp / 'parameters.json'), amp / 'parameters.json'),
    }


def diameter_records(mapping):
    from scipy.constants import Avogadro, elementary_charge, epsilon_0
    checks, cations = [], {}
    for amine, (_, point, path) in records(mapping).items():
        components = point['parameters']['components']
        values = {c['component_id']: {v['family']: v['value']['magnitude'] for v in c['coefficients']} for c in components}
        for c in components:
            ion = c['component_id']
            charge = c['fixed']['charge_number']['value']['magnitude']
            if not charge:
                continue
            d = values[ion]
            checks.append(dict(amine=amine, ion=ion, source=str(path.relative_to(r.ROOT)), source_sha256=s.sha256(path), **d))
            assert d['debye_huckel_diameter'] == d['segment_diameter'], (amine, ion, d)
            if d['segment_count'] == 1:
                assert d['packing_diameter'] == .88 * d['segment_diameter'], (amine, ion, d)
            else:
                assert c['fixed']['charged_molecule_ion']['value']['magnitude'] == 1 and 'packing_diameter' not in d
        ion, parent = values[f'protonated-{amine}'], values[amine]
        def volume(v):
            return v['segment_diameter'] * v['segment_count']**(1/3)
        assert ion['born_diameter'] == ion['segment_diameter']
        cations[amine] = dict(segments=ion['segment_count'], born_A=ion['born_diameter'],
                              volume_equivalent_A=volume(ion), parent_volume_equivalent_A=volume(parent))
    water = r.epcsaft.Mixture(r.epcsaft.Parameters.from_mapping(mapping))
    permittivity = water.state(298.15, P=101325., x={'water': 1.}, phase='liquid').bulk_relative_permittivity
    for d in cations.values():
        d.update(T_K=298.15, P_Pa=101325., water_permittivity=permittivity,
                 classical_continuum_Born_kJ_per_mol_at_d_Born=-elementary_charge**2 * Avogadro * (1-1/permittivity)
                 / (4*math.pi*epsilon_0*d['born_A']*1e-10) / 1000)
    amp = records(mapping)['aminomethylpropanol'][2]
    info = r.read(amp.with_name('conditional-uncertainty.json'))
    key = 'AMPH-segment-diameter'
    index = next(i for i, q in enumerate(info['coordinates']) if q['identity'] == key)
    cations['aminomethylpropanol'].update(bounds_A=info['coordinates'][index]['bounds'],
                                         active_bound=index in info['active_bounds'],
                                         conditional_standard_error_A=info['conditional_standard_error'][key])
    write('diameters.json', dict(ions=checks, cations=cations))
    return cations


def electrostatic_arms(mapping):
    mea = 'component/monoethanolamine/'
    keys = (mea+'dielectric_volume', mea+'dielectric_temperature',
            'component/carbon-dioxide/solvation_factor', mea+'solvation_factor')
    assert tuple(s.parameter_values(mapping)[k] for k in keys) == (.7309865858310542, 1019.0802597119892, 1., 1.)
    return {'P0': {}, 'P1': dict(zip(keys[:2], (.24645459482573953, 2436.43575418438), strict=True)),
            'M1': {keys[2]: 1.5}, 'M3': {keys[3]: 1.5}}


def band_comparisons(label, mapping):
    root = OUT / label
    record = root / 'parameters.json'
    if label == 'P0':
        record.write_bytes(RECORD.read_bytes())
    digest = s.sha256(record)
    f.OUT = OUT
    f.a.OUT = reuse.paper.OUT
    f.evidence(label, record, kim_pathways=label == 'P0')
    evidence = f.OUT / 'evidence' / label
    receipt = root / 'heat-replay.json'
    if not receipt.exists():
        old_record, old_runs = s.PARAMETERS, s.RUNS
        try:
            bands.replay(r.ROOT, record, digest, bands.EV if label == 'P0' else evidence, root,
                         control=label == 'P0', kim_2007=label != 'P0',
                         producer_sha='cb8d6cb26e64abc25b0c33c43577e4eaa676e8b2a4fea05f69358b3d501e3bbb')
        finally:
            s.PARAMETERS, s.RUNS = old_record, old_runs
    heat = r.read(receipt)
    assert heat['parameter_sha256'] == digest and heat['engine_wheel_sha256'] == reuse.SHA
    if label == 'P0':
        assert len(heat['reproduction']['rows']) == 28 and all(x['status'] == 'available' for x in heat['reproduction']['rows'])
    points = bands.points(record, digest, evidence, root)
    names = ('property', 'role', 'cohort', 'source', 'T_K', 'observed', 'predicted', 'unit')
    write(f'{label}/band-points.json', [dict(zip(names, p, strict=True)) for p in points])
    points = [tuple(p[k] for k in names) for p in r.read(root / 'band-points.json')]
    groups = []
    for prop, role, band in sorted({(p[0], p[1], bands.band(p[4])) for p in points}):
        group = [p for p in points if (p[0], p[1], bands.band(p[4])) == (prop, role, band)]
        groups.append(dict(property=prop, role=role, band=band, **bands.stats(group)))
    write(f'{label}/bands.json', groups)
    agreement = f.scores(label, mapping, root=evidence)
    if label == 'P0':
        historical = {(x['property'], x['role'], x['band']): x for x in bands.rows(bands.OUT / 'band-table.csv') if x['cohort'] == 'all'}
        differences = [dict(x, historical_n=int(ref['n']), historical_aard_percent=float(ref['AARD_percent']),
                            delta_percentage_points=x['AARD_percent']-float(ref['AARD_percent']))
                       for x in groups for ref in [historical[x['property'], x['role'], x['band']]]]
        write('P0/band-control-readback.json', differences)
        assert all(x['n'] == x['historical_n'] and round(x['AARD_percent'], 2) == round(x['historical_aard_percent'], 2)
                   for x in differences), differences
        retained = {x['dataset']: x for x in agreement}
        for key, n, aard in [('fitted: fitted CO2 partial pressure', 47, 11.64),
                             ('not fitted: six-source pressures', 112, 24.89), ('fitted: loaded density', 47, .15)]:
            assert retained[key]['n'] == n and round(retained[key]['aard_percent'], 2) == aard, retained[key]
        print('P0 Table S19 and #409 band checks passed', flush=True)
        write('P0/band-control-passed.json', dict(passed=True, record_sha256=digest, wheel_sha256=reuse.SHA))
    return agreement



def sodium_control(sets, fitted):
    na, co2, water = salt.NA, 'carbon-dioxide', salt.W
    spec = r.bind(s.parameter_mapping(RECORD))
    reactions = [x for x in next(iter(spec.problems.values())).reactions if x.name in ('R1', 'R2', 'R3')]
    laws = {rx.name: rx.correlation for rx in reactions}
    reactions = [r.eq.Reaction({k: v for k, v in rx.stoichiometry.items() if v}, name=rx.name,
                               correlation=rx.correlation, reference=rx.reference) for rx in reactions]
    assert (laws['R2'].temperature_min, laws['R2'].temperature_max) == (293.15, 393.15)
    T, mw = 298.15, salt.water_molar_mass()
    pks = [(q.a + q.b/T + q.c*math.log(T/q.reference_temperature) + q.d*T) for q in (laws['R2'], laws['R3'])]
    write('sodium-pK.json', dict(T_K=T, R2=-pks[0]/math.log(10), R3=-(pks[1]-math.log(mw))/math.log(10),
                                Peiper_Pitzer_R2=6.355, Peiper_Pitzer_R3=10.337))
    for label in ('F2', 'salt-fitted'):
        document = salt.salt_document({na: fitted[na], **sets[label]}, RECORD, reactive=True)
        salt.set_pair(document, co2, na, salt.k_node(document, f'pair/{co2}/{na}/k_ij', 0.,
                                                     dict(source_id='issue-423', locator='owner decision 5')))
        model = r.epcsaft.Mixture(r.epcsaft.Parameters.from_mapping(document))
        ratios = {k: .375 if k == na else .125 for k in model.component_ids if k != water}
        charges = {c['component_id']: c['fixed']['charge_number']['value']['magnitude'] for c in document['components']}
        assert sum(charges[i]*v for i, v in ratios.items()) == 0
        standard = dict(solvent=water, solute_molality_ratios=ratios, standard_molality_mol_per_kg=1.)
        neutral = r.eq.NeutralReference(**standard)
        phase = r.eq.Phase('L', kind='liquid', support=model.component_ids)
        rows = []
        for row in bands.rows(salt.INPUTS / 'peiper-pitzer-1982-table6.csv'):
            T, m, name = float(row['temperature_K']), float(row['nominal_molality']), row['salt']
            if m < .1 or name == 'mixed':
                continue
            row.update(unit='mol/kg water', P_Pa=salt.P_SALT, status='outside F2 R2 temperature range')
            rows.append(row)
            if not laws['R2'].temperature_min <= T <= laws['R2'].temperature_max:
                continue
            ion, k = (salt.HCO3, 1) if name == 'NaHCO3' else (salt.CO3, 2)
            problem = r.eq.Problem(T=T, P=salt.P_SALT, feed=r.eq.Amounts({water: 1/mw, na: k*m, ion: m}),
                                   reactions=reactions, phases=[phase], neutral_reference=neutral, row_tolerance=1e-10)
            result = r.eq.solve_equilibrium(model, problem)
            row.update(status='scored' if result.success and result.requested_tolerance_met else 'unavailable',
                       cause=result.message, residual_max=max(map(abs, result.residuals), default=None))
            if row['status'] == 'unavailable':
                write(f'N1/{label}/sodium-reactive.json', dict(standard=standard, CO2_Na_k=0., rows=rows))
                raise RuntimeError(row)
            x = dict(zip(model.component_ids, result.phase_mole_fractions(0), strict=True))
            for field, species in zip(('X2', 'Y', 'H2X', 'Z'), (salt.CO3, salt.HCO3, co2, salt.OH), strict=True):
                predicted = x[species] / (x[water] * mw)
                row[field+'_result'] = dict(predicted=predicted, residual=predicted-float(row[field]),
                                           within_print_rounding=abs(predicted-float(row[field])) <= .00005 if '.' in row[field] else None)
        assert sum(x['status'] == 'scored' for x in rows) == 36 and len(rows) == 60
        name = f'N1/{label}/sodium-reactive.json'
        write(name, dict(standard=standard, CO2_Na_k=0., rows=rows))
        rows = r.read(OUT / name)['rows']
        summary = []
        for T in (298.15, 308.15, 318.15):
            for key in ('X2', 'Y', 'H2X', 'Z'):
                data = [x[key+'_result'] for x in rows if float(x['temperature_K']) == T]
                scored = [x for x in data if x['within_print_rounding'] is not None]
                summary.append(dict(T_K=T, column=key, n=len(scored), within=sum(x['within_print_rounding'] for x in scored),
                                    max_absolute_residual_mol_kg=max(abs(x['residual']) for x in scored),
                                    signed_bias_mol_kg=sum(x['residual'] for x in scored)/len(scored)))
        write(f'N1/{label}/sodium-reactive-summary.json', summary)
        print(label, 'sodium reactive rows', 36, 'of', len(rows), flush=True)


def refit_arm(label, overrides, reference):
    import time
    f.OUT = OUT
    coordinates = r.read(BASE / 'F2/current/unpenalized/declaration.json')['declared']
    ties = {q['identity']: [t for t in q['targets'] if t[0] == 'born_diameter']
            for q in coordinates if any(t[0] == 'born_diameter' for t in q['targets'])}
    assert len(coordinates) == 11 and len(ties) == 2
    starts = {'previous': BASE / 'F1/parameters.json', 'current': f.a.RECORDS['candidate']}
    chosen = []
    for family, path in starts.items():
        source = s.parameter_mapping(path)
        historical = r.read(BASE / f'F2/{family}/unpenalized/declaration.json')['declared']
        values = s.parameter_values(source)
        assert all(values[q['identity']] == q['origin'] for q in historical)
        imposition = {q.replace('segment_diameter', 'born_diameter'): values[q] for q in ties}
        start = s.with_parameter_values(source, {**imposition, **overrides})
        name = f'{label}-refit/{family}'
        elapsed = OUT / name / 'readback.json'
        started = time.monotonic()
        endpoint, report = f.fit(name, start, f.LITERATURE, [q['identity'] for q in coordinates], ties)
        replay = r.read(OUT / name / 'replay.json') if endpoint is not None else {}
        write(f'{name}/readback.json', dict(status=report['status'] if report else 'unavailable',
                                           cost=replay.get('cost'), seconds=r.read(elapsed)['seconds'] if elapsed.exists() else time.monotonic()-started))
        if endpoint is not None and report['status'] == 'converged':
            assert all(s.parameter_values(endpoint)[q] == s.parameter_values(endpoint)[q.replace('segment_diameter','born_diameter')] for q in ties)
            assert len(report['declared']) == 11
            chosen.append((replay['cost'], family, endpoint, report))
    assert chosen, f'{label}: no converged fully replayable start'
    cost, family, endpoint, report = min(chosen, key=lambda x: x[0])
    replay_cost, groups = objective(f'{label}-refit', endpoint, reference)
    assert f.a.relative(cost, replay_cost) <= REPLAY_LIMIT
    write(f'{label}-refit/selected.json', dict(start=family, cost=cost, groups=groups,
                                               active_bounds=report['covariance']['active_bounds']))
    return endpoint


def permittivity(mapping, alternative):
    from dielectric_volume import composition
    from final_evidence import flash_problem
    from heat_evidence_170 import request
    from mea_water_permittivity import ROWS
    models = [r.epcsaft.Mixture(r.epcsaft.Parameters.from_mapping(m)) for m in (mapping, alternative)]
    values = [s.parameter_values(m) for m in (mapping, alternative)]
    rows = []
    samples = [dict(sample_id=x['sample_id'], T_K=298.15, MEA_mass_fraction=float(x['MEA_wt_percent'])/100,
                    loading=0., epsilon=float(x['epsilon_s']), source='Agieienko–Buchner')
               for x in bands.rows(ROWS)]
    samples += [dict(T_K=T, MEA_mass_fraction=w, loading=0., source='unloaded temperature comparison')
                for T in (313.15, 353.15, 393.15) for w in (.30, 1.)]
    samples += [x for x in bands.rows(ANALYSES / 'permittivity_temperature_loading/inputs/source-values.csv')
                if x['source'].startswith('Hajj')]
    for row in samples:
        T, weight, loading = (float(row[k]) for k in ('T_K', 'MEA_mass_fraction', 'loading'))
        states = []
        for model, record in zip(models, (mapping, alternative), strict=True):
            if not loading:
                x = composition(record, weight)
                state = model.state(T, P=101325., x=x, phase='liquid')
            else:
                problem = flash_problem(request(record, 313.15, .11), loading, T, 101325.,
                                        [r.eq.Phase('L', kind='liquid', support=model.component_ids)])
                solved = r.eq.solve_equilibrium(model, problem)
                if not solved.success or not solved.requested_tolerance_met:
                    states.append(dict(status='unavailable', cause=solved.message))
                    continue
                state = model.state(T, rho=solved.molar_densities[0], x=solved.phase_mole_fractions(0))
            states.append(dict(status='available', epsilon=state.bulk_relative_permittivity, density_mol_m3=state.molar_density,
                               residual=state.bulk_relative_permittivity-float(row['epsilon']) if row.get('epsilon') else None))
        row.update(P0=states[0], P1=states[1], unit='dimensionless')
        if not loading:
            def v(d, q):
                return math.fsum(x[i]*d[f'component/{i}/dielectric_{q}'] for i in x)
            terms = [v(d, 'volume')*(v(d, 'temperature')/T-1) for d in values]
            expected = terms[1]/terms[0]
            fixed = models[1].state(T, rho=states[0]['density_mol_m3'], x=x).bulk_relative_permittivity
            ratio = (fixed-1)/(states[0]['epsilon']-1)
            row.update(fixed_density_ratio=ratio, closed_form_ratio=expected)
        rows.append(row)
    write('P1/permittivity.json', rows)
    print('P1 permittivity checks', len(rows), flush=True)
    assert len(samples) == 50
    assert all(abs(x['fixed_density_ratio'] - x['closed_form_ratio']) <= REPLAY_LIMIT for x in rows if 'fixed_density_ratio' in x)
    assert all(abs(x['P0']['epsilon'] - x['P1']['epsilon']) <= REPLAY_LIMIT for x in rows if x.get('source') == 'Agieienko–Buchner')
    unloaded = [x['fixed_density_ratio'] for x in rows if x['source'] == 'unloaded temperature comparison'
                and x['MEA_mass_fraction'] == .30]
    assert all(abs(x-y) <= REPLAY_LIMIT for x, y in zip(unloaded, (1.00186697427, 1.00711755485, 1.01280262136), strict=True))


def share_case(label, mapping, parents=None):
    parents = dict.fromkeys(salt.CARBONATE_IDS) if parents is None else parents
    rows = salt.pool_and_shares(mapping, parents=parents)
    baseline = {x['state']: x for x in r.read(OUT / 'P0/carbonate-share.json')['rows']}
    for row in rows:
        accepted = row['status'] == 'Available'
        row.update(calc_over_obs=row['value']/row['observed'] if accepted else None,
                   residual=row['value']-row['observed'] if accepted else None, unit='dimensionless', source_locator='Jakobsen et al. 2005, Tables A1–A2 and 2')
    write(f'{label}/carbonate-share.json', dict(rows=rows))
    summary = {}
    for name, group in [('all', rows), ('without 018', [x for x in rows if not x['state'].endswith('_018')])]:
        scored = [x for x in group if x['status'] == 'Available' and baseline[x['state']]['status'] == 'Available']
        result = absolute_shares(group)
        base = absolute_shares([baseline[x['state']] for x in scored])
        matched = absolute_shares(scored)
        summary[name] = dict(result, matched_n=len(scored), F2_matched_geometric_mean=base['geometric_mean'],
                             matched_change=matched['geometric_mean']-base['geometric_mean'] if scored else None,
                             matched_factor=matched['geometric_mean']/base['geometric_mean'] if scored else None)
    write(f'{label}/carbonate-share.json', dict(rows=rows, summary=summary))
    return summary


def s1_admission(mapping):
    from final_evidence import phase_payload, stability
    from phase_diagnosis_255 import reduce_state
    spec = r.bind(mapping)
    inputs = r.read(salt.POOL_266)['problems']
    keys = [f'{p}:101325' for p in salt.CARBONATE_IDS]
    spec.spec['templates'].update({key: inputs[key] for key in keys})
    rows = {}
    for key in keys:
        parent = key.split(':')[0]
        problem = spec.problem(key, {})
        row = dict(T_K=problem.T, P_Pa=problem.P, feed=problem.feed.values, status='unavailable')
        rows[parent] = row
        try:
            result = r.eq.solve_equilibrium(spec.model, problem)
            row['final'] = phase_payload(spec.model, problem, result)
            assessment = reduce_state(dict(index=parent, classification='single-liquid parent', final=row['final']))
            row.update(admission=assessment, cause=result.message)
            if assessment['parent_admitted']:
                row.update(status='admitted', cause=None)
                check = stability(spec.model, problem, result)
                row['stability'] = check
                if any(t['resolved_descent'] for t in check['trials']):
                    row['stability_disposition'] = 'unconfirmed'
                else:
                    row['stability_disposition'] = 'no descent found' if check['completed'] else 'unresolved'
            elif result.success and result.requested_tolerance_met:
                row['cause'] = 'parent failed #396 closure, curvature or pressure-density admission'
        except r.epcsaft.EosError as error:
            row['cause'] = str(error)
    write('S1/parents.json', rows)
    assert sum(x['T_K'] == 293.15 and x['P_Pa'] == 101325. for x in rows.values()) == 5
    assert sum(x['T_K'] == 313.15 and x['P_Pa'] == 101325. for x in rows.values()) == 5
    return {k: None if row['status'] == 'admitted' else f"{row['status']}: {row['cause']}" for k, row in rows.items()}


def cation_replays(mapping, sizes):
    for amine, (declaration, point, _) in records(mapping).items():
        if declaration is None:
            continue
        key = f'component/protonated-{amine}/born_diameter'
        value = sizes[amine]['volume_equivalent_A']
        varied = dict(point, parameters=s.with_parameter_values(point['parameters'], {key: value}))
        assert s.with_parameter_values(varied['parameters'], {key: sizes[amine]['born_A']}) == point['parameters']
        for label, item in [('control', point), ('volume-equivalent', varied)]:
            route = reuse.Route(declaration, out=OUT / amine / label)
            values = s.parameter_values(item['parameters'])
            for ion in route.config['born_ties']:
                d = f'component/{ion}/born_diameter'
                assert values[d] == (value if label == 'volume-equivalent' and d == key else
                                     values[f'component/{ion}/segment_diameter']), (amine, label, ion)
            rows, ok, cost = route.replay(item)
            route.write('replay.json', dict(rows=rows, cost=cost, available=ok, born_A=s.parameter_values(item['parameters'])[key]))
            assert ok and math.isclose(cost, math.fsum(.5*x['weighted_residual']**2 for x in rows), rel_tol=REPLAY_LIMIT)
            if label == 'control':
                expected = 8.082968228315169 if amine == 'diethanolamine' else 564.4836961
                assert f.a.relative(cost, expected) <= 1e-8, (amine, cost, expected)
            route.reduce(item)




def molecular_co2(mapping):
    spec = r.bind(mapping)
    species = spec.model.component_ids.index('carbon-dioxide')
    identities = {}
    for row in spec.inputs['observations']['fitted']:
        for field in ('problem', 'initial', 'final', 'bubble'):
            if field in row:
                identities.setdefault(row[field], []).append(row['identity'])
    rows = []
    for name, sources in identities.items():
        problem = spec.problems[name]
        if not problem.reactions:
            rows.append(dict(state=name, sources=sources, status='carbon-free', liquid_x_CO2=0.))
            continue
        result = r.eq.solve_equilibrium(spec.model, problem)
        accepted = result.success and result.requested_tolerance_met
        rows.append(dict(state=name, sources=sources, status='available' if accepted else 'unavailable',
                         cause=result.message, liquid_x_CO2=result.phase_mole_fractions(0)[species] if accepted else None))
    highest = max((x for x in rows if x['liquid_x_CO2'] is not None), key=lambda x: x['liquid_x_CO2'])
    covered = {source for x in rows for source in x['sources']}
    write('M1/molecular-co2.json', dict(rows=rows, maximum=highest, fitted_rows_covered=len(covered)))
    assert len(covered) == 307


def search_classification(endpoint, search):
    from types import SimpleNamespace
    from part_ii import branch_counts
    path = r.ROOT / search['run'] / 'search'
    grid = r.read(path / 'grid.json.gz')['result']
    for row in grid:
        if r.descent(row):
            row.update(branch_counts(row))
    route = SimpleNamespace(bind=r.bind, states=lambda spec: sum(r.states(), []),
                            stability_row=r.stability_row, marks=lambda T, p: {})
    classification = reuse.witnesses(route, endpoint, grid)
    census = r.read(path / 'census.json')['result']['rows']
    classification['census_dispositions'] = [
        dict(index=x['index'], status=('unconfirmed' if x['index'] in search['census']['descent_indices']
             else 'unavailable' if not x['parent_admitted'] else 'unresolved' if not x['complete'] else 'no descent found'),
             cause=x['classification']) for x in census]
    return classification

def compare_refits(mappings, base):
    historical = r.read(BASE / 'F2/information.json')
    original = s.parameter_values(base)
    p0 = r.read(OUT / 'P0-refit/selected.json')['cost']
    tolerance = r.read(r.A6)['controls']['function_tolerance']
    summaries = {}
    for label, mapping in mappings.items():
        if not label.endswith('-refit'):
            continue
        record = r.read(OUT / label / 'selected.json')
        conditional = r.read(OUT / label / 'information.json')
        values = s.parameter_values(mapping)
        correlations = {}
        for row in historical['correlation_pairs_above_095']:
            names = row['parameters']
            free = conditional['free_coordinates']
            corr = conditional['conditional_correlation'][free.index(names[0])][free.index(names[1])] if all(p in free for p in names) else None
            correlations[' / '.join(names)] = dict(F2=row['correlation'], arm=corr)
        summaries[label] = dict(cost=record['cost'], delta_cost=record['cost']-p0,
                                tied_with_P0=abs(record['cost']-p0) <= tolerance*min(record['cost'], p0),
                                coordinates=[dict(identity=q['identity'], F2=original[q['identity']], arm=values[q['identity']])
                                             for q in historical['coordinates']],
                                active_bounds=record['active_bounds'], correlation_pairs=correlations)
    write('refit-comparison.json', dict(function_tolerance=tolerance, arms=summaries))

def main():
    base, reference, laws = controls()
    if not (OUT / 'P0/band-control-passed.json').exists():
        band_comparisons('P0', base)
    sizes = diameter_records(base)
    sets = salt_cases(base, laws)
    sodium_control(sets, laws)
    arms = electrostatic_arms(base)
    mappings = {label: s.with_parameter_values(base, change) for label, change in arms.items()}
    costs = {'P0': r.read(OUT/'controls.json')['cost']}
    for label, mapping in mappings.items():
        if label != 'P0':
            costs[label], _ = objective(label, mapping, reference)
    for arm, expected in [('M1', 151.332047084879), ('M3', 165.800264141939)]:
        assert f.a.relative(costs[arm], expected) <= REPLAY_LIMIT, (arm, costs[arm])
    trigger = 1e-6*costs['P0']
    write('arm-replay-costs.json', dict(trigger=trigger, arms={k: dict(cost=v, delta=v-costs['P0'],
          refit=k=='P0' or (k!='M1' and abs(v-costs['P0'])>trigger)) for k, v in costs.items()},
          exact_Figiel='pending tannerpolley/epcsaft#212'))
    permittivity(base, mappings['P1'])
    molecular_co2(mappings['M1'])
    reuse.RUN = r.B / 'results/runs/423' / reuse.SHA / bands.RECORD_SHA
    for label, overrides in arms.items():
        if label == 'P0' or (label != 'M1' and abs(costs[label]-costs['P0']) > trigger):
            endpoint = refit_arm(label, overrides, reference)
            arm = f'{label}-refit'
            mappings[arm] = endpoint
            path = OUT / arm / 'search.json'
            bicarbonate_k = s.parameter_values(endpoint)[ION_PAIR]
            if path.exists():
                assert r.ROOT / r.read(path)['run'] == reuse.run_key(arm, endpoint, bicarbonate_k)
            else:
                search = reuse.mea_search(arm, endpoint, bicarbonate_k)
                write(f'{arm}/search-classification.json', search_classification(endpoint, search))
                write(f'{arm}/search.json', search)
                print(arm, 'search seconds', search['seconds'], flush=True)
            if 'pilot' in sys.argv:
                return
            f.information(arm, endpoint, r.read(BASE/'F2/current/unpenalized/declaration.json')['declared'])
    compare_refits(mappings, base)
    for label, mapping in mappings.items():
        share_case(label, mapping)
        if label != 'P0':
            band_comparisons(label, mapping)
    from dielectric_volume import composition, scaled
    model = r.epcsaft.Mixture(r.epcsaft.Parameters.from_mapping(base))
    eps = model.state(313.15, P=101325., x=composition(base, .3), phase='liquid').bulk_relative_permittivity
    variations = {f'{ion}-{d:g}': s.with_parameter_values(base, {f'component/{ion}/born_diameter': d})
                  for ion, diameters in zip(born.IONS, ((2.5, 2.9296, 3., 3.5, 4.), (2.4422, 2.5, 3., 4., 4.953)), strict=True)
                  for d in diameters}
    variations.update({f'permittivity-{p:+g}pct': scaled(base, 1+(p/100.)*eps/(eps-1)) for p in (-5., 5.)})
    variations['S1'] = s.parameter_mapping(r.B / 'results/permittivity-refit/S1/parameters-0.json')
    reference_405 = r.read(r.B / 'results/born-diameter-sensitivity-405/summary.json')
    assert reference_405['wheel_sha256'] == reuse.SHA and reference_405['parameter_sha256'] == bands.RECORD_SHA
    bicarbonate_25 = next(x['cost'] for x in reference_405['cases'] if (x['ion'], x['diameter_A']) == (salt.HCO3, 2.5))
    checks = {f'{salt.HCO3}-2.5': bicarbonate_25, f'{salt.HCO3}-3.5': reference_405['bicarbonate_interior']['cost'],
              'S1': 151.787333918}
    for label, mapping in variations.items():
        cost, groups = objective(label, mapping, reference)
        if label in checks:
            assert f.a.relative(cost, checks[label]) <= REPLAY_LIMIT, (label, cost)
        write(f'{label}/metrics.json', dict(cost=cost, groups=groups))
        share_case(label, mapping, s1_admission(mapping) if label == 'S1' else None)
    cation_replays(base, sizes)


if __name__ == '__main__':
    main()
