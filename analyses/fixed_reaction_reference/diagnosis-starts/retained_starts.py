"""Historical #429 probes of the retained #440 start design."""
from starts import HERE as HERE, Starts, np as np, refit as refit
from refit import OUT as OUT, r as r, reg as reg

refit.a.study.reuse.bind_wheel()
r.verify()
MANIFEST = r.read(OUT/'MDEA/manifest.json.gz')
POINT = MANIFEST['start_A_declaration']
RUN = refit.configured('MDEA', 'diagnosis-starts')[0]
STARTS = Starts(RUN, POINT)
ROWS, NATIVE = STARTS.rows, STARTS.native
LOWER, UPPER, ORIGIN = STARTS.lower, STARTS.upper, STARTS.origin
at, vector, census = STARTS.at, STARTS.vector, STARTS.census
