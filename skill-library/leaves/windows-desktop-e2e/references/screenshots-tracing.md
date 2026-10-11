## Artifact Management

```python
# Screenshot on demand
page.screenshot("after_login")

# Full-screen capture (when window is off-screen or minimised)
import pyautogui
pyautogui.screenshot("artifacts/fullscreen.png")

# Screen recording with ffmpeg (start before test, stop after)
import subprocess

def start_recording(name):
    return subprocess.Popen([
        "ffmpeg", "-f", "gdigrab", "-framerate", "10",
        "-i", "desktop", "-y", f"artifacts/videos/{name}.mp4"
    ], stdin=subprocess.PIPE, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

def stop_recording(proc):
    proc.stdin.write(b"q"); proc.stdin.flush(); proc.wait(timeout=10)
```

## Per-Step Trace (opt-in)

The default failure screenshot is often too thin for diagnosing flaky tests. The step-level trace below is **off by default** — enable it only when reproducing a flaky case.

### Enable

```bash
E2E_TRACE=1 pytest tests/test_login.py -v
# Include typed text in the JSONL log (DO NOT use on tests that type credentials/PII):
E2E_TRACE=1 E2E_TRACE_INCLUDE_TEXT=1 pytest ...
```

### Patch into BasePage

```python
import os, json, time
TRACE_ENABLED      = os.environ.get("E2E_TRACE") == "1"
TRACE_INCLUDE_TEXT = os.environ.get("E2E_TRACE_INCLUDE_TEXT") == "1"

class BasePage:
    _step = 0

    def _trace(self, action, spec=None, text=None):
        if not TRACE_ENABLED:
            return
        BasePage._step += 1
        idx = f"{BasePage._step:03d}"
        os.makedirs(ARTIFACT_DIR, exist_ok=True)
        try:
            self.window.capture_as_image().save(
                os.path.join(ARTIFACT_DIR, f"step_{idx}_{action}.png"))
        except Exception:
            pass  # capture failure must not break the test
        rec = {
            "ts": time.time(), "step": BasePage._step, "action": action,
            "locator": getattr(spec, "criteria", None),
            "text": text if TRACE_INCLUDE_TEXT else ("<redacted>" if text else None),
        }
        with open(os.path.join(ARTIFACT_DIR, "trace.jsonl"), "a") as f:
            f.write(json.dumps(rec) + "\n")

    def click(self, spec):
        self.wait_visible(spec); self._trace("click_before", spec)
        spec.click_input();      self._trace("click_after",  spec)

    def type_text(self, spec, text):
        self.wait_visible(spec); self._trace("type_before", spec, text)
        # ... existing set_edit_text / keyboard fallback ...
        self._trace("type_after", spec)
```

### Caveats

- **PII / credentials**: `type_text` content is `<redacted>` by default. Never set `E2E_TRACE_INCLUDE_TEXT=1` on login or payment flows.
- **Overhead**: ~50–200ms per action + one PNG per step on disk. Don't enable on the default CI matrix — only on a dedicated flake-repro job.
- **Artifact bloat**: a long flow produces tens of MB; tune `retention-days` accordingly.
- **Parallel/rerun hygiene**: this simple example appends to `trace.jsonl` and uses a class-level counter. Clear the artifact directory before reruns, and use per-worker artifact dirs for parallel tests.
- **Coverage gap**: actions performed outside `BasePage` (raw `pywinauto` calls in test code) are not traced.

## Fallback: Screenshot Mode

When a control is not reachable via UIA (self-drawn, third-party, game engine):

```bash
pip install pyautogui Pillow opencv-python
```

```python
import pyautogui, cv2, numpy as np
from PIL import Image

def find_image_on_screen(template_path, confidence=0.85):
    """Locate a template image on screen. Returns (x, y) center or None."""
    screen   = np.array(pyautogui.screenshot())
    template = np.array(Image.open(template_path))
    result   = cv2.matchTemplate(
        cv2.cvtColor(screen, cv2.COLOR_RGB2BGR),
        cv2.cvtColor(template, cv2.COLOR_RGB2BGR),
        cv2.TM_CCOEFF_NORMED,
    )
    _, max_val, _, max_loc = cv2.minMaxLoc(result)
    if max_val >= confidence:
        h, w = template.shape[:2]
        return max_loc[0] + w // 2, max_loc[1] + h // 2
    return None

def click_image(template_path, confidence=0.85):
    pos = find_image_on_screen(template_path, confidence)
    if pos is None:
        raise RuntimeError(f"Image not found on screen: {template_path}")
    pyautogui.click(*pos)
```

### DPI / Scaling Rules (screenshot mode only)

Screenshot matching is brutally sensitive to Windows display scaling (100% / 125% / 150%). Three hard rules:

1. **Capture templates at the same scale as the target machine.** Don't try to rescue a mismatch with `PIL.Image.resize` — `cv2.matchTemplate` is very fragile against resampling artefacts.
2. **Pin the CI display scaling.** On `windows-latest` add a step like `Set-DisplayResolution 1920 1080 -Force` and disable per-monitor DPI scaling, so screenshot dimensions are reproducible.
3. **Record the scale alongside each artefact.** On capture, write `GetDpiForWindow(hwnd) / 96` to `artifacts/<test>/metadata.json` — postmortems become obvious instead of guess-work.

> Process-level DPI awareness (`SetProcessDpiAwarenessContext`) **can conflict with Qt's own DPI handling** when the app under test is Qt-based. Prefer "same-scale templates + CI pin" over flipping process-wide DPI mode in fixtures.

### Debugging Match Confidence

When tuning the `confidence` threshold, the only sane workflow is to **see** where the match landed. The helper below is diagnosis-only — do not call it from test code.

```python
def debug_match(template_path, out="artifacts/match_debug.png", confidence=0.85):
    """Diagnosis-only. Draw the best-match rectangle + score back on the current screen.

    NOT for production tests — use when calibrating confidence or chasing false matches.
    """
    import os, cv2, pyautogui, numpy as np
    screen = np.array(pyautogui.screenshot())[:, :, ::-1]
    tpl    = cv2.imread(template_path)
    if tpl is None:
        raise RuntimeError(f"Template unreadable: {template_path}")
    res    = cv2.matchTemplate(screen, tpl, cv2.TM_CCOEFF_NORMED)
    _, mv, _, ml = cv2.minMaxLoc(res)
    h, w   = tpl.shape[:2]
    colour = (0, 255, 0) if mv >= confidence else (0, 0, 255)  # green pass / red fail
    cv2.rectangle(screen, ml, (ml[0]+w, ml[1]+h), colour, 2)
    cv2.putText(screen, f"score={mv:.3f} thr={confidence}",
                (ml[0], max(20, ml[1]-6)),
                cv2.FONT_HERSHEY_SIMPLEX, 0.7, colour, 2)
    os.makedirs(os.path.dirname(out) or ".", exist_ok=True)
    cv2.imwrite(out, screen)
    return mv
```

**Use sparingly** — image matching breaks on DPI changes, theme switches, and partial occlusion.
Always try UIA first; fall back to screenshots only for genuinely unreachable controls.

