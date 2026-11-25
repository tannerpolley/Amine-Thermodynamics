"""Release-grid, measured-pressure and property comparisons for the selected MEA fit."""
# ruff: noqa: E402
from functools import partial
from hashlib import sha256
import json
import sys
from time import monotonic

from refit import OUT, WORK, MEA, P_REF, fingerprint, put, r
from phase_replays import point_for
import mea_pressure as pressure
import mea_stability as stability
from objective_weights_420 import census_classify, grid_classify

ALLOWANCE = 1500.


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


if __name__=='__main__':
    stability.a.study.reuse.bind_wheel()
    r.verify()
    stability.OUT = OUT
    _,point = point_for('MEA','selected','mea-screens')
    report = pilot(point) if not (OUT/'MEA/screen-pilot.json.gz').exists() else r.read(OUT/'MEA/screen-pilot.json.gz')
    if sys.argv[1:]!=['--pilot']:
        screens(point,report)
