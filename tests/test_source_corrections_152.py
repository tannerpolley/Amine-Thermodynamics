"""Source/result invariants only: no equilibrium solve, fit or publication write."""
import copy
import csv
import importlib.util
import json
from pathlib import Path
import sys

import pytest

ROOT = Path(__file__).resolve().parents[1]
BUNDLE = ROOT / "analyses/mea_parameter_bundle"
STUDY = BUNDLE / "results/source-corrections-152"
sys.path.insert(0, str(BUNDLE / "scripts"))
import shared_evaluation as shared


def rows(path):
    with path.open(newline="", encoding="utf-8-sig") as stream:
        return list(csv.DictReader(stream))


def test_source_population_and_immutable_assignments():
    vle = rows(shared.CANONICAL_VLE)
    active = rows(shared.CANONICAL_VLE.with_name("Combined_VLE.csv"))
    assert (len(vle), len(active)) == (327, 162)
    assert sum(row["source_key"] == "Hilliard2008" for row in active) == 31
    assert next(row for row in vle if row["observation_id"] == "vle_obs_0148")["temperature_measured_C"] == "60.106"
    old = rows(STUDY / "baseline/grouped_split_manifest.csv")
    new = rows(ROOT / "data/reference/MEA/manifests/grouped_split_manifest.csv")
    before = {(row["target_family"], row["record_id"]): row for row in old}
    assert set(before) == {(row["target_family"], row["record_id"]) for row in new}
    for row in new:
        assert all(row[field] == before[(row["target_family"], row["record_id"])][field] for field in ("group_id", "split", "role", "weight"))
    cv_before = {row["observation_id"]: row for row in rows(STUDY / "baseline/reactive_vle_cross_validation.csv")}
    for row in rows(ROOT / "data/reference/MEA/manifests/reactive_vle_cross_validation.csv"):
        if row["observation_id"] in cv_before:
            assert all(row[field] == cv_before[row["observation_id"]][field] for field in ("campaign_block_id", "cross_validation_fold"))


@pytest.mark.parametrize("source_key", ["Hilliard2008", "Xu2011"])
def test_actual_native_temperature_and_analytical_feed(source_key):
    shared.verify_wheel()
    source = next(row for row in rows(shared.CANONICAL_VLE) if row["source_key"] == source_key)
    template = shared.load_state_packet()["observations"][0]["request"]
    request = shared.source_feed_request(template, source)
    problem = shared._problem_from_request(shared.corrected_request(request))
    assert problem.T == float(source["temperature_measured_C"]) + 273.15
    actual = [problem.feed.values[name] for name in shared.COMPONENT_IDS]
    system = request["reaction_system"]
    extents = system["analytical_feed_contract"]["seed_extents_mol"]
    neutral = [amount - sum(row[i] * extent for row, extent in zip(system["reaction_matrix"], extents)) for i, amount in enumerate(actual)]
    assert abs(neutral[1] / (system["molar_masses_kg_per_mol"][2] * neutral[2]) / float(source["source_molality_mol_per_kg_water"]) - 1) <= 1e-12
    assert abs(neutral[1] - 1) < 1e-15
    assert abs(actual[1] - 0.99998) < 1e-15
    assert abs(sum(a * q for a, q in zip(actual, system["charges"]))) <= 1e-12
    for mutation in ("molality", "temperature", "contract", "double_seed"):
        bad = copy.deepcopy(request)
        if mutation == "molality":
            del bad["reaction_system"]["analytical_feed_contract"]["source_coordinates"]["source_molality_mol_per_kg_water"]
        elif mutation == "temperature":
            bad["temperature"]["value"] = 313.15
        elif mutation == "contract":
            del bad["reaction_system"]["analytical_feed_contract"]
        else:
            bad["reaction_system"]["feed_amounts_mol"][2] -= 0.00021
        with pytest.raises((KeyError, ValueError)):
            shared._problem_from_request(shared.corrected_request(bad))
    nominal = dict(source)
    nominal["temperature_reported_C"] = "40" if source_key == "Hilliard2008" else "100"
    if float(nominal["temperature_reported_C"]) != float(source["temperature_measured_C"]):
        with pytest.raises(ValueError):
            shared.source_feed_request(template, nominal)


def test_pool_transport_context_and_mat_unverified_preservation():
    old = shared.load_state_packet()["observations"]
    new = shared.expand_state_packet(shared.source_corrected_packet())["observations"]
    assert [row["identity"] for row in old] == [row["identity"] for row in new]
    for before, after in zip(old, new):
        assert [target["identity"] for target in before["targets"]] == [target["identity"] for target in after["targets"]]
        if before["identity"].startswith("Matin"):
            assert before["request"]["reaction_system"]["feed_amounts_mol"] == after["request"]["reaction_system"]["feed_amounts_mol"]
            assert before["request"]["temperature"] == after["request"]["temperature"]
            assert [t["observed"] for t in before["targets"]] == [t["observed"] for t in after["targets"]]
        for target in after["targets"]:
            if target["identity"].endswith("::HCO3-"):
                output = next(o for o in after["request"]["outputs"] if o["identity"] == target["prediction_identity"])
                assert output["coefficients"] == [0, 0, 0, 0, 0, 1, 1, 0, 0]
    membership = rows(ROOT / "data/reference/MEA/manifests/speciation_target_membership.csv")
    context = [r for r in membership if r["species"] == "2-OXA"]
    assert len(context) == 68 and all(r["target_eligible"] == "no" and not r["linear_coefficients"] for r in context)
    assert all(r["target_eligible"] == "no" for r in membership if r["state_id"] == "Matin2012_state_016")


def test_current_volumetrics_and_old_pin_refusal():
    from MEA.epcsaft_ionic.preregistration import PreregistrationError, validate_gate0_preregistration
    prereg = ROOT / "analyses/reactive_epcsaft_parameter_evidence/ionic_volumetric_fit_preregistration.json"
    with pytest.raises(PreregistrationError, match="Gate 0 tracer source artifact drifted"):
        validate_gate0_preregistration(json.loads(prereg.read_text()))
    amundsen = rows(ROOT / "data/reference/MEA/observations/density_viscosity/Amundsen_2009_density_viscosity.csv")
    assert sum(row["system"] == "pure_mea" for row in amundsen) == 10
    assert all(not r["uncertainty_value"] for r in amundsen if r["co2_loading_mol_per_mol_mea"])
    contract = rows(ROOT / "data/reference/MEA/manifests/ionic_volumetric_observation_contract.csv")
    analog = [r for r in contract if r["data_family"] == "ethanolammonium_carboxylate_density"]
    assert len(analog) == 128 and all(r["target_eligible"] == "no" for r in analog)


def test_public_views_refuse_execution_and_stale_hash():
    from MEA.common import data_access as data
    data.verify_regression_readiness_sources()
    with pytest.raises(RuntimeError, match="blocked"):
        data.require_regression_execution_admitted()
    with pytest.raises(RuntimeError, match="hash drift"):
        data.verify_source_hashes({"data/reference/MEA/manifests/grouped_split_manifest.csv": "0" * 64}, repo_root=ROOT)
    for role in ("active_training", "reserved_validation"):
        assert len(data.load_regression_vle_view(role=role, executable_only=False)) > 0
        assert len(data.load_regression_speciation_view(role=role, executable_only=False)) > 0


def test_declared_domain_pre_dispatch_and_protected_rows(monkeypatch):
    sys.path.insert(0, str(BUNDLE / "calibration-misfit"))
    import probe
    probe.RECORD = BUNDLE / "results/selected-current-best-parameters.json"
    def forbidden_solve(*args, **kwargs):
        raise AssertionError("domain classification must not invoke a solve")
    monkeypatch.setattr(probe, "base_record", forbidden_solve)
    excluded = [state for state in probe.CANONICAL if probe.reaction_domain_status(state)]
    assert [state["identity"] for state in excluded] == [f"canonical:vle_obs_{i}" for i in ("0286", "0287", "0288")]
    assert [round(state["request"]["temperature"]["value"] - 273.15, 10) for state in excluded] == [120.4, 121.0, 121.8]
    assert all("reaction R2 temperature outside reaction correlation" in probe.reaction_domain_status(state) for state in excluded)
    for identity in ("vle_obs_0119", "benchmark:vle_obs_0286", "transfer:canonical:vle_obs_0286", "Jakobsen2005_row9"):
        protected = copy.deepcopy(excluded[0])
        protected["identity"] = identity
        with pytest.raises(RuntimeError, match="protected comparison/target"):
            probe.reaction_domain_status(protected)
    inside = copy.deepcopy(excluded[0])
    inside["request"]["temperature"]["value"] = 393.15
    assert probe.reaction_domain_status(inside) is None
    assert shared.sha256(probe.RECORD) == "756fec502d3a1433d538abb073c4caeabf91902013ab7e27d5459ce70396543b"
