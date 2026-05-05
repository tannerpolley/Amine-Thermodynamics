import os
import subprocess
import sys
from dataclasses import dataclass
from pathlib import Path


SCRIPT_DIR = Path(__file__).resolve().parent
REPO_ROOT = SCRIPT_DIR.parents[0]
RUNTIME_TMP = REPO_ROOT / "out" / "tmp" / "plot_exports"
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))


@dataclass(frozen=True)
class ScriptJob:
    module: str
    timeout_seconds: int = 180
    optional_runtime: str | None = None


SCRIPT_JOBS = [
    ScriptJob("MEA.six_species.plot_speciation", 240),
    ScriptJob("MEA.six_species.plot_pressure", 240),
    ScriptJob("MEA.epcsaft_neutral.plot_pressure", 360),
    ScriptJob("MEA.nine_species.plot_speciation_diagnostic", 240),
    ScriptJob("MEA.nine_species.plot_pressure_diagnostic", 600),
    ScriptJob("MEA.epcsaft_diagnostics", 180, "epcsaft"),
    ScriptJob("MEA.epcsaft_present_plots", 240, "epcsaft"),
]


def _script_command(job: ScriptJob) -> list[str]:
    return [sys.executable, "-m", job.module]


def _epcsaft_runtime_available() -> tuple[bool, str]:
    try:
        from MEA.epcsaft_runtime import load_epcsaft

        load_epcsaft()
    except Exception as exc:
        return False, str(exc).splitlines()[0]
    return True, ""


def main() -> int:
    RUNTIME_TMP.mkdir(parents=True, exist_ok=True)
    env = os.environ.copy()
    env["MPLBACKEND"] = "Agg"
    env["OMP_NUM_THREADS"] = "1"
    env["OPENBLAS_NUM_THREADS"] = "1"
    env["MKL_NUM_THREADS"] = "1"
    env["NUMEXPR_NUM_THREADS"] = "1"
    env["TEMP"] = str(RUNTIME_TMP)
    env["TMP"] = str(RUNTIME_TMP)
    env["TMPDIR"] = str(RUNTIME_TMP)

    epcsaft_available, epcsaft_skip_reason = _epcsaft_runtime_available()
    failures = []
    skipped = []
    for job in SCRIPT_JOBS:
        if job.optional_runtime == "epcsaft" and not epcsaft_available:
            skipped.append(job.module)
            print(f"[SKIP] {job.module} ({epcsaft_skip_reason})")
            continue

        command = _script_command(job)
        print(f"[RUN] {job.module} ({sys.executable})")
        try:
            result = subprocess.run(
                command,
                cwd=str(REPO_ROOT),
                env=env,
                capture_output=True,
                text=True,
                timeout=job.timeout_seconds,
            )
            timed_out = False
        except subprocess.TimeoutExpired as exc:
            result = subprocess.CompletedProcess(
                exc.cmd,
                returncode=124,
                stdout=exc.stdout or "",
                stderr=exc.stderr or "",
            )
            timed_out = True

        saved_paths = [
            line.split("Saved plot:", 1)[1].strip()
            for line in result.stdout.splitlines()
            if "Saved plot:" in line
        ]

        if result.returncode == 0:
            print(f"[OK] {job.module}")
            for path in saved_paths:
                print(f"  PNG: {path}")
        else:
            failures.append(job.module)
            if timed_out:
                print(f"[TIMEOUT] {job.module} ({job.timeout_seconds}s)")
            else:
                print(f"[FAIL] {job.module}")
            for path in saved_paths:
                print(f"  PNG: {path}")
            stderr_lines = [line for line in result.stderr.splitlines() if line.strip()]
            stdout_lines = [line for line in result.stdout.splitlines() if line.strip()]
            tail = stderr_lines[-10:] if stderr_lines else stdout_lines[-10:]
            for line in tail:
                print(f"  {line}")

    print("\nSummary")
    print(f"  Successful: {len(SCRIPT_JOBS) - len(failures) - len(skipped)}/{len(SCRIPT_JOBS)}")
    print(f"  Skipped: {', '.join(skipped) if skipped else 'none'}")
    print(f"  Failed: {', '.join(failures) if failures else 'none'}")
    return 1 if failures else 0


if __name__ == "__main__":
    raise SystemExit(main())
