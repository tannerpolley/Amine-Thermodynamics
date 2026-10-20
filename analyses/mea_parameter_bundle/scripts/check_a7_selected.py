"""Reproduce 153 retained A7 quantities through the default parameter path (#196)."""
import csv
import hashlib
import json
import math
from pathlib import Path

import fit_observations as fo
import heat_evidence_170 as he
import shared_evaluation as s

ROOT = Path(__file__).resolve().parents[3]
BASE = ROOT / 'analyses/mea_parameter_bundle/results/joint-recalibration-170/amendment-7'
OUT = ROOT / 'analyses/mea_parameter_bundle/results/a7-paper-evidence/default-replay'


def main():
    endpoint = BASE / 'restricted-2/fit/usable-budget-endpoint.json'
    assert s.PARAMETERS.read_bytes() == endpoint.read_bytes()
    assert s.sha256(endpoint) == 'e234e8601ebc47b3dec25383ee0a0a8029cabb9f7f92c87866f595c505c7e58e'
    s.verify_wheel()
    spec = fo.load(BASE / 'restricted-2/fit-spec.json')
    mapping = s.parameter_mapping()
    inputs = [s.PARAMETERS, endpoint, BASE / 'restricted-2/fit-spec.json', Path(__file__),
              ROOT / spec['engine']['wheel_path']]
    inputs += [ROOT / spec[k] for k in ('packet_path', 'anchors_path', 'heat_rows_path')]
    inputs += [ROOT / d['table'] for d in spec['observations']]
    inputs += [ROOT / v['path'] for v in spec['inputs']]
    for bound in spec['inputs']:
        assert hashlib.sha256((ROOT / bound['path']).read_bytes()).hexdigest() == bound['sha256']
    reference = {}
    for filename, identity, field, factor, unit in (
        ('state-targets.csv', 'target', 'predicted', 1., 'Pa or mole fraction'),
        ('heats.csv', 'id', 'predicted_kJ_mol', 1000., 'J/mol CO2'),
        ('cp.csv', 'id', 'equilibrium_cp_kJ_kg_K', 1., 'kJ/(kg K)')):
        path = BASE / 'selected-assessment' / filename
        inputs.append(path)
        for row in csv.DictReader(path.open()):
            if filename != 'state-targets.csv' or row['kind'] == 'packet':
                assert row[identity] not in reference
                reference[row[identity]] = (float(row[field]) * factor, unit)
    _, rows = fo.rows_for(spec, mapping, 'base')
    values = fo.replay(mapping, rows)
    assert len(values) == 149 and all(r['status'] == 'Available' for r in values)
    masses = {c['component_id']: c['fixed']['molar_mass']['value']['magnitude'] for c in mapping['components']}
    for row in spec['direct_rows']:
        if row['quantity'] != 'equilibrium_isobaric_heat_capacity':
            continue
        value = he.cp_check(mapping, row['T_K'], row['source_loading'], row['source_observed_kJ_kg_K'], row=row)
        feed = row['analytical_feed']
        mass = sum(n * masses[c] for c, n in feed.items())
        helper_mass = sum(feed.get(c, 0) * m for c, m in zip(s.COMPONENT_IDS, he.hc.MOLAR_MASS, strict=True)) / 1000
        values.append(dict(target=row['id'], predicted=value['equilibrium_cp_kJ_kg_K'] * helper_mass / mass,
                           status='Available', analytical_feed=feed, pressure_Pa=row['P_Pa'], mass_kg=mass))
    comparisons = []
    for row in values:
        new, (old, unit) = row['predicted'], reference[row['target']]
        relative = abs(new - old) / max(abs(new), abs(old), 1e-300)
        comparisons.append(dict(target=row['target'], unit=unit, new=new, reference=old, relative_difference=relative))
    OUT.mkdir(parents=True, exist_ok=True)
    s.write_json(OUT / 'predictions.json', values)
    s.write_json(OUT / 'comparison.json', comparisons)
    s.write_json(OUT / 'input-hashes.json', {str(p.relative_to(ROOT)): hashlib.sha256(p.read_bytes()).hexdigest() for p in inputs})
    worst = max(r['relative_difference'] for r in comparisons)
    s.write_json(OUT / 'summary.json', dict(identities=len({r['target'] for r in comparisons}), worst_relative_difference=worst,
        tolerance=1e-10, engine_wheel_sha256=s.ENGINE_WHEEL_SHA256, engine_commit=s.ENGINE_COMMIT))
    assert len(comparisons) == len({r['target'] for r in comparisons}) == 153
    assert all(math.isfinite(r['new']) and math.isfinite(r['reference']) for r in comparisons) and worst <= 1e-10
    print(f'153 identities; worst relative difference {worst:.17g}')


if __name__ == '__main__':
    main()
