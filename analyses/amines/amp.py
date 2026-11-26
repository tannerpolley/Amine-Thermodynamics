"""Fixed-reference AMP reported declarations."""

from .model import CAMPAIGN_ARCHIVE, P_REF, REPORTED, ROOT, Route

DECLARATION = ROOT / "analyses/amp_transfer/inputs/retransfer-344/phase-2/AMP-05e94210.json"
ADDED = {"tong", "hartono-2021-supplemental"}
LOADED = "loaded-pressure"


class ExpandedPressure(Route):
    def bind(self, point):
        spec = super().bind(point)
        observations = spec.inputs["observations"]
        fitted, outside = (observations[role] for role in ("fitted", "comparisons"))
        added = [r for r in outside if r["group"] in ADDED]
        original = [r for r in fitted if r["group"] == LOADED]
        assert all(r["arguments"]["form"] == "log_ratio" and r["unit"] == "Pa" for r in original + added)
        (coefficient,) = {r["weight"] for r in original}
        for r in original + added:
            r.update(
                weight=coefficient * len(original) / (len(original) + len(added)),
                role="fitted",
            )
        fitted.extend(added)
        observations["comparisons"] = [r for r in outside if r["group"] not in ADDED]
        return spec


FIT_SETS = {
    "system-pressure": dict(
        route=ExpandedPressure,
        declaration=DECLARATION,
        reference_pressure_pa=None,
        archive=CAMPAIGN_ARCHIVE,
        endpoint=REPORTED / "AMP_free/manifest.json.gz",
        endpoint_keys=("prior_declaration",),
        reference=REPORTED / "AMP_free/reference-control.json.gz",
        reference_keys=("tracking",),
    ),
    "system-pressure-fixed-slope": dict(
        route=ExpandedPressure,
        declaration=DECLARATION,
        reference_pressure_pa=None,
        archive=CAMPAIGN_ARCHIVE,
        endpoint=REPORTED / "AMP_fixed/manifest.json.gz",
        endpoint_keys=("prior_declaration",),
        reference=REPORTED / "AMP_fixed/reference-control.json.gz",
        reference_keys=("tracking",),
    ),
    "reported": dict(
        route=ExpandedPressure,
        declaration=DECLARATION,
        retained=REPORTED / "AMP_free",
        reference_pressure_pa=P_REF,
        maximum_seconds=6750,
        replay_tolerance=1e-8,
    ),
    "fixed-slope": dict(
        route=ExpandedPressure,
        declaration=DECLARATION,
        retained=REPORTED / "AMP_fixed",
        reference_pressure_pa=P_REF,
        maximum_seconds=6750,
        replay_tolerance=1e-8,
    ),
}
