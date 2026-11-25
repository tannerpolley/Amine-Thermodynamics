"""Compare carbonate-pool odds and pH offsets at the matching Jakobsen loadings."""
from pathlib import Path
from tempfile import TemporaryDirectory
from time import monotonic
import math

from amp import DECLARATION
from common import ROOT, fingerprints, save
from part_ii import Route, eq, np, stable
from mea import B, C, H, W, request, s, setup, source_log_k

Q5 = ROOT/'analyses/round_3/results/q5.json'
SYMBOLS = Q5.with_name('ph-digitization.json')


def calculate(work):
    started=monotonic()
    Route(DECLARATION,work)
    mapping, model=setup()
    archived=stable.read(Q5)
    Mw=mapping['components'][W]['fixed']['molar_mass']['value']['magnitude']
    digitized={r['T_K']:r for r in stable.read(SYMBOLS)}
    rows=[]
    for old in archived['carbonate_pool_comparison']:
        row=dict(old)
        rows.append(row)
        T=old['T_K']
        problem=s._problem_from_request(request(mapping,T,old['loading']))
        problem.feed=eq.Amounts(old['feed_mol'])
        assert problem.P==old['P_Pa']
        result=eq.solve_equilibrium(model,problem)
        row['message']=result.message
        if not result.requested_tolerance_met:
            continue
        x=list(result.phase_mole_fractions(0))
        activities=[a for a in eq.reaction_activities(model,result) if a.phase_index==0]
        common=next(a for a in activities if a.basis.startswith('common-molality'))
        logs=common.species.log_activities
        molal_profiles=[math.log(x[i]/(x[W]*Mw*common.species.standard_molality_mol_per_kg)) for i in (B,C)]
        log_gamma_ratio=(logs[B]-molal_profiles[0])-(logs[C]-molal_profiles[1])
        reaction=next(r for r in problem.reactions if r.name=='R3')
        raw_ln_k=source_log_k(reaction.correlation,T)
        # Q4: subtract the mole-fraction-to-molality conversion for R3 solutes.
        nu=reaction.stoichiometry
        molality_term=(sum(nu.values())-nu['water'])*math.log(Mw*common.species.standard_molality_mol_per_kg)
        ln_k=raw_ln_k-molality_term
        model_ln_odds=math.log(x[C]/x[B])
        lhs=ln_k+logs[W]+log_gamma_ratio-logs[H]
        f=old['observed']
        observed_ln_odds=math.log(f/(1-f))
        row.update(ln_K_R3=ln_k, ln_K_raw_R3=raw_ln_k, log_molality_conversion=molality_term, ln_a_water=logs[W],ln_gamma_bicarbonate_over_carbonate=log_gamma_ratio,
                   pH_model=-logs[H]/math.log(10),model_odds=math.exp(model_ln_odds),
                   observed_odds=math.exp(observed_ln_odds), required_pH_shift=(observed_ln_odds-model_ln_odds)/math.log(10),
                   odds_identity_error=lhs-model_ln_odds, pool_replay_error=x[C]/(x[C]+x[B])-old['carbonate_pool_split'])
        curve=sorted((r for r in archived['rows'] if r['T_K']==T and r.get('symbol') and 'model_minus_electrode_pH' in r),
                      key=lambda r:r['loading'])
        a=old['loading']
        if not curve or not curve[0]['loading']<=a<=curve[-1]['loading']:
            row['electrode_match']=None
            continue
        u_a=digitized[T]['loading_read_off']
        u_pH=digitized[T]['pH_read_off']
        xs=[r['loading'] for r in curve]
        offsets=[-r['model_minus_electrode_pH'] for r in curve]
        offset=float(np.interp(a,xs,offsets))
        interval=[float(np.interp(t,xs,offsets)) for t in (a-u_a,a,a+u_a)]
        bounds=[min(interval)-u_pH,max(interval)+u_pH]
        ratio=math.exp(model_ln_odds)*10**offset
        row['electrode_match']=dict(delta_pH=offset,read_off_interval=bounds,electrode_stock_mass_fraction=archived['stock_MEA_mass_fraction'],
                                   correction_fraction_of_gap=offset/row['required_pH_shift'],corrected_odds=ratio,corrected_pool_fraction=ratio/(1+ratio))
    save('records/pH-carbonate.json',dict(rows=rows,pH_basis='model common-molality hydronium activity; electrode-scale offset depends on measurement and stock',
         inputs=fingerprints(Q5,SYMBOLS)),start=started)


if __name__=='__main__':
    with TemporaryDirectory() as directory:
        calculate(Path(directory))
