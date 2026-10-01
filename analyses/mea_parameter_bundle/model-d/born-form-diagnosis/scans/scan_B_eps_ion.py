import csv
import os
import json
import sys
from pathlib import Path

HARNESS_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(HARNESS_DIR))
import born_form_diagnosis

born_form_diagnosis.DEADLINE = float("inf")

PARAMETER = "model/relative_permittivity/ionic_region_relative_permittivity"
POINTS = (float(os.environ['SCAN_VALUE']),)
FORM = os.environ["SCAN_FORM"]
BASE = born_form_diagnosis.MAPPINGS[FORM]
BASE_VALUES = born_form_diagnosis.values(BASE)
RESULTS = born_form_diagnosis.HERE / "scan_B_results.csv"
FIELDS = ("param", "value", "pressure_cost", "bottinger_cost", "matin_cost", "cost", "status")

if BASE_VALUES[PARAMETER] != 8.0:
    raise RuntimeError(f"retained 11 baseline epsilon_ion is {BASE_VALUES[PARAMETER]}, expected 8.0")

rows = []
with RESULTS.open("x", newline="") as output:
    writer = csv.DictWriter(output, fieldnames=FIELDS)
    writer.writeheader()
    output.flush()

    for value in POINTS:
        row = {"param": "ionic_region_relative_permittivity", "value": value,
               "pressure_cost": "", "bottinger_cost": "", "matin_cost": "", "cost": ""}
        try:
            mapping = born_form_diagnosis.changed(BASE, {PARAMETER: value})
            mapped_values = born_form_diagnosis.values(mapping)
            if mapped_values[PARAMETER] != value:
                raise RuntimeError(f"changed() left epsilon_ion at {mapped_values[PARAMETER]}")
            fixed = {key: item for key, item in mapped_values.items() if key != PARAMETER}
            original = {key: item for key, item in BASE_VALUES.items() if key != PARAMETER}
            if fixed != original:
                raise RuntimeError("mapping changed parameters other than epsilon_ion")

            name = f"scan-B-eps_ion-{value:.1f}"
            result = born_form_diagnosis.evaluate(name, mapping, FORM)
            if result.get("complete") is not True:
                raise RuntimeError("evaluate() did not return a complete result")
            row.update({key: result[key] for key in FIELDS[2:-1]})
            row["status"] = "evaluated"
        except Exception as error:
            row["status"] = f"failed: {type(error).__name__}: {error}"

        writer.writerow(row)
        output.flush()
        rows.append(row)
        print(json.dumps(row), flush=True)
