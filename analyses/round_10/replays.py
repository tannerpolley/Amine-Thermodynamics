"""Replay outside-objective observations at retained #440 endpoints."""
# ruff: noqa: E402
import argparse
from ast import literal_eval
from pathlib import Path
import sys
from time import monotonic

from handoff import ENDPOINTS, WHEEL

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent / 'fixed_reaction_reference'))

from refit import MEA, P_REF, a, fingerprint, r, save
from phase_replays import point_for
from property_replays import fixed_native_reference
import mea_pressure


def compact(row):
    return {k: row[k] for k in ('identity', 'group', 'observed', 'unit', 'status', 'value', 'message') if k in row}


def mea_pressures(spec):
    canonical, wagner = mea_pressure.requests()
    population = mea_pressure.membership()
    templates = mea_pressure.pressure_template(spec)
    fitted = {q['identity'] for q in templates}
    records = []
    for group, requests in (('canonical', {k: canonical[k] for k in population if k not in fitted}),
                            ('Wagner', wagner)):
        records += [mea_pressure.pressure_record(spec, templates[0], k, q, group=group) for k, q in requests.items()]
    template = next(iter(canonical.values()))['request']
    for row in mea_pressure.off_window_population():
        request = r.s.source_feed_request(template, row)
        records.append(mea_pressure.pressure_record(spec, templates[0], 'off-window:'+row['observation_id'],
            dict(request=request, targets=[dict(source_identity=row['source_key'], observed=float(row['CO2_pressure'])*1000)]),
            group='off-window'))
    for record, row in zip(records, r.d.evaluate(spec, records), strict=True):
        source = population.get(row['identity'], row['row']['source_coordinates'])
        yield dict(compact(row), source=source.get('source_key', row['row']['source']),
                   T_K=spec.problems[record['problem']].T)


def mea_heats(spec, point, work):
    from fit_observations import heat_items
    from part_ii import reg
    import reference_states_428 as reference
    import stripper_temperature_409 as heat

    mapping = work / 'endpoint.json'
    save(mapping, point['parameters'])
    with fixed_native_reference():
        heat.replay(r.ROOT, mapping, r.s.sha256(mapping), work, work, control=False, kim_2007=True,
                    producer_sha=r.s.sha256(r.B/'scripts/kim2007_heat_pathways.py'))
        arcis = [literal_eval(q['source_row']) for q in heat.rows(MEA.parent/'evidence/F4/heat.csv')
                 if q['source'] == 'Arcis2011']
        items = heat_items(point['parameters'], spec.parameters, arcis, reference.request(point['parameters'], 322.5, .11))
        for row, item in zip(arcis, items, strict=True):
            pred = reg.predict(spec.model, item)
            yield dict(identity=row['record_id'], group='Arcis2011', T_K=float(row['temperature_K']), unit='kJ/mol CO2',
                       observed=-row['observed_addition_enthalpy_J_per_mol_CO2']/1000,
                       value=-pred.value/1000 if pred.status.name == 'Available' else None,
                       status=pred.status.name, message=pred.message)
    for row in r.read(work/'heat-replay.json')['rows']:
        yield dict(identity=row['record_id'], group=row['source'], T_K=row['T_K'], unit='kJ/mol CO2',
                   observed=row['observed_kJ_mol'], value=row['predicted_kJ_mol'], status=row['status'])
    for row in heat.rows(work/'kim2007-heat-pathways/kim-heat.csv'):
        flagged = row['source_inconsistent'] == 'True' or row['first_120'] == 'True'
        yield dict(identity=row['record_id'], group='Kim2007 flagged' if flagged else 'Kim2007',
                   T_K=float(row['T_K']), unit='kJ/mol CO2', observed=float(row['observed']),
                   value=float(row['predicted']) if row['interval_status'] == 'available' else None,
                   status=row['interval_status'])


def receiver_rows(spec, design):
    for role in ('fitted', 'comparisons'):
        records = spec.inputs['observations'][role]
        for record in records:
            group = record['group']
            unit = record['unit'] or ''
            # Kuranov and Carson are objective rows in the pressure-weighted MDEA fit.
            if (role == 'comparisons' and (unit == 'Pa' or unit.startswith('J/mol') and 'K)' not in unit)
                    or design == 'MDEA' and group in ('Kuranov', 'Carson')):
                problem = spec.problems[record.get('problem', record.get('initial'))]
                yield dict(compact(spec.prediction(record)), role=record['role'], T_K=problem.T)


def main(design, label):
    a.study.reuse.bind_wheel()
    assert r.SHA == WHEEL
    r.verify()
    started = monotonic()
    run, point = point_for(design, label, 'round-10-replay')
    spec = run.bind(point)
    assert all(rx.reference.reference_pressure_pa == P_REF for p in spec.problems.values() for rx in p.reactions)
    if design == 'MEA':
        rows = list(mea_pressures(spec))
        rows.extend(mea_heats(spec, point, r.ROOT/'build/round-10'/label))
    else:
        rows = list(receiver_rows(spec, design))
    assert len({row['identity'] for row in rows}) == len(rows)
    save(HERE/'results'/f'{design}-{label}.json.gz',
         dict(wheel=r.SHA, endpoint_fingerprint=fingerprint(point), reference_pressure_Pa=P_REF,
              seconds=monotonic()-started, rows=rows))
    print(design, label, len(rows), 'rows;', round(monotonic()-started, 2), 's', flush=True)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('amine', choices=ENDPOINTS)
    parser.add_argument('endpoint')
    args = parser.parse_args()
    assert args.endpoint in ENDPOINTS[args.amine]
    main(args.amine, args.endpoint)
