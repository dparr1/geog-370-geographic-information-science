"""Figures for Chapter 11, Data Classing and Choropleth Maps.

Usage: python data_classing.py <dir with ne_10m_admin_2_counties.geojson>

County data are in data/nc_counties_2025.csv: 2025 population estimates
(U.S. Census Bureau) and land area from the 2020 Census Gazetteer.
"""
import sys
from pathlib import Path

import numpy as np
import pandas as pd
import geopandas as gpd
import matplotlib.pyplot as plt
from matplotlib.colors import ListedColormap, Normalize
from matplotlib.patches import Patch

from style import NAVY, BASIN, CORNER, FOG, CLAY, save

HERE = Path(__file__).parent
OUT = HERE.parent.parent / "images" / "data-classing"
OUT.mkdir(parents=True, exist_ok=True)

ne = Path(sys.argv[1])
co = gpd.read_file(ne / "ne_10m_admin_2_counties.geojson")
co = co[co["REGION"] == "NC"].copy()
co["geoid"] = co["CODE_LOCAL"].astype(str)
df = pd.read_csv(HERE / "data" / "nc_counties_2025.csv", dtype={"geoid": str})
nc = co.merge(df, on="geoid").to_crs("EPSG:32119")
assert len(nc) == 100
x = nc["density"].to_numpy()

BLUES = {
    2: ["#9ecae1", "#08519c"],
    3: ["#deebf7", "#9ecae1", "#3182bd"],
    5: ["#eff3ff", "#bdd7e7", "#6baed6", "#3182bd", "#08519c"],
    9: ["#f7fbff", "#deebf7", "#c6dbef", "#9ecae1", "#6baed6",
        "#4292c6", "#2171b5", "#08519c", "#08306b"],
}
DIVERGING = ["#67a9cf", "#f7f7f7", "#fddbc7", "#f4a582", "#d6604d", "#b2182b"]


# ---------- classification methods ----------
def equal_interval(v, k):
    return list(np.linspace(v.min(), v.max(), k + 1))


def quantile(v, k):
    return list(np.quantile(v, np.linspace(0, 1, k + 1)))


def arithmetic(v, k):
    lo, hi = v.min(), v.max()
    w = (hi - lo) / (k * (k + 1) / 2)
    b = [lo]
    for i in range(1, k + 1):
        b.append(b[-1] + i * w)
    return b


def geometric(v, k):
    lo, hi = v.min(), v.max()
    r = (hi / lo) ** (1 / k)
    return [lo * r ** i for i in range(k + 1)]


def jenks(v, k):
    """Fisher-Jenks optimal breaks by dynamic programming."""
    s = np.sort(v)
    n = len(s)
    cs, cs2 = np.concatenate([[0], np.cumsum(s)]), np.concatenate([[0], np.cumsum(s ** 2)])

    def ssd(i, j):  # sum of squared deviations of s[i:j]
        m = j - i
        t = cs[j] - cs[i]
        return cs2[j] - cs2[i] - t * t / m

    cost = np.full((k + 1, n + 1), np.inf)
    back = np.zeros((k + 1, n + 1), dtype=int)
    cost[0, 0] = 0
    for c in range(1, k + 1):
        for j in range(c, n + 1):
            for i in range(c - 1, j):
                val = cost[c - 1, i] + ssd(i, j)
                if val < cost[c, j]:
                    cost[c, j], back[c, j] = val, i
    cuts, j = [], n
    for c in range(k, 0, -1):
        i = back[c, j]
        cuts.append(i)
        j = i
    cuts = sorted(cuts)[1:]
    return [s[0]] + [s[c - 1] for c in cuts] + [s[-1]]


def std_dev(v):
    m, sd = v.mean(), v.std()
    edges = [v.min()] + [m + z * sd for z in (-0.5, 0.5, 1.5, 2.5, 3.5)] + [v.max()]
    return [e for e in edges if e >= v.min() - 1e-9 and e <= v.max() + 1e-9] if False else edges


def classify(v, breaks):
    idx = np.searchsorted(breaks[1:-1], v, side="left")
    return np.clip(idx, 0, len(breaks) - 2)


def gvf(v, breaks):
    cls = classify(v, breaks)
    sdam = ((v - v.mean()) ** 2).sum()
    sdcm = sum(((v[cls == c] - v[cls == c].mean()) ** 2).sum()
               for c in np.unique(cls))
    return 1 - sdcm / sdam


def fmt(b):
    return f"{b:,.0f}"


def legend_labels(breaks):
    return [f"{fmt(breaks[i])} – {fmt(breaks[i + 1])}" for i in range(len(breaks) - 1)]


def draw(ax, values, breaks, colors, title=None, legend=True, loc="lower left",
         labels=None, fontsize=8.5):
    cls = classify(values, breaks)
    nc.assign(c=[colors[i] for i in cls]).plot(
        ax=ax, color=nc.assign(c=[colors[i] for i in cls])["c"],
        edgecolor="#b8bcbf", linewidth=0.3)
    ax.set_axis_off()
    if title:
        ax.set_title(title, fontsize=12, loc="left")
    if legend:
        labels = labels or legend_labels(breaks)
        counts = np.bincount(cls, minlength=len(colors))
        handles = [Patch(facecolor=colors[i], edgecolor=CORNER,
                         label=f"{labels[i]}  ({counts[i]})")
                   for i in range(len(colors))]
        ax.legend(handles=handles, loc=loc, frameon=False, fontsize=fontsize,
                  ncol=2 if len(colors) > 6 else 1, columnspacing=1.2,
                  handlelength=1.2, handleheight=1.0, borderaxespad=0)


def bbox(ax, below=110e3):
    x0, y0, x1, y1 = nc.total_bounds
    ax.set_xlim(x0 - 5e3, x1 + 5e3)
    ax.set_ylim(y0 - below, y1 + 5e3)


# ---------- figures ----------
def counts_vs_density():
    fig, axes = plt.subplots(1, 2, figsize=(13, 4.3))
    pop = nc["pop_2025"].to_numpy().astype(float)
    b1 = jenks(pop, 5)
    draw(axes[0], pop, b1, BLUES[5], "Population (a raw count)")
    b2 = jenks(x, 5)
    draw(axes[1], x, b2, BLUES[5], "Population density (people per square mile)")
    for ax in axes:
        bbox(ax)
    save(fig, OUT / "counts-vs-density.png")


def histogram():
    fig, ax = plt.subplots(figsize=(9, 3.6))
    bins = np.arange(0, 2450, 50)
    ax.hist(x, bins=bins, color="#6baed6", edgecolor="white", zorder=2)
    ax.axvline(np.median(x), color=NAVY, lw=1.5, ls="--", zorder=3)
    ax.axvline(x.mean(), color=CLAY, lw=1.5, ls="--", zorder=3)
    ax.text(np.median(x) + 25, 27, f"Median {np.median(x):,.0f}", color=NAVY, fontsize=10)
    ax.text(x.mean() + 25, 23, f"Mean {x.mean():,.0f}", color=CLAY, fontsize=10)
    big = nc.sort_values("density", ascending=False).head(4)
    for (_, r), h in zip(big.iterrows(), (6, 6, 9.5, 6)):
        ax.annotate(r["county"], (r["density"], 1), xytext=(r["density"], h),
                    ha="center", fontsize=9, color=BASIN,
                    arrowprops=dict(arrowstyle="-", color=BASIN, lw=0.8))
    ax.set_xlabel("People per square mile of land, 2025")
    ax.set_ylabel("Number of counties")
    ax.set_xlim(0, 2450)
    ax.set_ylim(0, 30)
    ax.spines[["top", "right"]].set_visible(False)
    ax.grid(axis="y", color=FOG, zorder=0)
    save(fig, OUT / "density-histogram.png")


def number_of_classes():
    fig, axes = plt.subplots(2, 2, figsize=(13, 7.0))
    for ax, k in zip(axes.flat[:3], (2, 5, 9)):
        draw(ax, x, quantile(x, k), BLUES[k], f"{k} classes (quantiles)",
             fontsize=7.5 if k == 9 else 8.5)
    ax = axes.flat[3]
    norm = Normalize(vmin=np.log10(x.min()), vmax=np.log10(x.max()))
    cmap = plt.get_cmap("Blues")
    nc.plot(ax=ax, color=[cmap(0.08 + 0.92 * norm(np.log10(v))) for v in x],
            edgecolor="#b8bcbf", linewidth=0.3)
    ax.set_axis_off()
    ax.set_title("Unclassed (each county its own shade)", fontsize=12, loc="left")
    cax = ax.inset_axes([0.02, 0.22, 0.32, 0.04])
    grad = np.linspace(0, 1, 256)[None, :]
    cax.imshow(grad, aspect="auto", cmap=ListedColormap([cmap(0.08 + 0.92 * g) for g in grad[0]]))
    cax.set_yticks([])
    ticks = [10, 100, 1000]
    cax.set_xticks([norm(np.log10(t)) * 255 for t in ticks])
    cax.set_xticklabels([f"{t:,}" for t in ticks], fontsize=8.5)
    cax.tick_params(length=2)
    for s in cax.spines.values():
        s.set_visible(False)
    cax.set_xlabel("People per sq mi (log scale)", fontsize=8.5)
    for ax in axes.flat:
        bbox(ax)
    fig.subplots_adjust(hspace=0.12, wspace=0.02)
    save(fig, OUT / "number-of-classes.png")


METHODS = [
    ("Equal interval", equal_interval(x, 5), BLUES[5]),
    ("Quantile", quantile(x, 5), BLUES[5]),
    ("Arithmetic progression", arithmetic(x, 5), BLUES[5]),
    ("Geometric progression", geometric(x, 5), BLUES[5]),
    ("Natural breaks (Jenks)", jenks(x, 5), BLUES[5]),
]
sd_b = std_dev(x)
sd_labels = ["Below −0.5 SD", "−0.5 to 0.5 SD", "0.5 to 1.5 SD", "1.5 to 2.5 SD",
             "2.5 to 3.5 SD", "Above 3.5 SD"]
sd_breaks = [x.min()] + [x.mean() + z * x.std() for z in (-0.5, 0.5, 1.5, 2.5, 3.5)] + [x.max()]
METHODS.append(("Standard deviation", sd_breaks, DIVERGING))


def methods_maps():
    fig, axes = plt.subplots(3, 2, figsize=(13, 10.4))
    for ax, (name, b, cols) in zip(axes.flat, METHODS):
        labels = None
        if name == "Standard deviation":
            labels = [f"{l}: {fmt(b[i])} – {fmt(b[i + 1])}"
                      for i, l in enumerate(sd_labels)]
        draw(ax, x, b, cols, name, labels=labels, fontsize=8)
        bbox(ax)
    fig.subplots_adjust(hspace=0.12, wspace=0.02)
    save(fig, OUT / "methods-maps.png")


def methods_histograms():
    fig, axes = plt.subplots(3, 2, figsize=(12, 8.4), sharex=True)
    bins = np.arange(0, 2450, 25)
    for ax, (name, b, cols) in zip(axes.flat, METHODS):
        cls = classify(x, b)
        for c in range(len(cols)):
            ax.hist(x[cls == c], bins=bins, color=cols[c], edgecolor=BASIN,
                    linewidth=0.4, zorder=2)
        for e in b[1:-1]:
            ax.axvline(e, color=NAVY, lw=1, ls=(0, (3, 2)), zorder=3)
        ax.set_title(f"{name}   (GVF {gvf(x, b):.2f})", fontsize=11, loc="left")
        ax.spines[["top", "right"]].set_visible(False)
        ax.set_xlim(0, 2450)
        ax.set_ylim(0, 22)
        ax.grid(axis="y", color=FOG, zorder=0)
    for ax in axes[-1]:
        ax.set_xlabel("People per square mile")
    for ax in axes[:, 0]:
        ax.set_ylabel("Counties")
    fig.tight_layout()
    save(fig, OUT / "methods-histograms.png")


def report():
    print(f"n={len(x)} mean={x.mean():.1f} median={np.median(x):.1f} sd={x.std():.1f}")
    for name, b, _ in METHODS:
        cls = classify(x, b)
        print(f"{name:24s} GVF={gvf(x, b):.3f} breaks={[round(v, 1) for v in b]} "
              f"counts={np.bincount(cls, minlength=len(b) - 1).tolist()}")


if __name__ == "__main__":
    report()
    counts_vs_density()
    histogram()
    number_of_classes()
    methods_maps()
    methods_histograms()
