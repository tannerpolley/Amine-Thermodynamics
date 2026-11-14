## Stability contribution to the fit objective

For completed search state $k$, let $\tau_k$ be the most negative reduced tangent-plane distance on a native resolved descending branch, or zero when the completed search finds none. An unavailable search has no assigned zero. The residual and penalized cost are

$$r_k=\sqrt{w}\,\tau_k/s,\qquad C_{\mathrm{penalized}}=C+\frac12\sum_k r_k^2.$$

Here $C$ is the 307-observation data cost, $w=1$, and the two penalty stages use $s=10^{-2}$ and $s=3\times10^{-3}$. These are the repository choices in #255, implemented by `epcsaft.regression.stability` in the pinned wheel; they are not inferred measurement errors. The pressure rule is $P=cP^*_{\mathrm{bubble}}$, with $c=1.05$ and $3.0$ on the dense and census-feed liquid grids. The separate offset check uses $c=1.5$. The grids and census retain the #255 state definitions; `stability/candidate/grid.json` and `stability/candidate/census-raw.json.gz` own the state exports.

The dense block has 1800 states: 15, 25, 35 and 45 wt% MEA, 313.15–393.15 K in 10 K steps, loadings $10^{-5}$ and 0.025–0.6 mol/mol in 0.025 steps, at both pressure ratios. Another 108 states use the census feed at the same two ratios. The offset block has 576 states: 20, 30 and 40 wt%, 318.15–388.15 K in 10 K steps and loadings 0.0125–0.5875 in 0.025 steps. The liquid–vapor census has 162 states and uses its retained reference pressures. A supplied-trial distance is a separate evaluation, and is not called a newly resolved descent.

The adoption-producing fit is `reduced-refit/F2/previous/unpenalized`. Its `finding.json` records convergence, data cost 150.76290287953717, and zero penalty cost. No penalty stage or retreat was needed for F2. The fresh #341 search checks this endpoint; it performs no new fit. The historical #255 penalty path does not describe how F2 was fitted.

When required by #255, retreat follows the physical parameter segment from an admissible anchor to the penalized endpoint. It tests the endpoint first, reduces the segment fraction in 0.01 steps until admissible, then refines the final interval by ten bisections. No available endpoint means that only a separately verified admissible anchor can be retained. This describes `stable_refit_255.retreat`; it was not invoked for F2. The series rule makes penalized fitting apply to the whole searched set once a split is found. There are no such penalized F2 observations to enumerate.

MEA supplied trials come only from `../reduced-refit/split-registry.json`, whose native resolved-descent admission rule is the owner's #337 decision. No tree discovery is performed. Split counts remain lower bounds from finite searches; completion with no found split does not prove global stability or physical single-phase behavior.
