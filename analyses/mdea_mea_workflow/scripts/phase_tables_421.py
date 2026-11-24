"""Materialize #421 completion tables from retained records."""
import json
import sys
from pathlib import Path

root = Path(__file__).resolve().parents[1] / 'results/phase-search-421'
def read(name):
    return json.loads((root / (name + '.json')).read_text())
def table(title, headers, rows):
    return '\n'.join([f'### {title}', '', '| ' + ' | '.join(headers) + ' |', '|' + '|'.join(['---'] * len(headers)) + '|'] + ['| ' + ' | '.join(map(str, row)) + ' |' for row in rows])
c = read('coverage-counts')
coverage = read('coverage')
measured = read('measured-phase')
properties = read('property-deviations')
parts = [table('Measured-range coverage', ['Tier', 'Stage', 'MDEA concentration', 'Loading', 'Records'], [[r['tier'], r['stage'], r['MDEA_wt_percent'], r['loading'], r['count']] for r in c['measured_range_counts']])]
parts.append(table('Coexistence root identities', ['Calculation', 'Attempt', 'Root identities'], [[r['key'], i + 1, ', '.join(x['identity'] for x in a['coexistence_roots'])] for r in measured for i, a in enumerate(r['attempts']) if a.get('coexistence_roots')]))
def aard(record, key):
    stats = record[key]['statistics']
    return 'Empty' if stats is None or stats.get('AARD_percent') is None else f"{stats['AARD_percent']:.4f}"
parts.append(table('Pressure-specific property subsets', ['Property', 'Pressure (Pa)', 'All AARD (%)', 'Linked AARD (%)', 'Excluded AARD (%)', 'Excluding supplied-only AARD (%)'], [[r['group'][0], r['pressure_assignment_Pa'], *(aard(r, k) for k in ('all', 'linked', 'excluded', 'excluded_supplied_only'))] for r in properties if r['pressure_assignment_Pa'] is not None]))
bubble = [r for r in coverage if r['bubble_multiplier'] is not None and r['complete']]
parts.append(table('Absolute-pressure reconstruction', ['Completed bubble-relative records', 'Reconstructed pressure', 'Unknown pressure'], [[len(bubble), sum(r['pressure_Pa'] is not None for r in bubble), sum(r['pressure_Pa'] is None for r in bubble)]]))
output = '\n\n'.join(parts) + '\n'
target = root / 'tables.md'
if '--check' in sys.argv:
    if not target.exists() or target.read_text() != output:
        raise SystemExit('Generated tables are stale')
else:
    target.write_text(output)
