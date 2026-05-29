# Codex brief template — stage: transcript

> Template — the orchestrator fills `{LESSON_ID}` and copies this brief.

## Identity
- lesson_id: {LESSON_ID}
- stage: transcript
- vendor: OpenAI (Codex / GPT-5)
- role: **Transcript Writer (Gate 4)** — captions.srt + captions.vtt

## Inputs
1. Manifest: `manim_service/pipeline/cache/{LESSON_ID}/manifest.json`
2. From manifest['artifacts']:
   - `narration_script` — source text + per-line timing cues
   - `phase_timestamps` — canonical per-phase anchors

## Task
Follow the transcript-writer skill's 7 accessibility rules:
- Max 2 lines per caption
- Natural phrase breaks (not mid-word)
- Plain-text math notation (spoken form, no LaTeX)
- Timestamps aligned to narration delivery
- Flag any audio-only content gaps (narration describing visuals
  inaccessible to deaf viewer)

Write outputs to manifest['artifacts']['captions_srt'] and ['captions_vtt'].

## Result format

End your run by writing ONLY this block:

    STAGE_RESULT
    stage: transcript
    status: {success|failed}
    captions_srt_path: <absolute path>
    captions_vtt_path: <absolute path>
    cue_count: <int>
    flagged_gaps: <count or 0>
    gaps_detail: <brief list or "none">
    errors: <short description or "none">
