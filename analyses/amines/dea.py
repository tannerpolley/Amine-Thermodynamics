"""Fixed-reference DEA reported declarations."""

import math

from .model import P_REF, REPORTED, ROOT, Route

DECLARATION = ROOT / "analyses/dea_transfer/inputs/part-ii-346/f2-carbamate-413-route.json"
PRESSURE = {"Lawson", "SeoHong", "Lal"}
PRESSURE_LOG_SCALE = 0.09
LAL_MOLARITY_MOL_M3 = 2000
LAL_FEED_TOLERANCE = 1e-12


class ExpandedDEA(Route):
    def bind(self, point):
        spec = super().bind(point)
        observations = spec.inputs["observations"]
        fitted, comparisons = (observations[k] for k in ("fitted", "comparisons"))
        promoted = [row for row in comparisons if row["group"] in ("SeoHong", "Lal")]
        pressures = [row for row in fitted + promoted if row["group"] in PRESSURE]
        for row in pressures:
            assert row["kind"] == "partial_pressure" and row["arguments"]["form"] == "log_ratio"
            row.update(
                role="fitted",
                weight=1 / (len(pressures) * PRESSURE_LOG_SCALE**2),
            )
            if row["group"] == "Lal":
                p = spec.problems[row["problem"]]
                amounts = p.feed.values
                masses = {
                    c["component_id"]: c["fixed"]["molar_mass"]["value"]["magnitude"]
                    for c in point["parameters"]["components"]
                }
                w = (
                    masses["diethanolamine"]
                    * amounts["diethanolamine"]
                    / (masses["diethanolamine"] * amounts["diethanolamine"] + masses["water"] * amounts["water"])
                )
                rho = 1021 + (w - 0.20) * (1035 - 1021) / 0.10
                assert math.isclose(
                    w * rho,
                    LAL_MOLARITY_MOL_M3 * masses["diethanolamine"],
                    rel_tol=LAL_FEED_TOLERANCE,
                )
                assert row["arguments"]["observed"] == float(row["row"]["p_CO2_kPa"]) * 1000
        observations["fitted"].extend(promoted)
        observations["comparisons"] = [row for row in comparisons if row not in promoted]
        return spec


FIT_SETS = {
    "reported": dict(
        route=ExpandedDEA,
        declaration=DECLARATION,
        retained=REPORTED / "DEA",
        reference_pressure_pa=P_REF,
        maximum_seconds=1620,
        replay_tolerance=1e-8,
    ),
}
