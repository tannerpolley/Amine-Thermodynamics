"""Coverage and observation comparisons at the reported bounded MDEA endpoint (#421)."""
from collections import Counter
from decimal import Decimal

from bounded_binary_411 import DECLARATION, RESULTS, Route, stable
from coexistence_421 import coexistence_roots
from part_ii import ROOT, calculation_declaration, deviation_statistics, eq

OUT = RESULTS.parent/'phase-search-421'
SENSITIVITY = RESULTS.parent/'shared-bicarbonate-417'
ALIASES = ROOT/'analyses/mea_parameter_bundle/results/release-recheck-414/mdea-comparison.json'
SUPPLIED_ONLY = {f'comparison:{i}:problem' for i in (157,161,201,221)}


def stage(row):
    if row['message'].startswith('pressure reference'):
        return 'bubble reference'
    return {(False,True): 'optimized unavailable', (True,False): 'supplied incomplete',
            (None,None): 'preparation failed'}[row.get('optimized_available'),row.get('supplied_available')]


def observation_coordinates(spec, observations, wt_percent, amine):
    merkley_path = RESULTS.parent/'merkley-loading-points.json'
    merkley = {(r['temperature_K'],r['MDEA_mass_percent']):r for r in stable.read(merkley_path)['rows']}
    measured = {}
    for o in observations:
        key = o.get('problem') or o.get('final') or o['initial']
        stock = spec.problems[key].feed.values
        loading = stock.get('carbon-dioxide',0.)/stock[amine] if stock.get(amine) else None
        row = dict(problem=key, MDEA_wt_percent=wt_percent(stock), loading=loading, source=o['row'], loading_basis='declared source state' if loading is not None else 'undefined (no MDEA)')
        if o['group'].startswith('Merkley'):
            source = merkley[float(o['row']['temperature_K']),float(o['row']['MDEA_mass_percent'])]
            row.update(loading=source['alpha_LP_mol_CO2_per_mol_MDEA'], loading_basis='digitized Fig. 4 loading point', loading_source=str(merkley_path.relative_to(ROOT)))
        measured[o['identity']] = row
    return measured


def coverage(route, point, spec, states, observations, links, data):
    report = stable.read(RESULTS/'stability.json')
    grid, witnesses = report['grid'], report['descent_witnesses']
    unfinished = {r['key']:r for r in grid['unavailable_searches']}
    alias = stable.read(ALIASES)['retained_descent_reference']['records']
    canonical = {r['key']:r for r in witnesses['calculations']}
    tier = lambda k: 'grid' if k.startswith('grid:') else 'data'
    counts = Counter((tier(k),stage(v)) for k,v in unfinished.items())
    assert len(unfinished) == len(grid['unavailable_searches']) == len(grid['unavailable']) == 1099 and unfinished.keys() == set(grid['unavailable'])
    assert len(states) == grid['states'] == 11824 and grid['available'] == 10725 and report['distinct_calculations'] == 10870
    assert Counter(map(tier,states)) == {t:sum(grid['branches'][t]['native'].values()) for t in ('data','grid')} == {'data':1564,'grid':10260}
    assert counts == {('grid','bubble reference'):870, ('grid','optimized unavailable'):4, ('data','optimized unavailable'):72,
                      ('data','supplied incomplete'):146, ('data','preparation failed'):7}
    assert len(alias) == 76 and len(canonical) == 27 and set(alias.values()) == canonical.keys()
    assert {k for k,v in unfinished.items() if v.get('descent')} == alias.keys() & unfinished.keys() and len(alias.keys() & unfinished.keys()) == 68
    assert all(unfinished[k].get('same_calculation_as',k) == alias[k] for k in alias.keys() & unfinished.keys())
    assert {k for k in canonical if unfinished.get(k,{}).get('native_branch') == 'none'} == SUPPLIED_ONLY
    assert witnesses['records_with_liquid_label'] == 48 and witnesses['largest_liquid_to_vapor_witness_distance'] <= 2.35e-12
    ratios = [v['declared_pressure_Pa']/v['model_bubble_pressure_Pa'] for v in canonical.values()]
    assert [round(min(ratios),7),round(max(ratios),7)] == [.1731113,.9806738]
    alternatives = {}
    for folder in sorted((SENSITIVITY/'mdea').iterdir()):
        label = folder.name.split('-')[1]
        rows = [r for p in sorted(folder.glob('search-*.json.gz')) for r in stable.read(p)]
        assert len(rows) == len({r['key'] for r in rows}) == 11824 and {r['key'] for r in rows} == states.keys()
        refused = [r for r in rows if not r['available']]
        assert (len(refused),sum(r['message'].startswith('pressure reference') for r in refused)) == {'low':(1245,1024),'high':(1104,874)}[label]
        alternatives[label] = {r['key']:dict(complete=r['available'],descent=r['descent'],pressure_Pa=r.get('supplied_parent_pressure_Pa')) for r in rows}
    bubbles = {k.rsplit(':',1)[0] for k,v in unfinished.items() if stage(v)=='bubble reference'}
    assert len(bubbles) == 435
    masses = {c['component_id']:c['fixed']['molar_mass']['value']['magnitude'] for c in point['parameters']['components']}
    amine, rows = route.config['amine'], []
    def wt_percent(stock):
        mass = stock.get(amine,0.)*masses[amine]
        return 100*mass/(mass+stock.get('water',0.)*masses['water'])
    measured = observation_coordinates(spec,observations,wt_percent,amine)
    ranks = {q:sorted((i for i in measured if measured[i][q] is not None),key=lambda i:measured[i][q]) for q in ('MDEA_wt_percent','loading')}
    bounds = {q:[ids[0],ids[-1]] for q,ids in ranks.items()}
    bubble_values = {o['problem']:data[o['identity']]['value'] for o in observations
                     if o['constructor']=='observation' and o['kind']=='pressure' and data[o['identity']]['requested_tolerance_met']
                     and isinstance(spec.problems[o['problem']].P,eq.Free)}
    comparisons = Counter()
    for k,state in states.items():
        p = spec.problems.get(state.get('problem',k.removesuffix(':cap')+':initial'))
        T, stock = (p.T,p.feed.values) if p else (state['T'],state['stock'])
        cap, refusal = data.get(state.get('cap_record')), unfinished.get(k)
        loading = cap['endpoint_loading'] if cap else state.get('a',stock.get('carbon-dioxide',0.)/stock[amine] if stock.get(amine) else None)
        ratio = state.get('c',1.05) if p is None or isinstance(p.P,eq.Free) else None
        pressure = (refusal or {}).get('supplied_parent_pressure_Pa') if ratio else p.P
        i, role = links.get(k,(state.get('cap_record'),'capped endpoint' if cap else None))
        source = measured.get(i)
        problem = source['problem'] if source else None
        reconstructed = (ratio and pressure is None and not refusal and problem in bubble_values
                         and calculation_declaration(p)==calculation_declaration(spec.problems[problem]))
        if reconstructed:
            pressure = ratio*bubble_values[problem]
        basis = 'source-state loading' if source and loading == source['loading'] and not data[i]['group'].startswith('Merkley') else 'prescribed diagnostic'
        if p is None:
            basis = 'constructed grid'
        elif cap:
            basis = 'missing endpoint' if loading is None else 'calculated cap'
        elif loading is None:
            basis = 'undefined (no MDEA)'
        coordinates = dict(MDEA_wt_percent=wt_percent(stock),loading=loading)
        support = {}
        for q,v in coordinates.items():
            lo,hi = (round(measured[i][q],12) for i in bounds[q])
            support[q] = basis if v is None else 'below' if round(v,12) < lo else 'above' if round(v,12) > hi else 'within'
        failure_stage = stage(refusal) if refusal else None
        comparisons[tier(k),failure_stage or 'completed',*support.values()] += 1
        rows.append(dict(key=k,tier=tier(k),T_K=T,**coordinates,observation=i,observation_role=role if source or i is None else 'phase check outside current observations',loading_basis=basis,
                         measured_range=support, reconstructed_from_bubble_problem=problem if reconstructed else None,
                         pressure_Pa=pressure,bubble_multiplier=ratio,complete=refusal is None,descent=k in alias,
                         stage=failure_stage,message=refusal['message'] if refusal else None,
                         reaction_ranges=route.marks(T,p),**{label:records[k] for label,records in alternatives.items()}))
    route.write('coverage.json', rows)
    route.write('coverage-counts.json', dict(tiers=Counter(map(tier,states)), unfinished={'data':225,'grid':874}, bubble_states=len(bubbles),
                                            stages=[dict(tier=t,stage=s,count=n) for (t,s),n in sorted(counts.items())], canonical=canonical, aliases=alias,
                                            measured_range_counts=[dict(tier=t,stage=s,MDEA_wt_percent=w,loading=a,count=n) for (t,s,w,a),n in sorted(comparisons.items())],
                                            measured_bounds=bounds, measured_observations=measured))
    return alias


def reductions(route, alias, links, data):
    crosswalk = [dict(key=k, canonical=v, identity=i, role=role, scored=data[i]['status']=='Available', observation=data[i]) for k,v in alias.items() for i,role in [links[k]]]
    def statistics(rows):
        pairs = [(r['observed'],r['value']) for r in rows if r['status']=='Available']
        return dict(total=len(rows),available=len(pairs),statistics=deviation_statistics(pairs,rows[0]['unit']) if pairs else None)
    def pressure(r):
        return next((float(Decimal(str(r['row'][field]))*scale) for field,scale in
                     (('pressure_Pa',1),('proposed_pressure_kPa',1000),('pressure_MPa',1000000)) if field in r['row']),None)
    group = lambda r: (r['group'],r['role'],r['unit'])
    selected = {r['identity'] for r in crosswalk}
    weak = {r['identity'] for r in crosswalk if r['canonical'] in SUPPLIED_ONLY}
    tables = []
    for baseline in stable.read(RESULTS/'comparison.json')['groups']:
        g = baseline['group'],baseline['role'],baseline['unit']
        rows = [r for r in data.values() if group(r)==g]
        pairs = statistics(rows)['statistics']
        assert (pairs is None and baseline['bounded']['AARD_percent'] is None) or abs(pairs['AARD_percent']-baseline['bounded']['AARD_percent']) < 1e-10
        if not selected.intersection(r['identity'] for r in rows):
            continue
        for P in [None, *sorted({pressure(r) for r in rows if pressure(r) is not None})]:
            original = [r for r in rows if P is None or pressure(r)==P]
            subsets = (original,[r for r in original if r['identity'] in selected],[r for r in original if r['identity'] not in selected],[r for r in original if r['identity'] not in weak])
            tables.append(dict(group=g,pressure_assignment_Pa=P,**{k:statistics(q) for k,q in zip(('all','linked','excluded','excluded_supplied_only'),subsets,strict=True)}))
    route.write('observation-crosswalk.json',crosswalk)
    route.write('property-deviations.json',tables)


if __name__ == '__main__':
    route, point = Route(DECLARATION,OUT), stable.read(RESULTS/'endpoint.json')
    spec = route.bind(point)
    obs = spec.inputs['observations']
    observations = obs['fitted']+obs['comparisons']
    links = {o[f]:(o['identity'],f) for o in observations for f in ('problem','initial','final','bubble') if f in o}
    links.update({p['problem']:(p['identity'].rsplit(':',1)[0], 'phase check') for p in obs['phase_states']})
    links.update({f'Merkley-capped:{j}:phase':(k,'prescribed diagnostic loading') for j,k in enumerate(('fit:125','fit:126','comparison:370','fit:127','fit:128','comparison:374'),3)})
    data = {r['identity']:r for r in stable.read(RESULTS/'data-rows.json')}
    alias = coverage(route,point,spec,{s['key']:s for s in route.states(spec)},observations,links,data)
    reductions(route,alias,links,data)
    coexistence_roots(route,spec)
