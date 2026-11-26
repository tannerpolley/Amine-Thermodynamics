"""Recompute #440 comparisons from the archived and fixed-reference contributors."""
# ruff: noqa: E402
from collections import Counter
from ast import literal_eval
from functools import cache
from hashlib import sha256
import json
from math import fsum, log, sqrt
import sys

from refit import (BASE, COUNTS, HERE, OUT, P_REF, REPLAY_TOLERANCE, configured, fingerprint, r,
                   remove_reference_pressure, row_manifest, rms, save, starts, start_vector, qmc, SEED, np)
from round_8.records import NAMES, blob
from reference_states_428 import ROW_TOLERANCE, phase_closure, scaled_pressure_error
from round_8.reductions import (
    CONNECTED_VAPOR, FINITE_NEGATIVE, TWO_LIQUIDS, no_descent, parent_agreement,
    phase_outcome, qualifying_pair, supplied_complete, vapor_trace_passes, witness_direction,
)

HANDOFF = HERE/'manuscript-handoff.json'
R7 = 'analyses/round_7/'
R8 = 'analyses/round_8/'


def original(path):
    return json.loads(blob(path,BASE))


@cache
def archived(path):
    assert (r.ROOT/path).read_bytes()==blob(path,BASE), f'changed archived contributor: {path}'
    return r.read(r.ROOT/path)


def available(q):
    return q.get('status')=='Available' and q.get('requested_tolerance_met',True) and q.get('value') is not None


def mdea_outcome(q, bank_size):
    from part_ii import stable

    key, pressure, tolerance = q['key'], q['P_Pa'], q['row_tolerance']
    assert tolerance==ROW_TOLERANCE and phase_closure(q['parent'],pressure,tolerance,temperature=q['T_K']), (
        f'{key}: trial-call and Gibbs parent closure')
    native = q['native_trials']
    supplied = q['supplied_witnesses']
    detected = any(t['descent'] for t in native) or any(map(stable.supplied_negative,supplied))
    result = None
    if detected:
        g, error = q['parent_gibbs_RT_mol']
        for field, vapor, outcome, gibbs, pair_error in (
            ('two_liquid',False,TWO_LIQUIDS,'Gibbs_sum_over_RT_mol','split_numerical_error_over_RT_mol'),
            ('liquid_vapor',True,CONNECTED_VAPOR,'Gibbs_over_RT_mol','error'),
        ):
            pair = q.get(field)
            if not pair or not qualifying_pair(pair,pressure,tolerance,vapor=vapor):
                continue
            assert (pair['T_K'],pair['pressure_Pa'],pair['feed_mol'])==(q['T_K'],pressure,q['feed_mol']), (
                f'{key}: pair state identity')
            assert pair['Gibbs_decrease_over_RT_mol']==g-pair[gibbs], f'{key}: Gibbs decrease'
            assert pair['numerical_error_over_RT_mol']==error+pair[pair_error], f'{key}: Gibbs error'
            result = result or outcome
        assert result, f'{key}: detected descent has no qualifying pair'
    native_complete = no_descent(q['native_completed'] and q['native_message'].endswith('unresolved trials 0'),native)
    supplied_done = supplied_complete(q['supplied_counts'],q['supplied_excluded'],bank_size)
    return phase_outcome(dict(key=key,parent_closed=True,native_complete=native_complete,supplied_complete=supplied_done,
                              descent=detected,pair=result),completion=True)


def mdea_bubble_comparison(q):
    from classify_descents import distinct_phases

    key, b = q['key'], q.get('bubble') or {}
    assert b.get('T_K')==q['T_K'] and b.get('feed_mol')==q['feed_mol'], f'{key}: bubble feed or temperature'
    amounts = b['amounts_mol']
    assert amounts==[p['amount_mol'] for p in b['phases']] and len(amounts)==2 and amounts[0]>0 and amounts[1]==0, (
        f'{key}: bubble amount')
    pressure, tolerance = b['pressure_Pa'], q['row_tolerance']
    assert b['requested_tolerance_met'] and tolerance==b['row_tolerance'] and phase_closure(b,pressure,tolerance), (
        f'{key}: bubble closure')
    assert vapor_trace_passes(b), f'{key}: bubble vapor trace'
    assert distinct_phases([p['x'] for p in b['phases']],
                           [p['density_mol_m3'] for p in b['phases']]), f'{key}: bubble phase distinctness'
    pair = q['liquid_vapor']
    return dict(imposed_Pa=q['P_Pa'],bubble_Pa=pressure,below=q['P_Pa']<pressure,
                decrease=pair['Gibbs_decrease_over_RT_mol'],error=pair['numerical_error_over_RT_mol'])


def mdea_grid_membership(row, path, ceiling):
    points = path['points']
    cutoff = next((p for p in points if p['pressure_Pa']>ceiling),None)
    loading = row['a']
    assert (row['stock'],row['T'])==(path['stock'],path['T_K']), f"{row['key']}: grid stock or temperature"
    if cutoff and loading>=cutoff['loading']:
        assert row['domain']=='outside' and row['cutoff']==cutoff, f"{row['key']}: cutoff point"
    elif point := next((p for p in points if p['loading']==loading),None):
        assert row['domain']=='inside' and row['marched_pressure_Pa']==point['pressure_Pa'], f"{row['key']}: marched pressure"
    else:
        assert row['domain']=='unassigned' and row['blocker']==path['stall'] and path['stall'], f"{row['key']}: unreached loading"
    return row['domain']


def march_connections(paths):
    from phase_replays import check_cold_point, check_reverse_connection, reverse_errors

    maximum_errors, connected = Counter(), 0
    for path in paths:
        for previous, point in zip(path['points'],path['points'][1:]):
            if point.get('start')!='cold':
                continue
            warm = path['warm_failures'][point['warm_failure']]
            check_cold_point(point,previous,path['stock'],path['T_K'],warm['target'],ROW_TOLERANCE)
            reverse = point['reverse']
            returned = reverse['returned']
            first, last = reverse['attempts'][0], reverse['attempts'][-1]
            assert first['from_loading']==point['loading'] and last['loading']==previous['loading'] and last['converged']
            assert reverse['stop'] is None and phase_closure(returned,returned['pressure_Pa'],ROW_TOLERANCE)
            errors = reverse_errors(previous,returned)
            assert reverse['errors']==errors, 'stored reverse branch errors'
            check_reverse_connection(errors)
            for key,value in errors.items():
                maximum_errors[key] = max(maximum_errors[key],value)
            connected += 1
    return connected, maximum_errors


def mdea_record_identity(data, endpoint, wheel, bank, *, computed=True):
    assert (data['endpoint_fingerprint'],data['wheel'],data['bank_fingerprint'])==(endpoint,wheel,bank), (
        'MDEA endpoint, wheel or supplied bank identity')
    if computed:
        assert all(row.get('wheel')==wheel for row in data['rows']), 'MDEA worker wheel identity'


def mdea_measured(rows, aliases, prior, bank_size):
    outcomes = {k:mdea_outcome(q,bank_size) for k,q in rows.items()}
    outcomes.update((k,outcomes[v]) for k,v in aliases.items())
    assert outcomes['fit:126:cap']==FINITE_NEGATIVE and outcomes['comparison:157:problem']==CONNECTED_VAPOR, (
        'MDEA pinned completion cases')
    excluded = {aliases.get(k,k) for k,q in prior.items() if not q['available'] and q['status']=='Available'}
    assert len(excluded)==26 and all(
        rows[k]['supplied_excluded']==2057 and rows[k]['supplied_counts']=={'evaluated':923} for k in excluded), (
        'MDEA CO₂-free supplied support census')
    cap = rows[aliases.get('comparison:362:cap','comparison:362:cap')]['capped_feed']
    crossing = next((a,b) for a,b in zip(cap['nodes'],cap['nodes'][1:])
                    if a['pressure_Pa']<=cap['target_Pa']<b['pressure_Pa'] and min(a['slope_Pa'],b['slope_Pa'])>0)
    assert (cap['bracket']==[q['loading'] for q in crossing] and cap['bracket'][0]<=cap['root']<=cap['bracket'][1]
            and cap['loading']==min(cap['source_cap'],cap['root']) and round(cap['loading'],6)==1.145715), (
        'MDEA comparison:362 positive-slope bracket or source cap')
    detections = {k for k,result in outcomes.items() if result==CONNECTED_VAPOR}
    assert detections=={k for k,q in prior.items() if q['descent']} and len(detections)==80, '80 MDEA detections'
    tied = {aliases.get(k,k) for k,q in prior.items() if q['status']=='CentralSolveUnavailable'}
    full = Counter('native descent' if any(t['descent'] for t in rows[k]['native_trials']) else
                   'supplied descent' if outcomes[k]==CONNECTED_VAPOR else 'finite negative' for k in tied)
    assert full=={'native descent':19,'supplied descent':4,'finite negative':3} and all(
        not rows[k]['native_message'].endswith('unresolved trials 0') for k in tied
        if outcomes[k]==CONNECTED_VAPOR and not any(t['descent'] for t in rows[k]['native_trials'])), (
        'MDEA Full trial decisions')
    comparisons = {k:mdea_bubble_comparison(q) for k,q in rows.items() if outcomes[k]==CONNECTED_VAPOR}
    assert len(comparisons)==27, '27 distinct MDEA decision-A feeds'
    return dict(outcomes=outcomes,counts=Counter(outcomes.values()), full_trial_decisions=full,
                bubble_comparisons=comparisons, formerly_unavailable=Counter(outcomes[k] for k,q in prior.items() if not q['available']))


def mdea_pressure_stats(rows):
    checks = Counter()
    for q in rows:
        for field in ('parent','liquid_vapor','bubble','two_liquid'):
            value = q.get(field,{})
            phases = (value.get('diagnostics') or {}).get('phases',[]) if field=='two_liquid' else value.get('phases',[])
            if phases:
                assert all('relative_pressure_residual' in p for p in phases), f"{q['key']}: raw ΔP/P"
                checks[field+'_phases'] += len(phases)
                name = field+'_maximum_scaled_pressure_error'
                checks[name] = max(checks[name],*(scaled_pressure_error(
                    p['pressure_residual_Pa'],p['density_mol_m3'],p['T_K']) for p in phases))
    return checks


def comparison_outcome(row, search, bank_size):
    from phase_replays import OUTSIDE_INCOMPLETE
    from part_ii import stable

    if row['domain']=='unassigned':
        return None, dict(message='loading march did not reach or pass the state')
    if search.get('blocker'):
        if row['domain']=='outside' and 'P_Pa' not in search and search.get('pressure_reference_message'):
            return OUTSIDE_INCOMPLETE, None
        return None, dict(message=search['blocker'])
    try:
        return mdea_outcome(search,bank_size), None
    except (AssertionError,KeyError) as error:
        native = search.get('native_trials',[])
        details = [dict(seed=t['seed'],evidence=t['evidence'],message=t['message']) for t in native
                   if not no_descent(True,[t]) and not t['descent']]
        witness = any(t['descent'] for t in native) or any(map(stable.supplied_negative,search.get('supplied_witnesses',[])))
        blocker = dict(message=str(error),native_message=search.get('native_message'),trials=details)
        if native and not witness and (details or not search['native_completed']):
            blocker['engine_issue'] = 'tannerpolley/epcsaft#266'
        return None, blocker


def comparison_split_check(inventory, searches, outcomes, splits):
    from phase_replays import SPLIT_PRESSURES

    assert len(splits)==2 and 'comparison:363:final' in splits, 'two low-k control keys'
    controls = {}
    for key in splits:
        row, q = inventory[key], searches[key]
        grid = key.startswith('grid:')
        pressure = SPLIT_PRESSURES[grid]
        assert q['P_Pa']==row['declared_pressure_Pa']==pressure, f'{key}: split control pressure'
        assert row['domain']==('outside' if grid else 'not applicable'), f'{key}: split control domain'
        assert outcomes[key]==TWO_LIQUIDS, f'{key}: two-liquid split replay'
        pair = q['two_liquid']
        controls[key] = dict(T_K=q['T_K'],P_Pa=pressure,domain=row['domain'],amounts_mol=pair['amounts_mol'],
                             densities_mol_m3=pair['densities_mol_m3'],Gibbs_decrease_over_RT_mol=pair['Gibbs_decrease_over_RT_mol'],
                             numerical_error_over_RT_mol=pair['numerical_error_over_RT_mol'])
    return controls


def comparison_consumed(row, search, spec, route):
    from part_ii import eq
    from reference_states_428 import balances

    key, ids = row['key'], spec.parameters.component_ids
    if 'P_Pa' not in search:
        return
    if 'stock' in row:
        feed = dict(row['stock'],**{'carbon-dioxide':row['a']*row['stock'][route.config['amine']]})
        T = row['T']
        pressure = row.get('declared_pressure_Pa',row['c']*search['pressure_reference_Pa']
                           if 'pressure_reference_Pa' in search else None)
        if row['domain']=='inside':
            assert search['pressure_reference_Pa']==row['marched_pressure_Pa'], f'{key}: marched search pressure'
    elif 'cap_record' in row:
        cap = search['capped_feed']
        record = next(q for role in ('fitted','comparisons') for q in spec.inputs['observations'][role]
                      if q['identity']==row['cap_record'])
        parent, args = spec.problems[record['initial']],record['arguments']
        crossing = next((a,b) for a,b in zip(cap['nodes'],cap['nodes'][1:])
                        if a['pressure_Pa']<=args['P']<b['pressure_Pa'] and min(a['slope_Pa'],b['slope_Pa'])>0)
        assert (cap['target_Pa']==args['P'] and cap['source_cap']==args['loading_cap']
                and cap['bracket']==[q['loading'] for q in crossing] and cap['bracket'][0]<=cap['root']<=cap['bracket'][1]
                and cap['loading']==min(cap['source_cap'],cap['root'])), f'{key}: capped feed bracket'
        feed = {c:n+cap['loading']*(args['basis_amount']*args['feed'].get(c,0.)) for c,n in parent.feed.values.items()}
        T, pressure = parent.T, parent.P
    else:
        parent = spec.problems[row['problem']]
        feed, T, pressure = parent.feed.values, parent.T, parent.P
        if isinstance(pressure,eq.Free) or row.get('compressed'):
            pressure = row.get('c',1.05)*search['pressure_reference_Pa']
    feed = [feed.get(c,0.) for c in ids]
    assert (T,pressure,feed)==(search['T_K'],search['P_Pa'],search['feed_mol']), (
        f'{key}: consumed comparison state')
    formulas = [spec.spec['element_formulas'][c] for c in ids]
    for value in (search.get('parent'),search.get('liquid_vapor'),search.get('two_liquid',{}).get('diagnostics')):
        if value and (phases := value.get('phases')):
            assert value['balances']==balances(feed,phases,formulas), f'{key}: comparison material balance'
            assert all(p['T_K']==T and p['charge_residual']==fsum(x*f['charge'] for x,f in zip(p['x'],formulas,strict=True))
                       for p in phases), f'{key}: comparison charge or temperature'


def summary(rows, pressure=False):
    good = [q for q in rows if available(q)]
    ratios = [q['value']/q['observed'] for q in good if q['observed']]
    result = dict(rows=len(rows),available=len(good),point_count=len(ratios),
                  fitted=sum(q.get('role')=='fitted' for q in rows))
    if ratios:
        result.update(AARD_percent=100*fsum(abs(x-1) for x in ratios)/len(ratios),
                      bias_percent=100*fsum(x-1 for x in ratios)/len(ratios))
        signed = [q['value']-q['observed'] for q in good]
        result.update(mean_abs_error=fsum(map(abs,signed))/len(signed),
                      mean_signed_error_predicted_minus_observed=fsum(signed)/len(signed))
        if pressure and all(x>0 for x in ratios):
            result['log_RMSE'] = sqrt(fsum(log(x)**2 for x in ratios)/len(ratios))
    return result


class Quantities:
    def __init__(self):
        self.items = {}
        self.files = {}
        self.attempts = {}
        self.selections = {}
        self.old = original(R7+'manuscript-handoff.json')['quantities']

    def read(self, path):
        if path not in self.files:
            absolute = OUT/path
            self.files[path] = (r.read(absolute), sha256(absolute.read_bytes()).hexdigest()) if absolute.is_file() else (None,None)
        return self.files[path][0]

    def reference(self,path):
        return dict(path=str((OUT/path).relative_to(r.ROOT)),sha256=self.files[path][1])

    def quantity(self,key,old,new,*,unit='1',population=None,pressure_basis=None,sources=(),old_source=None,
                 old_field=None,endpoint=None,independent=False,disposition=None):
        source = {'revision':BASE,'path':old_source,'field':old_field,
                  'sha256':sha256(blob(old_source,BASE)).hexdigest() if old_source else None}
        refs = [self.reference(p) for p in sources]
        numerical = disposition!='different available populations' and all(
            isinstance(x,(int,float)) and not isinstance(x,bool) for x in (old,new))
        changed = new-old if numerical else None
        self.items[key] = dict(old=old,new=new,unit=unit,population=population,pressure_basis=pressure_basis,
                               absolute_change=changed,percent_change=100*changed/old if numerical and old else None,
                               transition=[old,new] if isinstance(old,str) and new is not None else None,
                               disposition=disposition or ('independent contributor' if independent else 'open' if new is None else 'replayed'),
                               old_contributor=source,new_contributors=refs,endpoint_fingerprint=endpoint)

    def fit(self,design):
        base = f'{design}/reference-control.json.gz'
        control = self.read(base)
        if control is None:
            return
        manifests = f'{design}/manifest.json.gz'
        declaration = self.read(manifests)
        archived = control['source']
        old = self.cost(control['tracking'],f'{design} tracking objective')
        fixed = self.cost(control['fixed_at_old_parameters'],f'{design} objective at old parameters')
        assert abs(old-archived['objective'])<=REPLAY_TOLERANCE[design]*abs(old), f'{design} tracking objective'
        share = dict(population=dict(fitted=COUNTS[design],comparison=0),old_source=archived['path'])
        self.quantity(f'{design} objective at old parameters',old,fixed,sources=(base,),**share)
        if declaration is None:
            return
        assert declaration['wheel']==r.SHA and declaration['engine_commit']==r.COMMIT
        assert declaration['source']==archived and declaration['fixed_reference_pressure_pa']==P_REF
        tracking,old_point,_ = configured(design,'handoff-tracking',fixed=False)
        new,point,_ = configured(design,'handoff-fixed')
        old_rows,fixed_rows = row_manifest(tracking.bind(old_point)),row_manifest(new.bind(point))
        assert fingerprint(old_rows)==declaration['tracking_row_fingerprint'], f'{design} tracking fitted declaration'
        assert fingerprint(fixed_rows)==declaration['fixed_row_fingerprint'], f'{design} fixed fitted declaration'
        assert remove_reference_pressure(old_rows)==remove_reference_pressure(fixed_rows), f'{design} fitted row invariants'
        spec = new.bind(declaration['start_A_declaration'])
        assert declaration['rows']==row_manifest(spec), f'{design} bound manifest'
        actual_starts,_ = starts(spec)
        assert actual_starts==declaration['starts'], f'{design} Engine start readbacks'
        if design!='MEA':
            donor = declaration['donor']
            donor_path = f'MEA/{self.selections["MEA"][0]}.json.gz'
            donor_record = self.read(donor_path)
            assert donor['endpoint']==donor_record['endpoint_fingerprint'] and donor['sha256']==r.s.sha256(OUT/donor_path), f'{design} MEA donor'
            assert donor['parameter_sha256']==fingerprint(donor_record['endpoint']['parameters']), f'{design} donor parameters'
            self.quantity(f'{design} donor binding',None,dict(donor,salt_pairs=declaration['salt_pairs']),
                          sources=(manifests,donor_path),endpoint=donor['endpoint'])
        distances = {pair:sqrt(fsum((x-y)**2 for x,y in zip(
            declaration['starts'][pair[0]]['normalized'],declaration['starts'][pair[1]]['normalized'],strict=True))/
            len(declaration['coordinate_order'])) for pair in ('AB','AC','BC')}
        assert all(abs(v-declaration['pair_rms_distances'][k])<=4e-16 and v>=.2 for k,v in distances.items())
        self.quantity(f'{design} start distances',None,distances,sources=(manifests,))
        replacement_path = f'{design}/replacement-starts.json.gz'
        replacement = self.read(replacement_path)
        if replacement:
            assert replacement['wheel']==r.SHA and replacement['manifest_fingerprint']==fingerprint(declaration)
            accepted = {k:actual_starts[k] for k in replacement['accepted_original']}
            assert list(accepted)==[k for k in 'ABC' if self.read(f'{design}/{k}.json.gz')['report']['status']
                                    !='initial_evaluation_failed']
            native = spec.coordinates()
            lower,upper = (np.array([getattr(q,k) for q in native]) for k in ('lower','upper'))
            candidates = qmc.LatinHypercube(d=len(native),seed=SEED).random(64)
            remaining = set(range(64))-{q['draw'] for q in actual_starts.values()}
            for label,item in replacement['draws'].items():
                d = np.min([rms(candidates,v['normalized']) for v in accepted.values()],axis=0)
                i = max(remaining,key=lambda j:(d[j],-j))
                remaining.remove(i)
                vector = start_vector(spec,i,lower+(upper-lower)*candidates[i])
                separation = {k:float(rms(vector['normalized'],v['normalized'])) for k,v in accepted.items()}
                assert label==f'LHS-{i:02d}' and vector==item['start'], f'{design} {label} Latin hypercube readback'
                assert min(separation.values())>=.20 and separation==item['pair_rms_distances'], f'{design} {label} start separation'
                valid = item.get('statuses')==['Available']*COUNTS[design] and len(item.get('predictions',[]))==COUNTS[design]
                assert valid==(item['disposition']=='eligible'), f'{design} {label} initial evaluation'
                evaluation = {k:v for k,v in item.items() if k not in ('statuses','predictions')}
                evaluation['available_rows'] = item.get('statuses',[]).count('Available') if valid else None
                self.quantity(f'{design} {label} start screening',None,evaluation,unit='residual evaluation',
                              sources=(manifests,replacement_path),
                              disposition='replayed' if valid else 'refused at initial evaluation')
                if valid:
                    accepted[label] = actual_starts[label] = vector
            if 'exhausted' in replacement:
                assert replacement['accepted']==list(accepted) and replacement['remaining']==sorted(remaining)
                if replacement['exhausted']:
                    assert len(accepted)<3 and all(min(rms(candidates[i],v['normalized']) for v in accepted.values())<.20
                                                   for i in remaining), f'{design} premature LHS exhaustion'
            self.quantity(f'{design} admitted-start distances',None,
                          {x+'/'+y:float(rms(accepted[x]['normalized'],accepted[y]['normalized']))
                           for j,x in enumerate(accepted) for y in list(accepted)[j+1:]},
                          sources=(manifests,replacement_path))
        attempts, eligible = {}, {}
        for label in (*actual_starts,*(['A-loose'] if design=='MEA' else [])):
            path = f'{design}/{label}.json.gz'
            q = self.read(path)
            if q is None:
                self.quantity(f'{design} {label} fit',None,None,sources=(manifests,replacement_path),
                              disposition='open')
                continue
            start = 'A' if label=='A-loose' else label
            assert q['start']==label and q['optimizer_start']==actual_starts[start]['optimizer'], f'{design} {label} start identity'
            assert q['manifest_fingerprint']==fingerprint(declaration) and q['wheel']==r.SHA, f'{design} {label} manifest'
            report = q['report']
            cost, replay_pass, endpoint = None, False, q.get('endpoint_fingerprint')
            if endpoint:
                assert endpoint==fingerprint(q['endpoint']), f'{design} {label} endpoint fingerprint'
                assert all(rx['reference']['reference_pressure_pa']==P_REF
                           for group in q['endpoint']['reactions'].values() for rx in group), f'{design} {label} references'
            if q.get('replay'):
                cost = self.cost(q['replay'],f'{design} {label} objective')
                native = report['data_cost'] if report['data_cost'] is not None else report['final_cost']
                replay_pass = cost is not None and abs(cost-native)<=REPLAY_TOLERANCE[design]*abs(native)
                assert replay_pass==q.get('replay_passed'), f'{design} {label} independent objective replay'
            grad_norm, active, solver_gradient = self.stationarity(q)
            gradient_tolerance = q['controls']['gradient_tolerance']
            if solver_gradient is not None:
                native_gradient = report['covariance']['projected_gradient_norm']
                assert abs(solver_gradient-native_gradient)<=1e-8, f'{design} {label} optimizer gradient replay'
            probe_path = f'{design}/stationarity/{label}.json.gz'
            probe = self.read(probe_path)
            if probe and probe['endpoint']==endpoint:
                for j,t in enumerate(probe['trials']):
                    trial_cost = self.cost(t['replay'],f'{design} {label} descent probe {j}') if 'replay' in t else None
                    assert t['relative_reduction']==((cost-trial_cost)/cost if trial_cost is not None else None)
                self.quantity(f'{design} {label} descent probe',None,
                    dict(predicted=probe['relative_linearized_reduction'],
                         measured=[t['relative_reduction'] for t in probe['trials']]),
                    sources=(path,probe_path),endpoint=endpoint)
            chain = [q]
            while 'previous_stage' in chain[-1]:
                chain.append(chain[-1]['previous_stage'])
            chain.reverse()
            start_report = chain[0]['report']
            stages = [dict(status=v['report']['status'],initial_cost=v['report']['initial_cost'],
                           objective=(v.get('replay') or {}).get('cost'),iterations=v['report']['iterations'],
                           fit_seconds=v['fit_seconds'],replay_seconds=v.get('replay_seconds'),
                           diagnostic_seconds=v.get('diagnostic_seconds')) for v in chain]
            check_path = f'{design}/initial/{label}.json.gz'
            initial = self.read(check_path)
            attempts[label] = dict(status=report['status'],initial_cost=start_report['initial_cost'] if start_report['residual_evaluations'] else None,
                                   objective=cost,projected_gradient_inf=grad_norm,active_bounds=active,
                                   solver_scale_projected_gradient_inf=solver_gradient,gradient_tolerance=gradient_tolerance,
                                   termination=report['message'],draw=actual_starts[start]['draw'],
                                   stationarity_met=(solver_gradient<=q['controls']['gradient_tolerance']
                                                     if solver_gradient is not None else None),
                                   fit_seconds=fsum(v['fit_seconds'] for v in stages),
                                   replay_seconds=fsum(v['replay_seconds'] or 0. for v in stages) if endpoint else None,
                                   iterations=sum(v['iterations'] for v in stages),failure=report['failures'][:1],endpoint=endpoint,
                                   attempted=(q.get('replay') or (initial or {}).get('replay') or {}).get('attempted'),
                                   refused=(q.get('replay') or (initial or {}).get('replay') or {}).get('refused'),
                                   fit_stages=stages)
            for k in ('status','objective','projected_gradient_inf','solver_scale_projected_gradient_inf','stationarity_met','active_bounds'):
                self.quantity(f'{design} {label} {k}',None,attempts[label][k],sources=(path,manifests)+((replacement_path,) if label.startswith('LHS-') else ()),endpoint=endpoint,
                              disposition='refused at initial evaluation' if report['status']=='initial_evaluation_failed' else None,**share)
            if replay_pass and report['status']=='converged' and label in actual_starts:
                eligible[label] = (cost,q)
        self.attempts[design] = attempts
        selection_path = f'{design}/selection.json'
        selection = self.read(selection_path)
        selected, endpoint, cost = None,None,None
        if selection is not None:
            assert all(k in attempts for k in 'ABC'), f'{design} missing declared attempt'
            best = min((v[0] for v in eligible.values()),default=None)
            tied = [k for k,(v,q) in eligible.items() if abs(v-best)<=declaration['fit_controls']['function_tolerance']*best]
            selected = tied[0] if tied else None
            if selected:
                cost, q = eligible[selected]
                endpoint = q['endpoint_fingerprint']
            assert (selected,tied,endpoint,cost)==(selection['selected'],selection['tied'],selection['endpoint_fingerprint'],
                                                selection['cost']), f'{design} selected objective or endpoint fingerprint'
        self.selections[design] = (selected,endpoint)
        sources = (selection_path,base,manifests)+((f'{design}/{selected}.json.gz',) if selected else ())
        if design=='MDEA' and (OUT/'MDEA/stationarity/A-continuation.json.gz').exists() and selected=='A':
            sources = (*sources,'MDEA/stationarity/A-continuation.json.gz')
            disposition = 'undecided' if self.read(sources[-1])['report']['status']!='converged' else None
        else:
            disposition = None
        self.quantity(f'{design} selected objective',old,cost,sources=sources,endpoint=endpoint,
                      disposition=disposition,**share)
        if selected:
            q = self.read(f'{design}/{selected}.json.gz')
            uncertainty = q['diagnostics'].get('uncertainty',{})
            old_coordinates = {d['identity']:d for d in declaration['prior_declaration']['coordinates']}
            new_coordinates = {d['identity']:d for d in q['endpoint']['coordinates']}
            assert set(old_coordinates)==set(new_coordinates), f'{design} coordinate mapping'
            for k,d in new_coordinates.items():
                old = old_coordinates[k]
                value = old['bounds'][0]-d['bounds'][0] if d.get('kind')=='reaction_enthalpy_shift' else d['origin']
                self.quantity(f'{design} selected parameter {k}',old['origin'],value,
                    sources=sources,endpoint=endpoint,unit=d.get('unit','see bound declaration'),**share)
                if k in uncertainty.get('conditional_standard_error',{}):
                    self.quantity(f'{design} conditional standard error {k}',None,uncertainty['conditional_standard_error'][k],
                                  sources=sources,endpoint=endpoint,unit=d.get('unit','coordinate units'),**share)
            if design in ('DEA','AMP_free','AMP_fixed'):
                spectra = [r.s.parameter_values(v['parameters']) for v in (declaration['prior_declaration'],q['endpoint'])]
                for text,family,unit in (('carbamate energy divided by k','dispersion_energy_over_k','K'),
                                         ('carbamate segment diameter','segment_diameter','Å')):
                    identity = f'component/carbamate-anion/{family}'
                    value = [v[identity] for v in spectra]
                    self.quantity(f'{design} {text}',*value,unit=unit,sources=sources,old_source=archived['path'],endpoint=endpoint)
                if design.startswith('AMP'):
                    identity = 'pair/protonated-aminomethylpropanol/water/k_ij/reciprocal_temperature_slope'
                    values = [v[identity] for v in spectra]
                    self.quantity(f'C4 {design} reciprocal temperature slope',*values,unit='K',
                                  sources=sources,old_source=archived['path'],endpoint=endpoint)
            spreads = {}
            for label,(_cost,record) in eligible.items():
                if label==selected:
                    continue
                other = {row['identity']:row for row in record['replay']['rows']}
                for group in sorted({row['group'] for row in q['replay']['rows']}):
                    left = [row for row in q['replay']['rows'] if row['group']==group]
                    values = [(x['value'],other[x['identity']]['value']) for x in left]
                    spreads[f'{label} {group}'] = dict(rows=len(left),unit=left[0]['unit'],
                        max_absolute=max(abs(x-y) for x,y in values),
                        max_relative=max((abs(y/x-1) for x,y in values if x),default=None))
                differences = {d['identity']:d['origin'] for d in record['endpoint']['coordinates']}
                spreads[f'{label} endpoint coordinate RMS'] = sqrt(fsum(
                    ((d['origin']-differences[k])/(d['bounds'][1]-d['bounds'][0]))**2 for k,d in new_coordinates.items())/len(new_coordinates))
            self.quantity(f'C6 {design} fitted-row endpoint prediction spread',None,spreads,
                          sources=sources+tuple(f'{design}/{k}.json.gz' for k in eligible if k!=selected),
                          population=COUNTS[design],endpoint=endpoint)
            self.quantity(f'C6 {design} endpoint spread versus measurement deviation by operating band',
                          None,None,sources=sources,population=COUNTS[design],endpoint=endpoint)

    @staticmethod
    def cost(data, key):
        rows = data['rows']
        cost = .5*fsum(q['weighted_residual']**2 for q in rows) if all('weighted_residual' in q for q in rows) else None
        assert (cost is None and data['cost'] is None or cost is not None and
                abs(cost-data['cost'])<=1e-14*abs(cost)), f'{key}: changed objective contributor'
        assert len(rows)==data['attempted'] and sum('weighted_residual' not in q for q in rows)==data['refused']
        return data['cost']

    @staticmethod
    def stationarity(q):
        data = q.get('diagnostics',{})
        if 'jacobian_bound_normalized' not in data:
            return None,None,None
        coordinates = q['endpoint']['coordinates']
        rows = q['replay']['rows']
        residual = [r['weighted_residual'] for r in rows]
        products = [[a*b for a,b in zip(col,residual,strict=True)]
                    for col in zip(*data['jacobian_bound_normalized'],strict=True)]
        gradients = [fsum(col) for col in products]
        bound, projected = {},[]
        for d,g in zip(coordinates,gradients,strict=True):
            lower,upper = d['bounds']
            side = ('lower' if d['origin']-lower<=1e-6*d['scale'] else
                    'upper' if upper-d['origin']<=1e-6*d['scale'] else None)
            if side:
                bound[d['identity']]=side
            projected.append(0. if side=='lower' and g>0 or side=='upper' and g<0 else g)
        norm = max(map(abs,projected))
        # The archived dot uses BLAS summation. Bound its roundoff against the fsum replay.
        n_eps = len(residual)*sys.float_info.epsilon
        roundoff = n_eps/(1-n_eps)*max(fsum(map(abs,col)) for col in products)
        assert bound==data['active_bounds'] and abs(norm-data['projected_gradient_inf'])<=roundoff, q.get('start')
        normalized = [abs(min((d['bounds'][1]-d['origin'])/d['scale'],
                              max((d['bounds'][0]-d['origin'])/d['scale'],
                                  -g*d['scale']/(d['bounds'][1]-d['bounds'][0]))))
                      for g,d in zip(gradients,coordinates,strict=True)]
        return data['projected_gradient_inf'], bound,max(normalized)

    def properties(self,design):
        selected,endpoint = self.selections.get(design,(None,None))
        path = ('E/MEA/replay.json.gz' if design=='MEA' else
                f'{design}/property-comparisons/selected.json.gz'
                if (OUT/f'{design}/property-comparisons/selected.json.gz').exists() else f'{design}/properties.json.gz')
        result = self.read(path)
        if result:
            assert result.get('endpoint_fingerprint',endpoint)==endpoint, f'{design} properties endpoint fingerprint'
            if design=='MEA':
                point = self.read(f'MEA/{selected}.json.gz')['endpoint']
                assert result['summary']['parameter_fingerprint']==r.s.parameter_fingerprint(point['parameters']), 'MEA pressure endpoint'
        folders = {'MEA':('E/incumbent/replay.json.gz','rows'),'DEA':('F/assessment.json.gz','expanded_design'),
                   'MDEA':('C/salt/refit.json.gz','rows'),'AMP_free':('AMP/free/assessment.json.gz','rows'),
                   'AMP_fixed':('AMP/fixed/assessment.json.gz','rows')}
        p,field = folders[design]
        old_file = R7+'results/'+p
        old = archived(old_file)[field]
        new = result['rows'] if result else []
        if design=='MEA':
            old,new = ([dict(q,role='fitted' if i<COUNTS[design] else 'comparison') for i,q in enumerate(pool)]
                       for pool in (old,new))
        groups = sorted({(q['group'],q.get('unit') or 'unspecified') for q in old})
        for group,unit in groups:
            left,right = ([q for q in pool if q['group']==group and (q.get('unit') or 'unspecified')==unit] for pool in (old,new))
            if left and right:
                assert {x['identity']:x['observed'] for x in left}=={q['identity']:q['observed'] for q in right}, f'{design} {group} row keys'
            left_keys,right_keys = ({q['identity'] for q in pool if available(q)} for pool in (left,right))
            for side in ('all','matched') if right else ('all',):
                if side=='matched':
                    keys = left_keys & right_keys
                    left,right = ([q for q in pool if q['identity'] in keys] for pool in (left,right))
                a,b = (summary(pool,pressure=unit=='Pa') if pool else {} for pool in (left,right))
                counts = {k:dict(rows=v.get('rows'),available=v.get('available'),fitted=v.get('fitted'))
                          for k,v in (('old',a),('new',b))}
                for statistic in ('AARD_percent','bias_percent','log_RMSE','available','mean_abs_error',
                                  'mean_signed_error_predicted_minus_observed'):
                    if statistic not in a:
                        continue
                    key = f'{design} {group} {unit} {side} {statistic}'
                    different = side=='all' and left_keys!=right_keys and statistic!='available' and statistic in b
                    self.quantity(key,a[statistic],b.get(statistic),
                        unit='%' if statistic.endswith('percent') else 'rows' if statistic=='available' else
                             unit if 'error' in statistic else '1',
                        sources=(path,),old_source=old_file,old_field=field,population=counts,endpoint=endpoint,
                        disposition='different available populations' if different else None,
                        pressure_basis='source row and observation basis retained; pressure residuals use calculated pressure')
        if design=='DEA' and new:
            for group in ('Lawson','Lawson-394K','SeoHong','Lal','Carson'):
                for law in ('carbamate-hydrolysis','DEA-dissociation'):
                    for outside in (False,True):
                        subsets = [[q for q in rows if q['group']==group and q['outside_ranges'].get(law) is outside]
                                   for rows in (old,new)]
                        before,after = (summary(rows).get('AARD_percent') for rows in subsets)
                        if before is not None:
                            self.quantity(f'DEA {group} {"outside" if outside else "inside"} {law} AARD',before,after,
                                          unit='%',population=len(subsets[0]),sources=(path,),old_source=old_file,endpoint=endpoint,
                                          pressure_basis='source observation pressure; group range checked per reaction')
            count = [sum(q['group']=='Horstmann' and q.get('value') is not None and q['value']>0 and q['observed']<0 for q in rows)
                     for rows in (old,new)]
            self.quantity('DEA Horstmann positive predictions for negative excess enthalpy',*count,unit='rows',
                          sources=(path,),old_source=old_file,endpoint=endpoint)
            density = [q for q in new if q['group']=='Weiland']
            old_density = [q for q in old if q['group']=='Weiland']
            control_path = f'DEA/controls/{selected}.json.gz'
            control = self.read(control_path)
            if control and 'rows' in control:
                keys = {k.removesuffix(':problem') for k in control['rows']}
                for label in ('all 44 density samples','four historically split feeds'):
                    left,right = (pool if label.startswith('all') else [q for q in pool if q['identity'] in keys]
                                  for pool in (old_density,density))
                    self.quantity(f'C3 DEA AARD {label}',summary(left)['AARD_percent'],summary(right)['AARD_percent'],
                                  unit='%',population=len(left),sources=(path,control_path),old_source=old_file,endpoint=endpoint)
            p = 'DEA/screen/selected/declared/summary.json.gz'
            screen = self.read(p)
            if screen:
                baseline = R7+'results/F/search-outcome.json.gz'
                prior = archived(baseline)['confirmed']
                current = [q['key'] for q in screen['classifications'] if any(a['confirmed'] for a in q['attempts'])]
                sets = [{k.removesuffix(':problem') for k in keys} for keys in (prior,current)]
                old_score,new_score = (summary([q for q in rows if q['identity'] in keys])['AARD_percent']
                                       for rows,keys in zip((old_density,density),sets,strict=True))
                self.quantity('C3 DEA AARD on split feeds in each model',old_score,new_score,unit='%',
                              population=dict(old=len(prior),new=len(current),tested_density_rows=44),
                              sources=(path,p),old_source=baseline,endpoint=endpoint,
                              pressure_basis='assigned absolute density-cell pressure')
                self.quantity('C3 DEA split-feed comparison',sorted(prior),sorted(current),unit='state IDs',
                              population=44,sources=(p,),old_source=baseline,endpoint=endpoint,
                              pressure_basis='assigned absolute density-cell pressure')
                point = self.read(f'DEA/{selected}.json.gz')['endpoint']
                species_path = 'analyses/dea_transfer/inputs/part-ii-346/f2-carbamate-413-route.json'
                masses = {q['component_id']:q['fixed']['molar_mass']['value']['magnitude']
                          for q in point['parameters']['components']}
                species = original(species_path)['species']
                for key in sorted(set(prior)|set(current)):
                    identity = key.removesuffix(':problem')
                    left,right = (next(q for q in rows if q['identity']==identity) for rows in (old_density,density))
                    entries = [next((q for q in source if q['key']==key),{})
                               for source in (archived(baseline)['classifications'],screen['classifications'])]
                    values = []
                    for row,entry in zip((left,right),entries,strict=True):
                        states = [dict(density_kg_m3=rho*fsum(masses[k]*x for k,x in zip(species,composition,strict=True)),
                                       mole_fraction=n/fsum(attempt['amounts_mol']))
                                  for attempt in entry.get('attempts',[]) if attempt['confirmed']
                                  for rho,composition,n in zip(attempt['densities_mol_m3'],attempt['phases'],attempt['amounts_mol'],strict=True)]
                        values.append(dict(single_liquid_density=row['value'],observed_density=row['observed'],daughters=states))
                    self.quantity(f'C3 DEA {key} single liquid and daughters',*values,unit='kg/m³ and mole fraction',
                                  sources=(p,path,f'DEA/{selected}.json.gz'),old_source=baseline,endpoint=endpoint,
                                  pressure_basis='assigned absolute density-cell pressure',population=1)
        if design=='MDEA' and new:
            self.mdea_deviations(old,new,path,old_file)
        if design.startswith('AMP') and new:
            added = ('hartono-2021-supplemental','tong')
            counts = [dict(Counter(q['group'] for q in rows if q['group'] in added and q['role']=='fitted'))
                      for rows in (old,new)]
            self.quantity(f'C4 {design} added pressure rows',*counts,unit='rows',population=sum(counts[0].values()),
                          sources=(path,),endpoint=endpoint,old_source=old_file,pressure_basis='measured pressure')

    def mdea_deviations(self,old,new,path,old_file):
        selected,endpoint = self.selections['MDEA']
        for name,groups in (('loaded total',{'Kuranov'}),('all fitted pressures',{'Kuranov','Kuranov-binary','Kim'}),
                            ('development partials',{'Ermatchkov','Xiao'})):
            self.mdea_scores(name,old,new,lambda q:q['group'] in groups,path,old_file,endpoint)
        for outside in (False,True):
            for group in ('Kuranov','Kuranov-413K','Ermatchkov','Xiao','corrected-Kamps','Sedighi','Zheng'):
                self.mdea_scores(f'{group} outside R5 = {outside}',old,new,
                    lambda q:q['group']==group and q['outside_ranges'].get('MDEA-dissociation') is outside,path,old_file,endpoint)
        fit_path = f'MDEA/{selected}.json.gz'
        fitted = {q['identity']:q for q in self.read(fit_path)['replay']['rows']}
        for scoring,objective in archived(old_file)['objective'].items():
            rows = objective['rows']
            assert set(fitted)=={row['identity'] for row in rows}
            costs = [(q['group'],q['cost'],0.5*q['weight']*fitted[q['identity']]['residual']**2) for q in rows]
            totals = [fsum(q[i] for q in costs) for i in (1,2)]
            assert abs(totals[0]-objective['objective'])<1e-10
            self.quantity(f'C5 MDEA salt refit {scoring} objective',*totals,sources=(fit_path,path),
                          old_source=old_file,population=len(rows),endpoint=endpoint)
            for name,groups in (('loaded pressure',{'Kuranov'}),('density',{'loaded-density','unloaded-density'})):
                family = [q for q in costs if q[0] in groups]
                values = [100*fsum(q[i] for q in family)/totals[i-1] for i in (1,2)]
                self.quantity(f'C5 MDEA salt refit {scoring} {name} cost share',*values,unit='%',
                              sources=(fit_path,path),old_source=old_file,population=len(family),endpoint=endpoint)

    def mdea_scores(self,name,old,new,predicate,path,old_file,endpoint):
        left,right = ([q for q in rows if predicate(q)] for rows in (old,new))
        assert {q['identity'] for q in left}=={q['identity'] for q in right}
        if left:
            keys = {q['identity'] for q in left if available(q)} & {q['identity'] for q in right if available(q)}
            a,b = (summary([q for q in rows if q['identity'] in keys],True) for rows in (left,right))
            for metric in ('AARD_percent','bias_percent','log_RMSE','available'):
                values = [sum(map(available,rows)) for rows in (left,right)] if metric=='available' else [a.get(metric),b.get(metric)]
                self.quantity(f'C5 MDEA salt refit {name} {metric}',*values,
                              unit='%' if metric.endswith('percent') else 'rows' if metric=='available' else '1',
                              sources=(path,),old_source=old_file,endpoint=endpoint,
                              population=dict(rows=len(left),matched=len(keys),fitted=a['fitted']),
                              pressure_basis='same source rows; calculated bubble pressure')

    def phases(self,design):
        selected,endpoint = self.selections.get(design,(None,None))
        paths = {'MDEA':R8+'results/C6-replays.json.gz','AMP_free':R8+'results/C4-replays.json.gz',
                 'AMP_fixed':R8+'results/C4-replays.json.gz','DEA':R7+'results/F/search-outcome.json.gz'}
        oldfile = paths.get(design)
        old = archived(oldfile) if oldfile else {}
        old_record = f'{design}/controls/tracking.json.gz'
        tracking = self.read(old_record)
        fixed = self.read(f'{design}/controls/fixed-at-old.json.gz')
        extra = ('A-continuation','A-descent-continuation') if design=='MDEA' else ()
        for label in (*self.attempts.get(design,{}),*extra,'fixed-at-old'):
            path = f'{design}/controls/{label}.json.gz'
            record = self.read(path)
            if not record:
                continue
            if label in extra:
                fit = self.read(f'MDEA/stationarity/{label}.json.gz')
                fingerprint_ = fit['endpoint_fingerprint']
            else:
                fingerprint_ = self.attempts.get(design,{}).get(label,{}).get('endpoint')
            if fingerprint_:
                assert record['endpoint_fingerprint']==fingerprint_,f'{design} {label} phase endpoint fingerprint'
            rows = record.get('rows') or {k:dict(P_Pa=q['P_Pa'],refusal=record.get('refusal'))
                                            for k,q in (fixed or {}).get('rows',{}).items()}
            for key,row in rows.items():
                before = None
                if design=='MDEA':
                    p = min((k for k in old['rows'] if k.startswith('MDEA-0:')),
                            key=lambda k:abs(float(k.split(':')[1])-row['P_Pa']))
                    before = phase_outcome(old['rows'][p].get('value',{}))
                elif design=='AMP_free' and key in old['rows']:
                    before = phase_outcome(old['rows'][key].get('value',{}))
                elif design=='DEA':
                    before = 'confirmed split' if key in old['confirmed'] else None
                if tracking and key in tracking.get('rows',{}):
                    before = phase_outcome(tracking['rows'][key].get('value',{}))
                value = phase_outcome(row['value']) if 'value' in row else (
                    'no endpoint' if not fingerprint_ and label in self.attempts.get(design,{}) else 'unavailable')
                sources = (path,old_record) if tracking else (path,)
                self.quantity(f'{design} {label} phase {key}',before,value,unit='outcome',sources=sources,
                              old_source=oldfile,pressure_basis=dict(type='retained absolute pressure',P_Pa=row['P_Pa']),
                              population=1,endpoint=fingerprint_,
                              disposition='refused at initial evaluation' if value=='no endpoint' else
                              'undecided' if value in ('unavailable','unresolved','unresolved phase identity') else None)
        if design.startswith('AMP') and selected:
            control = f'{design}/controls/{selected}.json.gz'
            keys = old['rows']
            rows = self.read(control)['rows']
            assert len(keys)==6
            outcomes = Counter()
            for key,previous in keys.items():
                assert rows[key]['P_Pa']==previous['value']['P_Pa'], f'{design} {key}: experimental pressure'
                outcomes[self.items[f'{design} {selected} phase {key}']['new']] += 1
            self.quantity(f'C4 {design} selected experimental phase counts',None,dict(outcomes),unit='states',
                          sources=(control,),old_source=oldfile,population=len(keys),endpoint=endpoint,
                          pressure_basis='same six experimental absolute pressures as round 8')
        for path in sorted((OUT/design/'screen/selected').glob('*/summary.json.gz')):
            rel = str(path.relative_to(OUT))
            result = self.read(rel)
            assert result['endpoint_fingerprint']==endpoint, f'{design} screen endpoint fingerprint'
            rows = result['rows']
            classified = {q['key']:q for q in result['classifications']}
            count = Counter()
            for q in rows:
                k = q.get('same_calculation_as',q['key'])
                entry = classified.get(k,{})
                category = ('confirmed split' if any(a['confirmed'] for a in entry.get('attempts',[])) else
                            'unavailable search' if not q['available'] else 'unresolved descent or identity' if q['descent']
                            else 'no resolved descent')
                count[category] += 1
            protocol = path.parent.name
            baseline = (R7+'results/F/search-outcome.json.gz' if design=='DEA' else
                        R7+'results/C/salt/search-outcome.json.gz' if design=='MDEA' else
                        R7+f"results/AMP/{design.split('_')[1]}/{protocol}-outcome.json.gz")
            old = archived(baseline)
            before = {**{k:old['tally'][k] for k in ('states','available','descent')},'confirmed':len(old['confirmed'])}
            self.quantity(f'{design} {protocol} finite search counts',before,dict(count),unit='states',
                          population=len(rows),sources=(rel,),endpoint=endpoint,old_source=baseline,
                          pressure_basis='individual absolute or bubble-scaled pressure per row')
            if design=='MDEA':
                self.quantity('C2 MDEA release endpoint fingerprint',old['parameter_fingerprint'],endpoint,unit='SHA-256',
                              sources=(rel,),old_source=baseline,endpoint=endpoint)
            old_paths = {'DEA':'F/search-rows.json.gz','MDEA':'C/salt/search-0.json.gz'}
            old_rows_path = R7+'results/'+old_paths.get(design,f"AMP/{design.split('_')[-1]}/{protocol}-rows.json.gz")
            old_rows = archived(old_rows_path)
            assert {q['key'] for q in rows}=={q['key'] for q in old_rows}
            for metric,counts in (
                ('descent flags',[sum(q['descent'] for q in v) for v in (old_rows,rows)]),
                ('descent flags on unavailable searches',[sum(q['descent'] and not q['available'] for q in v) for v in (old_rows,rows)]),
            ):
                self.quantity(f'{design} {protocol} {metric}',*counts,unit='states',population=len(rows),sources=(rel,),
                              old_source=old_rows_path,endpoint=endpoint,
                              pressure_basis='declared search pressures; descent flags include unavailable searches')
            for is_grid in (True,False):
                def measures(pool, confirmed):
                    subset = [q for q in pool if q['key'].startswith('grid:')==is_grid]
                    return dict(attempts=len(subset),distinct=len({q.get('same_calculation_as',q['key']) for q in subset}),
                                available=sum(q['available'] for q in subset),descents=sum(q['descent'] for q in subset),
                                confirmed=[q['key'] for q in subset if q.get('same_calculation_as',q['key']) in confirmed],
                                unavailable_by_event=dict(Counter(q.get('event') or q.get('status') for q in subset if not q['available'])))
                current = {q['key'] for q in result['classifications'] if any(x['confirmed'] for x in q['attempts'])}
                a,b = measures(old_rows,set(old['confirmed'])),measures(rows,current)
                self.quantity(f'{design} {protocol} {"grid" if is_grid else "measured"} stratum',a,b,unit='states',
                              population=a['attempts'],sources=(rel,),old_source=old_rows_path,endpoint=endpoint,
                              pressure_basis='declared state pressures within this stratum')
            if design=='MDEA':
                self.mdea_census(result,rel)

    def mdea_census(self,result,screen_path):
        from comparisons import mdea_deviations

        p = 'MDEA/screen/selected/declared/state-inventory.json.gz'
        inventory = self.read(p)
        if not inventory:
            return
        _,endpoint = self.selections['MDEA']
        assert inventory['endpoint_fingerprint']==endpoint
        keys = {q['key']:q for q in inventory['rows']}
        rows = {q['key']:q for q in result['rows']}
        assert keys.keys()==rows.keys()
        path = R7+'results/B/census.json.gz'
        old = archived(path)
        links = {}
        for identity,entries in old['joins'].items():
            links[identity] = []
            for archived_entry in entries:
                key = archived_entry['key']
                q = keys[key]
                pressure = q.get('declared_pressure_Pa') or q.get('search_Pa')
                bubble = q.get('bubble_Pa')
                link = dict(archived_entry,pressure_Pa=pressure,completed_without_descent=rows[key]['available'] and not rows[key]['descent'],
                            below_bubble_salt=pressure<bubble if pressure is not None and bubble is not None else None)
                links[identity].append(link)
        raw = 'MDEA/properties.json.gz'
        current = self.read(raw)
        assert current['endpoint_fingerprint']==endpoint
        keyed = {(q['group'],q['role'],q['unit']):q for q in mdea_deviations(current['rows'],links)}
        for before in old['metrics']:
            group,role,unit = label = tuple(before[k] for k in ('group','role','unit'))
            if label not in keyed:
                continue
            after = keyed[label]
            self.quantity(f'C2 MDEA {group} {role} {unit} admitted search attempts',before['admitted_search_attempts'],
                          after['admitted_search_attempts'],unit='states',sources=(screen_path,p,raw),
                          pressure_basis='individually assigned pressure',endpoint=endpoint,old_source=path)
            for subset in ('all','resolved_fixed_pressure_subset'):
                a,b = (q[subset] for q in (before,after))
                self.quantity(f'C2 MDEA {group} {role} {unit} {subset}',a,b,unit=unit,
                              population={'old':a['attempted'],'new':b['attempted']},sources=(screen_path,p,raw),
                              endpoint=endpoint,old_source=path,pressure_basis='below-bubble gate uses individually assigned pressure')
        for item in old['sobrinorows']:
            before = item['observation']
            after = next(q for q in current['rows'] if q['identity']==before['identity'])
            q = keys[item['search']['key']]
            assert before['observed']==after['observed']
            self.quantity(f'C2 MDEA Sobrino {before["row"]["source_row"]} density',before['value'],after['value'],
                          unit='kg/m³',population=1,sources=(screen_path,p,raw),endpoint=endpoint,old_source=path,
                          pressure_basis=dict(type='assigned absolute pressure',P_Pa=q['declared_pressure_Pa']))
        witness_path = 'MDEA/screen/selected/declared/witness-readbacks.json.gz'
        witnesses = self.read(witness_path)
        if witnesses:
            assert witnesses['endpoint_fingerprint']==endpoint
            tracked = archived(R8+'results/mdea-phase-outcomes.json.gz')['quantities']['classifications']
            expected = {q['key']:q for q in result['classifications'] if not q['key'].startswith('grid:')}
            assert all(k.removeprefix('bubble:') in expected for k in witnesses['rows'])
            labels = {'liquid','vapor'}
            for key,q in expected.items():
                readback = witnesses['rows'].get(key,{})
                old = next((v for v in tracked if v['key']==key),{})
                directions = {witness_direction(w) for w in readback.get('value',[])}
                value = dict(directions=sorted(directions or {'unclassified'}),attempts=len(q['attempts']),
                             confirmed=sum(v['confirmed'] for v in q['attempts']),refusal=readback.get('refusal'))
                self.quantity(f'C2 MDEA measured witness {key}',old.get('directions'),value,unit='direction and outcomes',
                              population=1,sources=(screen_path,p,witness_path),pressure_basis=keys[key],
                              old_source=R8+'results/mdea-phase-outcomes.json.gz',endpoint=endpoint,
                              disposition='undecided' if readback.get('refusal') or not labels.intersection(directions) else None)

    def c1(self):
        steps = {}
        self.c1_results = {}
        files = {p.name:p for folder in (OUT/'C1', OUT/'C1/rebuild-441') for p in folder.glob('*.json.gz')}
        for _,path in sorted(files.items()):
            rel = str(path.relative_to(OUT))
            q = self.read(rel)
            record = path.name.removesuffix('.json.gz')
            mode = 'selected' if record.startswith('selected-') else 'fixed-at-old'
            assert q['mode']==mode and q['wheel']==r.SHA, rel
            design = record.removeprefix(mode+'-').split('-')[0]
            if mode=='selected':
                assert q['endpoint_fingerprint']==self.selections[design][1], f'{rel}: selected endpoint fingerprint'
            if not q.get('steps'):
                continue
            steps[rel] = [dict(step) for step in q['steps']]
            center = q['center']
            assert center['volume_m3']==fsum(v['amount_mol']/v['rho_mol_m3'] for v in center['values'])
            for step in steps[rel]:
                pts = step['points']
                for p in pts.values():
                    if 'G_J' in p:
                        assert p['G_J']==fsum(v['eos_G_J']+v['standard_G_J'] for v in p['values']), rel
                if 'signed_volume_error_m3' in step:
                    v = (pts['P+']['G_J']-pts['P-']['G_J'])/(2*step['step_Pa'])
                    assert v-center['volume_m3']==step['signed_volume_error_m3'], rel
                    assert step['volume_admitted']==all(p['admitted'] for p in (center,pts['P+'],pts['P-'])), rel
                if 'eq12_minus_Gibbs_Helmholtz_J' in step:
                    T,dt = q['T_K'],step['step_K']
                    h = -T*T*(pts['T+']['G_J']/(T+dt)-pts['T-']['G_J']/(T-dt))/(2*dt)
                    eq12 = fsum(c['eq12_H_J'] for c in step['caloric_components'])
                    assert h==step['Gibbs_Helmholtz_H_J'] and eq12-h==step['eq12_minus_Gibbs_Helmholtz_J'], rel
                    if 'engine_H_J' in center:
                        discrepancy = center['engine_H_J']-h
                        assert discrepancy==step['engine_minus_Gibbs_Helmholtz_J'], f'{rel}: Engine enthalpy minus Gibbs–Helmholtz'
                        step['engine_minus_Gibbs_Helmholtz_J'] = discrepancy
                    assert step['enthalpy_admitted']==all(p['admitted'] for p in (center,pts['T+'],pts['T-'])), rel
            for key,error,metric in (('volume','volume_arithmetic_error_m3','signed_volume_error_m3'),
                                     ('enthalpy','caloric_arithmetic_error_J','engine_minus_Gibbs_Helmholtz_J'),
                                     ('Eq. 12','caloric_arithmetic_error_J','eq12_minus_Gibbs_Helmholtz_J')):
                available = [s for s in steps[rel] if metric in s]
                if not available:
                    continue
                admitted = [s for s in available if s.get(('volume' if key=='volume' else 'enthalpy')+'_admitted')]
                used = admitted or available
                latest = used[-1]
                span = max(s[metric] for s in used)-min(s[metric] for s in used)
                num = latest[error]+span
                scale = q['apparent_amine_feed_mol'] if key!='volume' else 1.
                value = dict(signed_error=latest[metric]/scale,estimated_error=num/scale,
                             admitted_steps=len(admitted),
                             disposition=('agreement within numerical error' if len(admitted)>=2 and abs(latest[metric])<=num
                                          else 'undecided'))
                if key=='volume':
                    value.update(relative_error=latest['relative_volume_error'],relative_estimated_error=num/q['center']['volume_m3'])
                if key=='enthalpy' and 'H_over_T_minus_S_check_J' in latest:
                    value['secondary_H_over_T_minus_S_error_J_per_mol'] = (
                        latest['H_over_T_minus_S_check_J']-latest['Gibbs_Helmholtz_H_J'])/scale
                self.c1_results[rel,key] = value
                self.quantity(f'C1 {path.name.removesuffix(".json.gz")} {key}',None,value,disposition=value['disposition'],
                              unit='J/mol apparent amine' if key!='volume' else 'm³',sources=(rel,),
                              pressure_basis=dict(T_K=q['T_K'],P_Pa=q['P_Pa']),endpoint=q['endpoint_fingerprint'])
        for mode in ('fixed-at-old','selected'):
            paths = tuple(f'C1/{mode}-MDEA-daughter-{i}.json.gz' for i in (1,2))
            branches = [self.read(p) for p in paths]
            if not all(q and q.get('steps') for q in branches):
                continue
            a,b = branches
            assert (a['T_K'],a['P_Pa'],a['endpoint_fingerprint'],a['apparent_amine_feed_mol'])==(
                b['T_K'],b['P_Pa'],b['endpoint_fingerprint'],b['apparent_amine_feed_mol'])
            for key,metric,error in (('volume','signed_volume_error_m3','volume_arithmetic_error_m3'),
                                     ('enthalpy','engine_minus_Gibbs_Helmholtz_J','caloric_arithmetic_error_J'),
                                     ('Eq. 12','eq12_minus_Gibbs_Helmholtz_J','caloric_arithmetic_error_J')):
                available = [(left[metric]+right[metric],left[error]+right[error])
                             for left,right in zip(*(steps[p] for p in paths),strict=True)
                             if left.get(('volume' if key=='volume' else 'enthalpy')+'_admitted')
                             and right.get(('volume' if key=='volume' else 'enthalpy')+'_admitted') and metric in left and metric in right]
                if not available:
                    continue
                delta,err = available[-1]
                span = max(d for d,e in available)-min(d for d,e in available)
                scale = a['apparent_amine_feed_mol'] if key!='volume' else 1.
                value = dict(signed_error=delta/scale,estimated_error=(err+span)/scale,admitted_steps=len(available),
                             disposition=('agreement within numerical error' if len(available)>=2 and abs(delta)<=err+span
                                          else 'undecided'))
                self.quantity(f'C1 {mode} MDEA daughter-inventory sum {key}',None,value,disposition=value['disposition'],
                              unit='J/mol apparent amine' if key!='volume' else 'm³',sources=paths,
                              pressure_basis=dict(T_K=a['T_K'],P_Pa=a['P_Pa']),
                              endpoint=a['endpoint_fingerprint'])

    def numerical_diagnosis(self):
        p = 'MDEA/stationarity/A-continuation.json.gz'
        continued = self.read(p)
        if continued:
            prior = self.read('MDEA/A.json.gz')
            assert continued['source']==prior['endpoint_fingerprint']
            assert continued['endpoint_fingerprint']==fingerprint(continued['endpoint'])
            cost = self.cost(continued['replay'],'MDEA A continuation')
            norm,_,optimizer_gradient = self.stationarity(continued)
            report = continued['report']
            self.quantity('MDEA A continuation',prior['replay']['cost'],
                dict(cost=cost,iterations=report['iterations'],status=report['status'],termination=report['message'],
                     projected_gradient_inf=norm,optimizer_gradient=optimizer_gradient,
                     gradient_tolerance=continued['controls']['gradient_tolerance'],failures=report['failures'],
                     fit_seconds=continued['fit_seconds'],replay_seconds=continued['replay_seconds'],
                     diagnostic_seconds=continued['diagnostic_seconds']),
                endpoint=continued['endpoint_fingerprint'],sources=('MDEA/A.json.gz',p),
                disposition='undecided' if report['status']!='converged' else None)
        for design in ('AMP_free','AMP_fixed'):
            path = f'{design}/root-probe.json.gz'
            record = self.read(path)
            if record:
                manifest = f'{design}/manifest.json.gz'
                assert record['manifest_fingerprint']==fingerprint(self.read(manifest))
                for label,data in record['starts'].items():
                    self.quantity(f'{design} {label} bubble guess diagnostic',None,data['guesses'],unit='Pa',
                                  sources=(path,manifest),pressure_basis={'row':data['row']})
        p = 'MDEA/root-probe.json.gz'
        probe = self.read(p)
        if probe:
            for start,data in probe['records'].items():
                ranges = {}
                for multiplier in sorted({q['multiplier'] for q in data['nodes']}):
                    nodes = [q for q in data['nodes'] if q['multiplier']==multiplier]
                    pressures = [q['pressure'] for q in nodes if q['admitted']]
                    ranges[str(multiplier)] = dict(attempted=len(nodes),admitted=len(pressures),
                                                   min_Pa=min(pressures,default=None),max_Pa=max(pressures,default=None))
                self.quantity(f'MDEA {start} saturation guess diagnostic',None,ranges,
                              sources=(p,),unit='Pa',pressure_basis=dict(target_Pa=data['P_Pa'],row=data['row']))
        p = 'MDEA/stationarity/A-projected-direction.json.gz'
        probe = self.read(p)
        if probe:
            prior = self.read('MDEA/A.json.gz')
            assert probe['endpoint']==prior['endpoint_fingerprint']
            old_cost = prior['replay']['cost']
            reductions = []
            for trial in probe['trials']:
                cost = self.cost(trial['replay'],'MDEA projected gradient line')
                reduction = (old_cost-cost)/old_cost if cost is not None else None
                assert trial['relative_reduction']==reduction
                reductions.append(dict(step=trial['step'],cost=cost,relative_reduction=reduction))
            self.quantity('MDEA A projected gradient line',old_cost,reductions,sources=('MDEA/A.json.gz',p),
                          endpoint=probe['endpoint'])
            retry_path = 'MDEA/stationarity/A-descent-continuation.json.gz'
            retry = self.read(retry_path)
            if retry and retry.get('replay'):
                assert retry['source']==fingerprint(probe['trials'][-1]['point'])
                assert retry['endpoint_fingerprint']==fingerprint(retry['endpoint'])
                cost = self.cost(retry['replay'],'MDEA A admitted-descent continuation')
                self.quantity('MDEA A admitted-descent continuation',old_cost,
                    dict(cost=cost,optimizer_gradient=retry['report']['covariance']['projected_gradient_norm'],
                         status=retry['report']['status'],message=retry['report']['message'],
                         fit_seconds=retry['fit_seconds'],replay_seconds=retry['replay_seconds']),
                    sources=(p,retry_path),endpoint=retry['endpoint_fingerprint'],
                    disposition='undecided' if retry['report']['covariance']['projected_gradient_norm']>
                    retry['controls']['gradient_tolerance'] else None)
        p = 'R1-R3-R5.json'
        row = self.read(p)
        if row:
            assert row['actual_prediction']['residual']==row['actual_residual']
            assert row['actual_residual']-row['expected_residual']==row['difference']
            self.quantity('Legacy R1 weighted residual at row 129',row['expected_residual'],row['actual_residual'],
                          sources=(p,),old_source=row['source']+'/fit.json',disposition='diagnosed caloric basis change')
            basis = row['water_caloric_basis']
            revision = basis['caloric_record_commit']
            assert sha256(blob(basis['path'],revision)).hexdigest()==basis['caloric_record_sha256']
            assert sha256(blob(basis['path'],revision+'^')).hexdigest()==basis['archived_caloric_record_sha256']
            self.quantity('R1 row 129 Cp with archived water record',row['expected_prediction'],
                          basis['archived_water_replay_row_129_prediction'],unit='J/(mol feed K)',
                          sources=(p,),old_source=row['source']+'/fit.json',population=1)
            checks_file = 'R1-R3-R5-current-water.json.gz'
            checks = self.read(checks_file)
            assert checks['wheel']==r.SHA
            assert all(basis[k]==v for k,v in checks['water_caloric_basis'].items())
            for gate in ('R1','R3','R5'):
                data = checks[gate]
                self.quantity(f'{gate} numerical reproduction on current water caloric basis',None,
                              {k:v for k,v in data.items() if k!='records'},
                              sources=(p,checks_file),population=len(data['records']))

    def archived_inventory(self):
        root = original(R8+'manuscript-handoff.json')
        profile_root = 'AMP_free/conditional-profile/'
        profile_path = profile_root+'profile-expanded.json'
        profile = self.read(profile_path)
        if profile:
            assert profile['endpoint_fingerprint']==self.selections['AMP_free'][1] and profile['wheel']==r.SHA
            assert profile['delta_cutoff']==.5*profile['stage_variance']*3.84146
        electrode_path = 'MEA/electrode/D/electrode-selected.json.gz'
        electrode = self.read(electrode_path)
        hartono_path = 'AMP_free/hartono-S11.json.gz'
        hartono = self.read(hartono_path)
        for name,meta in self.old.items():
            key = f'Round 7 {name}'
            value = meta.get('value')
            record = meta.get('record')
            if not record or not record.startswith('analyses/'):
                record = R7+'manuscript-handoff.json'
            match = {}
            if electrode and name.startswith(('D MEA electrode ','D MEA model minus electrode ')):
                selected = self.selections['MEA'][0]
                meapath = f'MEA/{selected}.json.gz'
                endpoint = self.read(meapath)['endpoint']
                assert electrode['parameter_sha256']==sha256(json.dumps(endpoint['parameters'],indent=2,
                    allow_nan=False).encode()+b'\n').hexdigest()
                field = ('signed_delta' if 'model minus' in name else
                         'carbonate_share' if 'carbonate_share' in name else 'common_molality_minus_raw')
                values = [row[field] for row in electrode['rows'] if row['requested_tolerance_met']]
                mode = name.split()[-1]
                val = min(values) if mode=='min' else max(values) if mode=='max' else fsum(values)/len(values)
                match = dict(new=val,disposition='replayed',population=len(values),
                             endpoint_fingerprint=self.selections['MEA'][1],
                             new_contributors=[self.reference(p) for p in (electrode_path,meapath)])
            elif hartono and name.startswith('H Hartono salt expanded free '):
                assert hartono['endpoint_fingerprint']==self.selections['AMP_free'][1]
                old = archived(record)['results']['salt expanded free'][name.split()[-2]]['rows']
                rows = hartono['rows'][name.split()[-2]]
                assert {q['identity']:q['observed'] for q in rows}=={q['identity']:q['observed'] for q in old}
                scores = summary(rows)
                match = dict(new=scores.get('AARD_percent'),disposition='replayed' if scores['available']==26 else 'partial',
                             new_contributors=[self.reference(hartono_path)],endpoint_fingerprint=hartono['endpoint_fingerprint'])
            elif name=='D Cai incumbent alternative objective':
                label,endpoint = self.selections['MEA']
                path = f'MEA/{label}.json.gz'
                fit = self.read(path)
                rows = fit['replay']['rows']
                assert sum(q['group']=='Cai' for q in rows)==50
                value_after = .5*fsum(q['residual']**2*.04 if q['group']=='Cai' else q['weighted_residual']**2
                                      for q in rows)
                match = dict(new=value_after,disposition='replayed',endpoint_fingerprint=endpoint,
                             new_contributors=[self.reference(path)])
            elif profile and name.startswith('D AMP profile '):
                parts = name.split()
                if 'conditional' in parts:
                    slope = parts[-2]
                    item = profile['points'].get(slope)
                    if item is not None:
                        contributor = profile_root+item['record']
                        run = self.read(contributor)
                        paths = (profile_path,contributor) if run else (profile_path,)
                        if run:
                            if item['cost'] is not None:
                                assert abs(fsum(q['cost'] for q in run['replay'])-item['cost'])<=1e-12*item['cost']
                            assert item['status']==run['report']['status']
                        result = item.get('status') if 'solve' in parts else item['cost']
                        match = dict(new=result,new_contributors=[self.reference(p) for p in paths],
                                     disposition='replayed' if result is not None else 'undecided')
                elif parts[-1]=='bracket':
                    bracket = profile['brackets'].get(parts[-3])
                    if bracket:
                        result = bracket[parts[-2]]
                        match = dict(new=result,new_contributors=[self.reference(profile_path)],
                                     disposition='replayed' if bracket['closed'] else 'undecided')
            elif name.startswith('F DEA '):
                item = name.removeprefix('F DEA ')
                match = self.items.get('DEA '+item,{})
                candidates = [q for q in self.items if q.startswith('DEA ') and ' all ' in q]
                for q in candidates:
                    group,stat = item.rsplit(' ',1)
                    if q.startswith(f'DEA {group} ') and q.endswith(' '+stat):
                        match=self.items[q]
                        break
            elif name.endswith('selected converged objective'):
                design = ('AMP_fixed' if name.startswith('AMP fixed') else 'AMP_free' if name.startswith('AMP') else
                          'DEA' if name.startswith('DEA') else 'MDEA')
                match = self.items.get(f'{design} selected objective',{})
            elif name=='E MEA incumbent original objective':
                match = self.items.get('MEA selected objective',{})
            elif name=='D5 incumbent unresolved, phase pressure closure':
                match = self.items.get('MEA measured unresolved pressure closure',{})
            elif name.startswith('D5 incumbent ') or name=='E MEA incumbent supplied missing':
                path = 'MEA/screen/summary.json.gz'
                screen = self.read(path)
                field = name.removeprefix('D5 incumbent ')
                if screen and (field in screen['measured'] or name.endswith('supplied missing')):
                    counts = screen['measured']
                    val = screen['grid']['missing_supplied'] if name.endswith('supplied missing') else counts[field]
                    match = dict(new=val,disposition='replayed',new_contributors=[self.reference(path)])
            elif name=='E MEA incumbent legacy pressure AARD rise versus F2':
                paths = 'E/MEA/replay.json.gz',R7+'results/E/incumbent/replay.json.gz'
                replay = self.read(paths[0])
                if replay:
                    old = archived(paths[1])
                    pool = set(old['pressure_population'])
                    assert pool==set(replay['pressure_population'])
                    legacy = [[q for q in doc['rows'][:307] if q['identity'] in pool] for doc in (old,replay)]
                    old_aard,new_aard = (summary(rows,pressure=True)['AARD_percent'] for rows in legacy)
                    match = dict(new=value+new_aard-old_aard,disposition='replayed',
                                 new_contributors=[self.reference(paths[0])],
                                 endpoint_fingerprint=self.selections['MEA'][1])
            elif name.startswith('E MEA incumbent '):
                match = self.items.get(name.replace('E MEA incumbent ','MEA pressure ',1),{})
                if not match:
                    item = name.removeprefix('E MEA incumbent ')
                    if item.startswith('outside fit '):
                        match = self.items.get(item.replace('outside fit ','MEA off-window ',1),{})
                    elif item=='expanded objective':
                        match = self.items.get('MEA expanded 419-row objective cross-score',{})
                if not match and any(name.startswith(f'E MEA incumbent {g} ') for g in ('grid','offset','census')):
                    with_grid = name.removeprefix('E MEA incumbent ').split()
                    sub = 'main' if with_grid[0]=='grid' else with_grid[0]
                    new_key = 'MEA native and supplied census counts' if sub=='census' else f'MEA {sub} finite search counts'
                    better = self.items.get(new_key,{})
                    if better and with_grid[-1] in better['new']:
                        match = dict(better,new=better['new'][with_grid[-1]])
            elif name.startswith(('F search-outcome.json ','AMP/free ','AMP/fixed ')) and name.split()[-1] in (
                    'states','available','descent','confirmed'):
                parts = name.split()
                design = {'F':'DEA','AMP/free':'AMP_free','AMP/fixed':'AMP_fixed'}[parts[0]]
                protocol = 'declared' if design=='DEA' else parts[1].split('-')[0]
                match = self.items.get(f'{design} {protocol} finite search counts',{})
                if match:
                    counts = match['new']
                    val = dict(states=sum(counts.values()),
                               available=sum(counts.values())-counts.get('unavailable search',0),
                               confirmed=counts.get('confirmed split',0),
                               descent=self.items[f'{design} {protocol} descent flags']['new'])[parts[-1]]
                    match = dict(match,new=val)
            elif name=='C MDEA salt search-outcome.json.gz seconds':
                path = 'MDEA/screen/selected/declared/summary.json.gz'
                replay = self.read(path)
                if replay:
                    match = dict(new=replay['seconds'],disposition='replayed',new_contributors=[self.reference(path)])
            elif name.startswith('C MDEA salt refit '):
                match = self.items.get('C5 '+name[2:],{})
                if not match:
                    match = self.items.get('MDEA '+name.removeprefix('C MDEA salt refit ').replace(' AARD_percent',' Pa all AARD_percent').replace(' bias_percent',' Pa all bias_percent'),{})
            elif name.startswith('C MDEA salt RMS '):
                metric = name.split()[-1]
                item = self.items.get('MDEA declared finite search counts',{})
                if item:
                    c = item['new']
                    counts = dict(states=sum(c.values()),available=sum(v for k,v in c.items() if k!='unavailable search'),
                                  descent=self.items['MDEA declared descent flags']['new'],
                                  unavailable=c.get('unavailable search',0),confirmed=c.get('confirmed split',0))
                    match = dict(item,new=counts[metric])
            elif name.startswith('B MDEA ') and ' all ' in name:
                group,metric = name.removeprefix('B MDEA ').split(' all ',1)
                candidates = [q for k,q in self.items.items() if k.startswith(f'MDEA {group} ') and k.endswith(f' all {metric}')]
                if len(candidates)==1:
                    match = candidates[0]
            elif name.startswith('B MDEA ') and ('resolved_fixed_pressure_subset' in name or name.endswith(' admitted search attempts')):
                text = name.removeprefix('B MDEA ')
                suffix = ' admitted search attempts' if text.endswith(' admitted search attempts') else ' resolved_fixed_pressure_subset'
                group = text.split(suffix)[0]
                candidates = [v for k,v in self.items.items() if k.startswith(f'C2 MDEA {group} ') and k.endswith(suffix)]
                if len(candidates)==1:
                    item, = candidates
                    if suffix==' admitted search attempts':
                        val = item['new']
                    else:
                        metric = text.split()[-1]
                        val = item['new']['available'] if metric=='available' else (item['new']['scores'] or {}).get(metric)
                    match = dict(item,new=val,disposition='replayed' if val is not None else 'undecided')
            elif name.startswith(('AMP free ','AMP fixed ')):
                label = 'AMP_free' if name.startswith('AMP free ') else 'AMP_fixed'
                metric = name.removeprefix('AMP free ').removeprefix('AMP fixed ').removeprefix('slope ')
                match = self.items.get(f'{label} {metric}') or self.items.get(f'C4 {label} {metric}',{})
            elif name.startswith('DEA carbamate '):
                match = self.items.get(name,{})
            if match:
                new = match['new']
                numerical = match['disposition']!='different available populations' and all(
                    isinstance(x,(int,float)) and not isinstance(x,bool) for x in (value,new))
                delta = new-value if numerical else None
                self.items[key] = dict(unit=meta.get('unit'),population=meta.get('population'),pressure_basis=None,
                    endpoint_fingerprint=None,transition=None) | dict(match,old=value,absolute_change=delta,
                    percent_change=100*delta/value if numerical and value else None,
                    old_contributor=dict(revision=BASE,path=record,field=meta.get('field'),sha256=sha256(blob(record,BASE)).hexdigest()))
            else:
                historical = (name.endswith(' elapsed') or 'original-slope' in name or 'historical' in name or
                              name.startswith(('E MEA F2 ','E MEA F4 ','H public-','H study-','A MDEA tracking ','B Sobrino row ',
                                               'H Kuranov Table 2','H Hong ','D5 F2 ','D5 F4 ','C MDEA salt incumbent ','D AMP original archive ',
                                               'D AMP original trial ','D AMP constant-enthalpy R5 ','D AMP slope only at fixed ')))
                self.quantity(key,value,value if historical else None,unit=meta.get('unit'),population=meta.get('population'),
                              old_source=record,old_field=meta.get('field'),independent=historical,
                              disposition='historical contributor' if historical else None)
        for i,name in enumerate(NAMES,1):
            item = root['items'][f'C{i}']
            path = R8+f'results/{name}.json.gz'
            for key,meta in item['quantities'].items():
                value = archived(path)['quantities'][key]
                historical = key in ('low_pressure_controls','archived_design','hot_original','original_R5_control',
                                     'original_slope_control','round7_F4_display_excluded','published_Kamps_28','published_table_snapshot')
                markers = {1:{'branches':('C1 selected',),'reference_controls':('MDEA fixed-at-old phase',)},
                           2:{'fingerprint':('C2 MDEA release endpoint fingerprint',),
                              'classifications':('MDEA declared','C2 MDEA measured witness'),'counts':('MDEA declared',),'strata':('MDEA declared',),
                              'targeted':('MDEA A phase 263',),'grid_confirmed':('MDEA declared grid',)},
                           3:{'all_44':('C3 DEA AARD all 44',),'four':('C3 DEA AARD four historically',),
                              'rows':('C3 DEA Weiland','C3 DEA weiland'),'first_split':('C3 DEA weiland',)},
                           4:{'grid':('AMP_free native','AMP_fixed native'),
                              'added_pressure_rows':('C4 AMP_free added','C4 AMP_fixed added')},
                           5:{'available':('C5 mixed salt',),'models':('C5 MDEA salt refit',),'properties':('C5 Kuranov matched',
                              'C5 Carson matched','C5 Xiao matched','C5 Ermatchkov matched'),'residuals':('C5 ',)},
                           6:{'AMP':('AMP_free selected','AMP_fixed selected','C6 AMP'), 'MDEA':('MDEA selected','C6 MDEA'),
                              'MEA #435':('MEA selected','C6 MEA'),'unavailable':('C6 ',)},
                           7:{'hong':('C7 Hong',),'kamps':('C5 C7 corrected-Kamps',),'kuranov':('C7 Kuranov',)}}
                if i==5 and key=='available':
                    salt_path = 'salt.json.gz'
                    rows = self.read(salt_path)['combined']
                    counts = {k:sum(q.get('status')=='Available' for q in rows[k]) for k in value}
                    self.quantity('Round 8 C5 available',value,counts,unit='rows',sources=(salt_path,),
                                  old_source=path,old_field=meta['field'])
                    continue
                linked = [item for item in self.items if item.startswith(markers.get(i,{}).get(key,()))]
                if i==4 and key in ('rows','worked_state'):
                    linked = []
                    for design in ('AMP_free','AMP_fixed'):
                        selected,_ = self.selections[design]
                        states = [row['key'] for row in value] if key=='rows' else ['worked-state']
                        linked.extend(f'{design} {selected} phase {state}' for state in states)
                    assert all(q in self.items for q in linked), linked
                self.quantity(f'Round 8 C{i} {key}',value if historical else (value if isinstance(value,(int,float,str)) else len(value)),
                              value if historical else linked or None,old_source=path,old_field=meta['field'],
                              disposition='historical contributor' if historical else 'reduced under linked quantities' if linked else None)
        salt_path = 'salt.json.gz'
        salt = self.read(salt_path)
        assert salt['wheel']==r.SHA
        source_table = 'analyses/mea_parameter_bundle/results/carbonate-ions-282/inputs/peiper-pitzer-1982-table6.csv'
        data = salt['reconstruction']
        target = (data['numerator']-data['ideal_co2'])/fsum(data['ions'].values())
        assert abs(target-data['target'])<1e-14
        self.quantity('C5 Peiper–Pitzer first NaHCO3 ionic osmotic target',data['target'],target,
                      independent=True,sources=(salt_path,),old_source=source_table,population=1,
                      pressure_basis='prescribed molalities with dissolved ideal CO₂ removed')
        for stage,e in salt['stages'].items():
            assert e['passed'] and e['differences']['maximum_relative_prediction_difference']==0
            scale = .003 if e['group']=='NaCl' else .01
            cost = .5*fsum(((q['value']-q['observed'])/scale)**2 for q in e['rows'])
            assert abs(cost-e['replayed_cost'])<=1e-13*cost, stage
            self.quantity(f'C5 {stage} retained replay objective',e['retained_cost'],cost,
                          sources=(salt_path,),population=len(e['rows']),independent=True,
                          old_source=f'analyses/mea_parameter_bundle/results/salt-anchored-435/salt/{stage}.json')
        self.quantity('C5 mixed salt refusals',6,len(salt['mixed_refusals']),unit='rows',population=len(salt['combined']['mixed']),
                      sources=(salt_path,),independent=True,
                      old_source='analyses/mea_parameter_bundle/results/salt-anchored-435/salt/summary.json')

    def matched_literature(self):
        literature = R8+'results/literature-populations.json.gz'
        old = archived(literature)['quantities']
        selection,endpoint = self.selections.get('MDEA',(None,None))
        p = f'MDEA/property-comparisons/{selection}.json.gz'
        new = self.read(p)
        for key in ('published_Kamps_28','published_table_snapshot'):
            self.quantity(f'C7 {key}',old[key],old[key],old_source=literature,
                          old_field=f'quantities.{key}',independent=True,
                          pressure_basis='published comparison population')
        hong = old['hong']
        self.quantity('C7 Hong local instability count',hong['local_failures'],hong['local_failures'],unit='states',
                      old_source=literature,population=hong['inside_count'],independent=True,
                      pressure_basis='Hong reconstruction within its declared grid')
        hong_path = 'MEA/hong-matched.json.gz'
        hong_rows = self.read(hong_path)
        if hong_rows:
            assert len(hong_rows['rows'])==hong['inside_count']
        self.quantity('C7 Hong matched population refitted MEA AARD',hong['matched_scores']['adopted']['AARD_percent'],
                      summary(hong_rows['rows'],True).get('AARD_percent') if hong_rows else None,unit='%',
                      old_source=literature,sources=(hong_path,),population=hong['inside_count'],
                      pressure_basis='source partial pressures; Hong reconstruction kept on its original basis',
                      endpoint=self.selections['MEA'][1])
        for name,value in old['kuranov']['published'].items():
            self.quantity(f'C7 Kuranov published AARD {name}',value,value,old_source=literature,
                          unit='%',population='published membership by count',independent=True,
                          pressure_basis='published total pressures')
        keys = {str(q) for q in old['kuranov']['source_rows']}
        values = []
        if new:
            assert new['endpoint_fingerprint']==endpoint and selection
            values = [q for q in new['rows'] if q['group'] in ('Kuranov','Kuranov-binary','Kuranov-413K')
                      and q['row']['source_row'] in keys]
            values.append(new['additional_Kuranov_72'])
            assert {q['row']['source_row'] for q in values}==keys and len(values)==82
        self.quantity('C7 Kuranov row-matched 82 AARD',old['kuranov']['current']['AARD_percent'],
                      summary(values,True).get('AARD_percent'),unit='%',population=len(keys),
                      pressure_basis='source total pressures; row 72 comparison only',sources=(p,),
                      old_source=literature,old_field='quantities.kuranov.current',endpoint=endpoint)
        c5 = R8+'results/salt-and-weighting.json.gz'
        properties = archived(c5)['quantities']['properties'] | {'corrected-Kamps': old['kamps']}
        for group,q in properties.items():
            before = q['salt/refit']
            keys = set(before['common_keys'])
            right = [v for v in new['rows'] if v['identity'] in keys] if new else []
            if right:
                assert len(right)==len(keys) and {v['identity'] for v in right}==keys
            old_rows = R7+'results/C/salt/refit.json.gz'
            left = [v for v in archived(old_rows)['rows'] if v['identity'] in keys]
            assert len(left)==len(keys) and all(map(available,left))
            assert all(abs(summary(left)[m]-before['matched'][m])<1e-10 for m in ('AARD_percent','bias_percent'))
            common = {v['identity'] for v in right if available(v)}
            a,b = (summary([v for v in rows if v['identity'] in common]) for rows in (left,right))
            for metric in ('AARD_percent','bias_percent'):
                self.quantity(f"C5 {'C7 ' if group=='corrected-Kamps' else ''}{group} matched {metric}",
                              a.get(metric),b.get(metric),unit='%',
                              population=len(common),sources=(p,),
                              old_source=old_rows,old_field='rows',endpoint=endpoint,
                              pressure_basis='common available source row keys; archived exclusions retained')
            if group=='corrected-Kamps' and new:
                for old_row in before['missing']:
                    v, = [v for v in new['rows'] if v['identity']==old_row['identity']]
                    assert v['observed']==old_row['observed']
                    self.quantity(f"C7 corrected-Kamps additional row {v['identity']}",old_row['value'],v['value'],unit='Pa',
                                  population=dict(rows=1,observed_Pa=v['observed'],tracking_status=old_row['status'],
                                                  refit_status=v['status'],refit_relative_error_percent=summary([v]).get('bias_percent')),
                                  sources=(p,),old_source=literature,endpoint=endpoint,
                                  pressure_basis='calculated bubble pressure compared with source total pressure',
                                  disposition='refit only' if available(v) else 'open')

    def mea_comparisons(self):
        endpoint = self.selections['MEA'][1]
        oldpath = R7+'results/E/incumbent/replay.json.gz'
        p = 'E/MEA/replay.json.gz'
        new = self.read(p)
        old = archived(oldpath)
        if new:
            a,b = (v['summary']['expanded_cost'] for v in (old,new))
            self.quantity('MEA expanded 419-row objective cross-score',a,b,population=419,endpoint=endpoint,
                          old_source=oldpath,sources=(p,),pressure_basis='historical sensitivity residual definition')
            pair = [v['hot_wagner'] for v in (old,new)]
            assert [(q['identity'],q['observed']) for q in pair[0]]==[(q['identity'],q['observed']) for q in pair[1]]
            a,b = (summary(rows,True) for rows in pair)
            for metric in ('AARD_percent','bias_percent','log_RMSE','available'):
                self.quantity(f'MEA pressure unfitted hot Wagner {metric}',a[metric],b[metric],
                              unit='%' if metric.endswith('percent') else 'rows' if metric=='available' else '1',
                              old_source=oldpath,population=dict(fitted=0,comparison=len(pair[0])),sources=(p,),endpoint=endpoint,
                              pressure_basis='observed CO₂ partial pressure; model bubble partial pressure')
        for group,stats in old['summary']['pressure'].items():
            updated = (new or {}).get('summary',{}).get('pressure',{}).get(group,{})
            for key in ('AARD_percent','bias_percent','log_RMSE','available'):
                self.quantity(f'MEA pressure {group} {key}',stats[key],updated.get(key),
                              unit='%' if key.endswith('percent') else 'rows' if key=='available' else '1',
                              old_source=oldpath,population=stats['attempted'],sources=(p,),endpoint=endpoint,
                              pressure_basis='observed partial pressure; model bubble partial pressure')
        op = R7+'results/E/incumbent/off-window.json.gz'
        p = 'MEA/off-window.json.gz'
        offwindow = self.read(p)
        if offwindow:
            assert offwindow['endpoint_fingerprint']==endpoint
            before,after = archived(op)['rows'],offwindow['rows']
            assert {(q['identity'],q['observed']) for q in before}=={(q['identity'],q['observed']) for q in after}
            for group,w in (('Jou1995',None),('Aronu2011',None),('Aronu2011','0.15'),('Aronu2011','0.45')):
                label = group if w is None else f'{group} {int(float(w)*100)} wt%'
                a,b = (summary([q for q in rows if q['group']==group and (w is None or
                    q['row']['source_coordinates']['MEA_weight_fraction']==w)],True) for rows in (before,after))
                a['refused'],b['refused'] = (q['rows']-q['available'] for q in (a,b))
                for metric in ('AARD_percent','bias_percent','log_RMSE','available','refused'):
                    self.quantity(f'MEA off-window {label} {metric}',a.get(metric),b.get(metric),
                                  unit='%' if metric.endswith('percent') else 'rows' if metric in ('available','refused') else '1',
                                  old_source=op,population=a['rows'],sources=(p,),endpoint=endpoint,
                                  pressure_basis='observed partial pressure; model bubble partial pressure')
        p = 'MEA/heat-comparison.json.gz'
        heat = self.read(p)
        if heat:
            assert heat['endpoint_fingerprint']==endpoint
            from round_8.records import Sources
            retained = Sources().display('mea-heat-sensitivity')['replay']['rows']
            for group in {q['source'] for q in retained}:
                before,after = ([dict(q,observed=q['observed_kJ_mol'],value=q['predicted_kJ_mol'],
                                     status='Available' if q['status']=='available' else q['status'])
                                 for q in pool if q['source']==group] for pool in (retained,heat['rows']['rows']))
                assert {q['record_id'] for q in before}=={q['record_id'] for q in after}
                a,b = (summary(rows) for rows in (before,after))
                self.quantity(f'MEA {group} retained heat AARD',a.get('AARD_percent'),b.get('AARD_percent'),
                              unit='%',population=a['rows'],sources=(p,),endpoint=endpoint,
                              pressure_basis='retained absolute calorimetry pressure')

    def mea_screen(self):
        _,endpoint = self.selections['MEA']
        base = 'analyses/mea_parameter_bundle/results/salt-anchored-435/MEA/F4/search/'
        p = 'MEA/screen/grid.json.gz'
        result = self.read(p)
        if result:
            old_path = base+'grid.json.gz'
            previous = {q['key']:q for q in archived(old_path)['result']}
            assert result['endpoint_fingerprint']==endpoint and len(previous)==len(result['data'])
            assert set(previous)=={q['key'] for q in result['data']}
            for name,left,right in (('main',0,1908),('offset',1908,2484)):
                new = result['data'][left:right]
                counts = [dict(states=len(v),available=sum(q['available'] for q in v),
                               descent=sum(r.descent(q) for q in v)) for v in ([previous[q['key']] for q in new],new)]
                self.quantity(f'MEA {name} finite search counts',*counts,unit='states',old_source=old_path,
                              population=len(new),endpoint=endpoint,sources=(p,),pressure_basis='model bubble times declared multiplier')
        p = 'MEA/screen/census.json.gz'
        result = self.read(p)
        if result:
            old_path = base+'census.json'
            old = archived(old_path)['result']['summary']
            assert result['endpoint_fingerprint']==endpoint and old['states']==result['data']['summary']['states']
            self.quantity('MEA native and supplied census counts',old,result['data']['summary'],unit='states',
                          old_source=old_path,population=old['states'],endpoint=endpoint,sources=(p,),
                          pressure_basis='declared circuit pressure and native/supplied trials')
        summary_path = 'MEA/screen/summary.json.gz'
        result = self.read(summary_path)
        batches = tuple(f'E/MEA/measured/{i}.json.gz' for i in range(41))
        new = [row for p in batches for row in self.read(p) or []]
        old = [row for i in range(41) for row in archived(R7+f'results/E/incumbent/measured/{i}.json.gz')]
        previous = {q['identity']:q for q in old}
        assert all(q['identity'] in previous for q in new) and len(new)==len({q['identity'] for q in new})
        if result:
            from round_7.handoff import measured_failures
            assert result['endpoint_fingerprint']==endpoint and len(new)==len(old)==321
            metric = 'phase pressure closure'
            old_path = R7+'results/E/incumbent/measured-summary.json'
            missed = [sum(metric in measured_failures(row) for row in rows if not row['available'])
                      for rows in (old,new)]
            self.quantity('MEA measured unresolved pressure closure',*missed,unit='states',
                          sources=(summary_path,*batches),old_source=old_path,population=len(old),endpoint=endpoint)
        fields = ('source total pressure','1.05 times #435 bubble pressure','assigned observation pressure',None)
        for field in fields:
            def counts(rows):
                pool = [q for q in rows if q.get('pressure_basis')==field]
                return dict(states=len(pool),available=sum(q['available'] for q in pool),
                            descents=sum(bool(q.get('witnesses')) for q in pool),
                            unavailable=dict(Counter(q.get('cause') for q in pool if not q['available'])))
            self.quantity(f'MEA measured screen {field or "pressure not resolved"}',counts(old),counts(new) if new else None,
                          unit='states',population=len(old),pressure_basis=field,endpoint=endpoint,sources=(summary_path,*batches),
                          old_source=R7+'results/E/incumbent/measured-summary.json',
                          disposition='partial' if new and not result else None)
        refinements = 'MEA/screen/refinement.json.gz'
        refine = self.read(refinements)
        if refine:
            assert refine['endpoint_fingerprint']==endpoint
            trials = refine['recalculated']
            self.quantity('MEA measured pressure-refinement pilot',0,sum(q['available'] for q in trials),
                          unit='available states',population=len(trials),endpoint=endpoint,sources=(refinements,),
                          old_source=R7+'results/E/incumbent/measured-summary.json',
                          pressure_basis='same retained external pressure with tighter internal control',
                          disposition='released' if refine['released'] else 'stopped after pilot')

    def curves(self):
        from property_replays import MDEA_CURVES
        from round_8.records import Sources

        def differences(old,new,keys):
            left = {keys(q):q for q in old}
            right = {keys(q):q for q in new}
            assert len(left)==len(old) and len(right)==len(new) and right.keys()<=left.keys()
            pairs = [(left[k]['value'],q['value']) for k,q in right.items() if q.get('value') is not None and left[k].get('value') is not None]
            nonzero = [abs(y/x-1) for x,y in pairs if x]
            return (dict(requested=len(left),available=sum(q.get('value') is not None for q in old)),
                    dict(requested=len(right),available=sum(q.get('value') is not None for q in new),paired=len(pairs),
                         maximum_relative_change=max(nonzero,default=None),maximum_absolute_change=max((abs(x-y) for x,y in pairs),default=None)))

        loader = Sources()
        for p in sorted((OUT/'MEA/curves').glob('*.json.gz')):
            path = str(p.relative_to(OUT))
            data = self.read(path)
            endpoint = self.selections['MEA'][1]
            assert data['endpoint_fingerprint']==endpoint and data['pressure_reference_Pa']==P_REF
            base = data['source']
            old = loader.read(base,BASE)
            assert sha256(blob(base,BASE)).hexdigest()==data['source_sha256']
            fields = ('curve','sampling','temperature_K','pressure_Pa','analytical_loading','mea_mass_fraction','liquid_mea_mole_fraction','quantity')
            if p.name=='pressure.json.gz':
                fields = tuple(f for f in fields if f!='pressure_Pa')
            if p.name=='mea-water.json.gz':
                fields = tuple(f for f in fields if f!='temperature_K')
            def key(q):
                return tuple(str(q.get(f) or '') if f in ('curve','sampling','quantity') else float(q[f]) if q.get(f) not in (None,'') else None for f in fields)
            for unit in sorted({q['unit'] for q in old}):
                prior,now = ([dict(q,value=float(q['value']) if q.get('value') not in ('',None) else None) for q in v if q['unit']==unit]
                             for v in (old,data['rows']))
                before,after = differences(prior,now,key)
                self.quantity(f'MEA display {p.name.removesuffix(".json.gz")} {unit}',before,after,unit=unit,
                              population=len(prior),pressure_basis='retained figure sample coordinates',
                              sources=(path,),old_source=base,endpoint=endpoint)
        paths = tuple(str(p.relative_to(OUT)) for p in sorted((OUT/'MDEA/curves').glob('batch-*.json.gz')))
        old = archived(MDEA_CURVES)['rows']
        endpoint = self.selections['MDEA'][1]
        replay = [self.read(path) for path in paths]
        assert all(q['endpoint_fingerprint']==endpoint for q in replay)
        for group in sorted({q['group'] for q in old}):
            prior = [q for q in old if q['group']==group]
            now = [q for item in replay for q in item['rows'] if q['group']==group]
            before,after = differences(prior,now,lambda q:q['identity'])
            self.quantity(f'MDEA display {group} Pa',before,after if now else None,unit='Pa',population=len(prior),
                          pressure_basis='archived curve temperature, aqueous stock and loading',
                          sources=paths,old_source=MDEA_CURVES,endpoint=endpoint,
                          disposition='partial' if now and len(now)<len(prior) else None)
        archive_path = 'MDEA/curves/archive/batch-000.json.gz'
        if archive := self.read(archive_path):
            p = {q['identity']:q for q in old}
            error = [abs(q['value']/p[q['identity']]['value']-1) for q in archive['rows'] if q.get('value') is not None]
            assert len(error)==24 and max(error)<1e-9, 'MDEA historical display identity'
            self.quantity('MDEA archived curve declaration readback',0,max(error),unit='relative',population=len(error),
                          sources=(archive_path,),old_source=MDEA_CURVES,endpoint=archive['endpoint_fingerprint'])
        curve_sources = {
            'DEA':'analyses/dea_transfer/results/refit-413/curve-data.json',
            'AMP_free':'analyses/amp_transfer/results/salt-anchored-435/curve-data.json',
            'AMP_fixed':'analyses/amp_transfer/results/retransfer-412-f2-05e94210/slope-150/curve-data.json',
        }
        for design,prior_path in curve_sources.items():
            path = 'DEA/property-comparisons/selected.json.gz' if design=='DEA' else f'{design}/properties.json.gz'
            current = self.read(path)
            old = archived(prior_path)
            if isinstance(old,dict):
                old = old['rows']
            new = current['curves'] if current else []
            identities = {q['identity'] for q in new}
            endpoint = self.selections[design][1]
            for group,unit in sorted({(q['group'],q['unit']) for q in old if q['identity'] in identities}):
                prior,now = ([q for q in v if (q['group'],q['unit'])==(group,unit)] for v in (old,new))
                before,after = differences(prior,now,lambda q:q['identity'])
                self.quantity(f'{design} display {group} {unit}',before,after,unit=unit,population=len(prior),
                              sources=(path,),old_source=prior_path,endpoint=endpoint,
                              pressure_basis='archived curve temperature, stock and loading')

    def stage1_phases(self):
        from mea_replays import measured_batch, measured_identity
        from mea_stability import BASE as MEA_TRIALS
        from phase_replays import point_for, screen_declarations

        issue = 'tannerpolley/epcsaft#265'
        screen = 'MEA/screen/rebuild-441/'
        folder = screen+'measured-scaled/'
        inventory = folder+'inventory.json.gz'
        measured = self.read(inventory)
        if not measured:
            return

        def pressure_stats(tally, parent, *, temperature=None):
            phases = parent.get('phases',[])
            if phases:
                errors = [scaled_pressure_error(p['pressure_residual_Pa'],p['density_mol_m3'],p.get('T_K',temperature))
                          for p in phases]
                tally.update(parents_checked=1,phases_checked=len(phases))
                tally['maximum_scaled_pressure_error'] = max(tally['maximum_scaled_pressure_error'],*errors)

        def record(name, rows, paths, **evidence):
            assert all(self.read(path) is not None for path in paths), paths
            outcomes = {key:phase_outcome(row,completion=True) for key,row in rows.items() if 'blocker' not in row}
            blockers = {key:row['blocker'] for key,row in rows.items() if 'blocker' in row}
            self.quantity('Stage 1 '+name,None,dict(counts=dict(Counter(outcomes.values())),
                outcomes=outcomes,engine_items={k:q['engine_issue'] for k,q in rows.items() if 'engine_issue' in q},
                blockers=blockers,**evidence),sources=tuple(paths),population=len(rows),
                disposition='undecided' if blockers else None)

        def parent_rows(name):
            root = screen+'trial-call/'+name+'/'
            index = root+'inventory.json.gz'
            data = self.read(index)
            source = data['source']
            self.read(source)
            lane = 'MEA/grid' if name=='MEA/offset' else name
            point,_,_,bank,declared_source,_ = screen_declarations(lane)
            assert source==declared_source and data['source_sha256']==self.files[source][1]
            assert data['endpoint_fingerprint']==fingerprint(point) and data['wheel']==r.SHA
            assert data['bank_fingerprint']==fingerprint(bank)
            result,paths,closure = {},[index],{}
            for i in range(data['batches']):
                path = root+f'{i}.json.gz'
                paths.append(path)
                batch = self.read(path)
                assert all(batch[k]==data[k] for k in ('source','source_sha256','endpoint_fingerprint','wheel','bank_fingerprint'))
                assert [q['key'] for q in batch['rows']]==batch['keys']
                for q in batch['rows']:
                    key = q['key']
                    assert key not in result and q['wheel']==r.SHA
                    stratum = name
                    if name=='MEA/grid':
                        stratum = 'MEA dense grid' if key.startswith('dense|') else 'MEA census-grid'
                    tally = closure.setdefault(stratum,Counter())
                    pressure_stats(tally,q.get('parent',{}))
                    if q.get('blocker'):
                        tally['failures'] += 1
                        result[key] = dict(blocker=dict(record=path,diagnosis=q['blocker']))
                        continue
                    if q.get('restart'):
                        tally['restarts'] += 1
                    declared = len(bank.get(key,[])) if isinstance(bank,dict) else len(bank)
                    assert q.get('bank_size')==declared, f'{key}: supplied trial bank size'
                    assert phase_closure(q['parent'],q['P_Pa'],q['parent']['row_tolerance']), f'{key}: trial-call parent scaled closure'
                    assert no_descent(q['native_completed'],q['native_trials']), f'{key}: native trial completion'
                    assert supplied_complete(q.get('supplied_counts'),q.get('supplied_excluded'),declared), f'{key}: supplied trial count'
                    assert type(q.get('supplied_descents')) is int, f'{key}: missing supplied descent count'
                    assert q['supplied_descents']==0, f'{key}: supplied descent needs classification'
                    result[key] = dict(key=key,parent_closed=True,native_complete=True,supplied_complete=True,descent=False)
            assert list(result)==data['keys'], name
            return result,paths,closure

        def control_row(key, value, tally, pair=None, *, supplied=0):
            search = value['search']
            pressure_stats(tally,value)
            if value.get('blocker'):
                tally['failures'] += 1
                return dict(blocker=dict(diagnosis=value['blocker']))
            assert phase_closure(value,value['P_Pa'],value['declaration']['row_tolerance']), f'{key}: trial-call parent scaled closure'
            counts = Counter(evaluated=0)
            counts.update(q['evidence'] for q in value.get('supplied',[]))
            return dict(key=key,parent_closed=True,
                        native_complete=no_descent(search.get('completed') and search.get('no_descent_in_trial_set'),
                                                   value['native_trials']),
                        supplied_complete=supplied_complete(counts,0,supplied),
                        descent=value['instability']=='resolved descent',pair=pair)

        bank = r.read(MEA_TRIALS/'split-registry.json')['trials']
        _,point = point_for('MEA','selected','measured-bound-441')
        identity = measured_identity(point,bank)
        assert all(measured.get(k)==v for k,v in identity.items())
        names = measured['names']
        batches = [folder+f'{i//8}.json.gz' for i in range(0,len(names),8)]
        mea = [q for i,p in enumerate(batches) for q in measured_batch(self.read(p),identity,names[8*i:8*i+8])]
        assert len(mea)==len(names)==len(set(names))==321
        parents = dict(Counter(q['declared_parent'] for q in mea))
        assert parents=={'liquid':307,'liquid-vapour':14}
        closure, outcomes, restart_cases = Counter(),{},{}
        for i,q in enumerate(mea):
            key = q['identity']
            parent = q.get('parent',{})
            pressure_stats(closure,parent)
            if q.get('pressure_restart'):
                closure['restarts'] += 1
            if key in ('vle_obs_0047-pco2','vle_obs_0162-pco2'):
                native = q.get('pressure_restart',{}).get('original_parent',parent)
                stats = Counter()
                pressure_stats(stats,native)
                restart_cases[key] = dict(P_Pa=q['P_Pa'],T_K=q['T_K'],
                    native=native,maximum_scaled_pressure_error=stats['maximum_scaled_pressure_error'],
                    restarted=bool(q.get('pressure_restart')))
            if not q['available']:
                closure['failures'] += 1
                outcomes[key] = dict(blocker=dict(record=batches[i//8],diagnosis=q['cause']))
                continue
            assert len(parent['phases'])==(1 if q['declared_parent']=='liquid' else 2)
            assert phase_closure(parent,q['P_Pa'],q['row_tolerance']), f'{key}: trial-call parent scaled closure'
            outcomes[key] = dict(key=key,parent_closed=True,
                native_complete=no_descent(q['native_no_descent'] and q['optimized_message'].endswith('unresolved trials 0'),
                                          q['native_trials']),
                supplied_complete=supplied_complete(q.get('supplied_counts'),q.get('supplied_not_applicable'),len(bank)+1),
                descent=bool(q['witnesses']))
        record('MEA measured',outcomes,[inventory,*batches],parents=parents,
               pressure_closure={'MEA measured':closure},restart_cases=restart_cases)
        path = 'MEA/controls/rebuild-441/scaled/selected.json.gz'
        value = self.read(path)['rows']['100-kPa']['value']
        total = Counter()
        record('MEA control',{'100-kPa':control_row('100-kPa',value,total)},[path],pressure_closure={'MEA control':total})

        path = 'DEA/screen/rebuild-441/declared/summary.json.gz'
        dea = self.read(path)
        assert dea['wheel']==r.SHA
        by_key = {q['key']:q for q in dea['rows']}
        assert len(by_key)==len(dea['rows'])==1271
        assert dea['aliases']=={k:q['same_calculation_as'] for k,q in by_key.items() if 'same_calculation_as' in q}
        assert all(dest in by_key and source in by_key and source not in dea['aliases']
                   for dest,source in dea['aliases'].items())
        pair_path = 'DEA/screen/rebuild-441/declared/scaled-pairs.json.gz'
        pair_data = self.read(pair_path)
        assert pair_data['source']==path and pair_data['wheel']==r.SHA
        assert pair_data['endpoint_fingerprint']==dea['endpoint_fingerprint']
        pairs = {q['key']:q for q in pair_data['classifications']}
        assert len(pairs)==6
        passes = {}
        for key,q in pairs.items():
            assert phase_closure(q['parent'],q['pressure_Pa'],q['row_tolerance']), f'{key}: trial-call parent scaled closure'
            good = [a for a in q['attempts'] if qualifying_pair(a,q['pressure_Pa'],q['row_tolerance'])]
            assert good, key
            passes[key] = good[0]
        a = passes['weiland-1998:31:problem']
        deposit = pairs['weiland-1998:31:problem']
        assert phase_closure(a.get('comparison_parent',{}),deposit['pressure_Pa'],deposit['row_tolerance']), (
            'DEA deposit 31: comparison parent scaled closure')
        assert a['seed_from']=='weiland-1998:32:problem' and a['feed_mol']==deposit['feed_mol']
        assert [round(n,6) for n in a['amounts_mol']]==[13.656813,.961327]
        assert format(a['Gibbs_decrease_over_RT_mol'],'.6g')=='0.000565537'
        assert format(a['numerical_error_over_RT_mol'],'.3g')=='6.64e-09', 'DEA deposit 31: numerical error'
        l = passes['lawson-1976-viii:0:problem']
        tolerance = pairs['lawson-1976-viii:0:problem']['row_tolerance']
        assert format(l['Gibbs_decrease_over_RT_mol'],'.6g')=='2.76493e-06'
        assert format(l['numerical_error_over_RT_mol'],'.3g')=='1.87e-09', 'DEA Lawson 0: numerical error'
        diagnostics = l['diagnostics']
        assert diagnostics['physical_checks_pass'] and any(
            abs(q['relative_pressure_residual'])>tolerance for q in diagnostics['phases']), 'DEA Lawson 0: raw pressure error'
        blocker = 'lawson-1976-viii:1:problem'
        origin = 'DEA/screen/selected/declared/summary.json.gz'
        held, = (q for q in self.read(origin)['rows'] if q['key']==blocker)
        assert not held['available'] and not by_key[blocker]['available']
        assert held['message']==by_key[blocker]['message'] and 'reconstruction destroys support' in held['message']
        control = 'DEA/controls/rebuild-441/scaled/selected.json.gz'
        controls = self.read(control)['rows']
        assert len(controls)==4
        for k,row in controls.items():
            assert row['P_Pa']==pairs[k]['pressure_Pa'] and row['value']['feed_mol']==pairs[k]['feed_mol'], k
            assert row['value']['phases']==pairs[k]['parent']['phases'], k
        negatives,parent_paths,closure = parent_rows('DEA/declared')
        for q in pairs.values():
            pressure_stats(closure['DEA/declared'],q['parent'])
        assert set(negatives)|set(passes)|{blocker}==by_key.keys()-dea['aliases'].keys()
        outcomes = {k:dict(pair=TWO_LIQUIDS) for k in passes} | negatives | {blocker:dict(engine_issue=issue)}
        outcomes.update((k,outcomes[v]) for k,v in dea['aliases'].items())
        record('DEA screen',outcomes,[path,origin,pair_path,*parent_paths],aliases=dea['aliases'],
               parents=dict(Counter(q['parent_kind'] for q in dea['rows'])),pressure_closure=closure)
        total = Counter()
        record('DEA controls',{k:control_row(k,row['value'],total,TWO_LIQUIDS) for k,row in controls.items()},
               [control,pair_path],parents={'Liquid':len(controls)},pressure_closure={'DEA controls':total})

        for design,expected in (('AMP_free',4),('AMP_fixed',3)):
            path = f'{design}/controls/rebuild-441/scaled/selected.json.gz'
            result = self.read(path)
            assert result['wheel']==r.SHA and len(result['rows'])==7
            outcomes,pressure = {},{}
            total = Counter()
            for k,row in result['rows'].items():
                v = row['value']
                assert len(v['phases'])==1, k
                pair = v.get('liquid_vapor')
                outcome = None
                if pair:
                    assert qualifying_pair(pair,v['P_Pa'],v['declaration']['row_tolerance'],vapor=True), k
                    bubble = v['bubble']
                    assert bubble['feed_mol']==pair['feed_mol']==v['feed_mol'] and bubble['T_K']==v['T_K'], k
                    assert bubble['amounts_mol'][0]>0 and bubble['amounts_mol'][1]==0
                    assert bubble['requested_tolerance_met'] and phase_closure(bubble,bubble['pressure_Pa'],bubble['row_tolerance'])
                    assert vapor_trace_passes(bubble)
                    pressure[k] = dict(imposed_Pa=v['P_Pa'],bubble_Pa=bubble['pressure_Pa'],
                        below=v['P_Pa']<bubble['pressure_Pa'],decrease=pair['Gibbs_decrease_over_RT_mol'],
                        error=pair['numerical_error_over_RT_mol'])
                    outcome = CONNECTED_VAPOR
                outcomes[k] = control_row(k,v,total,outcome,supplied=int(k!='worked-state'))
            assert len(pressure)==expected and phase_outcome(outcomes['worked-state'],completion=True)==FINITE_NEGATIVE
            record(design+' controls',outcomes,[path],bubble_comparisons=pressure,parents={'Liquid':len(outcomes)},
                   pressure_closure={design+' controls':total})

        census = screen+'support-census.json.gz'
        checked = self.read(census)
        assert checked['wheel']==r.SHA
        slots = {'grid':1908,'offset':576,'census':162} | {
            f'AMP_{d}/{p}':666 for d in ('free','fixed') for p in ('native','supplied')}
        assert set(checked['rows'])==slots.keys()
        for name,size in slots.items():
            group = checked['rows'][name]
            assert len(group)==len({q['key'] for q in group})==size
            assert all(q['before']==q['after'] for q in group), f'{name} screen needs a support-set rerun'
            if '/' in name:
                design,protocol = name.split('/')
                path = f'{design}/screen/selected/{protocol}/summary.json.gz'
                baseline = self.read(path)
                assert baseline['wheel']==r.SHA
                negatives,parent_paths,closure = parent_rows(name)
                assert baseline['aliases']=={q['key']:q['same_calculation_as'] for q in baseline['rows']
                                             if 'same_calculation_as' in q}
                rows = negatives | {key:negatives[src] for key,src in baseline['aliases'].items()}
                assert len(rows)==len(baseline['rows']) and set(rows)=={q['key'] for q in group}
                record(name,rows,[census,path,*parent_paths],pressure_closure=closure)
            elif name!='census':
                path = 'MEA/screen/grid.json.gz'
                self.read(path)
                keys = {q['key'] for q in group}
                rows,parent_paths,closure = parent_rows('MEA/'+name)
                if name=='offset':
                    rows['offset|0.4|338.15|0.5375|1.5'] = dict(engine_issue=issue)
                assert rows.keys()==keys
                record('MEA '+name,rows,[census,path,*parent_paths],pressure_closure=closure)
            else:
                rows,parent_paths,closure = parent_rows('MEA/census')
                assert rows.keys()=={q['key'] for q in group}
                record('MEA census',rows,[census,'MEA/screen/census-raw.json.gz',*parent_paths],pressure_closure=closure)

        for name in ('salt-rms','historical-original'):
            path = f'MDEA/controls/rebuild-441/scaled/121-MPa-{name}.json.gz'
            data = self.read(path)
            assert data['wheel']==r.SHA and not data.get('blocker'), (name,data.get('blocker'))
            assert parent_agreement(data['direct_parent'],data['lifted_parent'])
            assert parent_agreement(data['direct_parent'],data['endpoint_parent'])
            assert data['crossing'][-1]['t']==data['zero_amount_crossing']
            search = data['target_search']
            assert parent_agreement(data['direct_parent'],search['parent'])
            assert phase_closure(search['parent'],data['P_Pa'],ROW_TOLERANCE)
            total = Counter()
            pressure_stats(total,search['parent'])
            record('MDEA '+name,{name:dict(key=name,parent_closed=True,
                native_complete=no_descent(search['completed'] and search['no_descent'],search['trials']),supplied_complete=True,
                descent=any(q['descent'] for q in search['trials']))},[path,'MDEA/controls/rebuild-441/historical.json.gz'],
                zero_amount_crossing=data['zero_amount_crossing'],pressure_closure={'MDEA '+name:total})
        path = 'MDEA/controls/rebuild-441/historical.json.gz'
        history = self.read(path)
        assert history['wheel']==r.SHA
        pairs = {}
        for q in history['rows']:
            if 'decrease' not in q:
                continue
            assert phase_closure(q.get('comparison_parent',{}),q['P'],ROW_TOLERANCE), (
                f"MDEA {q['family']}/{q['weights']}: comparison parent scaled closure")
            pair = dict(q,amounts_mol=q['amounts'],requested_tolerance_met=q['message'].startswith('converged:'),
                vapor_trace=q['trace'][0],Gibbs_decrease_over_RT_mol=q['decrease'],numerical_error_over_RT_mol=q['error'])
            assert all('original_density_mol_m3' not in p for p in pair['phases'])
            assert qualifying_pair(pair,q['P'],ROW_TOLERANCE,vapor=True)
            pairs[f"{q['family']}/{q['weights']}/{q['P']}"] = dict(pair=CONNECTED_VAPOR)
        assert len(pairs)==3
        record('MDEA retained positive controls',pairs,[path])
        path = 'MDEA/screen/selected/declared/summary.json.gz'
        key = "grid:{'water': 40.84100418410041, 'methyldiethanolamine': 1.0}:393.15:0.8:3.0"
        blocker, = (q for q in self.read(path)['rows'] if q['key']==key)
        assert not blocker['available'] and '1.730566017378354e-10' in blocker['message']
        record('MDEA retained open search',{key:dict(engine_issue=issue)},[path])

        paths = ['MEA/controls/rebuild-441/hong.json.gz',
                 'AMP_free/controls/rebuild-441/born.json.gz','AMP_free/controls/rebuild-441/born-direct.json.gz',
                 r.ROOT/'analyses/mea_parameter_bundle/results/split-diagnosis-433/born-off.json',
                 r.ROOT/'analyses/mea_parameter_bundle/results/split-diagnosis-433/verification.json']
        hong,_,_,born,verification = map(self.read,paths)
        signs = [tuple(v<0 for v in row['eigenvalues']) for row in hong['rows']]
        extrema = [f'{v:.5f}' for v in sorted(row['eigenvalues'][1] for row in hong['rows'])]
        assert Counter(signs)=={(True,True):131,(False,False):1}
        assert [row['key'] for row in hong['rows'] if min(row['eigenvalues'])>0]==['vle_obs_0233-pco2']
        assert [extrema[i] for i in (0,-2,-1)]==['-1.09040','-0.03407','0.03763']
        step_change = max(abs(a-b) for a,b in (q['eigenvalues'] for q in hong['rows']))
        assert step_change<=5.91e-8
        lowering = -fsum(born['old_split_vs_own_parent'].values())
        assert f'{lowering:.7f}'=='0.3637575'
        assert max(map(abs,verification['balance_split']['scaled_element_residual'].values()))<=ROW_TOLERANCE
        assert max(abs(p['charge']) for p in verification['phase_log'][1:])<=ROW_TOLERANCE
        derivatives = {}
        for design,want in (('MEA',(3,2,'1.35e-09','0.00252')),('DEA',(2,3,'-2.82e-09','0.00134'))):
            path = f'C1/rebuild-441/fixed-at-old-{design}.json.gz'
            paths.append(path)
            v,h = (self.c1_results[path,k] for k in ('volume','Eq. 12'))
            volume,enthalpy = v['signed_error'],h['signed_error']
            n_v,n_h = v['admitted_steps'],h['admitted_steps']
            assert (n_v,n_h,f'{volume:.3g}',f'{enthalpy:.3g}')==want
            derivatives[design] = dict(volume_pairs=n_v,enthalpy_pairs=n_h,volume_error_m3=volume,
                Eq12_minus_Gibbs_Helmholtz_J_per_mol_amine=enthalpy)
        self.quantity('Stage 1 separate controls',None,dict(Hong_negative=131,Hong_total=132,
            Hong_max_step_change=step_change,Born_off_Gibbs_decrease_over_RT_mol=lowering,derivatives=derivatives),
            sources=tuple(paths))

    def stage2_phases(self):
        from part_ii import SHA, WHEEL
        from phase_replays import (MDEA, MDEA_265, MDEA_CEILING_PA, MDEA_CONNECTED, MDEA_GRID,
                                   MDEA_REBUILD)

        endpoint_path = 'MDEA_slope_bound/declaration.json.gz'
        declaration = self.read(endpoint_path)
        assert declaration['wheel']==SHA and sha256(WHEEL.read_bytes()).hexdigest()==SHA
        endpoint = fingerprint(declaration['point'])
        # The bank comes from the same release inventory as the old screen.
        bank_path = MDEA.OLD/'split-record.json'
        bank = r.read(bank_path)
        bank = bank['trials']+bank.get('supplied_trials',[])
        bank_id = fingerprint(bank)
        prior_path = 'MDEA/screen/selected/declared/summary.json.gz'
        prior = {q['key']:q for q in self.read(prior_path)['rows']}
        common = (endpoint_path,prior_path)

        def data(name, folder=MDEA_CONNECTED):
            path = f'{folder}/{name}.json.gz'
            record = self.read(path)
            mdea_record_identity(record,endpoint,SHA,bank_id,computed=not name.endswith('-inventory'))
            return record, path

        measured, inventory = data('measured-inventory')
        aliases = measured['aliases']
        batches = [data(f'measured-{i}') for i in range(4)]
        retained_batches = [data(f'measured-{i}',MDEA_REBUILD) for i in range(4)]
        assert sum(len(batch['recomputed_keys']) for batch,_ in batches)==16
        for (batch,_),(retained,path) in zip(batches,retained_batches,strict=True):
            assert batch['retained_batch']==path
            assert [q['key'] for q in batch['rows']]==[q['key'] for q in retained['rows']]
            assert all(q['key'] in batch['recomputed_keys'] or q==old
                       for q,old in zip(batch['rows'],retained['rows'],strict=True))
        recipes = {q['key']:q for q in measured['rows']}
        rows = {q['key']:q for batch,_ in batches for q in batch['rows']}
        assert len(rows)==sum(len(batch['rows']) for batch,_ in batches)
        assert len(recipes)==len(measured['rows'])==1564 and set(rows)==recipes.keys()-aliases.keys()
        assert set(aliases.values())<=rows.keys(), 'MDEA measured aliases'
        measured_results = mdea_measured(rows,aliases,{k:prior[k] for k in recipes},len(bank))
        measured_results['pressure_closure'] = mdea_pressure_stats(rows.values())
        self.quantity('Stage 2 MDEA measured',None,measured_results,population=len(recipes),endpoint=endpoint,
                      sources=(*common,inventory,*(path for _,path in batches+retained_batches)))

        controls, controls_path = data('controls',MDEA_REBUILD)
        control_rows = {q['key']:q for q in controls['rows']}
        measured_key = controls['measured_control']
        assert measured_key=='comparison:416:final' and set(control_rows)=={'204-MPa','263-MPa'}
        control_rows['4.19-MPa'] = rows[aliases.get(measured_key,measured_key)]
        results = {k:mdea_outcome(q,len(bank)) for k,q in control_rows.items()}
        assert set(results.values())=={CONNECTED_VAPOR}, 'MDEA fixed-pressure controls'
        quantities = {k:dict(P_Pa=q['P_Pa'],T_K=q['T_K'],outcome=results[k],
                    decrease=q['liquid_vapor']['Gibbs_decrease_over_RT_mol'],
                    error=q['liquid_vapor']['numerical_error_over_RT_mol']) for k,q in control_rows.items()}
        self.quantity('Stage 2 MDEA fixed-pressure controls',None,
                      dict(rows=quantities,pressure_closure=mdea_pressure_stats(control_rows.values())),
                      population=3,endpoint=endpoint,sources=(*common,controls_path,*(path for _,path in batches)))

        march, march_path = data('domain-march')
        grid, grid_path = data('grid-inventory')
        assert {q['key'] for q in grid['rows']}==prior.keys()-recipes.keys() and len(grid['rows'])==10260
        assert grid['ceiling_Pa']==march['ceiling_Pa']==MDEA_CEILING_PA
        paths = {(tuple(q['stock'].items()),q['T_K']):q for q in march['rows']}
        assert len(paths)==len(march['rows'])==342
        domains = {q['key']:mdea_grid_membership(q,paths[tuple(q['stock'].items()),q['T']],MDEA_CEILING_PA)
                   for q in grid['rows']}
        engine = {q['key']:q['engine_issue'] for q in grid['rows'] if 'engine_issue' in q}
        assert engine=={MDEA_265:'tannerpolley/epcsaft#265'} and domains[MDEA_265]=='inside'
        assert {key for key,domain in domains.items() if domain=='inside' and not prior[key]['available']}==engine.keys(), (
            'the historical in-domain miss must be the retained #265 case')
        blockers = [q for q in march['rows'] if q['stall']]
        connected, maximum_errors = march_connections(march['rows'])

        before = '../diagnosis-starts/results/searches.json.gz'
        historical = self.read(before)['records']
        check14 = {(tuple(literal_eval(path['stock']).items()),path['T'],s['loading'])
                   for path in historical for s in path['states'] if not s['reached'] and not s['search_available']
                   and not any(p['reached'] and p['loading']<s['loading'] and p['pressure_Pa']>MDEA_CEILING_PA
                               for p in path['states'])}
        mapped14 = {(tuple(q['stock'].items()),q['T'],q['a']):q['domain'] for q in grid['rows']}
        dispositions14 = Counter(mapped14[key] for key in check14)
        assert len(check14)==14 and dispositions14.keys()<={'outside','unassigned'}, '14 historical unreached loadings'

        historical_outside = Counter()
        for q in grid['rows']:
            if q['domain']=='outside':
                old = prior[q['key']]
                assert q['archived_available']==old['available'], 'outside grid historical availability'
                historical_outside['descent' if old['descent'] else 'no descent'
                                   if old['available'] else 'not completed'] += 1

        grid_batches = [data(f'grid-{i}',MDEA_GRID) for i in range(8)]
        searched = {q['key']:q for batch,_ in grid_batches for q in batch['rows']}
        assert len(searched)==sum(len(b['rows']) for b,_ in grid_batches)
        inputs = {q['key']:q for q in grid['rows'] if q['domain']=='inside' and q['key'] not in engine}
        assert inputs.keys()<=searched.keys(), 'an assigned grid row has no search record'
        ids = [c['component_id'] for c in declaration['point']['parameters']['components']]
        outcomes, refuses = {}, {}
        for key,state in inputs.items():
            q = searched[key]
            feed = [state['stock'].get(c,0.) for c in ids]
            feed[ids.index('carbon-dioxide')] = state['a']*state['stock']['methyldiethanolamine']
            try:
                assert (q['P_Pa']==state['c']*state['marched_pressure_Pa'] and q['T_K']==state['T']
                        and q['feed_mol']==feed), f'{key}: consumed grid state'
                outcomes[key] = mdea_outcome(q,len(bank))
            except (AssertionError,KeyError) as exc:
                refuses[key] = q.get('blocker') or str(exc)
        outcomes.update((key,phase_outcome(dict(engine_issue=issue),completion=True)) for key,issue in engine.items())
        evidence = dict(domain_counts=Counter(domains.values()),march_blockers=blockers,
            paths_completed=len(paths)-len(blockers),cold_starts=connected,reverse_maximum_errors=maximum_errors,
            historical_unreached_excluded=dispositions14['outside'],historical_unreached_unassigned=dispositions14['unassigned'],
            historical_outside_outcomes=historical_outside,engine_items=engine,additional_search_blockers=refuses,
            search_outcomes=outcomes,inside_counts=Counter(outcomes.values()),
            pressure_closure=mdea_pressure_stats(searched[k] for k in inputs if k not in refuses))
        self.quantity('Stage 2 MDEA grid domain',None,evidence,population=len(domains),endpoint=endpoint,
                      disposition='undecided' if blockers or refuses else None,
                      sources=(*common,march_path,grid_path,before,*(path for _,path in grid_batches)))

    def stage3_phases(self):
        from part_ii import SHA, WHEEL, Route, calculation_declaration
        from phase_replays import (COMPARISON_SETS, MDEA, MDEA_CEILING_PA, MDEA_COMPARISON, WORK,
                                   comparison_prior, comparison_reuse, comparison_sources, comparison_splits,
                                   comparison_stratum)

        for k in COMPARISON_SETS:
            folder = f'{MDEA_COMPARISON}/{k}'
            endpoint_path, bank_path, prior_paths, split_path = comparison_sources(k)
            point = r.read(endpoint_path)
            endpoint = fingerprint(point)
            registry = r.read(bank_path)
            bank = registry['trials']+registry.get('supplied_trials',[])
            bank_id = fingerprint(bank)
            route = Route(MDEA.DECLARATION,WORK/folder,wheel=WHEEL,wheel_sha256=SHA)
            spec = route.bind(point)
            declaration = route.result('identity.json')
            prior, splits = comparison_prior(prior_paths),comparison_splits(split_path)
            sources = []

            def data(name, *, computed=True):
                path = f'{folder}/{name}.json.gz'
                record = self.read(path)
                sources.append(path)
                mdea_record_identity(record,endpoint,SHA,bank_id,computed=computed)
                assert record['declaration']==declaration, 'comparison declaration identity'
                return record

            manifest = data('inventory',computed=False)
            inventory = {q['key']:q for q in manifest['rows']}
            recipes = {q['key']:q for q in route.states(spec)}
            assert len(inventory)==len(manifest['rows'])==len(recipes)==11824 and inventory.keys()==recipes.keys()==prior.keys(), (
                'comparison inventory reconciliation')
            assert all(all(row[f]==v for f,v in recipes[key].items()) and row['original_message']==prior[key].get('message')
                       and all(row[f]==v for f,v in splits.get(key,{}).items()) for key,row in inventory.items()), (
                'comparison recipe, control or original message')
            assert manifest['reuse']==comparison_reuse(prior), 'comparison reuse census'
            assert manifest['reaction_references']=={
                rx.name:calculation_declaration(rx.reference) for rx in spec.problems['comparison:363:final'].reactions}, (
                'comparison historical reaction references')
            march = data('domain-march')
            march_pilot = data('march-pilot')
            paths = {(tuple(q['stock'].items()),q['T_K']):q for q in march['rows']}
            assert len(paths)==len(march['rows'])==342 and all(paths[tuple(q['stock'].items()),q['T_K']]==q
                                                                for q in march_pilot['rows']), 'comparison loading paths'
            connected, reverse = march_connections(paths.values())
            names = ['pilot',*(f'search-{i}' for i in range(8))]
            if (OUT/folder/'continued-search-0.json.gz').is_file():
                names.extend(f'continued-search-{i}' for i in range(8))
            pilot, *batches = (data(name) for name in names)
            rows = [q for batch in [pilot,*batches] for q in batch['rows']]
            searched = {q['key']:q for q in rows}
            search_paths = {q['key']:f'{folder}/{name}.json.gz' for name,batch in zip(names,[pilot,*batches],strict=True)
                            for q in batch['rows']}
            aliases = manifest['aliases']
            assert (len(searched)==len(rows) and searched.keys()<=inventory.keys()-aliases.keys()
                    and aliases.keys()<=inventory.keys() and set(aliases.values())<=inventory.keys()-aliases.keys()
                    and all(inventory[k]['domain']==inventory[v]['domain']=='not applicable' for k,v in aliases.items())), (
                'comparison search and alias reconciliation')
            records, outcomes, blockers, pending = {}, {}, {}, {}
            for key,row in inventory.items():
                if 'stock' in row:
                    path = paths[tuple(row['stock'].items()),row['T']]
                    domain = mdea_grid_membership(row,path,MDEA_CEILING_PA)
                else:
                    assert row['domain']=='not applicable', f'{key}: measured domain'
                    domain = row['domain']
                records[key] = dict(domain=domain,outcome=None)
                source = aliases.get(key,key)
                if source in searched:
                    q = searched[source]
                    assert q.get('bank_size',len(bank))==len(bank), f'{key}: declared trial count'
                    comparison_consumed(row,q,spec,route)
                    outcome, blocker = comparison_outcome(row,q,len(bank))
                elif domain=='unassigned':
                    outcome, blocker = comparison_outcome(row,{},len(bank))
                else:
                    pending[key] = source
                    continue
                if blocker:
                    blockers[key] = dict(blocker,record_key=source,
                                         record=search_paths.get(source,f'{folder}/domain-march.json.gz'))
                else:
                    outcomes[key] = outcome
            stratum = lambda key: comparison_stratum(inventory[key])
            held = {}
            for key in blockers:
                held.setdefault(stratum(key),key)
            assert all(stratum(key) in held for key in pending), 'comparison unexplained missing searches'
            for key, record in records.items():
                if stratum(key) in held:
                    record['blocked_by'] = key if key in blockers else held[stratum(key)]
                else:
                    record['outcome'] = outcomes[key]
            counts = Counter(q['outcome'] or 'held' for q in records.values())
            domains = Counter(q['domain'] for q in records.values())
            assert sum(counts.values())==sum(domains.values())==11824, 'comparison outcome and domain counts'
            controls = comparison_split_check(inventory,searched,outcomes,splits) if k=='0.1325' else {}
            old_sources = [endpoint_path,bank_path,*prior_paths]+([split_path] if split_path else [])
            evidence = dict(records=records,counts=counts,domain_counts=domains,controls=controls,held_strata=sorted(held),
                            blockers=blockers,pending=len(pending),reuse=manifest['reuse'],cold_starts=connected,
                            reverse_maximum_errors=reverse,
                            pressure_closure=mdea_pressure_stats(searched[key] for key in searched if outcomes.get(key) in
                                                               (FINITE_NEGATIVE,CONNECTED_VAPOR,TWO_LIQUIDS)),
                            inputs={str(p.relative_to(r.ROOT)):sha256(p.read_bytes()).hexdigest() for p in old_sources},
                            seconds=pilot['elapsed']+march['seconds']+sum(b['seconds'] for b in batches))
            self.quantity(f'Stage 3 MDEA k = {k}',None,evidence,population=len(records),endpoint=endpoint,
                          disposition='undecided' if held else None,sources=sources)
            for path in sources:
                del self.files[path]
            del rows, searched, batches, pilot

    def compute(self, *, stage2=False, stage3=False):
        for design in COUNTS:
            self.fit(design)
            self.properties(design)
            self.phases(design)
        self.c1()
        self.mea_comparisons()
        self.mea_screen()
        self.curves()
        self.matched_literature()
        self.numerical_diagnosis()
        self.archived_inventory()
        self.stage1_phases()
        if stage2:
            self.stage2_phases()
        if stage3:
            self.stage3_phases()
        timing = self.read('stages.json')
        if timing:
            for stage,data in timing.items():
                sources = ['stages.json']
                if 'AMP_profile_wall_s' in data:
                    path = 'AMP_free/conditional-profile/profile-expanded.json'
                    profile = self.read(path)
                    assert data['AMP_profile_wall_s']==profile['seconds'] and all(q['closed'] for q in profile['brackets'].values())
                    assert data['measured_s']==data['timed_subtotal_before_AMP_profile_s']+profile['seconds']
                    assert data['stop_overrun_s']==data['measured_s']-data['stop_s']
                    sources.append(path)
                if 'expansion_forecast_exception' in data:
                    path = stage.split()[0]+'/projection.json'
                    projection = self.read(path)
                    assert projection['projected_s']==data['projected_s']
                    assert all(v['fit_projection_basis'].startswith('maximum archived round-7 fit wall time')
                               for v in projection['designs'].values())
                    sources.append(path)
                self.quantity(f'Campaign stage {stage}',None,data,unit='s',sources=sources,
                              disposition=data['disposition'])
        starting = json.loads(blob(str(HANDOFF.relative_to(r.ROOT)),'d8f4c877f'))['quantities']
        starting = {k:v['disposition'] for k,v in starting.items() if v['disposition'] in ('open','undecided')}
        return dict(base=BASE,reference_pressure_pa=P_REF,wheel=r.SHA,starting_dispositions=starting,
                    selected_starts={k:v[0] for k,v in self.selections.items()},
                    fit_attempts=self.attempts,quantities=self.items)


def main(check):
    from phase_replays import COMPARISON_SETS, MDEA_REBUILD, MDEA_CONNECTED, MDEA_COMPARISON

    quantities = Quantities()
    stage2 = (OUT/MDEA_REBUILD/'measured-inventory.json.gz').is_file()
    stage3 = all((OUT/MDEA_COMPARISON/k/'search-7.json.gz').is_file() for k in COMPARISON_SETS)
    target = (OUT/MDEA_COMPARISON/'handoff.json' if stage3 else OUT/MDEA_CONNECTED/'handoff.json' if stage2 else HANDOFF)
    expected = quantities.compute(stage2=stage2,stage3=stage3)
    if check:
        retained = json.loads(target.read_text())
        for key in sorted(expected['quantities'].keys() | retained['quantities'].keys()):
            assert retained['quantities'].get(key)==expected['quantities'].get(key), f'{key}: changed contributor or stale disposition'
        assert retained==expected, 'stale fit attempt inventory'
        print(f"{len(expected['quantities'])} retained comparison quantities verified")
    else:
        if stage2:
            assert not target.exists(), target
        save(target,expected)
        if stage3:
            from notebook import render_mdea_stage3
            with target.with_name('notebook.qmd').open('x') as stream:
                stream.write(render_mdea_stage3(expected))
        elif stage2:
            from notebook import render_mdea_stage2
            with target.with_name('notebook.qmd').open('x') as stream:
                stream.write(render_mdea_stage2(expected))
        else:
            from notebook import render
            (HERE/'notebook.qmd').write_text(render(expected))


if __name__=='__main__':
    from refit import a
    a.study.reuse.bind_wheel()
    r.verify()
    main(sys.argv[1:]==['--check'])
