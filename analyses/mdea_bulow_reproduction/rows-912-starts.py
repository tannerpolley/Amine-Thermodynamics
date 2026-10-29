import sys,json,csv
from pathlib import Path
sys.path.insert(0,'analyses/mdea_bulow_reproduction')
import run, prepare as p, epcsaft
from epcsaft import equilibrium as eq
out=run.OUT
assert epcsaft.provenance()[1]==p.EXPECTED_WHEEL
checks=json.loads((out/'repeat-checks.json').read_text())
assert all(c['status']=='pass' for c in checks['checks'].values())
assert p.sha(out/'run-document.json')==checks['run_document_sha256']
assert p.sha(out/'declaration.json')==checks['declaration_sha256']
inv=json.loads((out/'inventory.json').read_text())
guesses={11:1799100,18:2012400,50:1443100,51:1830400}
original=run.problem
def problem(row):
    result=original(row)
    result.P=eq.Free(guesses[int(row['source_row'])])
    return result
run.problem=problem
doc=json.loads((out/'run-document.json').read_text())
rows=[r for r in csv.DictReader((p.ROOT/inv['table_path']).open()) if int(r['source_row']) in guesses]
results=[]
for row in rows:
    result=run.solve_row((doc,row)); result['initial_pressure_guess_Pa']=guesses[result['source_row']]; results.append(result)
    print(json.dumps(result),flush=True)
(out/'rows-912-starts.json').write_text(json.dumps(results,indent=2)+'\n')
