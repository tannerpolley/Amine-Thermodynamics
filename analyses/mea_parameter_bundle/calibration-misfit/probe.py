"""Solve packet states at the adopted record, optionally with named parameter overrides.

Usage: probe.py OUT.jsonl [identity-substring ...] [identity=value ...]
Writes one JSON line per state: identity, status, predictions, liquid composition.
Perturbed solves warm-start from the adopted solution of the same state.
Run single-threaded; the solve cache lives in /tmp.
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
shared.RUNS = Path('/tmp/mea-calibration-misfit-cache')
OBSERVATIONS = shared.load_state_packet()['observations']


def _canonical_pressure_observations():
    """The 161 active 30 wt% pCO2 rows (six sources), built as generate_figure_data.py builds them:
    the nearest-loading packet pressure request at the same temperature with the CO2 feed replaced."""
    templates = {}
    for o in OBSERVATIONS:
        if o['request']['pressure']['role'] == 'solved':
            t = round(o['request']['temperature']['value'] - 273.15)
            templates.setdefault(t, []).append((o['request']['reaction_system']['feed_amounts_mol'][0], o['request']))
    out = []
    with shared.CANONICAL_VLE.open(newline='', encoding='utf-8') as h:
        for row in csv.DictReader(h):
            if row['active_view_member'] != 'yes':
                continue
            t, loading = round(float(row['temperature_canonical_C'])), float(row['CO2_loading'])
            request = copy.deepcopy(min(templates[t], key=lambda c: abs(c[0] - loading))[1])
            system = request['reaction_system']
            system['feed_amounts_mol'][0] = loading
            system['conserved_totals'] = [math.fsum(c * a for c, a in zip(b, system['feed_amounts_mol'], strict=True))
                                          for b in system['balance_matrix']]
            out.append({'identity': 'canonical:' + row['observation_id'], 'request': request, 'targets': [{
                'identity': row['observation_id'] + '-pco2', 'observed': float(row['CO2_pressure']) * 1000.0,
                'basis': 'true-species-vapor-partial-pressure', 'source_identity': row['source_key'],
                'prediction_identity': 'co2-partial-pressure', 'scale': None}]})
    return out


CANONICAL = _canonical_pressure_observations()
_BASE = {}


def _base_model():
    if 'model' not in _BASE:
        _BASE['model'] = epcsaft.Mixture(shared.load_parameters())
    return _BASE['model']


def evaluate(sets=None, filters=(), canonical=False):
    """Yield one record per state matching ``filters`` at the adopted record plus ``sets``.

    States are the packet observations, or with ``canonical`` the 161 six-source pCO2 rows."""
    sets = dict(sets or {})
    reactions = shared._selected_reactions()
    reactions.update({k: v for k, v in sets.items() if k.startswith('reaction:')})
    eos = {k: v for k, v in sets.items() if not k.startswith('reaction:')}
    mapping = shared.with_parameter_values(shared.parameter_mapping(), eos) if eos else shared.parameter_mapping()
    model = epcsaft.Mixture(epcsaft.Parameters.from_mapping(mapping)) if eos else _base_model()
    fp = shared.parameter_fingerprint(mapping)
    for o in (CANONICAL if canonical else OBSERVATIONS):
        ident = o['identity']
        if filters and not any(f in ident for f in filters):
            continue
        t0 = time.perf_counter()
        anchors = []
        if sets:
            b = shared.evaluate_state(_base_model(), o['request'], shared._selected_reactions(), ident, [], budget_s=90)
            anchors = [a for a in [shared.anchor_from(b)] if a]
        r = shared.evaluate_state(model, o['request'], reactions, ident, anchors, budget_s=90, model_fingerprint=fp)
        liq = next((p for p in r.get('phases') or [] if p.get('role') == 'liquid'), None)
        yield {'identity': ident, 'status': r['status'], 'predictions': r['predictions'],
               'liquid': liq, 'wall_s': time.perf_counter() - t0, 'sets': sets,
               'wheel': shared.ENGINE_WHEEL_SHA256, 'T': o['request']['temperature']['value'],
               'feed': o['request']['reaction_system']['feed_amounts_mol'],
               'targets': [{k: t[k] for k in ('identity', 'observed', 'basis', 'source_identity',
                                              'prediction_identity', 'scale') if k in t} for t in o['targets']]}


def main(argv):
    out, rest = Path(argv[0]), argv[1:]
    sets = {k: float(v) for k, v in (a.split('=') for a in rest if '=' in a)}
    filters = [a for a in rest if '=' not in a and a != '--canonical']
    with out.open('a') as h:
        for rec in evaluate(sets, filters, canonical='--canonical' in rest):
            h.write(json.dumps(rec) + '\n')
            h.flush()
            print(rec['identity'], rec['status'], round(rec['wall_s'], 1), flush=True)


if __name__ == '__main__':
    main(sys.argv[1:])
