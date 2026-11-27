from __future__ import annotations

import argparse
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PY = sys.executable
RUFF = str(Path(PY).with_name("ruff"))
MAX_TRACKED_JSON_BYTES = 100 * 1024
MAX_TRACKED_JSON_LINES = 3_000
MAX_TRACKED_TEXT_BYTES = 1024 * 1024
MAX_TRACKED_FILE_BYTES = 5 * 1024 * 1024
TEXT_SUFFIXES = {".bib", ".csv", ".md", ".py", ".svg", ".tex", ".toml", ".tsv", ".txt", ".yaml", ".yml"}

QUICK_COMMANDS = [
    [RUFF, "check", "src", "scripts", "analyses", "tests"],
    [PY, "scripts/doctor.py"],
    [PY, "scripts/check_no_local_paths.py"],
    [PY, "scripts/validate_mea_data_library.py"],
    [PY, "-m", "compileall", "-x", r"results[\\/]+runs", "src", "tests", "scripts", "analyses"],
    [PY, "-m", "pytest", "-q", "--ignore=upstream"],
]


def run(command: list[str]) -> int:
    print("\n$ " + " ".join(command))
    return subprocess.run(command, cwd=ROOT).returncode



def tracked_size_problem(path: Path) -> str | None:
    byte_count = path.stat().st_size
    if path.suffix == ".json" and byte_count > MAX_TRACKED_JSON_BYTES:
        return f"{byte_count} bytes > {MAX_TRACKED_JSON_BYTES}"
    if path.suffix == ".json":
        with path.open("rb") as stream:
            line_count = sum(1 for _ in stream)
        if line_count > MAX_TRACKED_JSON_LINES:
            return f"{line_count} lines > {MAX_TRACKED_JSON_LINES}"
    if path.suffix.lower() in TEXT_SUFFIXES and byte_count > MAX_TRACKED_TEXT_BYTES:
        return f"{byte_count} bytes > {MAX_TRACKED_TEXT_BYTES}"
    if byte_count > MAX_TRACKED_FILE_BYTES:
        return f"{byte_count} bytes > {MAX_TRACKED_FILE_BYTES}"
    return None


def verify_tracked_file_size() -> int:
    tracked = subprocess.run(
        ["git", "ls-files", "-z"],
        cwd=ROOT,
        check=True,
        capture_output=True,
        text=True,
    ).stdout.split("\0")
    oversized: list[str] = []
    for relative in filter(None, tracked):
        path = ROOT / relative
        if not path.is_file():
            continue
        if problem := tracked_size_problem(path):
            oversized.append(f"{relative}: {problem}")
    if oversized:
        print("Oversized tracked files:")
        for problem in oversized:
            print(f"  {problem}")
        print("Remove generated files; compact or split durable evidence.")
        return 1
    print("Tracked file size contract passed.")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(description="Validate the Amine-Thermodynamics project layout and analysis artifacts.")
    parser.add_argument("mode", choices=["quick", "confidence"], help="quick runs structural/tests checks; confidence also checks the manuscript displays")
    args = parser.parse_args()

    commands = list(QUICK_COMMANDS)
    if args.mode == "confidence":
        commands.append([PY, "-m", "analyses.amines.displays", "--check"])
    status = verify_tracked_file_size()
    if status:
        return status
    for command in commands:
        status = max(status, run(command))
        if status:
            return status
    return status


if __name__ == "__main__":
    raise SystemExit(main())
