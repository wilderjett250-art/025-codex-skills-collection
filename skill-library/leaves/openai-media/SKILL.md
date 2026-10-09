---
name: openai-media
description: Use when the user explicitly requests OpenAI Sora video generation or editing, OpenAI text-to-speech, or transcription with the canonical local CLIs and required API access.
---

# OpenAI Media

Read exactly one canonical guide unless the requested workflow crosses media types:

- Sora video generation, editing, extension, polling, download, or batch work: `canonical/sora/SKILL.md`
- Text-to-speech, narration, accessibility reads, or voiceover: `canonical/speech/SKILL.md`
- Audio or video transcription with optional diarization: `canonical/transcribe/SKILL.md`

Resolve scripts relative to the selected canonical directory. Verify API credentials and service access before any live request, and never claim a generated or transcribed artifact exists without checking it.
