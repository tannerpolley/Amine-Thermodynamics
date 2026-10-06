"""Figure typography at the cas-sc class's 164.6 mm text width."""

import matplotlib as mpl

FULL_WIDTH = 16.46 / 2.54


def apply_style():
    mpl.rcParams.update({
        "font.family": "serif",
        "font.serif": ["STIXGeneral"],
        "mathtext.fontset": "stix",
        "pdf.fonttype": 42,
        "ps.fonttype": 42,
        "font.size": 9,
        "axes.labelsize": 9,
        "axes.titlesize": 9,
        "figure.labelsize": 9,
        "figure.titlesize": 9,
        "xtick.labelsize": 8,
        "ytick.labelsize": 8,
        "legend.fontsize": 8,
        "axes.linewidth": 0.7,
        "lines.linewidth": 1.0,
        "lines.markersize": 4,
        "lines.markeredgewidth": 0.7,
        "patch.linewidth": 0.7,
        "grid.linewidth": 0.5,
        "savefig.bbox": None,
    })
