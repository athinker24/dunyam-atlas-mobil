"""Katman 8 — Koppen-Geiger iklim siniflandirmasi.

Referans: docs/07-koppen.md
Algoritma: docs/reference/beck2018_KoppenGeiger.m (Beck et al. 2018) birebir.

Bu katman fizik icermez, saf esik mantigidir. Girdisi 12 aylik sicaklik ve
yagis; ciktisi Beck'in 1-30 numaralandirmasiyla sinif kodu.

Yaz/kis yarilari ENLEMDEN DEGIL, hucrenin kendi sicakligindan belirlenir
(NMJJAS ortalamasi ONDJFM'den yuksekse yaz Nisan-Eylul'dur). Bu, yarimkure
ayrimini kendiliginden halleder ve kurgusal dunyada da dogru calisir.
"""

from __future__ import annotations

import numpy as np

# Beck et al. 2018 legend.txt — bkz docs/reference/beck2018_legend.txt
CODES = {
    1: "Af", 2: "Am", 3: "Aw", 4: "BWh", 5: "BWk", 6: "BSh", 7: "BSk",
    8: "Csa", 9: "Csb", 10: "Csc", 11: "Cwa", 12: "Cwb", 13: "Cwc",
    14: "Cfa", 15: "Cfb", 16: "Cfc", 17: "Dsa", 18: "Dsb", 19: "Dsc", 20: "Dsd",
    21: "Dwa", 22: "Dwb", 23: "Dwc", 24: "Dwd", 25: "Dfa", 26: "Dfb", 27: "Dfc",
    28: "Dfd", 29: "ET", 30: "EF",
}
BROAD = {**{k: "A" for k in (1, 2, 3)}, **{k: "B" for k in (4, 5, 6, 7)},
         **{k: "C" for k in range(8, 17)}, **{k: "D" for k in range(17, 29)},
         **{k: "E" for k in (29, 30)}}


def classify(temp, precip, peel70: bool = False) -> np.ndarray:
    """(12,ny,nx) sicaklik (C) ve yagis (mm/ay) -> (ny,nx) uint8 sinif kodu.

    peel70: True verilirse kuraklik esigi icin literaturdeki %70 kriteri
        (Pw > 2.333*Ps, Peel 2007) kullanilir. VARSAYILAN FALSE, yani Beck'in
        .m dosyasindaki yazim (2.333*Pw > Ps). Ikisi ayni sey degil ve
        hangisinin referans rasteri urettigi OLCULDU: Beck'in yazimi tam
        isabette 0.83-0.86, %70 kriteri 0.65-0.79. Raster Beck'in kodundan
        uretilmis; referansa karsi olcum yapacaksak onun tanimini kullanmaliyiz.
        Bkz docs/07-koppen.md.
    """
    T = np.asarray(temp, dtype=np.float64)
    P = np.asarray(precip, dtype=np.float64)
    if T.shape[0] != 12 or P.shape != T.shape:
        raise ValueError("temp ve precip (12, ny, nx) olmali")

    apr_sep = [3, 4, 5, 6, 7, 8]  # Nisan..Eylul (0 tabanli)
    oct_mar = [9, 10, 11, 0, 1, 2]

    # yaz yarisi hucrenin KENDI sicakligindan belirlenir, enlemden degil
    summer_is_apr_sep = T[apr_sep].mean(0) > T[oct_mar].mean(0)
    sel = np.zeros(T.shape, dtype=bool)
    sel[apr_sep] = summer_is_apr_sep
    sel[oct_mar] = ~summer_is_apr_sep

    Ps = np.where(sel, P, 0.0).sum(0)
    Pw = np.where(sel, 0.0, P).sum(0)
    Pdry = P.min(0)
    Psdry = np.where(sel, P, np.inf).min(0)
    Pswet = np.where(sel, P, -np.inf).max(0)
    Pwdry = np.where(sel, np.inf, P).min(0)
    Pswet_w = np.where(sel, -np.inf, P).max(0)  # Pwwet

    MAT = T.mean(0)
    MAP = P.sum(0)
    Tmon10 = (T > 10).sum(0)
    Thot = T.max(0)
    Tcold = T.min(0)

    Pthresh = 2 * MAT + 14.0
    if peel70:
        win = Pw > 2.333 * Ps
        sum_ = Ps > 2.333 * Pw
    else:
        win = Pw * 2.333 > Ps
        sum_ = Ps * 2.333 > Pw
    Pthresh = np.where(win, 2 * MAT, Pthresh)
    Pthresh = np.where(sum_, 2 * MAT + 28.0, Pthresh)

    B = MAP < 10 * Pthresh
    BW = B & (MAP < 5 * Pthresh)
    BS = B & ~BW

    A = (Tcold >= 18) & ~B
    Af = A & (Pdry >= 60)
    Am = A & ~Af & (Pdry >= 100 - MAP / 25)
    Aw = A & ~Af & ~Am

    C = (Thot > 10) & (Tcold > 0) & (Tcold < 18) & ~B
    D = (Thot > 10) & (Tcold <= 0) & ~B
    E = (Thot <= 10) & ~B

    out = np.zeros(MAT.shape, dtype=np.uint8)

    def seasonal(base):
        """Ortak Cs/Cw/Cf ve Ds/Dw/Df mantigi."""
        s = base & (Psdry < 40) & (Psdry < Pswet_w / 3)
        w = base & (Pwdry < Pswet / 10)
        both = s & w
        s = s & ~(both & (Ps > Pw))
        w = w & ~(both & (Ps <= Pw))
        return s, w, base & ~s & ~w

    Cs, Cw, Cf = seasonal(C)
    Ds, Dw, Df = seasonal(D)

    # Beck'in atama sirasi: 1..30, sonraki eslesme oncekini ezer
    assign = [
        (1, Af), (2, Am), (3, Aw),
        (4, BW & (MAT >= 18)), (5, BW & (MAT < 18)),
        (6, BS & (MAT >= 18)), (7, BS & (MAT < 18)),
    ]
    for offset, grp in ((8, Cs), (11, Cw), (14, Cf)):
        a = grp & (Thot >= 22)
        b = grp & ~a & (Tmon10 >= 4)
        c = grp & ~a & ~b & (Tmon10 >= 1) & (Tmon10 < 4)
        assign += [(offset, a), (offset + 1, b), (offset + 2, c)]
    for offset, grp in ((17, Ds), (21, Dw), (25, Df)):
        a = grp & (Thot >= 22)
        b = grp & ~a & (Tmon10 >= 4)
        d = grp & ~a & ~b & (Tcold < -38)
        c = grp & ~a & ~b & ~d
        assign += [(offset, a), (offset + 1, b), (offset + 2, c), (offset + 3, d)]
    assign += [(29, E & (Thot > 0)), (30, E & (Thot <= 0))]

    for code, mask in assign:
        out[mask] = code
    return out


def accuracy(model: np.ndarray, truth: np.ndarray, mask: np.ndarray) -> dict:
    """Sinif ve ana grup isabet oranlari."""
    m = mask & (truth > 0) & (model > 0)
    if not m.any():
        return {"n": 0}
    a, b = model[m], truth[m]
    broad = np.zeros(31, dtype="<U1")
    for k, v in BROAD.items():
        broad[k] = v
    return {
        "n": int(m.sum()),
        "exact": float((a == b).mean()),
        "broad": float((broad[a] == broad[b]).mean()),
    }
