"""Render issue 197 A7 manuscript figures at retained states; no Engine compute."""
import json

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


def save(fig, name, caption, inputs):
    OUT.mkdir(parents=True, exist_ok=True)
    fig.savefig(OUT / (name + '.pdf'), metadata={'CreationDate': None, 'ModDate': None})
    fig.savefig(OUT / (name + '.png'), dpi=200)
    OUTPUTS[name] = dict(files=[name + '.pdf', name + '.png'], caption=caption, inputs=inputs)
    plt.close(fig)


def measured(ax, part, color, label, fitted):
    for marker, member in [('o', True), ('s', False)]:
        rows = [r for r in part if (r['target'] in fitted) == member]
        ax.scatter([float(r['loading']) for r in rows], [float(r['observed']) for r in rows],
                   marker=marker, facecolors='none', edgecolors=color, s=16, linewidths=.7,
                   label=label if member else None)
    ax.scatter([float(r['loading']) for r in part], [float(r['predicted']) for r in part],
               marker='x', color=color, s=12, linewidths=.7)


def main():
    fit, summary, document, fitted, spec, density, heat, errors, paired = a.checked()
    a.bind(a.BUNDLE/'scripts/manuscript_style.py')
    apply_style()
    fitted_ids = {r['id'] for r in fitted}
    canonical, wagner, packet = [a.rows(a.E / n) for n in ['canonical-pressure.csv', 'wagner-pressure.csv', 'pressure-figure-data.csv']]
    assert len(packet) == 79 and all(r['basis'] == 'true-species-vapor-partial-pressure' for r in canonical+wagner+packet)
    packet_fit = {r['target'] for r in packet if r['target'] in fitted_ids}
    fig, axes = plt.subplots(3, 3, figsize=(FULL_WIDTH, 7.2), layout='constrained')
    panels = [40, 60, 80, 100, 120]
    sources = sorted({r['source'] for r in canonical+wagner})
    configurations = [('canonical', t) for t in panels] + [('wagner', 80), ('wagner', 120)]
    for ax, (view, t) in zip(axes.flat, configurations):
        part = [dict(r, observed=float(r['observed'])/1000, predicted=float(r['predicted'])/1000)
                for r in (canonical if view=='canonical' else wagner) if min(panels, key=lambda x: abs(x-(float(r['temperature_K'])-273.15))) == t]
        for source, color in zip(sources, COLORS):
            measured(ax, [r for r in part if r['source'] == source], color, source, packet_fit)
        ax.set(title=('Wagner, ' if view=='wagner' else '')+f'{t} °C (nominal)', xlabel=LOADING, yscale='log', ylabel=r'$p_{CO_2}$ (kPa)')
        ax.grid(alpha=.15)
    axes.flat[-1].set_axis_off()
    handles = [Line2D([], [], marker='o', markerfacecolor='none', color=c, linestyle='none', label=s) for s,c in zip(sources,COLORS)]
    handles += [Line2D([], [], marker=m, markerfacecolor='none', color='black', linestyle='none', label=meaning)
                for m,meaning in [('o','Observed, fitted'),('s','Observed, not fitted'),('x','A7 at measured state')]]
    axes.flat[-2].set_axis_off()
    axes.flat[-2].legend(handles=handles, loc='center', frameon=False, fontsize=7)
    save(fig,'pressure','Canonical and Wagner pressure views only; packet view establishes fitted IDs and is not appended. Pa converted to kPa. Nominal temperatures group retained measured states; Wagner was assessed after acceptance and previously accessed. No phase claim above 333.15 K or loading 0.5.', ['canonical-pressure.csv','wagner-pressure.csv','pressure-figure-data.csv','fitted-rows.csv'])
    species, pool = a.rows(a.E/'species-figure-data.csv'), a.rows(a.E/'pool-figure-data.csv')
    assert len(pool)==19 and not any(r['target'] in fitted_ids for r in pool)
    assert all(r['basis'] in {'true-species-liquid-mole-fraction','true-species-liquid-mole-fraction-linear-aggregate'} for r in species+pool)
    fig, axes = plt.subplots(2,3,figsize=(FULL_WIDTH,5.4),layout='constrained')
    groups = [('Matin2012',20)]+[('Bottinger2008',t) for t in [20,40,60,80]]
    names = sorted({r['species'] for r in species})
    for ax,(source,t) in zip(axes.flat,groups):
        for name,color in zip(names,COLORS):
            part=[r for r in species if r['source']==source and round(float(r['temperature_K'])-273.15)==t and r['species']==name]
            measured(ax,part,color,name,fitted_ids)
        ax.set(title=f'{source}, {t} °C',xlabel=LOADING,ylabel='Liquid mole fraction')
        ax.grid(alpha=.15)
    ax=axes.flat[-1]
    measured(ax,pool,'#0072B2','Matin pool',set())
    ax.set(title='Matin pool, report-only (19)',xlabel=LOADING,ylabel=r'HCO$_3^-$ + CO$_3^{2-}$ mole fraction')
    handles=[Line2D([],[],marker='o',color=c,linestyle='none',label=(r'HCO$_3^-$ + CO$_3^{2-}$ pool' if n=='HCO3-' else n)) for n,c in zip(names,COLORS)]
    fig.legend(handles=handles,fontsize=7,frameon=False,loc='outside upper center',ncol=3)
    fig.supxlabel('Open circles: fitted; open squares: not fitted; crosses: A7',fontsize=8)
    save(fig,'speciation','Species observation operators retain aggregates: NMR MEA + MEAH+, titration species, and the separate 19-row Matin HCO3− + CO3²− pool. All values are mole fractions at retained states; pool rows are outside the objective and previously accessed.', ['species-figure-data.csv','pool-figure-data.csv','fitted-rows.csv'])
    fig,axes=plt.subplots(3,1,figsize=(FULL_WIDTH,6.8),layout='constrained',sharey=True)
    for ax,(source,pressure) in zip(axes,[('Vinjarapu2024',1734000),('Arcis2011',510000),('Arcis2011',1030000)]):
        part=[r for r in heat if r['source']==source and float(r['P_Pa'])==pressure]
        ax.errorbar([float(r['loading']) for r in part],[float(r['observed_kJ_mol']) for r in part],
                    yerr=[float(r['scale_J_mol_CO2'])/1000 for r in part],fmt='o',mfc='none',color='#0072B2',ms=4,lw=.6)
        ax.scatter([float(r['loading']) for r in part],[float(r['predicted_kJ_mol']) for r in part],marker='x',s=16,color='#D55E00')
        temperatures = {float(r['T_K']) for r in part}
        roles = {r['role'] for r in part}
        assert len(temperatures) == len(roles) == 1 and roles in ({'fitted'}, {'non-fitted prediction'})
        role = 'fitted' if roles == {'fitted'} else 'acceptance check'
        ax.set(title=f'{source} — {temperatures.pop():g} K; {pressure/1e6:g} MPa; {role}',xlabel=LOADING)
        ax.set_ylabel(r'Integral heat (kJ/mol CO$_2$)')
        ax.grid(alpha=.15)
    fig.suptitle('Open: observed; crosses: A7; bars: declared heat scale',fontsize=9)
    save(fig,'heat-of-absorption','Eight fitted Vinjarapu heats at 313.15 K and 1.734 MPa, and fourteen Arcis acceptance-check heats at 322.5 K, separated into the 0.51 and 1.03 MPa source-pressure groups. Bars show `scale_J_mol_CO2 / 1000`, not a declared confidence interval. There is no A7 no-heat series.', ['heat.csv'])
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
        ax.set(title=source+' fitted loaded',xlabel='Temperature (K)',ylabel='Error / declared scale s')
    excluded=set(summary['density']['Amundsen source-conflict five']['row_ids'])
    free=set(summary['density']['Amundsen CO2-free gate five']['row_ids'])
    for ax,record,group in [(axes[1,0],'Fitted', [r for r in density if r['id'] in set(spec['loaded_density_ids'])|free]),
                            (axes[1,1],'Non-fitted / excluded',[r for r in density if r['id'] not in set(spec['loaded_density_ids'])|free])]:
        for source,color in zip(sorted({r['source'] for r in density}),COLORS):
            for marker,is_excluded in [('o',False),('x',True)]:
                part=[r for r in group if r['source']==source and (r['id'] in excluded)==is_excluded]
                if not part:
                    continue
                ax.scatter([float(r['T_K']) for r in part],[float(r['error_kg_m3']) for r in part],marker=marker,color=color,s=12,label=source+(' excluded' if is_excluded else ''))
        ax.set(title=record+' A7 densities',xlabel='Temperature (K)',ylabel='Native density error (kg/m³)')
        ax.legend(fontsize=6,frameon=False,loc='upper center',bbox_to_anchor=(.5,-.18),ncol=2)
    fig.colorbar(plt.cm.ScalarMappable(norm=plt.Normalize(0,.5),cmap='viridis'),ax=list(axes[0]),label='Loading',shrink=.7)
    fig.suptitle('Top: A7 circles, A6 crosses, same 47 states; bottom: all 210 A7 rows',fontsize=9)
    save(fig,'loaded-density-errors','A7/A6 share the 47 fitted loaded-density identities, observed values, scales and states. Top panels show ±2s limits only for that fitted cohort; color denotes loading, with source separated. Bottom panels cover all 210 A7 densities and distinguish fitted, non-fitted and excluded rows. No empirical volume translation. Scales are not uniformly measurement uncertainty; 2s is not a 95% interval.', ['density.csv','fitted-rows.csv',str((a.J/'amendment-6/selected-assessment/density.csv').relative_to(a.ROOT))])
    fig,axes=plt.subplots(2,3,figsize=(FULL_WIDTH,5.4),layout='constrained',sharex=True,sharey=True)
    for row,record in enumerate(['A6','A7']):
        grid={}
        for index,r in paired[record].items():
            if index:
                grid.setdefault((r['temperature_K'],r['loading']),[]).append(r)
        assert len(grid)==24 and all(len(v)==3 for v in grid.values())
        for group in grid.values():
            for rank,r in enumerate(sorted(group,key=lambda x:float(x['pressure_Pa']))):
                ax=axes[row,rank]
                resolved=int(r['resolved_trials'])>0
                marker='s' if 'single-liquid' in r['classification'] else 'o'
                ax.scatter(float(r['temperature_K']),float(r['loading']),marker=marker,s=30,
                           facecolors='#D55E00' if resolved else 'none',edgecolors='#D55E00' if resolved else '#0072B2')
                if r['final_success']!='True' or int(r['failed_trial_optimizers']):
                    ax.annotate('!'+r['failed_trial_optimizers'],(float(r['temperature_K']),float(r['loading'])),fontsize=6)
        for rank,ax in enumerate(axes[row]):
            ax.set(title=record+' / '+['lowest','middle','highest'][rank]+' pressure',xlabel='Temperature (K)')
            ax.set_xticks([313.15,318.15,333.15],labels=['313.15','318.15','333.15'])
            ax.set_yticks([1e-5,.1,.3,.5],labels=[r'$10^{-5}$','0.1','0.3','0.5'])
            ax.grid(alpha=.15)
        axes[row,0].set_ylabel(LOADING)
    witness=paired['A7'][0]
    fig.suptitle('Resolved-descent points: A6 12/73; A7 0/73',fontsize=10)
    fig.supxlabel('Orange filled: resolved; blue open: none resolved; square: single liquid; circle: two-phase'
                     '\nIndex 0 shares index 41 temperature/loading (318.15 K, α ≈ 0.2556), with P rounded to 5918.5286 Pa'
'\nIndex 0: no resolved descent for A6 or A7; both classified two-phase',fontsize=7)
    save(fig,'phase-family','73 specified T/P/loading states, A6 versus A7 on the same wheel: 12/73 and 0/73 resolved-descent points. The three pressure levels vary with temperature/loading; S4 supplies exact pressures. The additional index-0 witness is reported separately from index 41. Zero resolved trials means no numerically resolved descent, not zero Gibbs change. Two-phase classifications do not identify two liquids. Finite searches do not certify a continuous stable region or states at 353 K.', ['phase-family.csv'])
    a6_assessment = a.load(a.J/'amendment-6/selected-assessment/provenance.json')
    fixed = a.J/'amendment-7/fixed-study/wheel-8298c602'
    records = dict(A7=a.record_identity(fit['record_sha256'], fit['engine']),
                   A6_assessment=a.record_identity(a6_assessment['parameter_sha256'], a6_assessment['engine']),
                   A6_phase_family=a.phase_identity(fixed/'after-adoption/a6-selected', fit['engine']),
                   A7_phase_family=a.phase_identity(fixed/'restricted-2-endpoint', fit['engine']))
    for name, output in OUTPUTS.items():
        output['records'] = {key: records[key] for key in (['A6_phase_family','A7_phase_family'] if name == 'phase-family' else ['A7','A6_assessment'] if name == 'loaded-density-errors' else ['A7'])}
    provenance=dict(generator=str(a.bind(a.ROOT/'analyses/mea_parameter_bundle/scripts/render_manuscript_figures.py').relative_to(a.ROOT)),
                    records=records, explanation=a.A6_ASSESSMENT_NOTE, inputs=dict(sorted(a.INPUTS.items())),outputs=OUTPUTS)
    (OUT/'provenance.json').write_text(json.dumps(provenance,indent=2,sort_keys=True)+'\n')
    print('Wrote five PDF/PNG figures and provenance.json; retained states only.')


if __name__=='__main__':
    main()
