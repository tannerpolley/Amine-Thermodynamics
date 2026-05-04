from numpy import exp, log, array
import numpy as np
from scipy.optimize import minimize, root
from scipy.interpolate import interp1d
from gekko import GEKKO
import matplotlib.pyplot as plt
import time
import pandas as pd
from matplotlib.animation import FuncAnimation, PillowWriter
import importlib.util
import pathlib
from Density import density
from convex_optimization_gekko import get_x_guess, solve_ChEq
from plot_export import save_plot


def chemical_equilibrium(Fl, Tl):

    Fl = np.append(Fl, np.array([0, 0, 0]))
    Fl_0_T = sum(Fl)
    x_0 = [Fl[i] / Fl_0_T for i in range(len(Fl))]

    # Constants and initial guesses provided

    a1, b1, c1, d1 = 234.3, -1204.1, -36.9, -0.0078
    a2, b2, c2, d2 = 176.7, -1582.5, -29.2, 0.0125

    # Compute log(K) values
    log_K1 = a1 + b1 / Tl + c1 * np.log(Tl) + d1 * Tl
    log_K2 = a2 + b2 / Tl + c2 * np.log(Tl) + d2 * Tl
    log_K = np.array([log_K1, log_K2])  # K_i values

    v_ij = np.array([
        [-1, -2, 0, 1, 1, 0],
        [-1, -1, -1, 1, 0, 1]
    ])

    s_ij = np.array([
        [1, 0, 0, 0, 1, 1],
        [0, 1, 0, 1, 1, 0],
        [0, 0, 1, 1, -1, 0],
        [0, 0, 0, 1, -1, -1],
    ])

    x_guesses = get_x_guess(x_0, log_K, v_ij)[0]

    scales = np.array(x_guesses)
    guesses_scaled = x_guesses / scales

    def root_solve(guesses_scaled, x_0, scales):
        guesses = guesses_scaled * scales
        x_CO2_0 = x_0[0]
        x_MEA_0 = x_0[1]
        x_H2O_0 = x_0[2]
        x_CO2 = guesses[0]
        x_MEA = guesses[1]
        x_H2O = guesses[2]
        x_MEAH = guesses[3]
        x_MEACOO = guesses[4]
        x_HCO3 = guesses[5]

        x = guesses

        #
        # Kee1 = float(np.prod([x[i] ** v_ij[0, i] for i in range(len(x))]))
        # Kee2 = float(np.prod([x[i] ** v_ij[1, i] for i in range(len(x))]))
        #
        # eq1 = (Kee1 - np.exp(log_K[0])) / Kee1
        # eq2 = (Kee2 - np.exp(log_K[1])) / Kee2
        # eq3 = (x_CO2_0 - (x_CO2 + x_MEACOO + x_HCO3)) / x_CO2_0
        # eq4 = (x_MEA_0 - (x_MEA + x_MEAH + x_MEACOO)) / x_MEA_0
        # eq5 = (x_H2O_0 - (x_H2O + x_MEAH - x_MEACOO)) / x_H2O_0
        # eq6 = (x_MEAH - (x_MEACOO + x_HCO3)) / x_MEAH
        # eqs = np.array([eq1, eq2, eq3, eq4, eq5, eq6])

        # linear mass-balance constraints
        eqs = []
        for i, log_k_eq_i in enumerate(log_K):
            Kee_i = 1
            for j, xj in enumerate(x):
                # build a pure-Gekko linear combination
                Kee_i *= x[j] ** v_ij[i, j]

            eqs.append((Kee_i - np.exp(log_k_eq_i)) / Kee_i)

        for i in range(len(s_ij)):
            sum_i = np.sum([x[j] * s_ij[i, j] for j in range(len(x_0))])
            if i < 3:
                eqs.append((x_0[i] - sum_i) / x_0[i])
            else:
                eqs.append((x_0[i] - sum_i) / (x[3] * s_ij[i, 3]))


        return eqs

    result = root(root_solve, guesses_scaled, args=(x_0, scales), tol=1e-10)

    x_true_scaled, solution, success = result.x, result.message, result.success

    # print(root_solve(x_true_scaled, x_0, scales))

    x_true_2 = x_true_scaled * scales

    # print(x_true)
    #
    x_true = solve_ChEq(x_0, guesses_scaled, log_K, v_ij, s_ij, scales)

    print(x_true)
    print(x_true_2)

    return x_true


def get_true_mol_frac(alpha, w_MEA_unloaded, Tl):

    MW_MEA_MW_H2O = .06108/.01802

    # Liquid Calculations
    Fl_T = 1 # doesnt matter

    x_MEA_unloaded = w_MEA_unloaded / (MW_MEA_MW_H2O + w_MEA_unloaded * (1 - MW_MEA_MW_H2O))
    x_H2O_unloaded = 1 - x_MEA_unloaded

    Fl_MEA_b = Fl_T * x_MEA_unloaded
    Fl_H2O_b = Fl_T * x_H2O_unloaded

    Fl_CO2_b = Fl_MEA_b * alpha
    Fl = np.array([Fl_CO2_b, Fl_MEA_b, Fl_H2O_b])

    return chemical_equilibrium(Fl, Tl)

if __name__ == '__main__':

    w_MEA = .3
    Tl = 273.15
    colors = ['tab:green', 'tab:blue', 'tab:orange', 'tab:olive', 'tab:red', 'tab:cyan', 'tab:purple', 'tab:brown',
              'tab:gray']
    comp = ['$CO_2$', 'MEA', '$H_2O$', '$MEAH^+$', '$MEACOO_-$', '$HCO_3^-$', '$CO_3^{2-}$', '$H_3O^+$', '$OH^-$']

    fig, ax = plt.subplots(figsize=(10, 10))
    x_true_arr = []
    alpha = np.linspace(0.001, 1.0, 51)
    for a in alpha:
        # get_true_mol_frac(a, w_MEA, Tl)
        output = get_true_mol_frac(a, w_MEA, Tl)
        # print(a, output)
        x_true_arr.append(output)
    x_true_arr = np.array(x_true_arr)
    x_true_arr = x_true_arr.T


    for c, x_true, color in zip(comp, x_true_arr, colors):
        if c == '$H_2O$':
            continue
        ax.semilogy(alpha, x_true, '--', color = color, label=c)
    minimum = np.floor(np.log10(min(x_true_arr[0])))
    ax.legend(loc='lower center')
    x_range = np.linspace(0, max(alpha), 11)
    y_range = np.logspace(minimum, 0, int(-minimum + 1))
    ax.set_xlim(x_range[0], x_range[-1])
    ax.set_ylim(y_range[0], y_range[-1])
    ax.set_xticks(x_range)
    ax.set_yticks(y_range)

    plt.tick_params(labelsize=12)
    save_plot(fig, __file__)
