"""Figures for Chapter 20, Suitability Modeling.

Usage: python suitability.py

Every landscape here is made up: a synthetic elevation surface, soils, and
roads on a 200 x 200 grid of 30 m cells (6 km on a side), generated from a
fixed random seed so the figures are reproducible.
"""
from pathlib import Path

import numpy as np
from matplotlib.colors import ListedColormap, LinearSegmentedColormap
from matplotlib.patches import FancyBboxPatch, Ellipse, Rectangle
from scipy import ndimage

from style import (plt, save, NAVY, PINE, BLUE, BASIN, CORNER, FOG, CLAY, POPLAR,
                   GINKGO, SAND, DOGWOOD, BERRY, DUSK, LAND, WATER)

OUT = Path(__file__).resolve().parents[2] / "images" / "suitability-modeling"
OUT.mkdir(parents=True, exist_ok=True)

SUIT = LinearSegmentedColormap.from_list("suit", ["#F3F4F4", DOGWOOD, PINE, NAVY])
N, CELL = 200, 30.0  # cells, meters
rng = np.random.default_rng(370)


# ---------------------------------------------------------------- landscape
def landscape():
    y, x = np.mgrid[0:N, 0:N] * CELL
    z = np.full((N, N), 150.0)
    hills = [(4200, 4300, 900, 420), (1500, 4800, 700, 260), (4800, 1400, 800, 300),
             (2600, 2300, 500, 140), (900, 1300, 600, 180), (5600, 5400, 500, 200)]
    for cx, cy, s, h in hills:
        z += 2.6 * h * np.exp(-((x - cx) ** 2 + (y - cy) ** 2) / (2 * s ** 2))
    z += ndimage.gaussian_filter(rng.normal(0, 1, (N, N)), 5) * 160
    gy, gx = np.gradient(z, CELL)
    slope = np.degrees(np.arctan(np.hypot(gx, gy)))
    # Aspect: degrees clockwise from north, rows run south to north here.
    aspect = (np.degrees(np.arctan2(-gx, -gy)) + 360) % 360
    soils_noise = ndimage.gaussian_filter(rng.normal(0, 1, (N, N)), 12)
    soils = np.digitize(soils_noise, np.quantile(soils_noise, [0.3, 0.65]))  # 0,1,2
    septic_ok = soils != 0
    roads = np.zeros((N, N), bool)
    pts = [[(0, 30), (60, 55), (120, 60), (199, 95)],
           [(85, 0), (90, 70), (70, 140), (80, 199)],
           [(120, 60), (160, 140), (199, 170)]]
    for line in pts:
        for (c0, r0), (c1, r1) in zip(line[:-1], line[1:]):
            n = int(max(abs(c1 - c0), abs(r1 - r0))) * 2 + 1
            cc = np.linspace(c0, c1, n).round().astype(int).clip(0, N - 1)
            rr = np.linspace(r0, r1, n).round().astype(int).clip(0, N - 1)
            roads[rr, cc] = True
    dist = ndimage.distance_transform_edt(~roads) * CELL
    return z, slope, aspect, soils, septic_ok, roads, dist


def road_rank(d):
    """0 under 300 m and over 2,000 m, rising to 1 at 1,100 m, then falling."""
    r = np.where(d < 1100, (d - 300) / 800, (2000 - d) / 900)
    return np.clip(r, 0, 1)


def slope_rank(s):
    """Continuous: 1 on flat ground, falling toward 0 near 50 degrees."""
    return np.clip(np.exp(-s / 16.0), 0, 1)


def show(ax, a, cmap, title, vmin=None, vmax=None, cbar=None, fig=None):
    im = ax.imshow(a, origin="lower", cmap=cmap, vmin=vmin, vmax=vmax, interpolation="nearest")
    ax.set_title(title, fontsize=11.5)
    ax.set_xticks([]); ax.set_yticks([])
    for s in ax.spines.values():
        s.set_color(BASIN)
    if cbar and fig is not None:
        cb = fig.colorbar(im, ax=ax, fraction=0.046, pad=0.03)
        cb.set_label(cbar, fontsize=9)
        cb.ax.tick_params(labelsize=8)
    return im


# ---------------------------------------------------------------- flowchart
def data_box(ax, x, y, text, fc=SAND, w=2.3, h=0.8, fs=9.5, weight="normal"):
    ax.add_patch(FancyBboxPatch((x - w / 2, y - h / 2), w, h, boxstyle="square,pad=0",
                                fc=fc, ec=NAVY, lw=1.2, zorder=2))
    ax.text(x, y, text, ha="center", va="center", fontsize=fs, zorder=3, weight=weight,
            linespacing=1.1)


def op_oval(ax, x, y, text, w=2.5, h=0.85, fs=9):
    ax.add_patch(Ellipse((x, y), w, h, fc=WATER, ec=NAVY, lw=1.2, zorder=2))
    ax.text(x, y, text, ha="center", va="center", fontsize=fs, zorder=3, linespacing=1.05)


def arr(ax, a, b):
    ax.annotate("", xy=b, xytext=a, zorder=1,
                arrowprops=dict(arrowstyle="-|>", color=NAVY, lw=1.2, shrinkA=0, shrinkB=0))


def flowchart():
    fig, ax = plt.subplots(figsize=(10, 7.4))
    ax.set_xlim(0, 13); ax.set_ylim(0, 10); ax.axis("off")
    cols = {"slope": 1.6, "aspect": 4.6, "soil": 8.0, "road": 11.3}
    # Inputs
    data_box(ax, 3.1, 9.3, "Elevation", fc=SAND, weight="bold")
    data_box(ax, cols["soil"], 9.3, "Soils", fc=SAND, weight="bold")
    data_box(ax, cols["road"], 9.3, "Roads", fc=SAND, weight="bold")
    # Derive
    op_oval(ax, cols["slope"], 8.0, "Slope")
    op_oval(ax, cols["aspect"], 8.0, "Aspect")
    op_oval(ax, cols["soil"], 8.0, "Select septic-\nsuitable soils")
    op_oval(ax, cols["road"], 8.0, "Euclidean\ndistance")
    arr(ax, (2.6, 8.9), (cols["slope"] + 0.2, 8.43))
    arr(ax, (3.6, 8.9), (cols["aspect"] - 0.2, 8.43))
    arr(ax, (cols["soil"], 8.9), (cols["soil"], 8.43))
    arr(ax, (cols["road"], 8.9), (cols["road"], 8.43))
    data_box(ax, cols["slope"], 6.75, "Slope (°)")
    data_box(ax, cols["aspect"], 6.75, "Aspect (°)")
    data_box(ax, cols["soil"], 6.75, "Septic-suitable\nsoils")
    data_box(ax, cols["road"], 6.75, "Distance to\nroad (m)")
    for k in cols:
        arr(ax, (cols[k], 7.57), (cols[k], 7.15))
    # Rank
    op_oval(ax, cols["slope"], 5.45, "Reclassify\n< 30° → 1")
    op_oval(ax, cols["aspect"], 5.45, "Reclassify\n90°–270° → 1")
    op_oval(ax, cols["soil"], 5.45, "Reclassify\nsuitable → 1")
    op_oval(ax, cols["road"], 5.45, "Reclassify\n300–2,000 m → 1")
    for k in cols:
        arr(ax, (cols[k], 6.35), (cols[k], 5.88))
    for k, lab in [("slope", "Slope\nsuitability"), ("aspect", "Aspect\nsuitability"),
                   ("soil", "Soil\nsuitability"), ("road", "Road\nsuitability")]:
        data_box(ax, cols[k], 4.2, lab, fc=DOGWOOD)
        arr(ax, (cols[k], 5.02), (cols[k], 4.6))
    # Weight
    for k, w in [("slope", 1), ("aspect", 4), ("soil", 2), ("road", 3)]:
        ax.text(cols[k] + 1.25, 3.62, f"× {w}", ha="left", va="center", fontsize=10,
                weight="bold", color=BERRY)
    op_oval(ax, 6.45, 2.35, "Weighted sum\n(add weighted layers)", w=3.6, h=1.0)
    for k in cols:
        arr(ax, (cols[k], 3.8), (6.45 + (cols[k] - 6.45) * 0.28, 2.85))
    data_box(ax, 6.45, 0.85, "Suitability index\n(0 to 10)", fc=PINE, w=2.9, h=0.95,
             weight="bold")
    ax.texts[-1].set_color("white")
    arr(ax, (6.45, 1.85), (6.45, 1.33))
    # Legend
    data_box(ax, 0.95, 1.6, "Data", w=1.3, h=0.55, fs=9)
    op_oval(ax, 0.95, 0.8, "Operation", w=1.6, h=0.6, fs=9)
    ax.text(0.15, 2.25, "Key", fontsize=9.5, weight="bold")
    ax.text(11.9, 2.35, "Weights", fontsize=9.5, weight="bold", color=BERRY, ha="center")
    ax.text(11.9, 1.95, "set how much\neach layer counts", fontsize=8.5, color=BERRY,
            ha="center", va="top")
    save(fig, OUT / "home-site-flowchart.png")


# ---------------------------------------------------------------- ranking curves
def ranking_curves():
    fig, axs = plt.subplots(1, 3, figsize=(11, 3.3))
    s = np.linspace(0, 50, 400)
    ax = axs[0]
    ax.plot(s, (s < 30).astype(float), color=CLAY, lw=2.4, drawstyle="steps-post")
    ax.set_title("Discrete: slope < 30°")
    ax.set_xlabel("Slope (degrees)")
    ax = axs[1]
    ax.plot(s, slope_rank(s), color=PINE, lw=2.4)
    ax.set_title("Continuous: flatter is better")
    ax.set_xlabel("Slope (degrees)")
    ax = axs[2]
    d = np.linspace(0, 3000, 400)
    ax.plot(d, road_rank(d), color=BLUE, lw=2.4)
    ax.axvspan(0, 300, color=FOG, zorder=0)
    ax.axvspan(2000, 3000, color=FOG, zorder=0)
    ax.text(150, 0.5, "too\nclose", ha="center", fontsize=8.5, color=BASIN)
    ax.text(2500, 0.5, "too far", ha="center", fontsize=8.5, color=BASIN)
    ax.set_title("Continuous: distance to road")
    ax.set_xlabel("Distance to nearest road (m)")
    for a in axs:
        a.set_ylim(-0.05, 1.12)
        a.set_ylabel("Suitability")
        a.spines[["top", "right"]].set_visible(False)
    fig.tight_layout()
    save(fig, OUT / "ranking-curves.png")


# ---------------------------------------------------------------- derive and rank
def derive_and_rank(z, slope, roads, dist):
    fig, axs = plt.subplots(2, 3, figsize=(11, 7.6))
    show(axs[0, 0], np.where(roads, 1, 0), ListedColormap(["#F7F7F7", NAVY]), "Roads")
    show(axs[0, 1], dist, "Blues_r", "Distance to road (m)", cbar="meters", fig=fig)
    show(axs[0, 2], road_rank(dist), SUIT, "Road suitability", 0, 1, cbar="0 to 1", fig=fig)
    show(axs[1, 0], z, "terrain", "Elevation (m)", cbar="meters", fig=fig)
    show(axs[1, 1], slope, "YlOrBr", "Slope (degrees)", cbar="degrees", fig=fig)
    show(axs[1, 2], slope_rank(slope), SUIT, "Slope suitability", 0, 1, cbar="0 to 1", fig=fig)
    fig.tight_layout()
    save(fig, OUT / "derive-and-rank.png")


# ---------------------------------------------------------------- combine methods
def grid(ax, a, title, cmap, vmin, vmax, fmt="{:g}", hl=None):
    ax.imshow(a, cmap=cmap, vmin=vmin, vmax=vmax)
    for (r, c), v in np.ndenumerate(a):
        col = "white" if (cmap is SUIT and (v - vmin) / max(vmax - vmin, 1e-9) > 0.55) else NAVY
        ax.text(c, r, fmt.format(v), ha="center", va="center", fontsize=10.5, color=col,
                weight="bold" if hl == (r, c) else "normal")
    if hl:
        ax.add_patch(Rectangle((hl[1] - 0.5, hl[0] - 0.5), 1, 1, fill=False, ec=CLAY, lw=2.6))
    ax.set_xticks(np.arange(-0.5, a.shape[1], 1), minor=True)
    ax.set_yticks(np.arange(-0.5, a.shape[0], 1), minor=True)
    ax.grid(which="minor", color="white", lw=1.5)
    ax.tick_params(which="both", length=0, labelbottom=False, labelleft=False)
    ax.set_title(title, fontsize=10.5)


def combine_methods():
    A = np.array([[1, 1, 0, 0], [1, 1, 1, 0], [0, 1, 1, 1], [0, 0, 1, 1]])   # slope
    B = np.array([[1, 0, 0, 1], [1, 1, 0, 1], [1, 1, 1, 1], [0, 1, 1, 0]])   # aspect
    C = np.array([[0, 1, 1, 1], [1, 1, 1, 1], [1, 0, 1, 1], [1, 1, 0, 0]])   # soils
    w = (1, 4, 2)
    hl = (2, 1)
    bin_cmap = ListedColormap([FOG, DOGWOOD])
    fig, axs = plt.subplots(2, 3, figsize=(9.6, 6.6))
    grid(axs[0, 0], A, "A: slope (weight 1)", bin_cmap, 0, 1, hl=hl)
    grid(axs[0, 1], B, "B: aspect (weight 4)", bin_cmap, 0, 1, hl=hl)
    grid(axs[0, 2], C, "C: soils (weight 2)", bin_cmap, 0, 1, hl=hl)
    grid(axs[1, 0], A * B * C, "Pass/fail: multiply\nA × B × C", bin_cmap, 0, 1, hl=hl)
    grid(axs[1, 1], A + B + C, "Ranking: add\nA + B + C", SUIT, 0, 3, hl=hl)
    grid(axs[1, 2], w[0] * A + w[1] * B + w[2] * C, "Rating: weight, then add\n1A + 4B + 2C",
         SUIT, 0, 7, hl=hl)
    fig.text(0.5, 0.975, "Criteria (top, 1 = pass, 0 = fail) and three ways to combine them (bottom)", ha="center", fontsize=12, weight="bold")
    fig.tight_layout(rect=(0, 0, 1, 0.96), h_pad=3)
    save(fig, OUT / "combine-methods.png")


# ---------------------------------------------------------------- result and sensitivity
def result(slope, aspect, septic_ok, dist):
    s = (slope < 30).astype(float)
    a = ((aspect > 90) & (aspect < 270)).astype(float)
    so = septic_ok.astype(float)
    r = ((dist > 300) & (dist < 2000)).astype(float)
    cm = ListedColormap([FOG, DOGWOOD])
    fig, axs = plt.subplots(2, 4, figsize=(12, 6.7),
                            gridspec_kw=dict(height_ratios=[1, 1.55]))
    for ax, lay, t in zip(axs[0], [s, a, so, r],
                          ["Slope < 30°\n(weight 1)", "Aspect 90°–270°\n(weight 4)",
                           "Septic-suitable soil\n(weight 2)", "300–2,000 m from road\n(weight 3)"]):
        show(ax, lay, cm, t, 0, 1)
    for ax in axs[1]:
        ax.remove()
    gs = axs[0, 0].get_gridspec()
    a1 = fig.add_subplot(gs[1, 0:2]); a2 = fig.add_subplot(gs[1, 2:4])
    idx1 = 1 * s + 4 * a + 2 * so + 3 * r
    idx2 = 4 * s + 1 * a + 2 * so + 3 * r
    im = show(a1, idx1, SUIT, "Weights 1, 4, 2, 3 (aspect counts most)", 0, 10)
    show(a2, idx2, SUIT, "Weights 4, 1, 2, 3 (slope counts most)", 0, 10)
    for ax, idx in [(a1, idx1), (a2, idx2)]:
        rr, cc = np.where(idx == 10)
        pct = 100 * (idx == 10).mean()
        ax.contour(idx == 10, levels=[0.5], colors=[CLAY], linewidths=1.4, origin="lower")
        ax.text(3, 192, f"Score 10: {pct:.0f}% of cells", fontsize=9.5, color=CLAY,
                va="top", weight="bold",
                bbox=dict(fc="white", ec="none", alpha=0.85, pad=2))
        hi = (idx >= 8).mean() * 100
        ax.text(3, 178, f"Score 8 or more: {hi:.0f}%", fontsize=9.5, color=NAVY, va="top",
                bbox=dict(fc="white", ec="none", alpha=0.85, pad=2))
    cb = fig.colorbar(im, ax=[a1, a2], fraction=0.025, pad=0.02)
    cb.set_label("Suitability index", fontsize=9.5)
    print("score10 pct", 100 * (idx1 == 10).mean(), "idx>=8 w1", (idx1 >= 8).mean() * 100,
          "w2", (idx2 >= 8).mean() * 100)
    print("same top cells?", ((idx1 >= 8) & (idx2 >= 8)).sum(), (idx1 >= 8).sum(), (idx2 >= 8).sum())
    save(fig, OUT / "home-site-result.png")


if __name__ == "__main__":
    z, slope, aspect, soils, septic_ok, roads, dist = landscape()
    print("slope max", slope.max(), "dist max", dist.max())
    flowchart()
    ranking_curves()
    derive_and_rank(z, slope, roads, dist)
    combine_methods()
    result(slope, aspect, septic_ok, dist)
