"""Assess adopted DEA and MDEA neutral components at the primary measured states."""
from collections import defaultdict
from pathlib import Path
from tempfile import TemporaryDirectory
from time import monotonic

from common import HERE, ROOT, fingerprints, save
from objective import REPORTED
from part_ii import Route, epcsaft, eq, deviation_statistics, stable
from amp import DECLARATION
from reconcile import read_csv

DEA = 'diethanolamine'
MDEA = 'methyldiethanolamine'
DEA_SELECTION = ROOT / 'analyses/dea_transfer/results/refit-413/selection.json'
DENSITY = HERE / 'inputs/Neumann2022_Table1_pure_MDEA.csv'
MDEA_VAPOR = HERE / 'inputs/Kim2008_Table3_pure_MDEA.csv'
DEA_DENSITY = HERE / 'inputs/Alvarez2010_pure_DEA.csv'
SATURATION = [ROOT / 'data/reference/DEA' / name for name in
              ('Horstmann2002_Table1_pure_DEA.csv', 'Klepacova2011_Table4_pure_DEA.csv')]
PDF_HASH = '73c47016f62d6bfd2eb5c4b3079339b3c19f6a1b9f0f2d5c79b566c453bd13b9'


def assess(compound, mapping, source_rows, saturated):
    pure = epcsaft.Pure(epcsaft.Parameters.from_mapping(mapping, components=[compound]))
    mixture = epcsaft.Mixture(epcsaft.Parameters.from_mapping(mapping))
    mass = next(c for c in mapping['components'] if c['component_id']==compound)['fixed']['molar_mass']['value']['magnitude']
    result = []
    for s in source_rows:
        T = float(s['T_K'])
        row = dict(source=s, compound=compound, T_K=T, saturation=saturated)
        result.append(row)
        try:
            if saturated:
                problem = pure.saturation(T)
                solved = eq.solve_equilibrium(pure, problem)
                row.update(P_observed_Pa=1000*float(s['P_kPa']),
                           U_P_Pa=1000*float(s['U_P_kPa']) if s.get('U_P_kPa') else None,
                           message=solved.message, tolerance=problem.row_tolerance)
                if not solved.requested_tolerance_met:
                    continue
                rho_l, rho_v = solved.molar_densities
                P = solved.pressure
                liquid, vapor = (pure.state(T,rho=d) for d in (rho_l,rho_v))
                row.update(pressure_Pa=P, solved_pressure_residuals_Pa=[liquid.pressure-P,vapor.pressure-P],
                           fugacity_log_ratio=liquid.log_fugacity_coefficient[0]-vapor.log_fugacity_coefficient[0],
                           vapor_density_mol_m3=rho_v, density_roots_distinct=rho_l>rho_v,
                           max_equilibrium_residual=max(map(abs, solved.residuals),default=0.))
                # Reclose at imposed P to separate readback of the returned saturation
                # densities from an independent check on both density branches.
                qualified = [pure.state(T,P=P,phase=root) for root in ('liquid','vapor')]
                row['reclosed'] = dict(
                    density_mol_m3=[s.molar_density for s in qualified],
                    pressure_residuals_Pa=[s.pressure-P for s in qualified],
                    fugacity_log_ratio=qualified[0].log_fugacity_coefficient[0]-qualified[1].log_fugacity_coefficient[0],
                    branch_mismatch=[s.density_branch_mismatch for s in qualified])
            else:
                P = float(s['P_MPa'])*1e6
                liquid = pure.state(T,P=P,phase='liquid')
                rho_l = liquid.molar_density
                row.update(pressure_Pa=P,density_observed_kg_m3=float(s['density_kg_m3']),
                           U_density_kg_m3=float(s['U_density_kg_m3']), pressure_residual_Pa=liquid.pressure-P)
            reduction = mixture.state(T,rho=rho_l,x={compound:1.})
            row.update(density_mol_m3=rho_l, density_kg_m3=rho_l*mass, branch=liquid.returned_density_branch.name,
                       pure_limit_pressure_difference_Pa=reduction.pressure-liquid.pressure,
                       pure_limit_helmholtz_difference=reduction.residual_helmholtz-liquid.residual_helmholtz)
        except (ValueError, RuntimeError, AttributeError) as error:
            row.update(refusal=f'{type(error).__name__}: {error}')
    return result


def calculate(work):
    started = monotonic()
    Route(DECLARATION, work)
    dea = stable.read(DEA_SELECTION)['chosen']['parameters']['parameters']
    mdea = stable.read(REPORTED)['parameters']
    rows = assess(DEA, dea, [r for p in SATURATION for r in read_csv(p) if float(r['T_K'])<=458.60], True)
    density_rows = [dict(r,source_key='Neumann2022',pdf_attachment_key='4V38X73R',
                         locator='Table 1, PDF p.5', purity_percent=99.9) for r in read_csv(DENSITY)]
    rows += assess(MDEA,mdea,density_rows,False)
    vapor_rows = [dict(r,source_key='Kim2008',pdf_attachment_key='4SMCK4SC',locator='Table 3, PDF p.2',
                       purity_percent=99) for r in read_csv(MDEA_VAPOR)]
    rows += assess(MDEA,mdea,vapor_rows,True)
    rows += assess(DEA,dea,[dict(r,source_key='Alvarez2010',locator='Table 1, pure diethanolamine',purity_percent=99,
                                  doi='10.1021/je900739x') for r in read_csv(DEA_DENSITY)],False)
    sources = defaultdict(list)
    for row in rows:
        sources[row['source']['source_key']].append(row)
    summary = {}
    for key, rr in sources.items():
        obs, calc, unit = ('P_observed_Pa','pressure_Pa','Pa') if rr[0]['saturation'] else ('density_observed_kg_m3','density_kg_m3','kg/m³')
        pair = [(r[obs],r[calc]) for r in rr if r.get(calc) is not None]
        summary[key] = dict(total=len(rr), T_range_K=[min(r['T_K'] for r in rr),max(r['T_K'] for r in rr)],
                            missing=[r['source']['source_row'] for r in rr if r.get(calc) is None],
                            worst=max((r for r in rr if r.get(calc) is not None), key=lambda r:abs(r[calc]/r[obs]-1),default=None),
                            **(deviation_statistics(pair, unit) if pair else {}))
    pure_fit_sources = {
        DEA: dict(source='Nasrifar and Tafazzol (2010), Table 2 and Eq. 38',
                  targets='Yaws smoothed saturation pressure and saturated liquid density',
                  exact_temperature_nodes='Unreported in the checked source; primary comparison row independence is unresolved'),
        MDEA: dict(source='Pahlavanzadeh and Fakouri Baygi (2013), §3.1, Table 2',
                   targets='DIPPR saturation pressure and saturated liquid density correlations, Eqs. 9–10',
                   temperature_interval_K=[303.15,443.15],
                   exact_temperature_nodes='Unreported in the checked source; primary comparison row independence is unresolved'),
    }
    save('E/pure-properties.json', dict(rows=rows, summary=summary, pure_fit_sources=pure_fit_sources,
         Neumann_PDF_sha256=PDF_HASH, projection_minutes=[1,3],
         Kim_PDF_sha256='76084d83956da30832ef6eb0ef1d2a911c31305fef0d7f944735915fe207c1a6',
         ThermoML=dict(Alvarez2010='41ec8b63968a66e85916b1fe2ce8a04e3c7a496ce751af16758b0e5547b6b867',
                       Kim2008='51baf217f8b5f257b4c5c26ec4713d84bc714c8775fffbd01af931591160e9c7'),
         inputs=fingerprints(DEA_SELECTION,REPORTED,DENSITY,MDEA_VAPOR,DEA_DENSITY,*SATURATION)), start=started)


if __name__ == '__main__':
    with TemporaryDirectory() as directory:
        calculate(Path(directory))
