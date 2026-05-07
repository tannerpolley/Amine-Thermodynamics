from pathlib import Path

from .config import (
    EPCSAFT_IONIC_ANALYSIS,
    EPCSAFT_NEUTRAL_ANALYSIS,
    SIX_SPECIES_ANALYSIS,
)


_ANALYSIS_BY_PACKAGE = {
    "six_species": SIX_SPECIES_ANALYSIS,
    "epcsaft_neutral": EPCSAFT_NEUTRAL_ANALYSIS,
    "epcsaft_ionic": EPCSAFT_IONIC_ANALYSIS,
}


def _workflow_name(script: Path) -> str:
    stem = script.stem
    return stem.removeprefix("plot_")


def default_output_dir(script_path, workflow_name: str | None = None) -> Path:
    script = Path(script_path).resolve()
    workflow = workflow_name or _workflow_name(script)
    package = script.parent.name
    plot_set = workflow.replace("\\", "/").strip("/").split("/")[-1]
    analysis = _ANALYSIS_BY_PACKAGE.get(package)
    if analysis is None:
        analysis = _ANALYSIS_BY_PACKAGE.get(workflow.replace("\\", "/").split("/")[0])
    if analysis is None:
        raise ValueError(f"No analysis output mapping is registered for {script_path!s}")
    return analysis / "results" / plot_set


def _write_default_sidecar(sidecar_path: Path, *, png_name: str, svg_name: str) -> None:
    if sidecar_path.exists():
        return
    sidecar_path.write_text(
        "\n".join(
            [
                "figure:",
                f"  png: {png_name}",
                f"  svg: {svg_name}",
                "  dpi: 300",
                "style:",
                "  source: src/MEA/common/plot_style.py",
                "",
            ]
        ),
        encoding="utf-8",
    )


def save_plot(fig, script_path, figure_name=None, *, workflow_name: str | None = None, dpi=300, close=True) -> Path:
    script = Path(script_path).resolve()
    output_dir = default_output_dir(script, workflow_name)
    output_dir.mkdir(parents=True, exist_ok=True)

    file_name = figure_name or script.stem
    stem = Path(file_name).stem

    output_path = output_dir / f"{stem}.png"
    svg_path = output_dir / f"{stem}.svg"
    sidecar_path = output_dir / f"{stem}.mpl.yaml"
    _write_default_sidecar(sidecar_path, png_name=output_path.name, svg_name=svg_path.name)
    if output_path.exists():
        output_path.unlink()
    if svg_path.exists():
        svg_path.unlink()
    fig.savefig(output_path, dpi=dpi, bbox_inches="tight")
    fig.savefig(svg_path, bbox_inches="tight")
    print(f"Saved plot: {output_path}")
    print(f"Saved SVG: {svg_path}")
    print(f"Plot style sidecar: {sidecar_path}")

    if close:
        import matplotlib.pyplot as plt

        plt.close(fig)

    return output_path
