from __future__ import annotations

from pathlib import Path

import numpy as np
import pytest

from MEA.common.mea_source_contracts import (
    common_source_ln_k,
    load_reaction_contract,
)
from MEA.epcsaft_ionic.reduced_tracer import _reaction_consistent_molar_masses


def test_common_source_constants_reproduce_the_313_15_k_vector() -> None:
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
