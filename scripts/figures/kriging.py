"""Figures for Chapter 17, Kriging.

Usage: python kriging.py

All data are made up (fixed seeds). Ordinary kriging is implemented here
with numpy, using the k nearest observations for each prediction.
"""
from pathlib import Path

import numpy as np
import matplotlib.pyplot as plt
from matplotlib.patches import Ellipse, Circle
from scipy.spatial import cKDTree

from style import NAVY, PINE, BLUE, BASIN, CORNER, FOG, CLAY, POPLAR, GINKGO, SAND, DOGWOOD, BERRY, DUSK, save
import interpolation as ip

OUT = Path(__file__).parent.parent.parent / "images" / "kriging"
OUT.mkdir(parents=True, exist_ok=True)


# ---------- variogram models ----------
def spherical(h, nug, psill, rng):
    h = np.asarray(h, float)
    r = np.minimum(h / rng, 1)
    g = nug + psill * (1.5 * r - 0.5 * r ** 3)
    return np.where(h == 0, 0, g)


def exponential(h, nug, psill, rng):
    h = np.asarray(h, float)
    g = nug + psill * (1 - np.exp(-3 * h / rng))
    return np.where(h == 0, 0, g)


def gaussian(h, nug, psill, rng):
    h = np.asarray(h, float)
    g = nug + psill * (1 - np.exp(-3 * (h / rng) ** 2))
    return np.where(h == 0, 0, g)


def empirical(p, z, nbins=15, maxd=None, angle=None, tol=22.5):
    """Binned semivariogram. angle in degrees from east (0 = west-east pairs)."""
    i, j = np.triu_indices(len(z), 1)
    dx, dy = p[j, 0] - p[i, 0], p[j, 1] - p[i, 1]
    d = np.hypot(dx, dy)
    g = 0.5 * (z[i] - z[j]) ** 2
    if angle is not None:
        a = np.degrees(np.arctan2(dy, dx)) % 180
        diff = np.minimum(np.abs(a - angle), 180 - np.abs(a - angle))
        m = diff <= tol
        d, g = d[m], g[m]
    maxd = maxd or d.max() / 2
    edges = np.linspace(0, maxd, nbins + 1)
    h, gam, n = [], [], []
    for a, b in zip(edges[:-1], edges[1:]):
        m = (d > a) & (d <= b)
        if m.sum() > 5:
            h.append(d[m].mean())
            gam.append(g[m].mean())
            n.append(m.sum())
    return np.array(h), np.array(gam), np.array(n), d, g


def fit(h, gam, n, model=spherical):
    best = None
    for rng_ in np.linspace(h.max() * 0.1, h.max() * 1.5, 60):
        for nugf in np.linspace(0, 0.5, 11):
            sill = gam[-3:].mean()
            for sf in np.linspace(0.6, 1.4, 17):
                nug = nugf * sill * sf
                ps = sill * sf - nug
                pred = model(h, nug, ps, rng_)
                err = (n * (gam - pred) ** 2 / np.maximum(pred, 1e-9) ** 2).sum()
                if best is None or err < best[0]:
                    best = (err, nug, ps, rng_)
    return best[1:]


def okrige(p, z, q, vario, k=16, aniso=None):
    """Ordinary kriging. aniso = (angle_deg, ratio): ratio = minor/major range,
    angle = direction of the major axis, degrees from east."""
    def tf(x):
        if aniso is None:
            return x
        a = np.radians(aniso[0])
        u = x[:, 0] * np.cos(a) + x[:, 1] * np.sin(a)
        v = -x[:, 0] * np.sin(a) + x[:, 1] * np.cos(a)
        return np.column_stack([u, v / aniso[1]])
    pt, qt = tf(p), tf(q)
    tree = cKDTree(pt)
    k = min(k, len(z))
    _, idx = tree.query(qt, k)
    P = pt[idx]                                 # (m, k, 2)
    D = np.linalg.norm(P[:, :, None, :] - P[:, None, :, :], axis=-1)
    m = len(q)
    A = np.ones((m, k + 1, k + 1))
    A[:, :k, :k] = vario(D)
    A[:, k, k] = 0
    d0 = np.linalg.norm(P - qt[:, None, :], axis=-1)
    b = np.ones((m, k + 1))
    b[:, :k] = vario(d0)
    sol = np.linalg.solve(A, b[..., None])[..., 0]
    lam, mu = sol[:, :k], sol[:, k]
    pred = (lam * z[idx]).sum(1)
    var = (lam * b[:, :k]).sum(1) + mu
    return pred, np.sqrt(np.maximum(var, 0)), lam, idx


def loocv(p, z, vario, k=16, aniso=None):
    pr, se = [], []
    for i in range(len(z)):
        m = np.arange(len(z)) != i
        a, s, *_ = okrige(p[m], z[m], p[i:i + 1], vario, k, aniso)
        pr.append(a[0])
        se.append(s[0])
    pr, se = np.array(pr), np.array(se)
    e = pr - z
    return dict(me=e.mean(), rmse=np.sqrt((e ** 2).mean()), ase=se.mean(),
                rmsse=np.sqrt(((e / np.maximum(se, 1e-9)) ** 2).mean()))


def mapax(ax, title=None):
    ax.set_xticks([])
    ax.set_yticks([])
    for s in ax.spines.values():
        s.set_color(CORNER)
    if title:
        ax.set_title(title, fontsize=11.5, loc="left")


# ---------- 1. semivariance by hand ----------
def semivariance_example():
    pts = {(10, 10): 4, (20, 10): 3, (10, 20): 4, (20, 20): 3}
    fig, axes = plt.subplots(1, 2, figsize=(11, 4.2))
    for ax in axes:
        for (x, y), v in pts.items():
            ax.scatter(x, y, s=110, c=BLUE, ec=NAVY, zorder=3)
            ax.text(x + (-2.2 if x < 15 else 2.2), y, str(v), ha="center", va="center", fontsize=13,
                    weight="bold", color=NAVY)
        ax.set_xlim(2, 28)
        ax.set_ylim(4, 27)
        ax.set_aspect("equal")
        ax.set_axis_off()
    ax = axes[0]
    ax.plot([10, 20], [10, 10], color=CLAY, lw=3, zorder=2)
    ax.text(15, 15, "(diagonal pairs are 14.1 apart,\nso they fall in another bin)", ha="center", va="center",
            fontsize=8.5, color=BASIN) if False else None
    ax.text(15, 6.0, "½ × (4 − 3)² = 0.5", ha="center", fontsize=11, color=CLAY)
    ax.set_title("One pair", fontsize=12, loc="left")
    ax = axes[1]
    pairs = [((10, 10), (20, 10)), ((10, 20), (20, 20)), ((10, 10), (10, 20)), ((20, 10), (20, 20))]
    sq = []
    for a, b in pairs:
        ax.plot(*np.array([a, b]).T, color=PINE, lw=2.2, zorder=2)
        sq.append((pts[a] - pts[b]) ** 2)
    g = 0.5 * sum(sq) / len(sq)
    ax.set_title(f"All {len(pairs)} pairs 10 apart (one bin)", fontsize=12, loc="left")
    ax.text(15, 5.0, f"γ(10) = ½ × ({' + '.join(str(s) for s in sq)}) ÷ {len(sq)} = {g:.2f}", ha="center",
            fontsize=11, color=PINE)
    save(fig, OUT / "semivariance-example.png")
    print("gamma(10)", sq, g)


# ---------- 2. linear surface and its cloud ----------
def linear_cloud():
    rng = np.random.default_rng(19)
    p = rng.uniform(0, 1000, (200, 2))
    z = p[:, 0] / 10
    i, j = np.triu_indices(len(z), 1)
    dx, dy = p[j, 0] - p[i, 0], p[j, 1] - p[i, 1]
    d = np.hypot(dx, dy)
    g = 0.5 * (z[i] - z[j]) ** 2
    ang = np.degrees(np.arctan2(dy, dx)) % 180
    ew = (np.minimum(ang, 180 - ang) <= 20)
    ns = (np.abs(ang - 90) <= 20)
    fig, axes = plt.subplots(1, 2, figsize=(12, 5), gridspec_kw=dict(width_ratios=[1, 1.25]))
    ax = axes[0]
    sc = ax.scatter(*p.T, c=z, cmap="viridis", s=22, ec="white", lw=0.3)
    cb = fig.colorbar(sc, ax=ax, fraction=0.046, pad=0.03)
    cb.set_label("Z", fontsize=9)
    ax.set_aspect("equal")
    ax.set_xlim(0, 1000)
    ax.set_ylim(0, 1000)
    mapax(ax, "Z rises from west to east; no change north to south")
    ax = axes[1]
    sub = np.random.default_rng(1).choice(len(d), 6000, replace=False)
    ax.scatter(d[sub], g[sub], s=3, c=CORNER, label="All pairs")
    s2 = sub[ew[sub]]
    ax.scatter(d[s2], g[s2], s=5, c=CLAY, label="West–east pairs")
    s3 = sub[ns[sub]]
    ax.scatter(d[s3], g[s3], s=5, c=PINE, label="North–south pairs")
    ax.set_xlabel("Distance between the pair")
    ax.set_ylabel("Semivariance, ½ (zᵢ − zⱼ)²")
    ax.spines[["top", "right"]].set_visible(False)
    ax.legend(frameon=False, fontsize=9.5, markerscale=3, loc="upper left")
    ax.set_title("Semivariogram cloud", fontsize=11.5, loc="left")
    fig.subplots_adjust(wspace=0.4)
    save(fig, OUT / "linear-cloud.png")


# ---------- 3. semivariogram anatomy ----------
def anatomy():
    rng = np.random.default_rng(5)
    h = np.linspace(40, 760, 18)
    nug, ps, rg = 2.0, 8.0, 450
    gam = spherical(h, nug, ps, rg) + rng.normal(0, 0.45, h.size)
    hf = np.linspace(0, 800, 400)
    fig, ax = plt.subplots(figsize=(8, 4.4))
    ax.plot(hf[1:], spherical(hf[1:], nug, ps, rg), color=BLUE, lw=2.4, label="Fitted model (spherical)")
    ax.scatter(h, gam, s=45, c=NAVY, zorder=4, label="Empirical semivariogram (one dot per bin)")
    ax.axhline(nug + ps, color=CLAY, lw=1.2, ls="--")
    ax.text(790, nug + ps + 0.25, "Sill", color=CLAY, ha="right", fontsize=11, weight="bold")
    ax.axvline(rg, color=PINE, lw=1.2, ls="--")
    ax.text(rg + 8, 0.6, "Range", color=PINE, fontsize=11, weight="bold")
    ax.annotate("", xy=(0, nug), xytext=(0, 0), arrowprops=dict(arrowstyle="<->", color=BERRY, lw=1.6))
    ax.text(12, nug / 2, "Nugget", color=BERRY, fontsize=11, weight="bold", va="center")
    ax.annotate("", xy=(620, nug + ps), xytext=(620, nug), arrowprops=dict(arrowstyle="<->", color=BASIN, lw=1.2))
    ax.text(630, nug + ps / 2, "Partial sill", color=BASIN, fontsize=10, va="center")
    ax.text(rg / 2, 11.6, "Autocorrelated", ha="center", fontsize=9.5, color=PINE)
    ax.text((rg + 800) / 2, 11.6, "Not autocorrelated", ha="center", fontsize=9.5, color=BASIN)
    ax.set_xlim(0, 800)
    ax.set_ylim(0, 12.4)
    ax.set_xlabel("Lag distance, h")
    ax.set_ylabel("Semivariance, γ(h)")
    ax.spines[["top", "right"]].set_visible(False)
    ax.legend(frameon=False, fontsize=9.5, loc="upper center", bbox_to_anchor=(0.5, -0.17), ncol=2)
    save(fig, OUT / "semivariogram.png")


# ---------- 4. model shapes ----------
def models():
    h = np.linspace(0.001, 800, 400)
    fig, ax = plt.subplots(figsize=(8, 4))
    ax.plot(h, spherical(h, 0, 10, 450), color=BLUE, lw=2.2, label="Spherical: reaches the sill at the range")
    ax.plot(h, exponential(h, 0, 10, 450), color=CLAY, lw=2.2, ls="--", label="Exponential: approaches the sill")
    ax.plot(h, gaussian(h, 0, 10, 450), color=PINE, lw=2.2, ls="-.", label="Gaussian: flat near zero")
    ax.plot(h, h / 60, color=BERRY, lw=2.2, ls=":", label="Linear: no sill (a sign of a trend)")
    ax.axvline(450, color=CORNER, lw=1)
    ax.text(455, 0.4, "range", color=BASIN, fontsize=9)
    ax.set_xlim(0, 800)
    ax.set_ylim(0, 13.5)
    ax.set_xlabel("Lag distance, h")
    ax.set_ylabel("Semivariance, γ(h)")
    ax.spines[["top", "right"]].set_visible(False)
    ax.legend(frameon=False, fontsize=9.5, loc="upper left")
    save(fig, OUT / "models.png")


# ---------- 5. three components ----------
def components():
    rng = np.random.default_rng(8)
    x = np.linspace(0, 100, 300)
    trend = 10 + 0.12 * x
    auto = 2.2 * np.sin(x / 7) + 1.2 * np.sin(x / 3.1 + 1)
    noise = rng.normal(0, 0.6, x.size)
    xs = np.sort(rng.uniform(0, 100, 30))
    ys = np.interp(xs, x, trend + auto) + rng.normal(0, 0.6, xs.size)
    fig, axes = plt.subplots(1, 2, figsize=(12, 3.8), gridspec_kw=dict(width_ratios=[1.6, 1]))
    ax = axes[0]
    ax.plot(x, trend, color=CLAY, lw=2.2, label="Trend")
    ax.plot(x, trend + auto, color=BLUE, lw=2.2, label="Trend + spatial autocorrelation")
    ax.scatter(xs, ys, s=22, c=NAVY, zorder=4, label="Observations (with random error)")
    ax.set_title("A. Trend and autocorrelation", fontsize=11.5, loc="left")
    ax.legend(frameon=False, fontsize=9, loc="upper left")
    ax2 = axes[1]
    ax2.plot(x, noise, color=BASIN, lw=0.9)
    ax2.axhline(0, color=CORNER)
    ax2.set_ylim(-4, 4)
    ax2.set_title("B. Random error", fontsize=11.5, loc="left")
    for a in axes:
        a.set_xlabel("Location")
        a.spines[["top", "right"]].set_visible(False)
    axes[0].set_ylabel("Value")
    save(fig, OUT / "components.png")


# ---------- 6. kriging weights vs IDW with a cluster ----------
def weights():
    p = np.array([[3.0, 6.0], [6.9, 7.7], [8.1, 7.0], [7.0, 6.5], [8.0, 8.4], [5.0, 2.0]])
    z = np.array([10.0, 20, 21, 19, 22, 12])
    x0 = np.array([[5.0, 5.0]])
    v = lambda h: spherical(h, 0, 10, 8)
    _, _, lam, idx = okrige(p, z, x0, v, k=len(z))
    lk = np.zeros(len(z))
    lk[idx[0]] = lam[0]
    d = np.hypot(*(p - x0[0]).T)
    wi = (1 / d ** 2) / (1 / d ** 2).sum()
    fig, axes = plt.subplots(1, 2, figsize=(11, 4.8))
    for ax, w, t in [(axes[0], wi, "IDW (power 2)"), (axes[1], lk, "Ordinary kriging")]:
        for (x, y), wt, val in zip(p, w, z):
            ax.plot([5, x], [5, y], color=CORNER, lw=1, ls="--", zorder=1)
            ax.scatter(x, y, s=1400 * abs(wt) + 20, c=BLUE if wt >= 0 else CLAY, ec=NAVY, alpha=0.85, zorder=3)
        for i2, ((x, y), wt) in enumerate(zip(p, w)):
            u = np.array([x - 5, y - 5]) / np.hypot(x - 5, y - 5)
            ox, oy = u * 0.75
            ax.text(x + ox, y + oy, f"{wt:.2f}", fontsize=9.5, color=NAVY, ha="center", va="center", zorder=5)
        ax.scatter(5, 5, s=120, marker="X", c=CLAY, ec=NAVY, lw=0.6, zorder=4)
        ax.set_xlim(1, 9.6)
        ax.set_ylim(1, 9.4)
        ax.set_aspect("equal")
        ax.set_axis_off()
        cl = w[1:5].sum()
        ax.set_title(f"{t}: the cluster of 4 gets {cl:.0%} of the weight", fontsize=11.5, loc="left")
    save(fig, OUT / "weights.png")
    print("idw", np.round(wi, 3), "krig", np.round(lk, 3))


# ---------- 7. the sine surface: semivariograms by direction ----------
def sine_data():
    rng = np.random.default_rng(31)
    p = rng.uniform(0, 1000, (200, 2))
    z = 10 * np.sin(2 * np.pi * p[:, 0] / 400)
    return p, z


SG = np.linspace(0, 1000, 120)
SX, SY = np.meshgrid(SG, SG)
SQ = np.column_stack([SX.ravel(), SY.ravel()])


def sine_variograms():
    p, z = sine_data()
    fig, axes = plt.subplots(1, 3, figsize=(14, 4.4), gridspec_kw=dict(width_ratios=[1, 1.15, 1.15]))
    ax = axes[0]
    ax.scatter(*p.T, c=z, cmap="RdBu", s=22, ec=NAVY, lw=0.3, vmin=-10, vmax=10)
    ax.set_aspect("equal")
    ax.set_xlim(0, 1000)
    ax.set_ylim(0, 1000)
    mapax(ax, "200 samples of a sine wave\n(wavelength 400, west to east)")
    for ax, ang, t in [(axes[1], None, "All directions"), (axes[2], 0, "West–east pairs only (±22.5°)")]:
        h, gam, n, d, g = empirical(p, z, nbins=20, maxd=900, angle=ang)
        ax.scatter(h, gam, s=30, c=NAVY)
        ax.plot(h, gam, color=BLUE, lw=1.2)
        ax.set_ylim(0, 210)
        ax.set_xlabel("Lag distance, h")
        ax.spines[["top", "right"]].set_visible(False)
        ax.set_title(t, fontsize=11.5, loc="left")
    axes[1].set_ylabel("Semivariance")
    for xv in (200, 600):
        axes[2].axvline(xv, color=CLAY, lw=1, ls="--")
    for xv in (400, 800):
        axes[2].axvline(xv, color=PINE, lw=1, ls="--")
    axes[2].text(205, 198, "½ wavelength:\nmost different", color=CLAY, fontsize=8.5, va="top")
    axes[2].text(405, 160, "1 wavelength:\nalike again", color=PINE, fontsize=8.5, va="top")
    save(fig, OUT / "sine-variograms.png")


# ---------- 8. isotropic vs anisotropic kriging of the sine surface ----------
def sine_kriging():
    p, z = sine_data()
    h, gam, n, *_ = empirical(p, z, nbins=12, maxd=300)
    nug, ps, rg = fit(h, gam, n, spherical)
    print("sine omni fit", nug, ps, rg)
    iso = lambda hh: spherical(hh, nug, ps, rg)
    # anisotropic: north-south pairs stay alike, so the major axis runs north-south (90 degrees)
    he, ge, ne, *_ = empirical(p, z, nbins=12, maxd=300, angle=0)
    nug2, ps2, rg2 = fit(he, ge, ne, spherical)
    ratio = 0.15
    print("sine EW fit", nug2, ps2, rg2, "major range", rg2 / ratio)
    an = lambda hh: spherical(hh, nug2, ps2, rg2 / ratio)
    aniso = (90, ratio)
    idw = ip.idw(p, z, SQ, 2, 12).reshape(SX.shape)
    a, _, _, _ = okrige(p, z, SQ, iso, k=16)
    b, _, _, _ = okrige(p, z, SQ, an, k=16, aniso=aniso)
    cv_iso = loocv(p, z, iso, 16)
    cv_an = loocv(p, z, an, 16, aniso)
    e_idw = []
    for i in range(len(z)):
        m = np.arange(len(z)) != i
        e_idw.append(ip.idw(p[m], z[m], p[i:i + 1], 2, 12)[0] - z[i])
    r_idw = np.sqrt(np.mean(np.square(e_idw)))
    fig, axes = plt.subplots(1, 3, figsize=(14, 5))
    for ax, Z, t in [(axes[0], idw, f"IDW (power 2, 12 neighbors)\nRMSE = {r_idw:.2f}"),
                     (axes[1], a.reshape(SX.shape), f"Kriging, isotropic\nRMSE = {cv_iso['rmse']:.2f}"),
                     (axes[2], b.reshape(SX.shape), f"Kriging, anisotropic\nRMSE = {cv_an['rmse']:.2f}")]:
        ax.imshow(Z, origin="lower", extent=(0, 1000, 0, 1000), cmap="RdBu", vmin=-10, vmax=10)
        ax.scatter(*p.T, s=5, c=NAVY, alpha=0.7)
        mapax(ax, t)
    axes[1].add_patch(Circle((880, 880), 90, fill=False, ec=NAVY, lw=1.6))
    axes[2].add_patch(Ellipse((880, 840), 50, 300, fill=False, ec=NAVY, lw=1.6))
    save(fig, OUT / "sine-kriging.png")
    print("cv idw", r_idw, "iso", cv_iso, "aniso", cv_an)


# ---------- 9. prediction and standard error on the chapter 16 surface ----------
def prediction_and_error():
    """Krige the chapter 16 samples after removing a first-order trend."""
    p, z = ip.samples()
    A = ip.poly_terms(p[:, 0], p[:, 1], 1)
    beta, *_ = np.linalg.lstsq(A, z, rcond=None)
    res = z - A @ beta
    h0, g0, n0, *_ = empirical(p, z, nbins=12, maxd=7)
    h, gam, n, *_ = empirical(p, res, nbins=12, maxd=7)
    nug, ps, rg = fit(h, gam, n, spherical)
    v = lambda hh: spherical(hh, nug, ps, rg)
    q = np.column_stack([ip.GX.ravel(), ip.GY.ravel()])

    def uk(pp, zz, qq):
        Ap = ip.poly_terms(pp[:, 0], pp[:, 1], 1)
        bb, *_ = np.linalg.lstsq(Ap, zz, rcond=None)
        r = zz - Ap @ bb
        pr, se, *_ = okrige(pp, r, qq, v, k=16)
        return pr + ip.poly_terms(qq[:, 0], qq[:, 1], 1) @ bb, se

    pred, se = uk(p, z, q)
    err, ses = [], []
    for i in range(len(z)):
        m = np.arange(len(z)) != i
        a1, s1 = uk(p[m], z[m], p[i:i + 1])
        err.append(a1[0] - z[i])
        ses.append(s1[0])
    err, ses = np.array(err), np.array(ses)
    cv = dict(me=err.mean(), rmse=np.sqrt((err ** 2).mean()), ase=ses.mean(),
              rmsse=np.sqrt(((err / ses) ** 2).mean()))
    print("trend", beta, "residual fit", nug, ps, rg, "cv", cv)
    fig, axes = plt.subplots(1, 3, figsize=(14, 4.8), gridspec_kw=dict(width_ratios=[1.1, 1, 1.1]))
    ax = axes[0]
    hf = np.linspace(0.01, 7, 200)
    ax.scatter(h0, g0, s=30, fc="white", ec=BASIN, zorder=3, label="Raw values: no sill (a trend)")
    ax.scatter(h, gam, s=34, c=NAVY, zorder=4, label="Residuals after removing the trend")
    ax.plot(hf, v(hf), color=BLUE, lw=2.2, label="Spherical model of the residuals")
    ax.set_xlabel("Lag distance, h")
    ax.set_ylabel("Semivariance")
    ax.spines[["top", "right"]].set_visible(False)
    ax.legend(frameon=False, fontsize=8.5, loc="upper left")
    ax.set_title("Semivariograms", fontsize=11.5, loc="left")
    ax = axes[1]
    ip.surf(ax, pred.reshape(ip.GX.shape), p, f"Prediction (trend + kriged residuals)\nCross-validation RMSE = {cv['rmse']:.1f}")
    ax = axes[2]
    im = ax.imshow(se.reshape(ip.GX.shape), origin="lower", extent=(0, 10, 0, 10), cmap="magma_r")
    ax.scatter(*p.T, s=14, c="white", ec=NAVY, lw=0.8)
    mapax(ax, "Prediction standard error")
    cb = fig.colorbar(im, ax=ax, fraction=0.046, pad=0.03)
    cb.ax.tick_params(labelsize=8)
    fig.subplots_adjust(wspace=0.25)
    save(fig, OUT / "prediction-error.png")
    print("se range", se.min(), se.max())


if __name__ == "__main__":
    semivariance_example()
    linear_cloud()
    anatomy()
    models()
    components()
    weights()
    sine_variograms()
    sine_kriging()
    prediction_and_error()
