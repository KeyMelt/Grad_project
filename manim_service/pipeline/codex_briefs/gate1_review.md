# Codex brief template — stage: gate1_review

> Template — the orchestrator fills `{LESSON_ID}` and copies this brief.

## Identity
- lesson_id: {LESSON_ID}
- stage: gate1_review
- vendor: OpenAI (Codex / GPT-5)
- role: **RL Expert Gate 1** — academic sign-off on plan.md + choreo.md

## Inputs (read by filesystem)
1. Manifest: `manim_service/pipeline/cache/{LESSON_ID}/manifest.json`
2. From manifest['artifacts']:
   - `specs` — teaching brief (the authority for scope)
   - `plan` — Script Writer's plan.md (under review)
   - `choreo` — Visual Director's choreo.md (under review)
   - `rl_knowledge_base` — series-wide concept DAG
   - `style_bible` — for §34/§35 sanity checks on choreo

## Task
Follow the rl-expert skill's 5-step review protocol. The plan is REJECTED only if
it contradicts verified RL theory (Sutton & Barto 2018), the teaching spec, the
project lesson sequence, or required app integration. **Do not reject for going
beyond specs.py/platform_contract.**

Additionally verify choreo §1 (Scientific Rigor) and §2 (Pedagogical Strategy):
- Claims correctly scoped (env variant, γ value, policy).
- The pedagogical pattern actually defeats the misconception listed in rl_knowledge_base.md.

## Result format

End your run by writing ONLY this block:

    STAGE_RESULT
    stage: gate1_review
    status: {success|failed}
    verdict: APPROVED|REJECTED
    fault_routing: SCRIPT_WRITER|VISUAL_DIRECTOR|NONE  # only meaningful if REJECTED
    review_path: <absolute path to the review markdown you wrote>
    errors: <short description or "none">

Write the review to `manim_service/concept_videos/{LESSON_ID}_gate1_review.md` —
include S&B citations for any rejection points.
