"""Present retained fit, derivative and phase comparisons as an analysis notebook."""
from collections import Counter
import gzip
import json
from pathlib import Path


def show(value):
    if value is None:
        return '—'
    if isinstance(value,float):
        return f'{value:.8g}'
    return str(value)


def mdea_slope_bound():
    results = Path(__file__).parent/'results/MDEA_slope_bound'
    if not (results/'checks.json.gz').exists():
        return []
    def read(name):
        return json.loads(gzip.decompress((results/name).read_bytes()))
    checks, declaration = read('checks.json.gz')['checks'], read('declaration.json.gz')
    slope = next(q['bounds'] for q in declaration['point']['coordinates']
                 if q['identity'] == 'pair/mdea-water/k_ij/a1 / temperature_law_coefficient')
    pressure = f"{declaration['pressure_Pa']/1e6:g} MPa"

    def wheel(_):
        return [f"Stage 0 used the study wheel with the reaction reference fixed at "
                f"{declaration['reaction_reference_pressure_Pa']/1e3:g} kPa.",
                f"The lower slope bound is {slope[0]:.10g} K⁻¹. The upper slope bound is {slope[1]:g} K⁻¹."]

    def replay(q):
        return [f"A replays all {q['rows']} predictions at cost {q['cost']:.17g}, with maximum relative prediction "
                f"and conditional standard-error differences of {q['max_relative_prediction_difference']:.3g} and "
                f"{q['max_relative_conditional_se_difference']:.3g}. Only the upper bound on $a_0$ is active."]

    def onset(q):
        cold = q['cold_onset']
        return [f"At {cold['T_K']} K and {pressure}, the binary liquid hull brackets gap onset between "
                f"{cold['k_no_gap']:.10g} and {cold['k_gap']:.10g}. At the $(U,s)$ corner, "
                f"$k={q['corner_k']:.10g}$ is {q['corner_margin']:.6g} below the no-gap end of the bracket."]

    def hull(q):
        left, right = q['known_answer']['gaps'][0]['x_MDEA_contacts']
        return [f"The four corners had {q['gaps']} gaps in {q['corner_states']} temperature–corner checks "
                f"on the {declaration['compositions']:,}-point composition grid. The LHS-53 control had a gap with "
                f"MDEA mole-fraction contacts {left:.4g} and {right:.4g}. These are finite-grid model checks."]

    def census(q):
        counts = ', '.join(f'{group} {count}' for group, count in sorted(q['by_family'].items()))
        return [f"{q['can_start']} of {q['candidates']} draws had every row available. "
                f"The census recorded {q['available_rows']} available and {q['unavailable_rows']} unavailable "
                f"rows ({counts}). All MDEA–water bubble rows were available. The census records Engine responses "
                'at the declared vectors.']

    lines = ['', '## MDEA–water slope bound (#427)', '']
    # A failed check is labelled in place; the checks before it keep their reported values.
    for number, paragraph in enumerate((wheel, replay, onset, hull, census), 1):
        check = checks.get(str(number))
        if check is None:
            lines += [f'Check {number} was not run because an earlier check did not pass.', '']
        elif not check['passed']:
            lines += [f'Check {number} did not pass. Its values are in the '
                      '[retained checks](results/MDEA_slope_bound/checks.json.gz).', '']
        else:
            lines += [*paragraph(check), '']
    return [*lines,
            'The approved two-wheel exception applies to the #427 candidate checks, fits and descent probes. '
            'Endpoint values are reported on the study wheel. The fit comparison awaits the second wheel. '
            '[Accepted plan](https://github.com/tannerpolley/Amine-Thermodynamics/issues/427#issuecomment-7178782607).',
            '',
            '[Declaration](results/MDEA_slope_bound/declaration.json.gz) · '
            '[A replay](results/MDEA_slope_bound/replay-A.json.gz) · '
            '[Onsets](results/MDEA_slope_bound/onset-S.json) · [Hulls](results/MDEA_slope_bound/hull-S.json) · '
            '[Row census](results/MDEA_slope_bound/census-S.json.gz) · '
            '[Checks and message counts](results/MDEA_slope_bound/checks.json.gz).',
            '',
            'Run `taskset -c 0-7 uv run --locked python analyses/fixed_reaction_reference/diagnosis-starts/stage0.py` '
            'from the repository root to repeat Stage 0. Add `--check` to recompute the checks from the retained records.', '']


def stage1_phases(quantities):
    if 'Stage 1 MEA measured' not in quantities:
        return []
    lines = ['', '## Rebuilt phase searches (#441)', '',
             '| Stratum | No descent | Two liquids | Liquid plus vapor-connected phase | Open Engine item | Blocked |',
             '|---|---:|---:|---:|---:|---:|']
    classes = ('no descent in the finite search','two liquids of lower Gibbs energy',
               'liquid plus a vapor-connected phase of lower Gibbs energy','open Engine item')
    for name,item in quantities.items():
        if name.startswith('Stage 1 ') and 'counts' in item['new']:
            counts = item['new']['counts']
            cells = [name.removeprefix('Stage 1 '),*[str(counts.get(k,0)) for k in classes],str(len(item['new']['blockers']))]
            lines.append('| '+' | '.join(cells)+' |')
    lines.extend(['','| Screen stratum | Distinct parents read | Pressure misses | Reclosed | Recovered by restart | Still missing |',
                  '|---|---:|---:|---:|---:|---:|'])
    density_gap = 0.
    for item in quantities.values():
        if isinstance(item['new'],dict):
            for name,value in item['new'].get('pressure_closure',{}).items():
                fields = ('parents_read','misses','reclosure','restart','still_missing')
                lines.append('| '+' | '.join([name,*(str(value.get(k,0)) for k in fields)])+' |')
                density_gap = max(density_gap,value.get('max_native_density_relative_difference',0.))
    lines.extend(['',f'The native stability test consumes the Engine equilibrium result. In these replays the largest '
                  f'relative molar-density difference from the independently reclosed parent was {density_gap:.3g}.'])
    blockers = [(name,key,v) for name,item in quantities.items() if name.startswith('Stage 1 ')
                for key,v in item['new'].get('blockers',{}).items()]
    if blockers:
        lines.extend(['','Pressure-closure blockers by stratum, including equivalent calculation keys.',''])
        for name,key,value in blockers:
            lines.append(f"- {name}. `{key}`. {value['diagnosis']}. See `results/{value['record']}`.")
    diagnosis = quantities['Stage 1 pressure closure diagnosis']['new']
    lines.extend(['','The pressure scans evaluated 401 consecutive densities around each Newton density '
                  'at the original and restarted compositions. Repeated reads and the derived-property '
                  'route agreed at the sampled densities.',
                  '', '| Parent | Minimum relative error magnitude, original / restart | Relative step per density ULP | RMS scatter, original / restart |',
                  '|---|---:|---:|---:|'])
    for key,scans in diagnosis.items():
        before,after = (scans[k] for k in ('initial_parent','parent'))
        lines.append(f"| `{key.replace('|', '&#124;')}` | {before['best_abs_relative_pressure_error']:.3g} / "
                     f"{after['best_abs_relative_pressure_error']:.3g} | {before['analytic_step_per_ULP']:.3g} | "
                     f"{before['local_fit_scatter_RMS']:.3g} / {after['local_fit_scatter_RMS']:.3g} |")
    lines.extend(['','For the MEA census-grid, Cai and Kundu parents, adjacent densities bracket the target '
                  'pressure and the closest scan points still miss the pressure limit. For Hartono, the '
                  'original search window contains a qualifying density. None of the declared reactions are '
                  'on that liquid support. Reclosure gave a relative pressure residual of −1.60e−11 '
                  'and both trial protocols completed without descent.'])
    lines.extend(['','The 321 measured MEA searches comprise 307 liquid and 14 liquid–vapor parents. '
                  'The qualified DEA pairs cover five Weiland feeds and the Lawson and Garst composition at '
                  '7.97232 kPa, which is 1.05 times the model bubble pressure. The searches use the declared models.',
                  '', '| AMP fit | Control | Imposed pressure (kPa) | Model bubble (kPa) | Gibbs decrease / RT (mol) | Paired error (mol) |',
                  '|---|---|---:|---:|---:|---:|'])
    for design in ('AMP_free','AMP_fixed'):
        for key,q in quantities[f'Stage 1 {design} controls']['new']['bubble_comparisons'].items():
            lines.append(f"| {design} | {key} | {q['imposed_Pa']/1000:.6g} | {q['bubble_Pa']/1000:.6g} | "
                         f"{q['decrease']:.6g} | {q['error']:.3g} |")
    lines.extend(['','Both historical MDEA targets at 383.15 K, 121.309 MPa and loading 1.368 '
                  'completed the declared finite search with zero descents. The continued vapor amount reached zero '
                  'along each parameter and reference-pressure path. The AMP bubble solves are model predictions on '
                  'the same feeds as their pressure controls. The three searches tied to '
                  '[Engine #265](https://github.com/tannerpolley/epcsaft/issues/265) remain open.',
                  'The support census matched every prior support set, so it triggered no screen reruns.'])
    return lines


def render(result):
    q = result['quantities']
    lines = [r"""---
title: Reaction standard-state pressure fixed at 100 kPa
resources:
  - manuscript-handoff.json
  - results/handoff-checks.json
  - results/stages.json
  - results/MDEA_slope_bound/*
---

The study compares three calculations on Engine commit `05e94210`.
The tracking model uses the retained coefficients. The 100 kPa control
changes the reaction reference with those coefficients held fixed. The
refit varies the designated coordinates with the same residual definitions
and external observation pressures. DEA and AMP also take the selected MEA
donor before refitting.

Each design uses an incumbent and two displaced starts from a 64-point
Latin hypercube with seed 427. The distances are root mean square differences
on the unit coordinate box. A relative objective tie favors the incumbent.
The selected fit is a local result. The calibration residuals, the
comparison against measurements, and the model's finite phase searches have
different meanings. Conditional standard errors describe the declared fit
and active bounds. The study awaits independent evidence review and
investigator promotion for manuscript use.

[Quantity index](manuscript-handoff.json) records contributor hashes, pressure
and population basis, and open quantities.

## Fitted objectives

| Design | Fitted rows | Tracking | Fixed at old parameters | Fixed and refitted | Change from tracking | Selection |
|---|---:|---:|---:|---:|---:|---|"""]
    for design,attempts in result['fit_attempts'].items():
        old = q[f'{design} objective at old parameters']
        new = q[f'{design} selected objective']
        selected = result['selected_starts'][design]
        label = f'{selected} provisional' if selected and new['disposition']=='undecided' else selected
        lines.append('| '+' | '.join(map(show,(design,old['population']['fitted'],old['old'],old['new'],
                                              new['new'],new['absolute_change'],label)))+' |')
    lines.extend(mdea_slope_bound())
    lines.extend(stage1_phases(q))
    lines.extend(['','## Start separation and endpoint stationarity','',
                  '| Design | A−B | A−C | B−C |','|---|---:|---:|---:|'])
    for design in result['fit_attempts']:
        distances = q[f'{design} start distances']['new']
        lines.append('| '+' | '.join(map(show,(design,*distances.values())))+' |')
    lines.extend(['','The first gradient uses the bound-normalized coordinate widths and zeros outward components '
                  'within $10^{-6}$ optimizer units of a bound. The Engine gradient uses optimizer coordinates and '
                  'the displacement $u-\\operatorname{clip}(u-J^\\mathsf{T}r,l,h)$. The pinned Engine computes it '
                  'in `engine/native/regression/fit.cpp` at commit `05e94210`. The inherited gradient tolerance '
                  'is $10^{-8}$ in these optimizer coordinates. Ceres can also stop on its function or parameter tolerance. '
                  'A replayed objective and a Ceres convergence report are shown separately from the gradient check.',
                  '','| Design | Start (LHS draw) | Status | Initial objective | Replayed objective | Bound gradient ∞-norm | Optimizer gradient ∞-norm | Gradient check | Fit / replay (s) |',
                  '|---|---|---|---:|---:|---:|---:|---|---:|'])
    for design,attempts in result['fit_attempts'].items():
        for label,row in attempts.items():
            draw = f" ({row['draw']})" if row['draw'] is not None else ''
            gradient = 'pass' if row['stationarity_met'] else 'miss' if row['stationarity_met'] is not None else '—'
            lines.append('| '+' | '.join(map(show,(design,label+draw,row['status'],row['initial_cost'],row['objective'],
                row['projected_gradient_inf'],row['solver_scale_projected_gradient_inf'],gradient,
                f"{show(row['fit_seconds'])} / {show(row['replay_seconds'])}")))+' |')
    for design,attempts in result['fit_attempts'].items():
        for label,row in attempts.items():
            if len(row['fit_stages'])>1:
                costs = ' → '.join(show(v['objective']) for v in row['fit_stages'])
                lines.extend(['',f'{design} {label} continued from each of its own stage endpoints. '
                                  f'The independently replayed objectives were {costs}.'])
            if row['failure']:
                first = row['failure'][0]
                lines.extend(['',f"**{design} {label}** reported {first['status']} at zero-based fitted row "
                                  f"{first['observation']}. {first['message']}"])
    screens = {key:value['new'] for key,value in q.items() if key.endswith(' start screening')}
    if screens:
        lines.extend(['','## Replacement starts','',
                      '| Design and draw | Minimum distance to admitted starts | Initial evaluation | Seconds |',
                      '|---|---:|---|---:|'])
        for key,d in screens.items():
            lines.append(f"| {key.removesuffix(' start screening')} | {min(d['pair_rms_distances'].values()):.6f} | "
                         f"{d.get('reason',d['disposition']).replace('|','/')} | {d['seconds']:.2f} |")
    probes = {key:value['new'] for key,value in q.items() if key.endswith(' descent probe')}
    if probes:
        lines.extend(['','## Replayed descent steps','',
                      'The box-constrained linearized least-squares step uses the endpoint Jacobian. '
                      'A replay at the resulting coefficients measures the actual objective reduction. '
                      'Both reductions are relative to the original objective.',
                      '','| Endpoint | Predicted reduction | Replayed reductions |',
                      '|---|---:|---|'])
        for key,d in probes.items():
            lines.append(f"| {key.removesuffix(' descent probe')} | {show(d['predicted'])} | "
                         f"{', '.join(map(show,d['measured']))} |")
    continuation = q.get('MDEA A continuation',{}).get('new')
    if continuation:
        trial = q.get('MDEA A projected gradient line',{}).get('new',[{}])[-1]
        restart = q.get('MDEA A admitted-descent continuation',{}).get('new')
        b = q['MDEA B saturation guess diagnostic']
        c = q['MDEA C saturation guess diagnostic']
        b_min = min(v['min_Pa'] for v in b['new'].values())/1000
        b_max = max(v['max_Pa'] for v in b['new'].values())/1000
        c_min = min(v['min_Pa'] for v in c['new'].values())/1000
        target = b['pressure_basis']['target_Pa']/1000
        lines.extend(['','## MDEA fit limits','',
                      f"The tightened Ceres continuation from A used {continuation['iterations']} iterations and returned "
                      f"objective {continuation['cost']:.12g} with optimizer projected gradient "
                      f"{continuation['optimizer_gradient']:.6g}. Its rejected trials concentrated on the Merkley "
                      "heat observation at zero-based row 124. The saturation search could not admit the vapor root "
                      "at 1.5 mol carbon dioxide per mol analytical amine.",
                      '',
                      f"The shortest tested projected-gradient step gave objective {trial.get('cost',float('nan')):.12g} "
                      f"and relative reduction {trial.get('relative_reduction',float('nan')):.6g}. "
                      "The decrease exceeds the inherited $10^{-10}$ relative function tolerance. "
                      "The two larger Gauss–Newton steps increased the objective and the smaller steps returned unexamined saturation gaps.",
                      '',
                      f"At start B, all 30 loading nodes returned bubble pressures from {b_min:.1f} to {b_max:.1f} kPa "
                      f"for each of three pressure guesses. All admitted nodes at C exceeded {int(c_min):,} kPa. "
                      f"The target was {target:,.0f} kPa in both cases. These finite samples leave feasibility undecided. "
                      "Among the 64 LHS draws, 61 were screened as replacements, two were the "
                      "original failures, and one fell below the separation limit after admitting the replacement. "
                      "With A, this yields two admitted starts in the declared design.",
                      '',
                      'The MDEA tables retain the phase and property comparisons at the provisional A endpoint.'])
        if restart:
            lines.extend(['',f"Restarting Ceres on the admitted descent step returned objective "
                          f"{restart['cost']:.12g} and optimizer projected gradient {restart['optimizer_gradient']:.6g}. "
                          f"{restart['message']}"])
    lines.extend(['',
                  'The Ceres function exits for MEA, DEA and both AMP fits are consistent with the small changes in the independent '
                  'descent replays. They missed the separate strict gradient threshold. A second displaced AMP fixed-slope start '
                  'returned the high-objective basin reached by C within the relative objective tie tolerance. '
                  'The basin is reproducible at the fit tolerance, with several active bounds and an unresolved strict gradient check.',
                  ''])
    legacy = q.get('Legacy R1 weighted residual at row 129')
    if legacy:
        cp = q['R1 row 129 Cp with archived water record']
        r1,r3,r5 = (q[f'{gate} numerical reproduction on current water caloric basis']['new']
                    for gate in ('R1','R3','R5'))
        lines.extend(['','## Numerical reproduction on the current water caloric basis','',
                      f"R1 originally stopped at zero-based row 129. The weighted residual was {legacy['new']:.16g} "
                      f"against {legacy['old']:.16g} at tolerance $10^{{-8}}$. Commit `32e572051` replaced the "
                      "water ideal-gas caloric correlation. With the archived water record restored on the study wheel, "
                      f"the predicted heat capacity for unloaded 30 wt% MDEA was {cp['new']:.14f} J/(mol feed K), "
                      f"compared with {cp['old']:.14f} in the archive. The current-basis expectations use the archived "
                      "residuals plus the measured water-record correction for the 33 heat-capacity rows.",
                      '',
                      f"R1 reproduced the B1 objective ({r1['cost']:.12g}) with maximum weighted residual error "
                      f"{r1['max_residual_error']:.3g}. R3 reproduced the Ermatchkov AARD ({r3['AARD_percent']:.8f}%) "
                      f"on {r3['rows']} rows at or below 49 wt% MDEA. R5 reproduced the A3 objective ({r5['cost']:.12g}) "
                      f"with maximum weighted residual error {r5['max_residual_error']:.3g} and matching coordinates."])
    profile = [q.get(f'Round 7 D AMP profile {side} {edge} bracket') for side in ('-1','1')
               for edge in ('within','beyond')]
    if all(p and p['new'] is not None for p in profile):
        lines.extend(['','## AMP conditional slope profile','',
                     '| Crossing | Tracking bracket (K) | Fixed-reference bracket (K) |',
                     '|---|---:|---:|'])
        for label,(a,b) in zip(('Lower','Upper'),(profile[:2],profile[2:]),strict=True):
            lines.append(f"| {label} | {a['old']:.5f} to {b['old']:.5f} | {a['new']:.5f} to {b['new']:.5f} |")
        lines.extend(['','The profile reoptimizes the other eight AMP coordinates for each held slope. '
                      'The cutoff uses the same conditional variance and objective-increment construction as round 7.'])
    lines.extend(['','## Observation deviations','',
                  '| Population | Statistic (%) | Tracking | Refitted |','|---|---|---:|---:|'])
    for key, item in q.items():
        if (key.endswith(' matched AARD_percent') and not key.startswith(('C5 ','MDEA corrected-Kamps '))
                or key.startswith(('C3 DEA AARD','C7 Kuranov row-matched','C7 Hong matched population'))
                or key.startswith(('MEA off-window ','MEA pressure ')) and key.endswith(' AARD_percent')):
            label = key.removesuffix(' AARD_percent').removesuffix(' matched')
            lines.append(f"| {label} | AARD | {show(item['old'])} | {show(item['new'])} |")
    lines.extend(['','### MDEA matched populations','',
                  '| Population | Common rows | Statistic (%) | Tracking | Refitted |',
                  '|---|---:|---|---:|---:|'])
    for key,item in q.items():
        if key.startswith('C5 ') and ' matched ' in key:
            label,stat = key.removeprefix('C5 ').removeprefix('C7 ').split(' matched ')
            statistic = 'AARD' if stat=='AARD_percent' else 'Signed bias'
            lines.append(f"| {label} | {item['population']} | {statistic} | {show(item['old'])} | {show(item['new'])} |")
        if key.startswith('C7 corrected-Kamps additional row '):
            extra = item
    counts = extra['population']
    full = q['MDEA corrected-Kamps Pa all AARD_percent']
    lines.extend(['',f"Corrected Kamps row 13 (`comparison:113`) was unavailable in tracking. The refitted "
                  f"bubble pressure was {extra['new']/1e6:.6f} MPa against the measured {counts['observed_Pa']/1e6:.3f} MPa "
                  f"({counts['refit_relative_error_percent']:+.2f}% signed deviation). The refitted AARD over all "
                  f"{full['population']['new']['available']} available rows was {full['new']:.5f}%.",
                  '', 'C6 reports prediction spread on fitted rows by property group. The comparison of spread '
                  'against deviations from measurements within the same operating bands remains open.'])
    lines.extend(['','## Phase searches','',
                  'The AMP experimental counts use the six retained absolute pressures for each selected endpoint. '
                  'The worked state and the 666 standard search states per protocol have separate outcomes.',
                  '','| State or search | Tracking outcome | Fixed-reference outcome |','|---|---|---|'])
    for key,item in q.items():
        if ' phase ' in key and not key.startswith('Round ') or key.endswith('finite search counts') or key.startswith('MEA measured screen'):
            outcome = item['new']
            if isinstance(outcome,dict):
                outcome = '<br>'.join(f'{n} {k}' for k,n in outcome.items())
            lines.append(f"| {key} | {show(item['old'])} | {show(outcome)} |")
    lines.extend(['','## Reference derivatives','',
                  r'Each pressure or temperature perturbation re-solves the same conserved feed with $P_s$ held at 100 kPa. '
                  r'The reconstructed extensive potential is $G^*=G_{\rm EOS}+RT\sum_i n_i b_i$. '
                  r'The pressure stencil tests $\partial G^*/\partial P=\sum_\alpha n_\alpha/\rho_\alpha$. '
                  r'The temperature stencil tests $-T^2\partial(G^*/T)/\partial T$ against Eq. 12 and the Engine enthalpy.',
                  'The error envelope combines the Engine arithmetic estimate for the potential and the spread across admitted steps. '
                  'The retained MDEA high-pressure daughters are separate conserved inventories for this check.',
                  '','| Branch and quantity | Signed discrepancy | Numerical error estimate | Relative volume discrepancy | Units | Admitted steps | Disposition |',
                  '|---|---:|---:|---:|---|---:|---|'])
    for key,item in q.items():
        if key.startswith('C1 ') and isinstance(item['new'],dict):
            v = item['new']
            lines.append(f"| {key} | {show(v['signed_error'])} | {show(v['estimated_error'])} | "
                         f"{show(v.get('relative_error'))} | {item['unit']} | {v['admitted_steps']} | {v['disposition']} |")
    timing = {k.removeprefix('Campaign stage '):v['new'] for k,v in q.items() if k.startswith('Campaign stage ')}
    if timing:
        lines.extend(['','## Stage timing','',
                      'Measured entries record timed calculations. The lanes overlapped.',
                      '','| Stage | Allowance (s) | Stop (s) | Throughput projection (s) | Measured (s) | Disposition |',
                      '|---|---:|---:|---:|---:|---|'])
        for stage,v in timing.items():
            lines.append('| '+' | '.join(map(show,(stage,v['allowance_s'],v['stop_s'],v.get('projected_s'),
                                                  v.get('measured_s'),v['disposition'])))+' |')
        for stage,v in timing.items():
            if 'notes' in v:
                lines.extend(['',f"**{stage}.** {v['notes']}"])
    counts = Counter(v['disposition'] for k,v in q.items())
    categories = {}
    for key, item in q.items():
        if item['disposition'] not in ('open','undecided'):
            continue
        parts = key.split()
        category = (' '.join(parts[:3]) if key.startswith('Round ') else
                    'C1 numerical error' if key.startswith('C1 ') else
                    'MDEA properties' if key.startswith('MDEA Merkley-outside') else
                    parts[0]+' phase controls' if ' phase ' in key else parts[0]+' fit and properties')
        categories.setdefault((item['disposition'],category),[]).append(key)
    lines.extend(['','## Coverage','',
                  f"The quantity index contains {counts['replayed']} replayed comparisons and "
                  f"{counts['independent contributor']} quantities with independent contributors. "
                  f"It records {counts['open']} open keys and {counts['undecided']} undecided results.",
                  '', 'Tables preserve exact comparisons at discrete feeds, fitted endpoints and pressure controls. '
                  'A phase outcome applies to its finite trials and recorded pressure and feed.',
                  '', '## Reproduction','',
                  'Run from the repository root with the installed study wheel verified against '
                  '`c9fbf898b14d004f915f01ed77675867908dd30d77dc28544b2860e9195c80bb`. '
                  'Use `refit.py prepare`, `refit.py attempt` and `refit.py select` for the named design. '
                  'Use `phase_replays.py pilot` on the bound A declaration after timing displaced B through its independent replay. '
                  'For an initial refusal use `refit.py initial DESIGN B` to retain the independent replay refusal. '
                  'The receiver expansion is `campaign.py DEA`, `campaign.py MDEA` or `campaign.py AMP`. '
                  'Use `refit.py replace DESIGN` for the seeded replacement screen and then `refit.py attempt DESIGN LHS-NN` '
                  'for an admitted draw. Run `stationarity.py DESIGN START` for the descent probe. '
                  'Use `stationarity.py root` or `stationarity.py amp-roots` for the pressure-guess diagnostics. '
                  'The MDEA diagnostic commands are `stationarity.py mdea-continue`, `stationarity.py mdea-descent` and '
                  '`stationarity.py mdea-restart`. Use `property_replays.py AMP-profile` for the conditional slope profile. '
                  'The selected MEA screen uses `mea_replays.py`. The derivative checks use '
                  '`reference_derivatives.py fixed-at-old` and `reference_derivatives.py selected`.',
                  '', 'Recompute the handoff with `uv run --no-sync python analyses/fixed_reaction_reference/handoff.py --check`.'])
    lines.extend(['','## Starting and remaining quantity keys',''])
    prior = result['starting_dispositions']
    original = Counter(prior.values())
    lines.extend([f"The starting handoff had {original['open']} open keys and {original['undecided']} undecided results.",
                  'The lists include the starting keys and any new unresolved results.'])
    for key,status in prior.items():
        item = q[key]
        if item['disposition']==status:
            continue
        parts = key.split()
        category = ' '.join(parts[:3]) if key.startswith('Round ') else parts[0]
        label = (f'{key} → {item["disposition"]} (started {status})')
        categories.setdefault(('updated',category),[]).append(label)
    for (status,category), keys in sorted(categories.items()):
        lines.extend(['',f'### {status.capitalize()} · {category} ({len(keys)})',''])
        if status=='open' and category=='Round 7 D':
            lines.extend(['The remaining bound and weighting sensitivities need separate fits.', ''])
        elif status=='open' and category in ('Round 7 A','Round 7 B','MDEA properties'):
            lines.extend(['The MDEA replay requires a qualified endpoint or an admitted property or phase evaluation on the declared basis.', ''])
        elif status=='open' and category=='Round 7 H':
            lines.extend(['The archived rounding checks require a table-specific contributor join.', ''])
        elif status=='undecided' and category.endswith('phase controls'):
            lines.extend(['The retained search did not resolve the phase outcome or its physical checks.', ''])
        lines.extend(f'- {key}' for key in keys)
    return '\n'.join(lines)+'\n'
