# Default operating stance

The older Python/matplotlib rules in this skill remain valid. The skill also supports R, especially `ggplot2 + patchwork + ComplexHeatmap + ggrepel + svglite/cairo_pdf + ragg`.

## Color policy

Prefer **unified method families across all panels** over maximal hue separation. For dense Nature Machine Intelligence-style figure pages, use the low-saturation `NMI pastel` family described in `references/api.md` and reserve green/red mainly for gains, drops, and other directional cues.

For ordinary scientific schematics, model architectures, workflows, and mechanism diagrams, use a **grey-first hierarchy** by default:

- Near-black charcoal for essential text and the single highest-priority result path; do not make pure black the universal stroke color.
- Dark grey for primary structure, medium grey for secondary branches, light grey for scaffolds and guides, and very pale grey for restrained fills.
- Pure black is an emphasis color, not the neutral default. If the user asks for mostly black typography, keep the typography near-black while preserving grey structural layers.
- Optionally use one muted, low-saturation accent hue for the manuscript's unique mechanism or selected route. Do not spread the accent across headings, decorative labels, and unrelated modules.
- Preserve grayscale readability. The figure must remain understandable if the optional accent is removed or printed without color.

The explicit palette requested by the user or target journal still overrides this default.

## Stance

- Start by classifying the requested figure into one of four archetypes: `quantitative grid`, `schematic-led composite`, `image plate + quant`, or `asymmetric mixed-modality figure`.
- Prefer one **hero panel** plus subordinate evidence panels over filling the canvas with equal-sized subplots.
- If the user asks for a single chart, still identify its role in the manuscript claim: discovery, mechanism, validation, comparison, robustness, or clinical/biological relevance.
- Keep the background white for plots and diagrams; switch to black only for microscopy / volume-rendering image plates.
- Prefer direct labels over legends when categories are spatially fixed or the legend would force unnecessary eye travel.
- Keep one restrained palette per figure: usually a grey neutral hierarchy plus, only when it carries meaning, one muted signal or accent family.
- Treat statistics, `n`, error-bar definitions, source-data traceability, and image-integrity notes as part of the figure, not as optional caption cleanup.
- When the user asks for broad `Nature` style rather than ML/NMI-specific style, read `references/nature-2026-observations.md` before choosing layout.
- When the user references `figures4papers` or the older `scientific-figure-making` skill, treat this skill as the successor and open `references/demos.md` for bundled Python demo scripts.

## User-facing privacy rule

Do not disclose private local paths, private filenames, chat-attachment names, internal reference filenames, template identifiers, or the provenance of private working materials in user-facing replies, generated code comments, figure legends, reports, or manuscript text. Use generic descriptions such as "the provided R template collection", "a private working draft", or "the internal figure contract". If the user provides a private plotting template collection, use it only as an internal adaptation source and do not reveal its path, filenames, or provenance. Only reveal an exact path or source file when the user explicitly asks for that audit trail.

## When to load this skill

- Python or R figures for **papers, slides, or reports** targeting Nature, Science, Cell, NeurIPS, ICLR, or similar venues.
- Requests involving **grouped bars, trend lines, heatmaps, radar plots, multi-panel grids**, or **PDF/SVG/high-DPI** output.
- Any mention of "Nature style", "publication figure", "paper figure", "SCI figure", "figures4papers", "scientific-figure-making", "R plotting template", or "high-quality scientific plot".
- Requests to improve a figure's logic, aesthetics, panel layout, figure legend, export quality, or journal-readiness.

## When NOT to load

- Plotly, Altair, Bokeh, or other interactive/web-first plotting.
- EDA-only plots without a publication target.
- Primary workflow is 3D, GIS, or non-scientific illustration tooling.
- Illustrator / Figma–first layout.
