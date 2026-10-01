"""Issue 140 Stage 3: registered source representation and existing fit/assessment owners."""
import csv
import importlib.util
import json
import math
import sys
import subprocess
import time
from pathlib import Path
import numpy as np

BASE = Path(__file__).resolve().parent
sys.path[:0] = [str(BASE.parents[1] / 'scripts'), str(BASE.parents[3] / 'src')]
import shared_evaluation as s
s.ENGINE_WHEEL_SHA256 = '9e6a76cf59d4e2fef3347d895bf3a966ecced01f13dc6e0caec74c3c3d618dc4'
s.ENGINE_COMMIT = None  # Wheel hash owns the build identity; its exact source commit is unrecorded.
spec = importlib.util.spec_from_file_location('reaction_constants', BASE / 'reaction-constants.py')
rc = importlib.util.module_from_spec(spec)
spec.loader.exec_module(rc)
fit, assessment, pa, R = rc.fit, rc.assessment, rc.pa, rc.R
OUT = BASE / 'stage-3'
fit.HERE = assessment.HERE = OUT
fit.RAW = assessment.RAW = pa.RAW / 'stage-3'
fit.RAW.mkdir(exist_ok=True)
assessment.calculation = lambda: pa
T0 = 313.15
assessment.STRUCTURES = ('constant-fixed','slope-fixed','slope-free')
assessment.FIXED_ROLES = True


def published(T):
    return math.log(10) * (-356.3094-.06091964*T+21834.37/T+126.8339*np.log10(T)-1684915/T**2)


def source():
    assert not (OUT / 'source-fit.json').exists(), 'one registered representation fit'
    environment = pa.verify(pa.RAW / 'stage-3-wheel-replay/.venv')
    T = 273.15 + 10*np.arange(11)
    X = np.column_stack((np.ones(11), 1/T-1/T0, np.log(T/T0), T-T0))
    scales = np.linalg.norm(X, axis=0)
    theta, _, rank, singular = np.linalg.lstsq(X/scales, published(T), rcond=None)
    L0, B, C, D = theta/scales
    assert rank == 4
    a = L0-B/T0-D*T0
    A = a-C*math.log(T0)
    fit.save(OUT/'source-fit.json',{'status':'checking','source_fit_count':1,'coefficients':{'L0':float(L0),'A_stored':float(A),'a_native':float(a),'B_K':float(B),'C':float(C),'D_per_K':float(D)}})
    mapping = s.with_parameter_values(s.parameter_mapping(BASE/'stage-2/restored-source-parameters.json'),
        {f'reaction:R2:correlation:{k}':float(v) for k,v in zip(('a','b_k','c','d_per_k'),(A,B,C,D))})
    fit.save(OUT/'austgen-source-parameters.json', s.parameter_mapping(BASE/'stage-2/restored-source-parameters.json'))
    mapping['purpose'] = 'Issue 140 Stage 3 PB source R2; common CO2 pool approximation; no loaded fit yet'
    reaction = next(r for r in mapping['reaction_correlations'] if r['reaction_id']=='R2')
    reaction.update(source={'source_id':'PlummerBusenberg1982','locator':'Table 3 p1015; stage-3/source-fit.json'},
        source_sha256='sha256:ad957d246e8daf35e9173a57c723f1e5940dde7bf700bea790df9e530c5a51d6', source_temperature_range_k=[273.15,523.15])
    fit.save(OUT/'restored-source-parameters.json', mapping)
    checks=[]
    for label, path, pressure in [('PB',OUT/'restored-source-parameters.json',101325.),('Austgen',OUT/'austgen-source-parameters.json',None)]:
        values=s.reaction_values(s.parameter_mapping(path))
        native=s._engine_reaction_records(json.loads(fit.TRAINING.read_text())[0]['request'],values)
        for r in native:
            r['engine_correlation'].update(temperature_min=293.15,temperature_max=353.15)
            if r['reaction_id']=='R2': r['engine_reference']['reference_pressure_pa']=pressure
        for t in (293.15,313.15,333.15,353.15):
            c=native[1]['engine_correlation']
            value=c['a']+c['b']/t+c['c']*math.log(t/T0)+c['d']*t
            expected=(L0+B*(1/t-1/T0)+C*math.log(t/T0)+D*(t-T0) if label=='PB' else values['reaction:R2:correlation:a']+values['reaction:R2:correlation:b_k']/t+values['reaction:R2:correlation:c']*math.log(t)+values['reaction:R2:correlation:d_per_k']*t)
            assert abs(value-expected)<5e-13
            if label=='PB': assert abs(R*(-c['b']+c['c']*t+c['d']*t*t)-R*(-B+C*t+D*t*t))<1e-8
            checks.append({'law':label,'temperature_k':t,'native_ln_k':value,'difference':value-expected})
        fit.save(OUT/('native-reaction-inputs.json' if label=='PB' else 'austgen-native-reaction-inputs.json'),native)
    grid=np.arange(293.15,354.15,1.)
    error=L0+B*(1/grid-1/T0)+C*np.log(grid/T0)+D*(grid-T0)-published(grid)
    source_H=R*math.log(10)*(-.06091964*grid**2-21834.37+126.8339*grid/math.log(10)+2*1684915/grid)/1000
    H=R*(-B+C*grid+D*grid**2)/1000
    rows=[{'temperature_k':float(t),'delta_ln_k':float(e),'delta_enthalpy_kj_mol':float(h)} for t,e,h in zip(grid,error,H-source_H)]
    fit.table(OUT/'representation-errors.csv',rows)
    fit.table(OUT/'native-coefficient-checks.csv',checks)
    for name in ('training-targets.csv','assessment-row-ids.json','never-accessed-vle-admission.csv'):
        (OUT/name).write_bytes((BASE/name).read_bytes())
    (OUT/'preregistration.md').write_bytes((BASE/'stage-3-preregistration.md').read_bytes())
    hashes=json.loads((BASE/'input-hashes.json').read_text())
    for path in (OUT/'restored-source-parameters.json',OUT/'austgen-source-parameters.json',Path(fit.__file__)):
        hashes['hashes'][str(path.relative_to(pa.probe.W))]=s.sha256(path)
    fit.save(OUT/'input-hashes.json',hashes)
    passed=bool(max(abs(error))<=.001 and max(abs(H-source_H))<=.10)
    fit.save(OUT/'source-fit.json',{'coefficients':{'L0':float(L0),'A_stored':float(A),'a_native':float(a),'B_K':float(B),'C':float(C),'D_per_K':float(D)},
        'rank':int(rank),'singular_values':singular.tolist(),'maximum_ln_k_error':float(max(abs(error))),
        'maximum_enthalpy_error_kj_mol':float(max(abs(H-source_H))),'passed':passed,'reference_temperature_k':T0,
        'environment':environment,'source_fit_count':1,'temperature_samples_k':T.tolist(),'equal_numerical_weights':True,
        'preregistration_sha256':s.sha256(BASE/'stage-3-preregistration.md'),'producer_sha256':s.sha256(Path(__file__)),
        'source_pdf_sha256':reaction['source_sha256'],'stage_2_source_fit_sha256':s.sha256(BASE/'stage-2/source-fit.json'),
        'source_uncertainty':'representation errors are not chemical measurement uncertainty; Edwards convention assumed',
        'reference_pressure_pa':101325.})
    print('Representation:',passed,'ln K',max(abs(error)),'enthalpy kJ/mol',max(abs(H-source_H)),flush=True)
    assert passed, 'registered source representation failed; no further fit authorized'


def configure(structure, start):
    assert structure in assessment.STRUCTURES and start in ('1','2')
    fit.FREE_REACTIONS = structure=='slope-free'
    fit.SOURCE = OUT/('austgen-source-parameters.json' if fit.FREE_REACTIONS else 'restored-source-parameters.json')
    fit.NATIVE_INPUTS = OUT/('austgen-native-reaction-inputs.json' if fit.FREE_REACTIONS else 'native-reaction-inputs.json')
    if fit.FREE_REACTIONS:
        design=fit.design
        def reaction_design(form, seed):
            ids,bounds,scales,values=design('slope-fixed',seed)
            base=s.reaction_values(s.parameter_mapping(fit.SOURCE))
            A,B=base['reaction:R2:correlation:a'],base['reaction:R2:correlation:b_k']
            return ids+['reaction:R2:correlation:a','reaction:R2:correlation:b_k'], bounds+[(A-8,A+8),(B-20000/R,B+20000/R)], scales+[.1,10], values+[A+(2000/(R*T0) if seed=='2' else 0),B+(-2000/R if seed=='2' else 0)]
        fit.design=reaction_design


def selection():
    assessment.select()
    path=OUT/'freeze.json'
    frozen=json.loads(path.read_text())
    frozen.update(selection='independent-R2 1% constant/slope rule; fixed roles; incomplete structures not ranked',
        wheel_sha256=s.ENGINE_WHEEL_SHA256, source_fit_sha256=s.sha256(OUT/'source-fit.json'),
        readiness_review='Ready at 129f19e; thread mea140-stage3-rereview-1',
        hashes={str(p.relative_to(pa.probe.W)):s.sha256(p) for p in [Path(__file__),BASE/'r2-temperature-run.py',Path(fit.__file__),Path(assessment.__file__),Path(s.__file__),BASE/'stage-3-preregistration.md',OUT/'input-hashes.json',OUT/'source-admission.json',*OUT.glob('*jacobian.csv'),*OUT.glob('*fit.json'),*OUT.glob('*parameters.json'),*OUT.glob('*reaction-inputs.json'),OUT/'representation-errors.csv',OUT/'native-coefficient-checks.csv']})
    fit.save(path,frozen)


def uncertainty(structure,start):
    path=OUT/f'{structure}-start-{start}-fit.json'
    result=json.loads(path.read_text())
    if not result['complete']: return
    ids=result['coordinates']
    rows=list(csv.DictReader((OUT/f'{structure}-start-{start}-jacobian.csv').open()))
    J=np.array([[float(r[f'd/d[{i}]']) for i in ids] for r in rows])
    free=[j for j,i in enumerate(ids) if i not in result['active_bounds']]
    rank=int(np.linalg.matrix_rank(J[:,free]))
    covariance=(2*result['rescore']['cost']/(len(rows)-rank)*np.linalg.inv(J[:,free].T@J[:,free]) if rank==len(free) else None)
    result['conditional_covariance']={'coordinates':[ids[j] for j in free],'matrix':covariance.tolist() if covariance is not None else None,
        'meaning':'local weighted residual covariance; active coordinates held fixed; diagnostic scales, not measurement uncertainty'}
    if fit.FREE_REACTIONS:
        base=s.reaction_values(s.parameter_mapping(fit.SOURCE))
        j=ids.index('reaction:R2:correlation:a')
        da=result['physical'][j]-base[ids[j]]; db=result['physical'][j+1]-base[ids[j+1]]
        result['R2_delta_L0']=da+db/T0
        result['R2_delta_H_kj_mol']=-R*db/1000
        if covariance is not None and j in free and j+1 in free and not result['active_bounds']:
            transform=np.zeros((2,len(free)))
            transform[0,free.index(j)]=1.; transform[0,free.index(j+1)]=1/T0; transform[1,free.index(j+1)]=-R/1000
            result['R2_covariance_L0_H_kj']= (transform@covariance@transform.T).tolist()
            result['R2_ln_k_SE']={str(T):float(np.sqrt(np.array([1.,1/T])@covariance[np.ix_([free.index(j),free.index(j+1)],[free.index(j),free.index(j+1)])]@np.array([1.,1/T]))) for T in (293.15,313.15,333.15,353.15,393.15)}
        else: result['R2_covariance_L0_H_kj']=None
        correlations=np.array(result['jacobian_column_correlations'])
        result['R2_identified']=bool(not result['active_bounds'] and rank==len(ids) and abs(correlations[j,ids.index(fit.SLOPE)])<.95 and abs(correlations[j+1,ids.index(fit.SLOPE)])<.95)
    fit.save(path,result)


if __name__ == '__main__':
    args=sys.argv[1:]
    if args==['source']: source()
    else:
        admission=json.loads((OUT/'source-admission.json').read_text())
        assert admission['passed'] and admission['source_fit_sha256']==s.sha256(OUT/'source-fit.json') and admission['preregistration_sha256']==s.sha256(OUT/'preregistration.md')
        pa.verify(pa.RAW/'stage-3-wheel-replay/.venv')
        original=s._engine_reaction_records
        def records(request, values):
            native=original(request,values)
            if values['reaction:R2:correlation:c']==json.loads((OUT/'source-fit.json').read_text())['coefficients']['C']:
                native[1]['engine_reference']['reference_pressure_pa']=101325.
            return native
        s._engine_reaction_records=records
        if args[0] in ('fit','rescore'):
            configure(*args[1:]); getattr(fit,args[0])(*args[1:])
            if args[0]=='rescore': uncertainty(*args[1:])
        elif args==['select']: selection()
        elif args[0] in ('stage','heat'):
            assert subprocess.check_output(['git','show','HEAD:'+str((OUT/'freeze.json').relative_to(pa.probe.W))])==(OUT/'freeze.json').read_bytes(), 'commit freeze before assessment'
            if args[0]=='stage':
                assert int(args[1]) in range(1,6)
                assessment.stage(int(args[1]))
            else:
                frozen=json.loads((OUT/'freeze.json').read_text())
                assert (OUT/'assessment-stage-5.json').exists() and not (OUT/'heat-comparison.json').exists()
                assessment.heat_comparison(pa,frozen,time.perf_counter()+1780,adopted_baseline=BASE)
        else: raise SystemExit('source | fit/rescore STRUCTURE START | select | stage 1..5 | heat')
