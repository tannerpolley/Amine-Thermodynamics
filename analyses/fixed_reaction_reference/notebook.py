"""Present retained fit, derivative and phase comparisons as an analysis notebook."""
from collections import Counter


def show(value):
    if value is None:
        return '—'
    if isinstance(value,float):
        return f'{value:.8g}'
    return str(value)


def render(result):
    q = result['quantities']
    lines = [r"""---
title: Reaction standard-state pressure fixed at 100 kPa
resources:
  - manuscript-handoff.json
  - results/handoff-checks.json
  - results/stages.json
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
                      "At start B, all 30 loading nodes returned bubble pressures from about 24 to 187 kPa for each "
                      "of three pressure guesses. All admitted bubble pressures at start C exceeded 1.96 MPa. "
                      "The target was 1.121 MPa in both cases. The search provides evidence about the sampled starts "
                      "and loading domain. Among the 64 LHS draws, 61 were screened as replacements, two were the "
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
        lines.extend(['','## Legacy residual check','',
                      f"R1 stopped at row 129 on the starting commit. The weighted residual was {legacy['new']:.16g} "
                      f"against {legacy['old']:.16g} at tolerance $10^{{-8}}$. Identical observation, residual scale "
                      "and weight reproduce the archived residual from the archived prediction. The pinned wheel's "
                      "equilibrium heat-capacity prediction for unloaded 30 wt% MDEA differs by "
                      "$-0.00237384$ J/(mol feed K). The underlying cause remains open. R3 and R5 lie after the R1 assertion."])
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
                  '| Population | Tracking AARD (%) | Refitted AARD (%) |','|---|---:|---:|'])
    for key, item in q.items():
        if (key.endswith(' all AARD_percent') or key.startswith(('C3 DEA AARD','MEA off-window','C7 Kuranov row-matched',
                                                               'C7 Hong matched population')) and item['unit']=='%'
                or key.startswith('MEA pressure ') and key.endswith(' AARD_percent')):
            lines.append(f"| {key.removesuffix(' all AARD_percent')} | {show(item['old'])} | {show(item['new'])} |")
    lines.extend(['','## Phase searches','',
                  '| State or search | Tracking outcome | Fixed-reference outcome |','|---|---|---|'])
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
