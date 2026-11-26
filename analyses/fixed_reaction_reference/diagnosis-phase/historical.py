"""Evaluate L+V at the historical target pressures on each control's own references."""

from copy import copy, deepcopy
from math import log
from pathlib import Path
import sys
from time import monotonic

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent))
import refit
from calculations import mdea_incumbent
from mdea_reference import route, FixedReference
from phases import cd, dilute_vapor_connection, physical, trials
from part_ii import calculation_declaration, eq
from reaction_reference import references
from scipy.optimize import brentq
from round_8.reductions import parent_agreement


def rows():
    from closure import c

    for family in ("salt", "historical"):
        for label in ("original", "rms", "fixed"):
            if label == "fixed" and family != "salt":
                continue
            run = (
                route(family, "diagnosis-phase/" + label, FixedReference)
                if label == "fixed"
                else route(family, "diagnosis-phase/" + label)
            )
            point = (
                mdea_incumbent(family)[0]
                if label != "rms"
                else c.r.read(c.refit.ROUND7 / f"C/{family}/selection.json.gz")[
                    "selected"
                ][2]
            )
            spec = run.bind(point)
            template = spec.problems[
                next(r["bubble"] for r in c.ROWS if r["group"] == "Merkley")
            ]
            controls = c.r.read(
                c.refit.ROUND7
                / f"C/{family}/{'original' if label == 'fixed' else label}-fixed-pressures.json.gz"
            )
            for key in ("pressure_121_MPa", "pressure_262_MPa"):
                q = controls[key]
                if (
                    label == "fixed"
                    and key != "pressure_121_MPa"
                    or label != "fixed"
                    and any(a["confirmed"] for a in q["attempts"])
                ):
                    continue
                t = monotonic()
                p = copy(template)
                p.T, p.P = q["T_K"], q["P_Pa"]
                p.feed = copy(template.feed)
                p.feed.values = q.get("feed") or dict(zip(q["species"], q["feed_mol"]))
                p.phases = [copy(z) for z in template.phases]
                p.phases[-1].amount = c.refit.eq.Free()
                if label == "fixed":
                    a = c.r.read(c.refit.ROUND7 / "A/reference.json.gz")["comparisons"][
                        "100 kPa"
                    ]["attempts"][0]
                    for i, ph in enumerate(p.phases):
                        ph.composition_guess = {
                            k: a["phases"][i][spec.parameters.component_ids.index(k)]
                            for k in ph.support
                        }
                        ph.packing_guess = a["packings"][i]
                n = p._native(spec.parameters)
                if label == "fixed":
                    references(n, True)
                    assert all(
                        rx.reference.reference_pressure_pa == 100000
                        for rx in n.reactions
                    )
                s = c.refit.eq.solve_equilibrium(spec.model, n)
                out = dict(
                    family=family,
                    weights=label,
                    T=p.T,
                    P=p.P,
                    message=s.message,
                    amounts=list(s.amounts),
                )
                if s.success and s.requested_tolerance_met and min(s.amounts) > 0:
                    out.update(physical(spec, n, s))
                    g = cd.gibbs(c.refit.eq.compile_problem(spec.model, n), s)
                    out["trace"] = dilute_vapor_connection(
                        spec.model, p.T, s.phase_mole_fractions(1), s.molar_densities[1]
                    )
                    n.phases = n.phases[:1]
                    parent = c.refit.eq.solve_equilibrium(spec.model, n)
                    if parent.success:
                        pg = cd.gibbs(c.refit.eq.compile_problem(spec.model, n), parent)
                        out.update(decrease=pg[0] - g[0], error=pg[1] + g[1])
                yield dict(out, seconds=monotonic() - t)


def lift_parameters(seed, target):
    lifted = deepcopy(target)
    laws = {c['identity']:c['temperature_law'] for pair in seed['pairs']
            for c in pair['coefficients'] if 'temperature_law' in c}
    for pair in lifted['pairs']:
        for coefficient in pair['coefficients']:
            key = coefficient['identity']
            if key not in {f'pair/{ion}/water/k_ij' for ion in ('bicarbonate-anion','carbonate-anion')}:
                continue
            k = coefficient.pop('value')['magnitude']
            law = coefficient['temperature_law'] = deepcopy(laws[key])
            assert [t['power'] for t in law['terms']]==[0,1], key
            for term,value in zip(law['terms'],(k,0.),strict=True):
                term['coefficient']['value']['magnitude'] = value
    return lifted


def deciding_path(run, seed_point, target_point, archive, target, output, *, lift):
    started = monotonic()
    seed_mapping, target_mapping = seed_point['parameters'], target_point['parameters']
    lifted = lift_parameters(seed_mapping,target_mapping) if lift else target_mapping
    T,P = target['T_K'],target['P_Pa']
    saved = dict(wheel=refit.r.SHA, endpoint_fingerprint=refit.fingerprint(target_point),
                 T_K=T,P_Pa=P,feed_mol=target['feed_mol'],path=[],fixed_reaction_reference_Pa=refit.P_REF)

    def declaration(mapping, reference):
        spec = run.bind(dict(target_point,parameters=mapping))
        name = next(q['bubble'] for q in spec.inputs['observations']['fitted'] if q['group']=='Merkley')
        p = copy(spec.problems[name])
        p.T,p.P,p.feed = T,P,eq.Amounts(dict(zip(target['species'],target['feed_mol'],strict=True)))
        p.phases = [copy(phase) for phase in p.phases]
        p.phases[-1].amount = eq.Free()
        for i,phase in enumerate(p.phases):
            x = archive['phases'][i]['x']
            phase.composition_guess = {k:x[target['species'].index(k)] for k in phase.support}
            phase.packing_guess = archive['phases'][i]['density_mol_m3']*spec.model._model.packing_fraction_coefficient(T,x)
        native = p._native(spec.parameters)
        if reference is not None:
            reactions = native.reactions
            for rx in reactions:
                if rx.reference.reference_pressure_pa is None:
                    rx.reference = eq.ReactionReference(rx.reference.source_basis,reference_pressure_pa=reference)
            native.reactions = reactions
        return spec,native

    def center(spec,problem, options=None):
        phases = problem.phases
        problem.phases = phases[:1]
        try:
            solved = eq.solve_equilibrium(spec.model,problem)
            row = dict(message=solved.message)
            if not solved.requested_tolerance_met or not solved.amounts:
                return row,None
            compiled = eq.compile_problem(spec.model,problem)
            g,error = cd.gibbs(compiled,solved)
            row.update(x=list(solved.phase_mole_fractions(0)),density_mol_m3=solved.molar_densities[0],
                       amount_mol=solved.amounts[0],Gibbs_over_RT_mol=g,error=error,
                       **physical(spec,problem,solved))
            return row,eq.stability_test(compiled,solved,options) if options is not None else None
        finally:
            problem.phases = phases

    def node(t):
        reference = refit.P_REF*(P/refit.P_REF)**t
        return declaration(refit.r.segment(seed_mapping,lifted,t),reference)

    try:
        spec,direct = declaration(target_mapping,None)
        _,tracking_at_pressure = declaration(target_mapping,P)
        saved['declared'],saved['tracking_at_pressure'] = map(calculation_declaration,(direct,tracking_at_pressure))
        assert refit.remove_reference_pressure(saved['declared'])==refit.remove_reference_pressure(saved['tracking_at_pressure'])
        assert saved['declared']['reactions']==target['declaration']['reactions'], 'archived target reactions differ'
        assert [rx.reference.reference_pressure_pa for rx in direct.reactions]==[None,None,None,refit.P_REF]
        direct_parent,_ = center(spec,direct)
        lifted_spec,lifted_problem = declaration(lifted,None)
        lifted_parent,_ = center(lifted_spec,lifted_problem)
        saved.update(direct_parent=direct_parent,lifted_parent=lifted_parent)
        assert direct_parent.get('physical_checks_pass') and lifted_parent.get('physical_checks_pass'), 'target parent closure'
        assert parent_agreement(lifted_parent,direct_parent), 'lifted target parent differs from declared target'
        start = None
        for i in range(21):
            t = i/20
            spec,p = node(t)
            parent,_ = center(spec,p)
            assert parent.get('physical_checks_pass'), parent
            result = eq.solve_equilibrium(spec.model,p,start)
            row = dict(t=t, message=result.message, amounts=list(result.amounts),parent=parent)
            saved['path'].append(row)
            if not (result.requested_tolerance_met and len(result.amounts)==2 and min(result.amounts)>0):
                assert 'vanished' in result.message, result.message
                assert i>0, 'retained seed did not give two phases'
                break
            compiled = eq.compile_problem(spec.model,p)
            g,error = cd.gibbs(compiled,result)
            x = [list(result.phase_mole_fractions(j)) for j in (0,1)]
            rho = list(result.molar_densities)
            trace,connected = dilute_vapor_connection(spec.model,T,x[1],rho[1])
            row.update(physical(spec,p,result), coordinates=list(result.coordinates),
                       reduced_curvature=result.reduced_hessian_minimum, vapor_trace=trace, vapor_connected=connected,
                       distinct=cd.distinct_phases(x,rho),
                       decrease=parent['Gibbs_over_RT_mol']-g,error=parent['error']+error)
            start = result
        endpoint, endpoint_problem = node(1.)
        saved['endpoint_parent'],_ = center(endpoint,endpoint_problem)
        assert parent_agreement(saved['endpoint_parent'],direct_parent), 'path endpoint parent differs from declared target'
        if start is result:
            assert row['physical_checks_pass'] and row['vapor_connected'] and row['decrease']>row['error']
            assert row['distinct']
            saved['outcome'] = 'liquid plus vapor-connected phase'
        else:
            opts = eq.StabilityOptions()
            opts.mode = type(opts.mode).Full
            searched_parent, report = center(run.bind(target_point),direct,opts)
            saved['target_search'] = dict(message=report.message,completed=report.completed,
                                          no_descent=report.no_descent_in_trial_set,trials=trials(report),
                                          parent=searched_parent)
            crossing = saved['crossing'] = []
            daughter = saved['path'][-2]['phases'][1]

            def tangent_plane(t):
                spec,p = node(t)
                options = eq.StabilityOptions()
                options.mode = type(options.mode).Full
                options.trials = p.phases[-1:]
                _, report = center(spec,p,options)
                trial_rows = trials(report)
                sample = dict(t=t,message=report.message,trials=trial_rows)
                crossing.append(sample)
                admissible = [v for v in trial_rows if (v['descent'] or v['evidence']=='no_resolved_descent')
                              and 'tpd_over_rt' in v['quantities']]
                assert admissible, f'no vapor tangent-plane value at path parameter {t}'
                match = min(admissible,key=lambda v:max(
                    abs(log(daughter['density_mol_m3']*v['quantities']['volume_m3_per_mol'])),
                    max(abs(a-b) for a,b in zip(daughter['x'],v['composition'],strict=True))))
                sample['matched_seed'] = match['seed']
                return match['quantities']['tpd_over_rt']

            root = brentq(tangent_plane,saved['path'][-2]['t'],t)
            residual = tangent_plane(root)
            match = next(q for q in crossing[-1]['trials'] if q['seed']==crossing[-1]['matched_seed'])
            assert abs(residual)<=match['quantities']['association_energy_estimate_over_rt'], (
                f'vapor tangent-plane zero did not close: {residual}')
            saved['zero_amount_crossing'] = root
            assert report.completed and report.no_descent_in_trial_set, report.message
            saved['outcome'] = 'no descent in the finite search'
    except (AttributeError, AssertionError, RuntimeError, ValueError) as error:
        saved['blocker'] = f'{type(error).__name__}: {error}'
    finally:
        refit.save(output,dict(saved,seconds=monotonic()-started))
    return saved


if __name__ == "__main__":
    from closure import c

    tick = monotonic()
    c.refit.save(
        c.refit.WORK / "diagnosis-phase/historical.json.gz",
        dict(wheel=c.r.SHA, rows=list(rows()), seconds=monotonic() - tick),
    )
