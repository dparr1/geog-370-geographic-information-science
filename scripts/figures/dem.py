"""Figures for Chapter 13, Digital Elevation Models.

Usage: python dem.py

The terrain maps use a real DEM of Linville Gorge, North Carolina:
data/linville_dem_10m_utm17n.tif, a USGS 3DEP 1/3 arc-second DEM (public
domain) reprojected to NAD83 / UTM zone 17N at 10 m and stored as whole
decimeters. Slope, aspect, hillshade, and viewshed are computed here with
numpy, using the same formulas as ArcGIS Pro (Horn's method), so no GIS
software is needed. The diagrams and worked examples use made-up numbers.
Needs numpy, scipy, matplotlib, and rasterio.
"""
from pathlib import Path

import numpy as np
import rasterio
from matplotlib.colors import LightSource, ListedColormap, BoundaryNorm, LinearSegmentedColormap
from matplotlib.patches import Rectangle, Polygon as MPoly, FancyArrowPatch, Circle, Arc, Wedge
from matplotlib.lines import Line2D
from scipy import ndimage

from style import (plt, save, NAVY, PINE, BLUE, BASIN, CORNER, FOG, CLAY, POPLAR,
                   GINKGO, SAND, DOGWOOD, BERRY, DUSK, LAND, WATER)

HERE = Path(__file__).resolve().parent
OUT = HERE.parents[1] / "images" / "dem"
OUT.mkdir(parents=True, exist_ok=True)

# ---------------------------------------------------------------- data
with rasterio.open(HERE / "data" / "linville_dem_10m_utm17n.tif") as src:
    DEM = src.read(1).astype(float) / 10.0  # decimeters to meters
    T = src.transform
CELL = 10.0
NR, NC = DEM.shape
X0, Y1 = T.c, T.f  # upper-left corner
EXTENT = [X0, X0 + NC * CELL, Y1 - NR * CELL, Y1]

# Table Rock summit (observer for the viewshed), in UTM 17N.
from pyproj import Transformer
TR_X, TR_Y = Transformer.from_crs("EPSG:4326", "EPSG:26917", always_xy=True).transform(-81.8830, 35.8911)

ELEV_CMAP = LinearSegmentedColormap.from_list(
    "elev", ["#3d7a54", "#8db673", "#d9d39a", "#c9a46b", "#9b6b46", "#f2efe9"])


# ---------------------------------------------------------------- surface math
def horn(z, d):
    """dz/dx (east) and dz/dy (north) by Horn's method, as in ArcGIS Pro."""
    p = np.pad(z, 1, mode="edge")
    a, b, c = p[:-2, :-2], p[:-2, 1:-1], p[:-2, 2:]
    dd, f = p[1:-1, :-2], p[1:-1, 2:]
    g, h, i = p[2:, :-2], p[2:, 1:-1], p[2:, 2:]
    dzdx = ((c + 2 * f + i) - (a + 2 * dd + g)) / (8 * d)
    dzdy = ((g + 2 * h + i) - (a + 2 * b + c)) / (8 * d)
    return dzdx, dzdy


def slope_deg(z, d):
    dx, dy = horn(z, d)
    return np.degrees(np.arctan(np.hypot(dx, dy)))


def aspect_deg(z, d):
    """Compass aspect, 0-360 clockwise from north; -1 where flat (ArcGIS formula)."""
    dx, dy = horn(z, d)
    a = np.degrees(np.arctan2(dy, -dx))
    asp = np.where(a < 0, 90.0 - a, np.where(a > 90, 360.0 - a + 90.0, 90.0 - a))
    return np.where((dx == 0) & (dy == 0), -1.0, asp)


def hillshade(z, d, az=315.0, alt=45.0):
    dx, dy = horn(z, d)
    s = np.arctan(np.hypot(dx, dy))
    asp = np.radians(np.where(aspect_deg(z, d) < 0, 0, aspect_deg(z, d)))
    zen = np.radians(90 - alt)
    v = np.cos(zen) * np.cos(s) + np.sin(zen) * np.sin(s) * np.cos(np.radians(az) - asp)
    return np.clip(255 * v, 0, 255)


def viewshed(z, d, r0, c0, h_obs=1.7, refraction=0.13):
    """Visible (True) cells from (r0, c0): line of sight to every cell, with
    Earth curvature and refraction corrected as in ArcGIS Pro."""
    R = 6371000.0
    nr, nc = z.shape
    rr, cc = np.mgrid[0:nr, 0:nc]
    dist = np.hypot(rr - r0, cc - c0) * d
    corr = (1 - refraction) * dist ** 2 / (2 * R)
    zc = z - corr
    zo = z[r0, c0] + h_obs
    with np.errstate(divide="ignore", invalid="ignore"):
        ang_t = (zc - zo) / dist  # tangent of the elevation angle to each cell
    vis = np.zeros_like(z, bool)
    vis[r0, c0] = True
    nsteps = int(np.ceil(dist.max() / d)) + 1
    flat_r, flat_c = rr.ravel(), cc.ravel()
    tgt = ang_t.ravel()
    out = np.ones(flat_r.size, bool)
    chunk = 20000
    for s0 in range(0, flat_r.size, chunk):
        r = flat_r[s0:s0 + chunk].astype(float)
        c = flat_c[s0:s0 + chunk].astype(float)
        t = tgt[s0:s0 + chunk]
        n = np.maximum(np.ceil(np.hypot(r - r0, c - c0)).astype(int), 1)
        mx = np.full(r.size, -np.inf)
        for k in range(1, nsteps):
            f = k / n
            live = f < 1
            if not live.any():
                break
            rs = r0 + (r[live] - r0) * f[live]
            cs = c0 + (c[live] - c0) * f[live]
            zi = ndimage.map_coordinates(zc, [rs, cs], order=1)
            di = np.hypot(rs - r0, cs - c0) * d
            a = (zi - zo) / di
            mx[live] = np.maximum(mx[live], a)
        out[s0:s0 + chunk] = t >= mx
    vis = out.reshape(z.shape)
    vis[r0, c0] = True
    return vis


def km_axes(ax, label=True):
    ax.set_xticks([]); ax.set_yticks([])
    for s in ax.spines.values():
        s.set_color(CORNER)


def scalebar(ax, extent, length=2000, color="white"):
    x0 = extent[0] + 0.06 * (extent[1] - extent[0])
    y0 = extent[2] + 0.05 * (extent[3] - extent[2])
    ax.plot([x0, x0 + length], [y0, y0], color=color, lw=3, solid_capstyle="butt")
    ax.text(x0 + length / 2, y0 + 0.02 * (extent[3] - extent[2]), f"{length/1000:g} km",
            ha="center", va="bottom", color=color, fontsize=9.5, weight="bold")


def north(ax, extent, color="white"):
    x = extent[1] - 0.07 * (extent[1] - extent[0])
    y = extent[3] - 0.13 * (extent[3] - extent[2])
    ax.annotate("N", xy=(x, y + 0.08 * (extent[3] - extent[2])), xytext=(x, y), ha="center",
                color=color, fontsize=11, weight="bold",
                arrowprops=dict(arrowstyle="-|>", color=color, lw=1.6))


# ---------------------------------------------------------------- contours vs. grid
def contours_vs_grid():
    """The same small area as contour lines (vector) and as a grid of cells (raster)."""
    r0, c0, n = 1050, 760, 160  # a 1.6 km square
    sub = DEM[r0:r0 + n, c0:c0 + n]
    fig, axs = plt.subplots(1, 3, figsize=(12.5, 4.4), gridspec_kw=dict(width_ratios=[1, 1, 1]))
    ax = axs[0]
    ax.set_facecolor("#f7f3e8")
    levels = np.arange(np.floor(sub.min() / 20) * 20, sub.max() + 20, 20)
    cs = ax.contour(sub[::-1], levels=levels, colors="#9b6b46", linewidths=0.7)
    idx = [l for l in levels if l % 100 == 0]
    cs2 = ax.contour(sub[::-1], levels=idx, colors="#7a4a2a", linewidths=1.6)
    ax.clabel(cs2, fmt="%d", fontsize=8)
    ax.set_aspect("equal"); km_axes(ax)
    ax.set_title("Contours (vector)\nevery 20 m, labels every 100 m", fontsize=11.5)

    ax = axs[1]
    agg = sub.reshape(16, 10, 16, 10).mean(axis=(1, 3))
    ax.imshow(agg, cmap=ELEV_CMAP, vmin=sub.min(), vmax=sub.max())
    for k in range(17):
        ax.axhline(k - 0.5, color="white", lw=0.5); ax.axvline(k - 0.5, color="white", lw=0.5)
    ax.add_patch(Rectangle((5.5, 5.5), 4, 4, fill=False, ec=CLAY, lw=2.5))
    km_axes(ax)
    ax.set_title("DEM (raster)\n100 m cells, one elevation each", fontsize=11.5)

    ax = axs[2]
    z = agg[6:10, 6:10]
    ax.imshow(z, cmap=ELEV_CMAP, vmin=sub.min(), vmax=sub.max())
    for i in range(4):
        for j in range(4):
            ax.text(j, i, f"{z[i, j]:.0f}", ha="center", va="center", fontsize=13, color=NAVY,
                    weight="bold")
    for k in range(5):
        ax.axhline(k - 0.5, color="white", lw=2); ax.axvline(k - 0.5, color="white", lw=2)
    for s in ax.spines.values():
        s.set_color(CLAY); s.set_linewidth(2.5)
    ax.set_xticks([]); ax.set_yticks([])
    ax.set_title("Zoom: the numbers\nelevation in meters", fontsize=11.5)
    fig.tight_layout()
    save(fig, OUT / "contours-vs-grid.png")


# ---------------------------------------------------------------- 3D
def dem_3d():
    step = 8
    z = DEM[::step, ::step]
    ny, nx = z.shape
    X, Y = np.meshgrid(np.arange(nx) * CELL * step, (ny - 1 - np.arange(ny)) * CELL * step)
    ls = LightSource(azdeg=315, altdeg=45)
    norm = (z - z.min()) / (z.max() - z.min())
    rgb = ls.shade(z, cmap=ELEV_CMAP, vert_exag=2, blend_mode="soft", dx=CELL * step, dy=CELL * step)
    fig = plt.figure(figsize=(9, 5.4))
    ax = fig.add_subplot(projection="3d")
    ax.plot_surface(X, Y, z, facecolors=rgb, rstride=1, cstride=1, linewidth=0, antialiased=False,
                    shade=False)
    ax.set_box_aspect((nx, ny, 0.22 * max(nx, ny)))
    ax.view_init(elev=32, azim=-112)
    ax.set_axis_off()
    fig.subplots_adjust(0, 0, 1, 1)
    save(fig, OUT / "dem-3d.png")
    from PIL import Image, ImageChops
    im = Image.open(OUT / "dem-3d.png").convert("RGB")
    bbox = ImageChops.difference(im, Image.new("RGB", im.size, "white")).getbbox()
    im.crop((max(bbox[0] - 20, 0), max(bbox[1] - 20, 0), bbox[2] + 20, bbox[3] + 20)).save(OUT / "dem-3d.png")


# ---------------------------------------------------------------- DEM vs DSM
def dem_dsm():
    x = np.linspace(0, 100, 1000)
    ground = 10 + 6 * np.sin(x / 18) + 0.04 * x
    surface = ground.copy()
    trees = [(12, 5, 13), (20, 4, 11), (27, 5, 14), (34, 4, 12), (78, 5, 15), (86, 4.5, 12), (93, 4, 13)]
    fig, ax = plt.subplots(figsize=(11, 4.6))
    for cx, r, h in trees:
        gx = np.interp(cx, x, ground)
        m = np.abs(x - cx) < r
        crown = gx + h - 0.6 * h * ((x[m] - cx) / r) ** 2
        surface[m] = np.maximum(surface[m], crown)
        ax.add_patch(Rectangle((cx - 0.4, gx), 0.8, h * 0.55, fc="#7a5a3a", ec="none", zorder=2))
        t = np.linspace(-r, r, 50)
        ax.fill_between(cx + t, gx + 0.35 * h, gx + h - 0.6 * h * (t / r) ** 2, color="#5f9a5a",
                        alpha=0.9, zorder=2, lw=0)
    # a building
    bx0, bx1 = 50, 64
    gb = np.interp(bx0, x, ground)
    bh = 11
    m = (x >= bx0) & (x <= bx1)
    surface[m] = gb + bh
    ax.fill_between(x, 0, ground, color="#d7c39b", zorder=1)
    ax.plot(x, ground, color="#7a4a2a", lw=2.6, zorder=4, label="DEM / DTM: bare earth (ground returns)")
    ax.plot(x, surface + 0.15, color=CLAY, lw=2.2, ls="--", zorder=5,
            label="DSM: first surface hit (first returns)")
    ax.add_patch(Rectangle((bx0, gb - 3), bx1 - bx0, bh + 3, fc=CORNER, ec=BASIN, lw=1, zorder=4.5))
    ax.text((bx0 + bx1) / 2, gb + bh / 2, "building", ha="center", va="center", fontsize=10, color=BASIN,
            zorder=6)
    # lidar pulses, straight down
    top = 40
    for px, through in [(13, True), (27, True), (42, False), (57, False), (79, True), (92, True)]:
        gx = np.interp(px, x, ground); sx = np.interp(px, x, surface)
        ax.plot([px, px], [top, gx if through else sx], color=BERRY, lw=1.1, alpha=0.7, zorder=5.5)
        ax.scatter([px], [sx], s=40, color=CLAY, zorder=7, ec="white", lw=0.8)
        if through and sx - gx > 1:
            ax.scatter([px], [gx], s=40, color="#7a4a2a", zorder=7, ec="white", lw=0.8)
    ax.text(42, top + 1, "Lidar pulses", color=BERRY, fontsize=10.5, ha="center", va="bottom")
    ax.set_xlim(0, 100); ax.set_ylim(0, 52)
    ax.legend(loc="upper right", frameon=False, fontsize=10.5)
    ax.axis("off")
    save(fig, OUT / "dem-dsm.png")


# ---------------------------------------------------------------- resolution
def resolution():
    r0, c0, n = 900, 600, 630  # 6.3 km square
    sub = DEM[r0:r0 + n, c0:c0 + n]
    fig, axs = plt.subplots(1, 3, figsize=(12.5, 4.5))
    for ax, k, lab in zip(axs, [1, 3, 9], ["10 m cells (1/3 arc-second)", "30 m cells (1 arc-second)",
                                           "90 m cells (3 arc-second)"]):
        z = sub.reshape(n // k, k, n // k, k).mean(axis=(1, 3)) if k > 1 else sub
        hs = hillshade(z, CELL * k)
        ax.imshow(hs, cmap="gray", vmin=0, vmax=255, extent=[0, 6300, 0, 6300])
        km_axes(ax)
        cells = z.size
        ax.set_title(f"{lab}\n{cells:,} cells", fontsize=11.5)
    scalebar(axs[0], [0, 6300, 0, 6300], 1000)
    fig.tight_layout()
    save(fig, OUT / "resolution.png")


# ---------------------------------------------------------------- units mistake
def units_mistake():
    z = DEM[::3, ::3]
    good = slope_deg(z, 30.0)
    bad = slope_deg(z, 30.0 / 111320.0 / np.cos(np.radians(35.9)))  # x and y in degrees
    fig, axs = plt.subplots(1, 2, figsize=(10, 4.9))
    for ax, s, t in zip(axs, [bad, good], ["x and y in degrees, z in meters\n(no z-factor)",
                                         "Projected to UTM: x, y, and z in meters"]):
        im = ax.imshow(s, cmap="magma_r", vmin=0, vmax=90)
        km_axes(ax)
        ax.set_title(t, fontsize=11.5)
        ax.text(0.03, 0.04, f"mean slope {np.mean(s):.0f}°", transform=ax.transAxes, fontsize=10.5,
                color="white", weight="bold",
                bbox=dict(fc=NAVY, ec="none", alpha=0.8, boxstyle="round,pad=0.3"))
    cb = fig.colorbar(im, ax=axs, shrink=0.8, label="Slope (degrees)")
    save(fig, OUT / "units-mistake.png")


# ---------------------------------------------------------------- rise over run
def rise_run():
    fig, axs = plt.subplots(1, 3, figsize=(12, 3.8))
    for ax, deg in zip(axs, [10, 45, 60]):
        run = 4.0
        rise = run * np.tan(np.radians(deg))
        sc = 3.2 / max(rise, run) if rise > run else 1
        ru, ri = run * sc if rise > run else run, rise * sc if rise > run else rise
        ax.add_patch(MPoly([[0, 0], [ru, 0], [ru, ri]], fc=SAND, ec=NAVY, lw=1.6))
        ax.add_patch(Arc((0, 0), 1.6, 1.6, theta1=0, theta2=deg, color=CLAY, lw=2))
        ax.text(1.0 if deg > 20 else 1.9, 0.18 if deg > 20 else 0.75, f"{deg}°", color=CLAY, fontsize=12,
                weight="bold")
        ax.text(ru / 2, -0.35, "run", ha="center", fontsize=11)
        ax.text(ru + 0.15, ri / 2, "rise", va="center", fontsize=11)
        pct = 100 * np.tan(np.radians(deg))
        ax.set_title(f"{deg}° = {pct:.0f}%", fontsize=13)
        ax.set_xlim(-0.3, 5.2); ax.set_ylim(-0.6, 3.6)
        ax.set_aspect("equal"); ax.axis("off")
    fig.text(0.5, 0.02, "Degrees: the angle, where tan(angle) = rise ÷ run.     Percent: rise ÷ run × 100.",
             ha="center", fontsize=11)
    save(fig, OUT / "rise-run.png")


# ---------------------------------------------------------------- 3x3 window
WIN = [[70, 65, 50], [95, 80, 50], [85, 90, 80]]
LABELS = [["a", "b", "c"], ["d", "e", "f"], ["g", "h", "i"]]


def window():
    fig, axs = plt.subplots(1, 2, figsize=(10.5, 4.3), gridspec_kw=dict(width_ratios=[1, 1.35]))
    ax = axs[0]
    vals = np.array(WIN, float)
    for i in range(3):
        for j in range(3):
            v = vals[i, j]
            f = (v - 50) / 45
            ax.add_patch(Rectangle((j, 2 - i), 1, 1, fc=plt.get_cmap("YlOrBr")(0.15 + 0.6 * f),
                                   ec="white", lw=2))
            ax.text(j + 0.5, 2 - i + 0.55, f"{v:.0f}", ha="center", va="center", fontsize=17,
                    weight="bold", color=NAVY)
            ax.text(j + 0.12, 2 - i + 0.82, LABELS[i][j], fontsize=11.5, style="italic",
                    color="white" if v >= 85 else BASIN)
    ax.add_patch(Rectangle((1, 1), 1, 1, fill=False, ec=CLAY, lw=3))
    ax.annotate("", xy=(3.0, -0.25), xytext=(2.0, -0.25),
                arrowprops=dict(arrowstyle="<->", color=NAVY, lw=1.3))
    ax.text(2.5, -0.5, "D = 50 m", ha="center", va="top", fontsize=11)
    ax.text(1.5, 3.2, "N", ha="center", fontsize=12, weight="bold")
    ax.annotate("", xy=(1.5, 3.55), xytext=(1.5, 3.3), arrowprops=dict(arrowstyle="-|>", color=NAVY))
    ax.set_xlim(-0.2, 3.2); ax.set_ylim(-0.9, 3.7); ax.set_aspect("equal"); ax.axis("off")
    ax = axs[1]; ax.axis("off")
    lines = [
        ("Fleming and Hoffer (4 neighbors)", NAVY, True),
        ("east–west:  (f − d) ÷ 2D = (50 − 95) ÷ 100 = −0.45", NAVY, False),
        ("north–south:  (b − h) ÷ 2D = (65 − 90) ÷ 100 = −0.25", NAVY, False),
        ("slope = atan √(0.45² + 0.25²) = 27.2°", CLAY, True),
        ("", NAVY, False),
        ("Horn (8 neighbors, used by ArcGIS Pro)", NAVY, True),
        ("east–west:  [(c + 2f + i) − (a + 2d + g)] ÷ 8D", NAVY, False),
        ("    = (230 − 345) ÷ 400 = −0.2875", NAVY, False),
        ("north–south:  [(a + 2b + c) − (g + 2h + i)] ÷ 8D", NAVY, False),
        ("    = (250 − 345) ÷ 400 = −0.2375", NAVY, False),
        ("slope = atan √(0.2875² + 0.2375²) = 20.5°", CLAY, True),
    ]
    for k, (t, col, b) in enumerate(lines):
        ax.text(0, 1 - k * 0.088, t, fontsize=11.2, color=col, weight="bold" if b else "normal",
                transform=ax.transAxes, va="top")
    fig.tight_layout()
    save(fig, OUT / "slope-window.png")


# ---------------------------------------------------------------- Linville maps
def dem_map(ax, z=None):
    z = DEM if z is None else z
    ax.imshow(z, cmap="gray", extent=EXTENT)
    km_axes(ax)


def dem_slope():
    s = slope_deg(DEM, CELL)
    fig, axs = plt.subplots(1, 2, figsize=(11, 6.6))
    im0 = axs[0].imshow(DEM, cmap="gray", extent=EXTENT)
    km_axes(axs[0]); axs[0].set_title("Elevation (m)", fontsize=12)
    fig.colorbar(im0, ax=axs[0], shrink=0.7, orientation="horizontal", pad=0.03)
    im1 = axs[1].imshow(s, cmap="magma_r", vmin=0, vmax=60, extent=EXTENT)
    km_axes(axs[1]); axs[1].set_title("Slope (degrees)", fontsize=12)
    fig.colorbar(im1, ax=axs[1], shrink=0.7, orientation="horizontal", pad=0.03, extend="max")
    scalebar(axs[0], EXTENT, 2000); north(axs[0], EXTENT)
    fig.tight_layout()
    save(fig, OUT / "linville-slope.png")


def dem_hillshade():
    fig, axs = plt.subplots(1, 2, figsize=(11, 6.6))
    for ax, az, t in zip(axs, [315, 135], ["Sun from the northwest (315°)", "Sun from the southeast (135°)"]):
        ax.imshow(hillshade(DEM, CELL, az, 45), cmap="gray", vmin=0, vmax=255, extent=EXTENT)
        km_axes(ax); ax.set_title(f"{t}, altitude 45°", fontsize=12)
        # sun marker
        x = EXTENT[0] + (0.08 if az == 315 else 0.92) * (EXTENT[1] - EXTENT[0])
        y = EXTENT[2] + (0.92 if az == 315 else 0.08) * (EXTENT[3] - EXTENT[2])
        ax.scatter([x], [y], s=380, marker="o", color=GINKGO, ec=POPLAR, lw=2, zorder=5)
    scalebar(axs[0], EXTENT, 2000)
    fig.tight_layout()
    save(fig, OUT / "linville-hillshade.png")


def shaded_relief():
    r0, c0, n = 700, 400, 1000
    z = DEM[r0:r0 + n, c0:c0 + n]
    hs = hillshade(z, CELL)
    fig, axs = plt.subplots(1, 2, figsize=(11, 5.6))
    axs[0].imshow(z, cmap=ELEV_CMAP)
    axs[0].set_title("Color DEM", fontsize=12)
    axs[1].imshow(hs, cmap="gray", vmin=0, vmax=255)
    axs[1].imshow(z, cmap=ELEV_CMAP, alpha=0.55)
    axs[1].set_title("Color DEM, 45% transparent, over a hillshade", fontsize=12)
    for ax in axs:
        km_axes(ax)
    fig.tight_layout()
    save(fig, OUT / "shaded-relief.png")


ASPECT_CLASSES = [("Flat", "#bdbdbd"), ("N", "#e8414f"), ("NE", "#f29b38"), ("E", "#f5e04a"),
                  ("SE", "#6dc35b"), ("S", "#4fc3d9"), ("SW", "#5a8ee0"), ("W", "#3f4fb5"),
                  ("NW", "#c04fc0")]


def aspect_class(a):
    k = np.where(a < 0, 0, ((a + 22.5) % 360 // 45).astype(int) + 1)
    return k


def dem_aspect():
    a = aspect_deg(DEM, CELL)
    k = aspect_class(a)
    cmap = ListedColormap([c for _, c in ASPECT_CLASSES])
    fig = plt.figure(figsize=(11, 6.6))
    ax = fig.add_axes([0.0, 0.03, 0.62, 0.94])
    ax.imshow(k, cmap=cmap, vmin=-0.5, vmax=8.5, extent=EXTENT, interpolation="nearest")
    km_axes(ax); ax.set_title("Aspect, in eight compass directions", fontsize=12)
    scalebar(ax, EXTENT, 2000, color=NAVY)
    # compass-rose legend
    lx = fig.add_axes([0.64, 0.22, 0.34, 0.56])
    for idx, (lab, col) in enumerate(ASPECT_CLASSES[1:]):
        c = 90 - idx * 45
        lx.add_patch(Wedge((0, 0), 1, c - 22.5, c + 22.5, fc=col, ec="white", lw=2))
        r = 1.22
        lx.text(r * np.cos(np.radians(c)), r * np.sin(np.radians(c)), lab, ha="center", va="center",
                fontsize=13, weight="bold", color=NAVY)
        rr = 0.68
        lx.text(rr * np.cos(np.radians(c)), rr * np.sin(np.radians(c)), f"{idx*45}°", ha="center",
                va="center", fontsize=9, color=NAVY)
    lx.add_patch(Circle((0, 0), 0.25, fc=ASPECT_CLASSES[0][1], ec="white", lw=2))
    lx.text(0, 0, "Flat", ha="center", va="center", fontsize=9, color=NAVY)
    lx.set_xlim(-1.5, 1.5); lx.set_ylim(-1.5, 1.5); lx.set_aspect("equal"); lx.axis("off")
    save(fig, OUT / "linville-aspect.png")


def dem_viewshed():
    k = 3
    z = DEM[: NR // k * k, : NC // k * k].reshape(NR // k, k, NC // k, k).mean(axis=(1, 3))
    d = CELL * k
    c0 = int((TR_X - X0) / d); r0 = int((Y1 - TR_Y) / d)
    # put the observer on the highest cell near the summit
    win = z[r0 - 3:r0 + 4, c0 - 3:c0 + 4]
    dr, dc = np.unravel_index(np.argmax(win), win.shape)
    r0, c0 = r0 - 3 + dr, c0 - 3 + dc
    vis = viewshed(z, d, r0, c0, h_obs=1.7)
    hs = hillshade(z, d)
    ext = [X0, X0 + z.shape[1] * d, Y1 - z.shape[0] * d, Y1]
    fig, ax = plt.subplots(figsize=(7.2, 8.4))
    ax.imshow(hs, cmap="gray", vmin=0, vmax=255, extent=ext)
    over = np.zeros(z.shape + (4,))
    over[vis] = [*plt.matplotlib.colors.to_rgb(POPLAR), 0.62]
    ax.imshow(over, extent=ext, interpolation="nearest")
    ox, oy = X0 + (c0 + 0.5) * d, Y1 - (r0 + 0.5) * d
    ax.scatter([ox], [oy], marker="^", s=220, color=CLAY, ec="white", lw=1.5, zorder=5)
    ax.annotate("Table Rock", xy=(ox, oy), xytext=(ox + 1300, oy + 900), color="white", weight="bold",
                fontsize=11, arrowprops=dict(arrowstyle="-", color="white"))
    km_axes(ax)
    scalebar(ax, ext, 2000)
    north(ax, ext)
    pct = 100 * vis.mean()
    ax.legend(handles=[Rectangle((0, 0), 1, 1, fc=POPLAR, alpha=0.7, label=f"Visible ({pct:.0f}% of the area)"),
                       Rectangle((0, 0), 1, 1, fc="#888888", label="Not visible")],
              loc="lower right", fontsize=10, framealpha=0.9)
    save(fig, OUT / "linville-viewshed.png")


# ---------------------------------------------------------------- hillshade geometry
def sun_geometry():
    fig, axs = plt.subplots(1, 2, figsize=(11, 4.6))
    ax = axs[0]  # top view: azimuth
    ax.add_patch(Circle((0, 0), 1, fill=False, ec=CORNER, lw=1.5))
    for lab, ang in [("N", 90), ("E", 0), ("S", 270), ("W", 180)]:
        ax.text(1.18 * np.cos(np.radians(ang)), 1.18 * np.sin(np.radians(ang)), lab, ha="center",
                va="center", fontsize=13, weight="bold")
    sa = np.radians(90 - 315)
    sx, sy = np.cos(sa), np.sin(sa)
    ax.scatter([sx], [sy], s=500, color=GINKGO, ec=POPLAR, lw=2, zorder=5)
    ax.annotate("", xy=(0, 0), xytext=(0.85 * sx, 0.85 * sy),
                arrowprops=dict(arrowstyle="-|>", color=POPLAR, lw=2.2))
    ax.add_patch(Arc((0, 0), 0.7, 0.7, theta1=135, theta2=450, color=CLAY, lw=2))
    ax.annotate("", xy=(0.35 * np.cos(np.radians(137)), 0.35 * np.sin(np.radians(137))),
                xytext=(0.35 * np.cos(np.radians(150)), 0.35 * np.sin(np.radians(150))),
                arrowprops=dict(arrowstyle="-|>", color=CLAY, lw=2))
    ax.plot([0, 0], [0, 0.95], color=BASIN, lw=1, ls=":")
    ax.text(0.5, -0.72, "azimuth 315°\nclockwise from north", color=CLAY, fontsize=10.5, ha="center")
    ax.set_title("Seen from above: the sun's azimuth", fontsize=12)
    ax.set_xlim(-1.4, 1.4); ax.set_ylim(-1.4, 1.4); ax.set_aspect("equal"); ax.axis("off")

    ax = axs[1]  # side view: altitude and a facet
    ax.plot([-1.7, 1.8], [0, 0], color=BASIN, lw=1.2)
    ax.add_patch(MPoly([[0.2, 0], [1.6, 0], [1.6, 0.6]], fc="#d7c39b", ec="#7a4a2a", lw=1.5))
    ax.add_patch(Arc((0.2, 0), 0.9, 0.9, theta1=0, theta2=np.degrees(np.arctan(0.6 / 1.4)), color=PINE, lw=2))
    ax.text(0.72, 0.05, "facet slope", color=PINE, fontsize=10)
    sx, sy = -1.55, 1.45
    ax.scatter([sx], [sy], s=500, color=GINKGO, ec=POPLAR, lw=2, zorder=5)
    px = -0.25  # ray meeting the ground at 45 degrees
    ax.plot([sx + 0.15, px], [sy - 0.15, 0], color=POPLAR, lw=1.8)
    ax.add_patch(Arc((px, 0), 0.8, 0.8, theta1=135, theta2=180, color=CLAY, lw=2))
    ax.text(-1.45, 0.1, "sun altitude 45°", color=CLAY, fontsize=10.5)
    for fx in [0.7, 1.1, 1.45]:
        fy = 0.6 * (fx - 0.2) / 1.4
        ax.annotate("", xy=(fx, fy), xytext=(fx - 0.75, fy + 0.75),
                    arrowprops=dict(arrowstyle="-|>", color=POPLAR, lw=1.6))
    ax.set_title("Seen from the side: altitude and slope", fontsize=12)
    ax.set_xlim(-1.8, 1.9); ax.set_ylim(-0.3, 1.7); ax.set_aspect("equal"); ax.axis("off")
    fig.tight_layout()
    save(fig, OUT / "sun-geometry.png")


# ---------------------------------------------------------------- line of sight
def line_of_sight():
    fig, ax = plt.subplots(figsize=(10, 4.6))
    d = [0, 30, 60, 100]
    z = [50, 43, 28, 20]
    xs = np.linspace(0, 100, 200)
    prof = np.interp(xs, d, z) + 1.2 * np.sin(xs / 6)
    prof[0], prof[-1] = 50, 20
    prof = np.interp(xs, d, z)
    ax.fill_between(xs, 0, prof, color="#d7c39b")
    ax.plot(xs, prof, color="#7a4a2a", lw=2)
    ax.plot([0, 100], [50, 20], color=CLAY, lw=1.6, ls="--")
    ax.plot([0, 30], [50, 43], color=PINE, lw=1.6, ls=":")
    ax.plot([0, 60], [50, 28], color=BLUE, lw=1.6, ls=":")
    pts = [(0, 50, "Observer\n(50 m)", NAVY), (30, 43, "P2\n30 m away, 43 m\nangle −13.1°", PINE),
           (60, 28, "P1\n60 m away, 28 m\nangle −20.1°", BLUE), (100, 20, "Target\n100 m away, 20 m\nangle −16.7°", CLAY)]
    for x, y, lab, col in pts:
        ax.scatter([x], [y], s=70, color=col, zorder=5, ec="white")
        ax.text(x + (2 if x < 100 else 0), y + 3 if x < 100 else y - 6, lab, color=col, fontsize=10,
                ha="left" if x < 100 else "right", va="bottom" if x < 100 else "top", weight="bold")
    ax.text(50, 3, "P2's angle (−13.1°) is higher than the target's (−16.7°), so P2 blocks the view.",
            ha="center", fontsize=10.5, color=NAVY)
    ax.set_xlim(-3, 104); ax.set_ylim(0, 70)
    ax.set_xlabel("Distance from observer (m)"); ax.set_ylabel("Elevation (m)")
    for s in ["top", "right"]:
        ax.spines[s].set_visible(False)
    save(fig, OUT / "line-of-sight.png")


if __name__ == "__main__":
    contours_vs_grid()
    dem_3d()
    dem_dsm()
    resolution()
    units_mistake()
    rise_run()
    window()
    dem_slope()
    dem_hillshade()
    shaded_relief()
    dem_aspect()
    sun_geometry()
    line_of_sight()
    dem_viewshed()
