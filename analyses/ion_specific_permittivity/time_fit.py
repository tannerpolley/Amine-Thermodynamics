"""Timed exact derivative workload for the issue 394 one-hour decision."""
from calculate import *
import cProfile
import pstats


def coordinates(spec):
    declared = json.loads((ROOT/'analyses/mea_parameter_bundle/results/reduced-refit/F2/previous/unpenalized/declaration.json').read_text())['declared']
    values = {c['identity']:c['value']['magnitude'] for x in BASE['components']+BASE['pairs'] for c in x['coefficients']}
    for q in declared:
        q['origin']=values[q['identity']]
    declared += [dict(identity='probe/'+ion+'/suppression',targets=[['ion_suppression_coefficient',ion,1.]],origin=0.,scale=1.,bounds=[-10.,10.]) for ion in IONS]
    spec.inputs['coordinates']=declared
    return declared


def main():
    verify()
    spec=specification()
    declared=coordinates(spec)
    dump('fit-coordinates.json',declared)
    coords=spec.coordinates()
    records=spec.inputs['observations']['fitted']
    times=[]
    # Exact derivatives at all 307 rows, grouped to locate the costly observable.
    for group in dict.fromkeys(r['group'] for r in records):
        rows=[r for r in records if r['group']==group]
        observations=[spec.observation(r) for r in rows]
        started=time.perf_counter()
        ev=reg.differentiate(spec.parameters,coords,observations,optimizer=[0.]*len(coords),holds=[],thermochemistry=spec.thermal)
        elapsed=time.perf_counter()-started
        result=dict(group=group,rows=len(rows),coordinates=len(coords),seconds=elapsed,statuses=[s.name for s in ev.statuses])
        times.append(result)
        dump('derivative-timing.json',times)
        print(json.dumps(result),flush=True)
    profiler=cProfile.Profile()
    profiler.enable()
    reg.differentiate(spec.parameters,coords,[spec.observation(r) for r in records[:10]],optimizer=[0.]*len(coords),holds=[],thermochemistry=spec.thermal)
    profiler.disable()
    with (OUT/'profile.txt').open('w') as stream:
        pstats.Stats(profiler,stream=stream).sort_stats('cumulative').print_stats(20)
    (OUT/'profile.txt').write_text((OUT/'profile.txt').read_text().rstrip()+'\n')


if __name__=='__main__':
    main()
