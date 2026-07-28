# Project Conventions

- Keep model equations, numerical methods, orchestration, and reporting separate.
- Reusable Python code belongs under `src/MEA`; scripts are thin entrypoints; each analysis owns its generated tables and rendered figure bundle.
- Use explicit species identities, units, composition/loading bases, observation roles, provenance keys, hashes, bounds, and tolerances. Never silently convert or relabel evidence.
- Preserve direct measurements, aggregates, reported-zero bounds, balance-derived context, and model-derived values as distinct roles.
- Fail closed when upstream ePC-SAFT capability/readiness is not explicitly admitted; do not add local optimizers, fake defaults, or compatibility shims.
- Scientific tests protect convergence, conservation, tolerances, published/independent benchmarks, and costly recurring failures—not implementation coverage.
- Manuscript prose states scientific provenance and limitations directly; internal tracker phases, receipts, bundles, and repository-history labels do not belong in reader-facing claims.
- Prefer smallest maintainable edits; avoid duplicated analysis ownership and obsolete generated files.
