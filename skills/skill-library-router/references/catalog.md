# Catalog Location

The searchable catalog is generated locally at `~/.codex/skill-library/catalog.json`.

1. pass the full request to `~/.codex/skill-library/scripts/route-task.ps1`;
2. use [domain-routing.md](domain-routing.md) and `find-skills.ps1` only for a manual domain/family drill-down;
3. inspect the returned match reasons, then read only the selected atomic Skill and its required references.

`routing-profile.json` adds Chinese aliases and project/phase/platform/risk metadata without copying those instructions into the prompt. This replaces the static legacy table so active and cold custom Skills share one source of truth. Runtime plugin Skills remain discoverable through Codex itself and should not be duplicated here. Cold modules may contain historical runtime-specific instructions and still require Windows/Codex adaptation and verification.
