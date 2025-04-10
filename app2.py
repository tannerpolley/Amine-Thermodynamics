import streamlit as st
import numpy as np
import pandas as pd
import plotly.graph_objects as go
from pcsaft import flashTQ, flashPQ

st.set_page_config(page_title="PC-SAFT Flash Tool", layout="wide")
st.title("🧪 PC-SAFT Flash Solver")

# === Number of components ===
n = st.sidebar.selectbox("Number of Components", [2, 3])

# === Component names ===
st.markdown("## 🧬 Component Names")
component_names = []
for i in range(n):
    name = st.text_input(f"Component {i+1} name", f"Component {i+1}", key=f"name_{i}")
    component_names.append(name)

# === Input matrix: variables as rows, components as columns ===
st.markdown("## 🧪 Component Parameters")

params_matrix = {
    "x": [],
    "m": [],
    "sigma": [],
    "epsilon_k": [],
}
row_labels = {
    "x": "$x_i$ (Mole Fraction)",
    "m": "$m_i$ (Segments)",
    "sigma": "$\\sigma_i$ [Å]",
    "epsilon_k": "$\\epsilon_i / k$ [K]"
}

for var_key in params_matrix.keys():
    st.markdown(f"#### {row_labels[var_key]}")
    cols = st.columns(n)
    for i, col in enumerate(cols):
        default_val = 1.0 / n if var_key == "x" else 1.0
        val = col.number_input(f"{component_names[i]}", value=default_val, step=0.01, key=f"{var_key}_{i}")
        params_matrix[var_key].append(val)

# Normalize mole fractions
x = np.array(params_matrix["x"])
x = x / np.sum(x) if np.sum(x) > 0 else np.array([1.0] + [0.0] * (n - 1))

# Parameter arrays
m = np.array(params_matrix["m"])
s = np.array(params_matrix["sigma"])
e = np.array(params_matrix["epsilon_k"])
vol_a = np.zeros(n)
e_assoc = np.zeros(n)

# === k_ij matrix ===
st.markdown("## 🔁 Binary Interaction Matrix $k_{ij}$")
k_ij = np.zeros((n, n))
k_cols = st.columns(n)
for i in range(n):
    for j in range(i, n):
        with k_cols[j]:
            val = st.number_input(f"$k_{{{i+1},{j+1}}}$", value=0.0, step=0.001, key=f"k_{i}_{j}")
            k_ij[i][j] = val
            k_ij[j][i] = val

# === Flash selection ===
st.markdown("## ⚡ Flash Options")
flash_type = st.radio("Choose flash type", ["flashTQ (T, q)", "flashPQ (P, q)"])
q = st.number_input("Vapor fraction $q$", min_value=0.0, max_value=1.0, value=0.0, step=0.01)
params = {"m": m, "s": s, "e": e, "vol_a": vol_a, "e_assoc": e_assoc, "k_ij": k_ij}

if flash_type == "flashTQ (T, q)":
    T = st.number_input("Temperature [K]", 200.0, 600.0, 233.15, 1.0)
    if st.button("Run flashTQ"):
        try:
            P_out, x_liq, y_vap = flashTQ(t=T, q=q, x=x, params=params)
            st.success("✅ flashTQ succeeded")
            st.markdown(f"**Solved Pressure:** {P_out / 1000:.2f} kPa")

            result_df = pd.DataFrame({
                "Component": component_names,
                "x_liq": np.round(x_liq, 5),
                "y_vap": np.round(y_vap, 5)
            })
            st.dataframe(result_df, use_container_width=True)
        except Exception as e:
            st.error(f"Flash failed: {e}")

elif flash_type == "flashPQ (P, q)":
    P = st.number_input("Pressure [Pa]", 1e3, 1e7, 1e6, 1000.0)
    if st.button("Run flashPQ"):
        try:
            T_out, x_liq, y_vap = flashPQ(p=P, q=q, x=x, params=params)
            st.success("✅ flashPQ succeeded")
            st.markdown(f"**Solved Temperature:** {T_out:.2f} K")

            result_df = pd.DataFrame({
                "Component": component_names,
                "x_liq": np.round(x_liq, 5),
                "y_vap": np.round(y_vap, 5)
            })
            st.dataframe(result_df, use_container_width=True)
        except Exception as e:
            st.error(f"Flash failed: {e}")

# === Plot section ===
if flash_type == "flashPQ (P, q)" and n == 3:
    st.markdown("## 🌐 Ternary Flash Surface")
    resolution = st.slider("Grid Resolution", 5, 50, 20)
    x1_vals = np.linspace(0, 1, resolution)
    x2_vals = np.linspace(0, 1, resolution)
    X1, X2 = np.meshgrid(x1_vals, x2_vals)
    Z = np.full_like(X1, np.nan)

    for i in range(resolution):
        for j in range(resolution):
            x1 = X1[i, j]
            x2 = X2[i, j]
            x3 = 1.0 - x1 - x2
            if x3 < 0:
                continue
            try:
                x_trial = np.array([x1, x2, x3])
                T_out, *_ = flashPQ(p=P, q=q, x=x_trial, params=params)
                Z[i, j] = T_out
            except:
                continue

    fig = go.Figure(data=[go.Surface(x=X1, y=X2, z=Z)])
    fig.update_layout(
        scene=dict(
            xaxis_title=f"{component_names[0]} (x₁)",
            yaxis_title=f"{component_names[1]} (x₂)",
            zaxis_title="T [K]",
        ),
        margin=dict(l=0, r=0, t=40, b=0)
    )
    st.plotly_chart(fig, use_container_width=True)
