"""Declared nonzero h/s anchors survive mapping to Engine at and away from the pivot."""
import hashlib
import json
import shutil
from pathlib import Path
import epcsaft as e
import pytest
from MEA.solvent_specification import SolventSpecification

def test_caloric_anchors(tmp_path):
    folder = tmp_path / 'mea'
    shutil.copytree(Path(__file__).resolve().parents[1]/'analyses/solvent_specification_mea', folder, ignore=shutil.ignore_patterns('results','*.py','notebook*'))
    path = folder/'inputs/caloric.json'
    old = hashlib.sha256(path.read_bytes()).hexdigest()
    data = json.loads(path.read_text()); source = data['components']['monoethanolamine']
    source.update(enthalpy_anchor_j_per_mol=1234.5, entropy_anchor_j_per_mol_k=6.75)
    path.write_text(json.dumps(data)); config = folder/'MEA.toml'
    config.write_text(config.read_text().replace(old,hashlib.sha256(path.read_bytes()).hexdigest()))
    spec = SolventSpecification(config); i = spec.parameters.component_ids.index('monoethanolamine')
    intervals = list(spec.thermal.component_intervals)
    intervals[i] = [e.IdealInterval(*source['range_k'],True,True,e.IdealCorrelation(e.IdealPolynomial(source['coefficients'],313.15,1234.5,6.75),data['reference_pressure_pa']))]
    parameters = e.Parameters.from_mapping(spec.inputs['endpoint'],components=['monoethanolamine'])
    mapped,direct = [e.Pure(parameters,thermochemistry=e.ThermochemistryRecord(data['reference_pressure_pa'],[q])) for q in (spec.thermal.component_intervals[i],intervals[i])]
    values = []
    for T in (313.15,333.15):
        args = dict(x=[1.],observables=[e.PropertyObservable.IdealEnthalpy,e.PropertyObservable.IdealEntropy],directions=[e.DensityActionDirection(0.,0.,[0.])])
        a,b = [m.density_actions(T,1.0,**args) for m in (mapped,direct)]
        assert [r.value for r in a.results] == pytest.approx([r.value for r in b.results],rel=1e-13)
        values.append(dict(T_K=T,enthalpy_J_mol=a.results[0].value,entropy_J_mol_K=a.results[1].value))
    (Path(__file__).resolve().parents[1]/'analyses/solvent_specification_mea/results/caloric-anchor.json').write_text(json.dumps(values,indent=2)+'\n')
