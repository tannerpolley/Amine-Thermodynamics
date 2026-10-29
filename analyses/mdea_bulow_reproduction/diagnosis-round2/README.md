# Bülow convention diagnosis, round 2

The [notebook](notebook.qmd) owns the results, methods, uncertainty and limits.
Seven expressible single-convention probes leave the five complete-isotherm
reproduction windows unmet. Corrected Figure 4 model lines replace the withdrawn
marker extraction from round 1. Evidence type: numerical diagnosis.

`probe.py` reuses the primary solver on 63 rows and records the four prohibited
retries in every 67-row output. `digitize.py` masks markers before tracing all
four Figure 4 model curves. `compare.py` compares retained pressures and curves;
`present.py` builds figures and the notebook without running the model.
`verify.py` checks source hashes, the unchanged primary result, qualification
counts and marker-crossing interpolation errors. `input-documents.json.gz`
retains all isothermal declarations, including the four unused row declarations;
no output implies that those four rows were solved.

Independent scientific review remains open. No interpretation is adopted.
