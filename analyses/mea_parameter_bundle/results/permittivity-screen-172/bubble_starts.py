"""Two bubble-based starts for remaining flash rows below their computed bubble pressure."""
import concurrent.futures
import multiprocessing
import permittivity_probe as s

CHECKS = [r for r in s.read(s.OUT/'flash-family-remaining-diagnosis.json')
          if r.get('bubble_accepted') and r['family_P_over_bubble_P'] < 1.]


def recover(row):
    basis, name = row['basis'],row['variant']
    model=s.mixture(s.VARIANTS[name] if basis=='current' else s.engine_variant(name))
    problem=s.flash_problem(basis,row['loading'],row['temperature_K'],row['pressure_Pa'])
    bubble=s.flash_problem(basis,row['loading'],row['temperature_K'],row['bubble_pressure_Pa'])
    bubble.P=s.h.eq.Free(row['bubble_pressure_Pa'])
    bubble.phases[1].amount=s.h.eq.Pinned(0.)
    r=s.h.eq.solve_equilibrium(model,bubble)
    out=dict(basis=basis,variant=name,index=row['index'],bubble_accepted=r.success)
    if r.success:
        starts=[s.h.eq.EquilibriumStart(amounts=[r.amounts[0]*f,r.amounts[0]*(1-f)],
            compositions=[r.mole_fractions[:9],r.mole_fractions[9:12]],packing_fractions=r.packing_fractions)
            for f in (.5,.9)]
        batch=s.h.eq.solve_equilibrium_starts(model,problem,starts,s.h.eq.EquilibriumWorkLimits(attempts=2,attempt_iterations=400,iterations=800))
        out.update(accepted=batch.selected is not None,selected=batch.selected,causes=batch.causes,
            attempts=[None if v is None else dict(accepted=v.success and v.requested_tolerance_met,message=v.message,
                residual=v.convergence.residual,objective_over_RT=v.objective,amounts=list(v.amounts),
                mole_fractions=list(v.mole_fractions),molar_densities=list(v.molar_densities),coordinates=list(v.coordinates))
                for v in batch.results])
    return out


if __name__=='__main__':
    with concurrent.futures.ProcessPoolExecutor(16,mp_context=multiprocessing.get_context('fork')) as pool:
        rows=list(pool.map(recover,CHECKS))
    s.save('flash-family-bubble-starts.json',rows)
    print('BUBBLE STARTS',len(rows),'RECOVERED',sum(r.get('accepted',False) for r in rows),flush=True)
