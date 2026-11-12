"""Calibration residuals and identification from retained stage-4 values only."""

import json
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np

AN = Path(__file__).resolve().parent
fig, axes = plt.subplots(1, 2, figsize=(11, 4), layout="constrained")
for kind, color, marker in [("A", "#0072B2", "o"), ("B", "#D55E00", "x")]:
    fit = json.loads((AN / f"results/reactive-{kind}-fit.json").read_text())
    singular = fit["endpoint_information"]["singular_values"]
    axes[0].scatter(np.arange(1, 18), singular, label=kind, c=color, marker=marker)
    evidence = json.loads((AN / f"results/reactive-{kind}-evidence.json").read_text())
    axes[1].scatter([0, 1], [evidence["NMR_RMS"], evidence["pressure_RMS"]], label=kind, c=color, marker=marker)
axes[0].set(xlabel="Singular direction (ordered)", ylabel="Scaled Jacobian singular value", yscale="log")
axes[1].set(xticks=[0, 1], xticklabels=["NMR", "Hilliard pressure"], ylabel="Calibration residual RMS / operational scale")
axes[1].set_ylim(bottom=0)
for ax in axes:
    ax.legend(title="Variant")
    ax.grid(alpha=0.2)
fig.savefig(AN / "figures/reactive-identification.png", dpi=160)
