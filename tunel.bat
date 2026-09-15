@echo off
rem Telefona kurmak ya da guncellemek icin: yerel sunucu + gecici Cloudflare tuneli.
rem Ekranda cikan https://....trycloudflare.com adresini telefonda ac.
rem Is bitince bu pencereyi ve sunucu penceresini kapat; uygulama telefonda cevrimdisi calismaya devam eder.
title Dunyam Atlasi - tunel
cd /d "%~dp0"
start "Dunyam sunucu" python -m http.server 8778
npx --yes cloudflared tunnel --url http://localhost:8778
