# Build and release boundaries

Read the project configuration and actual DevTools/CLI output before naming a release state.

| State | Minimum evidence |
| --- | --- |
| local implementation | source/config change exists in the confirmed root |
| static or build validated | focused checks or DevTools compile completed |
| development version uploaded | upload command/UI returned the exact version and AppID |
| experience version selected | the intended uploaded version is selected in the public platform |
| device accepted | the intended account/device executes the original path successfully |

An upload is not automatically an experience release. Compilation or source inspection does not prove a click, route, request, login, or device flow. Preserve version identifiers in the project handoff without copying secrets.
