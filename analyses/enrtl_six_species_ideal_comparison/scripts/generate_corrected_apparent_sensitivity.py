from __future__ import annotations

from pathlib import Path

import pandas as pd


REPO_ROOT = Path(__file__).resolve().parents[3]
ANALYSIS_DIR = Path(__file__).resolve().parents[1]
RESULTS_DIR = ANALYSIS_DIR / "results"
MAP_PATH = REPO_ROOT / "data/reference/MEA/manifests/ionic_parameter_observable_map.csv"
PROJECTION_PATH = RESULTS_DIR / "corrected_apparent_projection_diagnostics.csv"


def _disposition(identity: str) -> tuple[str, str]:
    if identity.endswith("::m"):
        return "freeze_structural_convention", "not separately identifiable from sigma and epsilon"
    if identity.endswith("::d_born"):
        return "freeze_not_admitted_to_fit", "no independent dielectric/activity target in this package"
    if identity == "MEAH+::sigma" or identity == "MEACOO-::sigma":
        return "do_not_fit_pressure_only", "candidate only for explicit-species density/speciation with regularization"
    if identity.endswith("::epsilon_over_k") or identity.endswith("::k_ij"):
        return "freeze_initially", "requires explicit-species Jacobian/profile evidence"
    if identity == "MEA_reaction_constants":
        return "freeze_source_bound", "reaction allocation is invisible to corrected neutral apparent pressure"
    return "freeze", "not a pressure-only species-set discriminator"


def main() -> int:
    mapping = pd.read_csv(MAP_PATH)
    projection = pd.read_csv(PROJECTION_PATH)
    max_delta = float(projection["max_abs_projection_delta"].max())
    rows = []
    for record in mapping.to_dict("records"):
        identity = str(record["parameter_identity"])
        if identity in {"carboxylate_analog_anions::segment_terms", "all_other_component_and_binary_parameters"}:
            continue
        action, followup = _disposition(identity)
        rows.append(
            {
                **{key: record[key] for key in ("parameter_identity", "current_value", "current_unit", "initial_disposition", "observable_family", "expected_sensitivity", "promotion_status")},
                "max_abs_corrected_projection_delta": max_delta,
                "corrected_apparent_pressure_sensitivity": "structural_zero",
                "recommended_pressure_fit_disposition": action,
                "explicit_species_followup": followup,
                "screen_status": "screened_not_uq_distribution",
            }
        )
    result = pd.DataFrame(rows)
    result.to_csv(RESULTS_DIR / "corrected_apparent_parameter_sensitivity_screen.csv", index=False, lineterminator="\n")
    pd.DataFrame([
        {"artifact": "corrected_apparent_parameter_sensitivity_screen.csv", "role": "pressure-only structural sensitivity screen", "source": "ionic_parameter_observable_map.csv"},
        {"artifact": "corrected_apparent_projection_diagnostics.csv", "role": "projection equality evidence", "source": "state_species_results.csv"},
    ]).to_csv(RESULTS_DIR / "corrected_apparent_sensitivity_manifest.csv", index=False, lineterminator="\n")
    (RESULTS_DIR / "corrected_apparent_sensitivity_summary.md").write_text(
        "# Corrected apparent-pressure sensitivity screen\n\n"
        "This is a structural sensitivity screen, not a probabilistic UQ distribution. "
        "At fixed feed and loading, reaction and internal ionic parameters can redistribute true species "
        "but cannot change the conserved carbon, amine, and water totals used by the corrected neutral apparent projection.\n\n"
        f"maximum six/nine projected-composition difference: {max_delta:.6e}\n"
        f"parameters screened: {len(result)}\n"
        "For the corrected neutral pressure observable, all screened reactive/ionic parameters are therefore "
        "structurally unidentifiable. The explicit-species follow-up column records which terms may still matter "
        "for nonideal density, fugacity, or speciation and must not be dropped from a nine-species ePC-SAFT model "
        "without a separate current-packet sensitivity/UQ run.\n",
        encoding="utf-8",
    )
    print(f"Generated corrected apparent sensitivity screen under {RESULTS_DIR}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
