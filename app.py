import streamlit as st
import numpy as np
import pandas as pd
import plotly.graph_objects as go
from pcsaft import flashTQ, flashPQ

st.set_page_config(page_title="PC-SAFT Flash Tool", layout="wide")
st.title("🧪 PC-SAFT Flash Solver for Ternary Mixtures")

# === PC-SAFT Parameters ===
m = np.array([1.0, 1.6069, 2.0020])
s = np.array([3.7039, 3.5206, 3.6184])
e = np.array([150.03, 191.42, 208.11])
vol_a = np.zeros(3)
e_assoc = np.zeros(3)
k_ij = np.array([
    [0.0000, 0.0003, 0.0115],
    [0.0003, 0.0000, 0.0051],
    [0.0115, 0.0051, 0.0000]
])
params = {
    "m": m,
    "s": s,
    "e": e,
    "vol_a": vol_a,
    "e_assoc": e_assoc,
    "k_ij": k_ij,
}

# === Mode Selection ===
mode = st.sidebar.radio("Mode", ["Single Flash", "Ternary Flash Surface"])

# ========================================================================================
# SINGLE FLASH MODE
# ========================================================================================
if mode == "Single Flash":
    st.header("🔹 Single Flash Calculation")

    flash_type = st.selectbox("Flash Type", ["flashTQ (T, q)", "flashPQ (P, q)"])

    x1 = st.number_input("x₁ (Component 1)", 0.0, 1.0, 0.3, 0.01)
    x2 = st.number_input("x₂ (Component 2)", 0.0, 1.0 - x1, 0.4, 0.01)
    x3 = 1.0 - x1 - x2
    if x3 < 0:
        st.error("❌ Mole fractions exceed 1. Adjust x₁ and x₂.")
        st.stop()
    x = np.array([x1, x2, x3])
    st.markdown(f"**x₃ (Component 3):** {x3:.4f}")

    q = st.number_input("Vapor fraction (q)", 0.0, 1.0, 0.0, 0.01)

    if flash_type == "flashTQ (T, q)":
        T = st.number_input("Temperature [K]", 200.0, 600.0, 233.15, 1.0)
        if st.button("Solve FlashTQ"):
            try:
                P_out, x_liq, y_vap = flashTQ(t=T, q=q, x=x, params=params)
                st.success("✅ flashTQ succeeded")
                st.markdown("### Flash Results")
                st.write(f"**Input T:** {T:.2f} K  **q:** {q:.3f}")
                st.write(f"**Solved P:** {P_out/1e3:.2f} kPa")

                species = [f"Component {i+1}" for i in range(3)]
                x_liq = np.asarray(x_liq).flatten().astype(float)
                y_vap = np.asarray(y_vap).flatten().astype(float)

                df = pd.DataFrame({
                    "Species": species,
                    "x": x_liq,
                    "y": y_vap
                })
                st.table(df)

            except Exception as e:
                st.error(f"Flash calculation failed: {e}")

    elif flash_type == "flashPQ (P, q)":
        P = st.number_input("Pressure [Pa]", 1000.0, 1e7, 1e6, 1000.0)
        if st.button("Solve FlashPQ"):
            try:
                T_out, x_liq, y_vap = flashPQ(p=P, q=q, x=x, params=params)
                st.success("✅ flashPQ succeeded")
                st.markdown("### Flash Results")
                st.write(f"**Input P:** {P:.0f} Pa  **q:** {q:.3f}")
                st.write(f"**Solved T:** {T_out:.2f} K")

                species = [f"Component {i+1}" for i in range(3)]
                x_liq = np.asarray(x_liq).flatten().astype(float)
                y_vap = np.asarray(y_vap).flatten().astype(float)

                df = pd.DataFrame({
                    "Species": species,
                    "x_liq (liquid phase)": x_liq,
                    "y_vap (vapor phase)": y_vap
                })
                st.table(df)

            except Exception as e:
                st.error(f"Flash calculation failed: {e}")

# ========================================================================================
# TERNARY FLASH SURFACE MODE
# ========================================================================================
elif mode == "Ternary Flash Surface":
    st.header("🌈 Ternary Flash Surface: T over Composition Triangle")

    P = st.sidebar.number_input("Pressure [Pa]", 1000.0, 1e7, 1e6, 1000.0)
    q = st.sidebar.number_input("Vapor fraction (q)", 0.0, 1.0, 0.0, 0.01)
    resolution = st.sidebar.slider("Grid Resolution", 5, 50, 20)

    st.info("Running flashPQ over composition triangle...")

    x1_vals = np.linspace(0, 1, resolution)
    x2_vals = np.linspace(0, 1, resolution)
    X1, X2 = np.meshgrid(x1_vals, x2_vals)
    Z = np.full_like(X1, np.nan, dtype=float)

    for i in range(resolution):
        for j in range(resolution):
            x1 = X1[i, j]
            x2 = X2[i, j]
            x3 = 1.0 - x1 - x2
            if x3 < 0:
                continue
            x = np.array([x1, x2, x3])
            try:
                T_out, *_ = flashPQ(p=P, q=q, x=x, params=params)
                Z[i, j] = T_out
            except:
                continue

    if np.isnan(Z).all():
        st.warning("⚠️ No valid flash points were computed.")
    else:
        fig = go.Figure(data=[go.Surface(x=X1, y=X2, z=Z, colorscale="Viridis", showscale=True)])
        fig.update_layout(
            scene=dict(
                xaxis_title="x₁ (Component 1)",
                yaxis_title="x₂ (Component 2)",
                zaxis_title="T [K]"
            ),
            title="Ternary Flash Surface: T vs x₁, x₂ (x₃ = 1 − x₁ − x₂)",
            margin=dict(l=0, r=0, b=0, t=40)
        )
        st.plotly_chart(fig, use_container_width=True)
