"""Issue 172: frozen same-wheel replay and 24 sequential measured-route fits."""
import concurrent.futures as cf
import csv
import json
import math
import multiprocessing
import os
from pathlib import Path
import subprocess
import sys
import time

from reduce_dielectric import OUT, ROOT, SHA, declaration, write

for key in ('OMP_NUM_THREADS', 'OPENBLAS_NUM_THREADS', 'MKL_NUM_THREADS'):
    os.environ[key] = '1'
problem = sys.argv[3] if sys.argv[1:2] == ['fit'] else 'F1'
os.environ.update(FINAL_RERUN='1', FINAL_POOL=str(int(problem in ('F4','F5'))),
    SENSITIVITY_OUTPUT=str(OUT/'scratch'))
sys.path[:0] = [str(ROOT/'analyses/mea_parameter_bundle/scripts'),
    str(ROOT/'analyses/mea_parameter_bundle/calibration-misfit'), str(ROOT/'src')]
import shared_evaluation as s
s.ENGINE_WHEEL_SHA256, s.ENGINE_COMMIT = SHA, '81d1e38a'
import probe
import heat_160 as h
import numpy as np
s.ENGINE_WHEEL_SHA256, s.ENGINE_COMMIT = SHA, '81d1e38a'
s.verify_wheel()
REFERENCE = OUT.parent/'heat-final-170'
WORKERS = os.cpu_count()
assert WORKERS == 32
TASKS = []


def rows(mapping, arcis=False):
    params, groups, reactive = h.d.rows_for(mapping,'11')
    sources = h.VINJARAPU + (h.ARCIS if arcis else [])
    heat = [(r['record_id'], item, 1.) for r,item in
        zip(sources,h.heat_items(mapping,params,sources),strict=True)]
    return params, reactive+heat


def prediction(index):
    mapping, (identity,item,weight) = TASKS[index]
    model = h.epcsaft.Mixture(h.epcsaft.Parameters.from_mapping(mapping),thermochemistry=h.thermal.record())
    value = h.reg.predict(model,item)
    row = dict(target=identity,observed=item.observed,scale=item.scale,weight=weight,form=item.form.name,
        status=value.status.name,message=value.message,requested_tolerance_met=value.requested_tolerance_met,
        stable_root_count=value.stable_root_count,branch=None if value.branch is None else value.branch.name,
        convergence=None if value.convergence is None else {k:s._jsonable(getattr(value.convergence,k))
            for k in ('residual','floor','amplification','contraction','iterations','stop')})
    if value.status.name == 'Available':
        residual = math.sqrt(weight)*(math.log(value.value/item.observed) if item.form == h.reg.ResidualForm.LogRatio
            else (value.value-item.observed)/item.scale)
        row.update(predicted=value.value,weighted_residual=residual,cost=.5*residual**2)
    return row


def evaluate(mapping,directory):
    directory.mkdir(exist_ok=True)
    _,items = rows(mapping,True)
    TASKS[:] = [(mapping,item) for item in items]
    with cf.ProcessPoolExecutor(WORKERS,mp_context=multiprocessing.get_context('fork')) as pool:
        values = list(pool.map(prediction,range(len(items))))
    write(directory/'replay.json',values)
    table(directory/'replay.csv',values)
    assert all(r['status']=='Available' and math.isfinite(r['predicted']) for r in values), 'Unavailable target'
    common = [r for r in values if r['target'] not in {x['record_id'] for x in h.ARCIS}]
    common_ids = set(json.loads((REFERENCE/'F1-A/native-fit.json').read_text())['targets'])
    reactive = [r for r in common if r['target'] in common_ids and r['target'] not in {x['record_id'] for x in h.VINJARAPU}]
    score = dict(cost=math.fsum(r['cost'] for r in common),common149_cost=math.fsum(r['cost'] for r in common if r['target'] in common_ids),
        scores=h.score([(r['target'],item,w) for (_,item,w),r in zip(items,values,strict=True) if r in reactive],
            [r['predicted'] for r in reactive],[r['weighted_residual'] for r in reactive]))
    for name,source in (('Vinjarapu',h.VINJARAPU),('Arcis',h.ARCIS)):
        selected = [r for r in values if r['target'] in {x['record_id'] for x in source}]
        score[name+'_RMSE_kJ_mol'] = math.sqrt(math.fsum(((r['predicted']-r['observed'])/1000)**2 for r in selected)/len(selected))
    write(directory/'summary.json',score)
    return common,score


def table(path,values):
    with path.open('w',newline='') as stream:
        writer = csv.DictWriter(stream,list(dict.fromkeys(k for r in values for k in r)),lineterminator='\n')
        writer.writeheader(); writer.writerows(values)


def baseline():
    values,score = evaluate(s.parameter_mapping(),OUT/'baseline')
    expected = json.loads((REFERENCE/'F1-A/native-fit.json').read_text())
    screen = json.loads((OUT/'inputs/screen-baseline-summary.json').read_text())
    assert [r['target'] for r in values] == expected['targets']
    assert [r['observed'] for r in values] == expected['observed']
    comparison = dict(relative_cost=abs(score['cost']/expected['final_cost']-1),
        max_abs_weighted_residual=max(abs(r['weighted_residual']-v) for r,v in zip(values,expected['weighted_residuals'],strict=True)),
        AARD_deltas={k:score['scores'][k]['AARD_percent']-screen[k]['AARD_percent'] for k in ('pressure','species')},
        heat_RMSE_deltas={k:score[k+'_RMSE_kJ_mol']-screen[k]['RMSE_kJ_mol'] for k in ('Vinjarapu','Arcis')})
    write(OUT/'baseline/comparison.json',comparison)
    assert comparison['relative_cost'] <= 1e-6 and comparison['max_abs_weighted_residual'] <= 1e-5
    assert all(abs(v)<=1e-4 for v in [*comparison['AARD_deltas'].values(),*comparison['heat_RMSE_deltas'].values()])
    print('BASELINE',score,comparison,flush=True)


def fit(branch,problem,letter):
    directory = OUT/branch/f'{problem}-{letter}'
    seed = json.loads((REFERENCE/f'{problem}-{letter}/start-parameters.json').read_text())
    reference = json.loads((REFERENCE/f'{problem}-{letter}/native-fit.json').read_text())
    pair = json.loads((OUT/'dielectric/reduction.json').read_text())['branches'][branch=='larger-dV']
    mapping = declaration(seed,pair)
    if problem == 'F3':
        family = next(f for f in mapping['model_families'] if f['kind']=='electrolyte')
        family['choice'] = 'fully-dissociated-debye-huckel'
        for key in ('c_shell','c_dielectric'): family.pop(key,None)
        for c in mapping['components']:
            c['coefficients'] = [r for r in c['coefficients'] if r['family'] not in ('solvation_factor','born_diameter')]
        mapping['model_coefficients'] = [r for r in mapping['model_coefficients'] if r['family']!='ionic_region_relative_permittivity']
    ids = list(h.IDS)
    scales,lower,upper = list(h.SCALES),list(h.d.LOWER),list(h.d.UPPER)
    if problem != 'F3':
        diameters = [f'component/{ion}/born_diameter' for ion in h.d1.m.IONS]
        mapping = s.with_parameter_values(mapping,dict(zip(diameters,(3.53322927146,3.54107030822) if letter=='A' else (4.,3.))))
        ids += diameters; scales += [.1,.1]; lower += [2.,2.]; upper += [5.,5.]
    params,items = rows(mapping)
    assert [r[0] for r in items]==reference['targets'] and [r[1].observed for r in items]==reference['observed']
    v = s.parameter_values(mapping)
    assert {i:v[i] for i in h.IDS}==reference['start']
    coords = [h.reg.coordinate(params,[(('born_diameter' if i.startswith('component/') else
        'k_ij_reciprocal_temperature_slope' if i==h.IDS[-1] else 'k_ij'),
        i.split('/')[1] if i.startswith('component/') else tuple(i.split('/')[1:3]),1.)],
        origin=v[i],scale=scale,bounds=(lo,hi)) for i,scale,lo,hi in zip(ids,scales,lower,upper,strict=True)]
    write(directory/'start-parameters.json',mapping)
    write(directory/'targets.json',[dict(target=i,observed=item.observed,scale=item.scale,weight=w,form=item.form.name) for i,item,w in items])
    clock = time.monotonic()
    fitted = h.reg.fit(params,coords,[r[1] for r in items],weights=[r[2] for r in items],
        controls=h.reg.FitControls(maximum_iterations=40,maximum_elapsed_time_seconds=2250.,workers=WORKERS),thermochemistry=h.thermal.record())
    raw = h.d1.m.fit_summary(fitted,time.monotonic()-clock)
    raw.update({k:s._jsonable(getattr(fitted,k)) for k in ('physical_jacobian','residuals','residual_evaluations','jacobian_evaluations')})
    raw.update(coordinates=ids,scales=scales,lower=lower,upper=upper,start={i:v[i] for i in ids},
        targets=[r[0] for r in items],observed=[r[1].observed for r in items],workers=WORKERS,
        covariance={k:s._jsonable(getattr(fitted.covariance,k)) for k in ('status','assumption','rank','singular_values','physical','variance_factor','active_bounds')},
        failures=[dict(trial=f.trial,observation=f.observation,status=f.status.name,message=f.message,jacobian=f.jacobian) for f in fitted.failures])
    write(directory/'native-fit.json',raw)
    print('FIT',branch,problem,letter,raw['status'],raw['final_cost'],raw['wall_s'],flush=True)
    h.d1.m.complete(fitted)
    final = s.with_parameter_values(mapping,dict(zip(ids,fitted.physical,strict=True)))
    assert s.reaction_values(final)==s.reaction_values(mapping)
    final['purpose'] = 'Issue 172 measured-route comparison; not adopted or physically validated.'
    write(directory/'parameters.json',final)


def campaign():
    assert json.loads((OUT/'classifier-check.json').read_text())['classification']=='unresolved'
    runs = []
    for branch in ('smaller-dV','larger-dV'):
        for problem in (f'F{i}' for i in range(1,7)):
            for letter in ('A','B'):
                directory = OUT/branch/f'{problem}-{letter}'
                directory.mkdir(exist_ok=False)
                command = [sys.executable,str(Path(__file__).resolve()),'fit',branch,problem,letter]
                print('START',branch,problem,letter,flush=True)
                clock = time.monotonic()
                with (directory/'execution.log').open('w') as log:
                    code = subprocess.run(command,cwd=ROOT,stdout=log,stderr=subprocess.STDOUT).returncode
                runs.append(dict(branch=branch,problem=problem,start=letter,command=command,returncode=code,wall_s=time.monotonic()-clock))
                write(OUT/'execution.json',runs)
                print('COMPLETE' if code==0 else 'FAILED',runs[-1],flush=True)
                if code: print((directory/'execution.log').read_text()[-3000:],flush=True)


if __name__=='__main__':
    if sys.argv[1]=='baseline': baseline()
    elif sys.argv[1]=='fit': fit(*sys.argv[2:])
    elif sys.argv[1]=='evaluate': evaluate(json.loads(Path(sys.argv[2]).read_text()),Path(sys.argv[3]))
    else: campaign()
