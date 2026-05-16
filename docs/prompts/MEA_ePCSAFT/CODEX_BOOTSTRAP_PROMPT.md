# Codex Bootstrap Prompt: MEA Manuscript Roadmap Package

You are working in `tannerpolley/MEA-Thermodynamics`.

Start by reading:

1. `docs/prompts/MEA_ePCSAFT/INGEST_ZIP_AND_EXECUTE.md`
2. `docs/roadmaps/mea_manuscript_phase_plan.md`
3. `docs/roadmaps/phase_acceptance_gates.md`
4. `docs/roadmaps/mea_data_curation_plan.md`
5. `docs/roadmaps/epcsaft_dependency_matrix.md`

Then execute the first six steps in:

```text
docs/prompts/MEA_ePCSAFT/FIRST_SIX_EXECUTION_STEPS.md
```

Boundaries:

- Keep the strict manuscript structure.
- Keep the main 15-figure plan.
- Keep the three scientific phases.
- Use repo-local `docs/papers/md` files for extraction.
- Do not fabricate data.
- Do not request MEA-specific public APIs in `epcsaft`.
- Do not overclaim final coupled regression before Phase 3 artifacts exist.

End with a PR-ready summary.
