import sys,json,pathlib
out=pathlib.Path.cwd()/'analyses/mea_parameter_bundle/results/permittivity-refit-172';sys.path.insert(0,str(out));import family as f
f.MAPPING=json.loads((out/'smaller-dV/F1-A/parameters.json').read_text());f.MODEL=f.screen.mixture(f.MAPPING);p=f.problem(0);r=f.c.h.eq.solve_equilibrium(f.MODEL,p);assert r.success
try:
 f.stable(f.screen.mixture(f.MAPPING),p,r)
except Exception as error: rejected=str(error)
else: raise AssertionError('Expected model-binding refusal')
report=f.stable(f.MODEL,p,r)
f.c.write(out/'model-binding-probe.json',dict(case='smaller-dV/F1-A family index0',rejected_new_instance=rejected,original_model_report=report,native_cold=f.payload(r),meaning='Same declaration does not replace originating model identity. Original model permits stability evaluation; no extra replay of a successful cold state is required.'))
print('MODEL IDENTITY',rejected,'correct model completed=',report['completed'],flush=True)
