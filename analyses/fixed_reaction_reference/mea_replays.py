"""Release-grid, measured-pressure and property comparisons for the selected MEA fit."""
# ruff: noqa: E402
from concurrent.futures import ProcessPoolExecutor
from functools import partial
from hashlib import sha256
import json
import sys
from time import monotonic
from types import SimpleNamespace

from refit import OUT, WORK, P_REF, fingerprint, put, r
from phase_replays import point_for, support_census
import mea_pressure as pressure
import mea_stability as stability
from objective_weights_420 import census_classify, grid_classify

ALLOWANCE = 1500.


def measured_identity(point, bank):
    return dict(endpoint_fingerprint=fingerprint(point),bank_fingerprint=fingerprint(bank),wheel=r.SHA)


def measured_batch(record, identity, names):
    assert all(record.get(k)==v for k,v in identity.items()), 'MEA batch endpoint, trial bank or wheel changed'
    rows = record['rows']
    assert [q['identity'] for q in rows]==names and all(q['wheel']==r.SHA for q in rows)
    return rows


def rebuild_measured(point, reference, names, bank, output, workers):
    started = monotonic()
    identity = measured_identity(point,bank)
    pilot = r.read(output/'measured-bound/pilot.json.gz')
    pilot_names = [q['identity'] for q in pilot['rows']]
    done = {q['identity'] for q in measured_batch(pilot,identity,pilot_names)}
    assert len(set(names))==321 and done<=set(names)
    pending = [i for i in names if i not in done]
    batches = [pending[i:i+8] for i in range(0,len(pending),8)]
    jobs = []
    for i, batch in enumerate(batches):
        path = output/f'measured-bound/{i}.json.gz'
        if path.exists():
            measured_batch(r.read(path),identity,batch)
        else:
            jobs.append((i,(point['parameters'],reference,batch,1.,P_REF,bank)))
    with ProcessPoolExecutor(workers) as pool:
        for (i,_), batch in zip(jobs,pool.map(stability.chunk,[args for _,args in jobs]),strict=True):
            stability.save(output/f'measured-bound/{i}.json.gz',dict(identity,rows=batch))
    stability.save(output/'measured-bound/inventory.json.gz',dict(identity,names=names,seconds=monotonic()-started))


def census_declaration(point):
    from final_evidence import flash_problem
    from heat_evidence_170 import request as heat_request

    request = heat_request(point['parameters'],313.15,.11)
    for reaction in request['reaction_system']['engine_reactions']:
        reference = reaction.get('engine_reference') or reaction.get('reference') or {}
        reaction['engine_reference'] = dict(reference,reference_pressure_pa=P_REF)

    def declaration(spec,state,scale):
        phases = [r.eq.Phase(q['identity'],kind=q['role'],support=q['support']) for q in state['final']['phases']]
        p = flash_problem(request,state['loading'],state['temperature_K'],state['pressure_Pa'],phases)
        return SimpleNamespace(problem=p._native(spec.parameters), declaration=p)

    return declaration


def census_support(point, main, offset, census, grid_bank, census_bank):
    spec = r.bind(point['parameters'],reaction_reference_pressure_pa=P_REF)
    spec.inputs['endpoint'] = point['parameters']
    return dict(grid=support_census(spec,main,r.stability_row,grid_bank),
                offset=support_census(spec,offset,r.stability_row,grid_bank),
                census=support_census(spec,census,census_declaration(point),census_bank,old_full=True))


def pilot(point):
    started = monotonic()
    grid_bank = r.read(stability.BASE/'split-trials.json')
    bank = r.read(stability.BASE/'split-registry.json')['trials']
    assert sha256(json.dumps(bank,sort_keys=True).encode()).hexdigest()==stability.a.REGISTRY
    main,offset = r.states()
    chosen = main[::19]+offset[::13]
    grid = r.grid(point['parameters'],chosen,grid_bank,capture=True,reaction_reference_pressure_pa=P_REF)
    grid_seconds = monotonic()-started
    r.OUT = WORK/'MEA/screen'
    indices = list(range(0,162,18))
    t = monotonic()
    census = r.census(point['parameters'],'pilot/census',dict.fromkeys(map(str,indices),bank),indices=indices,
                      keep_refusals=True,compact_supplied=True,confirm=census_classify,
                      reaction_reference_pressure_pa=P_REF)
    census_seconds = monotonic()-t
    measured = stability.measured(point['parameters'],'MEA',reaction_reference_pressure_pa=P_REF,pilot_only=True)
    projected = (grid_seconds*(len(main)+len(offset))/len(chosen)
                 + census_seconds*162/len(indices)
                 + measured['estimate_worker_s']/r.CORES)
    record = dict(endpoint_fingerprint=fingerprint(point),wheel=r.SHA,workers=r.CORES,
                  grid_seconds=grid_seconds,grid=grid,census_seconds=census_seconds,census=census,
                  census_rows=r.result('pilot/census/census-raw.json.gz'),measured=measured,
                  projected_seconds=projected, allowance_s=ALLOWANCE,
                  seconds=monotonic()-started, released=projected<=ALLOWANCE)
    put('MEA/screen-pilot.json.gz',record)
    print('MEA screen pilot',round(projected,2),'s projected',flush=True)
    return record


def display(point):
    start = monotonic()
    pressure.replay(point['parameters'],'MEA',reaction_reference_pressure_pa=P_REF,output=OUT)
    spec = r.bind(point['parameters'],reaction_reference_pressure_pa=P_REF)
    spec.inputs['endpoint'] = point['parameters']
    template = next(iter(pressure.requests()[0].values()))['request']
    rows = []
    for source in pressure.off_window_population():
        identity = 'off-window:'+source['observation_id']
        observed = float(source['CO2_pressure'])*1000
        try:
            record = pressure.pressure_record(spec,pressure.pressure_template(spec)[0],identity,
                dict(request=r.s.source_feed_request(template,source),targets=[dict(
                    source_identity=source['source_key'],observed=observed)]),group=source['source_key'])
            row, = r.d.evaluate(spec,[record])
        except (RuntimeError,ValueError) as error:
            row = dict(identity=identity,observed=observed,unit='Pa',group=source['source_key'],
                       status='Exception',message=f'{type(error).__name__}: {error}',value=None)
        rows.append(dict(row,role='comparison'))
    put('MEA/off-window.json.gz',dict(endpoint_fingerprint=fingerprint(point),wheel=r.SHA,rows=rows,seconds=monotonic()-start))


def screens(point, timing):
    if not timing['released']:
        return
    start = monotonic()
    display(point)
    summary = stability.a.study.reuse.mea_search('MEA',point['parameters'],None,output=WORK/'MEA/screen',
        resume=True,confirm=census_classify,reaction_reference_pressure_pa=P_REF)
    for name in ('grid','census-raw','census'):
        ending = '.json' if name=='census' else '.json.gz'
        data = r.result(f'search/{name}{ending}')
        put(f'MEA/screen/{name}.json.gz',dict(endpoint_fingerprint=fingerprint(point),wheel=r.SHA,data=data))
    grid = r.result('search/grid.json.gz')
    main,offset = r.states()
    classified = grid_classify(point['parameters'],[q for q in grid if r.descent(q)],main+offset,
                               bind=partial(r.bind,reaction_reference_pressure_pa=P_REF))
    measured = stability.measured(point['parameters'],'MEA',reaction_reference_pressure_pa=P_REF)
    put('MEA/screen/summary.json.gz',dict(endpoint_fingerprint=fingerprint(point),wheel=r.SHA,
        grid=summary,classifications=classified,measured=measured,seconds=monotonic()-start))


def measured_refinement(point):
    start = monotonic()
    mapping = point['parameters']
    reference = r.s.parameter_mapping(stability.REFERENCE/'F4/parameters.json')
    batches = sorted((OUT/'E/MEA/measured').glob('*.json.gz'))
    original = [q for path in batches for q in r.read(path) if not q['available'] and q.get('parent')
                and not q['parent']['physical_checks_pass']]
    eligible = [q for kind in ('liquid','liquid-vapour') for q in
                sorted((q for q in original if q['declared_parent']==kind),key=lambda q:q['identity'])[::13]][:8]
    names = [q['identity'] for q in eligible]
    args = (mapping,reference,names,.1,P_REF)
    recalculated = stability.chunk(args)
    elapsed = monotonic()-start
    projected = sum(q['seconds'] for q in recalculated)*len(original)/max(1,len(recalculated))/r.CORES
    admitted = bool(recalculated) and all(q['available'] and not q['witnesses'] for q in recalculated)
    released = admitted and projected<=140
    put('MEA/screen/refinement.json.gz',dict(endpoint_fingerprint=fingerprint(point),wheel=r.SHA,
        hypothesis='Tightening the equilibrium solve reduces the independent EOS pressure closure residual',
        original=eligible,recalculated=recalculated,eligible_count=len(original),seconds=elapsed,
        projected_seconds=projected,released=released))
    if not released:
        return
    rest = [q['identity'] for q in original if q['identity'] not in names]
    groups = [rest[i:i+4] for i in range(0,len(rest),4)]
    with ProcessPoolExecutor(r.CORES) as pool:
        for i,rows in enumerate(pool.map(stability.chunk,[(mapping,reference,g,.1,P_REF) for g in groups])):
            put(f'MEA/screen/refined/{i}.json.gz',dict(endpoint_fingerprint=fingerprint(point),wheel=r.SHA,rows=rows))


if __name__=='__main__':
    stability.a.study.reuse.bind_wheel()
    r.verify()
    stability.OUT = OUT
    _,point = point_for('MEA','selected','mea-screens')
    report = pilot(point) if not (OUT/'MEA/screen-pilot.json.gz').exists() else r.read(OUT/'MEA/screen-pilot.json.gz')
    if sys.argv[1:]==['--refinement']:
        measured_refinement(point)
    elif sys.argv[1:]!=['--pilot']:
        screens(point,report)
