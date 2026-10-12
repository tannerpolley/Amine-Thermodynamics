"""Single-liquid and bubble checks for rows still unavailable after two starts."""
import concurrent.futures
import multiprocessing
import permittivity_probe as s

ROWS = s.read(s.OUT/'flash-family.json')
RECOVERED = {(r['basis'],r['variant'],r['index']) for r in s.read(s.OUT/'flash-family-recovery.json') if r['accepted']}
FAILED = [r for r in ROWS if not r['accepted'] and (r['basis'],r['variant'],r['index']) not in RECOVERED]


def diagnose(row):
    basis, name = row['basis'], row['variant']
    model = s.mixture(s.VARIANTS[name] if basis=='current' else s.engine_variant(name))
    p = s.flash_problem(basis,row['loading'],row['temperature_K'],row['pressure_Pa'],[s.h.eq.Phase('L',kind='liquid')])
    out = {k:row[k] for k in ('basis','variant','index','loading','temperature_K','pressure_Pa')}
    try:
        liquid = s.h.eq.solve_equilibrium(model,p)
        out.update(liquid_accepted=liquid.success,liquid_message=liquid.message,liquid_residual=liquid.convergence.residual,
            liquid_density_mol_m3=list(liquid.molar_densities),liquid_objective_over_RT=liquid.objective)
        if liquid.success:
            p.phases = [s.h.eq.Phase('L',kind='liquid',composition_guess=liquid.mole_fractions[:9],packing_guess=liquid.packing_fractions[0]),
                s.h.eq.Phase('V',kind='vapor',support=s.s.COMPONENT_IDS[:3],amount=s.h.eq.Pinned(0.))]
            p.P = s.h.eq.Free(row['pressure_Pa'])
            bubble = s.h.eq.solve_equilibrium(model,p)
            out.update(bubble_accepted=bubble.success,bubble_message=bubble.message,bubble_residual=bubble.convergence.residual)
            if bubble.success:
                out.update(bubble_pressure_Pa=bubble.pressure[0],family_P_over_bubble_P=row['pressure_Pa']/bubble.pressure[0])
    except Exception as error:
        out['message']=f'{type(error).__name__}: {error}'
    return out


if __name__=='__main__':
    with concurrent.futures.ProcessPoolExecutor(16,mp_context=multiprocessing.get_context('fork')) as pool:
        rows=list(pool.map(diagnose,FAILED))
    s.save('flash-family-remaining-diagnosis.json',rows)
    s.table('flash-family-remaining-diagnosis.csv',rows)
    print('CHECKED',len(rows),'LIQUID',sum(r.get('liquid_accepted',False) for r in rows),'BUBBLE',sum(r.get('bubble_accepted',False) for r in rows),flush=True)
