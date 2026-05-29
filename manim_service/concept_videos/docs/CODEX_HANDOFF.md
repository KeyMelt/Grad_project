# Codex Handoff Protocol

How the RL concept-video pipeline splits work between **Claude Code** (the
reasoning/orchestration runtime) and **Codex / GPT-5.5** (the heavy execution
runtime) to keep production sustainable — small context windows, lower token
cost, and autonomous rendering.

Read this alongside:
- `manim_service/pipeline/SKILL_OWNERSHIP.md` — which runtime owns each skill
- `.claude/commands/produce-video.md` — the orchestrator that drives this
- `manim_service/concept_videos/docs/STYLE_BIBLE.md` — the quality standard

---

## 1. Why split

Running the whole 8-gate pipeline in one agent's context exhausts the window
(SESSION_LOG.md ~56 KB, plan.md ~37 KB, choreo.md ~44 KB, generated scene
30–40 KB) and burns tokens on code generation — the task Claude is least
cost-effective at. The fix: Claude does the reasoning gates; Codex does the two
heavy execution stages, on the same filesystem, communicating through
on-disk briefs and result files.

## 2. Division of labour

| Stage | Runtime | Produces |
|---|---|---|
| RL Expert spec, plan.md, choreo.md | Claude Code | `*_specs.md`, `*_plan.md`, `*_choreo.md` |
| Gate 1 (RL Expert), Gate 2 (Tech Validator) | Claude Code | gate verdicts |
| **Stage A — scene_render** | **Codex** | `*_concept.py`, silent 480p15 MP4 |
| Voice & BGM narration script | Claude Code | `*_narration_script.md`, `*_audio_brief.md` |
| **Stage B — narrate_mux** | **Codex** | narrated MP4 + `*_concept_narrated.audio_report.json` |
| Gate 4 transcript, Gate 5 QA, Gate 6 continuity, Gate 7 RL Expert | Claude Code | gate verdicts, captions |
| Gate 8 Producer + final 720p render trigger | Claude Code | library approval |

Codex owns code generation and shell execution (manim, kokoro, ffmpeg). Claude
owns RL correctness, creative writing, and quality judgment.

## 3. The two Codex stages

### Stage A — `scene_render`
**Precondition:** Gate 2 (Technical Validator) PASS.
**Inputs:** `{lesson_id}_plan.md`, `{lesson_id}_choreo.md`, STYLE_BIBLE.
**Work:**
1. Generate the Manim scene to `manim_service/concept_videos/{lesson_id}_concept.py`
   using the `manim-rl-animation-style-lock` skill (implement every choreo.md row).
2. Render dev quality:
   `/Users/ultramarine/.venvs/manim/bin/python -m manim -ql {scene}.py {SceneClass}`
3. Confirm the silent MP4 exists.

### Stage B — `narrate_mux`
**Precondition:** Voice & BGM `narration_script.md` written.
**Inputs:** `{lesson_id}_narration_script.md`, the silent MP4.
**Work:**
```bash
/Users/ultramarine/.venvs/manim/bin/python -m manim_service.audio.synthesize \
  --narration manim_service/concept_videos/{lesson_id}_narration_script.md \
  --silent-mp4 backend/media/concept_videos/{lesson_id}_concept.mp4 \
  --output    backend/media/concept_videos/{lesson_id}_concept_narrated.mp4 \
  --lesson-id {lesson_id} [--phase-timestamps <path>]
```
Read the `audio_report.json` `lines[].warnings`; surface "extends past video
end" rather than truncating.

## 4. Invocation

The orchestrator never calls `codex` directly. It writes a brief, then runs:

```bash
manim_service/pipeline/codex_render.sh \
  --lesson-id {lesson_id} \
  --stage     scene_render \
  --brief     manim_service/concept_videos/{lesson_id}_codex_brief.md \
  --result    manim_service/concept_videos/{lesson_id}_codex_result.md
```

`codex_render.sh` runs `codex exec --cd <repo> --sandbox danger-full-access
--output-last-message <result>` and maintains `pipeline_state.json` (handoff
status `codex_running` → `codex_done`/`codex_failed`, owner toggling).

## 5. Brief format (Claude writes, Codex reads)

A brief is a self-contained Markdown file at
`manim_service/concept_videos/{lesson_id}_codex_brief.md`. It must be compact —
point to documents on disk by path rather than pasting them. Required sections:

```markdown
# Codex Brief — {lesson_id} — stage: {scene_render|narrate_mux}

## Identity
- lesson_id: {lesson_id}
- manim_class: {SceneClassName}
- stage: {scene_render | narrate_mux}

## Inputs (read these from disk)
- plan.md:    manim_service/concept_videos/{lesson_id}_plan.md
- choreo.md:  manim_service/concept_videos/{lesson_id}_choreo.md
- style:      manim_service/concept_videos/docs/STYLE_BIBLE.md
- (narrate_mux only) narration: manim_service/concept_videos/{lesson_id}_narration_script.md
- (narrate_mux only) silent_mp4: backend/media/concept_videos/{lesson_id}_concept.mp4

## Gate context
- Gate 1 RL Expert: PASS
- Gate 2 Tech Validator: PASS
- Tech Validator notes (one line each, or "none"): ...

## Task
{exact steps for this stage — see §3}

## Constraints
- python: /Users/ultramarine/.venvs/manim/bin/python
- render quality: -ql (480p15 dev)
- Implement every choreo.md row; do not improvise layout. If a layout detail is
  missing from choreo.md, STOP and report MISSING_CHOREO rather than guessing.

## Result format
End your run by writing ONLY this block as your final message:

    STAGE_RESULT
    stage: {scene_render|narrate_mux}
    status: {success|failed}
    scene_py: {path or "-"}
    silent_mp4: {path or "-"}
    narrated_mp4: {path or "-"}
    audio_report: {path or "-"}
    render_seconds: {int or "-"}
    animations: {int or "-"}
    errors: {short description or "none"}
```

## 6. Result format (Codex writes, Claude reads)

Codex's final message — captured to `{lesson_id}_codex_result.md` by
`--output-last-message` — is the `STAGE_RESULT` block above. The orchestrator
parses it to decide whether to advance the gate or re-issue the brief. Treat a
missing or `status: failed` result as a stage failure; inspect
`pipeline_state.json` `handoff.status` to disambiguate a crash
(`codex_running` left dangling) from a clean failure (`codex_failed`).

## 7. State checkpoint

`manim_service/concept_videos/{lesson_id}_pipeline_state.json` is the
machine-readable resume point (schema and CLI in
`manim_service/pipeline/pipeline_state.py`). Either runtime can read it to learn
which gates are open and whether a handoff is in flight, without parsing
SESSION_LOG.md. SESSION_LOG.md remains the human audit trail and is still
written at Gate 8.

## 8. Failure handling

| Symptom | Meaning | Orchestrator action |
|---|---|---|
| no result file | Codex never produced a final message | treat as failed; re-issue brief once |
| `status: failed` | Codex hit an error it reported | read `errors:`; route fix (codegen → re-brief Stage A; missing choreo → Visual Director) |
| `MISSING_CHOREO` | choreo.md lacked a needed layout | re-spawn Visual Director, regenerate choreo, re-brief |
| handoff stuck `codex_running` | crash / timeout | re-run `codex_render.sh` for the same stage |
| audio "extends past video end" | narration longer than silent video | content-density mismatch → Script Writer, not a truncation |
| `com.apple.provenance` / `Operation not permitted` on `manim_service/audio/synthesize.py` | macOS security xattr blocks Codex sandbox read | run synthesis directly via Claude Code Bash tool — it is NOT sandboxed this way |

## 9. Drift guard

Before a production run, the orchestrator runs
`manim_service/pipeline/check_skill_canon.sh` to confirm Claude's skill symlinks
still resolve to the canonical Codex copies. `--repair` fixes any fork.
