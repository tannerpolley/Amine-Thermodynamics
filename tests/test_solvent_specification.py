"""Numerical reproduction of #222 endpoints, not physical validation."""

import concurrent.futures
import json
import math
import multiprocessing
import os
from pathlib import Path

import pytest

for variable in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS"):
    os.environ[variable] = "1"
from MEA.solvent_specification import SolventSpecification, relative_error_statistic  # noqa: E402

ROOT = Path(__file__).resolve().parents[1]
AN = ROOT / "analyses/solvent_specification_mdea"
OLD = ROOT / "analyses/mdea_mea_workflow/results/stage2-capped"
SPEC = None


def predict(row):
    return SPEC.prediction(row)


def evaluate(label):
    global SPEC
    SPEC = SolventSpecification(AN / f"{label}.toml")
    rows = SPEC.inputs["observations"]["fitted"]
    with concurrent.futures.ProcessPoolExecutor(
        max_workers=os.cpu_count(), mp_context=multiprocessing.get_context("fork")
    ) as pool:
        records = list(pool.map(predict, rows))
    assert all(r["status"] == "Available" for r in records), records
    residuals = [r["residual"] * math.sqrt(q["weight"]) for r, q in zip(records, rows, strict=True)]
    return records, residuals, 0.5 * sum(v * v for v in residuals)


def test_R1_R3_R5():
    global SPEC
    records, residuals, cost = evaluate("B1")
    expected = json.loads((OLD / "B1/fit.json").read_text())
    errors = [abs(a - b) for a, b in zip(residuals, expected["weighted_residuals"], strict=True)]
    first = next((i for i, e in enumerate(errors) if e > 1e-8), None)
    result = dict(
        R1=dict(
            cost=cost,
            expected_cost=374.45201342397434,
            cost_relative_error=abs(cost / 374.45201342397434 - 1),
            max_residual_error=max(errors),
            first_differing_residual=first,
            records=records,
        )
    )
    (AN / "results").mkdir(exist_ok=True)
    (AN / "results/endpoint-checks.json").write_text(json.dumps(result, indent=2) + "\n")
    assert first is None, (
        f"R1 STOP: residual {first}: actual {residuals[first]}, expected {expected['weighted_residuals'][first]}"
    )
    assert abs(cost / 374.45201342397434 - 1) <= 1e-8
    selected = [
        r
        for r in SPEC.inputs["observations"]["comparisons"]
        if r["group"] == "Ermatchkov" and r["row"]["mass_fraction"] <= 0.49
    ]
    with concurrent.futures.ProcessPoolExecutor(
        max_workers=os.cpu_count(), mp_context=multiprocessing.get_context("fork")
    ) as pool:
        er = list(pool.map(predict, selected))
    aard = relative_error_statistic(er)
    result["R3"] = dict(rows=len(er), AARD_percent=aard, expected=19.1460124028601, records=er)
    a3, _, a3cost = evaluate("A3")
    declarations = json.loads((OLD / "A3/declaration.json").read_text())["coordinates"]
    result["R5"] = dict(
        cost=a3cost,
        expected=403.71498514705206,
        coordinates_match=SPEC.inputs["coordinates"] == declarations,
        records=a3,
    )
    (AN / "results/endpoint-checks.json").write_text(json.dumps(result, indent=2) + "\n")
    assert len(er) == 88 and aard is not None and abs(aard - 19.1460124028601) <= 1e-6
    assert abs(a3cost / 403.71498514705206 - 1) <= 1e-8
    assert SPEC.inputs["coordinates"] == declarations

    with pytest.raises(ValueError, match="bound to another parameter endpoint"):
        SPEC.phase(SPEC.inputs["observations"]["phase_states"][0], SPEC.spec["phase_policy"])
