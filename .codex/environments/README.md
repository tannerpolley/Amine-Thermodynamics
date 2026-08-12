# Codex environment

A new worktree installs repository dependencies without the historical Engine
lock entry, then installs exactly one Governance-resolved `epcsaft` wheel. For
a pre-authority candidate, supply `EPCSAFT_ENGINE_WHEEL` and its
`EPCSAFT_ENGINE_SHA256`. Setup verifies all three public modules originate from
that wheel and never imports an Engine source checkout.
