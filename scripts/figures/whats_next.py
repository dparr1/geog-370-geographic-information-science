"""Figures for Chapter 19 (What's Next in GIS).

A diagram of how UNC's GIS courses connect, from the prerequisites in the
2026-27 UNC catalog, and a chart of red and near-infrared reflectance for NDVI
(illustrative values).

Usage: python whats_next.py
"""
from pathlib import Path
from matplotlib.patches import FancyBboxPatch
from style import plt, save, NAVY, PINE, BLUE, BASIN, FOG, CLAY, SAND, DOGWOOD, WATER

OUT = Path(__file__).resolve().parents[2] / "images" / "whats-next"
OUT.mkdir(parents=True, exist_ok=True)


def box(ax, x, y, code, title, fc, tc=NAVY, w=17, h=7.6):
    ax.add_patch(FancyBboxPatch((x - w / 2, y - h / 2), w, h,
                                boxstyle="round,pad=0,rounding_size=0.8",
                                fc=fc, ec=NAVY, lw=1.1, zorder=2))
    ax.text(x, y + 1.9, code, ha="center", va="center", weight="bold", fontsize=10.5, color=tc, zorder=3)
    ax.text(x, y - 1.4, title, ha="center", va="center", fontsize=8.6, color=tc, zorder=3, linespacing=1.1)


def arrow(ax, a, b, color=NAVY, rad=0.0):
    ax.annotate("", xy=b, xytext=a, zorder=1,
                arrowprops=dict(arrowstyle="-|>", color=color, lw=1.2,
                                shrinkA=0, shrinkB=0,
                                connectionstyle=f"arc3,rad={rad}"))


def course_path():
    fig, ax = plt.subplots(figsize=(10.5, 7.4))
    ax.set_xlim(0, 105)
    ax.set_ylim(0, 74)
    ax.axis("off")

    # Core of the GIS minor.
    box(ax, 11, 46, "GEOG 370", "GIScience\n(this course)", NAVY, tc="white")
    box(ax, 11, 14, "GEOG 215", "Intro to Spatial\nData Science", NAVY, tc="white")

    # Courses that need GEOG 370.
    col = 41
    rows = [("GEOG 455", "Cartography and\nGeovisualization", 64),
            ("GEOG 477", "Intro to Remote\nSensing", 55),
            ("GEOG 491", "Principles of GIS", 46),
            ("GEOG 567", "Google Earth\nEngine", 37),
            ("GEOG 592", "GIS Programming", 28),
            ("GEOG 594", "GPS and\nApplications", 19)]
    for code, title, y in rows:
        box(ax, col, y, code, title, DOGWOOD)
        arrow(ax, (19.5, 46), (col - 8.5, y))
    box(ax, col, 8, "GEOG 515", "Applied Spatial\nData Science", SAND)
    arrow(ax, (19.5, 46), (col - 8.5, 9.5))
    arrow(ax, (19.5, 14), (col - 8.5, 6.8))

    # Third tier.
    tx = 74
    box(ax, tx, 55, "GEOG 577", "Advanced Remote\nSensing", WATER)
    arrow(ax, (49.5, 55), (tx - 8.5, 55))
    box(ax, tx, 46, "GEOG 570", "Geographic\nInformation Analysis", WATER)
    arrow(ax, (49.5, 46), (tx - 8.5, 46))
    box(ax, tx, 37, "GEOG 586", "Scaling Up\nGeospatial Analysis", WATER)
    arrow(ax, (49.5, 45), (tx - 8.5, 38))
    box(ax, tx, 28, "GEOG 591", "Applied Issues\nin GIS", WATER)
    arrow(ax, (49.5, 44.5), (tx - 8.5, 29))

    for y, note in [(55, "or straight\nfrom 370"), (46, "also needs\nGEOG 391"), (28, "or straight\nfrom 370")]:
        ax.text(tx + 9.8, y, note, fontsize=8.6, color=BASIN, va="center", style="italic")

    for x, label, c in [(11, "Minor core", NAVY), (col, "Need GEOG 370", PINE), (tx, "Then", BLUE)]:
        ax.text(x, 71.5, label, ha="center", weight="bold", color=c)
    save(fig, OUT / "unc-course-path.png")


def ndvi():
    surfaces = ["Healthy\nvegetation", "Stressed\nvegetation", "Bare soil", "Water"]
    red = [0.05, 0.10, 0.25, 0.05]
    nir = [0.50, 0.30, 0.30, 0.02]
    fig, ax = plt.subplots(figsize=(8.5, 4.2))
    xs = range(len(surfaces))
    w = 0.36
    ax.bar([x - w / 2 for x in xs], red, w, color=CLAY, label="Red")
    ax.bar([x + w / 2 for x in xs], nir, w, color=PINE, label="Near-infrared")
    for x, r, n in zip(xs, red, nir):
        v = (n - r) / (n + r)
        ax.text(x, max(r, n) + 0.035, f"NDVI {v:.2f}", ha="center", weight="bold", color=NAVY)
    ax.set_xticks(list(xs))
    ax.set_xticklabels(surfaces)
    ax.set_ylabel("Share of light reflected")
    ax.set_ylim(0, 0.62)
    ax.spines[["top", "right"]].set_visible(False)
    ax.legend(frameon=False, loc="upper right")
    save(fig, OUT / "ndvi-reflectance.png")


if __name__ == "__main__":
    course_path()
    ndvi()
