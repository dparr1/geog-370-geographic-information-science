"""Figures for Chapter 10, Federal Spatial Data Sets.

The maps of NLCD, Landsat, MODIS NDVI, 3DEP, and NHD around Chapel Hill, and
the pixel-size, flood-zone, and resolution-versus-revisit diagrams, are
D. Parr's own figures from the lecture 9b slides (made from public-domain
federal data) and are copied into images/federal-data/ as they are. This
script makes the chapter's new diagrams:

  huc-digits.png        how a 12-digit hydrologic unit code nests
  flood-odds.png        chance of at least one 1% or 0.2% flood in n years
  ndvi-grid.png         NDVI worked out cell by cell from red and NIR bands

Run from the repository root:  python scripts/figures/federal_data.py
"""
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch, Rectangle

from style import (NAVY, PINE, BLUE, BASIN, CORNER, FOG, CLAY, POPLAR,
                   DOGWOOD, WATER, SAND, save)

OUT = "images/federal-data/"


def huc_digits():
    """The digits of a HUC-12, with each level's pair of digits labeled."""
    pairs = ["03", "03", "00", "02", "05", "03"]
    levels = [
        ("HUC-2", "Region", "South Atlantic-Gulf"),
        ("HUC-4", "Subregion", "Cape Fear"),
        ("HUC-6", "Basin", "Cape Fear"),
        ("HUC-8", "Subbasin", "Haw"),
        ("HUC-10", "Watershed", "example digits"),
        ("HUC-12", "Subwatershed", "example digits"),
    ]
    colors = [NAVY, PINE, BLUE, CLAY, POPLAR, BASIN]
    fig, ax = plt.subplots(figsize=(11, 4.6))
    ax.set_xlim(0, 15.2)
    ax.set_ylim(-3.4, 1.3)
    ax.axis("off")
    w = 0.9
    for i, (pair, col) in enumerate(zip(pairs, colors)):
        for j, d in enumerate(pair):
            x = 0.4 + (2 * i + j) * (w + 0.08)
            ax.add_patch(FancyBboxPatch((x, 0), w, 1.1,
                                        boxstyle="round,pad=0,rounding_size=0.08",
                                        fc=col, ec="white", lw=1.5))
            ax.text(x + w / 2, 0.55, d, ha="center", va="center",
                    color="white", fontsize=24, fontweight="bold")
    # brackets showing how each level adds two digits
    for i, ((code, name, place), col) in enumerate(zip(levels, colors)):
        x0 = 0.4
        x1 = 0.4 + (2 * i + 2) * (w + 0.08) - 0.08
        y = -0.35 - 0.5 * i
        ax.plot([x0, x1], [y, y], color=col, lw=3, solid_capstyle="butt")
        ax.plot([x1, x1], [y, y + 0.18], color=col, lw=3)
        t = ax.text(x1 + 0.15, y, f"{code}  {name}", va="center",
                    fontsize=10.5, fontweight="bold", color=col)
        ax.annotate(f"  {place}", xycoords=t, xy=(1, 0.5), va="center",
                    fontsize=10, color=NAVY if i < 4 else BASIN,
                    style="normal" if i < 4 else "italic")
    save(fig, OUT + "huc-digits.png")


def flood_odds():
    """Chance of at least one flood of a given annual chance in n years."""
    years = np.arange(0, 101)
    fig, ax = plt.subplots(figsize=(8.5, 4.6))
    for p, col, lab in [(0.01, BLUE, "1% annual chance (“100-year”) flood"),
                        (0.002, POPLAR, "0.2% annual chance (“500-year”) flood")]:
        prob = 1 - (1 - p) ** years
        ax.plot(years, prob * 100, color=col, lw=3, label=lab)
    # 30-year mortgage marker
    p30 = (1 - 0.99 ** 30) * 100
    ax.axvline(30, color=BASIN, lw=1, ls="--")
    ax.plot([30], [p30], "o", color=NAVY, ms=8, zorder=5)
    ax.annotate(f"30-year mortgage:\n{p30:.0f}% chance of at least\none 1% flood",
                xy=(30, p30), xytext=(38, 52), fontsize=10, color=NAVY,
                arrowprops=dict(arrowstyle="-", color=NAVY, lw=1))
    p100 = (1 - 0.99 ** 100) * 100
    ax.plot([100], [p100], "o", color=NAVY, ms=6, zorder=5)
    ax.annotate(f"{p100:.0f}% in 100 years", xy=(100, p100), xytext=(78, 74),
                fontsize=10, color=NAVY)
    ax.set_xlim(0, 102)
    ax.set_ylim(0, 80)
    ax.set_xlabel("Years")
    ax.set_ylabel("Chance of at least one flood (%)")
    ax.grid(color=FOG)
    ax.spines[["top", "right"]].set_visible(False)
    ax.legend(loc="upper left", frameon=False)
    save(fig, OUT + "flood-odds.png")


def ndvi_grid():
    """Red and NIR reflectance for a 3 x 3 patch, and the NDVI they give."""
    red = np.array([[0.04, 0.05, 0.12],
                    [0.05, 0.20, 0.25],
                    [0.06, 0.18, 0.05]])
    nir = np.array([[0.45, 0.50, 0.28],
                    [0.48, 0.26, 0.30],
                    [0.40, 0.24, 0.02]])
    ndvi = (nir - red) / (nir + red)
    fig, axes = plt.subplots(1, 3, figsize=(10.5, 3.9))
    panels = [(red, "Red reflectance", "Reds", 0, 0.5, "{:.2f}"),
              (nir, "Near-infrared reflectance", "Purples", 0, 0.5, "{:.2f}"),
              (ndvi, "NDVI = (NIR − Red) / (NIR + Red)", "RdYlGn", -1, 1, "{:.2f}")]
    for ax, (arr, title, cmap, lo, hi, fmt) in zip(axes, panels):
        ax.imshow(arr, cmap=cmap, vmin=lo, vmax=hi)
        for (r, c), v in np.ndenumerate(arr):
            shade = plt.get_cmap(cmap)((v - lo) / (hi - lo))
            lum = 0.299 * shade[0] + 0.587 * shade[1] + 0.114 * shade[2]
            ax.text(c, r, fmt.format(v).replace("-", "−"), ha="center",
                    va="center", fontsize=13, fontweight="bold",
                    color="white" if lum < 0.5 else NAVY)
        ax.set_xticks(np.arange(-0.5, 3, 1), minor=True)
        ax.set_yticks(np.arange(-0.5, 3, 1), minor=True)
        ax.grid(which="minor", color="white", lw=2)
        ax.tick_params(which="both", length=0, labelbottom=False, labelleft=False)
        ax.set_title(title, fontsize=11.5)
    save(fig, OUT + "ndvi-grid.png")


if __name__ == "__main__":
    huc_digits()
    flood_odds()
    ndvi_grid()
