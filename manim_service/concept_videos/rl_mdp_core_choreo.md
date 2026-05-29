# Choreography — rl_mdp_core

**plan.md reference:** manim_service/concept_videos/rl_mdp_core_plan.md
**Visual Director:** visual-director (skill)
**Date:** 2026-05-24
**Series position:** 1 of 10
**Manim class:** `RLMDPCoreConcept`

---

## 1. Scientific Rigor

The video makes four categories of claims. First, that FrozenLake-v1
(`is_slippery=True`) with action RIGHT from state 6 yields exactly three
equiprobable transitions to states {2, 7, 10} each with probability 1/3,
reward 0.0 for all, and `done=True` only for state 7 (a hole) — evidence is
the three-bar `ActionBarChart` and the `CodeStepper` iterating
`env.unwrapped.P[6][2]`; this value was confirmed by the Technical Validator
(corrected from the erroneous {7, 2, 5} in the prior `transition_prob_concept.py`).
Second, that the return for path 0→4→8→9→10→14→15 with γ=0.99 is
G₀ = (0.99)⁵ × 1.0 ≈ 0.951; the "≈" notation is deliberate — this is
an inference that the Technical Validator must confirm via live computation
before any Manim code is written (S&B §3.2, eq. 3.8, p. 55; see FLAG-4).
Third, that the recursion G_t = R_{t+1} + γG_{t+1} is derived algebraically
from the infinite sum and is named "the return recursion" throughout — it is
**not** the Bellman equation (which takes expectations under a policy and
belongs to V-02). Fourth, that γ=1 is valid for episodic FrozenLake because
termination is guaranteed (S&B §3.4, p. 57), and the video states this
qualification explicitly during the gamma sweep; omitting it would mislead
viewers about continuing tasks.

---

## 2. Pedagogical Strategy

**Primary pattern:** Bottom-up assembly (with embedded Failure case + recovery).

**Why this pattern fits this lesson:** `rl_mdp_core` is the opening video —
no prior equations, no prior visual vocabulary. Starting from the concrete
experience of watching the elf fail twice before succeeding (Segment 1) builds
the intuition bottom-up: slippery outcomes → p(s',r|s,a) names the
distribution → G_t aggregates the rewards → the return recursion folds the
future. Each formula is earned by a visual the viewer has already lived through.
The embedded "failure case" beats (two failed episodes before the successful
one) directly defeat misconception M-3 (RL = supervised learning with delayed
feedback) by showing zero reward with zero guidance — no correct-action label
ever appears.

**Misconception this strategy specifically defeats:** M-1 (p(s',r|s,a) is
the probability the agent chooses action a) is defeated in S3a-P7 by the
dual-arrow construction: the agent's choice is the action arrow (ACTION_COLOR)
while the environment's response is the three probability branches — two
separate visual objects, one teaching unit. This misconception is documented
in `rl_knowledge_base.md` (transition_prob entry, "Common misconceptions").

---

## 3. Cognitive Load Budget (≤ 4 primary mobjects per frame)

Counting rules applied: Header (title + subtitle) = 1; Caption = 1; FrozenLake
grid (per-tile VGroup) = 1; equation MathTex = 1 (unless split-opacity applies);
action arrow + label together = 1 (grouped subordinate); three outcome branches
= 1 (grouped); ActionBarChart (full) = 1; CodeStepper = 1; accumulator panel = 1;
agent sprite = 1 (separate from grid when it is the focal object).

| Phase | Primary mobjects at phase start | Primary mobjects at phase mid | Primary mobjects at phase end | Notes |
|---|---|---|---|---|
| S1-P1 | header, FrozenLake grid (full) (2) | header, grid, caption (3) | header, grid, caption (3) | Grid is sole PRIMARY visual — full CENTER |
| S1-P2a | header, grid, agent sprite, caption (4) | header, grid, agent sprite, caption (4) | header, agent-at-hole (PENALTY flash), caption (3) | At failure flash: grid dims to SECONDARY; hole cell + agent = 1 combined focal |
| S1-P2b | header, grid, agent sprite (reset), caption (4) | header, grid, agent trail + sprite, caption (4) | header, hole cell (PENALTY flash), caption (3) | Trail at SECONDARY during walk; hole flash brings cell to PRIMARY |
| S1-P3 | header, grid, agent sprite, caption (4) | header, grid, agent trail, caption (4) | header, goal cell (REWARD), reward label "1.0" (2) | Final frame: grid dims to SECONDARY; goal + reward label = PRIMARY |
| S2-P4 | header, grid (per-tile), caption (3) | header, state_labels VGroup (revealing), caption (3) | header, state_labels (settled), caption (3) | State labels are the PRIMARY; grid tiles drop to SECONDARY |
| S2-P5 | header, grid + state_labels, elf-at-6, caption (4) | header, elf-at-6, action_arrow_group, caption (4) | header, elf-at-6, action_arrow (solid), caption (4) | Dashed history arrow at SECONDARY when solid action arrow appears |
| S3a-P6 | p_eq_full (full-screen), header (2) | p_eq_full (writing), header (2) | p_eq_full (complete), caption (2) | FULL SCREEN — §33.2 compliance; nothing else at PRIMARY |
| S3a-P7 | p_eq_full (repositioned LEFT), grid (smaller, CENTER) (2) | grid (CENTER), three_branches, caption (3) | three_branches, active_trace_vector + eq_token pair (2) | Three branches = 1 grouped object; trace_vector + eq_token = 1 bound pair |
| S3b-P8 | p_eq (LEFT, SECONDARY), grid (CENTER, SECONDARY), ActionBarChart (RIGHT) (3) | ActionBarChart bars growing + active branch (CENTER) (2) | ActionBarChart (full, Σ=1 annotation), caption (2) | Chart is PRIMARY; eq and grid at SECONDARY |
| S3b-P9 (step 0) | CodeStepper (RIGHT-upper), ActionBarChart-inset (RIGHT-lower, SECONDARY), grid (CENTER, SECONDARY), caption (3) | code_line[0] (PRIMARY), grid (INDICATOR) (2) | code_line[0] (held), caption (2) | Step 0: grid Indicate = brief PRIMARY pulse |
| S3b-P9 (step 1) | code_line[1], state6_cell, action_arrow (3) | code_line[1], state6_cell (STATE_COLOR pulse), action_arrow (ACTION_COLOR pulse) (3) | code_line[1], state6_cell, action_arrow (3) | All three simultaneously PRIMARY via cross_highlight |
| S3b-P9 (step 2a) | code_line[2], state10_cell, bar_idx2 (rightmost) (3) | code_line[2], state10_cell (pulse), bar_idx2 (growing) (3) | code_line[2], bar_idx2 (settled at 1/3) (2) | |
| S3b-P9 (step 2b) | code_line[2], state7_cell (PENALTY), bar_idx1 (center) (3) | code_line[2], state7_cell (PENALTY pulse), bar_idx1 (growing) (3) | code_line[2], bar_idx1 (settled at 1/3) (2) | |
| S3b-P9 (step 2c) | code_line[2], state2_cell, bar_idx0 (leftmost), Σ=1 annotation (4) | code_line[2], state2_cell (pulse), bar_idx0 (growing) (3) | code_line[2], bar_idx0, Σ=1 annotation (pulse) (3) | Budget exactly 4 at start of step 2c |
| S3b-P10 | norm_eq (LEFT or CENTER), ActionBarChart-inset (SECONDARY), grid (SECONDARY) (3) | norm_eq (PRIMARY), caption (2) | marginal_eq (after morph), caption (2) | CodeStepper FadeOut before P10 begins |
| S4-P11 | Gt_sum (full-screen), header (2) | Gt_sum (writing), header (2) | Gt_sum (complete), caption (2) | FULL SCREEN — §33.2 compliance; ALL S3b elements FadeOut before entry |
| S4-P12 | Gt_sum (LEFT, panel), grid (CENTER, smaller) (2) | active_path_cell, reward_label, accumulator (3) | Gt_sum (LEFT, SECONDARY), accumulator "G₀≈0.951" (VALUE_COLOR) (2) | Grid at SECONDARY during accumulator final reveal |
| S4-P13 | Gt_sum (LEFT, SECONDARY), path (CENTER, SECONDARY), gamma_sweep_chart (RIGHT) (3) | gamma_chart bars growing, γ_token in Gt_sum (Indicate) (2) | gamma_chart (all 3 bars), caption (2) | γ token Indicate = brief PRIMARY pulse then returns to SECONDARY |
| S4-P14 | Gt_sum (LEFT, PRIMARY → morphing), gamma_chart (RIGHT, dims to SECONDARY) (2) | Gt_recursive (morphing, CENTER, font_size=48), gamma_chart (SECONDARY) (2) | Gt_recursive (PRIMARY, large), caption (2) | After morph: grid also dims to SECONDARY |
| S4-P15 | Gt_recursive (LEFT), grid (CENTER, SECONDARY), gamma_chart (RIGHT, SECONDARY), takeaway_caption (4) | Gt_recursive (SECONDARY), takeaway_caption (1) | forward_tease_caption (1) | Final hold: all panels at SECONDARY; captions are the sole PRIMARY |

---

## 4. Element Lifecycle Matrix

| Mobject | Phase IN | Visible during | Phase OUT | Re-enters at |
|---|---|---|---|---|
| Header (title + subtitle) | S1-P1 | S1-P1 through S4-P15 (persistent top-bar) | scene end | n/a (never leaves) |
| FrozenLake grid — native `rgb_array` frame (static full-frame reveal) | S1-P1 | S1-P1 only | S1-P1 end (FadeOut when agent enters) | never |
| FrozenLake grid — per-tile `frozenlake_frame()` VGroup (full size) | S1-P2a | S1-P2a through S2-P5 | S3a-P6 start (FadeOut — clean stage for p equation) | S3a-P7 (re-enters smaller, centered) |
| EpisodeTrail trail-path cells | S1-P2a | S1-P2a through S1-P3 | S1-P3 end (cleared after success) | never |
| Agent sprite `elf_right.png` (Segment 1 traversal) | S1-P2a | S1-P2a, S1-P2b, S1-P3 | S1-P3 end (FadeOut after goal) | S2-P5 (re-instantiated at state 6) |
| Hole-cell PENALTY flash (state 5) — Segment 1 fail 1 | S1-P2a | brief during S1-P2a failure | S1-P2a (auto-FadeOut after 0.5 s flash) | never |
| Hole-cell PENALTY flash (state 5) — Segment 1 fail 2 | S1-P2b | brief during S1-P2b failure | S1-P2b (auto-FadeOut after 0.5 s flash) | never |
| Reward label "1.0" (floating, REWARD_COLOR, state 15) | S1-P3 | S1-P3 goal moment only | S1-P3 end (FadeOut before S2-P4 caption swap) | never |
| State index labels 0–15 (LaggedStart VGroup) | S2-P4 | S2-P4 through S3a-P6 entry | S3a-P6 start (FadeOut with grid — clean stage) | S4-P12 (grid re-enters with labels smaller) |
| Agent sprite `elf_right.png` (at state 6, Segment 2) | S2-P5 | S2-P5 only | S2-P5 end (FadeOut before S3a-P6) | never |
| Dashed curved history arrow (S2-P5 Markov demo) | S2-P5 | S2-P5 only (brief — FadeOut before action arrow) | during S2-P5 (FadeOut after "history irrelevant" beat) | never |
| Action arrow RIGHT at state 6 (ACTION_COLOR, solid) | S2-P5 | S2-P5 through S3a-P7, S3b-P9 step 1 | S3b-P9 step 1 end (dims to SECONDARY after cross_highlight) | never |
| `p_eq_full` MathTex (full form, font_size=48, centered) | S3a-P6 | S3a-P6 (full screen) | S3a-P6 end → repositions in S3a-P7 (NOT FadeOut — transforms to panel) | n/a (morphs in place) |
| `p_eq_full` MathTex (repositioned LEFT, font_size=36, panel) | S3a-P7 | S3a-P7 through S3b-P10 | S3b-P10 end (FadeOut — replaced by norm_eq/marginal_eq morph which also exits) | never |
| FrozenLake grid — per-tile (smaller, CENTER) | S3a-P7 | S3a-P7 through S3b-P10 | S4-P11 start (FadeOut — clean stage for G_t equation) | S4-P12 (re-enters smaller) |
| Outcome branch arrow → state 2 (STATE_COLOR) | S3a-P7 | S3a-P7 through S3b-P8 | S3b-P8 end (FadeOut before CodeStepper migration) | never |
| Outcome branch arrow → state 7 (PENALTY_COLOR) | S3a-P7 | S3a-P7 through S3b-P8 | S3b-P8 end (FadeOut before CodeStepper migration) | never |
| Outcome branch arrow → state 10 (STATE_COLOR) | S3a-P7 | S3a-P7 through S3b-P8 | S3b-P8 end (FadeOut before CodeStepper migration) | never |
| Branch probability labels "1/3, r=0, done=False/True" (×3) | S3a-P7 | S3a-P7 through S3b-P8 | S3b-P8 end (FadeOut) | never |
| `trace_vector` — state 2 cell → `s'` token (transient) | S3a-P7 | ~1.2 s (auto-fade) | auto-FadeOut | never |
| `trace_vector` — state 7 cell → `s'` token (transient) | S3a-P7 | ~1.2 s (auto-fade) | auto-FadeOut | never |
| `trace_vector` — state 10 cell → `s'` token (transient) | S3a-P7 | ~1.2 s (auto-fade) | auto-FadeOut | never |
| `ActionBarChart` (full size, RIGHT, 3 bars) | S3b-P8 | S3b-P8 only (full size) | S3b-P8 end → migrates (scales down) into RIGHT-lower inset | n/a (migrates; does not leave canvas) |
| `ActionBarChart` (inset, RIGHT-lower, smaller) | S3b-P9 (after migration) | S3b-P9 through S3b-P10 | S3b-P10 end (FadeOut before S4-P11 clean stage) | never |
| `CodeStepper` panel (RIGHT-upper) | S3b-P9 | S3b-P9 only | S3b-P9 end (FadeOut) | never |
| `norm_eq` MathTex (normalization form) | S3b-P10 | S3b-P10 (brief, before morph) | morphs into `marginal_eq` (TransformMatchingTex — exits via morph) | never |
| `marginal_eq` MathTex (state-transition form) | S3b-P10 | S3b-P10 (after morph) | S3b-P10 end (FadeOut — complete clean stage for S4-P11) | never |
| `Gt_sum` MathTex (full form, font_size=48, centered) | S4-P11 | S4-P11 (full screen) | S4-P11 end → repositions LEFT in S4-P12 | n/a (morphs in place) |
| `Gt_sum` MathTex (repositioned LEFT, font_size=36, panel) | S4-P12 | S4-P12 through S4-P14 | S4-P14 (morphs into `Gt_recursive`) | n/a |
| FrozenLake grid — per-tile (smaller, CENTER, return path) | S4-P12 | S4-P12 through S4-P15 | S4-P15 end (dims to SECONDARY at S4-P14, stays as context through S4-P15) | n/a |
| Path highlight cells (states 0,4,8,9,10,14,15) | S4-P12 | S4-P12 (reveal one-by-one) | S4-P12 end (dim to SECONDARY trail) | never |
| Floating reward labels "R=0" × 5 + "R=1.0" × 1 | S4-P12 | brief per-step (~1.5 s each) | auto-FadeOut after each step's `assimilation_wait` | never |
| Accumulator panel (RIGHT, ValueTracker-driven label) | S4-P12 | S4-P12 through S4-P13 (migrates inward at S4-P13) | S4-P13 end (FadeOut) | never |
| Gamma sweep `ActionBarChart` (RIGHT, VALUE_COLOR bars, γ labels) | S4-P13 | S4-P13 through S4-P15 | S4-P15 end (dims to SECONDARY at S4-P14, stays as context) | n/a |
| `Gt_recursive` MathTex (font_size=48 after morph, CENTER) | S4-P14 | S4-P14 through S4-P15 | S4-P15 end | n/a |
| Final takeaway caption | S4-P15 | S4-P15 (first 5 s) | S4-P15 (FadeOut → forward tease swap) | never |
| Forward tease caption | S4-P15 | S4-P15 (last ~8 s) | scene end | n/a |

---

## 5. Motion Choreography (per-phase)

### Phase S1-P1 — Grid entry

| Time (rel. to phase start) | Animation | Purpose tag | Manim helper |
|---|---|---|---|
| 0.0 s | `show_header("Reinforcement Learning and the MDP Framework", subtitle="FrozenLake — the agent learns from scratch")` | REVEAL | `BaseConceptScene.show_header()` |
| 1.4 s | FadeIn static Gymnasium `rgb_array` frame centered (native render, wrapped in soft container per §14) | REVEAL | `ImageMobject(tmp.name)` + `FadeIn` |
| 3.4 s | `self.ingestion_wait(2.5)` — hold grid alone | RESOLVE (viewer enters the world before any formula) | `self.ingestion_wait()` |
| 5.9 s | Caption FadeIn: "An agent. A goal. A frozen lake." | REVEAL | `place_caption` + `FadeIn` |
| 7.4 s | `self.wait(2.0)` | — | — |

---

### Phase S1-P2a — Failed attempt 1 (0→1→5)

| Time (rel. to phase start) | Animation | Purpose tag | Manim helper |
|---|---|---|---|
| 0.0 s | FadeOut static frame; FadeIn per-tile `frozenlake_frame()` VGroup (same position, seamless swap) | REFRAME (switch to per-tile for animation capability) | `FadeOut` / `FadeIn` |
| 1.0 s | `FadeIn(elf_right, target_position=state0_center)` | REVEAL | `FadeIn(agent)` |
| 1.5 s | Caption swap: "No map. No hint. The elf goes." | REVEAL | `place_caption` |
| 2.0 s | `EpisodeTrail.step_to(1)` — elf moves 0→1 (`elf_right.png`); step trail highlights state 1 | CONNECT (motion binds to grid state) | `EpisodeTrail.step_to(1)` |
| 3.5 s | `EpisodeTrail.step_to(5)` — elf moves 1→5 (`elf_down.png`); state 5 tile PENALTY_COLOR flash | RESOLVE (the hole ends the episode) | `EpisodeTrail.step_to(5)` + `Indicate(state5_cell, color=PENALTY_COLOR)` |
| 4.5 s | Grid dims to `OPACITY_SECONDARY` for 0.5 s ("dark flash"), then back to `OPACITY_PRIMARY` | DERIVE (episode ends — visual blackout = zero information returned) | `.animate.set_opacity()` sequence |
| 5.0 s | Caption swap: "No map. No hint. Just a zero." | REVEAL | `place_caption` |
| 5.5 s | `self.wait(2.0)` | — | — |

---

### Phase S1-P2b — Failed attempt 2 (0→4→8→9→5)

| Time (rel. to phase start) | Animation | Purpose tag | Manim helper |
|---|---|---|---|
| 0.0 s | `EpisodeTrail.clear_trail()`; agent `smooth_move_to(state0_center)` | REFRAME (reset for second attempt) | `EpisodeTrail.clear_trail()` + `smooth_move_to` |
| 1.2 s | Caption swap: "It tried again." | REVEAL | `place_caption` |
| 1.7 s | `EpisodeTrail.step_to(4)` — 0→4 (`elf_right.png`) | CONNECT | `EpisodeTrail.step_to(4)` |
| 3.0 s | `EpisodeTrail.step_to(8)` — 4→8 (`elf_down.png`) | CONNECT | `EpisodeTrail.step_to(8)` |
| 4.3 s | `EpisodeTrail.step_to(9)` — 8→9 (`elf_right.png`) | CONNECT | `EpisodeTrail.step_to(9)` |
| 5.6 s | `EpisodeTrail.step_to(5)` — 9→5 (`elf_up.png`, slippage upward); PENALTY_COLOR flash on state 5 | RESOLVE (the ice moves it sideways — intuition for stochastic transitions) | `EpisodeTrail.step_to(5)` + `Indicate` |
| 6.5 s | Dark-flash repeat (OPACITY_SECONDARY 0.5 s) | DERIVE | `.animate.set_opacity()` |
| 7.0 s | Caption swap: "Same result. The ice moved it sideways." | REVEAL | `place_caption` |
| 7.5 s | `self.wait(1.5)` | — | — |

---

### Phase S1-P3 — Successful path (0→4→8→9→10→14→15)

| Time (rel. to phase start) | Animation | Purpose tag | Manim helper |
|---|---|---|---|
| 0.0 s | `EpisodeTrail.clear_trail()`; agent `smooth_move_to(state0_center)` | REFRAME | `EpisodeTrail.clear_trail()` |
| 1.2 s | Caption swap: "One more time." | REVEAL | `place_caption` |
| 1.7 s | `EpisodeTrail.step_to(4)` → `step_to(8)` → `step_to(9)` → `step_to(10)` → `step_to(14)` — each at 1.2 s rhythm | CONNECT (path building one step at a time) | `EpisodeTrail.step_to()` × 5 |
| 7.7 s | `EpisodeTrail.step_to(15)` — elf reaches goal; goal cell `Indicate(color=REWARD_COLOR)` sustained pulse | RESOLVE (the sparse reward finally arrives) | `EpisodeTrail.step_to(15)` + `Indicate` |
| 9.0 s | Floating reward label `Text("1.0", color=REWARD_COLOR, font_size=28)` FadeIn above state 15 | REVEAL (the entire signal = one number) | `FadeIn(reward_label)` |
| 10.0 s | Caption swap: "One number. That is all the agent ever receives." | REVEAL | `place_caption` |
| 10.5 s | `self.wait(2.5)` — extended hold (emotional peak) | — | — |

---

### Phase S2-P4 — State indices revealed

| Time (rel. to phase start) | Animation | Purpose tag | Manim helper |
|---|---|---|---|
| 0.0 s | FadeOut(`reward_label`); agent FadeOut; `EpisodeTrail.clear_trail()` | REFRAME (clear episode debris before formalism) | `FadeOut` |
| 1.0 s | Caption swap: "Each cell is a *state*. The agent always knows which one it occupies." | REVEAL | `place_caption` |
| 1.5 s | `LaggedStart([Write(label) for label in state_labels_0_to_15], lag_ratio=0.07)` — labels in `STATE_COLOR`, `font_size=20`, one per cell | REVEAL (coordinate system: S&B §3.1 state set) | `LaggedStart(Write)` |
| 4.5 s | `self.wait(2.0)` after all 16 labels settled | — | — |

---

### Phase S2-P5 — Markov property at state 6

| Time (rel. to phase start) | Animation | Purpose tag | Manim helper |
|---|---|---|---|
| 0.0 s | `FadeIn(elf_right_sprite, target=state6_center)` | REVEAL (agent placed at state 6) | `FadeIn(agent)` |
| 0.8 s | `Create(dashed_curved_arrow)` — multiple arcs entering state 6 from several directions, label "...history..." in GREY_A | REVEAL (the history the Markov property discards) | `Create(dashed_curved_arrow)` |
| 2.0 s | Caption: "The ice does not remember. Whatever path brought the agent here is gone." | REVEAL | `place_caption` |
| 3.5 s | `FadeOut(dashed_curved_arrow)` + `FadeOut(history_label)` | RESOLVE (history is dismissed — the Markov property in action) | `FadeOut` |
| 4.5 s | `Create(action_arrow_right)` — solid ACTION_COLOR arrow pointing RIGHT from state 6, label `"a = RIGHT"` | REVEAL (the only thing that matters with the current state) | `Create(Arrow)` + `Write(label)` |
| 5.5 s | Caption swap: "Only state 6 and the action RIGHT determine what comes next." | REVEAL | `place_caption` |
| 6.5 s | `self.wait(2.0)` | — | — |

---

### Phase S3a-P6 — Full-screen solo reveal of p(s',r|s,a) (§33.2 mandatory sequence)

| Time (rel. to phase start) | Animation | Purpose tag | Manim helper |
|---|---|---|---|
| 0.0 s | `self.play(FadeOut(grid_group), FadeOut(state_labels), FadeOut(elf_sprite), FadeOut(action_arrow), FadeOut(caption))` — ALL canvas elements except header | REFRAME (clear stage — §33.2 step 1) | `FadeOut` group |
| 1.5 s | `self.play(LaggedStart([Write(token) for token in p_eq_full_tokens], lag_ratio=0.12))` — `p_eq_full` centered, `font_size=48`, vertically centered in frame | REVEAL (§33.2 step 2 — equation occupies full frame) | `LaggedStart(Write)` |
| 5.0 s | `self.wait(2.0)` — hold equation alone (§33.2 step 3) | — (mandatory 2.0 s solo hold per §33.2) | `self.wait(2.0)` |
| 7.0 s | `self.ingestion_wait(2.5)` | — | `self.ingestion_wait()` |
| 9.5 s | Caption FadeIn: "The environment's response law. Given where you are and what you do — here is where you land and what you receive." | REVEAL | `place_caption` + `FadeIn` |
| 11.0 s | `self.wait(1.0)` (narration completes) | — | — |

---

### Phase S3a-P7 — Three outcome branches

| Time (rel. to phase start) | Animation | Purpose tag | Manim helper |
|---|---|---|---|
| 0.0 s | Simultaneous: `smooth_move_to(p_eq_full, LEFT_panel_target)` + `p_eq_full.animate.scale(36/48)` + `FadeIn(grid_smaller_center)` in ONE `self.play(...)` (§16, §17) | REFRAME (§33.2 step 4 — equation repositions, grid re-enters) | `smooth_move_to` + `grid FadeIn` combined |
| 1.4 s | `self.ingestion_wait(2.5)` | — | `self.ingestion_wait()` |
| 3.9 s | Caption swap: "Three equally likely outcomes. One action, three destinations." | REVEAL | `place_caption` |
| 4.4 s | `LaggedStart([Create(branch_to_state2), Create(branch_to_state7), Create(branch_to_state10)], lag_ratio=0.3)` — each with probability label "1/3, r=0, done=False/True"; state 7 branch in PENALTY_COLOR, others in STATE_COLOR | REVEAL (three outcomes = the p distribution made geometric) | `LaggedStart(Create)` |
| 6.5 s | `trace_vector(scene, state2_cell, p_eq_full[15])` — state 2 → s' token in equation (STATE_COLOR, ~1.2 s then auto-fade) | CONNECT (geometric s' binds to equation token) | `trace_vector()` |
| 8.0 s | `trace_vector(scene, state7_cell, p_eq_full[15])` — state 7 → s' token (PENALTY_COLOR variant) | CONNECT | `trace_vector()` |
| 9.5 s | `trace_vector(scene, state10_cell, p_eq_full[15])` — state 10 → s' token (STATE_COLOR) | CONNECT | `trace_vector()` |
| 11.0 s | `self.wait(2.0)` + `self.ingestion_wait(2.5)` | — | — |

---

### Phase S3b-P8 — ActionBarChart three bars at 1/3 each

| Time (rel. to phase start) | Animation | Purpose tag | Manim helper |
|---|---|---|---|
| 0.0 s | `FadeIn(ActionBarChart)` at RIGHT panel position (3 bars, sorted: bar_idx=0→state2, bar_idx=1→state7, bar_idx=2→state10, all POLICY_COLOR, labels STATE_COLOR) | REVEAL (the probability distribution becomes a bar chart) | `ActionBarChart` + `FadeIn` |
| 1.5 s | Bar height animations from 0 → 1/3 via `ValueTracker` + `always_redraw`, `LaggedStart` per bar | DERIVE (each bar's height IS the probability — p(s'|6,RIGHT)) | `ValueTracker` + `always_redraw` + `LaggedStart` |
| 3.5 s | `Indicate(state7_bar_label, color=PENALTY_COLOR)` — state 7 label pulses to PENALTY_COLOR (it's a hole) | CONNECT (links chart to semantic meaning of hole) | `Indicate` |
| 4.5 s | FadeIn Σ=1 annotation above bars (REWARD_COLOR, font_size=22) | REVEAL (normalization is satisfied) | `FadeIn(sigma_annotation)` |
| 5.5 s | Caption swap: "Each bar is how likely the agent actually ends up in that cell. Intention and outcome are two different things." | REVEAL | `place_caption` |
| 6.0 s | `self.wait(1.5)` + `self.ingestion_wait(2.5)` | — | — |

---

### Phase S3b-P9 — CodeStepper: env.unwrapped.P[6][2]

| Time (rel. to phase start) | Animation | Purpose tag | Manim helper |
|---|---|---|---|
| 0.0 s | `smooth_move_to(ActionBarChart, RIGHT_lower_inset_target)` + scale down | REFRAME (chart migrates to inset — makes room for CodeStepper) | `smooth_move_to` |
| 1.5 s | `FadeIn(CodeStepper, position=RIGHT_upper)` — 3-line code block, `font_size=20` | REVEAL (code panel enters RIGHT-upper) | `CodeStepper` + `FadeIn` |
| 2.5 s | `self.ingestion_wait(2.5)` | — | `self.ingestion_wait()` |
| 5.0 s | Caption swap: "The same distribution — readable in a single Python call." | REVEAL | `place_caption` |
| 5.5 s | `CodeStepper.step(0)` highlights `env = gym.make(...)` line; `cross_highlight_pair(scene, code.lines[0], grid_frame)` — full grid brief `Indicate` | CONNECT (line 0 = the environment the whole video is about) | `CodeStepper.step()` + `cross_highlight_pair` |
| 7.0 s | `self.wait(1.5)` | — | — |
| 8.5 s | `CodeStepper.step(1)` highlights `for prob, next_state...P[6][2]` line; `cross_highlight_pair(scene, code.lines[1], state6_cell)` — state 6 STATE_COLOR pulse; `cross_highlight_pair(scene, code.lines[1], action_arrow)` — ACTION_COLOR pulse | CONNECT (P[6][2] = state 6, action RIGHT — the indices bind to the grid) | `CodeStepper.step()` + `cross_highlight_pair` ×2 |
| 10.0 s | `self.wait(1.5)` | — | — |
| 11.5 s | Sub-step 2a: `CodeStepper.step(2)` (first iteration, next_state=10); `cross_highlight_pair(scene, code.lines[2], state10_cell)` — state 10 STATE_COLOR pulse; bar at position 2 (rightmost, state 10) grows to 1/3 in inset chart | CONNECT (iteration result 1 → state 10 cell AND rightmost bar; bar_idx=2 per FLAG-3) | `CodeStepper.step()` + `cross_highlight_pair` + `ValueTracker` |
| 13.0 s | `self.wait(1.5)` | — | — |
| 14.5 s | Sub-step 2b: second iteration, next_state=7; `cross_highlight_pair(scene, code.lines[2], state7_cell)` — PENALTY_COLOR pulse; bar at position 1 (center, state 7) grows to 1/3 | CONNECT (iteration result 2 → state 7 hole cell AND center bar; bar_idx=1 per FLAG-3) | `cross_highlight_pair` + `ValueTracker` |
| 16.0 s | `self.wait(1.5)` | — | — |
| 17.5 s | Sub-step 2c: third iteration, next_state=2; `cross_highlight_pair(scene, code.lines[2], state2_cell)` — STATE_COLOR pulse; bar at position 0 (leftmost, state 2) grows to 1/3; `Indicate(sigma_annotation)` — Σ=1 annotation pulses | RESOLVE (all three bars filled; normalization confirmed) | `cross_highlight_pair` + `ValueTracker` + `Indicate` |
| 19.0 s | `self.wait(1.5)` | — | — |

---

### Phase S3b-P10 — Normalization and summation collapse

| Time (rel. to phase start) | Animation | Purpose tag | Manim helper |
|---|---|---|---|
| 0.0 s | `FadeOut(CodeStepper)` | REFRAME (CodeStepper exits — its job is done) | `FadeOut` |
| 1.0 s | Clear LEFT panel: `FadeOut(p_eq_full_panel)`; `FadeIn(norm_eq)` centered (or LEFT-panel position), `font_size=36` — normalization form | REVEAL (the normalization constraint S&B eq. 3.3 p. 48) | `FadeIn(norm_eq)` |
| 2.5 s | Caption swap: "The four-argument form is the complete description. Marginalizing over rewards gives you the state-transition probability." | REVEAL | `place_caption` |
| 3.5 s | `self.wait(2.0)` | — | — |
| 5.5 s | `equation_morph(scene, norm_eq, marginal_eq)` via `TransformMatchingTex` — norm_eq morphs into marginal_eq showing p(s'|s,a) = Σ_r p(s',r|s,a) | DERIVE (summation collapse — M-5 defeat; S&B §3.1 p. 48 eq. 3.4) | `TransformMatchingTex` |
| 7.5 s | `self.ingestion_wait(2.5)` | — | `self.ingestion_wait()` |
| 10.0 s | `FadeOut(marginal_eq)` + `FadeOut(ActionBarChart_inset)` + `FadeOut(grid_smaller)` + `FadeOut(caption)` — complete clean stage for S4-P11 | REFRAME (all S3b elements leave — §33.2 requires clean stage for G_t) | `FadeOut` all remaining |

---

### Phase S4-P11 — Full-screen solo reveal of G_t (§33.2 mandatory sequence)

| Time (rel. to phase start) | Animation | Purpose tag | Manim helper |
|---|---|---|---|
| 0.0 s | Confirm all S3b elements have FadeOut'd (verify canvas = header only) | — | (pre-condition check) |
| 0.5 s | `self.play(LaggedStart([Write(token) for token in Gt_sum_tokens], lag_ratio=0.12))` — `Gt_sum` centered, `font_size=48`, vertically centered in frame | REVEAL (§33.2 step 2 — G_t occupies full frame; S&B eq. 3.8 p. 55) | `LaggedStart(Write)` |
| 5.0 s | `self.wait(2.0)` — mandatory solo hold (§33.2 step 3) | — | `self.wait(2.0)` |
| 7.0 s | `self.ingestion_wait(2.5)` | — | `self.ingestion_wait()` |
| 9.5 s | Caption FadeIn: "The agent's goal is not the next reward. It is the sum of all future rewards — weighted by distance." | REVEAL | `place_caption` |
| 11.0 s | `self.wait(1.0)` | — | — |

---

### Phase S4-P12 — Term-by-term return computation

| Time (rel. to phase start) | Animation | Purpose tag | Manim helper |
|---|---|---|---|
| 0.0 s | Simultaneous: `smooth_move_to(Gt_sum, LEFT_panel_target)` + `Gt_sum.animate.scale(36/48)` + `FadeIn(grid_smaller_center)` + `FadeIn(accumulator_panel_RIGHT)` in ONE `self.play(...)` | REFRAME (§33.2 step 4 — equation moves LEFT, grid and accumulator enter) | combined `self.play(...)` |
| 1.4 s | `self.ingestion_wait(2.5)` | — | `self.ingestion_wait()` |
| 3.9 s | Caption: "Five steps of nothing. Then, finally — a reward five steps away is still worth 95 cents on the dollar." | REVEAL | `place_caption` |
| 4.4 s | Path step 1: `EpisodeTrail.step_to(4)` — cell 0 highlights; floating "R=0" label (grey); accumulator: "G₀ = 0"; `trace_vector(scene, state0_cell, Gt_sum[2])` → `R_{t+1}` token (REWARD_COLOR) | CONNECT (path cell binds to the R_{t+1} term; return stays 0) | `EpisodeTrail.step_to()` + `trace_vector` |
| 5.9 s | `self.wait(1.5)` | — | — |
| 7.4 s | Path step 2: `step_to(8)` — cell 4; "R=0"; accumulator unchanged | CONNECT | `EpisodeTrail.step_to(8)` + floating label |
| 8.9 s | `self.wait(1.5)` | — | — |
| 10.4 s | Path step 3: `step_to(9)` — cell 8; "R=0" | CONNECT | same pattern |
| 11.9 s | `self.wait(1.5)` | — | — |
| 13.4 s | Path step 4: `step_to(10)` — cell 9; "R=0" | CONNECT | same pattern |
| 14.9 s | `self.wait(1.5)` | — | — |
| 16.4 s | Path step 5: `step_to(14)` — cell 10; "R=0" | CONNECT | same pattern |
| 17.9 s | `self.wait(1.5)` | — | — |
| 19.4 s | Path step 6 (GOAL): `step_to(15)` — cell 14; state 15 `Indicate(color=REWARD_COLOR)`; floating "R=1.0" (REWARD_COLOR); accumulator numeric-morph to "G₀ ≈ 0.951" (VALUE_COLOR); `trace_vector(scene, state15_cell, Gt_sum_panel[2])` → `R_{t+k+1}` token | RESOLVE (the deferred reward finally arrives — discounted but not lost) | `EpisodeTrail.step_to(15)` + `ValueTracker` numeric morph + `trace_vector` |
| 21.4 s | `self.ingestion_wait(2.5)` | — | `self.ingestion_wait()` |

---

### Phase S4-P13 — Gamma sweep

| Time (rel. to phase start) | Animation | Purpose tag | Manim helper |
|---|---|---|---|
| 0.0 s | Accumulator panel `smooth_move_to(inset_position)` + `FadeIn(gamma_sweep_chart, position=RIGHT_mid)` — three bars: γ=0.5 (VALUE_COLOR), γ=0.99 (VALUE_COLOR), γ=1.0 (VALUE_COLOR); heights from 0 via `ValueTracker` | REVEAL (the full γ sensitivity landscape) | `FadeIn(gamma_sweep_chart)` + `ValueTracker` |
| 2.0 s | Bar heights animate to final values: γ=0.5 bar → 0.031, γ=0.99 bar → 0.951, γ=1.0 bar → 1.0 | DERIVE (visual proof that patience controls the discount — S&B §3.2 boundary cases) | `ValueTracker` sweep |
| 3.5 s | `Indicate(Gt_sum_panel_gamma_token)` — γ token in LEFT equation pulses `VALUE_COLOR` | CONNECT (equation token binds to the chart it governs — §33.3 focused explanation) | `Indicate` + `cross_highlight_pair(scene, gamma_token, gamma_sweep_chart)` |
| 4.5 s | Caption: "With γ=0.5, a reward five steps away is worth 3 cents. With γ=1.0, it is worth the full dollar." | REVEAL | `place_caption` |
| 6.0 s | `self.wait(2.0)` | — | — |
| 8.0 s | Caption swap: "FrozenLake terminates — so γ=1 is valid here. But for tasks that run forever, γ<1 is required." | REVEAL (M-4 defeat — §5.1 spec) | `place_caption` |
| 9.5 s | `self.ingestion_wait(2.5)` | — | `self.ingestion_wait()` |

---

### Phase S4-P14 — Return recursion derived (DERIVE — NOT Bellman)

| Time (rel. to phase start) | Animation | Purpose tag | Manim helper |
|---|---|---|---|
| 0.0 s | `gamma_sweep_chart.animate.set_opacity(OPACITY_SECONDARY)` + `grid_smaller.animate.set_opacity(OPACITY_SECONDARY)` | REFRAME (dim flanking elements — the derivation needs visual focus) | `.animate.set_opacity()` |
| 1.0 s | `equation_morph(scene, Gt_sum_panel, Gt_recursive, run_time=2.5)` via `TransformMatchingTex` — tail γR_{t+2}+γ²R_{t+3}+⋯ collapses into γG_{t+1}; morph shows intermediate step: `G_t = R_{t+1} + γ(R_{t+2}+γR_{t+3}+⋯)` → `G_t = R_{t+1} + γG_{t+1}` | DERIVE (the return recursion — NOT the Bellman equation; S&B eq. 3.9 p. 55; FLAG-1 compliance) | `TransformMatchingTex` |
| 3.5 s | `Gt_recursive` centers and scales to `font_size=48` via `animate.scale()` | REFRAME (result equation grows to prominence) | `.animate.scale()` |
| 4.5 s | `self.ingestion_wait(2.5)` | — | `self.ingestion_wait()` |
| 7.0 s | Caption: "Factor out γ from the tail, and the entire future collapses into one term. That identity — G_t equals R_{t+1} plus γ times G_{t+1} — is the return recursion." | REVEAL (naming it explicitly: "return recursion" — FLAG-1) | `place_caption` |
| 9.0 s | `self.wait(2.0)` | — | — |
| 11.0 s | Caption swap: "We will see this identity again in the next video." | REVEAL (forward tease planted without crossing V-02 boundary) | `place_caption` |
| 12.5 s | `self.ingestion_wait(2.5)` | — | `self.ingestion_wait()` |

---

### Phase S4-P15 — Hold frame and forward tease

| Time (rel. to phase start) | Animation | Purpose tag | Manim helper |
|---|---|---|---|
| 0.0 s | `Gt_recursive.animate.move_to(LEFT_panel_target)` — recursion repositions LEFT; `grid_smaller.animate.set_opacity(OPACITY_SECONDARY)` (already at SECONDARY — confirm); `gamma_sweep_chart.animate.set_opacity(OPACITY_SECONDARY)` (already at SECONDARY) | REFRAME (final 3-panel layout: all panels individually known — §33.4 allows 3-panel here) | `smooth_move_to` + opacity confirms |
| 1.5 s | FadeIn takeaway caption: "A Markov Decision Process. From any state and action, p tells you where you land and what reward you get. The agent's goal is to maximize G_t — the discounted sum of all future rewards." | REVEAL | `place_caption` + `FadeIn` |
| 3.0 s | All equation/chart/grid panels dim to `OPACITY_SECONDARY`; caption remains PRIMARY | REFRAME (caption is the sole PRIMARY — the summary is the final lesson) | `.animate.set_opacity(OPACITY_SECONDARY)` |
| 5.0 s | `self.wait(5.0)` — hold takeaway alone | — | `self.wait(5.0)` |
| 10.0 s | Caption swap: "Next: we give the agent a *strategy* for choosing actions — and ask what each state is worth under that strategy." | REVEAL (forward tease to V-02 without using "policy" or "value function") | `FadeOut(takeaway_cap)` + `FadeIn(forward_cap)` |
| 11.5 s | `self.wait(8.0)` — final hold per spec §10 pacing note | — | `self.wait(8.0)` |

---

## 6. Camera Shot List

| Phase | Shot | Trigger time (within phase) | Helper | Duration | Purpose |
|---|---|---|---|---|---|
| S1-P2a | `pan_to_follow(self, agent, path=[state0→state1→state5])` | 2.0 s after phase start (agent begins walking) | `pan_to_follow(self, elf_sprite, path)` | continuous through episode | Agent path in top half of grid; keep active step visible without edge-crowding |
| S1-P2a | `zoom_reset(self)` | after hole flash + dark flash complete | `zoom_reset(self)` | 1.4 s | Return to wide for reset and caption |
| S1-P2b | `pan_to_follow(self, agent, path=[0→4→8→9→5])` | 1.7 s after phase start | `pan_to_follow(self, elf_sprite, path)` | continuous through episode | Path crosses center column; pan keeps elf visible |
| S1-P2b | `zoom_reset(self)` | after second hole flash | `zoom_reset(self)` | 1.4 s | Return to wide for caption |
| S1-P3 | `pan_to_follow(self, agent, path=[0→4→8→9→10→14→15])` | 1.7 s after phase start | `pan_to_follow(self, elf_sprite, path)` | continuous through success path | 7-step path traverses most of the grid; pan keeps destination visible |
| S1-P3 | `zoom_reset(self)` | after goal cell pulse settles | `zoom_reset(self)` | 1.4 s | Return to wide for reward label reveal |
| S3b-P9 | `zoom_reset(self)` | at start of S3b-P9 (simultaneous with CodeStepper FadeIn) | `zoom_reset(self)` | 1.4 s | Ensure full-width frame is visible for 3-panel code+grid+chart layout |

> **Zoom-omission justification (S3a-P6, S3a-P7 boundary, S4-P11, S4-P14):**
> The four `zoom_to` shots originally specified for the p-equation solo (S3a-P6),
> the G_t solo (S4-P11), and the return recursion (S4-P14) — plus their paired
> `zoom_reset` calls — have been **removed** from the implemented scene.
> Rationale: at 480p15 and `font_size=48`, both equations fill ≥40% of frame width
> after `scale_to_fit_width(config.frame_width × 0.9)` is applied (STYLE_BIBLE §3).
> A `zoom_to(scale=0.55)` at this size causes horizontal clipping (the equation
> extends beyond both frame edges), which is a worse user experience than a
> slightly-smaller-but-fully-visible equation. The `scale_to_fit_width` guarantee
> satisfies STYLE_BIBLE §33.2's legibility requirement without a camera zoom.
> The three episode-traversal `pan_to_follow` + `zoom_reset` shots in Segment 1
> and the single S3b-P9 `zoom_reset` are retained.

**Camera move count:** 7 shots across ~21 min ≈ 3.3 shots per 10 min. Well within the ≤6 per 10 min guideline. (Reduced from 13 by removing 6 zoom shots per zoom-omission justification above.)

---

## 7. Sprite-Math Binding Matrix

| Phase | Sprite action | Equation token(s) that highlight | Code line that highlights | Helper |
|---|---|---|---|---|
| S1-P2a | Agent moves 0→1 via `EpisodeTrail.step_to(1)` | None — no equation on screen yet (pre-formalism Segment 1) | None | `EpisodeTrail.step_to()` (no binding required — §26 "Optional for purely contextual sprite motion") |
| S1-P2a | Agent falls into hole at state 5 | None | None | `Indicate(hole_cell)` — visual only |
| S1-P2b | Agent moves 0→4→8→9→5 (slippage) | None — no equation on screen yet | None | `EpisodeTrail.step_to()` (optional; contextual) |
| S1-P3 | Agent walks to goal at state 15 | None | None | `EpisodeTrail.step_to(15)` + `Indicate(goal_cell)` |
| S2-P5 | Agent sprite placed at state 6; action arrow created | Equation token: none on screen yet; binding target is the `a = RIGHT` label adjacent to action arrow | None | `SpriteActionBinding(sprite=elf_sprite, action_arrow=action_arrow_right, eq_tokens=[], code_line=None)` — binds sprite position to action label |
| S3a-P7 | Three outcome branches from state 6 animate | `p_eq_full[2]` (s'), `p_eq_full[15]` (s' expanded), `p_eq_full[6]` (s), `p_eq_full[8]` (a) — tokens flash in sequence as each branch traces | None | `SpriteActionBinding` + `trace_vector` per branch (see §8) |
| S3b-P9 (step 1) | State 6 cell highlights + action arrow pulses | `p_eq_full[6]` (s=6 in equation, STATE_COLOR) + `p_eq_full[8]` (a=RIGHT, ACTION_COLOR) | `code.lines[1]` (`P[6][2]` line) | `cross_highlight_pair(scene, code.lines[1], state6_cell)` + `cross_highlight_pair(scene, code.lines[1], action_arrow)` |
| S3b-P9 (step 2a) | State 10 cell highlights (next_state=10 first iteration) | `p_eq_full[2]` (s' token) flash STATE_COLOR | `code.lines[2]` | `cross_highlight_pair(scene, code.lines[2], state10_cell)` — bar_idx=2 (rightmost) grows simultaneously |
| S3b-P9 (step 2b) | State 7 cell highlights (next_state=7 second iteration) | `p_eq_full[2]` (s' token) flash PENALTY_COLOR | `code.lines[2]` | `cross_highlight_pair(scene, code.lines[2], state7_cell)` — bar_idx=1 (center) grows |
| S3b-P9 (step 2c) | State 2 cell highlights (next_state=2 third iteration) | `p_eq_full[2]` (s' token) flash STATE_COLOR | `code.lines[2]` | `cross_highlight_pair(scene, code.lines[2], state2_cell)` — bar_idx=0 (leftmost) grows + Σ=1 pulses |
| S4-P12 (step 1–5) | Path cell highlights one-by-one (states 0,4,8,9,10,14) | `Gt_sum_panel[2]` (`R_{t+1}` token) — dims (no reward) or stays at SECONDARY | None | `EpisodeTrail.step_to()` + floating R=0 label; `trace_vector` from each cell to `R_{t+k+1}` token optional for first step only |
| S4-P12 (step 6, goal) | State 15 highlights (REWARD_COLOR pulse) + accumulator morphs to ≈0.951 | `Gt_sum_panel[14]` (`R_{t+k+1}` token) flashes REWARD_COLOR; `Gt_sum_panel[13]` (`γ^k` = `γ^5`) flashes VALUE_COLOR | None | `SpriteActionBinding(sprite=path_cell_15, action=goal_reached, eq_tokens=[Gt_sum_panel[14], Gt_sum_panel[13]])` + `trace_vector(scene, state15_cell, Gt_sum_panel[14])` |
| S4-P13 | Gamma sweep bars animate to heights 0.031, 0.951, 1.0 | `Gt_sum_panel[4]` (γ token) — `Indicate` pulse VALUE_COLOR | None | `cross_highlight_pair(scene, gamma_token, gamma_sweep_chart)` — `γ` token binds to entire chart |
| S4-P14 | `Gt_sum` morphs to `Gt_recursive` via `TransformMatchingTex` | `Gt_recursive[0]` (G_t), `Gt_recursive[2]` (R_{t+1}), `Gt_recursive[4]` (γ), `Gt_recursive[5]` (G_{t+1}) — all PRIMARY after morph | None | `equation_morph` / `TransformMatchingTex` — tokens highlight in VALUE_COLOR and REWARD_COLOR per color bindings |

---

## 8. trace_vector Source-Target Pairs

| Phase | Equation token (MathTex index) | Token meaning | Source geometry on canvas | Color | Trigger | Helper |
|---|---|---|---|---|---|---|
| S3a-P7 | `p_eq_full[15]` | s' (first instance, expanded form) | State 2 cell (outcome branch 1, ice) | STATE_COLOR | After branch_to_state2 `Create` completes | `trace_vector(scene, state2_cell, p_eq_full[15])` |
| S3a-P7 | `p_eq_full[15]` | s' (re-triggered, same token) | State 7 cell (outcome branch 2, hole) | PENALTY_COLOR | After branch_to_state7 `Create` completes | `trace_vector(scene, state7_cell, p_eq_full[15])` |
| S3a-P7 | `p_eq_full[15]` | s' (re-triggered, same token) | State 10 cell (outcome branch 3, ice) | STATE_COLOR | After branch_to_state10 `Create` completes | `trace_vector(scene, state10_cell, p_eq_full[15])` |
| S3a-P7 | `p_eq_full[18]` | r (reward token in expanded form) | Branch probability labels "r=0" on outcome branches | REWARD_COLOR | After all three branches visible, one trace total | `trace_vector(scene, branch_label_r, p_eq_full[18])` |
| S3a-P7 | `p_eq_full[6]` | s (current state, LHS) | State 6 cell (agent position) | STATE_COLOR | Before outcome branches animate (state 6 is the source) | `trace_vector(scene, state6_cell, p_eq_full[6])` |
| S3a-P7 | `p_eq_full[8]` | a (action, LHS) | Action arrow RIGHT at state 6 (ACTION_COLOR) | ACTION_COLOR | Simultaneous with s trace | `trace_vector(scene, action_arrow, p_eq_full[8])` |
| S4-P12 | `Gt_sum_panel[2]` | R_{t+1} (first reward term) | State 0 path cell (first step, R=0) | REWARD_COLOR | Phase start — first path step | `trace_vector(scene, state0_cell, Gt_sum_panel[2])` |
| S4-P12 | `Gt_sum_panel[14]` | R_{t+k+1} (general term, Σ form) | State 15 goal cell (final R=1.0) | REWARD_COLOR | Step 6 goal arrival | `trace_vector(scene, state15_cell, Gt_sum_panel[14])` |
| S4-P12 | `Gt_sum_panel[13]` | γ^k (discount weight in Σ form) | Accumulator label "γ⁵ × 1.0" on RIGHT panel | VALUE_COLOR | Simultaneous with goal trace | `trace_vector(scene, accumulator_label, Gt_sum_panel[13])` |
| S4-P13 | `Gt_sum_panel[4]` | γ (discount factor token, LHS expansion) | Gamma sweep chart (the γ axis label) | VALUE_COLOR | When gamma sweep chart appears | `trace_vector(scene, gamma_chart_title, Gt_sum_panel[4])` |

---

## 9. Hand-off Notes for Manim Expert

### FLAG-1 — Return recursion naming (CRITICAL)

The morph in S4-P14 produces `G_t = R_{t+1} + γG_{t+1}`. This equation is named
**"the return recursion"** everywhere — in captions, in the `place_caption` text,
and in any `Text` or `Tex` label adjacent to it. The word "Bellman" must **not**
appear anywhere in this scene file. If you are tempted to write "Bellman" as a
label or comment: stop. The Bellman equation is introduced in V-02. The RL Expert
will reject a rendered video that uses "Bellman" in connection with this identity.
Tag the `equation_morph` call with a comment: `# DERIVE (return recursion — NOT Bellman)`.

### FLAG-2 — CodeStepper scope (CRITICAL)

`CodeStepper` appears **only in Phase S3b-P9**. No other phase uses `CodeStepper`.
Specifically: Segment 1 (S1-P1 through S1-P3), Segment 2 (S2-P4 through S2-P5),
and Segment 3a (S3a-P6 through S3a-P7) must have **zero code panels**.
The Element Lifecycle Matrix above reflects this: CodeStepper Phase IN = S3b-P9,
Phase OUT = end of S3b-P9.

### FLAG-3 — ActionBarChart bar ordering (CRITICAL)

`ActionBarChart` bars in S3b-P8 and S3b-P9 are sorted **left-to-right by
next-state index**:
- **bar_idx = 0** (leftmost): state 2 (ice, STATE_COLOR)
- **bar_idx = 1** (center): state 7 (hole, PENALTY_COLOR)
- **bar_idx = 2** (rightmost): state 10 (ice, STATE_COLOR)

Gymnasium's `env.unwrapped.P[6][2]` tuple order is `(10, 7, 2)` — that is,
next_state=10 comes **first** in the Python loop iteration. The cross_highlight
must map:
- Sub-step 2a (first loop iteration, next_state=10) → highlights state 10 cell
  AND `bar_idx=2` (rightmost bar)
- Sub-step 2b (second iteration, next_state=7) → highlights state 7 cell AND
  `bar_idx=1` (center bar)
- Sub-step 2c (third iteration, next_state=2) → highlights state 2 cell AND
  `bar_idx=0` (leftmost bar)

Do NOT insert bars in iteration order (10→7→2 left-to-right). The viewer reads
the chart as a probability distribution sorted by state index; the code iterates
in a different order.

### FLAG-4 — G₀ ≈ 0.951 requires Technical Validator confirmation

The value (0.99)⁵ × 1.0 = 0.9509803... displayed as "≈ 0.951" in:
- The accumulator panel (S4-P12 final step)
- The gamma sweep chart γ=0.99 bar height (S4-P13)
- Any `MathTex` or `Text` label referencing this value

**Must use "≈ 0.951" not "= 0.951"** in all on-screen displays. The Technical
Validator must confirm this value via live `python -c "print(0.99**5 * 1.0)"` before
any Manim code rendering. Do not hardcode 0.9509803 in scene code — use a
`compute_return(gamma=0.99, rewards=[0,0,0,0,0,1.0])` helper function so the
value is live-computed. The displayed label rounds to 3 decimal places: f"{G0:.3f}".

### Narration describes the screen — rewrite rule

Any narration line that describes the animation rather than explaining its
mathematical meaning must be rewritten before the Voice & BGM Agent processes it.
The Manim Expert should flag any caption passed to `place_caption()` that follows
the banned pattern (§29.2 STYLE_BIBLE):

| If you see this caption text... | Rewrite to explain meaning, not visuals |
|---|---|
| "A bar chart appears on the right." | "Each bar is how likely the agent ends up in that cell." |
| "The elf moves to state 5." | "Choosing a direction and arriving there are two completely different events." |
| "The equation fades in." | (no caption needed — the equation speaks for itself) |
| "Three branches are shown." | "The probability splits three ways — the ice doesn't honor the agent's intention." |

### §33.4 — 3-panel layout permitted only in specific phases

The 3-panel layout (equation LEFT + grid CENTER + chart/code RIGHT) is only
permitted in phases where all three panels are individually familiar to the viewer:
- S3a-P7: grid familiar (from S1-S2), equation introduced this phase (ALLOWED — §33.4 permits equation repositioning after solo reveal)
- S3b-P8 through S3b-P10: all three panels individually introduced (ALLOWED — synthesis phase)
- S4-P12 through S4-P15: equation familiar (from S4-P11 solo reveal), grid familiar (from S1-S3), chart familiar (from S3b) (ALLOWED — synthesis phase)

No phase may introduce a new element into a 3-panel layout (§33.4 ban).

### Simultaneous repositions (§17 compliance)

S3a-P7 and S4-P12 both require a simultaneous multi-element reposition:
- In S3a-P7: `smooth_move_to(p_eq_full, LEFT_target)` + `p_eq_full.animate.scale(...)` + `FadeIn(grid_smaller)` — these must share ONE `self.play(...)` call so they are eased together.
- In S4-P12: same pattern for `Gt_sum` + `FadeIn(grid_smaller)` + `FadeIn(accumulator_panel)`.

Never split these into sequential `self.play(...)` calls — the simultaneous
timing is required by §16.1 and §17.

### Asset verification before any code

Run the asset verification command from `rl_mdp_core_specs.md §8.1` before
writing a single line of scene code. If any of the 8 PNG sprites is missing:
stop, report `MISSING_ASSETS` to Producer, do not substitute colored rectangles.
The `colored-rectangle fallback = BANNED` rule (QA G57) is enforced.

### CodeStepper color bindings in code panel

In the CodeStepper code panel, apply these syntax highlight overrides:
- `"FrozenLake-v1"` string → white (string literal)
- `env` → white (variable)
- `prob` → POLICY_COLOR (it is a probability value)
- `next_state` → STATE_COLOR
- `reward` → REWARD_COLOR
- `done` → PENALTY_COLOR when its value is True, white otherwise
- `6` (in `P[6]`) → STATE_COLOR (state index)
- `2` (in `P[6][2]`) → ACTION_COLOR (action index RIGHT = 2)

### Γ=0 boundary case

The γ=0 boundary case (pure myopia: G_t = R_{t+1} only) is part of the
discount boundary narration at S4-P13 but does not require a fourth bar in
the gamma sweep chart. The narration line covers it verbally; the chart
shows only three bars (γ=0.5, γ=0.99, γ=1.0). This is consistent with
the spec §4.4 gamma animation requirement.

### Phase OUT discipline reminder

Every `FadeOut` listed in the Element Lifecycle Matrix is mandatory. The
canonical failure mode for this lesson is stale elements from Segments 1–3
persisting into Segment 4. The staleness threshold is 8 s (§23 STYLE_BIBLE).
The S4-P11 entry explicitly requires ALL S3b elements to FadeOut before the
G_t equation appears. Do not "forget" the equation panel or chart inset.
