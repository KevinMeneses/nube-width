#!/bin/zsh
# Instala Nube Width en REAPER (macOS) como enlace: los cambios del repo se ven al volver a insertar el FX.
set -e
DST="$HOME/Library/Application Support/REAPER/Effects/Nube Width"
cd "$(dirname "$0")"
mkdir -p "$DST"
ln -sf "$PWD/nube_width.jsfx" "$DST/nube_width.jsfx"
echo "Listo: en REAPER busca \"Nube Width\" en el navegador de FX (JS: Nube Width)."
