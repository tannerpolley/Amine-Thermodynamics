"""Present the round-9 quantities from retained results."""
from collections import Counter


def render(q):
    dea, amp, counts, shared, kamps = (q[key] for key in (
        'R1 DEA two-liquid certificates', 'R2 AMP early and reported pressure controls',
        'R3 start, endpoint and search accounting', 'R4 shared interactions at 100 kPa',
        'R6 corrected Kamps pressure comparisons'))
    state = next(r for r in dea['rows'] if r['key'] == dea['worked_state'])
    phase = state['phases']
    drop = state['split']['Gibbs_decrease_over_RT_mol']
    error = state['split']['numerical_error_over_RT_mol']
    lines = [
        '---', 'title: Phase controls and shared-interaction sensitivity', '---', '',
        '## DEA split at 30 wt%', '',
        f"At {state['T_K']:.2f} K and assigned {state['P_Pa']/1000:.3f} kPa, a feed of 1 mol DEA "
        'at 0.50 mol CO₂/mol DEA gives the following two liquids.', '',
        '| Daughter | Amount (mol true species) | True mole share (%) | Density (kg/m³) | Molar volume (cm³/mol) |',
        '|---|---:|---:|---:|---:|',
        *[f"| {i} | {r['amount_mol']:.6f} | {r['true_mole_fraction']*100:.4f} | "
          f"{r['density_kg_m3']:.3f} | {r['molar_volume_m3_mol']*1e6:.5f} |" for i,r in enumerate(phase,1)], '',
        f"The decrease in $G^*/(RT)$ is {drop:.9f} mol with paired numerical error {error:.2e} mol. "
        f"The maximum reaction and interphase residuals are {state['max_reaction_residual']:.2e} and "
        f"{state['max_interphase_residual']:.2e}, respectively. Both daughters match liquid roots. "
        'The repeat with the enlarged trial set recovered all four splits. The direct daughter restart '
        'coalesced for this feed, and the retained neighboring-state start recovered the split. '
        'The [DEA readback](results/dea-phase-controls.json.gz) gives the complete compositions, conserved-group matrix, '
        'closure and phase criteria for all four states.', '',
        '## AMP at fixed external pressure', '',
        '| State | Search pressure (MPa) | Reported bubble pressure (MPa) | Early fit | Reported fit |',
        '|---|---:|---:|---|---|',
    ]
    for r in sorted(amp['rows'], key=lambda row: row['key'] != 'worked-state'):
        lines.append(f"| {r['key']} | {r['P_Pa']/1e6:.5f} | {r['reported_bubble_Pa']/1e6:.5f} | "
                     f"{r['outcomes']['early']} | {r['outcomes']['reported']} |")
    lines += [
        '', 'All four unresolved candidates had vapor-directed descents below the reported bubble pressure. '
        'One liquid–vapor candidate passed the strict root test. Three passed the equilibrium residual and physical '
        'checks with an unspecified returned vapor branch. A dilute-vapor trace connected those roots. The '
        '[AMP controls](results/amp-phase-controls.json.gz) retain the failed two-liquid starts and the source rows.', '',
        '## Search and start accounting', '',
        '| System | Attempted | Completed |', '|---|---:|---:|',
        *[f"| {name.replace('_', ' ')} | {r['attempted']} | {r['completed']} |" for name,r in counts['coverage'].items()], '',
    ]
    pressure_bases = Counter(r['pressure_basis'] for r in counts['mdea_distinct_states'])
    starts = counts['mdea_start_counts']
    lines += [
        f"MDEA has {counts['mdea_detections']} descent detections at {len(counts['mdea_distinct_states'])} distinct states "
        f"({pressure_bases['measured']} measured pressures and {pressure_bases['assigned']} assigned pressures). "
        f"Of {starts['drawn']} drawn starts, {starts['tested']} were tested and one was evaluable. "
        'The other endpoint came from inherited start A. The optimizer stop messages and the projected-gradient '
        'test are recorded for each stage in the [quantity handoff](manuscript-handoff.json).', '',
        '## Shared interactions at a 100 kPa reaction reference', '',
        'The alternative uses the retained water–bicarbonate and water–carbonate interactions '
        '0.7650000233694618 and −0.25. The two sensitivities use only inherited start A and the same observation '
        'weights and bounds as the salt-anchored models.', '',
        '| Observation | Common rows | Salt-anchored AARD (%) | MEA-fitted shared AARD (%) |',
        '|---|---:|---:|---:|',
    ]
    for key, result in shared['comparisons'].items():
        before, after = (result['models'][case]['AARD_percent'] for case in ('salt-anchored', 'MEA-fitted'))
        lines.append(f"| {key} | {len(result['common'])}/{result['requested']} | {before:.2f} | {after:.2f} |")
    last = shared['fit_stages']['MDEA'][-1]
    lines += ['', f"The MDEA sensitivity reached the iteration limit at $C={last['C']:.6f}$ "
                  f"with projected-gradient norm {last['projected_gradient']:.3g}. "
                  'The endpoint objective replay passed.', '',
              '| External pressure (MPa) | Basis | Salt-anchored | MEA-fitted shared |', '|---:|---|---|---|']
    for row in shared['phase_controls'].values():
        a, b = (row['models'][case]['outcome'] for case in ('salt-anchored', 'MEA-fitted'))
        lines.append(f"| {row['P_Pa']/1e6:.5f} | {row['basis']} | {a} | {b} |")
    lines += [
        '', 'These phase results apply to the tested declarations and starts. The errors quantify agreement on common '
        'observations. The residuals and paired Gibbs error quantify numerical verification. Experimental '
        'confirmation of phase identity remains open.', '',
        '## Corrected Kamps total pressures', '',
        f"The provisional MDEA fit gives {kamps['common_AARD_percent']:.2f}% AARD on the "
        f"{kamps['common_rows']} common rows and {kamps['full_AARD_percent']:.2f}% on all {kamps['full_rows']}. "
        f"The additional row is Ermatchkov et al. Table 6 row {kamps['additional_row']['row']['source_row']}, "
        f"with signed deviation +{kamps['additional_signed_percent']:.2f}%.", '',
        '## AMP enthalpy increment', '',
        'The signed R4 enthalpy increment in J/mol is fit coordinate 8 minus 5000 J/mol. '
        'The coordinate bounds $[0,10000]$ correspond to physical bounds $[-5000,5000]$ J/mol.', '',
        'The outputs are scalar and categorical comparisons. Full precision, failed calculations and contributor '
        'hashes are retained in the [quantity handoff](manuscript-handoff.json). Independent review and '
        'investigator promotion are pending.', '',
    ]
    return '\n'.join(lines)
