-- Escribe los parámetros del FX de la pista 1 (pestaña actual) en tests/out/dump.txt
local OUT = debug.getinfo(1, "S").source:match("^@(.*)/[^/]*$") .. "/out"
local f = io.open(OUT .. "/dump.txt", "w")
local tr = reaper.GetTrack(0, 0)
for p = 0, reaper.TrackFX_GetNumParams(tr, 0) - 1 do
  local _, n = reaper.TrackFX_GetParamName(tr, 0, p, ""); local _, v = reaper.TrackFX_GetFormattedParamValue(tr, 0, p, "")
  f:write(p + 1, " ", n, " = ", v, "\n")
end
f:write("done\n"); f:close()
