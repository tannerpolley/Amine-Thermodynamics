"""Recompute the numerical handoff and notebook from retained contributors."""
from hashlib import sha256
import json
import sys
from time import monotonic
from records import BASE, DISPLAY, HERE, ROOT, OUT, LIMITS, NAMES, Sources, replay_path, write
from reductions import reference, phases, dea, amp, salts, endpoints, literature

def notebook(quantities, table):
    c1, c4, c6, c7 = (quantities[i-1] for i in (1,4,6,7))
    lines = [r"""---
title: Round 8 referee calculations
---

At fixed liquid inventory, $G^*=G_{\rm EOS}+RT\sum_i n_i b_i(T,P_s)$ and
$G^*_P=V_{\rm EOS}+RT\sum_i n_i b_{i,P_s}\,dP_s/dP$. The reference
contributes when it tracks system pressure. At reaction equilibrium the same
envelope derivative holds on each differentiable branch at fixed conserved
feed. Sum the phase contributions for a pair and use one-sided derivatives
at a branch switch. At fixed volume the pressure-reference chain term is
$-RT^2\sum_i n_i b_{i,P_s}(\partial P/\partial T)_{V,n}$.

Peiper and Pitzer's printed water activities give
$-\ln a_w/M_w=\phi_{\rm eq}\sum_i m_i=\phi_{\rm st}\sum_s\nu_s m_s$
within printed precision. The fitted ionic target subtracts ideal dissolved
CO₂ molality from the equilibrium numerator and divides by the charge-closed
ionic molality sum.

The property errors compare model results with observations. The phase
results concern model predictions for the declared states and trial banks.
These results await independent review and investigator promotion.

[Quantity index](manuscript-handoff.json)

## Caloric comparison

The Gibbs–Helmholtz readback evaluates $H_G=-T^2[\partial(G^*/T)/\partial T]_{P,\mathrm{feed}}$
with $G=H-TS$ and common caloric references. It holds both the system
and reference pressures fixed as temperature varies. Energies are normalized
per mole of apparent amine fed. The spread is the maximum minus
minimum of $H_{\rm Engine}-H_G$ over the retained step pairs.

| Branch | Temperature (K) | Pressure (MPa) | Finest admitted step (K) | $H_{\rm Engine}-H_G$ (kJ/mol) | Spread (kJ/mol) |
| --- | ---: | ---: | ---: | ---: | ---: |"""]
    branches = c1['branches']
    difference = 'engine_minus_Gibbs_Helmholtz_kJ'
    for key, branch in branches.items():
        state = branch.get('state',branches['parent']['state'])
        steps = [(dt,q[difference]) for dt,q in zip(branch['step_K'],branch['steps'],strict=True) if difference in q]
        step, delta = (f'{x:.6g}' for x in steps[-1]) if steps else ('—','—')
        spread = branch['spread'].get(difference)
        lines.append(f"| {key} | {state['T_K']:.2f} | {state['P_Pa']/1e6:.6f} | {step} | {delta} | "
                     + (f'{spread:.6g} |' if spread is not None else 'unresolved |'))
    for key, branch in branches.items():
        if 'caloric_refusals' in branch:
            residuals = ', '.join(f'{float(t):.2f} K at {r:.3g}' for t,r in branch['failed_root_best_relative_residual'].items())
            causes = ', '.join(dict.fromkeys(branch['caloric_refusals'].values()))
            lines.extend(['', f'{key} pressure check misses ({residuals}). {causes}.'])
            if 'diagnostic_spread_kJ' in branch:
                lines.append(f"The caloric difference spans {branch['diagnostic_spread_kJ']:.6g} kJ/mol if those "
                             'same-root diagnostic values are included.')
    amp = branches['AMP']
    gauge_tests = [q['gauge_cancellation'] for q in amp['steps'] if 'gauge_cancellation' in q]
    if gauge_tests:
        shift = amp['state']['caloric_gauge']['shifted']['h_J_mol']
        remainder = max(abs(q['difference_after_FD_bias_J_mol']) for q in gauge_tests)
        lines.extend(['', f'Shifting the common AMP enthalpy anchor by {shift:g} J/mol of apparent amine '
                           'adds that constant to the Engine enthalpy. In the central difference of $G/T$, '
                           r'the same shift is multiplied by $T^2/(T^2-\Delta T^2)$. '
                           f'The largest residual change after accounting for that finite-step bias is {remainder:.2g} J/mol.'])
    fixed = c1['reference_controls']['100-kPa']
    if 'replay' in fixed:
        replay = fixed['replay']
        source_p, = {rx['reference']['reference_pressure_pa'] for rx in replay['declaration']['reactions']}
        detail = replay['attempts'][0]['message'] if replay['attempts'] else replay['status']
        lines.extend(['', f"The {source_p/1e3:g} kPa reference control at {replay['P_Pa']/1e6:.3f} MPa "
                          f"retains {replay['instability']}. Its split outcome is {fixed['outcome']}.",
                      '', f'> {detail}'])
    else:
        lines.extend(['', f"The fixed reference control stopped with {fixed['refusal']}."])
    tracking = c1['reference_controls']['tracking']
    if tracking.get('outcome')=='confirmed split':
        pair = next(q for q in tracking['replay']['attempts'] if q['confirmed'])
        lowering, error = (pair[k] for k in ('Gibbs_decrease_over_RT_mol','numerical_error_over_RT_mol'))
        lines.extend(['', f"Tracking pressure confirms the split. Gibbs lowering divided by $RT$ is {lowering:.6g} mol "
                          f"on the retained feed, with an estimated numerical error of {error:.3g} mol."])
    added = c4['added_pressure_rows']
    hot = [c4['hot_original'][k]['free'] for k in ('hartono-2021','tong-2012')]
    lines.extend(['', f"The AMP refit includes {added['hartono-2021-supplemental']} supplemental Hartono pressures "
                  f"and {added['tong']} loaded Tong pressures. The original hot-pressure biases were "
                  f"{hot[0]['bias_percent']:.1f}% on {hot[0]['rows']} Hartono observations and "
                  f"{hot[1]['bias_percent']:.1f}% on {hot[1]['rows']} Tong observations.",
                  '', '## MDEA endpoint inventory', '',
                  '| Endpoint | Original start cost | Stage-0 final cost | Terminal cost | Keyed phase results |',
                  '| --- | ---: | ---: | ---: | --- |'])
    for entry in c6['MDEA']['inventory']:
        label = entry['endpoint'] + (' (adopted)' if entry['adopted'] else '')
        results = '<br>'.join(f"{float(k.split(':')[1])/1e6:.3f} MPa — {q['outcome']}"
                              for k,q in entry['phase'].items())
        lines.append(f"| {label} | {entry['initial_cost']:.8f} | {entry['stage_0_final_cost']:.8f} | "
                     f"{entry['final_cost']:.8f} | {results or '—'} |")
    for name in ('MEA #435','AMP'):
        outcomes = [f"{entry['endpoint']} at {outcome['P_Pa']/1e6:.6g} MPa — {outcome['outcome']}"
                    if 'P_Pa' in outcome else f"{entry['endpoint']} — {key} {outcome['outcome']}"
                    for entry in c6[name]['inventory'] for key,outcome in entry['phase'].items()]
        lines.extend(['', f"{name} endpoint controls give "+', '.join(outcomes)+'.'])
    kuranov = c7['kuranov']['readback']
    missing = c7['kamps']['salt/refit']['missing']
    lines.extend(['', 'The current Kuranov population is matched by source row. Published aggregates are compared by count.',
                  f"The study-wheel readback for Kuranov row {kuranov['row']['source_row']} gives "
                  f"{kuranov['value']:.5f} Pa, a change of {c7['kuranov']['readback_minus_archived_Pa']:.3g} Pa "
                  'from the archived prediction.'])
    for row in missing:
        lines.append(f"The matched Kamps comparison excludes {row['identity']} from Ermatchkov "
                     f"{row['row']['source_locator']}, row {row['row']['source_row']} ({row['status']}).")
    lines.extend(['', f'Core contributors are read from `{BASE}`. The named display replays are read from `{DISPLAY}`.',
                  '', '## Retained results', '', '| Item | Disposition | Evidence | Record |',
                  '| --- | --- | --- | --- |', *table])
    return '\n'.join(lines)+'\n'

def main(check):
    doc, table, quantities_by_item = {}, [], []
    timing = OUT/'runtime.json'
    times = json.loads(timing.read_text()) if check else {}
    for i, reduce in enumerate((reference,phases,dea,amp,salts,endpoints,literature),1):
        start = monotonic()
        src, file = Sources(), replay_path(i)
        replay = src.read(str(file.relative_to(ROOT)),None) if file.exists() else {}
        for path, x in replay.get('sources',{}).items():
            src.read(path,x['revision'])
            assert src.hashes[path]==x, f'stale replay input {path}'
        status, reason, quantities = reduce(src,replay)
        quantities_by_item.append(quantities)
        record = dict(disposition=status,reason=reason,quantities=quantities,execution=replay,
                      contributors=dict(src.hashes))
        path = OUT/f'{NAMES[i-1]}.json.gz'
        if check:
            retained = src.read(str(path.relative_to(ROOT)),None)
            assert i!=2 or retained['quantities']['fingerprint']==quantities['fingerprint'], 'MDEA model fingerprint mismatch'
            assert retained==record, f'C{i} stale retained reduction'
        else:
            write(path,record)
            times[f'C{i}'] = dict(replay_s=replay.get('seconds',0),reduction_s=monotonic()-start,projection_s=LIMITS[i-1])
        doc[f'C{i}'] = dict(disposition=status,reason=reason,runtime=times[f'C{i}'],
                            quantities={k:dict(record=str(path.relative_to(HERE)),field=f'quantities.{k}')
                                        for k in quantities}, record_sha256=sha256(path.read_bytes()).hexdigest())
        table.append(f"| C{i} | {status} | {reason} | [Retained quantities](results/{path.name}) |")
    if not check:
        write(timing,times)
    handoff = dict(base=BASE,display_snapshot=DISPLAY,items=doc)
    path, qmd = HERE/'manuscript-handoff.json', HERE/'notebook.qmd'
    expected = notebook(quantities_by_item,table)
    if check:
        assert json.loads(path.read_text())==handoff, 'stale handoff quantity or disposition'
        assert qmd.read_text()==expected, 'stale notebook display'
        print('Round 8 handoff checks passed (C1–C7)')
    else:
        write(path,handoff)
        qmd.write_text(expected)
if __name__=='__main__':
    main(sys.argv[1:]==['--check'])
