"""Coverage and observation comparisons at the reported bounded MDEA endpoint (#421)."""
from collections import Counter

from binary_tpd_421 import binary
from bounded_binary_411 import DECLARATION, RESULTS, Route, stable
from part_ii import ROOT, deviation_statistics, eq

OUT = RESULTS.parent/'phase-search-421'
SENSITIVITY = RESULTS.parent/'shared-bicarbonate-417'
ALIASES = ROOT/'analyses/mea_parameter_bundle/results/release-recheck-414/mdea-comparison.json'
SUPPLIED_ONLY = {f'comparison:{i}:problem' for i in (157,161,201,221)}


def stage(row):
    if row['message'].startswith('pressure reference'):
        return 'bubble reference'
    return {(False,True): 'optimized unavailable', (True,False): 'supplied incomplete',
            (None,None): 'preparation failed'}[row.get('optimized_available'),row.get('supplied_available')]


def coverage(route, point, spec, states):
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
    data = {r['identity']:r for r in stable.read(RESULTS/'data-rows.json')}
    masses = {c['component_id']:c['fixed']['molar_mass']['value']['magnitude'] for c in point['parameters']['components']}
    amine, rows = route.config['amine'], []
    for k,state in states.items():
        p = spec.problems.get(state.get('problem',k.removesuffix(':cap')+':initial'))
        T, stock = (p.T,p.feed.values) if p else (state['T'],state['stock'])
        mass = stock.get(amine,0.)*masses[amine]
        cap, refusal = data.get(state.get('cap_record')), unfinished.get(k)
        loading = cap['endpoint_loading'] if cap else state.get('a',stock.get('carbon-dioxide',0.)/stock[amine] if mass else None)
        ratio = state.get('c',1.05) if p is None or isinstance(p.P,eq.Free) else None
        pressure = (refusal or {}).get('supplied_parent_pressure_Pa') if ratio else p.P
        rows.append(dict(key=k,tier=tier(k),T_K=T,MDEA_wt_percent=100*mass/(mass+stock.get('water',0.)*masses['water']),loading=loading,
                         pressure_Pa=pressure,bubble_multiplier=ratio,complete=refusal is None,descent=k in alias,
                         stage=stage(refusal) if refusal else None,message=refusal['message'] if refusal else None,
                         reaction_ranges=route.marks(T,p),**{label:records[k] for label,records in alternatives.items()}))
    route.write('coverage.json', rows)
    route.write('coverage-counts.json', dict(tiers=Counter(map(tier,states)), unfinished={'data':225,'grid':874}, bubble_states=len(bubbles),
                                            stages=[dict(tier=t,stage=s,count=n) for (t,s),n in sorted(counts.items())], canonical=canonical, aliases=alias))
    return unfinished, alias, canonical, alternatives


def reductions(route, spec, alias, canonical):
    data = {r['identity']:r for r in stable.read(RESULTS/'data-rows.json')}
    obs = spec.inputs['observations']
    links = {o[f]:(o['identity'],f) for role in ('fitted','comparisons') for o in obs[role] for f in ('problem','initial','final','bubble') if f in o}
    for p in obs['phase_states']:
        links[p['problem']] = (p['identity'].rsplit(':',1)[0], 'phase check')
    links.update({f'Merkley-capped:{j}:phase':(k,'prescribed diagnostic loading') for j,k in [(4,'fit:126'),(5,'comparison:370'),(8,'comparison:374')]})
    crosswalk = [dict(key=k, canonical=v, identity=i, role=role, observation=data.get(i)) for k,v in alias.items() for i,role in [links[k]]]
    def statistics(rows):
        pairs = [(r['observed'],r['value']) for r in rows if r['status']=='Available']
        return dict(total=len(rows),available=len(pairs),statistics=deviation_statistics(pairs,rows[0]['unit']) if pairs else None)
    pressure = lambda r: r['row'].get('pressure_Pa') if r['group'].startswith('Bottinger') else r['row'].get('proposed_pressure_kPa')
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
            tables.append(dict(group=g,pressure_assignment=P,**{k:statistics(q) for k,q in zip(('all','linked','excluded','excluded_supplied_only'),subsets,strict=True)}))
    route.write('observation-crosswalk.json',crosswalk)
    route.write('property-deviations.json',tables)
    return data
