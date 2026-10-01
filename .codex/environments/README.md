# Codex environment

A new worktree installs repository dependencies without an Engine lock entry,
then installs one local `epcsaft` wheel. Setup first honors
`EPCSAFT_ENGINE_WHEEL`; otherwise it installs the qualified wheel from
`/home/tnnrpolley21/Workspaces/Engineering/ePC-SAFT/build/fit-audit-20260929/candidate-28181e72/`
and checks its pinned SHA-256. An explicit wheel path may be paired with
`EPCSAFT_ENGINE_SHA256` for local co-development. Setup never downloads the
Engine.

Setup verifies all three public modules originate from that wheel and does not
import an Engine source checkout.
