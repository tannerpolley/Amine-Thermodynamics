"""#304 frozen working-fit prediction, using existing solvent prediction/phase producers."""
import copy
import csv
import hashlib
import json
import os
from concurrent.futures import ProcessPoolExecutor
from pathlib import Path
import tomllib
import epcsaft
from epcsaft import regression as reg
import zipfile
SHA256 = "0962e21d2fa7a8ba1ed4622f1110b3e8053bacd878fa41c999d85e8b9afab66b"
WHEEL = Path("/home/tnnrpolley21/Workspaces/Engineering/Amine-Thermodynamics/build/engine-wheels/main-391dfe5d64ede5036bf160bc6ae037ad5e14af32/epcsaft-1.3.0-cp313-cp313-manylinux_2_39_x86_64.whl")
assert hashlib.sha256(WHEEL.read_bytes()).hexdigest() == SHA256
with zipfile.ZipFile(WHEEL) as archive:
    assert all(archive.read(n) == (Path(epcsaft.__file__).parents[1] / n).read_bytes() for n in archive.namelist()
               if n.startswith(("epcsaft/", "epcsaft.libs/")) and not n.endswith("/"))
from MEA.solvent_specification import SolventSpecification, jsonable

AN = Path(__file__).resolve().parent
OUT = AN / 'results/kundu'
SHARED = {'water', 'carbon-dioxide', 'bicarbonate-anion', 'carbonate-anion', 'hydronium-cation', 'hydroxide-anion'}
CO2 = 'carbon-dioxide'

def toml_value(value):
    if isinstance(value, dict):
        return '{' + ', '.join(json.dumps(k) + ' = ' + toml_value(v) for k,v in value.items() if v is not None) + '}'
    if isinstance(value, list):
        return '[' + ', '.join(map(toml_value, value)) + ']'
    return json.dumps(value)

def save(path, value):
    path.write_text(json.dumps(jsonable(value), indent=2) + '\n')

def bind(path):
    return dict(path=os.path.relpath(path, AN), sha256=hashlib.sha256(path.read_bytes()).hexdigest())

def initialize(path):
    global spec
    spec = SolventSpecification(path)

def evaluate(record):
    prediction = spec.prediction(record)
    phase = spec.phase(dict(identity=record['identity'], problem=record['problem'], endpoint_sha256=spec.parameter_sha256), spec.spec['phase_policy'])
    envelope = []
    for factor in (.98, 1.02):
        base = spec.problems[record['problem']]
        problem = copy.copy(base)
        problem.feed = copy.copy(base.feed)
        problem.feed.values = dict(base.feed.values)
        problem.feed.values[CO2] *= factor
        assert problem.feed.values[CO2] == factor * base.feed.values[CO2]
        p = reg.predict(spec.model, reg.observation(spec.parameters, 'partial_pressure', problem,
            observed=record['arguments']['observed'], form='log_ratio', phase='V', species=[CO2]))
        envelope.append(dict(factor=factor, status=p.status.name, value=p.value, message=p.message, requested_tolerance_met=p.requested_tolerance_met))
    return dict(prediction=prediction, phase=phase, envelope=envelope)

def statistics(rows):
    errors = [100 * (r['predicted_Pa'] / r['observed_Pa'] - 1) for r in rows]
    return dict(rows=len(rows), E_p=sum(map(abs, errors))/len(errors), bias_percent=sum(errors)/len(errors))

def current_shared(document, decl):
    """Substitute the adopted #255/#297 shared species, pairs and R1-R3 laws (in place)."""
    mea = json.loads((AN.parent / 'solvent_specification_mea/inputs/endpoint.json').read_text())
    current = tomllib.loads((AN.parent / 'solvent_specification_mea/declarations.toml').read_text())
    document['components'] = [next(x for x in mea['components'] if x['component_id']==c['component_id']) if c['component_id'] in SHARED else c for c in document['components']]
    document['pairs'] = [next(x for x in mea['pairs'] if {x['component_id_a'],x['component_id_b']}=={p['component_id_a'],p['component_id_b']}) if {p['component_id_a'],p['component_id_b']}<=SHARED else p for p in document['pairs']]
    for r in decl['chemistry']['reactions']['aqueous']:
        if r['name'] in ('R1','R2','R3'):
            r['correlation'] = next(x['correlation'] for x in current['chemistry']['reactions']['aqueous'] if x['name']==r['name'])

def score(path, out, version, workers, group='kundu'):
    """Predict one comparison group with alpha +/- 2 % and phase trials; write states and per-row CSV."""
    initialize(path)
    records = [r for r in spec.inputs['observations']['comparisons'] if r['group']==group]
    with ProcessPoolExecutor(max_workers=workers, initializer=initialize, initargs=(path,)) as pool:
        results = list(pool.map(evaluate, records))
    save(out / f'{version}-states.json', results)
    rows = []
    for result in results:
        p, envelope = result['prediction'], result['envelope']
        assert p['status']=='Available' and p['requested_tolerance_met'], p
        assert all(e['status']=='Available' and e['requested_tolerance_met'] for e in envelope), envelope
        row = p['row']
        rows.append(dict(identity=p['identity'], T_K=float(row['T_K']), stock_mol_L=float(row['stock_AMP_mol_per_L']),
            alpha=float(row['alpha_mol_CO2_per_mol_AMP']), observed_Pa=p['observed'], predicted_Pa=p['value'],
            low_alpha_Pa=envelope[0]['value'], high_alpha_Pa=envelope[1]['value']))
    with (out / f'{version}-pressures.csv').open('w') as f:
        w = csv.DictWriter(f, fieldnames=list(rows[0])); w.writeheader(); w.writerows(rows)
    phases = [r['phase'] for r in results]
    assert all(p['requested_tolerance_met'] for p in phases)
    return dict(overall=statistics(rows),
        isotherms={str(t):statistics([r for r in rows if r['T_K']==t]) for t in sorted({r['T_K'] for r in rows})},
        stocks={str(c):statistics([r for r in rows if r['stock_mol_L']==c]) for c in sorted({r['stock_mol_L'] for r in rows})},
        envelope_contains_observed=sum(min(r['low_alpha_Pa'],r['high_alpha_Pa'])<=r['observed_Pa']<=max(r['low_alpha_Pa'],r['high_alpha_Pa']) for r in rows),
        phase={k:[r['identity'] for r in phases if r.get(k)] for k in ('dense','gas','ambiguous','unresolved')})

if __name__ == '__main__':
    OUT.mkdir(exist_ok=True)
    inputs = AN / 'inputs/kundu'
    inputs.mkdir(exist_ok=True)
    old = json.loads((AN / 'results/redesign/summary.json').read_text())
    run = 'redesign-1-A-slope-1'
    original = json.loads((AN / old['runs'][run]['endpoint']).read_text())
    declarations = tomllib.loads((AN / 'inputs/redesign' / f'{run}-declarations.toml').read_text())
    summary = dict(wheel_sha256=SHA256, workers=int(os.environ['AGENT_HEAVY_CORES']),
        starts=old['start_comparisons']['redesign-1-A-slope'], scored='current',
        mea_endpoint=bind(AN.parent / 'solvent_specification_mea/inputs/endpoint.json'), variants={})
    for version in ('historical', 'current'):
        document, decl = copy.deepcopy(original), copy.deepcopy(declarations)
        next(r for r in decl['chemistry']['reactions']['aqueous'] if r['name']=='carbamate-hydrolysis')['correlation'] = old['runs'][run]['law']
        if version == 'current':
            current_shared(document, decl)
        declaration_path = inputs / f'{version}-declarations.toml'
        declaration_path.write_text('\n'.join(f'{k} = {toml_value(v)}' for k,v in decl.items())+'\n')
        endpoint_path = inputs / f'{version}-endpoint.json'
        save(endpoint_path, document)
        configuration = tomllib.loads((AN / f'{run}.toml').read_text())
        configuration.update(declarations=bind(declaration_path), start=bind(endpoint_path), endpoint=bind(endpoint_path),
            caloric=bind(AN.parent / 'solvent_specification_mea/inputs/caloric.json'))
        path = AN / f'kundu-{version}.toml'
        path.write_text('\n'.join(f'{k} = {toml_value(v)}' for k,v in configuration.items())+'\n')
        summary['variants'][version] = dict(score(path, OUT, version, summary['workers']), parameter=bind(endpoint_path), declarations=bind(declaration_path))
        print(version, summary['variants'][version], flush=True)
        save(OUT / 'summary.json', summary)
