"""Numerical reproduction of #222 endpoints, not physical validation."""

import concurrent.futures
import copy
import json
import math
import multiprocessing
import os
from pathlib import Path
from types import SimpleNamespace

import pytest

for variable in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS"):
    os.environ[variable] = "1"
from MEA.solvent_specification import SolventSpecification, relative_error_statistic  # noqa: E402
import epcsaft  # noqa: E402
from epcsaft import equilibrium as eq, regression as reg  # noqa: E402

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
    assert len(SPEC.species_mapping(SPEC.spec["chemistry"]["reactions"])) == 8
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
    assert len(er) == 88 and aard is not None and abs(aard - 19.1460124028601) <= 1e-6
    assert abs(a3cost / 403.71498514705206 - 1) <= 1e-8
    assert SPEC.inputs["coordinates"] == declarations

    with pytest.raises(ValueError, match="bound to another parameter endpoint"):
        SPEC.phase(SPEC.inputs["observations"]["phase_states"][0], SPEC.spec["phase_policy"])

    (AN / "results/endpoint-checks.json").write_text(json.dumps(result, indent=2) + "\n")


@pytest.mark.parametrize("kind", ["reaction_coordinate", "reaction_enthalpy_shift"])
def test_reaction_coordinate_equivalence(kind):
    # d513820 equations.md: reaction_constant_coordinate_derivative and affine q=origin+scale*v.
    spec = SolventSpecification(AN / "B1.toml")
    record = spec.inputs["observations"]["fitted"][11]
    problem = spec.problems[record["problem"]]
    original = copy.deepcopy(spec.spec["chemistry"]["reactions"]["aqueous"])
    law = original[-1]["correlation"]
    declaration = dict(
        kind=kind,
        name="MDEA-dissociation",
        origin=0.0,
        scale=1000.0,
        bounds=[-2000.0, 2000.0],
        pivot_temperature=313.15,
    )
    if kind == "reaction_coordinate":
        declaration.update(coefficient="a", origin=law["a"], scale=0.2, bounds=[law["a"] - 1, law["a"] + 1])
    spec.inputs["coordinates"] = [declaration]
    observation = spec.observation(record)
    baseline = reg.predict(spec.model, observation).value
    results = []
    for optimizer in (0.0, 1.0):
        evaluation = reg.differentiate(
            spec.parameters, spec.coordinates(), [observation], optimizer=[optimizer], thermochemistry=spec.thermal
        )
        exported = spec.fitted_reactions(evaluation.chart)["aqueous"][-1]["correlation"]
        changed = copy.deepcopy(original)
        if kind == "reaction_coordinate":
            changed[-1]["correlation"]["a"] = law["a"] + 0.2 * optimizer
        else:
            h = 1000.0 * optimizer
            changed[-1]["correlation"]["a"] += h / (epcsaft.GAS_CONSTANT_J_PER_MOL_K * 313.15)
            changed[-1]["correlation"]["b"] -= h / epcsaft.GAS_CONSTANT_J_PER_MOL_K
        spec.spec["chemistry"]["reactions"]["aqueous"] = changed
        row = dict(
            T=problem.T,
            P=problem.P.guess,
            water=problem.feed.values["water"],
            alpha=problem.feed.values["carbon-dioxide"],
        )
        spec.problems[record["problem"]] = spec.problem("loaded-bubble", row)
        direct = reg.predict(spec.model, spec.observation(record))
        assert direct.status.name == "Available"
        actual_cost = 0.5 * record["weight"] * math.log(evaluation.predictions[0] / observation.observed) ** 2
        direct_cost = 0.5 * record["weight"] * direct.residual**2
        assert abs(actual_cost - direct_cost) <= 1e-10
        if optimizer == 0.0:
            assert abs(evaluation.predictions[0] - baseline) <= 1e-8
        for key in ("a", "b"):
            assert exported[key] == pytest.approx(changed[-1]["correlation"][key], rel=0.0, abs=1e-12)
        results.append(
            dict(
                optimizer=optimizer,
                predicted_Pa=evaluation.predictions[0],
                actual_cost=actual_cost,
                direct_cost=direct_cost,
            )
        )
    print(kind, results)
    (AN / f"results/{kind}-check.json").write_text(json.dumps(results, indent=2) + "\n")


def test_nonfinite_split_is_unresolved(monkeypatch, tmp_path):
    spec = SolventSpecification(AN / "B1.toml")
    trial = SimpleNamespace(
        seed=0,
        evidence="resolved_descent",
        message="synthetic split-coordinate failure",
        resolved_descent=True,
        quantities={},
        split_coordinates=[-math.inf],
        phase=SimpleNamespace(kind=SimpleNamespace(name="Liquid"), support=["water"]),
    )
    native = SimpleNamespace(completed=True, message="unresolved trials 0;", present_phases=[], work={}, trials=[trial])
    monkeypatch.setattr(eq, "stability_test", lambda *args: native)
    result = spec.phase(spec.inputs["observations"]["phase_states"][0], spec.spec["phase_policy"])
    path = tmp_path / "R4-trials.json"
    path.write_bytes((json.dumps(result, indent=2, allow_nan=False) + "\n").encode())
    result = json.loads(path.read_bytes())
    assert result["gas"] == [] and len(result["unresolved"]) == 1
    retained = result["stability"]["trials"][0]
    assert retained["seed"] == 0 and retained["message"] == trial.message
    assert retained["split_coordinates"] == ["-inf"]
    assert result["unresolved"][0]["classification_unavailable"] == "Missing or nonfinite logarithmic packing fraction"
