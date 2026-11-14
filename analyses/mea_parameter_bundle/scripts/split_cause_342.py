"""Fixed-composition energies and parameter moves for issue #342; no fitting."""
import itertools
import math
import os
import sys
from concurrent.futures import ProcessPoolExecutor
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))
import adoption_297 as a
import phase_diagnosis_255 as p
r = a.r
OUT = r.B/'results/split-cause-342'
REGISTRY = r.B/'results/reduced-refit/split-registry.json'
STABLE = r.B/'results/reduced-refit/F2/previous/unpenalized/parameters-0.json'
TERMS = p.TERMS + ['pv', 'ideal_and_standard']
def energy(mapping, parent, payload, isobaric=False):
    model = p.f.epcsaft.Mixture(p.f.epcsaft.Parameters.from_mapping(mapping), thermochemistry=p.f.thermal.record())
    phases = [p.f.eq.Phase(ph['identity'], kind=ph['role'], support=ph['support']) for ph in payload['phases']]
    problem = p.f.flash_problem(p.e.request(mapping,313.15,.11), parent['loading'],parent['temperature_K'],parent['pressure_Pa'],phases)
    coords, cursor, total, states = list(payload['coordinates']), 0, dict.fromkeys(TERMS,0.), []
    for ph in payload['phases']:
        x = dict(zip(ph['support'],ph['mole_fractions'],strict=True))
        state = model.state(parent['temperature_K'],P=parent['pressure_Pa'],x=x,phase=ph['role']) if isobaric else model.state(parent['temperature_K'],rho=ph['molar_density_mol_m3'],x=x)
        rho = state.molar_density
        states.append(dict(phase=ph['identity'],kind=ph['role'],amount_mol=ph['amount_mol'],density_mol_m3=rho,pressure_Pa=state.pressure,pressure_error_Pa=state.pressure-parent['pressure_Pa'],pressure_density_derivative=state.pressure_density_derivative,**x))
        cursor += len(ph['support'])+1
        coords[cursor] = math.log(model._model.packing_fraction_coefficient(parent['temperature_K'],[x.get(i,0.) for i in model.component_ids])*rho)
        cursor += 1
        for term in p.TERMS:
            total[term] += ph['amount_mol']*getattr(state,term)
        total['pv'] += ph['amount_mol']*parent['pressure_Pa']/(rho*8.31446261815324*parent['temperature_K'])
        assert abs(math.fsum(getattr(state,t) for t in p.TERMS)-state.residual_helmholtz) < 1e-10
    objective = p.f.eq.compile_problem(model,problem).evaluate(coords).objective
    total['ideal_and_standard'] = objective-math.fsum(total.values())
    return dict(total,states=states), objective
def alternative(mapping):
    import copy
    mapping = copy.deepcopy(mapping)
    old = r.read(r.B/'data/input/fit-campaigns/effective-F3-A.json')
    next(f for f in mapping['model_families'] if f['kind']=='permittivity')['choice'] = 'solvent-only'
    for component in mapping['components']:
        component['coefficients'] = [v for v in component['coefficients'] if v['family'] not in ('dielectric_volume','dielectric_temperature')]
        source = next(x for x in old['components'] if x['component_id']==component['component_id'])
        component['coefficients'] += [v for v in source['coefficients'] if v['family']=='relative_permittivity']
    mapping['correlations'] += [v for v in old['correlations'] if v['family']=='relative_permittivity']
    return mapping
def decompose():
    wide, stable = [r.s.parameter_mapping(path) for path in (r.STARTS['wide'],STABLE)]
    rows, compositions, relaxed = [], [], []
    reference = {x['index']:x for x in r.read(OUT/'F2/raw.json.gz')} if (OUT/'F2/raw.json.gz').exists() else {}
    for path in sorted((p.OLD/'comparison').glob('split-seeded-*.json')):
        split = r.read(path)
        if not split.get('confirmed'):
            continue
        parent = r.read(p.OLD/f'comparison/point-{split["index"]}.json')
        for name,mapping in [('wide',wide),('F2',stable),('wide-solvent-only',alternative(wide)),('F2-solvent-only',alternative(stable)),('wide-isobaric',wide),('F2-isobaric',stable),('wide-solvent-only-isobaric',alternative(wide)),('F2-solvent-only-isobaric',alternative(stable))]:
            before,g0 = energy(mapping,parent,parent['final'],isobaric=name.endswith('isobaric'))
            if name in ('F2','F2-isobaric') and reference:
                _,gr = energy(mapping,parent,reference[split['index']]['final'],isobaric=name.endswith('isobaric'))
                _,gs = energy(mapping,parent,split['result'],isobaric=name.endswith('isobaric'))
                relaxed.append(dict(record=name,source=str(path.relative_to(r.ROOT)),index=split['index'],old_parent_g_over_rt=g0,F2_parent_g_over_rt=gr,split_g_over_rt=gs,split_minus_F2_parent_over_rt=gs-gr))
            after,g1 = energy(mapping,parent,split['result'],isobaric=name.endswith('isobaric'))
            delta = {t:after[t]-before[t] for t in TERMS[:-1]}
            delta['ideal_and_standard'] = (g1-g0)-math.fsum(delta.values())
            error = abs(math.fsum(delta.values())-(g1-g0))/abs(g1-g0)
            assert error <= 1e-12
            if name in ('wide','wide-isobaric'):
                assert abs((g1-g0)-split['delta_G_over_RT'])/max(1.,abs(g0),abs(g1)) <= 1e-12
            rows.append(dict(source=str(path.relative_to(r.ROOT)),index=split['index'],record=name,temperature_K=parent['temperature_K'],loading=parent['loading'],pressure_Pa=parent['pressure_Pa'],delta_g_over_rt=g1-g0,closure_relative=error,**delta))
            compositions.extend(dict(record=name,configuration=kind,index=split['index'],source=str(path.relative_to(r.ROOT)),**ph) for kind,total in [('parent',before),('split',after)] for ph in total['states'])
    p.f.table(OUT/'contributions.csv',rows)
    p.f.table(OUT/'compositions.csv',compositions)
    if relaxed:
        p.f.table(OUT/'F2-parent-comparison.csv',relaxed)
    assert len(rows)==408
    p.f.table(OUT/'contribution-changes.csv',[dict(record=x['record'],source=x['source'],index=x['index'],**{t:rows[i+1][t]-x[t] for t in TERMS+['delta_g_over_rt']}) for i,x in enumerate(rows) if x['record'].startswith('wide')])
def state(task):
    native = p.f.stability
    def checked(model, problem, result):
        return native(model,problem,result,supplied=task[3],retained=native(model,problem,result))
    p.f.stability = checked
    try:
        raw, reduced = r._census(task[:3])
    finally:
        p.f.stability = native
    supplied = raw.get('stability',[{}])[0].get('supplied_trials',[])
    reduced['supplied_negative'] = sum(t['quantities']['tpd_over_rt']<0 for t in supplied)
    reduced['complete'] &= len(supplied)==len(task[3]) and all(t['evidence']=='evaluated' for t in supplied)
    for report in raw.get('stability',[]):
        report['supplied_distances_over_rt'] = [t['quantities']['tpd_over_rt'] for t in report.pop('supplied_trials',[])]
    print(task[1]['index'],reduced['resolved'],flush=True)
    return raw,reduced
def search(name, mapping):
    directory = OUT/name
    if (directory/'census.json').exists():
        return r.read(directory/'census.json')
    directory.mkdir(parents=True,exist_ok=True)
    registry = r.read(REGISTRY)
    chosen = r.read(p.OLD/'inputs/states.json')
    memory = int(next(x for x in open('/proc/meminfo') if x.startswith('MemAvailable')).split()[1])
    with ProcessPoolExecutor(min(int(os.environ['AGENT_HEAVY_CORES']),max(1,memory//1000000)),initializer=r.verify) as pool:
        results = list(pool.map(state,[(mapping,x,directory/f'{x["index"]}.json',registry['trials']) for x in chosen]))
    raw, reduced = map(list,zip(*results,strict=True))
    summary = dict(states=len(raw),resolved=sum(x['resolved']>0 for x in reduced),supplied_negative_states=sum(x.get('supplied_negative',0)>0 for x in reduced),incomplete=sum(not x['complete'] for x in reduced),registry_sha256=registry['sha256'],rows=reduced)
    p.dump(directory/'raw.json.gz',raw)
    p.dump(directory/'parameters.json',mapping)
    new, occurrences = [], 0
    for row in raw:
        for report in row.get('stability',[]):
            for t in report['trials']:
                if t['resolved_descent']:
                    occurrences, witness = occurrences+1, dict(kind=t['phase']['kind'],support=t['phase']['support'],composition=t['composition'],packing=math.exp(t['split_coordinates'][-1]))
                    if witness not in registry['trials']:
                        registry['trials'].append(witness)
                        new.append(witness)
    if occurrences:
        registry['before_dedup'] += occurrences-registry['sources'].get(str((directory/'raw.json.gz').relative_to(r.ROOT)),0)
        registry['sha256'] = a.hashlib.sha256(p.json.dumps(registry['trials'],sort_keys=True).encode()).hexdigest()
        registry['after_dedup'] = len(registry['trials'])
        registry['sources'][str((directory/'raw.json.gz').relative_to(r.ROOT))] = occurrences
        p.dump(REGISTRY,registry)
    summary['new_resolved_trials'] = len(new)
    p.dump(directory/'census.json',summary)
    print(name,{k:v for k,v in summary.items() if k!='rows'},flush=True)
    return summary
def moves():
    wide, stable = [r.s.parameter_mapping(path) for path in (r.STARTS['wide'],STABLE)]
    v,z = map(r.s.parameter_values,(wide,stable))
    changes = {k:z[k] for k in z if v.get(k)!=z[k]}
    p.dump(OUT/'parameter-changes.json',{k:dict(wide=v[k],F2=x) for k,x in changes.items()})
    results = {name:search(name,mapping) for name,mapping in [('wide',wide),('F2',stable)]}
    assert results['wide']['resolved']==54 and results['F2']['resolved']==0
    candidates = list(changes)
    for size in range(1,len(candidates)+1):
        zero = []
        for i,group in enumerate(itertools.combinations(candidates,size)):
            name = f'move-{size}-{i:02d}'
            result = search(name,r.s.with_parameter_values(wide,{k:z[k] for k in group}))
            results[name] = dict(parameters=group,**result)
            p.dump(OUT/'moves.json',results)
            if result['resolved']==result['supplied_negative_states']==result['incomplete']==0:
                zero.append(group)
        if zero:
            p.dump(OUT/'smallest-groups.json',dict(size=size,groups=zero))
            break
if __name__=='__main__':
    OUT.mkdir(exist_ok=True)
    r.verify()
    p.dump(OUT/f'provenance-{sys.argv[1]}.json',dict(base_commit=a.subprocess.check_output(['git','rev-parse','HEAD'],text=True).strip(),engine_commit=a.COMMIT,wheel_sha256=a.SHA,inputs={str(path.relative_to(r.ROOT)):a.sha(path) for path in (r.STARTS['wide'],STABLE,REGISTRY)},producer_sha256=a.sha(__file__),command=sys.argv))
    if sys.argv[1]=='decompose':
        decompose()
    else:
        moves()
