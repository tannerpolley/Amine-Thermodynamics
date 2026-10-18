# Route 2 wall-limit diagnosis: interrupted worker CPU is missing

**Class (c): an interrupted-run accounting defect is established; the reason the fit exceeded 300 s is unresolved.** The retained CPU/wall ratio **0.965075789** does not establish one-core execution. The native fit uses separate processes. MEA sends SIGTERM to their owner at 300 s, bypassing the native destructor that normally kills and reaps its workers. The wrapper's `RUSAGE_CHILDREN` includes reaped descendants only. Unreaped worker CPU is therefore absent from the interrupted fit's retained 289.631747 CPU-s. Those CPU values and all derived cumulative totals are lower bounds, not complete aggregate measurements. No fit or thermodynamic solve was repeated for this diagnosis.

## 1. Requested and actual parallelism

- Requested **32** native worker processes, including the fit owner. The constructed `FitControls.workers` is **32**, `maximum_iterations=40`, and `maximum_elapsed_time_seconds=300`.
- Launch CPU count **32**; available memory **20743548928 bytes**. The allowance is **268435456 bytes/worker**; all 32 require **8589934592 bytes**, below available memory. The MEA sizing selected 32. It did not reduce the request to one.
- The exact launcher sets OMP_NUM_THREADS, OPENBLAS_NUM_THREADS and MKL_NUM_THREADS to **1**. These limit numerical-library threads; Engine row workers are separate exec-started processes. Ceres uses one thread within the fit owner.
- The pinned Engine caps worker processes by non-electrolyte state groups, with no MEA state-group cap. There are **47 distinct pressure temperature/feed pairs** before adding species, heat and Cp states. That cap cannot explain a one-process fit.
- A normal Python host without active trace therefore takes the native **32-process** path. The actual process count was not sampled or returned before interruption, so **observed actual worker count is unavailable**. Static source behavior is not a process census. A native host or active trace capture would force one process, but neither is declared by this launch; no active trace is created in the inspected MEA call path.

The worker construction is in Engine `fit.cpp:463-500`; Python executable registration is `regression_bindings.cpp:48-60`; the constructor carries the workers argument at lines 135-145. The MEA fit passes `workers=sizing['workers_requested']`. Source identities and immutable links are in [source-identities.json](source-identities.json).

## 2. Work counts and comparison with the gate

| Quantity | Route 2 interrupted fit | Engine #497 gate |
|---|---:|---:|
| Coordinates | 14 | 7 |
| Fitting rows at lambda=0 | 166 | 149 |
| Positive-density-weight information rows | 178 | 149 |
| Completed optimizer iterations | Not returned | 14 in the frozen full fit |
| Residual/Jacobian evaluations | Not returned | 15/12 in the refrozen full fit |
| Time per fit evaluation | Unavailable | Current-wheel serial residual-plus-Jacobian call about 9.48 CPU-s |
| Reference computations | Unavailable | 296 frozen gate misses |
| Reference columns | Unavailable | 3462 |
| Density solves | Unavailable | 2637 |
| Equilibrium iterations | Unavailable | 1426 |

The current-wheel 9.48 CPU-s / 17.2 full-fit wall-s values are the Engine delivery reported in [#170](https://github.com/tannerpolley/Amine-Thermodynamics/issues/170#issuecomment-6205497286). The [#497](https://github.com/tannerpolley/ePC-SAFT/issues/497) identity file records its earlier refreeze separately: serial CPU 16.279413456, full fits 31.264-31.567 s, the same 149-row/seven-coordinate case and the work counts above. These historical/reference values are not new timing runs.

One **serial point-reader** information call on Route 2's A start used **45.207792000 CPU-s / 45.215482786 wall-s**, including construction and output of its 178-row/14-coordinate Jacobian. That is **4.768754 times** the reported gate serial CPU, but it is a different observation/coordinate set with four equilibrium Cp rows and different starting parameters. It is not a measured time per cached fit evaluation. The source documents that point readers use one process. No fit-work counts or full-parallel completion estimate can be reconstructed from this comparison.

The fit's counters and iteration/cost vectors exist in the returned native `FitResult`; MEA writes them only after `regression.fit` returns. It did not return. The opt-in `EPCSAFT_FIT_CPU_PROFILE` was not enabled by the launcher and no compute profile or trace was retained. An iteration count inferred from 300/9.48 would be unsupported. There is therefore no evidence establishing class (b), an inherently over-300-s fully parallel problem, or class (a), a worker-count/threading configuration failure.

## 3. Returned partial results and accounting falsifier

No partial iterate, endpoint, cost history, residual/Jacobian count or reference-work count was returned. The preserved `incomplete-fit.json` records this absence; the 300.112955133 s wall includes termination/reap overhead. The native owner cleanup is `fit.cpp:414-421`; worker parent-death behavior is `fit.cpp:794-802`. SIGTERM ended the owner with exit code -15 before that normal cleanup.

A bounded **non-scientific process probe** reproduced the missing accounting: its grandchild consumed **0.250933136 CPU-s**, but after terminating the owner, RUSAGE_CHILDREN reported only **0.002133000 CPU-s**. Explicitly reaping the adopted grandchild raised it to **0.253884000 CPU-s**, recovering **0.251751000 CPU-s**. All probe processes were captured by PID and reaped. [accounting-probe.json](accounting-probe.json) retains the numbers. The probe changes no Engine code, model, start, tolerance, bound or budget.

`RLIMIT_CPU=3000` on the wrapper child is also **per process**, inherited separately by spawned workers. It does not enforce a 3000 CPU-s aggregate fit ceiling. Aggregate compliance cannot be certified for this interrupted fit. This is a measurement/control defect, not a physical thermodynamics finding.

For accounting only, 32 discovered CPUs times the measured call span gives a **conservative upper bound 9603.614564256 CPU-s** for the whole fit, compared with the retained lower bound 289.631747. This is not an actual CPU measurement or a fit-time forecast. Up to **9313.982817256 CPU-s** is unrecorded under that bound. The retained budget file now separates lower bounds from this conservative reservation; the original numerical charges remain preserved.

## Disposition

The matched comparison remains stopped. The parent decides any rerun. Before another fit, its launcher needs aggregate process accounting/enforcement and a way to preserve native work/partial-result evidence on interruption. The existing native compute profile is one available observation mechanism; it was not activated here. No worker or timeout change is applied, and no Engine issue is written by this implementor. The diagnosis identifies why the near-one CPU/wall ratio cannot select a slow-fit cause, rather than claiming a one-core defect or an equation-of-state limitation.

The diagnosis is numerical verification of process accounting and read-only inspection of the exact pinned implementation. It is not calibration or physical validation. Its 60 CPU-s / 60 wall-s allowance includes the source fetches, the 0.26 s process probe, metadata-only control check, report and presentation. No extra fit or native thermodynamic solve runs.

## Final diagnosis charges and corrected reservation

Diagnosis charge: **32.497573000 CPU-s / 36.890317390 active wall-s**, within 60/60, including the source reads, process probe, metadata-only control check, static notebook render and conservative 15/15 for report/checks/commit. No native thermodynamic calculation or additional fit was run.

| Quantity | Recorded CPU plus conservative overhead, excluding missing workers | Conservative CPU reservation upper bound | Active wall-s |
|---|---:|---:|---:|
| Route 2 | 555.487189000 | 9869.470006256 | 565.475694846 |
| Cumulative program | 2823.022326720 | 12137.005143976 | at least 1268.240046973 |

The reservation uses only a conservative CPU-count times wall upper bound where aggregate CPU was not measured; it is not a claim of actual consumption. The remaining Route 2 allowance under that reservation is 5130.529993744 CPU-s / 1534.524305154 wall-s. It does not authorize another fit after the existing wall-limit stop. The parent owns any rerun and any repair to aggregate enforcement/retained work evidence.
