"""Replay #411 and score the four #126 readings on Kuranov Table 2."""
from hashlib import sha256
import json
from pathlib import Path
from statistics import fmean
import sys

ANALYSES = Path(__file__).resolve().parents[2]
sys.path[:0] = [str(ANALYSES), str(ANALYSES / "mdea_kuranov_refit")]
from part_ii import ROOT, SHA, Route  # noqa: E402
import conventions  # noqa: E402
import model  # noqa: E402
import score  # noqa: E402

WORKFLOW = ANALYSES / "mdea_mea_workflow"
OUTPUT = WORKFLOW / "results/kuranov-published-422"


def replay_records(spec, row):
    records = [r for role in ("fitted", "comparisons") for r in spec.inputs["observations"][role]
               if r["group"].startswith("Kuranov")]
    comparison = next(r for r in records if r["group"] == "Kuranov-413K")
    dataset = next(d for d in spec.spec["datasets"] if d["name"] == "outside-fit-Kuranov-413K")
    key = "kuranov:72"
    state = dict(T=row["T"], P=row["p_exp"], water=1 / 0.01801528 / row["m_mdea"],
                 alpha=row["alpha"], observed=row["p_exp"], scale=1.0)
    spec.problems[key] = spec.problem(dataset["template"], state)
    args = spec.bind(dataset["arguments"], state)
    basis = dict(comparison["basis"], arguments=args, template=dataset["template"])
    return records + [dict(comparison, identity=key, problem=key, row={"source_row": "72"},
                           arguments=args, basis=basis, group="Kuranov-393K", role="not fitted")]


def reduce(rows, name):
    unsolved = [r["row"] for r in rows if r[name]["pressure_Pa"] is None]
    errors = {r["row"]: 100 * (r[name]["pressure_Pa"] / r["p_exp"] - 1) for r in rows
              if r["row"] not in unsolved}
    aard = fmean(map(abs, errors.values())) if errors else None
    worst = max(errors, key=lambda i: abs(errors[i])) if errors else None
    return dict(n=len(rows), solved=len(errors), unsolved_rows=unsolved, AARD_percent=None if unsolved else aard,
                solved_AARD_percent=aard, bias_percent=fmean(errors.values()) if errors else None,
                max_abs_percent=abs(errors[worst]) if errors else None, worst_row=worst)


declaration = WORKFLOW / "inputs/bounded-binary-411.json"
route = Route(declaration, out=WORKFLOW / "results/runs/kuranov-published-422")
base = WORKFLOW / "results/bounded-binary-411"
inputs = (score.KURANOV, base / "endpoint.json", base / "data-rows.json")
release = ROOT / "analyses/mea_parameter_bundle/results/release-recheck-414/display-inputs.json"
inventory = json.loads(release.read_text())["files"]
expected = {k: v["retained_sha256"] for k, v in inventory.items() if "retained_sha256" in v}
expected.update(json.loads((WORKFLOW / "inputs/hashes.json").read_text()))
hashes = {str(p.relative_to(ROOT)): sha256(p.read_bytes()).hexdigest() for p in inputs}
assert all(expected[path] == digest for path, digest in hashes.items()), hashes
rows = [dict(r, alpha=r["m_co2"] / r["m_mdea"]) for r in score.kuranov_rows()]
assert [r["row"] for r in rows] == list(range(1, 83))
values, _, _ = route.replay(json.loads(inputs[1].read_text()), rows=lambda spec: replay_records(spec, rows[71]))
route.write("replay.json", values)
previous = {p["identity"]: p["value"] for p in json.loads(inputs[2].read_text())
            if p["group"].startswith("Kuranov")}
for r, p in zip(rows, sorted(values, key=lambda p: int(p["row"]["source_row"])), strict=True):
    assert r["row"] == int(p["row"]["source_row"]) and p["status"] == "Available", p
    relative = abs(p["value"] / previous[p["identity"]] - 1) if r["row"] != 72 else None
    assert relative is None or relative <= 1e-10, (p["identity"], relative)
    role = "fitted" if p["group"] in ("Kuranov", "Kuranov-binary") else "not fitted"
    r.update(role=role, group=p["group"], replay_relative_difference=relative,
             present=dict(pressure_Pa=p["value"], status=p["status"], basis=p["basis"]))
score.check_temperature_laws()
m_mdea = 0.6 / (0.4 * model.COMPONENTS[model.MDEA][0])
own = [dict(row=i, series="Wangler Table 10", T=303.0, m_mdea=m_mdea, m_co2=m_mdea * alpha,
            alpha=alpha, p_exp=bar * 1e5) for i, (alpha, bar) in
       enumerate(((0.9374, 9.2), (0.9973, 14.2), (1.0448, 24.5)), 1)]
documents = dict(Uyan=conventions.uyan(), Uyan_k0=conventions.uyan(False),
                 Wangler=model.document(), Wangler_charged=model.charged_molecule_ions(model.document(), model.MDEAH))
for name, document in documents.items():
    for campaign in (rows, own) if name.startswith("Wangler") else (rows,):
        predictions = score.solve_rows(document, campaign)
        for r in campaign:
            p = predictions[r["row"]]
            r[name] = dict(pressure_Pa=p["p_calc"] if p["success"] else None, message=p["message"],
                           status="solved" if p["success"] else "unsolved", linear_solver=p["linear_solver"])

limits = route.config["reaction_ranges_K"]["MDEA-dissociation"]
sets = {"K82": rows, "K19": rows[:41], "K32": rows[41:],
        "K19-loaded": [r for r in rows[:41] if r["alpha"] > 0.01],
        "alpha > 1.2": [r for r in rows if r["alpha"] > 1.2],
        "alpha <= 1.2": [r for r in rows if r["alpha"] <= 1.2],
        "C28": [r for r in rows[11:41] if r["alpha"] > 0],
        "Wangler Table 10": own}
sets["C21"] = [r for r in sets["C28"] if r["p_exp"] <= 3e6]
sets["not fitted"] = [r for r in rows if r["role"] == "not fitted"]
groups = {"fitted loaded": "Kuranov", "fitted CO2-free": "Kuranov-binary",
          "not fitted 413 K": "Kuranov-413K", "not fitted 393 K": "Kuranov-393K"}
sets.update({s: [r for r in rows if r["group"] == group] for s, group in groups.items()})
sets["fitted loaded, within 278–368 K"] = [r for r in sets["fitted loaded"] if limits[0] <= r["T"] <= limits[1]]
sets["fitted loaded, above 368 K"] = [r for r in sets["fitted loaded"] if r["T"] > limits[1]]
present = {s: reduce(rr, "present") for s, rr in sets.items() if rr is not own}
targets = {"Uyan": (("K82", "22.9"), ("K82", "34.4"), ("K19-loaded", "19.22"),
                    ("K19", "19.82"), ("K32", "25.91")),
           "Wangler": (("K82", "19.7"), ("K32", "19.44"), ("Wangler Table 10", "10.25"))}
reconstruction = [dict(reading=name, subset=s, printed=printed, **reduce(sets[s], name))
                  for name in documents for s, printed in targets[name.split("_")[0]]]
stats = dict(present=present, reconstruction=reconstruction, sets={s: [r["row"] for r in rr] for s, rr in sets.items()})
for script in (declaration, Path(__file__).resolve(), ANALYSES / "part_ii.py", model.__file__, score.__file__, conventions.__file__):
    path = Path(script)
    hashes[str(path.relative_to(ROOT))] = sha256(path.read_bytes()).hexdigest()
for r in rows + own:
    r["source_row"] = r.pop("row")
OUTPUT.mkdir(exist_ok=True)
for name, value in (("kuranov-rows", rows), ("wangler-table-10-rows", own), ("statistics", stats),
                    ("hashes", dict(wheel_sha256=SHA, files=hashes))):
    (OUTPUT / f"{name}.json").write_text(json.dumps(value, indent=2, allow_nan=False) + "\n")
for result in reconstruction:
    aard, printed = result["AARD_percent"], result["printed"]
    assert aard is None or abs(aard - float(printed)) > 0.5 * 10**-len(printed.split(".")[1]), result
for group, n, aard in zip(groups, (66, 4, 11, 1), (20.0922, 2.5631, 20.3271, 41.4625), strict=True):
    assert (present[group]["n"], round(present[group]["AARD_percent"], 4)) == (n, aard), present[group]
