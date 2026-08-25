from __future__ import annotations

import csv
from collections.abc import Mapping
from copy import deepcopy
import hashlib
import json
import math
from pathlib import Path
import tomllib
from typing import Literal

import epcsaft

from MEA.common.config import REPO_ROOT


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
PARAMETER_ROOT = (
    REPO_ROOT
    / "data/reference/epcsaft_bundles"
    / "mea-co2-h2o-nine-species-regression-input/1"
)

_FIXED_FAMILIES = frozenset({"molar_mass", "charge_number"})
_FAMILY_UNITS = {
    "molar_mass": "kilogram / mole",
    "charge_number": "elementary-charge",
    "segment_count": "dimensionless",
    "segment_diameter": "angstrom",
    "dispersion_energy_over_k": "kelvin",
    "relative_permittivity": "dimensionless",
    "packing_diameter": "angstrom",
    "debye_huckel_diameter": "angstrom",
    "born_diameter": "angstrom",
    "solvation_factor": "dimensionless",
    "k_ij": "dimensionless",
    "association_energy_over_k": "kelvin",
    "association_volume": "dimensionless",
    "ionic_region_relative_permittivity": "dimensionless",
    "ion_fraction_suppression_coefficient": "dimensionless",
    "ion_specific_suppression_coefficient": "dimensionless",
}


def expand_parameter_domain(
    mapping: dict[str, object],
    *,
    temperatures_k: tuple[float, ...] = (),
    pressures_pa: tuple[float, ...] = (),
) -> dict[str, object]:
    """Return a parameter document whose execution domain includes given states."""

    temperatures = tuple(float(value) for value in temperatures_k)
    pressures = tuple(float(value) for value in pressures_pa)
    if any(not math.isfinite(value) or value <= 0.0 for value in temperatures + pressures):
        raise ValueError("execution-domain temperatures and pressures must be positive")
    expanded = deepcopy(mapping)
    for domain in expanded["domains"]:
        if temperatures:
            domain["temperature_min"]["magnitude"] = min(
                float(domain["temperature_min"]["magnitude"]), *temperatures
            )
            domain["temperature_max"]["magnitude"] = max(
                float(domain["temperature_max"]["magnitude"]), *temperatures
            )
        if pressures:
            domain["pressure_min"]["magnitude"] = min(
                float(domain["pressure_min"]["magnitude"]), *pressures
            )
            domain["pressure_max"]["magnitude"] = max(
                float(domain["pressure_max"]["magnitude"]), *pressures
            )
    return expanded


def set_parameter_values(
    mapping: dict[str, object], values: Mapping[str, object]
) -> None:
    """Set identified parameter magnitudes in one Engine mapping."""

    remaining = set(values)

    def apply(item: object) -> None:
        if isinstance(item, dict):
            identity = item.get("identity")
            value = item.get("value")
            if identity in remaining and isinstance(value, dict):
                value["magnitude"] = values[identity]
                remaining.remove(identity)
            for child in item.values():
                apply(child)
        elif isinstance(item, list):
            for child in item:
                apply(child)

    apply(mapping)
    if remaining:
        raise RuntimeError(
            "Parameter identities missing from base mapping: " + ", ".join(sorted(remaining))
        )


def materialize_parameter_candidate(summary_path: Path) -> dict[str, object]:
    """Rebuild one exact fitted mapping from its compact scientific receipt."""

    summary = json.loads(summary_path.read_text(encoding="utf-8"))
    receipt = summary.get("parameter_candidate")
    values = summary.get("fitted_values")
    if not isinstance(receipt, dict) or not isinstance(values, dict):
        raise RuntimeError(f"Invalid parameter-candidate summary: {summary_path}")

    relative_base = Path(str(receipt["base_parameter_mapping"]))
    if relative_base.is_absolute() or ".." in relative_base.parts:
        raise RuntimeError(f"Invalid parameter-candidate base path: {relative_base}")
    mapping = json.loads((REPO_ROOT / relative_base).read_text(encoding="utf-8"))
    domain = receipt["domain"]
    mapping = expand_parameter_domain(
        mapping,
        temperatures_k=tuple(domain["temperature_range_k"]),
        pressures_pa=tuple(domain["pressure_range_pa"]),
    )
    set_parameter_values(mapping, values)

    payload = (json.dumps(mapping, indent=2, sort_keys=True) + "\n").encode()
    actual = f"sha256:{hashlib.sha256(payload).hexdigest()}"
    if actual != receipt["sha256"]:
        raise RuntimeError(
            f"Parameter-candidate hash mismatch: expected {receipt['sha256']}, got {actual}"
        )
    return mapping


def _rows(name: str) -> list[dict[str, str]]:
    with (PARAMETER_ROOT / name).open(newline="", encoding="utf-8") as handle:
        return list(csv.DictReader(handle))


def _provenance(row: dict[str, str]) -> dict[str, str]:
    return {
        "source_id": row["source_id"],
        "locator": row["locator"],
        "domain_id": row["domain_id"],
    }


def _value(row: dict[str, str]) -> dict[str, object]:
    family = row["family"]
    magnitude: int | float
    if family == "charge_number":
        magnitude = int(row["value"])
    else:
        magnitude = float(row["value"])
    return {
        "magnitude": magnitude,
        "unit": row["unit"] or _FAMILY_UNITS[family],
    }


def _model_families(
    permittivity: Literal[
        "solvent-only",
        "ion-fraction-suppression",
        "component-permittivity-mixing",
        "ion-specific-suppression",
    ],
) -> list[dict[str, object]]:
    provenance = {
        "source_id": "mea-retained-phase-two-artifact",
        "locator": (
            "data/reference/MEA/manifests/reactive_vle_model_configurations.json:"
            "diagnostic-explicit-model-switches"
        ),
        "domain_id": "mea-tracer-313-15-k-fit-range",
    }
    choices = (
        ("base", "model/base", "pc-saft"),
        ("association", "model/association", "general-site"),
        ("electrolyte", "model/electrolyte", "born"),
        (
            "permittivity",
            "model/relative_permittivity",
            permittivity,
        ),
        ("polar", "model/polar", "none"),
    )
    result: list[dict[str, object]] = []
    for kind, family_id, choice in choices:
        item: dict[str, object] = {
            "family_id": family_id,
            "kind": kind,
            "choice": choice,
            "provenance": dict(provenance),
        }
        if kind == "electrolyte":
            item.update({"c_shell": 1.0, "c_dielectric": 1.0})
        result.append(item)
    return result


def parameter_mapping(
    *,
    permittivity: Literal[
        "solvent-only",
        "ion-fraction-suppression",
        "component-permittivity-mixing",
        "ion-specific-suppression",
    ] = "ion-fraction-suppression",
    ion_specific_suppression: Mapping[str, float] | None = None,
) -> dict[str, object]:
    """Translate the retained CSV packet into the unified Engine schema.

    The packet is intentionally diagnostic: this function preserves its row
    provenance and does not qualify its provisional ionic or dielectric data.
    """

    bundle = tomllib.loads((PARAMETER_ROOT / "bundle.toml").read_text())
    component_rows = {row["component_id"]: row for row in _rows("components.csv")}
    single_rows = _rows("single.csv")
    model_rows = _rows("model.csv")
    ionic_permittivity = next(
        row
        for row in model_rows
        if row["family"] == "ionic_region_relative_permittivity"
    )
    singles_by_component: dict[str, list[dict[str, str]]] = {
        component_id: [] for component_id in COMPONENT_IDS
    }
    for row in single_rows:
        singles_by_component[row["component_id"]].append(row)
    charged_components = {
        component_id
        for component_id, rows in singles_by_component.items()
        if int(next(row["value"] for row in rows if row["family"] == "charge_number"))
    }
    if permittivity == "ion-specific-suppression":
        missing = charged_components - set(ion_specific_suppression or ())
        if missing:
            raise ValueError(
                "ion-specific suppression coefficients missing for "
                + ", ".join(sorted(missing))
            )
    elif ion_specific_suppression is not None:
        raise ValueError(
            "ion-specific suppression coefficients require ion-specific-suppression"
        )

    components: list[dict[str, object]] = []
    for component_id in COMPONENT_IDS:
        source = component_rows[component_id]
        fixed: dict[str, object] = {}
        coefficients: list[dict[str, object]] = []
        for row in singles_by_component[component_id]:
            entry = {
                "value": _value(row),
                "provenance": _provenance(row),
            }
            if row["family"] in _FIXED_FAMILIES:
                fixed[row["family"]] = entry
            else:
                coefficients.append(
                    {
                        "identity": f"component/{component_id}/{row['family']}",
                        "family": row["family"],
                        **entry,
                    }
                )
        charge = int(
            next(
                row["value"]
                for row in singles_by_component[component_id]
                if row["family"] == "charge_number"
            )
        )
        if charge:
            sigma_row = next(
                row
                for row in singles_by_component[component_id]
                if row["family"] == "segment_diameter"
            )
            for family in ("packing_diameter", "debye_huckel_diameter"):
                coefficients.append(
                    {
                        "identity": f"component/{component_id}/{family}",
                        "family": family,
                        "value": {
                            "magnitude": 0.88 * float(sigma_row["value"]),
                            "unit": "angstrom",
                        },
                        "provenance": {
                            **_provenance(sigma_row),
                            "locator": (
                                f"{sigma_row['locator']}:derived-{family}=0.88-sigma:"
                                "fixed-ssm-diameter-convention"
                            ),
                        },
                    }
                )
            if permittivity == "component-permittivity-mixing":
                coefficients.append(
                    {
                        "identity": f"component/{component_id}/relative_permittivity",
                        "family": "relative_permittivity",
                        "value": _value(ionic_permittivity),
                        "provenance": _provenance(ionic_permittivity),
                    }
                )
            elif permittivity == "ion-specific-suppression":
                assert ion_specific_suppression is not None
                coefficients.append(
                    {
                        "identity": (
                            f"component/{component_id}/"
                            "ion_specific_suppression_coefficient"
                        ),
                        "family": "ion_specific_suppression_coefficient",
                        "value": {
                            "magnitude": float(ion_specific_suppression[component_id]),
                            "unit": "dimensionless",
                        },
                        "provenance": {
                            "source_id": "zuber-et-al-2014",
                            "locator": (
                                "Zuber et al. (2014), Eqs. 8-9 and Tables 2/9; "
                                "analysis-declared aqueous coefficient assignment"
                            ),
                            "domain_id": "mea-tracer-313-15-k-fit-range",
                        },
                    }
                )
        components.append(
            {
                "component_id": component_id,
                "name": source["name"] or None,
                "aliases": json.loads(source["aliases"] or "[]"),
                "fixed": fixed,
                "coefficients": sorted(
                    coefficients, key=lambda item: str(item["identity"])
                ),
            }
        )

    pairs = [
        {
            "component_id_a": row["component_id_a"],
            "component_id_b": row["component_id_b"],
            "coefficients": [
                {
                    "identity": (
                        f"pair/{row['component_id_a']}/{row['component_id_b']}/"
                        f"{row['family']}"
                    ),
                    "family": row["family"],
                    "value": _value(row),
                    "provenance": _provenance(row),
                }
            ],
        }
        for row in _rows("pair.csv")
    ]

    site_rows = _rows("sites.csv")
    edge_rows: dict[
        tuple[tuple[str, str], tuple[str, str]], dict[str, dict[str, str]]
    ] = {}
    for row in _rows("association.csv"):
        endpoints = tuple(
            sorted(
                (
                    (row["component_id_a"], row["site_id_a"]),
                    (row["component_id_b"], row["site_id_b"]),
                )
            )
        )
        edge_rows.setdefault(endpoints, {})[row["family"]] = row
    edges: list[dict[str, object]] = []
    for endpoints, families in sorted(edge_rows.items()):
        energy = families["association_energy_over_k"]
        volume = families["association_volume"]
        prefix = (
            f"association/{endpoints[0][0]}/{endpoints[0][1]}/"
            f"{endpoints[1][0]}/{endpoints[1][1]}"
        )
        edges.append(
            {
                "endpoint_a": {
                    "component_id": endpoints[0][0],
                    "site_id": endpoints[0][1],
                },
                "endpoint_b": {
                    "component_id": endpoints[1][0],
                    "site_id": endpoints[1][1],
                },
                "energy_over_k": {
                    "identity": f"{prefix}/energy_over_k",
                    "value": _value(energy),
                },
                "volume": {
                    "identity": f"{prefix}/volume",
                    "value": _value(volume),
                },
                "source": {
                    "kind": "explicit",
                    "provenance": list(
                        {
                            tuple(sorted(item.items())): item
                            for item in (_provenance(energy), _provenance(volume))
                        }.values()
                    ),
                },
            }
        )

    induced_provenance = {
        "source_id": "schick-2023-pabsch-2020-induced-association",
        "locator": (
            "Schick et al. (2023), Table 1 and Section 2.4.2; "
            "Pabsch et al. (2020) CO2-water parameterization"
        ),
        "domain_id": "mea-tracer-313-15-k-fit-range",
    }
    for site_id, site_class in (("a", "a"), ("b", "b")):
        site_rows.append(
            {
                "component_id": "carbon-dioxide",
                "site_id": site_id,
                "site_class": site_class,
                "multiplicity": "1",
                **induced_provenance,
            }
        )
    for co2_site, water_site in (("a", "b"), ("b", "a")):
        prefix = f"association/carbon-dioxide/{co2_site}/water/{water_site}"
        edges.append(
            {
                "endpoint_a": {
                    "component_id": "carbon-dioxide",
                    "site_id": co2_site,
                },
                "endpoint_b": {"component_id": "water", "site_id": water_site},
                "energy_over_k": {
                    "identity": f"{prefix}/energy_over_k",
                    "value": {"magnitude": 1212.85, "unit": "kelvin"},
                },
                "volume": {
                    "identity": f"{prefix}/volume",
                    "value": {"magnitude": 0.04509, "unit": "dimensionless"},
                },
                "source": {
                    "kind": "explicit",
                    "provenance": [dict(induced_provenance)],
                },
            }
        )

    correlations_raw = tomllib.loads(
        (PARAMETER_ROOT / "correlations.toml").read_text()
    )["correlations"]
    correlations: list[dict[str, object]] = []
    for row in correlations_raw:
        correlation_id = (
            f"component/{row['component_id']}/{row['family']}/"
            "constant-plus-sum-of-exponentials"
        )
        correlations.append(
            {
                "correlation_id": correlation_id,
                "component_id": row["component_id"],
                "family": row["family"],
                "form": row["form"],
                "independent_variables": ["temperature"],
                "constant": {
                    "identity": f"{correlation_id}/constant",
                    "value": {
                        "magnitude": float(row["constant"]),
                        "unit": row["output_unit"],
                    },
                },
                "terms": [
                    {
                        "amplitude": {
                            "identity": f"{correlation_id}/term-{index}/amplitude",
                            "value": {
                                "magnitude": float(term["amplitude"]),
                                "unit": row["output_unit"],
                            },
                        },
                        "exponent_coefficient": {
                            "identity": (
                                f"{correlation_id}/term-{index}/exponent_coefficient"
                            ),
                            "value": {
                                "magnitude": float(term["exponent_coefficient"]),
                                "unit": "1 / kelvin",
                            },
                        },
                    }
                    for index, term in enumerate(row["coefficients"])
                ],
                "provenance": {
                    "source_id": row["source_id"],
                    "locator": row["locator"],
                    "domain_id": row["domain_id"],
                },
            }
        )

    model_coefficients = []
    for row in model_rows:
        if row["family"] == "relative_permittivity_formulation":
            continue
        if (
            permittivity != "ion-fraction-suppression"
            and row["family"] == "ion_fraction_suppression_coefficient"
        ):
            continue
        model_coefficients.append(
            {
                "identity": f"model/relative_permittivity/{row['family']}",
                "family": row["family"],
                "value": _value(row),
                "provenance": _provenance(row),
            }
        )

    domain = bundle["domains"][0]
    return {
        "schema": "epcsaft.parameters",
        "schema_version": 1,
        "document_id": "mea-nine-species-retained-diagnostic-v1",
        "document_version": 1,
        "purpose": "user-provided",
        "sources": [
            *bundle["sources"],
            {
                "source_id": induced_provenance["source_id"],
                "citation": "Schick et al. (2023) using Pabsch et al. (2020)",
                "use_basis": (
                    "CO2 2B sites and reciprocal CO2-water cross-association "
                    "with the source combining rule"
                ),
            },
            *(
                [
                    {
                        "source_id": "zuber-et-al-2014",
                        "citation": (
                            "Zuber et al. (2014), Fluid Phase Equilibria 376, "
                            "116-123, doi:10.1016/j.fluid.2014.05.037"
                        ),
                        "use_basis": (
                            "Ion-specific aqueous dielectric-suppression "
                            "coefficients and charge-class fallback values"
                        ),
                    }
                ]
                if permittivity == "ion-specific-suppression"
                else []
            ),
        ],
        "domains": [
            {
                "domain_id": domain["domain_id"],
                "kind": domain["kind"],
                "temperature_min": {
                    "magnitude": domain["temperature_min"],
                    "unit": domain["temperature_unit"],
                },
                "temperature_max": {
                    "magnitude": domain["temperature_max"],
                    "unit": domain["temperature_unit"],
                },
                "pressure_min": {
                    "magnitude": domain["pressure_min"],
                    "unit": domain["pressure_unit"],
                },
                "pressure_max": {
                    "magnitude": domain["pressure_max"],
                    "unit": domain["pressure_unit"],
                },
            }
        ],
        "components": components,
        "pairs": pairs,
        "model_families": _model_families(permittivity),
        "model_coefficients": model_coefficients,
        "correlations": correlations,
        "topology": {
            "presets": [],
            "sites": [
                {
                    "component_id": row["component_id"],
                    "site_id": row["site_id"],
                    "site_role": "donor" if row["site_class"] == "a" else "acceptor",
                    "multiplicity": int(row["multiplicity"]),
                    "provenance": _provenance(row),
                }
                for row in site_rows
            ],
            "edges": edges,
        },
    }


def load_parameters(
    *,
    permittivity: Literal[
        "solvent-only",
        "ion-fraction-suppression",
        "component-permittivity-mixing",
        "ion-specific-suppression",
    ] = "ion-fraction-suppression",
    ion_specific_suppression: Mapping[str, float] | None = None,
) -> epcsaft.Parameters:
    return epcsaft.Parameters.from_mapping(
        parameter_mapping(
            permittivity=permittivity,
            ion_specific_suppression=ion_specific_suppression,
        ),
        components=COMPONENT_IDS,
    )


__all__ = (
    "COMPONENT_IDS",
    "PARAMETER_ROOT",
    "expand_parameter_domain",
    "load_parameters",
    "materialize_parameter_candidate",
    "parameter_mapping",
    "set_parameter_values",
)
