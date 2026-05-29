# Plan: rl_mdp_core — Reinforcement Learning and the MDP Framework

**lesson_id:** rl_mdp_core  
**Manim class:** `RLMDPCoreConcept`  
**Scene file:** `manim_service/concept_videos/rl_mdp_core_concept.py`  
**Target duration:** content-determined; spec estimate ~21:00 (~1260 s)  
**RL Expert status:** APPROVED (advisory — new lesson, no prior submission gate required; spec §1 status field)

---

## Narrative hook

The elf stands at the top-left corner of a frozen lake. No labels. No
numbers. Just the grid and the goal glowing at the far corner. The elf
moves — and slips. It moves again — and falls into a hole, and the screen
goes dark. No voice tells it what went wrong. No label says "you should
have gone left." Only a zero. Then the elf tries again — and this time,
after five steps, it reaches the goal and a single number appears: one.
That number is the entire signal. *That* is reinforcement learning.

Only after the viewer feels the isolation of that sparse reward does
formalism arrive — first the grid's state indices, then the question of
what happens when the elf chooses RIGHT from state 6 (it doesn't always
go right), then the equation that names that uncertainty, and finally the
return that measures how much the agent values a reward five steps away.
Every formula is earned by a visual the viewer has already lived through.

---

## Color palette declaration

| Constant | Hex | Used for |
|---|---|---|
| `STATE_COLOR` | `#38BDF8` | State indices (0–15), `s`, `s'`, `S_t`, `S_{t+1}` tokens in equations, grid cell labels |
| `VALUE_COLOR` | `#FACC15` | Return `G_t`, `G_0`, numeric return values, `\gamma` token (discount modifies the return), `\gamma^k`, running accumulator label |
| `REWARD_COLOR` | `#34D399` | Reward `r`, `R_{t+1}`, goal cell (state 15), reward markers along path |
| `PENALTY_COLOR` | `#F87171` | Hole cells (states 5, 7, 11, 12), `done=True` outcome branch, failure flash |
| `POLICY_COLOR` | `#A78BFA` | Probability bars in `ActionBarChart`, `prob` variable in code panel, "1/3" fraction labels |
| `ACTION_COLOR` | `#FB923C` | Action arrow (RIGHT at state 6), action index `a`, action label in code panel |
| `BG_COLOR` | `#020617` | Scene background |
| `BG_PANEL` | `#0F172A` | Panel fills |
| `CODE_ACCENT` | `#64748B` | Code panel header, axis tick labels |

---

## Reserved-hemisphere layout matrix (MANDATORY — STYLE_BIBLE §16)

| Phase | LEFT (≈ −5.0 to −1.5 x) | CENTER (≈ −1.5 to +1.5 x) | RIGHT (≈ +1.5 to +5.0 x) |
|---|---|---|---|
| S1-P1 | — | FrozenLake grid (full frame, no labels) | — |
| S1-P2 | — | FrozenLake grid (full frame, agent traversal) | — |
| S1-P3 | — | FrozenLake grid (full frame, success path) | — |
| S2-P4 | — | FrozenLake grid (full frame, state indices revealed) | — |
| S2-P5 | — | FrozenLake grid (full frame, Markov demo at state 6) | — |
| S3a-P6 | — | FrozenLake grid clears → `p(s',r|s,a)` equation FULL SCREEN solo reveal | — |
| S3a-P7 | Equation panel (equation repositions LEFT) | FrozenLake grid (smaller, centered; 3-branch fork overlay) | — |
| S3b-P8 | Equation panel (LEFT, stable) | FrozenLake grid (smaller, centered; outcome branches) | `ActionBarChart` (RIGHT, 3 bars) |
| S3b-P9 | Equation panel (LEFT, stable) | FrozenLake grid (smaller; `done` flags visible) | `CodeStepper` replaces `ActionBarChart` on RIGHT (chart migrates to inset position within RIGHT) |
| S3b-P10 | Normalization form (equation panel updates, LEFT) | FrozenLake grid (stable, smaller) | `CodeStepper` (RIGHT, stable) |
| S4-P11 | — | FrozenLake grid clears → `G_t` equation FULL SCREEN solo reveal | — |
| S4-P12 | Equation panel `G_t` sum form (LEFT) | FrozenLake path animation (CENTER) | Numeric accumulator (RIGHT small panel) |
| S4-P13 | Equation panel `G_t` (LEFT, stable) | FrozenLake path (CENTER, stable) | Gamma sweep `ActionBarChart` (RIGHT replaces accumulator) |
| S4-P14 | Return recursion equation (LEFT, morph) | FrozenLake grid (CENTER, dimmed) | Gamma sweep chart (RIGHT, dims) |
| S4-P15 | All panels stable | All panels stable | Forward-tease caption only |

**Migration rules (explicit):**
- Before S3a-P7: grid shrinks via `smooth_move_to` and equation enters CENTER solo, then grid moves CENTER (smaller) and equation shifts LEFT simultaneously.
- Before S3b-P9: `ActionBarChart` scales down and migrates to inset position at RIGHT-lower so `CodeStepper` can enter at RIGHT-upper. No occlusion.
- Before S4-P11: ALL elements from S3b (equation panel, grid, code, chart) `FadeOut` so the `G_t` equation gets a clean full-screen entry.
- Before S4-P12: `G_t` equation repositions LEFT; FrozenLake grid re-enters CENTER (smaller); accumulator panel enters RIGHT.

---

## Cross-highlight matrix (MANDATORY — STYLE_BIBLE §15.2)

This matrix governs Segment 3b (transition probability), the only `CodeStepper` phase.

| Code line index | Code line content (verbatim from teaching spec §9.2) | Geometric target |
|---|---|---|
| 0 | `env = gym.make("FrozenLake-v1", is_slippery=True)` | Full FrozenLake grid reveal (already on canvas) — `Indicate` on the entire grid frame |
| 1 | `for prob, next_state, reward, done in env.unwrapped.P[6][2]:` | State 6 cell highlights (`STATE_COLOR` pulse); action RIGHT arrow pulses (`ACTION_COLOR`) |
| 2 | `    print(f"prob={prob:.3f}  next_state={next_state}  reward={reward}  done={done}")` | Three sub-steps executed sequentially: (a) state 10 cell highlights + bar 1/3 appears; (b) state 7 cell highlights `PENALTY_COLOR` (hole) + bar 1/3 appears; (c) state 2 cell highlights + bar 1/3 appears; Σ=1 annotation appears |

**Note (rl_expert FLAG-3):** `ActionBarChart` bars are sorted by next-state index
left-to-right: state 2 (leftmost) → state 7 (center) → state 10 (rightmost).
This differs from Gymnasium's internal tuple order (10, 7, 2). The cross-highlight
must map bar position 0 → state 2, bar position 1 → state 7, bar position 2 → state 10.
The Manim Expert must reconcile bar insertion order with the `cross_highlight_pair`
target at each code step.

---

## Conversational Arc

- **Opening tension:** The elf has one goal and no map. The only feedback it ever
  receives is a number. What can it possibly learn from that?
- **First reveal (S1-P1/P2/P3):** The viewer *feels* the absence of guidance before
  seeing any formula — two failed paths and one success, with nothing but zeroes
  and a single one.
- **Rising question (S2-P4/P5):** Once formalism arrives, the question becomes: how
  does the environment decide where the elf lands? The ice is slippery — the elf
  "chose" RIGHT but ended up somewhere else. How do we describe that mathematically?
- **Key insight — Segment 3 (S3a-P6):** The equation `p(s',r|s,a)` is the complete
  answer: the environment's response law. Everything the agent can ever learn about
  the world is encoded in this function.
- **Key insight — Segment 4 (S4-P11):** The return `G_t` is not just the next reward
  — it is a weighted sum of every future reward, and `γ` is the agent's patience.
  The single `1.0` at the goal, five steps away, still reaches the agent — discounted
  by distance.
- **Code connection:** `env.unwrapped.P[6][2]` makes the abstract `p(s',r|s,a)` into
  a Python list you can iterate over. The code panel collapses the distance between
  symbol and executable line.
- **Resolution:** The agent acts in a Markov Decision Process. The MDP is specified
  by `p(s',r|s,a)` and the return is `G_t`. Those two objects are all that the rest
  of the series will ever need.
- **Forward hook:** "We've seen what the MDP looks like. The next question is: how
  does the agent decide which action to take? That is the role of the *policy* —
  and what each state is worth under one — which is where the next video begins."

---

## Screen Focus Budget

| Phase | Primary (OPACITY_PRIMARY) | Secondary (OPACITY_SECONDARY) | Background |
|---|---|---|---|
| S1-P1 | FrozenLake grid (full frame) | Header only | None |
| S1-P2a | Agent sprite + current cell | Surrounding grid cells | None |
| S1-P2b | Failure flash (hole cell, `PENALTY_COLOR`) | Agent path so far | Grid tiles |
| S1-P3 | Agent + highlighted path cells | Reward annotation (state 15) | Grid |
| S2-P4 | State index labels (0–15 revealing) | Grid tile backgrounds | None |
| S2-P5 | State 6 cell + action arrow | State index labels, surrounding cells | Grid |
| S3a-P6 | `p(s',r|s,a)` equation, full frame centered, font 48 | Nothing (all else FadeOut) | None |
| S3a-P7a | Equation (LEFT, repositioned) | Grid (CENTER smaller) | None |
| S3a-P7b | Three outcome branches (CENTER) + equation token trace vectors | Grid cells (non-focal) | None |
| S3b-P8 | `ActionBarChart` (RIGHT) + active outcome branch (CENTER) | Equation (LEFT), other grid cells | None |
| S3b-P9a | Code line 0 + grid frame | Other code lines, equation | Grid |
| S3b-P9b | Code line 1 + state 6 cell + action arrow | Other code lines, other cells | Grid |
| S3b-P9c | Code line 2 + each outcome cell + bar (per sub-step) | All other elements | Grid |
| S3b-P10 | Normalization sum equation token | Σ=1 bar annotation, other equation tokens | Code, grid |
| S4-P11 | `G_t` equation, full frame centered, font 48 | Nothing (all else FadeOut) | None |
| S4-P12 | Active path cell + reward annotation + accumulator value | `G_t` equation (LEFT), path trail | Grid |
| S4-P13 | Gamma bar chart (RIGHT) + `γ` token in equation | `G_t` equation (LEFT), path (CENTER) | None |
| S4-P14 | Return recursion `G_t = R_{t+1} + γG_{t+1}` (CENTER large) | Prior sum form (LEFT, dims) | None |
| S4-P15 | All panels stable, no highlights | None | None |

---

## Gymnasium Assets Required

**Environment:** FrozenLake-v1 (`is_slippery=True`)

**Asset verification command:**
```python
import gymnasium, os
asset_dir = os.path.join(os.path.dirname(gymnasium.__file__),
                         'envs', 'toy_text', 'img')
required = [
    'ice.png',        # safe tiles: 1,2,3,4,6,8,9,10,13,14
    'stool.png',      # start tile: state 0
    'hole.png',       # hole tiles: 5,7,11,12
    'goal.png',       # goal tile: 15
    'elf_up.png',     # agent sprite facing up
    'elf_down.png',   # agent sprite facing down
    'elf_left.png',   # agent sprite facing left
    'elf_right.png',  # agent sprite facing right
]
missing = [f for f in required if not os.path.exists(os.path.join(asset_dir, f))]
assert not missing, f"MISSING_ASSETS: {missing}"
print("ASSET_DIR:", asset_dir)
# Verify at: [fill in from print output before rendering]
```

**Sprites used:**
- `stool.png` — state 0 (start)
- `ice.png` — states 1, 2, 3, 4, 6, 8, 9, 10, 13, 14
- `hole.png` — states 5, 7, 11, 12
- `goal.png` — state 15
- `elf_right.png` — primary agent sprite (Segments 1, 2, 3)
- `elf_down.png`, `elf_left.png`, `elf_up.png` — direction-aware in Segment 1 traversal

**Frame captures used:** YES — one static `rgb_array` render for the full grid reveal
in Segment 1 Phase 1 (before state indices appear). Per-tile composition via
`frozenlake_frame()` for all subsequent interactive phases.

**All assets must be confirmed present before the Manim Expert writes any scene code.**
If any asset is missing: report `MISSING_ASSETS` to Producer and STOP.

---

## Phase sequence

The four segments map onto 15 plan-phases. Each segment is a self-contained
teaching arc; together they form ONE continuous video with smooth pacing
transitions. Segment boundaries use a brief caption cross-fade and a 1.5 s
pause to signal the transition without a hard cut.

---

### Segment 1 — What is Reinforcement Learning?

**Segment narration intention:** Build the intuition that trial-and-error under a
sparse reward signal is both natural and genuinely hard. The absence of a teacher is
the defining feature of the RL problem — not a limitation of the example.

---

#### Phase S1-P1 — Grid entry (geometry: environment reveal, no labels)

**Animation events:**
- `show_header("Reinforcement Learning and the MDP Framework", subtitle="FrozenLake — the agent learns from scratch")`
- `mark_phase("seg1_grid_entry")`
- Full-frame FrozenLake grid (native Gymnasium `rgb_array` frame, wrapped in soft container) fades in centered. No state indices visible yet.
- Caption: "An agent. A goal. A frozen lake."

**Narration intention:** The viewer's first impression is the visual world the
agent inhabits — ice, holes, a goal — before any formalism is named. The sparseness
of the scene mirrors the sparseness of the agent's information.

**Screen primary:** FrozenLake grid (full CENTER, no competing elements)

**Helpers:**
- `show_header(title, subtitle)` — human-readable, no lesson_ids
- Native `rgb_array` render via Gymnasium embedded as `ImageMobject`, wrapped in soft container (`frozenlake_frame(soft_frame=True)`)
- `place_caption(text)`

**Wait:** `self.wait(2.0)` (geometry entry minimum) + `self.ingestion_wait(2.5)` after `FadeIn`

**Estimated time:** ~8 s

---

#### Phase S1-P2a — Failed attempt 1 (intuition: sparse reward, no guidance)

**Animation events:**
- `mark_phase("seg1_fail1")`
- Agent (`elf_right.png`) appears at state 0 via `FadeIn`. Caption updates.
- `EpisodeTrail.step_to(1)` → `EpisodeTrail.step_to(5)` — agent moves 0→1→5. State 5 is a hole; `PENALTY_COLOR` flash on cell 5. `elf_down.png` sprite shown at final position.
- Brief "dark flash" (grid dims to `OPACITY_SECONDARY` for 0.5 s then back) — episode ends.
- Caption: "No map. No hint. Just a zero."

**Narration intention:** The zero reward is not just a number — it is the *only*
feedback the agent receives. The viewer must feel the weight of that absence.
There is no indication of what the agent should have done differently.

**Screen primary:** Agent sprite + state 5 hole cell (at moment of fall)

**Helpers:**
- `EpisodeTrail` — grid + agent rectangle with `.step_to()`, `.clear_trail()`
- `place_caption(text)` — FadeOut old → FadeIn new

**Wait:** `self.wait(2.0)` after failure flash

**Estimated time:** ~10 s

---

#### Phase S1-P2b — Failed attempt 2 (slippage: 0→4→8→9→5)

**Animation events:**
- `mark_phase("seg1_fail2")`
- `EpisodeTrail.clear_trail()`; agent resets to state 0.
- `EpisodeTrail.step_to()` chain: 0→4→8→9→5 (slippage). State 5 PENALTY_COLOR flash again.
- Caption: "It tried again. Same result. The ice moved it sideways."

**Narration intention:** The second failure introduces the word "sideways" — without
yet naming the Markov property or transition probability. The viewer intuits that
the environment has its own randomness before the formalism arrives to explain it.

**Screen primary:** Agent path trail + state 5 cell (at moment of hole)

**Helpers:** `EpisodeTrail`, `place_caption`

**Wait:** `self.wait(1.5)`

**Estimated time:** ~8 s

---

#### Phase S1-P3 — Successful path (0→4→8→9→10→14→15, reward 1.0)

**Animation events:**
- `mark_phase("seg1_success")`
- `EpisodeTrail.clear_trail()`; agent resets to state 0.
- `EpisodeTrail.step_to()` chain: 0→4→8→9→10→14→15. At state 15, goal cell pulses `REWARD_COLOR`. Reward `1.0` appears as a brief floating label at state 15 in `VALUE_COLOR` — the ONLY number shown in this segment.
- Caption: "One number. That is all the agent ever receives."

**Narration intention:** The single reward `1.0` at the goal is the complete
signal from the environment. No partial credit. No explanation. The reward
hypothesis — that all goals can be framed as maximizing expected cumulative reward —
is planted here as an intuition before it is stated as a theorem.

**Screen primary:** State 15 goal cell + reward label `1.0`

**Helpers:** `EpisodeTrail`, `place_caption`, `Indicate` on goal cell

**Wait:** `self.wait(2.5)` (extended hold — this is the emotional peak of Segment 1)

**Estimated time:** ~12 s

---

**Segment 1 subtotal:** ~40 s (matches spec pacing §10 ~4:30 budget via narration expansion)

---

### Segment 2 — The MDP Framework

**Segment narration intention:** Build the intuition that the Markov property is a
*gift* — the environment's full response depends only on the current state, not on
the entire history. This makes the problem tractable. The formalism is a precise
statement of something the ice was doing all along.

---

#### Phase S2-P4 — State indices revealed (MDP structure: states)

**Animation events:**
- `mark_phase("seg2_state_indices")`
- Smooth transition from `EpisodeTrail` to per-tile `frozenlake_frame()` composition.
- State index labels 0–15 appear via `LaggedStart` over each tile, color `STATE_COLOR`, `font_size=20`.
- Caption: "Each cell is a *state*. The agent always knows which one it occupies."

**Narration intention:** The state index labels give the viewer a coordinate system
for the world. More importantly, the state is the *complete* description of where
the agent is — nothing else matters for what happens next. That completeness is the
Markov property.

**Screen primary:** State index labels (0–15) appearing via `LaggedStart`

**Helpers:**
- `frozenlake_frame()` per-tile composition
- `LaggedStart([Write(label) for label in state_labels], lag_ratio=0.07)`
- `place_caption`

**trace_vector pairs:** None in this phase (state indices are geometric labels,
not equation tokens being introduced for the first time).

**Wait:** `self.wait(2.0)` after all labels appear

**Estimated time:** ~10 s

---

#### Phase S2-P5 — Markov property demonstration (state 6, action RIGHT)

**Animation events:**
- `mark_phase("seg2_markov")`
- Agent (`elf_right.png`) placed at state 6 cell.
- A dashed curved arrow fades in pointing INTO state 6 from various directions (labeled "...history"), then `FadeOut` — the history is irrelevant.
- A solid `ACTION_COLOR` arrow points RIGHT from state 6, labeled `a = RIGHT`.
- Caption first: "The ice does not remember. Whatever path brought the agent here is gone."
- Caption second (after history arrow fades): "Only state 6 and the action RIGHT determine what comes next."

**Narration intention:** The Markov property eliminates history from the decision
problem. This is a mathematical simplification with a real cost — real-world
situations often ARE history-dependent — but for this framework it is the enabling
assumption. The viewer should feel this as liberating, not as a hidden limitation.

**Screen primary:** State 6 cell + ACTION_COLOR arrow (moment of Markov reveal)

**Helpers:**
- `frozenlake_frame()` per-tile composition (grid from S2-P4 stays; agent added)
- `Create(dashed_curved_arrow)` for history arrow → `FadeOut`
- `Create(action_arrow)` for `a = RIGHT` arrow
- `place_caption`

**SpriteActionBinding:** Agent sprite at state 6 + action arrow — the agent's
position IS the complete state. The binding should be flagged for Visual Director's
Sprite-Math Binding Matrix in `choreo.md`.

**Wait:** `self.wait(2.0)` after Markov reveal caption

**Estimated time:** ~12 s

---

**Segment 2 subtotal:** ~22 s (matches spec pacing §10 ~3:00 budget via narration expansion)

---

### Segment 3a — The Dynamics Function p(s',r|s,a)

**Segment narration intention (3a):** Build the intuition that `p(s',r|s,a)` is the
environment's complete answer to "what happens if the agent takes action `a` in
state `s`?" The equation is the agent's only model of the world, and the agent has
no control over it.

---

#### Phase S3a-P6 — Full-screen solo reveal of p(s',r|s,a) (STYLE_BIBLE §33.2)

**Animation events:**
- `mark_phase("seg3a_p_equation_solo")`
- ALL canvas elements fade to `OPACITY_SECONDARY` or `FadeOut`. Only header remains.
- `p_eq` equation appears centered, `font_size=48`:
  ```
  p(s', r | s, a) ≐ Pr{S_{t+1}=s', R_{t+1}=r | S_t=s, A_t=a}
  ```
- `LaggedStart` token-by-token `Write` animation.
- Hold equation alone.
- Caption: "The environment's response law. Given where you are and what you do — here is where you land and what you receive."

**Narration intention:** The equation is the formal name for the thing the ice was
doing in Segment 1. The four arguments are the inputs; the probability is the output.
The agent does not choose `p` — the environment does. That separation between what
the agent controls (the action) and what the environment controls (the response) is
the core of the MDP framework.

**Screen primary:** `p(s',r|s,a)` equation (FULL FRAME, nothing else at PRIMARY)

**Helpers:**
- `FadeOut` all prior mobjects before equation appears
- `MathTex` component array (see decomposition below) centered, `font_size=48`
- `LaggedStart([Write(token) for token in p_eq_tokens], lag_ratio=0.12)`
- `place_caption`

**MathTex decomposition (p equation, full form — will morph in S3a-P7):**
```python
p_eq_full = MathTex(
    "p", "(", "s'", ",", "r",
    "\\mid", "s", ",", "a", ")",
    "\\doteq",
    "\\Pr", "\\bigl\\{",
    "S_{t+1}", "=", "s'", ",",
    "R_{t+1}", "=", "r",
    "\\mid",
    "S_t", "=", "s", ",",
    "A_t", "=", "a",
    "\\bigr\\}",
    font_size=48,
)
# Color bindings:
# p_eq_full[2].set_color(STATE_COLOR)    # s'
# p_eq_full[4].set_color(REWARD_COLOR)   # r
# p_eq_full[6].set_color(STATE_COLOR)    # s
# p_eq_full[8].set_color(ACTION_COLOR)   # a
# p_eq_full[15].set_color(STATE_COLOR)   # s' (expanded)
# p_eq_full[18].set_color(REWARD_COLOR)  # r  (expanded)
# p_eq_full[21].set_color(STATE_COLOR)   # s  (expanded)
# p_eq_full[24].set_color(ACTION_COLOR)  # a  (expanded)
```

**trace_vector pairs:**
- Source: state 6 cell (now OFF screen — narrative reference) → token `s'` (write direction); defer actual trace to S3a-P7 when grid is visible alongside equation.

**Wait:** `self.wait(2.0)` (equation reveal minimum) + `self.ingestion_wait(2.5)`

**Estimated time:** ~12 s

---

#### Phase S3a-P7 — Three outcome branches: p visualized geometrically

**Animation events:**
- `mark_phase("seg3a_branches")`
- Equation (`p_eq_full`) repositions LEFT via `smooth_move_to`, shrinks to `font_size=36` via `equation_panel()` wrapper. FrozenLake grid (smaller, per-tile) re-enters CENTER. Both happen in ONE simultaneous `self.play(...)`.
- `self.ingestion_wait(2.5)` after reposition.
- THREE outcome branches animate from state 6 CENTER:
  - Branch 1: arrow pointing UP → state 2 (ice, `STATE_COLOR`) — label "1/3, r=0, done=False"
  - Branch 2: arrow pointing RIGHT → state 7 (hole, `PENALTY_COLOR`) — label "1/3, r=0, done=True"
  - Branch 3: arrow pointing DOWN → state 10 (ice, `STATE_COLOR`) — label "1/3, r=0, done=False"
- Each branch `Create`-animated with `lag_ratio=0.3` via `LaggedStart`.
- `trace_vector` from state 2 cell → `s'` token in equation. `trace_vector` from state 7 cell → `s'` token. `trace_vector` from state 10 cell → `s'` token (sequentially, not all at once).
- Caption: "Three equally likely outcomes. One action, three destinations."

**Narration intention:** The three branches make visceral what the equation
formalizes: choosing an action does not determine the outcome. The probability
distribution over next states IS the environment's response — and it may be
completely spread across multiple successors. The viewer now has an image they will
carry into every subsequent algorithm.

**Screen primary:** Three outcome branches (CENTER) — `trace_vector` pairs bind them to the equation

**Helpers:**
- `smooth_move_to` for equation reposition
- `frozenlake_frame()` per-tile composition (re-enter CENTER)
- `LaggedStart([Create(branch) for branch in branches], lag_ratio=0.3)`
- `trace_vector(scene, state_cell, eq_token)` for each of the three s' references
- `place_caption`

**Wait:** `self.wait(2.0)` after all three branches and traces complete + `self.ingestion_wait(2.5)`

**Estimated time:** ~18 s

---

**Segment 3a subtotal:** ~30 s (normalization and summation collapse continue in S3b)

---

### Segment 3b — Transition Probability Deep Dive

**Segment narration intention (3b):** Close the loop between the equation and
the code. `env.unwrapped.P[6][2]` is not an abstraction — it IS `p(s',r|s,a)`
for state 6, action RIGHT, stored as a Python list. The `ActionBarChart` makes
the distribution visible and the `CodeStepper` makes it executable.

---

#### Phase S3b-P8 — ActionBarChart: three bars at 1/3 each

**Animation events:**
- `mark_phase("seg3b_barchart")`
- `ActionBarChart` enters RIGHT with bars sorted by next-state index: bar 0 = state 2, bar 1 = state 7, bar 2 = state 10. All bars at height 1/3 (0.333). Labels: "s'=2", "s'=7", "s'=10" in `STATE_COLOR`. Bar fills in `POLICY_COLOR`.
- Σ=1 annotation appears above bars (in `REWARD_COLOR`).
- Each bar appears with `LaggedStart` + `ValueTracker`-driven height animation from 0 → 1/3.
- The state 7 bar label changes to `PENALTY_COLOR` (it is a hole) with a brief `Indicate`.
- Caption: "Each bar is how likely the agent actually ends up in that cell. Intention and outcome are two different things."

**Narration intention:** The chart makes concrete the probability distribution.
The viewer sees all three outcomes simultaneously and can compare their heights —
they are equal, which is the surprising fact about slippery ice. The `PENALTY_COLOR`
on state 7 links back to the hole-fall in Segment 1.

**Screen primary:** `ActionBarChart` (RIGHT) — bars growing via `ValueTracker`

**Helpers:**
- `ActionBarChart(labels=["s'=2","s'=7","s'=10"], values=[0.333,0.333,0.333])` — bars sorted by state index (FLAG-3 compliance)
- `reactive_bar` / `ValueTracker` for bar heights
- `place_mid_right_panel(chart.panel)`
- `Indicate` on state 7 bar label
- `place_caption`

**Wait:** `self.wait(1.5)` after full chart reveal + Σ=1 appears + `self.ingestion_wait(2.5)`

**Estimated time:** ~15 s

---

#### Phase S3b-P9 — CodeStepper: env.unwrapped.P[6][2]

**Animation events:**
- `mark_phase("seg3b_codestepper")`
- Migration: `ActionBarChart` scales down and shifts to lower-RIGHT inset via `smooth_move_to` (chart remains visible but smaller). `CodeStepper` panel enters RIGHT-upper via `FadeIn`.
- `self.ingestion_wait(2.5)` after migration.
- Caption: "The same distribution — readable in a single Python call."

**Code lines (verbatim from teaching spec §9.2 and `specs.py.code_focus_lines`):**
```python
env = gym.make("FrozenLake-v1", is_slippery=True)
for prob, next_state, reward, done in env.unwrapped.P[6][2]:
    print(f"prob={prob:.3f}  next_state={next_state}  reward={reward}  done={done}")
```

**CodeStepper step sequence (per cross-highlight matrix):**

- `CodeStepper.step(0)`: line `env = gym.make(...)` highlights + `cross_highlight_pair(scene, code.lines[0], grid_frame)` — full grid `Indicate`
- `CodeStepper.step(1)`: line `for prob, next_state, ...` highlights + `cross_highlight_pair(scene, code.lines[1], state6_cell)` — state 6 cell highlights `STATE_COLOR`, action RIGHT arrow pulses `ACTION_COLOR`
- `CodeStepper.step(2)` sub-step (a): first iteration (next_state=10) — `cross_highlight_pair(scene, code.lines[2], state10_cell)` — state 10 highlights; bar for state 10 (rightmost) at 1/3 grows
- `CodeStepper.step(2)` sub-step (b): second iteration (next_state=7) — `cross_highlight_pair(scene, code.lines[2], state7_cell)` — state 7 highlights `PENALTY_COLOR`; bar for state 7 at 1/3 grows
- `CodeStepper.step(2)` sub-step (c): third iteration (next_state=2) — `cross_highlight_pair(scene, code.lines[2], state2_cell)` — state 2 highlights; bar for state 2 (leftmost) at 1/3 grows; Σ=1 annotation on chart pulses

**Narration intention:** The code is not illustrative — it IS the mathematical
object. `env.unwrapped.P[6][2]` returns exactly the list of `(prob, next_state,
reward, done)` tuples that the equation `p(s',r|s,a)` describes. The variable name
`prob` holds a sample of the probability distribution; `next_state` holds `s'`;
`reward` holds `r`; `done` holds the terminal flag. The code and the equation are
two notations for the same thing.

**Screen primary (per step):**
- Step 0: Full grid frame
- Step 1: State 6 cell + action arrow
- Step 2a: State 10 cell + bar 2
- Step 2b: State 7 cell + bar 1 (PENALTY_COLOR)
- Step 2c: State 2 cell + bar 0 + Σ=1

**Helpers:**
- `CodeStepper(lines=code_lines, title="Gymnasium", width=5.1, font_size=20)`
- `smooth_move_to` for chart migration
- `cross_highlight_pair(scene, code_line, target_geom)` at each step
- `Indicate` for per-step cell highlights
- `place_mid_right_panel` + chart inset positioning

**Per-step wait:** `self.wait(1.5)` after each `CodeStepper.step()` call

**Estimated time:** ~35 s

---

#### Phase S3b-P10 — Normalization and summation collapse

**Animation events:**
- `mark_phase("seg3b_normalization")`
- `CodeStepper` fades out. Chart remains (inset).
- Normalization equation appears BELOW the `p` equation in the equation panel (or as a new centered equation after a panel clear):
  ```
  Σ_{s'} Σ_r p(s',r|s,a) = 1  ∀s∈S, a∈A(s)
  ```
- Then summation collapse appears (derive `p(s'|s,a)` from `p(s',r|s,a)`):
  ```
  p(s'|s,a) = Σ_r p(s',r|s,a)
  ```
  via `equation_morph` / `TransformMatchingTex`.
- Caption: "The four-argument form is the complete description. Marginalizing over rewards gives you the state-transition probability."

**Narration intention (M-5 defeat):** `p(s'|s,a)` and `p(s',r|s,a)` are
related but not identical. The four-argument form is the canonical MDP
object. The state-transition probability is a derived quantity — you get
it by summing over all possible rewards. For FrozenLake (where each
`(s,a,s')` has a unique reward), they carry the same information, but
the four-argument form is the one that generalizes.

**Screen primary:** Normalization equation (CENTER) during intro; then summation collapse equation during morph

**MathTex decompositions:**

```python
# Normalization form
norm_eq = MathTex(
    "\\sum_{s'}", "\\sum_r",
    "p", "(", "s'", ",", "r",
    "\\mid", "s", ",", "a", ")",
    "=", "1",
    font_size=36,
)
# norm_eq[4].set_color(STATE_COLOR)   # s'
# norm_eq[6].set_color(REWARD_COLOR)  # r
# norm_eq[8].set_color(STATE_COLOR)   # s
# norm_eq[10].set_color(ACTION_COLOR) # a

# Marginal (state-transition) form
marginal_eq = MathTex(
    "p", "(", "s'", "\\mid", "s", ",", "a", ")",
    "=", "\\sum_r",
    "p", "(", "s'", ",", "r",
    "\\mid", "s", ",", "a", ")",
    font_size=36,
)
# marginal_eq[2].set_color(STATE_COLOR)    # s' (LHS)
# marginal_eq[4].set_color(STATE_COLOR)    # s  (LHS)
# marginal_eq[6].set_color(ACTION_COLOR)   # a  (LHS)
# marginal_eq[12].set_color(STATE_COLOR)   # s' (RHS)
# marginal_eq[14].set_color(REWARD_COLOR)  # r  (RHS)
# marginal_eq[16].set_color(STATE_COLOR)   # s  (RHS)
# marginal_eq[18].set_color(ACTION_COLOR)  # a  (RHS)
```

**Helpers:**
- `equation_morph(scene, norm_eq, marginal_eq)` (or `TransformMatchingTex`)
- `self.ingestion_wait(2.5)` after morph

**Wait:** `self.wait(2.0)` after normalization + `self.ingestion_wait(2.5)` after morph

**Estimated time:** ~18 s

---

**Segment 3 subtotal:** ~61 s (matches spec pacing §10 ~6:30 budget via narration expansion)

---

### Segment 4 — Rewards and Returns

**Segment narration intention (4):** Build the intuition that the agent is not
optimizing for the next reward — it is optimizing for a weighted sum of ALL future
rewards. The discount factor `γ` is the agent's patience. A reward five steps away
is still real; `γ` determines how much it counts.

**NOTE (rl_expert FLAG-1):** The recursive form `G_t = R_{t+1} + γG_{t+1}` is
called "the return recursion" throughout. It is NOT called "the Bellman equation"
anywhere in this video. The Bellman equation is introduced in V-02.

---

#### Phase S4-P11 — Full-screen solo reveal of G_t (STYLE_BIBLE §33.2)

**Animation events:**
- `mark_phase("seg4_Gt_equation_solo")`
- ALL canvas elements from Segment 3 `FadeOut` (equation panel, grid, chart inset). Only header remains.
- `G_t` equation appears centered, `font_size=48`:
  ```
  G_t = R_{t+1} + γR_{t+2} + γ²R_{t+3} + ⋯ = Σ_{k=0}^{∞} γ^k R_{t+k+1}
  ```
- `LaggedStart` token-by-token `Write` animation, left-to-right.
- Caption: "The agent's goal is not the next reward. It is the sum of all future rewards — weighted by distance."

**Narration intention:** The return equation is the formal statement of the
reward hypothesis: maximize expected cumulative reward. The `γ^k` weighting
means rewards closer in time count more, but no future reward is completely
ignored. This is a radically different objective than "maximize the next reward."

**Screen primary:** `G_t` equation (FULL FRAME, nothing else at PRIMARY)

**MathTex decomposition (G_t sum form — will morph to recursive form in S4-P14):**
```python
Gt_sum = MathTex(
    "G_t", "=",
    "R_{t+1}", "+",
    "\\gamma", "R_{t+2}", "+",
    "\\gamma^2", "R_{t+3}", "+",
    "\\cdots",
    "=",
    "\\sum_{k=0}^{\\infty}", "\\gamma^k", "R_{t+k+1}",
    font_size=48,
)
# Gt_sum[0].set_color(VALUE_COLOR)   # G_t
# Gt_sum[2].set_color(REWARD_COLOR)  # R_{t+1}
# Gt_sum[4].set_color(VALUE_COLOR)   # γ
# Gt_sum[5].set_color(REWARD_COLOR)  # R_{t+2}
# Gt_sum[7].set_color(VALUE_COLOR)   # γ²
# Gt_sum[8].set_color(REWARD_COLOR)  # R_{t+3}
# Gt_sum[13].set_color(VALUE_COLOR)  # γ^k
# Gt_sum[14].set_color(REWARD_COLOR) # R_{t+k+1}
```

**Wait:** `self.wait(2.0)` (equation solo reveal minimum) + `self.ingestion_wait(2.5)`

**Estimated time:** ~12 s

---

#### Phase S4-P12 — Term-by-term return computation (path 0→4→8→9→10→14→15)

**Animation events:**
- `mark_phase("seg4_return_computation")`
- `Gt_sum` equation repositions LEFT via `smooth_move_to`, shrinks to `font_size=36` in panel. FrozenLake grid (per-tile, smaller) re-enters CENTER. Accumulator panel enters RIGHT.
- `self.ingestion_wait(2.5)` after reposition.
- Path highlighted cell by cell: 0→4→8→9→10→14→15. Each cell lights up in sequence.
- For each step, a floating reward label appears at the cell: "R=0" in gray for steps 1–5, then "R=1.0" in `REWARD_COLOR` at state 15.
- Accumulator label on RIGHT panel starts at "G₀ = 0" and updates:
  - Step 1: G₀ = 0 + 0.99⁰ × 0 = 0
  - Step 2: G₀ = 0 + 0.99¹ × 0 = 0
  - Step 3: G₀ = 0 + 0.99² × 0 = 0
  - Step 4: G₀ = 0 + 0.99³ × 0 = 0
  - Step 5: G₀ = 0 + 0.99⁴ × 0 = 0
  - Step 6 (goal): G₀ = 0 + 0.99⁵ × 1.0 ≈ **0.951** (in `VALUE_COLOR`)
- `ValueTracker` drives the accumulator label; the label numeric-morphs at each step.
- Caption: "Five steps of nothing. Then, finally — a reward five steps away is still worth 95 cents on the dollar."

**rl_expert FLAG-4:** G₀ ≈ 0.951 is an inference: (0.99)^5 × 1.0 = 0.9509803... ≈ 0.951.
The Technical Validator must confirm this value via live computation before scene code is written.

**Narration intention:** The numeric accumulation makes abstract discounting
concrete. The viewer watches the accumulator stay at zero through five steps,
then jump to 0.951. The key insight is that the reward at the end *has arrived*
in the agent's objective — it was not lost, just reduced by the distance.
The patience of `γ = 0.99` is almost complete.

**Screen primary (per step):** Active path cell + floating reward label (with accumulator as secondary)

**Helpers:**
- `EpisodeTrail.step_to()` for path highlight
- `ValueTracker` + `always_redraw` for accumulator label (numeric morph per step)
- `LaggedStart` for path cells
- `place_caption`

**Wait:** `self.wait(1.5)` per path step + `self.ingestion_wait(2.5)` after final value appears

**Estimated time:** ~25 s

---

#### Phase S4-P13 — Gamma sweep: γ ∈ {0.5, 0.99, 1.0}

**Animation events:**
- `mark_phase("seg4_gamma_sweep")`
- Accumulator panel migrates inward (smaller). Gamma sweep `ActionBarChart` enters RIGHT via `FadeIn`.
- Three bars labeled "γ=0.5", "γ=0.99", "γ=1.0" with heights:
  - γ=0.5: G₀ = (0.5)⁵ = 0.031 (bar very short)
  - γ=0.99: G₀ ≈ 0.951 (bar tall)
  - γ=1.0: G₀ = 1.0 (bar full height)
- Bars use `VALUE_COLOR` fills. `ValueTracker`-driven heights.
- `γ` token in `Gt_sum` equation (LEFT panel) `Indicate`-pulses when gamma sweep chart appears.
- Caption first: "With γ=0.5, a reward five steps away is worth 3 cents. With γ=1.0, it is worth the full dollar."
- Caption second: "FrozenLake terminates — so γ=1 is valid here. But for tasks that run forever, γ<1 is required."

**rl_expert bound condition (M-4 defeat):** The γ=1 validity narration must
explicitly state it applies to episodic tasks with guaranteed termination.
For infinite-horizon tasks, γ < 1 is required to keep G_t finite.

**Narration intention (M-4 defeat):** The discount factor is NOT required to
prevent infinite rewards in episodic tasks. `γ = 0.99` is used in this series
to prepare for generalizing to continuing tasks — not because episodic FrozenLake
demands it. The viewer who hears "γ prevents infinite reward" is hearing an
incomplete story.

**Screen primary:** Gamma sweep `ActionBarChart` (RIGHT) — bars at three γ values

**Helpers:**
- `ActionBarChart(labels=["γ=0.5","γ=0.99","γ=1.0"], values=[0.031,0.951,1.0])` with `VALUE_COLOR` fills
- `ValueTracker` + `always_redraw` bars
- `Indicate` on `γ` token in equation (LEFT)
- `cross_highlight_pair` linking `γ` token → gamma bar chart
- `place_caption`

**Wait:** `self.wait(2.0)` after full sweep chart + both captions + `self.ingestion_wait(2.5)`

**Estimated time:** ~20 s

---

#### Phase S4-P14 — Return recursion derived (G_t = R_{t+1} + γG_{t+1})

**Animation events:**
- `mark_phase("seg4_recursion")`
- Gamma chart fades to `OPACITY_SECONDARY`. FrozenLake grid dims to `OPACITY_SECONDARY`.
- `Gt_sum` (LEFT panel) morphs into the recursive form via `equation_morph`:
  ```
  G_t = R_{t+1} + γ G_{t+1}
  ```
  The morph shows the tail `γR_{t+2} + γ²R_{t+3} + ⋯` collapsing into `γG_{t+1}`.
- `self.ingestion_wait(2.5)` after morph completes.
- Caption: "Factor out γ from the tail, and the entire future collapses into one term. That identity — G_t equals R_{t+1} plus γ times G_{t+1} — is the return recursion."
- Secondary caption: "We will see this identity again in the next video."

**Narration intention (FLAG-1 enforcement):** The recursion `G_t = R_{t+1} + γG_{t+1}`
is derived algebraically from the sum form. It is named "the return recursion." It is
NOT named "the Bellman equation." The Bellman equation takes expectations of this
recursion under a policy — a step that is explicitly deferred to V-02.

**Screen primary:** `G_t = R_{t+1} + γG_{t+1}` equation (CENTER-large, after morph)

**MathTex decomposition (recursive form — target of morph from Gt_sum):**
```python
Gt_recursive = MathTex(
    "G_t", "=",
    "R_{t+1}", "+",
    "\\gamma", "G_{t+1}",
    font_size=48,
)
# Gt_recursive[0].set_color(VALUE_COLOR)  # G_t
# Gt_recursive[2].set_color(REWARD_COLOR) # R_{t+1}
# Gt_recursive[4].set_color(VALUE_COLOR)  # γ
# Gt_recursive[5].set_color(VALUE_COLOR)  # G_{t+1}
```

**Helpers:**
- `equation_morph(scene, Gt_sum_panel_eq, Gt_recursive)` — `TransformMatchingTex`
- `self.ingestion_wait(2.5)` after morph
- `place_caption`

**Wait:** `self.wait(2.0)` after recursion + secondary caption + `self.ingestion_wait(2.5)`

**Estimated time:** ~18 s

---

#### Phase S4-P15 — Hold frame and forward tease

**Animation events:**
- `mark_phase("seg4_hold_frame")`
- All panels settle at `OPACITY_PRIMARY` for final hold:
  - LEFT: Return recursion equation `G_t = R_{t+1} + γG_{t+1}`
  - CENTER: FrozenLake grid (dimmed to `OPACITY_SECONDARY` — stable reference)
  - RIGHT: Gamma chart (dimmed to `OPACITY_SECONDARY`)
- Final takeaway caption (stable, no active highlights):
  "A Markov Decision Process. From any state and action, p tells you where you land and what reward you get. The agent's goal is to maximize G_t — the discounted sum of all future rewards."
- After 5 s, caption cross-fades to forward tease:
  "Next: we give the agent a *strategy* for choosing actions — and ask what each state is worth under that strategy."
- Final `self.wait(8.0)` (spec §10 pacing note: "Final hold: 8.0 s on takeaway caption")

**Narration intention:** The closing caption is the summary statement the viewer
will carry forward. It links `p(s',r|s,a)` and `G_t` as the two objects that
define the MDP. The forward tease plants the question V-02 will answer without
using any V-02 vocabulary (no "policy," no "value function").

**Screen primary:** Final takeaway caption (all visual elements at SECONDARY, caption is sole PRIMARY)

**Helpers:**
- `place_caption(takeaway_text)` — 8 s hold
- `FadeOut(takeaway_cap)` → `FadeIn(forward_cap)` — caption swap for forward tease
- `self.wait(8.0)` (spec pacing minimum; governs narration-sync for V&BGM agent)

**Wait:** `self.wait(8.0)` (final hold, per spec §10; spec overrides skill default of 2.5 s)

**Estimated time:** ~15 s

---

**Segment 4 subtotal:** ~90 s (matches spec pacing §10 ~6:00 + 1:00 forward tease = ~7:00 budget via narration expansion)

---

## Pacing beats

| Phase | After event | Duration |
|---|---|---|
| S1-P1 | Grid `FadeIn` + `ingestion_wait` | `self.wait(2.0)` + `self.ingestion_wait(2.5)` |
| S1-P2a | Failure 1 flash | `self.wait(2.0)` |
| S1-P2b | Failure 2 flash | `self.wait(1.5)` |
| S1-P3 | Success + reward label | `self.wait(2.5)` |
| S2-P4 | State index labels appear | `self.wait(2.0)` |
| S2-P5 | Markov reveal caption | `self.wait(2.0)` |
| S3a-P6 | p equation solo reveal | `self.wait(2.0)` + `self.ingestion_wait(2.5)` |
| S3a-P7 | Equation reposition | `self.ingestion_wait(2.5)` |
| S3a-P7 | Three outcome branches + trace vectors | `self.wait(2.0)` + `self.ingestion_wait(2.5)` |
| S3b-P8 | ActionBarChart full reveal + Σ=1 | `self.wait(1.5)` + `self.ingestion_wait(2.5)` |
| S3b-P9 | Chart migration + CodeStepper entry | `self.ingestion_wait(2.5)` |
| S3b-P9 | Each CodeStepper.step() | `self.wait(1.5)` (× 4 steps) |
| S3b-P10 | Normalization equation | `self.wait(2.0)` |
| S3b-P10 | Summation collapse morph | `self.ingestion_wait(2.5)` |
| S4-P11 | G_t equation solo reveal | `self.wait(2.0)` + `self.ingestion_wait(2.5)` |
| S4-P12 | G_t equation reposition | `self.ingestion_wait(2.5)` |
| S4-P12 | Each path step (× 6) | `self.wait(1.5)` per step |
| S4-P12 | Final accumulator value G₀≈0.951 | `self.ingestion_wait(2.5)` |
| S4-P13 | Gamma sweep chart full reveal | `self.wait(2.0)` + `self.ingestion_wait(2.5)` |
| S4-P14 | Return recursion morph | `self.wait(2.0)` + `self.ingestion_wait(2.5)` |
| S4-P15 | Final hold | `self.wait(8.0)` |

**Estimated total (animation events only, before narration expansion):**
Σ of animation event durations: ~40 + ~22 + ~30 + ~31 + ~35 + ~18 + ~15 s
= ~250 s base animation time. With narration expansion (Kokoro at 1.0×, ~130 wpm),
the Voice & BGM agent's synthesis will govern final timing. Spec estimate: ~21:00.

---

## Opacity layer assignments

**OPACITY_PRIMARY (1.0):**
- Active equation token being narrated (per §33.3 focused-explanation sub-phases)
- Agent sprite + active cell (S1 traversal phases)
- Active outcome branch (S3a-P7)
- Active bar + its state cell (S3b-P8 bar animations)
- Active code line + its cross-highlighted cell (S3b-P9 per step)
- Path cell + reward annotation (S4-P12 per step)
- Gamma bar at the currently-narrated γ value (S4-P13)
- Return recursion equation (S4-P14 after morph)
- Final takeaway caption (S4-P15)

**OPACITY_SECONDARY (0.4):**
- Inactive grid cells during agent traversal
- Non-focal equation tokens during focused-explanation sub-phases
- Prior bars when a new bar is primary
- Code lines not currently active
- Grid during equation-only phases (S3a-P6, S4-P11)
- Equation panel during final hold (S4-P15)
- Gamma chart during return recursion (S4-P14)

**OPACITY_BACKGROUND (0.17):**
- Grid tile backgrounds (ice/hole/goal PNGs) when state index labels are primary
- Coordinate axes (if any structural scaffold)
- Code panel chrome when not actively stepped

---

## Gymnasium code snippet

**Used ONLY in Segment 3b (CodeStepper). Not used in Segments 1, 2, or 3a.**

Verbatim from teaching spec §9.2 and `specs.py.code_focus_lines`:

```python
env = gym.make("FrozenLake-v1", is_slippery=True)
for prob, next_state, reward, done in env.unwrapped.P[6][2]:
    print(f"prob={prob:.3f}  next_state={next_state}  reward={reward}  done={done}")
```

**Expected output (Technical Validator must confirm before scene code is written):**
```
prob=0.333  next_state=10  reward=0.0  done=False
prob=0.333  next_state=7   reward=0.0  done=True
prob=0.333  next_state=2   reward=0.0  done=False
```

**Variable color bindings in code panel:**
- `prob` → `POLICY_COLOR` (it is a probability value)
- `next_state` → `STATE_COLOR`
- `reward` → `REWARD_COLOR`
- `done` → `PENALTY_COLOR` when `True`, white otherwise
- `6` (state index in `P[6]`) → `STATE_COLOR`
- `2` (action index RIGHT in `P[6][2]`) → `ACTION_COLOR`

---

## Code-visual sync points

| Code line idx | Phase step | Variable values | What the sync highlights |
|---|---|---|---|
| 0 | S3b-P9 step 0 | `env = gym.make(...)` | Full FrozenLake grid frame `Indicate` |
| 1 | S3b-P9 step 1 | `P[6][2]` — state 6, action RIGHT | State 6 cell `STATE_COLOR` pulse; RIGHT arrow `ACTION_COLOR` pulse |
| 2a | S3b-P9 step 2 sub-step 1 | `next_state=10, prob=0.333` | State 10 cell highlights; bar 2 (rightmost, state 10) grows to 1/3 |
| 2b | S3b-P9 step 2 sub-step 2 | `next_state=7, prob=0.333, done=True` | State 7 cell `PENALTY_COLOR` highlights; bar 1 (center, state 7) grows to 1/3 |
| 2c | S3b-P9 step 2 sub-step 3 | `next_state=2, prob=0.333` | State 2 cell highlights; bar 0 (leftmost, state 2) grows to 1/3; Σ=1 annotation pulses |

**Bar order note (FLAG-3):** Bars are left-to-right by next-state index (2, 7, 10).
Gymnasium's `P[6][2]` tuple order is (10, 7, 2). The `cross_highlight_pair` calls
at sub-steps 2a, 2b, 2c must reference the correct bar by position index (2→bar_idx=0,
7→bar_idx=1, 10→bar_idx=2), not by the iteration order in the Python loop.

---

## Boundary conditions and misconception defeats

The following are addressed at specific phases (mapping from spec §5):

| Misconception | Defeat phase | Defeat mechanism |
|---|---|---|
| M-1: p(s',r\|s,a) is the probability the agent chooses action a | S2-P5 / S3a-P7 | Two separate arrows: "agent chooses" → action arrow; "environment responds" → three probability branches. Visual separation of agency vs environment response. |
| M-2: FrozenLake has deterministic transitions (p=1 for one outcome) | S3b-P8 | ActionBarChart: three equal bars at 1/3 each. No bar at full height. Caption explicitly states "equally likely." |
| M-3: RL is supervised learning with delayed feedback | S1-P2a / S1-P2b | Two failed attempts receive reward=0 with NO indication of correct action. The absence of guidance IS shown visually. |
| M-4: γ<1 is required to prevent infinite rewards | S4-P13 | γ=1.0 bar shown explicitly. Narration: "FrozenLake terminates — so γ=1 is valid here." |
| M-5: p(s'\|s,a) and p(s',r\|s,a) are the same | S3b-P10 | Summation collapse morph shows p(s'\|s,a) = Σ_r p(s',r\|s,a) on screen. |

---

## RL Expert collaboration notes

**Pre-brief consultation:**

The narrative hook and key equations were reviewed against the teaching spec authored
by the RL Expert. The spec was provided as the creative source of truth (status:
Advisory — no gate decision required for new lessons). All five flag items from the
production brief have been incorporated:

- **FLAG-1:** The return recursion `G_t = R_{t+1} + γG_{t+1}` is named "the return
  recursion" in S4-P14 narration, caption, and plan text. The word "Bellman" does
  not appear anywhere in connection with this identity.
- **FLAG-2:** `CodeStepper` appears ONLY in Segment 3b (Phase S3b-P9). Segments 1,
  2, and 3a have no `CodeStepper`. This is enforced in the spec (§9.1) and in this
  plan's phase descriptions.
- **FLAG-3:** `ActionBarChart` bars are sorted left-to-right by next-state index:
  state 2 (bar 0, leftmost) → state 7 (bar 1, center) → state 10 (bar 2, rightmost).
  Cross-highlight matrix maps loop iteration order to bar position index correctly.
- **FLAG-4:** G₀ ≈ 0.951 is noted as an inference requiring Technical Validator
  confirmation ((0.99)^5 × 1.0 = 0.9509803...). The claim is presented as "≈ 0.951"
  in all equations and accumulator labels. The Technical Validator must run live
  computation before the Manim Expert writes code.

**Concepts explicitly excluded (V-02 boundary, spec §2.4):**
- Policy π(a|s) — not named anywhere in this plan
- State-value function v_π(s) — not named
- Action-value function q_π(s,a) — not named
- Bellman equation of any kind — not named
- Optimal policy / optimal value — not named

The forward-tease caption in S4-P15 uses the phrase "a *strategy* for choosing
actions" (not "policy") and "what each state is worth" (not "value function") to
plant the question without crossing the V-02 boundary. This phrasing was reviewed
against spec §7.3 banned patterns.

**RL Expert status:** APPROVED (advisory; spec §1 explicitly states "Status: Advisory —
no gate decision required (new lesson, no prior submission)")

---

## Output checklist (self-verification)

1. Does Phase S1-P1 show geometry only — no equation? **YES.** Grid entry, no formulas.
2. Is the equation in Phase 3 or later? **YES.** First equation appears in S3a-P6.
3. Are all color assignments drawn from the STYLE_BIBLE palette only? **YES.** Table verified against STYLE_BIBLE §1.
4. Is every pacing beat at or above the minimum durations from STYLE_BIBLE §6? **YES.** All waits checked against the pacing table; minimum 1.5 s per sync step, 2.0 s after geometry/equation entry, 2.5 s `ingestion_wait` after morphs.
5. Does `self.wait(2.5)` appear as the final hold? **EXTENDED to 8.0 s** per spec §10 pacing note. The 8.0 s hold satisfies the 2.5 s minimum.
6. Is the Gymnasium code snippet the exact text from the teaching spec? **YES.** Verbatim from spec §9.2 and `specs.py.code_focus_lines`. Three lines, real Python variable names.
7. Is the MathTex decomposition shown as a component array? **YES.** Four equations decomposed: `p_eq_full`, `norm_eq`, `marginal_eq`, `Gt_sum`, `Gt_recursive`.
8. Does the layout matrix show only one panel per region per phase? **YES.** Reserved-hemisphere layout matrix explicit for all 15 phases.
9. Are code-visual sync points one-to-one? **YES.** Cross-highlight matrix has exactly one geometric target per step (with sub-steps explicitly mapped for line 2).
10. Is the RL Expert collaboration section filled in? **YES.** All flags addressed; V-02 boundary enforced.
11. Does every phase include a `narration_intention` field? **YES.** Present for all 15 phases.
12. Does the `narration_intention` explain MEANING — not describe the animation? **YES.** Each narration intention describes the conceptual insight, not the animation event.
13. Is the Screen Focus Budget filled in for every phase? **YES.** 15 phases covered in the Screen Focus Budget table.
14. Does the Screen Focus Budget name a single PRIMARY element per phase? **YES.** At most one primary element per phase; trace_vector pairs treated as one teaching unit.
15. Are Gymnasium asset paths cited? **YES.** Full verification command in "Gymnasium Assets Required" section.
16. Does the Conversational Arc section name the rhetorical journey? **YES.** Six-element arc from opening tension to forward hook.
