from __future__ import annotations

import csv
import json
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SPECIES = ("CO2", "MEA", "H2O", "MEAH+", "MEACOO-", "HCO3-", "CO3^2-", "H3O+", "OH-")
PINNED_EPCSAFT_COMMIT = "9f51afd0f9c11a6497ddca05c8b2dd0ea0ffa785"
OLD_ISSUE_BLOCKER = "issue " + "#115"
OLD_FAILED_VALIDATION_LABEL = "failed" + "-validation"
OLD_SCAFFOLD_BLOCKER = "scaffold_ready_" + "blocked"
OLD_CANDIDATE_STATUS = "source_verified_but_" + "solver_blocked"


def _rows(path: Path) -> list[dict[str, str]]:
    with path.open(newline="", encoding="utf-8") as handle:
        return list(csv.DictReader(handle))


class Phase2ActivityNativeSolverTests(unittest.TestCase):
    def test_reaction_manifest_promotes_austgen_activity_constants(self) -> None:
        path = ROOT / "data" / "reference" / "MEA" / "manifests" / "phase2_reaction_constant_manifest.csv"
        rows = _rows(path)
        self.assertEqual([row["reaction_id"] for row in rows], ["R1", "R2", "R3", "R4", "R5"])
        for row in rows:
            self.assertEqual(row["activity_basis_needed"], "thermodynamic_activity")
            self.assertEqual(row["conversion_status"], "source_verified")
            self.assertEqual(row["used_in_phase2"], "used_in_native_solver_residual_gated")
            self.assertEqual(row["regularization_role_in_phase3"], "fixed_input_candidate_for_phase3_regularization")
            self.assertIn("Nasrifar2010_Table1", row["source"])
            self.assertIn("residual-gated", row["notes"])
            self.assertNotIn(OLD_ISSUE_BLOCKER, row["notes"])

    def test_reaction_constant_source_values_are_verified_against_repo_sources(self) -> None:
        path = ROOT / "data" / "reference" / "MEA" / "manifests" / "phase2_reaction_constant_source_verification.csv"
        rows = _rows(path)
        self.assertEqual([row["reaction_id"] for row in rows], ["R1", "R2", "R3", "R4", "R5"])
        by_id = {row["reaction_id"]: row for row in rows}
        self.assertAlmostEqual(float(by_id["R1"]["source_value_C"]), -22.4773, places=4)
        self.assertAlmostEqual(float(by_id["R2"]["source_value_A"]), 231.456, places=3)
        self.assertAlmostEqual(float(by_id["R4"]["source_value_A"]), 2.8898, places=4)
        self.assertAlmostEqual(float(by_id["R5"]["source_value_D"]), -0.007484, places=6)
        for row in rows:
            self.assertEqual(row["source_verified"], "yes")
            self.assertEqual(row["external_source_path_used"], "no")
            self.assertEqual(row["source_status"], "source_verified")
            self.assertEqual(row["model_use_status"], "used_in_native_solver_residual_gated")
            self.assertIn("phase2_residual_acceptance_audit.csv", row["gate_notes"])
            self.assertTrue((ROOT / row["source_file_repo_relative"]).exists())

    def test_activity_constant_candidates_are_native_solver_inputs(self) -> None:
        path = ROOT / "data" / "reference" / "MEA" / "manifests" / "phase2_activity_constant_candidates.csv"
        rows = _rows(path)
        self.assertEqual([row["reaction_id"] for row in rows], ["R1", "R2", "R3", "R4", "R5"])
        status_by_reaction = {row["reaction_id"]: row["phase2_status"] for row in rows}
        self.assertEqual(set(status_by_reaction.values()), {"source_verified_native_solver_input"})
        source_by_reaction = {row["reaction_id"]: row["candidate_source"] for row in rows}
        self.assertEqual(source_by_reaction["R4"], "Nasrifar2010_Table1_via_Austgen1991")
        self.assertEqual(source_by_reaction["R5"], "Nasrifar2010_Table1_via_Austgen1991")
        self.assertEqual(float([row for row in rows if row["reaction_id"] == "R1"][0]["c3"]), -22.4773)
        for row in rows:
            self.assertEqual(row["validation_role"], "fixed_input_residual_gated")
            self.assertIn("validation outcomes do not revise model-run status", row["next_action"])
            self.assertNotIn(OLD_ISSUE_BLOCKER, row["next_action"])
            self.assertNotIn("C:/Users", row["source_files"])

    def test_phase2_parameter_artifact_has_true_species_basis(self) -> None:
        pure = ROOT / "data" / "reference" / "epcsaft_datasets" / "MEA_CO2_H2O_phase2" / "pure" / "any_solvent.csv"
        rows = _rows(pure)
        self.assertEqual([row["component"] for row in rows], list(SPECIES))

    def test_phase2_design_names_required_fields(self) -> None:
        text = (ROOT / "docs" / "roadmaps" / "phase2_activity_speciation_design.md").read_text(encoding="utf-8")
        for phrase in (
            "Species",
            "Vapor/liquid split",
            "Reaction network",
            "Balances",
            "Activity convention",
            "Reference states",
            "Parameter set",
            "Dielectric option",
            "Born option",
            "Solver route",
            "Package dependency status",
        ):
            self.assertIn(phrase, text)

    def test_analysis_declares_single_parameter_artifact(self) -> None:
        text = (ROOT / "analyses" / "phase2_activity_epcsaft" / "analysis.yaml").read_text(encoding="utf-8")
        self.assertIn("data/reference/epcsaft_datasets/MEA_CO2_H2O_phase2", text)
        self.assertIn("generate_data.py", text)

    def test_required_output_status_records_native_model_success_outputs(self) -> None:
        path = ROOT / "analyses" / "phase2_activity_epcsaft" / "results" / "phase2_required_output_status.csv"
        rows = {row["artifact"]: row for row in _rows(path)}
        self.assertEqual(rows["phase2_activity_speciation_problem.json"]["status"], "problem_definition_generated")
        self.assertEqual(rows["phase2_equilibrium_results.csv"]["status"], "model_ran_success")
        self.assertEqual(rows["phase2_pressure_speciation_parity.csv"]["status"], "model_ran_success")
        self.assertEqual(rows["phase2_pressure_metrics.csv"]["status"], "model_ran_success")
        self.assertEqual(rows["phase2_speciation_metrics.csv"]["status"], "model_ran_success")
        self.assertEqual(rows["phase2_solver_diagnostics.csv"]["status"], "generated")
        self.assertEqual(rows["phase2_residual_acceptance_audit.csv"]["status"], "model_ran_success")
        self.assertEqual(rows["phase2_speciation_activity_curves.csv"]["status"], "generated_from_native_epcsaft_activity_solver")
        self.assertEqual(rows["phase2_speciation_target_roles.csv"]["status"], "generated")
        self.assertEqual(rows["phase2_speciation_activity_plot.png"]["status"], "render_input_ready")
        self.assertEqual(rows["phase2_density_viscosity_validation.csv"]["status"], "optional_validation_inventory_ready")
        self.assertNotIn(OLD_FAILED_VALIDATION_LABEL, "\n".join(row["next_action"] for row in rows.values()))
        self.assertTrue((ROOT / "analyses" / "phase2_activity_epcsaft" / "results" / "phase2_equilibrium_results.csv").exists())

    def test_generated_problem_definition_records_native_solver_contract(self) -> None:
        path = ROOT / "analyses" / "phase2_activity_epcsaft" / "results" / "phase2_activity_speciation_problem.json"
        payload = json.loads(path.read_text(encoding="utf-8"))
        self.assertEqual(payload["status"], "problem_definition_generated")
        self.assertIn("material_balances", payload)
        self.assertIn("constraints", payload)
        self.assertNotIn("balances", payload)
        self.assertIn("total_amine", payload["material_balances"])
        self.assertIn("electroneutrality", payload["constraints"])
        activity_convention = payload["activity_convention"]
        self.assertEqual(
            activity_convention["candidate_manifest"],
            "data/reference/MEA/manifests/phase2_activity_constant_candidates.csv",
        )
        self.assertEqual(activity_convention["candidate_status_counts"]["source_verified_native_solver_input"], 5)
        self.assertNotIn(OLD_CANDIDATE_STATUS, activity_convention["candidate_status_counts"])
        self.assertEqual(activity_convention["current_manifest_conversion_status"], ["source_verified"])
        self.assertEqual(activity_convention["standard_state_used"], "mole_fraction_activity")
        self.assertEqual(
            activity_convention["solve_policy"],
            "run_only_with_pinned_epcsaft_native_activity_solver_and_generated_residual_gates",
        )
        self.assertEqual(payload["epcsaft_dependency"]["commit_id"], PINNED_EPCSAFT_COMMIT)

    def test_solver_report_separates_model_run_success_from_residual_claims(self) -> None:
        path = ROOT / "analyses" / "phase2_activity_epcsaft" / "results" / "phase2_solver_claim_boundary_report.md"
        text = path.read_text(encoding="utf-8")
        self.assertIn("phase2_status: model_ran_success", text)
        self.assertIn("solver_status: native_epcsaft_activity_solver_ran", text)
        self.assertIn("Phase 2 activity-evaluation claims are controlled by `phase2_residual_acceptance_audit.csv`.", text)
        self.assertIn("phase2_solver_diagnostics.csv", text)
        self.assertIn("phase2_residual_acceptance_audit.csv", text)
        self.assertIn("phase2_validation_status:", text)
        self.assertNotIn(OLD_SCAFFOLD_BLOCKER, text)
        self.assertNotIn("model-ran/" + OLD_FAILED_VALIDATION_LABEL, text)
        self.assertNotIn(OLD_ISSUE_BLOCKER, text)

    def test_phase2_emits_native_solver_curves_not_scaffold_curves(self) -> None:
        output = ROOT / "analyses" / "phase2_activity_epcsaft" / "figures" / "speciation" / "output"
        results = ROOT / "analyses" / "phase2_activity_epcsaft" / "results"
        for name in (
            "phase2_speciation_reference_points.csv",
            "phase2_speciation_activity_curves.csv",
            "phase2_speciation_40C.png",
            "phase2_speciation_40C.svg",
            "phase2_speciation_40C.mpl.yaml",
        ):
            self.assertTrue((output / name).exists(), name)
        self.assertTrue((results / "phase2_speciation_activity_curves.csv").exists())
        self.assertTrue((results / "phase2_speciation_target_roles.csv").exists())
        forbidden = [
            *output.glob("phase2_speciation_scaffold*"),
            *results.glob("phase2_speciation_scaffold*"),
        ]
        self.assertEqual(forbidden, [])
        curve_rows = _rows(results / "phase2_speciation_activity_curves.csv")
        self.assertGreater(len(curve_rows), 5000)
        self.assertEqual({row["curve_role"] for row in curve_rows}, {"epcsaft_activity_equilibrium_curve"})
        self.assertTrue(all(row["solver_success"].lower() == "true" for row in curve_rows))
        forty_mea_total = [
            row
            for row in curve_rows
            if float(row["temperature_C"]) == 40.0 and row["species"] == "MEA + MEAH+"
        ]
        self.assertGreaterEqual(len(forty_mea_total), 150)
        loadings = [float(row["CO2_loading"]) for row in forty_mea_total]
        self.assertLessEqual(min(loadings), 0.005)
        self.assertGreaterEqual(max(loadings), 0.799)

    def test_reference_points_only_use_direct_positive_targets(self) -> None:
        results = ROOT / "analyses" / "phase2_activity_epcsaft" / "results"
        points = _rows(results / "phase2_speciation_reference_points.csv")
        roles = _rows(results / "phase2_speciation_target_roles.csv")
        self.assertGreater(len(points), 0)
        self.assertTrue(
            all(row["target_role"] in {"direct_positive", "aggregate_direct_positive"} for row in points)
        )
        hco3_zero_roles = [
            row
            for row in roles
            if row["species"] == "HCO3-" and row["target_role"] == "direct_zero"
        ]
        self.assertGreater(len(hco3_zero_roles), 0)
        self.assertTrue(all(row["validation_use"] == "absolute_upper_bound" for row in hco3_zero_roles))

    def test_residual_audit_claim_gates_do_not_change_model_run_status(self) -> None:
        audit = _rows(ROOT / "analyses" / "phase2_activity_epcsaft" / "results" / "phase2_residual_acceptance_audit.csv")
        by_metric = {(row["species_or_property"], row["metric"]): row for row in audit}
        self.assertEqual(by_metric[("curve_grid_success_fraction", "success_fraction")]["passes"].lower(), "true")
        self.assertEqual(by_metric[("HCO3-", "direct_positive_median_abs_log10_error")]["passes"].lower(), "true")
        self.assertEqual(by_metric[("HCO3-", "reported_zero_max_model_mole_fraction")]["passes"].lower(), "true")
        self.assertEqual(by_metric[("CO2_pressure", "median_abs_log10_error")]["passes"].lower(), "true")
        status_rows = {
            row["artifact"]: row
            for row in _rows(ROOT / "analyses" / "phase2_activity_epcsaft" / "results" / "phase2_required_output_status.csv")
        }
        self.assertEqual(status_rows["phase2_residual_acceptance_audit.csv"]["status"], "model_ran_success")


if __name__ == "__main__":
    unittest.main()
