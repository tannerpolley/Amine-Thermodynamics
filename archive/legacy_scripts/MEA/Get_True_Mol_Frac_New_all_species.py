from __future__ import annotations

from plot_all_species_diagnostic import (
    AllSpeciesChemistryResult,
    SPECIES,
    all_species_residuals,
    get_true_mol_frac,
    main,
    result_rows,
    solve_all_species_result,
    solve_all_species_series,
    write_diagnostics,
)


if __name__ == "__main__":
    print("Deprecated: use MEA/plot_all_species_diagnostic.py for all-species diagnostics.")
    raise SystemExit(main())
