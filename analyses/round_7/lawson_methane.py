"""Conditional Lawson–Garst gas and liquid pressure readback."""
import math
import sys
from time import monotonic

import numpy as np
from scipy.optimize import minimize_scalar

from receivers import DEA, OUT, WORK, Route, a, r, save, transfer

GAUGE_PA = 1000 * 6894.757293168 + 101325
CRITICAL_T = np.array([304.18,190.6])
CRITICAL_P = np.array([7.380e6,4.61e6])


def log_phi(T, co2, methane):
    """Redlich–Kwong (1949), eqs. 2, 4, 5, 15, 18, 27, dry CO2–CH4."""
    pressure = co2+methane
    y = np.array([co2,methane])/pressure
    Ai = np.sqrt(.4278*(CRITICAL_T/T)**2.5*pressure/CRITICAL_P)
    Bi = .0867*(CRITICAL_T/T)*pressure/CRITICAL_P
    A = y@Ai
    B = y@Bi
    Z = max(v.real for v in np.roots([1.,-1.,A*A-B-B*B,-A*A*B]) if abs(v.imag)<1e-10 and v.real>B)
    return Bi[0]/B*(Z-1)-math.log(Z-B)-(A*A/B)*(2*Ai[0]/A-Bi[0]/B)*math.log1p(B/Z)


def methane(point, path, label):
    start = monotonic()
    run = Route(DEA,WORK/f'F/methane-{label}')
    spec = run.bind(point)
    idx = list(spec.parameters.component_ids).index('carbon-dioxide')
    out = []
    for row in spec.inputs['observations']['fitted']:
        if row['group'] != 'Lawson':
            continue
        observed = row['arguments']['observed']
        problem = spec.problems[row['problem']]
        result = r.eq.solve_equilibrium(spec.model,problem)
        record = dict(identity=row['identity'],source=row['row'],T_K=problem.T,observed_Pa=observed,
                      feed_mol=problem.feed.values,status=result.message)
        out.append(record)
        if not result.requested_tolerance_met:
            continue
        P = result.pressure
        x = list(result.phase_mole_fractions(0))
        p_hat = P*result.phase_mole_fractions(1)[idx]
        # Keep the methane-free liquid composition; ignore water and DEA in the dry gas RK mixture.
        liquid_reference = spec.model.state(problem.T,rho=result.molar_densities[0],x=x)
        base_phi = log_phi(problem.T,observed,0.)
        base_logf = math.log(P)+liquid_reference.log_fugacity_coefficient[idx]
        # Observed pCO2 and non-CO2 vapour pressure both consume part of the gauge span.
        water_amine = P-p_hat
        maximum = max(0.,GAUGE_PA-observed-water_amine)
        record.update(methane_free_pCO2_Pa=p_hat,methane_free_P_Pa=P,residual_Pa=p_hat-observed,
                      dry_methane_range_Pa=[0.,maximum],liquid_x=x,conditional_other_vapour_Pa=water_amine)
        def corrections(p):
            liquid = spec.model.state(problem.T,P=P+p,x=x,phase='liquid')
            dl = (math.log(P+p)+liquid.log_fugacity_coefficient[idx])-base_logf
            dg = log_phi(problem.T,observed,p)-base_phi
            return (dg,dl,dl-dg)
        try:
            nodes = np.linspace(0.,maximum,33)
            values = [corrections(float(p)) for p in nodes]
            bounds = {}
            for i,key in enumerate(('delta_log_phi_gas','delta_log_f_liquid','delta_log_pCO2')):
                candidates = [(float(nodes[0]),values[0][i]),(float(nodes[-1]),values[-1][i])]
                for j in range(1,len(nodes)-1):
                    v0,v1,v2 = [values[k][i] for k in (j-1,j,j+1)]
                    if (v1-v0)*(v2-v1)<0:
                        sign = 1 if v1 < v0 else -1
                        opt = minimize_scalar(lambda p: sign*corrections(p)[i], method='bounded',
                                              bounds=(nodes[j-1],nodes[j+1]))
                        candidates.append((float(opt.x),float(sign*opt.fun)))
                bounds[key] = [min(candidates,key=lambda k:k[1]),max(candidates,key=lambda k:k[1])]
            record.update(log_extrema=bounds,nodes_Pa=nodes,node_values=values,
                  pCO2_change_Pa=[p_hat*math.expm1(v) for _,v in bounds['delta_log_pCO2']])
        except (RuntimeError,ValueError,TypeError) as exc:
            record['refusal'] = str(exc)
    name = 'methane.json.gz' if label=='historical' else 'methane-refit.json.gz'
    save(OUT/'F'/name,dict(rows=out,seconds=monotonic()-start,endpoint_sha256=r.s.sha256(path),wheel_sha256=r.SHA,
         conditional=True,total_gauge_limit_Pa=GAUGE_PA,source='Lawson and Garst (1976), Experimental and Calculations pp. 21 and 25, Table II p. 23, APKXH9KU',
         coefficients=dict(temperature_K=CRITICAL_T,pressure_Pa=CRITICAL_P,
             source=['https://webbook.nist.gov/cgi/cbook.cgi?ID=C124389&Mask=4',
                     'https://webbook.nist.gov/cgi/cbook.cgi?ID=C74828&Mask=4','https://doi.org/10.1021/cr60137a013']),
         basis='1000 psig plus 101325 Pa. Dry CO2/CH4 RK mixtures and fixed methane-free liquid composition. Shifts evaluated at measured gas pCO2 as a local conditional sensitivity.',
         unconstrained='Liquid methane uptake and its effect on the reactive liquid composition are not bounded by Table II.'))


if __name__=='__main__':
    a.study.reuse.bind_wheel()
    r.verify()
    path = OUT/'F/selection.json.gz' if sys.argv[1]=='refit' else transfer.DEABASE.parent/'salt-anchored-435/campaign/selection.json.gz'
    result = r.read(path)
    methane(result['selected'][2] if sys.argv[1]=='refit' else result['chosen']['parameters'],path,sys.argv[1])
