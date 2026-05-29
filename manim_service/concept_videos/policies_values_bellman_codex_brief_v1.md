# Codex brief — policies_values_bellman / stage: scene_render

## Identity
- lesson_id: `policies_values_bellman`
- manim_class: `PoliciesValuesBellmanConcept`
- stage: `scene_render`
- Series position: V-02 of restructured curriculum (successor to V-01 `rl_mdp_core`)

## Inputs (read these — do NOT inline their content into your scratch)
- Plan: `manim_service/concept_videos/policies_values_bellman_plan.md` (1774 lines, Script-Writer authored)
- Choreo: `manim_service/concept_videos/policies_values_bellman_choreo.md` (611 lines, Visual-Director authored)
- Teaching spec: `manim_service/concept_videos/policies_values_bellman_specs.md` (1161 lines, RL Expert authored — reference for context)
- Style Bible: `manim_service/concept_videos/docs/STYLE_BIBLE.md`
- **Canonical numerical values: `manim_service/concept_videos/policies_values_bellman_tv_canonical.md`** — USE THE `v_pi` ARRAY FROM HERE. Do not re-compute, do not guess.

## Reusable helpers (already in repo — import, do NOT duplicate)
- `manim_service/scenes/panels.py` — `BaseConceptScene`, `place_left_panel`, `place_mid_right_panel`, `place_bottom_right_panel`, `place_top_right_panel`, opacity constants
- `manim_service/scenes/motion.py` — `smooth_move_to`, `ingestion_wait`, `mark_phase`, `hold_until`, `equation_morph`, `trace_vector`, `cross_highlight_pair`
- `manim_service/scenes/rl_visuals.py` — `FrozenLakeGrid`, `ValueHeatmap`, `PolicyArrowGrid`, `ActionValueBarChart`, `BackupDiagram`, `CodeStepper`
- Color constants (locked from V-01): STATE_COLOR=#38BDF8, VALUE_COLOR=#FACC15, REWARD_COLOR=#34D399, POLICY_COLOR=#A78BFA, ACTION_COLOR=#FB923C, PENALTY_COLOR=#F87171, CODE_ACCENT=#64748B, BG_PANEL=#0F172A, BG_GRID=#1E293B

## Gate context
- Gate 1 (RL Expert plan + choreo review): **APPROVED** on first attempt, 2026-05-27. No outstanding concerns. RL Expert flagged: Bellman MUST be derived in 5 steps (S5-P14..S5-P18), two sums kept visually separate, equiprobable π is the working policy, goal cell shows both green +1.0 reward AND yellow v_π=0 simultaneously, CodeStepper output is 0.000000 (intentional V-03 hand-off), closing forward-tease morphs "=" to "←" within ≤1.5 s and reverts.
- Gate 2 (Technical Validator): **PASS** after 2 numerical corrections applied to plan.md / specs.md / choreo.md (state 13: 0.176→0.170; state 14: 0.439→0.434; also 6: 0.041→0.039 and 0.44→0.43 narration). The corrected canonical v_π array is in `policies_values_bellman_tv_canonical.md`. All env API conventions verified live.

## Task
Implement the V-02 Manim scene per the `scene_render` protocol of
`manim_service/concept_videos/docs/CODEX_HANDOFF.md` §3.

1. **Asset check first** (STYLE_BIBLE §31 — see QUALITY MANDATE item 1 below).
2. **Generate the scene** at `manim_service/concept_videos/policies_values_bellman_concept.py`. The class is `PoliciesValuesBellmanConcept(BaseConceptScene)`. Implement every row of every choreo.md table — every Element Lifecycle Matrix entry becomes a FadeIn/FadeOut pair; every Motion Choreography row becomes a `self.play(...)` tagged with its purpose; every Camera Shot becomes a zoom_to/pan_to_follow/zoom_reset; every Sprite-Math Binding becomes a SpriteActionBinding or cross_highlight_pair; every trace_vector pair becomes a `trace_vector(...)` call.
3. **Audio-as-master timing**: every phase boundary defined in plan.md must close with a `self.hold_until(<phase_end_seconds>)` call. The phase end seconds come from the plan.md narration cue map (read it). This is the V-01 lock — do not violate it.
4. **Render**: `/Users/ultramarine/.venvs/manim/bin/python -m manim -ql manim_service/concept_videos/policies_values_bellman_concept.py PoliciesValuesBellmanConcept`. Confirm the silent MP4 is produced under `media/videos/policies_values_bellman_concept/480p15/`.
5. **If a layout detail is missing from choreo.md**, STOP and report `MISSING_CHOREO` rather than improvising. That routes back to the Visual Director.

## Result format

Write the `STAGE_RESULT` block per `manim_service/concept_videos/docs/CODEX_HANDOFF.md` §5 to:
`manim_service/concept_videos/policies_values_bellman_codex_result.md`

Required fields:
- `status: success` | `failed`
- `scene_py:` absolute path
- `silent_mp4:` absolute path
- `duration_seconds:` from manim_log
- `phase_timestamps_json:` absolute path
- `errors:` (only if failed; one of `MISSING_CHOREO`, `MISSING_ASSETS`, `RENDER_FAILURE`, `STYLE_VIOLATION`)
- `quality_checklist_pass:` 20/20 expected

## ⚠️ MANDATORY QUALITY RULES (verbatim from STYLE_BIBLE updates 2026-05-24)

```
QUALITY MANDATE — read before writing a single line of scene code:

1. GYMNASIUM ASSET VERIFICATION (STYLE_BIBLE §31): Run asset check first.
   Any missing asset → report MISSING_ASSETS and STOP. No rectangle fallbacks.

2. FONT SIZES (STYLE_BIBLE §3 updated):
   - Standalone equation (first reveal): font_size=48 minimum
   - Panel equation: font_size=36 minimum
   - All body text: font_size=22 minimum
   - No text below 22pt in the scene — grep every font_size= before submitting

3. EQUATION INTRODUCTION (STYLE_BIBLE §33.2):
   Every equation appearing for the first time MUST:
   a. Be preceded by FadeOut/OPACITY_SECONDARY of all competing elements
   b. Appear centered at font_size≥48 with self.wait(2.0) before adding context

4. PHASE CLEANUP (STYLE_BIBLE §23):
   Every phase transition MUST explicitly FadeOut elements from the prior phase.
   No stale visuals left dimly on screen.

5. SINGLE FOCAL POINT (STYLE_BIBLE §33.1):
   At most ONE object at OPACITY_PRIMARY per frame unless explicitly connected
   by trace_vector or cross_highlight_pair.

6. 20-ITEM QUALITY CHECKLIST: Run all 20 items from the Manim Expert SKILL.md
   Phase 3 Linter before submitting. Items 11–20 are new and mandatory.
```

## V-01 lessons learned (avoid repeating)

From the just-completed `rl_mdp_core` production (5 QA rejections before APPROVED):

- **No hardcoded coordinates.** Use `place_*_panel()` methods + relative `shift()`. Raw `to_edge(...)` / `move_to(np.array([...]))` will be rejected.
- **No GREY_A or any non-palette color.** The 10-color STYLE_BIBLE palette is exhaustive — use `CODE_ACCENT` for muted text.
- **No premature FadeOut.** Per choreo §4 Element Lifecycle Matrix, an element only exits in its declared EXIT phase. Dim to OPACITY_SECONDARY between phases if it must persist.
- **Insert `ingestion_wait(...)` between consecutive morphs** (STYLE_BIBLE §18). Two back-to-back `TransformMatchingTex` calls without an absorption buffer = QA reject.
- **When the focal element changes**, the old focal must drop to OPACITY_SECONDARY in the same `self.play(...)` call that enters the new focal — never leave two PRIMARY elements in different parts of the frame.
- **Camera zooms are expensive.** V-01 ended at 7 shots over 16:54. V-02 choreo allows 8 shots over ~17 min. Do not exceed.
