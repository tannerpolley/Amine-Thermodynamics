"""Export the frozen inputs of the two unavailable solves for Engine reproduction (no solve)."""
import copy, json, sys
from pathlib import Path
HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent))
import born_form_diagnosis as d

def ionic_eps(mapping, value):
    out = copy.deepcopy(mapping)
    c = next(c for c in out['model_coefficients'] if c['family'] == 'ionic_region_relative_permittivity')
    c['value']['magnitude'] = float(value)
    return out

cases = {
    'case1-shell-only-1-0': (d.changed(d.MAPPINGS['11'], {'model/electrolyte/c_dielectric': 0.0}), 'vle_obs_0119',
                             'p3-shell-only-fit.json'),
    'case2-eps-ion-2': (ionic_eps(d.MAPPINGS['11'], 2.0), 'vle_obs_0193', 'scan-B-eps_ion-2.0-failure.json'),
}
anchors = {json.loads(Path(path).read_text())['identity']: {'path': path, 'sha256': sha}
           for path, sha in json.loads((HERE.parent / 'accepted-fit-anchor-hashes-11.json').read_text()).items()}
obs = {o['identity']: o for o in d.OBS}
for name, (mapping, identity, failure) in cases.items():
    reactions = d.s.reaction_values(mapping)
    (HERE / f'{name}-parameters.json').write_text(json.dumps(mapping, indent=1, default=str))
    (HERE / f'{name}-request.json').write_text(json.dumps({
        'observation_identity': identity,
        'raw_request': obs[identity]['request'],
        'reaction_corrected_request': d.s.corrected_request(obs[identity]['request'], reactions),
        'anchor_state_record': anchors[identity],
        'parameter_fingerprint': d.s.parameter_fingerprint(mapping),
        'engine_wheel_sha256': d.s.ENGINE_WHEEL_SHA256,
        'retained_failure_record': failure,
        'reconstruction': 'born_form_diagnosis.declared(mapping, "11") -> s._problem_from_request(corrected_request, s.anchor_from(anchor record))',
    }, indent=1, default=str))
    print(name, 'ok', identity)
