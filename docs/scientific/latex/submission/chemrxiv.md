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
Electrolyte PC-SAFT (ePC-SAFT) with explicit ions and activity-based reaction equilibria describes CO₂ absorption in aqueous methyldiethanolamine, which forms no carbamate. This work extends that approach to monoethanolamine (MEA), whose carbamate chemistry changes the ion population with CO₂ loading. A nine-species ePC-SAFT model with Debye–Hückel and Born contributions and explicit carbamate, bicarbonate and carbonate chemistry was fitted simultaneously to 48 CO₂ partial pressures at 40 and 60 °C and 94 liquid species measurements at 20–60 °C in 30 wt% MEA, with average absolute relative deviations (AARD) of 13.53 % and 8.28 %. Outside the fit, the model gives 20.27 % on 21 pressures at 80 °C, and 24.51 % and 25.45 % on 11 and 12 previously unused pressures near 353 and 392 K. Within this model and its fitting bounds, removing the Born term triples the refitted cost, from 32.99 to 98.79, and raises the pressure AARD to 53.9 %. The protonated MEA–carbamate and protonated MEA–water interactions dominate the tested ablations. Across the three tested Born-input sets, solvation-shell and dielectric-saturation (SSM+DS) and original Born terms give costs of 31.7–34.6 after refitting; their ranking changes with the inputs and the titration bicarbonate data role. Refits to ≤60 °C data with literature amine and CO₂-hydration temperature laws give 27.61–29.33 % at 80 °C; fitting the hydration enthalpy gives 23.02 %. Electrolyte-term comparisons for this model should state which speciation data are fitted; independent solvation or activity data could guide Born-form choice, and heat-of-absorption or high-temperature equilibrium data could constrain the temperature response.

## Keywords
CO2 solubility; ePC-SAFT; modified Born term; monoethanolamine; chemical speciation; reactive vapor–liquid equilibrium

## Recommended subject categories
ChemRxiv's list per its search-result excerpt (names as shown there; confirm in the form): Chemical Engineering and Industrial Chemistry; Physical Chemistry; Theoretical and Computational Chemistry; also Energy, Catalysis, and others.
1. **Chemical Engineering and Industrial Chemistry**: CO₂ capture solvent, absorber-relevant vapor–liquid equilibrium.
2. **Physical Chemistry**: equation-of-state thermodynamics, electrolyte solutions, speciation.
3. **Theoretical and Computational Chemistry** (optional): model fitting and ablation; drop it if the form wants only two.

## Licence
Recommend **CC BY 4.0** (the owner's earlier choice). ChemRxiv offers CC BY 4.0, CC BY-NC 4.0 and CC BY-NC-ND 4.0, requires no copyright assignment, and says CC licences are compatible with most publishers' agreements. Elsevier states a preprint on a preprint server is not prior publication, and the Fluid Phase Equilibria guide allows prior preprint posting; Elsevier's FAQ was not read in full, so check the "preprint licence" wording if the journal asks.

## Statements (exact text from sections/data_code_availability.tex)

**Data availability**
The processed observations, parameter records, calculation results and figure data will be public at https://github.com/tannerpolley/Amine-Thermodynamics under the tag manuscript-v1 when this manuscript is posted. The selected SSM+DS parameter record is analyses/mea_parameter_bundle/results/selected-current-best-parameters.json, SHA-256 9055458d8b7cd767a0d08e9f37e4fd28631e29c363364d7b842ebade645cb241. The present 142-target fits, reported current-record assessments and Born-form re-evaluations used the epcsaft wheel with SHA-256 28181e72e429c6e87fc6361082af1a7b21c8747e76bda65a1c30abb4a97402f2. The two R2 refits used wheel SHA-256 9e6a76cf59d4e2fef3347d895bf3a966ecced01f13dc6e0caec74c3c3d618dc4; their records are in analyses/mea_parameter_bundle/results/temperature-reanchor-140/stage-3/. Historical fitting records retain their original wheel identities; in particular, the earlier 160-target SSM+DS multistart fit used wheel SHA-256 f66d972c032ce709ada69e8d8177e195c7e416800757663b7420c22bda5f6328. The Born-form costs are in analyses/mea_parameter_bundle/model-d/born-form-diagnosis/p5conv-costs.csv. The packet assessments of both forms are in analyses/mea_parameter_bundle/model-d/assessment-p5a-11-summary.json and assessment-p5a-00-summary.json in the same directory. The canonical pressure, transfer and extrapolation values with the corrected loading are in analyses/mea_parameter_bundle/model-d/assessment-p5a-loadfix-summary.json and the per-form assessment-p5a-11-loadfix-comparison-scores.csv and assessment-p5a-00-loadfix-comparison-scores.csv. The MIT License covers the repository software and original documentation; third-party experimental data retain their original terms and provenance.

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
1. Make the repository public (https://github.com/tannerpolley/Amine-Thermodynamics).
2. Confirm the tag `manuscript-v1` exists (metadata still has `release_commit: null`).
3. Upload to ChemRxiv: main PDF, supplement and the fields above (the abstract above is final).
4. After acceptance, update the preprint with the DOI link.
