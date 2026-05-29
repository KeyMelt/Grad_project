# Codex Brief — rl_mdp_core — stage: scene_render (v3 — QA fix pass)

## Identity
- lesson_id: rl_mdp_core
- manim_class: RLMDPCoreConcept
- stage: scene_render
- date: 2026-05-24

## Context
Gate 5 QA REJECTED the rendered video with SIX blocking visual-layer defects.
The content, narration sync, Gymnasium sprites, timing, and RL correctness all
PASS — do NOT change those. This is a targeted LAYOUT / SCALING / CLEANUP fix
pass on the existing scene. Fix exactly the six defects below and nothing else.

## HARD CONSTRAINTS (must not break)
- DO NOT change any `self.hold_until(...)` call or its target value. There are 16
  of them (one per phase). They pin the video to the narration timeline
  (total 1014.067 s, matched exactly). Preserve all of them verbatim.
- DO NOT change phase order, `mark_phase` names, equations' content/colors, the
  narration, or the choreo intent. Total video duration must stay ≈1014 s
  (hold_until makes this self-correcting, so just don't remove the calls).
- DO NOT reintroduce colored-rectangle FrozenLake tiles — keep the Gymnasium PNG
  sprites.

## Inputs (read from disk)
- existing scene: manim_service/concept_videos/rl_mdp_core_concept.py  (EDIT IN PLACE)
- choreo:         manim_service/concept_videos/rl_mdp_core_choreo.md  (layout regions: §16 hemispheres)
- style:          manim_service/concept_videos/docs/STYLE_BIBLE.md  (§16 layout, §23 lifecycle, §33 equation framing)
- helpers:        manim_service/scenes/panels.py

## The six defects to fix (verbatim from QA, with file lines)

### QA-1 (BLOCKER, §33.2/§29.1) — Full-screen solo equations are clipped off BOTH edges
- Phase 7 p-equation solo (~321–365 s) and Phase 12 G_t solo (~652–712 s).
- Cause: equation built at font_size=48 (already wide) then `zoom_to(self, eq, scale=0.55)`
  magnifies it so its ends fall outside the 480p frame. The clipping persists the whole hold.
- Lines: ~400 `zoom_to(self, self.p_eq_full, scale=0.55…)` and ~559 `zoom_to(self, self.gt_sum, scale=0.55…)`.
- FIX: Do NOT zoom IN on a wide equation. Remove those two `zoom_to` calls (and any
  paired `zoom_reset` that belongs to them). Instead guarantee the WHOLE equation fits
  on screen with margins: after building the equation centered, call
  `eq.scale_to_fit_width(config.frame_width * 0.9)` if its width exceeds that, keeping it
  centered. The equation must be FULLY visible (both ends inside frame) for the entire
  solo hold, at the largest size that still fits (must remain clearly legible at 480p —
  do not shrink below the equivalent of ~36 pt visual height).

### QA-2 (BLOCKER, §16.2) — LEFT-panel equation overruns left edge AND into center grid
- Phases 8–14 (~365–887 s). After repositioning to `LEFT*4.15`, `p_eq_full` (then `gt_sum`)
  is too wide for the LEFT hemisphere (−5.0..−1.5 x): left tokens go off-screen, right tokens
  collide with the CENTER grid.
- Lines: ~420 `smooth_move_to(self.p_eq_full, LEFT*4.15 + UP*0.85)`, ~574 `smooth_move_to(self.gt_sum, LEFT*4.15 + UP*0.8)`.
- FIX: The full forms (`p(s',r|s,a) ≐ Pr{…}` and the infinite-sum `G_t`) are too long for a
  side panel. In the 3-panel synthesis phases, show the COMPACT form in the LEFT panel:
  `p(s',r\mid s,a)` for phases 8–11, and `G_t = \sum_{k} \gamma^k R_{t+k+1}` (or
  `G_t = R_{t+1} + \gamma G_{t+1}` once derived) for phases 13–14. Build a compact MathTex,
  `scale_to_fit_width` it to ≤ 3.0 units (LEFT hemisphere width budget), and place it at the
  LEFT with ≥0.18 clearance from the grid. Keep the same token colors (STATE/REWARD/ACTION/VALUE).
  The full form is only required during its own full-screen solo reveal (QA-1), not in the panel.

### QA-3 (BLOCKER, §16.3) — Three outcome-branch labels collide with each other and the grid
- Phases 8–10 (~365–594 s). Labels "1/3, r=0, done=False/True" overlap each other and grid cells 6/7/10.
- Lines: ~226–232 (`_make_branch`) and ~426–431.
- FIX: Shorten each label to a single short token, e.g. `p=1/3 → s'=2`, `p=1/3 → s'=7 (hole)`,
  `p=1/3 → s'=10`. Position each label clear of the grid (≥0.18 buff) and clear of the other two
  (stack them vertically in a dedicated column to the RIGHT of the grid, or at the branch arrow tips
  with no mutual overlap). No two labels may share screen region.

### QA-4 (BLOCKER, §16.3) — CodeStepper panel occludes the header and the grid top edge
- Phase 10 (~503–594 s). Code panel at top-right covers part of the header and overlaps the grid.
- Lines: ~471–475 (`CodeStepper(..., width=5.4…)`, `place_top_right_panel(...)`).
- FIX: Place the code panel BELOW the header band (top of panel ≤ header bottom − 0.2) and clear of
  the grid (left edge of panel ≥ grid right edge + 0.18). Shrink width if needed (e.g. 4.6). Zero
  overlap with header or grid.

### QA-5 (BLOCKER, §23) — Stale empty orange-bordered rectangle persists ~380 s incl. final hold
- Appears ~Phase 11 (~630 s) and stays to scene end. It is the CodeStepper's outer stroke/frame:
  `FadeOut(self.code.panel)` (line ~499) removes the fill but not the whole CodeStepper group.
- FIX: FadeOut the ENTIRE CodeStepper mobject group (the object returned by `CodeStepper(...)`, e.g.
  `self.code` and all its sub-mobjects — panel, frame/stroke, title, code lines, highlight rect), not
  just `.panel`. Do this at the Phase 11 entry, before the normalization equation appears. After that,
  confirm the canvas contains only header + the active equation/grid for every phase ≥ 11. The final
  frame (Phase 16) must contain only the intended takeaway/forward-tease + LEFT recursion eq + dimmed
  grid — NO orphan rectangle.

### QA-6 (BLOCKER, §16.3/§33.2) — Return-recursion equation drawn on top of the grid, illegible
- Phase 15 (~887–953 s). `G_t = R_{t+1} + γG_{t+1}` is morphed at ORIGIN over the grid at SECONDARY
  opacity; grid sprites bleed through. (Naming is correct — keep "return recursion", never "Bellman".)
- Lines: ~653–666 (recursion morph at ORIGIN over grid; grid only dimmed) and ~670 (reposition only in Phase 16).
- FIX: At the recursion payoff, FadeOut (or fully clear) the grid FIRST, then present
  `G_t = R_{t+1} + \gamma G_{t+1}` centered at PRIMARY opacity (font≥48, fully on screen) and hold it
  for its window. It is the most important identity in the video — it must be crisp and unobstructed.

## Task
1. Apply the six fixes above to manim_service/concept_videos/rl_mdp_core_concept.py.
2. Keep all 16 `self.hold_until(...)` calls and targets unchanged.
3. Re-render: /Users/ultramarine/.venvs/manim/bin/python -m manim -ql manim_service/concept_videos/rl_mdp_core_concept.py RLMDPCoreConcept
4. Confirm media/videos/rl_mdp_core_concept/480p15/phase_timestamps.json total ≈ 1014 s (±3 s) and the silent MP4 exists.
5. Sanity-check your own fixes by extracting frames at 345, 410, 550, 690, 920, 1010 s and confirming:
   - 345 s and 690 s: the WHOLE equation is on screen (no clipping).
   - 410/550 s: branch labels and code panel do not overlap header/grid/each other.
   - 920 s: recursion equation is on a clear background, fully legible.
   - 1010 s: no orphan rectangle anywhere on the final frame.

## Result format
End your run by writing ONLY this block as your final message:

    STAGE_RESULT
    stage: scene_render
    status: success
    scene_py: manim_service/concept_videos/rl_mdp_core_concept.py
    silent_mp4: media/videos/rl_mdp_core_concept/480p15/RLMDPCoreConcept.mp4
    narrated_mp4: -
    audio_report: -
    render_seconds: <int>
    animations: <int>
    errors: none

If any fix cannot be done without changing timing or content, use status: failed and explain in errors:.
