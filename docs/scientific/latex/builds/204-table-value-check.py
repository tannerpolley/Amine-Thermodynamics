"""Issue 204: compare displayed numeric tokens and citation keys of every generated table, base commit against working tree."""
import collections
import json
import re
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[4]
TABLES = 'docs/scientific/latex/tables'
BASE = sys.argv[1] if len(sys.argv) > 1 else 'main'


def tokens(text):
    lines = [line for line in text.splitlines() if not line.startswith('%')]
    # The repeated page header, the column specification and the group font settings are not displayed values.
    lines = [line for line in lines if not line.startswith((r'\begingroup', r'\begin{longtable}', r'\begin{landscape}', r'\end{landscape}'))]
    text = re.sub(r'\\midrule\\endfirsthead.*?\\midrule\\endhead', '', '\n'.join(lines), flags=re.S)
    cites = [key.strip() for keys in re.findall(r'\\cite(?:\[[^]]*\])?\{([^}]*)\}', text) for key in keys.split(',')]
    text = re.sub(r'\\cite(?:\[([^]]*)\])?\{[^}]*\}', r' \1 ', text)
    text = re.sub(r'\\label\{[^}]*\}|\\ce\{(?:[^{}]|\{[^{}]*\})*\}', ' ', text)  # chemical formulas carry no values
    text = text.replace(r'\textminus{}', '-').replace(r'\allowbreak{}', '').replace('--', ' -- ')
    text = re.sub(r'\\times10\^\{([-+]?\d+)\}', r'e\1', text)
    numbers = re.findall(r'(?<![A-Za-z_\\\d.-])-?\d+(?:\.\d+)?(?:e[-+]?\d+)?', text)
    return collections.Counter(numbers), collections.Counter(cites)


def captions(text):
    return re.findall(r'\\caption\{(.*)\}\\label', text)


report = {'base': subprocess.check_output(['git', 'rev-parse', BASE], cwd=ROOT, text=True).strip(), 'tables': {}}
for path in sorted((ROOT / TABLES).glob('*.tex')):
    old = subprocess.check_output(['git', 'show', f'{BASE}:{TABLES}/{path.name}'], cwd=ROOT, text=True)
    new = path.read_text()
    (old_numbers, old_cites), (new_numbers, new_cites) = tokens(old), tokens(new)
    report['tables'][path.name] = dict(
        numeric_tokens=sum(new_numbers.values()), citation_keys=sum(new_cites.values()),
        identical=old_numbers == new_numbers and old_cites == new_cites,
        numbers_only_in_base=dict(old_numbers - new_numbers), numbers_only_in_new=dict(new_numbers - old_numbers),
        cites_only_in_base=dict(old_cites - new_cites), cites_only_in_new=dict(new_cites - old_cites),
        caption_changes=[dict(base=a, new=b) for a, b in zip(captions(old), captions(new), strict=True) if a != b])
report['all_identical'] = all(t['identical'] for t in report['tables'].values())
print(json.dumps(report, indent=2, ensure_ascii=False))
