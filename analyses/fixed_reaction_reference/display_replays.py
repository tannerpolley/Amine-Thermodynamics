"""Replay only missing fixed-reference inputs to the manuscript displays."""
from ast import literal_eval
from csv import DictReader
import sys
from time import monotonic
from unittest.mock import patch

from refit import P_REF, WORK, a, fingerprint, put, r, save
from phase_replays import point_for
from property_replays import fixed_native_reference
import mea_pressure
import paper_evidence_341 as evidence


def comparisons(run, point, mapping):
    from carbonate_ions_282 import CARBONATE_IDS, pool_and_shares
    import density_268 as density
    from stripper_temperature_409 import load, replay

    started = monotonic()
    spec = run.bind(point)
    density_data = density.evaluate(spec, density.density_records(spec, density.density_rows()))
    capacity = load('capacity_264', r.B/'heat-capacity-264/calculate.py', [])
    with patch.object(capacity, 'SolventSpecification', lambda _: run.bind(point)):
        capacity_spec, _, broad, _ = capacity.setup()
    cp = []
    for row, pred in zip(broad, capacity.evaluate(capacity_spec, broad), strict=True):
        measured = row['row']
        value = pred.get('value')
        cp.append(dict(pred, source=measured['source'], T_K=float(measured['T_K']), loading=float(measured['loading']),
                       observed_kJ_kg_K=float(measured['cp_kJ_kg_K']),
                       predicted_kJ_kg_K=value*row['feed_amount_mol']/row['feed_mass_kg']/1000 if value is not None else None))
    carbonate_spec = run.bind(point)
    with patch.object(r, 'bind', lambda _: carbonate_spec):
        carbonate = pool_and_shares(point['parameters'], parents=dict.fromkeys(CARBONATE_IDS))
    work = mapping.parent
    evidence = work/'evidence'
    source = r.B/'scripts/kim2007_heat_pathways.py'
    # Add only Kim 2007 to the finite-interval calculation. Its other two
    # sources were already retained by #440.
    from stripper_temperature_409 import KIM2014, VINJARAPU2024
    from stripper_temperature_409 import rows as source_rows
    with (fixed_native_reference(),
          patch('stripper_temperature_409.rows', lambda path: [] if path in
                (r.ROOT/KIM2014, r.ROOT/VINJARAPU2024) else source_rows(path))):
        replay(r.ROOT, mapping, r.s.sha256(mapping), evidence, work/'heat',
               control=False, kim_2007=True, producer_sha=r.s.sha256(source))
    with (evidence/'kim2007-heat-pathways/kim-heat.csv').open() as stream:
        kim = list(DictReader(stream))
    put('display-replays/mea-comparisons.json.gz', dict(wheel=r.SHA, endpoint_fingerprint=fingerprint(point),
        reference_pressure_pa=P_REF, density=density_data, heat_capacity=cp, carbonate_share=carbonate,
        kim_2007=kim, seconds=monotonic()-started))
    for name, rows in [('density', density_data), ('heat capacity', cp), ('carbonate', carbonate), ('Kim 2007', kim)]:
        print(name, sum(q.get('status', q.get('interval_status', '')).lower() == 'available' for q in rows), '/', len(rows))


def caloric_and_species(run, point, mapping):
    from fit_observations import heat_items
    import final_evidence as source
    import reference_states_428 as reference
    from part_ii import reg

    started = monotonic()
    spec = run.bind(point)
    old = r.B/'results/salt-anchored-435/MEA/evidence/F4'
    with (old/'heat.csv').open() as stream:
        arcis = [literal_eval(q['source_row']) for q in DictReader(stream) if q['source'] == 'Arcis2011']
    with fixed_native_reference():
        items = heat_items(point['parameters'], spec.parameters, arcis, reference.request(point['parameters'], 322.5, .11))
        heating = []
        for row, item in zip(arcis, items, strict=True):
            result = reg.predict(spec.model, item)
            heating.append(dict(identity=row['record_id'], observed=row['observed_addition_enthalpy_J_per_mol_CO2']/1000,
                                predicted=result.value/1000 if result.status.name == 'Available' else None,
                                status=result.status.name, message=result.message))
        worked = reference.mea(mapping, reaction_reference_pressure_pa=P_REF)
        _, observations = source.observations()
        with (old/'species-figure-data.csv').open() as stream:
            targets = {q['target'] for q in DictReader(stream)}
        fitted = {q['identity']: q for q in r.read(r.ROOT/'analyses/fixed_reaction_reference/results/MEA/A.json.gz')['replay']['rows']}
        species = [dict(identity=key, observed=fitted[key]['observed'],
                        predicted=fitted[key]['value'], status=fitted[key]['status'])
                   for key in sorted(targets & fitted.keys())]
        pending = targets - fitted.keys()
        for row in observations['packet']:
            keep = pending & {q['identity'] for q in row['targets']}
            if keep:
                try:
                    record, _ = source.job('Selected', mapping, 'packet', row, output_dir=mapping.parent)
                    species.extend(dict(q, identity=q['target'], status='Available')
                                   for q in source.score_rows('Selected', [record]) if q['target'] in keep)
                except (RuntimeError, ValueError) as error:
                    species.extend(dict(identity=q['identity'], observed=q['observed'], predicted=None,
                                        status='Unavailable', message=str(error))
                                   for q in row['targets'] if q['identity'] in keep)
    assert {q['identity'] for q in species} == targets and len(species) == len(targets)
    put('display-replays/caloric-and-species.json.gz', dict(wheel=r.SHA, endpoint_fingerprint=fingerprint(point),
        reference_pressure_pa=P_REF, arcis=heating, reference_state=worked, species=species, seconds=monotonic()-started))
    print('Arcis', sum(q['status'] == 'Available' for q in heating), '/', len(heating),
          'species', sum(q['status'] == 'Available' for q in species), '/', len(species), 'caloric checks', worked['checks'])


def mdea_onset():
    from binary_tpd_421 import PRESSURES, binary_model, bracket_onset, k_at

    _, point = point_for('MDEA', 'selected', 'display-replay')
    started = monotonic()
    model = binary_model(point['parameters'])
    pressures = {}
    for pressure in PRESSURES:
        rows, brackets = bracket_onset(model, pressure)
        pressures[str(int(pressure))] = dict(rows=list(rows.values()), brackets=brackets)
    put('display-replays/mdea-binary-onset.json.gz', dict(wheel=r.SHA,
        endpoint_fingerprint=fingerprint(point), k_at_423_K=k_at(point['parameters'], 423.),
        pressures=pressures, seconds=monotonic()-started))
    print({pressure: result['brackets'] for pressure, result in pressures.items()})



def receiver_comparisons():
    import lawson_methane

    run, point = point_for('DEA', 'selected', 'methane-display-replay')
    result = {}
    with (patch.object(lawson_methane, 'Route', lambda *_: run),
          patch.object(lawson_methane, 'save', result.__setitem__)):
        lawson_methane.methane(point, r.ROOT/'analyses/fixed_reaction_reference/results/DEA/A.json.gz', 'refit')
    methane, = result.values()
    put('display-replays/dea-methane.json.gz', dict(methane, wheel=r.SHA,
        endpoint_fingerprint=fingerprint(point), reference_pressure_pa=P_REF))
    print('DEA methane', sum('pCO2_change_Pa' in q for q in methane['rows']), '/', len(methane['rows']))

    for name in ('AMP_free', 'AMP_fixed'):
        started = monotonic()
        run, point = point_for(name, 'selected', 'bubble-display-replay')
        retained = r.read(r.ROOT/f'analyses/fixed_reaction_reference/results/{name}/controls/A.json.gz')
        assert retained['endpoint_fingerprint'] == fingerprint(point)
        state = retained['rows']['worked-state']['state']
        spec = run.bind(point)
        item = run.stability_row(spec, state, 1.)
        assert all(rx.reference.reference_pressure_pa == P_REF for rx in item.pressure_reference.reactions)
        bubble = r.eq.solve_equilibrium(spec.model, item.pressure_reference)
        put(f'display-replays/{name}-bubble.json.gz', dict(wheel=r.SHA, endpoint_fingerprint=fingerprint(point),
            reference_pressure_pa=P_REF, state=state,
            pressure_Pa=bubble.pressure if bubble.requested_tolerance_met else None,
            status=bubble.message, seconds=monotonic()-started))
        print(name, bubble.pressure, bubble.message)



def main():
    a.study.reuse.bind_wheel()
    if sys.argv[1:] == ['receivers']:
        receiver_comparisons()
        return
    if sys.argv[1:] == ['mdea-onset']:
        mdea_onset()
        return
    run, point = point_for('MEA', 'selected', 'display-replay')
    if len(sys.argv) > 1 and sys.argv[1] == 'caloric-and-species':
        mapping = WORK/'MEA/display-replay/parameters.json'
        save(mapping, point['parameters'])
        caloric_and_species(run, point, mapping)
        return
    spec = run.bind(point)
    template = mea_pressure.pressure_template(spec)[0]
    _, requests = mea_pressure.requests()
    started = monotonic()
    cooler = [mea_pressure.pressure_record(spec, template, key, request, group='Wagner comparison')
              for key, request in requests.items() if request['request']['temperature']['value'] < 370.]
    assert len(cooler) == 11
    wagner = r.d.evaluate(spec, cooler)
    put('display-replays/wagner.json.gz', dict(wheel=r.SHA, endpoint_fingerprint=fingerprint(point),
        reference_pressure_pa=P_REF, rows=wagner, seconds=monotonic()-started))
    started = monotonic()
    mapping = WORK/'MEA/display-replay/parameters.json'
    save(mapping, point['parameters'])
    # Keep the three original feeds and both pressure guesses. Capture the
    # producer's readbacks even when its ten-digit agreement check fails.
    result = {}
    failure = None
    with (fixed_native_reference(), patch.object(evidence, 'RECORD', mapping),
          patch.object(evidence.a, 'write', result.__setitem__)):
        try:
            evidence.checks()
        except (RuntimeError, ValueError, AssertionError) as error:
            failure = f'{type(error).__name__}: {error}'
    checks = result.get('check-values.json', [])
    put('display-replays/bubble-checks.json.gz', dict(wheel=r.SHA, endpoint_fingerprint=fingerprint(point),
        reference_pressure_pa=P_REF, rows=checks, failure=failure, seconds=monotonic()-started))
    comparisons(run, point, mapping)
    print(f'Wagner {sum(q["status"] == "Available" for q in wagner)}/{len(wagner)}; '
          f'bubble checks {sum(q["printed_digits_agree"] for q in checks)}/3; {failure or "agreement"}')


if __name__ == '__main__':
    main()
