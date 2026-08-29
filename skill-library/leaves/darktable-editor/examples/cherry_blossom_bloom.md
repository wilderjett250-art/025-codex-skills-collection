# Worked Example: Cherry Blossom Bloom

**Image:** `DSC09315.ARW` — Sony portrait, woman in front of cherry blossom tree, natural light.
**Goal:** Make cherry blossoms bloom with vivid pink/white color without blowing out the image or adding a haze.

---

## Session log (condensed)

### Step 1 — baseline

```python
open_image("C:/Agents/Darktable_MCP_tool/DSC09315.ARW")
render_preview(session_id)   # shows the RAW as-shot
snapshot(session_id, "baseline")
```

Image looks neutral. Blossoms present but color is muted. Skin tones clean.

---

### Step 2 — first bloom attempt

```python
set_module(session_id, "colorbalancergb", {
    "vibrance": 0.25,
    "saturation": 0.10,
    "chroma": 0.08,
})
render_preview(session_id)
snapshot(session_id, "bloom_v1")
```

Result: colors noticeably more vivid. Blossoms pinkier. User asked to push further.

---

### Step 3 — boosted (dull result, failure)

```python
set_module(session_id, "colorbalancergb", {
    "vibrance": 0.65,
    "saturation": 0.22,
    "chroma": 0.12,
    "highlights_Y": -0.03,   # ← MISTAKE: intended to add contrast
    "global_Y": 0.03,
})
render_preview(session_id)
snapshot(session_id, "boosted")
compare(session_id, "baseline", "boosted", mode="split")
```

**User feedback:** *"The boosted variant is way more dull and greyed out."*

**Root cause:** `highlights_Y: -0.03` pulled down the cherry blossoms (which sit in the highlights). This is the key lesson — lifting `global_Y` and simultaneously pulling `highlights_Y` negative crushed the very tones we were trying to make bloom.

---

### Step 4 — brighter (haze result, second failure)

```python
set_module(session_id, "colorbalancergb", {
    "vibrance": 0.65,
    "saturation": 0.22,
    "chroma": 0.12,
    "brilliance_global": 0.08,   # ← MISTAKE: trying to add brightness
})
render_preview(session_id)
```

**User feedback:** *"There is a haze over the entire image, it looks like it is a layer on top of it, that's not how exposure works."*

**Root cause:** `brilliance_global` is a highlight-bloom/glow effect, not an exposure substitute. It creates a lifted, milky look rather than genuine brightness.

---

### Step 5 — settled bloom (success)

```python
set_module(session_id, "colorbalancergb", {
    "vibrance": 0.65,
    "saturation": 0.22,
    "chroma": 0.12,
    # No zone luma, no brilliance — pure color push
})
render_preview(session_id)
snapshot(session_id, "final_bloom")
compare(session_id, "baseline", "final_bloom", mode="split")
```

**Result:** Blossoms bloom with vivid pink. No haze, no dull highlights. Skin tones remain warm but not oversaturated.

---

## Key lessons encoded from this session

1. **Do not touch `highlights_Y` when the subject IS the highlights.** Blossoms are bright — pulling highlights down desaturates and compresses them.
2. **`brilliance_global` ≠ exposure.** It adds glow/haze. Leave it at 0 for clean work.
3. **Pure color push works.** `vibrance + saturation + chroma` without any luma fiddling produced the best result.
4. **No `exposure` module** was used in the final settled state. Vibrance at 0.65 is safe without it.
5. **Compare after every meaningful change.** The split-wipe comparison was what revealed the "dull" problem that wasn't obvious from the preview alone.

---

## Final settled params

```python
{
    "vibrance":   0.65,
    "saturation": 0.22,
    "chroma":     0.12,
}
```

Module: `colorbalancergb`, no other modules active.
