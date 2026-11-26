"""Reconcile referee quantities from retained state and observation identities."""
from collections import Counter
from decimal import Decimal
from math import fsum, isclose, log
from statistics import mean
import sys
if __package__:
    from .records import DISPLAY, MEA, MDEA, SALT, ROOT
else:
    from records import DISPLAY, MEA, MDEA, SALT, ROOT

sys.path.insert(0,str(ROOT/'src'))
from MEA.common.retained_results import parameter_fingerprint  # noqa: E402
MODELS = [(case,label) for case in ('salt','historical') for label in ('incumbent','refit')]
AMP5 = 'analyses/round_5/results/A/'

def scores(rows):
    errors = [100*(r['value']/r['observed']-1) for r in rows if r['value'] is not None and r['observed']]
    return dict(requested=len(rows), available=sum(r['value'] is not None for r in rows), relative_count=len(errors),
                AARD_percent=mean(map(abs,errors)) if errors else None, bias_percent=mean(errors) if errors else None)

def matched(s, group):
    models = {f'{c}/{label}':{r['identity']:r for r in s.core(f'C/{c}/{label}.json.gz')['rows'] if r['group']==group}
              for c,label in MODELS}
    keys = set.intersection(*[{k for k,r in rows.items() if r['value'] is not None} for rows in models.values()])
    assert all(len({(rows[k]['observed'],str(rows[k]['row'])) for rows in models.values()})==1 for k in keys)
    return {m:dict(full=scores(list(rows.values())), matched=scores([rows[k] for k in sorted(keys)]),
                   missing=[r for r in rows.values() if r['value'] is None], common_keys=sorted(keys)) for m,rows in models.items()}

FINITE_NEGATIVE = 'no descent in the finite search'
TWO_LIQUIDS = 'two liquids of lower Gibbs energy'
CONNECTED_VAPOR = 'liquid plus a vapor-connected phase of lower Gibbs energy'


def phase_outcome(value, *, completion=False):
    if completion:
        if issue := value.get('engine_issue'):
            assert '#' in issue and issue.rsplit('#',1)[1].isdigit()
            return 'open Engine item'
        if value.get('pair'):
            return value['pair']
        if value['parent_closed'] and value['native_complete'] and value['supplied_complete'] and not value['descent']:
            return FINITE_NEGATIVE
        raise AssertionError(f"Search {value['key']} did not meet the completion rule")
    if any(q['confirmed'] for q in value.get('attempts',[])):
        return 'confirmed split'
    if 'instability' in value:
        return ('unresolved phase identity' if value['instability']=='resolved descent' else value['instability'])
    if value.get('search',{}).get('no_descent_in_trial_set'):
        return 'finite search, no resolved descent'
    return 'unresolved' if value.get('search',{}).get('completed') else 'unavailable'


def parent_agreement(left, right):
    fields = ('density_mol_m3','Gibbs_over_RT_mol')
    return all(isclose(a,b,rel_tol=1e-10) for a,b in zip(
        (*left['x'],*(left[k] for k in fields)),(*right['x'],*(right[k] for k in fields)),strict=True))


def vapor_trace_passes(pair):
    from shared_bicarbonate_417 import vapor_trace_connected

    return vapor_trace_connected(pair['vapor_trace'],pair['phases'][-1]['density_mol_m3'])


def qualifying_pair(pair, pressure, tolerance, *, vapor=False):
    from classify_descents import distinct_phases, matched
    from reference_states_428 import phase_closure

    amounts = pair.get('amounts_mol',[])
    if len(amounts)!=2 or min(amounts)<=0 or not pair.get('requested_tolerance_met'):
        return False
    details = pair if vapor else pair.get('diagnostics') or {}
    T = pair.get('T_K',pair.get('T'))
    if not phase_closure(details,pressure,tolerance,temperature=T):
        return False
    a,b = details['phases']
    distinct = distinct_phases((a['x'],b['x']),(a['density_mol_m3'],b['density_mol_m3']))
    roots = vapor_trace_passes(pair) if vapor else len(pair['roots'])==2 and all(
        any(r['returned']=='liquid' for r in matched(group,tolerance,density,T=T,P=pressure))
        for group,density in zip(pair['roots'],pair['densities_mol_m3'],strict=True))
    return (distinct and roots and amounts==[a['amount_mol'],b['amount_mol']]
            and pair['Gibbs_decrease_over_RT_mol']>pair['numerical_error_over_RT_mol'])


def no_descent(completed, trials):
    return bool(completed and trials) and all(t['evidence']=='no_resolved_descent'
        and t['message'].startswith(('converged:','Michelsen tangent-plane trial converged:'))
        and t.get('optimizer_success',True) and t.get('optimizer_tolerance_met') is not False
        and t.get('descent',t.get('resolved_descent')) is False for t in trials)


def supplied_complete(counts, excluded, declared):
    return (isinstance(counts,dict) and counts.keys()=={'evaluated'}
            and type(excluded) is int and type(declared) is int
            and 0<=excluded<=declared and type(counts['evaluated']) is int
            and counts['evaluated']==declared-excluded)


def witness_direction(entry):
    evidence = entry['evidence']
    witness = evidence['witness']
    roots = [v for v in evidence['roots'] if v.get('log_density_distance',1)<=log(1.01)
             and v['relative_pressure_residual']<=1e-10]
    error = witness['quantities'].get('arithmetic_error_estimate_over_rt')
    direction = min(roots,key=lambda v:v['log_density_distance'])['returned'] if roots else None
    if direction=='unspecified' and entry.get('dilute_trace',{}).get('connected'):
        direction = 'vapor'
    if not (error is not None and witness['quantities'].get('tpd_over_rt',0)<-error):
        direction = None
    return direction if direction in ('vapor','liquid') else 'unclassified'

def reference(s, replay):
    data = {k:v['value'] for k,v in replay['rows'].items() if 'value' in v and 'derivatives' in v['value']}
    quantities = {}
    difference = 'engine_minus_Gibbs_Helmholtz_kJ'
    diagnostic = 'diagnostic_engine_minus_Gibbs_Helmholtz_kJ'
    fields = ('eos_volume_m3','frozen_G_volume_m3','moving_G_volume_m3','correction_m3',
              'engine_system_enthalpy_J','engine_frozen_at_same_pressure_J','Gibbs_Helmholtz_J','pressure_tracking_term_J')
    for k,v in data.items():
        n = v['amine_feed_mol']
        reduced = []
        for q in v['derivatives']:
            step = {f:q[f]/n for f in fields if f in q}
            if 'diagnostic_Gibbs_Helmholtz_J' in q and 'engine_system_enthalpy_J' in q:
                step[diagnostic] = (q['engine_system_enthalpy_J']-q['diagnostic_Gibbs_Helmholtz_J'])/n/1000
            if all(f in q for f in ('Gibbs_Helmholtz_J','engine_system_enthalpy_J')):
                h, g = q['engine_system_enthalpy_J'],q['Gibbs_Helmholtz_J']
                step[difference] = (h-g)/n/1000
                alt = q.get('shifted_gauge',{})
                if all(f in alt for f in ('Gibbs_Helmholtz_J','engine_system_enthalpy_J')):
                    shift = v['caloric_gauge']['shifted']['h_J_mol']-v['caloric_gauge']['baseline']['h_J_mol']
                    factor = v['T_K']**2/(v['T_K']**2-q['step_K']**2)
                    dh, dg = (alt['engine_system_enthalpy_J']-h)/n, (alt['Gibbs_Helmholtz_J']-g)/n
                    step['gauge_cancellation'] = dict(engine_shift_J_mol=dh, gibbs_shift_J_mol=dg,
                          expected_engine_shift_J_mol=shift, expected_Gibbs_FD_shift_J_mol=shift*factor,
                          difference_after_FD_bias_J_mol=(dh-dg)-shift*(1-factor))
            reduced.append(step)
        quantities[k] = dict(steps=reduced, step_K=[q['step_K'] for q in v['derivatives']],
                             state={f:v[f] for f in v if f!='derivatives'})
        if any(diagnostic in q for q in reduced) and all(diagnostic in q or difference in q for q in reduced):
            values = [q.get(diagnostic,q.get(difference)) for q in reduced]
            quantities[k]['diagnostic_spread_kJ'] = max(values)-min(values)
        failures = [q for q in v['derivatives'] if 'caloric_refusal' in q]
        if failures:
            quantities[k]['caloric_refusals'] = {str(q['step_K']):q['caloric_refusal'] for q in failures}
            residuals = {}
            for q in failures:
                for attempt in q.get('caloric_root_attempts',[]):
                    if attempt['accepted']:
                        residuals.pop(str(attempt['T_K']),None)
                    elif (liquid := [r['relative_pressure_residual'] for r in attempt['roots'] if r.get('returned')=='liquid']):
                        residuals.setdefault(str(attempt['T_K']),[]).append(min(liquid))
            quantities[k]['failed_root_best_relative_residual'] = {t:min(values) for t,values in residuals.items()}
    if all(k in quantities for k in ('daughter-1','daughter-2')):
        a,b = (quantities[f'daughter-{i}'] for i in (1,2))
        assert a['step_K']==b['step_K']
        quantities['daughters-sum'] = dict(step_K=a['step_K'],steps=[
            {f:q[f]+r[f] for f in sorted(q.keys() & r.keys())} for q,r in zip(a['steps'],b['steps'],strict=True)])
    for v in quantities.values():
        for q in v['steps']:
            if 'moving_G_volume_m3' in q:
                q.update(correction_percent=100*q['correction_m3']/q['eos_volume_m3'],
                         slope_difference_m3=q['moving_G_volume_m3']-q['frozen_G_volume_m3']-q['correction_m3'])
        v['spread'] = {f:max(q[f] for q in v['steps'])-min(q[f] for q in v['steps'])
                       for f in (*fields,difference) if all(f in q for q in v['steps'])}
    low = s.core('A/reference.json.gz')['low_pressure_controls']
    controls = {k:dict(outcome=phase_outcome(row['value']), replay=row['value']) if 'value' in row else row
                for k,row in replay['rows'].items() if k in ('tracking','100-kPa')}
    complete = len(quantities)==8 and all(difference in v['spread'] for v in quantities.values()) and all(
        'gauge_cancellation' in q for q in quantities.get('AMP',{}).get('steps',[]))
    parent = quantities['parent']
    missing = [k for k,v in quantities.items() if difference not in v['spread']]
    scope = ('Caloric comparisons cover the fitted rows and extrapolated split.' if complete else
             f"The admitted caloric step spread remains unresolved for {', '.join(missing)}.")
    return ('narrowed claim',
            f"The MDEA parent correction is {parent['steps'][-1]['correction_percent']:.2f}% at {parent['state']['P_Pa']/1e6:.3f} MPa. {scope}",
            dict(branches=quantities, low_pressure_controls=low, reference_controls=controls))

def phases(s,replay):
    root = 'C/salt/'
    outcome = s.core(root+'search-outcome.json.gz')
    selected = parameter_fingerprint(s.core(root+'selection.json.gz')['selected'][2]['parameters'])
    fixed = s.core(root+'rms-fixed-pressures.json.gz')
    target = fixed['pressure_262_MPa']
    assert selected==outcome['parameter_fingerprint']==fixed['fingerprint'], 'MDEA model fingerprint mismatch'
    rows = s.core(root+'search-0.json.gz')
    batches = [s.core(root+f'phase-batches/{i}.json.gz') for i in range(12)]
    assert all(b['parameter_fingerprint']==selected for b in batches), 'MDEA phase batch fingerprint mismatch'
    assert {r['key']:r for b in batches for r in b['rows']}=={r['key']:r for r in rows if 'same_calculation_as' not in r}
    by_key = {r['key']:r for r in rows}
    joins = s.core('B/census.json.gz')['joins']
    observations = {}
    for identity,links in joins.items():
        for link in links:
            observations.setdefault(outcome['aliases'].get(link['key'],link['key']),[]).append(identity)
    strata = {}
    for stratum in ('grid','measured'):
        pool = [r for r in rows if r['key'].startswith('grid:')==(stratum=='grid')]
        descents = [r for r in pool if r['descent']]
        strata[stratum] = dict(attempts=len(pool), distinct=len({r.get('same_calculation_as',r['key']) for r in pool}),
                               unfinished=[r['key'] for r in pool if not r['available']], descent_attempts=len(descents),
                               distinct_descents=len({r.get('same_calculation_as',r['key']) for r in descents}))
    entries = []
    for q in outcome['classifications']:
        row, directions = by_key[q['key']], set()
        readback = replay['rows'].get(q['key'],{})
        for w in readback.get('value',[]):
            directions.add(witness_direction(w))
        entries.append(dict(q, model_bubble_Pa=row.get('pressure_basis',{}).get('model_bubble_pressure_Pa') or
                            replay['rows'].get('bubble:'+q['key'],{}).get('value',{}).get('P_Pa') or row.get('pressure_Pa'),
                            observation_ids=sorted(set(observations.get(q['key'],[]))), directions=sorted(directions or {'unclassified'}),
                            attempt_outcomes=['confirmed' if a['confirmed'] else 'coalesced' if 'coalesced' in a['message'] else 'unresolved'
                                              for a in q['attempts']], search_evidence=row))
    strata['targeted'] = dict(attempts=1,distinct=1,confirmed=target['outcome']=='confirmed split')
    grid = next(q for q in outcome['classifications'] if q['key'] in outcome['confirmed'])
    split = next(a for a in target['attempts'] if a['confirmed'])
    unclassified = sum('unclassified' in e['directions'] for e in entries if not e['key'].startswith('grid:'))
    return ('narrowed claim' if unclassified else 'answered', f'The adopted model confirms a grid split at {grid["pressure_Pa"]/1e6:.3f} MPa and a targeted split at {target["P_Pa"]/1e6:.3f} MPa. {unclassified} measured states include an unclassified direction.',
            dict(fingerprint=selected,strata=strata, classifications=entries, targeted=dict(target,confirmed_attempt=split), grid_confirmed=grid, counts=dict(total_descents=sum(r['descent'] for r in rows),
                distinct_descents=len(entries), measured_two_liquid_attempted=sum(bool(e['attempts']) for e in entries if not e['key'].startswith('grid:')))))

def dea(s,_):
    search=s.core('F/search-outcome.json.gz')
    assessment=s.core('F/assessment.json.gz')
    assert search['parameter_fingerprint']==assessment['identity']['parameters']
    pool=[q for q in assessment['expanded_design'] if q['group']=='Weiland']
    pairs=[dict(r, signed_relative_percent=100*(r['value']/r['observed']-1), phase=q) for q in search['classifications']
           if q['key'] in search['confirmed'] for r in pool if r['identity']+':problem'==q['key']]
    assert len(pairs)==4 and len(pool)==44
    first=next(q for q in pairs[0]['phase']['attempts'] if q['confirmed'])
    mapping=s.core('F/selection.json.gz')['selected'][2]['parameters']
    components={q['component_id']:q['fixed'] for q in mapping['components']}
    species=s.read('analyses/dea_transfer/inputs/part-ii-346/f2-carbamate-413-route.json')['species']
    masses=[components[k]['molar_mass']['value']['magnitude'] for k in species]
    charges=[components[k]['charge_number']['value']['magnitude'] for k in species]
    daughter=[dict(x=x,mole_fraction_of_total=n/fsum(first['amounts_mol']),density_mol_m3=rho,
                   density_kg_m3=rho*fsum(m*v for m,v in zip(masses,x,strict=True)),
                   charge_mol=n*fsum(z*v for z,v in zip(charges,x,strict=True))) for x,n,rho in
              zip(first['phases'],first['amounts_mol'],first['densities_mol_m3'],strict=True)]
    formulas=s.read('analyses/dea_transfer/inputs/part-ii-346/reporting-declarations-current.toml')['element_formulas']
    feed=pairs[0]['phase']['feed_mol']
    closure={e:fsum(formulas[k].get(e,0)*(fsum(n*x[i] for n,x in zip(first['amounts_mol'],first['phases'],strict=True))-feed[i])
                    for i,k in enumerate(species)) for e in ('C','H','N','O','charge')}
    return 'answered',f'Liquid density AARD is {scores(pairs)["AARD_percent"]:.5f}% across {len(pairs)} predicted split feeds and {scores(pool)["AARD_percent"]:.5f}% across all {len(pool)} observations.',         dict(four=scores(pairs),all_44=scores(pool),rows=pairs,first_split=dict(first,species=species,daughters=daughter,closure_mol=closure))

def amp(s,replay):
    old=s.read('analyses/round_3/results/q1.json')['rows']
    matched_rows={q['identity']:q for q in s.read(AMP5+'crosswalk.json.gz')['rows']}
    search=s.read(AMP5+'phase-controls.json.gz')
    assessment={q['identity']:q for q in s.core('AMP/free/assessment.json.gz')['rows']}
    rows=[dict(key=q['key'],historical=q['free'],historical_search=next(x['free']['P_Pa'] for x in old if x['key']==q['key']
               and x['pressure_basis']=='archived search pressure'), crosswalk=matched_rows[q['key'].removesuffix(':problem')],
               adopted_bubble=assessment[q['key'].removesuffix(':problem')], adopted=replay['rows'].get(q['key']))
          for q in old if q['pressure_basis']=='measured pressure']
    assert all(r['historical']['P_Pa']==r['crosswalk']['observed']==r['adopted_bubble']['observed'] for r in rows)
    for row in rows:
        result = (row['adopted'] or {}).get('value',{})
        row['outcome'] = phase_outcome(result)
    confirmed=sum(r['outcome']=='confirmed split' for r in rows)
    return 'narrowed claim',f'{confirmed} of {len(rows)} comparisons confirm an adopted two-liquid split. Grid conclusions apply to the declared searches.',         dict(rows=rows, archived_design=search['original_free'], worked_state=s.display('amp-common-pressure')['outcomes'],
             added_pressure_rows=Counter(q['group'] for q in assessment.values() if q['group'] in ('tong','hartono-2021-supplemental')),
             hot_original=s.read('analyses/round_3/results/q2.json')['scores'],
             original_R5_control=s.read('analyses/amp_transfer/results/retransfer-412-f2-05e94210/diagnosis/f2-probes.json'),
             original_slope_control=s.read('analyses/round_5/results/D/AMP-original-slope-150.json.gz')['summary'],
             grid={k:s.core(f'AMP/free/{k}-outcome.json.gz')['tally'] for k in ('native','supplied')})

def salts(s,_):
    raw=s.read(SALT+'salt/summary.json')['result']
    rows={(q['salt'],float(q['temperature_K']),float(q['molality'])):q for q in s.read(SALT+'salt/phi-residuals.csv')}
    residuals=[]
    for p in s.read(SALT+'inputs/peiper-pitzer-1982-table6.csv'):
        salt = p['salt']
        T,m = map(float,(p['temperature_K'],p['nominal_molality']))
        target=rows[salt,T,m]
        prior=next(q for q in raw['rows'][salt] if (q['T'],q['m'])==(T,m))
        model,obs=prior.get('value'),prior.get('observed')
        factor={'NaHCO3':1,'Na2CO3':2,'mixed':3}[salt]
        x,y,co2,z=map(float,(p['X2'],p['Y'],p['H2X'],p['Z']))
        closed=(factor*m-y-z)/2 if salt=='NaHCO3' else factor*m-y-2*x
        printed=float(p['phi'])*(factor*m+x+y+co2+z)
        water=-log(float(p['water_activity']))/.01801533
        exact=3*Decimal(p['nominal_molality'])-Decimal(p['Y'])-2*Decimal(p['X2']) if salt=='mixed' else None
        ionic=factor*m+y+(closed+z if salt=='NaHCO3' else x+closed)
        assert (model is None and not target['phi_model']) or (float(target['phi_model'])==model and abs((printed-co2)/ionic-obs)<1e-14)
        residuals.append(dict(p,phi_ionic=obs,model=model,signed_residual=None if model is None else model-obs,
                              signed_percent=None if model is None else 100*(model/obs-1),
                              closure_binary=closed,mixed_closure_decimal=str(exact),status=prior.get('unavailable','available'),
                              phi_times_equilibrium_molality=printed,water_activity_molality=water,
                              signed_print_rounding=printed-water,phi_stoichiometric=water/((factor+({'mixed':2}.get(salt,1)))*m)))
    counts=Counter(q['salt'] for q in residuals if q['model'] is not None)
    assert counts==dict(NaHCO3=45,Na2CO3=45,mixed=39)
    models={}
    archives = {c:s.core(f'C/{c}/search-0.json.gz') for c in ('salt','historical')}
    archives['salt-original'] = s.read(MDEA+'salt-anchored-435/campaign/search-0.json.gz')
    historical=s.read(MDEA+'bounded-binary-411/stability.json')
    old_unavailable=set(historical['grid']['unavailable'])
    old_data={q['key']:q['historical'] for v in s.core('B/census.json.gz')['joins'].values() for q in v}
    archives['historical-original']=[dict(key=q['key'],available=q['key'] not in old_unavailable,
         descent=old_data.get(q['key'],{}).get('descent',False)) for q in archives['historical']]
    assert sum(q['available'] for q in archives['historical-original'])==historical['grid']['available']
    common=set.intersection(*[{q['key'] for q in v} for v in archives.values()])
    def coverage(rows):
        return {k:dict(requested=len(v),available=sum(q['available'] for q in v),descents=sum(q['descent'] for q in v))
                for k,v in (('grid',[q for q in rows if q['key'].startswith('grid:')]),('measured',[q for q in rows if not q['key'].startswith('grid:')]))}
    for c,label in MODELS:
        record=s.core(f'C/{c}/{label}.json.gz')
        target=s.core(f'C/{c}/{"rms" if label=="refit" else "original"}-fixed-pressures.json.gz')
        models[f'{c}/{label}']=dict(objective={k:v['objective'] for k,v in record['objective'].items()},
                                targeted=target['pressure_262_MPa']['outcome'])
        pool = archives.get(c if label=='refit' else c+'-original')
        models[f'{c}/{label}']['phase'] = dict(design=coverage(pool),common_keys=coverage([q for q in pool if q['key'] in common]))
        models[f'{c}/{label}']['confirmed'] = (s.core(f'C/{c}/search-outcome.json.gz')['confirmed'] if label=='refit' else
             s.read(MDEA+'salt-anchored-435/campaign/search-outcome.json.gz')['confirmed'] if c=='salt' else historical['liquid_liquid_splits_among_completed_searches'])
    properties = {k:matched(s,k) for k in ('Kuranov','Ermatchkov','Xiao','Carson')}
    totals, heats = ([properties[k][f'salt/{label}']['matched'] for label in ('incumbent','refit')]
                     for k in ('Kuranov','Carson'))
    mixed_count = sum(q['salt']=='mixed' for q in residuals)
    reason = (f'{counts["mixed"]}/{mixed_count} mixed predictions are available. '
              f"Salt-set AARD changes from {totals[0]['AARD_percent']:.2f}% to {totals[1]['AARD_percent']:.2f}% on "
              f"{totals[0]['available']} matched Kuranov pressures and from {heats[0]['AARD_percent']:.2f}% to "
              f"{heats[1]['AARD_percent']:.2f}% on {heats[0]['available']} matched Carson heats.")
    return 'answered',reason,dict(residuals=residuals,available=counts,models=models,properties=properties)

def terminal_coordinates(fit, label):
    declared = fit['declared']
    values = {q['identity']:q['origin']+q['scale']*u for q,u in zip(declared,fit['optimizer'],strict=True)}
    assert len(values)==len(declared), f'C6 {label}: duplicate coordinate identity'
    # The archived physical vector lists parameter targets first, then reaction coordinates.
    expanded = [values[q['identity']]*factor for q in declared for _,_,factor in q.get('targets',[])]
    expanded.extend(values[q['identity']] for q in declared if 'targets' not in q)
    assert expanded==fit['physical'], f'C6 {label}: archived physical vector disagrees with declared coordinates'
    return values

def endpoints(s,replay):
    keys=('initial_cost','final_cost','physical','declared','status','message','maximum_elapsed_time_seconds')
    pairs={'MDEA':[s.core(f'C/salt/attempts/fit-{i}.json.gz') for i in range(3)],
           'AMP':[s.core(f'AMP/free/fit-{i}.json.gz') for i in range(2)],
           'MEA #435':[s.read(MEA+f'{label}/stage-0/fit.json')['result'] for label in ('F2','F4')]}
    selected = s.core('C/salt/selection.json.gz')['selected'][2]
    grid = s.core('C/salt/search-outcome.json.gz')
    pressures = [next(q['pressure_Pa'] for q in grid['classifications'] if q['key'] in grid['confirmed'])]
    pressures.append(s.core('C/salt/rms-fixed-pressures.json.gz')['pressure_262_MPa']['P_Pa'])
    outstanding = {q['key']:q['reason'] for q in replay['outstanding']}
    unavailable = {}
    out={}
    for name,pool in pairs.items():
        fits=[q.get('outcome.json',q).get('report',q) for q in pool]
        inventory=[]
        for i,(archive,q) in enumerate(zip(pool,fits,strict=True)):
            entry = {k:q[k] for k in keys if k in q}
            label = ('F2','F4')[i] if name=='MEA #435' else f'fit-{i}'
            entry.update(endpoint=label, initial_physical=[v['origin'] for v in q['declared']], phase={})
            phase_keys = [f'{name}-{i}'] if name=='AMP' else [f'MEA-{label}']
            if name=='MDEA':
                stage, start = archive['stage-0/fit.json'],archive['start.json']['coordinates']
                assert [v['identity'] for v in start]==[v['identity'] for v in q['declared']]
                assert archive['stage-1/fit.json']['physical']==q['physical']
                entry.update(initial_cost=stage['initial_cost'], initial_physical=[v['origin'] for v in start],
                             start_replay_cost=archive['start-replay.json']['cost'],
                             terminal_stage_initial_cost=q['initial_cost'], stage_0_physical=stage['physical'],
                             stage_0_final_cost=stage['final_cost'], stage_0_status=stage['status'],
                             stage_0_message=stage['message'], adopted=archive['outcome.json']['point']==selected)
                phase_keys = [f'MDEA-{i}:{p}' for p in pressures] if i<2 else []
            for key in phase_keys:
                row = replay['rows'].get(key,{})
                if 'value' in row:
                    value = row['value']
                    if name=='MDEA':
                        assert value['P_Pa']==float(key.split(':',1)[1])
                    phase = dict(outcome=phase_outcome(value), P_Pa=value['P_Pa'],
                                 attempts=value.get('attempts',[]), search=value.get('search'))
                    if phase['outcome'] in ('unavailable','unresolved','unresolved phase identity'):
                        unavailable[key] = value.get('status',value.get('search',{}).get('message'))
                else:
                    cause = row.get('refusal') or outstanding.get(key) or 'missing replay'
                    phase = dict(outcome='refused' if 'refusal' in row else 'outstanding', cause=cause)
                    unavailable[key] = cause
                entry['phase'][key] = phase
            inventory.append(entry)
        first, second = (terminal_coordinates(fit,f"{name} {entry['endpoint']}")
                         for fit,entry in zip(fits[:2],inventory[:2],strict=True))
        assert first.keys()==second.keys(), f'C6 {name}: endpoint coordinate identities differ'
        changes = []
        for q in fits[0]['declared']:
            identity, bounds = q['identity'], q['bounds']
            a,b = first[identity], second[identity]
            changes.append(dict(identity=identity,change=b-a,box_scaled=(b-a)/(bounds[1]-bounds[0]),
                                bounds=bounds,active=[min(abs(v-x) for x in bounds)<=1e-6*q['scale'] for v in (a,b)]))
        out[name]=dict(inventory=inventory, coordinate_changes=changes)
    fit_rows = {'MEA #435':[s.read(MEA+f'{label}/replay.json')['rows'] for label in ('F2','F4')]}
    for family in ('MDEA','AMP'):
        paths = pairs[family][:2]
        fit_rows[family] = []
        for p in paths:
            if family=='MDEA':
                fit_rows[family].append(p[sorted(k for k in p if k.endswith('/replay.json'))[-1]])
            else:
                props = p['start_replay']['rows']
                vals = p['report']['predictions']
                fit_rows[family].append([dict(q,value=v,cost=w*w/2) for q,v,w in zip(props,vals,p['report']['weighted_residuals'],strict=True)])
    for family,(a,b) in fit_rows.items():
        assert [(q['identity'],q['observed']) for q in a]==[(q['identity'],q['observed']) for q in b]
        out[family]['matched_properties'] = {group:[dict(scores([q for q in p if q['group']==group]),
              cost=fsum(q.get('cost',0) or 0 for q in p if q['group']==group)) for p in (a,b)] for group in sorted({q['group'] for q in a})}
        out[family]['paired_changes'] = {q['identity']:v['value']-q['value'] for q,v in zip(a,b,strict=True)
                                          if q['value'] is not None and v['value'] is not None}
    out['MEA #435']['finite_searches']={label:s.read(MEA+f'{label}/search/summary.json')['result'] for label in ('F2','F4')}
    out['round7_F4_display_excluded']=s.display('mea-heat-sensitivity')['sources']
    adopted, = (q for q in out['MDEA']['inventory'] if q['adopted'])
    reason = []
    for key,result in adopted['phase'].items():
        pressure = float(key.split(':',1)[1])/1e6
        reason.append(f"Adopted MDEA {adopted['endpoint']} at {pressure:.3f} MPa: {result['outcome']}.")
    return ('undecided' if unavailable else 'narrowed claim'), ' '.join(reason), dict(out,unavailable=unavailable)

def literature(s,replay):
    row=s.core('H/kuranov-82nd.json')
    population=s.read(MDEA+'salt-anchored-435/kuranov-matched-pressure.json.gz')['rows']
    assert len(population)==len({q['source_row'] for q in population})==82
    pressure=s.display('kuranov-row-72')['prediction']
    fit={q['row']['source_row']:q for q in s.core('C/salt/refit.json.gz')['rows'] if q['group'] in ('Kuranov','Kuranov-binary','Kuranov-413K')}
    readback = replay['rows']['kuranov:72']['value']
    assert (readback['row']['source_row'],readback['unit'],readback['observed']) == (
        pressure['row']['source_row'],pressure['unit'],pressure['observed'])
    current=[pressure if q['source_row']==72 else fit[str(q['source_row'])] for q in population]
    assert all(p['observed']==q['p_exp'] for p,q in zip(current,population,strict=True))
    hong=s.core('H/hong-S31.json.gz')['rows']
    inside=[q for q in hong.values() if q['block']=='canonical' and q['inside_hong_grid']=='True']
    failed=sum(q['stability']=='locally unstable' for q in inside)
    assert len(inside)==132 and failed==131
    kamps = matched(s,'corrected-Kamps')
    common, = {len(q['common_keys']) for q in kamps.values()}
    return 'answered',f'Kuranov AARD is {scores(current)["AARD_percent"]:.2f}% on {len(current)} matched rows. The corrected Kamps pool has {common} common keys. Hong fails local stability at {failed}/{len(inside)} equal-fugacity states.',         dict(kuranov=dict(source_rows=[q['source_row'] for q in population],current=scores(current),additional_row=row['row'],
                          readback=readback,readback_minus_archived_Pa=readback['value']-pressure['value'],
                          published={'Uyan':22.9,'Wangler':19.7,'Raeispour Shirazi and Lotfollahi':10.9,'Zhang and Chen':6.8}),
             kamps=kamps,published_Kamps_28={'Ermatchkov I':1.9,'Ermatchkov II':3.5},
             hong=dict(vapor_amount_fraction_of_feed=1e-9,inside_count=len(inside),local_failures=failed,
                       matched_scores={k:scores([dict(value=float(q[k]),observed=float(q['observed'])) for q in inside])
                                       for k in ('predicted','adopted','polley_hedengren_2026')},
                       rows=hong),published_table_snapshot=DISPLAY)
