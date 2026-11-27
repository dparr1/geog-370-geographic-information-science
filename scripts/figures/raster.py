"""Figures for Chapter 14, Raster Analysis.

Usage: python raster.py

All rasters are made up. The terrain is a smooth random surface (fixed seed).
"""
from pathlib import Path

import numpy as np
import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle, FancyArrowPatch
from matplotlib.colors import LightSource, ListedColormap

from style import NAVY, PINE, BLUE, BASIN, CORNER, FOG, CLAY, POPLAR, GINKGO, SAND, DOGWOOD, BERRY, save

OUT = Path(__file__).parent.parent.parent / "images" / "raster"
OUT.mkdir(parents=True, exist_ok=True)

N = None  # NoData
NODATA_FC = "#d9d9d9"


# ---------- helpers ----------
def grid(ax, vals, x0, y0, title=None, cmap="Blues", vmin=None, vmax=None, fs=10.5,
         colors=None, hi=None, hi_col=CLAY, cell=1.0, fmt="{:g}", title_fs=10.5):
    """Draw a grid of values with its top-left at (x0, y0 + rows). None is NoData."""
    vals = [list(r) for r in vals]
    nr, nc = len(vals), len(vals[0])
    nums = [v for r in vals for v in r if isinstance(v, (int, float)) and v is not None]
    if nums:
        vmin = min(nums) if vmin is None else vmin
        vmax = max(nums) if vmax is None else vmax
    cm = plt.get_cmap(cmap) if isinstance(cmap, str) else cmap
    for i in range(nr):
        for j in range(nc):
            v = vals[i][j]
            x, y = x0 + j * cell, y0 + (nr - 1 - i) * cell
            if v is None:
                fc, txt = NODATA_FC, "N"
            elif colors is not None:
                fc, txt = colors.get(v, "white"), str(v)
            elif isinstance(v, str):
                fc, txt = SAND, v
            else:
                f = 0.12 + 0.55 * (v - vmin) / (vmax - vmin + 1e-9)
                fc, txt = cm(f), fmt.format(v)
            ax.add_patch(Rectangle((x, y), cell, cell, fc=fc, ec="white", lw=1.5))
            ax.text(x + cell / 2, y + cell / 2, txt, ha="center", va="center", fontsize=fs,
                    color=NAVY, style="italic" if v is None else "normal")
    if hi:
        for (r0, c0, r1, c1) in hi:
            ax.add_patch(Rectangle((x0 + c0 * cell, y0 + (nr - 1 - r1) * cell), (c1 - c0 + 1) * cell,
                                   (r1 - r0 + 1) * cell, fill=False, ec=hi_col, lw=2.4, zorder=5))
    if title:
        ax.text(x0 + nc * cell / 2, y0 + nr * cell + 0.3, title, ha="center", fontsize=title_fs,
                color=NAVY, weight="bold")
    return nr, nc


def op(ax, x, y, s, fs=18):
    ax.text(x, y, s, ha="center", va="center", fontsize=fs, color=NAVY, weight="bold")


def clean(ax, lim):
    ax.set_xlim(lim[0], lim[1])
    ax.set_ylim(lim[2], lim[3])
    ax.set_aspect("equal")
    ax.set_axis_off()


def terrain(n=200, seed=15):
    """A smooth made-up elevation surface in meters."""
    rng = np.random.default_rng(seed)
    x = np.linspace(0, 1, n)
    X, Y = np.meshgrid(x, x)
    z = np.zeros_like(X)
    for _ in range(14):
        cx, cy = rng.uniform(-0.1, 1.1, 2)
        s = rng.uniform(0.08, 0.3)
        a = rng.uniform(-1, 1.6)
        z += a * np.exp(-((X - cx) ** 2 + (Y - cy) ** 2) / (2 * s ** 2))
    z += 0.9 * Y  # higher to the north
    z = (z - z.min()) / (z.max() - z.min())
    return z * 900 + 100


def slope_deg(z, cell):
    gy, gx = np.gradient(z, cell)
    return np.degrees(np.arctan(np.hypot(gx, gy)))


# ---------- 1. the raster model ----------
def raster_model():
    fig, ax = plt.subplots(figsize=(7.6, 5.2))
    nr, nc = 5, 7
    rng = np.random.default_rng(3)
    v = rng.integers(1, 9, (nr, nc))
    cm = plt.get_cmap("YlGn")
    for i in range(nr):
        for j in range(nc):
            ax.add_patch(Rectangle((j, nr - 1 - i), 1, 1, fc=cm(0.15 + 0.08 * v[i, j]), ec="white", lw=1.5))
            ax.text(j + 0.5, nr - 1 - i + 0.5, str(v[i, j]), ha="center", va="center", fontsize=10, color=NAVY)
    # highlight a cell: row 1, column 4
    r, c = 1, 6
    ax.add_patch(Rectangle((c, nr - 1 - r), 1, 1, fill=False, ec=CLAY, lw=2.6, zorder=5))
    ax.annotate("Row 1, column 6\nx = x₀ + 6 × cell size\ny = y₀ + 3 × cell size", xy=(c + 1, nr - 1 - r + 0.5),
                xytext=(nc + 0.5, nr - 0.6), fontsize=9.5, color=CLAY, va="top",
                arrowprops=dict(arrowstyle="-|>", color=CLAY, lw=1.2))
    # origin
    ax.scatter([0], [0], s=60, c=NAVY, zorder=6)
    ax.text(-0.2, -0.1, "Lower-left corner\n(x₀, y₀)", ha="right", va="top", fontsize=9.5, color=NAVY)
    # cell size
    ax.annotate("", xy=(0, -0.35), xytext=(1, -0.35), arrowprops=dict(arrowstyle="<->", color=NAVY, lw=1.2))
    ax.text(1.15, -0.35, "Cell size", ha="left", va="center", fontsize=9.5, color=NAVY)
    # extent
    ax.add_patch(Rectangle((0, 0), nc, nr, fill=False, ec=NAVY, lw=1.6, ls="--"))
    ax.annotate("", xy=(0, nr + 0.35), xytext=(nc, nr + 0.35), arrowprops=dict(arrowstyle="<->", color=BASIN, lw=1.2))
    ax.text(nc / 2, nr + 0.5, "Extent: 7 columns × cell size", ha="center", fontsize=9.5, color=BASIN)
    # row/col numbers
    for j in range(nc):
        ax.text(j + 0.5, nr + 0.05, str(j), ha="center", va="bottom", fontsize=8, color=BASIN)
    for i in range(nr):
        ax.text(-0.12, nr - 1 - i + 0.5, str(i), ha="right", va="center", fontsize=8, color=BASIN)
    clean(ax, (-2.6, nc + 4.2, -1.3, nr + 1.0))
    save(fig, OUT / "raster-model.png")


# ---------- 2. map algebra with NoData ----------
A3 = [[1, 4, 4], [3, 1, 2], [4, 1, 2]]
B3 = [[-1, 3, 3], [-1, 4, 2], [1, 3, N]]


def add(a, b):
    return [[N if (x is None or y is None) else x + y for x, y in zip(ra, rb)] for ra, rb in zip(a, b)]


def map_algebra():
    fig, ax = plt.subplots(figsize=(9, 3.3))
    C = add(A3, B3)
    grid(ax, A3, 0, 0, "Raster A", vmin=-1, vmax=7)
    op(ax, 3.6, 1.5, "+")
    grid(ax, B3, 4.2, 0, "Raster B", vmin=-1, vmax=7)
    op(ax, 7.8, 1.5, "=")
    grid(ax, C, 8.4, 0, "Raster C", cmap="Purples", vmin=-1, vmax=7,
         hi=[(0, 0, 0, 0), (2, 2, 2, 2)])
    grid(ax, A3, 0, 0, None, vmin=-1, vmax=7, hi=[(0, 0, 0, 0)], fs=10.5)
    grid(ax, B3, 4.2, 0, None, vmin=-1, vmax=7, hi=[(0, 0, 0, 0)], fs=10.5)
    ax.text(5.7, -0.55, "1 + (−1) = 0 in the top-left cell.   2 + NoData = NoData in the bottom-right cell.",
            ha="center", fontsize=9.5, color=CLAY)
    clean(ax, (-0.2, 11.6, -0.9, 3.8))
    save(fig, OUT / "map-algebra-add.png")


# ---------- 3. mismatched grids ----------
def mismatch():
    fig, axes = plt.subplots(1, 2, figsize=(10.5, 4.4))
    ax = axes[0]
    for i in range(3):
        for j in range(3):
            ax.add_patch(Rectangle((j * 2, i * 2), 2, 2, fc=DOGWOOD, ec=PINE, lw=1.8, alpha=0.6))
    for i in range(8):
        for j in range(8):
            ax.add_patch(Rectangle((1.3 + j * 0.75, 1.3 + i * 0.75), 0.75, 0.75, fill=False, ec=BLUE, lw=0.9))
    ax.add_patch(Rectangle((2, 2), 2, 2, fill=False, ec=CLAY, lw=2.6, zorder=5))
    ax.text(3, 3, "B", ha="center", va="center", fontsize=14, weight="bold", color=CLAY, zorder=6,
            bbox=dict(fc="white", ec="none", alpha=0.8, pad=1))
    ax.set_title("Cell B overlaps parts of 16 fine cells", fontsize=11.5, loc="left")
    ax.legend([Rectangle((0, 0), 1, 1, fc=DOGWOOD, ec=PINE, alpha=0.6), Rectangle((0, 0), 1, 1, fill=False, ec=BLUE)],
              ["Layer 1: coarse cells", "Layer 2: fine cells"], loc="upper center", bbox_to_anchor=(0.5, 0.0),
              ncol=2, frameon=False, fontsize=9.5)
    clean(ax, (-0.3, 7.5, -0.3, 7.5))
    ax = axes[1]
    ax.add_patch(Rectangle((0, 0), 6, 6, fc=DOGWOOD, ec=PINE, lw=1.8, alpha=0.6))
    ax.add_patch(Rectangle((1.3, 1.3), 6, 6, fc=BLUE, ec=BLUE, lw=1.8, alpha=0.25))
    ax.add_patch(Rectangle((1.3, 1.3), 4.7, 4.7, fill=False, ec=CLAY, lw=2.4, ls="--"))
    ax.text(3.65, 3.65, "Intersection:\nboth layers\nhave data", ha="center", va="center", fontsize=10, color=CLAY,
            weight="bold")
    ax.text(0.6, 0.6, "Layer 1 only", fontsize=9.5, color=PINE)
    ax.text(6.9, 7.0, "Layer 2 only", fontsize=9.5, color=NAVY, ha="right")
    ax.set_title("Different extents", fontsize=11.5, loc="left")
    clean(ax, (-0.3, 7.6, -0.3, 7.6))
    save(fig, OUT / "mismatch.png")


# ---------- 4. resampling ----------
def resampling():
    """Resample a 4x4 categorical raster onto a 3x3 grid with the same extent."""
    lc = np.array([[1, 1, 2, 2], [1, 1, 2, 3], [4, 1, 3, 3], [4, 4, 3, 3]])
    names = {1: "Forest", 2: "Farm", 3: "Water", 4: "Urban"}
    cols = {1: "#7fb77e", 2: GINKGO, 3: BLUE, 4: CLAY}
    fig, axes = plt.subplots(1, 3, figsize=(12.5, 4.6))
    s = 4 / 3
    centers = [((j + 0.5) * s, (2 - i + 0.5) * s) for i in range(3) for j in range(3)]

    def draw_input(ax, alpha=1.0):
        for i in range(4):
            for j in range(4):
                ax.add_patch(Rectangle((j, 3 - i), 1, 1, fc=cols[lc[i, j]], ec="white", lw=1.5, alpha=alpha))

    def val(cx, cy):  # input value at a cell center (col cx, row-from-bottom cy), clamped
        j = min(max(int(cx), 0), 3)
        i = 3 - min(max(int(cy), 0), 3)
        return lc[i, j]

    ax = axes[0]
    draw_input(ax)
    for i in range(4):
        for j in range(4):
            ax.text(j + 0.5, 3 - i + 0.5, str(lc[i, j]), ha="center", va="center", fontsize=10.5, color=NAVY)
    for k in range(4):
        ax.plot([k * s, k * s], [0, 4], color=NAVY, lw=1.6, ls="--")
        ax.plot([0, 4], [k * s, k * s], color=NAVY, lw=1.6, ls="--")
    ax.set_title("4 × 4 input; new 3 × 3 grid (dashed)", fontsize=11, loc="left")
    clean(ax, (-0.2, 4.2, -0.2, 4.2))

    ax = axes[1]
    draw_input(ax, alpha=0.15)
    nn = []
    for (x, y) in centers:
        v = val(x, y)
        nn.append(v)
        ax.add_patch(Rectangle((x - s / 2, y - s / 2), s, s, fc=cols[v], ec="white", lw=1.5))
        ax.text(x, y, str(v), ha="center", va="center", fontsize=11, color=NAVY)
    ax.set_title("Nearest neighbor: only real classes", fontsize=11, loc="left")
    clean(ax, (-0.2, 4.2, -0.2, 4.2))

    ax = axes[2]
    draw_input(ax, alpha=0.15)
    bil = []
    for (x, y) in centers:
        # bilinear between the four nearest input cell centers
        fx, fy = x - 0.5, y - 0.5
        j0, i0 = int(np.floor(fx)), int(np.floor(fy))
        tx, ty = fx - j0, fy - i0
        v00, v10 = val(j0 + 0.5, i0 + 0.5), val(j0 + 1.5, i0 + 0.5)
        v01, v11 = val(j0 + 0.5, i0 + 1.5), val(j0 + 1.5, i0 + 1.5)
        v = (v00 * (1 - tx) * (1 - ty) + v10 * tx * (1 - ty) + v01 * (1 - tx) * ty + v11 * tx * ty)
        v = round(v, 2)
        bil.append(v)
        bad = abs(v - round(v)) > 1e-6
        ax.add_patch(Rectangle((x - s / 2, y - s / 2), s, s, fc="white" if bad else cols[int(round(v))],
                               ec=CORNER, lw=1.2))
        ax.text(x, y, f"{v:g}", ha="center", va="center", fontsize=11, color=CLAY if bad else NAVY,
                weight="bold" if bad else "normal")
    ax.set_title("Bilinear: averages make fake classes", fontsize=11, loc="left")
    clean(ax, (-0.2, 4.2, -0.2, 4.2))
    fig.legend([Rectangle((0, 0), 1, 1, fc=cols[k]) for k in names], [f"{k} = {n}" for k, n in names.items()],
               loc="lower center", ncol=4, frameon=False, fontsize=9.5, bbox_to_anchor=(0.5, 0.0))
    save(fig, OUT / "resampling.png")
    print("nearest", nn, "bilinear", bil)


# ---------- 5. four scopes ----------
S_IN = [[10, 12, 30, 9], [8, 42, 5, 14], [-12, 8, 20, 3], [6, 1, 17, 11]]
ZONES = [["a", "a", "b", "b"], ["a", "a", "b", "b"], ["c", "c", "c", "b"], ["c", "c", "c", "b"]]


def focal_max(a):
    a = np.array(a)
    out = np.zeros_like(a)
    for i in range(4):
        for j in range(4):
            out[i, j] = a[max(i - 1, 0):i + 2, max(j - 1, 0):j + 2].max()
    return out.tolist()


def zone_mean(a, z):
    a = np.array(a, float)
    z = np.array(z)
    out = np.zeros_like(a)
    for k in np.unique(z):
        out[z == k] = a[z == k].mean()
    return np.round(out, 1).tolist()


def scopes():
    fig, axes = plt.subplots(2, 2, figsize=(11, 6.6))
    kw = dict(vmin=-12, vmax=46)
    # local
    ax = axes[0, 0]
    grid(ax, S_IN, 0, 0, "Input", hi=[(0, 0, 0, 0)], **kw)
    op(ax, 5.0, 2, "+ 4", fs=15)
    grid(ax, (np.array(S_IN) + 4).tolist(), 6, 0, "Output", cmap="Purples", hi=[(0, 0, 0, 0)], **kw)
    ax.set_title("Local: the same cell (add 4)", fontsize=12, loc="left")
    ax.text(5, -0.6, "10 + 4 = 14", ha="center", fontsize=10, color=CLAY)
    clean(ax, (-0.2, 10.2, -1.0, 4.9))
    # focal
    ax = axes[0, 1]
    fm = focal_max(S_IN)
    grid(ax, S_IN, 0, 0, "Input", hi=[(0, 0, 2, 2)], **kw)
    op(ax, 5.0, 2, "max", fs=14)
    grid(ax, fm, 6, 0, "Output", cmap="Purples", hi=[(1, 1, 1, 1)], **kw)
    ax.set_title("Neighborhood: a 3×3 window (maximum)", fontsize=12, loc="left")
    ax.text(5, -0.6, "The largest value in the window, 42, goes to its center", ha="center", fontsize=10, color=CLAY)
    clean(ax, (-0.2, 10.2, -1.0, 4.9))
    # zonal
    ax = axes[1, 0]
    zc = {"a": SAND, "b": DOGWOOD, "c": "#dbe9f6"}
    grid(ax, ZONES, 0, 0, "Zones", colors=zc, fs=10)
    zm = zone_mean(S_IN, ZONES)
    for i in range(4):
        for j in range(4):
            ax.add_patch(Rectangle((5.5 + j, 3 - i), 1, 1, fc=zc[ZONES[i][j]], ec="white", lw=1.5))
            ax.text(5.5 + j + 0.5, 3 - i + 0.5, f"{zm[i][j]:g}", ha="center", va="center", fontsize=9.5, color=NAVY)
    ax.text(7.5, 4.3, "Output: zone mean", ha="center", fontsize=10.5, weight="bold", color=NAVY)
    op(ax, 4.75, 2, "→", fs=16)
    ax.set_title("Zonal: every cell in the zone", fontsize=12, loc="left")
    ax.text(4.75, -0.6, "Zone a: (10 + 12 + 8 + 42) ÷ 4 = 18", ha="center", fontsize=10, color=CLAY)
    clean(ax, (-0.2, 10.2, -1.0, 4.9))
    # global
    ax = axes[1, 1]
    grid(ax, S_IN, 0, 0, "Input", hi=[(0, 0, 3, 3)], **kw)
    op(ax, 5.0, 2, "max", fs=14)
    grid(ax, [[42] * 4] * 4, 6, 0, "Output", cmap="Purples", **kw)
    ax.set_title("Global: every cell (maximum)", fontsize=12, loc="left")
    ax.text(5, -0.6, "The largest value anywhere, 42, goes to every cell", ha="center", fontsize=10, color=CLAY)
    clean(ax, (-0.2, 10.2, -1.0, 4.9))
    fig.subplots_adjust(hspace=0.25, wspace=0.12)
    save(fig, OUT / "scopes.png")
    return fm, zm


# ---------- 6. cell size: fine and coarse ----------
def cell_size():
    z = terrain(240)
    fig, axes = plt.subplots(1, 3, figsize=(13, 4.6))
    ls = LightSource(azdeg=315, altdeg=45)
    for ax, k, t in zip(axes, (1, 8, 40), ("Fine cells (1 unit)", "8 times coarser", "40 times coarser")):
        n = 240 // k
        zz = z[:n * k, :n * k].reshape(n, k, n, k).mean(axis=(1, 3))
        rgb = ls.shade(zz, cmap=plt.get_cmap("gist_earth"), vert_exag=0.06 * k, blend_mode="soft",
                       vmin=0, vmax=1200)
        ax.imshow(rgb, origin="lower", interpolation="nearest")
        ax.set_title(f"{t}: {n} × {n} cells", fontsize=11.5, loc="left")
        ax.set_xticks([])
        ax.set_yticks([])
        for s in ax.spines.values():
            s.set_color(CORNER)
    save(fig, OUT / "cell-size.png")


# ---------- 7. elevation x slope ----------
def elev_slope():
    z = terrain(200)
    cell = 30.0
    s = slope_deg(z, cell)
    ls = LightSource(azdeg=315, altdeg=45)
    hs = ls.hillshade(z, vert_exag=2, dx=cell, dy=cell)
    fig, axes = plt.subplots(1, 3, figsize=(13.5, 4.8))
    zn = (z - z.min()) / (z.max() - z.min())
    sn = (s - s.min()) / (s.max() - s.min())
    for ax, data, cmap, t, lab in [
        (axes[0], z, "gist_earth", "A: elevation (m)", "Elevation (m)"),
        (axes[1], s, "RdYlGn_r", "B: slope (degrees)", "Slope (°)"),
        (axes[2], zn * sn, "magma", "Rescaled A × rescaled B", "Index (0–1)"),
    ]:
        im = ax.imshow(data, origin="lower", cmap=cmap)
        ax.imshow(hs, origin="lower", cmap="gray", alpha=0.25)
        ax.set_title(t, fontsize=11.5, loc="left")
        ax.set_xticks([])
        ax.set_yticks([])
        cb = fig.colorbar(im, ax=ax, fraction=0.046, pad=0.03)
        cb.set_label(lab, fontsize=9)
        cb.ax.tick_params(labelsize=8)
    save(fig, OUT / "elevation-slope.png")
    print("elev range", z.min(), z.max(), "slope max", s.max())


# ---------- 8. logical ----------
L1 = [[1, 3, 1, 1], [0, N, 2, -1], [4, 2, 6, 3]]
L2 = [[0, 1, 0, 9], [0, 4, 2, 5], [5, 2, 1, N]]


def logical():
    def lt(a, b):
        return [[N if (x is None or y is None) else int(x < y) for x, y in zip(ra, rb)] for ra, rb in zip(a, b)]

    def eq(a, b):
        return [[N if (x is None or y is None) else int(x == y) for x, y in zip(ra, rb)] for ra, rb in zip(a, b)]

    isn = [[int(x is None) for x in r] for r in L2]
    bin_cols = {0: "#f2f2f2", 1: GINKGO}
    fig, axes = plt.subplots(3, 1, figsize=(9, 9.6))
    for ax, t, out, sym in [(axes[0], "Less than: 1 where A < B", lt(L1, L2), "<"),
                            (axes[1], "Equal: 1 where A = B", eq(L1, L2), "=")]:
        grid(ax, L1, 0, 0, "A", vmin=-1, vmax=9)
        op(ax, 4.6, 1.5, sym)
        grid(ax, L2, 5.2, 0, "B", vmin=-1, vmax=9)
        op(ax, 9.8, 1.5, "→")
        grid(ax, out, 10.4, 0, "Output", colors=bin_cols)
        ax.set_title(t, fontsize=12, loc="left")
        clean(ax, (-0.2, 14.6, -0.3, 3.8))
    ax = axes[2]
    grid(ax, L2, 5.2, 0, "B", vmin=-1, vmax=9)
    op(ax, 4.0, 1.5, "ISNULL", fs=13)
    op(ax, 9.8, 1.5, "→")
    grid(ax, isn, 10.4, 0, "Output", colors=bin_cols)
    ax.set_title("ISNULL: 1 where B is NoData (never outputs N)", fontsize=12, loc="left")
    clean(ax, (-0.2, 14.6, -0.3, 3.8))
    save(fig, OUT / "logical.png")
    return lt(L1, L2), eq(L1, L2)


# ---------- 9. reclassification ----------
def reclass():
    fig, axes = plt.subplots(1, 2, figsize=(12, 4.2))
    # by table: land cover codes to a 1-5 suitability score
    ax = axes[0]
    lc = [[11, 11, 41, 41], [21, 82, 41, 42], [21, 82, 82, 90], [24, 21, 82, 90]]
    table = {11: 0, 21: 2, 24: 1, 41: 4, 42: 4, 82: 5, 90: 3}
    out = [[table[v] for v in r] for r in lc]
    grid(ax, lc, 0, 0, "Land-cover code", cmap="Greens", fs=10)
    grid(ax, out, 9.2, 0, "Suitability", cmap="YlOrBr", vmin=0, vmax=5, fs=10)
    rows = ["11 Water → 0", "21 Developed, open → 2", "24 Developed, high → 1", "41 Deciduous forest → 4",
            "42 Evergreen forest → 4", "82 Cultivated crops → 5", "90 Woody wetlands → 3"]
    ax.text(4.35, 4.0, "Lookup table", fontsize=9.5, weight="bold", color=NAVY, va="top")
    for k, r in enumerate(rows):
        ax.text(4.3, 3.45 - k * 0.5, r, fontsize=8.3, color=NAVY, va="top")
    ax.set_title("(a) By table: exact values", fontsize=12, loc="left")
    clean(ax, (-0.2, 13.4, -0.3, 4.8))
    # by ranges: slope to classes
    ax = axes[1]
    sl = [[2, 4, 9, 14], [3, 7, 12, 22], [N, 5, 16, 31], [1, 6, 18, 27]]

    def cls(v):
        if v is None:
            return "d"
        return "a" if v < 5 else ("b" if v < 15 else "c")

    out = [[cls(v) for v in r] for r in sl]
    grid(ax, sl, 0, 0, "Slope (°)", cmap="Reds", fs=10)
    grid(ax, out, 9.2, 0, "Class", colors={"a": DOGWOOD, "b": GINKGO, "c": "#f4a582", "d": NODATA_FC}, fs=10)
    rows = ["0 to < 5 → a (gentle)", "5 to < 15 → b (moderate)", "15 and up → c (steep)", "NoData → d"]
    ax.text(4.3, 4.0, "Ranges", fontsize=9.5, weight="bold", color=NAVY, va="top")
    for k, r in enumerate(rows):
        ax.text(4.3, 3.45 - k * 0.5, r, fontsize=8.3, color=NAVY, va="top")
    ax.set_title("(b) By ranges: continuous values", fontsize=12, loc="left")
    clean(ax, (-0.2, 13.4, -0.3, 4.8))
    save(fig, OUT / "reclass.png")


# ---------- 10. conditional ----------
CB = [[-1, 3, 3], [-1, 4, 2], [1, 3, 9]]
CC = [[8, 3, 6], [-1, 5, 4], [1, 9, N]]


def conditional():
    out = [[(b if a == 1 else c) for a, b, c in zip(ra, rb, rc)] for ra, rb, rc in zip(A3, CB, CC)]
    pick = [[a == 1 for a in r] for r in A3]
    fig, ax = plt.subplots(figsize=(12, 3.8))
    cond = [["yes" if p else "no" for p in r] for r in pick]
    grid(ax, A3, 0, 0, "A", vmin=-1, vmax=9)
    op(ax, 3.6, 1.5, "→", fs=15)
    grid(ax, cond, 4.2, 0, "A = 1?", colors={"yes": DOGWOOD, "no": "#f4c7c3"}, fs=9.5)
    grid(ax, CB, 8.0, 0, "B (if yes)", vmin=-1, vmax=9)
    grid(ax, CC, 11.6, 0, "C (if no)", vmin=-1, vmax=9)
    op(ax, 15.2, 1.5, "→", fs=15)
    grid(ax, out, 15.8, 0, "Output", cmap="Purples", vmin=-1, vmax=9)
    for i in range(3):
        for j in range(3):
            x0 = 8.0 if pick[i][j] else 11.6
            ax.add_patch(Rectangle((x0 + j, 2 - i), 1, 1, fill=False, ec=PINE if pick[i][j] else CLAY, lw=2,
                                   zorder=5))
    ax.text(9.4, -0.6, "Outlined cells are the ones copied. The bottom-right comes from C, so it is NoData.",
            ha="center", fontsize=9.5, color=NAVY)
    clean(ax, (-0.2, 19.0, -1.0, 3.8))
    save(fig, OUT / "conditional.png")
    return out


# ---------- 11. neighborhood statistics ----------
def neighborhood_stats():
    w = np.array([[1, 2, 3], [3, 6, 6], [3, 9, 2]])
    fig, ax = plt.subplots(figsize=(9, 4.2))
    grid(ax, w.tolist(), 0, 0.5, "A 3×3 window", cmap="Blues", fs=12)
    vals = w.ravel()
    u, c = np.unique(vals, return_counts=True)
    stats = [("Mean", f"{vals.sum()} ÷ 9 = {vals.mean():.1f}"),
             ("Median", f"{np.median(vals):g} (the middle of the sorted values)"),
             ("Minimum", f"{vals.min()}"), ("Maximum", f"{vals.max()}"),
             ("Range", f"{vals.max()} − {vals.min()} = {np.ptp(vals)}"),
             ("Sum", f"{vals.sum()}"),
             ("Majority", f"{u[c.argmax()]} (appears {c.max()} times)"),
             ("Variety", f"{len(u)} different values")]
    for k, (n, s) in enumerate(stats):
        y = 3.6 - k * 0.48
        ax.text(4.0, y, n, fontsize=10.5, weight="bold", color=NAVY, va="center")
        ax.text(5.6, y, s, fontsize=10.5, color=NAVY, va="center")
    ax.text(1.5, 0.0, "Each result is written to\nthe center cell only", ha="center", va="top", fontsize=9.5,
            color=CLAY)
    clean(ax, (-0.2, 11, -0.9, 4.2))
    save(fig, OUT / "neighborhood-stats.png")
    return vals.mean()


# ---------- 12. aggregation ----------
FINE = [[3, 2, 2, 5, 6, 5, 0, 0, 0],
        [3, 1, 1, 7, 7, 6, 1, 1, 1],
        [3, 2, 1, 7, 6, 6, 0, 0, 0],
        [1, 2, 3, 9, 9, 9, 1, 0, 1],
        [3, 2, 1, 10, 10, 10, 5, 5, 0],
        [1, 3, 2, 8, 8, 8, 5, 5, 5],
        [N, N, N, 3, 3, 3, 10, 20, 30],
        [N, N, N, 3, 3, 3, 30, 30, 10],
        [N, N, N, 3, 3, 3, 20, 10, 20]]


def aggregate():
    coarse = []
    for bi in range(3):
        row = []
        for bj in range(3):
            b = [FINE[i][j] for i in range(bi * 3, bi * 3 + 3) for j in range(bj * 3, bj * 3 + 3)]
            b = [v for v in b if v is not None]
            row.append(round(float(np.mean(b)), 1) if b else None)
        coarse.append(row)
    fig, ax = plt.subplots(figsize=(10, 4.8))
    grid(ax, FINE, 0, 0, "9 × 9 fine raster", cmap="YlGnBu", vmin=0, vmax=30, fs=9.5, cell=0.5,
         hi=[(0, 0, 2, 2), (3, 0, 5, 2), (6, 0, 8, 2), (0, 3, 2, 5), (3, 3, 5, 5), (6, 3, 8, 5),
             (0, 6, 2, 8), (3, 6, 5, 8), (6, 6, 8, 8)], hi_col=NAVY)
    ax.add_patch(Rectangle((0, 3.0), 1.5, 1.5, fill=False, ec=CLAY, lw=2.8, zorder=6))
    op(ax, 5.6, 2.25, "→", fs=18)
    grid(ax, coarse, 6.6, 0, "3 × 3 coarse raster (mean)", cmap="YlGnBu", vmin=0, vmax=30, fs=11, cell=1.5,
         hi=[(0, 0, 0, 0)])
    ax.text(5.6, -0.45, "Top-left block: (3+2+2+3+1+1+3+2+1) ÷ 9 = 2", ha="center", fontsize=9.5, color=CLAY)
    clean(ax, (-0.2, 11.4, -0.8, 5.2))
    save(fig, OUT / "aggregate.png")
    return coarse


# ---------- 13. majority filter ----------
def majority_filter():
    crops = [["B", "B", "B", "C", "C"],
             ["B", "B", "B", "C", "C"],
             ["B", "C", "B", "B", "C"],
             ["B", "B", "B", "C", "C"],
             ["W", "W", "B", "C", "C"]]
    a = np.array(crops)
    out = a.copy()
    for i in range(5):
        for j in range(5):
            nb = [a[i + di, j + dj] for di, dj in ((-1, 0), (1, 0), (0, -1), (0, 1))
                  if 0 <= i + di < 5 and 0 <= j + dj < 5]
            u, c = np.unique(nb, return_counts=True)
            if c.max() > len(nb) / 2:
                out[i, j] = u[c.argmax()]
    cols = {"B": "#c6a15b", "C": GINKGO, "W": BLUE}
    fig, ax = plt.subplots(figsize=(9, 3.9))
    grid(ax, crops, 0, 0, "Classified image", colors=cols, fs=10, hi=[(2, 1, 2, 1)])
    op(ax, 6.5, 2.5, "→", fs=18)
    grid(ax, out.tolist(), 8, 0, "After a majority filter", colors=cols, fs=10, hi=[(2, 1, 2, 1)])
    changed = int((a != out).sum())
    ax.legend([Rectangle((0, 0), 1, 1, fc=cols[k]) for k in "BCW"], ["B = beans", "C = corn", "W = water"],
              loc="upper center", bbox_to_anchor=(0.5, 0.02), ncol=3, frameon=False, fontsize=9.5)
    clean(ax, (-0.2, 13.2, -0.3, 5.8))
    save(fig, OUT / "majority-filter.png")
    print("majority filter changed", changed, "cells")


# ---------- 14. global: distance to a river ----------
def distance():
    n = 120
    x = np.linspace(0, 10, n)
    X, Y = np.meshgrid(x, x)
    rx = 5 + 1.6 * np.sin(np.linspace(0, 10, 400) / 1.6)
    ry = np.linspace(0, 10, 400)
    d = np.full_like(X, np.inf)
    for a, b in zip(rx, ry):
        d = np.minimum(d, np.hypot(X - a, Y - b))
    fig, axes = plt.subplots(1, 2, figsize=(10.5, 4.6))
    ax = axes[0]
    ax.imshow(np.zeros_like(X), origin="lower", extent=(0, 10, 0, 10), cmap=ListedColormap(["#f4f4f4"]))
    ax.plot(rx, ry, color=BLUE, lw=3)
    ax.set_title("Source: a river", fontsize=11.5, loc="left")
    ax2 = axes[1]
    im = ax2.imshow(d * 100, origin="lower", extent=(0, 10, 0, 10), cmap="YlOrRd_r")
    ax2.contour(X, Y, d * 100, levels=[100, 200, 300, 400], colors=NAVY, linewidths=0.6)
    ax2.plot(rx, ry, color=BLUE, lw=3)
    ax2.set_title("Euclidean distance to the river (m)", fontsize=11.5, loc="left")
    cb = fig.colorbar(im, ax=ax2, fraction=0.046, pad=0.03)
    cb.ax.tick_params(labelsize=8)
    for a in axes:
        a.set_xticks([])
        a.set_yticks([])
        for s in a.spines.values():
            s.set_color(CORNER)
    save(fig, OUT / "distance.png")


if __name__ == "__main__":
    raster_model()
    map_algebra()
    mismatch()
    resampling()
    fm, zm = scopes()
    print("focal max", fm)
    print("zone mean", zm)
    cell_size()
    elev_slope()
    print("logical", logical())
    reclass()
    print("con", conditional())
    print("nbhd mean", neighborhood_stats())
    print("coarse", aggregate())
    majority_filter()
    distance()
