# -*- coding: utf-8 -*-
"""Repodaki motor/dunya kopyalari projedekilerle ayni mi?

Bu repo tek basina calisabilsin diye iklim motorunun ve dunya dosyalarinin
bir KOPYASI burada duruyor. Iki kopya sessizce ayrisirsa telefondaki dunya
ile masaustundeki dunya farkli olur ve kimse fark etmez.

    python _senkron_kontrol.py ../         # proje kokunu ver, karsilastir

Cikti 0 = ayni, 1 = fark var. Projedeki _repo_senkron.py ile guncellenir.
"""
import hashlib
import os
import sys

ESLESME = [
    ("motor", "climate", (".py",), {"reference.py"}),
    ("dunya/dunyam.json", "worlds/dunyam.json", None, None),
    ("dunya/dunyam.currents.json", "worlds/dunyam.currents.json", None, None),
    ("dunya/dunyam_heightmap.png", "data/work/dunyam_heightmap.png", None, None),
]


def ozet(yol):
    with open(yol, "rb") as fh:
        return hashlib.sha256(fh.read()).hexdigest()[:12]


def main(proje):
    burasi = os.path.dirname(os.path.abspath(__file__))
    fark = []
    for repo_yol, proje_yol, uzanti, haric in ESLESME:
        r = os.path.join(burasi, repo_yol)
        p = os.path.join(proje, proje_yol)
        if os.path.isdir(r):
            def uyar(ad):
                return (not uzanti or ad.endswith(uzanti)) and not (haric and ad in haric)
            for ad in sorted(os.listdir(r)):
                if not uyar(ad):
                    continue
                pr, pp = os.path.join(r, ad), os.path.join(p, ad)
                if not os.path.exists(pp):
                    fark.append("%s/%s projede yok" % (repo_yol, ad))
                elif ozet(pr) != ozet(pp):
                    fark.append("%s/%s FARKLI" % (repo_yol, ad))
            # ters yon: projeye eklenmis ama repoya kopyalanmamis dosya
            if os.path.isdir(p):
                for ad in sorted(os.listdir(p)):
                    if uyar(ad) and not os.path.exists(os.path.join(r, ad)):
                        fark.append("%s/%s repoda yok" % (repo_yol, ad))
        else:
            if not os.path.exists(p):
                fark.append("%s projede yok" % proje_yol)
            elif ozet(r) != ozet(p):
                fark.append("%s FARKLI" % repo_yol)
    if fark:
        print("SENKRON DEGIL:")
        for f in fark:
            print("  " + f)
        return 1
    print("repo kopyalari projedekilerle ayni")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1] if len(sys.argv) > 1 else ".."))
