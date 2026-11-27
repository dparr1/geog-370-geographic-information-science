"""Diagrams for the Attribute Queries chapter (images/attribute-queries/).

Run from the repository root:  python3 scripts/figures/attribute_queries.py
The seven parcels follow the example table in the GEOG 370 lecture; the
townships map is made up.
"""
import sys, os
import numpy as np
sys.path.insert(0, os.path.dirname(__file__))
from style import *  # noqa
import matplotlib.pyplot as plt
from matplotlib.patches import Circle, Rectangle, Polygon as MPoly, FancyBboxPatch

OUT = "images/attribute-queries"
COLS = ["ID", "Area", "Landuse", "Municip", "Density", "MillRate"]
ROWS = [
    (1, 10.5, "Urban", "City", 1112.2, "A"),
    (2, 330.3, "Farm", "County", 1.9, "C"),
    (3, 2.4, "Suburban", "Township", 237.5, "C"),
    (4, 96.0, "Suburban", "County", 98.1, "A"),
    (5, 22.1, "Urban", "City", 916.2, "B"),
    (6, 30.2, "Farm", "Township", 3.7, "A"),
    (7, 4.4, "Urban", "County", 153.8, "D"),
]
SHAPES = {
    1: [(0, 3), (2, 3), (2, 6), (0, 6)],
    5: [(2, 3), (4, 3), (4, 6), (2, 6)],
    7: [(4, 3), (6, 3), (6, 4.5), (4, 4.5)],
    3: [(4, 4.5), (6, 4.5), (6, 6), (4, 6)],
    6: [(0, 0), (3, 0), (3, 3), (0, 3)],
    4: [(3, 0), (6, 0), (6, 3), (3, 3)],
    2: [(6, 0), (10, 0), (10, 6), (6, 6)],
}


def table(ax, x0, y0, sel=(), cols=COLS, colhi=None, w=None, rowh=0.62, fs=10.5, nulls=None):
    w = w or [0.55, 0.9, 1.3, 1.3, 1.1, 1.05][:len(cols)]
    x = x0
    for j, c in enumerate(cols):
        ax.add_patch(Rectangle((x, y0), w[j], rowh, fc=PINE, ec=NAVY, lw=0.8))
        ax.text(x + w[j] / 2, y0 + rowh / 2, c, ha="center", va="center", color="white", fontweight="bold", fontsize=fs)
        x += w[j]
    for i, r in enumerate(ROWS):
        y = y0 - (i + 1) * rowh
        x = x0
        for j, c in enumerate(cols):
            v = r[COLS.index(c)]
            if nulls and (r[0], c) in nulls:
                v = "NULL"
            fc = GINKGO if r[0] in sel else "white"
            if colhi is not None and c == colhi and r[0] not in sel:
                fc = DOGWOOD
            ax.add_patch(Rectangle((x, y), w[j], rowh, fc=fc, ec=NAVY, lw=0.6))
            txt = f"{v:g}" if isinstance(v, float) else str(v)
            ax.text(x + w[j] / 2, y + rowh / 2, txt, ha="center", va="center", fontsize=fs,
                    color=BASIN if txt == "NULL" else NAVY, style="italic" if txt == "NULL" else "normal")
            x += w[j]
    return sum(w)


def parcel_map(ax, x0, y0, sel=(), s=0.5):
    for pid, pts in SHAPES.items():
        P = [(x0 + px * s, y0 + py * s) for px, py in pts]
        ax.add_patch(MPoly(P, closed=True, fc=GINKGO if pid in sel else FOG, ec=NAVY, lw=1.0))
        cx = np.mean([p[0] for p in P]); cy = np.mean([p[1] for p in P])
        ax.text(cx, cy, str(pid), ha="center", va="center", fontsize=12, fontweight="bold")


def panel(ax, sel, title, expr):
    ax.axis("off"); ax.set_aspect("equal")
    ax.text(0, 5.75, title, fontsize=13, fontweight="bold")
    ax.text(0, 5.2, expr, fontsize=11, family="DejaVu Sans Mono", color=PINE)
    parcel_map(ax, 0, 0.6, sel, s=0.42)
    table(ax, 4.6, 4.3, sel)
    ax.text(0, 0.0, f"Selected: {len(sel)} of 7 (records {', '.join(map(str, sorted(sel))) or 'none'})",
            fontsize=10.5, color=BASIN)
    ax.set_xlim(-0.1, 11.0); ax.set_ylim(-0.3, 6.1)


def selected(f):
    return {r[0] for r in ROWS if f(dict(zip(COLS, r)))}


def two(name, a, b):
    fig, axs = plt.subplots(2, 1, figsize=(9.5, 10.2))
    for ax, (t, e, f) in zip(axs, (a, b)):
        panel(ax, selected(f), t, e)
    fig.subplots_adjust(hspace=0.08)
    save(fig, f"{OUT}/{name}.png")


def parcels():
    two("simple-and-query",
        ("A simple query", '"Area" > 20', lambda r: r["Area"] > 20),
        ("A compound query with AND", '"Landuse" = \'Urban\' AND "Municip" = \'City\'',
         lambda r: r["Landuse"] == "Urban" and r["Municip"] == "City"))
    two("or-not-query",
        ("OR: either condition is enough", '"Area" > 20 OR "Municip" = \'City\'',
         lambda r: r["Area"] > 20 or r["Municip"] == "City"),
        ("NOT: the complement", 'NOT ("Landuse" = \'Urban\')', lambda r: r["Landuse"] != "Urban"))
    two("not-placement",
        ("NOT the whole bracket", 'NOT ("Landuse" = \'Urban\' AND "Municip" = \'County\')',
         lambda r: not (r["Landuse"] == "Urban" and r["Municip"] == "County")),
        ("NOT each condition, joined by AND", 'NOT "Landuse" = \'Urban\' AND NOT "Municip" = \'County\'',
         lambda r: r["Landuse"] != "Urban" and r["Municip"] != "County"))
    fig, ax = plt.subplots(figsize=(9.5, 6.0))
    panel(ax, selected(lambda r: (r["Landuse"] == "Urban" and r["MillRate"] == "B") or
                       (r["Municip"] != "City" and r["Density"] > 200)),
          "A complex query with brackets",
          '("Landuse" = \'Urban\' AND "MillRate" = \'B\')\n  OR (NOT "Municip" = \'City\' AND "Density" > 200)')
    ax.texts[0].set_position((0, 6.6))
    ax.texts[1].set_position((0, 5.5))
    ax.set_ylim(-0.3, 7.0)
    save(fig, f"{OUT}/complex-query.png")


def record_attribute():
    fig, ax = plt.subplots(figsize=(11.5, 6.1))
    ax.axis("off"); ax.set_aspect("equal")
    parcel_map(ax, 0, 0.9, sel={5}, s=0.42)
    w = table(ax, 5.0, 4.3, sel={5}, colhi="Landuse")
    ax.annotate("a record (row):\neverything about parcel 5", (5.0, 4.3 - 5 * 0.62 + 0.31), (1.0, -0.6), fontsize=11,
                arrowprops=dict(arrowstyle="->", color=NAVY, connectionstyle="arc3,rad=-0.2"))
    ax.annotate("an attribute (column):\nLanduse, for every parcel", (5.0 + 0.55 + 0.9 + 0.65, 4.92), (6.4, 5.9), fontsize=11,
                ha="center", arrowprops=dict(arrowstyle="->", color=PINE), color=PINE)
    ax.annotate("", (2.0, 2.3), (5.0, 4.3 - 5 * 0.62 + 0.31), arrowprops=dict(arrowstyle="<->", color=CLAY, lw=1.5,
                connectionstyle="arc3,rad=0.25"))
    ax.text(0, 4.3, "Parcels (not to scale)", fontsize=11, fontweight="bold")
    ax.set_xlim(-0.1, 12.4); ax.set_ylim(-1.0, 6.6)
    save(fig, f"{OUT}/record-attribute.png")


def binary():
    fig, ax = plt.subplots(figsize=(8.5, 3.6))
    ax.axis("off"); ax.set_aspect("equal")
    vals = [8, 4, 2, 1]; bits = [1, 1, 0, 1]
    for i, (v, b) in enumerate(zip(vals, bits)):
        x = i * 1.6
        ax.text(x + 0.7, 3.0, f"{v}s", ha="center", fontsize=12, color=BASIN)
        ax.add_patch(FancyBboxPatch((x + 0.15, 1.5), 1.1, 1.1, boxstyle="round,pad=0.02,rounding_size=0.12",
                                    fc=PINE if b else FOG, ec=NAVY))
        ax.text(x + 0.7, 2.05, str(b), ha="center", va="center", fontsize=24, fontweight="bold",
                color="white" if b else NAVY)
        ax.text(x + 0.7, 0.9, f"{b} × {v} = {b * v}", ha="center", fontsize=11)
    ax.text(6.6, 2.05, "=  8 + 4 + 0 + 1  =  13", va="center", fontsize=15, fontweight="bold")
    ax.text(0.15, 0.1, "Each column is worth twice the one to its right.", fontsize=11, color=BASIN)
    ax.set_xlim(0, 11.2); ax.set_ylim(-0.2, 3.5)
    save(fig, f"{OUT}/binary.png")


def venn_ax(ax, which, title, sub=None, pair_only=False):
    ax.set_aspect("equal"); ax.axis("off")
    ax.add_patch(Rectangle((0, 0), 10, 6.4, fc="white", ec=NAVY, lw=1.2))
    ax.text(0.3, 5.8, "T", fontsize=13, fontweight="bold")
    cen = {"A": (3.6, 3.4), "B": (5.6, 3.4), "C": (8.6, 1.3)}
    rad = {"A": 1.6, "B": 1.6, "C": 0.75}
    op, a, b = which
    if pair_only:
        apart = {a, b} == {"B", "C"}
        cen = {a: (3.2, 3.2), b: (6.8, 3.2) if apart else (5.6, 3.2)}
        rad = {a: 1.6, b: 1.6}
    from matplotlib.path import Path
    from shapely.geometry import Point
    geo = {k: Point(*cen[k]).buffer(rad[k], resolution=64) for k in cen}
    g = geo[a].intersection(geo[b]) if op == "AND" else geo[a].union(geo[b])
    if not g.is_empty:
        for poly in getattr(g, "geoms", [g]):
            ax.add_patch(MPoly(np.array(poly.exterior.coords), closed=True, fc=POPLAR, ec="none", alpha=0.85))
    for k in cen:
        ax.add_patch(Circle(cen[k], rad[k], fc="none", ec=NAVY, lw=1.3))
        ax.text(*cen[k], k, ha="center", va="center", fontsize=14, fontweight="bold")
    ax.set_title(title, fontsize=13)
    if sub:
        ax.text(5, -0.6, sub, ha="center", va="top", fontsize=10, color=BASIN)
    ax.set_xlim(-0.2, 10.2); ax.set_ylim(-1.6, 6.6)


def venns():
    fig, axs = plt.subplots(1, 2, figsize=(10, 3.8))
    venn_ax(axs[0], ("AND", "A", "B"), "A AND B: the intersection")
    venn_ax(axs[1], ("OR", "A", "B"), "A OR B: the union")
    save(fig, f"{OUT}/venn-and-or.png")
    fig, axs = plt.subplots(2, 2, figsize=(10, 7.4))
    venn_ax(axs[0, 0], ("AND", "B", "C"), "B AND C", "Geography majors who are also English majors:\nno overlap, so the query selects nothing", True)
    venn_ax(axs[0, 1], ("OR", "B", "C"), "B OR C", "Anyone majoring in Geography or English", True)
    venn_ax(axs[1, 0], ("AND", "A", "C"), "A AND C", "New Yorkers who major in English", True)
    venn_ax(axs[1, 1], ("OR", "A", "C"), "A OR C", "Anyone from New York or majoring in English", True)
    save(fig, f"{OUT}/venn-quiz.png")


def townships():
    """A made-up county of townships, each condition, then all three ANDed."""
    from shapely.geometry import MultiPoint, box
    from shapely.ops import voronoi_diagram
    rng = np.random.default_rng(370)
    pts = rng.uniform(0, 10, (40, 2))
    frame = box(0, 0, 10, 10)
    cells = [c.intersection(frame) for c in voronoi_diagram(MultiPoint(pts), envelope=frame).geoms]
    cx = np.array([c.centroid.x for c in cells]); cy = np.array([c.centroid.y for c in cells])
    dens = 20 + 160 * np.exp(-((cx - 3) ** 2 + (cy - 4) ** 2) / 14) + rng.normal(0, 10, len(cells))
    age = 33 + 1.3 * cy + rng.normal(0, 2.5, len(cells))
    vac = 6 + 0.8 * cx + rng.normal(0, 2, len(cells))
    a = dens > 50; b = age < 40; c = vac > 10
    sets = [(a, "a) Density > 50 per sq. mi."), (b, "b) Median age < 40"), (c, "c) Vacancy > 10%"),
            (a & b & c, "a AND b AND c")]
    fig, axs = plt.subplots(1, 4, figsize=(12, 3.6))
    for ax, (m, t) in zip(axs, sets):
        ax.set_aspect("equal"); ax.axis("off")
        for cell, on in zip(cells, m):
            ax.add_patch(MPoly(np.array(cell.exterior.coords), closed=True, fc=PINE if on else FOG, ec="white", lw=0.8))
        ax.add_patch(Rectangle((0, 0), 10, 10, fc="none", ec=NAVY, lw=1))
        ax.set_title(t, fontsize=11.5)
        ax.text(5, -0.8, f"{m.sum()} of {len(cells)} townships", ha="center", fontsize=10.5, color=BASIN)
        ax.set_xlim(-0.2, 10.2); ax.set_ylim(-1.5, 10.2)
    save(fig, f"{OUT}/townships-and.png")


def nulls():
    fig, ax = plt.subplots(figsize=(9, 4.6))
    ax.axis("off"); ax.set_aspect("equal")
    cols = ["ID", "Area", "Landuse", "Municip"]
    nl = {(3, "Landuse"), (6, "Landuse")}
    table(ax, 0, 4.3, sel=set(), cols=cols, nulls=nl)
    ax.text(4.4, 4.5, 'NOT ("Landuse" = \'Urban\')', fontsize=11, family="DejaVu Sans Mono", color=PINE)
    ax.text(4.4, 4.0, "selects 2 and 4 only. Parcels 3 and 6\nare dropped: NULL fails every test.", fontsize=10.5, va="top")
    ax.text(4.4, 2.6, '... OR "Landuse" IS NULL', fontsize=11, family="DejaVu Sans Mono", color=PINE)
    ax.text(4.4, 2.1, "adds them back: 2, 3, 4 and 6.", fontsize=10.5, va="top")
    ax.set_xlim(-0.1, 9.0); ax.set_ylim(-0.1, 5.1)
    save(fig, f"{OUT}/null-values.png")


if __name__ == "__main__":
    for w in (sys.argv[1:] or ["parcels", "record_attribute", "binary", "venns", "townships", "nulls"]):
        globals()[w]()
