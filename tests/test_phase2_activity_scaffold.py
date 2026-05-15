from __future__ import annotations

import csv
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SPECIES = ("CO2", "MEA", "H2O", "MEAH+", "MEACOO-", "HCO3-", "CO3^2-", "H3O+", "OH-")


def _rows(path: Path) -> list[dict[str, str]]:
    with path.open(newline="", encoding="utf-8") as handle:
        return list(csv.DictReader(handle))


class Phase2ActivityScaffoldTests(unittest.TestCase):
    def test_reaction_manifest_promotes_austgen_activity_constants(self) -> None:
        path = ROOT / "data" / "reference" / "MEA" / "manifests" / "phase2_reaction_constant_manifest.csv"
        rows = _rows(path)
        self.assertEqual([row["reaction_id"] for row in rows], ["R1", "R2", "R3", "R4", "R5"])
        for row in rows:
            self.assertEqual(row["activity_basis_needed"], "thermodynamic_activity")
            self.assertEqual(row["conversion_status"], "source_verified")
            self.assertEqual(row["used_in_phase2"], "not_yet_solver_blocked")
            self.assertIn("Nasrifar2010_Table1", row["source"])
            self.assertIn("residual gates", row["notes"])

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
            self.assertEqual(row["model_use_status"], "not_yet_solver_blocked")
            self.assertTrue((ROOT / row["source_file_repo_relative"]).exists())

    def test_activity_constant_candidates_keep_promotion_gate_explicit(self) -> None:
        path = ROOT / "data" / "reference" / "MEA" / "manifests" / "phase2_activity_constant_candidates.csv"
        rows = _rows(path)
        self.assertEqual([row["reaction_id"] for row in rows], ["R1", "R2", "R3", "R4", "R5"])
        status_by_reaction = {row["reaction_id"]: row["phase2_status"] for row in rows}
        self.assertEqual(set(status_by_reaction.values()), {"source_verified_but_solver_blocked"})
        source_by_reaction = {row["reaction_id"]: row["candidate_source"] for row in rows}
        self.assertEqual(source_by_reaction["R4"], "Nasrifar2010_Table1_via_Austgen1991")
        self.assertEqual(source_by_reaction["R5"], "Nasrifar2010_Table1_via_Austgen1991")
        self.assertEqual(float([row for row in rows if row["reaction_id"] == "R1"][0]["c3"]), -22.4773)
        for row in rows:
            self.assertEqual(row["validation_role"], "not_used_until_solver_and_residual_gates_pass")
            self.assertIn("issue #115", row["next_action"])
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

    def test_required_output_status_records_blocked_equilibrium_outputs(self) -> None:
        path = ROOT / "analyses" / "phase2_activity_epcsaft" / "results" / "phase2_required_output_status.csv"
        rows = {row["artifact"]: row for row in _rows(path)}
        self.assertEqual(rows["phase2_activity_speciation_problem.json"]["status"], "problem_definition_generated")
        self.assertEqual(rows["phase2_equilibrium_results.csv"]["status"], "scaffold_ready_blocked_by_epcsaft_issue_115")
        self.assertIn("issue #115", rows["phase2_equilibrium_results.csv"]["blocking_requirement"])
        self.assertEqual(rows["phase2_density_viscosity_validation.csv"]["status"], "data_inventory_ready")
        self.assertEqual(rows["phase2_pressure_metrics.csv"]["status"], "bounded_incomplete")
        self.assertEqual(rows["phase2_speciation_metrics.csv"]["status"], "bounded_incomplete")
        self.assertFalse((ROOT / "analyses" / "phase2_activity_epcsaft" / "results" / "phase2_equilibrium_results.csv").exists())

    def test_generated_problem_definition_records_candidate_manifest(self) -> None:
        import json

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
        self.assertEqual(activity_convention["candidate_status_counts"]["source_verified_but_solver_blocked"], 5)
        self.assertNotIn("promoted_reference_state_verified", activity_convention["candidate_status_counts"])
        self.assertEqual(activity_convention["current_manifest_conversion_status"], ["source_verified"])

    def test_bounded_incomplete_report_prevents_phase2_completion_claim(self) -> None:
        path = ROOT / "analyses" / "phase2_activity_epcsaft" / "results" / "phase2_bounded_incomplete_report.md"
        text = path.read_text(encoding="utf-8")
        self.assertIn("phase2_status: bounded_incomplete", text)
        self.assertIn("solver_status: scaffold_ready_blocked_by_epcsaft_issue_115", text)
        self.assertNotIn("Phase 2 complete", text)


if __name__ == "__main__":
    unittest.main()
