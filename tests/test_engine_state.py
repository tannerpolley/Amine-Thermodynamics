from __future__ import annotations

import math

import pytest

from epcsaft import Mixture, unit_registry as u

from MEA.epcsaft_ionic.parameter_document import COMPONENT_IDS, load_parameters


COMPOSITION = (0.02, 0.10, 0.8025, 0.03, 0.02, 0.01, 0.0025, 0.01, 0.005)


def test_unified_engine_loads_the_mea_packet_and_solves_a_liquid_state() -> None:
    parameters = load_parameters()
    assert parameters.component_ids == COMPONENT_IDS
    assert parameters.fingerprint == (
        "sha256:c621cd37257fdaa8946653cf3e3f36329f6b4a07af10afc082db8f22f7e911a7"
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
