# Choreography — mdp_foundations

**plan.md reference:** manim_service/concept_videos/mdp_foundations_plan.md
**Visual Director:** visual-director (skill)
**Date:** 2026-05-23
**Series position:** V-02 of Wave 1

---

## 1. Scientific Rigor

The video claims that a finite MDP supplies states, actions, rewards, transition probabilities, policies, returns, value functions, and the Bellman expectation equation. Evidence for each claim is visible on the same FrozenLake grid: state indices and terminal cells for 𝒮/𝒮⁺, action arrows for 𝒜, reward tokens for R, the state-6 RIGHT fan for p, policy bars for π, a non-optimal uniform-policy heatmap for v_π, and a backup tree for eq. 3.14. The state-6 RIGHT fan must use the live Gymnasium successor set {7,2,10}, each with probability 1/3, and never the old reference constant {7,2,5}. The value heatmap is a conceptual reading under a uniform-random policy, not an iterative computation. The closing preview names dp_policy_eval without displaying its loop, sweep, or assignment.

## 2. Pedagogical Strategy

**Primary pattern:** Bottom-up assembly

**Why this pattern suits this lesson:** MDP foundations are a vocabulary chain, so the learner needs each symbol to earn its place before the Bellman equation appears. One persistent grid reduces extraneous load: new concepts are overlays on the same spatial anchor rather than separate mini-lessons.

**Misconception this strategy specifically defeats:** M1 is defeated by visually separating the environment p-fan from the agent π panel. M4 is defeated by showing v_π for a uniform-random, non-optimal policy. M5 is defeated by deriving eq. 3.14 from the return recursion.

## 3. Cognitive Load Budget

| Phase | Primary mobjects at phase start | Primary mobjects at phase mid | Primary mobjects at phase end | Notes |
|---|---|---|---|---|
| (a) | header, grid | grid, state labels, action legend | grid, Markov note | ≤4 primary |
| (b) | grid, reward tokens | return equation, reward stream, γ label | recursion equation, grid | recursion is load-bearing |
| (c) | grid, fan arrows | fan arrows, ActionBarChart, code line | p equation, chart, grid | chart has three bars only |
| (d) | grid | PolicyArrowGrid, uniform bars, π equation | policy contrast note, grid | visually distinct from p-fan |
| (e) | grid | ValueHeatmap, value equations, q-bars | v-q bridge, terminal zeros | non-optimal policy label required |
| Recap | dimmed grid | recap card | recap card, dimmed grid | reset before derivation |
| (f) | recursion equation | BackupDiagram, derivation line, active branch | expanded Bellman equation, backup tree | term-by-term mapping |
| Closing | final equation | final equation, next pill, dimmed grid | same | no algorithm shown |

## 4. Element Lifecycle Matrix

| Mobject | Phase IN | Visible during | Phase OUT | Re-enters at |
|---|---|---|---|---|
| Header | (a) | all phases | scene end | never |
| FrozenLake grid | (a) | all phases | scene end | never |
| State labels 0–15 | (a) | all phases | scene end | never |
| Action legend | (a) | (a) | end of (a) FadeOut | never |
| Markov property note | (a) | (a) | end of (a) FadeOut | never |
| Reward stream | (b) | (b) | end of (b) FadeOut | never |
| Return equations | (b) | (b), (f) via copied recursion | end of (f) FadeOut | (f) |
| State-6 fan arrows | (c) | (c) | end of (c) FadeOut | never |
| ActionBarChart {7,2,10} | (c) | (c) | end of (c) FadeOut | never |
| CodeStepper | (c) | (c), (d) line 3 | end of (d) FadeOut | never |
| PolicyArrowGrid | (d) | (d) | end of (d) FadeOut | never |
| Uniform policy bars | (d) | (d) | end of (d) FadeOut | never |
| ValueHeatmap | (e) | (e), dimmed during recap and (f) | scene end | never |
| q-bars | (e) | (e) | end of (e) FadeOut | never |
| Recap card | Recap | Recap | before (f) FadeOut | never |
| BackupDiagram | (f) | (f), Closing | scene end | never |
| Bellman derivation equations | (f) | (f), Closing | scene end | never |
| Next pill | Closing | Closing | scene end | never |

## 5. Motion Choreography (per-phase)

### Phase (a) — MDP framework

| Time | Animation | Purpose tag | Manim helper |
|---|---|---|---|
| 0.0 s | `show_header("MDP Foundations", "From states to the Bellman equation")` | REVEAL | BaseConceptScene |
| 1.4 s | FadeIn persistent FrozenLake grid centered | REVEAL | `frozenlake_frame(6)` |
| 3.0 s | LaggedStart state labels 0–15 over grid | REVEAL | Text labels |
| 6.0 s | FadeIn action legend LEFT/DOWN/RIGHT/UP = 0/1/2/3 | CONNECT | `action_arrows_overlay` |
| 9.0 s | Write Markov property note beside grid | DERIVE | MathTex/Text |
| 12.0 s | FadeOut action legend and note; grid remains | RESOLVE | FadeOut |

### Phase (b) — Rewards and returns

| Time | Animation | Purpose tag | Manim helper |
|---|---|---|---|
| 0.0 s | FadeIn three reward tokens along path ending at goal | REVEAL | Text/Dot |
| 2.0 s | Write discounted return expanded sum | DERIVE | MathTex component array |
| 5.0 s | Numeric γ example `[0,0,1], γ=0.99 -> 0.9801` | RESOLVE | Text/MathTex |
| 8.0 s | ReplacementTransform tail into `G_t=R_{t+1}+γG_{t+1}` | DERIVE | ReplacementTransform |
| 11.0 s | Trace reward token to `R_{t+1}` and tail to `G_{t+1}` | CONNECT | `trace_vector` |

### Phase (c) — Transition probability

| Time | Animation | Purpose tag | Manim helper |
|---|---|---|---|
| 0.0 s | Highlight state 6 and RIGHT action | REVEAL | Circumscribe/Create |
| 1.5 s | Create three arrows to states 7, 2, 10 with tuple labels | REVEAL | Create |
| 4.0 s | FadeIn ActionBarChart with labels 7, 2, 10 and values 1/3 | RESOLVE | `ActionBarChart` |
| 6.5 s | Write `p(s',r|s,a)` and `Σp=1` caption | DERIVE | MathTex |
| 8.5 s | FadeIn CodeStepper and step lines 0–2 with cross-highlights | CONNECT | `CodeStepper`, `cross_highlight_pair` |
| 15.0 s | FadeOut p-fan and p-chart; grid remains | RESOLVE | FadeOut |

### Phase (d) — Policies

| Time | Animation | Purpose tag | Manim helper |
|---|---|---|---|
| 0.0 s | FadeIn deterministic PolicyArrowGrid on left | REVEAL | `PolicyArrowGrid` |
| 2.0 s | FadeIn uniform policy bars on right, each 0.25 | REVEAL | `ActionBarChart` |
| 4.0 s | Write `π(a|s)=Pr{A_t=a|S_t=s}` and `Σ_aπ=1` | DERIVE | MathTex |
| 6.0 s | Step CodeStepper line 3 and highlight uniform bars | CONNECT | `cross_highlight_pair` |
| 8.0 s | Caption contrast: p is environment, π is agent | RESOLVE | Text |

### Phase (e) — Value functions

| Time | Animation | Purpose tag | Manim helper |
|---|---|---|---|
| 0.0 s | FadeOut policy panels; FadeIn ValueHeatmap overlay | REVEAL | `ValueHeatmap` |
| 2.5 s | Highlight terminal cells {5,7,11,12,15} with value 0 | RESOLVE | Circumscribe |
| 4.5 s | Write `v_π(s)=E_π[G_t|S_t=s]` | DERIVE | MathTex |
| 6.5 s | FadeIn q-bars for state 6 actions | REVEAL | `ActionBarChart` |
| 8.5 s | Write `q_π(s,a)=E_π[G_t|S_t=s,A_t=a]` and `v_π=Σ_aπq_π` | DERIVE | MathTex |
| 11.0 s | Caption: v_π exists for any π, including uniform-random | RESOLVE | Text |

### Recap — cognitive reset

| Time | Animation | Purpose tag | Manim helper |
|---|---|---|---|
| 0.0 s | Dim grid and heatmap to background opacity | REFRAME | opacity animation |
| 1.0 s | FadeIn recap card with five symbol meanings | REVEAL | `panel`, `note_stack` |
| 5.0 s | FadeOut recap card, keep grid dimmed | RESOLVE | FadeOut |

### Phase (f) — Bellman expectation equation

| Time | Animation | Purpose tag | Manim helper |
|---|---|---|---|
| 0.0 s | Write copied recursion `G_t=R_{t+1}+γG_{t+1}` | REVEAL | MathTex |
| 2.5 s | Morph to `v_π(s)=E_π[G_t|S_t=s]` | DERIVE | `equation_morph` |
| 6.0 s | Morph to `v_π(s)=E_π[R_{t+1}+γG_{t+1}|S_t=s]` | DERIVE | `equation_morph` |
| 9.5 s | FadeIn BackupDiagram with root s, action dots, outcome leaves | REVEAL | `BackupDiagram` |
| 12.0 s | Highlight action branch and write `π(a|s)` | CONNECT | `BackupDiagram.highlight_action`, `trace_vector` |
| 15.0 s | Highlight outcome leaves and write `p(s',r|s,a)` | CONNECT | `BackupDiagram.highlight_outcome`, `trace_vector` |
| 18.0 s | Write leaf annotation `[r+γv_π(s')]` | CONNECT | `trace_vector` |
| 21.0 s | Morph to full double-sum Bellman equation eq. 3.14 | DERIVE | `equation_morph` |

### Closing — preview policy evaluation

| Time | Animation | Purpose tag | Manim helper |
|---|---|---|---|
| 0.0 s | FadeIn pill `Next: dp_policy_eval` | REVEAL | `pill` |
| 1.5 s | Caption: "Policy evaluation turns this equality into an assignment." | CONNECT | `place_caption` |
| 4.0 s | Stable final hold, no loop or assignment shown | RESOLVE | `self.wait(2.5)` |

## 6. Camera Shot List

| Phase | Shot | Trigger time | Helper | Duration | Purpose |
|---|---|---|---|---|---|
| (c) | zoom_to state 6 fan | after state 6 highlight | `zoom_to(self, fan_group, scale=0.75)` | 1.4 s | Reframe for successor-set correction |
| (c) | zoom_reset | after chart reveal | `zoom_reset(self)` | 1.4 s | Return to full layout |
| (f) | zoom_to derivation equation | before first morph | `zoom_to(self, derivation_eq, scale=0.65)` | 1.4 s | Reframe for algebra |
| (f) | zoom_reset | before BackupDiagram enters | `zoom_reset(self)` | 1.4 s | Return to equation/tree mapping |

## 7. Sprite-Math Binding Matrix (only phases with motion)

| Phase | Sprite action | Equation token(s) that highlight | Code line that highlights | Helper |
|---|---|---|---|---|
| (b) | reward token lands on goal | `R_{t+1}` | none | `trace_vector(...)` |
| (c) | state-6 RIGHT fan points to 7,2,10 | `p(s',r|s,a)`, `s'`, `a` | line 1 | `cross_highlight_pair(...)` |
| (d) | policy bars all settle at 0.25 | `π(a|s)`, `Σ_aπ=1` | line 3 | `cross_highlight_pair(...)` |
| (f) | backup root branches to action node | `π(a|s)` | none | `trace_vector(...)` |
| (f) | action node branches to leaves | `p(s',r|s,a)` | none | `trace_vector(...)` |
| (f) | leaf label appears | `[r+γv_π(s')]` | none | `trace_vector(...)` |

## 8. trace_vector Source-Target Pairs (per equation token first appearance)

| Phase | Equation token | Source geometry on canvas | Color | Helper |
|---|---|---|---|---|
| (b) | `R_{t+1}` | first reward token | `REWARD_COLOR` | `trace_vector(...)` |
| (b) | `γG_{t+1}` | tail of reward stream | `VALUE_COLOR` | `trace_vector(...)` |
| (c) | `s` | focal state 6 cell | `STATE_COLOR` | `trace_vector(...)` |
| (c) | `a` | RIGHT action arrow | `ACTION_COLOR` | `trace_vector(...)` |
| (c) | `s'` | successor cells 7,2,10 | `STATE_COLOR` | `trace_vector(...)` |
| (c) | `p(s',r|s,a)` | three 1/3 bars | `POLICY_COLOR` | `trace_vector(...)` |
| (d) | `π(a|s)` | uniform policy bars | `POLICY_COLOR` | `trace_vector(...)` |
| (e) | `v_π(s)` | value heatmap cell | `VALUE_COLOR` | `trace_vector(...)` |
| (e) | `q_π(s,a)` | q-bars for state 6 | `VALUE_COLOR` | `trace_vector(...)` |
| (f) | `π(a|s)` | BackupDiagram action branch | `POLICY_COLOR` | `trace_vector(...)` |
| (f) | `p(s',r|s,a)` | BackupDiagram leaf branches | `STATE_COLOR` | `trace_vector(...)` |
| (f) | `[r+γv_π(s')]` | leaf annotation | `REWARD_COLOR`/`VALUE_COLOR` | `trace_vector(...)` |

## 9. Hand-off Notes for the Manim Expert

Use the grid as a persistent scene object and add overlay layers; do not use `VGroup.become()` or rebuild the grid. The state-6 RIGHT bar chart has exactly three bars labelled 7, 2, 10, all 1/3, with Σp=1 under the bars. Use a uniform-random policy for the policy and value-function beats. The Bellman derivation must show the recursion-to-expectation-to-double-sum chain before the final equation.
