"""Declared phase requests and classification of the existing search evidence."""

import ast
import copy
from collections import Counter, defaultdict
from collections.abc import Mapping
from concurrent.futures import ProcessPoolExecutor
from multiprocessing import get_context
import json
import math
import os
from types import SimpleNamespace

import numpy as np

from .model import calculation_declaration
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


def measured_loading_envelope(spec, amine):
    """Loading range at each distinct unloaded stock of the fitted loaded observations."""
    by_stock = defaultdict(list)
    for row in spec.inputs["observations"]["fitted"]:
        for field in ("problem", "initial", "final"):
            if field not in row:
                continue
            feed = spec.problems[row[field]].feed.values
            amount = feed.get(amine, 0)
            carbon = feed.get("carbon-dioxide", 0)
            if amount > 0 and carbon > 0:
                water = feed["water"] / amount
                by_stock[round(water, 10)].append((water, carbon / amount))
    return {water: (rows[0][0], min(a for _, a in rows), max(a for _, a in rows))
            for water, rows in by_stock.items()}


def in_measured_envelope(state, amine, envelope):
    stock = state["stock"]
    water = round(stock["water"] / stock[amine], 10)
    if water not in envelope:
        return False
    _, lo, hi = envelope[water]
    return lo <= state["a"] <= hi


def measured_grid(route, spec, loadings):
    amine = route.config["amine"]
    envelope = measured_loading_envelope(spec, amine)
    stocks = [dict(water=water, **{amine: 1.0}) for water, _, _ in sorted(envelope.values())]
    return [state for state in grid_states(stocks, loadings) if in_measured_envelope(state, amine, envelope)]


def retained_measured_grid(route, spec, screen):
    amine = route.config["amine"]
    envelope = measured_loading_envelope(spec, amine)
    _, loadings = grid_axes(route, spec)
    rows = []
    for row in screen["rows"]:
        if not row["key"].startswith("grid:"):
            continue
        stock, _, loading, _ = row["key"].rsplit(":", 3)
        state = dict(stock=ast.literal_eval(stock.removeprefix("grid:")), a=float(loading))
        if in_measured_envelope(state, amine, envelope):
            rows.append(dict(key=row["key"], classification=search_class(row)))
    held = {row["key"] for row in rows}
    missing = [state["key"] for state in measured_grid(route, spec, loadings) if state["key"] not in held]
    return dict(stock_envelopes=list(envelope.values()), rows=rows, not_in_S_screen=missing)


def states(route, spec):
    from .mea import MEARoute

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
    stocks, loadings = grid_axes(route, spec)
    if route.config.get("amine") == "methyldiethanolamine":
        states.extend(measured_grid(route, spec, loadings))
    else:
        states.extend(grid_states(stocks, loadings))
    return list({r["key"]: r for r in states}.values())


def stability_row(route, spec, state, scale, *, metadata=None, cap_from_prediction=False):
    from .mea import MEARoute

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

    def __init__(self, spec, witnesses):
        self.spec = spec
        self.witnesses = witnesses
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
        compiled = eq.compile_problem(spec.model, item.problem)
        return frozenset(range(len(spec.parameters.component_ids))) - set(compiled.removed_species)

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


def measured_search_class(row):
    """Reclassify a held MEA measured-pressure record."""
    native = row["native_trials"]
    if any(t["descent"] for t in native) or any(t["source"] == "supplied" for t in row["witnesses"]):
        return "descent"
    if not (
        row["parent"]["physical_checks_pass"]
        and row["ion_rich_seed"]["strictly_positive"]
        and row["supplied_counts"].keys() == {"evaluated"}
        and row["ion_rich_result"]["evidence"] == "evaluated"
        and no_descent(bool(native), native)
    ):
        return "unavailable"
    return "searched, no instability"


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


R = epcsaft.GAS_CONSTANT_J_PER_MOL_K
# Match a recomputed root to the density at which the equilibrium was solved.
DENSITY_WINDOW = math.log(1.01)
COINCIDENCE = 1e-6
ERROR_TERMS = ("association_energy_estimate_over_rt",
               "feasibility_estimate_over_rt", "summation_estimate_over_rt")


def phase(model, T, P, amounts, rho, x, formulas):
    eos = model.state(T, rho=rho, x=x)
    return dict(T_K=T, amount_mol=amounts, density_mol_m3=rho, x=x, pressure_Pa=eos.pressure,
                pressure_residual_Pa=eos.pressure-P, relative_pressure_residual=(eos.pressure-P)/P, normalization_residual=math.fsum(x)-1,
                charge_residual=math.fsum(w*f['charge'] for w, f in zip(x, formulas, strict=True)))


def balances(feed, phases, formulas):
    inventory = sum(p['amount_mol']*np.array(p['x']) for p in phases)
    counts = np.array([[f.get(e, 0) for f in formulas] for e in 'CHNO'])
    atoms = counts @ (inventory-feed)
    scaled = atoms/(math.fsum(feed)*counts.max(axis=1))
    return dict(element_residual_mol=dict(zip('CHNO', atoms.tolist(), strict=True)), scaled_element_residual=dict(zip('CHNO', scaled.tolist(), strict=True)))


def scaled_pressure_error(residual, density, temperature):
    return abs(residual)/(density*R*temperature)


def phase_passed(p, P, tol, temperature=None):
    residual = p['pressure_residual_Pa']
    return (residual==p['pressure_Pa']-P and p.get('relative_pressure_residual',residual/P)==residual/P
            and p['normalization_residual']==math.fsum(p['x'])-1
            and max(abs(p['charge_residual']),abs(p['normalization_residual']),
                    scaled_pressure_error(residual,p['density_mol_m3'],p.get('T_K',temperature)))<=tol)


def phase_closure(value, pressure, tolerance, *, temperature=None):
    return bool(value.get('phases')) and all(phase_passed(p,pressure,tolerance,temperature) for p in value['phases']) and max(
        map(abs,value['balances']['scaled_element_residual'].values()))<=tolerance


def physical(spec, problem, result):
    ids = spec.parameters.component_ids
    formulas = [spec.spec['element_formulas'][c] for c in ids]
    T, P = result.temperature, result.pressure
    rows = [phase(spec.model, T, P, n, rho, result.phase_mole_fractions(i), formulas)
            for i, (n, rho) in enumerate(zip(result.amounts, result.molar_densities, strict=True))]
    feed = problem.feed.values
    if isinstance(feed, Mapping):
        feed = [feed.get(component, 0.0) for component in ids]
    residuals = balances(feed, rows, formulas)
    checks = dict(phases=rows,balances=residuals)
    return dict(checks,physical_checks_pass=phase_closure(checks,P,problem.row_tolerance),
                residuals=list(result.residuals),row_tolerance=problem.row_tolerance)


def pressure_roots(model, T, P, x, rho):
    checks = []
    for branch in ('liquid','vapor'):
        try:
            state = model.state(T, P=P, x=x, phase=branch)
            density, residual = state.molar_density, state.pressure-P
            checks.append(dict(requested=branch, returned=state.returned_density_branch.name.lower(), density=density,
                               T_K=T,P_Pa=P,log_density_distance=abs(math.log(density/rho)),
                               relative_pressure_residual=abs(residual)/P,pressure_residual_Pa=residual))
        except Exception as error:
            checks.append(dict(requested=branch, error=str(error)))
    return checks


def matched(checks, tolerance, density=None, *, T=None, P=None):
    def pressure_passes(root):
        temperature, pressure = root.get('T_K',T),root.get('P_Pa',P)
        if temperature is None or pressure is None:
            return False
        residual = root.get('pressure_residual_Pa',root['relative_pressure_residual']*pressure)
        return scaled_pressure_error(residual,root['density'],temperature)<=tolerance

    return [r for r in checks if 'density' in r and
            (r.get('log_density_distance',math.inf) if density is None else
             abs(math.log(r['density']/density)))<=DENSITY_WINDOW and pressure_passes(r)]


def distinct_phases(compositions, densities):
    return (max(abs(a-b) for a,b in zip(*compositions,strict=True))>COINCIDENCE or
            abs(math.log(densities[0]/densities[1]))>COINCIDENCE)


def gibbs(compiled, result, report=None):
    if report is None:
        report = eq.stability_test(compiled, result)
    phases = jsonable(report.present_phases)
    assert len(result.amounts)==len(phases) and phases
    return (math.fsum(n*q['g_over_rt'] for n,q in zip(result.amounts,phases,strict=True)),
            math.fsum(n*q[k] for n,q in zip(result.amounts,phases,strict=True) for k in ERROR_TERMS))


def coexistence(spec, parent, parent_g, guesses, *, inspect=None, start=None):
    compiled = eq.compile_problem(spec.model,parent)
    support = [i for i in range(len(spec.parameters.component_ids)) if i not in compiled.removed_species]
    phases = []
    for i,(x,packing) in enumerate(guesses):
        phase = type(parent.phases[0])()
        phase.name, phase.kind, phase.support_declared = f'L{i+1}', parent.phases[0].kind, True
        phase.support, phase.composition_guess, phase.packing_guess = support, [x[j] for j in support], packing
        phases.append(phase)
    original = parent.phases
    parent.phases = phases
    try:
        compiled = eq.compile_problem(spec.model,parent)
        result = eq.solve_equilibrium(spec.model,parent,start)
    finally:
        parent.phases = original
    out = dict(message=result.message, requested_tolerance_met=result.requested_tolerance_met,
               amounts_mol=list(result.amounts))
    if inspect is not None:
        out["diagnostics"] = inspect(compiled, result)
    if not result.requested_tolerance_met or len(result.amounts)!=2 or min(result.amounts)<=0:
        return dict(out, confirmed=False)
    diagnostics = out.get('diagnostics') or {}
    if 'physical_checks_pass' not in diagnostics:
        diagnostics.update(physical(spec,parent,result))
        out['diagnostics'] = diagnostics
    phases = [list(result.phase_mole_fractions(j)) for j in range(2)]
    densities = list(result.molar_densities)
    distinct = distinct_phases(phases,densities)
    report = eq.stability_test(compiled,result)
    roots = [pressure_roots(spec.model,result.temperature,result.pressure,x,rho)
             for x,rho in zip(phases,densities,strict=True)]
    liquid = all(any(r['returned']=='liquid' for r in matched(check,parent.row_tolerance)) for check in roots)
    g, error = gibbs(compiled,result,report)
    comparison = {} if parent_g is None else dict(Gibbs_decrease_over_RT_mol=parent_g[0]-g)
    estimated_error = error if parent_g is None else parent_g[1]+error
    return dict(out, confirmed=diagnostics['physical_checks_pass'] and distinct and liquid and comparison.get('Gibbs_decrease_over_RT_mol',-math.inf)>estimated_error,
                distinct=distinct, split_Gibbs_over_RT_mol=g, split_only=parent_g is None and distinct and liquid, **comparison,
                numerical_error_over_RT_mol=estimated_error, phases=phases,
                Gibbs_sum_over_RT_mol=g, objective_over_RT_mol=result.objective, residuals=list(result.residuals),
                densities_mol_m3=densities, packings=list(result.packing_fractions),
                max_abs_equilibrium_residual=max(map(abs,result.residuals)), roots=roots)


def dilute_vapor_connection(model, T, x, rho):
    density = rho*np.geomspace(1e-4, 1., 33)
    batch = model.states([T]*len(density), rho=density, x=x, derived_properties=True)
    trace = dict(density_mol_m3=density.tolist(), pressure_Pa=batch.pressure, dP_drho=batch.pressure_density_derivative, causes=batch.cause)
    return trace, vapor_trace_connected(trace,rho)


def vapor_trace_connected(trace, rho):
    pressure, density, derivative = (trace[k] for k in ('pressure_Pa','density_mol_m3','dP_drho'))
    return (len(pressure)==len(density)==len(derivative) and density[-1]==rho
            and all(v is not None and v>0 for v in derivative)
            and all(b>a for a,b in zip(pressure,pressure[1:])))


def liquid_vapor(spec, route, parent, guess, parent_g, *, incipient=False, seed=None):
    problem = parent
    original = parent.phases
    pressure = type(parent.pressure).fixed(parent.pressure.value)
    liquid = type(original[0])()
    liquid.name, liquid.kind, liquid.support_declared = 'L', original[0].kind, True
    liquid.support = original[0].support
    x, packing = guess
    liquid.composition_guess, liquid.packing_guess = [x[j] for j in liquid.support], packing
    vapor = type(liquid)()
    vapor.name, vapor.kind, vapor.support_declared = 'V', type(liquid.kind).Vapor, True
    vapor.support = [spec.parameters.component_ids.index(c) for c in route.config['vapor_species']]
    if incipient:
        vapor.amount = type(vapor.amount).pinned(0.)
        problem.pressure = type(problem.pressure).variable(problem.pressure.value)
        if seed and seed.get('phases'):
            liquid.composition_guess = [seed['phases'][0]['x'][j] for j in liquid.support]
            vapor.composition_guess = [seed['phases'][1]['x'][j] for j in vapor.support]
            liquid.packing_guess, vapor.packing_guess = seed['packings']
    problem.phases = [liquid, vapor]
    try:
        result = eq.solve_equilibrium(spec.model, problem)
        compiled = eq.compile_problem(spec.model, problem)
    finally:
        problem.phases, problem.pressure = original, pressure
    out = dict(support='L+incipient V' if incipient else 'L+V', message=result.message, qualified=False,
               T_K=result.temperature, pressure_Pa=result.pressure, amounts_mol=list(result.amounts),
               feed_mol=list(problem.feed.values), row_tolerance=problem.row_tolerance,
               requested_tolerance_met=result.requested_tolerance_met)
    if result.requested_tolerance_met and len(result.amounts)==2:
        out.update(physical(spec, problem, result), packings=list(result.packing_fractions))
        x, rho = [row['x'] for row in out['phases']], list(result.molar_densities)
        trace, connected = dilute_vapor_connection(spec.model, result.temperature, x[1], rho[1])
        out.update(vapor_trace=trace, vapor_connected=connected)
        out['qualified'] = out['physical_checks_pass'] and connected and distinct_phases(x,rho) and result.amounts[0]>0
        if incipient:
            out['qualified'] &= result.amounts[1]==0
        elif out['physical_checks_pass'] and result.amounts[1]>0:
            g, err = gibbs(compiled,result)
            out.update(Gibbs_over_RT_mol=g, error=err)
            out.update(Gibbs_decrease_over_RT_mol=parent_g[0]-g, numerical_error_over_RT_mol=parent_g[1]+err)
            out['qualified'] &= out['Gibbs_decrease_over_RT_mol']>out['numerical_error_over_RT_mol']
        else:
            out['qualified'] = False
    return out


def density_branch(trials):
    sides = {t.get('density_side') for t in trials}
    if not sides:
        return 'none'
    if len(sides)>1:
        return 'mixed'
    return {1: 'vapor', 2: 'liquid'}.get(next(iter(sides)), 'unresolved')


def confirm_descents(route, point, rows, states):
    """Re-solve coexistence for the distinct state keys with a recorded descent."""
    from .properties import marks

    verify()

    spec = route.bind(point)
    by_key = {s['key']:s for s in states}
    results, unresolved, solutions = [], [], {}

    def inspect(compiled, result):
        last[:] = [result]
        if result.requested_tolerance_met and len(result.amounts)==2 and min(result.amounts)>0:
            return physical(spec,parent,result)

    last = []
    for row in rows:
        if not search_descent(row):
            continue
        entry = dict(key=row['key'], native_branch=row['native_branch'],
                     supplied_branch=row['supplied_branch'], attempts=[])
        results.append(entry)
        try:
            item = stability_row(route, spec, by_key[row['key']], 1.)
            prediction = reg.predict(spec.model,item)
            parent = item.problem
            if prediction.pressure_reference is not None:
                parent.pressure = type(parent.pressure).fixed(prediction.pressure_reference.value*item.pressure_ratio)
            central = eq.solve_equilibrium(spec.model,parent)
            if not central.requested_tolerance_met:
                raise ValueError(central.message)
            T,P = central.temperature,central.pressure
            parent_x = list(central.phase_mole_fractions(0))
            parent_roots = pressure_roots(spec.model,T,P,parent_x,central.molar_densities[0])
            entry.update(temperature_K=T, pressure_Pa=P, feed_mol=list(parent.feed.values),
                         parent_roots=parent_roots, outside_ranges=marks(route,T,parent),
                         row_tolerance=parent.row_tolerance, parent=physical(spec,parent,central))
            compiled = eq.compile_problem(spec.model,parent)
            if not entry['parent']['physical_checks_pass']:
                raise ValueError('Parent misses scaled closure')
            report = eq.stability_test(compiled,central,item.stability_options)
            parent_g = gibbs(compiled,central,report)
            primary = (parent_x,central.packing_fractions[0])
            entry['liquid_vapor'] = liquid_vapor(spec,route,parent,primary,parent_g)
            guesses, supplied = [], []
            for witness in row.get('supplied_trial_evidence',[]):
                if not supplied_negative(witness):
                    continue
                phase, q = witness['phase'],witness['quantities']
                x = phase['composition']
                roots = pressure_roots(spec.model,T,P,x,q['molar_density_mol_m3'])
                candidates = matched(roots,parent.row_tolerance)
                evidence = dict(witness=witness,roots=roots)
                supplied.append(evidence)
                if candidates:
                    root = min(candidates,key=lambda r:r['log_density_distance'])
                    packing = q['packing_fraction']*root['density']/q['molar_density_mol_m3']
                    reclosed, _, _ = SuppliedTrials(spec, ()).applicable(item,[dict(phase,packing=packing)],set(phase['support']))
                    options = eq.StabilityOptions()
                    options.prepared_trials = eq.prepare_supplied_trials(spec.model,T,reclosed)
                    trial, = eq.stability_test(compiled,central,options).trials
                    evidence.update(reclosed_evidence=trial.evidence,reclosed_quantities=jsonable(trial.quantities))
                    if root['returned']=='liquid' and trial.evidence=='evaluated' and trial.quantities['tpd_over_rt']<0:
                        guesses.append([primary,(x,packing)])
            entry['supplied_pressure_roots'] = supplied
            if report.trials:
                native = [t for t in report.trials
                          if t.resolved_descent and t.quantities.get('density_side')==2 and t.split_coordinates]
                for trial in sorted(native,key=lambda t:t.quantities['split_delta_g_over_rt']):
                    z = list(trial.split_coordinates)
                    n = len(spec.parameters.component_ids)
                    if len(z)==n+2+len(trial.phase.support)+2:
                        phases = [(list(map(math.exp,z[:n])),math.exp(z[n+1])),
                                  (list(trial.composition),math.exp(z[-1]))]
                    else:
                        phases = [primary,(list(trial.composition),math.exp(z[-1]))]
                    guesses.insert(0,phases)
            entry['liquid_directed'] = bool(guesses)
            for guess in guesses if row['key'] not in ('weiland-1998:31:problem','lawson-1976-viii:0:problem') else []:
                attempt = coexistence(spec,parent,parent_g,guess,inspect=inspect)
                entry['attempts'].append(attempt)
                if attempt['confirmed']:
                    solutions[entry['key']] = last[0]
                    break
            if guesses and not any(a['confirmed'] for a in entry['attempts']):
                unresolved.append((entry,parent,parent_g))
        except (AssertionError, ValueError, RuntimeError) as error:
            entry['classification_error'] = str(error)
    for entry,parent,parent_g in sorted(unresolved,key=lambda item: item[0]['key'] in (
            'weiland-1998:31:problem','lawson-1976-viii:0:problem')):
        if entry['key']=='weiland-1998:31:problem':
            target = entry['feed_mol']
            carbon = spec.parameters.component_ids.index('carbon-dioxide')
            other, seed = min(
                ((r,a) for r in results if r.get('temperature_K')==entry['temperature_K']
                 and r['feed_mol'][:carbon]+r['feed_mol'][carbon+1:]==target[:carbon]+target[carbon+1:]
                 for a in r['attempts'] if a['confirmed']),
                key=lambda pair: abs(pair[0]['feed_mol'][carbon]-target[carbon]))
            start = solutions[other['key']]
            amine = target[spec.parameters.component_ids.index(route.config['amine'])]
            difference = target[carbon]-other['feed_mol'][carbon]
            steps = round(abs(difference)/amine/.0025)
            if steps <= 0 or not math.isclose(abs(difference),steps*.0025*amine,abs_tol=math.ulp(target[carbon])):
                raise ValueError(f"Invalid DEA continuation loading step for {entry['key']}")
            guess = list(zip(seed['phases'],seed['packings'],strict=True))
            trace = entry['continuation'] = []
            for i in range(1,steps+1):
                feed = target.copy()
                if i!=steps:
                    feed[carbon] = other['feed_mol'][carbon]+math.copysign(i*.0025*amine,difference)
                declared = parent.feed
                declared.values = feed
                parent.feed = declared
                center = eq.solve_equilibrium(spec.model,parent)
                if not center.requested_tolerance_met:
                    trace.append(dict(feed_mol=feed,message=center.message))
                    break
                comparison = {}
                if i==steps:
                    comparison['comparison_parent'] = physical(spec,parent,center)
                    if not comparison['comparison_parent']['physical_checks_pass']:
                        trace.append(dict(feed_mol=feed,message='Comparison parent misses scaled closure',**comparison))
                        break
                g = gibbs(eq.compile_problem(spec.model,parent),center)
                attempt = coexistence(spec,parent,g,guess,inspect=inspect,start=start)
                attempt.update(feed_mol=feed,seed_from=other['key'],**comparison)
                trace.append(attempt)
                if not attempt['requested_tolerance_met'] or min(attempt['amounts_mol'],default=0)<=0:
                    break
                start = last[0]
            if trace[-1]['feed_mol']==target and 'confirmed' in trace[-1]:
                entry['attempts'].append(trace[-1])
            continue
        neighbors = sorted(
            ((r,a) for r in results for a in r['attempts'] if a['confirmed']),
            key=lambda pair: (abs(entry['temperature_K']-pair[0]['temperature_K']),
                              abs(math.log(entry['pressure_Pa']/pair[0]['pressure_Pa']))),
        )[:3]
        if entry['key']=='lawson-1976-viii:0:problem':
            neighbors.sort(key=lambda pair: pair[0]['key']!='weiland-1998:32:problem')
        for other,seed in neighbors:
            attempt = coexistence(spec,parent,parent_g,list(zip(seed['phases'],seed['packings'],strict=True)),inspect=inspect)
            entry['attempts'].append(dict(attempt, seed_from=other['key']))
            if attempt['confirmed']:
                solutions[entry['key']] = last[0]
                break
    return results


def trials(report):
    return [dict(seed=t.seed, kind=t.phase.kind.name, support=list(t.phase.support), composition=list(t.composition),
                 evidence=t.evidence, message=t.message, descent=t.resolved_descent, quantities=t.quantities,
                 optimizer_success=t.optimizer.success, optimizer_tolerance_met=t.optimizer.requested_tolerance_met)
            for t in report.trials]


def fixed_control(route, spec, state, P, seed, *, mdea=False, assemblages=False):
    item = stability_row(route, spec, state, 1.)
    problem, model = item.problem, spec.model
    problem.pressure = type(problem.pressure).fixed(P)
    item.pressure_reference = None
    result = eq.solve_equilibrium(model, problem)
    compiled = eq.compile_problem(model, problem)
    out = dict(T_K=result.temperature, P_Pa=P, realized_Pa=result.pressure, feed_mol=list(problem.feed.values),
               species=list(spec.parameters.component_ids), declaration=calculation_declaration(problem),
               status=result.message, attempts=[])
    parent_g, guess, native, seeds = None, None, [], []
    if result.requested_tolerance_met:
        x, rho = list(result.phase_mole_fractions(0)), result.molar_densities[0]
        guess = (x, result.packing_fractions[0])
        out.update(physical(spec, problem, result))
        out['roots'] = pressure_roots(model, result.temperature, P, x, rho)
        if not out['physical_checks_pass']:
            out['instability'] = 'unresolved'
            out['blocker'] = 'Trial-call parent misses scaled closure'
            out['search'] = dict(completed=False,message=out['blocker'])
            out['native_trials'] = []
            return out
        report = eq.stability_test(compiled,result,item.stability_options)
        out['search'] = dict(completed=report.completed,message=report.message,available=report.completed,
                             no_descent_in_trial_set=report.no_descent_in_trial_set)
        parent_g = gibbs(compiled, result, report)
        out['parent_gibbs_RT_mol'] = parent_g
        native = trials(report)
        seeds = [t for t in report.trials if t.resolved_descent and t.split_coordinates
                 and t.quantities.get('density_side')==2 and len(t.phase.support)==len(x)]
        if seed and seed.get('witness'):
            witness = seed['witness']
            support = set(range(len(spec.parameters.component_ids))) - set(compiled.removed_species)
            supplied, _, _ = SuppliedTrials(spec, ()).applicable(item, [witness], support)
            options = eq.StabilityOptions()
            options.prepared_trials = eq.prepare_supplied_trials(model, result.temperature, supplied)
            out['supplied'] = trials(eq.stability_test(compiled, result, options)) if supplied else []
    out['native_trials'] = native
    resolved = any(t['descent'] for t in native) or any(
        supplied_negative(t) for t in out.get('supplied', []) if 'quantities' in t)
    out['instability'] = 'resolved descent' if resolved else 'finite search, no resolved descent' if (
        out.get('search', {}).get('no_descent_in_trial_set')) else 'unresolved' if result.requested_tolerance_met else 'unavailable'
    pair_solution = []
    if seed and (resolved or mdea or not assemblages):
        attempts = [list(zip(seed['pair']['phases'], seed['pair']['packings'], strict=True))]
        if guess is not None and not mdea:
            for t in sorted(seeds,key=lambda t:t.quantities['split_delta_g_over_rt']):
                z, n = t.split_coordinates, len(guess[0])
                donor = (list(map(math.exp,z[:n])),math.exp(z[n+1])) if len(z)==2*n+4 else guess
                attempts.append([donor,(list(t.composition),math.exp(z[-1]))])
        def inspect(compiled, solved):
            pair_solution[:] = compiled, solved
            if solved.requested_tolerance_met and len(solved.amounts)==2 and min(solved.amounts)>0:
                details = physical(spec, problem, solved)
                return details

        for index, guesses in enumerate(attempts):
            try:
                pair = coexistence(spec, problem, parent_g, guesses, inspect=inspect)
                pair.update(seed='archive' if index==0 else 'native split')
                out['attempts'].append(pair)
                if 'phases' in pair:
                    if mdea:
                        pair['dilute_vapor_traces'] = [dilute_vapor_connection(model, result.temperature, x, rho)
                                                       for x, rho in zip(pair['phases'], pair['densities_mol_m3'], strict=True)]
                if pair['confirmed']:
                    break
            except (ValueError, RuntimeError) as error:
                out['attempts'].append(dict(confirmed=False, message=str(error)))
    distances = [t for t in native+out.get('supplied', []) if (t.get('descent') or t.get('evidence') in ('evaluated','no_resolved_descent')) and 'quantities' in t
                 and 'tpd_over_rt' in t['quantities']]
    out['minimum_trial'] = min(distances, key=lambda t: t['quantities']['tpd_over_rt'], default=None)
    if (best := out['minimum_trial']) is not None:
        out['minimum_trial_roots'] = pressure_roots(model, result.temperature, P, best['composition'],
                                                       1/best['quantities']['volume_m3_per_mol'])
    if resolved:
        out['liquid_vapor'] = liquid_vapor(spec, route, problem, guess, parent_g)
        if assemblages:
            amp_candidates(spec, route, problem, out, pair_solution)
    return out


def assemblage_phase(template, name, kind, support, guess=(None, None), *, pinned=False):
    phase = type(template)()
    phase.name, phase.kind = name, getattr(type(template.kind), kind)
    phase.support, phase.support_declared = support, True
    x, phase.packing_guess = guess
    if x is not None:
        phase.composition_guess = [x[i] for i in support]
    if pinned:
        phase.amount = type(phase.amount).pinned(0.)
    return phase


def amp_assemblage(spec, problem, kind, phases):
    entry = dict(support=kind, qualified=False)
    original, pressure = problem.phases, problem.pressure
    incipient = 'incipient' in kind
    model = spec.model
    try:
        problem.phases = phases
        problem.pressure = (type(pressure).variable(pressure.value) if incipient
                            else type(pressure).fixed(pressure.value))
        solved = eq.solve_equilibrium(model, problem)
        entry.update(message=solved.message, pressure_Pa=solved.pressure, amounts_mol=list(solved.amounts),
                     requested_tolerance_met=solved.requested_tolerance_met, residuals=list(solved.residuals))
        if solved.requested_tolerance_met and len(solved.amounts) == len(phases):
            entry.update(physical(spec, problem, solved))
            roots = [pressure_roots(model, solved.temperature, solved.pressure, p['x'], p['density_mol_m3'])
                     for p in entry['phases']]
            entry['roots'] = roots
            wanted = ['liquid']*(len(phases)-1)+['vapor']
            entry['root_checks_pass'] = all(any(r['returned']==branch for r in matched(test, problem.row_tolerance))
                                            for branch, test in zip(wanted, roots, strict=True))
            entry['qualified'] = (entry['physical_checks_pass'] and entry['root_checks_pass']
                                  and min(solved.amounts[:(-1 if incipient else None)])>0)
            if not incipient:
                compiled = eq.compile_problem(model, problem)
                report = eq.stability_test(compiled, solved)
                entry['Gibbs_over_RT_mol'], entry['error'] = gibbs(compiled, solved, report)
                entry['omitted_phase_trials'] = trials(report)
    except (ValueError, RuntimeError) as error:
        entry.update(message=str(error))
    finally:
        problem.phases, problem.pressure = original, pressure
    return entry


def amp_candidates(spec, route, problem, out, pair_solution):
    model = spec.model
    vapor = [spec.parameters.component_ids.index(c) for c in route.config['vapor_species']]
    support = [i for i in range(len(spec.parameters.component_ids))
               if i not in eq.compile_problem(model, problem).removed_species]
    pair = next((a for a in out['attempts'] if a['confirmed']), None)
    g, error = out['parent_gibbs_RT_mol']
    candidates = [dict(support='L', Gibbs_over_RT_mol=g, error=error, qualified=out['physical_checks_pass']),
                  out['liquid_vapor']]
    out['candidates'] = candidates
    template = problem.phases[0]
    variants = []
    if pair:
        compiled, solved = pair_solution
        omitted = trials(eq.stability_test(compiled, solved))
        candidates.append(dict(support='L1+L2', qualified=True, pressure_Pa=solved.pressure,
                               Gibbs_over_RT_mol=pair['split_Gibbs_over_RT_mol'],
                               error=pair['numerical_error_over_RT_mol']-error,
                               amounts_mol=pair['amounts_mol'], omitted_phase_trials=omitted))
        liquid = [assemblage_phase(template, f'L{i+1}', 'Liquid', support, seed)
                  for i, seed in enumerate(zip(pair['phases'], pair['packings'], strict=True))]
        seed = next(t for t in out['native_trials'] if t['kind']=='Vapor' and t['seed']=='positive-neutral-base')
        vapor_guess = (seed['composition'], None)
        variants.append(('L1+L2+incipient V', liquid+[assemblage_phase(template, 'V', 'Vapor', vapor, vapor_guess, pinned=True)]))
        if any(t['kind']=='Vapor' and t['descent'] for t in omitted):
            variants.append(('L1+L2+V', liquid+[assemblage_phase(template, 'V', 'Vapor', vapor, vapor_guess)]))
    else:
        candidates.append(dict(support='L1+L2', qualified=False, message='Seeded attempts did not confirm distinct liquid roots below parent Gibbs beyond paired error.'))
    candidates.extend(amp_assemblage(spec, problem, kind, phases) for kind, phases in variants)
    eligible = sorted((c for c in candidates if c['qualified'] and 'Gibbs_over_RT_mol' in c), key=lambda c: c['Gibbs_over_RT_mol'])
    out['lowest_found'] = dict(scope='lowest-G feasible assemblage found among the tested supports', support=eligible[0]['support']) if eligible else None
    out['unresolved_supports'] = [c['support'] for c in candidates if not c['qualified'] and 'incipient' not in c['support']]
    if len(eligible)>1 and eligible[1]['Gibbs_over_RT_mol']-eligible[0]['Gibbs_over_RT_mol'] <= eligible[0]['error']+eligible[1]['error']:
        out['lowest_found']['comparison'] = 'Gibbs difference within paired numerical error'
    out['stable_assemblage'] = None


def seed_state(spec, entry):
    feed = dict(zip(spec.parameters.component_ids, entry['feed_mol'], strict=True))
    loading = feed.pop('carbon-dioxide') / feed['methyldiethanolamine']
    return dict(T=entry['temperature_K'], stock={c:n for c,n in feed.items() if n}, a=loading)


def mdea_predicates(outcome, *, tolerance):
    readback = outcome.get('reference_readback',{}).get('pair_readback',[])
    for i,result in enumerate(outcome['attempts']):
        diagnostics = result.get('diagnostics')
        checks = dict(requested_tolerance=result.get('requested_tolerance_met',False),
                      positive_amounts=len(result.get('amounts_mol',[]))==2 and min(result['amounts_mol'])>0,
                      balances_and_phases=(result if diagnostics is None else diagnostics).get('physical_checks_pass',False),
                      distinct=result.get('distinct',False),
                      liquid_root=bool(result.get('roots')) and all(
                          any(x['returned']=='liquid' for x in matched(
                              group,tolerance,T=outcome.get('T_K'),P=outcome.get('P_Pa'))) for group in result['roots']),
                      lowering=result.get('Gibbs_decrease_over_RT_mol',-math.inf)>result.get('numerical_error_over_RT_mol',math.inf))
        if i < len(readback) and readback[i]:
            checks['reaction'] = readback[i]['affinity_within_tolerance']
            checks['interphase'] = readback[i]['charge_neutral_transfer_within_tolerance']
        if checks['positive_amounts']:
            result['phase_fractions'] = [v/sum(result['amounts_mol']) for v in result['amounts_mol']]
        if result.get('phases'):
            result['separation'] = dict(max_delta_x=max(abs(i-j) for i,j in zip(*result['phases'],strict=True)),
                     log_density_ratio=abs(math.log(result['densities_mol_m3'][0]/result['densities_mol_m3'][1])))
        result['acceptance'] = checks
        result['disposition'] = ('confirmed' if all(checks.values()) else 'failed' if not checks['requested_tolerance']
            else 'coalesced' if checks['positive_amounts'] and not checks['distinct'] else 'unresolved')
    outcome['tolerances'] = dict(equilibrium_row=tolerance, coincidence=COINCIDENCE, log_root_matching=DENSITY_WINDOW)
    return outcome


def _bind_search(route, point, witnesses):
    global _route, _spec, _supplied
    verify()
    _route, _spec = route, route.bind(point)
    _supplied = SuppliedTrials(_spec, witnesses) if witnesses else None


def _search(state):
    return native_search(_route, _spec, state, supplied=_supplied,
                         cap_from_prediction=_route.config.get("amine") == "methyldiethanolamine")


def measured_search(spec, row, bank):
    """Re-evaluate the recorded absolute-pressure request and its trial bank."""
    verify()
    ids = spec.parameters.component_ids
    template = next(problem for problem in spec.problems.values() if len(problem.phases) == 2)
    liquid = eq.Phase("L", kind="liquid", support=ids)
    vapor = eq.Phase("V", kind="vapor", support=ids[:3], amount=eq.Pinned(0.0))
    T, P = row["T_K"], row["P_Pa"]
    basis = dict(identity=row["identity"], T_K=T, P_Pa=P, feed_mol=row["feed_mol"], row_tolerance=row["row_tolerance"])
    problem = eq.Problem(T=T, P=eq.Free(1e5), feed=eq.Amounts(row["feed_mol"]),
                         reactions=template.reactions, neutral_reference=template.neutral_reference,
                         row_tolerance=row["row_tolerance"], phases=[liquid, vapor])
    try:
        bubble = eq.solve_equilibrium(spec.model, problem)
        if not bubble.requested_tolerance_met:
            raise ValueError("Candidate bubble: " + bubble.message)
        problem.P = P
        liquid.composition_guess = list(bubble.phase_mole_fractions(0))
        liquid.packing_guess = bubble.packing_fractions[0]
        liquid_parent = P >= bubble.pressure
        if liquid_parent:
            problem.phases = [liquid]
        else:
            vapor.amount = eq.Free()
            vapor.composition_guess = {species: bubble.phase_mole_fractions(1)[i] for i, species in enumerate(ids[:3])}
            vapor.packing_guess = bubble.packing_fractions[1]
            problem.phases = [liquid, vapor]
        basis.update(bubble_Pa=bubble.pressure, declared_parent="liquid" if liquid_parent else "liquid-vapour")
        parent = eq.solve_equilibrium(spec.model, problem)
        if not parent.requested_tolerance_met or min(parent.amounts) <= 0:
            raise ValueError(parent.message)
        native = problem._native(spec.parameters)
        closure = physical(spec, native, parent)
        compiled = eq.compile_problem(spec.model, problem)
        options = eq.StabilityOptions()
        options.mode = type(options.mode).Full
        optimized = eq.stability_test(compiled, parent, options)

        inventory = [math.fsum(n * parent.phase_mole_fractions(i)[j] for i, n in enumerate(parent.amounts))
                     for j in range(len(ids))]
        amounts = dict(zip(ids, inventory, strict=True))
        extent = 0.5 * min(amounts["carbon-dioxide"], 0.5 * amounts["monoethanolamine"])
        change = {"carbon-dioxide": -1, "monoethanolamine": -2, "protonated-monoethanolamine": 1, "carbamate-anion": 1}
        rich = [amount + extent * change.get(species, 0) for species, amount in amounts.items()]
        total = math.fsum(rich)
        fractions = [amount / total for amount in rich]
        rho = spec.model.state(T, P=P, x=fractions, phase="liquid").molar_density
        witness = dict(support=list(range(len(ids))), composition=fractions, kind="Liquid",
                       packing=rho * spec.model._model.packing_fraction_coefficient(T, fractions))
        support = set(range(len(ids))) - set(compiled.removed_species)
        supplied = SuppliedTrials(spec, ())
        phases, repeated, _ = supplied.applicable(SimpleNamespace(problem=native), [*bank, witness], support)
        options = eq.StabilityOptions()
        options.prepared_trials = eq.prepare_supplied_trials(spec.model, T, phases)
        tested = eq.stability_test(compiled, parent, options).trials
        counts = Counter(tested[i].evidence for i, _ in repeated)
        descended = any(trial.resolved_descent for trial in optimized.trials) or any(
            supplied_negative(dict(evidence=tested[i].evidence, quantities=tested[i].quantities)) for i, _ in repeated)
        available = (closure["physical_checks_pass"] and optimized.completed and min(rich) > 0
                     and counts["evaluated"] == len(repeated) and bool(optimized.trials))
        return dict(basis, parent=closure, available=available, supplied_counts=dict(counts), descent=descended,
                    cause=None if available else "Inspect parent physical checks and native and supplied trial dispositions")
    except (ValueError, RuntimeError, IndexError, TypeError, AttributeError) as error:
        return dict(basis, available=False, descent=False, cause=f"{type(error).__name__}: {error}")


def _measured(row):
    return measured_search(_spec, row, _supplied.witnesses)


def compare_confirmations(retained, replayed):
    def outcomes(rows):
        return {row["key"]: (row["native_branch"], row["supplied_branch"],
                             any(attempt["confirmed"] for attempt in row["attempts"])) for row in rows}

    before, after = outcomes(retained), outcomes(replayed)
    return [dict(key=key, retained=before.get(key), replayed=after.get(key))
            for key in sorted(before.keys() | after.keys()) if before.get(key) != after.get(key)]


def control_requests(amine, spec):
    from .records import ROOT, read

    def prior_pair(entry):
        return next(attempt for attempt in entry["attempts"] if attempt["confirmed"])

    stage = ROOT / "analyses/round_7/results"
    if amine == "dea":
        retained = read(stage / "F/search-outcome.json.gz")
        for entry in retained["classifications"]:
            if entry["key"] in retained["confirmed"]:
                yield entry["key"], dict(problem=entry["key"]), entry["pressure_Pa"], dict(pair=prior_pair(entry)), False
    elif amine == "amp":
        retained = read(ROOT / "analyses/amp_transfer/results/retransfer-412-f2-05e94210/main/phase-classification-1.json.gz")
        bank = {row["key"]: row for row in retained["states"]}
        for row in read(ROOT / "analyses/round_3/results/q1.json")["rows"]:
            if row["pressure_basis"] != "measured pressure":
                continue
            entry = bank[row["key"]]
            witness = next(t for t in entry["supplied_pressure_roots"] if supplied_negative(t["witness"]))
            phase = dict(witness["witness"]["phase"],
                         packing=witness.get("reclosed_quantities", witness["witness"]["quantities"])["packing_fraction"])
            yield row["key"], dict(problem=row["key"]), row["free"]["P_Pa"], dict(pair=prior_pair(entry), witness=phase), True
        case = read(stage / "display-replays/amp-common-pressure.json.gz")
        pair = read(ROOT / "analyses/mea_parameter_bundle/results/reference-states-428/amp.json")["split"]
        yield "worked-state", case["state"], case["outcomes"]["free"]["fixed"]["P_Pa"], dict(pair=pair), False


def reported_controls(amine, design, route, spec, endpoint):
    from .model import REPORTED
    from .records import read

    wheel = verify()
    retained = read(REPORTED / design / "controls/A.json.gz")
    if retained["wheel"] != wheel or retained["endpoint_fingerprint"] != endpoint:
        raise ValueError(f"{design}: control baseline belongs to a different wheel or endpoint")
    rows = {}
    for key, state, pressure, seed, assemblages in control_requests(amine, spec):
        row = dict(state=state, P_Pa=pressure, pressure_basis="retained absolute pressure")
        rows[key] = row
        try:
            value = fixed_control(route, spec, state, pressure, seed, mdea=amine == "mdea", assemblages=assemblages)
            row["value"] = mdea_predicates(value, tolerance=value["declaration"]["row_tolerance"]) if amine == "mdea" else value
        except (AttributeError, IndexError, RuntimeError, ValueError) as error:
            row["refusal"] = f"{type(error).__name__}: {error}"

    def outcomes(data):
        return {key: (row["state"], row["P_Pa"], phase_outcome(value := row.get("value", {})),
                      sum(attempt["confirmed"] for attempt in value.get("attempts", []))) for key, row in data.items()}

    before, after = outcomes(retained["rows"]), outcomes(rows)
    differences = [dict(key=key, retained=before.get(key), replayed=after.get(key))
                   for key in sorted(before.keys() | after.keys()) if before.get(key) != after.get(key)]
    return dict(wheel=wheel, endpoint_fingerprint=endpoint, rows=rows, differences=differences)


def amp_measured_controls(route, point, first):
    from .fit import fingerprint

    spec = route.bind(point)
    observed = {row["problem"]: row["arguments"]["observed"]
                for role in ("fitted", "comparisons")
                for row in spec.inputs["observations"][role]
                if row["kind"] == "pressure" and row["group"] in ("hartono-2021-supplemental", "tong")}
    rows = {}
    for entry in first["classifications"]:
        key = entry["key"]
        if key not in observed:
            continue
        pair = next((a for a in entry["attempts"] if a["confirmed"]), None)
        if pair is None:
            continue
        state = dict(key=key, problem=key)
        result = fixed_control(route, spec, state, observed[key], dict(pair=pair), assemblages=True)
        candidates = result.get("candidates", []) or []
        liquid_vapor = next((candidate for candidate in candidates if candidate["support"] == "L+V"), {})
        vapor = any(t["descent"] and t["quantities"].get("density_side") == 1
                    for t in result.get("native_trials", []))
        outcome = phase_outcome(result)
        if outcome == "finite search, no resolved descent":
            outcome = "No resolved descent"
        elif outcome == "unresolved phase identity" and liquid_vapor.get("qualified"):
            outcome = "L+V passed; L+L unresolved"
        elif outcome == "unresolved phase identity" and vapor:
            outcome = "Vapor-directed; root unqualified"
        rows[key] = dict(outcome=outcome, pressure_Pa=observed[key], result=result)
    return dict(wheel=verify(), endpoint_fingerprint=fingerprint(point),
                first_fit_fingerprint=first["endpoint_fingerprint"], rows=rows)


def amp_third_liquid(route, point, controls):
    """Search for a second liquid at the measured-pressure L+V parents."""
    from .fit import fingerprint

    wheel, endpoint = verify(), fingerprint(point)
    if (controls["wheel"], controls["endpoint_fingerprint"]) != (wheel, endpoint):
        raise ValueError("The AMP measured controls use a different wheel or endpoint")
    spec = route.bind(point)
    vapor_support = [spec.parameters.component_ids.index(c) for c in route.config["vapor_species"]]
    rows = {}
    for key, control in controls["rows"].items():
        retained = control["result"].get("liquid_vapor", {})
        if not retained.get("qualified"):
            continue
        pressure = control["pressure_Pa"]
        problem = stability_row(route, spec, dict(key=key, problem=key), 1.).problem
        problem.pressure = type(problem.pressure).fixed(pressure)
        template = problem.phases[0]
        support = template.support
        guesses = [(p["x"], packing) for p, packing in zip(retained["phases"], retained["packings"], strict=True)]
        liquid = assemblage_phase(template, "L1", "Liquid", support, guesses[0])
        vapor = assemblage_phase(template, "V", "Vapor", vapor_support, guesses[1])
        problem.phases = [liquid, vapor]
        compiled = eq.compile_problem(spec.model, problem)
        parent = eq.solve_equilibrium(spec.model, problem, prepared=compiled)
        feed = list(problem.feed.values)
        ids = list(spec.parameters.component_ids)
        row = rows[key] = dict(T_K=parent.temperature, P_Pa=pressure, feed_mol=dict(zip(ids, feed, strict=True)),
                               loading=feed[ids.index("carbon-dioxide")]/feed[ids.index(route.config["amine"])],
                               declaration=calculation_declaration(problem), candidates=[])
        parent_record = row["parent"] = dict(message=parent.message, amounts_mol=list(parent.amounts),
                                             requested_tolerance_met=parent.requested_tolerance_met,
                                             residuals=list(parent.residuals))
        if not parent.requested_tolerance_met or len(parent.amounts) != 2 or min(parent.amounts) <= 0:
            row["outcome"] = "The reconstructed L+V parent did not qualify"
            continue
        parent_record.update(physical(spec, problem, parent))
        options = eq.StabilityOptions()
        options.trials = [assemblage_phase(template, "L2", "Liquid", support)]
        options.plane_value_errors = True
        search = row["search"] = dict(call="eq.stability_test(compiled, parent, options)",
                                      options=calculation_declaration(options))
        try:
            report = eq.stability_test(compiled, parent, options)
        except (ValueError, RuntimeError) as error:
            search.update(completed=False, message=str(error), error_type=type(error).__name__)
            row["outcome"] = "Engine error during the two-phase-parent search"
            break
        search.update(completed=report.completed, message=report.message,
                      no_descent_in_trial_set=report.no_descent_in_trial_set, trials=trials(report))
        g, error = gibbs(compiled, parent, report)
        parent_record.update(Gibbs_over_RT_mol=g, error=error,
                             retained_Gibbs_difference_over_RT_mol=g-retained["Gibbs_over_RT_mol"])
        if not parent_record["physical_checks_pass"] or abs(g-retained["Gibbs_over_RT_mol"]) > error+retained["error"]:
            row["outcome"] = "The reconstructed L+V parent did not reproduce the retained parent within error"
            continue
        dense_trials = []
        for trial in search["trials"]:
            q = trial["quantities"]
            if "tpd_over_rt" not in q or "plane_value_error_estimate_over_rt" not in q:
                continue
            x, rho = trial["composition"], 1/q["volume_m3_per_mol"]
            roots = pressure_roots(spec.model, parent.temperature, pressure, x, rho)
            trial["roots"] = roots
            trial["liquid_root"] = any(root["returned"] == "liquid" for root in matched(roots, problem.row_tolerance))
            if not trial["liquid_root"] or not trial["optimizer_tolerance_met"]:
                continue
            dense_trials.append(trial)
            phases = parent_record["phases"]
            trial["distinct"] = all(distinct_phases((p["x"], x), (p["density_mol_m3"], rho)) for p in phases)
            if trial["distinct"] and q["tpd_over_rt"] < -q["plane_value_error_estimate_over_rt"]:
                packing = rho * spec.model._model.packing_fraction_coefficient(parent.temperature, x)
                second = assemblage_phase(template, "L2", "Liquid", support, (x, packing))
                candidate = amp_assemblage(spec, problem, "L1+L2+V", [liquid, second, vapor])
                candidate["seed"] = trial["seed"]
                if "Gibbs_over_RT_mol" in candidate:
                    first_liquid, second_liquid = candidate["phases"][:2]
                    candidate["distinct_liquids"] = distinct_phases(
                        (first_liquid["x"], second_liquid["x"]),
                        (first_liquid["density_mol_m3"], second_liquid["density_mol_m3"]),
                    )
                    candidate["Gibbs_decrease_over_RT_mol"] = g-candidate["Gibbs_over_RT_mol"]
                    candidate["numerical_error_over_RT_mol"] = error+candidate["error"]
                    candidate["qualified"] &= (candidate["distinct_liquids"] and
                                               candidate["Gibbs_decrease_over_RT_mol"] > candidate["numerical_error_over_RT_mol"])
                else:
                    candidate["qualified"] = False
                row["candidates"].append(candidate)
        search["minimum_liquid_trial"] = min(dense_trials, key=lambda t: t["quantities"]["tpd_over_rt"], default=None)
        if any(candidate["qualified"] for candidate in row["candidates"]):
            row["outcome"] = "Confirmed L1+L2+V"
        elif row["candidates"]:
            row["outcome"] = "Distinct liquid descent without a qualified L1+L2+V result"
        elif report.completed and report.no_descent_in_trial_set and dense_trials:
            row["outcome"] = "No resolved additional liquid descent in the finite search"
        else:
            row["outcome"] = "The Engine did not complete a liquid search against the L+V parent"
    return dict(wheel=wheel, endpoint_fingerprint=endpoint, controls_fingerprint=fingerprint(controls), rows=rows)


def _census(row):
    from .mea import CENSUS_FEED

    verify()
    spec = _spec
    T, P = row["temperature_K"], row["pressure_Pa"]
    model, ids = spec.model, spec.parameters.component_ids
    template = next(problem for problem in spec.problems.values() if len(problem.phases) == 2)
    amine, water = CENSUS_FEED
    feed = eq.Amounts({"monoethanolamine": amine, "water": water, "carbon-dioxide": row["loading"] * amine})
    liquid = eq.Phase("L", kind="liquid", support=ids)
    vapor = eq.Phase("V", kind="vapor", support=ids[:3])
    problem = eq.Problem(T=T, P=P, feed=feed, phases=[liquid, vapor], reactions=template.reactions,
                         neutral_reference=template.neutral_reference, row_tolerance=template.row_tolerance)
    record = {key: row[key] for key in ("index", "temperature_K", "pressure_Pa", "loading")}
    parent = eq.solve_equilibrium(model, problem)
    liquid_problem = copy.copy(problem)
    liquid_problem.phases = [liquid]
    liquid_parent = eq.solve_equilibrium(model, liquid_problem)
    if liquid_parent.success:
        bubble_problem = copy.copy(problem)
        bubble_problem.P = eq.Free(P)
        bubble_problem.phases = [
            eq.Phase("L", kind="liquid", support=ids, composition_guess=liquid_parent.phase_mole_fractions(0),
                     packing_guess=liquid_parent.packing_fractions[0]),
            eq.Phase("V", kind="vapor", support=ids[:3], amount=eq.Pinned(0.0)),
        ]
        bubble = eq.solve_equilibrium(model, bubble_problem)
        if bubble.success:
            criterion = bubble.convergence.criterion
            uncertainty = bubble.pressure * max(bubble.convergence.residual, bubble.convergence.floor or 0.0,
                                                criterion.value if criterion else 0.0)
            record.update(bubble_pressure_Pa=bubble.pressure, pressure_uncertainty_Pa=uncertainty)
            if P > bubble.pressure:
                problem, parent = liquid_problem, liquid_parent
            elif not parent.success:
                compositions = [[bubble.phase_mole_fractions(i)[ids.index(species)] for species in phase.support]
                                for i, phase in enumerate(problem.phases)]
                starts = [eq.EquilibriumStart(amounts=[bubble.amounts[0] * f, bubble.amounts[0] * (1 - f)],
                                               compositions=compositions, packing_fractions=bubble.packing_fractions)
                          for f in (0.5, 0.9)]
                batch = eq.solve_equilibrium_starts(model, problem, starts,
                    eq.EquilibriumWorkLimits(attempts=2, attempt_iterations=400, iterations=800))
                if batch.selected is not None:
                    parent = batch.results[batch.selected]
    record["final"] = final = dict(success=parent.success, requested_tolerance_met=parent.requested_tolerance_met)
    if parent.success:
        compiled = eq.compile_problem(model, problem)
        final.update(amounts=list(parent.amounts), raw_residuals=list(compiled.evaluate(parent.coordinates).values),
                     reduced_hessian_minimum=parent.reduced_hessian_minimum,
                     pressure_density_derivatives=[model.state(T, rho=rho, x=parent.phase_mole_fractions(i))
                                                   .pressure_density_derivative
                                                   for i, rho in enumerate(parent.molar_densities)])
        options = eq.StabilityOptions()
        trials = copy.copy(problem)
        trials.phases = [eq.Phase("trial-L", kind="liquid", support=ids),
                         eq.Phase("trial-V", kind="vapor", support=ids[:3])]
        options.trials = trials._native(model).phases
        optimized = eq.stability_test(compiled, parent, options)
        trials.phases = [eq.Phase("previous-split", kind=w["kind"].lower(), support=[ids[i] for i in w["support"]],
                                  composition_guess=w["composition"], packing_guess=w["packing"])
                         for w in _supplied.witnesses]
        options.evaluate_supplied_trials = True
        options.trials = trials._native(model).phases
        supplied = eq.stability_test(compiled, parent, options)
        record["stability"] = [dict(completed=optimized.completed, trials=[
            dict(resolved_descent=t.resolved_descent, evidence=t.evidence, optimizer=dict(success=t.optimizer.success),
                 phase=dict(kind=t.phase.kind.name.lower())) for t in optimized.trials
        ], supplied_trials=[dict(evidence=t.evidence, quantities=jsonable(t.quantities)) for t in supplied.trials])]
    record["classification"] = census_class(record)
    for report in record.get("stability", ()):
        trials = report["supplied_trials"]
        report["supplied_counts"] = dict(Counter(t["evidence"] for t in trials))
        report["supplied_trials"] = [t for t in trials if t["evidence"] != "evaluated" or supplied_negative(t)]
    return record


def capped_heat_diagnosis(route, point, screen):
    """Retain the capped heat calculations and their phase-search resolution."""
    spec = route.bind(point)
    observations = {row["identity"]: row for pool in ("fitted", "comparisons")
                    for row in spec.inputs["observations"][pool]
                    if row["constructor"] == "saturation_capped_addition_enthalpy"}
    rows = []
    for search in screen["rows"]:
        identity, _, suffix = search["key"].rpartition(":")
        if suffix != "cap" or identity not in observations or search["available"]:
            continue
        row = observations[identity]
        initial = spec.problems[row["initial"]]
        rows.append(dict(key=search["key"], T_K=initial.T, P_Pa=row["arguments"]["P"],
                         source=row["row"], observed=row["arguments"]["observed"], status=search["status"],
                         message=search["message"],
                         cause=search.get("cause") or search["message"],
                         minimum=search.get("raw_minimum"), uncertainty=search.get("uncertainty")))
        if search.get("raw_minimum") is not None:
            state = dict(key=search["key"], cap_record=identity)
            item = stability_row(route, spec, state, 1.0, cap_from_prediction=True)
            prediction = reg.predict(spec.model, item)
            rows[-1]["trials"] = [dict(evidence=trial.evidence, message=trial.message,
                                       support=list(trial.phase.support), quantities=dict(trial.quantities))
                                  for trial in prediction.stability.report.trials]
    return dict(wheel=screen["wheel"], endpoint_fingerprint=screen["endpoint_fingerprint"], rows=rows)


def fresh_searches(amine, route, point, target):
    """Search the W declarations at the selected endpoint."""
    from time import monotonic

    from .fit import fingerprint, save
    from .records import RESULTS, ROOT, read

    wheel, endpoint = verify(), fingerprint(point)
    spec = route.bind(point)
    declared = states(route, spec)
    aliases = same_calculations(route, point, declared)
    if amine == "mea":
        bank = read(ROOT / "analyses/mea_parameter_bundle/results/reduced-refit/split-trials.json")
        protocols = {"grid": bank}
    elif amine == "mdea":
        bank = read(ROOT / "analyses/mdea_mea_workflow/results/retransfer-343/binary-penalty/split-record.json")
        protocols = {"declared": bank["trials"] + bank.get("supplied_trials", [])}
    else:
        bank = route.load(route.config["split_record"])["trials"]
        if amine == "amp":
            path = ROOT / "analyses/amp_transfer/results/retransfer-344-05e94210/campaign"
            saved = read(path / "new-witnesses.json.gz")
            count = read(path / "start-0/retreat-disposition.json")["initial_trial_count"]
            protocols = {"native": [], "supplied": bank + saved["additional"][:count - saved["initial"]]}
        else:
            protocols = {"declared": bank}

    checks = {}
    unique = [state for state in declared if state["key"] not in aliases]
    settings = dict(max_workers=int(os.environ["AGENT_HEAVY_CORES"]), mp_context=get_context("fork"),
                    initializer=_bind_search)
    for protocol, witnesses in protocols.items():
        start = monotonic()
        searches = {}
        with ProcessPoolExecutor(**settings, initargs=(route, point, witnesses)) as pool:
            for row in pool.map(_search, unique, chunksize=4):
                searches[row["key"]] = row["search"]
                if len(searches) % 100 == 0:
                    print(amine, protocol, len(searches), len(unique), f"{monotonic() - start:.1f} s", flush=True)
        descents = [dict(row, key=key, native_branch=density_branch(row.get("witnesses", [])),
                         supplied_branch=density_branch([trial["quantities"] for trial in row.get("supplied_trial_evidence", [])
                                                         if supplied_negative(trial)]))
                    for key, row in searches.items() if search_descent(row)]
        searches.update({key: searches[source] for key, source in aliases.items()})
        rows = [dict(searches[state["key"]], key=state["key"]) for state in declared]
        payload = dict(wheel=wheel, endpoint_fingerprint=endpoint, rows=rows, aliases=aliases,
                       seconds=monotonic() - start)
        save(target / f"{protocol}.json.gz", payload)
        confirmations = confirm_descents(route, point, descents, declared) if amine != "mea" else []
        save(target / f"{protocol}.json.gz", dict(payload, classifications=confirmations, seconds=monotonic() - start))
        checks[protocol] = dict(counts=dict(Counter(search_class(row) for row in rows)),
                               seconds=monotonic() - start)
        if amine == "mdea":
            save(target / "capped-heat-diagnosis.json.gz", capped_heat_diagnosis(route, point, payload))
    if amine == "mea":
        requests = RESULTS / "mea/reported/phase/requests"
        bank = read(ROOT / "analyses/mea_parameter_bundle/results/reduced-refit/split-registry.json")["trials"]
        bank = [dict(witness, kind=witness["kind"].capitalize()) for witness in bank]
        for protocol, calculate in (("measured", _measured), ("census", _census)):
            start = monotonic()
            with ProcessPoolExecutor(**settings, initargs=(route, point, bank)) as pool:
                rows = list(pool.map(calculate, read(requests / f"{protocol}.json.gz"), chunksize=4))
            save(target / f"{protocol}.json.gz", dict(wheel=wheel, endpoint_fingerprint=endpoint, rows=rows,
                                                     seconds=monotonic() - start))
    return dict(protocols=checks)


def reported_searches(amine, fit_set, route, point, target):
    from .fit import fingerprint, save
    from .model import REPORTED
    from .records import ROOT, read

    wheel, endpoint = verify(), fingerprint(point)
    spec = route.bind(point)
    declared = states(route, spec)
    keys = {state["key"] for state in declared}
    if amine == "mea":
        record = read(REPORTED / "MEA/screen/grid.json.gz")
        cases = [("grid", record, record["data"], {},
                  read(ROOT / "analyses/mea_parameter_bundle/results/reduced-refit/split-trials.json"))]
    else:
        if amine == "mdea":
            bank = read(ROOT / "analyses/mdea_mea_workflow/results/retransfer-343/binary-penalty/split-record.json")
        else:
            bank = route.load(route.config["split_record"])
        if amine == "amp":
            path = ROOT / "analyses/amp_transfer/results/retransfer-344-05e94210/campaign"
            saved = read(path / "new-witnesses.json.gz")
            manifest = read(path / "start-0/retreat-disposition.json")
            bank["trials"] += saved["additional"][:manifest["initial_trial_count"] - saved["initial"]]
            design = "AMP_free"
            domains = [(design, "selected", protocol) for protocol in ("native", "supplied")]
        else:
            domains = [(amine.upper(), "rebuild-441" if amine == "dea" else "selected", "declared")]
        witnesses = bank["trials"] + bank.get("supplied_trials", [])
        witnesses.sort(key=lambda witness: not witness.get("resolved_descent"))
        cases = []
        for design, lane, protocol in domains:
            record = read(REPORTED / design / "screen" / lane / protocol / "summary.json.gz")
            cases.append((protocol, record, record["rows"], record["aliases"], witnesses if protocol != "native" else []))
    checks = {}
    for protocol, record, retained, aliases, witnesses in cases:
        retained_keys = {row["key"] for row in retained}
        changed_keys = retained_keys ^ keys
        if changed_keys and (amine != "mdea" or any(not key.startswith("grid:") for key in changed_keys)):
            raise ValueError(f"{amine} {fit_set} {protocol}: measured state request keys differ")
        aliases = {key: source for key, source in aliases.items() if key in keys and source in keys}
        if record["wheel"] != wheel or record["endpoint_fingerprint"] != endpoint:
            raise ValueError(f"{amine} {fit_set} {protocol}: phase baseline belongs to a different wheel or endpoint")
        distinct = [state for state in declared if state["key"] not in aliases]
        with ProcessPoolExecutor(max_workers=int(os.environ["AGENT_HEAVY_CORES"]), mp_context=get_context("fork"),
                                 initializer=_bind_search, initargs=(route, point, witnesses)) as pool:
            searches = {row["key"]: row["search"] for row in pool.map(_search, distinct, chunksize=4)}
        confirmations = []
        if "classifications" in record:
            descents = [dict(row, key=key, native_branch=density_branch(row.get("witnesses", [])),
                             supplied_branch=density_branch([trial["quantities"] for trial in row.get("supplied_trial_evidence", [])
                                                             if supplied_negative(trial)]))
                        for key, row in searches.items() if search_descent(row)]
            confirmations = confirm_descents(route, point, descents, declared)
        searches.update({key: searches[source] for key, source in aliases.items()})
        def identity(row):
            return search_class(row), row.get("status"), row.get("event")
        differences = [dict(key=row["key"], retained=identity(row), replayed=identity(searches[row["key"]]))
                       for row in retained if row["key"] in keys and identity(row) != identity(searches[row["key"]])]
        save(target / f"{protocol}.json.gz", dict(wheel=wheel, endpoint_fingerprint=endpoint, rows=searches,
                                                 classifications=confirmations))
        checks[protocol] = dict(rows=len(searches), aliases=aliases, differences=differences,
                               removed_grid_keys=sorted(retained_keys - keys), new_grid_keys=sorted(keys - retained_keys),
                               confirmation_differences=compare_confirmations(record.get("classifications", []), confirmations))
    if amine == "mea":
        from .records import RESULTS

        folder = RESULTS / "mea/reported/phase"
        held = [row for path in sorted((folder / "measured").glob("*.json.gz")) for row in read(path)]
        bank = read(ROOT / "analyses/mea_parameter_bundle/results/reduced-refit/split-registry.json")["trials"]
        bank = [dict(witness, kind=witness["kind"].capitalize()) for witness in bank]
        census = read(folder / "screen/census-raw.json.gz")["data"]
        with ProcessPoolExecutor(max_workers=int(os.environ["AGENT_HEAVY_CORES"]), mp_context=get_context("fork"),
                                 initializer=_bind_search, initargs=(route, point, bank)) as pool:
            results = list(pool.map(_census, census, chunksize=4))
            measured = list(pool.map(_measured, held, chunksize=4))
        census_differences = [new["index"] for old, new in zip(census, results, strict=True)
                              if old["classification"] != new["classification"]]
        save(target / "census.json.gz", dict(wheel=wheel, endpoint_fingerprint=endpoint, rows=results))
        checks["census"] = dict(rows=len(results), differences=census_differences)
        fields = ("identity", "declared_parent", "feed_mol", "P_Pa", "T_K", "row_tolerance", "available")
        differences = [new["identity"] for old, new in zip(held, measured, strict=True)
                       if any(old.get(key) != new.get(key) for key in fields)
                       or bool(old["witnesses"]) != new["descent"]]
        save(target / "measured.json.gz", dict(wheel=wheel, endpoint_fingerprint=endpoint, rows=measured))
        checks["measured"] = dict(rows=len(measured), differences=differences)
    elif amine != "mdea":
        controls = reported_controls(amine, design, route, spec, endpoint)
        save(target / "controls.json.gz", controls)
        checks["controls"] = dict(rows=len(controls["rows"]), differences=controls["differences"])
    return dict(protocols=checks)
