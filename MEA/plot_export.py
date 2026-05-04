from pathlib import Path


def repo_root() -> Path:
    return Path(__file__).resolve().parents[1]


def default_output_dir(script_path) -> Path:
    script = Path(script_path).resolve()
    return repo_root() / "out" / "plots" / "MEA" / script.stem


def save_plot(fig, script_path, figure_name=None, *, dpi=300, close=True) -> Path:
    script = Path(script_path).resolve()
    output_dir = default_output_dir(script)
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
