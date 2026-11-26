"""Measured MEA parent admission at matched absolute pressures."""
# ruff: noqa: E402
from collections import Counter
from concurrent.futures import ProcessPoolExecutor
import copy
import math
import sys
from time import monotonic
from types import SimpleNamespace

from mea_pressure import OUT, REFERENCE, a, canonical, eq, expanded, membership, pressure_record, pressure_template, requests, r, save, s
from classify_descents import coexistence, gibbs
from phases import physical, trials

BASE = a.BASE


def bubble_problem(p):
    return eq.Problem(T=p.T, P=eq.Free(1e5), feed=p.feed, reactions=p.reactions,
                      neutral_reference=p.neutral_reference, row_tolerance=p.row_tolerance,
                      phases=[eq.Phase('L',kind='liquid',support=s.COMPONENT_IDS),
                              eq.Phase('V',kind='vapor',support=s.COMPONENT_IDS[:3],amount=eq.Pinned(0.))])


def preparations(mapping, reaction_reference_pressure_pa=None):
    spec = r.bind(mapping, reaction_reference_pressure_pa=reaction_reference_pressure_pa)
    spec.inputs['endpoint'] = mapping
    records = expanded(spec)
    source_template = next(iter(requests()[0].values()))['request']
    for identity,row in canonical().items():
        if row['source_key']=='Jou1995' and row['temperature_reported_C']=='25' and row['MEA_weight_fraction']=='0.3':
            key = 'measured:'+identity
            evidence = dict(request=s.source_feed_request(source_template,row),targets=[
                dict(source_identity=row['source_key'],observed=float(row['CO2_pressure'])*1000)])
            records.append(pressure_record(spec,pressure_template(spec)[0],key,evidence,group='Jou measured 298 K'))
    return spec, {q['identity']:q for q in records}


def calculations(mapping, reference, names, solver_factor=1., reaction_reference_pressure_pa=None, bank=None):
    a.study.reuse.bind_wheel()
    r.verify()
    spec, records = preparations(mapping,reaction_reference_pressure_pa)
    prior, baseline = preparations(reference)
    if bank is None:
        bank = r.read(BASE/'split-registry.json')['trials']
    bank = [dict(w,kind=w['kind'].capitalize()) for w in bank]
    for identity in names:
        started = monotonic()
        q = records[identity]
        p = spec.problems[q['problem']]
        source = membership().get(identity) or q['row'].get('source_coordinates')
        record = dict(identity=identity,group=q['group'],T_K=p.T,feed_mol=p.feed.values,
                      source=source or q['row'],row_tolerance=p.row_tolerance,wheel=r.SHA)
        try:
            bubble = bubble_problem(p)
            if isinstance(p.P,eq.Free):
                pre = prior.problems[baseline[identity]['problem']]
                old = eq.solve_equilibrium(prior.model,bubble_problem(pre))
                if not old.requested_tolerance_met:
                    raise ValueError('Reference bubble: '+old.message)
                record['reference_bubble_Pa'] = old.pressure
                measured = float(source['total_pressure'])*1000 if source and source['total_pressure'] else None
                ratio = None if measured else 1.05
                pressure = measured if measured is not None else ratio*old.pressure
                record.update(pressure_basis='source total pressure' if measured else '1.05 times #435 bubble pressure',
                              reference_pressure_ratio=pressure/old.pressure)
            else:
                pressure = p.P
                record['pressure_basis'] = 'assigned observation pressure'
            record['P_Pa'] = pressure
            candidate = eq.solve_equilibrium(spec.model,bubble)
            if not candidate.requested_tolerance_met:
                raise ValueError('Candidate bubble: '+candidate.message)
            record['bubble_Pa'] = candidate.pressure
            if not isinstance(p.P,eq.Free):
                ref = eq.solve_equilibrium(prior.model,bubble_problem(prior.problems[baseline[identity]['problem']]))
                record.update(reference_bubble_Pa=ref.pressure if ref.requested_tolerance_met else None,
                              reference_pressure_ratio=pressure/ref.pressure if ref.requested_tolerance_met else None)
            liquid = pressure>=candidate.pressure
            problem = copy.copy(bubble)
            problem.P = pressure
            problem.row_tolerance = p.row_tolerance*solver_factor
            phase = problem.phases[0]
            phase.composition_guess = list(candidate.phase_mole_fractions(0))
            phase.packing_guess = candidate.packing_fractions[0]
            if liquid:
                problem.phases = [phase]
            else:
                vap = problem.phases[1]
                vap.amount = eq.Free()
                vap.composition_guess = {k:candidate.phase_mole_fractions(1)[i] for i,k in enumerate(s.COMPONENT_IDS[:3])}
                vap.packing_guess = candidate.packing_fractions[1]
            record['declared_parent'] = 'liquid' if liquid else 'liquid-vapour'
            parent = eq.solve_equilibrium(spec.model,problem)
            record.update(parent_status=parent.message, realized_Pa=parent.pressure, amounts_mol=list(parent.amounts),
                          solver_row_tolerance=problem.row_tolerance)
            if not parent.requested_tolerance_met or min(parent.amounts)<=0:
                raise ValueError(parent.message)
            native_parent = problem._native(spec.parameters)
            validation = copy.copy(problem)
            validation.row_tolerance = p.row_tolerance
            validation = validation._native(spec.parameters)
            record['parent'] = physical(spec,validation,parent)
            if any(abs(q['pressure_residual_Pa'])/pressure > p.row_tolerance for q in record['parent']['phases']):
                nearby = copy.copy(problem)
                nearby.P = .999*pressure
                nearby.phases = [copy.copy(q) for q in problem.phases]
                for i, phase in enumerate(nearby.phases):
                    phase.composition_guess = {k:parent.phase_mole_fractions(i)[s.COMPONENT_IDS.index(k)]
                                               for k in phase.support}
                    phase.packing_guess = parent.packing_fractions[i]
                seed = eq.solve_equilibrium(spec.model,nearby)
                record['pressure_restart'] = dict(P_Pa=nearby.P,message=seed.message,original_parent=record['parent'])
                if not seed.requested_tolerance_met:
                    raise ValueError(seed.message)
                parent = eq.solve_equilibrium(spec.model,problem,start=seed)
                record.update(parent_status=parent.message, realized_Pa=parent.pressure,amounts_mol=list(parent.amounts))
                if not parent.requested_tolerance_met or min(parent.amounts)<=0:
                    raise ValueError(parent.message)
                record['parent'] = physical(spec,validation,parent)
            compiled = eq.compile_problem(spec.model,problem)
            options = eq.StabilityOptions()
            options.mode = type(options.mode).Full
            optimized = eq.stability_test(compiled,parent,options)
            record['optimized_message'] = optimized.message
            record['native_no_descent'] = optimized.no_descent_in_trial_set
            native = trials(optimized)
            # 2 MEA + CO2 -> MEAH+ + MEACOO-. Apply an interior extent to the analytical feed.
            inventory = [math.fsum(n*parent.phase_mole_fractions(i)[j] for i,n in enumerate(parent.amounts))
                         for j in range(len(s.COMPONENT_IDS))]
            vectors = dict(zip(s.COMPONENT_IDS,inventory,strict=True))
            extent = .5*min(vectors['carbon-dioxide'],.5*vectors['monoethanolamine'])
            change = {'carbon-dioxide':-1,'monoethanolamine':-2,'protonated-monoethanolamine':1,'carbamate-anion':1}
            seed = {k:n+extent*change.get(k,0.) for k,n in vectors.items()}
            total = math.fsum(seed.values())
            x = [v/total for v in seed.values()]
            rho = spec.model.state(p.T,P=pressure,x=x,phase='liquid').molar_density
            packing = rho*spec.model._model.packing_fraction_coefficient(p.T,x)
            formula = spec.spec['element_formulas']
            balance = {element:math.fsum(formula[k].get(element,0)*(seed[k]-vectors[k]) for k in seed)
                       for element in ('C','H','N','O','charge')}
            record['ion_rich_seed'] = dict(amounts_mol=seed,extent_mol=extent, balance_change_mol=balance,
                 strictly_positive=min(seed.values())>0,packing_fraction=packing)
            supplied = bank + [dict(support=list(range(len(x))),composition=x,kind='Liquid',packing=packing)]
            item = SimpleNamespace(problem=native_parent)
            phases, absent, repeated, _ = r._applicable(item,supplied,set(range(len(x)))-set(compiled.removed_species))
            options = eq.StabilityOptions()
            options.prepared_trials = eq.prepare_supplied_trials(spec.model,p.T,phases)
            tested = eq.stability_test(compiled,parent,options).trials
            counts = Counter(tested[i].evidence for i,_ in repeated)
            witnesses = [dict(t,packing=math.exp(w.split_coordinates[-1]),source='optimized') for t,w in
                         zip(native,optimized.trials,strict=True) if t['descent'] and w.split_coordinates]
            witnesses += [dict(seed,quantities=tested[i].quantities,source='supplied') for i,seed in repeated
                          if r.supplied_negative(dict(evidence=tested[i].evidence,quantities=tested[i].quantities))]
            record.update(native_trials=native,supplied_counts=dict(counts),supplied_not_applicable=len(absent),
                          ion_rich_result=next((dict(evidence=tested[i].evidence,quantities=tested[i].quantities)
                                      for i,w in reversed(repeated) if w is supplied[-1]),None),
                          witnesses=witnesses)
            if liquid and witnesses:
                parent_g = gibbs(compiled,parent)
                guesses = (list(parent.phase_mole_fractions(0)),parent.packing_fractions[0])
                record['fixed_pressure_rechecks'] = [coexistence(spec,item.problem,parent_g,
                    [guesses,(w['composition'],w['packing'])],
                    inspect=lambda c,v: physical(spec,item.problem,v) if v.requested_tolerance_met and len(v.amounts)==2 and min(v.amounts)>0 else None)
                    for w in witnesses if w['kind']=='Liquid' and len(w['composition'])==len(x)]
            record['available'] = (record['parent']['physical_checks_pass']
                    and optimized.completed
                    and record['ion_rich_seed']['strictly_positive']
                    and counts['evaluated']==len(repeated) and bool(native))
        except (ValueError,RuntimeError,IndexError,TypeError,AttributeError) as error:
            record.update(available=False,cause=f'{type(error).__name__}: {error}')
        if not record['available'] and 'cause' not in record:
            record['cause'] = 'Inspect parent physical checks and native and supplied trial dispositions'
        record['seconds'] = monotonic()-started
        yield record


def chunk(args):
    return list(calculations(*args))


def measured(mapping, label, *, reaction_reference_pressure_pa=None, pilot_only=False):
    start = monotonic()
    reference = s.parameter_mapping(REFERENCE/'F4/parameters.json')
    spec, rows = preparations(reference)
    names = list(membership())
    names.extend(i for i in rows if i.startswith('measured:'))
    names.extend(x['identity'] for x in rows.values() if x['group'] in ('loaded density','restored species','Jakobsen','common149')
                 and x['constructor']=='observation' and x['kind']!='partial_pressure'
                 and spec.problems[x['problem']].reactions)
    names = list(dict.fromkeys(names))
    output = []
    batches = [names[i:i+8] for i in range(0,len(names),8)]
    def record(i, payload):
        save(OUT / f'E/{label}/measured/{i}.json.gz',payload)
        output.extend(payload)
    pilot_path = OUT / f'E/{label}/measured-pilot.json.gz'
    if not pilot_path.is_file():
        pilot = chunk((mapping,reference,names[::37],1.,reaction_reference_pressure_pa))
        save(pilot_path,dict(rows=pilot, seconds=monotonic()-start,
             estimate_worker_s=sum(x['seconds'] for x in pilot)*len(names)/len(pilot),states=len(names)))
    if pilot_only:
        return r.read(pilot_path)
    pending = {}
    for i,batch in enumerate(batches):
        path = OUT / f'E/{label}/measured/{i}.json.gz'
        if not path.is_file():
            pending[i] = (batch,{})
            continue
        retained = {x['identity']:x for x in r.read(path)}
        assert list(retained)==batch
        repair = [k for k,x in retained.items() if x.get('ion_rich_seed',{}).get('strictly_positive') is False]
        if repair:
            save(OUT / f'E/{label}/measured-initial/{i}.json.gz',list(retained.values()))
            pending[i] = (repair,retained)
        else:
            output.extend(retained.values())
    with ProcessPoolExecutor(r.CORES) as pool:
        for (i,(_,old)),fresh in zip(pending.items(),
                pool.map(chunk,[(mapping,reference,names,1.,reaction_reference_pressure_pa) for names,_ in pending.values()]),strict=True):
            if old:
                old.update({x['identity']:x for x in fresh})
                fresh = list(old.values())
            record(i,fresh)
    summary = dict(states=len(output),available=sum(x['available'] for x in output),
                   descents=sum(bool(x.get('witnesses')) for x in output),seconds=monotonic()-start)
    save(OUT / f'E/{label}/measured-summary.json',summary)
    return summary


def coverage(label):
    started = monotonic()
    path = REFERENCE/'F4/parameters.json' if label=='incumbent' else OUT/f'E/{label}/parameters.json'
    mapping = s.parameter_mapping(path)
    if label=='incumbent':
        retained = r.read(REFERENCE/'F4/search-summary.json')
        assert retained['parameter_sha256']==s.sha256(path)
        assert retained['registry_sha256']==a.REGISTRY
        save(OUT/f'E/{label}/grid-summary.json',retained)
    elif (summary_path := OUT/f'E/{label}/grid-summary.json').is_file():
        retained = r.read(summary_path)
        assert retained.get('parameter_sha256',s.sha256(path))==s.sha256(path)
        assert retained['registry_sha256']==a.REGISTRY
    else:
        run_path = OUT/f'E/{label}/grid'
        identity_path = OUT/f'E/{label}/grid-input.json'
        digest = s.sha256(path)
        identity = dict(wheel_sha256=r.SHA,parameter_sha256=digest,registry_sha256=a.REGISTRY)
        assert not identity_path.is_file() or r.read(identity_path)==identity
        save(identity_path,identity)
        retained = a.study.reuse.mea_search(label,mapping,None,output=run_path,resume=True)
        save(OUT/f'E/{label}/grid-summary.json',dict(retained,parameter_sha256=s.sha256(path)))
    new = measured(mapping,label)
    grid_pass = all(not retained[g]['unavailable'] and not retained[g]['descent'] for g in ('grid','offset'))
    grid_pass &= retained['census']['descent']==retained['census']['incomplete']==retained['missing_supplied']==0
    save(OUT/f'E/{label}/coverage.json',dict(grid_pass=grid_pass,
         measured_pass=new['available']==new['states'] and not new['descents'],seconds=monotonic()-started))


def pressure_closure_probe():
    started = monotonic()
    path = REFERENCE/'F4/parameters.json'
    mapping = s.parameter_mapping(path)
    failures = [q for batch in (OUT/'E/incumbent/measured').glob('*.json.gz') for q in r.read(batch)
                if not q['available'] and q.get('parent') and not q['parent']['physical_checks_pass']]
    states = [x for kind in ('liquid','liquid-vapour') for x in
              sorted((q for q in failures if q['declared_parent']==kind),key=lambda q:q['identity'])[::13]][:8]
    names = [q['identity'] for q in states]
    recalculated = list(calculations(mapping,mapping,names,.1))
    save(OUT/'D/MEA-pressure-closure-tightened.json.gz',dict(seconds=monotonic()-started,
         hypothesis='Smaller native solve tolerance improves independent EOS pressure closure at the original acceptance tolerance',
         original=states,recalculated=recalculated,parameter_sha256=s.sha256(path)))
    root = OUT/'E/incumbent/measured-refined'
    save(root/'pilot.json.gz',recalculated)
    if not all(q['available'] and not q['witnesses'] for q in recalculated):
        return
    rest = [q['identity'] for q in failures if q['identity'] not in names]
    batches = [rest[i:i+4] for i in range(0,len(rest),4)]
    with ProcessPoolExecutor(r.CORES) as pool:
        for i,rows in enumerate(pool.map(chunk,[(mapping,mapping,batch,.1) for batch in batches])):
            save(root/f'{i}.json.gz',rows)
    save(OUT/'E/incumbent/pressure-refinement-timing.json',dict(seconds=monotonic()-started,states=len(failures)))


def controls():
    started = monotonic()
    path = REFERENCE/'controls/readback.json'
    prior = r.read(path)
    assert prior['wheel_sha256']==r.SHA
    r.OUT = OUT/'D/MEA-controls'
    stable = a.study.RECORD
    wide = r.ROOT/prior['prior_wide_parameters']['path']
    assert r.s.sha256(stable)==prior['adopted_F2_parameters_sha256']
    assert r.s.sha256(wide)==prior['prior_wide_parameters']['sha256']
    trial = prior['supplied_state_38']['trial']
    trials = {'38':[trial]}
    results = {}
    for name,source in (('historical-F2',stable),('wide F2 stress',wide)):
        results[name] = r.census(s.parameter_mapping(source),name.replace(' ','-'),trials,indices=[38],keep_refusals=True)
    save(r.OUT/'readback.json',dict(results=results,seconds=monotonic()-started,
         passed=results['historical-F2']['descent']==0 and results['wide F2 stress']['descent']==1
         and all(q['incomplete']==0 for q in results.values()),prior_sha256=s.sha256(path)))


if __name__=='__main__':
    a.study.reuse.bind_wheel()
    r.verify()
    for label in sys.argv[1:]:
        if label=='controls':
            controls()
        elif label=='pressure-probe':
            pressure_closure_probe()
        else:
            coverage(label)
