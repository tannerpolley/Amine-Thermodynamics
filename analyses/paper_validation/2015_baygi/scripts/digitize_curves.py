"""Digitize the model curves (lines, not points) of three published figures.

Baygi 2015 Fig. 11 (30 wt %, 313 and 393 K), Baygi 2015 Fig. 9 (15.3 wt %, 313-413 K) and Nasrifar and
Tafazzol 2010 Fig. 12a (15.3 wt %, 313/373/413 K). cse:digitize method: calibrate two known points per axis
(the frame lines, which carry the axis end values), trace each curve as the centre of its ink per pixel
column, write coordinates, calibration and error estimates, and a QA overlay. The bundled cse helper
needs OpenCV, which the project environment does not have; this is the same column-centre trace in PIL/numpy.

    uv run python analyses/paper_validation/2015_baygi/scripts/digitize_curves.py
"""
from __future__ import annotations

import hashlib
import json
from pathlib import Path

import numpy as np
import pandas as pd
from PIL import Image, ImageDraw
from scipy import ndimage

ANALYSIS_DIR = Path(__file__).resolve().parents[1]
SOURCE_DIR = ANALYSIS_DIR / "data" / "digitized" / "source"
OUT_DIR = ANALYSIS_DIR / "data" / "digitized"
BAYGI_PROVENANCE = ("copied unchanged from ePC-SAFT-project analyses/reproduction/2015-baygi/figures/{f}/source/paper-source-01-baygi-2015-figure-0{n}.png "
                    "(Mathpix crop of the paper figure, Zotero B8EJJPCJ)")

SPECS = {
    "baygi2015_fig11": {
        "image": SOURCE_DIR / "baygi2015-figure-011.png",
        "provenance": BAYGI_PROVENANCE.format(f="figure-11", n="11"),
        "figure": "Baygi and Pahlavanzadeh 2015 Fig. 11, w_MEA = 30 wt %, solid lines = PC-SAFT prediction",
        "ink": "rgb_black",
        "x_range": (0.0, 1.2), "y_decades": (-6, 6),
        "series": [("393 K", 393.0), ("313 K", 313.0)],  # top to bottom
        "exclude": [(485, 555, 10**6, 10**6)],  # legend: x >= 485 px and y >= 555 px
        "wt_percent": 30.0,
    },
    "baygi2015_fig09": {
        "image": SOURCE_DIR / "baygi2015-figure-009.png",
        "provenance": BAYGI_PROVENANCE.format(f="figure-09", n="09"),
        "figure": "Baygi and Pahlavanzadeh 2015 Fig. 9, w_MEA = 15.3 wt % (Jones 1959 data), solid lines = PC-SAFT prediction",
        "ink": "rgb_black",
        "x_range": (0.0, 0.8), "y_decades": (-5, 4),
        "series": [("413.15 K", 413.15), ("393.15 K", 393.15), ("373.15 K", 373.15),
                   ("353.15 K", 353.15), ("333.15 K", 333.15), ("313.15 K", 313.15)],
        "exclude": [(600, 480, 10**6, 10**6)],
        "wt_percent": 15.3,
    },
    "nasrifar2010_fig12a": {
        "image": SOURCE_DIR / "nasrifar2010-p7-001.png",
        "provenance": ("Zotero CBRPAXQG, PDF attachment 3G4FGGY4, page 7: `pdfimages -png -f 7 -l 7` 1-bit 1200 ppi "
                       "image 001, rows 0-2700 (Fig. 12a); PDF sha256 29165d43cf374760cc17a730d92e15ed77a9e969af1f3355a1ca39a275f7110f"),
        "figure": "Nasrifar and Tafazzol 2010 Fig. 12a, 15.3 wt % aqueous MEA, lines = PC-SAFT prediction",
        "ink": "stencil", "crop": (0, 0, 3196, 2700),
        "x_range": (0.0, 1.0), "y_decades": (-4, 4),
        "series": [("413.15 K", 413.15), ("373.15 K", 373.15), ("313.15 K", 313.15)],
        "exclude": [(1900, 1800, 10**6, 10**6)],  # legend
        "open_px": 13,  # disk diameter: removes the ~10 px open-marker outlines, keeps the 16-24 px curve strokes
        "wt_percent": 15.3,
        "despike": 0.06,  # decades: drops samples where a marker outline merged with the curve
    },
}


def _runs(flags: np.ndarray) -> list[tuple[int, int]]:
    idx = np.where(flags)[0]
    if len(idx) == 0:
        return []
    cuts = np.where(np.diff(idx) > 1)[0]
    return [(int(idx[a]), int(idx[b])) for a, b in zip(np.r_[0, cuts + 1], np.r_[cuts, len(idx) - 1])]


def load_ink(spec: dict) -> np.ndarray:
    im = Image.open(spec["image"])
    if spec["ink"] == "stencil":
        ink = np.array(im.convert("L")) == 255
    else:
        ink = np.array(im.convert("RGB")).astype(int).max(2) < 90  # black only: coloured markers are excluded
    if "crop" in spec:
        left, top, right, bottom = spec["crop"]
        ink = ink[top:bottom, left:right]
    return ink


def frame_centres(ink: np.ndarray) -> dict[str, float]:
    """Frame line centres from the long full-height/width ink lines."""
    cols, rows = ink.sum(0), ink.sum(1)
    col_runs = _runs(cols > 0.8 * cols.max())
    row_runs = _runs(rows > 0.8 * rows.max())
    return {"left": np.mean(col_runs[0]), "right": np.mean(col_runs[-1]),
            "top": np.mean(row_runs[0]), "bottom": np.mean(row_runs[-1]),
            "line_width_px": float(np.mean([b - a + 1 for a, b in col_runs + row_runs]))}


def tick_residual(ink: np.ndarray, frame: dict, spec: dict) -> dict:
    """Independent calibration check: inward tick marks (a few pixels long, just inside the frame) must sit on
    round axis values (multiples of 0.1 or 0.2 in loading, whole decades in pressure) under the frame calibration."""
    half = frame["line_width_px"] / 2
    span_x, span_y = frame["right"] - frame["left"], frame["bottom"] - frame["top"]
    depth = max(3, int(0.006 * span_y))
    x0, x1 = spec["x_range"]
    d0, d1 = spec["y_decades"]
    r0 = int(frame["bottom"] - half - 2 - depth)
    strip = ink[r0: r0 + depth]
    ticks_x = np.array([np.mean(r) for r in _runs(strip.sum(0) >= depth) if frame["left"] + 2 * half < np.mean(r) < frame["right"] - 2 * half])
    c0 = int(frame["left"] + half + 2)
    strip = ink[:, c0: c0 + depth]
    ticks_y = np.array([np.mean(r) for r in _runs(strip.sum(1) >= depth) if frame["top"] + 2 * half < np.mean(r) < frame["bottom"] - 2 * half])
    step = 0.2 if x1 - x0 > 0.9 else 0.1
    off_x = off_y = None
    if len(ticks_x):
        x_data = x0 + (ticks_x - frame["left"]) / span_x * (x1 - x0)
        off_x = np.abs(x_data - np.round(x_data / step) * step) / (x1 - x0) * span_x
    if len(ticks_y):
        y_dec = d0 + (frame["bottom"] - ticks_y) / span_y * (d1 - d0)
        off_y = np.abs(y_dec - np.round(y_dec)) / (d1 - d0) * span_y
    stat = lambda a, f: None if a is None else float(f(a))  # noqa: E731
    return {"n_x_ticks": len(ticks_x), "x_tick_off_grid_px_median": stat(off_x, np.median), "x_tick_off_grid_px_max": stat(off_x, np.max),
            "n_y_ticks": len(ticks_y), "y_tick_off_decade_px_median": stat(off_y, np.median), "y_tick_off_decade_px_max": stat(off_y, np.max)}


def trace(spec: dict, name: str) -> tuple[pd.DataFrame, dict, np.ndarray, dict]:
    ink = load_ink(spec)
    frame = frame_centres(ink)
    line = frame["line_width_px"]
    curves = ink.copy()
    # inside the frame only, minus the legend
    inner = np.zeros_like(curves)
    inner[int(frame["top"] + line): int(frame["bottom"] - line), int(frame["left"] + line): int(frame["right"] - line)] = True
    curves &= inner
    for left, top, right, bottom in spec["exclude"]:
        curves[top:bottom, left:right] = False
    if "open_px" in spec:
        k = spec["open_px"]
        yy, xx = np.mgrid[:k, :k]
        disk = (yy - (k - 1) / 2) ** 2 + (xx - (k - 1) / 2) ** 2 <= (k / 2) ** 2
        curves = ndimage.binary_opening(curves, structure=disk)
    labels, n = ndimage.label(curves, structure=np.ones((3, 3), bool))
    sizes = ndimage.sum(curves, labels, range(1, n + 1))
    width = np.array([np.ptp(np.where(labels == i)[1]) if s > 200 else 0 for i, s in enumerate(sizes, 1)])
    keep = [i for i, w in enumerate(width, 1) if w > 0.08 * (frame["right"] - frame["left"])]
    if len(keep) != len(spec["series"]):
        raise RuntimeError(f"{name}: expected {len(spec['series'])} curves, found {len(keep)} components {width}")
    x0, x1 = spec["x_range"]
    d0, d1 = spec["y_decades"]
    span_x, span_y = frame["right"] - frame["left"], frame["bottom"] - frame["top"]
    stride = max(1, int(round(span_x / 250)))
    rows = []
    traced = {}
    for comp in keep:
        cols = np.unique(np.where(labels == comp)[1])
        pts = []
        for c in cols[::stride]:
            ys = np.where(labels[:, c] == comp)[0]
            pts.append((float(c), float(ys.mean()), int(ys.size)))
        traced[comp] = pts
    # top to bottom at the column shared by all curves
    order = sorted(keep, key=lambda comp: np.mean([p[1] for p in traced[comp]]))
    for comp, (label, temperature_K) in zip(order, spec["series"], strict=True):
        pts = np.array(traced[comp])
        if "despike" in spec:
            ly = np.log10(10.0 ** d0 * (10.0 ** (d1 - d0)) ** ((frame["bottom"] - pts[:, 1]) / span_y))
            med = ndimage.median_filter(ly, size=9, mode="nearest")
            pts = pts[np.abs(ly - med) < spec["despike"]]
        px, py = pts[:, 0], pts[:, 1]
        loading = x0 + (px - frame["left"]) / span_x * (x1 - x0)
        log10_p = d0 + (frame["bottom"] - py) / span_y * (d1 - d0)
        # error: 1.5 px in each pixel coordinate (stroke centre 0.5-1 px, frame-line centre 0.5 px), propagated through
        # the local slope of the curve
        slope_px = np.gradient(py, px)  # pixel rows per pixel column (positive = falling)
        err_px_y = np.hypot(1.5, np.abs(slope_px) * 1.5)
        rows.append(pd.DataFrame({
            "figure_id": name, "series": label, "temperature_K": temperature_K, "MEA_weight_percent": spec["wt_percent"],
            "CO2_loading": loading, "pCO2_kPa": 10.0 ** log10_p, "pixel_x": px, "pixel_y": py,
            "stroke_px": pts[:, 2],
            "est_error_loading": np.hypot(1.5, 0.0) / span_x * (x1 - x0),
            "est_error_ln_pCO2": err_px_y / span_y * (d1 - d0) * np.log(10),
        }))
    ticks = tick_residual(ink, frame, spec) if spec["ink"] == "rgb_black" else {
        "note": "not run: the 1-bit Excel-style axes have outward/minor ticks; calibration rests on the frame-line centres"}
    return pd.concat(rows, ignore_index=True), frame, ink, ticks


def overlay(spec: dict, data: pd.DataFrame, frame: dict, path: Path) -> None:
    im = Image.open(spec["image"]).convert("RGB")
    if spec["ink"] == "stencil":
        im = Image.fromarray(255 - np.array(im))  # 1-bit stencil: ink is white, show it dark
    if "crop" in spec:
        im = im.crop(spec["crop"])
    draw = ImageDraw.Draw(im)
    r = max(2, im.size[0] // 300)
    for x, y in zip(data.pixel_x, data.pixel_y):
        draw.ellipse((x - r, y - r, x + r, y + r), outline=(255, 0, 0), width=max(1, r // 2))
    for xy in ((frame["left"], frame["top"], frame["left"], frame["bottom"]),
               (frame["right"], frame["top"], frame["right"], frame["bottom"]),
               (frame["left"], frame["top"], frame["right"], frame["top"]),
               (frame["left"], frame["bottom"], frame["right"], frame["bottom"])):
        draw.line(xy, fill=(0, 160, 255), width=max(1, r // 2))  # calibration frame
    if max(im.size) > 1400:
        im = im.resize((im.size[0] * 1000 // max(im.size), im.size[1] * 1000 // max(im.size)), Image.LANCZOS)
    path.parent.mkdir(parents=True, exist_ok=True)
    im.save(path)


def main() -> int:
    for name, spec in SPECS.items():
        data, frame, _, ticks = trace(spec, name)
        sha = hashlib.sha256(Path(spec["image"]).read_bytes()).hexdigest()
        data.to_csv(OUT_DIR / f"{name}_model_curves.csv", index=False, float_format="%.6g")
        overlay(spec, data, frame, OUT_DIR / f"{name}_model_curves_qa.png")
        x0, x1 = spec["x_range"]
        d0, d1 = spec["y_decades"]
        meta = {
            "figure": spec["figure"], "source_image": str(spec["image"]), "source_sha256": sha, "provenance": spec["provenance"],
            "image_pixels_wh": Image.open(spec["image"]).size, "crop": spec.get("crop"),
            "axis_calibration": {
                "x": {"scale": "linear", "left_frame_px": frame["left"], "right_frame_px": frame["right"], "values": [x0, x1]},
                "y": {"scale": "log10", "bottom_frame_px": frame["bottom"], "top_frame_px": frame["top"],
                      "values": [10.0 ** d0, 10.0 ** d1]},
                "frame_line_width_px": frame["line_width_px"]},
            "tick_check": ticks,
            "method": "black-ink connected components inside the frame, legend excluded"
                      + (f", disk opening {spec['open_px']} px to drop open-marker outlines" if "open_px" in spec else "")
                      + ", per-column stroke centre, sampled every few columns",
            "estimated_error": {
                "loading_abs_mean": float(data.est_error_loading.mean()),
                "ln_pCO2_median": float(data.est_error_ln_pCO2.median()),
                "ln_pCO2_p90": float(data.est_error_ln_pCO2.quantile(0.9)),
                "basis": "1.5 px per pixel coordinate propagated through the local curve slope; excludes any error in the "
                         "published figure itself"},
            "rows": {s: int((data.series == s).sum()) for s in data.series.unique()},
        }
        (OUT_DIR / f"{name}_model_curves.json").write_text(json.dumps(meta, indent=2, default=float))
        print(name, meta["rows"], "ln error median %.3f p90 %.3f" % (meta["estimated_error"]["ln_pCO2_median"], meta["estimated_error"]["ln_pCO2_p90"]), ticks)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
