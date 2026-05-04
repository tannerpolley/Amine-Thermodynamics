import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from scipy.interpolate import interp1d
from Get_True_Mol_Frac import get_true_mol_frac
from PC_SAFT import flash, PCSAFT
from PC_SAFT_v2 import flash_v2
from PC_SAFT_v3 import flash_v3
from pcsaft_electrolyte import pcsaft_den as pcsaft_den2
from pcsaft_electrolyte import pcsaft_fugcoef as pcsaft_fugcoef2
from pcsaft import flashTQ, pcsaft_ares, pcsaft_den, pcsaft_p, pcsaft_fugcoef
import time

#%%

T = 40

interp_data = pd.read_csv(r"C:\Users\Tanner\Documents\git\eNRTL_Fitting_Routine\compare_data_without_eNRTL.csv")
df = pd.read_csv(r'data/data_sets_to_load/Jou_1995_VLE.csv')
df = df[(df['temperature'] == T) &
        (df['CO2_loading'] > .1) &
        (df['CO2_loading'] < .6)]
P_CO2_data, α_data = df['CO2_pressure'].to_numpy(), df['CO2_loading'].to_numpy()
w_MEA = .3
Tl = 273.15 + T
interp_data_cut = interp_data[interp_data['temperature'] == T]
P_interp = interp1d(interp_data_cut['loading'], interp_data_cut['Pressure'])
P_H2O_interp = interp1d(interp_data_cut['loading'], interp_data_cut['fug_H2O'])
P_CO2_interp = interp1d(interp_data_cut['loading'], interp_data_cut['fug_CO2'])
loading = .3
x = get_true_mol_frac(loading, w_MEA, Tl)
x = np.array([xi / sum(x) for xi in x])
Pg = float(P_interp(loading)) * 1e3
y_CO2_g = P_CO2_interp(loading) / Pg
y_H2O_g = P_H2O_interp(loading)*1e3 / Pg
yg = [y_CO2_g, 1 - y_H2O_g - y_CO2_g, y_H2O_g]

sigma_H2O = 2.7927 + (10.11 * np.exp(-.01775 * T - 1.417 * np.exp(-.01146 * T)))
kij_CO2_MEA = .16
kij_CO2_H2O = .13
kij_MEA_H2O = -.18

prop_dic_2 = {
    'm': np.array([2.079, 3.0353, 1.9599, 0., 0., 0.]),
    's': np.array([2.7852, 3.0435, 2.363, 3., 3., 3.]),
    'e': np.array([169.21, 277.174, 279.42, 300., 300., 300.]),
    'vol_a': np.array([0, .037470, .1750, .03, .03, .03]),
    'e_assoc': np.array([0, 2586.3, 2059.28, 2000., 2000., 2000.]),
    'k_ij': np.array([[0.0, kij_CO2_MEA, kij_CO2_H2O, 0., 0., 0.],
                      [kij_CO2_MEA, 0.0, kij_MEA_H2O, 0., 0., 0.],
                      [kij_CO2_H2O, kij_MEA_H2O, 0.0, 0., 0., 0.],
                      [0., 0., 0., 0., 0., 0.],
                      [0., 0., 0., 0., 0., 0.],
                      [0., 0., 0., 0., 0., 0.]]),
    'dielc': 75.,
    # 'dipm': np.array([0, 2.27, 1.85, 0, 0, 0]),
    'dip_num': np.array([1., 1., 1., 1., 1., 1.]),
    'z': np.array([0., 0., 0., +1, -1, -1])
}

if __name__ == '__main__':
    # print(prop_dic_2)
    print(x)
    P, x, y = flashTQ(t=Tl, x=x, q=0, params=prop_dic_2)
    # print(P)
    P = 101325
    rho_x = pcsaft_den(t=Tl, p=P, x=x, params=prop_dic_2)
    print(rho_x)
    rho_y = pcsaft_den(t=Tl, p=P, x=y, params=prop_dic_2, phase='vap')
    print(pcsaft_fugcoef(t=Tl, rho=rho_x, x=x, params=prop_dic_2))
    print(pcsaft_fugcoef(t=Tl, rho=rho_y, x=y, params=prop_dic_2))
# print(x)
# P, x, y = flashTQ(t=Tl, q=0, x=x, params=prop_dic_2)
# print(P)
# print(x)
# print(y)


