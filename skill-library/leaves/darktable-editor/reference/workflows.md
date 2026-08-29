# Canonical Edit Workflows

Named recipes for common photo editing goals. Each is a sequence of `set_module` calls with rationale. All use `colorbalancergb` only unless noted — the `exposure` module is avoided where vibrance is pushed (see `pitfalls.md §1`).

---

## Bloom — saturated color pop

**When to use:** Flowers, landscapes, vivid subjects where you want punchy color without blowing out tones. The characteristic "cherry blossom bloom" look.

```python
set_module(session_id, "colorbalancergb", {
    "vibrance":   0.25,   # perceptual saturation boost — keep ≤0.35 if exposure module present
    "saturation": 0.10,   # gentle linear saturation
    "chroma":     0.08,   # slight chroma push
})
```

**Render and check.** Then optionally push further:

```python
# If you want more without risking exposure interaction:
set_module(session_id, "colorbalancergb", {
    "vibrance":   0.35,
    "saturation": 0.15,
    "chroma":     0.10,
})
```

**Do not combine with `exposure` module** when vibrance > 0.35. Use `global_Y` for small brightness tweaks instead:

```python
set_module(session_id, "colorbalancergb", {
    "vibrance":   0.35,
    "saturation": 0.15,
    "global_Y":   0.02,   # slight brightness lift — safe alternative to exposure EV
})
```

**Interaction notes:** Avoid `highlights_Y` negative — it pulls down bright subjects (blossoms, sky) and produces a dull/greyed look that contradicts the bloom intent.

---

## Cinematic teal-orange

**When to use:** Portraits, street, drama. Classic warm skin / cool shadows split.

```python
set_module(session_id, "colorbalancergb", {
    # Warm highlights (orange-ish)
    "highlights_H": 50,    # hue shift toward orange (0° = red, 60° = yellow, so ~50° warms)
    "highlights_C": 0.04,  # slight chroma push in highlights

    # Cool shadows (teal)
    "shadows_H":   200,    # hue shift toward cyan-teal
    "shadows_C":   0.04,

    # Gentle contrast
    "shadows_Y":   0.02,   # lift blacks slightly
})
```

**Check skin tones** — hue angle 50° in highlights can push toward orange. If skin looks too tan, reduce `highlights_H` to 30–40 or pull `highlights_C` back to 0.02.

**Interaction notes:** Don't combine with strong `vibrance` — the chroma push compounds and oversaturates the orange tones.

---

## Lift and separate (subtle contrast)

**When to use:** Flat-lit scenes, overcast days, studio. Adds dimension without dramatic color shifts.

```python
set_module(session_id, "colorbalancergb", {
    "shadows_Y":   0.03,    # lift blacks → breathing room in shadows
    "midtones_Y": -0.01,    # very slight mid pull → perceived depth
    # Leave highlights_Y at 0 — don't crush the brights
})
```

Follow with white balance correction if the flat light made the color cast obvious:

```python
set_module(session_id, "temperature", {
    "temperature": 5800,   # warm up slightly if overcast blue cast
})
```

---

## Moody / desaturated

**When to use:** Dark portraits, architectural, scenes where you want color but restrained.

```python
set_module(session_id, "colorbalancergb", {
    "saturation": -0.12,   # pull back overall saturation
    "shadows_Y":   0.02,   # lifted blacks for matte/analog feel
})
```

Optional: add slight warm-shadow color for the "faded analog" look:
```python
    "shadows_H":   30,     # warm shadows (toward yellow-orange)
    "shadows_C":   0.02,
```

---

## Clean-up / neutral baseline

**When to use:** Starting point before any stylistic grade, or to undo accumulated edits.

```python
reset_all(session_id)
```

Then if white balance is obviously off, correct it first before any other edit:

```python
# Check by calling get_module_params(session_id, "temperature") and comparing to camera WB
set_module(session_id, "temperature", {"temperature": 5200, "tint": 1.0})
```

Render the clean baseline, snapshot it, then start the stylistic work.

---

## Reference-guided grade

**When to use:** User provides a reference image ("make it look like this").

1. Call `analyze_reference(ref_path)` — returns LAB stats (mean, std) per tone zone, dominant hues, saturation level, contrast estimate.
2. Read the result and translate to `colorbalancergb` params:
   - Dominant hue in highlights → `highlights_H` + `highlights_C`
   - Dominant hue in shadows → `shadows_H` + `shadows_C`
   - High saturation std → push `vibrance`
   - Low contrast estimate → consider `shadows_Y` lift
3. Apply as one `set_module` call, render, compare.
4. Iterate based on user feedback.

Do not apply `analyze_reference` output blindly — treat it as a starting-point estimate. The agent's visual reasoning from the inline preview is the real feedback loop.

---

## Black & white

**Not currently supported** via agent edits. The `monochrome` module is opaque passthrough. To convert to BW:

1. Open the image in Darktable GUI, apply the monochrome module with desired channel mix, save the XMP.
2. Then open with `open_image` and continue grading (contrast, toning) via the skill.

Or: use `colorbalancergb` to strongly desaturate (`saturation: -1.0`) as a rough approximation — but this lacks channel-mix control and is not the recommended path.
