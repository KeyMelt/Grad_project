# Plan: rl_intro — What Is Reinforcement Learning?

**lesson_id:** `rl_intro`
**Manim class:** `RLIntroConcept`
**Scene file:** `manim_service/concept_videos/rl_intro_concept.py`
**Target duration:** 420–600 s (7–10 min)
**RL Expert status:** APPROVED (flags incorporated — see §10 RL Expert Collaboration Notes)

---

## 1. Narrative Hook

The elf stands at the top-left corner of a frozen lake. The ice is slippery, the
goal tile glows green in the distance, and four dark holes wait between here and
there. Nobody hands the elf a map. Nobody tells it which way to step. The viewer
watches it shuffle right, slip sideways, land on a hole, and vanish. It reappears
at the start. This time it goes down, then right — and falls again. On the third
attempt, threading a different path, it reaches the goal tile and a single reward
signal lights up. That is the whole problem: the elf must figure out how to reach
the goal by trying actions and seeing what happens — no labels, no supervisor, just
the outcome of each step. Before a single abstract term is named, the viewer already
understands why something smarter than random guessing would be useful here.

---

## 2. Color Palette Declaration

| Constant | Hex | Used for |
|---|---|---|
| `STATE_COLOR` | `#38BDF8` | Environment box border, State / Observation arrow and label, FrozenLake grid-cell outlines |
| `REWARD_COLOR` | `#34D399` | Goal tile border/label, Reward arrow and label, RL box border in ML contrast diagram, takeaway caption accent |
| `PENALTY_COLOR` | `#F87171` | Hole tile borders/fills, failed-path highlight in Phase 5 path contrast |
| `POLICY_COLOR` | `#A78BFA` | Agent box border and fill in loop diagram (agent acts under a future policy, per RL Expert flag) |
| `ACTION_COLOR` | `#FB923C` | Action arrow and label in loop diagram |
| `BG_COLOR` | `#020617` | Scene background (`camera.background_color`) |
| `BG_PANEL` | `#0F172A` | Panel fill for RoundedRectangle containers (ML contrast boxes, loop boxes) |
| `BG_GRID` | `#1E293B` | FrozenLake safe-tile background (at 0.15 opacity) |
| `CODE_ACCENT` | `#64748B` | Panel title text for ML contrast diagram headers, muted annotation text |

**Color not used in this video:** `VALUE_COLOR` — no value functions appear.
No `MathTex` color assignments are needed because this video contains no equations.

---

## 3. Reserved-Hemisphere Layout Matrix (STYLE_BIBLE §16)

| Phase | LEFT (≈ −5.0 to −1.5 x) | CENTER (≈ −1.5 to +1.5 x) | RIGHT (≈ +1.5 to +5.0 x) |
|---|---|---|---|
| 1a | — | FrozenLake grid (full size, via `frozenlake_frame`) | — |
| 1b | — | FrozenLake grid + elf walk animation | — |
| 1c | — | FrozenLake grid + elf success path | — |
| 2 | — | Three-box ML contrast diagram (full-width) | — |
| 3 | — | RL loop diagram: Agent box (left-of-center) + Environment box (right-of-center), arrows between | — |
| 4 | — | RL loop diagram (cycle animation × 2) | — |
| 5 | FrozenLake grid dims to OPACITY_SECONDARY; migrates LEFT after Phase 4 FadeOut and re-entry | Path comparison visual (two-path annotation) centered | Right annotation note: reward = 0 vs reward = 1 labels |
| 6 | FrozenLake grid at OPACITY_SECONDARY (static reference) | Named-feature labels: "Trial-and-Error" + "Delayed Reward" (staggered) | — |
| 7 | FrozenLake at OPACITY_SECONDARY (FadeOut at end) | Takeaway caption + closing connection text | — |

**Migration rule for Phase 5:** The RL loop diagram from Phases 3–4 FadesOut completely before Phase 5 begins. The FrozenLake grid re-enters CENTER at reduced size, then both paths animate on it. No element from Phases 3–4 persists at PRIMARY into Phase 5.

**Migration rule for Phase 6:** The Phase 5 FrozenLake grid scales down and migrates LEFT, dimming to OPACITY_SECONDARY. Center is cleared for the named-feature label sequence.

---

## 4. Phase Sequence

### Phase 1 — FrozenLake: The Problem Without a Name

**Goal:** Show the RL problem concretely before any theory. The elf navigates by trial
and error. No abstract terms yet.

**Subphase 1a — Grid Introduction**

**Visual:** The 4×4 FrozenLake grid fades in at CENTER, full size. Tiles appear:
- Start tile (S) in top-left: `stool.png` wrapped via `frozenlake_frame`
- Goal tile (G) in bottom-right: `goal.png` with `REWARD_COLOR` border
- Hole tiles at positions {5, 7, 11, 12}: `hole.png` with `PENALTY_COLOR` border
- Safe tiles: `ice.png` with `BG_GRID` fill at 0.15 opacity
- Elf sprite appears at S: `elf_right.png`

**Helpers:**
```
show_header("What Is Reinforcement Learning?",
            subtitle="Learning by interacting with an environment")
frozenlake_frame(state=0)  # renders full 4×4 grid composite
```
Tiles appear via `LaggedStart([FadeIn(tile) for tile in grid_tiles], lag_ratio=0.1)`.
Goal tile border pulses once with `Indicate(goal_border, color=REWARD_COLOR)`.
Hole borders pulse with `Indicate(hole_borders, color=PENALTY_COLOR)`.

**Caption:** "The elf wants to reach the goal — but the ice is slippery and there
are holes."

**Wait:** `self.wait(2.0)` ← first geometry reveal minimum (STYLE_BIBLE §6)

---

**Subphase 1b — Attempt 1: Elf Falls in Hole**

**Visual:** The elf sprite navigates the grid using `smooth_move_to` steps. Path:
S(0) → RIGHT(1) → RIGHT(2) → DOWN(6) → DOWN(7, hole). The elf reaches tile 7
(hole), a `PENALTY_COLOR` flash covers the tile briefly, elf sprite fades and
reappears at S(0). Caption changes. This is the non-optimal walk mandated by the
RL Expert flag — the elf must fall into at least one hole before succeeding.

**Helpers:**
```
pan_to_follow(scene, elf_sprite, path=[tile_0, tile_1, tile_2, tile_6, tile_7])
```
Each step: `smooth_move_to(elf, tile_n, run_time=0.7)` with directional sprite swap
(`elf_right.png` for horizontal moves, `elf_down.png` for vertical).
On reaching tile 7: `Flash(hole_tile_7, color=PENALTY_COLOR, flash_radius=0.4)`,
then `FadeOut(elf_sprite)`, `FadeIn(elf_sprite.move_to(tile_0))`.

**Caption:** "The elf doesn't know the rules of the ice — it only sees what happens
after each step."

**Wait:** `self.wait(2.0)` ← after failure animation settles

---

**Subphase 1c — Attempt 2: Elf Falls Again (Second Non-Optimal Path)**

**Visual:** Elf tries again: S(0) → DOWN(4) → DOWN(8) → DOWN(12, hole). Different
hole, same outcome. `PENALTY_COLOR` flash, elf resets to S.

**Helpers:** Same `smooth_move_to` chain with `elf_down.png`.
`Flash(hole_tile_12, color=PENALTY_COLOR)`, reset.

**Caption:** "No one tells it the right moves — it has to figure them out."

**Wait:** `self.wait(1.5)`

---

**Subphase 1d — Attempt 3: Elf Reaches Goal (Success)**

**Visual:** Elf navigates: S(0) → DOWN(4) → RIGHT(5)… wait — tile 5 is a hole.
Path must avoid {5,7,11,12}. Safe route: S(0) → DOWN(4) → DOWN(8) → RIGHT(9) →
RIGHT(10) → DOWN(14) → RIGHT(15, goal). Elf enters goal tile.
`Flash(goal_tile, color=REWARD_COLOR, flash_radius=0.6)`.
A reward label `Text("+1", color=REWARD_COLOR)` floats briefly above the goal tile
and fades. Elf pauses at G.

**Helpers:**
```
smooth_move_to(elf, tile_4, run_time=0.7)   # DOWN
smooth_move_to(elf, tile_8, run_time=0.7)   # DOWN
smooth_move_to(elf, tile_9, run_time=0.7)   # RIGHT
smooth_move_to(elf, tile_10, run_time=0.7)  # RIGHT
smooth_move_to(elf, tile_14, run_time=0.7)  # DOWN
smooth_move_to(elf, tile_15, run_time=0.7)  # RIGHT
Flash(goal_tile, color=REWARD_COLOR)
FadeIn(reward_label_plus1)
self.wait(1.0)
FadeOut(reward_label_plus1)
```

**Caption:** "When the elf reaches the goal, it receives a reward — a single
number that says 'that was good.'"

**Note:** Reward is +1 (not "score"). Caption avoids "score" per spec §11.
Rewards can be 0 or 1 only in this environment (no negatives) — secondary
misconception guard handled in Phase 5 caption.

**Wait:** `self.wait(2.0)`

**Subphase 1e — Phase 1 Closing Caption**

**Caption (final Phase 1):** "This is the reinforcement learning problem: learn to
act by interacting, with no labels — only rewards."

**Wait:** `self.wait(1.5)`

`FadeOut(frozenlake_grid)` — grid exits before Phase 2. Phase 2 uses CENTER clean.
`self.ingestion_wait(2.5)` ← panel FadeOut is a major structural composition change.

---

### Phase 2 — What RL Is NOT: The Three-Way ML Contrast

**Goal:** Distinguish RL from supervised and unsupervised learning. Defeat the
primary misconception ("RL is supervised learning with delayed feedback") visually.

**Visual:** Three `RoundedRectangle` panels appear sequentially in CENTER, arranged
horizontally. Each panel is ~2.8 units wide × 3.2 units tall with `BG_PANEL` fill.

**Panel 1 — Supervised Learning (appears first):**
- Title: `Text("Supervised Learning", font_size=20, color=WHITE)`
- Body: `Text("Learns from labeled examples", font_size=18, color=CODE_ACCENT)`
- Mini-illustration: a simple icon — `Text("(input → correct label)", font_size=16, color=CODE_ACCENT)`
- Bottom text: `Text("A supervisor knows the right answer", font_size=16, color=CODE_ACCENT)`

**Panel 2 — Unsupervised Learning (appears second, via LaggedStart with lag_ratio=0.4):**
- Title: `Text("Unsupervised Learning", font_size=20, color=WHITE)`
- Body: `Text("Finds hidden structure in data", font_size=18, color=CODE_ACCENT)`
- Bottom text: `Text("No labels, no rewards", font_size=16, color=CODE_ACCENT)`

**Panel 3 — Reinforcement Learning (appears last, ~0.8 s after Panel 2):**
- Title: `Text("Reinforcement Learning", font_size=20, color=REWARD_COLOR)` ← border uses REWARD_COLOR to draw the eye
- Body: `Text("Learns by trial and error", font_size=18, color=WHITE)`
- Sub-line: `Text("No labels — just rewards", font_size=18, color=REWARD_COLOR)`
- Bottom text: `Text("No supervisor, no dataset", font_size=16, color=CODE_ACCENT)`
- A `Text("?", font_size=32, color=POLICY_COLOR)` floats above the RL panel briefly to indicate the agent's uncertainty — then fades, replaced by a `REWARD_COLOR` arrow icon pointing to the panel.

**Helpers:**
```
LaggedStart(
    FadeIn(supervised_panel),
    FadeIn(unsupervised_panel),
    FadeIn(rl_panel),
    lag_ratio=0.5
)
```
After all three are visible: `Indicate(rl_panel_border, color=REWARD_COLOR, scale_factor=1.08)` — one pulse to confirm RL is the focus.

**Caption (after all three appear):** "RL is a third paradigm — no labeled examples,
no supervisor, just a reward signal."

**Wait:** `self.wait(2.0)` ← first geometry reveal of contrast diagram
`self.ingestion_wait(2.5)` ← RL panel FadeIn completes a structural composition change

**Caption update:** "The agent must discover which actions are good — the supervisor
does not exist."

**Wait:** `self.wait(2.0)`

`FadeOut(all_three_panels)` ← clean exit before Phase 3.
`self.ingestion_wait(2.5)` ← panel FadeOut is a major structural change.

---

### Phase 3 — The Abstract RL Loop Diagram

**Goal:** Abstract the FrozenLake problem into the two-box agent–environment loop.
Introduce the four loop elements with color binding. Resolve the "State /
Observation" dual-label.

**Visual sequence (staggered, not simultaneous):**

**3a — Agent box:**
`RoundedRectangle(width=2.8, height=1.6, corner_radius=0.18,
                  stroke_color=POLICY_COLOR, fill_color=BG_PANEL)`
appears at CENTER-LEFT (x ≈ −2.2), labeled `Text("Agent", font_size=24, color=POLICY_COLOR)`.
Caption: "The Agent — the decision-maker."
`self.wait(1.5)`

**3b — Environment box:**
`RoundedRectangle(width=2.8, height=1.6, corner_radius=0.18,
                  stroke_color=STATE_COLOR, fill_color=BG_PANEL)`
appears at CENTER-RIGHT (x ≈ +2.2), labeled `Text("Environment", font_size=24, color=STATE_COLOR)`.
Caption: "The Environment — everything the agent interacts with."
`self.wait(1.5)`
`self.ingestion_wait(2.5)` ← FadeIn of second box is a structural composition change.

**3c — Action arrow (Agent → Environment):**
`CurvedArrow` from Agent box (bottom-right) to Environment box (bottom-left),
curving downward. Color: `ACTION_COLOR`. Label: `Text("Action", font_size=20, color=ACTION_COLOR)`.
Caption: "The Agent chooses an Action."
`self.wait(1.5)`

**3d — State / Observation arrow (Environment → Agent):**
`CurvedArrow` from Environment box (top-left) to Agent box (top-right),
curving upward. Color: `STATE_COLOR`.
Label is a two-line `VGroup`:
```
label_top = Text("State", font_size=20, color=STATE_COLOR)
label_bot = Text("/ Observation", font_size=16, color=STATE_COLOR,
                 fill_opacity=0.7)
VGroup(label_top, label_bot).arrange(DOWN, buff=0.05)
```
The two-line stacked label sits on the upward arrow. This is the visual solution
for the "State / Observation" dual-label requirement: a single arrow carries
both terms, with "/ Observation" in smaller text and slightly dimmer opacity to
signal it is a qualifier, not a second distinct concept.
Caption: "The Environment sends back the State — what the agent perceives."
`self.wait(1.5)`
`self.ingestion_wait(2.5)` ← arrow FadeIn completes a structural composition change.

**3e — Reward arrow (Environment → Agent, alongside state arrow):**
The reward arrow shares the upward channel but is drawn as a second `CurvedArrow`
below the state/observation arrow (or alongside it), color `REWARD_COLOR`.
Label: `Text("Reward", font_size=20, color=REWARD_COLOR)`.
Caption: "The Environment also sends a Reward — a single number."
`self.wait(1.5)`
`self.ingestion_wait(2.5)` ← third arrow completes the loop diagram (structural composition change).

**3f — Full loop revealed, misconception guard caption:**
Caption: "In FrozenLake, the elf sees its exact state — not always the case in RL."
`self.wait(2.0)` ← loop diagram now fully visible, first geometry reveal of the complete loop.

---

### Phase 4 — The Cycle: The Loop Repeats

**Goal:** Make the repeating nature of the RL loop visceral. Run two full cycles.

**Visual:** The complete loop diagram from Phase 3 remains on screen.
`pan_to_follow` / camera slightly zooms to fit the loop tighter if needed
(zoom_to scale ≈ 0.75 to give loop room without showing empty canvas).

**Cycle 1 animation (sequential `Indicate`/`Circumscribe`):**
1. `Indicate(agent_box, color=POLICY_COLOR, scale_factor=1.1)` — Agent observes
2. `Indicate(action_arrow, color=ACTION_COLOR, scale_factor=1.1)` — Action fires
3. `Indicate(environment_box, color=STATE_COLOR, scale_factor=1.1)` — Environment reacts
4. `Indicate(state_arrow, color=STATE_COLOR, scale_factor=1.1)` — State returned
5. `Indicate(reward_arrow, color=REWARD_COLOR, scale_factor=1.1)` — Reward returned
6. `Indicate(agent_box, color=POLICY_COLOR, scale_factor=1.1)` — Agent observes again

Each Indicate: `run_time=0.6`. Pause `self.wait(0.4)` between each node
(assimilation_wait minimum 0.6 s total = 0.6 s; using 0.4+0.6 = 1.0 s per node including the animation).

Caption during cycle 1: "At every time step: observe state, choose action, receive reward."

`self.wait(1.5)` ← after cycle 1 completes.

**Cycle 2 animation (same sequence, slightly faster run_time=0.5 per node):**
Caption: "This repeats on every time step."
`self.wait(1.5)` ← after cycle 2 completes.

`self.ingestion_wait(2.5)` ← end of SynchronizedFocusGroup-equivalent step sequence.

`zoom_reset(scene)` — return to wide frame.

`FadeOut(loop_diagram_all)` — complete loop exits. Phase 5 starts clean.
`self.ingestion_wait(2.5)` ← diagram FadeOut is a major structural composition change.

---

### Phase 5 — Reward Signal and Cumulative Goal

**Goal:** Show that the agent's goal is cumulative reward over the entire episode,
not just the next step. Address secondary misconception (rewards are not always positive).
Use FrozenLake path contrast.

**Visual:** FrozenLake grid re-enters CENTER at slightly reduced size (via
`frozenlake_frame`, same asset set). Two paths drawn on the grid simultaneously:

- **Path A (success):** Trace the same success path from Phase 1 subphase 1d
  (0→4→8→9→10→14→15). Path drawn as a `REWARD_COLOR` trail of
  `DashedLine` segments connecting tile centers. Elf sprite walks this path ending
  at G. Reward label `+1` appears at G in `REWARD_COLOR`.
- **Path B (failure):** A second overlaid trail shows a failed path in `PENALTY_COLOR`
  (e.g., 0→1→2→6→7, ending at hole 7). No elf sprite on this path — just the colored
  dashed trail. A `×` mark in `PENALTY_COLOR` at tile 7. Reward label `0` in
  `CODE_ACCENT` (neutral, not rewarded).

Both paths visible simultaneously after being drawn sequentially:
`LaggedStart(Write(path_A_trail), Write(path_B_trail), lag_ratio=0.6)`.

Caption: "The agent wants to accumulate reward over the whole episode — not just survive the next step."
`self.wait(2.0)`

Caption update: "Rewards can be positive, zero, or negative — the exact values depend on the environment."
`self.wait(1.5)`

Caption update: "The goal: more total reward over time."
`self.wait(1.5)`

`FadeOut(frozenlake_grid_with_paths)` — exits clean.
`self.ingestion_wait(2.5)` ← panel FadeOut is a structural change.

---

### Phase 6 — Trial-and-Error and Delayed Reward: Named RL Features

**Goal:** Name the two distinguishing features of RL from S&B §1.1 p. 2. Address
exploration–exploitation at caption level only (per RL Expert flag — never animated).

**Visual:** Two named-feature cards appear sequentially in CENTER. No FrozenLake
grid (exits cleanly at end of Phase 5). Each card is a `RoundedRectangle`
(width ≈ 5.0, height ≈ 1.6, BG_PANEL fill, CODE_ACCENT stroke) with a bold label
and a one-line explanation.

**Card 1 — Trial-and-Error Search:**
```
Text("Trial-and-Error Search", font_size=26, color=WHITE, weight=BOLD)
Text("The agent must explore — no supervisor labels which action is correct.",
     font_size=18, color=CODE_ACCENT)
```
`FadeIn(card_1)` then `self.wait(2.0)`.

Caption: "RL's first distinguishing feature: the agent discovers good actions
by trying them." (S&B §1.1 p. 2)

**Card 2 — Delayed Reward (appears below Card 1, staggered):**
```
Text("Delayed Reward", font_size=26, color=WHITE, weight=BOLD)
Text("An action now may affect rewards many steps later.",
     font_size=18, color=CODE_ACCENT)
```
`FadeIn(card_2)` via `LaggedStart([FadeIn(card_1), FadeIn(card_2)], lag_ratio=0.6)`
(or card_2 enters after card_1 is already visible).
`self.wait(2.0)`

Caption: "RL's second distinguishing feature: reward may arrive long after the
action that caused it." (S&B §1.1 p. 2)

**Exploration–exploitation acknowledgment (caption only — never animated):**
Caption: "The agent also faces a challenge: try known good actions, or explore new ones — a tension we will return to."
`self.wait(1.5)`
This is a single caption. No animation, no diagram, no extra labels. Per RL Expert flag: named in one caption only; if this naturally expands it is trimmed.

`self.ingestion_wait(2.5)` ← FadeIn of both cards is a structural composition change.

`FadeOut(card_1)`, `FadeOut(card_2)` — both exit.
`self.ingestion_wait(2.5)` ← cards FadeOut is a structural change.

---

### Phase 7 — Takeaway and Closing Connection to mdp_framework

**Goal:** Consolidate the video into a single memorable sentence. Visually bridge
to the next video. Hold.

**Visual:**

**7a — Takeaway line:**
```
Text("Reinforcement learning is the science of learning to act",
     font_size=26, color=WHITE)
Text("by trial and error — no labels, just rewards.",
     font_size=26, color=REWARD_COLOR)
```
The two lines stack vertically in CENTER via `VGroup(...).arrange(DOWN, buff=0.2)`.
Both lines write in via `Write` with `LaggedStart(lag_ratio=0.3)`.

Caption: "The agent, the environment, the loop — that is reinforcement learning."

`self.wait(2.0)`

**7b — FrozenLake returns at reduced opacity for visual bridge:**
FrozenLake grid `FadeIn` at LEFT, `opacity=OPACITY_SECONDARY (0.4)`, small scale.
This is the "still visible" bridge the spec §10 Series Continuity Notes requires.

**7c — Closing connection:**
```
Text("Next: the Markov Decision Process", font_size=22, color=STATE_COLOR)
Text("We give this loop a precise mathematical home.", font_size=18, color=CODE_ACCENT)
```
`FadeIn` in CENTER below the takeaway line.

Caption: "In the next video, we formalize the loop — the Markov Decision Process."

`self.wait(2.5)` ← mandatory final hold (STYLE_BIBLE §6)

`FadeOut(everything)` — clean scene end.

---

## 5. STYLE_BIBLE §6 Content Density Floor — Exemption Note

**This video is exempt from STYLE_BIBLE §6 content density floor items 2 and 4.**

- **Item 2 (Theory section with equations):** Waived. This video contains no
  `MathTex`, no equations, and no `equation_morph` calls. The RL Expert's teaching
  spec (§6, "Allowed Expansions") explicitly states: "Any equation in MathTex —
  NOT PERMITTED in this video." The production brief RL Expert flags confirm:
  "No equations, no CodeStepper."

- **Item 4 (Code walkthrough with CodeStepper):** Waived. The teaching spec §3.6
  states: "This video uses FrozenLake visually only. No env.reset(), no env.step(),
  no env.unwrapped.P. No code panel. No CodeStepper." The `code_focus_lines` in
  the proposed `specs.py` entry is `()` (empty).

All other density floor items apply and are satisfied:
- Item 1 (Motivation): Phase 1 FrozenLake trial-and-error walk — SATISFIED.
- Item 3 (Visual demonstration): FrozenLake grid with elf walk, path contrast,
  loop diagram — SATISFIED (FrozenLake replaces ValueHeatmap as the visual demo for this conceptual video).
- Item 5 (Iteration demo): Not applicable — this video has no iterative algorithm.
- Item 6 (Boundary condition / misconception): The three-way ML contrast diagram
  (Phase 2) explicitly refutes "RL is supervised learning with delayed feedback" — SATISFIED.
- Item 7 (Closing connection): Phase 7 names `mdp_framework` — SATISFIED.

---

## 6. Cross-Highlight Matrix

**N/A — No CodeStepper, no equation panels.**

This video contains no `CodeStepper` and no `MathTex` equations. The
cross-highlight protocol (STYLE_BIBLE §15.2) applies only to phases containing
a CodeStepper. Cross-highlight protocol is not applicable to this video.

`trace_vector` annotations (STYLE_BIBLE §15.1) are also not applicable — there
are no equation tokens whose meaning needs to be grounded in geometric elements
because there are no equations.

---

## 7. Opacity Layer Assignments

**OPACITY_PRIMARY (1.0):**
- Phase 1: Active FrozenLake grid tiles, elf sprite, active hole/goal borders, active caption
- Phase 2: The panel currently being introduced (one at a time via LaggedStart), active caption
- Phase 3: The current loop element being introduced (one box or arrow at a time), active caption
- Phase 4: The currently-Indicated loop node/arrow during cycle animation
- Phase 5: FrozenLake grid, both path trails after draw, reward labels, active caption
- Phase 6: Current named-feature card being introduced, active caption
- Phase 7: Takeaway text lines, closing connection text, active caption

**OPACITY_SECONDARY (0.4):**
- Phase 2: Panels already introduced but not currently being spoken to (context support)
- Phase 3: Loop elements already revealed while a new element is being introduced
- Phase 4: Loop nodes NOT currently being Indicated during cycle animation
- Phase 5: FrozenLake background tiles (safe tiles at reduced opacity when paths are primary)
- Phase 6: First card after second card enters (both at PRIMARY momentarily, then card 1 dims to SECONDARY while caption speaks to card 2)
- Phase 7: FrozenLake grid re-entry at LEFT (entire grid at OPACITY_SECONDARY as a visual bridge)

**OPACITY_BACKGROUND (0.17):**
- Phase 1: FrozenLake ice/safe tile backgrounds (BG_GRID fill at 0.15 opacity per STYLE_BIBLE §1)
- Phase 7: FrozenLake grid at closing (may dim further if caption focus demands it)

---

## 8. Reserved-Hemisphere Matrix Per Phase (STYLE_BIBLE §16)

Detailed declaration — no element from a later phase may enter a hemisphere occupied
by a pedagogically-active earlier element without first relocating/fading that element.

| Phase | LEFT active element | CENTER active element | RIGHT active element | Migration event |
|---|---|---|---|---|
| 1a | — | FrozenLake grid (full size) | — | — |
| 1b–1d | — | FrozenLake + elf walk | — | — |
| 1e close | — | FrozenLake FadeOut | — | FadeOut → ingestion_wait(2.5) before Phase 2 |
| 2 | — | Three-box ML contrast (full-width) | — | All three boxes exit via FadeOut before Phase 3 |
| 3 | — | RL loop diagram: Agent (left-of-center) + Env (right-of-center) + 3 arrows | — | FadeOut before Phase 5 |
| 4 | — | RL loop (cycle animation) | — | FadeOut + ingestion_wait before Phase 5 |
| 5 | — | FrozenLake re-entry (centered, smaller) + path trails | Path annotation labels (small, right of grid) | FadeOut before Phase 6 |
| 6 | — | Feature cards (Trial-and-Error, Delayed Reward) | — | Cards FadeOut before Phase 7 |
| 7 | FrozenLake (OPACITY_SECONDARY, small) | Takeaway text + closing text | — | FadeOut all at scene end |

**No hemisphere conflict exists:** The FrozenLake grid exits CENTER before the ML
contrast diagram enters. The ML contrast diagram exits before the loop diagram enters.
The loop diagram exits before the Phase 5 path contrast enters. Each element owns
its hemisphere exclusively during its active phase.

---

## 9. Pacing Budget

### Phase-by-phase duration estimates

| Phase | Animation runtime | Wait calls | Subtotal |
|---|---|---|---|
| 1a — Grid intro | 1.5 s (LaggedStart tiles) | 2.0 s | ~3.5 s |
| 1b — Failure 1 (hole) | 3.5 s (5 steps × 0.7 s each) | 2.0 s | ~5.5 s |
| 1c — Failure 2 (hole) | 2.1 s (3 steps × 0.7 s) | 1.5 s | ~3.6 s |
| 1d — Success path | 4.2 s (6 steps × 0.7 s) | 2.0 s | ~6.2 s |
| 1e — Closing + FadeOut | 0.5 s caption | 1.5 s + ingestion 2.5 s | ~4.5 s |
| **Phase 1 total** | | | **~23 s** |
| 2 — ML contrast diagram | 3.0 s (3 panels LaggedStart) | 2.0 + 2.5 + 2.0 + 2.5 s | ~12 s |
| **Phase 2 total** | | | **~15 s** |
| 3a — Agent box | 0.8 s | 1.5 s | 2.3 s |
| 3b — Env box | 0.8 s | 1.5 + 2.5 s | 4.8 s |
| 3c — Action arrow | 0.8 s | 1.5 s | 2.3 s |
| 3d — State/Obs arrow | 0.8 s | 1.5 + 2.5 s | 4.8 s |
| 3e — Reward arrow | 0.8 s | 1.5 + 2.5 s | 4.8 s |
| 3f — Full loop caption | 0.0 s | 2.0 s | 2.0 s |
| **Phase 3 total** | | | **~21 s** |
| 4 — Cycle × 2 | 6 nodes × 0.6 s × 2 cycles = 7.2 s | 1.5 + 1.5 + 2.5 s | ~12.7 s |
| **Phase 4 total** | | | **~13 s** |
| 5 — Path contrast | 3.0 s (path trails) | 2.0 + 1.5 + 1.5 + 2.5 s | ~10.5 s |
| **Phase 5 total** | | | **~11 s** |
| 6 — Named features | 2.0 s (cards FadeIn) | 2.0 + 2.0 + 1.5 + 2.5 + 2.5 s | ~12.5 s |
| **Phase 6 total** | | | **~15 s** |
| 7 — Takeaway + close | 2.5 s (Write takeaway) | 2.0 + 2.5 s | ~7.0 s |
| **Phase 7 total** | | | **~7 s** |

### Explicit wait call list (scene order)

| Phase | After event | Wait call | Duration |
|---|---|---|---|
| 1a | Grid fully revealed (geometry entry) | `self.wait(2.0)` | 2.0 s |
| 1b | Elf falls in first hole + reset | `self.wait(2.0)` | 2.0 s |
| 1c | Elf falls in second hole + reset | `self.wait(1.5)` | 1.5 s |
| 1d | Elf reaches goal, reward label fades | `self.wait(2.0)` | 2.0 s |
| 1e | Phase 1 closing caption | `self.wait(1.5)` | 1.5 s |
| 1e | Grid FadeOut | `self.ingestion_wait(2.5)` | 2.5 s |
| 2 | All three boxes visible (geometry entry) | `self.wait(2.0)` | 2.0 s |
| 2 | RL panel FadeIn complete | `self.ingestion_wait(2.5)` | 2.5 s |
| 2 | Supervisor caption | `self.wait(2.0)` | 2.0 s |
| 2 | Contrast diagram FadeOut | `self.ingestion_wait(2.5)` | 2.5 s |
| 3a | Agent box appears | `self.wait(1.5)` | 1.5 s |
| 3b | Environment box appears | `self.wait(1.5)` | 1.5 s |
| 3b | Environment box FadeIn (structural) | `self.ingestion_wait(2.5)` | 2.5 s |
| 3c | Action arrow drawn | `self.wait(1.5)` | 1.5 s |
| 3d | State/Obs arrow drawn | `self.wait(1.5)` | 1.5 s |
| 3d | State/Obs arrow FadeIn (structural) | `self.ingestion_wait(2.5)` | 2.5 s |
| 3e | Reward arrow drawn | `self.wait(1.5)` | 1.5 s |
| 3e | Reward arrow FadeIn completes loop | `self.ingestion_wait(2.5)` | 2.5 s |
| 3f | Full loop visible (geometry reveal) | `self.wait(2.0)` | 2.0 s |
| 4 | Cycle 1 complete | `self.wait(1.5)` | 1.5 s |
| 4 | Cycle 2 complete | `self.wait(1.5)` | 1.5 s |
| 4 | End of cycle sequence | `self.ingestion_wait(2.5)` | 2.5 s |
| 4 | Loop diagram FadeOut | `self.ingestion_wait(2.5)` | 2.5 s |
| 5 | Path contrast revealed | `self.wait(2.0)` | 2.0 s |
| 5 | Misconception guard caption | `self.wait(1.5)` | 1.5 s |
| 5 | "Total reward" caption | `self.wait(1.5)` | 1.5 s |
| 5 | FrozenLake path contrast FadeOut | `self.ingestion_wait(2.5)` | 2.5 s |
| 6 | Trial-and-Error card visible | `self.wait(2.0)` | 2.0 s |
| 6 | Delayed Reward card visible | `self.wait(2.0)` | 2.0 s |
| 6 | Exploration–exploitation caption | `self.wait(1.5)` | 1.5 s |
| 6 | Cards FadeIn structural | `self.ingestion_wait(2.5)` | 2.5 s |
| 6 | Cards FadeOut | `self.ingestion_wait(2.5)` | 2.5 s |
| 7 | Takeaway text written | `self.wait(2.0)` | 2.0 s |
| 7 | **Final hold** | `self.wait(2.5)` | **2.5 s** |

### Total projected duration

Phase 1: ~23 s
Phase 2: ~15 s
Phase 3: ~21 s
Phase 4: ~13 s
Phase 5: ~11 s
Phase 6: ~15 s
Phase 7: ~7 s

Animation runtimes (all phases): ~35 s
Wait/ingestion calls sum: ~105 s

**Projected total: ~105 s animation + wait core. With narration pacing and caption
dwell time (each caption: ~4–8 s of narration audio), projected runtime is
approximately 420–540 s (7–9 min).**

This is within the 7–10 min target window. The plan is not underspecified — all
7 mandatory teaching beats are present with generous dwell times.

---

## 10. RL Expert Collaboration Notes

**Status:** RL Expert flags accepted and incorporated. This is the pre-brief
consultation outcome. The full teaching spec (`rl_intro_specs.md`) was authored
by the RL Expert and serves as the authoritative source of truth for this plan.

**Flags incorporated verbatim:**

1. **No equations, no CodeStepper.** STYLE_BIBLE §6 content density floor items
   2 and 4 do not apply. Exemption documented in §5 of this plan. No `MathTex`,
   no `equation_morph`, no `CodeStepper` appears anywhere in this plan.

2. **Agent box color: POLICY_COLOR (#A78BFA).** The Agent box border and label
   use `POLICY_COLOR` throughout. Documented in §2 Color Palette Declaration and
   in the Phase 3 visual description. Rationale noted: agent acts under a future
   policy.

3. **FrozenLake elf walk in Phase 1 must look non-optimal: the elf must fall
   into at least one hole before succeeding.** Phase 1 includes two explicit
   failures (Subphases 1b and 1c) before the success walk in Subphase 1d. The
   elf falls into hole 7 (attempt 1) and hole 12 (attempt 2) before navigating
   the success path on attempt 3.

4. **Exploration–exploitation: named in one caption only, never animated. If it
   naturally expands, trim it.** Phase 6 contains exactly one caption: "The agent
   also faces a challenge: try known good actions, or explore new ones — a tension
   we will return to." No animation, no card, no diagram is associated with this
   concept. The caption is single-use only.

5. **"State / Observation" dual label on the loop arrow — propose a visual
   solution.** Visual solution: a two-line `VGroup` label stacked on the upward
   arrow: `Text("State")` on top at full opacity, `Text("/ Observation")` below
   at slightly reduced opacity (fill_opacity=0.7) and smaller font (font_size=16
   vs 20). Both in `STATE_COLOR`. A single companion caption reads: "In FrozenLake,
   the elf sees its exact state — not always the case in RL." This seeds partial
   observability without teaching it.

6. **Target duration: 7–10 min. A beat sheet that projects under 6 min is
   underspecified.** Projected duration is 7–9 min. All seven mandatory teaching
   beats are present. No beats have been compressed.

**Pre-brief consultation outcome:** APPROVED (flags incorporated). Teaching spec
authored by RL Expert is treated as APPROVED guidance. Plan follows all S&B
citations (§1.1–1.3) and all "Do Not Oversimplify" constraints from spec §11.

**No RL Expert gate verdict required** per teaching spec status field: "ADVISORY —
no gate verdict required; intended as Script Writer input." RL Expert sign-off on
the rendered video occurs at the standard convergence gate (STYLE_BIBLE §22, item 1
and item 7).

---

## 11. Downstream Handoff Notes

### For the Visual Director (choreo.md)

1. **No equations, no CodeStepper, no SynchronizedFocusGroup.** The cross-highlight
   matrix (§6) is N/A. The sprite-math binding protocol (STYLE_BIBLE §26) applies
   only to Phase 1 elf walks — those are flavour motion before any algebra, so no
   `SpriteActionBinding` is required.

2. **Loop diagram geometry:** The two boxes (Agent, Environment) are positioned
   symmetrically around x=0 at approximately x=−2.2 and x=+2.2. The Action arrow
   curves below both boxes; the State/Observation and Reward arrows curve above
   (or to one side). The Visual Director should finalize exact curvature and
   label placement to avoid the two upper arrows overlapping. One option: State/Obs
   arrow curves above, Reward arrow runs as a parallel line with slight offset below
   the State/Obs arrow on the same upper channel. The dual-label stacking is
   specified; fine placement is the Visual Director's call.

3. **FrozenLake grid re-entry in Phase 5:** The grid re-enters at reduced size
   (approx 80% of Phase 1 size) to allow both path trails to be legible. The
   Visual Director should ensure hole tiles and goal tile remain distinguishable at
   this scale. If the 4×4 grid is too small at 80%, the Visual Director may
   increase to 90% and use a smaller font for path labels.

4. **Phase 6 feature cards:** Two `RoundedRectangle` cards stacked vertically in
   CENTER. The Visual Director should choose whether they appear side-by-side or
   stacked — stacked is recommended to keep each card wide enough to hold the
   two-line body text without wrapping.

5. **Camera moves:** Phase 4 cycle animation suggests a light zoom-to (≈ 0.75
   scale) to frame the loop diagram tightly. `zoom_reset` before Phase 5.
   Phase 1 elf walk may benefit from `pan_to_follow` if the grid is centered and
   the elf moves toward lower-right tiles far from center. The Visual Director
   owns the full camera shot list.

6. **Element lifecycle:** All seven phases have explicit FadeOut events. No
   element sits "stale" across phase boundaries. The Visual Director's lifecycle
   matrix should confirm each element's Phase OUT matches what this plan specifies.

7. **Cognitive load budget:** At no point in this video do more than 4 mobjects
   need to be at OPACITY_PRIMARY simultaneously. The most complex frame is Phase 3
   when all five loop elements (2 boxes + 3 arrows) are visible — but by that point
   earlier elements have dimmed to SECONDARY as each new element enters. The Visual
   Director should enforce opacity transitions so that only the newly-introduced
   element is at PRIMARY at the moment of introduction.

### For the Manim Expert (rl_intro_concept.py)

1. **No MathTex, no CodeStepper, no ValueHeatmap, no ActionBarChart,
   no BackupDiagram, no PolicyArrowGrid, no SynchronizedFocusGroup.**
   Import only: `frozenlake_frame`, `smooth_move_to`, `pan_to_follow`,
   `place_caption`, `show_header`, `zoom_to`, `zoom_reset` from the helper library.

2. **FrozenLake asset path:** `gymnasium/envs/toy_text/img/`. Wrap all assets via
   `frozenlake_frame()`, never raw `ImageMobject`. Fallback to colored rectangles
   if assets not found (STYLE_BIBLE §10).

3. **Elf sprite directionality:** Use `elf_right.png` for RIGHT moves, `elf_down.png`
   for DOWN moves. Swap the sprite (FadeOut/FadeIn or direct image swap) at each
   step change of direction. Phase 1 success path goes DOWN then RIGHT — sprite
   starts as `elf_down.png`, switches to `elf_right.png` at tile 9.

4. **Hole positions in 4×4 FrozenLake-v1 default map:**
   {5 (row=1,col=1), 7 (row=1,col=3), 11 (row=2,col=3), 12 (row=3,col=0)}.
   Verify via `env.unwrapped.desc` before hardcoding tile positions.

5. **Success path tiles:** 0→4→8→9→10→14→15. This path avoids all holes. Verify
   against the hole set above before rendering.

6. **subtitle hygiene:** `show_header("What Is Reinforcement Learning?",
   subtitle="Learning by interacting with an environment")` — no lesson_id in subtitle.

7. **Motion easing:** All `smooth_move_to` calls must use `run_time ≥ 0.9 s` for
   moves > 1 unit (STYLE_BIBLE §17). Elf steps use 0.7 s (< 1 unit per step on the
   grid) — this is within the < 2 unit distance threshold allowing 0.9 s minimum.
   At 0.7 s per step this is slightly below 0.9 s — the Manim Expert should adjust
   to 0.9 s per elf step to comply with STYLE_BIBLE §17 (distance ≈ 1.0–1.2 units
   per tile step; use 1.0 s to be safe).

8. **ingestion_wait vs wait:** Use `self.ingestion_wait(2.5)` (default) after every
   panel FadeIn/FadeOut and after the end of cycle animations. Use `self.wait(N)` for
   narrative pacing pauses. Both are required at their respective points (STYLE_BIBLE §18).

9. **Exploration–exploitation:** The caption in Phase 6 is the ONLY mention of
   this concept. Do not add any animation, diagram, or additional label. Single
   caption, single `self.wait(1.5)`, done.

10. **Scene class name:** `RLIntroConcept`. File: `rl_intro_concept.py`.
    Header: `show_header("What Is Reinforcement Learning?",
    subtitle="Learning by interacting with an environment")`.

### For the Technical Validator

Verification candidates (no on-screen numerics — these are background ground-truth checks):
- FrozenLake-v1 default reward on goal = 1.0 → `env.unwrapped.P[15][any_action]`
- FrozenLake-v1 hole states in 4×4 default map: {5, 7, 11, 12} → `env.unwrapped.desc`
- is_slippery=True by default → `gym.make("FrozenLake-v1").unwrapped.is_slippery`
- Success path 0→4→8→9→10→14→15 avoids all holes → manual verification against hole set

The Technical Validator's role is minimal for this video (no equations, no
Gymnasium API calls in the scene). Primary validation is the hole-set and reward
ground truth above.
