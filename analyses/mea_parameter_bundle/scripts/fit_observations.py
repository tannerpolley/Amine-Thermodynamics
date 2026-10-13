"""Declared MEA pressure, species and integral-heat observations (#179)."""
import json
import math
import os
from pathlib import Path

for key in ('OMP_NUM_THREADS', 'OPENBLAS_NUM_THREADS', 'MKL_NUM_THREADS'):
    os.environ[key] = '1'
import epcsaft
from epcsaft import equilibrium as eq, regression as reg
import shared_evaluation as s
import verify_reference_calorics as thermal

ROOT = Path(__file__).resolve().parents[3]


def load(path):
    return json.loads((ROOT / path).read_text())


def indexed(rows, key):
    result = {r[key]: r for r in rows}
    if len(result) != len(rows):
        raise ValueError(f'duplicate {key}')
    return result


def heat_items(mapping, params, sources, request):
    request = s.corrected_request(request, s.reaction_values(mapping))
    reactions = s._problem_from_request(request).reactions
    masses = {c['component_id']: c['fixed']['molar_mass']['value']['magnitude'] for c in mapping['components']}
    solvent = {'monoethanolamine': 1., 'water': masses['monoethanolamine']*.7/(.3*masses['water'])}
    items = []
    for row in sources:
        T, P, alpha = row['temperature_K'], row['system_pressure_Pa'], row['alpha_final']
        initial, final = [eq.Problem(T=T, P=P, feed=eq.Amounts({**solvent, 'carbon-dioxide': a}),
            phases=[eq.Phase('L', kind='liquid', support=s.COMPONENT_IDS)], reactions=reactions,
            neutral_reference=s._neutral_reference(request)) for a in (0., alpha)]
        items.append(reg.addition_enthalpy(params, initial, final, {'carbon-dioxide': 1.}, alpha,
            T, P, phase='vapor', observed=row['observed_addition_enthalpy_J_per_mol_CO2'],
            form='difference', scale=row['uH_J_per_mol_CO2']))
    return items


def rows_for(spec, mapping, observation_id):
    declaration = indexed(spec['observations'], 'id')[observation_id]
    ids = declaration['ordered_row_ids']
    if len(set(ids)) != len(ids):
        raise ValueError('duplicate observation IDs')
    frozen = indexed(load(declaration['table']), 'target')
    packet = s.load_state_packet(ROOT / spec['packet_path'])['observations']
    targets = indexed([dict(t, state=o) for o in packet for t in o['targets']], 'identity')
    anchors = indexed([json.loads(line) for line in (ROOT / spec['anchors_path']).open()], 'identity')
    sources = indexed(load(spec['heat_rows_path']), 'record_id')
    params = epcsaft.Parameters.from_mapping(mapping)
    template = next(o['request'] for o in packet if o['identity'] == 'Bottinger2008_state_046')
    from verify_temperature_reference import request_at
    heat_request = s.source_feed_request(template, dict(source_key='Amundsen2009', CO2_loading=.11,
        temperature_reported_C=40., MEA_weight_fraction=.30))
    heat_request = request_at(heat_request, 313.15, 101325., liquid_only=True)
    groups, rows = {}, []
    for identity, weight in zip(ids, declaration['weights'], strict=True):
        row = frozen[identity]
        if row['weight'] != weight:
            raise ValueError(f'{identity}: weight mismatch')
        if identity in sources:
            item = heat_items(mapping, params, [sources[identity]], heat_request)[0]
        else:
            target = targets[identity]
            o = target['state']
            if o['identity'] not in groups:
                request = s.corrected_request(o['request'], s.reaction_values(mapping))
                groups[o['identity']] = s._problem_from_request(request, s.anchor_from(anchors[o['identity']]))
            problem = groups[o['identity']]
            output = indexed(o['request']['outputs'], 'identity')[target['prediction_identity']]
            support = next(p.support for p in problem.phases if p.name == output['phase_identity']) or s.COMPONENT_IDS
            if any(c not in (0., 1.) for c in output['coefficients']):
                raise ValueError(f'{identity}: unsupported linear coefficients')
            species = (('bicarbonate-anion', 'carbonate-anion') if identity.startswith(('Matin','Bottinger'))
                and identity.endswith('::HCO3-') else tuple(c for c, v in zip(support, output['coefficients'], strict=True) if v))
            if target['observed'] != row['observed']:
                raise ValueError(f'{identity}: observed mismatch')
            item = reg.observation(params, 'partial_pressure' if row['form']=='LogRatio' else 'mole_fraction',
                problem, observed=row['observed'], form={'LogRatio':'log_ratio','Difference':'difference'}[row['form']],
                mass_basis=False, phase=output['phase_identity'], species=species,
                **({'scale':row['scale']} if row['form']=='Difference' else {}))
        if (item.observed, item.scale, item.form.name) != (row['observed'], row['scale'], row['form']):
            raise ValueError(f'{identity}: observation declaration mismatch')
        rows.append((identity, item, weight))
    return params, rows


def predict(mapping, items):
    model = epcsaft.Mixture(epcsaft.Parameters.from_mapping(mapping), thermochemistry=thermal.record())
    values = [reg.predict(model, item) for item in items]
    if any(v.status.name != 'Available' or not all(math.isfinite(x) for x in (v.value, v.residual)) for v in values):
        raise RuntimeError([(v.status.name, v.message, v.value, v.residual) for v in values
            if v.status.name != 'Available' or not all(math.isfinite(x) for x in (v.value, v.residual))])
    return values


def replay(mapping, rows):
    model = epcsaft.Mixture(epcsaft.Parameters.from_mapping(mapping), thermochemistry=thermal.record())
    result = []
    for identity, item, weight in rows:
        value = reg.predict(model, item)
        row = dict(target=identity, observed=item.observed, scale=item.scale, weight=weight, form=item.form.name,
            status=value.status.name, message=value.message, requested_tolerance_met=value.requested_tolerance_met,
            stable_root_count=value.stable_root_count)
        if hasattr(value, 'branch'):
            row.update(branch=None if value.branch is None else value.branch.name,
                convergence=None if value.convergence is None else {k:s._jsonable(getattr(value.convergence,k))
                    for k in ('residual','floor','amplification','contraction','iterations','stop')})
        if value.status.name == 'Available':
            r = math.sqrt(weight)*value.residual
            row.update(predicted=value.value, residual=value.residual, weighted_residual=r, cost=.5*r**2)
        result.append(row)
    return result


def replay_summary(values, heat_sources):
    heat_ids = {r['record_id'] for r in heat_sources}
    arcis_ids = {r['record_id'] for r in heat_sources if not r['record_id'].startswith('vinjarapu')}
    common = [r for r in values if r['target'] not in arcis_ids]
    if any(r['status'] != 'Available' for r in values):
        raise RuntimeError('unavailable replay observations; see predictions.json')
    score = dict(cost=math.fsum(r['cost'] for r in common), common149_cost=math.fsum(r['cost'] for r in common), scores={})
    for kind in ('pressure', 'species'):
        rr = [r for r in common if r['target'] not in heat_ids and r['target'].endswith('-pco2') == (kind=='pressure')]
        score['scores'][kind] = dict(n=len(rr), cost=math.fsum(.5*r['weighted_residual']**2 for r in rr),
            AARD_percent=100*math.fsum(abs(r['predicted']/r['observed']-1) for r in rr)/len(rr))
    for name, prefix in (('Vinjarapu','vinjarapu'),('Arcis','arcis')):
        rr = [r for r in values if (r['target'] in arcis_ids) == (name=='Arcis') and r['target'] in heat_ids]
        score[name+'_RMSE_kJ_mol'] = math.sqrt(math.fsum(((r['predicted']-r['observed'])/1000)**2 for r in rr)/len(rr))
    return score
