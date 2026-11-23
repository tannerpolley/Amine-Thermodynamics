"""Apply the accepted AMP penalty and retreat rules to the #404 fits."""
import math
import time

from part_ii import jsonable
from refit_404 import DECLARATIONS, PUBLISHED, RUN, Route, check_fixed, record_f0_source, replace_fixed, source_values, stable
import reduced_refit_338 as reduced


def search(route, point, states, *, trial_set=None):
    started = time.monotonic()
    rows = route.grid(point, states, trial_set=trial_set)
    tally = stable.tally(rows)
    tally['seconds'] = time.monotonic()-started
    tally['unavailable_rows'] = [r for r in rows if not r['available']]
    tally['descent_rows'] = [r for r in rows if stable.descent(r)]
    recorded_rows = jsonable(rows)
    records = sorted(route.out.glob('search-*.json'), key=lambda p: int(p.stem.split('-')[-1]), reverse=True)
    tally['search_record'] = next(p.name for p in records if stable.read(p) == recorded_rows)
    return tally


def complete(tally):
    return tally['available']==tally['states'] and not tally['descent']


def coordinate_differences(a, b):
    # Reaction enthalpy origins are reset at serialization. The bounds move by the fitted increment.
    return {x['identity']:dict(
        difference=(y['bounds'][0]-x['bounds'][0] if x.get('kind')=='reaction_enthalpy_shift'
                    else x['origin']-y['origin']), scale=x['scale'])
        for x,y in zip(a['coordinates'],b['coordinates'],strict=True) if x['identity']==y['identity']}


def penalty_trial(route, start, scale, enforced, reference, diagnostic_s):
    probe = Route(route.path,route.out/f'probe-{scale}')
    probe.workers = route.workers
    probe.controls = dict(route.controls,maximum_iterations=1)
    started = time.monotonic()
    report = stable.stage_fit('profile',0,scale,start,{},enforced,route=probe)
    measured = time.monotonic()-started
    # One native iteration includes its setup and final data and compressed replay.
    # Use the measured iteration times with the retained #344 evaluation counts.
    iteration_s = [x for x in report['iteration_seconds'] if x is not None]
    difference = max(reference['residual_evaluations']-report['residual_evaluations'],
                     reference['jacobian_evaluations']-report['jacobian_evaluations'],0)
    projected = measured + difference*math.fsum(iteration_s) + diagnostic_s
    timing = dict(seconds=measured,iteration_seconds=iteration_s,projected_stage_s=projected,
                  projected_from=reference['fit'],reference_residuals=reference['residual_evaluations'],
                  reference_jacobians=reference['jacobian_evaluations'],diagnostic_s=diagnostic_s,
                  residuals=report['residual_evaluations'],jacobians=report['jacobian_evaluations'],
                  status=report['status'],replay_available=report.get('endpoint_replay_available'),
                  workers=route.workers)
    route.write(f'profile-{scale}.json',timing)
    print('profile',route.out.name,scale,timing,flush=True)
    return bool(iteration_s and timing['replay_available'] and projected<=3600)


def alternative(route, point, states, enforced, expected_cost, fixed):
    """Verify the candidate on compressed and full domains after the shared bank is updated."""
    check_fixed(point,fixed)
    route.write('alternative-parameters.json',point)
    point = route.result('alternative-parameters.json')
    check_fixed(point,fixed)
    values, ok, cost = route.replay(point)
    assert ok and abs(cost/expected_cost-1)<=1e-8
    result = dict(cost=cost, compressed=search(route,point,enforced), full=search(route,point,states))
    registry = route.result('split-record.json')
    trials = registry['trials']+registry['supplied_trials']
    for label, rows in [('compressed_recheck',enforced),('full_recheck',states)]:
        result[label] = search(route, point, rows, trial_set=trials)
    result['accepted'] = all(complete(r) for r in result.values() if isinstance(r,dict))
    result['supplied_trial_bank_count'] = len(trials)
    route.write('alternative-checks.json',result)
    if result['accepted']:
        route.write('alternative-replay.json',values)
        route.reduce(point)
        route.curves(point)
    return result


def main():
    source = source_values()
    fixed = {r['identity']:float(r['value']) for r in source[:2]}
    route = Route(DECLARATIONS/'AMP-05e94210.json',RUN/'main')
    fits = route.result('fits.json')
    # Check the chosen point first. Carry each new witness to later checks.
    fits.sort(key=lambda r:r['cost'])
    history = stable.read(PUBLISHED/'completed-penalty-stages.json')
    checked = []
    route.write('start-coordinate-differences.json',coordinate_differences(fits[0]['endpoint'],fits[1]['endpoint']))
    for fit in fits:
        i = fit['start']
        target = Route(route.path,RUN/f'penalty-{i}')
        target.check_run_output()
        point = fit['endpoint']
        states = target.states(target.bind(point))
        enforced = target.penalty_states(states,target.bind(point))
        assert len(enforced)==862 and not target.penalty_unavailable
        registry = target.out/'split-record.json'
        if not registry.exists():
            target.write('split-record.json',route.result('split-record.json'))
        finding = dict(start=i,cost=fit['cost'],liquid_directed=fit['search']['penalty_trigger'])
        if fit['stages'][-1]['status']!='converged':
            finding['disposition'] = 'unpenalized starts must converge'
        elif not fit['search']['penalty_trigger']:
            finding['disposition'] = 'no resolved liquid-directed descent'
            if fit['search']['stable']:
                finding['alternative'] = alternative(target,point,states,enforced,fit['cost'],fixed)
        else:
            for previous in checked:
                diff = coordinate_differences(point,previous['point'])
                finding.setdefault('coordinate_differences',{})[str(previous['start'])] = diff
                assert len(diff)==9
                if all(abs(d['difference']/d['scale'])<=target.controls['parameter_tolerance'] for d in diff.values()):
                    finding['duplicate_of'] = previous['start']
                    break
            if 'duplicate_of' not in finding:
                anchor = record_f0_source(replace_fixed(target.start(target.config['starts'][i]), fixed), source)
                eligibility = search(target,anchor,states)
                target.write('anchor-eligibility.json',eligibility)
                print('anchor',i,{k:eligibility[k] for k in ('states','available','descent','seconds')},flush=True)
                if complete(eligibility):
                    finding.update(penalize(target, i, point, anchor, states, enforced, history, eligibility['seconds'], fixed))
                    if finding['stages']:
                        checked.append(dict(start=i,point=point))
                else:
                    finding['disposition'] = 'declared anchor did not pass the full search'
        route.write('split-record.json',target.result('split-record.json'))
        target.write('finding.json',finding)
        print('alternative',i,finding.get('disposition','complete'),flush=True)
        if finding.get('runtime_stop'):
            break


def penalize(route, start, point, anchor, states, enforced, history, diagnostic_s, fixed):
    steps = []
    for i,scale in enumerate(stable.STAGES):
        reference, = [r for r in history if r['case']=='campaign' and r['fit'].startswith(f'start-{start}/penalized-{i}/')]
        if not penalty_trial(route,point,scale,enforced,reference,diagnostic_s):
            return dict(stages=steps,runtime_stop=True,disposition=f'scale {scale} timing or replay stop')
        before = time.monotonic()
        endpoint, report = reduced.fit(f'penalized-{i}',point,{},[],scale=scale,route=route,penalty_rows=enforced)
        step = dict(scale=scale,status=report['status'],data_cost=report.get('endpoint_replay_cost'),
                    penalty_cost=report['stability_cost'],native_compressed=report['stability_tally'],
                    seconds=time.monotonic()-before)
        steps.append(step)
        if endpoint is None or report['status']!='converged':
            return dict(stages=steps,disposition=f'scale {scale} did not return a converged replayable fit')
        point = endpoint
        check_fixed(point,fixed)
        step['full_search'] = search(route,point,states)
        diagnostic_s = step['full_search']['seconds']
        route.write('stages.json',steps)
        if complete(step['full_search']):
            result = alternative(route,point,states,enforced,step['data_cost'],fixed)
            if result['accepted']:
                return dict(stages=steps,alternative=result,disposition='converged penalty endpoint passed')
            anchor = point
    # One measured compressed sweep with the current bank and replay estimates the 21 #344 sweeps.
    sweep = search(route,anchor,enforced)
    started = time.monotonic()
    _, ok, _ = route.replay(anchor)
    replay_s = time.monotonic()-started
    projected = 21*(sweep['seconds']+replay_s)
    route.write('retreat-timing.json',dict(sweep=sweep,replay_s=replay_s,sweeps=21,projected_s=projected,workers=route.workers))
    print('retreat projection',start,projected,flush=True)
    if projected>3600 or not ok or not complete(sweep):
        return dict(stages=steps,runtime_stop=projected>3600,disposition='compressed anchor or one-hour retreat gate failed')
    check_fixed(route.segment(anchor,point,.5),fixed)
    stable.retreat('retreat',anchor,point,enforced,shifts=({},{}),route=route,optimizer_report=report)
    trace = route.result('retreat/retreat.json')
    if not (route.out/'retreat/candidate.json').exists():
        return dict(stages=steps,retreat=trace,disposition='no eligible retreat point')
    candidate = route.result('retreat/candidate.json')
    result = alternative(route,candidate,states,enforced,trace['retreat_cost'],fixed)
    return dict(stages=steps,retreat=trace,alternative=result,
                disposition='retreated point passed' if result['accepted'] else 'retreat recheck failed')


if __name__=='__main__':
    main()
