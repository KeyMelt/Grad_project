# Choreography — policies_values_bellman

**plan.md reference:** `manim_service/concept_videos/policies_values_bellman_plan.md`
**specs.md reference:** `manim_service/concept_videos/policies_values_bellman_specs.md`
**Visual Director:** visual-director (skill)
**Date:** 2026-05-27
**Series position:** V-02 of restructured RL curriculum (direct sequel to V-01 `rl_mdp_core`)
**Manim class:** `PoliciesValuesBellmanConcept`
**Scene file (target):** `manim_service/concept_videos/policies_values_bellman_concept.py`

---

## 1. Scientific Rigor

This video makes precisely four classes of claim, each grounded by on-screen evidence:

1. **Policy is a probability distribution** ($\pi(a\mid s)$, normalized per state) — claim is shown verbatim full-frame in S2-P3 (S&B eq. p. 58) and evidenced visually in S2-P4 (two arrow-grids: deterministic "all RIGHT" and equiprobable random) plus S2-P5 (the $\tfrac14+\tfrac14+\tfrac14+\tfrac14=1$ annotation). **Scope qualifier:** all claims apply specifically to **FrozenLake-v1 4×4 with `is_slippery=True`, $\gamma=0.99$, equiprobable random policy $\pi(a\mid s)=1/4$.** This qualifier is explicit in the S3-P7 colorbar caption (`"v_π under π=1/4, γ=0.99, FrozenLake-v1 slippery"`) and in the S5 lower-right policy thumbnail held at OPACITY_BACKGROUND throughout the derivation.

2. **State values are expected future returns, not immediate rewards** — claim materializes in S3-P6 ($v_\pi(s) \doteq \mathbb{E}_\pi[G_t\mid S_t=s]$, S&B eq. (3.12) p. 58) and is evidenced numerically in S3-P7 (heatmap with $v_\pi(0)\approx 0.014$, $v_\pi(14)\approx 0.434$, $v_\pi(\text{holes})=v_\pi(\text{goal})=0$). The misconception defuse (S3-P8/P9) is itself evidence: state 14's reward is 0 but value 0.44, and the goal's reward is +1 yet value is 0. Every numeric label carries the `# NUMERIC_CLAIM` tag for Technical Validator refinement at $\theta=10^{-10}$.

3. **The Bellman expectation equation has TWO sums (one over actions, one over $(s', r)$)** — claim is staged geometrically before algebraically: the backup diagram in S5-P13 makes the two-level branching physically separate (state → 4 actions → 3 transitions per action) BEFORE any algebra appears, then the five-step derivation (S5-P14 through S5-P18) puts coordinates on each level. Evidence is the explicit `POLICY_COLOR` action-branch labels (outer sum) vs the `CODE_ACCENT` $p$-labels (inner sum) on the diagram. The two sums maintain visually distinct color identity throughout — they never collapse to $\sum_{a, s', r}$ in any frame.

4. **The Bellman equation is an EQUALITY (fixed-point identity), not an assignment rule** — claim is enforced by the numerical consistency check in S6-P20 (LHS = $v_\pi(6)\approx 0.039$ from the heatmap; RHS = $\tfrac14\sum_a\sum_{s',r} p[\cdot]\approx 0.039$ computed term-by-term; both equal within $\theta=10^{-10}$). The CodeStepper at S7 evaluates the RHS with $v_\text{prev}=0$ and gets $0.000000$ — *not* a contradiction but a deliberate V-03 hand-off: with the converged $v_\pi$ the RHS would equal 0.039; with a zero guess it returns 0; the gap is the algorithm waiting for V-03.

**Misleading claims actively avoided:** (a) we never call the equation just "Bellman's equation" — always "the Bellman expectation equation for $v_\pi$" (S&B eq. 3.14, distinguishes from the optimality form V-05 will introduce); (b) we never use "argmax," "value iteration," "policy iteration," "optimal," or "best policy" — all V-04/V-05 territory; (c) we never display $V[s] \leftarrow \ldots$ pseudocode during V-02 — that is V-03's contract. The S8-P25 morph $=\to\leftarrow$ holds for ≤ 1.5 s and reverts to the equality form, planting the V-03 seed without committing to V-03 algebra.

---

## 2. Pedagogical Strategy

**Primary pattern:** **Top-down decomposition** (the boxed Bellman equation is the destination; we peel the geometry onto each sub-piece, then assemble symbolically). Layered with a **Concrete-to-abstract** sub-pattern in Segments 2–3 (arrow-grid before $\pi$ definition is shrunk to a chip; heatmap before $v_\pi$ definition migrates to LEFT panel) and a **Worked example** anchor (state 6) throughout Segments 4–7.

**Why this pattern suits this lesson:** the Bellman expectation equation is the algebraic destination of every value-based RL method in the series. A bottom-up assembly would force the viewer to trust each algebraic step before it lands on geometry — exactly the failure mode that produces "stale demo" videos. By making the backup-diagram tree the **literal physical referent of the two sums BEFORE the algebra arrives**, we ensure each derivation step in S5-P14 to S5-P18 has a visible geometric correlate. The viewer is never holding an algebraic term whose meaning has not yet landed on the canvas.

**Misconception defeat map (every M-1..M-6 from specs §5.1 has a specific phase + visual cure):**

| Misconception | Defeat strategy (visual realization) | Defeating phase(s) |
|---|---|---|
| **M-1** "A policy is a function from states to actions." | **Contrast pair** sub-pattern at S2-P4 — deterministic "all RIGHT" (Policy A, LEFT) and equiprobable random (Policy B, RIGHT) coexist on the same canvas. Both are valid; both are policies. The viewer cannot maintain "function from state to action" framing while looking at four arrows per cell. Reinforced at S2-P5 by the normalization annotation: $\pi$ is *any* row-stochastic table. | S2-P3, S2-P4, S2-P5 |
| **M-2** "The value of a state is the reward it gives." | **Failure case + recovery** — state 14 spotlight in S3-P8 explicitly shows reward 0, value 0.44. Then S3-P9 escalates to the goal cell: reward +1 (green), value 0 (yellow), both pulsing simultaneously on the same cell. The two colors held side by side are the literal visual cure — they cannot be the same color in the same frame. | S3-P7, S3-P8, S3-P9 |
| **M-3** "The Bellman equation has one sum (over next states)." | **Top-down decomposition** anchored on the backup diagram (S5-P13): two physically distinct levels of branching — 4 action children in `POLICY_COLOR`/`ACTION_COLOR`, then 3 (s', r) leaves under each action in `STATE_COLOR`/`CODE_ACCENT`/`REWARD_COLOR`. The geometry pre-commits the two sums; the algebra in S5-P16 (outer) and S5-P17 (inner) names them. They never appear collapsed to $\sum_{a,s',r}$ in any frame. | S5-P13, S5-P16, S5-P17 |
| **M-4** "Deterministic policies don't need the sum over actions." | **Worked example** — the equiprobable random policy is adopted from S2-P5 onward as THE working policy for all of Segments 3–7. Every $\pi(a\mid s)=1/4$ term in the derivation is non-trivial; the viewer sees the four-way action sum computed term-by-term in S6-P20 and S7-P22. The deterministic Policy A from S2-P4 is FadedOut at S3-P6 and never returns. | S2-P5, S3+ (working-policy adoption) |
| **M-5** "$v_\pi$ and $q_\pi$ are unrelated." | **Bottom-up assembly** at S4-P11 → S4-P12 — four $q$-bars on the edges of cell 14, then the linking identity $v_\pi(14)=\tfrac14\sum_a q_\pi(14,a)$ appears with a bracket-arrow visually pointing from the four bars to the single $v$-value in the heatmap cell. The four-into-one motion is the literal arithmetic of the identity. | S4-P11, S4-P12 |
| **M-6** "The Bellman equation tells you how to update v." | **Failure case + recovery** at S6-P20 (LHS=RHS at state 6 — the equation is *checked*, not used) + S7-P23 (code with $v_\text{prev}=0$ produces 0.000000, NOT 0.039 — the equation is satisfied only at the true $v_\pi$). Then S8-P25 morphs `=` to `←` for ≤ 1.5 s and **reverts** — explicitly *not* committing the assignment form to memory. The viewer leaves with the equality as their canonical form; V-03 will earn the assignment. | S6-P20, S7-P23, S8-P25 |

---

## 3. Cognitive Load Budget

≤ 4 primary mobjects at any rendered frame (STYLE_BIBLE §33.1, Principle 5). Grouped subordinate elements (e.g., the four directional arrows on a single cell in S2-P4) count as one mobject when at the same opacity level. A MathTex equation counts as one mobject unless tokens are split across opacity tiers.

| Phase | Primary at phase START | Primary at phase MID | Primary at phase END | Notes |
|---|---|---|---|---|
| S1-P1 | Header | Recap caption stack (RIGHT, 3 lines = 1 group) + grid thumbnail (CENTER) | Recap caption stack + grid thumbnail | 2 primary. Header dims to BACKGROUND after first 0.5 s. |
| S1-P2 | Grid thumbnail (CENTER, dimmed→SECONDARY mid-phase) + recursion eq (LEFT, growing) | $G_t$ recursion panel (LEFT) + "today we cook" caption (RIGHT) | Recursion panel (LEFT) + caption (RIGHT) | 2 primary. |
| S2-P3 | $\pi(a\mid s)$ definition (CENTER, full-frame, font 48) | Same — staggered_write completes mid-phase | $\pi$ definition (full hold) | **1 primary** (full-frame solo, STYLE_BIBLE §33.2). |
| S2-P4 | $\pi$ chip (top, SECONDARY) | Policy A arrow-grid (LEFT) + Policy B arrow-grid (RIGHT) + "Two valid policies" caption (CENTER) | Policy A grid + Policy B grid + caption | 3 primary (deliberate dual-PRIMARY for contrast — Principle 1 REVEAL + Principle 5 budget honored: 3 ≤ 4). |
| S2-P5 | Both policy grids (smaller, flanking SECONDARY) | Normalization eq $\sum_a \pi(a\mid s)=\tfrac14+\tfrac14+\tfrac14+\tfrac14=1$ (CENTER) + cell-6 spotlights on both grids (one Group) | Normalization eq + spotlights | 2 primary. |
| S3-P6 | $v_\pi(s)\doteq\mathbb{E}_\pi[G_t\mid S_t=s]$ (CENTER, full-frame, font 48) | Same | Same | **1 primary** (§33.2 solo). |
| S3-P7 | $v_\pi$ eq migrating LEFT (SECONDARY mid-migration) | Heatmap (CENTER, cells fading in) + colorbar (RIGHT, SECONDARY) | Heatmap (CENTER, fully revealed) + $v_\pi$ panel (LEFT, SECONDARY) | 1 primary at phase end (heatmap dominates). |
| S3-P8 | Heatmap (CENTER, SECONDARY) | State 14 cell (PRIMARY, spotlit) + M-2 caption (RIGHT, PRIMARY) | State 14 spotlight + caption | 2 primary. Rest of heatmap dimmed to SECONDARY. |
| S3-P9 | State 14 (dims back to SECONDARY) | State 15 goal cell (PRIMARY): green `+1.0` reward marker (above) + yellow `v_π(15)=0` label (inside) — **cross-highlight pair** counts as one PRIMARY mobject per STYLE_BIBLE §33.1 + terminal caption (RIGHT, PRIMARY) | Same | 2 primary (the green+yellow co-display is one cross-highlight pair). |
| S4-P10 | $q_\pi(s,a)$ definition (CENTER, full-frame, font 48) | Same | Same | **1 primary** (§33.2 solo). Heatmap held at BACKGROUND lower-CENTER. |
| S4-P11 | $v_\pi$ eq (LEFT, SECONDARY) + $q_\pi$ eq (RIGHT, SECONDARY) | State 14 inset (CENTER) with 4 q-bars (one Group) | State 14 inset with 4 q-bars + bar labels | 1 primary (the 4-bar inset). |
| S4-P12 | State 14 inset (SECONDARY) + $q_\pi$ eq (FadeOut) | Linking identity (LEFT, PRIMARY) + bracket-arrow (CENTER, PRIMARY) | Linking identity + bracket-arrow + state-14 cell label `0.434` (CENTER, dimmed) | 2 primary. |
| S5-P13 | (clean canvas — all S4 elements FadeOut) | Backup diagram (CENTER, full-frame, growing level by level) | Backup diagram (full reveal) + policy thumbnail (lower-right, BACKGROUND) | **1 primary** (the diagram is one composite mobject). |
| S5-P14 | Backup diagram (CENTER, SECONDARY after step 1 morph begins) | Step-1 equation $v_\pi(s)\doteq\mathbb{E}_\pi[G_t\mid S_t=s]$ (LEFT, PRIMARY) + root node lit (CENTER, PRIMARY) | Step-1 eq + lit root | 2 primary. |
| S5-P15 | Step-1 eq (LEFT, SECONDARY) + diagram (CENTER) | Step-2 morph (LEFT, PRIMARY) + $R_{t+1}$ edge label + $G_{t+1}$ subtree brace (CENTER, PRIMARY, one Group) | Step-2 eq + edge+brace labels | 2 primary. |
| S5-P16 | Step-2 eq (LEFT, SECONDARY) | Step-3 morph with $\sum_a \pi(a\mid s)$ new tokens (LEFT, PRIMARY) + 4 action nodes pulsing `POLICY_COLOR→ACTION_COLOR` (CENTER, PRIMARY, one Group) | Step-3 eq + pulsing action nodes | 2 primary. |
| S5-P17 | Step-3 eq (LEFT, SECONDARY) | Step-4 morph with $\sum_{s',r}p(s',r\mid s,a)$ new tokens (LEFT, PRIMARY) + 3 transition leaves under RIGHT pulsing `CODE_ACCENT` + `REWARD_COLOR` (CENTER, PRIMARY, one Group) | Step-4 eq + pulsing leaves | 2 primary. |
| S5-P18 | Step-4 eq (LEFT, SECONDARY) | Step-5 morph with $v_\pi(s')$ token replacing $\mathbb{E}_\pi[G_{t+1}\mid S_{t+1}=s']$ (LEFT, PRIMARY) + leaves relabeled $v_\pi(2), v_\pi(7)=0, v_\pi(10)$ (CENTER, PRIMARY) | Step-5 eq + relabeled leaves | 2 primary. |
| S5-P19 | (FadeOut diagram + step-5 panel) | Boxed Bellman equation (CENTER, full-frame, font 48, Rectangle border) | Same | **1 primary** (§33.2 solo). |
| S6-P20 | Boxed eq shrinks to CENTER (PRIMARY) | LHS panel (LEFT, PRIMARY) + Boxed eq (CENTER, PRIMARY smaller) + RHS panel (RIGHT, PRIMARY) | Same + ≈ equality caption (below, SECONDARY) | 3 primary (deliberate triple — Principle 1 RESOLVE: the equation is *checked*; 3 ≤ 4). |
| S7-P21 | (FadeOut LHS/RHS panels) | Boxed eq migrating LEFT (PRIMARY) + Heatmap (CENTER, re-entering, PRIMARY) + CodeStepper entering RIGHT (PRIMARY) | Same | 3 primary. |
| S7-P22 | All three panels stable (Boxed eq LEFT SECONDARY between sync moments) | Per-step synced trio: active code line (RIGHT, PRIMARY) + matching equation token (LEFT, PRIMARY) + matching heatmap region (CENTER, PRIMARY) | Same; trio rotates per code step | 3 primary (the synced trio). |
| S7-P23 | All three panels stable | "0.000000" output marker (next to state 6 in heatmap, PRIMARY) + hand-off caption (RIGHT, PRIMARY) | Same + heatmap pulse contrasting converged vs zero | 2 primary (the output and the caption). |
| S8-P24 | (FadeOut code, heatmap, S7 caption) | Boxed Bellman equation (CENTER, full-frame re-enlarging) | Same | **1 primary** (§33.2 solo). |
| S8-P25 | Boxed equation (CENTER) | Morphing tokens: `=`→`←`, $v_\pi(s)$→$v_{k+1}(s)$, $v_\pi(s')$→$v_k(s')$ (one Group, ≤ 1.5 s) + "Next: equation → algorithm" caption (top, PRIMARY) | Equation REVERTS to equality form (PRIMARY) | 2 primary (morph group + caption). |
| S8-P26 | Boxed eq shrinking toward upper-CENTER | Takeaway card "$v_\pi$ is the fixed point of the Bellman equation" (CENTER, PRIMARY) + LEFT flanking caption "V-02: equation" (SECONDARY) + RIGHT flanking caption "V-03: algorithm" (SECONDARY) | Same; 8.0 s hold | 1 primary (the takeaway). |

**Budget audit:** no phase exceeds 4 primary mobjects. Phases S2-P4, S6-P20, S7-P21, S7-P22 sit at 3 primary — the upper margin — and are flagged for QA attention. Each is justified by the table's note column (contrast pair, identity check, sync trio).

---

## 4. Element Lifecycle Matrix

Every mobject mentioned in plan.md appears here with explicit ENTER phase, ACTIVE period (visible window), EXIT phase, and re-entry (if any). A mobject without an explicit Phase OUT is a staleness leak (Principle 2; QA F46).

| Mobject | Phase IN | Visible during | Phase OUT | Re-enters at |
|---|---|---|---|---|
| Header `show_header("Recap", "What V-01 gave us")` | S1-P1 | S1-P1 to S1-P2 (dims to BACKGROUND after first reveal) | end of S1-P2 (FadeOut with all S1 chrome before S2-P3) | never |
| Recap caption stack (3 lines, RIGHT) | S1-P1 | S1-P1 (PRIMARY) → S1-P2 (top 2 lines FadeOut; bottom line morphs into recursion panel) | top 2 captions FadeOut at S1-P2 start; the 3rd morphs (does not exit as itself) | n/a (morphed) |
| V-01 grid thumbnail (CENTER, small) | S1-P1 | S1-P1 (PRIMARY) → S1-P2 (SECONDARY dim) | end of S1-P2 (FadeOut before S2-P3 clean canvas) | never (heatmap in S3-P7 is a new ValueHeatmap mobject, not this thumbnail) |
| $G_t = R_{t+1}+\gamma G_{t+1}$ recursion panel (LEFT) | S1-P2 (morphed from caption) | S1-P2 only | end of S1-P2 (FadeOut for S2-P3 solo) | never (referenced by callback in S5-P15 narration; not re-summoned) |
| "Today, we cook" caption (RIGHT) | S1-P2 | S1-P2 only | end of S1-P2 (FadeOut) | never |
| $\pi(a\mid s) \doteq \Pr\{A_t=a\mid S_t=s\}$ definition (full-frame, font 48) | S2-P3 | S2-P3 (PRIMARY, solo) → S2-P4 (smooth_move_to top, smaller, SECONDARY chip) → S2-P5 (chip held) | end of S2-P5 (FadeOut before S3-P6 clean canvas) | never |
| `show_header("Policies", "The agent's strategy")` | S2-P3 | S2-P3 → S2-P5 (BACKGROUND chrome) | end of S2-P5 (FadeOut with header replacement) | never |
| Policy A arrow-grid (deterministic "all RIGHT", LEFT) | S2-P4 | S2-P4 (PRIMARY) → S2-P5 (SECONDARY smaller, flanking) | end of S2-P5 (FadeOut — Policy A is *not* the working policy and does not return) | never |
| Policy A caption "$\pi(\text{RIGHT}\mid s)=1$" | S2-P4 | S2-P4 → S2-P5 (held) | end of S2-P5 (FadeOut) | never |
| Policy B arrow-grid (equiprobable, RIGHT) | S2-P4 | S2-P4 → S2-P5 (smaller flanking) → preserved as `equiprobable_grid_group` after S2-P5 | end of S2-P5 visible form (FadeOut from full canvas); Group preserved hidden | re-enters as BACKGROUND thumbnail (lower-right corner, OPACITY 0.17) at S5-P13 through S5-P19; full FadeOut at end of S5-P19 |
| Policy B caption "$\pi(a\mid s)=\tfrac14$" | S2-P4 | S2-P4 → S2-P5 (held) | end of S2-P5 (FadeOut) | never |
| "Two valid policies. Same grid." caption (CENTER) | S2-P4 | S2-P4 only | end of S2-P4 (FadeOut; replaced by normalization eq in S2-P5) | never |
| State-6 spotlight squares on both policy grids | S2-P5 | S2-P5 only | end of S2-P5 (FadeOut with both policy grids) | never |
| Normalization equation $\sum_a \pi(a\mid s)=\tfrac14+\tfrac14+\tfrac14+\tfrac14=1$ | S2-P5 | S2-P5 only | end of S2-P5 (FadeOut) | never |
| "Normalization. For every state, the policy is a probability distribution." caption | S2-P5 | S2-P5 only | end of S2-P5 (FadeOut) | never |
| $v_\pi(s) \doteq \mathbb{E}_\pi[G_t \mid S_t=s]$ definition | S3-P6 | S3-P6 (PRIMARY, solo) → S3-P7 (smooth_move_to LEFT, smaller SECONDARY) → S3-P8, S3-P9 (held SECONDARY) → S4-P10 (BACKGROUND while $q_\pi$ takes solo) → S4-P11 (held LEFT SECONDARY) | end of S4-P12 (FadeOut as linking identity replaces it on LEFT) | implicit callback in S5-P14 step-1 equation, but a NEW MathTex is written there for TransformMatchingTex purposes |
| `show_header("State-value function", "How good is this state under π?")` | S3-P6 | S3-P6 to S3-P9 (BACKGROUND chrome) | end of S3-P9 (FadeOut at S4-P10 header replacement) | never |
| ValueHeatmap (4×4 grid, cells with values + tints) | S3-P7 | S3-P7 (PRIMARY full reveal) → S3-P8 (SECONDARY except spotlit cell 14) → S3-P9 (SECONDARY except spotlit cell 15) → S4-P10 (lower-CENTER inset, BACKGROUND) → S4-P11 (state 14 enlarged inset, partial PRIMARY) → S4-P12 (SECONDARY, lower-CENTER) | preserved as `heatmap_group` (hidden) at end of S4-P12 before S5-P13 clean canvas; **fully FadeOut** at end of S7-P23 | re-enters at S7-P21 (CENTER, smaller) → S7-P22 (cells pulse) → S7-P23 (state 6 with "0.000000" annotation) |
| Colorbar legend (RIGHT) | S3-P7 | S3-P7 only (SECONDARY) | end of S3-P7 (FadeOut before S3-P8 spotlight) | never |
| State 14 spotlight (`Indicate` square + glow) | S3-P8 | S3-P8 only | end of S3-P8 (FadeOut at S3-P9 transition to goal spotlight) | never (same cell highlighted differently in S4-P11 inset) |
| M-2 caption (RIGHT, 3 lines incl. "Value lives in the future, not the present.") | S3-P8 | S3-P8 only | end of S3-P8 (FadeOut) | never |
| Floating `r=0` marker above cell 14 | S3-P8 | S3-P8 only (≤ 1.5 s pulse) | end of S3-P8 (FadeOut after trace_vector resolves) | never |
| State 15 (goal) spotlight | S3-P9 | S3-P9 only | end of S3-P9 (FadeOut at S4-P10 clean transition) | never |
| Goal reward marker `+1.0` (REWARD_COLOR, above goal cell) | S3-P9 | S3-P9 only | end of S3-P9 (FadeOut) | never |
| Goal value label `v_π(15)=0` (VALUE_COLOR, inside goal cell) | S3-P9 | S3-P9 only (as pulse overlay; the heatmap's own value label persists) | end of S3-P9 (FadeOut; underlying heatmap cell-15 label persists into S4 inset BACKGROUND) | never (the underlying heatmap label survives via heatmap_group) |
| Terminal-state caption (RIGHT, "Terminal states have $v_\pi=0$…") | S3-P9 | S3-P9 only | end of S3-P9 (FadeOut) | never |
| $q_\pi(s,a) \doteq \mathbb{E}_\pi[G_t \mid S_t=s, A_t=a]$ definition | S4-P10 | S4-P10 (PRIMARY, solo) → S4-P11 (smooth_move_to RIGHT, SECONDARY) | end of S4-P11 (FadeOut at S4-P12 to free RIGHT) | never |
| `show_header("Action-value function", …)` | S4-P10 | S4-P10 to S4-P12 (BACKGROUND) | end of S4-P12 (FadeOut at S5-P13 clean canvas) | never |
| State-14 inset (enlarged copy of heatmap cell 14) | S4-P11 | S4-P11 → S4-P12 | end of S4-P12 (FadeOut at S5-P13 clean canvas) | never |
| 4 q-bars on cell 14 (L, D, R, U), labeled `ActionBarChart` | S4-P11 | S4-P11 → S4-P12 (bracket-arrow connects to v) | end of S4-P12 (FadeOut at S5-P13 clean canvas) | never |
| Bar action labels (L/D/R/U in `ACTION_COLOR`) | S4-P11 | S4-P11 → S4-P12 | end of S4-P12 | never |
| Linking identity general form (LEFT) | S4-P12 | S4-P12 only (then morphs to state-14 form) | morphs (no FadeOut as itself); morphed product FadeOut at end of S4-P12 | never |
| Linking identity state-14 form (LEFT) | S4-P12 (morphed) | S4-P12 only | end of S4-P12 (FadeOut at S5-P13 clean canvas) | never |
| Bracket-to-cell arrow (4 q-bars → $v_\pi(14)$ heatmap cell) | S4-P12 | S4-P12 only | end of S4-P12 (FadeOut) | never |
| Backup diagram rooted at state 6 (full composite VGroup) | S5-P13 | S5-P13 (PRIMARY full reveal) → S5-P14 (smaller, SECONDARY except root) → S5-P15 (highlighting one edge + brace) → S5-P16 (action nodes pulse) → S5-P17 (transition leaves pulse) → S5-P18 (leaves relabel) | end of S5-P18 (FadeOut with step-5 eq before S5-P19 boxed solo) | never |
| Equiprobable policy thumbnail (BACKGROUND, lower-right corner) | S5-P13 | S5-P13 to S5-P18 (BACKGROUND throughout) | end of S5-P18 (FadeOut with backup diagram) | never |
| Step-1 derivation panel (LEFT) | S5-P14 | S5-P14 only (then morphs through steps 2–5) | morphs sequentially (S5-P15..P18 each TransformMatchingTex against prior); final morphed form FadeOut at end of S5-P18 | this IS the same MathTex instance morphing — no re-entry needed |
| $R_{t+1}$ edge label on diagram | S5-P15 | S5-P15 only | end of S5-P15 (FadeOut with diagram-level annotations at S5-P19 clean) | never |
| $G_{t+1}$ subtree brace on diagram | S5-P15 | S5-P15 only | end of S5-P15 (the brace transforms into the $v_\pi(s')$ relabeling chain in S5-P18; visually FadeOut at S5-P18 morph) | never |
| Action-node pulse highlights (4 action nodes) | S5-P16 | S5-P16 only (pulse and rest) | pulse decays at end of S5-P16; nodes themselves are part of backup diagram | n/a (returns as element of diagram, not standalone) |
| Transition-leaf pulse highlights (3 leaves under RIGHT) | S5-P17 | S5-P17 only (pulse and rest) | pulse decays at end of S5-P17 | n/a |
| Relabeled leaves $v_\pi(2), v_\pi(7)=0, v_\pi(10)$ | S5-P18 | S5-P18 only | end of S5-P18 (FadeOut with diagram) | never |
| **Boxed Bellman equation** (the canonical mobject — `Rectangle` border + `v_step5` MathTex) | S5-P19 | S5-P19 (PRIMARY full-frame solo) → S6-P20 (CENTER, smaller, PRIMARY) → S7-P21 (smooth_move_to LEFT, PRIMARY then SECONDARY between sync moments) → S7-P22 (tokens pulse per sync step) → S7-P23 (LEFT, SECONDARY) → S8-P24 (smooth_move_to CENTER, re-enlarge to PRIMARY full-frame) → S8-P25 (morph $=\to\leftarrow$ and back) → S8-P26 (smaller upper-CENTER, SECONDARY) | end of S8-P26 (FadeOut at scene end) | **This is the most-traveled mobject in the scene.** It persists through 7 segments. |
| `show_header("The Bellman expectation equation for v_π", "S&B eq. (3.14), p. 59")` | S5-P19 | S5-P19 to S8-P26 (BACKGROUND chrome throughout) | end of S8-P26 (FadeOut at scene end; or replaced by "Coming next: dp_policy_eval" header at S8-P26) | never |
| LHS panel ($v_\pi(6)\approx 0.039$ + cell-6 inset, LEFT) | S6-P20 | S6-P20 only | end of S6-P20 (FadeOut before S7-P21) | never |
| RHS panel (term-by-term Bellman RHS computation, RIGHT) | S6-P20 | S6-P20 only | end of S6-P20 (FadeOut) | never |
| LHS↔heatmap memory arrow | S6-P20 | S6-P20 only | end of S6-P20 (FadeOut) | never |
| RHS↔backup-diagram memory arrow | S6-P20 | S6-P20 only | end of S6-P20 (FadeOut) | never |
| `≈ 0.039` equality caption (below boxed eq) | S6-P20 | S6-P20 only | end of S6-P20 (FadeOut) | never |
| `CodeStepper` panel (RIGHT, 11-step Python source) | S7-P21 | S7-P21 (entry, PRIMARY) → S7-P22 (per-step active line PRIMARY, others SECONDARY) → S7-P23 (output displayed, SECONDARY) | end of S7-P23 (FadeOut before S8-P24 boxed-equation re-center) | never |
| `0.000000` output marker (next to state 6 in heatmap) | S7-P23 | S7-P23 only | end of S7-P23 (FadeOut with all S7 elements) | never |
| Hand-off caption (RIGHT, 3 lines incl. "One sweep is not enough — V-03 will iterate.") | S7-P23 | S7-P23 only | end of S7-P23 (FadeOut) | never |
| Morph-Group (`=`→`←`, $v_\pi(s)$→$v_{k+1}(s)$, $v_\pi(s')$→$v_k(s')$) | S8-P25 | S8-P25 only (≤ 1.5 s held, then reverts) | reverts at end of morph; the boxed equation is restored to its V-02 equality form | n/a (reverts into the boxed-equation mobject) |
| "Next: equation → algorithm" caption (top, S8-P25) | S8-P25 | S8-P25 only | end of S8-P25 (FadeOut) | never |
| Takeaway card "$v_\pi$ is the fixed point of the Bellman equation" (CENTER, lower) | S8-P26 | S8-P26 only (8.0 s hold) | scene end (FadeOut implicit at scene close) | never |
| "V-02: the equation." caption (LEFT, flanking) | S8-P26 | S8-P26 only | scene end | never |
| "V-03: the algorithm." caption (RIGHT, flanking) | S8-P26 | S8-P26 only | scene end | never |
| `show_header("Coming next: dp_policy_eval", subtitle=None)` | S8-P26 | S8-P26 only (replaces S5-P19 boxed-equation header) | scene end | never |

**Leak audit:** every mobject above has an explicit Phase OUT. The longest-lived element is the Boxed Bellman equation (S5-P19 → S8-P26, 7 segments) — this is intentional per Principle 2 condition (1): it is repeatedly used as an anchor for trace_vector, cross_highlight_pair, and per-token highlight pulses in S6, S7, S8. The next-longest is the ValueHeatmap (S3-P7 → S4-P12 visible, then preserved Group, then re-enters S7-P21 → S7-P23) — justified by Principle 2 condition (1): heatmap cell-6 is the anchor for the CodeStepper synchronization in S7-P22 and the "0.000000" annotation in S7-P23. No mobject persists past its segment without explicit dimming to OPACITY_SECONDARY or OPACITY_BACKGROUND.

---

## 5. Motion Choreography (per-phase)

Every animation tagged REVEAL / DERIVE / RESOLVE / CONNECT / REFRAME (Principle 1; QA F47). `run_time` is the Manim parameter. Times are relative to phase start.

### Phase S1-P1 — Cold open: empty grid + recap captions

| t (rel.) | Animation | Purpose tag | Helper / Manim call | run_time |
|---|---|---|---|---|
| 0.0 s | `show_header("Recap", "What V-01 gave us")` writes top | REVEAL | `BaseConceptScene.show_header(...)` | 0.8 s |
| 0.8 s | FadeIn V-01 grid thumbnail at CENTER (scale 0.5) | REVEAL | `frozenlake_frame(grid_size=4, soft_frame=True, scale=0.5)` + `FadeIn` | 1.2 s |
| 2.0 s | `staggered_write` recap caption stack (3 lines, RIGHT) | REVEAL | `place_caption(stack, region="RIGHT")` + `LaggedStart` | 2.0 s |
| 4.0 s | `self.wait(2.0)` — assimilation hold | — | `self.wait(2.0)` | 2.0 s |

### Phase S1-P2 — The recursion callback

| t | Animation | Purpose | Helper | run_time |
|---|---|---|---|---|
| 0.0 s | FadeOut top 2 caption lines; line 3 ("Return $G_t$ — the recursion") remains | (cleanup, prerequisite for morph) | `FadeOut(caption[0:2])` | 0.6 s |
| 0.6 s | `equation_morph(caption_line_3, recursion_eq)` — caption transforms into a formal equation panel | DERIVE | `equation_morph(...)` | 1.4 s |
| 2.0 s | `smooth_move_to(recursion_eq, LEFT_X)` — migrate panel to LEFT hemisphere | REFRAME | `BaseConceptScene.smooth_move_to(...)` | 1.4 s |
| 3.4 s | Grid thumbnail dims to OPACITY_SECONDARY simultaneously with the migration | (focal demotion) | `grid_thumb.animate.set_opacity(0.4)` | 1.4 s (parallel) |
| 3.4 s | `place_caption("Today, we take the expectation of this recursion under a policy.", region="RIGHT")` with `staggered_write` | REVEAL | `place_caption(...)` | 1.5 s |
| 4.9 s | `self.wait(1.5)` | — | `self.wait(1.5)` | 1.5 s |
| 6.4 s | `self.ingestion_wait(2.5)` (post-scene-wide-reposition, STYLE_BIBLE §18) | — | `self.ingestion_wait(2.5)` | 2.5 s |

### Phase S2-P3 — π definition, full-frame solo

| t | Animation | Purpose | Helper | run_time |
|---|---|---|---|---|
| 0.0 s | FadeOut all S1 elements (header, recursion panel, grid thumbnail, "today we cook" caption) — group fade | (cleanup for solo canvas) | `FadeOut(s1_group)` | 1.0 s |
| 1.0 s | `show_header("Policies", "The agent's strategy")` writes top (HUMAN-READABLE subtitle, no slug) | REVEAL | `BaseConceptScene.show_header(...)` | 0.8 s |
| 1.8 s | `staggered_write(pi_def)` — token-by-token reveal of the 16-component MathTex | REVEAL | `staggered_write(pi_def)` (LaggedStart, lag=0.08) | 2.4 s |
| 4.2 s | `self.wait(2.0)` — equation reveal minimum | — | `self.wait(2.0)` | 2.0 s |
| 6.2 s | `self.ingestion_wait(2.5)` (post-morph, §18) | — | `self.ingestion_wait(2.5)` | 2.5 s |

### Phase S2-P4 — Two policies, same grid

| t | Animation | Purpose | Helper | run_time |
|---|---|---|---|---|
| 0.0 s | `smooth_move_to(pi_def, UP*3.0)` — shrink to header chip | REFRAME (demote prior focus) | `BaseConceptScene.smooth_move_to(pi_def, top, scale=0.55)` | 1.4 s |
| 1.4 s | FadeIn Policy A arrow-grid (LEFT) + Policy A caption "$\pi(\text{RIGHT}\mid s)=1$" | REVEAL | `PolicyArrowGrid(grid=frozenlake_frame(scale=0.4), policy_mode="deterministic", action=2)` + `staggered_write` caption | 1.6 s |
| 3.0 s | FadeIn Policy B arrow-grid (RIGHT) + Policy B caption "$\pi(a\mid s)=\tfrac14$" | REVEAL | `PolicyArrowGrid(..., policy_mode="equiprobable")` + caption | 1.6 s |
| 4.6 s | FadeIn center caption "Two valid policies. Same grid." | REVEAL | `place_caption(..., region="CENTER")` | 0.8 s |
| 5.4 s | `trace_vector` from Policy A caption to one arrow on Policy A grid (CONNECT) | CONNECT | `trace_vector(scene, src=caption_A, target=arrow_on_A_cell6, color=POLICY_COLOR)` | 0.8 s |
| 6.2 s | `trace_vector` from Policy B caption to the 4 arrows on one cell of Policy B grid | CONNECT | `trace_vector(scene, src=caption_B, target=arrow_bundle_on_B_cell6, color=POLICY_COLOR)` | 0.8 s |
| 7.0 s | `self.wait(2.5)` — both grids absorption | — | `self.wait(2.5)` | 2.5 s |

### Phase S2-P5 — Normalization

| t | Animation | Purpose | Helper | run_time |
|---|---|---|---|---|
| 0.0 s | Both policy grids shrink slightly toward their respective edges (smooth_move_to with scale 0.85) | REFRAME | `BaseConceptScene.smooth_move_to(...)` parallel on both grids | 1.2 s |
| 1.2 s | Spotlight `Square` (STATE_COLOR border) appears on cell 6 of BOTH grids simultaneously | REVEAL | `Indicate(cell_6_A, color=STATE_COLOR)` + `Indicate(cell_6_B, ...)` (parallel) | 0.8 s |
| 2.0 s | `staggered_write(normalization_eq)` at CENTER — token-by-token reveal of $\sum_a \pi(a\mid s)=\tfrac14+\tfrac14+\tfrac14+\tfrac14=1$ | REVEAL | `staggered_write(...)` LaggedStart lag=0.1 | 2.0 s |
| 4.0 s | `equation_morph` binds the four "$\tfrac14$" tokens to the four arrows on Policy B's cell 6 (one trace per token, staggered) | DERIVE / CONNECT | `equation_morph` + 4 × `trace_vector` (staggered 0.2 s) | 1.6 s |
| 5.6 s | FadeIn side caption "Normalization. For every state, the policy is a probability distribution." (below) | REVEAL | `place_caption(..., region="below")` | 0.8 s |
| 6.4 s | `self.wait(3.0)` — extended hold for adoption of equiprobable policy | — | `self.wait(3.0)` | 3.0 s |
| 9.4 s | `self.ingestion_wait(2.5)` (§18) | — | `self.ingestion_wait(2.5)` | 2.5 s |

### Phase S3-P6 — v_π definition, full-frame solo

| t | Animation | Purpose | Helper | run_time |
|---|---|---|---|---|
| 0.0 s | FadeOut all S2 elements (Policy A grid, both captions, normalization eq, spotlights, S2 header). **Preserve Policy B grid as a hidden Group `equiprobable_grid_group`** for S5 re-entry. | (cleanup for solo) | `FadeOut(s2_visible_group)` + `equiprobable_grid_group.set_opacity(0)` (preserved) | 1.0 s |
| 1.0 s | `show_header("State-value function", "How good is this state under π?")` | REVEAL | `BaseConceptScene.show_header(...)` | 0.8 s |
| 1.8 s | `staggered_write(v_def)` token-by-token | REVEAL | `staggered_write(v_def)` lag=0.08 | 2.4 s |
| 4.2 s | `self.wait(2.0)` | — | `self.wait(2.0)` | 2.0 s |
| 6.2 s | `self.ingestion_wait(2.5)` (§18) | — | `self.ingestion_wait(2.5)` | 2.5 s |

### Phase S3-P7 — Heatmap reveal

| t | Animation | Purpose | Helper | run_time |
|---|---|---|---|---|
| 0.0 s | `smooth_move_to(v_def, LEFT_X)` — migrate to LEFT and reduce font_size to 30 | REFRAME | `BaseConceptScene.smooth_move_to(v_def, LEFT_X, scale=0.65)` | 1.4 s |
| 1.4 s | `ValueHeatmap` instantiated at CENTER (cells initially invisible) — Manhattan-distance fade-in sequence begins from goal outward | REVEAL | `ValueHeatmap(env, values=v_pi_array)` + `cell_fade_in_sequence(manhattan_order=True)` | 4.0 s |
| 5.4 s | Hole cells (5, 7, 11, 12) tint to PENALTY_COLOR semi-transparent overlay; goal cell (15) acquires REWARD_COLOR border | REVEAL (boundary condition) | `cell.animate.set_fill(PENALTY_COLOR, opacity=0.4)` + `goal_cell_border` | 0.8 s (parallel) |
| 6.2 s | FadeIn colorbar on RIGHT (SECONDARY, scale 0.6) | REVEAL | `place_caption(colorbar, region="RIGHT")` | 0.8 s |
| 7.0 s | `trace_vector(scene, src=v_def[7]"G_t", target=heatmap.cell(14).label, color=VALUE_COLOR)` — single anchor binding the equation $G_t$ token to the brightest cell | CONNECT | `trace_vector(...)` | 1.0 s |
| 8.0 s | `self.wait(2.0)` | — | `self.wait(2.0)` | 2.0 s |
| 10.0 s | `self.ingestion_wait(2.5)` (§18, post-reposition + fade-in) | — | `self.ingestion_wait(2.5)` | 2.5 s |

### Phase S3-P8 — Misconception M-2 defuse (state 14 spotlight)

| t | Animation | Purpose | Helper | run_time |
|---|---|---|---|---|
| 0.0 s | All non-cell-14 heatmap cells dim to OPACITY_SECONDARY (0.4); cell 14 enlarges via `Indicate` scale_factor=1.15 | REFRAME (focal narrow) | `other_cells.animate.set_opacity(0.4)` + `Indicate(heatmap.cell(14), scale_factor=1.15)` | 1.2 s |
| 1.2 s | Floating `r=0` marker appears above cell 14 (REWARD_COLOR, MathTex, font 26) | REVEAL | `MathTex("r=0", color=REWARD_COLOR).next_to(cell_14, UP*0.3)` + FadeIn | 0.6 s |
| 1.8 s | `place_caption(M2_caption_3_lines, region="RIGHT", anchor=cell_14)` — staggered_write 3 lines | REVEAL | `place_caption(...)` + `staggered_write` | 2.0 s |
| 3.8 s | `trace_vector` from "Reward at state 14: 0" caption line to floating `r=0` marker | CONNECT | `trace_vector(scene, caption_line_1, r0_marker, color=REWARD_COLOR)` | 0.8 s |
| 4.6 s | `trace_vector` from "Value at state 14: 0.434" caption line to cell-14 yellow label | CONNECT | `trace_vector(scene, caption_line_2, cell_14.label, color=VALUE_COLOR)` | 0.8 s |
| 5.4 s | `self.wait(2.5)` — misconception absorption | — | `self.wait(2.5)` | 2.5 s |

### Phase S3-P9 — Misconception M-2 escalation (goal at value 0)

| t | Animation | Purpose | Helper | run_time |
|---|---|---|---|---|
| 0.0 s | Spotlight migrates: cell 14 dims back to OPACITY_SECONDARY; cell 15 (goal) enlarges via `Indicate` (parallel) | REFRAME | `cell_14.animate.set_opacity(0.4)` + `Indicate(heatmap.cell(15), scale_factor=1.15)` | 1.2 s |
| 1.2 s | FadeOut M-2 caption from S3-P8 (cleanup) | (cleanup) | `FadeOut(M2_caption)` | 0.6 s |
| 1.8 s | **Simultaneous** pulse: green `+1.0` reward marker appears above cell 15 (REWARD_COLOR) AND yellow `v_π(15)=0` label appears inside cell 15 (VALUE_COLOR) — both via `Indicate` with simultaneous start | RESOLVE (M-2 punchline) + CONNECT (cross-highlight pair: REWARD vs VALUE on same cell) | `goal_reward_marker = MathTex("+1.0", color=REWARD_COLOR)` + `goal_value_label = MathTex("v_\\pi(15)=0", color=VALUE_COLOR)` + parallel `Indicate` | 1.2 s |
| 3.0 s | `place_caption(terminal_caption_3_lines, region="RIGHT", anchor=cell_15)` | REVEAL | `place_caption(...)` + `staggered_write` | 2.0 s |
| 5.0 s | `trace_vector` from caption line 1 ("reward +1.0") to green marker | CONNECT | `trace_vector(..., color=REWARD_COLOR)` | 0.8 s |
| 5.8 s | `trace_vector` from caption line 2 ("value = 0") to yellow label inside cell | CONNECT | `trace_vector(..., color=VALUE_COLOR)` | 0.8 s |
| 6.6 s | `self.wait(2.5)` — misconception-critical hold | — | `self.wait(2.5)` | 2.5 s |
| 9.1 s | `self.ingestion_wait(2.5)` (§18) | — | `self.ingestion_wait(2.5)` | 2.5 s |

### Phase S4-P10 — q_π definition, full-frame solo

| t | Animation | Purpose | Helper | run_time |
|---|---|---|---|---|
| 0.0 s | Heatmap `smooth_move_to(lower_CENTER, scale=0.4)` — preserve as visible BACKGROUND inset (not FadeOut) | REFRAME (focal demote) | `BaseConceptScene.smooth_move_to(heatmap, DOWN*2 + ORIGIN, scale=0.4)` + opacity=0.17 | 1.4 s |
| 1.4 s | $v_\pi$ definition (LEFT) dims to OPACITY_SECONDARY 0.4 | (focal demote) | `v_def.animate.set_opacity(0.4)` | 0.4 s (parallel) |
| 1.4 s | S3 header FadeOut; `show_header("Action-value function", "Committing to one action, then following π")` | (header swap) | `FadeOut(s3_header)` + `show_header(...)` | 0.8 s |
| 2.2 s | `staggered_write(q_def)` token-by-token | REVEAL | `staggered_write(q_def)` lag=0.08 | 2.6 s |
| 4.8 s | `self.wait(2.0)` | — | `self.wait(2.0)` | 2.0 s |
| 6.8 s | `self.ingestion_wait(2.5)` (§18) | — | `self.ingestion_wait(2.5)` | 2.5 s |

### Phase S4-P11 — q-bars on state 14

| t | Animation | Purpose | Helper | run_time |
|---|---|---|---|---|
| 0.0 s | `smooth_move_to(q_def, RIGHT_X)` and reduce font_size to 30 | REFRAME | `BaseConceptScene.smooth_move_to(q_def, RIGHT_X, scale=0.65)` | 1.4 s |
| 1.4 s | State-14 inset enlarges from the heatmap lower-CENTER inset: `Indicate` + `smooth_scale` to scale=1.0 at mid-CENTER | REFRAME + REVEAL | `cell_14_inset = heatmap.cell(14).copy()` + `inset.animate.move_to(ORIGIN).scale(2.0)` | 1.6 s |
| 3.0 s | `ActionBarChart` instantiates 4 edge-attached bars (L, D, R, U) with `VALUE_COLOR` fills; bar labels in `ACTION_COLOR`; numeric values in `VALUE_COLOR` font 22 — `staggered_write` order: L → D → R → U | REVEAL | `ActionBarChart(state=14, values=q_pi_state14_values, action_labels=["L","D","R","U"], color=VALUE_COLOR, edge_attached=True)` + `staggered_write` | 2.4 s |
| 5.4 s | `trace_vector` from `q_π(s, a)` token in (RIGHT) equation to each of 4 bars (staggered 0.3 s) | CONNECT | 4 × `trace_vector(..., color=VALUE_COLOR)` | 2.0 s |
| 7.4 s | `self.wait(2.0)` | — | `self.wait(2.0)` | 2.0 s |
| 9.4 s | `self.ingestion_wait(2.5)` (§18) | — | `self.ingestion_wait(2.5)` | 2.5 s |

### Phase S4-P12 — Linking identity

| t | Animation | Purpose | Helper | run_time |
|---|---|---|---|---|
| 0.0 s | FadeOut `q_def` (RIGHT) to free hemisphere | (cleanup, prerequisite for new LEFT panel) | `FadeOut(q_def)` | 0.6 s |
| 0.6 s | $v_\pi$ definition (LEFT) FadeOut (it has served its role) | (cleanup) | `FadeOut(v_def)` | 0.6 s |
| 1.2 s | `staggered_write(link_general)` at LEFT panel position | REVEAL | `staggered_write(link_general)` lag=0.08 | 2.4 s |
| 3.6 s | `equation_morph(link_general, link_state14)` — general identity morphs to state-14 specific form | DERIVE | `equation_morph(link_general, link_state14)` (TransformMatchingTex) | 1.6 s |
| 5.2 s | `Arrow` from bracket above 4 q-bars to single $v_\pi(14)$ value in heatmap cell-14 (recalled from heatmap inset) | CONNECT | `Arrow(bracket_top, heatmap.cell(14).label, color=VALUE_COLOR, buff=0.1)` + `Create` | 1.2 s |
| 6.4 s | `trace_vector` from each $q_\pi(14, \cdot)$ token in `link_state14` to its corresponding bar (4 traces, staggered 0.25 s) | CONNECT | 4 × `trace_vector(..., color=VALUE_COLOR)` | 2.0 s |
| 8.4 s | `self.wait(2.0)` | — | `self.wait(2.0)` | 2.0 s |
| 10.4 s | `self.ingestion_wait(2.5)` (§18) | — | `self.ingestion_wait(2.5)` | 2.5 s |

### Phase S5-P13 — Backup diagram entry

| t | Animation | Purpose | Helper | run_time |
|---|---|---|---|---|
| 0.0 s | FadeOut all S4 elements (linking identity, state-14 inset, 4 q-bars, arrow, heatmap inset). **Preserve heatmap as hidden Group `heatmap_group`.** | (cleanup for backup diagram solo) | `FadeOut(s4_visible_group)` + `heatmap_group.set_opacity(0)` | 1.2 s |
| 1.2 s | S4 header FadeOut; `show_header("Bellman expectation derivation", "Backup diagram at state 6")` | (header swap) | `show_header(...)` | 0.8 s |
| 2.0 s | Backup diagram root node fades in at top-CENTER (state node, STATE_COLOR border, VALUE_COLOR `v_π(6)` label) | REVEAL | `BackupDiagram(root_state=6, ...).root_node` + `FadeIn` | 0.8 s |
| 2.8 s | Four action edges grow downward from root; four action nodes (ACTION_COLOR fill) appear at endpoints; π branch labels (POLICY_COLOR) appear on edges (staggered) | REVEAL | `staggered_write(action_layer)` lag=0.15 | 1.8 s |
| 4.6 s | Under the RIGHT action node only: three transition edges grow; three (s', r) leaf nodes appear (state 2, 7, 10) in STATE_COLOR; $p$ probability labels (CODE_ACCENT) on edges; reward labels `r=0` (REWARD_COLOR) on leaves | REVEAL | `staggered_write(transition_layer_under_RIGHT)` lag=0.12 | 2.2 s |
| 6.8 s | Equiprobable policy thumbnail FadeIn at lower-right corner, OPACITY_BACKGROUND 0.17 (from preserved `equiprobable_grid_group`) | REVEAL (context anchor) | `equiprobable_grid_group.animate.set_opacity(0.17).move_to(BOTTOM_RIGHT_CORNER)` | 0.8 s |
| 7.6 s | `trace_vector` from $\pi(R\mid 6)$ branch label → one arrow in the lower-right thumbnail | CONNECT (grounds π in equiprobable) | `trace_vector(..., color=POLICY_COLOR)` | 0.8 s |
| 8.4 s | `trace_vector` from $p(2\mid 6, R)$ leaf label → state 2 in the (faint) thumbnail | CONNECT | `trace_vector(..., color=CODE_ACCENT)` | 0.8 s |
| 9.2 s | `trace_vector` from $p(7\mid 6, R)$ leaf label → state 7 (hole) in the thumbnail | CONNECT | `trace_vector(..., color=CODE_ACCENT)` | 0.8 s |
| 10.0 s | `self.wait(2.5)` | — | `self.wait(2.5)` | 2.5 s |
| 12.5 s | `self.ingestion_wait(2.5)` (§18, full-frame reveal) | — | `self.ingestion_wait(2.5)` | 2.5 s |

### Phase S5-P14 — Derivation Step 1: definition

| t | Animation | Purpose | Helper | run_time |
|---|---|---|---|---|
| 0.0 s | Backup diagram `smooth_move_to(CENTER_right, scale=0.7)` — make room for LEFT equation panel | REFRAME | `BaseConceptScene.smooth_move_to(backup_diagram, RIGHT*1.5, scale=0.7)` | 1.4 s |
| 1.4 s | `staggered_write(v_def_step1)` at LEFT panel (reuses `v_def` MathTex from S3-P6 for TransformMatchingTex chain) | REVEAL | `staggered_write(v_def_step1)` lag=0.08 | 2.2 s |
| 3.6 s | `Indicate(backup_diagram.root_node, color=VALUE_COLOR)` — root pulses to bind to LHS $v_\pi(s)$ token | CONNECT | `Indicate(root_node, color=VALUE_COLOR, scale_factor=1.2)` | 1.0 s |
| 4.6 s | `trace_vector` from $v_\pi(s)$ token in eq (LEFT) → root node label `v_π(6)` in diagram | CONNECT | `trace_vector(..., color=VALUE_COLOR)` | 0.8 s |
| 5.4 s | `self.wait(1.5)` | — | `self.wait(1.5)` | 1.5 s |

### Phase S5-P15 — Derivation Step 2: substitute the recursion

| t | Animation | Purpose | Helper | run_time |
|---|---|---|---|---|
| 0.0 s | `equation_morph(v_def_step1, v_step2)` — $G_t$ token transforms to $R_{t+1} + \gamma G_{t+1}$ | DERIVE | `equation_morph(v_def_step1, v_step2)` (TransformMatchingTex; matching transform on shared tokens, new tokens FadeIn) | 1.8 s |
| 1.8 s | On backup diagram (CENTER): one root-to-action-RIGHT edge gets a label `R_{t+1}` (REWARD_COLOR); subtree under action RIGHT gets a `Brace` labeled `G_{t+1}` (VALUE_COLOR) | REVEAL + CONNECT | `MathTex("R_{t+1}", color=REWARD_COLOR).next_to(edge_to_RIGHT)` + `Brace(subtree_under_RIGHT, direction=DOWN, label="G_{t+1}", color=VALUE_COLOR)` + parallel Create | 1.2 s |
| 3.0 s | `trace_vector` from $R_{t+1}$ token in eq → labeled edge on diagram | CONNECT | `trace_vector(..., color=REWARD_COLOR)` | 0.8 s |
| 3.8 s | `trace_vector` from $G_{t+1}$ token in eq → braced subtree on diagram | CONNECT | `trace_vector(..., color=VALUE_COLOR)` | 0.8 s |
| 4.6 s | `self.wait(1.5)` | — | `self.wait(1.5)` | 1.5 s |
| 6.1 s | `self.ingestion_wait(2.5)` (§18, equation morph) | — | `self.ingestion_wait(2.5)` | 2.5 s |

### Phase S5-P16 — Derivation Step 3: outer sum over actions (policy randomness)

| t | Animation | Purpose | Helper | run_time |
|---|---|---|---|---|
| 0.0 s | FadeOut `R_{t+1}` edge label and `G_{t+1}` brace from S5-P15 (cleanup, the morph subsumes them) | (cleanup) | `FadeOut(edge_label_group)` | 0.5 s |
| 0.5 s | `equation_morph(v_step2, v_step3)` — new tokens $\sum_a$ and $\pi(a\mid s)$ FadeIn; rest matches | DERIVE | `equation_morph(v_step2, v_step3)` | 1.8 s |
| 2.3 s | `staggered_pulse(action_nodes, colors=[POLICY_COLOR, ACTION_COLOR], stagger=0.3)` — 4 action nodes pulse `POLICY_COLOR` first (branch labels light), then `ACTION_COLOR` (nodes themselves) | CONNECT + RESOLVE (outer sum geometrically realized) | `for node in action_nodes: Indicate(node.branch_label, color=POLICY_COLOR); Indicate(node, color=ACTION_COLOR)` with stagger | 2.0 s |
| 4.3 s | `trace_vector` from $\sum_a$ token in eq → the four action nodes as a Group | CONNECT | `trace_vector(scene, sum_a_token, VGroup(action_nodes), color=POLICY_COLOR)` | 0.8 s |
| 5.1 s | `trace_vector` from $\pi(a\mid s)$ token → the four $\pi$ branch labels (as Group) | CONNECT | `trace_vector(..., color=POLICY_COLOR)` | 0.8 s |
| 5.9 s | `self.wait(2.0)` | — | `self.wait(2.0)` | 2.0 s |
| 7.9 s | `self.ingestion_wait(2.5)` (§18) | — | `self.ingestion_wait(2.5)` | 2.5 s |

### Phase S5-P17 — Derivation Step 4: inner sum over (s', r) (environment randomness)

| t | Animation | Purpose | Helper | run_time |
|---|---|---|---|---|
| 0.0 s | `equation_morph(v_step3, v_step4)` — new tokens $\sum_{s',r}$ and $p(s',r\mid s,a)$ FadeIn (CODE_ACCENT); inner expectation collapses to concrete `r + γ E_π[G_{t+1}|S_{t+1}=s']` | DERIVE | `equation_morph(v_step3, v_step4)` | 2.0 s |
| 2.0 s | `staggered_pulse(transition_leaves_under_RIGHT, colors=[CODE_ACCENT, REWARD_COLOR], stagger=0.25)` — 3 transition leaves pulse `CODE_ACCENT` (p labels), then `REWARD_COLOR` (leaf r tokens) | CONNECT + RESOLVE (inner sum geometrically realized — kept visually distinct from outer) | `for leaf in transition_leaves: Indicate(leaf.p_label, color=CODE_ACCENT); Indicate(leaf.r_label, color=REWARD_COLOR)` with stagger | 1.6 s |
| 3.6 s | `trace_vector` from $\sum_{s',r}$ token → 3 transition leaves under RIGHT (as Group) | CONNECT | `trace_vector(..., color=CODE_ACCENT)` | 0.8 s |
| 4.4 s | `trace_vector` from $p(s',r\mid s,a)$ token → the 3 p labels on the leaf edges (Group) | CONNECT | `trace_vector(..., color=CODE_ACCENT)` | 0.8 s |
| 5.2 s | `trace_vector` from $r$ token → any single leaf reward label | CONNECT | `trace_vector(..., color=REWARD_COLOR)` | 0.6 s |
| 5.8 s | `self.wait(2.0)` | — | `self.wait(2.0)` | 2.0 s |
| 7.8 s | `self.ingestion_wait(2.5)` (§18) | — | `self.ingestion_wait(2.5)` | 2.5 s |

### Phase S5-P18 — Derivation Step 5: recursion closes

| t | Animation | Purpose | Helper | run_time |
|---|---|---|---|---|
| 0.0 s | `equation_morph(v_step4, v_step5)` — the inner expectation $\mathbb{E}_\pi[G_{t+1}\mid S_{t+1}=s']$ morphs to $v_\pi(s')$ (VALUE_COLOR) — single token swap | DERIVE (the recursion closes) | `equation_morph(v_step4, v_step5)` (TransformMatchingTex; ONE token visibly changes) | 1.8 s |
| 1.8 s | Backup-diagram transition leaves: their labels morph from $\mathbb{E}_\pi[G_{t+1}\mid \cdot]$ placeholders to $v_\pi(2)$, $v_\pi(7)=0$, $v_\pi(10)$ — all VALUE_COLOR; state 7 (hole) shows the explicit `=0` per terminal convention | DERIVE + RESOLVE | 3 × `TransformMatchingTex(leaf.placeholder, leaf.v_pi_label)` with stagger 0.25 s | 1.6 s |
| 3.4 s | `trace_vector` from $v_\pi(s')$ token in eq → each of the 3 relabeled leaves (3 traces, staggered 0.3 s) | CONNECT | 3 × `trace_vector(..., color=VALUE_COLOR)` | 1.4 s |
| 4.8 s | `self.wait(2.5)` — extended hold; conceptual climax | — | `self.wait(2.5)` | 2.5 s |
| 7.3 s | `self.ingestion_wait(2.5)` (§18) | — | `self.ingestion_wait(2.5)` | 2.5 s |

### Phase S5-P19 — Boxed Bellman equation, full-frame solo

| t | Animation | Purpose | Helper | run_time |
|---|---|---|---|---|
| 0.0 s | FadeOut backup diagram, step-5 LEFT panel, equiprobable policy thumbnail, S5 header (all S5 visible elements) | (cleanup for solo) | `FadeOut(s5_visible_group)` | 1.2 s |
| 1.2 s | `show_header("The Bellman expectation equation for v_π", "S&B eq. (3.14), p. 59")` | REVEAL | `BaseConceptScene.show_header(...)` | 0.8 s |
| 2.0 s | `equation_morph(v_step5, v_step5_boxed)` — same MathTex re-centered at CENTER, font_size=48, wrapped in thin `Rectangle` border | REVEAL (final form) | `equation_morph(v_step5, v_step5_boxed)` + `Create(Rectangle(...))` around equation | 1.8 s |
| 3.8 s | `self.wait(3.0)` — solo hold per STYLE_BIBLE §33.2 (≥ 2.5 s) | — | `self.wait(3.0)` | 3.0 s |
| 6.8 s | `self.ingestion_wait(2.5)` (§18) | — | `self.ingestion_wait(2.5)` | 2.5 s |

### Phase S6-P20 — LHS = RHS at state 6

| t | Animation | Purpose | Helper | run_time |
|---|---|---|---|---|
| 0.0 s | `smooth_move_to(boxed_bellman, ORIGIN, scale=0.7)` — equation shrinks for flanking panels | REFRAME | `BaseConceptScene.smooth_move_to(boxed_bellman, ORIGIN, scale=0.7)` | 1.4 s |
| 1.4 s | FadeIn LHS panel at LEFT: title "LHS: $v_\pi(6)$ from heatmap" + small heatmap inset (cell 6 highlighted) + value `0.039` | REVEAL | `place_caption("LHS: …", region="LEFT", anchor=heatmap_cell6_inset)` + FadeIn inset | 1.4 s |
| 2.8 s | FadeIn RHS panel at RIGHT: title "RHS: Bellman equation evaluated at s=6" + skeleton structure $\tfrac14 \sum_a \sum_{s',r} p[\cdot]$ | REVEAL | `place_caption("RHS: …", region="RIGHT")` + RHS skeleton MathTex | 1.4 s |
| 4.2 s | Term-by-term build-up in RHS panel: 4 actions × ~3 transitions each, with heatmap values inserted — `equation_morph` per accumulator step | DERIVE | `equation_morph(rhs_skeleton, rhs_step1)`, …, `equation_morph(rhs_stepN, rhs_final)` | 4.0 s |
| 8.2 s | `Arrow` LHS panel readout → boxed equation's LHS $v_\pi(s)$ token (binding LHS↔equation) | CONNECT | `Arrow(lhs_panel.value, boxed_bellman.lhs_token, color=VALUE_COLOR)` + Create | 0.8 s |
| 9.0 s | `Arrow` RHS panel result → boxed equation's RHS token group (binding RHS↔equation) | CONNECT | `Arrow(rhs_panel.result, boxed_bellman.rhs_group, color=VALUE_COLOR)` + Create | 0.8 s |
| 9.8 s | FadeIn equality caption below: "$\approx 0$ (within $\theta=10^{-10}$)" | REVEAL (RESOLVE — the equation is *checked*) | `place_caption("≈ 0 (within θ=1e-10)", region="below")` | 0.6 s |
| 10.4 s | `trace_vector` from LHS panel value `0.039` → boxed eq LHS $v_\pi(s)$ token | CONNECT | `trace_vector(..., color=VALUE_COLOR)` | 0.8 s |
| 11.2 s | `trace_vector` from RHS panel result `≈ 0.039` → boxed eq RHS group | CONNECT | `trace_vector(..., color=VALUE_COLOR)` | 0.8 s |
| 12.0 s | `self.wait(3.0)` — numerical hold | — | `self.wait(3.0)` | 3.0 s |
| 15.0 s | `self.ingestion_wait(2.5)` (§18) | — | `self.ingestion_wait(2.5)` | 2.5 s |

### Phase S7-P21 — Code panel entry

| t | Animation | Purpose | Helper | run_time |
|---|---|---|---|---|
| 0.0 s | FadeOut LHS panel + RHS panel + memory arrows + equality caption | (cleanup) | `FadeOut(s6_panel_group)` | 1.0 s |
| 1.0 s | `smooth_move_to(boxed_bellman, LEFT_X, scale=0.6)` — equation migrates LEFT | REFRAME | `BaseConceptScene.smooth_move_to(boxed_bellman, LEFT_X, scale=0.6)` | 1.4 s |
| 2.4 s | Heatmap re-enters CENTER from preserved `heatmap_group` (set_opacity 1.0, scale 0.55) | REVEAL (re-entry) | `heatmap_group.animate.set_opacity(1.0).move_to(ORIGIN).scale(0.55)` | 1.4 s |
| 3.8 s | `CodeStepper` panel enters RIGHT (FadeIn + slide-in from off-screen right) with 11-line Python source rendered, all lines initially OPACITY_SECONDARY | REVEAL | `CodeStepper(lines=source_lines, theme=CODE_ACCENT_PALETTE, font_size=22)` at RIGHT_X | 1.6 s |
| 5.4 s | `self.wait(1.5)` | — | `self.wait(1.5)` | 1.5 s |
| 6.9 s | `self.ingestion_wait(2.5)` (§18, scene-wide reposition) | — | `self.ingestion_wait(2.5)` | 2.5 s |

### Phase S7-P22 — Code walkthrough with cross-highlights

11 steps; each follows the cross-highlight matrix (plan §Cross-highlight matrix, lines 154–166) verbatim. Per-step format:

| Step i (rel. t = i × 1.6 s) | `CodeStepper.step(i)` + sync action | Purpose tag | Helper | run_time |
|---|---|---|---|---|
| 0 (0.0 s) | Active line: `env = gym.make("FrozenLake-v1", is_slippery=True)`. Sync: `Indicate` on the entire heatmap frame (CENTER) | CONNECT | `CodeStepper.step(0)` + `cross_highlight_pair(scene, code.line[0], heatmap.frame)` | 1.5 s |
| 1 (1.6 s) | Active line: `pi = np.ones((n_states, n_actions)) / n_actions`. Sync: equiprobable arrows overlay flashes in on heatmap (4 short arrows per cell, POLICY_COLOR, ~0.6 s flash then FadeOut) | CONNECT | `cross_highlight_pair(..., overlay=PolicyArrowGrid(mode="equiprobable", scale=0.5))` | 1.5 s |
| 2 (3.2 s) | Active line: `assert np.allclose(pi.sum(axis=1), 1.0)`. Sync: callout `"1/4+1/4+1/4+1/4=1"` (POLICY_COLOR) above cell 6 in heatmap | CONNECT | `cross_highlight_pair(..., overlay=normalization_callout_mathtex)` | 1.5 s |
| 3 (4.8 s) | Active line: `gamma = 0.99`. Sync: $\gamma$ token in boxed Bellman eq (LEFT) pulses VALUE_COLOR | CONNECT | `Indicate(boxed_bellman.gamma_token, color=VALUE_COLOR)` | 1.5 s |
| 4 (6.4 s) | Active line: `v_prev = np.zeros(n_states)`. Sync: heatmap yellow values dim to BG_GRID for ~0.6 s (visual "this is a guess"), then restore | CONNECT | `heatmap.cells.animate.set_color(BG_GRID).set(run_time=0.6)` then restore | 1.5 s |
| 5 (8.0 s) | Active line: `state = 6`. Sync: state 6 cell in heatmap acquires a spotlight border (STATE_COLOR) | CONNECT | `Indicate(heatmap.cell(6), color=STATE_COLOR, scale_factor=1.1)` | 1.5 s |
| 6 (9.6 s) | Active line: `v_new_6 = 0.0`. Sync: floating yellow `0.0` accumulator appears at top-right of cell 6 (will tick up in step 9) | REVEAL | `MathTex("0.0", color=VALUE_COLOR).next_to(heatmap.cell(6), UR*0.3)` + FadeIn | 1.5 s |
| 7 (11.2 s) | Active line: `for action in range(n_actions):`. Sync: 4 action nodes re-summoned briefly as 4 short pulses around cell 6 (ACTION_COLOR), then FadeOut | CONNECT | `staggered_pulse(action_pulses_around_cell6, color=ACTION_COLOR, stagger=0.15)` | 1.5 s |
| 8 (12.8 s) | Active line: `    for prob, next_state, reward, done in env.unwrapped.P[state][action]:`. Sync: 3 successor cells (2, 7, 10 — for action RIGHT) pulse CODE_ACCENT | CONNECT | `staggered_pulse([heatmap.cell(2), heatmap.cell(7), heatmap.cell(10)], color=CODE_ACCENT, stagger=0.2)` | 1.5 s |
| 9 (14.4 s) | Active line: `        v_new_6 += pi[state, action] * prob * (reward + gamma * v_prev[next_state])`. Sync: **4-way synced pulse** — boxed equation tokens pulse in sequence as their code variable name passes through the active line: `pi[state, action]`↔$\pi(a\mid s)$ POLICY_COLOR; `prob`↔$p(s',r\mid s,a)$ CODE_ACCENT; `reward`↔$r$ REWARD_COLOR; `gamma * v_prev[next_state]`↔$\gamma v_\pi(s')$ VALUE_COLOR. Sequential pulses with 0.3 s stagger. | CONNECT (load-bearing — the triple-link "code variable ↔ equation token ↔ grid region" is the central pedagogical payload of S7) | `SynchronizedFocusGroup([(boxed_bellman.pi_token, POLICY_COLOR), (boxed_bellman.p_token, CODE_ACCENT), (boxed_bellman.r_token, REWARD_COLOR), (boxed_bellman.gamma_v_token, VALUE_COLOR)], stagger=0.3)` | 1.5 s (extended to ~2.0 s if needed for 4 pulses; producer may bump to 2.0 s) |
| 10 (15.9 s or 16.4 s) | Active line: `print(f"...{v_new_6:.6f}")`. Sync: text `"RHS of Bellman at state 6 with v_prev=0: 0.000000"` (CODE_ACCENT) materializes; the `0.000000` value also appears next to cell 6 in heatmap; boxed eq LHS $v_\pi(s)$ token pulses VALUE_COLOR one final time | REVEAL + RESOLVE | `Write(output_text)` + `MathTex("0.000000", color=CODE_ACCENT).next_to(heatmap.cell(6))` + `Indicate(boxed_bellman.lhs_token, color=VALUE_COLOR)` | 3.0 s |
| 18.9 s | `self.ingestion_wait(2.5)` (§18, post-11-step walkthrough) | — | `self.ingestion_wait(2.5)` | 2.5 s |

### Phase S7-P23 — Output and V-03 hand-off setup

| t | Animation | Purpose | Helper | run_time |
|---|---|---|---|---|
| 0.0 s | `place_caption(handoff_3_lines, region="RIGHT")` — 3 lines including "**One sweep is not enough — V-03 will iterate.**" | REVEAL | `place_caption(...)` + `staggered_write` | 2.0 s |
| 2.0 s | Heatmap visibly pulses (`Indicate` on full heatmap with VALUE_COLOR, scale_factor=1.02) — contrast converged vs. zero | REFRAME (focal cue) | `Indicate(heatmap, color=VALUE_COLOR, scale_factor=1.02)` | 1.0 s |
| 3.0 s | `trace_vector` from caption line 1 "Heatmap value: 0.039" → heatmap cell 6 | CONNECT | `trace_vector(..., color=VALUE_COLOR)` | 0.8 s |
| 3.8 s | `trace_vector` from caption line 2 "Code RHS: 0.000000" → the `print` output line in CodeStepper | CONNECT | `trace_vector(..., color=CODE_ACCENT)` | 0.8 s |
| 4.6 s | `trace_vector` from caption line 3 "One sweep is not enough" → boxed eq's $v_\pi(s')$ token (the *RHS* one — the one that depends on $v_\text{prev}$) | CONNECT (RESOLVE M-6) | `trace_vector(..., color=VALUE_COLOR)` | 0.8 s |
| 5.4 s | `self.wait(3.0)` | — | `self.wait(3.0)` | 3.0 s |
| 8.4 s | `self.ingestion_wait(2.5)` (§18) | — | `self.ingestion_wait(2.5)` | 2.5 s |

### Phase S8-P24 — Boxed equation re-centered

| t | Animation | Purpose | Helper | run_time |
|---|---|---|---|---|
| 0.0 s | FadeOut CodeStepper panel, heatmap (full FadeOut now), S7 hand-off caption | (cleanup for final solo) | `FadeOut(s7_visible_group)` | 1.2 s |
| 1.2 s | `smooth_move_to(boxed_bellman, ORIGIN, scale=1.0)` — equation enlarges back to full-frame center | REFRAME (focal return) | `BaseConceptScene.smooth_move_to(boxed_bellman, ORIGIN, scale=1.0)` | 1.6 s |
| 2.8 s | `self.wait(2.0)` | — | `self.wait(2.0)` | 2.0 s |
| 4.8 s | `self.ingestion_wait(2.5)` (§18) | — | `self.ingestion_wait(2.5)` | 2.5 s |

### Phase S8-P25 — `=` → `←` brief morph (V-03 forward-tease)

| t | Animation | Purpose | Helper | run_time |
|---|---|---|---|---|
| 0.0 s | `place_caption("Next: equation → algorithm.", region="ABOVE")` brief reveal | REVEAL | `place_caption(...)` + `Write` | 0.8 s |
| 0.8 s | **Simultaneous triple-morph** (constrained to ≤ 1.5 s total per rl_expert_flag 8): `equation_morph(v_step5_boxed, v_step5_assignment_form)` — `=` token (idx 1) → `\leftarrow`; $v_\pi(s)$ token (LHS) → $v_{k+1}(s)$ with subscript `k+1` in CODE_ACCENT; $v_\pi(s')$ token (RHS) → $v_k(s')$ with subscript `k` in CODE_ACCENT | DERIVE (forward-tease) | `equation_morph(v_step5_boxed, v_step5_assignment_form, run_time=1.5)` | 1.5 s |
| 2.3 s | Hold the assignment form for 1.0 s | — | `self.wait(1.0)` | 1.0 s |
| 3.3 s | `equation_morph(v_step5_assignment_form, v_step5_boxed, run_time=1.0)` — **revert** to V-02 equality form | DERIVE (revert; leaves viewer with equality as the canonical) | `equation_morph(..., run_time=1.0)` | 1.0 s |
| 4.3 s | `trace_vector` from `\leftarrow` (during the 1.0 s hold) → "equation → algorithm" caption — one brief CONNECT | CONNECT | `trace_vector(..., color=CODE_ACCENT)` (overlapping with hold) | 0.8 s |
| 4.3 s | FadeOut "Next: equation → algorithm" caption | (cleanup) | `FadeOut(forward_tease_caption)` | 0.6 s |
| 4.9 s | `self.ingestion_wait(2.5)` (§18) | — | `self.ingestion_wait(2.5)` | 2.5 s |

### Phase S8-P26 — Takeaway and final hold

| t | Animation | Purpose | Helper | run_time |
|---|---|---|---|---|
| 0.0 s | `smooth_move_to(boxed_bellman, UP*1.5, scale=0.75)` — shrink toward upper-CENTER | REFRAME (focal yield to takeaway) | `BaseConceptScene.smooth_move_to(boxed_bellman, UP*1.5, scale=0.75)` | 1.4 s |
| 1.4 s | S5 header FadeOut; `show_header("Coming next: dp_policy_eval", subtitle=None)` (HUMAN-READABLE — V-03 is in library) | (header swap) | `show_header(...)` | 0.8 s |
| 2.2 s | FadeIn takeaway card at lower-CENTER: "$v_\pi$ is the fixed point of the Bellman equation." (VALUE_COLOR, font_size=36) | REVEAL (RESOLVE M-6) | `place_caption(takeaway, region="CENTER_BELOW_EQ", color=VALUE_COLOR, font_size=36)` + `Write` | 1.4 s |
| 3.6 s | FadeIn LEFT flanking caption "V-02: the equation." | REVEAL | `place_caption("V-02: the equation.", region="LEFT")` | 0.8 s |
| 4.4 s | FadeIn RIGHT flanking caption "V-03: the algorithm." | REVEAL | `place_caption("V-03: the algorithm.", region="RIGHT")` | 0.8 s |
| 5.2 s | All highlights deactivate; all primary mobjects stable at OPACITY_PRIMARY (no pulses) | (stable hold) | (no animation; ensure all `updaters` cleared) | — |
| 5.2 s | `self.wait(8.0)` — final extended hold per spec §10.2 | — | `self.wait(8.0)` | 8.0 s |

---

## 6. Camera Shot List

V-02 is a 26-phase video targeting 16–19 min. V-01 settled at 7 shots over 16:54 after QA pruning — V-02 aims for **7–8 shots** of equivalent density. Each shot has a justification rooted in Principle 3 (camera direction used where complexity demands it).

| # | Phase | Shot type | Trigger time (within phase) | Helper | Duration | Purpose / Justification |
|---|---|---|---|---|---|---|
| 1 | S2-P3 | `zoom_to` π definition (modest zoom-in, scale 0.85 — equation is already large at font 48, but a small camera lean-in emphasizes the solo) | 1.8 s after phase start (as `staggered_write` begins) | `zoom_to(self, pi_def, scale=0.85)` | 1.2 s | Principle 3: a single equation derivation full-frame reveal earns a small inward camera commitment so the viewer's eye is held on the equation. |
| 2 | S2-P3 | `zoom_reset` | end of phase, before S2-P4 transition | `zoom_reset(self, run_time=1.4)` | 1.4 s | Return to wide for the side-by-side policy grids that need both LEFT and RIGHT visible. |
| 3 | S5-P13 | `zoom_to` backup diagram | 2.0 s after phase start (as root + action layer appears) | `zoom_to(self, backup_diagram, scale=0.7)` | 1.5 s | Principle 3: the backup diagram is the load-bearing geometry for the entire derivation. A modest zoom-in commits the viewer's eye for the 7-phase S5 sequence. |
| 4 | S5-P14 | `zoom_to` LEFT equation panel + held zoom through P15–P18 | end of P14 morph (5.4 s in) | `zoom_to(self, VGroup(equation_panel, backup_diagram), scale=0.65)` | 1.5 s | Principle 3 (≥ 8 s single-equation derivation): the 5-step morph chain runs ~30 s of total wait+animation; the camera holds at a tight 2-panel framing throughout. |
| 5 | S5-P19 | `zoom_reset` then immediate slow zoom to boxed equation | at FadeOut of S5 elements (0.0 s) → 1.2 s for solo zoom-in | `zoom_reset(self, run_time=1.4)` then `zoom_to(self, boxed_bellman, scale=0.8)` | 1.4 + 1.5 = 2.9 s | Principle 3: the boxed equation is the destination — slow reset then deliberate inward commitment lands the punchline. Note: this is the ONE place we violate the "no zoom_to+zoom_reset within 4 s" guidance — but the intervening `equation_morph` (1.8 s) and `wait(3.0)` (3.0 s) total 4.8 s, satisfying the constraint by margin. |
| 6 | S7-P21 | `zoom_reset` | 1.0 s after phase start (after S6 cleanup) | `zoom_reset(self, run_time=1.6)` | 1.6 s | Principle 3 (any phase introducing a new wide-layout element): the CodeStepper enters RIGHT, requiring full canvas width. |
| 7 | S7-P22 | `pan_to_follow` to active code line + matched heatmap region per step | starts at step 0 (code line 0); continuous through 11 steps | `pan_to_follow(self, active_pair_sequence, run_time=1.0)` per step transition | continuous through 11 steps (~17 s total) | Principle 3: the sprite-equivalent (the per-step code/equation/heatmap synced trio) traverses the canvas. A subtle continuous pan keeps the active trio visually centered without flinching. Note: this is not a sharp zoom — `pan_to_follow` with a soft easing keeps the wide layout intact. |
| 8 | S8-P24 | `zoom_to` boxed Bellman equation (return to S5-P19's framing) | end of `smooth_move_to` (2.8 s) | `zoom_to(self, boxed_bellman, scale=0.8)` | 1.4 s | Principle 3 + Principle 1 REFRAME: the equation re-enters full-frame after Segments 6–7 — the camera commits inward to re-establish it as the central object before the final morph. |

**Shot density audit:** 8 shots over ~17 min runtime = 1 shot per ~2 min. This is the same density as V-01 (7 shots / 17 min). No shot violates the "no zoom_to + zoom_reset within 4 s" rule (the S5-P19 sequence is bridged by 4.8 s of intervening animation/wait). The S7-P22 `pan_to_follow` runs continuously rather than as a discrete cut — counts as one shot for budget purposes but operates as a slow smooth path.

---

## 7. Sprite-Math Binding Matrix

Every phase with motion AND math has a binding row (Principle 4; QA F50). For V-02, the "sprite" concept is broader than V-01's agent — here the moving elements are heatmap-cell highlights, backup-diagram node pulses, and code-line advances. The binding always ties motion + equation token + (when present) code line.

| Phase | Sprite / motion source | Equation token(s) that highlight simultaneously | Code line that highlights | Helper | Color binding |
|---|---|---|---|---|---|
| S2-P5 | Spotlight Squares on cell 6 of Policy A and Policy B grids appear | $\sum_a \pi(a\mid s)$, each "$\tfrac14$" token | (no code on screen) | `cross_highlight_pair(scene, eq_token, cell_6_spotlight)` per token | POLICY_COLOR |
| S3-P7 | Heatmap cells fade in (Manhattan order from goal) | $v_\pi(s)$ token in LEFT eq panel pulses on each cell completion | (no code) | `cross_highlight_pair(scene, v_def_token, current_fading_cell)` per cell wave | VALUE_COLOR |
| S3-P8 | State 14 cell enlarges + spotlights | $v_\pi(s)$ token (LEFT eq, LHS); $G_t$ token (LEFT eq, RHS) | (no code) | `cross_highlight_pair(scene, v_def_token, cell_14)` + `SpriteActionBinding(sprite=cell_14_spotlight, eq_tokens=[v_token, G_token])` | VALUE_COLOR |
| S3-P9 | Goal cell (state 15) acquires green `+1.0` marker AND yellow `v=0` label simultaneously | (no equation tokens — this is a geometric M-2 cure, the green-yellow pair is itself the binding) | (no code) | `cross_highlight_pair(scene, goal_reward_marker, goal_value_label)` — the pair-highlight IS the teaching device | REWARD_COLOR ↔ VALUE_COLOR (cross-color binding) |
| S4-P11 | 4 q-bars draw on cell 14 (staggered L→D→R→U) | $q_\pi(s,a)$ token in RIGHT eq panel | (no code) | `SpriteActionBinding(sprite=bar_i, action=action_i, eq_tokens=[q_token])` per bar | VALUE_COLOR (bars) + ACTION_COLOR (labels) |
| S4-P12 | Bracket-arrow grows from 4-bar bracket → cell-14 v-value label | Each $q_\pi(14, a)$ token in `link_state14` MathTex | (no code) | `SpriteActionBinding(sprite=bracket_arrow, action="aggregate", eq_tokens=[q_tokens_4])` + `cross_highlight_pair(scene, v_pi_14_token, heatmap_cell_14_label)` | VALUE_COLOR |
| S5-P14 | Backup-diagram root node pulses | $v_\pi(s)$ token (LEFT step-1 eq, LHS) | (no code) | `cross_highlight_pair(scene, v_pi_s_token, root_node)` | VALUE_COLOR |
| S5-P15 | One root-to-action-RIGHT edge labels `R_{t+1}`; subtree braces `G_{t+1}` | $R_{t+1}$ and $G_{t+1}$ tokens (LEFT step-2 eq) | (no code) | `cross_highlight_pair(scene, R_token, edge_label)` + `cross_highlight_pair(scene, G_token, subtree_brace)` | REWARD_COLOR + VALUE_COLOR |
| S5-P16 | 4 action nodes pulse `POLICY_COLOR → ACTION_COLOR` (staggered) | $\sum_a$ token + $\pi(a\mid s)$ token (LEFT step-3 eq) | (no code) | `SpriteActionBinding(sprite=action_node_i, action=action_i, eq_tokens=[sum_a, pi_token])` per node + `cross_highlight_pair(scene, sum_a, VGroup(action_nodes))` | POLICY_COLOR → ACTION_COLOR |
| S5-P17 | 3 transition leaves under RIGHT pulse `CODE_ACCENT` (p labels) + `REWARD_COLOR` (r labels) | $\sum_{s',r}$, $p(s',r\mid s,a)$, $r$ tokens (LEFT step-4 eq) | (no code) | `SpriteActionBinding(sprite=leaf_j, action="transition", eq_tokens=[sum_sr, p_token, r_token])` per leaf + `cross_highlight_pair(scene, sum_sr, VGroup(leaves))` | CODE_ACCENT + REWARD_COLOR |
| S5-P18 | 3 transition leaves relabel from $\mathbb{E}_\pi[G_{t+1}\mid \cdot]$ → $v_\pi(s')$ | $v_\pi(s')$ token (LEFT step-5 eq, in the RHS) | (no code) | `cross_highlight_pair(scene, v_pi_s_prime_token, VGroup(relabeled_leaves))` + 3 × `trace_vector` per leaf | VALUE_COLOR |
| S6-P20 | LHS-panel value `0.039` and RHS-panel result `≈ 0.039` materialize | Boxed eq LHS $v_\pi(s)$ token + RHS group | (no code) | `cross_highlight_pair(scene, boxed_lhs, lhs_panel_value)` + `cross_highlight_pair(scene, boxed_rhs, rhs_panel_result)` | VALUE_COLOR |
| S7-P22 step 0 | `Indicate` on full heatmap frame | (no eq token bound this step) | `env = gym.make(...)` | `cross_highlight_pair(scene, code.lines[0], heatmap.frame)` | (frame chrome) |
| S7-P22 step 1 | Equiprobable arrow overlay flashes on heatmap | $\pi(a\mid s)$ token in boxed eq | `pi = np.ones(...) / n_actions` | `cross_highlight_pair(scene, code.lines[1], heatmap_overlay)` + token highlight | POLICY_COLOR |
| S7-P22 step 2 | Normalization callout above cell 6 | $\sum_a \pi(a\mid s)$ token group | `assert np.allclose(pi.sum(axis=1), 1.0)` | `cross_highlight_pair(scene, code.lines[2], normalization_callout)` | POLICY_COLOR |
| S7-P22 step 3 | (no grid motion; eq-token pulse only) | $\gamma$ token in boxed eq | `gamma = 0.99` | `cross_highlight_pair(scene, code.lines[3], boxed_bellman.gamma_token)` | VALUE_COLOR |
| S7-P22 step 4 | Heatmap dims to BG_GRID briefly | $v_\pi(s')$ token (RHS of boxed eq — the one $v_\text{prev}$ controls) | `v_prev = np.zeros(n_states)` | `cross_highlight_pair(scene, code.lines[4], heatmap_dim_pulse)` + token pulse | VALUE_COLOR |
| S7-P22 step 5 | Cell-6 spotlight (STATE_COLOR) | $s$ token (boxed eq LHS subscript) | `state = 6` | `cross_highlight_pair(scene, code.lines[5], heatmap.cell(6))` | STATE_COLOR |
| S7-P22 step 6 | Floating yellow `0.0` accumulator above cell 6 | $v_\pi(s)$ token (boxed eq LHS) | `v_new_6 = 0.0` | `cross_highlight_pair(scene, code.lines[6], accumulator_marker)` | VALUE_COLOR |
| S7-P22 step 7 | 4 action pulses around cell 6 (ACTION_COLOR) | $\sum_a$ token (boxed eq) | `for action in range(n_actions):` | `SpriteActionBinding(sprite=action_pulse_i, action=action_i, eq_tokens=[sum_a])` per pulse | ACTION_COLOR |
| S7-P22 step 8 | 3 successor cells (2, 7, 10) pulse CODE_ACCENT | $\sum_{s',r} p$ token group | `for prob, next_state, reward, done in env.unwrapped.P[state][action]:` | `SpriteActionBinding(sprite=successor_pulse_j, action="transition", eq_tokens=[sum_sr, p_token])` per pulse | CODE_ACCENT |
| S7-P22 step 9 | 4 sequential token pulses on boxed eq (POLICY → CODE_ACCENT → REWARD → VALUE) timed to code-variable substring positions | $\pi(a\mid s)$, $p(s',r\mid s,a)$, $r$, $\gamma v_\pi(s')$ (sequential) | `v_new_6 += pi[state, action] * prob * (reward + gamma * v_prev[next_state])` | `SynchronizedFocusGroup([(pi_token, POLICY_COLOR), (p_token, CODE_ACCENT), (r_token, REWARD_COLOR), (gamma_v_token, VALUE_COLOR)], stagger=0.3)` — the **load-bearing** code-equation-geometry triple link of the entire video | 4-color sequential (per token) |
| S7-P22 step 10 | `0.000000` output materializes; LHS token pulses | $v_\pi(s)$ token (boxed eq LHS) | `print(f"...{v_new_6:.6f}")` | `cross_highlight_pair(scene, code.lines[10], output_text)` + final LHS pulse | VALUE_COLOR + CODE_ACCENT |
| S7-P23 | Heatmap pulses (Indicate on full grid) | (no token bound; the contrast caption resolves M-6) | (code panel finished) | `cross_highlight_pair(scene, handoff_caption_line_3, boxed_bellman.v_pi_s_prime_token)` — the RHS $v_\pi(s')$ is what equals $v_\text{prev}=0$ and produces the gap | VALUE_COLOR |
| S8-P25 | 3 simultaneous token morphs (`=`→`←`, LHS $v_\pi(s)$→$v_{k+1}(s)$, RHS $v_\pi(s')$→$v_k(s')$) | All 3 morphing tokens | (no code) | `equation_morph(v_step5_boxed, v_step5_assignment_form, run_time=1.5)` + `cross_highlight_pair(scene, arrow_token, forward_tease_caption)` | CODE_ACCENT (the subscripts `k+1`, `k`) |

**Audit:** every phase with motion + math has at least one binding row. The S7-P22 step 9 row is the climactic load-bearing binding — four tokens, four colors, one code line, one moment. This is the V-02 equivalent of V-01's "agent moves RIGHT → r appears" binding.

---

## 8. trace_vector Source-Target Pairs (per equation token first appearance)

Every equation token that has a geometric referent on canvas gets a `trace_vector` at first appearance (Principle 4; ties symbol to geometry). One pair per row.

| Phase | Equation token (MathTex component index) | Source geometry on canvas | Color | Helper |
|---|---|---|---|---|
| S2-P4 | "$\pi(\text{RIGHT}\mid s)=1$" caption (composite) | one arrow on Policy A's cell 6 | POLICY_COLOR | `trace_vector(scene, caption_A, arrow_on_A_cell6)` |
| S2-P4 | "$\pi(a\mid s)=\tfrac14$" caption (composite) | the 4-arrow bundle on Policy B's cell 6 | POLICY_COLOR | `trace_vector(scene, caption_B, arrow_bundle_on_B_cell6)` |
| S2-P5 | $\sum_a$ token (normalization eq idx 0) | the 4-arrow bracket above Policy B's cell 6 | POLICY_COLOR | `trace_vector(scene, sum_a, arrow_bracket_B_cell6)` |
| S2-P5 | Each "$\tfrac14$" token (idx 2, 4, 6, 8) | the corresponding arrow on Policy B's cell 6 | POLICY_COLOR | 4 × `trace_vector(scene, quarter_token_i, arrow_i)` (staggered 0.2 s) |
| S3-P7 | $v_\pi(s)$ token (`v_def` idx 0) | heatmap cell 14 label "0.434" (brightest cell, the anchor) | VALUE_COLOR | `trace_vector(scene, v_def[0], heatmap.cell(14).label)` |
| S3-P7 | $G_t$ token (`v_def` idx 7) | heatmap cell 14 label (via the $G_t = $ expected-return-on-the-grid binding) | VALUE_COLOR | `trace_vector(scene, v_def[7], heatmap.cell(14).label)` |
| S3-P8 | "Reward at state 14: 0" caption line | floating `r=0` marker above cell 14 | REWARD_COLOR | `trace_vector(scene, caption_line_1, r0_marker)` |
| S3-P8 | "Value at state 14: 0.434" caption line | cell-14 yellow label | VALUE_COLOR | `trace_vector(scene, caption_line_2, cell_14.label)` |
| S3-P9 | "Arriving at the goal: reward +1.0 (green)" caption line | green `+1.0` marker above cell 15 | REWARD_COLOR | `trace_vector(scene, caption_line_1, goal_reward_marker)` |
| S3-P9 | "Value at the goal: 0 (yellow)" caption line | yellow `v_π(15)=0` label inside cell 15 | VALUE_COLOR | `trace_vector(scene, caption_line_2, goal_value_label)` |
| S4-P11 | $q_\pi(s, a)$ token (`q_def` idx 0) | each of 4 q-bars on cell 14 | VALUE_COLOR | 4 × `trace_vector(scene, q_def[0], bar_i)` (staggered 0.3 s) |
| S4-P12 | Each $q_\pi(14, \cdot)$ token in `link_state14` (idx 7, 9, 11, 13) | corresponding bar (L/D/R/U) | VALUE_COLOR | 4 × `trace_vector(scene, q_token_i, bar_i)` (staggered 0.25 s) |
| S5-P13 | $\pi(R\mid 6)$ branch label (diagram) | one arrow in lower-right equiprobable-policy thumbnail (faint) | POLICY_COLOR | `trace_vector(scene, branch_label_R, thumbnail_arrow_R)` |
| S5-P13 | $p(2\mid 6, R)$ leaf label | state 2 in thumbnail (faint) | CODE_ACCENT | `trace_vector(scene, p_label_2, thumbnail_cell_2)` |
| S5-P13 | $p(7\mid 6, R)$ leaf label | state 7 (hole) in thumbnail | CODE_ACCENT | `trace_vector(scene, p_label_7, thumbnail_cell_7)` |
| S5-P14 | $v_\pi(s)$ token (`v_def_step1` idx 0) | root node label "$v_\pi(6)$" in backup diagram | VALUE_COLOR | `trace_vector(scene, v_def_step1[0], root_node_label)` |
| S5-P15 | $R_{t+1}$ token (`v_step2` idx 4) | labeled edge (root → action-RIGHT) in diagram | REWARD_COLOR | `trace_vector(scene, v_step2[4], edge_R_label)` |
| S5-P15 | $G_{t+1}$ token (`v_step2` idx 7) | braced subtree under action-RIGHT | VALUE_COLOR | `trace_vector(scene, v_step2[7], subtree_brace)` |
| S5-P16 | $\sum_a$ token (`v_step3` idx 2) | the 4 action nodes (as VGroup) | POLICY_COLOR | `trace_vector(scene, v_step3[2], VGroup(action_nodes))` |
| S5-P16 | $\pi(a\mid s)$ token (`v_step3` idx 3) | the 4 π branch labels (as VGroup) | POLICY_COLOR | `trace_vector(scene, v_step3[3], VGroup(pi_branch_labels))` |
| S5-P17 | $\sum_{s',r}$ token (`v_step4` idx 4) | the 3 transition leaves under RIGHT (as VGroup) | CODE_ACCENT | `trace_vector(scene, v_step4[4], VGroup(transition_leaves_R))` |
| S5-P17 | $p(s',r\mid s,a)$ token (`v_step4` idx 5) | the 3 p labels on leaf edges (as VGroup) | CODE_ACCENT | `trace_vector(scene, v_step4[5], VGroup(p_labels_R))` |
| S5-P17 | $r$ token (`v_step4` idx 7) | any single leaf reward label (e.g., leaf for state 7) | REWARD_COLOR | `trace_vector(scene, v_step4[7], leaf_7.r_label)` |
| S5-P18 | $v_\pi(s')$ token (`v_step5` idx 10) | each of the 3 relabeled leaves: $v_\pi(2), v_\pi(7)=0, v_\pi(10)$ | VALUE_COLOR | 3 × `trace_vector(scene, v_step5[10], leaf_label_i)` (staggered 0.3 s) |
| S6-P20 | $v_\pi(s)$ LHS token (boxed eq) | LHS panel value `0.039` | VALUE_COLOR | `trace_vector(scene, boxed_lhs_token, lhs_panel.value)` |
| S6-P20 | $\sum_a \pi \sum_{s',r} p [r + \gamma v_\pi(s')]$ token group (boxed eq RHS) | RHS panel result `≈ 0.039` | VALUE_COLOR | `trace_vector(scene, boxed_rhs_group, rhs_panel.result)` |
| S7-P23 | (caption "Heatmap value: 0.039") | heatmap cell 6 (yellow label, recalled from Segment 3 binding) | VALUE_COLOR | `trace_vector(scene, handoff_line_1, heatmap.cell(6).label)` |
| S7-P23 | (caption "Code RHS: 0.000000") | print output line in CodeStepper | CODE_ACCENT | `trace_vector(scene, handoff_line_2, code.output_line)` |
| S7-P23 | (caption "One sweep is not enough") | boxed equation's RHS $v_\pi(s')$ token (the *RHS* one — the one that depends on $v_\text{prev}$) | VALUE_COLOR | `trace_vector(scene, handoff_line_3, boxed_bellman.v_pi_s_prime_token)` |
| S8-P25 | `\leftarrow` token (in `v_step5_assignment_form`) | "Next: equation → algorithm" caption (top) | CODE_ACCENT | `trace_vector(scene, leftarrow_token, forward_tease_caption)` |

**Audit:** every equation token introduced with a geometric anchor has a `trace_vector` at first appearance. Tokens introduced in solo-frame phases (S2-P3, S3-P6, S4-P10, S5-P19, S8-P24) have NO trace_vector because there is no on-canvas geometry to bind to during those phases — they are the abstract reveals, and binding happens in the immediately-following layout-restore phases (S2-P4, S3-P7, S4-P11, S6-P20, S8-P25). Tokens that are pure morphs from earlier tokens (e.g., the $\pi(a\mid s)$ token migrating from `v_step3` to `v_step4`) reuse their original anchor via `TransformMatchingTex`.

---

## 9. Hand-off Notes for the Manim Expert

**Reusable mobject instances (do not duplicate; preserve via Group):**

1. **`v_def`** (S3-P6 `pi` definition `MathTex` instance) — reuse verbatim in S5-P14 step-1 equation. Create once at S3-P6, hide via `Group` opacity at end of S4-P12, re-introduce as `v_def_step1` at S5-P14 (same component array, same colors — the TransformMatchingTex chain S5-P14→P15→P16→P17→P18→P19 depends on this).
2. **`equiprobable_grid_group`** (S2-P4 Policy B `PolicyArrowGrid`) — preserve as hidden Group at end of S2-P5; re-enter at S5-P13 as the lower-right BACKGROUND thumbnail (set_opacity(0.17)); fully FadeOut at end of S5-P18.
3. **`heatmap_group`** (`ValueHeatmap` instantiated at S3-P7) — preserve as hidden Group at end of S4-P12; re-enter at S7-P21 (set_opacity(1.0), scale=0.55, CENTER); full FadeOut at end of S7-P23.
4. **`boxed_bellman`** (the Boxed Bellman equation, created at S5-P19) — this is the most-traveled mobject in the scene. Survives S5-P19 → S6-P20 → S7-P21 → S7-P22 → S7-P23 → S8-P24 → S8-P25 → S8-P26. **Do NOT re-create at S8-P24** — the same instance migrates via `smooth_move_to`. The S8-P25 morph (`equation_morph(boxed_bellman, v_step5_assignment_form)` then revert) operates on this instance.

**Helper API notes:**

- The `BackupDiagram` helper from `manim_service/scenes/rl_visuals.py` may need extension to accept `transition_branches={"RIGHT": [(2, 1/3, 0), ...]}` for asymmetric per-action transition layouts. If the existing helper does not support this, escalate to the Producer rather than improvising (see Producer collaboration rules in produce-video.md). The choreo presumes the helper exists with that signature; if it does not, the Manim Expert may use a hand-built VGroup of nodes + edges following the same color and geometry conventions.
- The `ActionBarChart(state=14, ..., edge_attached=True)` parameter `edge_attached=True` is a new mode (V-01 used vertical bars; here we want 4 bars on cell edges). If the helper does not yet support this, fall back to 4 separate `Rectangle` bars manually placed on cell-14 edges using `next_to(cell_14, LEFT|RIGHT|UP|DOWN, buff=0.05)`; preserve VALUE_COLOR fills and ACTION_COLOR action labels.
- The `SynchronizedFocusGroup` helper for S7-P22 step 9 is a new pattern — synchronized 4-color token pulses keyed to substring positions within a single code line. If not implemented, use 4 sequential `Indicate` calls with `stagger=0.3` and explicit `run_time=0.4` each, totaling ~1.5 s for the 4-color sweep. The narration timing depends on this — confirm with Voice & BGM Agent during their pass on S7-P22.
- `cell_fade_in_sequence(manhattan_order=True)` for the heatmap reveal at S3-P7: if not implemented, use a Python loop computing manhattan distance from cell 15 and emit `FadeIn` per cell with `lag_ratio=0.15` across the 16 cells.
- `equation_morph(...)` calls in S5-P14 through S5-P19 form a **TransformMatchingTex chain**. The Manim Expert MUST ensure that shared tokens between consecutive steps (`v_pi(s)`, `=`, `\sum_a`, `\pi(a\mid s)`, etc.) are referenced by the SAME MathTex component indices across `v_def_step1`, `v_step2`, `v_step3`, `v_step4`, `v_step5` so the morph animates by matching token text rather than by index-fall-through. The plan.md component arrays in §S5-P14 through §S5-P18 are constructed for exactly this.

**Numerical claims:**

Every heatmap value, every q-value, and every backup-diagram p-value carries a `# NUMERIC_CLAIM` comment in the Manim source. The Technical Validator runs `iterative_policy_evaluation(env, pi_equiprobable, gamma=0.99, theta=1e-10)` to refine these before render. The choreo's bindings (trace_vector targets, cross_highlight pairs) reference these values symbolically (e.g., "heatmap cell 14 label") and do NOT hard-code the numeric strings — the source-of-truth is the computed array.

**Sprite assets (mandatory, no fallbacks):**

- All FrozenLake tile renderings use `frozenlake_frame(soft_frame=True)` per the plan §Gymnasium Assets Required section. NO raw `ImageMobject` calls.
- If `MISSING_ASSETS` is reported by the asset-verification command, halt and report to Producer per spec §8.1.

**Camera:**

The S5 sustained zoom (shots 3–5 above) holds tight framing through the 5-step derivation. During this stretch the equation panel and backup diagram are the only PRIMARY mobjects — peripheral cleanup is unnecessary because the camera frame excludes the canvas edges. The `zoom_reset` at S5-P19 is the only camera-distance reset until S7-P21.

**Pacing budget reconciliation:**

Plan.md estimates ~129 s of pure waits across 26 phases. The choreo above adds ~95 s of animation `run_time` (sum of Manim helper run_times in section 5). Total animation+wait floor: ~224 s = ~3.7 min. The remaining 12–15 min (~720–900 s of expected runtime) is narration-coupled — Voice & BGM Agent will fix the actual durations after the dev render. The Manim Expert renders at 480p dev quality for QA; final 720p render is gated by the Producer per produce-video.md Step 14.

**STYLE_BIBLE compliance recap:**

- §11 ("dynamics function" exception) — the term appears at most twice: S1-P1 narration (implicit, V-01 callback) and S5-P17 narration (explicit, "the environment's dynamics function $p(s', r \mid s, a)$"). The Manim Expert does not control narration; this is a Voice & BGM Agent enforcement point.
- §15 (cross-highlight matrix) — fully implemented in S7-P22 (11 rows in the plan, 11 binding entries in section 7 above).
- §16 (reserved-hemisphere layout) — every phase respects LEFT/CENTER/RIGHT assignments; migrations use `smooth_move_to` per the plan's Migration Rules.
- §17 (`smooth_move_to` min run_time 1.2 s for distance > 2 units) — every smooth_move_to row in section 5 has run_time ≥ 1.2 s.
- §18 (`ingestion_wait(2.5)` after every morph and scene-wide reposition) — every phase that has a morph or full-canvas migration has an explicit `self.ingestion_wait(2.5)` row at the end. Audit: S1-P2, S2-P3, S2-P5, S3-P6, S3-P7, S3-P9, S4-P10, S4-P11, S4-P12, S5-P13, S5-P15, S5-P16, S5-P17, S5-P18, S5-P19, S6-P20, S7-P21, S7-P22, S7-P23, S8-P24, S8-P25 — all have ingestion_wait. S1-P1, S2-P4, S5-P14, S8-P26 do NOT — these are pure-reveal or final-hold phases (no morph + no scene-wide reposition). Per §18, ingestion_wait is required ONLY after morph or scene-wide reposition; these omissions are correct.
- §23 (explicit FadeOut on phase transitions) — every cleanup row in section 5 uses `FadeOut(group)` or per-element `FadeOut`. The Element Lifecycle Matrix (section 4) flags every transition Phase OUT.
- §33.1 (single focal point at OPACITY_PRIMARY) — section 3 (Cognitive Load Budget) enforces ≤ 4 primary mobjects per frame; most phases sit at 1–2 primary. Cross-highlight pairs (S3-P9 green-yellow goal cell) and contrast pairs (S2-P4 dual policy grids) count as one or noted multi-primary respectively.
- §33.2 (full-frame solo equation reveals) — S2-P3, S3-P6, S4-P10, S5-P19, S8-P24 are the five mandated solo reveals; each held ≥ 2.0 s with ingestion_wait(2.5) on exit (except S5-P19 which has 3.0 s solo hold per spec §10.2).

---

**End of choreo.md.** Hand-off to Technical Validator (Step 6 in produce-video.md). All Six Principles applied; all STYLE_BIBLE §§13–28 constraints honored; all rl_expert_flag binding constraints from plan.md §RL Expert collaboration notes preserved.
