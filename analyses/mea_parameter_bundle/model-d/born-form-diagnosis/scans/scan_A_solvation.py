import csv
import os
import sys
import time
from pathlib import Path

SCANS = Path(__file__).resolve().parent
sys.path.insert(0, str(SCANS.parent))
import born_form_diagnosis
born_form_diagnosis.DEADLINE = float('inf')


def main():
    started = time.perf_counter()
    output = born_form_diagnosis.HERE / 'scan_A_results.csv'
    fields = ('param', 'value', 'pressure_cost', 'bottinger_cost', 'matin_cost', 'cost', 'status')
    form = os.environ['SCAN_FORM']
    base = born_form_diagnosis.MAPPINGS[form]
    values = born_form_diagnosis.values(base)
    parameters = {
        'component/water/solvation_factor': ('water', (1.0, 1.25, 1.5, 1.75, 2.0), 1.5),
        'component/monoethanolamine/solvation_factor': ('monoethanolamine', (1.0, 1.25, 1.5, 1.75), 1.0),
    }

    for identity, (label, _, baseline) in parameters.items():
        if identity not in values:
            raise SystemExit(f'scan stopped: parameter id not found in values(MAPPINGS["11"]): {identity}')
        if values[identity] != baseline:
            raise SystemExit(f'scan stopped: expected {identity} baseline {baseline}, found {values[identity]}')
        probe = born_form_diagnosis.values(
            born_form_diagnosis.changed(base, {identity: 1.25})
        ).get(identity)
        if probe != 1.25:
            raise SystemExit(f'scan stopped: changed() did not accept {identity}; returned {probe!r}')
        print(f'parameter_id[{label}]={identity}', flush=True)

    scans = [(identity, label, (float(os.environ['SCAN_VALUE']),)) for identity, (label, _, _) in parameters.items() if label == os.environ['SCAN_AXIS']]
    results = {}
    with output.open('w', newline='') as stream:
        writer = csv.DictWriter(stream, fieldnames=fields)
        writer.writeheader()
        stream.flush()
        for identity, label, points in scans:
            for value in points:
                water = value if label == 'water' else 1.5
                mea = value if label == 'monoethanolamine' else 1.0
                configuration = (water, mea)
                if configuration not in results:
                    value_text = str(value)
                    name = f'scan-A-{label}-{value_text}'
                    row = {'param': identity, 'value': value_text}
                    try:
                        mapping = born_form_diagnosis.changed(base, {identity: value})
                        result = born_form_diagnosis.evaluate(name, mapping, form)
                        row.update({key: result[key] for key in fields[2:6]})
                        row['status'] = 'complete'
                    except Exception as error:
                        row.update({key: '' for key in fields[2:6]})
                        row['status'] = f'failed: {type(error).__name__}: {error}'
                    results[configuration] = row
                row = dict(results[configuration], param=identity, value=str(value))
                writer.writerow(row)
                stream.flush()

    print(f'wall_time_s={time.perf_counter() - started:.3f}', flush=True)


if __name__ == '__main__':
    main()
