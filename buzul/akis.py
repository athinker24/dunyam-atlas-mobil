"""Buz akı yönlendirmesi: vadi buzullarının hızlı, dengeli hâl yaklaşığı.

Tam buz akışı (buzul.py, SIA) 7000 m'lik dik dağlarda saniyelik adımlara
düşüyor. Bu arazide buz örtüsü değil dağ buzulu çıktığı için (kar çizgisi
yüksek, kıta içi kurak) dengeli hâl yeter: her hücrenin yıllık kütle
dengesi b (m buz) yatağın akış yönünde aşağı toplanır; akı Q = Σ b·alan
pozitif kaldıkça hücre buzla örtülü, sıfıra indiği yer buzul dili.
Kalınlık SIA'nın dengeli akı bağıntısından: q = 2A(ρg)^n/(n+2) · H^(n+2) · |∇s|^n.
"""
import heapq
import numpy as np

D8 = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 1), (1, -1), (1, 0), (1, 1)]


def doldur(z, deniz):
    """Öncelik sırasıyla çukur doldurma (Barnes 2014). Deniz hücreleri çıkış."""
    ny, nx = z.shape
    f = z.copy(); gorulen = deniz.copy()
    kenar = np.zeros_like(deniz); kenar[[0, -1]] = True; kenar[:, [0, -1]] = True
    h = []
    ilk = deniz | kenar
    gorulen |= ilk
    for i, j in zip(*np.where(ilk)):
        heapq.heappush(h, (f[i, j], i, j))
    while h:
        v, i, j = heapq.heappop(h)
        for di, dj in D8:
            a, b = i + di, j + dj
            if 0 <= a < ny and 0 <= b < nx and not gorulen[a, b]:
                gorulen[a, b] = True
                if f[a, b] <= v:
                    f[a, b] = v + 1e-3
                heapq.heappush(h, (f[a, b], a, b))
    return f


def yon(f, dx, dy):
    """D8 en dik iniş: hedef satır/sütun."""
    ny, nx = f.shape
    en = np.zeros_like(f); ti = np.tile(np.arange(ny)[:, None], (1, nx)); tj = np.tile(np.arange(nx), (ny, 1))
    ii, jj = ti.copy(), tj.copy()
    p = np.pad(f, 1, constant_values=np.inf)
    for di, dj in D8:
        k = p[1 + di:ny + 1 + di, 1 + dj:nx + 1 + dj]
        mesafe = np.hypot(dx * dj, dy * di)
        e = (f - k) / mesafe
        daha = e > en
        en = np.where(daha, e, en); ii = np.where(daha, ti + di, ii); jj = np.where(daha, tj + dj, jj)
    return ii, jj, en


def buz(z, b, dx, dy, A=1e-16, n=3, rho=917.0, g=9.81):
    """z: yatak (m, deniz<0), b: m buz/yıl, dx: (ny,1) m, dy: m."""
    ny, nx = z.shape
    deniz = z < 0
    f = doldur(z, deniz)
    dxa = dx * np.ones((1, nx))
    ii, jj, egim = yon(f, dxa, dy)
    alan = dxa * dy
    sira = np.argsort(-f, axis=None)
    Q = np.zeros(ny * nx)              # gelen akı, m3/yıl
    ic = (ii * nx + jj).ravel()
    bb = (b * alan).ravel(); d = deniz.ravel()
    cik = np.zeros(ny * nx)
    for k in sira:
        if d[k]:
            continue
        q = Q[k] + bb[k]
        if q > 0:
            cik[k] = q
            if ic[k] != k:
                Q[ic[k]] += q
    cik = cik.reshape(ny, nx)
    ortu = cik > 0
    # kalınlık: akı, hücre genişliğine yayılmış (birim genişlik akısı)
    gen = np.sqrt(alan)
    qw = cik / gen
    Gam = 2 * A * (rho * g) ** n / (n + 2)
    s = np.maximum(egim, 0.01)
    H = np.where(ortu, (qw / (Gam * s ** n)) ** (1.0 / (n + 2)), 0.0)
    return dict(ortu=ortu, H=H, Q=cik, egim=egim, dolu=f, ii=ii, jj=jj,
                gelen=Q.reshape(ny, nx))
