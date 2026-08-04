from __future__ import annotations

import csv
from fractions import Fraction
import hashlib
import json
import math
from pathlib import Path
from typing import Any

from MEA.common.config import DATA_ROOT, REPO_ROOT


REACTION_CONTRACT_PATH = DATA_ROOT / "manifests" / "chemical_reaction_source_contract.json"
SENTINEL_CONTRACT_PATH = (
    DATA_ROOT / "manifests" / "homogeneous_speciation_sentinel_contract.json"
)
EXPECTED_SPECIES_ORDER = (
    "CO2",
    "MEA",
    "H2O",
    "MEAH+",
    "MEACOO-",
    "HCO3-",
    "CO3--",
    "H3O+",
    "OH-",
)
EXPECTED_PROVIDER_SPECIES_ORDER = (
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
PRIMARY_ANCHORS_298_15_K = {
    "R1": -40.26536023393261,
    "R2": -18.658825483177367,
    "R3": -27.80868301316974,
    "R4": -3.031961596511823,
    "R5": -21.86574617291778,
}
EXPECTED_REACTION_CORRELATIONS = {
    "R1": {
        "kind": "ln_a_plus_b_over_t_plus_c_ln_t_plus_d_t",
        "a": 132.899,
        "b_k": -13445.9,
        "c": -22.4773,
        "d_per_k": 0.0,
    },
    "R2": {
        "kind": "ln_a_plus_b_over_t_plus_c_ln_t_plus_d_t",
        "a": 231.465,
        "b_k": -12092.1,
        "c": -36.7816,
        "d_per_k": 0.0,
    },
    "R3": {
        "kind": "ln_a_plus_b_over_t_plus_c_ln_t_plus_d_t",
        "a": 216.049,
        "b_k": -12431.7,
        "c": -35.4819,
        "d_per_k": 0.0,
    },
    "R4": {"kind": "ln_a_plus_b_over_t", "a": 2.151, "b_k": -1545.3},
    "R5": {
        "kind": "ln_from_negative_log10_a_over_t_plus_b_plus_c_t",
        "a_k": 2677.91,
        "b": 0.3869,
        "c_per_k": 0.0004277,
    },
}
EXPECTED_REACTION_SOURCE_RECORDS = [
    {
        "source_id": "Austgen1991",
        "doi": "10.1021/ie00051a007",
        "locator": "pp. 545-547, Standard States, Eq. 3, Eq. 7, Table V",
        "local_pdf_sha256": "8c0a6a57e5bf9e28b1f9da8022d54290506fe04b4286b6494ef8a44fd924f8db",
    },
    {
        "source_id": "Tong2012",
        "doi": "10.1016/j.ijggc.2011.11.005",
        "locator": "pp. 43-44, Eqs. 5-9 and 12, Table 5",
        "local_pdf_sha256": "78af3d67d58ff610dcc7c34fd55a75763470b7cd5bac0f3e39c256c7d7ffd61c",
    },
    {
        "source_id": "Aroua1999",
        "doi": "10.1021/je980290n",
        "locator": (
            "abstract and pp. 887-891; log10 Kformation = -0.934 + 671/T "
            "at infinite dilution"
        ),
        "local_pdf_sha256": None,
    },
    {
        "source_id": "BatesPinching1951",
        "doi": "10.6028/jres.046.039",
        "locator": "p. 349 and Eq. 7; -log10 K = 2677.91/T + 0.3869 + 0.0004277 T",
        "official_pdf": (
            "https://nvlpubs.nist.gov/nistpubs/jres/46/"
            "jresv46n5p349_A1b.pdf"
        ),
        "official_pdf_sha256": (
            "aff8621efd41dbce106bb189fd104840a1513d9d163f4f57dfb1abbf53a30db1"
        ),
        "local_pdf_sha256": None,
    },
]
EXPECTED_REACTION_SOURCE_IDS = {
    "R1": ["Austgen1991"],
    "R2": ["Austgen1991"],
    "R3": ["Austgen1991"],
    "R4": ["Tong2012", "Aroua1999"],
    "R5": ["BatesPinching1951"],
}
EXPECTED_SENTINEL_SOURCE_RECORDS = [
    {
        "source_id": "Wong2015",
        "doi": "10.1016/j.ijggc.2015.05.016",
        "locator": "Table 5, 313.15 K first 1 bar batch row",
        "local_pdf_sha256": (
            "312ea8218c98bf6b78289c5f43baf4e524442efd3943f1dfaf74270ff1292954"
        ),
    },
    {
        "source_id": "Bottinger2008",
        "doi": "10.1016/j.fluid.2007.09.017",
        "locator": "experimental pressure range and p. 128 oxazolidone discussion",
        "local_pdf_sha256": (
            "dd0c6986cbd058ec0a2343ac5097439862281492cd2dac01823144233f0fc0f4"
        ),
    },
]
EXPECTED_PROVIDER_INPUT = {
    "identity": "mea-nine-species-regression-input-v1",
    "bundle_path": (
        "data/reference/epcsaft_bundles/"
        "mea-co2-h2o-nine-species-regression-input/1"
    ),
    "receipt_path": (
        "data/reference/epcsaft_bundles/"
        "mea-co2-h2o-nine-species-regression-input/1.receipt.json"
    ),
    "receipt_sha256": (
        "3f8da81a07bd51178f4e929b17b92379c28e58799a889262a076f00bee3bcaf2"
    ),
    "bundle_id": "mea-co2-h2o-nine-species-regression-input",
    "bundle_version": 1,
    "bundle_fingerprint": (
        "sha256:741673651fa0120f6f6427a750674b0f7929a3da571dd6d1dd84d40485ae2553"
    ),
    "bundle_file_manifest_sha256": (
        "9633f197cb09afa8b4c36fba12fad17099fc0688b210c0d6254feb2553e860ea"
    ),
    "component_order_sha256": (
        "246049d6caa54cf752ab0e6257812c39d4e9deb5f079db3dd96280bd2ae05e85"
    ),
    "parameter_fingerprint": (
        "sha256:3773585e061b37643f5c7794e18424b83c86b82fa658983a0ee13fd8f1876fd6"
    ),
    "topology_fingerprint": (
        "sha256:4cd30249026b7361ee68b618f7437de081b0339e5a7b0cc41165930a01a4e762"
    ),
    "domain_id": "mea-tracer-313-15-k-fit-range",
    "domain_fingerprint": (
        "93510b66543e4e9e49c409a658b1bf7a01599ccd9ce3feef41bbab6b6eb668ab"
    ),
    "temperature_k": [313.15, 313.15],
    "pressure_pa": [6105.45, 300000.0],
    "provider_commit": "d88e9af12c6d7e4d5ef5d916c4d610920348e5a2",
    "provider_tree": "a6a1bcecce3521f5b2d32f9c819e6b882c9a3f42",
    "provider_wheel_sha256": (
        "4cee10a9158576307cda93f611b6ade3a7cf8819df44f83efe8cbc61ab038789"
    ),
    "provider_header_sha256": (
        "bb46f103b7116efcc31f000cd07082f2d79c36a3236265d3e1d9ab4d27cc733f"
    ),
    "provider_distribution_record_sha256": (
        "ba7dc8df2d9e96c03ec1e37c260f775420718ce1cacddf1b35b9f5248043dec6"
    ),
    "provider_installed_module_sha256": (
        "e3378b0b773be60da75aa4eaee36bb3078b3bfccca3b41def0c4e84ed849939e"
    ),
    "provider_capability_count": 17,
}
EXPECTED_BUNDLE_FILE_HASHES = {
    "association.csv": "195a8047403fc20ed414f29835d9f8d936e349e5baf4fb4264b7f2acb412b83e",
    "bundle.toml": "ef19afb3e5495e1128edf751f177a308c1e5a3ca6f8ad2948f25718f829cf96d",
    "components.csv": "3baa84d19c6db2252f8bfb29685821ec72a21171975a3f0239da62d77f347b75",
    "correlations.toml": (
        "733d92b4c348a5ad3f8aef3fed468f209ab0b99c82da43c6bfe471006a262114"
    ),
    "model.csv": "3f8a40d5015a69fcca82769ec9bbaa979494728a3f2c5288b567cd9a4b4421f4",
    "pair.csv": "f82391721156dd228356fc5b27f69d5768338eddb5ddd2d56e5abc95423ee112",
    "single.csv": "feb86ed20feca7956e640845f0a1a1e14fde956bdad9900908fca560a6743c9a",
    "sites.csv": "67b27bd84679bdf513a36ec4f1ca9e3dd1ee5923bab4fb5851cb64a1fe60ba8b",
}


def _load_json(path: Path) -> dict[str, Any]:
    with path.open(encoding="utf-8") as handle:
        value = json.load(handle)
    if not isinstance(value, dict):
        raise ValueError(f"Contract must be a JSON object: {path}")
    return value


def load_reaction_contract(
    path: Path = REACTION_CONTRACT_PATH,
) -> dict[str, Any]:
    return _load_json(path)


def load_sentinel_contract(
    path: Path = SENTINEL_CONTRACT_PATH,
) -> dict[str, Any]:
    return _load_json(path)


def common_source_ln_k(
    temperature_k: float,
    contract: dict[str, Any] | None = None,
) -> tuple[float, ...]:
    """Evaluate the five source constants on the frozen common activity scale."""

    contract = load_reaction_contract() if contract is None else contract
    source = validate_reaction_contract(contract)
    lower, upper = source["temperature_intersection_k"]
    if not lower <= temperature_k <= upper:
        raise ValueError("temperature lies outside the common reaction-source domain")
    reactions = contract["reactions"]
    offsets = contract["common_source_standard_state"][
        "source_to_common_ln_k_offsets"
    ]
    return tuple(
        _evaluate_ln_k(reaction, temperature_k) + float(offset)
        for reaction, offset in zip(reactions, offsets, strict=True)
    )


def _exact_rank(matrix: list[list[int]]) -> int:
    work = [[Fraction(value) for value in row] for row in matrix]
    if not work:
        return 0
    row_count = len(work)
    column_count = len(work[0])
    rank = 0
    for column in range(column_count):
        pivot = next(
            (row for row in range(rank, row_count) if work[row][column] != 0),
            None,
        )
        if pivot is None:
            continue
        work[rank], work[pivot] = work[pivot], work[rank]
        scale = work[rank][column]
        work[rank] = [value / scale for value in work[rank]]
        for row in range(row_count):
            if row == rank:
                continue
            multiple = work[row][column]
            if multiple:
                work[row] = [
                    value - multiple * pivot_value
                    for value, pivot_value in zip(work[row], work[rank], strict=True)
                ]
        rank += 1
        if rank == row_count:
            break
    return rank


def _evaluate_ln_k(reaction: dict[str, Any], temperature_k: float) -> float:
    correlation = reaction["correlation"]
    kind = correlation["kind"]
    if kind == "ln_a_plus_b_over_t_plus_c_ln_t_plus_d_t":
        return (
            correlation["a"]
            + correlation["b_k"] / temperature_k
            + correlation["c"] * math.log(temperature_k)
            + correlation["d_per_k"] * temperature_k
        )
    if kind == "ln_a_plus_b_over_t":
        return correlation["a"] + correlation["b_k"] / temperature_k
    if kind == "ln_from_negative_log10_a_over_t_plus_b_plus_c_t":
        return -math.log(10.0) * (
            correlation["a_k"] / temperature_k
            + correlation["b"]
            + correlation["c_per_k"] * temperature_k
        )
    raise ValueError(f"Unsupported reaction correlation kind: {kind}")


def _canonical_sha256(value: Any) -> str:
    encoded = json.dumps(
        value, sort_keys=True, separators=(",", ":"), ensure_ascii=True
    ).encode("utf-8")
    return hashlib.sha256(encoded).hexdigest()


def _expected_immutable_identities() -> dict[str, Any]:
    return {
        "bundle_id": EXPECTED_PROVIDER_INPUT["bundle_id"],
        "bundle_version": EXPECTED_PROVIDER_INPUT["bundle_version"],
        "bundle_fingerprint": EXPECTED_PROVIDER_INPUT["bundle_fingerprint"],
        "bundle_file_manifest_sha256": EXPECTED_PROVIDER_INPUT[
            "bundle_file_manifest_sha256"
        ],
        "bundle_file_hashes": EXPECTED_BUNDLE_FILE_HASHES,
        "component_ids": list(EXPECTED_PROVIDER_SPECIES_ORDER),
        "component_order_sha256": EXPECTED_PROVIDER_INPUT[
            "component_order_sha256"
        ],
        "parameter_fingerprint": EXPECTED_PROVIDER_INPUT["parameter_fingerprint"],
        "topology_fingerprint": EXPECTED_PROVIDER_INPUT["topology_fingerprint"],
        "domain_id": EXPECTED_PROVIDER_INPUT["domain_id"],
        "domain_fingerprint": EXPECTED_PROVIDER_INPUT["domain_fingerprint"],
        "temperature_k": EXPECTED_PROVIDER_INPUT["temperature_k"],
        "pressure_pa": EXPECTED_PROVIDER_INPUT["pressure_pa"],
        "provider_commit": EXPECTED_PROVIDER_INPUT["provider_commit"],
        "provider_tree": EXPECTED_PROVIDER_INPUT["provider_tree"],
        "provider_wheel_sha256": EXPECTED_PROVIDER_INPUT["provider_wheel_sha256"],
        "provider_header_sha256": EXPECTED_PROVIDER_INPUT["provider_header_sha256"],
    }


def validate_reaction_contract(contract: dict[str, Any]) -> dict[str, Any]:
    if (
        contract.get("schema_version") != 2
        or contract.get("identity") != "mea-nine-species-reaction-source-contract-v2"
        or contract.get("status")
        != "source_adjudicated_provider_transform_frozen"
    ):
        raise ValueError("Unexpected MEA reaction contract identity")
    species_order = tuple(contract.get("species_order", ()))
    if species_order != EXPECTED_SPECIES_ORDER:
        raise ValueError("MEA reaction species order does not match the nine-species contract")
    provider_species_order = tuple(contract.get("provider_species_order", ()))
    mappings = contract.get("source_to_provider_species_identity", [])
    if (
        provider_species_order != EXPECTED_PROVIDER_SPECIES_ORDER
        or any(set(row) != {"source_identity", "provider_identity", "charge"} for row in mappings)
        or [row.get("source_identity") for row in mappings]
        != list(EXPECTED_SPECIES_ORDER)
        or [row.get("provider_identity") for row in mappings]
        != list(EXPECTED_PROVIDER_SPECIES_ORDER)
        or [int(row.get("charge", 99)) for row in mappings]
        != [0, 0, 0, 1, -1, -1, -2, 1, -1]
    ):
        raise ValueError("MEA source-to-Provider species identity map is incomplete")

    species = contract.get("species", [])
    if [row.get("name") for row in species] != list(EXPECTED_SPECIES_ORDER):
        raise ValueError("MEA species records do not match the declared order")
    balance_rows = [
        [int(row["formula"][element]) for row in species]
        for element in contract["balance_row_order"]
    ]
    balance_rank = _exact_rank(balance_rows)
    if balance_rank != contract.get("declared_balance_rank"):
        raise ValueError("MEA balance matrix rank does not match its declaration")

    reactions = contract.get("reactions", [])
    if [row.get("reaction_id") for row in reactions] != list(PRIMARY_ANCHORS_298_15_K):
        raise ValueError("MEA reaction records must contain ordered unique R1-R5 rows")
    source_records = contract.get("source_records", [])
    source_ids = {row.get("source_id") for row in source_records}
    if None in source_ids or len(source_ids) != len(source_records):
        raise ValueError("MEA reaction source records must have unique source identities")
    if source_records != EXPECTED_REACTION_SOURCE_RECORDS:
        raise ValueError("MEA reaction source artifact identities have drifted")
    reaction_matrix = [list(map(int, row["stoichiometry"])) for row in reactions]
    if any(len(row) != len(species) for row in reaction_matrix):
        raise ValueError("MEA reaction stoichiometry dimensions do not match species order")
    reaction_rank = _exact_rank(reaction_matrix)
    if reaction_rank != contract.get("declared_reaction_rank"):
        raise ValueError("MEA reaction matrix rank does not match its declaration")

    for reaction, expected in zip(
        reactions, PRIMARY_ANCHORS_298_15_K.values(), strict=True
    ):
        reaction_id = reaction["reaction_id"]
        required_metadata = (
            "equation",
            "selected_source",
            "source_role",
            "activity_convention",
            "source_standard_state",
            "pressure_binding",
        )
        if (
            any(not reaction.get(field) for field in required_metadata)
            or reaction.get("dimensionless") is not True
            or reaction.get("contract_logarithm") != "natural"
            or reaction.get("source_record_ids")
            != EXPECTED_REACTION_SOURCE_IDS[reaction_id]
        ):
            raise ValueError(f"{reaction_id} source metadata is incomplete")
        if reaction.get("correlation") != EXPECTED_REACTION_CORRELATIONS[reaction_id]:
            raise ValueError(f"{reaction_id} primary-source correlation coefficients drifted")
        if reaction_id in {"R4", "R5"} and (
            "p°=100 kPa" not in reaction["pressure_binding"]
            or "every receipt-admitted trial system pressure"
            not in reaction["pressure_binding"]
        ):
            raise ValueError(f"{reaction_id} pressure-reference provenance drifted")
        temperature_k = float(reaction["anchor_temperature_k"])
        actual = _evaluate_ln_k(reaction, temperature_k)
        tolerance = float(reaction["anchor_abs_tolerance"])
        if abs(actual - expected) > tolerance:
            raise ValueError(f"{reaction_id} primary-source anchor is inconsistent")
        if abs(float(reaction["anchor_ln_k"]) - expected) > tolerance:
            raise ValueError(f"{reaction_id} retained anchor is inconsistent")
        lower, upper = map(float, reaction["temperature_range_k"])
        if not lower <= temperature_k <= upper:
            raise ValueError(f"{reaction_id} anchor lies outside its source range")
        for balance in balance_rows:
            if sum(
                coefficient * amount
                for coefficient, amount in zip(balance, reaction["stoichiometry"], strict=True)
            ):
                raise ValueError(f"{reaction_id} does not conserve the declared elements")
        if sum(
            int(row["charge"]) * amount
            for row, amount in zip(species, reaction["stoichiometry"], strict=True)
        ):
            raise ValueError(f"{reaction_id} does not conserve charge")

    if _exact_rank([*balance_rows, *reaction_matrix]) != len(species):
        raise ValueError("MEA balances and reactions do not span the species space")
    temperature_intersection = [
        max(float(row["temperature_range_k"][0]) for row in reactions),
        min(float(row["temperature_range_k"][1]) for row in reactions),
    ]
    if temperature_intersection[0] > temperature_intersection[1]:
        raise ValueError("MEA reaction source temperature domains do not intersect")

    common = contract.get("common_source_standard_state", {})
    if (
        common.get("identity") != "aqueous-molality-infinite-dilution-water-v1"
        or common.get("ready") is not True
        or common.get("solvent") != "H2O"
        or float(common.get("solute_standard_molality_mol_per_kg", 0.0)) != 1.0
    ):
        raise ValueError("MEA common source standard state is incomplete")
    water_molar_mass = float(common["water_molar_mass_kg_per_mol"])
    log_scale = math.log(
        water_molar_mass * float(common["solute_standard_molality_mol_per_kg"])
    )
    expected_scales = [
        0.0 if species_id == "H2O" else log_scale
        for species_id in EXPECTED_SPECIES_ORDER
    ]
    if any(
        abs(actual - expected) > 5.0e-15
        for actual, expected in zip(
            common["log_activity_scale_factors_by_species"],
            expected_scales,
            strict=True,
        )
    ):
        raise ValueError("MEA common source activity-scale vector is inconsistent")
    molar_mass_path = REPO_ROOT / common["water_molar_mass_source"]
    water_molar_mass_row = _source_row(molar_mass_path, "water-molar-mass")
    if (
        common.get("water_molar_mass_source")
        != f"{EXPECTED_PROVIDER_INPUT['bundle_path']}/single.csv"
        or common.get("water_molar_mass_source_sha256")
        != EXPECTED_BUNDLE_FILE_HASHES["single.csv"]
        or _sha256(molar_mass_path) != EXPECTED_BUNDLE_FILE_HASHES["single.csv"]
        or water_molar_mass_row.get("component_id") != "water"
        or water_molar_mass_row.get("family") != "molar_mass"
        or water_molar_mass_row.get("unit") != "kilogram / mole"
        or float(water_molar_mass_row.get("value", 0.0)) != water_molar_mass
    ):
        raise ValueError("MEA common source water-molar-mass fingerprint does not match")
    exponents = list(map(int, common["source_to_common_solute_stoichiometric_exponents"]))
    if exponents != [2, 1, 1, 0, 0]:
        raise ValueError("MEA source-to-common reaction exponents are inconsistent")
    offsets = [-exponent * log_scale for exponent in exponents]
    if any(
        abs(actual - expected) > 5.0e-15
        for actual, expected in zip(
            common["source_to_common_ln_k_offsets"], offsets, strict=True
        )
    ):
        raise ValueError("MEA source-to-common lnK offsets are inconsistent")
    common_ln_k = [
        anchor + offset
        for anchor, offset in zip(
            PRIMARY_ANCHORS_298_15_K.values(), offsets, strict=True
        )
    ]
    if any(
        abs(actual - expected) > 5.0e-15
        for actual, expected in zip(
            common["common_ln_k_298_15_k"], common_ln_k, strict=True
        )
    ):
        raise ValueError("MEA common-source lnK anchors are inconsistent")

    provider_transform = contract.get("provider_transform", {})
    payload = provider_transform.get("deterministic_payload", {})
    required_receipt = provider_transform.get("required_provider_receipt", {})
    expected_provider_identities = [
        "provider_distribution",
        "provider_version",
        "provider_commit",
        "provider_tree",
        "installed_artifact_sha256",
        "bundle_id",
        "bundle_version",
        "bundle_sha256",
        "parameter_fingerprint",
        "topology_fingerprint",
        "component_order_sha256",
        "source_domain_identity",
        "reference_state_identity",
        "helmholtz_basis_identity",
    ]
    expected_provider_outputs = [
        "neutral_basis_matrix",
        "neutral_reference_log_fugacity_contractions",
        "reference_composition",
        "reference_molality_mol_per_kg",
        "reference_convergence_error",
    ]
    expected_neutral_basis = [
        [1, 0, 0, 0, 0, 0, 0, 0, 0],
        [0, 1, 0, 0, 0, 0, 0, 0, 0],
        [0, 0, 1, 0, 0, 0, 0, 0, 0],
        [0, 0, 0, 1, 1, 0, 0, 0, 0],
        [0, 0, 0, 1, 0, 1, 0, 0, 0],
        [0, 0, 0, 2, 0, 0, 1, 0, 0],
        [0, 0, 0, 1, 0, 0, 0, 0, 1],
        [0, 0, 0, 0, 1, 0, 0, 1, 0],
    ]
    expected_reaction_to_basis = [
        [0, 0, -2, -1, 0, 0, 1, 1],
        [-1, 0, -2, -1, 1, 0, 0, 1],
        [0, 0, -1, -1, -1, 1, 0, 1],
        [0, 1, -1, -1, 1, 0, 0, 0],
        [0, 1, -1, -1, 0, 0, 0, 1],
    ]
    reconstructed_reactions = [
        [
            sum(
                coefficient * basis_row[column]
                for coefficient, basis_row in zip(
                    coefficients, expected_neutral_basis, strict=True
                )
            )
            for column in range(len(EXPECTED_PROVIDER_SPECIES_ORDER))
        ]
        for coefficients in expected_reaction_to_basis
    ]
    state = payload.get("state", {})
    transform_temperature_k = float(state.get("temperature_k", 0.0))
    source_activity_scales = list(
        map(
            float,
            payload.get("source_activity_scale_log_factors_provider_order", []),
        )
    )
    expected_common_at_state = [
        _evaluate_ln_k(reaction, transform_temperature_k) + offset
        for reaction, offset in zip(
            reactions, common["source_to_common_ln_k_offsets"], strict=True
        )
    ]
    expected_scale_projection = [
        sum(
            coefficient * scale
            for coefficient, scale in zip(
                row, source_activity_scales, strict=True
            )
        )
        for row in reaction_matrix
    ]
    expected_affine_base = [
        value + scale
        for value, scale in zip(
            expected_common_at_state, expected_scale_projection, strict=True
        )
    ]
    canonical_owner = required_receipt.get("canonical_owner", {})
    expected_owner = {
        "path": SENTINEL_CONTRACT_PATH.relative_to(REPO_ROOT).as_posix(),
        "identity": "mea-homogeneous-fixed-tp-sentinel-contract-v1",
        "field": "provider_regression_input",
    }
    owner_contract = _load_json(REPO_ROOT / canonical_owner.get("path", ""))
    owner_input = owner_contract.get(canonical_owner.get("field", ""), {})
    receipt_path = REPO_ROOT / owner_input.get("receipt_path", "")
    provider_receipt = _load_json(receipt_path)
    receipt_domain = provider_receipt.get("domain", {})
    source_temperature_domain = payload.get(
        "source_correlation_temperature_domain_k"
    )
    executable_temperature_domain = payload.get(
        "installed_provider_executable_temperature_domain_k"
    )
    if (
        provider_transform.get("ready") is not True
        or provider_transform.get("identity")
        != "mea-five-reaction-provider-neutral-basis-transform-v1"
        or provider_transform.get("required_common_source_convention")
        != common["identity"]
        or provider_transform.get("blockers") != []
        or payload.get("provider_component_order")
        != list(EXPECTED_PROVIDER_SPECIES_ORDER)
        or payload.get("reaction_order") != ["R1", "R2", "R3", "R4", "R5"]
        or source_temperature_domain != temperature_intersection
        or executable_temperature_domain != EXPECTED_PROVIDER_INPUT["temperature_k"]
        or not (
            source_temperature_domain[0]
            <= transform_temperature_k
            <= source_temperature_domain[1]
        )
        or not (
            executable_temperature_domain[0]
            <= transform_temperature_k
            <= executable_temperature_domain[1]
        )
        or receipt_domain.get("temperature_k") != executable_temperature_domain
        or payload.get("source_standard_reference_pressure_pa") != 100_000.0
        or "every receipt-admitted trial pressure"
        not in payload.get("numerical_anchor_role", "")
        or payload.get("reaction_matrix_provider_order") != reaction_matrix
        or payload.get("provider_neutral_basis", {}).get("matrix")
        != expected_neutral_basis
        or payload.get("reaction_to_neutral_basis_matrix")
        != expected_reaction_to_basis
        or reconstructed_reactions != reaction_matrix
        or len(source_activity_scales) != len(EXPECTED_PROVIDER_SPECIES_ORDER)
        or any(
            abs(actual - expected) > 5.0e-15
            for actual, expected in zip(
                source_activity_scales, expected_scales, strict=True
            )
        )
        or float(state.get("pressure_pa", 0.0)) != 100_000.0
        or any(
            abs(actual - expected) > 5.0e-14
            for actual, expected in zip(
                payload.get("common_ln_k_at_state", []),
                expected_common_at_state,
                strict=True,
            )
        )
        or any(
            abs(actual - expected) > 5.0e-14
            for actual, expected in zip(
                payload.get("source_activity_scale_projection_by_reaction", []),
                expected_scale_projection,
                strict=True,
            )
        )
        or any(
            abs(actual - expected) > 5.0e-14
            for actual, expected in zip(
                payload.get("provider_affine_base_ln_k_at_state", []),
                expected_affine_base,
                strict=True,
            )
        )
        or payload.get("source_records_sha256")
        != _canonical_sha256(source_records)
        or provider_transform.get("deterministic_payload_sha256")
        != _canonical_sha256(payload)
        or required_receipt.get("temperature_unit") != "K"
        or required_receipt.get("pressure_unit") != "Pa"
        or required_receipt.get("required_immutable_identities")
        != expected_provider_identities
        or required_receipt.get("required_outputs") != expected_provider_outputs
        or canonical_owner != expected_owner
        or owner_contract.get("identity") != expected_owner["identity"]
        or owner_input.get("identity") != EXPECTED_PROVIDER_INPUT["identity"]
        or owner_input.get("bundle_path") != EXPECTED_PROVIDER_INPUT["bundle_path"]
        or owner_input.get("receipt_path") != EXPECTED_PROVIDER_INPUT["receipt_path"]
        or owner_input.get("receipt_sha256")
        != EXPECTED_PROVIDER_INPUT["receipt_sha256"]
        or owner_input.get("immutable_identities")
        != _expected_immutable_identities()
        or _sha256(receipt_path) != EXPECTED_PROVIDER_INPUT["receipt_sha256"]
        or provider_receipt.get("status") != "REGRESSION_INPUT_EXECUTABLE"
        or provider_receipt.get("scientific_acceptance") != "NOT_ESTABLISHED"
    ):
        raise ValueError("MEA Provider transformation is incomplete or inconsistent")
    return {
        "reaction_count": len(reactions),
        "reaction_rank": reaction_rank,
        "balance_rank": balance_rank,
        "temperature_intersection_k": temperature_intersection,
        "provider_executable_temperature_domain_k": executable_temperature_domain,
        "common_source_standard_state": common["identity"],
        "common_ln_k_298_15_k": common_ln_k,
        "source_conversion_ready": True,
        "provider_transform_ready": True,
        "provider_species_order": list(provider_species_order),
        "provider_transform_sha256": provider_transform[
            "deterministic_payload_sha256"
        ],
        "blockers": [],
    }


def _sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _directory_manifest_sha256(path: Path) -> str:
    file_hashes = {
        item.relative_to(path).as_posix(): _sha256(item)
        for item in sorted(path.rglob("*"))
        if item.is_file()
    }
    return _canonical_sha256(file_hashes)


def _source_row(path: Path, record_id: str) -> dict[str, str]:
    with path.open(newline="", encoding="utf-8-sig") as handle:
        matches = [row for row in csv.DictReader(handle) if row["record_id"] == record_id]
    if len(matches) != 1:
        raise ValueError(f"Expected one source row {record_id} in {path}")
    return matches[0]


def validate_sentinel_contract(
    contract: dict[str, Any], reaction_contract: dict[str, Any]
) -> dict[str, Any]:
    reaction_summary = validate_reaction_contract(reaction_contract)
    if (
        contract.get("schema_version") != 1
        or contract.get("identity")
        != "mea-homogeneous-fixed-tp-sentinel-contract-v1"
        or contract.get("status") != "source_defined_regression_input_executable"
    ):
        raise ValueError("Unexpected MEA sentinel contract identity")
    if contract.get("source_records") != EXPECTED_SENTINEL_SOURCE_RECORDS:
        raise ValueError("MEA sentinel source records have drifted")
    if contract.get("source_artifact_verification") != {
        "role": "external_provenance_metadata",
        "runtime_file_dependency": False,
        "verification_limit": (
            "PDF identities are retained from source acquisition; package "
            "validation does not locate or re-hash external PDF bytes"
        ),
    }:
        raise ValueError("MEA sentinel external source-verification limit drifted")
    if tuple(contract.get("species_order", ())) != EXPECTED_SPECIES_ORDER:
        raise ValueError("MEA sentinel species order does not match the reaction contract")
    if (
        tuple(contract.get("provider_component_order", ()))
        != EXPECTED_PROVIDER_SPECIES_ORDER
    ):
        raise ValueError("MEA sentinel Provider component order is incomplete")

    bundle = contract.get("provider_regression_input", {})
    if (
        bundle.get("identity") != EXPECTED_PROVIDER_INPUT["identity"]
        or bundle.get("bundle_path") != EXPECTED_PROVIDER_INPUT["bundle_path"]
        or bundle.get("receipt_path") != EXPECTED_PROVIDER_INPUT["receipt_path"]
        or bundle.get("receipt_sha256") != EXPECTED_PROVIDER_INPUT["receipt_sha256"]
        or bundle.get("immutable_identities") != _expected_immutable_identities()
    ):
        raise ValueError("MEA canonical Provider-input identities have drifted")
    bundle_path = REPO_ROOT / bundle.get("bundle_path", "")
    receipt_path = REPO_ROOT / bundle.get("receipt_path", "")
    receipt = _load_json(receipt_path)
    bundle_files = {
        item.relative_to(bundle_path).as_posix(): _sha256(item)
        for item in sorted(bundle_path.rglob("*"))
        if item.is_file()
    }
    receipt_bundle = receipt.get("bundle", {})
    provider = receipt.get("provider", {})
    consumer = receipt.get("public_consumer", {})
    consumer_source = REPO_ROOT / consumer.get("source_path", "")
    consumer_harness = REPO_ROOT / consumer.get("harness_path", "")
    legacy_path = REPO_ROOT / bundle.get("legacy_diagnostic_bundle", {}).get("path", "")
    if (
        bundle.get("status") != "REGRESSION_INPUT_EXECUTABLE"
        or bundle.get("purpose") != "user-provided"
        or bundle.get("blockers") != []
        or _sha256(receipt_path) != EXPECTED_PROVIDER_INPUT["receipt_sha256"]
        or receipt.get("status") != "REGRESSION_INPUT_EXECUTABLE"
        or receipt.get("scientific_acceptance") != "NOT_ESTABLISHED"
        or receipt.get("predictive_authority") is not False
        or receipt.get("catalog_persistence") is not False
        or receipt_bundle.get("path") != bundle.get("bundle_path")
        or receipt_bundle.get("bundle_id") != EXPECTED_PROVIDER_INPUT["bundle_id"]
        or receipt_bundle.get("bundle_version")
        != EXPECTED_PROVIDER_INPUT["bundle_version"]
        or receipt_bundle.get("purpose") != "user-provided"
        or receipt_bundle.get("component_ids")
        != list(EXPECTED_PROVIDER_SPECIES_ORDER)
        or receipt_bundle.get("component_order_sha256")
        != EXPECTED_PROVIDER_INPUT["component_order_sha256"]
        or receipt_bundle.get("bundle_fingerprint")
        != EXPECTED_PROVIDER_INPUT["bundle_fingerprint"]
        or receipt_bundle.get("parameter_fingerprint")
        != EXPECTED_PROVIDER_INPUT["parameter_fingerprint"]
        or receipt_bundle.get("topology_fingerprint")
        != EXPECTED_PROVIDER_INPUT["topology_fingerprint"]
        or receipt_bundle.get("file_hashes") != EXPECTED_BUNDLE_FILE_HASHES
        or bundle_files != EXPECTED_BUNDLE_FILE_HASHES
        or receipt_bundle.get("file_manifest_sha256")
        != EXPECTED_PROVIDER_INPUT["bundle_file_manifest_sha256"]
        or _directory_manifest_sha256(legacy_path)
        != "358ff080c9eae8f0375a0732dd4dbcde53d84ac731c6a56985b68263cf59a095"
        or provider.get("commit") != EXPECTED_PROVIDER_INPUT["provider_commit"]
        or provider.get("tree") != EXPECTED_PROVIDER_INPUT["provider_tree"]
        or provider.get("wheel_sha256")
        != EXPECTED_PROVIDER_INPUT["provider_wheel_sha256"]
        or provider.get("installed_header_sha256")
        != EXPECTED_PROVIDER_INPUT["provider_header_sha256"]
        or provider.get("artifact_header_sha256")
        != provider.get("installed_header_sha256")
        or provider.get("distribution_record_sha256")
        != EXPECTED_PROVIDER_INPUT["provider_distribution_record_sha256"]
        or provider.get("installed_module_sha256")
        != EXPECTED_PROVIDER_INPUT["provider_installed_module_sha256"]
        or provider.get("capability_count")
        != EXPECTED_PROVIDER_INPUT["provider_capability_count"]
        or consumer.get("source_sha256") != _sha256(consumer_source)
        or consumer.get("harness_sha256") != _sha256(consumer_harness)
        or consumer.get("expected_domain_statuses")
        != {"outside_pressure": 3, "outside_temperature": 3}
        or "--gate0-provider-wheel" not in consumer.get("run_command", "")
        or "/tmp/" in json.dumps(consumer)
        or consumer.get("provider_source_checkout_on_python_path") is not False
        or consumer.get("provider_test_module_imported") is not False
        or consumer.get("exploratory_test_helper_receipt_retained") is not False
    ):
        raise ValueError("MEA regression-input bundle or public receipt is inconsistent")

    pressure = contract.get("pressure_observable_convention", {})
    pressure_source = REPO_ROOT / pressure.get("source_manifest", "")
    pressure_states = REPO_ROOT / pressure.get("state_manifest", "")
    provider_evidence = pressure.get("provider_evidence", {})
    if (
        pressure.get("status") != "TRACER_LIQUID_FUGACITY_EQUIVALENT"
        or pressure.get("target_observation_id") != "vle_obs_0137"
        or pressure.get("observed_pco2_pa") != 574.0
        or pressure.get("fixed_total_pressure_pa") != 7326.7
        or pressure.get("reported_pressure_relation")
        != "predicted_pco2_pa = liquid_co2_fugacity_pa"
        or pressure.get("vapor_fugacity_coefficient") != 1.0
        or pressure.get("no_phase_equilibrium") is not True
        or pressure.get("blockers")
        != ["composed_homogeneous_liquid_observable_receipt_missing"]
        or pressure.get("source_manifest_sha256") != _sha256(pressure_source)
        or pressure.get("state_manifest_sha256") != _sha256(pressure_states)
        or provider_evidence
        != {
            "provider_pr": "https://github.com/ePC-SAFT/ePC-SAFT/pull/44",
            "provider_commit": EXPECTED_PROVIDER_INPUT["provider_commit"],
            "provider_tree": EXPECTED_PROVIDER_INPUT["provider_tree"],
            "provider_wheel_sha256": EXPECTED_PROVIDER_INPUT[
                "provider_wheel_sha256"
            ],
            "provider_header_sha256": EXPECTED_PROVIDER_INPUT[
                "provider_header_sha256"
            ],
            "public_consumer_receipt": EXPECTED_PROVIDER_INPUT["receipt_path"],
        }
    ):
        raise ValueError("MEA homogeneous-liquid pressure Provider evidence is inconsistent")

    states = contract.get("states", [])
    if len(states) != 1:
        raise ValueError("MEA sentinel contract must contain exactly one source-bound state")
    state = states[0]

    source_path = REPO_ROOT / state["source_file"]
    source = _source_row(source_path, state["source_record_id"])
    temperature_k = float(source["temperature_K"])
    pressure_pa = float(source["pressure_bar"]) * 100_000.0
    loading = float(source["calculated_loading"])
    mass_fraction = float(source["mea_mass_fraction"])
    reported = state.get("reported_observations", {})
    if (
        temperature_k != float(state["temperature_k"])
        or pressure_pa != float(state["pressure_pa"])
        or loading != float(state["loading_mol_co2_per_mol_mea"])
        or mass_fraction != float(state["mea_mass_fraction_unloaded"])
        or float(source["calculated_loading"]) != float(reported.get("calculated_loading"))
        or float(source["predicted_loading"]) != float(reported.get("raman_loading"))
        or float(source["mse"]) != float(reported.get("mse"))
    ):
        raise ValueError("MEA sentinel state does not reproduce its Wong source row")
    if (
        state.get("pressure_convention")
        != "published nominal total pressure for the closed-feed batch row"
        or state.get("uncertainty_status")
        != "no row-specific standard uncertainty reported"
        or reported.get("mse_role")
        != "reported squared agreement metric, not a measurement uncertainty"
    ):
        raise ValueError("MEA sentinel pressure or uncertainty convention is incomplete")

    molar_mass = contract["molar_mass_basis"]
    molar_mass_path = REPO_ROOT / molar_mass["source_file"]
    expected_molar_masses = {"CO2": 0.04401, "MEA": 0.06108, "H2O": 0.01801528}
    source_molar_masses = {
        species_id: float(_source_row(molar_mass_path, record_id)["value"])
        for species_id, record_id in {
            "CO2": "carbon-dioxide-molar-mass",
            "MEA": "monoethanolamine-molar-mass",
            "H2O": "water-molar-mass",
        }.items()
    }
    if (
        molar_mass.get("source_file")
        != reaction_contract["common_source_standard_state"][
            "water_molar_mass_source"
        ]
        or molar_mass.get("source_file_sha256")
        != reaction_contract["common_source_standard_state"][
            "water_molar_mass_source_sha256"
        ]
        or _sha256(molar_mass_path) != EXPECTED_BUNDLE_FILE_HASHES["single.csv"]
        or molar_mass.get("unit") != "kilogram / mole"
        or molar_mass.get("values") != expected_molar_masses
        or source_molar_masses != expected_molar_masses
    ):
        raise ValueError("MEA sentinel molar-mass artifact fingerprint does not match")
    values = molar_mass["values"]
    water_amount = (
        (1.0 - mass_fraction)
        / mass_fraction
        * float(values["MEA"])
        / float(values["H2O"])
    )
    expected_feed = [loading, 1.0, water_amount, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0]
    actual_feed = list(map(float, state["feed_amounts_mol"]))
    if len(actual_feed) != len(expected_feed) or any(
        abs(actual - expected) > 2.0e-15
        for actual, expected in zip(actual_feed, expected_feed, strict=True)
    ):
        raise ValueError("MEA sentinel feed amounts do not match the source-bound mass basis")

    charges = [int(row["charge"]) for row in reaction_contract["species"]]
    charge = sum(
        amount * charge_number
        for amount, charge_number in zip(actual_feed, charges, strict=True)
    )
    if charge != float(state["initial_charge_equivalents_mol"]):
        raise ValueError("MEA sentinel feed is not exactly electroneutral")
    lower, upper = reaction_summary["temperature_intersection_k"]
    reaction_domain_passed = lower <= temperature_k <= upper
    if reaction_domain_passed is not state.get("reaction_domain_passed"):
        raise ValueError("MEA sentinel reaction-domain status is inconsistent")
    provider_lower, provider_upper = reaction_summary[
        "provider_executable_temperature_domain_k"
    ]
    if not (
        provider_lower <= temperature_k <= provider_upper
        and EXPECTED_PROVIDER_INPUT["pressure_pa"][0]
        <= pressure_pa
        <= EXPECTED_PROVIDER_INPUT["pressure_pa"][1]
    ):
        raise ValueError("MEA sentinel lies outside the installed Provider domain")

    oxazolidone = state["oxazolidone_rule"]
    exclusion_passed = loading < float(oxazolidone["excluded_when_loading_below"])
    if exclusion_passed is not oxazolidone.get("passed"):
        raise ValueError("MEA sentinel oxazolidone exclusion status is inconsistent")
    if state.get("observation_roles") != {
        "calculated_loading_0.150": "direct_closed_feed_input_from_gas_pressure_drop",
        "raman_loading_0.144": "calibration_derived_context_only",
        "species_concentrations": "not_available_for_this_row_and_not_predictive_acceptance",
        "equilibrium_capacity": "not_claimed",
    }:
        raise ValueError("MEA sentinel observation roles are incomplete")
    blockers = state.get("blockers")
    if (
        "equilibrium_ready" in state
        or state.get("source_input_ready") is not True
        or blockers != []
        or state.get("readiness_scope")
        != (
            "source-complete fixed-T,P input payload only; Equilibrium solve, "
            "sensitivity, and predictive acceptance are not established"
        )
    ):
        raise ValueError("MEA sentinel executable-input scope is inconsistent")

    return {
        "state_count": 1,
        "temperature_k": temperature_k,
        "pressure_pa": pressure_pa,
        "feed_amounts_mol": actual_feed,
        "initial_charge_equivalents_mol": charge,
        "reaction_domain_passed": reaction_domain_passed,
        "oxazolidone_exclusion_passed": exclusion_passed,
        "provider_regression_input_ready": True,
        "source_input_ready": True,
        "equilibrium_solver_ready": False,
        "equilibrium_sensitivity_ready": False,
        "blockers": blockers,
        "pressure_observable_status": pressure["status"],
        "pressure_no_phase_equilibrium": pressure["no_phase_equilibrium"],
        "pressure_observable_blockers": pressure["blockers"],
    }
