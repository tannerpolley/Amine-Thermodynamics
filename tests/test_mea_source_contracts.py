from __future__ import annotations

import copy
import hashlib
import json

import pytest

from MEA.common.mea_source_contracts import (
    load_reaction_contract,
    load_sentinel_contract,
    validate_reaction_contract,
    validate_sentinel_contract,
)


def test_reaction_contract_preserves_primary_source_anchors_and_rejects_conflict() -> None:
    contract = load_reaction_contract()
    summary = validate_reaction_contract(contract)

    assert summary == {
        "reaction_count": 5,
        "reaction_rank": 5,
        "balance_rank": 4,
        "temperature_intersection_k": [293.15, 323.15],
        "provider_executable_temperature_domain_k": [313.15, 313.15],
        "common_source_standard_state": "aqueous-molality-infinite-dilution-water-v1",
        "common_ln_k_298_15_k": [
            -32.23229024933365,
            -14.642290490877887,
            -23.79214802087026,
            -3.031961596511823,
            -21.86574617291778,
        ],
        "source_conversion_ready": True,
        "provider_transform_ready": True,
        "provider_species_order": [
            "carbon-dioxide",
            "monoethanolamine",
            "water",
            "protonated-monoethanolamine",
            "carbamate-anion",
            "bicarbonate-anion",
            "carbonate-anion",
            "hydronium-cation",
            "hydroxide-anion",
        ],
        "provider_transform_sha256": (
            "7817d533f40d5dbe04abe6b6c0c0177da42b7b369da7b79a4a6b877e2c5c366f"
        ),
        "blockers": [],
    }
    assert summary["reaction_rank"] + summary["balance_rank"] == 9

    corrupted = copy.deepcopy(contract)
    corrupted["reactions"][1]["correlation"]["a"] = 231.456
    with pytest.raises(ValueError, match="R2.*coefficients"):
        validate_reaction_contract(corrupted)

    coefficient_drift = copy.deepcopy(contract)
    coefficient_drift["reactions"][3]["correlation"]["a"] = 2.152
    coefficient_drift["reactions"][3]["anchor_ln_k"] += 0.001
    with pytest.raises(ValueError, match="R4.*coefficients"):
        validate_reaction_contract(coefficient_drift)

    source_drift = copy.deepcopy(contract)
    source_drift["source_records"][0]["local_pdf_sha256"] = "0" * 64
    with pytest.raises(ValueError, match="source artifact identities"):
        validate_reaction_contract(source_drift)

    incomplete = copy.deepcopy(contract)
    del incomplete["reactions"][3]["activity_convention"]
    with pytest.raises(ValueError, match="R4.*metadata"):
        validate_reaction_contract(incomplete)

    aliased = copy.deepcopy(contract)
    aliased["source_to_provider_species_identity"][6]["alias"] = "carbonate"
    with pytest.raises(ValueError, match="identity map"):
        validate_reaction_contract(aliased)

    wrong_provider_input = copy.deepcopy(contract)
    wrong_provider_input["provider_transform"]["required_provider_receipt"][
        "required_outputs"
    ][0] = "arbitrary_output"
    with pytest.raises(ValueError, match="Provider transformation"):
        validate_reaction_contract(wrong_provider_input)

    overclaimed_domain = copy.deepcopy(contract)
    payload = overclaimed_domain["provider_transform"]["deterministic_payload"]
    payload["installed_provider_executable_temperature_domain_k"] = [293.15, 323.15]
    overclaimed_domain["provider_transform"]["deterministic_payload_sha256"] = (
        hashlib.sha256(
            json.dumps(
                payload,
                sort_keys=True,
                separators=(",", ":"),
                ensure_ascii=True,
            ).encode("utf-8")
        ).hexdigest()
    )
    with pytest.raises(ValueError, match="Provider transformation"):
        validate_reaction_contract(overclaimed_domain)


def test_wong_sentinel_recomputes_feed_and_remains_fail_closed() -> None:
    reactions = load_reaction_contract()
    sentinel = load_sentinel_contract()
    summary = validate_sentinel_contract(sentinel, reactions)

    assert summary["state_count"] == 1
    assert summary["temperature_k"] == pytest.approx(313.15, abs=0.0)
    assert summary["pressure_pa"] == pytest.approx(100_000.0, abs=0.0)
    assert summary["feed_amounts_mol"] == pytest.approx(
        [0.15, 1.0, 7.911062165006594, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0],
        abs=2.0e-15,
    )
    assert summary["initial_charge_equivalents_mol"] == pytest.approx(0.0, abs=0.0)
    assert summary["reaction_domain_passed"] is True
    assert summary["oxazolidone_exclusion_passed"] is True
    assert summary["provider_regression_input_ready"] is True
    assert summary["source_input_ready"] is True
    assert summary["equilibrium_solver_ready"] is False
    assert summary["equilibrium_sensitivity_ready"] is False
    assert summary["blockers"] == []
    assert summary["bubble_application_interval_frozen"] is True
    assert summary["bubble_full_campaign_pressure_range_pa"] == [
        6105.45,
        3_000_000.0,
    ]
    assert summary["bubble_tracer_pressure_range_pa"] == [6105.45, 300_000.0]
    assert summary["bubble_tracer_ready"] is True
    assert summary["bubble_full_campaign_ready"] is False
    assert summary["bubble_full_campaign_blockers"] == [
        "provider-full-campaign-temperature-pressure-domain-missing",
        "reaction-source-correlation-temperature-domain-missing-above-323.15-k",
    ]

    corrupted = copy.deepcopy(sentinel)
    corrupted["states"][0]["feed_amounts_mol"][2] = 7.9
    with pytest.raises(ValueError, match="feed amounts"):
        validate_sentinel_contract(corrupted, reactions)

    incomplete = copy.deepcopy(sentinel)
    del incomplete["states"][0]["observation_roles"]["species_concentrations"]
    with pytest.raises(ValueError, match="observation roles"):
        validate_sentinel_contract(incomplete, reactions)

    redirected = copy.deepcopy(sentinel)
    redirected["provider_regression_input"]["receipt_path"] = (
        "data/reference/epcsaft_bundles/"
        "mea-co2-h2o-nine-species-diagnostic/1.receipt.json"
    )
    redirected["provider_regression_input"]["receipt_sha256"] = "0" * 64
    with pytest.raises(ValueError, match="canonical Provider-input identities"):
        validate_sentinel_contract(redirected, reactions)

    identity_drift = copy.deepcopy(sentinel)
    identity_drift["provider_regression_input"]["immutable_identities"][
        "parameter_fingerprint"
    ] = "sha256:" + "0" * 64
    with pytest.raises(ValueError, match="canonical Provider-input identities"):
        validate_sentinel_contract(identity_drift, reactions)

    molar_mass_drift = copy.deepcopy(sentinel)
    molar_mass_drift["molar_mass_basis"]["values"]["H2O"] = 0.018
    with pytest.raises(ValueError, match="molar-mass artifact"):
        validate_sentinel_contract(molar_mass_drift, reactions)
