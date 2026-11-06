"""Fixed-parameter diagnosis of retained MEA liquid splits; no fitting."""
import csv
import gzip
import json
import math
import os
from pathlib import Path
import sys
import time
from concurrent.futures import ProcessPoolExecutor

ROOT = Path.cwd()
B = ROOT/'analyses/mea_parameter_bundle'
sys.path[:0] = [str(B/'scripts'), str(B/'calibration-misfit'), str(ROOT/'src')]
import phase_search_214 as p
import fit_observations as o
import fit_campaign as c
f, e = p.f, p.e
OUT = B/'results/phase-diagnosis-255'
OLD = p.OUT
TERMS = ['hard_chain','dispersion','association','debye_huckel','born','cation_mixing','dipolar']
S = 'component/protonated-monoethanolamine/'
W = 'pair/protonated-monoethanolamine/water/k_ij'
K = 'pair/carbamate-anion/protonated-monoethanolamine/k_ij'
BO = ['component/'+x+'/born_diameter' for x in ('protonated-monoethanolamine','carbamate-anion')]

def dump(path, data):
    path.parent.mkdir(parents=True, exist_ok=True)
    if path.suffix=='.gz':
        with gzip.open(path,'wt') as h: json.dump(data,h,allow_nan=False)
    else: f.s.write_json(path,data)

def candidates():
    wide, final = [f.s.parameter_mapping(p.FITS[x]) for x in ('comparison','reported')]
    v, z = map(f.s.parameter_values,(wide, final))
    result = [('wide',wide,{}),('final',final,{})]
    def add(name,base,changes): result.append((name,f.s.with_parameter_values(base,changes),changes))
    def size(x): return {S+'segment_diameter':x,S+'debye_huckel_diameter':x,S+'packing_diameter':.88*x}
    for x in (4.5,4.8,5.,5.2,5.35): add('wide-size-'+str(x),wide,size(x))
    for x in (-.1,-.125,-.15,-.175,-.2,-.35,-.5): add('wide-water-'+str(x),wide,{W:x})
    for x in (-.8,-.5,0.): add('wide-pair-'+str(x),wide,{K:x})
    for x in (4.9,4.5,4.): add('wide-born-'+str(x),wide,dict.fromkeys(BO,x))
    for x in (4.8,5.,5.2,5.35): add('wide-size-water-'+str(x),wide,dict(size(x),**{W:-.5}))
    for x in (5.34,5.30,5.2,5.,4.8): add('final-size-'+str(x),final,size(x))
    for x in (-.499,-.49,-.45): add('final-water-'+str(x),final,{W:x})
    add('final-pair',final,{K:-.99})
    add('final-born',final,dict.fromkeys(BO,4.99))
    add('final-size-wide',final,size(v[S+'segment_diameter']))
    for x in (-.35,-.2,-.1,0.): add('final-water-'+str(x),final,{W:x})
    for fraction in (.25,.5,.75,1.):
        keys=[W,W+'/reciprocal_temperature_slope']
        add('wide-water-law-'+str(fraction),wide,{k:v[k]+fraction*(z[k]-v[k]) for k in keys})
    for diameter in (4.,4.5):
        add('wide-water-born-'+str(diameter),wide,dict({W:-.1},**dict.fromkeys(BO,diameter)))
    for pair in (-.8,-.5): add('wide-water-pair-'+str(pair),wide,{W:-.1,K:pair})
    add('final-water--0.3',final,{W:-.3})
    dump(OUT/'parameter-values.json',dict(wide=v,final=z))
    return result

def decomposition():
    mapping=f.s.parameter_mapping(p.FITS['comparison'])
    model=f.epcsaft.Mixture(f.epcsaft.Parameters.from_mapping(mapping),thermochemistry=f.thermal.record())
    rows=[]
    def totals(result,T,P):
        total=dict.fromkeys(TERMS+['pv'],0.)
        for phase in result['phases']:
            state=model.state(T,rho=phase['molar_density_mol_m3'],x=dict(zip(phase['support'],phase['mole_fractions'],strict=True)))
            n=phase['amount_mol']
            for term in TERMS: total[term]+=n*getattr(state,term)
            total['pv']+=n*P/(phase['molar_density_mol_m3']*8.31446261815324*T)
            assert abs(sum(getattr(state,t) for t in TERMS)-state.residual_helmholtz)<1e-10
        return total
    for path in sorted((OLD/'comparison').glob('split-seeded-*.json')):
        split=e.load(path)
        if not split.get('confirmed'): continue
        parent=e.load(OLD/'comparison'/f'point-{split["index"]}.json')
        T,P=parent['temperature_K'],parent['pressure_Pa']
        a,b=totals(parent['final'],T,P),totals(split['result'],T,P)
        row=dict(index=split['index'],trial=split['native_trial_index'],temperature_K=T,pressure_Pa=P,loading=parent['loading'],source=str(path.relative_to(ROOT)),delta_g_over_rt=split['delta_G_over_RT'])
        row.update({t:b[t]-a[t] for t in a})
        row['ideal_and_standard']=row['delta_g_over_rt']-sum(row[t] for t in a)
        liquids=sorted((ph for ph in split['result']['phases'] if ph['role']=='liquid'),key=lambda ph: ph['mole_fractions'][ph['support'].index('water')])
        assert len(liquids)==2
        phase_states=[model.state(T,rho=ph['molar_density_mol_m3'],x=dict(zip(ph['support'],ph['mole_fractions'],strict=True))) for ph in liquids]
        for term in TERMS:
            row['poor_minus_rich_'+term]=getattr(phase_states[0],term)-getattr(phase_states[1],term)
        row['poor_water_x'],row['rich_water_x']=[ph['mole_fractions'][ph['support'].index('water')] for ph in liquids]
        rows.append(row)
    f.table(OUT/'contributions.csv',rows)
    assert len(rows)==51

def reduce_state(raw):
    reports=raw.get('stability',[])
    trials=[t for report in reports for t in report['trials']]
    parent=raw.get('final',{})
    admitted=bool(parent.get('success') and parent.get('requested_tolerance_met') and max(map(abs,parent.get('raw_residuals',[math.inf])))<=1e-10 and parent['reduced_hessian_minimum']>=0 and all(v>0 for v in parent['pressure_density_derivatives']))
    unresolved=sum(t['evidence'] in ('unresolved','indeterminate') for t in trials)
    failed=sum(not t['optimizer']['success'] for t in trials)
    complete=admitted and bool(reports) and all(r['completed'] for r in reports) and len(trials)==9 and failed==0 and unresolved==0
    return dict(index=raw['index'],classification=raw['classification'],resolved=sum(t['resolved_descent'] for t in trials),minimum_tpd=min((t['quantities']['tpd_over_rt'] for t in trials if 'tpd_over_rt' in t['quantities']),default=None),failed_optimizers=failed,trials=len(trials),parent_admitted=admitted,reports_completed=bool(reports) and all(r['completed'] for r in reports),unresolved_trials=unresolved,complete=complete)

def regenerate_reductions():
    summaries=[]
    for row in csv.DictReader((OUT/'probes.csv').open()):
        directory=OUT/row['name']
        with gzip.open(directory/'phase-results.json.gz','rt') as h: raw=json.load(h)
        reduction=[reduce_state(r) for r in raw]
        summary=e.load(directory/'summary.json')
        assert len(reduction)==summary['states']
        assert sum(r['resolved']>0 for r in reduction)==summary['descent_states']
        summary['incomplete_states']=sum(not r['complete'] for r in reduction)
        dump(directory/'reduction.json',reduction)
        dump(directory/'summary.json',summary)
        row['incomplete_states']=summary['incomplete_states']
        summaries.append(row)
    f.table(OUT/'probes.csv',summaries)

def probe(task):
    name,mapping,changes=task
    started=time.monotonic()
    cpu=time.process_time()
    directory=OUT/name
    directory.mkdir(exist_ok=True)
    if (directory/'summary.json').exists():
        assert e.load(directory/'parameters.json')==mapping
        return e.load(directory/'summary.json')
    if (directory/'point.json').exists(): (directory/'point.json').rename(directory/'interrupted-point.json')
    dump(directory/'parameters.json',mapping)
    confirmed=sorted({int(r['index']) for r in csv.DictReader((OLD/'split-confirmations.csv').open()) if r['confirmed']=='True'})
    results=[]
    def run(index):
        old=e.load(OLD/'comparison'/f'point-{index}.json')
        row={k:old[k] for k in ('index','temperature_K','loading','pressure_Pa')}
        path=directory/'point.json'
        f.family_job(mapping,e.request(mapping,313.15,.11),row,[],path)
        raw=e.load(path)
        results.append(raw)
        return reduce_state(raw)
    reduction=[run(i) for i in confirmed]
    if all(r['resolved']==0 for r in reduction):
        reduction.extend(run(i) for i in range(162) if i not in confirmed)
    dump(directory/'phase-results.json.gz',results)
    (directory/'point.json').unlink()
    dump(directory/'reduction.json',reduction)
    spec=e.load(B/'results/engine-3e83e19c-refit-chain/a6/spec.json')
    _, rows=o.stage6_rows(spec,mapping)
    weights=c.stage6_weights(spec,[r for r,_ in rows],1.)
    values=o.replay(mapping,[(r['id'],item,w) for (r,item),w in zip(rows,weights,strict=True)])
    dump(directory/'replay.json',values)
    available=all(v['status']=='Available' and v['requested_tolerance_met'] for v in values)
    loaded=[v for v in values if v['target'] in spec['loaded_density_ids']]
    summary=dict(name=name,changes=changes,states=len(reduction),descent_states=sum(r['resolved']>0 for r in reduction),incomplete_states=sum(not r['complete'] for r in reduction),minimum_tpd=min((r['minimum_tpd'] for r in reduction if r['minimum_tpd'] is not None),default=None),rows=len(values),available=available,cost=sum(v.get('cost',0.) for v in values) if available else None,loaded_within_2s=sum(abs(v.get('residual',math.inf))<=2 for v in loaded),loaded_rows=len(loaded),wall_s=time.monotonic()-started,cpu_s=time.process_time()-cpu)
    dump(directory/'summary.json',summary)
    print(json.dumps(summary),flush=True)
    return summary

def engine_capability():
    import hashlib
    from epcsaft import regression as r
    mapping=f.s.parameter_mapping(p.FITS['comparison'])
    parameters=f.epcsaft.Parameters.from_mapping(mapping)
    problem=f.flash_problem(e.request(mapping,313.15,.11),.4,333.15,20000.)
    errors={}
    try:r.observation(parameters,'stability',problem,observed=0.,form='difference',scale=1.)
    except f.epcsaft.ParameterError as exc: errors['stability_kind']=str(exc)
    problem.phases=f.eq.Discover()
    try:r.observation(parameters,'pressure',problem,observed=20000.,form='difference',scale=1.)
    except f.epcsaft.ParameterError as exc: errors['discovery_observation']=str(exc)
    assert len(errors)==2
    paths=[Path(r.__file__),Path(r.__file__).with_name('_core.pyi')]
    dump(OUT/'engine-capability.json',dict(errors=errors,observation_kinds=list(r._KINDS),sources={str(p):hashlib.sha256(p.read_bytes()).hexdigest() for p in paths},locators=['regression.py:483-553 (declared phases required, unknown kind refused)','regression.py:718-790 (fit arguments)','_core.pyi:3774-3836 (ObservationKind)','_core.pyi:4704-4815 (CheckMetric, CheckGroup)']))

if __name__=='__main__':
    f.s.verify_wheel()
    if sys.argv[1:]==['--reduce-only']:
        regenerate_reductions()
        sys.exit(0)
    OUT.mkdir(exist_ok=True)
    tasks=candidates()
    dump(OUT/('provenance-resume.json' if (OUT/'provenance.json').exists() else 'provenance.json'),dict(engine_commit=f.s.ENGINE_COMMIT,wheel_sha256=f.s.sha256(f.s.installed_wheel()),script_sha256=f.s.sha256(Path(__file__)),inputs={str(v.relative_to(ROOT)):f.s.sha256(v) for v in p.FITS.values()},command=sys.argv))
    decomposition()
    engine_capability()
    # Independent fixed vectors; one numerical-library thread per process, memory-sized pool.
    memory=int(next(x for x in open('/proc/meminfo') if x.startswith('MemAvailable')).split()[1])
    with ProcessPoolExecutor(max_workers=min(len(tasks),os.cpu_count(),max(1,memory//750000))) as pool:
        summaries=list(pool.map(probe,tasks))
    f.table(OUT/'probes.csv',summaries)
