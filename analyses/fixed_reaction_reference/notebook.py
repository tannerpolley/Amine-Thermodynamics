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

| Design | Fitted rows | Tracking | Fixed at old parameters | Fixed and refitted | Change from tracking |
|---|---:|---:|---:|---:|---:|"""]
    for design,attempts in result['fit_attempts'].items():
        old = q[f'{design} objective at old parameters']
        new = q[f'{design} selected objective']
        lines.append('| '+' | '.join(map(show,(design,old['population']['fitted'],old['old'],old['new'],
                                              new['new'],new['absolute_change'])))+' |')
    lines.extend(['','## Start separation and endpoint stationarity','',
                  '| Design | A−B | A−C | B−C |','|---|---:|---:|---:|'])
    for design in result['fit_attempts']:
        distances = q[f'{design} start distances']['new']
        lines.append('| '+' | '.join(map(show,(design,*distances.values())))+' |')
    lines.extend(['','The projected gradient uses the bound-normalized coordinate widths. '
                  'The active-bound criterion is $10^{-6}$ times each optimizer scale. '
                  'All replay-eligible endpoints missed the solver-scale stationarity tolerance.',
                  '','| Design | Start | Status | Initial objective | Replayed objective | Projected gradient ∞-norm | Active bounds | Fit / replay (s) |',
                  '|---|---|---|---:|---:|---:|---|---:|'])
    for design,attempts in result['fit_attempts'].items():
        for label,row in attempts.items():
            bounds = '<br>'.join(f'{this} ({side})' for this,side in (row['active_bounds'] or {}).items())
            lines.append('| '+' | '.join(map(show,(design,label,row['status'],row['initial_cost'],row['objective'],
                row['projected_gradient_inf'],bounds or '—',f"{show(row['fit_seconds'])} / {show(row['replay_seconds'])}")))+' |')
    for design,attempts in result['fit_attempts'].items():
        for label,row in attempts.items():
            if len(row['fit_stages'])>1:
                costs = ' → '.join(show(v['objective']) for v in row['fit_stages'])
                lines.extend(['',f'{design} {label} continued from each of its own stage endpoints with the same controls. '
                                  f'The independently replayed objectives were {costs}.'])
            if row['failure']:
                first = row['failure'][0]
                lines.extend(['',f"**{design} {label}** reported {first['status']} at zero-based fitted row "
                                  f"{first['observation']}. {first['message']}"])
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
                  'The selected MEA screen uses `mea_replays.py`. The derivative checks use '
                  '`reference_derivatives.py fixed-at-old` and `reference_derivatives.py selected`.',
                  '', 'Recompute the handoff with `uv run --no-sync python analyses/fixed_reaction_reference/handoff.py --check`.'])
    return '\n'.join(lines)+'\n'
