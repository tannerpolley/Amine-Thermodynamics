# Independent delivered review — issue #342

Returned 2026-11-14 by the independent read-only Reviewer (`gpt-6-astra`, high effort). Source task: `issue342-delivered-review-1a5ff4e`. PR: [#356](https://github.com/tannerpolley/Amine-Thermodynamics/pull/356).

The returned report follows, with local link targets made repository-relative. The closeout commit records this report and updates review status and its rendered view; it changes no calculation, parameter, numerical result or scientific interpretation.

**Supported** for the fixed-model numerical attribution required by #342, at frozen commit `1a5ff4e11733c8a81c7e2fc29e178c975e69d44b`, against base `673bceba7e7fa103d28bc054850160687b27e92e`. **No required corrections** for the stated scientific use.

The result supports a coupled energy balance with a prominent dispersion change, and two independently sufficient single-coefficient changes in the tested coefficient space. It does not identify a unique microscopic cause or establish global stability.

I checked the full #342 contract, #337’s owner decisions and comments, both added producers and their direct calculation dependencies, retained raw reports, notebook presentation, literature passages and figure. Independent verification used the pinned wheel through `agent-heavy`; the checkout remains clean.

- **Energy attribution is supported.** I replayed all **102 primary isobaric comparisons**—51 configurations under each record—using native pressure roots and the compiled objective. Totals and explicit contribution differences reproduced within $10^{-9}$ mol absolute. At 333.15 K, loading 0.5 and 21.175719 kPa on the stated 30 mass% unloaded-feed basis, $\Delta G/(RT)$ changes from **−2.7295539154 to +7.1863284361 mol**. Dispersion contributes **+10.0772508146 mol** to that change, while Born contributes **−0.8776124211 mol**. Dispersion has the largest absolute change in **49/51** cases; Born does in two, justifying the retained alternative-permittivity probe. The **408** decompositions meet the issue’s $10^{-12}$ closure limit. The subtraction-defined remainder is correctly described as bookkeeping closure. [Calculation producer](../../scripts/split_cause_342.py#L16)

- **The parent reference is handled correctly.** Four frozen splits fall below the old parent evaluated under F2; that parent is not chemically stationary under F2. All 51 instead lie **0.3147586246–8.2608477712 mol above F2’s own equilibrated parent**. This distinction prevents a misleading F2 instability claim. The retained 908 pressure-root evaluations have maximum pressure error **$3.56154\times10^{-5}$ Pa** and positive pressure–density derivatives. [Reference explanation](../../notebook.qmd#L1579)

- **Parameter attribution and count identity are supported.** Reconstructing counts from all 23 raw censuses confirms **54/162 wide** and **0/162 F2**, with no incomplete states for either. Every single move matches its declared change from the original wide mapping; all 21 changes together reproduce the full F2 mapping. Both sufficient singles have zero native descents, supplied negatives and incomplete states. Thus minimum cardinality **one**, with **two solutions**, is justified. The deliberately broken diameter ties appropriately limit this to coefficient attribution, without adopting either intermediate vector. [Parameter results](../../notebook.qmd#L1543)

- **Registry handling is supported.** Independently rebuilding the append sequence from native-resolved trials reproduces the final registry exactly: unchanged **3507-entry prefix**, **2614 additions**, **6121 distinct entries**, and **2954 native-resolved occurrences** in the new case files. Combining retained prefixes and suffixes confirms all **6121 × 162** supplied evaluations for F2 and both sufficient singles, with zero negatives or unavailable values and the reported minima. No supplied-negative or scalar-only point is needed to explain an append. [Registry evidence](registry-append-check.json)

- **The incomplete probe remains a bounded limitation.** The 16 packing-diameter cases fail the existing exact nonnegative parent-Hessian gate despite successful solves and small residuals. They remain incomplete; neither a rounding explanation nor stability is inferred. This limits that probe’s complete census, but does not undermine the two sufficient singles or the wide/F2 identity result. No tolerance relaxation is required for this conclusion. [Admission-gap disclosure](../../notebook.qmd#L1573)

The figure is readable and its plotted contribution/composition rows match retained values. The historical map is explicitly labelled `bc779473` location evidence; its admission interpretation agrees with the archived Engine source. It must retain that historical qualification in any later manuscript use. Source, producer and rendered-HTML hashes match their records; the executable addition is **200/200 physical lines**.

The literature supports the notebook’s distinction between Böttinger’s explicit homogeneous measured subset, absence of reported second liquid in the broader Aronu/Amundsen measurements, and Baygi’s modeling convention. I checked the relevant methods/results passages, Aronu’s appended corrigendum and Baygi Eq. 11 visually.

**Optional observation:** the Böttinger modeling summary could distinguish the MEA interaction parameters taken from Jou (§6, Table 6) from the newly fitted DEA interactions (§6, Tables 7–8). That extra specificity does not change the phase-observation conclusion.

**Next stage: stop for owner promotion; then Write under #347.** This review does not promote the notebook for manuscript use.

I did not rerun the full native-search campaign or millions of supplied evaluations; I audited their raw evidence and independently replayed the primary energy comparisons. My first audit process ended with status 143; the remaining checks completed in resumed jobs. No background jobs remain.
