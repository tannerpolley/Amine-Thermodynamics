"""Join the stalled starts to their source pressures and the final phase identity probes."""

import csv
import gzip
import json
from pathlib import Path

HERE = Path(__file__).resolve().parent


def read(path):
    return json.loads(gzip.decompress(path.read_bytes()))


def main():
    roots = {(r["draw"], r["row"]): r for r in read(HERE / "roots.json.gz")["rows"]}
    out = []
    for p in sorted((HERE / "pressure-rows").glob("*.gz")):
        rec = read(p)
        key = rec["draw"], rec["row"]
        if key in roots:
            r = roots[key]
            pres = r["P"]
            connected = r["path"][1]
            densities = r["densities"]
            method = "TP flash"
            assert abs(pres / rec["trace"][-1]["bubble_Pa"] - 1) < 1e-10
        else:
            trial = read(HERE / "fraction-rows" / p.name)["trace"][-1]
            if trial["fraction"] == 0 and trial.get("pressure"):
                pres = trial["pressure"]
                connected = trial["dilute_connected"]
                densities = trial["densities"]
                method = "vapor fraction"
            else:
                trial = read(HERE / "dense-rows" / p.name)["trace"][-1]
                assert trial["t"] == 1 and trial["P"]
                pres = trial["P"]
                connected = trial["connected"]
                densities = trial["densities"]
                method = "neighboring bubble"
        out.append(
            dict(
                draw=key[0],
                row=key[1],
                loading=rec["loading"],
                observed_Pa=rec["observed_Pa"],
                computed_Pa=pres,
                pressure_ratio=pres / rec["observed_Pa"],
                dilute_connected=connected,
                parent_density_mol_m3=densities[0],
                incipient_density_mol_m3=densities[1],
                method=method,
            )
        )
    assert len(out) == len({(q["draw"], q["row"]) for q in out}) == 37
    with (HERE / "pressures.csv").open("w") as f:
        writer = csv.DictWriter(f, fieldnames=list(out[0]), lineterminator="\n")
        writer.writeheader()
        writer.writerows(sorted(out, key=lambda r: (r["draw"], r["row"])))


if __name__ == "__main__":
    main()
