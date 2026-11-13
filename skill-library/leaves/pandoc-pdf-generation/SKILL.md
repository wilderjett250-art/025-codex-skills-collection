---
name: pandoc-pdf-generation
description: PDF generation from markdown via Pandoc/XeLaTeX. TRIGGERS - markdown for PDF, print document, pandoc, xelatex, section numbering, table of contents, page breaks.
allowed-tools: Bash, Read, Write
---

# Pandoc / XeLaTeX PDF

Use when this toolchain is explicitly requested or already established. Preserve the required engine, citation behavior, fonts and publication format.

1. Resolve this SKILL.md's actual directory. The bundled script is [assets/build-pdf.sh](assets/build-pdf.sh), with its adjacent TeX preamble and Lua filter; it already resolves its own resources. Do not rely on `CLAUDE_PLUGIN_ROOT` or create project symlinks by default.
2. Verify the actual installed Pandoc, XeLaTeX, required fonts and compatible Bash. On Windows use PowerShell to inspect executables (`Get-Command`) and invoke only a verified Bash/WSL route; POSIX shell snippets are not PowerShell commands. WSL and Windows paths must be converted for the actual runtime.
3. Inspect the script's `--help` first. Run it from an authorized task directory with explicit input/output paths and the requested orientation. It supports `--portrait`, `--landscape`, `--monospace` and `--hide-details`; do not invent unsupported flags.
4. The provided template's font defaults are examples, not proof of Chinese font coverage. Select the user's required installed fonts via the established project/template configuration; do not silently substitute an engine or typeface.
5. Render/inspect the resulting pages when layout matters, check citations and preserve editable sources. Report a missing dependency precisely; do not claim a successful document from an unrun command or install global packages without the applicable authority.
