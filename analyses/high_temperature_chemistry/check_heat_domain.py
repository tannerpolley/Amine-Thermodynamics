"""Check the #245 fixed-pressure heat domain at every retained dose endpoint."""
import json
from run import AN, ROOT, OUT, SHA, SolventSpecification, fo, eq, assign, write

spec = SolventSpecification(ROOT / 'analyses/solvent_specification_mea/MEA-pre-260-340.toml')
reference = next(iter(spec.problems.values()))
request = json.loads((OUT / 'comparison-inputs.json').read_text())['species'][0]['request']
checks = []
for case in ('baseline', 'hamborg', 'all-five', 'holdout'):
    data = json.loads((OUT / f'{case}-assessment.json').read_text())
    cache = {}
    for r in data['heat']:
        if r['status'] != 'Available':
            continue
        item = fo.heat_items(spec.inputs['endpoint'], spec.parameters, [dict(temperature_K=r['T_K'], system_pressure_Pa=r['P_Pa'],
            alpha_final=r['loading'], observed_addition_enthalpy_J_per_mol_CO2=0., uH_J_per_mol_CO2=1000.)], request)[0]
        for loading in (r['previous_loading'], r['loading']):
            key = (r['T_K'], loading)
            if key not in cache:
                feed = dict(zip(spec.parameters.component_ids, item.final_problem.feed.values))
                feed['carbon-dioxide'] = loading
                vapor = ('carbon-dioxide', 'monoethanolamine', 'water') if loading else ('monoethanolamine', 'water')
                problem = eq.Problem(T=r['T_K'], P=eq.Free(10000.), feed=eq.Amounts(feed),
                    phases=[eq.Phase('L', kind='liquid', support=spec.parameters.component_ids), eq.Phase('V', kind='vapor', support=vapor, amount=eq.Pinned(0.))],
                    reactions=reference.reactions, neutral_reference=reference.neutral_reference, row_tolerance=1e-10)
                assign([problem], data['laws'])
                result = eq.solve_equilibrium(spec.model, problem)
                cache[key] = dict(case=case, T_K=r['T_K'], loading=loading, bubble_pressure_Pa=result.pressure,
                    requested_tolerance_met=result.requested_tolerance_met, success=result.success, message=result.message,
                    admitted=result.success and result.requested_tolerance_met and result.pressure <= r['P_Pa'])
                print(cache[key], flush=True)
    checks.extend(cache.values())
write('heat-domain.json', dict(checks=checks, admitted=all(r['admitted'] for r in checks)))
assert all(r['admitted'] for r in checks)
