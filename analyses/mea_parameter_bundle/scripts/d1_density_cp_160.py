"""Issue 160 owner revision: five-coordinate D1 fits and density-only translation.

Reuses p5conv's pinned Engine fit, final_evidence's assessment masks and #151
attribution. The empirical correction is fitted algebraically, never in a solve.
"""
import concurrent.futures as cf
import csv
import json
import math
import os
from pathlib import Path
import signal
import subprocess
import sys
import time

import numpy as np
from scipy.optimize import least_squares

sys.path.insert(0, str(Path(__file__).resolve().parent))
import density_cp_160 as m
from density_cp_160 import s, regression

ROOT = m.ROOT
BUNDLE = m.BUNDLE
ORIGINAL = m.OUT
OUT = ORIGINAL / 'D1-evidence'
IDS = json.loads((ORIGINAL / 'F1-A/native-fit.json').read_text())['coordinates'][:5]
SCALES = [.01, .01, .01, .01, 10.]


def load(path):
    return json.loads(Path(path).read_text())


def base():
    mapping = load(ORIGINAL / 'new-water-binaries-parameters.json')
    assert all(s.parameter_values(mapping)[f'component/{ion}/segment_count'] == 1. for ion in m.IONS)
    return mapping


def materialize(raw, mapping, path):
    assert len(raw['physical']) == 5
    mapping = s.with_parameter_values(mapping, dict(zip(IDS, raw['physical'], strict=True)))
    s.write_json(path, mapping)
    return mapping


def complete(raw):
    return (raw['status'] == 'converged' and len(raw['physical']) == 5
            and len(raw['predictions']) == len(raw['observed']) == len(raw['targets'])
            and raw.get('usable', True)
            and all(v == 'Available' for v in raw['observation_statuses'])
            and all(np.isfinite(np.asarray(raw[k], float)).all()
                    for k in ('physical', 'predictions', 'weighted_residuals', 'final_cost')))


def fit_worker(problem, letter):
    directory = OUT / f'{problem}-{letter}'
    os.environ['SENSITIVITY_OUTPUT'] = str(directory)
    os.environ['FINAL_NAME'] = f'{problem}-{letter}'
    os.environ['FINAL_RERUN'] = '1'
    os.environ['SENSITIVITY_CASE'] = f'{problem}-{letter}'
    os.environ['FINAL_POOL'] = str(int(problem in ('F4', 'F5')))
    p5 = m.module('p5d1', BUNDLE / 'model-d/born-form-diagnosis/p5conv-fit.py')
    d = p5.d
    mapping = base()
    original = BUNDLE/'model-d/born-form-diagnosis/p5conv-a-00-diagnostic-parameters.json'
    off = BUNDLE/'model-d/sensitivity-current/ablation-off-11-diagnostic-parameters.json'
    # Exact #154 problems and start pairs, on new water/refit binaries.
    if problem == 'F6':
        low = m.module('lowd1', ORIGINAL.parent / 'temperature-reanchor-140/low-temperature-fit.py')
        source, _, _ = low.source_context()
        adopted = s.parameter_values(mapping)
        mapping = m.new_water(source)
        mapping = s.with_parameter_values(mapping, {i: adopted[i] for i in
            ('pair/monoethanolamine/water/k_ij', 'pair/carbon-dioxide/water/k_ij')})
        ids, _, _, values = low.design('slope-fixed', '1' if letter == 'A' else '2')
        assert ids == IDS
        mapping = s.with_parameter_values(mapping, dict(zip(ids,values,strict=True)))
    else:
        paths = {'F1':(m.F1,original), 'F2':(original,m.F1), 'F3':(off,m.F1),
                 'F4':(m.F1,original), 'F5':(original,m.F1)}
        seed = s.parameter_values(s.parameter_mapping(paths[problem][letter=='B']))
        if problem in ('F2','F5'):
            adopted = s.parameter_values(mapping)
            mapping = m.new_water(s.parameter_mapping(original))
            mapping = s.with_parameter_values(mapping, {i: adopted[i] for i in
                ('pair/monoethanolamine/water/k_ij','pair/carbon-dioxide/water/k_ij')})
        mapping = s.with_parameter_values(mapping, {i: seed[i] for i in IDS})
    path = directory / 'start-parameters.json'
    s.write_json(path, mapping)
    form = '00' if problem in ('F2','F5') else '11'
    d.FILES[form] = path
    os.environ['SENSITIVITY_MAPPING'] = str(path)
    os.environ['FINAL_START'] = letter
    os.environ['FINAL_F1'] = str(OUT / 'F1-A/parameters.json')
    p5.main('off' if problem == 'F3' else 'refit', form)
    raw_path = directory / 'runs' / f'{problem}-{letter}' / f'{problem}-{letter}-fit.json'
    raw = load(raw_path)
    raw['observed'] = [r[1].observed for r in d.rows_for(mapping,'11')[2]]
    assert raw['coordinates'] == IDS and complete(raw), f'{problem}-{letter}: incomplete fit'
    assert all(s.parameter_values(s.parameter_mapping(directory / f'{problem}-{letter}-diagnostic-parameters.json'))[f'component/{ion}/segment_count'] == 1. for ion in m.IONS)
    s.write_json(directory / 'native-fit.json', raw)
    s.write_json(directory / 'parameters.json', load(directory / f'{problem}-{letter}-diagnostic-parameters.json'))


def launch_fit(problem, letter):
    directory = OUT / f'{problem}-{letter}'
    directory.mkdir(parents=True, exist_ok=True)
    t0 = time.monotonic()
    timed_out = False
    with (directory / 'execution.log').open('w') as log:
        child = subprocess.Popen([sys.executable, str(Path(__file__).resolve()), 'fit', problem, letter],
                                 cwd=ROOT, stdout=log, stderr=subprocess.STDOUT, start_new_session=True)
        pid_path = directory / 'child.pid'
        pid_path.write_text(str(child.pid))
        try:
            code = child.wait(timeout=900.)
        except subprocess.TimeoutExpired:
            timed_out = True
            os.killpg(child.pid, signal.SIGKILL)
            code = child.wait()
        finally:
            pid_path.unlink(missing_ok=True)
    execution = dict(problem=problem, start=letter, wall_s=time.monotonic()-t0,
                     watchdog_s=900., watchdog_triggered=timed_out, returncode=code)
    s.write_json(directory / 'execution.json', execution)
    print('FIT', execution, flush=True)
    assert code == 0 and not timed_out, f'{problem}-{letter}: watchdog or incomplete fit; see execution.log'
    return execution


def cancel_children():
    for path in OUT.glob('*/child.pid'):
        try:
            os.killpg(int(path.read_text()), signal.SIGKILL)
        except ProcessLookupError:
            pass


def select(problem):
    aa, bb = (load(OUT / f'{problem}-{letter}/native-fit.json') for letter in ('A', 'B'))
    assert complete(aa) and complete(bb)
    relative = abs(aa['final_cost']-bb['final_cost']) / max(abs(aa['final_cost']), abs(bb['final_cost']), 1e-300)
    letter = 'A' if aa['final_cost'] <= bb['final_cost'] else 'B'
    return dict(problem=problem, start=letter, relative_start_cost_difference=relative,
                starts_agree=relative <= 1e-6, cost_A=aa['final_cost'], cost_B=bb['final_cost'],
                parameters=str(OUT / f'{problem}-{letter}/parameters.json'),
                fit=str(OUT / f'{problem}-{letter}/native-fit.json'))


def density_job(mapping, source):
    T = float(source['temperature_C']) + 273.15
    alpha = float(source['co2_loading_mol_per_mol_mea'])
    w = float(source['mea_mass_fraction'])
    request = m.request(mapping, T, alpha, density=True)
    coordinates = dict(source_key='Amundsen2009', MEA_weight_fraction=w, CO2_loading=alpha,
                       temperature_reported_C=T-273.15)
    request = s.source_feed_request(request, coordinates)
    request = s.corrected_request(request, s.reaction_values(mapping))
    model = m.epcsaft.Mixture(m.epcsaft.Parameters.from_mapping(mapping))
    problem = s._problem_from_request(request)
    result = m.eq.solve_equilibrium(model, problem)
    assert result.success, result.message
    record = s._snapshot_from_result(model, problem, request, result)
    assert record['status']=='evaluated', record['failure_code']
    phase = record['phases'][0]
    x = np.array(phase['mole_fractions'])
    masses = np.array(request['reaction_system']['molar_masses_kg_per_mol'])
    mass = float(x @ masses)
    v = 1. / phase['molar_density_mol_m3']
    ion_x = float(x[s.COMPONENT_IDS.index(m.IONS[0])] + x[s.COMPONENT_IDS.index(m.IONS[1])])
    return dict(temperature_K=T, loading=alpha, mea_mass_fraction=w, observed_kg_m3=1000*float(source['value']),
                eos_molar_volume_m3_mol=v, mixture_molar_mass_kg_mol=mass, ion_mole_fraction_sum=ion_x,
                eos_density_kg_m3=mass/v, mole_fractions=x.tolist(), solved_state=record,
                source_locator=source['source_locator'], uncertainty_scope=source['uncertainty_scope'])


def correction(rows):
    v, x, mass, observed = (np.array([r[k] for r in rows]) for k in
                            ('eos_molar_volume_m3_mol', 'ion_mole_fraction_sum', 'mixture_molar_mass_kg_mol', 'observed_kg_m3'))
    def residual(value):
        return np.log(mass / (v + value[0]*1e-6*x) / observed)
    fitted = least_squares(residual, [0.], ftol=1e-12, xtol=1e-12, gtol=1e-12)
    assert fitted.success and np.isfinite(fitted.x).all() and np.isfinite(fitted.fun).all()
    c = float(fitted.x[0])
    return dict(c_cm3_mol=c, log_ratio_sum_of_squares=float(fitted.fun @ fitted.fun),
                optimizer_message=fitted.message, equilibrium_solves_during_c_fit=0,
                pressure_Pa=100000., Pc_over_RT_at_1bar={str(T):100000*c*1e-6/(8.31446261815324*T)
                    for T in (298.15, 318.15, 323.15, 343.15, 353.15)})


def corrected(rows, c):
    result = []
    for r in rows:
        v = r['eos_molar_volume_m3_mol'] + c*1e-6*r['ion_mole_fraction_sum']
        assert v > 0
        rho = r['mixture_molar_mass_kg_mol']/v
        result.append({k:v for k,v in r.items() if k not in ('solved_state', 'mole_fractions')} |
                      dict(corrected_density_kg_m3=rho, corrected_deviation_percent=100*(rho/r['observed_kg_m3']-1),
                           eos_deviation_percent=100*(r['eos_density_kg_m3']/r['observed_kg_m3']-1)))
    return result


def evaluation_job(args):
    import final_evidence as ef
    ef.OUT = OUT
    ef.EVAL = OUT / 'evaluation'
    return ef.job(*args)[0]


def table(path, rows):
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open('w', newline='') as output:
        writer = csv.DictWriter(output, list(dict.fromkeys(k for r in rows for k in r)), lineterminator='\n')
        writer.writeheader()
        writer.writerows(rows)


def evidence(choices, pool):
    import final_evidence as ef
    ef.OUT = OUT
    ef.EVAL = OUT / 'evaluation'
    ef.EVAL.mkdir(parents=True, exist_ok=True)
    selected = {p:dict(record=v['parameters'], raw=v['fit']) for p,v in choices.items()}
    ef.selected = lambda: selected
    packet, groups = ef.observations()
    jobs, excluded = [], []
    for problem, item in selected.items():
        ef.binding(problem,item['record'])
        mask = set(load(item['raw'])['targets'])
        use = groups if problem in ('F1','F2','F6') else {'packet':[{**o,'targets':[t for t in o['targets'] if t['identity'] in mask]}
            for o in packet if any(t['identity'] in mask for t in o['targets'])]}
        s.write_json(ef.EVAL/f'{problem}-mask.json', {k:[o['identity'] for o in vv] for k,vv in use.items()})
        for kind, observations in use.items():
            for o in observations:
                T = o['request']['temperature']['value']
                outside_domain = ef.probe.reaction_domain_status(o) if problem!='F6' else None
                if outside_domain or not 293.15<=T<=393.15:
                    excluded.append(dict(problem=problem,kind=kind,identity=o['identity'],temperature_K=T,reason='outside declared reaction domain'))
                else:
                    jobs.append((problem,item['record'],kind,o))
    futures = [pool.submit(evaluation_job, job) for job in jobs]
    records = [f.result() for f in cf.as_completed(futures)]
    records.sort(key=lambda r:(r['problem'], r['kind'], r['identity']))
    with (ef.EVAL/'states.jsonl').open('w') as output:
        for r in records:
            output.write(json.dumps(s._jsonable(r))+'\n')
    ef.summarize(records, [], selected, excluded)
    # Existing conditional covariance calculation; active bounds excluded.
    import refit
    from types import SimpleNamespace
    covariance = []
    for problem, choice in choices.items():
        raw = load(choice['fit'])
        W = np.array(raw['optimizer_jacobian']).reshape(len(raw['targets']),5)
        physical_J = W / np.array(SCALES)
        active = [IDS.index(v) if isinstance(v,str) else v for v in raw['active_bounds']]
        result = SimpleNamespace(physical=raw['physical'],covariance=SimpleNamespace(active_bounds=active))
        conditional = refit.identifiability(result,physical_J,np.array(raw['weighted_residuals']),IDS,[-.5,-.5,-.5,-1.,-1000.],[.5,.5,.5,1.,1000.])
        covariance.append(dict(problem=problem, record_sha256=s.sha256(Path(choice['parameters'])),
                               coordinates=IDS, scope='conditional on fixed chemistry, water, binaries, Born inputs and residual weights; active bounds excluded',
                               uncertainty=conditional))
    s.write_json(OUT/'conditional-uncertainty.json', covariance)
    for name, keep in (
        ('pressure-figure-data.csv', lambda r:r['kind']=='packet' and r['quantity']=='pressure' and r['problem'] in ('F1','F2','F6')),
        ('species-figure-data.csv', lambda r:r['kind']=='packet' and r['quantity']=='species' and r['problem'] in ('F1','F2','F6')),
        ('pool-figure-data.csv', lambda r:r['kind']=='packet' and r['problem'] in ('F1','F2','F4','F5'))):
        rows = [r for r in csv.DictReader((ef.EVAL/'targets.csv').open()) if keep(r)]
        ef.table(OUT/name, rows)
    return ef


def decomposition(choices):
    directory = OUT/'activity-contributions'
    directory.mkdir(parents=True, exist_ok=True)
    (directory/'runs').mkdir(exist_ok=True)
    reference = load(BUNDLE/'results/final-rerun/activity-contributions/inputs.json')
    born_reference_path = BUNDLE/'model-d/activity-contributions/inputs.json'
    born_reference = load(born_reference_path)['N6_by_record_sha256']
    inputs = {k:reference[k] for k in ('c2_reference_temperature_K','cohorts','state_count','state_ids','target_count','target_ids')}
    inputs.update(status='Issue 160 D1 model: new water, refit binaries, original ion sizes, corrected141',
                  packet=str(BUNDLE/'results/source-corrections-152/state-packet.json.gz'), sha256={},
                  N1_expected_costs={k:load(choices[p]['fit'])['final_cost'] for k,p in (('adopted','F1'),('off-refit','F3'))},
                  N6_by_record_sha256={}, records={}, states={}, evaluation_paths={})
    records = [json.loads(line) for line in (OUT/'evaluation/states.jsonl').open()]
    arguments = []
    for name, problem in (('adopted','F1'),('original','F2'),('off-refit','F3')):
        path = Path(choices[problem]['parameters'])
        inputs['records'][name] = str(path.resolve())
        state_path = directory/'runs'/f'{name}-states.jsonl'
        with state_path.open('w') as output:
            for r in records:
                if r['problem']==problem and r['kind']=='packet' and r['identity'] in inputs['state_ids']:
                    output.write(json.dumps(r)+'\n')
        inputs['states'][name] = str(state_path)
        replay = OUT/'evaluation'/f'{problem}-replay.json'
        inputs['evaluation_paths'][name] = str(replay)
        if problem != 'F3':
            reference_hash = ('9055458d8b7cd767a0d08e9f37e4fd28631e29c363364d7b842ebade645cb241'
                              if problem=='F1' else 'ebb5f8f9df2aa4ff9bbaec72899dae33fba2233823bb7e389bef92b3d2981900')
            inputs['N6_by_record_sha256'][s.sha256(path)] = born_reference[reference_hash]
        arguments += [name,str(path)]
    inputs['N6_reference_provenance'] = dict(path=str(born_reference_path),sha256=s.sha256(born_reference_path),
        rationale='Separate retained salt-free SSM+DS and original-Born references; Born inputs unchanged. Not fitted to current output.')
    for path in [Path(inputs['packet']), *map(Path, inputs['records'].values()), *map(Path, inputs['states'].values()), *map(Path, inputs['evaluation_paths'].values())]:
        inputs['sha256'][str(path)] = s.sha256(path)
    config = directory/'inputs.json'
    s.write_json(config, inputs)
    env = dict(os.environ, ACTIVITY_OUTPUT=str(directory), ACTIVITY_INPUTS=str(config))
    with (directory/'execution.log').open('w') as log:
        subprocess.run([sys.executable,str(BUNDLE/'model-d/activity-contributions/activity_contributions.py'),'calculate',*arguments],
                       cwd=ROOT, env=env, stdout=log, stderr=subprocess.STDOUT, check=True)


def campaign():
    OUT.mkdir(parents=True, exist_ok=True)
    started = time.monotonic()
    s.verify_wheel()
    raw_a = load(ORIGINAL/'D1/native-fit.json')
    assert complete(raw_a)
    raw_a.update(coordinates=IDS, scales=SCALES, reused_from=str(ORIGINAL/'D1/native-fit.json'))
    s.write_json(OUT/'F1-A/native-fit.json', raw_a)
    materialize(raw_a, base(), OUT/'F1-A/parameters.json')
    s.write_json(OUT/'F1-A/execution.json', dict(reused=True, original_native_fit_wall_s=raw_a['wall_s'], new_fit_wall_s=0))
    state = dict(base_commit='16d2115', wheel_sha256='28181e72e429c6e87fc6361082af1a7b21c8747e76bda65a1c30abb4a97402f2',
                 ion_segment_count=1., coordinate_count=5, density_targets_in_engine_fit=0,
                 pool_workers=len(os.sched_getaffinity(0)), starts={})
    pool = cf.ProcessPoolExecutor(max_workers=state['pool_workers'])
    try:
        state['starts']['F1-B'] = pool.submit(launch_fit, 'F1', 'B').result()
        main = select('F1')
        state['main'] = main
        preservation_limit = 1.10 * load(ORIGINAL / 'acceptance.json')['F1_cost141']
        assert min(main['cost_A'], main['cost_B']) <= preservation_limit, 'main cost acceptance failed'
        if not main['starts_agree']:
            print('Starts differ; #154 rule reports both and uses lower complete cost.', flush=True)
        mapping = s.parameter_mapping(Path(main['parameters']))
        sources = [r for r in csv.DictReader((ROOT/'data/reference/MEA/observations/density_viscosity/Amundsen_2009_density_viscosity.csv').open())
                   if r['property']=='density' and r['co2_loading_mol_per_mol_mea']]
        def target(r):
            return float(r['mea_mass_fraction']) == .3 and float(r['temperature_C']) in (50.,70.) and float(r['co2_loading_mol_per_mol_mea']) in (.3,.4)
        targets = [r for r in sources if target(r)]
        assert len(targets)==4
        target_states = [f.result() for f in [pool.submit(density_job, mapping, r) for r in targets]]
        s.write_json(OUT/'target-density-states.json', target_states)
        volume = correction(target_states)
        target_rows = corrected(target_states, volume['c_cm3_mol'])
        table(OUT/'corrected-target-densities.csv', target_rows)
        s.write_json(OUT/'volume-correction.json', volume)
        state['volume_correction'] = volume
        state['density_acceptance_passed'] = all(abs(r['corrected_deviation_percent']) <= 1.6 for r in target_rows)
        water = load(ORIGINAL/'stage2.json')['water']
        state['pure_water_Cp_acceptance_passed'] = all(abs(r['cp_deviation_percent'])<=3 for r in water)
        assert state['density_acceptance_passed'], 'corrected density acceptance failed'
        assert state['pure_water_Cp_acceptance_passed'], 'pure-water Cp acceptance failed'
        candidate = dict(mapping)
        candidate['document_id'] = 'mea-issue160-f1-double-prime-unpromoted-candidate'
        candidate['purpose'] = 'Calibrated D1 chemistry with empirical density-only volume translation; not promoted; no absorber validation.'
        candidate['empirical_density_correction'] = dict(volume, kind='density-only-volume-translation',
            component_ids=list(m.IONS), formula='rho_corr = M_mix / (v_EOS + 1e-6*c_cm3_mol*(x_MEAH+ + x_MEACOO-))',
            fitting_targets=str(OUT/'corrected-target-densities.csv'), applied_to_chemical_potentials=False,
            applied_to_enthalpy_or_heat_capacity=False, equilibrium_unchanged=True)
        s.write_json(OUT/'F1-double-prime-candidate-parameters.json', candidate)
        # Submit all ten remaining fit starts together. F1-A was retained;
        # F1-B above completes the twelve-run minimal set, without re-fitting A.
        fit_futures = {pool.submit(launch_fit,p,l):f'{p}-{l}' for p in ('F2','F3','F4','F5','F6') for l in ('A','B')}
        print('STAGE4 submitted',len(fit_futures),'fits; pool',state['pool_workers'],flush=True)
        for f in cf.as_completed(fit_futures):
            state['starts'][fit_futures[f]] = f.result()
            s.write_json(OUT/'campaign-execution.json',state)
        choices = {p:select(p) for p in ('F1','F2','F3','F4','F5','F6')}
        state['choices'] = choices
        s.write_json(OUT/'fit-summary.json',list(choices.values()))
        ef = evidence(choices, pool)
        outside = [r for r in sources if not target(r)]
        states = [f.result() for f in [pool.submit(density_job,mapping,r) for r in outside]]
        s.write_json(OUT/'outside-density-states.json',states)
        ef.table(OUT/'corrected-outside-densities.csv', corrected(states,volume['c_cm3_mol']))
        heats = [f.result() for f in [pool.submit(m.cp_check,mapping,T,a,cp) for T,a,cp in m.HILLIARD]]
        s.write_json(OUT/'heat-capacity-checks.json',dict(solution=heats,water=water,water_reference=str(ORIGINAL/'stage2.json'),
            density_translation_applied_to_enthalpy=False))
        pool.shutdown()
        decomposition(choices)
        state['status']='completed; unpromoted'
    except BaseException as error:
        cancel_children()
        pool.shutdown(wait=True, cancel_futures=True)
        state.update(status='stopped', failure=f'{type(error).__name__}: {error}')
        raise
    finally:
        state['wall_s']=time.monotonic()-started
        s.write_json(OUT/'campaign-execution.json',state)
        print('CAMPAIGN',state['status'],state['wall_s'],'s',flush=True)


if __name__ == '__main__':
    if sys.argv[1]=='fit':
        fit_worker(sys.argv[2],sys.argv[3])
    elif sys.argv[1]=='decomposition':
        started = time.monotonic()
        state = load(OUT/'campaign-execution.json')
        state['initial_postprocessing_failure'] = state.get('failure')
        decomposition(state['choices'])
        state.pop('failure',None)
        state.update(status='completed; unpromoted',decomposition_resume_wall_s=time.monotonic()-started)
        state['total_execution_wall_s'] = state['wall_s'] + state['decomposition_resume_wall_s']
        s.write_json(OUT/'campaign-execution.json',state)
        print('Decomposition complete; no fit rerun.',flush=True)
    else:
        campaign()
