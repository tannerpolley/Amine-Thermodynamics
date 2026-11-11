"""Historical density comparison and current adopted-record water display; no fits or rescoring."""
import json
from pathlib import Path
import sys

ROOT = Path.cwd()
BUNDLE = ROOT / 'analyses/mea_parameter_bundle'
sys.path[:0] = [str(BUNDLE / 'scripts'), str(ROOT / 'src')]
import fit_campaign as c, fit_observations as fo, heat_evidence_170 as he

BASE = BUNDLE / 'results/engine-3e83e19c-refit-chain'
OUT = BUNDLE / 'results/adoption-297/paper-evidence'
HISTORICAL_RECORD = BASE / 'restricted-2/attempt-3/run/fit/usable-budget-endpoint.json'


def main(mode):
    if mode == 'comparison-density':
        spec_path = BASE / 'a6/spec.json'
        spec = json.loads(spec_path.read_text())
        runtime = dict(engine=spec['engine'], evidence_class='historical comparison; not rerun')
        inputs = [spec_path, HISTORICAL_RECORD]
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
        fo.s.verify_wheel()
        runtime = dict(wheel_sha256=fo.s.ENGINE_WHEEL_SHA256, engine_commit=fo.s.ENGINE_COMMIT)
        water_path = BUNDLE / 'results/water-124/spec.json'
        inputs = [fo.s.PARAMETERS, water_path]
        result = fo.water_assessment(json.loads(water_path.read_text()), fo.s.parameter_mapping())
        rows = result['rows']
        fo.s.write_json(OUT / 'water-checks.json', result)
        fo.s.write_json(OUT / 'water-summary.json', dict(parameter_sha256=fo.s.sha256(fo.s.PARAMETERS), engine_commit=fo.s.ENGINE_COMMIT, wheel_sha256=fo.s.ENGINE_WHEEL_SHA256, metrics=result['metrics'], states=len(rows)))
        assert len(rows) == 42 and all(r['evaluated'] and r['cp_verified'] for r in rows)
        he.table(OUT / 'water.csv', [{k:v for k,v in r.items() if k != 'enthalpy_ladder'} for r in rows])
    c.write(OUT / (mode+'-inputs.json'), dict(runtime=runtime, files={str(p.relative_to(ROOT)):fo.s.sha256(p) for p in inputs}))


if __name__ == '__main__':
    main(sys.argv[1])
