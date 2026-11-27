"""Diagrams for the Census Data chapter (images/census-data/).

Run from the repository root:  python3 scripts/figures/census_data.py [names]
The nested-geography panels and the margin-of-error estimates are made up.
"""
import sys, os
import numpy as np
sys.path.insert(0, os.path.dirname(__file__))
from style import *  # noqa
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch, Rectangle, Polygon as MPoly

OUT = "images/census-data"


def hierarchy():
    fig, ax = plt.subplots(figsize=(10, 6.4))
    ax.set_xlim(0, 10); ax.set_ylim(0, 9.4); ax.axis("off")
    spine = ["Nation", "Regions (4)", "Divisions (9)", "States (50 + DC)", "Counties (about 3,100)",
             "Census tracts (about 85,000)", "Block groups (about 240,000)", "Blocks (about 8 million)"]
    ys = np.linspace(8.7, 0.6, len(spine))
    for y, s in zip(ys, spine):
        ax.add_patch(FancyBboxPatch((3.0, y - 0.36), 4.0, 0.72, boxstyle="round,pad=0.03",
                                    fc=PINE, ec=NAVY, lw=0.8))
        ax.text(5.0, y, s, ha="center", va="center", color="white", fontsize=10.5, fontweight="bold")
    for y0, y1 in zip(ys[:-1], ys[1:]):
        ax.annotate("", xy=(5, y1 + 0.38), xytext=(5, y0 - 0.38),
                    arrowprops=dict(arrowstyle="-|>", color=NAVY, lw=1.2))
    off = [(ys[4], "Metropolitan and micropolitan\nstatistical areas (built from counties)", 0),
           (ys[5] + 0.3, "Places: cities, towns, and\ncensus-designated places", 1),
           (ys[6], "ZIP Code Tabulation Areas\n(ZCTAs)", 1),
           (ys[5] - 0.6, "School districts, congressional\nand legislative districts", 0),
           (ys[3], "American Indian, Alaska Native,\nand Native Hawaiian areas", 0)]
    for y, s, side in off:
        x = 8.6 if side else 1.4
        ax.add_patch(FancyBboxPatch((x - 1.35, y - 0.38), 2.7, 0.76, boxstyle="round,pad=0.03",
                                    fc=SAND, ec=BASIN, lw=0.8, ls="--"))
        ax.text(x, y, s, ha="center", va="center", fontsize=8.6)
        ax.plot([x - 1.35 if side else x + 1.35, 7.0 if side else 3.0], [y, y], color=BASIN, lw=0.8, ls=":")
    ax.text(5, 9.3, "The spine: each level nests inside the one above", ha="center", fontsize=11,
            fontweight="bold", color=PINE)
    ax.text(1.4, 9.3, "Off the spine", ha="center", fontsize=11, fontweight="bold", color=BASIN)
    ax.text(8.6, 9.3, "Off the spine", ha="center", fontsize=11, fontweight="bold", color=BASIN)
    save(fig, f"{OUT}/hierarchy.png")


def nesting():
    """A made-up tract split into block groups and blocks."""
    rng = np.random.default_rng(8)
    fig, axs = plt.subplots(1, 3, figsize=(11.5, 4.1))
    # block grid: 6 x 5 irregular-ish blocks
    xs = np.array([0, 1.4, 2.9, 4.1, 5.6, 7.0, 8.0])
    ys = np.array([0, 1.3, 2.6, 4.2, 5.4, 6.5])
    jitter = rng.normal(0, 0.12, (len(ys), len(xs)))
    jitter[:, 0] = 0; jitter[:, -1] = 0; jitter[0, :] = 0; jitter[-1, :] = 0
    def pt(i, j):
        return (xs[j] + jitter[i, j], ys[i] + jitter[(i + 1) % len(ys), j] * 0.8 if 0 < i < len(ys) - 1 and 0 < j < len(xs) - 1 else ys[i])
    bg_of = lambda i, j: (0 if j < 3 else 1) + (0 if i < 2 else 2)
    bgc = [DOGWOOD, SAND, WATER, "#E8D9F0"]
    titles = ["Census tract", "Block groups", "Blocks"]
    for k, ax in enumerate(axs):
        ax.set_xlim(-0.3, 8.3); ax.set_ylim(-0.3, 6.8); ax.set_aspect("equal"); ax.axis("off")
        ax.set_title(titles[k], fontsize=12.5)
        for i in range(len(ys) - 1):
            for j in range(len(xs) - 1):
                poly = [pt(i, j), pt(i, j + 1), pt(i + 1, j + 1), pt(i + 1, j)]
                if k == 0:
                    continue
                elif k == 1:
                    fc = bgc[bg_of(i, j)]; ec, lw = fc, 0
                else:
                    fc = bgc[bg_of(i, j)]; ec, lw = "white", 1.4
                ax.add_patch(MPoly(poly, closed=True, fc=fc, ec=ec, lw=lw))
        if k == 0:
            ax.add_patch(Rectangle((0, 0), 8, 6.5, fc=DOGWOOD, ec="none"))
        ax.add_patch(Rectangle((0, 0), 8, 6.5, fill=False, ec=NAVY, lw=2.4))
        if k >= 1:
            # block group boundaries
            ax.plot([pt(i, 3)[0] for i in range(len(ys))], [pt(i, 3)[1] for i in range(len(ys))], color=NAVY, lw=1.6)
            ax.plot([pt(2, j)[0] for j in range(len(xs))], [pt(2, j)[1] for j in range(len(xs))], color=NAVY, lw=1.6)
        if k == 1:
            for n, (cx, cy) in enumerate([(2.0, 1.3), (5.6, 1.3), (2.0, 4.4), (5.6, 4.4)]):
                ax.text(cx, cy, f"BG {n + 1}", ha="center", va="center", fontsize=11, fontweight="bold")
        if k == 0:
            ax.text(4, 3.25, "Tract 0107.01\nabout 4,000 people", ha="center", va="center", fontsize=11,
                    fontweight="bold")
    axs[2].text(4, -0.25, "Blocks follow streets, streams, and rail lines", ha="center", va="top", fontsize=9.5,
                color=BASIN)
    save(fig, f"{OUT}/nesting.png")


def geoid():
    fig, ax = plt.subplots(figsize=(10.5, 3.0))
    ax.set_xlim(0, 15.6); ax.set_ylim(-1.6, 1.6); ax.axis("off")
    s = "371350107011003"
    parts = [(0, 2, "State", "37 = North Carolina", PINE), (2, 5, "County", "135 = Orange", CLAY),
             (5, 11, "Tract", "010701 = Tract 107.01", DUSK), (11, 12, "Block group", "1", POPLAR),
             (11, 15, "Block", "1003 (its first digit\nis the block group)", BERRY)]
    w = 1.0
    for i, ch in enumerate(s):
        c = [p for p in parts[:3] if p[0] <= i < p[1]]
        c = c[0][4] if c else (POPLAR if i == 11 else BERRY)
        ax.add_patch(Rectangle((0.3 + i * w, -0.4), w * 0.94, 0.8, fc=c, ec="white"))
        ax.text(0.3 + i * w + w * 0.47, 0, ch, ha="center", va="center", color="white", fontsize=16,
                fontweight="bold", family="monospace")
    for a, b, name, desc, c in parts:
        x0 = 0.3 + a * w; x1 = 0.3 + b * w - 0.06
        if name == "Block":
            y = -0.6; va = "top"; ax.plot([x0, x0, x1, x1], [y + 0.12, y, y, y + 0.12], color=c, lw=1.6)
            ax.text((x0 + x1) / 2, y - 0.1, f"{name}: {desc}", ha="center", va="top", fontsize=9.5, color=c,
                    fontweight="bold")
        else:
            y = 0.6; ax.plot([x0, x0, x1, x1], [y - 0.12, y, y, y - 0.12], color=c, lw=1.6)
            ax.text((x0 + x1) / 2, y + 0.1, f"{name}\n{desc}", ha="center", va="bottom", fontsize=9.5, color=c,
                    fontweight="bold")
    save(fig, f"{OUT}/geoid.png")


def moe():
    fig, ax = plt.subplots(figsize=(9.5, 4.0))
    names = ["Tract A", "Tract B", "Tract C", "Tract D", "Tract E"]
    est = np.array([48200, 52900, 61500, 39800, 75400])
    m = np.array([9100, 12400, 6800, 15300, 21800])
    y = np.arange(len(names))[::-1]
    for yi, e, mm, n in zip(y, est, m, names):
        cv = (mm / 1.645) / e * 100
        col = PINE if cv < 12 else (POPLAR if cv <= 40 else CLAY)
        ax.plot([e - mm, e + mm], [yi, yi], color=col, lw=6, alpha=0.35, solid_capstyle="round")
        ax.plot(e, yi, "o", color=col, ms=10)
        ax.text(e + mm + 1500, yi, f"\\${e:,} ± \\${mm:,}   (CV {cv:.0f}%)", va="center", fontsize=9.8, color=NAVY)
    ax.set_yticks(y); ax.set_yticklabels(names)
    ax.set_xlim(20000, 125000)
    ax.xaxis.set_major_formatter(plt.FuncFormatter(lambda v, p: f"\\${v / 1000:.0f}k"))
    ax.set_xlabel("Median household income (ACS 5-year estimate, 90% margin of error)")
    for s in ("top", "right", "left"):
        ax.spines[s].set_visible(False)
    ax.tick_params(axis="y", length=0)
    ax.grid(axis="x", color=CORNER, lw=0.6); ax.set_axisbelow(True)
    ax.set_title("Estimates are ranges, not points", fontsize=12.5, loc="left")
    save(fig, f"{OUT}/margin-of-error.png")


def acs_periods():
    fig, ax = plt.subplots(figsize=(10, 2.9))
    ax.set_xlim(2018.6, 2025.4); ax.set_ylim(-0.3, 2.9); ax.axis("off")
    for yr in range(2019, 2025):
        ax.text(yr + 0.5, 2.55, str(yr), ha="center", fontsize=10, color=BASIN)
        ax.plot([yr, yr], [0, 2.4], color=CORNER, lw=0.8, zorder=0)
    ax.plot([2025, 2025], [0, 2.4], color=CORNER, lw=0.8, zorder=0)
    ax.add_patch(FancyBboxPatch((2024.03, 1.55), 0.94, 0.6, boxstyle="round,pad=0.02", fc=CLAY, ec="none"))
    ax.text(2024.5, 1.85, "1-year", ha="center", va="center", color="white", fontweight="bold", fontsize=10.5)
    ax.text(2023.95, 1.85, "2024 ACS 1-year: 12 months of data,\nonly areas with 65,000+ people", ha="right",
            va="center", fontsize=9.8, color=CLAY)
    ax.add_patch(FancyBboxPatch((2020.03, 0.45), 4.94, 0.6, boxstyle="round,pad=0.02", fc=PINE, ec="none"))
    ax.text(2022.5, 0.75, "2020–2024 ACS 5-year: 60 months of data, every area down to block groups",
            ha="center", va="center", color="white", fontweight="bold", fontsize=10.5)
    save(fig, f"{OUT}/acs-periods.png")


FUNCS = dict(hierarchy=hierarchy, nesting=nesting, geoid=geoid, moe=moe, acs=acs_periods)

if __name__ == "__main__":
    os.makedirs(OUT, exist_ok=True)
    for n in (sys.argv[1:] or list(FUNCS)):
        FUNCS[n]()
