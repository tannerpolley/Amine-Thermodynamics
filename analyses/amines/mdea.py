"""Fixed-reference MDEA reported declarations."""

from collections import Counter

from .model import CAMPAIGN_ARCHIVE, P_REF, REPORTED, ROOT, Route

DECLARATION = ROOT / "analyses/mdea_mea_workflow/inputs/bounded-binary-411.json"
KURANOV_LOG_SCALE = 0.015


class MDEAWeights(Route):
    def bind(self, point):
        spec = super().bind(point)
        rows = spec.inputs["observations"]["fitted"]
        group_counts = Counter(row["group"] for row in rows)
        assert "measurement_covariance" not in spec.spec
        for row in rows:
            group = row["group"]
            row["weight"] = 1 / group_counts[group]
            if group == "Kuranov":
                assert row["arguments"]["form"] == "log_ratio"
                row["weight"] /= KURANOV_LOG_SCALE**2
        return spec


FIT_SETS = {
    "system-pressure": dict(
        route=MDEAWeights,
        declaration=DECLARATION,
        reference_pressure_pa=None,
        archive=CAMPAIGN_ARCHIVE,
        endpoint=REPORTED / "MDEA/manifest.json.gz",
        endpoint_keys=("prior_declaration",),
        reference=REPORTED / "MDEA/reference-control.json.gz",
        reference_keys=("tracking",),
    ),
    "reported": dict(
        route=MDEAWeights,
        declaration=DECLARATION,
        retained=REPORTED / "MDEA",
        reference_pressure_pa=P_REF,
        maximum_seconds=10980,
        replay_tolerance=1e-8,
    ),
    "slope-bound": dict(
        route=MDEAWeights,
        declaration=DECLARATION,
        retained=REPORTED / "MDEA_slope_bound",
        reference_pressure_pa=P_REF,
        bound_rule="k_bound",
    ),
}

REPORTED_SET = "reported"
