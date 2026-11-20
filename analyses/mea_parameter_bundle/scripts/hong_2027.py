"""Evaluate Hong's published 30 wt% MEA model on the frozen #246 observations."""
import sys
from collections import Counter
from pathlib import Path

from kim2007_heat_pathways import BUNDLE, CEILING, metrics, read

RESULTS = BUNDLE / 'results'
ADOPTED = RESULTS / 'paper-evidence-341/paper-evidence'
PUBLISHED = RESULTS / 'same-data-comparison/part1/published'
OUT = RESULTS / 'same-data-comparison/hong-2027'
EDGE_IDS = {f'vle_obs_{i:04d}-pco2' for i in (119, 121, 126, 128, 129, 130, 131, 133, 134, 137, 138, 139, 141)}
LOW_IDS = {f'vle_obs_{i:04d}-pco2' for i in (51, 60, 61, 62, 186, 194, 203, 204, 205, 214, 215, 224, 225, 226)}


def indexed(rows, key):
    index = {r[key]: r for r in rows}
    assert len(index) == len(rows), key
    return index


def comparison_rows():
    fitted = set(indexed(read(ADOPTED / 'fitted-rows.csv'), 'id'))
    result = []
    for filename, published, key, measured, predicted in (
        ('state-targets.csv', 'selected-assessment/state-targets.csv', 'target', 'observed', 'predicted'),
        ('density.csv', 'selected-assessment/density.csv', 'id', 'observed_kg_m3', 'predicted_kg_m3'),
        ('kim2007-heat-pathways/kim-heat.csv', 'kim2007-heat-pathways/kim-heat.csv', 'record_id', 'observed', 'predicted'),
    ):
        def selected(path):
            return [r for r in read(path) if key != 'target' or r['kind'] in ('canonical', 'wagner')]

        adopted, other = selected(ADOPTED / filename), indexed(selected(PUBLISHED / published), key)
        assert set(indexed(adopted, key)) == set(other)
        for row in adopted:
            identity = row[key]
            ref = other[identity]
            observed = float(row[measured])
            assert observed == float(ref[measured]), identity
            temperature = float(row.get('T_K', row.get('temperature_K')))
            loading = float(row['loading'])
            start = float(row.get('previous_loading', loading))
            mass_fraction = float(row.get('mea_mass_fraction', .30))
            block = row.get('kind', row['source'] if key == 'id' else f'Kim {temperature:.2f} K')
            edge = identity in EDGE_IDS
            strict = mass_fraction == .30 and .1 <= start <= loading <= 1 and 313.15 <= temperature <= 393.15
            within = strict or edge
            above_ceiling = key == 'record_id' and loading > CEILING
            if key == 'record_id':
                assert ref['interval_status'] == row['interval_status'] == ('above_ceiling' if above_ceiling else 'available')
            reason = ('Hilliard lower edge; 313.15 K weight' if edge else 'other MEA mass fraction' if mass_fraction != .30
                      else 'loading below 0.1' if start < .1 else 'temperature below 313.15 K' if temperature < 313.15
                      else 'above_ceiling in both comparison models' if above_ceiling else 'inside Hong grid')
            assert within or reason in ('other MEA mass fraction', 'loading below 0.1', 'temperature below 313.15 K'), identity
            result.append(dict(record_id=identity, block=block, source=row['source'], T_K=temperature, loading=loading,
                               previous_loading=start, mea_mass_fraction=mass_fraction, pressure_Pa=row.get('P_Pa', ''),
                               observed=observed, inside_hong_grid=strict, hilliard_edge=edge,
                               hong_eligible=within, three_model_eligible=within and not above_ceiling, reason=reason,
                               adopted_role='fitted' if identity in fitted else 'not fitted',
                               adopted=float(row[predicted]) if row[predicted] else None,
                               polley_hedengren_2026=float(ref[predicted]) if ref[predicted] else None))
    indexed(result, 'record_id')
    return result


def replay_comparison(rows):
    pressures = [r for r in rows if r['block'] == 'canonical']
    assert len(pressures) == 159
    values = {}
    for model, expected in [('adopted', 20.971795), ('polley_hedengren_2026', 52.341322)]:
        scored = metrics(pressures, predicted=model)
        assert scored['n'] == 159 and round(scored['aard_percent'], 6) == expected, scored
        values[model] = scored['aard_percent']
    return values


def freeze():
    rows = comparison_rows()
    print('Full 159-pressure replay:', replay_comparison(rows))
    assert {r['record_id'] for r in rows if r['hilliard_edge']} == EDGE_IDS
    assert {r['record_id'] for r in rows if r['block'] == 'canonical' and not r['hong_eligible']} == LOW_IDS
    kim = [r for r in rows if r['block'].startswith('Kim ')]
    assert len(kim) == 86 and sum(r['inside_hong_grid'] for r in kim) == 69
    assert Counter(r['block'] for r in rows if r['three_model_eligible']) == {
        'canonical': 145, 'wagner': 23, 'Kim 313.15 K': 21, 'Kim 353.15 K': 20, 'Kim 393.15 K': 15,
        'Amundsen2009': 18, 'Hartono2014': 25, 'Han2012': 45,
    }
    assert Counter(r['source'] for r in rows if r['block'] in ('canonical', 'wagner') and r['hong_eligible']) == {
        'Aronu2011': 32, 'Hilliard2008': 31, 'Idris2014': 10, 'Jou1995': 38, 'Mamun2005': 19, 'Xu2011': 15, 'Wagner2013': 23,
    }
    assert Counter(r['block'] for r in rows if r['three_model_eligible'] and r['adopted_role'] == 'fitted') == {
        'canonical': 45, 'Amundsen2009': 12, 'Hartono2014': 20,
    }
    from candidate_evidence_255 import table

    OUT.mkdir(parents=True, exist_ok=True)
    table(OUT / 'admission.csv', [{k: v for k, v in r.items() if k not in ('adopted', 'polley_hedengren_2026')} for r in rows])


if __name__ == '__main__':
    assert sys.argv[1:] == ['freeze']
    freeze()
