# QA Checklist

## Must Pass

- Figure is conceptual unless source data was supplied.
- No fabricated plots, axes, numeric values, p-values, heatmaps, microscopy, gels, spectra, or readouts.
- No invented genes, proteins, compounds, species, cell types, pathways, anatomy, or molecular structures.
- One image explains one core idea.
- Labels are short, readable, and supported by source material.
- Visual hierarchy is clear in 1-2 seconds.
- Style reads as research-paper schematic, not stock art or slide decoration.
- Background is white or transparent-looking.
- Palette is restrained and semantically meaningful.

## Failure Signals

Regenerate or edit if the image:

- looks like empirical evidence without supplied data
- implies a stronger causal or clinical claim than the source supports
- contains decorative science symbols unrelated to the source
- is too dense to read at figure-column size
- uses long paragraph labels
- has fake journal styling, logos, watermarks, or paper titles
- looks like biotech marketing art
- uses icon-tile or badge-card outcome callouts for improvement claims instead of plain text tied to the mechanism
- mixes mechanism, methods, and results into one crowded panel

## Iteration Rules

- Too data-like: remove evidence elements and use symbolic outputs.
- Too vague: add only source-supported entities and exact labels.
- Too crowded: reduce to 3-5 major elements or split into separate figures.
- Too decorative: remove unrelated DNA/cell/molecule/lab props.
- Too generic: anchor composition around the paper's actual mechanism, workflow, or comparison.

## Delivery Check

Return the image with a one-line purpose and saved asset path if saved. Keep caveats short.
