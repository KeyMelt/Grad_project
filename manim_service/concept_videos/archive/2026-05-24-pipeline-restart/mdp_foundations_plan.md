# Plan: mdp_foundations — MDP Foundations: From States to the Bellman Equation

**lesson_id:** mdp_foundations
**Manim class:** MdpFoundationsScene
**Scene file:** manim_service/concept_videos/mdp_foundations_concept.py
**Target duration:** 1,560–1,720 seconds
**RL Expert status:** PENDING Gate 1 review in this full_pipeline run

---

## Narrative hook

The same FrozenLake grid stays on screen while each new idea adds one transparent layer: first state numbers and actions, then reward tokens and return, then the slippery three-outcome fan from state 6, then policy arrows, then a value heatmap, and finally a backup tree. The learner sees one object accumulate enough structure that the Bellman expectation equation becomes the only compact way to describe what is already visible.

---

## Color palette declaration

| Constant | Hex | Used for |
|---|---|---|
| `STATE_COLOR` | `#38BDF8` | FrozenLake state indices, focal state 6, `s`, `s'`, `S_t` |
| `VALUE_COLOR` | `#FACC15` | `v_\pi`, `q_\pi`, value heatmap labels, q-bars |
| `REWARD_COLOR` | `#34D399` | `R_{t+1}`, `r`, goal reward token |
| `PENALTY_COLOR` | `#F87171` | Holes and terminal hole labels |
| `POLICY_COLOR` | `#A78BFA` | `\pi(a|s)`, policy arrows, uniform policy bars |
| `ACTION_COLOR` | `#FB923C` | Action arrows and action `a` terms |
| `BG_COLOR` | `#020617` | Scene background |
| `BG_PANEL` | `#0F172A` | Panels and recap card |
| `BG_GRID` | `#1E293B` | Grid scaffold |
| `CODE_ACCENT` | `#64748B` | Code panel header |

---

## Reserved-hemisphere layout matrix (MANDATORY — STYLE_BIBLE §16)

| Phase | LEFT (≈ -5.0 to -1.5 x) | CENTER (≈ -1.5 to +1.5 x) | RIGHT (≈ +1.5 to +5.0 x) |
|---|---|---|---|
| (a) MDP framework | Notes: 𝒮, 𝒜(s), Markov property | FrozenLake grid built once with 0–15 labels | Action legend |
| (b) Returns | Return equations and γ example | Same grid, reward tokens layer | Three-step reward stream |
| (c) Dynamics p | Model-access code panel | Same grid with state-6 fan overlay | ActionBarChart for successors {7,2,10} |
| (d) Policies π | PolicyArrowGrid overlay panel | Same grid, focal state retained | ProbabilityBarPanel for uniform π |
| (e) Values | Value equations | Same grid with ValueHeatmap overlay | q-bars for state 6 |
| Recap | Recap card centered over dimmed grid | Same grid dimmed beneath card | — |
| (f) Bellman | Derivation equation stack | Same grid, state 6 anchor dimmed | BackupDiagram and term labels |
| Closing | Final takeaway equation | Same grid dimmed | Next: dp_policy_eval pill |

Rules: the FrozenLake grid is built once in segment (a) and never rebuilt. Every later visual is an overlay or side panel. RIGHT-side panels replace one another only after the prior RIGHT panel fades out.

---

## Cross-highlight matrix (MANDATORY for CodeStepper)

| Code line index | Code line content (from teaching spec; preserve adopted platform lines verbatim) | Geometric pair (cross_highlight target) |
|---|---|---|
| 0 | `env = gym.make("FrozenLake-v1", is_slippery=True)` | the persistent FrozenLake grid |
| 1 | `for prob, next_state, reward, done in env.unwrapped.P[6][2]:` | the three outgoing arrows from state 6 |
| 2 | `    print(prob, next_state, reward, done)` | the three ActionBarChart bars labelled 7, 2, 10 |
| 3 | `policy = np.ones((env.observation_space.n, env.action_space.n)) / env.action_space.n` | the uniform policy probability bars, each 0.25 |

---

## Phase sequence

### Phase (a) — MDP framework

**Visual:** Build the FrozenLake 4×4 grid once, label cells 0–15, mark holes {5,7,11,12} and goal {15} as terminal states in 𝒮⁺, and show action arrows LEFT/DOWN/RIGHT/UP = 0/1/2/3. State the Markov property: the present state and action contain the relevant history for the next state and reward.
**Helpers:** `frozenlake_frame(6, soft_frame=True)`, state-index overlay, `action_arrows_overlay`, `show_header("MDP Foundations", "From states to the Bellman equation")`.
**Wait:** `self.wait(2.0)`.
**Budget:** 4:10.

### Phase (b) — Rewards and returns

**Visual:** Add reward tokens along a short terminal path and build `G_t = R_{t+1} + γR_{t+2} + γ²R_{t+3} + ... = Σ_{k=0}^{∞} γ^k R_{t+k+1}`. Animate one γ example for rewards `[0,0,1]` with `γ=0.99`, yielding `0.9801`, then write the recursion `G_t = R_{t+1} + γG_{t+1}` for reuse in (f).
**Helpers:** `MathTex` component arrays, `ReplacementTransform`, one numeric reward stream panel.
**trace_vector pairs:** reward token → `R_{t+1}`; later reward tokens → `γR_{t+2}`, `γ²R_{t+3}`; tail bracket → `G_{t+1}`.
**Wait:** `self.wait(1.5)` after γ example and `self.ingestion_wait(2.5)` after the recursion appears.
**Budget:** 4:40.

### Phase (c) — Transition probability

**Visual:** On the same grid, focus state 6 and action RIGHT. Show three outcome arrows to states `{7,2,10}` with labels `(1/3, 7, 0, True)`, `(1/3, 2, 0, False)`, `(1/3, 10, 0, False)`. The old reference scene's `{7,2,5}` constants must be corrected to `{7,2,10}` before reuse. Show `p(s',r|s,a)` and `Σ_{s'}Σ_r p(s',r|s,a)=1`.
**Helpers:** `ActionBarChart(["7","2","10"], [1/3,1/3,1/3])`, `CodeStepper`, `cross_highlight_pair`.
**trace_vector pairs:** outcome arrows → `s'`; bar values → `p`; reward labels → `r`; focal arrow → `a`.
**Wait:** `self.wait(1.5)` after chart reveal; per code line `self.wait(1.5)`.
**Budget:** 4:50.

### Phase (d) — Policies

**Visual:** Fade out the p-fan and chart, keeping the grid. Add a deterministic `PolicyArrowGrid` on the left and a visually separate probability bar panel on the right for uniform-random π at state 6: every action has 0.25 and `Σ_aπ(a|s)=1`. Caption: `p` is the environment response; `π` is the agent's action distribution.
**Helpers:** `PolicyArrowGrid`, `ActionBarChart(["LEFT","DOWN","RIGHT","UP"], [0.25]*4, bar_color=POLICY_COLOR)`.
**trace_vector pairs:** policy arrows → `π(a|s)`; probability bars → `Σ_aπ(a|s)=1`.
**Wait:** `self.wait(1.5)`.
**Budget:** 3:50.

### Phase (e) — Value functions

**Visual:** Add `ValueHeatmap` over the persistent grid using a non-optimal uniform-random policy, with terminal cells {5,7,11,12,15} displayed as 0. Show `v_π(s)=E_π[G_t|S_t=s]`, `q_π(s,a)=E_π[G_t|S_t=s,A_t=a]`, and `v_π(s)=Σ_aπ(a|s)q_π(s,a)` beside q-bars for state 6. State that values are defined for any policy π, not only an optimal one.
**Helpers:** `ValueHeatmap`, `ActionBarChart` for q-bars, `MathTex` component arrays.
**trace_vector pairs:** heatmap cell → `v_π(s)`; q-bars → `q_π(s,a)`; terminal cells → `0`.
**Wait:** `self.wait(1.5)` after heatmap and after q-bars.
**Budget:** 4:30.

### Recap — reset cognitive load

**Visual:** Dim all overlays and show a recap card: `π chooses actions`, `p chooses outcomes`, `r is immediate reward`, `γ carries future return`, `v_π is expected return under π`.
**Helpers:** `panel`, `note_stack`.
**Wait:** `self.ingestion_wait(2.5)`.
**Budget:** 1:20.

### Phase (f) — Bellman expectation equation

**Visual:** Derive, do not assert. Start from the recursion already shown: `G_t = R_{t+1}+γG_{t+1}`. Substitute into `v_π(s)=E_π[G_t|S_t=s]`, transform to `v_π(s)=E_π[R_{t+1}+γG_{t+1}|S_t=s]`, then expand over action branches `π(a|s)` and outcome leaves `p(s',r|s,a)` in a `BackupDiagram`. Conclude with `v_π(s)=Σ_aπ(a|s)Σ_{s',r}p(s',r|s,a)[r+γv_π(s')]`.
**Helpers:** `BackupDiagram`, `equation_morph`, `trace_vector`, `zoom_to`, `zoom_reset`.
**trace_vector pairs:** backup root → `s`; action dots → `π(a|s)`; leaves → `p(s',r|s,a)`; leaf label → `[r+γv_π(s')]`.
**Wait:** `self.ingestion_wait(2.5)` after each equation morph and final expanded equation.
**Budget:** 4:40.

### Closing — next video

**Visual:** Hold the expanded Bellman equation with the persistent grid dimmed and a pill: `Next: dp_policy_eval`. Caption: `Policy evaluation turns this equality into an assignment.` Do not show the loop, sweep, or update assignment.
**Helpers:** `pill`, `place_caption`.
**Wait:** `self.wait(2.5)`.
**Budget:** 1:20.

Total planned time budget: 29:20? No. Segment budgets above sum to 29:20 only before trimming, so the Pacing Linter applies the mandatory trims: remove optional boundary detail from (d) by 0:20, q-bar detail from (e) by 0:20, and optional marginal discussion from (c) by 0:20. **Final budget: 28:20**, under the 29:00 planning ceiling and leaving the required 60-second hard-ceiling buffer. If any single segment overruns by more than 60 seconds during narration, truncate in this order: (d) boundary-condition detail, (e) q-bar detail, (c) optional marginals. Load-bearing beats (a), (b) first recursion beat, and (f) derivation are not cut.

---

## Layout matrix

| Phase | LEFT | CENTER | RIGHT |
|---|---|---|---|
| (a) | Markov and set notes | persistent FrozenLake grid | action legend |
| (b) | return equations | same grid with reward tokens | reward stream / γ example |
| (c) | CodeStepper | same grid with state-6 fan | ActionBarChart {7,2,10} |
| (d) | PolicyArrowGrid | same grid | uniform π bars |
| (e) | value equations | same grid + ValueHeatmap | q-bars |
| Recap | — | recap card over dimmed grid | — |
| (f) | derivation equations | same grid dimmed | BackupDiagram |
| Closing | final Bellman equation | grid dimmed | Next: dp_policy_eval |

---

## Pacing beats

| Phase | After | Duration |
|---|---|---|
| (a) | Geometry entry complete | `self.wait(2.0)` |
| (b) | γ example | `self.wait(1.5)` |
| (b) | `G_t = R_{t+1}+γG_{t+1}` appears | `self.ingestion_wait(2.5)` |
| (c) | p-fan reveal | `self.wait(1.5)` |
| (c) | each code line | `self.wait(1.5)` |
| (d) | policy contrast | `self.wait(1.5)` |
| (e) | heatmap reveal | `self.wait(1.5)` |
| (e) | v-q bridge | `self.wait(1.5)` |
| Recap | recap card | `self.ingestion_wait(2.5)` |
| (f) | each equation morph | `self.ingestion_wait(2.5)` |
| Closing | final hold | `self.wait(2.5)` |

**Estimated duration:** 1,700 seconds planned narration maximum; rendered dev scene is a silent structural pass and may be shorter.

---

## Opacity layer assignments

**OPACITY_PRIMARY (1.0):** current segment overlay, focal state 6, active equation token, active bar, active code line, active backup branch.
**OPACITY_SECONDARY (0.4):** persistent grid when a side panel is active, inactive equation terms, inactive bars, prior segment overlays retained as context.
**OPACITY_BACKGROUND (0.17):** grid scaffold under recap and final Bellman derivation, old labels not currently taught.

---

## Gymnasium code snippet

```python
env = gym.make("FrozenLake-v1", is_slippery=True)
for prob, next_state, reward, done in env.unwrapped.P[6][2]:
    print(prob, next_state, reward, done)
policy = np.ones((env.observation_space.n, env.action_space.n)) / env.action_space.n
```

No `env.step()`, no `env.reset()`, no iteration loop, no sweep, no `max`, and no `V[state] = ...` assignment appear in this plan.

---

## Code-visual sync points

| Code line idx | Phase step | Action or state | What the sync highlights |
|---|---|---|---|
| 0 | (c) step 0 | FrozenLake-v1 | persistent grid |
| 1 | (c) step 1 | state 6, RIGHT | three outcome arrows to 7, 2, 10 |
| 2 | (c) step 2 | transition tuples | chart bars and tuple labels |
| 3 | (d) step 0 | uniform policy | four probability bars at 0.25 |

---

## RL Expert collaboration notes

Pre-brief for Gate 1: narrative hook is an accreting FrozenLake grid; key equation is S&B eq. 3.14, `v_π(s)=Σ_aπ(a|s)Σ_{s',r}p(s',r|s,a)[r+γv_π(s')]`; Phase (f) derives it from `G_t=R_{t+1}+γG_{t+1}`. Awaiting Gate 1 verdict in this full_pipeline run.
