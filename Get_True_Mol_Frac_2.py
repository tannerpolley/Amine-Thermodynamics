from numpy import exp, log, array
import numpy as np
from scipy.optimize import minimize, root
from ePC_SAFT_properties import prop_dic
from scipy.interpolate import interp1d
from gekko import GEKKO
import matplotlib.pyplot as plt
import time
import pandas as pd
from matplotlib.animation import FuncAnimation, PillowWriter
from Get_True_Mol_Frac import get_true_mol_frac
from pcsaft import pcsaft_fugcoef, flashTQ, pcsaft_den


def liquid_density(Tl, x):
    x_CO2, x_MEA, x_H2O = x

    MWs_l = np.array([44.01, 61.08, 18.02]) / 1000  # kg/mol

    MWT_l = sum([x[i] * MWs_l[i] for i in range(len(x))])

    a1, b1, c1 = [-5.35162e-7, -4.51417e-4, 1.19451]
    a2, b2, c2 = [-3.2484e-6, 0.00165, 0.793]

    V_MEA = MWs_l[1] * 1000 / (a1 * Tl ** 2 + b1 * Tl + c1)  # mL/mol
    V_H2O = MWs_l[2] * 1000 / (a2 * Tl ** 2 + b2 * Tl + c2)  # mL/mol

    # a, b, c, d, e = df_param['molar_volume'].values()
    a, b, c, d, e = 10.57920122, -2.020494157, 3.15067933, 192.0126008, -695.3848617

    V_CO2 = a + (b + c * x_MEA) * x_MEA * x_H2O + (d + e * x_MEA) * x_MEA * x_CO2

    V_l = V_CO2 * x_CO2 + x_MEA * V_MEA + x_H2O * V_H2O  # Liquid Molar Volume (mL/mol)
    V_l = V_l * 1e-6  # Liquid Molar Volume (mL/mol --> m3/mol)

    rho_mol_l = V_l ** -1  # Liquid Molar Density (m3/mol --> mol/m3)
    rho_mass_l = rho_mol_l * MWT_l  # Liquid Mass Density (mol/m3 --> kg/m3)

    return rho_mol_l, rho_mass_l


# From Akula Appendix of Model Development, Validation, and Part-Load Optimization of a
# MEA-Based Post-Combustion CO2 Capture Process Under SteadyState Flexible Capture Operation

def get_true_mol_frac_2(alpha, w_MEA, Tl):
    def solve_ChemEQ(guesses, x_0, Tl, i):

        x_CO2_0 = x_0[0]
        x_MEA_0 = x_0[1]
        x_H2O_0 = x_0[2]
        x_CO2 = guesses[0]
        x_MEA = guesses[1]
        x_H2O = guesses[2]
        x_MEAH = guesses[3]
        x_MEACOO = guesses[4]
        x_HCO3 = guesses[5]

        x = np.array([x_CO2, x_MEA, x_H2O, x_MEAH, x_MEACOO, x_HCO3])
        v1 = [-1, -2, 0, 1, 1, 0]
        v2 = [-1, -1, -1, 1, 0, 1]

        if i == 0:
            γ = np.array([1, 1, 1, 1, 1, 1])
        else:
            param_all = {}
            for prop in prop_dic['H2O'].keys():
                param_all[prop] = np.array([])
            for c in prop_dic.keys():
                for prop in prop_dic[c].keys():
                    param_all[prop] = np.append(param_all[prop], prop_dic[c][prop])
            kij_CO2_MEA = .16
            kij_CO2_H2O = .13
            kij_MEA_H2O = -.18

            # 6716.607003231374
            # 52129.681209827584

            param_all['dielc'] = 75
            param_all['k_ij'] = np.array([
                [0.0, kij_CO2_MEA, kij_CO2_H2O, 0., 0., 0.],
                [kij_CO2_MEA, 0.0, kij_MEA_H2O, 0., 0., 0.],
                [kij_CO2_H2O, kij_MEA_H2O, 0.0, 0., 0., 0.],
                [0., 0., 0., 0., 0., 0.],
                [0., 0., 0., 0., 0., 0.],
                [0., 0., 0., 0., 0., 0.]
            ])
            # print(x)
            # P, x, y = flashTQ(t=Tl, x=x, q=0, params=prop_dic_2)
            # print(P)
            P = 101325
            x = [xi/sum(x) for xi in x]

            rho = pcsaft_den(t=Tl, p=P, x=x, params=param_all)
            fug_coef_1 = pcsaft_fugcoef(Tl, rho, x, param_all)

            fug_coef_2 = []
            for c in prop_dic.keys():
                param_prop = {}
                if c != 'H2O':
                    for prop in prop_dic[c].keys():
                        if prop == 'z':
                            if "^" not in c:
                                continue
                        param_prop[prop] = np.array([prop_dic['H2O'][prop], prop_dic[c][prop]])

                    if "^" in c:
                        param_prop['dielc'] = 75
                    #
                    param_prop['k_ij'] = np.array([[0., 0.],
                                                  [0., 0.]])
                    # print(c, param_prop)

                    inf_dil = 1e-10
                    x_temp = np.array([1. - inf_dil, inf_dil])
                    rho = pcsaft_den(Tl, P, x_temp, param_prop)
                    fug_coef_c = pcsaft_fugcoef(Tl, rho, x_temp, param_prop)[1]
                    fug_coef_2.append(fug_coef_c)
                else:
                    for prop in prop_dic[c].keys():
                        if prop == 'z':
                            continue
                        param_prop[prop] = np.array([prop_dic[c][prop]])
                        x_temp = np.array([1.])

                    rho = pcsaft_den(Tl, P, x_temp, param_prop)
                    fug_coef_c = pcsaft_fugcoef(Tl, rho, x_temp, param_prop)[0]
                    fug_coef_2.append(fug_coef_c)
                # print(c, fug_coef_c)
            fug_coef_2 = np.array(fug_coef_2)
            # print('φ', fug_coef_2)
            γ = fug_coef_1 / fug_coef_2

        # print('γ', γ)
        a = x * γ

        a1, b1, c1, d1 = 234.2, -1434.4, -36.8, -.0074
        a2, b2, c2, d2 = 176.8, -991.2, -29.5, .0129

        # a1, b1, c1, d1 = 233.4, -3410, -36.8, 0
        # a2, b2, c2, d2 = 176.72, -2909, -28.46, 0

        # a1, b1, c1, d1 = 233.4, -899.9, -37.5, 0
        # a2, b2, c2, d2 = 176.72, -1947.9, -28.2, 0

        K1 = np.exp(a1 + b1 / Tl + c1 * np.log(Tl) + d1 * Tl)
        K2 = np.exp(a2 + b2 / Tl + c2 * np.log(Tl) + d2 * Tl)

        Kee1 = 1
        for i in range(len(x)):
            Kee1 *= a[i] ** v1[i]
        Kee2 = 1
        for i in range(len(x)):
            Kee2 *= a[i] ** v2[i]

        x_CO2_scale = 1
        x_MEA_scale = 1

        eq1 = Kee1 - K1
        eq2 = Kee2 - K2
        eq3 = x_CO2_0 / x_CO2_scale - (x_CO2 + x_MEAH) / x_CO2_scale
        eq4 = x_MEA_0 / x_MEA_scale - (x_MEA + x_MEAH + x_MEACOO) / x_MEA_scale
        eq5 = x_H2O_0 - (x_H2O + x_MEAH - x_MEACOO)
        eq6 = x_MEAH - (x_MEACOO + x_HCO3)

        eqs = [eq1, eq2, eq3, eq4, eq5, eq6]

        # print(eqs)

        return eqs

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

    x_app = get_x(alpha, w_MEA)
    x_true_i = np.array([0.0000001571790, 0.042678527, 0.887191216, 0.03506505, 0.03449605, 0.000569])
    x_true_i = np.array([1.72965188e-09, 4.51997445e-02, 8.87456471e-01, 3.36718914e-02,
                         3.33680079e-02, 3.03883524e-04])

    # x_true_f = np.array(root(solve_ChemEQ, x_true_i, args=(x_app, Tl + 273.15, 0)).x)
    i = 0
    tol = 1
    while tol > 1e-6:
        x_true_f = np.array(root(solve_ChemEQ, x_true_i, args=(x_app, Tl, i)).x)
        tol = sum(np.abs(x_true_f - x_true_i))
        # print(i, tol)
        x_true_i = x_true_f
        i += 1

    return np.array(x_true_f)


# if __name__ == '__main__':
#     # np.set_printoptions(precision=8, suppress=True)
#     print(get_true_mol_frac(.3, .3, 40 + 273.15))

if __name__ == '__main__':
    alpha = np.linspace(0.003, 1, 50)
    w_MEA = .3
    T_range = np.linspace(40, 120, 5)
    x_output = []
    T = 40+273.15
    # for T in T_range:
    plt.figure(figsize=(10,10))
    x_true_i = np.array([1.72965188e-09, 4.51997445e-02, 8.87456471e-01, 3.36718914e-02,
                         3.33680079e-02, 3.03883524e-04])
    for a in alpha:

        try:
            x = get_true_mol_frac(a, w_MEA, T)
            # print(x == x_true_i)
            if any(elem < 0 for elem in x) or x[0] == x_true_i[0]:
                x_output.append(np.array([np.nan, np.nan, np.nan, np.nan, np.nan, np.nan]))
            else:
                print(x)
                x_output.append(x)
        except:
            x_output.append(np.array([np.nan, np.nan, np.nan, np.nan, np.nan, np.nan]))
    x_output = np.array(x_output)
    plt.ylim((1e-5, 2e-1))
    plt.yscale('log')
    plt.plot(alpha, x_output)
    plt.grid()
    plt.show()

    # fig, ax = plt.subplots(figsize=(10, 10))
    #
    #
    # def animate(T):
    #     ax.clear()
    #
    #     Tl = T + 273.15
    #     x_true_arr = []
    #     for i, a in enumerate(alpha):
    #         output = get_true_mol_frac(a, w_MEA, Tl)
    #         # print(output)
    #         x_true_arr.append(output)
    #     x_true_arr = np.array(x_true_arr)
    #     x_true_arr = x_true_arr.T
    #     comp = ['CO2', 'MEA', 'H2O', 'MEAH^+', 'MEACOO^-', 'HCO3^-']
    #
    #     for c, x_true in zip(comp, x_true_arr):
    #         if c == 'H2O':
    #             continue
    #         # print(x_true)
    #         ax.semilogy(alpha, x_true, '--', label=c)
    #     ax.legend(loc='lower center')
    #     ax.set_xlim(0, 1)
    #     ax.set_ylim(5e-6, .2)
    #
    #
    # animation = FuncAnimation(fig, animate, frames=range(0, 120 + 1, 5))
    #
    # plt.tick_params(labelsize=12)
    # plt.show()
