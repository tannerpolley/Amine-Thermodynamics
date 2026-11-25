"""Follow the finite-vapor TP flash of each stalled Kuranov feed toward its bubble."""

# ruff: noqa: E402
from copy import copy
from multiprocessing import Pool
from pathlib import Path
import sys
from time import monotonic

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent / "diagnosis-starts"))
import continuation as c


def run(case):
    draw, row = case
    tick = monotonic()
    spec = c.c.at(c.c.vector(draw))
    bubble = spec.problems[c.STATES[row["row"]]["problem"]]
    flash = copy(bubble)
    flash.phases = [copy(p) for p in bubble.phases]
    flash.phases[-1].amount = c.eq.Free()
    solution = None
    trace = []
    # Begin below the last reached bubble at this feed's smaller loading.
    P = min((row["pressure_Pa"] or 8e6) * 0.85, 30e6)
    pilot = "--pilot" in sys.argv
    if pilot:
        P = row["pressure_Pa"] * 0.85
    step = P * (0.05 if pilot else 0.08)
    good = None
    for _ in range(100 if pilot else 30):
        flash.P = P
        s = c.eq.solve_equilibrium(spec.model, flash, solution)
        entry = dict(P=P, message=s.message, amounts=list(s.amounts))
        trace.append(entry)
        if s.success and s.requested_tolerance_met and min(s.amounts) > 0:
            solution, good = s, P
            # Transfer both compositions and packings to the incipient-phase problem.
            for i, phase in enumerate(bubble.phases):
                x = s.phase_mole_fractions(i)
                phase.composition_guess = {
                    k: x[spec.parameters.component_ids.index(k)] for k in phase.support
                }
                phase.packing_guess = s.packing_fractions[i]
            bubble.P = c.eq.Free(P)
            b = c.eq.solve_equilibrium(spec.model, bubble)
            entry.update(bubble=b.message)
            if b.success and b.requested_tolerance_met:
                entry.update(bubble_Pa=b.pressure, densities=list(b.molar_densities))
                break
            P += step
            if not pilot:
                step *= 1.25
        elif good is None:
            P *= 0.85
            if P < 1e6:
                break
        else:
            step /= 2
            if step < 1000:
                break
            P = good + step
    record = dict(
        draw=draw,
        row=row["row"],
        loading=row["loading"],
        observed_Pa=row["observed_Pa"],
        last_loading=row["reached"],
        last_bubble_Pa=row["pressure_Pa"],
        trace=trace,
        seconds=monotonic() - tick,
    )
    if not pilot:
        c.c.refit.save(HERE / "pressure-rows" / f"{draw}-{row['row']}.json.gz", record)
    return record


if __name__ == "__main__":
    tick = monotonic()
    cases = [
        (d["draw"], r)
        for d in c.c.r.read(c.c.HERE / "results/continuation.json.gz")["records"]
        for r in d["rows"]
        if not r["reached_target"] and "vapor" not in r["stall_message"].lower()
    ]
    assert len(cases) == 37
    with Pool(4) as pool:
        rows = pool.map(run, cases[:1] if "--pilot" in sys.argv else cases, chunksize=1)
    c.c.refit.save(
        HERE
        / ("pressure-pilot.json.gz" if "--pilot" in sys.argv else "pressure.json.gz"),
        dict(
            wheel=c.c.r.SHA,
            rows=rows
            if "--pilot" in sys.argv
            else [f"pressure-rows/{q['draw']}-{q['row']}.json.gz" for q in rows],
            seconds=monotonic() - tick,
        ),
    )
