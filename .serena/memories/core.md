# MEA-Thermodynamics Core

- Executable scientific argument for reactive aqueous MEA–CO2–H2O thermodynamics.
- Importable model/data/plot support: `src/MEA`; reusable observations and parameter tables: `data/reference`; analysis-owned generated evidence: `analyses/<category>/<analysis_id>`; manuscript: `docs/latex`.
- Preserve scientific traceability: exact units/bases/roles/provenance; keep raw observations distinct from balance-derived context and model outputs.
- EOS/state/property ownership stays in the pinned `epcsaft` dependency. Do not copy EOS logic or bypass fail-closed upstream capability/readiness gates.
- Final manuscript/archive results require immutable-pinned integration success.
- Repository profile is scientific-computing; code-intelligence ceiling is Level 2.
- No repo-local `.worktrees` workflow.
- For environment and dependency pins, read `mem:tech_stack`; for implementation conventions, read `mem:conventions`; for common commands, read `mem:suggested_commands`; for completion evidence, read `mem:task_completion`.
