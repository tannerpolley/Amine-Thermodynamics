import csv
import sys
import time
from pathlib import Path

SCANS = Path(__file__).resolve().parent
sys.path.insert(0, str(SCANS.parent))
import born_form_diagnosis
born_form_diagnosis.DEADLINE = float('inf')


def main():
    started = time.perf_counter()
    output = SCANS / 'scan_C_results.csv'
    fields = ('form', 'scale', 'pressure_cost', 'bottinger_cost', 'matin_cost', 'cost', 'status')
    scales = (0.8, 0.9, 1.0, 1.1, 1.2)
    diameter_ids = [f'component/{ion}/born_diameter' for ion in born_form_diagnosis.ION_IDS[:3]]

    with output.open('w', newline='') as stream:
        writer = csv.DictWriter(stream, fieldnames=fields)
        writer.writeheader()
        stream.flush()
        for form in ('11', '00'):
            base = born_form_diagnosis.MAPPINGS[form]
            diameters = born_form_diagnosis.values(base)
            for scale in scales:
                name = f'scan-C-{form}-scale-{scale:.1f}'
                row = {'form': form, 'scale': f'{scale:.1f}'}
                try:
                    mapping = born_form_diagnosis.changed(
                        base, {identity: diameters[identity] * scale for identity in diameter_ids})
                    result = born_form_diagnosis.evaluate(name, mapping, form)
                    row.update({key: result[key] for key in fields[2:6]})
                    row['status'] = 'complete'
                except Exception as error:
                    row.update({key: '' for key in fields[2:6]})
                    row['status'] = f'failed: {type(error).__name__}: {error}'
                writer.writerow(row)
                stream.flush()
    print(f'wall_time_s={time.perf_counter() - started:.3f}', flush=True)


if __name__ == '__main__':
    main()
