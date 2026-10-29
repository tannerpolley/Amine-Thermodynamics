"""Fixed Bülow Tables 1–3 reactive bubble pressures; issue 223, no fitting."""
import concurrent.futures
import csv
import json
import math
from pathlib import Path
import epcsaft
from epcsaft import equilibrium as eq
import prepare as p

OUT = Path(__file__).resolve().parent


def problem(row):
    nw=1/.01801528
    m=float(row['m_MDEA_mol_per_kg_H2O']); c=float(row['m_CO2_mol_per_kg_H2O'])
    xi=.97*min(m,c)
    guess={p.W:nw-xi,p.M:m-xi+1e-6,p.C:c-xi+1e-4*c,p.MH:xi,p.B:xi,p.D:1e-3*xi,p.H:1e-9,p.OH:1e-7}
    total=sum(guess.values())
    rx=[]
    for r in p.REACTIONS:
        a,b,d=r['c']
        rx.append(eq.Reaction(r['stoichiometry'],name=r['name'],correlation=eq.ReactionLogPolynomial(a+d*math.log(298.15),b,d,0.,298.15,273.,498.,'aqueous-mole-fraction-infinite-dilution-water-v1'),reference=eq.ReactionReference(eq.ReferenceSourceBasis.RawMoleFractionInfiniteDilution)))
    return eq.Problem(T=float(row['temperature_K']),P=eq.Free(float(row['ten_times_total_pressure_MPa'])*1e5),feed=eq.Amounts({p.W:nw,p.M:m,p.C:c}),phases=[eq.Phase('L',kind='liquid',support=p.IDS,composition_guess={k:v/total for k,v in guess.items()}),eq.Phase('V',kind='vapor',support=p.IDS[:3],amount=eq.Pinned(0.),composition_guess={p.W:.5,p.M:.0001,p.C:.4999})],reactions=rx,neutral_reference=eq.NeutralReference(solvent=p.W,standard_molality_mol_per_kg=1.,solute_molality_ratios={p.M:.125,p.C:.125,p.MH:.125,p.H:.125,p.B:.125,p.OH:.0625,p.D:.03125}),row_tolerance=1e-10)


# Element inventories in component order: C, H, N, O; H+ bookkeeping follows Eq. 1–4.
ELEMENTS=[(0,2,0,1),(5,13,1,2),(1,0,0,2),(5,14,1,2),(1,1,0,3),(1,0,0,3),(0,1,0,0),(0,1,0,1)]


def solve_row(task):
    doc,row=task
    mix=epcsaft.Mixture(epcsaft.Parameters.from_mapping(doc))
    result=eq.solve_equilibrium(mix,problem(row))
    out=dict(source_row=int(row['source_row']),T_K=float(row['temperature_K']),m_MDEA=float(row['m_MDEA_mol_per_kg_H2O']),m_CO2=float(row['m_CO2_mol_per_kg_H2O']),observed_P_Pa=float(row['ten_times_total_pressure_MPa'])*1e5,success=result.success,message=result.message,solver_status=result.solver_status,linear_solver=result.linear_solver,residuals=list(result.residuals),classified_residuals=list(result.classified_residuals),qualified=False)
    out.update(terminal_pressure_Pa=result.pressure,terminal_coordinates=list(result.coordinates),terminal_mole_fractions=list(result.mole_fractions),terminal_densities=list(result.molar_densities),first_numerical_failure=str(result.first_numerical_failure),reference_diagnostics=[dict(reaction_index=d.reaction_index,status=str(d.status),message=d.message,density_convergence=str(d.density_convergence)) for d in result.neutral_reference_diagnostics])
    if not result.success:
        return out
    x=list(result.phase_mole_fractions(0)); y=list(result.phase_mole_fractions(1))
    states=[mix.state(result.temperature,rho=result.molar_densities[i],x=comp) for i,comp in enumerate([x,y])]
    feed=[1/.01801528,out['m_MDEA'],out['m_CO2'],0,0,0,0,0]
    inventories=[sum(result.amounts[j]*comp[i] for j,comp in enumerate([x,y])) for i in range(8)]
    balance=[sum((inventories[i]-feed[i])*ELEMENTS[i][e] for i in range(8)) for e in range(4)]
    charge=sum(inventories[i]*p.VALUES[i][1] for i in range(8))
    sums=[abs(sum(comp)-1) for comp in [x,y]]
    replay_problem=problem(row)
    replay_problem.P=eq.Free(result.pressure)
    replay_problem.phases[0].composition_guess=dict(zip(p.IDS,x))
    replay_problem.phases[1].composition_guess=dict(zip(p.IDS[:3],y[:3]))
    replay=eq.solve_equilibrium(mix,replay_problem)
    replay_error=abs(replay.pressure/result.pressure-1) if replay.success else None
    out.update(P_Pa=result.pressure,yCO2_P_Pa=y[2]*result.pressure,x_liquid=x,y_vapor=y,rho_mol_m3=list(result.molar_densities),phase_amounts_mol=list(result.amounts),element_balance_mol=balance,charge_balance_mol=charge,phase_sum_errors=sums,relative_replay_error=replay_error,replay_message=replay.message,permittivity=[st.bulk_relative_permittivity for st in states],pressure_density_derivative=[st.pressure_density_derivative for st in states],max_equilibrium_residual=max(map(abs,result.classified_residuals)),ARD_row_percent=100*abs(1-result.pressure/out['observed_P_Pa']),pressure_label_diagnostic_percent=100*abs(1-y[2]*result.pressure/out['observed_P_Pa']))
    out['qualified']=(all(d.status==eq.NeutralReferenceStatus.Available for d in result.neutral_reference_diagnostics) and out['max_equilibrium_residual']<=1e-10 and max(map(abs,balance+[charge]))<=1e-10 and max(sums)<=1e-10 and replay.success and replay_error<=1e-8 and all(v>=0 and math.isfinite(v) for v in x+y) and all(st.bulk_relative_permittivity>0 and st.pressure_density_derivative>0 for st in states))
    return out


def main():
    assert epcsaft.provenance()[1]==p.EXPECTED_WHEEL
    checks=json.loads((OUT/'repeat-checks.json').read_text())
    assert all(c['status']=='pass' for c in checks['checks'].values())
    assert p.sha(OUT/'run-document.json')==checks['run_document_sha256']
    assert p.sha(OUT/'declaration.json')==checks['declaration_sha256']
    frozen=json.loads((OUT/'declaration.json').read_text())
    for name in ['sources','inventory']:
        assert p.sha(OUT/(name+'.json'))==frozen['preparation'][('source_record' if name=='sources' else name)+'_sha256']
    for table in json.loads((OUT/'sources.json').read_text())['tables']:
        assert p.sha(p.ROOT/table['path'])==table['sha256']
    doc=json.loads((OUT/'run-document.json').read_text())
    inventory=json.loads((OUT/'inventory.json').read_text())
    ids={i for g in inventory['isotherms'] for i in g['source_rows']}
    rows=[r for r in csv.DictReader((p.ROOT/inventory['table_path']).open()) if int(r['source_row']) in ids]
    with concurrent.futures.ProcessPoolExecutor(max_workers=16) as pool:
        results=list(pool.map(solve_row,[(doc,r) for r in rows]))
    p.write('row-results.json',results)
    summaries=[]
    for group in inventory['isotherms']:
        selected=[r for r in results if r['source_row'] in group['source_rows']]
        qualified=all(r['qualified'] for r in selected)
        ard=sum(r['ARD_row_percent'] for r in selected)/group['N'] if qualified else None
        summaries.append(dict(group,our_ARD_percent=ard,qualified_count=sum(r['qualified'] for r in selected),reached=qualified and group['interval_percent'][0]<=ard<=group['interval_percent'][1],source_locator='Bülow 2021 SI Table S3, p.2; Eq.28; Kuranov Table 2 p.1960'))
    verdict='inconclusive' if not all(r['qualified'] for r in results) else ('reproduced under the declared interpretation' if all(g['reached'] for g in summaries) else 'not reproduced')
    p.write('summary.json',dict(verdict=verdict,isotherms=summaries,failures=[r['source_row'] for r in results if not r['qualified']],wheel_path=str(epcsaft.provenance()[0]),wheel_sha256=p.EXPECTED_WHEEL,engine_commit=p.ENGINE_COMMIT,declaration_sha256=checks['declaration_sha256'],run_document_sha256=checks['run_document_sha256'],fitting=False,scripts_sha256={name:p.sha(OUT/name) for name in ['prepare.py','run.py']}))
    print(json.dumps(dict(verdict=verdict,isotherms=summaries),indent=2),flush=True)

if __name__=='__main__':main()
