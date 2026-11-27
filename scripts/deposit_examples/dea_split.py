"""Search the repaired DEA model at the former 30 wt% split state."""
from _inputs import RESULTS, endpoint, fingerprint, read
from analyses.amines.dea import FIT_SETS
from analyses.amines.phase import SuppliedTrials, native_search, search_class, states

route, point = endpoint(FIT_SETS["reported"])
key = "weiland-1998:32:problem"
retained = read(RESULTS / "move/dea/reported/phase/declared.json.gz")
assert retained["endpoint_fingerprint"] == fingerprint(point)
spec = route.bind(point)
(state,) = (r for r in states(route, spec) if r["key"] == key)
(expected,) = (r for r in retained["rows"] if r["key"] == key)
bank = SuppliedTrials(spec, route.load(route.config["split_record"])["trials"])
search = native_search(route, spec, state, supplied=bank)["search"]
assert search["available"]
assert search_class(search) == search_class(expected) == "searched, no instability"
print(f"{spec.problems[state['problem']].P:g} Pa: {search_class(search)}")
