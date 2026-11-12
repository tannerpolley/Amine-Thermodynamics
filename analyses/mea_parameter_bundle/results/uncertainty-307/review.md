# Independent delivered-result review: issue 307

**Supported.** Reviewed commit `fd203d7445143d060096d057604e0eee8069b378`, explicit base `79706636e8716974e045b582f1b1cbfe7e4c7009`. The independent CSE reviewer returned this verdict on 11 November 2026 after the complete result and capability review. No required scientific or implementation corrections remain.

The corrected implementation, retained numerical evidence, notebook interpretation and selected renders agree for the bounded uncertainty and sensitivity use requested in #307.

- R5 profiles translate the remaining native reaction-coordinate origin and bounds by the native completed-law offset, preserving the original-coordinate interval. All three retained pressure/heat equivalence checks give zero difference at optimizer steps 0 and 0.25. A separate reviewer calculation through the complete original coordinate declaration reproduced corrected profile-endpoint pressure and heat within 2.60e-13 relative.
- The MDEA 1% Born-diameter fit retains four rejected-trial records with observation identity, native cause and trial vector. These are saturation/equilibrium refusals at rejected vectors; the converged endpoint remains usable. Other current fits retain explicit empty failure lists.
- Independent retained-data calculations reproduced weighted costs, scaled-Jacobian singular values and directions, conditional covariance consistency, marginal sensitivity rankings, profile prediction changes and propagated band standard errors. All 24 intended profile endpoints are usable and converged.
- Native Engine fitting, derivatives and reaction-law completion remain the numerical owners. Installed Engine bytes match the specified wheel. The 371 added executable lines are below the approved 400-line ceiling. Both selected HTML outputs embed the exact retained uncertainty figures without notebook_files dependencies.

| Set | Prediction quantities | Pressure states | Temperature range (K) | Conditional relative pressure SE |
|---|---:|---:|---|---|
| MEA | 158 | 47 | 313–333.15 | 5.41–16.00% |
| MDEA B1 | 148 | 108 | 298.15–393.15 | 7.82–39.11% |

Native variance factors are 1.0000710 and 2.7639784. Both conditional refits retain zero coordinate movement.

This supports comparing parameter influence under the declared perturbations and identifying locally weak parameter combinations. Covariance and pressure bands remain linearized and conditional on the model, weights, source inputs and bound-fixed coordinates. Marginal one-SE rankings and refitted 1% profile-step rankings use different perturbation scales; their ordering does not establish statistical significance. The short inward scans locate neither confidence limits nor a global optimum. No phase-stability requalification, model-discrepancy estimate, new physical validation, adopted-parameter change or absorber-use qualification follows. Manuscript use still requires investigator promotion.

The review used the accepted method and retained evidence; its checkout lacked a local literature shelf and it made no fresh primary-paper judgment. No campaigns were rerun or files edited by the reviewer; fresh native work was limited to focused endpoint checks. Optional whitespace cleanup was explicitly nonblocking.
