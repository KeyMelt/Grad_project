# V-02 QA Review — policies_values_bellman (REAL visual QA, attempt 1 of 2 under patched gate)

**Date:** 2026-05-27 (post-gate-fix)
**Reviewer:** Producer (manual, after voiding the prior text-only "approval")
**Frames extracted:** 52 (26 mid-phase + 26 pre-transition) via ffmpeg
**Frames inspected:** 7 representative + targeted defect checks
**Source MP4:** `backend/media/concept_videos/policies_values_bellman_concept_narrated.mp4` (480p15, 21:30, h264+aac)

## Verdict: REJECTED

The prior 47/47 "approval" was structural inference, not visual QA. Real frame
inspection reveals defects in 6+ phases ranging from severe to catastrophic.

## frames_inspected

- `p07_mid_S3-P7_heatmap.png`: **DEFECT — heatmap missing**. Phase is named "heatmap_reveal" but the rendered mid-phase frame shows only the `v_π(s) ≐ E_π[G_t|S_t=s]` definition equation. The heatmap, which is the entire point of this phase, is absent at mid-phase.
- `p11_mid_S4-P11_q_bars.png`: **DEFECT — q-bar chart missing**. Phase is named "q_bars" and is supposed to show an `ActionValueBarChart` of q_π(14, ·). The frame shows v_π and q_π definitions side-by-side and the heatmap below, but NO bar chart.
- `p19_mid_S5-P19_boxed.png`: **DEFECT — equation off-canvas**. The boxed Bellman equation is cropped at the left edge — frame shows `) = Σ_a π(a|s) Σ_{s',r} p(s',r|s,a)[r + γv_π(s')]` with leading `v_π(s` cut off.
- `p21_mid_S7-P21_code_entry.png`: **CATASTROPHIC**. Three overlapping defects: (a) full Bellman equation at PRIMARY center-left; (b) duplicate boxed Bellman equation smaller, overlapping the heatmap; (c) heatmap + code panel layered behind, still visible. Code text is plain `Text(...)` — no §34 IDE styling.
- `p22_mid_S7-P22_sync.png`: **CATASTROPHIC** (user-flagged). Double-rendered equation with horizontal offset between copies; code panel obscures right column of heatmap (cells 3, 7, 11, 15 hidden); phantom small heatmap in bottom-right; no syntax highlighting, no line numbers, no debugger highlight.
- `p23_mid_S7-P23_output.png`: **CATASTROPHIC**. Same double-equation + code/heatmap overlap + bottom-right phantom inset. Captions stack on top of overlapping visuals.
- `p25_mid_S8-P25_tease.png`: **CATASTROPHIC — worst frame**. TRIPLE-OVERLAY of the assignment-form equation, runs off-canvas both edges, boxed Bellman persists underneath, empty orange-stroked rectangle artifact in lower-center, phantom `+` grid in bottom-right.
- `p26_mid_S8-P26_takeaway.png`: **DEFECT**. Bellman equation rendered twice (boxed takeaway card + full-size below at PRIMARY), empty orange-stroked rectangle floats lower-center, faint `+` grid bottom-right.

**total_frames_inspected: 8** (QA aborted early upon finding systemic defects — 52-frame full pass is wasted effort; scene needs rewrite)

## Root-cause analysis (5 systemic root causes)

### RC-1: Double-render of MathTex equations (P19, P21–P26)
`TransformMatchingTex` invocations don't remove the source mobject. The original
equation persists alongside the transformed copy. Affects every S5–S8 phase
that touches the Bellman equation.

### RC-2: Phantom small heatmap inset (P22, P23, P25, P26)
Choreo §4 specifies a preserved heatmap inset across segments 3–7 as callback.
The scene preserves it but never fades it at the segment 7 → 8 boundary; within
S7 it floats free, no panel anchor, overlapping other content.

### RC-3: Wide / off-canvas equation placement (P19, P25)
`move_to([0,0,0])` plus equation natural width exceeds 14.2 manim units. No
bounding-box check before placement. Boxed equations extend past frame edges.

### RC-4: 3+ panel violation in S7 (P21, P22, P23) + no IDE styling
S7 keeps equation panel AND heatmap panel alive while adding code panel,
producing 3+ panel frames. Code panel is plain `Text(...)` in a `panel()`
wrapper. **STYLE_BIBLE §34** (now canonical) requires two-panel + IDE
rendering for all code-walkthrough phases.

### RC-5: Missing or delayed mobject FadeIn (P7, P11)
- P7 "heatmap_reveal" mid-frame doesn't show the heatmap (reveal timed at
  end-of-phase, or never).
- P11 "q_bars" mid-frame doesn't show any bar chart (`ActionValueBarChart`
  is missing or off-canvas).

## Remediation path

This scene cannot be patched with surgical edits. Structural issues
(double-rendering, persistent insets, missing FadeIns) propagate across the
whole second half. S7 in particular requires complete rewrite using
`IDECodePanel` and STYLE_BIBLE §34 two-panel discipline.

**Recommended action:** Re-spawn Codex `scene_render` with:
1. This QA report as the defect dossier (must address every RC).
2. STYLE_BIBLE §34 and §35 as binding constraints.
3. The new `manim_service/scenes/code_ide.py::IDECodePanel` helper as
   the mandatory code-panel renderer for S7.
4. An explicit `PHASE_ENDS` array included in the brief — Codex shall NOT
   re-derive it.
5. An explicit lifecycle contract: every `self._live` register call has a
   matching FadeOut, and segment-boundary `_fade_all(keep=...)` sets are
   listed phase-by-phase.

`IDECodePanel` is implemented and verified (`/tmp/ide_smoketest.py` →
renders correctly with syntax highlighting, line numbers, debugger
highlight, proper indentation).
