"""Diagrams for the Location and Coordinate Systems chapter
(images/location-and-coordinates/).

Run from the repository root:  python3 scripts/figures/location_coordinates.py NE_DIR
NE_DIR holds Natural Earth GeoJSON (public domain): ne_110m_land.
"""
import sys, os
import numpy as np
sys.path.insert(0, os.path.dirname(__file__))
from style import *  # noqa
import matplotlib.pyplot as plt
from matplotlib.patches import Circle, Ellipse, Arc, FancyArrowPatch, Polygon as MPoly, Wedge
import geopandas as gpd
import cartopy.crs as ccrs

NE = sys.argv[1]
OUT = "images/location-and-coordinates"
land = gpd.read_file(f"{NE}/ne_110m_land.geojson")
PC = ccrs.PlateCarree()


def add_land(ax, fc=LAND, ec="#7A9A6A"):
    ax.add_geometries(land.geometry, crs=PC, facecolor=fc, edgecolor=ec, linewidth=0.4, zorder=1)


def grat(ax, step, lw=0.5, **kw):
    return ax.gridlines(crs=PC, xlocs=np.arange(-180, 181, step), ylocs=np.arange(-90, 91, step),
                        color=BASIN, linewidth=lw, alpha=0.7, **kw)


def arrow(ax, a, b, col=NAVY, lw=1.4, style="-|>", ms=14, **kw):
    ax.add_patch(FancyArrowPatch(a, b, arrowstyle=style, mutation_scale=ms, color=col, lw=lw, **kw))


# --- Eratosthenes ------------------------------------------------------------
def eratosthenes():
    fig, ax = plt.subplots(figsize=(10, 5.8))
    ax.set_aspect("equal"); ax.axis("off")
    R = 3.0
    ang = 20.0  # the real angle, 7.2 degrees, is drawn larger so it is easy to see
    ax.add_patch(Circle((0, 0), R, fc=WATER, ec=NAVY, lw=1.5))
    S = (0, R)
    t = np.radians(90 + ang); A = (R * np.cos(t), R * np.sin(t))
    for x in [0.0, 0.7, 1.4, 2.1]:
        arrow(ax, (x, 6.3), (x, 4.6), col=POPLAR, lw=1.3, ms=11)
    ax.text(2.6, 5.4, "sunlight arrives\nin parallel rays", color="#9A5A00", fontsize=10.5)
    # radii to the two cities
    ax.plot([0, 0], [0, R], color=NAVY, lw=1)
    ax.plot([0, A[0]], [0, A[1]], color=NAVY, lw=1)
    ax.add_patch(Arc((0, 0), 2.0, 2.0, theta1=90, theta2=90 + ang, color=CLAY, lw=2.2))
    ax.text(-0.35, 1.15, "7.2°", color=CLAY, fontsize=12, fontweight="bold", ha="right")
    # a vertical pole at Alexandria, pointing away from the center
    L = 1.3
    top = (A[0] * (1 + L / R), A[1] * (1 + L / R))
    ax.plot([A[0], top[0]], [A[1], top[1]], color=NAVY, lw=3.5, solid_capstyle="round")
    ax.plot([top[0], top[0]], [top[1], top[1] + 1.4], color=POPLAR, lw=1.6)
    ax.plot([top[0], top[0]], [top[1], A[1] - 0.05], color=POPLAR, lw=1.2, ls=":")
    ax.add_patch(Arc(top, 1.6, 1.6, theta1=270 - 0.01, theta2=270 + ang, color=CLAY, lw=2.2))
    ax.add_patch(Arc(top, 1.6, 1.6, theta1=90 + ang, theta2=90, color=CLAY, lw=0))
    ax.text(top[0] + 0.5, top[1] - 0.7, "7.2°", color=CLAY, fontsize=12, fontweight="bold")
    # a well at Syene
    ax.add_patch(plt.Rectangle((-0.15, R - 0.45), 0.3, 0.45, fc="#1F6FA8", ec=NAVY, lw=1, zorder=4))
    ax.plot(*A, "o", color=PINE, ms=8, zorder=5)
    ax.text(0.35, R + 0.15, "Syene: at noon on the solstice, the sun\nshines straight down a well, no shadow", fontsize=10.5)
    ax.text(top[0] - 0.35, top[1] - 0.2, "Alexandria: a vertical pole\ncasts a short shadow", fontsize=10.5, ha="right")
    ax.text(4.0, 0.4, "The pole's shadow angle equals\nthe angle between the two cities\nat Earth's center: 7.2°, or 1/50\nof a full circle. So the Earth's\ncircumference is about 50 times\nthe distance between them.",
            fontsize=10.5, va="center")
    ax.text(0, -R - 0.45, "The angle is drawn larger than 7.2° so you can see it.", ha="center", fontsize=9.5, color=BASIN)
    ax.set_xlim(-6.2, 7.8); ax.set_ylim(-3.6, 6.5)
    save(fig, f"{OUT}/eratosthenes.png")


# --- Sphere and ellipsoid ------------------------------------------------------
def ellipsoid():
    fig, axs = plt.subplots(1, 2, figsize=(10, 4.8))
    for k, ax in enumerate(axs):
        ax.set_aspect("equal"); ax.axis("off"); ax.set_xlim(-3.6, 3.6); ax.set_ylim(-3.2, 3.3)
    ax = axs[0]
    ax.add_patch(Circle((0, 0), 2.6, fc=WATER, ec=NAVY, lw=1.5))
    arrow(ax, (0, 0), (2.6, 0), col=CLAY, style="-|>")
    ax.text(1.3, 0.15, "r", color=CLAY, fontsize=14, fontweight="bold", ha="center")
    ax.set_title("Sphere: one radius everywhere", fontsize=13)
    ax = axs[1]
    a, b = 2.9, 2.2  # flattening exaggerated
    ax.add_patch(Ellipse((0, 0), 2 * a, 2 * b, fc=WATER, ec=NAVY, lw=1.5))
    ax.add_patch(Circle((0, 0), 2.6, fc="none", ec=BASIN, lw=0.8, ls=":"))
    arrow(ax, (0, 0), (a, 0), col=CLAY); arrow(ax, (0, 0), (0, b), col=PINE)
    ax.text(a / 2, 0.15, "a", color=CLAY, fontsize=14, fontweight="bold", ha="center")
    ax.text(0.15, b / 2, "b", color=PINE, fontsize=14, fontweight="bold")
    ax.text(a + 0.1, -0.45, "equator", fontsize=10, ha="right")
    ax.text(0, b + 0.15, "North Pole", fontsize=10, ha="center")
    ax.text(0, -b - 0.45, "flattening  f = (a − b) / a", fontsize=11.5, ha="center")
    ax.plot([0, 0], [-b, b], color=BASIN, lw=0.8, ls="--")
    ax.set_title("Ellipsoid: wider at the equator", fontsize=13)
    fig.text(0.5, 0.0, "Flattening is exaggerated. On the real Earth, a is only about 21 km longer than b.",
             ha="center", fontsize=10.5, color=BASIN)
    save(fig, f"{OUT}/sphere-ellipsoid.png")


# --- Geoid, ellipsoid and three heights --------------------------------------
def heights():
    fig, ax = plt.subplots(figsize=(10, 5.2))
    ax.axis("off")
    x = np.linspace(0, 10, 400)
    ell = 0.55 + 0 * x
    geoid = 1.65 + 0.35 * np.sin(x * 0.7 + 0.5) + 0.12 * np.sin(x * 2.1)
    terr = geoid + np.clip(3.2 * np.exp(-((x - 5.6) / 1.6) ** 2) + 0.4 * np.exp(-((x - 2.5) / 1.0) ** 2) - 0.15, -0.3, None)
    ax.fill_between(x, -0.2, terr, color="#C8B79A", zorder=1)
    ax.fill_between(x, -0.2, np.minimum(terr, geoid), where=terr < geoid, color=WATER, zorder=2)
    ax.plot(x, terr, color="#7B6A4F", lw=1.5, zorder=3)
    ax.plot(x, geoid, color=BLUE, lw=2.5, ls="--", zorder=4)
    ax.plot(x, ell, color=DUSK, lw=2.5, zorder=4)
    ax.text(9.95, geoid[-1] + 0.12, "geoid (about mean sea level)", ha="right", color="#1F6FA8", fontsize=11, fontweight="bold")
    ax.text(9.95, 0.27, "ellipsoid (smooth model)", ha="right", color=DUSK, fontsize=11, fontweight="bold")
    ax.text(8.6, 2.6, "Earth's surface", color="#7B6A4F", fontsize=11, fontweight="bold")
    i = np.argmin(abs(x - 5.6)); xp = x[i]
    ax.plot(xp, terr[i], "o", color=CLAY, ms=9, zorder=6)
    ax.text(xp + 0.1, terr[i] + 0.15, "a point on the ground", fontsize=10.5, zorder=6)
    for dx, y0, y1, lab, col in [(-0.75, ell[i], terr[i], "h", DUSK), (0.35, geoid[i], terr[i], "H", "#1F6FA8"),
                                 (0.35, ell[i], geoid[i], "N", PINE)]:
        arrow(ax, (xp + dx, y0), (xp + dx, y1), col=col, style="<|-|>", ms=12, lw=1.6)
        ax.text(xp + dx + (0.12 if dx > 0 else -0.12), (y0 + y1) / 2, lab, color=col, fontsize=15, fontweight="bold",
                ha="left" if dx > 0 else "right", va="center", zorder=7)
    ax.text(0.1, 4.9, "h = ellipsoid height (what GPS reports)\nH = orthometric height (elevation above the geoid)\n"
            "N = geoid height (gap between the two)\n\nh = H + N", fontsize=11, va="top")
    ax.set_xlim(0, 10); ax.set_ylim(-0.2, 5.0)
    save(fig, f"{OUT}/three-heights.png")


# --- Datum shift ---------------------------------------------------------------
def datum_shift():
    fig, ax = plt.subplots(figsize=(9, 5.6))
    ax.set_aspect("equal"); ax.axis("off")
    # Earth's irregular surface
    t = np.linspace(0, 2 * np.pi, 400)
    r = 3 + 0.08 * np.sin(5 * t) + 0.05 * np.cos(9 * t)
    ax.fill(r * np.cos(t), r * np.sin(t), color="#E9E2D3", ec="#7B6A4F", lw=1.2)
    ax.text(0, -2.4, "the real Earth", ha="center", color="#7B6A4F", fontsize=11, fontweight="bold")
    e1 = Ellipse((0, 0), 6.1, 5.9, fc="none", ec=PINE, lw=2)
    e2 = Ellipse((0.45, 0.3), 6.0, 5.75, fc="none", ec=CLAY, lw=2, ls="--")
    ax.add_patch(e1); ax.add_patch(e2)
    lat = np.radians(40)
    for (cx, cy, a, b, col, name) in [(0, 0, 3.05, 2.95, PINE, "Datum 1 (earth-centered,\nlike NAD83)"),
                                      (0.45, 0.3, 3.0, 2.875, CLAY, "Datum 2 (fitted to one\nregion, like NAD27)")]:
        px, py = cx + a * np.cos(lat), cy + b * np.sin(lat)
        ax.plot([cx, px], [cy, py], color=col, lw=1.2)
        ax.plot(cx, cy, "+", color=col, ms=12, mew=2)
        ax.plot(px, py, "o", color=col, ms=9, zorder=5)
    ax.text(-4.9, 2.7, "Datum 1: earth-centered,\nlike NAD83 or WGS84", color=PINE, fontsize=10.5, fontweight="bold")
    ax.text(-4.9, -3.4, "Datum 2: fitted to one region,\nlike NAD27", color=CLAY, fontsize=10.5, fontweight="bold")
    ax.annotate("same latitude and longitude,\ntwo different places on the ground", (2.6, 2.2), (3.4, 3.4), fontsize=10.5,
                arrowprops=dict(arrowstyle="->", color=NAVY))
    ax.set_xlim(-5, 6.5); ax.set_ylim(-3.6, 4.2)
    save(fig, f"{OUT}/datum-shift.png")


# --- Latitude and longitude as angles -------------------------------------------
def latlon():
    fig = plt.figure(figsize=(11, 5.2))
    ax = fig.add_axes([0.0, 0.0, 0.48, 0.92]); ax.set_aspect("equal"); ax.axis("off")
    R = 2.6
    ax.add_patch(Circle((0, 0), R, fc=WATER, ec=NAVY, lw=1.5))
    ax.plot([-R, R], [0, 0], color=NAVY, lw=1.2, ls="--")
    ax.text(-R + 0.1, 0.12, "equator (0°)", fontsize=10)
    lat = np.radians(35.9)
    P = (R * np.cos(lat), R * np.sin(lat))
    ax.plot([0, P[0]], [0, P[1]], color=CLAY, lw=1.8)
    ax.plot(*P, "o", color=CLAY, ms=9)
    ax.add_patch(Arc((0, 0), 1.8, 1.8, theta1=0, theta2=35.9, color=CLAY, lw=2))
    ax.text(1.0, 0.25, "latitude\n35.9° N", color=CLAY, fontsize=11, fontweight="bold")
    ax.text(P[0] + 0.12, P[1] + 0.1, "Chapel Hill", fontsize=10.5)
    ax.plot([0, 0], [-R - 0.3, R + 0.3], color=BASIN, lw=0.8)
    ax.text(0, R + 0.4, "North Pole (90° N)", ha="center", fontsize=10)
    ax.text(0, -R - 0.65, "South Pole (90° S)", ha="center", fontsize=10)
    ax.set_title("Latitude: the angle north or south\nof the equator, seen from the side", fontsize=12.5)
    ax.set_xlim(-3.3, 3.6); ax.set_ylim(-3.3, 3.6)
    ax = fig.add_axes([0.5, 0.0, 0.48, 0.92]); ax.set_aspect("equal"); ax.axis("off")
    ax.add_patch(Circle((0, 0), R, fc=WATER, ec=NAVY, lw=1.5))
    ax.text(0.15, 0.2, "North Pole", ha="left", fontsize=10)
    ax.plot(0, 0, "o", color=NAVY, ms=4)
    # looking down from above the North Pole, Greenwich at bottom, east counterclockwise
    g = np.radians(-90)
    ax.plot([0, R * np.cos(g)], [0, R * np.sin(g)], color=NAVY, lw=1.8)
    ax.text(0.1, -R - 0.35, "prime meridian (0°), Greenwich", ha="center", fontsize=10)
    lon = np.radians(-90 - 79.05)
    Q = (R * np.cos(lon), R * np.sin(lon))
    ax.plot([0, Q[0]], [0, Q[1]], color=PINE, lw=1.8)
    ax.plot(*Q, "o", color=PINE, ms=9)
    ax.add_patch(Arc((0, 0), 1.8, 1.8, theta1=np.degrees(lon), theta2=-90, color=PINE, lw=2))
    ax.text(-1.5, -0.95, "longitude\n79.05° W", color=PINE, fontsize=11, fontweight="bold")
    ax.text(Q[0] - 0.1, Q[1] + 0.2, "Chapel Hill", fontsize=10.5, ha="right")
    ax.set_title("Longitude: the angle east or west of the\nprime meridian, seen from above the pole", fontsize=12.5)
    ax.set_xlim(-3.3, 3.6); ax.set_ylim(-3.3, 3.6)
    save(fig, f"{OUT}/latitude-longitude.png")


# --- Parallels and meridians on a globe -----------------------------------------
def graticule_globe():
    fig = plt.figure(figsize=(10, 5))
    for k, (title, xl, yl, col) in enumerate([("Parallels: lines of latitude", [], np.arange(-75, 90, 15), CLAY),
                                              ("Meridians: lines of longitude", np.arange(-180, 180, 15), [], PINE)]):
        ax = fig.add_subplot(1, 2, k + 1, projection=ccrs.Orthographic(-40, 25))
        ax.set_global()
        add_land(ax, fc="#E5ECD9", ec="#B7C6A6")
        ax.gridlines(crs=PC, xlocs=xl if len(xl) else [], ylocs=yl if len(yl) else [], color=col, linewidth=1.0)
        if k == 0:
            ax.gridlines(crs=PC, xlocs=[], ylocs=[0], color=CLAY, linewidth=2.6)
            ax.text(-60, 2, "Equator 0°", transform=PC, fontsize=10.5, fontweight="bold", color=CLAY)
        else:
            ax.gridlines(crs=PC, xlocs=[0], ylocs=[], color=PINE, linewidth=2.6)
            ax.text(2, 10, "Prime\nMeridian 0°", transform=PC, fontsize=10.5, fontweight="bold", color=PINE)
        ax.spines["geo"].set_edgecolor(NAVY)
        ax.set_title(title, fontsize=13)
    save(fig, f"{OUT}/parallels-meridians.png")


# --- Great circle ------------------------------------------------------------------
def great_circle():
    tokyo = (139.69, 35.69); adel = (138.60, -34.93)
    ny = (-73.78, 40.64); lon_ = (-0.45, 51.47)
    fig = plt.figure(figsize=(11, 5))
    for k, (title, p) in enumerate([("On a flat Plate Carrée map", ccrs.PlateCarree()),
                                    ("On the globe", ccrs.Orthographic(-35, 45))]):
        ax = fig.add_subplot(1, 2, k + 1, projection=p)
        if k == 0:
            ax.set_extent([-100, 30, 20, 75], crs=PC)
        else:
            ax.set_global()
        add_land(ax)
        grat(ax, 15, lw=0.4)
        from pyproj import Geod
        pts = np.array(Geod(ellps="WGS84").npts(ny[0], ny[1], lon_[0], lon_[1], 200))
        gx = np.r_[ny[0], pts[:, 0], lon_[0]]; gy = np.r_[ny[1], pts[:, 1], lon_[1]]
        ax.plot(gx, gy, transform=PC, color=CLAY, lw=2.5, zorder=3)
        ax.plot(np.linspace(ny[0], lon_[0], 200), np.linspace(ny[1], lon_[1], 200), transform=PC, color=NAVY, lw=1.6,
                ls="--", zorder=3)
        for (x, y), n in [(ny, "New York"), (lon_, "London")]:
            ax.plot(x, y, "o", color=NAVY, ms=6, transform=PC, zorder=4)
            ax.text(x + 2, y - 4, n, transform=PC, fontsize=10.5, zorder=4)
        ax.spines["geo"].set_edgecolor(NAVY)
        ax.set_title(title, fontsize=13)
    fig.text(0.5, 0.03, "Solid red: the great-circle route, the shortest path (about 5,560 km).   "
             "Dashed: a straight line on the flat map, about 5,790 km.", ha="center", fontsize=10.5)
    save(fig, f"{OUT}/great-circle.png")


# --- Graticule spacing --------------------------------------------------------------
def graticule_spacing():
    fig = plt.figure(figsize=(11, 2.9))
    for k, step in enumerate([5, 15, 30]):
        ax = fig.add_subplot(1, 3, k + 1, projection=ccrs.Robinson())
        ax.set_global()
        add_land(ax)
        grat(ax, step, lw=0.5 if step > 5 else 0.35)
        ax.spines["geo"].set_edgecolor(NAVY)
        ax.set_title(f"Every {step}°", fontsize=13)
    save(fig, f"{OUT}/graticule-spacing.png")


# --- Plate Carrée ----------------------------------------------------------------------
def plate_carree():
    fig = plt.figure(figsize=(11, 4.4))
    ax = fig.add_axes([0.0, 0.05, 0.33, 0.85], projection=ccrs.Orthographic(-30, 30))
    ax.set_global(); add_land(ax); grat(ax, 15, lw=0.5)
    ax.tissot(rad_km=700, lons=[-30, -30, -30, 30, 0], lats=[0, 30, 60, 60, 30], n_samples=60, facecolor=CLAY, alpha=0.7, zorder=3)
    ax.spines["geo"].set_edgecolor(NAVY); ax.set_title("On the globe", fontsize=13)
    ax = fig.add_axes([0.36, 0.05, 0.63, 0.85], projection=ccrs.PlateCarree())
    ax.set_global(); add_land(ax); grat(ax, 15, lw=0.5)
    ax.tissot(rad_km=700, lons=[-30, -30, -30, 30, 0], lats=[0, 30, 60, 60, 30], n_samples=60, facecolor=CLAY, alpha=0.7, zorder=3)
    ax.spines["geo"].set_edgecolor(NAVY)
    ax.set_title("Plate Carrée: longitude as x, latitude as y", fontsize=13)
    save(fig, f"{OUT}/plate-carree.png")


if __name__ == "__main__":
    which = sys.argv[2:] or ["eratosthenes", "ellipsoid", "heights", "datum_shift", "latlon", "graticule_globe",
                             "great_circle", "graticule_spacing", "plate_carree"]
    for w in which:
        globals()[w]()
