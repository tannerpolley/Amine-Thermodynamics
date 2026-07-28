# Technical Stack

- Python `>=3.13,<3.14`, source layout under `src/`, setuptools build backend, uv lockfile/workflows.
- Core scientific stack: NumPy, pandas, SciPy, Matplotlib.
- Thermodynamic dependencies are immutable Git pins in `pyproject.toml`/`uv.lock`: `epcsaft` for active ePC-SAFT evaluation and `pcsaft` for retained legacy baseline comparison.
- Quality tools: Ruff and pytest.
- Manuscript: LaTeX/latexmk with tracked BibTeX databases; build wrapper enforces deterministic timestamps and freshness hashes.
- Final ePC-SAFT integration must use stable/pinned mode; development provider state is not admissible for final results.
