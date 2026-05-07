from __future__ import annotations

from MEA.six_species.chemistry import LEGACY_SPECIES_6, smoke_check


def main() -> int:
    result = smoke_check()
    print("Legacy six-species smoke check")
    print("species:", ", ".join(LEGACY_SPECIES_6))
    print("message:", result.message)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
