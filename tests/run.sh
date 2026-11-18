#!/bin/zsh
# Renderiza los casos en REAPER (pestaña temporal) y verifica la respuesta.
cd "$(dirname "$0")/.."
PY=${NUBE_PY:-python3}   # necesita numpy, scipy y soundfile
[ -f tests/signals/inst_voz4.wav ] || $PY tests/make_signals.py
rm -f tests/out/log.txt
/Applications/REAPER.app/Contents/MacOS/REAPER -nonewinst "$PWD/tests/render_cases.lua" >/dev/null 2>&1 &
for i in $(seq 1 240); do grep -q done tests/out/log.txt 2>/dev/null && break; sleep 1; done
grep -q done tests/out/log.txt || { echo "REAPER no terminó (¿diálogo abierto?)"; exit 1; }
grep -i error tests/out/log.txt
$PY tests/check.py
