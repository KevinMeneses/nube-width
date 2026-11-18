-- Renderiza cada caso en una pestaña nueva (Nube Width o la cadena de JSFX originales) y cierra la pestaña.
-- Uso: REAPER -nonewinst tests/render_cases.lua   (escribe tests/out/*.wav y tests/out/log.txt)
local ROOT = debug.getinfo(1, "S").source:match("^@(.*)/[^/]*$")
local OUT = ROOT .. "/out"
local NW = "JS:Nube Width/nube_width.jsfx"
local WID = "JS:Claude/claude_widener.jsfx"
local WTH = "JS:Claude/claude_width.jsfx"
local CAR = "JS:Claude/claude_center_carve.jsfx"
local PRESET = 15
os.execute('mkdir -p "' .. OUT .. '"')
local logf = io.open(OUT .. "/log.txt", "w")
local function log(...) local t = {} for _, v in ipairs({...}) do t[#t+1] = tostring(v) end logf:write(table.concat(t, " "), "\n") logf:flush() end

-- sliders de Nube Width con forma :log=mid (van normalizados 0..1)
local LOGP = {[4] = {80, 1000, 300}, [5] = {20, 500, 120}, [6] = {200, 6000, 1200}, [8] = {0.2, 4, 1}}
local function to_norm(s, v)
  local mn, mx, mid = table.unpack(LOGP[s])
  local sr = (mx - mn) / (mid - mn) - 1; local r = sr * sr
  return math.log((v - mn) / (mx - mn) * (r - 1) + 1) / math.log(r)
end
local function nw(p) return {{NW, p or {}}} end
-- cadena del Rhodes en Nube baja: widener 40/14/250 -> ancho 160 -> hueco 1200 -5 Q0.6, lados +1.5, solo con voz
local function rhodes(desde) return {{WID, {40, 14, 250}}, {WTH, {160}}, {CAR, {1200, -5, 0.6, 1.5, 1, -40, desde}}} end

local CASES = {
  -- iguales a los JSFX originales
  {"eq_wid_ref",    "inst.wav",      {{WID, {40, 14, 250}}}},
  {"eq_wid_nw",     "inst.wav",      nw({[2] = 40})},
  {"eq_wid2_ref",   "inst_mono.wav", {{WID, {100, 25, 600}}}},
  {"eq_wid2_nw",    "inst_mono.wav", nw({[2] = 100, [3] = 25, [4] = 600})},
  {"eq_wth_ref",    "inst.wav",      {{WTH, {160}}}},
  {"eq_wth_nw",     "inst.wav",      nw({[1] = 160})},
  {"eq_car_ref",    "inst.wav",      {{CAR, {1200, -5, 0.6, 0, 0, -40, 0}}}},
  {"eq_car_nw",     "inst.wav",      nw({[7] = -5})},
  {"eq_carv_ref",   "inst_voz4.wav", {{CAR, {1200, -5, 0.6, 1.5, 1, -40, 0}}}, 4},
  {"eq_carv_nw",    "inst_voz4.wav", nw({[7] = -5, [9] = 1.5, [10] = 1}), 4},
  {"eq_rhodes_ref", "inst_voz4.wav", rhodes(1.0), 4},
  {"eq_rhodes_nw",  "inst_voz4.wav", nw({[1] = 160, [2] = 40, [7] = -5, [9] = 1.5, [10] = 1, [12] = 1.0}), 4},
  {"eq_nubebaja_ref", "inst_voz4.wav", rhodes(12.8), 4},
  {"eq_nubebaja_nw",  "inst_voz4.wav", nw({[PRESET] = 1}), 4},
  -- neutro y mono
  {"neutro",        "mix.wav",       nw()},
  {"mono_todo",     "mix.wav",       nw({[1] = 300, [2] = 100, [3] = 20, [5] = 200, [9] = 6}), 2, -12},   -- -12 dB: que no recorte el WAV
  {"mono_wid100",   "inst_mono.wav", nw({[2] = 100})},
  {"ancho0",        "mix.wav",       nw({[1] = 0})},
  {"ancho200",      "mix.wav",       nw({[1] = 200})},
  {"graves_150",    "side50_2k.wav", nw({[5] = 150})},
  {"graves_imp",    "impulse_L.wav", nw({[5] = 150})},
  {"hueco_mid",     "mid1200.wav",   nw({[7] = -6})},
  {"hueco_side",    "side1200.wav",  nw({[7] = -6})},
  {"hueco_imp",     "impulse_L.wav", nw({[6] = 3000, [7] = -6, [8] = 2})},
  {"lados6",        "side1200.wav",  nw({[9] = 6})},
  {"salida6",       "mid1200.wav",   nw({[13] = 6})},
  {"esc_mono",      "mix.wav",       nw({[2] = 50, [1] = 150, [14] = 1})},
  {"esc_lados",     "mix.wav",       nw({[2] = 50, [1] = 150, [14] = 2})},
}
for p = 1, 21 do CASES[#CASES + 1] = {"preset" .. p, "inst_voz4.wav", nw({[PRESET] = p}), 4} end

reaper.Main_OnCommand(40859, 0) -- nueva pestaña
reaper.GetSetProjectInfo(0, "PROJECT_SRATE", 48000, true)
reaper.GetSetProjectInfo(0, "PROJECT_SRATE_USE", 1, true)
reaper.InsertTrackAtIndex(0, false); local tr = reaper.GetTrack(0, 0)
local item = reaper.AddMediaItemToTrack(tr)
local take = reaper.AddTakeToMediaItem(item)
reaper.SetMediaItemInfo_Value(item, "D_POSITION", 0)
local only = os.getenv("NUBE_CASE")

for _, c in ipairs(CASES) do
  local name, src, chain = c[1], c[2], c[3]
  if not only or name:find(only) then
    reaper.SetMediaTrackInfo_Value(tr, "I_NCHAN", c[4] or 2)
    local s = reaper.PCM_Source_CreateFromFile(ROOT .. "/signals/" .. src)
    reaper.SetMediaItemTake_Source(take, s)
    reaper.SetMediaItemTakeInfo_Value(take, "D_VOL", 10 ^ ((c[5] or 0) / 20))
    reaper.SetMediaItemInfo_Value(item, "D_LENGTH", math.min(reaper.GetMediaSourceLength(s), 30))
    reaper.SetMediaItemInfo_Value(item, "D_FADEINLEN", 0); reaper.SetMediaItemInfo_Value(item, "D_FADEOUTLEN", 0)
    reaper.UpdateItemInProject(item)
    while reaper.TrackFX_GetCount(tr) > 0 do reaper.TrackFX_Delete(tr, 0) end
    local ok = true
    for _, f in ipairs(chain) do
      local fx = reaper.TrackFX_AddByName(tr, f[1], false, -1)
      if fx < 0 then log("ERROR no cargó", f[1]) ok = false break end
      if f[1] == NW then
        if f[2][PRESET] then reaper.TrackFX_SetParam(tr, fx, PRESET - 1, f[2][PRESET]) end
        for s_, v in pairs(f[2]) do
          if s_ ~= PRESET then
            if LOGP[s_] then reaper.TrackFX_SetParamNormalized(tr, fx, s_ - 1, to_norm(s_, v))
            else reaper.TrackFX_SetParam(tr, fx, s_ - 1, v) end
          end
        end
      else
        for k, v in ipairs(f[2]) do reaper.TrackFX_SetParam(tr, fx, k - 1, v) end
      end
    end
    if not ok then break end
    local file = OUT .. "/" .. name .. ".wav"
    os.remove(file)
    reaper.GetSetProjectInfo(0, "RENDER_SETTINGS", 0, true)
    reaper.GetSetProjectInfo(0, "RENDER_BOUNDSFLAG", 1, true)
    reaper.GetSetProjectInfo(0, "RENDER_SRATE", 48000, true)
    reaper.GetSetProjectInfo(0, "RENDER_CHANNELS", 2, true)
    reaper.GetSetProjectInfo(0, "RENDER_TAILFLAG", 0, true)
    reaper.GetSetProjectInfo_String(0, "RENDER_FILE", OUT, true)
    reaper.GetSetProjectInfo_String(0, "RENDER_PATTERN", name, true)
    reaper.Main_OnCommand(42230, 0)
    local vals = {}
    local fx0 = reaper.TrackFX_GetCount(tr) - 1
    for k = 1, math.min(14, reaper.TrackFX_GetNumParams(tr, fx0)) do local _, v = reaper.TrackFX_GetFormattedParamValue(tr, fx0, k - 1, ""); vals[#vals + 1] = v end
    log("caso", name, table.concat(vals, " | "))
  end
end
reaper.Main_SaveProjectEx(0, OUT .. "/_tmp_test.rpp", 0)
reaper.Main_openProject("noprompt:" .. OUT .. "/_tmp_test.rpp")
reaper.Main_OnCommand(40860, 0) -- cerrar pestaña
log("done")
logf:close()
