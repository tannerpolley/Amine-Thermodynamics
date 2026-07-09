# Linux Workflow Migration Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Make MEA-Thermodynamics runnable from a Debian/Zorin Bash environment without Windows-only workflow entrypoints or documentation.

**Architecture:** Replace the Robocopy-backed manuscript projection with a strict Bash/rsync projection script. Normalize active commands, paths, runtime guidance, and development-container configuration around `uv`, POSIX paths, and the repository's existing Python entrypoints. Preserve scientific source material while removing obsolete platform workflow references.

**Tech Stack:** Bash, rsync, uv, Python 3.13, unittest, LaTeX/latexmk.

## Global Constraints

- Target Debian-family Linux and Bash only.
- Keep `docs/latex` as the manuscript source of truth.
- Keep generated solver output and user changes outside the migration scope.
- `uv` remains the documented Python workflow.

---

### Task 1: Establish a Linux workflow contract

**Files:**
- Create: `tests/test_linux_workflow_portability.py`

- [x] **Step 1: Add a test that rejects Windows command entrypoints in active workflow documentation.**
- [x] **Step 2: Run `uv run python -m unittest tests.test_linux_workflow_portability -v` and confirm it fails before the migration.**

### Task 2: Replace manuscript mirroring with Bash

**Files:**
- Delete: obsolete Windows manuscript sync script
- Create: `docs/latex/scripts/sync_to_overleaf_mirror.sh`

- [x] **Step 1: Implement strict source-to-mirror projection with `rsync`, `--dry-run`, and explicit mirror validation.**
- [x] **Step 2: Run `bash -n docs/latex/scripts/sync_to_overleaf_mirror.sh`.**

### Task 3: Normalize project workflow surfaces

**Files:**
- Modify: `README.md`, `HANDOFF.md`, active analysis README files, `docs/ePC-SAFT/*.md`, `docs/coordination/*.md`, and `docs/superpowers/**/*.md`
- Modify: `src/MEA/epcsaft_runtime.py`, `src/MEA/six_species/plot_pressure.py`, and affected rendering guidance
- Modify: `.devcontainer/devcontainer.json`

- [x] **Step 1: Change documented commands to Bash code fences and POSIX paths.**
- [x] **Step 2: Remove Windows-specific runtime instructions and the stale Streamlit devcontainer lifecycle.**
- [x] **Step 3: Run the portability test and targeted compile checks.**

### Task 4: Validate the migration

**Files:**
- Modify: `docs/.codex-journal/project_memory.md`

- [x] **Step 1: Run `uv run python scripts/validate_project.py quick`.**
- [x] **Step 2: Run `bash "$HOME/.codex/hooks/codex-cleanup.sh" --repo-root .`.**
- [x] **Step 3: Record the Linux workflow as a durable project fact.**
