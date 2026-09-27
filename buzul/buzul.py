"""Buzul geçmişi: kütle dengesi ve sığ buz yaklaşımıyla (SIA) buz örtüsü.

Motorun 0.5 derecelik aylık iklimi (iklim_kos.py) kaynak çözünürlükteki
araziye (4096x2048, ~0.088 derece) lapse ile indirgenir; buz yüzeyi
yükseldikçe sıcaklık düşer (yükseklik-kütle dengesi geri beslemesi).

    python buzul/buzul.py _iklim_6.npz --deniz -120 --yil 20000 --cikti _buz_6.npz

Kütle dengesi (PDD, Reeh 1991): aylık ortalama sıcaklık etrafında
sigma = 5 K normal dağılım; kar payı -2..+4 °C arası doğrusal (uygulamanın
kar kovasıyla aynı eşikler); erime kar 3, buz 8 mm su/K/gün; eriyen karın
%60'ı yeniden donar. Buz akışı: Glen yasası n = 3, A = 1e-16 Pa^-3 yıl^-1,
kaymasız SIA, Mahaffy şeması. Okyanusa ulaşan buz buzdağı olarak kopar
(H = 0; buz rafı yok).
"""
import argparse, os, sys
import numpy as np
from PIL import Image
from scipy.special import erfc
from scipy.interpolate import RegularGridInterpolator

BURASI = os.path.dirname(os.path.abspath(__file__))
KOK = os.path.dirname(BURASI)
sys.path.insert(0, KOK)

R = 6371e3
RHO_I, RHO_W, GRAV = 917.0, 1000.0, 9.81
GLEN_A, GLEN_N = 1e-16, 3
LAPSE = 5.2e-3              # motorun etkin yüzey lapse'ı (K/m)
SIGMA = 5.0
DDF_KAR, DDF_BUZ, YENIDEN = 3.0, 8.0, 0.6
AY_GUN = 365.25 / 12
KAR_ALT, KAR_UST = -2.0, 4.0
KUTU = (70.0, -15.0, -56.0, 56.0)   # kuzey, güney, batı, doğu


def arazi(deniz=0.0):
    """Kaynak çözünürlükte yükseklik (m), motorun eşlemesiyle birebir."""
    import json
    w = json.load(open(os.path.join(KOK, "dunya", "dunyam.json"), encoding="utf-8"))
    hm = w["heightmap"]
    d = np.asarray(Image.open(os.path.join(KOK, "dunya", "dunyam_heightmap.png")), dtype=np.float64)
    H, W = d.shape
    sea, vmin, vmax = hm["sea_level_value"], d.min(), d.max()
    egri = np.array(hm["elev_curve"]).T
    oran = np.maximum(d - sea, 0) / (vmax - sea)
    ust = np.interp(oran, egri[0], egri[1])
    alt = np.maximum(sea - d, 0) / (sea - vmin) * abs(hm["max_depth_m"])
    z = np.where(d >= sea, ust, -alt) - deniz
    lat = 90 - (np.arange(H) + 0.5) * 180 / H
    lon = -180 + (np.arange(W) + 0.5) * 360 / W
    r = (lat <= KUTU[0]) & (lat >= KUTU[1])
    c = (lon >= KUTU[2]) & (lon <= KUTU[3])
    return z[r][:, c], lat[r], lon[c]


def iklim_indir(npz, lat, lon):
    k = np.load(npz)
    clat, clon = k["lat"], k["lon"]
    # RegularGridInterpolator artan eksen ister
    o = np.argsort(clat)
    P = np.meshgrid(lat, lon, indexing="ij")
    nokta = np.stack([P[0].ravel(), P[1].ravel()], -1)
    def ic(a):
        f = RegularGridInterpolator((clat[o], clon), a[o], bounds_error=False, fill_value=None)
        return f(nokta).reshape(len(lat), len(lon))
    zc = ic(np.maximum(k["elev"], 0.0))
    T = np.stack([ic(k["T"][m]) + LAPSE * zc for m in range(12)])   # deniz seviyesine indir
    Pm = np.stack([np.maximum(ic(k["P"][m]), 0) for m in range(12)])
    return T, Pm   # T: deniz seviyesine indirgenmiş (yüzeyde: T - LAPSE*s)


def denge(T0, P, s):
    """Yıllık kütle dengesi, m buz/yıl. T0 deniz seviyesine indirgenmiş, s yüzey."""
    acc = np.zeros_like(s); pdd = np.zeros_like(s)
    for m in range(12):
        T = T0[m] - LAPSE * s
        acc += P[m] * np.clip((KAR_UST - T) / (KAR_UST - KAR_ALT), 0, 1)
        pdd += AY_GUN * (SIGMA / np.sqrt(2 * np.pi) * np.exp(-T**2 / (2 * SIGMA**2))
                         + T / 2 * erfc(-T / (np.sqrt(2) * SIGMA)))
    kar_erir = np.minimum(acc, DDF_KAR * pdd)
    kalan_pdd = pdd - kar_erir / DDF_KAR
    buz_erir = DDF_BUZ * kalan_pdd
    b = acc - (1 - YENIDEN) * kar_erir - buz_erir      # mm su
    return b / 1000 * RHO_W / RHO_I, acc, pdd


def sia(bed, T0, P, lat, lon, yil, H0=None, kayit=500):
    ny, nx = bed.shape
    dy = R * np.radians(abs(lat[1] - lat[0]))
    dx = (R * np.radians(lon[1] - lon[0]) * np.cos(np.radians(lat)))[:, None] * np.ones((1, nx))
    deniz = bed < 0
    H = np.zeros_like(bed) if H0 is None else H0.copy()
    Gam = 2 * GLEN_A * (RHO_I * GRAV) ** GLEN_N / (GLEN_N + 2)
    t, Hmax, sonra = 0.0, H.copy(), 0.0
    dxm = 0.5 * (dx[:, 1:] + dx[:, :-1])
    while t < yil:
        s = bed + H
        b, _, _ = denge(T0, P, np.maximum(s, 0))
        # x yüzleri
        Hx = 0.5 * (H[:, 1:] + H[:, :-1])
        sx = (s[:, 1:] - s[:, :-1]) / dxm
        syx = 0.25 * ((np.roll(s, -1, 0) - np.roll(s, 1, 0))[:, 1:] + (np.roll(s, -1, 0) - np.roll(s, 1, 0))[:, :-1]) / (2 * dy)
        Dx = Gam * Hx ** (GLEN_N + 2) * (sx**2 + syx**2) ** ((GLEN_N - 1) / 2)
        Hy = 0.5 * (H[1:] + H[:-1])
        sy = (s[1:] - s[:-1]) / dy
        sxy = 0.25 * ((np.roll(s, -1, 1) - np.roll(s, 1, 1))[1:] + (np.roll(s, -1, 1) - np.roll(s, 1, 1))[:-1]) / (2 * 0.5 * (dx[1:] + dx[:-1]))
        Dy = Gam * Hy ** (GLEN_N + 2) * (sy**2 + sxy**2) ** ((GLEN_N - 1) / 2)
        Dm = max(Dx.max(), Dy.max(), 1.0)
        dt = min(0.2 * min(dx.min(), dy) ** 2 / Dm, 50.0, yil - t)
        adim = locals().get("adim", 0) + 1
        qx = -Dx * sx; qy = -Dy * sy
        div = np.zeros_like(H)
        div[:, 1:-1] += (qx[:, 1:] - qx[:, :-1]) / dx[:, 1:-1]
        div[1:-1] += (qy[1:] - qy[:-1]) / dy
        H = np.maximum(H + dt * (b - div), 0)
        H[deniz & (H < -bed * RHO_W / RHO_I)] = 0    # yüzen buz kopar
        H[:, [0, -1]] = 0; H[[0, -1]] = 0
        Hmax = np.maximum(Hmax, H)
        t += dt
        if t >= sonra:
            print("  %6.0f yil  buz %.2f Mkm2  hacim %.2f Mkm3  dt %.2f" % (
                t, (H > 1).sum() * 0 + (dx * dy * (H > 1)).sum() / 1e12,
                (dx * dy * H).sum() / 1e18 * 1e3 / 1e3 / 1e3 * 1e3, dt), flush=True)
            sonra += kayit
    return H, Hmax


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("iklim")
    ap.add_argument("--deniz", type=float, default=0.0)
    ap.add_argument("--yil", type=float, default=20000)
    ap.add_argument("--cikti", required=True)
    a = ap.parse_args()
    z, lat, lon = arazi(a.deniz)
    T0, P = iklim_indir(a.iklim, lat, lon)
    b0, acc, pdd = denge(T0, P, np.maximum(z, 0))
    kara = z >= 0
    print("arazi", z.shape, "pozitif denge kara payi (hucre) %.2f%%" % (100 * (b0 > 0)[kara].mean()))
    H, Hmax = sia(z, T0, P, lat, lon, a.yil)
    np.savez_compressed(a.cikti, H=H.astype(np.float32), b0=b0.astype(np.float32),
                        z=z.astype(np.float32), lat=lat, lon=lon)
