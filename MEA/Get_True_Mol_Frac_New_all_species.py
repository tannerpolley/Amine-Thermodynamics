import numpy as np
from scipy.optimize import minimize, root
import pandas as pd
import matplotlib.pyplot as plt
from sympy.physics.quantum.matrixutils import to_numpy

from convex_optimization_gekko import get_x_guess, solve_ChEq


def chemical_equilibrium(Fl, Tl):

    Fl = np.append(Fl, np.array([0, 0, 0, 0, 0, 0]))
    Fl_0_T = sum(Fl)
    x_0 = [Fl[i] / Fl_0_T for i in range(len(Fl))]

    # 1 Water ionization |                  2H2O           <-> H3O+ + OH-
    # 2 Dissociation of carbon dioxide |    2H2O + CO2     <-> H3O+ + HCO3-
    # 3 Dissociation of bicarbonate |        H2O + HCO3-   <-> H3O+ + CO32-
    # 4 Carbamate reversion to bicarbonate | H2O + MEACOO- <-> MEA  + HCO3-
    # 5 Dissociation of protonated amine |   H2O + MEAH+   <-> MEA  + H3O+
    # Reverse of 5 from MEA flowsheet from Kim 2011
    # 5 Dissociation of protonated amine |  MEA  + H3O+ <->  H2O + MEAH+

    # From Baygi 2015 for 1-3 and 5, first three originally from Edwards 1978 converted to K from C
    # Hessen 2010 similar but 4 and 5 is different

    # 4 Originally found by Aroua 1999 in log10 form but then used by Tong 2012 in log form and then converted to mole fraction base by Baygi 2015
    # Going with the one found by Austgen 1991 since it has a better range. Hessen 2010 uses this one as well

    # 5 Originally from Bates and Pinching 1951 but were corrected to the pure amine reference state by Austgen 1991
    # and used by Nasrifar 2010, Baygi 2015,
    # Hessen 2010 somehow has some a different conversion than the others but using the previous one

    a1, b1, c1, d1 = 132.899, -13445.9, -22.4773, 0 # Edwards 1978 Table 1 H2O | Range: 273.15 - 498.15 K

    a2, b2, c2, d2 = 231.465, -12092.1, -36.7816, 0 # Edwards 1978 Table 1 CO2 | Range: 273.15 - 498.15 K

    a3, b3, c3, d3 = 216.049, -12431, -35.4891, 0 # Edwards 1978 Table 1 HCO3- | Range: 273.15 - 498.15 K

    a4, b4, c4, d4 = -1.8652, -1543.3, 0, 0 # Tong 2012 Table 5 | Range: 293.15 - 313.15
    # a4, b4, c4, d4 = 2.8898, -3635.09, 0, 0 # Austgen 1991 Table V 7a | Range: 298.15 - 393.15 K

    a5, b5, c5, d5 = 2.1211, -8189.38, 0.0, -0.007484 # Austgen 1991 Table V 6a | Range: 273.15 - 323.15 K
    # a5, b5, c5, d5 = -4.9074, -6166.12, 0.0, -9.84816 # Hessen 2010 Table 1 (4) | Range: 273.15 - 323.15 K

    # Compute log(K) values
    def log_K(a, b, c, d, Tl):
        return a + b / Tl + c * np.log(Tl) + d * Tl
    log_K1 = log_K(a1, b1, c1, d1, Tl)
    log_K2 = log_K(a2, b2, c2, d2, Tl)
    log_K3 = log_K(a3, b3, c3, d3, Tl)
    log_K4 = log_K(a4, b4, c4, d4, Tl)
    log_K5 = log_K(a5, b5, c5, d5, Tl)
    log_K = np.array([log_K1, log_K2, log_K3, log_K4, log_K5])  # K_i values
    # CO2, MEA, H2O, MEAH+, MEACOO-, HCO3-, CO32-, H3O+, OH-
    v_ij = np.array([
        [0,  0, -2, 0, 0, 0, 0, 1, 1],
        [-1, 0, -2, 0, 0, 1, 0, 1, 0],
        [0, 0, -1, 0, 0, -1, 1, 1, 0],
        [0, 1, -1, 0, -1, 1, 0, 0, 0],
        [0, 1, -1, -1, 0, 0, 0, 1, 0],
    ])

    s_ij = np.array([
        [1, 0, 0, 0, 1, -1, 1, 0, 0],
        [0, 1, 0, 1, 1, 0, 0, 0, 0],
        [0, 0, 1, 0, 0, 1, 1, 1, 1],
        [0, 0, 0, 1, -1, -1, -2, 1, -1],
    ])

    x_guesses = get_x_guess(x_0, log_K, v_ij)[0]


    # print(x_guesses)

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
        x_CO3 = guesses[6]
        x_H3O = guesses[7]
        x_OH = guesses[8]

        x = guesses

        #
        Kee1 = float(np.prod([x[j] ** v_ij[0, j] for j in range(len(x))]))
        Kee2 = float(np.prod([x[j] ** v_ij[1, j] for j in range(len(x))]))
        Kee3 = float(np.prod([x[j] ** v_ij[2, j] for j in range(len(x))]))
        Kee4 = float(np.prod([x[j] ** v_ij[3, j] for j in range(len(x))]))
        Kee5 = float(np.prod([x[j] ** v_ij[4, j] for j in range(len(x))]))

        # log_Kee1 = np.log(Kee1)
        # log_Kee2 = np.log(Kee2)
        # log_Kee3 = np.log(Kee3)
        # log_Kee4 = np.log(Kee4)
        # log_Kee5 = np.log(Kee5)

        # eq1 = (Kee1 - np.exp(log_K[0]))# / max(Kee1, np.exp(log_K[0]))
        eq1 = 0.0
        eq2 = (Kee2 - np.exp(log_K[1]))# / max(Kee2, np.exp(log_K[1]))
        eq3 = (Kee3 - np.exp(log_K[2]))# / max(Kee3, np.exp(log_K[2]))
        eq4 = (Kee4 - np.exp(log_K[3]))# / max(Kee4, np.exp(log_K[3]))
        eq5 = (Kee5 - np.exp(log_K[4]))# / max(Kee5, np.exp(log_K[4]))

        # print(log_Kee1, log_K[0])
        # print(log_Kee2, log_K[1])
        # print(log_Kee3, log_K[2])
        # print(log_Kee4, log_K[3])
        # print(log_Kee5, log_K[4])

        eq6 = (x_CO2_0 - (x_CO2 + x_MEACOO - x_HCO3 + x_CO3)) / x_CO2_0
        eq7 = (x_MEA_0 - (x_MEA + x_MEAH + x_MEACOO)) / x_MEA_0
        eq8 = (x_H2O_0 - (x_H2O + x_HCO3 + x_CO3 + x_H3O + x_OH)) / x_H2O_0
        cations = x_MEAH + x_H3O
        anions = x_MEACOO + x_HCO3 + 2*x_CO3 + x_OH
        eq9 = (cations - anions) / cations
        eqs = np.array([eq1, eq2, eq3, eq4, eq5, eq6, eq7, eq8, eq9])

        # print(eqs)

        return eqs
    #
    # result = root(root_solve, guesses_scaled, args=(x_0, scales), options={'xtol': 1e-14, 'maxfev': 10000, 'eps': 1e-8})
    # # #
    # # #
    # # #
    # x_true_scaled, solution, success = result.x, result.message, result.success
    # #
    # print()
    # print(result.x * scales)
    # print()
    # print(root_solve(result.x, x_0, scales))
    # print()
    # print(solution)
    # print(success)

    # x_true = x_true_scaled * scales
    #
    x_true = guesses_scaled * scales
    x_true = solve_ChEq(x_0, x_guesses, log_K, v_ij, s_ij, scales)

    return np.array(x_true)


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
    Tl = 273.15 + 40
    colors = ['tab:green', 'tab:blue', 'tab:orange', 'tab:olive', 'tab:red', 'tab:cyan', 'tab:purple', 'tab:brown',
              'tab:gray', 'tab:pink']
    species = ['CO2', 'MEA', 'H2O', 'MEAH^+', 'MEACOO^-', 'HCO3^-', 'CO3^2-', 'H3O^+', 'OH^-', 'MEA + MEAH^+']
    comp = ['$CO_2$', '$MEA$', '$H_2O$', '$MEAH^+$', '$MEACOO_-$', '$HCO_3^-$', '$CO_3^{2-}$', '$H_3O^+$', '$OH^-$', '$MEA + MEAH^+$']
    species_map = {species[i]: comp[i] for i in range(len(species))}

    plot_data = True

    fig, ax = plt.subplots(figsize=(10, 10))
    x_true_arr = []
    alpha = np.linspace(.001, .8, 101)
    for a in alpha:
        try:
            output = get_true_mol_frac(a, w_MEA, Tl)
        except:
            output = np.ones(9)*np.nan
        x_true_arr.append(output)

    x_true_arr = np.array(x_true_arr)
    x_true_arr = x_true_arr.T
    x_true_arr = np.vstack([x_true_arr, x_true_arr[1] + x_true_arr[3]])

    df = pd.read_csv(r'../data/MEA/ChEq/Combined_ChEq.csv')
    df = df[
        (df['temperature'] == (Tl - 273.15)) &
        (df['MEA_weight_fraction'] == .30)
        ]
    α_data = df['CO2_loading'].to_numpy()
    data_species = list(df.columns[3:-1])
    x_data = df[data_species].to_numpy()
    # x_data = []

    # for c, x_true, color in zip(species, x_true_arr, colors):
    #     if c == 'H2O':
    #         continue
    #     fig, ax = plt.subplots(figsize=(10, 10))
    #     ax.semilogy(alpha, x_true, '--', color=color, label=species_map[c])
    #     if plot_data:
    #         if c in data_species:
    #             ax.semilogy(α_data, df[c].to_numpy(), 'o', color=color, label=species_map[c])
    #         # minimum = np.floor(np.log10(min(df[c].to_numpy())))
    #         # maximum = np.ceil(np.log10(max(df[c].to_numpy())))
    #         ax.legend(loc='lower center')
    #         # x_range = np.linspace(0, max(alpha), 11)
    #         # y_range = np.logspace(minimum, maximum, int(-minimum + 1))
    #         # ax.set_xlim(x_range[0], x_range[-1])
    #         # ax.set_ylim(y_range[0], y_range[-1])
    #         # ax.set_xticks(x_range)
    #         # ax.set_yticks(y_range)
    #
    #         plt.tick_params(labelsize=12)
    #         plt.show()

    for c, x_true, color in zip(species, x_true_arr, colors):
        if c == 'H2O':
            continue
        ax.semilogy(alpha, x_true, '--', color=color, label=species_map[c])
        if plot_data:
            if c in data_species:
                ax.semilogy(α_data, df[c].to_numpy(), 'o', color=color, label=species_map[c])
    minimum = np.floor(np.log10(min(x_true_arr[0])))
    ax.legend(loc='lower center')
    x_range = np.linspace(0, max(alpha), 11)
    y_range = np.logspace(minimum, 0, int(-minimum + 1))
    ax.set_xlim(x_range[0], x_range[-1])
    ax.set_ylim(y_range[0], y_range[-1])
    ax.set_xticks(x_range)
    ax.set_yticks(y_range)

    plt.tick_params(labelsize=12)
    plt.show()
