# Empirical Pitfalls

Failures discovered during real editing sessions. Each entry: symptom → threshold → workaround.

---

## 1. exposure + high vibrance = broken render (white or black)

**Symptom:** `render_preview` returns a pure white or pure black image.

**Trigger:** Any `exposure` history entry combined with `colorbalancergb.vibrance > ~0.4–0.5`.

- Positive EV + vibrance=0.65 → white
- Negative EV + vibrance=0.5 → black
- No exposure module + vibrance=0.65 → renders correctly

**Threshold:** The breakpoint appears around vibrance=0.4 when the exposure module is present. Vibrance=0.35 is consistently safe with exposure.

**Workaround options (in order of preference):**
1. Remove the `exposure` module. Use `colorbalancergb.global_Y` (range -0.08…+0.08) for small brightness adjustments.
2. Keep vibrance ≤ 0.35 if the exposure module must stay.
3. Use `undo` to remove the last `set_module` call if you've already triggered it.

**Not yet root-caused.** Possibly a headless darktable-cli pipeline difference vs. the GUI; possibly a codec struct alignment issue at specific param combinations. Flag it explicitly to the user rather than silently retrying.

---

## 2. compensate_exposure_bias must be True

**Symptom:** Image over-exposes dramatically (appears blown out) despite a negative EV value.

**Trigger:** `compensate_exposure_bias=False` combined with negative EV + colorbalancergb.

**Why:** This flag tells darktable to compensate for the camera's embedded EXIF exposure compensation. Without it, the pipeline double-applies or misapplies the base exposure.

**Rule:** Never set `compensate_exposure_bias=False` unless you have a specific reason. The codec default is now `True`, matching darktable GUI default. Do not override it.

---

## 3. brilliance_global adds haze, not brightness

**Symptom:** Image looks like a translucent layer was placed on top — a flat haze rather than genuine brightness increase. User feedback verbatim: *"there is a haze over the entire image, it looks like it is a layer on top of it, thats not how exposure works"*.

**Trigger:** `colorbalancergb.brilliance_global` set to any positive value (e.g. 0.08).

**Why:** `brilliance_global` is a highlight-bloom/glow effect, not an exposure analog. It lifts mid-to-high tones non-linearly in a way that looks like a luminosity overlay.

**Rule:** Do not use `brilliance_global` as a substitute for exposure or brightness. Use `global_Y` for brightness, `exposure` (with vibrance ≤ 0.35) for genuine EV changes.

---

## 4. highlights_Y negative pulls down the subject

**Symptom:** The image looks dull and greyed-out despite intending a contrast boost. User feedback: *"the boosted variant is way more dull and greyed out"*.

**Trigger:** `colorbalancergb.highlights_Y` set to a small negative value (e.g. -0.03) to "add contrast by pulling down highlights".

**Why:** `highlights_Y` affects the top ~25% of luminance. If the subject (blossoms, bright faces, sky detail) lives in the highlights, pulling them down desaturates and compresses that part of the tonal range, creating a flat look.

**Rule:** Before adjusting zone luma, identify where the subject sits tonally:
- Subject in highlights (bright flowers, sky, window light) → do NOT pull `highlights_Y` negative
- Subject in midtones → `highlights_Y` changes won't hurt it
- To add contrast: lift `shadows_Y` slightly (0.02–0.04) without touching highlights

**Also:** any positive `shadows_Y` lifts the black point and produces a matte/milky haze effect — exactly what a "no haze" edit must avoid. If the goal is punchy and clean, keep `shadows_Y = 0`. Use vibrance/saturation/chroma for punch instead.

---

## 5. Silently-ignored field names

**Symptom:** A `set_module` call succeeds and returns a history entry, but the render looks unchanged. `get_module_params` shows 0 for the values you tried to set.

**Trigger:** Using field names that sound correct but are not in the codec schema:

| Wrong name | Correct name |
|---|---|
| `contrast` | no direct equivalent; use zone `_Y` params |
| `global_saturation` | `saturation` |
| `global_vibrance` | `vibrance` |
| `global_chroma` | `chroma` |
| `brightness` | `global_Y` |

These pack silently to 0.0. There is no error, no warning.

**Rule:** Always verify with `get_module_params` after an edit that changed something you expected to see.

---

## 6. modversion mismatch = black or wrong render

**Symptom:** `render_preview` returns black even on a clean baseline with only the `exposure` module applied.

**Trigger:** codec writing `modversion=6` when darktable 4.6.1 expects `modversion=7` for the exposure module.

**Why:** darktable reads the params struct according to modversion. A 24-byte v6 struct read as a v7 28-byte struct produces garbage field values.

**Status: Fixed.** The codec now writes modversion=7 (28 bytes, includes `compensate_hilite_pres`). If this error re-appears after a darktable upgrade, check whether DT bumped the modversion again.

---

## 7. Session lost after MCP server restart

**Symptom:** `set_module` or `render_preview` raises "Session not found".

**Trigger:** The MCP server was restarted (e.g. after `/mcp` reconnect in Claude Code, after a settings change, after a server crash).

**Why:** Sessions are in-memory only. The XMP on disk survives but the session object does not.

**Fix:** Call `open_image(raw_path)` again. The XMP is preserved; history continues from where it was. Then re-run `snapshot("baseline")` if needed.

---

## 8. OneDrive path locks XMP during atomic write

**Symptom:** `set_module` raises `PermissionError` (WinError 32) or the XMP write silently fails.

**Trigger:** The RAW file lives under `C:\Users\...\OneDrive\` or another synced folder. OneDrive holds transient locks on files it is uploading.

**Fix:** Move the RAW file to a non-synced directory before editing (`C:\Photos\`, `D:\RAW\`, etc.). Warn the user at `open_image` time if the path contains "OneDrive".

---

## 9. darktable-cli writes output with _01 suffix

**Symptom:** `render_preview` returns "file not found" even though darktable-cli reported success (exit 0).

**Trigger:** A stale `.jpg` exists at the target output path from a previous failed or interrupted render. darktable-cli avoids overwriting it by appending `_01`.

**Fix:** Clear `.dtmcp/preview/` and `.dtmcp/preview_cache/` between sessions, or call `open_image(raw_path, reset=True)` to start clean.

---

## 10. compare tool requires two snapshot labels that actually exist

**Symptom:** `compare` raises KeyError or "snapshot not found".

**Trigger:** Calling `compare("baseline", "boosted")` when you forgot to call `snapshot("boosted")` after the edit.

**Rule:** Always call `snapshot(session_id, label)` immediately after a `render_preview` the user approves, before calling `compare`. Use `list_snapshots(session_id)` to verify what's available.

---

## 11. temperature module black render when added fresh

**Symptom:** Pure black render after `set_module(session_id, "temperature", {"temperature": 4800})` on an image with no prior temperature history entry (fresh open or after `reset_all`).

**Trigger:** `illuminant=Camera` (the default) with `coeffs=[1,1,1,1]` (the old default when no coeffs were supplied). darktable expects real sensor multipliers with Camera illuminant; all-ones is an invalid state.

**Status: Fixed.** `Session.set_module` now reads the camera's embedded WB multipliers from EXIF via `rawpy` and injects them automatically when adding temperature fresh. `TemperatureCodec.encode` also raises `ValueError` eagerly if the invalid combination is ever passed directly.

**If it re-appears:** Check that `rawpy` is installed (`uv sync`) and that the RAW file is a format rawpy supports. If `rawpy` fails, the fallback coeffs `[2.0, 1.0, 1.5, 1.0]` are used — still valid, but the WB accuracy will be approximate until the user fine-tunes.

---

## 12. reset=True strips auto-presets → grainy / flat renders

**Symptom:** Renders look noticeably grainy and flat after `open_image(raw_path, reset=True)`. Darktable GUI shows the image with no noise reduction applied.

**Cause:** The old code set `auto_presets_applied=1` with an empty history, telling darktable "defaults already applied" when nothing was in the pipeline. Darktable skipped re-applying its default modules (denoise profiled, filmic rgb, etc.).

**Status: Fixed.** `session.py` now sets `auto_presets_applied=0` on reset, so darktable re-applies its full default pipeline on every render.

**Rule:** Avoid `reset=True` unless you genuinely need a blank slate. For undoing user edits within a session, use `reset_all(session_id)` instead — it moves the history cursor to 0 without touching the XMP structure.
