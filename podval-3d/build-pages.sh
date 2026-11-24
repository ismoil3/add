#!/bin/sh
# Builds the standalone GitHub Pages copies from the artifact sources:
#   podval-3d/index.html -> docs/index.html        (basement only)
#   khona/index.html     -> docs/khona/index.html  (house: basement + floor 1)
set -e
cd "$(dirname "$0")/.."
wrap() {
  mkdir -p "$(dirname "$2")"
  {
    printf '<!doctype html>\n<html lang="tg">\n<head>\n<meta charset="utf-8">\n<meta name="viewport" content="width=device-width, initial-scale=1, viewport-fit=cover">\n'
    printf '<style>:root{padding-top:env(safe-area-inset-top,0px);padding-bottom:env(safe-area-inset-bottom,0px)}body{margin:0;font:14px system-ui,sans-serif}img{max-width:100%%}[hidden]{display:none!important}</style>\n'
    sed -n '1,/<\/style>/p' "$1"
    printf '</head>\n<body>\n'
    sed '1,/<\/style>/d' "$1"
    printf '</body>\n</html>\n'
  } > "$2"
}
wrap podval-3d/index.html docs/index.html
wrap khona/index.html docs/khona/index.html
touch docs/.nojekyll
