# Start scientific work here

Read `docs/scientific/CONTEXT.md` in this directory first. Its established-work table connects the
estimation strategy, source audits, measurement inventories and completed
studies to their existing records, followed by the unresolved questions.
Use the installed CSE skill appropriate to that question.

The [scientific plan](PREDICTIVE_MEA_PROGRAM.md) owns estimation and assessment
requirements. The [document index](DOCUMENT_AUTHORITY_INDEX.md) identifies
other record owners. The [working notebook](../../analyses/mea_parameter_bundle/notebook.qmd)
presents retained bundle results; the [September audit](REPOSITORY_AUDIT_2026-09-08.md)
records known discrepancies. The [evidence map](../../analyses/evidence-map.qmd)
traces sources to retained data and results and lists the query commands.
For sources and retained data, start with the registered Zotero Companion
project `mea-thermodynamics`:

```bash
cse-zotero wiki-context mea-thermodynamics --query "<terms>" --json
cse-zotero wiki-evidence <ZOTERO_KEY> --query "<terms>" --json
```

Use `wiki-context --global --query "<terms>" --json` when the project view has
no match. Read exact source passages and check their hashes before making a
scientific claim. The project page and paper briefs provide navigation;
the source passages and retained numerical results support claims. Full-paper
reading copies remain in the ignored [literature shelf](../../literature/README.md),
with source identities in its index.

A new agent should report what is established, which result supports it, and
what remains unresolved before proposing further research. Continue existing
records; create another study only for a distinct unanswered question.
