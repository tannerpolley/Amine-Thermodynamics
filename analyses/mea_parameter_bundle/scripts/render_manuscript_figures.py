"""Render the manuscript figures from retained states and the retained model curves (#197, #202); no Engine compute."""
import json
import math
from itertools import groupby

import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.lines import Line2D

import a7_presentation as a
from manuscript_style import FULL_WIDTH, apply_style

OUT = a.ROOT / 'docs/scientific/latex/figures/generated'
COLORS = ['#0072B2', '#D55E00', '#009E73', '#CC79A7', '#7B5D00', '#006B75', '#555555']
LOADING = r'Loading (mol CO$_2$/mol MEA)'
OUTPUTS = {}
MARKERS = ['o', 's', '^', 'v', 'D', 'P', '*']
SOURCE_NAMES = {'Bottinger2008':'Böttinger et al. (2008)', 'Matin2012':'Matin et al. (2012)', 'Vinjarapu2024':'Vinjarapu et al. (2024)', 'Arcis2011':'Arcis et al. (2011)', 'Amundsen2009':'Amundsen et al. (2009)', 'Hartono2014':'Hartono et al. (2014)', 'Han2012':'Han et al. (2012)', 'Aronu2011':'Aronu et al. (2011)', 'Hilliard2008':'Hilliard (2008)', 'Idris2014':'Idris et al. (2014)', 'Jou1995':'Jou et al. (1995)', 'Mamun2005':"Ma’mun et al. (2005)", 'Wagner2013':'Wagner et al. (2013)', 'Xu2011':'Xu and Rochelle (2011)'}
SPECIES_NAMES = {'MEA':r'MEA', 'MEAH+':r'MEAH$^+$', 'MEACOO-':r'MEACOO$^-$', 'MEA + MEAH+':r'MEA + MEAH$^+$', 'HCO3-':r'HCO$_3^-$ + CO$_3^{2-}$', 'HCO3- + CO3^2-':r'HCO$_3^-$ + CO$_3^{2-}$'}
CURVES = a.BUNDLE / 'results/model-curves'
DASHED = 'Dashed: imposed single liquid below its bubble pressure'
UNKNOWN = lambda rows: any(r.get('below_bubble_pressure') == 'unavailable' for r in rows)



def save(fig, name, caption, inputs):
    OUT.mkdir(parents=True, exist_ok=True)
    fig.savefig(OUT / (name + '.pdf'), metadata={'CreationDate': None, 'ModDate': None})
    fig.savefig(OUT / (name + '.png'), dpi=200)
    OUTPUTS[name] = dict(files=[name + '.pdf', name + '.png'], caption=caption, inputs=inputs)
    plt.close(fig)


def curve(ax, rows, quantity, color, scale=1., dashes=()):
    """Model curve over its ordered states, with gaps at unavailable states; each segment takes its less certain end's style (below the bubble pressure: dashed; comparison unavailable: dotted)."""
    part = sorted((r for r in rows if r['quantity'] == quantity), key=lambda r: float(r['analytical_loading']))
    x = [float(r['analytical_loading']) for r in part]
    y = [float(r['value'])*scale if r['status'] == 'available' else math.nan for r in part]
    rank = [{'False': 0, 'True': 1}.get(r.get('below_bubble_pressure', 'False'), 2) for r in part]
    for style, run in groupby(range(len(x) - 1), key=lambda i: max(rank[i], rank[i+1])):
        i = list(run)
        ax.plot(x[i[0]:i[-1]+2], y[i[0]:i[-1]+2], color=color, lw=1, ls=((0, dashes), (0, (8, 3) + dashes), ':')[style])


def points(ax, x, y, marker, color, filled):
    ax.scatter(x, y, marker=marker, facecolors=color if filled else 'none', edgecolors=color, s=18, linewidths=.7, zorder=3)


def main():
    fit, summary, document, fitted, spec, density, heat, errors, paired = a.checked()
    a.bind(a.BUNDLE/'scripts/manuscript_style.py')
    apply_style()
    fitted_ids = {r['id'] for r in fitted}
    model = a.load(CURVES/'summary.json')
    assert model['parameter_sha256'] == fit['record_sha256'] and all(c['usable'] for f in model['families'].values() for c in f['curves'].values())
    canonical, wagner, packet = [a.rows(a.E / n) for n in ['canonical-pressure.csv', 'wagner-pressure.csv', 'pressure-figure-data.csv']]
    assert len(packet) == 79 and all(r['basis'] == 'true-species-vapor-partial-pressure' for r in canonical+wagner+packet)
    packet_fit = {r['target'] for r in packet if r['target'] in fitted_ids}
    # Measured points at their source analytical loadings, the curve abscissa (the retained loading column is a seeded-amount ratio).
    alpha = {'canonical:'+r['observation_id']: float(r['CO2_loading']) for r in a.rows(a.ROOT/'data/reference/MEA/observations/vapor_liquid_equilibrium/Canonical_VLE_Observations.csv')}
    alpha |= {'Wagner2013:csv-row-'+r['csv_data_row_number']: float(r['loading_mol_CO2_per_mol_MEA']) for r in a.rows(a.BUNDLE/'results/temperature-reanchor-140/never-accessed-vle-admission.csv') if r['admitted'] == 'yes'}
    assert all(abs(alpha[r['identity']] - float(r['loading'])) < 2e-3 for r in canonical+wagner)
    fig, (top, bottom) = plt.subplots(2, 1, figsize=(FULL_WIDTH, 6.4), layout='constrained', sharex=True, height_ratios=[2.3, 1])
    isotherms, sources, curves = [313.15, 333.15, 353.15, 373.15, 393.15], sorted({r['source'] for r in canonical+wagner}), a.rows(CURVES/'pressure.csv')
    for T, color in zip(isotherms, COLORS):
        curve(top, [r for r in curves if float(r['temperature_K']) == T], 'CO2 partial pressure', color, 1e-3)
        for source, marker in zip(sources, MARKERS):
            for fill in (True, False):
                part = [r for r in canonical+wagner if r['source'] == source and abs(float(r['temperature_K'])-T) <= 2 and (r['target'] in packet_fit) == fill]
                points(top, [alpha[r['identity']] for r in part], [float(r['observed'])/1000 for r in part], marker, color, fill)
                points(bottom, [alpha[r['identity']] for r in part], [100*(float(r['predicted'])/float(r['observed'])-1) for r in part], marker, color, fill)
    top.set(yscale='log', ylabel=r'CO$_2$ partial pressure (kPa)')
    bottom.axhline(0, color='grey', lw=.6)
    bottom.set(xlabel=LOADING, ylabel='(calc. − meas.)/meas. (%)')
    for ax in (top, bottom):
        ax.grid(alpha=.15)
    handles = [Line2D([], [], color=c, label=f'{T:g} K') for T, c in zip(isotherms, COLORS)]
    handles += [Line2D([], [], marker=m, markerfacecolor='none', color='black', linestyle='none', label=SOURCE_NAMES[s]) for s, m in zip(sources, MARKERS)]
    handles += [Line2D([], [], marker='s', markerfacecolor=f, color='black', linestyle='none', label=l) for f, l in (('black', 'Fitted'), ('none', 'Not fitted'))]
    top.legend(handles=handles, loc='lower right', ncol=2, fontsize=8, frameon=False)
    save(fig, 'pressure', 'CO2 partial pressure of the bubble-point vapor of 30 wt% MEA against analytical loading: model curves on five isotherms and the canonical and Wagner measurements, each assigned to the isotherm within 2 K. The lower panel gives calculated-minus-measured deviations at the measured states from the retained point predictions. Pa converted to kPa; sources differ slightly from the nominal 30 wt% solvent.', ['canonical-pressure.csv','wagner-pressure.csv','pressure-figure-data.csv','fitted-rows.csv','model-curves/pressure.csv'])
    membership = a.rows(a.ROOT/'data/reference/MEA/manifests/speciation_target_membership.csv')
    loading = {r['membership_id'].replace('|', '::'): float(r['co2_loading_mol_per_mol_mea']) for r in membership}
    species = list({r['target']: r for r in a.rows(a.E/'species-figure-data.csv')}.values())  # Matin rows de-duplicated by target identity
    assert all(r['basis'] in {'true-species-liquid-mole-fraction','true-species-liquid-mole-fraction-linear-aggregate'} for r in species)
    fig, axes = plt.subplots(4, 2, figsize=(FULL_WIDTH, 6.2), layout='constrained', sharex=True, height_ratios=[2, 1, 2, 1])
    curves, handles = a.rows(CURVES/'species.csv'), []
    styles = {'MEA': ('MEA', 'P'), 'MEAH+': ('MEAH+', 'X'), 'MEACOO-': ('MEACOO-', 's'), 'HCO3-': ('HCO3- + CO3^2-', '^'), 'MEA + MEAH+': ('MEA + MEAH+', 'o')}
    colors = dict(zip(['MEA + MEAH+', 'MEACOO-', 'HCO3- + CO3^2-', 'MEA', 'MEAH+'], COLORS))
    dash_patterns = dict(zip(colors, [(), (5, 2), (1, 1), (4, 1, 1, 1), (5, 1, 1, 1, 1, 1)]))
    for panel, T in enumerate([293.15, 313.15, 333.15, 353.15]):
        ax, minor = axes[2*(panel//2), panel%2], axes[2*(panel//2)+1, panel%2]
        for name, color in colors.items():
            curve(ax, [r for r in curves if float(r['temperature_K']) == T], name, color, dashes=dash_patterns[name])
        curve(minor, [r for r in curves if float(r['temperature_K']) == T], 'HCO3- + CO3^2-', colors['HCO3- + CO3^2-'], dashes=dash_patterns['HCO3- + CO3^2-'])
        for source, name in dict.fromkeys((r['source'], r['species']) for r in species):
            marker = styles[name][1] if source == 'Bottinger2008' else {'MEACOO-': 'D', 'HCO3-': 'v'}.get(name, styles[name][1])
            for fill in (True, False):
                part = [r for r in species if (r['source'], r['species']) == (source, name) and float(r['temperature_K']) == T and (r['target'] in fitted_ids) == fill]
                points(ax, [loading[r['target']] for r in part], [float(r['observed']) for r in part], marker, colors[styles[name][0]], fill)
                if name == 'HCO3-':
                    points(minor, [loading[r['target']] for r in part], [float(r['observed']) for r in part], marker, colors[styles[name][0]], fill)
            handles.append(Line2D([], [], marker=marker, markerfacecolor='none', color=colors[styles[name][0]], ls=(0, dash_patterns[styles[name][0]]), label=f'{SPECIES_NAMES[name]}, {SOURCE_NAMES[source]}'))
        ax.set(title=f'{T:g} K, {31 if T > 350 else 30} wt% MEA', ylabel='Liquid mole fraction')
        ax.grid(alpha=.15)
        minor.set(yscale='log', ylim=(1e-5, 2e-2), ylabel=r'HCO$_3^-$ + CO$_3^{2-}$')
        minor.grid(alpha=.15)
    for ax in axes[-1]:
        ax.set_xlabel(LOADING)
    handles = list({h.get_label(): h for h in handles}.values()) + [Line2D([], [], marker='o', markerfacecolor=f, color='black', linestyle='none', label=l) for f, l in (('black', 'Fitted'), ('none', 'Not fitted'))]
    fig.legend(handles=handles, loc='outside upper center', ncol=3, fontsize=8, frameon=False)
    save(fig, 'speciation', 'True-species liquid mole fractions of loaded MEA against analytical loading: model curves and the Böttinger and Matin measurements, with MEA + MEAH+ and HCO3− + CO3²− as the reported aggregates. States are single liquids imposed at 101 325 Pa; the 353.15 K panel uses 31 wt% MEA to match Böttinger’s samples, and its states above loading 0.51 lie below their bubble pressure.', ['species-figure-data.csv','fitted-rows.csv','model-curves/species.csv'])
    fig, ax = plt.subplots(figsize=(FULL_WIDTH, 3.8), layout='constrained')
    curves, handles = a.rows(CURVES/'heat.csv'), []
    for (T, P, source, marker), color in zip([(313.15, 1734000., 'Vinjarapu2024', 'o'), (322.5, 510000., 'Arcis2011', 's'), (322.5, 1030000., 'Arcis2011', '^')], COLORS):
        curve(ax, [r for r in curves if float(r['temperature_K']) == T and float(r['pressure_Pa']) == P], 'integral heat of absorption', color)
        part = [r for r in heat if r['source'] == source and float(r['P_Pa']) == P]
        assert {float(r['T_K']) for r in part} == {T}
        points(ax, [float(r['loading']) for r in part], [float(r['observed_kJ_mol']) for r in part], marker, color, source == 'Vinjarapu2024')
        handles.append(Line2D([], [], color=color, marker=marker, markerfacecolor=color if source == 'Vinjarapu2024' else 'none',
                              label=f"{SOURCE_NAMES[source]}, {T:g} K, {P/1e6:g} MPa ({'fitted' if source == 'Vinjarapu2024' else 'not fitted'})"))
    ax.set(xlabel=LOADING, ylabel=r'Integral heat of absorption (kJ/mol CO$_2$)')
    ax.grid(alpha=.15)
    fig.legend(handles=handles, fontsize=8, frameon=False, loc='outside lower center', ncol=2)
    save(fig, 'heat-of-absorption', 'Integral heat of absorption of CO2 into 30 wt% MEA from zero loading, per mole of CO2 absorbed; negative values are exothermic. Model curves at the three measured temperature-pressure conditions with the Vinjarapu (fitted) and Arcis (not fitted) measurements. Both liquids are equilibrium liquids and the CO2 feed is pure CO2 vapor at the same temperature and pressure.', ['heat.csv','model-curves/heat.csv'])
    a6=a.rows(a.J/'amendment-6/selected-assessment/density.csv')
    by_id={r['id']:r for r in a6}
    loaded=[r for r in density if r['id'] in spec['loaded_density_ids']]
    for r in loaded:
        assert all(r[k]==by_id[r['id']][k] for k in ['T_K','P_Pa','loading','observed_kg_m3','s_kg_m3'])
    fig,axes=plt.subplots(2,2,figsize=(FULL_WIDTH,5.5),layout='constrained')
    for ax,source in zip(axes[0],['Amundsen2009','Hartono2014']):
        for r in [x for x in loaded if x['source']==source]:
            color=plt.colormaps['viridis'](float(r['loading'])/.5)
            ax.scatter(float(r['T_K']),float(r['error_over_s']),color=color,marker='o',s=18)
            ax.scatter(float(r['T_K']),float(by_id[r['id']]['error_over_s']),color=color,marker='x',s=18)
        ax.axhline(2,color='grey',ls='--',lw=.6)
        ax.axhline(-2,color='grey',ls='--',lw=.6)
        ax.set(title=SOURCE_NAMES[source]+'; fitted loaded',xlabel='Temperature (K)',ylabel='Error / scale s')
    excluded=set(summary['density']['Amundsen source-conflict five']['row_ids'])
    free=set(summary['density']['Amundsen CO2-free gate five']['row_ids'])
    for ax,record,group in [(axes[1,0],'Fitted', [r for r in density if r['id'] in set(spec['loaded_density_ids'])|free]),
                            (axes[1,1],'Non-fitted / excluded',[r for r in density if r['id'] not in set(spec['loaded_density_ids'])|free])]:
        for source,color,source_marker in zip(sorted({r['source'] for r in density}),COLORS,MARKERS):
            for marker,is_excluded in [(source_marker,False),('x',True)]:
                part=[r for r in group if r['source']==source and (r['id'] in excluded)==is_excluded]
                if not part:
                    continue
                ax.scatter([float(r['T_K']) for r in part],[float(r['error_kg_m3']) for r in part],marker=marker,color=color,s=12,label=SOURCE_NAMES[source]+(' excluded' if is_excluded else ''))
        ax.set(title=record+' densities',xlabel='Temperature (K)',ylabel='Density error, calc. − obs. (kg/m³)')
        ax.legend(fontsize=8,frameon=False,loc='upper center',bbox_to_anchor=(.5,-.18),ncol=1)
    fig.colorbar(plt.cm.ScalarMappable(norm=plt.Normalize(0,.5),cmap='viridis'),ax=list(axes[0]),label='Loading',shrink=.7)

    save(fig,'loaded-density-errors','A7/A6 share the 47 fitted loaded-density identities, observed values, scales and states. Top panels show ±2s limits only for that fitted cohort; color denotes loading, with source separated. Bottom panels cover all 210 A7 densities and distinguish fitted, non-fitted and excluded rows. No empirical volume translation. Scales are not uniformly measurement uncertainty; 2s is not a 95% interval.', ['density.csv','fitted-rows.csv',str((a.J/'amendment-6/selected-assessment/density.csv').relative_to(a.ROOT))])
    fig, ax = plt.subplots(figsize=(FULL_WIDTH, 3.8), layout='constrained')
    temperatures, curves = [298.15, 313.15, 333.15, 353.15, 373.15, 393.15], a.rows(CURVES/'density.csv')
    data = [r for r in density if r['mea_mass_fraction'] == '0.3' and float(r['T_K']) in temperatures]
    sources, fitted_density = sorted({r['source'] for r in data}), set(spec['loaded_density_ids']) | free
    for T, color in zip(temperatures, COLORS):
        curve(ax, [r for r in curves if float(r['temperature_K']) == T], 'liquid density', color)
        for source, marker in zip(sources, MARKERS):
            for fill in (True, False):
                part = [r for r in data if float(r['T_K']) == T and r['source'] == source and (r['id'] in fitted_density) == fill]
                points(ax, [float(r['loading']) for r in part], [float(r['observed_kg_m3']) for r in part], marker, color, fill)
    handles = [Line2D([], [], color=c, label=f"{T:g} K, {0.7 if T > 364 else 0.1:g} MPa") for T, c in zip(temperatures, COLORS)]
    handles += [Line2D([], [], marker=m, markerfacecolor='none', color='black', linestyle='none', label=SOURCE_NAMES[s]) for s, m in zip(sources, MARKERS)]
    handles += [Line2D([], [], marker='o', markerfacecolor=f, color='black', linestyle='none', label=l) for f, l in (('black', 'Fitted'), ('none', 'Not fitted'))]
    fig.legend(handles=handles + [Line2D([], [], color='black', ls='--', label='Below bubble pressure')] + [Line2D([], [], color='black', ls=':', label='Bubble comparison unavailable')]*UNKNOWN(curves), fontsize=8, frameon=False, loc='outside right upper')
    ax.set(xlabel=LOADING, ylabel='Liquid density (kg/m³)')
    ax.grid(alpha=.15)
    save(fig, 'density-curves', 'Liquid density of 30 wt% MEA against analytical loading: model curves at six temperatures and the 30 wt% measurements at those temperatures. Single liquids are imposed at 0.1 MPa up to 353.15 K and at 0.7 MPa at 373.15 and 393.15 K, as in the retained Han comparison; zero loading carries exactly zero carbon. Dashed segments lie below their bubble pressure. No empirical volume translation.', ['density.csv','fitted-rows.csv','model-curves/density.csv'])
    fig, ax = plt.subplots(figsize=(FULL_WIDTH, 3.6), layout='constrained')
    curves, cai, handles = a.rows(CURVES/'mea-water.csv'), [r for r in a.load(a.ROOT/spec['stage2_rows_path'])['F1'] if r['id'].startswith('cai')], []
    observed = {r['id']: float(r['observed']) for r in fitted if r['group'] == 'Cai'}
    for P, color in zip((101330., 66660.), COLORS):
        state = {}
        for r in (r for r in curves if float(r['pressure_Pa']) == P):  # full ordered grid; unavailable states are gaps in both branches
            state.setdefault(float(r['liquid_mea_mole_fraction']), {})[r['quantity']] = float(r['value']) if r['status'] == 'available' else math.nan
        x = sorted(state)
        ax.plot(x, [state[v]['bubble temperature'] for v in x], color=color)
        ax.plot([1-state[v]['vapor water mole fraction'] for v in x], [state[v]['bubble temperature'] for v in x], color=color, ls='--')
        rows = [r for r in cai if r['P_Pa'] == P and r['quantity'] == 'temperature']
        points(ax, [r['feed']['monoethanolamine'] for r in rows], [observed[r['id']] for r in rows], 'o', color, True)
        points(ax, [1-observed[r['state_id']+'-mole_fraction'] for r in rows], [observed[r['id']] for r in rows], 's', color, True)
        handles += [Line2D([], [], color=color, marker='o', label=f'Liquid, {P/1e3:g} kPa'), Line2D([], [], color=color, ls='--', marker='s', label=f'Vapor, {P/1e3:g} kPa')]
    fig.legend(handles=handles, title='Model (lines) and Cai et al. (1996), fitted', fontsize=8, title_fontsize=8, frameon=False, loc='outside right upper')
    ax.set(xlabel='MEA mole fraction', ylabel='Temperature (K)')
    ax.grid(alpha=.15)
    save(fig, 'mea-water', 'Bubble temperature and incipient vapor composition of the neutral MEA-water binary (no reactions) at 101.33 and 66.66 kPa, over each isobar’s measured liquid range, with the Cai et al. (1996) measurements. Liquid and vapor MEA mole fractions are on the same basis; the vapor value is one minus the retained water mole fraction.', ['fitted-rows.csv','model-curves/mea-water.csv'])
    extension = a.BUNDLE/'results/phase-extension-201/run-3'
    all_phase = a.rows(extension/'phase-family-combined.csv')
    temperatures = sorted({float(r['temperature_K']) for r in all_phase})
    positions = {T:i for i,T in enumerate(temperatures)}
    assert len(temperatures)==6
    fig,axes=plt.subplots(2,3,figsize=(FULL_WIDTH,4.7),layout='constrained',sharex=True,sharey=True)
    for row,record in enumerate(['A6','A7']):
        grid={}
        for r in all_phase:
            if r['record']==record and not (r['family']=='original-73' and int(r['index'])==0):
                grid.setdefault((r['temperature_K'],r['loading']),[]).append(r)
        assert len(grid)==51 and all(len(v)==3 for v in grid.values())
        for group in grid.values():
            for rank,r in enumerate(sorted(group,key=lambda x:float(x['pressure_Pa']))):
                ax=axes[row,rank]
                excluded=r['admitted']=='False'
                resolved=int(r['resolved_trials'])>0
                marker='s' if 'single-liquid' in r['classification'] else 'o'
                if excluded:
                    ax.scatter(positions[float(r['temperature_K'])],float(r['loading']),marker='x',s=30,color='#555555')
                else:
                    assert r['final_success']=='True' and int(r['failed_trial_optimizers'])==0
                    ax.scatter(positions[float(r['temperature_K'])],float(r['loading']),marker=marker,s=30,
                               facecolors='#D55E00' if resolved else 'none',edgecolors='#D55E00' if resolved else '#0072B2')
        for rank,ax in enumerate(axes[row]):
            ax.set(title=('Comparison fit' if row==0 else 'Reported parameters')+f'\nP = {(.50,.80,.95)[rank]:.2f} P*',xlabel='Temperature (K)')
            ax.set_xticks(range(len(temperatures)),labels=[f'{T:g}' for T in temperatures],rotation=45,ha='right')
            ax.set_yticks([1e-5,.1,.3,.5,.6],labels=[r'$10^{-5}$','0.1','0.3','0.5','0.6'])
            ax.grid(alpha=.15)
        axes[row,0].set_ylabel(LOADING)
    assert sum(r['admitted']=='False' for r in all_phase if r['record']=='A7')==21
    assert sum(int(r['resolved_trials'])>0 for r in all_phase if r['record']=='A6')==33
    fig.suptitle('Detected instabilities: comparison fit 33/133; reported parameters 0/133',fontsize=10)
    fig.supxlabel('Filled: instability detected; open: none; crosses: excluded\nReported parameters: squares, single liquid; circles, liquid + vapor',fontsize=8)
    save(fig,'phase-family','133 searched and 21 excluded specified temperature/pressure/loading states at six temperatures, comparison fit versus reported parameters: 33/133 and 0/133 resolved-descent points. Columns show 0.50, 0.80 and 0.95 times fixed reference pressures. States with reference pressure above 10 MPa are excluded. The additional pressure-rounded state is counted but not drawn. Finite searches do not certify a continuous stable region.', ['phase-extension-201/run-3/phase-family-combined.csv'])
    a6_assessment = a.load(a.J/'amendment-6/selected-assessment/provenance.json')
    fixed = a.J/'amendment-7/fixed-study/wheel-8298c602'
    records = dict(A7=a.record_identity(fit['record_sha256'], fit['engine']),
                   A6_assessment=a.record_identity(a6_assessment['parameter_sha256'], a6_assessment['engine']),
                   A6_phase_family=a.phase_identity(fixed/'after-adoption/a6-selected', fit['engine']),
                   A7_phase_family=a.phase_identity(fixed/'restricted-2-endpoint', fit['engine']))
    records['extension_phase_family'] = a.load(extension/'provenance.json')
    for name, output in OUTPUTS.items():
        output['records'] = {key: records[key] for key in (['A6_phase_family','A7_phase_family','extension_phase_family'] if name == 'phase-family' else ['A7','A6_assessment'] if name == 'loaded-density-errors' else ['A7'])}
    provenance=dict(generator=str(a.bind(a.ROOT/'analyses/mea_parameter_bundle/scripts/render_manuscript_figures.py').relative_to(a.ROOT)),
                    records=records, explanation=a.A6_ASSESSMENT_NOTE, inputs=dict(sorted(a.INPUTS.items())),outputs=OUTPUTS)
    (OUT/'provenance.json').write_text(json.dumps(provenance,indent=2,sort_keys=True)+'\n')
    print(f'Wrote {len(OUTPUTS)} PDF/PNG figures and provenance.json from retained states and model curves.')


if __name__=='__main__':
    main()
