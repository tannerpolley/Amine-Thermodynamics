# Local Codex Instructions

Repository Profile: scientific-computing

## Startup Reads

- Read `docs/.codex-journal/user_preferences.md` when it exists.
- Read `docs/.codex-journal/project_memory.md` when it exists.

## Memory Policy

- Keep user preferences and durable project facts concise, date-stamped, and deduplicated.
- Do not update memory for routine Q&A or small one-off work.
- Do not store secrets, add placeholder entries, or create new memory under `.codex` or `$HOME/.codex/projects`.

## ePC-SAFT Cross-Repo Integration

- This is an official downstream application under ePC-SAFT Governance D-037.
- Engine governance lives at `/home/tnnrpolley21/Workspaces/Engineering/ePC-SAFT-project/governance`; the generic runtime lives in that repository's `engine/` directory.
- The Unified Engine is one `epcsaft` wheel with `epcsaft`, `epcsaft.equilibrium`, and `epcsaft.regression`. Do not install split packages or use compatibility imports.
- Prefer uv-managed workflows. Use `.venv/bin/python` only for interpreter-specific debugging or repo-local troubleshooting.
- Normal and final work uses one immutable Engine wheel and SHA-256 hash. Local co-development may use an explicitly supplied candidate wheel; never import an Engine source checkout.
- Keep MEA chemistry hypotheses, source data, model selection, regression, validation, parameter adoption, figures, and the thermodynamics manuscript in this repository.
- Keep Engine equations, generic equilibrium compilation, exact derivatives, and generic regression mechanics in ePC-SAFT-project. Do not create nested repositories, submodules, or sibling-source runtime imports.
- Reusable scientific packets are materialized from Data by exact commit, packet path/version, fingerprint, and file hashes. Do not discover sibling repositories at runtime.
- Keep Engine interactions behind the approved runtime and diagnostic modules. Unsupported scientific capabilities must fail explicitly; do not restore old APIs or local equation copies.

## Engineering Methods And Issue Tracking

- Read `docs/agents/methods.md` before using Matt engineering methods or Project Truss.
- GitHub Issues are the authoritative tracker; follow `docs/agents/issue-tracker.md`.
