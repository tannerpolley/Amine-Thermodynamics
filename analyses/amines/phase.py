"""Declared phase requests and classification of the existing search evidence."""

import copy
import json
import math

from .model import calculation_declaration
from .mea import MEARoute
from .wheel import verify

import epcsaft
from epcsaft import equilibrium as eq, regression as reg
from MEA.solvent_specification import jsonable, stability_payload, supplied_negative

LOWEST_LOADING = 1e-5
FINITE_NEGATIVE = "no descent in the finite search"


def capped_feed(spec, record, parent):
    """Follow the declared loading nodes to the first rising pressure bracket."""
    from scipy.optimize import brentq

    args = record["arguments"]
    bubble = copy.copy(spec.problems[record["bubble"]])
    initial = parent.feed.values
    direction = {c: args["basis_amount"] * args["feed"].get(c, 0.0) for c in initial}
    action = eq.SolvedStateActionDirection(0.0, 0.0, [direction.get(c, 0.0) for c in spec.parameters.component_ids], [])
    observable = eq.SolvedStateObservable(eq.SolvedStateObservableKind.Pressure)
    nodes = []

    def solve(loading, start):
        bubble.feed = eq.Amounts({c: n + loading * direction[c] for c, n in initial.items()})
        result = eq.solve_equilibrium(spec.model, bubble, start=start)
        if not result.requested_tolerance_met:
            raise ValueError(f"Saturation bracket at loading {loading}: {result.message}")
        return result

    previous, start = None, None
    for loading in args["loading_grid"]:
        result = solve(loading, start)
        compiled = eq.compile_problem(spec.model, bubble)
        (slope,) = eq.solved_state_first_actions(compiled, result, [observable], [action])[0].results
        if slope.status.name != "Available":
            raise ValueError(f"Saturation bracket slope at {loading}: {slope.status.name}")
        nodes.append(dict(loading=loading, pressure_Pa=result.pressure, slope_Pa=slope.action))
        if (
            previous is not None
            and previous["pressure_Pa"] <= args["P"] < result.pressure
            and min(previous["slope_Pa"], slope.action) > 0
        ):
            bracket = [previous["loading"], loading]

            def residual(a):
                return solve(a, start).pressure - args["P"]

            root = brentq(residual, *bracket, xtol=1e-14)
            capped = min(root, args["loading_cap"])
            parent.feed = eq.Amounts({c: n + capped * direction[c] for c, n in initial.items()})
            return dict(
                nodes=nodes,
                bracket=bracket,
                root=root,
                loading=capped,
                source_cap=args["loading_cap"],
                target_Pa=args["P"],
                pressure_residual_Pa=residual(root),
            )
        previous, start = nodes[-1], result
    raise ValueError(f"{record['identity']}: no positive-slope saturation bracket on declared loading grid")


def grid_states(stocks, loadings):
    """The liquid-parent grid at the declared stocks and loadings."""
    return [
        dict(
            key=f"grid:{stock}:{T}:{a}:{c}",
            T=round(313.15 + 10 * i, 2),
            stock=stock,
            a=a,
            c=c,
        )
        for stock in stocks
        for i in range(9)
        for T in [round(313.15 + 10 * i, 2)]
        for a in loadings
        for c in (1.05, 3.0)
    ]


def grid_axes(route, spec):
    """#337 rule (b) grid from the declared fitted stocks and data loadings: 0.1 mol/mol loading steps from 1e-5 to the
    largest data loading, and fitted concentrations within 1 wt% of the lowest of their group searched once, at that lowest."""
    loadings = route.config["loadings"]
    if not route.config["stocks"]:
        return [], []
    if loadings[0] != LOWEST_LOADING:
        raise ValueError("Part II grid declaration has a different minimum loading")
    top = loadings[-1]
    loadings = [LOWEST_LOADING] + [round(0.1 * k, 4) for k in range(1, math.ceil(top / 0.1 - 1e-9))] + [top]
    masses = {
        c["component_id"]: c["fixed"]["molar_mass"]["value"]["magnitude"]
        for c in epcsaft.parameters.document_mapping(spec.parameters)["components"]
    }
    amine = route.config["amine"]

    def weight(stock):
        return 100 * masses[amine] * stock[amine] / math.fsum(masses[c] * n for c, n in stock.items())

    stocks = []
    for stock in sorted(route.config["stocks"], key=weight):
        if not stocks or weight(stock) - weight(stocks[-1]) > 1.0:
            stocks.append(stock)
    return stocks, loadings


def states(route, spec):
    if isinstance(route, MEARoute):
        return route.phase_states()
    states = []
    for role in ("fitted", "comparisons"):
        for row in spec.inputs["observations"][role]:
            if row["constructor"] == "residual_excess_enthalpy":
                continue
            if row["constructor"] == "saturation_capped_addition_enthalpy":
                states.append(dict(key=row["identity"] + ":cap", cap_record=row["identity"]))
            for field in ("problem", "initial", "final", "bubble"):
                if field in row:
                    states.append(dict(key=row[field], problem=row[field]))
    states.extend(dict(key=r["problem"], problem=r["problem"]) for r in spec.inputs["observations"]["phase_states"])
    states.extend(grid_states(*grid_axes(route, spec)))
    return list({r["key"]: r for r in states}.values())


def stability_row(route, spec, state, scale, *, metadata=None, cap_from_prediction=False):
    if isinstance(route, MEARoute):
        return route.stability_row(spec, state, scale)
    if "cap_record" in state:
        record = next(
            r
            for role in ("fitted", "comparisons")
            for r in spec.inputs["observations"][role]
            if r["identity"] == state["cap_record"]
        )
        parent = copy.copy(spec.problems[record["initial"]])
        if cap_from_prediction:
            prediction = reg.predict(spec.model, spec.observation(record))
            if prediction.status.name != "Available":
                raise ValueError(prediction.message)
            args = record["arguments"]
            parent.feed = eq.Amounts({
                c: parent.feed.values.get(c, 0.0) + prediction.endpoint_loading * args["basis_amount"] * args["feed"].get(c, 0.0)
                for c in spec.parameters.component_ids
            })
            evidence = dict(loading=prediction.endpoint_loading)
        else:
            evidence = capped_feed(spec, record, parent)
        if metadata is not None:
            metadata["capped_feed"] = evidence
        bubble = None
    elif "binary_x" in state:
        water, amine = "water", route.config["amine"]
        feed = {water: 1 - state["binary_x"], amine: state["binary_x"]}
        parent = eq.Problem(
            T=state["T"],
            P=state["P"],
            feed=eq.Amounts(feed),
            phases=[eq.Phase("L", kind="liquid", support=list(feed))],
            row_tolerance=1e-10,
        )
        bubble = None
    elif "problem" in state:
        parent = copy.copy(spec.problems[state["problem"]])
        bubble = copy.copy(parent) if isinstance(parent.P, eq.Free) else None
        parent.phases = [copy.copy(parent.phases[0])]
        parent.phases[0].amount = eq.Free()
        parent.P = 1e5 if bubble is not None else parent.P
    else:
        template = next(p for p in spec.problems.values() if p.reactions)
        feed = dict(
            state["stock"],
            **{"carbon-dioxide": state["a"] * state["stock"][route.config["amine"]]},
        )
        parent = eq.Problem(
            T=state["T"],
            P=1e5,
            feed=eq.Amounts(feed),
            phases=[eq.Phase("L", kind="liquid", support=route.config["species"])],
            reactions=template.reactions,
            neutral_reference=template.neutral_reference,
            row_tolerance=template.row_tolerance,
        )
        bubble = copy.copy(parent)
        bubble.P = eq.Free(1e5)
        bubble.phases = list(parent.phases) + [
            eq.Phase(
                "V",
                kind="vapor",
                support=route.config["vapor_species"],
                amount=eq.Pinned(0.0),
            )
        ]
    if state.get("compressed"):
        bubble = copy.copy(parent)
        bubble.P = eq.Free(1e5)
        bubble.phases = list(parent.phases) + [
            eq.Phase(
                "V",
                kind="vapor",
                support=route.config["vapor_species"],
                amount=eq.Pinned(0.0),
            )
        ]
    item = reg.stability(
        spec.parameters,
        parent,
        scale=scale,
        **(dict(pressure_reference=bubble, pressure_ratio=state.get("c", 1.05)) if bubble else {}),
    )
    removed = set(eq.compile_problem(spec.model, item.problem).removed_species)
    if removed:
        # ponytail: remove when tannerpolley/epcsaft#24 excludes compiler-certified absent species.
        support = {i for i, v in enumerate(item.problem.feed.values) if v > 0}
        support.update(i for rx in item.problem.reactions for i, v in enumerate(rx.stoichiometry) if v != 0)
        support = sorted(support - removed)
        charges = {
            c["component_id"]: c["fixed"]["charge_number"]["value"]["magnitude"]
            for c in epcsaft.parameters.document_mapping(spec.parameters)["components"]
        }
        neutral = [i for i in support if charges[spec.parameters.component_ids[i]] == 0]
        trials = []
        for ids, kind in ((support, "Liquid"), (neutral, "Liquid"), (neutral, "Vapor")):
            phase = type(item.problem.phases[0])()
            phase.name, phase.kind, phase.support, phase.support_declared = (
                "feasible",
                getattr(type(phase.kind), kind),
                ids,
                True,
            )
            trials.append(phase)
        item.stability_options.trials = trials
    return item


def same_calculations(route, point, states):
    """Data-state key -> the first key whose search the Engine receives identically; grid keys differ by construction."""
    spec, first, same = route.bind(point), {}, {}
    for state in states:
        if state["key"].startswith("grid:"):
            continue
        try:
            item = stability_row(route, spec, state, 1.0)
        except Exception:
            continue  # measured on its own, where the refusal is recorded
        identity = json.dumps(
            calculation_declaration(
                [
                    item.problem,
                    item.pressure_reference,
                    item.pressure_ratio if item.pressure_reference is not None else None,
                    item.stability_options.trials,
                ]
            ),
            sort_keys=True,
        )
        same[state["key"]] = first.setdefault(identity, state["key"])
    return {key: source for key, source in same.items() if key != source}


class SuppliedTrials:
    """Evaluate retained trial compositions on the current liquid parent."""

    def __init__(self, spec, witnesses, *, compiled_support=True):
        self.spec = spec
        self.witnesses = witnesses
        self.compiled_support = compiled_support
        self.by_support = {}
        self.prepared = None

    def applicable(self, item, witnesses, support):
        phases, repeated, unique = [], [], {}
        for witness in witnesses:
            if not set(witness["support"]) <= support:
                continue
            kind = witness.get("kind", "Liquid" if len(witness["support"]) == len(self.spec.parameters.component_ids) else "Vapor")
            identity = (kind, tuple(witness["support"]), tuple(witness["composition"]), witness["packing"])
            i = unique.setdefault(identity, len(phases))
            repeated.append((i, witness))
            if i < len(phases):
                continue
            phase = type(item.problem.phases[0])()
            phase.name, phase.kind, phase.support_declared = "previous-split", getattr(type(phase.kind), kind), True
            phase.support, phase.composition_guess, phase.packing_guess = identity[1:]
            phases.append(phase)
        return phases, repeated, tuple(unique)

    def support(self, item):
        spec = self.spec
        if self.compiled_support:
            compiled = eq.compile_problem(spec.model, item.problem)
            return frozenset(range(len(spec.parameters.component_ids))) - set(compiled.removed_species)
        # The earlier screens offered all species present in the feed or reactions.
        return frozenset(i for i, amount in enumerate(item.problem.feed.values) if amount > 0) | frozenset(
            i for reaction in item.problem.reactions for i, value in enumerate(reaction.stoichiometry) if value
        )

    def evaluate(self, item, prediction, key):
        spec = self.spec
        support = self.support(item)
        if isinstance(self.witnesses, dict):
            witnesses = self.witnesses.get(key, ())
            phases, repeated, identities = self.applicable(item, witnesses, support)
        else:
            witnesses = self.witnesses
            if support not in self.by_support:
                self.by_support[support] = self.applicable(item, witnesses, support)
            phases, repeated, identities = self.by_support[support]
        if not witnesses:
            return {}
        excluded = len(witnesses) - len(repeated)
        if not phases:
            return dict(supplied_trial_counts=dict(available=0, unavailable=0, not_applicable=excluded))
        details = dict(supplied_available=False, supplied_minimum_tpd=None, supplied_trial_evidence=[])
        evaluated = 0
        try:
            parent = item.problem
            if prediction.pressure_reference is not None:
                parent.pressure = type(parent.pressure).fixed(prediction.pressure_reference.value * item.pressure_ratio)
            result = eq.solve_equilibrium(spec.model, parent)
            prepared_key = (parent.temperature.value, identities)
            if self.prepared is None or self.prepared[0] != prepared_key:
                self.prepared = prepared_key, eq.prepare_supplied_trials(spec.model, prepared_key[0], phases)
            options = eq.StabilityOptions()
            options.prepared_trials = self.prepared[1]
            report = eq.stability_test(eq.compile_problem(spec.model, parent), result, options)
            trials = [dict(evidence=t.evidence, resolved_descent=t.resolved_descent, quantities=jsonable(t.quantities), message=t.message)
                      for t in report.trials]
            pairs = ([(trials[i], witness) for i, witness in repeated] if len(trials) == len(phases)
                     else [(trial, None) for trial in trials])
            evaluated = sum(trial["evidence"] == "evaluated" for trial, _ in pairs)
            evidence = {}
            for trial, witness in pairs:
                if supplied_negative(trial):
                    side = trial["quantities"].get("density_side")
                    old = evidence.get(side)
                    if old is None or trial["quantities"]["tpd_over_rt"] < old["quantities"]["tpd_over_rt"]:
                        evidence[side] = dict(trial, phase=witness)
            details.update(
                supplied_parent_pressure_Pa=result.pressure,
                supplied_available=result.requested_tolerance_met and len(trials) == len(phases) and evaluated == len(repeated),
                supplied_minimum_tpd=min((trial["quantities"]["tpd_over_rt"] for trial, _ in pairs if trial["evidence"] == "evaluated"), default=None),
                supplied_trial_evidence=list(evidence.values()),
            )
        except (ValueError, RuntimeError, TypeError) as error:
            details["supplied_error"] = f"{type(error).__name__}: {error}"
        details["supplied_trial_counts"] = dict(available=evaluated, unavailable=len(repeated) - evaluated, not_applicable=excluded)
        return details


def native_search(route, spec, state, *, supplied=None, cap_from_prediction=False):
    wheel = verify()
    metadata = {}
    try:
        item = stability_row(route, spec, state, 1.0, metadata=metadata, cap_from_prediction=cap_from_prediction)
        prediction = reg.predict(spec.model, item)
        search = stability_payload(prediction)
        if prediction.stability is not None:
            search["witnesses"] = [
                dict(
                    resolved_descent=True,
                    kind=t.phase.kind.name,
                    density_side=t.quantities.get("density_side"),
                    support=list(t.phase.support),
                    composition=list(t.composition),
                    packing=math.exp(t.split_coordinates[-1]),
                )
                for t in prediction.stability.report.trials
                if t.resolved_descent and t.split_coordinates
            ]
        search["parent_kind"] = item.problem.phases[0].kind.name
        if supplied is not None:
            search["optimized_available"] = search["available"]
            search.update(supplied.evaluate(item, prediction, state["key"]))
            search["available"] &= search.get("supplied_available", True)
    except (ValueError, RuntimeError) as error:
        search = dict(
            status="Exception",
            message=f"{type(error).__name__}: {error}",
            available=False,
        )
    return dict(key=state["key"], wheel=wheel, search=search, **metadata)


def search_descent(search):
    value = search.get("value")
    optimized = search.get("optimized_available", search["available"]) and value is not None and value < 0
    minimum = search.get("supplied_minimum_tpd")
    return bool(optimized or (minimum is not None and minimum < 0)
                or any(map(supplied_negative, search.get("supplied_trials", ()))))


def search_class(search):
    if search_descent(search):
        return "descent"
    if not search["available"]:
        return "unavailable"
    if search.get("no_descent_in_trial_set"):
        return "searched, no instability"
    return "no resolved descent"


def census_class(row):
    """Classify the MEA census from the held parent and its Engine trials."""
    if "failure" in row:
        return "unavailable"
    state, reports = row.get("final"), row.get("stability", [])
    if any(t["resolved_descent"] for r in reports for t in r["trials"]) or any(
        supplied_negative(t) for r in reports for t in r.get("supplied_trials", [])
    ):
        return "failed"
    if state is None or not state["success"] or not state["requested_tolerance_met"]:
        return "failed"
    if "raw_residuals" in state and (
        max(map(abs, state["raw_residuals"]), default=0.0) > 1e-10
        or state["reduced_hessian_minimum"] < 0
        or any(v <= 0 for v in state["pressure_density_derivatives"])
        or any(v < 0 for v in state["amounts"])
    ):
        return "failed"
    if (
        any(t["evidence"] != "evaluated" for r in reports for t in r.get("supplied_trials", []))
        or len(reports) != 1 or not reports[0]["completed"] or not reports[0]["trials"]
        or {t["phase"]["kind"] for t in reports[0]["trials"]} != {"liquid", "vapor"}
        or any(not t["optimizer"]["success"]
               or t["evidence"] in ("unresolved", "indeterminate", "negative_plane_without_positive_donor")
               for t in reports[0]["trials"])
        or "raw_residuals" not in state or row.get("bubble_pressure_Pa") is None
        or row.get("pressure_uncertainty_Pa") is None
    ):
        return "unresolved"
    dP = row["pressure_Pa"] - row["bubble_pressure_Pa"]
    if abs(dP) <= row["pressure_uncertainty_Pa"]:
        return "unresolved"
    expected = 2 if dP < 0 else 1
    if len(state["amounts"]) != expected:
        return "unresolved"
    return "passed-two-phase" if expected == 2 else "passed-single-liquid"


def phase_outcome(value, *, completion=False):
    if completion:
        if issue := value.get("engine_issue"):
            assert "#" in issue and issue.rsplit("#", 1)[1].isdigit()
            return "open Engine item"
        if value.get("pair"):
            return value["pair"]
        if value["parent_closed"] and value["native_complete"] and value["supplied_complete"] and not value["descent"]:
            return FINITE_NEGATIVE
        raise AssertionError(f"Search {value['key']} did not meet the completion rule")
    if any(q["confirmed"] for q in value.get("attempts", [])):
        return "confirmed split"
    if "instability" in value:
        return "unresolved phase identity" if value["instability"] == "resolved descent" else value["instability"]
    if value.get("search", {}).get("no_descent_in_trial_set"):
        return "finite search, no resolved descent"
    return "unresolved" if value.get("search", {}).get("completed") else "unavailable"


def no_descent(completed, trials):
    return bool(completed and trials) and all(
        t["evidence"] == "no_resolved_descent"
        and t["message"].startswith(("converged:", "Michelsen tangent-plane trial converged:"))
        and t.get("optimizer_success", True)
        and t.get("optimizer_tolerance_met") is not False
        and t.get("descent", t.get("resolved_descent")) is False
        for t in trials
    )


def supplied_complete(counts, excluded, declared):
    return (
        isinstance(counts, dict)
        and counts.keys() == {"evaluated"}
        and type(excluded) is int
        and type(declared) is int
        and 0 <= excluded <= declared
        and type(counts["evaluated"]) is int
        and counts["evaluated"] == declared - excluded
    )
