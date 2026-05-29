# Codex brief template — stage: voice_bgm

> Template — the orchestrator fills `{LESSON_ID}` and copies this brief.

## Identity
- lesson_id: {LESSON_ID}
- stage: voice_bgm
- vendor: OpenAI (Codex / GPT-5)
- role: **Voice & BGM Agent (Gate 3)** — narration script + BGM brief

## Inputs
1. Manifest: `manim_service/pipeline/cache/{LESSON_ID}/manifest.json`
2. From manifest['artifacts']:
   - `plan` — Gate-2-verified plan.md
   - `choreo` — choreo.md (for per-phase narration intentions)
   - `tv_canonical` — verified numerical values to speak
   - `phase_timestamps` — per-phase start times (after Manim render completes)
   - `silent_mp4` — for runtime reference

## Task
Follow the voice-bgm skill's phase-timing workflow. Produce:
1. `narration_script.md` — one line of narration per phase boundary defined in
   `phase_timestamps.json`. Aligned to phase starts.
2. `audio_brief.md` — BGM track selection from STYLE_BIBLE §12 palette
   (default: NO BGM unless the choreo explicitly calls for it) + volume envelope.

Numerical values spoken in narration MUST match `tv_canonical` exactly. No
filler. No undefined jargon. Measured educational register.

Write outputs to manifest['artifacts']['narration_script'] and ['audio_brief'].

## Result format

End your run by writing ONLY this block:

    STAGE_RESULT
    stage: voice_bgm
    status: {success|failed}
    narration_path: <absolute path>
    audio_brief_path: <absolute path>
    line_count: <int>
    errors: <short description or "none">
