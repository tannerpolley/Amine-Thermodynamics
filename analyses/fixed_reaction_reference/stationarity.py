"""Check feasible local descent and root guesses without changing the fit declaration."""
from copy import copy
from time import monotonic
import refit as f
from scipy.optimize import lsq_linear

def at_chart(run,spec,point,u):
    chart=f.reg.evaluate_coordinates(spec.parameters,spec.coordinates(),u,[],
                                     thermochemistry=spec.thermal)
    return run.endpoint_mapping(point, dict(optimizer=u,physical=chart.physical,
                                reactions=spec.fitted_reactions(chart)),point['coordinates'])

def stationarity(name,label, fractions=(1.,.5)):
    tick=monotonic()
    q = f.r.read(f.OUT/f'{name}/{label}.json.gz')
    p=q['endpoint']
    c=q['replay']['cost']
    run,_,_=f.configured(name,'stationarity-probe')
    spec=run.bind(p)
    lower,upper=(f.np.array([(d['bounds'][i]-d['origin'])/d['scale'] for d in p['coordinates']])
                 for i in (0,1))
    width=f.np.array([(d['bounds'][1]-d['bounds'][0])/d['scale'] for d in p['coordinates']])
    J=f.np.array(q['diagnostics']['jacobian_bound_normalized'])/width
    r=f.np.array([x['weighted_residual'] for x in q['replay']['rows']])
    linear=lsq_linear(J,-r,bounds=(lower,upper),method='bvls',tol=1e-13)
    assert linear.success, linear.message
    u=f.np.clip(linear.x,lower,upper)
    ju=J@u
    predicted=-float((r+0.5*ju)@ju)/c
    trials=[]
    for fraction in fractions:
        try:
            bounded_step=(fraction*u).tolist()
            point=at_chart(run,spec,p,bounded_step)
        except (ValueError,RuntimeError) as error:
            trials.append(dict(fraction=fraction,refusal=str(error),relative_reduction=None))
            continue
        trial=f.replay(run.bind(point))
        cost=trial['cost']
        trials.append(dict(fraction=fraction,point=point,endpoint_fingerprint=f.fingerprint(point),replay=trial,
                           relative_reduction=(c-cost)/c if cost is not None else None))
        if cost is not None and (c-cost)/c > q['controls']['function_tolerance']:
            break
    f.put(f'{name}/stationarity/{label}.json.gz',dict(endpoint=q['endpoint_fingerprint'],wheel=f.r.SHA,
        cost=c,relative_linearized_reduction=predicted,optimizer_step=u.tolist(),trials=trials,seconds=monotonic()-tick))
    print(name,label,predicted,[(v['fraction'],v['relative_reduction']) for v in trials],flush=True)

def root():
    tick=monotonic()
    man=f.r.read(f.OUT/'MDEA/manifest.json.gz')
    run,_,_=f.configured('MDEA','root-probe')
    start=man['start_A_declaration']
    bound=run.bind(start)
    records={}
    for label in ('B','C'):
        p=at_chart(run,bound,start,man['starts'][label]['optimizer'])
        spec=run.bind(p)
        attempt=f.r.read(f.OUT/f'MDEA/{label}.json.gz')
        row=spec.inputs['observations']['fitted'][attempt['report']['failures'][0]['observation']]
        args=row['arguments']
        prob=spec.problems[row['bubble']]
        nodes=[]
        for multiplier in (.1,1.,10.):
            for alpha in args['loading_grid']:
                test=copy(prob)
                test.feed=f.eq.Amounts(dict(prob.feed.values,**{'carbon-dioxide':alpha*args['basis_amount']}))
                test.P=f.eq.Free(args['P']*multiplier)
                try:
                    value=f.eq.solve_equilibrium(spec.model,test)
                    nodes.append(dict(multiplier=multiplier,loading=alpha,
                                      pressure=value.pressure if value.requested_tolerance_met else None,
                                      message=value.message,admitted=value.requested_tolerance_met))
                except (ValueError,RuntimeError) as error:
                    nodes.append(dict(multiplier=multiplier,loading=alpha,admitted=False,message=str(error)))
            records[label]=dict(row=row['identity'],P_Pa=args['P'],nodes=nodes)
            f.put('MDEA/root-probe.json.gz',dict(wheel=f.r.SHA,records=records,seconds=monotonic()-tick))

def amp_roots():
    started = monotonic()
    cases = {'AMP_free':('B','C'),'AMP_fixed':('B',)}
    for design,labels in cases.items():
        manifest = f.r.read(f.OUT/f'{design}/manifest.json.gz')
        run,_,_ = f.configured(design,'initial-pressure-guess')
        initial = manifest['start_A_declaration']
        bound = run.bind(initial)
        record = dict(wheel=f.r.SHA,manifest_fingerprint=f.fingerprint(manifest),starts={})
        for label in labels:
            point = at_chart(run,bound,initial,manifest['starts'][label]['optimizer'])
            spec = run.bind(point)
            attempt = f.r.read(f.OUT/f'{design}/{label}.json.gz')
            failure = attempt['report']['failures'][0]
            row = spec.inputs['observations']['fitted'][failure['observation']]
            original = spec.problems[row['problem']]
            guesses = []
            for factor in (.1,1.,10.):
                prob = copy(original)
                prob.P = f.eq.Free(original.P.guess*factor)
                try:
                    value = f.eq.solve_equilibrium(spec.model,prob)
                    guesses.append(dict(P_guess_Pa=prob.P.guess,P_Pa=value.pressure,
                        requested_tolerance_met=value.requested_tolerance_met,
                        admitted=bool(value.success and value.requested_tolerance_met),message=value.message))
                except (ValueError,RuntimeError) as error:
                    guesses.append(dict(P_guess_Pa=prob.P.guess,admitted=False,message=str(error)))
            record['starts'][label] = dict(row=row['identity'],failure=failure,guesses=guesses)
        f.put(f'{design}/root-probe.json.gz',dict(record,seconds=monotonic()-started))


def mdea_descent():
    started = monotonic()
    prior = f.r.read(f.OUT/'MDEA/A.json.gz')
    point = prior['endpoint']
    run,_,_ = f.configured('MDEA','projected-gradient-line')
    spec = run.bind(point)
    gradient = f.np.array([g*d['scale']/(d['bounds'][1]-d['bounds'][0])
                          for g,d in zip(prior['diagnostics']['projected_gradient'],point['coordinates'],strict=True)])
    direction = -gradient/max(abs(gradient))
    trials = []
    original_cost = prior['replay']['cost']
    for step in (.1,.01,.001,.0001):
        u = (direction*step).tolist()
        trial = at_chart(run,spec,point,u)
        replay = f.replay(run.bind(trial))
        cost = replay['cost']
        reduction = (original_cost-cost)/original_cost if cost is not None else None
        trials.append(dict(step=step,optimizer_step=u,replay=replay,point=trial,relative_reduction=reduction))
        f.put('MDEA/stationarity/A-projected-direction.json.gz',dict(endpoint=prior['endpoint_fingerprint'],
            wheel=f.r.SHA,trials=trials,seconds=monotonic()-started))
        if reduction is not None and reduction>prior['controls']['function_tolerance']:
            break


def mdea_continuation(after_descent=False):
    prior = f.r.read(f.OUT/'MDEA/A.json.gz')
    point = prior['endpoint']
    label, maximum_seconds = 'A-continuation',440
    if after_descent:
        descent = f.r.read(f.OUT/'MDEA/stationarity/A-projected-direction.json.gz')['trials'][-1]
        assert descent['relative_reduction']>prior['controls']['function_tolerance']
        point = descent['point']
        label, maximum_seconds = 'A-descent-continuation',72
    path = f'MDEA/stationarity/{label}.json.gz'
    run,_,_ = f.configured('MDEA',label)
    spec = run.bind(point)
    controls = prior['controls'] | dict(function_tolerance=1e-14,maximum_elapsed_time_seconds=maximum_seconds)
    spec.spec['optimizer'] = controls
    started = monotonic()
    _,report,_ = spec.fit()
    record = dict(wheel=f.r.SHA,source=f.fingerprint(point),controls=controls,report=report,
                  fit_seconds=monotonic()-started)
    f.put(path,record)
    if report['physical'] and report['reactions']:
        endpoint = run.endpoint_mapping(point,report,point['coordinates'])
        bound = run.bind(endpoint)
        started = monotonic()
        replay = f.replay(bound)
        passed = replay['cost'] is not None and f.a.f.a.relative(replay['cost'],report['final_cost'])<=f.REPLAY_TOLERANCE['MDEA']
        record.update(endpoint=endpoint,endpoint_fingerprint=f.fingerprint(endpoint),replay=replay,
                      replay_seconds=monotonic()-started,replay_passed=passed)
        f.put(path,record)
        started = monotonic()
        record.update(diagnostics=f.endpoint_diagnostics(bound,replay,endpoint,controls),
                      diagnostic_seconds=monotonic()-started)
        f.put(path,record)


if __name__=='__main__':
    import sys
    f.a.study.reuse.bind_wheel()
    f.r.verify()
    if sys.argv[1]=='root':
        root()
    elif sys.argv[1]=='amp-roots':
        amp_roots()
    elif sys.argv[1]=='mdea-descent':
        mdea_descent()
    elif sys.argv[1] in ('mdea-continue','mdea-restart'):
        mdea_continuation(after_descent=sys.argv[1]=='mdea-restart')
    else:
        labels=sys.argv[2:] or ['A']
        for label in labels:
            wide = (sys.argv[1],label)==('MDEA','A')
            stationarity(sys.argv[1],label,(1.,.5,.125,.03125,.0078125) if wide else (1.,.5))
