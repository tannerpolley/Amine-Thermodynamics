# Analysis Toybox

This directory is a sandbox for bounded scientific experiments. A toybox
workflow may use SciPy, finite differences, simplified weighting, or other
expedient methods to test whether an idea is worth implementing in the unified
ePC-SAFT Engine.

Nothing under `analyses/toybox/` is a publication input or an accepted
parameter source. A result can leave the toybox only through a separate,
reviewed workflow that binds current data provenance, an immutable Engine
artifact, admissible residual definitions, numerical acceptance gates, and
independent validation.

Toybox workflows must state:

- the engineering question and fitted coordinates;
- data roles, units, weighting, starts, bounds, and failure handling;
- what the result established and failed to establish;
- the source branch and commit when historical outputs are retained.
