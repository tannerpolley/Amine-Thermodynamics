"""Plot promoted F2 values only; no model evaluation."""
import json
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.lines import Line2D
import final_rerun_tables as t
from final_rerun_tables import a, F, E
OUT = t.ROOT/'docs/scientific/latex/figures/generated'
plt.rcParams.update({'font.size':11,'font.family':'STIXGeneral','mathtext.fontset':'stix','pdf.fonttype':42,'figure.constrained_layout.use':True})
STYLES = ['-', '--', '-.', (0, (7, 2, 1, 2, 1, 2)), (0, (5, 1, 1, 1)), (0, (3, 1, 1, 1, 1, 1)), '-', ':']
TEMPERATURES = [293.15, 313.15, 333.15, 353.15, 373.15, 393.15, 298.15, 322.5]
COLORS = ['#0072B2','#D55E00','#009E73','#CC79A7','#665500','#007DA8','#222222','#6F4C9B']

def temperature_style(temperature):
    index = TEMPERATURES.index(float(temperature)) if float(temperature) in TEMPERATURES else 0
    return COLORS[index % len(COLORS)], STYLES[index % len(STYLES)]

# Temperature is shown by marker shape at one size, with the color and line style of the same temperature.
SIZE = 26
def temperature_marker(temperature):
    return {293.15: 'v', 313.15: 'o', 322.5: 's', 333.15: 's', 353.15: '^', 373.15: 'D', 393.15: 'P'}[float(temperature)]

def temperature_legend(temperatures):
    return [Line2D([], [], color=temperature_style(T)[0], linestyle=temperature_style(T)[1],
                   marker=temperature_marker(T), markerfacecolor='none', markersize=SIZE**0.5,
                   label=f'{T:g} K') for T in temperatures]

def save(fig,name):
    fig.savefig(OUT/(name+'.pdf'),metadata={'CreationDate':None,'ModDate':None}); plt.close(fig)

def points(ax,rows,x,y,label,marker='o',scale=1):
    ax.scatter([float(r[x]) for r in rows],[float(r[y])*scale for r in rows],s=16,facecolors='none',edgecolors='black',marker=marker,label=label,zorder=3)

def main():
    meta={r['observation_id']:r for r in a.rows(t.ROOT/'data/reference/MEA/observations/vapor_liquid_equilibrium/Canonical_VLE_Observations.csv')}
    canonical = a.rows(F/'canonical-pressure.csv'); curves = a.rows(F/'model-curves/pressure.csv')
    fitted = {r['id'] for r in a.rows(F/'fitted-rows.csv') if r['quantity'] == 'PartialPressure'}; assert len(fitted) == 47 and fitted <= {r['target'] for r in canonical}
    fig,ax=plt.subplots(figsize=(6.8,4.4))
    for T,color in zip([313.15,333.15,353.15,373.15,393.15],COLORS):
        color, style = temperature_style(T)
        part=[r for r in curves if float(r['temperature_K'])==T and r['status']=='available']; part.sort(key=lambda r: float(r['analytical_loading'])); ax.plot([float(r['analytical_loading']) for r in part],[float(r['value'])/1000 for r in part],color=color,linestyle=style,label=f'{T:g} K')
        part=[r for r in canonical if abs(float(r['temperature_K'])-T)<2]; ax.scatter([float(meta[r['target'].removesuffix('-pco2')]['CO2_loading']) for r in part],[float(r['observed'])/1000 for r in part],s=SIZE,marker=temperature_marker(T),facecolors=[color if r['target'] in fitted else 'none' for r in part],edgecolors=color)
    ax.set(xlabel='Loading (mol CO$_2$/mol total MEA)',ylabel='CO$_2$ partial pressure (kPa)',yscale='log'); ax.legend(handles=temperature_legend([313.15,333.15,353.15,373.15,393.15]),ncol=2); save(fig,'pressure')
    fig,axes=plt.subplots(1,2,figsize=(6.8,3.4)); rows=a.rows(F/'transfer.csv')
    for ax,w,letter in zip(axes,[.15,.45],'ab'):
        part=[r for r in rows if float(meta[r['target'].removesuffix('-pco2')]['MEA_weight_fraction'])==w]
        for T,color in zip(sorted({r['temperature_K'] for r in part},key=float),COLORS):
            color, style = temperature_style(T)
            sub=[r for r in part if r['temperature_K']==T]
            ax.scatter([float(meta[r['target'].removesuffix('-pco2')]['CO2_loading']) for r in sub],[float(r['observed'])/1000 for r in sub],s=SIZE,marker=temperature_marker(T),facecolors='none',edgecolors=color,label=f'{float(T):g} K')
            ax.scatter([float(meta[r['target'].removesuffix('-pco2')]['CO2_loading']) for r in sub],[float(r['predicted'])/1000 for r in sub],s=SIZE,color=color,marker='x')
        ax.set_title(f'({letter}) {100*w:g} wt% MEA', loc='left'); ax.set(yscale='log',xlabel='Loading (mol CO$_2$/mol total MEA)',ylabel='CO$_2$ partial pressure (kPa)')
    assert axes[0].get_legend_handles_labels()[1] == axes[1].get_legend_handles_labels()[1]  # one legend serves both panels
    axes[0].legend(fontsize=9)
    save(fig,'concentration-pressure')
    rows=a.rows(F/'model-curves/species.csv'); obs=list({r['target']:r for r in a.rows(F/'species-figure-data.csv')}.values()); membership={r['membership_id'].replace('|','::'):r['co2_loading_mol_per_mol_mea'] for r in a.rows(t.ROOT/'data/reference/MEA/manifests/speciation_target_membership.csv')}
    names=['MEA + MEAH+','MEACOO-','MEAH+','HCO3- + CO3^2-']; fig,axes=plt.subplots(2,2,figsize=(6.8,5.4))
    for ax,name,letter in zip(axes.flat,names,'abcd'):
        for T,color in zip([293.15,313.15,333.15,353.15],COLORS):
            color, temperature_dash = temperature_style(T)
            part=[r for r in rows if r['quantity']==name and float(r['temperature_K'])==T and r['status']=='available']
            for below,style in [('False','-'),('True',':')]:
                sub=sorted([r for r in part if r['below_bubble_pressure']==below],key=lambda r:float(r['analytical_loading'])); ax.plot([float(r['analytical_loading']) for r in sub],[float(r['value']) for r in sub],color=color,linestyle=temperature_dash if below=='False' else ':',label=f'{T:g} K' if below=='False' else None)
            sub=[r for r in obs if r['species']==('HCO3-' if name.startswith('HCO3') else name) and float(r['temperature_K'])==T]; ax.scatter([float(membership[r['target']]) for r in sub],[float(r['observed']) for r in sub],s=SIZE,marker=temperature_marker(T),facecolors='none',edgecolors=color)
        ax.set_title(f'({letter}) ' + {'MEA + MEAH+':r'MEA + MEAH$^+$','MEACOO-':r'MEACOO$^-$','MEAH+':r'MEAH$^+$','HCO3- + CO3^2-':r'HCO$_3^-$ + CO$_3^{2-}$'}[name], loc='left'); ax.set(xlabel='Loading (mol CO$_2$/mol total MEA)',ylabel='Liquid mole fraction')
        ax.set_xlim(-.03,.83)
        if name.startswith('HCO3'): ax.set(yscale='log')
    axes[0,0].legend(handles=temperature_legend([293.15,313.15,333.15,353.15]),fontsize=9); save(fig,'speciation')
    for file,name,ylabel,quantity,scale in [('heat','heat-of-absorption','Integral heat (kJ/mol CO$_2$)','integral heat of absorption',1),('density','density-curves','Liquid density (kg/m$^3$)','liquid density',1)]:
        rows=a.rows(F/f'model-curves/{file}.csv'); fig,ax=plt.subplots(figsize=(6.8,3.8))
        for key,color in zip(dict.fromkeys(r['curve'] for r in rows),COLORS*3):
            color, style = temperature_style(next(r['temperature_K'] for r in rows if r['curve']==key))
            if file == 'heat' and key.startswith('322.5'):
                style = ':' if '0.51' in key else '-.'
            part=[r for r in rows if r['curve']==key and r['status']=='available' and r['quantity']==quantity]; part.sort(key=lambda r: float(r['analytical_loading'])); ax.plot([float(r['analytical_loading']) for r in part],[float(r['value'])*scale for r in part],label=key,color=color,linestyle=style)
        obs=[r for r in a.rows(F/f'{file}.csv') if file=='heat' or abs(float(r['mea_mass_fraction'])-.3)<1e-6]
        if file == 'heat':
            conditions = [(313.15,1734000.,8), (322.5,510000.,8), (322.5,1030000.,6)]
            legend = []
            for T, P, count in conditions:
                sub = [r for r in obs if float(r['T_K'])==T and float(r['P_Pa'])==P]
                assert len(sub)==count
                color, style = temperature_style(T)
                if T == 322.5: style = ':' if P==510000. else '-.'
                face = color if P==1030000. else 'none'
                ax.scatter([float(r['loading']) for r in sub], [float(r['observed_kJ_mol']) for r in sub],
                           s=SIZE, marker=temperature_marker(T), facecolors=face, edgecolors=color, zorder=3)
                legend.append(Line2D([], [], color=color, linestyle=style, marker=temperature_marker(T),
                                     markerfacecolor=face, markersize=SIZE**0.5,
                                     label=f'{T:g} K, {P/1e6:g} MPa'))
            ax.legend(handles=legend, fontsize=9)
        else:
            points(ax,obs,'loading','observed_kg_m3','Measured')
            ax.legend(fontsize=9,ncol=2)
        ax.set(xlabel='Loading (mol CO$_2$/mol total MEA)',ylabel=ylabel); save(fig,name)
    rows=a.rows(F/'model-curves/mea-water.csv'); fig,ax=plt.subplots(figsize=(6.8,3.4))
    for key,color in zip(dict.fromkeys(r['curve'] for r in rows),COLORS):
        style = STYLES[list(dict.fromkeys(r['curve'] for r in rows)).index(key)]
        part=[r for r in rows if r['curve']==key and r['quantity']=='bubble temperature' and r['status']=='available']; ax.plot([float(r['liquid_mea_mole_fraction']) for r in part],[float(r['value']) for r in part],color=color,linestyle=style,label=key)
    replay=a.load(E/'candidate/replay.json')['rows']; obs=[dict(r['row'],observed=r['observed']) for r in replay if r['group']=='Cai' and r['row']['quantity']=='temperature']; points(ax,[dict(r,x_mea=r['feed']['monoethanolamine']) for r in obs],'x_mea','observed','Measured')
    ax.set(xlabel='Liquid MEA mole fraction',ylabel='Bubble temperature (K)'); ax.legend(); save(fig,'mea-water')
    rows=a.rows(a.BUNDLE/'results/split-cause-342/figure-contributions.csv'); fig,ax=plt.subplots(figsize=(6.8,4)); names=['hard_chain','dispersion','association','debye_huckel','born','pv','ideal_and_standard','delta_g_over_rt']
    for i,r in enumerate(rows): ax.barh([k+i*.35 for k in range(len(names))],[float(r[n]) for n in names],height=.35,color=['#0072B2','#B54D00'][i],edgecolor='#222222',linewidth=.6,hatch='' if i==0 else '///',label='Unpenalized comparison' if i==0 else 'Present model, frozen compositions')
    ax.set(yticks=[k+.175 for k in range(len(names))],yticklabels=['Hard chain','Dispersion','Association','Debye–Hückel','Born','PV','Ideal + standard','Total'],xlabel='Split minus parent G/(RT) (mol)'); ax.axvline(0,color='black',lw=.7); ax.legend(); save(fig,'split-energy')
    rows=[r for r in a.rows(E/'uncertainty/prediction-bands.csv') if r['group']=='common149: partial_pressure']; assert len(rows)==47; rows.sort(key=lambda r:(float(meta[r['identity'].removesuffix('-pco2')]['temperature_reported_C']),float(meta[r['identity'].removesuffix('-pco2')]['CO2_loading']))); fig,ax=plt.subplots(figsize=(6.8,3.4)); ax.errorbar(range(len(rows)),[float(r['value'])/1000 for r in rows],yerr=[1.96*float(r['SE_bound_fixed'])/1000 for r in rows],fmt='o',ms=3); ax.set(xlabel='Fitted pressure observations, ordered by temperature and loading',ylabel='CO$_2$ partial pressure (kPa)'); save(fig,'pressure-uncertainty')
    (t.ROOT/'docs/scientific/latex/builds/347-figure-hashes.json').write_text(json.dumps({'commit':t.BASE,'files':a.INPUTS},indent=2)+'\n')

if __name__=='__main__': main()
