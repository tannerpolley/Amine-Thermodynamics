# Replay input identity

`parameters.json`, `state-packet.json`, and the retained Engine wheel are the
exact, hashed inputs for this diagnostic replay. The generator verifies all
three before calculation.

The Born--permittivity formulation study used the retained candidate wheel at
`engine-candidates/406cd4e/epcsaft-0.2.0.dev0-cp313-cp313-linux_x86_64.whl`
(SHA-256
`529051a41e5fe2e3a8f944500d1fc2ddf4deaf57cc54f151d1d68d13b6f67a4a`).
Its Engine commit `406cd4e942a1e96260debafdc23c4b8baf7c6226` is the verified
Lagrangian-Hessian acceleration at `fb02e6d` plus the two linear component
permittivity rules required for the B and C comparisons. It does not replace
the pinned wheel used by the active parameter-bundle handoff.

The parameter document is retained byte-for-byte. Its
`data/reference/epcsaft_datasets/MEA_CO2_H2O_phase2/...` locator strings are
archival provenance labels paired with source hashes from the upstream packet;
the deleted paths are not live local parameter authorities and do not imply a
compatibility route. Parameter authority for this replay is the exact document
hash recorded by the generator and the evidence discussed in the notebook.

Continuation states embedded in `state-packet.json` are warm-start evidence
only. The generator converts their liquid compositions and volume to a finite
phase start, clears the continuation identity and state, and then solves with
the separately hashed notebook parameter document.
