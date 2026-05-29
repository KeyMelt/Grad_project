# Audio Brief — rl_mdp_core

**Date:** 2026-05-24
**plan.md reference:** manim_service/concept_videos/rl_mdp_core_plan.md
**narration_script reference:** manim_service/concept_videos/rl_mdp_core_narration_script.md

---

## Voice (series-locked, STYLE_BIBLE §12)

| Field | Value |
|---|---|
| TTS engine | Kokoro v1.0 (local, ONNX) |
| Voice id | `am_michael` |
| Register | Measured, professorial, American male |
| Speed | 1.0 (do not override) |
| Sample rate | 24 kHz |
| Output format | AAC stereo, 192 kbps (mono dual-routed to L+R) |

The voice id `am_michael` is the series constant. No deviation.

---

## BGM — NONE (STYLE_BIBLE §12)

**This video uses no background music.** Per series policy, concept videos
are narration-only: the narration carries the pedagogy, and any BGM would
compete with the on-screen mathematical text. This mirrors the 3Blue1Brown
approach. No BGM track, no volume envelope, no ducking.

---

## Mixing / envelope

- Master narration gain: 0.9 (−1 dB headroom), applied uniformly (compose.py `_MASTER_GAIN`).
- Inter-clip pad: 0.08 s between adjacent lines (prevents waveform discontinuity).
- No ducking (no competing BGM track).
- Final mux: narration WAV muxed into the silent MP4 via ffmpeg; audio length is the master if it exceeds the silent video (mux holds last frame). **For this lesson, the silent video must be re-timed to ~21:00 so audio and video durations match within ±0.5 s — see Production Note below.**

---

## Per-segment delivery notes (register guidance for QA review)

| Segment | Phases | Delivery character |
|---|---|---|
| 1 — What is RL? | S1-P1 … S1-P3 | Slow, deliberate, building tension. Let the silences after "Only a zero." breathe. The emotional weight of the sparse reward is the point. |
| 2 — MDP Framework | S2-P4 … S2-P5 | Measured, clarifying. The Markov property is framed as a gift; the tone should feel like an unlock, not a constraint. |
| 3a — Dynamics function | S3a-P6 … S3a-P7 | Reverent on the equation reveal (full-screen solo). Each of the four arguments gets a distinct beat. |
| 3b — Transition probability | S3b-P8 … S3b-P10 | Confident, concrete. The code-equals-math point lands flat and certain — no hedging. |
| 4 — Returns | S4-P11 … S4-P15 | The discount-factor section is the conceptual climax. The γ=1 qualification must be delivered carefully (it is the M-4 misconception defeat). Close warm on the forward tease. |

---

## Emphasis marks (already embedded in narration_script.md via *asterisks*)

Kokoro maps `*word*` to vocal stress. One stress per sentence maximum.
Key emphasis points: "*absence* of feedback", "*reward of one*", "*Markov property*",
"*p of s-prime, r, given s and a*", "*return*", "*gamma*", "*return recursion*", "*strategy*".

---

## Production Note — timing reconciliation (2026-05-24)

The first silent render (RLMDPCoreConcept.mp4) is 240.9 s, but the narration
runs to ~21:00. Per STYLE_BIBLE §12 QA-D ("final video duration matches
narration duration ±0.5 s; no phase-boundary overflow warnings"), the silent
scene must be re-rendered with per-phase holds that match each phase's measured
narration duration (3B1B-style holds on the primary content — equation/diagram
visible while the narrator explains). The narration script's phase timing table
is the authority for per-phase windows. After re-render, synthesize with
`--phase-timestamps` so each line lands inside its phase window.

---

*End of audio brief — rl_mdp_core*
