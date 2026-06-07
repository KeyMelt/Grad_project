# Style Bible — RL Concept Video Series

**Owner:** Series Continuity Agent maintains; Producer approves changes.  
**Status:** Living document — all agents read this before every task; all changes require Producer sign-off.

---

## 1. Semantic Color Palette

Every color used in any video **must appear in this table.** No custom colors.

| Constant | Hex | Semantic meaning | Applied to |
|---|---|---|---|
| `STATE_COLOR` | `#38BDF8` | States, cells, s, s' | Grid cells, state labels, s subscripts in equations |
| `VALUE_COLOR` | `#FACC15` | Value functions V(s), Q(s,a) | Value labels, equation V/Q terms, value bar fills |
| `REWARD_COLOR` | `#34D399` | Rewards, positive outcomes | Reward labels, goal cell highlights, r terms |
| `PENALTY_COLOR` | `#F87171` | Penalties, holes, negative outcomes | Hole cells, penalty labels, negative rewards |
| `POLICY_COLOR` | `#A78BFA` | Policy π, action probability distributions | π terms, policy arrow fills, probability bars |
| `ACTION_COLOR` | `#FB923C` | Actions, arrows, a | Action arrows, a subscripts, code highlight rectangles |
| `BG_COLOR` | `#020617` | Scene background | `camera.background_color` |
| `BG_PANEL` | `#0F172A` | Panel fill | Panel `RoundedRectangle` fill |
| `BG_GRID` | `#1E293B` | Structural background grids | Grid cell backgrounds (use at 0.15 opacity) |
| `CODE_ACCENT` | `#64748B` | Code panel headers, muted accents | Code panel title bars |

**Color-geometry binding rule (mandatory):** if a variable uses a specific color in the equation, its corresponding geometric counterpart must use the same color. If `V(s)` uses `VALUE_COLOR` in the equation, the value label on the grid cell also uses `VALUE_COLOR`. No exceptions.

### Legacy aliases (backward-compat only — do not use in new scenes)

| Alias | Resolves to |
|---|---|
| `ACCENT_BLUE` | `STATE_COLOR` |
| `ACCENT_YELLOW` | `VALUE_COLOR` |
| `ACCENT_GREEN` | `REWARD_COLOR` |
| `ACCENT_SLATE` | `CODE_ACCENT` |
| `BG_DEEP` | `BG_COLOR` |

---

## 2. Opacity Hierarchy

Three layers only. Every object in every video belongs to exactly one layer.

| Constant | Value | Layer | What belongs here |
|---|---|---|---|
| `OPACITY_PRIMARY` | `1.0` | Active / focus | Current equation term, targeted grid cell, highlighted bar, active code line |
| `OPACITY_SECONDARY` | `0.4` | Supporting / context | Inactive equation terms, non-targeted grid cells, surrounding graph structure |
| `OPACITY_BACKGROUND` | `0.17` | Structural scaffold | Coordinate axes, grid planes, lattice lines, scene furniture |

**Rule:** when a `SynchronizedFocusGroup` highlights one item, everything else in the group drops to `OPACITY_SECONDARY`. Background scaffold stays at `OPACITY_BACKGROUND` regardless.

---

## 3. Typography

### MathTex

| Use case | font_size |
|---|---|
| Primary equation (standalone, full-screen focus shot) | 48 |
| Primary equation (inside panel or shared layout) | 36 |
| Secondary / contextual equation | 28 |
| Inline annotation | 22 |

**Size rationale:** at 480p15 (development quality) and 720p30 (production), equations smaller than 28pt render as blurry hairlines that viewers cannot read without pausing. Primary standalone equations MUST fill ≥ 40% of the visible frame width. If they don't, increase font_size or reduce the number of concurrent on-screen elements.

**Decomposition rule (mandatory):** any `MathTex` that will be transformed later must be written as an array of string components, not a raw multi-token string:

```python
bellman = MathTex(
    "V", "(", "s", ")", "=",
    "\\max_a",
    "\\sum_{s'}",
    "P", "(", "s'", "|", "s", ",", "a", ")",
    "[", "R", "+", "\\gamma", "V", "(", "s'", ")", "]",
)
```

Use `TransformMatchingTex` for morphing between algebraic lines.

### Text / labels

| Use case | font_size |
|---|---|
| Scene title | 40 |
| Scene subtitle | 26 |
| Panel title | 22 |
| Code lines | 20 |
| Caption line | 22 |
| Bar chart labels | 20–22 |
| Grid cell labels | 20 |

**Caption legibility mandate:** captions at the bottom of the frame must be readable without zooming at the delivery resolution. 22pt is the minimum for any text that a viewer needs to read while the animation is playing. Text smaller than 20pt anywhere on screen is a QA REJECT unless it is a purely decorative axis tick label.

### Font family

Manim default (`LaTeX` for `MathTex`/`Tex`, system sans-serif for `Text`). No decorative fonts.

---

## 4. Layout Standards

### Standard 3-panel grid

```
┌─────────────────────────────────────────────────────┐
│  [Header: title + subtitle — top edge]              │
│                                                     │
│  LEFT (x ≈ -4.2)  │ CENTER (x ≈ 0)  │ RIGHT (x ≈ +4.2)│
│  equation_panel   │ env_panel       │ ActionBarChart  │
│  or MathTex       │ FrozenLake /    │ or code_panel   │
│                   │ CliffWalking /  │ or note_stack   │
│                   │ Blackjack       │                 │
│                                                     │
│  [Caption: single line — bottom edge]               │
└─────────────────────────────────────────────────────┘
```

**Anchor positions (from `BaseConceptScene`):**

| Method | Approximate position | Use for |
|---|---|---|
| `place_left_panel(mob)` | `LEFT * 4.0 + DOWN * 0.15` | Primary equation |
| `place_top_right_panel(mob)` | `RIGHT * 3.8 + UP * 2.0` | Secondary info |
| `place_mid_right_panel(mob)` | `RIGHT * 3.8` | Chart or code |
| `place_bottom_right_panel(mob)` | `RIGHT * 3.8 + DOWN * 2.0` | Notes or legend |
| `place_caption(text)` | Bottom edge | One-line caption |

**Panel dimensions:**

| Panel type | Default width | Min height |
|---|---|---|
| `equation_panel` | 5.6 | 2.0 |
| `code_panel` | 5.4 | 1.6 |
| `panel` (generic) | 5.4 | 1.6 |
| `env_panel` | 4.8 | auto |
| `ActionBarChart` | 3.2 wide × 2.4 tall | — |

### Header

Always added via `show_header(title, subtitle=None)`. Title at top edge with `LaggedStart` `FadeIn`. Never skip the header.

### Caption

One line maximum. Always via `place_caption(text)`. Bottom edge. Swap captions by `FadeOut` old → `FadeIn` new — never overwrite.

---

## 5. Animation Grammar

### Approved primitives

| Animation | Use case |
|---|---|
| `Write` | Equations and formula tokens |
| `Create` | Geometric shapes, arrows, rectangles |
| `FadeIn` / `FadeOut` | Panels, captions, supporting visuals |
| `Transform` / `ReplacementTransform` | Token expansion, concept substitution |
| `TransformMatchingTex` | Equation morphing (component arrays required) |
| `LaggedStart` | Multi-object staggered entrances |
| `Indicate` / `Circumscribe` | Brief attention flash on a single object |
| `Succession` | Sequential beats within a single `play()` call |
| `.animate.set_opacity()` | Dimming / restoring layers |
| `ValueTracker` + `always_redraw` | Continuously updated visuals (bars, positions) |

### Banned animations

| Animation | Reason |
|---|---|
| `Rotating` / `Spin` | Decorative, no teaching value |
| `Bounce` | Decorative |
| Camera zoom/pan during equation typing | Distracts from content |
| `FadeIn` as the sole animation type | Static slideware — fails teaching |
| Simultaneous multi-panel reveals (all at once) | Overwhelms viewer |

### Staggered entrance requirement

Any complex object introduction (multi-row equations, note stacks, panel groups with ≥3 items) **must** use `LaggedStart`:

```python
self.play(
    LaggedStart(
        *[Write(mob) for mob in equation_parts],
        lag_ratio=0.15,
    )
)
```

---

## 6. Pacing Standards

### Length policy — quality over brevity

**There is no target duration for concept videos.** Content depth determines
length, never the reverse. A concept video must FULLY teach the concept it
claims to teach — theory, derivation, visual demonstration, code walkthrough,
iteration/convergence demo where applicable, boundary conditions, and
connection to neighbouring concepts.

| Output type | Typical length | Hard ceiling |
|---|---|---|
| Concept video (the focus of this skill) | 8–15 min for typical lessons; up to 25 min for foundational lessons | **30 min** |
| Trace / replay (per-episode visualisation) | 2–4 min | 5 min |

**Concept-video length rules:**

- **No floor.** A plan that runs under 5 min for a concept video is almost
  certainly thin. Treat it as evidence of an underspecified beat sheet.
- **Hard ceiling: 30 min.** If a beat sheet would exceed 30 min, the lesson
  must be split into two videos. Escalate to Producer for the split decision.
- **Underrunning a thorough plan is a defect, not an efficiency.** Do not
  compress mandatory beats out of the plan to hit an artificial target.

### Content density floor (mandatory for concept videos)

A concept video must contain every item below. Missing items are blocking
failures at the QA gate.

1. Motivation tied to prior lessons in the prerequisite DAG.
2. Theory section with the key equation and a proper derivation — at least
   two `equation_morph` calls, OR one morph plus one `token_expand` sequence.
3. Visual demonstration appropriate to the lesson type: `ValueHeatmap` /
   `QValueTable` for value-function lessons, `PolicyArrowGrid` for policy
   lessons, `EpisodeTrail` for episode-based lessons, `BackupDiagram` where
   the lesson features a Bellman backup.
4. Code walkthrough using `CodeStepper` with runnable Python lines from the
   RL Expert teaching spec's platform-contract/code section. If the teaching
   spec adopts `specs.py.code_focus_lines`, use those exact lines with no
   abbreviation. Tie code lines to the equation and geometry via synchronized
   cross-highlights.
5. For iterative algorithms: the iteration itself shown visually across
   multiple `V_k` snapshots. "Fast-forward to convergence" captions are
   never an acceptable substitute for showing the iteration.
6. At least one boundary condition or common misconception from the
   lesson's `rl_knowledge_base.md` entry, addressed visually.
7. Closing connection to the next lesson in the DAG.

### Minimum wait times (mandatory)

| Moment | Minimum `self.wait()` |
|---|---|
| After first geometry reveal | 2.0 s |
| After equation first appears | 2.0 s |
| After each synchronized step | 1.5 s (via `assimilation_wait()`) |
| After code panel reveal | 1.5 s |
| Final hold frame | 2.5 s |

`BaseConceptScene.assimilation_wait()` default is **1.5 s**. Do not override below 0.6 s for any individual step.

---

## 7. Geometry-Before-Algebra Rule

**Every scene starts with the visual/geometry, not the equation.**

The equation must feel *earned* by the visual context the viewer has already seen. Sequence:

1. Show the environment (grid, card table, agent behavior)
2. Show the outcome distribution (ActionBarChart or agent trails)
3. Only then introduce the equation — the viewer already understands it intuitively

Violation: starting a scene by writing an equation before any visual context is shown.

---

## 8. Three-Phase Generation Workflow

Every concept video passes through three phases before any code is written:

```
Phase 1 — Pedagogical Architect (plan only, no code)
  Output: plan.md
  Defines: geometry-first sequence, color palette declaration,
           layout matrix, opacity layer assignments, pacing beats,
           Gymnasium code snippet, code-visual sync points

Phase 2 — Structural Syntactic Agent (code generation)
  Output: raw_scene.py
  Enforces: ValueTrackers for dynamic objects, TransformMatchingTex
            for equation morphing, LaggedStart for complex reveals,
            relative layout only (no hardcoded coordinates),
            all helpers from panels.py used correctly

Phase 3 — Pacing & Refinement Linter (polish)
  Output: polished_scene.py + review.md
  Adjusts: self.wait() calls (minimums from §6), text overlap
           elimination, opacity hierarchy enforcement,
           final wait() present, no hardcoded coordinates remaining
```

**Artifacts per video:** `plan.md`, `raw_scene.py`, `polished_scene.py`, `review.md`.

---

## 9. Render Quality Policy

| Stage | Quality flag | Resolution | When |
|---|---|---|---|
| Development loop | `-ql` | 480p15 | All iterations during review |
| Final render | `-qm` | 720p30 | Only after all gates are open (Producer approval) |

Never render at `-qm` during the feedback loop. The Manim Expert never decides to use final quality — only the Producer triggers it.

---

## 10. Gymnasium Asset Inventory

### FrozenLake

**Asset path:** `gymnasium/envs/toy_text/img/`

| File | Used for |
|---|---|
| `ice.png` | Safe tiles |
| `stool.png` | Start tile (S) |
| `hole.png` | Hole tiles |
| `goal.png` | Goal tile (G) |
| `cracked_hole.png` | Cracked hole variant |
| `elf_up/down/left/right.png` | Agent sprite (direction-aware) |

Loaded via `frozenlake_frame(state)` → `ImageMobject`. Fallback: colored rectangle if assets not found.

### Blackjack

**Asset path:** `gymnasium/envs/toy_text/img/`

| File | Used for |
|---|---|
| `{suit}{rank}.png` | Face-up cards (e.g. `CA.png`, `H7.png`, `S10.png`) |
| `Card.png` | Face-down dealer card |

Suits: `C` (clubs), `D` (diamonds), `H` (hearts), `S` (spades).  
Ranks: `A`, `2`–`10`, `J`, `Q`, `K`.

Loaded via `card_mobject(code)` → `ImageMobject`.

### CliffWalking

**Asset path:** `gymnasium/envs/toy_text/img/`

| File | Used for |
|---|---|
| `gridworld_median_*.png` | Grid tile borders |
| `elf_down.png` | Agent sprite |
| `cookie.png` | Goal marker |

Cliff cells (row=3, col=1..10) styled with `PENALTY_COLOR` fill.

---

## 11. Terminology Glossary

Canonical names used in narration, captions, and on-screen text. Agents must not deviate.

| Canonical term | Banned alternatives |
|---|---|
| state-value function | value function, V function |
| action-value function | Q function, quality function |
| transition probability | dynamics, environment dynamics (**exception:** "dynamics function" is S&B §3.1's own term for the four-argument form p(s',r\|s,a) and is permitted when referring precisely to that form; the ban targets vague uses of "dynamics" or "environment dynamics" as substitutes for the full notation) |
| policy | strategy, behavior |
| episode | run, trial, rollout (use "rollout" only for policy rollouts, not episodes) |
| discount factor γ | discount rate |
| Bellman equation | Bellman update (use "equation" for the identity, "update" for the iterative rule) |
| backup | backup diagram (noun); never "backup" as a verb |
| stochastic policy | random policy, mixed policy |
| deterministic policy | greedy policy (only if it is greedy — do not use interchangeably) |

---

## 12. Audio — Narration

### Voice (locked across the series)

| Field | Value |
|---|---|
| TTS engine | Kokoro v1.0 (local, ONNX) |
| Voice id | `am_michael` |
| Register | Measured, professorial, American male |
| Speed | 1.0 (do not override) |
| Sample rate | 24 kHz |
| Output format | AAC stereo, 192 kbps (mono dual-routed to L+R) |

The voice id is a series constant. Changing it requires Producer approval
and a new entry in this section. If we add a separate output type later
(e.g. "Study Buddy podcast" with a different voice), document it here as
a distinct entry — do not silently swap voices on existing types.

### BGM policy — none

**The series uses no background music.** Concept videos are
narration-only — narration carries the pedagogy and BGM would compete with
on-screen mathematical text. This mirrors the 3Blue1Brown approach.

If a future lesson genuinely requires BGM (e.g. an outro to a multi-part
series), the Producer grants an exception and a track is added to this
section with its own volume envelope. Default remains no BGM.

### Synthesis pipeline

The Voice & BGM agent runs Kokoro via:
`python -m manim_service.audio.synthesize` (see voice-bgm SKILL.md Step 5).
The script reads `narration_script.md`, synthesises each timed line, and
muxes the result into the silent Manim MP4 via ffmpeg. Each synthesised
line is placed at its declared `[HH:MM:SS]` cue; subsequent lines shift
later if a clip overruns. A per-line `audio_report.json` is emitted next
to the final MP4 for QA inspection.

### Quality bar (enforced by QA group D)

- Narration track present (AAC, mono → stereo, 24 kHz).
- Voice id matches `am_michael`.
- Final video duration matches narration duration ±0.5 s.
- No phase-boundary overflow warnings in the audio report.
- No clipping, no abrupt cuts, no mispronounced technical terms.
- Narration lines for "first geometry reveal", "first equation reveal",
  and "final hold" begin within ±1.0 s of the visual cue.

---

## 13. Semantic Color Binding Matrix (mandatory)

The visual layer and the equation layer share **the same colour for the
same concept**. The viewer's eye must never have to translate between a
colour-coded equation token and a different-coloured geometric object.

| Symbol / on-screen object | Color constant | Examples |
|---|---|---|
| State `s`, `s'`, `S_t` ; grid cell labels and outlines ; agent token | `STATE_COLOR` | the `s` in MathTex, every grid-cell border, the `S` start label |
| Value `v_π`, `v_k`, `v_{k+1}`, `V_*`, `Q`, value bars, heatmap fills | `VALUE_COLOR` | numeric labels inside ValueHeatmap, the `v_k` token in equations |
| Reward `r`, `R_{t+1}` ; goal cell ; ✓ markers | `REWARD_COLOR` | the `r` in equations, the `G` goal label on FrozenLake |
| Penalty / hole cells / ✗ markers | `PENALTY_COLOR` | hole-tile fills, the `-1` rewards on CliffWalking |
| Policy `π`, `π(a|s)`, `\mathbb{E}_π` ; action probabilities ; agent under policy | `POLICY_COLOR` | the `π` in equations, the agent dot when walking under π |
| Action `a` ; arrows ; `max_a` ; action labels and dots | `ACTION_COLOR` | the `a` in equations, all four directional arrows, action-dot in backup diagram |
| Code accents, panel headers, axis labels | `CODE_ACCENT` | code-panel title bar, plot axis ticks |

**Rules (QA E41 enforces):**
- If `s` is `STATE_COLOR` in the equation, every `s` referenced in the
  geometry must also be `STATE_COLOR`. No exceptions.
- A code-line variable name corresponding to one of the symbols above
  must be highlighted in the same colour as the symbol (e.g. the
  ``next_state`` identifier in the code panel uses `STATE_COLOR`).
- "Plain text" labels (captions, narration callouts) that name one of
  these concepts must use the same colour or grey — never another
  semantic colour.

---

## 14. Asset Border Standards

Every environment asset (FrozenLake PNG, Blackjack card render,
CliffWalking gridworld tile composite) is wrapped in a soft container
that masks the asset's native white/light backgrounds and blends it into
the dark scene canvas.

**Standard wrapper:** the helper functions in `panels.py` (e.g.
`frozenlake_frame()`, `card_mobject()`, `cliffwalking_panel()`) produce
this wrapper by default. It is a `RoundedRectangle`:
- `fill_color = BG_PANEL`, `fill_opacity = 1.0`
- `stroke_color = STATE_COLOR` (or the panel's accent), `stroke_width =
  1.4`, `stroke_opacity = 0.55`
- Padded ~0.12 units larger than the wrapped image on every side
- `corner_radius = 0.14`

**Banned:** raw `ImageMobject` placement of any Gymnasium-rendered asset
directly on the scene canvas. The stark white edges of the asset against
`BG_COLOR` create harsh contrast that pulls focus away from internal
mechanics. (QA E37.)

Use ``soft_frame=False`` in the helpers ONLY when the asset is being
placed inside another containing panel that already supplies its own
framing — e.g. `environment_panel()`.

---

## 15. Cross-Modal Highlight Rules (Geometry ↔ Algebra ↔ Code)

The viewer should not have to mentally connect a piece of code, an
equation token, and an on-screen geometric region by spatial scanning.
The video itself draws the connection at the moment of teaching.

### 15.1 `trace_vector` at equation derivation (QA E45)

When a new equation token is `Write`-animated for the first time AND its
meaning is grounded in a visible geometric element (a tree-branch label,
a probability arrow, a cell, a reward marker), the scene MUST draw a
transient `trace_vector` from the source geometry to the new token.

- Use the helper `from manim_service.scenes import trace_vector`.
- The trace is dashed/transient: ~1.2 s on screen total, then fades.
- One trace per token. Do not chain traces.

### 15.2 `cross_highlight_pair` at code execution (QA E43)

When a `CodeStepper.step(i)` advances the active line AND that line's
effect is locally observable on the grid/matrix/value display, the
scene MUST simultaneously flash the affected region using
`cross_highlight_pair(scene, code_line, target_geometry)`.

Example bindings (from the plan.md cross-highlight matrix):

| Lesson | Code line content | Geometric pair |
|---|---|---|
| dp_policy_eval | `for action, action_prob in enumerate(policy[state]):` | the four action arrows in the focal cell |
| dp_policy_eval | `for transition_prob, next_state, reward, done in env.unwrapped.P[state][action]:` | the outcome arrows emanating from the focal cell |
| dp_policy_eval | `new_value += action_prob * transition_prob * (reward + gamma * V[next_state])` | the next-state cell in the heatmap |
| dp_policy_eval | `V[state] = new_value` | the focal cell whose label gets updated |

The Script Writer's plan.md must include a **cross-highlight matrix**
for any phase containing a `CodeStepper`. Missing matrix = QA REJECTED.

---

## 16. Layout Standards — Reserved Hemispheres (mandatory)

Every concept-video scene reserves screen real-estate so that **no
later-introduced element ever fully occludes an earlier element that
remains pedagogically active**. (QA E38.)

### 16.1 The 3-column rule

| Hemisphere | Standard occupant |
|---|---|
| LEFT (≈ −5.0 to −1.5 x) | Equation panel (after Phase 3); environment grid (early phases) |
| CENTER (≈ −1.5 to +1.5 x) | The single most-active visual right now — heatmap during iteration, fork diagram during derivation, single grid during motivation |
| RIGHT (≈ +1.5 to +5.0 x) | Reserved for the code panel, iteration counter, or supplementary annotations |

When a phase introduces a NEW element on RIGHT (e.g. a `CodeStepper`),
the CENTER and LEFT elements must scale down and migrate to make room
**before** the new element appears. They do NOT remain at original
size and get occluded.

### 16.2 Text safety padding

Every `Text`, `MathTex`, and label mobject must keep at least **0.18
units** of clear space (`buff=0.18` in `.next_to()` / `.arrange()`) from
any neighbouring mobject. Tighter spacing is permitted only between
sub-tokens within a single decomposed `MathTex`. (QA E38.)

### 16.3 No element occlusion

No mobject ever covers ≥ 50% of another active mobject's bounding box.
If a phase introduces a panel that would overlap an existing element by
more than 50%, the existing element must first be relocated (via
`smooth_move_to`) or faded out.

---

## 17. Motion & Easing (mandatory)

Every positional transformation (`.animate.move_to(...)`,
`.animate.to_edge(...)`, `.animate.shift(...)`) MUST run with smoothed
easing and a **minimum `run_time` of 0.9 s for distance < 2 units, or 1.2
s otherwise**. (QA E39.)

- Use `BaseConceptScene.smooth_move_to(mob, target)` instead of bare
  `self.play(mob.animate.move_to(target))`. The helper enforces the
  minimum run_time and uses Manim's smooth rate function (ease-in-out)
  by default.
- Banned: any positional `.animate` call with `run_time < 0.9 s` that
  moves a mobject more than 1 unit. Snap-style relocations are a focus
  break.
- Multi-element repositions (e.g. equation slides LEFT while grid
  shrinks toward CENTER) use a single `self.play(...)` with both
  animations so they share the same eased timeline.

---

## 18. Pacing — Ingestion Buffers (mandatory)

After every major structural morph the scene MUST inject a
`BaseConceptScene.ingestion_wait()` (default 2.5 s) before the next
animation begins. (QA E40.)

A "major structural morph" is any of:
- An `equation_morph` / `TransformMatchingTex` call
- A scene-wide reposition (multiple mobjects moving simultaneously)
- A panel `FadeIn` or `FadeOut` that changes the active visual
  composition
- A `ValueHeatmap.sweep_update` completion
- The end of a `SynchronizedFocusGroup` step sequence
- A camera `zoom_to` / `zoom_reset`

`ingestion_wait` is distinct from `assimilation_wait`: the former is a
mandatory post-morph buffer (≥ 1.5 s, default 2.5 s), the latter is a
narrative pacing pause (≥ 0.6 s, default 1.5 s). Both are required at
their respective points.

---

## 19. Iteration Demos — Sweep, Not Flash (mandatory)

When showing iterative updates across a value table or heatmap, use
`ValueHeatmap.sweep_update(scene, new_values)` (or the equivalent
`QValueTable` sweep helper) instead of `update_values`. (QA E42.)

The sweep animates each cell's recolor in sequence — usually
Manhattan-distance-from-goal order — with an optional carry indicator
dot tracing the path. The viewer SEES value propagating outward from
the reward source instead of an all-at-once flash that obscures the
direction of propagation.

`update_values` (the original method) is retained for non-iterative
re-displays — e.g. the side-by-side π_A vs π_B contrast in dp_policy_eval
Phase 6, where both heatmaps appear at once and there is no temporal
sweep to convey.

---

## 20. Code Fidelity — Runnable Python Only

The `CodeStepper` panel carries **runnable Python** — variable names
that exist, library calls that work, indentation that parses. No
pseudocode placeholders like `future`, `transition`, `accumulator`. (QA E44.)

- The concept-video source of truth is the RL Expert-authored
  `manim_service/concept_videos/[lesson_id]_specs.md`. Its platform-contract
  / code section may adopt lines from `backend/concept_videos/specs.py`
  `LessonVideoSpec.code_focus_lines` for app compatibility. When adopted, each
  line must remain a real Python statement using real variable names.
- The Gymnasium model is accessed via `env.unwrapped.P` — never
  `env.P` (the latter fails on a wrapped env).
- Indentation in the code panel matches the indentation a learner would
  type. Two-line nested loops show as two indented levels in the
  `CodeStepper`.

If a Manim Expert finds that a platform-contract code line uses a pseudocode
placeholder, escalate to the RL Expert / Producer. The fix is to update the
teaching spec first, then update any compatibility export such as `specs.py`
if the app still depends on it — not to silently substitute the pseudocode
with the real variable in just the scene.

---

## 21. Title & Subtitle Hygiene

The on-screen subtitle introduced by `BaseConceptScene.show_header(title,
subtitle)` must be **human-readable**. Developer-facing identifiers,
lesson_ids, file paths, internal slugs, and version strings are banned
from subtitles. (QA E36.)

| Allowed | Banned |
|---|---|
| `show_header("Policy Evaluation", subtitle="Computing v_π under a fixed policy")` | `show_header("Policy Evaluation", subtitle="dp_policy_eval")` |
| `show_header("Q-Learning")` (no subtitle is also fine) | `show_header("Policy Evaluation", subtitle="manim_service.concept_videos.dp_policy_eval_concept")` |
| `show_header("First-Visit Monte Carlo", subtitle="MC prediction on Blackjack")` | any `*_concept`, `*_eval`, `dp_*`, `mc_*`, `td_*` token in the subtitle |

The lesson_id lives in the filename, the SESSION_LOG, the worker
registry, and the specs entry — never on screen.

---

## 22. Convergence Gates (summary)

A video is added to the library when **all** of the following are open:

1. RL Expert signs off `plan.md` and `choreo.md`
2. Technical Validator issues PASS on all code snippets and numerical examples
3. Voice & BGM Agent delivers `narration_script.md` and `audio_brief.md`
4. Transcript Writer delivers `captions.srt` and `captions.vtt` with no flagged gaps
5. QA Agent issues APPROVED on rendered video, audio, and captions
6. Series Continuity Agent issues CONSISTENT across video, narration, and captions
7. RL Expert issues final academic sign-off
8. Producer approves for library addition

---

## 23. Element Lifecycle Management (mandatory)

The "stale environment sitting unused on canvas" failure mode is the
canonical violation this section closes. The Visual Director's
`choreo.md` Element Lifecycle Matrix is BINDING — every mobject named
in the plan must have an explicit Phase IN, a Visible-During range,
and a Phase OUT. (QA F46.)

**Staleness threshold:** no mobject may sit on canvas at any opacity
level for more than **8 seconds** while not actively referenced by
narration, by a `cross_highlight_pair`, by a `trace_vector`, by a
`SpriteActionBinding`, or by a current animation. Either dim to
`OPACITY_BACKGROUND`, or `FadeOut`. The choreo.md Phase OUT column
states which.

**Re-entry:** a mobject that left the canvas may re-enter in a later
phase. The Element Lifecycle Matrix's "Re-enters at" column declares
where. The re-entered mobject does NOT need to be the same Python
object — semantically equivalent is sufficient (e.g., a smaller copy
of the FrozenLake grid).

**Banned:** keeping the Phase-1 environment grid visible through every
subsequent phase "for reference" when no later phase actually uses it.
This is the visual equivalent of buffer hoarding.

---

## 24. Motion Choreography — Motion Teaches, Not Decorates (mandatory)

Every `self.play(...)` in the rendered scene corresponds to a row in
the choreo.md Motion Choreography table tagged with one of:

| Tag | Meaning |
|---|---|
| **REVEAL** | Introduces a new piece of information (Write, FadeIn of a previously unseen element) |
| **DERIVE** | Transforms one form into another (TransformMatchingTex, equation_morph, sweep_update, numeric morph) |
| **RESOLVE** | Answers a question raised earlier (a value bar reaches its final height, the optimal action arrow appears) |
| **CONNECT** | Explicitly binds two on-canvas elements (trace_vector, cross_highlight_pair, SpriteActionBinding) |
| **REFRAME** | Changes the camera's focal point (zoom_to, pan_to_follow, zoom_reset) |

Decorative motion — animations whose only job is to fill time, look
fancy, or substitute for content — is BANNED. (QA F47.)

3Blue1Brown reference: every animation he plays has a teaching purpose.
The arrow that grows from the curve is showing slope. The point that
slides along the parametric path is showing parameterisation. The
camera that zooms into the equation is reframing the viewer's
attention. The Visual Director chooses motion the same way — purpose
first, prettiness only when it serves the purpose.

---

## 25. Camera Direction (mandatory when complexity demands)

The default camera frame is the wide 14-by-8-ish Manim frame. Camera
moves are tools to manage viewer focus when the default frame would
spread attention too thin. Use them deliberately:

| Move | When |
|---|---|
| `zoom_to(scene, target, scale=0.55)` | When a single equation derivation will run for ≥ 8 s — reframe to remove the rest of the canvas from contention |
| `pan_to_follow(scene, sprite, path)` | When a sprite traverses more than half the canvas width — keep the active region centred |
| Side-by-side reframe (zoom out + reposition) | When the teaching device is a contrast pair (two heatmaps, two policies, two grids) — give both equal attention |
| `zoom_reset(scene)` | Returning to wide after a derivation OR introducing a new wide-layout element (CodeStepper, side-by-side contrast) |

**Banned:** zooming in and out within the same 4 s window (a "flinch,"
not a shot). A scene with zero camera moves over 10+ minutes is
suspicious — the choreo.md should justify why none was needed.
(QA F49.)

Camera shots are listed in the choreo.md Camera Shot List, one row
per shot with: phase, shot description, trigger time within phase,
helper call, duration, and purpose.

---

## 26. Sprite-Math Binding Protocol (mandatory for algorithmic motion)

When an on-screen sprite (agent, evaluator, ball, vector) moves AND
the algorithm being taught explains that motion mathematically, the
two must animate together. The `SpriteActionBinding` helper in
panels.py couples motion to highlight; the choreo.md Sprite-Math
Binding Matrix lists every binding.

**Required for:** every phase where a sprite moves AND there is an
equation or code panel on screen referring to the rule that justifies
the sprite's motion. (QA F50.)

**Optional for:** purely contextual sprite motion (e.g., a flavour
agent walking in Phase 1 motivation before any equation has been
written).

**Banned:** a sprite that moves "on its own" while the algebra sits
inert and unhighlighted next to it — the viewer is left to mentally
connect what the math says is happening with what the visual is
showing happening. That mental connection is what the binding does
for them.

Example (from dp_policy_eval Phase 4): the evaluator sprite enters
cell *s*, `v_{k+1}(s)` flashes; the sprite looks at next state *s'*,
`v_k(s')` flashes; the sprite writes the new value, `←` flashes and
the cell label numeric-morphs. The viewer is never asked to translate
between motion and math — they happen together.

---

## 27. Cognitive Load Budget (≤ 4 primary mobjects per frame)

At any rendered frame, the count of mobjects at `OPACITY_PRIMARY`
(1.0) MUST NOT EXCEED FOUR. Everything else is at
`OPACITY_SECONDARY` (0.4), `OPACITY_BACKGROUND` (0.17), or gone.
(QA F48.)

The choreo.md Cognitive Load Budget table specifies the primary
mobject set at the start, middle, and end of each phase. The Manim
Expert uses opacity transitions to enforce the budget.

**Counting rules** (also in visual-director SKILL.md):

- Two grouped subordinate elements at the same opacity count as ONE
  mobject (e.g., `action_arrows_overlay` = 1 mobject when all four
  arrows share a single opacity level)
- A single `MathTex` equation counts as ONE mobject regardless of
  internal token count, UNLESS some tokens are at PRIMARY while others
  are at SECONDARY simultaneously — in which case the two tiers count
  separately
- The header (title + subtitle) counts as ONE mobject for the whole
  scene
- A caption at the bottom of the screen counts as ONE mobject

If a phase needs five or more primary mobjects, the Visual Director
must split the phase into two sub-phases or move some elements to
SECONDARY first.

---

## 28. Scientific Rigor + Pedagogical Strategy (mandatory in every choreo.md)

Every choreo.md begins with two sections (§1 Scientific Rigor and §2
Pedagogical Strategy) that the RL Expert and the QA Agent both read.

### 28.1 Scientific Rigor

3–6 sentences explaining:
- What claims the video makes
- What evidence is on screen for each claim
- What qualifications would mislead the viewer if omitted (env variant,
  γ value, policy choice, asset assumptions)

The Technical Validator's PASS depends on the numerical claims; the
Scientific Rigor section depends on the **framing** of those claims.
A video can be numerically correct and still misleadingly scoped.
(QA F51.)

### 28.2 Pedagogical Strategy

One sentence naming the primary teaching pattern from the approved
list:

- **Worked example** — single instance, walked through end to end
- **Contrast pair** — same algorithm on two inputs (π_uniform vs π_LEFT, etc.)
- **Concrete-to-abstract** — start from numerics, derive the symbolic
- **Failure case + recovery** — show the misconception first, then refute it visually
- **Top-down decomposition** — start from the equation, break each piece down geometrically
- **Bottom-up assembly** — build the equation up from the geometry one term at a time

Followed by 2–3 sentences explaining why this pattern fits the
lesson, and one sentence naming the specific misconception (from
rl_knowledge_base.md) that this pattern is designed to defeat.
(QA F52.)

---

## 29. Narration-Visual Synchronization Contract (mandatory)

The narration and the visual are TWO SIDES OF THE SAME ARGUMENT. The visual
shows the phenomenon; the narration explains what it means. Neither can do the
other's job. All pipeline agents enforce this contract.

### 29.1 Equation on-screen mandate (QA G55)

Any equation **spoken** in the narration MUST be **visible on screen** at the
moment the narrator says it, within a ±0.5 s window. This is a hard requirement,
not a guideline. Implementation:

- The Manim Expert schedules equation `Write` animations to fire at the timestamp
  declared in the narration script's `[HH:MM:SS]` cue.
- The Voice & BGM Agent flags every narration line containing an equation with a
  `[EQ_ON_SCREEN]` marker; the QA Agent verifies the marker against the rendered
  frame at the declared cue time.
- No equation may be narrated before it appears (no "in a moment we'll see...") or
  after it disappears.

### 29.2 Visual primacy — narration explains meaning, never describes the screen (QA G56)

The viewer can see the animation. **Do not describe it.** The narration explains
WHY what is happening matters — the mathematical relationship, the physical
intuition, the thing the viewer should feel.

| ❌ BANNED — describing the screen | ✅ REQUIRED — explaining meaning |
|---|---|
| "A four-by-four grid is appearing on screen." | "The ice is slippery — the agent can slip sideways even when it chooses a direction." |
| "The bar chart on the right shows three bars." | "Each bar is how likely the agent actually ends up in that cell." |
| "Now we fade in the Bellman equation." | "The value of a state is just the weighted average of every future it might reach." |
| "The elf moves to the right here." | "Choosing right doesn't guarantee arriving right — that's what makes this hard." |
| "You can see the reward is plus one at the goal." | "That single plus-one is the only signal the agent ever receives — no partial credit." |
| "Three items appear on screen." | (Describe nothing. Move directly to the meaning.) |

**The litmus test:** remove the visual entirely. Does the narration still make
coherent sense as a standalone audio explanation? If yes, the narration is doing
its job. If the narration only makes sense because the viewer can see the
animation, it is describing, not explaining — rewrite it.

### 29.3 Narration-intention field in plan.md (mandatory)

Every plan.md phase block must include a `narration_intention` line stating the
conceptual insight the narrator is building in the viewer's mind — not a
description of the animation events.

```markdown
## Phase 2 — Stochastic traversal

**Animation events:** Agent moves right from state 6; slides to states 5, 7, and 2 in
three successive attempts; each landing highlighted.

**Narration intention:** build the intuition that "choosing an action" and "arriving
at the intended cell" are two entirely different things on slippery ice.
```

If `narration_intention` is missing, the RL Expert rejects the plan at Gate 1.

---

## 30. Conversational Register — 3Blue1Brown Standard (mandatory)

All narration for this series follows the register established in 3Blue1Brown's
"Essence of Linear Algebra" and "Essence of Calculus." The voice is that of a
knowledgeable guide building genuine curiosity — not a textbook being read aloud.

### 30.1 Approved conversational moves

| Move | Example |
|---|---|
| Rhetorical question | "But what does 'value' actually mean here?" |
| Naming the tension | "The agent wants the goal — but has no map and no supervisor." |
| Expressing discovery | "Here's what makes this beautiful:" |
| Building suspense | "So the natural question becomes..." |
| Acknowledging what the viewer already knows | "If you've seen the previous video, you know that..." |
| Forward-teasing (used sparingly) | "We'll see exactly why this matters in a moment." |
| Connecting equation to intuition | "That sum is just the weighted average of every future the agent might reach." |
| Short punchy emphasis | "No labels. No supervisor. Just the number." |

### 30.2 Banned narration patterns

| ❌ Pattern | Why banned |
|---|---|
| "In this video, we're going to learn about..." | Robotic preamble — start with the concept |
| "As you can see..." / "Notice on screen..." | Describes visuals — forbidden by §29.2 |
| "The equation for the X is..." (cold drop) | Equation must be earned, not announced |
| Opening with "So," / "Okay," / "Alright," / "Basically," | Filler openers — cut them |
| "There are four actions: up, down, left, right." | Dry enumeration — show, don't list |
| Reading symbols literally: "V of s equals max over a of..." | Robotic symbol recitation; explain meaning instead |
| Hedging: "kind of," "sort of," "basically," "in a way" | Undermines authority |
| Excited filler: "Wow!", "Amazing!", "Let's go!" | Performative — not educational |

### 30.3 Sentence character

- **Vary sentence length.** Mix short punchy sentences (4–8 words) with longer
  explanatory ones (12–18 words). Monotone rhythm creates monotone delivery.
- **Begin sentences with the concept, not a connector.** "Value functions capture
  long-term worth" not "So, value functions capture long-term worth."
- **Rhetorical questions are content.** "What happens if the reward is delayed by
  ten steps?" is a valid narration sentence.
- **One vocal stress per sentence.** Mark with `*asterisks*`. The synthesizer maps
  these to Kokoro emphasis. Overusing emphasis kills it.
- **Avoid run-on sentences.** A sentence with more than two clauses should be split.

### 30.4 Equation spoken forms (mandatory conventions)

| Symbol / LaTeX | Spoken form |
|---|---|
| `V(s)` | "the value of state s" |
| `Q(s, a)` | "the Q-value of taking action a in state s" |
| `π(a\|s)` | "the probability of choosing action a in state s under policy π" |
| `\gamma` | "gamma" |
| `\sum_{s'}` | "the sum over all reachable next states" |
| `\max_a` | "the action that maximizes" |
| `E_\pi` | "the expected value under policy π" |
| `← ` (update arrow) | "is updated to" |
| `+1` reward | "a reward of one" |
| `0` reward | "no reward" |
| `-1` reward | "a penalty of one" |

**Never read raw LaTeX aloud.** Every equation narrated must have its spoken form
written out in the narration script.

### 30.5 Speaking numbers like a person (mandatory)

On-screen precision is for the eye; the narration is for the ear. **Nobody says
"zero point zero zero zero zero zero zero."** A lecturer reads the *meaning* of a
number, not its digits. This is the #1 source of screen-reader monotony — fix it.

| On screen | ❌ Screen-reader | ✅ Human lecturer |
|---|---|---|
| `0.000000` | "zero point zero zero zero zero zero zero" | "zeroed out" / "still flat zero" / "nothing yet" |
| `0.433579` | "zero point four three three five seven nine" | "about 0.43" / "roughly four-tenths" |
| `0.039` | "zero point zero three nine" | "around four percent" / "a hair above zero" |
| `0.012` | "zero point zero one two" | "barely off zero" |
| `0.333` | "zero point three three three" | "about a third" |
| `0.53` | "zero point five three" | "just over half" |
| `0.99` (γ) | "zero point nine nine" | "a discount close to one" / "nearly one" |
| `1290` | "one two nine zero" | "about thirteen hundred" |

Rules:
- **Round hard for the ear.** Two significant figures is plenty; one is often better.
- **Never voice trailing zeros**, and never spell a number digit-by-digit.
- **Prefer the qualitative read** ("about a third", "barely moved", "zeroed out")
  when the exact value isn't the teaching point. Reach for a precise rounded number
  only when the *specific* value matters (e.g. the goal state's value being ~0.43).
- The full-precision number stays *on screen*; the script writes the spoken form.

### 30.6 Sound like a person, not a parser (mandatory)

The narration should sound like a sharp lecturer talking *to one student*, not a
document being voiced. Concretely:

- **Use contractions.** "it's", "we're", "that's", "here's", "doesn't", "let's" —
  always, unless the uncontracted form carries deliberate stress.
- **Talk, don't recite.** Reframe a fact as a small realization: "And here's the
  catch — one sweep isn't enough." rather than "One sweep is not enough."
- **Address the viewer as "you."** "You'd expect the value to be high here — it's
  not."
- **Let rhythm breathe.** A short fragment after a long sentence lands. "So the
  whole table updates at once. Every state. One pass."
- **Plain words over jargon** when both work: "the look-ahead", "the running total",
  "fold the future back" beat their formal twins on first contact.

These coexist with §30.2: still no filler openers ("So,", "Okay,"), no hedging that
undercuts authority ("kind of", "I guess"), and no performative excitement.

---

## 31. Gymnasium Asset Mandate (mandatory)

All environment renders in any concept video **MUST use the actual Gymnasium PNG
sprite assets.** Colored-rectangle fallbacks are **banned in all delivered
renders**. This is a QA G57 block.

### 31.1 Pre-production asset verification

Before writing any FrozenLake, CliffWalking, or Blackjack scene, the Manim Expert
(via Codex) MUST verify assets exist:

```python
import gymnasium, os
asset_dir = os.path.join(os.path.dirname(gymnasium.__file__),
                         'envs', 'toy_text', 'img')
required = ['ice.png', 'stool.png', 'hole.png', 'goal.png',
            'elf_right.png', 'elf_left.png', 'elf_up.png', 'elf_down.png']
missing = [f for f in required if not os.path.exists(os.path.join(asset_dir, f))]
assert not missing, f"Missing Gymnasium assets: {missing}"
print("ASSET_DIR:", asset_dir)
```

If any asset is missing, **stop** and report `MISSING_ASSETS` to the Producer.
Do not substitute rectangles. Do not proceed.

### 31.2 Native Gymnasium frame embedding (preferred method)

For Phase 1 "reveal the environment" beats, embedding actual Gymnasium render
frames produces the highest-fidelity, most authentic representation:

```python
import gymnasium as gym, numpy as np
from PIL import Image
import tempfile, os

env = gym.make('FrozenLake-v1', render_mode='rgb_array')
env.reset(seed=42)
frame = env.render()          # HxWx3 numpy array, native Gymnasium pixel art
img = Image.fromarray(frame)
tmp = tempfile.NamedTemporaryFile(suffix='.png', delete=False)
img.save(tmp.name)
mob = ImageMobject(tmp.name).scale_to_fit_width(5.5)
```

Wrap the ImageMobject in a soft container per §14 — never place it naked on
the canvas.

### 31.3 Per-tile composition (via helpers)

`frozenlake_frame(state)` composes individual tile PNGs (ice, hole, goal, stool,
elf sprites) into a Manim `VGroup`. Use this when you need to animate individual
tiles (highlighting, scaling) that a flat frame image cannot support.

Both methods are approved. Full Gymnasium frame is preferred for static reveals;
per-tile composition is preferred for interactive/highlighted sequences.

---

## 32. Codex CLI Mandate for Execution Stages (mandatory)

The two heavy execution stages — `scene_render` and `narrate_mux` — MUST run
via the Codex CLI through `manim_service/pipeline/codex_render.sh`. These stages
MUST NOT be executed by a Claude Code subagent writing Python directly.

This is a **pipeline non-negotiable.** The Producer command (`produce-video.md`)
already enforces this with a warning box at Step 7. Every Producer run must
follow it — if a Claude subagent is tempted to write the Manim scene file
directly, that is a violation.

### 32.1 Why this matters

| Issue | What happens without Codex | What happens with Codex |
|---|---|---|
| Context exhaustion | Claude orchestrator runs out of context while generating 30–40 KB of scene Python | Codex runs scene generation in a fresh context; Claude receives only the result |
| Quality | Claude in a large context produces degraded Manim code and skips checklist items | Codex follows the brief strictly, runs the Quality Checklist, re-renders on failure |
| Cost | Generating scene code in Claude burns expensive reasoning tokens | Codex handles code generation at lower cost |
| Skill enforcement | A Claude agent writing Manim code shortcuts the 3-phase workflow | Codex brief explicitly requires the 3-phase workflow; no shortcuts possible |

### 32.2 What the Codex brief MUST include (mandatory for quality)

Beyond CODEX_HANDOFF.md §5 base requirements, every `scene_render` brief must
explicitly contain (verbatim or by path reference):

1. **STYLE_BIBLE §§29-33** (new quality requirements from this update) — narration sync, conversational register, Gymnasium asset mandate, screen focus standards
2. **§3 updated font sizes** — 48pt standalone, 36pt panel
3. The user's **8 quality complaints** mapped to specific STYLE_BIBLE sections:
   - "Narrator describes the screen" → §29.2
   - "Equations not on screen when narrated" → §29.1
   - "Small illegible text" → §3 (updated)
   - "Overlaying artifacts" → §23 (Element Lifecycle)
   - "No Gymnasium assets" → §31
4. The reference video style summary (§33 below)

---

## 33. Screen Focus Standards — 3Blue1Brown Focal Discipline (mandatory)

At any given moment, the viewer's attention belongs to EXACTLY ONE primary
teaching object. The 3-panel layout (§4) exists for organized co-presence; it
is NOT a license for three competing focal points.

### 33.1 Primary element occupancy rule (QA G58)

The element being taught in the current beat must EITHER:
- Occupy ≥ 50% of the visible screen area, OR
- Be the sole object at `OPACITY_PRIMARY`

If two objects share `OPACITY_PRIMARY`, they must be visually bound by a
`trace_vector` or `cross_highlight_pair` at that exact moment — they are one
teaching unit, not two independent focal points.

### 33.2 The "equation introduction" shot (mandatory sequence)

When an equation appears for the **first time** in the video:

1. **Clear the stage** — all non-header elements fade to `OPACITY_SECONDARY` or
   `FadeOut`. The equation gets the full frame.
2. **Reveal the equation centered**, `font_size ≥ 48`, in the vertical middle of
   the frame. Use `Write` or `LaggedStart(Write(...))` for token-by-token reveal.
3. **Hold ≥ 2.0 s** before adding anything else — the viewer needs to see it whole.
4. **THEN** add the geometric counterpart to the right or below, with the equation
   repositioning if necessary.

Shortcutting this sequence (e.g., equation appears in a small left panel while
the environment is already visible in the center) is a QA G58 violation.

### 33.3 The "focused explanation" shot

When the narration is explaining a specific sub-expression (e.g., explaining what
`γ` means inside the Bellman equation):

1. All other tokens in the equation drop to `OPACITY_SECONDARY`.
2. The token being explained pulses with `Indicate` once, then returns to
   `OPACITY_PRIMARY`.
3. The geometric partner of that token (if one exists on screen) simultaneously
   highlights via `cross_highlight_pair`.
4. The camera does NOT move — this is a focus-within-frame operation only.

### 33.4 When the 3-panel layout is allowed

The 3-panel layout (equation LEFT + environment CENTER + code/chart RIGHT) is
only permitted in phases where:
- All three panels are **individually familiar** to the viewer from prior beats
- The current beat is showing a **relationship** among them (the algorithm step
  connecting all three), not introducing any new element
- All three panels have `font_size ≥ 36` for their primary text
- The three panels have been **individually taught** in prior beats; this phase
  is synthesis, not introduction

Introducing any new element into a 3-panel layout (e.g., adding the equation
for the first time while the environment is already showing) is banned.

---

## 34. Code Walkthrough Pattern — IDE-Style Step-Through Debugger (mandatory)

**This is a non-negotiable production pattern.** Every phase that explains
Gymnasium code (or any code) MUST follow this exact structure. No exceptions.

### 34.1 Layout

Two-panel split, environment-and-code only — no third panel:

| Side | Content |
|---|---|
| LEFT (≈45% width) | The Gymnasium environment (grid, sprites, current-state highlight). Anchored via `place_left_panel`. |
| RIGHT (≈45% width) | The actual Python/Gymnasium code, rendered IDE-style. Anchored via `place_mid_right_panel` or a dedicated `place_code_panel` helper. |

Center gutter (≈10%) is empty; it becomes the stage when an artifact
needs to be brought forward (see §34.4).

### 34.2 IDE rendering requirements

The code panel is NOT plain `Text`. It MUST be rendered as if displayed in
an IDE:

- **Monospaced font:** `Consolas`, `Menlo`, `Fira Code`, or any monospaced
  family available to manim. Plain proportional Text is banned for code.
- **Syntax highlighting:** keywords (def, for, in, if, return, import,
  class, lambda, with, as) in one accent color; built-ins (range, len,
  print, int, float, list, dict) in another; string literals in a third;
  numeric literals in a fourth; comments dimmed. The palette must reuse
  the STYLE_BIBLE 10-color set — no new hex literals.
- **Line numbers:** subdued line numbers in the gutter at
  `OPACITY_BACKGROUND` (≈0.17), `CODE_ACCENT` color.
- **Active-line highlight:** a translucent `Rectangle` behind the current
  line at `BG_PANEL` with `stroke_color=VALUE_COLOR` (the "debugger
  highlight"). The rectangle moves line-by-line as the walkthrough steps.
- **Font size:** `font_size ≥ 22` for code, `font_size ≥ 18` for line
  numbers. Never below.

A new helper `manim_service/scenes/code_ide.py::IDECodePanel` SHOULD be
authored when the next video needs it; until then, every code-walkthrough
phase must apply the rules above inline.

### 34.3 Step-through cadence

The walkthrough is a debugger session, not a reading. For each code line:

1. Move the debugger highlight to the current line (`smooth_move_to`,
   run_time ≤ 0.5 s).
2. Narration explains what THIS line does in the context of the env.
3. If this line produces an observable effect in the environment
   (state change, sampled outcome, value update, action selection), the
   effect MUST be shown on the LEFT panel at the same time the line
   executes. Narration ties them: "this line samples the next state — the
   left panel shows it land on cell 7".
4. `self.wait()` ≥ 1.5 s after the line executes (debugger pause).
5. Advance to next line.

A code line that produces no observable effect (an import, a constant
binding) gets ≤ 1.0 s with no environment update — keep it short.

### 34.4 Sampling / table-lookup interlude

When the code samples from or reads a table (transition probabilities,
reward table, policy distribution, action-value table), the walkthrough
PAUSES on that line and the referenced table is brought to center stage:

1. The env (LEFT) and the code panel (RIGHT) dim to `OPACITY_SECONDARY`.
2. The relevant table fades in **centered**, at `OPACITY_PRIMARY`, at
   `font_size ≥ 28`. No element on the LEFT or RIGHT remains at PRIMARY
   while the table is on stage.
3. The narration explains what is being sampled, walks one row of the
   table, and the env may briefly mirror that row (e.g., the three
   possible next states each glow once in turn) — but this brief env
   activity stays at `OPACITY_SECONDARY` underneath the centered table.
4. The table fades out completely (`FadeOut`, not dim — it does not need
   to persist), the env and code panel return to `OPACITY_PRIMARY`, and
   the walkthrough resumes from the next line.

**No overlap is permitted between the centered table and the code or env
panels.** If the renderer is producing simultaneous PRIMARY-opacity
elements in different parts of the frame during a sampling interlude,
that is a hard QA REJECT.

### 34.5 Forbidden patterns

- Showing the code panel and any third panel (chart, second equation,
  recap card) at PRIMARY simultaneously.
- Letting the centered sampling artifact (table) overlap the code or env
  panel — they must be fully dimmed first.
- Plain non-monospaced code text.
- Code without syntax highlighting (single-color code is banned).
- Stepping forward in code while a sampling-interlude artifact is still
  on screen.

---

## 35. Equation Dissection Pattern — Token-by-Token with Env Anchor (mandatory)

**This is a non-negotiable production pattern.** Every phase that introduces,
derives, or re-explains an equation MUST follow this exact structure.

### 35.1 Layout

Two-panel split, equation-and-env only — no code panel during equation
dissection:

| Side | Content |
|---|---|
| LEFT or CENTER | The equation, rendered as a decomposed `MathTex` array (every variable, operator, and grouping is its own token). |
| RIGHT or paired with the equation | The Gymnasium environment showing the agent's situation that the equation is describing. |

### 35.2 Dissection cadence

The equation is read token by token. For each token:

1. All other tokens drop to `OPACITY_SECONDARY`. The current token alone
   stays at `OPACITY_PRIMARY`. (Per §33.3.)
2. Narration explains what THIS token means **relative to the agent's
   actions in the environment**, not as a math symbol. Examples of
   acceptable narration framings:
   - "γ — the agent discounts future reward by this factor every step."
   - "Σ over a — the agent doesn't know which action it'll pick yet, so
     we average over all of them weighted by the policy."
   - "p(s', r | s, a) — what the environment does in response, sampled
     from this table."
   - "v_π(s') — the value the agent would expect from the next state,
     under the same policy."
3. The env (RIGHT) animates the corresponding agent behavior:
   - For state symbols: the relevant cell highlights.
   - For action symbols: an arrow or sprite move into that action.
   - For transition / probability terms: the sampled successors highlight
     in turn at their probability weights.
   - For value / return terms: the value label appears on the relevant
     cells.
   - For discount γ: an animated `γ^k` decay across cells the agent could
     visit.
4. `cross_highlight_pair(token, env_partner)` is mandatory for every
   token that has a geometric partner.
5. `self.wait()` ≥ 1.5 s after the token is explained.
6. Advance to next token.

### 35.3 Derivation chains

When an equation is derived in N steps (e.g., the 5-step Bellman
derivation), each step lives in its own phase and follows §35.2 for the
newly-introduced token(s) of that step. The previously-derived form
remains visible at `OPACITY_SECONDARY` above the current form; it is
never erased mid-derivation. The full chain is only erased after the
boxed final form is held in a dedicated full-frame solo (per §33.2).

### 35.4 Forbidden patterns

- Reading an equation left-to-right with no token-level highlights ("here
  is the Bellman equation:" then a 5-second wait) — this teaches nothing.
- Explaining a symbol as a math object alone ("γ is a real number between
  0 and 1") with no env anchor.
- A token at `OPACITY_PRIMARY` with no geometric partner highlighted on
  the env panel for tokens that have one.
- Showing the code panel during equation dissection. Code walkthroughs
  (§34) and equation dissections (§35) are **mutually exclusive** phase
  types — never combined in one phase.

### 35.5 QA enforcement

QA Phase 0 (see qa-agent SKILL.md) extracts a frame in the middle of
every equation-dissection phase. The frame must show:
- Exactly ONE token at `OPACITY_PRIMARY` in the equation.
- ALL other tokens visibly dimmer.
- The env panel showing the agent-behavior partner for that token.

Frames that show multiple tokens at PRIMARY simultaneously, or no env
anchor activity, are hard REJECTs.

---

## Mutual exclusion: §34 vs §35

A single phase is EITHER a code walkthrough (§34) OR an equation
dissection (§35) — never both. If a beat needs to connect code to an
equation, it must be its own phase that explicitly hands off (e.g.,
"the line we just walked through computes the inner sum of the equation
— let's look at that equation now"), with a clean transition between
the two-panel layouts.

---

## 36. Canvas Utilization & Legibility (mandatory, gate-enforced)

A layout that is technically correct (nothing clipped) but uses a third of the
screen is still a bad layout. Tiny artifacts marooned in an empty frame are
illegible the moment the video is watched on a phone or in a small embed — which
is how most students will watch it. **Fill the frame and make every artifact
readable on the smallest screen.**

### 36.1 Fill both dimensions (QA: canvas-utilization)

The bounding box of the phase's primary content must span **≥ 40 % of BOTH the
frame width and the frame height.** A multi-element phase whose content sits in a
thin horizontal band (everything at the vertical middle, empty top and bottom) or
a narrow column is a violation. The deterministic gate
(`layout_audit.py`, `LOW_CANVAS_USE`) reports `under-uses canvas: NN%×NN%` for any
phase that fails this; treat it as a layout defect to fix, not a cosmetic note.

### 36.2 Stack, do not cram (equation + artifact)

When an equation and a supporting artifact (backup tree, grid, chart) must be
on screen together, the default is **vertical**: the equation large across the
**top** band, the artifact large **centered below it.** Do NOT squeeze the
equation into a narrow side column to fit the artifact beside it — that shrinks
both. Horizontal side-by-side is only acceptable when each half independently
satisfies §36.1 and §36.3.

### 36.3 Minimum legible sizes (small-screen floor)

- Primary equation: `font_size ≥ 40` (a focal derivation step should fill the
  top band — `scale_to_fit_width(~12)` when long, not a fixed tiny size).
- Any primary text/caption a viewer must read: `font_size ≥ 24`.
- Secondary/decorative labels (node labels, dim context): `font_size ≥ 18`.
- Never park a focal artifact at < 40 % frame width when the rest of the frame
  is empty — scale it up to use the space.

### 36.4 Camera zoom is not a substitute for layout

Zooming the camera into one artifact (`zoom_to(... scale<1)`) leaves everything
placed for the full frame outside the view (clipped) and is a frequent source of
off-canvas defects. Lay out for the frame you are actually rendering. Reset the
camera (`zoom_reset` / `set_width(14.222)`) before a phase that places content
across the whole frame.

---

## 37. Segment-Based Authoring & Rendering (mandatory)

A concept video is **not** one monolithic scene file. A one-line fix to a
21-minute video must never require re-rendering 21 minutes. Author every video as
a **workspace of independently-renderable segments** and let the pipeline render
only what changed.

### 37.1 Workspace structure

    manim_service/workspaces/<lesson_id>/
        manifest.json            # ordered segments + quality flag
        segments/
            s01_intro.py         # exactly ONE Scene subclass per file
            s02_policy.py
            ...
        cache/                   # rendered segment MP4s, content-hash keyed
        <lesson_id>_silent.mp4   # the concatenated render product

### 37.2 Segments are self-contained

Each segment Scene **starts from and ends on the clean dark background** (fade in
from / fade out to black). No mobject, camera, or Python state is carried across
segment files — anything a segment needs, it rebuilds. This is what makes a
segment independently renderable and seamlessly concatenable. A segment maps to a
narration/teaching beat boundary (roughly the old "S<n>" segments).

### 37.3 Render only what changed

    # render changed segments + concat (caching reuses unchanged segments)
    python -m manim_service.pipeline.segment_render --lesson-id <id>
    # force one segment
    python -m manim_service.pipeline.segment_render --lesson-id <id> --segment s05_derivation

Editing one segment re-renders only that segment; a shared-module change
(`manim_service/scenes/*.py`) correctly busts every segment. The tool concatenates
the cached segment MP4s into `<lesson_id>_silent.mp4`.

### 37.4 Narration is applied ONCE, to the approved concat

Voiceover / BGM (`narrate_mux`) runs on the **final, QA-approved, concatenated
silent video** — never per segment, and never redone for a visual-only fix unless
the concatenated video itself changed. This avoids re-synthesising TTS every time
a single scene is patched. The per-phase `hold_until` timing contract still holds,
so narration aligns with the concat by construction.

---

## 38. Notation Expansion — Unpack the Sum (SIGNATURE TECHNIQUE, mandatory)

**This is the defining teaching move of the series — the thing that sets these
videos apart.** A compact expression (a sum, an expectation, a recursion — `Σ_a`,
`Σ_{s',r}`, `E_π`, the Bellman backup) *hides* the very thing the learner needs to
see. **Never leave a summation condensed when you first teach it.** Expand it into
its concrete terms, ground each term in the environment, then collapse it back so
the symbol finally *means* something. Every video from V-03 onward is built around
this move; a phase that introduces a summation without performing it is incomplete.

### 38.1 The four-beat expansion (apply to every first-time sum / expectation)

1. **Simplify to make it concrete.** Pin the free parameters to friendly values
   *on screen* and say so out loud — typically **γ = 1**, a single **deterministic
   best action**, and one specific starting state. The goal is real numbers, not
   abstract indices. ("Set gamma to 1 for a moment, and just take the best move.")

2. **Morph the operator into its actual terms.** Use `TransformMatchingTex` to turn
   the `Σ`/`E` into the written-out sum. The compact `v(s) = r + γ·v(s')` becomes the
   explicit `v(5) = 1 + 3 = 4`; a multi-outcome sum becomes `[t₁ + t₂ + t₃]` with each
   tᵢ a real number. The learner must SEE what the sigma contained.

3. **Ground every term on the grid, at the same instant.** As each term appears, the
   matching cell / transition / path lights up (`trace_vector`,
   `cross_highlight_pair`, `sprite_action_binding`). Term ↔ cell binding is
   mandatory: the equation and the environment tell the *same* story simultaneously.
   This is the cross-modal half — without it the expansion is just algebra.

4. **Collapse back to the general form.** Once the concrete expansion is understood,
   morph it back to the compact notation (restore γ, re-fold the sum). The learner now
   reads the symbol as the thing they just watched.

### 38.2 Build value from the goal backward

When showing where a state's value comes from, **propagate from the terminal/goal
back to the current state, one hop at a time**, so the learner watches value
accumulate along the path. "The goal is worth +1. The state before it inherits that
plus its own reward — so it's worth 4. And the state before *that*…" Each hop both
updates the number AND lights the cell. The recursion becomes a visible chain of
cells, not a symbol. (Worked example: v(5) = reward 1 + best-next-value 3 = 4.)

### 38.3 Worked numeric anchor (mandatory)

Every expansion carries **real numbers from the actual environment** through to a
final computed value. Abstract-only expansions are banned — the learner must leave
the beat with a concrete number they watched get built.

### 38.4 Relationship to §35

This supersedes "read the equation token by token" as the *centrepiece*. Token
highlighting (§35) still applies to the dissection, but the heart of any equation
beat is the **expand → ground → collapse** morph plus the synchronized grid
animation — never a static recitation of symbols.

---

## 39. Visual-First Teaching — Use the Whole Toolbox (mandatory, from V-03)

Equations and numbers are the *last* resort, not the first. Explain with the
environment, arrows, sprites, tables, and camera moves; reach for symbols only
once the picture is in the viewer's head. Assume the viewer knows nothing — make
every abstract object concrete before you operate on it.

### 39.1 Expand the *specific* sub-sum, in place (not the whole equation)

When a summation/expectation is the thing being taught, expand **only that one
operator** into its explicit terms while the rest of the equation stays put, then
fold it back. Use `manim_service.scenes.TexEquation`:

    eq  = TexEquation([("v","v(s)"), ("eq","="), ("sum","\\sum_a \\pi(a\\mid s)\\,q(s,a)")])
    eq2 = eq.expand(self, "sum", [("t0","\\tfrac14 q(s,L)"), ("p0","+"), ...])  # only Σ_a unfolds
    eq2.collapse(self, ("sum","\\sum_a \\pi(a\\mid s)\\,q(s,a)"), replacing=[...])

Whole-equation re-writes are banned for this beat — morph the **sub-part** the
narration is talking about. Each expanded term is grounded on the grid the instant
it appears (§38.1 step 3), with an **arrow** from the term to its cell.

### 39.2 One numeric channel, never two

Do NOT explain the same quantity twice numerically (e.g. a value on the grid AND
the same value in a side list). Pick ONE place the number lives — usually the cell
it belongs to — and carry the rest of the meaning with arrows, motion, and colour.
Redundant number panels read as a spreadsheet, not a lesson.

### 39.3 Put the agent in the world

Use the environment's real sprite (the FrozenLake **elf** via
`heatmap.place_agent / move_agent`). Let it walk the path you're describing, slip
when you discuss slipping, sit on the state under analysis. A moving character
holds attention far better than a highlighted rectangle.

### 39.4 Make abstractions concrete before using them (don't assume understanding)

Before an abstract object appears in an equation, show it as a picture:
- a **policy** → a state→action arrow grid (or a small table) the viewer can read,
  not just the symbol `π`;
- a **transition** → an arrow (or three, for slipping) on the grid;
- a **return / value** → a number that grows on a cell.
If a beat introduces a symbol the viewer hasn't *seen* as a concrete thing, it's
incomplete.

### 39.5 Use the full toolbox

Tables, labelled figures, arrows, sprite motion, and **camera moves** (zoom to the
cell under discussion, pan along a path) are all preferred to a static wall of
symbols. Pick the tool that makes the idea obvious to someone seeing it for the
first time.

### 39.6 Value grids: FLAT 2D grid, numbers that FLOAT above it

Keep the grid a **crisp, undistorted, top-down 2D grid** — the proven
`EnvironmentValueHeatmap` (real `ice/hole/goal` sprites). Show value as a **number
that floats above its cell**, with a soft drop shadow on the tile to sell the height.
Get the dimensional feel from the float + shadow, **not** from tilting the camera.

Hard-won rules (do not relitigate these — each was an explicit user rejection):
- **No camera tilt / no isometric 3D for the grid.** The gymnasium tiles are
  top-down art; under a `ThreeDScene` perspective they shear into ugly parallelograms.
  "The grid elements must stay 2D." A real 3D `ThreeDScene` iso grid was tried and
  rejected — do not revive `IsoValueGrid` / `DPE3DSegmentScene` for value grids.
- **No bars.** Bar-height encoding reads ambiguously at low values; rejected twice.
  The number is the signal.
- **Numbers float, they don't sit flat on the tile.** Flat-on-the-tile "looks cheap."
  Use `manim_service.scenes.FloatingValues` (binds to an `EnvironmentValueHeatmap`):
  `reveal_value` rises one chip into place (goal-backward fill, S2); `set_values`
  morphs the whole field (iteration/convergence, S4). Each chip is a dark `#0B1220`
  rounded backing + number, lifted above the cell with an elliptical drop shadow
  below it. It hides the heatmap's own flat labels automatically.
- **The agent moves; it never just stands there.** Drive the elf along the policy /
  the path being explained (`heatmap.place_agent` / `move_agent`). Fade it out before
  a value-fill if it would sit under a number.
- **Make the policy concrete.** Don't assume the viewer knows what "the policy" is —
  show it as a table (state → action probabilities) and let the agent actually run it.

These segments are plain 2D `BaseConceptScene`s, so the deterministic layout gate
covers them — keep them gate-clean.
