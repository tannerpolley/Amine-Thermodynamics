"""Replay the same observations with only the water ideal-gas record changed."""
import csv
import json
import math
import shutil
import sys
import tempfile
import tomllib
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
BUNDLE = ROOT / 'analyses/mea_parameter_bundle'
sys.path[:0] = [str(BUNDLE/'scripts'), str(ROOT/'src')]
import epcsaft
from MEA.solvent_specification import SolventSpecification
import model_curves as c
import kim2007_heat_pathways as kim
import verify_temperature_reference as vt

OUT = Path(__file__).resolve().parent
FIT = json.loads((OUT/'fit.json').read_text())
OLD = json.loads((OUT/'old-water.json').read_text())
NEW = dict(OLD, coefficients=FIT['coefficients'], range_k=[273.15, 400.0], source_range_k=[273.15, 400.0])


def main():
    c.s.verify_wheel()
    assert c.s.sha256(c.s.PARAMETERS) == kim.PARAMETER_HASH == c.s.sha256(c.RECORD)
    spec = SolventSpecification(ROOT/'analyses/solvent_specification_mea/MEA.toml')
    cp_rows = [r for r in spec.inputs['observations']['fitted'] if r['group'] == 'Cp']
    assert len(cp_rows) == 4
    heat_rows = c.fo.load(c.SPEC['heat_rows_path'])
    assert len(heat_rows) == 22
    packet = {o['identity']: o['request'] for o in c.s.load_state_packet()['observations']}
    base = c.s.corrected_request(packet['vle_obs_0130'], c.s._selected_reactions())
    outputs = {}
    runtime = Path(tempfile.mkdtemp(prefix='water-ideal-gas-'))
    kim.c = c
    for name, water in [('old', OLD), ('new', NEW)]:
        c.he.vrc.CALORICS['components']['water'] = water
        thermal = c.he.vrc.record()
        spec.thermal = thermal
        spec.model = epcsaft.Mixture(spec.parameters, thermochemistry=thermal)
        c.MODEL = epcsaft.Mixture(c.PARAMS, thermochemistry=thermal)
        c.solved.__defaults__ = (c.MODEL, None)
        kim.CACHE, kim.PROBLEMS = {}, {}
        c.s.RUNS = runtime / name
        rows = []
        p0 = c.he.vrc.CALORICS['reference_pressure_pa']
        params = epcsaft.Parameters.from_mapping(c.MAPPING, components=['water'])
        form = epcsaft.IdealShomate(water['coefficients'], water['formation_enthalpy_j_per_mol'])
        interval = epcsaft.IdealInterval(*water['range_k'], True, True, epcsaft.IdealCorrelation(form, p0))
        pure = epcsaft.Pure(params, thermochemistry=epcsaft.ThermochemistryRecord(p0, [[interval]]))
        reactions = tomllib.loads((ROOT/'analyses/solvent_specification_mea/declarations.toml').read_text())['chemistry']['reactions']['aqueous']
        for T in (273.15, 298.15, 313.15, 318.15, 353.15, 393.15, 400.0):
            state = pure.state(T, rho=p0/(8.31446261815324*T))
            for prop, unit in [('ideal_enthalpy', 'J/mol'), ('ideal_entropy', 'J/mol/K'), ('ideal_isobaric_heat_capacity', 'J/mol/K')]:
                rows.append(dict(group='water ideal', identity=f'{prop}@{T}', unit=unit, value=getattr(state, prop), status='available'))
            for reaction in reactions:
                rows.append(dict(group='reaction water ideal enthalpy term', identity=f"{reaction['name']}@{T}", unit='J/mol reaction',
                                 value=reaction['stoichiometry']['water']*state.ideal_enthalpy, status='available'))
            if name == 'new' and T == 298.15:
                assert abs(state.ideal_enthalpy+241826) < 1e-6 and abs(state.ideal_entropy-188.834) < 1e-6
        for row in cp_rows:
            result = spec.prediction(row)
            result.update(group='Hilliard Cp', unit='J/mol/K')
            rows.append(result)
        for row, result in zip(heat_rows, c.fo.predict(c.MAPPING, c.fo.heat_items(c.MAPPING, c.PARAMS, heat_rows, c.HEAT_REQUEST)), strict=True):
            rows.append(dict(group='integral heat', identity=row['record_id'], unit='J/mol CO2', value=result.value,
                             status=result.status.name, message=result.message, requested_tolerance_met=result.requested_tolerance_met))
        for row in kim.source_rows():
            if row['loading'] > kim.CEILING:
                value, status = None, 'above_ceiling'
            else:
                value, status = kim.heat(row['T_K'], row['previous_loading'], row['loading'])
            rows.append(dict(group='Kim finite addition', identity=row['record_id'], unit='kJ/mol CO2', value=value,
                             status=status, T_K=row['T_K'], loading=row['loading'], previous_loading=row['previous_loading']))
        problem, state = vt.solve(c.MODEL, vt.request_at(base, 313.15))
        value = c.he.vrc.liquid_heat(c.MODEL, base, 313.15, state.pressure, vt.anchor(problem, state))
        rows.append(dict(group='reference caloric', identity='vle_obs_0130', unit='kJ/mol CO2', value=value['heat_kJ_per_mol'], status='available', details=value))
        outputs[name] = rows
        print(name, len(rows), flush=True)
    results = []
    for old, new in zip(outputs['old'], outputs['new'], strict=True):
        assert (old['group'], old['identity']) == (new['group'], new['identity'])
        a, b = old.get('value'), new.get('value')
        results.append(dict(group=old['group'], identity=old['identity'], unit=old['unit'], old=old, new=new,
                            difference=None if a is None or b is None else b-a))
    (OUT/'comparison.json').write_text(json.dumps(results, indent=2, allow_nan=False)+'\n')
    shutil.rmtree(runtime)
    print('comparison retained', flush=True)


if __name__ == '__main__':
    main()
