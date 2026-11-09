import csv,json,sys
from pathlib import Path
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
p=Path(__file__).parent
lines=Path(sys.argv[1]).read_text().splitlines()
rows=[]
for line in lines:
 if not line.startswith('RESULT '): continue
 r=json.loads(line[7:]); q=r.pop('L'); y=r.pop('y'); amounts=r.pop('amounts'); n=amounts[0]; v=amounts[1]
 mea=q[1]+q[3]+q[4]; co=q[0]+q[4]+q[5]+q[6]; water=q[2]+q[5]+q[6]+q[7]+q[8]
 r['w_MEA']=mea*.061080535833333255/(mea*.061080535833333255+water*.01801522125);r['alpha']=co/mea
 r['balance_error_mol']=max(abs(n*mea+v*y[1]-1),abs(n*co+v*y[0]-.358),abs(n*water+v*y[2]-7.929776437398854))
 for i,val in enumerate(q): r[f'x{i}']=val
 for i,val in enumerate(y): r[f'y{i}']=val
 r['liquid_mol']=n
 rows.append(r)
assert rows and max(r['balance_error_mol'] for r in rows)<1e-8
with (p/'points.csv').open('w') as f:
 w=csv.DictWriter(f,fieldnames=rows[0],lineterminator='\n');w.writeheader();w.writerows(rows)
print('maximum balance error',max(r['balance_error_mol'] for r in rows))
fig,axes=plt.subplots(1,2,figsize=(10,4),sharey=True)
for ax,T in zip(axes,(353.15,358.15)):
 for name in ('final','candidate'):
  for rule in ('solvent-only','solvent-density-temperature'):
   data=[r for r in rows if r['set']==name and r['rule']==rule and r['T']==T]
   if not data: continue
   ax.plot([r['V'] for r in data],[r['P'] for r in data],marker='.',linestyle='none',label=f'{name}, {rule}')
   m=min(data,key=lambda q:q['P']);i=next((i for i,r in enumerate(data) if r['w_MEA']>.45),None)
   print(name,rule,T,'minimum sampled',m['P'],m['V'],'w alpha',m['w_MEA'],m['alpha'],'crossing',[(r['V'],r['w_MEA'],r['alpha']) for r in data[max(0,i-1):i+1]] if i else None)
 ax.set_title(f'{T} K');ax.set_xlabel('Vapor amount (mol)');ax.grid(alpha=.2)
axes[0].set_ylabel('Pressure (Pa)'); axes[1].legend(fontsize=7);fig.tight_layout();fig.savefig(p/'pressure.png',dpi=140)
