"""Qualify the Engine's first-order temperature reference chain on the adopted MEA model (#84).

Rows, one CSV each:
- actions: Engine A1 temperature actions of liquid true-species mole fractions (and the
  solved pressure for VLE) against centered re-solves at two steps, 315-360 K;
- slopes: per-reaction RT^2 dC_r/dT at held pressure (centered terminal contractions);
- attribution: Delta(d ln pCO2/dT) = sum_r S_r dC_r/dT|_P with S_r = d ln pCO2/d ln K_r
  from centered re-solves at fixed T (pressure response retained);
- water: the declared pure-water reference point against Wagner-Pruss (2002).

Run with an explicitly supplied candidate wheel installed; its SHA-256 is recorded.
"""
from __future__ import annotations

import copy
import csv
import hashlib
import importlib.metadata
import json
import math
from pathlib import Path
from urllib.parse import unquote, urlparse

import shared_evaluation as shared
from epcsaft import GAS_CONSTANT_J_PER_MOL_K as R
from epcsaft import equilibrium

OUTPUT = Path(__file__).resolve().parents[1] / "results" / "reference-temperature"
TEMPERATURES_K = (315.0, 330.0, 345.0, 360.0)
SOURCE_UPPER_K = {"R4": 323.15, "R5": 323.15}  # common source intersection 293.15-323.15 K
STEPS_K = (0.04, 0.02)
ACTION_RTOL, ACTION_ATOL = 1e-5, 1e-12
LOG_K_STEP = 1e-3
WATER = shared.COMPONENT_IDS.index("water")
CO2 = shared.COMPONENT_IDS.index("carbon-dioxide")


def wheel_sha256() -> str:
    url = json.loads(importlib.metadata.distribution("epcsaft").read_text("direct_url.json") or "{}")["url"]
    return hashlib.sha256(Path(unquote(urlparse(url).path)).read_bytes()).hexdigest()


def request_at(base: dict, temperature: float, pressure: float | None = None,
               liquid_only: bool = False, shift: tuple[int, float] | None = None) -> dict:
    request = copy.deepcopy(base)
    request["temperature"]["value"] = temperature
    if pressure is not None:
        request["pressure"] = {"role": "fixed", "value": pressure, "bounds": [1.0, 1.0e7]}
    if liquid_only:
        request["phases"] = [p for p in request["phases"] if p["fluid_role"] == "liquid"]
    if shift is not None:
        index, delta = shift
        request["reaction_system"]["engine_reactions"][index]["engine_correlation"]["a"] += delta
    return request


def anchor(problem: object, result: object) -> tuple[shared.Anchor, dict[str, list[float]]]:
    """The solved state as the continuation guess for neighbouring re-solves."""
    width = len(shared.COMPONENT_IDS)
    liquid = phase_index(problem, "liquid")
    phases = {p.name: [result.mole_fractions[i * width + shared.COMPONENT_IDS.index(c)]
                       for c in (p.support or shared.COMPONENT_IDS)]
              for i, p in enumerate(problem.phases)}
    return shared.Anchor(0, 0.0, result.pressure[0],
                         tuple(result.mole_fractions[liquid * width:(liquid + 1) * width]),
                         1.0 / result.molar_densities[liquid]), phases


def solve(model: object, request: dict,
          guess: tuple[shared.Anchor, dict[str, list[float]]] | None = None) -> tuple[object, object]:
    problem = shared._problem_from_request(request, None if guess is None else guess[0])
    if guess is not None:
        problem.phases = [equilibrium.Phase(p.name, support=p.support, kind=p.kind, amount=p.amount,
                                            composition_guess=guess[1].get(p.name, p.composition_guess))
                          for p in problem.phases]
    result = equilibrium.solve_equilibrium(model, problem)
    if not result.success or max(map(abs, result.residuals)) > 1e-9:
        raise RuntimeError(f"solve failed at T={request['temperature']['value']}: {result.message}")
    return problem, result


def observables(problem: object) -> list[tuple[str, object, callable]]:
    liquid = phase_index(problem, "liquid")
    rows = [(f"x_L:{c}", equilibrium.SolvedStateObservable(
        equilibrium.SolvedStateObservableKind.PhaseMoleFraction, liquid, i),
        lambda r, i=i, liquid=liquid: r.mole_fractions[liquid * len(shared.COMPONENT_IDS) + i])
        for i, c in enumerate(shared.COMPONENT_IDS)]
    if len(problem.phases) > 1:
        rows.append(("P", equilibrium.SolvedStateObservable(equilibrium.SolvedStateObservableKind.Pressure),
                     lambda r: r.pressure[0]))
    return rows


def phase_index(problem: object, role: str) -> int:
    return next(i for i, p in enumerate(problem.phases) if str(getattr(p.kind, "name", p.kind)).lower() == role)


def pco2(result: object, problem: object) -> float:
    vapor = phase_index(problem, "vapor")
    return result.pressure[0] * result.mole_fractions[vapor * len(shared.COMPONENT_IDS) + CO2]


def contractions(model: object, base: dict, temperature: float, pressure: float,
                 warm: tuple[shared.Anchor, dict[str, list[float]]]) -> list[float]:
    _, result = solve(model, request_at(base, temperature, pressure, liquid_only=True), warm)
    return [d.terminal_contraction for d in result.neutral_reference_diagnostics]


def water_reference(temperature: float) -> tuple[float, float]:
    """Wagner and Pruss (2002) Eqs. 2.5-2.6: saturation pressure (Pa) and liquid density (mol/m^3)."""
    tc, pc, rhoc, tau = 647.096, 22.064e6, 322.0 / 0.01801528, 1.0 - temperature / 647.096
    a = (-7.85951783, 1.84408259, -11.7866497, 22.6807411, -15.9618719, 1.80122502)
    e = (1.0, 1.5, 3.0, 3.5, 4.0, 7.5)
    psat = pc * math.exp(tc / temperature * sum(ai * tau**ei for ai, ei in zip(a, e)))
    b = (1.99274064, 1.09965342, -0.510839303, -1.75493479, -45.5170352, -6.74694450e5)
    f = (1 / 3, 2 / 3, 5 / 3, 16 / 3, 43 / 3, 110 / 3)
    return psat, rhoc * (1.0 + sum(bi * tau**fi for bi, fi in zip(b, f)))


def write(name: str, rows: list[dict]) -> str:
    path = OUTPUT / f"{name}.csv"
    with path.open("w", newline="") as stream:
        writer = csv.DictWriter(stream, fieldnames=list(rows[0]), lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main() -> None:
    OUTPUT.mkdir(parents=True, exist_ok=True)
    model = shared.epcsaft.Mixture(shared.load_parameters())
    reactions = shared._selected_reactions()
    packet = {o["identity"]: o["request"] for o in shared.load_state_packet()["observations"]}
    speciation = shared.corrected_request(packet["Bottinger2008_state_058"], reactions)
    vle = shared.corrected_request(packet["vle_obs_0130"], reactions)
    states = [(f"058@{t:g}K", speciation, t) for t in TEMPERATURES_K]
    states.append(("vle_obs_0130", vle, float(vle["temperature"]["value"])))
    names = [r["reaction_id"] for r in speciation["reaction_system"]["engine_reactions"]]
    actions, slopes, attribution, water = [], [], [], []
    warm: tuple[shared.Anchor, dict[str, list[float]]] | None = None
    for label, base, temperature in states:
        try:
            problem, central = solve(model, request_at(base, temperature))
        except RuntimeError:
            if warm is None:
                raise
            problem, central = solve(model, request_at(base, temperature), warm)
        warm = anchor(problem, central)
        compiled = equilibrium.compile_problem(model, problem)
        items = observables(problem)
        batch = equilibrium.solved_state_actions(compiled, central, equilibrium.SolvedStateActionRequest(
            [o for _, o, _ in items], [equilibrium.SolvedStateActionDirection(
                1.0, 0.0, [0.0] * len(shared.COMPONENT_IDS), [])]))
        differences = []
        for step in STEPS_K:
            upper = solve(model, request_at(base, temperature + step), warm)[1]
            lower = solve(model, request_at(base, temperature - step), warm)[1]
            differences.append([(g(upper) - g(lower)) / (2 * step) for _, _, g in items])
        for (name, _, _), item, coarse, fine in zip(items, batch.results, *differences):
            action = item.action
            passed = (item.status.name == "Available" and action is not None
                      and abs(action - fine) <= ACTION_ATOL + ACTION_RTOL * abs(fine))
            actions.append({"state": label, "T_K": temperature, "observable": name,
                            "status": item.status.name, "action_per_K": action,
                            "resolve_fine_per_K": fine, "resolve_coarse_per_K": coarse,
                            "passed": passed})
        pressure = central.pressure[0]
        lower_c = contractions(model, base, temperature - STEPS_K[1], pressure, warm)
        upper_c = contractions(model, base, temperature + STEPS_K[1], pressure, warm)
        center = central.neutral_reference_diagnostics
        dct = []
        for index, name in enumerate(names):
            slope = (upper_c[index] - lower_c[index]) / (2 * STEPS_K[1])
            dct.append(slope)
            slopes.append({"state": label, "T_K": temperature, "reaction": name,
                           "reference_pressure_pa": center[index].reference_pressure_pa,
                           "dC_dT_per_K": slope, "RT2_dC_dT_kJ_per_mol": R * temperature**2 * slope / 1e3,
                           "observed_terminal_change": center[index].observed_terminal_change,
                           "source_extrapolated": temperature > SOURCE_UPPER_K.get(name, math.inf)})
        if len(problem.phases) > 1:
            ln_p = math.log(pco2(central, problem))
            sensitivity = []
            for index in range(len(names)):
                up = solve(model, request_at(base, temperature, shift=(index, LOG_K_STEP)), warm)
                down = solve(model, request_at(base, temperature, shift=(index, -LOG_K_STEP)), warm)
                sensitivity.append((math.log(pco2(up[1], up[0])) - math.log(pco2(down[1], down[0])))
                                   / (2 * LOG_K_STEP))
            change = math.fsum(s * d for s, d in zip(sensitivity, dct))
            fd = solve(model, request_at(base, temperature + STEPS_K[1]), warm)
            fd_lower = solve(model, request_at(base, temperature - STEPS_K[1]), warm)
            total = (math.log(pco2(fd[1], fd[0])) - math.log(pco2(fd_lower[1], fd_lower[0]))) / (2 * STEPS_K[1])
            for index, name in enumerate(names):
                attribution.append({"state": label, "T_K": temperature, "reaction": name,
                                    "S_dlnpCO2_dlnK": sensitivity[index], "dC_dT_per_K": dct[index],
                                    "contribution_per_K": sensitivity[index] * dct[index]})
            attribution.append({"state": label, "T_K": temperature, "reaction": "sum",
                                "S_dlnpCO2_dlnK": None, "dC_dT_per_K": None, "contribution_per_K": change})
            attribution.append({"state": label, "T_K": temperature, "reaction": "total_dlnpCO2_dT",
                                "S_dlnpCO2_dlnK": math.exp(ln_p), "dC_dT_per_K": None,
                                "contribution_per_K": total})
        for reference_pressure in sorted({d.reference_pressure_pa for d in center}):
            state = model.state(temperature, P=reference_pressure,
                                x=[1.0 if i == WATER else 0.0 for i in range(len(shared.COMPONENT_IDS))],
                                phase="liquid")
            psat, rho_sat = water_reference(temperature)
            correction = 5.0e-10 * abs(reference_pressure - psat)  # |kappa_T dP|, kappa_T <= 5e-10 /Pa
            deviation = state.molar_density / rho_sat - 1.0
            water.append({"state": label, "T_K": temperature, "reference_pressure_pa": reference_pressure,
                          "rho_eos_mol_m3": state.molar_density, "rho_wagner_pruss_sat_mol_m3": rho_sat,
                          "psat_wagner_pruss_pa": psat, "pressure_correction_bound": correction,
                          "relative_deviation": deviation, "dP_drho": state.pressure_density_derivative,
                          "branch": state.density_branch.name, "below_psat": reference_pressure < psat,
                          "passed": state.pressure_density_derivative > 0.0
                          and abs(deviation) + correction <= 0.05})
        print(label, "done", flush=True)
    hashes = {name: write(name, rows) for name, rows in
              (("actions", actions), ("slopes", slopes), ("attribution", attribution), ("water", water))}
    shared.write_json(OUTPUT / "summary.json", {
        "engine_wheel_sha256": wheel_sha256(),
        "producer_sha256": hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
        "parameter_sha256": shared.sha256(shared.PARAMETERS), "csv_sha256": hashes,
        "action_criterion": f"|A - FD| <= {ACTION_ATOL} + {ACTION_RTOL}|FD|, FD centered at {STEPS_K[1]} K",
        "water_criterion": "dP/drho > 0 and |rho/rho_sat - 1| + 5e-10 |P - Psat| <= 0.05 (branch identification)",
        "actions_passed": sum(r["passed"] for r in actions), "actions_total": len(actions),
        "water_passed": sum(r["passed"] for r in water), "water_total": len(water),
        "claim_limit": "Numerical qualification of the reference-chain slope on one adopted model; "
                       "not empirical accuracy or calorimetric heat; R4/R5 above 323.15 K are source extrapolation.",
    })
    if not all(r["passed"] for r in actions + water):
        raise RuntimeError("temperature-reference discrepancy retained in the CSV")


if __name__ == "__main__":
    main()
