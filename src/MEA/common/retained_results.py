"""Read retained JSON and identify the parameter mappings it records."""
import gzip
import hashlib
import json
from pathlib import Path


def read(path):
    path = Path(path)
    if path.suffix == '.json' and not path.is_file() and path.with_suffix('.json.gz').is_file():
        path = path.with_suffix('.json.gz')  # retained endpoints are stored compressed
    opener = gzip.open if path.suffix == '.gz' else open
    with opener(path, 'rb') as stream:
        return json.load(stream)


def result(root, name, wheel_sha256):
    payload = read(root / name)
    assert payload['wheel_sha256'] == wheel_sha256, name
    return payload['result']


def parameter_fingerprint(mapping: dict[str, object]) -> str:
    text = json.dumps(mapping, sort_keys=True, separators=(',', ':'))
    return f"sha256:{hashlib.sha256(text.encode()).hexdigest()}"
