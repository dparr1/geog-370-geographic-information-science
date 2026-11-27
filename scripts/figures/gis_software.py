"""Figures for Chapters 20 and 21 (Getting to Know QGIS and ArcGIS Pro).

Timelines, a map-making workflow, and schematic diagrams of the ArcGIS Pro
window, project, and Geoprocessing pane. The ArcGIS Pro diagrams are drawn
from scratch (not screenshots), so they show the layout, not every button.
The QGIS screenshots come from qgis_screenshots.py and qgis_annotate.py.

Usage: python gis_software.py
"""
from pathlib import Path
from matplotlib.patches import FancyBboxPatch, Rectangle, Circle
from style import plt, save, NAVY, PINE, BLUE, BASIN, CORNER, FOG, CLAY, POPLAR, SAND, DOGWOOD, LAND, WATER, GINKGO

OUT = Path(__file__).resolve().parents[2] / "images"
(OUT / "qgis").mkdir(parents=True, exist_ok=True)
(OUT / "arcgis-pro").mkdir(parents=True, exist_ok=True)


def badge(ax, x, y, n, r=1.6):
    ax.add_patch(Circle((x, y), r, fc=CLAY, ec="white", lw=1.5, zorder=10))
    ax.text(x, y, str(n), ha="center", va="center", color="white", fontsize=10, weight="bold", zorder=11)


def rbox(ax, x, y, w, h, fc, ec=NAVY, lw=1, r=0.6, z=1):
    ax.add_patch(FancyBboxPatch((x, y), w, h, boxstyle=f"round,pad=0,rounding_size={r}", fc=fc, ec=ec, lw=lw, zorder=z))


# ---------------------------------------------------------------- timelines
def timeline(events, path, color, start, end, title):
    fig, ax = plt.subplots(figsize=(10, 3.8))
    ax.set_xlim(start - 2.5, end + 2.5)
    ax.set_ylim(-3.6, 3.6)
    ax.axis("off")
    ax.plot([start - 0.5, end + 0.5], [0, 0], color=NAVY, lw=2, zorder=1)
    for yr in range(start, end + 1):
        if yr % 5 == 0:
            ax.plot([yr, yr], [-0.15, 0.15], color=NAVY, lw=1)
            ax.text(yr, -0.3, str(yr), ha="center", va="top", fontsize=8.5, color=BASIN)
    for i, (x, label, detail) in enumerate(events):
        s = 1 if i % 2 == 0 else -1
        ax.plot([x, x], [0, s * 1.15], color=color, lw=1.2, zorder=1)
        ax.scatter([x], [0], s=55, color=color, edgecolor="white", zorder=3)
        if s > 0:
            ax.text(x, 1.3, detail, ha="center", va="bottom", fontsize=8.2, color=BASIN, linespacing=1.15)
            ax.text(x, 1.3 + 0.36 * (detail.count("\n") + 1) + 0.12, label, ha="center", va="bottom", fontsize=9.5, weight="bold")
        else:
            ax.text(x, -1.3, label, ha="center", va="top", fontsize=9.5, weight="bold")
            ax.text(x, -1.78, detail, ha="center", va="top", fontsize=8.2, color=BASIN, linespacing=1.15)
    ax.set_title(title, loc="left", fontsize=12)
    save(fig, path)


timeline([
    (2002.5, "2002", "Gary Sherman starts\nQuantum GIS"),
    (2007.5, "2007", "Joins OSGeo\nas an incubator project"),
    (2009, "2009", "1.0 \u201cKore\u201d"),
    (2013.7, "2013", "2.0 \u201cDufour\u201d: renamed QGIS;\nSEXTANTE tools built in"),
    (2018.15, "2018", "3.0 \u201cGirona\u201d:\nQt5 and Python 3"),
    (2022.5, "every 4 months", "new release; every third\nis long-term (LTR)"),
    (2026.2, "2026", "4.0 \u201cNorrk\u00f6ping\u201d:\nQt6"),
], OUT / "qgis" / "qgis-timeline.png", PINE, 2000, 2027, "A short history of QGIS")

timeline([
    (1969, "1969", "Jack and Laura Dangermond\nfound Esri in Redlands, CA"),
    (1982, "1982", "ARC/INFO, a command-\nline GIS"),
    (1992, "1992", "ArcView GIS"),
    (1999.9, "1999\u20132001", "ArcGIS 8: ArcMap\nand ArcCatalog"),
    (2004.4, "2004", "ArcGIS 9 adds\nArcGIS Server"),
    (2015.1, "2015", "ArcGIS Pro 1.0:\n64-bit, 2D and 3D"),
    (2022.5, "2022", "ArcGIS Pro 3.0"),
    (2026.2, "2026", "ArcMap retired\n(March 1)"),
], OUT / "arcgis-pro" / "esri-timeline.png", BLUE, 1967, 2027, "A short history of Esri's desktop GIS")


# ---------------------------------------------------------- map workflow
def workflow():
    steps = [
        ("1  Add data", "layers from files,\ndatabases, or the web", WATER),
        ("2  Check the CRS", "pick a projection that\nsuits the map's area", WATER),
        ("3  Symbolize", "classify and color by\nan attribute", DOGWOOD),
        ("4  Label", "name the features\nthat matter", DOGWOOD),
        ("5  Lay out", "title, legend, scale bar,\nnorth arrow, source", SAND),
        ("6  Export", "PNG, PDF, or SVG\nat print resolution", SAND),
    ]
    fig, ax = plt.subplots(figsize=(11, 2.6))
    ax.set_xlim(0, 61)
    ax.set_ylim(0, 12)
    ax.axis("off")
    w, gap = 8.6, 1.68
    for i, (head, body, fc) in enumerate(steps):
        x = 0.5 + i * (w + gap)
        rbox(ax, x, 1.5, w, 9, fc)
        ax.text(x + w / 2, 8.4, head, ha="center", va="center", fontsize=9.2, weight="bold")
        ax.text(x + w / 2, 4.6, body, ha="center", va="center", fontsize=7.4, color=BASIN, linespacing=1.3)
        if i < len(steps) - 1:
            ax.annotate("", xy=(x + w + gap - 0.1, 6), xytext=(x + w + 0.1, 6),
                        arrowprops=dict(arrowstyle="-|>", color=NAVY, lw=1.4))
    ax.text(0.5 + 1 * (w + gap) - gap / 2, 0.4, "Map view", ha="center", fontsize=8, color=BASIN, style="italic")
    ax.text(0.5 + 2 * (w + gap) + w + gap / 2, 0.4, "Layer properties / Symbology", ha="center", fontsize=8, color=BASIN, style="italic")
    ax.text(0.5 + 4 * (w + gap) + w + gap / 2, 0.4, "Print layout", ha="center", fontsize=8, color=BASIN, style="italic")
    save(fig, OUT / "qgis" / "map-workflow.png")


workflow()


# ------------------------------------------------- ArcGIS Pro interface
def arcgis_interface():
    fig, ax = plt.subplots(figsize=(10, 6.4))
    ax.set_xlim(0, 100)
    ax.set_ylim(0, 64)
    ax.axis("off")
    ax.add_patch(Rectangle((0, 0), 100, 64, fc="white", ec=NAVY, lw=1.5))
    # title bar with quick access toolbar
    ax.add_patch(Rectangle((0, 60.5), 100, 3.5, fc=NAVY, ec=NAVY))
    for i in range(5):
        ax.add_patch(Rectangle((1 + i * 2.4, 61.3), 1.8, 1.8, fc="#8fa4c2", ec="none"))
    ax.text(50, 62.25, "NC_Density \u2014 Map \u2014 ArcGIS Pro", color="white", ha="center", va="center", fontsize=9)
    ax.text(92, 62.25, "Sign in", color="white", ha="center", va="center", fontsize=8)
    # ribbon tabs
    tabs = ["Project", "Map", "Insert", "Analysis", "View", "Edit", "Imagery", "Share", "Help"]
    x = 1
    for t in tabs:
        w = len(t) * 1.05 + 2
        sel = t == "Map"
        ax.add_patch(Rectangle((x, 57.3), w, 3, fc="white" if sel else FOG, ec=CORNER if not sel else NAVY, lw=0.8))
        ax.text(x + w / 2, 58.8, t, ha="center", va="center", fontsize=8.5, weight="bold" if sel else "normal",
                color="white" if t == "Project" else NAVY)
        if t == "Project":
            ax.add_patch(Rectangle((x, 57.3), w, 3, fc=BLUE, ec=BLUE))
            ax.text(x + w / 2, 58.8, t, ha="center", va="center", fontsize=8.5, color="white")
        x += w + 0.3
    ax.text(x + 1.5, 58.8, "Feature Layer  |  Labeling  |  Data", ha="left", va="center", fontsize=8, color=BERRY_ if False else "#9F237E")
    # ribbon groups
    ax.add_patch(Rectangle((0, 49), 100, 8.3, fc="white", ec=CORNER))
    groups = ["Clipboard", "Navigate", "Layer", "Selection", "Inquiry", "Labeling", "Offline"]
    gw = 100 / len(groups)
    for i, g in enumerate(groups):
        gx = i * gw
        for j in range(3):
            ax.add_patch(Rectangle((gx + 1.5 + j * 4.3, 52.3), 3.2, 3.2, fc=[WATER, DOGWOOD, SAND][j % 3], ec=CORNER, lw=0.6))
        ax.text(gx + gw / 2, 50.0, g, ha="center", va="center", fontsize=7.5, color=BASIN)
        if i:
            ax.plot([gx, gx], [49.5, 56.8], color=CORNER, lw=0.8)
    # contents pane
    ax.add_patch(Rectangle((0, 4), 20, 45, fc=FOG, ec=CORNER))
    ax.text(1, 47, "Contents", fontsize=9.5, weight="bold", va="center")
    ax.text(1, 44.6, "Drawing Order", fontsize=7.5, color=BASIN, va="center")
    items = [("Map", None, 0), ("cities", CLAY, 1), ("rivers", BLUE, 1), ("counties", DOGWOOD, 1),
             ("Topographic", CORNER, 1)]
    for k, (name, c, ind) in enumerate(items):
        yy = 41.5 - k * 3.1
        ax.add_patch(Rectangle((1 + ind * 1.5, yy - 0.7), 1.4, 1.4, fc="white", ec=NAVY, lw=0.6))
        ax.text(1.7 + ind * 1.5, yy, "\u2713", ha="center", va="center", fontsize=7)
        if c:
            ax.add_patch(Rectangle((3.2 + ind * 1.5, yy - 0.6), 1.2, 1.2, fc=c, ec="none"))
        ax.text(5 + ind * 1.5, yy, name, va="center", fontsize=8.5, weight="bold" if k == 0 else "normal")
    # map view
    ax.add_patch(Rectangle((20, 4), 58, 45, fc=WATER, ec=CORNER))
    ax.add_patch(Rectangle((20.5, 46), 9, 2.6, fc="white", ec=CORNER))
    ax.text(25, 47.3, "Map", ha="center", va="center", fontsize=8.5, weight="bold")
    ax.add_patch(Rectangle((29.7, 46), 9, 2.6, fc=FOG, ec=CORNER))
    ax.text(34.2, 47.3, "Layout", ha="center", va="center", fontsize=8.5, color=BASIN)
    xs = [24, 30, 38, 46, 55, 64, 72, 75, 70, 62, 55, 47, 40, 33, 27]
    ys = [26, 31, 33, 34, 35, 37, 33, 27, 20, 14, 11, 16, 20, 21, 22]
    ax.fill(xs, ys, fc=LAND, ec=PINE, lw=1)
    for (px, py) in [(34, 27), (48, 28), (57, 24), (63, 30), (68, 20)]:
        ax.add_patch(Circle((px, py), 0.7, fc=CLAY, ec="white"))
    ax.plot([30, 38, 45, 52, 58, 61], [31, 28, 25, 22, 18, 12], color=BLUE, lw=1.5)
    # catalog pane
    ax.add_patch(Rectangle((78, 4), 22, 45, fc=FOG, ec=CORNER))
    ax.text(79, 47, "Catalog", fontsize=9.5, weight="bold", va="center")
    for k, name in enumerate(["Maps", "Layouts", "Toolboxes", "Databases", "Styles", "Folders", "Locators"]):
        ax.text(80, 43 - k * 3, "›  " + name, va="center", fontsize=8.5)
    ax.add_patch(Rectangle((78, 4), 22, 8, fc="white", ec=CORNER))
    ax.text(78.6, 10, "Catalog | Geoprocessing | Symbology", fontsize=6.2, color=BASIN, va="center")
    ax.text(89, 7, "(other panes share\nthe same space as tabs)", fontsize=7, color=BASIN, ha="center", va="center", style="italic")
    # status bar
    ax.add_patch(Rectangle((0, 0), 100, 4, fc=FOG, ec=CORNER))
    ax.text(22, 2, "1:3,365,000  ⌄", fontsize=8, va="center")
    ax.text(40, 2, "79.05\u00b0W  35.91\u00b0N  ⌄", fontsize=8, va="center")
    ax.text(62, 2, "Selected Features: 0", fontsize=8, va="center")
    for n, (bx, by) in enumerate([(13.5, 62.25), (97.6, 58.8), (42.8, 50.6), (14, 47), (49, 40), (95, 47), (12, 2)], 1):
        badge(ax, bx, by, n)
    save(fig, OUT / "arcgis-pro" / "arcgis-pro-interface.png")


BERRY_ = None
arcgis_interface()


# ----------------------------------------------------- project structure
def arcgis_project():
    fig, ax = plt.subplots(figsize=(10, 4.6))
    ax.set_xlim(0, 100)
    ax.set_ylim(0, 46)
    ax.axis("off")
    rbox(ax, 1, 1, 98, 44, "white", lw=1.5, r=1)
    ax.text(3, 42.3, "NC_Density\\   (the project folder)", fontsize=10.5, weight="bold", va="center")
    rbox(ax, 4, 6, 37, 33, WATER, r=0.8)
    ax.text(22.5, 36.3, "NC_Density.aprx", ha="center", fontsize=10.5, weight="bold")
    ax.text(22.5, 33.6, "the project file: stores settings and links, not data", ha="center", fontsize=7.8, color=BASIN)
    for k, (h, d) in enumerate([("Maps", "layers, symbology, labels"), ("Layouts", "pages for printing or export"),
                                ("Connections", "to folders, databases, servers"), ("Toolboxes and tasks", "saved models and workflows")]):
        rbox(ax, 6.5, 26 - k * 5.8, 32, 4.6, "white", r=0.5)
        ax.text(8, 29.4 - k * 5.8, h, fontsize=8.8, weight="bold", va="center")
        ax.text(8, 27.3 - k * 5.8, d, fontsize=7.6, color=BASIN, va="center")
    rbox(ax, 46, 23, 24, 16, DOGWOOD, r=0.8)
    ax.text(58, 36.3, "NC_Density.gdb", ha="center", fontsize=10.5, weight="bold")
    ax.text(58, 33.6, "default file geodatabase", ha="center", fontsize=7.8, color=BASIN)
    ax.text(58, 28.5, "counties\nrivers\ncounties_Buffer", ha="center", va="center", fontsize=8.5, linespacing=1.35)
    rbox(ax, 46, 6, 24, 13.5, SAND, r=0.8)
    ax.text(58, 16.6, "NC_Density.atbx", ha="center", fontsize=10.5, weight="bold")
    ax.text(58, 13.4, "default toolbox for\nmodels and scripts", ha="center", va="center", fontsize=7.8, color=BASIN)
    rbox(ax, 74, 23, 23, 16, FOG, r=0.8)
    ax.text(85.5, 36.3, "ImportLog, Index,", ha="center", fontsize=9, weight="bold")
    ax.text(85.5, 33.6, "and other folders", ha="center", fontsize=9, weight="bold")
    ax.text(85.5, 28.5, "created by ArcGIS Pro;\nleave them alone", ha="center", va="center", fontsize=7.8, color=BASIN)
    rbox(ax, 74, 6, 23, 13.5, "white", ec=CLAY, r=0.8)
    ax.text(85.5, 15.8, "Your data elsewhere", ha="center", fontsize=9, weight="bold")
    ax.text(85.5, 11, "shapefiles, CSVs, rasters\non a USB drive or\nnetwork share", ha="center", va="center", fontsize=7.8, color=BASIN)
    ax.annotate("", xy=(46, 31), xytext=(41, 31), arrowprops=dict(arrowstyle="-|>", color=NAVY))
    ax.annotate("", xy=(46, 12.5), xytext=(41, 12.5), arrowprops=dict(arrowstyle="-|>", color=NAVY))
    ax.plot([22.5, 22.5, 85.5], [6, 3.6, 3.6], color=CLAY, ls="--", lw=1)
    ax.annotate("", xy=(85.5, 6), xytext=(85.5, 3.5), arrowprops=dict(arrowstyle="-|>", color=CLAY))
    ax.text(54, 4.3, "links to outside data break if those files move", fontsize=7.8, color=CLAY, ha="center")
    save(fig, OUT / "arcgis-pro" / "arcgis-pro-project.png")


arcgis_project()


# --------------------------------------------------- geoprocessing pane
def arcgis_gp():
    fig, ax = plt.subplots(figsize=(5.6, 6.6))
    ax.set_xlim(0, 56)
    ax.set_ylim(0, 66)
    ax.axis("off")
    ax.add_patch(Rectangle((0, 0), 56, 66, fc="white", ec=NAVY, lw=1.5))
    ax.add_patch(Rectangle((0, 62), 56, 4, fc=FOG, ec=CORNER))
    ax.text(2, 64, "Geoprocessing", fontsize=10, weight="bold", va="center")
    ax.text(2, 59.5, "\u2190   Pairwise Buffer", fontsize=11, weight="bold", va="center")
    ax.text(2, 56.3, "Parameters", fontsize=9, weight="bold", va="center", color=BLUE)
    ax.plot([2, 15], [55, 55], color=BLUE, lw=2)
    ax.text(17, 56.3, "Environments", fontsize=9, va="center", color=BASIN)
    fields = [("Input Features", "rivers", True), ("Output Feature Class", "rivers_PairwiseBuffer", True),
              ("Distance [value or field]", "5        Miles  ⌄", True), ("Method", "Planar  ⌄", False),
              ("Dissolve Type", "Dissolve all output features into a single feature  ⌄", False)]
    y = 51
    for lab, val, req in fields:
        ax.text(2, y, ("* " if req else "") + lab, fontsize=8.5, va="center", color=CLAY if req else NAVY)
        ax.add_patch(Rectangle((2, y - 5), 52, 3.3, fc="white", ec=CORNER))
        ax.text(3, y - 3.35, val, fontsize=8, va="center")
        y -= 8
    ax.add_patch(Rectangle((2, 4), 22, 4.5, fc="#cfe3f3", ec=BLUE))
    ax.text(13, 6.25, "\u25B6  Run", ha="center", va="center", fontsize=10, weight="bold", color=NAVY)
    ax.text(27, 6.25, "\u2713 Completed  (1.9 s)", fontsize=8, va="center", color=PINE)
    for n, (bx, by) in enumerate([(52, 59.5), (52, 51), (52, 43), (52, 35), (52, 27), (52, 6.25)], 1):
        badge(ax, bx, by, n, r=1.7)
    save(fig, OUT / "arcgis-pro" / "arcgis-pro-geoprocessing.png")


arcgis_gp()
