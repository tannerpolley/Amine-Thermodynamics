"""Issue 284: unloaded 30 wt% MEA heat-capacity slope split into pure water, pure MEA and excess, then (stage 2) one
added MEA-water k_ij temperature-law coefficient fitted with the #255 driver; no adoption.

Stage 1: c_p^E = c_p - sum_i w_i c_p,i (mass basis, kJ/kg/K). Over 313.15 -> 353.15 K each part's slope error e_k is
model change minus reference change, and e_mix = w_W e_W + w_MEA e_MEA + e_E. References: IAPWS-95 water (chemicals
1.5.2), pure MEA from Maham 1997 (primary) and Chiu 1999, mixture from Hilliard 2008 and Concepcion 2023 (#264 sources).
Stage 2: k_ij(T) = a0 + a_p (T - 313.15)^p + s (1/T - 1/313.15), p = 1 or 2 chosen by bound-scaled sensitivity.
Commands (repository root):
  reference  -- ePC-SAFT .venv (chemicals 1.5.2): IAPWS-95 water table
  stage1 | shares                                -- worktree .venv, agent-heavy (retained stage 1: bc779473 wheel 8b9609d4)
  qualify0 | qualify2 | fit2 <final|candidate> | assess2 <run> | select2 | grid2 | present
                                                 -- stage 2 on the 391dfe5d wheel (0962e21d, #291), worktree only
"""
import copy
import csv
import hashlib
import json
import math
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[3]
B = ROOT / 'analyses/mea_parameter_bundle'
OUT = B / 'results/cp-slope-284'
M, W, C = 'monoethanolamine', 'water', 'carbon-dioxide'
GRID = [round(298.15 + 5 * i, 2) for i in range(20)]  # 298.15 ... 393.15 K
WATER_GRIDS = [(101325., [T for T in GRID if T <= 368.15]), (300000., GRID)]
T1, T2 = 313.15, 353.15
MIXTURES = {'Hilliard2008': dict(molality=7.0), 'Concepcion2023': dict(mass_fraction=.2997)}
H = (.05, .025)  # centred-difference steps for the residual-Cv closure (#264 calculate.py lines 139-147)


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def table(path, rows):
    with Path(path).open('w', newline='') as stream:
        writer = csv.DictWriter(stream, list(dict.fromkeys(k for r in rows for k in r)), lineterminator='\n')
        writer.writeheader()
        writer.writerows(rows)


def reference():
    from chemicals import iapws
    import importlib.metadata
    assert importlib.metadata.version('chemicals') == '1.5.2'
    assert sha(iapws.__file__) == 'da5db0ea54148b11c1ed4c13045aa111bf180bce89272fea65ca6746645a2e51'  # as density-cp-160
    rows = [dict(T_K=T, P_Pa=P, cp_kJ_kg_K=iapws.iapws95_properties(T, P)[5] / 1000, rho_kg_m3=iapws.iapws95_properties(T, P)[0])
            for P, temperatures in WATER_GRIDS for T in temperatures]
    table(OUT / 'iapws95-water.csv', rows)
    (OUT / 'iapws95-provenance.json').write_text(json.dumps(dict(
        source='IAPWS R6-95(2018)', zotero_key='Y3FU9CXJ', implementation='chemicals 1.5.2', module_sha256=sha(iapws.__file__),
        interpreter=sys.executable, producer_sha256=sha(__file__), table_sha256=sha(OUT / 'iapws95-water.csv'),
        note='Same implementation and module bytes as results/density-cp-160/cp-124-assessment/reference-provenance.json'), indent=1) + '\n')


# ---------------------------------------------------------------- stage 1 (Engine)

def residual_cv_parts(model, T, rho, x=None):
    """Per-term residual Cv, -R(2T da/dT + T^2 d2a/dT2) at fixed density, for both steps (J/mol/K)."""
    import epcsaft
    sys.path.insert(0, str(B / 'heat-capacity-264'))
    import calculate as hc
    kw = {} if x is None else dict(x=x)
    out = []
    for h in H:
        states = [model.state(T + k * h, rho=rho, **kw) for k in (-1, 0, 1)]
        out.append({t: -epcsaft.GAS_CONSTANT_J_PER_MOL_K * (2 * T * (getattr(states[2], t) - getattr(states[0], t)) / (2 * h)
                    + T**2 * (getattr(states[2], t) - 2 * getattr(states[1], t) + getattr(states[0], t)) / h**2) for t in hc.TERMS})
    return out


def pure_rows(cid, model, molar_mass, grids):
    rows = []
    for P, temperatures in grids:
        for T in temperatures:
            st = model.state(T, P=P, phase='liquid', derived_properties=True)
            assert st.pressure_density_derivative > 0, (cid, T, P)
            coarse, fine = residual_cv_parts(model, T, st.molar_density)
            closure = sum(fine.values()) - st.residual_isochoric_heat_capacity
            f = 1 / molar_mass / 1000
            rows.append(dict(component=cid, T_K=T, P_Pa=P, cp_kJ_kg_K=st.total_isobaric_heat_capacity * f,
                             ideal_kJ_kg_K=st.ideal_isobaric_heat_capacity * f, residual_cp_kJ_kg_K=st.residual_isobaric_heat_capacity * f,
                             residual_cv_kJ_kg_K=st.residual_isochoric_heat_capacity * f,
                             **{f'residual_cv_{t}_kJ_kg_K': v * f for t, v in fine.items()},
                             closure_J_mol_K=closure, closure_bound_J_mol_K=1e-4 + 1e-4 * abs(st.residual_isochoric_heat_capacity),
                             refinement_J_mol_K=max(abs(fine[t] - coarse[t]) for t in fine), rho_kg_m3=st.molar_density * molar_mass,
                             density_termination=str(st.density_convergence)))
            print(cid, T, P, rows[-1]['cp_kJ_kg_K'], flush=True)
    return rows


def mixture_rows(spec, broad, masses, source, basis):
    """#264's unloaded Cp row (trace CO2 1e-6 per MEA, 101325 Pa) on the 5 K grid at one source's composition."""
    import copy
    from epcsaft import equilibrium as eq
    import calculate as hc
    water = 1 / (basis['molality'] * masses[W]) if 'molality' in basis else masses[M] * (1 - basis['mass_fraction']) / basis['mass_fraction'] / masses[W]
    template = next(r for r in broad if r['identity'] == 'Hilliard2008-313.15-0.0')
    feed = {M: 1., W: water, C: 1e-6}
    rows = []
    for T in GRID:
        problem = copy.copy(spec.problems[template['problem']])
        problem.T, problem.P, problem.feed = T, 101325., eq.Amounts(feed)
        name = f'{source}-grid-{T}'
        spec.problems[name] = problem
        r = copy.deepcopy(template)
        r.update(identity=name, problem=name, row=dict(template['row'], source=source, T_K=str(T), loading='0', cp_kJ_kg_K='0'))
        r['feed_mass_kg'], r['feed_amount_mol'] = sum(n * masses[c] for c, n in feed.items()), sum(feed.values())
        rows.append(r)
    out = hc.decompose(spec, rows, spec._intervals)
    w = masses[M] / (masses[M] + water * masses[W])
    for o in out:
        o.pop('observed_kJ_kg_K')
        o['MEA_mass_fraction'] = w
    return out


def driver():
    """The #255 driver bound to the 391dfe5d wheel (#291); the repository's Engine pin is unchanged."""
    sys.path[:0] = [str(B / 'scripts'), str(B / 'heat-capacity-264')]
    import stable_refit_255 as r
    import calculate as hc
    r.COMMIT, r.SHA = COMMIT2, SHA2
    r.WHEEL = ROOT / f'build/engine-wheels/main-{COMMIT2}/epcsaft-1.3.0-cp313-cp313-manylinux_2_39_x86_64.whl'
    r.s.ENGINE_WHEEL_SHA256, r.s.ENGINE_COMMIT = SHA2, COMMIT2
    r.verify()
    return r, hc


def decompose():
    r, hc = driver()
    s = r.s
    import epcsaft
    record = r.STARTS['final']
    mapping = s.parameter_mapping(record)
    hc.SolventSpecification = lambda toml: r.bind(mapping)
    spec, _, broad, intervals = hc.setup()  # corrected (#260) water ideal-gas record
    spec._intervals = intervals
    ids = list(spec.parameters.component_ids)
    masses = {c['component_id']: c['fixed']['molar_mass']['value']['magnitude'] for c in spec.inputs['endpoint']['components']}
    pure = {cid: epcsaft.Pure(epcsaft.Parameters.from_mapping(spec.inputs['endpoint'], components=[cid]),
                              thermochemistry=epcsaft.ThermochemistryRecord(1e5, [intervals[ids.index(cid)]])) for cid in (W, M)}
    water = pure_rows(W, pure[W], masses[W], WATER_GRIDS)
    mea = pure_rows(M, pure[M], masses[M], [(101325., GRID)])
    mixture = {source: mixture_rows(spec, broad, masses, source, basis) for source, basis in MIXTURES.items()}
    # Grid rows reproduce #264's own rows at their source coordinates (same problem, new composition only by construction).
    check = {x['identity']: x for x in json.loads((B / 'results/stable-refit-255/evidence/final/heat-capacity-264.json').read_text())['rows']}
    reproduced = []
    for source, rows in mixture.items():
        for o in rows:
            ref = check.get(f"{source}-{o['T_K']}-0.0")
            if ref:
                # #264 ran Concepcion at its 100000 Pa; this issue runs every state at 101325 Pa.
                reproduced.append(dict(identity=ref['identity'], grid=o['equilibrium_kJ_kg_K'], retained=ref['predicted_kJ_kg_K'],
                                       retained_pressure_Pa=100000. if source == 'Concepcion2023' else 101325.,
                                       relative=abs(o['equilibrium_kJ_kg_K'] / ref['predicted_kJ_kg_K'] - 1)))
    same = [x for x in reproduced if x['retained_pressure_Pa'] == 101325.]
    assert same and max(x['relative'] for x in same) <= 1e-12 and max(x['relative'] for x in reproduced) <= 1e-6, reproduced
    closure = [dict(part=x['component'], T_K=x['T_K'], P_Pa=x['P_Pa'], closure_J_mol_K=x['closure_J_mol_K'], bound=x['closure_bound_J_mol_K'])
               for x in water + mea] + [dict(part=src, T_K=o['T_K'], P_Pa=101325., closure_J_mol_K=o['closure_J_mol_K']) for src, rows in mixture.items() for o in rows]
    for x in water + mea:
        assert abs(x['closure_J_mol_K']) <= x['closure_bound_J_mol_K'], x  # mixture closure is asserted inside hc.decompose
    return r.jsonable(dict(
        wheel_sha256=r.SHA, engine_commit=r.COMMIT, parameter_record=str(record.relative_to(ROOT)), parameter_sha256=sha(record),
        caloric_water='#260 IAPWS-95 ideal-gas record (data/reference/MEA/thermal/physical-ideal-gas-calorics.json)',
        caloric_water_sha256=sha(ROOT / 'data/reference/MEA/thermal/physical-ideal-gas-calorics.json'), producer_sha256=sha(__file__),
        units='kJ/(kg K) of the phase or pure liquid; closure in J/(mol K)', pressure_Pa=101325., closure_rule='|sum of term residual Cv - native| <= 1e-4 + 1e-4 |Cv_res|, h = 0.025 K',
        reproduction_of_264_rows=reproduced,
        maximum_closure_J_mol_K=max(abs(x['closure_J_mol_K']) for x in closure),
        water=water, mea=mea, mixture=mixture))


def stage1():
    (OUT / 'decomposition.json').write_text(json.dumps(decompose(), indent=1, allow_nan=False) + '\n')
    shares()


# ---------------------------------------------------------------- shares and routing (retained values only)

def mea_reference():
    rows = list(csv.DictReader((OUT / 'pure-mea-sources.csv').open()))
    chiu = {float(x['T_K']): float(x['cp_value']) for x in rows if x['source'] == 'Chiu1999'}
    return {'Maham1997': lambda T: (82.5 + .275 * T) / 61.08,  # Table 2, Eq. 1, 299.1-397.8 K; M = 61.08 g/mol
            'Chiu1999': lambda T: chiu[T]}  # Table 2 'this study', 303.15-353.15 K


def shares(d=None):
    """Shares from the retained decomposition (written), or from a given one (returned, for the #291 reproduction)."""
    retained = d is None
    d = json.loads((OUT / 'decomposition.json').read_text()) if retained else d
    iapws = {(float(x['T_K']), float(x['P_Pa'])): float(x['cp_kJ_kg_K']) for x in csv.DictReader((OUT / 'iapws95-water.csv').open())}
    measured = {(x['source'], float(x['T_K'])): float(x['cp_kJ_kg_K']) for x in csv.DictReader((B / 'heat-capacity-264/sources.csv').open())
                if float(x['loading']) == 0}
    water = {x['T_K']: x['cp_kJ_kg_K'] for x in d['water'] if x['P_Pa'] == 101325.}
    mea = {x['T_K']: x['cp_kJ_kg_K'] for x in d['mea']}
    refs = mea_reference()
    rows, excess = [], []
    for source, mix in d['mixture'].items():
        m = {o['T_K']: o['equilibrium_kJ_kg_K'] for o in mix}
        w = mix[0]['MEA_mass_fraction']
        for ref_name, ref in refs.items():
            def change(f):
                return f(T2) - f(T1)
            model = dict(water=change(water.get), mea=change(mea.get), mixture=change(m.get))
            model['excess'] = model['mixture'] - (1 - w) * model['water'] - w * model['mea']
            reference_ = dict(water=change(lambda T: iapws[(T, 101325.)]), mea=change(ref), mixture=change(lambda T: measured[(source, T)]))
            reference_['excess'] = reference_['mixture'] - (1 - w) * reference_['water'] - w * reference_['mea']
            e = {k: model[k] - reference_[k] for k in model}
            weighted = dict(water=(1 - w) * e['water'], mea=w * e['mea'], excess=e['excess'])
            share = {k: v / e['mixture'] for k, v in weighted.items()}
            identity = weighted['water'] + weighted['mea'] + weighted['excess'] - e['mixture']
            rows.append(dict(mixture_source=source, mea_source=ref_name, MEA_mass_fraction=w, interval_K=[T1, T2], model_change=model,
                             reference_change=reference_, slope_error=e, weighted_slope_error=weighted, share=share,
                             identity_residual=identity, carrier=[k for k, v in share.items() if v >= .5]))
            for T in sorted(m):
                if (source, T) in measured:
                    try:
                        r_mea = ref(T)
                    except KeyError:
                        r_mea = None
                    x = dict(mixture_source=source, mea_source=ref_name, T_K=T, MEA_mass_fraction=w, model_mixture=m[T], measured_mixture=measured[(source, T)],
                             model_water=water.get(T), iapws_water=iapws.get((T, 101325.)), model_mea=mea[T], reference_mea=r_mea)
                    x['model_excess'] = m[T] - (1 - w) * water[T] - w * mea[T] if water.get(T) else None
                    x['reference_excess'] = (measured[(source, T)] - (1 - w) * x['iapws_water'] - w * r_mea) if r_mea and x['iapws_water'] else None
                    if x['reference_excess'] is not None:  # level split: model - measured = water + MEA + excess parts
                        x.update(mixture_level_error=m[T] - measured[(source, T)], water_level_part=(1 - w) * (water[T] - x['iapws_water']),
                                 mea_level_part=w * (mea[T] - r_mea), excess_level_part=x['model_excess'] - x['reference_excess'])
                    excess.append(x)
    carriers = {tuple(r['carrier']) for r in rows}
    primary = [r for r in rows if r['mea_source'] == 'Maham1997']
    one = len(carriers) == 1 and len(next(iter(carriers))) == 1
    carrier = next(iter(carriers))[0] if one else None
    route = {'excess': 'Stage 2', 'mea': 'stop: return to Design', 'water': 'stop and report'}.get(carrier, 'stop and report')
    out = dict(rule='carrier: share >= 0.5 against both mixture sources (and, here, both pure-MEA sources)', interval_K=[T1, T2],
               cases=rows, carriers_by_case={f"{r['mixture_source']}|{r['mea_source']}": r['carrier'] for r in rows},
               carrier=carrier, routing=route, primary_mea_source='Maham1997',
               primary_cases_agree=len({tuple(r['carrier']) for r in primary}) == 1)
    if not retained:
        return out
    (OUT / 'shares.json').write_text(json.dumps(dict(wheel_sha256=d['wheel_sha256'], result=out), indent=1, allow_nan=False) + '\n')
    table(OUT / 'excess-by-temperature.csv', excess)
    print(json.dumps(dict(carriers=out['carriers_by_case'], routing=route,
                          shares={f"{r['mixture_source']}|{r['mea_source']}": r['share'] for r in rows}), indent=1))


# ---------------------------------------------------------------- stage 2: one added k_ij temperature-law coefficient

LAW = 'pair/monoethanolamine/water/k_ij'  # a0 keeps the record's k_ij identity; s keeps its slope identity
SLOPE = LAW + '/reciprocal_temperature_slope'
# Bounds are the issue's design choices; one optimizer scale moves k by 0.01 at 353.15 K (40 K from T_r).
NEW = {1: dict(identity=LAW + '/a1', unit='1 / kelvin', bound=1e-3, scale=.01 / 40),
       2: dict(identity=LAW + '/a2', unit='1 / kelvin ** 2', bound=2e-5, scale=.01 / 1600)}
# Stage 2 runs on Engine main 391dfe5d (#291), which differentiates Cp with respect to a2 at every #264 state. The bc779473
# attempt and its refusal stay in stage2/.
COMMIT2 = '391dfe5d64ede5036bf160bc6ae037ad5e14af32'
SHA2 = '0962e21d2fa7a8ba1ed4622f1110b3e8053bacd878fa41c999d85e8b9afab66b'
S2 = OUT / 'stage2-391dfe5d'
STARTS2 = {'final': B / 'results/selected-current-best-parameters.json', 'candidate': B / 'results/stable-refit-255/evidence/candidate-parameters.json'}


def convert(mapping, power, value=0.):
    """The record with MEA-water k_ij as pair_parameter_temperature_law: a0, the added a_power and the existing s."""
    m = copy.deepcopy(mapping)
    pair = next(p for p in m['pairs'] if {p['component_id_a'], p['component_id_b']} == {M, W})
    k = next(c for c in pair['coefficients'] if c['family'] == 'k_ij')
    slope = next(c for c in pair['coefficients'] if c['family'] == 'k_ij_reciprocal_temperature_slope')
    assert len(pair['coefficients']) == 2 and k['identity'] == LAW and slope['identity'] == SLOPE
    assert slope['reference_temperature'] == dict(magnitude=313.15, unit='kelvin')
    meta = {key: v for key, v in k.items() if key not in ('identity', 'family', 'value')}
    pair['coefficients'] = [dict(family='k_ij', identity=LAW + '/temperature_law', **meta, temperature_law=dict(
        form='polynomial-plus-reciprocal-temperature', reference_temperature=dict(slope['reference_temperature']),
        terms=[dict(power=0, coefficient=dict(identity=LAW, value=dict(k['value']))),
               dict(power=power, coefficient=dict(identity=NEW[power]['identity'], value=dict(magnitude=value, unit=NEW[power]['unit'])))],
        reciprocal_temperature_slope=dict(identity=SLOPE, value=dict(slope['value']))))]
    return m


def k_of_T(mapping, T):
    v = __import__('shared_evaluation').parameter_values(mapping)
    p, a = next(((p, v[q['identity']]) for p, q in NEW.items() if q['identity'] in v), (1, 0.))
    return v[LAW] + a * (T - 313.15)**p + v[SLOPE] * (1 / T - 1 / 313.15)


def engine(power=None):
    """The #255 driver bound to this issue: outputs under stage2/p<power>/, converted starts, 51 Hilliard rows, A6 + 1."""
    r, hc = driver()
    if power is None:
        return r, hc
    r.ELAPSED = 76800.  # owner, 2026-11-09: the 7200 s stage limit was sized for 32 cores; these fits run on 3. Other controls unchanged.
    out = S2 / f'p{power}'
    out.mkdir(parents=True, exist_ok=True)
    a6 = r.read(B / 'results/engine-3e83e19c-refit-chain/a6/spec.json')
    for q in a6['information_coordinates']:
        if q['identity'] in (LAW, SLOPE):  # same coordinates and bounds, now law slots
            q.update(family='temperature_law_coefficient', target=q['identity'])
    n = NEW[power]
    a6['information_coordinates'].append(dict(identity=n['identity'], family='temperature_law_coefficient', target=n['identity'],
                                              scale=n['scale'], bounds=[-n['bound'], n['bound']]))
    (out / 'a6-spec.json').write_text(json.dumps(a6, indent=1) + '\n')
    starts = out / 'starts'
    starts.mkdir(exist_ok=True)
    for name, path in STARTS2.items():
        (starts / f'{name}.json').write_text(json.dumps(convert(r.s.parameter_mapping(path), power), indent=1) + '\n')
    shifts = r.read(B / 'results/stable-refit-255/wide/retreat.json')['result']['shifts']  # the #255 candidate's totals
    r.OUT, r.A6 = out, out / 'a6-spec.json'
    r.STARTS = {name: starts / f'{name}.json' for name in STARTS2}
    r.SHIFTS = {'final': r.SHIFTS['final'], 'candidate': shifts}

    def rows(spec):
        """#264 probe rows: the 303 non-Cp rows plus the 51 in-domain Hilliard rows (2% scale) replacing the 4 Cp rows."""
        hc.SolventSpecification = lambda toml: spec
        _, original, broad, _ = hc.setup()
        chosen = [x for x in original if x['group'] not in ('Cp', 'integral heat')] + [x for x in broad if x['group'] == 'broad Cp']
        assert len(chosen) == 354
        return chosen
    r.RUNS = {name: dict(start=name, rows=rows) for name in STARTS2}
    bind = r.bind

    def converted_bind(mapping):
        """#255 takes coordinate origins from the specification's stored final-set endpoint; it gets the same law form."""
        spec = bind(mapping)
        spec.inputs['endpoint'] = convert(spec.inputs['endpoint'], power)
        return spec
    converted_bind.__wrapped__ = bind
    r.bind = converted_bind
    return r, hc


def broad_cp(r, hc, mapping):
    """#264's 60 Cp rows, Hilliard 51 and the phase searches at the 60 states (dense descent is a non-empty dense list)."""
    hc.SolventSpecification = lambda toml: r.bind(mapping)
    spec, _, broad, _ = hc.setup()
    p = hc.evaluate(spec, broad)
    assert hc.available(p)
    rows = [dict(identity=x['identity'], group=x['group'], source=x['row']['source'], T_K=float(x['row']['T_K']), loading=float(x['row']['loading']),
                 observed_kJ_kg_K=float(x['row']['cp_kJ_kg_K']), predicted_kJ_kg_K=v['value'] * x['feed_amount_mol'] / x['feed_mass_kg'] / 1000)
            for x, v in zip(broad, p, strict=True)]
    def aard(xs):
        return 100 * sum(abs(x['predicted_kJ_kg_K'] / x['observed_kJ_kg_K'] - 1) for x in xs) / len(xs)
    at = {(x['source'], x['T_K'], x['loading']): x['predicted_kJ_kg_K'] for x in rows}
    return dict(rows=rows, AARD_60_percent=aard(rows), AARD_hilliard_51_percent=aard([x for x in rows if x['group'] == 'broad Cp']),
                unloaded_change_313_353=at[('Hilliard2008', T2, 0.)] - at[('Hilliard2008', T1, 0.)], spec=spec, broad=broad)


def qualify0():
    """#291 step 2 on the 391dfe5d wheel, before any fit: the 307 #255 rows at the final set and the #255 candidate against
    their retained 8b9609d4 replays (<= 1e-8 relative), the stage-1 numbers, and the a2 Cp derivative at the 60 #264
    states with centred differences at unloaded Hilliard 313.15/333.15/353.15 K (<= 3e-7). The zero-change replay is qualify2."""
    new = decompose()
    r, hc = driver()  # unconverted records: before engine() rebinds the starts
    out = dict(replay_255={}, stage1={})
    retained = B / 'results/stable-refit-255'
    for name, rel in (('final', 'qualification/final-replay.json'), ('candidate', 'wide/replay.json')):
        values, ok, cost = r.replay(r.s.parameter_mapping(STARTS2[name]))
        old = r.read(retained / rel)
        ref = {x['identity']: x for x in old['result']}
        worst = max(values, key=lambda v: abs(v['value'] / ref[v['identity']]['value'] - 1))
        out['replay_255'][name] = dict(retained=str((retained / rel).relative_to(ROOT)), retained_wheel_sha256=old['wheel_sha256'], rows=len(values),
                                       available=ok, cost=cost, retained_cost=math.fsum(x['cost'] for x in old['result']),
                                       maximum_relative=abs(worst['value'] / ref[worst['identity']]['value'] - 1), at=worst['identity'])
        out['replay_255'][name]['passed'] = ok and len(values) == len(ref) == 307 and out['replay_255'][name]['maximum_relative'] <= 1e-8
    old = json.loads((OUT / 'decomposition.json').read_text())

    def numbers(d):
        rows = [('water', x) for x in d['water']] + [('mea', x) for x in d['mea']] + [(k, x) for k, xs in d['mixture'].items() for x in xs]
        flat = [(part, x, k, v) for part, x in rows for k, v in x.items() if k.endswith('kJ_kg_K')]  # per-term dicts are flattened
        return {(part, x['T_K'], x.get('P_Pa', 101325.), k + (f':{j}' if isinstance(v, dict) else '')): w
                for part, x, k, v in flat for j, w in (v.items() if isinstance(v, dict) else [(None, v)])}
    a, b = numbers(new), numbers(old)
    assert a.keys() == b.keys()
    totals = [k for k in a if k[3] in ('cp_kJ_kg_K', 'equilibrium_kJ_kg_K')]
    worst = max(totals, key=lambda k: abs(a[k] / b[k] - 1))
    s_new, s_old = shares(new), json.loads((OUT / 'shares.json').read_text())['result']
    share_difference = max(abs(x['share'][k] - y['share'][k]) for x, y in zip(s_new['cases'], s_old['cases'], strict=True) for k in x['share'])
    out['stage1'] = dict(retained_wheel_sha256=old['wheel_sha256'], cp_values=len(totals), maximum_relative_cp=abs(a[worst] / b[worst] - 1), at=list(worst),
                         maximum_absolute_any_term_kJ_kg_K=max(abs(a[k] - b[k]) for k in a), maximum_share_difference=share_difference,
                         maximum_closure_J_mol_K=new['maximum_closure_J_mol_K'], carrier=s_new['carrier'], routing=s_new['routing'])
    out['stage1']['passed'] = out['stage1']['maximum_relative_cp'] <= 1e-8 and s_new['carrier'] == s_old['carrier'] == 'excess'
    r, hc = engine(2)
    d2 = derivatives(r, hc, r.s.parameter_mapping(STARTS2['final']), 2, dict(derivatives=[], central_differences=[]))
    refused = [dict(identity=x['identity'], status=x['status'], message=x['message']) for x in d2['derivatives'] if x['status'] != 'Available']
    out['a2_derivative'] = dict(states=len(d2['derivatives']), available=len(d2['derivatives']) - len(refused), refused=refused,
                                central_differences=d2['central_differences'], passed=not refused and len(d2['derivatives']) == 60
                                and all(x['relative'] is not None and x['relative'] <= 3e-7 for x in d2['central_differences']))
    out['derivatives'] = d2['derivatives']
    out['passed'] = all(x['passed'] for x in out['replay_255'].values()) and out['stage1']['passed'] and out['a2_derivative']['passed']
    r.write('qualification/step0.json', out)
    print(json.dumps({k: v for k, v in out.items() if k != 'derivatives'}, indent=1, default=str), flush=True)
    assert out['passed'], 'step 0 failed: see qualification/step0.json'


def qualify2():
    """Sensitivity (choice of a1 or a2), then the zero-change replay of the chosen conversion at both starts."""
    r, hc = engine()
    final = r.s.parameter_mapping(STARTS2['final'])
    base = broad_cp(r, hc, final)
    sensitivity = {}
    for power, n in NEW.items():
        change = {}
        for label, value in [('+h', .01 * n['bound']), ('-h', -.01 * n['bound']), ('+bound', n['bound']), ('-bound', -n['bound'])]:
            change[label] = broad_cp(r, hc, convert(final, power, value))['unloaded_change_313_353']
            print(power, label, change[label], flush=True)
        sensitivity[power] = dict(coefficient=n['identity'], bound=n['bound'], unloaded_change=change,
                                  derivative_times_bound=(change['+h'] - change['-h']) / (.02 * n['bound']) * n['bound'],
                                  k_change_at_bound_393K=n['bound'] * 80**power)
    power = max(NEW, key=lambda p: abs(sensitivity[p]['derivative_times_bound']))
    r, hc = engine(power)
    replay = {}
    for name, path in STARTS2.items():
        old, new = r.s.parameter_mapping(path), r.s.parameter_mapping(r.STARTS[name])
        v_old, ok_old, cost_old = r.replay(old)
        v_new, ok_new, cost_new = r.replay(new)
        b_old, b_new = (broad_cp(r, hc, m)['rows'] for m in (old, new))
        rel = [abs(a['value'] / b['value'] - 1) for a, b in zip(v_new, v_old, strict=True)] + \
              [abs(a['predicted_kJ_kg_K'] / b['predicted_kJ_kg_K'] - 1) for a, b in zip(b_new, b_old, strict=True)]
        replay[name] = dict(rows=len(rel), available=ok_old and ok_new, cost=[cost_old, cost_new], maximum_relative=max(rel),
                            k_ij_313_393=[[k_of_T(m, T) for T in (313.15, 353.15, 393.15)] for m in (old, new)])
        if name == 'final':
            r.write('qualification/final-replay.json', v_new)
    excluded = r.read(B / 'results/stable-refit-255/qualification/summary.json')['result']['excluded']
    passed = all(x['available'] and x['maximum_relative'] <= 1e-12 for x in replay.values())
    r.write('qualification/summary.json', dict(passed=passed, excluded=excluded, chosen_power=power, sensitivity=sensitivity, zero_change_replay=replay,
                                                 final_set_broad_cp=dict(AARD_60_percent=base['AARD_60_percent'], AARD_hilliard_51_percent=base['AARD_hilliard_51_percent'],
                                                                         unloaded_change_313_353=base['unloaded_change_313_353']),
                                                 excluded_source='results/stable-refit-255/qualification/summary.json'))
    (S2 / 'chosen-power').write_text(f'{power}\n')
    print(json.dumps(dict(power=power, sensitivity=sensitivity, replay=replay), indent=1))
    assert passed


def chosen():
    return engine(int((S2 / 'chosen-power').read_text()))


def fit2(run):
    r, _ = chosen()
    r.run_fit(run)


def assess2(run):
    """#255 criteria 1-3 (307 rows, enforced/offset/census) plus F2-F4 heat-capacity checks at the run's candidate."""
    r, hc = chosen()
    # Retain #264's original comparison rows, including integral heats excluded from fitting.
    for name, mapping in ((run, r.result(f'{run}/candidate.json')),
                          ('qualification', r.s.parameter_mapping(STARTS2['final']))):
        if (r.OUT / name / 'comparison-264.json').exists():
            continue
        hc.SolventSpecification = lambda toml: r.bind(mapping)
        spec, original, broad, _ = hc.setup()
        predictions, cp_predictions = hc.evaluate(spec, original), hc.evaluate(spec, broad)
        assert hc.available(predictions) and hc.available(cp_predictions)
        r.write(f'{name}/comparison-264.json', dict(original=predictions, original_metrics=hc.group_metrics(original, predictions),
                                                  broad=cp_predictions, broad_metrics=hc.group_metrics(broad, cp_predictions)))
    rows = r.RUNS[run]['rows']
    if not (r.OUT / run / 'assessment.json').exists():
        r.assess(run)
    candidate = r.result(f'{run}/candidate.json')
    _, ok, cost354 = r.replay(candidate, rows)
    cp = broad_cp(r, hc, candidate)
    phase = hc.stability(cp['spec'], cp['broad'])
    at = {(x['source'], x['T_K']): x['predicted_kJ_kg_K'] for x in cp['rows'] if x['loading'] == 0}
    measured = {(x['source'], float(x['T_K'])): float(x['cp_kJ_kg_K']) for x in csv.DictReader((B / 'heat-capacity-264/sources.csv').open()) if float(x['loading']) == 0}
    envelope = {T: dict(model=at[('Hilliard2008', T)], low=min(measured[('Hilliard2008', T)], measured[('Concepcion2023', T)]),
                        high=max(measured[('Hilliard2008', T)], measured[('Concepcion2023', T)])) for T in (313.15, 333.15, 353.15)}
    for x in envelope.values():
        x['inside'] = x['low'] <= x['model'] <= x['high']
    q = r.result('qualification/summary.json')
    a = r.result(f'{run}/assessment.json')
    v, scales = r.s.parameter_values(candidate), {c['identity']: c for c in r.read(r.A6)['information_coordinates']}
    law = {i: dict(value=v[i], bounds=scales[i]['bounds'], interior=scales[i]['bounds'][0] < v[i] < scales[i]['bounds'][1])
           for i in (LAW, SLOPE, NEW[q['chosen_power']]['identity'])}
    source_mean = (measured[('Hilliard2008', T2)] - measured[('Hilliard2008', T1)] + measured[('Concepcion2023', T2)] - measured[('Concepcion2023', T1)]) / 2
    f2 = dict(model=cp['unloaded_change_313_353'], source_mean=source_mean, tolerance=.05, passed=abs(cp['unloaded_change_313_353'] - source_mean) <= .05)
    dense = sum(bool(x['dense']) for x in phase)
    f4 = dict(criteria_255=a['passed'], stability_255=a['stability_passed'], AARD_60_percent=cp['AARD_60_percent'], AARD_60_baseline=2.512,
              AARD_hilliard_51_percent=cp['AARD_hilliard_51_percent'], AARD_hilliard_51_baseline=2.443, dense_descent_264_states=dense,
              gas_descent_264_states=sum(bool(x['gas']) for x in phase), unresolved_264_states=sum(bool(x['unresolved']) for x in phase),
              law_interior=all(x['interior'] for x in law.values()))
    f4['passed'] = bool(f4['criteria_255'] and f4['AARD_60_percent'] <= 2.512 and dense == 0 and f4['law_interior'])
    r.write(f'{run}/heat-capacity.json', dict(cost_354=cost354, available_354=ok, law=law, k_ij=[dict(T_K=T, k=k_of_T(candidate, T)) for T in GRID],
                                              F2=f2, F3=dict(states=envelope, passed=all(x['inside'] for x in envelope.values())), F4=f4,
                                              broad_cp=cp['rows'], phase_264=phase))
    print(run, json.dumps(dict(cost_354=cost354, F2=f2, F3=all(x['inside'] for x in envelope.values()), F4=f4, law=law)), flush=True)


def select2():
    """#255 selection on this objective: among runs passing F4, the lower 354-row cost."""
    r, _ = chosen()
    runs = {n: r.result(f'{n}/heat-capacity.json') for n in STARTS2}
    passing = [n for n, x in runs.items() if x['F4']['passed']]
    pick = min(passing or runs, key=lambda n: runs[n]['cost_354'])
    r.write('selected.json', dict(run=pick, admissible=bool(passing), runs={n: dict(cost_354=x['cost_354'], F2=x['F2']['passed'], F3=x['F3']['passed'],
                                  F4=x['F4']['passed']) for n, x in runs.items()}))


def diagnose2():
    """Why the a2 fit stops: Engine derivative of each #264 Cp row with respect to a1 and a2 at the converted final set,
    central differences (h = 1% of bound) at unloaded Hilliard 313/333/353 K, and fixed-parameter scans (diagnostic only)."""
    r, hc = chosen()
    final = r.s.parameter_mapping(STARTS2['final'])
    out = dict(derivatives=[], central_differences=[], fixed_parameter_scans=[])
    for power in NEW:
        derivatives(r, hc, final, power, out)
        for a in ([-2e-7, -2e-6, -1e-5, -2e-5, 2e-5] if power == 2 else [-1e-3, 1e-3]):
            x = broad_cp(r, hc, convert(final, power, a))
            at = {y['T_K']: y['predicted_kJ_kg_K'] for y in x['rows'] if y['source'] == 'Hilliard2008' and y['loading'] == 0}
            out['fixed_parameter_scans'].append(dict(coefficient=NEW[power]['identity'], value=a, cp_313_kJ_kg_K=at[T1], cp_333_kJ_kg_K=at[333.15], cp_353_kJ_kg_K=at[T2],
                                                     change_313_353=x['unloaded_change_313_353'], AARD_hilliard_51_percent=x['AARD_hilliard_51_percent']))
            print(out['fixed_parameter_scans'][-1], flush=True)
    out['note'] = 'Diagnostic only: single-coefficient changes at otherwise fixed final-set parameters; not fits and not candidates.'
    r.write('diagnosis.json', out)
    print(json.dumps({k: v for k, v in out.items() if k != 'derivatives'}, indent=1))
    print([(x['identity'], x['coefficient'][-2:], x['status'], x['message'][:100]) for x in out['derivatives'] if x['status'] != 'Available'])


def derivatives(r, hc, final, power, out):
    """Engine Cp derivative of each #264 row with respect to one law coefficient at the converted final set, and centred
    differences (h = 1 % of the bound) at unloaded Hilliard 313.15/333.15/353.15 K."""
    import epcsaft
    from epcsaft import regression as reg
    spec = r.bind(convert(final, power))
    hc.SolventSpecification = lambda toml: spec
    _, _, broad, _ = hc.setup()
    ids = list(spec.parameters._native.temperature_law_coefficient_identities)
    model = epcsaft.Mixture(spec.parameters, thermochemistry=spec.thermal, active_parameters=[
        epcsaft.ActiveParameter(epcsaft.ParameterFamily.TemperatureLawCoefficient, [ids.index(NEW[power]['identity'])])])
    for x in broad:
        try:
            d = reg.differentiate(model, spec.observation(x))
            status, value, message = d.status.name, list(d.value), d.message
        except epcsaft.ParameterError as error:  # the fit's 'invalid direction ... balance' stop
            status, value, message = 'ParameterError', [], str(error)
        out['derivatives'].append(dict(coefficient=NEW[power]['identity'], identity=x['identity'], T_K=float(x['row']['T_K']), loading=float(x['row']['loading']),
                                       pressure_Pa=spec.problems[x['problem']].P, status=status, derivative_J_mol_K=value, message=message))
    h = .01 * NEW[power]['bound']
    for T in (T1, 333.15, T2):
        ident = f'Hilliard2008-{T}-0.0'
        values = {}
        for a in (h, -h):
            s2 = r.bind(convert(final, power, a))
            values[a] = s2.prediction(next(x for x in r.RUNS['final']['rows'](s2) if x['identity'] == ident))['value']
        engine_ = next(x for x in out['derivatives'] if x['identity'] == ident and x['coefficient'] == NEW[power]['identity'])
        fd = (values[h] - values[-h]) / (2 * h)
        out['central_differences'].append(dict(coefficient=NEW[power]['identity'], identity=ident, step=h, central_J_mol_K=fd, engine=engine_['derivative_J_mol_K'],
                                               relative=abs(engine_['derivative_J_mol_K'][0] / fd - 1) if engine_['derivative_J_mol_K'] else None))
    return out


def grid2():
    """Mixture Cp on the stage-1 grid at the selected endpoint; pure water and MEA do not depend on MEA-water k_ij."""
    r, hc = chosen()
    pick = r.result('selected.json')['run']
    mapping = r.result(f'{pick}/candidate.json')
    hc.SolventSpecification = lambda toml: r.bind(mapping)
    spec, _, broad, intervals = hc.setup()
    spec._intervals = intervals
    masses = {c['component_id']: c['fixed']['molar_mass']['value']['magnitude'] for c in spec.inputs['endpoint']['components']}
    r.write('selected-grid.json', dict(run=pick, mixture={s: mixture_rows(spec, broad, masses, s, b) for s, b in MIXTURES.items()}))


def present():
    """Figure and plotted values from retained results only."""
    import matplotlib
    matplotlib.use('Agg')
    import matplotlib.pyplot as plt
    d = json.loads((OUT / 'decomposition.json').read_text())
    iapws = list(csv.DictReader((OUT / 'iapws95-water.csv').open()))
    mea_src = list(csv.DictReader((OUT / 'pure-mea-sources.csv').open()))
    mix_src = [x for x in csv.DictReader((B / 'heat-capacity-264/sources.csv').open()) if float(x['loading']) == 0]
    excess = list(csv.DictReader((OUT / 'excess-by-temperature.csv').open()))
    selected = S2 / f"p{(S2 / 'chosen-power').read_text().strip()}" / 'selected-grid.json' if (S2 / 'chosen-power').exists() else None
    stage2 = json.loads(selected.read_text())['result'] if selected and selected.exists() else None
    water = {x['T_K']: x['cp_kJ_kg_K'] for x in d['water'] if x['P_Pa'] == 101325.}
    mea = {x['T_K']: x['cp_kJ_kg_K'] for x in d['mea']}
    plotted = []

    def line(ax, xs, ys, series, **kw):
        ax.plot(xs, ys, **kw)
        plotted.extend(dict(panel=ax.get_title(), series=series, kind='model line', T_K=x, cp_kJ_kg_K=y) for x, y in zip(xs, ys))

    def points(ax, xs, ys, series, **kw):
        ax.plot(xs, ys, ls='none', **kw)
        plotted.extend(dict(panel=ax.get_title(), series=series, kind='reference points', T_K=x, cp_kJ_kg_K=y) for x, y in zip(xs, ys))

    fig, axes = plt.subplots(2, 2, figsize=(10, 7.5), constrained_layout=True)
    ax = axes[0, 0]
    ax.set_title('(a) pure water')
    for P, style in [(101325., '-'), (300000., '--')]:
        rows = [x for x in d['water'] if x['P_Pa'] == P]
        line(ax, [x['T_K'] for x in rows], [x['cp_kJ_kg_K'] for x in rows], f'model {P:.0f} Pa', color='#0072B2', ls=style, label=f'model, {P / 1e6:.4g} MPa')
        ref = [x for x in iapws if float(x['P_Pa']) == P]
        points(ax, [float(x['T_K']) for x in ref], [float(x['cp_kJ_kg_K']) for x in ref], f'IAPWS-95 {P:.0f} Pa', color='k',
               marker='o' if P == 101325. else 'x', mfc='none', ms=4, label=f'IAPWS-95, {P / 1e6:.4g} MPa')
    ax = axes[0, 1]
    ax.set_title('(b) pure liquid MEA, 0.101 MPa')
    line(ax, list(mea), list(mea.values()), 'model', color='#0072B2', label='model')
    for src, marker, unit in [('Maham1997', 'x', 61.08), ('Chiu1999', 'o', 1.)]:
        rows = [x for x in mea_src if x['source'] == src]
        ys = [float(x['cp_value']) / unit for x in rows]
        ax.errorbar([float(x['T_K']) for x in rows], ys, yerr=[y * (.009 if src == 'Maham1997' else .02) for y in ys], ls='none', marker=marker,
                    mfc='none', color='k' if src == 'Maham1997' else '#D55E00', ms=5, capsize=2,
                    label=f"{src[:-4]} {src[-4:]} ({'±0.9 %' if src == 'Maham1997' else '±2 %'})")
        plotted.extend(dict(panel=ax.get_title(), series=src, kind='reference points', T_K=float(x['T_K']), cp_kJ_kg_K=y) for x, y in zip(rows, ys))
    ax = axes[1, 0]
    ax.set_title('(c) 30 wt% MEA–water, unloaded, 0.101 MPa')
    h = d['mixture']['Hilliard2008']
    line(ax, [o['T_K'] for o in h], [o['equilibrium_kJ_kg_K'] for o in h], 'final set (7 m)', color='#0072B2', label='model, final set')
    if stage2:
        s2 = stage2['mixture']['Hilliard2008']
        line(ax, [o['T_K'] for o in s2], [o['equilibrium_kJ_kg_K'] for o in s2], f"stage 2 {stage2['run']} start (7 m)", color='#009E73', ls='--',
             label='model, k_ij(T) with a₂ (not adopted)')
    for src, marker, color in [('Hilliard2008', 'o', 'k'), ('Concepcion2023', 's', '#D55E00'), ('Weiland1997', '^', '#CC79A7')]:
        rows = [x for x in mix_src if x['source'] == src]
        points(ax, [float(x['T_K']) for x in rows], [float(x['cp_kJ_kg_K']) for x in rows], src, marker=marker, color=color, mfc='none', ms=5,
               label=src.replace('Concepcion', 'Concepción ').replace('Hilliard', 'Hilliard ').replace('Weiland', 'Weiland '))
    ax = axes[1, 1]
    ax.set_title('(d) excess $c_p^E=c_p-\\sum_i w_i c_{p,i}$')
    model_e = [o['equilibrium_kJ_kg_K'] - (1 - o['MEA_mass_fraction']) * water[o['T_K']] - o['MEA_mass_fraction'] * mea[o['T_K']] for o in h if o['T_K'] in water]
    line(ax, [o['T_K'] for o in h if o['T_K'] in water], model_e, 'final set excess (7 m)', color='#0072B2', label='model, final set')
    if stage2:
        e2 = [o['equilibrium_kJ_kg_K'] - (1 - o['MEA_mass_fraction']) * water[o['T_K']] - o['MEA_mass_fraction'] * mea[o['T_K']] for o in s2 if o['T_K'] in water]
        line(ax, [o['T_K'] for o in s2 if o['T_K'] in water], e2, 'stage 2 excess (7 m)', color='#009E73', ls='--', label='model, k_ij(T) with a₂')
    for (mix, ref), marker, color in [(('Hilliard2008', 'Maham1997'), 'o', 'k'), (('Hilliard2008', 'Chiu1999'), 'x', 'k'),
                                      (('Concepcion2023', 'Maham1997'), 's', '#D55E00'), (('Concepcion2023', 'Chiu1999'), '+', '#D55E00')]:
        rows = [x for x in excess if x['mixture_source'] == mix and x['mea_source'] == ref and x['reference_excess']]
        points(ax, [float(x['T_K']) for x in rows], [float(x['reference_excess']) for x in rows], f'{mix} - IAPWS-95 - {ref}', marker=marker,
               color=color, mfc='none', ms=5, label=f'{mix[:-4]} − IAPWS-95 − {ref[:-4]}'.replace('Concepcion', 'Concepción'))
    ax.axhline(0, color='0.6', lw=.6)
    for ax in axes.flat:
        ax.set_xlabel('T / K')
        ax.set_ylabel('$c_p$ / kJ kg$^{-1}$ K$^{-1}$')
        ax.legend(fontsize=7, frameon=False)
        ax.axvspan(T1, T2, color='0.92', zorder=0)
    axes[1, 1].set_ylabel('$c_p^E$ / kJ kg$^{-1}$ K$^{-1}$')
    fig.savefig(OUT / 'heat-capacity-slope.png', dpi=180)
    table(OUT / 'plotted-values.csv', plotted)


if __name__ == '__main__':
    commands = {'reference': reference, 'stage1': stage1, 'qualify0': qualify0, 'shares': shares, 'qualify2': qualify2, 'select2': select2, 'grid2': grid2, 'present': present, 'diagnose2': diagnose2}
    if sys.argv[1] in ('fit2', 'assess2'):
        {'fit2': fit2, 'assess2': assess2}[sys.argv[1]](sys.argv[2])
    else:
        commands[sys.argv[1]]()
