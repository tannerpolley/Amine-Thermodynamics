"""Issue 213: conditional five-coordinate reference and unrounded acceptance limits."""
import csv
import hashlib
import math
from pathlib import Path
import sys
ROOT = Path(__file__).resolve().parents[3]
sys.path[:0] = [str(ROOT/'src'), str(Path(__file__).parent), str(ROOT/'analyses/mea_parameter_bundle/calibration-misfit')]
import fit_campaign as c
import fit_observations as o
import heat_evidence_170 as h
OUT = ROOT/'analyses/mea_parameter_bundle/results/engine-3e83e19c-density-free'
CHAIN = OUT.with_name('engine-3e83e19c-refit-chain')
SOURCE = CHAIN/'restricted-2/attempt-3/spec.json'
CANDIDATE = CHAIN/'restricted-2/attempt-3/run/fit/usable-budget-endpoint.json'
sha = lambda p: hashlib.sha256(Path(p).read_bytes()).hexdigest()
relative = lambda p: str(p.relative_to(ROOT))
if sys.argv[1] == 'prepare':
    OUT.mkdir(exist_ok=False)
    original, prior = c.load(SOURCE), c.load(ROOT/'analyses/mea_parameter_bundle/data/input/fit-campaigns/heat-170.json')
    assert sha(CANDIDATE) == '00e77608a8489fc9e03a7d2a86c08cb5ff782bb441368a62fa6390b8bfe9cc91'
    start = OUT/'start.json'
    start.write_bytes(CANDIDATE.read_bytes())
    mapping = c.load(start)
    spec = {k: prior[k] for k in ('packet_path', 'anchors_path', 'heat_rows_path', 'thermal_path', 'worker_memory')}
    spec.update(campaign_id='density-free-213', engine=original['engine'], observations=original['observations'], controls=dict(original['controls'], maximum_elapsed_time_seconds=600.0))
    spec['coordinates'] = [dict(x, bounds=y['bounds'], origin={'candidate': o.s.parameter_values(mapping)[x['identity']]}) for x,y in zip(prior['coordinates'][:5], original['information_coordinates'][:5], strict=True)]
    variant = dict(problem='density-free', born=next(f['choice'] for f in mapping['model_families'] if f['kind']=='electrolyte'), permittivity=next(f for f in mapping['model_families'] if f['kind']=='permittivity'), chemistry=o.s.reaction_values(mapping))
    spec['cases'] = [dict(id='reference', variant=variant, coordinates=list(range(5)), observations='base', starts=[dict(id='candidate', parameters_path=relative(start), sha256=sha(start))])]
    paths = [ROOT/spec[k] for k in ('packet_path','anchors_path','heat_rows_path','thermal_path')]+[ROOT/spec['observations'][0]['table'], SOURCE, CANDIDATE, start, ROOT/'analyses/mea_parameter_bundle/data/input/fit-campaigns/heat-170.json']
    spec['inputs'] = [dict(path=relative(p), sha256=sha(p)) for p in paths]
    c.write(OUT/'spec.json', spec)
elif sys.argv[1] == 'fit':
    c.run(OUT/'spec.json', OUT/'run', case_ids=['reference'], operation='fit')
elif sys.argv[1] == 'analyze':
    spec = c.load(OUT/'spec.json')
    c.verify(spec)
    native = c.load(OUT/'run/reference/candidate/native-fit.json')
    assert native['selection_eligible'] and native['status']=='converged' and native['usable']
    endpoint = c.load(OUT/'run/reference/candidate/parameters.json')
    assert o.s.with_parameter_values(endpoint, native['start']) == dict(c.load(OUT/'start.json'), purpose=endpoint['purpose'])
    params, rows = o.rows_for(spec, endpoint, 'base')
    base = o.replay(endpoint, rows)
    heats = o.load(spec['heat_rows_path'])
    arcis = [r for r in heats if not r['record_id'].startswith('vinjarapu')]
    assert len(arcis)==14
    items = o.heat_items(endpoint, params, arcis, h.request(endpoint, 313.15, .11))
    arcis_values = o.replay(endpoint, [(r['record_id'], item, 1.) for r,item in zip(arcis,items,strict=True)])
    c.write(OUT/'reference-base-replay.json', base)
    c.write(OUT/'reference-arcis-replay.json', arcis_values)
    reference = o.replay_summary(base+arcis_values, heats)
    assert (len(base), reference['scores']['pressure']['n'], reference['scores']['species']['n'], sum(r['target'].startswith('vinjarapu') for r in base), len(arcis_values)) == (149,47,94,8,14)
    assert all(r['status']=='Available' and r['requested_tolerance_met'] and all(math.isfinite(r[k]) for k in ('predicted','residual','weighted_residual')) for r in base+arcis_values)
    c.write(OUT/'reference-quantities.json', reference)
    displayed = c.load(CHAIN/'displays/summary.json')
    indexed = o.indexed(c.load(CHAIN/'displays/reported/full-replay.json'), 'target')
    candidate_base = [indexed[i] for i in spec['observations'][0]['ordered_row_ids']]
    errors = {p: iter(e) for p,e in displayed['arcis']['reported']['errors_kJ_mol'].items()}
    candidate_arcis = [dict(target=r['record_id'], observed=r['observed_addition_enthalpy_J_per_mol_CO2'], predicted=r['observed_addition_enthalpy_J_per_mol_CO2']+1000*next(errors[str(r['system_pressure_Pa'])]), status='Available') for r in arcis]
    candidate = o.replay_summary(candidate_base+candidate_arcis, heats)
    assert math.isclose(candidate['Arcis_RMSE_kJ_mol'], displayed['arcis']['reported']['RMSE_kJ_mol'], rel_tol=0., abs_tol=1e-12)
    candidate['Arcis_RMSE_kJ_mol'] = displayed['arcis']['reported']['RMSE_kJ_mol']
    assert all((r['observed'],r['scale'],r['weight'],r['form'])==(item.observed,item.scale,w,item.form.name) for r,(_,item,w) in zip(candidate_base,rows,strict=True))
    c.write(OUT/'candidate-quantities.json', candidate)
    constant = c.load(CHAIN/'displays/cai-constant-replay.json')
    assert len(constant)==50 and all(r['status']=='Available' for r in constant)
    definitions = [
        ('common149_cost', reference['common149_cost'], 1.10, 0., candidate['common149_cost'], '1.10 * density-free common149 cost'),
        ('pressure_AARD_percent', reference['scores']['pressure']['AARD_percent'], 1., 2., candidate['scores']['pressure']['AARD_percent'], 'density-free pressure AARD + 2 percentage points'),
        ('species_AARD_percent', reference['scores']['species']['AARD_percent'], 1., 2., candidate['scores']['species']['AARD_percent'], 'density-free species AARD + 2 percentage points'),
        ('Vinjarapu_RMSE_kJ_mol', reference['Vinjarapu_RMSE_kJ_mol'], 1., 1., candidate['Vinjarapu_RMSE_kJ_mol'], 'density-free Vinjarapu RMSE + 1 kJ/mol CO2'),
        ('Arcis_RMSE_kJ_mol', reference['Arcis_RMSE_kJ_mol'], 1., 1., candidate['Arcis_RMSE_kJ_mol'], 'density-free Arcis RMSE + 1 kJ/mol CO2'),
        ('cai_cost', math.fsum(r['cost'] for r in constant), 1.05, 0., c.load(CHAIN/'displays/reported/score.json')['cai_cost'], '1.05 * refitted constant-interaction Cai cost')]
    limits = {k: dict(reference_value=v, multiplier=m, increment=a, definition=d, limit=m*v+a, candidate_value=x, margin=m*v+a-x, passes=x<=m*v+a) for k,v,m,a,x,d in definitions}
    c.write(OUT/'limits.json', dict(decision='passes' if all(v['passes'] for v in limits.values()) else 'return to owner', limits=limits, inputs=[dict(path=relative(p), sha256=sha(p)) for p in (OUT/'spec.json', OUT/'reference-quantities.json', OUT/'candidate-quantities.json', CANDIDATE, CHAIN/'displays/reported/full-replay.json', CHAIN/'displays/reported/score.json', CHAIN/'displays/summary.json', CHAIN/'displays/cai-constant-replay.json')]))
    with (OUT/'parameters.csv').open('w', newline='') as stream:
        writer = csv.writer(stream, lineterminator='\n')
        writer.writerow(['coordinate','value','unit'])
        writer.writerows((i,v,'K' if i.endswith('slope') else 'dimensionless') for i,v in zip(native['coordinates'],native['physical'],strict=True))
    c.write(OUT/'summary.json', dict(status=native['status'], usable=native['usable'], iterations=native['iterations'], initial_cost=native['initial_cost'], final_cost=native['final_cost'], replay_cost_difference=reference['cost']-native['final_cost'], decision=c.load(OUT/'limits.json')['decision']))
