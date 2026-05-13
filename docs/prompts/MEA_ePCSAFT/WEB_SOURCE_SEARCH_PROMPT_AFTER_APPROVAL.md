# Prompt: Search for Remaining Source Articles After User Approval

Use this prompt only after the user explicitly approves source searching.

Goal: find sources for two remaining data categories:

1. Loaded-MEA pH or electrochemical data.
2. Direct MEAH+ salt or carbamate salt osmotic/activity data.

Do not download or paste full copyrighted papers. Identify articles, DOIs, likely tables/figures, and whether the data are usable.

## Search category A — loaded MEA pH/electrochemical data

Search for:
- CO2-loaded monoethanolamine pH data
- loaded MEA potentiometric data
- pH of aqueous monoethanolamine CO2 loading
- electrochemical measurement CO2 loaded MEA
- proton activity monoethanolamine CO2

Required metadata:
- article title
- authors
- year
- DOI
- property measured
- temperature range
- MEA concentration
- CO2 loading/pressure range
- pH scale or electrode method
- whether data appear in tables or figures
- likely use: fit / validation / convention check / reject

## Search category B — direct MEAH+ salt or carbamate salt osmotic/activity data

Search for:
- ethanolammonium salt osmotic coefficient
- ethanolammonium chloride activity coefficient
- monoethanolammonium activity coefficient
- MEA carbamate salt osmotic coefficient
- monoethanolamine carbamate salt thermodynamics
- ammonium carbamate osmotic coefficient as analog only
- ethanolammonium acetate mean ionic activity coefficient

Required metadata:
- article title
- authors
- year
- DOI
- salt identity
- solvent
- temperature
- molality/concentration range
- osmotic coefficient / MIAC / water activity / density
- whether the data constrain MEAH+, MEACOO-, or only an analog
- recommended use: direct evidence / transferability check / reject

## Strict evidence rule

Do not treat ethanolammonium acetate, ethanolammonium chloride, or ethanolammonium hexanoate as MEACOO- evidence. They may only support MEAH+ transferability if the counterion is independently modeled.

Do not treat ammonium carbamate as MEACOO- evidence unless the manuscript explicitly labels it as an analog and not a direct fit target.

## Output

Create/update:

```text
docs/roadmaps/pending_source_search_results.md
data/reference/MEA/manifests/pending_external_source_manifest.csv
```

No data import until the user has downloaded/provided the articles or the data are openly accessible and license-safe.
