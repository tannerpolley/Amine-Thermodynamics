"""Repeat the two old-vector derivative checks using the retained pressure reclosure."""

from closure import HERE, c
import reference_derivatives as rd
from time import monotonic


def run():
    baseline = c.r.read(rd.R8)["rows"]
    for design in ("MEA", "DEA"):
        tick = monotonic()
        route, point, _ = c.refit.configured(design, "C1")
        spec = route.bind(point)
        old = baseline[design]["value"]
        result = rd.worked_state(
            spec, spec.model, spec.thermal, old["observation"], old["amine_feed_mol"]
        )
        c.refit.save(
            HERE / f"derivatives-{design}.json.gz",
            dict(wheel=c.r.SHA, seconds=monotonic() - tick, **result),
        )


if __name__ == "__main__":
    run()
