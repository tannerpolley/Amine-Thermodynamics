"""Replay the retained phase controls and release search populations."""
# ruff: noqa: E402
from collections import Counter
import sys
from time import monotonic
from concurrent.futures import ProcessPoolExecutor
from functools import cache
from hashlib import sha256
from types import SimpleNamespace

from refit import OUT, WORK, P_REF, ROUND7, configured, fingerprint, put, r
from calculations import MDEA, Route, transfer
from mdea_reference import seed_state, predicates
from phases import fixed
from receivers import AMP, DEA
from part_ii import eq
from reference_states_428 import scaled_pressure_error
from round_3.phases import physical, trials
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


def controls(design,label,*,rebuild=False,scaled=False):
    started = monotonic()
    folder = "rebuild-441/scaled/" if scaled else "rebuild-441/" if rebuild else ""
    path = f'{design}/controls/{folder}{label}.json.gz'
    try:
        run,point = point_for(design,label,'decisive-phase-rebuild-441' if rebuild else 'decisive-phase')
    except ValueError as error:
        put(path,dict(refusal=str(error),seconds=monotonic()-started))
        return
    spec = run.bind(point)
    record = dict(endpoint_fingerprint=fingerprint(point),wheel=r.SHA,rows={})
    for key,state,P,seed,assemblages in control_states(design,spec):
        row = dict(state=state,P_Pa=P,pressure_basis='retained absolute pressure')
        record['rows'][key] = row

        def checkpoint(value):
            row['value'] = value
            put(path,dict(record,seconds=monotonic()-started))

        try:
            bubble = rebuild and design.startswith('AMP')
            value = fixed(run,spec,state,P,seed,mdea=design=='MDEA',assemblages=assemblages,
                          decision_bubble=bubble,checkpoint=checkpoint if bubble else None)
            if design=='MDEA':
                value = predicates(value,tolerance=1e-10)
            if label!='tracking':
                assert all(rx['reference']['reference_pressure_pa']==P_REF
                           for rx in value['declaration']['reactions'])
            row['value'] = value
        except (AttributeError,IndexError,RuntimeError,ValueError,AssertionError) as error:
            row['refusal'] = f'{type(error).__name__}: {error}'
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


def support_census(spec, states, declare, bank, *, old_full=False):
    rows = []
    for state in states:
        row = dict(key=state['key'])
        rows.append(row)
        try:
            item = declare(spec,state,1.)
            before = set(range(len(spec.parameters.component_ids))) if old_full else (
                {i for i,n in enumerate(item.problem.feed.values) if n>0}
                | {i for rx in item.problem.reactions for i,v in enumerate(rx.stoichiometry) if v})
            after = r.supplied_support(spec,item)
            supplied = bank.get(state['key'],[]) if isinstance(bank,dict) else bank
            row.update(before=sorted(before),after=sorted(after),excluded=sum(
                not set(w['support'])<=after for w in supplied),bank_size=len(supplied))
        except (ValueError,RuntimeError,TypeError,AttributeError) as error:
            row['blocker'] = f'{type(error).__name__}: {error}'
    return rows


@cache
def screen_declarations(name):
    from mea_stability import BASE
    from mea_replays import census_declaration

    design, _, protocol = name.partition('/')
    run, point = point_for(design,'selected','parent-closure-rebuild-441')
    if design=='MEA':
        if protocol=='census':
            path = 'MEA/screen/census-raw.json.gz'
            states = r.read(OUT/path)['data']
            return (point,run,[(dict(q,key=str(q['index'])),q) for q in states],
                    r.read(BASE/'split-registry.json')['trials'],path,census_declaration(point))
        path = 'MEA/screen/grid.json.gz'
        rows = {q['key']:q for q in r.read(OUT/path)['data']}
        return point,run,[(q,rows[q['key']]) for group in r.states() for q in group
                         if q['key']!='offset|0.4|338.15|0.5375|1.5'],r.read(BASE/'split-trials.json'),path,None
    path = f'{design}/screen/{"rebuild-441" if design=="DEA" else "selected"}/{protocol}/summary.json.gz'
    _,run,bank = next(x for x in release_routes(design,'parent-closure-rebuild-441') if x[0]==protocol)
    spec = run.bind(point)
    states = {q['key']:q for q in run.states(spec)}
    data = r.read(OUT/path)
    assert data['endpoint_fingerprint']==fingerprint(point) and data['wheel']==r.SHA
    rows = [(states[q['key']],q) for q in data['rows'] if q['available'] and not r.descent(q)
            and q['key'] not in data['aliases']]
    return point, run, rows, bank, path, None


def _screen_parents(args):
    name, selected = args
    from refit import a

    a.study.reuse.bind_wheel()
    r.verify()
    point,run,rows,bank,path,census = screen_declarations(name)
    spec = run.bind(point)
    retained = {state['key']:(state,row) for state,row in rows}
    prepared = None
    rows = []
    for key in selected:
        state,old = retained[key]
        out = dict(key=key,message=old.get('message'),wheel=r.SHA)
        started = monotonic()
        try:
            options = eq.StabilityOptions()
            if census:
                item = census(spec,state,1.)
                p = item.problem
                final = old['final']
                n = len(spec.parameters.component_ids)
                center = SimpleNamespace(temperature=final['temperature'],pressure=final['pressure'],
                    amounts=final['amounts'],molar_densities=final['molar_densities'],residuals=final['residuals'],
                    phase_mole_fractions=lambda i: final['mole_fractions'][i*n:(i+1)*n])
                archive = old['stability'][0]
                P = p.pressure.value
            else:
                item = run.stability_row(spec,state,1.)
                options = item.stability_options
                p = item.problem
                P = (old['pressure_Pa']*item.pressure_ratio if item.pressure_reference is not None
                     else p.pressure.value)
                p.pressure = type(p.pressure).fixed(P)
                center = eq.solve_equilibrium(spec.model,p)
                if not center.requested_tolerance_met:
                    raise ValueError(center.message)
                if 'parent' in old:
                    assert center.molar_densities==[old['parent']['rho']]
                    assert list(center.phase_mole_fractions(0))==old['parent']['x']
            options.mode = type(options.mode).Full
            if census:
                template = type(p.phases[0])
                seeds = []
                for kind,ids in [('Liquid',r.s.COMPONENT_IDS),('Vapor',r.s.COMPONENT_IDS[:3])]:
                    phase = template()
                    phase.kind,phase.name,phase.support_declared = getattr(type(phase.kind),kind),kind,True
                    phase.support = [spec.parameters.component_ids.index(c) for c in ids]
                    seeds.append(phase)
                options.trials = seeds
            compiled = eq.compile_problem(spec.model,p)
            out.update(P_Pa=P,T_K=center.temperature,parent_kinds=[q.kind.name for q in p.phases])
            out['parent'] = physical(spec,p,center)
            if any(scaled_pressure_error(q['pressure_residual_Pa'],q['density_mol_m3'],q['T_K'])>p.row_tolerance
                   for q in out['parent']['phases']):
                out['initial_parent'] = out['parent']
                phases = p.phases
                for i,phase in enumerate(phases):
                    x,rho = center.phase_mole_fractions(i),center.molar_densities[i]
                    phase.composition_guess = [x[j] for j in phase.support]
                    phase.packing_guess = rho*spec.model._model.packing_fraction_coefficient(center.temperature,x)
                p.phases = phases
                p.pressure = type(p.pressure).fixed(.999*P)
                seed = eq.solve_equilibrium(spec.model,p)
                p.pressure = type(p.pressure).fixed(P)
                out['restart'] = dict(P_Pa=.999*P,message=seed.message)
                if not seed.requested_tolerance_met:
                    raise ValueError(seed.message)
                center = eq.solve_equilibrium(spec.model,p,start=seed)
                if not center.requested_tolerance_met:
                    raise ValueError(center.message)
                compiled = eq.compile_problem(spec.model,p)
                out['parent'] = physical(spec,p,center)
            if not out['parent']['physical_checks_pass']:
                raise ValueError('Trial-call parent misses scaled pressure or balance closure')
            witnesses = bank.get(key,[]) if isinstance(bank,dict) else bank
            out['bank_size'] = len(witnesses)
            if census and 'restart' not in out:
                out.update(native_completed=archive['completed'],native_message=archive['message'],
                           native_trials=[dict(seed=t['seed'],evidence=t['evidence'],message=t['message'],
                                descent=t['resolved_descent'],optimizer_success=t['optimizer']['success'],
                                optimizer_tolerance_met=t['optimizer']['requested_tolerance_met']) for t in archive['trials']],
                           supplied_counts=dict(archive['supplied_counts']),supplied_excluded=0)
            else:
                report = eq.stability_test(compiled,center,options)
                out.update(native_completed=report.completed,native_message=report.message,native_trials=trials(report))
                support = r.supplied_support(spec,item,compiled=compiled)
                supplied_bank = [dict(w,kind=w['kind'].capitalize()) for w in witnesses] if census else witnesses
                supplied, excluded, repeated, identities = r._applicable(item,supplied_bank,support)
                counts = Counter(evaluated=0)
                if supplied:
                    k = center.temperature,identities
                    if prepared is None or prepared[0]!=k:
                        prepared = k,eq.prepare_supplied_trials(spec.model,center.temperature,supplied)
                    supplied_options = eq.StabilityOptions()
                    supplied_options.prepared_trials = prepared[1]
                    ts = eq.stability_test(compiled,center,supplied_options).trials
                    counts.update(ts[i].evidence for i,_ in repeated)
                    out['supplied_descents'] = sum(r.supplied_negative(
                        dict(evidence=ts[i].evidence,quantities=ts[i].quantities)) for i,_ in repeated)
                out.update(supplied_counts=dict(counts),supplied_excluded=len(excluded))
        except (ValueError,RuntimeError,AttributeError,AssertionError,IndexError) as error:
            out['blocker'] = f'{type(error).__name__}: {error}'
        rows.append(dict(out,seconds=monotonic()-started))
    return rows


def screen_parents(name, *, workers, pilot=False):
    declaration = 'MEA/grid' if name=='MEA/offset' else name
    point,_,rows,bank,path,_ = screen_declarations(declaration)
    keys = [state['key'] for state,_ in rows if declaration!='MEA/grid' or
            state['key'].startswith('offset|')==(name=='MEA/offset')]
    metadata = dict(endpoint_fingerprint=fingerprint(point),wheel=r.SHA,
                    bank_fingerprint=fingerprint(bank),source=path,
                    source_sha256=sha256((OUT/path).read_bytes()).hexdigest())
    folder = f'MEA/screen/rebuild-441/trial-call/{name}'
    if pilot:
        chosen = keys[::max(1,len(keys)//8)][:8]
        if name=='MEA/grid':
            chosen[0] = 'dense|0.35|313.15|0.35|1.05'
        groups = [[k] for k in chosen]
    else:
        groups = [keys[i:i+12] for i in range(0,len(keys),12)]
    start = monotonic()
    retained = []
    with ProcessPoolExecutor(workers) as pool:
        for i,batch in enumerate(pool.map(_screen_parents,[(declaration,g) for g in groups])):
            retained.extend(batch)
            if not pilot:
                put(f'{folder}/{i}.json.gz',dict(metadata,keys=groups[i],rows=batch))
    elapsed = monotonic()-start
    if pilot:
        cpu = sum(q['seconds'] for q in retained)
        result = dict(metadata,rows=retained,seconds=elapsed,requested=len(keys),
                      projected_seconds=elapsed+cpu*len(keys)/len(retained)/workers)
        put(f'{folder}/pilot.json.gz',result)
    else:
        put(f'{folder}/inventory.json.gz',dict(metadata,keys=keys,seconds=elapsed,batches=len(groups)))
    print(name,len(retained),round(elapsed,3),
          Counter(q.get('blocker','retained') for q in retained),flush=True)


def screening(design, label, pilot=False, *, rebuild=False, workers=None):
    tick = monotonic()
    _,point = point_for(design,label,'screen')
    endpoint = fingerprint(point)
    for protocol,run,bank in release_routes(design,f'screen-{label}' + ('-rebuild-441' if rebuild else '')):
        started = monotonic()
        folder = f'{design}/screen/{"rebuild-441" if rebuild else label}/{protocol}'
        if workers is not None:
            run.workers = workers
        spec = run.bind(point)
        states = run.states(spec)
        assert len(states)==(666 if design.startswith('AMP') else 11824 if design=='MDEA' else 1271)
        aliases = run.same_calculations(point,states)
        unique = [q for q in states if q['key'] not in aliases]
        held = {}
        if rebuild and design=='DEA':
            prior = r.read(OUT/'DEA/screen/selected/declared/summary.json.gz')
            assert prior['endpoint_fingerprint']==endpoint and prior['wheel']==r.SHA
            held = {q['key']:q for q in prior['rows'] if q['key']=='lawson-1976-viii:1:problem'}
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
                assert record['endpoint_fingerprint']==endpoint and record['wheel']==r.SHA
                assert [q['key'] for q in record['rows']]==[q['key'] for q in keys]
            else:
                t = monotonic()
                if design=='MDEA':
                    run.out = WORK/design/f'screen-{label}'/protocol/str(i)
                fresh = iter(run.grid(point,[q for q in keys if q['key'] not in held],trial_set=bank))
                batch = [held[q['key']] if q['key'] in held else next(fresh) for q in keys]
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
    elif action in ('parent-closure','parent-pilot'):
        screen_parents(design,workers=int(label),pilot=action=='parent-pilot')
    else:
        screening(design,label,pilot=action=='pilot')
