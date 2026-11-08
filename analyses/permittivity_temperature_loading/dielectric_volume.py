"""Native dielectric-volume perturbations and scenario parameter binding (#265)."""
import copy
import gzip
import hashlib
import json
from pathlib import Path
import zipfile
import epcsaft
from MEA.solvent_specification import SolventSpecification, jsonable


def dump(path, value):
    path.parent.mkdir(parents=True, exist_ok=True)
    data = (json.dumps(jsonable(value), allow_nan=False, indent=2) + '\n').encode()
    path.write_bytes(gzip.compress(data, mtime=0) if path.suffix == '.gz' else data)


def scaled(mapping, scale):
    mapping = copy.deepcopy(mapping)
    for component in mapping['components']:
        for coefficient in component['coefficients']:
            if coefficient['family'] == 'dielectric_volume':
                coefficient['value']['magnitude'] *= scale
    return mapping


class Scenario(SolventSpecification):
    def continue_groups(self):
        pass  # Rebuild continuation once, after all scenario parameter bindings exist.


def specification(path, scale):
    spec = Scenario(path)
    spec.parameters = epcsaft.Parameters.from_mapping(scaled(spec.inputs['endpoint'], scale))
    spec.model = epcsaft.Mixture(spec.parameters, thermochemistry=spec.thermal)
    spec.construction_parameters = {key: epcsaft.Parameters.from_mapping(scaled(
        spec.inputs['endpoint'] if key == spec.parameter_sha256 else spec.load_record(next(
            d['observation_parameters'] for d in spec.spec['datasets'] if d.get('observation_parameters', {}).get('sha256') == key)), scale))
        for key in spec.construction_parameters}
    SolventSpecification.continue_groups(spec)
    return spec


def composition(mapping, weight, amine="monoethanolamine"):
    mass = {c['component_id']: c['fixed']['molar_mass']['value']['magnitude'] for c in mapping['components']}
    amounts = {amine: weight / mass[amine], 'water': (1 - weight) / mass['water']}
    return {k: v / sum(amounts.values()) for k, v in amounts.items()}


def verify_wheel(wheel, digest):
    assert hashlib.sha256(wheel.read_bytes()).hexdigest() == digest
    with zipfile.ZipFile(wheel) as archive:
        for name in archive.namelist():
            if name.startswith('epcsaft/') and not name.endswith('/'):
                assert archive.read(name) == (Path(epcsaft.__file__).parent.parent / name).read_bytes(), name
