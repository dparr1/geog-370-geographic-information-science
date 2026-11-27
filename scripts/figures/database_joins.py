"""Diagrams for the Database Joins chapter (images/database-joins/).

Run from the repository root:  python3 scripts/figures/database_joins.py [names]
The forest and trail tables use real North Carolina national forests and
trails; acreages are rounded. The student tables follow the GEOG 370 lecture.
"""
import sys, os
sys.path.insert(0, os.path.dirname(__file__))
from style import *  # noqa
import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle, Circle, FancyBboxPatch, FancyArrowPatch

OUT = "images/database-joins"


def draw_table(ax, x0, y0, cols, rows, widths, title=None, rowh=0.55, fs=10,
               hi=None, keycol=None, keyfc=SAND, head=PINE, nullgrey=True, colfc=None):
    """Draw a table with its top-left at (x0, y0). Returns row centre y values."""
    if title:
        ax.text(x0, y0 + 0.18, title, fontsize=fs + 1.5, fontweight="bold", va="bottom")
    x = x0
    for j, c in enumerate(cols):
        fc = head
        if colfc and j in colfc:
            fc = colfc[j]
        ax.add_patch(Rectangle((x, y0 - rowh), widths[j], rowh, fc=fc, ec=NAVY, lw=0.8))
        ax.text(x + widths[j] / 2, y0 - rowh / 2, c, ha="center", va="center",
                color="white", fontweight="bold", fontsize=fs)
        x += widths[j]
    ys = []
    for i, r in enumerate(rows):
        y = y0 - (i + 2) * rowh
        ys.append(y + rowh / 2)
        x = x0
        for j, v in enumerate(r):
            fc = "white"
            if keycol is not None and j == keycol:
                fc = keyfc
            if hi and i in hi:
                fc = hi[i]
            ax.add_patch(Rectangle((x, y), widths[j], rowh, fc=fc, ec=NAVY, lw=0.6))
            txt = str(v)
            isnull = txt == "NULL"
            ax.text(x + widths[j] / 2, y + rowh / 2, txt, ha="center", va="center", fontsize=fs,
                    color=CLAY if (isnull and nullgrey) else NAVY,
                    style="italic" if isnull else "normal",
                    fontweight="bold" if isnull else "normal")
            x += widths[j]
    return ys


FORESTS = [
    ("Nantahala", "Franklin", "531,000", 1),
    ("Pisgah", "Pisgah Forest", "512,000", 2),
    ("Uwharrie", "Troy", "51,000", 3),
    ("Croatan", "New Bern", "160,000", 4),
]
TRAILS = [
    (1, "Bartram Trail"),
    (1, "Joyce Kilmer Loop"),
    (2, "Art Loeb Trail"),
    (2, "Shut-In Trail"),
    (3, "Uwharrie Trail"),
    (4, "Neusiok Trail"),
]


def relational():
    fig, ax = plt.subplots(figsize=(10, 4.4))
    ax.set_xlim(0, 10.4); ax.set_ylim(-0.75, 4.5); ax.axis("off")
    fw = [1.45, 1.5, 1.15, 1.1]
    ys_f = draw_table(ax, 0.1, 4.0, ["Name", "Ranger office", "Acres", "Forest_ID"],
                      FORESTS, fw, title="Forests", keycol=3)
    tw = [1.1, 2.0]
    ys_t = draw_table(ax, 7.2, 4.0, ["Forest_ID", "Trail"], TRAILS, tw, title="Trails", keycol=0)
    xf = 0.1 + sum(fw)
    xt = 7.2
    cols = [PINE, CLAY, DUSK, POPLAR]
    for (fid, name), yt in zip(TRAILS, ys_t):
        yf = ys_f[fid - 1]
        ax.add_patch(FancyArrowPatch((xt - 0.03, yt), (xf + 0.03, yf), arrowstyle="-|>",
                                     mutation_scale=11, lw=1.4, color=cols[fid - 1]))
    ax.text(xf - fw[3] / 2, 1.05, "Primary key:\none value per forest,\nnever repeated",
            ha="center", va="top", fontsize=9.5, color=PINE, fontweight="bold")
    ax.text(xt + tw[0] / 2, -0.2, "Foreign key: points back to\nForests; values can repeat",
            ha="center", va="top", fontsize=9.5, color=PINE, fontweight="bold")
    save(fig, f"{OUT}/relational-tables.png")


def joined():
    fig, ax = plt.subplots(figsize=(10, 4.1))
    ax.set_xlim(0, 10); ax.set_ylim(-0.3, 4.2); ax.axis("off")
    rows = []
    for fid, name in TRAILS:
        f = FORESTS[fid - 1]
        rows.append((fid, name, f[0], f[1], f[2], f[3]))
    w = [1.1, 2.0, 1.45, 1.6, 1.0, 1.1]
    colfc = {2: DUSK, 3: DUSK, 4: DUSK, 5: DUSK}
    draw_table(ax, 0.6, 3.7, ["Forest_ID", "Trail", "Name", "Ranger office", "Acres", "Forest_ID"],
               rows, w, colfc=colfc)
    ax.annotate("", xy=(0.6, 3.82), xytext=(0.6 + w[0] + w[1], 3.82),
                arrowprops=dict(arrowstyle="-", color=PINE, lw=2))
    ax.text(0.6 + (w[0] + w[1]) / 2, 3.88, "Destination: Trails (kept as is)", ha="center",
            va="bottom", fontsize=10, color=PINE, fontweight="bold")
    x2 = 0.6 + w[0] + w[1]
    ax.annotate("", xy=(x2, 3.82), xytext=(x2 + sum(w[2:]), 3.82),
                arrowprops=dict(arrowstyle="-", color=DUSK, lw=2))
    ax.text(x2 + sum(w[2:]) / 2, 3.88, "Appended from the source: Forests", ha="center",
            va="bottom", fontsize=10, color=DUSK, fontweight="bold")
    save(fig, f"{OUT}/joined-table.png")


def venn():
    fig, axs = plt.subplots(1, 4, figsize=(11, 3.1))
    titles = ["Inner join", "Left join", "Right join", "Full outer join"]
    keep = [("mid",), ("L", "mid"), ("mid", "R"), ("L", "mid", "R")]
    notes = ["Only rows that match\nin both tables", "Every row of the left\n(destination) table",
             "Every row of the right\n(source) table", "Every row of\nboth tables"]
    import numpy as np
    from matplotlib.path import Path
    from matplotlib.patches import PathPatch
    t = np.linspace(0, 2 * np.pi, 400)
    r = 1.0
    cl, cr = (-0.55, 0), (0.55, 0)
    for ax, ti, k, n in zip(axs, titles, keep, notes):
        ax.set_xlim(-1.8, 1.8); ax.set_ylim(-1.9, 1.5); ax.set_aspect("equal"); ax.axis("off")
        # grid sample to shade regions
        xs, ys = np.meshgrid(np.linspace(-1.6, 1.6, 500), np.linspace(-1.1, 1.1, 300))
        inL = (xs - cl[0]) ** 2 + ys ** 2 <= r * r
        inR = (xs - cr[0]) ** 2 + ys ** 2 <= r * r
        m = np.zeros_like(xs, dtype=bool)
        if "L" in k: m |= inL & ~inR
        if "R" in k: m |= inR & ~inL
        if "mid" in k: m |= inL & inR
        ax.contourf(xs, ys, m.astype(float), levels=[0.5, 1.5], colors=[PINE], alpha=0.85)
        for c in (cl, cr):
            ax.add_patch(Circle(c, r, fill=False, ec=NAVY, lw=1.6))
        ax.text(cl[0] - 0.35, 0, "Left", ha="center", va="center", fontsize=9.5,
                color="white" if "L" in k else NAVY, fontweight="bold")
        ax.text(cr[0] + 0.35, 0, "Right", ha="center", va="center", fontsize=9.5,
                color="white" if "R" in k else NAVY, fontweight="bold")
        ax.set_title(ti, fontsize=12.5)
        ax.text(0, -1.25, n, ha="center", va="top", fontsize=9.5)
    save(fig, f"{OUT}/join-types-venn.png")


def cardinality():
    fig, axs = plt.subplots(1, 4, figsize=(12, 3.9))
    cases = [
        ("One-to-one", ["NC", "SC", "VA"], ["Gov. of NC", "Gov. of SC", "Gov. of VA"],
         [(0, 0), (1, 1), (2, 2)], "Simple join works"),
        ("Many-to-one", ["Durham Co.", "Orange Co.", "Wake Co.", "Horry Co."], ["NC", "SC"],
         [(0, 0), (1, 0), (2, 0), (3, 1)], "Simple join works"),
        ("One-to-many", ["NC", "SC"], ["Durham Co.", "Orange Co.", "Wake Co.", "Horry Co."],
         [(0, 0), (0, 1), (0, 2), (1, 3)], "Summarize the source\nfirst, or use a relate"),
        ("Many-to-many", ["Zhang", "Shankar", "Parr"], ["GEOG 370", "GEOG 215", "CS 101"],
         [(0, 0), (0, 2), (1, 0), (1, 1), (2, 1), (2, 2)], "Needs a linking table"),
    ]
    for ax, (ti, left, right, links, note) in zip(axs, cases):
        ax.set_xlim(0, 4); ax.set_ylim(-1.2, 4.4); ax.axis("off")
        ax.set_title(ti, fontsize=12.5)
        def ypos(n, i):
            top, bot = 3.7, 0.3
            if n == 1:
                return (top + bot) / 2
            return top - i * (top - bot) / (n - 1) if n > 2 else [2.9, 1.1][i]
        ok = note.startswith("Simple")
        for i, s in enumerate(left):
            y = ypos(len(left), i)
            ax.add_patch(FancyBboxPatch((0.05, y - 0.28), 1.45, 0.56, boxstyle="round,pad=0.02",
                                        fc=SAND, ec=NAVY, lw=0.8))
            ax.text(0.775, y, s, ha="center", va="center", fontsize=9)
        for i, s in enumerate(right):
            y = ypos(len(right), i)
            ax.add_patch(FancyBboxPatch((2.45, y - 0.28), 1.5, 0.56, boxstyle="round,pad=0.02",
                                        fc=DOGWOOD, ec=NAVY, lw=0.8))
            ax.text(3.2, y, s, ha="center", va="center", fontsize=8.6 if len(s) > 12 else 9)
        for a, b in links:
            ax.plot([1.55, 2.4], [ypos(len(left), a), ypos(len(right), b)], color=NAVY, lw=1.2)
        ax.text(0.775, 4.05, "Destination", ha="center", fontsize=9, color=BASIN)
        ax.text(3.2, 4.05, "Source", ha="center", fontsize=9, color=BASIN)
        ax.text(2.0, -0.35, note, ha="center", va="top", fontsize=9.5, fontweight="bold",
                color=PINE if ok else CLAY)
    save(fig, f"{OUT}/cardinality.png")


def one_to_many():
    fig, ax = plt.subplots(figsize=(10, 3.6))
    ax.set_xlim(0, 10); ax.set_ylim(-0.6, 3.9); ax.axis("off")
    ys_d = draw_table(ax, 0.2, 3.4, ["STATE", "Pop_2020"],
                      [("NC", "10,439,388"), ("SC", "5,118,425"), ("VA", "8,631,393")],
                      [0.9, 1.4], title="States (destination)", keycol=0)
    rows = [("Durham", "NC", "324,833"), ("Orange", "NC", "148,696"), ("Wake", "NC", "1,129,410"),
            ("Horry", "SC", "351,029"), ("Fairfax", "VA", "1,150,309")]
    ys_s = draw_table(ax, 6.0, 3.4, ["County", "STATE", "Pop_2020"], rows, [1.1, 0.9, 1.3],
                      title="Counties (source)", keycol=1)
    for i, (c, st, p) in enumerate(rows):
        d = ["NC", "SC", "VA"].index(st)
        ax.add_patch(FancyArrowPatch((6.0, ys_s[i]), (0.2 + 2.3, ys_d[d]),
                                     arrowstyle="-|>", mutation_scale=10, lw=1.2,
                                     color=CLAY if st == "NC" else BASIN))
    ax.text(4.1, 3.0, "?", fontsize=34, color=CLAY, fontweight="bold", ha="center", va="center")
    ax.text(4.8, -0.35, "NC matches three counties. Which county's values belong in NC's row?",
            ha="center", fontsize=10.5, color=CLAY)
    save(fig, f"{OUT}/one-to-many.png")


def architecture():
    fig, axs = plt.subplots(1, 2, figsize=(11, 4.4), gridspec_kw=dict(width_ratios=[1, 1]))
    for ax in axs:
        ax.set_xlim(0, 10); ax.set_ylim(0, 8); ax.axis("off")
    # left: direct file access
    ax = axs[0]
    ax.set_title("Without a DBMS: each program reads its own files", fontsize=12)
    progs = ["Mapping app", "Permit office app", "Report script"]
    files = [["roads.dbf", "parcels.dbf"], ["parcels_copy.xls"], ["parcels_2019.csv", "roads.dbf"]]
    for i, (p, fs) in enumerate(zip(progs, files)):
        y = 6.6 - i * 2.4
        ax.add_patch(FancyBboxPatch((5.6, y - 0.45), 3.9, 0.9, boxstyle="round,pad=0.05", fc=DOGWOOD, ec=NAVY))
        ax.text(7.55, y, p, ha="center", va="center", fontsize=10)
        for k, f in enumerate(fs):
            yy = y + 0.45 - k * 0.95
            ax.add_patch(Rectangle((0.3, yy - 0.38), 3.2, 0.76, fc=SAND, ec=NAVY, lw=0.8))
            ax.text(1.9, yy, f, ha="center", va="center", fontsize=9.5)
            ax.annotate("", xy=(5.55, y), xytext=(3.55, yy), arrowprops=dict(arrowstyle="-|>", color=NAVY, lw=1))
    ax.text(5, 0.1, "Copies drift apart; no one controls who edits what.", ha="center", fontsize=9.5, color=CLAY)
    # right: three tier
    ax = axs[1]
    ax.set_title("With a DBMS: three tiers", fontsize=12)
    tiers = [(6.6, "Client tier", "web browser, QGIS, ArcGIS Pro", DOGWOOD),
             (4.1, "Application tier", "web server, map server", WATER),
             (1.6, "Database tier", "DBMS (e.g., PostgreSQL + PostGIS)", SAND)]
    for y, t, s, c in tiers:
        ax.add_patch(FancyBboxPatch((1.0, y - 0.75), 8.0, 1.5, boxstyle="round,pad=0.05", fc=c, ec=NAVY))
        ax.text(5, y + 0.25, t, ha="center", va="center", fontsize=11, fontweight="bold")
        ax.text(5, y - 0.3, s, ha="center", va="center", fontsize=9.5)
    for y in (5.85, 3.35):
        ax.annotate("", xy=(5, y - 0.95), xytext=(5, y - 0.05), arrowprops=dict(arrowstyle="<|-|>", color=NAVY, lw=1.6, mutation_scale=14))
    ax.text(5, 0.1, "One stored copy; the DBMS checks every request.", ha="center", fontsize=9.5, color=PINE)
    save(fig, f"{OUT}/dbms-architecture.png")


def census_workflow():
    fig, ax = plt.subplots(figsize=(11, 3.2))
    ax.set_xlim(0, 11); ax.set_ylim(0.6, 4.2); ax.axis("off")
    draw_table(ax, 0.1, 3.9, ["GEOID", "NAMELSAD", "geometry"],
               [("37135010701", "Tract 107.01", "polygon"), ("37135010702", "Tract 107.02", "polygon"),
                ("37135011200", "Tract 112", "polygon")], [1.35, 1.2, 0.9], fs=9,
               title="Tract layer (destination)", keycol=0)
    draw_table(ax, 4.0, 3.9, ["GEOID", "POP"], [("37135010701", "4,812"), ("37135011200", "3,205"),
                                               ("37135010702", "5,147")], [1.35, 0.8], fs=9,
               title="Population CSV (source)", keycol=0)
    draw_table(ax, 6.8, 3.9, ["GEOID", "NAMELSAD", "geometry", "POP"],
               [("37135010701", "Tract 107.01", "polygon", "4,812"),
                ("37135010702", "Tract 107.02", "polygon", "5,147"),
                ("37135011200", "Tract 112", "polygon", "3,205")], [1.35, 1.2, 0.9, 0.7], fs=9,
               title="Joined layer", keycol=0, colfc={3: DUSK})
    ax.text(3.7, 2.8, "+", fontsize=26, ha="center", va="center", fontweight="bold")
    ax.annotate("", xy=(6.7, 2.75), xytext=(6.25, 2.75), arrowprops=dict(arrowstyle="-|>", lw=2, color=NAVY))
    ax.text(5.5, 1.05, "Match on GEOID: both fields are text, 11 characters, leading zeros kept.\n"
            "The rows can be in any order; the join matches on values, not on position.",
            ha="center", va="center", fontsize=10, color=PINE)
    save(fig, f"{OUT}/census-join.png")


def leading_zero():
    fig, ax = plt.subplots(figsize=(9, 2.9))
    ax.set_xlim(0, 9); ax.set_ylim(0, 3.1); ax.axis("off")
    draw_table(ax, 0.2, 2.8, ["GEOID (text)"], [("06001400100",), ("06001400200",), ("06001400300",)],
               [1.9], fs=10, title="Tracts", keycol=0)
    draw_table(ax, 3.6, 2.8, ["GEOID (number)"], [("6001400100",), ("6001400200",), ("6001400300",)],
               [1.9], fs=10, title="CSV opened as numbers", keycol=0, keyfc="#F8D3D1")
    draw_table(ax, 7.0, 2.8, ["POP"], [("NULL",), ("NULL",), ("NULL",)], [1.2], fs=10, title="Join result")
    ax.text(4.55, 0.15, "The leading zero of California's state code (06) was dropped, so no key matches.",
            ha="center", fontsize=10, color=CLAY)
    save(fig, f"{OUT}/leading-zero.png")


FUNCS = dict(relational=relational, joined=joined, venn=venn, cardinality=cardinality,
             one_to_many=one_to_many, architecture=architecture, census=census_workflow,
             leading_zero=leading_zero)

if __name__ == "__main__":
    os.makedirs(OUT, exist_ok=True)
    names = sys.argv[1:] or list(FUNCS)
    for n in names:
        FUNCS[n]()
