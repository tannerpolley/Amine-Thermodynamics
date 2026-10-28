"""Shared-only water and CO2 predictions must remain unchanged."""
import importlib.util
import json
from pathlib import Path
spec=importlib.util.spec_from_file_location('preparation',Path(__file__).with_name('prepare.py'))
p=importlib.util.module_from_spec(spec);spec.loader.exec_module(p)
checks=[]
for cid,rho in [(p.W,55000.),(p.C,100.)]:
 reference=p.epcsaft.Pure(p.epcsaft.Parameters.from_mapping(p.BASE,components=[cid])).state(313.15,rho=rho)
 for v in 'AB':
  d=json.loads((p.OUT/f'inputs/variant-{v}.json').read_text())
  state=p.epcsaft.Pure(p.epcsaft.Parameters.from_mapping(d,components=[cid])).state(313.15,rho=rho)
  errors={k:abs(getattr(state,k)-getattr(reference,k)) for k in ('pressure','residual_helmholtz','residual_enthalpy')}
  assert all(e==0. for e in errors.values())
  checks.append(dict(component=cid,variant=v,T_K=313.15,rho_mol_m3=rho,reference_pressure_Pa=reference.pressure,absolute_differences=errors))
p.write('results/shared-reference-checks.json',checks)
for v in 'AB':
 d=json.loads((p.OUT/f'results/admission-{v}.json').read_text())
 for state in d['states']:
  terms=state['terms'];assert abs(sum(terms[k] for k in ('hard_chain','dispersion','association','debye_huckel','born'))-terms['residual_helmholtz'])<1e-10
print('Water/CO2 predictions unchanged in both variants; per-term Helmholtz sums close within 1e-10.')
