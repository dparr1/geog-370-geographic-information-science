"""Diagrams for the OpenStreetMap and Data Quality chapter (images/osm-data-quality/).

Run from the repository root:  python3 scripts/figures/osm_data_quality.py [names]
The Nepal figures redraw data from Parr (2015), "Crisis Mapping and the Nepal
Earthquake: The Impact of New Contributors," Kartographische Nachrichten.
The OSM element diagram is made up.
"""
import sys, os
import numpy as np
sys.path.insert(0, os.path.dirname(__file__))
from style import *  # noqa
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch, Polygon as MPoly, FancyArrowPatch

OUT = "images/osm-data-quality"


def elements():
    items = [
        ("Lineage", "Where the data came from and\nwhat has been done to them"),
        ("Positional accuracy", "How close coordinates are\nto true positions"),
        ("Attribute accuracy", "How correct the non-spatial\nvalues are"),
        ("Logical consistency", "Whether the data follow their\nown rules (closed polygons,\nconnected roads)"),
        ("Completeness", "What is missing, and\nwhat is there that shouldn't be"),
        ("Temporal quality", "How current the data are,\nand how accurate their dates"),
        ("Usage, purpose,\nand constraints", "What the data were made for,\nand limits on their use"),
    ]
    fig, ax = plt.subplots(figsize=(11, 4.6))
    ax.set_xlim(0, 12); ax.set_ylim(0, 5.2); ax.axis("off")
    cols = [PINE, BLUE, DUSK, CLAY, POPLAR, BERRY, BASIN]
    pos = [(0.15 + i * 2.95, 2.75) for i in range(4)] + [(1.6 + i * 2.95, 0.15) for i in range(3)]
    for (x, y), (t, d), c in zip(pos, items, cols):
        ax.add_patch(FancyBboxPatch((x, y), 2.75, 2.3, boxstyle="round,pad=0.03", fc="white", ec=c, lw=2))
        ax.add_patch(FancyBboxPatch((x, y + 1.55), 2.75, 0.75, boxstyle="round,pad=0.03", fc=c, ec=c, lw=2))
        ax.text(x + 1.375, y + 1.92, t, ha="center", va="center", color="white", fontweight="bold",
                fontsize=10.5 if "\n" not in t else 9.5)
        ax.text(x + 1.375, y + 0.75, d, ha="center", va="center", fontsize=9.3)
    save(fig, f"{OUT}/quality-elements.png")


def osm_elements():
    fig, ax = plt.subplots(figsize=(11, 5.0))
    ax.set_xlim(0, 22); ax.set_ylim(0, 10); ax.set_aspect("equal"); ax.axis("off")
    # node
    ax.plot(2.5, 6.5, "o", ms=14, mfc=CLAY, mec=NAVY)
    ax.text(2.5, 9.3, "Node", ha="center", fontsize=13, fontweight="bold")
    ax.text(2.5, 8.55, "a single point", ha="center", fontsize=9.5, color=BASIN)
    tag = dict(boxstyle="round,pad=0.35", fc=SAND, ec=BASIN, lw=0.6)
    ax.text(2.5, 4.4, "amenity=cafe\nname=Epilogue", ha="center", va="top", fontsize=9, family="monospace", bbox=tag)
    # way (open)
    xs = [6.2, 7.6, 9.2, 10.6]; ys = [5.4, 7.3, 6.0, 7.6]
    ax.plot(xs, ys, color=NAVY, lw=3)
    ax.plot(xs, ys, "o", ms=8, mfc="white", mec=NAVY, mew=1.5)
    ax.text(8.4, 9.3, "Way", ha="center", fontsize=13, fontweight="bold")
    ax.text(8.4, 8.55, "an ordered list of nodes", ha="center", fontsize=9.5, color=BASIN)
    ax.text(8.4, 4.4, "highway=residential\nname=Franklin Street", ha="center", va="top", fontsize=9,
            family="monospace", bbox=tag)
    # closed way (area)
    poly = [(12.6, 5.3), (15.4, 5.3), (15.4, 7.8), (14.0, 7.8), (14.0, 6.7), (12.6, 6.7)]
    ax.add_patch(MPoly(poly, closed=True, fc=WATER, ec=NAVY, lw=3))
    for p in poly:
        ax.plot(*p, "o", ms=8, mfc="white", mec=NAVY, mew=1.5)
    ax.text(14.0, 9.3, "Closed way", ha="center", fontsize=13, fontweight="bold")
    ax.text(14.0, 8.55, "first node = last node: an area", ha="center", fontsize=9.5, color=BASIN)
    ax.text(14.0, 4.4, "building=university\nname=Saunders Hall", ha="center", va="top", fontsize=9,
            family="monospace", bbox=tag)
    # relation
    ax.plot([17.2, 18.4, 19.6], [5.2, 6.4, 5.4], color=PINE, lw=3)
    ax.plot([19.6, 20.6, 21.3], [5.4, 6.8, 7.8], color=PINE, lw=3, ls=(0, (4, 2)))
    for x, y in [(17.2, 5.2), (18.4, 6.4), (19.6, 5.4), (20.6, 6.8), (21.3, 7.8)]:
        ax.plot(x, y, "o", ms=7, mfc="white", mec=PINE, mew=1.5)
    ax.plot(18.9, 7.6, marker="s", ms=10, mfc=GINKGO, mec=NAVY)
    ax.text(19.3, 9.3, "Relation", ha="center", fontsize=13, fontweight="bold")
    ax.text(19.3, 8.55, "a group of elements", ha="center", fontsize=9.5, color=BASIN)
    ax.text(19.3, 4.4, "type=route\nroute=bus\nref=CW", ha="center", va="top", fontsize=9,
            family="monospace", bbox=tag)
    ax.text(11, 0.6, "Every element can carry tags: free-form key=value pairs (shown in the yellow boxes).",
            ha="center", fontsize=10.5, color=NAVY)
    save(fig, f"{OUT}/osm-elements.png")


def extrinsic_intrinsic():
    fig, axs = plt.subplots(1, 2, figsize=(11, 4.0))
    for ax in axs:
        ax.set_xlim(0, 10); ax.set_ylim(0, 7.4); ax.set_aspect("equal"); ax.axis("off")
    ax = axs[0]
    ax.set_title("Extrinsic: compare with a reference", fontsize=12)
    t = np.linspace(0.6, 9.4, 50)
    ref = 3.4 + 1.4 * np.sin(t / 1.6)
    osm = ref + 0.35 * np.sin(t * 2.3) + 0.15
    ax.plot(t, ref, color=NAVY, lw=5, alpha=0.35, label="Authoritative (e.g., TIGER)")
    ax.plot(t, osm, color=CLAY, lw=2, label="OpenStreetMap")
    for x in (2.0, 4.6, 7.6):
        i = np.argmin(abs(t - x))
        ax.annotate("", xy=(t[i], ref[i]), xytext=(t[i], osm[i]),
                    arrowprops=dict(arrowstyle="<->", color=BASIN, lw=1))
    ax.legend(loc="lower center", frameon=False, fontsize=9.5, ncol=1, bbox_to_anchor=(0.5, -0.05))
    ax.text(5, 6.4, "Measure the offset, and what\neach dataset has that the other lacks", ha="center",
            fontsize=9.5, color=BASIN)
    ax = axs[1]
    ax.set_title("Intrinsic: study OSM's own history", fontsize=12)
    stats = [("Editors who touched the area", "12"), ("Versions of each feature", "1 to 9"),
             ("Last edit", "3 months ago"), ("Validated tasks", "94%")]
    for i, (k, v) in enumerate(stats):
        y = 5.6 - i * 1.4
        ax.add_patch(FancyBboxPatch((0.4, y - 0.5), 9.2, 1.0, boxstyle="round,pad=0.03", fc=FOG, ec="none"))
        ax.text(0.8, y, k, va="center", fontsize=10)
        ax.text(9.2, y, v, va="center", ha="right", fontsize=11, fontweight="bold", color=PINE)
    save(fig, f"{OUT}/extrinsic-intrinsic.png")


def nepal_contributors():
    years = ["2005", "2006", "2007", "2008", "2009", "2010", "2011", "2012", "2013", "2014",
             "2015\nbefore\nquake", "2015\nafter\nquake"]
    n = [22, 84, 215, 553, 627, 621, 559, 937, 1629, 1690, 1788, 9989]
    fig, ax = plt.subplots(figsize=(10.5, 4.6))
    cols = [BLUE] * 11 + [CLAY]
    ax.bar(range(len(n)), n, color=cols, width=0.7)
    for i, v in enumerate(n):
        ax.text(i, v + 150, f"{v:,}", ha="center", va="bottom", fontsize=9.5, color=NAVY)
    ax.set_xticks(range(len(n))); ax.set_xticklabels(years, fontsize=9.5)
    ax.set_ylabel("Contributors who mapped in Nepal")
    ax.yaxis.set_major_formatter(plt.FuncFormatter(lambda v, p: f"{v:,.0f}"))
    for s in ("top", "right"):
        ax.spines[s].set_visible(False)
    ax.set_ylim(0, 11200)
    ax.text(5.0, 8200, "8,725 contributors joined in the ten years\nbefore the earthquake (blue bars combined)",
            ha="center", fontsize=10, color=BLUE, fontweight="bold")
    ax.text(10.2, 9900, "9,989 joined\nin the weeks after", ha="right", va="center", fontsize=10, color=CLAY,
            fontweight="bold")
    ax.set_title("Contributors to OpenStreetMap in Nepal, by the year they joined", fontsize=12, loc="left")
    save(fig, f"{OUT}/nepal-contributors.png")


def nepal_edits():
    fig, axs = plt.subplots(1, 3, figsize=(11, 3.7))
    data = [("Features per contributor\n(created, modified, deleted)", 223.5, 108.6, "{:.1f}"),
            ("Existing features changed per\ncontributor (modified, deleted)", 63.1, 14.1, "{:.1f}"),
            ("Changes to existing features as a\nshare of a contributor's edits", 20.1, 12.6, "{:.1f}%")]
    for ax, (t, a, b, f) in zip(axs, data):
        ax.bar([0, 1], [a, b], color=[BLUE, CLAY], width=0.6)
        for x, v in zip([0, 1], [a, b]):
            ax.text(x, v * 1.02, f.format(v), ha="center", va="bottom", fontsize=11, fontweight="bold")
        ax.set_xticks([0, 1]); ax.set_xticklabels(["Joined before\n25 April 2015", "Joined 25 April\nto 6 May 2015"],
                                                   fontsize=9.5)
        ax.set_yticks([])
        for s in ("top", "right", "left"):
            ax.spines[s].set_visible(False)
        ax.set_title(t, fontsize=10.5)
        ax.set_ylim(0, max(a, b) * 1.2)
    fig.tight_layout()
    save(fig, f"{OUT}/nepal-edits.png")


def hot_workflow():
    fig, ax = plt.subplots(figsize=(11, 2.8))
    ax.set_xlim(0, 12); ax.set_ylim(0, 3); ax.axis("off")
    steps = [("1. Remote mapping", "Volunteers anywhere trace roads\nand buildings from satellite imagery", BLUE),
             ("2. Field mapping", "Local mappers add street names,\nbuilding uses, and evacuation sites", PINE),
             ("3. Response", "Aid organizations use the map\nto plan and deliver help", CLAY)]
    for i, (t, d, c) in enumerate(steps):
        x = 0.2 + i * 4.0
        ax.add_patch(FancyBboxPatch((x, 0.3), 3.4, 2.4, boxstyle="round,pad=0.04", fc="white", ec=c, lw=2.2))
        ax.text(x + 1.7, 2.15, t, ha="center", va="center", fontsize=12, fontweight="bold", color=c)
        ax.text(x + 1.7, 1.15, d, ha="center", va="center", fontsize=9.8)
        if i < 2:
            ax.annotate("", xy=(x + 3.95, 1.5), xytext=(x + 3.5, 1.5),
                        arrowprops=dict(arrowstyle="-|>", color=NAVY, lw=2))
    save(fig, f"{OUT}/hot-workflow.png")


FUNCS = dict(elements=elements, osm_elements=osm_elements, extrinsic=extrinsic_intrinsic,
             contributors=nepal_contributors, edits=nepal_edits, hot=hot_workflow)

if __name__ == "__main__":
    os.makedirs(OUT, exist_ok=True)
    for n in (sys.argv[1:] or list(FUNCS)):
        FUNCS[n]()
