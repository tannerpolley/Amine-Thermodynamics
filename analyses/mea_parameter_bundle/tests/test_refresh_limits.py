"""The refresh deadline must terminate a blocked stage and its child process."""

import importlib.util
from pathlib import Path
import subprocess
import sys
import time

import pytest

SPEC = importlib.util.spec_from_file_location(
    "refresh_results", Path(__file__).parents[1] / "scripts/refresh_results.py"
)
refresh = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(refresh)


def test_stage_deadline_stops_descendants(tmp_path, monkeypatch):
    monkeypatch.setattr(refresh, "ANALYSIS", tmp_path)
    command = [
        sys.executable,
        "-c",
        "import subprocess,sys,time; from pathlib import Path; p=subprocess.Popen([sys.executable,'-c','import time; time.sleep(60)']); Path('child.pid').write_text(str(p.pid)); time.sleep(60)",
    ]
    started = time.monotonic()
    with pytest.raises(subprocess.TimeoutExpired):
        refresh.run_stage(command, 0.3, 512)
    assert time.monotonic() - started < 4
    pid = int((tmp_path / "child.pid").read_text())
    status = Path(f"/proc/{pid}/status")
    assert not status.exists() or "State:\tZ" in status.read_text()


def test_stage_inherits_single_thread_and_cpu_limits(tmp_path, monkeypatch):
    monkeypatch.setattr(refresh, "ANALYSIS", tmp_path)
    command = [
        sys.executable,
        "-c",
        "import os,resource; assert len(os.sched_getaffinity(0))==1; assert all(os.environ[n]=='1' for n in ('OMP_NUM_THREADS','OPENBLAS_NUM_THREADS','MKL_NUM_THREADS')); assert resource.getrlimit(resource.RLIMIT_AS)[0]==512*1024*1024",
    ]
    refresh.run_stage(command, 3, 512)
