# Amendment 6: smaller-d_V control loaded densities (#170)

An information-only call (no fit, no new code; native output in `evaluation/`, reduction command text in `../commands.json`) on wheel `main-21e761c3`, made at the A4 smaller-d_V control endpoint (`amendment-4/matched-smaller-dV/control/usable-budget-endpoint.json`, sha256 `c64a891d…`). Readiness review r1, correction 1.

- **12 Amundsen 2009 loaded-density errors** (30 wt %, 298/323/343 K, loading 0.1–0.4): **−24.28 to −108.15 kg/m³** against the 2 kg/m³ #183 gate (`densities.json`). They differ from the larger-d_V control (amendment-5 probe P) by at most 0.0087 kg/m³.
- **Cold replay of the 205 objective rows** against `matched-smaller-dV/control/native.json`: largest weighted-row difference 6.9e-12, relative cost difference 1.3e-14.
- **Compute:** 19.75 s wall, 19.67 CPU-s. A first attempt stopped at the wheel-path check before any calculation (0.08 s, 0.06 CPU-s; `setup-failure-wheel-path/`).
