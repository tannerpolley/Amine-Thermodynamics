"""Issue 283: reciprocal-temperature k_ij slopes for MEACOO-–water and MEAH+–MEACOO-; no adoption.

Design: issue #283 body (readiness Ready). Reuses the #255 driver (stable_refit_255) and downstream rerun
(candidate_evidence_255) on the same bc779473 wheel. Outputs: results/ion-temperature-283/.
Commands (repository root, worktree .venv, background `agent-heavy`):
  qualify | fit <a|b> | assess <a|b> | extras <a|b> | select | attribute | regress | evidence | compare | present
"""
# ruff: noqa: E402 -- the #255 driver sets library threads and the wheel identity before Engine imports.
import copy
import csv
import json
import math
from pathlib import Path
import sys
from types import SimpleNamespace

sys.path.insert(0, str(Path(__file__).parent))
import stable_refit_255 as r
import numpy as np

s, d, reg = r.s, r.d, r.reg
R255 = r.OUT
OUT = r.OUT = r.B / 'results/ion-temperature-283'  # every r.write/r.result/census/retreat now targets this issue
ISSUE = 'https://tnnrpolley21-ms-7c95.taila72856.ts.net:3000/tannerpolley/Amine-Thermodynamics/issues/283'
SLOPES = (('carbamate-anion', 'water'), ('carbamate-anion', 'protonated-monoethanolamine'))
SLOPE_IDS = [f'pair/{a}/{b}/k_ij/reciprocal_temperature_slope' for a, b in SLOPES]
MEAH_SLOPE = 'pair/protonated-monoethanolamine/water/k_ij/reciprocal_temperature_slope'
# Start (a): #255 variant (b) endpoint; start (b): #255 primary candidate with the R4 shift at 0. Both slopes start at 0.
STARTS = {'a': 'joint-chemistry', 'b': 'wide'}
STAGE = 3e-3
SLOPE_COORDINATES = [dict(targets=[['k_ij_reciprocal_temperature_slope', list(p), 1.]], identity=i, origin=0., scale=10.,
                          bounds=[-1000., 1000.]) for p, i in zip(SLOPES, SLOPE_IDS, strict=True)]
_coordinates = r.coordinates
# The 17 variant (b) coordinates (16 #255 + R4 shift) plus the two slopes: 19.
r.coordinates = lambda *args, **kw: _coordinates(*args, **kw) + copy.deepcopy(SLOPE_COORDINATES)


def with_slopes(mapping, values=(0., 0.)):
    """Record with the two slope entries at `values` (K), reference temperature 313.15 K (Engine applies k(T) only when declared)."""
    out = copy.deepcopy(mapping)
    for (a, b), identity, value in zip(SLOPES, SLOPE_IDS, values, strict=True):
        pair = next(p for p in out['pairs'] if (p['component_id_a'], p['component_id_b']) == (a, b))
        pair['coefficients'] = [c for c in pair['coefficients'] if c['identity'] != identity] + [dict(
            family='k_ij_reciprocal_temperature_slope', identity=identity, value=dict(magnitude=float(value), unit='kelvin'),
            reference_temperature=dict(magnitude=313.15, unit='kelvin'), qualification='candidate_extrapolation',
            candidate_domain_id='mea-candidate-293-15-to-393-15-k', provenance=dict(source_id='issue-283-hypothesis', locator=ISSUE))]
    return out


def r255(rel):
    payload = r.read(R255 / rel)
    assert payload['wheel_sha256'] == r.SHA
    return payload['result']


def start(run):
    name = STARTS[run]
    return with_slopes(r255(f'{name}/candidate.json')), r255(f'{name}/retreat.json')['shifts']


def records(spec, mapping):
    """The 317 fitted rows: the 307 #255 rows plus the 10 Böttinger 353.15 K targets (#263 all-five)."""
    return [(x, x['weight']) for x in spec.inputs['observations']['fitted']], r.bottinger_targets(spec, mapping)


def bottinger(mapping):
    spec = r.bind(mapping)
    rows = []
    for x in r.bottinger_targets(spec, mapping):
        p = reg.predict(spec.model, x['item'])
        scale = .1 * x['observed'] + .001
        rows.append(dict(identity=x['identity'], species=x['species'], observed=x['observed'], predicted=p.value, status=p.status.name,
                         relative_error_percent=100 * (p.value / x['observed'] - 1), cost=.5 * ((p.value - x['observed']) / scale) ** 2))
    return dict(rows=rows, cost=math.fsum(x['cost'] for x in rows),
                maximum_carbamate_excess_percent=max(x['relative_error_percent'] for x in rows if x['species'] == 'MEACOO-'))


# ---------------------------------------------------------------- loading-controlled transfer regression

STRENGTH = {x['record_id']: round(100 * float(x['mea_mass_fraction'])) for x in csv.DictReader(
    (r.ROOT / 'data/reference/MEA/manifests/grouped_split_manifest.csv').open()) if x['source_key'] == 'Aronu2011'}
DT = 1 / 313.15 - 1 / 353.15


def aronu(mapping):
    """The 106 Aronu 2011 rows (outside the fit), evaluated through #261's study declarations at this record."""
    saved, r.TOML = r.TOML, r.SPEC261
    try:
        spec = r.bind(mapping)
        ids = set(r.read(r.B / 'results/pressure-transfer-261/recommendation-data-roles.json')['roles']['outside_fit_concentration_source'])
        chosen = [x for x in spec.inputs['observations']['comparisons'] + spec.inputs['observations']['fitted'] if x['identity'] in ids]
        values = d.evaluate(spec, chosen)
    finally:
        r.TOML = saved
    assert len(chosen) == 106 and all(v['status'] == 'Available' for v in values)
    return [dict(identity=x['identity'], wt_percent=STRENGTH[x['identity'].removesuffix('-pco2')], T_K=x['row']['T_K'], loading=x['row']['loading'],
                 observed=v['observed'], predicted=v['value'], ln_ratio=math.log(v['value'] / v['observed'])) for x, v in zip(chosen, values, strict=True)]


def regression(rows):
    """Per strength, least squares ln(p_calc/p_obs) = c0 + c1/T + c2*alpha. The 313 -> 353 K rise at fixed loading is
    -c1(1/313.15 - 1/353.15). Standard errors assume independent residuals (descriptive linear model, sparse isotherms)."""
    out = {}
    for w in (15, 30, 45):
        chosen = [x for x in rows if x['wt_percent'] == w]
        X = np.array([[1., 1 / x['T_K'], x['loading']] for x in chosen])
        y = np.array([x['ln_ratio'] for x in chosen])
        c = np.linalg.lstsq(X, y, rcond=None)[0]
        cov = float((y - X @ c) @ (y - X @ c)) / (len(y) - 3) * np.linalg.inv(X.T @ X)
        out[w] = dict(n=len(chosen), c0=c[0], c1_K=c[1], c2=c[2], rise=-c[1] * DT, rise_se=DT * math.sqrt(cov[1, 1]),
                      loading_slope=c[2], loading_slope_se=math.sqrt(cov[2, 2]), mean_loading=float(X[:, 2].mean()),
                      aard_percent=100 * float(np.mean([abs(x['predicted'] / x['observed'] - 1) for x in chosen])),
                      mean_ln_ratio=float(y.mean()))
    return out


# ---------------------------------------------------------------- qualification

def qualify():
    """Replay both #255 starts within 1e-8 of their retained values; declaring both slopes at 0 changes predictions by <= 1e-12."""
    r.verify()
    out = dict(excluded=r255('qualification/summary.json')['excluded'])
    final = s.parameter_mapping(r.STARTS['final'])
    values, ok, cost = r.replay(final)
    retained = {v['identity']: v for v in r255('qualification/final-replay.json')}
    out['final'] = dict(available=ok, cost=cost, maximum_row_difference=max(r.compare(values, retained, (('value', 'value'), ('residual', 'residual')))))
    r.write('qualification/final-replay.json', values)
    for run, name in STARTS.items():
        bare = r255(f'{name}/candidate.json')
        values, ok, cost = r.replay(bare)
        retained = {v['identity']: v for v in r255(f'{name}/replay.json')}
        b = bottinger(bare)
        kept = {x['identity']: x['predicted'] for x in r255('joint-chemistry/extras.json')['primary' if name == 'wide' else name]['bottinger_353']}
        zero_values, zero_ok, zero_cost = r.replay(with_slopes(bare))
        z = bottinger(with_slopes(bare))
        out[run] = dict(start=name, available=ok and zero_ok, cost=cost, bottinger_cost=b['cost'], cost_317=cost + b['cost'],
                        maximum_row_difference=max(r.compare(values, retained, (('value', 'value'), ('residual', 'residual')))),
                        maximum_bottinger_difference=max(abs(x['predicted'] / kept[x['identity']] - 1) for x in b['rows']),
                        zero_slope_maximum_difference=max([abs(u['value'] - v['value']) / max(1., abs(v['value'])) for u, v in zip(zero_values, values, strict=True)]
                                                          + [abs(u['predicted'] / v['predicted'] - 1) for u, v in zip(z['rows'], b['rows'], strict=True)]),
                        zero_slope_cost_difference=zero_cost - cost)
        print(run, json.dumps(out[run]), flush=True)
    # The regression input path: direct evaluation equals the #255 downstream transfer and canonical rows.
    for name, mapping in (('final', final), ('candidate', r255('wide/candidate.json'))):
        rows = aronu(mapping)
        kept = {x['identity'].split(':')[-1]: float(x['predicted']) for f in ('transfer', 'canonical-pressure')
                for x in csv.DictReader((R255 / f'evidence/{name}/{f}.csv').open()) if x['source'] == 'Aronu2011'}
        out[f'aronu_{name}'] = dict(rows=len(rows), maximum_relative_difference=max(abs(x['predicted'] / kept[x['identity'].removesuffix('-pco2')] - 1) for x in rows))
    out['passed'] = (out['final']['available'] and out['final']['maximum_row_difference'] <= 1e-8
                     and all(out[k]['available'] and out[k]['maximum_row_difference'] <= 1e-8 and out[k]['maximum_bottinger_difference'] <= 1e-8
                             and out[k]['zero_slope_maximum_difference'] <= 1e-12 for k in STARTS)
                     and all(out[f'aronu_{n}']['maximum_relative_difference'] <= 1e-8 for n in ('final', 'candidate')))
    r.write('qualification/summary.json', out)
    assert out['passed'], 'qualification failed: see qualification/summary.json'


# ---------------------------------------------------------------- fit, assessment, selection

def fit(run):
    """One 3e-3 penalty stage from a stable start, then the #255 retreat toward that start (stop rule as the #255 variants)."""
    r.verify()
    q = r.result('qualification/summary.json')
    assert q['passed']
    enforced = [x for x in r.states()[0] if x['key'] not in q['excluded']]
    mapping, shifts = start(run)
    report = r.stage_fit(run, 0, STAGE, mapping, shifts, enforced, (), ('R4',), None, r.bottinger_353)
    available = report.get('endpoint_replay_available')
    r.retreat(run, mapping, r.result(f'{run}/stage-0/parameters.json') if available else None, enforced, None,
              (shifts, report['endpoint_shifts'] if available else None))


def assess(run):
    """#255 criteria 1-3 against the final set (stable_refit_255.assess) for this run's candidate."""
    r.assess(run)


def select():
    """The usable endpoint with the lower 317-row cost (307 rows plus the 10 Böttinger rows)."""
    runs = {run: r.result(f'{run}/extras.json') for run in STARTS}
    chosen = min(runs, key=lambda run: runs[run]['cost_317'])
    r.write('primary.json', dict(run=chosen, rule='lower 317-row cost', runs={k: {f: v[f] for f in ('cost_307', 'cost_317', 'passed', 't')}
                                                                             for k, v in runs.items()}))


def uncertainty(mapping, shifts):
    """Conditional standard errors and correlations at the record (refit.identifiability): 317 weighted rows, the
    covariance of the off-bound coordinates with on-bound coordinates held fixed."""
    import refit
    spec = r.bind(mapping)
    declared = r.coordinates(spec, shifts, (), ('R4',))
    values = s.parameter_values(mapping)
    for q in declared:  # evaluate at the record itself: q = origin at optimizer 0
        if 'targets' in q:
            q['origin'] = values[q['identity']]
    spec.inputs['coordinates'] = declared
    fitted, targets = records(spec, mapping)
    observations = [spec.observation(x) for x, _ in fitted] + [x['item'] for x in targets]
    weights = np.array([w for _, w in fitted] + [1.] * len(targets))
    ev = reg.differentiate(spec.parameters, spec.coordinates(), observations, optimizer=[0.] * len(declared), holds=[], thermochemistry=spec.thermal)
    replayed = d.evaluate(spec, [x for x, _ in fitted])
    residual = np.array([v['residual'] for v in replayed] + [(x['predicted'] - x['observed']) / (.1 * x['observed'] + .001) for x in bottinger(mapping)['rows']])
    prediction_error = max(abs(p - v) / max(1., abs(v)) for p, v in zip(ev.predictions, [v['value'] for v in replayed] + [x['predicted'] for x in bottinger(mapping)['rows']], strict=True))
    scales = np.array([q['scale'] for q in declared])
    J = np.array(ev.residual_optimizer_gradient).reshape(len(observations), len(declared)) * np.sqrt(weights)[:, None] / scales
    q_values = [q['origin'] for q in declared]  # enthalpy shifts are increments (0) inside total-shift bounds
    lower, upper = [q['bounds'][0] for q in declared], [q['bounds'][1] for q in declared]
    active = [k for k, q in enumerate(q_values) if min(q - lower[k], upper[k] - q) <= 1e-6 * scales[k]]
    ids = [q['identity'] for q in declared]
    out = refit.identifiability(SimpleNamespace(physical=q_values, covariance=SimpleNamespace(active_bounds=active)),
                                J, np.sqrt(weights) * residual, ids, lower, upper)
    return dict(out, prediction_error=prediction_error, coordinates=ids, values=q_values, on_bounds=[ids[k] for k in active])


def k_range(mapping):
    """k_ij(T) = k + b(1/T - 1/313.15) at the domain ends 293.15 and 393.15 K (monotone in 1/T), and 1 - k > 0."""
    v = s.parameter_values(mapping)
    out = {}
    for pair, identity in [(('protonated-monoethanolamine', 'water'), MEAH_SLOPE), *zip(SLOPES, SLOPE_IDS)]:
        k, b = v[f'pair/{pair[0]}/{pair[1]}/k_ij'], v.get(identity, 0.)
        ends = [k + b * (1 / T - 1 / 313.15) for T in (293.15, 393.15)]
        out['/'.join(pair)] = dict(k_313=k, slope_K=b, k_293=ends[0], k_393=ends[1], one_minus_k_positive=all(1 - x > 0 for x in ends))
    return out


def extras(run):
    """Issue outcomes at the start and at this run's candidate: costs, Böttinger table, transfer regression, slopes, k(T)."""
    r.verify()
    mapping, shifts = start(run)
    candidate = r.result(f'{run}/candidate.json')
    a = r.result(f'{run}/assessment.json')
    fit_report = r.result(f'{run}/stage-0/fit.json')
    retreat = r.result(f'{run}/retreat.json')
    b = bottinger(candidate)
    v = s.parameter_values(candidate)
    out = dict(run=run, start=STARTS[run], t=retreat['t'], shifts=retreat['shifts'], passed=a['passed'], stability_passed=a['stability_passed'],
               cost_307=a['cost'], bottinger_cost=b['cost'], cost_317=a['cost'] + b['cost'],
               fit=dict(status=fit_report['status'], iterations=fit_report['iterations'], initial_cost=fit_report['initial_cost'],
                        data_cost=fit_report['data_cost'], stability_cost=fit_report['stability_cost'], wall_s=fit_report['wall_s'],
                        stability_tally=fit_report['stability_tally'], endpoint_prediction_difference=fit_report.get('endpoint_prediction_difference')),
               bottinger_start=bottinger(mapping), bottinger=b, slopes={k: v[k] for k in SLOPE_IDS + [MEAH_SLOPE]},
               k_range=k_range(candidate), regression=regression(aronu(candidate)),
               uncertainty=uncertainty(candidate, retreat['shifts']))
    if fit_report.get('endpoint_replay_available'):
        # The penalty-stage endpoint before the retreat (t = 1): diagnostic only, it has resolved descent at the listed states.
        stage = r.result(f'{run}/stage-0/parameters.json')
        measured = fit_report['stability_predictions'][-len(fit_report['enforced']):]
        out['stage_endpoint'] = dict(cost_307=fit_report['endpoint_replay_cost'], shifts=fit_report['endpoint_shifts'], bottinger=bottinger(stage),
                                     slopes={k: s.parameter_values(stage)[k] for k in SLOPE_IDS + [MEAH_SLOPE]}, k_range=k_range(stage),
                                     regression=regression(aronu(stage)),
                                     descent=[dict(key=k, tau=p['value']) for k, p in zip(fit_report['enforced'], measured, strict=True)
                                              if p and p.get('available') and p['value'] < 0])
        out['stage_endpoint']['cost_317'] = out['stage_endpoint']['cost_307'] + out['stage_endpoint']['bottinger']['cost']
    r.write(f'{run}/extras.json', out)
    print(run, json.dumps({k: out[k] for k in ('t', 'passed', 'cost_307', 'cost_317', 'slopes')}),
          b['maximum_carbamate_excess_percent'], json.dumps({w: round(x['rise'], 3) for w, x in out['regression'].items()}), flush=True)


def attribute():
    """Selected endpoint with each new slope set back to 0 in turn, every other parameter fixed (no stability search)."""
    r.verify()
    run = r.result('primary.json')['run']
    candidate = r.result(f'{run}/candidate.json')
    v = s.parameter_values(candidate)
    cases = {'endpoint': candidate, **{f'{i} = 0': s.with_parameter_values(candidate, {i: 0.}) for i in SLOPE_IDS},
             'both slopes = 0': s.with_parameter_values(candidate, dict.fromkeys(SLOPE_IDS, 0.))}
    out = dict(run=run, slopes={i: v[i] for i in SLOPE_IDS}, cases={})
    for name, mapping in cases.items():
        values, ok, cost = r.replay(mapping)
        b = bottinger(mapping)
        out['cases'][name] = dict(available=ok, cost_307=cost, cost_317=None if cost is None else cost + b['cost'], bottinger=b,
                                  regression=regression(aronu(mapping)))
        print(name, cost, b['maximum_carbamate_excess_percent'], json.dumps({w: round(x['rise'], 3) for w, x in out['cases'][name]['regression'].items()}), flush=True)
    r.write('attribution.json', out)


# ---------------------------------------------------------------- downstream rerun (#255 stage-3 producers)

def evidence():
    """candidate_evidence_255 producers on the selected endpoint. The final set's outputs are #255's on the same wheel and inputs
    (evidence/final links to them); the MDEA rerun covers what MDEA shares with the record (bicarbonate-water k, R2 law)."""
    import candidate_evidence_255 as c  # imported after r.OUT moved: its EV and RECORDS are under this issue
    r.verify()
    run = r.result('primary.json')['run']
    c.EV.mkdir(parents=True, exist_ok=True)
    if not c.RECORDS['candidate'].exists():
        c.RECORDS['candidate'].write_text(json.dumps(r.result(f'{run}/candidate.json'), indent=2, allow_nan=False) + '\n')
    final = c.EV / 'final'
    if not final.exists():
        final.symlink_to(Path('../../stable-refit-255/evidence/final'))
    c.assessment('candidate')
    c.point_data('candidate', run)
    curves = c.curves('candidate')
    if not (c.EV / 'candidate/model-curves/summary.json').exists():
        c.run('candidate', curves, [])
    c.kim('candidate', curves)
    c.density('candidate')
    c.heat_capacity('candidate')
    mapping = s.parameter_mapping(c.RECORDS['candidate'])
    c.mdea(s.parameter_values(mapping)['pair/bicarbonate-anion/water/k_ij'], c.r2_law(mapping))


def compare():
    import candidate_evidence_255 as c
    c.compare()


def regress():
    """The loading-controlled transfer regression on the final set, the #255 candidate and the selected endpoint."""
    r.verify()
    run = r.result('primary.json')['run']
    sets = {'final set': s.parameter_mapping(r.STARTS['final']), '#255 candidate': r255('wide/candidate.json'), 'new endpoint': r.result(f'{run}/candidate.json')}
    out = {}
    for name, mapping in sets.items():
        rows = aronu(mapping)
        out[name] = dict(regression=regression(rows), rows=rows)
    r.write('regression.json', dict(run=run, sets=out))


def present():
    """Presentation only, from regression.json: loading-controlled residual against temperature for each strength."""
    import matplotlib
    matplotlib.use('Agg')
    import matplotlib.pyplot as plt
    sets = r.result('regression.json')['sets']
    colors = {'final set': '#333333', '#255 candidate': '#0072B2', 'new endpoint': '#D55E00'}
    fig, axes = plt.subplots(1, 3, figsize=(12, 4), sharey=True)
    plotted = []
    for ax, w in zip(axes, ('15', '30', '45'), strict=True):
        for name, color in colors.items():
            g = sets[name]['regression'][w]
            rows = [x for x in sets[name]['rows'] if str(x['wt_percent']) == w]
            # Residual moved to the strength's mean loading with the fitted loading slope; line is the fitted 1/T term there.
            points = [(x['T_K'], x['ln_ratio'] - g['c2'] * (x['loading'] - g['mean_loading'])) for x in rows]
            ax.plot(*zip(*points), 'o', mfc='none', ms=4, color=color, alpha=.8)
            T = np.linspace(313.15, 353.15, 41)
            line = g['c0'] + g['c1_K'] / T + g['c2'] * g['mean_loading']
            ax.plot(T, line, '-', color=color, lw=1.5, label=f"{name}: rise {g['rise']:+.2f} ± {g['rise_se']:.2f}")
            plotted += [dict(strength_wt_percent=w, set=name, series='row at mean loading', T_K=t, value=v) for t, v in points]
            plotted += [dict(strength_wt_percent=w, set=name, series='fitted line', T_K=t, value=v) for t, v in zip(T, line)]
        ax.axhline(0, color='0.6', lw=.8)
        ax.set(title=f'{w} wt% MEA (Aronu 2011)', xlabel='Temperature / K')
        ax.legend(fontsize=7, loc='lower left')
    axes[0].set_ylabel('ln(p$_{calc}$/p$_{obs}$) at the mean loading')
    fig.tight_layout()
    fig.savefig(OUT / 'transfer-temperature-term.png', dpi=180)
    with (OUT / 'transfer-temperature-term-plotted-values.csv').open('w', newline='') as stream:
        writer = csv.DictWriter(stream, list(plotted[0]), lineterminator='\n')
        writer.writeheader()
        writer.writerows(plotted)


if __name__ == '__main__':
    command, *rest = sys.argv[1:]
    {'qualify': qualify, 'fit': fit, 'assess': assess, 'select': select, 'extras': extras, 'attribute': attribute,
     'evidence': evidence, 'compare': compare, 'regress': regress, 'present': present}[command](*rest)
