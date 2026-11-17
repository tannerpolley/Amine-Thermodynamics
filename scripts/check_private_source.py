"""Reject private-source identifiers using configuration kept outside Git."""
from functools import lru_cache
import hashlib
import json
import os
from pathlib import Path
import subprocess
import tempfile

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


def search(command, root, data=None):
    result = subprocess.run(command, cwd=root, input=data, capture_output=True, env={**os.environ, "GIT_ATTR_NOSYSTEM": "1"})
    if result.returncode not in (0, 1):
        raise SystemExit("Private-source search failed.")
    return result.stdout


def scan(root):
    values = patterns()
    if any(any(char in value for char in "\r\n\0") for value in values):
        raise SystemExit("Invalid private-source check configuration.")
    with tempfile.NamedTemporaryFile(mode="w", encoding="utf-8") as pattern_file:
        pattern_file.write("\n".join(values) + "\n")
        pattern_file.flush()
        empty = subprocess.run(["git", "mktree"], cwd=root, input=b"", capture_output=True)
        if empty.returncode:
            raise SystemExit("Private-source attribute isolation failed.")
        git = ["git", "--attr-source=" + empty.stdout.decode("ascii").strip(),
               "-c", "core.attributesFile=/dev/null"]
        if cores := os.environ.get("AGENT_HEAVY_CORES"):
            git.extend(["-c", f"grep.threads={int(cores)}"])
        matches = search(git + ["grep", "-I", "-i", "-n", "-z", "-F", "-f", pattern_file.name, "--"], root)
        failures = []
        while matches:
            path, separator, matches = matches.partition(b"\0")
            number, second_separator, matches = matches.partition(b"\0")
            if not separator or not second_separator or not number.isdigit():
                raise SystemExit("Invalid private-source search output.")
            line, _, matches = matches.partition(b"\n")
            if path == PUBLISHED_PATH.encode() and hashlib.sha256(line).hexdigest() == PUBLISHED_LINE_HASH:
                continue
            label = hashlib.sha256(path).hexdigest()[:12]
            failures.append(f"tracked path {label}, line {int(number)}: private-source identifier")
        tracked = subprocess.run(["git", "ls-files", "-z"], cwd=root, capture_output=True)
        if tracked.returncode:
            raise SystemExit("Private-source tracked-path search failed.")
        paths = search(["grep", "-a", "-z", "-i", "-F", "-f", pattern_file.name], root, tracked.stdout)
        failures.extend(f"tracked path {hashlib.sha256(path).hexdigest()[:12]}: private-source identifier"
                        for path in paths.split(b"\0") if path)
        staged = subprocess.run(["git", "ls-files", "--stage", "-z"], cwd=root, capture_output=True)
        if staged.returncode:
            raise SystemExit("Private-source link listing failed.")
        for entry in staged.stdout.split(b"\0"):
            if not entry.startswith(b"120000 "):
                continue
            metadata, path = entry.split(b"\t", 1)
            target = subprocess.run(["git", "cat-file", "blob", metadata.split()[1]],
                                    cwd=root, capture_output=True)
            if target.returncode:
                raise SystemExit("Private-source link search failed.")
            if search(["grep", "-a", "-i", "-F", "-f", pattern_file.name], root, target.stdout):
                failures.append(f"tracked path {hashlib.sha256(path).hexdigest()[:12]}: private-source identifier")
    return failures


if __name__ == "__main__":
    failures = scan(Path(__file__).resolve().parents[1])
    if failures:
        raise SystemExit("\n".join(failures))
