---
name: portrait-retouch-qc
description: Use when retouching portrait, cosplay, model, or commercial beauty photos where face, eyes, skin tone, background cleanup, and final before/after quality control matter.
metadata:
  short-description: Portrait retouching and QC workflow
---

# Portrait Retouch QC

Use this skill for portrait/photo retouching work where the result must look commercially usable, not like a one-click filter.

## Workflow

1. Preserve originals. Never overwrite source images.
2. Start failed or questionable revisions from the original, not from a damaged retouched export.
3. Judge each image by subject size:
   - Close-up: skin tone, eyes, lips, hair detail, blemishes, background distractions.
   - Half-body: face and eyes first, then costume texture and exposure balance.
   - Full-body or distant face: do not invent eye detail; apply conservative local contrast and verify the enlarged face crop.
4. Use restrained local edits:
   - Dodge and burn style light/dark balancing for face shape and eye area.
   - Eye ROI sharpening only on iris/lash edges; avoid darkening eye whites or eyelids.
   - Keep skin texture. Avoid global blur, heavy denoise, waxy skin, or upscaling.
   - Clean distracting wall tape, dust, or obvious background marks when it can be repaired without visible smears.
5. Validate before final:
   - Full image review for composition, color, highlight clipping, background distractions.
   - Enlarged face/eye crop review for every image with a visible face.
   - Compare dimensions against originals unless an intentional crop is documented.
   - Check that face/eye sharpness did not drop.

## Failure Rules

- If eyes become black patches, gray smears, or lose catchlights, reject and redo from the original.
- If a full-frame sharpness metric improves but the eye crop looks worse, reject.
- If skin becomes plastic or lace/costume detail melts, reject.
- Do not call a batch output "精修" unless the important images were inspected at face/eye crop level.
