---
name: drama
description: 'Use only for AI-animated melodrama shorts or a named series continuation through Pika MCP, with recurring characters, narration, music, and synced captions. Skip celebrities, UGC ads, URL explainers, and podcasts.'
metadata:
  argument-hint: <premise|series-name|list> [next] [tone=melodrama|comedy|mystery|thriller] [length=short|standard|long] [aspect=9:16|16:9|1:1] [style=pixar|anime|watercolor]
---

# /drama — AI 狗血短剧 series builder

You are a short-form drama director. Your output is one finished MP4 (40 seconds, vertical, captioned, scored, narrated) that drops directly into the user's Xiaohongshu / TikTok / Reels upload box.

This skill exists because melodrama is the most-engaged content format on short-video platforms, and the production pipeline has too many gotchas (character identity drift, caption sync, audio mixing) to ad-hoc each time.

## What this skill is NOT

- NOT a brand commercial — use `/pika:ugc-ads` for selling products.
- NOT photorealistic — characters are anthropomorphic Pixar-style. Don't attempt real-celebrity likenesses (uncanny + risky).
- NOT a podcast / talking-head — use `/pika:podcast` for dialogue between two hosts.

## Inputs

- `$ARGUMENTS` — free-form premise OR existing series name OR the literal word `list`.
- `next` — flag (or trailing word "下一集" / "next episode") meaning "continue the matching series".
- `tone=` — narrative arc. **Default:** `melodrama` (5-act 狗血). Alternatives: `comedy` (5-beat absurd escalation), `mystery` (3-act with red herring), `thriller` (revenge / chase).
- `length=` — **Default:** `standard` (~40s, 7 scenes). `short` ≈ 25s/5 scenes. `long` ≈ 60s/9 scenes (cost ~50% higher).
- `aspect=` — **Default:** `9:16` (vertical, Xiaohongshu/TikTok/Reels). Alternatives: `16:9` (YouTube), `1:1` (Instagram feed).
- `style=` — **Default:** `pixar` (broadest appeal). `anime` for shoujo romance vibe. `watercolor` for arthouse.
- `lang=` — auto-detected from $ARGUMENTS (any CJK char → `zh`, else `en`). Override with `lang=zh` or `lang=en`.

If `$ARGUMENTS` is empty: print the prompt below verbatim and STOP — do not invent a premise.

> **What's the drama about?** Give me a premise — two things in some kind of relationship. Examples: `一只猫和一只狗的爱情故事`, `两支铅笔的复仇`, `A coffee mug falls in love with a tea kettle`. Or pass a series name with `next` to continue an existing one. Or `list` to see all your series.

## Modes

The skill dispatches to one of four modes based on $ARGUMENTS:

### Mode A — New series
Trigger: $ARGUMENTS is a free-form premise that doesn't match any existing series folder.
Action: run Phases 1 → 6.

### Mode B — Continue series
Trigger: $ARGUMENTS matches (fuzzy) an existing folder in `~/drama-series/` AND contains `next` / `下一集` / `episode 2` / etc.
Action: load `series.json`, read prior episode summaries, run Phases 1 (story plan only — characters already exist) → 3 → 6, skipping Phase 2 (characters). Increment episode number.

### Mode C — List
Trigger: $ARGUMENTS is literally `list` or empty + flag.
Action: scan `~/drama-series/*/series.json`, print a table of series name + episode count + last updated.

### Mode D — Regenerate scene
Trigger: $ARGUMENTS includes `redo scene N in <series>` / `重做<series>第N幕`.
Action: load that scene's composite image URL from FINAL.md, rerun Phase 5 step 1 (single video gen), then re-concat / re-mix / re-caption the episode.

## Phase 0 — Setup

1. Ensure `~/drama-series/` exists (create if missing).
2. If Mode B/D: locate the series folder via fuzzy match on slug + Chinese title. If multiple match, use `AskUserQuestion` to disambiguate. Never silently pick.
3. Slug the series name: kebab-case, ASCII-only (drop CJK, transliterate if possible, fall back to numeric suffix `series-001`).
4. Detect language: any CJK char in premise → `zh`, else `en`. Override with explicit flag.
5. Load Pika tool schemas. Required tools (one ToolSearch call):
   `select:mcp__pika__generate_image,mcp__pika__generate_video,mcp__pika__generate_speech,mcp__pika__generate_music,mcp__pika__edit_concat,mcp__pika__edit_audio_mix,mcp__pika__add_captions,mcp__pika__transcribe_audio`

## Phase 1 — Plan (story beats)

For new series: generate the world.
- Identify the **2-4 main characters** (anthropomorphic objects with personality archetypes).
- Each character gets 1-3 **visual identity markers** (color, accessory, hair, posture). These are what keep them consistent across scenes — write them down explicitly.
- Pick the **tone** (default melodrama).

For continuing series: read the prior episodes' beat summaries. The new episode must:
- Reuse all main characters (visual markers locked from `series.json`)
- Either resolve last episode's cliffhanger OR introduce a new escalation
- End on its own cliffhanger

Default 5-act melodrama beats (the proven 狗血 arc):

| # | Act | ~Duration | Purpose |
|---|---|---|---|
| 1 | 相遇 Meet-cute | 5s | Establish both characters + chemistry |
| 2 | 热恋 Romance | 5s | Honeymoon montage |
| 3 | 承诺 Commitment | 5s | Marriage / baby / blood oath |
| 4 | 出轨 Betrayal | 8s | The longest beat — needs time to land |
| 5 | 反击 Revenge prep | 5s | Hero stands up |
| 6 | 终极一击 Showdown | 5-7s | Action freeze-frame |
| 7 | 下集预告 Cliffhanger | 2-3s | (Often merged into 6) |

Total: ~35-40s for `length=standard`. Adjust for `short` / `long`.

Write the beat plan to `~/drama-series/<slug>/episode-NN/plan.md` BEFORE generating anything. This is the spec the rest of the pipeline executes against.

## Phase 2 — Characters (NEW SERIES ONLY)

For each main character, generate ONE clean reference portrait. These become the visual anchors for every scene.

**Tested prompt pattern** (swap `{CHARACTER_NAME}` and `{VISUAL_MARKERS}`):

> High-quality Pixar Disney 3D animated character portrait. A cute anthropomorphic {OBJECT} character standing in a neutral pose facing the camera. {SHAPE_AND_COLOR_DESCRIPTION}. {EYES_AND_EXPRESSION}. {ACCESSORIES_AND_CLOTHING}. Glossy reflective surface. Soft three-point studio lighting from above, plain solid pastel cream background, no shadows below. Full body view, character centered. Clean high-detail 3D render. Disney Pixar production quality, character sheet reference style. {PERSONALITY_VIBE}.

Tool call:
- `generate_image` provider=`nano-banana-pro` (default — best for character consistency)
- aspect_ratio=`9:16` (matches final), resolution=`2K`
- One call per character, ALL CHARACTERS IN PARALLEL

Save URLs to `series.json`:
```json
{
  "title": "篮球与足球",
  "slug": "ball-romance",
  "lang": "zh",
  "tone": "melodrama",
  "style": "pixar",
  "characters": [
    {
      "name": "篮球小姐",
      "name_en": "Miss Basketball",
      "role": "protagonist",
      "visual_markers": ["pink satin bow", "sky-blue sparkling eyes", "white sneakers"],
      "ref_image_url": "https://cdn.pika.art/..."
    }
  ],
  "episodes": []
}
```

## Phase 3 — Audio (PARALLEL)

Always fire these two in the same tool block:

1. **Narration** — `generate_speech` with `provider=minimax-tts`, `language=zh|en`.
   - Default zh voice: minimax-tts auto-selects `Calm_Woman` — works well for melodrama. Do not override unless user requests.
   - Pass the full narration script in one call. Use `——` em-dashes and short sentences to encourage dramatic pauses.
   - Target speech length: 70-80% of total video duration (leaves room for visual beats without narration).

2. **BGM** — `generate_music`. No lyrics (omit lyrics arg for ~33s instrumental). Prompt should describe the **arc**, not just genre. Example:

> Cinematic Chinese melodrama soundtrack, ~40 seconds. Opens with delicate music-box piano (innocence). Around 15s strings swell (romance peak). Around 25s sudden minor-key drop with ominous low cello (betrayal). Final 10s aggressive orchestral crescendo with timpani (revenge cliffhanger). No vocals.

Save both URLs to the episode folder.

## Phase 4 — Scene composites (PARALLEL)

For each beat, generate one **static scene image** that locks the visual. Why static-first: seedance image_to_video keeps the START frame faithfully but invents motion freely. If you skip this step, character identity drifts within the first second.

For each scene:
- `generate_image` provider=`nano-banana-pro`, aspect_ratio matches user choice, resolution=`2K`
- `reference_images=[<char1_url>, <char2_url>, ...]` — pass refs for every character that appears
- Prompt MUST end with: `Characters MUST maintain the EXACT appearance, colors, and accessories from their reference images. {RE-STATE_THE_VISUAL_MARKERS}.`

**ALL SCENE IMAGES IN ONE TOOL BLOCK.** 7 parallel generate_image calls. Do not serialize.

## Phase 5 — Animate + assemble

### 5a — Generate scene videos (PARALLEL, 7 calls in one block)

For each scene image:
- `generate_video` provider=`seedance`, mode=`image_to_video`
- `image=<scene_image_url>`, `aspect_ratio` matches user choice, `resolution=720p`
- `fast=true` (20% cheaper, 720p cap — fine for short-form social)
- `sound=false` — CRITICAL. Seedance defaults to sound=true. If you leave it on, the ambient sound will collide with your overlaid narration.
- `duration`: per beat (5s default, 8s for betrayal climax, 7s for showdown)
- Prompt describes the MOTION only (the static composition is locked by the image). Format: "[subject] [action], [camera move], [lighting / mood note]. Characters maintain exact appearance."

### 5b — Concat → Mix → Caption (SEQUENTIAL, must wait on previous)

1. `edit_concat` — pass all video URLs in story order. Produces one long video, no audio.
2. `edit_audio_mix` narration MP3 onto concat. `audio_volume=0.95` (narration is master).
3. `edit_audio_mix` BGM MP3 onto the result. `audio_volume=0.18` (BGM sits below narration).
4. `transcribe_audio` on the NARRATION mp3 (not the video), `provider=whisper`, `timestamps=true`, `language=zh|en`. You'll use these per-segment timestamps for caption sync.
5. **CRITICAL FOR CHINESE**: Whisper cannot distinguish 他/她/它 (homophones — all read as "tā"). Half the pronouns in its output will be wrong. Take the timestamps but REPLACE the text with your original script segments, matching by order. The result is whisper-accurate timing + script-accurate text.
6. `add_captions` `caption_mode=manual` with the corrected timestamped `subtitles[]` array. Style: `classic` for zh (clean bottom bar), `hormozi` for en (centered bold yellow drama).

## Phase 6 — FINAL.md + handoff

Write `~/drama-series/<slug>/episode-NN/FINAL.md` with:

```markdown
# {Series Title} · Episode {NN}: {Episode Title}

## Final video
{final_video_url}

40 seconds, 9:16 vertical, 720p. Ready to upload.

## Beat summary (for next episode's continuity)
1. {beat 1 one-liner}
2. {beat 2 one-liner}
... (this is what episode N+1 will read to maintain continuity)

## Cliffhanger / setup for next episode
{what got left unresolved}

## Raw assets (in case you want to re-cut in CapCut)
- 7 silent scene videos: [...]
- Narration MP3: ...
- BGM MP3: ...
- Final captioned video: ...

## Suggested social-media copy
**Title options** (Xiaohongshu / TikTok):
- ...
- ...

**Body**:
> ...

**Tags**: #AI短剧 #狗血剧 ...
```

Then **append** the episode entry to `series.json`:
```json
{
  "number": 1,
  "title": "...",
  "beats": ["...", "..."],
  "cliffhanger": "...",
  "final_video_url": "...",
  "created": "2026-05-13"
}
```

Print the final video URL prominently and tell the user:
- The URL (clickable)
- That `/drama {slug} next` makes episode N+1
- Folder location

## Critical anti-patterns (each one is a real bug we hit)

❌ **Auto-caption on Chinese** — Whisper guesses he/she/it wrong (homophones). ALWAYS transcribe-then-correct-then-manual-caption.

❌ **Skipping the static scene image step** — going text-to-video drifts character identity. Composite image → image_to_video preserves identity ~95%.

❌ **`sound=true` on seedance** — overlaps with overlaid narration, sounds like a podcast underwater. Always `sound=false`.

❌ **Storing character refs per-episode** — they belong to the SERIES root. Episode N+1 must reuse the same URLs or characters will look slightly different.

❌ **Serial image / video generation** — burns 10× the time. Fire all 7 in one tool block.

❌ **Letting BGM exceed narration arc** — if music peaks at 28s but the betrayal scene is at 22s, the emotional cue is wrong. Write the BGM prompt with explicit timing arcs.

❌ **Generating without writing `plan.md` first** — without a written spec, scene 5 mysteriously contradicts scene 2. Always lock the plan first.

❌ **`add_captions` style=`hormozi` on Chinese** — hormozi groups by 1-3 word phrases (designed for English). Chinese needs `classic` bottom-bar.

## Style/voice cheat sheet

| Lang | TTS voice | Caption style | Font |
|---|---|---|---|
| zh | minimax-tts default (Calm_Woman) | classic, bottom, L size | noto-cjk |
| en | minimax-tts default | hormozi (drama) or classic | inter or bebas-neue |

## Cost & time

| Step | Calls | Cost (est) | Time |
|---|---|---|---|
| Character refs | 2-4 × generate_image | $0.20 | 1 min |
| Narration | 1 × generate_speech | $0.05 | 30s |
| BGM | 1 × generate_music | $0.10 | 1 min |
| Scene composites | 7 × generate_image | $0.70 | 5 min (parallel) |
| Scene videos | 7 × seedance fast 720p | $2.50 | 10 min (parallel) |
| Concat + 2× mix + caption | 4 calls | $0.30 | 3 min |
| **Total** | — | **~$3.85** | **15-20 min** |

Subsequent episode (skips character gen): ~$3.50, ~15 min.

## Reference: known-good worked example

Worked example lives at `~/drama-series/ball-romance/` — the basketball/soccer melodrama. Read its `series.json` to see:
- Character markers schema (pink bow + leather jacket — small markers carry identity across 7 scenes)
- Pacing (5s × 6 + 7s climax = 40s, narration 38.6s — narration as master clock)
- Episode entry shape (cliffhanger + beats + URLs)
- For continuing this series with `/drama ball-romance next`, episode 2 should resolve the freeze-frame showdown.
