# Codex brief template — stage: continuity

> Template — the orchestrator fills `policies_values_bellman` and copies this brief.

## Identity
- lesson_id: policies_values_bellman
- stage: continuity
- vendor: OpenAI (Codex / GPT-5; multimodal — uses image inputs)
- role: **Series Continuity (Gate 6)** — cross-series consistency vs prior approved videos

## Inputs
1. Manifest: `manim_service/pipeline/cache/policies_values_bellman/manifest.json`
2. From manifest['artifacts']:
   - `narrated_mp4` — this lesson's rendered narrated MP4
   - `scene` — this lesson's scene.py source
   - `narration_script` — this lesson's narration
   - `style_bible` — palette + conventions reference
   - `session_log` — read to identify prior approved videos in the library

## Task — VISUAL CHECK REQUIRED

This gate previously failed by reading only text. You MUST extract frames
and visually compare. Steps:

1. Read SESSION_LOG.md, identify the IMMEDIATE PREDECESSOR in the series
   (last `PRODUCER APPROVAL` entry whose lesson_id ≠ this one). Note its
   narrated MP4 path.

2. Run `frame_selector` for BOTH videos:
   ```
   /Users/ultramarine/.venvs/manim/bin/python -m manim_service.pipeline.frame_selector \
     --lesson-id policies_values_bellman \
     --phase-timestamps <this lesson's phase_timestamps.json> \
     --choreo <this lesson's choreo.md> \
     --spot-check 4
   ```
   Repeat for the predecessor.

3. Use Bash + ffmpeg to extract each frame. For each, observe and write:
   - Color palette match (this video uses the same 10 STYLE_BIBLE colors as predecessor)
   - Font sizes consistent
   - Panel anchors consistent (same place_*_panel methods)
   - Recap card style consistent if this video opens with a recap
   - Notation conventions consistent (v_π, q_π, γ, π(a|s), etc.)

4. Read the scene.py and narration_script.md for terminology checks (no banned terms per STYLE_BIBLE §11).

## Result format

End your run by writing ONLY this block:

    STAGE_RESULT
    stage: continuity
    status: {success|failed}
    verdict: CONSISTENT|INCONSISTENT
    review_path: <absolute path to continuity_review.md including frames_compared list>
    frames_compared_count: <int — must be ≥ 8 (4 this video + 4 predecessor)>
    conflicts: <count or 0>
    errors: <short description or "none">

The review_path file MUST contain a `frames_compared:` block listing every
extracted PNG path and a one-sentence visual diff. Absent block = void verdict.
