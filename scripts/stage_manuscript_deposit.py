"""Stage and check the manuscript sources, wheels and declared analysis inputs."""

import argparse
from hashlib import sha256
import json
import os
from pathlib import Path
import re
import shutil
import subprocess
import sys
from tempfile import TemporaryDirectory

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from analyses.amines.records import ROOT, catalog
from analyses.amines.wheel import locked_archive
from check_private_source import PUBLISHED_LINE_HASH, PUBLISHED_PATH, path_is_blocked, scan

LATEX = Path("docs/scientific/latex")
NUMBER_SOURCES = LATEX / "tables/number-sources.json"
SUBMISSION = LATEX / "submission_metadata.yml"


def write_json(path, payload):
    path.write_text(json.dumps(payload, indent=2) + "\n")


def engine_wheels():
    wheel, expected = locked_archive()
    wheels = {wheel.relative_to(ROOT): expected.removeprefix("sha256:")}
    text = (ROOT / SUBMISSION).read_text()
    engines = text.split("\nengines:\n")[1].split("\nparameter_records:")[0]
    declarations = re.findall(
        r"^    version: (\S+)\n    engine_commit: ([a-f0-9]{40})\n"
        r"    engine_wheel_sha256: ([a-f0-9]{64})$", engines, re.MULTILINE,
    )
    if not declarations or len(declarations) != engines.count("  - scope:"):
        raise ValueError("Could not read submission Engine wheel declarations")
    for version, commit, digest in declarations:
        directory = Path("build/engine-wheels") / f"main-{commit}"
        matches = list((ROOT / directory).glob(f"epcsaft-{version}-*.whl"))
        if len(matches) != 1:
            raise ValueError(f"Expected one Engine {version} wheel in {directory}")
        path = directory / matches[0].name
        if path in wheels and wheels[path] != digest:
            raise ValueError(f"Submission and uv.lock wheel hashes differ: {path}")
        wheels[path] = digest
    return wheels


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
                    or path.name == ".latexmkrc" or "figures" in path.parts
                    or path.name.startswith("graphical_abstract."))):  # displays --check regenerates it
            selected.add(path)
    wheels = engine_wheels()
    selected.update(wheels)
    for path in sorted(selected):
        source = ROOT / path
        if path.is_absolute() or ".." in path.parts or path_is_blocked(path.as_posix()) or source.is_symlink():
            raise ValueError("Deposit input violates the source path rules")
        if not source.is_file():
            raise FileNotFoundError(path)
        value = source.read_bytes()
        if expected_input := wheels.get(path) or retained.get(path.as_posix(), {}).get("sha256"):
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
        files=len(selected), wheel_sha256={path.as_posix(): digest for path, digest in wheels.items()},
    ))
    shutil.copyfile(ROOT / "scripts/deposit_examples/README.md", destination / "README.md")
    print(f"Staged {len(selected)} inputs at {destination}")


def rebuild(destination):
    latex = destination / LATEX
    env = {**os.environ, "TEXINPUTS": "./styles//:"}
    env.pop("VIRTUAL_ENV", None)
    with TemporaryDirectory() as directory:
        displays = subprocess.run(
            ["uv", "run", "--locked", "python", "-m", "analyses.amines.displays", "--check"],
            cwd=destination, env={**env, "UV_PROJECT_ENVIRONMENT": directory}, text=True, stdout=subprocess.PIPE,
        )
    print(displays.stdout, end="", flush=True)
    displays.check_returncode()
    for name in ("supplement", "main", "supplement", "main"):
        subprocess.run(["latexmk", "-g", "-pdf", "-interaction=nonstopmode", "-halt-on-error",
                        "-outdir=builds", f"{name}.tex"], cwd=latex, env=env, check=True)
    checks = {}
    for name in ("main", "supplement"):
        path = latex / "builds" / f"{name}.pdf"
        reference = ROOT / LATEX / "builds" / path.name
        actual = pdf_text(path)
        (destination / "provenance" / f"{name}.txt").write_bytes(actual)
        checks[name] = {
            "pdf_sha256": sha256(path.read_bytes()).hexdigest(),
            "reference_pdf_sha256": sha256(reference.read_bytes()).hexdigest(),
            "layout_text_matches": actual == pdf_text(reference),
            "pages": actual.count(b"\f"),
            "undefined_references_or_citations": bool(re.search(
                r"Warning:.*undefined", path.with_suffix(".log").read_text(errors="replace"),
            )),
        }
    write_json(destination / "provenance" / "rebuild-check.json", {**checks, "displays": displays.stdout.strip()})
    if not all(row["layout_text_matches"] and not row["undefined_references_or_citations"]
               for row in checks.values()):
        raise ValueError("Rebuilt PDF text differs or cross-references remain undefined")
    for name in checks:
        subprocess.run(["latexmk", "-c", "-outdir=builds", f"{name}.tex"],
                       cwd=latex, env=env, check=True)


def pdf_text(path):
    return subprocess.check_output(["pdftotext", "-layout", str(path), "-"])


def seal(destination):
    paths = sorted(path for path in destination.rglob("*") if path.is_file()
                   and not any((part.startswith(".") and part != ".latexmkrc") or part == "__pycache__"
                               or part.endswith(".egg-info")
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
