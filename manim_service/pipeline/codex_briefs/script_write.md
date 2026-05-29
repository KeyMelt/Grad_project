# Codex brief template — stage: script_write

> Template — the orchestrator fills `{LESSON_ID}` and copies this brief to
> `manim_service/concept_videos/{LESSON_ID}_codex_brief_script_write.md`.

## Identity
- lesson_id: {LESSON_ID}
- stage: script_write
- vendor: OpenAI (Codex / GPT-5)
- role: **Script Writer** — produces the canonical plan.md beat sheet

## Inputs (read by filesystem — DO NOT inline these into your reply)
1. Manifest: `manim_service/pipeline/cache/{LESSON_ID}/manifest.json` — read this first.
2. From the manifest's `artifacts` map, read:
   - `specs` — RL Expert teaching brief
   - `style_bible` — STYLE_BIBLE.md
   - `common_defects` — COMMON_DEFECTS.md (so you do not author defects in)
   - `rl_knowledge_base` — series-wide concept DAG

## Task
Author a complete plan.md following the script-writer skill's 3-phase workflow:
Pedagogical Architect → Code Agent → Pacing Linter.

Write the file to `{LESSON_ID}_plan.md` (resolve via manifest['artifacts']['plan']).

## Length policy
Quality over brevity. Content depth determines length. Hard cap 30 minutes; no
floor. Underrunning a concept the spec demands is a defect.

## STYLE_BIBLE §34 / §35 awareness
For any code-walkthrough phase, the plan must declare a TWO-panel layout
(env LEFT + IDE code RIGHT, NO third panel) and step-through cadence.
For any equation-dissection phase, the plan must declare TOKEN-by-TOKEN with
env anchor. Mixed phases are unauthorable — escalate.

## Result format

End your run by writing ONLY this block as your final message:

    STAGE_RESULT
    stage: script_write
    status: {success|failed}
    plan_path: <absolute path to the plan.md you wrote>
    flag_list: <brief bullet flags or "none">
    errors: <short description or "none">

The Producer reads `plan_path` from this block and routes it onward.
