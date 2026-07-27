from __future__ import annotations

import copy

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
        "common_source_standard_state": "aqueous-molality-infinite-dilution-water-v1",
        "common_ln_k_298_15_k": [
            -32.23229024933365,
            -14.642290490877887,
            -23.79214802087026,
            -3.031961596511823,
            -21.86574617291778,
        ],
        "source_conversion_ready": True,
        "provider_transform_ready": False,
        "blockers": [
            "provider-neutral-reference-unavailable-until-qualified-bundle-domain",
        ],
    }
    assert summary["reaction_rank"] + summary["balance_rank"] == 9

    corrupted = copy.deepcopy(contract)
    corrupted["reactions"][1]["correlation"]["a"] = 231.456
    with pytest.raises(ValueError, match="R2.*anchor"):
        validate_reaction_contract(corrupted)

    incomplete = copy.deepcopy(contract)
    del incomplete["reactions"][3]["activity_convention"]
    with pytest.raises(ValueError, match="R4.*metadata"):
        validate_reaction_contract(incomplete)


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
    assert summary["equilibrium_ready"] is False
    assert summary["blockers"] == [
        "provider-parameter-bundle-provisional",
        "provider-applicability-domain-unknown",
    ]

    corrupted = copy.deepcopy(sentinel)
    corrupted["states"][0]["feed_amounts_mol"][2] = 7.9
    with pytest.raises(ValueError, match="feed amounts"):
        validate_sentinel_contract(corrupted, reactions)

    incomplete = copy.deepcopy(sentinel)
    del incomplete["states"][0]["observation_roles"]["species_concentrations"]
    with pytest.raises(ValueError, match="observation roles"):
        validate_sentinel_contract(incomplete, reactions)
