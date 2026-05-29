# Narration Script — rl_mdp_core

**Date:** 2026-05-24 (re-timed: audio-as-master)
**Voice:** am_michael (Kokoro v1.0, 1.0x, 24 kHz)
**plan.md reference:** manim_service/concept_videos/rl_mdp_core_plan.md

---

## Phase 1 — Grid entry

[00:00:00] An agent. A goal. A frozen lake.
[00:00:04] The ice stretches between them — and the ice does not cooperate.
[00:00:10] The agent cannot see ahead. It has no teacher, no map, no instructions.
[00:00:16] The only thing it will ever receive is a number — once, at the very end, if it reaches the goal.
[00:00:23] That single number is its only guide. And the question is: can anything be learned from that?

---

## Phase 2 — Failed attempt 1 (path: 0→1→5)

[00:00:32] The agent sets out. Two steps — and it falls through the ice.
[00:00:37] No message arrives. No hint. Nothing points back toward a better path.
[00:00:43] Only a zero.
[00:00:45] That zero is not feedback in any rich sense — it is the *absence* of feedback.
[00:00:52] The agent chose, the environment responded, and the only signal is a number that says nothing about what went wrong.
[00:01:01] There is no teacher watching, no supervisor pointing to the mistake.
[00:01:06] The agent must learn anyway. That is the defining challenge of reinforcement learning.

---

## Phase 3 — Failed attempt 2 (slippage: 0→4→8→9→5)

[00:01:15] The agent tries again — a different path, more careful steps.
[00:01:20] But the ice has its own say. At each step, the agent chooses a direction — and arrives somewhere else.
[00:01:27] The environment is *stochastic*. The agent's choice does not determine the outcome; it only shifts the probabilities.
[00:01:36] A fall into the same hole. Another zero.
[00:01:40] Notice the gap between what the agent intended and where it ended up.
[00:01:46] That gap — between intention and outcome — is not a failure of the agent. It is a property of the world.
[00:01:54] The world does not bend to the agent's will. The agent must account for that.

---

## Phase 4 — Successful path (0→4→8→9→10→14→15, reward 1.0)

[00:02:02] One more attempt.
[00:02:04] Five steps across the ice — the agent slips, recovers, slips again — and finally reaches the far corner.
[00:02:12] And now something different happens.
[00:02:16] A *reward of one*.
[00:02:19] That is all. One number. No explanation of which steps were good. No partial credit for the near-misses.
[00:02:27] Every zero along the way told the agent nothing. Only the final step, at the goal, carries a signal.
[00:02:34] This is called a sparse reward — and it is the norm in many real problems, not the exception.
[00:02:42] A reward at the very end of a sequence cannot be credited to any single action — the agent must figure out which actions across all five steps actually mattered.
[00:02:54] How does an agent even begin to reason about that?
[00:02:58] The answer requires a precise language for describing what the environment does and what the agent is trying to maximize.
[00:03:08] That language is the Markov Decision Process. And it starts with a deceptively simple idea.

---

## Phase 5 — State indices revealed

[00:03:17] Every cell the agent can occupy is a *state*.
[00:03:21] The frozen lake has sixteen of them — numbered zero at the top-left, fifteen at the bottom-right.
[00:03:29] A state is a complete description of where the agent is. Nothing else matters for what happens next.
[00:03:36] Not the path that brought the agent here. Not the number of steps taken. Not the history of failed attempts.
[00:03:44] Only the current state, combined with the action the agent takes, determines what the environment does next.
[00:03:52] This is the *Markov property* — and it is both a simplification and an enabling assumption.
[00:04:00] The simplification: we discard history, and the problem becomes tractable.
[00:04:06] The enabling assumption: the state must actually capture everything relevant. For FrozenLake, the cell number does that.

---

## Phase 6 — Markov property demonstration (state 6, action RIGHT)

[00:04:16] Take state six — one of the safe cells in the second row.
[00:04:21] Suppose the agent arrived here after two steps. Or four steps. Or by a completely different route.
[00:04:29] It does not matter.
[00:04:31] The ice has no memory of how the agent got here. The environment's response depends only on where the agent is *now* and what it chooses to do *now*.
[00:04:43] The agent chooses RIGHT from state six.
[00:04:46] But the ice is slippery — "choosing right" is not the same as "arriving right."
[00:04:52] What actually happens next is governed by a probability distribution over possible landing cells.
[00:05:00] The agent chose. The environment will respond. But the response is not the action — it is something the environment controls entirely.
[00:05:11] So the natural question becomes: what is the precise mathematical object that describes the environment's response?

---

## Phase 7 — Full-screen solo reveal of p(s',r|s,a)

[00:05:21] [EQ_ON_SCREEN] This is the dynamics function — *p of s-prime, r, given s and a*.
[00:05:27] [EQ_ON_SCREEN] It is a probability — the chance that the agent lands in state s-prime and receives reward r, given that it was in state s and chose action a.
[00:05:38] [EQ_ON_SCREEN] Four arguments. Four roles. And they divide the world cleanly in two.
[00:05:44] [EQ_ON_SCREEN] The agent controls *a* — the action. The environment controls everything else.
[00:05:51] [EQ_ON_SCREEN] State s is where the agent is. The action a is what it does. State s-prime is where it *lands*. Reward r is what it *receives*.

---

## Phase 8 — Three outcome branches

[00:06:05] [EQ_ON_SCREEN] From state six, choosing RIGHT, the ice spreads the agent's landing across three cells.
[00:06:12] [EQ_ON_SCREEN] Upward one row. Rightward one column. Downward one row.
[00:06:17] [EQ_ON_SCREEN] Each destination carries the same probability — one third.
[00:06:23] [EQ_ON_SCREEN] The agent cannot steer between them. The choice of RIGHT has been made. The ice decides the rest.
[00:06:30] [EQ_ON_SCREEN] That one-third for each outcome is the *value* of p for this state, this action, and each possible next state.
[00:06:39] [EQ_ON_SCREEN] The s-prime in the equation is not a fixed destination — it is a variable that ranges over every cell the agent might reach.
[00:06:49] [EQ_ON_SCREEN] One of those destinations is a hole. Landing there ends the episode immediately. The reward is still zero — the hole carries no penalty, only termination.
[00:07:01] [EQ_ON_SCREEN] The agent intended right. The ice gave it three equally weighted possibilities. The equation *p of s-prime, r, given s and a* is the formal name for that uncertainty — every time, for every state, for every action.
[00:07:18] This is what the agent is navigating. Not a fixed world — a *distribution* over worlds at every step.

---

## Phase 9 — ActionBarChart: three bars at 1/3 each

[00:07:28] [EQ_ON_SCREEN] The three outcomes from state six, action RIGHT — made visible as a distribution.
[00:07:34] [EQ_ON_SCREEN] Each bar represents how likely the agent ends up in that particular cell. One third for state two. One third for state seven. One third for state ten.
[00:07:46] [EQ_ON_SCREEN] Equal heights. Equal probabilities. The ice plays no favorites.
[00:07:51] [EQ_ON_SCREEN] The bars must sum to one — that is the normalization constraint on the dynamics function. All probability mass must be accounted for.
[00:08:02] State seven is a hole — reaching it ends the episode. The probability of landing there is the same as anywhere else. The world does not warn you before you fall.
[00:08:14] Intention and outcome are two separate events. The choice has been made. The distribution is what happens next.

---

## Phase 10 — CodeStepper: env.unwrapped.P[6][2]

[00:08:24] The same distribution — the same p of s-prime, r, given s and a — lives inside the Gymnasium environment as a Python data structure.
[00:08:35] `env.unwrapped.P[6][2]` addresses the environment's dynamics model directly: state six, action indexed two, which is RIGHT.
[00:08:46] The outer loop ranges over every possible outcome. Each iteration exposes four values: the probability of that outcome, the next state, the reward, and whether the episode ends.
[00:08:59] Those four values are exactly the four arguments of the dynamics function — just arranged as a Python tuple rather than mathematical notation.
[00:09:10] For the first iteration: next state is ten, probability one third, reward zero, episode continues.
[00:09:18] For the second: next state is seven — that is the hole. Probability one third, reward zero, and the episode terminates.
[00:09:27] For the third: next state is two, probability one third, reward zero, episode continues.
[00:09:35] Three tuples. Three outcomes. The probabilities sum to one — the full distribution is here.
[00:09:42] The code is not an approximation of the mathematics. It is the same object, stored in a computer's memory, accessible one key lookup away.

---

## Phase 11 — Normalization and summation collapse

[00:09:54] [EQ_ON_SCREEN] The dynamics function is *complete* — summing over all next states and all possible rewards must yield one.
[00:10:03] [EQ_ON_SCREEN] That is the normalization constraint: the sum over all s-prime and all r of p of s-prime, r, given s and a, equals one — for every state and every available action.
[00:10:17] [EQ_ON_SCREEN] Sometimes the reward structure is not what we care about — we want to know only *where* the agent lands, not what it receives.
[00:10:26] [EQ_ON_SCREEN] Summing the four-argument form over all possible rewards gives the state-transition probability: p of s-prime given s and a.
[00:10:36] [EQ_ON_SCREEN] That derived form tells you the probability of landing in s-prime. The four-argument form is the *canonical* object — it contains strictly more information, and every derived quantity follows from it.

---

## Phase 12 — Full-screen solo reveal of G_t

[00:10:53] [EQ_ON_SCREEN] There is a second question we have not yet answered.
[00:10:57] [EQ_ON_SCREEN] The dynamics function tells us where the agent lands and what it receives — one step at a time.
[00:11:04] [EQ_ON_SCREEN] But what is the agent actually trying to maximize?
[00:11:09] [EQ_ON_SCREEN] Not the next reward. The *return* — the weighted sum of all future rewards.
[00:11:15] [EQ_ON_SCREEN] G sub t equals R sub t-plus-one, plus *gamma* times R sub t-plus-two, plus gamma-squared times R sub t-plus-three, and so on — which compresses to: the sum over k from zero to infinity of gamma to the k times R sub t-plus-k-plus-one.
[00:11:35] [EQ_ON_SCREEN] Every reward in the agent's future contributes to G sub t. Rewards further away are weighted by higher powers of gamma. Nothing is ignored — only discounted.

---

## Phase 13 — Term-by-term return computation (path 0→4→8→9→10→14→15)

[00:11:52] Walk through the successful path, step by step.
[00:11:56] The agent starts at state zero. The first step brings no reward. The second step brings no reward. The third, fourth, fifth — all zeros.
[00:12:07] Five steps of nothing.
[00:12:10] The accumulator stays at zero through every one of them — because there is nothing to accumulate.
[00:12:17] Then, at the sixth step, the agent reaches the goal. A *reward of one* arrives.
[00:12:23] But that reward did not arrive at step one. It arrived at step six. And the return discounts by distance.
[00:12:32] With gamma equal to 0.99, a reward six steps away is worth 0.99 to the fifth power times one — which is approximately *0.951*.
[00:12:46] The reward is not lost. It reaches the agent's objective in full — just reduced by the distance it traveled through time.
[00:12:56] A patient agent with gamma close to one treats a reward ten steps away almost as seriously as a reward right now.
[00:13:05] That patience is exactly what the agent needs to value the distant goal on this frozen lake — where no reward arrives until the very end.

---

## Phase 14 — Gamma sweep: γ ∈ {0.5, 0.99, 1.0}

[00:13:17] How much does the distance actually cost?
[00:13:21] With *gamma equal to 0.5* — the agent is impatient. A reward five steps away is worth 0.5 to the fifth power, which is roughly three cents on the dollar.
[00:13:35] With gamma equal to 0.99, the same reward is worth ninety-five cents. The agent is nearly as patient as it can be.
[00:13:45] With gamma equal to 1.0 — every future reward counts at full value, no discounting at all.
[00:13:54] FrozenLake always terminates. Every episode ends, either in a hole or at the goal. So gamma equal to 1.0 is valid here — the sum G sub t is always finite because the episode is finite.
[00:14:10] But for tasks that run forever — tasks with no natural endpoint — gamma strictly less than one is *required*. Without discounting, the infinite sum of rewards may not converge to a finite number.
[00:14:25] In this series, gamma is set to 0.99 by convention — not because FrozenLake demands it, but to prepare for algorithms that must handle continuing tasks where gamma less than one is not optional.
[00:14:40] The discount factor is the agent's relationship with its own future.

---

## Phase 15 — Return recursion derived

[00:14:48] [EQ_ON_SCREEN] Look at the sum form of G sub t. Factor out gamma from every term after the first.
[00:14:55] [EQ_ON_SCREEN] What remains is: R sub t-plus-one, plus gamma times the quantity R sub t-plus-two, plus gamma times R sub t-plus-three, plus — which is exactly the definition of G sub t-plus-one.
[00:15:10] [EQ_ON_SCREEN] The entire infinite tail collapses into a single term.
[00:15:15] [EQ_ON_SCREEN] *G sub t equals R sub t-plus-one, plus gamma times G sub t-plus-one.*
[00:15:22] [EQ_ON_SCREEN] This is the *return recursion*. The return at any step equals the immediate reward plus a discounted version of the return from the very next step.
[00:15:33] [EQ_ON_SCREEN] The recursion does not change what G sub t means — it just expresses that meaning more compactly, by folding the future into a single symbol.
[00:15:44] We will see this identity again in the next video — in a form that will let us reason about what each state is worth.

---

## Phase 16 — Hold frame and forward tease

[00:15:54] Two objects define a Markov Decision Process.
[00:15:58] The dynamics function *p of s-prime, r, given s and a* — the environment's response law, specifying for any state and action the distribution over where you land and what you receive.
[00:16:13] The return *G sub t* — the agent's objective, the discounted sum of everything that will ever happen from this moment forward.
[00:16:23] The agent acts in a world governed by p. It tries to maximize G sub t.
[00:16:29] Everything else in this series — every algorithm, every theorem, every update rule — is built on top of these two objects.
[00:16:39] Next: we give the agent a *strategy* for choosing actions — and ask what each state is worth under that strategy.

---

