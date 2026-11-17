"""Issue 394: composed-law identity, observation replay and bounded run-cost probe."""
import copy
import csv
import hashlib
import json
import math
import os
from pathlib import Path
import sys
import time
import zipfile

ROOT = Path(__file__).resolve().parents[2]
AN = Path(__file__).resolve().parent
OUT = AN / 'results'
sys.path.insert(0, str(ROOT / 'src'))
import epcsaft
from epcsaft import equilibrium as eq, regression as reg
from MEA.solvent_specification import SolventSpecification, jsonable

SPEC = ROOT / 'analyses/solvent_specification_mea'
BASE = json.loads((SPEC / 'inputs/endpoint.json').read_text())
IONS = ['protonated-monoethanolamine', 'carbamate-anion', 'bicarbonate-anion']


def dump(name, value):
    (OUT / name).write_text(json.dumps(jsonable(value), indent=2, allow_nan=False) + '\n')


def composed(mapping, coefficients=None):
    result = copy.deepcopy(mapping)
    coefficients = coefficients or {}
    for family in result['model_families']:
        if family['kind'] == 'permittivity':
            family['choice'] = 'solvent-density-temperature-ion-specific-suppression'
    for component in result['components']:
        if component['fixed']['charge_number']['value']['magnitude']:
            coefficient = copy.deepcopy(component['coefficients'][0])
            coefficient.update(identity='probe/' + component['component_id'] + '/suppression',
                               family='ion_specific_suppression_coefficient',
                               value=dict(magnitude=coefficients.get(component['component_id'], 0.), unit='dimensionless'))
            coefficient['provenance'] = dict(source_id='issue-394-exploratory', locator='https://github.com/tannerpolley/Amine-Thermodynamics/issues/394')
            component['coefficients'].append(coefficient)
    return result


class Probe(SolventSpecification):
    def continue_groups(self):
        pass


def specification(coefficients=None):
    spec = Probe(SPEC / 'MEA.toml')
    spec.parameters = epcsaft.Parameters.from_mapping(composed(BASE, coefficients))
    spec.model = epcsaft.Mixture(spec.parameters, thermochemistry=spec.thermal)
    for key in spec.construction_parameters:
        mapping = BASE if key == spec.parameter_sha256 else spec.load_record(next(
            d['observation_parameters'] for d in spec.spec['datasets'] if d.get('observation_parameters', {}).get('sha256') == key))
        spec.construction_parameters[key] = epcsaft.Parameters.from_mapping(composed(mapping, coefficients))
    SolventSpecification.continue_groups(spec)
    return spec


def verify():
    wheel = next((ROOT / 'build/ion-specific-probe/wheels').glob('*.whl'))
    with zipfile.ZipFile(wheel) as archive:
        for name in archive.namelist():
            if name.startswith('epcsaft/') and not name.endswith('/'):
                assert archive.read(name) == (Path(epcsaft.__file__).parent.parent / name).read_bytes(), name
    return dict(wheel=wheel.name, wheel_sha256=hashlib.sha256(wheel.read_bytes()).hexdigest(), installed_files_verified=True,
                engine_commit='245c0c9d0c0caa4b823b940f38eef8d5cc5fa9e2', python=sys.version, cores=os.environ['AGENT_HEAVY_CORES'])


def replay():
    provenance = verify()
    x = dict(water=.80, monoethanolamine=.18, **{IONS[0]:.01, IONS[1]:.01})
    models = [epcsaft.Mixture(epcsaft.Parameters.from_mapping(m)) for m in (BASE, composed(BASE))]
    identity = [dict(T_K=353., rho_mol_m3=rho, adopted=models[0].state(353., rho=rho, x=x).bulk_relative_permittivity,
                     composed_zero=models[1].state(353., rho=rho, x=x).bulk_relative_permittivity) for rho in (45000.,40000.)]
    assert [r['adopted'] for r in identity]==[55.15795653250771,49.14040580667352]
    assert all(r['adopted']==r['composed_zero'] for r in identity)
    dump('identity.json', identity)
    started = time.perf_counter()
    spec = specification()
    preparation = time.perf_counter() - started
    rows = spec.inputs['observations']['fitted']
    reference = json.loads((SPEC / 'inputs/reference.json').read_text())
    records = []
    for row, ref in zip(rows, reference, strict=True):
        started = time.perf_counter()
        result = spec.prediction(row)
        result['wall_seconds'] = time.perf_counter() - started
        if result['status'] == 'Available' and result.get('requested_tolerance_met'):
            result['cost'] = .5 * row['weight'] * result['residual'] ** 2
            result['prediction_relative_difference'] = abs(result['value']-ref['predicted']) / max(abs(ref['predicted']),1e-300)
            result['residual_absolute_difference'] = abs(result['residual']-ref['residual'])
        records.append(result)
    # Preserve Cai's declared joint temperature/fraction admission rule.
    for identity in {r['state_identity'] for r in rows if r['group']=='Cai'}:
        indices = [i for i,r in enumerate(rows) if r['state_identity']==identity]
        temperature = next(records[i].get('value') for i in indices if rows[i]['kind']=='temperature')
        admitted = len(indices)==2 and all('cost' in records[i] for i in indices)
        admitted = admitted and temperature is not None and rows[indices[0]]['temperature_domain'][0]<=temperature<=rows[indices[0]]['temperature_domain'][1]
        if not admitted:
            for i in indices:
                records[i].pop('cost',None)
                records[i]['status']='PairUnavailable'
    dump('observations.json', records)
    groups = {g:dict(rows=sum(r['group']==g for r in records), unavailable=sum(r['group']==g and 'cost' not in r for r in records),
                        cost=math.fsum(r.get('cost',0.) for r in records if r['group']==g),
                        seconds=sum(r['wall_seconds'] for r in records if r['group']==g)) for g in dict.fromkeys(r['group'] for r in records)}
    dump('replay.json', dict(**provenance, preparation_seconds=preparation, groups=groups, rows=len(records), available=sum('cost' in r for r in records),
                            cost=math.fsum(r.get('cost',0.) for r in records),reference_cost=sum(r['cost'] for r in reference),
                            max_prediction_relative_difference=max((r.get('prediction_relative_difference',0.) for r in records)),
                            max_residual_absolute_difference=max((r.get('residual_absolute_difference',0.) for r in records))))
    summary=json.loads((OUT/'replay.json').read_text())
    assert summary['available']==307 and summary['max_prediction_relative_difference']<=1e-10
    assert abs(summary['cost']/summary['reference_cost']-1)<=1e-10
    print(json.dumps(summary),flush=True)


def trend():
    # Negative and positive equal-ion coefficients are exploratory, not literature fits.
    spec = specification()
    template = next(r for r in spec.inputs['observations']['fitted'] if spec.problems[r.get('problem',r.get('initial'))].reactions)
    problem = copy.copy(spec.problems[template.get('problem',template.get('initial'))])
    problem.T, problem.P = 353.15, 101325.
    water = .7 / .01801528
    amine = .3 / .06108
    problem.phases = [eq.Phase('L',kind='liquid',support=spec.model.component_ids)]
    records=[]
    for coefficient in (-10.,-5.,-2.,0.,2.,5.,7.01,10.,'fitted'):
        scenario = specification({ion:coefficient for ion in IONS}) if coefficient!='fitted' else specification()
        if coefficient=='fitted':
            scenario.parameters=epcsaft.Parameters.from_mapping(json.loads((OUT/'fitted-parameters.json').read_text()))
            scenario.model=epcsaft.Mixture(scenario.parameters,thermochemistry=scenario.thermal)
        for source in csv.DictReader((AN/'inputs/hajj-353K.csv').open()):
            loading=float(source['loading_mol_CO2_per_mol_MEA'])
            observed=float(source['relative_permittivity_inferred_from_915_2450_MHz'])
            problem.feed=eq.Amounts({'water':water/amine,'monoethanolamine':1.,'carbon-dioxide':loading})
            started=time.perf_counter()
            row=dict(coefficient=coefficient,loading=loading,T_K=353.15,P_Pa=101325.,source_epsilon=observed)
            try:
                state=eq.solve_equilibrium(scenario.model,problem)
                row.update(success=state.success,tolerance_met=state.requested_tolerance_met,message=state.message,residuals=list(state.residuals))
                if state.success and state.requested_tolerance_met:
                    native=scenario.model.state(353.15,rho=state.molar_densities[0],x=state.phase_mole_fractions(0))
                    row.update(epsilon=native.bulk_relative_permittivity,rho_mol_m3=state.molar_densities[0],x=state.phase_mole_fractions(0))
            except Exception as error:
                row.update(exception=type(error).__name__,message=str(error))
            row['wall_seconds']=time.perf_counter()-started
            records.append(row)
            dump('trend.json',records)
            print(json.dumps(row),flush=True)


if __name__=='__main__':
    {'replay':replay,'trend':trend}[sys.argv[1]]()
