"""Figures for Chapter 15, Spatial Interpolation.

Usage: python interpolation.py <Natural Earth dir>

The surfaces and samples are made up (fixed seeds), except the airport map,
which uses Natural Earth airports and states.
"""
import sys
from pathlib import Path

import numpy as np
import matplotlib.pyplot as plt
from matplotlib.patches import Circle, Ellipse, Wedge, FancyArrowPatch
from scipy.interpolate import RBFInterpolator
from scipy.spatial import Voronoi, cKDTree

from style import NAVY, PINE, BLUE, BASIN, CORNER, FOG, CLAY, POPLAR, GINKGO, SAND, DOGWOOD, BERRY, DUSK, save

OUT = Path(__file__).parent.parent.parent / "images" / "interpolation"
OUT.mkdir(parents=True, exist_ok=True)

CMAP = "gist_earth"


# ---------- a made-up "true" surface ----------
BUMPS = [(2.5, 7.5, 1.4, 55), (7.0, 6.5, 1.0, 40), (6.0, 2.5, 1.6, -30), (3.0, 3.0, 0.8, 25), (8.5, 9.0, 0.9, 30)]


def truth(x, y):
    z = 40 + 3.0 * x + 2.0 * y
    for cx, cy, s, a in BUMPS:
        z = z + a * np.exp(-((x - cx) ** 2 + (y - cy) ** 2) / (2 * s ** 2))
    return z


G = np.linspace(0, 10, 160)
GX, GY = np.meshgrid(G, G)
TRUE = truth(GX, GY)
VMIN, VMAX = TRUE.min(), TRUE.max()


def samples(n=40, seed=18):
    rng = np.random.default_rng(seed)
    p = rng.uniform(0.3, 9.7, (n, 2))
    return p, truth(p[:, 0], p[:, 1])


# ---------- interpolators ----------
def nearest(p, z, q):
    _, i = cKDTree(p).query(q)
    return z[i]


def idw(p, z, q, power=2, k=None):
    d = np.hypot(q[:, None, 0] - p[None, :, 0], q[:, None, 1] - p[None, :, 1])
    d = np.maximum(d, 1e-9)
    if k is not None:
        idx = np.argsort(d, axis=1)[:, :k]
        dd = np.take_along_axis(d, idx, 1)
        zz = z[idx]
    else:
        dd, zz = d, np.broadcast_to(z, d.shape)
    w = 1 / dd ** power
    return (w * zz).sum(1) / w.sum(1)


def poly_terms(x, y, order):
    return np.column_stack([x ** i * y ** j for i in range(order + 1) for j in range(order + 1 - i)])


def poly(p, z, q, order=2):
    A = poly_terms(p[:, 0], p[:, 1], order)
    beta, *_ = np.linalg.lstsq(A, z, rcond=None)
    return poly_terms(q[:, 0], q[:, 1], order) @ beta


def rbf(p, z, q):
    return RBFInterpolator(p, z, kernel="thin_plate_spline")(q)


METHODS = [("Nearest neighbor", nearest), ("IDW (power 2, 12 neighbors)", lambda p, z, q: idw(p, z, q, 2, 12)),
           ("Global polynomial (2nd order)", lambda p, z, q: poly(p, z, q, 2)), ("Radial basis function", rbf)]


def loocv(f, p, z):
    err = []
    for i in range(len(z)):
        m = np.arange(len(z)) != i
        err.append(f(p[m], z[m], p[i:i + 1])[0] - z[i])
    err = np.array(err)
    return np.sqrt((err ** 2).mean()), err.mean()


def grid_eval(f, p, z):
    q = np.column_stack([GX.ravel(), GY.ravel()])
    return f(p, z, q).reshape(GX.shape)


def surf(ax, Z, p=None, title=None):
    im = ax.imshow(Z, origin="lower", extent=(0, 10, 0, 10), cmap=CMAP, vmin=VMIN - 10, vmax=VMAX + 10)
    ax.contour(GX, GY, Z, levels=np.arange(20, 160, 10), colors=NAVY, linewidths=0.4, alpha=0.6)
    if p is not None:
        ax.scatter(*p.T, s=14, c="white", ec=NAVY, lw=0.8, zorder=4)
    if title:
        ax.set_title(title, fontsize=11.5, loc="left")
    ax.set_xticks([])
    ax.set_yticks([])
    for s in ax.spines.values():
        s.set_color(CORNER)
    return im


# ---------- 1. the problem ----------
def problem():
    fig, ax = plt.subplots(figsize=(5.4, 4.4))
    pts = [(2.0, 7.2, 35), (7.6, 7.8, 19), (1.6, 1.8, 22), (8.2, 2.4, 24)]
    x0 = (4.8, 4.6)
    for x, y, v in pts:
        ax.plot([x0[0], x], [x0[1], y], color=CORNER, lw=1.2, ls="--", zorder=1)
        ax.scatter(x, y, s=120, c=BLUE, ec=NAVY, lw=1, zorder=3)
        ax.text(x, y + 0.55, str(v), ha="center", fontsize=12, weight="bold", color=NAVY)
    ax.scatter(*x0, s=160, marker="X", c=CLAY, ec=NAVY, lw=0.8, zorder=4)
    ax.text(x0[0] + 0.4, x0[1] - 0.2, "?", fontsize=18, weight="bold", color=CLAY, va="top")
    ax.legend([plt.Line2D([], [], marker="o", ls="", mfc=BLUE, mec=NAVY, ms=9),
               plt.Line2D([], [], marker="X", ls="", mfc=CLAY, mec=NAVY, ms=10)],
              ["Observation", "Unsampled location"], loc="lower center", bbox_to_anchor=(0.5, -0.02),
              ncol=2, frameon=False, fontsize=9.5)
    ax.set_xlim(0, 10)
    ax.set_ylim(0.6, 9)
    ax.set_aspect("equal")
    ax.set_axis_off()
    save(fig, OUT / "problem.png")


# ---------- 2. exact vs inexact (1D) ----------
X1 = np.array([0, 10, 20, 30, 40, 50, 60, 70])
Z1 = np.array([1.0, 2.0, 1.5, 3.0, 3.0, 2.0, 3.5, 4.0])
XF = np.linspace(-2, 72, 600)


def exact_inexact():
    fig, ax = plt.subplots(figsize=(8.5, 3.6))
    ax.scatter(X1, Z1, s=50, c=NAVY, zorder=5, label="Observations")
    rb = RBFInterpolator(X1[:, None], Z1, kernel="thin_plate_spline")(XF[:, None])
    ax.plot(XF, rb, color=PINE, lw=2.2, label="Exact: passes through every observation")
    b = np.polyfit(X1, Z1, 1)
    ax.plot(XF, np.polyval(b, XF), color=CLAY, lw=2.2, ls="--", label="Inexact: a trend line misses them")
    ax.set_xlabel("Distance along a profile")
    ax.set_ylabel("Value")
    ax.spines[["top", "right"]].set_visible(False)
    ax.legend(frameon=False, fontsize=9.5, loc="upper left")
    ax.set_ylim(0, 5.2)
    save(fig, OUT / "exact-inexact.png")


# ---------- 3. 1D profiles of the methods ----------
def profiles():
    fig, axes = plt.subplots(2, 2, figsize=(11, 6.2), sharex=True, sharey=True)
    q = XF[:, None]
    p = X1[:, None].astype(float)
    nn = Z1[np.abs(XF[:, None] - X1[None, :]).argmin(1)]
    avg = np.array([Z1[np.abs(X1 - x) <= 15].mean() for x in XF])
    d = np.maximum(np.abs(XF[:, None] - X1[None, :]), 1e-9)
    idw1 = (Z1 / d).sum(1) / (1 / d).sum(1)
    idw3 = (Z1 / d ** 3).sum(1) / (1 / d ** 3).sum(1)
    rb = RBFInterpolator(p, Z1, kernel="thin_plate_spline")(q)
    for ax, ys, t in [(axes[0, 0], [(nn, PINE, "-", None)], "Nearest neighbor: steps"),
                      (axes[0, 1], [(avg, BLUE, "-", None)], "Average neighbor (radius 15): inexact"),
                      (axes[1, 0], [(idw1, CLAY, "-", "power 1"), (idw3, BERRY, "--", "power 3")],
                       "IDW: exact, flat near each point"),
                      (axes[1, 1], [(rb, DUSK, "-", None)], "Radial basis function: exact, smooth")]:
        for y, c, ls, lab in ys:
            ax.plot(XF, y, color=c, lw=2, ls=ls, label=lab)
        ax.scatter(X1, Z1, s=40, c=NAVY, zorder=5)
        ax.set_title(t, fontsize=11.5, loc="left")
        ax.spines[["top", "right"]].set_visible(False)
        if ys[0][3]:
            ax.legend(frameon=False, fontsize=9, loc="upper left")
    axes[1, 0].set_xlabel("Distance along a profile")
    axes[1, 1].set_xlabel("Distance along a profile")
    axes[0, 0].set_ylabel("Value")
    axes[1, 0].set_ylabel("Value")
    axes[0, 0].set_ylim(0, 5)
    fig.tight_layout()
    save(fig, OUT / "profiles.png")
    print("rbf range", rb.min(), rb.max(), "obs", Z1.min(), Z1.max())


# ---------- 4. Thiessen polygons on the made-up surface ----------
def thiessen():
    p, z = samples()
    fig, axes = plt.subplots(1, 2, figsize=(10.5, 4.9))
    surf(axes[0], TRUE, p, "The true surface and 40 samples")
    Z = grid_eval(nearest, p, z)
    surf(axes[1], Z, p, "Nearest neighbor (Thiessen polygons)")
    vor = Voronoi(np.vstack([p, [[-50, -50], [-50, 60], [60, -50], [60, 60]]]))
    for (a, b) in vor.ridge_vertices:
        if a >= 0 and b >= 0:
            v = vor.vertices[[a, b]]
            axes[1].plot(*v.T, color="white", lw=0.9)
    for ax in axes:
        ax.set_xlim(0, 10)
        ax.set_ylim(0, 10)
    save(fig, OUT / "thiessen.png")


# ---------- 5. airports: Thiessen polygons at national scale ----------
def airports(ne):
    import geopandas as gpd
    from shapely.ops import voronoi_diagram
    from shapely.geometry import MultiPoint
    a = gpd.read_file(ne / "ne_10m_airports.geojson")
    s = gpd.read_file(ne / "ne_50m_admin_1_states_provinces_lakes.geojson")
    us = s[(s.adm0_a3 == "USA") & (~s.postal.isin(["AK", "HI"]))].to_crs("EPSG:5070")
    a = gpd.sjoin(a.to_crs("EPSG:5070"), us[["geometry"]], predicate="within")
    outline = us.unary_union
    vd = voronoi_diagram(MultiPoint(list(a.geometry)), envelope=outline.envelope.buffer(5e5))
    cells = gpd.GeoDataFrame(geometry=list(vd.geoms), crs="EPSG:5070").clip(outline)
    cells["area"] = cells.area / 1e6
    fig, ax = plt.subplots(figsize=(10, 6))
    cells.plot(ax=ax, column="area", cmap="YlOrBr", edgecolor="white", lw=0.6,
               legend=True, legend_kwds=dict(label="Polygon area (km²)", shrink=0.6))
    us.boundary.plot(ax=ax, color=BASIN, lw=0.3)
    a.plot(ax=ax, color=NAVY, markersize=8)
    ax.set_axis_off()
    save(fig, OUT / "airports-thiessen.png")
    print("airports", len(a), "polygon area km2 min/median/max", cells.area.min() / 1e6,
          cells["area"].median(), cells["area"].max())


# ---------- 6. average neighbor ----------
PTS2 = np.array([[10, 30], [20, 40], [30, 30], [30, 10], [50, 40], [50, 10], [10, 0], [40, 20]], float)
V2 = np.array([1.0, 2.0, 3.0, 3.0, 4.0, 2.0, 1.0, 5.0])


def average_neighbor():
    x0 = np.array([22.0, 24.0])
    r = 17.0
    d = np.hypot(*(PTS2 - x0).T)
    inside = d <= r
    fig, ax = plt.subplots(figsize=(5.6, 4.6))
    ax.add_patch(Circle(x0, r, fc=BLUE, alpha=0.12, ec=BLUE, lw=1.6))
    ax.scatter(*PTS2[~inside].T, s=70, fc="white", ec=BASIN, lw=1.3, zorder=3)
    ax.scatter(*PTS2[inside].T, s=70, c=BLUE, ec=NAVY, zorder=4)
    for (x, y), v in zip(PTS2, V2):
        ax.text(x + 1.4, y + 1.2, f"{v:g}", fontsize=10.5, color=NAVY, weight="bold")
    ax.scatter(*x0, s=110, marker="X", c=CLAY, ec=NAVY, lw=0.6, zorder=5)
    ax.annotate("", xy=(x0[0] - r, x0[1]), xytext=x0, arrowprops=dict(arrowstyle="<->", color=NAVY, lw=1.1))
    ax.text(x0[0] - r / 2, x0[1] - 2.6, "r", fontsize=12, style="italic", color=NAVY, ha="center")
    est = V2[inside].mean()
    ax.text(25, -6.5, f"Estimate = ({' + '.join(f'{v:g}' for v in V2[inside])}) ÷ {inside.sum()} = {est:g}",
            ha="center", fontsize=10.5, color=CLAY)
    ax.set_xlim(-2, 56)
    ax.set_ylim(-8, 46)
    ax.set_aspect("equal")
    ax.set_axis_off()
    save(fig, OUT / "average-neighbor.png")
    print("avg neighbor", V2[inside], est)


# ---------- 7. neighborhood options ----------
def search_options():
    rng = np.random.default_rng(9)
    pts = np.vstack([rng.normal([6.6, 6.4], 0.6, (12, 2)), rng.uniform(0.5, 9.5, (16, 2))])
    x0 = np.array([5, 5])
    fig, axes = plt.subplots(1, 4, figsize=(14, 3.9))
    d = np.hypot(*(pts - x0).T)
    # fixed radius
    ax = axes[0]
    sel = d <= 2.6
    ax.add_patch(Circle(x0, 2.6, fc=BLUE, alpha=0.12, ec=BLUE, lw=1.4))
    ax.set_title(f"Fixed radius: {sel.sum()} points", fontsize=11, loc="left")
    sets = [sel]
    # k nearest
    ax = axes[1]
    k = 8
    sel = np.zeros(len(pts), bool)
    sel[np.argsort(d)[:k]] = True
    ax.add_patch(Circle(x0, np.sort(d)[k - 1] + 0.05, fc=BLUE, alpha=0.12, ec=BLUE, lw=1.4, ls="--"))
    ax.set_title("Variable radius: 8 nearest", fontsize=11, loc="left")
    sets.append(sel)
    # quadrants: 2 nearest per quadrant
    ax = axes[2]
    ang = np.degrees(np.arctan2(*(pts - x0).T[::-1])) % 360
    sel = np.zeros(len(pts), bool)
    cols = [SAND, DOGWOOD, "#dbe9f6", "#f4d6e6"]
    for qd in range(4):
        ax.add_patch(Wedge(x0, 4.2, qd * 90, qd * 90 + 90, fc=cols[qd], ec=BASIN, lw=0.8, alpha=0.8))
        m = np.where((ang >= qd * 90) & (ang < qd * 90 + 90))[0]
        sel[m[np.argsort(d[m])[:2]]] = True
    ax.set_title("Quadrants: 2 nearest in each", fontsize=11, loc="left")
    sets.append(sel)
    # ellipse
    ax = axes[3]
    e = Ellipse(x0, 8.4, 3.2, angle=40, fc=BLUE, alpha=0.12, ec=BLUE, lw=1.4)
    ax.add_patch(e)
    t = np.radians(-40)
    rel = pts - x0
    u = rel[:, 0] * np.cos(t) - rel[:, 1] * np.sin(t)
    v = rel[:, 0] * np.sin(t) + rel[:, 1] * np.cos(t)
    sel = (u / 4.2) ** 2 + (v / 1.6) ** 2 <= 1
    ax.set_title("Ellipse: a directional trend", fontsize=11, loc="left")
    sets.append(sel)
    for ax, sel in zip(axes, sets):
        ax.scatter(*pts[~sel].T, s=30, fc="white", ec=BASIN, lw=1.1, zorder=3)
        ax.scatter(*pts[sel].T, s=30, c=BLUE, ec=NAVY, lw=0.8, zorder=4)
        ax.scatter(*x0, s=90, marker="X", c=CLAY, ec=NAVY, lw=0.6, zorder=5)
        ax.set_xlim(0, 10)
        ax.set_ylim(0, 10)
        ax.set_aspect("equal")
        ax.set_xticks([])
        ax.set_yticks([])
        for s in ax.spines.values():
            s.set_color(CORNER)
    save(fig, OUT / "search-options.png")


# ---------- 8. IDW worked example ----------
def idw_example():
    fig, ax = plt.subplots(figsize=(7.4, 4.6))
    x0 = np.array([4.0, 3.2])
    st = [("Austin", 19, 40, 100), ("San Antonio", 22, 50, 215), ("Houston", 21, 150, 15)]
    scale = 0.05
    for name, t, dist, ang in st:
        a = np.radians(ang)
        r = dist * scale if dist < 100 else 5.6
        p = x0 + r * np.array([np.cos(a), np.sin(a)])
        ax.plot(*np.array([x0, p]).T, color=CORNER, lw=1.4, ls="--", zorder=1)
        ax.scatter(*p, s=110, c=BLUE, ec=NAVY, zorder=3)
        ax.text(p[0], p[1] + 0.35, f"{name}\n{t} °C", ha="center", va="bottom", fontsize=10, color=NAVY)
        mid = (x0 + p) / 2
        ax.text(mid[0], mid[1] - 0.15, f"d = {dist}", fontsize=9.5, color=BASIN, ha="center", va="top",
                bbox=dict(fc="white", ec="none", pad=1))
    ax.scatter(*x0, s=140, marker="X", c=CLAY, ec=NAVY, lw=0.6, zorder=4)
    ax.text(x0[0] + 0.25, x0[1] - 0.35, "?", fontsize=16, color=CLAY, weight="bold", va="top")
    ax.text(5.0, -0.2, "Distances not to scale", fontsize=8.5, color=BASIN, ha="center")
    ax.set_xlim(-0.5, 10.5)
    ax.set_ylim(-0.6, 6.4)
    ax.set_aspect("equal")
    ax.set_axis_off()
    save(fig, OUT / "idw-example.png")
    t = np.array([19, 22, 21])
    d = np.array([40, 50, 150])
    print("idw p1", (t / d).sum(), (1 / d).sum(), (t / d).sum() / (1 / d).sum(),
          "p2", (t / d ** 2).sum() / (1 / d ** 2).sum())


# ---------- 9. power ----------
def idw_power():
    p, z = samples()
    fig, axes = plt.subplots(1, 3, figsize=(13, 4.6))
    for ax, pw in zip(axes, (1, 2, 5)):
        Z = grid_eval(lambda a, b, c: idw(a, b, c, pw), p, z)
        surf(ax, Z, p, f"IDW, power {pw}")
    save(fig, OUT / "idw-power.png")


# ---------- 10. polynomial order (1D) ----------
def poly_order():
    rng = np.random.default_rng(4)
    x = np.linspace(0, 10, 18)
    y = 1 + 2.2 * x - 0.2 * x ** 2 + 0.7 * np.sin(1.2 * x) + rng.normal(0, 0.25, x.size)
    xf = np.linspace(0, 10, 300)
    fig, ax = plt.subplots(figsize=(8.5, 3.8))
    ax.scatter(x, y, s=40, c=NAVY, zorder=5, label="Observations")
    for o, c, ls in [(1, CLAY, "-"), (2, POPLAR, "--"), (3, PINE, "-")]:
        b = np.polyfit(x, y, o)
        lab = {1: "1st order: a straight line (plane)", 2: "2nd order: one bend", 3: "3rd order: two bends"}[o]
        ax.plot(xf, np.polyval(b, xf), color=c, lw=2.2, ls=ls, label=lab)
    ax.set_xlabel("x")
    ax.set_ylabel("Value")
    ax.spines[["top", "right"]].set_visible(False)
    ax.legend(frameon=False, fontsize=9.5, loc="upper left")
    save(fig, OUT / "poly-order.png")


# ---------- 11. methods compared, with cross-validation RMSE ----------
def compare():
    p, z = samples()
    fig, axes = plt.subplots(2, 3, figsize=(13, 9.2))
    surf(axes[0, 0], TRUE, p, "True surface (made up)")
    res = {}
    for ax, (name, f) in zip([axes[0, 1], axes[0, 2], axes[1, 0], axes[1, 1]], METHODS):
        Z = grid_eval(f, p, z)
        rmse, me = loocv(f, p, z)
        res[name] = (rmse, me, np.sqrt(((Z - TRUE) ** 2).mean()))
        surf(ax, Z, p, f"{name}\nCross-validation RMSE = {rmse:.1f}")
    # local polynomial: IDW-weighted first-order fit in a moving window
    ax = axes[1, 2]

    def lp(pp, zz, q):
        out = np.empty(len(q))
        for i, (x, y) in enumerate(q):
            d = np.hypot(pp[:, 0] - x, pp[:, 1] - y)
            w = np.exp(-(d / 2.5) ** 2)
            A = poly_terms(pp[:, 0], pp[:, 1], 1) * np.sqrt(w)[:, None]
            b, *_ = np.linalg.lstsq(A, zz * np.sqrt(w), rcond=None)
            out[i] = (poly_terms(np.array([x]), np.array([y]), 1) @ b)[0]
        return out
    Z = grid_eval(lp, p, z)
    rmse, me = loocv(lp, p, z)
    res["Local polynomial"] = (rmse, me, np.sqrt(((Z - TRUE) ** 2).mean()))
    surf(ax, Z, p, f"Local polynomial (1st order)\nCross-validation RMSE = {rmse:.1f}")
    fig.subplots_adjust(hspace=0.25, wspace=0.08)
    save(fig, OUT / "compare.png")
    print("surface range", VMIN, VMAX, "samples", z.min(), z.max())
    for k, v in res.items():
        print(f"{k}: cv rmse {v[0]:.2f}, mean error {v[1]:.2f}, true rmse {v[2]:.2f}")


# ---------- 12. sampling designs ----------
def sampling():
    rng = np.random.default_rng(21)
    fig, axes = plt.subplots(1, 4, figsize=(14, 3.9))
    g = np.linspace(0.6, 9.4, 6)
    sysp = np.array([(x, y) for x in g for y in g])
    rnd = rng.uniform(0.3, 9.7, (36, 2))
    cents = rng.uniform(1.5, 8.5, (5, 2))
    clu = np.vstack([rng.normal(c, 0.45, (7, 2)) for c in cents])
    # adaptive: coarse grid then add points where the gradient is high
    g2 = np.linspace(1, 9, 4)
    first = np.array([(x, y) for x in g2 for y in g2])
    gy, gx = np.gradient(TRUE, G, G)
    mag = np.hypot(gx, gy)
    cand = rng.uniform(0.3, 9.7, (3000, 2))
    ci = np.clip((cand / 10 * 159).astype(int), 0, 159)
    m = mag[ci[:, 1], ci[:, 0]]
    second = cand[np.argsort(m)[::-1][::40][:20]]
    for ax, pts, t in [(axes[0], [sysp], "Systematic"), (axes[1], [rnd], "Random"),
                       (axes[2], [clu], "Clustered"), (axes[3], [first, second], "Adaptive (two passes)")]:
        ax.imshow(TRUE, origin="lower", extent=(0, 10, 0, 10), cmap=CMAP, vmin=VMIN - 10, vmax=VMAX + 10,
                  alpha=0.55)
        ax.scatter(*pts[0].T, s=20, c="white", ec=NAVY, lw=0.9, zorder=4)
        if len(pts) > 1:
            ax.scatter(*pts[1].T, s=26, marker="^", c=CLAY, ec=NAVY, lw=0.6, zorder=5)
        ax.set_title(t, fontsize=11.5, loc="left")
        ax.set_xlim(0, 10)
        ax.set_ylim(0, 10)
        ax.set_xticks([])
        ax.set_yticks([])
        for s in ax.spines.values():
            s.set_color(CORNER)
    axes[3].text(0.2, -0.9, "▲ second pass, where values change quickly", fontsize=8.5, color=CLAY)
    save(fig, OUT / "sampling.png")


# ---------- 13. cross validation example ----------
def cross_validation():
    pts = {(20, 20): 4, (40, 20): 3, (30, 30): 4, (30, 10): 2, (10, 30): 2, (50, 30): 5}
    # neighbors of the removed point (30, 20) at distance 10: (20,20)=4 and (40,20)=3
    # and at 14.14: (20,30)=4 and (40,10)=2
    pts = {(20, 20): 4, (40, 20): 3, (20, 30): 4, (40, 10): 2}
    removed = (30, 20)
    fig, ax = plt.subplots(figsize=(5.8, 4.4))
    for (x, y), v in pts.items():
        ax.plot([removed[0], x], [removed[1], y], color=CORNER, lw=1.2, ls="--")
        ax.scatter(x, y, s=90, c=BLUE, ec=NAVY, zorder=3)
        d = np.hypot(x - removed[0], y - removed[1])
        ax.text(x + (1.6 if x > 30 else -1.6), y + 1.2, f"{v}", fontsize=12, weight="bold", color=NAVY,
                ha="left" if x > 30 else "right")
        mx, my = (x + removed[0]) / 2, (y + removed[1]) / 2
        off = (0, -0.8) if y == removed[1] else (1.8, 1.8)
        ax.text(mx + off[0], my + off[1], f"{d:.2f}".rstrip("0").rstrip("."), fontsize=9, color=BASIN,
                ha="center", va="center")
    ax.scatter(*removed, s=120, fc="white", ec=CLAY, lw=2, zorder=4)
    ax.text(removed[0] - 1.5, removed[1] - 2.5, "Removed:\nobserved 3.0", fontsize=9.5, color=CLAY,
            ha="right", va="top")
    z = np.array(list(pts.values()), float)
    d = np.array([np.hypot(x - 30, y - 20) for x, y in pts])
    est = (z / d).sum() / (1 / d).sum()
    ax.text(30, 4.5, f"IDW estimate (power 1) = {est:.2f}\nError = {est - 3:.2f}", fontsize=10, color=NAVY,
            ha="center", va="top")
    ax.set_xlim(12, 48)
    ax.set_ylim(0, 35)
    ax.set_aspect("equal")
    ax.set_axis_off()
    save(fig, OUT / "cross-validation.png")
    print("cv example", est)


if __name__ == "__main__":
    ne = Path(sys.argv[1])
    problem()
    exact_inexact()
    profiles()
    thiessen()
    airports(ne)
    average_neighbor()
    search_options()
    idw_example()
    idw_power()
    poly_order()
    compare()
    sampling()
    cross_validation()
