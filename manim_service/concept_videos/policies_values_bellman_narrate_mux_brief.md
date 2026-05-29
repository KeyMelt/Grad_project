# Codex Brief — policies_values_bellman — stage: narrate_mux

## Identity
- lesson_id: policies_values_bellman
- manim_class: PoliciesValuesBellmanConcept
- stage: narrate_mux
- python: /Users/ultramarine/.venvs/manim/bin/python
- project_root: /Users/ultramarine/Desktop/grad_project

## Gate context
- Gate 1 RL Expert: PASS
- Gate 2 Tech Validator: PASS
- Gate 3 Voice & BGM: PASS
- Gate 4 Transcript Writer: PASS
- Gate 5 QA: REJECTED for MISSING_NARRATION only — sole blocker is the lack of audio mux; this stage fixes that.

## Inputs (read these from disk)
- narration:   manim_service/concept_videos/policies_values_bellman_narration_script.md
- silent_mp4:  media/videos/policies_values_bellman_concept/480p15/PoliciesValuesBellmanConcept.mp4
- audio_brief: manim_service/concept_videos/policies_values_bellman_audio_brief.md

## Task

Run the narration synthesis and mux:

```bash
/Users/ultramarine/.venvs/manim/bin/python -m manim_service.audio.synthesize \
  --narration manim_service/concept_videos/policies_values_bellman_narration_script.md \
  --silent-mp4 media/videos/policies_values_bellman_concept/480p15/PoliciesValuesBellmanConcept.mp4 \
  --output    backend/media/concept_videos/policies_values_bellman_concept_narrated.mp4 \
  --lesson-id policies_values_bellman
```

After synthesis completes:
1. Confirm `policies_values_bellman_concept_narrated.mp4` exists.
2. Read `policies_values_bellman_concept_narrated.audio_report.json` — check every entry in
   `lines[].warnings` for "extends past video end". If any such warning appears,
   report it in the errors: field (do NOT silently truncate).
3. Record the narrated MP4 duration from the audio report.

## Constraints
- python: /Users/ultramarine/.venvs/manim/bin/python
- BGM: None (per audio_brief.md, STYLE_BIBLE §12 default)
- Voice: am_michael, speed 1.0, 24 kHz (Kokoro default)
- Do NOT re-render the Manim scene — use the silent MP4 as-is.

## Result format

End your run by writing ONLY this block as your final message:

    STAGE_RESULT
    stage: narrate_mux
    status: {success|failed}
    scene_py: -
    silent_mp4: media/videos/policies_values_bellman_concept/480p15/PoliciesValuesBellmanConcept.mp4
    narrated_mp4: {path or "-"}
    audio_report: {path or "-"}
    render_seconds: -
    animations: -
    errors: {short description or "none"}
