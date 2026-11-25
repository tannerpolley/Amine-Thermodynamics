"""Resolve immutable contributors and keep the calculation and display paths separate."""
import csv
import gzip
from functools import cache
from hashlib import sha256
import json
from pathlib import Path
import subprocess
import tomllib
HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
OUT = HERE / 'results'
R7 = 'analyses/round_7/results/'
BASE = 'be37c32a3'
DISPLAY = 'be3e316c5'
MEA = 'analyses/mea_parameter_bundle/results/salt-anchored-435/MEA/'
MDEA = 'analyses/mdea_mea_workflow/results/'
SALT = 'analyses/mea_parameter_bundle/results/carbonate-ions-282/'
LIMITS = (210, 85, 10, 12, 20, 45, 8)
NAMES = ('reference-derivatives', 'mdea-phase-outcomes', 'dea-split-densities', 'amp-six-states',
         'salt-and-weighting', 'endpoint-comparison', 'literature-populations')

@cache
def blob(path, revision):
    return subprocess.check_output(['git', 'show', f'{revision}:{path}'], cwd=ROOT)

class Sources:
    def __init__(self):
        self.hashes = {}

    @cache
    def read(self, path, revision=BASE):
        data = blob(path, revision) if revision else (ROOT / path).read_bytes()
        if revision == BASE and sha256((ROOT / path).read_bytes()).digest() != sha256(data).digest():
            raise ValueError(f'changed contributor: {path}')
        self.hashes[path] = dict(revision=revision, sha256=sha256(data).hexdigest())
        if path.endswith('.toml'):
            return tomllib.loads(data.decode())
        if path.endswith('.csv'):
            return list(csv.DictReader(data.decode().splitlines()))
        return json.loads(gzip.decompress(data) if path.endswith('.gz') else data)

    def core(self, path):
        return self.read(R7 + path)

    def display(self, name):
        record = self.read(R7 + f'display-replays/{name}.json.gz', DISPLAY)
        for path,digest in record['sources'].items():
            source = blob(path,DISPLAY)
            assert sha256(gzip.decompress(source) if path.endswith('.gz') else source).hexdigest()==digest, path
        return record

def write(path, value):
    data = (json.dumps(value, indent=2, allow_nan=False) + '\n').encode()
    tmp = path.with_suffix('.tmp')
    tmp.write_bytes(gzip.compress(data, mtime=0) if path.suffix == '.gz' else data)
    tmp.replace(path)

def replay_path(item):
    return OUT / f'C{item}-replays.json.gz'
