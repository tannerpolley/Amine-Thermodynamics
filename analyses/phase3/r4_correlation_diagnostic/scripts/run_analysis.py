from __future__ import annotations

import argparse
from collections import Counter
import csv
from concurrent.futures import ProcessPoolExecutor
from dataclasses import dataclass
from importlib import metadata
import hashlib
import json
import math
from pathlib import Path
import shutil
import tempfile
from typing import Any
from urllib.parse import unquote, urlparse

import numpy as np
from MEA.common.analysis_io import write_json_file
from MEA.common.config import REPO_ROOT
from MEA.common.mea_source_contracts import (
    load_reaction_contract,
    load_sentinel_contract,
    validate_reaction_contract,
    validate_sentinel_contract,
)


ANALYSIS = REPO_ROOT / "analyses/phase3/r4_correlation_diagnostic"
RESULTS = ANALYSIS / "results"
FIGURE_OUTPUT = ANALYSIS / "figures/r4_diagnostic/output"
SOURCE_REFERENCE = ANALYSIS / "source_reference_transfer_contract.json"
ANALYSIS_PARTITION = ANALYSIS / "data/input/r4_training_partition.json"
VLE = (
    REPO_ROOT
    / "data/reference/MEA/observations/vapor_liquid_equilibrium"
    / "Canonical_VLE_Observations.csv"
)
SPECIATION = (
    REPO_ROOT
    / "data/reference/MEA/observations/liquid_speciation"
    / "Canonical_Combined_ChEq.csv"
)
METROLOGY = REPO_ROOT / "data/reference/MEA/manifests/pco2_metrology_manifest.csv"
CANONICAL_SPLIT = REPO_ROOT / "data/reference/MEA/manifests/grouped_split_manifest.csv"
REACTION_CONTRACT = (
    REPO_ROOT / "data/reference/MEA/manifests/chemical_reaction_source_contract.json"
)
SENTINEL_CONTRACT = (
    REPO_ROOT
    / "data/reference/MEA/manifests/homogeneous_speciation_sentinel_contract.json"
)
BASE_BUNDLE = (
    REPO_ROOT
    / "data/reference/epcsaft_bundles"
    / "mea-co2-h2o-nine-species-regression-input/1"
)

GROSS_CO2 = {
    "segment_count": 1.5131,
    "segment_diameter": 3.1869,
    "dispersion_energy_over_k": 163.33,
    "quadrupole_moment": 4.4,
}
NEUTRAL_DIPOLES = {"water": 1.8546, "monoethanolamine": 2.27}

REFERENCE_TEMPERATURE_K = 313.15
R4_LN_K_BOUNDS = (-20.0, 10.0)
MOLAR_MASS_ROUNDING_TOLERANCE_KG_PER_MOL = 5.0e-6
SOURCE_REFERENCE_CONVERGENCE_TOLERANCE = 5.0e-5
EOS_DIRECTIONAL_STEP = 1.0e-5
EOS_DIRECTIONAL_ABS_TOLERANCE = 2.0e-6
EOS_DIRECTIONAL_REL_TOLERANCE = 5.0e-3
REACTION_IDS = ("R1", "R2", "R3", "R4", "R5")
EOS_PARAMETER_SPECS = (
    {
        "name": "MEAH+::sigma",
        "family": "segment_diameter",
        "component_id": "protonated-monoethanolamine",
        "value": 3.48508556586,
        "unit": "angstrom",
        "affine_scale": 1.9,
    },
    {
        "name": "MEAH+::epsilon_over_k",
        "family": "dispersion_energy_over_k",
        "component_id": "protonated-monoethanolamine",
        "value": 232.687201645,
        "unit": "kelvin",
        "affine_scale": 450.0,
    },
    {
        "name": "MEACOO-::sigma",
        "family": "segment_diameter",
        "component_id": "carbamate-anion",
        "value": 3.53543525721,
        "unit": "angstrom",
        "affine_scale": 1.9,
    },
)
EXPECTED_DISTRIBUTIONS = {
    "epcsaft": {
        "version": "0.2.0.dev0",
        "record_sha256": "99986b14dfc31d96ee241308a30e3e05979f73e7ee8c17bcc97106f14858a78d",
        "wheel_sha256": "1622162b929cb8cd1a10d7c582a6b913babb8580a9f2188ee4fdf324d92f2772",
    },
    "epcsaft-equilibrium": {
        "version": "0.2.0.dev0",
        "record_sha256": "2718d1395ec219e4fd9b69d88255f5997a7451b827ffb5214fefabf71a3bf07b",
        "wheel_sha256": "397f0745fc692d33ea3a2d855a33346c516038bfd221798bc05f8ca02fde9b77",
    },
}


@dataclass(frozen=True)
class FitRow:
    observation_id: str
    source_key: str
    mea_mass_fraction: float
    temperature_k: float
    loading: float
    pressure_pa: float
    observed_pco2_pa: float
    split: str
    role: str
    group_id: str
    measurement_origin: str
    source_locator: str
    carbamate_target: float | None
    carbamate_lower_row: str
    carbamate_upper_row: str


@dataclass(frozen=True)
class EvaluationTask:
    bundle: str
    row: FitRow
    r4_coefficients: tuple[float, float, float, float]
    cached_offsets: tuple[float, ...] | None
    with_sensitivity: bool


def _rows(path: Path) -> list[dict[str, str]]:
    with path.open(newline="", encoding="utf-8") as handle:
        return list(csv.DictReader(handle))


def _write_csv(path: Path, rows: list[dict[str, object]]) -> None:
    if not rows:
        raise ValueError(f"refusing to write an empty result table: {path.name}")
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=tuple(rows[0]), lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)


def _append_csv(path: Path, additions: list[dict[str, object]]) -> None:
    existing = _rows(path)
    _write_csv(path, [*existing, *additions])


def _append_source(
    manifest: Path,
    source_id: str,
    citation: str,
    use_basis: str,
    doi: str | None = None,
) -> None:
    manifest.write_text(
        manifest.read_text(encoding="utf-8")
        + "\n[[sources]]\n"
        + f'source_id = "{source_id}"\n'
        + f'citation = "{citation}"\n'
        + ("" if doi is None else f'doi = "{doi}"\n')
        + f'use_basis = "{use_basis}"\n',
        encoding="utf-8",
    )


def _prepare_m5_bundle(destination: Path) -> None:
    """Build the full-polar diagnostic bundle from the frozen base records."""

    shutil.copytree(BASE_BUNDLE, destination)
    manifest = destination / "bundle.toml"
    manifest.write_text(
        manifest.read_text(encoding="utf-8").replace(
            'bundle_id = "mea-co2-h2o-nine-species-regression-input"',
            'bundle_id = "mea-model-comparison-m2"',
        ),
        encoding="utf-8",
    )
    for source in (
        (
            "mea-model-comparison",
            "MEA-Thermodynamics controlled M0--M3 experiment",
            "Nonpromoting parameter override for a bounded model comparison.",
            None,
        ),
        (
            "pabsch-2020-induced-association",
            "Pabsch, Held, and Sadowski (2020), Ind. Eng. Chem. Res. 59, 16790--16801",
            "Fixed CO2--water induced-association topology and pure association inputs.",
            "10.1021/acs.iecr.0c01888",
        ),
        (
            "gross-vrabec-polar-equations",
            "Gross (2005), AIChE J. 51, 2556; Gross and Vrabec (2006), AIChE J. 52, 1194; Vrabec and Gross (2009), J. Phys. Chem. B 113, 10935",
            "Fixed Gross--Vrabec DD/QQ/DQ35 equations implemented by the recorded Provider commit.",
            None,
        ),
        (
            "gross-2005-co2-qq",
            "Gross (2005), doi:10.1002/aic.10502, Table A1 first CO2 row",
            "CO2 pure parameters fitted with QQ active and measured Q=4.4 D angstrom.",
            None,
        ),
        (
            "neutral-dipole-diagnostic",
            "Clough et al. (1973), J. Chem. Phys. 59, 2254; Tripathi (2016), doi:10.5821/dissertation-2117-106297, chapter 7",
            "Fixed physical gas-phase moments; no moment or H2O/MEA PC-SAFT parameter was fitted here.",
            None,
        ),
    ):
        _append_source(manifest, *source)

    common = {
        "source_id": "pabsch-2020-induced-association",
        "domain_id": "mea-tracer-313-15-k-fit-range",
    }
    _append_csv(
        destination / "sites.csv",
        [
            {
                "record_id": f"carbon-dioxide-site-{site}",
                "component_id": "carbon-dioxide",
                "site_id": site,
                "site_class": site,
                "multiplicity": 1,
                "locator": "Pabsch2020 Table 2: CO2 association scheme N=1/1",
                **common,
            }
            for site in ("a", "b")
        ],
    )
    cross_energy = 0.5 * 2425.7
    cross_kappa = (
        math.sqrt(0.04509 * 0.0450)
        * (math.sqrt(2.7927 * 2.7852) / (0.5 * (2.7927 + 2.7852))) ** 3
    )
    association_rows = []
    for co2_site, water_site in (("a", "b"), ("b", "a")):
        prefix = f"carbon-dioxide-{co2_site}-water-{water_site}"
        endpoints = {
            "component_id_a": "carbon-dioxide",
            "site_id_a": co2_site,
            "component_id_b": "water",
            "site_id_b": water_site,
            **common,
        }
        association_rows.extend(
            (
                {
                    "record_id": f"{prefix}-association-energy-over-k",
                    "family": "association_energy_over_k",
                    "value": format(cross_energy, ".15g"),
                    "unit": "kelvin",
                    "locator": (
                        "Pabsch2020 Table 2 and Eq. 16: induced CO2--water "
                        "association; arithmetic-mean cross energy"
                    ),
                    **endpoints,
                },
                {
                    "record_id": f"{prefix}-association-volume",
                    "family": "association_volume",
                    "value": format(cross_kappa, ".15g"),
                    "unit": "",
                    "locator": (
                        "Pabsch2020 Table 2 kappa values with the existing "
                        "Wolbach--Sandler cross-volume rule"
                    ),
                    **endpoints,
                },
            )
        )
    _append_csv(destination / "association.csv", association_rows)

    single_rows = _rows(destination / "single.csv")
    gross_families = set(GROSS_CO2) - {"quadrupole_moment"}
    found = set()
    for row in single_rows:
        family = row["family"]
        if row["component_id"] == "carbon-dioxide" and family in gross_families:
            row["value"] = format(GROSS_CO2[family], ".15g")
            row["source_id"] = "gross-2005-co2-qq"
            row["locator"] = "Gross (2005), Table A1, first carbon-dioxide row"
            found.add(family)
    if found != gross_families:
        raise ValueError(f"missing CO2 pure records: {gross_families - found}")
    association_rows = _rows(destination / "association.csv")
    cross_kappa = (
        math.sqrt(0.04509 * 0.0450)
        * (
            math.sqrt(2.7927 * GROSS_CO2["segment_diameter"])
            / (0.5 * (2.7927 + GROSS_CO2["segment_diameter"]))
        )
        ** 3
    )
    for row in association_rows:
        if (
            row["source_id"] == "pabsch-2020-induced-association"
            and row["family"] == "association_volume"
        ):
            row["value"] = format(cross_kappa, ".15g")
            row["locator"] += "; recomputed with Gross (2005) CO2 segment diameter"
    _write_csv(destination / "association.csv", association_rows)
    polar_rows: list[dict[str, object]] = [
        {
            "record_id": "carbon-dioxide-quadrupole-moment",
            "component_id": "carbon-dioxide",
            "family": "quadrupole_moment",
            "value": GROSS_CO2["quadrupole_moment"],
            "unit": "debye * angstrom",
            "source_id": "gross-2005-co2-qq",
            "locator": "Table A1, first carbon-dioxide row",
            "domain_id": common["domain_id"],
        }
    ]
    polar_rows.extend(
        {
            "record_id": f"{component_id}-dipole-moment",
            "component_id": component_id,
            "family": "dipole_moment",
            "value": value,
            "unit": "debye",
            "source_id": "neutral-dipole-diagnostic",
            "locator": (
                "Clough et al. (1973): rotationless H2O moment"
                if component_id == "water"
                else "stable gas-phase MEA conformer; single-conformer diagnostic"
            ),
            "domain_id": common["domain_id"],
        }
        for component_id, value in NEUTRAL_DIPOLES.items()
    )
    _write_csv(destination / "single.csv", [*single_rows, *polar_rows])
    _append_csv(
        destination / "model.csv",
        [
            {
                "record_id": "gross-vrabec-point-multipole",
                "family": "polar_formulation",
                "value": "gross-vrabec-point-multipole",
                "unit": "",
                "source_id": "gross-vrabec-polar-equations",
                "locator": "Gross (2005); Gross and Vrabec (2006); Vrabec and Gross (2009)",
                "domain_id": common["domain_id"],
            }
        ],
    )


def _sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def _tree_hashes(root: Path) -> dict[str, str]:
    return {
        str(path.relative_to(root)): _sha256(path)
        for path in sorted(root.rglob("*"))
        if path.is_file()
    }


def _validated_reaction_contract() -> dict[str, Any]:
    contract = load_reaction_contract()
    validate_reaction_contract(contract)
    return contract


def _literature_r4_coefficients() -> tuple[float, float, float, float]:
    reaction = _validated_reaction_contract()["reactions"][3]
    if reaction["reaction_id"] != "R4":
        raise ValueError("canonical fourth reaction is not R4")
    correlation = reaction["correlation"]
    if correlation["kind"] != "ln_a_plus_b_over_t":
        raise ValueError("R4 correlation form drifted")
    return (
        float(correlation["a"]),
        float(correlation["b_k"]),
        0.0,
        0.0,
    )


def _distribution_identity(name: str) -> dict[str, str]:
    distribution = metadata.distribution(name)
    record = distribution.read_text("RECORD")
    direct_url = distribution.read_text("direct_url.json")
    if record is None:
        raise ValueError(f"installed {name} distribution has no RECORD")
    identity = {
        "name": name,
        "version": distribution.version,
        "record_sha256": hashlib.sha256(record.encode()).hexdigest(),
    }
    if direct_url is None:
        raise ValueError(f"installed {name} distribution has no direct_url.json")
    wheel_url = json.loads(direct_url).get("url", "")
    parsed_url = urlparse(wheel_url)
    if parsed_url.scheme != "file":
        raise ValueError(f"installed {name} does not identify a local wheel")
    wheel_path = Path(unquote(parsed_url.path))
    if not wheel_path.is_file():
        raise ValueError(f"installed {name} wheel is unavailable: {wheel_path}")
    identity["wheel_sha256"] = _sha256(wheel_path)
    return identity


def _require_candidate_environment() -> dict[str, dict[str, str]]:
    identities = {}
    for name, expected in EXPECTED_DISTRIBUTIONS.items():
        try:
            identity = _distribution_identity(name)
        except (metadata.PackageNotFoundError, ValueError) as error:
            raise RuntimeError(
                "full R4 reproduction requires the exact external candidate-wheel "
                f"environment; missing distribution: {name}"
            ) from error
        if any(identity[key] != value for key, value in expected.items()):
            raise RuntimeError(
                f"installed {name} identity differs from the retained receipt"
            )
        identities[name] = identity
    return identities


def _interpolated_carbamate_target(
    temperature_k: float, loading: float, mea_mass_fraction: float
) -> tuple[float | None, str, str]:
    if not math.isclose(mea_mass_fraction, 0.30):
        return None, "", ""
    candidates = []
    for row in _rows(SPECIATION):
        if (
            row["source_key"] == "Bottinger2008"
            and row["species"] == "MEACOO-"
            and row["measurement_role"] == "direct_positive"
            and row["target_membership"] == "active_v1"
            and math.isclose(float(row["mea_mass_fraction"]), 0.30)
            and math.isclose(float(row["temperature_K"]), temperature_k)
        ):
            candidates.append(
                (
                    float(row["co2_loading_mol_per_mol_mea"]),
                    float(row["value_mole_fraction"]),
                    row["record_id"],
                )
            )
    candidates.sort()
    if len(candidates) < 2 or not candidates[0][0] <= loading <= candidates[-1][0]:
        return None, "", ""
    for lower, upper in zip(candidates, candidates[1:], strict=False):
        if lower[0] <= loading <= upper[0]:
            if math.isclose(lower[0], upper[0]):
                value = lower[1]
            else:
                fraction = (loading - lower[0]) / (upper[0] - lower[0])
                value = lower[1] + fraction * (upper[1] - lower[1])
            return value, lower[2], upper[2]
    raise AssertionError("measured carbamate interpolation bracket was not found")


def _fit_rows() -> tuple[FitRow, ...]:
    canonical = {row["observation_id"]: row for row in _rows(VLE)}
    metrology = {row["observation_id"]: row for row in _rows(METROLOGY)}
    canonical_split = {
        row["record_id"]: row
        for row in _rows(CANONICAL_SPLIT)
        if row["target_family"] == "vle_pressure"
    }
    partition = json.loads(ANALYSIS_PARTITION.read_text(encoding="utf-8"))
    training_groups = set(partition["training_group_ids"])
    result = []
    for observation_id, row in sorted(canonical.items()):
        metrology_role = metrology[observation_id]
        if metrology_role["target_eligible"] != "yes":
            continue
        source_partition = (
            canonical_split.get(row["active_row_id"]) or canonical_split[observation_id]
        )
        group_id = source_partition["group_id"]
        role = (
            "active_training" if group_id in training_groups else "reserved_validation"
        )
        temperature_k = 273.15 + float(
            row["temperature_canonical_C"] or row["temperature_reported_C"]
        )
        loading = float(row["CO2_loading"])
        mea_mass_fraction = float(row["MEA_weight_fraction"])
        pressure_pa = float(metrology_role["state_pressure_pa"])
        observed_pco2_pa = 1000.0 * float(row["CO2_pressure"])
        if (
            metrology_role["measurement_origin"]
            not in {
                "calibration_derived_partial_pressure",
                "total_pressure_derived",
            }
            or metrology_role["pressure_specification"] != "row_reported_total_pressure"
            or not math.isclose(pressure_pa, 1000.0 * float(row["total_pressure"]))
            or not math.isclose(
                observed_pco2_pa,
                1000.0 * float(metrology_role["observed_pco2_kpa"]),
            )
        ):
            raise ValueError(f"pressure-row source contract drift: {observation_id}")
        carbamate, lower, upper = _interpolated_carbamate_target(
            temperature_k, loading, mea_mass_fraction
        )
        result.append(
            FitRow(
                observation_id=observation_id,
                source_key=row["source_key"],
                mea_mass_fraction=mea_mass_fraction,
                temperature_k=temperature_k,
                loading=loading,
                pressure_pa=pressure_pa,
                observed_pco2_pa=observed_pco2_pa,
                split="training" if role == "active_training" else "validation",
                role=role,
                group_id=group_id,
                measurement_origin=metrology_role["measurement_origin"],
                source_locator=metrology_role["source_locator"],
                carbamate_target=carbamate,
                carbamate_lower_row=lower,
                carbamate_upper_row=upper,
            )
        )
    role_counts = Counter(row.role for row in result)
    if role_counts != partition["expected_role_counts"]:
        raise ValueError(f"R4 multisource partition drift: {dict(role_counts)}")
    if {row.source_key for row in result if row.role == "active_training"} != {
        "Hilliard2008",
        "Jou1995",
    }:
        raise ValueError("R4 training-source contract drift")
    return tuple(result)


def _prepare_fit_bundle(destination: Path) -> None:
    _prepare_m5_bundle(destination)
    manifest = destination / "bundle.toml"
    text = manifest.read_text(encoding="utf-8")
    text = text.replace("temperature_max = 313.15", "temperature_max = 393.15")
    text = text.replace("pressure_max = 300000", "pressure_max = 3000000")
    text = text.replace(
        'bundle_id = "mea-model-comparison-m2"',
        'bundle_id = "mea-m5-r4-multisource-fit"',
    )
    text += (
        "\n[[sources]]\n"
        'source_id = "mea-r4-multisource-fit"\n'
        'citation = "MEA-Thermodynamics multisource R4 pressure fit"\n'
        'use_basis = "Source-row T/P fit range 313.15--393.15 K and 6105.45--3000000 Pa; regression-input authority only."\n'
    )
    manifest.write_text(text, encoding="utf-8")


def _evaluate_correlation(reaction: dict[str, Any], temperature_k: float) -> float:
    correlation = reaction["correlation"]
    kind = correlation["kind"]
    if kind == "ln_a_plus_b_over_t_plus_c_ln_t_plus_d_t":
        return (
            float(correlation["a"])
            + float(correlation["b_k"]) / temperature_k
            + float(correlation["c"]) * math.log(temperature_k)
            + float(correlation["d_per_k"]) * temperature_k
        )
    if kind == "ln_from_negative_log10_a_over_t_plus_b_plus_c_t":
        return -math.log(10.0) * (
            float(correlation["a_k"]) / temperature_k
            + float(correlation["b"])
            + float(correlation["c_per_k"]) * temperature_k
        )
    if kind == "ln_a_plus_b_over_t":
        return float(correlation["a"]) + float(correlation["b_k"]) / temperature_k
    raise ValueError(f"unsupported reaction-correlation kind: {kind}")


def _r4_ln_k(
    temperature_k: float, coefficients: tuple[float, float, float, float]
) -> float:
    a, b_k, c, d_per_k = coefficients
    return (
        a + b_k / temperature_k + c * math.log(temperature_k) + d_per_k * temperature_k
    )


def _source_ln_k(
    temperature_k: float, r4_coefficients: tuple[float, float, float, float]
) -> tuple[float, ...]:
    contract = _validated_reaction_contract()
    offsets = contract["common_source_standard_state"]["source_to_common_ln_k_offsets"]
    result = []
    for index, (reaction, offset) in enumerate(
        zip(contract["reactions"], offsets, strict=True)
    ):
        value = (
            _r4_ln_k(temperature_k, r4_coefficients)
            if index == 3
            else _evaluate_correlation(reaction, temperature_k) + float(offset)
        )
        result.append(value)
    return tuple(result)


def _reaction_inputs(
    bundle: Path, loading: float, mea_mass_fraction: float
) -> tuple[
    tuple[str, ...],
    tuple[int, ...],
    tuple[tuple[float, ...], ...],
    tuple[tuple[float, ...], ...],
    tuple[float, ...],
    tuple[float, ...],
    tuple[float, ...],
]:
    contract = _validated_reaction_contract()
    sentinel = load_sentinel_contract()
    validate_sentinel_contract(sentinel, contract)
    component_ids = tuple(contract["provider_species_order"])
    charges = tuple(int(species["charge"]) for species in contract["species"])
    elements = tuple(contract["balance_row_order"])
    elemental = tuple(
        tuple(float(species["formula"][element]) for species in contract["species"])
        for element in elements
    )
    balances = (elemental[elements.index("C")], elemental[elements.index("N")])
    molar_mass = sentinel["molar_mass_basis"]["values"]
    water = (
        (1.0 - mea_mass_fraction)
        / mea_mass_fraction
        * float(molar_mass["MEA"])
        / float(molar_mass["H2O"])
    )
    feed = (loading, 1.0, water, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0)
    totals = tuple(
        math.fsum(balance[index] * feed[index] for index in range(len(feed)))
        for balance in balances
    )
    reactions = tuple(
        tuple(float(value) for value in reaction["stoichiometry"])
        for reaction in contract["reactions"]
    )
    masses = _reaction_consistent_molar_masses(bundle, component_ids, elemental)
    return component_ids, charges, balances, reactions, feed, totals, masses


def _reaction_consistent_molar_masses(
    bundle: Path,
    component_ids: tuple[str, ...],
    balance_matrix: tuple[tuple[float, ...], ...],
) -> tuple[float, ...]:
    reported = {
        row["component_id"]: float(row["value"])
        for row in _rows(bundle / "single.csv")
        if row["family"] == "molar_mass"
    }
    if set(reported) != set(component_ids):
        raise ValueError("bundle does not contain one molar mass per component")
    balances = np.asarray(balance_matrix, dtype=float)
    values = np.asarray([reported[component] for component in component_ids])
    elemental_masses, *_ = np.linalg.lstsq(balances.T, values, rcond=None)
    projected = balances.T @ elemental_masses
    rounding_residual = float(np.max(np.abs(projected - values)))
    if rounding_residual > MOLAR_MASS_ROUNDING_TOLERANCE_KG_PER_MOL:
        raise ValueError(
            "bundle molar masses exceed the admitted source-rounding tolerance: "
            f"{rounding_residual:.6e} kg/mol"
        )
    return tuple(float(value) for value in projected)


def _public_transfer_offsets(
    model: Any, temperature_k: float, pressure_pa: float
) -> tuple[tuple[float, ...], dict[str, object]]:
    import epcsaft

    contract = _validated_reaction_contract()
    source_reference = json.loads(SOURCE_REFERENCE.read_text(encoding="utf-8"))[
        "source_reference"
    ]
    component_ids = tuple(contract["provider_species_order"])
    declaration = epcsaft.SourceReferenceDeclaration(
        reference_state_id="aqueous-molality-infinite-dilution-water-v1",
        component_ids=component_ids,
        solvent_mole_fractions=tuple(source_reference["mole_fractions"]),
        activity_convention_id=source_reference["activity_convention_id"],
        standard_molality_mol_per_kg=float(
            source_reference["solute_standard_molality_mol_per_kg"]
        ),
        reference_pressure_pa=float(source_reference["source_reference_pressure_pa"]),
        required_derivatives=(),
    )
    transfer = epcsaft.source_reference_transfer(
        model,
        declaration,
        T=temperature_k * epcsaft.unit_registry.kelvin,
        P=pressure_pa * epcsaft.unit_registry.pascal,
    )
    temperature_interval = tuple(
        float(value) for value in transfer.source_temperature_interval_k
    )
    pressure_interval = tuple(
        float(value) for value in transfer.source_pressure_interval_pa
    )
    convergence_error = float(transfer.reference_convergence_error)
    if not temperature_interval[0] <= temperature_k <= temperature_interval[1]:
        raise ValueError(
            "source-reference transfer temperature is outside its receipt domain"
        )
    if not pressure_interval[0] <= pressure_pa <= pressure_interval[1]:
        raise ValueError(
            "source-reference transfer pressure is outside its receipt domain"
        )
    if (
        not math.isfinite(convergence_error)
        or convergence_error > SOURCE_REFERENCE_CONVERGENCE_TOLERANCE
    ):
        raise ValueError(
            "source-reference transfer did not meet the frozen convergence tolerance"
        )
    reactions = np.asarray(
        [reaction["stoichiometry"] for reaction in contract["reactions"]], dtype=float
    )
    basis = np.asarray(transfer.neutral_basis, dtype=float)
    coordinates = np.linalg.lstsq(basis.T, reactions.T, rcond=None)[0].T
    reconstruction = float(np.max(np.abs(coordinates @ basis - reactions)))
    if reconstruction > 2.0e-12:
        raise ValueError("source reactions are outside the installed neutral basis")
    offsets = coordinates @ np.asarray(transfer.transfer_log_contractions, dtype=float)
    return tuple(float(value) for value in offsets), {
        "artifact_fingerprint": transfer.artifact_fingerprint,
        "reference_state_fingerprint": transfer.reference_state_fingerprint,
        "domain_fingerprint": transfer.domain_fingerprint,
        "temperature_interval_k": list(temperature_interval),
        "pressure_interval_pa": list(pressure_interval),
        "reference_convergence_error": convergence_error,
        "basis_reconstruction_inf_norm": reconstruction,
    }


def _pco2(
    model: Any, temperature_k: float, amounts: np.ndarray, volume_m3: float
) -> float:
    import epcsaft

    total = float(np.sum(amounts))
    state = model.state(
        T=temperature_k * epcsaft.unit_registry.kelvin,
        rho=(total / volume_m3)
        * epcsaft.unit_registry.mole
        / epcsaft.unit_registry.meter**3,
        x=tuple(float(value) for value in amounts / total),
    )
    if state.fugacity is None:
        raise ValueError("Provider did not return liquid fugacity")
    return float(state.fugacity.value[0].to("pascal").magnitude)


def _evaluate_state(task: EvaluationTask) -> dict[str, object]:
    row = task.row
    import epcsaft
    import epcsaft_equilibrium

    bundle = Path(task.bundle)
    component_ids, charges, balances, reactions, feed, totals, masses = (
        _reaction_inputs(bundle, row.loading, row.mea_mass_fraction)
    )
    model = epcsaft.Mixture(
        epcsaft.Parameters.from_bundle(bundle, components=component_ids)
    )
    if task.cached_offsets is None:
        offsets, transfer_receipt = _public_transfer_offsets(
            model, row.temperature_k, row.pressure_pa
        )
    else:
        offsets = task.cached_offsets
        transfer_receipt = {}
    source_ln_k = _source_ln_k(row.temperature_k, task.r4_coefficients)
    provider_ln_k = tuple(
        source + offset for source, offset in zip(source_ln_k, offsets, strict=True)
    )
    problem = epcsaft_equilibrium.ChemicalEquilibriumProblem(
        species_ids=component_ids,
        charges=charges,
        molar_masses_kg_per_mol=masses,
        balance_matrix=balances,
        conserved_totals=totals,
        reaction_matrix=reactions,
        feed_amounts_mol=feed,
        equilibrium_constants=tuple(
            epcsaft_equilibrium.ChemicalEquilibriumConstant(
                ln_value=value,
                source_id="MEA-R4-temperature-screen",
                reference_id="provider-helmholtz-coordinate-basis",
                reaction_orientation="products_positive",
                conversion_id="already-provider-basis",
                dimensionless=True,
            )
            for value in provider_ln_k
        ),
        strict_interior_amount_floor_mol=1.0e-18,
        source_standard_state=None,
    )
    phase = epcsaft_equilibrium.ProviderPhase(
        model=model,
        expected_parameter_fingerprint=model.parameter_fingerprint,
        admissible_packing_fraction_interval=(1.0e-6, 0.74),
    )
    request = (
        epcsaft_equilibrium.ChemicalEquilibriumSensitivityRequest()
        if task.with_sensitivity
        else None
    )
    solved = epcsaft_equilibrium.chemical_equilibrium(
        phase,
        row.temperature_k * epcsaft.unit_registry.kelvin,
        row.pressure_pa * epcsaft.unit_registry.pascal,
        problem,
        sensitivity_request=request,
    )
    amounts = np.asarray(solved.amounts_mol, dtype=float)
    prediction = _pco2(model, row.temperature_k, amounts, solved.volume_m3)
    mole_fractions = amounts / float(np.sum(amounts))
    reaction_derivatives: dict[str, float | None] = {
        reaction_id: None for reaction_id in REACTION_IDS
    }
    carbamate_derivatives: dict[str, float | None] = {
        reaction_id: None for reaction_id in REACTION_IDS
    }
    derivative_consistency = None
    if task.with_sensitivity:
        sensitivity = solved.sensitivity
        if sensitivity is None or sensitivity.status != "available":
            raise ValueError("exact reaction-state sensitivity is unavailable")
        consistencies = []
        total_amount = float(np.sum(amounts))
        for reaction_index, reaction_id in enumerate(REACTION_IDS):
            column = next(
                index
                for index, parameter in enumerate(sensitivity.parameters)
                if parameter.kind == "provider_basis_ln_k"
                and parameter.source_index == reaction_index
            )
            amount_direction = np.asarray(
                sensitivity.amount_derivatives[column], dtype=float
            )
            volume_direction = float(sensitivity.volume_derivatives[column])
            estimates = []
            for step in (EOS_DIRECTIONAL_STEP, 0.5 * EOS_DIRECTIONAL_STEP):
                plus = _pco2(
                    model,
                    row.temperature_k,
                    amounts + step * amount_direction,
                    solved.volume_m3 + step * volume_direction,
                )
                minus = _pco2(
                    model,
                    row.temperature_k,
                    amounts - step * amount_direction,
                    solved.volume_m3 - step * volume_direction,
                )
                estimates.append((math.log10(plus) - math.log10(minus)) / (2.0 * step))
            reaction_derivatives[reaction_id] = estimates[1]
            difference = abs(estimates[0] - estimates[1])
            scale = max(abs(estimates[0]), abs(estimates[1]))
            consistency = difference / max(scale, EOS_DIRECTIONAL_ABS_TOLERANCE)
            consistencies.append(consistency)
            d_total = float(np.sum(amount_direction))
            d_carbamate = (
                amount_direction[4] / amounts[4] - d_total / total_amount
            ) / math.log(10.0)
            carbamate_derivatives[reaction_id] = float(d_carbamate)
        derivative_consistency = max(consistencies)
        if any(
            not math.isfinite(value)
            for value in (
                *reaction_derivatives.values(),
                *carbamate_derivatives.values(),
            )
        ) or any(
            consistency > EOS_DIRECTIONAL_REL_TOLERANCE for consistency in consistencies
        ):
            raise ValueError(
                "EOS directional derivative is not step-converged: "
                f"relative_difference={max(consistencies):.6e}, "
                f"pco2={reaction_derivatives}"
            )
    diagnostics = solved.diagnostics
    result = {
        "observation_id": row.observation_id,
        "temperature_k": row.temperature_k,
        "loading": row.loading,
        "pressure_pa": row.pressure_pa,
        "observed_pco2_pa": row.observed_pco2_pa,
        "predicted_pco2_pa": prediction,
        "log10_pressure_residual": math.log10(prediction / row.observed_pco2_pa),
        "carbamate_mole_fraction": float(mole_fractions[4]),
        "carbamate_target": row.carbamate_target,
        "log10_carbamate_residual": (
            None
            if row.carbamate_target is None
            else math.log10(float(mole_fractions[4]) / row.carbamate_target)
        ),
        "dlog10_pco2_dlnk4": reaction_derivatives["R4"],
        "directional_derivative_relative_difference": derivative_consistency,
        "source_ln_k": list(source_ln_k),
        "provider_ln_k": list(provider_ln_k),
        "transfer_offsets": list(offsets),
        "transfer_receipt": transfer_receipt,
        "model_fingerprint": model.parameter_fingerprint,
        "certification": diagnostics.chemical_certification_level,
        "numerical_status": diagnostics.numerical_status,
        "physical_status": diagnostics.physical_status,
        "local_minimum_status": diagnostics.local_minimum_status,
        "reaction_affinity_inf_norm": diagnostics.reaction_affinity_inf_norm,
        "kkt_stationarity_inf_norm": diagnostics.kkt_stationarity_inf_norm,
        "pressure_relative_residual": diagnostics.pressure_relative_residual,
        "packing_fraction": diagnostics.packing_fraction,
        "minimum_amount_mol": diagnostics.minimum_amount_mol,
        "search_status": diagnostics.search.status,
        "evaluated_start_count": diagnostics.search.evaluated_start_count,
    }
    for reaction_id in REACTION_IDS:
        result[f"dlog10_pco2_dlnk_{reaction_id}"] = reaction_derivatives[reaction_id]
        result[f"dlog10_meacoo_dlnk_{reaction_id}"] = carbamate_derivatives[reaction_id]
    return result


def _evaluate_state_safe(task: EvaluationTask) -> dict[str, object]:
    import epcsaft
    import epcsaft_equilibrium

    try:
        return _evaluate_state(task)
    except (epcsaft.EosError, epcsaft_equilibrium.ChemicalEquilibriumError) as error:
        diagnostics = getattr(error, "diagnostics", None)
        return {
            "observation_id": task.row.observation_id,
            "failure_type": type(error).__name__,
            "failure_reason": str(error),
            "failure_kind": (
                ""
                if diagnostics is None
                else str(getattr(diagnostics, "failure_kind", ""))
            ),
        }


def _evaluate_batch(
    bundle: Path,
    rows: tuple[FitRow, ...],
    r4_coefficients: tuple[float, float, float, float],
    offsets: dict[str, tuple[float, ...]],
    *,
    with_sensitivity: bool,
    workers: int,
    retain_state_failures: bool = False,
) -> list[dict[str, object]]:
    tasks = tuple(
        EvaluationTask(
            bundle=str(bundle),
            row=row,
            r4_coefficients=r4_coefficients,
            cached_offsets=offsets.get(row.observation_id),
            with_sensitivity=with_sensitivity,
        )
        for row in rows
    )
    with ProcessPoolExecutor(max_workers=workers) as executor:
        results = list(executor.map(_evaluate_state_safe, tasks))
    failures = [result for result in results if "failure_type" in result]
    if failures and not retain_state_failures:
        raise ValueError(
            "R4 state evaluation failures:\n"
            + "\n".join(json.dumps(failure, sort_keys=True) for failure in failures)
        )
    successful = [result for result in results if "failure_type" not in result]
    if any(result["certification"] != "LOCAL_EQUILIBRIUM" for result in successful):
        raise ValueError(
            "one or more R4 fit states lacks local-equilibrium certification"
        )
    return results


def _rmse(results: list[dict[str, object]]) -> float:
    residuals = np.asarray([result["log10_pressure_residual"] for result in results])
    return float(np.sqrt(np.mean(residuals**2)))


def _metric_rows(fit_rows: list[dict[str, object]]) -> list[dict[str, object]]:
    output = []
    for model_id in ("M5_literature_R4", "M5_fitted_R4"):
        model_rows = [row for row in fit_rows if row["model_id"] == model_id]
        groupings = [("overall", "all", model_rows)]
        for field in ("role", "source_key", "temperature_c"):
            for value in sorted({str(row[field]) for row in model_rows}):
                groupings.append(
                    (
                        field,
                        value,
                        [row for row in model_rows if str(row[field]) == value],
                    )
                )
        for grouping, value, rows in groupings:
            residuals = np.asarray(
                [float(row["log10_pressure_residual"]) for row in rows]
            )
            output.append(
                {
                    "model_id": model_id,
                    "grouping": grouping,
                    "group": value,
                    "row_count": len(rows),
                    "log10_rmse": float(np.sqrt(np.mean(residuals**2))),
                    "log10_mae": float(np.mean(np.abs(residuals))),
                    "log10_bias": float(np.mean(residuals)),
                }
            )
    return output


def _eos_parameter_sensitivities(
    bundle: Path,
    rows: tuple[FitRow, ...],
    r4_coefficients: tuple[float, float, float, float],
    offsets: dict[str, tuple[float, ...]],
) -> tuple[list[dict[str, object]], dict[str, object]]:
    import epcsaft
    import epcsaft_equilibrium

    component_ids = tuple(load_reaction_contract()["provider_species_order"])
    model = epcsaft.Mixture(
        epcsaft.Parameters.from_bundle(bundle, components=component_ids)
    )
    phase = epcsaft_equilibrium.ProviderPhase(
        model=model,
        expected_parameter_fingerprint=model.parameter_fingerprint,
        admissible_packing_fraction_interval=(1.0e-6, 0.74),
    )
    active_parameters = tuple(
        epcsaft_equilibrium.ChemicalEquilibriumActiveParameter(
            family=str(spec["family"]),
            identity="component",
            component_ids=(str(spec["component_id"]),),
            value=float(spec["value"]),
            unit=str(spec["unit"]),
        )
        for spec in EOS_PARAMETER_SPECS
    )
    observation_rows = []
    observation_metadata = []
    for row in rows:
        inputs = _reaction_inputs(bundle, row.loading, row.mea_mass_fraction)
        ids, charges, balances, reactions, feed, totals, masses = inputs
        source_ln_k = _source_ln_k(row.temperature_k, r4_coefficients)
        provider_ln_k = tuple(
            source + offset
            for source, offset in zip(
                source_ln_k, offsets[row.observation_id], strict=True
            )
        )
        problem = epcsaft_equilibrium.ChemicalEquilibriumProblem(
            species_ids=ids,
            charges=charges,
            molar_masses_kg_per_mol=masses,
            balance_matrix=balances,
            conserved_totals=totals,
            reaction_matrix=reactions,
            feed_amounts_mol=feed,
            equilibrium_constants=tuple(
                epcsaft_equilibrium.ChemicalEquilibriumConstant(
                    ln_value=value,
                    source_id="MEA-R4-multisource-fit",
                    reference_id="provider-helmholtz-coordinate-basis",
                    reaction_orientation="products_positive",
                    conversion_id="already-provider-basis",
                    dimensionless=True,
                )
                for value in provider_ln_k
            ),
            strict_interior_amount_floor_mol=1.0e-18,
            source_standard_state=None,
        )
        primitives = [
            (
                "pco2",
                epcsaft_equilibrium.ChemicalObservationPrimitive(
                    kind="neutral_component_fugacity_pa",
                    component_id="carbon-dioxide",
                ),
            )
        ]
        if row.carbamate_target is not None:
            primitives.append(
                (
                    "carbamate_mole_fraction",
                    epcsaft_equilibrium.ChemicalObservationPrimitive(
                        kind="species_mole_fraction",
                        component_id="carbamate-anion",
                    ),
                )
            )
        for observable, primitive in primitives:
            observation_rows.append(
                epcsaft_equilibrium.ChemicalObservationRow(
                    row_id=f"{row.observation_id}::{observable}",
                    state_id=row.observation_id,
                    state_schema_id="fixed_TP_homogeneous_liquid_v1",
                    source_id=row.source_key,
                    transform_id="natural_log",
                    temperature=row.temperature_k * epcsaft.unit_registry.kelvin,
                    pressure=row.pressure_pa * epcsaft.unit_registry.pascal,
                    problem=problem,
                    primitive=primitive,
                )
            )
            observation_metadata.append((row, observable))
    context = epcsaft_equilibrium.chemical_observation_context(
        phase,
        rows=tuple(observation_rows),
        active_parameters=active_parameters,
    )
    evaluated = context.evaluate(
        tuple(parameter.value for parameter in active_parameters),
        with_jacobian=True,
    )
    values = np.asarray(evaluated["values"], dtype=float)
    jacobian = np.asarray(evaluated["jacobian"], dtype=float).reshape(
        len(observation_rows), len(active_parameters)
    )
    if int(evaluated["status"]) != 0 or any(
        int(row["status"]) != 0 for row in evaluated["row_results"]
    ):
        raise ValueError("one or more exact EOS sensitivity rows failed")
    sensitivity_rows = []
    for row_index, ((row, observable), value) in enumerate(
        zip(observation_metadata, values, strict=True)
    ):
        for parameter_index, spec in enumerate(EOS_PARAMETER_SPECS):
            derivative = jacobian[row_index, parameter_index]
            sensitivity_rows.append(
                {
                    "observation_id": row.observation_id,
                    "source_key": row.source_key,
                    "role": row.role,
                    "temperature_c": row.temperature_k - 273.15,
                    "loading_mol_co2_per_mol_mea": row.loading,
                    "observable": observable,
                    "parameter": spec["name"],
                    "parameter_unit": spec["unit"],
                    "affine_scale": spec["affine_scale"],
                    "value": value,
                    "dlog10_observable_daffine_coordinate": float(
                        derivative
                        / value
                        * float(spec["affine_scale"])
                        / math.log(10.0)
                    ),
                }
            )
    receipt = {
        "context_identity": context.artifact_identity,
        "contract_fingerprint": context.contract_fingerprint,
        "capability_fingerprint": context.capability_fingerprint,
        "parameter_ids": list(context.parameter_ids),
        "parameter_units": list(context.parameter_units),
        "row_count": len(observation_rows),
        "state_count": len(rows),
        "failed_rows": 0,
    }
    return sensitivity_rows, receipt


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Fit the four-coefficient MEA R4 correlation to Hilliard and Jou pressure groups"
    )
    parser.add_argument("--workers", type=int, default=5)
    args = parser.parse_args()
    if not 1 <= args.workers <= 16:
        raise ValueError("workers must lie between one and sixteen")

    installed_artifacts = _require_candidate_environment()
    rows = _fit_rows()
    role_by_observation_id = {row.observation_id: row.role for row in rows}
    training_rows = tuple(row for row in rows if row.role == "active_training")
    literature_coefficients = _literature_r4_coefficients()
    iterations: list[dict[str, object]] = []
    offsets: dict[str, tuple[float, ...]] = {}
    transfer_receipts: dict[str, dict[str, object]] = {}

    with tempfile.TemporaryDirectory(prefix="mea-r4-fit-") as temporary:
        bundle = Path(temporary) / "m5-r4-fit"
        _prepare_fit_bundle(bundle)
        generated_bundle_files = _tree_hashes(bundle)
        initial_training_evaluations = _evaluate_batch(
            bundle,
            training_rows,
            literature_coefficients,
            offsets,
            with_sensitivity=True,
            workers=args.workers,
            retain_state_failures=True,
        )
        initial_training_failures = [
            result
            for result in initial_training_evaluations
            if "failure_type" in result
        ]
        initial_training_results = [
            result
            for result in initial_training_evaluations
            if "failure_type" not in result
        ]
        successful_training_ids = {
            str(result["observation_id"]) for result in initial_training_results
        }
        fit_training_rows = tuple(
            row
            for row in training_rows
            if row.observation_id in successful_training_ids
        )
        group_counts = Counter(row.group_id for row in fit_training_rows)
        group_weights = {
            row.observation_id: 1.0 / group_counts[row.group_id]
            for row in fit_training_rows
        }

        def weighted_rmse(results: list[dict[str, object]]) -> float:
            residuals = np.asarray(
                [float(result["log10_pressure_residual"]) for result in results]
            )
            weights = np.asarray(
                [group_weights[str(result["observation_id"])] for result in results]
            )
            return float(np.sqrt(np.sum(weights * residuals**2) / np.sum(weights)))

        for result in initial_training_results:
            observation_id = str(result["observation_id"])
            offsets[observation_id] = tuple(
                float(value) for value in result["transfer_offsets"]
            )
            receipt = result["transfer_receipt"]
            if receipt:
                transfer_receipts[observation_id] = dict(receipt)

        feature_matrix = np.asarray(
            [
                [
                    1.0,
                    1.0 / row.temperature_k,
                    math.log(row.temperature_k),
                    row.temperature_k,
                ]
                for row in fit_training_rows
            ]
        )
        direct = np.asarray(
            [float(result["dlog10_pco2_dlnk4"]) for result in initial_training_results]
        )
        residual = np.asarray(
            [
                float(result["log10_pressure_residual"])
                for result in initial_training_results
            ]
        )
        weights = np.sqrt(
            np.asarray(
                [
                    group_weights[str(result["observation_id"])]
                    for result in initial_training_results
                ]
            )
        )
        raw_jacobian = direct[:, None] * feature_matrix
        column_scales = np.linalg.norm(raw_jacobian * weights[:, None], axis=0)
        scaled_jacobian = raw_jacobian / column_scales * weights[:, None]
        scaled_residual = residual * weights
        scaled_step = np.linalg.lstsq(scaled_jacobian, -scaled_residual, rcond=None)[0]
        coefficient_step = scaled_step / column_scales
        candidate = tuple(
            float(value + delta)
            for value, delta in zip(
                literature_coefficients, coefficient_step, strict=True
            )
        )
        step_fraction = 1.0
        training_temperatures = sorted({row.temperature_k for row in fit_training_rows})
        while any(
            not R4_LN_K_BOUNDS[0]
            <= _r4_ln_k(temperature, candidate)
            <= R4_LN_K_BOUNDS[1]
            for temperature in training_temperatures
        ):
            step_fraction *= 0.5
            if step_fraction < 2.0**-20:
                raise ValueError(
                    "four-coefficient R4 step cannot satisfy the lnK safeguard"
                )
            candidate = tuple(
                float(value + step_fraction * delta)
                for value, delta in zip(
                    literature_coefficients, coefficient_step, strict=True
                )
            )
        singular = np.linalg.svd(scaled_jacobian, compute_uv=False)
        raw_singular = np.linalg.svd(raw_jacobian * weights[:, None], compute_uv=False)
        iterations.append(
            {
                "iteration": 0,
                "initial_a": literature_coefficients[0],
                "initial_b_k": literature_coefficients[1],
                "initial_c": literature_coefficients[2],
                "initial_d_per_k": literature_coefficients[3],
                "candidate_a": candidate[0],
                "candidate_b_k": candidate[1],
                "candidate_c": candidate[2],
                "candidate_d_per_k": candidate[3],
                "step_fraction": step_fraction,
                "log10_rmse": _rmse(initial_training_results),
                "group_normalized_log10_rmse": weighted_rmse(initial_training_results),
                "jacobian_rank": int(np.linalg.matrix_rank(scaled_jacobian)),
                "scaled_jacobian_condition_number": float(singular[0] / singular[-1]),
                "raw_jacobian_condition_number": float(
                    raw_singular[0] / raw_singular[-1]
                ),
            }
        )

        reserved_rows = tuple(row for row in rows if row.role == "reserved_validation")
        initial_reserved_results = _evaluate_batch(
            bundle,
            reserved_rows,
            literature_coefficients,
            offsets,
            with_sensitivity=False,
            workers=args.workers,
            retain_state_failures=True,
        )
        initial_reserved_failures = [
            result for result in initial_reserved_results if "failure_type" in result
        ]
        initial_reserved_results = [
            result
            for result in initial_reserved_results
            if "failure_type" not in result
        ]
        for result in initial_reserved_results:
            observation_id = str(result["observation_id"])
            offsets[observation_id] = tuple(
                float(value) for value in result["transfer_offsets"]
            )
            receipt = result["transfer_receipt"]
            if receipt:
                transfer_receipts[observation_id] = dict(receipt)
        initial_results = [*initial_training_results, *initial_reserved_results]

        candidate_results = _evaluate_batch(
            bundle,
            rows,
            candidate,
            offsets,
            with_sensitivity=False,
            workers=args.workers,
            retain_state_failures=True,
        )
        candidate_failures = [
            result for result in candidate_results if "failure_type" in result
        ]
        candidate_results = [
            result for result in candidate_results if "failure_type" not in result
        ]
        candidate_training_results = [
            result
            for result in candidate_results
            if role_by_observation_id[str(result["observation_id"])]
            == "active_training"
        ]
        candidate_training_ids = {
            str(result["observation_id"]) for result in candidate_training_results
        }
        fit_training_ids = {row.observation_id for row in fit_training_rows}
        if candidate_training_ids == fit_training_ids and weighted_rmse(
            candidate_training_results
        ) < weighted_rmse(initial_training_results):
            best_coefficients = candidate
            best_results = candidate_results
            best_training_results = candidate_training_results
        else:
            best_coefficients = literature_coefficients
            best_results = initial_results
            best_training_results = initial_training_results

        failed_ids = {
            str(result["observation_id"])
            for result in (
                *initial_training_failures,
                *initial_reserved_failures,
                *candidate_failures,
            )
        }
        sensitivity_rows = []
        for group_id in sorted({row.group_id for row in rows}):
            group = sorted(
                (
                    row
                    for row in rows
                    if row.group_id == group_id and row.observation_id not in failed_ids
                ),
                key=lambda row: row.loading,
            )
            if not group:
                continue
            sensitivity_rows.append(group[len(group) // 2])
        selected_sensitivity_rows = tuple(sensitivity_rows)
        best_sensitivity_results = _evaluate_batch(
            bundle,
            selected_sensitivity_rows,
            best_coefficients,
            offsets,
            with_sensitivity=True,
            workers=args.workers,
        )
        eos_sensitivity_rows, eos_sensitivity_receipt = _eos_parameter_sensitivities(
            bundle, selected_sensitivity_rows, best_coefficients, offsets
        )

    row_lookup = {row.observation_id: row for row in rows}
    state_failure_rows: list[dict[str, object]] = []
    for model_id, failures in (
        (
            "M5_literature_R4",
            [*initial_training_failures, *initial_reserved_failures],
        ),
        ("M5_fitted_R4", candidate_failures),
    ):
        evidence_stage = (
            "literature-R4 all-row evaluation"
            if model_id == "M5_literature_R4"
            else "fitted-R4 all-row evaluation"
        )
        for failure in failures:
            row = row_lookup[str(failure["observation_id"])]
            state_failure_rows.append(
                {
                    "model_id": model_id,
                    "observation_id": row.observation_id,
                    "source_key": row.source_key,
                    "role": row.role,
                    "temperature_c": row.temperature_k - 273.15,
                    "loading_mol_co2_per_mol_mea": row.loading,
                    "state_pressure_pa": row.pressure_pa,
                    "failure_kind": failure["failure_kind"],
                    "failure_reason": failure["failure_reason"],
                    "evidence_stage": evidence_stage,
                }
            )

    fit_rows: list[dict[str, object]] = []
    for model_id, coefficients, evaluated in (
        ("M5_literature_R4", literature_coefficients, initial_results),
        ("M5_fitted_R4", best_coefficients, best_results),
    ):
        for result in evaluated:
            row = row_lookup[str(result["observation_id"])]
            fit_rows.append(
                {
                    "model_id": model_id,
                    "observation_id": row.observation_id,
                    "source_key": row.source_key,
                    "mea_mass_fraction": row.mea_mass_fraction,
                    "temperature_k": row.temperature_k,
                    "temperature_c": row.temperature_k - 273.15,
                    "loading_mol_co2_per_mol_mea": row.loading,
                    "state_pressure_pa": row.pressure_pa,
                    "observed_pco2_pa": row.observed_pco2_pa,
                    "predicted_pco2_pa": result["predicted_pco2_pa"],
                    "log10_pressure_residual": result["log10_pressure_residual"],
                    "carbamate_target_mole_fraction": row.carbamate_target,
                    "predicted_carbamate_mole_fraction": result[
                        "carbamate_mole_fraction"
                    ],
                    "log10_carbamate_residual": result["log10_carbamate_residual"],
                    "carbamate_interpolation_lower_row": row.carbamate_lower_row,
                    "carbamate_interpolation_upper_row": row.carbamate_upper_row,
                    "ln_k4": _r4_ln_k(row.temperature_k, coefficients),
                    "split": row.split,
                    "role": row.role,
                    "group_id": row.group_id,
                    "measurement_origin": row.measurement_origin,
                    "certification": result["certification"],
                    "reaction_affinity_inf_norm": result["reaction_affinity_inf_norm"],
                    "kkt_stationarity_inf_norm": result["kkt_stationarity_inf_norm"],
                    "pressure_relative_residual": result["pressure_relative_residual"],
                    "packing_fraction": result["packing_fraction"],
                    "minimum_amount_mol": result["minimum_amount_mol"],
                    "model_fingerprint": result["model_fingerprint"],
                }
            )

    reaction_sensitivity_rows = []
    for result in best_sensitivity_results:
        row = row_lookup[str(result["observation_id"])]
        for reaction_id in REACTION_IDS:
            reaction_sensitivity_rows.append(
                {
                    "observation_id": row.observation_id,
                    "source_key": row.source_key,
                    "role": row.role,
                    "temperature_c": row.temperature_k - 273.15,
                    "loading_mol_co2_per_mol_mea": row.loading,
                    "reaction_id": reaction_id,
                    "dlog10_pco2_dlnk": result[f"dlog10_pco2_dlnk_{reaction_id}"],
                    "dlog10_meacoo_dlnk": result[f"dlog10_meacoo_dlnk_{reaction_id}"],
                }
            )

    parameter_rows = [
        {
            "parameter": "A",
            "unit": "dimensionless",
            "literature_value": literature_coefficients[0],
            "fitted_value": best_coefficients[0],
            "lower_bound": "",
            "upper_bound": "",
        },
        {
            "parameter": "B",
            "unit": "K",
            "literature_value": literature_coefficients[1],
            "fitted_value": best_coefficients[1],
            "lower_bound": "",
            "upper_bound": "",
        },
        {
            "parameter": "C",
            "unit": "dimensionless",
            "literature_value": literature_coefficients[2],
            "fitted_value": best_coefficients[2],
            "lower_bound": "",
            "upper_bound": "",
        },
        {
            "parameter": "D",
            "unit": "1/K",
            "literature_value": literature_coefficients[3],
            "fitted_value": best_coefficients[3],
            "lower_bound": "",
            "upper_bound": "",
        },
        {
            "parameter": "lnK4_at_313.15K",
            "unit": "dimensionless",
            "literature_value": _r4_ln_k(
                REFERENCE_TEMPERATURE_K, literature_coefficients
            ),
            "fitted_value": _r4_ln_k(REFERENCE_TEMPERATURE_K, best_coefficients),
            "lower_bound": R4_LN_K_BOUNDS[0],
            "upper_bound": R4_LN_K_BOUNDS[1],
        },
    ]
    _write_csv(FIGURE_OUTPUT / "r4_correlation_fit_rows.csv", fit_rows)
    _write_csv(RESULTS / "r4_correlation_fit_parameters.csv", parameter_rows)
    _write_csv(RESULTS / "r4_correlation_fit_metrics.csv", _metric_rows(fit_rows))
    _write_csv(
        FIGURE_OUTPUT / "r4_reaction_sensitivity_rows.csv",
        reaction_sensitivity_rows,
    )
    _write_csv(FIGURE_OUTPUT / "r4_eos_sensitivity_rows.csv", eos_sensitivity_rows)
    _write_csv(RESULTS / "r4_state_failures.csv", state_failure_rows)

    transfer_values = tuple(transfer_receipts.values())
    receipt = {
        "status": "diagnostic_multisource_regression",
        "objective": "group-normalized Hilliard-40C and Jou-40C-to-120C pCO2 regression",
        "correlation": "lnK4(T) = A + B/T + C ln(T) + D T",
        "row_counts": {
            "training_admitted": len(training_rows),
            "training_fit_evaluated": len(fit_training_rows),
            "training_failed": len(initial_training_failures),
            "reserved_validation": len(rows) - len(training_rows),
            "literature_evaluated": len(initial_results),
            "fitted_evaluated": len(best_results),
            "failure_records": len(state_failure_rows),
        },
        "training_groups": dict(sorted(group_counts.items())),
        "canonical_split_sha256": _sha256(CANONICAL_SPLIT),
        "analysis_partition_sha256": _sha256(ANALYSIS_PARTITION),
        "partition_role": "Analysis-local override for this nonpromoting experiment; the canonical 147/220 split is unchanged.",
        "carbamate_role": "source-interpolated comparison only; excluded from the objective",
        "source_domain_limit": (
            "The selected R4 and R5 literature correlations end at 323.15 K. "
            "R5 is extrapolated for Jou rows above 323.15 K, so this R4-only fit cannot be promoted."
        ),
        "provider_domain_role": (
            "The authority-neutral M5 input bundle uses the source-row 313.15--393.15 K and "
            "6105.45--3000000 Pa fit range only inside a temporary application-owned copy."
        ),
        "fit_method": "one group-normalized exact-sensitivity Gauss-Newton update in column-scaled A/B/C/D coordinates; candidate retained only if the evaluated training objective improves",
        "row_weighting": "equal total weight per source/temperature group; equal weight within each group",
        "safeguard": {"ln_k4_over_training_temperatures": list(R4_LN_K_BOUNDS)},
        "regularization": "none",
        "derivative_audit": {
            "directional_step": EOS_DIRECTIONAL_STEP,
            "absolute_tolerance": EOS_DIRECTIONAL_ABS_TOLERANCE,
            "relative_tolerance": EOS_DIRECTIONAL_REL_TOLERANCE,
        },
        "initial_training_log10_pressure_rmse": _rmse(initial_training_results),
        "fitted_training_log10_pressure_rmse": _rmse(best_training_results),
        "initial_group_normalized_training_log10_pressure_rmse": weighted_rmse(
            initial_training_results
        ),
        "fitted_group_normalized_training_log10_pressure_rmse": weighted_rmse(
            best_training_results
        ),
        "initial_all_row_log10_pressure_rmse": _rmse(initial_results),
        "fitted_all_row_log10_pressure_rmse": _rmse(best_results),
        "literature": dict(
            zip(("a", "b_k", "c", "d_per_k"), literature_coefficients, strict=True)
        ),
        "fitted": dict(
            zip(("a", "b_k", "c", "d_per_k"), best_coefficients, strict=True)
        ),
        "identifiability": {
            "unique_training_temperatures": training_temperatures,
            "jacobian_rank": iterations[0]["jacobian_rank"],
            "scaled_jacobian_condition_number": iterations[0][
                "scaled_jacobian_condition_number"
            ],
            "raw_jacobian_condition_number": iterations[0][
                "raw_jacobian_condition_number"
            ],
            "interpretation": "A/B/C/D are numerically fitted but are not separately identifiable when the scaled Jacobian remains ill-conditioned.",
        },
        "active_bound": bool(
            any(
                math.isclose(
                    _r4_ln_k(temperature, best_coefficients), bound, abs_tol=1.0e-8
                )
                for temperature in training_temperatures
                for bound in R4_LN_K_BOUNDS
            )
        ),
        "promotion_allowed": False,
        "generated_bundle_files": generated_bundle_files,
        "base_bundle_files": _tree_hashes(BASE_BUNDLE),
        "source_files": {
            str(path.relative_to(REPO_ROOT)): _sha256(path)
            for path in (
                VLE,
                SPECIATION,
                METROLOGY,
                CANONICAL_SPLIT,
                REACTION_CONTRACT,
                SENTINEL_CONTRACT,
                SOURCE_REFERENCE,
                ANALYSIS_PARTITION,
            )
        },
        "installed_artifacts": {
            "provider": installed_artifacts["epcsaft"],
            "equilibrium": installed_artifacts["epcsaft-equilibrium"],
        },
        "eos_sensitivity": eos_sensitivity_receipt,
        "source_reference_transfer": {
            "evaluated_state_count": len(transfer_values),
            "convergence_tolerance": SOURCE_REFERENCE_CONVERGENCE_TOLERANCE,
            "artifact_fingerprints": sorted(
                {str(item["artifact_fingerprint"]) for item in transfer_values}
            ),
            "reference_state_fingerprints": sorted(
                {str(item["reference_state_fingerprint"]) for item in transfer_values}
            ),
            "domain_fingerprints": sorted(
                {str(item["domain_fingerprint"]) for item in transfer_values}
            ),
            "maximum_reference_convergence_error": max(
                float(item["reference_convergence_error"]) for item in transfer_values
            ),
        },
    }
    write_json_file(RESULTS / "r4_correlation_fit_receipt.json", receipt)
    print(json.dumps(receipt["fitted"], indent=2))
    print(
        "group-normalized training log10 pressure RMSE: "
        f"{receipt['initial_group_normalized_training_log10_pressure_rmse']:.6f} -> "
        f"{receipt['fitted_group_normalized_training_log10_pressure_rmse']:.6f}"
    )


if __name__ == "__main__":
    main()
