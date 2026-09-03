"""Build the deterministic MEA absorption parameter archive."""

from __future__ import annotations

import hashlib
import json
import zipfile
from pathlib import Path


ANALYSIS = Path(__file__).resolve().parents[1]
REPO = ANALYSIS.parents[1]
OUTPUT = ANALYSIS / "results/handoff/mea-reactive-epcsaft-parameter-bundle.zip"
ROOT = "mea-reactive-epcsaft-parameter-bundle"
PARAMETERS = ANALYSIS / "results/selected-current-best-parameters.json"
STATE_PACKET = ANALYSIS / "data/input/state-packet.json"
ENGINE = (
    ANALYSIS
    / "data/input/engine/epcsaft-0.2.0.dev0-cp313-cp313-linux_x86_64.whl"
)
EXPECTED_PARAMETER_SHA256 = (
    "0ea2ab19015c96472f98982181ac8753e1a238c1cb18d0ff78426820525310c8"
)
EXPECTED_STATE_PACKET_SHA256 = (
    "41017bcf727a486a8f3feb280e19c111a15c5dda5a3cca4e8c7dc5b051168fef"
)
EXPECTED_ENGINE_SHA256 = (
    "f6e5b51dad79741c759393688f7daa547c9eb73f5944d5f877b3b32b1e56714a"
)
R123_OFFSETS = (8.0330699846, 4.0165349923, 4.0165349923)


def sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def source(path: Path) -> bytes:
    return path.read_bytes()


def reaction_definition() -> bytes:
    packet = json.loads(STATE_PACKET.read_text(encoding="utf-8"))
    system = packet["observations"][0]["request"]["reaction_system"]
    reactions = [
        {
            "reaction_id": "R1",
            "stoichiometry": system["reaction_matrix"][0],
            "ln_k_form": "a + b_k / T + c * ln(T) + d_per_k * T + standard_state_offset",
            "coefficients": {"a": 132.899, "b_k": -13445.9, "c": -22.4773, "d_per_k": 0.0},
            "standard_state_offset": R123_OFFSETS[0],
            "temperature_domain_k": [273.15, 498.15],
        },
        {
            "reaction_id": "R2",
            "stoichiometry": system["reaction_matrix"][1],
            "ln_k_form": "a + b_k / T + c * ln(T) + d_per_k * T + standard_state_offset",
            "coefficients": {"a": 231.465, "b_k": -12092.1, "c": -36.7816, "d_per_k": 0.0},
            "standard_state_offset": R123_OFFSETS[1],
            "temperature_domain_k": [273.15, 498.15],
        },
        {
            "reaction_id": "R3",
            "stoichiometry": system["reaction_matrix"][2],
            "ln_k_form": "a + b_k / T + c * ln(T) + d_per_k * T + standard_state_offset",
            "coefficients": {"a": 216.049, "b_k": -12431.7, "c": -35.4819, "d_per_k": 0.0},
            "standard_state_offset": R123_OFFSETS[2],
            "temperature_domain_k": [273.15, 498.15],
        },
        {
            "reaction_id": "R4",
            "stoichiometry": system["reaction_matrix"][3],
            "ln_k_form": "a + b_k / T",
            "coefficients": {"a": 3.3515778177997895, "b_k": -1895.3},
            "temperature_domain_k": [293.15, 393.15],
            "qualification": "fitted jointly to the retained pressure and speciation data; evaluated over 293.15--393.15 K",
        },
        {
            "reaction_id": "R5",
            "stoichiometry": system["reaction_matrix"][4],
            "ln_k_form": "-ln(10) * (a_k / T + b + c_per_k * T)",
            "coefficients": {"a_k": 2677.91, "b": 0.3869, "c_per_k": 0.0004277},
            "temperature_domain_k": [273.15, 323.15],
        },
    ]
    definition = {
        "schema_version": 1,
        "temperature_unit": "kelvin",
        "species_ids": system["species_ids"],
        "charges": system["charges"],
        "reaction_sign_convention": "products_positive",
        "reactions": reactions,
        "balance_matrix": system["balance_matrix"],
        "source_standard_state": system["source_standard_state"],
        "model_choices": {
            "base": "pc-saft",
            "association": "general-site with reciprocal induced carbon-dioxide--water association",
            "electrolyte": "Debye--Huckel plus automatically activated corrected SSM+DS",
            "relative_permittivity": "solvent-only MEA--water mass-fraction mixing",
            "vapor": "neutral incipient vapor evaluated by the pinned ePC-SAFT Engine",
        },
    }
    return (json.dumps(definition, indent=2) + "\n").encode()


README = """# MEA reactive ePC-SAFT parameter bundle

This directory contains the exact nine-species parameter mapping and pinned
ePC-SAFT wheel used by MEA-Thermodynamics on 2026-09-02. It can be used in
absorption-column experiments.

## Scientific use

Verified model choices:

- species: CO2, MEA, H2O, MEAH+, MEACOO-, HCO3-, CO3^2-, H3O+, and OH-;
- reciprocal induced CO2--H2O association and no CO2 self-association;
- Debye--Huckel plus automatically activated corrected SSM+DS electrostatics;
- solvent-only MEA--water mass-fraction relative-permittivity mixing;
- selected R4: ln(K) = 3.3515778178 - 1895.3/T;
- selected CO2 dispersion energy: epsilon/k = 173.44025 K;
- all other coordinates are the values in parameters/parameters.json.

The reaction order, stoichiometry, correlations, units, standard state, and
R1--R3 source-to-common-molality corrections are in
chemistry/reaction-system.json. Compile these correlations at every process
temperature; do not copy an equilibrium-constant value from one validation
state into another temperature.

## Install and verify

Use Python 3.13 on Linux x86_64:

```bash
python3.13 -m venv .venv
.venv/bin/pip install engine/epcsaft-0.2.0.dev0-cp313-cp313-linux_x86_64.whl
.venv/bin/python verify_bundle.py
```

Then load the parameter mapping with:

```python
from pathlib import Path
import epcsaft

root = Path("mea-reactive-epcsaft-parameter-bundle")
parameters = epcsaft.Parameters.from_json(root / "parameters/parameters.json")
model = epcsaft.Mixture(parameters)
```

Construct new column states through `epcsaft.equilibrium` using the species
order and reaction definition in chemistry/reaction-system.json. The retained
validation/state-packet.json is immutable evidence and contains historical
continuation states; do not reuse those continuation states as process-column
initial conditions.

## Fit summary

The automatic-SSM+DS replay evaluates 120/161 pressure states with log10 RMSE
0.4950 and median factor 2.3473. It evaluates 42/44 speciation states and 125
positive targets with log10 RMSE 0.2643. Every one of the 43 failed states is
retained in validation/automatic-extended-full-states.csv.

The populated unique Born diameters and non-unit water solvation factor
activate SSM+DS without separate switches. A zero Born diameter inherits the
same ion diameter used by Debye--Huckel, recovering original Born. The
research notebook records the parameter evidence, structural comparison,
sensitivity results, and next experiments.
"""


VERIFY = r'''"""Verify the extracted MEA handoff and load its parameter mapping."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path


root = Path(__file__).resolve().parent
inventory = json.loads((root / "bundle.json").read_text(encoding="utf-8"))
for item in inventory["files"]:
    path = root / item["path"]
    data = path.read_bytes()
    assert len(data) == item["bytes"], item["path"]
    assert hashlib.sha256(data).hexdigest() == item["sha256"], item["path"]

import epcsaft

parameters = epcsaft.Parameters.from_json(root / "parameters/parameters.json")
specs = {spec.identity: spec for spec in parameters.parameter_specs}
assert float(specs["component/carbon-dioxide/dispersion_energy_over_k"].value.magnitude) == 173.44025
assert abs(float(specs["reaction:R4:correlation:a"].value.magnitude) - 3.3515778177997895) < 1e-14
assert float(specs["reaction:R4:correlation:b_k"].value.magnitude) == -1895.3
print("bundle hashes and ePC-SAFT parameter load: ok")
print(f"parameter fingerprint: {parameters.fingerprint}")
'''


def payloads() -> dict[str, bytes]:
    files = {
        "README.md": README.encode(),
        "verify_bundle.py": VERIFY.encode(),
        "parameters/parameters.json": source(PARAMETERS),
        "chemistry/reaction-system.json": reaction_definition(),
        "engine/epcsaft-0.2.0.dev0-cp313-cp313-linux_x86_64.whl": source(ENGINE),
        "validation/state-packet.json": source(STATE_PACKET),
        "validation/fit-residuals.csv": source(
            ANALYSIS / "results/current-best-fit-residuals.csv"
        ),
        "validation/fit-statistics.csv": source(
            ANALYSIS / "results/current-best-fit-statistics.csv"
        ),
        "validation/non-evaluable-states.csv": source(
            ANALYSIS / "results/figure-calculation-failures.csv"
        ),
        "validation/final-candidate-comparison.csv": source(
            ANALYSIS
            / "results/best-in-slot-campaign/final-full-validation-summary.csv"
        ),
        "validation/automatic-extended-full-states.csv": source(
            ANALYSIS
            / "results/born-permittivity-study/automatic-extended-full-states.csv"
        ),
        "validation/automatic-extended-full-targets.csv": source(
            ANALYSIS
            / "results/born-permittivity-study/automatic-extended-full-targets.csv"
        ),
        "validation/automatic-extended-full-summary.csv": source(
            ANALYSIS
            / "results/born-permittivity-study/automatic-extended-full-summary.csv"
        ),
        "figures/pressure.pdf": source(
            ANALYSIS
            / "figures/pressure/output/pressure-diagnostic-replay.pdf"
        ),
        "documentation/research-notebook.pdf": source(
            ANALYSIS / "results/notebook.pdf"
        ),
    }
    return files


def add(zf: zipfile.ZipFile, name: str, data: bytes) -> None:
    info = zipfile.ZipInfo(f"{ROOT}/{name}", (1980, 1, 1, 0, 0, 0))
    info.compress_type = zipfile.ZIP_STORED
    info.external_attr = 0o100644 << 16
    zf.writestr(info, data)


def main() -> None:
    assert sha256(source(PARAMETERS)) == EXPECTED_PARAMETER_SHA256
    assert sha256(source(STATE_PACKET)) == EXPECTED_STATE_PACKET_SHA256
    assert sha256(source(ENGINE)) == EXPECTED_ENGINE_SHA256
    files = payloads()
    inventory = {
        "schema_version": 1,
        "bundle_id": "mea-reactive-epcsaft-parameter-bundle",
        "bundle_date": "2026-09-02",
        "model": "nine-species reactive aqueous MEA ePC-SAFT",
        "parameter_document_sha256": EXPECTED_PARAMETER_SHA256,
        "engine_wheel_sha256": EXPECTED_ENGINE_SHA256,
        "state_packet_sha256": EXPECTED_STATE_PACKET_SHA256,
        "files": [
            {"path": name, "bytes": len(data), "sha256": sha256(data)}
            for name, data in sorted(files.items())
        ],
    }
    files["bundle.json"] = (json.dumps(inventory, indent=2) + "\n").encode()
    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    with zipfile.ZipFile(OUTPUT, "w") as zf:
        for name, data in sorted(files.items()):
            add(zf, name, data)
    digest = sha256(OUTPUT.read_bytes())
    OUTPUT.with_suffix(".zip.sha256").write_text(
        f"{digest}  {OUTPUT.name}\n", encoding="utf-8"
    )
    print(OUTPUT.relative_to(REPO))
    print(digest)


if __name__ == "__main__":
    main()
