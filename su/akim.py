"""Yüzey akışı: aylık su dengesi (kar kovası + toprak kovası).

İklim motorunun aylık sıcaklık ve yağışı kaynak araziye (~0.088°) indirilir
(buzul/buzul.py ile aynı: sıcaklık 5.2 K/km lapse, yağış ara değerleme).

Potansiyel buharlaşma Oudin vd. (2005): PE = Re/(λρ) · (T+5)/100, T > −5 °C.
Yalnız atmosfer üstü ışınım (gezegenin eğikliği ve yılından, motorun
daily_insolation'ı) ve sıcaklık ister; akış modellemesi için 27 formül
arasında en iyilerden biri çıkmış, Penman'a yakın. Thornthwaite kurak
iklimde buharlaşmayı az tahmin eder, burada kurak plato önemli.

Kar: uygulamanın kar kovasıyla aynı (kar payı −2..+4 °C, erime 75 mm/°C/ay).
Toprak: Thornthwaite-Mather kovası, kapasite 150 mm; gerçek buharlaşma
toprak nemiyle doğrusal azalır. Hiç erimeyen kar (buzul) dengeli hâlde buz
olarak aşağı akıp erir: yıllık birikimi akışa sayılır.
Göl yüzeyi buharlaşması: tamamlayıcı ilişki (Bouchet 1963; Morton 1983
CRLE): kurak havada açık su, çevre toprağın buharlaştıramadığı enerjiyi de
alır, E_göl = 2·PE − AET (nemli yerde ≈ PE). Kurak havzalarda Aral ~1000,
Hazar ~1000 mm/yıl mertebesine oturur; yalnız PE kullanılınca %30-40 az
çıkıyordu. Ay ortalaması 0 °C altındaysa buz örtüsü, 0.
"""
import json, os, sys
import numpy as np
BURASI = os.path.dirname(os.path.abspath(__file__))
KOK = os.path.dirname(BURASI)
sys.path.insert(0, KOK); sys.path.insert(0, os.path.join(KOK, "buzul"))
import buzul as B
from motor import temperature
import uret

TOPRAK = 150.0
KAR_ALT, KAR_UST, ERIME = -2.0, 4.0, 75.0


def ay_gunleri(w):
    y = w.year_length_days
    return (np.arange(12) + 0.5) * y / 12, y / 12


def hesapla(iklim_npz, deniz=0.0):
    z, lat, lon = B.arazi(deniz)
    T0, P = B.iklim_indir(iklim_npz, lat, lon)
    s = np.maximum(z, 0)
    T = T0 - B.LAPSE * s[None]
    w = uret.dunya_yukle()
    gunler, ay_gun = ay_gunleri(w)
    Re = temperature.daily_insolation(lat, gunler, w) * 0.0864      # MJ/m2/gün, (12, nlat)
    PE = np.where(T > -5, Re[:, :, None] / 2.45 * (T + 5) / 100, 0.0) * ay_gun   # mm/ay
    ny, nx = z.shape
    kar = np.zeros((ny, nx)); top = np.full((ny, nx), TOPRAK)
    R = np.zeros((ny, nx)); AET = np.zeros((ny, nx)); kalan_kar = np.zeros((ny, nx)); Egol = np.zeros((ny, nx))
    for tur in range(4):
        if tur == 3:
            R[:] = 0; AET[:] = 0; Egol[:] = 0; kar0 = kar.copy()
        for m in range(12):
            frac = np.clip((KAR_UST - T[m]) / (KAR_UST - KAR_ALT), 0, 1)
            yag_kar = P[m] * frac; yag_su = P[m] - yag_kar
            kar += yag_kar
            erime = np.minimum(kar, ERIME * np.maximum(T[m], 0)); kar -= erime
            su = yag_su + erime
            # toprak: önce buharlaşma talebi yağıştan, eksik topraktan orantılı
            fazla = su - PE[m]
            et = np.where(fazla >= 0, PE[m], su + top * (1 - np.exp(fazla / TOPRAK)))
            top = np.where(fazla >= 0, top + fazla, top * np.exp(fazla / TOPRAK))
            tas = np.maximum(top - TOPRAK, 0); top -= tas
            if tur == 3:
                R += tas; AET += et
                Egol += np.where(T[m] > 0, np.maximum(PE[m], 2 * PE[m] - et), 0)
    kalan_kar = np.maximum(kar - kar0, 0)          # yıl boyunca biriken: buzul akışı
    R += kalan_kar
    kar[:] = np.minimum(kar, kar0)
    return dict(z=z, lat=lat, lon=lon, P=P.sum(0), PE=PE.sum(0), AET=AET, R=R, Egol=Egol,
                Pay=P, Tay=T, PEay=PE, buzul=kalan_kar > 0)


if __name__ == "__main__":
    d = hesapla(sys.argv[1] if len(sys.argv) > 1 else os.path.join(KOK, "buzul", "_iklim_bugun.npz"))
    kara = d["z"] >= 0
    wgt = np.cos(np.radians(d["lat"]))[:, None] * kara
    ort = lambda a: float((a * wgt).sum() / wgt.sum())
    print("kara ort. yağış %.0f  PE %.0f  gerçek buh. %.0f  akış %.0f  göl buh. %.0f mm/yıl; akış/yağış %.2f"
          % (ort(d["P"]), ort(d["PE"]), ort(d["AET"]), ort(d["R"]), ort(d["Egol"]), ort(d["R"]) / ort(d["P"])))
    np.savez_compressed(os.path.join(BURASI, "_akim.npz"), **{k: np.asarray(v, dtype=np.float32) if np.asarray(v).dtype == np.float64 else v for k, v in d.items() if k not in ("Pay", "Tay", "PEay")})
