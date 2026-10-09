# Codex environment

A new worktree installs repository dependencies without an Engine lock entry,
then installs one local `epcsaft` wheel. Setup first honors
`EPCSAFT_ENGINE_WHEEL`; otherwise it installs the paper wheel (Engine main
`026b3031`) from the Engine's never-pruned
`/home/tnnrpolley21/Workspaces/Engineering/ePC-SAFT/build/wheels/main-026b3031/`
and checks its pinned SHA-256. An explicit wheel path may be paired with
`EPCSAFT_ENGINE_SHA256` for local co-development. Setup never downloads the
Engine.

Setup verifies all three public modules originate from that wheel and does not
import an Engine source checkout.
