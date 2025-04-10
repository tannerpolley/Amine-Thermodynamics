import streamlit as st
import numpy as np
import pandas as pd
import plotly.graph_objects as go
import json
from pcsaft import flashTQ, flashPQ

st.set_page_config(page_title="PC-SAFT Flash Tool", layout="wide")
st.title("PC-SAFT Flash Solver")

# Step 1: Number of components
st.markdown("## Step 1: Select Number of Components")
n = st.selectbox("Number of Components", [2, 3], index=1)

# Labels for input
var_labels = {
    "species": "Species",
    "z": "zᵢ",
    "m": "mᵢ",
    "sigma": "σᵢ",
    "epsilon_k": "εᵢ / k"
}

# Initialize matrix
param_matrix = {
    key: [0.000]*n if key != "species" else [f"Component {i+1}" for i in range(n)]
    for key in var_labels
}

# Load preset
uploaded = st.file_uploader("Upload Preset JSON", type="json", label_visibility="collapsed")
if uploaded:
    try:
        loaded = json.load(uploaded)
        for key in var_labels:
            data = loaded.get(key, [])
            for i in range(n):
                if i < len(data):
                    param_matrix[key][i] = data[i]
        st.success("✅ Preset loaded successfully!")
    except Exception as e:
        st.error(f"❌ Failed to load preset: {e}")

# Step 2: Component properties
st.markdown("## Step 2: Component Properties")
cols = st.columns(n + 1)
cols[0].markdown("**Property ↓ / Component →**")
for i in range(n):
    cols[i + 1].markdown(f"<div style='text-align:center'><b>{i+1}</b></div>", unsafe_allow_html=True)

for var_key, label in var_labels.items():
    row = st.columns(n + 1)
    row[0].markdown(f"**{label}**" if var_key == "species" else f"${label}$")
    for i in range(n):
        key = f"{var_key}_{i}"
        default_val = str(param_matrix[var_key][i]) if var_key == "species" else f"{param_matrix[var_key][i]:.3f}"
        user_val = row[i + 1].text_input("", value=default_val, key=key, label_visibility="collapsed")
        if var_key == "species":
            param_matrix[var_key][i] = user_val.strip()
        else:
            try:
                parsed = float(user_val)
                param_matrix[var_key][i] = round(parsed, 3) if var_key == "z" else parsed
            except ValueError:
                param_matrix[var_key][i] = 0.000

# Save Preset
with st.expander("💾 Save Current Setup"):
    preset_name = st.text_input("Preset File Name", value="my_flash_preset")
    if st.button("Save Preset"):
        preset_data = json.dumps(param_matrix)
        st.download_button("Download Preset JSON", preset_data, file_name=f"{preset_name}.json")

# Extract input
component_names = param_matrix["species"]
z = np.array(param_matrix["z"])
m = np.array(param_matrix["m"])
s = np.array(param_matrix["sigma"])
e = np.array(param_matrix["epsilon_k"])
vol_a = np.zeros(n)
e_assoc = np.zeros(n)

# k_ij matrix
st.markdown("### Binary Interaction Matrix $k_{ij}$")
k_ij = np.zeros((n, n))
k_cols = st.columns(n)
for i in range(n):
    for j in range(i, n):
        with k_cols[j]:
            k_val = st.text_input(f"$k_{{{i+1},{j+1}}}$", value="0.000", key=f"k_{i}_{j}")
            try:
                val = float(k_val)
            except ValueError:
                val = 0.0
            k_ij[i][j] = val
            k_ij[j][i] = val

params = {"m": m, "s": s, "e": e, "vol_a": vol_a, "e_assoc": e_assoc, "k_ij": k_ij}

# Step 3: Flash
st.markdown("## Step 3: Flash Calculation")
flash_mode = st.selectbox("Flash Type", ["Bubble T", "Bubble P", "Dew T", "Dew P"])

q = 0.0 if "Bubble" in flash_mode else 1.0
comp_input = z.copy()

if "T" in flash_mode:
    T = st.number_input("Temperature [K]", 200.0, 600.0, 233.15)
    if st.button("Run Flash"):
        try:
            P_out, x_liq, y_vap = flashTQ(t=T, q=q, x=comp_input, params=params)
            st.success("✅ Flash succeeded")
            st.write(f"**Solved Pressure:** {P_out / 1000:.2f} kPa")
            st.table(pd.DataFrame({
                "Component": component_names,
                "x": np.round(x_liq, 4),
                "y": np.round(y_vap, 4)
            }))
        except Exception as e:
            st.error(f"Flash failed: {e}")
else:
    P = st.number_input("Pressure [Pa]", 1000.0, 1e7, 1e6)
    if st.button("Run Flash"):
        try:
            T_out, x_liq, y_vap = flashPQ(p=P, q=q, x=comp_input, params=params)
            st.success("✅ Flash succeeded")
            st.write(f"**Solved Temperature:** {T_out:.2f} K")
            st.table(pd.DataFrame({
                "Component": component_names,
                "x": np.round(x_liq, 4),
                "y": np.round(y_vap, 4)
            }))
        except Exception as e:
            st.error(f"Flash failed: {e}")

# Step 4: Plot
if n == 3:
    st.markdown("## Step 4: Generate Ternary Surface Plot")
    resolution = st.slider("Grid Resolution", 5, 50, 20)

    if st.button("Generate Ternary Surface"):
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
                    if "T" in flash_mode:
                        P_out, *_ = flashTQ(t=T, q=q, x=x_trial, params=params)
                        Z[i, j] = P_out / 1000
                    else:
                        T_out, *_ = flashPQ(p=P, q=q, x=x_trial, params=params)
                        Z[i, j] = T_out
                except:
                    continue

        label = "P [kPa]" if "T" in flash_mode else "T [K]"
        fig = go.Figure(data=[go.Surface(x=X1, y=X2, z=Z)])
        fig.update_layout(
            scene=dict(
                xaxis_title=f"{component_names[0]} (x₁)",
                yaxis_title=f"{component_names[1]} (x₂)",
                zaxis_title=label,
            ),
            margin=dict(l=0, r=0, t=40, b=0)
        )
        st.plotly_chart(fig, use_container_width=True)
