# Audio Brief — policies_values_bellman

**Date:** 2026-05-27
**narration_script.md reference:** /Users/ultramarine/Desktop/grad_project/manim_service/concept_videos/policies_values_bellman_narration_script.md
**Total video duration:** 1289.933 s (≈ 21 min 30 s)
**Voice:** `am_michael` (Kokoro v1.0, series default — STYLE_BIBLE §12)

---

## BGM selection

**No BGM.** Per STYLE_BIBLE §12, the concept-video series is narration-only.
Background music would compete with the on-screen mathematical text and is
explicitly disallowed for this lesson type. This audio brief documents
that choice for Series Continuity verification across the series.

- No track is selected.
- No loop point or seam test is required.
- No ducking schedule is required because there is no second audio bus
  to duck against narration.

If a future Producer decision adds an exception for a specific lesson,
that exception must (a) be granted in writing, (b) update STYLE_BIBLE §12,
and (c) replace this section with a track recommendation, loop test, and
phase-by-phase ducking table.

---

## Volume envelope

Single bus — narration only.

| Moment | Time | Narration volume |
|---|---|---|
| Scene open | 00:00:00 | 100% (no fade-in; first line is content) |
| Under all phases | 00:00:00 – 00:21:29 | 100% |
| Scene close | last 1.0 s of final hold | natural tail (no fade-out applied; Kokoro line end is the cut) |

No ducking, no crossfades, no music bed.

---

## Audio-only content flags

Lines where the narration introduces a concept whose on-screen anchor is
*not* the equation/grid currently in focus. The Transcript Writer must
ensure these are clearly captioned because a viewer relying on captions
cannot fall back to the visual to disambiguate.

- **Phase S1-P1, [00:00:15]** — "the *return* — the discounted sum of every reward still to come."
  The grid is on screen as a visual anchor; the term "return" is named in
  the recap caption stack but not formally re-defined here. Caption must
  spell out "return" in full (not abbreviate to G).

- **Phase S2-P3, [00:01:18]** — "A-sub-t equals a, when the state is S-sub-t equals s."
  Spoken-form subscripts will not be visible on screen as a separate gloss;
  caption must render them as plain text "A_t = a" / "S_t = s" for
  accessibility, even though the on-screen equation uses LaTeX subscripts.

- **Phase S3-P9, [00:08:13]** — "Once the agent is *at* the goal, the episode is over.
  There is no future return left to collect."
  This is the misconception defuse line. The on-screen marker shows the
  goal cell co-displayed with green (terminal) and yellow (non-reward)
  indicators, but the *reasoning* (episode termination → no future return)
  is delivered audio-only. Caption must preserve the full sentence.

- **Phase S4-P11, [00:09:42]** — "Up and left are worse, but never zero.
  Even a bad action keeps some hope alive on slippery ice."
  The numerical values for q(14, UP) and q(14, LEFT) are not labeled on
  the bar chart at this moment; only the bars themselves are drawn.
  Caption must keep the comparative phrasing intact.

- **Phase S5-P15, [00:12:30]** — "The *next reward*, plus the *discounted future return* from the next state."
  The equation panel shows R_{t+1} + γG_{t+1} but the verbal gloss "next
  reward / discounted future return" is the pedagogical bridge and lives
  in narration only.

- **Phase S5-P17, [00:14:13]** — "The outer sum is over actions.
  The inner sum is over transitions. They never collapse into one."
  This is the rl_expert_flag-2 callout. The "never collapse into one"
  warning is audio-only — there is no on-screen graphic flagging the
  anti-pattern. Caption must preserve this sentence verbatim.

- **Phase S5-P18, [00:15:11]** — "v-sub-pi is the *fixed point* of this relationship —
  the function that is consistent with itself under pi."
  The term "fixed point" appears on screen only briefly; caption must
  render it in plain text without abbreviation.

- **Phase S6-P20, [00:16:50]** — "The Bellman equation does not *compute* v-sub-pi. It *checks* that v-sub-pi is itself."
  This is the V-03 hand-off priming sentence. No on-screen text says
  "checks, not computes" — audio-only.

- **Phase S7-P23, [00:19:48]** — "One sweep is not enough — the heatmap takes many sweeps to emerge.
  *V-03* is where we iterate this loop until the numbers stop changing."
  The "V-03 hand-off" sentence is audio-only; the hand-off caption on
  screen says less. Transcript Writer must include the full sentence.

- **Phase S8-P25, [00:20:51]** — "That algorithm is the next video — *policy evaluation*.
  v-sub-pi is the fixed point it converges to."
  The V-03 forward-tease. "Fixed point it converges to" is audio-only and
  is the bridge sentence Series Continuity will check.

No other audio-only gaps. All numerical values quoted in narration
(`0.012`, `0.039`, `0.434`, `0.533`, `0.522`, `0.000000`) match the
canonical values in `policies_values_bellman_tv_canonical.md`.

---

## Synthesis command (for the Producer / pipeline)

```bash
/Users/ultramarine/.venvs/manim/bin/python -m manim_service.audio.synthesize \
  --narration manim_service/concept_videos/policies_values_bellman_narration_script.md \
  --silent-mp4 backend/media/concept_videos/policies_values_bellman_concept.mp4 \
  --output    backend/media/concept_videos/policies_values_bellman_concept_narrated.mp4 \
  --lesson-id policies_values_bellman \
  --phase-timestamps /Users/ultramarine/Desktop/grad_project/media/videos/policies_values_bellman_concept/480p15/phase_timestamps.json
```

Review the resulting `policies_values_bellman_concept_narrated.audio_report.json`
for any `extends past video end` warnings before declaring delivery.
