# Replay input identity

`parameters.json`, the compact `state-packet.json`, and the retained Engine wheel are the
exact, hashed inputs for this diagnostic replay. The generator verifies all
three before calculation.

The active parameter-bundle handoff uses the pinned wheel under `engine/`;
historical comparison receipts retain their original Engine commit and hash.

The parameter document is retained byte-for-byte. Its
`data/reference/epcsaft_datasets/MEA_CO2_H2O_phase2/...` locator strings are
archival provenance labels paired with source hashes from the upstream packet;
the deleted paths are not live local parameter authorities and do not imply a
compatibility route. Parameter authority for this replay is the exact document
hash recorded by the generator and the evidence discussed in the notebook.

Continuation states expanded from compact `state-packet.json` are warm-start evidence
only. The generator converts their liquid compositions and volume to a finite
phase start, clears the continuation identity and state, and then solves with
the separately hashed notebook parameter document.
