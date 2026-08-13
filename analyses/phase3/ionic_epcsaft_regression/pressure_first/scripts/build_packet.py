from __future__ import annotations

import hashlib
import json
from pathlib import Path

import pandas as pd


ROOT = Path(__file__).resolve().parents[5]
ANALYSIS = ROOT / "analyses/phase3/ionic_epcsaft_regression/pressure_first"
MANIFESTS = ROOT / "data/reference/MEA/manifests"
OUTPUT = ANALYSIS / "results"


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _canonical_sha256(value: object) -> str:
    return hashlib.sha256(
        json.dumps(value, allow_nan=False, separators=(",", ":"), sort_keys=True).encode()
    ).hexdigest()


def _analysis_role(row: pd.Series) -> str:
    if row["domain_role"] != "current_R4_R5_source_domain":
        return "non_scoring_domain_challenge"
    campaign = row["campaign_block_id"]
    if campaign in {
        "pco2|Hilliard2008|w=0.17|T=40",
        "pco2|Hilliard2008|w=0.3|T=40",
    }:
        return "training"
    if campaign == "pco2|Hilliard2008|w=0.4|T=40":
        return "model_selection"
    if campaign == "pco2|Jou1995|w=0.3|T=40":
        return "reserved"
    raise ValueError(f"unassigned in-domain campaign {campaign}")


def _measurement_equation(role: str) -> str:
    if role == "calibration_derived_partial_pressure":
        return "predicted_pco2_pa = y_CO2 * P; observed value derives from calibrated gas composition and measured total pressure"
    if role == "total_pressure_derived":
        return "predicted_pco2_pa = y_CO2 * P; observed value derives from source Eq. (1): total pressure corrected for N2 and calculated solvent vapor pressures"
    raise ValueError(f"unsupported pressure measurement role {role}")


def main() -> None:
    prereg_path = ANALYSIS / "config/preregistration.json"
    cross_path = MANIFESTS / "reactive_vle_cross_validation.csv"
    metrology_path = MANIFESTS / "pco2_metrology_manifest.csv"
    prereg = json.loads(prereg_path.read_text())
    cross = pd.read_csv(cross_path, dtype=str).fillna("")
    cross = cross.loc[cross["observable_family"] == "pco2"].copy()
    metrology = pd.read_csv(metrology_path, dtype=str).fillna("")
    packet = cross.merge(
        metrology,
        on="observation_id",
        how="left",
        suffixes=("", "_metrology"),
        validate="one_to_one",
    )
    if len(packet) != 121 or packet["observation_id"].nunique() != 121:
        raise RuntimeError("pressure packet must contain exactly 121 unique observations")
    checks = (
        packet["measurement_role"] == packet["measurement_origin"],
        packet["observed_value"].astype(float)
        == packet["observed_pco2_kpa"].astype(float),
        packet["state_pressure_pa"].astype(float)
        == packet["state_pressure_pa_metrology"].astype(float),
    )
    if not all(check.all() for check in checks):
        raise RuntimeError("cross-validation and pressure-metrology rows disagree")
    for source_file, rows in packet.groupby("source_file"):
        actual = _sha256(ROOT / source_file)
        if set(rows["source_file_sha256"]) != {actual}:
            raise RuntimeError(f"source-file hash mismatch for {source_file}")

    packet["canonical_row_identity"] = (
        packet["source_file_sha256"] + ":row:" + packet["source_row_identity"]
    )
    packet["measurement_equation"] = packet["measurement_role"].map(
        _measurement_equation
    )
    packet["observed_pco2_pa"] = packet["observed_value"].astype(float) * 1000.0
    packet["analysis_role"] = packet.apply(_analysis_role, axis=1)
    scales = prereg["residual_policy"]["provisional_scales_log10"]
    packet["residual_scale_log10"] = packet["measurement_role"].map(scales)
    packet["residual_scale_status"] = (
        "preregistered_provisional_diagnostic_not_source_uncertainty"
    )
    packet["covariance_or_leakage_group"] = packet["campaign_block_id"]
    packet["target_eligibility"] = packet["analysis_role"].map(
        lambda role: "diagnostic_scoring" if role in {"training", "model_selection"} else "withheld"
    )
    packet["promotion_eligibility"] = "no"
    packet["promotion_blocker"] = (
        "provisional_residual_scale;unqualified_neutral_parameters;coupled_reactive_bubble_not_evaluable"
    )
    columns = [
        "observation_id",
        "canonical_row_identity",
        "source_key",
        "source_file",
        "source_file_sha256",
        "source_row_identity",
        "source_locator",
        "temperature_K",
        "temperature_reported_C",
        "mea_mass_fraction",
        "co2_loading_mol_per_mol_mea",
        "measurement_role",
        "measurement_identity",
        "measurement_equation",
        "observed_value",
        "reported_basis",
        "observed_pco2_pa",
        "state_pressure_pa",
        "pressure_specification",
        "uncertainty_status",
        "residual_scale_log10",
        "residual_scale_status",
        "covariance_status",
        "covariance_or_leakage_group",
        "campaign_block_id",
        "cross_validation_fold",
        "domain_role",
        "analysis_role",
        "target_eligibility",
        "promotion_eligibility",
        "promotion_blocker",
    ]
    OUTPUT.mkdir(parents=True, exist_ok=True)
    packet_path = OUTPUT / "pressure_candidate_packet.csv"
    packet[columns].to_csv(packet_path, index=False, lineterminator="\n")
    split = packet.groupby(["analysis_role", "source_key"]).size().reset_index(name="rows")
    split_path = OUTPUT / "pressure_split_summary.csv"
    split.to_csv(split_path, index=False, lineterminator="\n")
    receipt = {
        "schema_version": 1,
        "identity": "mea-pressure-first-packet-receipt-v1",
        "preregistration_sha256": _sha256(prereg_path),
        "input_hashes": {
            str(cross_path.relative_to(ROOT)): _sha256(cross_path),
            str(metrology_path.relative_to(ROOT)): _sha256(metrology_path),
        },
        "source_hashes": {
            source_file: source_hash
            for source_file, source_hash in packet[
                ["source_file", "source_file_sha256"]
            ].drop_duplicates().itertuples(index=False, name=None)
        },
        "packet": {
            "path": str(packet_path.relative_to(ROOT)),
            "sha256": _sha256(packet_path),
            "rows": len(packet),
            "unique_rows": packet["canonical_row_identity"].nunique(),
        },
        "counts": {
            "by_role": packet["analysis_role"].value_counts().sort_index().to_dict(),
            "by_source": packet["source_key"].value_counts().sort_index().to_dict(),
            "by_measurement_role": packet["measurement_role"].value_counts().sort_index().to_dict(),
        },
        "reserved_policy": "reserved observed values are not consumed by fitting or model selection",
        "claim_boundary": "diagnostic packet with provisional weights; no parameter-promotion eligibility",
    }
    receipt["receipt_sha256"] = _canonical_sha256(receipt)
    receipt_path = OUTPUT / "pressure_packet_receipt.json"
    receipt_path.write_text(json.dumps(receipt, indent=2, sort_keys=True) + "\n")
    print(packet_path.relative_to(ROOT), receipt["packet"]["sha256"])
    print(receipt_path.relative_to(ROOT), receipt["receipt_sha256"])


if __name__ == "__main__":
    main()
