# Visual Review Reference

Read this only while setting up a screenshot-matching task or closing its visual evidence.

## Compact visual ledger

Use a short table or manifest; measure only details that affect the next implementation decision.

| Region | Reference observation | Implementation observation | Delta | Next correction |
|---|---|---|---|---|
| page shell |  |  |  |  |
| primary layout |  |  |  |  |
| typography |  |  |  |  |
| surfaces and borders |  |  |  |  |
| assets and icons |  |  |  |  |
| dense or repeated component |  |  |  |  |

Prioritize deltas in this order:

1. Wrong route, state, viewport, or scroll position
2. Shell and major region geometry
3. Text metrics, wrapping, and content fit
4. Colours, borders, radius, shadows, and imagery crop
5. Icon source, optical size, alignment, and micro-spacing

## Capture manifest

Store only what a later operator needs to repeat the visual check.

    # UI parity manifest

    - Reference: <user-provided path or authorized URL>
    - Reference dimensions: <width>x<height>
    - Target: <route, component, and UI state>
    - Capture viewport: <width>x<height CSS px>
    - Theme / scale / scroll position:
    - Implementation capture:
    - Focused crops:
    - Capture route or command:
    - Reviewed at:

    ## Remaining differences

    - none | <specific visible difference, reason, and acceptance owner>

## Focused-crop triggers

Capture and inspect a crop in addition to the full viewport when any of these are present:

- compact buttons, icon-only controls, badges, tabs, chips, or counters;
- toolbars, tables, repeated cards, media rows, charts, maps, or dashboards;
- text wrapping near a fixed-height boundary;
- elements that overlap, clip, use sticky positioning, or have tight spacing;
- siblings that should share a baseline, equal gap, or repeated media ratio.

## Cleanup boundary

Candidate screenshots are generated process artifacts, not proof by default. After final review, identify each exact route-and-viewport family from the manifest. Retain its reference and the latest three verified candidate captures; move only confirmed older disposable candidates to the Recycle Bin. Keep the final capture when it is required by the project handoff or delivery record.
