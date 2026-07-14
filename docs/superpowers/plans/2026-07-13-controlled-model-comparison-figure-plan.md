# Controlled Model Comparison Figure Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Add a deterministic, manuscript-ready two-panel figure that visualizes the same-record Phase 1/Phase 2 pressure comparison from the saved 31-row paired table.

**Architecture:** Keep calculation and rendering separate. The existing Phase 2 generator owns `paired_pressure_rows.csv`; the Phase 2 renderer validates that table, snapshots only the plotted columns, writes the retained Matplotlib bundle, and copies the PDF into the LaTeX figure tree. Repository validation, MPLGallery, and manuscript tests lock the output and claim boundary.

**Tech Stack:** Python 3.13, pandas, NumPy, Matplotlib, `uv`, `unittest`/pytest, YAML sidecars, LaTeX.

## Global Constraints

- Use only `analyses/phase2/activity_epcsaft/results/controlled_comparison/paired_pressure_rows.csv`; do not recompute either model in the renderer.
- Require exactly the accepted paired rows and fail instead of silently dropping invalid records.
- Communicate model and row outcome with marker shape as well as color.
- Emit same-stem PNG, SVG, and PDF plus exact plotted CSV and `.mpl.yaml` sidecar.
- Register the SVG in `.mplgallery/manifest.yaml` and copy only the PDF into `docs/latex/figures/`.
- State the result as applying to the present fixed parameterization on the 31 tested records.
- Do not display pressure uncertainty because the canonical records contain none.

---

### Task 1: Validate Paired Rows and Render the Figure Bundle

**Files:**
- Create: `tests/test_controlled_comparison_figure.py`
- Create: `analyses/phase2/activity_epcsaft/figures/controlled_comparison/input/source_manifest.csv`
- Create: `analyses/phase2/activity_epcsaft/figures/controlled_comparison/scripts/render_figure.py`
- Modify: `analyses/phase2/activity_epcsaft/scripts/render_figures.py`

**Interfaces:**
- Consumes: `paired_pressure_rows.csv` with observed pressure, both predicted pressures, both signed residuals, acceptance flags, eligibility, and preferred-model labels.
- Produces: `prepare_controlled_comparison_plot_data(rows: pd.DataFrame) -> pd.DataFrame` and `plot_controlled_comparison(rows: pd.DataFrame) -> tuple[Path, Path, Path, Path, Path]`.

- [ ] **Step 1: Write failing validation and classification tests**

Add tests that load the Phase 2 render module, call `prepare_controlled_comparison_plot_data`, and assert:

```python
plot_data = render.prepare_controlled_comparison_plot_data(pd.read_csv(PAIRED_ROWS))
self.assertEqual(len(plot_data), 31)
self.assertEqual(plot_data["comparison_outcome"].value_counts().to_dict(), {"worsened": 27, "improved": 4})
self.assertTrue((plot_data["ideal_abs_log10_error"] >= 0.0).all())
self.assertTrue((plot_data["activity_abs_log10_error"] >= 0.0).all())
```

Also mutate one pressure to zero and one eligibility flag to false; each call must raise `ValueError` with a message identifying the failed contract.

- [ ] **Step 2: Run the focused test and verify RED**

Run:

```bash
uv run pytest tests/test_controlled_comparison_figure.py -q
```

Expected: FAIL because `prepare_controlled_comparison_plot_data` and the controlled-comparison renderer do not exist.

- [ ] **Step 3: Implement the minimal validation and plotting functions**

In `render_figures.py`, add constants for the paired input, output directory, and LaTeX destination. Implement strict required-column validation, boolean normalization, positive finite pressure checks, finite residual checks, accepted/eligible checks, and classification:

```python
plot_data["ideal_abs_log10_error"] = plot_data["phase1_log10_residual"].abs()
plot_data["activity_abs_log10_error"] = plot_data["phase2_log10_residual"].abs()
plot_data["comparison_outcome"] = np.where(
    plot_data["activity_abs_log10_error"] < plot_data["ideal_abs_log10_error"],
    "improved",
    "worsened",
)
```

Reject ties explicitly because the generated summary reports zero ties. Render:

- panel A: observed versus model pressure, log–log, open circles for ideal and filled triangles for activity, with a one-to-one line;
- panel B: ideal absolute residual versus activity absolute residual, linear, with a one-to-one line, improved circles and worsened triangles, plus `4 improved; 27 worsened` annotation.

Use `finish_axes`, `save_figure_bundle`, `normalize_svg`, and `write_mpl_sidecar`. Save the exact prepared frame as `controlled_pressure_comparison_plot_data.csv`, copy the PDF to `docs/latex/figures/mea_controlled_pressure_comparison.pdf`, and return all five retained output paths.

- [ ] **Step 4: Add the focused wrapper and source manifest**

The wrapper imports the Phase 2 render module exactly like the existing pressure wrapper and calls:

```python
paired_rows = pd.read_csv(phase2_render.CONTROLLED_COMPARISON_INPUT)
phase2_render.plot_controlled_comparison(paired_rows)
```

The source manifest contains one canonical input row pointing to `results/controlled_comparison/paired_pressure_rows.csv` and states that it is the accepted same-record comparison input.

- [ ] **Step 5: Invoke the figure from the Phase 2 render entry point**

In `main()`, read the paired table and call `plot_controlled_comparison` before returning. The existing pressure and speciation render calls remain unchanged.

- [ ] **Step 6: Run focused tests and verify GREEN**

Run:

```bash
uv run pytest tests/test_controlled_comparison_figure.py -q
uv run python analyses/phase2/activity_epcsaft/figures/controlled_comparison/scripts/render_figure.py
```

Expected: tests PASS and the five-file figure bundle plus LaTeX PDF exist.

- [ ] **Step 7: Commit the renderer slice**

```bash
git add tests/test_controlled_comparison_figure.py analyses/phase2/activity_epcsaft/scripts/render_figures.py analyses/phase2/activity_epcsaft/figures/controlled_comparison docs/latex/figures/mea_controlled_pressure_comparison.pdf
git commit -m "feat: visualize controlled pressure comparison"
```

### Task 2: Register and Validate the Retained Figure

**Files:**
- Modify: `.mplgallery/manifest.yaml`
- Modify: `scripts/validate_project.py`
- Modify: `tests/test_project_structure.py`
- Test: `tests/test_controlled_comparison_figure.py`

**Interfaces:**
- Consumes: the five-file bundle from Task 1.
- Produces: exact repository validation and MPLGallery registration for the controlled comparison.

- [ ] **Step 1: Write failing artifact-contract assertions**

Add an expected-artifact test that requires:

```python
expected = {
    "controlled_pressure_comparison.png",
    "controlled_pressure_comparison.svg",
    "controlled_pressure_comparison.pdf",
    "controlled_pressure_comparison_plot_data.csv",
    "controlled_pressure_comparison.mpl.yaml",
}
self.assertEqual({path.name for path in OUTPUT.iterdir() if path.is_file()}, expected)
```

Assert that the plotted-data sidecar hash matches the CSV and that the root manifest contains the controlled-comparison SVG, sidecar, and plotted-data paths.

- [ ] **Step 2: Run tests and verify RED**

Run:

```bash
uv run pytest tests/test_controlled_comparison_figure.py tests/test_project_structure.py -q
```

Expected: FAIL because project validation and MPLGallery do not yet own the new bundle.

- [ ] **Step 3: Add exact validation and registry entries**

Add the input manifest and five outputs to the appropriate `REQUIRED_FILES` entries in `scripts/validate_project.py`. Add one manifest record with:

```yaml
- plot_id: analyses__phase2__activity_epcsaft__figures__controlled_comparison__output__controlled_pressure_comparison
  title: Controlled ideal and activity-model pressure comparison
  svg_path: analyses/phase2/activity_epcsaft/figures/controlled_comparison/output/controlled_pressure_comparison.svg
  sidecar_path: analyses/phase2/activity_epcsaft/figures/controlled_comparison/output/controlled_pressure_comparison.mpl.yaml
  data_path: analyses/phase2/activity_epcsaft/figures/controlled_comparison/output/controlled_pressure_comparison_plot_data.csv
  source: project-render
```

- [ ] **Step 4: Run tests and validation and verify GREEN**

Run:

```bash
uv run pytest tests/test_controlled_comparison_figure.py tests/test_project_structure.py -q
uv run python scripts/validate_project.py quick
```

Expected: all tests and quick validation PASS.

- [ ] **Step 5: Commit the ownership slice**

```bash
git add .mplgallery/manifest.yaml scripts/validate_project.py tests/test_project_structure.py analyses/phase2/activity_epcsaft/figures/controlled_comparison
git commit -m "test: register controlled comparison figure"
```

### Task 3: Integrate the Figure into the Manuscript

**Files:**
- Modify: `tests/test_manuscript_claim_integrity.py`
- Modify: `docs/latex/sections/mea_system_modeling_results.tex`
- Retain: `docs/latex/figures/mea_controlled_pressure_comparison.pdf`

**Interfaces:**
- Consumes: the retained controlled-comparison PDF and the existing generated metrics.
- Produces: a submission-safe figure include and caption in Results and Discussion.

- [ ] **Step 1: Write a failing manuscript-integrity test**

Require the Results section to contain:

```python
self.assertIn(r"figures/mea_controlled_pressure_comparison.pdf", results)
self.assertIn(r"\label{fig:controlled-pressure-comparison}", results)
self.assertIn("same 31 Jou1995 records", results)
self.assertIn("present fixed activity treatment", results)
```

Also assert that the caption does not contain repository-facing words such as `artifact`, `generated`, `script`, or `workflow`.

- [ ] **Step 2: Run the test and verify RED**

Run:

```bash
uv run pytest tests/test_manuscript_claim_integrity.py -q
```

Expected: FAIL because the figure is not included in the manuscript.

- [ ] **Step 3: Add the manuscript figure**

Place a centered figure after the first controlled-comparison paragraph and before the separate six-source context paragraph:

```latex
\begin{center}
    \includegraphics[width=0.96\linewidth,height=0.42\textheight,keepaspectratio]{figures/mea_controlled_pressure_comparison.pdf}
    \captionof{figure}{Same-record pressure comparison for the 31 Jou1995 measurements.  Panel (a) compares observed pressure with predictions from the ideal Smith--Missen baseline and the present fixed activity-based ePC-SAFT calculation.  Panel (b) compares their absolute \(\log_{10}(P_{\mathrm{model}}/P_{\mathrm{data}})\) residuals; points below the one-to-one line favor the activity calculation.  The activity treatment reduces the absolute residual for 4 records and increases it for 27 records.}
    \label{fig:controlled-pressure-comparison}
\end{center}
```

- [ ] **Step 4: Build and visually inspect**

Run:

```bash
uv run pytest tests/test_manuscript_claim_integrity.py -q
bash scripts/build_manuscript.sh
```

Expected: tests PASS, manuscript build PASS, and the figure/caption fit without clipping, illegible labels, or a page containing only a figure and caption.

- [ ] **Step 5: Regenerate twice and prove determinism**

Run the focused renderer twice and compare SHA-256 hashes for the PNG, SVG, PDF, plotted CSV, and sidecar. Expected: all five hashes remain identical.

- [ ] **Step 6: Run final verification**

Run:

```bash
uv run ruff check src scripts analyses tests
uv run pytest -q
uv run python scripts/render_all_plots.py
uv run python scripts/validate_project.py confidence
uv run python scripts/check_epcsaft_integration.py --mode final
bash scripts/build_manuscript.sh
bash "$HOME/.codex/hooks/codex-cleanup.sh" --repo-root .
```

Expected: all commands PASS and cleanup reports no task-owned residue.

- [ ] **Step 7: Commit and update PR #19**

```bash
git add docs/latex/sections/mea_system_modeling_results.tex tests/test_manuscript_claim_integrity.py docs/latex/figures/mea_controlled_pressure_comparison.pdf
git commit -m "docs: add controlled comparison figure"
git push
```

Expected: PR #19 contains the figure addition and its CI checks return successful conclusions.
