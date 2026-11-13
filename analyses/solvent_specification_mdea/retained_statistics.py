"""Issue #320: aggregate retained B1 rows into AARD and signed bias. No model evaluation.

Run from the repository root: python3 analyses/solvent_specification_mdea/retained_statistics.py
AARD = mean(|predicted - observed| / observed) x 100; bias = mean((predicted - observed) / observed) x 100,
the definitions used for the pressure summaries (Part I, MEA fitted/non-fitted pressures).
"""
import hashlib
import json
from collections import defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
PRESSURE = ROOT / "analyses/solvent_specification_mdea/results/adoption-302/B1/pressure.json"
REPLAY = ROOT / "analyses/mdea_mea_workflow/results/refit-298/B1-endpoint/fitted-replay.json"
REPLAY_SUMMARY = ROOT / "analyses/mdea_mea_workflow/results/refit-298/B1-endpoint/replay-summary.json"
ADOPTION_REPLAY = ROOT / "analyses/solvent_specification_mdea/results/adoption-302/replay.json"
REACTION = ROOT / "analyses/mdea_mea_workflow/results/reaction-basis-kamps-maurer.json"
OUT = ROOT / "analyses/solvent_specification_mdea/results/retained-statistics-320.json"
RANGE_K = json.loads(REACTION.read_text())["source_findings"]["range_K"]


def stats(pairs, unit=None):
    """pairs: (observed, predicted). Relative errors in percent; absolute error in the property's unit."""
    n = len(pairs)
    rel = [(p - o) / o * 100 for o, p in pairs]
    out = {"rows": n, "AARD_percent": sum(abs(r) for r in rel) / n}
    if not unit:
        out["bias_percent"] = sum(rel) / n
    if unit:
        out["mean_abs_error"] = sum(abs(p - o) for o, p in pairs) / n
        out["mean_signed_error_predicted_minus_observed"] = sum(p - o for o, p in pairs) / n
        out["unit"] = unit
    return out


def in_range(t):
    return RANGE_K[0] <= t <= RANGE_K[1]


# a. Pressure groups (CO2 partial pressure), per temperature, in/out of the law's range, overall
pressure = defaultdict(list)
for r in json.loads(PRESSURE.read_text()):
    assert r["success"]
    pressure[r["group"]].append((float(r["row"]["temperature_K"]), r["observed_Pa"], r["predicted_Pa"]))
split = {}
for g, rows in pressure.items():
    by_t = defaultdict(list)
    for t, o, p in rows:
        by_t[t].append((o, p))
    split[g] = {
        "per_temperature_K": {f"{t:.2f}": stats(v) for t, v in sorted(by_t.items())},
        "inside_278_368K": stats([(o, p) for t, o, p in rows if in_range(t)]) if any(in_range(t) for t, *_ in rows) else None,
        "outside_278_368K": stats([(o, p) for t, o, p in rows if not in_range(t)]) if any(not in_range(t) for t, *_ in rows) else None,
        "overall": stats([(o, p) for _, o, p in rows]),
    }
assert abs(split["Ermatchkov"]["overall"]["AARD_percent"] - 18.2705616) < 1e-6
assert abs(split["Xiao"]["overall"]["AARD_percent"] - 28.1910414) < 1e-6

# b. Fitted rows by source
UNITS = {"Jakobsen": "dimensionless (protonated fraction)", "Carson": "J/mol CO2", "Merkley": "J/mol CO2",
         "Cp": "J/(mol-feed K)", "loaded-density": "kg/m^3", "unloaded-density": "kg/m^3"}
PRESSURE_GROUPS = {"Kuranov", "Kim"}
groups = defaultdict(list)
by_range = {"Kuranov": defaultdict(list), "Merkley": defaultdict(list)}
for r in json.loads(REPLAY.read_text()):
    assert r["status"] == "Available"
    g = r["meta"]["group"]
    pair = (r["meta"]["observed"], r["value"])
    groups[g].append((pair, r["unit"]))
    if g in by_range:
        by_range[g][float(r["meta"]["row"]["temperature_K"])].append(pair)
summary = json.loads(REPLAY_SUMMARY.read_text())["groups"]
fitted = {}
for g, v in groups.items():
    assert len(v) == summary[g]["rows"]
    fitted[g] = stats([p for p, _ in v], None if g in PRESSURE_GROUPS else UNITS[g])
    fitted[g]["scaled_RMS"] = summary[g]["scaled_RMS"]
    fitted[g]["fitted_unit_in_replay"] = v[0][1]
fitted["Merkley_by_temperature_K"] = {
    f"{t:.2f}": {**stats(v, UNITS["Merkley"]), "inside_278_368K": in_range(t)} for t, v in sorted(by_range["Merkley"].items())
}
kur = by_range["Kuranov"]
fitted["Kuranov_by_law_range"] = {
    name: stats([p for t, v in kur.items() if in_range(t) == flag for p in v])
    for name, flag in (("inside_278_368K", True), ("outside_278_368K", False))
}
fitted["Kuranov_by_law_range"]["outside_temperatures_K"] = sorted(t for t in kur if not in_range(t))

# The adoption-302 replay holds the same 278 predictions as the B1-endpoint fitted replay.
a = json.loads(ADOPTION_REPLAY.read_text())
b = json.loads(REPLAY.read_text())
assert [x["value"] for x in a] == [x["value"] for x in b]

sha = lambda p: hashlib.sha256(p.read_bytes()).hexdigest()
result = {
    "note": "Aggregation of retained rows; no model evaluation. AARD and bias definitions in the script docstring.",
    "dissociation_law_range_K": RANGE_K,
    "ermatchkov_xiao_pressure": split,
    "B1_fitted_by_source": fitted,
    "files": {str(p.relative_to(ROOT)): sha(p) for p in (PRESSURE, REPLAY, REPLAY_SUMMARY, ADOPTION_REPLAY, REACTION)},
}
OUT.write_text(json.dumps(result, indent=2) + "\n")
print(json.dumps(result, indent=2))
