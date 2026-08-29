#!/usr/bin/env bash
set -euo pipefail

CODEX_TARGET="${CODEX_HOME:-$HOME/.codex}"
ACTIVE_COUNT=0
COLD_COUNT=0
MCP_COUNT=0

if [[ -d "$CODEX_TARGET/skills" ]]; then
  ACTIVE_COUNT="$(find "$CODEX_TARGET/skills" -mindepth 2 -maxdepth 2 -name SKILL.md -type f | wc -l | tr -d ' ')"
fi
if [[ -d "$CODEX_TARGET/skill-library/leaves" ]]; then
  COLD_COUNT="$(find "$CODEX_TARGET/skill-library/leaves" -mindepth 2 -maxdepth 2 -name SKILL.md -type f | wc -l | tr -d ' ')"
fi
if command -v codex >/dev/null 2>&1; then
  MCP_COUNT="$(codex mcp list --json 2>/dev/null | node -e 'let s="";process.stdin.on("data",d=>s+=d).on("end",()=>{const v=JSON.parse(s);console.log(Array.isArray(v)?v.length:Object.keys(v).length)})')"
fi

echo "Codex home: $CODEX_TARGET"
echo "Active Skills: $ACTIVE_COUNT"
echo "On-demand Skills: $COLD_COUNT"
echo "Configured MCP servers: $MCP_COUNT"
echo "Skill catalog: $(test -f "$CODEX_TARGET/skill-library/catalog.json" && echo ready || echo MISSING)"

if [[ "$ACTIVE_COUNT" -ge 9 && "$COLD_COUNT" -ge 277 && -f "$CODEX_TARGET/skill-library/catalog.json" ]]; then
  echo "Skill installation looks complete."
  exit 0
fi
echo "Installation is incomplete. Run ./INSTALL.command again."
exit 1
