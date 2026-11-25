"""Forecast and run an issue #440 lane under the retained per-lane budgets."""
# ruff: noqa: E402
import os
import resource
import sys
from time import monotonic

from refit import ALLOWANCE, OUT, ROUND7, attempt, continue_fit, put, r, select
from phase_replays import controls, point_for, screening


def projection(lane):
    designs = ('AMP_free','AMP_fixed') if lane=='AMP' else (lane,)
    per_design = {}
    for design in designs:
        pilot = r.read(OUT/f'{design}/B.json.gz')
        files = list((OUT/design/'screen').glob('**/pilot.json.gz'))
        assert len(files)==(2 if lane=='AMP' else 1), files
        batches = [r.read(p) for p in files]
        measured_fit = sum(pilot.get(k,0.) for k in ('fit_seconds','replay_seconds','diagnostic_seconds'))
        if pilot.get('replay_passed'):
            planned = measured_fit
            provenance = 'measured fixed-reference B fit and independent replay'
        else:
            initial = r.read(OUT/f'{design}/initial/B.json.gz')
            assert initial['matches_fit_failure'], initial
            measured_fit += initial['seconds']
            if lane=='MDEA':
                records = ROUND7/'C/salt/attempts'
                planned = max(r.read(p)['outcome.json']['seconds'] for p in records.glob('*.json.gz'))
            else:
                records = ROUND7/'AMP'/design.split('_')[1]
                planned = max(r.read(p)['seconds'] for p in records.glob('fit-*.json.gz'))
            provenance = 'maximum archived round-7 fit wall time because B returned no replayable endpoint'
        per_design[design] = dict(pilot_fit_replay_s=measured_fit,remaining_fit_s=2*planned,
            fit_projection_basis=provenance, pilot_screen_s=sum(q['seconds'] for q in batches),
            projected_screen_s=sum(q['projected_seconds'] for q in batches),
            setup_s=r.read(OUT/f'{design}/manifest.json.gz')['seconds'],
            B_iterations=pilot['report']['iterations'], B_status=pilot['report']['status'],
            screen_batches=[dict(path=str(p.relative_to(OUT)),rows=len(q['rows']),
                refused=sum(not x['available'] for x in q['rows']),seconds=q['seconds'],
                projected_seconds=q['projected_seconds']) for p,q in zip(files,batches,strict=True)])
    allowance = ALLOWANCE[designs[0]]
    # Include the old study's allowance for reductions and matched-pressure controls.
    projected = sum(sum(v[k] for k in ('setup_s','pilot_fit_replay_s','remaining_fit_s','pilot_screen_s',
                                       'projected_screen_s')) for v in per_design.values())
    record = dict(designs=per_design,workers=4,allowance_s=allowance,hard_stop_s=1.5*allowance,
                  projected_s=projected, disposition='released' if projected<=allowance else 'paused before expansion')
    put(f'{lane}/projection.json',record)
    return record


def expand(lane):
    report = projection(lane)
    print(lane,report['disposition'],round(report['projected_s'],2),'s',flush=True)
    if report['disposition']!='released':
        return
    start = monotonic()
    for design in report['designs']:
        for label in 'AC':
            if not (OUT/f'{design}/{label}.json.gz').exists():
                attempt(design,label)
        for label in 'ABC':
            continue_fit(design,label)
        select(design)
        for label in ('A','B','C','fixed-at-old'):
            controls(design,label)
        selected = r.read(OUT/f'{design}/selection.json')['selected']
        if selected is not None:
            run,point = point_for(design,'selected','property-replay')
            rows = run.reduce(point)
            record = r.read(OUT/f'{design}/{selected}.json.gz')
            path = f'{design}/properties.json.gz'
            properties = dict(endpoint_fingerprint=record['endpoint_fingerprint'],wheel=r.SHA,rows=rows)
            put(path,properties)
            if 'curve_rows' in run.config:
                try:
                    properties['curves'] = run.curves(point)
                except (FileNotFoundError,RuntimeError,ValueError) as error:
                    properties['curve_refusal'] = f'{type(error).__name__}: {error}'
                put(path,properties)
            screening(design,'selected')
    own, children = (resource.getrusage(who) for who in (resource.RUSAGE_SELF,resource.RUSAGE_CHILDREN))
    put(f'{lane}/expansion-timing.json',dict(wall_s=monotonic()-start,
        cpu_s=sum(q.ru_utime+q.ru_stime for q in (own,children)),peak_process_rss_KiB=max(q.ru_maxrss for q in (own,children)),
        workers=4, projected_s=report['projected_s']))


if __name__=='__main__':
    from refit import a
    a.study.reuse.bind_wheel()
    r.verify()
    lane = sys.argv[1]
    if sys.argv[2:]==['--project']:
        projection(lane)
    else:
        # The lane service supplies a 4-CPU and 4-GiB quota plus the cumulative
        # wall deadline. In-process affinity caps nested workers as well.
        cpus = sorted(os.sched_getaffinity(0))
        rank = {'DEA':0,'MDEA':1,'AMP':2}[lane]
        offset = 4*rank
        os.sched_setaffinity(0,cpus[offset:offset+4] or cpus[:4])
        expand(lane)
