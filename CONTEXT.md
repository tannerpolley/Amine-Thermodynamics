# MEA thermodynamics domain language

This glossary fixes the terms used when planning and evaluating the MEA–H₂O–CO₂ model. Detailed equations, data contracts, implementation plans, and project status belong in their owner documents rather than here.

## Predictive reactive VLE

A coupled equilibrium calculation in which liquid reaction/speciation and liquid–vapor phase equilibrium are solved together. Neutral CO₂, H₂O, and MEA may enter the vapor phase; charged species remain liquid-only. A predictive claim requires evaluation on campaign-blocked data not used to select the model or parameters.

## Homogeneous reactive tracer

A fixed-temperature, fixed-pressure, single-liquid-phase equilibrium calculation used to verify reaction, activity, source-reference, derivative, and numerical contracts. It is an intermediate diagnostic and is not reactive VLE evidence.

## Reactive bubble state

A coupled reacting-liquid and vapor equilibrium state at prescribed temperature and liquid feed or composition, with bubble pressure and equilibrium vapor composition among the solved outputs.

## Admissible observation

A source-verified measurement with explicit identity, units, composition basis, uncertainty or declared residual scale, provenance, and leakage group. Quarantined, model-derived, unresolved-basis, duplicate-derived, and unbounded censored values are not admissible regression observations.

## Candidate observation

A source-traceable measurement whose identity and campaign block are known but which still lacks one or more execution requirements, such as a residual scale, pressure contract, model-domain admission, or immutable Data-packet binding. Candidate observations may be partitioned for planning but may not be scored or fitted.

## Campaign block

The smallest group of observations that must remain together during model assessment because the rows share a source, apparatus, prepared stock, calibration, temperature series, or derived quantities.

## Campaign-blocked cross-validation

Model and parameter selection performed by holding out complete campaign blocks. It estimates transfer across experiments without pretending that correlated rows are independent.

## All-data refit

The final parameter estimation performed after the model form is frozen, using every admissible in-domain observation. Its residuals describe calibration quality, not independent prediction.

## Model configuration

One declarative combination of neutral polar physics, association topology, dielectric formulation, and Born correction. Each configuration has an immutable identity so comparisons do not depend on informal labels such as M0–M5.

## Promoted parameter set

The single parameter set accepted for scientific use after numerical, identifiability, campaign-blocked assessment, domain, provenance, and immutable-artifact gates pass. Alternative fits remain comparison evidence.

## Application curation

MEA-owned decisions about species, reactions, source rows, measurement roles, units and bases, campaign blocks, residual policies, fit stages, and scientific acceptance.

## Materialized Data packet

The immutable, hash-addressed snapshot of MEA-curated inputs consumed by the unified ePC-SAFT Engine. Runtime code never discovers or imports a sibling repository to obtain it.
