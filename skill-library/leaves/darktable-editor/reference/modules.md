# Module Parameter Reference

Modules with full encode/decode support in `dt-edit-mcp`. All params are Python dicts passed to `set_module`.

---

## `exposure` — EV and black level (modversion 7)

Darktable 4.6.1 writes this module at **modversion 7** (28 bytes). Do not assume v6.

```python
params = {
    "mode": "manual",              # "manual" or "deflicker"
    "exposure": 0.0,               # EV, float. -4.0 … +4.0 useful range
    "black": 0.0,                  # black level lift, float. usually 0
    "deflicker_percentile": 50.0,  # only relevant when mode="deflicker"
    "deflicker_target_level": -4.0,
    "compensate_exposure_bias": True,  # ALWAYS leave True (see pitfalls.md)
    "compensate_hilite_pres": False,
}
```

### Safe ranges

| Param | Safe | Caution | Avoid |
|---|---|---|---|
| `exposure` | -2.0 … +1.5 | ±2.0–3.0 | Outside ±3.0 |
| `black` | -0.01 … +0.02 | ±0.05 | Outside ±0.1 |

**Critical:** When `colorbalancergb.vibrance > ~0.4`, combining *any* `exposure` module entry breaks the pipeline (white or black render). See `pitfalls.md §1`. Prefer `colorbalancergb.global_Y` for subtle brightness changes when vibrance is high.

---

## `temperature` — white balance (modversion 3)

Controls RGBG channel multipliers and illuminant adaptation.

```python
params = {
    "temperature": 5500.0,   # Kelvin. Tungsten ~3200, Daylight ~5500, Cloudy ~6500
    "tint": 1.0,             # Green-magenta shift. 1.0 = neutral
    "red": 1.0,              # individual channel coefficients (usually leave these)
    "green": 1.0,
    "blue": 1.0,
    "g2": 1.0,
    "illuminant": 0,         # integer enum, 0 = camera WB
    "adaptation": 0,
}
```

### Safe ranges

| Param | Safe | Effect |
|---|---|---|
| `temperature` | 2800–8000 | Full range is safe; visual effect is large at extremes |
| `tint` | 0.8–1.2 | Beyond this produces obvious casts |

When only adjusting warmth, set `temperature` and leave everything else at defaults.

---

## `colorbalancergb` — primary color grading (modversion 5, gzipped)

This is the main grading module. 132-byte struct, uses gzip+base64 encoding.

### Global parameters

```python
params = {
    # These three are the main dials for overall color intensity
    "vibrance":   0.0,   # Perceptual saturation boost. Safe: 0–0.35. See caution below.
    "saturation": 0.0,   # Linear saturation. Safe: -0.3–0.3
    "chroma":     0.0,   # Chroma scaling. Safe: -0.2–0.2

    # Luma
    "global_Y":   0.0,   # Global brightness. Safe: -0.08–0.08. NOT the same as EV.
}
```

**`vibrance` caution:** > 0.4 combined with an `exposure` module entry currently breaks the pipeline. Safe ceiling when using `exposure`: 0.35. Safe ceiling without `exposure` module: ~0.65 (tested in session).

### Zone parameters (shadows / midtones / highlights)

Zones are approximate: shadows ≈ bottom 25% luminance, midtones ≈ 25–75%, highlights ≈ top 25%.

```python
params = {
    # Y = luminance (luma), C = chroma (saturation), H = hue angle (0–360°)
    "shadows_Y":    0.0,   # lift/lower shadow tones
    "midtones_Y":   0.0,   # lift/lower midtone tones
    "highlights_Y": 0.0,   # lift/lower highlight tones

    "shadows_C":    0.0,   # saturate/desaturate shadows
    "midtones_C":   0.0,
    "highlights_C": 0.0,

    "shadows_H":    0.0,   # hue shift in shadows (degrees, 0–360)
    "midtones_H":   0.0,
    "highlights_H": 0.0,

    # Zone weights (how wide each zone's influence is)
    "shadows_weight":    1.0,
    "midtones_weight":   1.0,
    "highlights_weight": 1.0,
}
```

### Silently-ignored field names (do not use)

These look plausible but are **not valid** and pack to 0:

- `contrast` ❌
- `global_saturation` ❌ → use `saturation`
- `global_vibrance` ❌ → use `vibrance`
- `global_chroma` ❌ → use `chroma`

### Zone luma warnings

- Pulling `highlights_Y` negative to "add contrast" will drag down whatever subject lives in the highlights (e.g. cherry blossoms, bright sky).
- Identify where the subject sits tonally before touching zone luma.
- For contrast without zone luma: use small positive `shadows_Y` (lift blacks) combined with no `highlights_Y` change — this gives an S-curve-like effect safely.

---

## Unsupported modules (opaque passthrough)

These modules in the XMP can be enabled/disabled via `disable_module`, but their `params` cannot be modified:

- `filmicrgb` — tone mapping
- `toneequal` — zone-based tone equalizer
- `denoiseprofile` — profiled noise reduction
- `sharpen`, `diffuse` — sharpening
- `channelmixerrgb` — color calibration
- `monochrome` — BW conversion (use this via the GUI, not the agent)
- All others not listed above

For these, only `enabled` can be toggled via `set_module(..., enabled=False)`.
