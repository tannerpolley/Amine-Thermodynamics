# ChemRxiv draft fields for the A7 rewrite

This is a local submission aid. No preprint update or publication is authorized here. Portal fields and licence choices require checking at submission; this rewrite makes no claim about the live form.

## Title

Electrolyte PC-SAFT with carbamate chemistry for CO2 in aqueous monoethanolamine: joint calibration and a finite phase test

## Author and affiliation

Tanner W. Polley (corresponding author), ORCID 0009-0008-5957-4152, tpolley3@byu.edu. Department of Chemical Engineering, Brigham Young University, Provo, UT 84602, United States.

## Abstract

Can one explicit-ion equation of state represent equilibrium, caloric and density properties of 30 wt% aqueous monoethanolamine without a numerically resolved Gibbs-energy descent, that is, a lower-Gibbs-energy phase arrangement, at specified states, and what does that restriction cost? A nine-species electrolyte perturbed-chain statistical associating fluid theory (ePC-SAFT) model with carbamate chemistry is jointly calibrated through 16 adjustable parameters against 307 quantities: pressures, species, heats, densities, heat capacities and binary equilibria. Pressure and species data also fitted by a predecessor parameterization give average absolute relative deviations of 11.86 and 7.10%, and fitted integral-heat root-mean-square error is 1.83 kJ/mol CO2. Without empirical volume translation, 44 of 47 fitted loaded densities fall within twice their declared scales. No descent was numerically resolved in 657 trials at 73 specified states (313.15–333.15 K, α 10⁻⁵–0.5). A preceding fit to the same objective met all 47 loaded-density requirements but had resolved descent at 12 of these states; the selected endpoint has three density failures at 353.15 K, 0.40–0.53% below measurement and outside the phase-search temperatures. Comparisons outside the objective are not independent validation: Arcis heats served as an acceptance check, and Wagner pressures and transfer data were examined during model development. Carbonate share, the titration bicarbonate pool, unloaded heat capacity at 318.15 K and 45 wt% pressure transfer remain discrepant. Two sequential single-start fits in sampled bounds establish a constrained local feasibility result with conditional errors and finite phase evidence, not a global optimum or physical validation of phase behavior or process performance.

## Keywords

CO2 solubility; ePC-SAFT; joint parameter estimation; monoethanolamine; chemical speciation; reactive vapor–liquid equilibrium.

## Data availability

The A7 data release DOI is pending. The planned release will identify file roles, reproduction commands and omitted dependencies, with a SHA-256 checksum inventory. The analysis repository is https://github.com/tannerpolley/Amine-Thermodynamics; its evidence commit, including the analysis notebook, is 8f40c125e5945ac785cc0ad1889fc79bea2096c9, and the selected parameter file has SHA-256 e234e8601ebc47b3dec25383ee0a0a8029cabb9f7f92c87866f595c505c7e58e. A7 calculations use the ePC-SAFT Engine software from the private repository https://github.com/tannerpolley/ePC-SAFT, at commit 8298c6029ebb8b467929badc4a223c580ec591ab, with wheel SHA-256 8897a0caab9f2508ed642f42c8b5226957fbe7035ed7bfdad71e4166798785b3. The Engine wheel is not bundled with the planned A7 data release; reproducing the thermodynamic calculations requires access to that dependency. The earlier deposit, DOI 10.5281/zenodo.23323107, concerns the F1 predecessor and does not contain this A7 release.

## Declarations

Funding, competing-interest and generative-AI statements are the approved text in `sections/data_code_availability.tex` and `submission_metadata.yml`. They must be reviewed by the author with the assembled rewrite before submission. The prior licence preference was CC BY 4.0; no licence or portal attestation is submitted by this task.

## Files and remaining gates

The local main and supplement PDFs are `builds/main.pdf` and `builds/supplement.pdf`. Independent number/claim and reader-story reviews, owner review, A7 data publication approval and submission authorization remain open. Historical readiness checks and the F1 deposit do not certify this rewrite.
