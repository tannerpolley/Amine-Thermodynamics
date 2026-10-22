"""Recompute ARD, pressure basis, and reaction/feed invariants from retained rows."""
import ast
import csv
import hashlib
import json
import math
from pathlib import Path

RESULTS = Path(__file__).resolve().parent / 'results'


def ermatchkov_scopes(rows, molar_mass):
    """CO2-free solvent mass fraction from mol/kg water and kg/mol MDEA."""
    fractions = [float(r['m_mdea']) * molar_mass / (1 + float(r['m_mdea']) * molar_mass) for r in rows]
    scopes = {}
    for name, within in (('within_scope', True), ('above_49_mass_percent', False)):
        subset = [(r, w) for r, w in zip(rows, fractions) if (w <= .49) == within]
        solved = [r for r, _ in subset if r['success'] == 'True']
        scopes[name] = dict(rows=len(subset), solved=len(solved),
            unsolved_rows=[int(r['row']) for r, _ in subset if r['success'] != 'True'],
            maximum_MDEA_mass_percent=100 * max(w for _, w in subset),
            ARD_percent_solved_rows=100 * sum(abs(1-float(r['p_calc'])/float(r['p_exp'])) for r in solved)/len(solved)
            if solved else None)
    return scopes


def main():
    report = json.loads((RESULTS / 'refit-summary.json').read_text())
    parameters = json.loads((RESULTS / 'fitted-parameters.json').read_text())
    molar_mass = next(c['fixed']['molar_mass']['value']['magnitude'] for c in parameters['components']
                      if c['component_id'] == 'methyldiethanolamine')
    cases = {'reading-a-reproduction-rows.csv': json.loads((RESULTS / 'reading-a-reproduction-summary.json').read_text()),
             'constant-start-kuranov.csv': report['constant_start'], 'fitted-kuranov.csv': report['fit']['kuranov'],
             'fitted-hsieh-quadratic-kuranov.csv': report['permittivity_sensitivity']}
    cases.update({'ermatchkov-'+name+'.csv': values for name, values in report['ermatchkov'].items()})
    checks = {}
    for filename, summary in cases.items():
        path = RESULTS / filename
        with path.open() as handle:
            rows = list(csv.DictReader(handle))
        assert len(rows) == summary['rows'] and len({r['row'] for r in rows}) == len(rows)
        solved = [r for r in rows if r['success'] == 'True']
        assert len(solved) == summary['solved'] == len(rows), filename
        ard = 100 * sum(abs(1-float(r['p_calc'])/float(r['p_exp'])) for r in solved)/len(rows)
        assert abs(ard-summary['ARD_percent_solved_rows']) < 1e-10, filename
        errors = dict(charge=0., liquid_sum=0., vapor_sum=0., loading=0., water_to_mdea=0., partial_pressure=0.)
        for r in solved:
            x, y = (ast.literal_eval(r[key]) for key in ('x_liquid', 'y_vapor'))
            assert all(math.isfinite(v) and v >= 0 for v in x+y) and float(r['p_calc']) > 0
            values = dict(charge=abs(x[3]-x[4]-2*x[5]+x[6]-x[7]), liquid_sum=abs(sum(x)-1),
                vapor_sum=abs(sum(y)-1), loading=abs((x[2]+x[4]+x[5])/(x[1]+x[3])-float(r['m_co2'])/float(r['m_mdea'])),
                water_to_mdea=abs((x[0]+x[4]+x[5]+x[7])/(x[1]+x[3])/(1/.01801528/float(r['m_mdea']))-1))
            if 'p_total_Pa' in r:
                values['partial_pressure'] = abs(float(r['p_calc'])/(float(r['p_total_Pa'])*y[2])-1)
            for key, value in values.items():
                errors[key] = max(errors[key], value)
        assert max(errors.values()) < 1e-12, (filename, errors)  # roundoff check on these dimensionless invariants
        checks[filename] = dict(rows=len(rows), ARD_percent=ard, maximum_invariant_errors=errors,
                               sha256=hashlib.sha256(path.read_bytes()).hexdigest())
        if filename.startswith('ermatchkov-'):
            scopes = ermatchkov_scopes(rows, molar_mass)
            assert scopes == summary['concentration_scopes'], filename
            assert [s['rows'] for s in scopes.values()] == [88, 13], filename
            assert all(s['solved'] == s['rows'] for s in scopes.values()), filename
            checks[filename]['concentration_scopes'] = scopes
        if filename == 'fitted-kuranov.csv':
            checks[filename]['max_relative_difference_from_native_fit'] = max(abs(float(r['p_calc'])/p-1)
                for r, p in zip(rows, report['fit']['predictions_Pa']))
            checks[filename]['replayed_log_pressure_cost'] = .5*sum(math.log(float(r['p_calc'])/float(r['p_exp']))**2 for r in rows)
    assert report['fit']['pass_10_9_percent'] == (checks['fitted-kuranov.csv']['ARD_percent'] < 10.9)
    (RESULTS / 'numerical-checks.json').write_text(json.dumps(checks, indent=1, allow_nan=False)+'\n')
    print(json.dumps(checks, indent=1))


if __name__ == '__main__':
    main()
