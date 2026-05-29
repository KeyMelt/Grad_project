# Common Manim Defect Dossier (mandatory reading for Manim Expert)

This file is appended to by every QA rejection. Every Manim Expert spawn MUST
read it and confirm none of these defects appear in their output. The file is
short on purpose — keep one entry per defect class, not per incident.

## How to use this file

Before declaring STAGE_RESULT, run through every entry below. For each, check
whether your scene exhibits the symptom. If yes, apply the FIX. The Self-QA
Phase 0 frame inspection MUST verify each applicable check on actual rendered
pixels, not by reading the source.

---

## RC-1: `TransformMatchingTex` leaves source mobject alive

**Symptom (frame):** Two copies of the same equation overlap at the same
location, often with a slight horizontal offset between them. Worst case:
triple-overlay when a morph happens twice.

**Root cause:** `TransformMatchingTex(source, target)` transforms only the
matching tokens. The source mobject is NOT removed from the scene; only the
matched glyphs animate. Non-matching parts of source persist as ghost shapes.

**Fix (one of):**
- `self.play(FadeOut(source), TransformMatchingTex(source.copy(), target))`
- Use `ReplacementTransform` for non-token-preserving morphs
- After the morph: `self.remove(source)`

**Self-QA check:** Extract a frame at `phase_end - 0.2 s` for every phase
that uses `TransformMatchingTex` or `equation_morph`. If you see two
equations at the same y-position, this defect is present.

---

## RC-2: Persistent inset / callback element forgotten in `_fade_all` keep set

**Symptom (frame):** A small grid, mini-equation, or chip persists in a
corner across multiple segments long after its declared exit phase.

**Root cause:** `_fade_all(keep=(...))` is called at segment boundaries with
an explicit keep set, but a callback element (heatmap inset, equation
thumbnail) is registered via `self._register(...)` AND is supposed to exit
at a specific boundary — and the developer forgot to remove it from the
keep set at that boundary.

**Fix:** At each segment boundary, explicitly list which prior-segment
elements survive. The lifecycle contract in the brief is binding — copy it
verbatim into the scene code as a comment above each `_fade_all` call.

**Self-QA check:** Inspect one frame in each of the last 3 segments of the
video. No element from a prior-segment callback should be visible unless
the brief explicitly lists it in the keep set for that segment.

---

## RC-3: Equation extends off-canvas

**Symptom (frame):** Equation text or its surrounding box is cropped at
the left or right edge of the frame.

**Root cause:** `move_to([0,0,0])` + an unconstrained-width `MathTex` whose
natural rendered width exceeds the 14.222-unit visible canvas.

**Fix:** Apply `eq.scale_to_fit_width(11.5)` BEFORE positioning. This leaves
~1.3 units of margin on each side. If the equation is morphed (e.g. the
S8-P25 `=` → `←` tease), apply `scale_to_fit_width(11.5)` to the morphed
form too.

**Self-QA check:** For every boxed-equation phase, the extracted frame
must show both left and right edges of the box stroke fully inside the
canvas.

---

## RC-4: `set_opacity` on `SurroundingRectangle` fills it solid

**Symptom (frame):** A previously stroke-only rectangle appears as a
solid filled rectangle (often solid yellow VALUE_COLOR) after a fade-in or
opacity restoration.

**Root cause:** `Mobject.set_opacity(val)` sets BOTH `fill_opacity` and
`stroke_opacity` to `val`. A `SurroundingRectangle` has `fill_opacity=0` by
default; if you `.animate.set_opacity(1.0)`, the fill becomes opaque solid
yellow.

**Fix:** When animating opacity on rectangles intended to be stroke-only,
use `.animate.set_stroke(opacity=...)` not `.animate.set_opacity(...)`.

**Self-QA check:** Any phase that fades a `SurroundingRectangle` back in
must be frame-inspected. If you see a solid yellow filled rectangle in
that frame, this defect is present.

---

## RC-5: First animation of a "reveal" phase is scheduled after a wait

**Symptom (frame):** A phase named `heatmap_reveal` or `q_bars_reveal`
shows an empty canvas (or only the prior-segment carry-over) at its mid-phase
timestamp.

**Root cause:** The reveal animation (`FadeIn(heatmap)`) is scheduled near
the END of the phase rather than at the beginning. So at the mid-phase
inspection point, the target element hasn't appeared yet.

**Fix:** For any phase whose name contains "reveal" / "entry" / "intro" /
"definition", the reveal `FadeIn` / `Write` of the named element must be
the FIRST animation in the phase body, before any `wait()` or transition.

**Self-QA check:** For every reveal/entry/intro phase, extract a frame at
`start + 1.0 s`. The named element MUST be at OPACITY_PRIMARY in that frame.

---

## RC-6: §34 violation — code panel mixed with equation panel

**Symptom (frame):** A code-walkthrough phase shows three or more panels
at PRIMARY opacity (equation + env + code).

**Root cause:** Author forgot that STYLE_BIBLE §34 requires TWO panels
only — env LEFT and IDE code RIGHT. The equation panel from the prior
segment was not faded out before entering S7.

**Fix:** At the start of every §34 code-walkthrough phase, explicitly
`FadeOut` the equation panel (or set opacity to 0) BEFORE `FadeIn` of the
code panel. If the equation needs to be referenced, bring it to a brief
centered interlude (§34.4) with both side panels dimmed.

**Self-QA check:** Every §34 phase frame must show exactly TWO panels at
PRIMARY (one LEFT, one RIGHT). No third panel.

---

## RC-7: §35 violation — multiple equation tokens at PRIMARY simultaneously

**Symptom (frame):** During an equation-dissection phase, two or more
tokens of the equation are at full opacity together. Either no dimming
applied, or wrong `OPACITY_PRIMARY`/`OPACITY_SECONDARY` assignments.

**Root cause:** Author forgot that §35 requires ONE token at PRIMARY per
phase. All other tokens drop to SECONDARY in the same `play()` call that
brings the active token to PRIMARY.

**Fix:** For each token-explanation beat, the `self.play()` must
simultaneously: (a) set all other tokens to `OPACITY_SECONDARY`, (b) set
the active token to `OPACITY_PRIMARY`, (c) `cross_highlight_pair` the
active token with its env partner.

**Self-QA check:** Every §35 phase mid-frame must show exactly ONE token
at full brightness with all other equation tokens visibly dimmer.

---

## RC-8: IDE code panel text clipped at right edge

**Symptom (frame):** Code text in the IDE panel runs off the right edge
of the panel's background rectangle. Reader cannot read the trailing
portion of long lines.

**Root cause:** `IDECodePanel` width too narrow for the longest source
line at the chosen font size.

**Fix:** Either (a) shorten the code (use shorter variable names so the
longest line fits), (b) widen the panel (up to 8.0 — beyond that it
overlaps the env panel), or (c) drop font_size to 18 (STYLE_BIBLE §34
minimum). Prefer (a) — code in a teaching video is paraphrased anyway.

**Self-QA check:** Inspect frame at mid-P22 (or whichever phase steps
through code). Every visible code line must fit fully inside the panel.

---

## RC-9: PHASE_ENDS array drifts from plan.md Segment targets

**Symptom:** `total_duration_seconds` is significantly less than the
plan's content-determined target (e.g. 203 s instead of 1290 s for a
21-minute video). The video looks rushed; every phase is too short for
its narration.

**Root cause:** The author invented their own `PHASE_ENDS` based on
animation runtimes rather than reading the plan's per-segment targets.

**Fix:** The Manim Expert brief always carries the canonical
`PHASE_ENDS` array. Use it verbatim. Each phase ends with
`self.hold_until(PHASE_ENDS[idx - 1])` — the `hold_until` pads with
`self.wait` until the target time. Never compute end times from
animation totals.

**Self-QA check:** Read `phase_timestamps.json` after render and confirm
`total_duration_seconds` is within ±2 s of `PHASE_ENDS[-1]`.

---

## RC-10: STAGE_RESULT claims quality_checklist_pass without inspection

**Symptom:** STAGE_RESULT says `quality_checklist_pass: 20/20` but the
rendered video has visible defects from this dossier.

**Root cause:** Author asserted approval without running Self-QA Phase 0.

**Fix:** STAGE_RESULT format now requires a `frames_inspected:` block.
You MUST list every extracted frame path with a one-sentence observation
of what you actually see (not what you intended). If `frames_inspected:`
is empty or fabricated, the gate fails. The Producer scans the report and
voids any submission missing or hallucinating this block.

**Self-QA check:** Before writing STAGE_RESULT, count `frames_inspected:`
entries. If less than 12 strategic frames (per `frame_selector.py`),
abort and run more inspection.

---

## Format for new entries (when QA discovers a new defect class)

When QA rejects a video for a defect not yet in this file, append:

```markdown
## RC-N: <one-line symptom>

**Symptom (frame):** ...
**Root cause:** ...
**Fix:** ...
**Self-QA check:** ...
```

Then bump `RC-N` to next integer. This file is the institutional memory
of every visual mistake we've ever fixed. Manim Expert reads it before
every render.
