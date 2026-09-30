import copy
import csv
import math
import sys
import time
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent))
import born_form_diagnosis
born_form_diagnosis.DEADLINE = float('inf')

PERMITTIVITY_ID = 'component/monoethanolamine/relative_permittivity'
VALUES = (24.0, 32.0, 40.0)
FORMS = ('11', '00')
FIELDS = ('form', 'value', 'pressure_cost', 'bottinger_cost', 'matin_cost', 'cost', 'status')


def with_permittivity(mapping, value):
    if PERMITTIVITY_ID in born_form_diagnosis.values(mapping):
        candidate = born_form_diagnosis.changed(mapping, {PERMITTIVITY_ID: value})
        if born_form_diagnosis.values(candidate).get(PERMITTIVITY_ID) == value:
            return candidate

    candidate = copy.deepcopy(mapping)
    coefficient = next(
        parameter
        for component in candidate['components']
        if component.get('component_id') == 'monoethanolamine'
        for parameter in component.get('coefficients', [])
        if parameter.get('family') == 'relative_permittivity'
    )
    coefficient['value']['magnitude'] = float(value)
    return candidate


def main():
    output = HERE / 'scan_D_results.csv'
    rows = []
    started = time.perf_counter()
    with output.open('w', newline='') as handle:
        writer = csv.DictWriter(handle, fieldnames=FIELDS)
        writer.writeheader()
        handle.flush()
        for form in FORMS:
            for value in VALUES:
                row = {'form': form, 'value': value, 'status': 'ok'}
                try:
                    mapping = with_permittivity(born_form_diagnosis.MAPPINGS[form], value)
                    result = born_form_diagnosis.evaluate(
                        f'scan-D-{form}-eps_mea-{value:g}', mapping, form
                    )
                    if not result.get('complete'):
                        raise RuntimeError('evaluator returned an incomplete result')
                    for key in FIELDS[2:6]:
                        row[key] = float(result[key])
                except Exception as error:
                    message = str(error).replace('\n', ' | ')
                    row['status'] = f'failed: {type(error).__name__}: {message}'
                writer.writerow(row)
                handle.flush()
                rows.append(row)
                print(row, flush=True)

    if len(rows) != 6:
        raise RuntimeError(f'expected six recorded scan points, found {len(rows)}')
    expected = {'11': 47.6258, '00': 40.2015}
    for form, baseline_cost in expected.items():
        baseline = next(row for row in rows if row['form'] == form and row['value'] == 32.0)
        if baseline['status'] != 'ok' or not math.isclose(
            baseline['cost'], baseline_cost, rel_tol=1e-6, abs_tol=5e-5
        ):
            raise RuntimeError(f'{form} baseline sanity check failed: {baseline}')
        alternatives = [
            row for row in rows
            if row['form'] == form and row['value'] != 32.0 and row['status'] == 'ok'
        ]
        if not any(
            not math.isclose(row['cost'], baseline['cost'], rel_tol=1e-12, abs_tol=1e-12)
            for row in alternatives
        ):
            raise RuntimeError(f'{form} has no successful non-baseline cost change')

    print(f'wall_s={time.perf_counter() - started:.3f}', flush=True)


if __name__ == '__main__':
    main()
