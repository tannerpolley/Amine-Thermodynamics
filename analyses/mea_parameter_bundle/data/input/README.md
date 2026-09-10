# Replay input identity

`parameters.json`, the compact `state-packet.json`, and the retained Engine wheel are the
exact, hashed inputs for this diagnostic replay. The generator verifies all
three before calculation.

The Born--permittivity formulation study used the retained candidate wheel at
`engine-candidates/d8e02e4/epcsaft-0.2.0.dev0-cp313-cp313-linux_x86_64.whl`
(SHA-256
`2a95e27415b948149d69f92870a8ea0bbaca2ff9e32d39b9bc938ec0a77b46dd`).
Its Engine commit `d8e02e4c6aab99669d17123248a1ac9729b47213` is the verified
candidate used for the historical comparison. It does not replace
the pinned wheel used by the active parameter-bundle handoff.

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
