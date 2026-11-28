"""Figures for Chapter 13, Density and Neighborhoods.

Usage: python density.py <dir with ne_10m_admin_2_counties.geojson>

All point data are made up (fixed random seed).
"""
import sys
from pathlib import Path

import numpy as np
import matplotlib.pyplot as plt
from matplotlib.patches import Circle, Rectangle, FancyArrowPatch

from style import NAVY, PINE, BLUE, BASIN, CORNER, FOG, CLAY, POPLAR, GINKGO, DOGWOOD, save

OUT = Path(__file__).parent.parent.parent / "images" / "density"
OUT.mkdir(parents=True, exist_ok=True)

rng = np.random.default_rng(370)
# 20 made-up points: a cluster in the middle, a few scattered, one outlier
PTS = np.array([
    [4.6, 4.9], [5.3, 5.4], [4.9, 5.9], [5.8, 4.7], [4.2, 5.6], [5.6, 6.2],
    [3.7, 4.4], [6.3, 5.5], [5.0, 4.2], [4.4, 3.6], [2.4, 6.9], [1.0, 2.6],
    [1.9, 1.7], [6.9, 2.6], [7.6, 4.3], [2.0, 5.2], [6.0, 7.6], [3.6, 7.9],
    [8.1, 6.6], [9.3, 9.2],
])


def frame(ax, lim=10):
    ax.add_patch(Rectangle((0, 0), lim, lim, fill=False, ec=CORNER, lw=1.2))
    ax.set_xlim(-0.3, lim + 0.3)
    ax.set_ylim(-0.3, lim + 0.3)
    ax.set_aspect("equal")
    ax.set_axis_off()


def distance_neighbors():
    fig, axes = plt.subplots(1, 2, figsize=(11, 5.2))
    d = 1.4
    for ax, fi, where in [(axes[0], 0, "A point in the cluster"),
                          (axes[1], 11, "A point near the edge")]:
        frame(ax)
        f = PTS[fi]
        ax.add_patch(Circle(f, d, fc=BLUE, alpha=0.12, ec=BLUE, lw=1.5))
        dist = np.hypot(*(PTS - f).T)
        inside = (dist <= d) & (dist > 0)
        ax.scatter(*PTS[~inside].T, s=50, fc="white", ec=BASIN, lw=1.3, zorder=3)
        ax.scatter(*PTS[inside].T, s=50, c=BLUE, ec=NAVY, lw=1, zorder=4)
        ax.scatter(*f, s=110, marker="D", c=CLAY, ec=NAVY, lw=1, zorder=5)
        ax.annotate("", xy=(f[0] + d, f[1]), xytext=f,
                    arrowprops=dict(arrowstyle="<->", color=NAVY, lw=1.2))
        ax.text(f[0] + d / 2, f[1] + 0.12, "d", ha="center", fontsize=12,
                style="italic", color=NAVY)
        n = inside.sum()
        ax.set_title(f"{where}: {n} neighbor{'s' if n != 1 else ''}", fontsize=12, loc="left")
    axes[1].text(0.35, 9.7, "Part of the circle\nfalls outside the\nstudy area", fontsize=9.5,
                 color=BASIN, va="top")
    save(fig, OUT / "distance-neighbors.png")


def contiguity():
    fig, axes = plt.subplots(1, 2, figsize=(9.5, 4.8))
    for ax, case in zip(axes, ["Rook's case", "Queen's case"]):
        for i in range(5):
            for j in range(5):
                di, dj = abs(i - 2), abs(j - 2)
                if di == 0 and dj == 0:
                    c = GINKGO
                elif di + dj == 1 or (case == "Queen's case" and di == 1 and dj == 1):
                    c = DOGWOOD
                else:
                    c = "white"
                ax.add_patch(Rectangle((i, j), 1, 1, fc=c, ec=BASIN, lw=1.2))
        n = 4 if case.startswith("Rook") else 8
        ax.set_title(f"{case}: {n} neighbors", fontsize=12, loc="left")
        ax.set_xlim(-0.1, 5.1)
        ax.set_ylim(-0.1, 5.1)
        ax.set_aspect("equal")
        ax.set_axis_off()
    save(fig, OUT / "contiguity-grid.png")


def contiguity_nc(ne):
    import geopandas as gpd
    co = gpd.read_file(ne / "ne_10m_admin_2_counties.geojson")
    nc = co[co["REGION"] == "NC"].to_crs("EPSG:32119").reset_index(drop=True)
    nc["geometry"] = nc.buffer(0)
    focus = nc[nc["NAME"] == "Orange"].index[0]
    fg = nc.geometry[focus]
    rook, queen = [], []
    for i, g in nc.geometry.items():
        if i == focus:
            continue
        inter = fg.intersection(g.buffer(5))  # tolerate tiny gaps in generalized data
        if inter.is_empty:
            continue
        if fg.boundary.intersection(g.buffer(5)).length > 2000:
            rook.append(i)
        else:
            queen.append(i)
    print("rook:", list(nc.loc[rook, "NAME"]), "corner-only:", list(nc.loc[queen, "NAME"]))
    fig, ax = plt.subplots(figsize=(8, 5.4))
    x0, y0, x1, y1 = nc.geometry[[focus] + rook + queen].total_bounds
    pad = 25e3
    nc.plot(ax=ax, color="white", edgecolor=CORNER, lw=0.8)
    nc.loc[rook].plot(ax=ax, color=DOGWOOD, edgecolor=BASIN, lw=0.8)
    if queen:
        nc.loc[queen].plot(ax=ax, color="#d9ead3", edgecolor=BASIN, lw=0.8, hatch="//")
    nc.loc[[focus]].plot(ax=ax, color=GINKGO, edgecolor=NAVY, lw=1.2)
    for i in [focus] + rook + queen:
        p = nc.geometry[i].representative_point()
        ax.text(p.x, p.y, nc.loc[i, "NAME"], ha="center", va="center", fontsize=9, color=NAVY)
    ax.set_xlim(x0 - pad, x1 + pad)
    ax.set_ylim(y0 - pad, y1 + pad)
    ax.set_axis_off()
    save(fig, OUT / "contiguity-nc.png")


def knn():
    fig, axes = plt.subplots(1, 2, figsize=(11, 5.2))
    for ax, k in zip(axes, (1, 4)):
        frame(ax)
        ax.scatter(*PTS.T, s=50, fc="white", ec=BASIN, lw=1.3, zorder=3)
        for fi, col in [(0, CLAY), (19, PINE)]:
            f = PTS[fi]
            dist = np.hypot(*(PTS - f).T)
            dist[fi] = np.inf
            nn = np.argsort(dist)[:k]
            for j in nn:
                ax.add_patch(FancyArrowPatch(f, PTS[j], arrowstyle="-|>", mutation_scale=12,
                                             color=col, lw=1.4, shrinkA=6, shrinkB=6, zorder=2))
            ax.scatter(*PTS[nn].T, s=50, c=col, ec=NAVY, lw=1, zorder=4, alpha=0.85)
            ax.scatter(*f, s=110, marker="D", c=col, ec=NAVY, lw=1, zorder=5)
        ax.set_title(f"k = {k}", fontsize=13, loc="left")
    save(fig, OUT / "knn.png")


def kernels():
    fig, ax = plt.subplots(figsize=(8, 3.6))
    u = np.linspace(-1.4, 1.4, 600)
    inside = np.abs(u) <= 1
    unif = np.where(inside, 0.5, 0)
    quart = np.where(inside, 15 / 16 * (1 - u ** 2) ** 2, 0)
    gauss = np.exp(-0.5 * (u / 0.4) ** 2) / (0.4 * np.sqrt(2 * np.pi))
    ax.plot(u, unif, color=BLUE, lw=2.2, label="Uniform: every point inside counts the same")
    ax.plot(u, quart, color=CLAY, lw=2.2, label="Quartic (ArcGIS Pro's default)")
    ax.plot(u, gauss, color=PINE, lw=2.2, ls="--", label="Gaussian (normal)")
    ax.axvline(0, color=CORNER, lw=1, zorder=0)
    ax.set_xticks([-1, 0, 1])
    ax.set_xticklabels(["−bandwidth", "the cell", "+bandwidth"])
    ax.set_yticks([])
    ax.set_ylabel("Weight of a point")
    ax.spines[["top", "right", "left"]].set_visible(False)
    ax.legend(frameon=False, fontsize=9.5, loc="upper left", bbox_to_anchor=(0.0, 1.12))
    ax.set_ylim(0, 1.35)
    save(fig, OUT / "kernel-shapes.png")


def incidents():
    a = rng.normal([3.2, 6.0], 0.45, (60, 2))
    b = rng.normal([6.8, 3.4], 0.7, (45, 2))
    c = rng.normal([6.0, 7.2], 0.3, (20, 2))
    d = rng.uniform(0.3, 9.7, (35, 2))
    p = np.vstack([a, b, c, d])
    return p[(p >= 0).all(1) & (p <= 10).all(1)]


def kde(points, h, n=200):
    g = np.linspace(0, 10, n)
    X, Y = np.meshgrid(g, g)
    Z = np.zeros_like(X)
    for px, py in points:
        r2 = ((X - px) ** 2 + (Y - py) ** 2) / h ** 2
        Z += np.where(r2 < 1, 3 / np.pi * (1 - r2) ** 2, 0)  # quartic kernel
    return g, Z / h ** 2


def kernel_window():
    p = incidents()
    fig, ax = plt.subplots(figsize=(5.6, 5.6))
    for v in np.arange(0, 10.01, 0.5):
        ax.plot([v, v], [0, 10], color=FOG, lw=0.8, zorder=0)
        ax.plot([0, 10], [v, v], color=FOG, lw=0.8, zorder=0)
    ax.scatter(*p.T, s=12, c=NAVY, zorder=3)
    cell = (6.75, 3.25)
    ax.add_patch(Rectangle((6.5, 3.0), 0.5, 0.5, fc=CLAY, ec=NAVY, lw=1.2, zorder=4))
    ax.add_patch(Circle(cell, 1.5, fc=CLAY, alpha=0.12, ec=CLAY, lw=1.8, zorder=2))
    ax.annotate("", xy=(cell[0] + 1.5, cell[1]), xytext=cell,
                arrowprops=dict(arrowstyle="<->", color=NAVY, lw=1.2), zorder=5)
    ax.text(cell[0] + 0.75, cell[1] - 0.18, "bandwidth", ha="center", va="top", fontsize=9, color=NAVY,
            zorder=6, bbox=dict(fc="white", ec="none", pad=1, alpha=0.9))
    n_in = (np.hypot(*(p - cell).T) <= 1.5).sum()
    frame(ax)
    ax.set_ylim(-0.9, 10.3)
    ax.text(5, -0.55, f"{n_in} points fall inside the kernel around the red cell",
            ha="center", fontsize=10, color=NAVY)
    save(fig, OUT / "kernel-window.png")


def bandwidths():
    p = incidents()
    fig, axes = plt.subplots(1, 3, figsize=(13, 4.6))
    for ax, h, t in zip(axes, (0.4, 1.2, 3.5), ("Small bandwidth", "Medium bandwidth", "Large bandwidth")):
        g, Z = kde(p, h)
        ax.imshow(Z, origin="lower", extent=(0, 10, 0, 10), cmap="YlOrRd")
        ax.scatter(*p.T, s=4, c=NAVY, alpha=0.6)
        ax.add_patch(Circle((1.0, 9.0), h, fill=False, ec=NAVY, lw=1.2, ls="--"))
        ax.set_title(f"{t} ({h:g} units)", fontsize=12, loc="left")
        ax.set_xlim(0, 10)
        ax.set_ylim(0, 10)
        ax.set_xticks([])
        ax.set_yticks([])
        for s in ax.spines.values():
            s.set_color(CORNER)
    save(fig, OUT / "bandwidths.png")


if __name__ == "__main__":
    distance_neighbors()
    contiguity()
    contiguity_nc(Path(sys.argv[1]))
    knn()
    kernels()
    kernel_window()
    bandwidths()
