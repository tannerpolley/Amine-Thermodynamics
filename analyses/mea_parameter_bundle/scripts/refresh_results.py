"""Refresh the selected bundle sequentially under one hard wall-clock budget."""

from __future__ import annotations

import argparse
import fcntl
import math
import os
from pathlib import Path
import resource
import signal
import subprocess
import sys
import time

ANALYSIS = Path(__file__).resolve().parents[1]


def run_stage(
    command: list[str],
    remaining: float,
    memory_mib: int,
    *,
    cwd: Path | None = None,
    rendering: bool = False,
) -> None:
    def limits() -> None:
        available = sorted(os.sched_getaffinity(0))
        os.sched_setaffinity(0, {available[-1]})
        os.nice(10)
        if not rendering:
            ceiling = memory_mib * 1024 * 1024
            resource.setrlimit(resource.RLIMIT_AS, (ceiling, ceiling))

    env = dict(
        os.environ,
        OMP_NUM_THREADS="1",
        OPENBLAS_NUM_THREADS="1",
        MKL_NUM_THREADS="1",
        NUMEXPR_NUM_THREADS="1",
        PYTHONUNBUFFERED="1",
        MPLBACKEND="Agg",
        MEA_BOUNDED_RUN="1",
    )
    if rendering:
        # V8 reserves large virtual cages; bound its heap, not its address space.
        env["QUARTO_DENO_V8_OPTIONS"] = (
            f"--max-old-space-size={memory_mib},--max-heap-size={memory_mib}"
        )
    process = subprocess.Popen(
        command,
        cwd=ANALYSIS if cwd is None else cwd,
        env=env,
        start_new_session=True,
        preexec_fn=limits,
    )
    try:
        code = process.wait(timeout=remaining)
        if code:
            raise subprocess.CalledProcessError(code, command)
    finally:
        # Workers inherit this group: stop only descendants of this owned stage.
        try:
            os.killpg(process.pid, signal.SIGTERM)
        except ProcessLookupError:
            pass
        try:
            process.wait(timeout=2)
        except subprocess.TimeoutExpired:
            pass
        try:
            os.killpg(process.pid, signal.SIGKILL)
        except ProcessLookupError:
            pass
        process.wait()


def bounded_main(main) -> None:
    """Give standalone analysis CLIs the same resource boundary as a refresh."""
    if os.environ.get("MEA_BOUNDED_RUN") == "1":
        main()
    else:
        run_stage(
            [sys.executable, str(Path(sys.argv[0]).resolve()), *sys.argv[1:]],
            900,
            2048,
            cwd=Path.cwd(),
        )


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--wall-seconds", type=float, default=900)
    parser.add_argument(
        "--memory-mib",
        type=int,
        default=2048,
        help="solver address-space / Quarto V8 heap limit, not an aggregate RAM quota",
    )
    args = parser.parse_args()
    if (
        not math.isfinite(args.wall_seconds)
        or args.wall_seconds <= 0
        or args.memory_mib <= 0
    ):
        parser.error("resource limits must be finite and positive")
    runs = ANALYSIS / "results/runs"
    runs.mkdir(parents=True, exist_ok=True)
    with (runs / "refresh.lock").open("a") as lock:
        try:
            fcntl.flock(lock, fcntl.LOCK_EX | fcntl.LOCK_NB)
        except BlockingIOError:
            parser.error("another bundle refresh is already running")
        started = time.monotonic()
        commands = [
            [sys.executable, "scripts/generate_figure_data.py"],
            [sys.executable, "scripts/evaluate_direct_absorption_heat.py"],
            [sys.executable, "scripts/validate_thermal_references.py", "--equilibrium"],
            [sys.executable, "scripts/render_figures.py"],
            ["bash", "render.sh", "notebook.qmd"],
            [sys.executable, "scripts/build_absorption_handoff.py"],
        ]
        try:
            for command in commands:
                remaining = args.wall_seconds - (time.monotonic() - started)
                if remaining <= 0:
                    raise subprocess.TimeoutExpired(command, args.wall_seconds)
                print(
                    f"Stage: {' '.join(command)}; {remaining:.0f}s remain", flush=True
                )
                if command[1] in (
                    "scripts/generate_figure_data.py",
                    "scripts/evaluate_direct_absorption_heat.py",
                ):
                    command = [*command, "--overall-timeout-s", str(remaining)]
                run_stage(
                    command, remaining, args.memory_mib, rendering=command[0] == "bash"
                )
        except (
            subprocess.TimeoutExpired,
            subprocess.CalledProcessError,
            KeyboardInterrupt,
        ) as exc:
            print(
                f"Refresh stopped: {exc}. Completed state caches remain; no automatic retry.",
                file=sys.stderr,
            )
            raise SystemExit(1) from exc
        print(
            "Selected data, figures, notebook, and handoff refreshed and hash-checked",
            flush=True,
        )


if __name__ == "__main__":
    main()
