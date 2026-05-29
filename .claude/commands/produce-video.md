Produce a full concept video for the given lesson_id by orchestrating all pipeline
agents as autonomous subagents. Each pipeline step spawns a separate Agent instance —
the current session acts only as the Producer orchestrator.

Two execution modes:
- `mode=auto` (default): run end-to-end without stopping unless a PRODUCTION HOLD is reached.
- `mode=supervised`: pause at four human-review checkpoints (A–D) and wait for explicit
  approval before each expensive or irreversible stage. The human may describe edits at
  any checkpoint; the orchestrator applies them before continuing.

Invoked as:
  /project:produce-video lesson_id=<id> [mode=auto|supervised]

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

Extract `lesson_id` and optional `mode` from the command arguments.

If `lesson_id` is absent, stop immediately:
```
Usage: /project:produce-video lesson_id=<id> [mode=auto|supervised]
```

**`lesson_id` validation** — must be a stable slug:
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

**`mode` parsing** — extract `mode=` from the arguments:
- `mode=supervised` → set `SUPERVISED=true`. Four human checkpoints (A–D) will
  pause the pipeline at key stages.
- `mode=auto` or `mode` absent → set `SUPERVISED=false`. Pipeline runs
  end-to-end without stopping (original behaviour).
- Any other value → stop and print:
  ```
  PRODUCER REJECTION — invalid mode "[value]". Use mode=auto or mode=supervised.
  ```

Print the resolved mode immediately after parsing:
```
Pipeline mode: [AUTO | SUPERVISED]
Pipeline state for [lesson_id]: [NEW | RESUMING from gate N | ALREADY IN LIBRARY | ON HOLD]
```

---

## Step 1 — Read SESSION_LOG and determine pipeline state

Read `manim_service/SESSION_LOG.md`. Search for any prior production run for this
`lesson_id`:
- "PRODUCER APPROVAL — [lesson_id]" → already in library; report and stop.
- "PRODUCTION HOLD — [lesson_id]" → on hold; report and stop pending human review.
- A partial gate table for this lesson_id → resume from the last open gate.

If no prior run found, start fresh from Step 2.

(The pipeline state line is printed at the end of Step 0 together with the
mode line. Do not print it again here.)

Initialize the convergence gate table and carry it through all steps:
```
Gate  Agent                   Vendor / Model        Status   Notes
──────────────────────────────────────────────────────────────────────────────
 -    Spec author (advisory)  Claude / Sonnet       [ ]      Step 3: specs.md
 -    Script Writer           OpenAI / GPT-5        [ ]      Step 4: plan.md
 -    Visual Director         Claude / Sonnet       [ ]      Step 4.5: choreo.md
 1    RL Expert (plan review) OpenAI / GPT-5        [ ]      plan + choreo sign-off
 2    Technical Validator     OpenAI / GPT-5        [ ]      live Gymnasium PASS
 -    Manim Expert            Claude / Sonnet       [ ]      Step 7: scene + Self-QA
 3    Voice & BGM Agent       OpenAI / GPT-5        [ ]      narration_script + audio_brief
 4    Transcript Writer       OpenAI / GPT-5        [ ]      .srt + .vtt; 0 gaps
 5    QA Agent (VERIFIER)     Claude / Opus         [ ]      spot-check Manim Expert self-QA
 6    Series Continuity       OpenAI / GPT-5        [ ]      frames_compared CONSISTENT
 7    RL Expert (final)       Claude / Sonnet       [ ]      Final sign-off w/ frames_inspected
 8    Producer                Claude / Sonnet       [ ]      Library approval
──────────────────────────────────────────────────────────────────────────────
Total: Claude 6 (1 Opus + 5 Sonnet), OpenAI 6 (Codex/GPT-5)
```

If resuming, mark already-confirmed gates [✓] and skip their steps.

---

## Step 1.5 — Preflight (skill canon + state checkpoint)

This pipeline splits heavy execution to Codex (see
`manim_service/concept_videos/docs/CODEX_HANDOFF.md`). Before spawning agents:

1. Verify Claude's pipeline skill symlinks resolve to the canonical Codex
   copies (prevents silent skill drift):
   ```bash
   bash manim_service/pipeline/check_skill_canon.sh
   ```
   If it reports drift, run `bash manim_service/pipeline/check_skill_canon.sh --repair`
   and re-run the check before continuing.

2. Initialize (or load) the machine-readable state checkpoint:
   ```bash
   /Users/ultramarine/.venvs/manim/bin/python -m manim_service.pipeline.pipeline_state init [lesson_id]
   ```
   This file (`manim_service/concept_videos/[lesson_id]_pipeline_state.json`) is
   the resume point. Update it as gates open with:
   ```bash
   ... pipeline_state set-gate [lesson_id] <gate_key> pass
   ```
   Gate keys: `g1_rl_expert_plan g2_tech_validator g3_voice_bgm g4_transcript
   g5_qa g6_series_continuity g7_rl_expert_final g8_producer`.

---

## Step 2 — Build the lesson manifest (single source of truth)

**Token discipline (2026-05-28):** Inline pasting of large artifact contents
into agent prompts is BANNED. Instead, build a manifest at
`manim_service/pipeline/cache/<lesson_id>/manifest.json` and pass its PATH to
every agent. Both Claude and Codex agents read the manifest and fetch what
they need from disk. This saved ~70% of input tokens in V-03 pilot.

```bash
/Users/ultramarine/.venvs/manim/bin/python -m manim_service.pipeline.lesson_cache \
  <lesson_id> build
```

The orchestrator (you) still reads the following files INTO ITS OWN CONTEXT
for routing decisions — these are short and you reference them constantly:
- `manim_service/concept_videos/docs/STYLE_BIBLE.md` — for terminology/palette
- `manim_service/concept_videos/docs/COMMON_DEFECTS.md` — for defect-class routing
- `manim_service/concept_videos/docs/rl_knowledge_base.md` — entry for this lesson
- `backend/concept_videos/specs.py` — platform contract (if present)

Agents receive the manifest path and the brief path. Nothing else inline.

If the lesson_id is not in `specs.py`, set the manifest's `platform_contract`
note to `UNREGISTERED_NEW_LESSON`; the RL Expert teaching spec must include
an app-metadata proposal for later Producer registration.

---

## Step 3 — RL Expert teaching spec (advisory, no gate)

**Vendor: Claude (Sonnet).** Judgment-heavy, long-context S&B reasoning.

Spawn an Agent:
```
description: "RL Expert teaching spec — [lesson_id]"
subagent_type: claude
model: sonnet
prompt: |
  You are the RL Expert for an RL teaching video production pipeline.
  Read your full skill file at: ~/.claude/skills/rl-expert/SKILL.md

  Task: author the concept teaching spec (advisory — no gate decision required)
  lesson_id: [lesson_id]
  manifest_path: manim_service/pipeline/cache/[lesson_id]/manifest.json
  target_path: manim_service/concept_videos/[lesson_id]_specs.md

  Read the manifest first. From it, fetch:
    - platform_contract — manifest['notes']['platform_contract'] (or the file
      manifest['artifacts'] points to if a spec already exists)
    - rl_knowledge_base — manifest['artifacts']['rl_knowledge_base']
    - style_bible — manifest['artifacts']['style_bible']
  Do NOT expect content pasted into this prompt.

  Treat lesson_id as identity/routing only. Treat platform_contract as minimum
  app compatibility metadata only — it must NOT cap the concept scope. If it
  is UNREGISTERED_NEW_LESSON, infer the app metadata proposal yourself.

  Write a complete teaching spec to target_path covering:
  - concept definition and why it matters
  - prerequisite concepts and series position
  - canonical equations and acceptable variants
  - required worked examples / environments
  - common misconceptions and boundary conditions (with defeat strategies)
  - minimum visual obligations
  - numerical claims the Technical Validator must check
  - allowed expansions beyond platform_contract
  - app metadata proposal (title, environment_name, theory_equation,
    worked_example, code_focus_lines, misconception_to_prevent, takeaway_line,
    pacing_notes, theory_verification)
  - explicit "Do not oversimplify" notes

  Output to the orchestrator (your response): one short paragraph confirming
  the target_path was written, plus flags for the Script Writer (or "None").
  Do not paste the spec content into your response — it's on disk.
```

Collect the generated specs.md path and the flags. Carry both into Step 4.

---

## Step 4 — Script Writer produces plan.md

**Vendor: OpenAI (Codex / GPT-5).** Structured beat-sheet generation; fast at
templated output. The brief is path-only.

1. Copy the Codex brief template, filling `{LESSON_ID}`:
   ```bash
   sed "s/{LESSON_ID}/[lesson_id]/g" \
     manim_service/pipeline/codex_briefs/script_write.md \
     > manim_service/concept_videos/[lesson_id]_codex_brief_script_write.md
   ```

2. Dispatch Codex:
   ```bash
   bash manim_service/pipeline/codex_render.sh \
     --lesson-id [lesson_id] --stage script_write \
     --brief manim_service/concept_videos/[lesson_id]_codex_brief_script_write.md \
     --result manim_service/concept_videos/[lesson_id]_script_write_result.md
   ```

3. Read the result file. Parse the STAGE_RESULT block — confirm `status: success`
   and `plan_path` exists. Record the result with `lesson_cache`:
   ```bash
   /Users/ultramarine/.venvs/manim/bin/python -c "
   from manim_service.pipeline.lesson_cache import record_stage_result
   record_stage_result('[lesson_id]', stage='script_write',
                       result_path='<from STAGE_RESULT>', verdict='WRITTEN')
   "
   ```

---

## Step 4.5 — Visual Director produces choreo.md

The Visual Director sits between the Script Writer and the Technical
Validator. It owns spatial composition, element lifecycle, motion
choreography, camera direction, sprite-math binding, cognitive load
budget, scientific rigor declaration, and pedagogical strategy
declaration. The Manim Expert will later read `choreo.md` alongside
`plan.md` and implement both faithfully — choreography is no longer left
to scene-writer improvisation.

**Vendor: Claude (Sonnet).** Spatial composition reasoning under dense rules
(STYLE_BIBLE §§13–28 plus §34/§35).

Spawn an Agent:
```
description: "Visual Director — choreo.md for [lesson_id]"
subagent_type: claude
model: sonnet
prompt: |
  You are the Visual Director for an RL teaching video production pipeline.
  Read your full skill file at: ~/.claude/skills/visual-director/SKILL.md

  Input brief:
  lesson_id: [lesson_id]
  manifest_path: manim_service/pipeline/cache/[lesson_id]/manifest.json
  choreo_md_target: manim_service/concept_videos/[lesson_id]_choreo.md
  rl_expert_status: PENDING-Gate1 (Script Writer's plan is not yet
      approved at Gate 1; you proceed in parallel — Gate 1 will review
      plan.md AND your choreo.md together)

  Read the manifest first. From it, fetch artifacts['specs'], artifacts['plan'],
  artifacts['style_bible'], artifacts['rl_knowledge_base'],
  artifacts['common_defects']. Do NOT expect content pasted into this prompt.

  Produce a complete choreo.md per the output template in your skill. Every
  required section (Scientific Rigor, Pedagogical Strategy, Cognitive Load
  Budget, Element Lifecycle Matrix, Motion Choreography, Camera Shot List,
  Sprite-Math Binding Matrix, trace_vector pairs, Hand-off Notes) MUST be
  present. STYLE_BIBLE §34 (code walkthrough — two-panel + IDE) and §35
  (equation dissection — token-by-token) are mandatory production patterns —
  every code phase and every derivation phase must encode them.

  Write the file to choreo_md_target. Reply with a one-line confirmation;
  do NOT paste the choreo into your response.
```

The Manim Expert reads both plan.md and choreo.md from the manifest.

---

## [SUPERVISED CHECKPOINT A] — Creative review
**Active only when `SUPERVISED=true`. Skip entirely when `SUPERVISED=false`.**

Before spawning the Gate 1 RL Expert review, pause so the human can read
the generated brief and request edits.

1. Print the following banner:
   ```
   ══ SUPERVISED CHECKPOINT A — Creative Review ══════════════════════════
   Teaching spec, plan, and choreo are ready for your review:

     Spec  : manim_service/concept_videos/[lesson_id]_specs.md
     Plan  : manim_service/concept_videos/[lesson_id]_plan.md
     Choreo: manim_service/concept_videos/[lesson_id]_choreo.md

   Open any of these files and read them. Then tell me how to proceed:
     • "proceed"            — continue to Gate 1 as-is
     • describe any edits   — I'll apply them before Gate 1
     • "abort"              — stop without recording a PRODUCTION HOLD
   ════════════════════════════════════════════════════════════════════════
   ```

2. **Wait for the human's reply.** Do NOT spawn the Gate 1 agent until you
   receive it.

3. Response handling:
   - `"proceed"` (case-insensitive) → continue to Step 5.
   - Natural-language edit description → apply the described changes to the
     relevant file(s) (specs.md, plan.md, and/or choreo.md) using Edit.
     After applying, print a short diff summary and re-display the checkpoint
     banner, then wait again.
   - `"abort"` → print:
     ```
     Pipeline aborted at Checkpoint A (user request). No PRODUCTION HOLD recorded.
     ```
     Stop. Do not update SESSION_LOG.

4. There is no retry limit at checkpoints — the human may iterate as many
   times as needed.

---

## Step 5 — Gate 1: RL Expert plan sign-off

**Vendor: OpenAI (Codex / GPT-5).** Cross-vendor counterweight to Claude's
Visual Director — independent second opinion on the plan and choreo.

1. Fill brief template:
   ```bash
   sed "s/{LESSON_ID}/[lesson_id]/g" \
     manim_service/pipeline/codex_briefs/gate1_review.md \
     > manim_service/concept_videos/[lesson_id]_codex_brief_gate1_review.md
   ```
2. Dispatch:
   ```bash
   bash manim_service/pipeline/codex_render.sh \
     --lesson-id [lesson_id] --stage gate1_review \
     --brief manim_service/concept_videos/[lesson_id]_codex_brief_gate1_review.md \
     --result manim_service/concept_videos/[lesson_id]_gate1_result.md
   ```
3. Parse `verdict:` and `fault_routing:` from the STAGE_RESULT block.

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

**Vendor: OpenAI (Codex / GPT-5).** Native `danger-full-access` lets Codex
execute live Gymnasium without approval prompts — its natural strength.

1. Fill brief template:
   ```bash
   sed "s/{LESSON_ID}/[lesson_id]/g" \
     manim_service/pipeline/codex_briefs/tech_validate.md \
     > manim_service/concept_videos/[lesson_id]_codex_brief_tech_validate.md
   ```
2. Dispatch:
   ```bash
   bash manim_service/pipeline/codex_render.sh \
     --lesson-id [lesson_id] --stage tech_validate \
     --brief manim_service/concept_videos/[lesson_id]_codex_brief_tech_validate.md \
     --result manim_service/concept_videos/[lesson_id]_tech_validate_result.md
   ```
3. Parse `verdict:` from STAGE_RESULT (`PASS` or `DISCREPANCY`). If a
   canonical values file was produced, the manifest auto-discovers it via
   the standard `tv_canonical` artifact key.

- `PASS` → mark Gate 2 [✓], proceed to Checkpoint B (or directly to Step 7 in auto mode).
- Discrepancy list → re-spawn Step 4 with corrected values appended to the brief,
  re-run Gate 1 RL Expert review, then re-spawn this step.
  On second failure, place on PRODUCTION HOLD and stop.

---

## [SUPERVISED CHECKPOINT B] — Pre-render approval
**Active only when `SUPERVISED=true`. Skip entirely when `SUPERVISED=false`.**

Gates 1 and 2 are both open. The next step is the Codex scene render — the
heaviest step in the pipeline (~30–40 min of code generation + render time).
Pause so the human can confirm before committing.

1. Print:
   ```
   ══ SUPERVISED CHECKPOINT B — Pre-Render Approval ═══════════════════════
   Gates 1 (RL Expert) and 2 (Technical Validator) are both PASS.
   Next: Codex scene render (~30–40 min).

   Final approved plan : manim_service/concept_videos/[lesson_id]_plan.md
   Final choreo        : manim_service/concept_videos/[lesson_id]_choreo.md
   Tech Validator notes: [paste the one-line TV notes, or "None"]

   Tell me how to proceed:
     • "proceed"            — launch Codex scene render
     • describe any edits   — I'll apply them to plan.md / choreo.md before rendering
     • "abort"              — stop without recording a PRODUCTION HOLD
   ════════════════════════════════════════════════════════════════════════
   ```

2. **Wait for the human's reply.**

3. Response handling:
   - `"proceed"` → continue to Step 7.
   - Edit description → apply changes to the relevant file(s). After applying,
     print a diff summary. If the edit touches plan.md in a way that could
     invalidate Gate 2 (e.g. adds new numerical claims), note this and offer to
     re-run the Technical Validator before rendering. Then re-display the banner.
   - `"abort"` → stop. Do not write to SESSION_LOG.

---

## Step 7 — Manim Expert (scene.py + render + Self-QA Phase 0)

**Vendor: Claude (Sonnet).** (Was Codex.) Sonnet now authors the scene with
the manim-rl-animation-style-lock skill AND performs its own Self-QA Phase 0
frame inspection before handoff. This is the **tandem-with-QA** design that
reduces rejection rounds from ~3–5 to ~1.

Why Sonnet, not Opus: budget constraint. The Self-QA Phase 0 catches most
defects before they reach QA Gate 5 (Opus). Sonnet's Read-tool frame
inspection is cheap; Opus is reserved for the spot-check verifier role.

Spawn:
```
description: "Manim Expert — scene + self-QA for [lesson_id] (attempt N)"
subagent_type: claude
model: sonnet
prompt: |
  You are the Manim Expert. Read your skill at:
  ~/.claude/skills/manim-rl-animation-style-lock/SKILL.md

  Also read MANDATORY:
  - manim_service/concept_videos/docs/STYLE_BIBLE.md (especially §34 and §35)
  - manim_service/concept_videos/docs/COMMON_DEFECTS.md (RC-1..RC-N dossier)
  - manim_service/concept_videos/docs/CODEX_HANDOFF.md §3 (workflow protocol)

  Task: author + render + self-QA scene.py for V-<series-number>.

  lesson_id: [lesson_id]
  manifest_path: manim_service/pipeline/cache/[lesson_id]/manifest.json
  attempt: N (of 2 allowed before Producer escalation)
  prior_qa_rejection: [paste defect list from prior QA REJECTED report, or "None"]

  Read manifest first. From it:
  - artifacts['plan'] — beat sheet
  - artifacts['choreo'] — visual composition contract (BINDING)
  - artifacts['tv_canonical'] — numerical values to hard-code
  - artifacts['style_bible'] — §34/§35 + lifecycle hygiene
  - artifacts['common_defects'] — defect dossier

  Workflow per the skill:
  - Section E (3-Phase Generation): Pedagogical Architect → Structural Agent
    → Pacing Linter → polished_scene.py
  - Render: `/Users/ultramarine/.venvs/manim/bin/python -m manim -ql \
    <scene_path> <SceneClassName>`
  - **Section E.4 (Self-QA Phase 0, MANDATORY)**:
    1. Run `python -m manim_service.pipeline.frame_selector` to get strategic
       frame timestamps.
    2. Extract every frame via Bash + ffmpeg into /tmp/self_qa_[lesson_id]/.
    3. Read each PNG with the Read tool. Write one-sentence observations.
    4. Apply the defect dossier (RC-1..RC-10) to each frame.
    5. If defects found: PATCH-class → Edit + re-render. STRUCTURAL → revise
       Phase 2 + re-render. Loop up to 2 self-revisions.
    6. Write self_qa_report.md to:
       manim_service/concept_videos/[lesson_id]_self_qa_report.md

  STAGE_RESULT format (return this in your reply, NOT pasted file content):
  ```
  STAGE_RESULT
  stage: scene_render
  status: success | failed
  scene_py: <absolute path>
  silent_mp4: <absolute path>
  phase_timestamps_json: <absolute path>
  duration_seconds: <from manim log>
  self_qa_report_path: <absolute path>
  total_frames_inspected: <int — must be ≥ phase_count / 2>
  self_revisions: 0 | 1 | 2
  ready_for_qa: true | false
  known_residuals: <list or "none">
  errors: <only if failed; e.g. MISSING_CHOREO, MISSING_ASSETS, RENDER_FAILURE>
  ```

  Submissions with total_frames_inspected < phase_count/2 are auto-voided.
  Fabricated frame observations (templated, no specifics) are auto-voided.
```

**Producer validation** (you, the orchestrator):
1. Parse STAGE_RESULT. Confirm `status: success` and `ready_for_qa: true`.
2. Spot-check: open the self_qa_report.md and look at any 1 frame entry.
   Does the observation describe something specific (a defect or a clean
   element) or is it vague ("frame looks fine")? Vague = void; re-spawn.
3. Record paths via `lesson_cache.record_stage_result`.
4. On `MISSING_CHOREO` → re-spawn Step 4.5 with the missing layout note.
5. On `RENDER_FAILURE` → re-spawn this step with the traceback.
6. On second failure of any kind → PRODUCTION HOLD.

---

## [SUPERVISED CHECKPOINT C] — Post-render preview
**Active only when `SUPERVISED=true`. Skip entirely when `SUPERVISED=false`.**

The silent MP4 is ready. Pause so the human can watch the animation before
locking in the narration track.

1. Print:
   ```
   ══ SUPERVISED CHECKPOINT C — Post-Render Preview ═══════════════════════
   Silent render complete.

     Scene file : [scene_py path]
     Silent MP4 : [silent_mp4 path]

   Open the MP4 and review the animation. Then tell me how to proceed:
     • "proceed"            — continue to narration synthesis
     • describe any fixes   — I'll apply them to the scene, re-render, then
                              ask again (note: re-renders take ~30 min)
     • "abort"              — stop without recording a PRODUCTION HOLD
   ════════════════════════════════════════════════════════════════════════
   ```

2. **Wait for the human's reply.**

3. Response handling:
   - `"proceed"` → continue to Step 8 (Gate 3 Voice & BGM).
   - Fix description → apply the described changes to `[lesson_id]_concept.py`
     (and to choreo.md / plan.md if the fix has planning implications). After
     editing, re-run the Codex scene render step (Step 7b) with a supplemental
     brief note describing the fix. Record the new silent MP4 path, then
     re-display this checkpoint banner and wait again.
   - `"abort"` → stop. Do not write to SESSION_LOG.

---

## Step 8 — Gate 3: Voice & BGM Agent

**Vendor: OpenAI (Codex / GPT-5).** Bounded narration generation aligned to
phase timestamps.

1. Fill brief template:
   ```bash
   sed "s/{LESSON_ID}/[lesson_id]/g" \
     manim_service/pipeline/codex_briefs/voice_bgm.md \
     > manim_service/concept_videos/[lesson_id]_codex_brief_voice_bgm.md
   ```
2. Dispatch:
   ```bash
   bash manim_service/pipeline/codex_render.sh \
     --lesson-id [lesson_id] --stage voice_bgm \
     --brief manim_service/concept_videos/[lesson_id]_codex_brief_voice_bgm.md \
     --result manim_service/concept_videos/[lesson_id]_voice_bgm_result.md
   ```
3. Confirm `status: success`, `narration_path` and `audio_brief_path` exist.

---

## Step 8.5 — Narration synthesis + mux (run directly — NOT via Codex)

`manim_service/audio/synthesize.py` carries a `com.apple.provenance` macOS xattr
that blocks Codex's sandboxed process from reading it. Run the synthesis **directly**
from the Claude Code Bash tool (which is not subject to that sandbox):

```bash
/Users/ultramarine/.venvs/manim/bin/python -m manim_service.audio.synthesize \
  --narration manim_service/concept_videos/[lesson_id]_narration_script.md \
  --silent-mp4 backend/media/concept_videos/[lesson_id]_concept.mp4 \
  --output    backend/media/concept_videos/[lesson_id]_concept_narrated.mp4 \
  --lesson-id [lesson_id]
```

After it finishes, read `audio_report.json` for "extends past video end" warnings:
```python
import json
d = json.load(open("backend/media/concept_videos/[lesson_id]_concept_narrated.audio_report.json"))
warns = [l for l in d.get("lines",[]) if any("extends past" in w for w in l.get("warnings",[]))]
print(f"{len(warns)} overrun lines; video_duration={d.get('video_duration_seconds')}s")
```
If overrun lines > 0: content-density mismatch → route back to Script Writer (Step 4).
On synthesis error: inspect stderr; fix the narration script and retry once.

Record `narrated_mp4` and `audio_report` paths. Update pipeline state:
```bash
... pipeline_state set-artifact [lesson_id] narrated_mp4 backend/media/concept_videos/[lesson_id]_concept_narrated.mp4

---

## Step 9 — Gate 4: Transcript Writer

**Vendor: OpenAI (Codex / GPT-5).** Mechanical SRT/VTT generation from
narration; can run in **parallel** with Step 8.5 (narration mux) since both
depend only on Step 8's narration_script.md.

1. Fill brief template:
   ```bash
   sed "s/{LESSON_ID}/[lesson_id]/g" \
     manim_service/pipeline/codex_briefs/transcript.md \
     > manim_service/concept_videos/[lesson_id]_codex_brief_transcript.md
   ```
2. Dispatch:
   ```bash
   bash manim_service/pipeline/codex_render.sh \
     --lesson-id [lesson_id] --stage transcript \
     --brief manim_service/concept_videos/[lesson_id]_codex_brief_transcript.md \
     --result manim_service/concept_videos/[lesson_id]_transcript_result.md
   ```
3. Read STAGE_RESULT. If `flagged_gaps > 0`: gaps are audio-only content the
   deaf viewer would miss — route back to Step 4 (Script Writer) with the
   gap list. On second flagged-gaps result: PRODUCTION HOLD.

### Parallelization
Steps 8.5 (narration mux) and 9 (transcript) can run concurrently. Start
both in parallel after Step 8 succeeds; join before Step 10 (QA needs the
narrated MP4).

---

## Step 10 — Gate 5: QA Agent

**⚠️ MANIM IS A BLANK CANVAS.** Code that compiles and renders successfully can
still produce overlapping panels, double-rendered equations, stale visuals
from earlier phases, and incoherent layouts. The QA agent MUST extract frames
from the rendered MP4 and visually inspect them. Text-only inference is fraud.

Spawn an Agent with **opus** (visual judgment requires the stronger model):
```
description: "QA Agent — [lesson_id] (attempt N)"
subagent_type: claude
model: opus
prompt: |
  You are the QA Agent. Read your skill at: ~/.claude/skills/qa-agent/SKILL.md

  **VERIFIER MODE (2026-05-28).** You no longer discover defects from scratch.
  The Manim Expert ran Self-QA Phase 0 and wrote a self_qa_report.md
  inspecting all strategic frames. Your job is to verify their report against
  the actual pixels by spot-checking 5 frames.

  Task: Gate 5 verifier review.
  lesson_id: [lesson_id]
  manifest_path: manim_service/pipeline/cache/[lesson_id]/manifest.json
  self_qa_report_path: manim_service/concept_videos/[lesson_id]_self_qa_report.md
  attempt: N (of 2 allowed)

  Read the manifest. From it fetch:
  - artifacts['narrated_mp4'], artifacts['phase_timestamps'], artifacts['choreo']
  - artifacts['scene'], artifacts['narration_script'], artifacts['captions_srt']
  - artifacts['common_defects'] — the dossier you reference for known defect classes

  Phase 0 (verifier flow):
  1. Read self_qa_report.md. Validate structure: ≥ phase_count/2 frames
     inspected, observations are specific (not templated). If invalid →
     REJECT with cause FABRICATED_SELF_QA.
  2. Compute spot-check subset:
     ```
     python -m manim_service.pipeline.frame_selector \
       --lesson-id [lesson_id] \
       --phase-timestamps <path> --choreo <path> \
       --spot-check 5
     ```
  3. Extract those 5 frames via ffmpeg into /tmp/qa_spot_[lesson_id]/.
  4. Read each PNG with the Read tool. Compare your observation to the
     Manim Expert's observation of the same timestamp in their report.
  5. Apply COMMON_DEFECTS.md checks to each spot-check frame.

  Verdict:
  - APPROVED — all 5 spot-checks agree with self_qa_report; no new defects.
  - REJECTED (cause: SELF_QA_DISAGREEMENT) — your spot-check contradicts
    the Manim Expert. Cite frame ts + their observation vs yours.
  - REJECTED (cause: NEW_DEFECT_FOUND) — defect not in dossier. Append to
    COMMON_DEFECTS.md as a new RC-N so future renders catch it.
  - REJECTED (cause: FABRICATED_SELF_QA) — self_qa_report invalid.

  Tag every defect PATCH or STRUCTURAL. PATCH-class routes back to Manim
  Expert for surgical Edit + re-render only. STRUCTURAL routes back to
  earlier stages.

  Then apply the source-code checks (A1-A10), audio sync (B11-B20), and
  content density (C21-C27) from the rest of the skill checklist. These
  use Read on scene.py + narration_script.md — not the MP4.

  Report STAGE_RESULT in your reply (paths only; full report on disk):
  ```
  STAGE_RESULT
  stage: gate5_qa
  verdict: APPROVED | REJECTED
  cause: NONE | FABRICATED_SELF_QA | SELF_QA_DISAGREEMENT | NEW_DEFECT_FOUND
  defect_class: NONE | PATCH | STRUCTURAL
  review_path: manim_service/concept_videos/[lesson_id]_qa_review.md
  frames_spot_checked: 5
  ```
```

**Producer validation:**
1. Parse `verdict` and `defect_class`.
2. `APPROVED` → mark Gate 5 [✓], proceed.
3. `REJECTED PATCH` → re-spawn Step 7 (Manim Expert) with the qa_review.md
   as input; Manim Expert applies Edit + re-renders. NO upstream re-spawn.
4. `REJECTED STRUCTURAL` (first time) → re-spawn Step 7 with the full defect
   list. Manim Expert reruns the 3-phase workflow.
5. `REJECTED FABRICATED_SELF_QA` → re-spawn Step 7 — Manim Expert must
   actually inspect frames. This is a process failure, log to SESSION_LOG.
6. Second REJECTED of any kind → PRODUCTION HOLD.

---

## Step 11 — Gate 6: Series Continuity Agent

**Vendor: OpenAI (Codex / GPT-5).** Multimodal frame comparison vs the
immediate predecessor. Can run in **parallel** with Step 12 (RL Expert Gate 7).

1. Fill brief template:
   ```bash
   sed "s/{LESSON_ID}/[lesson_id]/g" \
     manim_service/pipeline/codex_briefs/continuity.md \
     > manim_service/concept_videos/[lesson_id]_codex_brief_continuity.md
   ```
2. Dispatch:
   ```bash
   bash manim_service/pipeline/codex_render.sh \
     --lesson-id [lesson_id] --stage continuity \
     --brief manim_service/concept_videos/[lesson_id]_codex_brief_continuity.md \
     --result manim_service/concept_videos/[lesson_id]_continuity_result.md
   ```
3. Parse `verdict:` from STAGE_RESULT. Confirm `frames_compared_count ≥ 8`
   (4 this video + 4 predecessor). If less, the report is void; re-spawn.

### Parallelization
Spawn Step 11 and Step 12 concurrently. Both depend only on the narrated MP4
and Gate-5 approval. Join before Step 13 (Producer needs both verdicts).

---

## Step 12 — Gate 7: RL Expert final sign-off

**Vendor: Claude (Sonnet).** Academic verification with frame inspection at
equation-display + numerical-claim phases.

Spawn:
```
description: "RL Expert final review — [lesson_id]"
subagent_type: claude
model: sonnet
prompt: |
  You are the RL Expert. Read your skill: ~/.claude/skills/rl-expert/SKILL.md

  Task: Gate 7 final sign-off on the rendered+narrated artifact.
  lesson_id: [lesson_id]
  manifest_path: manim_service/pipeline/cache/[lesson_id]/manifest.json

  Read the manifest. From it fetch artifacts['specs'], artifacts['plan'],
  artifacts['choreo'], artifacts['narration_script'], artifacts['narrated_mp4'],
  artifacts['phase_timestamps'], artifacts['tv_canonical'],
  artifacts['rl_knowledge_base']. Do NOT expect content pasted into this prompt.

  Note: plan.md was approved at Gate 1 against the teaching spec. This review
  checks whether the rendered scene faithfully implements them, or whether
  the Manim Expert introduced misconceptions during production.

  Follow the 5-step review protocol.

  **Frame inspection (required):** use frame_selector with --spot-check 4 to
  get 4 frames focused on eq_diss / boxed phases. Extract via ffmpeg, Read
  each PNG. Verify on-screen equation forms and numerical values match S&B
  and tv_canonical exactly.

  STAGE_RESULT:
  ```
  STAGE_RESULT
  stage: gate7_rl_final
  verdict: APPROVED | REJECTED
  review_path: manim_service/concept_videos/[lesson_id]_rl_expert_final.md
  frames_inspected: <int — must be ≥ 4>
  ```
```

- `APPROVED` → mark Gate 7 [✓], proceed to Checkpoint D (or directly to Step 13 in auto mode).
- `REJECTED` → re-issue the Step 7 Codex `scene_render` handoff with RL Expert
  corrections appended to the brief, re-run Step 8.5 (narrate_mux) and
  Gates 5–6, then re-spawn this step. On second rejection, place on PRODUCTION HOLD.

---

## [SUPERVISED CHECKPOINT D] — Final go/no-go
**Active only when `SUPERVISED=true`. Skip entirely when `SUPERVISED=false`.**

All 7 pipeline gates are open. This is the final human sign-off before the
video is registered in the library and the 720p render is triggered.

1. Print:
   ```
   ══ SUPERVISED CHECKPOINT D — Final Go/No-Go ════════════════════════════
   All 7 gates are open. Ready to register in the library.

   Gate summary:
     Gate 1  RL Expert plan          ✓ APPROVED
     Gate 2  Technical Validator     ✓ PASS
     Gate 3  Voice & BGM             ✓ DELIVERED
     Gate 4  Transcript Writer       ✓ DELIVERED
     Gate 5  QA Agent                ✓ APPROVED  (attempt [N] of 2)
     Gate 6  Series Continuity       ✓ CONSISTENT
     Gate 7  RL Expert final         ✓ APPROVED

   Artifacts:
     Scene      : manim_service/concept_videos/[lesson_id]_concept.py
     Narrated   : backend/media/concept_videos/[lesson_id]_concept_narrated.mp4
     Duration   : [duration from audio_report]
     Captions   : [lesson_id]_captions.srt / .vtt

   Tell me how to proceed:
     • "approve"            — register in library, trigger 720p render, close pipeline
     • describe any notes   — I'll append them to the SESSION_LOG entry (no re-work)
     • "hold"               — record PRODUCTION HOLD in SESSION_LOG and stop
   ════════════════════════════════════════════════════════════════════════
   ```

2. **Wait for the human's reply.**

3. Response handling:
   - `"approve"` → continue to Step 13 (Gate 8 Producer approval).
   - Notes description (e.g. "add a note about X") → incorporate the note into
     the SESSION_LOG entry that will be written at Step 15; confirm with the
     human, then continue to Step 13.
   - `"hold"` → append a `PRODUCTION HOLD — [lesson_id]` entry to SESSION_LOG.md
     (with the human's reason if provided) and stop. The pipeline can be resumed
     later by running `/project:produce-video lesson_id=[lesson_id] mode=supervised`
     after the hold condition is resolved.

---

## Step 13 — Gate 8: Producer library approval

**Vendor: Claude (Sonnet) — the orchestrator IS the Producer.** No separate
agent spawn needed except the minor worker.py registration edit.

1. Confirm all 7 prior gates are marked [✓] in the manifest's stage_results.
2. Confirm `lesson_id` is in `backend/concept_videos/specs.py` for app
   compatibility. If absent, spawn a Sonnet agent to add a `LessonVideoSpec`
   entry using the app metadata proposal in `[lesson_id]_specs.md`.
3. Check `CONCEPT_VIDEO_SCENES` in `manim_service/jobs/worker.py`. If not registered:
   ```
   description: "Register scene in CONCEPT_VIDEO_SCENES — [lesson_id]"
   subagent_type: claude
   model: sonnet
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
5. Confirm file inventory exists (the manifest's artifact paths resolve):
   ```python
   from manim_service.pipeline.lesson_cache import read_manifest, absolute
   m = read_manifest("[lesson_id]")
   missing = [k for k in m.artifacts if not absolute("[lesson_id]", k).exists()]
   assert not missing, f"Missing artifacts: {missing}"
   ```
6. Confirm the per-stage result files all written:
   - `[lesson_id]_specs.md`, `[lesson_id]_plan.md`, `[lesson_id]_choreo.md`
   - `[lesson_id]_tv_canonical.md`, `[lesson_id]_gate1_result.md`,
     `[lesson_id]_tech_validate_result.md`
   - `[lesson_id]_self_qa_report.md` (Manim Expert), `[lesson_id]_qa_review.md` (Gate 5)
   - `[lesson_id]_continuity_result.md`, `[lesson_id]_rl_expert_final.md`
   - `[lesson_id]_voice_bgm_result.md`, `[lesson_id]_transcript_result.md`
   - silent + narrated MP4s, audio_report.json, .srt, .vtt

6. Record final gate state:
   ```bash
   ... pipeline_state set-gate [lesson_id] g8_producer pass
   ```

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
**Supervised checkpoints cleared:** [A / B / C / D — list which ones ran with edits, or "N/A (auto mode)"]
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
| Invalid mode value | Stop. Print PRODUCER REJECTION with valid options. |
| lesson_id already in library | Stop. Report library status. |
| lesson_id on PRODUCTION HOLD | Stop. Direct to human review. |
| Agent rejects twice at same gate | Escalate: re-spawn upstream agent with diagnosis. |
| Agent rejects three times | Append PRODUCTION HOLD to SESSION_LOG. Stop. |
| Supervised checkpoint: "abort" | Stop immediately. Do NOT write PRODUCTION HOLD. |
| Supervised checkpoint: "hold" (D only) | Append PRODUCTION HOLD to SESSION_LOG. Stop. |
| Checkpoint C fix causes plan change | Re-run Gates 1–2 before re-rendering if plan.md changed. |
| Skill drift at preflight | `bash manim_service/pipeline/check_skill_canon.sh --repair`, then re-verify. |
| Codex handoff: no result file | Re-run `codex_render.sh` for the same stage once; then PRODUCTION HOLD. |
| Codex handoff: `status: failed` | Read `errors:` in the result; route fix per CODEX_HANDOFF.md §8. |
| Codex handoff: `MISSING_CHOREO` | Re-spawn Visual Director (Step 4.5), regenerate choreo.md, re-issue brief. |
| Codex handoff stuck `codex_running` | Crash/timeout — re-run `codex_render.sh` for that stage. |
| Codex CLI not found | Default path: `/opt/homebrew/bin/codex`. Override with `CODEX_BIN` env var. Fallback: `/Applications/Codex.app/Contents/Resources/codex`. See codex_render.sh. |
| Narration "extends past video end" | Content-density mismatch → Script Writer (Step 4), not a truncation. |
| Worker 404 at render | Register scene via agent spawn. Re-trigger render. |
| Render fails (non-404) | Report. Pipeline stays complete; render is a retry. |
| manim_service unreachable | Start with: uvicorn manim_service.api.main:app --host 0.0.0.0 --port 8200 |
