from pathlib import Path

from .config import PLOT_ROOT


def _workflow_name(script: Path) -> str:
    stem = script.stem
    return stem.removeprefix("plot_")


def default_output_dir(script_path, workflow_name: str | None = None) -> Path:
    script = Path(script_path).resolve()
    workflow = workflow_name or _workflow_name(script)
    package = script.parent.name
    if package in {"six_species", "nine_species"}:
        return PLOT_ROOT / package / workflow
    return PLOT_ROOT / workflow


def save_plot(fig, script_path, figure_name=None, *, workflow_name: str | None = None, dpi=300, close=True) -> Path:
    script = Path(script_path).resolve()
    output_dir = default_output_dir(script, workflow_name)
    output_dir.mkdir(parents=True, exist_ok=True)

    file_name = figure_name or script.stem
    if not file_name.lower().endswith(".png"):
        file_name = f"{file_name}.png"

    output_path = output_dir / file_name
    if output_path.exists():
        output_path.unlink()
    fig.savefig(output_path, dpi=dpi, bbox_inches="tight")
    print(f"Saved plot: {output_path}")

    if close:
        import matplotlib.pyplot as plt

        plt.close(fig)

    return output_path
