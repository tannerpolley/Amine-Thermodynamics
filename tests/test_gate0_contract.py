from __future__ import annotations

import copy

import pytest

from MEA.common.data_access import (
    load_pco2_metrology_manifest,
    load_regression_readiness_summary,
    load_regression_vle_view,
    load_speciation_target_membership,
    regression_split_hash,
)
from MEA.epcsaft_ionic.preregistration import (
    PreregistrationError,
    load_gate0_preregistration,
    validate_gate0_preregistration,
)


def test_gate0_observation_contracts_fail_closed() -> None:
    pressure = load_pco2_metrology_manifest(executable_only=False)
    assert len(pressure) == 327
    assert set(pressure["measurement_origin"]) <= {
        "direct_partial_pressure",
        "calibration_derived_partial_pressure",
        "total_pressure_derived",
        "model_derived",
        "unresolved",
    }
    assert not pressure.loc[
        pressure["target_eligible"].eq("yes"), "measurement_origin"
    ].isin({"model_derived", "unresolved"}).any()
    assert pressure.loc[pressure["target_eligible"].eq("yes"), "source_locator"].ne("").all()
    assert pressure.loc[pressure["target_eligible"].eq("yes"), "state_pressure_pa"].ne("").all()
    assert pressure["uncertainty_status"].ne("").all()

    speciation = load_speciation_target_membership(executable_only=False)
    executable = speciation.loc[speciation["target_eligible"].eq("yes")]
    assert not executable["measurement_role"].str.contains("zero").any()
    aggregates = executable.loc[
        executable["measurement_role"].eq("aggregate_direct_positive")
    ]
    assert aggregates["linear_coefficients"].eq('{"MEA":1.0,"MEAH+":1.0}').all()
    assert aggregates["measurement_identity"].ne("").all()
    assert aggregates["covariance_status"].ne("").all()
    aggregate_states = set(aggregates["state_id"])
    assert not executable.loc[
        executable["state_id"].isin(aggregate_states)
        & executable["species"].isin({"MEA", "MEAH+"})
    ].shape[0]

    assert regression_split_hash() == (
        "af205ad5968667cf25dc9205d780738035769664a94cc9a421cd3c67148ff804"
    )
    assert len(load_regression_vle_view()) == 24
    assert len(load_regression_vle_view(role="reserved_validation")) == 97
    assert load_regression_readiness_summary()["executable_observation_counts"] == {
        "speciation": {"active_training": 131, "reserved_validation": 67},
        "vle_pressure": {"active_training": 24, "reserved_validation": 97},
    }


def test_gate0_preregistration_freezes_three_coordinates_without_admitting_fit() -> None:
    contract = load_gate0_preregistration()
    assert contract["status"] == "GATE_0_FROZEN_EXECUTION_BLOCKED"
    assert [row["identity"] for row in contract["active_coordinates"]] == [
        "MEAH+::sigma",
        "MEAH+::epsilon_over_k",
        "MEACOO-::sigma",
    ]
    assert contract["multistart"] == {
        "count": 32,
        "design": "scrambled_sobol_in_affine_coordinates",
        "seed": 390035,
        "include_provisional_seed": True,
    }
    assert contract["regularization"]["status"] == "NOT_ADMITTED_NO_IMMUTABLE_SCALE"
    assert contract["heat_of_absorption"]["status"] == "NOT_ADMITTED"
    assert contract["tracer"]["selected_state_ids"] == []

    drifted = copy.deepcopy(contract)
    drifted["fixed_terms"][0] = "arbitrary"
    with pytest.raises(PreregistrationError, match="frozen contract drifted"):
        validate_gate0_preregistration(drifted)
