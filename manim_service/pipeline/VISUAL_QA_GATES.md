# Deterministic Visual QA Gates

Token-free, autonomous defect gates for the concept-video pipeline. Built to
replace the old "QA agent reads 26 frames × 3 rounds and accepts known
residuals" loop with binary, deterministic pass/fail checks. The LLM only ever
sees a handful of frames from an already-clean video.

## The three gates

| Gate | Module | When | Cost | Catches | Blocking? |
|------|--------|------|------|---------|-----------|
| **G2** static lint | `scene_inspector.py` | before render | 0 | `SLOW-ENTER` cold dim-entry (`run_time > 1.0`, crossfades excluded) | advisory |
| **G1** layout audit | `layout_audit.py` + `BaseConceptScene` hook | during render (auto) | 0 | `OFF-CANVAS` of PRIMARY content (hard); `CROWD` collision/duplicate (advisory) | **blocking** (off-canvas) |
| **G4** quality gate | `quality_gate.py` | after render | 0 (+≤5 frames once) | orchestrates G1+G2, emits ≤5-frame polish set on PASS | **blocking** |

Two precision rules learned from grounding G1 on real renders (otherwise it
floods false positives that make the gate worthless):

- **OFF-CANVAS is hard only for PRIMARY (focal) content.** A dim decorative
  element bleeding off a corner (e.g. a background policy thumbnail) is
  intentional → reported as advisory `off_canvas_warn`, never a hard fail.
- **CROWD excludes composition and is advisory, not blocking.** A framed
  element inside its box, a small label nested in a node, or any sub-`MAJOR_AREA`
  element is composition, not crowding. What survives (two major focal blocks
  partially colliding, or a near-equal full overlap = double-render) is a
  warning for the LLM polish pass to judge.

Ghost-rectangle / orphan mobjects are handled at the source instead: scenes
should clear the slate by fading `self.mobjects` (not just a tracked `_live`
list) at phase boundaries, so untracked leftovers (e.g. a stale code-panel
highlight) cannot persist as a ghost. Small-element crowding (labels colliding
under closely-spaced nodes) is below G1's threshold by design and is left to the
≤5-frame LLM polish pass.

## How G1 is wired (zero per-scene effort)

`BaseConceptScene.mark_phase()` audits the *previous* phase's settled layout;
`tear_down()` audits the final phase and writes `layout_audit.json` next to the
rendered MP4. Every scene that calls `mark_phase` (all current scenes) gets the
audit for free — no edits to scene bodies, no extra render time.

## Commands

```bash
PY=/Users/ultramarine/.venvs/manim/bin/python

# G2 — lint a scene before spending render time (advisory)
$PY -m manim_service.pipeline.scene_inspector \
    manim_service/concept_videos/<lesson>_concept.py

# G1 — summarise the auto-emitted audit (exit 1 on any hard defect)
$PY -m manim_service.pipeline.layout_audit \
    media/videos/<lesson>_concept/<quality>/layout_audit.json

# G1 — re-tune thresholds offline (no re-render): recompute verdicts from the
# stored raw geometry, in place
$PY -m manim_service.pipeline.layout_audit --reanalyze \
    media/videos/<lesson>_concept/<quality>/layout_audit.json

# G4 — full Gate-5: runs G1+G2, extracts the polish frame set on PASS
$PY -m manim_service.pipeline.quality_gate --lesson-id <lesson>
#   exit 0 PASS (deterministic-clean)  1 BLOCK (hard defect)  2 CANNOT-RUN (render first)
```

## Slotting into the 8-gate flow

`quality_gate.py` is the deterministic core of **Gate 5 (QA)**. Recommended
order: run G2 before handing the scene to render; after render, run G4. Only on
`VERDICT: PASS` does an agent look at the ≤5 frames in `/tmp/qa_review_<lesson>/`
for subjective polish (elegance, pacing, the thin-empty-box residue). Hard
defects never reach the LLM — they are fixed in scene code and re-rendered.

## Thresholds (tunable; re-tune offline with `--reanalyze`)

- `layout_audit.PRIMARY_OPACITY = 0.70` — at/above = focal element
- `layout_audit.OFF_CANVAS_TOL = 0.06` — units a group may exceed the frame before it clips
- `layout_audit.MAJOR_AREA = 1.5` — below this (sq units) a group is a sub-element, not a focal block (excluded from CROWD)
- `layout_audit.CROWD_MIN_FRAC = 0.15` — min overlap (of smaller area) to report a collision
- `layout_audit.CONTAINMENT_FRAC = 0.85` — overlap at/above this = one (near) contains the other (composition)
- `layout_audit.NEAR_EQUAL_AREA = 0.85` — comparable size + full overlap = double-render
- `layout_audit.MAX_PRIMARY = 3` — > this many PRIMARY groups = clutter warning
- `scene_inspector.SLOW_REVEAL_RUNTIME = 1.0` — first cold-reveal run_time (strictly `>`) that flags dim-entry
