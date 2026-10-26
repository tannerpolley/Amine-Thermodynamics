"""Render the manuscript figures from the retained Engine 3e83e19c states and model curves of #212-#215 (#211); no Engine compute."""
import ast
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
CURVES = a.E / 'model-curves'
SPECIES_LINES = ((0, (5, 2)), ':')  # #205: dashed; dotted and lighter below the bubble pressure; an unavailable comparison has no style and fails



def save(fig, name, caption, inputs):
    OUT.mkdir(parents=True, exist_ok=True)
    fig.savefig(OUT / (name + '.pdf'), metadata={'CreationDate': None, 'ModDate': None})
    fig.savefig(OUT / (name + '.png'), dpi=200)
    OUTPUTS[name] = dict(files=[name + '.pdf', name + '.png'], caption=caption, inputs=inputs)
    plt.close(fig)


def curve(ax, rows, quantity, color, scale=1., styles=((0, ()), (0, (8, 3)), ':'), below_alpha=None):
    """Model curve over its ordered states, with gaps at unavailable states; each segment takes its less certain end's style (default below the bubble pressure: dashed; comparison unavailable: dotted)."""
    part = sorted((r for r in rows if r['quantity'] == quantity), key=lambda r: float(r['analytical_loading']))
    x = [float(r['analytical_loading']) for r in part]
    y = [float(r['value'])*scale if r['status'] == 'available' else math.nan for r in part]
    rank = [{'False': 0, 'True': 1}.get(r.get('below_bubble_pressure', 'False'), 2) for r in part]
    for style, run in groupby(range(len(x) - 1), key=lambda i: max(rank[i], rank[i+1])):
        i = list(run)
        ax.plot(x[i[0]:i[-1]+2], y[i[0]:i[-1]+2], color=color, lw=1, ls=styles[style], alpha=below_alpha if style == 1 else None)


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
        curve(top, [r for r in curves if float(r['temperature_K']) == T], 'CO2 partial pressure', color, 1e-3, styles=SPECIES_LINES, below_alpha=.5)
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
    handles = [Line2D([], [], color=c, ls=SPECIES_LINES[0], label=f'{T:g} K') for T, c in zip(isotherms, COLORS)]
    handles += [Line2D([], [], marker=m, markerfacecolor='none', color='black', linestyle='none', label=SOURCE_NAMES[s]) for s, m in zip(sources, MARKERS)]
    handles += [Line2D([], [], marker='s', markerfacecolor=f, color='black', linestyle='none', label=l) for f, l in (('black', 'Fitted'), ('none', 'Not fitted'))]
    top.legend(handles=handles, title='Dashed: calculated; markers: measured', title_fontsize=8, loc='lower right', ncol=2, fontsize=8, frameon=False)
    save(fig, 'pressure', 'CO2 partial pressure of the bubble-point vapor of 30 wt% MEA against analytical loading: dashed model curves on five isotherms and the canonical and Wagner measurements, each assigned to the isotherm within 2 K. The lower panel gives calculated-minus-measured deviations at the measured states from the retained point predictions. Pa converted to kPa; sources differ slightly from the nominal 30 wt% solvent.', ['canonical-pressure.csv','wagner-pressure.csv','pressure-figure-data.csv','fitted-rows.csv','model-curves/pressure.csv'])
    membership = a.rows(a.ROOT/'data/reference/MEA/manifests/speciation_target_membership.csv')
    loading = {r['membership_id'].replace('|', '::'): float(r['co2_loading_mol_per_mol_mea']) for r in membership}
    species = list({r['target']: r for r in a.rows(a.E/'species-figure-data.csv')}.values())  # Matin rows de-duplicated by target identity
    assert all(r['basis'] in {'true-species-liquid-mole-fraction','true-species-liquid-mole-fraction-linear-aggregate'} for r in species)
    for r in species:  # fitted status rule (#205): all fitted except the 353.15 K Böttinger states and Matin's HCO3- + CO3^2- totals
        assert (r['target'] in fitted_ids) == (float(r['temperature_K']) < 350 and (r['source'], r['species']) != ('Matin2012', 'HCO3-')), r['target']
    curves, temperatures = a.rows(CURVES/'species.csv'), [293.15, 313.15, 333.15, 353.15]
    at = lambda T: [r for r in curves if float(r['temperature_K']) == T]
    shapes = {'MEA + MEAH+': 'o', 'MEACOO-': 's', 'MEAH+': '^', 'MEA': 'D', 'HCO3-': 'v'}  # one shape per species; fill = source
    tcolor = dict(zip(temperatures, plt.colormaps['plasma']([0, .33, .6, .82])))  # cold to warm, luminance rising for grayscale
    quantity = lambda name: {'HCO3-': 'HCO3- + CO3^2-'}.get(name, name)
    marks = lambda ax, rows, x, y, color: [points(ax, [x(r)], [y(r)], shapes[r['species']], color(r), r['source'] == 'Bottinger2008') for r in rows]
    source = [Line2D([], [], marker='o', ls='none', color='black', markerfacecolor=f, label=l) for f, l in (('black', 'Filled: NMR (Böttinger)'), ('none', 'Open: titration (Matin)'))]
    shape = [Line2D([], [], marker=m, ls='none', color='black', markerfacecolor='none', label=SPECIES_NAMES[n]) for n, m in shapes.items()]
    legend = lambda top, **k: fig.legend(handles=[h for pair in zip(top + source[:1], shape + source[1:]) for h in pair], loc='outside lower center', ncol=6, fontsize=7.5,
                                         frameon=False, handlelength=1.8, columnspacing=1, **k)  # rows: temperature and line keys, species shapes; source last
    temperature_key = lambda **k: [Line2D([], [], color=tcolor[T], label=f'{T-273.15:.0f} °C' + (' (31 wt%)' if T > 350 else ''), **k) for T in temperatures]
    fig = plt.figure(figsize=(FULL_WIDTH, 5.2), layout='constrained')
    grid = fig.add_gridspec(2, 3, width_ratios=[1.35, 1, 1])
    ax = fig.add_subplot(grid[:, 0])
    for name, (x, offset, align) in {'MEA + MEAH+': (.53, (0, 22), ('center', 'bottom')), 'MEAH+': (.6, (4, 0), ('left', 'center')), 'MEACOO-': (.6, (4, 0), ('left', 'center')),
                                     'HCO3-': (.27, (0, 5), ('center', 'bottom')), 'MEA': (.6, (4, 0), ('left', 'center'))}.items():  # where each curve stands apart
        curve(ax, at(313.15), quantity(name), 'black', styles=SPECIES_LINES, below_alpha=.5)
        y = float(min((r for r in at(313.15) if r['quantity'] == quantity(name)), key=lambda r: abs(float(r['analytical_loading']) - x))['value'])
        ax.annotate(SPECIES_NAMES[name], (x, y), xytext=offset, textcoords='offset points', ha=align[0], va=align[1], fontsize=8, arrowprops=dict(arrowstyle='-', lw=.5) if offset[1] > 10 else None)
    marks(ax, [r for r in species if float(r['temperature_K']) == 313.15], lambda r: loading[r['target']], lambda r: float(r['observed']), lambda r: 'black')
    ax.set(title='(a) Speciation at 40 °C', xlabel=LOADING, ylabel='Liquid mole fraction', xlim=(0, .8), xticks=[0, .2, .4, .6])
    for (row, col), name, label in (((0, 1), 'MEA + MEAH+', '(b)'), ((0, 2), 'MEACOO-', '(c)'), ((1, 1), 'MEAH+', '(d)'), ((1, 2), 'HCO3-', '(e)')):
        ax = fig.add_subplot(grid[row, col])
        for T in temperatures:
            curve(ax, at(T), quantity(name), tcolor[T], styles=SPECIES_LINES, below_alpha=.5)
        marks(ax, [r for r in species if r['species'] == name], lambda r: loading[r['target']], lambda r: float(r['observed']), lambda r: tcolor[float(r['temperature_K'])])
        ax.set(title=f'{label} {SPECIES_NAMES[name]}', xlabel='Loading' if row else None)
    ax.set(yscale='log', ylim=(1e-5, 3e-2))
    for ax in fig.axes:
        ax.grid(alpha=.15)
    legend(temperature_key(ls=SPECIES_LINES[0]) + [Line2D([], [], color='black', ls=':', alpha=.5, label='Below bubble pressure')])
    save(fig, 'speciation', 'True-species liquid mole fractions of loaded MEA against analytical loading: (a) all reported species at 313.15 K; (b)-(e) one species or aggregate at four temperatures. Dashed lines are single liquids imposed at 101 325 Pa (31 wt% MEA at 353.15 K), dotted where below their bubble pressure; markers are Böttinger NMR (filled) and Matin titration (open) measurements, shaped by species.', ['species-figure-data.csv','fitted-rows.csv','model-curves/species.csv'])
    fig, axes = plt.subplots(1, 2, figsize=(FULL_WIDTH, 4.2), layout='constrained')
    for ax, names, limits, scale, title in ((axes[0], {'MEA + MEAH+', 'MEACOO-', 'MEAH+', 'MEA'}, (0, .12), 'linear', '(a) Amine species'), (axes[1], {'HCO3-'}, (1e-4, 2e-2), 'log', '(b) ' + SPECIES_NAMES['HCO3-'])):
        marks(ax, [r for r in species if r['species'] in names], lambda r: float(r['observed']), lambda r: float(r['predicted']), lambda r: tcolor[float(r['temperature_K'])])
        ax.plot(limits, limits, color='black', lw=.7)
        for factor in (.9, 1.1):
            ax.plot(limits, [factor*v for v in limits], color='black', ls=':', lw=.6)
        ax.set(xlim=limits, ylim=limits, xscale=scale, yscale=scale, box_aspect=1, title=title, xlabel='Measured mole fraction', ylabel='Calculated mole fraction')
        ax.grid(alpha=.15)
    legend(temperature_key(marker='o', ls='none') + [Line2D([], [], color='black', ls=':', lw=.6, label='±10 %')])
    save(fig, 'species-parity', 'Calculated against measured true-species liquid mole fractions at the measured states, from the retained point predictions: (a) amine species, (b) HCO3− + CO3²− totals on logarithmic axes. Solid line 1:1, dotted ±10 %. Shape, color and fill as in the speciation figure.', ['species-figure-data.csv','fitted-rows.csv'])
    fig, ax = plt.subplots(figsize=(FULL_WIDTH, 3.8), layout='constrained')
    curves, handles = a.rows(CURVES/'heat.csv'), []
    for (T, P, source, marker), color in zip([(313.15, 1734000., 'Vinjarapu2024', 'o'), (322.5, 510000., 'Arcis2011', 's'), (322.5, 1030000., 'Arcis2011', '^')], COLORS):
        curve(ax, [r for r in curves if float(r['temperature_K']) == T and float(r['pressure_Pa']) == P], 'integral heat of absorption', color, styles=SPECIES_LINES, below_alpha=.5)
        part = [r for r in heat if r['source'] == source and float(r['P_Pa']) == P]
        assert {float(r['T_K']) for r in part} == {T}
        points(ax, [float(r['loading']) for r in part], [float(r['observed_kJ_mol']) for r in part], marker, color, source == 'Vinjarapu2024')
        handles.append(Line2D([], [], color=color, ls=SPECIES_LINES[0], marker=marker, markerfacecolor=color if source == 'Vinjarapu2024' else 'none',
                              label=f"{SOURCE_NAMES[source]}, {T:g} K, {P/1e6:g} MPa ({'fitted' if source == 'Vinjarapu2024' else 'not fitted'})"))
    ax.set(xlabel=LOADING, ylabel=r'Integral heat of absorption (kJ/mol CO$_2$)')
    ax.grid(alpha=.15)
    fig.legend(handles=handles, title='Dashed: calculated; markers: measured', title_fontsize=8, fontsize=8, frameon=False, loc='outside lower center', ncol=2)
    save(fig, 'heat-of-absorption', 'Integral heat of absorption of CO2 into 30 wt% MEA from zero loading, per mole of CO2 absorbed; negative values are exothermic. Dashed model curves at the three measured temperature-pressure conditions with the Vinjarapu (fitted) and Arcis (not fitted) measurements. Both liquids are equilibrium liquids and the CO2 feed is pure CO2 vapor at the same temperature and pressure.', ['heat.csv','model-curves/heat.csv'])
    by_id={r['id']:r for r in a.rows(a.E/'comparison-loaded-density-errors.csv')}  # comparison fit at the same 47 fitted loaded states
    loaded=[r for r in density if r['id'] in spec['loaded_density_ids']]
    assert len(by_id)==len(loaded)==47
    for r in loaded:
        assert all(float(r[k])==float(by_id[r['id']][k]) for k in ['T_K','P_Pa','observed_kg_m3','s_kg_m3']) and math.isclose(float(r['loading']),float(by_id[r['id']]['loading']),rel_tol=1e-12)
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

    save(fig,'loaded-density-errors','The reported and comparison fits share the 47 fitted loaded-density states, observed values and scales. Top panels show ±2s limits only for that fitted cohort; color denotes loading, with source separated. Bottom panels cover all 210 reported-fit densities and distinguish fitted, non-fitted and excluded rows. No empirical volume translation. Scales are not uniformly measurement uncertainty; 2s is not a 95% interval.', ['density.csv','fitted-rows.csv','comparison-loaded-density-errors.csv'])
    fig, ax = plt.subplots(figsize=(FULL_WIDTH, 3.8), layout='constrained')
    temperatures, curves = [298.15, 313.15, 333.15, 353.15, 373.15, 393.15], a.rows(CURVES/'density.csv')
    data = [r for r in density if r['mea_mass_fraction'] == '0.3' and float(r['T_K']) in temperatures]
    sources, fitted_density = sorted({r['source'] for r in data}), set(spec['loaded_density_ids']) | free
    for T, color in zip(temperatures, COLORS):
        curve(ax, [r for r in curves if float(r['temperature_K']) == T], 'liquid density', color, styles=SPECIES_LINES, below_alpha=.5)
        for source, marker in zip(sources, MARKERS):
            for fill in (True, False):
                part = [r for r in data if float(r['T_K']) == T and r['source'] == source and (r['id'] in fitted_density) == fill]
                points(ax, [float(r['loading']) for r in part], [float(r['observed_kg_m3']) for r in part], marker, color, fill)
    handles = [Line2D([], [], color=c, ls=SPECIES_LINES[0], label=f"{T:g} K, {0.7 if T > 364 else 0.1:g} MPa") for T, c in zip(temperatures, COLORS)]
    handles += [Line2D([], [], marker=m, markerfacecolor='none', color='black', linestyle='none', label=SOURCE_NAMES[s]) for s, m in zip(sources, MARKERS)]
    handles += [Line2D([], [], marker='o', markerfacecolor=f, color='black', linestyle='none', label=l) for f, l in (('black', 'Fitted'), ('none', 'Not fitted'))]
    fig.legend(handles=handles + [Line2D([], [], color='black', ls=SPECIES_LINES[1], alpha=.5, label='Below bubble pressure')], title='Dashed: calculated\nMarkers: measured', title_fontsize=8, fontsize=8, frameon=False, loc='outside right upper')
    ax.set(xlabel=LOADING, ylabel='Liquid density (kg/m³)')
    ax.grid(alpha=.15)
    save(fig, 'density-curves', 'Liquid density of 30 wt% MEA against analytical loading: dashed model curves at six temperatures and the 30 wt% measurements at those temperatures. Single liquids are imposed at 0.1 MPa up to 353.15 K and at 0.7 MPa at 373.15 and 393.15 K, as in the retained Han comparison; zero loading carries exactly zero carbon. Dotted, lighter segments lie below their bubble pressure. No empirical volume translation.', ['density.csv','fitted-rows.csv','model-curves/density.csv'])
    fig, ax = plt.subplots(figsize=(FULL_WIDTH, 3.6), layout='constrained')
    curves, cai, handles = a.rows(CURVES/'mea-water.csv'), [ast.literal_eval(r['declaration']) for r in fitted if r['group'] == 'Cai'], []
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
    # Separate fits: every plotted value is calculated with the reported parameters.
    assert a.load(a.E/'water-summary.json')['parameter_sha256'] == fit['record_sha256']
    water = a.rows(a.E/'water.csv')
    fig, axes = plt.subplots(1, 3, figsize=(FULL_WIDTH, 2.7), layout='constrained', sharex=True)
    for ax, column, title in zip(axes, ['saturated_liquid_rho_error_relative', 'psat_error_relative', 'cp_error_relative'], ['(a) Saturated-liquid density', '(b) Saturation pressure', r'(c) $C_P$ at 0.3 and 0.101 MPa']):
        for grid, marker, filled in (('primary', 'o', True), ('staggered', 'o', False), ('atmospheric-controls', '^', True)):
            part = [r for r in water if r['grid'] == grid and r[column] not in ('', 'nan')]
            points(ax, [float(r['T_K']) for r in part], [100*float(r[column]) for r in part], marker, COLORS[0], filled)
        ax.axhline(0, color='grey', lw=.6)
        ax.set(title=title, xlabel='Temperature (K)')
        ax.grid(alpha=.15)
    axes[0].set_ylabel('(calc. − IAPWS-95)/IAPWS-95 (%)')
    fig.legend(handles=[Line2D([], [], marker=m, ls='none', color=COLORS[0], markerfacecolor=COLORS[0] if f else 'none', label=l) for m, f, l in
                        (('o', True, 'Fitted, 0.3 MPa or saturation'), ('o', False, 'Not fitted, interleaved temperatures'), ('^', True, 'Fitted, 0.101 MPa'))],
               loc='outside lower center', ncol=3, fontsize=8, frameon=False)
    save(fig, 'water-iapws', 'Relative deviations of the pure-water parameters from IAPWS-95 at the 20 fitted temperatures, 19 interleaved temperatures and three atmospheric heat-capacity states.', ['water.csv'])
    kiepe = [dict(r, state=ast.literal_eval(r['declaration'])) for r in fitted if r['group'] == 'Kiepe']
    temperatures = sorted({round(r['state']['T_K'], 1) for r in kiepe})
    tcolor = dict(zip(temperatures, plt.colormaps['plasma']([.82*i/(len(temperatures)-1) for i in range(len(temperatures))])))
    fig, axes = plt.subplots(1, 2, figsize=(FULL_WIDTH, 3.0), layout='constrained')
    for r in kiepe:
        T, x = round(r['state']['T_K'], 1), r['state']['feed']['carbon-dioxide']
        points(axes[0], [x], [float(r['observed'])/1e6], 'o', tcolor[T], False)
        axes[0].scatter([x], [float(r['predicted'])/1e6], marker='x', color=tcolor[T], s=18, linewidths=.7, zorder=3)
        points(axes[1], [float(r['observed'])/1e6], [100*(float(r['predicted'])/float(r['observed'])-1)], 'o', tcolor[T], True)
    axes[0].set(xlabel=r'Liquid CO$_2$ mole fraction', ylabel='Total pressure (MPa)', title='(a) Bubble pressure')
    axes[1].axhline(0, color='grey', lw=.6)
    axes[1].set(xlabel='Measured pressure (MPa)', ylabel='(calc. − meas.)/meas. (%)', title='(b) Deviation')
    for ax in axes:
        ax.grid(alpha=.15)
    fig.legend(handles=[Line2D([], [], marker='o', ls='none', color=tcolor[T], label=f'{T:g} K') for T in temperatures] +
                       [Line2D([], [], marker=m, ls='none', color='black', markerfacecolor='none', label=l) for m, l in (('o', 'Measured'), ('x', 'Calculated'))],
               loc='outside right upper', fontsize=8, frameon=False)
    save(fig, 'co2-water', 'Bubble pressure of CO2-water at the 39 Kiepe et al. (2002) states, measured and calculated at the same temperature and liquid composition, with relative deviations.', ['fitted-rows.csv'])
    permittivity = a.E/'permittivity'
    assert a.load(permittivity/'summary.json')['parameter_sha256'] == fit['record_sha256']
    rows = a.rows(permittivity/'rows.csv')
    fig, axes = plt.subplots(1, 2, figsize=(FULL_WIDTH, 2.8), layout='constrained')
    w = [float(r['MEA_wt_percent']) for r in rows]
    points(axes[0], w, [float(r['observed_epsilon']) for r in rows], 'o', COLORS[0], False)
    axes[0].scatter(w, [float(r['calculated_epsilon']) for r in rows], marker='x', color=COLORS[0], s=18, linewidths=.7, zorder=3)
    points(axes[1], w, [float(r['calculated_epsilon'])-float(r['observed_epsilon']) for r in rows], 'o', COLORS[0], True)
    axes[0].set(xlabel='MEA mass fraction (wt%)', ylabel='Relative permittivity', title='(a) Permittivity at 298.15 K')
    axes[1].axhline(0, color='grey', lw=.6)
    axes[1].set(xlabel='MEA mass fraction (wt%)', ylabel='Calc. − meas.', title='(b) Deviation')
    for ax in axes:
        ax.grid(alpha=.15)
    axes[0].legend(handles=[Line2D([], [], marker=m, ls='none', color=COLORS[0], markerfacecolor='none', label=l) for m, l in (('o', 'Measured'), ('x', 'Calculated'))], fontsize=8, frameon=False)
    save(fig, 'mea-permittivity', 'Relative permittivity of unloaded MEA-water at 298.15 K and 101325 Pa: the 14 Agieienko-Buchner measurements and the solvent law at the equation-of-state density, with the reported parameters.', ['permittivity/rows.csv'])
    # One 162-state grid (#214), the same states for both fits; the reference pressures are the reported fit's bubble pressures.
    temperatures = sorted({float(r['temperature_K']) for r in paired['reported'].values()})
    fractions = sorted({float(r['fraction']) for r in paired['reported'].values()})
    positions = {T: i for i, T in enumerate(temperatures)}
    fig, axes = plt.subplots(2, len(fractions), figsize=(FULL_WIDTH, 4.7), layout='constrained', sharex=True, sharey=True)
    for row, record in enumerate(['comparison', 'reported']):
        for r in paired[record].values():
            resolved = int(r['resolved_trials']) > 0
            axes[row, fractions.index(float(r['fraction']))].scatter(positions[float(r['temperature_K'])], float(r['loading']), marker='s' if 'single-liquid' in r['classification'] else 'o', s=30,
                                                                       facecolors='#D55E00' if resolved else 'none', edgecolors='#D55E00' if resolved else '#0072B2')
        for fraction, ax in zip(fractions, axes[row]):
            ax.set(title=('Comparison fit' if row == 0 else 'Reported parameters') + f'\nP = {fraction:.2f} P*', xlabel='Temperature (K)')
            ax.set_xticks(range(len(temperatures)), labels=[f'{T:g}' for T in temperatures], rotation=45, ha='right')
            ax.set_yticks([1e-5, .1, .3, .5, .6], labels=[r'$10^{-5}$', '0.1', '0.3', '0.5', '0.6'])
            ax.grid(alpha=.15)
        axes[row, 0].set_ylabel(LOADING)
    n = len(paired['reported'])
    descents = {name: sum(int(r['resolved_trials']) > 0 for r in part.values()) for name, part in paired.items()}
    fig.suptitle(f"Detected instabilities: comparison fit {descents['comparison']}/{n}; reported parameters {descents['reported']}/{n}", fontsize=10)
    single = any('single-liquid' in r['classification'] for part in paired.values() for r in part.values())
    fig.supxlabel('Filled: instability detected; open: none' + ('\nSquares: single liquid; circles: liquid + vapor' if single else '; all states liquid + vapor'), fontsize=8)
    save(fig, 'phase-family', f"{n} temperature/pressure/loading states at six temperatures, comparison fit versus reported parameters: {descents['comparison']}/{n} and {descents['reported']}/{n} resolved-descent states. Columns show 0.50, 0.80 and 0.95 times reference pressures equal to the reported fit's bubble pressures. Finite searches do not certify a continuous stable region.", ['phase-family.csv'])
    comparison = a.load(a.E/'comparison-score.json')
    records = dict(reported=a.record_identity(fit['record_sha256'], fit['engine']), comparison=a.record_identity(comparison['parameter_sha256'], fit['engine']))
    for name, output in OUTPUTS.items():
        output['records'] = {key: records[key] for key in (['reported', 'comparison'] if name in ('phase-family', 'loaded-density-errors') else ['reported'])}
    a.inventoried()
    provenance=dict(generator=str(a.bind(a.ROOT/'analyses/mea_parameter_bundle/scripts/render_manuscript_figures.py').relative_to(a.ROOT)),
                    records=records, inputs=dict(sorted(a.INPUTS.items())),outputs=OUTPUTS)
    (OUT/'provenance.json').write_text(json.dumps(provenance,indent=2,sort_keys=True)+'\n')
    print(f'Wrote {len(OUTPUTS)} PDF/PNG figures and provenance.json from retained states and model curves.')


if __name__=='__main__':
    main()
