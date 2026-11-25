"""Run the Q7 state order against the expanded AMP endpoints."""
from pathlib import Path
from tempfile import TemporaryDirectory
from time import monotonic
import copy
import hashlib
import json

from amp import DECLARATION, ENDPOINTS, ORIGINAL, Q7
from common import ROOT, RESULTS, fingerprints, save
from part_ii import Route, eq, stable
from refit_404 import TRIAL_SHA, trial_bank
from classify_descents import classify
from phases import fixed

AMP_REFERENCE = ROOT / 'analyses/mea_parameter_bundle/results/reference-states-428/amp.json'


def bank_hash(bank):
    return hashlib.sha256((json.dumps(bank, indent=2) + '\n').encode()).hexdigest()


def classification(route, point, rows, states):
    details = classify(route, point, rows, states)
    confirmed = [r['key'] for r in details if any(a['confirmed'] for a in r['attempts'])]
    unresolved = [r['key'] for r in details if r['key'] not in confirmed and
                  (r.get('liquid_directed') or r.get('classification_error') or
                   r['native_branch'] in ('unresolved', 'liquid', 'mixed') or
                   r['supplied_branch'] in ('unresolved', 'liquid', 'mixed'))]
    return dict(rows=details, confirmed=confirmed, unresolved=unresolved,
                vapor_directed=[r['key'] for r in details if r['key'] not in confirmed + unresolved])


def expanded_search(work, route, points, states, bank):
    positive = {r['key'] for r in stable.read(Q7) if r['outcome'] == 'resolved descent'}
    spec = route.bind(points['original-main'])
    # Select hot and cool rows from both archived search outcomes before seeing new TPDs.
    by_case = {}
    for state in states:
        T = route.temperature(spec, state)
        by_case.setdefault((state['key'] in positive, T >= 373., 'problem' in state), state)
    pilot = list(by_case.values())
    for label in ('free', 'fixed'):
        point = points['expanded-' + label]
        for protocol in ('native', 'supplied'):
            started = monotonic()
            record_path = f'A/search-{label}-{protocol}'
            for name, subset in (('pilot', pilot), ('full', states)):
                sample_start = monotonic()
                run = Route(DECLARATION, work / label / protocol / name)
                if protocol == 'supplied':
                    run.write('split-record.json', copy.deepcopy(bank))
                    initial = bank_hash(run.result('split-record.json'))
                    assert initial == TRIAL_SHA
                    rows = run.grid(point, subset)
                    final_bank = run.result('split-record.json')
                    final = bank_hash(final_bank)
                    bank_record = ('A/search-free-supplied-full-final-bank.json.gz' if final == TRIAL_SHA
                                   else f'A/supplied-final-bank-{final}.json.gz')
                    if not (RESULTS / bank_record).is_file():
                        save(bank_record, final_bank)
                else:
                    initial = final = None
                    rows = run.grid(point, subset, trial_set=[])
                search_seconds = monotonic() - sample_start
                save(f'{record_path}-{name}-rows.json.gz', dict(rows=rows, search_seconds=search_seconds,
                     initial_bank_sha256=initial, final_bank_sha256=final))
                detail = classification(run, point, rows, subset)
                seconds = monotonic() - sample_start
                tally = stable.tally(rows)
                save(f'{record_path}-{name}.json.gz', dict(attempted=len(subset), completed=sum(bool(r.get('completed')) for r in rows),
                     tally=tally, classification=detail, search_seconds=search_seconds,
                     classification_seconds=seconds-search_seconds), start=started)


def common_pressure(route, points):
    started = monotonic()
    reference = stable.read(AMP_REFERENCE)
    stock = {c: n for c, n in zip(reference['species'], reference['feed_mol'], strict=True) if n and c != 'carbon-dioxide'}
    state = dict(T=reference['T_K'], stock=stock, a=reference['loading'])
    specs = {label: route.bind(point) for label, point in points.items()}
    bubbles = {}
    for label, spec in specs.items():
        item = route.stability_row(spec, state, 1.)
        solved = eq.solve_equilibrium(spec.model, item.pressure_reference)
        bubbles[label] = dict(status=solved.requested_tolerance_met, pressure_Pa=solved.pressure if solved.requested_tolerance_met else None,
                              message=solved.message)
    values = [b['pressure_Pa'] for b in bubbles.values() if b['pressure_Pa'] is not None]
    pressure = 1.05 * max(values) if values else None
    outcomes = {}
    for label, spec in specs.items():
        if pressure is None:
            break
        try:
            record = fixed(route, spec, state, pressure, dict(pair=reference['split']))
            record['minimum_by_density_side'] = {
                str(side): min((t['quantities']['tpd_over_rt'] for t in record['native_trials']
                                if t['quantities'].get('density_side') == side and 'tpd_over_rt' in t['quantities']), default=None)
                for side in (1, 2)}
            outcomes[label] = record
        except (RuntimeError, ValueError, AssertionError) as error:
            outcomes[label] = dict(refusal=f'{type(error).__name__}: {error}')
    save('A/common-pressure.json.gz', dict(bubbles=bubbles, common_Pa=pressure, outcomes=outcomes,
         margins_Pa={label: pressure - b['pressure_Pa'] if b['pressure_Pa'] is not None else None for label, b in bubbles.items()},
         inputs=fingerprints(AMP_REFERENCE)), start=started)


def calculate(work):
    started = monotonic()
    route = Route(DECLARATION, work / 'reference')
    point_paths = {**{f'original-{label}': ENDPOINTS / label / 'parameters.json' for label in ORIGINAL},
                   **{f'expanded-{label}': RESULTS / f'A/expanded-{label}.json.gz' for label in ('free', 'fixed')}}
    points = {label: stable.read(p) for label, p in point_paths.items()}
    points = {label: p['point'] if label.startswith('expanded') else p for label, p in points.items()}
    states = route.states(route.bind(points['original-main']))
    original_search = ENDPOINTS / 'main/search-1.json.gz'
    original_fixed_search = ENDPOINTS / 'slope-150/search-1.json.gz'
    original_classification = ENDPOINTS / 'main/phase-classification-1.json.gz'
    assert [s['key'] for s in states] == [r['key'] for r in stable.read(original_search)] and len(states) == 666
    bank = trial_bank(route)
    q7 = stable.read(Q7)
    old_classes = stable.read(original_classification)
    save('A/phase-controls.json.gz', dict(states=states, bank_sha256=bank_hash(bank), starting_trials=len(bank['trials']),
         original_free=dict(descents=[r['key'] for r in q7 if r['outcome'] == 'resolved descent'],
                            confirmed=[r['key'] for r in old_classes['states'] if any(a['confirmed'] for a in r['attempts'])]),
         original_fixed=stable.tally(stable.read(original_fixed_search)),
         inputs=fingerprints(Q7, DECLARATION, original_search, original_fixed_search, original_classification, *point_paths.values())))
    common_pressure(route, points)
    expanded_search(work, route, points, states, bank)
    save('A/phase-timing.json', dict(projection_minutes=[7, 11]), start=started)


if __name__ == '__main__':
    with TemporaryDirectory() as directory:
        calculate(Path(directory))
