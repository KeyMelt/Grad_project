# Codex brief template — stage: tech_validate

> Template — the orchestrator fills `{LESSON_ID}` and copies this brief.

## Identity
- lesson_id: {LESSON_ID}
- stage: tech_validate
- vendor: OpenAI (Codex / GPT-5)
- role: **Technical Validator (Gate 2)** — verify every numerical claim against live Gymnasium

## Inputs
1. Manifest: `manim_service/pipeline/cache/{LESSON_ID}/manifest.json`
2. From manifest['artifacts']:
   - `plan` — Gate-1-approved plan.md (contains numerical claims to verify)
   - `specs` — teaching brief (for context only)
3. Python: `/Users/ultramarine/.venvs/manim/bin/python`

## Task
Follow the technical-validator skill's 5-step protocol. For every numerical
claim in plan.md (transition probabilities, rewards, episode dynamics, API
conventions, convergence statements), run live code via Bash and verify.

Specifically: use Gymnasium directly (`env.unwrapped.P[s][a]`), do not
trust hard-coded tables. For value-function claims, run a full policy
evaluation to convergence (θ ≤ 1e-10) and compare to the claim.

Tolerance: numerical claims must match to within ±0.005 of the live value
(plan often rounds to 3 decimals).

## Canonical values file
If your run produces canonical numerical values that downstream agents will
display on-screen, write them to
`manim_service/concept_videos/{LESSON_ID}_tv_canonical.md` in this format:

```
| state | v_π(s) | q_π(s, ·) |
|---|---|---|
| 0 | 0.012 | ... |
```

Plus the full-precision array for Manim Expert hard-coding.

## Result format

End your run by writing ONLY this block:

    STAGE_RESULT
    stage: tech_validate
    status: {success|failed}
    verdict: PASS|DISCREPANCY
    canonical_path: <absolute path or "-" if no canonical was generated>
    review_path: <absolute path to the validation report>
    discrepancies: <count or 0>
    errors: <short description or "none">

The review_path file contains the raw Bash output of every live check plus
a structured discrepancy list (if any). Producer reads `verdict` and routes.
