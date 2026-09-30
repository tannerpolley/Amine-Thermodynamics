"""Format the completed assessment beside the older decision-23 values."""
import csv
import hashlib
import json
from pathlib import Path

HERE=Path(__file__).resolve().parent
def table(headers,rows):
    return '| '+' | '.join(headers)+' |\n| '+' | '.join(['---']*len(headers))+' |\n'+'\n'.join('| '+' | '.join(map(str,row))+' |' for row in rows)+'\n'

def assessment():
    model=HERE.parent
    source=model/'assessment-p5a-summary.json'
    oldsource=model/'assessment-28181e72-summary.json'
    summary=json.loads(source.read_text());old=json.loads(oldsource.read_text())['variants']
    new={f:json.loads((model/f'assessment-p5a-{f}-summary.json').read_text()) for f in ('11','00')}
    for f in new:assert new[f]==summary['variants'][f]
    variants=[new['11'],new['00'],old['1-1'],old['0-0']]
    headers=['Comparison','Units','142-target SSM+DS','142-target Original','Old SSM+DS','Old Original']
    rows=[];exact=[]
    def add(label,unit,values):
        values=list(map(float,values))
        rows.append([label,unit,*[f'{x:.6f}' for x in values]])
        exact.append(dict(quantity=label,unit=unit,p5a_11=values[0],p5a_00=values[1],decision23_11=values[2],decision23_00=values[3]))
    for key,label in [('pressure_gate','Pressure gate, 104 rows, 40–80 °C'),('fitted_pressure','Fitted pressure, 48 targets'),('fitted_speciation','Fitted species, new 94 / old 112 targets')]:
        add(label,'AARD, %',[v[key]['aard_percent'] for v in variants])
    for key,label,scope in [('held_out_80C_pressure','80 °C packet pressure, 11 targets','packet validation (80 degC) pCO2'),('held_out_80C_speciation','80 °C packet species, 11 targets','packet validation (80 degC) speciation'),('canonical_80C_pressure','80 °C canonical pressure, 21 rows','T=80C')]:
        add(label,'AARD, %',[v[key]['aard_percent'] for v in variants[:2]]+[next(r for r in v['pressure_speciation_and_carbonate_scores'] if r['scope']==scope)['aard_percent'] for v in variants[2:]])
    for mass,n in [('0.15',33),('0.45',37)]:
        add(f'{float(mass)*100:g} wt% transfer, {n} rows','AARD, %',[next(r for r in v['composition_second_look'] if r['mea_mass_fraction']==mass)['aard_percent'] for v in variants])
    text='The completed assessment compares the decision-24 records with the older decision-23 records. It is **numerical verification on fitted and previously inspected assessment data, not physical validation**. Both new records meet the 104-row pressure rule (AARD ≤35%) and the numerical-completeness checks. The Supported delivered-review gate remains open; no parameter record is adopted here.\n\n'+table(headers,rows)
    text+='\nAARD is the unweighted mean absolute relative deviation with the observed value in the denominator. Fitted-species AARD compares **94 new targets with 112 old targets**; the target sets differ. The packet pressure and species groups at 80 °C each contain 11 targets; the canonical pressure group contains 21 rows. These groups are outside the fit but were inspected previously. The 15/45 wt% comparisons are a second look, not untouched validation, and retain large errors.\n\n'
    ranges=[v['carbonate_nine_point_ratio_min_max'] for v in variants]
    text+=table(headers,[['Carbonate, nine points','calculated / observed',*[f'{float(a):.6f}–{float(b):.6f}' for a,b in ranges]]])
    for j,kind in enumerate(('minimum','maximum')):add('Carbonate ratio '+kind,'dimensionless',[r[j] for r in ranges])
    text+='\nThe carbonate summary keeps the existing exclusion at 40 °C and loading 0.21; all ten raw points remain retained. The range describes the comparison with Jakobsen, not an independent carbonate validation.\n\n'
    pools=[new[f]['Matin_pool_report_only'] for f in ('11','00')]+[summary['old_decision23'][f]['Matin_pool_report_only'] for f in ('11','00')]
    rows=[]
    for key,label,unit in [('aard_percent','Matin pool AARD','%'),('mean_signed_relative_error_percent','Matin pool signed relative mean','%'),('mean_signed_weighted_residual','Matin pool signed weighted mean','dimensionless'),('mean_signed_mole_fraction_error','Matin pool signed mole-fraction mean','mol/mol')]:
        add(label,unit,[p[key] for p in pools])
    text+=table(headers,rows)
    text+='\nAll 18 Matin HCO₃⁻ + CO₃²⁻ targets are **report-only under decision 24**, whereas they were fitted in the older records. The signed means use model minus observation in their stated scale. SSM+DS disagrees more with the pool after it leaves the objective. The source-method basis for that role remains distinct from the fit preference.\n\n'
    checks=[]
    for i,v in enumerate(variants):
        packet=v['packet_checks'] if i<2 else next(r for r in v['solver_checks'] if r['scope']=='packet states')
        canonical=v['canonical_checks'] if i<2 else next(r for r in v['solver_checks'] if r['scope']=='six-source pCO2 states')
        checks.append(['142-target' if i<2 else 'Old decision-23','SSM+DS' if i%2==0 else 'Original Born',f'{packet["evaluated"]}/{packet.get("rows",packet.get("n"))}',f'{canonical["evaluated"]}/{canonical.get("rows",canonical.get("n"))}',packet['tolerance_not_met'],canonical['tolerance_not_met'],packet['balance_errors'],canonical['balance_errors'],f'{float(packet["max_abs_stationarity"]):.3e}',f'{float(canonical["max_abs_stationarity"]):.3e}'])
    checklabels=['Packet complete','Canonical complete','Packet tolerance failures','Canonical tolerance failures','Packet balance errors','Canonical balance errors','Packet max stationarity','Canonical max stationarity']
    text+=table(['Numerical check','142-target SSM+DS','142-target Original','Old SSM+DS','Old Original'],[[label,*[row[i+2] for row in checks]] for i,label in enumerate(checklabels)])
    text+='\nThe new transfer evaluation is complete at all 70 rows, with zero tolerance failures and balance errors for each form. The checks retain the Engine requested tolerance, material-balance error ≤1e−7 × max(1, |conserved total|) mol and charge-balance error ≤1e−7 mol of elementary charge. This establishes numerical completeness for these evaluations.\n\n'
    salt=[]
    for temperature in ['278.15','288.15','298.15','308.15','318.15','all']:
        group=[next(r for r in v['nahco3_indicative'] if r['temperature_k']==temperature) for v in variants]
        salt.append([temperature,group[0]['n'],*[f'{float(r["ard_percent"]):.6f}' for r in group]])
        add('NaHCO3 ARD T='+temperature,'%', [r['ard_percent'] for r in group])
    text+=table(['NaHCO₃ temperature, K','Rows','142-target SSM+DS ARD, %','142-target Original ARD, %','Old SSM+DS ARD, %','Old Original ARD, %'],salt)
    text+='\nAll 60 new NaHCO₃ rows are evaluated without reported failures. They compare with evaluated Pitzer-fit values using unrefitted Figiel sodium inputs; this is an indicative check, not measured-salt validation of MEA parameters.\n\n[Assessment summary](model-d/assessment-p5a-summary.json), [SSM+DS assessment](model-d/assessment-p5a-11-summary.json), [Original Born assessment](model-d/assessment-p5a-00-summary.json), and [older decision-23 assessment](model-d/assessment-28181e72-summary.json) retain the exact values. The assessment and this section still require the owner’s Supported delivered review.\n\n'
    with (HERE/'born-assessment-comparison.csv').open('w',newline='') as handle:
        w=csv.DictWriter(handle,list(exact[0]));w.writeheader();w.writerows(exact)
    paths=[source,oldsource,*[model/f'assessment-p5a-{f}-{suffix}' for f in ('11','00') for suffix in ('summary.json','scores.csv','packet-summary.json','canonical-summary.json','transfer-scores.csv','transfer-summary.json','matin-pool-summary.json','nahco3-scores.csv')]]
    (HERE/'born-assessment-source-hashes.json').write_text(json.dumps({str(p.relative_to(HERE.parent.parent)):hashlib.sha256(p.read_bytes()).hexdigest() for p in paths},indent=2)+'\n')
    return text
