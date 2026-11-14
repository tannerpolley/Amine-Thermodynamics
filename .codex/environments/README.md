# Codex environment

A new worktree installs repository dependencies without an Engine lock entry,
then installs one local `epcsaft` wheel. Setup first honors
`EPCSAFT_ENGINE_WHEEL`; otherwise it installs the wheel that `pyproject.toml`
and `uv.lock` pin (Engine main `391dfe5d`, built from the commit history now in
`tannerpolley/epcsaft-validation`) from the main checkout's ignored
`build/engine-wheels/main-391dfe5d64ede5036bf160bc6ae037ad5e14af32/` and checks
its pinned SHA-256. An explicit wheel path may be paired with
`EPCSAFT_ENGINE_SHA256` for local co-development. Setup never downloads the
Engine.

Setup verifies all three public modules originate from that wheel and does not
import an Engine source checkout.
