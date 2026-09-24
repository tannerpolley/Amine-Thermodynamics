"""Reject mixed-generation data, figures, and handoffs without running the model."""

from __future__ import annotations

import argparse
import gzip
import hashlib
import json
from pathlib import Path
import subprocess

ANALYSIS = Path(__file__).resolve().parents[1]
REPO = ANALYSIS.parents[1]
MANUSCRIPT = ANALYSIS.parent
PARAMETERS = ANALYSIS / "results/selected-current-best-parameters.json"
# The pinned wheel lives outside the repository; its SHA-256 (enforced against the
# installed wheel by shared_evaluation.verify_wheel) is the Engine identity.
ENGINE_KEY = "engine_wheel_sha256"
FIGURE_DATA = ANALYSIS / "results/figure-calculation-record.json"
FIGURES = ANALYSIS / "results/figure-render-record.json"
HEAT = ANALYSIS / "results/calorimetry/current-selected-direct-enthalpy-summary.json"
THERMAL = ANALYSIS / "results/calorimetry/thermal-reference-validation.json"
NOTEBOOK = ANALYSIS / "results/notebook-render-record.json"


def hashes(paths: list[Path] | tuple[Path, ...]) -> dict[str, str]:
    result = {}
    for requested in paths:
        path = requested
        if not path.is_file() and path.suffix == ".json":
            path = path.with_suffix(".json.gz")
        data = path.read_bytes()
        logical = path
        if path.name.endswith(".json.gz"):
            data = gzip.decompress(data)
            logical = path.with_suffix("")
        result[str(logical.resolve().relative_to(REPO))] = hashlib.sha256(data).hexdigest()
    return result


def pinned_engine_wheel_sha256() -> str:
    from shared_evaluation import ENGINE_WHEEL_SHA256

    return ENGINE_WHEEL_SHA256


def source_hashes(*sources: Path) -> dict[str, str]:
    return {ENGINE_KEY: pinned_engine_wheel_sha256(), **hashes((PARAMETERS, *sources))}


def require_hashes(expected: dict[str, str]) -> None:
    for name, digest in expected.items():
        if name == ENGINE_KEY:
            if digest != pinned_engine_wheel_sha256():
                raise ValueError(
                    f"Stale Engine: generated with wheel {digest}; regenerate its owning stage"
                )
            continue
        path = REPO / name
        if not path.is_file() and path.suffix == ".json":
            path = path.with_suffix(".json.gz")
        if not path.is_file() or hashes((path,)).get(name) != digest:
            raise ValueError(
                f"Stale or missing input/output: {name}; regenerate its owning stage"
            )


def stamp_results(
    record_path: Path,
    output_paths: list[Path],
    sources: tuple[Path, ...] = (),
    *,
    inputs: dict[str, str] | None = None,
) -> None:
    """Call only after successful generation; pass start-of-run inputs for long jobs."""
    expected = source_hashes(*sources) if inputs is None else inputs
    require_hashes(expected)
    payload = json.loads(record_path.read_text()) if record_path.exists() else {}
    payload["publication"] = {"inputs": expected, "outputs": hashes(output_paths)}
    pending = record_path.with_suffix(record_path.suffix + ".tmp")
    pending.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
    pending.replace(record_path)


def require_results(record_path: Path) -> None:
    if not record_path.is_file():
        raise ValueError(f"Missing generation evidence: {record_path}")
    publication = json.loads(record_path.read_text()).get("publication")
    if (
        not publication
        or not publication.get("inputs")
        or not publication.get("outputs")
    ):
        raise ValueError(
            f"Unverified generation: {record_path}; regenerate its owning stage"
        )
    require_hashes(publication["inputs"])
    require_hashes(publication["outputs"])


def require_current_results(*, notebook: bool = False) -> None:
    for record in (FIGURE_DATA, FIGURES, HEAT, THERMAL):
        require_results(record)
    if notebook:
        require_results(NOTEBOOK)


def bundle_pages() -> list[Path]:
    return sorted(ANALYSIS.rglob("*.qmd"))


def rendered_page(page: Path) -> Path:
    """Native Quarto Manuscript view of a registered notebook page."""
    relative = page.relative_to(MANUSCRIPT).with_name(f"{page.stem}-preview.html")
    return MANUSCRIPT / "_site" / relative


def render_inputs() -> dict[str, str]:
    return source_hashes(
        *bundle_pages(),
        MANUSCRIPT / "_quarto.yml",
        MANUSCRIPT / "_cse-manuscript.json",
        FIGURE_DATA,
        FIGURES,
        HEAT,
        THERMAL,
    )


def certify() -> None:
    """Render through the root CSE wrapper and stamp only unchanged inputs."""
    require_current_results()
    inputs = render_inputs()
    subprocess.run(["bash", "render.sh"], cwd=MANUSCRIPT, check=True)
    if render_inputs() != inputs:
        raise ValueError("Notebook inputs changed during rendering; refusing certification")
    stamp_results(NOTEBOOK, [rendered_page(page) for page in bundle_pages()], inputs=inputs)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--certify",
        action="store_true",
        help="render the root manuscript and stamp the bundle HTML",
    )
    if parser.parse_args().certify:
        certify()
    else:
        require_current_results()
    print("Current result hashes verified; no model execution")
