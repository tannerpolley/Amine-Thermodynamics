# Reactive Speciation Feasibility Implementation Plan

> Execute in place on a `codex/` branch. Preserve the frozen readiness identities and keep all production regression gates closed.

**Goal:** Test the smallest scientifically defensible MEA-owned reactive-state solver over clean-provider activity evaluations and compare it with pinned `epcsaft` 1.5.2.

**Architecture:** A focused solver consumes an `ActivityEvaluator` protocol. Provider-specific construction and convention checks remain in the experiment adapter. The analysis runner writes a provenance-rich receipt and never promotes results.

---

## Task 1: Specify the solver boundary test-first

- [x] Add focused tests for a nine-species activity evaluator, eight residuals, positive normalized compositions, and deterministic evaluation accounting.
- [x] Prove the generic solver reproduces the Phase 1 ideal solution when supplied `log(activity) = log(x)`.
- [x] Implement the minimal solver/result types in a new focused module.

## Task 2: Construct the clean-provider MEA fixture

- [x] Map the Phase 2 pure, pair, charge, dielectric, Born, and association records into the clean provider's public bundle schema.
- [x] Mark the bundle `package-test-fixture`, record every source SHA-256, and reject missing species or parameter families.
- [x] Build/install the clean provider as an immutable wheel for the experiment and record its Git and wheel identities.

## Task 3: Establish the activity convention and solve

- [x] Compare clean-provider residual chemical potentials and fugacity outputs against the pinned 1.5.2 state at one fixed composition.
- [x] Accept only a documented mapping to the reaction catalog's mole-fraction activity convention; otherwise emit a blocked receipt.
- [x] Use Phase 1 seeds to solve the fixed 313.15 K, 30 wt% MEA states at loadings 0.20, 0.40, and 0.60.

## Task 4: Compare with the pinned lane

- [x] Record all nine composition differences for every state.
- [x] Record all five reaction residuals and three balance residuals for both lanes.
- [x] Keep solver, numerical, physical, and provider-contract acceptance distinct.

## Task 5: Perturb seeds and measure cost

- [x] Repeat each state from deterministic positive log-space perturbations.
- [x] Record convergence, maximum solution spread, provider evaluation count, and elapsed time.
- [x] Write a JSON receipt whose conclusion is `feasible` or `blocked`, never an execution-admission or promotion claim.

## Verification and publication

- [x] Run the focused tests in red-green order, then relevant regression and integration contract tests.
- [x] Run Ruff, the full test suite when practical, and the final ePC-SAFT integration check.
- [x] Verify readiness hashes remain unchanged and `upstream_execution_admitted` remains false.
- [x] Run the repository cleanup audit.
- [ ] Commit, push, open a pull request, and merge only after local and hosted checks pass.
