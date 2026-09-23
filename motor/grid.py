"""Katman 0 — grid, kara/deniz maskesi, hucre geometrisi.

Referans: docs/00-grid.md
"""

from __future__ import annotations

import json
import math
from dataclasses import dataclass, field

import numpy as np
from scipy import ndimage


@dataclass(frozen=True)
class World:
    """Gezegen ozellikleri. Dunya'ya ozel hicbir deger koda gomulmez."""

    name: str
    radius_km: float
    gravity_ms2: float
    rotation_period_h: float
    rotation_sign: int
    axial_tilt_deg: float
    year_length_days: float
    northward_equinox_doy: float
    sea_level_m: float
    air_density_kgm3: float
    solar_constant_wm2: float
    global_mean_sealevel_temp_c: float
    currents_file: str = ""
    heightmap: dict = field(default_factory=dict)
    params: dict = field(default_factory=dict)
    regions: dict = field(default_factory=dict)

    def __post_init__(self):
        """Dunya dosyasi elle yazilir; motorun ASIL guven siniri burasi.

        Olculdu — dogrulama olmadan gecersiz degerler UC ayri sekilde
        davraniyordu ve en kotusu ucuncusuydu:
          - radius_km=0, rotation_period_h=0  -> ciplak ZeroDivisionError
          - air_density=0, year_length=0      -> her alan inf/NaN
          - air_density NEGATIF               -> sessizce calisiyor, ruzgar
            16.5'ten 1.5 m/s'ye dusuyor ve hicbir uyari cikmiyor. Ayni
            sekilde negatif yaricap, sifir/negatif gunes sabiti, rotation_sign=0
            ve tilt=200 de sessizce anlamsiz sonuc uretiyordu.
        """
        for ad in ("radius_km", "gravity_ms2", "rotation_period_h",
                   "year_length_days", "air_density_kgm3", "solar_constant_wm2"):
            v = float(getattr(self, ad))
            if not math.isfinite(v) or v <= 0:
                raise ValueError(f"{self.name}: {ad} pozitif ve sonlu olmali ({v} verildi)")
        if self.rotation_sign not in (1, -1):
            raise ValueError(
                f"{self.name}: rotation_sign +1 ya da -1 olmali ({self.rotation_sign} verildi); "
                "-1 retrograd donus demektir, 0 tanimsizdir")
        if not math.isfinite(self.axial_tilt_deg) or abs(self.axial_tilt_deg) > 180.0:
            raise ValueError(
                f"{self.name}: axial_tilt_deg -180..180 araliginda olmali "
                f"({self.axial_tilt_deg} verildi)")
        for ad in ("northward_equinox_doy", "sea_level_m",
                   "global_mean_sealevel_temp_c"):
            v = float(getattr(self, ad))
            if not math.isfinite(v):
                raise ValueError(f"{self.name}: {ad} sonlu olmali ({v} verildi)")

    @classmethod
    def load(cls, path: str) -> "World":
        with open(path, encoding="utf-8") as fh:
            d = json.load(fh)
        return cls(**{k: v for k, v in d.items() if not k.startswith("_")})

    @property
    def omega(self) -> float:
        """Acisal hiz, rad/s."""
        return 2.0 * math.pi / (self.rotation_period_h * 3600.0)

    @property
    def radius_m(self) -> float:
        return self.radius_km * 1000.0


@dataclass(frozen=True)
class Grid:
    """Duzenli enlem-boylam izgarasi. lat KUZEYDEN GUNEYE azalir.

    Tum gradyan isaretleri bu yonelime bagli; degistirilirse circulation.py
    icindeki dP/dy isareti de degismeli.
    """

    lat: np.ndarray  # (ny,) derece, azalan
    lon: np.ndarray  # (nx,) derece, artan
    elev: np.ndarray  # (ny, nx) m, blok ortalamasi
    relief: np.ndarray  # (ny, nx) m, blok ici max-min
    land: np.ndarray  # (ny, nx) bool
    world: World

    @property
    def shape(self):
        return self.elev.shape

    @property
    def dlat(self) -> float:
        return abs(float(self.lat[1] - self.lat[0]))

    @property
    def dlon(self) -> float:
        return abs(float(self.lon[1] - self.lon[0]))

    @property
    def wraps(self) -> bool:
        """Domain boylamda tam turu kapatiyor mu (kuresel calistirma)?

        True ise boylam ekseni SARMALANIR: turevler, yumusatmalar, iz surme
        ve aki yuzleri son sutundan ilk sutuna gecer. Bolgesel kutularda
        False'tur ve kenarlar acik sinir gibi davranir.
        """
        return (self.lon.size * self.dlon) >= 360.0 - 1e-6

    @property
    def bounds(self):
        """(bati, guney, dogu, kuzey) — hucre kenarlari, merkezleri degil."""
        hx, hy = self.dlon / 2, self.dlat / 2
        return (
            float(self.lon[0]) - hx,
            float(self.lat[-1]) - hy,
            float(self.lon[-1]) + hx,
            float(self.lat[0]) + hy,
        )

    @property
    def lat2d(self) -> np.ndarray:
        return np.repeat(self.lat[:, None], self.lon.size, axis=1)

    @property
    def dy_m(self) -> float:
        return self.world.radius_m * math.radians(self.dlat)

    #: Kutupta cos(lat) sifira gider ve dx_m ile bolen her sey patlar
    #: (nem semasinda cikis orani u/dx sonsuza kosar). Fiziksel olarak o
    #: hucreler zaten cozunurlugun altinda; tabani belgeleyip sabitliyoruz.
    MIN_COS_LAT = math.cos(math.radians(85.0))

    @property
    def dx_m(self) -> np.ndarray:
        """(ny,) — enlemle daralir, ihmal edilemez. Kutupta tabanlanir."""
        cos = np.maximum(np.cos(np.radians(self.lat)), self.MIN_COS_LAT)
        return self.world.radius_m * cos * math.radians(self.dlon)

    def ddx(self, field: np.ndarray) -> np.ndarray:
        """Boylam yonunde turev (birim/m). Sarmalanan gridde dikis yerinden gecer."""
        if self.wraps:
            d = (np.roll(field, -1, axis=1) - np.roll(field, 1, axis=1)) / 2.0
        else:
            d = np.gradient(field, axis=1)
        return d / self.dx_m[:, None]

    def ddy(self, field: np.ndarray) -> np.ndarray:
        """Enlem yonunde turev (birim/m), KUZEY pozitif.

        lat kuzeyden guneye azaldigi icin satir turevinin isareti terstir.
        """
        return -np.gradient(field, axis=0) / self.dy_m

    def smooth(self, field: np.ndarray, sigma_cells: float) -> np.ndarray:
        """Gauss yumusatma; sarmalanan gridde boylam ekseni dolanir."""
        if sigma_cells <= 0.5:
            return field
        mode = ["nearest", "wrap" if self.wraps else "nearest"]
        return ndimage.gaussian_filter(field, sigma_cells, mode=mode)

    def sample(self, field: np.ndarray, ij: np.ndarray, order: int = 1) -> np.ndarray:
        """Kesirli (satir, sutun) konumlarinda ornekleme; dikisten gecebilir.

        map_coordinates tek bir kenar modu alir, oysa bize enlemde "nearest"
        boylamda "wrap" lazim. Diziyi boylamda birer sutun pedleyip indeksi
        kaydirmak ikisini birden verir.
        """
        if not self.wraps:
            return ndimage.map_coordinates(field, ij, order=order, mode="nearest")
        padded = np.concatenate([field[:, -1:], field, field[:, :1]], axis=1)
        jj = np.mod(ij[1], self.lon.size) + 1.0
        return ndimage.map_coordinates(
            padded, np.stack([ij[0], jj]), order=order, mode="nearest")

    def sampler(self, ij: np.ndarray, dtype=None):
        """SABIT bir kaynak konum kumesi icin bilineer ornekleyici doner.

        Ayni `ij` ile onlarca kez ornekleme yapan donguler icin. Bilineer
        indeksler ve agirliklar konuma baglidir, ORNEKLENEN ALANA degil —
        bir kez hesaplanip tekrar kullanilabilirler. sample() ise her cagrida
        koordinatlari yeniden isliyor.

        Olculdu (180x360, kuresel grid): cagri basina 2.96 ms -> 0.49 ms,
        6.0 kat. Kuresel 1 derece kosuda nem dongusu tek basina ~12 000
        cagri yapiyor. Sonuc map_coordinates ile ayni (fark 1e-13,
        kayan nokta artigi).

        Konum degisiyorsa (or. maritime iz surme) plan kurmanin anlami yok;
        orada sample() dogru secimdir.

        dtype: agirliklarin tipi. float32 verilirse float32 alanlar float32
        kalir (numpy aksi halde float64'e terfi ettirir ve kazanc kaybolur).
        """
        ny, nx = self.shape
        i = np.clip(np.asarray(ij[0], dtype=float), 0.0, ny - 1.0)
        i0f = np.floor(i)
        fi = i - i0f
        i0 = i0f.astype(np.intp)
        i1 = np.minimum(i0 + 1, ny - 1)

        if self.wraps:
            j = np.asarray(ij[1], dtype=float)
            j0f = np.floor(j)
            fj = j - j0f
            j0 = np.mod(j0f.astype(np.intp), nx)
            j1 = np.mod(j0 + 1, nx)
        else:
            j = np.clip(np.asarray(ij[1], dtype=float), 0.0, nx - 1.0)
            j0f = np.floor(j)
            fj = j - j0f
            j0 = j0f.astype(np.intp)
            j1 = np.minimum(j0 + 1, nx - 1)

        # duz (ravel) indeks fancy-indexing'i belirgin hizlandiriyor
        a00, a01 = i0 * nx + j0, i0 * nx + j1
        a10, a11 = i1 * nx + j0, i1 * nx + j1
        w00 = (1.0 - fi) * (1.0 - fj)
        w01 = (1.0 - fi) * fj
        w10 = fi * (1.0 - fj)
        w11 = fi * fj
        if dtype is not None:
            w00, w01 = w00.astype(dtype), w01.astype(dtype)
            w10, w11 = w10.astype(dtype), w11.astype(dtype)

        def ornekle(field: np.ndarray) -> np.ndarray:
            f = np.asarray(field).ravel()
            return f[a00] * w00 + f[a01] * w01 + f[a10] * w10 + f[a11] * w11

        return ornekle

    def wrap_j(self, jj: np.ndarray) -> np.ndarray:
        """Sutun indeksini sarmalar ya da kirpar, domaine gore."""
        nx = self.lon.size
        return np.mod(jj, nx) if self.wraps else np.clip(jj, 0, nx - 1)

    @property
    def cell_km(self) -> float:
        """Tipik hucre boyutu (km) — yumusatma olceklerini hucreye cevirmek icin."""
        return 0.5 * (self.dy_m + float(self.dx_m.mean())) / 1000.0

    @property
    def area_m2(self) -> np.ndarray:
        """(ny,) — hucre alani, kuresel kusak formulu."""
        h = math.radians(self.dlat) / 2.0
        phi = np.radians(self.lat)
        return self.world.radius_m**2 * math.radians(self.dlon) * (np.sin(phi + h) - np.sin(phi - h))


#: Kuresel maskede, en buyuk su kutlesinin bu oranindan buyuk her bilesen
#: de okyanus sayilir — iki karsilastirilabilir okyanusu olan bir dunyada
#: yalnizca en buyugu almak digerini kara yapardi.
OCEAN_SIZE_FRAC = 0.10


def land_mask(elev: np.ndarray, sea_level: float, wraps: bool = False) -> np.ndarray:
    """Deniz seviyesi altinda olmak yetmez; su kutlesinin BAGLI olmasi gerekir.

    Naif `elev > sea_level` kurali Hazar (-28 m), Turfan (-154 m), Kattara
    (-133 m) gibi kapali havzalari okyanus sanir. Bkz docs/00-grid.md 0.4.

    Baglilik olcutu domaine gore degisir:

    * BOLGESEL kutu — okyanus, harita kenarindaki su kutlesine baglidir.
      Kenar, kutunun disindaki dunyaya acilan kapidir.
    * KURESEL grid — kenar diye bir sey YOKTUR, kutuplar da kara olabilir.
      Orada okyanus, en buyuk bagli su kutlesi (ve onunla karsilastirilabilir
      buyuklukteki digerleri). Kenar kuralini kuresel gridde kullanmak
      ekvator boyunca uzanan bir okyanusu kara sayiyordu.
    """
    below = elev <= sea_level
    if not below.any():
        return np.ones(elev.shape, dtype=bool)

    if wraps:
        # ndimage.label dikis yerini bilmez: diziyi iki kez yan yana koyup
        # etiketleriz. Ayni fiziksel hucrenin iki kopyasi (j ve j+nx) farkli
        # etiket alabilir — dikisten gecen bir kutlenin bati parcasi ilk
        # kopyada, dogu parcasi ikinci kopyada birlesir. Iki kopyanin
        # etiketleri esdeger sayilip birlestirilir; yalniz ilk yariya bakmak
        # dikisten gecen kutleyi iki parca sayiyor ve boyutunu bolüyordu.
        from scipy.sparse import coo_matrix
        from scipy.sparse.csgraph import connected_components
        nx = below.shape[1]
        lbl2, n = ndimage.label(np.concatenate([below, below], axis=1))
        if n == 0:
            return np.ones(elev.shape, dtype=bool)
        a, b = lbl2[:, :nx].ravel(), lbl2[:, nx:].ravel()
        m = (a > 0) & (b > 0)
        graf = coo_matrix((np.ones(m.sum()), (a[m], b[m])), shape=(n + 1, n + 1))
        _, esit = connected_components(graf, directed=False)
        lbl = np.where(lbl2[:, :nx] > 0, esit[lbl2[:, :nx]] + 1, 0)
        sizes = np.bincount(lbl.ravel())
        sizes[0] = 0
        ocean_ids = np.flatnonzero(sizes >= OCEAN_SIZE_FRAC * sizes.max())
    else:
        lbl, _ = ndimage.label(below)
        edge = np.concatenate([lbl[0], lbl[-1], lbl[:, 0], lbl[:, -1]])
        ocean_ids = np.unique(edge[edge > 0])

    if ocean_ids.size == 0:
        return np.ones(elev.shape, dtype=bool)  # tamamen ic bolge
    return ~np.isin(lbl, ocean_ids)


def downsample(src: np.ndarray, block: int, sea_level: float, wraps: bool = False):
    """Kaynak yukseklik dizisini block x block bloklarla indirger.

    Doner: (elev, relief, land).

    Sira onemli: maske ONCE kaynak cozunurlukte hesaplanir, sonra indirgenir.
    Ters sira dar bogazlari kapatir ve arkalarindaki denizi kapali havza
    sanar (Georgia Bogazi vakasi, bkz docs/00-grid.md 0.4).
    """
    src_land = land_mask(src, sea_level, wraps=wraps)
    shp = (src.shape[0] // block, block, src.shape[1] // block, block)
    b = src.reshape(shp)
    bl = src_land.reshape(shp)

    n_land = bl.sum(axis=(1, 3))
    land = n_land >= (block * block) / 2.0  # cogunluk kurali

    # kara hucresinde yalnizca kara alt-hucreleri sayilir; yoksa deniz tabani
    # kiyi hucrelerinin yuksekligini asagi ceker
    elev = np.where(land, (b * bl).sum(axis=(1, 3)) / np.maximum(n_land, 1), b.mean(axis=(1, 3)))
    hi = np.where(bl, b, -np.inf).max(axis=(1, 3))
    lo = np.where(bl, b, np.inf).min(axis=(1, 3))
    relief = np.where(land, hi - lo, b.max(axis=(1, 3)) - b.min(axis=(1, 3)))
    return elev, relief, land


def build(lat, lon, elev, relief, world: World, land=None) -> Grid:
    lat = np.asarray(lat, dtype=np.float64)
    lon = np.asarray(lon, dtype=np.float64)
    elev = np.asarray(elev, dtype=np.float64)
    relief = np.asarray(relief, dtype=np.float64)
    if lat.size < 2 or lon.size < 2:
        raise ValueError(
            f"grid en az 2x2 olmali (verilen {lat.size}x{lon.size}); "
            "tek satir/sutun bir iklim alani degildir, hucre araligi tanimsiz")
    if lat[0] < lat[-1]:
        raise ValueError("lat kuzeyden guneye azalmali")
    g = Grid(lat, lon, elev, relief, np.zeros(elev.shape, bool), world)
    if land is None:
        land = land_mask(elev, world.sea_level_m, wraps=g.wraps)
    return Grid(lat, lon, elev, relief, np.asarray(land, dtype=bool), world)


def _check_res(res_deg: float) -> None:
    """res_deg bir TRUST BOUNDARY: 0 ve negatif sessizce yutuluyordu.

    Blok hesabi max(1, round(res_deg/src_res)) oldugu icin res_deg=0 ve
    res_deg=-2 kaynak cozunurluge dusuyor ve kullanici istedigini aldigini
    saniyordu. CLI'dan '--res 0' yazmak yeterli.
    """
    if not np.isfinite(res_deg) or res_deg <= 0:
        raise ValueError(f"res_deg pozitif olmali ({res_deg} verildi)")


def _check_bounds(bounds, *, wrap_ok: bool) -> None:
    """bounds = (bati, guney, dogu, kuzey). Dejenere kutu anlasilir hata versin.

    Sifir yukseklikli bir kutu ciplak ZeroDivisionError veriyordu.
    wrap_ok: ingest antimeridyeni kesen kutuyu (bati > dogu) kabul eder,
    duz gorsel okuyan from_heightmap etmez.
    """
    w, s, e, n = (float(x) for x in bounds)
    if n <= s:
        raise ValueError(f"bounds kuzey ({n}) guneyden ({s}) buyuk olmali")
    if e == w or (e < w and not wrap_ok):
        raise ValueError(
            f"bounds dogu ({e}) batidan ({w}) buyuk olmali"
            + ("" if wrap_ok else "; duz gorselde antimeridyeni kesen kutu desteklenmiyor"))


def ingest(tif_path: str, bounds, world: World, res_deg: float = 1.0 / 6.0) -> Grid:
    """GeoTIFF yukseklik verisini hedef cozunurluge indirger.

    bounds = (bati, guney, dogu, kuzey), derece.
    Her hedef hucre icin blok ortalamasi (elev) ve blok ici max-min (relief)
    saklanir — ikisinin neden ayri gerektigi docs/00-grid.md 0.3'te.

    Kara/deniz maskesi KAYNAK cozunurlukte hesaplanir, indirgemeden once.
    Ortalama aldiktan sonra hesaplamak dar bogazlari kapatir: Georgia Bogazi
    (Vancouver Adasi arkasi, 400 m derin acik deniz) Juan de Fuca ve Johnstone
    bogazlari blok ortalamasinda kapandigi icin kapali havza sanilip 65 hucre
    karaya donuyordu. Bkz docs/00-grid.md 0.4.

    Kara hucrelerinde yukseklik ve rolyef YALNIZCA kara alt-hucrelerinden
    hesaplanir; yoksa kiyi hucrelerinde deniz tabani ortalamayi asagi ceker.

    rasterio yalnizca burada kullanilir; motorun geri kalani saf numpy.
    """
    import rasterio
    from rasterio.windows import from_bounds

    _check_res(res_deg)
    _check_bounds(bounds, wrap_ok=True)
    w0, s0, e0, n0 = bounds
    with rasterio.open(tif_path) as src:
        if w0 > e0:
            # ANTIMERIDYENI KESEN kutu: rasterio tek pencerede okuyamaz
            # ("Bounds and transform are inconsistent"). Iki parca okunup
            # birlestirilir. Kurgusal dunyada ilginc bir kita dikisin
            # ustunde oturabilir ve kullanici haritasini donduremez.
            lon_max = src.bounds.right
            lon_min = src.bounds.left
            wa = from_bounds(w0, s0, lon_max, n0, transform=src.transform)
            wb = from_bounds(lon_min, s0, e0, n0, transform=src.transform)
            a = src.read(1, window=wa, masked=False)
            b = src.read(1, window=wb, masked=False)
            if a.shape[0] != b.shape[0]:
                k = min(a.shape[0], b.shape[0])
                a, b = a[:k], b[:k]
            data = np.concatenate([a, b], axis=1).astype(np.float64)
            tr = src.window_transform(wa)
        else:
            win = from_bounds(*bounds, transform=src.transform)
            data = src.read(1, window=win, masked=False).astype(np.float64)
            tr = src.window_transform(win)

    src_res = abs(tr.a)
    block = max(1, int(round(res_deg / src_res)))
    ny, nx = (data.shape[0] // block) * block, (data.shape[1] // block) * block
    if ny == 0 or nx == 0:
        raise ValueError(f"kirpma cok kucuk: {data.shape} / blok {block}")
    span = (e0 - w0) if e0 > w0 else (e0 - w0 + 360.0)
    wraps = abs(span - 360.0) < 1e-6
    elev, relief, land = downsample(data[:ny, :nx], block, world.sea_level_m, wraps)

    # hucre merkezleri
    lat = tr.f + (np.arange(ny // block) + 0.5) * block * tr.e
    lon = tr.c + (np.arange(nx // block) + 0.5) * block * tr.a
    return build(lat, lon, elev, relief, world, land=land)


def _heightmap_oku(path, band):
    """(float64 dizi, nodata) dondurur. rasterio varsa onu, yoksa Pillow'u kullanir.

    Motor cekirdegi saf numpy+scipy olmali; rasterio yalnizca Dunya
    dogrulamasinda (reference.py, run.py) bulunur. Kurgusal dunya yolu duz bir
    PNG okur ve bunun icin rasterio gerekmez — mobil repo onsuz kosar.
    Iki okuyucu da ayni diziyi verir; test_heightmap_okuyucular_ayni kilitler.
    """
    try:
        import rasterio
    except ImportError:
        rasterio = None

    if rasterio is not None:
        import warnings
        # duz gorseller cografi referans tasimaz; uyari beklenen durum
        with warnings.catch_warnings():
            warnings.simplefilter("ignore", rasterio.errors.NotGeoreferencedWarning)
            with rasterio.open(path) as src:
                return src.read(band).astype(np.float64), src.nodatavals[band - 1]

    from PIL import Image
    with Image.open(path) as im:
        # Saydamlik, duz bir gorselde "burasi bos" demenin tek yolu; asagidaki
        # nodata denetiminin gorsel karsiligi. Ne ile doldurulacagini bilemeyiz.
        if "A" in im.getbands() or "transparency" in im.info:
            raise ValueError(
                f"heightmap {path} saydamlik tasiyor. Saydam pikselin yuksekligi "
                "bilinmiyor; gorseli bosluksuz doldurup tekrar dene.")
        bantlar = im.getbands()
        if band > len(bantlar):
            raise ValueError(f"heightmap {len(bantlar)} bant tasiyor, band={band} istendi")
        kare = im if len(bantlar) == 1 else im.split()[band - 1]
        return np.asarray(kare).astype(np.float64), None


def _egri_dogrula(egri, max_elev_m):
    """elev_curve bir GUVEN SINIRI: elle yazilan dunya dosyasindan geliyor.

    KAPSAM: egri yalnizca DENIZ USTUNU esler. Deniz alti (batimetri) her
    zaman elev_gamma ile eslenir — bir egri verip elev_gamma=1.0 birakmak
    okyanus tabanini dogrusal yapar. Modelde neredeyse etkisiz (hava akisi
    okyanus uzerinde deniz seviyesine kelepcelenir) ama sessiz degil:
    bilerek boyle.

    Bicim: [[oran, metre], ...] — oran, deniz seviyesi ile en yuksek piksel
    arasinda 0..1; metre o oranin karsiligi. Aradaki degerler dogrusal.

    Neden var: tek bir elev_gamma butun araziyi ayni yonde ceker. Olculdu,
    bu projenin kurgusal dunyasinda gamma=2 ile ova 417 m (istenen 150),
    tarim bolgesi 1206 m (istenen 660), plato 1411 m (istenen 1580) cikiyordu
    — yani ovayi indirmek icin gamma buyutulse plato da iniyordu. Egri her
    araligi ayri egebildigi icin yedi bolgenin hepsi ayni anda tutturulabildi.
    Worldbuilding araclarinin ciktisi gercek bir hipsometrik egri tasimaz
    (bkz from_heightmap belgesi); bu, o egriyi disaridan vermenin yolu.
    """
    e = np.asarray(egri, dtype=np.float64)
    if e.ndim != 2 or e.shape[1] != 2 or len(e) < 2:
        raise ValueError(f"elev_curve [[oran, metre], ...] olmali, verilen sekil {e.shape}")
    x, y = e[:, 0], e[:, 1]
    if not np.all(np.isfinite(e)):
        raise ValueError("elev_curve NaN/sonsuz iceriyor")
    if not np.all(np.diff(x) > 0):
        raise ValueError(f"elev_curve oranlari KESIN artmali, verilen: {x.tolist()}")
    if np.any(np.diff(y) < 0):
        raise ValueError(
            f"elev_curve metreleri azalamaz (esleme monoton olmali), verilen: {y.tolist()}")
    if abs(x[0]) > 1e-9 or abs(y[0]) > 1e-9:
        raise ValueError(f"elev_curve 0.0 -> 0.0 ile baslamali, baslangic ({x[0]}, {y[0]})")
    if abs(x[-1] - 1.0) > 1e-9 or abs(y[-1] - max_elev_m) > 1e-6:
        raise ValueError(
            f"elev_curve 1.0 -> max_elev_m ({max_elev_m}) ile bitmeli, "
            f"bitis ({x[-1]}, {y[-1]})")
    return x, y


def from_heightmap(
    path: str,
    world: World,
    *,
    sea_level_value: float,
    max_elev_m: float,
    max_depth_m: float,
    bounds=(-180.0, -90.0, 180.0, 90.0),
    res_deg: float = 1.0 / 6.0,
    band: int = 1,
    elev_gamma: float = 1.0,
    elev_curve=None,
) -> Grid:
    """Cografi referansi OLMAYAN bir yukseklik goruntusunden grid kurar.

    Kurgusal dunya icin giris noktasi budur. ETOPO gibi georeferansli
    veriler `ingest()` ile okunur; burada girdi duz bir gorsel olabilir
    (PNG, TIFF, BMP, JPG — gri tonlamali, 8 ya da 16 bit).

    Deger -> yukseklik esleme, worldbuilding'de yaygin olan bicimde:
    tek bir DEGER deniz seviyesini temsil eder, ustu ve alti AYRI olceklenir.
    Boylece batimetri ile topografyayi bagimsiz kalibre edebilirsin — bir
    heightmap'te derin okyanus cukurlari genelde dagların ayrintisi kadar
    iyi cizilmez.

        v >= sea : elev = ((v - sea) / (vmax - sea)) ** gamma * max_elev_m
        v <  sea : elev = -((sea - v) / (sea - vmin)) ** gamma * |max_depth_m|

    elev_gamma (varsayilan 1.0 = dogrusal, eski davranisla birebir ayni) bu
    egrinin BICIMINI ayarlar; uc noktalari — deniz seviyesi, en yuksek zirve,
    en derin nokta — degismeden kalir. Neden gerekli: worldbuilding araclarinin
    urettigi displacement haritalari gercek bir hipsometrik egri tasimaz,
    araziyi "sisirirler". Olculdu, bir kullanici haritasinda: en yuksek zirve
    6700 m verildiginde karanin %75'i 2000 m'nin uzerine cikiyordu (Dunya'da
    bu oran %5, ortalama kara yuksekligi 840 m) ve butun kita tundraya
    donuyordu. gamma > 1 orta yukseklikleri asagi ceker ve zirveye
    dokunmaz — yani "en yuksek dagim 6700 m" ile "kitam ovalik" istekleri
    dogrusal bir eslemede celisir, burada celismez.

    Kabaca: gamma = ln(hedef_medyan / max_elev_m) / ln(medyan_v_normalize).

    Bu esleme `world.sea_level_m = 0` varsayar; dunya dosyasinda baska bir
    deger varsa esleme ona kaydirilir.

    bounds = (bati, guney, dogu, kuzey). Varsayilan tum gezegen; o zaman
    Grid.wraps True olur ve butun katmanlar dikisten gecen moda gecer.
    Goruntunun satir 0'i KUZEY kabul edilir (standart equirectangular).
    """
    data, nodata = _heightmap_oku(path, band)

    # Nodata bir TRUST BOUNDARY: deger -> yukseklik eslemesi onu sirandan bir
    # piksel sanir ve genelde en derin degere oturtur. Olculdu: nodata=0 olan
    # bir delik kitanin ortasinda -6000 m'lik sahte bir cukur aciyordu, hicbir
    # uyari vermeden. Ne ile doldurulacagini tahmin edemeyiz, o yuzden hata.
    if nodata is not None and np.isfinite(nodata):
        delik = int((data == nodata).sum())
        if delik:
            raise ValueError(
                f"heightmap {delik} nodata pikseli iceriyor (nodata={nodata:g}). "
                "Deger -> yukseklik eslemesi bunlari gercek yukseklik sanar ve "
                "sahte cukur/tepe uretir. Gorseli bosluksuz doldurup tekrar dene.")

    _check_res(res_deg)
    _check_bounds(bounds, wrap_ok=False)
    ny_src, nx_src = data.shape
    w, s, e, n = bounds
    span_x, span_y = e - w, n - s
    ar_img, ar_geo = nx_src / ny_src, span_x / span_y
    if abs(ar_img / ar_geo - 1.0) > 0.02:
        raise ValueError(
            f"goruntu en/boy orani {ar_img:.3f}, sinirlarinki {ar_geo:.3f}. "
            "Equirectangular bir dunya haritasinda ikisi esit olmali "
            "(tum gezegen icin genislik = 2 x yukseklik).")

    vmin, vmax = float(data.min()), float(data.max())
    sea = float(sea_level_value)
    if not (vmin < sea < vmax):
        raise ValueError(f"sea_level_value={sea} veri araliginin ({vmin}..{vmax}) icinde olmali")

    g = float(elev_gamma)
    if not (np.isfinite(g) and g > 0):
        raise ValueError(f"elev_gamma={elev_gamma} pozitif ve sonlu olmali")

    egri = _egri_dogrula(elev_curve, max_elev_m) if elev_curve is not None else None

    _oran = np.maximum(data - sea, 0.0) / (vmax - sea)
    ust = _oran ** g if egri is None else np.interp(_oran, egri[0], egri[1]) / max_elev_m
    alt = (np.maximum(sea - data, 0.0) / (sea - vmin)) ** g
    elev = np.where(data >= sea, ust * max_elev_m, -alt * abs(max_depth_m)) + world.sea_level_m

    src_res = span_x / nx_src
    block = max(1, int(round(res_deg / src_res)))
    ny, nx = (ny_src // block) * block, (nx_src // block) * block
    if ny == 0 or nx == 0:
        raise ValueError(f"goruntu cok kucuk: {data.shape} / blok {block}")

    # Kaynak blok boyuna tam bolunmuyorsa artan satir/sutunlar ATILMAZ, kaynak
    # en yakin komsu indeksle ny x nx'e esit aralikla yeniden orneklenir.
    # Onceden sondaki satirlar atiliyor ama hucre enlemleri yine tam araliga
    # yayiliyordu: 2048 satirin 2046'si kullanilip 180 dereceye gerildiginden
    # hucreler guneye dogru kayiyordu (en guneyde 0.18 derece, olculdu).
    # Simdi her kaynak pikselin konum hatasi en fazla yarim piksel. Tam
    # bolunen kaynakta (Dunya dogrulamasi) hicbir sey degismez.
    if ny != ny_src or nx != nx_src:
        ri = np.minimum(((np.arange(ny) + 0.5) * ny_src / ny).astype(int), ny_src - 1)
        ci = np.minimum(((np.arange(nx) + 0.5) * nx_src / nx).astype(int), nx_src - 1)
        elev = elev[ri][:, ci]

    wraps = abs(span_x - 360.0) < 1e-6
    ev, relief, land = downsample(elev, block, world.sea_level_m, wraps)

    dlat, dlon = span_y / (ny // block), span_x / (nx // block)
    lat = n - (np.arange(ny // block) + 0.5) * dlat
    lon = w + (np.arange(nx // block) + 0.5) * dlon
    return build(lat, lon, ev, relief, world, land=land)

