"""Issue 172, Design section 3: Agieienko S1/S2 and Yang Eqs. 1a/2a/2b."""
import copy
import csv
import hashlib
import importlib.metadata
import json
import os
from pathlib import Path
import sys
import zipfile

for key in ('OMP_NUM_THREADS', 'OPENBLAS_NUM_THREADS', 'MKL_NUM_THREADS'):
    os.environ[key] = '1'
import epcsaft
import numpy as np

OUT = Path(__file__).resolve().parent
ROOT = OUT.parents[3]
WHEEL = Path('/home/tnnrpolley21/Workspaces/Engineering/ePC-SAFT/build/wheels/main-81d1e38a/epcsaft-0.2.0.dev0-cp313-cp313-linux_x86_64.whl')
SHA = '3fd8140211aac1fb1e82807f066cdf507be733b36c6c27bf41377e7bb939aa86'
CURRENT = OUT.parent / 'selected-current-best-parameters.json'
A, C, T = .3777, 1403., 298.15
K = C / T - 1


def write(path, value):
    path.write_text(json.dumps(value, indent=2, allow_nan=False) + '\n')


def coefficients(q):
    delta = q[0]**2 - 4*K*A*q[1]
    if delta < 0:
        return delta, []
    values = []
    for sign in (-1, 1):
        u = (q[0] + sign*np.sqrt(delta))/(2*K)
        v = T*(q[0]-K*u)/A
        values.append(dict(dielectric_volume_L_mol=float(A+u), dielectric_temperature_K=float(C+v),
            admissible=bool(A+u > 0 and C+v > 393.15)))
    return float(delta), values


def declaration(record, pair):
    result = copy.deepcopy(record)
    next(f for f in result['model_families'] if f['kind'] == 'permittivity')['choice'] = 'solvent-density-temperature'
    result['correlations'] = [r for r in result['correlations'] if r['family'] != 'relative_permittivity']
    template = json.loads((OUT.parent/'permittivity-screen-172/MEA-1403-CO2-near-zero-parameters.json').read_text())
    result['sources'].extend(r for r in template['sources'] if r['source_id'] == 'permittivity-screen-172')
    for component in result['components']:
        component['coefficients'] = [r for r in component['coefficients'] if r['family'] != 'relative_permittivity']
        original = next(c for c in template['components'] if c['component_id'] == component['component_id'])
        for coefficient in original['coefficients']:
            if coefficient['family'] in ('dielectric_volume', 'dielectric_temperature'):
                coefficient = copy.deepcopy(coefficient)
                if component['component_id'] == 'monoethanolamine':
                    coefficient['value']['magnitude'] = pair['dielectric_volume_L_mol'] if coefficient['family'] == 'dielectric_volume' else pair['dielectric_temperature_K']
                component['coefficients'].append(coefficient)
    return result


def measured_provenance(record):
    result = copy.deepcopy(record)
    source = 'permittivity-refit-172'
    result['sources'] = [r for r in result['sources'] if r['source_id'] not in ('permittivity-screen-172',source)]
    result['sources'].append(dict(source_id=source,citation='Issue172 accepted design/amendment2; Yang2024 Table6; AgieienkoBuchner2024 ESI S1/S2',
        use_basis='Two-branch dielectric calibration and reactive comparison; not adopted'))
    locators = {'water':'Yang2024 Table6 fixed water dV=0.3777 L/mol dT=1403 K',
        'monoethanolamine':'dielectric/reduction.json; admitted ESI p2 Tables S1/S2 SHA256 e928ae3242dc38612f0fbf44e7e1e42c296ca49e3638ac4ef2f08a6c50f0f5c2',
        'carbon-dioxide':'Issue172 Design section2; assumed near-zero-volume CO2 coefficients; not measured'}
    for component in result['components']:
        for coefficient in component['coefficients']:
            if coefficient['family'] in ('dielectric_volume','dielectric_temperature'):
                coefficient['provenance'].update(source_id=source,locator=locators[component['component_id']])
    return result


def main():
    assert hashlib.sha256(WHEEL.read_bytes()).hexdigest() == SHA
    assert hashlib.sha256(CURRENT.read_bytes()).hexdigest() == '66ff7715958e9d22e77bd129faf7f67822204e3285b50993bf3f67d72c3b9778'
    package = Path(epcsaft.__file__).resolve().parent
    assert package.is_relative_to(Path(sys.prefix).resolve())
    with zipfile.ZipFile(WHEEL) as archive:
        for name in archive.namelist():
            if name.startswith('epcsaft/') and not name.endswith('/'):
                assert (package.parent/name).read_bytes() == archive.read(name), name
    record = json.loads(CURRENT.read_text())
    ids = [c['component_id'] for c in record['components']]
    model = epcsaft.Mixture(epcsaft.Parameters.from_mapping(record, components=ids))
    masses = {c['component_id']:c['fixed']['molar_mass']['value']['magnitude'] for c in record['components']}
    rows = list(csv.DictReader((OUT/'inputs/agieienko-buchner-2024.csv').open()))
    compositions, densities, fractions = [], [], []
    for row in rows:
        w = float(row['MEA_wt_percent'])/100
        amounts = {'monoethanolamine':w/masses['monoethanolamine'], 'water':(1-w)/masses['water']}
        x = [amounts.get(i,0.)/sum(amounts.values()) for i in ids]
        state = model.state(T, P=101325., x=x, phase='liquid')
        compositions.append(x)
        densities.append(state.molar_density/1000)
        fractions.append(x[ids.index('monoethanolamine')])
        row.update(derived_MEA_mole_fraction=fractions[-1], native_density_mol_L=densities[-1],
            native_density_kg_m3=state.molar_density*sum(x[i]*masses[c] for i,c in enumerate(ids)),
            native_pressure_Pa=state.pressure)
    x, r = np.array(fractions), np.array(densities)
    observed = np.array([float(row['epsilon_s']) for row in rows])
    scale = .01*observed
    H = np.column_stack((r*x,r*x*x))
    q, _, rank, singular = np.linalg.lstsq(H/scale[:,None], (observed-1-r*A*K)/scale, rcond=None)
    delta, pairs = coefficients(q)
    predicted = 1+r*(A*K+q[0]*x+q[1]*x*x)
    covariance = np.linalg.inv((H/scale[:,None]).T@(H/scale[:,None])) if rank == 2 else None
    result = dict(q=q.tolist(), rank=int(rank), singular_values=singular.tolist(), discriminant=delta,
        branches=pairs, scale_covariance=None if covariance is None else covariance.tolist(),
        cost=float(.5*np.sum(((predicted-observed)/scale)**2)),
        wheel_sha256=SHA, installed_module=str(package), python=sys.version,
        packages={p:importlib.metadata.version(p) for p in ('epcsaft','numpy','scipy')},
        assumptions='Neutral unloaded MEA-water at 101325 Pa; no volume translation; small protonation neglected.',
        sensitivity=[])
    for factor in (.99,1.01):
        shifted = np.linalg.lstsq(H/scale[:,None], (factor*observed-1-r*A*K)/scale,rcond=None)[0]
        shifted_delta, shifted_pairs = coefficients(shifted)
        result['sensitivity'].append(dict(coherent_permittivity_factor=factor,q=shifted.tolist(),
            discriminant=shifted_delta,branches=shifted_pairs))
    for i,row in enumerate(rows):
        row.update(reduced_epsilon=float(predicted[i]), residual_epsilon=float(predicted[i]-observed[i]),
            weighted_residual=float((predicted[i]-observed[i])/scale[i]))
    for label,pair in zip(('smaller-dV','larger-dV'),pairs,strict=True):
        candidate = declaration(record,pair)
        native = epcsaft.Mixture(epcsaft.Parameters.from_mapping(candidate,components=ids))
        replay = [native.state(T,rho=densities[i]*1000,x=composition).bulk_relative_permittivity
                  for i,composition in enumerate(compositions)]
        pair['max_abs_native_replay_epsilon'] = float(np.max(np.abs(np.array(replay)-predicted)))
        for i,row in enumerate(rows):
            row[label+'_epsilon'] = replay[i]
        if pair['admissible']:
            directory = OUT/label
            directory.mkdir(exist_ok=True)
            write(directory/'dielectric-parameters.json',candidate)
        if covariance is not None:
            u = pair['dielectric_volume_L_mol']-A
            v = pair['dielectric_temperature_K']-C
            transform = np.linalg.inv(np.array([[K,A/T],[v/T,u/T]]))
            pair['scale_covariance_dV_dT'] = (transform@covariance@transform.T).tolist()
    write(OUT/'dielectric/reduction.json',result)
    with (OUT/'dielectric/rows.csv').open('w',newline='') as stream:
        writer = csv.DictWriter(stream,list(rows[0]),lineterminator='\n')
        writer.writeheader(); writer.writerows(rows)
    print(json.dumps(result,indent=2),flush=True)
    assert rank == 2 and len(pairs) == 2 and delta > 0, 'Design requires two distinct real branches'
    assert all(p['admissible'] for p in pairs), 'Design amendment required: inadmissible dielectric branch'
    assert all(p['max_abs_native_replay_epsilon'] <= 1e-10 for p in pairs), 'Native dielectric replay failed'


if __name__ == '__main__':
    main()
