"""Señales de prueba (48 kHz, float32). Usa audio de Nube baja si está en la máquina."""
import numpy as np, soundfile as sf, pathlib
D = pathlib.Path(__file__).parent / "signals"; D.mkdir(exist_ok=True)
SR = 48000
HOME = pathlib.Path.home()
def a(db): return 10 ** (db / 20)
def save(name, *ch): sf.write(D / name, np.stack(ch, 1).astype(np.float32), SR, subtype="FLOAT")
n = SR * 2; t = np.arange(n) / SR
s = lambda f, db: a(db) * np.sin(2 * np.pi * f * t)
z = np.zeros(n)
# tonos en el centro (L = R) y en los lados (L = -R)
save("mid1200.wav", s(1200, -12), s(1200, -12))
save("side1200.wav", s(1200, -12), -s(1200, -12))
x = s(50, -12) + s(2000, -12); save("side50_2k.wav", x, -x)
# impulso solo en L: M = S = imp / 2 (respuesta del centro y de los lados a la vez)
imp = z.copy(); imp[SR // 2] = 0.5; save("impulse_L.wav", imp, z)

# material real: 16 s de la instrumental de Nube baja (estéreo), versión mono y versión con voz en 3/4
INST = HOME / "Music/ClaudeBeats/Mezcla/nube_baja_nube_plugins_premaster_instrumental.wav"
MIX = HOME / "Music/ClaudeBeats/Mezcla/nube_baja_mezcla_premaster_X20.wav"
VOZ = HOME / "Music/NubeDeEss/tests/signals/voz.wav"
L = SR * 16
inst, sr = sf.read(INST); assert sr == SR; inst = inst[SR * 14: SR * 14 + L]
save("inst.wav", inst[:, 0], inst[:, 1])
m = inst.mean(1); save("inst_mono.wav", m, m)
voz, sr = sf.read(VOZ); assert sr == SR; voz = voz[:L]
voz = np.pad(voz, ((0, L - len(voz)), (0, 0)))
sf.write(D / "inst_voz4.wav", np.concatenate([inst, voz], 1).astype(np.float32), SR, subtype="FLOAT")
mix, sr = sf.read(MIX); assert sr == SR; mix = mix[SR * 40: SR * 40 + L]
save("mix.wav", mix[:, 0], mix[:, 1])
print("ok", sorted(p.name for p in D.iterdir()))
