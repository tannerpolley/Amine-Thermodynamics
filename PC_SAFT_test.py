import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from pcsaft import flashTQ
from scipy.interpolate import interp1d
from Get_True_Mol_Frac import get_true_mol_frac
from PC_SAFT import flash, PCSAFT
# from pcsaft_electrolyte import *
from pcsaft import flashTQ, pcsaft_ares, pcsaft_den, pcsaft_p, pcsaft_fugcoef
import pcsaft
print(pcsaft.__file__)
import time

import sys

# for path in sys.path:
#     print(path)

#%%
plt.figure(figsize=(10, 10))


def Rochelle_fit(loading, T):
    return np.exp((39.3 - 12155 / T - 19.0 * loading ** 2 + 1105 * loading / T + 12800 * loading ** 2 / T)) / 1e3


interp_data = pd.read_csv(r"C:\Users\Tanner\Documents\git\eNRTL_Fitting_Routine\compare_data_without_eNRTL.csv")

colors = ['tab:orange', 'tab:blue', 'tab:green', 'tab:red', 'tab:purple', 'tab:pink', 'tab:brown']
for i, T in enumerate([40, 60, 80, 100, 120]):
    df = pd.read_csv(r'data/data_sets_to_load/Jou_1995_VLE.csv')
    df = df[(df['temperature'] == T) &
            (df['CO2_loading'] > .1) &
            (df['CO2_loading'] < .6)]
    P_CO2_data, α_data = df['CO2_pressure'].to_numpy(), df['CO2_loading'].to_numpy()
    w_MEA = .3
    Tl = 273.15 + T
    P_CO2_list = []
    P_CO2_2_list = []
    P_CO2_3_list = []
    P_CO2_4_list = []
    loading_range = np.linspace(α_data[0], α_data[-1], 21)
    # interp_data_cut = interp_data[interp_data['temperature'] == T]
    # P_interp = interp1d(interp_data_cut['loading'], interp_data_cut['Pressure'])
    # P_H2O_interp = interp1d(interp_data_cut['loading'], interp_data_cut['fug_H2O'])
    # P_CO2_interp = interp1d(interp_data_cut['loading'], interp_data_cut['fug_CO2'])
    print(T)
    for loading in loading_range:
        x = get_true_mol_frac(loading, w_MEA, Tl)
        x = np.array([xi / sum(x) for xi in x])
        # Pg = float(P_interp(loading)) * 1e3
        # y_CO2_g = P_CO2_interp(loading) * 1e3 / Pg
        # y_H2O_g = P_H2O_interp(loading) * 1e3 / Pg
        # yg = [y_CO2_g, 1 - y_H2O_g - y_CO2_g, y_H2O_g]

        kij_CO2_MEA = .16
        kij_CO2_H2O = .15
        kij_MEA_H2O = -.18

        # From
        prop_dic = {
            'm': np.array([2.079, 3.0353, 1.9599]),
            's': np.array([2.7852, 3.0435, 2.363]),
            'e': np.array([169.21, 277.174, 279.42]),
            'vol_a': np.array([0, .037470, .1750]),
            'e_assoc': np.array([0, 2586.3, 2059.28]),
            'k_ij': np.array([[0.0, kij_CO2_MEA, kij_CO2_H2O],
                              [kij_CO2_MEA, 0.0, kij_MEA_H2O],
                              [kij_CO2_H2O, kij_MEA_H2O, 0.0]]),
            # 'dielc': 75
        }
        # sigma_H2O = 2.7927 + (10.11 * np.exp(-.01775 * Tl - 1.417 * np.exp(-.01146 * Tl)))
        # kij_CO2_H2O = -2.2e-2 + 4.2e-4 * (Tl - 298) - 1.7e-6 * (Tl - 298) ** 2
        # kij_MEA_H2O = -1.5275e-2 - 5.24e-5 * (Tl - 298) + 7.9e-6 * (Tl - 298) ** 2

        prop_dic_2 = {
            'm': np.array([2.079, 3.0353, 1.9599, 1, 1, 1]),
            's': np.array([2.7852, 3.0435, 2.363, 3, 3, 3]),
            'e': np.array([169.21, 277.174, 279.42, 300, 300, 300]),
            'vol_a': np.array([0, .037470, .1750, 0, 0, 0]),
            'e_assoc': np.array([0, 2586.3, 2059.28, 0, 0, 0]),
            'k_ij': np.array([[0.0, kij_CO2_MEA, kij_CO2_H2O, 0., 0., 0.],
                              [kij_CO2_MEA, 0.0, kij_MEA_H2O, 0., 0., 0.],
                              [kij_CO2_H2O, kij_MEA_H2O, 0.0, 0., 0., 0.],
                              [0., 0., 0., 0., 0., 0.],
                              [0., 0., 0., 0., 0., 0.],
                              [0., 0., 0., 0., 0., 0.]]),
            'dielc': 75,
            # # 'dipm': np.array([0, 2, 9, 2, 2, 2]),
            'z': np.array([0, 0, 0, +1, -1, -1])
        }

        start_time = time.time()
        params = prop_dic
        if params == prop_dic:
            x = x[:3]
            x = np.array([xi / sum(x) for xi in x])
        try:

            P, xl, y = flashTQ(t=Tl, q=0, x=x, params=prop_dic)
            P_CO2_2 = P * y[0] /1e3
            P_CO2_2_list.append(P_CO2_2)
        except:
            P_CO2_2_list.append(np.nan)

    #%%
    plt.plot(α_data, P_CO2_data, 'x', color=colors[i])
    plt.plot(loading_range, P_CO2_2_list, ':', label=f'Zmeri - T = {T}', color=colors[i])

plt.xlabel("CO$_{2}$ Loading, mol CO$_{2}$/mol MEA", fontsize=16)
plt.ylabel("CO$_{2}$ pressure, kPa", fontsize=16)
plt.tick_params(labelsize=14)
plt.tight_layout()
plt.yscale('log')
plt.legend()
plt.show()
