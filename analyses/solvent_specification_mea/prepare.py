"""Materialize the accepted endpoint declarations; never evaluate observations here."""
import ast
import copy
import csv
import hashlib
import json
import math
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / 'analyses/mea_parameter_bundle/scripts'))
import fit_observations as f
from fit_campaign import stage6_weights
from MEA.solvent_specification import SolventSpecification, jsonable

AN = Path(__file__).resolve().parent
E = ROOT / 'analyses/mea_parameter_bundle/results/engine-3e83e19c-paper-evidence'
C = ROOT / 'analyses/mea_parameter_bundle/results/engine-3e83e19c-refit-chain/restricted-2/attempt-3'
sources = {}
def read(path):
    sources[str(path.relative_to(ROOT))] = hashlib.sha256(path.read_bytes()).hexdigest()
    return json.loads(path.read_bytes())
def write(name, value):
    path = AN / 'inputs' / name
    path.write_text(json.dumps(value, indent=2) + '\n')
    return dict(path='inputs/' + name, sha256=hashlib.sha256(path.read_bytes()).hexdigest())
def toml(value):
    if isinstance(value, dict):
        return '{' + ', '.join(json.dumps(k) + ' = ' + toml(v) for k, v in value.items() if v is not None) + '}'
    if isinstance(value, (list, tuple)):
        return '[' + ', '.join(map(toml, value)) + ']'
    return json.dumps(value)
def fields(value):
    return {k: jsonable(getattr(value, k)) for k in dir(value) if not k.startswith('_') and not callable(getattr(value, k))}
def equal(a, b):
    if isinstance(a, (list, tuple)):
        for x,y in zip(a,b,strict=True): equal(x,y)
    elif a is None or isinstance(a, (str, int, float, bool, dict)) or (hasattr(a, 'name') and hasattr(a, 'value')):
        assert a == b, (a, b)
    else:
        for k in dir(a):
            if not k.startswith('_') and not callable(getattr(a, k)):
                equal(getattr(a, k), getattr(b, k))

def problem(p, chemistry):
    reactions = [dict(name=r.name, stoichiometry=dict(zip(ids, r.stoichiometry)), correlation=fields(r.correlation), reference=fields(r.reference)) for r in p.reactions]
    key = 'amended' if reactions and reactions[1]['correlation']['temperature_max'] == 436.85 else 'aqueous'
    if reactions:
        assert key not in chemistry or chemistry[key] == reactions
        chemistry[key] = reactions
    n = p.neutral_reference
    return dict(**(dict(reaction_set=key, neutral_reference='aqueous') if reactions else {}),
        T=dict(free=True, guess=p.temperature.value) if p.temperature.free else p.temperature.value, P=dict(free=True, guess=p.pressure.value) if p.pressure.free else p.pressure.value,
        feed=dict(basis='amounts', values=dict(zip(ids, p.feed.values))), phases=[dict(name=q.name, kind=q.kind.name.lower(), support=[ids[i] for i in q.support],
        amount=dict(status=q.amount.kind.name.lower(), **({'value':q.amount.fraction} if q.amount.kind.name == 'Pinned' else {})),
        composition_guess=list(q.composition_guess), packing_guess=q.packing_guess) for q in p.phases],
        topology_declared=p.topology_declared, row_tolerance=p.row_tolerance, standard_gibbs_j_per_mol=list(p.standard_gibbs_j_per_mol),
        solver_options={q['name']:q['value'] for q in p.solver_options if q['name'] != 'EQUILIBRIUM_ROW_RESIDUAL'})

spec = read(C / 'spec.json')
mapping = read(E / 'reported-parameters.json')
assert sources[str((E / 'reported-parameters.json').relative_to(ROOT))] == '00e77608a8489fc9e03a7d2a86c08cb5ff782bb441368a62fa6390b8bfe9cc91'
for path in (E.parent / 'selected-current-best-parameters.json', C / 'run/fit/usable-budget-endpoint.json'):
    assert path.read_bytes() == (E / 'reported-parameters.json').read_bytes()
    read(path)
for name, digest in {'full-replay.json':'aeb3331cf95cb174faa9cfa5891e887dbae0829448b5c67a2da17727ed386560', 'fitted-rows.csv':'e18efef61548d20e40578a2223cb203dd903ed288c02b94ab24009d6b861fb44', 'fit-summary.json':'7968c9ce1ca9947d70795787afedccf4f90786a77196e890412a13871f37d0fb', 'replay-identity.json':'96069e3402f3d3d6a26f12f155d9bde730ff838c43f706a85fd0412166fa3f27'}.items():
    assert hashlib.sha256((E / name).read_bytes()).hexdigest() == digest
    sources[str((E / name).relative_to(ROOT))] = digest
membership = {r['target']:r for r in csv.DictReader((E / 'fitted-rows.csv').open())}
reference = [r for r in read(E / 'full-replay.json') if r['target'] in membership]
assert len(reference) == len(membership) == 307
for path in [spec[k] for k in ('packet_path','anchors_path','heat_rows_path','stage2_rows_path','state_requests_path')] + [d['table'] for d in spec['observations']]:
    sources[path] = hashlib.sha256((ROOT / path).read_bytes()).hexdigest()
for record in spec['inputs']:
    assert hashlib.sha256((ROOT / record['path']).read_bytes()).hexdigest() == record['sha256']
    sources[record['path']] = record['sha256']
for path in [Path(f.__file__), Path(f.s.__file__), Path(f.thermal.__file__), Path(sys.modules['fit_campaign'].__file__),
             Path(sys.modules['verify_temperature_reference'].__file__), ROOT/'analyses/solvent_specification_mdea/declarations.toml', ROOT/'src/MEA/common/mea_source_contracts.py', ROOT/'data/reference/MEA/manifests/chemical_reaction_source_contract.json']:
    sources[str(path.relative_to(ROOT))] = hashlib.sha256(path.read_bytes()).hexdigest()
params, common = f.rows_for(spec, mapping, 'base')
rows = {i:(item,w) for i,item,w in common}
amended = copy.deepcopy(mapping)
for d in amended['domains']:
    if d['domain_id'] in spec['cases'][0]['neutral_domain_ids']:
        d.update(spec['cases'][0]['neutral_domain'])
construction = write('construction-parameters.json', amended)
domain_differences = [
    dict(domain_id=a['domain_id'], fields={k:dict(before=a.get(k), after=b.get(k)) for k in set(a)|set(b) if a.get(k)!=b.get(k)})
    for a,b in zip(mapping['domains'],amended['domains'],strict=True) if a!=b]
restored = copy.deepcopy(amended)
for original, changed in zip(mapping['domains'], restored['domains'], strict=True):
    if original['domain_id'] in spec['cases'][0]['neutral_domain_ids']:
        for key in spec['cases'][0]['neutral_domain']:
            if key in original:
                changed[key] = original[key]
            else:
                changed.pop(key)
assert restored == mapping
case = dict(spec['cases'][0], kiepe_continuation=False)
_, initial = f.stage2_rows(spec, mapping, case)
_, continued = f.stage2_rows(spec, mapping, spec['cases'][0])
declared = {r['id']:r for r,_,_ in initial}
for r, item, _ in initial:
    rows[r['id']] = (item, r['weight'])
request = f.s.corrected_request(f.s.load_state_packet(ROOT/spec['packet_path'])['observations'][0]['request'],f.s.reaction_values(mapping),mapping=mapping)
base = f.s._problem_from_request(request)
for r, weight in zip(spec['direct_rows'], stage6_weights(spec, spec['direct_rows'], 1.0), strict=True):
    p = f.eq.Problem(T=r['T_K'], P=r['P_Pa'], feed=f.eq.Amounts(r['analytical_feed']), phases=[f.eq.Phase('L',kind='liquid',support=f.s.COMPONENT_IDS)], reactions=base.reactions, neutral_reference=base.neutral_reference,row_tolerance=spec['verification']['raw_residual'])
    rows[r['id']] = (f.reg.observation(params,r['quantity'],p,observed=r['observed'],form='difference',scale=r['scale'],**(dict(phase='L',mass_basis=True) if r['quantity']=='phase_density' else {})),weight)
assert set(rows) == set(membership)
ids = params.component_ids
chemistry, templates, datasets = {}, {}, []
domains = {g:[min(v),max(v)] for g in {r['group'] for r in membership.values()} if (v:=[rows[i][0].problem.temperature.value for i,r in membership.items() if r['group']==g])}
for order, ref in enumerate(reference):
    identity = ref['target']; item, weight = rows[identity]
    assert (item.observed,item.scale,item.form.name,weight) == (ref['observed'],ref['scale'],ref['form'],ref['weight'])
    declaration = declared.get(identity, {})
    row = dict(identity=identity, source=json.dumps(ast.literal_eval(membership[identity]['declaration'])), observation_order=order)
    args = dict(observed=item.observed, **({'scale':item.scale} if item.form.name=='Difference' else {}), form={'Difference':'difference','LogRatio':'log_ratio'}[item.form.name])
    heat = item.kind.name == 'AdditionEnthalpy'
    names = ('initial','final') if heat else ('problem',)
    d = dict(name=identity,group=membership[identity]['group'],role='calibration',constructor='addition_enthalpy' if heat else 'observation',kind=next(k for k,v in f.reg._KINDS.items() if v==item.kind) if not heat else 'pressure',arguments=args,weight=weight,filter={},temperature_domain=domains[membership[identity]['group']])
    if identity in declared:
        d['observation_parameters'] = construction
        d['state_identity'] = declaration['state_id']
    if d['group'] == 'Cai':
        d['temperature_domain'] = [293.15, 436.85]
    if d['group'] == 'Kiepe':
        d['continuation'] = dict(group=str(declaration['T_K']), order=order)
    for name, native in zip(names, (item.problem,item.final_problem), strict=False):
        template = problem(native, chemistry)
        def bind(value):
            if isinstance(value, float):
                key = f'v{len(row)}'; row[key] = value; return '$' + key
            if isinstance(value, dict):
                return {k:bind(v) for k,v in value.items()}
            return [bind(v) for v in value] if isinstance(value,list) else value
        templates[f'{order}-{name}'] = bind(template)
        d['template' if name=='problem' else name] = f'{order}-{name}'
    if heat:
        args.update(feed=dict(zip(ids,item.composition)),amount=item.feed_amount,T=item.temperature,P=item.pressure,phase=item.branch.name.lower())
    else:
        args.update(phase=item.problem.phases[item.phase].name,species=[ids[i] for i in item.species],mass_basis=item.mass_basis)
        if item.kind.name == 'PhaseAmountRatio':
            args.update(denominator_phase=item.problem.phases[item.denominator_phase].name,denominator_species=[ids[i] for i in item.denominator_species])
    path = AN / f'inputs/{order}.csv'
    with path.open('w') as stream:
        writer = csv.DictWriter(stream,fieldnames=list(row)); writer.writeheader(); writer.writerow(row)
    d.update(path=str(path.relative_to(AN)),sha256=hashlib.sha256(path.read_bytes()).hexdigest(),columns={k:k for k in row if k not in ('identity','source')})
    datasets.append(d)
n = item.problem.neutral_reference
neutral = dict(solvent=ids[n.solvent_index],solute_molality_ratios={cid:v for cid,v in zip(ids,n.solute_molality_ratios) if v},standard_molality_mol_per_kg=n.standard_molality_mol_per_kg,species_reference={})
thermal = read(f.thermal.PHYSICAL_CALORICS)
s = thermal['components']['monoethanolamine']; cp = s['coefficients']; centre = s['enthalpy_entropy_anchor_k']
s['coefficients'] = [sum(a*math.comb(j,k)*centre**(j-k) for j,a in enumerate(cp) if j>=k) for k in range(4)]
s.update(enthalpy_anchor_j_per_mol=0.,entropy_anchor_j_per_mol_k=0.)
import tomllib
shared = dict(templates=templates, chemistry=dict(reactions=chemistry,neutral_references=dict(aqueous=neutral)),datasets=datasets)
mdea = tomllib.loads((AN.parent/'solvent_specification_mdea/declarations.toml').read_text())
shared['element_formulas'] = {cid:mdea['element_formulas'][cid] for cid in ids if cid in mdea['element_formulas']}
shared['element_formulas'].update({'monoethanolamine':dict(C=2,H=7,N=1,O=1,charge=0),'protonated-monoethanolamine':dict(C=2,H=8,N=1,O=1,charge=1),'carbamate-anion':dict(C=3,H=6,N=1,O=3,charge=-1)})
shared['analytical_components'] = {cid:({'monoethanolamine':1,'carbon-dioxide':1} if cid=='carbamate-anion' else {'monoethanolamine':1} if 'monoethanolamine' in cid else mdea['analytical_components'][cid]) for cid in ids}
(AN/'declarations.toml').write_text('\n'.join(k+' = '+toml(v) for k,v in shared.items())+'\n')
config = dict(schema='solvent-specification-1',declarations=dict(path='declarations.toml',sha256=hashlib.sha256((AN/'declarations.toml').read_bytes()).hexdigest()),endpoint=write('endpoint.json',mapping),coordinates=write('endpoint-only-coordinates.json',[]),phase_states=write('endpoint-only-phase-states.json',[]),caloric=write('caloric.json',thermal))
config['start'] = config['endpoint']
(AN/'MEA.toml').write_text('\n'.join(k+' = '+toml(v) for k,v in config.items())+'\n')
loaded = SolventSpecification(AN/'MEA.toml')
loaded.species_mapping(loaded.spec['chemistry']['reactions'])
for record, dataset in zip(loaded.inputs['observations']['fitted'], datasets, strict=True):
    if record['group'] == 'Kiepe':
        source = {k:float(v) for k,v in next(csv.DictReader((AN/dataset['path']).open())).items() if k not in ('identity','source')}
        equal(rows[record['identity']][0].problem, loaded.problem(dataset['template'], source)._native(loaded.model))
    expected = next((item for r,item,_ in continued if r['id']==record['identity']), rows[record['identity']][0])
    equal(expected,loaded.observation(record))
pairs = {}
for record in loaded.inputs['observations']['fitted']:
    if record['group'] == 'Cai':
        identity = record['state_identity']
        inputs = (loaded.problems[record['problem']], record['observation_parameters'])
        if identity in pairs:
            equal(inputs, pairs[identity])
        pairs[identity] = inputs
assert len(pairs) == 25
write('reference.json',reference)
write('preparation-provenance.json',dict(sources=sources,selected_ids=list(membership),declarations_equal=307,continuation_equal=len(loaded.continuation),paired_states_equal=len(pairs),construction_source=construction,construction_domain_changes=spec['cases'][0]['neutral_domain'],construction_differences=domain_differences,construction='Stage-2 construction and continuation use amended parameters; prediction uses unamended endpoint',endpoint_only='Empty coordinates and phase states; start equals endpoint; no fit or phase search'))

# Issue 235 fit declaration: 14 reactive C/spec.json coordinates at the design table's perturbed origins.
# The table fixes each d (one tenth of a scale, inward at active bounds); it is copied, not recomputed.
endpoint_values = {}
def collect(value):
    if isinstance(value, dict):
        if isinstance(value.get('value'), dict) and 'magnitude' in value['value'] and 'identity' in value:
            endpoint_values[value['identity']] = value['value']['magnitude']
        for v in value.values(): collect(v)
    elif isinstance(value, list):
        for v in value: collect(v)
collect(mapping)
perturbation = {0:-.1, 1:.1, 2:.1, 3:.1, 4:.1, 5:.1, 6:-.1, 7:-.1, 8:-.1, 9:.1, 10:-.1, 11:-.1, 14:-.1, 15:.1}
fit_coordinates = []
for index, d in perturbation.items():
    q = spec['information_coordinates'][index]; scale, bounds = q['scale'], q['bounds']
    if 'coefficient' in q:  # R5 source coefficient -> native natural-log b, factor applied once
        base = next(r for r in chemistry['aqueous'] if r['name'] == q['reaction'])['correlation'][q['coefficient']]
        scale, bounds = scale * abs(q['source_to_native_factor']), sorted(q['source_to_native_factor'] * v for v in bounds)
        kind = dict(kind='reaction_coordinate', name=q['reaction'], coefficient=q['coefficient'])
    elif q.get('enthalpy_shift'):  # incremental to the inherited shifts; R2 bounds translated to total [-10000, 10000] J/mol
        base, bounds = 0.0, [-8636.068425883279, 11363.931574116721] if q['reaction'] == 'R2' else bounds
        kind = dict(kind='reaction_enthalpy_shift', name=q['reaction'], pivot_temperature=313.15)
    else:
        base = endpoint_values[q['identity']]
        kind = dict(targets=[[t['family'], t['target'], t['factor']] for t in q.get('targets', [dict(q, factor=1.0)])])
    fit_coordinates.append(dict(kind, original_index=index, identity=q['identity'], base=base, scale=scale, bounds=bounds, d=d, origin=base + scale * d))
probe = json.loads((AN / 'results/design-replay-e6dae5c7/coordinate-checks.json').read_text())['coordinates']
assert [{k: z[k] for k in probe[0]} for z in fit_coordinates] == probe
optimizer = dict(maximum_iterations=60, function_tolerance=1e-8, parameter_tolerance=1e-10, gradient_tolerance=1e-8, maximum_elapsed_time_seconds=1200.0)
fit = dict(config, coordinates=write('fit-coordinates.json', fit_coordinates), optimizer=optimizer)
(AN / 'MEA-fit.toml').write_text('\n'.join(k + ' = ' + toml(v) for k, v in fit.items()) + '\n')
