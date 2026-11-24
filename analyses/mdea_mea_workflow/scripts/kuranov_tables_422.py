"""Materialize the notebook's checked tables without running the model."""
from contextlib import redirect_stdout
from pathlib import Path
import os

root = Path(__file__).resolve().parents[1]
os.chdir(root)
cell = (root / "notebook.qmd").read_text().split("```{python}", 1)[1].split("```", 1)[0]
with (root / "results/kuranov-published-422/tables.md").open("w") as output, redirect_stdout(output):
    exec(compile(cell, "notebook.qmd", "exec"))
