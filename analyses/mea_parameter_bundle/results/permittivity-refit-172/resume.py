"""Resume only the five original attempts interrupted by the tool host."""
import datetime
import hashlib
import json
import os
import subprocess
import sys
import time
from pathlib import Path

OUT = Path(__file__).resolve().parent
runs = json.loads((OUT/'execution.json').read_text())
assert len(runs) == 19
for case in ('F4-B','F5-A','F5-B','F6-A','F6-B'):
    directory = OUT/'larger-dV'/case
    directory.mkdir(exist_ok=True)
    assert not (directory/'native-fit.json').exists()
    retained = {p.name:hashlib.sha256(p.read_bytes()).hexdigest() for p in directory.glob('*.json')}
    if (directory/'execution.log').exists():
        (directory/'execution.log').rename(directory/'execution-interrupted-host.log')
        (directory/'host-interruption.json').write_text(json.dumps(dict(
            cause='Tool-host cancellation; no native result returned; original timing unavailable',
            original_input_hashes=retained),indent=2)+'\n')
    command = ['nice','-n','10',sys.executable,str(OUT/'run.py'),'fit','larger-dV',*case.split('-')]
    start = datetime.datetime.now(datetime.timezone.utc).isoformat()
    clock = time.monotonic()
    with (directory/'execution.log').open('w') as log:
        job = subprocess.Popen(command,stdout=subprocess.PIPE,stderr=subprocess.STDOUT,text=True)
        for line in job.stdout:
            log.write(line); log.flush(); print(line,end='',flush=True)
        code = job.wait()
    assert all(hashlib.sha256((directory/name).read_bytes()).hexdigest()==value for name,value in retained.items())
    runs.append(dict(branch='larger-dV',problem=case.split('-')[0],start=case[-1],command=command,
        started_UTC=start,ended_UTC=datetime.datetime.now(datetime.timezone.utc).isoformat(),
        returncode=code,wall_s=time.monotonic()-clock,workers=32,maximum_iterations=40,
        maximum_elapsed_time_seconds=2250,numeric_threads=1,requested_nice_increment=10,
        inherited_priority=os.getpriority(os.PRIO_PROCESS,0),priority=min(19,os.getpriority(os.PRIO_PROCESS,0)+10)))
    (OUT/'execution.json').write_text(json.dumps(runs,indent=2)+'\n')
    print('ACCOUNTED',case,code,runs[-1]['wall_s'],flush=True)
