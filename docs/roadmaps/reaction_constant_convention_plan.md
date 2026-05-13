# Reaction Constant Convention Plan

## Purpose

Prevent invalid mixing of apparent, mole-fraction, molality, and thermodynamic equilibrium constants.

## Phase 1 convention

Use literature mole-fraction or apparent constants only in the same convention used by the reproduction baseline. If activities are set equal to mole fractions, say so explicitly.

## Phase 2 convention

Use activity-based thermodynamic constants only where the reference state is explicit and compatible with ePC-SAFT activity coefficients.

Required metadata:

- reaction name,
- stoichiometry,
- constant kind,
- basis,
- standard state,
- activity coefficient convention,
- reference species,
- temperature function,
- pressure function if present,
- source,
- valid temperature/pressure range,
- whether conversion is required.

## Phase 3 convention

Reaction-equilibrium constants may move only as explicit fitted corrections:

- Level 0: fixed literature K(T,P)
- Level 1: fitted scalar Delta logK with tight regularization
- Level 2: fitted temperature coefficients with regularization
- Level 3: simultaneous K plus ePC-SAFT parameter fit

Every fitted K correction must report:

- initial value,
- final value,
- bound,
- regularization weight,
- data family supporting movement,
- residual improvement,
- identifiability note.
