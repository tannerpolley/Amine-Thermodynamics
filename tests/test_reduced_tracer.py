from __future__ import annotations

import math
from pathlib import Path

import numpy as np
import pytest

from MEA.common.mea_source_contracts import (
    common_source_ln_k,
    load_reaction_contract,
)
from MEA.epcsaft_ionic.reduced_tracer import _reaction_consistent_molar_masses


def test_common_source_constants_reproduce_the_frozen_313_15_k_vector() -> None:
    assert common_source_ln_k(313.15) == pytest.approx(
        (
            -31.17540213354659,
            -14.505037067112742,
            -23.53653838436904,
            -2.7836958326680508,
            -20.889878783626997,
        ),
        rel=0.0,
        abs=5.0e-14,
    )


def test_source_rounded_masses_are_projected_only_for_exact_conservation() -> None:
    reaction_contract = load_reaction_contract()
    elements = reaction_contract["balance_row_order"]
    species = reaction_contract["species"]
    balance_matrix = tuple(
        tuple(float(row["formula"][element]) for row in species)
        for element in elements
    )
    component_ids = tuple(reaction_contract["provider_species_order"])
    bundle = (
        Path(__file__).resolve().parents[1]
        / "data/reference/epcsaft_bundles"
        / "mea-co2-h2o-nine-species-regression-input/1"
    )
    projected = _reaction_consistent_molar_masses(
        bundle, component_ids, balance_matrix
    )
    reactions = np.asarray(
        [row["stoichiometry"] for row in reaction_contract["reactions"]],
        dtype=float,
    )

    assert np.max(np.abs(reactions @ np.asarray(projected))) < 2.0e-16
    assert projected == pytest.approx(
        (
            0.04400839250000016,
            0.06108053583333324,
            0.018015221250000046,
            0.06208747291666654,
            0.1040819912500001,
            0.06101667666666691,
            0.060009739583333596,
            0.019022158333333344,
            0.01700828416666675,
        ),
        rel=0.0,
        abs=2.0e-16,
    )


def test_installed_reduced_tracer_emits_two_exact_columns() -> None:
    pytest.importorskip("epcsaft_equilibrium")
    from MEA.epcsaft_ionic.reduced_tracer import build_reduced_tracer_input

    tracer = build_reduced_tracer_input()
    result = tracer.evaluator.evaluate(tracer.primary_start, with_jacobian=True)

    failure = "\n".join(
        (
            f"error={result['error']!r}; values={result['values']!r}",
            *(
                "; ".join(f"{key}={row[key]!r}" for key in row)
                for row in result["row_results"]
            ),
        )
    )
    assert result["status"] == 0, failure
    assert tracer.observed_values == (574.0, 0.0502)
    assert tracer.natural_log_scales == pytest.approx(
        (math.log(10.0), math.log(10.0)), rel=0.0, abs=0.0
    )
    assert result["parameter_ids"] == [
        "segment_diameter;component;protonated-monoethanolamine",
        "segment_diameter;component;carbamate-anion",
    ]
    assert result["row_ids"] == [
        "vle_obs_0137::pco2",
        "Bottinger2008_state_049::MEACOO-",
    ]
    assert result["primitive_ids"] == [
        "neutral_component_fugacity_pa;carbon-dioxide",
        "species_mole_fraction;carbamate-anion",
    ]
    assert result["primitive_units"] == ["Pa", "dimensionless"]
    assert result["transform_ids"] == ["natural_log", "natural_log"]
    assert result["expected_provider_topology_fingerprint"] == (
        "sha256:4cd30249026b7361ee68b618f7437de081b0339e5a7b0cc41165930a01a4e762"
    )
    assert result["provider_artifact_identity"].startswith("epcsaft==0.2.0.dev0;")
    assert result["owner_artifact_identity"].startswith(
        "epcsaft-equilibrium==0.2.0.dev0;"
    )
    assert result["contract_fingerprint"].startswith("sha256:")
    assert result["artifact_identity"].startswith("sha256:")
    assert len(result["values"]) == 2
    assert len(result["jacobian"]) == 4
    assert all(value > 0.0 and math.isfinite(value) for value in result["values"])
    assert all(math.isfinite(value) for value in result["jacobian"])
    assert [row["status"] for row in result["row_results"]] == [0, 0]

    values = np.asarray(result["values"], dtype=float)
    direct = np.asarray(result["jacobian"], dtype=float).reshape(2, 2)
    scaled_log10 = (
        direct / values[:, None] / np.asarray(tracer.natural_log_scales)[:, None]
    ) * np.asarray(tracer.affine_scales)[None, :]
    assert np.linalg.matrix_rank(scaled_log10) == 2
    assert np.linalg.cond(scaled_log10) <= 1.0e6
