"""Read back the DEA split certificate and the AMP/MDEA phase controls."""
import math
import sys
from time import monotonic

from shared_interactions import OUT, RESULTS, a, fingerprint, r, save
from amp_transfer import classify_descents as cd
from mdea_reference import predicates
from part_ii import eq, np
from phase_replays import control_states, point_for
from phases import certificate, dilute_vapor_connection, fixed, physical
from round_8.reductions import phase_outcome, witness_direction


def dea():
    run, point = point_for('DEA', 'selected', 'round-9-certificate')
    spec = run.bind(point)
    species = list(spec.parameters.component_ids)
    components = {q['component_id']: q['fixed'] for q in point['parameters']['components']}
    mass = np.array([components[k]['molar_mass']['value']['magnitude'] for k in species])
    charge = np.array([components[k]['charge_number']['value']['magnitude'] for k in species])
    screens = [r.read(OUT / 'DEA/screen' / group / 'declared/summary.json.gz')
               for group in ('selected', 'selected-registry-growth')]
    assert all(s['endpoint_fingerprint'] == fingerprint(point) for s in screens)
    repeat = {q['key']: q['attempts'] for q in screens[1]['classifications']}
    rows = []
    for entry in screens[0]['classifications']:
        original = next((q for q in entry['attempts'] if q['confirmed']), None)
        if original is None:
            continue
        key, T, P = (entry[k] for k in ('key', 'temperature_K', 'pressure_Pa'))
        problem = run.stability_row(spec, dict(problem=key), 1.).problem
        problem.pressure = type(problem.pressure).fixed(P)
        model = spec.model
        parent = eq.solve_equilibrium(model, problem)
        compiled = eq.compile_problem(model, problem)
        assert parent.requested_tolerance_met and list(problem.feed.values) == entry['feed_mol']
        parent_g = cd.gibbs(compiled, parent)

        # Chemical rows contain -B transpose in the conserved multiplier columns.
        J = np.array(compiled.jacobian(parent.coordinates)).reshape(len(parent.rows), -1)
        indices = [i for i, row in enumerate(parent.rows) if row.kind.name == 'Chemical']
        columns = slice(compiled.primal_size, compiled.primal_size + compiled.rank)
        B = -J[indices, columns].T
        assert [parent.rows[i].index for i in indices] == list(range(len(species)))
        nu = np.array([q.stoichiometry for q in problem.reactions]).T
        assert np.linalg.matrix_rank(B) == compiled.rank and np.allclose(B @ nu, 0, atol=1e-13)

        def inspect(chart, solved):
            if not solved.requested_tolerance_met or len(solved.amounts) != 2 or min(solved.amounts) <= 0:
                return dict(refusal=solved.message)
            details = physical(spec, problem, solved)
            details['certificate'] = certificate(spec, problem, chart, solved)
            return details

        def solve(seed):
            return cd.coexistence(spec, problem, parent_g, list(zip(seed['phases'], seed['packings'], strict=True)),
                                  inspect=inspect)

        daughter_restart = solve(original)
        split = daughter_restart.copy()
        if not split['confirmed'] and (neighbor := original.get('seed_from')):
            prior = next(q for q in screens[0]['classifications'] if q['key'] == neighbor)
            split = solve(next(q for q in prior['attempts'] if q['confirmed']))
        details = split.pop('diagnostics')
        assert split['confirmed'] and details['physical_checks_pass'], (key, split, details)
        cert = details.pop('certificate')
        assert cert['reaction_pass'] and cert['transfer_pass'] and cert['primitive_pass']
        limit = split['numerical_error_over_RT_mol'] + original['numerical_error_over_RT_mol']
        assert abs(split['Gibbs_decrease_over_RT_mol'] - original['Gibbs_decrease_over_RT_mol']) <= limit
        phases = details['phases']
        total = math.fsum(split['amounts_mol'])
        total_mass = math.fsum(p['amount_mol'] * (mass @ p['x']) for p in phases)
        for phase in phases:
            x, rho, n = phase['x'], phase['density_mol_m3'], phase['amount_mol']
            dp_drho = model.state(T, rho=rho, x=x, derived_properties=True).pressure_density_derivative
            assert dp_drho > 0
            phase.update(dP_drho_Pa_m3_mol=dp_drho, molar_volume_m3_mol=1/rho, density_kg_m3=float(rho*(mass @ x)),
                         true_mole_fraction=n/total, mass_fraction=float(n*(mass @ x)/total_mass),
                         charge_residual_mol=float(n*(charge @ x)))
        rows.append(dict(key=key, T_K=T, P_Pa=P, pressure_basis='assigned density-cell pressure',
                         feed_mol=entry['feed_mol'], component_mass_sum_residual_kg=total_mass-float(mass @ entry['feed_mol']),
                         loading=entry['feed_mol'][0]/entry['feed_mol'][1],
                         unloaded_wt_percent=100*mass[1]/(mass[1]+mass[2]*entry['feed_mol'][2]),
                         row_tolerance=problem.row_tolerance, species=species,
                         conservation_matrix=B.tolist(), multiplier_labels=compiled.coordinate_labels()[columns],
                         tangent_plane_gibbs_basis='modified Gibbs energy G* at fixed 100 kPa reaction reference',
                         parent_G_over_RT_mol=parent_g[0], split=split, **details,
                         reaction_contractions=cert['reaction_contractions'],
                         interphase_residuals=cert['electrochemical_difference_L2_minus_L1'],
                         interphase_limit=cert['transfer_limit'],
                         daughter_restart=dict(confirmed=daughter_restart['confirmed'], message=daughter_restart['message']),
                         declared_search_attempts=entry['attempts'], registry_growth_attempts=repeat[key]))
    assert len(rows) == 4 and all(any(a['confirmed'] for a in q['registry_growth_attempts']) for q in rows)
    return dict(endpoint_fingerprint=fingerprint(point), rows=sorted(rows, key=lambda q: q['key']),
                liquid_root_rule=dict(log_density_distance_max=cd.DENSITY_WINDOW,
                                      coincidence_distance=cd.COINCIDENCE))


def amp():
    run, point = point_for('AMP_free', 'selected', 'round-9-amp-controls')
    spec = run.bind(point)
    label = r.read(OUT / 'AMP_free/selection.json')['selected']
    revised = r.read(OUT / f'AMP_free/controls/{label}.json.gz')
    bubbles = r.read(OUT / 'AMP_free/properties.json.gz')
    assert revised['endpoint_fingerprint'] == bubbles['endpoint_fingerprint'] == fingerprint(point)
    legacy = r.read(r.ROOT / 'analyses/round_3/results/q1.json')['rows']
    common = r.read(r.ROOT / 'analyses/round_5/results/A/common-pressure.json.gz')
    old = {q['key']: q['free'] for q in legacy if q['pressure_basis'] == 'measured pressure'}
    old['worked-state'] = common['outcomes']['original-main']
    calculated = {q['identity'] + ':problem': q for q in bubbles['rows']}
    rows = []
    for key, record in revised['rows'].items():
        value, before = record['value'], old[key]
        assert all(value[field] == before[field] for field in ('T_K', 'P_Pa', 'feed_mol'))
        source = calculated.get(key)
        bubble = source['value'] if source else r.read(OUT/'display-replays/AMP_free-bubble.json.gz')['pressure_Pa']
        outcomes = dict(early=phase_outcome(before), reported=phase_outcome(value))
        witness = None
        if outcomes['reported'] == 'unresolved phase identity':
            assert record['P_Pa'] < bubble
            trial = value['minimum_trial']
            roots = value['minimum_trial_roots']
            witness = dict(evidence=dict(witness=trial, roots=roots))
            root = min(cd.matched(roots, 1e-10), key=lambda q: q['log_density_distance'], default={})
            if root.get('returned') == 'unspecified':
                rho = 1/trial['quantities']['volume_m3_per_mol']
                trace, connected = dilute_vapor_connection(spec.model, value['T_K'], trial['composition'], rho)
                witness['dilute_trace'] = dict(trace=trace, connected=connected)
            witness['direction'] = witness_direction(witness)
            for candidate in value['candidates']:
                if candidate['support'] != 'L+V' or candidate['root_checks_pass']:
                    continue
                vapor = candidate['phases'][1]
                trace, connected = dilute_vapor_connection(
                    spec.model, value['T_K'], vapor['x'], vapor['density_mol_m3'])
                candidate['dilute_trace'] = dict(trace=trace, connected=connected)
        rows.append(dict(key=key, T_K=value['T_K'], P_Pa=record['P_Pa'], reported_bubble_Pa=bubble,
                         source=source['row'] if source else old[key]['declaration'],
                         early_bubble_Pa=common['bubbles']['original-main']['pressure_Pa'] if source is None else None,
                         feed_mol=value['feed_mol'], outcomes=outcomes, witness=witness,
                         early_attempts=before['attempts'], reported_attempts=value['attempts'],
                         reported_candidates=value.get('candidates', [])))
    assert rows[-1]['key'] == 'worked-state' and rows[-1]['outcomes']['early'] == 'confirmed split'
    assert len(rows) == 7 and sum(q['witness'] is not None for q in rows) == 4
    return dict(endpoint_fingerprint=fingerprint(point), rows=rows)


def mdea(fit):
    run, baseline = point_for('MDEA', 'selected', 'round-9-mdea-controls')
    spec = run.bind(fit['endpoint'])
    spec_baseline = run.bind(baseline)
    state_path = OUT / 'MDEA/screen/selected/declared/summary.json.gz'
    screen = r.read(state_path)
    # Use a descent state with a measured pressure, rather than an assigned
    # pressure on a heat/speciation observation.
    comparison = r.read(OUT / 'MDEA/properties.json.gz')['rows']
    sources = {q['identity'] + ':final': q for q in comparison if q['row'].get('source_key') == 'Zheng2020'}
    measured = next(q for q in screen['classifications'] if q['key'] in sources)
    key = measured['key']
    assert math.isclose(float(sources[key]['row']['pressure_MPa']) * 1e6, measured['pressure_Pa'])
    results = {}
    cases = list(control_states('MDEA', spec))
    measured_seed = next(a for a in measured['attempts'] if a.get('phases'))
    cases.append((key, dict(problem=key), measured['pressure_Pa'], dict(pair=measured_seed), False))
    for label, state, P, seed, assemblages in cases:
        results[label] = dict(P_Pa=P, basis='measured total pressure' if label == key else 'retained high-pressure control',
                              source=sources[key]['row'] if label == key else state, models={})
        for model, bound in (('salt-anchored', spec_baseline), ('MEA-fitted', spec)):
            try:
                result = fixed(run, bound, state, P, seed, mdea=True, assemblages=assemblages)
                results[label]['models'][model] = predicates(result, tolerance=1e-10)
            except (RuntimeError, ValueError, AssertionError) as exc:
                results[label]['models'][model] = dict(refusal=str(exc))
    return results


if __name__ == '__main__':
    a.study.reuse.bind_wheel()
    r.verify()
    for name in sys.argv[1:]:
        tick = monotonic()
        args = [r.read(RESULTS / 'MDEA-shared-fit.json.gz')] if name == 'mdea' else []
        value = globals()[name](*args)
        save(RESULTS / f'{name}-phase-controls.json.gz', dict(value=value, wheel=r.SHA, wall_s=monotonic()-tick))
        print(name, monotonic()-tick, flush=True)
