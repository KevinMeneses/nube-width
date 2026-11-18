#!/bin/zsh
# Cierra la demo de la interfaz (si hay) y la vuelve a abrir con el código nuevo. NUBE_SHOT=archivo.png toma captura.
cd "$(dirname "$0")"
R=/Applications/REAPER.app/Contents/MacOS/REAPER
osascript -e 'tell application "System Events" to tell process "REAPER" to get name of every window' 2>/dev/null | grep -q "Nube Width demo" && { $R -nonewinst "$PWD/ui_close.lua" >/dev/null 2>&1 & sleep 3; }
mkdir -p out; echo "${NUBE_PRESET:-1}" > out/ui_preset.txt
rm -f out/ui.txt; $R -nonewinst "$PWD/ui_demo.lua" >/dev/null 2>&1 &
for i in $(seq 1 20); do grep -q done out/ui.txt 2>/dev/null && break; sleep 0.5; done; sleep 2.5
# captura solo la ventana del FX (por su id: no hace falta traerla al frente)
[ -n "$NUBE_SHOT" ] && screencapture -x -o -l "$(swift winid.swift)" "$NUBE_SHOT"
echo listo
