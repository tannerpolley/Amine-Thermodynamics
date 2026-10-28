"""Present retained #222 endpoint and attribution evidence; no calculations."""
import csv,json,hashlib
from pathlib import Path
AN=Path(__file__).resolve().parents[1]
def load(p):return json.loads((AN/p).read_text())
labels=['A1','A3','A4','B1','B3'];diagnostics=['without-unloaded-density','without-Cp','without-both','widened-bounds']
groups=['unloaded-density','Cp','Kuranov','Merkley','Carson','Jakobsen','loaded-density','Kim']
names=['k(MDEA-water)','slope(MDEA-water) K','k(MDEAH+-CO2)','k(MDEAH+-water)','slope(MDEAH+-water) K','k(MDEAH+-HCO3-)','sigma angstrom','u/k K','Born angstrom']

def gather(case,out):
 f=load(out+'/fit.json');decl=load(out+'/declaration.json');phase=load(out+'/carson-phase.json')
 params=[];it=iter(f['physical'])
 for c in decl['coordinates']:
  values=[next(it) for t in c['targets']];params.append(values[0])
 assert next(it,None) is None
 omitted=load(out+'/omitted-group-residuals.json') if (AN/out/'omitted-group-residuals.json').exists() else []
 costs=dict(f['group_costs'])
 for g in groups:
  if g not in costs:costs[g]=sum(.5*r['weight']*r['residual']**2 for r in omitted if r['group']==g)
 return dict(case=case,path=out,status=f['status'],message=f['message'],usable=f['usable'],iterations=f['iterations'],cost=f['final_cost'],group_costs=costs,active_bounds=f['covariance']['active_bounds'],parameters=dict(zip(names,params)),singular_values=f['covariance']['singular_values'],Carson=[{k:r[k] for k in ('source_row','completed','message','split','split_delta_g_over_rt','split_error_over_rt','max_residual')} for r in phase])

def table(records):
 lines=['| Case | Cost | Active coordinate indices (1-based) | Carson row 1 ΔG/RT | Carson row 10 ΔG/RT |','|---|---:|---|---:|---:|']
 for r in records:
  ph={q['source_row']:q for q in r['Carson']}
  def phase(n):return f"{ph[n]['split_delta_g_over_rt']:.6g}" if ph[n]['split'] else ('no witness' if ph[n]['completed'] and 'unresolved trials 0' in ph[n]['message'] else 'unresolved')
  lines.append(f"| {r['case']} | {r['cost']:.6f} | {', '.join(str(n+1) for n in r['active_bounds']) or 'none'} | {phase('1')} | {phase('10')} |")
 return '\n'.join(lines)

if __name__=='__main__':
 a=[gather(x,'results/joint-fit/'+x) for x in labels]
 b=[gather(x,'results/diagnosis-a1-bounds/'+x) for x in diagnostics]
 # Native fit Jacobian is weighted; its SVD agrees with retained covariance.
 f=load('results/joint-fit/A1/fit.json');decl=load('results/joint-fit/A1/declaration.json')
 gradients={g:[sum(f['optimizer_jacobian'][i*9+c]*f['weighted_residuals'][i] for i,m in enumerate(decl['observations']) if m['group']==g) for c in range(9)] for g in groups}
 (AN/'results/diagnosis-a1-bounds/a1-group-gradients.json').write_text(json.dumps(dict(basis='J_weighted.T @ r_weighted; derivative of cost in scaled optimizer coordinates',groups=gradients,total=[sum(v[c] for v in gradients.values()) for c in range(9)]),indent=2)+'\n')
 summary=dict(part1=a,part2=b,coordinate_order=names,group_order=groups)
 (AN/'results/diagnosis-a1-bounds/summary.json').write_text(json.dumps(summary,indent=2)+'\n')
 for records,out in [(a,'results/joint-fit'),(b,'results/diagnosis-a1-bounds')]:
  text='# '+('Remaining joint-fit starts' if records is a else 'A1 bound-pressure diagnosis')+'\n\n'
  text+='Diagnostic calibration only, on Engine 3e83e19c, wheel SHA-256 0d08dff9be39fb8fc9018119c47612f53d823cd0e456914d7dd44c6941596804. Base commit 2623829. No endpoint is selected or adopted; no outside-fit observations are evaluated. Independent delivered review and Design remain open.\n\n'
  text+=table(records)+'\n\nCoordinate order: '+ '; '.join(f'{i+1}: {n}' for i,n in enumerate(names))+'.\n\n'
  text+='Cost is half the sum of weighted squared scaled residuals. Diagnostic omitted-group costs below are evaluated at the endpoint but excluded from its fitted objective. A missing phase witness is only a completed-search statement, not proof of global stability. Negative split Gibbs energy is a numerical model result, not physical validation.\n\n'
  text+='The frozen 395 K reaction-domain amendment and Merkley fit temperatures 333.15 and 388.71 K are retained. Fits use the frozen 40-iteration/2100-second controls and tolerances; each compute.json records the memory-sized worker count and one BLAS thread per process. A2 and B2 remain duplicates.\n\n'
  text+='Reproduce from this worktree using `nice -n 10 agent-heavy /home/tnnrpolley21/Workspaces/Engineering/Amine-Thermodynamics/.venv/bin/python -I analyses/mdea_mea_workflow/scripts/remaining_starts_bounds.py`. Existing fit files are reused; phase/replay evidence is regenerated. The initial evaluation object access correction in fit_mdea.py changes no numerical declaration.\n\n'
  for r in records:
   text+='## '+r['case']+'\n\n'+r['status']+': '+r['message']+f" Iterations: {r['iterations']}.\n\n"
   text+='| Group | Cost |\n|---|---:|\n'+'\n'.join(f"| {g} | {r['group_costs'][g]:.9g} |" for g in groups)+'\n\n'
   text+='| Coordinate | Endpoint | Active bound |\n|---|---:|---|\n'+'\n'.join(f"| {n} | {v:.12g} | {'yes' if i in r['active_bounds'] else ''} |" for i,(n,v) in enumerate(r['parameters'].items()))+'\n\n'
   text+='Scaled-Jacobian singular values: '+', '.join(f'{s:.9g}' for s in r['singular_values'])+'. Full right singular vectors and active bounds are in fit.json. Full Carson searches, numerical error estimates, and equilibrium residuals are in carson-phase.json. Endpoint documents and fitted-row replay are retained alongside them.\n\n'
  (AN/out/'README.md').write_text(text)
 print(table(a));print(table(b))
 for records,out in [(a,'results/joint-fit'),(b,'results/diagnosis-a1-bounds')]:
  with (AN/out/'endpoint-summary.csv').open('w') as stream:
   writer=csv.writer(stream);writer.writerow(['case','status','cost','active_bounds']+names+groups+['Carson_row1','Carson_row10'])
   for r in records:writer.writerow([r['case'],r['status'],r['cost'],str(r['active_bounds'])]+list(r['parameters'].values())+[r['group_costs'][g] for g in groups]+[q['message'] for q in r['Carson']])
 cause='''## Attribution and its limits

The evidence supports a conflict among fitted properties within the frozen model and scales. It does not identify a wrong shared parameter or a single erroneous source. Removing either unloaded density or Cp changes the ion endpoint substantially, reverses the cation–bicarbonate and Born bound directions, and removes the Carson witnesses in these two searches. The omitted group then becomes badly misfitted. This is evidence of competing parameter demands; attributing them to a specific physical term or dataset error remains an inference requiring Design.

At A1, the unloaded-density group has cost 1273.529611. All 24 predictions reproduce with only MDEA and water present to 5.69e−13 kg/m³; the seven ion-coordinate Jacobian columns are exactly zero. The density misfit is therefore irreducible by ion coordinates directly. The MDEA–water coordinates remain free: fitting just their existing reciprocal law to density converges locally at cost 287.565760, k(313.15 K) = −0.206213778 and slope −175.541668 K, without active bounds. This leaves a nonzero neutral-model misfit, and is not proof of a global minimum or evidence that pure MDEA parameters alone are wrong. No association correction, pure parameter, data scale or model equation was changed.

The density and Cp groups exert opposing scaled cost gradients on the neutral reciprocal slope: +247.187 and −253.858. Thus density affects the ionic compromise indirectly through shared neutral coordinates. On the three A1 bound-active coordinates, the group gradients give a more specific local attribution: Kuranov contributes −1.33241 of the total −1.11407 cation–CO₂ gradient (pushing upward), −0.27030 of the total −0.13651 cation–bicarbonate gradient (pushing upward), and +1.72877 of the total +3.60992 Born gradient (pushing downward); Cp contributes +1.03331 to the Born gradient. Every group with nonzero Born sensitivity contributes in the downward direction. These derivatives use the frozen scaled coordinates and weights; they describe the local A1 endpoint, not unique physical causation.

Widening the three requested bounds lowers cost by 110.077659 (4.44%) but retains two active bounds and produces Carson witnesses at both rows. Row 1 ΔG/RT = −3.45906e−5 exceeds its estimated numerical error 2.61e−8 in magnitude; row 10 is −0.108570 versus 2.60e−8. It does not solve the bound or phase problem. The two omissions that converge also remain bound-constrained. The both-removed endpoint reaches the iteration limit and cannot support an optimum claim: the density-removed endpoint has a feasible lower cost, 53.235284, on the both-removed objective.

## Design options, without selection

1. Examine the neutral model's ability to describe density and Cp together before another transfer assessment: fixed pure MDEA inputs, reciprocal interaction law, cross-association and caloric assumptions are possible review boundaries. Changing any of them requires a new design and falsifier.
2. Audit the property bases and source consistency, and reconsider their roles or scales only with an explicit owner decision. The omission diagnostics do not authorize dropping either group.
3. If wider ionic bounds are scientifically justified, design the new ranges together with the phase requirement. The present widened run demonstrates that expanding these three intervals alone is insufficient.
4. Keep the current stops and the outside-fit block until a revised model or objective passes new bound and phase criteria. Further convergence work for the both-removed diagnostic would need an amended execution allowance; its current endpoint is incomplete.

These are engineering options, not a literature-mandated sequence. Baygi and Pahlavanzadeh (2015), §§3.1–3.3, separate pure/binary calibration from ternary assessment. Uyan et al. (2015), §4.2.3, use a binary cross-association correction and a different temperature law; those features are possible design alternatives, not evidence that they resolve this model's density/Cp conflict. The actual paper passages were read from the ignored shelf in the main checkout; all three Baygi/Uyan/Wangler reading-copy hashes match their indexed live Zotero Markdown files. No exact source equation or table was retranscribed for this diagnosis.

No endpoint is selected or adopted. No outside-fit data, including Ermatchkov, were evaluated. Weak-direction profiles, the Neumann sensitivity and the original transfer follow-ups remain blocked. These are calibration and numerical phase-search results, not physical validation, a transfer verdict, or absorber qualification. Independent delivered review and investigator promotion remain open.
'''
 prefix=(AN/'notebook.qmd').read_text().split('## Joint fit and mandatory stop')[0].split('## Remaining starts')[0]
 prefix=prefix.replace('Kim pre-fit and joint-fit bound stop','remaining starts and bound-pressure diagnosis')
 start=prefix.index('---',3)+4;end=prefix.index('## Kim-only pre-fit')
 prefix=prefix[:start]+'''All three distinct Variant A starts converge to the same bound-constrained result; both Variant B starts converge to another bound-constrained result. The A1 omission diagnostics support a conflict between density and Cp within the frozen model. Widening the three active bounds does not resolve the bounds or Carson phase stops. Nothing is adopted, and outside-fit assessment remains blocked. These results have not been independently reviewed or promoted for manuscript use.

'''+prefix[end:]
 text=prefix+'''## Remaining starts

The owner authorized the remaining starts and A1 attribution on 2026-10-28 in issue #222. The objective is unchanged: 280 residuals, the 395.0 K application reaction-domain amendment with unchanged coefficients, and only the four 20/40 wt% Merkley markers at 333.15 and 388.71 K. A2 and B2 are duplicates. Engine 3e83e19c is used through the pinned wheel and isolated main-venv interpreter. No Engine source is imported.

'''+table(a)+'\n\n'+'''B1 row 10 has an unresolved trial and no admitted split; B3 has no witness and zero unresolved trials. A finite no-witness search does not prove global stability. Negative split values are model numerical evidence, not observed demixing.

'''
 for records,title in [(a,'Joint-fit endpoint evidence'),(b,'A1 diagnostic endpoint evidence')]:
  text+='## '+title+'\n\n'
  if records is b:text+=table(b)+'\n\nThe both-removed endpoint is usable for diagnostics but not converged. Omitted group costs below are evaluated on fitted-source rows but excluded from the diagnostic objective.\n\n'
  text+='| Case | '+' | '.join(groups)+' |\n|---|'+'---:|'*len(groups)+'\n'
  for r in records:text+='| '+r['case']+' | '+' | '.join(f"{r['group_costs'][g]:.6f}" for g in groups)+' |\n'
  text+='\n| Coordinate | '+' | '.join(r['case'] for r in records)+' |\n|---|'+'---:|'*len(records)+'\n'
  for n in names:text+='| '+n+' | '+' | '.join(f"{r['parameters'][n]:.9g}" for r in records)+' |\n'
  text+='\nCoordinate indices in the endpoint tables refer to the coordinate order above. Exact active bounds, all singular values, right vectors, termination messages, and full phase-search records are retained in the linked READMEs.\n\n'
  text+='| Case | Scaled-Jacobian singular values |\n|---|---|\n'
  for r in records:text+='| '+r['case']+' | '+', '.join(f'{x:.7g}' for x in r['singular_values'])+' |\n'
  text+='\n'
 text+='''## A1 residual patterns

[Every density and Cp residual](results/diagnosis-a1-bounds/a1-density-cp-residuals.csv) retains temperature, unloaded-solvent mass fraction, loading, observed and predicted values, physical units, scaled and weighted residuals, and cost. Density spans 293.15–393.15 K at 10–40 wt%; Cp is at 298.15 K at 30–50 wt%. Density differences range from −4.09935 to +3.01330 kg/m³. Cp differences range from −0.28498 to +0.94890 J/g/K. The residual scales are the frozen objective conventions, not newly assigned measurement uncertainties.

![A1 model-minus-observation residuals on fitted rows only. Points are discrete evaluations, separated by unloaded-solvent composition. Density is compared against temperature; Cp against loading at 298.15 K. No outside-fit rows appear.](results/diagnosis-a1-bounds/a1-density-cp-residuals.png)

'''+cause+'''\n## Retained evidence and reproduction

[Joint-fit README](results/joint-fit/README.md) and [diagnosis README](results/diagnosis-a1-bounds/README.md) provide full endpoint tables and commands. Each endpoint includes the declaration, predictions, weighted residuals, scaled Jacobian, singular vectors, active bounds, endpoint document, fitted-row replay and Carson rows 1/10 searches. The reduced objectives also retain omitted-group predictions. The runtime receipt verifies the installed wheel files byte for byte. The initial derivative-object indexing error is corrected without changing declarations or equations; its failed attempt remains recorded under A3.

All eight new endpoints replay below the frozen 1e−8 relative tolerance. The no-ion density replay and zero ion sensitivities establish the stated invariance. No new numerical tolerance or acceptance rule is introduced. Numerical precision does not quantify experimental uncertainty or model discrepancy. The source notebook is retained; the ordinary site refresh is attempted separately and any missing renderer dependency is recorded in the diagnosis README.
'''
 (AN/'notebook.qmd').write_text(text)
 with (AN/'results/diagnosis-a1-bounds/README.md').open('a') as stream:stream.write('\n[The research notebook](../../notebook.qmd) owns the cause, inference limits, residual figure and Design options. `a1-density-cp-residuals.csv` owns the per-row residuals; `ion-free-density.json`, `ion-free-density-only-fit.json` and `a1-group-gradients.json` retain the attribution checks. Reproduce the neutral calculations with `scripts/a1_density_cp.py`, the figure with `scripts/plot_a1_residuals.py`, and this presentation with `scripts/summarize_bounds.py`, using the same isolated interpreter.\n')
