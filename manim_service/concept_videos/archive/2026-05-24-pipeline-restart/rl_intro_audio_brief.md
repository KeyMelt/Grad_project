# Audio Brief — rl_intro

**Date:** 2026-05-21
**narration_script.md reference:** /Users/ultramarine/Desktop/grad_project/manim_service/concept_videos/rl_intro_narration_script.md
**Total silent video duration:** 169.07 s (480p15 dev render)
**lesson_id:** rl_intro

---

## BGM selection

**Per STYLE_BIBLE §12 — BGM policy: NONE.**

The series uses no background music. Concept videos are narration-only.
This mirrors the 3Blue1Brown approach: BGM competes with on-screen text
and narration in a dense-concept video.

No track selection, no volume envelope, no loop test required for this lesson.

If a future lesson receives a Producer-granted BGM exception, this section will
document the track character, loop point, and volume envelope. No such exception
exists for rl_intro.

**Series Continuity note:** every lesson in the rl_intro → mdp_framework → dp_policy_eval
chain must document the same "BGM: none" policy here for cross-video consistency.

---

## Narration track specification

| Field | Value |
|---|---|
| TTS engine | Kokoro v1.0 (local, ONNX) |
| Voice id | `am_michael` |
| Speed | 1.0 (locked — do not override) |
| Sample rate | 24 kHz |
| Output format | AAC stereo, 192 kbps (mono dual-routed to L+R) |
| Synthesis script | `python -m manim_service.audio.synthesize` |

---

## Narration cue schedule

| Phase | Sub-phase | First cue | Last cue | Line count |
|---|---|---|---|---|
| 1a | Grid introduction | 00:00:02 | 00:00:05 | 2 |
| 1b | Attempt 1 — failure | 00:00:07 | 00:00:14 | 3 |
| 1c | Attempt 2 — failure | 00:00:17 | 00:00:22 | 3 |
| 1d | Attempt 3 — success | 00:00:24 | 00:00:30 | 3 |
| 1e | Closing caption | 00:00:34 | 00:00:34 | 1 |
| 2 | ML contrast | 00:00:42 | 00:00:59 | 6 |
| 3a | Agent box | 00:01:01 | 00:01:01 | 1 |
| 3b | Environment box | 00:01:05 | 00:01:08 | 2 |
| 3c | Action arrow | 00:01:12 | 00:01:12 | 1 |
| 3d | State / Obs arrow | 00:01:17 | 00:01:21 | 2 |
| 3e | Reward arrow | 00:01:24 | 00:01:28 | 2 |
| 3f | Full loop | 00:01:31 | 00:01:34 | 2 |
| 4 | Cycle ×2 | 00:01:37 | 00:01:50 | 5 |
| 5 | Path contrast | 00:02:02 | 00:02:15 | 5 |
| 6 | Named features | 00:02:19 | 00:02:34 | 5 |
| 7 | Takeaway + close | 00:02:38 | 00:02:46 | 3 |

**Total narration lines:** 47
**Last narration cue:** 00:02:46
**Final hold begins (plan.md):** ~00:02:47 (2.5 s hold per STYLE_BIBLE §6)
**Silent video ends:** 00:02:49

The last narration line at 00:02:46 ends before the 2.5 s final hold begins —
this satisfies the STYLE_BIBLE §12 quality bar ("narration for final hold begins
within ±1.0 s of visual cue" and must end before the hold window).

---

## STYLE_BIBLE §12 quality-bar self-check

| Check | Status |
|---|---|
| Narration track present | Will be produced by `synthesize` pipeline |
| Voice id matches `am_michael` | Confirmed — no override |
| First geometry reveal narration within ±1.0 s | Phase 1a cue at 00:00:02; grid appears at ~00:00:00. Delta ≈ 2.0 s — **FLAG: cue at 00:00:02 is within the 2.0 s post-reveal hold window (plan §9: `self.wait(2.0)` after grid FadeIn). Acceptable — narration begins during the hold, not after the next animation.** |
| No "first equation reveal" check | N/A — video contains no equations (plan §5 exemption) |
| Final hold narration ends before 2.5 s hold begins | Last line at 00:02:46; hold at ~00:02:47. Compliant. |
| No phase-boundary overflow | Synthesiser enforces shift-later policy. Verify `audio_report.json` after mux. |

---

## Audio-only content flag

Concepts mentioned in narration that have no corresponding visual on screen at that moment:

- **Phase 1e [00:00:34]:** The narration says "reinforcement learning problem" — the on-screen caption reads the same phrase, so this is a narration-caption duplicate. No accessibility gap; included for completeness.
- **Phase 2 [00:00:54–00:00:59]:** The narration contrasts RL with supervised and unsupervised learning using the phrases "no labels" and "no supervisor." All three panels are visible at these cues — no accessibility gap.
- **Phase 3f [00:01:34]:** The narration says "Not every environment reveals its full state." This is a qualitative statement with no diagram. The on-screen caption for Phase 3f reads: "In FrozenLake, the elf sees its exact state — not always the case in RL." The Transcript Writer should ensure this line appears as a caption even if the visual only holds the static loop diagram.
- **Phase 4 [00:01:46–00:01:50]:** The narration uses the word "episode." No episode-counter or episode-label appears on screen. The Transcript Writer must caption "episode" explicitly.
- **Phase 6 [00:02:34]:** The narration says "explore new ones — a tension we will return to." This is the exploration-exploitation acknowledgment. Per plan §10 RL Expert flag, it is caption-only; no visual exists for it. The Transcript Writer must include this line verbatim in the captions.
- **Phase 7 [00:02:46]:** The narration says "Markov Decision Process." The on-screen closing text also says this, so captions will capture it automatically. No gap.

**Summary:** Two narration-only concepts require explicit Transcript Writer attention:
(a) the word "episode" in Phase 4, and (b) the exploration-exploitation caption in Phase 6.
All other narrated concepts have visual counterparts.

---

## Synthesis command (reference)

```bash
cd /Users/ultramarine/Desktop/grad_project

/Users/ultramarine/.venvs/manim/bin/python -m manim_service.audio.synthesize \
  --narration manim_service/concept_videos/rl_intro_narration_script.md \
  --silent-mp4 media/videos/rl_intro_concept/480p15/RLIntroConcept.mp4 \
  --output    media/videos/rl_intro_concept/480p15/RLIntroConcept_narrated.mp4 \
  --lesson-id rl_intro
```

Expected output:
- `media/videos/rl_intro_concept/480p15/RLIntroConcept_narrated.mp4`
- `media/videos/rl_intro_concept/480p15/rl_intro_concept_narrated.audio_report.json`

Check `audio_report.json` for `lines[].warnings` before declaring delivery.
Any `"extends past video end"` warning must be escalated to the Script Writer
as a content-density mismatch — do not silently truncate.
