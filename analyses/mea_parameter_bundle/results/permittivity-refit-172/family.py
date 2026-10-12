"""Issue 172 original attempt sequence and amendment 2 stability classification."""
import concurrent.futures as cf
import copy
import json
import math
import multiprocessing
from pathlib import Path
import sys

import run as c
sys.path.insert(0,str(c.OUT.parent/'permittivity-screen-172'))
import permittivity_probe as screen

MAPPING = None
COLD = []


def payload(r):
    return dict(success=r.success,requested_tolerance_met=r.requested_tolerance_met,message=r.message,
        residual=r.convergence.residual,amounts=list(r.amounts),mole_fractions=list(r.mole_fractions),
        densities=list(r.molar_densities),packing=list(r.packing_fractions),coordinates=list(r.coordinates),
        objective=r.objective,iterations=r.iterations,reduced_hessian_minimum=r.reduced_hessian_minimum,
        residuals=list(r.residuals),constraint_multipliers=list(r.constraint_multipliers))


def problem(index,liquid=False):
    loading,T,P = screen.POINTS[index]
    p = screen.flash_problem('current',loading,T,P,
        [c.h.eq.Phase('L',kind='liquid',support=c.s.COMPONENT_IDS)] if liquid else None)
    params,groups,_ = c.h.d.rows_for(MAPPING,'11')
    request = c.s.corrected_request(groups[0][0]['request'],c.s.reaction_values(MAPPING))
    p.reactions = c.s._problem_from_request(request).reactions
    p.neutral_reference = c.s._neutral_reference(request)
    return p


def cold(index):
    try:
        r = c.h.eq.solve_equilibrium(screen.mixture(MAPPING),problem(index))
        return dict(index=index,**payload(r))
    except Exception as error:
        return dict(index=index,success=False,message=f'{type(error).__name__}: {error}')


def stable(model,p,r):
    trial = copy.copy(p)
    trial.phases = [c.h.eq.Phase('L',kind='liquid',support=c.s.COMPONENT_IDS),
        c.h.eq.Phase('V',kind='vapor',support=c.s.COMPONENT_IDS[:3])]
    options = c.h.eq.StabilityOptions()
    options.trials = trial._native(model).phases
    report = c.h.eq.stability_test(c.h.eq.compile_problem(model,p),r,options)
    trials = [dict(seed=t.seed,support=list(t.phase.support),evidence=t.evidence,
        resolved_descent=t.resolved_descent,optimizer_success=t.optimizer.success,
        optimizer_message=t.optimizer.message,message=t.message,quantities=dict(t.quantities),
        raw_coordinates=list(t.raw_coordinates),raw_residuals=list(t.raw_residuals),split_checks=list(t.split_checks)) for t in report.trials]
    descent = any(t['resolved_descent'] for t in trials)
    unresolved = not report.completed or any(not t['optimizer_success'] or t['evidence'] in
        ('unresolved','indeterminate','negative_plane_without_positive_donor') for t in trials)
    return dict(completed=report.completed,message=report.message,trials=trials,descent=descent,unresolved=unresolved)


def finish(index):
    loading,T,P = screen.POINTS[index]
    model,p = screen.mixture(MAPPING),problem(index)
    row = dict(index=index,loading=loading,temperature_K=T,pressure_Pa=P,attempts=[COLD[index]])
    final,final_problem,kind = None,p,'two-phase'
    if COLD[index]['success']:
        batch = c.h.eq.solve_equilibrium_starts(model,p,[c.h.eq.EquilibriumStart(coordinates=COLD[index]['coordinates'])],
            c.h.eq.EquilibriumWorkLimits(attempts=1,attempt_iterations=400,iterations=400))
        if batch.selected is not None: final = batch.results[batch.selected]
    else:
        nearest = sorted((r for r in COLD if r['success'] and screen.POINTS[r['index']][1]==T),
            key=lambda r:abs(screen.POINTS[r['index']][0]-loading)+abs(math.log(screen.POINTS[r['index']][2]/P)))[:2]
        row['nearest_seed_indices'] = [r['index'] for r in nearest]
        if nearest:
            batch = c.h.eq.solve_equilibrium_starts(model,p,[c.h.eq.EquilibriumStart(coordinates=r['coordinates']) for r in nearest],
                c.h.eq.EquilibriumWorkLimits(attempts=2,attempt_iterations=400,iterations=800))
            row['attempts'] += [dict(cause=cause,result=None if r is None else payload(r)) for cause,r in zip(batch.causes,batch.results)]
            if batch.selected is not None: final = batch.results[batch.selected]
    liquid_problem = problem(index,True)
    liquid = c.h.eq.solve_equilibrium(model,liquid_problem)
    row['liquid'] = payload(liquid)
    bubble = None
    if liquid.success:
        bp = copy.copy(liquid_problem)
        bp.phases = [c.h.eq.Phase('L',kind='liquid',composition_guess=liquid.mole_fractions[:9],packing_guess=liquid.packing_fractions[0]),
            c.h.eq.Phase('V',kind='vapor',support=c.s.COMPONENT_IDS[:3],amount=c.h.eq.Pinned(0.))]
        bp.P = c.h.eq.Free(P)
        bubble = c.h.eq.solve_equilibrium(model,bp)
        row['bubble'] = payload(bubble)
        if bubble.success:
            Pb = bubble.pressure[0]
            row['bubble_pressure_Pa'] = Pb
            row['bubble_EOS_pressure_closure_Pa'] = max(abs(model.state(T,rho=rho,x=list(bubble.mole_fractions[offset:offset+width])+[0.]*(9-width)).pressure-Pb)
                for rho,offset,width in zip(bubble.molar_densities,(0,9),(9,3),strict=True))
            if final is None and P < Pb:
                starts = [c.h.eq.EquilibriumStart(amounts=[bubble.amounts[0]*f,bubble.amounts[0]*(1-f)],
                    compositions=[bubble.mole_fractions[:9],bubble.mole_fractions[9:12]],packing_fractions=bubble.packing_fractions) for f in (.5,.9)]
                batch = c.h.eq.solve_equilibrium_starts(model,p,starts,c.h.eq.EquilibriumWorkLimits(attempts=2,attempt_iterations=400,iterations=800))
                row['attempts'] += [dict(cause=cause,result=None if r is None else payload(r)) for cause,r in zip(batch.causes,batch.results)]
                if batch.selected is not None: final = batch.results[batch.selected]
            if final is None and P > Pb:
                final,final_problem,kind = liquid,liquid_problem,'single-liquid'
    row['classification'] = 'failed'
    if final is not None and final.success and final.requested_tolerance_met and all(a>=0 for a in final.amounts):
        row['final'] = payload(final)
        try:
            evidence = stable(model,final_problem,final)
            row['stability'] = evidence
            if evidence['descent']: return row
            row['classification'] = 'unresolved'
            if evidence['unresolved'] or not row.get('bubble_pressure_Pa'): return row
            if abs(P-row['bubble_pressure_Pa']) <= row['bubble_EOS_pressure_closure_Pa']: return row
            consistent = P < row['bubble_pressure_Pa'] if kind=='two-phase' else P > row['bubble_pressure_Pa']
            row['classification'] = kind if consistent else 'failed'
        except Exception as error:
            row.update(classification='unresolved',stability_failure=f'{type(error).__name__}: {error}')
    return row


def family(mapping,directory):
    global MAPPING,COLD
    MAPPING = mapping
    with cf.ProcessPoolExecutor(c.WORKERS,mp_context=multiprocessing.get_context('fork')) as pool:
        COLD = list(pool.map(cold,range(73)))
    c.write(directory/'family-cold.json',COLD)
    with cf.ProcessPoolExecutor(c.WORKERS,mp_context=multiprocessing.get_context('fork')) as pool:
        rows = list(pool.map(finish,range(73)))
    c.write(directory/'family.json',rows)
    counts = {kind:sum(r['classification']==kind for r in rows) for kind in ('two-phase','single-liquid','unresolved','failed')}
    assert sum(counts.values())==73
    c.write(directory/'family-counts.json',counts)
    c.table(directory/'family.csv',[{k:v for k,v in r.items() if k not in ('attempts','final','stability','liquid','bubble')} for r in rows])
    print('FAMILY',directory,counts,flush=True)


if __name__=='__main__':
    if sys.argv[1]=='classifier':
        MAPPING = screen.VARIANTS['MEA-1403-CO2-near-zero']
        COLD = [dict(r,success=r['accepted']) for r in screen.read(c.OUT/'inputs/screen-family.json')
            if r['basis']=='current' and r['variant']=='MEA-1403-CO2-near-zero']
        row = finish(63)
        c.write(c.OUT/'classifier-check.json',row)
        assert row['classification']=='unresolved', row
        assert any(t['evidence']=='indeterminate' for t in row['stability']['trials'])
        assert any(not t['optimizer_success'] for t in row['stability']['trials'])
        print('CLASSIFIER',row['classification'],flush=True)
    elif sys.argv[1]=='baseline': family(c.s.parameter_mapping(),c.OUT/'baseline')
    else: family(json.loads(Path(sys.argv[1]).read_text()),Path(sys.argv[2]))
