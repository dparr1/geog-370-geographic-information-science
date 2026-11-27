"""Diagrams for the Geocoding and Georeferencing chapter
(images/geocoding-georeferencing/).

Run from the repository root:  python3 scripts/figures/geocoding_georeferencing.py [names]
All streets, parcels, buildings, and control points are made up. The address
interpolation and RMSE examples follow the GEOG 370 lecture.
"""
import sys, os
import numpy as np
sys.path.insert(0, os.path.dirname(__file__))
from style import *  # noqa
import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle, Polygon as MPoly, FancyArrowPatch, FancyBboxPatch, Circle

OUT = "images/geocoding-georeferencing"


def interpolation():
    fig, ax = plt.subplots(figsize=(10.5, 4.0))
    ax.set_xlim(38.5, 55.5); ax.set_ylim(-3.2, 3.4); ax.axis("off")
    ax.plot([42, 52], [0, 0], color=NAVY, lw=13, solid_capstyle="butt")
    for x, lab in [(42, "From node\nX = 42"), (52, "To node\nX = 52")]:
        ax.plot(x, 0, "o", ms=13, mfc="white", mec=NAVY, mew=2.5, zorder=3)
        ax.text(x - 0.45 if x < 47 else x + 0.45, 0, lab, ha="right" if x < 47 else "left", va="center", fontsize=10)
    ax.text(44.2, 0, "Main St", ha="center", va="center", fontsize=10, fontweight="bold", color="white", zorder=4)
    ax.text(42.2, 1.6, "Left side: 1100", ha="left", fontsize=10.5, color=PINE)
    ax.text(51.8, 1.6, "1198", ha="right", fontsize=10.5, color=PINE)
    ax.annotate("", xy=(51.7, 1.35), xytext=(42.3, 1.35), arrowprops=dict(arrowstyle="-|>", color=PINE, lw=1.4))
    ax.text(42.2, -2.15, "Right side: 1101", ha="left", fontsize=10.5, color=CLAY)
    ax.text(51.8, -2.15, "1199", ha="right", fontsize=10.5, color=CLAY)
    ax.annotate("", xy=(51.7, -1.75), xytext=(42.3, -1.75), arrowprops=dict(arrowstyle="-|>", color=CLAY, lw=1.4))
    for k, x in enumerate(np.linspace(42.6, 51.4, 9)):
        ax.add_patch(Rectangle((x - 0.3, 0.55), 0.6, 0.55, fc=SAND, ec=BASIN, lw=0.6))
        ax.add_patch(Rectangle((x - 0.3, -1.45), 0.6, 0.55, fc=SAND, ec=BASIN, lw=0.6))
    xa = 42 + (1147 - 1101) / (1199 - 1101) * 10
    ax.plot(xa, -0.75, marker="v", ms=16, mfc=CLAY, mec=NAVY, zorder=4)
    ax.annotate(f"1147 Main St\nX = 42 + (46 / 98) × 10 = {xa:.1f}", xy=(xa, -0.75), xytext=(xa + 0.2, -2.9),
                ha="center", va="center", fontsize=10.5, fontweight="bold", color=CLAY,
                bbox=dict(boxstyle="round,pad=0.3", fc="white", ec=CLAY, lw=0.8))
    ax.text(39.0, 2.9, "Odd numbers on one side, even on the other; the point is interpolated, not measured.",
            fontsize=10, color=BASIN)
    save(fig, f"{OUT}/interpolation.png")


def reference_files():
    fig, ax = plt.subplots(figsize=(10, 6.2))
    ax.set_xlim(0, 20); ax.set_ylim(0, 12.6); ax.set_aspect("equal"); ax.axis("off")
    # ZIP code area (large polygon)
    zip_poly = [(0.3, 0.3), (19.7, 0.3), (19.7, 11.0), (0.3, 11.0)]
    ax.add_patch(MPoly(zip_poly, fc="#F4F6F7", ec=BASIN, lw=1.2, ls="--"))
    # streets
    for y in (3.0, 8.0):
        ax.plot([0.3, 19.7], [y, y], color=CORNER, lw=9, solid_capstyle="butt", zorder=1)
    for x in (5.0, 12.0, 17.0):
        ax.plot([x, x], [0.3, 11.0], color=CORNER, lw=9, solid_capstyle="butt", zorder=1)
    ax.text(1.0, 8.0, "Elm St", va="center", fontsize=9, color=BASIN, zorder=2)
    ax.text(1.0, 3.0, "Oak St", va="center", fontsize=9, color=BASIN, zorder=2)
    # parcels along Elm St, north side between x=5 and 12
    xs = np.linspace(5.5, 11.5, 6)
    for i in range(5):
        fc = SAND if i != 3 else GINKGO
        ax.add_patch(Rectangle((xs[i], 8.5), xs[i + 1] - xs[i], 2.2, fc=fc, ec=BASIN, lw=0.8, zorder=2))
        ax.add_patch(Rectangle((xs[i] + 0.25, 9.3), xs[i + 1] - xs[i] - 0.5, 0.9, fc="white", ec=BASIN, lw=0.5, zorder=2))
    # target parcel centroid
    pc = ((xs[3] + xs[4]) / 2, 9.6)
    marks = [
        ((xs[3] + xs[4]) / 2, 9.6, "o", PINE, "Parcel centroid"),
        (9.95, 8.35, "s", BLUE, "Street centerline\n(interpolated, offset)"),
        (8.5, 8.0, "D", POPLAR, "ZIP+4 segment center"),
        (10.0, 5.65, "^", CLAY, "5-digit ZIP Code centroid"),
    ]
    for x, y, m, c, lab in marks:
        ax.plot(x, y, marker=m, ms=13, mfc=c, mec=NAVY, mew=1, zorder=5)
    ax.annotate("Parcel centroid:\non the property", xy=marks[0][:2], xytext=(14.2, 10.3), fontsize=9.5,
                color=PINE, fontweight="bold", arrowprops=dict(arrowstyle="-", color=PINE, lw=0.8), zorder=6)
    ax.annotate("Street interpolation:\nalong the centerline", xy=marks[1][:2], xytext=(13.0, 6.3), fontsize=9.5,
                color=BLUE, fontweight="bold", arrowprops=dict(arrowstyle="-", color=BLUE, lw=0.8), zorder=6)
    ax.annotate("ZIP+4: center of\nthe block face", xy=marks[2][:2], xytext=(5.6, 5.2), fontsize=9.5,
                color=POPLAR, fontweight="bold", arrowprops=dict(arrowstyle="-", color=POPLAR, lw=0.8), zorder=6)
    ax.annotate("ZIP Code centroid:\nthe same point for every\naddress in the ZIP Code", xy=marks[3][:2],
                xytext=(13.3, 1.0), fontsize=9.5, color=CLAY, fontweight="bold",
                arrowprops=dict(arrowstyle="-", color=CLAY, lw=0.8), zorder=6)
    ax.text(0.3, 12.2, "One address, four reference files, four different points", fontsize=12,
            fontweight="bold")
    ax.text(0.5, 11.3, "Dashed outline: the ZIP Code area. Gold parcel: the true address.", fontsize=9.5, color=BASIN)
    save(fig, f"{OUT}/reference-files.png")


BUILD = [
    [(8, 10), (22, 10), (22, 24), (8, 24)],
    [(30, 8), (46, 8), (46, 18), (30, 18)],
    [(12, 34), (26, 34), (26, 52), (12, 52)],
    [(34, 30), (52, 30), (52, 40), (43, 40), (43, 50), (34, 50)],
]


def file_to_map():
    fig, axs = plt.subplots(1, 2, figsize=(11, 4.8))
    ax = axs[0]
    for b in BUILD:
        ax.add_patch(MPoly(b, fc=SAND, ec=NAVY, lw=1.2))
    ax.set_xlim(0, 60); ax.set_ylim(60, 0)
    ax.set_xticks(range(0, 61, 10)); ax.set_yticks(range(0, 61, 10))
    ax.set_xlabel("Column (pixels)"); ax.set_ylabel("Row (pixels)")
    ax.set_title("Before: file coordinates", fontsize=12)
    ax.set_aspect("equal"); ax.grid(color=CORNER, lw=0.6)
    ax.xaxis.tick_top(); ax.xaxis.set_label_position("top")
    # after: rotate, scale, translate
    ang = np.radians(-12); s = 8.0
    x0, y0 = 497620, 3761780
    def tr(p):
        c, r = p
        x = s * (c * np.cos(ang) - r * np.sin(ang)) + x0
        y = -s * (c * np.sin(ang) + r * np.cos(ang)) + y0
        return (x, y)
    ax = axs[1]
    for b in BUILD:
        ax.add_patch(MPoly([tr(p) for p in b], fc=SAND, ec=NAVY, lw=1.2))
    ax.set_xlim(497580, 498140); ax.set_ylim(3761280, 3761840)
    ax.set_aspect("equal"); ax.grid(color=CORNER, lw=0.6)
    ax.xaxis.set_major_formatter(plt.FuncFormatter(lambda v, p: f"{v:,.0f}"))
    ax.yaxis.set_major_formatter(plt.FuncFormatter(lambda v, p: f"{v:,.0f}"))
    ax.tick_params(axis="x", labelrotation=30, labelsize=8.5); ax.tick_params(axis="y", labelsize=8.5)
    ax.set_xlabel("Easting (m)"); ax.set_ylabel("Northing (m)")
    ax.set_title("After: map coordinates (UTM)", fontsize=12)
    fig.tight_layout()
    save(fig, f"{OUT}/file-to-map.png")


def affine():
    fig, axs = plt.subplots(1, 5, figsize=(12, 2.9))
    sq = np.array([(0, 0), (1, 0), (1, 1), (0, 1)])
    def T(p, kind):
        x, y = p[:, 0], p[:, 1]
        if kind == "Original":
            return p
        if kind == "Translation":
            return np.c_[x + 0.35, y + 0.25]
        if kind == "Scale":
            return np.c_[x * 1.35, y * 0.75]
        if kind == "Skew":
            return np.c_[x + 0.4 * y, y]
        if kind == "Rotation":
            a = np.radians(25)
            return np.c_[x * np.cos(a) - y * np.sin(a) + 0.2, x * np.sin(a) + y * np.cos(a)]
    for ax, k in zip(axs, ["Original", "Translation", "Scale", "Skew", "Rotation"]):
        ax.set_xlim(-0.5, 1.7); ax.set_ylim(-0.3, 1.5); ax.set_aspect("equal")
        ax.set_xticks([]); ax.set_yticks([])
        for s_ in ax.spines.values():
            s_.set_color(CORNER)
        if k != "Original":
            ax.add_patch(MPoly(sq, fill=False, ec=CORNER, lw=1.2, ls="--"))
        ax.add_patch(MPoly(T(sq.astype(float), k), fc=WATER, ec=PINE, lw=2))
        ax.set_title(k, fontsize=11.5)
    save(fig, f"{OUT}/affine.png")


def residuals():
    rng = np.random.default_rng(10)
    fig, ax = plt.subplots(figsize=(7.4, 5.6))
    pts = np.array([(1.2, 1.9), (8.6, 1.4), (4.8, 4.9), (1.6, 8.3), (8.3, 8.6), (5.2, 1.8)])
    err = np.array([(0.25, 0.10), (-0.18, 0.32), (0.05, -0.08), (-0.30, -0.22), (0.15, -0.05), (0.62, 0.55)])
    est = pts + err
    ax.set_xlim(0, 10); ax.set_ylim(0, 10); ax.set_aspect("equal")
    ax.grid(color=CORNER, lw=0.6)
    for i, (p, e) in enumerate(zip(pts, est)):
        ax.plot(*p, marker="+", ms=16, mew=2.4, color=NAVY, zorder=3)
        ax.plot(*e, marker="o", ms=8, mfc=CLAY, mec="white", zorder=3)
        ax.add_patch(FancyArrowPatch(p, e, arrowstyle="-|>", mutation_scale=10, lw=1.4, color=CLAY, zorder=2))
        r = np.hypot(*(e - p))
        ax.text(p[0] - 0.25, p[1] - 0.45, f"GCP {i + 1}\nresidual {r * 100:.0f} m", fontsize=8.8, ha="center",
                va="top", color=NAVY)
    ax.set_xlabel("Easting (hundreds of meters)"); ax.set_ylabel("Northing (hundreds of meters)")
    from matplotlib.lines import Line2D
    h = [Line2D([], [], marker="+", ls="", color=NAVY, ms=12, mew=2, label="True position (reference map)"),
         Line2D([], [], marker="o", ls="", mfc=CLAY, mec="white", ms=8, label="Where the transformation puts it")]
    ax.legend(handles=h, loc="upper center", bbox_to_anchor=(0.5, -0.12), ncol=2, frameon=False, fontsize=9.5)
    r = np.hypot(err[:, 0], err[:, 1]) * 100
    rmse = np.sqrt(np.mean(r ** 2))
    ax.set_title(f"Residuals at six GCPs; RMSE = {rmse:.0f} m. GCP 6 may be misplaced.", fontsize=11)
    save(fig, f"{OUT}/residuals.png")
    print(r, rmse)


def polynomial():
    rng = np.random.default_rng(4)
    x = np.array([0.5, 1.6, 2.4, 3.3, 4.6, 5.5, 6.7, 7.4, 8.6, 9.5])
    true = lambda t: 2 + 0.2 * t + 0.07 * t ** 2 + 0.7 * np.sin(t / 1.2)
    y = true(x) + rng.normal(0, 0.18, len(x))
    xx = np.linspace(0, 10, 300)
    fig, axs = plt.subplots(1, 3, figsize=(11.5, 3.4), sharey=True)
    for ax, k, ttl in zip(axs, (1, 2, 3), ("1st order: 3+ GCPs", "2nd order: 6+ GCPs", "3rd order: 10+ GCPs")):
        c = np.polyfit(x, y, k)
        ax.plot(xx, true(xx), color=CORNER, lw=6, label="True distortion")
        ax.plot(xx, np.polyval(c, xx), color=PINE, lw=2.2, label="Fitted model")
        ax.plot(x, y, "o", ms=7, mfc=CLAY, mec="white", label="GCPs")
        ax.set_title(ttl, fontsize=11.5)
        ax.set_xticks([]); ax.set_yticks([])
        for s in ("top", "right"):
            ax.spines[s].set_visible(False)
    axs[0].legend(frameon=False, fontsize=9, loc="upper left")
    save(fig, f"{OUT}/polynomial-orders.png")


FUNCS = dict(interpolation=interpolation, reference=reference_files, file_to_map=file_to_map, affine=affine,
             residuals=residuals, polynomial=polynomial)

if __name__ == "__main__":
    os.makedirs(OUT, exist_ok=True)
    for n in (sys.argv[1:] or list(FUNCS)):
        FUNCS[n]()
