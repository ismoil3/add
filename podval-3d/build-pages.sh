#!/bin/sh
# Builds the standalone GitHub Pages copy (docs/index.html) from podval-3d/index.html.
set -e
cd "$(dirname "$0")/.."
{
  printf '<!doctype html>\n<html lang="tg">\n<head>\n<meta charset="utf-8">\n<meta name="viewport" content="width=device-width, initial-scale=1, viewport-fit=cover">\n'
  printf '<style>:root{padding-top:env(safe-area-inset-top,0px);padding-bottom:env(safe-area-inset-bottom,0px)}body{margin:0;font:14px system-ui,sans-serif}img{max-width:100%%}[hidden]{display:none!important}</style>\n'
  sed -n '1,/<\/style>/p' podval-3d/index.html
  printf '</head>\n<body>\n'
  sed '1,/<\/style>/d' podval-3d/index.html
  printf '</body>\n</html>\n'
} > docs/index.html
touch docs/.nojekyll
