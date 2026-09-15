@echo off
title Dunyam Atlasi - yerel sunucu
cd /d "%~dp0"
start "" http://localhost:8778/
python -m http.server 8778
