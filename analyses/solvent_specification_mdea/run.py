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


def phase(record):
    return SPEC.phase(record, SPEC.spec["phase_policy"])


def runtime():
    wheel, digest = epcsaft.provenance()
    assert digest == "ca7093ca721fdc80226c74d018a582f31705684c6995e80b0492c193334dd5d5"
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
            engine_commit="d513820994a78bfe628d42fffd55b2eeab6f89bd",
            python=sys.version,
            packages={k: importlib.metadata.version(k) for k in ("epcsaft", "numpy", "scipy")},
            workers=os.cpu_count(),
            BLAS_threads_per_process=1,
        ),
    )


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
            masses = {cid: species[cid]["molar_mass"]["value"]["magnitude"]
                      for cid in SPEC.spec["composition"]["analytical_amines"] + ["water"]}
            wt = [100 * float(r["amine"]) * masses["methyldiethanolamine"] /
                  (float(r["amine"]) * masses["methyldiethanolamine"] + float(r["water"]) * masses["water"])
                  for r in rows]
            values = {"T_K": [float(r["T"]) for r in rows], "wt_percent": wt,
                      "loading_mol_per_mol": [float(r["alpha"]) for r in rows]}
            region = {key: [min(v), max(v)] for key, v in values.items()}
            evaluated_region = {}
            for key, column in values.items():
                evaluated = [v for v, r in zip(column, records, strict=True) if r["status"] == "Available"]
                evaluated_region[key] = [min(evaluated), max(evaluated)] if evaluated else None
            available = [r for r in records if r["status"] == "Available" and r["observed"]]
            datasets.append(dict(name=declaration["name"], role=declaration["role"], region=region,
                                 rows=len(rows), available_rows=len(available), evaluated_region=evaluated_region,
                                 AARD_percent=relative_error_statistic(available),
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
            fitted_parameter_document=dict(
                status="Unavailable",
                cause="Missing public serializer from native ParameterDocument returned by reg.fitted_parameters / _core.fitted_document to epcsaft.parameters JSON read by Parameters.from_json",
                required_check="Export the B1 refit, reload it and reproduce its cost within 1e-8 relative and R1 residuals within 1e-8 absolute",
            ),
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
