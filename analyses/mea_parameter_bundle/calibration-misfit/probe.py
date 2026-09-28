"""Solve packet states at the base record RECORD, optionally with named parameter overrides.

Usage: probe.py OUT.jsonl [--record=PATH] [--canonical] [identity-substring ...] [identity=value ...]
RECORD defaults to the pre-refit record on the Engine packet v5 association topology (candidate.py --packet-v5).
Writes one JSON line per state: identity, status, predictions, liquid composition, base record SHA-256.
Perturbed solves warm-start from the base-record solution of the same state.
Run single-threaded; the solve cache and logs live in results/runs/calibration-misfit (ignored).
"""
import copy
import csv
import json
import math
import sys
import time
from pathlib import Path

W = Path(__file__).resolve().parents[3]
sys.path[:0] = [str(W / 'analyses/mea_parameter_bundle/scripts'), str(W / 'src')]
import shared_evaluation as shared  # noqa: E402
import epcsaft  # noqa: E402

shared.verify_wheel()  # the pinned Engine wheel must be installed
SCRATCH = W / 'analyses/mea_parameter_bundle/results/runs/calibration-misfit'
shared.RUNS = SCRATCH / 'cache'
OBSERVATIONS = shared.load_state_packet()['observations']
RECORD = Path(__file__).with_name('pre-refit-packet-v5-parameters.json')


def pressure_observations(select):
    """pCO2 states for the canonical VLE rows accepted by ``select``, built as generate_figure_data.py
    builds them: the nearest-loading packet pressure request at the same temperature with the CO2 feed
    replaced. Water is rescaled to the row's MEA mass fraction (the packet requests are all 30 wt%)."""
    templates = {}
    for o in OBSERVATIONS:
        if o['request']['pressure']['role'] == 'solved':
            t = round(o['request']['temperature']['value'] - 273.15)
            templates.setdefault(t, []).append((o['request']['reaction_system']['feed_amounts_mol'][0], o['request']))
    out = []
    with shared.CANONICAL_VLE.open(newline='', encoding='utf-8') as h:
        for row in csv.DictReader(h):
            if not select(row):
                continue
            t = round(float(row['temperature_canonical_C'] or row['temperature_reported_C']))
            loading = float(row['CO2_loading'])
            request = copy.deepcopy(min(templates[t], key=lambda c: abs(c[0] - loading))[1])
            system = request['reaction_system']
            w = float(row['MEA_weight_fraction'])
            system['feed_amounts_mol'][0] = loading
            system['feed_amounts_mol'][2] *= (1 - w) / w / (0.7 / 0.3)  # the template is the 30 wt% solvent
            system['conserved_totals'] = [math.fsum(c * a for c, a in zip(b, system['feed_amounts_mol'], strict=True))
                                          for b in system['balance_matrix']]
            out.append({'identity': 'canonical:' + row['observation_id'], 'request': request, 'targets': [{
                'identity': row['observation_id'] + '-pco2', 'observed': float(row['CO2_pressure']) * 1000.0,
                'basis': 'true-species-vapor-partial-pressure', 'source_identity': row['source_key'],
                'prediction_identity': 'co2-partial-pressure', 'scale': None}]})
    return out


CANONICAL = pressure_observations(lambda row: row['active_view_member'] == 'yes')
_BASE = {}


def _base_model():
    """The RECORD model and its cache fingerprint (the evaluator's default key is the selected record)."""
    if 'model' not in _BASE:
        mapping = shared.parameter_mapping(RECORD)
        _BASE.update(model=epcsaft.Mixture(epcsaft.Parameters.from_mapping(mapping)),
                     fingerprint=shared.parameter_fingerprint(mapping))
    return _BASE['model']


def base_record(o):
    """The evaluator record of one state at RECORD; its liquid anchor warm-starts perturbed solves and declares fit states."""
    return shared.evaluate_state(_base_model(), o['request'], shared._selected_reactions(), o['identity'], [], budget_s=90,
                                 model_fingerprint=_BASE['fingerprint'])


SLOPE = '/k_ij/reciprocal_temperature_slope'


def with_values(mapping, values):
    """``shared.with_parameter_values`` that first adds any missing k_ij 1/T slope node (value 0, T_ref
    313.15 K), in the form the record already uses for the CO2-MEA pair."""
    mapping = copy.deepcopy(mapping)
    have = set(shared.parameter_values(mapping))
    for ident in values:
        if ident.endswith(SLOPE) and ident not in have:
            _, a, b, _, _ = ident.split('/')
            pair = next(p for p in mapping['pairs'] if {p['component_id_a'], p['component_id_b']} == {a, b})
            node = copy.deepcopy(next(c for p in mapping['pairs'] for c in p['coefficients']
                                      if c['family'] == 'k_ij_reciprocal_temperature_slope'))
            node.update({'identity': ident, 'value': {'magnitude': 0.0, 'unit': 'kelvin'}})
            node['provenance'] = {**node['provenance'], 'locator': 'calibration-misfit refit C: added 1/T slope'}
            pair['coefficients'].append(node)
    return shared.with_parameter_values(mapping, values)


def check(r):
    """Solver, balance and stationarity (reaction affinity and phase equality) status of one evaluator record."""
    evidence = dict(r.get('evidence') or [])
    return {'failure_code': r.get('failure_code', ''), 'solver_status': r.get('solver_status'),
            'tolerance_met': evidence.get('requested_tolerance_met'),
            'balance_errors': evidence.get('validation_errors', []),  # material/charge balance > 1e-7
            'max_abs_stationarity': (evidence.get('compiled_point_evaluation') or {}).get('raw_stationarity_max_abs')}


def evaluate(sets=None, filters=(), canonical=False, states=None):
    """Yield one record per state matching ``filters`` at RECORD plus ``sets``.

    States are ``states``, else the packet observations, or with ``canonical`` the 161 six-source pCO2 rows."""
    sets = dict(sets or {})
    reactions = shared._selected_reactions()
    reactions.update({k: v for k, v in sets.items() if k.startswith('reaction:')})
    eos = {k: v for k, v in sets.items() if not k.startswith('reaction:')}
    mapping = with_values(shared.parameter_mapping(RECORD), eos) if eos else shared.parameter_mapping(RECORD)
    model = epcsaft.Mixture(epcsaft.Parameters.from_mapping(mapping)) if eos else _base_model()
    fp = shared.parameter_fingerprint(mapping)
    _base_model()
    for o in states or (CANONICAL if canonical else OBSERVATIONS):
        ident = o['identity']
        if filters and not any(f in ident for f in filters):
            continue
        t0 = time.perf_counter()
        anchors = []
        if sets:
            anchors = [a for a in [shared.anchor_from(base_record(o))] if a]
        r = shared.evaluate_state(model, o['request'], reactions, ident, anchors, budget_s=90, model_fingerprint=fp)
        liq = next((p for p in r.get('phases') or [] if p.get('role') == 'liquid'), None)
        yield {'identity': ident, 'status': r['status'], 'predictions': r['predictions'], 'check': check(r),
               'liquid': liq, 'wall_s': time.perf_counter() - t0, 'sets': sets,
               'wheel': shared.ENGINE_WHEEL_SHA256, 'record_sha256': shared.sha256(RECORD),
               'T': o['request']['temperature']['value'],
               'feed': o['request']['reaction_system']['feed_amounts_mol'],
               'targets': [{k: t[k] for k in ('identity', 'observed', 'basis', 'source_identity',
                                              'prediction_identity', 'scale') if k in t} for t in o['targets']]}


def main(argv):
    global RECORD
    out, rest = Path(argv[0]), argv[1:]
    RECORD = Path(next((a.split('=', 1)[1] for a in rest if a.startswith('--record=')), RECORD))
    rest = [a for a in rest if not a.startswith('--record=')]
    sets = {k: float(v) for k, v in (a.split('=') for a in rest if '=' in a)}
    filters = [a for a in rest if '=' not in a and a != '--canonical']
    with out.open('a') as h:
        for rec in evaluate(sets, filters, canonical='--canonical' in rest):
            h.write(json.dumps(rec) + '\n')
            h.flush()
            print(rec['identity'], rec['status'], round(rec['wall_s'], 1), flush=True)


if __name__ == '__main__':
    main(sys.argv[1:])
