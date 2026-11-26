"""Bind reported declarations and evaluate the declared rows."""

import copy
import dataclasses
import hashlib
import json
import math
from pathlib import Path

from .wheel import ROOT, verify

verify()

import epcsaft  # noqa: E402
from MEA.solvent_specification import SolventSpecification  # noqa: E402

REPORTED = ROOT / "analyses/fixed_reaction_reference/results"
P_REF = 100_000.0
MODEL_RUNTIME_DEFAULTS = {"c_shell": 1.0, "c_dielectric": 1.0}


def parameter_mapping(path: Path) -> dict[str, object]:
    mapping = json.loads(path.read_text(encoding="utf-8"))
    for family in mapping.get("model_families", ()):
        if family.get("kind") == "electrolyte" and family.get("choice") == "born":
            for key, value in MODEL_RUNTIME_DEFAULTS.items():
                family.setdefault(key, value)
    return mapping


def _identified(node: object):
    """Yield every ``{"identity", "value": {"magnitude"}}`` coefficient node."""
    if isinstance(node, dict):
        value = node.get("value")
        if isinstance(node.get("identity"), str) and isinstance(value, dict) and "magnitude" in value:
            yield node
        for child in node.values():
            yield from _identified(child)
    elif isinstance(node, list):
        for child in node:
            yield from _identified(child)


def parameter_values(mapping: dict[str, object]) -> dict[str, float]:
    """Identified coefficient magnitudes in their record units."""
    return {node["identity"]: float(node["value"]["magnitude"]) for node in _identified(mapping)}


def with_parameter_values(mapping: dict[str, object], values: dict[str, float]) -> dict[str, object]:
    """Copy of ``mapping`` with the named coefficient magnitudes replaced."""
    updated = copy.deepcopy(mapping)
    found = set()
    for node in _identified(updated):
        if node["identity"] in values:
            node["value"]["magnitude"] = values[node["identity"]]
            found.add(node["identity"])
    if missing := set(values) - found:
        raise KeyError(f"unknown parameter identities: {sorted(missing)}")
    return updated


def target_identity(mapping, family, target):
    if family == "temperature_law_coefficient":
        return target
    return next(
        c["identity"]
        for block in (mapping["components"] if isinstance(target, str) else mapping["pairs"])
        if (
            block.get("component_id") == target
            if isinstance(target, str)
            else {block["component_id_a"], block["component_id_b"]} == set(target)
        )
        for c in block["coefficients"]
        if c["family"] == family
    )


def calculation_declaration(value):
    if dataclasses.is_dataclass(value):
        return {f.name: calculation_declaration(getattr(value, f.name)) for f in dataclasses.fields(value)}
    if isinstance(value, dict):
        return {k: calculation_declaration(v) for k, v in value.items()}
    if isinstance(value, (list, tuple)):
        return [calculation_declaration(v) for v in value]
    if hasattr(value, "name") and hasattr(value, "value"):
        return value.name
    if type(value).__module__.startswith("epcsaft"):
        return {
            k: calculation_declaration(getattr(value, k))
            for k in dir(value)
            if not k.startswith("_") and not callable(getattr(value, k))
        }
    return value


class Route:
    def __init__(self, declaration, *, reference_pressure_pa):
        verify()
        self.path = Path(declaration).resolve()
        self.config = json.loads(self.path.read_text())
        self.fixed_reference_pressure_pa = reference_pressure_pa

    def load(self, reference):
        path = self.path.parent / reference["path"]
        assert hashlib.sha256(path.read_bytes()).hexdigest() == reference["sha256"], path
        return json.loads(path.read_text())

    def bind(self, point):
        datasets = self.load(self.config["dataset_changes"]) if "dataset_changes" in self.config else {}
        interval = self.config["calculation_interval_K"]
        reactions = copy.deepcopy(point["reactions"])
        for group in reactions.values():
            for reaction in group:
                reaction["correlation"].update(temperature_min=interval[0], temperature_max=interval[1])
        datasets.update(
            reactions=reactions,
            reaction_reference_pressure_pa=self.fixed_reference_pressure_pa,
        )
        spec = SolventSpecification(self.path.parent / self.config["specification"], **datasets)
        spec.parameters = epcsaft.Parameters.from_mapping(point["parameters"])
        spec.model = epcsaft.Mixture(spec.parameters, thermochemistry=spec.thermal)
        assert list(spec.parameters.component_ids) == self.config["species"]
        spec.inputs["endpoint"] = point
        spec.construction_parameters = {k: spec.parameters for k in spec.construction_parameters}
        for problem in spec.problems.values():
            assert interval[0] <= problem.T <= interval[1], problem.T
        for role in ("fitted", "comparisons"):
            for row in spec.inputs["observations"][role]:
                row["temperature_domain"] = interval
                row["role"] = row.get(
                    "role",
                    self.config.get("roles", {}).get(row["group"], "fitted" if role == "fitted" else "not fitted"),
                )
                assert row["role"] in ("fitted", "not fitted", "comparison only")
                assert (row["role"] == "fitted") == (role == "fitted")
        spec.inputs["coordinates"] = copy.deepcopy(point["coordinates"])
        if "covariance" in self.config:
            covariance = self.load(self.config["covariance"])
            rows = spec.inputs["observations"]["fitted"]
            assert covariance["identities"] == [r["identity"] for r in rows]
            if any(
                r["arguments"]["form"] != "difference" or r["weight"] != 1 or r["arguments"]["scale"] != 1 for r in rows
            ):
                raise ValueError("Covariance uses raw difference observations")
            spec.spec["measurement_covariance"] = covariance["covariance"]
        return spec

    def endpoint_mapping(self, start, report, declared):
        point, values = copy.deepcopy(start), iter(report["physical"])
        for coordinate, optimizer in zip(point["coordinates"], report["optimizer"], strict=True):
            coordinate["origin"] += coordinate["scale"] * optimizer
            if coordinate.get("kind") == "reaction_enthalpy_shift":
                shift = coordinate["origin"]
                coordinate["bounds"] = [v - shift for v in coordinate["bounds"]]
                coordinate["origin"] = 0.0
        updates = {}
        for q in declared:
            for family, target, factor in q.get("targets", []):
                identity = target_identity(start["parameters"], family, target)
                updates[identity] = next(values)
        point["parameters"] = with_parameter_values(start["parameters"], updates)
        point["reactions"] = report["reactions"]
        for coordinate in point["coordinates"]:
            if coordinate.get("kind") == "reaction_coordinate":
                law = next(
                    r["correlation"]
                    for group in point["reactions"].values()
                    for r in group
                    if r["name"] == coordinate["name"]
                )
                origin = law.get(coordinate["coefficient"], 0.0)
                # Transport only the completion offset, not the fitted displacement.
                delta = origin - coordinate["origin"]
                coordinate["bounds"] = [v + delta for v in coordinate["bounds"]]
                coordinate["origin"] = origin
        return point


def row_manifest(spec):
    fields = ("problem", "initial", "final", "bubble")
    return {
        role: [
            dict(
                row,
                states={field: calculation_declaration(spec.problems[row[field]]) for field in fields if field in row},
            )
            for row in spec.inputs["observations"][role]
        ]
        for role in ("fitted", "comparisons")
    }


def replay(spec):
    records = spec.inputs["observations"]["fitted"]
    rows = evaluate(spec, records)
    return dict(
        rows=rows,
        attempted=len(rows),
        refused=sum("cost" not in row for row in rows),
        cost=math.fsum(row["cost"] for row in rows) if all("cost" in row for row in rows) else None,
    )


def evaluate(spec, records):
    values = [spec.prediction(r) for r in records]
    for r, v in zip(records, values, strict=True):
        if v["status"] == "Available" and v["requested_tolerance_met"]:
            v["weighted_residual"] = math.sqrt(r["weight"]) * v["residual"]
            v["cost"] = 0.5 * v["weighted_residual"] ** 2
    return values
