"""Diagrams for the Spatial Joins chapter (images/spatial-joins/).

Run from the repository root:
    python3 scripts/figures/spatial_joins.py /path/to/natural-earth-geojson [names]
The airports map uses Natural Earth's states, populated places, and airports
layers. The other panels use made-up points and polygons.
"""
import sys, os
import numpy as np
sys.path.insert(0, os.path.dirname(__file__))
from style import *  # noqa
import matplotlib.pyplot as plt
from matplotlib.patches import Polygon as MPoly, Circle, FancyArrowPatch, Rectangle

OUT = "images/spatial-joins"
NE = sys.argv[1] if len(sys.argv) > 1 else "/home/user/work/ne"
rng = np.random.default_rng(370)

# Four made-up "counties" on a 10 x 8 grid
COUNTIES = {
    "Alder": [(0, 4), (4.5, 4), (4, 8), (0, 8)],
    "Birch": [(4.5, 4), (10, 4), (10, 8), (4, 8)],
    "Cedar": [(0, 0), (5.5, 0), (5, 4), (0, 4)],
    "Dogwood": [(5.5, 0), (10, 0), (10, 4), (5, 4)],
}
CCOL = {"Alder": DOGWOOD, "Birch": SAND, "Cedar": WATER, "Dogwood": "#E8D9F0"}


def pip(x, y, poly):
    from matplotlib.path import Path
    return Path(poly).contains_point((x, y))


def schools():
    pts = [(1.2, 6.5), (2.8, 5.2), (3.3, 7.1), (5.6, 6.0), (7.2, 7.0), (8.8, 5.1), (6.5, 4.8),
           (8.1, 6.2), (1.5, 2.6), (3.6, 1.2), (7.0, 2.5), (8.7, 1.1), (6.2, 1.6), (9.1, 3.2)]
    return pts


def county_of(x, y):
    for k, p in COUNTIES.items():
        if pip(x, y, p):
            return k


def draw_counties(ax, fill=None, lw=1.2, labels=True):
    for k, p in COUNTIES.items():
        fc = fill[k] if fill else CCOL[k]
        ax.add_patch(MPoly(p, closed=True, fc=fc, ec=NAVY, lw=lw))
        if labels:
            cx = np.mean([q[0] for q in p]); cy = np.mean([q[1] for q in p])
            ax.text(cx, cy + (1.3 if cy > 4 else -1.4), k, ha="center", va="center", fontsize=10,
                    fontweight="bold", color=NAVY, alpha=0.8)


HOTELS = [(2.0, 5.5), (7.5, 6.0), (5.0, 1.5)]
ATTR = [(1.0, 7.2), (3.2, 4.2), (6.0, 7.3), (8.8, 7.0), (8.6, 4.4), (4.0, 2.6), (6.6, 0.8), (1.6, 1.4),
        (9.2, 2.2)]
HCOL = [PINE, CLAY, DUSK]


def nearest(p, cands):
    d = [np.hypot(p[0] - c[0], p[1] - c[1]) for c in cands]
    i = int(np.argmin(d))
    return i, d[i]


def four_kinds():
    fig, axs = plt.subplots(2, 2, figsize=(10.5, 9.2))
    for ax in axs.flat:
        ax.set_xlim(-0.2, 10.2); ax.set_ylim(-0.2, 8.2); ax.set_aspect("equal")
        ax.set_xticks([]); ax.set_yticks([])
        for s in ax.spines.values():
            s.set_color(CORNER)
    S = schools()
    # simple inside
    ax = axs[0, 0]
    draw_counties(ax)
    ccols = {"Alder": PINE, "Birch": POPLAR, "Cedar": BLUE, "Dogwood": DUSK}
    for x, y in S:
        ax.plot(x, y, "o", ms=9, mfc=ccols[county_of(x, y)], mec="white", mew=1.2)
    ax.set_title("Simple inside join\nWhich county is each school in?", fontsize=11.5)
    # summarized inside
    ax = axs[0, 1]
    counts = {k: 0 for k in COUNTIES}
    for x, y in S:
        counts[county_of(x, y)] += 1
    shade = {1: "#E3EFEA", 2: "#B6D8CC", 3: "#7FB9A9", 4: "#3F9482", 5: PINE}
    draw_counties(ax, fill={k: shade[min(v, 5)] for k, v in counts.items()}, labels=False)
    for x, y in S:
        ax.plot(x, y, "o", ms=6, mfc=NAVY, mec="white", mew=0.8)
    for k, p in COUNTIES.items():
        cx = np.mean([q[0] for q in p]); cy = np.mean([q[1] for q in p])
        ax.text(cx, cy + (1.35 if cy > 4 else -1.45), f"{k}: {counts[k]}", ha="center", va="center",
                fontsize=10.5, fontweight="bold",
                bbox=dict(boxstyle="round,pad=0.25", fc="white", ec=NAVY, lw=0.6))
    ax.set_title("Summarized inside join\nHow many schools are in each county?", fontsize=11.5)
    # simple distance
    ax = axs[1, 0]
    ax.add_patch(Rectangle((-0.2, -0.2), 10.4, 8.4, fc=FOG, ec="none"))
    for h in HOTELS:
        i, d = nearest(h, ATTR)
        ax.plot([h[0], ATTR[i][0]], [h[1], ATTR[i][1]], color=NAVY, lw=1.6, ls="--")
        mx, my = (h[0] + ATTR[i][0]) / 2, (h[1] + ATTR[i][1]) / 2
        ax.text(mx + 0.3, my - 0.1, f"{d:.1f} km", va="center", fontsize=9.5, color=NAVY, fontweight="bold")
    for a in ATTR:
        ax.plot(*a, marker="*", ms=14, mfc=GINKGO, mec=NAVY, mew=0.8)
    for h, c in zip(HOTELS, HCOL):
        ax.plot(*h, marker="s", ms=11, mfc=c, mec="white", mew=1.2)
    ax.set_title("Simple distance join\nWhich attraction is closest to each hotel, and how far?",
                 fontsize=11.5)
    # summarized distance
    ax = axs[1, 1]
    ax.add_patch(Rectangle((-0.2, -0.2), 10.4, 8.4, fc=FOG, ec="none"))
    cnt = [0, 0, 0]
    for a in ATTR:
        i, d = nearest(a, HOTELS)
        cnt[i] += 1
        ax.plot([a[0], HOTELS[i][0]], [a[1], HOTELS[i][1]], color=HCOL[i], lw=1.3, alpha=0.8)
        ax.plot(*a, marker="*", ms=14, mfc=GINKGO, mec=HCOL[i], mew=1.3)
    for h, c, n in zip(HOTELS, HCOL, cnt):
        ax.plot(*h, marker="s", ms=11, mfc=c, mec="white", mew=1.2)
        ax.text(h[0] - 0.3, h[1] - 0.75, f"{n} attractions", ha="right" if h[0] > 4 else "left", fontsize=10, fontweight="bold",
                color=c, bbox=dict(boxstyle="round,pad=0.2", fc="white", ec=c, lw=0.6))
    ax.set_title("Summarized distance join\nHow many attractions are closest to each hotel?",
                 fontsize=11.5)
    # legend
    from matplotlib.lines import Line2D
    h = [Line2D([], [], marker="o", ls="", mfc=NAVY, mec="white", ms=8, label="School"),
         Line2D([], [], marker="s", ls="", mfc=PINE, mec="white", ms=9, label="Hotel"),
         Line2D([], [], marker="*", ls="", mfc=GINKGO, mec=NAVY, ms=13, label="Attraction")]
    fig.legend(handles=h, loc="lower center", ncol=3, frameon=False, fontsize=10.5,
               bbox_to_anchor=(0.5, -0.01))
    fig.subplots_adjust(left=0.01, right=0.99, top=0.95, bottom=0.06, wspace=0.06, hspace=0.2)
    save(fig, f"{OUT}/four-kinds.png")


def attribute_vs_spatial():
    fig, axs = plt.subplots(1, 2, figsize=(11, 4.2))
    # left: attribute join, schematic
    ax = axs[0]
    ax.set_xlim(0, 10); ax.set_ylim(0, 8); ax.axis("off")
    ax.set_title("Attribute join: match on a shared key", fontsize=12)
    from database_joins import draw_table
    draw_table(ax, 0.2, 6.6, ["FIPS", "County"], [("37063", "Durham"), ("37135", "Orange"), ("37183", "Wake")],
               [1.3, 1.6], fs=9.5, keycol=0, rowh=0.75)
    draw_table(ax, 5.4, 6.6, ["FIPS", "Pop_2020"], [("37183", "1,129,410"), ("37063", "324,833"),
                                                    ("37135", "148,696")], [1.3, 1.9], fs=9.5, keycol=0, rowh=0.75)
    pairs = [(0, 1), (1, 2), (2, 0)]
    for a, b in pairs:
        ya = 6.6 - (a + 1.5) * 0.75; yb = 6.6 - (b + 1.5) * 0.75
        ax.add_patch(FancyArrowPatch((5.35, yb), (3.15, ya), arrowstyle="-|>", mutation_scale=10,
                                     lw=1.2, color=PINE))
    ax.text(5, 0.9, "The FIPS values match, whatever the row order.", ha="center", fontsize=10, color=PINE)
    # right: spatial join
    ax = axs[1]
    ax.set_xlim(-0.2, 10.2); ax.set_ylim(-0.6, 8.6); ax.set_aspect("equal"); ax.axis("off")
    ax.set_title("Spatial join: match on location", fontsize=12)
    draw_counties(ax)
    pts = [(1.4, 6.0), (3.2, 6.6), (3.0, 5.0), (6.6, 6.4), (8.2, 5.2), (2.4, 2.0), (7.3, 2.4), (8.6, 1.3),
           (6.4, 1.2), (4.0, 1.0)]
    for x, y in pts:
        ax.plot(x, y, marker="P", ms=10, mfc=CLAY, mec="white", mew=1)
    ax.text(5, -0.45, "EMS calls (points) have no neighborhood field;\nthe polygon each falls in supplies it.",
            ha="center", va="top", fontsize=10, color=PINE)
    save(fig, f"{OUT}/attribute-vs-spatial.png")


def degree_length():
    lat = np.linspace(0, 80, 200)
    from pyproj import Geod
    g = Geod(ellps="WGS84")
    lon_km = [g.inv(0, la, 1, la)[2] / 1000 for la in lat]
    lat_km = [g.inv(0, la - 0.5, 0, la + 0.5)[2] / 1000 if la > 0.5 else g.inv(0, 0, 0, 1)[2] / 1000 for la in lat]
    fig, axs = plt.subplots(1, 2, figsize=(11.5, 4.3), gridspec_kw=dict(width_ratios=[1.05, 1]))
    ax = axs[0]
    ax.plot(lat, lat_km, color=PINE, lw=2.4, label="1° of latitude (north–south)")
    ax.plot(lat, lon_km, color=CLAY, lw=2.4, label="1° of longitude (east–west)")
    for la in (0, 35.9, 45, 60):
        v = g.inv(0, la, 1, la)[2] / 1000
        ax.plot(la, v, "o", color=CLAY, ms=6)
        ax.text(la + 1.5, v + 3, f"{v:.0f} km", fontsize=9.5, color=CLAY)
    ax.axvline(35.9, color=BASIN, lw=0.8, ls=":")
    ax.text(36.5, 15, "Chapel Hill", fontsize=9, color=BASIN, rotation=90)
    ax.set_xlabel("Latitude (degrees)"); ax.set_ylabel("Ground distance (km)")
    ax.set_ylim(0, 125); ax.set_xlim(0, 80)
    ax.legend(frameon=False, loc="lower left", fontsize=9.5)
    ax.set_title("A degree is not a fixed distance", fontsize=12)
    for s in ("top", "right"):
        ax.spines[s].set_visible(False)
    # right: nearest neighbor flips
    ax = axs[1]
    ax.set_title("At 45° N: which attraction is closer?", fontsize=12)
    ax.set_xlim(-0.35, 1.25); ax.set_ylim(-0.25, 1.05); ax.set_aspect("equal")
    H = (0, 0); A = (0.9, 0); B = (0, 0.8)
    kmlon = g.inv(0, 45, 1, 45)[2] / 1000
    kmlat = g.inv(0, 44.5, 0, 45.5)[2] / 1000
    ax.plot([H[0], A[0]], [H[1], A[1]], color=CLAY, lw=2)
    ax.plot([H[0], B[0]], [H[1], B[1]], color=PINE, lw=2)
    ax.plot(*H, marker="s", ms=13, mfc=NAVY, mec="white")
    ax.plot(*A, marker="*", ms=18, mfc=GINKGO, mec=NAVY)
    ax.plot(*B, marker="*", ms=18, mfc=GINKGO, mec=NAVY)
    ax.text(-0.06, -0.08, "Hotel", ha="right", va="top", fontsize=10)
    ax.text(A[0], A[1] + 0.07, "A", ha="center", fontsize=12, fontweight="bold")
    ax.text(B[0] + 0.06, B[1], "B", va="center", fontsize=12, fontweight="bold")
    ax.text(0.45, -0.07, f"0.9° east\n= {0.9 * kmlon:.0f} km", ha="center", va="top", fontsize=10, color=CLAY)
    ax.text(0.04, 0.4, f"0.8° north\n= {0.8 * kmlat:.0f} km", ha="left", va="center", fontsize=10, color=PINE)
    ax.text(0.68, 0.72, "In degrees, B is closer\n(0.8 < 0.9).\nOn the ground, A is closer\n"
            f"({0.9 * kmlon:.0f} km < {0.8 * kmlat:.0f} km).", ha="center", va="center", fontsize=10,
            bbox=dict(boxstyle="round,pad=0.4", fc=SAND, ec=NAVY, lw=0.6))
    ax.set_xticks([0, 0.5, 1]); ax.set_yticks([0, 0.5, 1])
    ax.set_xlabel("Degrees east of the hotel"); ax.set_ylabel("Degrees north of the hotel")
    ax.grid(color=CORNER, lw=0.6)
    for s in ("top", "right"):
        ax.spines[s].set_visible(False)
    fig.tight_layout()
    save(fig, f"{OUT}/degree-distance.png")


def nc_airports():
    import geopandas as gpd
    st = gpd.read_file(f"{NE}/ne_50m_admin_1_states_provinces_lakes.geojson")
    st = st[st["iso_a2"] == "US"]
    ap = gpd.read_file(f"{NE}/ne_10m_airports.geojson")
    keep = {"CLT": "Charlotte (CLT)", "RDU": "Raleigh-Durham (RDU)", "GSO": "Greensboro (GSO)",
            "ILM": "Wilmington (ILM)", "TYS": "Knoxville (TYS)", "CAE": "Columbia (CAE)"}
    ap = ap[ap["iata_code"].isin(keep)].copy()
    ap["label"] = ap["iata_code"].map(keep)
    pp = gpd.read_file(f"{NE}/ne_10m_populated_places_simple.geojson")
    pp = pp[(pp["adm1name"] == "North Carolina")].copy()
    crs = 32119
    st, ap, pp = st.to_crs(crs), ap.to_crs(crs), pp.to_crs(crs)
    j = gpd.sjoin_nearest(pp, ap[["iata_code", "label", "geometry"]], distance_col="dist_m")
    j["dist_mi"] = j["dist_m"] / 1609.344
    cols = {"CLT": PINE, "RDU": CLAY, "GSO": DUSK, "ILM": POPLAR, "TYS": BERRY, "CAE": BLUE}
    fig, ax = plt.subplots(figsize=(11, 5.6))
    st.plot(ax=ax, fc="white", ec=CORNER, lw=0.8)
    st[st["name"] == "North Carolina"].plot(ax=ax, fc=FOG, ec=NAVY, lw=1)
    for _, r in j.iterrows():
        a = ap[ap["iata_code"] == r["iata_code"]].geometry.iloc[0]
        ax.plot([r.geometry.x, a.x], [r.geometry.y, a.y], color=cols[r["iata_code"]], lw=1.1, alpha=0.8)
    for code, g in j.groupby("iata_code"):
        ax.scatter(g.geometry.x, g.geometry.y, s=18 + g["dist_mi"] * 0.9, color=cols[code], ec="white",
                   lw=0.6, zorder=3)
    for _, r in ap.iterrows():
        ax.plot(r.geometry.x, r.geometry.y, marker="^", ms=12, mfc=cols[r["iata_code"]], mec=NAVY, zorder=4)
        dy = 14000 if r["iata_code"] != "ILM" else -26000
        ax.text(r.geometry.x, r.geometry.y + dy, r["label"], ha="center", fontsize=9.5, fontweight="bold",
                color=cols[r["iata_code"]], zorder=5,
                bbox=dict(boxstyle="round,pad=0.15", fc="white", ec="none", alpha=0.85))
    for nm in ["Asheville", "Kitty Hawk", "Fayetteville", "Hickory"]:
        r = j[j["name"] == nm]
        if len(r):
            r = r.iloc[0]
            dx = -70000 if nm == "Kitty Hawk" else 6000
            dy = -45000 if nm == "Kitty Hawk" else -15000
            ax.text(r.geometry.x + dx, r.geometry.y + dy, f"{nm}\n{r['dist_mi']:.0f} mi", fontsize=8.5,
                    color=NAVY, zorder=5, bbox=dict(boxstyle="round,pad=0.1", fc="white", ec="none", alpha=0.8))
    xmin, ymin, xmax, ymax = st[st["name"] == "North Carolina"].total_bounds
    ax.set_xlim(xmin - 140000, xmax + 30000); ax.set_ylim(ymin - 110000, ymax + 40000)
    ax.set_aspect("equal"); ax.axis("off")
    save(fig, f"{OUT}/nc-airports.png")
    out = j[["name", "pop_max", "iata_code", "dist_mi"]].sort_values("dist_mi", ascending=False)
    print(out.to_string())


def buffer_count():
    fig, ax = plt.subplots(figsize=(7.5, 4.6))
    ax.set_xlim(0, 12); ax.set_ylim(-0.8, 7); ax.set_aspect("equal"); ax.axis("off")
    road = np.array([(0.3, 1.2), (3, 2.6), (6, 3.0), (9, 4.6), (11.7, 5.6)])
    from shapely.geometry import LineString, Point
    ls = LineString(road)
    buf = ls.buffer(0.7)
    ax.add_patch(MPoly(np.array(buf.exterior.coords), fc=WATER, ec=BLUE, lw=1, ls="--"))
    ax.plot(road[:, 0], road[:, 1], color=NAVY, lw=4, solid_capstyle="round")
    pts = [(1.5, 1.4), (2.6, 2.9), (4.4, 3.2), (5.2, 2.2), (6.8, 3.7), (7.6, 3.1), (9.8, 5.2), (10.6, 4.6),
           (3.6, 4.6), (8.0, 1.6), (6.2, 5.8), (10.9, 2.8), (1.4, 3.5)]
    n = 0
    for p in pts:
        inside = buf.contains(Point(p))
        n += inside
        ax.plot(*p, marker="X", ms=10, mfc=CLAY if inside else CORNER, mec=NAVY if inside else BASIN, mew=0.6)
    ax.text(6, 6.7, f"Join_Count = {n} crashes within the search distance of this road",
            ha="center", fontsize=11, fontweight="bold", color=NAVY)
    ax.text(6, -0.55, "Dashed outline: the search distance (a buffer) around the road", fontsize=9.5, color=BLUE, ha="center")
    save(fig, f"{OUT}/within-distance.png")


FUNCS = dict(four_kinds=four_kinds, attribute_vs_spatial=attribute_vs_spatial, degree=degree_length,
             airports=nc_airports, buffer=buffer_count)

if __name__ == "__main__":
    os.makedirs(OUT, exist_ok=True)
    names = sys.argv[2:] or list(FUNCS)
    for n in names:
        FUNCS[n]()
