from __future__ import annotations

import math
from pathlib import Path
from typing import Literal

from epcsaft import ParameterBundle, unit_registry as u
from epcsaft.records import (
    AssociationParameterRecord,
    ComponentRecord,
    ConstantPlusSumOfExponentialsCorrelation,
    ExponentialTerm,
    ModelParameterRecord,
    PairParameterRecord,
    SingleParameterRecord,
    SiteRecord,
    SourceRecord,
    ValidityDomain,
)

from MEA.common.analysis_io import read_csv_rows
from MEA.smith_missen.ideal_speciation import SPECIES_9


REPO_ROOT = Path(__file__).resolve().parents[3]
PARAMETER_ROOT = (
    REPO_ROOT / "data" / "reference" / "epcsaft_datasets" / "MEA_CO2_H2O_phase2"
)
PURE_CSV = PARAMETER_ROOT / "pure" / "any_solvent.csv"
KIJ_CSV = PARAMETER_ROOT / "mixed" / "binary_interaction" / "k_ij.csv"
SOURCE_AUDIT = REPO_ROOT / "docs" / "ePC-SAFT" / "full-component-parameter-source-audit.md"
SOURCE_PATHS = (PURE_CSV, KIJ_CSV, SOURCE_AUDIT)
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
SOURCE_ID = "mea-retained-phase-two-artifact"
DOMAIN_ID = "diagnostic-domain"
REFERENCE_TEMPERATURE_K = 313.15


def _status(species: str) -> str:
    if species in {"MEAH+", "MEACOO-"}:
        return "provisional-historical-evaluation"
    if species in {"HCO3-", "CO3^2-", "H3O+", "OH-"}:
        return "transferred-diagnostic"
    return "retained-literature-lineage"


def _provenance(locator: str) -> dict[str, str]:
    return {
        "source_id": SOURCE_ID,
        "locator": locator,
        "domain_id": DOMAIN_ID,
    }


def _pure_locator(species: str, family: str) -> str:
    relative = PURE_CSV.relative_to(REPO_ROOT).as_posix()
    return f"{relative}:component={species}:family={family}:status={_status(species)}"


def _read_kij() -> dict[tuple[str, str], float]:
    values: dict[tuple[str, str], float] = {}
    for row in read_csv_rows(KIJ_CSV):
        left = str(row["component"])
        for right in SPECIES_9:
            if left != right:
                values[tuple(sorted((left, right)))] = float(row[right])
    return values


def build_mea_diagnostic_bundle(
    *,
    purpose: Literal["package-test-fixture", "user-provided"],
) -> ParameterBundle:
    pure_rows = read_csv_rows(PURE_CSV)
    by_species = {str(row["component"]): row for row in pure_rows}
    component_by_species = dict(zip(SPECIES_9, COMPONENT_IDS, strict=True))
    components = tuple(
        ComponentRecord(component_id, name=species, aliases=(species,))
        for species, component_id in component_by_species.items()
    )
    singles: list[SingleParameterRecord] = []
    correlations: list[ConstantPlusSumOfExponentialsCorrelation] = []
    for species, component_id in component_by_species.items():
        row = by_species[species]
        values = (
            ("molar_mass", float(row["MW"]) * u.kilogram / u.mole, "molar-mass"),
            ("segment_count", float(row["m"]), "segment-count"),
            ("dispersion_energy_over_k", float(row["e"]) * u.kelvin, "dispersion-energy"),
            ("charge_number", int(row["z"]), "charge"),
            ("solvation_factor", float(row["f_solv"]), "solvation-factor"),
        )
        for family, value, record_suffix in values:
            singles.append(
                SingleParameterRecord(
                    f"{component_id}-{record_suffix}",
                    component_id,
                    family,
                    value,
                    **_provenance(_pure_locator(species, family)),
                )
            )
        if species == "H2O":
            correlations.append(
                ConstantPlusSumOfExponentialsCorrelation(
                    f"{component_id}-segment-diameter",
                    component_id,
                    "segment_diameter",
                    2.7927 * u.angstrom,
                    (
                        ExponentialTerm(10.11 * u.angstrom, -0.01775 / u.kelvin),
                        ExponentialTerm(-1.417 * u.angstrom, -0.01146 / u.kelvin),
                    ),
                    **_provenance(_pure_locator(species, "segment_diameter")),
                )
            )
        else:
            singles.append(
                SingleParameterRecord(
                    f"{component_id}-segment-diameter",
                    component_id,
                    "segment_diameter",
                    float(row["s"]) * u.angstrom,
                    **_provenance(_pure_locator(species, "segment_diameter")),
                )
            )
        if int(row["z"]) == 0:
            singles.append(
                SingleParameterRecord(
                    f"{component_id}-relative-permittivity",
                    component_id,
                    "relative_permittivity",
                    float(row["dielc"]),
                    **_provenance(_pure_locator(species, "relative_permittivity")),
                )
            )
        else:
            singles.append(
                SingleParameterRecord(
                    f"{component_id}-born-diameter",
                    component_id,
                    "born_diameter",
                    float(row["d_born"]) * u.angstrom,
                    **_provenance(_pure_locator(species, "born_diameter")),
                )
            )

    kij = _read_kij()
    pairs: list[PairParameterRecord] = []
    kij_relative = KIJ_CSV.relative_to(REPO_ROOT).as_posix()
    for left_index, left in enumerate(SPECIES_9):
        for right in SPECIES_9[left_index + 1 :]:
            left_id = component_by_species[left]
            right_id = component_by_species[right]
            pair_status = (
                "provisional-historical-evaluation"
                if {left, right} == {"MEAH+", "MEACOO-"}
                else "explicit-diagnostic"
            )
            pairs.append(
                PairParameterRecord(
                    f"kij-{left_id}-{right_id}",
                    left_id,
                    right_id,
                    "k_ij",
                    kij[tuple(sorted((left, right)))],
                    **_provenance(
                        f"{kij_relative}:row={left}:column={right}:status={pair_status}"
                    ),
                )
            )

    associating = ("MEA", "H2O")
    sites = tuple(
        SiteRecord(
            f"{component_by_species[species]}-site-{site}",
            component_by_species[species],
            site,
            site,
            1,
            **_provenance(_pure_locator(species, f"association_site_{site}")),
        )
        for species in associating
        for site in ("a", "b")
    )
    associations: list[AssociationParameterRecord] = []
    for species in associating:
        row = by_species[species]
        component_id = component_by_species[species]
        for family, value, unit in (
            ("association_energy_over_k", float(row["e_assoc"]), u.kelvin),
            ("association_volume", float(row["vol_a"]), 1.0),
        ):
            associations.append(
                AssociationParameterRecord(
                    f"{component_id}-self-{family.replace('_', '-')}",
                    component_id,
                    "a",
                    component_id,
                    "b",
                    family,
                    value * unit,
                    **_provenance(_pure_locator(species, family)),
                )
            )
    water_sigma = (
        2.7927
        + 10.11 * math.exp(-0.01775 * REFERENCE_TEMPERATURE_K)
        - 1.417 * math.exp(-0.01146 * REFERENCE_TEMPERATURE_K)
    )
    mea_sigma = float(by_species["MEA"]["s"])
    cross_energy = 0.5 * (
        float(by_species["H2O"]["e_assoc"]) + float(by_species["MEA"]["e_assoc"])
    )
    cross_volume = math.sqrt(
        float(by_species["H2O"]["vol_a"]) * float(by_species["MEA"]["vol_a"])
    ) * (math.sqrt(water_sigma * mea_sigma) / (0.5 * (water_sigma + mea_sigma))) ** 3
    for water_site, mea_site in (("a", "b"), ("b", "a")):
        for family, value, unit in (
            ("association_energy_over_k", cross_energy, u.kelvin),
            ("association_volume", cross_volume, 1.0),
        ):
            associations.append(
                AssociationParameterRecord(
                    f"water-{water_site}-mea-{mea_site}-{family.replace('_', '-')}",
                    component_by_species["H2O"],
                    water_site,
                    component_by_species["MEA"],
                    mea_site,
                    family,
                    value * unit,
                    **_provenance(
                        "Wolbach-Sandler cross-association combining rule at 313.15 K; "
                        "inputs=data/reference/epcsaft_datasets/MEA_CO2_H2O_phase2/"
                        "pure/any_solvent.csv:rows=H2O,MEA:status=retained-diagnostic"
                    ),
                )
            )

    models = (
        ModelParameterRecord(
            "dielectric-ion-suppression",
            "dielectric_ion_suppression_coefficient",
            7.01,
            **_provenance(
                "data/reference/epcsaft_datasets/MEA_CO2_H2O_phase2/"
                "user_options.json:dielectric_saturation:status=retained-diagnostic"
            ),
        ),
        ModelParameterRecord(
            "ionic-region-permittivity",
            "ionic_region_relative_permittivity",
            8.0,
            **_provenance(
                "data/reference/epcsaft_datasets/MEA_CO2_H2O_phase2/"
                "pure/any_solvent.csv:ionic-dielc=8:status=transferred-diagnostic"
            ),
        ),
    )
    return ParameterBundle.from_records(
        bundle_id="mea-co2-h2o-nine-species-diagnostic",
        bundle_version=1,
        purpose=purpose,
        sources=(
            SourceRecord(
                SOURCE_ID,
                "MEA-Thermodynamics retained Phase 2 parameter artifact",
                "diagnostic nonpredictive evaluation input; exact literature lineage and provisional rows are audited in docs/ePC-SAFT/full-component-parameter-source-audit.md",
            ),
        ),
        domains=(ValidityDomain(DOMAIN_ID, "unknown"),),
        components=components,
        singles=tuple(singles),
        pairs=tuple(pairs),
        sites=sites,
        associations=tuple(associations),
        correlations=tuple(correlations),
        models=models,
    )
