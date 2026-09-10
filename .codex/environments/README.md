# Codex environment

A new worktree installs repository dependencies without an Engine lock entry,
then installs one local `epcsaft` wheel. Setup first honors
`EPCSAFT_ENGINE_WHEEL`; otherwise it consumes exactly one wheel from the
sibling Engine checkout's `build/environment-wheel/` and verifies its local
`wheel.sha256` evidence when available. It never downloads or builds the
Engine. If no suitable local wheel exists, build ePC-SAFT locally or provide an
explicit wheel path and optional `EPCSAFT_ENGINE_SHA256`.

Setup verifies all three public modules originate from that wheel and never
imports an Engine source checkout.
