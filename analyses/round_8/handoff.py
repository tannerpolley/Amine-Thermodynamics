"""Recompute the numerical handoff and notebook from retained contributors."""
from hashlib import sha256
import json
import sys
from time import monotonic
from records import BASE, DISPLAY, HERE, ROOT, OUT, LIMITS, NAMES, Sources, replay_path, write
from reductions import reference, phases, dea, amp, salts, endpoints, literature

def main(check):
    doc, table = {}, []
    timing = OUT/'runtime.json'
    times = json.loads(timing.read_text()) if check else {}
    for i, reduce in enumerate((reference,phases,dea,amp,salts,endpoints,literature),1):
        start = monotonic()
        src, file = Sources(), replay_path(i)
        replay = src.read(str(file.relative_to(ROOT)),None) if file.exists() else {}
        for path, x in replay.get('sources',{}).items():
            src.read(path,x['revision'])
            assert src.hashes[path]==x, f'stale replay input {path}'
        status, reason, quantities = reduce(src,replay)
        record = dict(disposition=status,reason=reason,quantities=quantities,execution=replay,
                      contributors=dict(src.hashes))
        path = OUT/f'{NAMES[i-1]}.json.gz'
        if check:
            retained = src.read(str(path.relative_to(ROOT)),None)
            assert i!=2 or retained['quantities']['fingerprint']==quantities['fingerprint'], 'MDEA model fingerprint mismatch'
            assert retained==record, f'C{i} stale retained reduction'
        else:
            write(path,record)
            times[f'C{i}'] = dict(replay_s=replay.get('seconds',0),reduction_s=monotonic()-start,projection_s=LIMITS[i-1])
        doc[f'C{i}'] = dict(disposition=status,reason=reason,runtime=times[f'C{i}'],
                            quantities={k:dict(record=str(path.relative_to(HERE)),field=f'quantities.{k}')
                                        for k in quantities}, record_sha256=sha256(path.read_bytes()).hexdigest())
        table.append(f"| C{i} | {status} | {reason} | [Retained quantities](results/{path.name}) |")
    if not check:
        write(timing,times)
    handoff = dict(base=BASE,display_snapshot=DISPLAY,items=doc)
    path, qmd = HERE/'manuscript-handoff.json', HERE/'notebook.qmd'
    prefix, _, current = qmd.read_text().partition('## Retained results\n\n')
    notebook = '| Item | Disposition | Evidence | Record |\n| --- | --- | --- | --- |\n'+'\n'.join(table)+'\n'
    if check:
        assert json.loads(path.read_text())==handoff, 'stale handoff quantity or disposition'
        assert current==notebook, 'stale notebook display'
        print('Round 8 handoff checks passed (C1–C7)')
    else:
        write(path,handoff)
        qmd.write_text(prefix+'## Retained results\n\n'+notebook)
if __name__=='__main__':
    main(sys.argv[1:]==['--check'])
