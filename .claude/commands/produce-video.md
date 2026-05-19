Produce a full concept video for the given lesson_id, orchestrating all pipeline agents
in the canonical sequence. Invoked as:

  /project:produce-video lesson_id=<id>

---

## Step 0 — Parse arguments

Extract `lesson_id` from the command arguments. If absent, stop immediately:

```
Usage: /project:produce-video lesson_id=<id>
Valid IDs: dp_policy_eval, dp_policy_improvement, dp_value_iteration,
           mc_first_visit, td_sarsa, td_q_learning
```

Verify the lesson_id is in `KNOWN_LESSON_IDS`:
`dp_policy_eval` · `dp_policy_improvement` · `dp_value_iteration` ·
`mc_first_visit` · `td_sarsa` · `td_q_learning`

If the lesson_id is not in the set, stop and print the PRODUCER REJECTION format from
the producer skill.

---

## Step 1 — Read SESSION_LOG.md and determine pipeline state

Read `manim_service/SESSION_LOG.md`. Search for any prior production run for this
`lesson_id`. Look for entries matching:
- "PRODUCER APPROVAL — [lesson_id]" → video is already in the library; report this and stop.
- "PRODUCTION HOLD — [lesson_id]" → pipeline is on hold; report and stop pending human review.
- A partial gate table for this lesson_id → resume from the last open gate (skip completed steps).

If no prior production run is found, start fresh from Step 2.

Print your determination:
```
Pipeline state for [lesson_id]: [NEW | RESUMING from gate N | ALREADY IN LIBRARY | ON HOLD]
```

---

## Step 2 — Invoke the Producer skill

Invoke the `producer` skill now. It governs the entire pipeline. Read:
- `manim_service/concept_videos/docs/STYLE_BIBLE.md` (§13 convergence gates)
- `manim_service/concept_videos/docs/rl_knowledge_base.md` (lesson entry for this lesson_id)
- `backend/concept_videos/specs.py` (confirm the lesson_id is registered)

Initialize the convergence gate table:
```
Gate  Agent                   Status    Notes
─────────────────────────────────────────────────────────────────
 1    RL Expert               [ ]       plan.md sign-off
 2    Technical Validator     [ ]       PASS
 3    Voice & BGM Agent       [ ]       narration_script.md + audio_brief.md
 4    Transcript Writer       [ ]       captions.srt + captions.vtt; 0 gaps
 5    QA Agent                [ ]       APPROVED
 6    Series Continuity Agent [ ]       CONSISTENT
 7    RL Expert               [ ]       Final sign-off
 8    Producer                [ ]       Library approval
─────────────────────────────────────────────────────────────────
```

If resuming, mark gates already confirmed open as [✓] and skip their steps below.

---

## Step 3 — RL Expert pre-brief review (advisory)

Invoke the `rl-expert` skill with:
```
mode: pre-brief
lesson_id: [lesson_id]
brief_summary: [1–3 sentences describing the planned concept video scope]
```

The RL Expert reviews the knowledge base entry and flags any concept-level issues
(prerequisite lesson not in library yet, scope too broad for duration, etc.).

This step is advisory — it does not open a gate. Record any flags and carry them
into the Script Writer brief.

---

## Step 4 — Script Writer produces plan.md

Invoke the `script-writer` skill with a production brief:
```
lesson_id: [lesson_id]
specs_entry: [the entry from backend/concept_videos/specs.py]
rl_expert_guidance: [flags and notes from Step 3, or "None"]
target_duration_seconds: 120
```

The Script Writer will produce a `plan.md` covering:
phase sequence, MathTex decomposition, Gymnasium code snippets,
pacing table, and visual component list.

Save or display the resulting `plan.md` for Gate 1 review.

---

## Step 5 — Gate 1: RL Expert plan sign-off

Invoke the `rl-expert` skill with:
```
mode: plan-review
lesson_id: [lesson_id]
plan_md: [the plan.md from Step 4]
```

- If `APPROVED`: mark Gate 1 [✓].
- If `REJECTED`: route feedback to the Script Writer (Step 4 redo).
  On second rejection, invoke the `producer` skill's escalation protocol.

Do not proceed to Step 6 until Gate 1 is open.

---

## Step 6 — Gate 2: Technical Validator

Invoke the `technical-validator` skill with:
```
lesson_id: [lesson_id]
plan_md: [the Gate 1-approved plan.md]
```

The Technical Validator runs live Gymnasium code against every numerical claim
in `plan.md` using `/Users/ultramarine/.venvs/manim/bin/python`.

- If `PASS`: mark Gate 2 [✓].
- If discrepancy list returned: route corrected values to the Script Writer.
  Script Writer updates `plan.md` and resubmits to Technical Validator.
  On second failure, invoke the `producer` skill's escalation protocol.

Do not proceed to Step 7 until Gate 2 is open.

---

## Step 7 — Manim Expert: scene production

Invoke the `manim-rl-animation-style-lock` skill with:
```
lesson_id: [lesson_id]
plan_md: [the Gate 2-verified plan.md]
phase: raw
```

The Manim Expert produces `raw_scene.py` from `plan.md` following the
geometry-before-algebra rule (STYLE_BIBLE §7). Then:

```
phase: polish
raw_scene_path: [path to raw_scene.py]
```

The Manim Expert self-renders at 480p15, reviews, and delivers `polished_scene.py`.

Save `polished_scene.py` to `manim_service/concept_videos/[lesson_id]_concept.py`.

Note: This step has no convergence gate of its own — the scene proceeds directly
to Gate 3 (Voice & BGM), Gate 5 (QA Agent), and Gate 6 (Series Continuity) review.

---

## Step 8 — Gate 3: Voice & BGM Agent

Invoke the `voice-bgm` skill with:
```
lesson_id: [lesson_id]
plan_md: [the approved plan.md]
mp4_path: [path to 480p15 polished render]
```

The Voice & BGM Agent delivers:
- `narration_script.md` — line-by-line narration with per-line timing cues
- `audio_brief.md` — BGM track selection + volume envelope from STYLE_BIBLE §12

When both files are delivered with no outstanding revision requests:
mark Gate 3 [✓].

---

## Step 9 — Gate 4: Transcript Writer

Invoke the `transcript-writer` skill with:
```
narration_script_path: [path to narration_script.md from Step 8]
```

The Transcript Writer delivers:
- `captions.srt` — SubRip format, UTF-8, max 2 lines per caption
- `captions.vtt` — WebVTT format, UTF-8, max 2 lines per caption

- If no audio-only gaps flagged: mark Gate 4 [✓].
- If gaps flagged: route back to the Script Writer to add narration coverage.
  Script Writer updates `plan.md` sections where gaps exist, Voice & BGM re-delivers
  the affected lines, Transcript Writer re-reviews.
  On second failure, invoke the `producer` skill's escalation protocol.

Do not proceed to Step 10 until Gate 4 is open.

---

## Step 10 — Gate 5: QA Agent

Invoke the `qa-agent` skill with:
```
lesson_id: [lesson_id]
polished_scene_path: [path to polished_scene.py]
mp4_path: [path to 480p15 render]
rejection_history: [list of prior QA rejections, or "None"]
```

- If `APPROVED`: mark Gate 5 [✓].
- If `REJECTED`: route blocking issues to the Manim Expert for fixes.
  Manim Expert re-renders at 480p15 and resubmits.
  On second rejection, invoke the `producer` skill's escalation protocol.

Do not proceed to Step 11 until Gate 5 is open.

---

## Step 11 — Gate 6: Series Continuity Agent

Invoke the `series-continuity` skill with:
```
lesson_id: [lesson_id]
polished_scene_path: [path to polished_scene.py]
mp4_path: [path to 480p15 render]
```

The Series Continuity Agent reads `manim_service/SESSION_LOG.md` to understand the
full series history, then checks for color convention conflicts, terminology
inconsistencies, and prerequisite scaffolding gaps.

- If `CONSISTENT`: mark Gate 6 [✓].
- If `INCONSISTENT`: route specific conflicts to the Manim Expert (visual fixes) or
  Script Writer (terminology/scaffolding fixes). Re-render and resubmit.
  On second failure, invoke the `producer` skill's escalation protocol.

Do not proceed to Step 12 until Gate 6 is open.

---

## Step 12 — Gate 7: RL Expert final sign-off

Invoke the `rl-expert` skill with:
```
mode: final-review
lesson_id: [lesson_id]
polished_scene_path: [path to polished_scene.py]
mp4_path: [path to 480p15 render]
```

The RL Expert reviews the rendered video against Sutton & Barto (2018) for any
misconceptions, oversimplifications, or prerequisite violations introduced during
scene production (the rendering phase may have diverged from the approved plan).

- If `APPROVED`: mark Gate 7 [✓].
- If `REJECTED`: route findings to the Manim Expert (scene edits), re-render,
  and resubmit to RL Expert.
  On second rejection, invoke the `producer` skill's escalation protocol.

Do not proceed to Step 13 until Gate 7 is open.

---

## Step 13 — Gate 8: Producer library approval

Invoke the `producer` skill to run the library approval checklist:

1. Verify all 7 prior gates are marked [✓].
2. Verify `lesson_id` is in `KNOWN_LESSON_IDS` and `backend/concept_videos/specs.py`.
3. Verify `lesson_id` is registered in `CONCEPT_VIDEO_SCENES` in
   `manim_service/jobs/worker.py`. If not registered, instruct the Manim Expert to
   add the entry before the final render (see producer skill for exact format).
4. Verify the prerequisite DAG: all prerequisite lesson_ids are already in the library
   or approved in the same release batch.
5. Verify file inventory: `polished_scene.py`, 480p15 MP4, `narration_script.md`,
   `audio_brief.md`, `captions.srt`, `captions.vtt`, `plan.md` all exist.

When all checks pass, issue the PRODUCER APPROVAL statement (see producer skill output
format) and mark Gate 8 [✓].

---

## Step 14 — Final 720p30 render

With all 8 gates open, trigger the final production render:

```bash
# Start manim_service if not already running:
# uvicorn manim_service.api.main:app --host 0.0.0.0 --port 8200

curl -X POST http://localhost:8200/render/concept-video \
  -H "Content-Type: application/json" \
  -d '{"lesson_id": "[lesson_id]", "quality": "720p30", "force": true}'
```

Poll `/jobs/{job_id}` until `status` is `"complete"` or `"failed"`.

If `"complete"`: the final MP4 is at
`backend/media/concept_videos/[lesson_id]_concept.mp4`.

If `"failed"` due to 404 (scene not yet registered): follow the producer skill's
registration recovery procedure, then re-trigger.

If `"failed"` for any other reason: report the error. Do not mark the run as complete.

---

## Step 15 — SESSION_LOG.md update

Append to `manim_service/SESSION_LOG.md`:

```
## Production Run — [lesson_id] — [YYYY-MM-DD]

**Gates opened:**
- Gate 1 (RL Expert plan sign-off): [date/time]
- Gate 2 (Technical Validator PASS): [date/time]
- Gate 3 (Voice & BGM delivery): [date/time]
- Gate 4 (Transcript delivery): [date/time]
- Gate 5 (QA APPROVED): [date/time]
- Gate 6 (Series Continuity CONSISTENT): [date/time]
- Gate 7 (RL Expert final sign-off): [date/time]
- Gate 8 (Producer approval): [date/time]

**Rejections encountered:** [N total, with gate and agent details, or "None"]
**Exceptions granted:** [list, or "None"]
**Final MP4:** backend/media/concept_videos/[lesson_id]_concept.mp4
**Series position:** [N of 6]
**Status:** COMPLETE
```

---

## Error handling summary

| Condition | Action |
|-----------|--------|
| Invalid lesson_id | Stop. Print PRODUCER REJECTION. |
| lesson_id already in library | Stop. Report library status. |
| lesson_id on PRODUCTION HOLD | Stop. Direct to human review. |
| Agent rejects twice at same gate | Invoke producer escalation protocol. |
| Agent rejects three times | Place on PRODUCTION HOLD in SESSION_LOG. |
| Worker returns 404 at render | Register scene, re-trigger render. Do not cancel pipeline. |
| Final render fails (non-404) | Report error. Pipeline stays at Gate 8 open; render is a separate retry. |
