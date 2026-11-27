from analyses.amines import dea, mdea
from analyses.amines.fit import retained_endpoint, route_for
from analyses.amines.phase import SuppliedTrials, measured_search_class, native_search, search_class, states
from analyses.amines.wheel import ROOT, verify
from analyses.amines.records import RESULTS, read


def test_classify_held_mea_measured_searches_without_solving():
    measured = RESULTS / "mea/reported/phase/measured"
    rows = [row for path in sorted(measured.glob("*.json.gz")) for row in read(path)]
    assert rows
    for row in rows:
        expected = "descent" if row["witnesses"] else "searched, no instability" if row["available"] else "unavailable"
        assert measured_search_class(row) == expected, row["identity"]


def test_supplied_mdea_trial_detects_descent_when_optimized_search_is_unavailable():
    design = mdea.FIT_SETS["reported"]
    point, _ = retained_endpoint(design)
    route = route_for(design)
    spec = route.bind(point)
    key = "comparison:157:problem"
    (state,) = (q for q in states(route, spec) if q["key"] == key)
    retained = read(RESULTS / "mdea/reported/phase/MDEA/screen/selected/declared/summary.json.gz")
    assert retained["wheel"] == verify()
    (row,) = (q for q in retained["rows"] if q["key"] == key)
    bank = read(ROOT / "analyses/mdea_mea_workflow/results/retransfer-343/binary-penalty/split-record.json")
    supplied = SuppliedTrials(spec, bank["trials"] + bank["supplied_trials"], compiled_support=False)
    result = native_search(route, spec, state, supplied=supplied)["search"]
    assert result["status"] == row["status"]
    assert result["optimized_available"] == row["optimized_available"] is False
    assert result["supplied_minimum_tpd"] == row["supplied_minimum_tpd"]
    assert search_class(result) == "descent"


def test_dea_registry_preserves_supplied_refusal_on_original_support():
    design = dea.FIT_SETS["reported"]
    point, _ = retained_endpoint(design)
    route = route_for(design)
    spec = route.bind(point)
    key = "carson-2000:10:initial"
    (state,) = (q for q in states(route, spec) if q["key"] == key)
    batches = RESULTS / "dea/reported/phase/selected-registry-growth/declared/batches"
    initial = read(batches / "0.json.gz")
    retained = read(batches / "1.json.gz")
    assert initial["wheel"] == retained["wheel"] == verify()
    witnesses = [w for row in initial["rows"] for w in row.get("witnesses", [])]
    (row,) = (q for q in retained["rows"] if q["key"] == key)
    supplied = SuppliedTrials(spec, witnesses, compiled_support=False)
    result = native_search(route, spec, state, supplied=supplied)["search"]
    assert search_class(result) == "unavailable"
    assert result["supplied_trial_counts"] == row["supplied_trial_counts"]


def test_original_mdea_cap_uses_the_saturation_predictions_refusal():
    design = mdea.FIT_SETS["system-pressure"]
    point = read(design["endpoint"])["prior_declaration"]
    route = route_for(design)
    spec = route.bind(point)
    key = "comparison:362:cap"
    (state,) = (q for q in states(route, spec) if q["key"] == key)
    rows = read(RESULTS / "mdea/system-pressure/phase/search-0.json.gz")
    (row,) = (q for q in rows if q["key"] == key)
    result = native_search(route, spec, state, cap_from_prediction=True)["search"]
    assert result["status"] == row["status"] == "Exception"
    assert search_class(result) == "unavailable"
