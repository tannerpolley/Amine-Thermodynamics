"""Format the manuscript handoff from retained records, without loading the Engine."""
import argparse
from io import StringIO
import json
from pathlib import Path

HERE = Path(__file__).resolve().parent


def read(name):
    return json.loads((HERE/'results'/f'{name}.json').read_text())


def number(value, format_spec='.6g'):
    return 'Unavailable' if value is None else format(value,format_spec)


def table(head, rows):
    return '\n'.join(['| '+' | '.join(head)+' |', '| '+' | '.join(['---']*len(head))+' |',
                      *('| '+' | '.join(map(str,row))+' |' for row in rows)])


def handoff():
    q1,q2,q3,q4,q5,q6,q7,q8 = [read(name) for name in ('q1','q2','q3','q4','q5','q6','q7-summary','q8')]
    yield '## Q1. AMP fixed-pressure supplement'
    yield ('Compare both fits at the same species-ordered feed, temperature and absolute pressure. '
           'A near-zero minimum without a resolved descent applies only to the finite trial set. '
           'At S14 the fixed-slope endpoint has a vapor-side descent at the free fit’s search pressure. '
           'The seeded liquid pair is confirmed only for the free fit. [Paired records](results/q1.json).')
    yield table(['State','Pressure basis','Pa','Free min. TPD/RT','Fixed min. TPD/RT','Free LL','Fixed LL'],
        ((r['key'].split(":problem")[0] if not r['key'].startswith('grid:') else 'AMP grid loading '+r['key'].split(':')[-2],
          r['pressure_basis'],number(r['free']['P_Pa'],',.2f'),*(number(r[k]['minimum_trial']['quantities']['tpd_over_rt']
          if r[k]['minimum_trial'] else None) for k in ('free','fixed')),
          *('confirmed' if any(a['confirmed'] for a in r[k]['attempts']) else 'unconfirmed' for k in ('free','fixed'))) for r in q1['rows']))
    yield '## Q2. AMP total pressure at 373–393 K'
    yield ('Report the matched, constrained single-liquid AARD and signed bias (prediction minus observation). '
           'Retain unstable parents in these scores. The pressure-specific search and comparison of feasible supports '
           'are in [the row records](results/q2.json). Global stability remains unverified.')
    yield table(['Source','Matched','Zero loading','Resolved descents at observed P','Free AARD / bias (%)','Fixed AARD / bias (%)'],
                ((k,r['matched'],r['baseline'],r['fixed_pressure_outcomes'].get('resolved descent',0),
                  *(f"{r[e]['AARD_percent']:.4f} / {r[e]['bias_percent']:.4f}" for e in ('free','fixed'))) for k,r in q2['scores'].items()))
    worked = next(r for r in q2['rows'] if r['identity']=='hartono-2021:55')
    search = worked['measured_pressure_search']
    bubble = next(c for c in search['candidates'] if 'incipient' in c['support'])
    yield (f"Hartono 55 measured {worked['observed_Pa']:,.0f} Pa. The free liquid parent gave "
           f"{search['minimum_trial']['quantities']['tpd_over_rt']:.6f} minimum TPD/RT at that pressure. "
           f"The lowest-G feasible assemblage found among the tested supports was {search['lowest_found']['support']}. "
           f"The separate local two-liquid bubble was {number(bubble['pressure_Pa'],',.1f')} Pa "
           f"with liquid amounts {bubble['amounts_mol'][0]:.4f} and {bubble['amounts_mol'][1]:.5f} mol.")
    local = [(r,c) for r in q2['rows'] for c in r['measured_pressure_search'].get('candidates',[])
             if c['support']=='L1+L2+incipient V' and c['qualified']]
    yield table(['Observation','Observed total pressure (Pa)','Local LL bubble (Pa)'],
                ((r['identity'],number(r['observed_Pa'],',.0f'),number(c['pressure_Pa'],',.1f')) for r,c in local))
    yield '## Q3. MDEA Table 8 supplement'
    yield ('Gibbs decrease is parent minus pair, divided by $RT$, on the 1 mol MDEA feed basis. '
           'Both low-fit decreases reproduce within the original paired numerical errors. The other endpoints had '
           'converged parents, with rejected or exhausted seeded LL attempts. [Feeds, roots, and attempts](results/q3.json).')
    yield table(['Water–bicarbonate $k$','K','Pa','CO₂ / H₂O mol','Gibbs decrease / RT (mol)'],
                ((number(r['k']),number(r['T_K']),number(r['P_Pa'],',.3f'),f"{r['feed_mol'][0]:.4g} / {r['feed_mol'][1]:.9g}",
                  number(r['attempts'][0].get('Gibbs_decrease_over_RT_mol'))) for r in q3['rows']))
    yield '## Q4. Eq. 8, nomenclature, and S15'
    yield ('R1–R3 aqueous references are evaluated at system pressure, including the solved pressure in a bubble calculation. '
           'R4–R5 use 100,000 Pa where present. Vinjarapu et al. (2024, apparatus p. 4 and discussion pp. 7–8) identifies '
           '17.34 bar as the physical calorimeter back pressure. Austgen et al. (1991, Eq. 7 and Table V) gives the temperature laws '
           'on the mole-fraction basis. Keep S15’s five pressure entries and the 100,000 Pa ideal-gas caloric standard. '
           'Use the following common-molality R1/R3 log constants and pure fugacity contractions. [Readback](results/q4.json).')
    yield table(['Reaction','Common-molality ln K','Γ'],((r['reaction'],number(r['common_ln_K'],'.6f'),number(r['common_Gamma'],'.6f'))
                                                          for r in q4['S15_common_basis'] if r['reaction'] in ('R1','R3')))
    yield table(['Case','Baseline pCO₂ (Pa)','Fixed-reference pCO₂ (Pa)','Δ bubble P (Pa)','Max. absolute liquid Δx'],
                ((r['identity'], number(r['baseline'].get('value_Pa')),number(r['fixed_reference'].get('value_Pa')),
                  number(r.get('bubble_pressure_change',{}).get('absolute')),number(max(abs(v['absolute']) for v in r['species_x_change'].values())))
                 for r in q4['rows']))
    yield (f"The S15 0→0.31 mol/mol addition at 313.15 K and 1.734 MPa changes from {q4['heat'][0]['value_kJ_mol']:.6f} to "
           f"{q4['heat'][1]['value_kJ_mol']:.6f} kJ/mol added CO₂. The unloaded heat endpoint has undefined quotients "
           "for reactions requiring absent carbon species. The lightest canonical bubble and Böttinger 046 miss the separate "
           "relative EOS pressure readback threshold in both conventions while passing the native scaled equations. "
           "The matched fixed-pressure 100 kPa control has identical species mole fractions.")
    yield '## Q5. MEA pH and carbonate diagnostic'
    grid = [r for r in q5['rows'] if r['symbol'] is None]
    ctrl = next(r for r in grid if r['loading']==.3)
    yield (f"At 30 wt% unloaded MEA, {ctrl['T_K']:.2f} K, {ctrl['P_Pa']:,.0f} Pa and loading {ctrl['loading']:.2f}, "
           f"R2 gives pH {ctrl['pH']:.6f} and raw R1 gives {ctrl['raw_R1_pH']:.6f}. "
           "Use R2 common molality. Each electrode series is compared at its own temperature with figure read-off bounds. "
           "The pressure of the electrode measurements and the difference between electrode and EOS activity scales are unreported. "
           "This comparison cannot attribute the carbonate deficit to one term. "
           "[Matched pH, ion decompositions, and carbonate comparison](results/q5.json) · [Digitization](results/ph-digitization.json).")
    yield table(['Loading (mol/mol)','R2 pH','CO₃²⁻/(CO₃²⁻ + HCO₃⁻)'],((r['loading'],number(r['pH']),number(r['carbonate_share'])) for r in grid))
    yield table(['Electrode data','Temperature (K)','Available / measured','Model minus electrode pH (range)'],
                ((source['source'],source['T_K'],f"{len(values)} / {len(source['points'])}",f"{min(values):.2f} to {max(values):.2f}")
                 for source in read('ph-digitization') if (values := [r['model_minus_electrode_pH'] for r in q5['rows']
                    if r['symbol'] and r['symbol']['source']==source['source'] and 'model_minus_electrode_pH' in r])))
    yield table(['Ion at loading 0.30','ln γ (molality)','DH','Born','Remainder'],
                ((name,number(ion['ln_gamma']),*(number(ion['attribution_5dp'][k],'.5f') for k in ('DH','Born','remainder')))
                 for name,ion in ctrl['ions'].items()))
    yield '![Matched electrode and EOS pH on the two temperature series.](results/ph-comparison.svg)'
    yield '## Q6. AMP S14 certificate'
    d = q6['split']['diagnostics']
    yield (f"On the solved pair, the maximum absolute primitive chemical row is "
           f"{max(abs(r['residual']) for r in d['primitive_chemical_rows']):.3g} against {d['primitive_limit']:.1g}. "
           f"The largest reaction and electrochemical residuals are {max(abs(r['residual']) for r in d['reaction_contractions']):.3g} and "
           f"{max(map(abs,d['electrochemical_difference_L2_minus_L1'].values())):.3g}, respectively. "
           f"The {len(d['vapor_trials'])} neutral vapor trials gave minimum TPD/RT {d['vapor_minimum']:.6f}. "
           "Report this minimum only for those trials. [Primitive rows, contraction bounds, trial seeds and errors](results/q6.json).")
    yield '## Q7. Empty-bank search recall'
    yield (f"Native trials recovered {q7['recovered']}/{q7['archived_positive']} archived positives "
           f"({q7['missed']} missed, {q7['positive_unavailable']} unavailable). "
           f"The replay searched {q7['searched']}/{q7['total']} keys, including aliases, and detected {q7['new_detections']} new descents "
           f"among {q7['searched_negatives']} archived negatives. The archived realized pressure matches for {q7['matched_pressure']} keys. "
           f"The archive lacks that field for {q7['missing_archived_pressure']} keys. "
           "[Counts and timing](results/q7-summary.json) · [Replay rows](results/q7-recall.json.gz).")
    yield '## Q8. Retained manuscript statistics'
    dea,mdea,k,phase,amp = (q8[name] for name in ('dea','mdea','kuranov','phase_counts','amp'))
    yield (f"DEA supplement. Start 0 cost {dea['chosen_cost']:.15f} and start 1 cost {dea['alternative_cost']:.15f}. "
           f"Both are within the absolute tie tolerance {dea['absolute_tie_tolerance']:.1g}. Use the start-1 vector "
           f"`{dea['physical']}` in declared order. {dea['disposition'].capitalize()}. "
           f"The MDEA unbounded half-sum of squared weighted residuals is {mdea['cost']:.11f}. "
           "Outside-fit alternative predictions are unavailable in the archive. [Vectors, deviations, and matched rows](results/q8.json).")
    yield table(['Fit and dataset','Fitted rows','AARD (%)','Signed bias (%)'],
                ((fit+' '+r['group'],r['rows'],number(r['AARD_percent']),number(r['bias_percent']))
                 for fit,record in [('DEA start 1',dea),('MDEA unbounded',mdea)] for r in record['scores']))
    yield ('Water supplement. The five frozen water coefficients exactly match F2. '
           '[IAPWS-95 grid conditions, coefficient values and mean/maximum errors](results/q8.json).')
    yield table(['Frozen water coordinate','Value'],((key,number(value,'.15g')) for key,value in q8['water']['coefficients'].items()))
    yield table(['Candidate assessment grid','Property','Evaluated rows','Mean error (%)','Maximum error (%)'],
                ((r['grid'],r['quantity'],r['evaluated_rows'],number(r['mean_percent']),number(r['max_percent']))
                 for r in q8['water']['metrics'] if r['record']=='lambda-0.1-A'))
    yield (f"Kuranov Table 2. {k['counts']['fitted']} fitted and {k['counts']['not fitted']} outside-fit rows, including "
           f"row {k['added_row']['source_row']} at {k['added_row']['T']:.2f} K and {k['added_row']['p_exp']:,.0f} Pa outside fit. "
           f"Present-model AARD is {k['scores']['fitted']['AARD_percent']:.4f}% fitted and {k['scores']['not fitted']['AARD_percent']:.4f}% outside fit.")
    yield (f"MDEA measured states. {phase['attempts']} attempts across {phase['attempted_states']} of {phase['states']} states. "
           f"{phase['converged']} attempts converged, {phase['converged_distinct']} to distinct roots across "
           f"{phase['states_with_converged_distinct']} states, each liquid plus dilute-vapor-connected. "
           f"Confirmed two-liquid count {phase['confirmed_two_liquid']}.")
    yield (f"AMP relative objectives. Degrees of freedom {amp['df'][0]} / {amp['df'][1]}, conditional variance factors "
           f"{amp['residual_variance'][0]:.6f} / {amp['residual_variance'][1]:.6f}, descriptive F {amp['descriptive_F']:.5f}. "
           "Interpret with the declared weights and active-bound coordinates.")
    yield ('Transplanted ion comparison. Use separate sodium laws and the common ionic reference at matched salt, temperature and molality. '
           'Negative charge-closure OH⁻ accounts for the mixed-salt refusals. The residuals constrain inorganic osmotic behavior. '
           '[Common-row statistics, refusals and historical wheel labels](results/q8.json).')
    yield table(['Sodium law / set','NaHCO₃ AARD (%)','Na₂CO₃ AARD (%)','Mixed AARD (%)'],
                ((case,*(number(v['AARD_percent']) for v in groups.values())) for case,groups in q8['salts'].items()))


def ph_plot():
    import matplotlib
    matplotlib.use('Agg')
    from matplotlib import pyplot as plt

    matplotlib.rcParams.update({'svg.hashsalt': 'round-3-ph', 'svg.fonttype': 'none'})
    fig, axes = plt.subplots(1,2,figsize=(7.4,3.5),sharex=True,sharey=True,layout='constrained')
    model = read('q5')['rows']
    for ax, source, title in zip(axes,read('ph-digitization'),('Hartono and Svendsen, 40 °C','Matin et al., 21 °C'),strict=True):
        data = [r for r in model if r['symbol'] and r['symbol']['source']==source['source']]
        ax.errorbar([r['loading'] for r in data],[r['symbol']['pH'] for r in data],
                    xerr=source['loading_read_off'],yerr=source['pH_read_off'],
                    fmt='o',markersize=2.5,mfc='white',mec='#2b2b2b',ecolor='#707070',alpha=.8,label='Electrode (read-off bounds)')
        available = [r for r in data if r.get('pH') is not None]
        ax.scatter([r['loading'] for r in available],[r['pH'] for r in available],
                   marker='+',s=14,color='#0072b2',label='F2 R2 activity at 101.325 kPa')
        ax.set(title=title,xlabel='Loading (mol CO₂/mol MEA)')
        ax.grid(alpha=.2)
    axes[0].set_ylabel('pH')
    axes[0].legend(loc='lower left',fontsize=8)
    output = StringIO()
    fig.savefig(output,format='svg',metadata={'Date':None})
    plt.close(fig)
    return output.getvalue()


if __name__=='__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--check',action='store_true')
    args = parser.parse_args()
    generated = {'manuscript-handoff.md':'\n\n'.join(handoff())+'\n', 'results/ph-comparison.svg':ph_plot()}
    for name, content in generated.items():
        path = HERE/name
        if args.check:
            if not path.is_file() or path.read_text()!=content:
                raise SystemExit(f'{path} is stale')
        else:
            path.write_text(content)
