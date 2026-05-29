# Codex Brief — mdp_foundations — stage: narrate_mux

## Identity
- lesson_id: mdp_foundations
- manim_class: MdpFoundationsScene
- stage: narrate_mux
- python: /Users/ultramarine/.venvs/manim/bin/python
- project_root: /Users/ultramarine/Desktop/grad_project

## Gate context
- Gate 1 RL Expert: PASS
- Gate 2 Tech Validator: PASS (state-6 RIGHT successors confirmed {7,2,10} each 1/3)
- Gate 3 Voice & BGM: PASS

## Inputs (read these from disk)
- narration:   manim_service/concept_videos/mdp_foundations_narration_script.md
- silent_mp4:  backend/media/concept_videos/mdp_foundations_concept.mp4
- audio_brief: manim_service/concept_videos/mdp_foundations_audio_brief.md

## Task

Run the narration synthesis and mux:

```bash
/Users/ultramarine/.venvs/manim/bin/python -m manim_service.audio.synthesize \
  --narration manim_service/concept_videos/mdp_foundations_narration_script.md \
  --silent-mp4 backend/media/concept_videos/mdp_foundations_concept.mp4 \
  --output    backend/media/concept_videos/mdp_foundations_concept_narrated.mp4 \
  --lesson-id mdp_foundations
```

After synthesis completes:
1. Confirm `mdp_foundations_concept_narrated.mp4` exists.
2. Read `mdp_foundations_concept_narrated.audio_report.json` — check every entry in
   `lines[].warnings` for "extends past video end". If any such warning appears,
   report it in the errors: field (do NOT silently truncate).
3. Record the narrated MP4 duration from the audio report.

## Constraints
- python: /Users/ultramarine/.venvs/manim/bin/python
- BGM: None (as specified in audio_brief.md — no BGM track)
- Voice: am_michael, speed 1.0, 24 kHz (Kokoro default)
- Do NOT re-render the Manim scene — use the silent MP4 as-is.

## Result format

End your run by writing ONLY this block as your final message:

    STAGE_RESULT
    stage: narrate_mux
    status: {success|failed}
    scene_py: -
    silent_mp4: backend/media/concept_videos/mdp_foundations_concept.mp4
    narrated_mp4: {path or "-"}
    audio_report: {path or "-"}
    render_seconds: -
    animations: -
    errors: {short description or "none"}
