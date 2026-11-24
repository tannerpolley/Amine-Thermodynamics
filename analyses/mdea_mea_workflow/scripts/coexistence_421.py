"""Trial and coexistence evidence at the prescribed MDEA pressures (#421)."""
import math
import sys

from bounded_binary_411 import OLD
from part_ii import ROOT, eq, jsonable, reg, stable

sys.path.insert(0, str(ROOT/'analyses/amp_transfer'))
from classify_descents import classify, coexistence, gibbs, pressure_roots, ERROR_TERMS
from shared_bicarbonate_417 import vapor_at_parent

SPLIT_ONLY = 'feasible two-liquid equilibrium; bulk Gibbs comparison unavailable'


def salt_trials(spec, item, parent):
    ids = list(spec.parameters.component_ids)
    chosen = [ids.index(i) for i in ('water','bicarbonate-anion','protonated-methyldiethanolamine')]
    compiled = eq.compile_problem(spec.model,item.problem)
    for ion in (.10,.25):
        x = [0.]*len(ids)
        for i,v in zip(chosen,(1-2*ion,ion,ion),strict=True):
            x[i] = v
        seed = dict(kind='Liquid',support=chosen,composition=x)
        try:
            state = spec.model.state(parent.temperature,P=parent.pressure,x=x,phase='liquid')
            packing = state.molar_density*spec.model._model.packing_fraction_coefficient(parent.temperature,x)
            trials, absent, _, _ = stable._applicable(item,[dict(seed,packing=packing)],set(range(len(ids)))-set(compiled.removed_species))
            if absent:
                yield dict(seed, evidence=absent)
                continue
            options = eq.StabilityOptions()
            options.prepared_trials = eq.prepare_supplied_trials(spec.model,parent.temperature,trials)
            trial, = eq.stability_test(compiled,parent,options).trials
            yield dict(seed, evidence=trial.evidence, message=trial.message, prepared_composition=list(trial.composition), quantities=jsonable(trial.quantities))
        except (RuntimeError, ValueError) as error:
            yield dict(seed, refusal=str(error))


def fixed(route, spec):
    old = stable.read(OLD/'descent-and-penalty-diagnosis/two-liquid-equilibrium.json')
    T,P,feed = (old[k] for k in ('T_K','P_Pa','feed'))
    template = next(p for p in spec.problems.values() if p.reactions)
    declaration = eq.Problem(T=T,P=P,feed=eq.Amounts(feed), phases=[eq.Phase('L',kind='liquid',support=route.config['species'])],
                             reactions=template.reactions,neutral_reference=template.neutral_reference,row_tolerance=template.row_tolerance)
    item = reg.stability(spec.parameters,declaration,scale=1.)
    parent = eq.solve_equilibrium(spec.model,item.problem)
    native = reg.predict(spec.model,item)
    historic = old['attempts'][0]
    seeds = [(x,rho*spec.model._model.packing_fraction_coefficient(T,x)) for x,rho in zip(historic['composition'],historic['molar_densities_mol_m3'],strict=True)]
    g = gibbs(eq.compile_problem(spec.model,item.problem),parent) if parent.requested_tolerance_met else None
    guesses = [seeds]
    if g is not None:
        primary = (list(parent.phase_mole_fractions(0)),parent.packing_fractions[0])
        guesses.extend([primary,seed] for seed in seeds)
    attempts = [coexistence(spec,item.problem,g,guess) for guess in guesses]
    outcome = 'confirmed split' if any(a['confirmed'] for a in attempts) else SPLIT_ONLY if any(a.get('split_only') for a in attempts) else 'unresolved' if g else 'unavailable'
    route.write('fixed-pressure.json',dict(T_K=T,P_Pa=P,feed=feed,reference=historic,parent=parent.message,parent_g=g,native=native.message,
                                         outcome=outcome,guesses=guesses,attempts=attempts,salt=list(salt_trials(spec,item,parent)) if g else []))


def measured(route, point, spec, states, canonical, unfinished):
    missing = [states[k] for k in canonical if k not in unfinished]
    route.short_rows = True
    recovered = stable.grid(point,missing,stable.read(OLD/'split-record.json')['trials'],route=route)
    rows = {**unfinished,**{r['key']:r for r in recovered}}
    output = classify(route, point, [rows[k] for k in canonical], list(states.values()))
    for entry in output:
        k = entry['key']
        item = route.stability_row(spec,states[k],1.)
        parent = eq.solve_equilibrium(spec.model,item.problem)
        entry.update(pressure_basis=canonical[k], original=rows[k], salt=list(salt_trials(spec,item,parent)) if parent.requested_tolerance_met else [])
        entry['pressure_closed_vapor'] = [vapor_at_parent(spec.model,entry,t) for t in entry.get('supplied_pressure_roots',[])]
    route.write('measured-phase.json',output)
