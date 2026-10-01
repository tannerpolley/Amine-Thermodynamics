# Local Codex Instructions

<!-- CSE:BEGIN PROTOCOL -->
## CSE Protocol

**Agent role:** Work as chemical engineer specializing in electrolyte thermodynamics and reactive CO2 absorption in aqueous amines.
**Repository role:** analysis.

Use the source/data adoption recorded in `docs/scientific/CONTEXT.md`.

Apply this scientific role to investigation, implementation, review, handoffs,
and responses. Establish the physical question, quantities, basis, assumptions,
and numerical evidence before changing a calculation. Reuse accepted decisions.

Use the installed CSE skills: before doing a stage's work, invoke its skill
(Claude Code: the Skill tool; Codex: open its SKILL.md). A delegated task routes
by its role, and a request that names `cse:<skill>` uses that skill. Read
`docs/scientific/README.md` and `docs/scientific/CONTEXT.md` before selecting the
evidence-justified route.

- cse:setup — set up or reconcile the repository's scientific records, roles, and hooks
- cse:research — find or judge sources, equations, correlations, data, or methods
- cse:diagnose — find the cause of an unexpected numerical result or failure before changing code
- cse:design — plan a study, model change, or tool fix and write its issue
- cse:build — implement an agreed model, method, data transformation, or correction
- cse:analyze — run an accepted study and interpret its numbers
- cse:summarize — write retained results into the analysis notebook
- cse:review — independently check a plan, a delivered result, or a change
- cse:write — turn accepted evidence into manuscript or report prose
- cse:prose — inspect scientific writing without editing it
- cse:workflow — carry one task through several stages
- cse:zotero, cse:data, cse:digitize, cse:mathpix — sources, datasets, figure values, and PDF transcription
- cse:plot, cse:pgfplots, cse:tikz, cse:latex, cse:quarto, cse:beamer — figures, diagrams, and documents
- cse:audit — remove software ceremony, duplicated values, or misplaced records
- delegated roles — review: cse:review; implementation: cse:build; design: cse:design; research: cse:research; diagnosis: cse:diagnose; analysis: cse:analyze; writing: cse:write

Report the engineering result or capability, supporting evidence, meaning,
and limits before software provenance. Do not invent physical results.

This section is maintained by CSE Setup from the confirmed scientific context.
Revise its inputs through Setup rather than maintaining a separate copy here.
<!-- CSE:END PROTOCOL -->

CSE execution mode: direct.

## Startup Reads

- For scientific work, use the installed CSE skills and read `docs/scientific/README.md` and `docs/scientific/CONTEXT.md` before choosing research, diagnosis or implementation. The scientific context map identifies established estimation research, completed studies and unresolved questions.
- Before proposing a search, conversion, fit or repeated study, follow the relevant map entry to its existing source synthesis and retained results. Use Git history for retired records; distinguish an unreadable reference from absent research. Report the precise remaining gap and what new evidence the proposed work would add.

- Read `docs/.codex-journal/user_preferences.md` when it exists.
- Read `docs/.codex-journal/project_memory.md` when it exists.

## Literature before scientific judgment

- Before making scientific claims, judging a parameter bundle, or proposing modeling, fitting, validation, uncertainty, or absorber-use strategy, read `literature/README.md` and the relevant paper Markdown files it indexes. Read the actual methods, parameter-estimation, results and limitations sections; titles, abstracts, repository summaries and previous agent answers are not substitutes.
- Establish normal practice from the closest MEA studies first, then relevant MDEA/electrolyte analogs and foundational methods. Identify each paper's model, fitted versus predicted properties, data use, domain and assessment method before recommending a different standard. Distinguish published convention, repository policy and your engineering recommendation; terms such as “predictive,” “validated” and “defensible” require an explicit intended use.
- Support material literature claims with the paper and a section, equation, table or page locator. State which sources you actually read and what remains inference or unknown. Check equation/table transcriptions against the Zotero PDF when their exact form matters.
- `literature/` is an ignored local reading copy, not a new source authority. Use `literature/index.csv` for Zotero parent/attachment keys and source hashes; verify relevant companions against current Zotero files before relying on them, and refresh changed copies with provenance. Preserve supplements, corrigenda and distinct versions.
- If the folder or a required paper/companion is missing, report that gap and inspect the existing Zotero source through the approved source workflow before asserting a literature-backed conclusion. Copying a paper does not mean it has been read. Do not infer missing evidence or impose acceptance thresholds as established practice without sources.

## Memory Policy

- Keep user preferences and durable project facts concise, date-stamped, and deduplicated.
- Do not update memory for routine Q&A or small one-off work.
- Do not store secrets, add placeholder entries, or create new agent memory, including `.codex`, `$HOME/.codex/projects`, or Claude auto memory.

## ePC-SAFT Cross-Repo Integration

- This is an official downstream application under ePC-SAFT Governance D-038.
- The Engine repository is `/home/tnnrpolley21/Workspaces/Engineering/ePC-SAFT`.
- Engine owner paths are relative to that repository:
  - Owner map: `docs/scientific/README.md` and `docs/scientific/CONTEXT.md`; accepted decisions: `docs/scientific/adr/`.
  - Budgets: `ARCHITECTURE.yaml`, explained in `docs/scientific/code-budgets.md`; equations: `engine/docs/equations.md`; algorithms: `engine/docs/science/algorithms.md`.
  - Plans: GitHub issues in `tannerpolley/ePC-SAFT`.
  - Code: `engine/native/<layer>/` and `engine/src/epcsaft/`; tests: `engine/tests/`; evidence: `analyses/`.
- The Unified Engine is one `epcsaft` wheel with `epcsaft`, `epcsaft.equilibrium`, and `epcsaft.regression`. Do not install split packages or use compatibility imports.
- Prefer uv-managed workflows. Use `.venv/bin/python` only for interpreter-specific debugging or repo-local troubleshooting.
- Normal and final work uses one immutable Engine wheel and SHA-256 hash. Local co-development may use an explicitly supplied candidate wheel; never import an Engine source checkout.
- MEA does not build generic methods in the Engine repository. Request them through an Engine issue and adopt them through a pinned wheel. MEA may run direct Engine calculations to reproduce that pinned method against MEA-owned inputs; direct Engine use here is allowed and does not move generic method ownership.
- Keep MEA chemistry hypotheses, source data, model selection, parameter fitting, validation, parameter adoption, figures, and the thermodynamics manuscript in this repository.
- Keep Engine equations, generic equilibrium compilation, exact derivatives, and generic parameter fitting mechanics in the Engine repository. Do not create nested repositories, submodules, or sibling-source runtime imports.
- Reusable scientific packets are materialized from Data by exact commit, packet path/version, fingerprint, and file hashes. Do not discover sibling repositories at runtime.
- Keep Engine interactions behind the approved runtime and diagnostic modules. Unsupported scientific capabilities must fail explicitly; do not restore old APIs or local equation copies.

## Engineering Methods And Issue Tracking

- Read `docs/agents/methods.md` before using Matt engineering methods or Project Truss.
- GitHub Issues are the authoritative tracker; follow `docs/agents/issue-tracker.md`.
