"""Diagnose the adopted model's CO2 partial-pressure misfit on the 79 solved-pressure calibration states.

Joins the packet observations, the retained `main-cb16` cold sweep and the adoption-time full replay,
then solves each state once at the adopted reactions and once per +0.05 shift of ln K (R2, R4, R5).
Writes per-state rows and falsifier summaries to results/runs/pco2-calibration-misfit/.
Run single-threaded: OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1 MKL_NUM_THREADS=1.
"""
import csv, math, sys
from pathlib import Path
import numpy as np
from scipy.optimize import lsq_linear

W = Path(__file__).resolve().parents[3]
sys.path[:0] = [str(W / 'analyses/mea_parameter_bundle/scripts'), str(W / 'src')]
import shared_evaluation as shared

A = W / 'analyses/mea_parameter_bundle'
OUT = A / 'results/runs/pco2-calibration-misfit'
SWEEP = A / 'results/runs/reaction-temperature-fit/cold-start-sweep/cold-start-sweep.csv'
FIT = A / 'results/reaction-temperature-fit/full-validation-targets.csv'
STEP = 0.05  # ln K shift
TP = shared.REACTION_REFERENCE_TEMPERATURE_K
# +STEP in ln K for each reaction, expressed on its stored coefficient (R5 is -log10 K = a_k/T + b + c T).
SHIFTS = {'R2': ('reaction:R2:correlation:a', STEP), 'R4': ('reaction:R4:correlation:a', STEP),
          'R5': ('reaction:R5:correlation:b', -STEP / math.log(10.0))}


def rms(x):
    x = np.asarray(x, float)
    return float(np.sqrt(np.mean(x ** 2))) if len(x) else float('nan')


def main():
    shared.verify_wheel()
    shared.RUNS = Path('/tmp/mea-pco2-misfit')  # solve cache stays outside the tree
    prov = {'engine_wheel_sha256': shared.ENGINE_WHEEL_SHA256, 'parameter_sha256': shared.sha256(shared.PARAMETERS),
            'packet_sha256': shared.sha256(shared.STATE_PACKET), 'script_sha256': shared.sha256(Path(__file__))}
    sweep = {r['identity']: r for r in csv.DictReader(SWEEP.open()) if r['label'] == 'main-cb16'}
    fit = {r['observation_id']: r for r in csv.DictReader(FIT.open()) if r['family'] == 'pressure'}
    model = shared.epcsaft.Mixture(shared.load_parameters(shared.PARAMETERS))
    base_reactions = shared._selected_reactions()
    rows = []
    for o in shared.load_state_packet()['observations']:
        req = o['request']
        if req['pressure']['role'] != 'solved':
            continue
        (t,) = o['targets']
        ident = o['identity']
        row = {'identity': ident, 'source': t['source_identity'], 'role': t['role'], 'basis': t['basis'],
               'temperature_k': req['temperature']['value'],
               'loading': req['reaction_system']['feed_amounts_mol'][0] / req['reaction_system']['feed_amounts_mol'][1],
               'observed_pco2_pa': t['observed'], 'sweep_main_cb16_pco2_pa': float(sweep[ident]['co2_partial_pressure_pa']),
               'fit_time_pco2_pa': float(fit[ident]['predicted']) * 1000.0 if ident in fit else float('nan')}
        preds = {}
        for name, change in [('base', None), *SHIFTS.items()]:
            reactions = dict(base_reactions)
            if change:
                reactions[change[0]] += change[1]
            r = shared.evaluate_state(model, req, reactions, ident, [], budget_s=60)
            preds[name] = r['predictions'].get('co2-partial-pressure') if r['status'] == 'evaluated' else None
            print(ident, name, r['status'], preds[name], flush=True)
        row['fresh_pco2_pa'] = preds['base'] or float('nan')
        for k in SHIFTS:
            row[f'dlnp_dlnK_{k}'] = (math.log(preds[k] / preds['base']) / STEP) if preds[k] and preds['base'] else float('nan')
        row['ln_pred_over_obs'] = math.log(row['fresh_pco2_pa'] / row['observed_pco2_pa'])
        row['ln_fresh_over_sweep'] = math.log(row['fresh_pco2_pa'] / row['sweep_main_cb16_pco2_pa'])
        row['ln_fresh_over_fit_time'] = math.log(row['fresh_pco2_pa'] / row['fit_time_pco2_pa'])
        rows.append(row)

    # Local measurement-scatter floor per (source, T): von Neumann estimate on the model residual ordered by loading.
    for r in rows:
        r['residual_step_to_next_loading'] = float('nan')
    groups = {}
    for r in rows:
        groups.setdefault((r['source'], round(r['temperature_k'] - 273.15)), []).append(r)
    for g in groups.values():
        g.sort(key=lambda r: r['loading'])
        for a, b in zip(g, g[1:]):
            a['residual_step_to_next_loading'] = b['ln_pred_over_obs'] - a['ln_pred_over_obs']
        # ln pCO2 change from the sources' stated 2 % relative loading uncertainty, using the observed local slope.
        if len(g) > 2:
            slope = np.gradient([math.log(r['observed_pco2_pa']) for r in g], [r['loading'] for r in g])
            for r, s in zip(g, slope):
                r['ln_pco2_from_2pct_loading'] = float(abs(s) * 0.02 * r['loading'])
    for r in rows:
        r.setdefault('ln_pco2_from_2pct_loading', float('nan'))

    # Hilliard observed vs Jou observed at Hilliard loadings (same T, both 30 wt%), log-linear interpolation in loading.
    for r in rows:
        r['ln_obs_over_jou_interp'] = float('nan')
        jou = sorted((q['loading'], math.log(q['observed_pco2_pa'])) for q in rows
                     if q['source'] == 'Jou1995' and q['temperature_k'] == r['temperature_k'])
        if r['source'] == 'Hilliard2008' and len(jou) > 1 and jou[0][0] <= r['loading'] <= jou[-1][0]:
            r['ln_obs_over_jou_interp'] = math.log(r['observed_pco2_pa']) - float(np.interp(r['loading'], *zip(*jou)))

    # Best reaction-constant corrections in the span of the local ln K sensitivities (linear, prediction only).
    ok = [r for r in rows if all(np.isfinite(r[f'dlnp_dlnK_{k}']) for k in SHIFTS)]
    res = np.array([r['ln_pred_over_obs'] for r in ok])
    J = np.array([[r[f'dlnp_dlnK_{k}'] for k in SHIFTS] for r in ok])
    tau = np.array([[(1 / TP - 1 / r['temperature_k']) * 1e3] for r in ok])  # enthalpy-like coordinate, 1/kK
    fits = {'constant_lnK_R2_R4_R5': J, 'constant_plus_enthalpy_R2_R4_R5': np.hstack([J, J * tau]),
            'constant_lnK_R2_R4_R5_bounded_0.3': J}
    for name, M in fits.items():
        bound = 0.3 if name.endswith('bounded_0.3') else np.inf  # ponytail: 0.3 ln K is a nominal source-sized bound, not a source uncertainty
        delta = lsq_linear(M, -res, bounds=(-bound, bound)).x
        after = res + M @ delta
        for r, v in zip(ok, after):
            r[f'after_{name}'] = float(v)
        fits[name] = (delta, after)

    fields = list(rows[0].keys())
    with (OUT / 'pco2-misfit-states.csv').open('w', newline='') as h:
        w = csv.DictWriter(h, fieldnames=fields + list(prov))
        w.writeheader()
        for r in rows:
            w.writerow({**r, **prov})

    summary = []
    def add(scope, subset, key='ln_pred_over_obs'):
        v = [r[key] for r in subset if np.isfinite(r.get(key, float('nan')))]
        if v:
            summary.append({'scope': scope, 'quantity': key, 'count': len(v), 'mean': float(np.mean(v)), 'rms': rms(v),
                            'aard_percent': 100 * float(np.mean(np.abs(np.expm1(np.array(v))))) if key == 'ln_pred_over_obs' else ''})
    add('all', rows)
    for s in ('Hilliard2008', 'Jou1995'):
        add(f'source={s}', [r for r in rows if r['source'] == s])
    for tc in sorted({round(r['temperature_k'] - 273.15) for r in rows}):
        add(f'T={tc}C', [r for r in rows if round(r['temperature_k'] - 273.15) == tc])
    for lo, hi in ((0, 0.2), (0.2, 0.3), (0.3, 0.5), (0.5, 0.55), (0.55, 1.0)):
        add(f'loading[{lo},{hi})', [r for r in rows if lo <= r['loading'] < hi])
    for s in ('Hilliard2008', 'Jou1995'):
        for tc in (40, 60):
            add(f'source={s},T={tc}C,loading[0.15,0.52]', [r for r in rows if r['source'] == s and
                round(r['temperature_k'] - 273.15) == tc and 0.15 <= r['loading'] <= 0.52])
    add('Hilliard observed vs Jou observed interpolated', rows, 'ln_obs_over_jou_interp')
    steps = [r['residual_step_to_next_loading'] for r in rows if np.isfinite(r['residual_step_to_next_loading'])]
    summary.append({'scope': 'within-(source,T) adjacent-loading scatter floor, sqrt(mean(step^2)/2)', 'quantity': 'ln_pred_over_obs',
                    'count': len(steps), 'mean': '', 'rms': rms(steps) / math.sqrt(2), 'aard_percent': ''})
    add('stated 2 % loading uncertainty propagated to ln pCO2', rows, 'ln_pco2_from_2pct_loading')
    for k in ('fresh_over_sweep', 'fresh_over_fit_time'):
        add('all', rows, f'ln_{k}')
    # Share of residual sum of squares removed by group means (loading bin, temperature, source).
    ss = float(np.sum([r['ln_pred_over_obs'] ** 2 for r in rows]))
    bins = (0.2, 0.3, 0.5, 0.55)
    for label, key in (('loading bin', lambda r: int(np.searchsorted(bins, r['loading'], side='right'))),
                       ('temperature', lambda r: r['temperature_k']), ('source', lambda r: r['source'])):
        grp = {}
        for r in rows:
            grp.setdefault(key(r), []).append(r['ln_pred_over_obs'])
        left = sum(float(np.sum((np.array(v) - np.mean(v)) ** 2)) for v in grp.values())
        summary.append({'scope': f'residual after removing {label} means ({len(grp)} groups); mean = share of sum of squares removed',
                        'quantity': 'ln_pred_over_obs', 'count': len(rows), 'mean': 1 - left / ss,
                        'rms': math.sqrt(left / len(rows)), 'aard_percent': ''})
    for name, (delta, after) in fits.items():
        summary.append({'scope': f'{name}: shifts ' + ' '.join(f'{v:+.3f}' for v in delta), 'quantity': 'ln_pred_over_obs after linear shift',
                        'count': len(after), 'mean': float(np.mean(after)), 'rms': rms(after), 'aard_percent': ''})
    for k in SHIFTS:
        v = [r[f'dlnp_dlnK_{k}'] for r in ok]
        summary.append({'scope': f'sensitivity {k} min/median/max {min(v):+.3f}/{np.median(v):+.3f}/{max(v):+.3f}',
                        'quantity': f'dlnp_dlnK_{k}', 'count': len(v), 'mean': float(np.mean(v)), 'rms': rms(v), 'aard_percent': ''})
    with (OUT / 'pco2-misfit-summary.csv').open('w', newline='') as h:
        w = csv.DictWriter(h, fieldnames=['scope', 'quantity', 'count', 'mean', 'rms', 'aard_percent', *prov])
        w.writeheader()
        for s in summary:
            w.writerow({**s, **prov})
    for s in summary:
        print(s)


if __name__ == '__main__':
    OUT.mkdir(parents=True, exist_ok=True)
    main()
