"""Conditional uncertainty and diagnostic bound profiles for issue 307; no adoption.

Run: agent-heavy uv run --no-sync python .../uncertainty_307.py MEA|MDEA
One fit at a time; native workers use AGENT_HEAVY_CORES. Restart skips saved fits.
"""
# ruff: noqa: E402 -- analysis paths must precede project imports.
import copy
import csv
import json
import os
from pathlib import Path
import sys
from types import SimpleNamespace

ROOT = Path(__file__).resolve().parents[3]
sys.path[:0] = [str(ROOT/'src'), str(Path(__file__).parent), str(ROOT/'analyses/permittivity_temperature_loading'), str(ROOT/'analyses/mea_parameter_bundle/calibration-misfit'), str(ROOT/'analyses/mdea_mea_workflow/scripts')]
import numpy as np
import epcsaft
from epcsaft import regression as reg
from MEA.solvent_specification import SolventSpecification, jsonable
from dielectric_volume import verify_wheel
import refit

SHA = '0962e21d2fa7a8ba1ed4622f1110b3e8053bacd878fa41c999d85e8b9afab66b'
WHEEL = ROOT/'build/engine-wheels/main-391dfe5d64ede5036bf160bc6ae037ad5e14af32/epcsaft-1.3.0-cp313-cp313-manylinux_2_39_x86_64.whl'
BASE = '79706636e8716974e045b582f1b1cbfe7e4c7009'


def read(path):
    return json.loads(Path(path).read_text())


def write(path, value):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(jsonable(value), indent=2, allow_nan=False)+'\n')


def table(path, rows):
    with path.open('w') as f:
        w = csv.DictWriter(f, fieldnames=list(rows[0]),lineterminator='\n')
        w.writeheader()
        w.writerows(rows)


def setup(name):
    if name == 'MEA':
        import adoption_297 as a
        spec = a.r.bind(a.r.s.parameter_mapping(a.RECORDS['candidate']))
        # bind preserves historical observation construction; provenance names the evaluated endpoint.
        spec.parameter_sha256 = a.sha(a.RECORDS['candidate'])
        record = read(a.OUT/'conditional-uncertainty.json')
        declared = copy.deepcopy(record['coordinate_map'])
        for q in declared:
            if q.get('kind') == 'reaction_enthalpy_shift':
                q['bounds'] = [x-q['value'] for x in q['bounds']]
        out = ROOT/'analyses/mea_parameter_bundle/results/uncertainty-307'
    else:
        spec = SolventSpecification(ROOT/'analyses/solvent_specification_mdea/B1.toml')
        declared = read(ROOT/'analyses/mdea_mea_workflow/results/refit-298/B1-endpoint/declaration.json')['coordinates']
        fit = read(ROOT/'analyses/mdea_mea_workflow/results/refit-298/B1-endpoint/fit.json')
        # Coordinate origins in declaration are the fit start; native optimizer gives endpoint.
        for i,q in enumerate(declared):
            q['origin'] += q['scale']*fit['optimizer'][i]
            q['identity'] = str(q['targets'][0][1])+' / '+q['targets'][0][0]
            q['value'] = q['origin']
            family,target,_ = q['targets'][0]
            q['unit'] = ('1 / kelvin' if str(target).endswith('/a1') else 'kelvin' if family in ('k_ij_reciprocal_temperature_slope','dispersion_energy_over_k') else 'angstrom' if family in ('segment_diameter','born_diameter') else 'dimensionless')
        out = ROOT/'analyses/solvent_specification_mdea/results/uncertainty-307'
    spec.inputs['coordinates'] = declared
    return spec, declared, out


def fit(spec, indices, folder):
    path = folder/'fit.json'
    if path.exists():
        saved = read(path)
        if not saved['trial_failures'] or 'failures' in saved:
            saved.setdefault('failures',[])
            write(path,saved)
            return saved
    rows = spec.inputs['observations']['fitted']
    controls = dict(spec.spec.get('optimizer', read(ROOT/'analyses/mea_parameter_bundle/results/engine-3e83e19c-refit-chain/a6/spec.json')['controls']), workers=int(os.environ['AGENT_HEAVY_CORES']))
    controls.update(maximum_iterations=40, maximum_elapsed_time_seconds=2100.)
    result = reg.fit(spec.parameters, [spec.coordinates()[i] for i in indices],
                     [spec.observation(r) for r in rows], weights=[r['weight'] for r in rows],
                     thermochemistry=spec.thermal, controls=reg.FitControls(**controls), singular_vectors=True)
    fields = ('status','message','usable','initial_cost','final_cost','optimizer','physical','predictions',
              'weighted_residuals','iterations','trial_failures','optimizer_jacobian')
    saved = {k: getattr(result,k) for k in fields}
    saved['failures'] = [dict(trial=f.trial,observation=f.observation,identity=rows[f.observation]['identity'] if 0<=f.observation<len(rows) else None,
        status=f.status.name,message=f.message,jacobian=f.jacobian,optimizer=list(f.optimizer)) for f in result.failures]
    saved['covariance'] = {k:getattr(result.covariance,k) for k in ('status','assumption','rank','active_bounds','optimizer','physical','variance_factor','singular_values','right_vectors')}
    saved.update(indices=indices, controls=controls)
    write(path,saved)
    print(folder, result.status, result.final_cost, flush=True)
    return read(path)


def derivative(spec, records):
    return reg.differentiate(spec.parameters, spec.coordinates(), [spec.observation(r) for r in records],
                             optimizer=[0.]*len(spec.inputs['coordinates']), thermochemistry=spec.thermal)


def prediction_records(spec,name):
    # Use the retained pressure/species/caloric states rather than inventing a new operating grid.
    rows = spec.inputs['observations']['fitted']
    predictions = list(rows)
    if name == 'MDEA':
        predictions = [r for r in rows if r['group']=='Carson']
        predictions += [r for r in spec.inputs['observations']['comparisons'] if r['group']=='Ermatchkov' and float(r['row']['mass_fraction'])<=.49]
        # Xiao states are owned by the #298 pressure driver and absent from the specification.
        import assess_298 as a
        law = next(r['correlation'] for r in spec.spec['chemistry']['reactions']['aqueous'] if r['name']=='R2')
        next(r for r in a.s.j.d.REACTIONS if r.name=='R2').correlation = a.s.eq.ReactionLogPolynomial(**law)
        for row in a.s.j.rows('Xiao2018_context.csv'):
            prob = a.s.j.problem(float(row['temperature_K']),101000.,a.s.j.water(float(row['unloaded_MDEA_mass_fraction'])),float(row['alpha_exp']),True)
            key = 'Xiao:'+str(len(predictions))
            spec.problems[key] = prob
            predictions.append(dict(identity=key,group='Xiao',problem=key,constructor='observation',kind='partial_pressure',
                arguments=dict(phase='V',species=['carbon-dioxide'],observed=float(row['p_CO2_kPa'])*1000,form='difference',scale=1.),
                temperature_domain=[293.15,395.],observation_parameters=spec.parameter_sha256))
    if name == 'MEA':
        predictions = [r for r in predictions if r['kind'] in ('partial_pressure','equilibrium_isobaric_heat_capacity','phase_density')
            or r['constructor']=='addition_enthalpy' or (r['kind']=='mole_fraction' and
            any(x in r['arguments'].get('species',[]) for x in ('carbamate-anion','bicarbonate-anion')))]
        # Distinguish the measured bicarbonate+carbonate aggregate from the predicted bicarbonate share.
        predictions += [dict(r,identity=r['identity']+':bicarbonate-only',
            arguments=dict(r['arguments'],species=['bicarbonate-anion'])) for r in predictions
            if r['kind']=='mole_fraction' and 'bicarbonate-anion' in r['arguments'].get('species',[])]
        predictions = [dict(r,group=r['group']+': '+('heat of absorption' if r['constructor']=='addition_enthalpy' else
            r['kind']+(' / '+','.join(r['arguments'].get('species',[])) if r['kind']=='mole_fraction' else ''))) for r in predictions]
    return predictions


def main(name):
    verify_wheel(WHEEL,SHA)
    spec,decl,out = setup(name)
    n = len(decl)
    scales = np.array([q['scale'] for q in decl])
    active = [i for i,q in enumerate(decl) if min(q['origin']-q['bounds'][0],q['bounds'][1]-q['origin']) <= 1e-6*q['scale']]
    free = [i for i in range(n) if i not in active]
    rows = spec.inputs['observations']['fitted']
    out.mkdir(parents=True,exist_ok=True)
    write(out/'inputs.json',dict(base=BASE,wheel_sha256=SHA,parameter_sha256=spec.parameter_sha256,
          coordinates=decl,active=active,free=free,rows=len(rows),profile_fractions=[.01,.05,.1]))
    if not (out/'adopted.json').exists():
        ev = derivative(spec,rows)
        replay = [spec.prediction(r) for r in rows]
        assert all(r['status']=='Available' for r in replay)
        write(out/'adopted.json',dict(predictions=ev.predictions,gradient=ev.optimizer_gradient,
              jacobian=ev.residual_optimizer_gradient,residuals=[r['residual'] for r in replay]))
    point = read(out/'adopted.json')
    y = np.array(point['predictions'])
    weights = np.array([r['weight'] for r in rows])
    residual = np.array(point['residuals'])*np.sqrt(weights)
    J = np.array(point['jacobian']).reshape(-1,n)*np.sqrt(weights)[:,None]
    cost = float(residual@residual/2)
    conditional = fit(spec,free,out/'conditional')
    movement = {decl[i]['identity']:u for i,u in zip(free,conditional['optimizer'])}
    local = refit.identifiability(SimpleNamespace(physical=[q['origin'] for q in decl],covariance=SimpleNamespace(active_bounds=active)),
                                 J/scales,residual,[q['identity'] for q in decl],[q['bounds'][0] for q in decl],[q['bounds'][1] for q in decl])
    se = np.array([local['conditional_standard_error'][decl[i]['identity']] for i in free])
    corr = np.array(local['conditional_correlation'])
    C = corr*np.outer(se/scales[free],se/scales[free])
    covariance_source = 'adopted-point conditional inverse-Jacobian; bound coordinates fixed'
    if (max(map(abs,movement.values())) <= 1e-4 and
            (cost-conditional['final_cost'])/cost <= 1e-8 and conditional['covariance']['status']=='available'):
        native = conditional['covariance']
        C = np.array(native['optimizer']).reshape(len(free),len(free))*native['variance_factor']
        se = np.sqrt(np.diag(C))*scales[free]
        covariance_source = 'native conditional covariance; bound coordinates fixed'
    native_se = (np.sqrt(np.diag(np.array(conditional['covariance']['optimizer']).reshape(len(free),len(free))) * conditional['covariance']['variance_factor'])*scales[free]).tolist() if conditional['covariance']['status']=='available' else None
    table(out/'standard-errors.csv',[dict(parameter=decl[i]['identity'],unit=decl[i].get('unit'),native_SE_bound_fixed=native_se[k] if native_se else None,adopted_point_SE_bound_fixed=local['conditional_standard_error'][decl[i]['identity']]) for k,i in enumerate(free)])
    native_optimizer = np.array(conditional['covariance']['optimizer']).reshape(len(free),len(free))
    native_diagonal = np.sqrt(np.diag(native_optimizer))
    native_correlation = native_optimizer/np.outer(native_diagonal,native_diagonal)
    # Retain both estimates; record the covariance actually used for the ranking.
    U,sv,V = np.linalg.svd(J,full_matrices=False)
    write(out/'covariance.json',dict(adopted_cost=cost,conditional_cost_change=conditional['final_cost']-cost,
          scaled_movement=movement,adopted_point=local,native=conditional['covariance'],
          ranking_covariance=covariance_source,native_standard_errors=native_se,
          native_correlation=native_correlation.tolist(),
          singular_values=sv.tolist(),right_vectors=V.tolist()))
    predictions = prediction_records(spec,name)
    if not (out/'predictions.json').exists():
        ev = derivative(spec,predictions)
        write(out/'predictions.json',dict(records=[{k:r.get(k) for k in ('identity','group','kind','row','arguments')} for r in predictions],
              values=ev.predictions,gradient=ev.optimizer_gradient))
    pred = read(out/'predictions.json')
    py = np.array(pred['values'])
    pred['records'] = [{k:r.get(k) for k in ('identity','group','kind','row','arguments','constructor')} for r in predictions]
    for r,record in zip(predictions,pred['records'],strict=True):
        problem = spec.problems[r.get('problem',r.get('initial'))]
        record['conditions'] = dict(T_K=problem.T,feed_amounts=problem.feed.values,
            P_Pa=problem.P if isinstance(problem.P,(int,float)) else None,pressure_guess_Pa=getattr(problem.P,'guess',None))
    write(out/'predictions.json',pred)
    G = np.array(pred['gradient']).reshape(-1,n)
    groups = list(dict.fromkeys(r['group'] for r in predictions))
    sensitivity = []
    for i in free:
        delta = G[:,i]*se[free.index(i)]/scales[i]
        changes = {g:float(np.max(np.abs(delta[[r['group']==g for r in predictions]])/np.maximum(np.abs(py[[r['group']==g for r in predictions]]),1e-30))) for g in groups}
        sensitivity.append(dict(parameter=decl[i]['identity'],value=decl[i].get('value',decl[i]['origin']),SE_bound_fixed=se[free.index(i)],
            unit=decl[i].get('unit'),max_fractional_change=max(changes.values()),top_predictions='; '.join(sorted(changes,key=changes.get,reverse=True)[:3]),group_changes=changes))
    bands = np.sqrt(np.maximum(0,np.einsum('ij,jk,ik->i',G[:,free],C,G[:,free])))
    table(out/'prediction-bands.csv',[dict(identity=r['identity'],group=r['group'],value=v,SE_bound_fixed=b,lower_95=v-1.96*b,upper_95=v+1.96*b) for r,v,b in zip(predictions,py,bands)])
    write(out/'interior-ranking.json',sensitivity)
    profiles = []
    for i in active:
        q = decl[i]
        sign = 1 if q['origin']-q['bounds'][0] < q['bounds'][1]-q['origin'] else -1
        for fraction in (.01,.05,.1):
            folder = out/f'profile-{i}-{fraction}'
            ss,dd,_ = setup(name)
            dd[i]['origin'] += sign*fraction*(q['bounds'][1]-q['bounds'][0])
            prediction_records(ss,name)
            probe = ss.inputs['observations']['fitted'][:1]
            chart = derivative(ss,probe).chart
            transformations = []
            complete = []
            if q.get('kind')=='reaction_enthalpy_shift':
                probe += [next(r for r in ss.inputs['observations']['fitted'] if r['constructor']=='addition_enthalpy')]
                for j,other in enumerate(dd):
                    if other.get('kind')=='reaction_coordinate' and other['name']==q['name']:
                        shifted = getattr(chart.reaction_laws[q['name']],other['coefficient'])
                        transformations.append(dict(index=j,original_origin=other['origin'],original_bounds=other['bounds'][:],offset=shifted-other['origin']))
                for step in (0.,.25):
                    vector = [0.]*n
                    vector[transformations[0]['index']] = step
                    complete.append(reg.differentiate(ss.parameters,ss.coordinates(),[ss.observation(r) for r in probe],optimizer=vector,thermochemistry=ss.thermal).predictions)
                for t in transformations:
                    dd[t['index']]['origin'] += t['offset']
                    dd[t['index']]['bounds'] = [b+t['offset'] for b in t['original_bounds']]
                    t['translated_coordinate'] = copy.deepcopy(dd[t['index']])
            ss.parameters = epcsaft.Parameters(chart.parameters, ss.parameters.component_ids, ss.parameters.site_ids)
            for problem in ss.problems.values():
                for reaction in problem.reactions:
                    if reaction.name in chart.reaction_laws:
                        reaction.correlation = chart.reaction_laws[reaction.name]
            if transformations:
                reduced = []
                for step in (0.,.25):
                    vector = [step if j==transformations[0]['index'] else 0. for j in range(n) if j!=i]
                    reduced.append(reg.differentiate(ss.parameters,[ss.coordinates()[j] for j in range(n) if j!=i],
                        [ss.observation(r) for r in probe],optimizer=vector,thermochemistry=ss.thermal).predictions)
                difference = float(np.max(np.abs(np.array(reduced)/np.array(complete)-1)))
                write(folder/'chart-equivalence.json',dict(transformations=transformations,optimizer_steps=[0.,.25],complete=complete,reduced=reduced,max_relative_difference=difference))
                assert difference<=1e-10  # #297 prediction-replay tolerance, not a fit-quality threshold.
            result = fit(ss,[j for j in range(n) if j!=i],folder)
            indices = [j for j in range(n) if j!=i]
            if not (folder/'predictions.json').exists():
                ev = reg.differentiate(ss.parameters,[ss.coordinates()[j] for j in indices],
                    [ss.observation(r) for r in predictions],optimizer=result['optimizer'],thermochemistry=ss.thermal)
                write(folder/'predictions.json',dict(values=ev.predictions))
            moved = np.array(read(folder/'predictions.json')['values'])
            changes = {g:float(np.max(np.abs(moved[[r['group']==g for r in predictions]]/py[[r['group']==g for r in predictions]]-1))) for g in groups}
            profiles.append(dict(parameter=q['identity'],group_changes=changes,fraction=fraction,fixed_value=q.get('value',q['origin'])+dd[i]['origin']-q['origin'],
                cost=result['final_cost'],delta_cost=result['final_cost']-cost,status=result['status'],usable=result['usable'],
                max_fitted_prediction_change=float(np.max(np.abs(np.array(result['predictions'])/y-1))) if result['predictions'] else None))
            write(out/'profiles.json',profiles)
    for i in active:
        scan = [r for r in profiles if r['parameter']==decl[i]['identity']]
        changes = scan[0]['group_changes']
        sensitivity.append(dict(parameter=decl[i]['identity'],value=decl[i].get('value',decl[i]['origin']),SE_bound_fixed=None,
            unit=decl[i].get('unit'),max_fractional_change=max(changes.values()),top_predictions='; '.join(sorted(changes,key=changes.get,reverse=True)[:3]),
            group_changes=changes,profile_step=scan[0]['fixed_value']-decl[i].get('value',decl[i]['origin'])))
    write(out/'ranking.json',sorted(sensitivity,key=lambda r:r['max_fractional_change'],reverse=True))
    table(out/'ranking.csv',[{k:v for k,v in r.items() if k not in ('group_changes','profile_step')} for r in sorted(sensitivity,key=lambda r:r['max_fractional_change'],reverse=True)])



def present(name):
    import matplotlib
    matplotlib.use('Agg')
    import matplotlib.pyplot as plt
    out = ROOT/('analyses/mea_parameter_bundle/results/uncertainty-307' if name=='MEA' else 'analyses/solvent_specification_mdea/results/uncertainty-307')
    decl = read(out/'inputs.json')['coordinates']
    ranking = read(out/'ranking.json')
    covariance = read(out/'covariance.json')
    profiles = read(out/'profiles.json')
    inputs = read(out/'inputs.json')
    pred = read(out/'predictions.json')
    bands = list(csv.DictReader((out/'prediction-bands.csv').open()))
    labels = [r['parameter'].replace('protonated-monoethanolamine','MEAH+').replace('monoethanolamine','MEA').replace('protonated-methyldiethanolamine','MDEAH+').replace('bicarbonate-anion','HCO3-').replace('carbamate-anion','MEACOO-') for r in ranking]
    labels = [x.replace('component/','').replace('pair/','').replace('segment_diameter','segment diameter').replace('dispersion_energy_over_k','dispersion energy / kB').replace('born_diameter','Born diameter').replace('reciprocal_temperature_slope','reciprocal-T slope').replace('temperature_law_coefficient','T-law coefficient').replace('enthalpy_shift','enthalpy shift') for x in labels]
    fig,ax = plt.subplots(figsize=(12,8))
    ax.scatter([100*r['max_fractional_change'] for r in ranking],range(len(ranking)),
               c=['#d2691e' if r['SE_bound_fixed'] is None else '#176b91' for r in ranking])
    ax.set_yticks(range(len(labels)),labels,fontsize=8)
    ax.invert_yaxis()
    ax.set_xscale('log')
    ax.set_xlabel('Largest absolute prediction change (%)\nBlue: one conditional SE; orange: 1% inward profile step with refit')
    ax.set_title(name+': which fitted coordinates affect the retained predictions?')
    ax.grid(axis='x',alpha=.2)
    fig.tight_layout()
    fig.savefig(out/'sensitivity.png',dpi=170)
    plt.close(fig)
    pressure = [(i,b) for i,b in enumerate(bands) if b['group'] in ('Xiao','Ermatchkov') or (name=='MEA' and pred['records'][i]['kind']=='partial_pressure')]
    fig,ax = plt.subplots(figsize=(9,5))
    for group in dict.fromkeys(b['group'] for _,b in pressure):
        subset = [(i,b) for i,b in pressure if b['group']==group]
        index = [float(pred['records'][i]['arguments']['observed']) for i,b in subset]
        v = np.array([float(b['value']) for i,b in subset])
        e = np.array([1.96*float(b['SE_bound_fixed']) for i,b in subset])
        ax.errorbar(index,v,yerr=e,fmt='o',markersize=3,capsize=2,label=group,alpha=.75)
    ax.set_yscale('symlog',linthresh=1.)
    ax.set_xscale('log')
    ax.set_xlabel('Observed CO₂ partial pressure (Pa)')
    ax.set_ylabel('CO₂ partial pressure (Pa)')
    ax.set_title(name+': nominal predictions and conditional 95% linearized bands')
    ax.legend(fontsize=8)
    fig.tight_layout()
    fig.savefig(out/'pressure-bands.png',dpi=170)
    plt.close(fig)
    pressure_se = [float(b['SE_bound_fixed'])/float(b['value']) for _,b in pressure]
    temperatures = [pred['records'][i]['conditions']['T_K'] for i,b in pressure]
    text = ['## Parameter uncertainty and sensitivity (#307)\n',
        f"Pressure bands cover {len(pressure)} retained states at {min(temperatures):.5g}–{max(temperatures):.5g} K. Their conditional relative standard errors range from {100*min(pressure_se):.3g}% to {100*max(pressure_se):.3g}%. Covariance propagation includes parameter correlations; the marginal one-SE perturbations used for ranking do not. Large local fractional changes are derivatives multiplied by SE, not nonlinear perturbed predictions.\n", 
        f"The {inputs['rows']}-row adopted record is unchanged. Covariance and bands are local, linearized and conditional on the fixed model, observation weights, source inputs and bound coordinates. They describe parameter uncertainty under an unknown common residual variance, not model discrepancy, future measurement noise or physical validation. The native variance factor is {covariance['native']['variance_factor']:.8g}.\n",
        f"The interior-only diagnostic refit changes cost by {covariance['conditional_cost_change']:.6g}; the largest absolute movement in units of coordinate scale is {max(map(abs,covariance['scaled_movement'].values())):.6g}. Ranking uses {covariance['ranking_covariance']}. [Both covariance estimates, the native correlation matrix and all movements](covariance.json) are retained.\n",
        'The ranking statistic is the maximum absolute fractional prediction change over each named retained group. Interior coordinates move by one conditional standard error with the others fixed. Bound coordinates use the first inward profile point (1% of the original bound interval), with all remaining coordinates refitted. These are different perturbation sizes; their ranks do not establish statistical significance. Near-zero predictions can dominate relative changes.\n',
        '| Parameter | Adopted value (physical unit) | SE (bound coordinates fixed) or profile | Largest fractional change | Most affected predictions |\n|---|---:|---|---:|---|']
    for r in ranking:
        scans = [p for p in profiles if p['parameter']==r['parameter']]
        uncertainty = f"± {r['SE_bound_fixed']:.4g} (bound fixed)" if r['SE_bound_fixed'] is not None else '; '.join(f"{p['fixed_value']:.5g}: Δcost {p['delta_cost']:.4g} ({p['status']})" for p in scans)
        text.append(f"| {r['parameter']} | {r['value']:.7g} {r.get('unit','')} | {uncertainty} | {r['max_fractional_change']:.4g} | {r['top_predictions']} |")
    text += ['\n![Prediction changes per conditional SE or inward profile step.](sensitivity.png)\n',
             '![Covariance propagated to pressure predictions at the retained measured states (discrete parity comparison). Error bars are nominal ±1.96 conditional SE; the symmetric logarithmic axis preserves any negative lower limits. These are local parameter-only bands, not physical prediction intervals.](pressure-bands.png)\n',
             'The two weakest directions of the complete weighted Jacobian in the original optimizer scales are:\n']
    vectors = np.array(covariance['right_vectors'])
    singular = covariance['singular_values']
    for k in (-1,-2):
        indices = np.argsort(np.abs(vectors[k]))[-4:][::-1]
        text.append(f"- Singular value {singular[k]:.6g}: "+'; '.join(f"{decl[i]['identity']} ({vectors[k,i]:+.4f})" for i in indices)+'.')
    text += ['\nThese directions include bound coordinates; their two-sided singular-vector displacements are not necessarily feasible. They describe local confounding in the declared scales, not a unique physical mechanism.\n',
             'Each bound scan fixes the coordinate at 1%, 5% and 10% of its original interval inward from the adopted bound, independently starting the other coordinates at the adopted point. Native fits have at most 40 iterations and 2100 seconds per point, using the existing stopping tolerances. Returned cost changes and terminations are reported without new fit-quality thresholds. The bound endpoint is the adopted constrained fit. The limited inward grid does not locate a confidence limit or a global optimum. Profiles do not requalify phase stability or change the adopted record. For R5, fixing its enthalpy shift translates the remaining native b coordinate and bounds by the native chart offset; the original admissible interval is preserved. Complete/reduced chart prediction equivalence is retained at zero and a 0.25-scale b displacement. Native rejected-trial causes are retained with each fit.\n',
             '[Profile results](profiles.json), [prediction values and exact native columns](predictions.json), [bands](prediction-bands.csv), [ranked values](ranking.csv) and [input identity](inputs.json) retain the calculation. MEA ranks only pressure, heat, heat capacity, carbamate/bicarbonate and density at states already in its adopted specification. Bicarbonate is additionally resolved alone at the four states with bicarbonate+carbonate observations; this extra model quantity is not a new measured observation or a fitted target. The summed observable is retained separately; MDEA uses the 20 Xiao and 88 Ermatchkov pressure states at ≤49 wt% from #298, its adopted R2 law, and the 40 Carson heat states. Parameter units and ties are in the coordinate declarations; reaction enthalpy shifts are shown as adopted totals in J/mol, whereas refit increments are about zero.\n',
             'Engine commit `391dfe5d64ede5036bf160bc6ae037ad5e14af32`, wheel SHA-256 `'+SHA+'`. Run from the repository root using `agent-heavy env PYTHONPATH=src uv run --no-sync python analyses/mea_parameter_bundle/scripts/uncertainty_307.py '+name+'`. The source base is `'+BASE+'`; the approved ceiling is 400 gross added executable lines. No manuscript promotion is claimed. Independent delivered review is pending.\n']
    import re
    summary = re.sub(r'\]\((?!https?:)([^)]+)\)',r'](results/uncertainty-307/\1)', '\n'.join(text)+'\n')
    review = ROOT/'analyses/mea_parameter_bundle/results/uncertainty-307/review.md'
    if review.exists():
        link = 'results/uncertainty-307/review.md' if name=='MEA' else '../mea_parameter_bundle/results/uncertainty-307/review.md'
        summary = summary.replace('Independent delivered review is pending.',f'Independent delivered review is recorded in the [report]({link}).')
    (out/'summary.qmd').write_text(summary)



def verify_results(name):
    out = ROOT/('analyses/mea_parameter_bundle/results/uncertainty-307' if name=='MEA' else 'analyses/solvent_specification_mdea/results/uncertainty-307')
    adopted = read(out/'adopted.json')
    reference = read(ROOT/('analyses/mea_parameter_bundle/results/adoption-297/candidate/replay.json' if name=='MEA' else 'analyses/solvent_specification_mdea/results/adoption-302/replay.json'))
    if name=='MEA':
        reference = reference['rows']
    delta = [abs(a-b['value'])/max(abs(b['value']),1e-30) for a,b in zip(adopted['predictions'],reference,strict=True)]
    errors = list(csv.DictReader((out/'standard-errors.csv').open()))
    se_difference = max(abs(float(q['native_SE_bound_fixed'])/float(q['adopted_point_SE_bound_fixed'])-1) for q in errors)
    inputs = read(out/'inputs.json')
    profiles = read(out/'profiles.json')
    write(out/'verification.json',dict(rows=len(delta),max_relative_adopted_prediction_difference=max(delta),
          max_relative_native_vs_adopted_point_SE_difference=se_difference,profiles=len(profiles),
          converged_profiles=sum(p['status']=='converged' for p in profiles),bound_coordinates=len(inputs['active']),
          adopted_parameter_sha256=inputs['parameter_sha256'],wheel_sha256=SHA))


if __name__ == '__main__':
    for name in (['MEA','MDEA'] if sys.argv[1]=='all' else [sys.argv[1]]):
        if len(sys.argv)==2:
            main(name)
        present(name)
        verify_results(name)
