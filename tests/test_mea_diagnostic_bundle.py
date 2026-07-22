from __future__ import annotations

import pytest


pytest.importorskip(
    "epcsaft.records",
    reason="typed bundle records require the exact clean Provider artifact",
)

from epcsaft.records import SingleParameterRecord  # noqa: E402

from MEA.epcsaft_ionic.diagnostic_bundle import (  # noqa: E402
    COMPONENT_IDS,
    build_mea_diagnostic_bundle,
)


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
