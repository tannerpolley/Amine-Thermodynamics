from __future__ import annotations

from plot_legacy_pressure import (
    EXPECTED_MEDIAN_ABS_LOG10_ERROR,
    compute_jou_metrics,
    legacy_pcsaft_params,
    main,
    predict_co2_pressure_kpa,
)


if __name__ == "__main__":
    print("Deprecated: use MEA/plot_legacy_pressure.py for the canonical legacy Jou pressure plot.")
    raise SystemExit(main())
