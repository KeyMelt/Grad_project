# Choreography — dp_policy_eval (v3)

**plan.md reference:** manim_service/concept_videos/dp_policy_eval_plan.md
**Visual Director:** visual-director (skill)
**Date:** 2026-05-20
**Series position:** 1 of 6
**Manim class:** `PolicyEvaluationConcept`

---

## 1. Scientific Rigor

The video claims (i) that the iterative Bellman expectation update
converges to the value function v_π of a *given* policy π under
guaranteed termination or γ < 1, (ii) that on slippery FrozenLake-v1
with γ = 0.99 and the equiprobable policy this converges to
V[14] ≈ 0.434 (the cell adjacent to the goal under "going RIGHT"
slips to goal with prob 1/3), and (iii) that the deterministic
"always LEFT" policy produces v_π ≡ 0 because it never reaches the
goal. The evidence is on-screen iterative sweep of the
EnvironmentValueHeatmap across V_0 → V_71, plus the side-by-side
contrast with the LEFT-policy heatmap. The qualifications carried
explicitly in narration: these specific values depend on (a) the
slippery dynamics, (b) γ = 0.99, (c) the equiprobable policy. A
deterministic FrozenLake variant, a different γ, or a different
policy would yield different numbers.

## 2. Pedagogical Strategy

**Primary pattern:** Concrete-to-abstract.

**Why this pattern fits:** Policy evaluation introduces the iterative
Bellman expectation backup. Starting from the actual FrozenLake env
the learner already saw in the coding exercise — the same elf, the
same ice tiles, the same holes — and only later writing the symbolic
update earns the equation through the visual experience. The
v3 rewrite specifically keeps the env grid on screen as the single
spine of the scene: there is no abstract Bellman-tree diagram in
empty space (that was the v2 failure mode the user flagged at 1:01).

**Misconception this strategy defeats:** *"Policy evaluation finds
the best policy."* Phase 6's contrast pair (equiprobable π vs LEFT-only
π) on two side-by-side env-heatmaps makes the misconception visually
impossible — same algorithm, two policies, two manifestly different
value functions.

## 3. Cognitive Load Budget (≤ 4 primary mobjects per frame)

| Phase | Start | Middle | End |
|---|---|---|---|
| 1 | header + heatmap + caption (3) | header + heatmap + elf + caption (4) | header + heatmap + caption (3) |
| 2 | heatmap + focal_halo + caption (3) | heatmap + focal_halo + outcome_arrows_group + r+γv_label (4) | heatmap + caption (2) |
| 3 | heatmap + v_iter + caption (3) | heatmap + v_iter + active_trace_vector + caption (4) | heatmap + v_iter (held PRIMARY) (2) |
| 4 | heatmap + v_iter (SECONDARY) + k/Δ_label + caption (3) | heatmap + elf + active_eq_block + caption (4) | heatmap + k/Δ_label + caption (3) |
| 5 | heatmap (SECONDARY) + code_panel + active_eq_block + caption (3) | code_panel + active_code_line + active_eq_block + heatmap_cell_highlight (4) | code_panel + heatmap (3) |
| 6 | hm_uniform + title_a + hm_left + title_b (4) | both heatmaps + caption (3) | hm_uniform + caption (2) |
| 7 | hm_uniform + caption (2) | hm_uniform + delta_plot + θ_line + caption (4) | hm_uniform + delta_plot + caption (3) |
| 8 | pill + caption (2) | pill + heatmap + caption (3) | pill + caption (2) |

---

## 4. Element Lifecycle Matrix

| Mobject | Phase IN | Visible during | Phase OUT | Re-enters at |
|---|---|---|---|---|
| Header (title + subtitle) | 1 | 1 only | end of Phase 1 | never |
| `heatmap` (EnvironmentValueHeatmap, the spine) | 1 | **1–8 continuously** (single instance) | scene end | n/a (never leaves) |
| Phase-1 caption stream | 1 | 1 only | end of Phase 1 | swapped |
| Elf agent sprite (Phase 1 walker, via heatmap.place_agent) | 1 | 1 only | end of Phase 1 via heatmap.remove_agent | re-instantiated in Phase 4 |
| Focal-cell halo (state 14) | 2 | 2–3 (acts as trace_vector source) | end of Phase 3 (after traces fire) | never |
| `s` label MathTex | 2 | 2–3 | end of Phase 3 | never |
| RIGHT action arrow + `a` label | 2 | 2 only | end of Phase 2 | never |
| Three outcome arrows (in-grid, to states 2, 7, 10) + 1/3 prob labels | 2 | 2 only | end of Phase 2 | never |
| `r + γ v_π(s')` floating annotation | 2 | 2–3 (trace_vector source for r and v_k) | end of Phase 3 | never |
| `v_iter` MathTex | 3 | 3–5 | end of Phase 5 | never |
| Token-trace annotations | 3 | brief during writes | dismissed by trace_vector's auto-fade | never |
| `k_label`, `Δ_label` | 4 | 4–7 (Δ plot in Phase 7 uses them as context) | end of Phase 7 | never |
| Elf evaluator sprite (Phase 4 binding demo) | 4 | 4 only (bound to v_iter highlight blocks) | end of binding demo via heatmap.remove_agent | never |
| `CodeStepper` panel | 5 | 5 only | end of Phase 5 | never |
| Phase 6 second heatmap (`hm_left`) | 6 | 6 only | end of Phase 6 | never |
| Phase 6 titles "π = equiprobable" / "π = always LEFT" | 6 | 6 only | end of Phase 6 | never |
| Δ-vs-k plot (axes + curve + θ + cross_dot) | 7 | 7 only | end of Phase 7 | never |
| Closing pill | 8 | 8 only | scene end | never |

The heatmap never leaves. The elf appears in Phases 1 and 4 only. The
abstract Bellman fork from v2 does NOT exist in this choreography.

---

## 5. Motion Choreography (per-phase, every animation tagged)

### Phase 1 — motivation

| t | Animation | Tag | Helper |
|---|---|---|---|
| 0.0 | `show_header(...)` + FadeIn Phase-1 caption | REVEAL | BaseConceptScene |
| 2.5 | FadeIn heatmap CENTER (all ice tiles + holes + goal visible, no value overlays yet) | REVEAL | EnvironmentValueHeatmap |
| 5.0 | `heatmap.place_agent(state=0, direction="down")` | REVEAL | `place_agent` |
| 7.0 | sequence of 4–5 `heatmap.move_agent(state=..., direction=...)` calls with 0.9s each + wait 0.6s | RESOLVE (showing "follow π") | `move_agent` |
| ~16 | caption swap to "how good is each state under π?" | REVEAL | place_caption + FadeOut/FadeIn |
| ~21 | `ingestion_wait(2.5)` then `heatmap.remove_agent()` | (cleanup) | `remove_agent` |
| ~25 | end-of-phase: FadeOut header + Phase-1 caption (heatmap STAYS) | (cleanup) | FadeOut |

### Phase 2 — slippery outcomes in-grid

| t | Animation | Tag | Helper |
|---|---|---|---|
| 0.0 | `mark_phase("slippery_outcomes")` | (system) | |
| 0.0 | smooth_move_to: leave heatmap centered (no move yet — we're working IN the grid) | (no-op) | |
| 0.5 | Create SurroundingRectangle around focal cell (state 14, the row/col=(3,2)) — STATE_COLOR halo | REVEAL | SurroundingRectangle + Create |
| 2.0 | Write `s` MathTex above focal cell | REVEAL | Write |
| 4.0 | FadeIn ACTION_COLOR arrow from focal cell pointing RIGHT + Write `a = RIGHT` label | REVEAL | FadeIn + Write |
| 7.0 | LaggedStart of 3 short arrows from focal cell to actual neighbouring outcome cells (states 2, 7, 10) + each cell halos faintly + each arrow shows `1/3` label | REVEAL | LaggedStart of FadeIn |
| 12.0 | Write the floating `r + γ v_π(s')` annotation next to the focal-cell halo | REVEAL | Write |
| 14.0 | `ingestion_wait(2.5)` | (ingestion) | |
| 16.5 | FadeOut the 3 outcome arrows + 1/3 labels + RIGHT action arrow + `a` label (KEEP focal halo + `s` label + r+γv annotation for Phase 3 traces) | (cleanup, partial) | FadeOut |
| 18.5 | end-of-phase: caption swap | REVEAL | |

### Phase 3 — earn the iterative equation

| t | Animation | Tag | Helper |
|---|---|---|---|
| 0.0 | `mark_phase("equation_earned")` | (system) | |
| 0.0 | smooth_move_to(heatmap, target=LEFT side, scale-down via animate.set_height to 3.0) | REFRAME | smooth_move_to |
| 1.5 | zoom_to(v_iter target area, scale=0.85) — slight reframe to favour the equation side | REFRAME | zoom_to |
| 3.0 | Write v_iter MathTex (decomposed) to the right of the grid | REVEAL | Write |
| ~3.5 | DURING the Write: 4 trace_vector calls fire in sequence (focal_halo→s; one outcome cell→s'; goal cell→r; r+γv annotation→γv_k block) | CONNECT (×4) | trace_vector |
| ~10 | `ingestion_wait(3.0)` | (ingestion) | |
| ~13 | FadeOut focal_halo, s_label, r+γv annotation (their job — being trace_vector sources — is done) | (cleanup) | FadeOut |
| ~14.5 | zoom_reset | REFRAME | zoom_reset |
| ~16 | caption: "Treat the equality as an assignment. Sweep v_{k+1}(s) by averaging this over actions and outcomes, until values stop changing." | REVEAL | place_caption + FadeOut/FadeIn |
| ~22 | assimilation_wait(2.5) | | |

### Phase 4 — iteration on the env-heatmap with sprite-math binding

| t | Animation | Tag | Helper |
|---|---|---|---|
| 0.0 | `mark_phase("iteration_demo")` | (system) | |
| 0.0 | smooth_move_to(v_iter, top-left smaller); smooth_move_to(heatmap, mid-left, height ≈ 3.6) | REFRAME | smooth_move_to ×2 |
| 2.5 | FadeIn k_label "k = 0" + Δ_label "Δ = 0.00" RIGHT of heatmap | REVEAL | Write |
| 4.0 | `ingestion_wait(2.0)` | (ingestion) | |
| 6.0 | heatmap.place_agent(state=14, direction="up") — elf appears at focal cell | REVEAL | `place_agent` |
| 7.5 | pan_to_follow camera around the focal cell | REFRAME | pan_to_follow |
| 9.0 | sprite_action_binding(elf at focal, highlight v_{k+1}(s) block in v_iter, dim others) | CONNECT (the §26 sprite-math binding) | sprite_action_binding |
| 13 | heatmap.move_agent(state=10, direction="up") + sprite_action_binding(highlight v_k(s') block, dim others) | CONNECT | move_agent + sprite_action_binding |
| 17 | heatmap.move_agent(state=14, direction="down") + sprite_action_binding(highlight ← + v_{k+1}(s) block) | CONNECT | move_agent + sprite_action_binding |
| 21 | heatmap.remove_agent() + restore all v_iter tokens to PRIMARY | (cleanup) | remove_agent + animate.set_opacity |
| 22 | zoom_reset | REFRAME | zoom_reset |
| 23.5 | `ingestion_wait(2.5)` | (ingestion) | |
| 26 | heatmap.sweep_update(V_1) + update k_label "k = 1", Δ_label "0.2500" | DERIVE (one iteration of the algorithm) | sweep_update |
| 33 | wait(5.0) for narration | | |
| 38 | heatmap.sweep_update(V_2) + update labels | DERIVE | sweep_update |
| 43 | wait(5.0) | | |
| 48 | heatmap.sweep_update(V_5) + update labels | DERIVE | sweep_update |
| 53 | wait(5.0) | | |
| 58 | heatmap.sweep_update(V_10) + update labels | DERIVE | sweep_update |
| 62 | wait(4.0) | | |
| 66 | heatmap.sweep_update(V_converged) + k_label "k = 71" + Δ_label "8.3e-9" | DERIVE | sweep_update |
| 72 | `ingestion_wait(3.0)` + assimilation_wait(5.0) | | |

### Phase 5 — code walkthrough

| t | Animation | Tag | Helper |
|---|---|---|---|
| 0.0 | `mark_phase("code_walkthrough")` | (system) | |
| 0.0 | smooth_move_to(heatmap, smaller LEFT-CENTER); smooth_move_to(v_iter, even smaller top-left, set_opacity SECONDARY) | REFRAME (lifecycle dim) | smooth_move_to ×2 |
| 3.0 | FadeIn CodeStepper RIGHT | REVEAL | CodeStepper + FadeIn |
| 5.0 | `ingestion_wait(2.5)` | (ingestion) | |
| 7.5 | code.step(0) + cross_highlight_pair(code.lines[0], heatmap.cell_bbox(14), ACTION_COLOR) + dim equation parts | CONNECT | cross_highlight_pair |
| 13 | wait(5.0) | | |
| 18 | code.step(1) + cross_highlight_pair(code.lines[1], VGroup(heatmap.cell_bbox(10), cell_bbox(13), cell_bbox(14)), STATE_COLOR) | CONNECT | cross_highlight_pair |
| 24 | wait(6.0) | | |
| 30 | code.step(2) + cross_highlight_pair(code.lines[2], heatmap.cell_bbox(15), REWARD_COLOR) | CONNECT | cross_highlight_pair |
| 36 | wait(6.0) | | |
| 42 | code.step(3) + cross_highlight_pair(code.lines[3], heatmap.cell_bbox(14), VALUE_COLOR) | CONNECT | cross_highlight_pair |
| 48 | code.reset() + restore opacities | (cleanup) | code.reset |

### Phase 6 — misconception (contrast pair)

| t | Animation | Tag | Helper |
|---|---|---|---|
| 0.0 | `mark_phase("misconception")` | (system) | |
| 0.0 | FadeOut(CodeStepper) + FadeOut(v_iter) + FadeOut(k_label) + FadeOut(Δ_label) + smooth_move_to(heatmap, LEFT smaller) | (cleanup + REFRAME) | FadeOut ×4 + smooth_move_to |
| 3.0 | FadeIn caption: "Misconception: policy evaluation finds the best policy. It does not." | REVEAL | place_caption + FadeIn |
| 6.0 | LaggedStart of [FadeIn hm_left RIGHT, FadeIn title_a above hm_uniform, FadeIn title_b above hm_left] | REVEAL | LaggedStart |
| 11 | `ingestion_wait(2.5)` | (ingestion) | |
| 14 | caption swap to RESOLVE | RESOLVE | |
| 21 | FadeOut(hm_left, title_b) | (cleanup) | FadeOut |

### Phase 7 — boundaries

| t | Animation | Tag | Helper |
|---|---|---|---|
| 0.0 | `mark_phase("boundaries")` | (system) | |
| 0.0 | caption swap: "Terminal cells never update. v(terminal) ≡ 0 by definition." | REVEAL | |
| 4.0 | Indicate hole cells one by one (state 5, 7, 11, 12) via PENALTY_COLOR | RESOLVE | Indicate ×4 |
| 7.5 | Indicate goal cell (state 15) via REWARD_COLOR | RESOLVE | Indicate |
| 10 | FadeIn Δ-vs-k Axes RIGHT | REVEAL | Axes + Create |
| 12 | Create the log-Δ curve | DERIVE | Create |
| 16 | Create θ_line + Write θ_label | REVEAL | DashedLine + Write |
| 19 | FadeIn cross_dot + Write "k = 71" label | RESOLVE | FadeIn + Write |
| 22 | caption swap: "Δ < θ stop rule" | RESOLVE | |

### Phase 8 — closing

| t | Animation | Tag | Helper |
|---|---|---|---|
| 0.0 | `mark_phase("closing")` | (system) | |
| 0.0 | FadeOut Δ plot | (cleanup) | FadeOut |
| 2.0 | LaggedStart [FadeIn pill_text "Next: Policy Improvement", FadeIn pill_sub "make π greedy w.r.t. v_π"] | REVEAL | LaggedStart |
| 5.0 | final caption + wait(4.0) | RESOLVE | |

---

## 6. Camera Shot List

| Phase | Shot | Trigger | Helper | Duration | Purpose |
|---|---|---|---|---|---|
| 3 | zoom_to v_iter writing area (scale=0.85) | 1.5s in | `zoom_to(self, v_iter_anchor, scale=0.85)` | 1.4s | Reframe so equation derivation has the focal real-estate during writing + trace_vectors |
| 3 | zoom_reset | ~14.5s in | `zoom_reset(self)` | 1.4s | Return to wide for the post-derivation caption |
| 4 | pan_to_follow elf evaluator | 7.5s in | `pan_to_follow(self, heatmap.agent, path_points=[focal, next, focal])` | ~9s total across the binding demo | Keep the active cell centered while the sprite-math binding plays |
| 4 | zoom_reset before multi-V_k sweep | 22s in | `zoom_reset(self)` | 1.4s | Full canvas visible for the 5-sweep iteration demo |

---

## 7. Sprite-Math Binding Matrix (Phase 4 only — sprite + algebra on screen together)

| Phase | Sprite action | Equation tokens that highlight | Helper |
|---|---|---|---|
| 4 | Elf placed at focal cell (state 14) | `v_{k+1}(s) ←` token block | `place_agent` + `sprite_action_binding(highlight=v_kp1_block)` |
| 4 | Elf moves to one outcome cell (state 10, direction "up") | `v_k(s')` block | `move_agent` + `sprite_action_binding(highlight=v_k_block)` |
| 4 | Elf returns to focal cell (state 14, direction "down") | `v_{k+1}(s) ←` block (write-back signal) | `move_agent` + `sprite_action_binding(highlight=v_kp1_block)` |

---

## 8. trace_vector Source-Target Pairs

| Phase | MathTex token | Source on canvas | Color |
|---|---|---|---|
| 3 | `v_iter[2]` ("s") | focal-cell halo on heatmap (state 14) | STATE_COLOR |
| 3 | `v_iter[5..11]` (`π(a|s)` group) | The retained RIGHT action arrow on the grid (if still present) OR the focal-cell halo as fallback | POLICY_COLOR |
| 3 | `v_iter[17]` ("r") | goal cell on heatmap (state 15) — the only non-zero reward source | REWARD_COLOR |
| 3 | `v_iter[27..31]` (`v_k(s')` block) | one of the outcome cells (state 10) on heatmap | VALUE_COLOR |

---

## 9. Hand-off Notes for the Manim Expert

- **The heatmap is the spine.** Treat `self._heatmap` as a single
  instance instantiated in Phase 1 and never recreated. Phase 2, 3, 4,
  5, 6, 7, 8 all reference the same Mobject; transformations are
  `smooth_move_to` + `set_height` + opacity changes, never new
  instantiations.
- **No abstract fork.** Phase 2 stays inside the grid — the three
  outcome arrows go from the focal cell to actual cells in the same
  heatmap. Do not draw a tree off to one side.
- **No equation morph chain.** Phase 3 writes `v_iter` directly. The
  closed-form Bellman expectation is mentioned in narration; it is
  NOT animated.
- **The Phase-6 second heatmap (`hm_left`) IS a new instance.** That's
  the one exception to "the spine doesn't re-instantiate" — the
  contrast pair needs two instances. The original (`hm_uniform`) is
  the spine; `hm_left` is the throwaway for the LEFT-policy contrast.
- **Cell coordinates:** flat state index `s` → `(s // 4, s % 4)` row/col.
  Use `heatmap.cell_bbox(state_idx)` to get the tile Mobject for
  cross_highlight_pair targets.
- **Agent direction:** at each `move_agent` call, pass the direction
  that matches the motion (`up`/`down`/`left`/`right`). The helper
  swaps the elf sprite to face that direction.
- **No `Dot` agents.** The only sprite is the elf, supplied by
  `heatmap.place_agent(...)`. The v2 purple-dot agent is permanently
  banned for any FrozenLake video.
