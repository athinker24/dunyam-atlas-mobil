"""Nehirlerin aylık akış rejimi: her kolun aşağı ucunda 12 aylık debi, yıllık ortalamanın yüzdesi.

    python su/rejim.py      # su/_disa.pkl ve buzul/_iklim_bugun025.npz gerekir; ~3 dk
    python su/delta.py      # deltalar su.json'a yeniden eklenir (rejim.py su.json'u baştan yazar)

Ağ (alıcı ağacı, göller) uret_su.py'nin kurduğu hâliyle `_disa.pkl`'den okunur, yeniden
çözülmez; yalnız aylık kaynak değişir. Kaynak: akim.py'nin aylık yüzey akışı (kar
erimesi ve buzul akışı dahil); göl yüzeyinde o ayın yağışı eksi göl buharlaşması.

Her ay ağ boyunca ayrı biriktirilir (nehir.debi), sonra aşağı uçta tek bir doğrusal
hazneden geçirilir: kaynaktan ağıza yolculuk ve yeraltı suyu ayın akışını geciktirir ve
yayar. Zaman sabiti τ (ay) = 0.5 + yol boyu / 2000 km (1 m/s akış ~2600 km/ay) ve yukarıda
göl varsa göl payına göre +4 aya kadar (büyük göl mevsimi düzler: St. Lawrence gibi).
Hazne aylık adımla dönemsel kararlı hâle döndürülür: yıllık ortalama korunur.

Taban akışı: akışın TABAN payı yeraltından gelir ve ayrıca YERALTI_TAU aylık bir hazneden
geçer. İlk sürümde (yalnız tek hazne) büyük nehirler kurak ayda sıfıra iniyordu, en yüksek/
en düşük ay oranı 280'e çıkıyordu; motorun yağışı Dünya'dan iki kat mevsimsel (CLAUDE.md §8)
ve toprak kovası kurak ayda hiç akış vermiyor. Küresel taban akışı payı ~%60 (günlük; Beck
vd. 2013, 3394 havza); aylık ölçekte 0.5 seçildi.
"""
import os, sys, pickle
import numpy as np
BURASI = os.path.dirname(os.path.abspath(__file__)); KOK = os.path.dirname(BURASI)
sys.path.insert(0, BURASI); sys.path.insert(0, KOK)
import akim, nehir, disa

IKLIM = os.path.join(KOK, "buzul", "_iklim_bugun025.npz")
TABAN, YERALTI_TAU = 0.5, 4.0


def ss(x, a, b):
    t = np.clip((np.asarray(x, float) - a) / (b - a), 0, 1)
    return t * t * (3 - 2 * t)


def hazne(Q, tau):
    """Q (12,) aylık giriş, tau ay: doğrusal haznenin dönemsel kararlı çıkışı, aylık adımla
    (a = e^(-1/τ)); kararlı döngüye oturana dek yıllarca döndürülür. İlk sürüm Fourier
    çözümüydü (1 / (1 + iωτ)); 12 aylık dizide Nyquist bileşeni bozuluyor, tek tek aylar
    sıfıra kırpılan bir testere salınımı çıkıyordu."""
    a = np.exp(-1.0 / max(float(tau), 1e-6))
    S = float(np.mean(Q)); out = np.zeros(12)
    for _ in range(int(np.ceil(6 * tau / 12)) + 2):
        for m in range(12):
            S = a * S + (1 - a) * Q[m]; out[m] = S
    return out


def aylik_debi(d, alici, gm, deniz, lat, lon):
    """(12, N) m³/s: her ay ağ boyunca biriktirilmiş debi (gecikmesiz)."""
    dy = 6371e3 * np.radians(abs(lat[1] - lat[0]))
    dx = (6371e3 * np.radians(lon[1] - lon[0]) * np.cos(np.radians(lat)))[:, None]
    alan = dx * dy * np.ones(gm.shape)
    sira = nehir.sira_kur(alici)
    ay_s = nehir.SANIYE_YIL / 12
    out = []
    for m in range(12):
        k = np.where(gm, d["Pay"][m] - d["Egolay"][m], d["Ray"][m]) * alan / 1000
        k[deniz] = 0
        out.append(nehir.debi(alici, sira, k, gm) / ay_s)
    gol_ust = nehir.debi(alici, sira, np.where(gm, alan, 0)) / 1e6        # yukarıdaki göl alanı km²
    havza = nehir.debi(alici, sira, np.where(deniz, 0, alan)) / 1e6
    return np.array(out), gol_ust, havza


def main():
    p = pickle.load(open(os.path.join(BURASI, "_disa.pkl"), "rb"))
    d = akim.hesapla(IKLIM)
    Qay, gol_ust, havza = aylik_debi(d, p["alici"], p["gm"], p["deniz"], p["lat"], p["lon"])
    bf = p["boy"].ravel()
    tau = 0.5 + bf / 2000.0 + 4 * ss(gol_ust / np.maximum(havza, 1), 0.005, 0.05)
    ort_y = p["q"].ravel()
    # sağlama: aylık ortalama yıllık debiyle uyuşmalı (göl hücresinde aylık kırpma farkı küçük)
    nm = ort_y >= 50
    oran = Qay.mean(0)[nm] / ort_y[nm]
    print("aylık ort / yıllık debi (Q>=50): medyan %.3f, %%5-95: %.3f-%.3f" % tuple(np.percentile(oran, [50, 5, 95])))

    def rejim(h):
        g = np.maximum(Qay[:, h], 0); t = float(tau[h])
        q = (1 - TABAN) * hazne(g, t) + TABAN * hazne(g, t + YERALTI_TAU)
        o = max(q.mean(), 1e-9)
        return [int(round(100 * v / o)) for v in np.maximum(q, 0)]
    disa.yaz(p["goller"], p["alici"], p["q"], p["boy"], p["gm"], p["deniz"], p["lat"], p["lon"], rejim=rejim)


if __name__ == "__main__":
    main()
