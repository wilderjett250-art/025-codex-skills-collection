# CosKit + Codex Imagegen Workflow

This project intentionally does not call CosKit's Gemini/OpenAI image APIs.
CosKit is used only as a source of retouching workflow structure and prompt
templates. Image reading, visual judgement, and final image creation must be
handled by Codex's own imagegen capability in the active conversation.

## Workflow Boundary

Local script responsibilities:

- Scan an input folder.
- Score and select candidate images.
- Create the parent `output/` folder.
- Copy selected originals into `output/selected_originals/`.
- Write `score_report.csv`, `manifest.json`, `imagegen_tasks.json`, and `imagegen_instructions.md`.

Codex imagegen responsibilities:

- Inspect each selected image visually.
- Apply the CosKit-inspired portrait retouch prompt.
- Produce the final edited image.
- Place or save the final image in `output/edited/` when the environment exposes
  a downloadable file path for the generated result.

Finalization responsibilities:

- Codex generated images are normally saved under `~/.codex/generated_images/`.
- Use `scripts/finalize_imagegen_outputs.py` to convert/copy generated images into
  the task's expected `output/edited/*.jpg` paths.
- Pass generated image paths in the same order as `imagegen_tasks.json`.

## Recommended Imagegen Prompt

Use this prompt for natural female portrait beautification:

```text
你是一位专业的人像摄影后期修图师。请基于原图进行自然高级的人像美化，保持人物身份、五官、发型、服装、姿态、背景和构图不变，不要重绘成另一个人。

修图目标：
- 肤质自然干净：淡化痘印、斑点、毛孔和暗沉，但保留真实皮肤纹理，避免塑料感。
- 美白提亮：均匀提亮面部和可见皮肤，让肤色更通透，但不能死白。
- 光线优化：压住过曝高光，提亮面部阴影，保留立体光影。
- 色彩风格：清透、干净、温柔，适合女生写真；天空和背景颜色更通透，花草色彩更鲜明但不过饱和。
- 细节增强：眼神更清晰，头发和服装边缘自然，整体锐度适中。

禁止：
- 不要改变脸型到不像本人。
- 不要改变衣服、背景、姿势、画面比例。
- 不要添加文字、水印、边框或多余装饰。
- 不要过度磨皮、不要网红夸张滤镜。

输出：只返回修好后的图片。
```

## CosKit Skill Mapping

The prompt above condenses these CosKit skill concepts:

- `tone_adjust`: exposure, highlights, shadows, contrast.
- `color_style`: white balance, color grading, clean portrait style.
- `detail_enhance`: controlled sharpening and noise cleanup.
- `skin_smooth`: blemish and pore cleanup while preserving texture.
- `skin_whiten`: natural brightening and translucent skin tone.
- `face_adjust`: only very subtle face optimization, preserving identity.

## Important Limitation

Codex imagegen is not a local Python package. Do not call it from
`photo_cull_retouch.py`. A Codex agent must invoke imagegen from the
conversation after the local selection step. The local script should only create
selection results and prompt tasks, then optionally finalize generated files.
