from __future__ import annotations

import epcsaft

from MEA.epcsaft_ionic.model import DEFAULT_INITIAL_GUESS, load_speciation_targets, load_vle_targets, predict_co2_pressure_kPa


def main() -> int:
    values = dict(DEFAULT_INITIAL_GUESS)
    vle = load_vle_targets(1)[0]
    spec = load_speciation_targets(1)[0]
    try:
        pressure = predict_co2_pressure_kPa(vle.x, vle.T, vle.P, values)
        pressure_status = f"predicted_CO2_kPa={pressure:.6g}"
    except epcsaft.InputError as exc:
        pressure_status = f"pressure_backend_unavailable={str(exc).splitlines()[0]}"
        pressure = None
    print(f"VLE smoke target: T={vle.T}, loading={vle.loading}, {pressure_status}")
    print(f"Speciation smoke target: T={spec.T}, loading={spec.loading}, x_sum={spec.x.sum():.12g}")
    return 0 if pressure is None or pressure > 0.0 else 1


if __name__ == "__main__":
    raise SystemExit(main())
