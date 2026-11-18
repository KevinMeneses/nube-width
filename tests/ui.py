"""Ayudante para probar la interfaz con cliclick (ventana del FX de 1000x640 en su tamaño por defecto)."""
import subprocess, time, pathlib, re, math
ROOT = pathlib.Path(__file__).resolve().parent.parent
def _bounds():
    out = subprocess.run(["swift", str(ROOT / "tests/winid.swift"), "--bounds"], capture_output=True, text=True).stdout.split()
    if len(out) < 5: raise SystemExit("no encuentro la ventana del FX (abre la demo con tests/reopen.sh)")
    wid, x, y, w, h = (float(v) for v in out[:5]); return int(wid), x, y, h
WID, X0, Y0, H0 = _bounds()
WX, WY = X0, Y0 + H0 - 640          # esquina del área gráfica (la cabecera de REAPER va arriba)
def pt(x, y): return f"{round(WX + x)},{round(WY + y)}"
def cc(*args): subprocess.run(["cliclick", "-w", "60", *args], check=True); time.sleep(0.4)
def wheel(n): subprocess.run(["swift", str(ROOT / "tests/scroll.swift"), str(n)], check=True); time.sleep(0.4)
def shot(path): subprocess.run(["screencapture", "-x", "-o", "-l", str(WID), path], check=True); return path
def dump():
    p = ROOT / "tests/out/dump.txt"; p.unlink(missing_ok=True)
    subprocess.Popen(["/Applications/REAPER.app/Contents/MacOS/REAPER", "-nonewinst", str(ROOT / "tests/ui_dump.lua")],
                     stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    for _ in range(40):
        if p.exists() and "done" in p.read_text(): return p.read_text().replace("done\n", "")
        time.sleep(0.25)
    return "(sin respuesta)"
def param(n):
    """valor formateado del slider n"""
    m = re.search(rf"^{n} (.*)$", dump(), re.M); return m.group(1).rsplit(" = ", 1)[1] if m else None
def num(s): return float(s.split()[0]) if s else float("nan")
def drag(x0, y0, x1, y1, steps=8):
    cc(f"dd:{pt(x0, y0)}")
    for k in range(1, steps + 1): cc(f"m:{pt(x0 + (x1 - x0) * k / steps, y0 + (y1 - y0) * k / steps)}")
    cc(f"du:{pt(x1, y1)}")
# layout (ventana 1000x640): dy = 54, dh = 400, py = 464
DY, DH, PY = 54, 400, 464
FX0 = 14 + min(400, (1000 - 120) * 0.34) + 16; FW = 1000 - 14 - 120 - 16 - FX0
f2x = lambda f: FX0 + FW * math.log(f / 20) / math.log(1000)
c2y = lambda d: DY + 18 + (DH - 36) * (18 - d) / 48
LISTEN = {0: (111, PY + 20), 1: (185, PY + 20), 2: (269, PY + 20)}
HUECO = {0: (520, PY + 20), 1: (619, PY + 20)}
KNOB = {1: 46, 2: 120, 3: 194, 4: 268, 5: 342, 6: 470, 7: 544, 8: 618, 9: 692, 11: 766, 13: 950}
knob = lambda i: (KNOB[i], PY + 92)
PRESETS = (208, 22)
GONIO = (14 + 150, DY + 150)
