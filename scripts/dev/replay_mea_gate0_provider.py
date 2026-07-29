from __future__ import annotations

import argparse
import hashlib
import json
import os
import subprocess
import tempfile
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[2]
BUNDLE = (
    ROOT
    / "data/reference/epcsaft_bundles"
    / "mea-co2-h2o-nine-species-regression-input/1"
)
RECEIPT = BUNDLE.parent / "1.receipt.json"
PROBE = Path(__file__).with_name("mea_gate0_provider_probe.cpp")
COMPONENTS = (
    "carbon-dioxide",
    "monoethanolamine",
    "water",
    "protonated-monoethanolamine",
    "carbamate-anion",
    "bicarbonate-anion",
    "carbonate-anion",
    "hydronium-cation",
    "hydroxide-anion",
)


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _run(command: list[str], *, cwd: Path | None = None) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        command,
        cwd=cwd,
        check=True,
        text=True,
        capture_output=True,
        env={**os.environ, "PYTHONPATH": ""},
    )


def replay(wheel: Path) -> dict[str, Any]:
    receipt = json.loads(RECEIPT.read_text(encoding="utf-8"))
    provider = receipt["provider"]
    consumer = receipt["public_consumer"]
    if _sha256(wheel) != provider["wheel_sha256"]:
        raise RuntimeError("Provider wheel SHA-256 does not match the frozen receipt")
    if _sha256(PROBE) != consumer["source_sha256"]:
        raise RuntimeError("tracked public C++ consumer differs from the frozen receipt")
    if _sha256(Path(__file__)) != consumer["harness_sha256"]:
        raise RuntimeError("tracked replay harness differs from the frozen receipt")

    with tempfile.TemporaryDirectory(prefix="mea-gate0-provider-") as temporary:
        work = Path(temporary)
        venv = work / "venv"
        _run(["uv", "venv", "--python", "3.13", str(venv)])
        python = venv / "bin/python"
        _run(["uv", "pip", "install", "--python", str(python), str(wheel), "pint"])

        model_path = work / "mea-gate0.native"
        export_program = "\n".join(
            (
                "import importlib, json, pathlib, sys",
                'package = importlib.import_module("epcsaft")',
                f"components = {COMPONENTS!r}",
                "parameters = package.Parameters.from_bundle(sys.argv[1], components=components)",
                "mixture = package.Mixture(parameters)",
                "package.export_native_model(mixture, sys.argv[2])",
                "root = pathlib.Path(package.__file__).resolve().parent",
                "print(json.dumps({",
                '  "module_origin": str(pathlib.Path(package.__file__).resolve()),',
                '  "include": str(root / "include"),',
                '  "cmake": str(root / "cmake"),',
                '  "parameter_fingerprint": mixture.parameter_fingerprint,',
                '  "bundle_fingerprint": parameters.bundle_fingerprint,',
                "}, sort_keys=True))",
            )
        )
        exported = json.loads(
            _run(
                [str(python), "-c", export_program, str(BUNDLE), str(model_path)],
                cwd=ROOT,
            ).stdout
        )
        module_origin = Path(exported["module_origin"])
        if not module_origin.is_relative_to(venv):
            raise RuntimeError("Provider module did not load from the isolated wheel environment")
        if exported["parameter_fingerprint"] != receipt["bundle"]["parameter_fingerprint"]:
            raise RuntimeError("public bundle load changed the parameter fingerprint")
        if exported["bundle_fingerprint"] != receipt["bundle"]["bundle_fingerprint"]:
            raise RuntimeError("public bundle load changed the bundle fingerprint")

        include = Path(exported["include"])
        header = include / "epcsaft/native_sdk_v1.h"
        if _sha256(header) != provider["installed_header_sha256"]:
            raise RuntimeError("installed public header differs from the frozen receipt")
        cmake_source = work / "cmake"
        cmake_source.mkdir()
        (cmake_source / "CMakeLists.txt").write_text(
            "\n".join(
                (
                    "cmake_minimum_required(VERSION 3.20)",
                    "project(mea_gate0_provider_probe LANGUAGES CXX)",
                    "find_package(Threads REQUIRED)",
                    "find_package(epcsaft CONFIG REQUIRED)",
                    "add_executable(mea_gate0_provider_probe ${PROBE_SOURCE})",
                    "target_link_libraries(mea_gate0_provider_probe PRIVATE epcsaft::native_sdk)",
                    "",
                )
            ),
            encoding="utf-8",
        )
        build = work / "build"
        _run(
            [
                "cmake",
                "-S",
                str(cmake_source),
                "-B",
                str(build),
                "-DCMAKE_BUILD_TYPE=Release",
                f"-Depcsaft_DIR={exported['cmake']}",
                f"-DPROBE_SOURCE={PROBE}",
            ]
        )
        _run(["cmake", "--build", str(build), "--config", "Release"])
        executable = build / "mea_gate0_provider_probe"
        dynamic_dependencies = _run(["ldd", str(executable)]).stdout
        if "ePC-SAFT-project/ePC-SAFT" in dynamic_dependencies:
            raise RuntimeError("public consumer bound a sibling Provider source checkout")
        probe = json.loads(
            _run(
                [
                    str(executable),
                    str(model_path),
                    receipt["bundle"]["parameter_fingerprint"],
                    receipt["bundle"]["topology_fingerprint"],
                ]
            ).stdout
        )
        expected = {
            "abi_version": provider["abi_version"],
            "table_size": provider["table_size"],
            "component_count": len(COMPONENTS),
            "neutral_basis_row_count": provider["neutral_basis_row_count"],
            "neutral_reference_result_size": provider["neutral_reference_result_size"],
            "neutral_reference_derivative_result_size": provider[
                "neutral_reference_derivative_result_size"
            ],
            "derivative_status": 0,
            "derivative_availability": 10,
            "source_pressure_min_pa": receipt["domain"]["pressure_pa"][0],
            "source_pressure_max_pa": receipt["domain"]["pressure_pa"][1],
            "outside_pressure_status": consumer["expected_domain_statuses"][
                "outside_pressure"
            ],
            "outside_temperature_status": consumer["expected_domain_statuses"][
                "outside_temperature"
            ],
        }
        if probe != expected:
            raise RuntimeError(f"public Provider replay differs: expected={expected}, actual={probe}")
        return {
            "status": "REGRESSION_INPUT_EXECUTABLE",
            "wheel_sha256": provider["wheel_sha256"],
            "header_sha256": provider["installed_header_sha256"],
            "probe_source_sha256": _sha256(PROBE),
            "harness_sha256": _sha256(Path(__file__)),
            "binary_sha256": _sha256(executable),
            "source_checkout_bound": False,
            "probe": probe,
        }


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Replay the MEA Gate 0 receipt through the installed public Provider SDK."
    )
    parser.add_argument("--wheel", type=Path, required=True)
    args = parser.parse_args()
    print(json.dumps(replay(args.wheel.resolve()), indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
