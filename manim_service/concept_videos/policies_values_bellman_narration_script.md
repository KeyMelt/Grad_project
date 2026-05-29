# Narration Script — policies_values_bellman

**Date:** 2026-05-27
**Target duration:** 1289.933 s (≈ 21 min 30 s)
**plan.md reference:** /Users/ultramarine/Desktop/grad_project/manim_service/concept_videos/policies_values_bellman_plan.md
**choreo.md reference:** /Users/ultramarine/Desktop/grad_project/manim_service/concept_videos/policies_values_bellman_choreo.md
**MP4 reference:** /Users/ultramarine/Desktop/grad_project/media/videos/policies_values_bellman_concept/480p15/PoliciesValuesBellmanConcept.mp4
**Phase timestamps:** /Users/ultramarine/Desktop/grad_project/media/videos/policies_values_bellman_concept/480p15/phase_timestamps.json
**Voice:** `am_michael` (Kokoro v1.0, series default — STYLE_BIBLE §12)

---

## Phase timing reference

| Phase | Start | End | Duration |
|---|---|---|---|
| S1-P1 | 00:00:00 | 00:00:30 | 30.0 s |
| S1-P2 | 00:00:30 | 00:01:00 | 30.7 s |
| S2-P3 | 00:01:00 | 00:01:59 | 59.2 s |
| S2-P4 | 00:01:59 | 00:03:20 | 80.6 s |
| S2-P5 | 00:03:20 | 00:04:30 | 70.3 s |
| S3-P6 | 00:04:30 | 00:05:30 | 59.2 s |
| S3-P7 | 00:05:30 | 00:06:50 | 80.5 s |
| S3-P8 | 00:06:50 | 00:07:40 | 50.1 s |
| S3-P9 | 00:07:40 | 00:08:30 | 50.2 s |
| S4-P10 | 00:08:30 | 00:09:10 | 39.2 s |
| S4-P11 | 00:09:10 | 00:09:59 | 49.9 s |
| S4-P12 | 00:09:59 | 00:10:30 | 30.8 s |
| S5-P13 | 00:10:30 | 00:11:09 | 39.2 s |
| S5-P14 | 00:11:09 | 00:11:59 | 50.0 s |
| S5-P15 | 00:11:59 | 00:12:49 | 50.0 s |
| S5-P16 | 00:12:49 | 00:13:39 | 50.0 s |
| S5-P17 | 00:13:39 | 00:14:29 | 50.0 s |
| S5-P18 | 00:14:29 | 00:15:19 | 50.0 s |
| S5-P19 | 00:15:19 | 00:15:59 | 40.0 s |
| S6-P20 | 00:15:59 | 00:16:59 | 60.0 s |
| S7-P21 | 00:16:59 | 00:17:39 | 40.0 s |
| S7-P22 | 00:17:39 | 00:19:29 | 110.0 s |
| S7-P23 | 00:19:29 | 00:19:59 | 30.0 s |
| S8-P24 | 00:19:59 | 00:20:29 | 30.0 s |
| S8-P25 | 00:20:29 | 00:20:59 | 30.0 s |
| S8-P26 | 00:20:59 | 00:21:29 | ~30.0 s |

---

## Phase S1-P1 — V-01 recap, the kitchen we built last time

[00:00:00] Last time we built the *language* of reinforcement learning.
[00:00:07] States, actions, rewards, and a transition rule the agent never controls.
[00:00:15] From those four pieces we defined the *return* — the discounted sum of every reward still to come.
[00:00:23] That return is the only thing the agent ever tries to maximize.

---

## Phase S1-P2 — The recursion callback

[00:00:30] [EQ_ON_SCREEN] We also found that the return obeys a *recursion*.
[00:00:36] [EQ_ON_SCREEN] The return at time t equals the next reward plus gamma times the return that follows.
[00:00:46] One step now, the whole future folded into a single discounted term.
[00:00:53] This recursion is the seed everything in today's video will grow from.

---

## Phase S2-P3 — Policy definition, full-frame

[00:01:00] What we never had in V-01 was a way to describe *how* the agent chooses.
[00:01:08] [EQ_ON_SCREEN] A *policy*, written pi of a given s, is a probability distribution over actions.
[00:01:18] [EQ_ON_SCREEN] It is the probability that the agent picks action A-sub-t equals a, when the state is S-sub-t equals s.
[00:01:30] Notice what this is not — it is not a memorised solution, not a plan, not an answer.
[00:01:40] A policy is simply a *table of probabilities*, one row per state.
[00:01:49] Any such table is a valid policy. Whether it is a good one is a separate question.

---

## Phase S2-P4 — Two policies on the same grid

[00:01:59] Here are two policies for the same environment.
[00:02:06] On the left, the agent always picks right — a *deterministic* policy.
[00:02:15] On the right, the agent splits its choice equally across four actions — a *stochastic* policy.
[00:02:25] Both are policies. Neither is more "real" than the other.
[00:02:34] The deterministic case is just the stochastic case where one probability is one and the rest are zero.
[00:02:46] So "policy" is not a function from state to action — it is a *distribution* that happens, sometimes, to put all its mass on one action.
[00:03:00] Keep this picture in mind. Today's machinery treats every policy the same way.
[00:03:11] The randomness we are about to integrate over lives in this table.

---

## Phase S2-P5 — Normalization, and adopting the equiprobable policy

[00:03:20] [EQ_ON_SCREEN] Every policy must satisfy one structural constraint.
[00:03:28] [EQ_ON_SCREEN] For each state, the probabilities across actions must sum to *one*.
[00:03:39] That is the only rule. No other shape is required of pi.
[00:03:48] For the rest of this video we adopt the *equiprobable* policy — one quarter, one quarter, one quarter, one quarter.
[00:04:00] It is the simplest non-trivial policy we can study, and it makes the value computations transparent.
[00:04:12] Every number you are about to see is measured under this single policy.
[00:04:22] Change pi, and every number changes with it.

---

## Phase S3-P6 — State-value definition, full-frame

[00:04:30] Now the question this entire video is built around.
[00:04:36] [EQ_ON_SCREEN] *How good* is state s, if from here on we follow the policy pi?
[00:04:46] [EQ_ON_SCREEN] We quantify that with the *state-value function*, v-sub-pi of s.
[00:04:57] [EQ_ON_SCREEN] It is the expectation, under pi, of the return G-sub-t, given that we are in state s.
[00:05:10] Read it slowly: average future return, starting from s, behaving according to pi.
[00:05:21] One number per state. A complete answer to "how good is here?"

---

## Phase S3-P7 — Heatmap reveal

[00:05:30] Run that definition on every cell of FrozenLake and you get a *grid of numbers*.
[00:05:40] The brighter the cell, the higher the expected return when the agent starts there.
[00:05:50] Notice the bright corridor leading toward the goal — that is where the expected return concentrates.
[00:06:02] The start state sits at *0.012* — not zero, but small. The agent is far from the goal and the ice is slippery.
[00:06:14] State 14, the cell adjacent to the goal, reaches *0.434* — the highest non-terminal value on the board.
[00:06:27] This grid *is* v-sub-pi. The rest of the video is one question: where did these numbers come from?
[00:06:40] Segment 5 will derive them from first principles. For now, just feel their shape.

---

## Phase S3-P8 — State 14, value is not reward

[00:06:50] Look at state 14 — the cell sitting one step from the goal.
[00:06:58] FrozenLake gives the agent *zero* immediate reward for being there.
[00:07:07] Zero. There is no bonus for proximity, no partial credit, no shaping signal.
[00:07:17] And yet v-sub-pi at state 14 is *0.434* — the brightest non-terminal cell.
[00:07:27] That gap — zero immediate reward, non-zero value — is the entire idea.
[00:07:36] Value is not what you get *now*. Value is what you can *expect* later.

---

## Phase S3-P9 — The goal itself has value zero

[00:07:40] Now a fact that catches almost everyone the first time.
[00:07:46] The *goal* state — the place we want to reach — has value *zero*.
[00:07:55] Not infinity, not a hundred, not the largest number on the board. Zero.
[00:08:04] The intuition "the goal should have the highest value" is wrong, and here is why.
[00:08:13] Once the agent is *at* the goal, the episode is over. There is no future return left to collect.
[00:08:25] v-sub-pi of a terminal state is zero by definition — for the goal *and* every hole.

---

## Phase S4-P10 — Action-value definition

[00:08:30] The state-value answers "how good is here?".
[00:08:37] [EQ_ON_SCREEN] The *action-value function*, q-sub-pi of s and a, answers a slightly different question.
[00:08:48] [EQ_ON_SCREEN] How good is it to *commit* to action a right now, then follow pi from the next state onward?
[00:09:00] One action of commitment, then back to the policy. That is the only difference.

---

## Phase S4-P11 — Four q-values per state

[00:09:10] At state 14, there are *four* action-values — one per action.
[00:09:19] Going down gives the highest expected return — *0.533* — because the goal is south.
[00:09:31] Going right is almost as good — *0.522* — the slip can still carry the agent home.
[00:09:42] Up and left are worse, but never zero. Even a bad action keeps some hope alive on slippery ice.
[00:09:55] These four bars are not separate from v-sub-pi. They are its *decomposition*.

---

## Phase S4-P12 — v as the policy-weighted average of q

[00:09:59] [EQ_ON_SCREEN] Under the equiprobable policy, v-sub-pi of s is the *average* of the four q-values at s.
[00:10:10] [EQ_ON_SCREEN] At state 14, the four q-values average to *0.434* — exactly the heatmap cell.
[00:10:22] In general, v-sub-pi is the *policy-weighted* sum of q-sub-pi over actions.

---

## Phase S5-P13 — Backup diagram, two layers of branching

[00:10:30] Look at what happens when the agent is at state 6, one step into its future.
[00:10:39] First, *pi* picks an action — four possible branches, weighted by the policy.
[00:10:49] Then, for each action, the *environment* picks a next state — three more branches, weighted by p.
[00:11:00] Two layers of randomness. Two distinct sums are about to appear in the equation.

---

## Phase S5-P14 — Derivation step 1, definition

[00:11:09] We are going to *derive* the Bellman equation, one identity at a time.
[00:11:18] [EQ_ON_SCREEN] We start from the definition you have already seen.
[00:11:27] [EQ_ON_SCREEN] v-sub-pi of s is the expectation, under pi, of the return given S-sub-t equals s.
[00:11:40] Nothing new yet. Just the entry point. Watch what unfolds from here.

---

## Phase S5-P15 — Derivation step 2, substitute the recursion

[00:11:59] Recall the recursion from V-01.
[00:12:06] [EQ_ON_SCREEN] G-sub-t equals R-sub-(t+1) plus gamma times G-sub-(t+1).
[00:12:18] [EQ_ON_SCREEN] Substitute that inside the expectation, and the return splits into two pieces.
[00:12:30] The *next reward*, plus the *discounted future return* from the next state.
[00:12:42] The expectation now ranges over both pieces, because both depend on the policy and the environment.

---

## Phase S5-P16 — Derivation step 3, outer sum over actions

[00:12:49] The expectation hides two sources of randomness. We pull them out one at a time.
[00:13:00] [EQ_ON_SCREEN] First, *pi* — the agent's choice of action.
[00:13:07] [EQ_ON_SCREEN] Replace expectation-under-pi with an outer sum over actions, weighted by pi of a given s.
[00:13:20] [EQ_ON_SCREEN] That is the *policy* contribution to the expectation, made explicit.
[00:13:32] Notice on the diagram — the four action branches now glow in sync with the new sum.

---

## Phase S5-P17 — Derivation step 4, inner sum over (s', r)

[00:13:39] Inside each action branch lies the *second* source of randomness — the environment.
[00:13:50] [EQ_ON_SCREEN] Replace what remains with an inner sum over next-state and reward pairs.
[00:14:01] [EQ_ON_SCREEN] Each pair is weighted by p of s-prime and r given s and a.
[00:14:13] The outer sum is over actions. The inner sum is over transitions. They never collapse into one.
[00:14:25] Two sums, two sources of randomness — exactly as the backup diagram promised.

---

## Phase S5-P18 — Derivation step 5, recursion closes

[00:14:29] One last move, and the recursion *closes*.
[00:14:36] [EQ_ON_SCREEN] The expected return from the next state is, by definition, v-sub-pi of that next state.
[00:14:49] [EQ_ON_SCREEN] Substitute, and v-sub-pi appears on both sides of the equation.
[00:15:00] Outside the sum, evaluated at s. Inside the sum, evaluated at s-prime.
[00:15:11] v-sub-pi is the *fixed point* of this relationship — the function that is consistent with itself under pi.

---

## Phase S5-P19 — Boxed Bellman equation

[00:15:19] [EQ_ON_SCREEN] This is the *Bellman expectation equation* for v-sub-pi.
[00:15:30] [EQ_ON_SCREEN] Outer sum over actions, weighted by the policy. Inner sum over transitions, weighted by p.
[00:15:43] It is the single most important relationship in everything that follows in this course.
[00:15:54] Let it sit for a moment.

---

## Phase S6-P20 — LHS equals RHS at state 6

[00:15:59] The Bellman equation is an *equality*, not an instruction.
[00:16:07] The true v-sub-pi satisfies it at every state, simultaneously.
[00:16:16] Take state 6. The heatmap reports v-sub-pi of 6 is approximately *0.039*.
[00:16:27] Now evaluate the right-hand side from the converged values — the same *0.039* falls out.
[00:16:39] Left side and right side agree at machine precision. The identity holds.
[00:16:50] The Bellman equation does not *compute* v-sub-pi. It *checks* that v-sub-pi is itself.

---

## Phase S7-P21 — Code entry, equation becomes runnable

[00:16:59] The equation can be read as math, or it can be read as *code*.
[00:17:07] On the right is the exact same relationship, written in Python against the Gymnasium API.
[00:17:18] One outer loop over actions. One inner loop over the transitions returned by env-dot-P.
[00:17:30] Every symbol in the equation has a variable in the code waiting to receive it.

---

## Phase S7-P22 — Equation, code, and grid in sync

[00:17:39] Watch how three views move together.
[00:17:47] `pi[state, action]` is *pi of a given s* — the policy weight for the outer sum.
[00:17:58] `prob` is *p of s-prime and r given s and a* — the transition weight for the inner sum.
[00:18:11] `reward` is *r* — the immediate reward returned by the environment on that transition.
[00:18:23] And `gamma * v_prev[next_state]` is *gamma times v-sub-pi of s-prime* — the discounted value of where the agent lands.
[00:18:38] Each line of Python is one term of the Bellman equation, applied to one cell of the grid.
[00:18:53] The equation, the code, and the geometry are three views of a single object.
[00:19:08] Trust the link. From here on, when we write code, we are writing the Bellman equation.

---

## Phase S7-P23 — Output 0.000000, the V-03 hand-off

[00:19:29] Run that code once, starting from a guess of all zeros.
[00:19:38] The right-hand side at state 6 evaluates to *0.000000*.
[00:19:48] One sweep is not enough — the heatmap takes many sweeps to emerge. *V-03* is where we iterate this loop until the numbers stop changing.

---

## Phase S8-P24 — Boxed equation re-centered

[00:19:59] Back to the equation that organizes everything we have done.
[00:20:08] Outer sum, policy. Inner sum, environment. Recursion, closure. Identity, not algorithm.
[00:20:22] One picture to carry forward.

---

## Phase S8-P25 — `=` to `←`, V-03 forward-tease

[00:20:29] What if you do not *know* v-sub-pi? What if you only have a guess?
[00:20:40] [EQ_ON_SCREEN] Turn the equality into an *assignment*. Sweep every state. Repeat until nothing changes.
[00:20:51] That algorithm is the next video — *policy evaluation*. v-sub-pi is the fixed point it converges to.

---

## Phase S8-P26 — Takeaway and final hold

[00:20:59] A policy is a distribution over actions. A state-value function is the expected return under that policy.
[00:21:11] The Bellman equation is the *self-consistency* the true state-value function must satisfy.
[00:21:22] Next time we turn that consistency into a *computation*.
