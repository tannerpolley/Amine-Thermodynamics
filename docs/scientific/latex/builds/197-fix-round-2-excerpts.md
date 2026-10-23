# Exact before/after excerpts for issue 197, correction round 2

Baseline: `ae15c4d`. Science overrides the story N7 residual-scaling sentence. N8 uses the appended reviewer correction.

## `docs/scientific/latex/main.tex:101`

Before:
```
The fitted protonated-amine dissociation constant exceeds the Bates--Pinching value by 0.49 pK
```
After:
```
The fitted protonated-amine dissociation p$K$ exceeds the Bates--Pinching value by 0.49
```

## `docs/scientific/latex/submission/chemrxiv.md:13`

Before:
```
dissociation constant exceeds
```
After:
```
dissociation pK exceeds
```

## `docs/scientific/latex/submission/chemrxiv.md:13`

Before:
```
by 0.49 pK at
```
After:
```
by 0.49 at
```

## `docs/scientific/latex/submission/cover_letter.md:7`

Before:
```
dissociation constant exceeds
```
After:
```
dissociation pK exceeds
```

## `docs/scientific/latex/submission/cover_letter.md:7`

Before:
```
by 0.49 pK at
```
After:
```
by 0.49 at
```

## `docs/scientific/latex/sections/data_methods.tex:132`

Before:
```
a tolerance of $10^{-10}$ on the equilibrium-equation residuals, recomputed in unscaled form.
```
After:
```
a tolerance of $10^{-10}$ on the recomputed residuals used to decide convergence, after the solver's row scaling.
```

## `docs/scientific/latex/supplement.tex:101`

Before:
```
an equilibrium-row tolerance of $10^{-10}$ recomputed in the unscaled equations.
```
After:
```
a tolerance of $10^{-10}$ on the recomputed residuals used to decide convergence, after the solver's row scaling.
```

## `docs/scientific/latex/sections/mea_system_modeling_results.tex:100`

Before:
```
so the model underpredicts at 15
```
After:
```
so, on logarithmic average, the model underpredicts at 15
```

## `docs/scientific/latex/sections/mea_system_modeling_results.tex:146`

Before:
```
Two sequential single-start fits with bounds chosen from fixed-diameter test calculations, give local solutions;
```
After:
```
Two sequential single-start fits, with bounds chosen from fixed-parameter probes (Section~S5), give local solutions;
```

## `docs/scientific/latex/sections/mea_system_modeling_results.tex:71`

Before:
```
lie within the declared \SI{1.0}{\kilogram\per\cubic\metre} absolute-error limit
```
After:
```
lie within the \SI{1.0}{\kilogram\per\cubic\metre} absolute-error limit
```

## `docs/scientific/latex/sections/mea_system_modeling_results.tex:72`

Before:
```
separating fitted rows from non-fitted and excluded comparisons; the fitted $2s$ requirement is not extended to every row.
```
After:
```
separating fitted from non-fitted and excluded observations; the $2s$ requirement applies only to the 47 fitted loaded densities.
```

## `docs/scientific/latex/sections/mea_system_modeling_results.tex:75`

Before:
```
Outside the fitted density rows, calculated-minus-observed errors reach
```
After:
```
Among the densities not fitted, calculated-minus-observed errors reach
```

## `docs/scientific/latex/sections/mea_system_modeling_results.tex:80`

Before:
```
The four fitted heat-capacity errors, in source row order, are
```
After:
```
The four fitted heat-capacity errors, in the order of \cref{tab:residual-summary}, are
```

## `docs/scientific/latex/sections/mea_system_modeling_results.tex:111`

Before:
```
The 19 non-fitted Matin bicarbonate + carbonate total rows give
```
After:
```
The 19 non-fitted Matin bicarbonate + carbonate totals give
```

## `docs/scientific/latex/sections/mea_system_modeling_results.tex:135`

Before:
```
their different data, operators and fitting roles
```
After:
```
their different data, calculated quantities and fitting roles
```

## `docs/scientific/latex/sections/mea_system_modeling_results.tex:29`

Before:
```
Lower panels show all 210 densities, including compositions outside 30 wt\%,
```
After:
```
Lower panels show the restricted-bound fit for all 210 densities, including compositions outside 30 wt\%,
```

## `docs/scientific/latex/scripts/final_rerun_tables.py:180`

Before:
```
A7 objective operators. Rows partition eight disjoint groups and 307 quantities;
```
After:
```
A7 objective groups. The eight groups are disjoint and contain 307 quantities;
```

## `docs/scientific/latex/scripts/final_rerun_tables.py:180`

Before:
```
Scales retain their declared meaning; they are not uniformly measurement uncertainties.
```
After:
```
Scales are not uniformly measurement uncertainties.
```

## `docs/scientific/latex/scripts/final_rerun_tables.py:181`

Before:
```
'Operator'
```
After:
```
'Quantity'
```

## `docs/scientific/latex/scripts/final_rerun_tables.py:175`

Before:
```
' (row-specific)'
```
After:
```
' (per observation)'
```

## `docs/scientific/latex/scripts/final_rerun_tables.py:419`

Before:
```
VLE/density comparisons; density cohorts differ from this work
```
After:
```
VLE/density comparisons; density data sets differ from this work
```

## `docs/scientific/latex/scripts/final_rerun_tables.py:407`

Before:
```
.replace('cp_', r'$C_P$ ')
```
After:
```
.replace('cp_', r'$C_P$ ').replace('shomate', 'Shomate')
```

## `docs/scientific/latex/scripts/final_rerun_tables.py:317`

Before:
```
Costs sum disjoint fitted rows; quantity meanings and native units are in the objective table.
```
After:
```
Entry costs add to the total objective cost of 148.9; quantity definitions and units are in main-text Table 3.
```

## `docs/scientific/latex/scripts/final_rerun_tables.py:326`

Before:
```
These comparisons were not fitted but were seen during model development.
```
After:
```
These comparisons were not fitted but were seen during model development. The pressure/species subset is the 79 Jou and Hilliard pressures used in the pressure and species calculations, 47 of them fitted.
```

## `docs/scientific/latex/scripts/final_rerun_tables.py:357`

Before:
```
Paired phase-search summary.
```
After:
```
Phase-search summary for both fits.
```

## `docs/scientific/latex/scripts/final_rerun_tables.py:357`

Before:
```
Index 0 repeats index 41 at 318.15 K and loading 0.2556, with pressure rounded to 5918.5286 Pa; both count. Two-phase classifications include vapor.
```
After:
```
One 318.15 K state (loading 0.2556) is evaluated twice, once at its pressure rounded to 5918.5286 Pa; both evaluations are counted. Two-phase classifications include liquid--vapor equilibrium.
```

## `docs/scientific/latex/scripts/final_rerun_tables.py:374`

Before:
```
Mole fractions in declared order
```
After:
```
Mole fractions (order in caption)
```

## `docs/scientific/latex/scripts/final_rerun_tables.py:82`

Before:
```
    escaped = re.sub(r'(?<![\w.])[-+]?\d+(?:\.\d*)?[eE][-+]?\d+(?![\w.])', lambda m: '$' + scientific(m.group()) + '$', escaped)
```
After:
```
    escaped = re.sub(r'(?<![\w.-])-(?=\d)', r'\\textminus{}', escaped)
    escaped = re.sub(r'(?<![\w.])[-+]?\d+(?:\.\d*)?[eE][-+]?\d+(?![\w.])', lambda m: '$' + scientific(m.group()) + '$', escaped)
```

## `docs/scientific/latex/supplement.tex:55`

Before:
```
so overlapping pressure views are not additive.
```
After:
```
so the overlapping pressure sets are not additive.
```

## `docs/scientific/latex/supplement.tex:200`

Before:
```
the exact compiled ePC-SAFT Engine package will be provided to referees
```
After:
```
the compiled ePC-SAFT library used here will be provided to referees
```

## N9 `docs/scientific/latex/references.bib:19` (`RVYVQKSF`)

Before:
```
A Modified Electrolyte Non-Random Two-Liquid Model with Analytical Expression for Excess Enthalpy: {{Application}} to the {{MEA-H2O-{\ce{CO2}}}} System
```
After:
```
A Modified Electrolyte Non-Random Two-Liquid Model with Analytical Expression for Excess Enthalpy: {{Application}} to the {{MEA-{\ce{H2O}}-{\ce{CO2}}}} System
```

## N9 `docs/scientific/latex/references.bib:98` (`NL4W5CA6`)

Before:
```
Model of {{Vapor-Liquid Equilibria}} for {{Aqueous Acid Gas-Alkanolamine Systems}}. 2. {{Representation}} of {{H2S}} and {{{\ce{CO2}} Solubility}} in {{Aqueous MDEA}} and {{{\ce{CO2}} Solubility}} in {{Aqueous Mixtures}} of {{MDEA}} with {{MEA}} or {{DEA}}
```
After:
```
Model of {{Vapor-Liquid Equilibria}} for {{Aqueous Acid Gas-Alkanolamine Systems}}. 2. {{Representation}} of {{{\ce{H2S}}}} and {{{\ce{CO2}} Solubility}} in {{Aqueous MDEA}} and {{{\ce{CO2}} Solubility}} in {{Aqueous Mixtures}} of {{MDEA}} with {{MEA}} or {{DEA}}
```

## N9 `docs/scientific/latex/references.bib:141` (`E322TKPZ`)

Before:
```
Online {{NMR}} Spectroscopic Study of Species Distribution in {{MEA-H2O-{\ce{CO2}}}} and {{DEA-H2O-{\ce{CO2}}}}
```
After:
```
Online {{NMR}} Spectroscopic Study of Species Distribution in {{MEA-{\ce{H2O}}-{\ce{CO2}}}} and {{DEA-{\ce{H2O}}-{\ce{CO2}}}}
```

## N9 `docs/scientific/latex/references.bib:244` (`MMI98GID`)

Before:
```
Competitive {{H2S}}--{{{\ce{CO2}}}} Absorption in Reactive Aqueous Methyldiethanolamine Solution: {{Prediction}} with {{{ePC-SAFT}}}
```
After:
```
Competitive {{{\ce{H2S}}}}--{{{\ce{CO2}}}} Absorption in Reactive Aqueous Methyldiethanolamine Solution: {{Prediction}} with {{{ePC-SAFT}}}
```

## N9 `docs/scientific/latex/references.bib:375` (`9GBQCJNU`)

Before:
```
The Refined E-{{NRTL}} Model Applied to {{{\ce{CO2}}-H2O}}-Alkanolamine Systems
```
After:
```
The Refined E-{{NRTL}} Model Applied to {{{\ce{CO2}}-{\ce{H2O}}}}-Alkanolamine Systems
```

## N9 `docs/scientific/latex/references.bib:426` (`VDRXENRB`)

Before:
```
Liquid-{{Phase Composition Determination}} in {{{\ce{CO2}}-H2O-Alkanolamine Systems}}: {{An NMR Study}}
```
After:
```
Liquid-{{Phase Composition Determination}} in {{{\ce{CO2}}-{\ce{H2O}}-Alkanolamine Systems}}: {{An NMR Study}}
```

## N9 `docs/scientific/latex/references.bib:453` (`P9HDI8CX`)

Before:
```
Experimental {{Determination}} and {{Prediction}} of {{Gas Solubility Data}} for {{{\ce{CO2}}}} + {{H2O Mixtures Containing NaCl}} or {{KCl}} at {{Temperatures}} between 313 and 393 {{K}} and {{Pressures}} up to 10 {{MPa}}
```
After:
```
Experimental {{Determination}} and {{Prediction}} of {{Gas Solubility Data}} for {{{\ce{CO2}}}} + {{{\ce{H2O}} Mixtures Containing NaCl}} or {{KCl}} at {{Temperatures}} between 313 and 393 {{K}} and {{Pressures}} up to 10 {{MPa}}
```

## N9 `docs/scientific/latex/references.bib:586` (`MIWSMGMV`)

Before:
```
A New Model Combining Helmholtz Energy Equations of State with Excess {G}ibbs Energy Models to Describe Reactive Mixtures
```
After:
```
A New Model Combining {H}elmholtz Energy Equations of State with Excess {G}ibbs Energy Models to Describe Reactive Mixtures
```

## N9 `docs/scientific/latex/references.bib:681` (`UC2KB9PU`)

Before:
```
Modeling {{{\ce{CO2}}}} and {{H2S}} Solubilities in Aqueous Alkanolamine Solutions via an Extension of the Cubic-Two-State Equation of State
```
After:
```
Modeling {{{\ce{CO2}}}} and {{{\ce{H2S}}}} Solubilities in Aqueous Alkanolamine Solutions via an Extension of the Cubic-Two-State Equation of State
```

## N9 `docs/scientific/latex/references.bib:742` (`ZILDPWWE`)

Before:
```
Prediction of {{{\ce{CO2}}}} and {{H2S}} Solubility and Enthalpy of Absorption in Reacting {{N}}-Methyldiethanolamine /Water Systems with {{{ePC-SAFT}}}
```
After:
```
Prediction of {{{\ce{CO2}}}} and {{{\ce{H2S}}}} Solubility and Enthalpy of Absorption in Reacting {{N}}-Methyldiethanolamine /Water Systems with {{{ePC-SAFT}}}
```
