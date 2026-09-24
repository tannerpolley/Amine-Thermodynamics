"""Identifiability of a refit from its logged forward-difference Jacobian.

Usage: identifiability.py LOG.jsonl LINE NAMES...
LINE is the 1-based log line of the base point; the next len(NAMES) lines are its one-coordinate
steps (refit.py's Jacobian order). Scaled calibration residuals as in refit.py. Writes
refit-A-identifiability.csv: estimate, standard error, correlations, singular values.
"""
import csv
import json
import sys
from pathlib import Path
import numpy as np

from refit import is_validation, residuals


def table(states):
    return {(r['identity'], t): sc for r in states if not is_validation(r)
            for _, t, sc, _ in residuals(r) or []}


def main(log, line, names):
    lines = [json.loads(text) for text in open(log)][line - 1:line + len(names)]
    tabs = [table(d['states']) for d in lines]
    keys = sorted(set.intersection(*(set(t) for t in tabs)))
    x = [np.array(d['x']) for d in lines]
    f0 = np.array([tabs[0][k] for k in keys])
    J = np.array([(np.array([tabs[i + 1][k] for k in keys]) - f0) / (x[i + 1][i] - x[0][i])
                  for i in range(len(names))]).T
    s2 = f0 @ f0 / (len(keys) - len(names))
    cov = np.linalg.inv(J.T @ J) * s2
    se = np.sqrt(np.diag(cov))
    corr = cov / np.outer(se, se)
    sv = np.linalg.svd(J / np.linalg.norm(J, axis=0), compute_uv=False)
    out = Path(__file__).with_name('refit-A-identifiability.csv')
    with out.open('w', newline='') as h:
        w = csv.writer(h)
        w.writerow(['parameter', 'estimate', 'standard_error', *[f'corr[{n}]' for n in names],
                    'normalized_singular_value', 'n_residuals', 'residual_variance', 'log_line'])
        for i, n in enumerate(names):
            w.writerow([n, x[0][i], se[i], *corr[i], sv[i], len(keys), s2, line])
    print(open(out).read())


if __name__ == '__main__':
    main(sys.argv[1], int(sys.argv[2]), sys.argv[3:])
