from numpy import exp, log, array
import numpy as np
from scipy.optimize import minimize, root
from scipy.interpolate import interp1d
from gekko import GEKKO
import matplotlib.pyplot as plt
import time
import pandas as pd
from matplotlib.animation import FuncAnimation, PillowWriter
from Density import density
from plot_export import save_plot


# From Akula Appendix of Model Development, Validation, and Part-Load Optimization of a
# MEA-Based Post-Combustion CO2 Capture Process Under SteadyState Flexible Capture Operation


def get_true_mol_frac(alpha, w_MEA, Tl):

    def solve_ChemEQ(guesses, Cl_0, Tl):

        Cl_CO2_0 = Cl_0[0]
        Cl_MEA_0 = Cl_0[1]
        Cl_H2O_0 = Cl_0[2]
        Cl_CO2 = guesses[0]
        Cl_MEA = guesses[1]
        Cl_H2O = guesses[2]
        Cl_MEAH = guesses[3]
        Cl_MEACOO = guesses[4]
        Cl_HCO3 = guesses[5]
        #
        a1, b1, c1, d1 = 234.2, -1434.4, -36.8, -.0074
        a2, b2, c2, d2 = 176.8, -991.2, -29.5, .0129
        #
        # a1, b1, c1, d1 = 233.4, -3410, -36.8, 0
        # a2, b2, c2, d2 = 176.72, -2909, -28.46, 0

        # a1, b1, c1, d1 = 233.4, -899.9, -37.5, 0
        # a2, b2, c2, d2 = 176.72, -1947.9, -28.2, 0

        K1 = np.exp(a1 + b1 / Tl + c1 * np.log(Tl) + d1 * Tl) / 2000 # kmol -> mol
        K2 = np.exp(a2 + b2 / Tl + c2 * np.log(Tl) + d2 * Tl) / 2000 # kmol -> mol
        # print(K1, K2)

        Kee1 = (Cl_MEAH * Cl_MEACOO) / (Cl_CO2 * Cl_MEA ** 2)  # carbamate
        Kee2 = (Cl_MEAH * Cl_HCO3) / (Cl_CO2 * Cl_MEA * Cl_H2O)  # bicarbonate
        #
        if Cl_0[0] > 3800:
            Cl_CO2_scale = 20
        else:
            Cl_CO2_scale = 5

        eq1 = Kee1 / 100 - K1 / 100
        eq2 = Kee2 / 100 - K2 / 100
        eq3 = Cl_CO2_0 / Cl_CO2_scale - (Cl_CO2 + Cl_MEACOO + Cl_HCO3) / Cl_CO2_scale
        eq4 = Cl_MEA_0 / 3000 - (Cl_MEA + Cl_MEAH + Cl_MEACOO) / 3000
        eq5 = Cl_H2O_0 / 10000 - (Cl_H2O + Cl_MEAH - Cl_MEACOO) / 10000
        eq6 = Cl_MEAH - (Cl_MEACOO + Cl_HCO3)

        return eq1, eq2, eq3, eq4, eq5, eq6

    def get_x(CO2_loading, w_MEA):
        MW_MEA = 61.084
        MW_H2O = 18.02

        x_MEA_unloaded = w_MEA / (MW_MEA / MW_H2O + w_MEA * (1 - MW_MEA / MW_H2O))
        x_H2O_unloaded = 1 - x_MEA_unloaded

        n_MEA = 100 * x_MEA_unloaded
        n_H2O = 100 * x_H2O_unloaded

        n_CO2 = n_MEA * CO2_loading
        n_tot = n_MEA + n_H2O + n_CO2
        x_CO2, x_MEA, x_H2O = n_CO2 / n_tot, n_MEA / n_tot, n_H2O / n_tot

        return x_CO2, x_MEA, x_H2O


    alpha_range = np.linspace(0.001, 1, 100)
    data = {
        'CO2_loading': [],
        'temperature': []
    }
    comp = ['CO2', 'MEA', 'H2O', 'MEAH^+', 'MEACOO^-', 'HCO3^-']
    for c in comp:
        data[c] = []
    guesses = np.array([1.32885319e-10, 4.85942087e3, 3.92196901e4, 4.95855464e1, 4.95482234e1, 3.73230850e-2])
    for i, a in enumerate(alpha_range):
        x = get_x(a, w_MEA)
        rho_mol_l, _, _ = density(Tl, x, 0)
        Cl_0 = [x[i] * rho_mol_l for i in range(len(x))]
        result = root(solve_ChemEQ, guesses, args=(Cl_0, Tl))
        Cl_true, solution = result.x, result.message

        guesses = Cl_true
        x_true = Cl_true / (sum(Cl_true))
        data['CO2_loading'].append(a)
        data['temperature'].append(Tl)
        for j, c in enumerate(comp):
            data[c].append(Cl_true[j])
    interp_dic = {}
    for c in comp:
        interp_dic[c] = interp1d(alpha_range, data[c])
    Cl_true_return = []
    for c in comp:
        Cl_true_return.append(float(interp_dic[c](alpha)))
    Cl_true_return = np.array(Cl_true_return)
    x_true_return = Cl_true_return / (sum(Cl_true_return))
    return np.array(x_true_return), Cl_true_return

# if __name__ == '__main__':
#     print(get_true_mol_frac(.3, .3, 273.15)[1])

if __name__ == '__main__':

    w_MEA = .3
    Tl = 273.15
    colors = ['tab:green', 'tab:blue', 'tab:orange', 'tab:olive', 'tab:red', 'tab:cyan', 'tab:purple', 'tab:brown',
              'tab:gray']
    comp = ['$CO_2$', 'MEA', '$H_2O$', '$MEAH^+$', '$MEACOO_-$', '$HCO_3^-$', '$CO_3^{2-}$', '$H_3O^+$', '$OH^-$']

    fig, ax = plt.subplots(figsize=(10, 10))
    x_true_arr = []
    alpha = np.linspace(.001, 1.0, 100)
    for a in alpha:
        output = get_true_mol_frac(a, w_MEA, Tl)[0]
        x_true_arr.append(output)
    x_true_arr = np.array(x_true_arr)
    x_true_arr = x_true_arr.T

    for c, x_true, color in zip(comp, x_true_arr, colors):
        if c == '$H_2O$':
            continue
        ax.semilogy(alpha, x_true, '--', color = color, label=c)
    minimum = int(np.log10(min(x_true_arr[0])))
    minimum = -10
    ax.legend(loc='lower center')
    x_range = np.linspace(0, 1, 11)
    y_range = np.logspace(minimum, 0, (minimum*-1)+1)
    ax.set_xlim(x_range[0], x_range[-1])
    ax.set_ylim(y_range[0], y_range[-1])
    ax.set_xticks(x_range)
    ax.set_yticks(y_range)

    plt.tick_params(labelsize=12)
    save_plot(fig, __file__)


# if __name__ == '__main__':
#     alpha = np.linspace(0.01, 1, 100)
#     w_MEA = .3
#     T_range = np.linspace(0, 120, 13)
#
#     fig, ax = plt.subplots(figsize=(10, 10))
#
#
#     def animate(T):
#         ax.clear()
#
#         Tl = T + 273.15
#         x_true_arr = []
#         for i, a in enumerate(alpha):
#             output = get_true_mol_frac(a, w_MEA, Tl)
#             # print(output)
#             x_true_arr.append(output)
#         x_true_arr = np.array(x_true_arr)
#         x_true_arr = x_true_arr.T
#         comp = ['CO2', 'MEA', 'H2O', 'MEAH^+', 'MEACOO^-', 'HCO3^-']
#
#         for c, x_true in zip(comp, x_true_arr):
#             if c == 'H2O':
#                 continue
#             # print(x_true)
#             ax.semilogy(alpha, x_true, '--', label=c)
#         ax.legend(loc='lower center')
#         ax.set_xlim(0, 1)
#         ax.set_ylim(1e-10, .2)
#         ax.set_title(Tl)
#
#
#     animation = FuncAnimation(fig, animate, frames=range(0, 120 + 1, 5))
#
#     plt.tick_params(labelsize=12)
#     plt.show()
