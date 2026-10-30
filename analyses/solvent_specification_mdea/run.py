"""Retain the accepted B1 fit and 751-state endpoint phase reproduction."""

import os

import concurrent.futures
import gzip
import hashlib
import importlib.metadata
import json
import multiprocessing
import sys
import zipfile
from pathlib import Path

for variable in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS"):
    os.environ[variable] = "1"

import epcsaft  # noqa: E402
from epcsaft import regression as reg  # noqa: E402
from epcsaft.parameters import document_mapping  # noqa: E402
from MEA.solvent_specification import SolventSpecification, relative_error_statistic  # noqa: E402

AN = Path(__file__).resolve().parent
OLD = AN.parent / "mdea_mea_workflow/results/stage2-capped/B1"
SPEC = None


def write(name, value):
    path = AN / "results" / name
    path.parent.mkdir(parents=True, exist_ok=True)
    data = (json.dumps(value, indent=2, allow_nan=False) + "\n").encode()
    if len(data) > 5_000_000:
        path = path.with_suffix(path.suffix + ".gz")
        data = gzip.compress(data, mtime=0)
    path.write_bytes(data)


def predict(record):
    return SPEC.prediction(record)


def phase(record):
    return SPEC.phase(record, SPEC.spec["phase_policy"])


def runtime():
    wheel, digest = epcsaft.provenance()
    assert digest == "b4c0f6d8eb8971abd3c0bd801cb9167b8ca602cb2a63b16a22e924d5b6727496"
    with zipfile.ZipFile(wheel) as archive:
        for name in archive.namelist():
            if name.startswith("epcsaft/") and not name.endswith("/"):
                assert archive.read(name) == (Path(epcsaft.__file__).parent.parent / name).read_bytes(), name
    write(
        "runtime.json",
        dict(
            wheel=str(wheel),
            wheel_sha256=digest,
            module=epcsaft.__file__,
            installed_files_byte_identical=True,
            engine_commit="217026ab60b8e244cd7d9dac126b8b3d16bccb67",
            python=sys.version,
            packages={k: importlib.metadata.version(k) for k in ("epcsaft", "numpy", "scipy")},
            workers=os.cpu_count(),
            BLAS_threads_per_process=1,
        ),
    )


if sys.argv[1] not in ("export", "handoff"):
    runtime()
checks = json.loads((AN / "results/endpoint-checks.json").read_text())
assert checks["R1"]["first_differing_residual"] is None and checks["R1"]["cost_relative_error"] <= 1e-8
if sys.argv[1] == "R2":
    SPEC = SolventSpecification(AN / "B1.toml", parameter="start")
    native, report, parameters = SPEC.fit()
    expected = json.loads((OLD / "fit.json").read_text())
    report["cost_relative_error"] = abs(report["final_cost"] / 374.45201342397434 - 1)
    report["maximum_optimizer_difference"] = max(
        abs(a - b) for a, b in zip(report["optimizer"], expected["optimizer"], strict=True)
    )
    report["passed"] = (
        report["usable"]
        and report["status"] == "converged"
        and report["cost_relative_error"] <= 1e-6
        and report["maximum_optimizer_difference"] <= 1e-5
    )
    write("R2.json", report)
    print(
        "R2",
        report["status"],
        report["iterations"],
        report["final_cost"],
        report["maximum_optimizer_difference"],
        report["passed"],
        flush=True,
    )
elif sys.argv[1] == "R4":
    SPEC = SolventSpecification(AN / "B1.toml")
    records = SPEC.inputs["observations"]["phase_states"]
    assert len(records) == 751
    expected_hash = SPEC.spec["endpoint"]["sha256"]
    assert all(r.get("endpoint_sha256", expected_hash) == expected_hash for r in records)
    with concurrent.futures.ProcessPoolExecutor(
        max_workers=os.cpu_count(), mp_context=multiprocessing.get_context("fork")
    ) as pool:
        results = list(pool.map(phase, records))
    expected = json.loads(gzip.decompress((OLD / "phase.json.gz").read_bytes()))[:745] + json.loads(
        (OLD / "capped-phase.json").read_text()
    )
    summary = dict(states=len(results), policy=SPEC.spec["phase_policy"])
    for key in ("dense", "gas", "ambiguous", "unresolved", "reconstruction"):
        summary[key] = [r["identity"] for r in results if r.get(key)]
    reference_gas = [r["index"] for r in expected if r["density_gate"]["gas_evolution"]]
    summary["identities_match"] = [r["identity"] for r in results] == [r["index"] for r in expected]
    summary["gas_identities_match"] = summary["gas"] == reference_gas
    summary["passed"] = (
        summary["identities_match"]
        and summary["gas_identities_match"]
        and len(summary["gas"]) == 37
        and not any(summary[k] for k in ("dense", "ambiguous", "unresolved", "reconstruction"))
    )
    write("R4-trials.json", results)
    write("R4.json", summary)
    print("R4", summary, flush=True)
elif sys.argv[1] == "export":
    assert json.loads((AN / "results/issue-232-R1.json").read_text())["cost_relative_error"] <= 1e-10
    assert epcsaft.provenance()[1] == "b4c0f6d8eb8971abd3c0bd801cb9167b8ca602cb2a63b16a22e924d5b6727496"
    exports = {}
    for label in ("B1", "A3"):
        SPEC = SolventSpecification(AN / f"{label}.toml", parameter="start")
        fit = json.loads((OLD.parent / label / "fit.json").read_text())
        chart = reg.evaluate_coordinates(SPEC.parameters, SPEC.coordinates(), fit["optimizer"], [], SPEC.thermal)
        fitted = reg.fitted_parameters(SPEC.parameters, chart)
        write(f"{label}-parameters.json", document_mapping(fitted))
        path = next((AN / "results").glob(f"{label}-parameters.json*"))
        data = path.read_bytes()
        reloaded = epcsaft.Parameters.from_mapping(json.loads(gzip.decompress(data) if path.suffix == ".gz" else data), components=fitted.component_ids)
        entries = list(zip(fitted._document.entries, reloaded._document.entries, strict=True))
        equal = sum(a.magnitude.hex() == b.magnitude.hex() and (a.identity, a.field, a.index, a.unit) == (b.identity, b.field, b.index, b.unit) for a, b in entries)
        assert equal == len(entries)
        SPEC.parameters = reloaded
        SPEC.model = epcsaft.Mixture(reloaded, thermochemistry=SPEC.thermal)
        with concurrent.futures.ProcessPoolExecutor(max_workers=os.cpu_count(), mp_context=multiprocessing.get_context("fork")) as pool:
            records = list(pool.map(predict, SPEC.inputs["observations"]["fitted"]))
        assert all(r["status"] == "Available" for r in records)
        write(f"{label}-reload-residuals.json", records)
        cost = 0.5 * sum(r["residual"] ** 2 * q["weight"] for r, q in zip(records, SPEC.inputs["observations"]["fitted"], strict=True))
        assert abs(cost / fit["final_cost"] - 1) <= 1e-8
        exports[label] = dict(path=str(path.relative_to(AN)), sha256=hashlib.sha256(data).hexdigest(), bytes=len(data), wheel_sha256=epcsaft.provenance()[1], components=fitted.component_ids,
                              note="Reaction laws stay in reactions.aqueous; the parameter document excludes them.", fitted_cost=fit["final_cost"], reload_cost=cost, cost_relative_error=abs(cost / fit["final_cost"] - 1), native_entries_equal=equal, native_entries=len(entries))
    write("parameter-reload.json", exports)
elif sys.argv[1] == "handoff":
    SPEC = SolventSpecification(AN / "B1.toml")
    reactions = json.loads((AN / "results/R2.json").read_text())["reactions"]
    species = SPEC.species_mapping(reactions)
    comparisons = json.loads((AN / "results/comparisons.json").read_text())
    retained = {r["identity"]: r for r in checks["R1"]["records"] + comparisons}
    properties = {}
    for prop, groups in SPEC.spec["export_property_groups"].items():
        datasets = []
        for declaration in SPEC.spec["datasets"]:
            if declaration["group"] not in groups:
                continue
            rows = SPEC.load_record(declaration)
            records = [retained[r["identity"]] for r in rows]
            wt = [100 * float(r["amine"]) * species["methyldiethanolamine"]["molar_mass"]["value"]["magnitude"] /
                  sum(float(r[key]) * species[cid]["molar_mass"]["value"]["magnitude"] for key, cid in (("amine", "methyldiethanolamine"), ("water", "water")))
                  for r in rows]
            values = {"T_K": [float(r["T"]) for r in rows], "wt_percent": wt,
                      "loading_mol_per_mol": [float(r["alpha"]) if float(r["amine"]) else None for r in rows]}
            region = {key: [min(v), max(v)] if None not in v else None for key, v in values.items()}
            evaluated_region = {}
            for key, column in values.items():
                if key == "loading_mol_per_mol" and declaration["constructor"] == "saturation_capped_addition_enthalpy":
                    column = [r.get("endpoint_loading") for r in records]
                evaluated = [v for v, r in zip(column, records, strict=True) if r["status"] == "Available" and v is not None]
                evaluated_region[key] = [min(evaluated), max(evaluated)] if evaluated else None
            available = [r for r in records if r["status"] == "Available"]
            datasets.append(dict(name=declaration["name"], role=declaration["role"], region=region,
                                 rows=len(rows), available_rows=len(available), evaluated_region=evaluated_region,
                                 AARD_percent=relative_error_statistic([r for r in available if r["observed"] != 0]),
                                 **({"loading_unavailable_cause": "Undefined: analytical MDEA amount is zero for pure-water rows."} if None in values["loading_mol_per_mol"] else {}),
                                 unavailable=[r for r in records if r["status"] != "Available"],
                                 observation=dict(constructor=declaration["constructor"], kind=declaration["kind"])))
        properties[prop] = dict(datasets=datasets, phase_search="assessment.phase_search",
                                active_bounds="assessment.active_bounds", fitted_bounds=SPEC.inputs["coordinates"],
                                actions="Unavailable: derivative actions not assessed in retained #228 results")
    files = [
        AN / "B1.toml",
        AN / "declarations.toml",
        AN / "inputs/caloric.json",
        AN / "inputs/preparation-provenance.json",
        AN / "inputs/phase-provenance.json",
        AN / "inputs/parameter-caloric-provenance.json",
    ]
    files += [AN / SPEC.spec[key]["path"] for key in ("endpoint", "coordinates", "start", "phase_states")]
    files += [AN / d["path"] for d in SPEC.spec["datasets"]]
    files += list((AN / "results").glob("R[24]*")) + [
        AN / "results/runtime.json",
        AN / "results/endpoint-checks.json",
        AN / "results/comparisons.json",
    ]
    write(
        "handoff.json",
        dict(
            fitted_parameter_document=json.loads((AN / "results/parameter-reload.json").read_text()),
            species=species,
            balance_checks=dict(species_charges="Exact match to Engine", reactions="All elements and charge conserved"),
            conventions=SPEC.spec["export_conventions"],
            reactions={group: [dict(r, interpretation=SPEC.spec["export_conventions"]["reaction_direction"])
                               for r in rows] for group, rows in reactions.items()},
            neutral_references={name: dict(r, species_reference={}, effective_species_reference={
                cid: "PureLiquid" if cid == r["solvent"] else "InfiniteDilution" for cid in species})
                for name, r in SPEC.spec["chemistry"]["neutral_references"].items()},
            problem_templates=SPEC.spec["templates"],
            caloric=SPEC.inputs["caloric"],
            runtime=json.loads((AN / "results/runtime.json").read_text()),
            files=[dict(path=str(p.relative_to(AN)), sha256=hashlib.sha256(p.read_bytes()).hexdigest()) for p in files],
            assessment=dict(
                kind="Numerical reproduction; calibration and conditional outside-fit assessment",
                temperature_domain_K=[293.15, 395.0],
                composition_basis="Prepared analytical molar feed; CO2 loading per mole MDEA",
                properties=properties,
                observation_policy=SPEC.spec["datasets"],
                active_bounds=json.loads((AN / "results/R2.json").read_text())["covariance"]["active_bounds"],
                phase_search=json.loads((AN / "results/R4.json").read_text()),
                limits=[
                    "Accepted active bounds",
                    "Finite phase and saturation searches",
                    "Unmodeled nitrogen headspace",
                    "Property-specific unavailable and extrapolated quantities retained",
                    "Not qualified for absorber use",
                ],
                export_complete=False,
            ),
        ),
    )
else:
    raise ValueError("Expected R2, R4 or handoff")
