import os
import subprocess
import sys
from pathlib import Path


SCRIPT_DIR = Path(__file__).resolve().parent
REPO_ROOT = SCRIPT_DIR.parents[0]
RUNTIME_TMP = REPO_ROOT / "out" / "tmp" / "plot_exports"
SCRIPT_NAMES = [
    "legacy_pcsaft_baseline.py",
    "Get_True_Mol_Frac.py",
    "Get_True_Mol_Frac_New.py",
    "Get_True_Mol_Frac_New_all_species.py",
    "Get_True_Mol_Frac_with_activity.py",
    "epcsaft_diagnostics.py",
    "epcsaft_present_plots.py",
]
DEFAULT_TIMEOUT_SECONDS = 180
SCRIPT_TIMEOUT_SECONDS = {
    "legacy_pcsaft_baseline.py": 240,
    "Get_True_Mol_Frac.py": 240,
    "Get_True_Mol_Frac_New.py": 240,
    "Get_True_Mol_Frac_New_all_species.py": 240,
    "Get_True_Mol_Frac_with_activity.py": 240,
    "epcsaft_diagnostics.py": 180,
    "epcsaft_present_plots.py": 240,
}


def _script_command(script_name: str) -> list[str]:
    return [sys.executable, script_name]


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

    failures = []
    for script_name in SCRIPT_NAMES:
        command = _script_command(script_name)
        print(f"[RUN] {script_name} ({sys.executable})")
        timeout_seconds = SCRIPT_TIMEOUT_SECONDS.get(script_name, DEFAULT_TIMEOUT_SECONDS)
        try:
            result = subprocess.run(
                command,
                cwd=str(SCRIPT_DIR),
                env=env,
                capture_output=True,
                text=True,
                timeout=timeout_seconds,
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
            print(f"[OK] {script_name}")
            for path in saved_paths:
                print(f"  PNG: {path}")
        else:
            failures.append(script_name)
            if timed_out:
                print(f"[TIMEOUT] {script_name} ({timeout_seconds}s)")
            else:
                print(f"[FAIL] {script_name}")
            for path in saved_paths:
                print(f"  PNG: {path}")
            stderr_lines = [line for line in result.stderr.splitlines() if line.strip()]
            stdout_lines = [line for line in result.stdout.splitlines() if line.strip()]
            tail = stderr_lines[-10:] if stderr_lines else stdout_lines[-10:]
            for line in tail:
                print(f"  {line}")

    print("\nSummary")
    print(f"  Successful: {len(SCRIPT_NAMES) - len(failures)}/{len(SCRIPT_NAMES)}")
    print(f"  Failed: {', '.join(failures) if failures else 'none'}")
    return 1 if failures else 0


if __name__ == "__main__":
    raise SystemExit(main())
