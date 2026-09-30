from pathlib import Path
import fit
fit.probe.RECORD = fit.RECORDS['0-0']
ids, starts = fit.starts('40-80', '0-0', 'S1')
lower, upper = (list(bounds) for bounds in zip(*fit.FORMS['S1'].values()))
stem = Path(__file__).resolve().parent / '0-0-S1-40-80C-28181e72'
fit.refit.main(['incumbent-R4-C', 'seed-1', 'seed-2'], ids, lower, upper, starts, stem, 80)
fit.add_domain_ends('40-80', stem)
