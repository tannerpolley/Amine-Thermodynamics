import numpy as np


def density(T, z, P, phase='liquid'):

    MWs_l = np.array([.04401, .06108, .01802])  # kg/mol
    MWs_v = np.array([.04401, .01802, .02801, .032])  # kg/mol

    if phase == 'liquid':
        Tl = T
        x = z
        x_CO2, x_MEA, x_H2O = x

        MWT_l = sum([x[i] * MWs_l[i] for i in range(len(x))])

        a1, b1, c1 = -10.5792012186177, 192.012600751473, -695.384861676286
        a2, b2, c2, d2, e2 = [-5.35162e-7, -4.51417e-4, 1.19451, -2.02049415703576, 3.1506793296904, ]
        a3, b3, c3 = [-3.2484e-6, 0.00165, 0.793]

        V_CO2 = a1 + (b1 + c1 * x_MEA) * x_MEA
        V_MEA = MWs_l[1] * 1000 / (a2 * Tl ** 2 + b2 * Tl + c2) + x_H2O * (d2 + e2 * x_MEA)  # mL/mol
        V_H2O = MWs_l[2] * 1000 / (a3 * Tl ** 2 + b3 * Tl + c3)  # mL/mol

        V_l = V_CO2 * x_CO2 + x_MEA * V_MEA + x_H2O * V_H2O  # Liquid Molar Volume (mL/mol)
        V_l = V_l * 1e-6  # Liquid Molar Volume (mL/mol --> m3/mol)

        rho_mol_l = V_l ** -1  # Liquid Molar Density (m3/mol --> mol/m3)
        rho_mass_l = rho_mol_l * MWT_l  # Liquid Mass Density (mol/m3 --> kg/m3)

        volume = [V_l, V_CO2 * 1e-6, V_MEA * 1e-6, V_H2O * 1e-6]

        return rho_mol_l, rho_mass_l, volume

    elif phase == 'vapor':
        Tv = T
        y = z
        rho_mol_v = P / (R * Tv)  # Vapor Molar Density (mol/m3)

        MWT_v = 0
        for i in range(len(y)):
            MWT_v += y[i] * MWs_v[i]  # kg/mol

        rho_mass_v = rho_mol_v * MWT_v  # Vapor Mass Density (mol/m3 --> kg/m3)

        return rho_mol_v, rho_mass_v

    return None