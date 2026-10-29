"""Reconstruct Hamborg Eq.21 from rounded Table 1; audit Table 16, not fit it."""
import csv
from pathlib import Path
import numpy as np

root = Path(__file__).resolve().parent
T = np.array([293., 303., 318., 333.])
y = np.array([-22.65, -21.95, -20.96, -20.04])
X = np.column_stack([1 / T, np.ones(4), np.log(T)])
a = np.linalg.lstsq(X, y, rcond=None)[0]
rows = list(csv.DictReader((root / 'hamborg-table-16.csv').open()))
assert [int(row['run']) for row in rows] == list(range(1, 25))
assert max(abs(X @ a - y)) < 0.001  # rounded correlation is internally consistent
residuals = []
for row in rows:
    t = float(row['T_K'])
    calculated = a[0] / t + a[1] + a[2] * np.log(t)
    residual = float(row['ln_K']) - calculated
    residuals.append(residual)
    row.update(reconstructed_ln_K=f'{calculated:.8f}',
               observed_minus_reconstructed_ln_K=f'{residual:.8f}',
               K_relative_difference_percent=f'{100 * np.expm1(residual):.6f}')
with (root / 'hamborg-correlation-residuals.csv').open('w') as f:
    writer = csv.DictWriter(f, fieldnames=rows[0], lineterminator="\n")
    writer.writeheader()
    writer.writerows(rows)
print('A, B, C:', a)
print('Table 1 residuals:', X @ a - y)
print('Table 16 mean, RMS, max absolute:', np.mean(residuals),
      np.sqrt(np.mean(np.square(residuals))), max(abs(np.array(residuals))))
