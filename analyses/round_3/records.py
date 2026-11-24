"""Reduce the existing referee records without predicting or fitting."""
from collections import Counter, defaultdict
import csv
import math
from time import monotonic

from recall import DECLARATION, ENDPOINTS
from part_ii import ROOT, Route, deviation_statistics, stable
from reference_states_428 import BUNDLE, identity, s
from phases import MDEA, BOUNDED

DEA = ROOT/'analyses/dea_transfer'
RESULTS = BOUNDED.parent


def fit_deviations(spec, report, reference):
    groups, rows = defaultdict(list), []
    for r, value, status, residual, weighted in zip(spec.inputs['observations']['fitted'], report['predictions'], report['statuses'],
            report['residuals'], report['weighted_residuals'], strict=True):
        observed = r['arguments']['observed']
        former = reference[r['identity']]
        assert (r['group'],r['unit'],observed)==(former['group'],former['unit'],float(former['observed']))
        err = math.log(value/observed) if r['arguments']['form']=='log_ratio' else (value-observed)/r['arguments']['scale']
        assert status=='Available' and math.isclose(err,residual,abs_tol=1e-10)
        assert math.isclose(residual*math.sqrt(r['weight']),weighted,abs_tol=1e-10)
        rows.append(dict(identity=r['identity'], role='fitted', group=r['group'], unit=r['unit'], kind=r['kind'],
                         observed=observed, prediction=value, weighted_residual=weighted, weight=r['weight'], status=status))
        groups[r['group'],r['unit'],r['kind']].append((observed,value))
    scores = [dict(group=g,kind=k,**deviation_statistics(pairs,u)) for (g,u,k),pairs in groups.items()]
    return dict(rows=rows,scores=scores,cost=math.fsum(r['weighted_residual']**2/2 for r in rows),
                outside_fit='Unavailable: other-endpoint predictions were not retained for these observations')


def reductions(work, save):
    start = monotonic()
    inputs = []
    def read(p):
        inputs.append(p)
        return stable.read(p)

    selection_path = DEA/'results/refit-413/selection.json'
    selection = read(selection_path)
    chosen, other = selection['candidates']
    dea_route = Route(DEA/'inputs/part-ii-346/f2-carbamate-413-route.json', work/'dea')
    spec = dea_route.bind(other['parameters'])
    inputs += [dea_route.path, spec.path]
    dea_csv = selection_path.with_name('paper-data.csv')
    inputs.append(dea_csv)
    with dea_csv.open() as file:
        dea_ref = {r['identity']:r for r in csv.DictReader(file) if r['role']=='fitted'}
    assert chosen['name']==selection['chosen']['name']=='start-0' and other['name']=='start-1'
    tolerance = dea_route.controls['function_tolerance']
    assert chosen['cost']<other['cost']<=chosen['cost']+tolerance and selection['ties']==['start-0','start-1']
    changed = fit_deviations(spec,other['optimizer_report'],dea_ref)
    dea = dict(chosen_cost=chosen['cost'], alternative_cost=other['cost'], absolute_tie_tolerance=tolerance,
               coordinates=other['declared'], physical=other['optimizer_report']['physical'], endpoint=other['parameters'],
               split_counts=other['split_counts'], search=other['search'], disposition=other['disposition'], **changed)

    archive = BOUNDED/'fits/unbounded-2'
    unbounded = read(archive/'stage-1-fit.json')
    mdea_route = Route(MDEA,work/'mdea')
    spec = mdea_route.bind(read(archive/'endpoint.json'))
    inputs += [MDEA, spec.path, MDEA.parent/mdea_route.config['dataset_changes']['path']]
    reference = {r['identity']:r for r in read(BOUNDED/'data-rows.json') if r['role']=='fitted'}
    mdea = fit_deviations(spec,unbounded,reference)
    assert math.isclose(mdea['cost'],unbounded['data_cost'],rel_tol=1e-12) and round(mdea['cost'],8)==479.44283987
    mdea['retained_summary'] = read(archive/'summary.json')
    for group in mdea['scores']:
        ids = [r['identity'] for r in mdea['rows'] if (r['group'],r['unit'],r['kind'])==(group['group'],group['unit'],group['kind'])]
        group['bounded_on_same_rows'] = deviation_statistics([(reference[i]['observed'],reference[i]['value']) for i in ids],group['unit'])

    water_dir = BUNDLE/'results/water-124'
    reference_grid = BUNDLE/'results/density-cp-160/cp-124-assessment/iapws95-reference.csv'
    metrics = water_dir/'metrics.csv'
    inputs.extend((reference_grid,metrics))
    with reference_grid.open() as stream:
        grid = list(csv.DictReader(stream))
    with metrics.open() as stream:
        statistics = [dict(r, mean_percent=100*float(r['mean_absolute_relative_error']), max_percent=100*float(r['maximum_absolute_relative_error']),
                           conditions=[(float(g['T_K']),float(g['P_Pa'])) for g in grid if g['grid']==r['grid']]) for r in csv.DictReader(stream)]
    old, current = (s.parameter_values(read(path)) for path in
                    (water_dir/'lambda-0.1-A/parameters.json', BUNDLE/'results/selected-current-best-parameters.json'))
    ids = read(water_dir/'verification.json')['only_five_coordinates_changed']
    assert len(ids)==5 and all(old[i]==current[i] for i in ids)
    water = dict(metrics=statistics, coefficients={i: current[i] for i in ids}, provenance=read(water_dir/'inputs.json')['wheel_sha256'],
                 fitted_rows=dict(saturated_liquid_rho=20,psat=20,cp=23), reference='IAPWS-95')

    kuranov = read(RESULTS/'kuranov-published-422/kuranov-rows.json')
    added, = [r for r in kuranov if r['source_row']==72]
    assert (added['T'], added['p_exp'],added['role'])==(393.16,1205300.,'not fitted')
    counts = Counter(r['role'] for r in kuranov)
    assert sorted(r['source_row'] for r in kuranov)==list(range(1,83)) and counts=={'fitted':70,'not fitted':12}
    assert sum(r['replay_relative_difference'] is not None for r in kuranov)==81 and added['replay_relative_difference'] is None
    kuranov_scores = {role:deviation_statistics([(r['p_exp'],r['present']['pressure_Pa']) for r in kuranov
                              if r['role']==role and r['present']['status']=='Available'],'Pa') for role in counts}

    measured = read(RESULTS/'phase-search-421/measured-phase.json')
    coverage = read(RESULTS/'phase-search-421/coverage-counts.json')['canonical']
    distinct = [a for r in measured for a in r['attempts'] if a.get('distinct') and a['requested_tolerance_met']]
    assert len({r['key'] for r in measured})==len(measured)==27 and {r['key'] for r in measured}==set(coverage)
    n_states = sum(any(a.get('distinct') and a['requested_tolerance_met'] for a in r['attempts']) for r in measured)
    roots = Counter(tuple(sorted(p['identity'] for p in a['coexistence_roots'])) for a in distinct)
    assert len(distinct)==24 and n_states==16 and all('liquid' in labels and len(set(labels))==2 for labels in roots)
    phase_counts = dict(states=len(measured),attempted_states=sum(bool(r['attempts']) for r in measured),
                        attempts=sum(len(r['attempts']) for r in measured),converged=sum(a['requested_tolerance_met'] for r in measured for a in r['attempts']),
                        converged_distinct=len(distinct),states_with_converged_distinct=n_states,
                        roots={' + '.join(k):v for k,v in roots.items()},confirmed_two_liquid=sum(a['confirmed'] for a in distinct))

    main, fixed = (ENDPOINTS/p for p in ('main','slope-150'))
    free_summary = read(main/'fit-summary.json')
    costs = [next(r['cost'] for r in free_summary['fits'] if r['start']==free_summary['selection']['selected']),
             read(fixed/'confirmation.json')['selected_cost']]
    amp_route = Route(DECLARATION,work/'amp')
    bindings = [amp_route.bind(read(p/'parameters.json')).inputs['observations']['fitted'] for p in (main,fixed)]
    inputs += [DECLARATION, DECLARATION.with_name('specification.toml')]
    signature = lambda rows: [(r['identity'],r['weight'],r['arguments'],r['unit']) for r in rows]
    assert signature(bindings[0])==signature(bindings[1]) and len(bindings[0])==156
    assert all([r['identity'] for r in bindings[0]]==[r['identity'] for r in read(p/'data-rows.json') if r['role']=='fitted'] for p in (main,fixed))
    uncertainty = [read(p/'conditional-uncertainty.json') for p in (main,fixed)]
    active = [[list(u['cost_gradient'])[i] for i in u['active_bounds']] for u in uncertainty]
    assert all(set(a)==set(u['active_bound_outward_descent']) for a,u in zip(active,uncertainty,strict=True)) and set(active[0])==set(active[1])
    dfs = [156-len(u['free_coordinates']) for u in uncertainty]
    variance = [2*c/df for c,df in zip(costs,dfs,strict=True)]
    assert dfs==[149,150] and all(math.isclose(v,u['residual_variance'],rel_tol=1e-10) for v,u in zip(variance,uncertainty,strict=True))
    amp = dict(costs=costs,RSS=[2*c for c in costs],df=dfs,residual_variance=variance,
               active=active,free=[u['free_coordinates'] for u in uncertainty],descriptive_F=2*(costs[1]-costs[0])/variance[0],
               residual_ids_weights={r['identity']:r['weight'] for r in bindings[0]})

    salt_dir, = (BUNDLE/'results/shared-ion-electrostatics-423').glob('*/*/N1')
    salts, common = {}, None
    for sodium in ('N1','N2'):
        for label in ('Held','F2','salt-fitted'):
            observed = read(salt_dir.parent/sodium/label/'osmotic.json')
            key = [(r['salt'],r['T'],r['m'],r['pressure_Pa'],r['status'],r.get('composition_mol_per_kg'),r.get('observed')) for r in observed]
            if common is None:
                common = key
            assert key==common
            groups = {salt:[r for r in observed if r['salt']==salt] for salt in ('NaHCO3','Na2CO3','mixed')}
            salts[f'{sodium}/{label}'] = {k:dict(total=len(group),refused=Counter(r.get('unavailable') for r in group if r['status']!='Available'),
                             **deviation_statistics([(r['observed'],r['value']) for r in group if r['status']=='Available'],'dimensionless'))
                                         for k,group in groups.items()}
    historical = read(salt_dir.parent/'controls.json')
    save('q8',start, dea=dea,mdea=mdea,water=water,kuranov=dict(added_row=added,counts=counts,scores=kuranov_scores),
         phase_counts=phase_counts,amp=amp,salts=salts,historical_salt={k:v for k,v in historical.items() if k.startswith('historical_')},
         inputs=identity(*inputs))
