"""Independent two-step composition Hessian at every reconstructed in-grid liquid."""

from closure import HERE, c
import hong_2027 as hong
from time import monotonic
import csv
import json
import numpy as np


def rows():
    for q in csv.DictReader((hong.OUT / "canonical.csv").open()):
        if q["inside_hong_grid"] != "True":
            continue
        tick = monotonic()
        m = hong.model(float(q["w"]))
        eig = [
            hong.eigenvalue_fd(
                m,
                float(q["T_K"]),
                np.array(json.loads(q["liquid"])),
                float(q["liquid_density_mol_m3"]),
                h,
            )
            for h in (1e-6, 5e-7)
        ]
        yield dict(
            key=q["record_id"],
            status=q["stability"],
            native=q["minimum_eigenvalue"],
            eigenvalues=eig,
            seconds=monotonic() - tick,
        )


if __name__ == "__main__":
    tick = monotonic()
    c.refit.save(
        HERE / "hong.json.gz",
        dict(wheel=c.r.SHA, rows=list(rows()), seconds=monotonic() - tick),
    )
