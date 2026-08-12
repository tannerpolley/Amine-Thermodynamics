from __future__ import annotations

import math
from pathlib import Path

import pytest

from epcsaft import Mixture, Parameters, unit_registry as u


COMPONENT_IDS = (
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
COMPOSITION = (0.02, 0.10, 0.8025, 0.03, 0.02, 0.01, 0.0025, 0.01, 0.005)
BUNDLE = (
    Path(__file__).resolve().parents[1]
    / "data/reference/epcsaft_bundles"
    / "mea-co2-h2o-nine-species-regression-input/1"
)


def test_unified_engine_loads_the_mea_bundle_and_solves_a_liquid_state() -> None:
    parameters = Parameters.from_bundle(BUNDLE, components=COMPONENT_IDS)
    assert parameters.fingerprint == (
        "sha256:7ac9cf016af9086a8f1c70189b524cbad1e29a75bb742862106d34ba7ab44ae0"
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
