# Strict Atomic Skill Routing Map

Every domain Skill has one canonical home. Classification is a tree, not a many-parent graph:

`domain/<layer-1 domain>/<layer-2 discipline>/<family>/<skill>`

Control Skills use a separate root:

`control/execution-governance/<discipline>/<family>/<skill>`

Platforms, phases, project types, risks, and aliases are retrieval facets only. They never create a second parent.

Start with the full-prompt route. If one prompt asks for several actions, create one work unit per atomic capability. Each work unit gets one owner; access and claim gates are attached separately.

| Layer-1 domain | Includes these layer-2 disciplines | Typical work |
| --- | --- | --- |
| `computing-digital` | project-flow, code-engineering, frontend-ui, backend-api, data-database, devops-runtime, browser-desktop, ai-ml, mobile-interactive, security-quality | software, cloud, data, AI, browser, mobile, cybersecurity |
| `engineering-hardware` | hardware-iot | embedded devices, firmware, CAD, physical equipment |
| `documents-media` | documents-media | Word/PDF/slides, image, audio, video production and QA |
| `research-education` | research-knowledge | literature, citations, experiments, academic production |
| `business-operations` | business-ops | marketing, sales, finance, inventory, logistics, productivity |

`execution-governance` is not a subject domain. It holds routing, project classification, large-project decomposition, handoff, local experience, and evidence gates.

Example: “修复 FastAPI 并部署到腾讯云” stays inside layer 1 `computing-digital`, but becomes two work units:

- `backend-api/framework-services/fastapi-patterns`
- `devops-runtime/deployment-runtime/deployment-patterns`

`腾讯云` is a platform facet. If the existing Edge session is required, `external-browser` is an access Skill. Acceptance is a control gate. None gives either capability Skill a second domain parent.

The catalog keeps names, descriptions, aliases, project types, phases, platforms, and risk tags for recall. Only `canonicalPath` determines taxonomy membership.
