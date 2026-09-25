#!/bin/sh
# Cloudflare Workers derleme komutu: yalniz uygulamanin dosyalarini site/'ye
# kopyalar. Motor, dunya tanimi, kabartma kaynagi ve belgeler yayinlanmaz.
# Ayar: derleme komutu "sh yayinla.sh", yayin "npx wrangler deploy"
# (wrangler.jsonc assets.directory = ./site). uygulama.yml testi site/'de kosar.
set -eu
cd "$(dirname "$0")"
rm -rf site
mkdir -p site/data
cp index.html app.js style.css sw.js manifest.webmanifest site/
cp -R icons site/
cp data/atlas.json data/doku.png data/yukseklik.png data/kabartma.jpg data/kabartma_gri.jpg data/kabartma_bir.jpg data/dolasim.png site/data/
echo "site/ hazir: $(find site -type f | wc -l) dosya"
