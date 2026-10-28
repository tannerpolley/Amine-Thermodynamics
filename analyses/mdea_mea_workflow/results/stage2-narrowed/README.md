# Phase-evidence bound narrowing

Neither variant produces an endpoint passing the required phase search within six steps. No narrowed bounds are frozen, no narrowed outside-fit error statistic is evaluated, and no narrowed Ermatchkov verdict or bicarbonate/control follow-up is available. No MDEA outcome falsifies the MEA bicarbonate value.

The owner-approved procedure uses one-change inward probes of active ion bounds, moves one bound by 10% of its original width, and ranks the probes by the least-negative resolved liquid split, breaking ties by unresolved-state count. Decisions use phase evidence only. Each refit starts from its objective-preferred declared start, projected into the changed interval. Fitted data, weights, scales, the linear neutral-water law, Neumann Cp and the 395 K domain remain fixed.

A narrows the cation-water lower limit through -0.4 and -0.3, the Born upper limit to 6.5 angstrom, the water limit to -0.2, then Born to 6.0 and 5.5 angstrom. Its final cost is 463.272605270, with 33 liquid-witness state records and 112 unresolved records. B narrows the cation-bicarbonate upper limit through 0.8, 0.6, 0.4, 0.2, 0 and -0.2. Its final cost is 392.099097184, with 30 liquid-witness state records and 101 unresolved records. Counts include duplicate physical states for distinct observables. The retained exact floating-point bounds own their values.

Each `step-N/` retains probe phase evidence, chosen bounds, full fit declaration, endpoint, fitted objective/group costs, saturation scans, and all fitted/comparison phase records. Each variant's `path.json` owns the ordered path. `coordinates-and-bounds.csv` gives every coordinate and active side at all 12 endpoints; `liquid-witnesses.csv` indexes every resolved liquid trial with its error estimate. No finite no-witness search proves global stability. Unresolved trials and unavailable states are numerical non-results.

Böttinger is evaluated at 5 and 25 bar under the owner's native-question ruling, with per-row pressure missing. Only liquid–liquid witnesses count as liquid instability; vapor witnesses are reported separately. Every available model-saturation state and the capped Merkley 156 kPa endpoint is also searched. All prescribed narrowed saturation scans find a bracket and none has multiple admitted sign changes. The corrected searches replace the explicitly withdrawn atmospheric-pressure phase records. The fitted-state probes and objectives are unchanged by this outside-fit pressure correction. B's second fit was interrupted for that decision and resumed from its last completed step; no interrupted fit supplies an endpoint.

B1's original unlike-ion value is +1 in its physical vector. The earlier notebook prose stating -1 was incorrect. The original active A values are cation–CO2 +0.5, cation–water -0.5, unlike-ion -1 and Born 7 angstrom. B1 originally has unlike-ion +1 and Born 7 angstrom. Final active A values are water -0.2 (lower), unlike-ion -1 (lower), Born 5.5 angstrom (upper); final active B values are unlike-ion -0.2 (upper), Born 7 angstrom (upper).

Run from this worktree root:

```bash
nice -n 10 agent-heavy /home/tnnrpolley21/Workspaces/Engineering/Amine-Thermodynamics/.venv/bin/python -I analyses/mdea_mea_workflow/scripts/stage2.py diagnostic
nice -n 10 agent-heavy /home/tnnrpolley21/Workspaces/Engineering/Amine-Thermodynamics/.venv/bin/python -I analyses/mdea_mea_workflow/scripts/stage2.py narrow
nice -n 10 agent-heavy /home/tnnrpolley21/Workspaces/Engineering/Amine-Thermodynamics/.venv/bin/python -I analyses/mdea_mea_workflow/scripts/stage2.py present
```

`narrow` resumes retained completed steps. `rephase` reruns the fitted/comparison searches at retained endpoints without refitting. Runtime receipts verify Engine 3e83e19c and wheel SHA-256 0d08dff9be39fb8fc9018119c47612f53d823cd0e456914d7dd44c6941596804 against installed files. Pools use all cores permitted by free memory, at 256 MiB per process, with one BLAS thread per process. Saturation scan states are independent jobs under the same worker-count policy, followed by bracket inversion; there is no nested pool.

The one stage-2 runner has 588 lines against the approved 600-line ceiling relative to 799f9f3. It reuses the frozen declarations, native Engine fit/phase methods and existing model modules. No local Engine equation or generic optimizer is added. Endpoint reconstruction was checked against the retained A1/B1 documents. Retained-result checks verify all 16 diagnostic/narrowed endpoint projections preserve the shared component, correlation, pair and topology records, every primary denominator is 88, every Böttinger pressure comparison contains all 58 rows, and each group-cost sum matches its fit cost. These are input/accounting checks, not phase qualification or physical validation. The requested new scans, numerical audit and follow-up remain conditional on a stable endpoint and are therefore not run.

The notebook and its ordinary HTML view are the scientific handoff. All files and rendering stay in this worktree; the main checkout and its preview service are untouched. No subagents, merge or push are used. Independent review remains open.

Presentation: full site refresh stopped because `snakemake` is absent. Direct Quarto HTML rendering of this worktree notebook is used; the main preview service is untouched.

A reference-grid assertion pins the original 324 fitted phase states so that objective omissions cannot silently remove phase queries.

## Stored evidence

Phase-search JSON files larger than 5 MB are stored as `.json.gz` (gzip level 9). `../compressed-evidence.json` lists each raw SHA-256; restore with `gunzip -k <file>.json.gz` before rerunning the summary scripts.
