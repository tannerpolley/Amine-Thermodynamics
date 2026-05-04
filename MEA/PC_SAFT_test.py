import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from pathlib import Path
import sys

from Get_True_Mol_Frac_New_all_species import get_true_mol_frac
# from Get_True_Mol_Frac_New import get_true_mol_frac
from Get_True_Mol_Frac_with_activity import get_true_mol_frac_with_activity

from plot_export import save_plot

REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from pcsaft_models_polley.ePC_SAFT_properties import get_prop_dict

try:
    from pcsaft import flashTQ, pcsaft_den, pcsaft_fugcoef
except ImportError:
    from pcsaft_models_polley import pcsaft_electrolyte_py as local_pcsaft
    from pcsaft_models_polley import pcsaft_electrolyte as local_pcsaft_core

    def _phase_name(phase):
        return {"liquid": "liq", "vapor": "vap"}.get(phase, phase)

    def _bubble_kwargs(x, params):
        kwargs = {}
        for key in ("k_ij", "e_assoc", "vol_a", "dipm", "dip_num", "z"):
            if key in params:
                kwargs[key] = params[key]
        if "dielc" in params:
            kwargs["dielc"] = float(local_pcsaft.f_dielc(np.asarray(x, dtype=float), np.asarray(params["dielc"], dtype=float)))
        return kwargs

    def pcsaft_den(t, p, x, params, phase="liq"):
        return local_pcsaft.pcsaft_den(t, p, np.asarray(x, dtype=float), params, phase=_phase_name(phase))

    def pcsaft_fugcoef(t, rho, x, params):
        return local_pcsaft.pcsaft_fugcoef(t, rho, np.asarray(x, dtype=float), params)

    def flashTQ(t, q, x, params):
        if q != 0:
            raise NotImplementedError("Local fallback flashTQ shim only supports q=0.")
        p_guess = 101325.0
        x = np.asarray(x, dtype=float)
        xv_guess = x.copy()
        bubble_p, y = local_pcsaft_core.pcsaft_bubbleP(
            p_guess,
            xv_guess,
            x,
            np.asarray(params["m"], dtype=float),
            np.asarray(params["s"], dtype=float),
            np.asarray(params["e"], dtype=float),
            t,
            **_bubble_kwargs(x, params),
        )
        return float(np.asarray(bubble_p).reshape(-1)[0]), x, np.asarray(y, dtype=float)

DATA_ROOT = Path(__file__).resolve().parents[1] / "data" / "MEA"

fig = plt.figure(figsize=(14, 10))


def Rochelle_fit(loading, T):
    return np.exp((39.3 - 12155 / T - 19.0 * loading ** 2 + 1105 * loading / T + 12800 * loading ** 2 / T)) / 1e3


# 3B for MEA and 2B for H2O

# species = ['CO2', 'MEA-2B', 'H2O-2B-CC', 'MEAH+', 'MEACOO-', 'HCO3-']
species = ['CO2', 'MEA-2B', 'H2O-2B-CC', 'MEAH+', 'MEACOO-', 'HCO3-', 'CO32-', 'H3O+', 'OH-']

interp_data = pd.read_csv(r"C:\Users\Tanner\Documents\git\eNRTL_Fitting_Routine\compare_data_without_eNRTL.csv")

add_activity = False

colors = ['tab:blue', 'tab:orange', 'tab:green', 'tab:cyan', 'tab:purple', 'tab:pink', 'tab:brown']
for i, T in enumerate([40, 60, 80, 100, 120]):
    df = pd.read_csv(DATA_ROOT / "VLE" / "Combined_VLE.csv")
    df = df[(df['temperature'] == T) &
            # (df['CO2_loading'] > .05) &
            (df['CO2_loading'] < .6)]
    P_CO2_data, α_data = df['CO2_pressure'].to_numpy(), df['CO2_loading'].to_numpy()
    w_MEA = .3
    Tl = 273.15 + T

    prop_dic = get_prop_dict(species, T)

    x_small = 1e-10
    γ_index = np.ones(len(species))*x_small
    γ_index[2] = 1.0 - (5 * x_small)
    P_CO2_list = []
    γ_CO2_list = []
    loading_range = np.linspace(min(α_data), max(α_data), 21)
    # loading_range = np.linspace(.3, .3, 1)
    for loading in loading_range:

        params = prop_dic.copy()

        x = get_true_mol_frac(loading, w_MEA, Tl)
        x = np.array([x[i] / sum(x) for i in range(len(x))])

        if add_activity:

            P = 101325
            rho = pcsaft_den(Tl, P, x, params=params.copy(), phase='liquid')
            ϕ_j = pcsaft_fugcoef(Tl, rho, x, params=params.copy())

            # x_2 = np.array([0.0, 0.0, 1.0, 0.0, 0.0, 0.0])
            x_2 = np.zeros(len(x))
            x_2[2] = 1.0
            rho_2 = pcsaft_den(Tl, P, x_2, params=params.copy(), phase='liquid')
            ϕ_inf_j = pcsaft_fugcoef(Tl, rho_2, x_2, params=params.copy())

            x_2 = np.array([0.0, 1.0, 0.0, 0.0, 0.0, 0.0])
            x_2 = np.zeros(len(x))
            x_2[1] = 1.0
            rho_2 = pcsaft_den(Tl, P, x_2, params=params.copy(), phase='liquid')

            ϕ_inf_j_MEA = pcsaft_fugcoef(Tl, rho_2, x_2, params=params.copy())[1]
            ϕ_inf_j[1] = ϕ_inf_j_MEA

            γ = ϕ_j / np.array(ϕ_inf_j)

            tol = 1e-6
            x_old = x + 10 * tol

            while np.max(np.abs(x - x_old)) > tol:
                x_old = x.copy()

                x = get_true_mol_frac_with_activity(loading, w_MEA, Tl, γ)
                x = np.array([x[i] / sum(x) for i in range(len(x))])
                P = 101325
                rho = pcsaft_den(x=x, t=Tl, p=P, params=params, phase='liquid')
                ϕ_j = pcsaft_fugcoef(Tl, rho, x, params=params)

                x_2 = np.array([0.0, 0.0, 1.0, 0.0, 0.0, 0.0])
                rho_2 = pcsaft_den(Tl, P, x_2, params=params.copy(), phase='liquid')
                ϕ_inf_j = pcsaft_fugcoef(Tl, rho_2, x_2, params=params.copy())

                x_2 = np.array([0.0, 1.0, 0.0, 0.0, 0.0, 0.0])
                rho_2 = pcsaft_den(Tl, P, x_2, params=params.copy(), phase='liquid')
                ϕ_inf_j_MEA = pcsaft_fugcoef(Tl, rho_2, x_2, params=params.copy())[1]

                ϕ_inf_j[1] = ϕ_inf_j_MEA

                γ = ϕ_j / np.array(ϕ_inf_j)

        P, xl, y = flashTQ(Tl, 0, x, params=params)

        # P_CO2 = γ[0]
        P_CO2 = P * y[0] / 1e3
        P_CO2_list.append(P_CO2)
        # if add_activity:
        γ_CO2_list.append(x[0])

    P_CO2_list = np.array(P_CO2_list)

    plt.plot(α_data, P_CO2_data, 'x', color=colors[i])
    plt.plot(loading_range, P_CO2_list, '--', label=f'ePC-SAFT - T = {T}', color=colors[i])

plt.xlabel("CO$_{2}$ Loading, mol CO$_{2}$/mol MEA", fontsize=16)
plt.ylabel("CO$_{2}$ pressure, kPa", fontsize=16)
plt.tick_params(labelsize=14)
plt.tight_layout()
plt.ylim((10e-5, 5e3))
plt.yscale('log')
plt.legend()
save_plot(fig, __file__, "co2_partial_pressure")
