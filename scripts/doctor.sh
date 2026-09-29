#!/usr/bin/env bash
set -euo pipefail

CODEX_TARGET="${CODEX_HOME:-$HOME/.codex}"
REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
ACTIVE_COUNT=0
COLD_COUNT=0
MCP_COUNT=0
EXPECTED_ACTIVE="$(find "$REPO_ROOT/skills" -mindepth 2 -maxdepth 2 -name SKILL.md -type f | wc -l | tr -d ' ')"
EXPECTED_COLD="$(find "$REPO_ROOT/skill-library/leaves" -mindepth 2 -maxdepth 2 -name SKILL.md -type f | wc -l | tr -d ' ')"

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

CATALOG_COUNT=0
LOAD_SMOKE=0
DUPLICATES=0
if [[ -f "$CODEX_TARGET/skill-library/catalog.json" ]]; then
  CATALOG_COUNT="$(node -e 'const fs=require("node:fs");const c=JSON.parse(fs.readFileSync(process.argv[1],"utf8").replace(/^\uFEFF/,""));console.log(c.skills.length)' "$CODEX_TARGET/skill-library/catalog.json")"
fi
if [[ -f "$CODEX_TARGET/skill-library/scripts/read-skill.mjs" && "$CATALOG_COUNT" -gt 0 ]]; then
  CHECK_ROOT="${SKILL_ACTIVITY_TEST_ROOT:-${TMPDIR:-/tmp}}"
  CHECK_DIR="$(mktemp -d "$CHECK_ROOT/codex-skill-doctor.XXXXXXXX")"
  if SKILL_ACTIVITY_DIR="$CHECK_DIR" node "$CODEX_TARGET/skill-library/scripts/read-skill.mjs" skill-library-router >/dev/null 2>&1; then
    LOAD_SMOKE=1
  fi
  if [[ -d "$CHECK_DIR" && "$(basename "$CHECK_DIR")" == codex-skill-doctor.* ]]; then
    rm -r "$CHECK_DIR"
  fi
fi
for active in "$CODEX_TARGET"/skills/*/SKILL.md; do
  [[ -f "$active" ]] || continue
  name="$(basename "$(dirname "$active")")"
  if [[ -f "$CODEX_TARGET/skill-library/leaves/$name/SKILL.md" ]]; then
    DUPLICATES=$((DUPLICATES + 1))
  fi
done
echo "Installed catalog entries: $CATALOG_COUNT"
echo "On-demand Skill read: $(test "$LOAD_SMOKE" -eq 1 && echo passed || echo FAILED)"
echo "Duplicate active/library names: $DUPLICATES"

if [[ "$ACTIVE_COUNT" -ge "$EXPECTED_ACTIVE" && "$COLD_COUNT" -ge "$EXPECTED_COLD" && "$CATALOG_COUNT" -ge $((EXPECTED_ACTIVE + EXPECTED_COLD)) && "$DUPLICATES" -eq 0 && "$LOAD_SMOKE" -eq 1 ]]; then
  echo "Skill installation looks complete."
  exit 0
fi
echo "Installation is incomplete. Run ./INSTALL.command again."
exit 1
