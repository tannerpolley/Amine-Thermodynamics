"""Digitize the ePC-SAFT model lines of Wangler 2018 Fig. 11 (w_MDEA 0.32, total pressure) and Fig. 12 (w_MDEA 0.48,
"log(p_CO2)") so conventions.py can compare Engine pressures with Wangler's own model, as it does for Uyan Fig. 5.

Source: Wangler et al. 2018, Fluid Phase Equilib. 461, 15-27 (Zotero ZILDPWWE, PDF attachment G7ZTAJZS), PDF page 8
(printed p. 22).  The page is rendered at 600 dpi with pdftoppm; each panel is calibrated by its frame (alpha 0 and
1.4; p 0.1 and 100 bar, log scale) and checked against the interior major ticks.  Lines are black and markers grey with
black outlines, so a dark run counts as line only when white paper lies on both sides of it.  Each line is followed
from a seed by continuity in 0.005 steps of alpha.
Usage: python wangler_figures.py [pdf]   writes results/wangler-figures-11-12.{csv,json} and the QA overlay PNG.
"""
import csv
import hashlib
import json
import math
import subprocess
import sys
import tempfile
from pathlib import Path

from PIL import Image, ImageDraw

HERE = Path(__file__).resolve().parent
OUT = HERE / "results" / "wangler-figures-11-12"
PDF = Path("/home/tnnrpolley21/Zotero/storage/G7ZTAJZS/Wangler et al. - 2018 - Prediction of CO2 and H2S solubility and "
           "enthalpy of absorption in reacting N-methyldiethanolamine .pdf")
DPI, PAGE = 600, 8
# panel: crop box as page fractions (left, top, right, bottom); seeds (T in K: [(alpha, p in bar)]) read by eye from the
# panel, several per line where markers interrupt it
PANELS = {  # guides: eye-read (alpha, p bar) polylines that only assign each measured line pixel to its isotherm
    "Fig. 11 (w_MDEA 0.32, total pressure)": ((0.50, 0.07, 0.97, 0.30), {
        413.15: [(0.056, 4.16), (0.101, 5.35), (0.205, 11.79), (0.306, 22.6), (0.407, 34.33), (0.507, 49.8), (0.608, 65.82),
                 (0.709, 83.03), (0.784, 100.0)],
        393.15: [(0.041, 1.96), (0.101, 2.25), (0.205, 3.36), (0.306, 5.87), (0.407, 9.79), (0.507, 17.1), (0.608, 29.87),
                 (0.709, 49.8), (0.809, 75.66), (0.903, 100.0)],
        373.15: [(0.294, 1.89), (0.407, 3.36), (0.507, 5.35), (0.608, 9.34), (0.709, 18.76), (0.809, 35.97), (0.91, 59.97),
                 (1.026, 100.0)],
        333.15: [(0.603, 1.08), (0.698, 1.75), (0.789, 3.21), (0.89, 7.41), (0.99, 17.1), (1.091, 35.97), (1.192, 68.95),
                 (1.232, 95.46)],
        313.15: [(0.649, 0.4), (0.749, 0.96), (0.849, 2.32), (0.95, 5.87), (1.051, 14.87), (1.151, 35.97), (1.242, 91.12)]}),
    "Fig. 12 (w_MDEA 0.48, axis 'log(p_CO2)')": ((0.50, 0.30, 0.97, 0.50), {
        353.15: [(0.35, 1.09), (0.478, 2.1), (0.679, 6.41), (0.88, 20.54), (1.009, 49.74)],
        313.15: [(0.78, 0.75), (0.81, 1.45), (0.86, 3.19), (0.921, 6.72), (0.981, 15.53), (1.059, 29.81), (1.122, 52.11),
                 (1.179, 79.23)]}),
}
TOLERANCE_PX = 45  # 0.15 decade: wider than the guide reading error, narrower than the gap between isotherms
DARK, WHITE = 110, 215


def frame(px, W, H):
    cols = [x for x in range(W) if sum(px[x, y] < DARK for y in range(H)) > 0.45 * H]
    rows = [y for y in range(H) if sum(px[x, y] < DARK for x in range(W)) > 0.5 * W]
    left = [x for x in cols if x < W / 2]
    right = [x for x in cols if x > W / 2]
    top = [y for y in rows if y < H / 2]
    bottom = [y for y in rows if y > H / 2]
    return sum(left) / len(left), sum(right) / len(right), sum(top) / len(top), sum(bottom) / len(bottom)


def ticks(px, f):
    """Interior major ticks: bottom-axis columns (alpha 0.2 ... 1.2) and left-axis rows (p 1 and 10 bar)."""
    left, right, top, bottom = f
    xs = [x for x in range(int(left) + 8, int(right) - 8) if sum(px[x, y] < DARK for y in range(int(bottom) - 45, int(bottom) - 6)) > 30]
    ys = [y for y in range(int(top) + 8, int(bottom) - 8) if sum(px[x, y] < DARK for x in range(int(left) + 6, int(left) + 45)) > 32]
    group = lambda v: [sum(g) / len(g) for g in _clusters(v)]  # noqa: E731
    return group(xs), group(ys)


def _clusters(values):
    out = []
    for v in values:
        if out and v - out[-1][-1] <= 2:
            out[-1].append(v)
        else:
            out.append([v])
    return out


def runs(px, x, top, bottom):
    """Dark runs in column x that have white paper on both sides (lines, not marker outlines)."""
    out, y0 = [], None
    for y in range(int(top) + 12, int(bottom) - 12):
        dark = px[x, y] < DARK
        if dark and y0 is None:
            y0 = y
        if not dark and y0 is not None:
            if y - y0 <= 40 and px[x, y0 - 5] > WHITE and px[x, y + 4] > WHITE:  # steep lines give long runs
                out.append((y0 + y - 1) / 2)
            y0 = None
    return out


def digitize(image, box, seeds):
    W, H = image.size
    crop = image.crop((int(W * box[0]), int(H * box[1]), int(W * box[2]), int(H * box[3]))).convert("L")
    px = crop.load()
    f = frame(px, *crop.size)
    left, right, top, bottom = f
    to_px = lambda a, p: (left + a / 1.4 * (right - left), bottom - (math.log10(p) + 1) / 3 * (bottom - top))  # noqa: E731
    to_data = lambda x, y: ((x - left) / (right - left) * 1.4, 10 ** ((bottom - y) / (bottom - top) * 3 - 1))  # noqa: E731
    xt, yt = ticks(px, f)
    check = {"alpha_ticks": [round(to_data(x, 0)[0], 4) for x in xt], "p_ticks_bar": [round(to_data(0, y)[1], 4) for y in yt]}
    points = []
    for x in range(int(left) + 20, int(right) - 20, 6):  # every 6 px column (alpha step ~0.005)
        line_px = runs(px, x, top, bottom)
        for T, guide in seeds.items():
            a = to_data(x, 0)[0]
            if not guide[0][0] <= a <= guide[-1][0]:
                continue
            k = next(i for i in range(1, len(guide)) if a <= guide[i][0])
            (a1, p1), (a2, p2) = guide[k - 1], guide[k]
            y_guide = to_px(a, 10 ** (math.log10(p1) + (a - a1) / (a2 - a1) * (math.log10(p2) - math.log10(p1))))[1]
            near = [y for y in line_px if abs(y - y_guide) < TOLERANCE_PX]
            if len(near) == 1:  # exactly one line pixel run near this isotherm's guide: unambiguous
                points.append({"T_K": T, "alpha": round(a, 4), "p_bar": to_data(x, near[0])[1], "pixel_x": x, "pixel_y": near[0]})
    claimed = {}
    for p in points:  # a run within tolerance of two guides is ambiguous: drop it for both isotherms
        claimed.setdefault((p["pixel_x"], p["pixel_y"]), []).append(p["T_K"])
    return crop, f, check, [p for p in points if len(claimed[(p["pixel_x"], p["pixel_y"])]) == 1]


def main(pdf=PDF):
    with tempfile.TemporaryDirectory() as tmp:
        subprocess.run(["pdftoppm", "-r", str(DPI), "-f", str(PAGE), "-l", str(PAGE), "-png", str(pdf), f"{tmp}/p"], check=True)
        page = Image.open(next(Path(tmp).glob("p-*.png")))
        page.load()
    rows, meta, overlays = [], {"source": {"citation": "Wangler et al. 2018, Fluid Phase Equilib. 461, 15-27",
                                           "zotero_parent": "ZILDPWWE", "zotero_attachment": "G7ZTAJZS",
                                           "pdf_sha256": hashlib.sha256(Path(pdf).read_bytes()).hexdigest(),
                                           "pdf_page": PAGE, "printed_page": 22, "dpi": DPI}, "panels": {}}, []
    for panel, (box, seeds) in PANELS.items():
        crop, f, check, points = digitize(page, box, seeds)
        rows += [{"figure": panel, **p} for p in points]
        meta["panels"][panel] = {"crop_page_fractions": box, "frame_px": dict(zip(("left", "right", "top", "bottom"), f)),
                                 "axes": "alpha 0 to 1.4 linear at the frame; p 0.1 to 100 bar log10 at the frame",
                                 "interior_major_ticks_read_back": check, "seeds": seeds, "points": len(points)}
        overlay = crop.convert("RGB")
        draw = ImageDraw.Draw(overlay)
        for p in points:
            draw.ellipse((p["pixel_x"] - 3, p["pixel_y"] - 3, p["pixel_x"] + 3, p["pixel_y"] + 3), outline=(220, 0, 0))
        overlays.append(overlay)
    sheet = Image.new("RGB", (max(o.width for o in overlays), sum(o.height for o in overlays)), "white")
    y = 0
    for o in overlays:
        sheet.paste(o, (0, y))
        y += o.height
    sheet.save(f"{OUT}-overlay.png")
    with open(f"{OUT}.csv", "w", newline="") as handle:
        writer = csv.DictWriter(handle, list(rows[0]), lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)
    Path(f"{OUT}.json").write_text(json.dumps(meta, indent=1) + "\n")
    print(json.dumps({k: (v["points"], v["interior_major_ticks_read_back"]) for k, v in meta["panels"].items()}, indent=1))


if __name__ == "__main__":
    main(Path(sys.argv[1]) if len(sys.argv) > 1 else PDF)
