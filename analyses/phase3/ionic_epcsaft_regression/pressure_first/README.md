# Pressure-first reactive-VLE screen

This Issue #13 analysis freezes 121 source-resolved candidate CO2-pressure
rows. The admitted reaction-correlation domain contains 30 training, 6
model-selection, and 8 reserved rows; 77 higher-temperature rows remain
non-scoring challenges. Reserved rows were not evaluated.

The retained reactive calculation compares exact pressure roots for the M0
nonpolar origin and source-fixed M1 CO2-quadrupole origin on six Hilliard
training states. Both use the declared one-liquid/one-vapor topology and exact
total derivatives. Neither model passes the preregistered residual-trend and
model-selection gates, so no pressure parameter was promoted.

The independent neutral-binary audit evaluates all 29 Cai (1996) MEA-water VLE
rows with the two source-consistent Baygi (2015) models. Both one-coordinate
fits are full rank, interior, and multistart-consistent, but both fail the
source-scale residual and composition-trend gates. Baygi fitted Bubble-T and
Dew-T composition objectives; the retained fixed-state closure results do not
claim to reproduce that objective. No fitted interaction was transferred into
the reactive model.

The canonical decision is `results/pressure_block_ladder_decision.json`.
Exact plotted values are retained beside two diagnostic figure bundles:

- `pressure_block_ladder_diagnostic`: experimental versus exact M0/M1 pressure roots;
- `cai_baygi_binary_model_comparison_diagnostic`: source-consistent binary closure audit.

The manuscript remains unchanged. The next scientific capability is a generic
declared-one-liquid/one-vapor Bubble-T/Dew-T observation family with exact
total parameter derivatives.

Regeneration commands are declared in `analysis.yaml`.
