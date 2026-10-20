# Replay input identity

`parameters.json`, the compact `state-packet.json.gz`, and the retained Engine wheel are the
exact, hashed inputs for this diagnostic replay. The generator verifies all
three before calculation.

The active parameter-bundle handoff uses the relative wheel pin in
`pyproject.toml`; historical comparisons retain their original Engine identities.
`parameters.json` is now version 2, SHA-256
`2a03b675aebdccb854c27857e95f493a1aea1436f7d2e236630bd621d9d82f05`. Only the document version and explicit
CO2/MEA no-cross-association declaration changed in #191. This keeps the model
without claiming the physical interaction is absent. Both wheels in the
[adoption comparison](../../results/engine-21e761c3-adoption/README.md) and wheel
8298c602 ([its adoption](../../results/engine-8298c602-adoption/README.md)) refuse
this source snapshot because `model/electrolyte/ionic_dispersion` is missing;
no new physical choice was inserted.

Before version 2, JSON whitespace and key order were compacted without
changing the parameter mapping, to satisfy the repository size limit. Its
`data/reference/epcsaft_datasets/MEA_CO2_H2O_phase2/...` locator strings are
archival provenance labels paired with source hashes from the upstream packet;
the deleted paths are not live local parameter authorities and do not imply a
compatibility route. Parameter authority for this replay is the exact document
hash recorded by the generator and the evidence discussed in the notebook.

Continuation states expanded from compact `state-packet.json.gz` are warm-start evidence
only. The generator converts their liquid compositions and volume to a finite
phase start, clears the continuation identity and state, and then solves with
the separately hashed notebook parameter document.
