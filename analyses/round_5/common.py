"""Retain Round 5 calculation records and source identities."""
import gzip
import hashlib
import json
import sys
from pathlib import Path
from time import monotonic

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
RESULTS = HERE / 'results'
sys.path[:0] = [str(ROOT / 'analyses/round_3'), str(ROOT / 'analyses'), str(ROOT / 'analyses/amp_transfer')]


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def fingerprints(*paths):
    return {path.relative_to(ROOT).as_posix(): digest(path) for path in paths}


def save(name, value, *, start=None):
    from part_ii import jsonable

    path = RESULTS / name
    if start is not None:
        from run import receipt

        value = dict(value, seconds=monotonic() - start, **receipt())
    contents = (json.dumps(jsonable(value), indent=2, sort_keys=True, allow_nan=False) + '\n').encode()
    if path.suffix == '.gz':
        contents = gzip.compress(contents, mtime=0)
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_suffix('.tmp')
    temporary.write_bytes(contents)
    temporary.replace(path)
