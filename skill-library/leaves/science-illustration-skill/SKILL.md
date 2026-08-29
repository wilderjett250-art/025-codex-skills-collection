---
name: science-illustration-skill
description: 'Create scientific paper figures, graphical abstracts, mechanism or workflow schematics, study designs, or model diagrams. Never fabricate data, plots, microscopy, gels, spectra, molecular structures, or measurements.'
---

# Science Illustration Skill

## Core Purpose

Design publication-style conceptual scientific illustrations: mechanisms, workflows, assay pipelines, study designs, model schematics, comparisons, and graphical abstracts. Make clean schematic figures, not decorative science art.

Scientific integrity is the first constraint. Do not fabricate evidence.

## Mode Interaction

When this skill is active, follow this skill's scientific integrity, visual planning, generation, QA, and delivery rules even if another global or conversational style mode is active. Do not let terse, minimal, or simplification modes override figure quality, source fidelity, QA iteration, or the required output style.

## Read As Needed

- `references/scientific-integrity.md`: read before generating data-like, empirical, molecular, microscopy, gel, spectrum, clinical, or quantitative visuals.
- `references/style-dna.md`: use for visual style, palette, label, and layout rules.
- `references/figure-types.md`: use to choose the smallest figure structure that fits the source material.
- `references/prompt-template.md`: use for single-image generation and edit prompts.
- `references/qa-checklist.md`: use for post-generation checks and iteration rules.

## Workflow

### 1. Understand The Source

Read the user's abstract, methods paragraph, figure caption, notes, screenshot, dataset description, or pasted source material.

Extract only:

- topic and research field
- central mechanism, workflow, comparison, or study structure
- required entities and exact labels
- unsupported details that must stay generic
- whether the request is conceptual or empirical

If the user asks for empirical-looking evidence without source data, do not generate it. Offer a conceptual schematic instead.

### 2. Plan The Figure

For planning requests, return a short figure strategy or shot list:

- figure type
- one-sentence message
- layout
- required visual elements
- exact labels
- details that must not be inferred

Prefer 1-3 figures. Split mechanisms, methods, and summary visuals only when one figure would become crowded.

### 3. Generate One Figure At A Time

Use `image_gen` directly when the user asks to generate. Do not wait for confirmation unless the request would fabricate scientific evidence.

Each generation prompt must include:

- publication-style scientific schematic
- clean white or transparent-looking background
- restrained palette
- short readable labels
- one core idea per image
- exact labels from the source
- a clear ban on fabricated data or evidence

Do not combine unrelated panels just because space is available.

### 4. QA And Iterate

Check `references/qa-checklist.md`. Regenerate or edit if the image:

- implies unsupported empirical evidence
- contains fake charts, axes, microscopy, gel bands, spectra, or readouts
- invents molecular or anatomical detail
- has unreadable or excessive labels
- looks like stock art, sci-fi UI, a pitch deck, or a dense textbook page
- mixes too many ideas in one figure

### 5. Save Assets

When working inside a project, save final images under one of:

```text
assets/science-illustrations/
assets/<paper-slug>-figures/
```

Use numbered filenames:

```text
01-mechanism-schematic.png
02-assay-workflow.png
03-graphical-abstract.png
```

Do not overwrite existing assets unless the user explicitly asks.

## Output Style

- Planning: concise shot list.
- Generation: generated image plus purpose and save path.
- Caveats: short, only when scientific uncertainty affects the figure.
