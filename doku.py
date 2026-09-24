# -*- coding: utf-8 -*-
"""Uygulamanin harita dokulari. uret.py cagirir; tek basina da kosar.

Veri 0.26 derecelik hucrelerde; telefonda o cozunurlukte cizmek kiyilari
basamakli, sinif sinirlarini kare kare gosterir. Bu modul atlas kirpiminin
OLCEK kati cozunurlukte uc doku yazar (varsayilan 4x, ~0.066 derece):

  data/doku.png       RGB, kayipsiz
                      R = kara orani (0..255, kiyi yumusak) — yukseklik
                          haritasi tuvalinden, modelin kara maskesiyle ayni
                          kural (land_mask: kapali havza kara)
                      G = okyanusta kiyiya uzaklik (sig/derin tonu icin)
                      B = yumusatilmis Koppen sinif kodu (0 = yok)
  data/yukseklik.png  L, kara yuksekligi, karekok olcekte 0..en yuksek
                      (Arazi katmani; hucre degil tuval cozunurlugunde)
  data/kabartma.jpg   L, kabartma golgesi, 128 = notr. Sahibin editor
                      gorselinden (dunya/kabartma_kaynak.jpg) renk tonu
                      ayrilarak cikarilir; gorsel yoksa yukseklikten
                      hesaplanan golgeye duser.

Yumusak Koppen: her sinifin tek-sicak maskesi yuksek cozunurlukte Gauss ile
bulaniklastirilip en buyugu secilir. Sinirlar hucre kosesinden degil egriden
gecer; hucrenin kendi sinifi degismez (uygulama hucre kartinda ham sinifi
gosterir, piksel gorunumu de ham veridir).
"""
from __future__ import annotations

import os

import numpy as np
from PIL import Image
from scipy import ndimage

from motor import grid as G

OLCEK = 4


def _tuval(w):
    hm = w.heightmap
    with Image.open(hm["file"]) as im:
        can = np.asarray(im).astype(np.float64)
    kara = G.land_mask(can, float(hm["sea_level_value"]), wraps=True)
    # tuval degeri -> metre, grid.from_heightmap ile ayni esleme
    sea, vmax = float(hm["sea_level_value"]), float(can.max())
    oran = np.clip((can - sea) / (vmax - sea), 0.0, 1.0)
    if hm.get("elev_curve") is not None:
        e = np.asarray(hm["elev_curve"], dtype=np.float64)
        metre = np.interp(oran, e[:, 0], e[:, 1])
    else:
        metre = oran ** float(hm.get("elev_gamma", 1.0)) * float(hm["max_elev_m"])
    return can, kara, metre


def _kabartma_gorselden(w, cy, cx, kara_hi):
    """Editor gorselinden golge: parlaklik / kara uzerinde yavas degisen taban.

    Taban (renk tonu) 18 gorsel pikselinde normalize bulaniklikla bulunur;
    oran 1 civarinda golgeyi verir. Dagdaki parlak benekler tanh ile
    bastirilir (denemede fazla serttiler).
    """
    kb = w.heightmap.get("kabartma")
    if not kb:
        return None, None
    yol = kb["file"]
    if not os.path.isabs(yol):
        yol = os.path.join(os.path.dirname(os.path.abspath(__file__)), yol)
    if not os.path.exists(yol):
        return None, None
    with Image.open(yol) as im:
        rgb = np.asarray(im.convert("RGB")).astype(np.float32)
    L = 0.299 * rgb[..., 0] + 0.587 * rgb[..., 1] + 0.114 * rgb[..., 2]
    deniz = (rgb[..., 2] > rgb[..., 0] + 15) & (rgb[..., 2] > rgb[..., 1] - 5)
    ag = (~deniz).astype(np.float32)
    s = 18.0 * (rgb.shape[1] / 4428.0)
    taban = ndimage.gaussian_filter(np.where(deniz, 0, L), s) / np.maximum(ndimage.gaussian_filter(ag, s), 1e-3)
    oran = np.where(deniz, 1.0, L / np.maximum(taban, 1.0))
    oran = ndimage.gaussian_filter(oran, 0.8)
    gy = (cy - kb["oy"]) / kb["sy"]
    gx = (cx - kb["ox"]) / kb["sx"]
    k = ndimage.map_coordinates(oran, [gy, gx], order=1, cval=1.0)
    # ortusme denetimi: gorsel karasi ile doku karasi
    gk = ndimage.map_coordinates((~deniz).astype(np.float32), [gy, gx], order=1, cval=0.0) > 0.5
    tk = kara_hi > 0.5
    iou = float((gk & tk).sum() / max((gk | tk).sum(), 1))
    return k, iou


def _kabartma_yukseklikten(metre_hi, piksel_m):
    """Yedek: yukseklikten klasik tepe golgesi (isik kuzeybatidan)."""
    gy, gx = np.gradient(metre_hi, piksel_m)
    az, alt = np.radians(315.0), np.radians(45.0)
    egim = np.arctan(np.hypot(gx, gy) * 2.0)
    yon = np.arctan2(-gx, gy)
    h = np.sin(alt) * np.cos(egim) + np.cos(alt) * np.sin(egim) * np.cos(az - yon)
    return 1.0 + (h - np.sin(alt)) * 0.9


def uret(w, bolge: dict, K: np.ndarray, pencere, cikti_dir: str, olcek: int = OLCEK) -> dict:
    """bolge: kirpilmis bolge (bounds, w, h). K: kirpilmis sinif dizisi (h, w)."""
    h, wd = bolge["h"], bolge["w"]
    B = bolge["bounds"]
    H, W = h * olcek, wd * olcek
    lat = B[3] - (np.arange(H) + 0.5) * (B[3] - B[1]) / H
    lon = B[0] + (np.arange(W) + 0.5) * (B[2] - B[0]) / W
    LON, LAT = np.meshgrid(lon, lat)

    can, kara, metre = _tuval(w)
    CH, CW = can.shape
    cy = (90.0 - LAT) / 180.0 * CH - 0.5
    cx = (LON + 180.0) / 360.0 * CW - 0.5

    kara_hi = ndimage.map_coordinates(kara.astype(np.float32), [cy, cx], order=1, mode="nearest")
    R = np.clip(np.round(kara_hi * 255), 0, 255).astype(np.uint8)

    okyanus = kara_hi < 0.5
    uzak = ndimage.distance_transform_edt(okyanus)
    G_ = np.clip(np.round(np.sqrt(np.clip(uzak / (60.0 * olcek / 4), 0, 1)) * 255), 0, 255).astype(np.uint8)

    # yumusak Koppen
    Ku = np.kron(K, np.ones((olcek, olcek), np.uint8))
    en = np.zeros((H, W), np.float32)
    sinif = np.zeros((H, W), np.uint8)
    for kod in np.unique(K):
        if kod == 0:
            continue
        p = ndimage.gaussian_filter((Ku == kod).astype(np.float32), olcek * 0.9)
        m = p > en
        en[m] = p[m]
        sinif[m] = kod
    Bk = np.where(kara_hi > 0.02, sinif, 0).astype(np.uint8)
    Image.fromarray(np.dstack([R, G_, Bk])).save(os.path.join(cikti_dir, "doku.png"), optimize=True)

    # yukseklik (kara), karekok olcek
    m_hi = ndimage.map_coordinates(metre, [cy, cx], order=1, mode="nearest")
    ust = float(max(m_hi[kara_hi > 0.5].max(), 1.0))
    Y = np.clip(np.round(np.sqrt(np.clip(m_hi, 0, None) / ust) * 255), 0, 255).astype(np.uint8)
    Image.fromarray(Y).save(os.path.join(cikti_dir, "yukseklik.png"), optimize=True)

    # kabartma
    k, iou = _kabartma_gorselden(w, cy, cx, kara_hi)
    kaynak = "editor gorseli"
    if k is None:
        piksel_m = w.radius_km * 1000 * np.radians((B[3] - B[1]) / H)
        k = _kabartma_yukseklikten(m_hi, piksel_m)
        kaynak, iou = "yukseklik haritasi (editor gorseli yok)", None
    k = 1.0 + 0.42 * np.tanh((k - 1.0) / 0.42)          # parlak benekleri bastir
    k = np.where(kara_hi > 0.02, k, 1.0)
    KB = np.clip(np.round(128 + (k - 1.0) * 255), 0, 255).astype(np.uint8)
    Image.fromarray(KB).save(os.path.join(cikti_dir, "kabartma.jpg"), quality=86)

    return {"olcek": olcek, "w": W, "h": H, "yukseklik_ust": round(ust, 1),
            "kabartma": kaynak, "kabartma_ortusme": None if iou is None else round(iou, 4)}
