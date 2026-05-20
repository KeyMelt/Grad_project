Produce a full concept video for the given lesson_id by orchestrating all pipeline
agents as autonomous subagents. Each pipeline step spawns a separate Agent instance —
the current session acts only as the Producer orchestrator. Run end-to-end without
stopping for user confirmation unless a PRODUCTION HOLD condition is reached.

Invoked as:
  /project:produce-video lesson_id=<id>

---

## Authority model — lesson_id vs. teaching spec

`lesson_id` is only the stable identity / routing / artifact namespace for one
video. It determines filenames, resume state, registry keys, media paths, and
the lesson page that will receive the finished MP4. It is **not** a creative
scope limit.

`backend/concept_videos/specs.py` is a platform compatibility contract. It
contains app-facing metadata and any code lines the current product must still
recognise. It may define minimum integration obligations, but it must never be
used to reject additional theory, examples, derivations, visual explanations,
or pedagogical depth that the RL Expert judges necessary.

The pipeline's teaching authority is the RL Expert-authored Markdown spec:

```
manim_service/concept_videos/[lesson_id]_specs.md
```

All downstream agents treat that file as the concept brief. `specs.py` remains
available only as compatibility metadata unless the RL Expert explicitly adopts
part of it into `[lesson_id]_specs.md`.

---

## Step 0 — Parse arguments

Extract `lesson_id` from the command arguments. If absent, stop immediately:

```
Usage: /project:produce-video lesson_id=<id>
```

Validate only that `lesson_id` is a stable slug:
- lowercase letters, numbers, and underscores only
- starts with a lowercase letter
- no spaces

If invalid, stop and print:
```
PRODUCER REJECTION — [lesson_id]
Reason: invalid lesson_id slug. Use lowercase letters, numbers, and underscores.
```

Do not reject a lesson_id merely because it is outside the original six-video
lineup. Expanded course lesson_ids are valid production targets once the RL
Course Architect has placed them in the course plan and the Producer can satisfy
the final app-registration checklist.

---

## Step 1 — Read SESSION_LOG and determine pipeline state

Read `manim_service/SESSION_LOG.md`. Search for any prior production run for this
`lesson_id`:
- "PRODUCER APPROVAL — [lesson_id]" → already in library; report and stop.
- "PRODUCTION HOLD — [lesson_id]" → on hold; report and stop pending human review.
- A partial gate table for this lesson_id → resume from the last open gate.

If no prior run found, start fresh from Step 2.

Print:
```
Pipeline state for [lesson_id]: [NEW | RESUMING from gate N | ALREADY IN LIBRARY | ON HOLD]
```

Initialize the convergence gate table and carry it through all steps:
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

If resuming, mark already-confirmed gates [✓] and skip their steps.

---

## Step 2 — Load reference documents (orchestrator reads these once)

Before spawning any agents, read these files into your context:
- `manim_service/concept_videos/docs/STYLE_BIBLE.md`
- `manim_service/concept_videos/docs/rl_knowledge_base.md` (the entry for this lesson_id if present; otherwise the full prerequisite/DAG context)
- `/Users/ultramarine/Desktop/grad_support_files/grad_project/manim_service/concept_videos/rl_course_plan.md` if it exists
- `backend/concept_videos/specs.py` (platform compatibility metadata for this lesson_id if present)

You will pass the relevant excerpts into each agent's prompt below. Label the
`specs.py` excerpt as **platform_contract**, not as the teaching brief. If the
lesson_id is not yet in `specs.py`, set `platform_contract` to
`UNREGISTERED_NEW_LESSON` and continue; the RL Expert teaching spec must include
an app-metadata proposal for later Producer registration.

---

## Step 3 — RL Expert teaching spec (advisory, no gate)

Spawn an Agent:
```
description: "RL Expert teaching spec — [lesson_id]"
subagent_type: claude
prompt: |
  You are the RL Expert for an RL teaching video production pipeline.
  Read your full skill file at: ~/.claude/skills/rl-expert/SKILL.md

  Task: author the concept teaching spec (advisory — no gate decision required)
  lesson_id: [lesson_id]
  platform_contract: [paste the full LessonVideoSpec entry from specs.py, or UNREGISTERED_NEW_LESSON]
  rl_knowledge_base_entry: [paste the full lesson entry from rl_knowledge_base.md, or "No direct entry yet"]
  course_plan_context: [paste the matching rl_course_plan.md entry if available]
  target_path: manim_service/concept_videos/[lesson_id]_specs.md

  Treat lesson_id as an identity/routing key only. Treat platform_contract as
  minimum app compatibility metadata only. It must not cap the concept scope.
  If platform_contract is UNREGISTERED_NEW_LESSON, infer the appropriate app
  metadata proposal from the course plan and your RL expertise.

  Write a complete Markdown teaching spec to target_path. It should state what
  this concept requires pedagogically and academically, based on your RL
  expertise, Sutton & Barto grounding, Gymnasium behavior where relevant, and
  the rl_knowledge_base entry. Include:
  - concept definition and why it matters
  - prerequisite concepts and series position
  - canonical equations and acceptable variants
  - required worked examples / environments
  - common misconceptions and boundary conditions
  - minimum visual obligations
  - code ideas that should be connected to the lesson, including any required
    platform_contract code lines if they remain valid
  - numerical claims that Technical Validator must check
  - allowed expansions beyond platform_contract
  - app metadata proposal: title, environment_name, theory_equation,
    worked_example, code_focus_lines, misconception_to_prevent, takeaway_line,
    pacing_notes, and theory_verification candidates for specs.py
  - explicit "Do not oversimplify" notes

  Output: the path and full contents of [lesson_id]_specs.md, plus a brief
  bullet list of flags (or "No flags") for the Script Writer. Do not issue a
  gate verdict — this is advisory only.
```

Collect the generated specs.md path and the flags. Carry both into Step 4.

---

## Step 4 — Script Writer produces plan.md

Spawn an Agent:
```
description: "Script Writer — plan.md for [lesson_id]"
subagent_type: claude
prompt: |
  You are the Script Writer for an RL teaching video production pipeline.
  Read your full skill file at: ~/.claude/skills/script-writer/SKILL.md

  Production brief:
  lesson_id: [lesson_id]
  teaching_spec_md: [paste the full [lesson_id]_specs.md content from Step 3]
  platform_contract: [paste the full LessonVideoSpec entry from specs.py, or UNREGISTERED_NEW_LESSON]
  rl_knowledge_base_entry: [paste the full lesson entry, or "No direct entry yet"]
  course_plan_context: [paste the matching course-plan entry if available]
  rl_expert_flags: [paste the flags from Step 3, or "None"]
  style_bible_path: manim_service/concept_videos/docs/STYLE_BIBLE.md

  Treat teaching_spec_md as the creative and pedagogical source of truth.
  Treat platform_contract as minimum app compatibility metadata only. Do not
  shrink the plan to the platform_contract; include every academically useful
  expansion the teaching spec calls for.

  Length policy: quality over brevity. There is NO target duration. Content
  depth determines length, not the other way around. The video must FULLY
  cover the concept — theory, derivation, visual demonstration, code
  walkthrough, iteration/convergence demo where applicable, and connection
  to prior/next concepts. The only hard cap is 30 minutes; do not write a
  plan that would exceed it. Underrunning is a defect, not an efficiency.

  Follow the 3-phase internal workflow in your skill (Pedagogical Architect →
  Code Agent → Pacing Linter) before writing. Then produce a complete plan.md
  covering all 10 required sections. Write the file to:
  manim_service/concept_videos/[lesson_id]_plan.md

  Return the full plan.md content in your response.
```

Save the returned plan.md path for subsequent steps.

---

## Step 4.5 — Visual Director produces choreo.md

The Visual Director sits between the Script Writer and the Technical
Validator. It owns spatial composition, element lifecycle, motion
choreography, camera direction, sprite-math binding, cognitive load
budget, scientific rigor declaration, and pedagogical strategy
declaration. The Manim Expert will later read `choreo.md` alongside
`plan.md` and implement both faithfully — choreography is no longer left
to scene-writer improvisation.

Spawn an Agent:
```
description: "Visual Director — choreo.md for [lesson_id]"
subagent_type: claude
prompt: |
  You are the Visual Director for an RL teaching video production pipeline.
  Read your full skill file at: ~/.claude/skills/visual-director/SKILL.md

	  Input brief:
	  lesson_id: [lesson_id]
	  teaching_spec_path: manim_service/concept_videos/[lesson_id]_specs.md
	  plan_md_path: manim_service/concept_videos/[lesson_id]_plan.md
  rl_expert_status: PENDING-Gate1 (Script Writer's plan is not yet
      approved at Gate 1; you proceed in parallel — Gate 1 will review
      plan.md AND your choreo.md together)
  choreo_md_target: manim_service/concept_videos/[lesson_id]_choreo.md
  style_bible_path: manim_service/concept_videos/docs/STYLE_BIBLE.md
  rl_knowledge_base_path: manim_service/concept_videos/docs/rl_knowledge_base.md

  Produce a complete choreo.md per the output template in your skill.
  Every required section (Scientific Rigor, Pedagogical Strategy,
  Cognitive Load Budget, Element Lifecycle Matrix, Motion Choreography,
  Camera Shot List, Sprite-Math Binding Matrix, trace_vector pairs,
  Hand-off Notes) MUST be present.

  Cite the Six Principles from your skill by number where decisions
  are non-obvious. Apply STYLE_BIBLE §§13–28 strictly. Defer to
  3Blue1Brown reference patterns when no STYLE_BIBLE rule applies.

  Write the file to the target path. Return the full choreo.md content
  in your response.
```

Save the returned choreo.md path for subsequent steps. The Manim Expert
will receive both `plan.md` and `choreo.md` as binding inputs.

---

## Step 5 — Gate 1: RL Expert plan sign-off

Spawn an Agent (up to 2 attempts before escalation):
```
description: "RL Expert plan review — [lesson_id] (attempt N)"
subagent_type: claude
prompt: |
  You are the RL Expert for an RL teaching video production pipeline.
  Read your full skill file at: ~/.claude/skills/rl-expert/SKILL.md

  Task: plan-review (Gate 1)
  lesson_id: [lesson_id]
  teaching_spec_md: [paste the full [lesson_id]_specs.md content from Step 3]
  plan_md: [paste the full plan.md content from Step 4]
  choreo_md: [paste the full choreo.md content from Step 4.5]
  rl_knowledge_base_entry: [paste the full lesson entry]
  attempt: N (of 2 allowed before Producer escalation)

  Follow the 5-step review protocol in your skill. Use teaching_spec_md as the
  scope authority. Do not reject a plan merely because it goes beyond
  specs.py/platform_contract; reject only if it contradicts verified RL theory,
  the teaching spec, the project lesson sequence, or required app integration.

  In addition to the plan.md review, verify the choreo.md's Scientific Rigor
  (§1) and Pedagogical Strategy (§2) sections are sound:
  - Scientific Rigor: claims correctly scoped, qualifications present
    where the visualisation depends on a particular env variant
    (slippery vs deterministic, γ value, equiprobable π vs other).
  - Pedagogical Strategy: the chosen pattern actually defeats the
    misconception listed in rl_knowledge_base.md.

  Use the APPROVED or REJECTED output template from your skill.
  If REJECTED, list specific corrections with S&B citations. A
  rejection routes back to the Script Writer (plan content) OR the
  Visual Director (choreography/rigor) depending on the failure type;
  state explicitly which agent owns the fix.
```

- `APPROVED` → mark Gate 1 [✓], proceed to Step 6.
- `REJECTED` (Script Writer fault) → re-spawn Step 4 with the rejection
  notes appended to the brief, then re-spawn Step 4.5 (since the new
  plan may invalidate the prior choreo), then re-spawn this step.
- `REJECTED` (Visual Director fault) → re-spawn Step 4.5 only with the
  rejection notes appended, then re-spawn this step.
- On second rejection of either kind, place the lesson on PRODUCTION HOLD,
  append the hold to SESSION_LOG.md, and stop.

---

## Step 6 — Gate 2: Technical Validator

Spawn an Agent:
```
description: "Technical Validator — [lesson_id]"
subagent_type: claude
prompt: |
  You are the Technical Validator for an RL teaching video production pipeline.
  Read your full skill file at: ~/.claude/skills/technical-validator/SKILL.md

  Task: validate all numerical claims and code snippets in the plan.
  lesson_id: [lesson_id]
  teaching_spec_md: [paste the full [lesson_id]_specs.md content]
  plan_md: [paste the Gate-1-approved plan.md content]
  python_interpreter: /Users/ultramarine/.venvs/manim/bin/python
  rl_knowledge_base_entry: [paste the full lesson entry]

  Follow the 5-step validation protocol in your skill. Use Bash to run every
  numerical claim against the live Gymnasium environment. Include raw Bash output
  in your report. Use the PASS or discrepancy-list output template from your skill.
```

- `PASS` → mark Gate 2 [✓], proceed to Step 7.
- Discrepancy list → re-spawn Step 4 with corrected values appended to the brief,
  re-run Gate 1 RL Expert review, then re-spawn this step.
  On second failure, place on PRODUCTION HOLD and stop.

---

## Step 7 — Manim Expert: scene production

Spawn an Agent (this is the most tool-intensive step — it writes files and renders):
```
description: "Manim Expert — scene production for [lesson_id]"
subagent_type: claude
prompt: |
  You are the Manim Expert for an RL teaching video production pipeline.
  Read your full skill file at: ~/.claude/skills/manim-rl-animation-style-lock/SKILL.md
  Also read: manim_service/concept_videos/docs/STYLE_BIBLE.md

  Task: implement the concept video scene from the approved plan AND choreo.
  lesson_id: [lesson_id]
  teaching_spec_md: [paste the full [lesson_id]_specs.md content]
  plan_md: [paste the Gate-2-verified plan.md content]
  choreo_md: [paste the Gate-1-approved choreo.md content]
  output_scene_path: manim_service/concept_videos/[lesson_id]_concept.py
  manim_python: /Users/ultramarine/.venvs/manim/bin/python
  render_quality: -ql (480p15, development quality)

  Both plan.md and choreo.md are BINDING. The plan defines the narrative
  beats and equations; the choreo defines the visual composition,
  element lifecycle, motion choreography, camera shots, sprite-math
  bindings, and trace_vector pairs. Implement every row of every
  choreo.md table. Improvisation (decisions made because the plan
  didn't say where something goes) is now a QA REJECT — if a layout
  detail is missing from choreo.md, escalate to the Visual Director
  rather than guessing.

  Phase 1 — raw implementation:
  Write raw_scene.py following the plan.md phase sequence exactly. Use helpers from
  manim_service/scenes/ (panels, motion, rl_visuals). Apply the geometry-before-algebra
  rule (STYLE_BIBLE §7). Decompose all MathTex as component arrays.
  Implement choreo.md row-by-row: every Element Lifecycle Matrix entry
  becomes a FadeIn/FadeOut pair; every Motion Choreography row becomes a
  self.play(...) tagged with its purpose; every Camera Shot becomes a
  zoom_to/pan_to_follow/zoom_reset; every Sprite-Math Binding becomes a
  SpriteActionBinding or cross_highlight_pair; every trace_vector pair
  becomes a trace_vector(...) call.

  Phase 2 — self-lint and polish:
  Review raw_scene.py against the style checklist in your skill. Fix pacing, wait
  times, layout overlaps, opacity hierarchy. Verify every choreo.md row
  is implemented (no row may be silently skipped). Write the polished
  version to: manim_service/concept_videos/[lesson_id]_concept.py

  Phase 3 — render:
  Run: /Users/ultramarine/.venvs/manim/bin/python -m manim -ql \
    manim_service/concept_videos/[lesson_id]_concept.py [SceneClassName]
  Confirm no import errors and that the MP4 is produced.

  Return: the polished scene file path and the rendered MP4 path.
```

Record the polished scene path and MP4 path. Proceed to Steps 8–12 in parallel
where possible (Gates 3 and 4 can run concurrently; Gates 5 and 6 require the MP4).

---

## Step 8 — Gate 3: Voice & BGM Agent

Spawn an Agent:
```
description: "Voice & BGM Agent — [lesson_id]"
subagent_type: claude
prompt: |
  You are the Voice & BGM Agent for an RL teaching video production pipeline.
  Read your full skill file at: ~/.claude/skills/voice-bgm/SKILL.md
  Also read STYLE_BIBLE §12 (BGM palette): manim_service/concept_videos/docs/STYLE_BIBLE.md

  Task: produce narration script and BGM brief.
  lesson_id: [lesson_id]
  plan_md: [paste the approved plan.md]
  mp4_path: [path to 480p15 render from Step 7]

  Follow the phase-timing workflow in your skill. Write output files to:
  - manim_service/concept_videos/[lesson_id]_narration_script.md
  - manim_service/concept_videos/[lesson_id]_audio_brief.md

  Return the paths to both files and confirm delivery.
```

When both files are written with no outstanding revision requests: mark Gate 3 [✓].

---

## Step 9 — Gate 4: Transcript Writer

Spawn an Agent:
```
description: "Transcript Writer — [lesson_id]"
subagent_type: claude
prompt: |
  You are the Transcript Writer for an RL teaching video production pipeline.
  Read your full skill file at: ~/.claude/skills/transcript-writer/SKILL.md

  Task: produce closed caption files from the narration script.
  narration_script_path: manim_service/concept_videos/[lesson_id]_narration_script.md

  Read the narration script. Apply the 7 accessibility rules in your skill.
  Write output files to:
  - manim_service/concept_videos/[lesson_id]_captions.srt
  - manim_service/concept_videos/[lesson_id]_captions.vtt

  Flag any audio-only content gaps (narration that describes a visual without spoken
  description inaccessible to a deaf viewer). List flagged segments explicitly.
  Return the paths to both files and any flagged gaps.
```

- No gaps flagged → mark Gate 4 [✓].
- Gaps flagged → re-spawn Step 4 (Script Writer) with gap descriptions appended,
  re-run Gates 1–2–Step 7–Step 8, then re-spawn this step.
  On second failure, place on PRODUCTION HOLD and stop.

---

## Step 10 — Gate 5: QA Agent

Spawn an Agent:
```
description: "QA Agent — [lesson_id] (attempt N)"
subagent_type: claude
prompt: |
  You are the QA Agent for an RL teaching video production pipeline.
  Read your full skill file at: ~/.claude/skills/qa-agent/SKILL.md

  Task: full quality review of the rendered video, narration, and captions.
  lesson_id: [lesson_id]
  polished_scene_path: manim_service/concept_videos/[lesson_id]_concept.py
  mp4_path: [path to 480p15 render]
  narration_script_path: manim_service/concept_videos/[lesson_id]_narration_script.md
  captions_srt_path: manim_service/concept_videos/[lesson_id]_captions.srt
  rejection_history: [list of prior QA rejections for this lesson, or "None"]
  attempt: N (of 2 allowed before Producer escalation)

  Apply the full 20-item quality checklist in your skill. Check visual quality,
  pacing, style-lock compliance, three-way sync (equation/grid/code), Gymnasium
  asset fidelity, narration timing alignment, and caption accuracy.
  Use the APPROVED or REJECTED output template. If REJECTED, list pain points
  with frame references where possible, ordered by severity.
```

- `APPROVED` → mark Gate 5 [✓].
- `REJECTED` (first time) → re-spawn Step 7 (Manim Expert) with pain points appended,
  then re-spawn this step.
- `REJECTED` (second time, same root issue) → escalate to Script Writer (re-spawn
  Step 4 with QA diagnosis), re-run pipeline from Step 5. On third failure, place
  on PRODUCTION HOLD and stop.

---

## Step 11 — Gate 6: Series Continuity Agent

Spawn an Agent:
```
description: "Series Continuity Agent — [lesson_id]"
subagent_type: claude
prompt: |
  You are the Series Continuity Agent for an RL teaching video production pipeline.
  Read your full skill file at: ~/.claude/skills/series-continuity/SKILL.md

  Task: cross-series consistency check.
  lesson_id: [lesson_id]
  polished_scene_path: manim_service/concept_videos/[lesson_id]_concept.py
  mp4_path: [path to 480p15 render]
  session_log_path: manim_service/SESSION_LOG.md
  style_bible_path: manim_service/concept_videos/docs/STYLE_BIBLE.md
  narration_script_path: manim_service/concept_videos/[lesson_id]_narration_script.md

  Read SESSION_LOG.md to identify all previously approved videos in the library.
  Check the 5 categories in your skill: color conventions, terminology,
  cross-video references, prerequisite scaffolding, and visual grammar.
  Use the CONSISTENT or INCONSISTENT output template.
  If INCONSISTENT, list each conflict with the specific prior video it contradicts.
```

- `CONSISTENT` → mark Gate 6 [✓].
- `INCONSISTENT` → route visual conflicts to Step 7 (Manim Expert), terminology
  conflicts to Step 4 (Script Writer). Re-run affected gates. On second failure,
  place on PRODUCTION HOLD and stop.

---

## Step 12 — Gate 7: RL Expert final sign-off

Spawn an Agent:
```
description: "RL Expert final review — [lesson_id]"
subagent_type: claude
prompt: |
  You are the RL Expert for an RL teaching video production pipeline.
  Read your full skill file at: ~/.claude/skills/rl-expert/SKILL.md

	  Task: final academic sign-off (Gate 7)
	  lesson_id: [lesson_id]
	  teaching_spec_md: [paste the full [lesson_id]_specs.md content]
	  polished_scene_path: manim_service/concept_videos/[lesson_id]_concept.py
  mp4_path: [path to 480p15 render]
  rl_knowledge_base_entry: [paste the full lesson entry]
	  note: The plan.md was approved at Gate 1 against teaching_spec_md. This review
	        checks whether the rendered scene faithfully implements the plan and
	        teaching spec, or introduced new errors during production.

  Follow the 5-step review protocol. Focus on misconceptions or oversimplifications
  that may have been introduced by the Manim Expert during scene production.
  Use the APPROVED or REJECTED output template with S&B citations for any issues.
```

- `APPROVED` → mark Gate 7 [✓].
- `REJECTED` → re-spawn Step 7 (Manim Expert) with RL Expert corrections, re-run
  Gates 5–6, then re-spawn this step. On second rejection, place on PRODUCTION HOLD.

---

## Step 13 — Gate 8: Producer library approval

Run the library approval checklist directly (no agent spawn needed — this is the
orchestrator's own gate):

1. Confirm all 7 prior gates are marked [✓].
2. Confirm `lesson_id` is in `backend/concept_videos/specs.py` for app
   compatibility. This check does not limit the teaching spec or plan scope.
   If absent, spawn a backend metadata Agent to add a `LessonVideoSpec` entry
   using the app metadata proposal in `[lesson_id]_specs.md`; then re-check.
3. Check `CONCEPT_VIDEO_SCENES` in `manim_service/jobs/worker.py`. If not registered,
   spawn a minimal Agent to add the entry:
   ```
   description: "Register scene in CONCEPT_VIDEO_SCENES — [lesson_id]"
   subagent_type: claude
   prompt: |
     Edit manim_service/jobs/worker.py. Find the CONCEPT_VIDEO_SCENES dict and add:
     "[lesson_id]": SceneRef(
         scene_file=ROOT / "manim_service" / "concept_videos" / "[lesson_id]_concept.py",
         scene_class="[ClassName]",
     ),
     Also add "[lesson_id]" to KNOWN_LESSON_IDS if not already present.
     Confirm the edit was made.
   ```
4. Confirm prerequisite DAG: all prerequisite lesson_ids from the course plan or
   teaching spec are approved in SESSION_LOG.
5. Confirm file inventory exists:
   - `manim_service/concept_videos/[lesson_id]_specs.md`
   - `manim_service/concept_videos/[lesson_id]_concept.py`
   - 480p15 MP4
   - `[lesson_id]_narration_script.md`
   - `[lesson_id]_audio_brief.md`
   - `[lesson_id]_captions.srt`
   - `[lesson_id]_captions.vtt`
   - `[lesson_id]_plan.md`
   - `[lesson_id]_choreo.md`

When all checks pass, print:
```
PRODUCER APPROVAL — [lesson_id]
All 8 convergence gates open. Proceeding to final 720p render.
```
Mark Gate 8 [✓].

---

## Step 14 — Final 720p30 render

```bash
curl -s -X POST http://localhost:8200/render/concept-video \
  -H "Content-Type: application/json" \
  -d '{"lesson_id": "[lesson_id]", "quality": "720p30", "force": true}' \
  | python3 -c "import sys,json; d=json.load(sys.stdin); print(d['job_id'])"
```

Poll until complete:
```bash
while true; do
  STATUS=$(curl -s http://localhost:8200/jobs/{job_id} | python3 -c \
    "import sys,json; d=json.load(sys.stdin); print(d['status'])")
  echo "Status: $STATUS"
  [ "$STATUS" = "complete" ] || [ "$STATUS" = "failed" ] && break
  sleep 5
done
```

- `complete` → final MP4 is at `backend/media/concept_videos/[lesson_id]_concept.mp4`
- `failed` (404 / scene not registered) → re-run the registration sub-step from
  Step 13 then re-trigger. Do not mark the pipeline failed.
- `failed` (other) → report the error. Pipeline stays at Gate 8 open; render is a
  separate retry. Do not place on PRODUCTION HOLD for a render-only failure.

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

**Rejections encountered:** [N total — list gate, agent, and resolution, or "None"]
**Exceptions granted:** [list, or "None"]
**Teaching spec:** manim_service/concept_videos/[lesson_id]_specs.md
**Final MP4:** backend/media/concept_videos/[lesson_id]_concept.mp4
**Series position:** [course-plan wave/order, or original-six subset position]
**Status:** COMPLETE
```

---

## Error handling summary

| Condition | Action |
|-----------|--------|
| Invalid lesson_id | Stop. Print PRODUCER REJECTION. |
| lesson_id already in library | Stop. Report library status. |
| lesson_id on PRODUCTION HOLD | Stop. Direct to human review. |
| Agent rejects twice at same gate | Escalate: re-spawn upstream agent with diagnosis. |
| Agent rejects three times | Append PRODUCTION HOLD to SESSION_LOG. Stop. |
| Worker 404 at render | Register scene via agent spawn. Re-trigger render. |
| Render fails (non-404) | Report. Pipeline stays complete; render is a retry. |
| manim_service unreachable | Start with: uvicorn manim_service.api.main:app --host 0.0.0.0 --port 8200 |
