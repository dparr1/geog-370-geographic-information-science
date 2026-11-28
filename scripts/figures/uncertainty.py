"""Figures for Chapter 12, Uncertainty in Geospatial Data.

Usage: python uncertainty.py

Every map, point, and value here is made up for illustration.
"""
from pathlib import Path

import numpy as np
from matplotlib.patches import (Circle, Rectangle, Polygon as MPoly, FancyBboxPatch,
                                RegularPolygon)
from matplotlib.colors import to_rgb
from scipy import ndimage

from style import (plt, save, NAVY, PINE, BLUE, BASIN, CORNER, FOG, CLAY, POPLAR,
                   GINKGO, SAND, DOGWOOD, BERRY, DUSK, LAND, WATER)

OUT = Path(__file__).resolve().parents[2] / "images" / "uncertainty"
OUT.mkdir(parents=True, exist_ok=True)
rng = np.random.default_rng(22)


def off(ax):
    ax.set_aspect("equal"); ax.axis("off")


# ---------------------------------------------------------------- cloud
def cloud():
    fig, ax = plt.subplots(figsize=(7.5, 5))
    pts = rng.normal(0, 1, (700, 2)) * [1.0, 0.7]
    d = np.hypot(pts[:, 0], pts[:, 1] / 0.7)
    ax.scatter(pts[:, 0], pts[:, 1], s=9, c=BLUE, alpha=np.clip(1.1 - d / 3, 0.08, 0.9), lw=0)
    for k, a in [(1, 0.9), (2, 0.6)]:
        t = np.linspace(0, 2 * np.pi, 200)
        ax.plot(k * np.cos(t), k * 0.7 * np.sin(t), color=NAVY, lw=1, ls="--", alpha=a)
    ax.scatter([0], [0], s=160, c=CLAY, ec=NAVY, zorder=5, marker="o")
    ax.annotate("Recorded value\n(our best estimate)", xy=(0, 0), xytext=(-3.3, 1.7),
                fontsize=10.5, weight="bold", color=CLAY,
                arrowprops=dict(arrowstyle="-|>", color=CLAY, lw=1.3))
    tx, ty = 1.1, -0.55
    ax.scatter([tx], [ty], s=120, marker="*", c=GINKGO, ec=NAVY, zorder=6)
    ax.annotate("", xy=(tx, ty), xytext=(0, 0),
                arrowprops=dict(arrowstyle="-|>", color=NAVY, lw=1.2, ls=":"))
    ax.annotate("The true value is in here\nsomewhere, but we can't see it.\nThe gap is the error.",
                xy=(tx, ty), xytext=(1.7, -2.1), fontsize=9.5,
                arrowprops=dict(arrowstyle="-", color=BASIN, lw=0.8))
    ax.text(2.2, 1.55, "Uncertainty describes\nthe whole cloud:\nhow wide it is and\nhow it is spread", fontsize=9.5,
            color=BLUE, weight="bold")
    ax.set_xlim(-3.6, 4.1); ax.set_ylim(-2.6, 2.4); off(ax)
    save(fig, OUT / "cloud.png")


# ---------------------------------------------------------------- RMSE
def rmse():
    true = np.array([[1, 1], [3, 1.4], [5.2, 0.8], [1.6, 3.2], [3.8, 3.6], [5.6, 3.0], [2.2, 5.2], [4.8, 5.4]])
    dm = np.array([3, 4, 5, 2, 4, 3, 5, 2], float)  # offsets in meters
    ang = np.radians([30, 120, 340, 290, 210, 50, 140, 15])
    offs = np.c_[np.cos(ang), np.sin(ang)] * dm[:, None] / 10  # map units: 10 m each
    mapped = true + offs
    d = np.hypot(*offs.T) * 10  # meters
    r = np.sqrt((d ** 2).mean())
    fig, (ax, tx) = plt.subplots(1, 2, figsize=(10.5, 4.6), gridspec_kw=dict(width_ratios=[1.15, 1]))
    ax.add_patch(Rectangle((0, 0), 6.6, 6.4, fc=FOG, ec="none"))
    for (x0, y0), (x1, y1), di, i in zip(true, mapped, d, range(1, 9)):
        ax.annotate("", xy=(x1, y1), xytext=(x0, y0),
                    arrowprops=dict(arrowstyle="-|>", color=CLAY, lw=1.3, shrinkA=3, shrinkB=3))
        ax.scatter([x0], [y0], s=55, marker="^", c=PINE, ec=NAVY, zorder=4)
        ax.scatter([x1], [y1], s=40, c=CLAY, ec=NAVY, zorder=4)
        ax.text(x0 - 0.12, y0 - 0.28, str(i), fontsize=8.5, ha="right", color=NAVY)
    ax.scatter([], [], marker="^", c=PINE, ec=NAVY, label="True position (survey)")
    ax.scatter([], [], c=CLAY, ec=NAVY, label="Position on the map")
    ax.legend(loc="upper center", bbox_to_anchor=(0.5, -0.01), ncol=2, fontsize=9, frameon=False)
    ax.set_xlim(-0.1, 6.7); ax.set_ylim(-0.1, 6.5); off(ax)
    ax.text(0.2, 6.2, "Offsets exaggerated for clarity", fontsize=8.5, color=BASIN)
    tx.axis("off")
    rows = [["Point", "Offset d (m)", "d²"]] + [[str(i + 1), f"{v:.0f}", f"{v * v:.0f}"] for i, v in enumerate(d)]
    tb = tx.table(cellText=rows[1:], colLabels=rows[0], loc="upper center", cellLoc="center",
                  colWidths=[0.22, 0.3, 0.25])
    tb.auto_set_font_size(False); tb.set_fontsize(9.5); tb.scale(1, 1.25)
    for (rr, cc), cell in tb.get_celld().items():
        cell.set_edgecolor(CORNER)
        if rr == 0:
            cell.set_facecolor(NAVY); cell.get_text().set_color("white"); cell.get_text().set_weight("bold")
    tx.text(0.5, 0.06, f"Sum of d² = {(d ** 2).sum():.0f}   n = 8\n"
                       f"RMSE = √({(d ** 2).sum():.0f} / 8) = √{(d ** 2).mean():.1f} = {r:.1f} m",
            ha="center", fontsize=11, weight="bold", transform=tx.transAxes)
    print("RMSE", r, d.round(1), (d ** 2).round(1), (d ** 2).sum())
    save(fig, OUT / "rmse.png")


# ---------------------------------------------------------------- road classes
def roads():
    fig, axs = plt.subplots(1, 2, figsize=(10, 4.4))
    styles = {"Interstate": (CLAY, 6), "Ramp": (POPLAR, 3), "Local road": (BASIN, 2.2)}
    hw = np.array([[0, 2], [10, 2]])
    ramp1 = np.array([[3, 2], [4.2, 3.0], [5, 3.6]])
    ramp2 = np.array([[5, 3.6], [5.8, 3.0], [7, 2]])
    local = np.array([[5, 0], [5, 6]])
    segs_bad = [(np.array([[0, 2], [2.5, 2]]), "Interstate"), (np.array([[2.5, 2], [4.5, 2]]), "Ramp"),
                (np.array([[4.5, 2], [6.5, 2]]), "Interstate"), (np.array([[6.5, 2], [8, 2]]), "Local road"),
                (np.array([[8, 2], [10, 2]]), "Interstate"),
                (np.array([[5, 0], [5, 2.6]]), "Local road"), (np.array([[5, 2.6], [5, 4.2]]), "Ramp"),
                (np.array([[5, 4.2], [5, 6]]), "Local road"),
                (ramp1, "Ramp"), (ramp2, "Interstate")]
    segs_good = [(hw, "Interstate"), (local, "Local road"), (ramp1, "Ramp"), (ramp2, "Ramp")]
    for ax, segs, title in [(axs[0], segs_bad, "Inconsistent: classes change along one road"),
                            (axs[1], segs_good, "Consistent: each road keeps one class")]:
        ax.add_patch(Rectangle((0, 0), 10, 6, fc="#F5F3EA", ec="none"))
        for xy, cls in segs:
            c, w = styles[cls]
            ax.plot(*xy.T, color=c, lw=w, solid_capstyle="butt", zorder=3 if cls != "Interstate" else 2)
        ax.set_title(title, fontsize=11)
        ax.set_xlim(0, 10); ax.set_ylim(0, 6); off(ax)
    for name, (c, w) in styles.items():
        axs[1].plot([], [], color=c, lw=w, label=name)
    fig.legend(loc="lower center", ncol=3, frameon=False, fontsize=9.5)
    fig.tight_layout(rect=(0, 0.07, 1, 1))
    save(fig, OUT / "road-consistency.png")


# ---------------------------------------------------------------- topology errors
def topology():
    fig, axs = plt.subplots(1, 4, figsize=(11, 3.2))
    # Undershoot
    ax = axs[0]
    ax.plot([0, 4], [2, 2], color=NAVY, lw=2.2)
    ax.plot([2, 2], [0, 1.65], color=NAVY, lw=2.2)
    ax.add_patch(Circle((2, 1.82), 0.32, fill=False, ec=CLAY, lw=1.6))
    ax.set_title("Undershoot:\nline stops short")
    # Overshoot
    ax = axs[1]
    ax.plot([0, 4], [2, 2], color=NAVY, lw=2.2)
    ax.plot([2, 2], [0, 2.45], color=NAVY, lw=2.2)
    ax.add_patch(Circle((2, 2.22), 0.36, fill=False, ec=CLAY, lw=1.6))
    ax.set_title("Overshoot:\nline runs past")
    # Gap
    ax = axs[2]
    ax.add_patch(MPoly([(0.3, 0.3), (1.95, 0.3), (1.8, 3.4), (0.3, 3.4)], fc=DOGWOOD, ec=NAVY, lw=1.4))
    ax.add_patch(MPoly([(2.15, 0.3), (3.7, 0.3), (3.7, 3.4), (2.05, 3.4)], fc=SAND, ec=NAVY, lw=1.4))
    ax.add_patch(Circle((2.0, 1.9), 0.45, fill=False, ec=CLAY, lw=1.6))
    ax.set_title("Gap between\nneighbors")
    # Overlap
    ax = axs[3]
    ax.add_patch(MPoly([(0.3, 0.3), (2.3, 0.3), (2.3, 3.4), (0.3, 3.4)], fc=DOGWOOD, ec=NAVY, lw=1.4, alpha=0.85))
    ax.add_patch(MPoly([(1.8, 0.3), (3.7, 0.3), (3.7, 3.4), (1.8, 3.4)], fc=SAND, ec=NAVY, lw=1.4, alpha=0.85))
    ax.add_patch(Rectangle((1.8, 0.3), 0.5, 3.1, fc=CLAY, alpha=0.45, ec="none"))
    ax.set_title("Overlap between\nneighbors")
    for ax in axs:
        ax.set_xlim(-0.1, 4.1); ax.set_ylim(-0.1, 3.7); off(ax)
        ax.title.set_fontsize(10.5)
    fig.tight_layout()
    save(fig, OUT / "topology-errors.png")


# ---------------------------------------------------------------- lifecycle
def lifecycle():
    stages = [("Collection", "Instrument limits\nand malfunctions\nMissing data", BLUE),
              ("Processing", "Projection\nGeneralization\nEstimation, prediction", PINE),
              ("Storage", "Misclassified\nattributes\nBroken data links", DUSK),
              ("Display", "Abstraction\nSymbolization\nClassing", BERRY),
              ("Use", "Misreading patterns:\nType 1 and\nType 2 errors", CLAY)]
    fig, ax = plt.subplots(figsize=(11, 3.4))
    ax.set_xlim(0, 11); ax.set_ylim(0, 3.4); ax.axis("off")
    for i, (name, sub, c) in enumerate(stages):
        x = 1.1 + i * 2.2
        ax.add_patch(FancyBboxPatch((x - 0.95, 2.2), 1.9, 0.8, boxstyle="round,pad=0,rounding_size=0.15",
                                    fc=c, ec="none"))
        ax.text(x, 2.6, name, ha="center", va="center", color="white", weight="bold", fontsize=11.5)
        ax.text(x, 1.95, sub, ha="center", va="top", fontsize=9, color=NAVY, linespacing=1.3)
        if i < 4:
            ax.annotate("", xy=(x + 1.27, 2.6), xytext=(x + 0.97, 2.6),
                        arrowprops=dict(arrowstyle="-|>", color=NAVY, lw=1.4))
    save(fig, OUT / "lifecycle.png")


# ---------------------------------------------------------------- visual variables
def blob(ax, x, y, r, **kw):
    t = np.linspace(0, 2 * np.pi, 9)[:-1]
    rr = r * (1 + 0.18 * np.sin(3 * t + 0.7))
    ax.add_patch(MPoly(np.c_[x + rr * np.cos(t), y + rr * np.sin(t)], closed=True, **kw))


def visual_variables():
    fig, axs = plt.subplots(1, 4, figsize=(11.5, 3.6))
    # Crispness: draw a blurred raster for the uncertain one
    n = 200
    yy, xx = np.mgrid[0:n, 0:n] / n
    for ax, title, note in zip(axs, ["Crispness", "Transparency", "Saturation", "Added symbols"],
                               ["sharp vs. blurred edges", "solid vs. faded", "rich vs. washed-out color",
                                "glyphs, error bars, labels"]):
        ax.set_title(title, fontsize=12, pad=20)
        ax.text(0.5, -0.12, note, ha="center", fontsize=9, color=BASIN, transform=ax.transAxes)
        ax.text(0.27, 1.0, "Certain", ha="center", fontsize=9, transform=ax.transAxes, color=NAVY)
        ax.text(0.75, 1.0, "Uncertain", ha="center", fontsize=9, transform=ax.transAxes, color=NAVY)
        ax.set_xlim(0, 2); ax.set_ylim(0, 1.1); off(ax)
    # Crispness
    disk = ((xx - 0.5) ** 2 + (yy - 0.5) ** 2) < 0.12
    sharp = disk.astype(float)
    soft = ndimage.gaussian_filter(sharp, 14)
    rgb = np.array(to_rgb(PINE))
    for img, x0 in [(sharp, 0.05), (soft, 1.0)]:
        rgba = np.zeros((n, n, 4)); rgba[..., :3] = rgb; rgba[..., 3] = img
        axs[0].imshow(rgba, extent=(x0, x0 + 0.95, 0.05, 1.0), origin="lower")
    # Transparency
    axs[1].add_patch(Circle((0.5, 0.52), 0.36, fc=PINE, alpha=1.0))
    axs[1].add_patch(Circle((1.5, 0.52), 0.36, fc=PINE, alpha=0.3))
    # Saturation: same hue, less saturated
    import colorsys
    h, l, s = colorsys.rgb_to_hls(*to_rgb(PINE))
    axs[2].add_patch(Circle((0.5, 0.52), 0.36, fc=PINE))
    axs[2].add_patch(Circle((1.5, 0.52), 0.36, fc=colorsys.hls_to_rgb(h, min(l + 0.38, 0.85), s * 0.25)))
    # Added symbols
    axs[3].add_patch(Circle((0.5, 0.52), 0.36, fc=PINE))
    axs[3].add_patch(Circle((1.5, 0.52), 0.36, fc=PINE))
    axs[3].text(1.5, 0.5, "?", ha="center", va="center", fontsize=26, color="white", weight="bold")
    axs[3].errorbar([1.5], [0.52], xerr=[0.46], color=NAVY, capsize=4, lw=1.2)
    fig.tight_layout()
    save(fig, OUT / "visual-variables.png")


# ---------------------------------------------------------------- location circle
def location_circle():
    fig, axs = plt.subplots(1, 2, figsize=(9.5, 4.6))
    for ax, r, title in [(axs[0], 0.45, "Outdoors, strong GPS signal"),
                         (axs[1], 1.9, "Indoors or between tall buildings")]:
        ax.add_patch(Rectangle((0, 0), 8, 6, fc="#F2EFE6", ec="none"))
        for i in range(0, 9, 2):
            ax.add_patch(Rectangle((i - 0.15, 0), 0.3, 6, fc="white", ec=CORNER, lw=0.6))
        for j in range(0, 7, 2):
            ax.add_patch(Rectangle((0, j - 0.15), 8, 0.3, fc="white", ec=CORNER, lw=0.6))
        ax.add_patch(Rectangle((2.3, 2.3), 1.4, 1.4, fc=DOGWOOD, ec="none"))
        ax.add_patch(Circle((4.4, 3.3), r, fc=BLUE, alpha=0.22, ec=BLUE, lw=1))
        ax.add_patch(Circle((4.4, 3.3), 0.17, fc="#1A73E8", ec="white", lw=2.2, zorder=4))
        ax.set_title(title, fontsize=11)
        ax.set_xlim(0, 8); ax.set_ylim(0, 6); off(ax)
    axs[1].annotate("accuracy radius:\nabout a 2-in-3 chance\nyou are inside", xy=(4.4 + 1.9 * 0.7, 3.3 - 1.9 * 0.7),
                    xytext=(6.3, 0.45), fontsize=8.5, ha="center",
                    bbox=dict(fc="white", ec=CORNER, pad=2),
                    arrowprops=dict(arrowstyle="-", color=NAVY, lw=0.8))
    fig.tight_layout()
    save(fig, OUT / "location-circle.png")


# ---------------------------------------------------------------- abstraction
def abstraction():
    fig, axs = plt.subplots(1, 3, figsize=(11, 3.9))
    r = np.random.default_rng(5)
    # 1. "Photo": detailed block
    ax = axs[0]
    ax.add_patch(Rectangle((0, 0), 10, 10, fc="#B9B4A5"))
    ax.add_patch(Rectangle((0.6, 0.6), 8.8, 8.8, fc="#D9D4C3", ec="none"))
    for (x, y, w, h, c) in [(1, 1, 3, 2.5, "#8E8A80"), (4.6, 1, 2.2, 3.4, "#A0938A"), (7.2, 1, 1.9, 2.4, "#7C7A74"),
                            (1, 6, 2.2, 3.1, "#958F83"), (6.2, 6.5, 2.9, 2.5, "#8B8378"), (3.8, 7.2, 1.8, 1.9, "#A69C8E")]:
        ax.add_patch(Rectangle((x, y), w, h, fc=c, ec="#5E5A52", lw=0.6))
    for _ in range(26):
        x, y = r.uniform(1, 9, 2)
        if 3.5 < y < 5.8 or r.random() < 0.3:
            ax.add_patch(Circle((x, y), r.uniform(0.25, 0.55), fc="#5F8A4E", ec="#3F6234", lw=0.4, alpha=0.95))
    ax.add_patch(Rectangle((3.2, 3.8), 3.6, 1.5, fc="#6FA0C8", ec="none", alpha=0.8))
    ax.set_title("What is there", fontsize=11)
    # 2. Footprints
    ax = axs[1]
    ax.add_patch(Rectangle((0.6, 0.6), 8.8, 8.8, fc="white", ec=NAVY, lw=1.2))
    for (x, y, w, h) in [(1, 1, 3, 2.5), (4.6, 1, 2.2, 3.4), (7.2, 1, 1.9, 2.4), (1, 6, 2.2, 3.1),
                         (6.2, 6.5, 2.9, 2.5), (3.8, 7.2, 1.8, 1.9)]:
        ax.add_patch(Rectangle((x, y), w, h, fc=CORNER, ec=NAVY, lw=0.8))
    ax.set_title("Building footprints", fontsize=11)
    # 3. Point symbol
    ax = axs[2]
    ax.add_patch(Rectangle((0.6, 0.6), 8.8, 8.8, fc="white", ec=CORNER, lw=1, ls="--"))
    ax.scatter([5], [5], marker="*", s=1400, c=CLAY, ec=NAVY, lw=1.2)
    ax.set_title("One point symbol", fontsize=11)
    for a in axs:
        a.set_xlim(-0.2, 10.2); a.set_ylim(-0.2, 10.2); off(a)
    fig.text(0.5, 0.02, "Clarity goes up  →          →  Certainty about what is really there goes down",
             ha="center", fontsize=10.5, weight="bold", color=NAVY)
    fig.tight_layout(rect=(0, 0.06, 1, 1))
    save(fig, OUT / "abstraction.png")


# ---------------------------------------------------------------- reliability diagram
def reliability():
    fig, (ax, lg) = plt.subplots(1, 2, figsize=(9.8, 4.2), gridspec_kw=dict(width_ratios=[1, 1.15]))
    ax.add_patch(Rectangle((0, 0), 6, 7, fc="white", ec=NAVY, lw=1.4))
    ax.add_patch(MPoly([(0, 0), (3.6, 0), (2.6, 4.3), (0, 4.9)], fc="none", ec=NAVY, hatch="////", lw=1))
    ax.add_patch(MPoly([(3.6, 0), (6, 0), (6, 3.4), (2.6, 4.3)], fc="none", ec=NAVY, hatch="....", lw=1))
    ax.add_patch(MPoly([(0, 4.9), (2.6, 4.3), (6, 3.4), (6, 7), (0, 7)], fc="none", ec=NAVY, lw=1))
    ax.text(3, 7.25, "RELIABILITY DIAGRAM", ha="center", fontsize=9.5, weight="bold")
    ax.set_xlim(-0.3, 6.3); ax.set_ylim(-0.3, 7.6); off(ax)
    lg.axis("off"); lg.set_xlim(0, 10); lg.set_ylim(0, 10)
    items = [("////", "Plane-table ground survey, 1925"),
             ("....", "Aerial photographs, 1948"),
             ("", "Compiled from older maps, date unknown")]
    for i, (h, t) in enumerate(items):
        y = 8.6 - i * 1.6
        lg.add_patch(Rectangle((0.2, y - 0.45), 1.1, 0.9, fc="white", ec=NAVY, hatch=h))
        lg.text(1.7, y, t, va="center", fontsize=9.5)
    lg.text(0.2, 3.7, "CONTOURS", fontsize=9.5, weight="bold")
    lg.plot([0.2, 1.4], [2.7, 2.7], color="#8B5A2B", lw=1.6)
    lg.text(1.7, 2.7, "Reliable", va="center", fontsize=9.5)
    lg.plot([0.2, 1.4], [1.6, 1.6], color="#8B5A2B", lw=1.6, ls=(0, (5, 3)))
    lg.text(1.7, 1.6, "Approximate", va="center", fontsize=9.5)
    save(fig, OUT / "reliability-diagram.png")


# ---------------------------------------------------------------- showing uncertainty on a map
def estimate_map():
    r = np.random.default_rng(9)
    n = 7
    est = ndimage.gaussian_filter(r.normal(0, 1, (n, n)), 1.2)
    est = (est - est.min()) / (est.max() - est.min()) * 40 + 5  # e.g. percent in poverty
    cv = np.clip(r.gamma(2.2, 9, (n, n)), 3, 60)  # coefficient of variation, percent
    from matplotlib import cm
    cmap = plt.get_cmap("YlGnBu")
    fig, axs = plt.subplots(1, 2, figsize=(10, 4.7))
    for ax, show_unc, title in [(axs[0], False, "Estimates only"),
                                (axs[1], True, "Estimates, faded where unreliable")]:
        for (i, j), v in np.ndenumerate(est):
            col = np.array(cmap((v - 5) / 40))[:3]
            if show_unc:
                a = 1.0 if cv[i, j] < 15 else (0.55 if cv[i, j] < 30 else 0.18)
                col = col * a + (1 - a) * np.ones(3)
            ax.add_patch(Rectangle((j, i), 1, 1, fc=col, ec="white", lw=1.5))
            if show_unc and cv[i, j] >= 30:
                ax.text(j + 0.5, i + 0.5, "?", ha="center", va="center", fontsize=10, color=BASIN)
        ax.set_title(title, fontsize=11.5)
        ax.set_xlim(0, n); ax.set_ylim(0, n); off(ax)
    # legend
    sm = plt.cm.ScalarMappable(cmap=cmap, norm=plt.Normalize(5, 45))
    cb = fig.colorbar(sm, ax=axs, orientation="horizontal", fraction=0.05, pad=0.04, shrink=0.5)
    cb.set_label("Estimated percent (made-up)", fontsize=9)
    fig.text(0.79, 0.02, "Faded: CV 15–30%   Very faded with ?: CV over 30%", ha="center", fontsize=8.5,
             color=BASIN)
    save(fig, OUT / "estimate-map.png")


if __name__ == "__main__":
    cloud()
    rmse()
    roads()
    topology()
    lifecycle()
    visual_variables()
    location_circle()
    abstraction()
    reliability()
    estimate_map()
