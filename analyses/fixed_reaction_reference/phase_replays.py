"""Replay the retained phase controls and release search populations."""
# ruff: noqa: E402
from collections import Counter
import sys
from time import monotonic

from refit import OUT, WORK, P_REF, ROUND7, configured, fingerprint, put, r
from calculations import MDEA, Route, transfer
from mdea_reference import seed_state, predicates
from phases import fixed
from receivers import AMP, DEA
from round_8.records import Sources
from round_8.reductions import phase_outcome


def point_for(design, label, tag):
    run, point, _ = configured(design, tag if label!='tracking' else tag+'-tracking',fixed=label!='tracking')
    if label=='selected':
        label = r.read(OUT/f'{design}/selection.json')['selected']
        if label is None:
            raise ValueError(f'{design} selection is undecided')
    if label in ('tracking','fixed-at-old'):
        return run,point
    path = (f'MDEA/stationarity/{label}.json.gz' if design=='MDEA' and label in
            ('A-continuation','A-descent-continuation') else f'{design}/{label}.json.gz')
    attempt = r.read(OUT/path)
    if not attempt.get('endpoint'):
        raise ValueError(f"{design} {label}: {attempt['report']['message']}")
    point = attempt['endpoint']
    assert fingerprint(point)==attempt['endpoint_fingerprint']
    return run,point


def incumbent_pair(entry):
    return next(x for x in entry['attempts'] if x['confirmed'])


def control_states(design, spec):
    source = Sources()
    if design=='MEA':
        yield '100-kPa',r.states()[0][0],P_REF,None,False
    elif design=='DEA':
        old = source.core('F/search-outcome.json.gz')
        for entry in old['classifications']:
            if entry['key'] in old['confirmed']:
                yield entry['key'],dict(problem=entry['key']),entry['pressure_Pa'],dict(pair=incumbent_pair(entry)),False
    elif design=='MDEA':
        old = source.core('C/salt/search-outcome.json.gz')
        entry, = [q for q in old['classifications'] if q['key'] in old['confirmed']]
        yield '204-MPa',seed_state(spec,entry),entry['pressure_Pa'],dict(pair=incumbent_pair(entry)),False
        target = source.core('C/salt/rms-fixed-pressures.json.gz')['pressure_262_MPa']
        feed = target['feed']
        state = dict(T=target['T_K'],stock={k:v for k,v in feed.items() if v and k!='carbon-dioxide'},
                     a=feed['carbon-dioxide']/feed['methyldiethanolamine'])
        yield '263-MPa',state,target['P_Pa'],dict(pair=incumbent_pair(target)),False
    else:
        bank = {q['key']:q for q in source.read(
            'analyses/amp_transfer/results/retransfer-412-f2-05e94210/main/phase-classification-1.json.gz')['states']}
        for q in source.read('analyses/round_3/results/q1.json')['rows']:
            if q['pressure_basis']!='measured pressure':
                continue
            archive = bank[q['key']]
            witness = next(w for w in archive['supplied_pressure_roots'] if r.supplied_negative(w['witness']))
            witness = dict(witness['witness']['phase'],
                           packing=witness.get('reclosed_quantities',witness['witness']['quantities'])['packing_fraction'])
            yield q['key'],dict(problem=q['key']),q['free']['P_Pa'],dict(pair=incumbent_pair(archive),witness=witness),True
        archive = source.display('amp-common-pressure')
        P = archive['outcomes']['free']['fixed']['P_Pa']
        seed = source.read('analyses/mea_parameter_bundle/results/reference-states-428/amp.json')['split']
        yield 'worked-state',archive['state'],P,dict(pair=seed),False


def controls(design,label):
    started = monotonic()
    path = f'{design}/controls/{label}.json.gz'
    try:
        run,point = point_for(design,label,'decisive-phase')
    except ValueError as error:
        put(path,dict(refusal=str(error),seconds=monotonic()-started))
        return
    spec = run.bind(point)
    record = dict(endpoint_fingerprint=fingerprint(point),wheel=r.SHA,rows={})
    for key,state,P,seed,assemblages in control_states(design,spec):
        row = dict(state=state,P_Pa=P,pressure_basis='retained absolute pressure')
        try:
            value = fixed(run,spec,state,P,seed,mdea=design=='MDEA',assemblages=assemblages)
            if design=='MDEA':
                value = predicates(value,tolerance=1e-10)
            if label!='tracking':
                assert all(rx['reference']['reference_pressure_pa']==P_REF
                           for rx in value['declaration']['reactions'])
            row['value'] = value
        except (AttributeError,IndexError,RuntimeError,ValueError,AssertionError) as error:
            row['refusal'] = f'{type(error).__name__}: {error}'
        record['rows'][key] = row
        put(path,dict(record,seconds=monotonic()-started))
    print(design,label,{k:phase_outcome(q.get('value',{})) for k,q in record['rows'].items()},flush=True)


def release_routes(design, tag):
    options = dict(fixed_reference_pressure_pa=P_REF)
    root = WORK/design/tag
    if design=='DEA':
        run = Route(DEA,root,**options)
        bank = run.load(run.config['split_record'])
        return [('declared',run,bank['trials']+bank.get('supplied_trials',[]))]
    if design=='MDEA':
        bank = r.read(MDEA.OLD/'split-record.json')
        return [('declared',Route(MDEA.DECLARATION,root,**options),bank['trials']+bank.get('supplied_trials',[]))]
    native = Route(AMP.DECLARATION,root/'native',**options)
    supplied = Route(AMP.DECLARATION,root/'supplied',**options)
    bank = transfer.amp_stability.trial_bank(supplied)
    assert transfer.amp_stability.bank_hash(bank)==transfer.amp_stability.TRIAL_SHA
    return [('native',native,[]),('supplied',supplied,bank['trials']+bank.get('supplied_trials',[]))]


def baseline_screen(design,protocol):
    path = ('C/salt/search-0.json.gz' if design=='MDEA' else 'F/search-rows.json.gz'
            if design=='DEA' else f"AMP/{design.split('_')[1]}/{protocol}-rows.json.gz")
    return {q['key']:q for q in r.read(ROUND7/path)}


def screening(design, label, pilot=False):
    tick = monotonic()
    _,point = point_for(design,label,'screen')
    endpoint = fingerprint(point)
    for protocol,run,bank in release_routes(design,f'screen-{label}'):
        started = monotonic()
        folder = f'{design}/screen/{label}/{protocol}'
        spec = run.bind(point)
        states = run.states(spec)
        assert len(states)==(666 if design.startswith('AMP') else 11824 if design=='MDEA' else 1271)
        aliases = run.same_calculations(point,states)
        unique = [q for q in states if q['key'] not in aliases]
        if pilot:
            selected = unique[::47] if design=='MDEA' else unique[::17]
            batch = run.grid(point,selected,trial_set=bank)
            elapsed = monotonic()-started
            record = dict(endpoint_fingerprint=endpoint,wheel=r.SHA,protocol=protocol,seconds=elapsed,
                          rows=batch,requested=len(states),distinct=len(unique),
                          projected_seconds=elapsed*len(unique)/len(batch))
            put(f'{folder}/pilot.json.gz',record)
            print(design,protocol,'first screen batch',len(batch),round(elapsed,2),'s projected',
                  round(record['projected_seconds'],2),'s',flush=True)
            continue
        # Keep each batch independently readable if the lane stops.
        blocks = 12 if design=='MDEA' else 4
        merged = {}
        for i in range(blocks):
            keys = unique[i::blocks]
            path = f'{folder}/batches/{i}.json.gz'
            if (OUT/path).exists():
                record = r.read(OUT/path)
                assert record['endpoint_fingerprint']==endpoint
                assert [q['key'] for q in record['rows']]==[q['key'] for q in keys]
            else:
                t = monotonic()
                if design=='MDEA':
                    run.out = WORK/design/f'screen-{label}'/protocol/str(i)
                batch = run.grid(point,keys,trial_set=bank)
                record = dict(endpoint_fingerprint=endpoint,wheel=r.SHA,rows=batch,seconds=monotonic()-t)
                put(path,record)
            merged.update((q['key'],q) for q in record['rows'])
        classifications = transfer.classify(run,point,list(merged.values()),states)
        merged.update((dest,dict(merged[src],key=dest,seconds=0.,same_calculation_as=src)) for dest,src in aliases.items())
        rows = [merged[q['key']] for q in states]
        baseline = baseline_screen(design,protocol)
        assert set(merged)==set(baseline)
        put(f'{folder}/summary.json.gz',dict(endpoint_fingerprint=endpoint,wheel=r.SHA,rows=rows,
            classifications=classifications,tally=r.tally(rows),aliases=aliases,
            original_pressure_basis={k:q.get('pressure_basis',{'model_bubble_pressure_Pa':q.get('pressure_Pa')})
                                     for k,q in baseline.items()},
            unavailable_by_message=dict(Counter(q.get('message') or q.get('status') for q in rows if not q['available'])),
            seconds=monotonic()-started))
    return monotonic()-tick


if __name__=='__main__':
    from refit import a
    a.study.reuse.bind_wheel()
    r.verify()
    action,design,label = sys.argv[1:]
    if action=='controls':
        controls(design,label)
    else:
        screening(design,label,pilot=action=='pilot')
