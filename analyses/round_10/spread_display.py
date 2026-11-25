"""Display rows for the round-10 handoff."""


def spread_table(q, table, head, num):
    def spread(value):
        return r'\num{' + f'{value:.3g}' + '}' if value is not None else '---'

    labels = {
        'Cai': 'Cai bubble pressure', 'Horstmann': 'Horstmann excess enthalpy',
        'Lawson-394K': 'Lawson and Garst (394 K) partial pressure',
        'Lawson-VIII': 'Lawson and Garst (50--54.5 wt%) partial pressure',
        'kundu': 'Kundu partial pressure', 'tong-baseline': r'Tong \COtwo-free bubble pressure',
        'Pappa2006': 'Pappa pure AMP vapor pressure',
        'Kuranov': 'Kuranov loaded total pressure', 'Kuranov-413K': 'Kuranov total pressure (413 K)',
        'Carson': 'Carson integral heat', 'Zheng': 'Zheng integral heat',
        'Ermatchkov': 'Ermatchkov partial pressure', 'Xiao': 'Xiao partial pressure',
        'Sedighi': 'Sedighi total pressure',
        'Merkley-half-loading': 'Merkley integral heat (half loading)',
        'Merkley-outside': 'Merkley integral heat (remaining states)',
        'corrected-Kamps': 'Corrected Kamps total pressure',
        'corrected-Kamps (27 common rows)': 'Corrected Kamps total pressure (27 rows)',
        'Arcis2011': 'Arcis integral heat', 'Kim2007': 'Kim and Svendsen absorption heat',
        'Kim2014': 'Kim et al. absorption heat', 'Vinjarapu2024': 'Vinjarapu et al. integral heat',
        'Kim2007 flagged': 'Kim and Svendsen absorption heat (flagged)',
        'Mamun2005 (outside objective)': "Ma'mun partial pressure",
        'Wagner2013': 'Wagner partial pressure',
    }
    rows = []
    for amine, record in q['K1 Endpoint prediction spread'].items():
        rows.append(head(amine.replace('_free', ', free slope'), 6))
        for name, r in record['groups'].items():
            extreme = r['row_spreads'].get(r['max_row'], {})
            label = labels.get(name)
            if label is None:
                base = name.removesuffix(' (hot)')
                label = labels[base] + ' (hot)' if base in labels else name
            rows.append([label.replace('%', r'\%'), f"{r['common']}/{r['requested']}",
                         num(r['endpoint_AARD_percent']['A'], 3), spread(r['AARD_spread_pp']),
                         spread(extreme.get('relative_spread_percent')),
                         num(extreme.get('selected_abs_relative_deviation_percent'), 3)])
    table('supplement-endpoint-prediction-spread',
          'Measured-data deviations and prediction spread across retained endpoints at a fixed 100 kPa reaction reference.',
          ['Observation set', 'Common / requested', r'A AARD (\%)',
           'AARD spread (percentage points)', r'Max. row spread (\%)', r'A error at max. spread (\%)'],
          rows, [.37,.11,.103,.132,.116,.102], long=True, size=r'\footnotesize',
          notes=r'A is the reported endpoint. The spreads use A, B and LHS-21 for MEA, A, B and C for DEA, '
          r'A, LHS-06 and LHS-45 for AMP, and both A continuations and LHS-53 for MDEA. '
          r'MDEA Kuranov (66) and Carson (40) are fitted. Kuranov pressures are total pressures and Carson heats are integral. '
          r'MEA pressure rows use \COtwo partial pressure. Hot denotes $T\geq370$ K. '
          r'AARD uses the common available rows with nonzero measurements. AARD spread is the maximum minus the minimum AARD. '
          r'Row spread is $100(\max y^{\mathrm{calc}}-\min y^{\mathrm{calc}})/|y^{\mathrm{obs}}|$. '
          r'The last column is the absolute relative deviation of A on the row of maximum spread. '
          r'A dash marks an undefined comparison. The pure AMP prefit is shared.')
