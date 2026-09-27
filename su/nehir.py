"""Nehirler: göllerle birlikte akış yönlendirmesi ve debi.

Yüzey = arazi, göl hücrelerinde göl seviyesi. Öncelik sırasıyla su basma
(Barnes 2014) denizden ve KAPALI göllerden başlar; her hücre suyunu kendisine
ulaşılan komşuya verir. Böylece çukurlar (aşınmış eşikler dahil) düz bir
yataktan geçilir, çıkışlı göller eşiklerinden taşar, kapalı göller son
noktadır. Debi: kara hücrelerinde akış R, göl hücrelerinde P − E_göl
(negatif olabilir, akış sıfırın altına inmez).
"""
import heapq, os, sys
import numpy as np
BURASI = os.path.dirname(os.path.abspath(__file__))
D8 = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 1), (1, -1), (1, 0), (1, 1)]
SANIYE_YIL = 365.25 * 86400


def yonlendir(z, deniz, seviye, kapali):
    ny, nx = z.shape
    yuz = np.where(np.isfinite(seviye), seviye, z)
    alici = np.full(ny * nx, -1, dtype=np.int64)
    gorulen = np.zeros((ny, nx), bool)
    kenar = np.zeros_like(deniz); kenar[[0, -1]] = True; kenar[:, [0, -1]] = True
    tohum = deniz | kapali | kenar
    # Anahtar (seviye, özgün yükseklik): doldurulmuş düzlükte (aşınmış çukur,
    # göl) sıra özgün araziye göre; su çukurun taban hattını izler. Yalnız
    # sayaçla sıralayınca düzlükte cetvelle çizilmiş ışınlar çıkıyordu.
    h = [(float(yuz[i, j]), float(z[i, j]), 0, int(i), int(j)) for i, j in zip(*np.where(tohum))]
    heapq.heapify(h); gorulen |= tohum
    sira = []; say = 0
    while h:
        v, _, _, i, j = heapq.heappop(h)
        sira.append(i * nx + j)
        for di, dj in D8:
            a, b = i + di, j + dj
            if 0 <= a < ny and 0 <= b < nx and not gorulen[a, b]:
                gorulen[a, b] = True
                alici[a * nx + b] = i * nx + j
                say += 1
                heapq.heappush(h, (max(float(yuz[a, b]), v), float(z[a, b]), say, a, b))
    return alici, np.array(sira, dtype=np.int64)


def debi(alici, sira, kaynak):
    """kaynak m3/yıl; yukarıdan aşağı biriktirir (sıranın tersi)."""
    q = kaynak.ravel().astype(np.float64).copy()
    for c in sira[::-1]:
        r = alici[c]
        if q[c] < 0:
            q[c] = 0.0
        if r >= 0:
            q[r] += q[c]
    return q
