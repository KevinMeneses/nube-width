"""Pruebas de la interfaz con el mouse. Requiere la demo abierta con el preset 3 (NUBE_PRESET=3 tests/reopen.sh).
Trae REAPER al frente y mueve el mouse: no correr mientras alguien usa la Mac."""
import sys, os
sys.path.insert(0, os.path.dirname(__file__))
from ui import *
OUT = os.environ.get("NUBE_SHOTS", str(ROOT / "tests/out"))
fails = 0
def check(name, got, want):
    global fails
    ok = (want(got) if callable(want) else got == want); fails += not ok
    print(f"{'OK ' if ok else 'MAL'} {name:48s} {got!r}")

subprocess.run(["osascript", "-e", 'tell application "REAPER" to activate']); time.sleep(0.6)
cc(f"c:{pt(500, 5)}")                                       # foco en la ventana del FX
check("arranca con preset 3 (ancho 140)", num(param(1)), 140.0)
cc(f"c:{pt(*LISTEN[1])}"); check("clic en Mono", param(14), lambda v: v.startswith("Mono"))
cc(f"c:{pt(*LISTEN[2])}"); check("clic en Solo lados", param(14), lambda v: v.startswith("Solo lados"))
cc(f"c:{pt(*LISTEN[0])}"); check("clic en Normal", param(14), "Normal")
cc(f"c:{pt(*HUECO[1])}"); check("hueco: Solo con voz", param(10), lambda v: v.startswith("Solo cuando"))
cc(f"c:{pt(*HUECO[0])}"); check("hueco: Siempre", param(10), "Siempre")
x, y = knob(1); drag(x, y, x, y - 50)
check("arrastrar Ancho hacia arriba sube", num(param(1)), lambda v: v > 150)
cc(f"dc:{pt(x, y)}"); check("doble clic en Ancho = 100 %", num(param(1)), 100.0)
x, y = knob(7); cc(f"m:{pt(x, y)}"); c0 = num(param(7)); wheel(-5)
check("rueda sobre Cantidad baja el hueco", num(param(7)), lambda v: v < c0 - 0.2)
x, y = knob(2); drag(x, y, x, y - 40)
check("arrastrar Side sintético sube", num(param(2)), lambda v: v > 35)
f0, g0 = num(param(6)), num(param(7))
hx, hy = f2x(f0), c2y(g0); drag(hx, hy, hx + 60, hy + 30)
check("arrastrar el punto del hueco: más agudo", num(param(6)), lambda v: v > f0 * 1.5)
check("arrastrar el punto del hueco: más profundo", num(param(7)), lambda v: v < g0 - 2)
q0 = num(param(8)); hx, hy = f2x(num(param(6))), c2y(num(param(7))); cc(f"m:{pt(hx, hy)}"); wheel(5)
check("rueda sobre el punto del hueco cambia el Q", num(param(8)), lambda v: v > q0 + 0.05)
x = f2x(150); drag(x, DY + 200, FX0 + 1, DY + 200)
check("arrastrar Graves mono a la izquierda = apagado", param(5), lambda v: num(v) <= 20.5)
cc(f"dc:{pt(FX0 + 3, DY + 200)}"); check("doble clic en la línea = 120 Hz", num(param(5)), 120.0)
w0 = num(param(1)); drag(*GONIO, GONIO[0], GONIO[1] - 60)
check("arrastrar en el goniómetro sube el ancho", num(param(1)), lambda v: v > w0 + 10)
time.sleep(1.5); shot(f"{OUT}/ui_editado.png")
cc(f"c:{pt(*PRESETS)}"); time.sleep(0.6); cc("kp:arrow-down", "kp:return")
check("menú Presets -> Nube baja - Rhodes (ancho 160)", (num(param(1)), num(param(7))), (160.0, -5.0))
print("FALLAS:", fails)
sys.exit(1 if fails else 0)
