"""Issue 264: source-defined Cp comparison, decomposition and bounded calibration probes."""
import copy, csv, hashlib, json, math, os, sys, time, zipfile
from pathlib import Path
import numpy as np
import epcsaft
from epcsaft import equilibrium as eq, regression as reg
from epcsaft.parameters import document_mapping
from MEA.solvent_specification import SolventSpecification, jsonable

OUT = Path(__file__).resolve().parent
ROOT = OUT.parents[2]
AN = ROOT / 'analyses/solvent_specification_mea'
SHA = '83ede7d2722d3581603f6e4139c614b8bbfc903ce90609c90b802d46eea77dd6'
WHEEL = Path('/home/tnnrpolley21/Workspaces/Engineering/ePC-SAFT/build/wheels/main-e6dae5c7/epcsaft-1.2.0-cp313-cp313-manylinux_2_39_x86_64.whl')
M, W, C = 'monoethanolamine', 'water', 'carbon-dioxide'
R = epcsaft.GAS_CONSTANT_J_PER_MOL_K
TERMS = ('hard_chain', 'dispersion', 'association', 'dipolar', 'debye_huckel', 'born')
LAW = ('a', 'b', 'c', 'd', 'e', 'f', 'reference_temperature', 'temperature_min', 'temperature_max', 'standard_state_id')

def write(name, value):
    (OUT / name).write_text(json.dumps(dict(wheel_sha256=SHA, result=jsonable(value)), indent=2, allow_nan=False)+'\n')

def load(name):
    return json.loads((OUT / name).read_text())['result']

def thermal(spec, corrected=True):
    src = copy.deepcopy(spec.inputs['caloric'])
    if corrected:
        src['components'][W] = json.loads((ROOT/'data/reference/MEA/thermal/physical-ideal-gas-calorics.json').read_text())['components'][W]
    else:
        src['components'][W] = json.loads((OUT.parent/'water-ideal-gas/old-water.json').read_text())
    intervals = []
    for cid in spec.parameters.component_ids:
        q = src['components'].get(cid)
        if q is None:
            intervals.append([])
            continue
        f = epcsaft.IdealPolynomial(q['coefficients'], q['enthalpy_entropy_anchor_k'], q['enthalpy_anchor_j_per_mol'], q['entropy_anchor_j_per_mol_k']) if q['representation']=='cp_polynomial' else epcsaft.IdealShomate(q['coefficients'], q['formation_enthalpy_j_per_mol'])
        intervals.append([epcsaft.IdealInterval(*q['range_k'], True, True, epcsaft.IdealCorrelation(f, src['reference_pressure_pa']))])
    spec.thermal = epcsaft.ThermochemistryRecord(src['reference_pressure_pa'], intervals)
    spec.model = epcsaft.Mixture(spec.parameters, thermochemistry=spec.thermal)
    return intervals

def evaluate(spec, rows):
    records = [spec.prediction(r) for r in rows]
    for r,p in zip(rows,records,strict=True):
        if p['status']=='Available':
            p['weighted_residual'] = math.sqrt(r['weight'])*p['residual']
            p['cost'] = .5*p['weighted_residual']**2
    return records

def available(records):
    return all(p['status']=='Available' and p['requested_tolerance_met'] and all(math.isfinite(p[k]) for k in ('value','residual')) for p in records)

def group_metrics(rows, predictions):
    total = math.fsum(p.get('cost',0) for p in predictions)
    groups = {}
    for g in dict.fromkeys(r['group'] for r in rows):
        pairs = [(r,p) for r,p in zip(rows,predictions) if r['group']==g]
        pp = [p for r,p in pairs if p['status']=='Available']
        groups[g] = dict(rows=len(pairs), available=len(pp), unavailable=[p for r,p in pairs if p['status']!='Available'], cost=sum(p.get('cost',0) for p in pp), cost_share=sum(p.get('cost',0) for p in pp)/total if total else None,
                         AARD_percent=100*np.mean([abs(p['value']/p['observed']-1) for p in pp]) if pp else None, RMSE_native=np.sqrt(np.mean([(p['value']-p['observed'])**2 for p in pp])) if pp else None,
                         within_2scale=[r['identity'] for r,p in pairs if p['status']=='Available' and abs(p['residual'])<=2])
        kinds={r.get('kind','addition_enthalpy') for r,p in pairs}
        groups[g]['RMSE_by_quantity']={k:np.sqrt(np.mean([(p['value']-p['observed'])**2 for r,p in pairs if r.get('kind','addition_enthalpy')==k and p['status']=='Available'])) for k in kinds}
        if len(kinds)>1: groups[g]['RMSE_native']=None
    return dict(total_cost=total, groups=groups)

def qualify():
    assert hashlib.sha256(WHEEL.read_bytes()).hexdigest()==SHA
    with zipfile.ZipFile(WHEEL) as z:
        assert all(z.read(n)==(Path(epcsaft.__file__).parent.parent/n).read_bytes() for n in z.namelist() if n.startswith('epcsaft/') and not n.endswith('/'))
    spec = SolventSpecification(AN/'MEA-post-260-340.toml')
    thermal(spec, corrected=False)  # reference.json predates the #260 water correction
    rows = spec.inputs['observations']['fitted']
    pred = evaluate(spec, rows)
    refs = json.loads((ROOT/'analyses/mea_parameter_bundle/results/adoption-297/historical-spec/inputs/reference.json').read_text())
    differences = []
    for r,p,q in zip(rows,pred,refs,strict=True):
        assert r['identity']==q['target']
        differences.append(dict(identity=r['identity'], passed=p['status']=='Available' and p['requested_tolerance_met'] and all(abs(p[k]-q[v])<=1e-8+1e-8*abs(q[v]) for k,v in [('value','predicted'),('residual','residual'),('weighted_residual','weighted_residual')]),
                                absolute={k:abs(p[k]-q[v]) for k,v in [('value','predicted'),('residual','residual'),('weighted_residual','weighted_residual')]}))
    write('qualification.json', dict(rows=len(rows), differences=differences, metrics=group_metrics(rows,pred), python=sys.version, installed_files_byte_identical=True, absolute_floor=1e-8, relative_tolerance=1e-8))
    write('original-predictions.json', pred)
    assert len(rows)==307 and all(d['passed'] for d in differences)
    print('qualified all 307', flush=True)

def setup():
    assert all(d['passed'] for d in load('qualification.json')['differences'])
    spec = SolventSpecification(AN/'MEA-post-260-340.toml')
    intervals = thermal(spec)
    original = spec.inputs['observations']['fitted']
    template = spec.problems[original[-4]['problem']]
    masses = {c['component_id']:c['fixed']['molar_mass']['value']['magnitude'] for c in spec.inputs['endpoint']['components']}
    sources = list(csv.DictReader((OUT/'sources.csv').open()))
    broad = []
    for i,s in enumerate(sources):
        if s['role']=='outside-loading-domain': continue
        t,alpha = float(s['T_K']),float(s['loading'])
        water = 1/(float(s['MEA_molality'])*masses[W]) if s['MEA_molality'] else masses[M]*(1-float(s['MEA_unloaded_mass_fraction']))/float(s['MEA_unloaded_mass_fraction'])/masses[W]
        feed = {M:1., W:water, C:max(alpha,1e-6)}
        mass,amount = sum(n*masses[c] for c,n in feed.items()),sum(feed.values())
        problem = copy.copy(template)
        problem.T,problem.P,problem.feed = t,float(s['calculation_pressure_Pa']),eq.Amounts(feed)
        name = f"{s['source']}-{t}-{alpha}"
        spec.problems[name] = problem
        r = copy.deepcopy(original[-4])
        r.update(identity=name, problem=name, group='broad Cp' if s['role']=='probe-fit' else s['source']+' comparison', row=dict(s), temperature_domain=[298.15,393.15], continuation=None)
        observed = float(s['cp_kJ_kg_K'])*1000*mass/amount
        r['arguments'] = dict(r['arguments'], observed=observed, scale=float(s['relative_scale'])*observed)
        r['feed_mass_kg'],r['feed_amount_mol'] = mass,amount
        broad.append(r)
    assert len(broad)==60 and sum(r['group']=='broad Cp' for r in broad)==51
    original = list(original)
    for s in json.loads((OUT.parent/'data/input/fit-campaigns/heat-rows.json').read_text()):
        name=s['record_id']
        water=masses[M]*.7/(.3*masses[W])
        for label,alpha in [('initial',0.),('final',s['alpha_final'])]:
            problem=copy.copy(template)
            problem.T,problem.P,problem.feed=s['temperature_K'],s['system_pressure_Pa'],eq.Amounts({M:1.,W:water,C:alpha})
            spec.problems[name+label]=problem
        original.append(dict(identity=name,group='integral heat',observation_parameters=spec.parameter_sha256,constructor='addition_enthalpy',initial=name+'initial',final=name+'final',weight=1.,temperature_domain=[293.15,393.15],row=s,
                             arguments=dict(feed={C:1.},amount=s['alpha_final'],T=s['temperature_K'],P=s['system_pressure_Pa'],phase='vapor',observed=s['observed_addition_enthalpy_J_per_mol_CO2'],form='difference',scale=s['uH_J_per_mol_CO2'])))
    return spec, original, broad, intervals

def decompose(spec, rows, intervals):
    pure = {cid:epcsaft.Pure(epcsaft.Parameters.from_mapping(spec.inputs['endpoint'],components=[cid]),thermochemistry=epcsaft.ThermochemistryRecord(1e5,[intervals[list(spec.parameters.component_ids).index(cid)]])) for cid in (M,W,C)}
    result=[]
    for r in rows:
        problem=spec.problems[r['problem']]
        solved=eq.solve_equilibrium(spec.model,problem)
        assert solved.success and solved.requested_tolerance_met,solved.message
        x=dict(zip(spec.parameters.component_ids,solved.mole_fractions,strict=True))
        state=spec.model.state(problem.T,P=problem.P,x=x,phase='liquid',derived_properties=True)
        action=eq.solved_state_actions(eq.compile_problem(spec.model,problem),solved,eq.SolvedStateActionRequest([eq.SolvedStateObservable(eq.SolvedStateObservableKind.PhaseProperty,0,0,epcsaft.PropertyObservable.TotalIsobaricHeatCapacity)],[eq.SolvedStateActionDirection(0.,0.,[0.]*len(x),[])]))
        assert action.results[0].status.name=='Available',str(action.results[0].status)
        factor=solved.amounts[0]/r['feed_mass_kg']/1000
        frozen=action.results[0].value*factor
        neutral={cid:pure[cid].state(problem.T,rho=1.).ideal_isobaric_heat_capacity*x[cid]*factor for cid in pure}
        native_cv=state.residual_isochoric_heat_capacity
        parts=[]
        for h in (.05,.025):
            states=[spec.model.state(problem.T+k*h,rho=state.molar_density,x=x) for k in (-1,0,1)]
            part={term:-R*(2*problem.T*(getattr(states[2],term)-getattr(states[0],term))/(2*h)+problem.T**2*(getattr(states[2],term)-2*getattr(states[1],term)+getattr(states[0],term))/h**2) for term in TERMS}
            parts.append(part)
        closure=sum(parts[-1].values())-native_cv
        assert abs(closure)<=1e-4+1e-4*abs(native_cv),(r['identity'],closure,native_cv)
        cp=spec.prediction(r)
        assert cp['status']=='Available',cp
        equilibrium=cp['value']*r['feed_amount_mol']/r['feed_mass_kg']/1000
        result.append(dict(identity=r['identity'],T_K=problem.T,loading=float(r['row']['loading']),source=r['row']['source'],observed_kJ_kg_K=float(r['row']['cp_kJ_kg_K']),equilibrium_kJ_kg_K=equilibrium,frozen_kJ_kg_K=frozen,neutral_ideal_kJ_kg_K=neutral,
                           completed_source_reference_kJ_kg_K=frozen-state.residual_isobaric_heat_capacity*factor-sum(neutral.values()),residual_Cv_kJ_kg_K={k:v*factor for k,v in parts[-1].items()},coupling_minus_R_kJ_kg_K=(state.residual_isobaric_heat_capacity-native_cv)*factor,reaction_equilibration_kJ_kg_K=equilibrium-frozen,
                           closure_J_mol_K=closure,refinement_J_mol_K={k:parts[1][k]-parts[0][k] for k in TERMS},phase_amount_mol=solved.amounts[0],feed_amount_mol=r['feed_amount_mol'],feed_mass_kg=r['feed_mass_kg']))
        print('decomposed',r['identity'],flush=True)
    return result

def baseline():
    spec,original,broad,intervals=setup()
    write('corrected-original.json',dict(predictions=evaluate(spec,original),metrics=group_metrics(original,evaluate(spec,original))))
    write('baseline.json',dict(predictions=evaluate(spec,broad),metrics=group_metrics(broad,evaluate(spec,broad))))
    write('decomposition.json',decompose(spec,broad,intervals))

def apply_laws(spec,laws):
    for problem in spec.problems.values():
        for reaction in problem.reactions:
            if reaction.name in laws:
                old=reaction.correlation
                fields=dict(laws[reaction.name],temperature_min=old.temperature_min,temperature_max=old.temperature_max)
                reaction.correlation=eq.ReactionLogPolynomial(**fields)

def stability(spec,rows):
    # Same existing application classifier: gas descent is distinct from dense descent.
    policy=dict(carbon_component=C,carbon_species=[C,'carbamate-anion','bicarbonate-anion','carbonate-anion'],neutral_species=[M,W,C],packing_fraction_threshold=.10,ambiguity_interval=[.08,.12])
    return [spec.phase(dict(r,endpoint_sha256=spec.parameter_sha256),policy) for r in rows]

def probe(name, replay_only=False):
    spec,original,broad,intervals=setup()
    coordinate_path = ROOT/'analyses/solvent_specification_mea/inputs/fit-coordinates.json'
    assert hashlib.sha256(coordinate_path.read_bytes()).hexdigest() == 'ea65e392c34484f2c54b8f61cc465f25c8d6a9377a5b51a1f0db5e60585251af'
    coords=json.loads(coordinate_path.read_text())
    for q in coords:q['origin']=q['base']
    if name=='B':
        pair=next(p for p in spec.inputs['endpoint']['pairs'] if {p['component_id_a'],p['component_id_b']}=={M,W})
        for family,delta,scale in [('k_ij',.05,.01),('k_ij_reciprocal_temperature_slope',100.,20.)]:
            value=next(c['value']['magnitude'] for c in pair['coefficients'] if c['family']==family)
            coords.append(dict(identity=family+' MEA-water',targets=[[family,[M,W],1.]],origin=value,scale=scale,bounds=[value-delta,value+delta]))
    spec.inputs['coordinates']=coords
    rows=[r for r in original if r['group'] not in ('Cp','integral heat')]+[r for r in broad if r['group']=='broad Cp']
    spec.inputs['observations']['fitted']=rows
    spec.spec['optimizer']=dict(maximum_iterations=60,function_tolerance=1e-8,parameter_tolerance=1e-10,gradient_tolerance=1e-8,maximum_elapsed_time_seconds=1200.)
    if replay_only:
        report=load(f'probe-{name}-fit.json')
        fitted=epcsaft.Parameters.from_mapping(load(f'probe-{name}-parameters.json'))
    else:
        before=evaluate(spec,rows)
        assert available(before)
        write(f'probe-{name}-start.json',dict(coordinates=coords,metrics=group_metrics(rows,before),predictions=before))
        result,report,fitted=spec.fit()
        report['reaction_laws']={n:{k:getattr(l,k) for k in LAW} for n,l in result.chart.reaction_laws.items()}
        report['coordinates']=coords
        write(f'probe-{name}-fit.json',report)
        if not result.usable: return
        write(f'probe-{name}-parameters.json',document_mapping(fitted))
    spec.parameters=fitted
    spec.model=epcsaft.Mixture(fitted,thermochemistry=spec.thermal)
    apply_laws(spec,report['reaction_laws'])
    predictions=evaluate(spec,rows)
    assert available(predictions)
    assert max(abs(p['weighted_residual']-v) for p,v in zip(predictions,report['weighted_residuals'],strict=True))<1e-6
    orig=evaluate(spec,original)
    metrics=group_metrics(original,orig)
    base=load('corrected-original.json')['metrics']['groups']
    deterioration={}
    for g,v in metrics['groups'].items():
        b=base[g]
        pressure=g in ('common149','Kiepe','Cai','restored species','Jakobsen')
        deterioration[g]=dict(AARD_change_percentage_points=v['AARD_percent']-b['AARD_percent'],AARD_ratio=v['AARD_percent']/b['AARD_percent'],RMSE_ratio=None if pressure else v['RMSE_native']/b['RMSE_native'],lost_within_2scale=sorted(set(b['within_2scale'])-set(v['within_2scale'])))
        d=deterioration[g]
        d['passes']=bool(v['available']==v['rows'] and (d['AARD_change_percentage_points']<=2 if pressure else not d['lost_within_2scale'] and max(d['AARD_ratio'],d['RMSE_ratio'])<=1.25))
    bp=evaluate(spec,broad)
    write(f'probe-{name}-replay.json',dict(original=orig,original_metrics=metrics,broad=bp,broad_metrics=group_metrics(broad,bp),fit_metrics=group_metrics(rows,predictions),deterioration=deterioration,passes_deterioration=all(d['passes'] for d in deterioration.values()),native_cost=report['final_cost'],replay_cost=group_metrics(rows,predictions)['total_cost']))
    write(f'probe-{name}-stability.json',stability(spec,broad))
    write(f'probe-{name}-decomposition.json',decompose(spec,broad,intervals))
    print('probe',name,report['status'],report['final_cost'],flush=True)

if __name__=='__main__':
    {'qualify':qualify,'baseline':baseline,'stability':lambda:write('baseline-stability.json',stability(setup()[0],setup()[2])),'A':lambda:probe('A'),'A-replay':lambda:probe('A',True),'B':lambda:probe('B'),'B-replay':lambda:probe('B',True)}[sys.argv[1]]()
