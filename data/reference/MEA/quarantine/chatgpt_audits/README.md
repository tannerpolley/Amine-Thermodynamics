# Quarantined ChatGPT audit artifacts

These directories contain the exact extracted contents of two ChatGPT Pro audit ZIP files supplied on 2026-07-23. They are preserved as acquisition leads and audit history, not as admitted experimental data.

Neither archive includes all exact primary-source files cited by its reports. Audit A explicitly marks all 608 rows source-incomplete. Audit B asserts stronger closure, but its supplied artifacts include empty five-byte row files, unavailable `/mnt/data` source paths, and claims that conflict with Audit A. The repository therefore assigns every artifact in both directories `regression_admission=prohibited`.

- `audit_2026-07-23_a/`: exact contents of `mea_epcsaft_audit_bundle.zip`
- `audit_2026-07-23_b/`: exact contents below the archive's `MEA_thermodynamics_data_audit/` directory
- `archive_receipts.csv`: immutable archive hashes and bounded package-level findings
- `audit_conflicts.csv`: conflicts that must be resolved from primary-source bytes before promotion

Promotion requires a separate reviewed acquisition: obtain the exact primary file, hash it, verify the locator and transcription independently, preserve the reported basis and measurement role, and pass the normal admission contracts. Do not edit files inside either audit directory; add repository-owned interpretation beside them.
