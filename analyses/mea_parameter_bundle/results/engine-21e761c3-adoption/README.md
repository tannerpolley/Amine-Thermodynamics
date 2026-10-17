# Engine 21e761c3 adoption (#191/#192)

The selected heat F1 record gives **152/152 bitwise-equal predictions** on
Engine 84ca269d without the new declaration and 21e761c3 with it. The worst
relative difference is **0**; the worst absolute difference is zero for every
quantity. [comparison.json](comparison.json) retains every old/new value,
input identity, source-input refusal and comparison definition.

| Quantity | Count | Bitwise equal | Unit |
|---|---:|---:|---|
| CO2 partial pressure | 47 | 47 | Pa |
| Species mole fractions | 94 | 94 | mol/mol |
| Vinjarapu integral heat of absorption | 8 | 8 | J/mol CO2 |
| Equilibrium solution heat capacity | 3 | 3 | kJ/(kg K) |

The first 149 quantities use the existing `base` observation set in
`results/fit-campaign-179-baseline-complete/spec.json` through
`scripts/fit_observations.py:rows_for/replay`, with its unchanged corrected
source packet and warm starts. The other three use
`scripts/heat_evidence_170.py:cp_check/HILLIARD`: 318.15 K at nominal loadings
0 and 0.358, and 353.15 K at 0.358 mol CO2/mol MEA. The existing nominally
unloaded proxy is 0.00001. This is numerical verification for these quantities
and this record; it adds no physical validation, parameter fit, uncertainty
estimate or process-use qualification. Plotting 152 exact zeros would not
clarify the comparison. Independent review remains with the parent.

## Wheel and installation

- Tag: `main-21e761c318c2ac5b555a245365c844d38a93e4cb`.
- Full merged commit: `21e761c318c2ac5b555a245365c844d38a93e4cb`.
- Relative path: `build/engine-wheels/main-21e761c318c2ac5b555a245365c844d38a93e4cb/epcsaft-0.2.0.dev0-cp313-cp313-manylinux_2_39_x86_64.whl`.
- SHA-256: `d2f61e3a5961b859151fbe0487f4ab633405b11620d9dd64682656a68a110357`.
- Old commit: `84ca269dfa0c7068417a1c4c326acae276d4d965`; wheel SHA-256
  `98a140a00796782b536c892695b3546547ab5986a4905ae723190aceee38d83a`.
  Its supplied local interpreter and wheel paths are in `comparison.json`.

Downloads in both the worktree and main checkout passed
`sha256sum --check --strict`. The release asset's digest, tag target, and
`release.json` commit, filename and checksum match the identities above.
Only ignored downloads were written in main; its environment was untouched.
`uv lock` and `uv sync --locked` exit 0 in the worktree. The relative source and
wheel hash are in `pyproject.toml` and `uv.lock`. Installed package/library
bytes match both comparison wheels; no Engine source checkout was imported.

The shared evaluator's `ENGINE_WHEEL_SHA256`, `ENGINE_COMMIT` and stale comment
now identify this wheel: three added lines and four removed, within the approved
four-line ceiling, with no algorithm change. Retained 026b3031 outputs remain
unchanged. For a fresh checkout, download before installation:

```bash
tag=main-21e761c318c2ac5b555a245365c844d38a93e4cb
wheel_dir="build/engine-wheels/$tag"
mkdir -p "$wheel_dir"
gh release download "$tag" --repo tannerpolley/ePC-SAFT --dir "$wheel_dir" \
  --pattern 'epcsaft-*.whl' --pattern '*.sha256' --pattern release.json
(cd "$wheel_dir" && sha256sum --check --strict ./*.sha256)
gh api "repos/tannerpolley/ePC-SAFT/releases/tags/$tag" \
  --jq '.assets[] | select(.name | endswith(".whl")) | .digest'
gh api "repos/tannerpolley/ePC-SAFT/git/ref/tags/$tag" --jq .object.sha
uv sync --locked
```

Require the reported digest to equal `sha256:` plus the recorded checksum,
and the tag target to equal the full commit. Also check `release.json` against
the same commit, filename and checksum. Keep the wheel ignored and retained
locally; a retry must not replace an existing pin with different bytes.

## Document versions and source-input limitation

Only two of 274 tracked parameter documents change. Each adds one
`topology.no_cross_association` item with its own `document_id` and path in the
provenance, and increments its version. All other fields are unchanged. The
declaration keeps CO2/MEA unlike-site edges inactive in the existing model;
it does not claim the physical interaction is absent.

- `data/input/parameters.json`: version **1 → 2**, SHA-256
  `2a03b675aebdccb854c27857e95f493a1aea1436f7d2e236630bd621d9d82f05`.
- `results/selected-current-best-parameters.json`: version **2 → 3**, SHA-256
  `7b0b4bb5669c1b2061fd7ec26e5fb4c8491005bdb5ba8f9e22e4c0b0b4b84308`.
  Its previous version and unchanged `results/heat-160/A-parameters.json` have
  SHA-256 `66ff7715958e9d22e77bd129faf7f67822204e3285b50993bf3f67d72c3b9778`.

Both wheels refuse the source input after the existing shared evaluator's
`c_shell=1.0` and `c_dielectric=1.0` defaults, with exactly
`ParameterError: missing model/electrolyte/ionic_dispersion`. This refusal
predates #569 and is not caused by adoption. No ionic-dispersion form was chosen;
**zero source-input predictions were compared**. The old wheel also accepts
the selected record's declared mapping; its 152 predictions used the undeclared
pre-adoption version. The other 272 parameter documents, frozen campaign inputs,
retained numerical outputs and figure locks remain byte-unchanged.

## Existing checks

[checks.json](checks.json) records exits, exact failing test names and structural
checks. Worktree diagnostic logs remain under `tmp/engine-21e761c3-adoption/`.

- Ruff: **exit 1**, 678 findings, all in unchanged files or unchanged lines.
- Pytest: **exit 1**, **68 passed, 7 failed**. The two native source-feed
  temperature/composition checks pass. Remaining failures concern existing
  historical/canonical tables, film-property admission, manuscript expectations,
  source inventory, volumetric-source checks, and a stale selected-record hash.
  The last is `test_declared_domain_pre_dispatch_and_protected_rows`: it expects
  no-heat hash `756fec50…`, while the base already held heat-fit hash `66ff7715…`.
  The same seven tests fail on `main` 5082ba4 with its Engine 026b3031 environment,
  with the same failure lines apart from that test's current-record hash, so the
  adoption adds no test failure (orchestrator baseline, 2026-10-17).
- Manuscript freshness: **exit 1**, missing
  `docs/scientific/latex/builds/main.pdf`. No manuscript build or Overleaf sync ran.

No requested check stopped on an undeclared frozen historical document under
#569, or reported a new-wheel numerical difference from a retained 026b3031
output. Those outputs were not regenerated; the comparison is against 84ca269d
only. Repository-wide checks are not all passing. This work does not qualify
unexecuted amendment-2 campaigns or promote new manuscript results.
