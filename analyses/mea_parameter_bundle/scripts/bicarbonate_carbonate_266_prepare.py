"""Materialize issue 266 observations from retained source feeds and declarations."""
import copy
import csv
import hashlib
import json
import math
from pathlib import Path
import fit_observations as f
from MEA.solvent_specification import SolventSpecification, jsonable

ROOT = Path(__file__).resolve().parents[3]
OUT = ROOT / 'analyses/mea_parameter_bundle/results/bicarbonate-carbonate-266'
OUT.mkdir(exist_ok=True)
spec = SolventSpecification(ROOT / 'analyses/mea_parameter_bundle/results/adoption-340/historical-spec/MEA.toml')
sources = {}
for path in [Path(f.__file__), Path(f.s.__file__), ROOT/'analyses/mea_parameter_bundle/data/input/state-packet.json.gz']:
    sources[str(path.relative_to(ROOT))] = hashlib.sha256(path.read_bytes()).hexdigest()
def read(path):
    path = ROOT / path
    sources[str(path.relative_to(ROOT))] = hashlib.sha256(path.read_bytes()).hexdigest()
    return list(csv.DictReader(path.open()))
base = 'data/reference/MEA/observations/liquid_speciation/'
matin = read(base + 'Matin_2012_ChEq.csv')
bottinger = read(base + 'Bottinger_2007_ChEq.csv')
jakobsen = read(base + 'Jakobsen_2005_ChEq.csv')
states = read(base + 'Jakobsen_2005_model_states.csv')
read('data/reference/MEA/manifests/speciation_linear_coefficient_rules.csv')
series = [r for r in bottinger if float(r['MEA_weight_fraction']) == .3 and float(r['temperature']) == 20]
def interpolate(alpha, points):
    points = sorted(points)
    assert points[0][0] <= alpha <= points[-1][0]
    for (a, x), (b, y) in zip(points, points[1:]):
        if a <= alpha <= b:
            return x + (y - x) * (alpha - a) / (b - a)
reconciliation = []
for i, r in enumerate(matin, 1):
    alpha, observed = float(r['CO2_loading']), float(r['HCO3^-'])
    other = interpolate(alpha, [(float(b['CO2_loading']), float(b['HCO3^-'])) for b in series])
    reconciliation.append(dict(identity=f'Matin2012_state_{i:03}', loading=alpha, matin=observed,
        bottinger=other, lower=min(observed, other), upper=max(observed, other), scale=abs(observed-other)))
assert len(reconciliation) == 19 and all(r['scale'] > 0 for r in reconciliation)
packet = f.s.load_state_packet()['observations']
template = next(r['request'] for r in packet if r['identity'] == 'Matin2012_state_001')
source_rows, records, problems = [], [], {}
pool = ['bicarbonate-anion', 'carbonate-anion']
carbon = ['carbon-dioxide', 'carbamate-anion', *pool]
for source, rows in [('Matin2012', matin), ('Bottinger2008', bottinger), ('Jakobsen2005', jakobsen)]:
    for i, r in enumerate(rows, 1):
        identity = f'{source}_state_{i:03}'
        if source == 'Bottinger2008' and r not in series:
            continue
        state = states[i-1] if source == 'Jakobsen2005' else None
        alpha = float(state['model_CO2_loading'] if state else r['CO2_loading'])
        fraction = float(state['model_unloaded_MEA_mass_fraction'] if state else r['MEA_weight_fraction'])
        temperature = float(r['temperature']) + 273.15
        request = f.s.source_feed_request(template, dict(source_key=source, CO2_loading=alpha,
            MEA_weight_fraction=fraction, temperature_reported_C=float(r['temperature'])))
        feed = dict(zip(f.s.COMPONENT_IDS, request['reaction_system']['feed_amounts_mol'], strict=True))
        included = source == 'Jakobsen2005' and i in (10, 11, 12, 13)
        source_rows.append(dict(identity=identity, input=r, model_state=state, fit_added=included or source=='Matin2012',
            exclusion=None if included or source=='Matin2012' else 'outside-fit Böttinger' if source=='Bottinger2008' else
            'temperature' if temperature != 293.15 else 'composition' if fraction != float(states[9]['model_unloaded_MEA_mass_fraction']) else 'loading support'))
        observed = float(r['HCO3^-']) + (float(r['CO3^2-']) if source=='Jakobsen2005' else 0)
        scale = interpolate(alpha, [(x['loading'], x['scale']) for x in reconciliation]) if included else (
            reconciliation[i-1]['scale'] if source=='Matin2012' else .01)
        pressures = (500000., 2500000.) if source=='Bottinger2008' else (101325.,500000.,2500000.) if source=='Matin2012' else (101325.,)
        for pressure in pressures:
            key = identity + f':{pressure:g}'
            problems[key] = dict(T=temperature, P=pressure, feed=dict(basis='amounts', values=feed),
                phases=[dict(name='L', kind='liquid', support=list(f.s.COMPONENT_IDS))], reaction_set='aqueous',
                neutral_reference='aqueous', row_tolerance=1e-10)
            for quantity, numerator, denominator, value in [('pool', pool, None, observed)] + ([
                ('carbonate-pool-split', ['carbonate-anion'], pool, float(r['CO3^2-'])/observed),
                ('carbonate-carbon-fraction', ['carbonate-anion'], carbon,
                 float(r['CO3^2-'])/(observed+float(r['MEACOO^-'])+float(r['CO2'] or 0)))] if source=='Jakobsen2005' else []):
                args = dict(observed=value, scale=scale, form='difference', phase='L', species=numerator, mass_basis=False)
                if denominator:
                    args.update(denominator_phase='L', denominator_species=denominator)
                records.append(dict(identity=key+':'+quantity, state_identity=identity, problem=key, group=source+' '+quantity,
                    constructor='observation', kind='amount_ratio' if denominator else 'mole_fraction', arguments=args,
                    temperature_domain=[293.15,313.15], observation_parameters=spec.parameter_sha256, row=dict(r, model_loading=alpha),
                    weight=1/19 if source=='Matin2012' else 1/4 if included else 0.,
                    added=quantity=='pool' and (source=='Matin2012' and pressure==101325. or included)))
values = {q['identity']: q['value']['magnitude'] for c in spec.inputs['endpoint']['components'] for q in c['coefficients']}
values.update({q['identity']: q['value']['magnitude'] for p in spec.inputs['endpoint']['pairs'] for q in p['coefficients']})
coordinates = [dict(identity='reaction:'+name+':a', kind='reaction_coordinate', name=name, coefficient='a',
    origin=next(r['correlation']['a'] for r in spec.spec['chemistry']['reactions']['aqueous'] if r['name']==name), scale=.1) for name in ('R2','R3')]
for pair in [('bicarbonate-anion','water'), ('carbonate-anion','water'), ('carbonate-anion','protonated-monoethanolamine')]:
    identity = 'pair/'+'/'.join(pair)+'/k_ij'
    coordinates.append(dict(identity=identity, targets=[['k_ij',list(pair),1.]], origin=values[identity], scale=.01))
identity = 'component/carbonate-anion/segment_diameter'
sigma = values[identity]
coordinates.append(dict(identity=identity, targets=[[k,'carbonate-anion',values['component/carbonate-anion/'+k]/sigma]
    for k in ('segment_diameter','packing_diameter','debye_huckel_diameter')], origin=sigma, scale=.01))
for q in coordinates:
    delta = math.log(10) if q.get('kind')=='reaction_coordinate' else .2 if q['identity']==identity else .1
    q['bounds'] = [q['origin']-delta, q['origin']+delta]
(OUT/'inputs.json').write_text(json.dumps(jsonable(dict(reconciliation=reconciliation, sources=sources, source_rows=source_rows,
    records=records, problems=problems, coordinates=coordinates)), indent=2, allow_nan=False)+'\n')
print('materialized', len(records), 'comparison observations;', sum(r['added'] for r in records), 'added fit rows')
