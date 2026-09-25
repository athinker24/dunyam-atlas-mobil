@echo off
rem Tarayici sunucudan ONCE aciliyordu ve ilk acilista hata sayfasi gorunebiliyordu:
rem once sunucu, kisa bekleme, sonra tarayici.
title Dunyam Atlasi - yerel sunucu
cd /d "%~dp0"
start "Dunyam sunucu" python -m http.server 8778
timeout /t 2 /nobreak >nul
start "" http://localhost:8778/
