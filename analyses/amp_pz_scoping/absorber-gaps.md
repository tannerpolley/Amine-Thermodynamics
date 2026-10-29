# Absorber inputs beyond thermodynamic equilibrium

For [MEA-Absorption-Column#85](https://github.com/tannerpolley/MEA-Absorption-Column/issues/85), a thermodynamic parameter record is only one input to a rate-based column. The column also needs reaction rates, molecular transport and packing-specific transfer relations. This document lists gaps; it authorizes no column implementation or parameter adoption.

[Column issue #85](https://github.com/tannerpolley/MEA-Absorption-Column/issues/85) requests a solvent declaration containing the thermodynamic hand-off and these user-supplied transport/kinetic quantities. Its body describes #228 as unbuilt; that historical statement is superseded by the merged #228 comments. The present remaining thermodynamic export limitation is ePC-SAFT#928 (native fitted parameter JSON serialization), not absence of a fitting driver. This scoping task neither opens Engine requests nor changes the column tracker.
