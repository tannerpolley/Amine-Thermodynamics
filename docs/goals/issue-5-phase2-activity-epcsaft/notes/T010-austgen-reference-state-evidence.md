# T010 Austgen Reference-State Evidence

## Source

- PDF: `local Zotero Austgen PDF outside this repo`
- Extracted markdown: `external Austgen source outside this repo`

## Verified Claims

- Austgen uses pure-liquid standard states for water and alkanolamine solvents.
- Ionic and molecular solutes use ideal infinitely dilute aqueous solution reference states.
- The article defines an unsymmetric activity-coefficient convention and uses `K = product((x_i gamma_i)^nu_i)` for reaction constants.
- Table V states equilibrium constants are mole-fraction based and gives the R1-R5 coefficients used by the Phase 2 manifest.
- The protonated amine dissociation constants are corrected to the pure amine reference state.

## Implementation Consequence

The Phase 2 reaction constants are now promoted as source-verified thermodynamic-activity fixed inputs. Equilibrium rows and figures remain blocked by the pinned upstream ePC-SAFT package, which raises `backend_unavailable` for activity-coupled chemical-equilibrium solves. The package blocker maps to upstream issue #115.
