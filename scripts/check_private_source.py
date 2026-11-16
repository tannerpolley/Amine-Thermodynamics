"""Reject private-source identifiers using configuration kept outside Git."""
from functools import lru_cache
import hashlib
import json
import os
from pathlib import Path
import subprocess

PUBLISHED_PATH = "docs/scientific/latex/references.bib"
PUBLISHED_LINE_HASH = "248491963d1ff382cd0ce4c72665e02d099d27b575caed9e9fe920c63e68d507"


@lru_cache(maxsize=1)
def patterns():
    raw = os.environ.get("PRIVATE_SOURCE_PATTERNS")
    if not raw:
        root = Path(__file__).resolve().parents[1]
        common = subprocess.check_output(["git", "rev-parse", "--git-common-dir"], cwd=root).decode().strip()
        config = (root / common / "private-source-patterns.json").resolve()
        if not config.is_file():
            raise SystemExit("Private-source check requires private configuration or PRIVATE_SOURCE_PATTERNS.")
        raw = config.read_text()
    values = json.loads(raw)
    if not isinstance(values, list) or not values or not all(isinstance(v, str) and v for v in values):
        raise SystemExit("Invalid private-source check configuration.")
    return tuple(value.lower() for value in values)


def path_is_blocked(path):
    return any(value in path.lower() for value in patterns())


def violations(path, data):
    label = hashlib.sha256(path.encode()).hexdigest()[:12]
    if path_is_blocked(path):
        yield f"tracked path {label}: private-source identifier"
    if b"\0" in data:
        return
    for number, line in enumerate(data.decode("utf-8", errors="replace").splitlines(), 1):
        if path == PUBLISHED_PATH and hashlib.sha256(line.encode()).hexdigest() == PUBLISHED_LINE_HASH:
            continue
        if any(value in line.lower() for value in patterns()):
            yield f"tracked path {label}, line {number}: private-source identifier"


if __name__ == "__main__":
    root = Path(__file__).resolve().parents[1]
    patterns()
    paths = subprocess.check_output(["git", "ls-files", "-z"], cwd=root).decode().split("\0")
    failures = []
    for path in paths:
        if not path:
            continue
        file = root / path
        if file.is_symlink():
            data = os.readlink(file).encode()
        elif file.is_file():
            data = file.read_bytes()
        else:
            continue
        failures.extend(violations(path, data))
    if failures:
        raise SystemExit("\n".join(failures))
