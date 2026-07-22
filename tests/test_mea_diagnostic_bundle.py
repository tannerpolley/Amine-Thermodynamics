from __future__ import annotations

import hashlib
import json
import math
from pathlib import Path

import pytest


pytest.importorskip(
    "epcsaft.records",
    reason="typed bundle records require the exact clean Provider artifact",
)

from epcsaft.records import SingleParameterRecord  # noqa: E402
from epcsaft import (  # noqa: E402
    EPCSAFT,
    ParameterBundle,
    native_sdk,
    unit_registry as u,
)

from MEA.epcsaft_ionic.diagnostic_bundle import (  # noqa: E402
    COMPONENT_IDS,
    REPO_ROOT,
    build_mea_diagnostic_bundle,
)


CANONICAL_BUNDLE = (
    REPO_ROOT
    / "data"
    / "reference"
    / "epcsaft_bundles"
    / "mea-co2-h2o-nine-species-diagnostic"
    / "1"
)
RECEIPT = CANONICAL_BUNDLE.parent / "1.receipt.json"
DIAGNOSTIC_COMPOSITION = (
    0.02,
    0.10,
    0.8025,
    0.03,
    0.02,
    0.01,
    0.0025,
    0.01,
    0.005,
)


def _file_hashes(path: Path) -> dict[str, str]:
    return {
        item.relative_to(path).as_posix(): hashlib.sha256(item.read_bytes()).hexdigest()
        for item in sorted(path.rglob("*"))
        if item.is_file()
    }


def test_mea_bundle_has_exact_species_charge_and_provenance_contract() -> None:
    bundle = build_mea_diagnostic_bundle(purpose="package-test-fixture")
    selected = bundle.select(COMPONENT_IDS)

    assert COMPONENT_IDS == (
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
    assert selected.component_ids == COMPONENT_IDS
    charges = {
        record.component_id: int(record.value)
        for record in selected.records
        if isinstance(record, SingleParameterRecord)
        and record.family == "charge_number"
    }
    assert tuple(charges[component_id] for component_id in COMPONENT_IDS) == (
        0,
        0,
        0,
        1,
        -1,
        -1,
        -2,
        1,
        -1,
    )
    assert bundle.sources
    assert bundle.domains
    source_ids = {source.source_id for source in bundle.sources}
    domain_ids = {domain.domain_id for domain in bundle.domains}
    for record in bundle.records:
        assert record.source_id in source_ids
        assert record.domain_id in domain_ids
        assert record.locator.strip()
    assert any(
        "provisional-historical-evaluation" in record.locator
        for record in bundle.records
    )


def test_user_bundle_round_trip_matches_canonical_artifact(tmp_path: Path) -> None:
    bundle = build_mea_diagnostic_bundle(purpose="user-provided")
    emitted = tmp_path / "bundle"
    bundle.to_path(emitted)
    loaded = ParameterBundle.from_path(emitted)

    assert loaded.purpose == "user-provided"
    assert loaded.fingerprint == bundle.fingerprint
    assert loaded.select(COMPONENT_IDS).fingerprint == bundle.select(
        COMPONENT_IDS
    ).fingerprint
    assert CANONICAL_BUNDLE.is_dir()
    assert _file_hashes(emitted) == _file_hashes(CANONICAL_BUNDLE)


def test_installed_provider_executes_canonical_bundle_and_exposes_native_sdk() -> None:
    bundle = ParameterBundle.from_path(CANONICAL_BUNDLE)
    model = EPCSAFT(bundle.select(COMPONENT_IDS))
    state = model.evaluate(
        temperature=313.15 * u.kelvin,
        molar_density=40000 * u.mole / u.meter**3,
        mole_fractions=DIAGNOSTIC_COMPOSITION,
    )
    capsule = native_sdk(model)
    receipt = json.loads(RECEIPT.read_text(encoding="utf-8"))

    assert model.component_ids == COMPONENT_IDS
    assert math.fsum(DIAGNOSTIC_COMPOSITION) == 1.0
    assert math.fsum(
        fraction * charge
        for fraction, charge in zip(
            DIAGNOSTIC_COMPOSITION,
            receipt["charges"],
            strict=True,
        )
    ) == pytest.approx(0.0, abs=2e-18)
    assert all(
        math.isfinite(value)
        for value in (
            state.residual_helmholtz,
            state.compressibility_factor,
            state.pressure.to("pascal").magnitude,
            *state.residual_chemical_potential_over_rt,
        )
    )
    assert type(capsule).__name__ == "PyCapsule"
    assert receipt["provider"]["commit"] == (
        "5c4cd54b3596e51331ca9f6c871daec34a72eb4f"
    )
    assert receipt["smoke_state"]["temperature_k"] == 313.15
    assert receipt["smoke_state"]["molar_density_mol_per_m3"] == 40000.0
    assert receipt["smoke_state"]["mole_fractions"] == list(
        DIAGNOSTIC_COMPOSITION
    )
    assert receipt["smoke_state"]["pressure_pa"] == pytest.approx(
        state.pressure.to("pascal").magnitude
    )
    assert receipt["smoke_state"]["residual_helmholtz"] == pytest.approx(
        state.residual_helmholtz
    )
    assert receipt["smoke_state"]["native_sdk_capsule"] == (
        "epcsaft.native_sdk.v1"
    )
