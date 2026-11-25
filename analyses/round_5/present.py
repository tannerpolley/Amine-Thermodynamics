"""Generate the Round 5 manuscript handoff from retained records only."""
import argparse
import gzip
import json
from pathlib import Path

HERE = Path(__file__).resolve().parent
RESULTS = HERE/'results'
AMP_ORIGINAL = HERE.parent/'amp_transfer/results/retransfer-412-f2-05e94210'


def load(name):
    p = RESULTS/name
    if not p.is_file():
        return None
    with (gzip.open(p,'rt') if p.suffix == '.gz' else p.open()) as stream:
        return json.load(stream)


def original_slope():
    source = AMP_ORIGINAL/'main/parameters.json'
    coords = json.loads(source.read_text())['coordinates']
    value = next(c['origin'] for c in coords if c['identity']=='AMPH-water-slope')
    return number(value,8), f'[original slope](../{source.relative_to(HERE.parent).as_posix()})'


def link(name, field=None):
    label = name.rsplit('/',1)[-1]
    return (f'[{label}](results/{name})' + (f' · `{field}`' if field else '')) if (RESULTS/name).is_file() else '—'


def number(value, digits=6):
    return f'{value:.{digits}g}' if value is not None else '—'


def table(header, rows):
    return '\n'.join(['| '+' | '.join(header)+' |', '| '+' | '.join(['---']*len(header))+' |',
                      *['| '+' | '.join(str(v) for v in row)+' |' for row in rows]])


def amp():
    yield '## A. AMP pressure calibration and phase behavior'
    phase_file = 'A/phase-controls.json.gz'
    phases = load(phase_file)
    records = []
    for design, endpoint, label in [('original','main','free'),('original','slope-150','fixed'),
                                    ('expanded','free','free'),('expanded','fixed','fixed')]:
        p = f'A/{design}-{endpoint}.json.gz'
        value = load(p)
        if value is None:
            continue
        if design == 'original':
            slope, slope_link = ('−150',link(p)) if label == 'fixed' else original_slope()
            desc = len(phases['original_free']['descents']) if label == 'free' else phases['original_fixed']['descent']
            count = len(phases['original_free']['confirmed']) if label == 'free' else sum(phases['original_fixed'].get('liquid_liquid_splits',{}).values())
            with gzip.open(AMP_ORIGINAL/endpoint/'search-1.json.gz','rt') as stream:
                original_search = json.load(stream)
            completed = sum(bool(r['completed']) for r in original_search)
            records.append((design,label,slope,number(value['cost'],10),'retained original',
                            f"{completed} / {len(original_search)}",desc,count,
                            ' · '.join(dict.fromkeys((link(p),link(phase_file),slope_link)))))
        else:
            for protocol in ('native','supplied'):
                sha_record = f'A/search-{label}-{protocol}-full.json.gz'
                search = load(sha_record) or {}
                tally = search.get('tally', {})
                confirmed = search.get('classification', {}).get('confirmed')
                records.append((design,label,number(value['slope_K'],8),number(value['cost'],10),protocol,
                                f"{search.get('completed','—')} / {search.get('attempted','—')}",
                                tally.get('descent','—'),len(confirmed) if confirmed is not None else '—',link(p)+' · '+link(sha_record)))
    yield table(('Data design','Slope family','Slope (K)','Objective','Phase search','Completed / attempted',
                 'Descents','Confirmed LL','Retained records'), records)
    yield ('The added pressure rows enter the fit. The five zero-loading Tong rows and the Kundu partial pressures remain comparisons. '
           f'The original fitted-residual replay and the row-level changes are retained in {link("A/crosswalk.json.gz","rows")}.')
    p = 'A/crosswalk.json.gz'
    if data := load(p):
        old = [r for r in data['rows'] if r['group']=='loaded-pressure']
        added = [r for r in data['rows'] if r['old_role']!='fitted' and r['new_role']=='fitted']
        yield (f"The loaded-pressure block grows from {len(old)} to {len(old)+len(added)} observations. "
               f"The coefficient multiplying each squared log-pressure residual in twice the objective changes from "
               f"{number(old[0]['old_weight'])} to {number(old[0]['new_weight'])}. {link(p,'rows')}")
    observables = []
    for endpoint in ('original-main','original-slope-150','expanded-free','expanded-fixed'):
        p = f'A/{endpoint}.json.gz'
        result = load(p)
        if not result:
            continue
        design = endpoint.split('-',1)[0]
        for r in result[design]['scores']:
            if r['T_K'] is None:
                observables.append((endpoint,r['group'],r['kind'],r['role'],r['total'],number(r.get('AARD_percent')),
                                    number(r.get('bias_percent')),number(r.get('mean_abs_error')),r['unit'],link(p,f'{design}.scores')))
    yield table(('Endpoint','Source block','Observable','Role','Rows','AARD (%)','Signed bias (%)','Mean absolute error','Unit','Retained record'),observables)
    p = 'A/common-pressure.json.gz'
    result = load(p)
    if result:
        yield f"At S14 the four bubble references set a common pressure of {number(result['common_Pa'],10)} Pa. {link(p,'common_Pa')}"
        rows = []
        for k,v in result['outcomes'].items():
            best = next((a for a in v.get('attempts',[]) if a['confirmed']), {})
            minima = v.get('minimum_by_density_side',{})
            rows.append((k,number(result['bubbles'][k]['pressure_Pa'],9),number(result['margins_Pa'][k],9),
                         number(minima.get('1')),number(minima.get('2')),
                         number(best.get('Gibbs_decrease_over_RT_mol')),number(best.get('numerical_error_over_RT_mol')),link(p,f'outcomes.{k}')))
        yield table(('Endpoint','Bubble pressure (Pa)','Margin (Pa)','Vapor TPD/RT','Liquid TPD/RT',
                     'Gibbs decrease / RT (mol)','Paired error (mol)','Retained record'),rows)
    profile_rows = []
    for design in ('original','expanded'):
        p = f'A/profile-{design}.json'
        if result := load(p):
            brackets = ', '.join(f"{side}: {number(b['within'])} to {number(b['beyond'])}" for side,b in result['brackets'].items())
            profile_rows.append((design,number(result['stage_variance']),number(result['delta_cutoff']),brackets or 'open',link(p)))
    if profile_rows:
        yield table(('Data design','Stage variance','Nominal ΔC cutoff','Slope brackets (K)','Retained record'),profile_rows)
        yield 'The thresholds describe the declared weighted objectives. Correlated observations and heuristic weights limit statistical interpretation.'


def reactions():
    yield '## B. Aqueous reference convention'
    p = 'B/reactions.json.gz'
    data = load(p)
    if not data:
        yield 'The three paired reference-convention calculations are pending.'
        return
    rows = []
    for r in data['rows']:
        for label,v in r['conventions'].items():
            pair = next((a for a in v.get('attempts',[]) if a['confirmed']),next(iter(v.get('attempts',[])),{}))
            closure = next((q for q in v['pair_readback'] if q), {})
            transfer = max(map(abs, closure.get('charge_neutral_transfers', [])), default=None)
            rows.append((r['key'], label, number(r['P_Pa'],10),number(pair.get('Gibbs_decrease_over_RT_mol')),
                         number(pair.get('numerical_error_over_RT_mol')),number(transfer),r['phase_disposition'],
                         link(p,f"{r['key']}.{label}")))
    yield table(('Feed','Reference','System P (Pa)','Gibbs decrease / RT (mol)','Paired error (mol)',
                 'Largest neutral transfer / RT','Pair disposition','Retained record'),rows)
    yield ('Each convention uses one composition-independent species-standard vector at fixed temperature and system pressure. '
           'The empirical reaction law supplies its temperature dependence. Any dependence of the completed vector on pressure comes '
           'through the fugacity reference conversion. The retained volume and enthalpy derivatives apply to the added standard vector. '
           'The reported EOS volume and calorics exclude that additional term. '
           f'The highest-pressure state is extreme extrapolation. {link(p,"rows")}')
    p_supports = 'B/MDEA-supports.json.gz'
    if supports := load(p_supports):
        rows = []
        for i, row in enumerate(supports['rows']):
            for candidate in row.get('candidates') or [{}]:
                misses = [label for field, label in (('physical_checks_pass','physical closure'),
                                                     ('root_checks_pass','pressure-root readback'))
                          if candidate.get(field) is False]
                message = ', '.join(misses) or candidate.get('message','—').split(';',1)[0]
                rows.append((number(row['T_K']), number(row['P_Pa'],10), row['reference_convention'],
                             candidate.get('support','—'), number(candidate.get('pressure_Pa'),10),
                             'yes' if candidate.get('qualified') else 'no', number(candidate.get('Gibbs_over_RT_mol'),10),
                             row.get('support_refusal', message), link(p_supports,f'rows[{i}]')))
        yield table(('MDEA T (K)','System P (Pa)','Reference','Support','Candidate P (Pa)','Qualified in search',
                     'Gibbs / RT (mol)','Check missed or solver message','Retained record'),rows)
        yield ('The L+V searches use the reevaluated liquid parent and the default vapor initialization. '
               'The two-liquid candidates use the archived pair seeds. The incipient vapor calculation solves '
               'for pressure separately and is excluded from the fixed-pressure Gibbs comparison.')
    derivatives = []
    for i,r in enumerate(data['rows']):
        for label,v in r['conventions'].items():
            if estimates := v.get('derivative_estimates'):
                estimate = estimates[-1]
                derivatives.append((i+1,label,number(estimate.get('volume_m3',[None])[0]),
                                    number(estimate.get('enthalpy_J',[None])[0]),link(p,f'rows[{i}].conventions.{label}.derivative_estimates')))
    yield table(('Feed in order above','Reference','Parent standard V (m³)','Parent standard H (J)','Retained record'),derivatives)


def objective():
    yield '## C. Objective contributions and weights'
    p = 'C/reported-objectives.json'
    result = load(p)
    if result:
        yield table(('Reported model','C','Interior rank','All-row variance','Stage variance','Retained record'),
                    [(k,number(v['objective'],10),v['rank'],number(v['all_variance'],9),number(v['stage_variance'],9),link(p,f'models.{k}'))
                     for k,v in result['models'].items()])
        yield table(('Reported model','Observable','Rows','Objective contribution','Weight sum','Retained record'),
                    [(model,k,g['count'],number(g['cost'],8),number(g['weight_sum'],8),link(p,f'models.{model}.groups.{k}'))
                     for model,v in result['models'].items() for k,g in v['groups'].items()])
        yield table(('Conditional MEA k','Objective','Increase','Nominal cutoff','Retained record'),
                    [(number(r['k'],9),number(r['cost'],10),number(r['increase'],8),number(result['MEA_delta_cutoff'],8),
                      link(p,f'MEA_profile[{i}]')) for i,r in enumerate(result['MEA_profile'])])
    p = 'C/MEA-k-profile.json.gz'
    if data := load(p):
        yield table(('MEA fixed k','Replayed objective','Retained objective','Increase','Retained record'),
                    [(number(r['k'],9),number(r['replay_cost'],10),number(r['retained_cost'],10),
                      number(r.get('increase_from_center'),8),link(p,f'rows[{i}]')) for i,r in enumerate(data['rows'])])
        lower = sorted((r for r in data['rows'] if r['k'] < data['rows'][0]['k'] and r['available']),key=lambda r:r['k'])
        bracket = next(((a,b) for a,b in zip(lower,lower[1:]) if
                        a['increase_from_center']>data['delta_cutoff']>=b['increase_from_center']),None)
        if bracket:
            yield (f"The retained lower MEA crossing lies between {number(bracket[0]['k'])} and "
                   f"{number(bracket[1]['k'])}. The scan approaches the upper bound with no crossing. {link(p,'rows')}")
    profiles = []
    for label in ('low','reported','high'):
        p = f'C/MDEA-k-{label}.json.gz'
        if data := load(p):
            profiles.append((number(data['k'],9),number(data['information']['objective'],10),link(p,'information')))
    if profiles:
        yield table(('Fixed MDEA k','Objective','Retained record'),profiles)
    yield ('The profile thresholds are nominal objective-scale sensitivities for the declared weights. '
           'The MDEA fixed-k contrasts have no unrestricted MDEA minimum in this comparison.')
    comparisons = []
    for path in sorted((RESULTS/'C').glob('*assessment*')):
        name = path.relative_to(RESULTS).as_posix()
        data = load(name)
        if default := data.get('default', data.get('information')):
            phase = data.get('Q3', [data['S14']] if 'S14' in data else [])
            pairs = sum(any(a['confirmed'] for a in state.get('attempts', [])) for state in phase)
            comparisons.append((path.name.split('-assessment')[0],number(default['objective'],10),
                                number(data.get('alternative',{}).get('objective'),10),default['rank'],
                                ', '.join(default['active_bounds']) or 'none',f'{pairs} / {len(phase)}',link(name)))
    if comparisons:
        yield table(('Candidate','Default metric','Normalized metric','Interior rank','Active bounds',
                     'Feeds with confirmed LL','Retained record'),comparisons)
    p_refit = 'C/normalized-MDEA-1.json.gz'
    data = load(p_refit)
    if data and data['report'] and (end := data['report'].get('endpoint_replay_cost')) is not None:
        initial = data['records']['start-replay.json']['cost']
        yield (f"The fixed k=0.765 MDEA fit reduced the normalized objective from {number(initial,12)} "
               f"to {number(end,12)}. {link(p_refit,'report')}")
        p_assessment = 'C/normalized-MDEA-1-refit-assessment.json.gz'
        if assessment := load(p_assessment):
            yield table(('MDEA T (K)','System P (Pa)','Q3 search','Confirmed LL','Retained record'),
                        [(number(r.get('T_K')),number(r.get('P_Pa'),10),r.get('instability',r.get('refusal')),
                          'yes' if any(a['confirmed'] for a in r.get('attempts',[])) else 'no',
                          link(p_assessment,f'Q3[{i}]')) for i,r in enumerate(assessment['Q3'])])
    stopped = []
    for candidate in ('MDEA-0','MDEA-1'):
        p = f'C/normalized-{candidate}-time-stop.json.gz'
        if data := load(p):
            records = data['records']
            stages = sorted(records.items())
            replayed = [r for k,r in stages if k.endswith('/fit.json')]
            optimizer = [r for k,r in stages if k.endswith(('/fit.json','/fit-native.json'))]
            end = optimizer[-1] if optimizer else {}
            stopped.append((candidate,number(records.get('start-replay.json',{}).get('cost'),10),
                            number(end.get('data_cost',end.get('final_cost')),10),
                            number(replayed[-1].get('endpoint_replay_cost') if replayed else None,10),
                            end.get('status','No endpoint returned'),
                            number(data['alternative_process_wall_seconds']/60),link(p)))
    if stopped:
        yield table(('Stopped run','Starting normalized objective','Last native objective',
                     'Last replayed normalized objective','Last optimizer status',
                     'Fit-process minutes at stop','Retained record'),stopped)
    p = 'C/partial-pressures.json.gz'
    if data := load(p):
        yield table(('MDEA endpoint','Available rows','Combined AARD (%)','Combined signed bias (%)','Retained record'),
                    [(k,v['combined']['rows'],number(v['combined']['AARD_percent']),number(v['combined']['bias_percent']),link(p,f'endpoints.{k}'))
                     for k,v in data['endpoints'].items()])


def curvature():
    yield '## D. Composition curvature and hot extension'
    p = 'D/S14-hessian.json'
    if data := load(p):
        yield table(('S14 liquid phase','Minimum generalized eigenvalue','Difference from #433','Retained record'),
                    [(label,number(r['minimum'],9),number(r['difference']),link(p,f'phases[{i}]'))
                     for i,(label,r) in enumerate(zip(('parent','daughter 1','daughter 2'),data['phases'],strict=True))])
    rows = []
    for path in sorted((RESULTS/'D').glob('*.json.gz')):
        name = path.relative_to(RESULTS).as_posix()
        record = load(name)
        for r in record.get('summary',[]):
            rows.append((path.name.removesuffix('.json.gz'), r['kind'],r['count'],r['sign_counts']['positive'],r['sign_counts']['negative'],
                         r['sign_counts']['undecided'],r['refused'],number(r['minimum']),link(name,'summary')))
    if rows:
        yield table(('Fit','State type','States','Analytic positive','Analytic negative','Analytic undecided',
                     'Unavailable','Analytic minimum','Retained record'),rows)
    p = 'D/MDEA-unbounded-near-zero.json'
    check = load(p)
    if check and min(check['extrapolated_projected_mu_curvature'][-4:]) < 0 < max(check['extrapolated_projected_mu_curvature'][-4:]):
        signs = next(r for r in load('D/MDEA-unbounded.json.gz')['summary'] if r['kind']=='unloaded or binary')
        yield (f"The independent directional readback for fit:502 at {number(check['T_K'])} K changes sign at the finest steps. "
               f"With that state undecided, the {signs['count']} unbounded MDEA binary states include "
               f"{signs['sign_counts']['positive']-1} positive, {signs['sign_counts']['undecided']+1} undecided "
               f"and {signs['refused']} unavailable. The analytic minimum remains "
               f"{number(check['hessian']['minimum'],3)}. {link(p,'extrapolated_projected_mu_curvature')}")
    p = 'D/hot-paths.json.gz'
    if data := load(p):
        states = [r for path in data['paths'] for r in path['rows']]
        computed = [r['curvature']['minimum'] for r in states if 'curvature' in r]
        yield table(('Paths retained','States sampled','Liquid descents','Vapor descents','Negative eigenvalues',
                     'Lowest eigenvalue','Refusals','Retained record'),
                    [(f"{len(data['paths'])} / {data['planned_paths']}",len(states),sum(r.get('liquid') is True for r in states),
                      sum(r.get('vapor') is True for r in states),sum(r.get('negative') is True for r in states),
                      number(min(computed,default=None)),sum('refusal' in r or 'curvature_refusal' in r for r in states),link(p,'paths'))])
        if states and all(r.get('liquid') is False and r.get('vapor') is False and r.get('negative') is False for r in states):
            yield f"The finite grid supplies a sampled bound through {number(max(r['T_K'] for r in states))} K. {link(p,'temperature_grid_K')}"
    p = 'D/overlap.json.gz'
    if data := load(p):
        rows = data['rows']
        yield (f"The extended declaration replayed {len(rows)} original grid paths and temperatures. "
               f"Pressure and stability differences are retained per state. {link(p,'rows')}")
    yield ('Negative curvature is evidence of local instability of the model liquid. Positive curvature can coexist with a lower tangent at a distant composition. '
           'The calculations test properties of the model and supply no observation of physical demixing.')


def molecular():
    yield '## E. Molecular geometry, pure properties and association'
    p = 'E/pure-properties.json'
    if data := load(p):
        yield table(('Source','Predicted / measured','Mean abs. relative error (%)','Signed bias (%)','Retained record'),
                    [(k,f"{v.get('rows',0)} / {v['total']}",number(v.get('AARD_percent')),number(v.get('bias_percent')),link(p,f'summary.{k}'))
                     for k,v in data['summary'].items()])
    p = 'E/cation-geometry.json'
    if data := load(p):
        yield (f"The chain has {number(data['m'])} segments and a {number(data['sigma_A'])} Å segment diameter. The spherical segment "
               f"diameter is {number(data['spherical_sigma_A'])} Å at the same $m\\sigma^3$. {link(p)}")
    candidates = []
    for label in ('chain','sphere'):
        for when in ('before','after'):
            p = f'E/cation-{label}-{when}.json.gz'
            if data := load(p):
                info = data.get('information', {})
                q3 = data.get('Q3',[])
                candidates.append((label,when,number(info.get('objective'),10),info.get('rank','—'),
                                   ', '.join(info.get('active_bounds',[])) or 'none',
                                   sum(any(a['confirmed'] for a in r.get('attempts',[])) for r in q3),link(p)))
    if candidates:
        yield table(('MDEAH⁺ geometry','Refit','Objective','Interior rank','Active bounds','Q3 confirmed LL','Retained record'),candidates)
        yield 'The geometry contrast holds the electrostatic diameters and association topology fixed. The remaining fits compare EOS parameterizations for the declared measurements.'
    p = 'E/cation-optimizer-sample.json'
    if load(p):
        yield f"A bounded CPU sample of the spherical fit identifies the native derivative sweeps. {link(p)}"
    rows = []
    p = 'E/DEA-combining-rule.json.gz'
    q = 'E/DEA-explicit-1-control.json'
    baseline, control = load(p), load(q)
    if baseline and control:
        observed = next(r for r in baseline['binary_rows'] if r['group']=='Horstmann heat' and r['x']==0.6414)
        rows.append(('combining rule',number(control.get('combining_a')),number(control.get('combining_b_K')),
                     number(control['combining_binary']),number(observed.get('predicted')),
                     number(baseline['binary_scores']['Horstmann VLE / fitted'].get('aard')),
                     number(baseline['binary_scores']['Cai VLE / fitted'].get('aard')),
                     number(control['combining_reactive']),link(p)+' · '+link(q)))
    for multiplier in ('1','1.05','1.1','1.15'):
        p = f'E/DEA-association-{multiplier}-binary.json.gz'
        q = f'E/DEA-association-{multiplier}-reactive.json.gz'
        if binary := load(p):
            reactive = (load(q) or {}).get('chosen')
            row = next(r for r in binary['postfit'] if r['group']=='Horstmann heat' and r['x']==0.6414)
            scores = binary['after_scores']
            rows.append((multiplier,number(binary['a']),number(binary['b_K']),number(binary['optimizer'].get('fun')),
                         number(row.get('predicted')),number(scores['Horstmann VLE / fitted'].get('aard')),
                         number(scores['Cai VLE / fitted'].get('aard')),
                         number(reactive['report']['endpoint_replay_cost'] if reactive else None),link(p)+' · '+link(q)))
    if rows:
        yield table(('Unlike energy multiplier','k at 365.15 K','Slope (K)','Binary objective','Hᴱ at xw=0.6414 (J/mol)',
                     'Horstmann pressure AARD (%)','Cai pressure AARD (%)','Reactive objective','Retained records'),rows)
        if control:
            yield (f"The combining-rule and explicit-edge control have the same association term at the frozen-volume state. "
                   f"The temperature dependence of the combining-rule volume still changes predicted enthalpy. {link('E/DEA-explicit-1-control.json')}")


def generate():
    yield '# Round 5 manuscript handoff'
    yield ('These calculations compare declared EOS fits, pressure and composition paths, and observation groups. Numerical agreement and phase searches '
           'apply to the checks and supports recorded for each case. Results are for investigator review.')
    for group in (amp,reactions,objective,curvature,molecular):
        yield from group()
    yield '## Wall time'
    operations = {'A':(18,35,['A/calibration.json','A/phase-timing.json','A/profile-original.json','A/profile-expanded.json']),
                  'B':(1,4,['B/reactions.json.gz','B/MDEA-supports.json.gz']),
                  'C':(8,14,['C/reported-objectives.json','C/partial-pressures.json.gz','C/cross-start-timing.json','C/normalized-timing.json','C/MEA-k-profile.json.gz']),
                  'D':(6,18,['D/fitted-timing.json','D/hot-paths.json.gz','D/overlap.json.gz']),
                  'E':(6,17,['E/cation-timing.json','E/pure-properties.json','E/DEA-association-timing.json'])}
    time_rows = []
    for group,(low,high,names) in operations.items():
        ran = [(name,read['seconds']) for name in names if (read:=load(name)) and 'seconds' in read]
        elapsed = sum(seconds for _,seconds in ran)/60 if ran else None
        evidence = ' · '.join(f'{link(name)} {seconds/60:.2f} min' for name,seconds in ran)
        runtime = 'C/group-runtime.json'
        if group=='C' and (data := load(runtime)):
            elapsed = data['seconds']/60
            evidence += ' · '+link(runtime)
        time_rows.append((group, f'{low}–{high}', number(elapsed),evidence))
    yield ('Measured wall times sum the listed operations, with the continuous timed interval used for Group C. '
           'Several operations ran concurrently.')
    yield table(('Group','Projected minutes','Recorded minutes','Operation records'),time_rows)
    p = 'C/normalized-MDEA-1-timing.json'
    if rerun := load(p):
        yield (f"The isolated four-worker MDEA k=0.765 rerun took {number(rerun['seconds'],5)} s "
               f"including both metric replays and the Q3 checks. The separate diagnostic profile attributed "
               f"84% of sampled CPU stacks to automatic differentiation and 33% to saturation-loading searches. "
               f"The profiled fit took about ten times the wall time of the ordinary MDEA fit. "
               f"Engine #214 tracks reuse in the saturation-loading search. {link(p)} · "
               "[Engine #214](https://github.com/tannerpolley/epcsaft/issues/214)")
    yield '## Reconciled records and open items'
    p = 'records/Hilliard-Cp.json'
    if data := load(p):
        roles = data['current_broad_roles']
        yield (f"The Hilliard heat-capacity comparison contains {roles['fitted']} fitted "
               f"and {roles['outside']} outside-fit observations. {link(p,'current_broad_roles')}")
    p = 'records/S8-pressure-bands.json'
    if data := load(p):
        yield table(('Outside-fit band','Rows','AARD (%)','Signed bias (%)','Printed AARD (%)','Retained record'),
                    [(name,r['statistics']['rows'],number(r['statistics']['AARD_percent'],13),
                      number(r['statistics']['bias_percent'],10),r['displayed_AARD'],link(p,f'bands.{name}'))
                     for name,r in data['bands'].items()])
    p = 'records/MDEA-coverage.json.gz'
    if data := load(p):
        yield table(('MDEA state record tier','Stage','Incomplete records','Retained record'),
                    [(r['tier'],r['stage'],r['count'],link(p,f'groups[{i}]')) for i,r in enumerate(data['groups'])])
        q8 = data['Q8']
        yield (f"Q8 reached distinct phases at {q8['states_with_converged_distinct']} of "
               f"{q8['attempted_states']} attempted feeds. The confirmed two-liquid count is "
               f"{q8['confirmed_two_liquid']}. {link(p,'Q8')}")
    p = 'records/pH-carbonate.json'
    if data := load(p):
        yield table(('Jakobsen observation','Measured fraction','Calculated fraction','Required pH shift',
                     'Electrode pH shift','pH-adjusted fraction','Retained record'),
                    [(r['identity'],number(r['observed']),number(r['carbonate_pool_split']),number(r['required_pH_shift']),
                      number((r['electrode_match'] or {}).get('delta_pH')),number((r['electrode_match'] or {}).get('corrected_pool_fraction')),
                      link(p,f'rows[{i}]')) for i,r in enumerate(data['rows'])])
    p = 'records/AMP-public-trials.json.gz'
    if data := load(p):
        counts = data['native_supplied_overlap']
        yield table(('Original AMP search outcome','States','Retained record'),
                    [(name,n,link(p,'native_supplied_overlap')) for name,n in counts.items()])
    reconciliation = {
        'Kuranov-R2.json':'Temperature and observation identities for Kuranov rows 72 and 28',
        'Hilliard-Cp.json':'Hilliard broad and fitted heat capacity identities and their intersection',
        'S8-pressure-bands.json':'Outside-fit absorber and stripper partial-pressure bands',
        'MDEA-coverage.json.gz':'Stage-keyed MDEA coverage, property pressure deficits and Q8 root classifications',
        'AMP-native-starts.json.gz':'Original AMP classification and unavailable pressures',
        'AMP-public-trials.json.gz':'AMP replay by publicly returned trial identity',
        'pH-carbonate.json':'Carbonate odds and matched electrode offsets',
        'public-1.3.2.json':'Reference-state numerical and rounding checks on the isolated public distribution',
        'study-wheel-S13-controls.json':'Corresponding checks on the pinned study wheel',
        'open-items.json':'Numerical misses, unavailable evidence and remaining checks',
    }
    for name, description in reconciliation.items():
        if (RESULTS/'records'/name).is_file():
            yield f"- {description}. {link('records/'+name)}"


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--check',action='store_true')
    args = parser.parse_args()
    path = HERE/'manuscript-handoff.md'
    content = '\n\n'.join(generate())+'\n'
    if args.check:
        if path.read_text() != content:
            raise SystemExit(f'{path} is stale')
    else:
        path.write_text(content)
