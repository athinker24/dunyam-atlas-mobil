"""Göller: çukur ağacı ve su dengesi (Fill-Spill-Merge, Barnes vd. 2021).

1. Taşma ağacı: kara hücreleri alçaktan yükseğe sırayla "su basar"
   (union-find). Her yerel en düşük nokta bir yaprak çukur; iki çukur bir
   eşikte birleşince ebeveyn düğüm; denize değen çukur denize bağlanır.
2. Su dengesi: bir çukurun gölü, yatağındaki hücreler için
   Σ(E_göl − P + R) toplamı çukura gelen akışa eşit olunca dengede. Gelen
   akış hepsini doyurursa göl eşiğe kadar dolar ve fazlası eşikten kardeş
   çukura ya da denize taşar. İki kardeş de doluysa birleşip tek göl olurlar.
3. Taşan su kardeşin hangi yaprağına düşer: eşik hücresinin o yandaki
   komşusundan en dik iniş yolu.
Sonuç: her göl için seviye, alan, hacim, derinlik, çıkışlı mı kapalı mı.
"""
import os, sys, time
import numpy as np
BURASI = os.path.dirname(os.path.abspath(__file__))

D8 = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 1), (1, -1), (1, 0), (1, 1)]
DENIZ = 0


def dik_inis(z):
    """Her hücrenin en düşük komşusu (kendinden alçaksa), yoksa kendisi."""
    ny, nx = z.shape
    p = np.pad(z, 1, constant_values=np.inf)
    en = z.copy(); hedef = np.arange(ny * nx).reshape(ny, nx)
    ii, jj = np.indices((ny, nx))
    for di, dj in D8:
        k = p[1 + di:ny + 1 + di, 1 + dj:nx + 1 + dj]
        d = k < en
        en = np.where(d, k, en)
        hedef = np.where(d, (ii + di) * nx + (jj + dj), hedef)
    return hedef.ravel()


def son_nokta(hedef):
    h = hedef.copy()
    while True:
        h2 = h[h]
        if np.array_equal(h2, h):
            return h
        h = h2


def agac(z, deniz):
    """Taşma ağacı. Düğüm 0 = deniz."""
    ny, nx = z.shape
    zf = z.ravel(); N = zf.size
    dugum_hucre = np.full(N, -1, dtype=np.int64)     # hücrenin eklendiği andaki düğüm
    dugum_hucre[deniz.ravel()] = DENIZ
    uf = [0]                                           # union-find: düğüm -> temsilci düğüm
    cocuk = [None]; esik_z = [np.inf]; esik_h = [-1]; ebeveyn = [-1]; kardes_giris = [None]
    deniz_giris = {}                                   # denize bağlanan düğüm -> eşiğin öbür yanındaki hücre
    def bul(a):
        r = a
        while uf[r] != r:
            r = uf[r]
        while uf[a] != r:
            uf[a], a = r, uf[a]
        return r
    kok_dugum = {}                                     # temsilci -> o bileşenin güncel kök düğümü
    kok_dugum[0] = 0
    sira = np.argsort(zf, kind="stable")
    sira = sira[~deniz.ravel()[sira]]
    for c in sira:
        i, j = divmod(int(c), nx)
        komsu_kok = {}
        for di, dj in D8:
            a, b = i + di, j + dj
            if 0 <= a < ny and 0 <= b < nx:
                k = a * nx + b
                d = dugum_hucre[k]
                if d >= 0:
                    r = bul(d)
                    if r not in komsu_kok:
                        komsu_kok[r] = k
        if not komsu_kok:
            n = len(uf); uf.append(n); cocuk.append(None); esik_z.append(np.inf); esik_h.append(-1)
            ebeveyn.append(-1); kardes_giris.append(None); kok_dugum[n] = n
            dugum_hucre[c] = n
            continue
        kokler = list(komsu_kok.items())
        # önce deniz (varsa), sonra diğerleri
        kokler.sort(key=lambda x: x[0] != bul(0))
        r0, k0 = kokler[0]
        for r1, k1 in kokler[1:]:
            ra, rb = bul(r0), bul(r1)
            if ra == rb:
                continue
            na, nb = kok_dugum[ra], kok_dugum[rb]
            if ra == bul(0) or rb == bul(0):
                x = nb if ra == bul(0) else na
                esik_z[x] = zf[c]; esik_h[x] = c; ebeveyn[x] = 0
                deniz_giris[x] = k0 if ra == bul(0) else k1
                uf[bul(x) if False else (rb if ra == bul(0) else ra)] = bul(0)
                continue
            n = len(uf); uf.append(n)
            cocuk.append((na, nb)); esik_z.append(np.inf); esik_h.append(-1); ebeveyn.append(-1)
            # taşan su kardeşin hangi hücresine girer: o yandaki komşu
            kardes_giris.append((k1 if bul(dugum_hucre[k1]) == rb else k0, k0 if bul(dugum_hucre[k0]) == ra else k1))
            for x in (na, nb):
                esik_z[x] = zf[c]; esik_h[x] = c; ebeveyn[x] = n
            uf[ra] = n; uf[rb] = n
            kok_dugum[n] = n
            r0 = n
        dugum_hucre[c] = kok_dugum[bul(r0)]
    return dict(dugum_hucre=dugum_hucre, cocuk=cocuk, esik_z=np.array(esik_z), esik_h=np.array(esik_h),
                ebeveyn=np.array(ebeveyn), kardes_giris=kardes_giris, deniz_giris=deniz_giris)


def coz(z, deniz, R, P, E, alan, asinma=0.0):
    """R, P, E mm/yıl; alan m2. Döner: göl maskesi, seviye, göl listesi."""
    t0 = time.time()
    A = agac(z, deniz)
    print("  ağaç: %d düğüm, %.0fs" % (len(A["cocuk"]), time.time() - t0), flush=True)
    ny, nx = z.shape; zf = z.ravel()
    dh = A["dugum_hucre"]; cocuk = A["cocuk"]; M = len(cocuk)
    Rv = (R * alan / 1000).ravel()                      # m3/yıl
    Kv = ((E - P + R) * alan / 1000).ravel()            # göl hücresi olunca "maliyet"
    # akış çukura: dik iniş son noktasının düğümü
    son = son_nokta(dik_inis(np.where(deniz, -1e9, z)))
    yaprak_akis = None
    kendi_K = np.bincount(np.maximum(dh, 0), weights=np.where(dh > 0, Kv, 0), minlength=M)
    # son sıra: çocuklar ebeveynden önce (düğümler oluşturulma sırasında zaten öyle)
    yaprak_mi = np.array([c is None for c in cocuk])
    Stop = kendi_K.copy()
    for n in range(1, M):
        if cocuk[n] is not None:
            a, b = cocuk[n]; Stop[n] += Stop[a] + Stop[b]
    # taşan suyun kardeşte düştüğü yaprak
    ebeveyn = A["ebeveyn"]
    def altinda(yap, hedef):
        while yap > 0:
            if yap == hedef:
                return True
            yap = ebeveyn[yap]
        return False
    # her düğümün en alçak yaprağı (yedek giriş)
    en_alcak = list(range(M)); en_z = np.full(M, np.inf)
    for c in np.where(dh > 0)[0]:
        if yaprak_mi[dh[c]] and zf[c] < en_z[dh[c]]:
            en_z[dh[c]] = zf[c]
    for n in range(1, M):
        if cocuk[n] is not None:
            a, b = cocuk[n]
            en_alcak[n] = en_alcak[a] if en_z[en_alcak[a]] <= en_z[en_alcak[b]] else en_alcak[b]
            en_z[n] = min(en_z[a], en_z[b])
    yap_of = np.array(en_alcak)
    hedef_d = dh[son]
    yaprak_akis = np.bincount(np.where(hedef_d > 0, yap_of[np.maximum(hedef_d, 0)], 0), weights=np.where(hedef_d > 0, Rv, 0), minlength=M)
    giris_yaprak = [None] * M
    yanlis = 0
    for n in range(1, M):
        if cocuk[n] is not None:
            a, b = cocuk[n]
            ka, kb = A["kardes_giris"][n]   # (b tarafı giriş, a tarafı giriş)
            gb, ga = int(yap_of[max(dh[son[ka]], 0)]), int(yap_of[max(dh[son[kb]], 0)])
            if not altinda(gb, b):
                gb = en_alcak[b]; yanlis += 1
            if not altinda(ga, a):
                ga = en_alcak[a]; yanlis += 1
            giris_yaprak[n] = (gb, ga)
    print("  giriş düzeltilen:", yanlis, flush=True)
    # Çözüm yukarıdan aşağı: bir alt ağaca ulaşan toplam su W, kapasitesi
    # S'yi (göl yatağının Σ(E−P+R)'si) aşarsa alt ağacın hepsi dolar, çünkü
    # su alt ağacın eşiğinden ancak içindeki bütün çukurlar dolunca çıkar.
    # Bir çocuğun fazlası kardeşine, eşik hücresinin o yandaki yaprağından
    # girer. Böylece her düğümün suyu bir kez hesaplanır.
    Rsub = yaprak_akis.copy()
    for n in range(1, M):
        if cocuk[n] is not None:
            a, b = cocuk[n]; Rsub[n] = Rsub[a] + Rsub[b]
    # Eşik aşınması: çukur derinliği (eşik − taban) asinma'dan azsa taşan
    # su eşiği zamanla kazmış sayılır; çukur su tutmaz, su geçer. (Kapalı
    # sığ çukurları da kapsar: kapsamayınca kurak bölgelerde binlerce km²
    # 3 m'lik tuz tavası çıkıp göl payı %3.3'e fırlıyordu.)
    derinlik = np.where(np.isfinite(A["esik_z"]), A["esik_z"] - np.where(np.isfinite(en_z), en_z, 0), np.inf)
    silik = np.zeros(M, bool); silik[1:] = derinlik[1:] < asinma
    Scap = np.where(silik, -np.inf, Stop); Scap[0] = np.inf
    Suse = np.where(silik, 0.0, Stop)      # silik çukur su tüketmez, hepsi geçer
    tin = np.zeros(M, np.int64); tout = np.zeros(M, np.int64); saat = 0
    kokler = [n for n in range(1, M) if A["ebeveyn"][n] <= 0]
    for r in kokler:
        yig = [(r, 0)]
        while yig:
            n, durum = yig.pop()
            if durum == 0:
                tin[n] = saat; saat += 1; yig.append((n, 1))
                if cocuk[n] is not None:
                    yig.append((cocuk[n][0], 0)); yig.append((cocuk[n][1], 0))
            else:
                tout[n] = saat; saat += 1
    icinde = lambda y, n: tin[n] <= tin[y] and tout[y] <= tout[n]
    # Denize bağlanan bir kökün taşan suyu doğrudan denize gitmeyebilir:
    # eşiğin öbür yanından inip denize bağlı başka bir kökün gölüne düşebilir
    # (ör. plato suyu, çıkışı boğaza açılan tatlı göle). O yüzden kökler
    # arası taşma da izlenir; kökler, taşma miktarları sabitlenene dek
    # yeniden çözülür (taşma yalnız artar, yakınsar).
    # Hedef: eşiğin öbür yanından, denizden su basma yolunu (yalnız deniz
    # tohumlu) aşağı izle; ilk girilen BAŞKA kökün çukurunda o çukurun dibine
    # in. Yalnız en dik inişle bakılınca iniş bazen vericinin kendi çukuruna
    # geri dönüyor, su denize gitmiş sayılıyordu.
    kok_of = np.zeros(M, np.int64)
    for n in range(M - 1, 0, -1):
        kok_of[n] = n if A["ebeveyn"][n] <= 0 else kok_of[A["ebeveyn"][n]]
    ebv = A["ebeveyn"]
    for n in range(1, M):            # ebeveyn her zaman çocuktan sonra oluşur
        pass
    kok_of = np.arange(M)
    for n in range(M - 1, 0, -1):
        if ebv[n] > 0:
            pass
    def kok_bul(n):
        while ebv[n] > 0:
            n = ebv[n]
        return n
    import heapq as _hq
    fl = np.full(ny * nx, -1, dtype=np.int64); gor = deniz.ravel().copy()
    h = [(zf[c], c) for c in np.where(gor)[0]]; _hq.heapify(h)
    while h:
        v, c = _hq.heappop(h)
        i, j = divmod(int(c), nx)
        for di, dj in D8:
            a_, b_ = i + di, j + dj
            if 0 <= a_ < ny and 0 <= b_ < nx:
                kk = a_ * nx + b_
                if not gor[kk]:
                    gor[kk] = True; fl[kk] = c; _hq.heappush(h, (max(zf[kk], v), kk))
    kok_hedef = {}
    for r in kokler:
        e = A["deniz_giris"].get(r)
        if e is None:
            continue
        c = e
        for _ in range(100000):
            if c < 0 or deniz.ravel()[c]:
                break
            d = dh[c]
            if d > 0:
                kr = kok_bul(int(d))
                if kr != r and zf[c] < A["esik_z"][kr]:
                    y = int(yap_of[max(dh[son[c]], 0)])
                    if y > 0 and kok_bul(y) == kr:
                        kok_hedef[r] = y
                    break
            c = fl[c]
    kok_ext = {}
    Q = np.zeros(M)
    for gecis in range(50):
        onceki = dict(kok_ext); yeni_ext = {}
        for r in kokler:
            yig = [(r, kok_ext.get(r, []))]
            while yig:
                n, giren = yig.pop()
                Q[n] = Rsub[n] + sum(t for _, t in giren)
                if cocuk[n] is None:
                    continue
                a, b = cocuk[n]
                ga_, gb_ = [(y, t) for y, t in giren if icinde(y, a)], [(y, t) for y, t in giren if not icinde(y, a)]
                Wa = Rsub[a] + sum(t for _, t in ga_); Wb = Rsub[b] + sum(t for _, t in gb_)
                gb, ga = giris_yaprak[n]
                if Wa > Scap[a] and Wb < Scap[b]:
                    gb_ = gb_ + [(gb, Wa - Suse[a])]
                elif Wb > Scap[b] and Wa < Scap[a]:
                    ga_ = ga_ + [(ga, Wb - Suse[b])]
                yig.append((a, ga_)); yig.append((b, gb_))
            if r in kok_hedef and Q[r] >= Scap[r]:
                y = kok_hedef[r]
                hedef_kok = y
                while A["ebeveyn"][hedef_kok] > 0:
                    hedef_kok = A["ebeveyn"][hedef_kok]
                yeni_ext.setdefault(hedef_kok, []).append((y, Q[r] - Suse[r]))
        kok_ext = yeni_ext
        if {k: round(sum(t for _, t in v)) for k, v in kok_ext.items()} == {k: round(sum(t for _, t in v)) for k, v in onceki.items()}:
            break
    dolu = Q >= Scap
    fazla = np.where(dolu, Q - Stop, 0.0)
    print("  su dengesi: %d kök, %.0fs" % (len(kokler), time.time() - t0), flush=True)
    etkin = yaprak_mi.copy()
    for n in range(1, M):
        if cocuk[n] is not None:
            a, b = cocuk[n]; etkin[n] = dolu[a] and dolu[b]
    etkin[0] = False
    gol_dugum = [n for n in range(1, M) if etkin[n] and not silik[n] and not (ebeveyn[n] > 0 and etkin[ebeveyn[n]])]
    # alt ağaç hücreleri
    uyeler = [[] for _ in range(M)]
    for c in np.where(dh > 0)[0]:
        uyeler[dh[c]].append(c)
    def alt(n):
        yig, out = [n], []
        while yig:
            m = yig.pop(); out.extend(uyeler[m])
            if cocuk[m] is not None:
                yig.extend(cocuk[m])
        return np.array(out, dtype=np.int64)
    seviye = np.full(ny * nx, np.nan); goller = []
    alanf = alan.ravel()
    for n in gol_dugum:
        h = alt(n)
        h = h[np.argsort(zf[h], kind="stable")]
        if dolu[n]:
            m = len(h); lvl = A["esik_z"][n]
        else:
            cs = np.cumsum(Kv[h])
            m = int(np.searchsorted(cs, Q[n]))
            if m == 0:
                continue
            lvl = zf[h[min(m, len(h)) - 1]] if m >= len(h) else 0.5 * (zf[h[m - 1]] + zf[h[m]])
        g = h[:m]
        if not np.isfinite(lvl):
            continue
        seviye[g] = lvl
        derin = lvl - zf[g]
        goller.append(dict(dugum=n, seviye=float(lvl), alan_km2=float(alanf[g].sum() / 1e6),
                           hacim_km3=float((alanf[g] * derin).sum() / 1e9), derin_m=float(derin.max()),
                           cikisli=bool(dolu[n]), cikis_hucre=int(A["esik_h"][n]) if dolu[n] else -1,
                           giren_km3_yil=float(Q[n] / 1e9), fazla_km3_yil=float(fazla[n] / 1e9),
                           hucreler=g))
    return seviye.reshape(ny, nx), goller, A


if __name__ == "__main__":
    k = np.load(os.path.join(BURASI, "_akim.npz"))
    z, lat, lon = k["z"].astype(np.float64), k["lat"], k["lon"]
    dy = 6371e3 * np.radians(abs(lat[1] - lat[0]))
    dx = (6371e3 * np.radians(lon[1] - lon[0]) * np.cos(np.radians(lat)))[:, None]
    alan = dx * dy * np.ones_like(z)
    asinma = float(sys.argv[1]) if len(sys.argv) > 1 else 0.0
    seviye, goller, A = coz(z, z < 0, k["R"], k["P"], k["Egol"], alan, asinma)
    goller.sort(key=lambda g: -g["alan_km2"])
    kara_alan = alan[z >= 0].sum() / 1e6
    print("aşınma %.0f m: göl sayısı %d, toplam alan %.0f km2 = karanın %%%.2f" % (asinma, len(goller), sum(g["alan_km2"] for g in goller), 100 * sum(g["alan_km2"] for g in goller) / kara_alan))
    for g in goller[:25]:
        i, j = divmod(int(g["hucreler"][0]), z.shape[1])
        print("  %8.0f km2  %6.0f km3  derin %4.0f m  seviye %5.0f  %s  giren %.1f km3/y  %.1f, %.1f" % (
            g["alan_km2"], g["hacim_km3"], g["derin_m"], g["seviye"], "çıkışlı" if g["cikisli"] else "KAPALI",
            g["giren_km3_yil"], lat[i], lon[j]))
    np.savez_compressed(os.path.join(BURASI, "_gol_%d.npz" % asinma), seviye=seviye)
    import pickle
    pickle.dump([{k: v for k, v in g.items()} for g in goller], open(os.path.join(BURASI, "_goller_%d.pkl" % asinma), "wb"))
