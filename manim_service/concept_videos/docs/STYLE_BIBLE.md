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

## 12. BGM Palette

**Style:** Contemplative, ambient, minimal. No percussion, no melody that competes with narration. Suitable for focused study.

**Volume envelope (standard):**

| Moment | Volume |
|---|---|
| Scene open (0–2 s) | Fade in 0→30% |
| Under narration | Duck to 15% |
| Hold frames / wait periods | 30% |
| Scene end (last 2 s) | Fade out to 0% |

**Loop requirement:** BGM loop points must be clean (no audible seam). Test with a 60 s loop before selecting a track.

---

## 13. Convergence Gates (summary)

A video is added to the library when **all** of the following are open:

1. RL Expert signs off `plan.md`
2. Technical Validator issues PASS on all code snippets and numerical examples
3. Voice & BGM Agent delivers `narration_script.md` and `audio_brief.md`
4. Transcript Writer delivers `captions.srt` and `captions.vtt` with no flagged gaps
5. QA Agent issues APPROVED on rendered video, audio, and captions
6. Series Continuity Agent issues CONSISTENT across video, narration, and captions
7. RL Expert issues final academic sign-off
8. Producer approves for library addition
