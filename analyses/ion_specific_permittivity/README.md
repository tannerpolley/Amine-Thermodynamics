# Ion-specific suppression probe (#394)

This exploratory analysis changes no adopted parameter, Engine pin, observation
role, manuscript or analysis-site membership. It tests the composed Engine law
on the adopted F2 Part I record. The question and authorized coefficient fit
are [issue #394](https://github.com/tannerpolley/Amine-Thermodynamics/issues/394).

- [Notebook](notebook.qmd): results, conditions, uncertainty and limitations.
- [Source assessment](sources.md): table verification, frequency band and the
  reason for the symmetric exploratory coefficient interval.
- `results/build.json`: merged Engine commit, wheel SHA-256, build command,
  original Part I input hashes and branch base.
- `results/identity.json` and `results/replay.json`: #388 declaration identity
  and all 307 Part I observations.
- `results/fit.json`, `fit-information.json`, `fitted-parameters.json` and
  `fitted-observations.json`: one three-core fit and independent replay.
- `results/derivative-timing.json`, `runtime-estimate.json` and `profile.txt`:
  the pre-fit workload measurement and conservative estimate.

## Reproduce

Use Python 3.13 and the wheel identified in `results/build.json`, installed
only in `build/ion-specific-probe/venv` with NumPy, SciPy and Matplotlib. The
wheel is an unrepaired local Linux build and needs the local numerical shared
libraries; it is not a portable release. No Engine source is imported.
From the repository root, run each calculation in a background shell:

```bash
agent-heavy build/ion-specific-probe/venv/bin/python -u analyses/ion_specific_permittivity/calculate.py replay
agent-heavy build/ion-specific-probe/venv/bin/python -u analyses/ion_specific_permittivity/time_fit.py
agent-heavy build/ion-specific-probe/venv/bin/python -u analyses/ion_specific_permittivity/fit.py
agent-heavy build/ion-specific-probe/venv/bin/python -u analyses/ion_specific_permittivity/reduce_fit.py
agent-heavy build/ion-specific-probe/venv/bin/python -u analyses/ion_specific_permittivity/calculate.py trend
agent-heavy build/ion-specific-probe/venv/bin/python -u analyses/ion_specific_permittivity/assess.py
agent-heavy build/ion-specific-probe/venv/bin/python -u analyses/ion_specific_permittivity/assess.py full
agent-heavy build/ion-specific-probe/venv/bin/python analyses/ion_specific_permittivity/present.py
```

The runtime estimate precedes the fit. It uses one measured complete 307-row
exact-derivative evaluation, plus two measured residual evaluations per allowed
iteration, without a parallel speedup assumption. This is a conservative
one-run estimate, not a performance comparison. `assess.py` reuses the existing
Part I grid and census producers, replaces their historical parameter binding
with this probe's F2 mapping, and verifies this explicitly authorized wheel
instead of their historical import-time pin. Its changes exist only in the
probe process. It writes only within this analysis folder.

The notebook is rendered standalone because the owner explicitly prohibited
changes to `analyses/_cse-manuscript.json`. It is not registered in the analysis
site and is not promoted for manuscript use.
