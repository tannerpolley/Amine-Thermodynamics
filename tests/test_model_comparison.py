from __future__ import annotations

from pathlib import Path

import pandas as pd
import pytest

from MEA.common.model_comparison import build_controlled_comparison


ROOT = Path(__file__).resolve().parents[1]
CONTROLLED_RESULTS = (
    ROOT
    / "analyses/phase2/activity_epcsaft/results/controlled_comparison"
)


def _canonical_rows() -> pd.DataFrame:
    return pd.DataFrame(
        [
            {
                "row_id": "vle_0001",
                "source_key": "Jou1995",
                "temperature": 40.0,
                "MEA_weight_fraction": 0.3,
                "CO2_loading": 0.20,
                "CO2_pressure": 1.0,
            },
            {
                "row_id": "vle_0002",
                "source_key": "Jou1995",
                "temperature": 60.0,
                "MEA_weight_fraction": 0.3,
                "CO2_loading": 0.30,
                "CO2_pressure": 2.0,
            },
            {
                "row_id": "vle_0003",
                "source_key": "Aronu2011",
                "temperature": 80.0,
                "MEA_weight_fraction": 0.3,
                "CO2_loading": 0.40,
                "CO2_pressure": 3.0,
            },
        ]
    )


def _phase1_rows() -> pd.DataFrame:
    return pd.DataFrame(
        [
            {
                "model_family": "legacy_pcsaft_smith_missen",
                "temperature_C": 40.0,
                "MEA_weight_fraction": 0.3,
                "CO2_loading": 0.20,
                "observed_CO2_pressure_kPa": 1.0,
                "predicted_CO2_pressure_kPa": 0.5,
                "log10_pred_over_obs": -0.301029995664,
            },
            {
                "model_family": "legacy_pcsaft_smith_missen",
                "temperature_C": 60.0,
                "MEA_weight_fraction": 0.3,
                "CO2_loading": 0.30,
                "observed_CO2_pressure_kPa": 2.0,
                "predicted_CO2_pressure_kPa": 4.0,
                "log10_pred_over_obs": 0.301029995664,
            },
            {
                "model_family": "neutral_epcsaft_parity",
                "temperature_C": 40.0,
                "MEA_weight_fraction": 0.3,
                "CO2_loading": 0.20,
                "observed_CO2_pressure_kPa": 1.0,
                "predicted_CO2_pressure_kPa": 0.75,
                "log10_pred_over_obs": -0.124938736608,
            },
        ]
    )


def _phase2_rows() -> pd.DataFrame:
    return pd.DataFrame(
        [
            {
                "row_id": "vle_0001",
                "source": "Jou1995",
                "temperature_C": 40.0,
                "MEA_weight_fraction": 0.3,
                "CO2_loading": 0.20,
                "observed_CO2_pressure_kPa": 1.0,
                "model_CO2_pressure_kPa": 0.8,
                "log10_model_over_data": -0.096910013008,
                "solver_success": True,
                "message": "converged",
            },
            {
                "row_id": "vle_0002",
                "source": "Jou1995",
                "temperature_C": 60.0,
                "MEA_weight_fraction": 0.3,
                "CO2_loading": 0.30,
                "observed_CO2_pressure_kPa": 2.0,
                "model_CO2_pressure_kPa": 3.0,
                "log10_model_over_data": 0.176091259056,
                "solver_success": False,
                "message": "residual gate failed",
            },
            {
                "row_id": "vle_0003",
                "source": "Aronu2011",
                "temperature_C": 80.0,
                "MEA_weight_fraction": 0.3,
                "CO2_loading": 0.40,
                "observed_CO2_pressure_kPa": 3.0,
                "model_CO2_pressure_kPa": 3.3,
                "log10_model_over_data": 0.041392685158,
                "solver_success": True,
                "message": "converged",
            },
        ]
    )


def _role_rows(count: int = 15) -> pd.DataFrame:
    return pd.DataFrame(
        [
            {
                "row_id": f"cheq_{index:04d}",
                "source": "Jakobsen",
                "species": "HCO3-",
                "target_role": "direct_zero",
                "validation_use": "absolute_upper_bound",
            }
            for index in range(count)
        ]
    )


def test_build_controlled_comparison_uses_common_rows_and_exposes_rejections() -> None:
    bundle = build_controlled_comparison(
        _canonical_rows(), _phase1_rows(), _phase2_rows(), _role_rows()
    )

    assert bundle.paired_rows["row_id"].tolist() == ["vle_0001", "vle_0002"]
    assert bundle.paired_rows["comparison_eligible"].tolist() == [True, False]
    assert bundle.paired_rows["phase2_status"].tolist() == ["accepted", "rejected"]
    assert bundle.paired_rows.loc[1, "rejection_reason"] == "phase2: residual gate failed"

    paired_overall = bundle.metrics.query(
        "scope == 'paired' and group_type == 'overall'"
    ).set_index("model")
    assert paired_overall.loc["ideal_baseline", "attempted_count"] == 2
    assert paired_overall.loc["ideal_baseline", "accepted_count"] == 1
    assert paired_overall.loc["activity_model", "accepted_count"] == 1
    assert paired_overall.loc["ideal_baseline", "median_abs_log10_error"] == pytest.approx(
        0.301029995664
    )
    assert paired_overall.loc["activity_model", "median_abs_log10_error"] == pytest.approx(
        0.096910013008
    )

    full_activity = bundle.metrics.query(
        "scope == 'full_context' and model == 'activity_model' and group_type == 'overall'"
    ).iloc[0]
    assert full_activity["attempted_count"] == 3
    assert full_activity["accepted_count"] == 2
    assert full_activity["failure_count"] == 1


def test_build_controlled_comparison_rejects_ambiguous_canonical_identity() -> None:
    canonical = pd.concat([_canonical_rows(), _canonical_rows().iloc[[0]].assign(row_id="vle_9999")])

    with pytest.raises(ValueError, match="canonical comparison identity"):
        build_controlled_comparison(canonical, _phase1_rows(), _phase2_rows(), _role_rows())


def test_build_controlled_comparison_rejects_duplicate_phase2_row_id() -> None:
    phase2 = pd.concat([_phase2_rows(), _phase2_rows().iloc[[0]]], ignore_index=True)

    with pytest.raises(ValueError, match="duplicate Phase 2 row_id"):
        build_controlled_comparison(_canonical_rows(), _phase1_rows(), phase2, _role_rows())


def test_build_controlled_comparison_rejects_duplicate_phase1_identity() -> None:
    phase1 = pd.concat([_phase1_rows(), _phase1_rows().iloc[[0]]], ignore_index=True)

    with pytest.raises(ValueError, match="duplicate Phase 1 comparison identity"):
        build_controlled_comparison(_canonical_rows(), phase1, _phase2_rows(), _role_rows())


def test_build_controlled_comparison_rejects_phase2_unit_or_value_mismatch() -> None:
    phase2 = _phase2_rows().copy()
    phase2.loc[phase2["row_id"] == "vle_0001", "observed_CO2_pressure_kPa"] = 1000.0

    with pytest.raises(ValueError, match="Phase 2 values do not match canonical records"):
        build_controlled_comparison(_canonical_rows(), _phase1_rows(), phase2, _role_rows())


def test_build_controlled_comparison_rejects_unmatched_phase1_record() -> None:
    phase1 = _phase1_rows().copy()
    phase1.loc[phase1["model_family"] == "legacy_pcsaft_smith_missen", "CO2_loading"] += 0.001

    with pytest.raises(ValueError, match="unmatched Phase 1 records"):
        build_controlled_comparison(_canonical_rows(), phase1, _phase2_rows(), _role_rows())


def test_repository_comparison_recovers_31_jou_rows_and_15_zero_targets() -> None:
    bundle = build_controlled_comparison(
        pd.read_csv(ROOT / "data/reference/MEA/VLE/Combined_VLE.csv"),
        pd.read_csv(
            ROOT
            / "analyses/phase1/smith_missen_baseline/results/phase1_pressure_results.csv"
        ),
        pd.read_csv(
            ROOT / "analyses/phase2/activity_epcsaft/results/phase2_pressure_results.csv"
        ),
        pd.read_csv(
            ROOT
            / "analyses/phase2/activity_epcsaft/results/phase2_speciation_target_roles.csv"
        ),
    )

    assert len(bundle.paired_rows) == 31
    assert bundle.paired_rows["row_id"].is_unique
    assert set(bundle.paired_rows["source"]) == {"Jou1995"}
    assert bundle.paired_rows["comparison_eligible"].all()
    assert bundle.summary["reported_zero_target_count"] == 15
    assert bundle.summary["paired_row_count"] == 31
    assert bundle.summary["paired_eligible_count"] == 31
    assert bundle.uncertainty_coverage["uncertainty_available_count"].sum() == 0


def test_generated_controlled_comparison_matches_recomputed_metrics() -> None:
    expected_files = {
        "paired_pressure_rows.csv",
        "metrics.csv",
        "metrics.json",
        "uncertainty_coverage.csv",
        "speciation_role_counts.csv",
    }
    assert {path.name for path in CONTROLLED_RESULTS.glob("*")} == expected_files

    regenerated = build_controlled_comparison(
        pd.read_csv(ROOT / "data/reference/MEA/VLE/Combined_VLE.csv"),
        pd.read_csv(
            ROOT
            / "analyses/phase1/smith_missen_baseline/results/phase1_pressure_results.csv"
        ),
        pd.read_csv(
            ROOT / "analyses/phase2/activity_epcsaft/results/phase2_pressure_results.csv"
        ),
        pd.read_csv(
            ROOT
            / "analyses/phase2/activity_epcsaft/results/phase2_speciation_target_roles.csv"
        ),
    )
    persisted_pairs = pd.read_csv(CONTROLLED_RESULTS / "paired_pressure_rows.csv")
    persisted_pairs["rejection_reason"] = persisted_pairs["rejection_reason"].fillna("")
    pd.testing.assert_frame_equal(
        persisted_pairs,
        regenerated.paired_rows,
        check_dtype=False,
    )
    pd.testing.assert_frame_equal(
        pd.read_csv(CONTROLLED_RESULTS / "metrics.csv"),
        regenerated.metrics,
        check_dtype=False,
    )
