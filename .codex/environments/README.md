# Codex environment

A new worktree installs repository dependencies without an Engine lock entry,
then installs one local `epcsaft` wheel. Setup first honors
`EPCSAFT_ENGINE_WHEEL`; otherwise it installs the wheel that `pyproject.toml`
and `uv.lock` pin (Engine main `05e94210` of `tannerpolley/epcsaft`, wheel
released from `tannerpolley/epcsaft-validation`) from the main checkout's ignored
`build/engine-wheels/main-05e94210fa64cf69725e45babc0411d32139df5a/` and checks
its pinned SHA-256. An explicit wheel path may be paired with
`EPCSAFT_ENGINE_SHA256` for local co-development. Setup never downloads the
Engine.

Setup verifies all three public modules originate from that wheel and does not
import an Engine source checkout.
