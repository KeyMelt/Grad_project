# Plan: policies_values_bellman — Policies, Value Functions, and the Bellman Expectation Equation

**lesson_id:** policies_values_bellman
**Manim class:** `PoliciesValuesBellmanConcept`
**Scene file:** `manim_service/concept_videos/policies_values_bellman_concept.py`
**Target duration:** content-determined; spec estimate ~19:00 (~1140 s). 12–22 min target window.
**RL Expert status:** APPROVED (advisory — UNREGISTERED_NEW_LESSON, spec §1)
**Series position:** V-02 of restructured curriculum. Direct sequel to V-01 (`rl_mdp_core`).
**Downstream hand-off:** V-03 (`dp_policy_eval`) — closing forward-tease only; no V-03 algebra in this video.

---

## Narrative hook

The FrozenLake grid from V-01 fades in, but this time *empty* — no agent, no
path, just sixteen ice tiles and the goal glowing at corner 15. A single
question appears in the caption: "Last time, the world responded. Today, the
agent decides." Then arrows bloom on every cell: first one thick purple
arrow per cell, all pointing right — a *deterministic* strategy. The arrows
melt into four short arrows per cell — an *equiprobable* one. Two policies,
same grid, both valid. The viewer has not seen an equation yet, but they
have already met $\pi$.

Then the arrows clear and the cells fill with numbers — yellow values fading
in across the grid, brightest near the goal, darkest in the middle, exactly
zero on the holes *and* on the goal. The narration plants the first hard
fact: "The goal has value zero. The reward is at the goal — but the value
isn't. Watch what the difference is."

Only then does algebra arrive: $v_\pi(s) \doteq \mathbb{E}_\pi[G_t \mid S_t=s]$
— the formal name for what the viewer has just seen colored on the grid.
And only then does the Bellman equation get *derived*, not asserted, by
expanding the return recursion from V-01 under a fixed policy. Each step is
shown on a one-step backup tree rooted at state 6 — so that when the boxed
equation finally appears full-screen, the two sums on its right-hand side
are not abstract. They are the two layers of branching the viewer has been
staring at for the whole derivation.

The video closes by showing the equation as an *equality* — a fixed-point
identity — and morphing its `=` to `←` for a heartbeat to plant the seed
that V-03 will turn this equation into an algorithm.

---

## Color palette declaration

Inherits V-01 palette verbatim — no new constants.

| Constant | Hex | Used for in this video |
|---|---|---|
| `STATE_COLOR` | `#38BDF8` | State labels (0–15), $s$, $s'$, $S_t$, $S_{t+1}$ tokens in equations, backup-diagram state nodes |
| `VALUE_COLOR` | `#FACC15` | $v_\pi$ symbols, $q_\pi$ symbols, value labels inside heatmap cells, $\gamma$ token, $q$-bar fills |
| `REWARD_COLOR` | `#34D399` | $r$, $R_{t+1}$, goal cell reward annotation (`+1.0` on entry), backup-diagram leaf reward labels |
| `POLICY_COLOR` | `#A78BFA` | $\pi$, $\pi(a\|s)$ label tokens, policy arrows on the policy-grid panels, action-branch labels in the backup diagram |
| `ACTION_COLOR` | `#FB923C` | Action symbols $a$, $A_t$, LEFT/DOWN/RIGHT/UP labels, action nodes in the backup diagram |
| `PENALTY_COLOR` | `#F87171` | Hole cells (5, 7, 11, 12) and their value labels (still 0, but cell tint is red) |
| `CODE_ACCENT` | `#64748B` | Transition-probability $p$ labels in the backup diagram (environment quantities — NEUTRAL, not policy), `CodeStepper` panel chrome |
| `BG_PANEL` | `#0F172A` | All panel fills |
| `BG_GRID` | `#1E293B` | Heatmap background where value=0 |

**Critical color rule (carried from V-01, called out in rl_expert_flag 7):**
Reward at the goal is `REWARD_COLOR` (green). Value at the goal cell is
`VALUE_COLOR` (yellow). The goal cell in Segment 3 must simultaneously
display a green `+1.0` reward marker AND a yellow `v_π(15)=0` label. This
co-occurrence is the visual cure for misconception M-2 and must not be
collapsed into a single color.

---

## Reserved-hemisphere layout matrix (MANDATORY — STYLE_BIBLE §16)

| Phase | LEFT (≈ −5.0 to −1.5 x) | CENTER (≈ −1.5 to +1.5 x) | RIGHT (≈ +1.5 to +5.0 x) |
|---|---|---|---|
| S1-P1 | — | FrozenLake grid (small, V-01 recap thumbnail) | Recap caption stack (3 lines) |
| S1-P2 | $G_t = R_{t+1} + \gamma G_{t+1}$ recursion (LEFT, callback) | Grid (CENTER, dimmed) | Recap caption (RIGHT, fades to "Today, we cook.") |
| S2-P3 | — | $\pi(a\|s) \doteq \Pr\{A_t=a \mid S_t=s\}$ definition (FULL SCREEN solo, font 48) | — |
| S2-P4 | Policy A (deterministic "all RIGHT") arrow grid 4×4 | Caption "Two valid policies. Same grid." | Policy B (equiprobable) arrow grid 4×4 |
| S2-P5 | Policy A grid (smaller) | Normalization annotation $\sum_a \pi(a\|s)=1$ (single cell highlighted) + "$\tfrac14+\tfrac14+\tfrac14+\tfrac14=1$" callout | Policy B grid (smaller, equiprobable becomes the *working policy* for the rest of the video) |
| S3-P6 | — | $v_\pi(s) \doteq \mathbb{E}_\pi[G_t \mid S_t=s]$ definition (FULL SCREEN solo, font 48) | — |
| S3-P7 | $v_\pi(s) \doteq \mathbb{E}_\pi[G_t \mid S_t=s]$ equation (repositioned LEFT) | Heatmap grid (CENTER) — cells fade in with yellow value labels, holes red with `v=0`, goal green-bordered with yellow `v=0` | Value legend / colorbar (RIGHT) |
| S3-P8 | Equation panel (LEFT, stable) | Heatmap (CENTER, stable; state 14 spotlit) | Caption: "Reward 0 here. Value 0.43 here. Value lives in the future." (RIGHT, attached to state 14 spotlight) |
| S3-P9 | Equation panel (LEFT, stable) | Heatmap (CENTER, state 14 spotlit, goal `+1.0` reward marker pulses) | Caption emphasizing "goal: reward +1, value 0" |
| S4-P10 | — | $q_\pi(s, a) \doteq \mathbb{E}_\pi[G_t \mid S_t=s, A_t=a]$ definition (FULL SCREEN solo, font 48) | — |
| S4-P11 | $v_\pi$ definition (LEFT, smaller) | Heatmap (CENTER, state 14 enlarged inset with 4 edge labels for $q_\pi(14, L/D/R/U)$) | $q_\pi$ definition (RIGHT) |
| S4-P12 | $v_\pi(14)=\frac14[q_\pi(14,L)+q_\pi(14,D)+q_\pi(14,R)+q_\pi(14,U)]$ (LEFT, single-equation panel) | State-14 inset with arrow connecting 4 $q$-bars → 1 $v$-value | — (cleared from $q$ definition to free RIGHT for next phase) |
| S5-P13 | — | Backup diagram rooted at state 6 (FULL SCREEN entry; two-level tree: state → 4 actions → for the RIGHT branch, 3 (s′,r) leaves) | — |
| S5-P14 | Step-1 derivation: $v_\pi(s) \doteq \mathbb{E}_\pi[G_t\|S_t=s]$ (LEFT, growing equation panel) | Backup diagram (CENTER, smaller; root lights) | — |
| S5-P15 | Step-2 derivation: $=\mathbb{E}_\pi[R_{t+1}+\gamma G_{t+1}\|S_t=s]$ (LEFT, morph) | Backup diagram (CENTER) — one edge labeled $R_{t+1}$, subtree labeled $G_{t+1}$ | — |
| S5-P16 | Step-3 derivation: outer sum $\sum_a \pi(a\|s)$ appears (LEFT, morph) | Backup diagram (CENTER) — 4 action nodes pulse `POLICY_COLOR` then `ACTION_COLOR` | — |
| S5-P17 | Step-4 derivation: inner sum $\sum_{s',r} p(s',r\|s,a)$ appears (LEFT, morph) | Backup diagram (CENTER) — 3 transition leaves under RIGHT pulse `CODE_ACCENT` | — |
| S5-P18 | Step-5 derivation: leaf relabel $\mathbb{E}[G_{t+1}\|S_{t+1}=s']\to v_\pi(s')$ (LEFT, morph) | Backup diagram (CENTER, leaves relabeled yellow) | — |
| S5-P19 | — | **Boxed Bellman equation** $v_\pi(s) = \sum_a \pi(a\|s)\sum_{s',r} p(s',r\|s,a)[r+\gamma v_\pi(s')]$ (FULL SCREEN solo, font 48, ≥ 2.5 s hold) | — |
| S6-P20 | LHS calculation: $v_\pi(6) \approx 0.039$ (LEFT panel, pulled from Segment 3 heatmap) | Boxed Bellman equation (CENTER, smaller) + arrows binding LHS↔heatmap, RHS↔backup-diagram numbers | RHS calculation: $\tfrac14\sum_a\sum_{s',r} p[\cdot] \approx 0.039$ (RIGHT panel, built term-by-term) |
| S7-P21 | Boxed Bellman equation (LEFT, smaller) | Heatmap (CENTER, smaller — reused from Segment 3) | `CodeStepper` (RIGHT) — Bellman-RHS evaluator at state 6 with `v_prev=0` |
| S7-P22 | Boxed Bellman equation (LEFT, stable, color-coded tokens) | Heatmap (CENTER, state 6 spotlit) | `CodeStepper` (RIGHT, sync with equation tokens via cross_highlight_pair) |
| S7-P23 | Boxed Bellman equation (LEFT, stable) | Heatmap (CENTER, state 6 spotlit) | Code output `0.000000` displayed; caption "One sweep is not enough — V-03 will iterate." |
| S8-P24 | — | Boxed Bellman equation (CENTER, FULL SCREEN — re-centered for final morph) | — |
| S8-P25 | — | Brief morph: `=` → `←` and $v_\pi(s)$ → $v_{k+1}(s)$ on LEFT, $v_\pi(s')$ → $v_k(s')$ on RHS (≤ 1.5 s) | — |
| S8-P26 | Caption: "V-02: the equation." | Caption: "V-03: the algorithm." | Final-hold takeaway card: "$v_\pi$ is the fixed point of the Bellman equation." (≥ 8.0 s hold) |

**Migration rules (explicit):**

- **Before S2-P3:** All S1 recap elements (small grid + caption stack + $G_t$
  recursion panel) `FadeOut` together to give the $\pi$ definition a clean
  full-frame entry.
- **Before S2-P4:** $\pi$ definition shrinks to a small header chip
  (`smooth_move_to` to top-of-frame) before the side-by-side policy grids
  appear in LEFT and RIGHT.
- **Before S3-P6:** Both policy grids `FadeOut`; the equiprobable grid is
  saved as a small inset object that will return in Segment 7 (do not lose
  it from the scene tree — `Group` it into a reusable holder).
- **Before S4-P10:** Heatmap shrinks into a small inset at lower-CENTER,
  re-emerging in Phase S4-P11 with state 14 enlarged. Avoid full FadeOut so
  the viewer perceives continuity with Segment 3.
- **Before S5-P13:** ALL of LEFT/CENTER/RIGHT clear (Segment 4 inset, $v_\pi$
  definition, $q_\pi$ definition) — the backup diagram needs a clean canvas
  for its first reveal. The equiprobable policy grid (held since S2-P5)
  reappears as a tiny thumbnail at the lower-right corner during S5 to
  remind the viewer which policy the algebra refers to. Set it to
  `OPACITY_BACKGROUND` (0.17) — present but inactive.
- **Before S6-P20:** Backup diagram fades; boxed Bellman equation
  `smooth_move_to` to CENTER (smaller); LHS and RHS calculation panels
  enter LEFT and RIGHT simultaneously.
- **Before S7-P21:** LHS and RHS calculation panels `FadeOut`; boxed
  Bellman equation migrates LEFT; heatmap re-enters CENTER (already
  preserved as a Group); `CodeStepper` enters RIGHT.
- **Before S8-P24:** Code panel, heatmap, captions all `FadeOut`; boxed
  Bellman equation enlarges back to full-frame center for the final morph.
- All migrations use `BaseConceptScene.smooth_move_to(...)` (STYLE_BIBLE §17,
  min `run_time` 1.2 s for distance > 2 units) followed by
  `self.ingestion_wait(2.5)` (§18).

**Reserved-hemisphere conflict check (Phase 4 audit pass):**
- No phase introduces a new RIGHT-hemisphere panel without first relocating
  or fading existing RIGHT content. (E.g. the policy B grid in S2-P4 occupies
  RIGHT, is migrated to a smaller scale at S2-P5, and is faded out before
  S3-P6.)
- The boxed Bellman equation never appears in two hemispheres at once. When
  it migrates between CENTER (P19, P24) and LEFT (P21–P23), prior copies are
  removed before the new placement.
- Heatmap appears in CENTER in Segment 3, leaves the scene as a preserved
  Group at S4-P10, and re-enters CENTER at S7-P21 — at no point does a
  second copy coexist with the original.

---

## Cross-highlight matrix (MANDATORY — STYLE_BIBLE §15.2)

This matrix governs Segment 7 (the single `CodeStepper` phase, S7-P21
through S7-P23). All lines are runnable Python copied verbatim from
teaching spec §9.2; the platform-contract `code_focus_lines` adopt a
subset and are preserved in adopted form.

| Step idx | Code line content (verbatim) | Geometric pair (cross_highlight target) |
|---|---|---|
| 0 | `env = gym.make("FrozenLake-v1", is_slippery=True)` | Full FrozenLake heatmap reveal (CENTER) — `Indicate` on the entire grid frame |
| 1 | `pi = np.ones((n_states, n_actions)) / n_actions` | Equiprobable policy arrow-grid overlay flashes in over the heatmap (4 short arrows per cell, `POLICY_COLOR`) |
| 2 | `assert np.allclose(pi.sum(axis=1), 1.0)` | Single cell (state 6) gets a "$\tfrac14+\tfrac14+\tfrac14+\tfrac14=1$" callout in `POLICY_COLOR` |
| 3 | `gamma = 0.99` | $\gamma$ token in the boxed Bellman equation (LEFT) pulses `VALUE_COLOR` |
| 4 | `v_prev = np.zeros(n_states)` | Heatmap (CENTER) momentarily dims its yellow values to BG_GRID (visual "this is just a guess") — restores to original colors at end of step |
| 5 | `state = 6` | State 6 cell in the heatmap gets a spotlight border (`STATE_COLOR`) |
| 6 | `v_new_6 = 0.0` | A floating yellow `0.0` accumulator appears at the top-right of state 6 (this will tick up — but in this iteration it stays 0) |
| 7 | `for action in range(n_actions):` | The four action nodes from the (now-hidden) backup diagram are briefly re-summoned as 4 short pulses around state 6 (`ACTION_COLOR`), then fade |
| 8 | `    for prob, next_state, reward, done in env.unwrapped.P[state][action]:` | The 3 successor cells (state 2, 7, 10 — for action RIGHT) pulse `CODE_ACCENT` to denote $p$ |
| 9 | `        v_new_6 += pi[state, action] * prob * (reward + gamma * v_prev[next_state])` | Each token in the boxed Bellman equation pulses `VALUE_COLOR` in sync with the matching variable in the code: `pi[state, action]` ↔ $\pi(a\|s)$ (`POLICY_COLOR`); `prob` ↔ $p(s',r\|s,a)$ (`CODE_ACCENT`); `reward` ↔ $r$ (`REWARD_COLOR`); `gamma * v_prev[next_state]` ↔ $\gamma v_\pi(s')$ (`VALUE_COLOR`) |
| 10 | `print(f"RHS of Bellman at state 6 with v_prev=0: {v_new_6:.6f}")` | The text `0.000000` materializes next to state 6 in the heatmap. **Caption appears:** "Heatmap shows the *converged* $v_\pi$. Code shows one iteration from $v_\text{prev}=0$. They will agree only after V-03 sweeps thousands of times." |

**Adopted platform-contract `code_focus_lines` (verbatim, from spec §10):**

```
env = gym.make('FrozenLake-v1', is_slippery=True)
pi = np.ones((n_states, n_actions)) / n_actions
assert np.allclose(pi.sum(axis=1), 1.0)
v_new_6 = 0.0
for action in range(n_actions):
    for prob, next_state, reward, done in env.unwrapped.P[6][action]:
        v_new_6 += pi[6, action] * prob * (reward + 0.99 * v_prev[next_state])
```

These are real Python. No pseudocode placeholders. `V[next_state]`-style real
variable names confirmed. **Code Fidelity audit (Phase 4 item 7): PASS.**

**Note for the Manim Expert:** the platform-contract list omits the
`n_states = env.observation_space.n`, `n_actions = env.action_space.n`,
`gamma = 0.99`, and `v_prev = np.zeros(n_states)` lines that the cross-highlight
matrix references as steps 3–4. Those lines must appear in the on-screen
`CodeStepper` source (they are runnable and necessary), even though they
are not part of the platform `code_focus_lines` tuple. Per STYLE_BIBLE §20,
the displayed source is the runnable file; the platform contract is a
*minimum* — additional supporting lines are allowed and required for
runnable code.

---

## Conversational Arc

The narration rhetorical journey for this lesson:

- **Opening tension:** "Last time, the world responded. Today, the agent
  decides." The viewer knows from V-01 what an MDP is, what a reward is,
  what a return is — but the agent in V-01 was a passive observer of slips.
  How does it actually *choose*?
- **First reveal (Segment 2):** A policy is a *rule for choosing actions*
  — not "the best" rule, just any rule. Two policies on the same grid:
  one deterministic, one random. Both valid. The viewer's intuition for
  "policy = function from state to action" is gently broken: a policy is
  a *distribution*.
- **Rising question (end of Segment 2):** OK — so given a policy, *how good
  is each state*? The agent is going to follow this rule. What does it get?
- **Second reveal (Segment 3):** A heatmap of values. State 14 (next to
  the goal) is bright yellow. State 0 is dim. The holes are red and zero.
  And — surprise — the *goal itself* is also zero. The narration explicitly
  defuses the "but the goal should be valuable!" reaction.
- **Bridging (Segment 4):** Each state has a single $v$-value, but also
  four $q$-values — one per action. The relationship $v_\pi=\sum_a\pi\,q_\pi$
  is shown as four bars stacking and averaging into one $v$ in state 14.
- **Key insight (Segment 5):** The *equation that ties the heatmap to the
  policy and the dynamics* is derived from the V-01 recursion, one step at
  a time. The viewer sees the outer sum (over actions, governed by $\pi$)
  and the inner sum (over (s',r), governed by $p$) emerge as two distinct
  layers of a backup tree. When the recursion closes in step 5, the
  viewer feels the equation snap into place.
- **Numerical resolution (Segment 6):** The boxed equation is not a hope —
  it is a checkable identity. LHS=RHS at state 6, both ≈ 0.039, both
  computed from the heatmap. The Bellman equation is *true*.
- **Code connection (Segment 7):** Real Gymnasium Python evaluates the
  RHS of the Bellman equation at state 6 from a `v_prev=0` initial guess.
  Output: 0.000000. The viewer expects 0.039 — but sees 0. The gap is the
  bridge to V-03.
- **Resolution:** "The Bellman equation is an *equality*, satisfied by the
  true $v_\pi$ at the fixed point. The code we just ran does one step —
  not enough. Tomorrow we sweep."
- **Forward hook:** A 1.5-second morph of `=` to `←` and $v_\pi$ to
  $v_{k+1}, v_k$. The next video has a name (`dp_policy_eval`) but no
  pseudocode appears. The seed is planted; V-03 will grow it.

---

## Screen Focus Budget

| Phase | Primary (OPACITY_PRIMARY = 1.0) | Secondary (OPACITY_SECONDARY = 0.4) | Background (OPACITY_BACKGROUND = 0.17) |
|---|---|---|---|
| S1-P1 | Recap caption stack (RIGHT) | V-01 grid thumbnail (CENTER) | Header |
| S1-P2 | $G_t = R_{t+1}+\gamma G_{t+1}$ recursion panel (LEFT) | Grid thumbnail (CENTER), caption (RIGHT) | Header |
| S2-P3 | $\pi(a\|s)$ definition (full frame, font 48) | None (all else FadeOut) | None |
| S2-P4 | Policy A arrow grid (LEFT) + Policy B arrow grid (RIGHT) — both PRIMARY for side-by-side contrast | "Two valid policies. Same grid." caption (CENTER) | Header |
| S2-P5 | Normalization annotation $\sum_a \pi(a\|s)=1$ on one cell (CENTER) | Both policy grids (smaller, flanking) | Header |
| S3-P6 | $v_\pi(s) \doteq \mathbb{E}_\pi[G_t\|S_t=s]$ definition (full frame, font 48) | None | None |
| S3-P7 | Heatmap reveal — yellow values fading in across grid (CENTER) | $v_\pi$ equation (LEFT) | Colorbar (RIGHT) |
| S3-P8 | State 14 spotlight + "Reward 0. Value 0.43. Value lives in the future." caption | Other heatmap cells, $v_\pi$ equation | None |
| S3-P9 | State 15 goal cell — green `+1.0` reward marker AND yellow `v=0` label (simultaneous, both PRIMARY) | "$v_\pi(15)=0$, but reward at goal is +1" caption | None |
| S4-P10 | $q_\pi(s, a)$ definition (full frame, font 48) | None | None |
| S4-P11 | State 14 inset with 4 $q$-bars on edges (CENTER) | $v_\pi$ definition (LEFT), $q_\pi$ definition (RIGHT) | None |
| S4-P12 | Linking identity $v_\pi(14)=\tfrac14\sum_a q_\pi(14,a)$ with stacked-bars arrow | State 14 inset (lower CENTER) | None |
| S5-P13 | Backup diagram (full frame) — root, 4 action branches, 3 transition leaves | None (clean canvas) | None |
| S5-P14 | Step-1 equation (LEFT) + root node lit (CENTER) | Rest of backup diagram | Equiprobable policy thumbnail (lower-right corner, faint) |
| S5-P15 | Step-2 equation morph (LEFT) + $R_{t+1}$ edge + $G_{t+1}$ subtree highlights (CENTER) | Rest of backup diagram | Policy thumbnail |
| S5-P16 | Step-3 outer sum $\sum_a \pi(a\|s)$ token (LEFT, NEW) + 4 action nodes pulsing `POLICY_COLOR`→`ACTION_COLOR` (CENTER) | Rest of equation (LEFT prior tokens) and rest of tree | Policy thumbnail |
| S5-P17 | Step-4 inner sum $\sum_{s',r} p(s',r\|s,a)$ token (LEFT, NEW) + 3 transition leaves pulsing `CODE_ACCENT` (CENTER) | Prior equation tokens, action nodes | Policy thumbnail |
| S5-P18 | Step-5 leaf relabel $v_\pi(s')$ (LEFT, NEW, `VALUE_COLOR`) + transition leaves relabeled yellow (CENTER) | Prior equation, action nodes, root | Policy thumbnail |
| S5-P19 | **Boxed Bellman equation, full frame, font 48** | None (all else FadeOut) | None |
| S6-P20 | LHS panel ($v_\pi(6) \approx 0.039$, LEFT) + boxed equation (CENTER smaller) + RHS panel ($\tfrac14\sum\cdots \approx 0.039$, RIGHT) | Arrows binding LHS↔heatmap memory and RHS↔backup-diagram memory | None |
| S7-P21 | `CodeStepper` panel entry (RIGHT) | Heatmap (CENTER), boxed Bellman equation (LEFT) | None |
| S7-P22 | Current code step + matching equation token + matching heatmap region (the synced trio for each step 0–9) | Other code lines, other equation tokens, other heatmap cells | None |
| S7-P23 | `0.000000` output next to state 6 + caption "One sweep is not enough" (RIGHT) | Code panel finished, equation, heatmap | None |
| S8-P24 | Boxed Bellman equation (CENTER, full frame, re-enlarged) | None | None |
| S8-P25 | `=` morphing to `←`; $v_\pi(s)$ morphing to $v_{k+1}(s)$; $v_\pi(s')$ morphing to $v_k(s')$ (CENTER) | Rest of equation | None |
| S8-P26 | Takeaway card "$v_\pi$ is the fixed point of the Bellman equation" (CENTER) | "V-02: equation. V-03: algorithm." flanking captions | None |

---

## Gymnasium Assets Required

**Environment:** FrozenLake-v1 (`is_slippery=True`)

**Asset verification command:**
```python
import gymnasium, os
asset_dir = os.path.join(os.path.dirname(gymnasium.__file__),
                         'envs', 'toy_text', 'img')
required = [
    'ice.png',       # safe tiles: 1,2,3,4,6,8,9,10,13,14
    'stool.png',     # start tile: state 0
    'hole.png',      # hole tiles: 5,7,11,12
    'goal.png',      # goal tile: 15
    'elf_up.png',    # agent sprite (for any directional pulses; light usage here)
    'elf_down.png',
    'elf_left.png',
    'elf_right.png',
]
missing = [f for f in required if not os.path.exists(os.path.join(asset_dir, f))]
assert not missing, f"MISSING_ASSETS: {missing}"
print("ASSET_DIR:", asset_dir)
# Verify at: <fill in from print output before rendering>
```

**Sprites used:**
- `stool.png` — state 0 (recap thumbnail, heatmap, code phase)
- `ice.png` — states 1, 2, 3, 4, 6, 8, 9, 10, 13, 14
- `hole.png` — states 5, 7, 11, 12 (also tinted `PENALTY_COLOR` overlay)
- `goal.png` — state 15 (also wrapped in green `REWARD_COLOR` border for the
  reward-vs-value teaching device in S3-P9)
- `elf_right.png` — sparing use only; this video is policy/value/equation
  focused, not agent-traversal focused. Optional appearance during S7
  (CodeStepper) sub-step that visualizes one action choice.

**Frame captures used:** NO direct `env.render()` rgb_array captures.
All composition is per-tile via `frozenlake_frame(soft_frame=True)` for the
heatmap and the policy-arrow grids. Sub-panels (policy A, policy B) are
two reduced-size composed frames side by side, NOT separate render calls.

**Asset wrapping (STYLE_BIBLE §16.1 / helper enforcement):** all tile
ImageMobjects pass through `frozenlake_frame(soft_frame=True)` — never raw
`ImageMobject` against the canvas.

---

## Phase sequence

The video has 8 segments mapping to 26 plan-phases. Each segment is a
self-contained teaching arc; together they form ONE continuous video.
Segment boundaries use a brief caption cross-fade and a 1.5 s pause.

Wait conventions:
- `self.wait(N)` = narrative pacing pause (assimilation, ≥ 0.6 s, default 1.5 s).
- `self.ingestion_wait(2.5)` = mandatory post-morph buffer (STYLE_BIBLE §18,
  ≥ 1.5 s, default 2.5 s).
- These appear in distinct slots; both are required.

---

### Segment 1 — V-01 Recap (Phases S1-P1 to S1-P2; target ~60 s, hard cap)

#### Phase S1-P1 — Cold open: empty grid

**Visual:** FrozenLake grid fades in at CENTER (small thumbnail size — this
is a *recap*, not the main panel). Header reads "Recap: where V-01 left
off." A 3-line caption stack appears stage-RIGHT:
- "States, actions, rewards (V-01)"
- "Transition probability $p(s', r \mid s, a)$ (V-01)"
- "Return $G_t = \sum_k \gamma^k R_{t+k+1}$ (V-01)"

**Helpers:**
- `BaseConceptScene.show_header("Recap", subtitle="What V-01 gave us")`
- `frozenlake_frame(grid_size=4, soft_frame=True, scale=0.5)` at CENTER
- `place_caption(caption_stack, region="RIGHT")`

**Narration intention:** Reactivate the V-01 mental model. The viewer needs
states, actions, rewards, $p$, $G_t$, and the recursion present and warm
before policy is introduced. Frame as "the kitchen we built last time."

**Screen primary:** Recap caption stack (RIGHT), with grid as visual anchor.

**Wait:** `self.wait(2.0)` (geometry entry minimum).

#### Phase S1-P2 — The recursion callback

**Visual:** The recap caption fades, leaving only the third item — "Return
$G_t = R_{t+1} + \gamma G_{t+1}$ — the recursion" — which `smooth_move_to`'s
to LEFT and enlarges to a one-line equation panel. Grid stays at CENTER
(dimmed to OPACITY_SECONDARY). New caption at RIGHT: "Today, we take the
*expectation* of this recursion under a policy." A subtle `trace_vector`
from "policy" word in the caption to (empty) center anticipates Segment 2.

**Helpers:**
- `equation_morph(prior_caption, recursion_eq)` for the line-to-equation
  transformation
- `BaseConceptScene.smooth_move_to(recursion_eq, LEFT_X)` (run_time ≥ 1.2 s)
- `place_caption("Today, we take the expectation of this recursion under a policy.", region="RIGHT")`

**trace_vector pairs:** none (no new equation tokens, only repositioning).

**Narration intention:** Plant the load-bearing identity. The viewer must
walk into Segment 2 expecting the recursion to be *expected under a policy*,
because that is exactly what the Bellman derivation in Segment 5 will do.

**Screen primary:** $G_t = R_{t+1} + \gamma G_{t+1}$ recursion panel (LEFT).

**Wait:** `self.wait(1.5)` then `self.ingestion_wait(2.5)` (scene-wide
reposition).

---

### Segment 2 — Policy as a Distribution (Phases S2-P3 to S2-P5; target ~3:30)

#### Phase S2-P3 — Policy definition, full-frame solo (STYLE_BIBLE §33.2)

**Visual:** All S1 elements `FadeOut`. The screen clears. The policy
definition appears full-frame center, font_size = 48, color-decomposed:

$$\pi(a \mid s) \doteq \Pr\{A_t = a \mid S_t = s\}$$

Component array (mandatory MathTex decomposition):

```python
pi_def = MathTex(
    "\\pi",            # 0  POLICY_COLOR
    "(",               # 1
    "a",               # 2  ACTION_COLOR
    "\\mid",           # 3
    "s",               # 4  STATE_COLOR
    ")",               # 5
    "\\doteq",         # 6
    "\\Pr\\{",         # 7
    "A_t",             # 8  ACTION_COLOR
    "=",               # 9
    "a",               # 10 ACTION_COLOR
    "\\mid",           # 11
    "S_t",             # 12 STATE_COLOR
    "=",               # 13
    "s",               # 14 STATE_COLOR
    "\\}",             # 15
    font_size=48,
)
pi_def[0].set_color(POLICY_COLOR)
pi_def[2].set_color(ACTION_COLOR);  pi_def[4].set_color(STATE_COLOR)
pi_def[8].set_color(ACTION_COLOR);  pi_def[10].set_color(ACTION_COLOR)
pi_def[12].set_color(STATE_COLOR);  pi_def[14].set_color(STATE_COLOR)
```

**Helpers:**
- `staggered_write(pi_def)` (LaggedStart, token-by-token reveal)
- `BaseConceptScene.show_header("Policies", subtitle="The agent's strategy")`
  (subtitle is HUMAN-READABLE — no lesson_id)

**trace_vector pairs:** None (full-frame solo reveal; no other on-screen
geometry exists at this moment).

**Narration intention:** Establish that a policy is *not yet* a strategy
for winning — it is *any* probability distribution over actions, indexed by
state. The Pr{...} notation is the canonical S&B form (eq. (3.12) p. 58).
The viewer should walk out of this beat understanding that $\pi$ is a
*table of probabilities*.

**Screen primary:** $\pi(a \mid s)$ definition (CENTER, full frame).

**Wait:** `self.wait(2.0)` (equation reveal minimum) then
`self.ingestion_wait(2.5)` after the morph completes.

#### Phase S2-P4 — Two policies, same grid

**Visual:** Definition shrinks via `smooth_move_to` to a header chip at the
top of the frame. Two 4×4 FrozenLake grids appear side by side — LEFT and
RIGHT.

- **LEFT grid (Policy A — deterministic "always RIGHT"):** every cell has a
  single thick arrow pointing right, color `POLICY_COLOR`. Above the grid:
  "Policy A: $\pi(\text{RIGHT} \mid s) = 1$ for every $s$".
- **RIGHT grid (Policy B — equiprobable random):** every cell has four
  short arrows (one per action), each labeled "$\tfrac14$" in
  `POLICY_COLOR`. Above the grid: "Policy B: $\pi(a \mid s) = \tfrac14$ for
  every $(s, a)$".

Center caption: "Two valid policies. Same grid."

**Helpers:**
- `PolicyArrowGrid(grid=frozenlake_frame(scale=0.4), policy_mode="deterministic", action=2)` for LEFT
- `PolicyArrowGrid(grid=frozenlake_frame(scale=0.4), policy_mode="equiprobable")` for RIGHT
- `staggered_write(...)` for the captions

**trace_vector pairs:**
- "$\pi(\text{RIGHT} \mid s) = 1$" caption → one of the LEFT-grid arrows
  (any cell)
- "$\pi(a \mid s) = \tfrac14$" caption → one of the RIGHT-grid arrow
  bundles (any cell, all four arrows)

**Narration intention:** Defeat misconception M-1 ("policy = function from
state to action"). The viewer must see two policies coexisting and feel
that "policy" is not a uniquely-determined object — it is a *choice*. The
deterministic vs. stochastic split is the same object in two cases of
its support, not two different objects.

**Screen primary:** Both arrow grids (PRIMARY together — this is a
side-by-side contrast, both panels are pedagogically active).

**Wait:** `self.wait(2.5)` (the viewer must absorb both grids
simultaneously — extended hold beyond minimum).

#### Phase S2-P5 — Normalization

**Visual:** Both policy grids shrink slightly toward their respective edges.
A single cell (state 6) is highlighted in BOTH grids (a spotlight `Square`
in `STATE_COLOR`). At CENTER, an annotation appears for the equiprobable
case:

$$\sum_{a \in \mathcal{A}(s)} \pi(a \mid s) = \tfrac14 + \tfrac14 + \tfrac14 + \tfrac14 = 1$$

Color-decompose so $\pi(a \mid s)$ tokens are `POLICY_COLOR`. A bracket
visually connects this sum to the four arrows in Policy B's state 6 cell.
Side text emphasizes: "Normalization. For every state, the policy is a
probability distribution."

**Helpers:**
- `MathTex(...)` with component decomposition (the four "$\tfrac14$" tokens
  are individually colored `POLICY_COLOR`)
- `equation_morph()` to bind the four arrow probabilities to the four
  fraction tokens
- `place_caption("Normalization. For every state, the policy is a probability distribution.", region="below")`

**trace_vector pairs:**
- $\sum_a$ token → the bracket above the four arrows in Policy B's state 6
- Each $\tfrac14$ token → its corresponding arrow

**Narration intention:** Establish the only structural constraint $\pi$
must satisfy. The viewer should leave Segment 2 with: "A policy is any
table where each row sums to 1." This forces them to internalize the
distribution interpretation before any value-function machinery appears.
The equiprobable policy is then *adopted* as the working policy for the
remainder of the video (rl_expert_flag 3).

**Screen primary:** Normalization equation (CENTER).

**Wait:** `self.wait(3.0)` then `self.ingestion_wait(2.5)`.

---

### Segment 3 — State-Value Function (Phases S3-P6 to S3-P9; target ~4:00)

#### Phase S3-P6 — Value definition, full-frame solo (STYLE_BIBLE §33.2)

**Visual:** All Segment 2 elements `FadeOut`. The screen clears (the
equiprobable Policy B grid is preserved as a `Group` for later reuse — see
migration rules). The $v_\pi$ definition appears full-frame center,
font_size = 48:

$$v_\pi(s) \doteq \mathbb{E}_\pi\!\left[\,G_t \;\big|\; S_t = s\,\right]$$

Component array (mandatory):

```python
v_def = MathTex(
    "v_{\\pi}",                # 0  base white, subscript pi POLICY_COLOR
    "(",                       # 1
    "s",                       # 2  STATE_COLOR
    ")",                       # 3
    "\\doteq",                 # 4
    "\\mathbb{E}_{\\pi}",      # 5  subscript pi POLICY_COLOR
    "\\bigl[",                 # 6
    "G_t",                     # 7  VALUE_COLOR
    "\\,\\big|\\,",            # 8
    "S_t",                     # 9  STATE_COLOR
    "=",                       # 10
    "s",                       # 11 STATE_COLOR
    "\\bigr]",                 # 12
    font_size=48,
)
v_def[0].set_color_by_tex("\\pi", POLICY_COLOR)  # the pi subscript only
v_def[0].set_color_by_tex("v", VALUE_COLOR)
v_def[2].set_color(STATE_COLOR)
v_def[5].set_color_by_tex("\\pi", POLICY_COLOR)
v_def[7].set_color(VALUE_COLOR)
v_def[9].set_color(STATE_COLOR);  v_def[11].set_color(STATE_COLOR)
```

**Helpers:**
- `staggered_write(v_def)`
- `BaseConceptScene.show_header("State-value function", subtitle="How good is this state under π?")`

**trace_vector pairs:** None (full-frame solo).

**Narration intention:** Name the question. "How good is state $s$ if we
follow $\pi$ from here?" — quantify with expected return. This is the S&B
eq. (3.12) form verbatim; the viewer should see the definition before they
see the heatmap so the heatmap is recognized as *the answer to a question
they have just been told to ask*.

**Screen primary:** $v_\pi$ definition (CENTER, full frame).

**Wait:** `self.wait(2.0)` then `self.ingestion_wait(2.5)`.

#### Phase S3-P7 — Heatmap reveal

**Visual:** Definition `smooth_move_to`'s to LEFT and shrinks to one-line
panel size. A 4×4 FrozenLake heatmap appears at CENTER. Cells fade in one
by one (Manhattan-distance from the goal), each labeled with its $v_\pi(s)$
value in `VALUE_COLOR` font_size=28. Cell shading is `VALUE_COLOR`-gradient
proportional to value (brighter = higher), with two overrides:
- Hole cells (5, 7, 11, 12) tinted `PENALTY_COLOR` (semi-transparent), still
  labeled `v=0`.
- Goal cell (15) bordered `REWARD_COLOR` (green), still labeled `v=0` in
  yellow.

A small colorbar on RIGHT shows the value→color mapping (0 to ~0.43).

**Values to display (best-estimate from spec §4.3; Technical Validator
will refine at $\theta=10^{-10}$ — every numeric label below is marked
`# NUMERIC_CLAIM` in code so the validator can find them):**

| s | v_π(s) | s | v_π(s) | s | v_π(s) | s | v_π(s) |
|---|---|---|---|---|---|---|---|
| 0 | 0.012 | 4 | 0.015 | 8 | 0.033 | 12 | 0.000 |
| 1 | 0.010 | 5 | 0.000 | 9 | 0.084 | 13 | 0.170 |
| 2 | 0.019 | 6 | 0.039 | 10 | 0.138 | 14 | 0.434 |
| 3 | 0.009 | 7 | 0.000 | 11 | 0.000 | 15 | 0.000 |

**Helpers:**
- `ValueHeatmap(env=frozenlake_grid, values=v_pi_array)` — instantiate with
  values pre-computed (no live `sweep_update` in this video; that is V-03's
  job). Use `cell_fade_in_sequence(manhattan_order=True)` so the viewer
  visually sees value-from-goal propagation as an animation cue, but NOT
  framed as iteration.
- `BaseConceptScene.smooth_move_to(v_def, LEFT_X)` (≥ 1.2 s run_time)
- `place_caption(colorbar, region="RIGHT")`

**trace_vector pairs:**
- Equation token $v_\pi(s)$ (LEFT) → state 14 cell label `0.43` (CENTER)
  — one trace at heatmap-completion moment

**Narration intention:** Reveal that the value function is a *grid of
numbers*, one per state. The brighter the cell, the higher the expected
return when starting there under the equiprobable policy. The viewer
should walk away with a *visual* mental model of $v_\pi$ — a shaded grid —
before any equation derivation begins. This sets up the visual reference
that Segment 5's algebra will compute.

**Screen primary:** Heatmap (CENTER, fully revealed).

**Wait:** `self.wait(2.0)` (heatmap entry minimum) then
`self.ingestion_wait(2.5)` (scene-wide reposition + fade-in completion).

#### Phase S3-P8 — Misconception M-2 defuse (state 14 spotlight)

**Visual:** State 14 cell zooms slightly (`Indicate` + `smooth_scale`) and
glows. A caption attached to the cell appears on RIGHT:
- Line 1: "Reward at state 14: 0"
- Line 2: "Value at state 14: 0.434"
- Line 3 (emphasized): "**Value lives in the future, not the present.**"

**Helpers:**
- `Indicate(heatmap.cell(14))` with scale_factor=1.15, color flash
- `place_caption(misconception_caption, region="RIGHT", anchor=heatmap.cell(14))`

**trace_vector pairs:**
- "Reward at state 14: 0" caption → heatmap cell 14 (zero reward indicator,
  shown as a small `r=0` floating annotation appearing briefly above the cell)
- "Value at state 14: 0.434" caption → heatmap cell 14 label

**Narration intention:** Defeat misconception M-2 ("value = immediate
reward") at the most extreme example. State 14 yields literally zero
immediate reward (FrozenLake gives 0 on every non-goal transition), yet
its $v_\pi$ is the highest non-terminal value on the grid. The viewer
should *feel the gap* between immediate reward and expected return. Per
rl_expert_flag 7: green vs. yellow distinction is the visual cure.

**Screen primary:** State 14 spotlight + caption.

**Wait:** `self.wait(2.5)` (extended for misconception absorption).

#### Phase S3-P9 — Misconception M-2 escalation (state 15 = goal at value 0)

**Visual:** Spotlight migrates to state 15 (goal). A green `+1.0` reward
marker pulses on entry (the reward awarded when *arriving* at the goal),
and the yellow `v_π(15)=0` label inside the cell pulses *simultaneously*.
Both appear visually side by side on the same cell.

Caption on RIGHT:
- Line 1: "Arriving at the goal: reward `+1.0` (green)."
- Line 2: "Value at the goal: `0` (yellow)."
- Line 3 (emphasized): "**Terminal states have $v_\pi = 0$. The reward
  belongs to the predecessor's expansion, not to the terminal.**"

(rl_expert_flag 4: this is the defusing of the "but the goal should be
valuable!" reaction. It is mandatory per spec §12.6.)

**Helpers:**
- `Indicate(heatmap.cell(15))` with two simultaneous color-annotations:
  - `goal_reward_marker = MathTex("+1.0", color=REWARD_COLOR)` pulsing above the cell
  - `goal_value_label = MathTex("v_\\pi(15)=0", color=VALUE_COLOR)` pulsing inside the cell
- `place_caption(terminal_explanation, region="RIGHT", anchor=heatmap.cell(15))`

**trace_vector pairs:**
- Caption "reward +1.0" → green marker above cell 15
- Caption "value = 0" → yellow label inside cell 15

**Narration intention:** Lock in the terminal-state convention before
Segment 5 begins. The viewer must accept that $v_\pi(s_T) \equiv 0$ before
the Bellman derivation, or they will trip on the recursion closure (the
leaf nodes of the backup diagram for state 6 include state 7, a hole, with
$v_\pi(7)=0$). This phase is the load-bearing boundary-condition lesson.

**Screen primary:** Goal cell with both green and yellow markers
co-displayed. Caption (RIGHT).

**Wait:** `self.wait(2.5)` (extended hold; misconception-critical) then
`self.ingestion_wait(2.5)`.

---

### Segment 4 — Action-Value Function and the Linking Identity (Phases S4-P10 to S4-P12; target ~2:00)

#### Phase S4-P10 — q-value definition, full-frame solo (STYLE_BIBLE §33.2)

**Visual:** Heatmap shrinks and `smooth_move_to`'s to a lower-CENTER inset
(NOT faded — preserved for continuity). $v_\pi$ definition (LEFT) stays
in place but dims to OPACITY_SECONDARY. The $q_\pi$ definition appears
full-frame, font_size = 48:

$$q_\pi(s, a) \doteq \mathbb{E}_\pi\!\left[\,G_t \;\big|\; S_t = s,\, A_t = a\,\right]$$

Component array:

```python
q_def = MathTex(
    "q_{\\pi}", "(", "s", ",", "a", ")",         # 0–5
    "\\doteq",                                    # 6
    "\\mathbb{E}_{\\pi}",                         # 7
    "\\bigl[", "G_t", "\\,\\big|\\,",             # 8–10
    "S_t", "=", "s", ",",                         # 11–14
    "A_t", "=", "a",                              # 15–17
    "\\bigr]",                                    # 18
    font_size=48,
)
q_def[0].set_color_by_tex("\\pi", POLICY_COLOR)  # subscript pi
q_def[0].set_color_by_tex("q", VALUE_COLOR)
q_def[2].set_color(STATE_COLOR);  q_def[4].set_color(ACTION_COLOR)
q_def[7].set_color_by_tex("\\pi", POLICY_COLOR)
q_def[9].set_color(VALUE_COLOR)
q_def[11].set_color(STATE_COLOR); q_def[13].set_color(STATE_COLOR)
q_def[15].set_color(ACTION_COLOR); q_def[17].set_color(ACTION_COLOR)
```

**Helpers:** `staggered_write(q_def)`.

**trace_vector pairs:** None (solo).

**Narration intention:** Introduce the *commitment-to-one-action* sibling
of $v_\pi$. The viewer already knows what $v_\pi$ measures; $q_\pi$ asks
"what if we *commit* to action $a$ once, then follow $\pi$ thereafter?"

**Screen primary:** $q_\pi$ definition (CENTER, full frame).

**Wait:** `self.wait(2.0)` then `self.ingestion_wait(2.5)`.

#### Phase S4-P11 — q-bars on state 14

**Visual:** $q_\pi$ definition `smooth_move_to`'s to RIGHT. State 14 from
the preserved heatmap inset enlarges to mid-CENTER. Four labeled bars (or
edge labels) appear on the four edges of cell 14:
- LEFT edge: $q_\pi(14, \text{LEFT})$ bar, height ∝ value
- DOWN edge: $q_\pi(14, \text{DOWN})$ bar
- RIGHT edge: $q_\pi(14, \text{RIGHT})$ bar (the highest — points toward goal)
- UP edge: $q_\pi(14, \text{UP})$ bar

All in `VALUE_COLOR`. Numeric labels next to each bar (best-estimate;
Technical Validator confirms). Each bar's action label (L/D/R/U) is in
`ACTION_COLOR`.

Format note: numeric values are NUMERIC_CLAIM-tagged; spec §4.4 calls them
"four values whose mean is $v_\pi(14) \approx 0.434$" — the Technical
Validator's live run is authoritative. Approximate per-action values are
**not** pre-committed in this plan; the Manim Expert should request the
exact four numbers from the Technical Validator before rendering.

**Helpers:**
- `ActionBarChart(state=14, values=q_pi_state14_values, action_labels=["L","D","R","U"], color=VALUE_COLOR)`
  configured to render as 4 edge-attached bars rather than the standard
  4-vertical-bar layout
- `BaseConceptScene.smooth_move_to(q_def, RIGHT_X)`

**trace_vector pairs:**
- $q_\pi(s, a)$ token in equation (RIGHT) → each of the four bars (one trace
  per bar; staggered so they don't visually chain)

**Narration intention:** Show that there are *four* action-values per state,
one per action. They're not separate quantities — they are the
decomposition of $v_\pi(14)$ across the four action choices. The bar
visualization is the visual cure for misconception M-5 ($v_\pi$ and
$q_\pi$ unrelated).

**Screen primary:** State 14 inset with 4 $q$-bars (CENTER).

**Wait:** `self.wait(2.0)` then `self.ingestion_wait(2.5)`.

#### Phase S4-P12 — Linking identity

**Visual:** Above the 4 bars, the linking identity appears in a panel that
`smooth_move_to`'s to LEFT:

$$v_\pi(s) = \sum_{a \in \mathcal{A}(s)} \pi(a \mid s)\, q_\pi(s, a)$$

For the equiprobable case at state 14:

$$v_\pi(14) = \tfrac{1}{4}\!\left[q_\pi(14, L) + q_\pi(14, D) + q_\pi(14, R) + q_\pi(14, U)\right]$$

Component array (the morph from the general form to the state-14 specific
form is the second equation morph required by content density floor §3):

```python
link_general = MathTex(
    "v_{\\pi}", "(", "s", ")",                     # 0–3
    "=",                                            # 4
    "\\sum_{a \\in \\mathcal{A}(s)}",               # 5
    "\\pi", "(", "a", "\\mid", "s", ")",            # 6–11
    "\\,", "q_{\\pi}", "(", "s", ",", "a", ")",     # 12–18
    font_size=44,
)
# Color: v_pi VALUE_COLOR; s STATE_COLOR; pi POLICY_COLOR; q_pi VALUE_COLOR; a ACTION_COLOR

link_state14 = MathTex(
    "v_{\\pi}", "(", "14", ")", "=",                # 0–4
    "\\tfrac{1}{4}",                                # 5
    "\\bigl[",                                      # 6
    "q_{\\pi}(14, L)", "+",                         # 7–8
    "q_{\\pi}(14, D)", "+",                         # 9–10
    "q_{\\pi}(14, R)", "+",                         # 11–12
    "q_{\\pi}(14, U)",                              # 13
    "\\bigr]",                                      # 14
    font_size=44,
)
```

A visual `Arrow` connects the bracket (the sum of the 4 bars) to the
single $v_\pi(14)$ value in the heatmap cell — making the
average-of-q-values literally point at the v-value.

**Helpers:**
- `equation_morph(link_general, link_state14)` (TransformMatchingTex)
- `Arrow(bracket_top, heatmap_cell_14, color=VALUE_COLOR)`

**trace_vector pairs:**
- Each $q_\pi(14, \cdot)$ token in `link_state14` → the corresponding bar
  on the inset

**Narration intention:** Solidify M-5 defeat. The viewer must *see* that
$v_\pi$ is the policy-weighted average of $q_\pi$. Under equiprobable
policy, this collapses to a literal average. The bracket-to-cell arrow
makes the averaging operation visible.

**Screen primary:** Linking identity (LEFT) + bracket-to-cell arrow.

**Wait:** `self.wait(2.0)` then `self.ingestion_wait(2.5)`.

---

### Segment 5 — Bellman Derivation (Phases S5-P13 to S5-P19; target ~5:30, load-bearing)

This is the load-bearing segment per rl_expert_flag 1. All five derivation
steps from spec §3.4 must be animated. The backup diagram (Stage 1) must
precede the algebra (Stages 2 and 3 — Stage 3 lives in Segment 6).

#### Phase S5-P13 — Backup diagram entry

**Visual:** ALL Segment 4 elements `FadeOut` (the heatmap is preserved as a
hidden `Group` for Segment 7's reuse — see migration rules). The screen
clears. A backup diagram rooted at state 6 grows from CENTER, level by
level:

- **Root (top):** state node labeled "$v_\pi(6)$" — circle, `STATE_COLOR`
  border, `VALUE_COLOR` label
- **Level 2 (action nodes):** four nodes branching down, labeled
  $\pi(L\|6), \pi(D\|6), \pi(R\|6), \pi(U\|6)$. Branch labels in
  `POLICY_COLOR`; action node fills in `ACTION_COLOR`.
- **Level 3 (transition leaves, ONLY under the RIGHT action node initially —
  others appear in later derivation phases):** three nodes branching from
  RIGHT, labeled with successor states $s'$ and transition labels
  $p(2\|6,R)=\tfrac13, p(7\|6,R)=\tfrac13, p(10\|6,R)=\tfrac13$.
  - Successor state nodes in `STATE_COLOR`.
  - Probability labels in `CODE_ACCENT` (gray — environment quantities,
    NEUTRAL; **rl_expert_flag enforced**: do NOT use `POLICY_COLOR` for $p$).
  - Reward label `r=0` attached to each leaf in `REWARD_COLOR` (for state
    7, the hole, `r=0` since FrozenLake holes don't give negative reward —
    they just terminate).

A small thumbnail of the equiprobable policy grid appears at lower-right
corner, faint (`OPACITY_BACKGROUND` 0.17), as a quiet reminder that this
algebra refers to π=equiprobable.

**Helpers:**
- `BackupDiagram(root_state=6, action_branches=4, transition_branches={"RIGHT": [(2, 1/3, 0), (7, 1/3, 0), (10, 1/3, 0)]}, palette=PALETTE)` — custom helper invocation
- `staggered_write(...)` for the per-level reveal
- Lower-right thumbnail: `frozenlake_arrow_grid(scale=0.18, opacity=0.17, policy="equiprobable")`

**trace_vector pairs:**
- $\pi(R\|6)$ branch label → an arrow in the lower-right policy thumbnail
  (a faint trace, just to ground that $\pi$ in this tree is the
  equiprobable policy from Segment 2)
- $p(2\|6, R)$ leaf label → state 2 in the (faint) thumbnail
- $p(7\|6, R)$ leaf label → state 7 (hole) in the thumbnail

**Narration intention:** Make the two layers of branching *physically
separate* before any algebra runs. Defeat misconception M-3 ("Bellman has
one sum") visually. The outer level is policy randomness (the agent
choosing $a$ given $s$); the inner level is environment randomness (the
world choosing $(s', r)$ given $(s, a)$). Two layers, two sums — the
algebra in P14–P18 will name them.

**Screen primary:** Backup diagram (CENTER, full reveal).

**Wait:** `self.wait(2.5)` then `self.ingestion_wait(2.5)` (full-frame
reveal).

#### Phase S5-P14 — Derivation Step 1: definition

**Visual:** Backup diagram shrinks slightly and `smooth_move_to`'s to
CENTER-right. The root node ($v_\pi(6)$) pulses. A new equation panel
opens at LEFT and writes:

$$v_\pi(s) \;\doteq\; \mathbb{E}_\pi\bigl[\,G_t \,\big|\, S_t = s\,\bigr]$$

This is identical to Segment 3 P6's definition (intentional callback —
the derivation begins with what we already know).

Component array: reuse `v_def` from S3-P6 verbatim; this allows
TransformMatchingTex in later phases.

**Helpers:**
- `staggered_write(v_def_step1)` at LEFT panel position
- `Indicate(backup_diagram.root_node, color=VALUE_COLOR)`

**trace_vector pairs:**
- $v_\pi(s)$ token in equation (LEFT) → root node label "$v_\pi(6)$" in
  backup diagram

**Narration intention:** Anchor the derivation in the definition. The
viewer is told: "we are starting from the definition of $v_\pi$ — the
expected return under $\pi$ — and we are going to unfold it." This is
the conceptual entry point.

**Screen primary:** Step-1 equation (LEFT) + lit root node.

**Wait:** `self.wait(1.5)`.

#### Phase S5-P15 — Derivation Step 2: substitute the recursion

**Visual:** The equation morphs (`TransformMatchingTex`) — $G_t$ token is
replaced by $R_{t+1} + \gamma G_{t+1}$. The new equation reads:

$$v_\pi(s) = \mathbb{E}_\pi\bigl[\,R_{t+1} + \gamma G_{t+1} \,\big|\, S_t = s\,\bigr]$$

Component array:

```python
v_step2 = MathTex(
    "v_{\\pi}(s)", "=",                          # 0–1
    "\\mathbb{E}_{\\pi}", "\\bigl[",             # 2–3
    "R_{t+1}",                                   # 4  REWARD_COLOR
    "+",                                          # 5
    "\\gamma",                                   # 6  VALUE_COLOR
    "G_{t+1}",                                   # 7  VALUE_COLOR
    "\\,\\big|\\,", "S_t", "=", "s", "\\bigr]",   # 8–12
    font_size=42,
)
```

On the backup diagram (CENTER), one edge (from root to action-RIGHT node,
say) is labeled $R_{t+1}$ in `REWARD_COLOR`, and the subtree beneath is
brace-labeled $G_{t+1}$ in `VALUE_COLOR`.

**Helpers:**
- `equation_morph(v_def_step1, v_step2)` (TransformMatchingTex with
  matching transform on shared tokens; new tokens fade in)
- `Brace(subtree_under_action_R, label="G_{t+1}", color=VALUE_COLOR)`

**trace_vector pairs:**
- $R_{t+1}$ token → labeled edge in backup diagram
- $G_{t+1}$ token → braced subtree

**Narration intention:** Apply the V-01 recursion identity. This is the
moment the recap from Segment 1 pays off — the viewer recognizes
$G_t = R_{t+1} + \gamma G_{t+1}$ from V-01 and follows the substitution.
"The expected return from $s$ — split into the next reward plus the
discounted return from the next state."

**Screen primary:** Step-2 equation (LEFT) + labeled edge in diagram.

**Wait:** `self.wait(1.5)` then `self.ingestion_wait(2.5)` (equation morph).

#### Phase S5-P16 — Derivation Step 3: outer sum over actions (policy randomness)

**Visual:** The expectation $\mathbb{E}_\pi$ unfolds by *conditioning on
the action*. The equation morphs to:

$$v_\pi(s) = \sum_{a} \pi(a \mid s)\, \mathbb{E}\!\left[\,R_{t+1} + \gamma G_{t+1} \,\big|\, S_t = s,\, A_t = a\,\right]$$

The new tokens are $\sum_a$ and $\pi(a \mid s)$ — `POLICY_COLOR` for the
$\pi$ tokens. **This is the outer sum** (rl_expert_flag 2).

Simultaneously on the backup diagram, the four action nodes pulse together
(stagger): first `POLICY_COLOR` (the $\pi$ branch labels light), then
`ACTION_COLOR` (the action nodes themselves). The visual mapping:
"$\sum_a \pi(a \mid s)$" *is* the four action branches summed.

Component array:

```python
v_step3 = MathTex(
    "v_{\\pi}(s)", "=",                                  # 0–1
    "\\sum_{a}",                                          # 2  default (sum is structural)
    "\\pi(a\\mid s)",                                    # 3  POLICY_COLOR (whole sub-expression)
    "\\,\\mathbb{E}", "\\bigl[",                          # 4–5  (no pi subscript now — conditioned)
    "R_{t+1}", "+", "\\gamma", "G_{t+1}",                # 6–9
    "\\,\\big|\\,", "S_t", "=", "s", ",", "A_t", "=", "a", "\\bigr]",  # 10–18
    font_size=42,
)
v_step3[3].set_color(POLICY_COLOR)
v_step3[6].set_color(REWARD_COLOR);  v_step3[8].set_color(VALUE_COLOR); v_step3[9].set_color(VALUE_COLOR)
v_step3[12].set_color(STATE_COLOR);  v_step3[17].set_color(ACTION_COLOR)
```

**Helpers:**
- `equation_morph(v_step2, v_step3)` (matching transform; new tokens
  $\sum_a$ and $\pi(a\|s)$ fade in)
- Backup diagram: `staggered_pulse(action_nodes, colors=[POLICY_COLOR, ACTION_COLOR], stagger=0.3)`

**trace_vector pairs:**
- $\sum_a$ token → the four action nodes as a Group
- $\pi(a \mid s)$ token → the four $\pi$ branch labels

**Narration intention:** Name the policy's role in the expectation. "$\pi$
is one of the two sources of randomness in $\mathbb{E}_\pi$ — pull it out
as a sum over actions, weighted by $\pi(a\|s)$." The viewer should see the
outer sum *appear* on the equation as the action nodes simultaneously
*activate* on the diagram. The two halves of the cross-modal link arrive
together.

**Screen primary:** Step-3 equation (LEFT, with new $\sum_a \pi$ tokens
glowing) + pulsing action nodes (CENTER).

**Wait:** `self.wait(2.0)` then `self.ingestion_wait(2.5)`.

#### Phase S5-P17 — Derivation Step 4: inner sum over (s', r) (environment randomness)

**Visual:** The inner expectation unfolds by *conditioning on next state
and reward*. The equation morphs to:

$$v_\pi(s) = \sum_{a} \pi(a \mid s) \sum_{s', r} p(s', r \mid s, a)\, \bigl[\,r + \gamma\, \mathbb{E}_\pi[G_{t+1} \mid S_{t+1} = s']\,\bigr]$$

The new tokens are $\sum_{s', r}$ and $p(s', r \mid s, a)$ — `CODE_ACCENT`
for the $p$ tokens (environment quantities, neutral). The reward
expectation inside the brackets becomes a concrete $r$ (since we're
conditioning on the value).

**This is the inner sum** (rl_expert_flag 2 — kept separate from the
outer sum).

Simultaneously on the backup diagram, the three transition leaves under
the RIGHT action node pulse `CODE_ACCENT`. The $p$ labels light. The leaf
reward $r$ tokens pulse `REWARD_COLOR`.

**Narration callout (rl_expert_flag 9):** This is one of the two permitted
uses of the term "dynamics function" — when explicitly naming
$p(s', r \mid s, a)$ as "the environment's dynamics function." The other
permitted use was the V-01 recap (S1-P1) implicitly. After this phase, the
term "transition probability" or just "$p$" is used.

Component array:

```python
v_step4 = MathTex(
    "v_{\\pi}(s)", "=",                                       # 0–1
    "\\sum_{a}", "\\pi(a\\mid s)",                            # 2–3 POLICY_COLOR pi
    "\\sum_{s',r}",                                            # 4
    "p(s',r\\mid s,a)",                                       # 5  CODE_ACCENT
    "\\bigl[", "r",                                            # 6–7  REWARD_COLOR
    "+", "\\gamma",                                            # 8–9  VALUE_COLOR
    "\\mathbb{E}_{\\pi}[G_{t+1}\\mid S_{t+1}=s']",            # 10
    "\\bigr]",                                                 # 11
    font_size=40,
)
v_step4[3].set_color(POLICY_COLOR)
v_step4[5].set_color(CODE_ACCENT)
v_step4[7].set_color(REWARD_COLOR)
v_step4[9].set_color(VALUE_COLOR)
```

**Helpers:**
- `equation_morph(v_step3, v_step4)`
- Backup diagram: `staggered_pulse(transition_leaves_under_RIGHT, colors=[CODE_ACCENT, REWARD_COLOR], stagger=0.25)`

**trace_vector pairs:**
- $\sum_{s', r}$ token → the three transition leaves under RIGHT (as Group)
- $p(s', r \mid s, a)$ token → the three $p$ labels on the leaf edges
- $r$ token → any leaf reward label

**Narration intention:** Name the environment's role in the expectation.
"$p$ is the other source of randomness — pull it out as a sum over
$(s', r)$, weighted by $p(s', r \mid s, a)$." Critically, the OUTER sum
remains over actions; the INNER sum is over transitions. The viewer must
not see them collapsed (rl_expert_flag 2 — non-negotiable).

**Screen primary:** Step-4 equation (LEFT) + pulsing transition leaves
(CENTER).

**Wait:** `self.wait(2.0)` then `self.ingestion_wait(2.5)`.

#### Phase S5-P18 — Derivation Step 5: recursion closes

**Visual:** The inner expectation $\mathbb{E}_\pi[G_{t+1} \mid S_{t+1}=s']$
is *recognized* as $v_\pi(s')$ — the definition from Step 1 applied to the
*next* state. The equation morphs:

$$v_\pi(s) = \sum_{a} \pi(a \mid s) \sum_{s', r} p(s', r \mid s, a)\, \bigl[\,r + \gamma\, v_\pi(s')\,\bigr]$$

The transition leaves in the backup diagram (state 2, 7, 10) get their
labels replaced from $\mathbb{E}_\pi[G_{t+1} \mid S_{t+1}=s']$ to
$v_\pi(2), v_\pi(7), v_\pi(10)$ — all in `VALUE_COLOR`. State 7 (the hole)
shows $v_\pi(7) = 0$ in the leaf, calling back to S3-P9's terminal
convention.

**The recursion has closed:** $v_\pi$ appears on both sides of the equation.

Component array:

```python
v_step5 = MathTex(
    "v_{\\pi}(s)", "=",                                       # 0–1
    "\\sum_{a}", "\\pi(a\\mid s)",                            # 2–3
    "\\sum_{s',r}", "p(s',r\\mid s,a)",                       # 4–5
    "\\bigl[",                                                 # 6
    "r", "+", "\\gamma",                                       # 7–9
    "v_{\\pi}(s')",                                            # 10  VALUE_COLOR
    "\\bigr]",                                                 # 11
    font_size=40,
)
v_step5[3].set_color(POLICY_COLOR)
v_step5[5].set_color(CODE_ACCENT)
v_step5[7].set_color(REWARD_COLOR)
v_step5[9].set_color(VALUE_COLOR)
v_step5[10].set_color(VALUE_COLOR)
```

**Helpers:**
- `equation_morph(v_step4, v_step5)` — the only token that visibly changes
  is index 10: $\mathbb{E}_\pi[G_{t+1} \mid S_{t+1}=s']$ → $v_\pi(s')$
- Backup diagram: replace leaf labels with $v_\pi(\cdot)$ tokens via
  TransformMatchingTex

**trace_vector pairs:**
- $v_\pi(s')$ token (LEFT) → each of the three relabeled leaves (3 traces,
  staggered)

**Narration intention:** The pedagogical payoff. "The expected return
*from the next state* is *by definition* the value of the next state.
Substitute, and the recursion closes — $v_\pi$ on the left, $v_\pi$ inside
the sum on the right. The value function is the *fixed point* of this
equation."

**Screen primary:** Step-5 equation (LEFT) + relabeled leaves (CENTER).

**Wait:** `self.wait(2.5)` (extended; this is the conceptual climax) then
`self.ingestion_wait(2.5)`.

#### Phase S5-P19 — Boxed Bellman equation, full-frame solo (STYLE_BIBLE §33.2)

**Visual:** Backup diagram and step-5 equation BOTH `FadeOut`. The screen
clears. The final boxed Bellman equation appears full-frame center,
font_size = 48, wrapped in a thin `Rectangle` border:

$$\boxed{\;v_\pi(s) \;=\; \sum_{a} \pi(a \mid s) \sum_{s', r} p(s', r \mid s, a)\,\bigl[\,r + \gamma\, v_\pi(s')\,\bigr]\;}$$

The equation reuses `v_step5`'s component array exactly (so future morphs
in Segments 7 and 8 can TransformMatchingTex against it).

A header chip above reads: "**The Bellman expectation equation for $v_\pi$**"
(rl_expert_flag: full qualifier, not just "Bellman's equation").

**Helpers:**
- `equation_morph(v_step5, v_step5_boxed)` with `Rectangle` border added
- `BaseConceptScene.show_header("The Bellman expectation equation for v_π", subtitle="S&B eq. (3.14), p. 59")`

**trace_vector pairs:** None (solo, final form).

**Narration intention:** Deliver the equation. The viewer has just earned
it. The narration here is sparse: "This is the Bellman expectation equation
for $v_\pi$. It is the single most important relationship in everything
that follows." Long hold (≥ 2.5 s) gives the equation room to land.

**Screen primary:** Boxed Bellman equation (CENTER, full frame, font 48).

**Wait:** `self.wait(3.0)` (full-frame solo with extended hold per STYLE_BIBLE
§33.2 minimum) then `self.ingestion_wait(2.5)`.

---

### Segment 6 — Numerical Consistency Check at State 6 (Phase S6-P20; target ~1:00)

#### Phase S6-P20 — LHS = RHS at state 6

**Visual:** Boxed Bellman equation shrinks via `smooth_move_to` to CENTER
(reduced scale). Two calculation panels appear flanking it:

- **LEFT panel — LHS:** A clean readout. Title: "LHS: $v_\pi(6)$ from
  Segment 3 heatmap." Below it, a small heatmap inset (just the state 6
  cell highlighted) with the value `0.039` displayed prominently
  (NUMERIC_CLAIM, Technical Validator authoritative).

- **RIGHT panel — RHS:** The Bellman RHS computed term by term.
  Format: "$\tfrac14 \sum_a \sum_{s', r} p(s', r \mid 6, a) [r + 0.99 \cdot v_\pi(s')]$"
  evaluated by walking through the 4 actions × ~3 transitions each, with
  the heatmap values inserted. Result: `≈ 0.039` (NUMERIC_CLAIM).

Below both panels: equality sign and "$\approx 0$ (within $\theta=10^{-10}$)"
caption.

Visual arrows bind LHS readout ↔ heatmap (memory: Segment 3), and RHS
readout ↔ backup diagram tree (memory: Segment 5). The viewer
*remembers* both contexts.

**Helpers:**
- `place_caption("LHS: v_π(6) from heatmap", region="LEFT", anchor=heatmap_cell6_inset)`
- `place_caption("RHS: Bellman equation evaluated at s=6", region="RIGHT", anchor=rhs_breakdown)`
- `equation_morph(...)` step-by-step inside the RHS panel as each term is
  computed
- `Arrow` connectors for the LHS↔heatmap and RHS↔diagram bindings

**trace_vector pairs:**
- LHS panel "$v_\pi(6) \approx 0.039$" → boxed equation's left-hand-side $v_\pi(s)$ token
- RHS panel result "$\approx 0.039$" → boxed equation's right-hand-side
  $\sum_a \pi \sum_{s',r} p [r + \gamma v_\pi(s')]$ token group

**Narration intention:** Demonstrate that the Bellman equation is an
*equality*, not an assignment. The true $v_\pi$ satisfies it at every
state. The viewer sees both sides evaluated to the same number — the
identity is *checked*, not promised. (rl_expert_flag: this is the
visual proof of "fixed-point identity, not algorithm.")

**Screen primary:** LHS panel + RHS panel + boxed equation (all PRIMARY
for the duration of this phase).

**Wait:** `self.wait(3.0)` (extended numerical hold) then
`self.ingestion_wait(2.5)`.

---

### Segment 7 — CodeStepper Bridge to V-03 (Phases S7-P21 to S7-P23; target ~3:00)

This is the single CodeStepper segment per spec §9.2.

#### Phase S7-P21 — Code panel entry

**Visual:** LHS and RHS panels from S6-P20 `FadeOut`. The boxed Bellman
equation migrates LEFT via `smooth_move_to`. The Segment 3 heatmap
(preserved Group) reappears at CENTER. A `CodeStepper` panel enters RIGHT.

The code lines (per cross-highlight matrix; spec §9.2 verbatim plus
supporting lines per STYLE_BIBLE §20):

```python
import gymnasium as gym
import numpy as np

env = gym.make("FrozenLake-v1", is_slippery=True)
n_states = env.observation_space.n        # 16
n_actions = env.action_space.n            # 4

# Equiprobable random policy: pi(a|s) = 1/4 for every state-action pair.
pi = np.ones((n_states, n_actions)) / n_actions
assert np.allclose(pi.sum(axis=1), 1.0)   # row sums = 1 (normalization)

# One step of the Bellman expectation equation at state 6, given a v_prev guess.
gamma = 0.99
v_prev = np.zeros(n_states)               # initial guess
state = 6
v_new_6 = 0.0
for action in range(n_actions):
    for prob, next_state, reward, done in env.unwrapped.P[state][action]:
        v_new_6 += pi[state, action] * prob * (reward + gamma * v_prev[next_state])
print(f"RHS of Bellman at state 6 with v_prev=0: {v_new_6:.6f}")
```

**Helpers:**
- `CodeStepper(lines=above_python, theme=CODE_ACCENT_PALETTE, font_size=22)`
- `BaseConceptScene.smooth_move_to(boxed_bellman, LEFT_X)`
- Heatmap re-entry: `FadeIn(preserved_heatmap_group)` at CENTER (reduced
  scale to coexist with LEFT equation and RIGHT code)

**trace_vector pairs:** None on entry (sync phase is P22).

**Narration intention:** Translate equation to executable code. The
viewer should perceive the code panel as the *runnable instantiation* of
the equation just derived.

**Screen primary:** `CodeStepper` (RIGHT).

**Wait:** `self.wait(1.5)` then `self.ingestion_wait(2.5)` (scene-wide
reposition).

#### Phase S7-P22 — Code walkthrough with cross-highlights

**Visual:** `CodeStepper.step(i)` advances through the 11 steps in the
cross-highlight matrix (i ∈ 0..10). Each step:
- Active code line highlights in CODE_ACCENT panel.
- The geometric pair from the matrix `Indicate`s in sync via
  `cross_highlight_pair(scene, code.lines[i], target_geometry)`.
- For step 9 specifically (the term-accumulator line), the four equation
  tokens in the boxed Bellman equation pulse in sequence:
  `pi[state, action]` (POLICY_COLOR) → `prob` (CODE_ACCENT) → `reward`
  (REWARD_COLOR) → `gamma * v_prev[next_state]` (VALUE_COLOR).

Per-step wait: `self.wait(1.5)` (STYLE_BIBLE §6 sync-step minimum).

**Helpers:**
- `CodeStepper.step(i)` for each i in 0..10
- `cross_highlight_pair(scene, code.lines[i], target)` for each step
- Inside step 9 specifically: `SynchronizedFocusGroup(equation_tokens, code_token_pulses)`

**trace_vector pairs:** Handled by the cross-highlight matrix — no
additional traces required in this phase.

**Narration intention:** Demonstrate that each variable in the Python
corresponds to exactly one token in the equation, and exactly one region
of the grid. The triple (code variable, equation token, geometry) is the
load-bearing pedagogical link. Per spec §9.2, the narration ties together
`pi[state, action]` ↔ $\pi(a \mid s)$, `prob` ↔ $p(s', r \mid s, a)$,
`reward` ↔ $r$, and `gamma * v_prev[next_state]` ↔ $\gamma v_\pi(s')$.

**Screen primary:** Synced trio for each step.

**Wait:** 11 × `self.wait(1.5)` = 16.5 s of per-step beats; final
`self.ingestion_wait(2.5)` after step 10.

#### Phase S7-P23 — Output `0.000000` and V-03 hand-off setup

**Visual:** Code execution finishes. Output `0.000000` materializes next
to state 6 in the heatmap (in CODE_ACCENT panel text style). A caption
appears at RIGHT:
- Line 1: "Heatmap value: $v_\pi(6) \approx 0.039$"
- Line 2: "Code RHS with $v_\text{prev}=0$: $0.000000$"
- Line 3 (emphasized): "**One sweep is not enough — V-03 will iterate.**"

The heatmap visibly pulses, contrasting the converged values with the
zero output. (rl_expert_flag 5: deliberate V-03 hand-off, not a bug.)

**Helpers:**
- `Text("RHS of Bellman at state 6 with v_prev=0: 0.000000", color=CODE_ACCENT)` materializes
- `place_caption(handoff_caption, region="RIGHT")`
- `Indicate(heatmap)` for the value-vs-zero contrast pulse

**trace_vector pairs:**
- "Heatmap value: 0.039" caption → heatmap cell 6 (preserves Segment 3 binding)
- "Code RHS: 0.000000" caption → the `print` output line in CodeStepper
- "One sweep is not enough" caption → the boxed Bellman equation's
  $v_\pi(s')$ token (it is *because* $v_\pi(s')$ on the RHS is currently
  $v_\text{prev}(s') = 0$ that the sweep produces 0)

**Narration intention:** Plant the V-03 hand-off explicitly. The viewer
sees the *gap* between the heatmap (converged $v_\pi$) and the code output
(one iteration from zero). The narration: "Today we *proved* the equation
holds at the true $v_\pi$. Tomorrow we *compute* the true $v_\pi$ by
running this code thousands of times, with $v_\text{prev}$ updated each
sweep, until nothing changes. That algorithm is V-03 — *policy
evaluation*." (No V-03 algebra or pseudocode is shown.)

**Screen primary:** Output text + hand-off caption.

**Wait:** `self.wait(3.0)` then `self.ingestion_wait(2.5)`.

---

### Segment 8 — Forward-Tease and Final Hold (Phases S8-P24 to S8-P26; target ~1:30)

#### Phase S8-P24 — Boxed equation re-centered

**Visual:** Code panel, heatmap, and S7 caption `FadeOut`. The boxed
Bellman equation `smooth_move_to`'s from LEFT back to CENTER and enlarges
to full-frame solo (reusing the S5-P19 size and position).

**Helpers:**
- `BaseConceptScene.smooth_move_to(boxed_bellman, ORIGIN, scale=1.0)`
- Other elements `FadeOut`

**trace_vector pairs:** None.

**Narration intention:** Re-establish the equation as the central object
before the final morph. Give it visual primacy.

**Screen primary:** Boxed Bellman equation (CENTER, full frame).

**Wait:** `self.wait(2.0)` then `self.ingestion_wait(2.5)`.

#### Phase S8-P25 — `=` → `←` brief morph (V-03 forward-tease)

**Visual:** Within ≤ 1.5 s, three simultaneous morphs (rl_expert_flag 8 —
strict time budget):
- `=` token (equation index 1) → `\leftarrow` (assignment arrow)
- $v_\pi(s)$ token (LHS) → $v_{k+1}(s)$ (with subscript $k+1$ in CODE_ACCENT)
- $v_\pi(s')$ token (RHS) → $v_k(s')$ (with subscript $k$ in CODE_ACCENT)

The morph holds for ~1.0 s in its V-03 form, then **reverts** back to the
V-02 equality form. This visually plants the seed without committing to
V-03 algebra (rl_expert_flag 8: no pseudocode, no iteration counter, no
convergence theorem).

A brief caption flashes at the top: "Next video: equation → algorithm."

**Helpers:**
- `equation_morph(v_step5_boxed, v_step5_assignment_form, run_time=1.5)`
- After 1.0 s hold: `equation_morph(v_step5_assignment_form, v_step5_boxed, run_time=1.0)` — revert
- `place_caption("Next: equation → algorithm.", region="ABOVE", run_time=1.0)`

**trace_vector pairs:**
- $\leftarrow$ token → caption "equation → algorithm" (one trace, brief)

**Narration intention:** Plant the V-03 seed. The narration is sparse:
"What if you don't *know* $v_\pi$? What if you only have a guess? Turn
the equation into an *assignment*. Sweep every state. Repeat until nothing
changes. That algorithm is the next video — *policy evaluation*." Then
the V-02 equality form returns, leaving the viewer with the equation as
they should remember it.

**Screen primary:** Morphing equation tokens (CENTER).

**Wait:** Total `self.wait(1.5)` covering the morph + hold + revert
(rl_expert_flag 8: ≤ 1.5 s morph cap). Then `self.ingestion_wait(2.5)`.

#### Phase S8-P26 — Takeaway and final hold

**Visual:** Equation shrinks toward upper-CENTER. A takeaway card appears
at lower-CENTER: "**$v_\pi$ is the fixed point of the Bellman equation.**"
Two flanking captions at LEFT and RIGHT:
- LEFT: "V-02: the equation."
- RIGHT: "V-03: the algorithm."

All highlights deactivate. All mobjects at OPACITY_PRIMARY (stable, no
pulses). Header reads "Coming next: dp_policy_eval" (HUMAN-READABLE; the
lesson_id appears only because the V-03 video is in the library — this is
recall-aid, not a slug exposure).

**Helpers:**
- `place_caption(takeaway, region="CENTER_BELOW_EQ", color=VALUE_COLOR, font_size=36)`
- `place_caption("V-02: the equation.", region="LEFT")`
- `place_caption("V-03: the algorithm.", region="RIGHT")`
- `BaseConceptScene.show_header("Coming next: dp_policy_eval", subtitle=None)`

**trace_vector pairs:** None.

**Narration intention:** Close the loop. The viewer leaves knowing that
$v_\pi$ is a *fixed point* of the Bellman equation — a recipe for being
*self-consistent* under $\pi$ — and that V-03 will turn this property
into a computable algorithm. No new content; pure consolidation.

**Screen primary:** Takeaway card (CENTER).

**Wait:** `self.wait(8.0)` — final hold (extended per spec §10.2 pacing
notes for the takeaway).

---

## Layout matrix (Phase-by-Phase summary)

See the **Reserved-hemisphere layout matrix** section above — that table is
authoritative. This section is a compact restatement for the Pacing Linter
and Visual Director hand-off.

| Phase | LEFT | CENTER | RIGHT |
|---|---|---|---|
| S1-P1 | — | grid thumbnail | recap captions |
| S1-P2 | $G_t$ recursion | grid (dim) | "today we cook" |
| S2-P3 | — | $\pi(a\|s)$ DEF (solo) | — |
| S2-P4 | policy A grid | "two valid policies" | policy B grid |
| S2-P5 | policy A (small) | $\sum_a \pi = 1$ annotation | policy B (small) |
| S3-P6 | — | $v_\pi$ DEF (solo) | — |
| S3-P7 | $v_\pi$ DEF | heatmap | colorbar |
| S3-P8 | $v_\pi$ DEF | heatmap + state 14 spotlight | M-2 caption |
| S3-P9 | $v_\pi$ DEF | heatmap + goal spotlight | terminal caption |
| S4-P10 | $v_\pi$ DEF (dim) | $q_\pi$ DEF (solo) | — |
| S4-P11 | $v_\pi$ DEF | state 14 inset + 4 q-bars | $q_\pi$ DEF |
| S4-P12 | $v=\sum_a \pi q$ | state 14 inset + arrow | — |
| S5-P13 | — | backup diagram (full) | — |
| S5-P14 | derivation step 1 | backup diagram | — |
| S5-P15 | derivation step 2 | backup diagram + $R_{t+1}, G_{t+1}$ labels | — |
| S5-P16 | derivation step 3 | backup diagram + action pulses | — |
| S5-P17 | derivation step 4 | backup diagram + transition pulses | — |
| S5-P18 | derivation step 5 | backup diagram + leaves → $v_\pi(s')$ | — |
| S5-P19 | — | BOXED BELLMAN (solo) | — |
| S6-P20 | LHS panel | boxed equation (small) | RHS panel |
| S7-P21 | boxed equation | heatmap | CodeStepper enters |
| S7-P22 | boxed equation (tokens pulse) | heatmap (cells pulse) | CodeStepper (line pulses) |
| S7-P23 | boxed equation | heatmap | "$0.000000$" + hand-off caption |
| S8-P24 | — | boxed equation (full re-enlarge) | — |
| S8-P25 | — | equation morphing $=$→$\leftarrow$ | — |
| S8-P26 | "V-02: equation" | takeaway card | "V-03: algorithm" |

---

## Pacing beats

| Phase | After | Duration |
|---|---|---|
| S1-P1 | Recap thumbnail + captions revealed | `self.wait(2.0)` |
| S1-P2 | Recursion panel migrates LEFT | `self.wait(1.5)` + `self.ingestion_wait(2.5)` |
| S2-P3 | $\pi$ definition full-frame written | `self.wait(2.0)` + `self.ingestion_wait(2.5)` |
| S2-P4 | Two policy grids side by side | `self.wait(2.5)` |
| S2-P5 | Normalization annotation completed | `self.wait(3.0)` + `self.ingestion_wait(2.5)` |
| S3-P6 | $v_\pi$ definition full-frame written | `self.wait(2.0)` + `self.ingestion_wait(2.5)` |
| S3-P7 | Heatmap fully revealed | `self.wait(2.0)` + `self.ingestion_wait(2.5)` |
| S3-P8 | State 14 spotlight + caption | `self.wait(2.5)` |
| S3-P9 | Goal cell green-yellow co-display | `self.wait(2.5)` + `self.ingestion_wait(2.5)` |
| S4-P10 | $q_\pi$ definition full-frame written | `self.wait(2.0)` + `self.ingestion_wait(2.5)` |
| S4-P11 | 4 q-bars drawn on state 14 inset | `self.wait(2.0)` + `self.ingestion_wait(2.5)` |
| S4-P12 | Linking identity + bracket arrow | `self.wait(2.0)` + `self.ingestion_wait(2.5)` |
| S5-P13 | Backup diagram fully drawn | `self.wait(2.5)` + `self.ingestion_wait(2.5)` |
| S5-P14 | Step 1 equation written; root pulses | `self.wait(1.5)` |
| S5-P15 | Step 2 morph done; edge + subtree labeled | `self.wait(1.5)` + `self.ingestion_wait(2.5)` |
| S5-P16 | Step 3 morph done; action nodes pulse | `self.wait(2.0)` + `self.ingestion_wait(2.5)` |
| S5-P17 | Step 4 morph done; transition leaves pulse | `self.wait(2.0)` + `self.ingestion_wait(2.5)` |
| S5-P18 | Step 5 morph done; recursion closes | `self.wait(2.5)` + `self.ingestion_wait(2.5)` |
| S5-P19 | Boxed Bellman equation full-frame solo | `self.wait(3.0)` + `self.ingestion_wait(2.5)` |
| S6-P20 | LHS=RHS numerical check completed | `self.wait(3.0)` + `self.ingestion_wait(2.5)` |
| S7-P21 | CodeStepper enters; equation/heatmap reposition | `self.wait(1.5)` + `self.ingestion_wait(2.5)` |
| S7-P22 | 11 code steps × cross-highlights | 11 × `self.wait(1.5)` = 16.5 s, then `self.ingestion_wait(2.5)` |
| S7-P23 | Output 0.000000 + hand-off caption | `self.wait(3.0)` + `self.ingestion_wait(2.5)` |
| S8-P24 | Boxed equation re-centered full-frame | `self.wait(2.0)` + `self.ingestion_wait(2.5)` |
| S8-P25 | `=`→`←` morph and revert | `self.wait(1.5)` + `self.ingestion_wait(2.5)` |
| S8-P26 | Takeaway final hold | `self.wait(8.0)` |

**Estimated duration tally (waits only — does not include morph run_times):**

```
Segment 1: 2.0 + 1.5 + 2.5                           =  6.0 s
Segment 2: 2.0+2.5 + 2.5 + 3.0+2.5                   = 12.5 s
Segment 3: 2.0+2.5 + 2.0+2.5 + 2.5 + 2.5+2.5         = 16.5 s
Segment 4: 2.0+2.5 + 2.0+2.5 + 2.0+2.5               = 13.5 s
Segment 5: 2.5+2.5 + 1.5 + 1.5+2.5 + 2.0+2.5
         + 2.0+2.5 + 2.5+2.5 + 3.0+2.5               = 30.0 s
Segment 6: 3.0 + 2.5                                  =  5.5 s
Segment 7: 1.5+2.5 + 16.5+2.5 + 3.0+2.5              = 28.5 s
Segment 8: 2.0+2.5 + 1.5+2.5 + 8.0                   = 16.5 s
                                                  -----------
                                            TOTAL  ≈ 129 s of WAITS
```

Add narration time + morph run_times + per-token Write durations. With
typical concept-video ratios (waits ≈ 12–15% of total runtime), the
expected total runtime is **~16–19 minutes**, landing inside the
12–22 min target window. Voice & BGM Agent narration timing is the final
governor.

---

## Opacity layer assignments

**OPACITY_PRIMARY (1.0):**
- Current step's equation token(s) being written or morphed
- Current step's active heatmap cell or spotlit grid cell
- Current step's active backup-diagram node or branch group
- Full-frame solo equations during their dedicated phases (S2-P3, S3-P6,
  S4-P10, S5-P19, S8-P24)
- During synced phases (S7-P22), the trio (equation token + code line +
  geometric region) all PRIMARY together

**OPACITY_SECONDARY (0.4):**
- Prior equation tokens (already-revealed parts of the derivation that are
  not the current focus)
- Heatmap cells outside the spotlight
- Backup-diagram parts not currently pulsing
- Captions providing context outside the immediate focus
- Earlier equations that remain on screen but are no longer the topic
  (e.g., $v_\pi$ definition LEFT in Segment 4, while $q_\pi$ is the topic)

**OPACITY_BACKGROUND (0.17):**
- The equiprobable policy thumbnail in the lower-right corner during
  Segment 5 (a quiet reminder that the algebra refers to π=equiprobable)
- Headers and grid frame chrome
- Subtitle text once the phase's main element has appeared

---

## Gymnasium code snippet

The full runnable Python that powers the CodeStepper in Segment 7,
preserving the platform-contract `code_focus_lines` verbatim (per spec §10):

```python
import gymnasium as gym
import numpy as np

env = gym.make("FrozenLake-v1", is_slippery=True)
n_states = env.observation_space.n        # 16
n_actions = env.action_space.n            # 4

# Equiprobable random policy: pi(a|s) = 1/4 for every state-action pair.
pi = np.ones((n_states, n_actions)) / n_actions
assert np.allclose(pi.sum(axis=1), 1.0)   # row sums = 1 (normalization)

# One step of the Bellman expectation equation at state 6, given a v_prev guess.
gamma = 0.99
v_prev = np.zeros(n_states)               # initial guess; in V-02 this is just the RHS evaluator
state = 6
v_new_6 = 0.0
for action in range(n_actions):
    for prob, next_state, reward, done in env.unwrapped.P[state][action]:
        v_new_6 += pi[state, action] * prob * (reward + gamma * v_prev[next_state])
print(f"RHS of Bellman at state 6 with v_prev=0: {v_new_6:.6f}")
```

**Expected output (Technical Validator-confirmed; if mismatch by > 1e-6,
escalate to RL Expert):**

```
RHS of Bellman at state 6 with v_prev=0: 0.000000
```

**Adopted platform-contract subset** (`code_focus_lines` tuple, verbatim
from spec §10):

```
env = gym.make('FrozenLake-v1', is_slippery=True)
pi = np.ones((n_states, n_actions)) / n_actions
assert np.allclose(pi.sum(axis=1), 1.0)
v_new_6 = 0.0
for action in range(n_actions):
    for prob, next_state, reward, done in env.unwrapped.P[6][action]:
        v_new_6 += pi[6, action] * prob * (reward + 0.99 * v_prev[next_state])
```

(Note: the platform-contract subset uses `'FrozenLake-v1'` single-quoted,
matching `specs.py` convention; the on-screen source uses double-quoted
`"FrozenLake-v1"` for Python style consistency. The Manim Expert should
display the source as runnable Python — double-quoted — and the platform
metadata is a textual subset compatibility, not a verbatim copy of the
displayed source character-for-character.)

---

## Code-visual sync points

Sync table for Segment 7's 11-step walkthrough (S7-P22). The
cross-highlight matrix above is the canonical mapping; this table
reformulates it for the Pacing Linter and the Voice & BGM Agent's timing
reference. One row per `CodeStepper.step(i)` call; one sync step per row.

| Step | Code line | Sync action | Equation token (boxed Bellman, LEFT) | Geometric region (heatmap CENTER) | Wait |
|---|---|---|---|---|---|
| 0 | `env = gym.make(...)` | grid frame `Indicate` | — | full heatmap | 1.5 s |
| 1 | `pi = np.ones((n_states, n_actions)) / n_actions` | policy arrows overlay flash | $\pi(a\|s)$ | one cell's 4 arrows | 1.5 s |
| 2 | `assert np.allclose(pi.sum(axis=1), 1.0)` | $\sum_a \pi = 1$ callout | $\sum_a \pi(a\|s)$ | one cell highlight | 1.5 s |
| 3 | `gamma = 0.99` | $\gamma$ token pulse | $\gamma$ | — | 1.5 s |
| 4 | `v_prev = np.zeros(n_states)` | heatmap dim/restore | $v_\pi(s')$ | full heatmap | 1.5 s |
| 5 | `state = 6` | state 6 spotlight | $s$ on LHS | cell 6 | 1.5 s |
| 6 | `v_new_6 = 0.0` | floating accumulator | $v_\pi(s)$ on LHS | cell 6 top-right marker | 1.5 s |
| 7 | `for action in range(n_actions):` | 4 action nodes pulse | $\sum_a$ | cell 6 with 4 action arrows | 1.5 s |
| 8 | `    for prob, next_state, reward, done in env.unwrapped.P[state][action]:` | 3 successor cells (for action RIGHT) pulse | $\sum_{s', r} p$ | cells 2, 7, 10 | 1.5 s |
| 9 | `        v_new_6 += pi[state, action] * prob * (reward + gamma * v_prev[next_state])` | 4-way synced pulse: $\pi$ token + $p$ token + $r$ token + $\gamma v_\pi(s')$ token, each `Indicate`s as its variable name appears in the code | $\pi(a\|s)$, $p(s', r\|s, a)$, $r$, $\gamma v_\pi(s')$ (4 tokens, sequential) | cells 2, 7, 10 (sequential per term) | 1.5 s |
| 10 | `print(...)` | "0.000000" output materializes; hand-off caption | $v_\pi(s)$ on LHS (final pulse) | cell 6 with "0.000000" annotation | 3.0 s |

---

## RL Expert collaboration notes

**Pre-brief (sent before this plan was written):**

> Proposed narrative hook (paraphrased): two policies on the same grid →
> heatmap of values → backup diagram → 5-step derivation → boxed Bellman
> equation → numerical LHS=RHS check at state 6 → CodeStepper showing
> `v_prev=0` produces 0.0 RHS → V-03 forward-tease via `=` → `←` morph.
>
> Key equation: $v_\pi(s) = \sum_a \pi(a\|s) \sum_{s', r} p(s', r \mid s, a)
> [r + \gamma v_\pi(s')]$ (S&B eq. 3.14, p. 59).
>
> Phase 3 (first equation appearance) caption text: "Policy: a probability
> distribution over actions per state."

**RL Expert response (binding constraints — verbatim from production
brief's `rl_expert_flags`):**

1. **Bellman derivation is non-negotiable** — five steps animated, no
   asserted final form. Plan incorporates per phases S5-P14 through S5-P19.
2. **Two sums separate** — outer over $a$ (policy randomness), inner over
   $(s', r)$ (environment randomness). Backup diagram (S5-P13) precedes
   the algebra. Plan never collapses to $\sum_{a, s', r}$.
3. **Equiprobable random policy is the working example** — adopted from
   S2-P5 onward as the canonical policy for the value heatmap, $q$-bars,
   backup diagram, derivation, and code. Plan never substitutes a
   deterministic policy mid-stream.
4. **Terminal states (5, 7, 11, 12, 15) all have $v_\pi=0$** on the
   heatmap. Phase S3-P9 is the explicit defusing of "but the goal should
   be valuable!" — the green `+1.0` reward marker and yellow `v=0` label
   co-display on the goal cell. Both colors required.
5. **CodeStepper expected output is 0.0** — deliberate V-03 hand-off.
   Phase S7-P23 carries the "one sweep is not enough" caption to bridge
   to V-03. Heatmap (converged) and code output (one iteration) explicitly
   contrasted in narration.
6. **Heatmap numbers are best-estimates** — every numeric label is marked
   `# NUMERIC_CLAIM` in the Manim source so the Technical Validator can
   refine them at $\theta=10^{-10}$ before render. Spec §11 candidate
   table is the source of best-estimates; live computation is
   authoritative.
7. **Reward color stays GREEN; value color stays YELLOW.** Goal cell in
   S3-P9 shows both simultaneously. Plan never collapses to a single
   color or swaps assignments.
8. **Closing forward-tease names V-03 but writes no V-03 equations.**
   Phase S8-P25 has a ≤ 1.5 s morph of `=` to `←` and $v_\pi$ to $v_{k+1},
   v_k$, then reverts. No pseudocode, no iteration counter, no
   convergence theorem.
9. **"Dynamics function" appears at most twice** — once implicitly in the
   V-01 recap (S1-P1), once in the Bellman derivation step 4 (S5-P17,
   when conditioning on $p$). Everywhere else "transition probability"
   or just "$p$".
10. **Optional $q_\pi$ Bellman equation (spec §3.5) is dropped.** Spec
    explicitly allows dropping for pacing tightening; the linking identity
    $v_\pi = \sum_a \pi q_\pi$ is preserved (S4-P12) but the Bellman form
    for $q_\pi$ is not derived. V-04 will introduce it. Per
    rl_expert_flag 10, never compress the $v_\pi$ derivation to make room
    for $q_\pi$.

**Status:** APPROVED (advisory) — UNREGISTERED_NEW_LESSON, no prior
submission gate required. Plan respects all 10 binding flags.

**Deviations from the canonical 7-phase reference template
(`transition_prob_concept.py`):**

This plan has 26 phases across 8 segments — substantially longer than the
7-phase reference. Justification:

- The lesson teaches **three tightly-coupled concepts** ($\pi$, $v_\pi$,
  Bellman) plus a fourth-supporting concept ($q_\pi$) plus a derivation
  plus a numerical check plus a code panel plus a V-03 forward-tease. The
  spec explicitly requires all of these (§3, §4, §6, §9, §12). A 7-phase
  structure cannot contain them at the required depth.
- The Bellman derivation alone (Segment 5, P13–P19) is 7 phases — it is a
  load-bearing 5-step algebraic sequence anchored on a backup diagram.
  Compressing it would violate rl_expert_flag 1.
- Each "full-frame solo equation reveal" phase (S2-P3, S3-P6, S4-P10,
  S5-P19, S8-P24) is mandatory per STYLE_BIBLE §33.2. Five solo reveals
  add five phases beyond the reference 7.

This expansion is consistent with V-01's plan structure (15 phases across
4 segments for `rl_mdp_core`, ~16:54 runtime). The estimated 16–19 min
runtime for this video lands inside the 12–22 min target window. The
Visual Director and Manim Expert will absorb the phase count via the 8
segment groupings (each segment is a coherent sub-arc with a clear
boundary).

---

## Self-verify output checklist (16 items, per skill SKILL.md §Output Checklist)

1. ✅ Phase 1 (S1-P1) shows only geometry (recap grid + caption stack) — no equation.
2. ✅ First equation appears at S2-P3 (Phase 3 of the segment-2 sub-arc; Phase 3+ of the overall arc as required).
3. ✅ All colors drawn from V-01-frozen palette only — STATE/VALUE/REWARD/POLICY/ACTION/PENALTY/CODE_ACCENT/BG_PANEL/BG_GRID — no new constants introduced.
4. ✅ Every pacing beat ≥ STYLE_BIBLE §6 minima; mandatory `ingestion_wait(2.5)` after every morph and scene-wide reposition.
5. ✅ Final hold S8-P26 = `self.wait(8.0)` — meets and exceeds the 2.5 s minimum.
6. ✅ Gymnasium code snippet is verbatim from spec §9.2 with adopted `code_focus_lines` preserved verbatim.
7. ✅ Every equation shown as MathTex component array (π definition, $v_\pi$ definition, $q_\pi$ definition, 5 derivation steps, boxed Bellman, linking identity).
8. ✅ Layout matrix has at most one panel per hemisphere per phase; migrations are explicit (see Migration Rules).
9. ✅ Code-visual sync table is one-to-one: 11 code lines ↔ 11 sync steps; no code line maps to multiple sync steps and no sync step references multiple distinct code lines.
10. ✅ RL Expert collaboration section filled; all 10 binding flags honored.
11. ✅ Every phase has a `narration_intention` field stating MEANING, not animation description.
12. ✅ `narration_intention` fields explain WHY each phase matters pedagogically, distinct from the visual description.
13. ✅ Screen Focus Budget table covers all 26 phases.
14. ✅ Screen Focus Budget names a single PRIMARY (or for legitimately side-by-side phases like S2-P4, a clearly-noted dual-PRIMARY).
15. ✅ Gymnasium asset paths cited in the Gymnasium Assets Required section, with verification command and per-sprite usage table.
16. ✅ Conversational Arc section names the rhetorical journey from opening tension to forward hook.

**All 16 items pass. Plan is ready for RL Expert final sign-off and
hand-off to the Visual Director (`choreo.md` author) and then to the
Technical Validator.**

---

## Hand-off summary

**To Visual Director:** Use this plan to author `choreo.md`. Owned by the
Visual Director: cognitive-load budget tables, element lifecycle matrix
(Phase IN / Phase OUT), motion choreography purpose tags, camera shot list,
sprite-math binding matrix, Scientific Rigor and Pedagogical Strategy
sections. The phase sequence above provides the input scaffold.

**To Technical Validator:** Confirm all 14 NUMERIC_CLAIM-tagged values
listed in spec §11 (state values for s ∈ {0, 6, 10, 13, 14}; terminal
zeros for s ∈ {5, 7, 11, 12, 15}; four $q_\pi(14, a)$ values;
$v_\text{new\_6}$ = 0.0 from `v_prev=0`; LHS-RHS consistency at state 6).
All values referenced in the heatmap (S3-P7) and the numerical check
(S6-P20) must match the Technical Validator's live re-computation at
$\theta=10^{-10}$. If any value differs by > 0.005 from the spec table,
update this plan's numeric labels before render.

**To Manim Expert:** All MathTex component arrays are decomposed in this
plan and reusable across phases. The `equation_morph` chain from `v_def`
(S3-P6) through `v_step1..v_step5_boxed` (S5-P14..S5-P19) and through
`v_step5_assignment_form` (S8-P25) shares component indices so
TransformMatchingTex animates correctly. All sprite paths via
`frozenlake_frame(soft_frame=True)`; no raw ImageMobject.
