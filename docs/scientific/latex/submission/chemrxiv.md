# ChemRxiv submission sheet

Sources for ChemRxiv's fields (search-result excerpts only; the pages themselves returned HTTP 403 to the fetch tool, so nothing below is verified against the live form):
- https://chemrxiv.org/submission-guide (search excerpt)
- https://chemrxiv.org/engage/chemrxiv/submission-information (FAQs, search excerpt)
- https://chemrxiv.org/terms (listed in search, not read)
- https://www.elsevier.com/about/policies-and-standards/sharing/policy-faq and the Fluid Phase Equilibria guide for authors (search excerpts)

## Title
Electrolyte PC-SAFT with carbamate chemistry for CO2 in aqueous monoethanolamine: the role of the Born term and of speciation data

## Author and affiliation
- Tanner W. Polley (corresponding author), ORCID 0009-0008-5957-4152, tpolley3@byu.edu
- Department of Chemical Engineering, Brigham Young University, Provo, UT 84602, United States

## Abstract
Electrolyte PC-SAFT (ePC-SAFT) with explicit ions and activity-based reaction equilibria describes CO₂ absorption in aqueous methyldiethanolamine, which forms no carbamate. This work extends that approach to monoethanolamine (MEA), whose carbamate chemistry changes the ion population with CO₂ loading. A nine-species ePC-SAFT model with Debye–Hückel and Born contributions and explicit carbamate, bicarbonate and carbonate chemistry was fitted through five binary interaction parameters to 47 CO₂ partial pressures at 40 and 60 °C and 94 liquid species measurements at 20–60 °C in 30 wt% MEA, with average absolute relative deviations (AARD) of 13.98 % and 8.26 %. Outside this fit, it gives 19.58 % on 21 pressures at 80 °C, and 22.50 % and 22.27 % on 11 and 12 pressures near 353 and 392 K that entered no fit; because 80 °C data informed fixed reaction-enthalpy shifts, these are not independent temperature predictions. Refitted without the Born term within the same bounds, the model gives a fitted-pressure AARD of 53.60 %. A decomposition of the calculated pressure shows that the Born term lowers the activity sum that sets the CO₂ pressure increasingly with loading, and that the refitted interactions offset its removal at low loading but not at high loading. The solvation-shell and dielectric-saturation (SSM+DS) and original Born terms calibrate comparably; SSM+DS has the lower cost when titration bicarbonate data are not fitted, and original Born when they are. A refit with literature reaction temperature laws and the published CO₂ dispersion energy matches the fit at or below 60 °C but gives 28.91 % at 80 °C and 51.05 % at 100–120 °C, so data at or below 60 °C do not determine the temperature response of this model. Electrolyte-term comparisons for this model should state which speciation data are fitted, and heat-of-absorption or high-temperature equilibrium data are needed to constrain its temperature response.

## Keywords
CO2 solubility; ePC-SAFT; modified Born term; monoethanolamine; chemical speciation; reactive vapor–liquid equilibrium

## Recommended subject categories
ChemRxiv's list per its search-result excerpt (names as shown there; confirm in the form): Chemical Engineering and Industrial Chemistry; Physical Chemistry; Theoretical and Computational Chemistry; also Energy, Catalysis, and others.
1. **Chemical Engineering and Industrial Chemistry**: CO₂ capture solvent, absorber-relevant vapor–liquid equilibrium.
2. **Physical Chemistry**: equation-of-state thermodynamics, electrolyte solutions, speciation.
3. **Theoretical and Computational Chemistry** (optional): model fitting and electrolyte-term comparison; drop it if the form wants only two.

## Licence
Recommend **CC BY 4.0** (the owner's earlier choice). ChemRxiv offers CC BY 4.0, CC BY-NC 4.0 and CC BY-NC-ND 4.0, requires no copyright assignment, and says CC licences are compatible with most publishers' agreements. Elsevier states a preprint on a preprint server is not prior publication, and the Fluid Phase Equilibria guide allows prior preprint posting; Elsevier's FAQ was not read in full, so check the "preprint licence" wording if the journal asks.

## Statements (exact text from sections/data_code_availability.tex)

**Data availability**
The processed observations, parameter files, calculation results and figure data are available at https://github.com/tannerpolley/Amine-Thermodynamics on the branch work/final-rerun (pull request 155). The selected SSM+DS parameter set, F1, is in analyses/mea_parameter_bundle/results/selected-current-best-parameters.json, SHA-256 ae92bac5d2ef7ab690e692f6b1686e18cf06f24ac6b53a6aab4fafeb3046f1aa. The six fits, the comparisons outside the fit, the conditional standard errors, the pressure decomposition and the figure data are in analyses/mea_parameter_bundle/results/final-rerun/, and the source-data corrections are in analyses/mea_parameter_bundle/results/source-corrections-152/. All fits and evaluations used the epcsaft software build (Python wheel) with SHA-256 28181e72e429c6e87fc6361082af1a7b21c8747e76bda65a1c30abb4a97402f2. The estimation of the fixed R2 and R5 shifts is retained in analyses/mea_parameter_bundle/results/reaction-temperature-fit/. The figures are drawn from the retained figure data by analyses/mea_parameter_bundle/scripts/render_manuscript_figures.py, and the result tables by docs/scientific/latex/scripts/final_rerun_tables.py. The MIT License covers the repository software and original documentation; third-party experimental data retain their original terms and provenance.

**Funding**
This research received no specific grant from funding agencies in the public, commercial, or not-for-profit sectors.

**Competing interests**
The author declares no known competing financial interests or personal relationships that could have appeared to influence the work reported in this paper.

**Generative AI declaration**
During preparation of this manuscript, OpenAI Codex and Claude (Anthropic) were used to draft and revise manuscript text, check computational consistency, and assist with bibliography checking and correction. The author reviewed and edited the content and takes responsibility for the final manuscript.

**Ethics**: no human or animal subjects (not stated in the manuscript; owner to confirm if the form asks).

## Files to upload
- Main file: `docs/scientific/latex/builds/main.pdf`
- Supplementary: `docs/scientific/latex/builds/supplement.pdf`
- Format and size limits, and whether the form asks for separate AI or data-availability fields, could not be verified.

## Link to a later journal version
Not verified. ChemRxiv's help pages were inaccessible. Expected route: after journal acceptance, add the published-article DOI to the preprint record via a new version or "update" on the item page; confirm in the ChemRxiv FAQ before relying on it.

## Owner checklist
1. Upload to ChemRxiv: main PDF, supplement and the fields above.
2. The data-availability statement points to the branch `work/final-rerun` (pull request 155); replace it with the release tag once that tag exists.
3. After acceptance, update the preprint with the DOI link.
