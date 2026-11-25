from verify import amp_inputs, dump, eq, np
from decompose import parent, slope_move, describe
a,r,p,fixed=amp_inputs()
from part_ii import stable, ROOT
from pathlib import Path
T,P,feed=(a[k] for k in ('T_K','P_Pa','feed_mol'))
out=[]
for label,point in [('fixed',fixed),('slope-only',slope_move(p,-150.,353.22)),('k-frozen',slope_move(p,0.,353.22))]:
    spec=r.bind(point)
    problem,res,_=parent(spec,T,P,feed,a['phases'][0])
    opt=eq.StabilityOptions()
    opt.mode=type(opt.mode).Full
    report=eq.stability_test(eq.compile_problem(spec.model,problem),res,opt)
    out.append(dict(label=label, parent=describe(res),note=report.message,
                    trials=[dict(msg=t.message,evidence=str(t.evidence),resolved=t.resolved_descent,composition=t.composition,q=t.quantities) for t in report.trials]))
dump('amp-absolute-pressure-controls.json',out)
