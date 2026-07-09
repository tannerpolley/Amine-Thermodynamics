from __future__ import annotations

import argparse
import hashlib
import json
import re
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
LATEX_DIR = ROOT / "docs" / "latex"
BUILD_DIR = LATEX_DIR / "builds"
PDF_PATH = BUILD_DIR / "main.pdf"
LOG_PATH = BUILD_DIR / "main.log"
BLG_PATH = BUILD_DIR / "main.blg"
RECEIPT_PATH = BUILD_DIR / "verification-receipt.json"

INPUT_SUFFIXES = {".tex", ".bib", ".bst", ".cls", ".sty", ".pdf", ".png", ".svg", ".jpg", ".jpeg"}
UNDEFINED_PATTERNS = (
    re.compile(r"Citation .* undefined", re.IGNORECASE),
    re.compile(r"Reference .* undefined", re.IGNORECASE),
    re.compile(r"There were undefined references", re.IGNORECASE),
    re.compile(r"I didn't find a database entry for", re.IGNORECASE),
)


def manuscript_inputs() -> list[Path]:
    completed = subprocess.run(
        ["git", "ls-files", "-z", "--cached", "--others", "--exclude-standard", "--", "docs/latex"],
        cwd=ROOT,
        check=True,
        capture_output=True,
    )
    relative_paths = [Path(item.decode()) for item in completed.stdout.split(b"\0") if item]
    inputs = sorted(
        ROOT / path
        for path in relative_paths
        if path.suffix.lower() in INPUT_SUFFIXES and "builds" not in path.parts and "out" not in path.parts
    )
    if not inputs:
        raise RuntimeError("No tracked manuscript inputs were found.")
    return inputs


def file_sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def input_sha256(paths: list[Path]) -> str:
    digest = hashlib.sha256()
    for path in paths:
        relative = path.relative_to(ROOT).as_posix().encode()
        digest.update(relative)
        digest.update(b"\0")
        digest.update(bytes.fromhex(file_sha256(path)))
    return digest.hexdigest()


def validate_build(paths: list[Path]) -> dict[str, object]:
    for path in (PDF_PATH, LOG_PATH):
        if not path.is_file():
            raise RuntimeError(f"Missing manuscript build artifact: {path.relative_to(ROOT)}")

    newest_input = max(path.stat().st_mtime_ns for path in paths)
    if PDF_PATH.stat().st_mtime_ns < newest_input:
        raise RuntimeError("docs/latex/builds/main.pdf is older than a manuscript input.")

    logs = LOG_PATH.read_text(encoding="utf-8", errors="replace")
    if BLG_PATH.exists():
        logs += "\n" + BLG_PATH.read_text(encoding="utf-8", errors="replace")
    failures = [pattern.pattern for pattern in UNDEFINED_PATTERNS if pattern.search(logs)]
    if failures:
        raise RuntimeError("Manuscript build contains undefined citations or references: " + ", ".join(failures))

    return {
        "input_count": len(paths),
        "input_sha256": input_sha256(paths),
        "pdf_sha256": file_sha256(PDF_PATH),
        "pdf_size_bytes": PDF_PATH.stat().st_size,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="Verify that the manuscript PDF matches current tracked inputs.")
    parser.add_argument("--write-receipt", action="store_true", help="Record the current successful build hashes.")
    args = parser.parse_args()

    build = validate_build(manuscript_inputs())
    if args.write_receipt:
        BUILD_DIR.mkdir(parents=True, exist_ok=True)
        RECEIPT_PATH.write_text(json.dumps(build, indent=2, sort_keys=True) + "\n", encoding="utf-8")
        print(f"Manuscript verification receipt: {RECEIPT_PATH.relative_to(ROOT)}")
        return 0

    if not RECEIPT_PATH.is_file():
        raise RuntimeError(f"Missing manuscript verification receipt: {RECEIPT_PATH.relative_to(ROOT)}")
    recorded = json.loads(RECEIPT_PATH.read_text(encoding="utf-8"))
    for key in ("input_count", "input_sha256", "pdf_sha256", "pdf_size_bytes"):
        if recorded.get(key) != build[key]:
            raise RuntimeError(f"Manuscript build receipt mismatch for {key}; rebuild with scripts/build_manuscript.sh.")
    print(f"Manuscript PDF is current: {PDF_PATH.relative_to(ROOT)} ({build['pdf_sha256']})")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
