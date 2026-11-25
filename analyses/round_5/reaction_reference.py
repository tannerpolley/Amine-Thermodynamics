"""Compare aqueous reaction references at identical physical temperatures and pressures."""
from pathlib import Path
from tempfile import TemporaryDirectory
from time import monotonic
import argparse
import math

from common import ROOT, RESULTS, fingerprints, save
from part_ii import Route, epcsaft, eq, np, stable
from phases import BOUNDED, MDEA, fixed, physical, trials
from classify_descents import coexistence, gibbs
from recall import DECLARATION, ENDPOINTS
from mea import references, source_log_k

ROUND3 = ROOT / 'analyses/round_3/results'
AMP_RECORD = ROOT / 'analyses/mea_parameter_bundle/results/reference-states-428/amp.json'
AMP_VERIFICATION = ROOT / 'analyses/mea_parameter_bundle/results/split-diagnosis-433/verification.json'
R = epcsaft.GAS_CONSTANT_J_PER_MOL_K


class FixedReference(Route):
    def stability_row(self, spec, state, scale):
        item = super().stability_row(spec, state, scale)
        references(item.problem, True)
        return item


def reference_readback(route, spec, state, T, P, outcome):
    item = route.stability_row(spec, state, 1.)
    problem = item.problem
    problem.pressure = type(problem.pressure).fixed(P)
    model = spec.model
    nu = np.array([r.stoichiometry for r in problem.reactions])
    z = np.array([spec.spec['element_formulas'][c]['charge'] for c in spec.model.component_ids])
    pivot = next(i for i, c in enumerate(spec.model.component_ids) if c.startswith('protonated-'))
    directions = np.delete(np.eye(len(z)) - np.outer(z / z[pivot], np.eye(len(z))[pivot]), pivot, axis=0)

    def read_standard(Ti, Pi, *, full=False):
        problem.temperature = type(problem.temperature).fixed(Ti)
        problem.pressure = type(problem.pressure).fixed(Pi)
        compiled = eq.compile_problem(model, problem)
        result = eq.solve_equilibrium(model, problem)
        if not result.requested_tolerance_met:
            raise ValueError(result.message)
        options = eq.StabilityOptions()
        if full:
            options.mode = type(options.mode).Full
        report = eq.stability_test(compiled, result, options)
        return np.asarray(report.standard_over_rt), result, report

    def raw(x, rho):
        return np.log(np.array(x) * rho) + model.state(T, rho=rho, x=x).residual_chemical_potential_over_rt

    standard, parent, report = read_standard(T, P, full=True)
    raw_parent = raw(parent.phase_mole_fractions(0), parent.molar_densities[0])
    activities = [a for a in eq.reaction_activities(model, parent) if a.phase_index == 0]
    reactions = []
    for rx, a, raw_contraction, completed in zip(problem.reactions, activities, nu @ raw_parent, nu @ standard, strict=True):
        ln_k = source_log_k(rx.correlation, T)
        pressure_standard = sum(rx.stoichiometry) * math.log(a.standard_pressure_pa / (R * T))
        fugacity_reference = a.log_pressure_quotient - a.log_quotient
        reactions.append(dict(name=rx.name, P_ref_Pa=a.reference_pressure_pa, ln_K=ln_k,
                              ln_Q=a.log_quotient, standard_contraction=completed, fugacity_reference=fugacity_reference,
                              pressure_standard_conversion=pressure_standard, raw_contraction=raw_contraction,
                              completion_error=completed + ln_k + fugacity_reference + pressure_standard))
    if not any(a['confirmed'] for a in outcome['attempts']):
        parent_g = gibbs(eq.compile_problem(model,problem),parent)
        for t in report.trials:
            if not (t.resolved_descent and t.split_coordinates and t.quantities.get('density_side')==2 and len(t.phase.support)==len(z)):
                continue
            coordinates = t.split_coordinates
            primary = (list(map(math.exp,coordinates[:len(z)])), math.exp(coordinates[len(z)+1]))
            pair = coexistence(spec,problem,parent_g,[primary,(list(t.composition),math.exp(coordinates[-1]))],
                               inspect=lambda c,s: physical(spec,problem,s) if s.requested_tolerance_met and len(s.amounts)==2 else None)
            outcome['attempts'].append(dict(pair,seed=t.seed))
            if pair['confirmed']:
                break
    attempts = []
    for a in outcome['attempts']:
        if not a.get('phases'):
            attempts.append(None)
            continue
        mu = [raw(x, rho) + standard for x, rho in zip(a['phases'], a['densities_mol_m3'], strict=True)]
        affinity = [nu @ v for v in mu]
        transfer = directions @ (mu[0]-mu[1])
        attempts.append(dict(affinities=affinity, charge_neutral_transfers=transfer,
                             affinity_within_tolerance=bool(np.max(np.abs(affinity))<=problem.row_tolerance),
                             charge_neutral_transfer_within_tolerance=bool(np.max(np.abs(transfer))<=problem.row_tolerance)))
    inventories = [np.array(parent.phase_mole_fractions(0)) * parent.amounts[0]]
    inventories.extend(sum(n * np.asarray(x) for n, x in zip(a['amounts_mol'], a['phases'], strict=True))
                       for a in outcome['attempts'] if 'phases' in a)
    derivatives = []
    for dt, dp in [(0.04, P * 1e-4), (0.02, P * 5e-5)]:
        record = dict(step_K=dt, step_Pa=dp)
        derivatives.append(record)
        try:
            ds_dp = (read_standard(T, P + dp)[0] - read_standard(T, P - dp)[0]) / (2 * dp)
            record['volume_m3'] = [float(n @ ds_dp * R * T) for n in inventories]
        except (ValueError, RuntimeError) as error:
            record['volume_refusal'] = str(error)
        lower = route.config['calculation_interval_K'][0]
        try:
            if T-dt < lower:
                ds_dt = (-3*standard+4*read_standard(T+dt,P)[0]-read_standard(T+2*dt,P)[0])/(2*dt)
                record['temperature_stencil'] = 'second-order forward at lower reaction-temperature limit'
            else:
                ds_dt = (read_standard(T+dt,P)[0]-read_standard(T-dt,P)[0])/(2*dt)
                record['temperature_stencil'] = 'centered'
            record['enthalpy_J'] = [float(-n @ ds_dt * R * T**2) for n in inventories]
        except (ValueError, RuntimeError) as error:
            record['enthalpy_refusal'] = str(error)
    return dict(standard_over_rt=standard, plane_over_rt=report.plane_over_rt, trial_records=trials(report),
                parent_affinities=nu @ (raw_parent + standard), row_tolerance=problem.row_tolerance,
                contractions=reactions, derivative_estimates=derivatives, pair_readback=attempts,
                added_reference_in_EOS_volume_and_calorics=False)


def feed_state(target):
    feed = dict(zip(target['species'], target['feed_mol'], strict=True))
    loading = feed.pop('carbon-dioxide')
    return dict(stock={c: amount for c, amount in feed.items() if amount}, T=target['T_K'], a=loading)


def calculate(work):
    start = monotonic()
    low, = (BOUNDED.parent / 'shared-bicarbonate-417/mdea').glob('mdea-low-*/endpoint.json.gz')
    q3, q4, q6 = [ROUND3 / f'q{i}.json' for i in (3, 4, 6)]
    amp = stable.read(AMP_RECORD)
    q6_record = stable.read(q6)
    assert all(amp[k] == q6_record[k] for k in ('feed_mol', 'T_K', 'P_Pa'))
    assert all(amp['split'][k] == q6_record['split'][k] for k in ('phases', 'packings', 'Gibbs_decrease_over_RT_mol', 'numerical_error_over_RT_mol'))
    targets = [dict(amp, key='S14', reference=-stable.read(AMP_VERIFICATION)['delta'],
                    reference_428=amp['split']['Gibbs_decrease_over_RT_mol'],
                    reference_error=amp['split']['numerical_error_over_RT_mol'], attempts=[amp['split']]),
               *stable.read(q3)['rows'][:2]]
    controls = stable.read(q4)['checks']
    records = []
    for i, target in enumerate(targets):
        declaration, endpoint = (DECLARATION, ENDPOINTS / 'main/parameters.json') if i == 0 else (MDEA, low)
        state = feed_state(target)
        assert state['stock'][stable.read(declaration)['amine']] == 1
        record = dict(key=target['key'], T_K=target['T_K'], P_Pa=target['P_Pa'], feed_mol=target['feed_mol'],
                      reference=target['reference'], reference_error=target['reference_error'], conventions={})
        if 'reference_428' in target:
            record['reference_428'] = target['reference_428']
        records.append(record)
        for label, route_class in (('baseline', Route), ('100-kPa', FixedReference)):
            route = route_class(declaration, work / str(i) / label)
            spec = route.bind(stable.read(endpoint))
            started = monotonic()
            result = record['conventions'][label] = {}
            try:
                result.update(fixed(route, spec, state, target['P_Pa'], dict(pair=target['attempts'][0]),
                                    mdea=i > 0, assemblages=i == 0))
                if label == 'baseline':
                    delta = result['attempts'][0].get('Gibbs_decrease_over_RT_mol')
                    result['within_reference_error'] = delta is not None and abs(delta - target['reference']) <= target['reference_error']
                    if 'reference_428' in target:
                        result['within_reference_428_error'] = delta is not None and abs(delta - target['reference_428']) <= target['reference_error']
                result.update(reference_readback(route, spec, state, target['T_K'], target['P_Pa'], result))
            except (ValueError, RuntimeError, AssertionError, AttributeError, TypeError) as error:
                result['refusal'] = f'{type(error).__name__}: {error}'
            result['seconds'] = monotonic() - started
        changed = record['conventions']['100-kPa']
        baseline = record['conventions']['baseline']
        record['phase_disposition'] = ('persists' if baseline.get('within_reference_error') and
                                       any(a['confirmed'] for a in changed.get('attempts', [])) else 'undecided')
        save('B/reactions.json.gz', dict(rows=records, Q4_control=controls, projection_minutes=[1, 4],
             inputs=fingerprints(AMP_RECORD, AMP_VERIFICATION, q3, q4, q6, DECLARATION, MDEA, low, ENDPOINTS / 'main/parameters.json')), start=start)


def mdea_supports(work):
    started = monotonic()
    q3 = ROUND3 / 'q3.json'
    reference = RESULTS / 'B/reactions.json.gz'
    low, = (BOUNDED.parent / 'shared-bicarbonate-417/mdea').glob('mdea-low-*/endpoint.json.gz')
    rows = []
    for i, (target, baseline) in enumerate(zip(stable.read(q3)['rows'][:2], stable.read(reference)['rows'][1:], strict=True)):
        assert all(target[k] == baseline[k] for k in ('key', 'T_K', 'P_Pa', 'feed_mol'))
        state = feed_state(target)
        for label, route_class in (('baseline', Route), ('100-kPa', FixedReference)):
            tick = monotonic()
            route = route_class(MDEA, work / str(i) / label)
            spec = route.bind(stable.read(low))
            row = dict(key=target['key'], reference_convention=label, T_K=target['T_K'],
                       P_Pa=target['P_Pa'], feed_mol=target['feed_mol'])
            rows.append(row)
            try:
                outcome = fixed(route, spec, state, target['P_Pa'], dict(pair=target['attempts'][0]),
                                mdea=True, assemblages=True)
                row.update(outcome)
                if 'candidates' not in outcome:
                    row['support_refusal'] = f"{outcome['instability']}. Parent solver: {outcome['status']}"
                    continue
                expected = baseline['conventions'][label]['attempts'][0]
                actual = next(iter(outcome['attempts']), {})
                delta = actual.get('Gibbs_decrease_over_RT_mol')
                reference_delta = expected.get('Gibbs_decrease_over_RT_mol')
                difference = delta - reference_delta if delta is not None and reference_delta is not None else None
                error = expected.get('numerical_error_over_RT_mol')
                row['archived_seed_replay'] = dict(confirmation_matches=actual.get('confirmed') == expected['confirmed'],
                                                  Gibbs_difference_RT_mol=difference, paired_error_RT_mol=error,
                                                  within_paired_error=abs(difference) <= error if difference is not None else None)
            except (ValueError, RuntimeError, AttributeError, TypeError) as error:
                row['support_refusal'] = f'{type(error).__name__}: {error}'
            finally:
                row['seconds'] = monotonic() - tick
    save('B/MDEA-supports.json.gz', dict(rows=rows, inputs=fingerprints(q3, reference, MDEA, low)), start=started)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--mdea-supports', action='store_true')
    args = parser.parse_args()
    with TemporaryDirectory() as directory:
        (mdea_supports if args.mdea_supports else calculate)(Path(directory))
