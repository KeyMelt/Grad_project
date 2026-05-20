# Plan: dp_policy_eval — Policy Evaluation (v3 rebuild, 2026-05-20)

**lesson_id:** dp_policy_eval
**Manim class:** `PolicyEvaluationConcept`
**Scene file:** `manim_service/concept_videos/dp_policy_eval_concept.py`
**Target duration:** content-determined; expected 7–9 minutes
**RL Expert status:** PENDING

This is the v3 rewrite. v1 and v2 are stashed in
`.archive/dp_policy_eval_v2_2026-05-20_stashed/`. Key v2 failures the
v3 plan corrects:

- **Abstract Bellman fork in empty space.** Removed. v3 stays inside
  the FrozenLake grid — three slippery-outcome cells light up *in the
  grid itself* (no synthetic tree off to one side).
- **Tiny purple-dot agent.** Removed. v3 uses the actual `elf_down.png`
  Gymnasium sprite.
- **Two equation morphs chaining in tight succession.** Reduced to ONE
  derivation — write the iterative form directly. The closed-form
  Bellman expectation is mentioned in narration but not animated as a
  separate morph (less visual chaos).
- **Generic ValueHeatmap with floating numbers.** Replaced by the new
  `EnvironmentValueHeatmap` which uses ice / hole / goal tile sprites
  as cell backgrounds with value labels bounded inside each cell.
- **Two separate grids.** Reduced to ONE env-grid that lives from
  Phase 1 through Phase 8 — same Mobject, gets smaller / migrates as
  later panels enter, but never disappears and reappears.

---

## Narrative hook

A FrozenLake grid. An elf at the start. The elf moves under a fixed
policy — sometimes ending up where it intended, sometimes (slippery
ice) ending up elsewhere. The viewer immediately sees the policy AND
the stochasticity AND the goal. Then the question: *given this policy,
how good is each cell?* The grid never leaves the screen; we make it
smaller as the equation and the code arrive, and we OVERLAY value
numbers on the same cells the elf was walking on. The viewer is
NEVER asked to translate between "the env" and "the algorithm" —
they live on the same canvas throughout.

---

## Color palette declaration (binding per STYLE_BIBLE §1 + §13)

| Constant | Hex | Used for |
|---|---|---|
| `STATE_COLOR` | `#38BDF8` | grid cell outline, `s` and `s'` subscripts in equations |
| `VALUE_COLOR` | `#FACC15` | value overlay tint, `v_π` / `v_k` / `v_{k+1}` tokens |
| `REWARD_COLOR` | `#34D399` | goal cell highlight, `r` token, ✓ markers |
| `PENALTY_COLOR` | `#F87171` | hole cell highlight |
| `POLICY_COLOR` | `#A78BFA` | the elf sprite tint, `π` and `E_π` tokens |
| `ACTION_COLOR` | `#FB923C` | action arrows on the grid, `a` token |
| `CODE_ACCENT` | `#64748B` | code panel chrome |

---

## Phase sequence (geometry-first, env-asset-driven throughout)

There is only one main visual element: the FrozenLake grid. Everything
else (equation, code, heatmap values) is overlaid on it, dismissed, or
positioned adjacent to it. The grid is the spine.

### Phase 1 — Motivation: the elf walks the grid (target ≈ 50 s)

- `show_header("Policy Evaluation", subtitle="Computing v_π under a fixed policy")`
- `mark_phase("motivation")`
- `EnvironmentValueHeatmap` instantiated with `values=[0.0]*16` (no
  tints visible yet) — this single object is the grid for the whole
  scene. Sized at width ≈ 5.6 and centred.
- `heatmap.place_agent(state=0, direction="down")` — the elf appears
  at the start tile.
- Caption (bottom): "FrozenLake. The agent follows a *policy* π — at
  every state, it picks each action with probability 1/4. The ice is
  slippery, so it sometimes ends up elsewhere."
- `assimilation_wait(2.5)`
- A short episode under equiprobable π: 4–5 cells walked. Use
  `heatmap.move_agent(state, direction)` so the elf sprite swaps
  direction at each step.
- Caption swap: "Given a fixed π, how good is each state? We can't
  enumerate every episode. We need to *compute* v_π(s) recursively."
- `assimilation_wait(2.5)`
- `heatmap.remove_agent()` — the agent leaves so the next phase can
  focus on a single state without a moving sprite confusing the frame.

### Phase 2 — One state, three slippery outcomes (target ≈ 60 s)

NO abstract fork diagram. The slippery outcomes are visualised
**inside the grid itself**, on the actual cells the agent might land
in. This is the key visual reform from v2 and matches the 3B1B "stay
inside the scene that introduced the question" principle.

- `mark_phase("slippery_outcomes")`
- The grid stays put. A SurroundingRectangle highlight (STATE_COLOR)
  appears around the focal cell — state 6 (row 1, col 2 — which is the
  cell adjacent to the hole at state 7).
- `s` MathTex label appears just above the focal cell, color
  `STATE_COLOR`.
- Caption: "Stand at state s. Pick one action — say, RIGHT."
- An `ACTION_COLOR` arrow appears from the focal cell pointing RIGHT.
  Small `a = RIGHT` label.
- `assimilation_wait(2.0)`
- Caption swap: "Because of the slippery ice, RIGHT can land on any of
  three cells with probability 1/3 each."
- **Three SHORT arrows appear** from the focal cell toward the three
  outcome cells *in the grid*: cells (2, 2) = state 10, (1, 3) = state 7
  (which is a hole), (0, 2) = state 2. Each outcome cell gets a faint
  STATE_COLOR halo, and a small probability label `1/3` next to the
  arrow tip.
- Caption swap: "Land on a hole — value zero. Land elsewhere — value
  is the future return from that cell, r + γ v_π(s')."
- A small floating annotation appears next to the focal-cell halo:
  `r + γ v_π(s')` (correctly colored — `r` in REWARD_COLOR, `v_π` in
  VALUE_COLOR, `s'` in STATE_COLOR).
- `ingestion_wait(2.5)`

### Phase 3 — Earn the iterative equation (target ≈ 70 s)

ONE equation, written once. No compact → sum → iterative chain. The
iterative form is the form that drives the algorithm; we write it
directly. The closed-form Bellman expectation is mentioned in
narration only.

- `mark_phase("equation_earned")`
- The grid `smooth_move_to` LEFT (shrink to height ≈ 3.0).
- `v_iter` MathTex is `Write`-animated to the right of the grid (one
  decomposed `MathTex` with component-array sub-mobjects, colored per
  the palette).
- `trace_vector` calls connect:
  - grid focal cell halo → `s` in v_iter (STATE_COLOR)
  - the elf-was-here motion trail / the `π` label that was on the
    focal-cell action arrow → `π(a|s)` token (POLICY_COLOR)
  - the goal cell on the grid → `r` token (REWARD_COLOR)
  - one of the three outcome cells from Phase 2 → `v_k(s')` token
    (VALUE_COLOR)
- Each `trace_vector` fires while the matching token is being written
  via `Write`, so the connection happens AT THE MOMENT of derivation,
  not after.
- `ingestion_wait(3.0)` — let the equation and its grounding settle
  on the screen for a real beat.
- Caption: "Treat the equality as an assignment. Update v_{k+1}(s)
  by averaging this expression over actions and outcomes — repeated
  until the values stop changing."
- `assimilation_wait(2.0)`

### Phase 4 — Iteration on the env-heatmap (target ≈ 150 s)

The grid we've been using becomes the value heatmap. Same tiles,
same shape, NOW with value overlays. No separate ValueHeatmap; the
EnvironmentValueHeatmap was always this, just with `values=[0.0]*16`.
Now we start updating those values.

- `mark_phase("iteration_demo")`
- Migrate the equation `v_iter` up-left (smaller, ~0.85x), grid stays
  CENTER-LEFT and grows back to height ≈ 3.6 to make the value
  overlays readable.
- Iteration counter `k = 0` and `Δ = 0.00` MathTex appear RIGHT of
  the heatmap.
- `heatmap.place_agent(state=14, direction="up")` — the elf reappears
  at state 14 as the "evaluator" walker. This is the **sprite-math
  binding** that ties motion to algebra.
- Single-cell binding demo:
  - `sprite_action_binding(...)` — elf at state 14, `v_{k+1}(s)`
    block in equation flashes
  - `sprite_action_binding(...)` — elf moves UP to state 10 (one of
    s' candidates), `v_k(s')` block flashes
  - `sprite_action_binding(...)` — elf returns to 14, `←` and
    `v_{k+1}(s)` block flash again to signal "write the value back"
  - `heatmap.remove_agent()` — the sprite has done its job
- Now the full multi-V_k sweep:
  - `heatmap.sweep_update(scene, _V_1, per_cell_run_time=0.20)` —
    yellow tint creeps onto state 14, all others stay dark
  - update `k_label` to "k = 1", `Δ_label` to "0.2500"
  - `ingestion_wait(2.0)` + assimilation_wait(6.0) for narration
  - `heatmap.sweep_update(scene, _V_2)` — tints spread to states 10,
    13; k=2; Δ updates
  - same for V_5, V_10, V_71 with shorter sweep run times (0.10) for
    the late iterations so the run doesn't feel slow
  - Final V_converged hold for narration

### Phase 5 — Code walkthrough with grid cross-highlights (target ≈ 110 s)

- `mark_phase("code_walkthrough")`
- Equation slides further up-left, heatmap shrinks toward LEFT, code
  panel enters RIGHT.
- Each `code.step(i)` is paired with `cross_highlight_pair` against
  the heatmap cells:
  - line 0 (outer loop) ↔ `heatmap.cell_bbox(state=14)` (the focal cell)
  - line 1 (inner loop) ↔ VGroup of next-state cells (10, 13, 14
    itself for slippery) — flashes the multiple-outcome group
  - line 2 (accumulator) ↔ `heatmap.cell_bbox(state=15)` (goal cell —
    where r=1 comes from)
  - line 3 (assignment) ↔ `heatmap.cell_bbox(state=14)` (the focal
    cell whose label updates)

### Phase 6 — Misconception (contrast pair, target ≈ 50 s)

- `mark_phase("misconception")`
- Clear the canvas of the iteration UI (k_label, Δ_label, code panel).
- TWO `EnvironmentValueHeatmap` instances side by side — one with
  `values=_V_CONVERGED` (equiprobable π, the one we just computed) and
  one with `values=[0.0]*16` (deterministic LEFT, never reaches goal).
- Labelled "π = equiprobable" and "π = always LEFT" (POLICY_COLOR).
- Caption: "Same algorithm, two different π. Going LEFT never reaches
  the goal: v_π ≡ 0. Evaluation tells you *how good a specific policy
  is* — not which policy is best."

### Phase 7 — Boundaries: terminals and asymptotic convergence (target ≈ 50 s)

- `mark_phase("boundaries")`
- Keep the equiprobable heatmap (LEFT); the LEFT-policy one fades.
- `Indicate` the hole cells (PENALTY_COLOR) and the goal cell
  (REWARD_COLOR). Caption: "Terminal cells never update. v(terminal)
  ≡ 0 by definition."
- Small `Axes`-based Δ-vs-k log plot to the right with the θ
  threshold marked at iteration 71.

### Phase 8 — Closing & DAG-next preview (target ≈ 30 s)

- `mark_phase("closing")`
- Dismiss the Δ plot. Equiprobable heatmap holds. A pill in CENTER:
  "Next: Policy Improvement — make π greedy w.r.t. v_π."
- Final caption + 4 s hold.

---

## Reserved-hemisphere layout matrix

| Phase | LEFT | CENTER | RIGHT |
|---|---|---|---|
| 1 | — | env-heatmap (elf walking) | — |
| 2 | — | env-heatmap (focal cell + outcome arrows in-grid) | — |
| 3 | env-heatmap (smaller, still alive) | — | v_iter equation + token notes |
| 4 | v_iter (up), env-heatmap (mid-LEFT-CENTER, larger) | — | k_label + Δ_label |
| 5 | v_iter (top), env-heatmap (small LEFT-CENTER) | — | CodeStepper |
| 6 | env-heatmap (equiprobable) | (gap) | env-heatmap (LEFT-only) |
| 7 | env-heatmap (equiprobable) | — | Δ-vs-k plot |
| 8 | env-heatmap (equiprobable) | "Next: Policy Improvement" pill | — |

The env-heatmap is the SAME Mobject from Phase 1 through Phase 8.
It migrates and resizes via `smooth_move_to` but never re-instantiates.

---

## Cross-highlight matrix (Phase 5)

| Code line index | Code line content (verbatim from specs.py) | Geometric pair (cross_highlight target) |
|---|---|---|
| 0 | `for action, action_prob in enumerate(policy[state]):` | focal cell halo (state 14) |
| 1 | `    for transition_prob, next_state, reward, done in env.unwrapped.P[state][action]:` | VGroup of next-state cells (states 10, 13, 14) |
| 2 | `        new_value += action_prob * transition_prob * (reward + gamma * V[next_state])` | goal cell (state 15) |
| 3 | `V[state] = new_value` | focal cell (state 14) — label updates |

---

## Mandatory helper usage

| Helper | Used in phase(s) |
|---|---|
| `EnvironmentValueHeatmap` | **1–8 (single instance, the spine)** |
| `EnvironmentValueHeatmap.place_agent` / `move_agent` / `remove_agent` | 1, 4 |
| `EnvironmentValueHeatmap.sweep_update` | 4 (5 sweeps) |
| `EnvironmentValueHeatmap.cell_bbox` | 5 (cross-highlight targets) |
| `BaseConceptScene.smooth_move_to` | 3, 4, 5 |
| `BaseConceptScene.ingestion_wait` | every phase boundary |
| `BaseConceptScene.mark_phase` | every phase |
| `equation_morph` | NOT used (single equation; no morph chain) |
| `trace_vector` | 3 (4 traces grounding v_iter tokens) |
| `cross_highlight_pair` | 5 (one per code step) |
| `sprite_action_binding` | 4 (single-cell binding demo before the sweep) |
| `CodeStepper` | 5 |
| `pan_to_follow` | 4 (during sprite binding) |
| `zoom_to` / `zoom_reset` | 3 (zoom for equation derivation), 4 (reset before sweep) |

---

## Code fidelity (specs.py.code_focus_lines verbatim)

```
for action, action_prob in enumerate(policy[state]):
    for transition_prob, next_state, reward, done in env.unwrapped.P[state][action]:
        new_value += action_prob * transition_prob * (reward + gamma * V[next_state])
V[state] = new_value
```

These are the EXACT four lines now stored in `specs.py`. No abbreviation,
no comments inserted, no pseudocode.

---

## Content density floor (STYLE_BIBLE §6) — self-check

- [x] Motivation (Phase 1): elf walks the grid under π
- [x] Theory derivation (Phase 3): iterative form written with 4 trace_vector groundings; no morph chain (intentional simplification — narration covers the closed-form connection)
- [x] Mandatory RL viz (Phase 4): EnvironmentValueHeatmap with 5 V_k snapshots
- [x] Code walkthrough (Phase 5): verbatim specs.py lines + cross-highlights
- [x] Iteration shown (Phase 4): V_0 → V_1 → V_2 → V_5 → V_10 → V_71 (5 sweeps, ≥3 required)
- [x] Boundary / misconception (Phase 6 + 7): contrast pair + terminal cells highlighted + Δ-vs-k plot
- [x] DAG-next connection (Phase 8): preview of policy improvement
