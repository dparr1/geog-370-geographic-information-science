"""Diagrams for the Map Projections chapter (images/map-projections/).

Run from the repository root:  python3 scripts/figures/map_projections.py NE_DIR
NE_DIR holds Natural Earth GeoJSON (public domain) from
https://github.com/nvkelso/natural-earth-vector/tree/master/geojson :
ne_110m_land, ne_50m_land, ne_50m_admin_0_countries,
ne_50m_admin_1_states_provinces_lakes.
Needs matplotlib, numpy, shapely, geopandas, pyproj and cartopy.
"""
import sys, os
import numpy as np
sys.path.insert(0, os.path.dirname(__file__))
from style import *  # noqa
import matplotlib.pyplot as plt
from matplotlib.patches import Circle, Ellipse, Polygon as MPoly, FancyBboxPatch, FancyArrowPatch, Rectangle
import geopandas as gpd
import cartopy.crs as ccrs
from pyproj import Proj, Transformer
from shapely.geometry import box
from shapely.ops import transform as stransform

NE = sys.argv[1]
OUT = "images/map-projections"
land110 = gpd.read_file(f"{NE}/ne_110m_land.geojson")
land50 = gpd.read_file(f"{NE}/ne_50m_land.geojson")
countries = gpd.read_file(f"{NE}/ne_50m_admin_0_countries.geojson")
states = gpd.read_file(f"{NE}/ne_50m_admin_1_states_provinces_lakes.geojson")
us = states[states["adm0_a3"] == "USA"]
conus = us[~us["name"].isin(["Alaska", "Hawaii"])]
nc = us[us["name"] == "North Carolina"]
PC = ccrs.PlateCarree()


def add_land(ax, gdf=land110, fc=LAND, ec="#7A9A6A", lw=0.4):
    ax.add_geometries(gdf.geometry, crs=PC, facecolor=fc, edgecolor=ec, linewidth=lw, zorder=1)


def grat(ax, step=30, **kw):
    g = ax.gridlines(crs=PC, xlocs=np.arange(-180, 181, step), ylocs=np.arange(-90, 91, step),
                     color=BASIN, linewidth=0.4, alpha=0.6, draw_labels=False, **kw)
    return g


def outline(ax):
    ax.spines["geo"].set_edgecolor(NAVY)
    ax.spines["geo"].set_linewidth(0.8)


# --- 1. From Earth to a map: the four layers ------------------------------
def pyramid():
    fig, ax = plt.subplots(figsize=(8.6, 4.4))
    ax.set_xlim(0, 10); ax.set_ylim(0, 5.2); ax.axis("off")
    layers = [
        ("Earth", "The real, irregular surface.\nThe geoid approximates mean sea level.", BASIN, 4.2),
        ("Ellipsoid", "A smooth mathematical shape\nthat fits the Earth, such as GRS 80.", DUSK, 3.6),
        ("Datum", "Pins the ellipsoid to the Earth and defines\nlatitude and longitude, such as NAD83.", PINE, 3.0),
        ("Map projection", "Turns latitude and longitude into\nflat x, y coordinates, such as UTM.", NAVY, 2.4),
    ]
    for i, (name, desc, col, w) in enumerate(layers):
        y = 0.3 + i * 1.18
        ax.add_patch(FancyBboxPatch((2.6 - w / 2, y), w, 0.95, boxstyle="round,pad=0.02,rounding_size=0.08",
                                    fc=col, ec="none"))
        ax.text(2.6, y + 0.47, name, ha="center", va="center", color="white", fontsize=14, fontweight="bold")
        ax.text(5.3, y + 0.47, desc, ha="left", va="center", fontsize=11.5)
    ax.add_patch(FancyArrowPatch((-0.1, 0.4), (-0.1, 4.9), arrowstyle="-|>", mutation_scale=18, color=PINE, lw=2))
    ax.set_xlim(-0.9, 10)
    ax.text(-0.5, 2.6, "Each layer is built\non the one below", rotation=90, va="center", ha="center", fontsize=10, color=PINE)
    save(fig, f"{OUT}/building-a-projection.png")


# --- 2. The light-bulb picture of a projection ----------------------------
def light():
    fig, ax = plt.subplots(figsize=(8, 5.4))
    ax.set_aspect("equal"); ax.axis("off")
    R = 2.0
    ax.add_patch(Circle((0, 0), R, fc=WATER, ec=NAVY, lw=1.5, zorder=1))
    # the map plane, tangent at the top
    ax.plot([-6.2, 6.2], [R, R], color=NAVY, lw=2.5, zorder=3)
    ax.text(6.25, R + 0.12, "map plane", ha="right", va="bottom", fontsize=11, fontweight="bold")
    ax.add_patch(Circle((0, 0), 0.16, fc=GINKGO, ec=NAVY, lw=1, zorder=5))
    ax.text(0, -0.42, "light source", ha="center", fontsize=10)
    angles = np.radians([0, 15, 30, 45, 60, 70])
    for s in (-1, 1):
        for k, a in enumerate(angles):
            px, py = R * np.sin(s * a), R * np.cos(a)
            mx = R * np.tan(s * a)
            ax.plot([0, mx], [0, R], color=POPLAR, lw=0.9, alpha=0.9, zorder=2)
            ax.plot(px, py, "o", ms=6, color=PINE, zorder=4)
            ax.plot(mx, R, "o", ms=7, color=CLAY, mec=NAVY, mew=0.6, zorder=4)
    ax.annotate("point of tangency:\nno distortion", (0, R), (-1.3, 3.55), ha="center", fontsize=10,
                arrowprops=dict(arrowstyle="->", color=NAVY))
    ax.annotate("points equally spaced\non the globe", (R * np.sin(np.radians(45)), R * np.cos(np.radians(45))),
                (3.2, -0.6), ha="center", fontsize=10, color=PINE, arrowprops=dict(arrowstyle="->", color=PINE))
    ax.annotate("spread farther apart\non the map", (R * np.tan(np.radians(60)), R), (4.4, 3.4), ha="center",
                fontsize=10, color=CLAY, arrowprops=dict(arrowstyle="->", color=CLAY))
    ax.set_xlim(-6.3, 6.3); ax.set_ylim(-2.3, 4.0)
    save(fig, f"{OUT}/light-source.png")


# --- 3. Three developable surfaces ----------------------------------------
def surfaces():
    fig = plt.figure(figsize=(11, 7.2))
    # top row: sketches
    names = ["Planar (azimuthal)", "Cylindrical", "Conic"]
    for i in range(3):
        ax = fig.add_axes([0.02 + i * 0.33, 0.47, 0.3, 0.48]); ax.set_aspect("equal"); ax.axis("off")
        ax.set_xlim(-2.2, 2.2); ax.set_ylim(-2.2, 2.6)
        ax.set_title(names[i], fontsize=14)
        globe = dict(fc=WATER, ec=NAVY, lw=1.2)
        if i == 0:
            ax.add_patch(Circle((0, 0), 1.3, **globe, zorder=2))
            ax.add_patch(Ellipse((0, 0), 2.6, 0.6, fc="none", ec=BASIN, lw=0.6, ls="--", zorder=3))
            ax.add_patch(MPoly([[-1.8, 1.3], [1.0, 1.3], [1.8, 1.75], [-1.0, 1.75]], closed=True,
                               fc=SAND, ec=POPLAR, lw=1.5, alpha=0.85, zorder=4))
            ax.plot(0.0, 1.3, "o", color=CLAY, zorder=5)
            ax.text(0.25, 2.0, "touches at one point", fontsize=10, ha="center")
        elif i == 1:
            ax.add_patch(Rectangle((-1.3, -1.7), 2.6, 3.4, fc=SAND, ec="none", alpha=0.85, zorder=1))
            ax.add_patch(Circle((0, 0), 1.3, **globe, zorder=2))
            ax.add_patch(Ellipse((0, 0), 2.6, 0.6, fc="none", ec=CLAY, lw=2, zorder=4))
            ax.add_patch(Ellipse((0, 1.7), 2.6, 0.6, fc=SAND, ec=POPLAR, lw=1.5, zorder=3))
            ax.add_patch(Ellipse((0, -1.7), 2.6, 0.6, fc="none", ec=POPLAR, lw=1.5, zorder=3, alpha=0.9))
            ax.plot([-1.3, -1.3], [-1.7, 1.7], color=POPLAR, lw=1.5, zorder=3)
            ax.plot([1.3, 1.3], [-1.7, 1.7], color=POPLAR, lw=1.5, zorder=3)
            ax.text(0, -2.2, "touches along the equator", fontsize=10, ha="center")
        else:
            ax.add_patch(Circle((0, 0), 1.3, **globe, zorder=2))
            apex = (0, 2.5)
            yb = 0.4
            ax.add_patch(MPoly([apex, [-1.75, yb], [1.75, yb]], closed=True, fc=SAND, ec=POPLAR, lw=1.5,
                               alpha=0.85, zorder=3))
            ax.add_patch(Ellipse((0, yb), 3.5, 0.6, fc=SAND, ec=POPLAR, lw=1.5, zorder=3, alpha=0.9))
            ax.add_patch(Ellipse((0, 0.83), 2.24, 0.45, fc="none", ec=CLAY, lw=2, zorder=4))
            ax.text(0, -2.0, "touches along a parallel", fontsize=10, ha="center")
    # bottom row: the unrolled maps, drawn with real projections
    projs = [ccrs.AzimuthalEquidistant(central_latitude=90),
             ccrs.Mercator(min_latitude=-78, max_latitude=80),
             ccrs.LambertConformal(central_longitude=0, standard_parallels=(30, 60), cutoff=-10)]
    for i, p in enumerate(projs):
        ax = fig.add_axes([0.03 + i * 0.33, 0.04, 0.28, 0.36], projection=p)
        if i == 0:
            ax.set_extent([-180, 180, 10, 90], crs=PC)
            import matplotlib.path as mpath
            t = np.linspace(0, 2 * np.pi, 200)
            ax.set_boundary(mpath.Path(np.c_[np.sin(t), np.cos(t)] * 0.5 + 0.5), transform=ax.transAxes)
        else:
            ax.set_global()
        add_land(ax)
        grat(ax, 30)
        outline(ax)
    fig.text(0.5, 0.42, "Unrolled flat, each surface becomes a map", ha="center", fontsize=12, fontweight="bold", color=PINE)
    save(fig, f"{OUT}/developable-surfaces.png")


# --- 4. Tangent and secant -------------------------------------------------
def secant():
    fig, axs = plt.subplots(1, 2, figsize=(11, 5))
    R = 3.0
    th = np.linspace(-1.15, 1.15, 200)
    for k, ax in enumerate(axs):
        ax.set_aspect("equal"); ax.axis("off")
        ax.plot(R * np.sin(th), R * np.cos(th), color=NAVY, lw=2)
        ax.plot(0, 0, "o", color=NAVY, ms=4)
        c = R if k == 0 else R * 0.8
        ax.plot([-4.6, 4.6], [c, c], color=POPLAR, lw=3, solid_capstyle="round")
        ax.text(4.65, c, "map\nsurface", va="center", fontsize=10, color=POPLAR, fontweight="bold")
        ax.text(-3.4, 0.6, "Earth's\nsurface", fontsize=10, ha="center")
        if k == 0:
            ax.set_title("Tangent: touches at one place", fontsize=13)
            ax.plot(0, R, "o", color=CLAY, ms=9, zorder=5)
            ax.annotate("standard point or line:\nscale is exact", (0, R), (0, 1.4), ha="center", fontsize=10,
                        arrowprops=dict(arrowstyle="->", color=CLAY), color=CLAY)
        else:
            ax.set_title("Secant: cuts through in two places", fontsize=13)
            a0 = np.arccos(0.8)
            for s in (-1, 1):
                ax.plot(s * R * np.sin(a0), c, "o", color=CLAY, ms=9, zorder=5)
            ax.text(0, 3.35, "standard lines: scale is exact", ha="center", fontsize=10, color=CLAY)
            for s in (-1, 1):
                ax.annotate("", (s * R * np.sin(a0), c - 0.05), (s * 0.9, 3.3), arrowprops=dict(arrowstyle="->", color=CLAY))
            # between: AB -> ab ; outside: DE -> de
            for (t1, t2, L1, L2, col) in [(0.12, 0.45, "A", "B", PINE), (0.8, 1.02, "D", "E", DUSK)]:
                for t, L in ((t1, L1), (t2, L2)):
                    px, py = R * np.sin(t), R * np.cos(t)
                    mx = c * np.tan(t)
                    ax.plot([0, max(px, mx) / np.sin(t) * np.sin(t) if False else (px if py > c else mx)],
                            [0, (py if py > c else c)], color=BASIN, lw=0.6, ls=":")
                    ax.plot(px, py, "o", color=col, ms=5)
                    ax.plot(mx, c, "s", color=col, ms=5)
                    inside = py > c
                    ax.text(px + 0.08, py + (0.12 if inside else -0.38), L, fontsize=11, fontweight="bold", color=col)
                    ax.text(mx - 0.08, c + (-0.38 if inside else 0.14), L.lower(), fontsize=11, fontweight="bold", color=col)
            ax.text(-4.6, -0.2, "Between the standard lines,\nab is shorter than AB.\nOutside them, de is longer than DE.",
                    fontsize=10.5, va="top")
        ax.set_xlim(-4.7, 5.6); ax.set_ylim(-1.6, 3.7)
    save(fig, f"{OUT}/tangent-secant.png")


# --- 5. Four properties, four projections, with Tissot circles -------------
def tissot_grid():
    lons = np.arange(-150, 181, 30)
    lats = np.arange(-60, 61, 30)
    chapel = (-79.05, 35.91)
    specs = [
        ("Mercator: conformal", ccrs.Mercator(min_latitude=-80, max_latitude=84), "Circles stay round, but grow toward the poles."),
        ("Mollweide: equal-area", ccrs.Mollweide(), "Every circle covers the same area, but they stretch."),
        ("Azimuthal equidistant", ccrs.AzimuthalEquidistant(*chapel), "Distances from Chapel Hill (center) are true."),
        ("Robinson: compromise", ccrs.Robinson(), "Nothing exact; every error is kept moderate."),
    ]
    fig = plt.figure(figsize=(11, 7.6))
    for i, (title, p, sub) in enumerate(specs):
        ax = fig.add_subplot(2, 2, i + 1, projection=p)
        ax.set_global()
        ax.add_feature  # noqa
        add_land(ax)
        grat(ax, 30)
        lo, la = np.meshgrid(lons, lats)
        if i == 2:
            ax.tissot(rad_km=500, lons=lo.ravel(), lats=la.ravel(), n_samples=60, facecolor=CLAY, alpha=0.6, zorder=3)
            ax.plot(*chapel, "*", color=GINKGO, mec=NAVY, ms=14, transform=PC, zorder=5)
        else:
            ax.tissot(rad_km=500, lons=lo.ravel(), lats=la.ravel(), n_samples=60, facecolor=CLAY, alpha=0.6, zorder=3)
        outline(ax)
        ax.set_title(title, fontsize=13)
        ax.text(0.5, -0.07, sub, transform=ax.transAxes, ha="center", fontsize=10.5, color=BASIN)
    fig.subplots_adjust(hspace=0.32, wspace=0.06)
    save(fig, f"{OUT}/four-projections.png")


# --- 6. Greenland at its true size, moved to the equator -------------------
def greenland():
    g = countries[countries["ADMIN"] == "Greenland"].geometry.iloc[0]
    c = g.centroid
    src = Transformer.from_crs("EPSG:4326", f"+proj=laea +lat_0={c.y} +lon_0={c.x} +datum=WGS84", always_xy=True)
    tgt_lat, tgt_lon = 2.0, 20.0
    dst = Transformer.from_crs(f"+proj=laea +lat_0={tgt_lat} +lon_0={tgt_lon} +datum=WGS84", "EPSG:4326", always_xy=True)
    flat = stransform(lambda x, y, z=None: src.transform(x, y), g)
    moved = stransform(lambda x, y, z=None: dst.transform(x, y), flat)
    afr = countries[countries["CONTINENT"] == "Africa"].dissolve().geometry.iloc[0]
    fig = plt.figure(figsize=(11, 5.6))
    for i, (p, title) in enumerate([(ccrs.Mercator(min_latitude=-60, max_latitude=84), "On a Mercator map"),
                                    (ccrs.Mollweide(central_longitude=0), "At true size (equal-area)")]):
        ax = fig.add_subplot(1, 2, i + 1, projection=p)
        ax.set_extent([-75, 60, -40, 84], crs=PC)
        add_land(ax, land50, fc=FOG, ec=CORNER)
        ax.add_geometries([afr], crs=PC, fc=DOGWOOD, ec=PINE, lw=0.6, zorder=2)
        ax.add_geometries([g], crs=PC, fc=BLUE, ec=NAVY, lw=0.6, zorder=3)
        ax.add_geometries([moved], crs=PC, fc=(0.91, 0.33, 0.31, 0.25), ec=CLAY, lw=1.6, ls="--", zorder=4)
        grat(ax, 20)
        outline(ax)
        ax.set_title(title, fontsize=13)
        ax.text(-20, 80, "Greenland", transform=PC, fontsize=10, fontweight="bold", ha="center", zorder=5)
        ax.text(22, -15, "Africa", transform=PC, fontsize=11, fontweight="bold", ha="center", color=PINE, zorder=5)
    fig.text(0.5, 0.02, "Dashed red outline: Greenland at its true size, moved to the equator over Africa.",
             ha="center", fontsize=10.5, color=CLAY)
    save(fig, f"{OUT}/greenland-africa.png")


# --- 7. Scale error across the United States: LCC and TM ------------------
def scale_error():
    cases = [
        ("Lambert Conformal Conic", "+proj=lcc +lat_1=33 +lat_2=45 +lat_0=39 +lon_0=-96 +datum=NAD83",
         "standard parallels at 33° N and 45° N"),
        ("Transverse Mercator", "+proj=tmerc +lat_0=39 +lon_0=-96 +k_0=0.99 +datum=NAD83",
         "central meridian 96° W, two lines of true scale"),
    ]
    lon = np.linspace(-128, -64, 260); lat = np.linspace(22, 52, 160)
    LO, LA = np.meshgrid(lon, lat)
    fig = plt.figure(figsize=(11.5, 4.6))
    levels = [-1.5, -1, -0.5, 0, 0.5, 1, 2, 3, 4, 6]
    for i, (title, p4, sub) in enumerate(cases):
        P = Proj(p4)
        f = P.get_factors(LO, LA)
        err = (np.asarray(f.meridional_scale) - 1) * 100
        crs = ccrs.Projection(p4) if False else None
        ax = fig.add_subplot(1, 2, i + 1, projection=ccrs.LambertConformal(central_longitude=-96, standard_parallels=(33, 45))
                             if i == 0 else ccrs.TransverseMercator(central_longitude=-96, central_latitude=39, scale_factor=0.99))
        ax.set_extent([-121, -71, 23, 50], crs=PC)
        ax.add_geometries(conus.geometry, crs=PC, fc=FOG, ec=BASIN, lw=0.4, zorder=1)
        cf = ax.contourf(LO, LA, err, levels=levels, transform=PC, cmap="RdBu_r", norm=plt.matplotlib.colors.TwoSlopeNorm(0, -1.5, 6),
                         alpha=0.45, zorder=2)
        cs = ax.contour(LO, LA, err, levels=([-0.5, 0, 0.5, 1, 2, 3] if i == 0 else [-0.5, 0, 1, 3]), transform=PC, colors=NAVY, linewidths=0.8, zorder=3)
        ax.clabel(cs, fmt=lambda v: f"{v:+g}%" if v else "0%", fontsize=8.5)
        outline(ax)
        ax.set_title(title, fontsize=13)
        ax.text(0.5, -0.08, sub, transform=ax.transAxes, ha="center", fontsize=10.5, color=BASIN)
    save(fig, f"{OUT}/scale-error.png")


# --- 8. UTM zones over the United States ------------------------------------
def utm():
    fig = plt.figure(figsize=(10.5, 6))
    ax = fig.add_subplot(projection=ccrs.AlbersEqualArea(central_longitude=-96, standard_parallels=(29.5, 45.5)))
    ax.set_extent([-125, -66, 23, 50], crs=PC)
    ax.add_geometries(conus.geometry, crs=PC, fc=FOG, ec=BASIN, lw=0.4, zorder=1)
    ax.add_geometries(nc.geometry, crs=PC, fc=DOGWOOD, ec=PINE, lw=1, zorder=2)
    lat = np.linspace(22, 49.5, 50)
    for z in range(10, 20):
        w = -180 + (z - 1) * 6
        ax.plot([w] * 50, lat, transform=PC, color=NAVY, lw=1.2, zorder=3)
        ax.plot([w + 3] * 50, lat, transform=PC, color=CLAY, lw=0.8, ls="--", zorder=3)
        ax.text(w + 3, 49.7, str(z), transform=PC, ha="center", va="bottom", fontsize=12, fontweight="bold", zorder=4)
    ax.plot([-66] * 50, lat, transform=PC, color=NAVY, lw=1.2, zorder=3)
    ax.text(-96, 22.6, "Zone boundaries every 6° of longitude (solid); central meridians (dashed red)",
            transform=PC, ha="center", fontsize=10, color=BASIN)
    ax.text(-79.2, 33.6, "NC", transform=PC, fontsize=10, fontweight="bold", color=PINE, ha="center")
    outline(ax)
    save(fig, f"{OUT}/utm-zones.png")


# --- 9. North Carolina: two UTM zones, one State Plane zone -----------------
def nc_zones():
    sp = "+proj=lcc +lat_1=34.333333 +lat_2=36.166667 +lat_0=33.75 +lon_0=-79 +x_0=609601.22 +datum=NAD83"
    fig = plt.figure(figsize=(11, 5))
    ax = fig.add_subplot(projection=ccrs.LambertConformal(central_longitude=-79, central_latitude=33.75,
                                                          standard_parallels=(34.333333, 36.166667)))
    ax.set_extent([-84.6, -75.2, 33.4, 37.0], crs=PC)
    neigh = us[us["name"].isin(["Virginia", "Tennessee", "South Carolina", "Georgia"])]
    ax.add_geometries(neigh.geometry, crs=PC, fc="white", ec=CORNER, lw=0.6, zorder=1)
    ax.add_geometries(nc.geometry, crs=PC, fc=DOGWOOD, ec=PINE, lw=1.2, zorder=2)
    lon = np.linspace(-85, -75, 100)
    for la, lab in [(34 + 20 / 60, "34° 20′ N"), (36 + 10 / 60, "36° 10′ N")]:
        ax.plot(lon, [la] * 100, transform=PC, color=POPLAR, lw=2, zorder=3)
        ax.text(-84.5, la + 0.06, f"State Plane standard parallel, {lab}", transform=PC, fontsize=9.5, color="#9A5A00", zorder=4)
    ax.plot([-78, -78], [33.4, 37.0], transform=PC, color=NAVY, lw=2, ls="--", zorder=3)
    ax.text(-78.6, 33.6, "UTM zone 17N", transform=PC, fontsize=12, fontweight="bold", ha="right", zorder=4)
    ax.text(-77.4, 33.6, "UTM zone 18N", transform=PC, fontsize=12, fontweight="bold", ha="left", zorder=4)
    ax.text(-77.95, 36.85, "78° W", transform=PC, fontsize=9.5, ha="left", zorder=4)
    cities = {"Asheville": (-82.55, 35.6), "Charlotte": (-80.84, 35.23), "Chapel Hill": (-79.05, 35.91),
              "Raleigh": (-78.64, 35.78), "Wilmington": (-77.94, 34.21), "Greenville": (-77.37, 35.61)}
    for n, (x, y) in cities.items():
        ax.plot(x, y, "o", color=NAVY, ms=5, transform=PC, zorder=5)
        ax.text(x + 0.1, y + 0.05, n, transform=PC, fontsize=9.5, zorder=5,
                bbox=dict(fc="white", ec="none", alpha=0.7, pad=0.5) if n == "Wilmington" else None)
    outline(ax)
    save(fig, f"{OUT}/nc-zones.png")


# --- 10. Web Mercator tiles --------------------------------------------------
def tiles():
    fig = plt.figure(figsize=(11, 4))
    for z in range(3):
        ax = fig.add_subplot(1, 3, z + 1, projection=ccrs.Mercator.GOOGLE)
        ax.set_global()
        add_land(ax)
        n = 2 ** z
        e = 20037508.34
        for k in range(n + 1):
            v = -e + 2 * e * k / n
            ax.plot([v, v], [-e, e], color=NAVY, lw=1.2)
            ax.plot([-e, e], [v, v], color=NAVY, lw=1.2)
        outline(ax)
        ax.set_title(f"Zoom {z}: {n * n} tile{'s' if n > 1 else ''}", fontsize=13)
    save(fig, f"{OUT}/web-mercator-tiles.png")


if __name__ == "__main__":
    which = sys.argv[2:] or ["pyramid", "light", "surfaces", "secant", "tissot_grid", "greenland", "scale_error", "utm", "nc_zones", "tiles"]
    for w in which:
        globals()[w]()
