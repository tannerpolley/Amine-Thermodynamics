# Independent delivered review of issue #338

**Supported** for the stated purpose: calibration and numerical-verification evidence for the owner's parameter choice in #340. No adoption, manuscript promotion, physical validation, or global-stability conclusion follows from this review.

Reviewer: independent T3 Reviewer, GPT-6 Astra, high effort. Task `node:delegated-task:command%3Amcp%3A6370de88-0b08-4a7a-b370-6ba309ad7f5c%3Adelegate-task%3A0872d803-b989-47e5-8351-d8447ec43bc7`. Reviewed commit `260a74617e704512d589430f0c43f0403407b4c3`, against explicit implementation base `13bb6fb`. The review was read-only and ran no optimization or full assessment. The reviewer read #338, both owner amendments, and #337's series rules, owner decisions and comments.

The following is the reviewer's delivered conclusion, retained from its final result.

> The principal result is supported: replacing the complete R2 and R5 laws removes three fitted parameters with a dimensionless cost increase of 2.0214779. The Born-diameter ties remove another two with a further increase of 0.2308793. Subsequent cumulative restrictions cost more.

| Record | Fitted parameters | 307-row cost | Increase from F0 | On bounds |
|---|---:|---:|---:|---:|
| F0 | 16 | 148.510546 | 0 | 6 |
| F1 | 13 | 150.532024 | 2.021478 | 2 |
| F2 | 11 | 150.762903 | 2.252357 | 1 |
| F3 | 9 | 169.138149 | 20.627603 | 1 |
| F4 | 9 | 174.451397 | 25.940851 | 2 |
| F4-0 | 8 | 176.049063 | 27.538518 | 1 |
| F5 | 8 | 186.615092 | 38.104546 | 3 |

These costs use the same 307 observations and declared residual scales and weights. They do not imply uniform improvement across properties. For example, the not-fitted six-source pressure average absolute relative deviation increases from 23.82475% for F0 to 24.18310% for F1 and 39.70391% for F5. The full property comparisons, units, data roles and conditional-error limits are retained in the result account.

**Required defects, unsupported claims and duplicated responsibilities:** none found that invalidate this delivery for its stated use.

The supporting checks were:

- **Numerical evidence:** independently checked retained rows, parameter hashes, cost sums, assessment provenance and input fingerprints. F0 is byte-exact to the specified record and reproduces the reference predictions and cost exactly. Salt replay differences are zero; reduced endpoint checks satisfy the specified relative tolerance.
- **Starts and stability:** all twelve retained native reports end on function tolerance, with zero continuations. Each start has 1908 grid states, 576 offset states and 162 census states available, with no discovered split. Each census additionally evaluates 143 historical supplied trials, all evaluated and nonnegative. The supplied evaluations supplement the optimized Full search. Selection uses fitted cost; tolerance ties are disclosed. F4's bound triggers F4-0, and F5 continues from F4.
- **Literature laws:** inspected Bates–Pinching p.351, Eq.(10) and Table 2, including the retained page image and source PDF hash; also inspected the relevant Austgen, Böttinger and Baygi passages and verified their shelf/source hashes. The exact R5 conversion gives ln K(298.15 K) = −21.865746172917778. The measured Table 2 mean absolute residual, 0.0009073164433412793 pK, is appropriately reported beside the source's 0.0010, without gating.
- **Implementation and ownership:** examined the generalized coordinate construction, endpoint reconstruction, fit, search, supplied-trial, retreat and assessment paths and their connected producers. Existing #255 fitting/retreat, #307 conditional-information and assessment producers retain numerical ownership. True Born ties are used. Historical unstable evidence checks supplied negative tangent-plane distance and refusal to write an unstable anchor without an endpoint. The implementation adds coordination and reporting rather than another numerical method.
- **Uncertainty and delivery:** conditional errors exclude active-bound coordinates and retain coordinate identities, correlations and variance factors. Selected-record hashes agree across checked assessment producers. All seven records have inherited Part II values. Independent Git accounting confirms 597 gross additions: 509 in the driver, 77 in `stable_refit_255.py` and 11 in `final_evidence.py`, within the amended 600-line ceiling. Protected parameter, pin, manuscript and registry paths are unchanged.
- **Presentation:** inspected the complete notebook context, cost figure and rendered section; the rendered HTML hash matches the retained delivery check. The notebook section distinguishes this comparison from historical adoption evidence.

**Optional hardening or scope changes:** none requested. Additional starts, broader searches, uncertainty propagation or published-model scoring would expand this task. #339's unavailable-at-freeze common-row scores do not block #338.

Limits remain material: two starts establish local solutions; finite searches provide lower-bound split counts; zero penalty cost is inferred on the searched states, and no penalized refit or retreat was triggered by these candidates. Conditional standard errors are not prediction intervals. F4/F4-0/F5 inherit bound salt-fit values and extrapolate the salt laws from 278–318 K to MEA states up to 393 K. Previously inspected not-fitted data do not constitute independent physical validation.

**Next stage: stop at the #340 owner adoption checkpoint.** The reviewed evidence is suitable for that choice. Writing requires the owner's subsequent parameter selection and explicit promotion of the reviewed notebook for manuscript use.
