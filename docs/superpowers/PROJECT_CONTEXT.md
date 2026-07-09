# MEA-Thermodynamics Superpowers Project Context

## Durable Intent

MEA-Thermodynamics is the downstream evidence, validation, and manuscript repository for monoethanolamine (MEA) thermodynamics work that depends on the upstream `ePC-SAFT` package. The repo owns curated experimental data, target construction, analysis artifacts, plotted evidence, validation gates, and manuscript-ready language. Upstream `ePC-SAFT` owns package-level thermodynamic and regression capabilities.

This setup keeps issue work tied to reproducible artifacts: analysis data, plot bundles, validation checks, and manuscript sections must remain traceable to their source folders.

## Artifact Model

Canonical Superpowers Project artifacts live in flat roots:

- Specs: `docs/superpowers/specs`
- Plans: `docs/superpowers/plans`
- Issue mirrors: `docs/superpowers/issues`
- Milestone index pages: `docs/superpowers/milestones`

Milestone pages are roadmap views only. Specs, plans, and issue mirrors stay in their canonical roots and link back to the milestone pages when needed.

Analysis and manuscript artifacts stay in their existing project locations:

- Paper validation: `analyses/paper_validation/2015_baygi`
- Phase 1 baselines: `analyses/phase1`
- Phase 2 activity ePC-SAFT: `analyses/phase2/activity_epcsaft`
- Phase 3 ionic ePC-SAFT regression: `analyses/phase3/ionic_epcsaft_regression`
- Manuscript source and figures: `docs/latex`

## Roadmap And Milestones

GitHub milestones and local milestone pages use the same titles:

- Project Infrastructure
- Paper Validation
- Phase 1 Baselines
- Phase 2 Activity ePC-SAFT
- Phase 3 Ionic Regression
- Manuscript Submission

The milestone index is `docs/superpowers/milestones/README.md`.

## GitHub Tracker Config

- Repository: `tannerpolley/MEA-Thermodynamics`
- GitHub milestone titles: `Project Infrastructure`, `Paper Validation`, `Phase 1 Baselines`, `Phase 2 Activity ePC-SAFT`, `Phase 3 Ionic Regression`, `Manuscript Submission`
- Issue mirror path: `docs/superpowers/issues`
- Source spec path: `docs/superpowers/specs`
- Source plan path: `docs/superpowers/plans`
- Recommended issue labels: `superpowers:spec`, `superpowers:plan`, `superpowers:issue`, `status:ready`, `status:hitl`, `status:blocked`, `type:analysis`, `type:manuscript`, `type:infrastructure`, `phase:paper-validation`, `phase:phase-1`, `phase:phase-2`, `phase:phase-3`
- Optional hierarchy labels: `parent`, `child`, `blocked`, `needs-upstream`, `needs-user-decision`

AFK/HITL policy:

- Agents may edit specs, plans, issue mirrors, analysis code, analysis docs, validation scripts, and manuscript drafts when the task scope is explicit.
- User review is required before final manuscript submission, external package pin changes for final results, issue deletion, milestone deletion, broad branch merges, or any claim that upgrades scientific status beyond the validated artifacts.
- GitHub Project board creation or mutation requires a separate native confirmation step.

## Execution Model

Issue work is assignable to an agent when all of the following are true:

- The issue has a GitHub milestone.
- The issue links to either a spec, plan, or enough acceptance criteria for a bounded implementation.
- The expected validation command is named, usually `uv run python scripts/validate_project.py quick` for routine changes or `uv run python scripts/validate_project.py confidence` for release/manuscript gates.
- The work can be completed without changing scientific claims unless the issue explicitly includes that review gate.

For multi-turn issue execution, start a `/goal` with a concrete objective, keep one plan item in progress at a time, and mark the goal complete only after implementation, validation, cleanup, and status reporting are finished.

## Extension Skills

Agents should discover this workflow through these skills:

- `$superpowers-project:setup-project`
- `$superpowers-project:brainstorm-spec`
- `$superpowers-project:write-plan`
- `$superpowers-project:create-issues`
- `$superpowers-project:orchestrate-issues`
- `$superpowers-project:resolve-issue`
- `$superpowers-project:merge-changes`

Use `matplotlib-plotting` and `mplgallery-svg-artifacts` for Matplotlib plot bundles and MPLGallery-discoverable SVG artifacts. Use `article-writer-latex-submission` and the repo LaTeX policy for manuscript edits.

## Current Open Questions

- Whether GitHub Project board automation should be added after the milestone setup.
- Whether each milestone should receive a starter spec or plan immediately, or only when issue work begins.
- Whether Phase 3 completion should remain one milestone or split later into native-package integration and final scientific promotion gates.
