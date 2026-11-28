"""Stage and check the manuscript sources, wheel and declared analysis inputs."""

import argparse
from hashlib import sha256
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from analyses.amines.records import ROOT, catalog
from analyses.amines.wheel import locked_archive
from check_private_source import PUBLISHED_LINE_HASH, PUBLISHED_PATH, path_is_blocked, scan

LATEX = Path("docs/scientific/latex")
NUMBER_SOURCES = LATEX / "tables/number-sources.json"


def write_json(path, payload):
    path.write_text(json.dumps(payload, indent=2) + "\n")


def stage(destination):
    if destination.exists() and any(destination.iterdir()):
        raise ValueError(f"Deposit destination is not empty: {destination}")
    failures = scan(ROOT)
    if failures:
        raise SystemExit("\n".join(failures))
    tracked = subprocess.check_output(["git", "ls-files", "-z"], cwd=ROOT, text=True).split("\0")
    selected = {Path("LICENSE"), Path("pyproject.toml"), Path("uv.lock"), NUMBER_SOURCES}
    retained = catalog()
    number_sources = json.loads((ROOT / NUMBER_SOURCES).read_text())
    selected.update(Path(path) for path, row in retained.items()
                    if row["disposition"] not in {"comparison-only", "orphan", "notebook-input"})
    selected.update(Path(path) for path, row in number_sources.items() if row["read"])
    for name in filter(None, tracked):
        path = Path(name)
        if (name.startswith(("src/MEA/", "scripts/deposit_examples/"))
                or name.startswith("analyses/amines/") and path.suffix in {".py", ".qmd"}
                or path == Path("analyses/amines/number-collisions.json")
                or path == Path("analyses/amines/sources.json")
                or path.is_relative_to(LATEX) and (path.suffix in {".tex", ".bib", ".cls", ".bst", ".sty"}
                    or path.name == ".latexmkrc" or "figures" in path.parts)):
            selected.add(path)
    wheel, expected = locked_archive()
    if "sha256:" + sha256(wheel.read_bytes()).hexdigest() != expected:
        raise ValueError("Deposit wheel differs from uv.lock")
    selected.add(wheel.relative_to(ROOT))
    for path in sorted(selected):
        source = ROOT / path
        if path.is_absolute() or ".." in path.parts or path_is_blocked(path.as_posix()) or source.is_symlink():
            raise ValueError("Deposit input violates the source path rules")
        if not source.is_file():
            raise FileNotFoundError(path)
        value = source.read_bytes()
        if expected_input := retained.get(path.as_posix(), {}).get("sha256"):
            if sha256(value).hexdigest() != expected_input:
                raise ValueError(f"Changed deposit input: {path}")
        if path.as_posix() == PUBLISHED_PATH:
            value = b"".join(line for line in value.splitlines(keepends=True)
                             if sha256(line.rstrip(b"\r\n")).hexdigest() != PUBLISHED_LINE_HASH)
        output = destination / path
        output.parent.mkdir(parents=True, exist_ok=True)
        output.write_bytes(value)
    (destination / "provenance").mkdir(exist_ok=True)
    write_json(destination / "provenance/source.json", dict(
        commit=subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=ROOT, text=True).strip(),
        files=len(selected), wheel_sha256=expected,
    ))
    shutil.copyfile(ROOT / "scripts/deposit_examples/README.md", destination / "README.md")
    print(f"Staged {len(selected)} inputs at {destination}")


def rebuild(destination):
    latex = destination / LATEX
    env = {**os.environ, "TEXINPUTS": "./styles//:"}
    for name in ("supplement", "main", "supplement", "main"):
        subprocess.run(["latexmk", "-pdf", "-interaction=nonstopmode", "-halt-on-error",
                        "-outdir=builds", f"{name}.tex"], cwd=latex, env=env, check=True)
    for name in ("main", "supplement"):
        path = latex / "builds" / f"{name}.pdf"
        subprocess.run(["pdftotext", "-layout", str(path), str(destination / "provenance" / f"{name}.txt")], check=True)


def seal(destination):
    paths = sorted(path for path in destination.rglob("*") if path.is_file()
                   and not any(part.startswith(".") or part == "__pycache__"
                               for part in path.relative_to(destination).parts)
                   and path.name != "SHA256SUMS")
    (destination / "SHA256SUMS").write_text("".join(
        f"{sha256(path.read_bytes()).hexdigest()}  {path.relative_to(destination).as_posix()}\n" for path in paths))
    print(f"Recorded {len(paths)} checksums")


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("operation", choices=("stage", "rebuild", "seal"))
    parser.add_argument("destination", type=Path)
    args = parser.parse_args()
    {"stage": stage, "rebuild": rebuild, "seal": seal}[args.operation](args.destination.resolve())


if __name__ == "__main__":
    main()
