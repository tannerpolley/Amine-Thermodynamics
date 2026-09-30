"""At most three five-coordinate warm confirmations; no Born-input fitting."""
import time
STARTED=time.perf_counter()
import json
import sys
from pathlib import Path
import born_form_diagnosis as d


def main(label):
    if label=='shell-only':
        mapping=d.changed(d.MAPPINGS['11'],{d.QIDS[8]:0.})
        group='configuration (1,0)'
    else:
        steps=json.loads((d.HERE/'p2-selected-steps.json').read_text())
        step=next((r for r in steps if r['label']==label),None)
        if step is None or not step['available']:
            d.save('p3-'+label+'-unavailable.json',{'classification':'unavailable','reason':'no complete admissible predicted-step evaluation'})
            return
        mapping=d.changed(d.MAPPINGS['11'],step['changes']);group=step['group']
        if label=='joint-group':
            best=next((r for r in steps if r['label']=='best-group' and r['available']),None)
            if best and d.s.parameter_fingerprint(mapping)==d.s.parameter_fingerprint(d.changed(d.MAPPINGS['11'],best['changes'])):
                d.save('p3-joint-group-duplicate.json',{'reason':'same actual inputs as best-group; no duplicate refit'})
                return
    d.enough(30.)
    out,final=d.fitted('p3-'+label,mapping,'11',iterations=10,elapsed=240.)
    base=json.loads((d.HERE/'baseline-11.json').read_text())
    reduction=base['cost']-out['cost']
    classification='at least half accounted for' if reduction>=3.71 else 'inconclusive' if reduction>=1.86 else 'not supported locally'
    d.save('p3-'+label+'-confirmation.json',{'group':group,'achieved_cost':out['cost'],'achieved_reduction':reduction,
        'classification':classification,'converged':out['status']=='converged',
        'iterations':out['iterations'],'status':out['status'],
        'interpretation':'achieved numerical reduction at fixed Born inputs; an optimum only if convergence is shown',
        'inputs':d.values(final)})
    final['purpose']='Local numerical Born-form diagnosis, MEA #121; not adopted.'
    d.save('p3-'+label+'-diagnostic-parameters.json',final)
    print('CONFIRMATION',label,out['cost'],reduction,classification,out['status'],flush=True)


if __name__=='__main__':
    label=sys.argv[1];status='complete'
    try:main(label)
    except BaseException as error:
        status='failed';d.save('p3-'+label+'-job-failure.json',{'exception':type(error).__name__,'message':str(error)});raise
    finally:
        d.save('job-times.json',d.OLD_JOBS+[{'job':'p3-'+label,'wall_s':time.perf_counter()-STARTED,'status':status,
            'script_sha256':d.s.sha256(Path(__file__))}])
