import numpy as np

def dielectric_constant(loading, w_MEA, Tl):

    U1, U2, U3, U4, U5 = 3.4279e2, -5.0886e-3, 9.4690e-7, -2.0525, 3.1159e3
    U6, U7, U8, U9 = -1.8289e2, -8.0325e3, 4.21452e6, 2.1417
    A = U1 * np.exp(U2 * Tl + U3 * Tl ** 2)
    C = U4 + U5 / (U6 + Tl)
    B = U7 + U8 / Tl + U9 / Tl
    P_bar = 1
    ϵ_0_H2O = A + C * np.log((B + P_bar) / (B + 1000))

    T = Tl - 273.15
    a, b, c, d, e, f, g = -.0155, .418, 319, -3.47, 3.12, -.643, .258  # Hajj 2024
    ϵ_0_MEA = (a * T ** 2 + b * T + c) * (d * loading ** 3 + e * loading ** 2 + f * loading + g)
    ϵ = ϵ_0_H2O * (1 - w_MEA) + ϵ_0_MEA * w_MEA

    return ϵ
