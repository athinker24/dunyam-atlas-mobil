@echo off
rem Tarayici sunucudan ONCE aciliyordu ve ilk acilista hata sayfasi gorunebiliyordu:
rem once sunucu, kisa bekleme, sonra tarayici.
title Dunyam Atlasi - yerel sunucu
cd /d "%~dp0"
rem Yalniz bu makine: varsayilan 0.0.0.0 depo kokunu (.git dahil) yerel aga aciyordu.
start "Dunyam sunucu" python -m http.server 8778 --bind 127.0.0.1
timeout /t 2 /nobreak >nul
start "" http://localhost:8778/
