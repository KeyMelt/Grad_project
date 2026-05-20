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
| Primary equation (standalone) | 36 |
| Primary equation (inside panel) | 30 |
| Secondary / contextual equation | 24 |
| Inline annotation | 20 |

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
| Scene title | 36 |
| Scene subtitle | 22 |
| Panel title | 20 |
| Code lines | 19 |
| Caption line | 18 |
| Bar chart labels | 18–20 |
| Grid cell labels | 16–18 |

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
| transition probability | dynamics, environment dynamics |
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
