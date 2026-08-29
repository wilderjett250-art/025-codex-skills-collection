---
name: autocad-cad-homework
description: Use on Windows to create, edit, inspect, convert, or package AutoCAD and CAD coursework in DWG, DXF, script, AutoLISP, layout, dimension, or plotted-PDF form.
---

# AutoCAD CAD Homework

Use this skill for CAD coursework and AutoCAD deliverables on the current Windows machine.

## Local Setup

- Discover `acad.exe` and `accoreconsole.exe` from the current AutoCAD installation.
- Configure `autocad_mcp` and `autocad_coreconsole` with this machine's own bridge and paths.
- Prefer the headless Core Console route for background script execution when it is installed and validated.

## Default Route

1. Read the assignment source first, especially Word/PDF briefs and screenshots.
2. Preserve the user's source files. Copy reference material to an ASCII working folder when automation has trouble with Chinese or WeChat cache paths.
3. Prefer deterministic CAD generation over mouse drawing:
   - Use `autocad_coreconsole`, `accoreconsole.exe`, `.scr`, and AutoLISP first when the user needs background execution that does not occupy the screen.
   - Generate DXF with `ezdxf` for geometry drafts, checks, and fast iteration.
   - Use AutoCAD scripts, AutoLISP, COM, or AutoCAD MCP for DWG creation, block work, layer setup, dimensioning, layout, and PDF plotting.
   - Use `computer-use` only for first-launch dialogs, visual verification, APPLOAD/startup-suite setup, or actions unavailable through native CAD interfaces.
4. For deliverables requiring DWG compatibility, save or convert through AutoCAD and verify the resulting file opens in AutoCAD.
5. Package only the requested final files and inspect the archive contents before reporting completion.

## Coursework Standards

- For A3 drawing work, explicitly set units, scale, model/layout intent, layers, lineweights, text style, dimension style, title block, and plot settings.
- For Chinese CAD text, use Songti-style Chinese text and Times New Roman for Latin letters and numbers when the brief requires it.
- For title blocks, create a reusable external DWG block when required by the assignment.
- For student-number parameter changes, extract the exact name, student number, last digit, and last two digits from the user-provided brief or chat evidence before drawing.
- Save a CAD2018-compatible DWG when the assignment requires CAD2018 format, even when the installed AutoCAD version is newer.

## Validation

- Confirm the installed AutoCAD path exists before using it.
- Validate Python CAD helpers with an import or focused smoke test before relying on them.
- For generated drawings, verify at least:
  - file exists and has nonzero size;
  - expected layers and title-block text are present;
  - PDF output opens or renders;
  - archive contains exactly the required deliverables.
- If AutoCAD asks for login, licensing, trusted file, or macro loading approval, stop and ask the user to handle or approve that specific UI step.
- Do not use `computer-use` for long CAD drawing workflows when the user wants to keep using the screen. Prefer core console, MCP, COM, or script execution.

## Safety

- Keep third-party MCP servers in a dedicated, user-approved local tools directory.
- Avoid enabling broad desktop-control MCPs unless the task specifically needs GUI control beyond the existing `computer-use` plugin.
- Do not leave temporary scripts, generated test drawings, or partial PDFs in the final handoff folder.
