"""Index each unavailable MDEA search by its own declaration and first failed stage."""

import gzip
import json
from collections import Counter
from pathlib import Path
from time import monotonic

HERE = Path(__file__).resolve().parent
BASE = HERE.parent.parent
SOURCE = BASE / "mdea_mea_workflow/results"


def stage(q):
    msg = q.get("message", "") or ""
    if msg.startswith("pressure reference"):
        return "bubble reference"
    if q.get("supplied_available") is False:
        return "supplied trials"
    if msg.startswith("distinct stationary minima"):
        return "overlapping minima"
    if q["status"] == "Exception":
        return "parent declaration"
    return "optimized trial"


def run():
    tick = monotonic()
    files = {
        "fixed selected": [
            HERE.parent / "results/MDEA/screen/selected/declared/summary.json.gz"
        ],
        "tracking incumbent": [SOURCE / "phase-search-421/coverage.json"],
    }
    for p in sorted((SOURCE / "shared-bicarbonate-417/mdea").glob("mdea-*")):
        files[p.name.split("-")[1]] = sorted(p.glob("search-*.json.gz"))
    files["salt original"] = [SOURCE / "salt-anchored-435/campaign/search-0.json.gz"]
    for name in ("salt", "historical"):
        files[name + " rms"] = [BASE / f"round_7/results/C/{name}/search-0.json.gz"]
    result = {}
    for name, paths in files.items():
        rows = []
        for path in paths:
            data = json.loads(
                gzip.decompress(path.read_bytes())
                if path.suffix == ".gz"
                else path.read_bytes()
            )
            if isinstance(data, dict):
                data = data["rows"]
            for q in data:
                if not q.get("complete", q.get("available")):
                    rows.append(
                        dict(
                            key=q["key"],
                            stage=q.get("stage") or stage(q),
                            message=q.get("message"),
                            canonical=q.get("same_calculation_as", q["key"]),
                        )
                    )
        result[name] = dict(
            files=[str(p.relative_to(BASE)) for p in paths],
            rows=rows,
            counts=Counter(q["stage"] for q in rows),
        )
    (HERE / "inventory.json.gz").write_bytes(
        gzip.compress(
            json.dumps(dict(screens=result, seconds=monotonic() - tick)).encode(),
            mtime=0,
        )
    )


if __name__ == "__main__":
    run()
