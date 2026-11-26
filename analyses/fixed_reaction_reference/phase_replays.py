"""Replay the retained phase controls and release search populations."""
# ruff: noqa: E402
from collections import Counter, defaultdict
import os
import sys
from time import monotonic
from concurrent.futures import ProcessPoolExecutor
from functools import cache, partial
from hashlib import sha256
from pathlib import Path
from types import SimpleNamespace

from refit import OUT, WORK, P_REF, ROUND7, MDEAWeights, configured, fingerprint, put, r, save
from calculations import MDEA, Route, transfer
from mdea_reference import seed_state, predicates
from phases import fixed
from receivers import AMP, DEA
from part_ii import SHA, WHEEL, calculation_declaration, eq, stable
from round_3.phases import cd, dilute_vapor_connection, physical, trial_parent, trials
from reference_states_428 import phase_closure
from round_8.reductions import vapor_trace_passes
from round_8.records import Sources
from round_8.reductions import phase_outcome

MDEA_CEILING_PA = 5_036_700.
MDEA_REBUILD = 'MDEA_slope_bound/screen/rebuild-441'
MDEA_GRID = MDEA_REBUILD+'/cold-march'
MDEA_CONNECTED = MDEA_REBUILD+'/reverse-connection'
MDEA_265 = "grid:{'water': 40.84100418410041, 'methyldiethanolamine': 1.0}:393.15:0.8:3.0"
MDEA_COMPARISON = 'MDEA_comparison'
COMPARISON_SETS = ('0.7650','0.1325','1.0000')
OUTSIDE_INCOMPLETE = 'not searched to completion, outside the screened interval'
SPLIT_PRESSURES = (1_121_000., 203_126_858.89663097)


def check_cold_point(point, previous, stock, temperature, loading, tolerance):
    P = point['pressure_Pa']
    assert (point['stock'],point['T_K'],point['loading'])==(stock,temperature,loading), 'cold bubble path identity'
    assert P>=previous['pressure_Pa'], 'cold bubble pressure below its predecessor'
    assert point['phase_kinds']==['Liquid','Vapor'], 'cold bubble root labels'
    assert phase_closure(point,P,tolerance,temperature=temperature), 'cold bubble scaled closure'
    liquid, vapor = point['phases']
    assert liquid['T_K']==vapor['T_K']==temperature, 'cold bubble phase temperature'
    assert liquid['amount_mol']>0 and vapor['amount_mol']==0, 'cold bubble incipient amount'
    assert any(r['returned']=='liquid' for r in cd.matched(
        point['liquid_roots'],tolerance,liquid['density_mol_m3'],T=temperature,P=P)), 'cold bubble liquid root'
    assert vapor_trace_passes(point), 'cold incipient phase lacks a vapor connection'


def reverse_errors(previous, returned):
    assert returned['loading']==previous['loading'], 'reverse continuation did not reach the predecessor loading'
    left, right = previous['phases'], returned['phases']
    assert len(left)==len(right)==2, 'reverse continuation phase count'
    return dict(pressure_relative=abs(returned['pressure_Pa']/previous['pressure_Pa']-1),
                density_relative=max(abs(b['density_mol_m3']/a['density_mol_m3']-1) for a,b in zip(left,right,strict=True)),
                mole_fraction_absolute=max(abs(x-y) for a,b in zip(left,right,strict=True)
                                            for x,y in zip(a['x'],b['x'],strict=True)))


def check_reverse_connection(errors):
    assert max(errors['pressure_relative'],errors['density_relative'])<=1e-6, 'reverse pressure or density mismatch'
    assert errors['mole_fraction_absolute']<=1e-8, 'reverse mole-fraction mismatch'


def reverse_bubble(solve, spec, bubble, previous, cold, seed):
    started = monotonic()
    target, last = previous['loading'], cold['loading']
    step = last-target
    attempts, returned = [], None
    stop = None
    while last>target:
        loading = max(target,last-step)
        tick = monotonic()
        result = solve(loading,seed)
        converged = result.success and result.requested_tolerance_met
        record = dict(loading=loading,from_loading=last,message=result.message,converged=converged,
                      iterations=result.iterations,seconds=monotonic()-tick)
        attempts.append(record)
        if converged:
            record['pressure_Pa'] = result.pressure
            last, seed = loading, result
        else:
            if 'third directional energy contraction unavailable: nonfinite' in record['message']:
                record['engine_issue'] = 'tannerpolley/epcsaft#275'
            step /= 2
            if step<1e-3:
                stop = record['message']
                break
    errors = None
    if stop is None:
        returned = dict(physical(spec,bubble,seed),loading=last,pressure_Pa=seed.pressure)
        errors = reverse_errors(previous,returned)
        try:
            assert returned['physical_checks_pass'], 'reverse predecessor misses phase closure'
            check_reverse_connection(errors)
        except AssertionError as error:
            stop = str(error)
    return dict(attempts=attempts,returned=returned,errors=errors,stop=stop,
                engine_issue=attempts[-1].get('engine_issue') if stop else None,
                seconds=monotonic()-started)


def loading_march(spec, run, states):
    """Return the converged loading path up to the first point above the ceiling."""
    started = monotonic()
    first = states[0]
    bubble = run.stability_row(spec, first, 1.).pressure_reference
    ids = spec.parameters.component_ids
    feed = list(bubble.feed.values)
    carbon, amine = (ids.index(c) for c in ('carbon-dioxide', run.config['amine']))
    points, warm_failures, solution, last = [], [], None, None
    cold_attempts = []
    stall = None

    def solve(loading, start):
        feed[carbon] = loading*feed[amine]
        native_feed = bubble.feed
        native_feed.values = feed
        bubble.feed = native_feed
        return eq.solve_equilibrium(spec.model,bubble,start=start)

    for target in sorted({s['a'] for s in states}):
        loading, step = target, target-(last or 0.)
        while True:
            result = solve(loading,solution)
            if result.success and result.requested_tolerance_met:
                points.append(dict(loading=loading, pressure_Pa=result.pressure))
                solution, last = result, loading
                if result.pressure>MDEA_CEILING_PA or loading==target:
                    break
                loading = min(target, loading+step)
            else:
                failure = dict(target=target,loading=loading,message=result.message)
                if solution is not None:
                    warm_failures.append(failure)
                step /= 2
                if step<1e-3 or last is None:
                    stall = failure
                    if solution is None:
                        break
                    result = solve(target,None)
                    attempt = dict(loading=target,start='cold',message=result.message,stock=first['stock'],
                                   T_K=first['T'],warm_failure=len(warm_failures)-1)
                    cold_attempts.append(attempt)
                    stall = dict(warm=stall,cold=attempt)
                    if result.success and result.requested_tolerance_met:
                        attempt.update(physical(spec,bubble,result),pressure_Pa=result.pressure,
                                       phase_kinds=[p.kind.name for p in bubble.phases])
                        liquid, vapor = attempt['phases']
                        attempt['liquid_roots'] = cd.pressure_roots(spec.model,result.temperature,
                            result.pressure,liquid['x'],liquid['density_mol_m3'])
                        attempt['vapor_trace'], _ = dilute_vapor_connection(
                            spec.model,result.temperature,vapor['x'],vapor['density_mol_m3'])
                        try:
                            check_cold_point(attempt,points[-1],first['stock'],first['T'],target,bubble.row_tolerance)
                        except AssertionError as error:
                            attempt['qualification_failure'] = str(error)
                            break
                        points[-1]['phases'] = physical(spec,
                            run.stability_row(spec,dict(first,a=last),1.).pressure_reference,solution)['phases']
                        attempt['reverse'] = reverse_bubble(solve,spec,bubble,points[-1],attempt,result)
                        if attempt['reverse']['stop']:
                            break
                        points.append(attempt)
                        solution, last, stall = result, target, None
                    break
                loading = min(target, last+step)
        if stall or points[-1]['pressure_Pa']>MDEA_CEILING_PA:
            break
    return dict(stock=first['stock'], T_K=first['T'], points=points, stall=stall,warm_failures=warm_failures,
                cold_attempts=cold_attempts,
                seconds=monotonic()-started)


def _loading_path(states, run, point):
    run.verify()
    return dict(loading_march(run.bind(point),run,states),wheel=run.wheel_sha256)


def comparison_sources(k):
    results = MDEA.RESULTS.parent
    bank = MDEA.OLD/'split-record.json'
    if k=='0.7650':
        return MDEA.RESULTS/'endpoint.json', bank, [results/'phase-search-421/coverage.json',
                                                    MDEA.RESULTS/'stability.json'], None
    side = {'0.1325':'low','1.0000':'high'}[k]
    folder, = (results/'shared-bicarbonate-417/mdea').glob(f'mdea-{side}-*')
    return folder/'endpoint.json.gz', bank, sorted(folder.glob('search-*.json.gz')), folder/'stability.json.gz'


def comparison_prior(sources):
    if sources[0].name=='coverage.json':
        counts = r.read(sources[1])
        unavailable = {q['key']:q for q in counts['grid']['unavailable_searches']}
        rows = [dict(q,available=q['complete'],**{
            'archive':unavailable.get(q['key'],{})}) for q in r.read(sources[0])]
        assert len(unavailable)==sum(not q['available'] for q in rows)==1099
    else:
        rows = [q for path in sources for q in r.read(path)]
    by_key = {q['key']:q for q in rows}
    assert len(by_key)==len(rows)==11824, 'historical comparison inventory'
    return by_key


def comparison_reuse(prior):
    """Count admission evidence before attempting a reuse identity comparison."""
    missing = Counter()
    for q in prior.values():
        if q['available'] and not q['descent']:
            record = q.get('archive',q)
            if not {'parent','native_trials','supplied_counts'}<=record.keys():
                missing['missing amendment-4 evidence'] += 1
            else:
                raise AssertionError(f"{q['key']}: check consumed parent, feed, cap and bank before reuse")
    return dict(passed=0,**missing)


def comparison_splits(path):
    if path is None:
        return {}
    return {q['key']:dict(declared_pressure_Pa=q['pressure_Pa'],two_liquid_seed={
                field:a[field] for field in ('phases','packings')})
            for q in r.read(path)['pressure_roots'] for a in q['attempts'] if a['confirmed']}


def comparison_domain(state, path):
    if not path:
        return dict(domain='not applicable')
    cutoff = next((p for p in path['points'] if p['pressure_Pa']>MDEA_CEILING_PA),None)
    if cutoff and state['a']>=cutoff['loading']:
        return dict(domain='outside',cutoff=cutoff)
    if point := next((p for p in path['points'] if p['loading']==state['a']),None):
        return dict(domain='inside',marched_pressure_Pa=point['pressure_Pa'])
    assert path['stall'], state['key']
    return dict(domain='unassigned',blocker=path['stall'])


def comparison_stratum(row):
    return 'measured' if row['domain']=='not applicable' else f"grid {row['domain']}"


def comparison_screen(run, point, bank, states, prior, splits, output, *, mode):
    """Retain independent loading paths, specimen searches and their inventory."""
    from fixed_reaction_reference.handoff import comparison_outcome

    started = monotonic()
    output = Path(output)
    identity = dict(endpoint_fingerprint=fingerprint(point),wheel=run.wheel_sha256,
                    bank_fingerprint=fingerprint(bank),declaration=r.read(run.out/'identity.json'))
    assert len(states)==len(prior)==11824 and {q['key'] for q in states}==prior.keys()

    def retain(name, **payload):
        path = output/f'{name}.json.gz'
        assert not path.exists(), path
        save(path,dict(identity,**payload))

    def read(name):
        record = r.read(output/f'{name}.json.gz')
        assert all(record[k]==v for k,v in identity.items()), name
        return record

    def search_batches(inventory, aliases, held, prefix):
        by_key = {q['key']:q for q in inventory}
        pending = [q for q in inventory if q['key'] not in aliases and q['domain']!='unassigned']
        stopped = {comparison_stratum(q) for q in inventory if q['domain']=='unassigned'}

        def register_stops(rows):
            for q in rows:
                state = by_key[q['key']]
                _, blocker = comparison_outcome(state,q,len(bank))
                if blocker:
                    stopped.add(comparison_stratum(state))
                    print(output,q['key'],blocker,flush=True)

        register_stops(held.values())
        for i in range(8):
            tick = monotonic()
            batch = [q for q in pending[i::8] if q['key'] not in held and comparison_stratum(q) not in stopped]
            rows = stable.grid(point,batch,bank,route=run,completion=True) if batch else []
            retain(f'{prefix}-{i}',rows=rows,seconds=monotonic()-tick)
            print(output,prefix,i,len(rows),round(monotonic()-tick,2),flush=True)
            register_stops(rows)

    if mode=='continue':
        manifest = read('inventory')
        names = ['pilot',*(f'search-{i}' for i in range(8))]
        held = {q['key']:q for name in names for q in read(name)['rows']}
        search_batches(manifest['rows'],manifest['aliases'],held,'continued-search')
        return

    pilot = mode=='pilot'

    groups = defaultdict(list)

    def group_key(row):
        return tuple(row['stock'].items()),row.get('T',row.get('T_K'))

    for q in states:
        if 'stock' in q:
            groups[group_key(q)].append(q)
    selected = [*groups][::21]
    for q in states:
        if q['key'] in splits and 'stock' in q and group_key(q) not in selected:
            selected.append(group_key(q))
    paths = {} if pilot else {group_key(q):q for q in read('march-pilot')['rows']}
    tick = monotonic()
    requested = selected if pilot else [k for k in groups if k not in paths]
    with ProcessPoolExecutor(run.workers) as pool:
        paths.update(zip(requested,pool.map(partial(_loading_path,run=run,point=point),
                                             (groups[k] for k in requested)),strict=True))
    retain('march-pilot' if pilot else 'domain-march',rows=list(paths.values()),seconds=monotonic()-tick)
    print(output,'loading paths',len(paths),'stalls',sum(bool(p['stall']) for p in paths.values()),
          round(monotonic()-tick,2),flush=True)
    aliases = run.same_calculations(point,states)
    assert not splits.keys() & aliases.keys(), 'split control must own its calculation'
    inventory = []
    for q in states:
        if pilot and 'stock' in q and group_key(q) not in paths:
            continue
        key = q['key']
        path = paths[group_key(q)] if 'stock' in q else None
        inventory.append(dict(q,**comparison_domain(q,path),**splits.get(key,{}),
                              original_message=prior[key].get('message')))
    pending = [q for q in inventory if q['key'] not in aliases and q['domain']!='unassigned']
    if pilot:
        sample = {q['key'] for q in pending[::max(1,len(pending)//128)]} | splits.keys()
        pending = [q for q in pending if q['key'] in sample]
        tick = monotonic()
        rows = stable.grid(point,pending,bank,route=run,completion=True)
        retain('pilot',rows=rows,seconds=monotonic()-tick,elapsed=monotonic()-started)
        print(output,len(rows),monotonic()-started,flush=True)
        return
    reuse = comparison_reuse(prior)
    retain('inventory',rows=inventory,aliases=aliases,reuse=reuse,
           reaction_references={k:calculation_declaration(q.reference)
                                for k,q in ((rx.name,rx) for rx in run.bind(point).problems['comparison:363:final'].reactions)})
    held = {q['key']:q for q in read('pilot')['rows']}
    search_batches(inventory,aliases,held,'search')


def mdea_rebuild(run, point, bank, prior, *, modes, folder=MDEA_REBUILD):
    spec = run.bind(point)
    states = run.states(spec)
    old = {q['key']:q for q in prior['rows']}
    assert len(states)==len(old)==11824 and {q['key'] for q in states}==old.keys()
    identity = dict(endpoint_fingerprint=fingerprint(point),wheel=run.wheel_sha256,
                    bank_fingerprint=fingerprint(bank))

    def retain(name, rows, started, **metadata):
        path = f'{folder}/{name}.json.gz'
        assert not (OUT/path).exists(), path
        put(path,dict(identity,rows=rows,seconds=monotonic()-started,**metadata))
        print(path, len(rows), flush=True)

    if 'measured' in modes:
        tick = monotonic()
        measured = [q for q in states if not q['key'].startswith('grid:')]
        aliases = run.same_calculations(point,measured)
        unique = [q for q in measured if q['key'] not in aliases]
        retain('measured-inventory',measured,tick,aliases=aliases)
        # The old pilot supplies only the identities to replace in the bank-bound batches.
        replaced = {q['key'] for q in r.read(OUT/MDEA_REBUILD/'pilot-measured.json.gz')['rows']}
        for i in range(4):
            tick = monotonic()
            keys = unique[i::4]
            source = f'{MDEA_REBUILD}/measured-{i}.json.gz'
            retained = r.read(OUT/source)
            assert all(retained[k]==v for k,v in identity.items())
            assert [q['key'] for q in keys]==[q['key'] for q in retained['rows']]
            pending = [dict(q,decision_bubble=True) for q in keys if q['key'] in replaced]
            fresh = {q['key']:q for q in stable.grid(point,pending,bank,route=run,completion=True)} if pending else {}
            rows = [fresh.get(q['key'],q) for q in retained['rows']]
            retain(f'measured-{i}',rows,tick,retained_batch=source,recomputed_keys=list(fresh))

    if 'controls' in modes:
        tick = monotonic()
        controls = [dict(state,key=key,declared_pressure_Pa=P)
                    for key,state,P,_,_ in control_states('MDEA',spec)]
        rows = stable.grid(point,controls,bank,route=run,completion=True)
        retain('controls',rows,tick,measured_control='comparison:416:final')

    if set(modes)&{'march','reverse-pilot'}:
        tick = monotonic()
        groups = defaultdict(list)
        for q in states:
            if q['key'].startswith('grid:'):
                groups[tuple(q['stock'].items()),q['T']].append(q)
        pilot_path = OUT/f'{folder}/reverse-pilot.json.gz'
        if 'reverse-pilot' in modes:
            old_march = r.read(OUT/MDEA_GRID/'domain-march.json.gz')
            cold = [(tuple(q['stock'].items()),q['T_K']) for q in old_march['rows'] if q['warm_failures']]
            selected = cold[::8]
            with ProcessPoolExecutor(run.workers) as pool:
                rows = list(pool.map(partial(_loading_path,run=run,point=point),(groups[k] for k in selected)))
            retain('reverse-pilot',rows,tick)
            return
        pilot = r.read(pilot_path)
        assert all(pilot[k]==v for k,v in identity.items())
        paths = {(tuple(p['stock'].items()),p['T_K']):p for p in pilot['rows']}
        with ProcessPoolExecutor(run.workers) as pool:
            for path in pool.map(partial(_loading_path,run=run,point=point),
                                 (group for k,group in groups.items() if k not in paths),chunksize=2):
                paths[tuple(path['stock'].items()),path['T_K']] = path
        retain('domain-march',list(paths.values()),tick,ceiling_Pa=MDEA_CEILING_PA)
        grid = []
        for key, group in groups.items():
            path = paths[key]
            reached = {q['loading']:q for q in path['points']}
            cutoff = path['points'][-1] if path['points'] and path['points'][-1]['pressure_Pa']>MDEA_CEILING_PA else None
            for q in group:
                loading = q['a']
                row = dict(q,original_message=old[q['key']]['message'])
                if cutoff and loading>=cutoff['loading']:
                    row.update(domain='outside',cutoff=cutoff,archived_available=old[q['key']]['available'])
                elif loading in reached:
                    row.update(domain='inside',marched_pressure_Pa=reached[loading]['pressure_Pa'])
                    if q['key']==MDEA_265:
                        row['engine_issue'] = 'tannerpolley/epcsaft#265'
                else:
                    row.update(domain='unassigned', blocker=path['stall'])
                grid.append(row)
        retain('grid-inventory',grid,tick,ceiling_Pa=MDEA_CEILING_PA)

    if set(modes)&{'grid-pilot','grid'}:
        inventory = r.read(OUT/f'{folder}/grid-inventory.json.gz')
        assert all(inventory[k]==v for k,v in identity.items())
        requested = [q for q in inventory['rows'] if q['domain']=='inside' and 'engine_issue' not in q]
        if 'grid-pilot' in modes:
            tick = monotonic()
            selected = requested[::max(1,len(requested)//128)]
            retain('grid-pilot',stable.grid(point,selected,bank,route=run,completion=True),tick)
        if 'grid' in modes:
            pilot = r.read(OUT/f'{folder}/grid-pilot.json.gz')
            assert all(pilot[k]==v for k,v in identity.items())
            held = {q['key']:q for q in pilot['rows']}
            for i in range(8):
                tick = monotonic()
                members = requested[i::8]
                pending = [q for q in members if q['key'] not in held]
                fresh = iter(stable.grid(point,pending,bank,route=run,completion=True))
                retain(f'grid-{i}',[held[q['key']] if q['key'] in held else next(fresh) for q in members],tick)


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
                p = item.problem
                P = (old['pressure_Pa']*item.pressure_ratio if item.pressure_reference is not None
                     else p.pressure.value)
                center = None
            center = trial_parent(spec,p,P,out,center=center)
            if not census and 'parent' in old:
                consumed = out.get('initial_parent',out['parent'])['phases'][0]
                assert consumed['density_mol_m3']==old['parent']['rho'] and list(consumed['x'])==old['parent']['x']
            compiled = eq.compile_problem(spec.model,p)
            out.update(P_Pa=P,T_K=center.temperature,parent_kinds=[q.kind.name for q in p.phases])
            witnesses = bank.get(key,[]) if isinstance(bank,dict) else bank
            out['bank_size'] = len(witnesses)
            if census and 'restart' not in out:
                out.update(native_completed=archive['completed'],native_message=archive['message'],
                           native_trials=[dict(seed=t['seed'],evidence=t['evidence'],message=t['message'],
                                descent=t['resolved_descent'],optimizer_success=t['optimizer']['success'],
                                optimizer_tolerance_met=t['optimizer']['requested_tolerance_met']) for t in archive['trials']],
                           supplied_counts=dict(archive['supplied_counts']),supplied_excluded=0,
                           supplied_descents=sum(map(r.supplied_negative,archive['supplied_trials'])))
            else:
                if census:
                    options = eq.StabilityOptions()
                    template = type(p.phases[0])
                    seeds = []
                    for kind,ids in [('Liquid',r.s.COMPONENT_IDS),('Vapor',r.s.COMPONENT_IDS[:3])]:
                        phase = template()
                        phase.kind,phase.name,phase.support_declared = getattr(type(phase.kind),kind),kind,True
                        phase.support = [spec.parameters.component_ids.index(c) for c in ids]
                        seeds.append(phase)
                    options.trials = seeds
                else:
                    options = item.stability_options
                options.mode = type(options.mode).Full
                report = eq.stability_test(compiled,center,options)
                out.update(native_completed=report.completed,native_message=report.message,native_trials=trials(report))
                support = r.supplied_support(spec,item,compiled=compiled)
                supplied_bank = [dict(w,kind=w['kind'].capitalize()) for w in witnesses] if census else witnesses
                supplied, excluded, repeated, identities = r._applicable(item,supplied_bank,support)
                counts = Counter(evaluated=0)
                out['supplied_descents'] = 0
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
    from part_ii import SHA, WHEEL
    a.study.reuse.bind_wheel()
    r.verify()
    if sys.argv[1]=='mdea-rebuild':
        _, declaration_path, endpoint_path, bank_path, screen_path, folder, *modes = sys.argv[1:]
        declaration = r.read(endpoint_path)
        assert declaration['wheel']==SHA and 'rebuild-441' in folder.split('/')
        run = MDEAWeights(declaration_path,WORK/folder,fixed_reference_pressure_pa=declaration['reaction_reference_pressure_Pa'],
                          wheel=WHEEL,wheel_sha256=SHA)
        run.workers = min(8,len(os.sched_getaffinity(0)))
        trial_set = r.read(bank_path)
        mdea_rebuild(run,declaration['point'],trial_set['trials']+trial_set.get('supplied_trials',[]),
                     r.read(screen_path),modes=modes,folder=folder)
    elif sys.argv[1]=='mdea-comparison':
        _, mode, k, declaration, endpoint, bank_path, output, *sources = sys.argv[1:]
        assert mode in ('pilot','full','continue') and k in COMPARISON_SETS
        *prior, split_path = sources
        run = Route(declaration,WORK/MDEA_COMPARISON/k,wheel=WHEEL,wheel_sha256=SHA)
        run.workers = min(8,len(os.sched_getaffinity(0)))
        point = r.read(endpoint)
        registry = r.read(bank_path)
        bank = registry['trials']+registry.get('supplied_trials',[])
        assert len(bank)==2980 and registry['species']==run.config['species']
        comparison_screen(run,point,bank,run.states(run.bind(point)),
                          comparison_prior(list(map(Path,prior))),comparison_splits(None if split_path=='-' else split_path),
                          output,mode=mode)
    else:
        action,design,label = sys.argv[1:]
        if action=='controls':
            controls(design,label)
        elif action in ('parent-closure','parent-pilot'):
            screen_parents(design,workers=int(label),pilot=action=='parent-pilot')
        else:
            screening(design,label,pilot=action=='pilot')
