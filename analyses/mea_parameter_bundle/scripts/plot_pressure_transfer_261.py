"""Show each separately fitted pressure-transfer probe and the issue's limits."""
import hashlib
import json
from pathlib import Path
import matplotlib.pyplot as plt

OUT = Path(__file__).resolve().parents[1] / 'results/pressure-transfer-261'
rows = [r for r in json.loads((OUT / 'probe-summary.json').read_text()) if r['scores']['held-15wt']['n'] or r['scores']['held-45wt']['n']]
assert rows
fig, axes = plt.subplots(1, 2, figsize=(12, max(4, .45*len(rows))))
for axis, keys, limit in zip(axes, [('held-15wt','held-45wt'),('original47',)], [24.2,13.86], strict=True):
    for key in keys:
        points = [(i, row['scores'][key]['AARD_percent']) for i,row in enumerate(rows) if row['scores'][key]['n']]
        axis.scatter([v for i,v in points], [i for i,v in points], label=key)
    axis.axvline(limit, color='black', linestyle=':', label=f'Issue limit {limit:g}%')
    axis.set(yticks=range(len(rows)), yticklabels=[r['name'] for r in rows], xlabel='Average absolute relative pressure deviation / %')
    axis.invert_yaxis(); axis.legend(fontsize=8); axis.grid(axis='x', alpha=.2)
axes[0].set_title('Held-out concentration rows')
axes[1].set_title('Original 47 calibration pressures')
fig.suptitle('Local probes: each row is a separately fitted model')
fig.tight_layout(); fig.savefig(OUT/'pressure-transfer.png', dpi=160,metadata={'Engine wheel SHA-256':rows[0]['engine_wheel_sha256']}); plt.close(fig)
(OUT/'figure-inputs.json').write_text(json.dumps(dict(source_sha256=hashlib.sha256((OUT/'probe-summary.json').read_bytes()).hexdigest(), values=rows, limits_from_issue_261=[24.2,13.86], interpretation='Discrete local fits; no parameter confidence intervals or global optimum claim'),indent=2)+'\n')
