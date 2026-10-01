"""One registered Stage 3 campaign; host CPU gate before each bounded job."""
import json
import os
from pathlib import Path
import re
import subprocess

BASE = Path(__file__).resolve().parent
ROOT = BASE.parents[3]
os.chdir(ROOT)
env = dict(os.environ, OMP_NUM_THREADS='1', OPENBLAS_NUM_THREADS='1', MKL_NUM_THREADS='1',
    UV_PROJECT_ENVIRONMENT=str(BASE.parents[1]/'results/runs/temperature-reanchor-140/stage-3-wheel-replay/.venv'))
def run(args, seconds):
    assert not re.match(r'(?:\S*/)?python[0-9.]*\s', 'bash -c .venv/bin/python stage1_fit.py')
    assert re.match(r'(?:\S*/)?python[0-9.]*\s', '.venv/bin/python stage1_fit.py')
    while True:
        report=subprocess.check_output(['ps','-eo','pid,ppid,args'],text=True)
        workers={int(pid):(int(parent),command) for line in report.splitlines()[1:] for pid,parent,command in [line.strip().split(None,2)]
            if re.match(r'(?:\S*/)?python[0-9.]*\s',command) and any(s in command for s in ('fit','assessment','evaluate_direct_absorption_heat','r2-temperature.py'))}
        occupied=[pid for pid in workers if not any(parent==pid for parent,_ in workers.values())]
        print('CPU gate',args,'workers',[(p,workers[p][1]) for p in occupied],flush=True)
        if len(occupied)<2: break
        subprocess.run(['bash','-c',f'while kill -0 {occupied[0]} 2>/dev/null; do sleep 60; done'],check=True)
    subprocess.run(['timeout',str(seconds),'uv','run','--no-sync','python',str(BASE/'r2-temperature.py'),*args],env=env,check=True)

run(['source'],60)
for structure in ('constant-fixed','slope-fixed','slope-free'):
    for start in ('1','2'):
        run(['fit',structure,start],2400)
        result=json.loads((BASE/f'stage-3/{structure}-start-{start}-fit.json').read_text())
        if result['native_complete']: run(['rescore',structure,start],1800)
run(['select'],60)
subprocess.run(['git','add',str(BASE/'stage-3')],check=True)
subprocess.run(['git','commit','-m','Freeze issue 140 Stage 3 records before high-temperature assessment'],check=True)
if json.loads((BASE/'stage-3/freeze.json').read_text())['records']:
    for stage in range(1,6): run(['stage',str(stage)],1800)
    run(['heat'],1800)
print('Registered Stage 3 calculations finished; retained evidence requires notebook and delivered review.',flush=True)
