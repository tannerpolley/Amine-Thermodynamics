"""Present the round-10 quantities from retained replay and screen records."""


def number(value, digits=3):
    return '—' if value is None else f'{value:.{digits}f}'


def spread(value):
    return '—' if value is None else f'{value:.3g}'


def render(q):
    lines = ['---', 'title: Endpoint spread, phase searches and densities', '---', '',
             '## K1. Spread across endpoints', '',
             'Only rows with nonzero measurements and available values at all compared endpoints enter AARD. '
             r'The row spread is $100(\max y_c-\min y_c)/|y_o|$. AARD spread is max–min in percentage points. '
             'Column A gives the measured-data deviation of the manuscript endpoint on the same rows. '
             'For MDEA the spread uses both A continuations and LHS-53. '
             'The spreads describe these endpoints and observations. They do not quantify parameter uncertainty.', '',
             '| Amine and observations | Common / requested | A AARD (%) | AARD spread (pp) | Max. row spread (%) | A error at max. spread (%) |',
             '|---|---:|---:|---:|---:|---:|']
    for amine, result in q['K1 Endpoint prediction spread'].items():
        for group, g in result['groups'].items():
            maximum = g['row_spreads'].get(g['max_row'], {})
            lines.append(f"| {amine}, {group} | {g['common']}/{g['requested']} | "
                         f"{number(g['endpoint_AARD_percent']['A'])} | {spread(g['AARD_spread_pp'])} | "
                         f"{spread(maximum.get('relative_spread_percent'))} | "
                         f"{number(maximum.get('selected_abs_relative_deviation_percent'))} |")
    lines += ['', 'Every requested prediction and refusal is in [the replay records](results/). '
              'The [quantity handoff](manuscript-handoff.json) gives the row identities, row spreads, '
              'measured deviations at the maximum spread and the matched AARD for each endpoint.', '',
              '## K2. Parent assemblages and AMP controls', '']
    m = q['K2 MEA search parent assemblages']
    lines += [f"MEA: {m['liquid_grid']['completed']:,} of {m['liquid_grid']['attempted']:,} liquid-grid states completed. "
              f"The {m['census']['attempted']} L–V census cases returned {m['census']['outcomes']['passed-two-phase']} "
              f"passed two-phase and {m['census']['outcomes']['passed-single-liquid']} passed single-liquid parents. "
              f"The measured-pressure screen completed {m['measured']['completed']} of {m['measured']['attempted']} states.", '',
              '| AMP control | Measured pressure (MPa) | Selected-endpoint outcome |', '|---|---:|---|']
    for key, row in q['K2 AMP control outcomes'].items():
        source = key.split(':')[0]
        outcome = row['outcome'].replace(';', ',')
        lines.append(f"| {source} row {row['source']['row']} ({row['source']['T_K']} K) | "
                     f"{row['pressure_Pa']/1e6:.5f} | {outcome} |")
    lines += ['', '## K3. DEA density at 298.15 K and assigned 101.325 kPa', '',
              r'Bulk density uses additive daughter volumes, $\rho=(\sum_i w_i/\rho_i)^{-1}$.', '',
              '| Deposit ID | Processed source row | Measured | Single liquid | Two-liquid bulk |',
              '|---:|---:|---:|---:|---:|']
    dea = q['K3 DEA measured and calculated densities']
    for r in dea['rows']:
        lines.append(f"| {r['deposit_id']} | {r['processed_source_row']} | {r['observed_kg_m3']:.2f} | "
                     f"{r['single_liquid_kg_m3']:.2f} | {r['two_liquid_kg_m3']:.2f} |")
    lines += ['', 'Densities are in kg/m³. AARD is '
              f"{dea['AARD_percent']['single_liquid']:.3f}% for the single liquid and "
              f"{dea['AARD_percent']['two_liquid']:.3f}% for the two-liquid bulk. "
              'Agreement of bulk densities alone does not identify the phases in the experiment.', '',
              '## K4. MDEA bubble pressures at measured descent states', '',
              '| State | Measured (MPa) | Bubble pressure (MPa) | Outcome |', '|---|---:|---:|---|']
    for name, r in q['K4 MDEA bubble pressures at measured descent states'].items():
        pressure = None if r['bubble_Pa'] is None else r['bubble_Pa']/1e6
        status = r['diagnostic'] if pressure is None else r['status']
        lines.append(f"| {name} | {r['measured_Pa']/1e6:.5f} | {number(pressure, 5)} | {status} |")
    lines += ['', 'The handoff records model predictions and numerical checks for the specified states. Experimental phase identity remains open.']
    return '\n'.join(lines) + '\n'
