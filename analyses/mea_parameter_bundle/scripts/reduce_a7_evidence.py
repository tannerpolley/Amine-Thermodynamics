"""Reduce retained A7 results for #196; no Engine solve or differentiation."""
import csv
import hashlib
import json
import math
from pathlib import Path
import shutil


ROOT = Path(__file__).resolve().parents[3]
BUNDLE = ROOT / 'analyses/mea_parameter_bundle'
BASE = BUNDLE / 'results/engine-3e83e19c-refit-chain'
OUT = BUNDLE / 'results/engine-3e83e19c-paper-evidence'
FIT = BASE / 'restricted-2/attempt-3'
ASSESSMENT = OUT / 'selected-assessment'
INPUTS = {}


def bind(path):
    INPUTS[str(path.relative_to(ROOT))] = hashlib.sha256(path.read_bytes()).hexdigest()
    return path


def load(path):
    return json.loads(bind(path).read_text())


def read(path):
    return list(csv.DictReader(bind(path).open()))


def write(name, value):
    (OUT / name).write_text(json.dumps(value, indent=2, allow_nan=False) + '\n')


def table(name, rows):
    with (OUT / name).open('w', newline='') as stream:
        writer = csv.DictWriter(stream, list(dict.fromkeys(k for r in rows for k in r)), lineterminator='\n')
        writer.writeheader()
        writer.writerows(rows)


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    bind(Path(__file__))
    endpoint = load(FIT / 'run/fit/usable-budget-endpoint.json')
    selected = bind(FIT / 'run/fit/usable-budget-endpoint.json')
    sha = INPUTS[str(selected.relative_to(ROOT))]
    assert sha == '00e77608a8489fc9e03a7d2a86c08cb5ff782bb441368a62fa6390b8bfe9cc91'
    spec = load(FIT / 'spec.json')
    for item in spec['inputs']:
        assert INPUTS.setdefault(item['path'], hashlib.sha256((ROOT / item['path']).read_bytes()).hexdigest()) == item['sha256']
    native = load(FIT / 'run/fit/native.json')
    replay = load(BASE / 'displays/reported/full-replay.json')
    score = load(BASE / 'displays/reported/score.json')
    declarations = {r['id']: r for r in native['rows']}
    assert len(replay) == len(declarations) == 307 and {r['target'] for r in replay} == set(declarations)
    common = set(spec['observations'][0]['ordered_row_ids'])
    loaded = set(spec['loaded_density_ids'])
    groups = {}
    fitted = []
    for row in replay:
        d = declarations[row['target']]
        assert row['status'] == 'Available' and math.isfinite(row['predicted'])
        assert all(row[k] == d.get(k, 1.) for k in ('observed', 'scale', 'weight'))
        group = ('common149' if d['id'] in common else 'loaded density' if d['id'] in loaded else 'CO2-free density'
            if d['id'].startswith('AMU-DENS') else 'Cai' if d['id'].startswith('cai') else 'Kiepe'
            if d['id'].startswith('kiepe') else 'Cp' if d['id'].startswith('Hilliard2008_Cp') else 'Jakobsen'
            if d['id'].startswith('Jakobsen') else 'restored species')
        fitted.append(dict(row, id=d['id'], quantity=d['quantity'], group=group, declaration=d))
        groups.setdefault(group, []).append(row)
        assert math.isclose(row['cost'], .5 * row['weight'] * row['residual']**2, rel_tol=1e-12, abs_tol=1e-12)
    assert {k: len(v) for k, v in groups.items()} == dict(common149=149, **{'restored species':7, 'Jakobsen':6,
        'loaded density':47, 'CO2-free density':5, 'Cai':50, 'Kiepe':39, 'Cp':4})
    for name, predicate in [('pressure', lambda r:r['target'].endswith('-pco2')),
                            ('heat', lambda r:r['target'].startswith('vinjarapu')),
                            ('species', lambda r:'::' in r['target'])]:
        groups['common149 ' + name] = [r for r in groups['common149'] if predicate(r)]
    stats = {k:dict(n=len(v), cost=math.fsum(r['cost'] for r in v),
        AARD_percent=100 * math.fsum(abs(r['predicted']/r['observed']-1) for r in v)/len(v)) for k,v in groups.items()}
    cost = math.fsum(r['cost'] for r in replay)
    assert math.isclose(cost, score['cost'], rel_tol=1e-10) and math.isclose(cost, native['final_cost'], rel_tol=1e-10)
    assert math.isclose(stats['common149']['cost'], score['C149'], rel_tol=1e-10)
    table('fitted-rows.csv', fitted)
    conditional = BASE / 'displays/conditional'
    for name in ('conditional-uncertainty.json','conditional-standard-errors.csv','conditional-correlations.csv'):
        shutil.copyfile(bind(conditional / name), OUT / name)
    coordinates = load(conditional / 'conditional-uncertainty.json')['coordinate_map']
    bind(FIT / 'run/fit/chemistry-coordinates.json')
    write('fit-summary.json', dict(cost=cost, groups=stats, iterations=native['iterations'], coordinates=coordinates,
        active_bounds=native['covariance']['active_bounds'], gate_score=score, engine=spec['engine'], record_sha256=sha))
    for name in ('state-targets.csv', 'state-summary.json', 'states-excluded.json', 'states-unavailable.json',
                 'summary.json', 'verification.json', 'density.csv', 'cp.csv', 'carbonate-share.csv'):
        shutil.copyfile(bind(ASSESSMENT / name), OUT / name)
    states = read(ASSESSMENT / 'state-targets.csv')
    assert len(states) == len({(r['kind'],r['identity'],r['target']) for r in states}) == 462
    assert all(r['status']=='Available' and r['record_sha256']==sha for r in states)
    for name, kind, quantity, count in [('pressure-figure-data.csv','packet','pressure',79),
        ('species-figure-data.csv','packet','species',131), ('canonical-pressure.csv','canonical','pressure',159),
        ('wagner-pressure.csv','wagner','pressure',23), ('transfer.csv','transfer','pressure',70)]:
        rows = [r for r in states if (r['kind'],r['quantity'])==(kind,quantity)]
        assert len(rows)==count
        table(name, rows)
    pool = [r for r in states if r['kind']=='packet' and r['source']=='Matin2012' and r['species']=='HCO3-']
    assert len(pool)==19 and not any(r['target'] in declarations for r in pool)
    table('pool-figure-data.csv', pool)
    state_summary = load(ASSESSMENT / 'state-summary.json')
    for name, cohort in state_summary['scores'].items():
        rows = [r for r in states if r['target'] in cohort['row_ids'] and r['identity'] in cohort['state_ids']]
        assert len(rows)==cohort['n_total'] and set(cohort['row_ids'])=={r['target'] for r in rows}
        aard = 100 * math.fsum(abs(float(r['predicted'])/float(r['observed'])-1) for r in rows)/len(rows)
        assert math.isclose(aard, cohort['AARD_percent'], rel_tol=1e-12)
    table('high-temperature-comparison.csv', [dict(cohort=k, **{f:v for f,v in c.items() if f not in ('row_ids','state_ids')})
        for k,c in state_summary['scores'].items() if '100-120' in k])
    heats = read(ASSESSMENT / 'heats.csv')
    sources = {r['record_id']:r for r in load(ROOT / spec['heat_rows_path'])}
    assert len(heats)==22 and {r['id'] for r in heats}==set(sources)
    table('heat.csv', [dict(r, scale_J_mol_CO2=sources[r['id']]['uH_J_per_mol_CO2'], unit='kJ/mol CO2',
        role='fitted' if r['id'] in declarations else 'non-fitted prediction', source_row=sources[r['id']]) for r in heats])
    phase = read(BUNDLE / 'results/engine-3e83e19c-phase-search/run-2/phase-family.csv')
    assert len(phase)==324
    table('phase-family.csv', phase)
    write('input-hashes.json', INPUTS)
    print(json.dumps(dict(objective_rows=307, cost=cost, groups=stats, state_rows=462, phase_rows=len(phase)), indent=2))


if __name__ == '__main__':
    main()
