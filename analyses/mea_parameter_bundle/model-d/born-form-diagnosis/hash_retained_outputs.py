"""Hash compact and bulk retained outputs in their current locations."""
import hashlib
import json
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[3]
OUTPUT = HERE / 'retained-output-hashes.json'

def main():
    paths = sorted(p for p in HERE.rglob('*') if p.is_file() and p != OUTPUT)
    paths += [ROOT / '.gitignore', HERE.parents[1] / 'notebook.qmd',
              ROOT / 'analyses/_site/mea_parameter_bundle/notebook-preview.html']
    records = {str(p.relative_to(ROOT)): hashlib.sha256(p.read_bytes()).hexdigest() for p in paths}
    assert any('/runs/' in p for p in records)
    assert any('/figures/' in p for p in records)
    OUTPUT.write_text(json.dumps({'basis': 'Paths relative to the worktree root; current compact and runs locations.',
        'excluded': ['retained-output-hashes.json itself'], 'sha256': records}, indent=2) + '\n')
    print(json.dumps({'files': len(records), 'hash_list_sha256': hashlib.sha256(OUTPUT.read_bytes()).hexdigest()}))

if __name__ == '__main__':
    main()
