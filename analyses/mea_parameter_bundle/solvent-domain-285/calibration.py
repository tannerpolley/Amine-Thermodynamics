import json, sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[3]
sys.path.insert(0,str(ROOT/'src'))
from MEA.solvent_specification import SolventSpecification
SolventSpecification.continue_groups=lambda self: None
s=SolventSpecification(ROOT/'analyses/solvent_specification_mea/MEA.toml')
rows=[]
for r in s.inputs['observations']['fitted']:
 p=s.problems[r.get('problem',r.get('initial'))]; d=p.feed.values
 def a(k): return d.get(k,0.)
 mea=sum(a(k) for k in ('monoethanolamine','protonated-monoethanolamine','carbamate-anion'))
 co=sum(a(k) for k in ('carbon-dioxide','carbamate-anion','bicarbonate-anion','carbonate-anion'))
 water=sum(a(k) for k in ('water','bicarbonate-anion','carbonate-anion','hydronium-cation','hydroxide-anion'))
 rows.append(dict(identity=r['identity'],group=r['group'],w=mea*.061080535833333255/(mea*.061080535833333255+water*.01801522125),alpha=co/mea if mea else None))
assert len(rows)==307 and sum(r['alpha'] is None for r in rows)==39
valid=[r for r in rows if r['alpha'] is not None]
print(json.dumps(dict(count=len(rows),alpha_count=len(valid),max_w=max(rows,key=lambda r:r['w']),min_alpha=min(valid,key=lambda r:r['alpha']),max_alpha=max(valid,key=lambda r:r['alpha'])),indent=2))
