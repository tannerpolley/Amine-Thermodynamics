# Prompt: Ingest MEA Roadmap Package, Organize Repo, Then Execute First Tasks

You are working in the `tannerpolley/MEA-Thermodynamics` repository.

The user has attached a ZIP package containing planning files under `repo_overlay/`. Your first job is to organize this package into the repository, avoid duplicates, then proceed with the roadmap tasks.

## 1. Unpack and inspect

Unzip the attached package outside the repository first.

Expected package root:

```text
MEA_roadmap_agent_package/
  README.md
  repo_overlay/
    docs/roadmaps/
    docs/prompts/MEA_ePCSAFT/
    data/reference/MEA/manifests/
```

Inspect all files before copying.

## 2. Copy into the repo carefully

Copy files from:

```text
repo_overlay/
```

into the root of:

```text
tannerpolley/MEA-Thermodynamics/
```

If a target file already exists:

1. Do not blindly overwrite.
2. Compare content.
3. Merge the new structure and preserve any newer repo-specific facts.
4. Keep the strict manuscript structure, figure list, and staged phase logic.

## 3. Do not include paper text

The package intentionally contains planning files only.

Do not paste full article text into roadmap files. Use repo-local Markdown papers under:

```text
docs/papers/md/
```

as extraction sources.

## 4. Core policy

The MEA-Thermodynamics project owns:

- MEA data curation.
- manuscript figures/tables.
- data manifests.
- pressure/speciation/density validation splits.
- scientific interpretation.

The ePC-SAFT package owns:

- generic EOS implementation.
- generic derivative plumbing.
- generic equilibrium solvers.
- generic regression optimizer internals.
- generic TargetRow/TargetDataset schemas.

Do not design or request MEA-specific public APIs in `epcsaft`.

Forbidden package APIs:

```python
fit_mea_absorption(...)
fit_co2_capture_column(...)
fit_lithium_extraction_parameters(...)
screen_lithium_extractants(...)
```

Allowed generic concepts:

```python
ReactionSet(...)
EquilibriumProblem(...)
RegressionProblem(...)
TargetDataset(...)
PhaseSpec(...)
ParameterSet(...)
model.equilibrium(problem)
epcsaft.regress_parameters(problem)
```

## 5. Preserve the manuscript structure

Do not rewrite the manuscript structure. Preserve this spine:

1. Introduction
   1.1 MEA and reactive CO2 absorption
   1.2 Thermodynamic modeling of MEA–CO2–H2O
   1.3 SAFT and PC-SAFT models for alkanolamines
   1.4 ePC-SAFT and advanced Born electrostatics
   1.5 Contribution of this work

2. Theory
   2.1 PC-SAFT residual Helmholtz energy
   2.2 Electrolyte PC-SAFT and ion activity coefficients
   2.3 Modified Born term with solvation shell and dielectric saturation
   2.4 MEA–CO2–H2O reaction network
   2.5 Phase-equilibrium conditions and reference states

3. Data and Methods
   3.1 Experimental data inventory
   3.2 Species basis and parameter hierarchy
   3.3 Pure-component and binary parameters
   3.4 MEAH+ and MEACOO- regression
   3.5 Coupled pressure/speciation objective
   3.6 Computational implementation and reproducibility

4. Results and Discussion
   4.1 Neutral baseline validation
   4.2 Full ionic parameter set
   4.3 MEAH+/MEACOO- regression results
   4.4 Chemical speciation
   4.5 CO2 partial pressure
   4.6 Sensitivity and identifiability
   4.7 Comparison with literature models
   4.8 Model limitations and transferability

5. Conclusions

6. Data and Code Availability

Supplementary Information:
S1 Full data manifest; S2 Parameter source audit; S3 Additional figures; S4 Regression diagnostics; S5 Solver settings and validation tests.

## 6. Preserve the main figure plan

Keep these figures as the target plan:

1. Literature/modeling roadmap.
2. Reactive species and model architecture.
3. Modified Born SSM+DS schematic.
4. Data map over temperature, loading, pressure, and MEA weight fraction.
5. Pure MEA vapor pressure and saturated liquid density.
6. Binary neutral validation for MEA–H2O and CO2–H2O.
7. MEAH+/MEACOO- parameter regression movement.
8. MEAH+/MEACOO- speciation parity.
9. MEAH+/MEACOO- loading curves.
10. Full chemical speciation vs CO2 loading.
11. CO2 partial pressure vs loading.
12. CO2 pressure parity.
13. Residuals by loading, temperature, and source.
14. Sensitivity/identifiability.
15. Literature-model comparison.

## 7. Updated data status

Treat these as repo-local or expected repo-local extraction tasks:

- Wong 2015 Raman high-pressure MEA speciation: expected under `docs/papers/md`.
- Amundsen 2009 CO2-loaded MEA density/viscosity: expected under `docs/papers/md`.
- MEA–H2O dielectric constants: extract from existing attached/repo-local literature or cited leads.

Treat these as source-pending placeholders until the user provides/approves sources:

- Loaded-MEA pH or electrochemical data.
- Direct MEAH+ salt or carbamate salt osmotic/activity data.

Do not fabricate data.

## 8. Required repo-local searches

Run these before creating extraction tasks:

```powershell
rg -n -i "Wong|Raman|protonated MEA|carbamate|bicarbonate|carbonate|molecular CO2|30 wt|60 bar" docs/papers/md data/reference/MEA
rg -n -i "Amundsen|density|viscosity|loaded MEA|CO2-loaded|aqueous MEA" docs/papers/md data/reference/MEA
rg -n -i "dielectric|relative permittivity|permittivity|MEA water|monoethanolamine water|Hsieh|Floriano|Nascimento" docs/papers/md data/reference/MEA
rg -n -i "pH|electrochemical|electrode|potentiometric|loaded MEA|CO2-loaded MEA" docs/papers/md data/reference/MEA
rg -n -i "osmotic|activity coefficient|mean ionic activity|MEAH|ethanolammonium|carbamate salt|MEA carbamate" docs/papers/md data/reference/MEA
```

If Wong/Amundsen files are not found, note that the user stated they have been added or will be added under `docs/papers/md`; leave extraction tasks ready.

## 9. Execute the first six tasks

After organizing the package, start the six tasks listed in:

```text
docs/prompts/MEA_ePCSAFT/FIRST_SIX_EXECUTION_STEPS.md
```

Make the smallest PR-ready changes. Do not start broad code rewrites.

## 10. Required output

At the end of the agent run, report:

1. Files created/updated.
2. Files from package merged or skipped.
3. Current ePC-SAFT dependency status.
4. Phase 1/2/3 acceptance gate status.
5. Data status:
   - Wong 2015
   - Amundsen 2009
   - MEA–H2O dielectric constants
   - loaded-MEA pH/electrochemical data
   - direct MEAH+ salt/carbamate salt osmotic-activity data
6. Exact next commands.
7. Blockers that belong in `ePC-SAFT`, not `MEA-Thermodynamics`.
