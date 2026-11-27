"""Source/result invariants only: no equilibrium solve, fit or publication write."""
import copy
import csv
from pathlib import Path

import pytest

from analyses.amines import mea
from analyses.amines.wheel import verify

ROOT = Path(__file__).resolve().parents[1]
BUNDLE = ROOT / "analyses/mea_parameter_bundle"
STUDY = BUNDLE / "results/source-corrections-152"
CANONICAL = mea.PRESSURE_INPUTS["canonical"]


def rows(path):
    with path.open(newline="", encoding="utf-8-sig") as stream:
        return list(csv.DictReader(stream))


def test_source_population_and_immutable_assignments():
    vle = rows(CANONICAL)
    active = rows(CANONICAL.with_name("Combined_VLE.csv"))
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
    verify()
    mapping = mea.parameter_mapping(BUNDLE / "results/selected-current-best-parameters.json")
    source = next(row for row in rows(CANONICAL) if row["source_key"] == source_key)
    template = mea.load_state_packet()["observations"][0]["request"]
    request = mea.source_feed_request(template, source)
    problem = mea._problem_from_request(mea.corrected_request(request, mapping))
    assert problem.T == float(source["temperature_measured_C"]) + 273.15
    actual = [problem.feed.values[name] for name in mea.COMPONENT_IDS]
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
            mea._problem_from_request(mea.corrected_request(bad, mapping))
    nominal = dict(source)
    nominal["temperature_reported_C"] = "40" if source_key == "Hilliard2008" else "100"
    if float(nominal["temperature_reported_C"]) != float(source["temperature_measured_C"]):
        with pytest.raises(ValueError):
            mea.source_feed_request(template, nominal)


def test_pool_transport_context_and_mat_unverified_preservation():
    old = mea.load_state_packet()["observations"]
    new = mea.load_state_packet(mea.PRESSURE_INPUTS["packet"])["observations"]
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


def test_current_volumetrics():
    amundsen = rows(ROOT / "data/reference/MEA/observations/density_viscosity/Amundsen_2009_density_viscosity.csv")
    assert sum(row["system"] == "pure_mea" for row in amundsen) == 10
    assert all(not r["uncertainty_value"] for r in amundsen if r["co2_loading_mol_per_mol_mea"])
    contract = rows(ROOT / "data/reference/MEA/manifests/ionic_volumetric_observation_contract.csv")
    analog = [r for r in contract if r["data_family"] == "ethanolammonium_carboxylate_density"]
    assert len(analog) == 128 and all(r["target_eligible"] == "no" for r in analog)
