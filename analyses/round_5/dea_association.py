"""Refit the DEA binary and reactive stages with explicit unlike association edges."""
import importlib.util
from pathlib import Path
from tempfile import TemporaryDirectory
from time import monotonic
import sys

HERE = Path(__file__).resolve().parent
records_spec = importlib.util.spec_from_file_location('round5_records',HERE/'common.py')
records = importlib.util.module_from_spec(records_spec)
records_spec.loader.exec_module(records)
DEA_SOURCE = HERE.parent/'dea_transfer'
sys.path[:0] = [str(DEA_SOURCE),str(DEA_SOURCE/'diagnosis-410')]
import binary_refit as binary
from excess_enthalpy import explicit_cross
from part_ii import Route, epcsaft, eq, reg, stable
import reduced_refit_338 as reduced
from reactive_refit import BINARY, ROUTE

COMBINING = DEA_SOURCE/'results/reactive-refit-425'
NOMINAL = (1.,1.05,1.10,1.15)


def binary_stability(doc, rows):
    parameters = epcsaft.Parameters.from_mapping(doc)
    model = epcsaft.Mixture(parameters)
    result = []
    for r in rows:
        if not r['fitted'] or r['group'] == binary.HEAT or r['predicted'] is None:
            continue
        feed = binary.composition(r['x'])
        L = eq.Phase('L',kind='liquid',support=list(feed))
        P = r['predicted']*1000
        problem = eq.Problem(T=r['T'],P=P,feed=eq.Amounts(feed),phases=[L],row_tolerance=1e-10)
        try:
            solved = eq.solve_equilibrium(model,problem)
            if not solved.requested_tolerance_met:
                raise ValueError(solved.message)
            compiled = eq.compile_problem(model,problem)
            opts = eq.StabilityOptions()
            opts.mode = type(opts.mode).Full
            compiled_trials = eq.Problem(T=r['T'],P=P,feed=eq.Amounts(feed),phases=[
                eq.Phase('L2',kind='liquid',support=list(feed)),
                eq.Phase('V',kind='vapor',support=list(feed))])
            opts.trials = reg.stability(parameters,compiled_trials,scale=1.).problem.phases
            report = eq.stability_test(compiled,solved,opts)
            result.append(dict(group=r['group'],T_K=r['T'],P_Pa=P,x_water=r['x'],
                               trials=[dict(seed=t.seed,descent=t.resolved_descent,evidence=t.evidence,
                                            quantities=t.quantities) for t in report.trials]))
        except (RuntimeError,ValueError,TypeError) as error:
            result.append(dict(group=r['group'],T_K=r['T'],P_Pa=P,x_water=r['x'],refusal=str(error)))
    return result


def replay_stability():
    reference = COMBINING/'run/selection.json'
    chosen = stable.read(reference)['chosen']
    baseline = chosen['parameters']['parameters']
    explicit, epsilon, volume = explicit_cross(baseline,1.)
    args = dict(T=363.15,rho=30000.,x=binary.composition(.6))
    association = [binary.mixture(doc).state(**args).association for doc in (baseline,explicit)]
    combining_fit = stable.read(BINARY)
    records.save('E/DEA-explicit-1-control.json',dict(
        state=args, combining_association=association[0], explicit_association=association[1],
        association_difference=association[1]-association[0], explicit_energy_K=epsilon, explicit_volume=volume,
        combining_binary=combining_fit['replay_cost'], combining_a=combining_fit['a'],
        combining_b_K=combining_fit['b'], combining_reactive=chosen['cost'],
        inputs=records.fingerprints(reference,BINARY)))
    for multiplier in NOMINAL:
        name = f'E/DEA-association-{multiplier:g}-binary.json.gz'
        path = records.RESULTS/name
        if not path.is_file():
            continue
        tick = monotonic()
        record = stable.read(path)
        mapping = explicit_cross(baseline,multiplier)[0]
        endpoint = binary.with_binary(mapping,record['a'],record['b_K'])
        prior = record['binary_stability']
        stability = binary_stability(endpoint,record['postfit'])
        records.save(name,dict(record, binary_stability=stability, prior_binary_stability=prior,
                               binary_stability_replay_seconds=monotonic()-tick))


def calculate(work):
    started = monotonic()
    refit = stable.read(BINARY)
    comparison_path = COMBINING/'run/selection.json'
    comparison = stable.read(comparison_path)['chosen']
    doc = comparison['parameters']['parameters']
    inputs = list(binary.rows())
    rows = [r for r in inputs if r['fitted']]
    assert [sum(r['group']==g for r in rows) for g in binary.GROUPS]==[42,7,14]
    combine = binary.evaluate(doc, inputs, readback=True)
    records.save('E/DEA-combining-rule.json.gz',dict(binary_rows=combine,
                 binary_scores=binary.reduce_rows(combine), reactive_cost=comparison['cost'],
                 inputs=records.fingerprints(BINARY,comparison_path,ROUTE)),start=started)
    for multiplier in NOMINAL:
        tick = monotonic()
        label = f'{multiplier:g}'
        trial, epsilon, kappa = explicit_cross(doc,multiplier)
        before = binary.evaluate(trial,inputs,readback=True)
        fit, rejected = binary.search(trial,rows,(refit['a'],refit['b']),constrained=False)
        a,b = map(float,binary.SCALE*fit.x)
        endpoint = binary.with_binary(trial,a,b)
        after = binary.evaluate(endpoint,inputs,readback=True)
        pure_changes = [dict(group=r['group'], x_water=r['x'],T_K=r['T'],
                             difference=p['predicted']-r['predicted'] if p['predicted'] is not None and r['predicted'] is not None else None)
                        for r,p in zip(combine,before,strict=True) if not r['fitted']]
        record = dict(multiplier=multiplier,explicit_energy_K=epsilon*multiplier,explicit_volume=kappa,
                      prefit=before,postfit=after,pure_limit_changes=pure_changes,
                      before_scores=binary.reduce_rows(before),after_scores=binary.reduce_rows(after),
                      a=a,b_K=b,optimizer=dict(fit),rejected=rejected,combining_rule_a=refit['a'],combining_rule_b=refit['b'])
        name = f'E/DEA-association-{label}-binary.json.gz'
        records.save(name,record,start=tick)
        record['binary_stability'] = binary_stability(endpoint,after)
        records.save(name,record,start=tick)
        route = Route(ROUTE,work/label)
        starts = []
        for i, pref in enumerate(route.config['starts']):
            other = route.start(pref)
            point = dict(other,parameters=binary.with_binary(explicit_cross(other['parameters'],multiplier)[0],a,b))
            name = f'start-{i}'
            p,r = reduced.fit(name,point,{},[],route=route,penalty_rows=[])
            starts.append(dict(point=p,report=r,initial=point,
                               rows={f.relative_to(route.out/name).as_posix():stable.read(f) for f in (route.out/name).rglob('*.json')}))
        usable = [r for r in starts if r['report'] and r['report'].get('endpoint_replay_available') and r['report']['status']=='converged']
        chosen = min(usable,key=lambda r:r['report']['endpoint_replay_cost'],default=None)
        data = route.reduce(chosen['point']) if chosen is not None else []
        records.save(f'E/DEA-association-{label}-reactive.json.gz',dict(starts=starts,chosen=chosen,
                     data_rows=data, Lawson_and_Carson=[r for r in data if r['group'] in ('Lawson','Carson')]),start=tick)
        if monotonic()-started>1080:
            records.save('E/DEA-association-timing.json',dict(stop='Twice the 9-minute upper projection elapsed',last_multiplier=multiplier),start=started)
            return
    records.save('E/DEA-association-timing.json',dict(projection_minutes=[3,9]),start=started)


if __name__=='__main__':
    import argparse

    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--stability-only', action='store_true')
    if parser.parse_args().stability_only:
        replay_stability()
    else:
        with TemporaryDirectory() as directory:
            calculate(Path(directory))
