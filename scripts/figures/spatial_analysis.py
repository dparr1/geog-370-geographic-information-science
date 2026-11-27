"""Figures for Chapter 13, Spatial Analysis: Overlay and Proximity.

Usage: python spatial_analysis.py <dir with ne_50m_admin_1_states_provinces_lakes.geojson>

Apart from the U.S. state maps, all features are made up.
"""
import sys
from pathlib import Path

import numpy as np
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch, Polygon as MPoly, Rectangle
from shapely.geometry import Point, LineString, Polygon, box
from shapely.ops import unary_union

from style import (NAVY, PINE, BLUE, BASIN, CORNER, FOG, CLAY, POPLAR, GINKGO,
                   SAND, DOGWOOD, BERRY, DUSK, save)

OUT = Path(__file__).parent.parent.parent / "images" / "spatial-analysis"
OUT.mkdir(parents=True, exist_ok=True)


def draw(ax, geom, fc="none", ec=NAVY, lw=1.2, alpha=1.0, z=1, hatch=None):
    if geom.is_empty:
        return
    if geom.geom_type in ("Polygon", "MultiPolygon"):
        polys = [geom] if geom.geom_type == "Polygon" else list(geom.geoms)
        for p in polys:
            ax.add_patch(MPoly(np.array(p.exterior.coords), closed=True, fc=fc, ec=ec,
                               lw=lw, alpha=alpha, zorder=z, hatch=hatch))
            for h in p.interiors:
                ax.add_patch(MPoly(np.array(h.coords), closed=True, fc="white", ec=ec,
                                   lw=lw, zorder=z + 0.1))
    elif geom.geom_type in ("LineString", "MultiLineString"):
        lines = [geom] if geom.geom_type == "LineString" else list(geom.geoms)
        for l in lines:
            ax.plot(*l.xy, color=ec, lw=lw, zorder=z, solid_capstyle="round")
    elif geom.geom_type == "Point":
        ax.scatter([geom.x], [geom.y], s=40, c=fc if fc != "none" else ec, ec=NAVY, zorder=z)


def clean(ax, lim=None):
    ax.set_aspect("equal")
    ax.set_axis_off()
    if lim:
        ax.set_xlim(lim[0], lim[1])
        ax.set_ylim(lim[2], lim[3])


def box_text(ax, x, y, w, h, text, fc, ec=NAVY, fs=10, color=NAVY, weight="normal"):
    ax.add_patch(FancyBboxPatch((x - w / 2, y - h / 2), w, h, boxstyle="round,pad=0.02,rounding_size=0.08",
                                fc=fc, ec=ec, lw=1.2))
    ax.text(x, y, text, ha="center", va="center", fontsize=fs, color=color, weight=weight)


def arrow(ax, x0, y0, x1, y1):
    ax.annotate("", xy=(x1, y1), xytext=(x0, y0),
                arrowprops=dict(arrowstyle="-|>", color=NAVY, lw=1.3, mutation_scale=14))


# ---------- 1. the Batcave cartographic model ----------
def batcave_model():
    fig, ax = plt.subplots(figsize=(12, 4.4))
    ax.set_xlim(0, 12)
    ax.set_ylim(0, 4.4)
    ax.set_axis_off()
    D, O, R = SAND, "#dbe9f6", DOGWOOD  # data, operation, result
    box_text(ax, 1.1, 3.5, 1.8, 0.6, "Soils layer", D)
    box_text(ax, 1.1, 1.9, 1.8, 0.6, "Crime table", D)
    box_text(ax, 1.1, 0.9, 1.8, 0.6, "ZIP Code layer", D)
    box_text(ax, 3.6, 3.5, 2.2, 0.75, "1. Select by attribute\nSOIL = 'Limestone'", O, fs=9.5)
    box_text(ax, 3.6, 1.4, 2.2, 0.75, "2. Table join\non ZIP Code", O, fs=9.5)
    box_text(ax, 6.2, 3.5, 1.9, 0.6, "Limestone areas", D)
    box_text(ax, 6.2, 1.4, 1.9, 0.6, "ZIP Codes\nwith crimes", D, fs=9.5)
    box_text(ax, 6.2, 0.35, 2.2, 0.55, "3. Select highest\ncrime ZIP Code", O, fs=9)
    box_text(ax, 8.6, 0.35, 1.8, 0.55, "Highest-crime\nZIP Code", D, fs=9)
    box_text(ax, 8.6, 2.45, 2.2, 0.75, "4. Spatial join\n(closest)", O, fs=9.5)
    box_text(ax, 11.0, 2.45, 1.7, 0.75, "Batcave\nsite", R, weight="bold")
    arrow(ax, 2.0, 3.5, 2.5, 3.5)
    arrow(ax, 2.0, 1.9, 2.5, 1.55)
    arrow(ax, 2.0, 0.9, 2.5, 1.25)
    arrow(ax, 4.7, 3.5, 5.25, 3.5)
    arrow(ax, 4.7, 1.4, 5.25, 1.4)
    arrow(ax, 6.2, 1.1, 6.2, 0.63)
    arrow(ax, 7.3, 0.35, 7.7, 0.35)
    arrow(ax, 7.15, 3.4, 7.5, 2.7)
    arrow(ax, 8.6, 0.63, 8.6, 2.07)
    arrow(ax, 9.7, 2.45, 10.15, 2.45)
    handles = [Rectangle((0, 0), 1, 1, fc=c, ec=NAVY) for c in (D, O, R)]
    ax.legend(handles, ["Data layer", "Operation", "Result"], loc="upper right",
              frameon=False, fontsize=9.5, ncol=3, bbox_to_anchor=(1.0, 1.02))
    save(fig, OUT / "batcave-model.png")


def batcave_map():
    """Made-up city: soils, ZIP Codes with crime counts, and the result."""
    rng = np.random.default_rng(14)
    zips = {}
    names = ["78701", "78702", "78703", "78704", "78705", "78741"]
    crimes = [2310, 3120, 1480, 2760, 1990, 4870]
    cells = [box(0, 5, 4, 10), box(4, 5, 8, 10), box(8, 5, 12, 10),
             box(0, 0, 4, 5), box(4, 0, 8, 5), box(8, 0, 12, 5)]
    for n, c, g in zip(names, crimes, cells):
        zips[n] = (g, c)
    lime = [Polygon([(0.6, 6.2), (2.8, 6.8), (3.2, 8.8), (1.0, 9.2)]),
            Polygon([(4.6, 1.0), (6.6, 0.6), (7.2, 2.6), (5.0, 3.0)]),
            Polygon([(9.0, 7.6), (11.2, 7.2), (11.4, 9.4), (9.4, 9.5)])]
    clay = [Polygon([(4.6, 6.0), (7.5, 5.6), (7.4, 9.0), (4.4, 8.6)]),
            Polygon([(8.6, 1.0), (11.4, 0.8), (11.2, 3.6), (8.8, 4.0)]),
            Polygon([(0.5, 0.8), (3.4, 1.2), (3.0, 4.2), (0.8, 3.8)])]
    fig, axes = plt.subplots(1, 3, figsize=(13, 4.3))
    # panel 1 soils
    ax = axes[0]
    for g in lime:
        draw(ax, g, fc="#e8dfc8", ec=BASIN, lw=0.8)
    for g in clay:
        draw(ax, g, fc="#c9a27a", ec=BASIN, lw=0.8)
    draw(ax, box(0, 0, 12, 10), ec=CORNER, lw=1)
    ax.set_title("Soils", fontsize=12, loc="left")
    ax.legend([Rectangle((0, 0), 1, 1, fc="#e8dfc8", ec=BASIN), Rectangle((0, 0), 1, 1, fc="#c9a27a", ec=BASIN)],
              ["Limestone", "Clay"], loc="upper center", bbox_to_anchor=(0.5, -0.0), ncol=2,
              frameon=False, fontsize=9.5)
    # panel 2 crimes by zip
    ax = axes[1]
    cmax = max(crimes)
    for n, (g, c) in zips.items():
        shade = plt.get_cmap("Reds")(0.15 + 0.75 * c / cmax)
        draw(ax, g, fc=shade, ec="white", lw=1.5)
        x, y = g.centroid.x, g.centroid.y
        tc = "white" if c > 4000 else NAVY
        ax.text(x, y + 0.4, n, ha="center", fontsize=9.5, color=tc, weight="bold")
        ax.text(x, y - 0.5, f"{c:,} crimes", ha="center", fontsize=9, color=tc)
    ax.set_title("Crimes by ZIP Code (table join)", fontsize=12, loc="left")
    # panel 3 result
    ax = axes[2]
    for n, (g, c) in zips.items():
        draw(ax, g, fc=CLAY if n == "78741" else "white", ec=CORNER, lw=1, alpha=0.35 if n == "78741" else 1)
    target = zips["78741"][0]
    dists = [target.distance(g) for g in lime]
    best = int(np.argmin(dists))
    for i, g in enumerate(lime):
        draw(ax, g, fc=PINE if i == best else "#e8dfc8", ec=NAVY if i == best else BASIN,
             lw=1.6 if i == best else 0.8, z=3)
    bx, by = lime[best].centroid.x, lime[best].centroid.y
    ax.text(bx - 0.6, by + 1.6, "Batcave site:\nclosest limestone", ha="center", fontsize=9.5,
            color=PINE, weight="bold")
    ax.text(10.0, 1.2, "Highest\ncrime:\n78741", ha="center", fontsize=9, color=CLAY,
            weight="bold")
    ax.set_title("Result (spatial join, closest)", fontsize=12, loc="left")
    for ax in axes:
        clean(ax, (-0.2, 12.2, -0.2, 10.2))
    save(fig, OUT / "batcave-map.png")


# ---------- 2. spatial scope ----------
def scope(ne):
    import geopandas as gpd
    s = gpd.read_file(ne / "ne_50m_admin_1_states_provinces_lakes.geojson")
    us = s[(s.adm0_a3 == "USA") & (~s.postal.isin(["AK", "HI"]))].to_crs("EPSG:5070")
    west = us[us.region == "West"]
    ut = us[us.postal == "UT"].geometry.iloc[0]
    nb = [p for p, g in zip(us.postal, us.geometry) if p != "UT" and g.buffer(2000).intersects(ut)]
    print("Utah neighbors:", nb)
    fig, axes = plt.subplots(1, 3, figsize=(13, 4.6))
    titles = ["Local: Utah's own value only", f"Neighborhood: Utah and its {len(nb)} neighbors",
              "Global: every state"]
    for k, ax in enumerate(axes):
        for p, g in zip(west.postal, west.geometry):
            if k == 2:
                fc = BLUE
            elif p == "UT":
                fc = POPLAR
            elif k == 1 and p in nb:
                fc = "#bcd8ee"
            else:
                fc = "white"
            draw(ax, g, fc=POPLAR if p == "UT" else fc, ec=BASIN, lw=0.7)
            if p in ["UT"] + (nb if k == 1 else []):
                c = g.representative_point()
                ax.text(c.x, c.y, p, ha="center", va="center", fontsize=8.5, color=NAVY)
        x0, y0, x1, y1 = west.total_bounds
        clean(ax, (x0 - 5e4, x1 + 5e4, y0 - 5e4, y1 + 5e4))
        ax.set_title(titles[k], fontsize=11.5, loc="left")
    save(fig, OUT / "spatial-scope.png")


def dissolve(ne):
    import geopandas as gpd
    s = gpd.read_file(ne / "ne_50m_admin_1_states_provinces_lakes.geojson")
    us = s[(s.adm0_a3 == "USA") & (~s.postal.isin(["AK", "HI"]))].to_crs("EPSG:5070")
    cols = {"West": POPLAR, "Midwest": BLUE, "South": DOGWOOD, "Northeast": BERRY}
    fig, axes = plt.subplots(1, 2, figsize=(13, 4.4))
    for r, c in cols.items():
        us[us.region == r].plot(ax=axes[0], color=c, edgecolor="white", lw=0.6)
    d = us.dissolve(by="region")
    for r, c in cols.items():
        d.loc[[r]].plot(ax=axes[1], color=c, edgecolor="white", lw=1.2)
        p = d.loc[r].geometry.representative_point()
        axes[1].text(p.x, p.y, r, ha="center", va="center", fontsize=11, color=NAVY, weight="bold")
    axes[0].set_title(f"Before: {len(us)} states and DC, each with a Region field", fontsize=11.5, loc="left")
    axes[1].set_title(f"After dissolving on Region: {len(d)} polygons", fontsize=11.5, loc="left")
    for ax in axes:
        ax.set_axis_off()
    save(fig, OUT / "dissolve.png")


# ---------- 3. buffers ----------
PTS = [Point(2, 2.2), Point(3.1, 3.0), Point(6.5, 5.6), Point(4.6, 6.8)]


def buffers():
    fig, axes = plt.subplots(1, 3, figsize=(12.5, 4.4))
    b = unary_union([p.buffer(3.0) for p in PTS]).bounds
    lim = (b[0] - 0.2, b[2] + 0.2, b[1] - 0.2, b[3] + 0.2)
    ax = axes[0]
    for p in PTS:
        draw(ax, p.buffer(1.5), fc=BLUE, ec=NAVY, lw=1, alpha=0.35)
    ax.set_title("Fixed buffers (overlaps kept)", fontsize=11.5, loc="left")
    ax = axes[1]
    draw(ax, unary_union([p.buffer(1.5) for p in PTS]), fc=BLUE, ec=NAVY, lw=1, alpha=0.35)
    ax.set_title("Dissolved buffers", fontsize=11.5, loc="left")
    ax = axes[2]
    rings = [(3.0, "#dbe9f6"), (2.0, "#9ecae1"), (1.0, "#4292c6")]
    for r, c in rings:
        draw(ax, unary_union([p.buffer(r) for p in PTS]), fc=c, ec=NAVY, lw=0.8)
    ax.set_title("Nested (multiple-ring) buffers", fontsize=11.5, loc="left")
    for ax in axes:
        for p in PTS:
            draw(ax, p, fc=CLAY, z=5)
        clean(ax, lim)
    save(fig, OUT / "buffer-types.png")


def line_buffers():
    fig, axes = plt.subplots(1, 2, figsize=(12, 4.6))
    ax = axes[0]
    t = np.linspace(0, 1, 200)
    north = LineString(np.c_[1.5 + 6 * t, 4.6 + 3.0 * np.sin(np.pi * t)])
    south = LineString(np.c_[1.5 + 6 * t, 4.6 - 2.6 * np.sin(np.pi * t)])
    ends = [LineString([(0.3, 4.6), (1.5, 4.6)]), LineString([(7.5, 4.6), (8.7, 4.6)])]
    lines = unary_union([north, south] + ends)
    buf = lines.buffer(0.75)
    draw(ax, buf, fc=BLUE, ec=NAVY, lw=1, alpha=0.3)
    draw(ax, lines, ec=BLUE, lw=2.5, z=3)
    holes = [Polygon(h) for g in ([buf] if buf.geom_type == "Polygon" else buf.geoms) for h in g.interiors]
    for h in holes:
        draw(ax, h, fc=GINKGO, ec=NAVY, lw=0.8, z=2)
        c = h.representative_point()
    if holes:
        big = max(holes, key=lambda h: h.area)
        c = big.representative_point()
        ax.text(c.x, c.y, "Enclosed area:\nnot in the buffer", ha="center", va="center", fontsize=9,
                color=NAVY)
    ax.set_title("Line buffers can enclose areas", fontsize=11.5, loc="left")
    clean(ax, (0, 9, 0, 9.4))
    ax = axes[1]
    rivers = [("Big River", LineString([(1, 8.8), (2.2, 6.5), (3.6, 4.5), (4.2, 2.0), (5.5, 0.2)]), 1.0),
              ("Middle Creek", LineString([(8.6, 7.8), (6.6, 6.0), (5.0, 5.2), (3.6, 4.5)]), 0.6),
              ("Small Branch", LineString([(7.8, 1.6), (6.0, 2.4), (4.2, 2.0)]), 0.3)]
    for name, l, d in rivers:
        draw(ax, l.buffer(d), fc=BLUE, ec="none", alpha=0.3)
    for name, l, d in rivers:
        draw(ax, l, ec=BLUE, lw=1 + 2 * d, z=3)
    ax.text(3.3, 7.6, "Big River\nbuffdist = 100 m", fontsize=9, color=NAVY)
    ax.text(6.8, 7.0, "Middle Creek\nbuffdist = 60 m", fontsize=9, color=NAVY)
    ax.text(6.2, 0.6, "Small Branch\nbuffdist = 30 m", fontsize=9, color=NAVY)
    ax.set_title("Variable-distance buffers (from a field)", fontsize=11.5, loc="left")
    clean(ax, (0, 9.4, 0, 9.4))
    save(fig, OUT / "line-buffers.png")


# ---------- 4. overlay ----------
A1 = Polygon([(0, 0), (6, 0), (6, 3), (0, 3)])
A2 = Polygon([(0, 3), (6, 3), (6, 6), (0, 6)])
B1 = Polygon([(0, 0), (2.6, 0), (3.4, 6), (0, 6)])
B2 = Polygon([(2.6, 0), (6, 0), (6, 6), (3.4, 6)])


def overlay():
    fig, axes = plt.subplots(1, 3, figsize=(13, 4.6))
    ax = axes[0]
    draw(ax, A1, fc=SAND, ec=NAVY)
    draw(ax, A2, fc=GINKGO, ec=NAVY)
    ax.text(3, 1.5, "Class = A", ha="center", fontsize=10.5)
    ax.text(3, 4.5, "Class = B", ha="center", fontsize=10.5)
    ax.set_title("Layer 1 (Class)", fontsize=11.5, loc="left")
    ax = axes[1]
    draw(ax, B1, fc="#dbe9f6", ec=PINE, lw=1.6)
    draw(ax, B2, fc="#b9d7c9", ec=PINE, lw=1.6)
    ax.text(1.4, 3, "Cost = 10", ha="center", fontsize=10.5)
    ax.text(4.6, 3, "Cost = 25", ha="center", fontsize=10.5)
    ax.set_title("Layer 2 (Cost)", fontsize=11.5, loc="left")
    ax = axes[2]
    pieces = [(A1.intersection(B1), "1", "A", 10), (A1.intersection(B2), "2", "A", 25),
              (A2.intersection(B1), "3", "B", 10), (A2.intersection(B2), "4", "B", 25)]
    shades = [SAND, "#f2d9a8", GINKGO, "#e6c23a"]
    for (g, n, c, k), sh in zip(pieces, shades):
        draw(ax, g, fc=sh, ec=NAVY)
        p = g.representative_point()
        ax.text(p.x, p.y + 0.35, n, ha="center", fontsize=12, weight="bold", color=NAVY)
        ax.text(p.x, p.y - 0.4, f"{c}, {k}", ha="center", fontsize=9.5, color=NAVY)
    ax.set_title("Output: 4 polygons (Class, Cost)", fontsize=11.5, loc="left")
    for ax in axes:
        clean(ax, (-0.3, 6.3, -0.3, 6.3))
    save(fig, OUT / "polygon-overlay.png")


def clip_intersect_union():
    data = Polygon([(0, 0.5), (4.2, 0.5), (4.2, 4.5), (0, 4.5)])
    bound = Point(4.0, 2.5).buffer(2.0, resolution=48)
    fig, axes = plt.subplots(1, 4, figsize=(13.5, 3.8))
    ax = axes[0]
    draw(ax, data, fc="#dbe9f6", ec=BLUE, lw=1.5)
    draw(ax, bound, fc=SAND, ec=POPLAR, lw=1.5, alpha=0.7)
    ax.text(1.2, 2.5, "Data\nlayer", ha="center", fontsize=10)
    ax.text(5.3, 2.5, "Bounding\nlayer", ha="center", fontsize=10)
    ax.set_title("Inputs", fontsize=11.5, loc="left")
    ax = axes[1]
    draw(ax, data, fc="none", ec=CORNER, lw=1, z=0)
    draw(ax, bound, fc="none", ec=CORNER, lw=1, z=0)
    draw(ax, data.intersection(bound), fc="#dbe9f6", ec=BLUE, lw=1.5)
    ax.set_title("Clip: data layer's attributes", fontsize=11, loc="left")
    ax = axes[2]
    draw(ax, data, fc="none", ec=CORNER, lw=1, z=0)
    draw(ax, bound, fc="none", ec=CORNER, lw=1, z=0)
    draw(ax, data.intersection(bound), fc=DOGWOOD, ec=PINE, lw=1.5)
    ax.set_title("Intersect: both layers' attributes", fontsize=11, loc="left")
    ax = axes[3]
    draw(ax, data.difference(bound), fc="#dbe9f6", ec=NAVY, lw=1.2)
    draw(ax, bound.difference(data), fc=SAND, ec=NAVY, lw=1.2)
    draw(ax, data.intersection(bound), fc=DOGWOOD, ec=NAVY, lw=1.2)
    ax.set_title("Union: all areas, split", fontsize=11, loc="left")
    for ax in axes:
        clean(ax, (-0.3, 6.3, -0.2, 5.0))
    save(fig, OUT / "clip-intersect-union.png")


def slivers():
    fig, axes = plt.subplots(1, 2, figsize=(11, 4.2))
    t = np.linspace(0, 1, 40)
    base = np.c_[3 + 0.6 * np.sin(6 * t), 6 * t]
    rng = np.random.default_rng(3)
    wob = base + np.c_[rng.normal(0, 0.12, 40), np.zeros(40)]
    wob[0], wob[-1] = base[0], base[-1]
    left1 = Polygon(np.vstack([[(0, 0)], base, [(0, 6)]]))
    left2 = Polygon(np.vstack([[(0, 0)], wob, [(0, 6)]]))
    ax = axes[0]
    ax.plot(*base.T, color=BLUE, lw=1.6, label="Boundary in layer 1")
    ax.plot(*wob.T, color=CLAY, lw=1.6, label="Same boundary in layer 2")
    ax.legend(frameon=False, fontsize=9.5, loc="upper center", bbox_to_anchor=(0.5, 0.02), ncol=2)
    ax.set_title("One boundary, digitized twice", fontsize=11.5, loc="left")
    clean(ax, (1.4, 4.8, -0.2, 6.2))
    ax = axes[1]
    sl = left1.symmetric_difference(left2)
    draw(ax, sl, fc=CLAY, ec=NAVY, lw=0.6)
    ax.plot(*base.T, color=CORNER, lw=0.6, zorder=0)
    n = len(sl.geoms) if sl.geom_type == "MultiPolygon" else 1
    ax.set_title(f"After overlay: {n} sliver polygons", fontsize=11.5, loc="left")
    clean(ax, (1.4, 4.8, -0.2, 6.2))
    save(fig, OUT / "slivers.png")


def point_in_polygon():
    county = Polygon([(0.5, 0.5), (7.5, 0.8), (7.2, 6.4), (0.8, 6.0)])
    pts = [("A", Point(2.0, 4.6), "Theft"), ("B", Point(5.6, 4.0), "Burglary"),
           ("C", Point(3.8, 1.8), "Theft")]
    fig, ax = plt.subplots(figsize=(5.2, 3.9))
    draw(ax, county, fc="#eef4e8", ec=PINE, lw=1.6)
    ax.text(4.0, 5.6, "Greene County (Rural)", ha="center", fontsize=10.5, color=PINE, weight="bold")
    for n, p, c in pts:
        draw(ax, p, fc=CLAY, z=4)
        ax.text(p.x + 0.25, p.y, f"{n}: {c}", va="center", fontsize=10, color=NAVY)
    clean(ax, (0, 8, 0, 6.8))
    save(fig, OUT / "point-in-polygon.png")


# ---------- 5. map algebra ----------
def grid(ax, vals, x0, y0, title, cmap="Blues", vmin=None, vmax=None, hi=None, fmt="{:g}"):
    n = vals.shape[0]
    cm = plt.get_cmap(cmap)
    vmin = vals.min() if vmin is None else vmin
    vmax = vals.max() if vmax is None else vmax
    for i in range(n):
        for j in range(n):
            v = vals[i, j]
            f = 0.12 + 0.6 * (v - vmin) / (vmax - vmin + 1e-9)
            ax.add_patch(Rectangle((x0 + j, y0 + n - 1 - i), 1, 1, fc=cm(f), ec="white", lw=1.5))
            ax.text(x0 + j + 0.5, y0 + n - 1 - i + 0.5, fmt.format(v), ha="center", va="center",
                    fontsize=9.5, color=NAVY)
    if hi:
        (r0, c0, r1, c1), col = hi
        ax.add_patch(Rectangle((x0 + c0, y0 + n - 1 - r1), c1 - c0 + 1, r1 - r0 + 1, fill=False,
                               ec=col, lw=2.4, zorder=5))
    ax.text(x0 + n / 2, y0 + n + 0.35, title, ha="center", fontsize=10.5, color=NAVY, weight="bold")


def map_algebra():
    a = np.array([[1, 2, 2, 4], [2, 3, 4, 5], [3, 4, 6, 7], [4, 5, 7, 9]])
    b = np.array([[0, 1, 1, 1], [0, 0, 1, 1], [1, 0, 0, 1], [1, 1, 0, 0]])
    fig, axes = plt.subplots(1, 4, figsize=(14, 3.6))
    # local
    ax = axes[0]
    grid(ax, a, 0, 0, "A")
    ax.text(4.5, 2, "+", fontsize=18, ha="center", va="center")
    grid(ax, b, 5, 0, "B", cmap="Greens")
    ax.set_title("Local: A + B, cell by cell", fontsize=11.5, loc="left", pad=22)
    ax.set_xlim(-0.2, 9.2)
    # result for local in a separate small text
    ax = axes[1]
    grid(ax, a + b, 0, 0, "A + B", cmap="Purples")
    ax.set_title(" ", fontsize=11.5, pad=22)
    ax.set_xlim(-2.5, 6.5)
    # focal
    ax = axes[2]
    grid(ax, a, 0, 0, "A", hi=((1, 1, 3, 3), CLAY))
    m = a[1:4, 1:4].mean()
    ax.text(5.0, 2.0, f"Mean of the\n3×3 window\n= {m:.1f}", fontsize=9.5, color=CLAY, va="center")
    ax.set_title("Focal: a moving window", fontsize=11.5, loc="left", pad=22)
    ax.set_xlim(-0.2, 8)
    # zonal
    ax = axes[3]
    zones = np.array([[1, 1, 2, 2], [1, 1, 2, 2], [1, 3, 3, 2], [3, 3, 3, 3]])
    zc = {1: SAND, 2: DOGWOOD, 3: "#dbe9f6"}
    for i in range(4):
        for j in range(4):
            ax.add_patch(Rectangle((j, 3 - i), 1, 1, fc=zc[zones[i, j]], ec="white", lw=1.5))
            ax.text(j + 0.5, 3 - i + 0.5, str(a[i, j]), ha="center", va="center", fontsize=9.5)
    ax.text(2, 4.35, "A, in three zones", ha="center", fontsize=10.5, weight="bold", color=NAVY)
    for k, z in enumerate((1, 2, 3)):
        ax.text(4.4, 3.2 - k * 1.1, f"Zone {z} mean = {a[zones == z].mean():.1f}", fontsize=9.5,
                color=NAVY, bbox=dict(fc=zc[z], ec="none", pad=2))
    ax.set_title("Zonal: summarize by zone", fontsize=11.5, loc="left", pad=22)
    ax.set_xlim(-0.2, 8.4)
    for ax in axes:
        ax.set_ylim(-0.2, 4.8)
        ax.set_aspect("equal")
        ax.set_axis_off()
    save(fig, OUT / "map-algebra.png")


if __name__ == "__main__":
    ne = Path(sys.argv[1])
    batcave_model()
    batcave_map()
    scope(ne)
    dissolve(ne)
    buffers()
    line_buffers()
    overlay()
    clip_intersect_union()
    slivers()
    point_in_polygon()
    map_algebra()
