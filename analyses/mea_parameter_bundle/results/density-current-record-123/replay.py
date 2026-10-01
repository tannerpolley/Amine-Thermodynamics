import copy, csv, hashlib, importlib.metadata, json, math, sys, zipfile
from pathlib import Path
root = Path(__file__).resolve().parents[4]
sys.path[:0] = [str(root / 'analyses/mea_parameter_bundle/scripts'), str(root / 'src')]
import shared_evaluation as s
import epcsaft
s.verify_wheel()
assert s.sha256(s.PARAMETERS) == '9055458d8b7cd767a0d08e9f37e4fd28631e29c363364d7b842ebade645cb241'
d = importlib.metadata.distribution('epcsaft')
with zipfile.ZipFile(s.installed_wheel()) as z:
    for name in z.namelist():
        if not name.endswith('/') and not name.endswith('/RECORD'):
            assert hashlib.sha256(Path(d.locate_file(name)).read_bytes()).digest() == hashlib.sha256(z.read(name)).digest()
idx = int(sys.argv[1])
t, a, observed, expected = [(50,.3,1.0580,1.1972948357556386), (50,.4,1.0830,1.2758152292749247), (70,.3,1.0464,1.1823542187429583), (70,.4,1.0719,1.2583197324472444), (50,.000101,.9981,.9938731010497854)][idx]
mapping = s.parameter_mapping()
mass = {c['component_id']:float(c['fixed']['molar_mass']['value']['magnitude']) for c in mapping['components']}
masses = [mass[k] for k in s.COMPONENT_IDS]
model = epcsaft.Mixture(epcsaft.Parameters.from_mapping(mapping))
template = next(o['request'] for o in s.load_state_packet()['observations'] if o['identity'] == 'Bottinger2008_state_046')
req = copy.deepcopy(template)
req['temperature']['value'] = t + 273.15
req['reaction_system']['feed_amounts_mol'][0] = a - .0001
req['reaction_system']['conserved_totals'] = [2+a,1.0]
req = s.corrected_request(req,s.reaction_values(mapping))
system = req['reaction_system']
feed = system['feed_amounts_mol']
totals = [math.fsum(c*n for c,n in zip(row,feed)) for row in system['balance_matrix']]
loading = (totals[0]-2*totals[1])/totals[1]
assert abs(loading-a) < 1e-14
result = s._solve_in_child(model,s._problem_from_request(req),timeout_s=895,request=req)
liquid = next(p for p in result.phases if p['role']=='liquid')
rho = liquid['molar_density_mol_m3']*math.fsum(x*m for x,m in zip(liquid['mole_fractions'],masses))/1000
evidence = dict(result.evidence)
stationarity = evidence['compiled_point_evaluation']['raw_stationarity_max_abs']
assert result.status == 'evaluated' and result.solver_status == 'SUCCESS'
assert evidence['requested_tolerance_met'] and not evidence.get('validation_errors',[])
assert math.isfinite(rho) and rho > 0 and abs(rho-expected) < 1e-9
row = dict(state=f'Amundsen2009_{t}C_loading_{a}',temperature_K=t+273.15,temperature_C=t,loading_mol_co2_per_mol_mea=a,mea_mass_fraction_co2_free=.30,basis='CO2-free solvent; total absorbed CO2 per analytical MEA',pressure_assumed_Pa=101325,pressure_basis='Ambient modeling assumption; measurement pressure not reported',amundsen_density_g_cm3=observed,amundsen_loading=0 if idx==4 else a,source_locator=f'Amundsen2009 p.3097 Table {1 if idx==4 else 3}; {t} C; '+('30 wt% unloaded' if idx==4 else f'loading {a}'),source_uncertainty_g_cm3=.0005 if idx==4 else .002,model_density_g_cm3=rho,deviation_percent=100*(rho/observed-1),solver_status=result.solver_status,tolerance_met=evidence['requested_tolerance_met'],balance_errors=json.dumps(evidence.get('validation_errors',[])),max_abs_stationarity=stationarity,loading_from_feed=loading,conserved_totals=json.dumps(totals),liquid_pressure_Pa=liquid['pressure_pa'],record_sha256=s.sha256(s.PARAMETERS),wheel_sha256=s.sha256(s.installed_wheel()))
print('DENSITY_ROW '+json.dumps(row),flush=True)
Path(f'/tmp/mea123-row-{idx}.json').write_text(json.dumps(row))
