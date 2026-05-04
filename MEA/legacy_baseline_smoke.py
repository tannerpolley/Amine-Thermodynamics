from __future__ import annotations

from legacy_chemical_equilibrium import smoke_check


def main() -> int:
    result = smoke_check()
    print("Legacy baseline smoke passed")
    print("mole_fractions:", result.mole_fractions)
    print("residuals:", result.residuals)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
