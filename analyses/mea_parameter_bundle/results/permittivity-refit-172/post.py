import datetime,json,pathlib,subprocess,time
root=pathlib.Path.cwd();out=root/'analyses/mea_parameter_bundle/results/permittivity-refit-172'
assert len(json.loads((out/'execution.json').read_text()))==24
command=['nice','-n','10','uv','run','--no-project','--python',str(root/'tmp/permittivity-refit-172-venv/bin/python'),str(out/'assess.py')]
start=datetime.datetime.now(datetime.timezone.utc).isoformat();clock=time.monotonic()
with (out/'post-execution.log').open('w') as log:
 job=subprocess.Popen(command,stdout=subprocess.PIPE,stderr=subprocess.STDOUT,text=True)
 for line in job.stdout:
  log.write(line);log.flush();print(line,end='',flush=True)
 code=job.wait()
(out/'post-execution.json').write_text(json.dumps(dict(command=command,started_UTC=start,ended_UTC=datetime.datetime.now(datetime.timezone.utc).isoformat(),wall_s=time.monotonic()-clock,returncode=code,workers=32,numeric_threads=1,priority=10),indent=2)+'\n')
raise SystemExit(code)
