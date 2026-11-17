"""Reuse the retained Part I stability declarations for the probe wheel."""
from calculate import *
from concurrent.futures import ProcessPoolExecutor
sys.path.insert(0,str(ROOT/'analyses/mea_parameter_bundle/scripts'))
import shared_evaluation as shared
# Existing phase-search imports verify the historical pin at import time.
# This probe verifies its explicitly authorized local wheel instead.
shared.verify_wheel=verify
import stable_refit_255 as previous


def bind(mapping):
    spec=specification()
    spec.parameters=epcsaft.Parameters.from_mapping(mapping)
    spec.model=epcsaft.Mixture(spec.parameters,thermochemistry=spec.thermal)
    spec.inputs['endpoint']=mapping
    return spec


def configure():
    previous.bind=bind
    previous.verify=verify
    previous.SHA=verify()['wheel_sha256']
    previous.OUT=OUT


def full():
    configure()
    mapping=json.loads((OUT/'fitted-parameters.json').read_text())
    enforced,offset=previous.states()
    started=time.perf_counter()
    rows=previous.grid(mapping,enforced+offset,trials={})
    dump('fitted-stability-grid.json',rows)
    dump('fitted-stability-summary.json',dict(grid=previous.tally(rows[:len(enforced)]),offset=previous.tally(rows[len(enforced):]),grid_seconds=time.perf_counter()-started))
    print('full grid done',time.perf_counter()-started,flush=True)
    previous.census(mapping,'fitted-census')
    print('census done',flush=True)


def main():
    configure()
    mapping=composed(BASE)
    enforced,offset=previous.states()
    selected=[enforced[0],enforced[len(enforced)//2],enforced[-1],offset[len(offset)//2]]
    started=time.perf_counter()
    rows=previous.grid(mapping,selected,trials={})
    dump('stability-timing.json',dict(rows=rows,wall_seconds=time.perf_counter()-started,full_grid_states=len(enforced)+len(offset)))
    print('grid timing',[(r['key'],r.get('available'),r['seconds']) for r in rows],flush=True)
    state=previous.read(ROOT/'analyses/mea_parameter_bundle/results/engine-3e83e19c-phase-search/run-2/inputs/states.json')[0]
    started=time.perf_counter()
    raw,reduced=previous._census((mapping,state,OUT/'census-timing-raw.json'))
    dump('census-timing.json',dict(raw=raw,reduced=reduced,seconds=time.perf_counter()-started))
    print('census timing',time.perf_counter()-started,flush=True)


if __name__=='__main__':
    full() if len(sys.argv)>1 and sys.argv[1]=='full' else main()
