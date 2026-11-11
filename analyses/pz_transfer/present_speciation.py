"""Present only retained speciation values; no Engine calculation."""

import csv
from pathlib import Path
import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt

AN = Path(__file__).resolve().parent
rows = list(csv.DictReader((AN / "results/nmr-residuals.csv").open()))
fig, axes = plt.subplots(2, 4, figsize=(13, 6), sharex=True)
for j, T in enumerate([283.15, 298.15, 313.15, 333.15]):
    for g in [1, 2]:
        a = axes[g - 1, j]
        for r in rows:
            if float(r["T_K"]) != T or int(r["group"]) != g:
                continue
            alpha = float(r["co2_mol"]) / float(r["pz_mol"])
            a.errorbar(
                alpha,
                float(r["observed_fraction"]),
                yerr=float(r["marginal_scale_mol"]) / float(r["pz_mol"]),
                fmt="o",
                ms=3,
                color="#0072B2",
                alpha=0.7,
            )
            a.plot(alpha, float(r["calculated_fraction"]), "x", ms=4, color="#D55E00")
        a.set_title(f"{T:.2f} K" + (" (<313 K)" if T < 313 else ""))
        a.set_ylabel(f"f{g} (mol group/mol PZ)")
        a.grid(alpha=0.2)
        if g == 2:
            a.set_xlabel("CO₂/PZ (mol/mol)")
fig.suptitle(
    "Three law offsets at fixed variant-A EOS starts leave NMR disagreement\nBlue: source groups ± operational marginal scale; orange: conditional fit; blank f2 omitted",
    fontsize=11,
)
fig.tight_layout()
fig.savefig(AN / "figures/speciation-nmr.png", dpi=160)
plt.close(fig)
fig, ax = plt.subplots(figsize=(7, 4))
for law, color, marker in [("P1", "#0072B2", "o"), ("P2", "#D55E00", "s")]:
    data = [
        r
        for r in csv.DictReader((AN / "results/hetzer-comparison.csv").open())
        if r["law"] == law and float(r["T_K"]) <= 323.15
    ]
    ax.errorbar(
        [float(r["T_K"]) for r in data],
        [float(r["difference_lnK"]) for r in data],
        yerr=[float(r["conditional_SE_lnK"]) for r in data],
        fmt=marker,
        color=color,
        label=law + " ± Hamborg law SE",
    )
ax.axhline(0, color="black", lw=0.7)
ax.set(
    xlabel="Temperature (K)",
    ylabel="ln K(Hamborg fit) − ln K(Hetzer)",
    title="P2 has the larger independent-source disagreement",
)
ax.legend()
ax.grid(alpha=0.2)
fig.tight_layout()
fig.savefig(AN / "figures/speciation-hetzer.png", dpi=160)
