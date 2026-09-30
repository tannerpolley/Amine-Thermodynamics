"""Render the Born-form comparison from retained CSVs; no model imports or solves."""
import csv
import hashlib
import json
import os
from pathlib import Path

HERE=Path(__file__).resolve().parent
FIGURES=HERE/'figures';FIGURES.mkdir(exist_ok=True)
os.environ.setdefault('MPLCONFIGDIR',str(HERE/'runs/matplotlib-cache'))
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import numpy as np

COLORS={'11':'#0072B2','00':'#D55E00'}
LABELS={'11':'SSM+DS (1,1)','00':'Original Born (0,0)'}
plt.rcParams.update({'font.size':11,'axes.spines.top':False,'axes.spines.right':False,'svg.fonttype':'none'})
plotted=[]
def rows(relative):return list(csv.DictReader((HERE/relative).open()))
def retain(figure,panel,series,x,cost,source,**extra):
    plotted.append(dict(figure=figure,panel=panel,series=series,x_value=x,cost=cost,source_file=source,
        source_sha256=hashlib.sha256((HERE/source).read_bytes()).hexdigest(),**extra))
def save(fig,name):
    fig.savefig(FIGURES/(name+'.svg'),bbox_inches='tight')
    fig.savefig(FIGURES/(name+'.png'),dpi=160,bbox_inches='tight');plt.close(fig)

def costs():
    source='key-objective-evaluations.csv'
    baseline={r['name'][-2:]:r for r in rows(source) if r['name'] in ('baseline-11','baseline-00')}
    sp_source='runs/tables/objective-species-costs-and-signed-residuals.csv'
    sp=[r for r in rows(sp_source) if r['evaluation'] in ('baseline-11','baseline-00') and int(r['n'])>0]
    groups=[('cost','Full objective'),('pressure_cost','Pressure (48)'),('bottinger_cost','Böttinger (40)'),('matin_cost','Matin (72)')]
    identities=[('Matin','HCO3-'),('Matin','MEA'),('Matin','MEAH+'),('Matin','MEACOO-'),
                ('Bottinger','HCO3-'),('Bottinger','MEACOO-'),('Bottinger','MEA + MEAH+')]
    names=['Matin: HCO₃⁻ pool','Matin: MEA','Matin: MEAH⁺','Matin: MEACOO⁻',
           'Böttinger: HCO₃⁻ pool','Böttinger: MEACOO⁻','Böttinger: MEA + MEAH⁺']
    fig,axes=plt.subplots(1,2,figsize=(13,5),gridspec_kw={'width_ratios':[1,1.5]})
    for form,offset in [('11',-.18),('00',.18)]:
        vv=[float(baseline[form][key]) for key,_ in groups]
        axes[0].barh(np.arange(4)+offset,vv,height=.34,color=COLORS[form],label=LABELS[form])
        for (key,label),value in zip(groups,vv):retain('cost-by-group-and-species','group',form,label,value,source)
        values=[]
        for source_name,species in identities:
            rec=next(r for r in sp if r['evaluation']=='baseline-'+form and r['source']==source_name and r['species']==species)
            value=float(rec['cost']);values.append(value)
            retain('cost-by-group-and-species','species',form,source_name+' '+species,value,sp_source,
                   mean_signed_weighted_residual=float(rec['mean_signed_weighted_residual']),n=int(rec['n']))
        axes[1].barh(np.arange(7)+offset,values,height=.34,color=COLORS[form])
    for ax in axes:ax.invert_yaxis();ax.set_xlabel('Dimensionless cost, ½∑r²');ax.grid(axis='x',alpha=.2);ax.set_axisbelow(True)
    axes[0].set_yticks(np.arange(4),[g[1] for g in groups]);axes[0].legend(loc='lower right',fontsize=10)
    axes[1].set_yticks(np.arange(7),names)
    axes[0].set_title('Original Born has the lower full cost')
    axes[1].set_title('Matin bicarbonate contributes 6.02 of the 7.42 gap')
    fig.tight_layout(w_pad=3);save(fig,'born-cost-by-group-and-species')

def ranking():
    source='p5conv-costs.csv';rr=rows(source)
    base={r['name'][-2:]:float(r['cost']) for r in rows('key-objective-evaluations.csv') if r['name'] in ('baseline-11','baseline-00')}
    fig,axes=plt.subplots(1,2,figsize=(12,4.8))
    for form,offset in [('11',-.18),('00',.18)]:
        values=[base[form]]+[float(next(r for r in rr if r['run']==f'p5conv-{case}-{form}')['fitted_cost']) for case in ('a','b')]
        axes[0].bar(np.arange(3)+offset,values,width=.34,color=COLORS[form],label=LABELS[form])
        for label,n,value in zip(('Historical full','Without Matin bicarbonate','Without all Matin'),(160,142,88),values):
            retain('p5-ranking-reversal','fitted set',form,label,value,'key-objective-evaluations.csv' if n==160 else source,n=n)
        resc=[float(next(r for r in rr if r['run']==f'p5conv-{case}-{form}')['full_cost']) for case in ('a','b')]
        axes[1].bar(np.arange(2)+offset,resc,width=.34,color=COLORS[form])
        for label,value in zip(('P5a point','P5b point'),resc):retain('p5-ranking-reversal','full re-score',form,label,value,source,n=160)
    axes[0].set_xticks(np.arange(3),['Historical full\n160 targets','P5a: no Matin HCO₃⁻\n142 targets','P5b: no Matin\n88 targets'])
    axes[1].set_xticks(np.arange(2),['P5a point','P5b point'])
    for ax in axes:ax.set_ylabel('Dimensionless cost, ½∑r²');ax.grid(axis='y',alpha=.2);ax.set_axisbelow(True)
    axes[0].set_title('Reduced fitted sets favor SSM+DS');axes[1].set_title('Full 160-target re-scores favor Original Born')
    axes[0].legend(fontsize=10);fig.tight_layout(w_pad=2);save(fig,'born-p5-ranking-reversal')

def scans():
    fig,axes=plt.subplots(2,2,figsize=(12,8));axes=axes.ravel()
    a_source='scans/scan_A_results.csv';a=rows(a_source)
    for parameter,style,label in [('water','-','Water factor, form (1,1)'),('monoethanolamine','--','MEA factor, form (1,1)')]:
        rr=[r for r in a if r['param']==f'component/{parameter}/solvation_factor']
        axes[0].plot([float(r['value']) for r in rr],[float(r['cost']) for r in rr],style+'o',color=COLORS['11'],label=label)
        for r in rr:retain('fixed-k-scans','A',label,float(r['value']),float(r['cost']),a_source)
    axes[0].set_yscale('log');axes[0].set_xlabel('Solvation factor (dimensionless)');axes[0].legend(fontsize=9)
    b_source='scans/scan_B_results.csv';b=rows(b_source)
    good=[r for r in b if r['cost']]
    axes[1].plot([float(r['value']) for r in good],[float(r['cost']) for r in good],'-o',color=COLORS['11'])
    axes[1].set_xscale('log',base=2);axes[1].set_yscale('log');axes[1].set_xticks([2,4,8,16,32],['2','4','8','16','32'])
    axes[1].text(2,.06,'Unavailable\nEngine diagnosis',transform=axes[1].get_xaxis_transform(),fontsize=9,ha='left')
    axes[1].set_xlabel('Ion-region relative permittivity (dimensionless)')
    for r in b:retain('fixed-k-scans','B','11',float(r['value']),float(r['cost']) if r['cost'] else None,b_source,available=bool(r['cost']))
    for ax,letter,xkey,xlabel in [(axes[2],'C','scale','Multiplier of all Born diameters (dimensionless)'),
                                 (axes[3],'D','value','MEA relative permittivity (dimensionless)')]:
        source=f'scans/scan_{letter}_results.csv';rr=rows(source)
        for form in ('11','00'):
            one=[r for r in rr if r['form']==form]
            ax.plot([float(r[xkey]) for r in one],[float(r['cost']) for r in one],'-o',color=COLORS[form],label=LABELS[form])
            for r in one:retain('fixed-k-scans',letter,form,float(r[xkey]),float(r['cost']),source)
        ax.set_xlabel(xlabel);ax.legend(fontsize=9)
    for ax,title in zip(axes,['A: Baseline solvent factors give the lowest sampled cost',
        'B: εion = 8 gives the lowest available sampled cost','C: Diameter-scale response depends on the form',
        'D: Changing MEA permittivity moves the forms differently']):
        ax.set_title(title,fontsize=11);ax.set_ylabel('Dimensionless cost, ½∑r²');ax.grid(alpha=.2)
    fig.tight_layout(h_pad=3,w_pad=2);save(fig,'born-fixed-k-scans')

if __name__=='__main__':
    costs();ranking();scans()
    fields=sorted(set().union(*(r.keys() for r in plotted)))
    with (HERE/'born-comparison-plotted-values.csv').open('w',newline='') as handle:
        writer=csv.DictWriter(handle,fields);writer.writeheader();writer.writerows(plotted)
    (HERE/'born-comparison-figure-sources.json').write_text(json.dumps({r['source_file']:r['source_sha256'] for r in plotted},indent=2)+'\n')
    print('Rendered three figures from retained CSVs;',len(plotted),'plotted rows retained.')
