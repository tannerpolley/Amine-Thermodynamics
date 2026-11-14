"""Plot promoted F2 values only; no model evaluation."""
import json
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import final_rerun_tables as t
from final_rerun_tables import a, F, E
OUT = t.ROOT/'docs/scientific/latex/figures/generated'
plt.rcParams.update({'font.size':9,'pdf.fonttype':42,'figure.constrained_layout.use':True})
COLORS = ['#0072B2','#D55E00','#009E73','#CC79A7','#665500','#56B4E9']

def save(fig,name):
    fig.savefig(OUT/(name+'.pdf'),metadata={'CreationDate':None,'ModDate':None}); plt.close(fig)

def points(ax,rows,x,y,label,marker='o',scale=1):
    ax.scatter([float(r[x]) for r in rows],[float(r[y])*scale for r in rows],s=16,facecolors='none',edgecolors='black',marker=marker,label=label,zorder=3)

def main():
    meta={r['observation_id']:r for r in a.rows(t.ROOT/'data/reference/MEA/observations/vapor_liquid_equilibrium/Canonical_VLE_Observations.csv')}
    canonical = a.rows(F/'canonical-pressure.csv'); curves = a.rows(F/'model-curves/pressure.csv')
    fig,ax=plt.subplots(figsize=(6.8,4.4))
    for T,color in zip([313.15,333.15,353.15,373.15,393.15],COLORS):
        part=[r for r in curves if float(r['temperature_K'])==T and r['status']=='available']; part.sort(key=lambda r: float(r['analytical_loading'])); ax.plot([float(r['analytical_loading']) for r in part],[float(r['value'])/1000 for r in part],color=color,label=f'{T:g} K')
        part=[r for r in canonical if abs(float(r['temperature_K'])-T)<2]; ax.scatter([float(meta[r['target'].removesuffix('-pco2')]['CO2_loading']) for r in part],[float(r['observed'])/1000 for r in part],s=14,facecolors='none',edgecolors=color)
    ax.set(xlabel='Loading (mol CO₂/mol total MEA)',ylabel='CO₂ partial pressure (kPa)',yscale='log'); ax.legend(ncol=2); save(fig,'pressure')
    fig,axes=plt.subplots(1,2,figsize=(6.8,3.4)); rows=a.rows(F/'transfer.csv')
    for ax,w in zip(axes,[.15,.45]):
        part=[r for r in rows if float(meta[r['target'].removesuffix('-pco2')]['MEA_weight_fraction'])==w]
        for T,color in zip(sorted({r['temperature_K'] for r in part},key=float),COLORS):
            sub=[r for r in part if r['temperature_K']==T]
            ax.scatter([float(meta[r['target'].removesuffix('-pco2')]['CO2_loading']) for r in sub],[float(r['observed'])/1000 for r in sub],s=17,facecolors='none',edgecolors=color,label=f'{float(T):g} K')
            ax.scatter([float(meta[r['target'].removesuffix('-pco2')]['CO2_loading']) for r in sub],[float(r['predicted'])/1000 for r in sub],s=17,color=color,marker='x')
        ax.set(title=f'{100*w:g} wt% MEA',yscale='log',xlabel='Loading (mol/mol)',ylabel='CO₂ partial pressure (kPa)'); ax.legend(fontsize=7)
    save(fig,'concentration-pressure')
    rows=a.rows(F/'model-curves/species.csv'); obs=list({r['target']:r for r in a.rows(F/'species-figure-data.csv')}.values()); membership={r['membership_id'].replace('|','::'):r['co2_loading_mol_per_mol_mea'] for r in a.rows(t.ROOT/'data/reference/MEA/manifests/speciation_target_membership.csv')}
    names=['MEA + MEAH+','MEACOO-','MEAH+','HCO3- + CO3^2-']; fig,axes=plt.subplots(2,2,figsize=(6.8,5.4))
    for ax,name in zip(axes.flat,names):
        for T,color in zip([293.15,313.15,333.15,353.15],COLORS):
            part=[r for r in rows if r['quantity']==name and float(r['temperature_K'])==T and r['status']=='available']
            for below,style in [('False','-'),('True',':')]:
                sub=sorted([r for r in part if r['below_bubble_pressure']==below],key=lambda r:float(r['analytical_loading'])); ax.plot([float(r['analytical_loading']) for r in sub],[float(r['value']) for r in sub],style,color=color,label=f'{T:g} K' if below=='False' else None)
            sub=[r for r in obs if r['species']==('HCO3-' if name.startswith('HCO3') else name) and float(r['temperature_K'])==T]; ax.scatter([float(membership[r['target']]) for r in sub],[float(r['observed']) for r in sub],s=14,facecolors='none',edgecolors=color)
        ax.set(title={'MEA + MEAH+':r'MEA + MEAH$^+$','MEACOO-':r'MEACOO$^-$','MEAH+':r'MEAH$^+$','HCO3- + CO3^2-':r'HCO$_3^-$ + CO$_3^{2-}$'}[name],xlabel='Loading (mol CO₂/mol total MEA)',ylabel='Liquid mole fraction')
        if name.startswith('HCO3'): ax.set(yscale='log')
    axes[0,0].legend(fontsize=7); save(fig,'speciation')
    for file,name,ylabel,quantity,scale in [('heat','heat-of-absorption','Integral heat (kJ/mol CO₂)','integral heat of absorption',1),('density','density-curves','Liquid density (kg/m³)','liquid density',1)]:
        rows=a.rows(F/f'model-curves/{file}.csv'); fig,ax=plt.subplots(figsize=(6.8,3.8))
        for key,color in zip(dict.fromkeys(r['curve'] for r in rows),COLORS*3):
            part=[r for r in rows if r['curve']==key and r['status']=='available' and r['quantity']==quantity]; part.sort(key=lambda r: float(r['analytical_loading'])); ax.plot([float(r['analytical_loading']) for r in part],[float(r['value'])*scale for r in part],label=key,color=color)
        obs=[r for r in a.rows(F/f'{file}.csv') if file=='heat' or abs(float(r['mea_mass_fraction'])-.3)<1e-6]; points(ax,obs,'loading','observed_kJ_mol' if file=='heat' else 'observed_kg_m3','Measured')
        ax.set(xlabel='Loading (mol CO₂/mol total MEA)',ylabel=ylabel); ax.legend(fontsize=7,ncol=2); save(fig,name)
    rows=a.rows(F/'model-curves/mea-water.csv'); fig,ax=plt.subplots(figsize=(6.8,3.4))
    for key,color in zip(dict.fromkeys(r['curve'] for r in rows),COLORS):
        part=[r for r in rows if r['curve']==key and r['quantity']=='bubble temperature' and r['status']=='available']; ax.plot([float(r['liquid_mea_mole_fraction']) for r in part],[float(r['value']) for r in part],color=color,label=key)
    replay=a.load(E/'candidate/replay.json')['rows']; obs=[dict(r['row'],observed=r['observed']) for r in replay if r['group']=='Cai' and r['row']['quantity']=='temperature']; points(ax,[dict(r,x_mea=r['feed']['monoethanolamine']) for r in obs],'x_mea','observed','Measured')
    ax.set(xlabel='Liquid MEA mole fraction',ylabel='Bubble temperature (K)'); ax.legend(); save(fig,'mea-water')
    rows=a.rows(a.BUNDLE/'results/split-cause-342/figure-contributions.csv'); fig,ax=plt.subplots(figsize=(6.8,4)); names=['hard_chain','dispersion','association','debye_huckel','born','pv','ideal_and_standard','delta_g_over_rt']
    for i,r in enumerate(rows): ax.barh([k+i*.35 for k in range(len(names))],[float(r[n]) for n in names],height=.35,label='Unpenalized comparison' if i==0 else 'F2, frozen compositions')
    ax.set(yticks=[k+.175 for k in range(len(names))],yticklabels=['Hard chain','Dispersion','Association','Debye–Hückel','Born','PV','Ideal + standard','Total'],xlabel='Split minus parent G/(RT) (mol)'); ax.axvline(0,color='black',lw=.7); ax.legend(); save(fig,'split-energy')
    rows=[r for r in a.rows(E/'uncertainty/prediction-bands.csv') if r['group']=='common149: partial_pressure']; assert len(rows)==47; fig,ax=plt.subplots(figsize=(6.8,3.4)); ax.errorbar(range(len(rows)),[float(r['value'])/1000 for r in rows],yerr=[1.96*float(r['SE_bound_fixed'])/1000 for r in rows],fmt='o',ms=3); ax.set(xlabel='Observation order',ylabel='CO₂ partial pressure (kPa)'); save(fig,'pressure-uncertainty')
    (t.ROOT/'docs/scientific/latex/builds/347-figure-hashes.json').write_text(json.dumps({'commit':t.BASE,'files':a.INPUTS},indent=2)+'\n')

if __name__=='__main__': main()
