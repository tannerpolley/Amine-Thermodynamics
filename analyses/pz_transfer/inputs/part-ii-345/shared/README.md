# Piperazine declaration for the shared Part II calculation

These materialized inputs adapt the phase-1 declaration to the merged
`analyses/part_ii.py` interface. Paths are relative to this directory.
`campaign.json` uses F2; `previous.json` replays the frozen F0 A12 endpoint
without adopting F2 or changing its Born diameters.

The two complete starts preserve the retained endpoint and retained second
optimizer vector. The three P3–P5 values are total offsets to the unshifted
source laws, already included in each start's reaction document. Their charts
use the corresponding absolute a coefficients and absolute bounds. The
shared calculation transports these charts after source-reference completion.

`covariance.json` is the full 294-by-294 covariance from
`reactive.calibration`: normalized-area NMR covariance followed by the 62
pressure variances. Its identities follow the exact original fitted-row order.
Every fitted observation uses raw difference form, scale 1 and weight 1.
The fitted row counts are 232 NMR group fractions and 62 Hilliard pressures;
52 Ermatchkov pressures are not fitted and 94 Kamps pressures are comparison
only. The existing solid-precipitation exclusion is preserved. All other rows
are included, including 283.15 K and 395.0 K.

The split record separates 100 retained native resolved descents from two
composition-only historical supplied trials. The latter remain
`resolved_descent: false`; their provenance is retained verbatim, including
the phase-1 collector's inference from the neighbour producer. That inference
does not make the two composition-only records native trial records. Packing
values 0.4128283021108707 and 0.41196189417630624 are the recovered neighbour
values supplied in the owner's instruction. Only this PZ record is consumed.

The grid uses every distinct fitted molality (48 stocks), the #255 census
loading nodes and the maximum loading in the PZ data (1.64226 mol/mol).
There are 8,640 grid entries. The specification has 440 observation entries
at 329 measured reactive states: the two NMR groups at one state have separate
problem identities. The shared producer therefore searches 9,080 entries;
these entry counts must not be called counts of distinct physical states.

Curves use 21 loading nodes per series. Hilliard curves use its nominal source
temperatures (313.15 and 333.15 K) and stock levels (0.9, 2, 2.5, 3.6 and
5 mol/kg); observations keep their actual temperatures and concentrations.
Ermatchkov curves use the retained comparison's nominal stocks (1, 2, 2.75,
4 mol/kg). Other curves retain source temperatures and molalities. Where a
series has only one observation, its loading interval is that of the source
group, rather than a line drawn through one measured point. Curve observations
carry normalization value 1 solely for construction; they are never measured
data or fitted observations.

273.15–498.15 K is the source-correlation range stated by Austgen 1991 Table V p.547 (citing Edwards 1978), not verified measured coverage.
PZ source ranges and the distinct 283.15–395 K calculation interval remain
those of phase 1. Range marks never exclude a temperature.
