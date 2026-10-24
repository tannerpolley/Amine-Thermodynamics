"""Comparison density export and fixed-water display for issue #215; no fits or rescoring."""
import json
from pathlib import Path
import sys

ROOT = Path.cwd()
BUNDLE = ROOT / 'analyses/mea_parameter_bundle'
sys.path[:0] = [str(BUNDLE / 'scripts'), str(ROOT / 'src')]
import fit_campaign as c, fit_observations as fo, heat_evidence_170 as he

BASE = BUNDLE / 'results/engine-3e83e19c-refit-chain'
OUT = BUNDLE / 'results/engine-3e83e19c-paper-evidence'
CANDIDATE = BASE / 'restricted-2/attempt-3/run/fit/usable-budget-endpoint.json'


def main(mode):
    spec_path = BASE / ('a6/spec.json' if mode == 'comparison-density' else 'restricted-2/attempt-3/spec.json')
    spec = json.loads(spec_path.read_text())
    runtime = c.verify(spec)
    assert runtime['wheel_sha256'] == '0d08dff9be39fb8fc9018119c47612f53d823cd0e456914d7dd44c6941596804'
    inputs = [spec_path, CANDIDATE]
    if mode == 'comparison-density':
        replay_path = BASE / 'displays/comparison/full-replay.json'
        replay = {r['target']: r for r in json.loads(replay_path.read_text())}
        metadata = {r['id']: r for r in spec['direct_rows'] if r['id'] in spec['loaded_density_ids']}
        assert len(metadata) == 47 and len(replay) == 307
        rows = [dict(id=k, source=r['source_locator'], T_K=r['T_K'], P_Pa=r['P_Pa'], loading=r['analytical_feed']['carbon-dioxide']/r['analytical_feed']['monoethanolamine'],
            observed_kg_m3=replay[k]['observed'], s_kg_m3=replay[k]['scale'], predicted_kg_m3=replay[k]['predicted'], error_kg_m3=replay[k]['predicted']-replay[k]['observed'], error_over_s=replay[k]['residual']) for k,r in metadata.items()]
        he.table(OUT / 'comparison-loaded-density-errors.csv', rows)
        inputs.extend([replay_path, BASE / 'a6/run/fit/usable-budget-endpoint.json'])
    else:
        assert mode == 'water'
        water_path = BUNDLE / 'results/water-124/spec.json'
        result = fo.water_assessment(json.loads(water_path.read_text()), fo.s.parameter_mapping(CANDIDATE))
        rows = result['rows']
        c.write(OUT / 'water-checks.json', result)
        c.write(OUT / 'water-summary.json', dict(parameter_sha256=fo.s.sha256(CANDIDATE), engine=spec['engine'], metrics=result['metrics'], states=len(rows)))
        assert len(rows) == 42 and all(r['evaluated'] and r['cp_verified'] for r in rows)
        he.table(OUT / 'water.csv', [{k:v for k,v in r.items() if k != 'enthalpy_ladder'} for r in rows])
        inputs.append(water_path)
    c.write(OUT / (mode+'-inputs.json'), dict(runtime=runtime, files={str(p.relative_to(ROOT)):fo.s.sha256(p) for p in inputs}))


if __name__ == '__main__':
    main(sys.argv[1])
