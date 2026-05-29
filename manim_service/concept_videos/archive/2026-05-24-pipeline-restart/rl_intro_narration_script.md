# Narration Script — rl_intro

**Date:** 2026-05-21
**Target duration:** ~218 s (narration-matched render); narration tracks visual cues within ±2.0 s
**plan.md reference:** /Users/ultramarine/Desktop/grad_project/manim_service/concept_videos/rl_intro_plan.md
**MP4 reference:** /Users/ultramarine/Desktop/grad_project/media/videos/rl_intro_concept/480p15/RLIntroConcept.mp4
**Voice:** am_michael · Kokoro v1.0 · speed 1.0 · 24 kHz
**BGM:** None (STYLE_BIBLE §12)

---

## Phase timing reference

Derived from plan.md §9 pacing budget, scaled to narration-matched ~218 s render.
Ingestion waits and animation runtimes are folded in. Sub-phase boundaries are approximate;
the synthesiser places each line at its declared cue and shifts later lines if a clip overruns.

| Phase | Sub-phase | Start | End | Duration |
|---|---|---|---|---|
| 1a | Grid introduction | 00:00 | 00:06 | ~6 s |
| 1b | Attempt 1 — hole at tile 7 | 00:06 | 00:15 | ~9 s |
| 1c | Attempt 2 — hole at tile 12 | 00:15 | 00:22 | ~7 s |
| 1d | Attempt 3 — success | 00:22 | 00:34 | ~12 s |
| 1e | Phase 1 closing caption + fade | 00:34 | 00:40 | ~6 s |
| 2 | Three-way ML contrast | 00:40 | 00:59 | ~19 s |
| 3a | Agent box | 00:59 | 01:03 | ~4 s |
| 3b | Environment box | 01:03 | 01:10 | ~7 s |
| 3c | Action arrow | 01:10 | 01:15 | ~5 s |
| 3d | State / Observation arrow | 01:15 | 01:23 | ~8 s |
| 3e | Reward arrow | 01:23 | 01:29 | ~6 s |
| 3f | Full loop — misconception caption | 01:29 | 01:35 | ~6 s |
| 4 | Loop cycle ×2 | 01:35 | 02:00 | ~25 s |
| 5 | Path contrast + cumulative reward | 02:00 | 02:17 | ~17 s |
| 6 | Named-feature cards | 02:17 | 02:37 | ~20 s |
| 7 | Takeaway + closing connection | 02:37 | 02:49 | ~12 s |

---

## Phase 1a — Grid Introduction

[00:00:02] A four-by-four *FrozenLake* grid appears — sixteen tiles of ice.
[00:00:05] The bottom-right tile is the goal. Four dark holes wait between here and there.

---

## Phase 1b — Attempt 1: Elf Falls into Hole (Tile 7)

[00:00:07] The elf starts at the top-left corner and steps right — then right again, then down.
[00:00:11] The ice is slippery. The elf lands on a hole and vanishes.
[00:00:14] It returns to the start, having learned nothing yet — only that one path failed.

---

## Phase 1c — Attempt 2: Elf Falls Again (Tile 12)

[00:00:17] A second attempt: the elf steps down three tiles in a row.
[00:00:20] A different hole. The same outcome.
[00:00:22] No one tells the elf which moves are safe — it can only observe what happens.

---

## Phase 1d — Attempt 3: Success

[00:00:24] On the third attempt, the elf finds a different path.
[00:00:27] It reaches the *goal* tile.
[00:00:30] A single number appears: plus one. That is the *reward* — the signal that this outcome was good.

---

## Phase 1e — Phase 1 Closing Caption

[00:00:34] This is the reinforcement learning problem: learn to act by interacting — no labels, just *rewards*.

---

## Phase 2 — Three-Way ML Contrast

[00:00:42] Three learning paradigms side by side.
[00:00:45] Supervised learning trains from labeled examples: an input paired with the correct answer.
[00:00:50] Unsupervised learning finds hidden structure in data — no labels and no rewards.
[00:00:54] *Reinforcement learning* is different from both.
[00:00:56] The agent receives no labels. There is no supervisor. Only a reward signal.
[00:00:59] The agent must discover which actions are good — the supervisor does not exist.

---

## Phase 3a — Agent Box

[00:01:01] The *Agent* — the decision-maker in the loop.

---

## Phase 3b — Environment Box

[00:01:05] The *Environment* — everything outside the agent.
[00:01:08] The elf navigating FrozenLake is an agent. The grid itself is the environment.

---

## Phase 3c — Action Arrow

[00:01:12] The agent chooses an *Action* — one direction to step on each time step.

---

## Phase 3d — State / Observation Arrow

[00:01:17] The environment sends back a *State* — what the agent perceives after acting.
[00:01:21] In FrozenLake, the elf sees exactly which tile it occupies. That is its state.

---

## Phase 3e — Reward Arrow

[00:01:24] The environment also sends a *Reward* — a single number signaling how well the last action went.
[00:01:28] In FrozenLake that reward is one at the goal and zero everywhere else.

---

## Phase 3f — Full Loop Visible

[00:01:31] The loop is now complete: Agent and Environment, connected by Action, State, and Reward.
[00:01:34] Not every environment reveals its full state — the elf is an unusually transparent case.

---

## Phase 4 — The Loop Repeats (Cycle ×2)

[00:01:37] At every *time step*: the agent observes the state.
[00:01:40] It chooses an action.
[00:01:42] The environment reacts and returns a new state and a reward.
[00:01:46] Then the agent observes again — and the cycle continues.
[00:01:50] This repeats on every time step, for the length of the entire episode.

---

## Phase 5 — Path Contrast and Cumulative Reward

[00:02:02] Two paths on the same grid — one successful, one not.
[00:02:05] The green trail reaches the goal and collects a *reward* of one.
[00:02:08] The red trail ends at a hole — reward zero.
[00:02:11] The agent's goal is to accumulate reward across the whole *episode* — not just survive the next step.
[00:02:15] Rewards can be positive, zero, or negative — the exact values depend on the environment.

---

## Phase 6 — Named RL Features

[00:02:19] The first distinguishing feature of reinforcement learning: *Trial-and-Error Search*.
[00:02:23] The agent must explore — no supervisor labels which action is correct.
[00:02:27] The second distinguishing feature: *Delayed Reward*.
[00:02:31] An action now may affect rewards many steps later.
[00:02:34] The agent also faces a tension — try known good actions, or explore new ones. We will return to this.

---

## Phase 7 — Takeaway and Closing Connection

[00:02:38] Reinforcement learning is the science of learning to act by trial and error — no labels, just rewards.
[00:02:43] The Agent, the Environment, the loop — that is reinforcement learning.
[00:02:46] In the next video, we give this loop a precise mathematical home: the *Markov Decision Process*.

---

## Synthesis notes

- All cues are approximate (±1.0 s against visual beat). The synthesiser shifts later lines
  if any clip overruns its window.
- No math notation in this script — the video contains no equations (plan §5 exemption).
- The term "Markov Decision Process" in Phase 7 is spoken for the first time as a forward
  reference only; it is not defined here. The Transcript Writer must include it in captions
  even if the visual only shows the closing text.
- "Plus one" (Phase 1d) and "reward zero" (Phase 5) are the spoken forms of the on-screen
  labels "+1" and "0" — no raw numeric symbols read aloud.
