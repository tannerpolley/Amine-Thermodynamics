"""Disposable issue-201 diagnosis; never writes the original phase results."""
import argparse
import hashlib
import json
import math
import os
from pathlib import Path
import resource
import signal
import subprocess
import sys
import time

HERE = Path(__file__).resolve().parent
RUN = HERE.parent


def read(path):
    return json.loads(Path(path).read_text())


def write(path, value):
    Path(path).write_text(json.dumps(value, indent=2, allow_nan=False) + '\n')


def supervise(args):
    ledger = read(HERE/'budget.json') if (HERE/'budget.json').exists() else []
    wall_left = 900 - sum(r['wall_s'] for r in ledger)
    cpu_left = 2700 - sum(r['cpu_s'] for r in ledger)
    assert min(wall_left, cpu_left) > 0
    name = args.name
    assert not (HERE/f'{name}.json').exists() and not (HERE/f'{name}.log').exists()
    command = [sys.executable, str(Path(__file__).resolve()), '--worker', *sys.argv[1:]]
    before = resource.getrusage(resource.RUSAGE_CHILDREN)
    start = time.monotonic()
    with (HERE/f'{name}.log').open('w') as log:
        child = subprocess.Popen(command, stdout=log, stderr=subprocess.STDOUT, start_new_session=True)
        killed = False
        try:
            child.wait(timeout=min(150, wall_left, cpu_left))
        except subprocess.TimeoutExpired:
            os.killpg(child.pid, signal.SIGKILL)
            child.wait()
            killed = True
    after = resource.getrusage(resource.RUSAGE_CHILDREN)
    entry = dict(name=name, command=command, pid=child.pid, wall_s=time.monotonic()-start,
                 cpu_s=after.ru_utime+after.ru_stime-before.ru_utime-before.ru_stime,
                 max_rss_kib=after.ru_maxrss, exitcode=child.returncode, killed=killed,
                 host_load=os.getloadavg())
    ledger.append(entry)
    write(HERE/'budget.json', ledger)
    print(json.dumps(entry), flush=True)
    print((HERE/f'{name}.log').read_text(), end='')
    assert child.returncode == 0


def worker(args):
    for key in ('OMP_NUM_THREADS','OPENBLAS_NUM_THREADS','MKL_NUM_THREADS','BLIS_NUM_THREADS','NUMEXPR_NUM_THREADS'):
        os.environ[key] = '1'
    sys.path.insert(0, str(HERE.parents[2]/'scripts'))
    import phase_extension_201 as extension
    f, eq = extension.f, extension.f.eq
    f.s.verify_wheel()

    def payload(model, problem, result):
        value = f.phase_payload(model, problem, result)
        value['solver_settings'] = result.solver_settings
        value['linear_solver'] = result.linear_solver
        value['rows'] = [dict(index=i, kind=r.kind.name, phase=r.phase, species_or_moiety=r.index, eqid=r.eqid,
                              residual=value['residuals'][i], classified=value['classified_residuals'][i])
                         for i, r in enumerate(result.rows)]
        value['failing_classified_rows'] = [r for r in value['rows'] if abs(r['classified']) > 1e-10]
        return value

    def seed_phases(problem, seed):
        for i, phase in enumerate(problem.phases):
            count = 9 if i == 0 else 3
            phase.composition_guess = seed['mole_fractions'][i*9:i*9+count]
            phase.packing_guess = seed['packing_fractions'][i]
            if i == 0:
                phase.amount = eq.Free(seed['amounts'][i])
        problem.P = eq.Free(seed['pressure'])

    result_path = HERE/f'{args.name}.json'
    meta = dict(mode=args.mode, probe_sha256=hashlib.sha256(Path(__file__).read_bytes()).hexdigest(), source_commit=subprocess.check_output(['git','rev-parse','HEAD'],text=True).strip(),
                python=sys.version, engine_commit=f.s.ENGINE_COMMIT, wheel_sha256=f.s.sha256(f.s.installed_wheel()),
                engine_path=str(f.epcsaft.__file__), nice=os.getpriority(os.PRIO_PROCESS,0),
                threads={k:os.environ[k] for k in ('OMP_NUM_THREADS','OPENBLAS_NUM_THREADS','MKL_NUM_THREADS','BLIS_NUM_THREADS','NUMEXPR_NUM_THREADS')},
                libraries={k:extension.importlib.metadata.version(k) for k in ('epcsaft','numpy','scipy')},
                row_tolerance=1e-10, seed=args.seed, basis_mol=dict(MEA=9.7292821,water=76.9751925))
    if args.mode == 'reference':
        mapping, data = read(RUN/'inputs/reference-runtime.json'), read(RUN/'inputs/engine-case7-reactions.json')
        model = f.epcsaft.Mixture(f.epcsaft.Parameters.from_mapping(mapping, components=f.s.COMPONENT_IDS))
        reactions = [eq.Reaction(nu,correlation=eq.ReactionLogPolynomial(a,0.,0.,0.,data['T_ref'],data['T_min'],data['T_max'],eq.EOS_STANDARD_STATE_ID))
                     for nu,a in zip(data['stoichiometry'],data['ln_k'],strict=True)]
        problem = eq.Problem(T=args.temperature,P=eq.Free(7398.16),
            feed=eq.Amounts({'carbon-dioxide':args.feed_scale*args.loading*9.7292821,'monoethanolamine':args.feed_scale*9.7292821,'water':args.feed_scale*76.9751925}),
            reactions=reactions,row_tolerance=1e-10,
            phases=[eq.Phase('L',kind='liquid'),eq.Phase('V',kind='vapor',support=f.s.COMPONENT_IDS[:3],amount=eq.Pinned(0.))])
        if args.seed:
            seed_phases(problem, read(args.seed)['result'])
        if args.pressure_guess is not None:
            problem.P = eq.Free(args.pressure_guess)
        result = eq.solve_equilibrium(model,problem)
        value = payload(model,problem,result)
        meta.update(temperature_K=args.temperature,loading=args.loading,pressure_guess_Pa=problem.P.guess,feed_scale=args.feed_scale,actual_feed_mol=problem.feed.values,
                    reaction_domain_K=[data['T_min'],data['T_max']], result=value)
        meta['admitted'] = bool(result.success and result.requested_tolerance_met and 1 <= result.pressure <= 1e7
            and result.amounts[0]>0 and result.amounts[1]==0 and max(map(abs,value['raw_residuals']))<=1e-10
            and result.reduced_hessian_minimum>=0 and all(v>0 for v in value['pressure_density_derivatives']))
    else:
        old = read(RUN/args.fit/f'point-{args.index}.json')
        mapping = f.s.parameter_mapping(extension.FITS[args.fit])
        model = f.epcsaft.Mixture(f.epcsaft.Parameters.from_mapping(mapping),thermochemistry=f.thermal.record())
        request = extension.request(mapping,313.15,.11)
        meta.update(fit=args.fit,index=args.index,temperature_K=old['temperature_K'],loading=old['loading'],pressure_Pa=old['pressure_Pa'])
        if args.mode == 'parent':
            history = [] if not args.seed else [read(args.seed)]
            row = {k:old[k] for k in ('index','temperature_K','loading','pressure_Pa')}
            f.family_job(mapping,request,row,history,result_path)
            meta['row'] = read(result_path)
        elif args.mode == 'bubble':
            problem = f.flash_problem(request,old['loading'],old['temperature_K'],old['pressure_Pa'],
                [eq.Phase('L',kind='liquid',support=f.s.COMPONENT_IDS),
                 eq.Phase('V',kind='vapor',support=f.s.COMPONENT_IDS[:3],amount=eq.Pinned(0.))])
            liquid = old['liquid']
            problem.phases[0].composition_guess = liquid['mole_fractions'][:9]
            problem.phases[0].packing_guess = liquid['packing_fractions'][0]
            problem.P = eq.Free(old['pressure_Pa'])
            if args.seed:
                seed_doc = read(args.seed)
                seed = seed_doc.get('result') or seed_doc['bubble']
                seed_phases(problem, seed)
            if args.pressure_guess is not None:
                problem.P = eq.Free(args.pressure_guess)
            result = eq.solve_equilibrium(model,problem)
            value = payload(model,problem,result)
            meta.update(pressure_guess_Pa=problem.P.guess, result=value)
            if result.success:
                single = f.flash_problem(request,old['loading'],old['temperature_K'],old['pressure_Pa'],
                    [eq.Phase('L',kind='liquid',support=f.s.COMPONENT_IDS)])
                accepted = eq.solve_equilibrium(model,single)
                row = dict(old,final=payload(model,single,accepted),bubble=value,bubble_pressure_Pa=result.pressure,
                    pressure_uncertainty_Pa=result.pressure*max(result.convergence.residual,result.convergence.floor or 0.,result.convergence.criterion.value))
                row['stability'] = [f.stability(model,single,accepted)] if accepted.success else []
                row['classification'] = f.phase_classification(row)
                meta['row'] = row
        elif args.mode == 'trials':
            problem = f.flash_problem(request,old['loading'],old['temperature_K'],old['pressure_Pa'],
                [eq.Phase('L',kind='liquid',support=f.s.COMPONENT_IDS)])
            if args.seed:
                seed = read(args.seed)['final']
                problem.phases[0].composition_guess = seed['mole_fractions'][:9]
                problem.phases[0].packing_guess = seed['packing_fractions'][0]
                problem.phases[0].amount = eq.Free(seed['amounts'][0])
            result = eq.solve_equilibrium(model,problem)
            meta.update(result=payload(model,problem,result),stability=f.stability(model,problem,result))
    write(result_path,meta)
    if 'result' in meta:
        v=meta['result']
        print(args.name,v['success'],v['pressure'],v['convergence'], 'failing rows',v['failing_classified_rows'],flush=True)
    if 'row' in meta:
        row=meta['row']
        print('parent',row.get('classification'),row.get('bubble_pressure_Pa'),len(row.get('stability',[{'trials':[]}])[0]['trials']),flush=True)


if __name__ == '__main__':
    parser=argparse.ArgumentParser()
    parser.add_argument('--worker',action='store_true')
    parser.add_argument('mode',choices=['reference','parent','bubble','trials'])
    parser.add_argument('name')
    parser.add_argument('--temperature',type=float)
    parser.add_argument('--loading',type=float)
    parser.add_argument('--fit',default='A7')
    parser.add_argument('--index',type=int)
    parser.add_argument('--seed')
    parser.add_argument('--pressure-guess',type=float)
    parser.add_argument('--feed-scale',type=float,default=1.)
    args=parser.parse_args()
    if args.worker:
        worker(args)
    else:
        supervise(args)
