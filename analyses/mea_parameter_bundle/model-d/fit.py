"""#121 model D (owner decisions 20-22): C_src's refit with wider bounds (S1), then 1/T slopes (S2) only if S1 fails.

Usage: fit.py RULE BORN FORM [START ...]   RULE: old or 40-80; BORN: 1-1 or 0-0; FORM: S1 or S2
       fit.py --domain-ends RULE STEM       k(T) at 293.15, 353.15 and 393.15 K for every start of STEM-multistart.json
RULE old: decisions 20-22, all 180 refit rows (the #107 gates); outputs BORN-FORM-*.
RULE 40-80: decision 23, pCO2 rows above 80 degC leave the objective (160 rows); outputs BORN-FORM-40-80C-*.
BORN 1-1: SSM+DS, c_shell = c_dielectric = 1, the base record probe.RECORD as loaded (Figiel 2025).
BORN 0-0: original Born, c_shell = c_dielectric = 0 set explicitly (candidate.py --born-0-0).
S1: C_src's five coordinates; carbamate-, HCO3-- and MEAH+-water k_ij within +-0.5, MEAH+-water 1/T slope within
+-1000 K (T_ref 313.15 K), MEAH+-MEACOO- k_ij within [-1, 1]. S2: S1 plus 1/T slopes (T_ref 313.15 K, +-1000 K) on
carbamate-water, HCO3--water and MEAH+-MEACOO-. Rows, weights, R4, fitter and limits are refit.py's.
Starts: C_src's (pre-refit, incumbent-R4 C optimum) and C_src's optimum, plus numpy default_rng(1) and (2) uniform
in the box; S2 also starts from its Born form's S1 optimum, and rule 40-80 also from the old-rule optimum. Writes
STEM-multistart.json, -iterations.csv and -jacobian.csv here. Admissible: k(T) < 1 at both ends of the rule's domain
(old 293.15-393.15 K, 40-80 293.15-353.15 K) for every pair with a slope; an inadmissible start is reported, not run.
"""
import json
import sys
from pathlib import Path

import numpy as np

HERE = Path(__file__).parent
sys.path.insert(0, str(HERE.parent / 'calibration-misfit'))
import probe  # noqa: E402
import refit  # noqa: E402
import candidate  # noqa: E402

SLOPE = '/reciprocal_temperature_slope'  # appended to a pair's k_ij identity
CARBAMATE_W, MEAH_W, HCO3_W, CATION_ANION = refit.IDS[:4]
S1 = {CARBAMATE_W: (-0.5, 0.5), MEAH_W: (-0.5, 0.5), HCO3_W: (-0.5, 0.5), CATION_ANION: (-1.0, 1.0),
      MEAH_W + SLOPE: (-1000.0, 1000.0)}
assert list(S1) == refit.IDS
S2 = {**S1, **{k + SLOPE: (-1000.0, 1000.0) for k in (CARBAMATE_W, HCO3_W, CATION_ANION)}}
FORMS = {'S1': S1, 'S2': S2}
RECORDS = {'1-1': probe.RECORD, '0-0': candidate.BORN_00}
T_REF, TEMPERATURES = 313.15, (293.15, 353.15, 393.15)
RULES = {'old': {'stem': '{born}-{form}', 'pco2_max_c': None, 'domain': (293.15, 393.15)},
         '40-80': {'stem': '{born}-{form}-40-80C', 'pco2_max_c': 80, 'domain': (293.15, 353.15)}}
C_SRC = json.loads((HERE.parent / 'calibration-misfit/refit-C-multistart.json').read_text())


def domain_ends(ids, values, temperatures=TEMPERATURES):
    """k(T) = k + b (1/T - 1/T_ref) at each temperature, for every pair with a 1/T slope."""
    x = dict(zip(ids, values))
    return {k: [x[k] + x[k + SLOPE] * (1 / t - 1 / T_REF) for t in temperatures] for k in ids if k + SLOPE in x}


def admissible(ids, values, rule):
    return all(k < 1 for ends in domain_ends(ids, values, RULES[rule]['domain']).values() for k in ends)


def best(stem):
    record = json.loads(Path(f'{stem}-multistart.json').read_text())
    return min((v for k, v in record.items() if k != 'provenance' and v['usable']), key=lambda v: v['final_cost'])


def starts(rule, born, form):
    ids, (lower, upper) = list(FORMS[form]), zip(*FORMS[form].values())
    pad = [0.0] * (len(ids) - len(S1))  # new slopes start at 0
    out = {'C_src': C_SRC['pre-refit']['fitted'] + pad,
           'pre-refit': refit.STARTS['pre-refit'] + pad, 'incumbent-R4-C': refit.STARTS['incumbent-R4-C'] + pad}
    if rule != 'old':
        out['old-rule'] = best(HERE / RULES['old']['stem'].format(born=born, form=form))['fitted']
    if form == 'S2':
        out['S1'] = best(HERE / RULES[rule]['stem'].format(born=born, form='S1'))['fitted'] + pad
    out |= {f'seed-{n}': list(np.random.default_rng(n).uniform(list(lower), list(upper))) for n in (1, 2)}
    refused = {k: domain_ends(ids, v) for k, v in out.items() if not admissible(ids, v, rule)}
    for k in refused:  # the Engine refuses a record with k(T) > 1 at a domain end
        print(f'{born} {form} start {k} not run: inadmissible, k(T) at domain ends {refused[k]}', flush=True)
    return ids, {k: v for k, v in out.items() if k not in refused}


def main(rule, born, form, names):
    probe.RECORD = RECORDS[born]
    ids, points = starts(rule, born, form)
    lower, upper = (list(b) for b in zip(*FORMS[form].values()))
    stem = HERE / RULES[rule]['stem'].format(born=born, form=form)
    refit.main(names, ids, lower, upper, points, stem, RULES[rule]['pco2_max_c'])
    add_domain_ends(rule, stem)


def add_domain_ends(rule, stem):
    path = Path(f'{stem}-multistart.json')
    record = json.loads(path.read_text())
    ids = record['provenance']['parameters']
    for name, v in record.items():
        if name != 'provenance':
            v['k_at_temperatures_k'] = {'temperatures_k': TEMPERATURES, **domain_ends(ids, v['fitted'])}
            v.pop('k_at_domain_ends', None)
            v['admissible'] = admissible(ids, v['fitted'], rule)
            v['admissibility_domain_k'] = RULES[rule]['domain']
    path.write_text(json.dumps(record, indent=1) + '\n')


if __name__ == '__main__':
    if sys.argv[1] == '--domain-ends':
        add_domain_ends(sys.argv[2], sys.argv[3])
    else:
        main(sys.argv[1], sys.argv[2], sys.argv[3], sys.argv[4:])
