# Audio Brief — mdp_foundations

**lesson_id:** mdp_foundations
**stage:** narrate_mux
**Date:** 2026-05-23

## Voice

- Engine: Kokoro v1.0
- Voice: `am_michael` (series default — matches rl_intro)
- Speed: 1.0
- Sample rate: 24 kHz
- Format: WAV (intermediate); Kokoro default

## BGM

None. STYLE_BIBLE §12 — this video has continuous dense equation narration across
all eight phases. No BGM track is appropriate; silence between narration lines is
the only acceptable background.

## Narration script

Path: `manim_service/concept_videos/mdp_foundations_narration_script.md`

All time cues are in [HH:MM:SS] format. The synthesiser should honour cue times
as target placements; if a clip overruns its window, shift subsequent lines forward
rather than truncating.

## Silent MP4

Path: `backend/media/concept_videos/mdp_foundations_concept.mp4`
Rendered at: 480p15 (-ql), 86 animations, ~78 s dev render time.

## Output

Narrated MP4: `backend/media/concept_videos/mdp_foundations_concept_narrated.mp4`
Audio report: `backend/media/concept_videos/mdp_foundations_concept_narrated.audio_report.json`

## Warnings to surface

Read `audio_report.json` `lines[].warnings` after synthesis. Surface any line
flagged "extends past video end" rather than silently truncating. These indicate
a narration density mismatch that requires Script Writer (not truncation).

## Phase timing reference (from narration_script.md)

| Phase | Start | End |
|---|---|---|
| (a) MDP framework | 00:00:00 | 00:04:10 |
| (b) Rewards and returns | 00:04:10 | 00:08:50 |
| (c) Transition probability | 00:08:50 | 00:13:20 |
| (d) Policies | 00:13:20 | 00:16:50 |
| (e) Value functions | 00:16:50 | 00:21:00 |
| Recap card | 00:21:00 | 00:22:20 |
| (f) Bellman equation | 00:22:20 | 00:27:00 |
| Closing | 00:27:00 | 00:28:20 |
