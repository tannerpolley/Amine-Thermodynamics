from __future__ import annotations

import csv
import json
import math
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[3]
SRC_ROOT = REPO_ROOT / "src"
if str(SRC_ROOT) not in sys.path:
    sys.path.insert(0, str(SRC_ROOT))

from MEA.epcsaft_ionic.model import EPCSAFT_IONIC_ANALYSIS

OUT_DIR = EPCSAFT_IONIC_ANALYSIS / "results" / "oh_born_derivation"

# Standard Born hydration relation, using water at 298.15 K.
# |Delta G| = 69.467728 * z^2 * (1 - 1/epsilon_r) / r_nm
BORN_CONSTANT_KJ_NM_PER_MOL = 69.467728
WATER_RELATIVE_PERMITTIVITY_298K = 78.37
OH_HYDRATION_FREE_ENERGY_KCAL_MOL = 106.4
KCAL_TO_KJ = 4.184


def derive() -> dict[str, object]:
    hydration_kj_mol = OH_HYDRATION_FREE_ENERGY_KCAL_MOL * KCAL_TO_KJ
    radius_nm = (
        BORN_CONSTANT_KJ_NM_PER_MOL
        * (1.0 - 1.0 / WATER_RELATIVE_PERMITTIVITY_298K)
        / hydration_kj_mol
    )
    radius_angstrom = radius_nm * 10.0
    diameter_angstrom = 2.0 * radius_angstrom
    return {
        "species": "OH-",
        "parameter": "d_born",
        "hydration_free_energy_abs_kcal_mol": OH_HYDRATION_FREE_ENERGY_KCAL_MOL,
        "hydration_free_energy_abs_kj_mol": hydration_kj_mol,
        "water_relative_permittivity_298K": WATER_RELATIVE_PERMITTIVITY_298K,
        "born_constant_kj_nm_per_mol": BORN_CONSTANT_KJ_NM_PER_MOL,
        "born_radius_nm": radius_nm,
        "born_radius_angstrom": radius_angstrom,
        "born_diameter_angstrom": diameter_angstrom,
        "promoted_d_born": diameter_angstrom,
        "source_basis": (
            "Born hydration-energy inversion using an absolute hydroxide hydration free energy "
            "of 106.4 kcal/mol and the Born/cavity-radius interpretation documented by Jacobs1985. "
            "This is a literature-backed estimate, not an MEA-system regression."
        ),
        "external_source_leads": [
            "Palascak and Shields 2004, J. Phys. Chem. A, DOI 10.1021/jp049914o",
            "Marcus 1988, Chem. Rev., DOI 10.1021/cr00090a003",
            "Jacobs1985 in docs/latex/references.bib for Born-model radius interpretation",
        ],
    }


def main() -> None:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    payload = derive()
    (OUT_DIR / "oh_born_derivation.json").write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
    with (OUT_DIR / "oh_born_derivation.csv").open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(payload.keys()), lineterminator="\n")
        writer.writeheader()
        writer.writerow(payload)
    (OUT_DIR / "oh_born_derivation.mpl.yaml").write_text(
        "artifact:\n"
        "  title: Hydroxide Born diameter derivation\n"
        "  description: Tabular literature-backed Born hydration-energy inversion for the promoted hydroxide Born diameter.\n"
        "  csv: oh_born_derivation.csv\n"
        "  json: oh_born_derivation.json\n",
        encoding="utf-8",
    )
    print(json.dumps(payload, indent=2))


if __name__ == "__main__":
    main()
