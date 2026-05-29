# Codex brief — policies_values_bellman / stage: scene_render (V2 — REWRITE after real QA)

## Identity
- lesson_id: `policies_values_bellman`
- manim_class: `PoliciesValuesBellmanConcept`
- stage: `scene_render`
- Series position: V-02
- **This is a rewrite.** The prior render had catastrophic visual defects across 8+ phases. See QA dossier — every defect must be fixed.

## Inputs (read these — do NOT inline content into your scratch)
- Plan: `manim_service/concept_videos/policies_values_bellman_plan.md` (~1774 lines)
- Choreo: `manim_service/concept_videos/policies_values_bellman_choreo.md` (~611 lines)
- Teaching spec: `manim_service/concept_videos/policies_values_bellman_specs.md`
- **Style Bible: `manim_service/concept_videos/docs/STYLE_BIBLE.md`** — **§34 and §35 are MANDATORY new sections (added today)**
- **Canonical numerical values: `manim_service/concept_videos/policies_values_bellman_tv_canonical.md`** — USE the v_pi array from here. Do not re-compute.
- **QA defect dossier: `manim_service/concept_videos/policies_values_bellman_qa_review.md`** — every RC-1..RC-5 must be addressed
- Prior (defective) scene: `manim_service/concept_videos/policies_values_bellman_concept.py` — you may reference its structure but DO NOT carry its bugs forward. Overwrite it.

## Reusable helpers (already in repo)
- `manim_service/scenes/panels.py` — `BaseConceptScene`, `place_left_panel`, `place_mid_right_panel`, `place_bottom_right_panel`, `place_top_right_panel`, opacity constants
- `manim_service/scenes/motion.py` — `smooth_move_to`, `ingestion_wait`, `mark_phase`, `hold_until`, `equation_morph`, `trace_vector`, `cross_highlight_pair`
- `manim_service/scenes/rl_visuals.py` — `FrozenLakeGrid`, `EnvironmentValueHeatmap`, `PolicyArrowGrid`, `QValueTable`, `BackupDiagram`, `EpisodeTrail`. **For P11: use `ActionValueBarChart` (from `panels.py`) or `QValueTable` — the bar chart MUST render visibly.**
- **`manim_service/scenes/code_ide.py::IDECodePanel`** — NEW. Required for S7 code-walkthrough phases per STYLE_BIBLE §34. Smoke-tested. API:
  ```python
  from manim_service.scenes import IDECodePanel
  code = IDECodePanel([
      "env = gym.make('FrozenLake-v1', is_slippery=True)",
      "for prob, ns, r, done in env.unwrapped.P[6][action]:",
      ...
  ], width=6.4, font_size=22, title="bellman_evaluator.py")
  code.move_to([3.4, 0, 0])   # right panel anchor
  self.add(code)
  self.play(*code.step(self, 0))  # highlight line 0
  self.play(*code.step(self, 5))  # advance to line 5
  self.play(*code.reset(self))
  ```

## CRITICAL — defect dossier from prior render (must fix every one)

### RC-1: Double-render of MathTex via TransformMatchingTex
**Symptom:** equation duplicates appear from P19 onward.
**Root cause:** `TransformMatchingTex(source, target)` leaves `source` alive — only matching tokens transform; source must be explicitly removed.
**Fix:** every `TransformMatchingTex` call must be paired with `self.remove(source)` AFTER the play, OR run as `self.play(FadeOut(source), TransformMatchingTex(...))`, OR use `ReplacementTransform`.

### RC-2: Phantom small heatmap inset
**Symptom:** small `+` grid persists in bottom-right from S5/S6 through S8.
**Root cause:** preserved heatmap inset created once, never faded.
**Fix:** at the start of `_phase24_recentering`, explicitly `self.play(FadeOut(self.heatmap_inset))` and remove it from `self._live`. Confirm via frame-extraction that no inset appears in P24–P26 frames.

### RC-3: Wide / off-canvas equation placement
**Symptom:** boxed Bellman extends past frame edges at P19 and P25.
**Root cause:** `move_to([0,0,0])` + equation natural width > 14.2 manim units.
**Fix:** `eq.scale_to_fit_width(11.5)` BEFORE placing. Same rule for the morphed `←` form in P25.

### RC-4: S7 three-panel violation + plain code text
**Symptom:** S7 phases show equation + heatmap + code all PRIMARY; code is non-IDE-styled.
**Fix per STYLE_BIBLE §34:** S7-P21, P22, P23 are TWO-panel only:
- LEFT: heatmap (env panel) at PRIMARY, anchored via `place_left_panel`
- RIGHT: `IDECodePanel` at PRIMARY, anchored via `place_mid_right_panel`
- Bellman equation either faded out before S7, OR brought to center stage only during a brief sampling-interlude (§34.4) where both side panels drop to OPACITY_SECONDARY in the SAME `self.play()` call.

### RC-5: Missing FadeIns at named phases
**Symptom:** P7 frame shows no heatmap; P11 frame shows no q-bars.
**Fix:**
- P7: `EnvironmentValueHeatmap` MUST be visible at `start + 1.0 s`. `FadeIn(heatmap)` must be the FIRST animation of the phase, not the last.
- P11: `ActionValueBarChart` (or `QValueTable`) MUST be visible at `start + 1.0 s`. Schedule its reveal as the first animation. Position via `place_mid_right_panel` — NOT a hand-computed `np.array([...])`.

## Mandatory pre-render verification

Before declaring success, you (Codex) MUST:
1. Render the scene to 480p15.
2. Read `phase_timestamps.json`. Confirm `total_duration_seconds ≈ 1290.0` (±2 s). If significantly less, your PHASE_ENDS array is wrong.
3. Extract 4 frames via ffmpeg at these timestamps and confirm visually:
   - `t=331.0` (S3-P7 mid): heatmap MUST be present and PRIMARY
   - `t=551.0` (S4-P11 mid): q-bar chart MUST be present and PRIMARY
   - `t=920.9` (S5-P19 mid): boxed Bellman MUST be fully inside frame, no clipping
   - `t=1060.9` (S7-P22 mid): EXACTLY two panels (env LEFT + IDE code RIGHT). NO equation panel. NO phantom inset.
4. If any check fails, fix the scene and re-render BEFORE writing STAGE_RESULT.

## Hard-coded PHASE_ENDS (use verbatim — do NOT derive)

```python
PHASE_ENDS = [
    30.0,   60.0,                                   # S1 P1, P2
    120.0,  200.0,  270.0,                          # S2 P3, P4, P5
    330.0,  410.0,  460.0,  510.0,                  # S3 P6, P7, P8, P9
    550.0,  600.0,  630.0,                          # S4 P10, P11, P12
    670.0,  720.0,  770.0,  820.0,  870.0,  920.0,  960.0,  # S5 P13-P19
    1020.0,                                         # S6 P20
    1060.0, 1170.0, 1200.0,                         # S7 P21, P22, P23
    1230.0, 1260.0, 1290.0,                         # S8 P24, P25, P26
]
```

## Lifecycle contract (mandatory)

Every phase ends with `self.hold_until(PHASE_ENDS[idx-1])`.

Every mobject placed must be tracked in `self._live`. At SEGMENT boundaries, call `self._fade_all(keep=(...))` with an explicit keep set. Keep sets are listed below — these are binding:

| Segment boundary | keep= mobjects |
|---|---|
| S1 → S2 (after P2) | () — clean slate |
| S2 → S3 (after P5) | (frozen_lake_grid,) — env carries over |
| S3 → S4 (after P9) | (frozen_lake_grid, heatmap) — both carry into S4 |
| S4 → S5 (after P12) | (frozen_lake_grid, heatmap_inset_small) — only the SMALL inset carries; main heatmap fades |
| S5 → S6 (after P19) | (boxed_bellman, heatmap_inset_small) |
| S6 → S7 (after P20) | (heatmap_full,) — re-introduce full heatmap as env panel for S7; **fade boxed_bellman AND inset** |
| S7 → S8 (after P23) | (boxed_bellman,) — bring back boxed equation centered |

The small heatmap inset MUST be `FadeOut` cleanly at S6 → S7. It MUST NEVER appear in any S7 or S8 frame.

## §34 spec for S7 implementation

### S7-P21: Code entry (40 s, 1020 → 1060)
- Two-panel: env_heatmap (LEFT) + IDECodePanel (RIGHT). Equation absent.
- Animations:
  1. Bring env_heatmap into LEFT anchor.
  2. Bring `IDECodePanel(CODE_LINES, title="bellman_evaluator.py")` into RIGHT anchor.
  3. Pause 1.5 s.
  4. Highlight state-6 cell in env_heatmap (the cell `state = 6` binding refers to).

### S7-P22: Step-through (110 s, 1060 → 1170)
- Same two-panel layout throughout.
- Step the debugger highlight through code lines 0 through 11 in sequence, with `self.wait(7.5)` between each step (~8.5 s/line over 110 s).
- For lines with env-observable effects (state binding, sampling), use `cross_highlight_pair(code.lines[i], env_cell)`.
- For the sampling line (`for prob, next_state, reward, done in env.unwrapped.P[6][action]:`), insert a §34.4 sampling-interlude:
  - In ONE `self.play()` call: env and code dim to OPACITY_SECONDARY, AND a centered transition-probability table fades in at OPACITY_PRIMARY at ORIGIN.
  - Show the 3 sampled successors (state 7, 2, 10) each at prob 0.333.
  - In ONE `self.play()` call: FadeOut the centered table, AND env+code return to OPACITY_PRIMARY.
  - Resume stepping.

### S7-P23: Output handoff (30 s, 1170 → 1200)
- Same two-panel layout. Code highlight on the final `print(...)` line.
- Caption stack (BOTTOM, NOT covering the heatmap):
  - "Heatmap value: 0.039"
  - "Code RHS from v_prev=0: 0.000000"
  - "One sweep is not enough — V-03 will iterate."
- Position via `place_bottom_right_panel` or below the IDECodePanel — not overlapping env or code.

## §35 hot spots (equation dissection)

S5-P14 through P19 derive the Bellman equation in 5 steps. Per §35:
- Equation is centerpiece; env (heatmap or single-cell highlight) paired with it.
- One token at PRIMARY per phase; all others at SECONDARY.
- Every introduced token gets `cross_highlight_pair` with env partner.
- The boxed final form in P19 must be `scale_to_fit_width(11.5)` and `move_to(ORIGIN)`. No off-canvas clipping.

S8-P25 forward-tease: use `equation_morph` from `motion.py`, NOT raw `TransformMatchingTex` without source removal. Morphed `←` form must also `scale_to_fit_width(11.5)`. Hold ≤ 1.5 s, then `FadeOut(morphed)` and restore the boxed `=` form.

## Result format

Write `STAGE_RESULT` to `manim_service/concept_videos/policies_values_bellman_codex_result.md`:

Required fields:
- `status: success` | `failed`
- `scene_py:` absolute path
- `silent_mp4:` absolute path
- `duration_seconds:` from manim log (MUST be ≈ 1290 s ± 2)
- `phase_timestamps_json:` absolute path
- `frames_verified:` list of the 4 mandatory pre-render check frames, one observation each. **Required — voids submission if absent.**
- `errors:` (only if failed)
- `quality_checklist_pass:` only claim 20/20 if you actually inspected frames. Claiming 20/20 on an un-inspected scene is fraud.

## Render command

```bash
/Users/ultramarine/.venvs/manim/bin/python -m manim -ql \
  manim_service/concept_videos/policies_values_bellman_concept.py \
  PoliciesValuesBellmanConcept
```
