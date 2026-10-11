# Third-party notices

The root installer, MCP catalog, custom active Skills, and packaging files in this repository are covered by the repository license unless a file states otherwise.

The on-demand library aggregates Skills and supporting assets from multiple upstream sources. Any license, copyright notice, attribution, or origin metadata shipped inside an individual Skill directory remains authoritative for that directory. Inclusion here does not relicense third-party material under the root license.

Plugin-provided and Codex system Skills are not vendored from runtime caches. `presets/plugins.json` records official plugin identifiers so a compatible Codex installation can obtain them from their original marketplace or runtime.

This repository is public. Review source and redistribution terms before adding or updating each imported Skill; pinned source records are in `skill-library/sources-lock.json` where available. Do not assume the root MIT license overrides a vendored directory's license.

`skill-library/leaves/answer-me-with-html/scripts/am.mjs` is an unmodified bundled CLI from QingYunA/answer-me-with-html at revision `533c39fd47d814a6bee3d9c1df388345f4e4c858` (version 0.5.0). Its MIT license is retained in that directory; the bundle retains dependency license notices. The local Skill and offline wrapper are adaptations, not upstream claims or a hosted service.

Windows-MCP snapshot/observation ideas were reviewed at revision `b74c507d9e709223a0904cf08019edf55f2a75bb` and described in local route guidance. No Windows-MCP program code or server runtime is redistributed here.
