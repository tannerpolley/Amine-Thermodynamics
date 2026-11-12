"""Bounded phase-search probes at frozen stage-4 endpoints; no fitting."""

# ruff: noqa: E402
import copy
import hashlib
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT / "analyses/pz_transfer"))
import epcsaft
from epcsaft import equilibrium as eq
from binary_evidence import jsonable
from reactive import pressure_problem, laws_at, problem, PZ, W, CO2

OUT = Path(__file__).resolve().parent
AN = ROOT / "analyses/pz_transfer"
WHEEL = Path(
    "/home/tnnrpolley21/Workspaces/Engineering/Amine-Thermodynamics/build/engine-wheels/main-391dfe5d64ede5036bf160bc6ae037ad5e14af32/epcsaft-1.3.0-cp313-cp313-manylinux_2_39_x86_64.whl"
)
from run import SHA
import zipfile

assert hashlib.sha256(WHEEL.read_bytes()).hexdigest() == SHA
with zipfile.ZipFile(WHEEL) as z:
    for n in z.namelist():
        if n.startswith("epcsaft/") and not n.endswith("/"):
            assert (
                z.read(n) == (Path(epcsaft.__file__).parent.parent / n).read_bytes()
            ), n

import csv

rows = list(csv.DictReader((AN / "inputs/hilliard-d5.csv").open()))
output = []
for kind in "AB":
    par = epcsaft.Parameters.from_mapping(
        json.loads((AN / f"results/reactive-{kind}-endpoint.json").read_text())
    )
    x = json.loads((AN / f"results/reactive-{kind}-fit.json").read_text())["optimizer"]
    model = epcsaft.Mixture(par)
    for index in (0, 31, 61):
        row = rows[index]
        base = pressure_problem(par, row, x=x)
        sol = eq.solve_equilibrium(model, base)
        for label in (
            ["default", "refined", "parent-seed", "compressed-1.05", "compressed-3"]
            if index == 0
            else ["default"]
        ):
            prob = copy.copy(base)
            if label == "refined":
                prob.row_tolerance = 1e-12
            if label.startswith("compressed"):
                prob = problem(laws_at(x), float(row["T_K"]))
                prob.P = sol.pressure * float(label.split("-")[1])
                prob.feed.values = {
                    PZ: 1.0,
                    W: 1 / (0.0180153 * float(row["mPZ"])),
                    CO2: float(row["alpha_per_PZ"]),
                }
            s = eq.solve_equilibrium(model, prob)
            trials = copy.copy(prob)
            trials.phases = [
                eq.Phase("trial-L", kind="liquid", support=list(par.component_ids)),
                eq.Phase("trial-V", kind="vapor", support=[W, CO2, PZ]),
            ]
            opt = eq.StabilityOptions()
            if label == "parent-seed":
                trials.phases[0].composition_guess = list(
                    s.mole_fractions[: len(par.component_ids)]
                )
                trials.phases[0].packing_guess = 0.4
                opt.evaluate_supplied_trials = False
            opt.trials = trials._native(model).phases
            n = eq.stability_test(eq.compile_problem(model, prob), s, opt)
            r = dict(
                variant=kind,
                row=index + 1,
                label=label,
                T_K=float(row["T_K"]),
                mPZ=row["mPZ"],
                alpha=row["alpha_per_PZ"],
                pressure_Pa=s.pressure,
                solution_tolerance_met=s.requested_tolerance_met,
                max_residual=max(map(abs, s.residuals)),
                completed=n.completed,
                message=n.message,
                present_phases=jsonable(n.present_phases),
                trials=[],
            )
            for t in n.trials:
                q = {
                    k: jsonable(getattr(t, k))
                    for k in [
                        "seed",
                        "evidence",
                        "message",
                        "resolved_descent",
                        "quantities",
                        "composition",
                        "raw_coordinates",
                        "raw_residuals",
                        "split_coordinates",
                    ]
                }
                q.update(kind=t.phase.kind.name, optimizer_success=t.optimizer.success)
                r["trials"].append(q)
            output.append(r)
            (OUT / "probes.json").write_text(
                json.dumps(
                    dict(
                        wheel_sha256=SHA,
                        input_sha256={
                            str(p.relative_to(ROOT)): hashlib.sha256(
                                p.read_bytes()
                            ).hexdigest()
                            for p in [
                                AN / "inputs/hilliard-d5.csv",
                                AN / "results/speciation-reactions.json",
                                *[
                                    AN / f"results/reactive-{k}-{name}.json"
                                    for k in "AB"
                                    for name in ["endpoint", "fit"]
                                ],
                            ]
                        },
                        component_order=list(par.component_ids),
                        probes=output,
                    ),
                    indent=2,
                )
                + "\n"
            )
            print(kind, index + 1, label, n.message, flush=True)

assert len(output) == 14
assert all(r["solution_tolerance_met"] for r in output)
assert all(
    any(t["evidence"] == "indeterminate" for t in r["trials"])
    for r in output
    if not r["label"].startswith("compressed")
)
assert all(
    r["completed"]
    and not any(
        t["resolved_descent"] or t["evidence"] in ["indeterminate", "unresolved"]
        for t in r["trials"]
    )
    for r in output
    if r["label"].startswith("compressed")
)
