"""Construct the stability feed from the retained first pressure crossing and the source cap."""

from closure import HERE, c, point_for
from copy import copy
from scipy.optimize import brentq
from time import monotonic


def run():
    route, point = point_for("MDEA", "selected", "pressure-readback")
    spec = route.bind(point)
    for q in c.r.read(HERE / "controls.json.gz")["caps"]:
        tick = monotonic()
        r = next(
            x
            for x in spec.inputs["observations"]["comparisons"]
            if x["identity"] == q["key"]
        )
        p = c.reg.predict(spec.model, spec.observation(r))
        nodes = p.saturation.nodes
        lo, hi = next(
            (a, b)
            for a, b in zip(nodes, nodes[1:])
            if a.state.success and b.state.success and a.mismatch <= 0 < b.mismatch
        )
        bubble = copy(spec.problems[r["bubble"]])
        bubble.feed = copy(bubble.feed)
        stock = dict(bubble.feed.values)
        target = r["arguments"]["P"]
        history = []

        def residual(loading):
            bubble.feed.values = stock | {"carbon-dioxide": loading}
            s = c.refit.eq.solve_equilibrium(spec.model, bubble, lo.state)
            history.append(
                dict(
                    loading=loading,
                    message=s.message,
                    pressure=s.pressure if s.success else None,
                )
            )
            if not s.success or not s.requested_tolerance_met:
                raise ValueError(s.message)
            return s.pressure - target

        out = dict(
            key=q["key"], bracket=[lo.loading, hi.loading], P=target, nodes=history
        )
        try:
            root = brentq(residual, lo.loading, hi.loading, xtol=1e-14)
            out["pressure_residual_Pa"] = residual(root)
            out["root"] = root
            alpha = min(root, r["arguments"]["loading_cap"])
            out["loading"] = alpha
            state = dict(
                T=bubble.T,
                stock={k: v for k, v in stock.items() if k != "carbon-dioxide" and v},
                a=alpha,
            )
            item = route.stability_row(spec, state, 1.0)
            item.pressure_reference = None
            item.problem.pressure = type(item.problem.pressure).fixed(target)
            pred = c.reg.predict(spec.model, item)
            out["native_search"] = dict(status=pred.status.name, message=pred.message)
        except (ValueError, RuntimeError) as e:
            out["error"] = str(e)
        yield dict(out, seconds=monotonic() - tick)


if __name__ == "__main__":
    tick = monotonic()
    c.refit.save(
        HERE / "cap.json.gz",
        dict(wheel=c.r.SHA, rows=list(run()), seconds=monotonic() - tick),
    )
