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
            self.assertEqual(row["conversion_status"], "thermodynamic_activity")
            self.assertEqual(row["used_in_phase2"], "fixed_input_pending_upstream_activity_solver")
            self.assertIn("Austgen1991", row["source"])

    def test_activity_constant_candidates_keep_promotion_gate_explicit(self) -> None:
        path = ROOT / "data" / "reference" / "MEA" / "manifests" / "phase2_activity_constant_candidates.csv"
        rows = _rows(path)
        self.assertEqual([row["reaction_id"] for row in rows], ["R1", "R2", "R3", "R4", "R5"])
        status_by_reaction = {row["reaction_id"]: row["phase2_status"] for row in rows}
        self.assertEqual(set(status_by_reaction.values()), {"promoted_reference_state_verified"})
        source_by_reaction = {row["reaction_id"]: row["candidate_source"] for row in rows}
        self.assertEqual(source_by_reaction["R4"], "Austgen1991_TableV")
        self.assertEqual(source_by_reaction["R5"], "Austgen1991_TableV")
        for row in rows:
            self.assertEqual(row["validation_role"], "promoted_fixed_input_pending_solver")
            self.assertIn("issue #115", row["next_action"])

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
        self.assertEqual(rows["phase2_activity_speciation_problem.json"]["status"], "generated")
        self.assertEqual(rows["phase2_equilibrium_results.csv"]["status"], "blocked_upstream_solver_backend_unavailable")
        self.assertIn("issue #115", rows["phase2_equilibrium_results.csv"]["blocking_requirement"])
        self.assertEqual(rows["phase2_density_viscosity_validation.csv"]["status"], "data_available_model_not_evaluated")
        self.assertFalse((ROOT / "analyses" / "phase2_activity_epcsaft" / "results" / "phase2_equilibrium_results.csv").exists())

    def test_generated_problem_definition_records_candidate_manifest(self) -> None:
        import json

        path = ROOT / "analyses" / "phase2_activity_epcsaft" / "results" / "phase2_activity_speciation_problem.json"
        payload = json.loads(path.read_text(encoding="utf-8"))
        activity_convention = payload["activity_convention"]
        self.assertEqual(
            activity_convention["candidate_manifest"],
            "data/reference/MEA/manifests/phase2_activity_constant_candidates.csv",
        )
        self.assertEqual(activity_convention["candidate_status_counts"]["promoted_reference_state_verified"], 5)
        self.assertNotIn("blocked_original_source_required", activity_convention["candidate_status_counts"])
        self.assertEqual(activity_convention["current_manifest_conversion_status"], ["thermodynamic_activity"])


if __name__ == "__main__":
    unittest.main()
