"""Compare chain and volume-matched spherical MDEAH+ with fixed electrostatic diameters."""
from pathlib import Path
from tempfile import TemporaryDirectory
from time import monotonic
import math

from common import fingerprints, save
from objective import MDEA, REPORTED, fit, information, q3_checks
from part_ii import Route, stable

CATION = 'protonated-methyldiethanolamine'


def calculate(work):
    started = monotonic()
    route = Route(MDEA, work)
    point = stable.read(REPORTED)
    mapping = point['parameters']
    coordinates = [q for q in point['coordinates'] if not any(t[:2] == ['segment_diameter', CATION] for t in q['targets'])]
    assert len(coordinates) == len(point['coordinates'])-1
    assert not any(c.get('component_id')==CATION and c.get('family')=='segment_diameter' for c in mapping['correlations'])
    chain = dict(point, coordinates=coordinates)
    values = stable.s.parameter_values(mapping)
    m_id, sigma_id = [f'component/{CATION}/{family}' for family in ('segment_count','segment_diameter')]
    m, sigma = values[m_id], values[sigma_id]
    mapped = sigma * math.cbrt(m)
    sphere = dict(chain, parameters=stable.s.with_parameter_values(mapping, {m_id:1., sigma_id:mapped}))
    assert math.isclose(m*sigma**3, mapped**3, rel_tol=1e-14)
    assert mapping['topology'] == sphere['parameters']['topology']
    assert {k for k,v in stable.s.parameter_values(sphere['parameters']).items() if values[k]!=v} == {m_id,sigma_id}
    save('E/cation-geometry.json', dict(m=m, sigma_A=sigma, spherical_sigma_A=mapped, m_sigma_cubed_A3=m*sigma**3,
         qualified_temperature_interval_K=route.config['calculation_interval_K'], diameter_law='constant for this component',
         unchanged_electrostatic_diameters_A={k: v for k,v in values.items() if CATION in k and k.endswith(('born_diameter','debye_huckel_diameter'))},
         inputs=fingerprints(MDEA, REPORTED)), start=started)
    for label, start in (('chain',chain),('sphere',sphere)):
        tick = monotonic()
        result = fit(route, label, start)
        save(f'E/cation-{label}-fit.json.gz', result, start=tick)
        for when, p in (('before',start),('after',result['point'])):
            if p is None:
                continue
            try:
                assessment = dict(information=information(route,p), Q3=q3_checks(route,p))
                spec = route.bind(p)
                terms = []
                for r in assessment['Q3']:
                    if r.get('phases'):
                        phase = r['phases'][0]
                        state = spec.model.state(r['T_K'],rho=phase['density_mol_m3'],x=phase['x'])
                        terms.append(dict(key=r['key'], hard_chain=state.hard_chain,dispersion=state.dispersion,
                                          rho=phase['density_mol_m3'],x=phase['x']))
                assessment['parent_EOS_contributions'] = terms
            except (AssertionError, ValueError, RuntimeError) as error:
                assessment = dict(refusal=f'{type(error).__name__}: {error}')
            save(f'E/cation-{label}-{when}.json.gz', assessment, start=tick)
    save('E/cation-timing.json', dict(projection_minutes=[2,5]), start=started)


if __name__ == '__main__':
    with TemporaryDirectory() as directory:
        calculate(Path(directory))
