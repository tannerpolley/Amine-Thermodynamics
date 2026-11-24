"""Issue #409: adopted MEA record F2 (ae17803e…) at absorber versus stripper temperatures; no fit.

`replay EXPORT`: Kim et al. 2014 finite-addition heats, the only comparison not retained for F2, run with the #338 Kim
2007 heat call, on wheel 391dfe5d, from a `git archive` of f7e09b9ec (the commit that produced the F2 evidence).
Run from EXPORT with a Python environment holding that wheel. Retained F2 Kim 2007 393.15 K intervals are recomputed first;
the replay stops unless they reproduce. `table`: band table from the retained F2 evidence and the replay.
"""
import csv
import concurrent.futures
import hashlib
import json
import math
import multiprocessing
import os
from pathlib import Path
import sys

for key in ('OMP_NUM_THREADS', 'OPENBLAS_NUM_THREADS', 'MKL_NUM_THREADS'):
    os.environ[key] = '1'

BUNDLE = Path(__file__).resolve().parents[1]
OUT = BUNDLE / 'results/stripper-temperature-409'
F2 = BUNDLE / 'results/reduced-refit/F2/parameters.json'
EV = BUNDLE / 'results/reduced-refit/evidence/F2'
RECORD_SHA = 'ae17803e1bcb2ca0a1970e05c7cc235d615c4d8a3a349b5afef0b0401dedefed'
KIM_PRODUCER_SHA = '557c943a6c4079b6a2631ab99478086daf515efb218485920b578a5efab1dcc4'  # as run for F2 (inputs.json)
KIM2014 = 'data/reference/MEA/observations/calorimetry/Kim_2014_calorimetry_30wt.csv'
VINJARAPU2024 = 'data/reference/MEA/observations/calorimetry/Vinjarapu_2024_calorimetry_30wt.csv'
ABSORBER_MAX, STRIPPER_MIN = 353.2, 370.0  # K; owner's bands: absorber up to about 353 K, stripper about 370 K and above


def rows(path):
    with Path(path).open() as stream:
        return list(csv.DictReader(stream))


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def load(name, path, subs):
    import importlib.util
    text = Path(path).read_text().replace('Path(__file__)', f'Path({str(path)!r})')
    for old, new in subs:
        assert old in text, (name, old)
        text = text.replace(old, new)
    module = importlib.util.module_from_spec(importlib.util.spec_from_loader(name, loader=None))
    sys.modules[name] = module
    exec(compile(text, str(path), 'exec'), module.__dict__)
    return module


def interval(job):
    T, a, b = job
    k.c.s.RUNS = k.RUNTIME / f'worker-{os.getpid()}'
    return k.heat(T, a, b)


def heat_reference(evidence):
    check = [dict(record_id=r['record_id'], T_K=float(r['T_K']), previous_loading=float(r['previous_loading']),
                  loading=float(r['loading']), retained=float(r['predicted']))
             for r in rows(evidence / 'kim2007-heat-pathways/kim-heat.csv') if float(r['T_K']) == 393.15]
    return check + [dict(record_id=r['id'], T_K=float(r['T_K']), previous_loading=0.,
                         loading=float(r['loading']), retained=-float(r['predicted_kJ_mol']))
                    for r in rows(evidence / 'heat.csv') if r['role'] == 'fitted']


def check_heat_reproduction(reproduction, reference):
    differences = []
    for row, expected in zip(reproduction['rows'], reference, strict=True):
        assert row['status'] == 'available' and all(row[k] == v for k, v in expected.items()), row
        difference = abs(row['replayed'] - expected['retained']) / abs(expected['retained'])
        assert row['relative_difference'] == difference, row
        differences.append(difference)
    worst = max(differences)
    assert worst == reproduction['max_relative_difference'] and worst <= 1e-10, worst  # #340 limit


def replay(export, record=None, record_sha=RECORD_SHA, evidence=None, out=None, *, control=True, kim_2007=False,
           producer_sha=KIM_PRODUCER_SHA):
    global k
    historical_route = out is None
    out, evidence = out or OUT, evidence or EV
    export = Path(export).resolve()
    scripts = export / 'analyses/mea_parameter_bundle/scripts'
    sys.path[:0] = [str(scripts), str(export / 'analyses/mea_parameter_bundle/calibration-misfit'), str(export / 'src')]
    assert sha(scripts / 'kim2007_heat_pathways.py') == producer_sha
    import shared_evaluation as s
    s.verify_wheel()
    record = record if record is not None else export / F2.relative_to(BUNDLE.parents[1])
    assert sha(record) == record_sha
    s.PARAMETERS = record
    s.RUNS = out / 'runtime'
    c = load('model_curves', scripts / 'model_curves.py', [  # the #338 evidence substitutions (candidate_evidence_255.curves)
        ("BUNDLE / 'results/engine-3e83e19c-paper-evidence'", f'Path({str(evidence)!r})'),
        ("BUNDLE / 'results/engine-3e83e19c-refit-chain/restricted-2/attempt-3/run/fit/usable-budget-endpoint.json'", f'Path({str(record)!r})')])
    k = load('kim', scripts / 'kim2007_heat_pathways.py', [])
    k.c, k.CACHE, k.PROBLEMS = c, {}, {}
    k.RUNTIME = out / 'runtime'
    # Reproduction: retained F2 Kim 2007 393.15 K intervals and the 8 fitted Vinjarapu 313.15 K integral heats (0 -> alpha).
    reference = heat_reference(evidence) if control else []
    check = [row.copy() for row in reference]
    source = []
    previous = {}
    for r in rows(export / KIM2014):  # semi-differential; first interval starts at zero, as the F2 Kim 2007 call
        T, a = float(r['temperature_degC']) + 273.15, float(r['CO2_loading_mol_per_mol_MEA'])
        source.append(dict(record_id=r['record_id'], source='Kim2014', T_K=T, previous_loading=previous.get(T, 0.), loading=a,
                           observed_kJ_mol=float(r['dHabs_kJ_per_mol_CO2_reported'])))
        previous[T] = a
    for r in rows(export / VINJARAPU2024):  # Table 5, 120 °C, 17.34 bar: integral from zero loading, the fitted rows' declaration
        if r['source_table'] == 'Table 5':
            assert float(r['system_pressure_bar']) * 1e5 == k.PRESSURE
            source.append(dict(record_id=r['record_id'], source='Vinjarapu2024', T_K=float(r['temperature_degC']) + 273.15, previous_loading=0.,
                               loading=float(r['CO2_loading_mol_per_mol_MEA']), observed_kJ_mol=float(r['dHint_kJ_per_mol_CO2_reported'])))
    kim_rows = k.source_rows() if kim_2007 else []
    jobs = [(r['T_K'], r['previous_loading'], r['loading']) for r in check + source + kim_rows]
    with concurrent.futures.ProcessPoolExecutor(int(os.environ['AGENT_HEAVY_CORES']), mp_context=multiprocessing.get_context('fork')) as pool:
        values = list(pool.map(interval, jobs))
    for r, (q, status) in zip(check, values[:len(check)]):
        r.update(replayed=q, status=status, relative_difference=abs(q - r['retained']) / abs(r['retained']) if q is not None else None)
    worst = max((r['relative_difference'] for r in check if r['relative_difference'] is not None), default=None)
    reproduction = dict(rows=check, max_relative_difference=worst)
    predictions = [dict(r, predicted_kJ_mol=q, status=status) for r, (q, status) in zip(source, values[len(check):len(check)+len(source)], strict=True)]
    if kim_rows:
        from candidate_evidence_255 import table
        for row, (q, status) in zip(kim_rows, values[len(check)+len(source):], strict=True):
            row.update(observed=float(row['dHdiff_kJ_per_mol_CO2_reported']), predicted=q, interval_status=status,
                       scaled_residual=(q-float(row['dHdiff_kJ_per_mol_CO2_reported']))/(.022*abs(float(row['dHdiff_kJ_per_mol_CO2_reported'])))
                       if q is not None else None)
        destination = evidence / 'kim2007-heat-pathways/kim-heat.csv'
        destination.parent.mkdir(parents=True, exist_ok=True)
        table(destination, kim_rows)
    out.mkdir(parents=True, exist_ok=True)
    (out / 'heat-replay.json').write_text(json.dumps(dict(
        parameter_sha256=record_sha, engine_wheel_sha256=s.ENGINE_WHEEL_SHA256, engine_commit=s.ENGINE_COMMIT,
        producer_commit='f7e09b9ec' if historical_route else 'bcf32c440', kim_producer_sha256=producer_sha, sources={p: sha(export / p) for p in (KIM2014, VINJARAPU2024)},
        system_pressure_Pa=k.PRESSURE, loading_ceiling=k.CEILING,
        reproduction=reproduction, rows=predictions), indent=1, allow_nan=False) + '\n')
    if control:
        check_heat_reproduction(reproduction, reference)
    print('reproduction max relative difference', worst, '; available', sum(x['status'] == 'available' for x in predictions), '/', len(predictions))


def band(T):
    return 'absorber' if T <= ABSORBER_MAX else 'stripper' if T >= STRIPPER_MIN else 'intermediate'


def points(record=F2, record_sha=RECORD_SHA, evidence=None, out=None):
    """(property, role, cohort, source, T_K, observed, predicted, unit); heats as positive heat release."""
    out, evidence = out or OUT, evidence or EV
    points = []
    fitted = {r['identity']: r for r in json.loads(record.with_name('replay.json').read_text())['rows']}
    states = rows(evidence / 'state-targets.csv')
    assert {r['record_sha256'] for r in states} == {record_sha}
    for r in states:  # canonical (six-source) and Wagner pCO2; packet rows duplicate canonical ones
        if r['quantity'] == 'pressure' and r['kind'] in ('canonical', 'wagner', 'transfer'):
            role = 'fitted' if r['target'] in fitted else 'not fitted, 15/45 wt%' if r['kind'] == 'transfer' else 'not fitted'
            cohort ='Hilliard 2008 + Jou 1995 (common149)' if role == 'fitted' else {
                'canonical': 'six-source 30 wt%', 'wagner': 'Wagner 2013', 'transfer': 'Aronu 2011 15/45 wt%'}[r['kind']]
            points.append(('CO2 partial pressure', role, cohort, r['source'], float(r['temperature_K']), float(r['observed']), float(r['predicted']), 'Pa'))
    assert sum(p[1] == 'fitted' and p[0] == 'CO2 partial pressure' for p in points) == 47
    for r in rows(evidence / 'heat.csv'):
        role = 'fitted' if r['role'] == 'fitted' else 'not fitted'
        points.append(('heat of absorption', role, r['source'], r['source'], float(r['T_K']), -float(r['observed_kJ_mol']), -float(r['predicted_kJ_mol']), 'kJ/mol CO2'))
    for r in rows(evidence / 'kim2007-heat-pathways/kim-heat.csv'):
        if r['interval_status'] == 'available':
            # #245 flags: run-2 rows 0.078/0.445 inconsistent with their integrals; first 120 °C additions from zero loading
            flagged = r['source_inconsistent'] == 'True' or r['first_120'] == 'True'
            points.append(('heat of absorption', 'not fitted, source-flagged' if flagged else 'not fitted', 'Kim and Svendsen 2007','Kim2007', float(r['T_K']), float(r['observed']), float(r['predicted']), 'kJ/mol CO2'))
    for r in json.loads((out / 'heat-replay.json').read_text())['rows']:
        if r['status'] == 'available':
            cohort = {'Kim2014': 'Kim et al. 2014 (replayed)', 'Vinjarapu2024': 'Vinjarapu 2024 Table 5 (replayed)'}[r['source']]
            points.append(('heat of absorption', 'not fitted', cohort, r['source'], r['T_K'], r['observed_kJ_mol'], r['predicted_kJ_mol'], 'kJ/mol CO2'))
    cp_fitted = {(float(r['T_K']), float(r['loading'])) for r in rows(evidence / 'cp.csv')}
    for r in rows(evidence / 'cp.csv'):
        points.append(('heat capacity', 'fitted', 'Hilliard 2008 (fitted states)', 'Hilliard2008', float(r['T_K']), float(r['observed_kJ_kg_K']), float(r['equilibrium_cp_kJ_kg_K']), 'kJ/(kg K)'))
    capacity = json.loads((evidence / 'heat-capacity-264.json').read_text())
    assert capacity['parameter_sha256'] == record_sha
    for r in capacity['rows']:
        if (r['T_K'], r['loading']) not in cp_fitted:
            points.append(('heat capacity', 'not fitted', f"{r['source']} {'loaded' if r['loading'] > 0 else 'CO2-free'}", r['source'], r['T_K'], r['observed_kJ_kg_K'], r['predicted_kJ_kg_K'], 'kJ/(kg K)'))
    # Not-fitted densities: #268's 234-row comparison on F2, the owner #338 scored; fitted rows from the F2 objective replay.
    compared = {r['identity']: r for r in json.loads((evidence / 'density-268/density.json').read_text())['result']}
    density_fitted = {r['identity'].replace('AMU-DENS-', 'Amundsen2009_state_'): r for r in fitted.values() if 'density' in r['group']}
    assert len(density_fitted.keys() & compared.keys()) == 52 and all(r['status'] == 'Available' for r in compared.values())
    for identity, r in compared.items():
        x = r['row']
        role = 'fitted' if identity in density_fitted else 'not fitted'
        loaded = 'loaded' if float(x['loading']) > 0 else 'CO2-free'
        value = density_fitted[identity]['value'] if role == 'fitted' else r['value']
        points.append(('density', role, f"{x['source']} {loaded}", x['source'], float(x['T_K']), float(x['observed_kg_m3']), value, 'kg/m3'))
    return points


def stats(group):
    errors = [p - o for *_, o, p, _ in group]
    return dict(n=len(group), AARD_percent=100 * sum(abs(e / o) for e, (*_, o, p, _) in zip(errors, group)) / len(group),
                RMSE=math.sqrt(sum(e * e for e in errors) / len(group)), bias=sum(errors) / len(group),
                mean_signed_relative_percent=100 * sum(e / o for e, (*_, o, p, _) in zip(errors, group)) / len(group),
                T_min_K=min(g[4] for g in group), T_max_K=max(g[4] for g in group), unit=group[0][7],
                sources=' '.join(sorted({g[3] for g in group})))


def band_summary(data, level=None):
    keys = sorted({(p[0], p[1], band(p[4]), p[2] if level == 'cohort' else 'all') for p in data})
    summary = []
    for prop, role, b, cohort in keys:
        group = [p for p in data if (p[0], p[1], band(p[4])) == (prop, role, b) and cohort in ('all', p[2])]
        row = dict(property=prop, band=b, role=role)
        if level is not None:
            row['cohort'] = cohort
        summary.append(dict(row, **stats(group)))
    return summary


def compare_bands(groups):
    reference = {(x['property'], x['role'], x['band']): x
                 for x in rows(OUT / 'band-table.csv') if x['cohort'] == 'all'}
    assert len(groups) == len(reference)
    differences = []
    for x in groups:
        ref = reference[x['property'], x['role'], x['band']]
        n, aard = int(ref['n']), float(ref['AARD_percent'])
        assert x['n'] == n and round(x['AARD_percent'], 2) == round(aard, 2), (x, ref)
        differences.append(dict(x, historical_n=n, historical_aard_percent=aard,
                                delta_percentage_points=x['AARD_percent']-aard))
    return differences


def table():
    data = points()
    # Falsifier: whole cohorts, regrouped here, must reproduce #338's F2 agreement.csv AARD.
    agreement = {r['dataset']: float(r['aard_percent']) for r in rows(F2.parents[1] / 'agreement.csv') if r['fit'] == 'F2'}
    checks = {'not fitted: six-source pressures': lambda p: p[2] == 'six-source 30 wt%', 'not fitted: Wagner pressures': lambda p: p[2] == 'Wagner 2013',
              'not fitted: Arcis heats': lambda p: p[3] == 'Arcis2011', 'not fitted: Han densities': lambda p: p[3] == 'Han2012',
              'not fitted: Kim heats': lambda p: p[3] == 'Kim2007' and p[4] < 370, 'fitted: fitted CO2 partial pressure': lambda p: p[0] == 'CO2 partial pressure' and p[1] == 'fitted',
              'fitted: fitted heat of absorption': lambda p: p[0] == 'heat of absorption' and p[1] == 'fitted'}
    regrouped = {name: stats([p for p in data if rule(p)])['AARD_percent'] for name, rule in checks.items()}
    assert all(abs(regrouped[n] - agreement[n]) <= 1e-9 * agreement[n] for n in checks), (regrouped, agreement)
    (OUT / 'agreement-check.json').write_text(json.dumps({n: dict(regrouped=regrouped[n], agreement_csv=agreement[n]) for n in checks}, indent=1) + '\n')
    summary = [row for level in ('role', 'cohort') for row in sorted(
        band_summary(data, level), key=lambda x: (x['property'], x['band'], x['role'], x['cohort']))]
    with (OUT / 'band-table.csv').open('w', newline='') as stream:
        writer = csv.DictWriter(stream, list(summary[0]), lineterminator='\n')
        writer.writeheader()
        writer.writerows(summary)
    with (OUT / 'points.csv').open('w', newline='') as stream:
        writer = csv.writer(stream, lineterminator='\n')
        writer.writerow(('property', 'role', 'cohort', 'source', 'T_K', 'band', 'observed', 'predicted', 'unit'))
        writer.writerows((*p[:5], band(p[4]), *p[5:]) for p in data)
    for s in summary:
        if s['cohort'] == 'all':
            print(f"{s['property']:22} {s['band']:12} {s['role']:10} n={s['n']:3} AARD={s['AARD_percent']:6.2f}% bias={s['bias']:+.4g} {s['unit']} [{s['T_min_K']}-{s['T_max_K']}] {s['sources']}")


if __name__ == '__main__':
    {'replay': lambda: replay(sys.argv[2]), 'table': table}[sys.argv[1]]()
