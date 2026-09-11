"""Reject mixed-generation data, figures, and handoffs without running the model."""

from __future__ import annotations

import argparse
import gzip
import hashlib
import json
from pathlib import Path

ANALYSIS = Path(__file__).resolve().parents[1]
REPO = ANALYSIS.parents[1]
PARAMETERS = ANALYSIS / "results/selected-current-best-parameters.json"
ENGINE = ANALYSIS / "data/input/engine/epcsaft-0.2.0.dev0-cp313-cp313-linux_x86_64.whl"
FIGURE_DATA = ANALYSIS / "results/figure-calculation-receipt.json"
FIGURES = ANALYSIS / "results/figure-render-receipt.json"
HEAT = ANALYSIS / "results/calorimetry/current-selected-direct-enthalpy-summary.json"
THERMAL = ANALYSIS / "results/calorimetry/thermal-reference-validation.json"
NOTEBOOK = ANALYSIS / "results/notebook-render-receipt.json"


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


def source_hashes(*sources: Path) -> dict[str, str]:
    return hashes((PARAMETERS, ENGINE, *sources))


def require_hashes(expected: dict[str, str]) -> None:
    for name, digest in expected.items():
        path = REPO / name
        if not path.is_file() and path.suffix == ".json":
            path = path.with_suffix(".json.gz")
        if not path.is_file() or hashes((path,)).get(name) != digest:
            raise ValueError(
                f"Stale or missing input/output: {name}; regenerate its owning stage"
            )


def stamp_results(
    receipt_path: Path,
    output_paths: list[Path],
    sources: tuple[Path, ...] = (),
    *,
    inputs: dict[str, str] | None = None,
) -> None:
    """Call only after successful generation; pass start-of-run inputs for long jobs."""
    expected = source_hashes(*sources) if inputs is None else inputs
    require_hashes(expected)
    payload = json.loads(receipt_path.read_text()) if receipt_path.exists() else {}
    payload["publication"] = {"inputs": expected, "outputs": hashes(output_paths)}
    pending = receipt_path.with_suffix(receipt_path.suffix + ".tmp")
    pending.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
    pending.replace(receipt_path)


def require_results(receipt_path: Path) -> None:
    if not receipt_path.is_file():
        raise ValueError(f"Missing generation evidence: {receipt_path}")
    publication = json.loads(receipt_path.read_text()).get("publication")
    if (
        not publication
        or not publication.get("inputs")
        or not publication.get("outputs")
    ):
        raise ValueError(
            f"Unverified generation: {receipt_path}; regenerate its owning stage"
        )
    require_hashes(publication["inputs"])
    require_hashes(publication["outputs"])


def require_current_results(*, notebook: bool = False) -> None:
    for receipt in (FIGURE_DATA, FIGURES, HEAT, THERMAL):
        require_results(receipt)
    if notebook:
        require_results(NOTEBOOK)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--stamp-notebook", action="store_true")
    parser.add_argument("--fingerprint", action="store_true")
    parser.add_argument("--expected-fingerprint")
    args = parser.parse_args()
    require_current_results()
    pages = sorted(
        path for path in ANALYSIS.rglob("*.qmd") if "_site" not in path.parts
    )
    inputs = source_hashes(
        *pages,
        ANALYSIS / "_quarto.yml",
        FIGURE_DATA,
        FIGURES,
        HEAT,
        THERMAL,
    )
    fingerprint = hashlib.sha256(
        json.dumps(inputs, sort_keys=True).encode()
    ).hexdigest()
    if args.fingerprint:
        print(fingerprint)
        raise SystemExit(0)
    if args.stamp_notebook:
        if args.expected_fingerprint != fingerprint:
            raise ValueError(
                "Notebook inputs changed during rendering; refusing certification"
            )
        stamp_results(
            NOTEBOOK,
            [page.with_suffix(".html") for page in pages],
            inputs=inputs,
        )
    print("Current result hashes verified; no model execution")
