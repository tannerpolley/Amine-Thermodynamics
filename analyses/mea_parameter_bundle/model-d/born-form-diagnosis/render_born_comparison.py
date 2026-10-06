"""Render the retained Born-form comparisons; no model imports or solves."""
import argparse
import csv
import hashlib
import json
import os
import sys
from pathlib import Path

HERE=Path(__file__).resolve().parent
FIGURES=HERE/'figures';FIGURES.mkdir(exist_ok=True)
ROOT=HERE.parents[3]
GENERATED=ROOT/'docs/scientific/latex/figures/generated'
GENERATED.mkdir(parents=True,exist_ok=True)
os.environ.setdefault('MPLCONFIGDIR',str(HERE/'runs/matplotlib-cache'))
sys.path.insert(0,str(ROOT/'analyses/mea_parameter_bundle/scripts'))
from manuscript_style import FULL_WIDTH, apply_style

import matplotlib
matplotlib.use('Agg')
apply_style()
import matplotlib.pyplot as plt
import numpy as np
from matplotlib.patches import Patch

COLORS={'11':'#0072B2','00':'#D55E00'}
HATCHES={'11':'///','00':'xxx'}
LABELS={'11':'SSM+DS (1,1)','00':'Original Born (0,0)'}
plotted=[]
def rows(relative):return list(csv.DictReader((HERE/relative).open()))
def retain(figure,panel,series,x,cost,source,**extra):
    plotted.append(dict(figure=figure,panel=panel,series=series,x_value=x,cost=cost,source_file=source,
        source_sha256=hashlib.sha256((HERE/source).read_bytes()).hexdigest(),**extra))
def save(fig,name):
    fig.savefig(FIGURES/(name+'.svg'))
    fig.savefig(FIGURES/(name+'.png'),dpi=160)
    if name in {'born-cost-by-group-and-species','born-p5-ranking-reversal'}:
        fig.savefig(GENERATED/(name+'.pdf'))
    plt.close(fig)

def add_panels(axes):
    for letter,ax in zip(('(a)','(b)'),axes):
        ax.text(0,1.035,letter,transform=ax.transAxes,ha='left',va='bottom',fontweight='bold')

def form_legend():
    return [Patch(facecolor=COLORS[key],edgecolor='black',linewidth=.7,hatch=HATCHES[key],label=LABELS[key]) for key in ('11','00')]

def costs():
    snapshot=rows('born-comparison-plotted-values.csv')
    group_rows=[r for r in snapshot if r['figure']=='cost-by-group-and-species' and r['panel']=='group']
    species_rows=[r for r in snapshot if r['figure']=='cost-by-group-and-species' and r['panel']=='species']
    plotted.extend(group_rows+species_rows)
    groups=['Full objective','Pressure (48)','Böttinger (40)','Matin (72)']
    identities=['Matin HCO3-','Matin MEA','Matin MEAH+','Matin MEACOO-',
                'Bottinger HCO3-','Bottinger MEACOO-','Bottinger MEA + MEAH+']
    fig,axes=plt.subplots(1,2,figsize=(FULL_WIDTH,3.9),gridspec_kw={'width_ratios':[.85,2.15]})
    for form,offset in [('11',-.18),('00',.18)]:
        vv=[float(next(r['cost'] for r in group_rows if r['series']==form and r['x_value']==label)) for label in groups]
        axes[0].barh(np.arange(4)+offset,vv,height=.34,color=COLORS[form],edgecolor='black',linewidth=.7,
                     hatch=HATCHES[form],label=LABELS[form])
        values=[float(next(r['cost'] for r in species_rows if r['series']==form and r['x_value']==label)) for label in identities]
        axes[1].barh(np.arange(7)+offset,values,height=.34,color=COLORS[form],edgecolor='black',linewidth=.7,
                     hatch=HATCHES[form])
    for ax in axes:ax.invert_yaxis();ax.grid(axis='x',alpha=.2);ax.set_axisbelow(True);ax.tick_params(axis='y',labelsize=8)
    axes[0].set_yticks(np.arange(4),['Full\nobjective','Pressure\n(48)','Böttinger\n(40)','Matin\n(72)'])
    axes[1].set_yticks(np.arange(7),[r'Matin: $\mathrm{HCO_3^-}$ pool','Matin: MEA',r'Matin: $\mathrm{MEAH^+}$',
                                    r'Matin: $\mathrm{MEACOO^-}$',r'Böttinger: $\mathrm{HCO_3^-}$ pool',
                                    r'Böttinger: $\mathrm{MEACOO^-}$',r'Böttinger: MEA + $\mathrm{MEAH^+}$'])
    add_panels(axes)
    fig.legend(handles=form_legend(),loc='upper center',bbox_to_anchor=(.57,.995),ncol=2,frameon=False)
    fig.supxlabel(r'Dimensionless cost, $C=\frac{1}{2}\sum r^2$',y=.025)
    fig.tight_layout(rect=(0, .03, 1, .91), w_pad=1.5)
    save(fig,'born-cost-by-group-and-species')

def ranking():
    snapshot=rows('born-comparison-plotted-values.csv')
    fitted=[r for r in snapshot if r['figure']=='p5-ranking-reversal' and r['panel']=='fitted set']
    rescored=[r for r in snapshot if r['figure']=='p5-ranking-reversal' and r['panel']=='full re-score']
    plotted.extend(fitted+rescored)
    fig,axes=plt.subplots(1,2,figsize=(FULL_WIDTH,3.45))
    for form,offset in [('11',-.18),('00',.18)]:
        set_names=('Historical full','Without Matin bicarbonate','Without all Matin')
        values=[float(next(r['cost'] for r in fitted if r['series']==form and r['x_value']==label)) for label in set_names]
        axes[0].bar(np.arange(3)+offset,values,width=.34,color=COLORS[form],edgecolor='black',linewidth=.7,
                    hatch=HATCHES[form],label=LABELS[form])
        labels=('P5a point','P5b point')
        resc=[float(next(r['cost'] for r in rescored if r['series']==form and r['x_value']==label)) for label in labels]
        axes[1].bar(np.arange(2)+offset,resc,width=.34,color=COLORS[form],edgecolor='black',linewidth=.7,
                    hatch=HATCHES[form])
    axes[0].set_xticks(np.arange(3),['160-target fit\n(Matin pool fitted)','142-target fit','88-target fit'])
    axes[1].set_xticks(np.arange(2),['142-target fit','88-target fit'])
    for ax in axes:ax.grid(axis='y',alpha=.2);ax.set_axisbelow(True);ax.tick_params(axis='x',labelsize=8)
    add_panels(axes)
    fig.legend(handles=form_legend(),loc='upper center',bbox_to_anchor=(.55,.995),ncol=2,frameon=False)
    fig.supylabel(r'Dimensionless cost, $C=\frac{1}{2}\sum r^2$',x=.015)
    fig.subplots_adjust(left=.13,right=.99,bottom=.23,top=.85,wspace=.36)
    save(fig,'born-p5-ranking-reversal')

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

def verify_plotted_values(figure_names):
    retained=list(csv.DictReader((HERE/'born-comparison-plotted-values.csv').open()))
    expected=[r for r in retained if r['figure'] in figure_names]
    actual=[r for r in plotted if r['figure'] in figure_names]
    if len(expected)!=len(actual):raise ValueError(f'plotted row count changed: {len(expected)} != {len(actual)}')
    def key(row):return (row['figure'],row['panel'],row['series'],row['x_value'],row['cost'],row['source_file'])
    old={key(row):row for row in expected}
    new={key({k:str(v) for k,v in row.items()}):{k:str(v) for k,v in row.items()} for row in actual}
    if old.keys()!=new.keys():raise ValueError('plotted series or coordinates changed')
    for k,record in new.items():
        if any(old[k].get(field,'')!=value for field,value in record.items()):
            raise ValueError(f'plotted value changed for {k}')

def write_manuscript_provenance():
    source_hashes=json.loads((HERE/'born-comparison-figure-sources.json').read_text())
    source_names={r['source_file'] for r in plotted if r['figure'] in {'cost-by-group-and-species','p5-ranking-reversal'}}
    output_names=('born-cost-by-group-and-species','born-p5-ranking-reversal')
    outputs={str((GENERATED/f'{name}.pdf').relative_to(ROOT)):hashlib.sha256((GENERATED/f'{name}.pdf').read_bytes()).hexdigest()
             for name in output_names}
    local={f'figures/{name}.{ext}':hashlib.sha256((FIGURES/f'{name}.{ext}').read_bytes()).hexdigest()
           for name in output_names for ext in ('svg','png')}
    style=ROOT/'analyses/mea_parameter_bundle/scripts/manuscript_style.py'
    provenance={'rendering_only':True,'renderer':str(Path(__file__).resolve().relative_to(ROOT)),
        'renderer_sha256':hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
        'style':str(style.relative_to(ROOT)),'style_sha256':hashlib.sha256(style.read_bytes()).hexdigest(),
        'source_ancestry_sha256':{name:source_hashes[name] for name in sorted(source_names)},
        'render_input_file':str((HERE/'born-comparison-plotted-values.csv').relative_to(ROOT)),
        'render_input_sha256':hashlib.sha256((HERE/'born-comparison-plotted-values.csv').read_bytes()).hexdigest(),
        'plotted_values_sha256':hashlib.sha256((HERE/'born-comparison-plotted-values.csv').read_bytes()).hexdigest(),
        'manuscript_pdf_sha256':outputs,'analysis_figure_sha256':local,
        'manuscript_width_mm':164.6,'panels':['(a)','(b)'],'color_and_grayscale_encoding':'form colors plus distinct hatch patterns'}
    (HERE/'born-manuscript-render-provenance.json').write_text(json.dumps(provenance,indent=2)+'\n')

if __name__=='__main__':
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--figures',nargs='+',choices=('costs','ranking','scans'),default=('costs','ranking'))
    selected=set(parser.parse_args().figures)
    if 'costs' in selected:costs()
    if 'ranking' in selected:ranking()
    if 'scans' in selected:scans()
    selected_data={'cost-by-group-and-species' if 'costs' in selected else None,
                   'p5-ranking-reversal' if 'ranking' in selected else None,
                   'fixed-k-scans' if 'scans' in selected else None} - {None}
    verify_plotted_values(selected_data)
    if selected=={'costs','ranking'}:
        write_manuscript_provenance()
    else:
        print('Rendered requested Born figures from retained values; snapshot unchanged.')
