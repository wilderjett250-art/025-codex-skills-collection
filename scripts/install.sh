#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"
CODEX_TARGET="${CODEX_HOME:-$HOME/.codex}"
PROFILE_NAME="full"
FILESYSTEM_ROOT=""
FORCE_MCP=0
SKIP_MCP=0
SKIP_PLUGINS=0

while [[ $# -gt 0 ]]; do
  case "$1" in
    --profile) PROFILE_NAME="$2"; shift 2 ;;
    --filesystem-root) FILESYSTEM_ROOT="$2"; shift 2 ;;
    --force) FORCE_MCP=1; shift ;;
    --skip-mcp) SKIP_MCP=1; shift ;;
    --skip-plugins) SKIP_PLUGINS=1; shift ;;
    *) echo "Unknown argument: $1" >&2; exit 2 ;;
  esac
done

command -v node >/dev/null 2>&1 || { echo "Node.js is required." >&2; exit 1; }
mkdir -p "$CODEX_TARGET/skills" "$CODEX_TARGET/skill-library"
STAMP="$(date +%Y%m%d-%H%M%S)"
BACKUP_ROOT="$CODEX_TARGET/backups/codex-skills-mcp-toolkit/$STAMP"
mkdir -p "$BACKUP_ROOT/skills"

echo "==> Target Codex home: $CODEX_TARGET"
echo "==> Backing up matching content"
if [[ -f "$CODEX_TARGET/config.toml" ]]; then
  cp "$CODEX_TARGET/config.toml" "$BACKUP_ROOT/config.toml"
fi
for source in "$REPO_ROOT"/skills/*; do
  [[ -d "$source" ]] || continue
  name="$(basename "$source")"
  if [[ -d "$CODEX_TARGET/skills/$name" ]]; then
    cp -R "$CODEX_TARGET/skills/$name" "$BACKUP_ROOT/skills/$name"
  fi
done
if [[ -d "$CODEX_TARGET/skill-library/leaves" ]]; then
  cp -R "$CODEX_TARGET/skill-library" "$BACKUP_ROOT/skill-library"
fi
echo "  Backup: $BACKUP_ROOT"

echo "==> Installing active Skills"
for source in "$REPO_ROOT"/skills/*; do
  [[ -d "$source" ]] || continue
  name="$(basename "$source")"
  mkdir -p "$CODEX_TARGET/skills/$name"
  cp -R "$source"/. "$CODEX_TARGET/skills/$name"/
  echo "  Installed: $name"
done

echo "==> Installing the on-demand Skill Library"
cp -R "$REPO_ROOT/skill-library"/. "$CODEX_TARGET/skill-library"/
cp "$REPO_ROOT/scripts/route-task.mjs" "$CODEX_TARGET/skill-library/scripts/route-task.mjs"
cp "$REPO_ROOT/scripts/find-skills.mjs" "$CODEX_TARGET/skill-library/scripts/find-skills.mjs"
node "$REPO_ROOT/scripts/materialize-catalog.mjs" \
  "$REPO_ROOT/skill-library/catalog.portable.json" \
  "$CODEX_TARGET/skill-library/catalog.json"

if [[ "$SKIP_MCP" -eq 0 ]]; then
  echo "==> Registering MCP profile: $PROFILE_NAME"
  command -v codex >/dev/null 2>&1 || { echo "codex command is required for MCP registration." >&2; exit 1; }
  MCP_ARGS=(--profile "$PROFILE_NAME")
  [[ -n "$FILESYSTEM_ROOT" ]] && MCP_ARGS+=(--filesystem-root "$FILESYSTEM_ROOT")
  [[ "$FORCE_MCP" -eq 1 ]] && MCP_ARGS+=(--force)
  [[ "$SKIP_PLUGINS" -eq 1 ]] && MCP_ARGS+=(--skip-plugins)
  node "$REPO_ROOT/scripts/install-mcp.mjs" "${MCP_ARGS[@]}"
fi

echo "==> Installation complete"
echo "Fully quit and reopen Codex, then start a new task."
echo "Run ./DOCTOR.command to verify the installation."
