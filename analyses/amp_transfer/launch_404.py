"""Launch a #404 stage using measured free resources and the selected uv environment."""

import json
import os
from pathlib import Path
import sys
import time


def cpu_sample():
    fields = list(map(int, Path('/proc/stat').read_text().splitlines()[0].split()[1:9]))
    return sum(fields), fields[3]


if __name__ == '__main__':
    before, idle_before = cpu_sample()
    time.sleep(2)
    after, idle_after = cpu_sample()
    free_cpu = (idle_after-idle_before)/(after-before)*len(os.sched_getaffinity(0))
    memory_kib = int(next(row.split()[1] for row in Path('/proc/meminfo').read_text().splitlines()
                          if row.startswith('MemAvailable:')))
    memory_gb = memory_kib/1e6
    cores = max(1, min(16, int(free_cpu), int((memory_gb-7)/.35)))
    here = Path(__file__).resolve().parent
    env = os.environ | dict(AGENT_HEAVY_CORES=str(cores), PYTHONPATH=str(here.parent))
    print(json.dumps(dict(idle_cpu_equivalent=free_cpu, available_memory_GB=memory_gb,
                          requested_cores=cores)), flush=True)
    os.execvpe('agent-heavy', ['agent-heavy', 'uv', 'run', '--no-sync', 'python',
                             str(here/sys.argv[1]), *sys.argv[2:]], env)
