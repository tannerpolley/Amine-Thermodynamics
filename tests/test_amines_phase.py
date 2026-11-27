from analyses.amines import dea, mdea
from analyses.amines.fit import retained_endpoint, route_for
from analyses.amines.phase import SuppliedTrials, measured_search_class, native_search, search_class, states
from analyses.amines.wheel import ROOT, verify
from analyses.amines.records import RESULTS, read

MOVE = RESULTS / "move"


def selected(design, amine):
    return retained_endpoint(design | {"retained": MOVE / amine / "reported/fit"})


def test_classify_held_mea_measured_searches_without_solving():
    measured = RESULTS / "mea/reported/phase/measured"
    rows = [row for path in sorted(measured.glob("*.json.gz")) for row in read(path)]
    assert rows
    for row in rows:
        expected = "descent" if row["witnesses"] else "searched, no instability" if row["available"] else "unavailable"
        assert measured_search_class(row) == expected, row["identity"]


def test_supplied_mdea_trial_detects_descent_when_optimized_search_is_unavailable():
    design = mdea.FIT_SETS["reported"]
    point, _ = selected(design, "mdea")
    route = route_for(design)
    spec = route.bind(point)
    key = "comparison:157:problem"
    (state,) = (q for q in states(route, spec) if q["key"] == key)
    retained = read(MOVE / "mdea/reported/phase/declared.json.gz")
    assert retained["wheel"] == verify()
    (row,) = (q for q in retained["rows"] if q["key"] == key)
    bank = read(ROOT / "analyses/mdea_mea_workflow/results/retransfer-343/binary-penalty/split-record.json")
    supplied = SuppliedTrials(spec, bank["trials"] + bank["supplied_trials"])
    result = native_search(route, spec, state, supplied=supplied)["search"]
    assert result["status"] == row["status"]
    assert result["optimized_available"] == row["optimized_available"] is False
    assert result["supplied_minimum_tpd"] == row["supplied_minimum_tpd"]
    assert search_class(result) == "descent"


def test_mdea_carbon_free_parent_excludes_carbon_bearing_supplied_trials():
    design = mdea.FIT_SETS["reported"]
    point, _ = selected(design, "mdea")
    route = route_for(design)
    spec = route.bind(point)
    key = "fit:85:initial"
    (state,) = (row for row in states(route, spec) if row["key"] == key)
    retained = read(RESULTS / "mdea/reported/phase/MDEA/screen/selected/declared/summary.json.gz")
    (row,) = (row for row in retained["rows"] if row["key"] == key)
    bank = read(ROOT / "analyses/mdea_mea_workflow/results/retransfer-343/binary-penalty/split-record.json")
    from analyses.amines.phase import _bind_search, _search

    _bind_search(route, point, bank["trials"] + bank["supplied_trials"])
    result = _search(state)["search"]
    assert result["optimized_available"]
    assert result["supplied_trial_counts"] == {
        "available": row["supplied_trial_counts"]["available"],
        "unavailable": 0,
        "not_applicable": row["supplied_trial_counts"]["unavailable"],
    }
    assert search_class(result) == "searched, no instability"


def test_mea_measured_parent_uses_density_scaled_pressure_closure():
    from analyses.amines import mea
    from analyses.amines.phase import measured_search, scaled_pressure_error

    design = mea.FIT_SETS["reported"]
    point, _ = selected(design, "mea")
    spec = route_for(design).bind(point)
    measured = RESULTS / "mea/reported/phase/measured"
    key = "vle_obs_0034-pco2"
    (row,) = (row for path in measured.glob("*.json.gz") for row in read(path) if row["identity"] == key)
    assert row["available"] is False
    bank = read(ROOT / "analyses/mea_parameter_bundle/results/reduced-refit/split-registry.json")["trials"]
    result = measured_search(spec, row, [dict(trial, kind=trial["kind"].capitalize()) for trial in bank])
    (liquid,) = result["parent"]["phases"]
    tol = row["row_tolerance"]
    assert abs(liquid["relative_pressure_residual"]) > tol
    assert scaled_pressure_error(liquid["pressure_residual_Pa"], liquid["density_mol_m3"], liquid["T_K"]) <= tol
    assert result["available"] and not result["descent"]


def test_dea_lawson_trace_species_reconstruction():
    design = dea.FIT_SETS["reported"]
    point = read(design["retained"] / "A.json.gz")["endpoint"]
    route = route_for(design | {"route": dea.ExpandedDEA})
    spec = route.bind(point)
    key = "lawson-1976-viii:1:problem"
    (state,) = (row for row in states(route, spec) if row["key"] == key)
    result = native_search(route, spec, state)["search"]
    assert result["completed"] and result["available"]
    assert "reconstruction destroys support" not in (result.get("cause") or "")
