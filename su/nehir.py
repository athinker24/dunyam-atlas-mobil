"""Nehirler: göllerle birlikte akış yönlendirmesi ve debi.

Yüzey = arazi, göl hücrelerinde göl seviyesi. Öncelik sırasıyla su basma
(Barnes 2014) denizden ve KAPALI göllerden başlar; her hücre suyunu kendisine
ulaşılan komşuya verir. Böylece çukurlar (aşınmış eşikler dahil) düz bir
yataktan geçilir, çıkışlı göller eşiklerinden taşar, kapalı göller son
noktadır. Debi: kara hücrelerinde akış R, göl hücrelerinde P − E_göl
(negatif olabilir, akış sıfırın altına inmez).
"""
import heapq, os
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
    sira = np.array(sira, dtype=np.int64)
    # Aşınmış çukur (doldurulmuş ama göl olmayan): su önce çukurun dibine
    # iner, oradan TEK kanalla (su basma yolu) çıkar. Yalnız su basma yolu
    # kullanılınca düz tabanda her kol ayrı yol çiziyor, örgülü bir yumak
    # çıkıyordu.
    dolgu = np.empty(ny * nx); yf = yuz.ravel()
    dolgu[sira[0]] = yf[sira[0]]
    # dolgu seviyesi: bir hücrenin seviyesi = max(kendisi, alıcısının dolgusu); sıra alıcıyı önce verir
    for c in sira:
        r = alici[c]
        dolgu[c] = yf[c] if r < 0 else max(yf[c], dolgu[r])
    p = np.pad(yuz, 1, constant_values=np.inf)
    en = yuz.copy(); ini = np.full(ny * nx, -1, dtype=np.int64)
    ii, jj = np.indices((ny, nx))
    for di, dj in D8:
        k = p[1 + di:ny + 1 + di, 1 + dj:nx + 1 + dj]
        mesafe = np.hypot(di, dj)
        e = (yuz - k) / mesafe
        d = (k < yuz) & (e > np.where(en < yuz, (yuz - en), 0))
        en = np.where(d, yuz - e, en)
        ini = np.where(d.ravel(), ((ii + di) * nx + (jj + dj)).ravel(), ini)
    cukur = dolgu > yf + 1e-6
    tohumf = tohum.ravel()
    yol = np.zeros(ny * nx, bool)
    dip = np.where(cukur & (ini < 0) & ~tohumf)[0]
    for c in dip:
        while c >= 0 and not yol[c]:
            yol[c] = True
            if not cukur[c]:
                break
            c = alici[c]
    yeni = np.where(yol | (ini < 0), alici, ini)
    yeni[tohumf] = -1
    # yeni ağacın sırası: köklerden yukarı genişlik öncelikli
    kok = np.where(yeni < 0)[0]
    geçerli = yeni >= 0
    o = np.argsort(yeni[geçerli], kind="stable"); cocuk = np.where(geçerli)[0][o]; ust = yeni[cocuk]
    bas = np.searchsorted(ust, np.arange(ny * nx)); son = np.searchsorted(ust, np.arange(ny * nx), side="right")
    sira2 = list(kok); i = 0
    while i < len(sira2):
        c = sira2[i]; sira2.extend(cocuk[bas[c]:son[c]]); i += 1
    return yeni, np.array(sira2, dtype=np.int64)


def debi(alici, sira, kaynak, gol=None):
    """kaynak m3/yıl; yukarıdan aşağı biriktirir (sıranın tersi).

    Göl hücrelerinde eksi (buharlaşma) kırpılmaz, gölün çıkışına kadar
    taşınır: gölün bütün yüzeyinin buharlaşması çıkıştan düşülür. Önce her
    hücrede sıfıra kırpılıyordu; yalnız nehrin geçtiği göl hücrelerinin
    buharlaşması düşülüyor, çıkış debisi ~%60 fazla çıkıyordu (tatlı gölde
    397 yerine su dengesinden ~245 m³/s). Kara hücresinde kırpılır."""
    q = kaynak.ravel().astype(np.float64).copy()
    g = np.zeros(q.size, bool) if gol is None else gol.ravel()
    for c in sira[::-1]:
        r = alici[c]
        if q[c] < 0 and not (g[c] and r >= 0 and g[r]):
            q[c] = 0.0
        if r >= 0:
            q[r] += q[c]
    return q


def sira_kur(alici):
    """Alıcı ağacı için kökten yukarı sıra."""
    n = alici.size
    kok = np.where(alici < 0)[0]
    g = alici >= 0
    o = np.argsort(alici[g], kind="stable"); cocuk = np.where(g)[0][o]; ust = alici[cocuk]
    bas = np.searchsorted(ust, np.arange(n)); son = np.searchsorted(ust, np.arange(n), side="right")
    sira = list(kok); i = 0
    while i < len(sira):
        c = sira[i]; sira.extend(cocuk[bas[c]:son[c]]); i += 1
    return np.array(sira, dtype=np.int64)


def yana_katil(alici, q, yuz, shape, esik=20.0, oran=2.0, tolerans=15.0):
    """Yan yana paralel akan dereyi büyük komşusuna katar.

    Izgarada bir hücre arayla paralel akan iki dere hiç birleşmez (D8'in
    kusuru); gerçekte küçüğü büyüğüne katılır. Dere hücresinin 8 komşusundan
    debisi en az oran katı olan ve en çok tolerans m yüksekte olanı varsa,
    küçük dere oraya yönlendirilir. Büyüğün debisi küçüğünkinden fazla olduğu
    için büyük yol küçüğün içinden geçemez: döngü oluşmaz.
    """
    ny, nx = shape
    qf = q.ravel(); yf = yuz.ravel(); yeni = alici.copy()
    aday = np.where(qf >= esik)[0]
    for c in aday:
        i, j = divmod(int(c), nx)
        en, hedef = qf[c] * oran, -1
        for di, dj in D8:
            a, b = i + di, j + dj
            if 0 <= a < ny and 0 <= b < nx:
                k = a * nx + b
                if k != alici[c] and alici[k] != c and qf[k] > en and yf[k] <= yf[c] + tolerans:
                    en, hedef = qf[k], k
        if hedef >= 0:
            yeni[c] = hedef
    return yeni


def paralel_birlestir(alici, q, yuz, shape, yasak=None, esik=20.0, yaricap=4, tolerans=15.0, oran=1.1):
    """Birbirine yakın paralel akan dereleri birleştirir (27 Eylül, sahibi).

    Yumuşatılmış dağ eteği düzgün bir eğik düzlem; su orada hücreden hücreye
    dümdüz iner ve 200 km boyunca 6-12 km arayla akan, hiç birleşmeyen dere
    tarakları çıkıyordu. Hack yasasına göre 200 km'lik bir nehrin havzası
    ~4.000 km², ortalama eni 20-25 km: gerçekte bunlar birleşir.

    yana_katil'in genişletilmişi: dere hücresi, `yaricap` hücre içinde (bir
    hücre ~9 km) debisi kendisininkinin en az `oran` katı olan BAŞKA bir
    derenin hücresine katılır. Koşullar: hedef en çok `tolerans` m yüksekte,
    aradaki hücreler de (sırt aşılmasın) ikisinin yükseğinden en çok
    `tolerans` m yüksekte, hedef kendi aşağı yolunda değil. Hedefin debisi
    büyük olduğu için döngü oluşmaz (aşağı yolda debi azalmaz).
    """
    ny, nx = shape
    qf = q.ravel(); yf = yuz.ravel(); yeni = alici.copy()
    yf2 = yf.reshape(shape)
    kom = [(di, dj) for di in range(-yaricap, yaricap + 1) for dj in range(-yaricap, yaricap + 1)
           if (di or dj) and di * di + dj * dj <= yaricap * yaricap + 1]
    aday = np.where(qf >= esik)[0]
    if yasak is not None:
        aday = aday[~yasak.ravel()[aday]]
    say = 0
    for c in aday:
        i, j = divmod(int(c), nx)
        # kendi aşağı yolu (yarıçapın birkaç katı kadar)
        asagi = set(); x = int(c)
        for _ in range(4 * yaricap + 2):
            x = int(alici[x])
            if x < 0:
                break
            asagi.add(x)
        en, hedef = qf[c] * oran, -1
        for di, dj in kom:
            a, b = i + di, j + dj
            if not (0 <= a < ny and 0 <= b < nx):
                continue
            k = a * nx + b
            if qf[k] <= en or k in asagi or alici[k] == c or yf[k] > yf[c] + tolerans:
                continue
            if yasak is not None and yasak[a, b]:
                continue
            # aradaki hücreler: sırt aşılmasın
            n = max(abs(di), abs(dj)); ust = max(yf[c], yf[k]) + tolerans; gec = True
            for t in range(1, n):
                ii = i + round(di * t / n); jj = j + round(dj * t / n)
                if yf2[ii, jj] > ust:
                    gec = False; break
            if gec:
                en, hedef = qf[k], k
        if hedef >= 0 and hedef != alici[c]:
            yeni[c] = hedef; say += 1
    return yeni, say
