"""Build the deterministic MEA absorption parameter archive."""

from __future__ import annotations

import gzip
import hashlib
import json
import zipfile
from pathlib import Path

from result_freshness import (
    hashes,
    rendered_page,
    require_current_results,
    require_hashes,
)
from MEA.common.mea_source_contracts import EXPECTED_REACTION_CORRELATIONS
from shared_evaluation import (
    MODEL_RUNTIME_DEFAULTS,
    R123_SOURCE_TO_COMMON_MOLALITY_OFFSETS as R123_OFFSETS,
    expand_state_packet,
)


ANALYSIS = Path(__file__).resolve().parents[1]
REPO = ANALYSIS.parents[1]
OUTPUT = ANALYSIS / "results/handoff/mea-reactive-epcsaft-parameter-bundle.zip"
ROOT = "mea-reactive-epcsaft-parameter-bundle"
PARAMETERS = ANALYSIS / "results/selected-current-best-parameters.json"
STATE_PACKET = ANALYSIS / "data/input/state-packet.json.gz"
ENGINE = ANALYSIS / "data/input/engine/epcsaft-0.2.0.dev0-cp313-cp313-linux_x86_64.whl"
EXPECTED_STATE_PACKET_SHA256 = (
    "e9d3ea9903fec9b5239dddcfe5bb8449e9f1a1aff488f0900cc9a91479ba48ba"
)
EXPECTED_ENGINE_SHA256 = (
    "40fba7cfb9c8414152f3e49636c49ae2e3f7099e30040d54d464ccb38355f805"
)


def sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def source(path: Path) -> bytes:
    return path.read_bytes()


def reaction_definition(parameter_bytes: bytes, packet_bytes: bytes) -> bytes:
    packet = expand_state_packet(json.loads(gzip.decompress(packet_bytes)))
    parameters = json.loads(parameter_bytes)
    coefficients = {
        row["reaction_id"]: {
            item["name"]: item["value"]["magnitude"] for item in row["coefficients"]
        }
        for row in parameters["reaction_correlations"]
    }
    system = packet["observations"][0]["request"]["reaction_system"]
    reactions = [
        {
            "reaction_id": "R1",
            "stoichiometry": system["reaction_matrix"][0],
            "ln_k_form": "a + b_k / T + c * ln(T) + d_per_k * T + standard_state_offset",
            "coefficients": coefficients.get(
                "R1",
                {
                    key: value
                    for key, value in EXPECTED_REACTION_CORRELATIONS["R1"].items()
                    if key != "kind"
                },
            ),
            "standard_state_offset": 0.0 if "R1" in coefficients else R123_OFFSETS[0],
            "temperature_domain_k": [273.15, 498.15],
        },
        {
            "reaction_id": "R2",
            "stoichiometry": system["reaction_matrix"][1],
            "ln_k_form": "a + b_k / T + c * ln(T) + d_per_k * T + standard_state_offset",
            "coefficients": coefficients.get(
                "R2",
                {
                    key: value
                    for key, value in EXPECTED_REACTION_CORRELATIONS["R2"].items()
                    if key != "kind"
                },
            ),
            "standard_state_offset": 0.0 if "R2" in coefficients else R123_OFFSETS[1],
            "temperature_domain_k": [293.15, 393.15]
            if "R2" in coefficients
            else [273.15, 498.15],
            "qualification": (
                "Selected common-molality coefficients; offset already folded into a. See the selected parameter provenance and adoption record for the fitted change."
                if "R2" in coefficients
                else "Austgen 1991 source correlation"
            ),
        },
        {
            "reaction_id": "R3",
            "stoichiometry": system["reaction_matrix"][2],
            "ln_k_form": "a + b_k / T + c * ln(T) + d_per_k * T + standard_state_offset",
            "coefficients": coefficients.get(
                "R3",
                {
                    key: value
                    for key, value in EXPECTED_REACTION_CORRELATIONS["R3"].items()
                    if key != "kind"
                },
            ),
            "standard_state_offset": 0.0 if "R3" in coefficients else R123_OFFSETS[2],
            "temperature_domain_k": [273.15, 498.15],
        },
        {
            "reaction_id": "R4",
            "stoichiometry": system["reaction_matrix"][3],
            "ln_k_form": "a + b_k / T",
            "coefficients": coefficients["R4"],
            "temperature_domain_k": [293.15, 393.15],
        },
        {
            "reaction_id": "R5",
            "stoichiometry": system["reaction_matrix"][4],
            "ln_k_form": "-ln(10) * (a_k / T + b + c_per_k * T)",
            "coefficients": coefficients["R5"],
            "temperature_domain_k": [273.15, 323.15],
        },
    ]
    selected_reactions = {
        row["reaction_id"]: row for row in parameters["reaction_correlations"]
    }
    for reaction in reactions:
        selected = selected_reactions.get(reaction["reaction_id"])
        if selected is not None:
            reaction["qualification"] = selected["qualification"]
            reaction["source"] = selected["source"]
            if "candidate_domain_id" in selected:
                reaction["candidate_domain_id"] = selected["candidate_domain_id"]
            # The selected document owns domains as well as fitted coefficients.
            del reaction["temperature_domain_k"]
    definition = {
        "schema_version": 1,
        "temperature_unit": "kelvin",
        "domains": parameters["domains"],
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
ePC-SAFT wheel of the recorded MEA-Thermodynamics exploratory incumbent.
The exact identities are in bundle.json. This is not independent validation
for predictive column use.

## Scientific use

Verified model choices:

- species: CO2, MEA, H2O, MEAH+, MEACOO-, HCO3-, CO3^2-, H3O+, and OH-;
- reciprocal induced CO2--H2O association and no CO2 self-association;
- Debye--Huckel plus automatically activated corrected SSM+DS electrostatics;
- solvent-only MEA--water mass-fraction relative-permittivity mixing;
- reaction coefficients come from the recorded selection (see
  chemistry/reaction-system.json and
  validation/reaction-temperature-fit/adoption-record.json);
- `parameters/parameters.json` preserves the adopted record and `bundle.json`
  supplies its declared shell-Born runtime defaults.

The reaction order, stoichiometry, correlations, units, standard state, and
R1--R3 source-to-common-molality corrections are in
chemistry/reaction-system.json. Compile these correlations at every process
temperature; do not copy an equilibrium-constant value from one validation
state into another temperature.

## Thermal references for non-isothermal use

`thermal/reference-thermochemistry.json` is the species reference enthalpy
and heat-capacity declaration in exact Engine component order, on the
polynomial form of the Engine commit recorded in the file. It is the
unique solution of the five typed reaction constraints, three neutral
thermal anchors (CO2 ideal-gas Shomate; H2O and MEA pure-liquid cp
correlations net of the Engine's residual cp at 1 atm), and one charge gauge
over the declared reference domain. Consult the included thermal validation
record for the measured reaction-reference consistency and evaluated states;
a reference declaration alone does not establish successful equilibrium.
Do not use it above 393.15 K: the source-reference transfer leaves the EOS
domain there at the 1 bar reference pressure.

Species references are shared across phases; vaporization enthalpy is the
EOS residual difference. `thermal/downstream-only-ideal-gas-cp.json` supplies
N2/O2 (and gas-basis CO2/H2O) ideal-gas cp for non-EOS gas components.
`thermal/thermal-reference-validation.*` retain the consistency, pure-liquid
cp, water vaporization, and solution cp checks and the missing evidence list.

## Install and verify

Use Python 3.13 on Linux x86_64:

```bash
python3.13 -m venv .venv
.venv/bin/pip install engine/epcsaft-0.2.0.dev0-cp313-cp313-linux_x86_64.whl
.venv/bin/python verify_bundle.py
```

`verify_bundle.py` applies the `model_runtime_defaults` recorded in
`bundle.json` through `Parameters.from_mapping` before checking the Engine
load. Use the same mapping step when loading the preserved adopted parameter
document in another program.

Construct new column states through `epcsaft.equilibrium` using the species
order and reaction definition in chemistry/reaction-system.json. The retained
validation/state-packet.json.gz is immutable evidence and contains historical
continuation states; do not reuse those continuation states as process-column
initial conditions.

## Fit summary

Current pressure/speciation results and coverage are in validation/fit-statistics.csv
and validation/non-evaluable-states.csv. Their generation identities are in
validation/figure-calculation-record.json. Calorimetry results are in
validation/calorimetry-summary.json. Older model-selection comparisons live
under history/ and must not be presented as predictions of the selected vector.

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

mapping = json.loads(
    (root / "parameters/parameters.json").read_text(encoding="utf-8")
)
for family in mapping.get("model_families", ()):
    if family.get("kind") == "electrolyte" and family.get("choice") == "born":
        for key, value in inventory["model_runtime_defaults"].items():
            family.setdefault(key, value)
parameters = epcsaft.Parameters.from_mapping(mapping)
assert hashlib.sha256((root / "parameters/parameters.json").read_bytes()).hexdigest() == inventory["parameter_document_sha256"]
print("bundle hashes and ePC-SAFT parameter load: ok")
'''


def payloads() -> tuple[dict[str, bytes], dict[str, str]]:
    require_current_results(notebook=True)
    captured = {}

    def source(path: Path) -> bytes:
        data = path.read_bytes()
        captured.update(hashes((path,)))
        return data

    files = {
        "README.md": README.encode(),
        "verify_bundle.py": VERIFY.encode(),
        "parameters/parameters.json": source(PARAMETERS),
        "engine/epcsaft-0.2.0.dev0-cp313-cp313-linux_x86_64.whl": source(ENGINE),
        "validation/state-packet.json.gz": source(STATE_PACKET),
        "validation/fit-residuals.csv": source(
            ANALYSIS / "results/current-best-fit-residuals.csv"
        ),
        "validation/fit-statistics.csv": source(
            ANALYSIS / "results/current-best-fit-statistics.csv"
        ),
        "validation/non-evaluable-states.csv": source(
            ANALYSIS / "results/figure-calculation-failures.csv"
        ),
        "history/final-candidate-comparison.csv": source(
            ANALYSIS / "results/best-in-slot-campaign/final-full-validation-summary.csv"
        ),
        "figures/pressure.pdf": source(
            ANALYSIS / "figures/pressure/output/pressure-diagnostic-replay.pdf"
        ),
        "documentation/research-notebook.html": source(
            rendered_page(ANALYSIS / "notebook.qmd")
        ),
        "validation/figure-calculation-record.json": source(
            ANALYSIS / "results/figure-calculation-record.json"
        ),
        "validation/figure-render-record.json": source(
            ANALYSIS / "results/figure-render-record.json"
        ),
        "validation/notebook-render-record.json": source(
            ANALYSIS / "results/notebook-render-record.json"
        ),
        "validation/calorimetry-summary.json": source(
            ANALYSIS
            / "results/calorimetry/current-selected-direct-enthalpy-summary.json"
        ),
        "thermal/reference-thermochemistry.json": source(
            ANALYSIS
            / "results/calorimetry/current-selected-reference-thermochemistry.json"
        ),
        "thermal/thermal-reference-validation.json": source(
            ANALYSIS / "results/calorimetry/thermal-reference-validation.json"
        ),
        "thermal/thermal-reference-validation.csv": source(
            ANALYSIS / "results/calorimetry/thermal-reference-validation.csv"
        ),
        "thermal/downstream-only-ideal-gas-cp.json": DOWNSTREAM_GAS_CP.encode(),
        **{
            f"validation/reaction-temperature-fit/{name}": source(
                ANALYSIS / "results/reaction-temperature-fit" / name
            )
            for name in (
                "screen-record.json",
                "candidate-record.json",
                "full-validation-record.json",
                "full-validation-targets.csv",
                "adoption-record.json",
                "sensitivity-check-record.json",
                "parity-record.json",
            )
        },
    }
    files["chemistry/reaction-system.json"] = reaction_definition(
        files["parameters/parameters.json"], files["validation/state-packet.json.gz"]
    )
    return files, captured


# Not Engine components; supplied for the absorber gas phase on the same
# ideal-gas cp basis as the CO2 anchor. Shomate coefficients from the NIST
# WebBook (Chase 1998), cp in J/mol/K with t = T/1000.
DOWNSTREAM_GAS_CP = (
    json.dumps(
        {
            "basis": "ideal gas; Shomate cp = A + B t + C t^2 + D t^3 + E / t^2, t = T[K]/1000, J/mol/K",
            "source": "NIST WebBook, Chase 1998",
            "components": {
                "nitrogen": {
                    "range_k": [100, 500],
                    "A": 28.98641,
                    "B": 1.853978,
                    "C": -9.647459,
                    "D": 16.63537,
                    "E": 0.000117,
                },
                "oxygen": {
                    "range_k": [100, 700],
                    "A": 31.32234,
                    "B": -20.23531,
                    "C": 57.86644,
                    "D": -36.50624,
                    "E": -0.007374,
                },
                "carbon-dioxide": {
                    "range_k": [298, 1200],
                    "A": 24.99735,
                    "B": 55.18696,
                    "C": -33.69137,
                    "D": 7.948387,
                    "E": -0.136638,
                },
                "water": {
                    "range_k": [500, 1700],
                    "A": 30.09200,
                    "B": 6.832514,
                    "C": 6.793435,
                    "D": -2.534480,
                    "E": 0.082139,
                    "note": "extrapolated below 500 K; reproduces the JANAF 298.15 K value 33.59 J/mol/K",
                },
            },
            "note": "In the Engine bundle the water and MEA references are liquid-anchored (see thermal/reference-thermochemistry.json); use these ideal-gas values only for N2/O2 and for gas-phase sensible heat of non-EOS components.",
        },
        indent=2,
    )
    + "\n"
)


def add(zf: zipfile.ZipFile, name: str, data: bytes) -> None:
    info = zipfile.ZipInfo(f"{ROOT}/{name}", (1980, 1, 1, 0, 0, 0))
    info.compress_type = zipfile.ZIP_STORED
    info.external_attr = 0o100644 << 16
    zf.writestr(info, data)


def main() -> None:
    parameter_hash = sha256(source(PARAMETERS))
    adoption = json.loads(
        (
            ANALYSIS / "results/reaction-temperature-fit/adoption-record.json"
        ).read_text()
    )
    if parameter_hash != adoption.get("adopted_parameter_sha256"):
        raise ValueError(
            "Selected parameters do not match the recorded adoption; refusing handoff"
        )
    assert sha256(source(STATE_PACKET)) == EXPECTED_STATE_PACKET_SHA256
    assert sha256(source(ENGINE)) == EXPECTED_ENGINE_SHA256
    files, captured = payloads()
    if sha256(files["parameters/parameters.json"]) != parameter_hash:
        raise ValueError("Selected parameters changed during packaging")
    inventory = {
        "schema_version": 1,
        "bundle_id": "mea-reactive-epcsaft-parameter-bundle",
        "model": "nine-species reactive aqueous MEA ePC-SAFT",
        "model_runtime_defaults": MODEL_RUNTIME_DEFAULTS,
        "parameter_document_sha256": parameter_hash,
        "engine_wheel_sha256": EXPECTED_ENGINE_SHA256,
        "state_packet_sha256": EXPECTED_STATE_PACKET_SHA256,
        "files": [
            {"path": name, "bytes": len(data), "sha256": sha256(data)}
            for name, data in sorted(files.items())
        ],
    }
    files["bundle.json"] = (json.dumps(inventory, indent=2) + "\n").encode()
    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    pending = OUTPUT.with_suffix(".zip.tmp")
    with zipfile.ZipFile(pending, "w") as zf:
        for name, data in sorted(files.items()):
            add(zf, name, data)
    require_current_results(notebook=True)
    require_hashes(captured)
    if sha256(source(PARAMETERS)) != parameter_hash:
        pending.unlink()
        raise ValueError("Selected parameters changed during packaging")
    pending.replace(OUTPUT)
    digest = sha256(OUTPUT.read_bytes())
    OUTPUT.with_suffix(".zip.sha256").write_text(
        f"{digest}  {OUTPUT.name}\n", encoding="utf-8"
    )
    print(OUTPUT.relative_to(REPO))
    print(digest)


if __name__ == "__main__":
    main()
