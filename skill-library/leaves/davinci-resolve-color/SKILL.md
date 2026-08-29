---
name: davinci-resolve-color
description: Use when the user explicitly requires local DaVinci Resolve for grading, LUT development, media or timeline workflows, export checks, or Resolve scripting diagnostics.
---

# Davinci Resolve Color

## Overview

Use the local DaVinci Resolve installation and its official scripting bridge for color workflows. Prefer Photoshop for ordinary single-photo retouching unless the user explicitly requires DaVinci Resolve.

## Environment

- Discover the Resolve executable and version on the current machine; do not assume another operator's install path.
- Resolve's official scripting module is commonly under the shared Blackmagic Design application-data directory, but verify it locally.
- Set `DAVINCI_RESOLVE_MCP_SERVER` to this machine's `davinci-resolve-mcp` `server.py` before using the bundled self-test helper.
- Use a user-approved task output directory and never overwrite source media.

## Route

1. Preserve the source media. Copy user-provided images or video clips to a task folder before any Resolve import/export workflow.
2. Run the MCP self-test before claiming Resolve automation is available:

```powershell
python .\scripts\check_environment.py
```

3. If Resolve is not running, either launch it through the MCP `launch_resolve` tool or ask the user to open it when GUI/login/project prompts are expected.
4. After Resolve is running, use the MCP `resolve_scripting_status` tool or the self-test command to confirm the scripting bridge is connected.
5. For a single JPG/PNG photo, use Resolve only when the user asks for DaVinci specifically; otherwise use `photoshop-editing`.
6. Keep exports under the user-approved task output directory.

## Color Guidance

- For "transparent" or "clean" looks: reduce haze, set black/white points conservatively, protect face highlights, lift midtone contrast, and avoid crushing backlit shadows.
- For portraits: check face and glasses at 100% or with a crop before final export. Do not introduce waxy skin or haloed hair edges.
- For backlit images: preserve the soft light character; avoid making the image look like a hard daylight correction unless requested.
- For still-image workflows, document whether the final export came from Resolve, Photoshop, or an approved fallback.

## Validation

Before final delivery, verify:

- Resolve/Photoshop route used matches the user's requirement.
- Source file was not overwritten.
- Export path, dimensions, and format are reported.
- For portraits, inspect full frame and a face crop.
