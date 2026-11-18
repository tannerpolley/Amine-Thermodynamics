#!/usr/bin/env bash
set -euo pipefail

repo_root="$(git rev-parse --show-toplevel)"
cd "$repo_root"

for required_command in git python3 realpath sha256sum uv; do
    command -v "$required_command" >/dev/null 2>&1 || {
        echo "missing required command: $required_command" >&2
        exit 1
    }
done

git_common_dir="$(realpath "$(git rev-parse --git-common-dir)")"
main_checkout="$(dirname "$git_common_dir")"
engine_wheel="${EPCSAFT_ENGINE_WHEEL:-}"
expected_engine_sha256="${EPCSAFT_ENGINE_SHA256:-}"
if [[ -z "$engine_wheel" ]]; then
    engine_wheel="$main_checkout/build/engine-wheels/main-05e94210fa64cf69725e45babc0411d32139df5a/epcsaft-1.3.1-cp313-cp313-manylinux_2_39_x86_64.whl"
    expected_engine_sha256="${expected_engine_sha256:-c9fbf898b14d004f915f01ed77675867908dd30d77dc28544b2860e9195c80bb}"
fi
engine_wheel="$(realpath "$engine_wheel")"
if [[ -n "$expected_engine_sha256" ]]; then
    actual_sha256="$(sha256sum "$engine_wheel" | cut -d ' ' -f 1)"
    [[ "$actual_sha256" == "$expected_engine_sha256" ]] || {
        echo "Engine wheel SHA-256 mismatch: $actual_sha256" >&2
        exit 1
    }
fi

uv sync --frozen --group dev --no-install-package epcsaft

mapfile -t stale_distributions < <(
    .venv/bin/python - <<'PY'
from importlib import metadata
import re

for distribution in metadata.distributions():
    name = distribution.metadata.get("Name", "")
    normalized = re.sub(r"[-_.]+", "-", name).lower()
    if normalized.startswith("epcsaft") and normalized != "epcsaft":
        print(name)
PY
)
if ((${#stale_distributions[@]})); then
    uv pip uninstall --python .venv/bin/python "${stale_distributions[@]}"
fi

uv pip install --python .venv/bin/python --reinstall "$engine_wheel"

.venv/bin/python - "$engine_wheel" <<'PY'
from importlib import metadata
from pathlib import Path
import epcsaft
from epcsaft import equilibrium, regression

root = Path(metadata.distribution("epcsaft").locate_file("")).resolve()
for module in (epcsaft, equilibrium, regression):
    path = Path(module.__file__).resolve()
    if root not in path.parents:
        raise SystemExit(f"{module.__name__} does not originate from the Engine wheel")
print(Path(__import__("sys").argv[1]).resolve())
PY
