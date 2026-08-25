from __future__ import annotations

import math

import pytest

from epcsaft import Mixture, Parameters, unit_registry as u

from MEA.common.config import REPO_ROOT
from MEA.epcsaft_ionic.parameter_document import (
    COMPONENT_IDS,
    expand_parameter_domain,
    load_parameters,
    materialize_parameter_candidate,
    parameter_mapping,
)


COMPOSITION = (0.02, 0.10, 0.8025, 0.03, 0.02, 0.01, 0.0025, 0.01, 0.005)


def test_compact_parameter_candidates_rebuild_exact_engine_documents() -> None:
    results = (
        REPO_ROOT
        / "analyses/phase3/ionic_epcsaft_regression/born_permittivity_sensitivity/results"
    )
    for label in (
        "final_shared_refinement",
        "full_predictive_refinement",
        "predictive_training_refinement",
    ):
        mapping = materialize_parameter_candidate(results / label / "summary.json")
        assert Parameters.from_mapping(mapping).fingerprint


def test_execution_domain_expands_to_requested_states_without_mutating_source() -> None:
    source = parameter_mapping()
    expanded = expand_parameter_domain(
        source, temperatures_k=(303.15, 323.15), pressures_pa=(100_000.0, 6_080_000.0)
    )
    assert source["domains"][0]["pressure_max"]["magnitude"] == 300_000.0
    assert expanded["domains"][0]["temperature_min"]["magnitude"] == 303.15
    assert expanded["domains"][0]["temperature_max"]["magnitude"] == 323.15
    assert expanded["domains"][0]["pressure_max"]["magnitude"] == 6_080_000.0


def test_unified_engine_loads_the_mea_packet_and_solves_a_liquid_state() -> None:
    parameters = load_parameters()
    assert parameters.component_ids == COMPONENT_IDS
    assert parameters.fingerprint == (
        "sha256:d1e35ffa905f4a8c18989f2db191bdbf9533bdb2e5fadcb57060880a8c630bdc"
    )

    state = Mixture(parameters).state(
        T=313.15 * u.kelvin,
        P=100_000.0 * u.pascal,
        x=COMPOSITION,
        phase="liquid",
    )
    density = float(state.molar_density.to("mole / meter**3").magnitude)
    pressure = float(state.pressure.to("pascal").magnitude)
    assert math.isfinite(density) and density > 0.0
    assert pressure == pytest.approx(100_000.0, abs=1.0e-5)


def test_mea_packet_supports_source_component_permittivity_mixing() -> None:
    mapping = parameter_mapping(permittivity="component-permittivity-mixing")
    charged = [
        component
        for component in mapping["components"]
        if component["fixed"]["charge_number"]["value"]["magnitude"]
    ]
    assert all(
        next(
            coefficient["value"]["magnitude"]
            for coefficient in component["coefficients"]
            if coefficient["family"] == "relative_permittivity"
        )
        == 8.0
        for component in charged
    )
    assert all(
        coefficient["family"] != "ion_fraction_suppression_coefficient"
        for coefficient in mapping["model_coefficients"]
    )
    assert load_parameters(
        permittivity="component-permittivity-mixing"
    ).component_ids == COMPONENT_IDS


def test_mea_packet_supports_zuber_ion_specific_suppression() -> None:
    coefficients = {
        "protonated-monoethanolamine": 2.60,
        "carbamate-anion": 7.89,
        "bicarbonate-anion": 7.89,
        "carbonate-anion": 7.89,
        "hydronium-cation": 9.55,
        "hydroxide-anion": 13.96,
    }
    mapping = parameter_mapping(
        permittivity="ion-specific-suppression",
        ion_specific_suppression=coefficients,
    )
    actual = {
        component["component_id"]: next(
            coefficient["value"]["magnitude"]
            for coefficient in component["coefficients"]
            if coefficient["family"] == "ion_specific_suppression_coefficient"
        )
        for component in mapping["components"]
        if component["component_id"] in coefficients
    }
    assert actual == coefficients
    assert load_parameters(
        permittivity="ion-specific-suppression",
        ion_specific_suppression=coefficients,
    ).component_ids == COMPONENT_IDS
