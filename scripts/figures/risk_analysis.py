"""Figures for Chapter 21, Risk Analysis.

Usage: python risk_analysis.py <dir with Natural Earth GeoJSON:
    ne_10m_admin_0_countries, ne_10m_rivers_lake_centerlines,
    ne_10m_populated_places_simple>

The Three Little Pigs diagram, the risk framework, the Dhaka workflow, and the
made-up town are new diagrams. The AHP weights charted in weights.png are from
Dewan (2013), Tables 6.4-6.6.
"""
import sys
from pathlib import Path

import numpy as np
import geopandas as gpd
from matplotlib.patches import Circle, Polygon as MPoly, FancyBboxPatch, Rectangle
from matplotlib.colors import ListedColormap, BoundaryNorm
from scipy import ndimage

from style import (plt, save, NAVY, PINE, BLUE, BASIN, CORNER, FOG, CLAY, POPLAR,
                   GINKGO, SAND, DOGWOOD, BERRY, DUSK, LAND, WATER)

OUT = Path(__file__).resolve().parents[2] / "images" / "risk-analysis"
OUT.mkdir(parents=True, exist_ok=True)


def house(ax, x, y, fc, label, sub, s=1.0, ec=NAVY):
    body = Rectangle((x - 0.5 * s, y - 0.45 * s), 1.0 * s, 0.75 * s, fc=fc, ec=ec, lw=1.4, zorder=3)
    roof = MPoly([(x - 0.65 * s, y + 0.3 * s), (x, y + 0.85 * s), (x + 0.65 * s, y + 0.3 * s)],
                 closed=True, fc=fc, ec=ec, lw=1.4, zorder=3)
    door = Rectangle((x - 0.12 * s, y - 0.45 * s), 0.24 * s, 0.4 * s, fc="white", ec=ec, lw=1, zorder=4)
    for p in (body, roof, door):
        ax.add_patch(p)
    ax.text(x, y - 0.75 * s, label, ha="center", va="top", fontsize=10.5, weight="bold")
    ax.text(x, y - 1.12 * s, sub, ha="center", va="top", fontsize=9, color=BASIN)


def pigs():
    fig, ax = plt.subplots(figsize=(10, 5.6))
    ax.set_xlim(-6.2, 9.2); ax.set_ylim(-4.6, 4.2); ax.set_aspect("equal"); ax.axis("off")
    ax.add_patch(Circle((0, 0), 4.0, fc="#FDECEC", ec=CLAY, lw=1.8, ls="--", zorder=1))
    ax.text(0, 3.55, "Hazard footprint (the wolf's huff-and-puff reach)", ha="center",
            fontsize=9.5, color=CLAY, weight="bold")
    # The wolf: a simple marker
    ax.add_patch(Circle((0, 0.55), 0.55, fc=BASIN, ec=NAVY, lw=1.2, zorder=3))
    ax.add_patch(MPoly([(-0.45, 0.95), (-0.25, 1.45), (-0.05, 1.0)], fc=BASIN, ec=NAVY, zorder=3))
    ax.add_patch(MPoly([(0.45, 0.95), (0.25, 1.45), (0.05, 1.0)], fc=BASIN, ec=NAVY, zorder=3))
    ax.text(0, -0.2, "Wolf\n(hazard)", ha="center", va="top", fontsize=10.5, weight="bold")
    house(ax, -2.5, 1.1, GINKGO, "Straw", "most vulnerable")
    house(ax, 2.5, 1.1, "#C49A6C", "Sticks", "moderate")
    house(ax, 0, -2.4, CLAY, "Brick", "least vulnerable")
    house(ax, 7.0, 0.6, GINKGO, "Straw", "outside the reach:\nnot exposed")
    ax.annotate("", xy=(-1.95, 1.0), xytext=(-0.6, 0.6),
                arrowprops=dict(arrowstyle="-|>", color=CLAY, lw=2))
    ax.text(-6.0, -4.4, "Exposed: inside the dashed circle", fontsize=9.5, color=CLAY)
    save(fig, OUT / "three-pigs.png")


def framework():
    fig, ax = plt.subplots(figsize=(10, 4.6))
    ax.set_xlim(0, 10); ax.set_ylim(0, 5); ax.axis("off")
    ups = [("Hazard", "how likely and\nhow severe", CLAY, 1.2),
           ("Exposure", "who and what is\nin harm's way", POPLAR, 3.4),
           ("Vulnerability", "how easily they\nare harmed", BERRY, 5.6)]
    for name, sub, c, x in ups:
        ax.annotate("", xy=(x, 4.1), xytext=(x, 1.0),
                    arrowprops=dict(arrowstyle="simple,head_width=1.6,head_length=1.0,tail_width=0.9",
                                    fc=c, ec="none"))
        ax.text(x, 0.75, name, ha="center", va="top", fontsize=11.5, weight="bold", color=c)
        ax.text(x, 0.3, sub, ha="center", va="top", fontsize=9, color=BASIN)
    x = 8.4
    ax.annotate("", xy=(x, 1.0), xytext=(x, 4.1),
                arrowprops=dict(arrowstyle="simple,head_width=1.6,head_length=1.0,tail_width=0.9",
                                fc=PINE, ec="none"))
    ax.text(x, 0.75, "Capacity and measures", ha="center", va="top", fontsize=11.5,
            weight="bold", color=PINE)
    ax.text(x, 0.3, "planning, social and economic\ncapacity, management", ha="center",
            va="top", fontsize=9, color=BASIN)
    ax.text(3.4, 4.75, "push risk UP", ha="center", fontsize=11, weight="bold", color=NAVY)
    ax.text(8.4, 4.75, "pulls risk DOWN", ha="center", fontsize=11, weight="bold", color=NAVY)
    ax.plot([7.0, 7.0], [0.2, 4.9], color=CORNER, lw=1.2)
    save(fig, OUT / "risk-framework.png")


def dhaka_locator(ne):
    co = gpd.read_file(ne / "ne_10m_admin_0_countries.geojson")
    rv = gpd.read_file(ne / "ne_10m_rivers_lake_centerlines.geojson")
    pp = gpd.read_file(ne / "ne_10m_populated_places_simple.geojson")
    ext = (87.6, 93.2, 20.4, 26.9)
    fig, ax = plt.subplots(figsize=(6.4, 7.0))
    ax.set_facecolor(WATER)
    co.plot(ax=ax, color="#EEEDE6", ec=BASIN, lw=0.6)
    bd = co[co["ADM0_A3"] == "BGD"]
    bd.plot(ax=ax, color=LAND, ec=NAVY, lw=1.1)
    sub = rv.cx[ext[0]:ext[1], ext[2]:ext[3]]
    sub.plot(ax=ax, color=BLUE, lw=1.3)
    for name, lon, lat, rot in [("Ganges (Padma)", 88.9, 24.25, -28), ("Brahmaputra (Jamuna)", 89.55, 25.5, -85),
                                ("Meghna", 90.95, 23.85, -60)]:
        ax.text(lon, lat, name, fontsize=8.5, color="#1F5F8B", style="italic", rotation=rot,
                ha="center", va="center")
    d = pp[pp["name"] == "Dhaka"].iloc[0]
    ax.scatter([d.geometry.x], [d.geometry.y], s=90, c=CLAY, ec=NAVY, zorder=5)
    ax.text(d.geometry.x + 0.15, d.geometry.y + 0.1, "Dhaka", fontsize=12, weight="bold", zorder=5)
    ax.text(90.3, 21.0, "Bay of Bengal", fontsize=10, color="#1F5F8B", style="italic", ha="center")
    ax.text(91.9, 26.4, "INDIA", fontsize=9, color=BASIN, ha="center")
    ax.text(88.2, 22.1, "INDIA", fontsize=9, color=BASIN, ha="center")
    ax.text(90.0, 24.9, "BANGLADESH", fontsize=10, color=NAVY, weight="bold", ha="center")
    ax.text(92.9, 21.4, "MYANMAR", fontsize=9, color=BASIN, ha="right")
    ax.set_xlim(ext[0], ext[1]); ax.set_ylim(ext[2], ext[3])
    ax.set_xticks([88, 90, 92]); ax.set_yticks([21, 23, 25])
    ax.set_xticklabels(["88°E", "90°E", "92°E"]); ax.set_yticklabels(["21°N", "23°N", "25°N"])
    ax.tick_params(labelsize=8.5)
    save(fig, OUT / "dhaka-locator.png")


def node(ax, x, y, text, fc, w=2.3, h=0.75, fs=9, tc=NAVY, weight="normal"):
    ax.add_patch(FancyBboxPatch((x - w / 2, y - h / 2), w, h, boxstyle="round,pad=0.02,rounding_size=0.12",
                                fc=fc, ec=NAVY, lw=1.1, zorder=2))
    ax.text(x, y, text, ha="center", va="center", fontsize=fs, color=tc, weight=weight,
            zorder=3, linespacing=1.1)


def arr(ax, a, b, color=NAVY):
    ax.annotate("", xy=b, xytext=a, zorder=1,
                arrowprops=dict(arrowstyle="-|>", color=color, lw=1.2, shrinkA=0, shrinkB=0))


def workflow():
    fig, ax = plt.subplots(figsize=(11, 6.2))
    ax.set_xlim(0, 14); ax.set_ylim(0, 8); ax.axis("off")
    # Step labels
    for x, t in [(1.6, "Step 1\nHazard"), (6.6, "Step 2\nVulnerability"), (12.3, "Step 3\nRisk")]:
        ax.text(x, 7.6, t, ha="center", va="center", fontsize=10.5, weight="bold", color=PINE)
    node(ax, 1.6, 6.2, "Flood frequency\n(1988–2007)", SAND)
    node(ax, 1.6, 4.9, "Floodwater\ndepth", SAND)
    node(ax, 1.6, 3.2, "Flood hazard\n(4 classes)", CLAY, tc="white", weight="bold")
    arr(ax, (1.6, 5.82), (1.6, 5.28)); arr(ax, (1.6, 4.52), (1.6, 3.58))
    ax.text(1.75, 4.05, "overlay", fontsize=8.5, color=BASIN, style="italic")
    node(ax, 4.6, 6.2, "Physical\nelevation, land use,\nchannel, geology", SAND, w=2.6, h=1.05)
    node(ax, 7.4, 6.2, "Social\ndemographic, economic,\ninfrastructure", SAND, w=2.6, h=1.05)
    node(ax, 10.1, 6.2, "Coping capacity\nawareness, literacy,\nwealth, services", DOGWOOD, w=2.5, h=1.05)
    ax.text(6.0, 5.25, "AHP weights, WLC combines", ha="center", fontsize=8.5, color=BASIN,
            style="italic")
    node(ax, 6.6, 3.2, "Composite\nvulnerability", BERRY, tc="white", weight="bold", w=2.5)
    arr(ax, (4.6, 5.67), (6.1, 3.58)); arr(ax, (7.4, 5.67), (6.8, 3.58))
    arr(ax, (10.1, 5.67), (7.6, 3.5), color=PINE)
    ax.text(9.25, 4.4, "subtract", fontsize=8.5, color=PINE, style="italic", rotation=-38)
    node(ax, 12.3, 1.3, "Flood risk\nby community", NAVY, tc="white", weight="bold", w=2.5)
    ax.text(8.2, 0.75, "Risk = hazard × vulnerability", ha="center", fontsize=10.5, weight="bold")
    arr(ax, (1.6, 2.82), (11.05, 1.45)); arr(ax, (6.6, 2.82), (11.05, 1.6))
    save(fig, OUT / "dhaka-workflow.png")


def weights():
    groups = [
        ("Physical vulnerability", [("Elevation", 0.483), ("Land use", 0.316),
                                    ("Distance to channel", 0.145), ("Geology", 0.056)], CLAY),
        ("Social vulnerability", [("Demographic", 0.557), ("Economic", 0.320),
                                  ("Infrastructure\nand lifelines", 0.123)], BERRY),
        ("Coping capacity", [("Flood awareness", 0.464), ("Literacy", 0.267),
                             ("Housing price", 0.160), ("Shelters", 0.069), ("Hospitals", 0.040)], PINE),
    ]
    fig, axs = plt.subplots(1, 3, figsize=(12, 3.9))
    for ax, (title, items, c) in zip(axs, groups):
        names = [n for n, _ in items][::-1]
        vals = [v for _, v in items][::-1]
        ax.barh(names, vals, color=c)
        for i, v in enumerate(vals):
            ax.text(v + 0.01, i, f"{v:.3f}", va="center", fontsize=9)
        ax.set_xlim(0, 0.68)
        ax.set_title(title, fontsize=11.5)
        ax.spines[["top", "right"]].set_visible(False)
        ax.tick_params(labelsize=9)
        ax.set_xlabel("AHP weight (sums to 1)", fontsize=9)
    fig.tight_layout()
    save(fig, OUT / "weights.png")


def town():
    """Hazard, vulnerability, and risk for 36 made-up communities."""
    rng = np.random.default_rng(21)
    n = 6
    y, x = np.mgrid[0:n, 0:n]
    # Hazard: highest near a river along the left and bottom.
    hz = np.clip(4 - np.minimum(x, y) - (x + y) / 6 + rng.normal(0, 0.35, (n, n)), 0, None)
    hz = np.digitize(hz, [0.6, 1.6, 2.6])  # 0..3
    vu = np.clip(rng.normal(1.6, 0.9, (n, n)) + (x > 3) * 0.8 - (y > 3) * 0.5, 0, 3).round().astype(int)
    rk = hz * vu
    fig, axs = plt.subplots(1, 3, figsize=(11.5, 4.3))
    cm4 = ListedColormap(["#F3F4F4", "#F7C6C4", "#EE8A86", CLAY])
    cmv = ListedColormap(["#F3F4F4", "#E3BEDA", "#C774B2", BERRY])
    cmr = ListedColormap(["#F3F4F4", DOGWOOD, BLUE, NAVY])
    rnorm = BoundaryNorm([-0.5, 0.5, 2.5, 5.5, 9.5], 4)
    for ax, a, cm, t, norm in [(axs[0], hz, cm4, "Hazard (0–3)", None),
                               (axs[1], vu, cmv, "Vulnerability (0–3)", None),
                               (axs[2], rk, cmr, "Risk = hazard × vulnerability", rnorm)]:
        ax.imshow(a, cmap=cm, norm=norm, vmin=None if norm else 0, vmax=None if norm else 3, origin="lower")
        for (r, c), v in np.ndenumerate(a):
            dark = (norm is None and v >= 2) or (norm is not None and v >= 3)
            ax.text(c, r, str(v), ha="center", va="center", fontsize=10,
                    color="white" if dark else NAVY)
        ax.set_xticks(np.arange(-0.5, n, 1), minor=True)
        ax.set_yticks(np.arange(-0.5, n, 1), minor=True)
        ax.grid(which="minor", color="white", lw=2)
        ax.tick_params(which="both", length=0, labelbottom=False, labelleft=False)
        ax.set_title(t, fontsize=11.5)
    # Outline two communities: A, high hazard but no vulnerability (risk 0), and
    # B, moderate hazard but high vulnerability (risk 6).
    for ax in axs:
        for (r, c), lab in [((4, 0), "A"), ((2, 4), "B")]:
            ax.add_patch(Rectangle((c - 0.5, r - 0.5), 1, 1, fill=False, ec=GINKGO, lw=3))
            ax.text(c - 0.42, r + 0.42, lab, fontsize=8, weight="bold", color=NAVY, va="top",
                    bbox=dict(fc=GINKGO, ec="none", pad=1))
    fig.text(0.84, 0.02, "Risk classes: 0, 1–2, 3–5, 6–9", ha="center", fontsize=9, color=BASIN)
    fig.tight_layout()
    print("hazard\n", hz[::-1], "\nvuln\n", vu[::-1], "\nrisk\n", rk[::-1])
    save(fig, OUT / "town-risk.png")


if __name__ == "__main__":
    ne = Path(sys.argv[1]) if len(sys.argv) > 1 else Path("/tmp/ne")
    pigs()
    framework()
    dhaka_locator(ne)
    workflow()
    weights()
    town()
