# Smallest next regression experiment

1. Ideal-liquid chemistry: keep the two sibling eNRTL combo reactions and the
   current fitted `A+B/T+C ln(T/K)` coefficients fixed; use `a_i=x_i` only as
   the six-species reference calculation. This is the present analysis, not an
   ePC-SAFT activity calculation.
2. Activity-aware six-species model: inject one accepted immutable ePC-SAFT
   Engine wheel and a packet-bound six-species subset, then evaluate the same
   states with the same two reaction stoichiometries and standard-state
   identity. First hold both reaction correlations fixed and record activity,
   charge, balance, and `ln Q-ln K` residuals. Missing or inapplicable packet
   inputs must fail explicitly.
3. Parameter regression: only after step 2 closes numerically, regress the six
   reaction-correlation coefficients (or a preregistered lower-dimensional
   subset) against the retained VLE and speciation views. Keep ePC-SAFT pure and
   binary parameters fixed, do not fit a new interaction block, and score
   pressure/speciation on held-out source groups. This would be a parameter
   experiment, not validation or adoption of an active MEA parameter set.

The smallest discriminating next run is step 2 at the existing 30 wt% states,
with no coefficient fitting. It separates liquid-activity effects from the
already-fitted reaction-correlation effects before adding regression freedom.
