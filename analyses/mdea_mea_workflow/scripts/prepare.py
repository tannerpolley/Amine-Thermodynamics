"""Bounded stage-1 preparation for issue 222; no joint-coordinate fitting."""
import copy
import hashlib
import importlib.util
import json
import math
from pathlib import Path
import sys
import zipfile

import numpy as np
import epcsaft
from epcsaft import equilibrium as eq, regression as reg  # noqa: F401 -- reused by bounded preparation scripts

ROOT = Path(__file__).resolve().parents[3]
MAIN = Path('/home/tnnrpolley21/Workspaces/Engineering/Amine-Thermodynamics')
OUT = ROOT / 'analyses/mdea_mea_workflow'
DATA = ROOT / 'data/reference/MDEA'
M, H, W, C = 'methyldiethanolamine', 'protonated-methyldiethanolamine', 'water', 'carbon-dioxide'
BUNDLE = ROOT / 'analyses/mea_parameter_bundle'
sys.path[:0] = [str(ROOT/'src'), str(BUNDLE/'scripts')]
import shared_evaluation as shared
import mea_association_volume as conversion


def sha(p):
    return hashlib.sha256(Path(p).read_bytes()).hexdigest()


def write(p, obj):
    p = OUT/p
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(json.dumps(conversion.jsonable(obj), indent=2, allow_nan=False)+'\n')


def value(v, unit):
    return dict(magnitude=v, unit=unit)


def coef(cid, family, v, unit):
    return dict(family=family, identity=f'component/{cid}/{family}', value=value(v, unit))


def load_method():
    spec = importlib.util.spec_from_file_location('published_mdea', ROOT/'analyses/mdea_kuranov_refit/model.py')
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


published = load_method()
BASE = json.loads((BUNDLE/'results/selected-current-best-parameters.json').read_text())
assert sha(BUNDLE/'results/selected-current-best-parameters.json') == '00e77608a8489fc9e03a7d2a86c08cb5ff782bb441368a62fa6390b8bfe9cc91'


def documents(kappa):
    shared_ids = {W,C,'hydronium-cation','hydroxide-anion','bicarbonate-anion','carbonate-anion'}
    d = copy.deepcopy(BASE)
    d['document_id'] = 'mdea-mea-workflow-stage1'
    d['purpose'] = 'Issue 222 start 1, preparation only'
    d['components'] = [c for c in d['components'] if c['component_id'] in shared_ids]
    d['correlations'] = [c for c in d['correlations'] if c['component_id'] in shared_ids]
    d['pairs'] = [p for p in d['pairs'] if {p['component_id_a'],p['component_id_b']} <= shared_ids]
    d['topology']['sites'] = [s for s in d['topology']['sites'] if s['component_id'] in shared_ids]
    d['topology']['edges'] = [e for e in d['topology']['edges'] if {e['endpoint_a']['component_id'],e['endpoint_b']['component_id']} <= shared_ids]
    d['topology']['no_cross_association'] = [p for p in d['topology'].get('no_cross_association',[]) if {p['component_id_a'],p['component_id_b']} <= shared_ids]
    d['reaction_correlations'] = [r for r in d['reaction_correlations'] if r['reaction_id'] in ('R1','R2','R3')]
    for cid, charge, mass, m, sigma in [(M,0,.1191622,3.675,3.563),(H,1,.12017014,1.,5.50)]:
        entries = [('segment_count',m,'dimensionless'),('segment_diameter',sigma,'angstrom'),('dispersion_energy_over_k',228.711 if cid==M else 228.71,'kelvin'),('solvation_factor',1.,'dimensionless')]
        if charge:
            entries += [('packing_diameter',.88*sigma,'angstrom'),('debye_huckel_diameter',sigma,'angstrom'),('born_diameter',5.,'angstrom')]
        d['components'].append(dict(component_id=cid, provenance='Issue 222 start 1; Pahlavanzadeh 2013 Table 2; Uyan 2015 Tables 3-4',fixed=dict(molar_mass=dict(value=value(mass,'kilogram / mole')),charge_number=dict(value=value(charge,'elementary-charge'))),coefficients=[coef(cid,*e) for e in entries]))
    ids=[c['component_id'] for c in d['components']]
    for i,a in enumerate(ids):
        for b in ids[i+1:]:
            if {a,b} & {M,H} and {a,b}!={H,'hydronium-cation'}:
                d['pairs'].append(dict(component_id_a=a,component_id_b=b,provenance='Issue 222 start 1: MDEA-specific interaction zero',coefficients=[dict(family='k_ij',identity=f'pair/{a}/{b}/k_ij',value=value(0.,'dimensionless'))]))
    source = published.document()['topology']
    for s in source['sites']:
        if s['component_id']==M: d['topology']['sites'].append(copy.deepcopy(s))
    edge=copy.deepcopy(next(e for e in source['edges'] if e['endpoint_a']['component_id']==M and e['endpoint_b']['component_id']==M))
    edge['volume']['value']['magnitude']=kappa
    d['topology']['edges'].append(edge)
    for e in source['edges']:
        if {e['endpoint_a']['component_id'],e['endpoint_b']['component_id']}=={M,W}:
            e=copy.deepcopy(e); e.pop('volume_correction',None)
            # Reuse the selected water and newly declared MDEA owners.
            water_edge=next(x for x in d['topology']['edges'] if x['endpoint_a']['component_id']==W and x['endpoint_b']['component_id']==W)
            e['source']['inputs']={q:[water_edge[q]['identity'],edge[q]['identity']] for q in ('energy_over_k','volume')}
            d['topology']['edges'].append(e)
    for ion in (M,H):
        d['topology']['no_cross_association'].append(dict(component_id_a=ion,component_id_b=C,provenance='Issue 222; Uyan 2015 section 4.1'))
    b=copy.deepcopy(d)
    component=next(c for c in b['components'] if c['component_id']==H)
    component['fixed']['charged_molecule_ion']=dict(value=value(1,'dimensionless'))
    for c in component['coefficients']:
        if c['family']=='segment_count': c['value']['magnitude']=3.675
        if c['family'] in ('segment_diameter','debye_huckel_diameter'): c['value']['magnitude']=3.563
    component['coefficients']=[c for c in component['coefficients'] if c['family']!='packing_diameter']
    for s in source['sites']:
        if s['component_id']==H:b['topology']['sites'].append(copy.deepcopy(s))
    selfh=copy.deepcopy(next(e for e in source['edges'] if e['endpoint_a']['component_id']==H and e['endpoint_b']['component_id']==H))
    selfh['volume']['value']['magnitude']=kappa
    b['topology']['edges'].append(selfh)
    for other, oe in [(W,water_edge),(M,edge)]:
        for donor, acceptor in ((H,other),(other,H)):
            b['topology']['edges'].append(dict(endpoint_a=dict(component_id=donor,site_id='a'),endpoint_b=dict(component_id=acceptor,site_id='b'),source=dict(kind='combining-rule',rule_id='wolbach-sandler',provenance='Uyan 2015 Table 4 footnote a; issue 222',inputs={q:[selfh[q]['identity'],oe[q]['identity']] for q in ('energy_over_k','volume')})))
    # Shared records and shared interactions must remain byte-equivalent as JSON values.
    for candidate in (d,b):
        assert [c for c in candidate['components'] if c['component_id'] in shared_ids]==[c for c in BASE['components'] if c['component_id'] in shared_ids]
        assert [p for p in candidate['pairs'] if {p['component_id_a'],p['component_id_b']} <= shared_ids]==[p for p in BASE['pairs'] if {p['component_id_a'],p['component_id_b']} <= shared_ids]
    return d,b


def kappa_conversion():
    # Reuse the MEA saturation solve, parameter substitution and native observation declaration.
    d=published.document()
    d['components']=[c for c in d['components'] if c['component_id']==M]
    d['correlations']=[c for c in d['correlations'] if c['component_id']==M]
    d['pairs']=[]
    d['reaction_correlations']=[]
    # Published no-Born families retained for pure saturation.
    d['topology']={key:[v for v in vals if (v['component_id']==M if key=='sites' else v['endpoint_a']['component_id']==M and v['endpoint_b']['component_id']==M)] for key,vals in d['topology'].items()}
    conversion.DOCUMENT=d
    conversion.MEA=M
    conversion.EDGE='association/methyldiethanolamine/volume'
    conversion.OUT=OUT/'results/kappa'
    conversion.OUT.mkdir(parents=True,exist_ok=True)
    conversion.REFERENCES=[conversion.state(.123858*(1-.12*math.exp(-3*228.711/T))**3,T) for T in [293.15+5*i for i in range(21)]]
    write('results/kappa/reference.json',conversion.REFERENCES)
    params=conversion.parameters(.123858)
    observations=[]
    declarations=[]
    for r in conversion.REFERENCES:
        for kind,key,extra in [('pressure','p_Pa',{}),('phase_density','rho_L_mol_m3',dict(phase='L',mass_basis=False))]:
            observations.append(reg.observation(params,kind,conversion.problem(r['T_K']),observed=r[key],scale=r[key],form='difference',**extra))
            declarations.append(dict(T_K=r['T_K'],kind=kind,observed=r[key],scale=r[key],weight=1.,form='difference',**extra))
    coordinate=reg.coordinate(params,[('association_volume',((M,'a'),(M,'b')),1.)],origin=.123858,scale=.123858,bounds=(.123858*.88**3,.123858))
    controls=dict(maximum_iterations=100,maximum_elapsed_time_seconds=60,function_tolerance=1e-12,gradient_tolerance=1e-12,parameter_tolerance=1e-10,workers=0)
    write('results/kappa/declaration.json',dict(observations=declarations,controls=controls,source='MEA mea_association_volume.py main least-squares declaration'))
    fit=reg.fit(params,[coordinate],observations,weights=[1.]*42,controls=reg.FitControls(**controls))
    write('results/kappa/fit.json',fit)
    assert fit.usable and fit.status=='converged',fit.message
    k=float(format(fit.physical[0],'.8g'))
    rows=[dict(r,reference=ref) for ref in conversion.REFERENCES for r in [conversion.state(k,ref['T_K'])]]
    write('results/kappa/replay.json',rows)
    summary=dict(kappa=k,unrounded=fit.physical[0],pressure_aard_percent=100*np.mean([abs(r['p_Pa']/r['reference']['p_Pa']-1) for r in rows]),density_aard_percent=100*np.mean([abs(r['rho_L_mol_m3']/r['reference']['rho_L_mol_m3']-1) for r in rows]),max_equilibrium_residual=max(abs(v) for line in (conversion.OUT/'solves.jsonl').read_text().splitlines() for v in json.loads(line)['result']['residuals']),status='complete',reason='Owner accepted kappa=0.11800686 fixed to eight significant figures, issue 222 Stage-1 owner decisions 2026-10-28.')
    write('results/kappa/summary.json',summary)
    return k


def main():
    wheel=MAIN/'build/engine-wheels/main-3e83e19ccc771b51d8ebc038931ab25192f4c5b5/epcsaft-0.2.0.dev0-cp313-cp313-manylinux_2_39_x86_64.whl'
    assert sha(wheel)==shared.ENGINE_WHEEL_SHA256
    with zipfile.ZipFile(wheel) as z:
        assert all((Path(epcsaft.__file__).parent.parent/n).read_bytes()==z.read(n) for n in z.namelist() if n.startswith('epcsaft/') and not n.endswith('/'))
    write('inputs/runtime.json',dict(wheel=str(wheel),wheel_sha256=sha(wheel),installed_files_byte_identical=True,module=epcsaft.__file__,parameter_sha256=sha(BUNDLE/'results/selected-current-best-parameters.json'),method_hashes={str(p.relative_to(ROOT)):sha(p) for p in [BUNDLE/'scripts/mea_association_volume.py',BUNDLE/'scripts/fit_observations.py',BUNDLE/'scripts/fit_campaign.py']}))
    try:k=kappa_conversion()
    except Exception as e:
        write('results/kappa/failure.json',dict(error=f'{type(e).__name__}: {e}'))
        raise
    for variant,d in zip('AB',documents(k)):
        write(f'inputs/variant-{variant}.json',d)
    print('kappa',k,flush=True)


if __name__=='__main__':main()
