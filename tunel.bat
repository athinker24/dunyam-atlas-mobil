@echo off
rem Telefona kurmak ya da guncellemek icin: yerel sunucu + gecici Cloudflare tuneli.
rem Ekranda cikan https://....trycloudflare.com adresini telefonda ac.
rem Is bitince bu pencereyi ve sunucu penceresini kapat; uygulama telefonda cevrimdisi calismaya devam eder.
rem Tunel herkese aciktir: depo kokunu degil yalniz uygulama dosyalarini sunar
rem (once .git, motor ve dunya tanimi de indirilebiliyordu; gece denetimi).
rem Liste yayinla.sh ile ayni olmali.
title Dunyam Atlasi - tunel
cd /d "%~dp0"
if exist site rmdir /s /q site
mkdir site\data
for %%f in (index.html app.js style.css sw.js manifest.webmanifest) do copy /y %%f site\ >nul
xcopy /e /i /q /y icons site\icons >nul
for %%f in (atlas.json doku.png yukseklik.png kabartma.jpg kabartma_gri.jpg kabartma_bir.jpg dolasim.png su.json tektonik.json levha.png bitki.json bitki.png bitki_veri.png) do copy /y data\%%f site\data\ >nul
rem Sunucu YALNIZ bu makineye baglanir. Varsayilan 0.0.0.0 idi: tunel
rem acikken site/ ayni zamanda yerel aga da aciliyordu (baslat.bat
rem zaten --bind 127.0.0.1 kullaniyordu, burasi atlanmisti). Tunelin
rem kendisi 127.0.0.1 uzerinden bagladigi icin bir sey kaybolmaz.
start "Dunyam sunucu" python -m http.server 8778 --bind 127.0.0.1 --directory site
npx --yes cloudflared tunnel --url http://127.0.0.1:8778
