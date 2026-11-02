"""Application declarations and assessment; numerical calculations belong to Engine."""

import copy
import csv
import hashlib
import json
import math
import os
import tomllib
from pathlib import Path

import epcsaft
from epcsaft import equilibrium as eq, regression as reg


def jsonable(value):
    if isinstance(value, float) and not math.isfinite(value):
        return str(value)
    if value is None or isinstance(value, (str, bool, int, float)):
        return value
    if isinstance(value, dict):
        return {str(k): jsonable(v) for k, v in value.items()}
    if hasattr(value, "name"):
        return value.name
    return [jsonable(v) for v in value]


class SolventSpecification:
    def __init__(self, path, parameter="endpoint"):
        self.path = Path(path)
        self.spec = tomllib.loads(self.path.read_text())
        if self.spec["schema"] != "solvent-specification-1":
            raise ValueError("Unsupported solvent specification")
        shared = self.spec["declarations"]
        data = (self.path.parent / shared["path"]).read_bytes()
        if hashlib.sha256(data).hexdigest() != shared["sha256"]:
            raise ValueError("Declaration hash mismatch")
        self.spec.update(tomllib.loads(data.decode()))
        self.inputs = {key: self.load_record(self.spec[key]) for key in ("start", "endpoint", "coordinates", "caloric")}
        self.parameters = epcsaft.Parameters.from_mapping(self.inputs[parameter])
        self.parameter_sha256 = self.spec[parameter]["sha256"]
        self.problems = {}
        self.construction_parameters = {self.parameter_sha256: self.parameters}
        self.continuation = {}
        self.inputs["observations"] = {
            "fitted": [],
            "comparisons": [],
            "phase_states": self.load_record(self.spec["phase_states"]),
        }
        for dataset in self.spec["datasets"]:
            document = dataset.get("observation_parameters", self.spec[parameter])
            if document["sha256"] not in self.construction_parameters:
                self.construction_parameters[document["sha256"]] = epcsaft.Parameters.from_mapping(self.load_record(document))
            for source in self.load_record(dataset):
                row = {key: float(source[column]) for key, column in dataset["columns"].items()}
                if any(row[key] < bounds[0] or row[key] > bounds[1] for key, bounds in dataset["filter"].items()):
                    continue
                record = dict(
                    observation_parameters=document["sha256"],
                    continuation=dataset.get("continuation"),
                    state_identity=dataset.get("state_identity"),
                    identity=source["identity"],
                    observation_order=row["observation_order"],
                    group=dataset["group"],
                    row=json.loads(source["source"]),
                    weight=self.bind(dataset["weight"], row),
                    constructor=dataset["constructor"],
                    arguments=self.bind(dataset["arguments"], row),
                    kind=dataset["kind"],
                    temperature_domain=dataset["temperature_domain"],
                )
                names = (
                    ("problem",)
                    if record["constructor"] == "observation"
                    else ("initial", "bubble" if "bubble" in dataset else "final")
                )
                for name in names:
                    template = dataset["template"] if name == "problem" else dataset[name]
                    key = source["identity"] + ":" + name
                    self.problems[key] = self.problem(template, row)
                    record[name] = key
                target = "fitted" if dataset["role"] == "calibration" else "comparisons"
                self.inputs["observations"][target].append(record)
        for key in ("fitted", "comparisons"):
            self.inputs["observations"][key].sort(key=lambda r: r["observation_order"])
        for record in self.inputs["observations"]["phase_states"]:
            key = record["identity"] + ":phase"
            row = {k: float(record[k]) for k in ("T", "P", "water", "alpha", "amine")}
            self.problems[key] = self.problem(record["template"], row)
            record["problem"] = key
        thermal = self.inputs["caloric"]
        intervals = []
        for cid in self.parameters.component_ids:
            source = thermal["components"].get(cid)
            if source is None:
                intervals.append([])
                continue
            if source["representation"] == "cp_polynomial":
                form = epcsaft.IdealPolynomial(source["coefficients"], source["enthalpy_entropy_anchor_k"],
                                               source["enthalpy_anchor_j_per_mol"], source["entropy_anchor_j_per_mol_k"])
            elif source["representation"] == "shomate":
                form = epcsaft.IdealShomate(source["coefficients"], source["formation_enthalpy_j_per_mol"])
            else:
                raise ValueError("Unsupported caloric declaration")
            intervals.append(
                [
                    epcsaft.IdealInterval(
                        *source["range_k"], True, True, epcsaft.IdealCorrelation(form, thermal["reference_pressure_pa"])
                    )
                ]
            )
        self.thermal = epcsaft.ThermochemistryRecord(thermal["reference_pressure_pa"], intervals)
        self.model = epcsaft.Mixture(self.parameters, thermochemistry=self.thermal)
        self.continue_groups()

    def continue_groups(self):
        groups = {}
        for record in self.inputs["observations"]["fitted"]:
            if record.get("continuation"):
                groups.setdefault(record["continuation"]["group"], []).append(record)
        self.continuation = {}
        for records in groups.values():
            records = sorted(records, key=lambda r: r["continuation"]["order"])
            if len({r["continuation"]["order"] for r in records}) != len(records):
                raise ValueError("Duplicate continuation order")
            first = self.problems[records[0]["problem"]]
            signature = lambda p: [
                (q.name, q.kind, q.support, type(q.amount).__name__,
                 getattr(q.amount, "value", None), getattr(q.amount, "guess", None))
                for q in p.phases]
            previous, predecessor, failure = None, None, None
            for record in records:
                problem = self.problems[record["problem"]]
                if (record["observation_parameters"] != records[0]["observation_parameters"]
                        or isinstance(problem.T, eq.Free) or problem.T != first.T
                        or signature(problem) != signature(first)):
                    raise ValueError("Conflicting continuation declarations")
                evidence = dict(predecessor=predecessor, observation_parameters=record["observation_parameters"])
                self.continuation[record["identity"]] = evidence
                if failure is not None:
                    evidence.update(status="DependentUnavailable", cause=failure)
                    continue
                try:
                    if not isinstance(problem.P, eq.Free):
                        raise ValueError("Continuation requires free pressure")
                    if previous is not None:
                        problem.P = eq.Free(previous.pressure)
                        for i, phase in enumerate(problem.phases):
                            phase.composition_guess = {
                                cid: previous.mole_fractions[
                                    i * len(self.model.component_ids) + self.model.component_ids.index(cid)]
                                for cid in phase.support}
                            phase.packing_guess = previous.packing_fractions[i]
                    evidence["incoming"] = jsonable(dict(
                        pressure=problem.P.guess,
                        phases=[dict(name=q.name, composition=q.composition_guess, packing=q.packing_guess)
                                for q in problem.phases]))
                    model = epcsaft.Mixture(self.construction_parameters[record["observation_parameters"]], thermochemistry=self.thermal)
                    state = eq.solve_equilibrium(model, problem)
                    evidence.update({k: jsonable(getattr(state, k)) for k in (
                        "success", "message", "residuals", "pressure", "mole_fractions",
                        "packing_fractions", "requested_tolerance_met")})
                    quantities = [state.pressure, *state.residuals, *state.mole_fractions, *state.packing_fractions]
                    if (not state.success or not state.requested_tolerance_met or not state.residuals
                            or max(map(abs, state.residuals)) > problem.row_tolerance
                            or len(state.mole_fractions) != len(problem.phases) * len(model.component_ids)
                            or len(state.packing_fractions) != len(problem.phases)
                            or not all(math.isfinite(v) for v in quantities)):
                        raise ValueError("Continuation unavailable: " + state.message)
                    evidence["status"] = "Available"
                    previous, predecessor = state, record["identity"]
                except Exception as error:
                    failure = dict(evidence, target=record["identity"], exception=type(error).__name__, exception_message=str(error))
                    evidence.update(status="ContinuationUnavailable", cause=failure)

    def species_mapping(self, reactions):
        species = {}
        for component in self.inputs["endpoint"]["components"]:
            cid = component["component_id"]
            formula = self.spec["element_formulas"][cid]
            fixed = component["fixed"]
            if formula["charge"] != fixed["charge_number"]["value"]["magnitude"]:
                raise ValueError(f"Formula charge differs from Engine: {cid}")
            coverage = "ideal_gas_record" if cid in self.inputs["caloric"]["components"] else "reaction_reference_completion"
            if coverage == "reaction_reference_completion" and not any(
                cid in r["stoichiometry"] for g in reactions.values() for r in g
            ):
                raise ValueError(f"Missing caloric coverage: {cid}")
            species[cid] = dict(
                caloric_coverage=coverage,
                analytical_components=self.spec["analytical_components"][cid],
                component_id=cid, aliases=component.get("aliases", []), element_formula=formula,
                **{key: fixed[key] for key in ("charge_number", "molar_mass")},
                phase_supports={name: [p["name"] for p in t["phases"] if cid in p["support"]]
                                for name, t in self.spec["templates"].items()},
                analytical_feed_templates=[name for name, t in self.spec["templates"].items()
                                           if cid in t["feed"]["values"]],
            )
        quantities = set().union(*(r["element_formula"] for r in species.values()))
        for group in reactions.values():
            for reaction in group:
                for quantity in quantities:
                    total = sum(n * species[cid]["element_formula"].get(quantity, 0)
                                for cid, n in reaction["stoichiometry"].items())
                    if total != 0:
                        raise ValueError(f"Unbalanced {quantity}: {reaction['name']}: {total}")
        return species

    def load_record(self, record):
        path = self.path.parent / record["path"]
        data = path.read_bytes()
        if hashlib.sha256(data).hexdigest() != record["sha256"]:
            raise ValueError(f"Input hash mismatch: {path}")
        return list(csv.DictReader(data.decode().splitlines())) if path.suffix == ".csv" else json.loads(data)

    def bind(self, value, row):
        if isinstance(value, str) and value.startswith("$"):
            return row[value[1:]]
        if isinstance(value, dict):
            return {k: self.bind(v, row) for k, v in value.items()}
        if isinstance(value, list):
            return [self.bind(v, row) for v in value]
        return value

    def problem(self, template, row):
        declaration = self.bind(self.spec["templates"][template], row)
        if "reaction_set" in declaration:
            reactions = copy.deepcopy(self.spec["chemistry"]["reactions"][declaration.pop("reaction_set")])
            for reaction in reactions:
                reaction["correlation"] = eq.ReactionLogPolynomial(**reaction["correlation"])
            declaration["reactions"] = reactions
        if "neutral_reference" in declaration:
            declaration["neutral_reference"] = self.spec["chemistry"]["neutral_references"][
                declaration["neutral_reference"]
            ]
        return eq.problem_from_mapping(declaration)

    def observation(self, record):
        parameters = self.construction_parameters[record["observation_parameters"]]
        args = record["arguments"]
        constructor = record["constructor"]
        if constructor == "observation":
            return reg.observation(parameters, record["kind"], self.problems[record["problem"]], **args)
        if constructor == "addition_enthalpy":
            return reg.addition_enthalpy(
                parameters, self.problems[record["initial"]], self.problems[record["final"]], **args
            )
        if constructor == "saturation_capped_addition_enthalpy":
            return reg.saturation_capped_addition_enthalpy(
                parameters, self.problems[record["initial"]], self.problems[record["bubble"]], **args
            )
        raise ValueError(f"Unsupported observation constructor: {constructor}")

    def prediction(self, record):
        domain = record["temperature_domain"]
        problem = self.problems[record.get("problem", record.get("initial"))]
        continuation = self.continuation.get(record["identity"], {})
        if continuation.get("status", "Available") != "Available":
            return dict(identity=record["identity"], group=record["group"], **continuation)
        if not isinstance(problem.T, eq.Free) and not domain[0] <= problem.T <= domain[1]:
            return dict(
                identity=record["identity"],
                group=record["group"],
                status="OutsideDeclaredDomain",
                message="Temperature outside declared assessment domain",
                value=None,
                observed=record["arguments"]["observed"],
                row=record["row"],
            )
        try:
            prediction = reg.predict(self.model, self.observation(record))
            if prediction.status.name == "Available" and not all(math.isfinite(v) for v in (prediction.value, prediction.residual)):
                raise ValueError(f"Nonfinite native prediction: {prediction.value}, {prediction.residual}; {prediction.message}")
            return dict(
                identity=record["identity"],
                group=record["group"],
                row=record["row"],
                observed=record["arguments"]["observed"],
                convergence=None if prediction.convergence is None else {
                    k: jsonable(getattr(prediction.convergence, k))
                    for k in ("residual", "floor", "amplification", "contraction", "iterations", "stop")},
                **{k: jsonable(getattr(prediction, k, None)) for k in ("saturation_loading", "endpoint_loading")},
                optional_field_unavailability={k: "Not exposed by the installed Engine prediction"
                                               for k in ("saturation_loading", "endpoint_loading") if not hasattr(prediction, k)},
                **{
                    key: jsonable(getattr(prediction, key))
                    for key in (
                        "status",
                        "message",
                        "value",
                        "residual",
                        "requested_tolerance_met",
                        "branch",
                        "stable_root_count",
                    )
                },
            )
        except Exception as error:
            return dict(identity=record["identity"], group=record["group"], status="Exception", exception=type(error).__name__, message=str(error))

    def coordinates(self):
        coordinates = []
        for q in self.inputs["coordinates"]:
            kind = q.get("kind", "parameter")
            options = {key: q[key] for key in ("origin", "scale", "bounds")}
            if kind == "reaction_coordinate":
                coordinate = reg.reaction_coordinate(q["name"], q["coefficient"], **options)
            elif kind == "reaction_enthalpy_shift":
                coordinate = reg.reaction_enthalpy_shift(q["name"], pivot_temperature=q["pivot_temperature"], **options)
            elif kind == "parameter":
                targets = [(f, tuple(t) if isinstance(t, list) else t, m) for f, t, m in q["targets"]]
                coordinate = reg.coordinate(self.parameters, targets, **options)
            else:
                raise ValueError(f"Unsupported coordinate kind: {kind}")
            coordinates.append(coordinate)
        return coordinates

    def fitted_reactions(self, chart):
        reactions = copy.deepcopy(self.spec["chemistry"]["reactions"])
        source_coordinates = [
            q for q in self.inputs["coordinates"] if q.get("kind") in ("reaction_coordinate", "reaction_enthalpy_shift")
        ]
        assigned = {}
        # EvaluatedCoordinates: native reaction rows follow EOS and held-diameter rows.
        for q, value in zip(source_coordinates, chart.physical[len(chart.active) :], strict=True):
            if q["kind"] == "reaction_coordinate":
                assigned.setdefault(q["name"], {})[q["coefficient"]] = value
        # Completed laws carry one observation's domain; each destination keeps its own bounds.
        fields = ("a", "b", "c", "d", "e", "f", "reference_temperature")
        for group in reactions.values():
            for reaction in group:
                reaction["correlation"].update(assigned.get(reaction["name"], {}))
                if reaction["name"] in chart.reaction_laws:
                    law = chart.reaction_laws[reaction["name"]]
                    if law.standard_state_id != reaction["correlation"]["standard_state_id"]:
                        raise ValueError(f"Standard-state mismatch for fitted reaction {reaction['name']}")
                    reaction["correlation"].update({key: getattr(law, key) for key in fields})
        return reactions

    def fit(self):
        coords = self.coordinates()
        records = self.inputs["observations"]["fitted"]
        controls = reg.FitControls(**self.spec["optimizer"], workers=os.cpu_count())
        result = reg.fit(
            self.parameters,
            coords,
            [self.observation(r) for r in records],
            weights=[r["weight"] for r in records],
            thermochemistry=self.thermal,
            controls=controls,
            singular_vectors=True,
        )
        report = {
            key: jsonable(getattr(result, key))
            for key in (
                "status",
                "message",
                "usable",
                "initial_cost",
                "final_cost",
                "physical",
                "optimizer",
                "predictions",
                "residuals",
                "weighted_residuals",
                "iterations",
                "iteration_costs",
                "iteration_seconds",
                "trial_failures",
                "residual_evaluations",
                "jacobian_evaluations",
            )
        }
        report["reactions"] = self.fitted_reactions(result.chart)
        report["covariance"] = {
            key: jsonable(getattr(result.covariance, key))
            for key in (
                "status",
                "rank",
                "singular_values",
                "active_bounds",
                "projected_gradient_norm",
                "right_vectors",
            )
        }
        report["failures"] = [
            dict(trial=f.trial, observation=f.observation, status=f.status.name, message=f.message, jacobian=f.jacobian)
            for f in result.failures
        ]
        return result, report, reg.fitted_parameters(self.parameters, result)

    def phase(self, record, policy):
        if record["endpoint_sha256"] != self.parameter_sha256:
            raise ValueError("Phase inputs are bound to another parameter endpoint")
        prob = self.problems[record["problem"]]
        try:
            state = eq.solve_equilibrium(self.model, prob)
            support = list(prob.phases[0].support)
            if prob.feed.values.get(policy["carbon_component"], 0.0) == 0.0:
                support = [c for c in support if c not in policy["carbon_species"]]
            neutral = [c for c in policy["neutral_species"] if c in support]
            trials = copy.copy(prob)
            trials.phases = [
                eq.Phase("trial-0", kind="liquid", support=support),
                eq.Phase("trial-1", kind="vapor", support=neutral),
            ]
            options = eq.StabilityOptions()
            options.trials = trials._native(self.model).phases
            native = eq.stability_test(eq.compile_problem(self.model, prob), state, options)
            report = {k: jsonable(getattr(native, k)) for k in ("completed", "message", "present_phases", "work")}
            report["trials"] = []
            dense, gas, ambiguous, unresolved, reconstruction = [], [], [], [], []
            for t in native.trials:
                row = dict(
                    seed=t.seed,
                    evidence=t.evidence,
                    message=t.message,
                    resolved_descent=t.resolved_descent,
                    quantities=jsonable(t.quantities),
                    split_coordinates=[v if math.isfinite(v) else str(v) for v in t.split_coordinates],
                    phase=dict(kind=t.phase.kind.name.lower(), support=list(t.phase.support)),
                )
                report["trials"].append(row)
                if t.resolved_descent:
                    if not t.split_coordinates or not math.isfinite(t.split_coordinates[-1]):
                        row["classification_unavailable"] = "Missing or nonfinite logarithmic packing fraction"
                        unresolved.append(row)
                        continue
                    eta = math.exp(t.split_coordinates[-1])
                    row["packing_fraction"] = eta
                    (dense if eta >= policy["packing_fraction_threshold"] else gas).append(t.seed)
                    if policy["ambiguity_interval"][0] < eta < policy["ambiguity_interval"][1]:
                        ambiguous.append(t.seed)
                if t.evidence in ("unresolved", "indeterminate", "negative_plane_without_positive_donor"):
                    unresolved.append(row)
                    if t.message.endswith("reconstruction destroys support"):
                        reconstruction.append(row)
            if not native.completed or not state.requested_tolerance_met:
                unresolved.append(dict(message=state.message))
            native_count = int(native.message.split("unresolved trials ")[1].split(";")[0])
            if native_count != sum(
                t.evidence in ("unresolved", "indeterminate", "negative_plane_without_positive_donor")
                for t in native.trials
            ):
                unresolved.append(dict(message="Unresolved count mismatch"))
            return dict(
                identity=record["identity"],
                problem=record["problem"],
                requested_tolerance_met=state.requested_tolerance_met,
                residuals=list(state.residuals),
                amounts=list(state.amounts),
                mole_fractions=list(state.mole_fractions),
                stability=report,
                dense=dense,
                gas=gas,
                ambiguous=ambiguous,
                unresolved=unresolved,
                reconstruction=reconstruction,
            )
        except Exception as error:
            return dict(identity=record["identity"], unresolved=[dict(cause=type(error).__name__, message=str(error))])


def relative_error_statistic(records):
    if not records or any(
        r["status"] != "Available" or not r["observed"] or not math.isfinite(r["value"]) for r in records
    ):
        return None
    return 100 * sum(abs(r["value"] / r["observed"] - 1) for r in records) / len(records)
