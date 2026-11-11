"""Reduce the qualified #297 observation replay for current notebook consumers; no model evaluation."""
import csv
import hashlib
import json
import math
from pathlib import Path

BUNDLE = Path(__file__).resolve().parents[1]
OUT = BUNDLE/'results/adoption-297/paper-evidence'


def main():
    qualified = json.loads((OUT.parent/'candidate/replay.json').read_text())
    selected = BUNDLE/'results/selected-current-best-parameters.json'
    assert hashlib.sha256(selected.read_bytes()).hexdigest()==qualified['parameter_sha256']
    rows = [dict(id=x['identity'],group=x['group'],quantity=x['row'].get('quantity') or x['row'].get('kind'),
                 observed=x['observed'],predicted=x['value'],residual=x['residual'],weighted_residual=x['weighted_residual'],
                 cost=x['cost'],status=x['status']) for x in qualified['rows']]
    with (OUT/'fitted-rows.csv').open('w',newline='') as stream:
        writer=csv.DictWriter(stream,fieldnames=list(rows[0]),lineterminator='\n')
        writer.writeheader()
        writer.writerows(rows)
    summary=json.loads((OUT/'fit-summary.json').read_text())
    summary['cost']=math.fsum(x['cost'] for x in rows)
    groups={group:[x for x in rows if x['group']==group] for group in dict.fromkeys(x['group'] for x in rows)}
    for family,quantity in [('pressure','PartialPressure'),('species','PhaseMoleFraction'),('heat','AdditionEnthalpy')]:
        groups['common149 '+family]=[x for x in rows if x['group']=='common149' and x['quantity']==quantity]
    summary['groups']={k:dict(n=len(v),cost=math.fsum(x['cost'] for x in v),AARD_percent=100*math.fsum(abs(x['predicted']/x['observed']-1) for x in v)/len(v)) for k,v in groups.items()}
    (OUT/'fit-summary.json').write_text(json.dumps(summary,indent=2)+'\n')


if __name__=='__main__':
    main()
