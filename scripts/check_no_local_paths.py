from __future__ import annotations

import re
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
TARGETS = (
    "docs",
    "data/reference/MEA/manifests",
    "analyses",
    "pyproject.toml",
    "uv.lock",
    "src/MEA",
)
FORBIDDEN_PATTERNS = (
    re.compile(r"C:/Users/", re.IGNORECASE),
    re.compile(r"C:\\Users\\", re.IGNORECASE),
    re.compile(r"/Users/[^/\s]+/"),
    re.compile(r"Documents[\\/]git[\\/]", re.IGNORECASE),
)
SKIP_SUFFIXES = {
    ".png",
    ".jpg",
    ".jpeg",
    ".gif",
    ".pdf",
    ".ico",
    ".pkl",
    ".pickle",
    ".pyc",
}


def tracked_files() -> list[Path]:
    result = subprocess.run(
        ["git", "ls-files", "-z", "--", *TARGETS],
        cwd=ROOT,
        check=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
    )
    names = result.stdout.decode("utf-8", errors="surrogateescape").split("\0")
    return [ROOT / name for name in names if name]


def scan_file(path: Path) -> list[tuple[int, str]]:
    if path.suffix.lower() in SKIP_SUFFIXES:
        return []
    try:
        text = path.read_text(encoding="utf-8")
    except UnicodeDecodeError:
        text = path.read_text(encoding="utf-8", errors="ignore")
    violations: list[tuple[int, str]] = []
    for line_number, line in enumerate(text.splitlines(), start=1):
        if any(pattern.search(line) for pattern in FORBIDDEN_PATTERNS):
            violations.append((line_number, line.strip()))
    return violations


def main() -> int:
    failures: list[tuple[Path, int, str]] = []
    for path in tracked_files():
        if not path.exists():
            continue
        for line_number, line in scan_file(path):
            failures.append((path, line_number, line))
    if failures:
        print("Tracked files contain non-portable local paths:")
        for path, line_number, line in failures:
            rel = path.relative_to(ROOT).as_posix()
            print(f"  {rel}:{line_number}: {line}")
        return 1
    print("No non-portable local paths found in tracked project artifacts.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
