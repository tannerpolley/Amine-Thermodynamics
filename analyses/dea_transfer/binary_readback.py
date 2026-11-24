"""Reduce the retained #425 fits and compare the residuals from each start."""
from pathlib import Path
import sys

import matplotlib.pyplot as plt
import numpy as np

from binary_refit import A_OLD, B_PROBE, CAI, GROUPS, HEAT, REFERENCE, SCALE, T_REF, composition, evaluate, residuals, rows, with_binary
from excess_enthalpy import mixture
from f2_carbamate import dump, read


def report(out):
    doc = read(REFERENCE/'selection.json')['chosen']['parameters']['parameters']
    inputs = list(rows())
    fitted = [r for r in inputs if r['fitted']]
    fig, axes = plt.subplots(3, 2, figsize=(9, 8), sharex='col', layout='constrained')
    for name, a, b in [('#413', A_OLD, 0), ('#410', A_OLD, B_PROBE)]:
        dump(out/f'{name[1:]}-comparison.json', evaluate(with_binary(doc, a, b), inputs, readback=True))
    for case, path in enumerate(sorted(out.glob("*/fit.json"))):
        fit = read(path)
        a, b = fit['a'], fit['b']
        model = mixture(with_binary(doc, a, b))
        temperatures = (313.15, 365.15, min(r['T'] for r in fitted if r['group']==CAI),
                        max(r['T'] for r in fitted if r['group']==CAI))
        law = []
        for T in temperatures:
            k = a+b*(1/T-1/T_REF)
            state = model.state(T, rho=10000, x=composition(.5))
            constant = mixture(with_binary(doc,k,0)).state(T,rho=10000,x=composition(.5))
            law.append(dict(T=T, expected_k=k, dispersion_difference=state.dispersion-constant.dispersion))
        assert max(abs(row['dispersion_difference']) for row in law)<1e-12
        def slope(step):
            return np.column_stack([(residuals(evaluate(with_binary(doc, *(np.array([a,b])+d)),fitted))-
                                     residuals(evaluate(with_binary(doc, *(np.array([a,b])-d)),fitted)))/(2*step)
                                    for d in np.diag(SCALE*step)])
        singular = [np.linalg.svd(slope(h),compute_uv=False).tolist() for h in (1e-4,5e-5)]
        dump(path.with_name('readback.json'), dict(bound_law=law, scaled_singular_values=singular))
        for i, group in enumerate(GROUPS):
            block = [r for r in fit['rows'] if r['group']==group and r['fitted']]
            for j, field in enumerate(('x', 'T')):
                axes[i,j].scatter([r[field] for r in block], [r['predicted']-r['observed'] for r in block],
                                  label=path.parent.name, s=19, alpha=.8, marker=('o', '^', 's', '+')[case],
                                  color=('#0072B2', '#D55E00', '#009E73', '#CC79A7')[case])
    for i, group in enumerate(GROUPS):
        axes[i,0].set_ylabel(f"{group}\nResidual ({'J/mol' if group==HEAT else 'kPa'})")
        for axis in axes[i]:
            axis.axhline(0, color='.55', linewidth=.7)
    axes[-1,0].set_xlabel('Liquid water mole fraction')
    axes[-1,1].set_xlabel('Temperature (K)')
    axes[0,1].legend(fontsize='small')
    fig.savefig(out/'binary-residuals.png', dpi=170)


if __name__=='__main__':
    report(Path(sys.argv[1]))
