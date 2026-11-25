"""Table rows for the round-9 numerical handoff."""


def tables(q, table, head, num, scientific, dea_density, amp_outcomes):
    dea, amp, shared = (q[key] for key in ('R1 DEA two-liquid certificates',
                                           'R2 AMP early and reported pressure controls',
                                           'R4 shared interactions at 100 kPa'))
    rows = []
    density = {r['key']: r for r in dea_density['rows']}
    for state in dea['rows']:
        d = density[state['key']]
        case = f"Deposit ID {d['deposit_id']}, processed source row {d['processed_source_row']}, "
        case += rf"{state['unloaded_wt_percent']:.0f} wt\%, $\alpha={state['loading']:.2f}$"
        phase = state['phases']
        rows += [head(case, 6)]
        for label, key, factor, digits in [
            ('Amount (mol true species)', 'amount_mol', 1, 6),
            ('Share of total true moles (\\%)', 'true_mole_fraction', 100, 4),
            ('Share of total mass (\\%)', 'mass_fraction', 100, 4),
            ('Density (kg/m$^3$)', 'density_kg_m3', 1, 3),
            (r'$\partial P/\partial\rho_{\rm mol}$ (Pa m$^3$/mol)', 'dP_drho_Pa_m3_mol', 1, 2),
            ('Molar volume (cm$^3$/mol)', 'molar_volume_m3_mol', 1e6, 5),
        ]:
            values = [num(factor*p[key], digits) for p in phase]
            bulk = [num(d[k+'_kg_m3'], 2) for k in ('observed', 'single_liquid', 'two_liquid')] if key == 'density_kg_m3' else []
            rows.append([label, *values, *bulk])
        rows += [['Mole fraction ' + symbol, *[scientific(p['x'][i]) for p in phase]]
                 for i, symbol in enumerate((r'\COtwo', 'DEA', r'\HtwoO', r'\ce{DEAH+}',
                     r'\ce{DEACOO-}', r'\ce{HCO3-}', r'\ce{CO3^2-}', r'\ce{H3O+}', r'\ce{OH-}'))]
        rows += [
            ['Charge residual (mol)', *[scientific(p['charge_residual_mol']) for p in phase]],
            ['Pressure residual (Pa)', *[scientific(p['pressure_residual_Pa']) for p in phase]],
            ['Maximum reaction residual',
             *[scientific(max(abs(r['residual']) for r in state['reaction_contractions'] if r['phase']==i)) for i in range(2)]],
            ['Maximum interphase residual', scientific(state['max_interphase_residual']), ''],
            ['Elemental balance residuals (mol)', 'C, H, N, O',
             ', '.join(scientific(state['balances']['element_residual_mol'][e]) for e in 'CHNO')],
            [r'$\Delta G^*/(RT)$ decrease and paired error (mol)',
             scientific(state['split']['Gibbs_decrease_over_RT_mol']), scientific(state['split']['numerical_error_over_RT_mol'])],
            ['Two liquid roots', 'Matched', 'Matched'],
            ['Confirmed search / registry-growth repeat', f"{state['declared_confirmed']} / {state['registry_growth_confirmed']}", ''],
            ['Restart from its own daughters', 'Confirmed' if state['daughter_restart']['confirmed'] else 'Coalesced', ''],
        ]
    rows = [row + [''] * (6-len(row)) if len(row) > 1 else row for row in rows]
    rows.append([r'Density AARD across the four feeds (\%)', '', '', '',
                 *[num(dea_density['AARD_percent'][m], 3) for m in ('single_liquid', 'two_liquid')]])
    matrix = dea['rows'][0]['conservation_matrix']
    B = r'$\left[\begin{smallmatrix}' + r'\\'.join('&'.join(str(round(x)) for x in row) for row in matrix) + r'\end{smallmatrix}\right]$'
    table('supplement-dea-split-certificate',
          'Two-liquid certificates for the four DEA density-cell feeds at 298.15 K and assigned 101.325 kPa.',
          ['Quantity', 'Liquid 1', 'Liquid 2', 'Measured bulk', 'Single-liquid bulk', 'Two-liquid bulk'],
          rows, [.35,.13,.14,.093,.105,.105], long=True, size=r'\footnotesize',
          notes=r'One mol DEA in each feed. Deposit IDs are zero-based. The 9.73\% for the denser liquid of processed source row 33 divides its true-species amount by the sum of both daughter amounts. '
          r'The two-liquid bulk density is $(\sum_i w_i/\rho_i)^{-1}$ using daughter mass fractions $w_i$ and densities $\rho_i$. '
          r'Liquid roots must match within $|\ln(\rho_{\rm root}/\rho)|\le\ln(1.01)$ and relative pressure error $\le10^{-10}$. '
          r'Both phases must have positive isothermal pressure derivatives and positive amounts and differ by more than $10^{-6}$ in maximum mole-fraction difference or log density ratio. '
          r'The decrease in $G^*/(RT)$ must exceed the paired numerical error. Reaction residuals are $\ln Q-\ln K$ and interphase residuals are differences in '
          r'electrochemical potential divided by $RT$. '
          r'For main-text Eq.~(\ref{main-eq:tpd}), $g=G^*/n$ on the true-species molar basis and $B=$ ' + B +
          r' in the displayed species order, with charge enforced separately. Deposit ID 32 (processed source row 33) is reproduced from the retained neighboring-state start.')

    rows = []
    for state in sorted(amp['rows'], key=lambda q: q['key'] != 'worked-state'):
        key = state['key']
        if key == 'worked-state':
            src = 'Worked feed'
            early = r'Two liquids, $\Delta G^*/(RT)=' + f"-{state['early_attempts'][0]['Gibbs_decrease_over_RT_mol']:.5f}" + '$ mol'
        else:
            family, search, _ = key.split(':')
            src = family.split('-')[0].title() + f" r{state['source']['row']} ({search})"
            early = 'Two liquids'
        witness = state['witness']
        if witness:
            reported = 'Vapor-directed descent'
            lv = 'L+V passed' if state['reported_liquid_vapor_gate'] == 'passed' else 'L+V vapor root unspecified'
            gates = ' / '.join(state['reported_two_liquid_gates'])
        else:
            reported = 'No resolved descent'
            lv = '---'
            gates = '---'
        if key == 'worked-state':
            gates = 'Indeterminate reduced Hessian'
        else:
            reported = amp_outcomes[key]['outcome'].replace('; ', r'\newline ')
        rows.append([src, num(state['T_K'], 2), num(state['P_Pa']/1e6, 5), num(state['reported_bubble_Pa']/1e6, 5),
                     early, reported, gates, lv])
    table('amp-endpoint-pressure-controls',
          'Early and reported AMP fits at one common test pressure and six measured total pressures.',
          ['Source row (search ID)', '$T$ (K)', '$P$ (MPa)', r'Reported $P_{\rm bub}$ (MPa)',
           'Early fit', 'Reported outcome', 'Reported L+L refusal', 'Reported L+V'],
          rows, [.113,.070,.085,.105,.121,.127,.161,.140], size=r'\footnotesize',
          notes=r'Tong row numbers restart at each temperature. The early fit uses the system-pressure reference and the reported fit uses 100 kPa. '
          r'The worked feed contains 1 mol AMP at unloaded 30 wt\% and $\alpha=0.70$. '
          r'A dilute-vapor connection was checked for each descent with an unspecified returned density branch. '
          r'For three L+V candidates the residuals passed and the strict vapor-root label was unspecified. '
          r'No L+L control passed at the reported endpoint.')

    labels = {'MEA legacy-47': r'MEA, fitted $p_{\COtwo}$',
              'MEA Mamun2005': r'MEA, Ma\textquotesingle mun $p_{\COtwo}$',
              'MDEA Kuranov': 'MDEA, Kuranov loaded total pressure',
              'MDEA Ermatchkov': r'MDEA, Ermatchkov $p_{\COtwo}$',
              'MDEA Carson': 'MDEA, Carson integral heat'}
    rows = [[labels[key], f"{len(case['common'])}/{case['requested']}",
             *[num(case['models'][name]['AARD_percent'], 2) for name in ('salt-anchored','MEA-fitted')]]
            for key, case in shared['comparisons'].items()]
    receiver = shared['fit_stages']['MDEA'][-1]
    table('supplement-shared-interaction-sensitivity',
          'Matched observations for the salt-anchored and historical MEA-fitted shared interactions at 100 kPa.',
          ['Observable', 'Common / requested', r'Salt-anchored AARD (\%)', r'MEA-fitted shared AARD (\%)'],
          rows, [.41,.15,.19,.19],
          notes=r'Start A only for the sensitivity. The alternative has $k_{\rm water,HCO_3^-}=0.765000$ '
          r'and $k_{\rm water,CO_3^{2-}}=-0.25$. The 100 kPa value is the reaction reference. '
          r'The Kuranov pressure weights are the same for both MDEA fits. '
          f"The MDEA sensitivity stopped at the iteration limit, with replayed objective {num(receiver['C'], 6)} "
          f"and projected gradient {scientific(receiver['projected_gradient'])}.")
    rows = [[('Zheng et al., Table 4 r' + case['source']['source_row']) if case['basis'].startswith('measured') else label,
             num(case['P_Pa']/1e6, 5),
             *[model['outcome'].capitalize() for model in case['models'].values()]]
            for label, case in shared['phase_controls'].items()]
    table('supplement-shared-interaction-phase-controls',
          'MDEA phase controls for the two shared sets at a fixed 100 kPa reaction reference.',
          ['State', '$P$ (MPa)', 'Salt-anchored', 'MEA-fitted shared'],
          rows, [.25,.16,.26,.26], notes='The Zheng pressure is measured. The two higher pressures are targeted controls.')
