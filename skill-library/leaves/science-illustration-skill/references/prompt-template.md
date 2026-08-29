# Prompt Template

Use one prompt per image. Replace placeholders from the user's source material.

```text
Generate one clean scientific illustration suitable for a research paper, preprint, poster, or graphical abstract.

Purpose:
{mechanism schematic / experimental workflow / study design / assay pipeline / model architecture / comparison / graphical abstract}

Scientific subject:
{topic and field}

Core message:
{one sentence, only supported by the source material}

Layout:
{single panel / two panels / three panels}. {Describe the spatial arrangement and flow.}

Required visual elements:
{element 1} / {element 2} / {element 3} / {element 4}

Labels to include exactly:
{short label 1} / {short label 2} / {short label 3} / {short label 4}

Style:
Clean white background, polished research-review-style scientific schematic, soft muted base colors, thin precise vector-like linework, restrained accent colors, simplified recognizable components, clear panels or insets when useful, arrows/connectors/callouts where needed, legible short labels in a Helvetica/Arial-like sans-serif placed near the relevant elements, balanced whitespace, no decorative clutter.

Scientific integrity constraints:
Do not include fabricated data, charts, axes, p-values, heatmaps, microscopy-like panels, gel bands, spectra, molecular structures, instrument readouts, or quantitative evidence. Show only conceptual relationships and details supported by the source. Use generic symbolic readouts where exact data is not supplied.

Avoid:
Stock science art, glossy 3D render, sci-fi UI, dense textbook page, pitch-deck style, icon-tile outcome badges, chart-like improvement icons, long title text, logos, watermarks, decorative unrelated domain motifs.
```

## Edit Prompts

Remove fake evidence:

```text
Edit the image to remove all data-like or empirical evidence elements, including charts, axes, microscopy-like panels, gel bands, spectra, numeric values, or instrument readouts. Preserve the conceptual schematic, layout, labels, and clean publication style. Replace removed evidence with generic symbolic outputs only if needed.
```

Simplify labels:

```text
Edit the image to reduce label density. Keep only the essential short labels provided by the source. Preserve the scientific meaning, layout, and clean white schematic style.
```

Make it more publication-like:

```text
Regenerate the same scientific concept as a restrained research-paper schematic: clean white background, precise linework, sparse labels, balanced whitespace, no stock-art gloss, no sci-fi UI, and no fabricated empirical evidence.
```
