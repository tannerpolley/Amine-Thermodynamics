from __future__ import annotations

import numpy as np


PROPERTIES = {
    "CO2": {
        "MW": 44.01e-3,
        "m": 2.079,
        "s": 2.7852,
        "e": 169.21,
        "e_assoc": 0.0,
        "vol_a": 0.0,
        "assoc_scheme": None,
        "dipm": 0.0,
        "dip_num": 1,
        "z": 0.0,
        "dielc": 1.4122,
    },
    "MEA-2B": {
        "MW": 61.08e-3,
        "m": 3.0353,
        "s": 3.0435,
        "e": 277.174,
        "e_assoc": 2586.3,
        "vol_a": 0.037470,
        "assoc_scheme": "2B",
        "dipm": 0.0,
        "dip_num": 1,
        "z": 0.0,
        "dielc": 32.0,
    },
    "H2O-2B-CC": {
        "MW": 18.01528e-3,
        "m": 1.9599,
        "s": 2.362,
        "e": 279.42,
        "e_assoc": 2059.28,
        "vol_a": 0.1750,
        "assoc_scheme": "2B",
        "dipm": 0.0,
        "dip_num": 1,
        "z": 0.0,
        "dielc": 78.09,
    },
    "MEAH+": {
        "MW": 62.09e-3,
        "m": 1.0,
        "s": 3.0435,
        "e": 277.174,
        "e_assoc": 0.0,
        "vol_a": 0.0,
        "assoc_scheme": None,
        "dipm": 0.0,
        "dip_num": 1,
        "z": 1.0,
        "dielc": 8.0,
    },
    "MEACOO-": {
        "MW": 75.07e-3,
        "m": 1.0,
        "s": 3.0435,
        "e": 277.174,
        "e_assoc": 0.0,
        "vol_a": 0.0,
        "assoc_scheme": None,
        "dipm": 0.0,
        "dip_num": 1,
        "z": -1.0,
        "dielc": 8.0,
    },
    "HCO3-": {
        "MW": 61.0168e-3,
        "m": 1.0,
        "s": 3.0,
        "e": 300.0,
        "e_assoc": 0.0,
        "vol_a": 0.0,
        "assoc_scheme": None,
        "dipm": 0.0,
        "dip_num": 1,
        "z": -1.0,
        "dielc": 8.0,
    },
    "CO32-": {
        "MW": 60.01e-3,
        "m": 1.0,
        "s": 3.0,
        "e": 300.0,
        "e_assoc": 0.0,
        "vol_a": 0.0,
        "assoc_scheme": None,
        "dipm": 0.0,
        "dip_num": 1,
        "z": -1.0,
        "dielc": 8.0,
    },
    "H3O+": {
        "MW": 19.02e-3,
        "m": 1.0,
        "s": 3.0,
        "e": 300.0,
        "e_assoc": 0.0,
        "vol_a": 0.0,
        "assoc_scheme": None,
        "dipm": 0.0,
        "dip_num": 1,
        "z": 1.0,
        "dielc": 8.0,
    },
    "OH-": {
        "MW": 17.01e-3,
        "m": 1.0,
        "s": 3.0,
        "e": 300.0,
        "e_assoc": 0.0,
        "vol_a": 0.0,
        "assoc_scheme": None,
        "dipm": 0.0,
        "dip_num": 1,
        "z": -1.0,
        "dielc": 8.0,
    },
}


def _k_ij_value(species_i: str, species_j: str, temperature_K: float) -> float:
    pair = {species_i, species_j}
    if pair == {"CO2", "H2O-2B-CC"}:
        return -2.2e-2 + 4.2e-4 * (temperature_K - 298.0) - 1.7e-6 * (temperature_K - 298.0)
    if pair == {"CO2", "MEA-2B"}:
        return 0.0
    if pair == {"MEA-2B", "H2O-2B-CC"}:
        return 0.250
    if pair == {"MEAH+", "MEACOO-"}:
        return 0.0
    return 0.0


def get_prop_dict(species: list[str], temperature_K: float) -> dict[str, np.ndarray | list[str | None]]:
    prop_dict: dict[str, np.ndarray | list[str | None]] = {}
    for prop in PROPERTIES[species[0]]:
        values = [PROPERTIES[name][prop] for name in species]
        prop_dict[prop] = values if prop == "assoc_scheme" else np.asarray(values)

    n_species = len(species)
    prop_dict["k_ij"] = np.array(
        [[_k_ij_value(left, right, temperature_K) for right in species] for left in species],
        dtype=float,
    )
    prop_dict["k_hb"] = np.zeros((n_species, n_species), dtype=float)
    prop_dict["l_ij"] = np.zeros((n_species, n_species), dtype=float)
    return prop_dict
