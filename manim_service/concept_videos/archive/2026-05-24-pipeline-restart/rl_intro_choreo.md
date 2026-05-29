# Choreography — rl_intro

**plan.md reference:** `manim_service/concept_videos/rl_intro_plan.md`
**Visual Director:** visual-director (skill)
**Date:** 2026-05-21
**Series position:** 1 of 15

---

## 1. Scientific Rigor

This video makes four factual claims, each supported by on-screen evidence. First, it claims that reinforcement learning is distinct from supervised and unsupervised learning because it has no supervisor and no labeled dataset — this is supported by the three-box contrast diagram in Phase 2, where each box carries a one-line distinguishing property and the RL box explicitly reads "no labels, just rewards" (S&B §1.1, pp. 2–3). Second, it claims that the RL agent–environment interface consists of four elements: agent, environment, state/observation signal, and reward signal — these are displayed as a two-box loop diagram with three labeled arrows in Phase 3, each element introduced individually with its canonical color binding (S&B §1.1, pp. 1–2; §1.3, p. 6). Third, it claims that the elf in FrozenLake-v1 receives reward 1.0 on reaching the goal tile and reward 0.0 everywhere else including holes — this is shown by the `+1` reward label at tile 15 and the `0` at failed paths in Phase 5; the qualification that hole tiles terminate the episode with reward 0 (not a negative reward) is stated in the Phase 5 secondary-misconception caption. Fourth, the video uses `is_slippery=True` by default, which means the elf's actual transitions may differ from its intended moves — this is seeded in the Phase 1 caption ("the ice is slippery") and the Phase 3f misconception-guard caption ("In FrozenLake, the elf sees its exact state — not always the case in RL"), without formally teaching partial observability or slip probability. The qualification that rewards are environment-specific (not universally ±1) is stated explicitly in Phase 5.

---

## 2. Pedagogical Strategy

**Primary pattern:** Concrete-to-abstract

**Why this pattern suits this lesson:** This is the series entry point: the learner has no prior RL vocabulary, so beginning with an equation or a formal loop diagram would present notation with no intuitive anchor. By showing the FrozenLake problem first (Phases 1 and 5), the viewer builds physical intuition for agent, environment, state, and reward before these terms are named or diagrammed — when the abstract loop finally appears in Phase 3, the viewer recognizes it as a description of what they already watched. The contrast diagram in Phase 2 positions RL against familiar ML paradigms, giving the viewer a conceptual slot to place this new paradigm before its mechanics are detailed.

**Misconception this strategy specifically defeats:** The primary misconception listed in `rl_knowledge_base.md` for the `rl_intro` entry (spec §5): "RL is supervised learning with delayed feedback." This is defeated visually by the three-way contrast in Phase 2 — the Supervised Learning box explicitly shows a supervisor handing a labeled card, and the RL box shows a question mark (no supervisor), making the structural absence of labels spatially explicit rather than just verbally asserted.

---

## 3. Cognitive Load Budget

Counting rules applied: header (title + subtitle) = 1 mobject throughout; active caption = 1 mobject; FrozenLake grid composite = 1 mobject; elf sprite = 1 mobject; each RoundedRectangle panel = 1 mobject; each loop element (box or arrow) = 1 mobject; each feature card = 1 mobject; takeaway VGroup = 1 mobject.

The critical frame is Phase 3 end (Agent box + Env box + Action arrow + State/Obs arrow + Reward arrow = 5 loop elements visible). Resolution: the newest-entering element is always PRIMARY (1.0); all prior loop elements dim to SECONDARY (0.4) at the instant it enters. See §5 Phase 3 choreography and §9 Hand-off Notes for the exact opacity transition sequence. This keeps the primary count at 1 loop element + 1 caption = 2 primary mobjects at every sub-beat during Phase 3 construction, and at most 2 primary (newest loop element + caption) at Phase 3 end.

| Phase | Primary mobjects at phase start | Primary mobjects at phase mid | Primary mobjects at phase end | Notes |
|---|---|---|---|---|
| 1a | header (1), caption (1) | header (1), grid (1), caption (1) | header (1), grid (1), elf (1), caption (1) | 4 max — within cap |
| 1b | header (1), grid (1), elf (1), caption (1) | header (1), grid (1), elf (1), caption (1) | header (1), grid (1), caption (1) [elf fades to SECONDARY after reset] | Elf at PRIMARY while walking; dims briefly before reset FadeIn |
| 1c | header (1), grid (1), elf (1), caption (1) | header (1), grid (1), elf (1), caption (1) | header (1), grid (1), caption (1) | Same as 1b |
| 1d | header (1), grid (1), elf (1), caption (1) | header (1), grid (1), elf (1), caption (1) | header (1), grid (1), reward_label (1), caption (1) | reward_label is PRIMARY while visible; 4 max |
| 1e | header (1), grid (1), caption (1) | — | header (1), caption (1) [grid FadeOut] | Grid exits — 2 primary at close |
| 2 | header (1), supervised_panel (1), caption (1) | header (1), supervised_panel (1), unsupervised_panel (1), caption (1) | header (1), rl_panel (1), caption (1) [prior panels dim to SECONDARY] | RL panel enters at PRIMARY; panels 1–2 dim to 0.4 simultaneously |
| 3a | header (1), agent_box (1), caption (1) | — | header (1), agent_box (1), caption (1) | 3 primary |
| 3b | header (1), agent_box (SECONDARY), env_box (1), caption (1) | — | header (1), env_box (1), caption (1) | Agent dims when Env enters |
| 3c | header (1), action_arrow (1), caption (1) | — | header (1), action_arrow (1), caption (1) | Agent + Env at SECONDARY |
| 3d | header (1), state_arrow (1), caption (1) | — | header (1), state_arrow (1), caption (1) | Action arrow dims to SECONDARY |
| 3e | header (1), reward_arrow (1), caption (1) | — | header (1), reward_arrow (1), caption (1) | All prior loop elements at SECONDARY; 3 primary |
| 3f | header (1), loop_diagram_group (SECONDARY composite), caption (1) | — | header (1), loop_diagram_group (SECONDARY), caption (1) | Full loop at SECONDARY as a group = 1 secondary composite; 2 primary |
| 4 | header (1), loop_diagram_group (1), caption (1) | header (1), indicated_node (1), loop_remainder (SECONDARY), caption (1) | header (1), loop_diagram_group (SECONDARY), caption (1) | During Indicate: indicated node PRIMARY, remainder SECONDARY |
| 5 | header (1), grid (1), caption (1) | header (1), grid (1), path_A (1), caption (1) | header (1), grid (1), paths_AB (1), reward_labels (1) | Paths counted as 1 group; reward labels as 1 group |
| 6 | header (1), card_1 (1), caption (1) | header (1), card_1 (SECONDARY), card_2 (1), caption (1) | header (1), card_1 (SECONDARY), card_2 (SECONDARY), caption (1) | Both cards dim to SECONDARY at exploration caption |
| 7 | header (1), takeaway_vgroup (1), caption (1) | header (1), takeaway_vgroup (1), frozenlake_ghost (SECONDARY), caption (1) | header (1), takeaway_vgroup (1), closing_text (1), caption (1) | FrozenLake ghost at SECONDARY = 0 primary cost |

---

## 4. Element Lifecycle Matrix

| Mobject | Phase IN | Visible during | Phase OUT | Re-enters at |
|---|---|---|---|---|
| `header` (title "What Is Reinforcement Learning?" + subtitle) | 1a (Write via `show_header`) | 1a–7 (persistent scene identity) | end of Phase 7 (FadeOut with everything) | never |
| `caption` (active bottom-edge caption) | 1a | every phase | end of Phase 7 | never (swapped in place each time) |
| `frozenlake_grid` Phase 1 (full size, CENTER) | 1a (LaggedStart FadeIn tiles) | 1a–1e | end of Phase 1e (FadeOut before Phase 2; ingestion_wait 2.5 s follows) | Phase 5 (new instance, reduced size) |
| `elf_sprite` Phase 1 (direction-aware ImageMobject) | 1a (FadeIn at tile 0 with `elf_right.png`) | 1a–1d (all walk subphases) | end of Phase 1d (FadeOut after goal-tile pause, 1.0 s hold; elf gone before Phase 1e closing caption) | never |
| `hole_border_flash_7` (PENALTY_COLOR Flash on tile 7) | 1b (Flash, transient) | 1b (< 0.4 s total, then gone) | 1b (self-dismissing Flash) | never |
| `hole_border_flash_12` (PENALTY_COLOR Flash on tile 12) | 1c (Flash, transient) | 1c (< 0.4 s total) | 1c (self-dismissing Flash) | never |
| `reward_label_plus1` (Text "+1", REWARD_COLOR, floats above tile 15) | 1d (FadeIn after goal Flash) | 1d (1.0 s hold) | 1d (FadeOut after 1.0 s hold, before Phase 1e caption) | Phase 5 (text "+1" reappears as path label, new instance) |
| `supervised_panel` (RoundedRectangle + text group) | 2 (FadeIn, first in LaggedStart) | 2 (dims to SECONDARY when unsupervised_panel enters) | end of Phase 2 (FadeOut in group before Phase 3) | never |
| `unsupervised_panel` (RoundedRectangle + text group) | 2 (FadeIn second, lag_ratio=0.5) | 2 (dims to SECONDARY when rl_panel enters) | end of Phase 2 (FadeOut in group) | never |
| `rl_panel` (RoundedRectangle with REWARD_COLOR border + text + question_mark) | 2 (FadeIn last, ~0.8 s after unsupervised_panel) | 2 (at PRIMARY until ingestion_wait; dims to SECONDARY with Indicate pulse) | end of Phase 2 (FadeOut in group; ingestion_wait 2.5 s follows) | never |
| `question_mark_float` (Text "?", POLICY_COLOR, above rl_panel) | 2 (FadeIn briefly after rl_panel appears) | 2 (2.0 s max) | 2 (FadeOut before Phase 2 Indicate pulse; replaced by REWARD_COLOR arrow icon) | never |
| `rl_panel_arrow_icon` (REWARD_COLOR small arrow icon on rl_panel) | 2 (FadeIn after question_mark_float FadeOut) | 2–2 end | 2 (FadeOut with all_three_panels) | never |
| `agent_box` (RoundedRectangle, POLICY_COLOR border, label "Agent") | 3a (Create) | 3a–4 (PRIMARY in 3a; SECONDARY from 3b onward until Phase 4 Indicate) | end of Phase 4 (FadeOut with full loop; ingestion_wait 2.5 s follows) | never |
| `env_box` (RoundedRectangle, STATE_COLOR border, label "Environment") | 3b (Create) | 3b–4 (PRIMARY in 3b; SECONDARY from 3c onward until Phase 4 Indicate) | end of Phase 4 (FadeOut with full loop) | never |
| `action_arrow` (CurvedArrow, ACTION_COLOR, curves below; label "Action") | 3c (Create) | 3c–4 (PRIMARY in 3c; SECONDARY from 3d onward) | end of Phase 4 (FadeOut with full loop) | never |
| `state_obs_arrow` (CurvedArrow, STATE_COLOR, curves above upper channel; label VGroup "State / Observation") | 3d (Create) | 3d–4 (PRIMARY in 3d; SECONDARY from 3e onward) | end of Phase 4 (FadeOut with full loop) | never |
| `reward_arrow` (CurvedArrow, REWARD_COLOR, parallel upper channel with curvature offset; label "Reward") | 3e (Create) | 3e–4 (PRIMARY in 3e; SECONDARY at Phase 3f full-loop-visible moment) | end of Phase 4 (FadeOut with full loop) | never |
| `frozenlake_grid` Phase 5 (reduced size, new instance, CENTER) | 5 (FadeIn) | 5 only | end of Phase 5 (FadeOut with paths; ingestion_wait 2.5 s follows) | Phase 7 (new instance, small, LEFT, OPACITY_SECONDARY) |
| `path_A_trail` (DashedLine REWARD_COLOR, tiles 0→4→8→9→10→14→15) | 5 (Write, LaggedStart first) | 5 (after draw, stays visible for path contrast) | end of Phase 5 (FadeOut with grid) | never |
| `path_B_trail` (DashedLine PENALTY_COLOR, tiles 0→1→2→6→7) | 5 (Write, LaggedStart second, lag_ratio=0.6) | 5 (after draw, stays visible for path contrast) | end of Phase 5 (FadeOut with grid) | never |
| `path_x_mark` (Text "×", PENALTY_COLOR, at tile 7) | 5 (FadeIn after path_B draw) | 5 | end of Phase 5 (FadeOut with grid) | never |
| `reward_label_path_A` (Text "+1", REWARD_COLOR, at tile 15) | 5 (FadeIn after path_A draw) | 5 | end of Phase 5 (FadeOut with grid) | never |
| `reward_label_path_B` (Text "0", CODE_ACCENT, at tile 7) | 5 (FadeIn after path_B draw) | 5 | end of Phase 5 (FadeOut with grid) | never |
| `card_1` (RoundedRectangle + "Trial-and-Error Search" + body text) | 6 (FadeIn, first) | 6 (PRIMARY on entry; dims to SECONDARY when card_2 enters) | end of Phase 6 (FadeOut; ingestion_wait 2.5 s follows) | never |
| `card_2` (RoundedRectangle + "Delayed Reward" + body text) | 6 (FadeIn after card_1 visible, lag_ratio=0.6) | 6 (PRIMARY on entry) | end of Phase 6 (FadeOut; ingestion_wait 2.5 s follows) | never |
| `takeaway_vgroup` (VGroup: two-line Text, line 1 WHITE, line 2 REWARD_COLOR) | 7a (Write, LaggedStart lag_ratio=0.3) | 7 | end of Phase 7 (FadeOut with everything) | never |
| `frozenlake_ghost` Phase 7 (small, LEFT, opacity=0.4; new instance) | 7b (FadeIn after takeaway_vgroup written) | 7b–7c | end of Phase 7 (FadeOut with everything) | never |
| `closing_text_vgroup` (VGroup: "Next: the Markov Decision Process" + sub-line) | 7c (FadeIn below takeaway_vgroup) | 7c | end of Phase 7 (FadeOut with everything) | never |

---

## 5. Motion Choreography (per-phase)

### Phase 1a — Grid Introduction

| Time (rel. to phase start) | Animation | Purpose tag | Manim helper |
|---|---|---|---|
| 0.0 s | `show_header("What Is Reinforcement Learning?", subtitle="Learning by interacting with an environment")` | REVEAL | `BaseConceptScene.show_header` |
| 1.2 s | `LaggedStart([FadeIn(tile) for tile in grid_tiles], lag_ratio=0.1)` — 16 tiles fade in across 4×4 grid, CENTER | REVEAL | `frozenlake_frame(state=0)` |
| 3.0 s | `Indicate(goal_border, color=REWARD_COLOR, scale_factor=1.08, run_time=0.8)` — goal tile pulses once | RESOLVE (confirms which tile is the objective) | Manim `Indicate` |
| 3.9 s | `Indicate(hole_borders_group, color=PENALTY_COLOR, scale_factor=1.05, run_time=0.8)` — all four hole borders pulse simultaneously | REVEAL (names danger zones) | Manim `Indicate` |
| 4.7 s | `FadeIn(elf_sprite)` at tile 0 (`elf_right.png`) | REVEAL | `frozenlake_frame` elf overlay |
| 5.0 s | `self.wait(2.0)` — first geometry reveal minimum (STYLE_BIBLE §6) | — | — |
| 5.0 s | `place_caption("The elf wants to reach the goal — but the ice is slippery and there are holes.")` | REVEAL | `BaseConceptScene.place_caption` |

### Phase 1b — Attempt 1: Elf Falls in Hole (tile 7)

Path: 0 → 1 → 2 → 6 → 7

| Time (rel. to phase start) | Animation | Purpose tag | Manim helper |
|---|---|---|---|
| 0.0 s | `place_caption("The elf doesn't know the rules of the ice — it only sees what happens after each step.")` | REVEAL | `place_caption` |
| 0.3 s | Swap sprite to `elf_right.png` (already correct); `smooth_move_to(elf, tile_1, run_time=1.0)` | REVEAL (first step, first trial) | `BaseConceptScene.smooth_move_to` |
| 1.3 s | `smooth_move_to(elf, tile_2, run_time=1.0)` — RIGHT, sprite stays `elf_right.png` | REVEAL | `smooth_move_to` |
| 2.3 s | Swap sprite to `elf_down.png`; `smooth_move_to(elf, tile_6, run_time=1.0)` — DOWN | REVEAL | sprite swap + `smooth_move_to` |
| 3.3 s | `smooth_move_to(elf, tile_7, run_time=1.0)` — DOWN, hits hole | RESOLVE (failure outcome shown) | `smooth_move_to` |
| 4.3 s | `pan_to_follow` releases; `Flash(hole_tile_7, color=PENALTY_COLOR, flash_radius=0.4, run_time=0.5)` | RESOLVE (confirms penalty) | Manim `Flash` |
| 4.8 s | `FadeOut(elf_sprite, run_time=0.4)` | RESOLVE (elf vanishes into hole) | `FadeOut` |
| 5.2 s | `FadeIn(elf_sprite_reset)` at tile 0, `elf_right.png` | REVEAL (episode resets) | `FadeIn` + position reset |
| 5.6 s | `self.wait(2.0)` — after failure animation settles | — | — |

**Camera note:** `pan_to_follow` active during this subphase — see §6 Camera Shot List row 1b.

### Phase 1c — Attempt 2: Elf Falls Again (tile 12)

Path: 0 → 4 → 8 → 12

| Time (rel. to phase start) | Animation | Purpose tag | Manim helper |
|---|---|---|---|
| 0.0 s | `place_caption("No one tells it the right moves — it has to figure them out.")` | REVEAL | `place_caption` |
| 0.3 s | Swap sprite to `elf_down.png`; `smooth_move_to(elf, tile_4, run_time=1.0)` | REVEAL | `smooth_move_to` |
| 1.3 s | `smooth_move_to(elf, tile_8, run_time=1.0)` — DOWN | REVEAL | `smooth_move_to` |
| 2.3 s | `smooth_move_to(elf, tile_12, run_time=1.0)` — DOWN, hits hole | RESOLVE (second failure) | `smooth_move_to` |
| 3.3 s | `Flash(hole_tile_12, color=PENALTY_COLOR, flash_radius=0.4, run_time=0.5)` | RESOLVE | `Flash` |
| 3.8 s | `FadeOut(elf_sprite, run_time=0.4)` | RESOLVE | `FadeOut` |
| 4.2 s | `FadeIn(elf_sprite_reset)` at tile 0 | REVEAL (reset again) | `FadeIn` |
| 4.6 s | `self.wait(1.5)` | — | — |

**Camera note:** `pan_to_follow` active — see §6 row 1c. Tile 12 is lower-left quadrant (row=3, col=0), far from default center; camera must follow DOWN movement.

### Phase 1d — Attempt 3: Elf Reaches Goal

Path: 0 → 4 → 8 → 9 → 10 → 14 → 15

| Time (rel. to phase start) | Animation | Purpose tag | Manim helper |
|---|---|---|---|
| 0.0 s | `place_caption("When the elf reaches the goal, it receives a reward — a single number that says 'that was good.'")` | REVEAL | `place_caption` |
| 0.3 s | Sprite stays `elf_down.png`; `smooth_move_to(elf, tile_4, run_time=1.0)` | REVEAL (success attempt begins) | `smooth_move_to` |
| 1.3 s | `smooth_move_to(elf, tile_8, run_time=1.0)` — DOWN | REVEAL | `smooth_move_to` |
| 2.3 s | Swap sprite to `elf_right.png`; `smooth_move_to(elf, tile_9, run_time=1.0)` — RIGHT | REVEAL | sprite swap + `smooth_move_to` |
| 3.3 s | `smooth_move_to(elf, tile_10, run_time=1.0)` — RIGHT | REVEAL | `smooth_move_to` |
| 4.3 s | Swap sprite to `elf_down.png`; `smooth_move_to(elf, tile_14, run_time=1.0)` — DOWN | REVEAL | sprite swap + `smooth_move_to` |
| 5.3 s | Swap sprite to `elf_right.png`; `smooth_move_to(elf, tile_15, run_time=1.0)` — RIGHT, goal | RESOLVE (reaches objective) | sprite swap + `smooth_move_to` |
| 6.3 s | `Flash(goal_tile_15, color=REWARD_COLOR, flash_radius=0.6, run_time=0.6)` | RESOLVE (reward signal fires) | `Flash` |
| 6.9 s | `FadeIn(reward_label_plus1)` — Text "+1" floats above tile 15, REWARD_COLOR | REVEAL (reward value named) | `FadeIn` |
| 7.0 s | `self.wait(1.0)` | — | — |
| 8.0 s | `FadeOut(reward_label_plus1, run_time=0.5)` | — | `FadeOut` |
| 8.5 s | `self.wait(2.0)` — after success path settles | — | — |

**Camera note:** `pan_to_follow` active. Tile 14 and 15 are lower-right quadrant. See §6 row 1d.

### Phase 1e — Closing + FadeOut

| Time (rel. to phase start) | Animation | Purpose tag | Manim helper |
|---|---|---|---|
| 0.0 s | `FadeOut(elf_sprite, run_time=0.5)` | RESOLVE (elf stands down; phase closes) | `FadeOut` |
| 0.5 s | `place_caption("This is the reinforcement learning problem: learn to act by interacting, with no labels — only rewards.")` | REFRAME (names the paradigm for the first time) | `place_caption` |
| 0.8 s | `self.wait(1.5)` | — | — |
| 2.3 s | `zoom_reset(self, run_time=1.6)` — return to wide frame before FadeOut (STYLE_BIBLE §18: zoom_reset is a major structural morph) | REFRAME | `zoom_reset` |
| 3.9 s | `FadeOut(frozenlake_grid, run_time=1.0)` | RESOLVE (phase complete; canvas cleared for Phase 2) | `FadeOut` |
| 4.9 s | `self.ingestion_wait(2.5)` — grid FadeOut is a major structural composition change (STYLE_BIBLE §18) | — | — |

### Phase 2 — What RL Is NOT: Three-Way ML Contrast

| Time (rel. to phase start) | Animation | Purpose tag | Manim helper |
|---|---|---|---|
| 0.0 s | `place_caption("Machine learning has three distinct paradigms.")` | REVEAL | `place_caption` |
| 0.5 s | `LaggedStart(FadeIn(supervised_panel), FadeIn(unsupervised_panel), FadeIn(rl_panel), lag_ratio=0.5)` — staggered panel reveal; supervised enters first, rl_panel last; as each enters the previously-entered panels dim to OPACITY_SECONDARY simultaneously | REVEAL | `LaggedStart` + `FadeIn` |
| 3.5 s | `self.wait(2.0)` — first geometry reveal of contrast diagram (STYLE_BIBLE §6) | — | — |
| 3.5 s | `FadeIn(question_mark_float)` above rl_panel — Text "?", POLICY_COLOR | REVEAL (agent uncertainty before naming) | `FadeIn` |
| 4.5 s | `self.ingestion_wait(2.5)` — rl_panel FadeIn completes a structural composition change | — | — |
| 4.5 s | `place_caption("RL is a third paradigm — no labeled examples, no supervisor, just a reward signal.")` | REVEAL (primary contrast stated) | `place_caption` |
| 5.5 s | `FadeOut(question_mark_float, run_time=0.4)` | RESOLVE (uncertainty resolves into the RL identity) | `FadeOut` |
| 5.9 s | `FadeIn(rl_panel_arrow_icon, run_time=0.4)` — REWARD_COLOR arrow on rl_panel | CONNECT (binds the reward color to RL) | `FadeIn` |
| 6.3 s | `Indicate(rl_panel_border, color=REWARD_COLOR, scale_factor=1.08, run_time=0.7)` | RESOLVE (confirms RL is the focus) | `Indicate` |
| 7.0 s | `self.wait(2.0)` — post-Indicate dwell | — | — |
| 7.0 s | `place_caption("The agent must discover which actions are good — the supervisor does not exist.")` | REVEAL | `place_caption` |
| 9.0 s | `self.wait(2.0)` | — | — |
| 9.0 s | `FadeOut(supervised_panel, unsupervised_panel, rl_panel, run_time=1.0)` — group exit | RESOLVE (contrast panel work done) | `FadeOut` |
| 10.0 s | `self.ingestion_wait(2.5)` — panel FadeOut structural change (STYLE_BIBLE §18) | — | — |

### Phase 3 — The Abstract RL Loop Diagram

**Opacity transition rule for Phase 3:** At the moment each new loop element enters, ALL previously-revealed loop elements simultaneously transition to OPACITY_SECONDARY (0.4) via `.animate.set_opacity(0.4)`, grouped with the new element's Create animation in a single `self.play(...)` call. The new element enters at OPACITY_PRIMARY (1.0). Caption is always PRIMARY. Header is always PRIMARY. This ensures the primary count at any Phase 3 frame = 1 loop element (newest) + caption (1) + header (1) = 3, well within the §27 cap of 4. (STYLE_BIBLE §27.)

**Phase 3 loop diagram arrow geometry — upper channel resolution (Special Design Challenge 1):**

Two arrows share the Environment→Agent upper channel (State/Obs and Reward). They must not overlap. Solution:

- `state_obs_arrow`: `CurvedArrow` with `angle=-PI/3` (curves upward/away from the horizontal), arc midpoint displaced +0.45 units above the straight-line path between the two boxes. Label VGroup anchors above the arc midpoint.
- `reward_arrow`: `CurvedArrow` with `angle=-PI/4` (curves upward but less steeply), arc midpoint displaced +0.20 units above the straight-line path. Label anchors above this arc midpoint, and the label is offset 0.3 units rightward of the state_obs_arrow label horizontally to prevent text collision.

Net result: state_obs_arrow has the outer (more curved) arc; reward_arrow hugs the inner (less curved) arc. Vertical gap between arc midpoints ≈ 0.25 units, sufficient for visual separation. Both labels are in their respective semantic colors (STATE_COLOR, REWARD_COLOR) and are legible. (STYLE_BIBLE §16.2 — 0.18 unit minimum buffer between labels.)

The action arrow runs below both boxes, curving downward: `CurvedArrow` with `angle=PI/3` (curves downward), arc midpoint displaced −0.45 units below the horizontal. This gives the diagram a clear top-channel / bottom-channel separation.

| Time (rel. to phase start) | Animation | Purpose tag | Manim helper |
|---|---|---|---|
| 0.0 s | `place_caption("The Agent — the decision-maker.")` | REVEAL | `place_caption` |
| 0.3 s | `Create(agent_box)` at CENTER-LEFT (x ≈ −2.2, y ≈ 0) — POLICY_COLOR border, label "Agent" | REVEAL | `Create` + `Text` |
| 1.1 s | `self.wait(1.5)` | — | — |
| 2.6 s | `place_caption("The Environment — everything the agent interacts with.")` | REVEAL | `place_caption` |
| 2.9 s | `self.play(Create(env_box), agent_box.animate.set_opacity(0.4))` — env_box enters PRIMARY, agent_box dims to SECONDARY simultaneously | REVEAL | `Create` + `.animate.set_opacity` |
| 3.7 s | `self.wait(1.5)` | — | — |
| 5.2 s | `self.ingestion_wait(2.5)` — second box FadeIn is structural (STYLE_BIBLE §18) | — | — |
| 5.2 s | `place_caption("The Agent chooses an Action.")` | REVEAL | `place_caption` |
| 5.5 s | `self.play(Create(action_arrow), agent_box.animate.set_opacity(0.4), env_box.animate.set_opacity(0.4))` — action_arrow PRIMARY, both boxes held at SECONDARY | REVEAL | `Create` + `.animate.set_opacity` |
| 6.3 s | `self.wait(1.5)` | — | — |
| 7.8 s | `place_caption("The Environment sends back the State — what the agent perceives.")` | REVEAL | `place_caption` |
| 8.1 s | `self.play(Create(state_obs_arrow), action_arrow.animate.set_opacity(0.4))` — state_obs_arrow PRIMARY, action_arrow dims | REVEAL | `Create` + `.animate.set_opacity` |
| 8.9 s | `self.wait(1.5)` | — | — |
| 10.4 s | `self.ingestion_wait(2.5)` — third element (state arrow) completes structural addition (STYLE_BIBLE §18) | — | — |
| 10.4 s | `place_caption("The Environment also sends a Reward — a single number.")` | REVEAL | `place_caption` |
| 10.7 s | `self.play(Create(reward_arrow), state_obs_arrow.animate.set_opacity(0.4))` — reward_arrow PRIMARY, state_obs_arrow dims; agent_box, env_box, action_arrow remain at SECONDARY | REVEAL | `Create` + `.animate.set_opacity` |
| 11.5 s | `self.wait(1.5)` | — | — |
| 13.0 s | `self.ingestion_wait(2.5)` — reward arrow completes the loop diagram (structural; STYLE_BIBLE §18) | — | — |
| 13.0 s | `place_caption("In FrozenLake, the elf sees its exact state — not always the case in RL.")` | REVEAL (misconception guard: partial observability seeded) | `place_caption` |
| 13.3 s | `self.wait(2.0)` — full loop now visible for first time; geometry reveal minimum (STYLE_BIBLE §6) | — | — |

### Phase 4 — The Cycle: The Loop Repeats

Before cycle 1: `zoom_to(self, loop_diagram_group, scale=0.75, run_time=1.5)` — tighter frame gives the loop room. This is a major structural morph; `ingestion_wait(2.5)` follows. (STYLE_BIBLE §18, §25.)

**Cycle 1 (run_time=0.6 per Indicate, self.wait(0.4) between each):**

| Time (rel. to phase start) | Animation | Purpose tag | Manim helper |
|---|---|---|---|
| 0.0 s | `zoom_to(self, loop_diagram_group, scale=0.75, run_time=1.5)` | REFRAME | `zoom_to` |
| 1.5 s | `self.ingestion_wait(2.5)` — zoom_to is a major structural morph (STYLE_BIBLE §18) | — | — |
| 4.0 s | `place_caption("At every time step: observe state, choose action, receive reward.")` | REVEAL | `place_caption` |
| 4.3 s | `Indicate(agent_box, color=POLICY_COLOR, scale_factor=1.1, run_time=0.6)` | REVEAL (cycle node 1) | `Indicate` |
| 4.9 s | `self.wait(0.4)` | — | — |
| 5.3 s | `Indicate(action_arrow, color=ACTION_COLOR, scale_factor=1.1, run_time=0.6)` | REVEAL (cycle node 2) | `Indicate` |
| 5.9 s | `self.wait(0.4)` | — | — |
| 6.3 s | `Indicate(env_box, color=STATE_COLOR, scale_factor=1.1, run_time=0.6)` | REVEAL (cycle node 3) | `Indicate` |
| 6.9 s | `self.wait(0.4)` | — | — |
| 7.3 s | `Indicate(state_obs_arrow, color=STATE_COLOR, scale_factor=1.1, run_time=0.6)` | REVEAL (cycle node 4) | `Indicate` |
| 7.9 s | `self.wait(0.4)` | — | — |
| 8.3 s | `Indicate(reward_arrow, color=REWARD_COLOR, scale_factor=1.1, run_time=0.6)` | REVEAL (cycle node 5) | `Indicate` |
| 8.9 s | `self.wait(0.4)` | — | — |
| 9.3 s | `Indicate(agent_box, color=POLICY_COLOR, scale_factor=1.1, run_time=0.6)` — agent observes again, completing cycle 1 | RESOLVE (loop closure demonstrated) | `Indicate` |
| 9.9 s | `self.wait(1.5)` — after cycle 1 | — | — |

**Cycle 2 (run_time=0.5 per Indicate, faster to reinforce rhythmic repetition):**

| Time (rel. to phase start) | Animation | Purpose tag | Manim helper |
|---|---|---|---|
| 11.4 s | `place_caption("This repeats on every time step.")` | REFRAME (generalizes the loop) | `place_caption` |
| 11.7 s | Repeat 6-node Indicate sequence with run_time=0.5 each, self.wait(0.4) between | RESOLVE (cycle nature visceralized) | `Indicate` ×6 |
| 16.2 s | `self.wait(1.5)` — after cycle 2 | — | — |
| 17.7 s | `self.ingestion_wait(2.5)` — end of cycle sequence (STYLE_BIBLE §18) | — | — |
| 20.2 s | `zoom_reset(self, run_time=1.6)` — return to wide frame (STYLE_BIBLE §25; zoom_reset before Phase 5 new layout) | REFRAME | `zoom_reset` |
| 21.8 s | `self.ingestion_wait(2.5)` — zoom_reset is a major structural morph (STYLE_BIBLE §18) | — | — |
| 24.3 s | `FadeOut(agent_box, env_box, action_arrow, state_obs_arrow, reward_arrow, run_time=1.0)` — complete loop exits | RESOLVE (loop phase done; canvas clears) | `FadeOut` |
| 25.3 s | `self.ingestion_wait(2.5)` — diagram FadeOut is structural (STYLE_BIBLE §18) | — | — |

### Phase 5 — Reward Signal and Cumulative Goal

| Time (rel. to phase start) | Animation | Purpose tag | Manim helper |
|---|---|---|---|
| 0.0 s | `place_caption("The agent wants to accumulate reward over the whole episode — not just survive the next step.")` | REVEAL | `place_caption` |
| 0.5 s | `FadeIn(frozenlake_grid_phase5)` — new instance, 85% scale, CENTER | REVEAL (FrozenLake returns as concrete reference) | `frozenlake_frame` + `FadeIn` |
| 1.5 s | `LaggedStart(Write(path_A_trail), Write(path_B_trail), lag_ratio=0.6)` — REWARD_COLOR trail then PENALTY_COLOR trail drawn | REVEAL (two paths drawn sequentially) | `LaggedStart` + `Write` |
| 4.5 s | `FadeIn(reward_label_path_A)` "+1" at tile 15, REWARD_COLOR; `FadeIn(reward_label_path_B)` "0" at tile 7, CODE_ACCENT; `FadeIn(path_x_mark)` "×" at tile 7, PENALTY_COLOR | RESOLVE (outcomes labeled) | `FadeIn` |
| 5.0 s | `self.wait(2.0)` — first geometry reveal of path contrast (STYLE_BIBLE §6) | — | — |
| 5.0 s | `place_caption("Rewards can be positive, zero, or negative — the exact values depend on the environment.")` | REVEAL (secondary misconception guard) | `place_caption` |
| 7.0 s | `self.wait(1.5)` | — | — |
| 7.0 s | `place_caption("The goal: more total reward over time.")` | RESOLVE (cumulative objective stated) | `place_caption` |
| 8.5 s | `self.wait(1.5)` | — | — |
| 8.5 s | `FadeOut(frozenlake_grid_phase5, path_A_trail, path_B_trail, reward_label_path_A, reward_label_path_B, path_x_mark, run_time=1.0)` | RESOLVE (phase done) | `FadeOut` |
| 9.5 s | `self.ingestion_wait(2.5)` — FadeOut structural (STYLE_BIBLE §18) | — | — |

### Phase 6 — Trial-and-Error and Delayed Reward: Named RL Features

Cards stacked vertically in CENTER: card_1 above, card_2 below, separated by 0.3 units of buff (STYLE_BIBLE §16.2).

| Time (rel. to phase start) | Animation | Purpose tag | Manim helper |
|---|---|---|---|
| 0.0 s | `place_caption("RL's first distinguishing feature: the agent discovers good actions by trying them. (S&B §1.1 p. 2)")` | REVEAL | `place_caption` |
| 0.5 s | `FadeIn(card_1)` — "Trial-and-Error Search" card at CENTER-upper | REVEAL | `FadeIn` |
| 1.5 s | `self.wait(2.0)` | — | — |
| 3.5 s | `place_caption("RL's second distinguishing feature: reward may arrive long after the action that caused it. (S&B §1.1 p. 2)")` | REVEAL | `place_caption` |
| 3.8 s | `self.play(FadeIn(card_2), card_1.animate.set_opacity(0.4))` — card_2 enters PRIMARY, card_1 dims to SECONDARY | REVEAL | `FadeIn` + `.animate.set_opacity` |
| 4.6 s | `self.wait(2.0)` | — | — |
| 6.6 s | `self.ingestion_wait(2.5)` — both cards now visible; structural composition set (STYLE_BIBLE §18) | — | — |
| 6.6 s | `place_caption("The agent also faces a challenge: try known good actions, or explore new ones — a tension we will return to.")` | REVEAL (exploration–exploitation named, caption only; no animation per RL Expert flag) | `place_caption` |
| 9.1 s | `self.wait(1.5)` | — | — |
| 9.1 s | `FadeOut(card_1, card_2, run_time=1.0)` | RESOLVE (phase done) | `FadeOut` |
| 10.1 s | `self.ingestion_wait(2.5)` — cards FadeOut structural (STYLE_BIBLE §18) | — | — |

### Phase 7 — Takeaway and Closing Connection

| Time (rel. to phase start) | Animation | Purpose tag | Manim helper |
|---|---|---|---|
| 0.0 s | `place_caption("The agent, the environment, the loop — that is reinforcement learning.")` | REFRAME (consolidation) | `place_caption` |
| 0.5 s | `LaggedStart(Write(takeaway_line_1), Write(takeaway_line_2), lag_ratio=0.3)` — VGroup, line 1 WHITE, line 2 REWARD_COLOR, CENTER | RESOLVE (series' first takeaway statement) | `Write` + `LaggedStart` |
| 2.5 s | `self.wait(2.0)` | — | — |
| 4.5 s | `FadeIn(frozenlake_ghost)` — Phase 7 FrozenLake re-entry: small scale (65% of Phase 1 size), anchored LEFT at x ≈ −3.8, y ≈ 0, opacity=0.4 (OPACITY_SECONDARY); **position**: `place_left_panel` anchor (LEFT * 4.0 + DOWN * 0.15) then `scale(0.65)` | REFRAME (visual bridge to next video; STYLE_BIBLE §23 re-entry) | `FadeIn` with opacity parameter |
| 5.0 s | `FadeIn(closing_text_vgroup)` — VGroup stacked below takeaway_vgroup: "Next: the Markov Decision Process" (STATE_COLOR, font_size=22) + "We give this loop a precise mathematical home." (CODE_ACCENT, font_size=18) | CONNECT (binds to next video in DAG) | `FadeIn` |
| 5.5 s | `place_caption("In the next video, we formalize the loop — the Markov Decision Process.")` | CONNECT | `place_caption` |
| 6.0 s | `self.wait(2.5)` — mandatory final hold (STYLE_BIBLE §6) | — | — |
| 8.5 s | `FadeOut(*self.mobjects, run_time=1.0)` — clean scene end | RESOLVE | `FadeOut` |

---

## 6. Camera Shot List

| Phase | Shot | Trigger time (within phase) | Helper | Duration | Purpose |
|---|---|---|---|---|---|
| 1b | `pan_to_follow` — track elf RIGHT across tiles 0→1→2, then DOWN to tile 6, then tile 7 (lower-right mid region) | 0.3 s into Phase 1b (first step begins) | `pan_to_follow(self, elf_sprite, path=[tile_0, tile_1, tile_2, tile_6, tile_7])` | continuous ~4.0 s through elf walk | Keep elf visible as it moves toward center-right then downward; tile 7 is row=1, col=3, reachable without extreme pan needed but camera should track smoothly (STYLE_BIBLE §25) |
| 1c | `pan_to_follow` — track elf DOWN from tile 0 → 4 → 8 → 12; tile 12 is row=3, col=0, lower-left quadrant | 0.3 s into Phase 1c | `pan_to_follow(self, elf_sprite, path=[tile_0, tile_4, tile_8, tile_12])` | continuous ~3.0 s | Tile 12 is the farthest from default center in the down-left direction; camera must follow to keep elf visible (STYLE_BIBLE §25) |
| 1d | `pan_to_follow` — track success path; tiles 14 and 15 are lower-right quadrant, far from default CENTER | 0.3 s into Phase 1d | `pan_to_follow(self, elf_sprite, path=[tile_0, tile_4, tile_8, tile_9, tile_10, tile_14, tile_15])` | continuous ~6.0 s through full success walk | Tile 15 is the bottom-right corner of the 4×4 grid; without pan the elf would appear at frame edge during the key reward moment (STYLE_BIBLE §25) |
| 1e | `zoom_reset` — return to wide frame before Phase 2 | At 2.3 s into Phase 1e (after closing caption established) | `zoom_reset(self, run_time=1.6)` | 1.6 s | Required before FadeOut/FadeIn at Phase 2 wide-layout contrast diagram. Deliberate slower run_time conveys "returning to overview" (STYLE_BIBLE §25, §18) |
| 4 | `zoom_to` — tighten frame on loop diagram before cycle animations | 0.0 s into Phase 4 | `zoom_to(self, loop_diagram_group, scale=0.75, run_time=1.5)` | 1.5 s | Loop diagram is the key visual of the series; cycle animation at wide frame leaves canvas empty around it. Tighter frame eliminates distraction and gives Indicate animations more screen weight (STYLE_BIBLE §25) |
| 4 | `zoom_reset` — return to wide frame after cycle sequence completes | At 20.2 s into Phase 4 (after ingestion_wait post-cycle-2) | `zoom_reset(self, run_time=1.6)` | 1.6 s | Required before Phase 5 introduces a new wide-layout element (FrozenLake re-entry). Separation from zoom_to: ~17 s, well beyond the 4 s "flinch" exclusion zone (STYLE_BIBLE §25, §18) |
| 7 | Wide frame maintained | Phase 7 start (already reset in Phase 4) | No camera call needed | — | Phase 7 uses the full wide frame to show takeaway text (center), FrozenLake ghost (left), and closing text (center-lower) simultaneously. STYLE_BIBLE §25: "wide enough to show the 3-panel layout." |

**Camera move count:** 6 moves across ~7–9 minutes. This is within the "~6 camera moves per 10 minutes" guideline (STYLE_BIBLE §25 principle).

---

## 7. Sprite-Math Binding Matrix

**Phase 1 elf motion: FLAVOUR — no binding required.**

The elf walk in Phase 1 (Subphases 1b, 1c, 1d) is flavour motion before any algorithm, equation, or code has been introduced. The plan.md states explicitly (§11 Downstream Handoff Notes, item 1): "The sprite-math binding protocol (STYLE_BIBLE §26) applies only to Phase 1 elf walks — those are flavour motion before any algebra, so no `SpriteActionBinding` is required." STYLE_BIBLE §26 states: "Optional for: purely contextual sprite motion (e.g., a flavour agent walking in Phase 1 motivation before any equation has been written)." No binding rows exist for Phase 1.

**No sprite-math bindings required in this video.** This video contains no equations, no CodeStepper, no MathTex, and no algorithm panels. STYLE_BIBLE §26 bindings apply only when a sprite moves AND there is an equation or code panel on screen. Neither condition exists in any phase of this video. The elf walk is the only sprite motion in the entire video, and it is explicitly FLAVOUR before any algebra (plan.md §11 item 1; specs.md §6 "Not permitted: any equation in MathTex"). QA F50 applies only where binding is required; the exemption here is architectural (no math layer exists), not a waiver of a violated rule.

| Phase | Sprite action | Equation token(s) that highlight | Code line that highlights | Helper |
|---|---|---|---|---|
| — | No bindings required in this video — see declaration above | — | — | — |

---

## 8. trace_vector Source-Target Pairs

**NONE — no equation tokens exist.**

This video contains no `MathTex`, no equations, and no equation tokens. STYLE_BIBLE §15.1 states that `trace_vector` is required "when a new equation token is `Write`-animated for the first time AND its meaning is grounded in a visible geometric element." No equation tokens are ever Written in this video. STYLE_BIBLE §6 content density floor items 2 and 4 are waived per plan.md §5 and the RL Expert teaching spec §6. `trace_vector` calls are therefore not applicable to any phase of this video.

| Phase | Equation token | Source geometry | Color | Helper |
|---|---|---|---|---|
| — | No trace_vector pairs — see declaration above | — | — | — |

---

## 9. Hand-off Notes for the Manim Expert

**1. Helpers to import — complete list for this video.**
Import only from the helper library (no MathTex, no DP helpers):
`frozenlake_frame`, `smooth_move_to`, `pan_to_follow`, `place_caption`, `show_header`, `zoom_to`, `zoom_reset`
from `manim_service.scenes.panels` and `manim_service.scenes.motion`.
Do NOT import: `ValueHeatmap`, `QValueTable`, `CodeStepper`, `BackupDiagram`, `PolicyArrowGrid`, `EpisodeTrail`, `ActionBarChart`, `SpriteActionBinding`, `SynchronizedFocusGroup`, `trace_vector`, `cross_highlight_pair`, `equation_morph`.

**2. Opacity transitions in Phase 3 — implementation pattern.**
Every time a new loop element is Created, the prior loop elements must dim in the SAME `self.play(...)` call:
```python
# Example: env_box enters, agent_box dims simultaneously
self.play(
    Create(env_box),
    agent_box.animate.set_opacity(OPACITY_SECONDARY),
    run_time=0.8
)
```
This single-call pattern ensures both animations share the same eased timeline (STYLE_BIBLE §17 multi-element reposition rule). Do NOT dim in a separate subsequent play call — that would create a visible sequential flicker.

**3. Phase 3 upper-channel arrow geometry — exact implementation.**
- `state_obs_arrow = CurvedArrow(env_box.get_top() + LEFT * 0.4, agent_box.get_top() + RIGHT * 0.4, angle=-PI/3, color=STATE_COLOR)`
  Label VGroup: `state_label.next_to(state_obs_arrow.get_center(), UP, buff=0.22)` (above the outer arc)
- `reward_arrow = CurvedArrow(env_box.get_top() + LEFT * 0.8, agent_box.get_top() + RIGHT * 0.8, angle=-PI/4, color=REWARD_COLOR)`
  Label: `reward_label.next_to(reward_arrow.get_center(), UP, buff=0.18)` then `.shift(RIGHT * 0.3)` to clear state_obs label horizontally
- Verify no label bounding-box overlap after placement. Both arrows start at slightly different x positions on the env_box top edge to give them visually distinct roots.

**4. Action arrow geometry.**
- `action_arrow = CurvedArrow(agent_box.get_bottom() + RIGHT * 0.4, env_box.get_bottom() + LEFT * 0.4, angle=PI/3, color=ACTION_COLOR)`
  Label: `action_label.next_to(action_arrow.get_center(), DOWN, buff=0.22)`

**5. FrozenLake grid re-entry in Phase 7 — exact specification (Special Design Challenge 4).**
Phase 7 FrozenLake ghost:
```python
frozenlake_ghost = frozenlake_frame(state=15)  # show goal reached state
frozenlake_ghost.scale(0.65)
frozenlake_ghost.move_to(LEFT * 3.8 + DOWN * 0.15)  # place_left_panel anchor
self.play(FadeIn(frozenlake_ghost, run_time=0.8), rate_func=smooth)
frozenlake_ghost.set_opacity(OPACITY_SECONDARY)  # 0.4 — REFRAME tag, visual bridge only
```
This is a REFRAME motion per §5 Phase 7 choreography. The ghost anchors LEFT per plan.md §8 Phase 7 hemisphere matrix (LEFT: FrozenLake OPACITY_SECONDARY). The 65% scale leaves center and right canvas unoccluded for takeaway text and closing text. This is not a PRIMARY element — it is purely a visual bridge (STYLE_BIBLE §23 re-entry).

**6. Elf sprite direction changes — complete mapping.**
| Step | From → To | Sprite file | Direction |
|------|-----------|-------------|-----------|
| tile 0 → tile 1 | start | `elf_right.png` | RIGHT |
| tile 1 → tile 2 | continue | `elf_right.png` | RIGHT |
| tile 2 → tile 6 | swap | `elf_down.png` | DOWN |
| tile 6 → tile 7 | continue | `elf_down.png` | DOWN |
| (reset to tile 0) | | `elf_right.png` | — |
| tile 0 → tile 4 | start 1c | `elf_down.png` | DOWN |
| tile 4 → tile 8 | continue | `elf_down.png` | DOWN |
| tile 8 → tile 12 | continue | `elf_down.png` | DOWN |
| (reset to tile 0) | | `elf_down.png` | — |
| tile 0 → tile 4 | start 1d | `elf_down.png` | DOWN |
| tile 4 → tile 8 | continue | `elf_down.png` | DOWN |
| tile 8 → tile 9 | swap | `elf_right.png` | RIGHT |
| tile 9 → tile 10 | continue | `elf_right.png` | RIGHT |
| tile 10 → tile 14 | swap | `elf_down.png` | DOWN |
| tile 14 → tile 15 | swap | `elf_right.png` | RIGHT |
Implement sprite swap as: `self.play(FadeOut(elf_sprite, run_time=0.15), FadeIn(elf_sprite_new, run_time=0.15))` at the start of each step where the direction changes. The run_time of 0.15 s is sub-perceptual; the viewer sees a smooth direction change.

**7. smooth_move_to run_time compliance.**
All elf steps cover ~1.0–1.2 units (one tile). Use `run_time=1.0` throughout (plan.md §11 item 7 notes 0.9 s minimum; 1.0 s is the safe value). STYLE_BIBLE §17 mandates minimum 0.9 s for distances < 2 units.

**8. Phase 2 panels — three-panel horizontal layout.**
Panels arranged with `VGroup(supervised_panel, unsupervised_panel, rl_panel).arrange(RIGHT, buff=0.35)` centered at x=0. Each panel ≈ 2.8 wide × 3.2 tall, total width ≈ 9.3 + buffers ≈ 9.5 units. This spans most of the 14-unit canvas width — check that no panel extends beyond x=±6.0. If the total exceeds the safe zone, reduce each panel width to 2.5 units and font sizes proportionally.

**9. Feature cards Phase 6 — stacked vertical layout.**
`VGroup(card_1, card_2).arrange(DOWN, buff=0.3)` centered at x=0, y=0. Each card ≈ 5.0 wide × 1.8 tall (enough to hold two-line body text at font_size=18 without wrapping). Confirm with a dev render.

**10. Ingestion wait after zoom_reset in Phase 1e.**
The sequence is: caption → wait(1.5) → `zoom_reset` (run_time=1.6) → `ingestion_wait(2.5)` → FadeOut(frozenlake_grid) → `ingestion_wait(2.5)` before Phase 2. The `ingestion_wait` after zoom_reset is mandatory (STYLE_BIBLE §18: "a camera `zoom_to` / `zoom_reset`" qualifies as a major structural morph). Do not collapse the two ingestion_waits into one.

**11. Phase 4 Indicate — non-indicated nodes at OPACITY_SECONDARY.**
During each Indicate call in Phase 4, the non-indicated loop elements should be at OPACITY_SECONDARY (0.4). Implement as: before the first Indicate, set all five loop elements to SECONDARY; then each Indicate brings its target momentarily to PRIMARY via the scale_factor pulse. The SECONDARY state of the non-targets is maintained passively (they were already dimmed in Phase 3). The Indicate animation internally handles the scale-up/down — do not manually set_opacity to PRIMARY before calling Indicate; Manim's Indicate already provides the brightness/scale flash at default opacity.

**12. Series opening frame note.**
Phase 1a begins immediately with `show_header` then grid FadeIn. There is no prior video reference (Video 1 of 15). The header is the opening frame. Do not add a "previous video" bridge.

**13. Validation of success path before coding.**
Verify `0→4→8→9→10→14→15` against `env.unwrapped.desc` to confirm none of these tiles are holes. Expected hole set: {5, 7, 11, 12}. Success path is clear. (From plan.md §11 "For the Technical Validator.")
