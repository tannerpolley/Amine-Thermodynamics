# Reactive Speciation Feasibility

This bounded experiment tests an MEA-owned, charge-balanced reactive-state solver over public clean-provider EOS evaluations. It compares three fixed states with the immutable `epcsaft` 1.5.2 lane and measures repeat-seed behavior.

The output is diagnostic evidence only. It cannot admit upstream regression execution, promote parameters, or replace the repository's final ePC-SAFT integration lane.

Run the pinned lane first, then run the clean lane from an isolated environment containing an immutable clean-provider wheel:

```bash
uv run python analyses/phase3/reactive_speciation_feasibility/scripts/run_experiment.py --lane pinned
PYTHONPATH=/path/to/clean/provider/site-packages:src \
  CLEAN_PROVIDER_WHEEL=/path/to/epcsaft.whl \
  uv run --no-sync python analyses/phase3/reactive_speciation_feasibility/scripts/run_experiment.py --lane clean
```

The clean run writes `results/reactive_speciation_feasibility_receipt.json`.
