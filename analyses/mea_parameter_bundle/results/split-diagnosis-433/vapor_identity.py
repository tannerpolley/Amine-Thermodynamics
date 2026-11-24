import math
from verify import amp_inputs,dump,np
from decompose import parent,slope_move
from part_ii import stable,ROOT
a, route, p, fixed=amp_inputs()
T,P,feed=(a[k] for k in ('T_K','P_Pa','feed_mol'))
out=[]
for row, point in zip(stable.read(ROOT/'analyses/mea_parameter_bundle/results/split-diagnosis-433/amp-absolute-pressure-controls.json'),
                     [fixed,slope_move(p,-150.,353.22),slope_move(p,0.,353.22)],strict=True):
    spec=route.bind(point)
    witness=next(t for t in row['trials'] if t['resolved'] and t['q'].get('density_side')==1.)
    x=witness['composition']
    model=spec.model
    root=model.state(T,P=P,x=x,phase='vapor')
    trace=[]
    for rho in np.geomspace(root.molar_density*1.e-4,root.molar_density,33):
        st=model.state(T,rho=rho,x=x)
        trace.append(dict(rho=rho,P=st.pressure,dPdrho=st.pressure_density_derivative))
    out.append(dict(label=row['label'],rho=root.molar_density,returned=root.returned_density_branch.name,
                    x=x,P=root.pressure,trace=trace))
dump('amp-control-vapor-identity.json',out)
