"""Compara los renders de tests/out con los JSFX originales y con la teoría. Sale con código 1 si algo falla."""
import numpy as np, soundfile as sf, pathlib, sys
from scipy import signal as sg
D = pathlib.Path(__file__).parent / "out"; S = pathlib.Path(__file__).parent / "signals"; SR = 48000
def a(db): return 10 ** (db / 20)
def db(x): return 20 * np.log10(np.abs(x) + 1e-30)
def load(name, d=D):
    x, sr = sf.read(d / f"{name}.wav"); assert sr == SR; return x
def sig(name): return load(name, S)[:, :2]
def MS(x): return (x[:, 0] + x[:, 1]) / 2, (x[:, 0] - x[:, 1]) / 2
def tone(x, f, t0=0.5, t1=1.9):
    """amplitud (dBFS) de un seno de frecuencia f (mínimos cuadrados)"""
    seg = x[int(t0 * SR):int(t1 * SR)]; tt = np.arange(int(t0 * SR), int(t1 * SR)) / SR
    M = np.stack([np.sin(2 * np.pi * f * tt), np.cos(2 * np.pi * f * tt)], 1)
    c, *_ = np.linalg.lstsq(M, seg, rcond=None); return db(np.hypot(*c))
# K-weighting (BS.1770, 48 kHz) y loudness integrada con compuertas
KB = [(np.array([1.53512485958697, -2.69169618940638, 1.19839281085285]), np.array([1, -1.69065929318241, 0.73248077421585])),
      (np.array([1.0, -2.0, 1.0]), np.array([1, -1.99004745483398, 0.99007225036621]))]
def lufs(*chans):
    z = 0
    for c in chans:
        y = c
        for b, a_ in KB: y = sg.lfilter(b, a_, y)
        n = int(0.4 * SR); h = n // 4; m = (len(y) - n) // h + 1
        z = z + np.array([np.mean(y[i * h:i * h + n] ** 2) for i in range(m)])
    l = -0.691 + 10 * np.log10(z + 1e-30); g = z[l > -70]
    g = g[-0.691 + 10 * np.log10(g) > -0.691 + 10 * np.log10(g.mean()) - 10]
    return -0.691 + 10 * np.log10(g.mean())
def corr(x): return np.sum(x[:, 0] * x[:, 1]) / np.sqrt(np.sum(x[:, 0] ** 2) * np.sum(x[:, 1] ** 2))
def sm(x): m, s = MS(x); return max(10 * np.log10(np.sum(s ** 2) / np.sum(m ** 2) + 1e-30), -99)

fails = 0
def scalar(name, got, want, tol):
    global fails
    ok = abs(got - want) <= tol; fails += not ok
    print(f"{'OK ' if ok else 'MAL'} {name:46s} {got:+9.3f}   (esperado {want:+.3f} ± {tol})")
def inrange(name, got, lo, hi):
    global fails
    ok = lo <= got <= hi; fails += not ok
    print(f"{'OK ' if ok else 'MAL'} {name:46s} {got:+9.3f}   (entre {lo:+.3f} y {hi:+.3f})")

for p in sorted(D.glob("*.wav")):
    if p.stem.startswith("perf_"): continue
    x = load(p.stem)
    if not np.all(np.isfinite(x)) or np.abs(x).max() > 4:
        fails += 1; print("MAL", p.stem, "tiene NaN o pasa de +12 dBFS")

print("== igual a los JSFX originales (diferencia máxima en dBFS; -138 = el último bit del float de 32)")
for c, src in (("wid", "inst"), ("wid2", "inst_mono"), ("wth", "inst"), ("car", "inst"), ("carv", "inst_voz4"),
               ("rhodes", "inst_voz4"), ("nubebaja", "inst_voz4")):
    r, n = load(f"eq_{c}_ref"), load(f"eq_{c}_nw")
    inrange(f"{c}: Nube Width = original", db(np.abs(r - n).max()), -999, -120)
    inrange(f"{c}: el original sí cambia el audio", db(np.abs(r - sig(src)).max()), -40, 20)
r, x = load("eq_nubebaja_ref"), sig("inst_voz4"); k = int(12.8 * SR)
dm = MS(r)[0] - MS(x)[0]   # antes de 12.8 s el hueco no actúa: el centro queda igual (el ancho sí actúa, como en el original)
inrange("nube baja: centro intacto antes de 12.8 s", db(np.abs(dm[:k - 1024]).max()), -999, -120)
inrange("nube baja: el hueco actúa después de 12.8 s", db(np.abs(dm[k + 4800:]).max()), -40, 0)

print("== neutro y mono")
inrange("por defecto: salida = entrada", db(np.abs(load("neutro") - sig("mix")).max()), -999, -140)
for c, src, g in (("mono_todo", "mix", -12), ("mono_wid100", "inst_mono", 0), ("ancho200", "mix", 0), ("graves_150", "side50_2k", 0)):
    mo, mi = MS(load(c))[0], MS(sig(src))[0] * a(g)
    inrange(f"{c}: (L+R)/2 igual a la entrada", db(np.abs(mo - mi).max()), -999, -120)
mi, mo = MS(sig("mix"))[0] * a(-12), MS(load("mono_todo"))[0]
x = load("mono_todo"); print(f"    todo al máximo (ancho 300, sintético 100, lados +6): corr {corr(x):+.2f}, lados/centro {sm(x):+.1f} dB, pico {db(np.abs(x).max()):+.1f} dBFS")
scalar("mono_todo: loudness en mono (LU)", lufs(mo) - lufs(mi), 0, 0.01)
x = load("mono_wid100"); i = sig("inst_mono")
print(f"    side sintético 100 % sobre audio mono: corr {corr(i):+.2f} -> {corr(x):+.2f}, lados/centro {sm(x):+.1f} dB, "
      f"L {lufs(x[:, 0]) - lufs(i[:, 0]):+.2f} LU, R {lufs(x[:, 1]) - lufs(i[:, 1]):+.2f} LU, mono {lufs(MS(x)[0]) - lufs(MS(i)[0]):+.3f} LU")
x = load("ancho0"); inrange("ancho 0 %: L = R", db(np.abs(x[:, 0] - x[:, 1]).max()), -999, -140)
s2, s1 = MS(load("ancho200"))[1], MS(sig("mix"))[1]
inrange("ancho 200 %: lados x2 exacto", db(np.abs(s2 - 2 * s1).max()), -999, -120)

print("== graves en mono (pasa-altos LR4 de 150 Hz en los lados)")
def hp4(f, fc):   # Linkwitz-Riley = 2 Butterworth de 2o orden en serie (con la deformación bilineal)
    w = (np.tan(np.pi * f / SR) / np.tan(np.pi * fc / SR)) ** 2; return 2 * db(w / np.sqrt((1 - w) ** 2 + 2 * w))
x = load("graves_150")
scalar("lados 50 Hz", tone(x[:, 0], 50), -12 + hp4(50, 150), 0.05)
scalar("lados 2 kHz", tone(x[:, 0], 2000), -12 + hp4(2000, 150), 0.02)
imp = np.zeros(SR); imp[SR // 2] = 0.5
def resp(name):
    """respuesta del centro y de los lados (impulso en L: M = S = imp / 2)"""
    m, s = MS(load(name)[:SR]); f = np.fft.rfftfreq(SR, 1 / SR); ref = np.fft.rfft(imp / 2)
    return f, db(np.fft.rfft(m) / ref), db(np.fft.rfft(s) / ref)
f, hm, hs = resp("graves_imp"); band = (f > 20) & (f < 20000)
inrange("graves: centro plano (dB)", np.abs(hm[band]).max(), 0, 0.001)
inrange("graves: lados = LR4 teórico (error dB)", np.abs(hs[band & (f > 40)] - hp4(f[band & (f > 40)], 150)).max(), 0, 0.05)
print(f"    lados: 50 Hz {np.interp(50, f, hs):+.1f} dB, 100 Hz {np.interp(100, f, hs):+.1f}, 150 Hz {np.interp(150, f, hs):+.1f}, 300 Hz {np.interp(300, f, hs):+.2f}")

print("== hueco en el centro")
scalar("1.2 kHz en el centro baja 6 dB", tone(load("hueco_mid")[:, 0], 1200), -18, 0.05)
scalar("1.2 kHz en los lados intacto", tone(load("hueco_side")[:, 0], 1200), -12, 0.02)
def rbj(f, f0, g, q):
    A = 10 ** (g / 40); w = 2 * np.pi * f0 / SR; al = np.sin(w) / (2 * q); a0 = 1 + al / A
    b = np.array([1 + al * A, -2 * np.cos(w), 1 - al * A]) / a0; a_ = np.array([1, -2 * np.cos(w) / a0, (1 - al / A) / a0])
    return b, a_
b, a_ = rbj(None, 3000, -6, 2); _, H = sg.freqz(b, a_, worN=f[band], fs=SR)
f, hm, hs = resp("hueco_imp")
inrange("hueco 3 kHz -6 Q2: centro = RBJ (error dB)", np.abs(hm[band] - db(H)).max(), 0, 0.02)
inrange("hueco: lados planos (dB)", np.abs(hs[band]).max(), 0, 0.001)
scalar("lados +6 dB", tone(load("lados6")[:, 0], 1200), -6, 0.02)
scalar("salida +6 dB", tone(load("salida6")[:, 0], 1200), -6, 0.02)
x = load("esc_mono"); inrange("escuchar mono: L = R = (L+R)/2 de entrada", db(max(np.abs(x[:, 0] - x[:, 1]).max(), np.abs(x[:, 0] - MS(sig("mix"))[0]).max())), -999, -120)
x = load("esc_lados"); inrange("escuchar lados: L = -R", db(np.abs(x[:, 0] + x[:, 1]).max()), -999, -130)
inrange("escuchar lados: hay señal (dBFS pico)", db(np.abs(x).max()), -40, 0)

print("== presets sobre la instrumental de Nube baja (16 s; voz en 3/4)")
print("    preset                                    corr      lados/centro    estéreo   mono    mono vs teoría")
NAMES = ["Nube baja - Rhodes", "Nube baja - Hook", "Pads / acordes", "Melodía / lead", "Coros y dobles", "Voz principal",
         "808 / bajo mono", "Bajo armónicos", "Hi-hats / perc", "Clap / snare", "Guitarra / stab", "Órgano", "Pluck / kalimba",
         "Silbido / flauta", "Reverb / delay", "Inst: hueco voz", "Inst: hueco con voz", "Master + ancho", "Master angosto",
         "Todo mono", "Por defecto"]
# (frecuencia, cantidad, Q) del hueco de los presets en modo "siempre"; los de "solo con voz" se miden aparte
CARVE = {3: (1500, -3, 0.7), 5: (1200, -4, 0.6), 13: (1200, -3, 0.6), 14: (1500, -3, 0.6), 15: (1500, -3, 0.6), 16: (1500, -3, 0.5)}
VOICE = {1: -5, 17: -6}
x0 = sig("inst_voz4"); m0 = MS(x0)[0]; L0 = lufs(x0[:, 0], x0[:, 1]); M0 = lufs(m0); t0 = int(0.3 * SR)
for p in range(1, 22):
    x = load(f"preset{p}"); m = MS(x)[0]
    dl, dm = lufs(x[:, 0], x[:, 1]) - L0, lufs(m) - M0
    if p in VOICE:
        res = "  (hueco según la voz)"
        ok = VOICE[p] - 0.5 <= dm <= 0.01
    else:
        f0, g, q = CARVE.get(p, (1200, 0, 0.6))
        b, a_ = rbj(None, f0, g, q); pred = sg.lfilter(b, a_, m0)
        e = db(np.sqrt(np.mean((m[t0:] - pred[t0:]) ** 2)) / np.sqrt(np.mean(m[t0:] ** 2)))
        res = f"  error {e:7.1f} dB"; ok = e < -60
    fails += not ok
    print(f"{'OK ' if ok else 'MAL'} {p:2d} {NAMES[p - 1]:22s} {corr(x0):+.2f} -> {corr(x):+.2f}   {sm(x0):+6.1f} -> {sm(x):+6.1f}   "
          f"{dl:+6.2f}   {dm:+6.2f}{res}")
print("    (mono vs teoría: diferencia entre el mono de salida y el mono de entrada pasado solo por la campana del hueco)")
print("\nFALLAS:", fails)
sys.exit(1 if fails else 0)
