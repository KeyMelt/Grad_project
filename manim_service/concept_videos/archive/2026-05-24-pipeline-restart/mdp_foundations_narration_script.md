# Narration Script — mdp_foundations

**Date:** 2026-05-23
**Target duration:** ~1,700 s (≈28:20); narration tracks visual cues within ±2.0 s
**plan.md reference:** manim_service/concept_videos/mdp_foundations_plan.md
**MP4 reference:** backend/media/concept_videos/mdp_foundations_concept.mp4
**Voice:** am_michael · Kokoro v1.0 · speed 1.0 · 24 kHz
**BGM:** None (STYLE_BIBLE §12 — educational density too high for concurrent music)

---

## Phase timing reference

Derived from plan.md pacing budget after Pacing Linter trim (28:20 ceiling).

| Phase | Start | End | Duration |
|---|---|---|---|
| (a) MDP framework | 00:00 | 04:10 | ~4:10 |
| (b) Rewards and returns | 04:10 | 08:50 | ~4:40 |
| (c) Transition probability | 08:50 | 13:20 | ~4:30 |
| (d) Policies | 13:20 | 16:50 | ~3:30 |
| (e) Value functions | 16:50 | 21:00 | ~4:10 |
| Recap card | 21:00 | 22:20 | ~1:20 |
| (f) Bellman expectation equation | 22:20 | 27:00 | ~4:40 |
| Closing | 27:00 | 28:20 | ~1:20 |

---

## Phase (a) — MDP Framework

[00:00:03] A four-by-four grid of frozen ice appears — sixteen tiles, numbered zero through fifteen.
[00:00:10] Row zero is at the top: states zero, one, two, three. Each subsequent row adds four.
[00:00:18] Five tiles are different from the rest. Dark holes mark states five, seven, eleven, and twelve. The bright tile at state fifteen is the *goal*.
[00:00:28] These five tiles are *terminal* — once the agent lands on any of them, the episode ends.
[00:00:35] The remaining eleven tiles are frozen surface. The agent can take four actions from any non-terminal state: *LEFT*, *DOWN*, *RIGHT*, or *UP* — action indices zero through three.
[00:00:47] Every idea in this video lives on this grid. It will stay on screen throughout, gaining one new layer of meaning per segment.

[00:00:56] The first idea: why does this grid constitute a *Markov Decision Process*?
[00:01:02] An MDP is a formal description of an agent interacting with an environment. It is built from three objects: a set of states *script-S*, a set of actions *script-A of s* available at each state, and the environment's response rule — called *the dynamics*.
[00:01:17] The state set here is all sixteen cell indices. The action set at every non-terminal state is the four directions.

[00:01:26] The defining mathematical property of an MDP is the *Markov property*. It states that the probability of the next state and the next reward depends *only* on the current state and the current action — not on anything that happened before.
[00:01:41] Written precisely: the probability that S sub t-plus-one equals s-prime and R sub t-plus-one equals r, given the full history of states and actions, equals the same probability given only the current state S sub t and the current action A sub t.
[00:01:56] The past is compressed into the present state. The elf's tile index is sufficient — the sequence of tiles it visited to get there does not matter.

[00:02:08] The environment's response rule — the function that computes that probability — is named *p of s-prime, r given s, a*. We will derive its structure in detail in segment three. For now, simply: p is the environment's mechanism, and the agent does not control it.

[00:02:25] Holes five, seven, eleven, and twelve, and the goal at fifteen, are highlighted as the *terminal subset* — in the textbook notation, script-S-plus. From a terminal state, no further action is meaningful; the episode resets.
[00:02:40] That is the MDP framework: states, actions, the Markov property, and an unnamed dynamics function p. The next segment gives that function its first explicit form.

[00:02:52] Before we move on: notice that this grid has been built once. It will not be rebuilt. Every segment from here to the Bellman equation simply adds a new transparent layer on top.

---

## Phase (b) — Rewards and Returns

[00:04:13] The RL agent's goal is to accumulate reward. But what, precisely, is *reward*?
[00:04:19] At each time step, after the agent acts, the environment returns a single scalar number. This is called *the reward* — written R sub t-plus-one, received one step after the action at time t.

[00:04:31] The *reward hypothesis* — stated in Sutton and Barto — is the foundational bet of reinforcement learning: all goals can be expressed as the maximization of the *expected cumulative sum* of received rewards.
[00:04:45] Not just the next reward. The *cumulative* reward — summed over the entire episode or beyond.

[00:04:54] That cumulative sum is the *return*, written G sub t.
[00:04:59] For a stream of future rewards, the return is: G sub t equals R sub t-plus-one, plus gamma times R sub t-plus-two, plus gamma-squared times R sub t-plus-three, and so on.
[00:05:12] Written as a sum: G sub t equals the sum over k from zero to infinity of gamma to the k times R sub t-plus-k-plus-one.

[00:05:23] The new object is *gamma* — the *discount factor*. Gamma lives in the closed interval zero to one.
[00:05:30] Watch what gamma does to a concrete reward stream. Suppose the agent receives zero reward for two steps, then one reward on the third step. At gamma equals zero-point-nine-nine, the return is: zero, plus zero-point-nine-nine times zero, plus zero-point-nine-nine squared times one.
[00:05:48] Zero-point-nine-nine squared is zero-point-nine-eight-zero-one. The return for that stream is *zero-point-nine-eight-zero-one*.
[00:05:57] Rewards in the far future contribute, but they are scaled down by gamma for every step they are away.

[00:06:06] Two boundary conditions to remember.
[00:06:10] When gamma equals zero, the agent is *myopic* — G sub t collapses to just R sub t-plus-one. Only the next reward counts.
[00:06:19] When gamma equals one, all future rewards count equally. This is valid only when the episode is *guaranteed to terminate* — as it is in FrozenLake, where every episode eventually lands on a hole or the goal.

[00:06:32] The episodic case — tasks with a terminal time T — is the one this video uses. The infinite sum is effectively finite because R equals zero after the terminal step.

[00:06:44] Now the most important line of this entire video before segment six.
[00:06:50] The return satisfies a *recursive identity*: G sub t equals R sub t-plus-one *plus* gamma times G sub t-plus-one.
[00:06:59] Read it aloud: the return starting now equals the immediate reward, plus gamma times the return starting one step from now.
[00:07:08] This one line is the seed of the Bellman equation. We will substitute it directly into the definition of value in segment six. Mark it.

[00:07:19] Gamma close to one: the agent is *patient* — it weighs distant rewards almost as much as immediate ones.
[00:07:26] Gamma close to zero: the agent is *impatient* — only the immediate reward matters.
[00:07:32] For FrozenLake, a reasonable gamma is zero-point-nine-nine. A single reward of one at the goal, discounted over a ten-step path, is still about zero-nine-oh-five — well worth pursuing.

---

## Phase (c) — Transition Probability

[00:08:53] Segment three: the dynamics function p in full detail.
[00:08:58] The Markov property told us the next state and reward depend only on the current state and action. The dynamics function *is that probability*, written precisely.

[00:09:09] *p of s-prime, r given s, a* is defined as the probability that the next state equals s-prime and the next reward equals r, given that the current state is s and the current action is a.
[00:09:22] This is a four-argument function of the transition tuple: successor state, reward, current state, current action.

[00:09:32] It is a valid probability distribution. For every fixed s and a, summing over all successor states s-prime and all rewards r gives one.
[00:09:42] This normalization is not optional — it is part of the definition.

[00:09:50] Let us read it from FrozenLake directly. Focus on state six — row one, column two — and action RIGHT, index two.
[00:09:59] The environment — not the agent — determines where the elf ends up. Because the ice is slippery, a step intended to the right does *not* always land one cell to the right.

[00:10:12] The code on the left queries the transition table:
[00:10:16] `env dot unwrapped dot P open-bracket six close-bracket open-bracket two close-bracket`.
[00:10:23] This returns a list of four-tuples: probability, next-state, reward, done.

[00:10:31] Three tuples come back — not one. The slippery model distributes probability across three successor states.
[00:10:39] One-third probability to state seven — that is the intended rightward step. State seven is a *hole*, so done equals *true*.
[00:10:49] One-third probability to state two — the grid cell directly above, where the perpendicular UP slip lands.
[00:10:56] One-third probability to state ten — the grid cell directly below, where the perpendicular DOWN slip lands.
[00:11:04] All three rewards are zero. The goal at state fifteen is not reachable from state six via action RIGHT.

[00:11:13] The ActionBarChart on the right makes this concrete: three equal bars, each exactly one-third. The successor labels are seven, two, and ten.
[00:11:24] The sum of the three bars is one. The normalization condition is satisfied for this state-action pair — and for every state-action pair in FrozenLake.

[00:11:35] Notice what p is *not*: p is not the agent's choice. The agent chose action RIGHT. The *environment* then flipped between three outcomes. The agent has zero control over which of the three successors actually materialises.
[00:11:50] That distinction — environment dynamics versus agent policy — is the conceptual divide this entire series is built on.

[00:12:00] Two optional derived forms: the *state-transition marginal* p of s-prime given s and a equals the sum over r of p of s-prime, r given s, a. And the *expected reward function* r of s, a equals the sum over r of r times the sum over s-prime of p. These follow directly from the four-argument form but are not required to unblock the next video.

---

## Phase (d) — Policies

[00:13:23] Segment four: the agent's side of the boundary. Until now, we described the environment's response rule p. Now we describe the *agent's* decision rule.
[00:13:35] The agent's decision rule is called a *policy*, written pi.

[00:13:41] *pi of a given s* is the probability that the agent chooses action a when it observes state s.
[00:13:49] Like p, it is a probability distribution. But unlike p, this one belongs to the agent: pi of a given s is greater than or equal to zero, and the sum over all actions a of pi of a given s equals one.
[00:14:03] For every state, the agent's action probabilities form a valid simplex.

[00:14:11] On the left side of the screen: a deterministic policy. One arrow per cell — the agent always chooses the same action in each state. This is the special case where one action gets probability one and every other action gets probability zero.
[00:14:25] On the right side: a stochastic policy. For every state, the agent assigns a positive probability to each of the four actions. The example shown is the *uniform-random policy*: each of the four actions receives probability one-quarter.

[00:14:42] Read the uniform-random policy aloud: at state six, pi of LEFT given six is zero-point-two-five; pi of DOWN given six is zero-point-two-five; pi of RIGHT given six is zero-point-two-five; pi of UP given six is zero-point-two-five. Sum: one.

[00:14:58] Critical distinction — say it explicitly:
[00:15:02] *p* chooses which *outcome* occurs after the agent acts. The agent cannot control p.
[00:15:09] *pi* chooses which *action* the agent takes. The environment cannot control pi.
[00:15:16] They are *separate objects* — one owned by the environment, one owned by the agent.

[00:15:25] The uniform-random policy shown here is not a strategic choice. It is deliberately non-optimal. That matters for the next segment.
[00:15:34] The next video — policy evaluation — evaluates exactly this uniform-random policy on exactly this FrozenLake grid. You will need to accept that a non-optimal policy has a perfectly well-defined, computable value.
[00:15:48] Policies are evaluated, not just optimised.

---

## Phase (e) — Value Functions

[00:16:53] Segment five: measuring the expected return under a policy. This is the value function.
[00:17:00] The *state-value function* v sub pi of s is the expected value of the return G sub t, starting from state s and following policy pi forever after.
[00:17:12] Written as an expectation: v sub pi of s equals E sub pi of G sub t, given that S sub t equals s.
[00:17:21] The subscript pi on the expectation means: we average over all trajectories generated by *this* policy pi and the environment's dynamics p.

[00:17:33] The colour overlay on the grid is a value *heatmap*. Each cell's brightness encodes v sub pi of s under the uniform-random policy.
[00:17:43] Lighter cells have higher expected return. Darker cells have lower expected return. The heatmap is reading left to right, top to bottom across all sixteen states simultaneously.

[00:17:55] The five terminal cells — holes five, seven, eleven, twelve and goal fifteen — are displayed at value *zero*. No further reward accrues after a terminal state. The expected return from a terminal state, regardless of policy, is identically zero.

[00:18:10] This is the second value function: the *action-value function* q sub pi of s, a — the expected return given that the agent starts at state s, takes action a *first*, and then follows pi.
[00:18:24] The bars on the right show q sub pi of six, a for each of the four actions at our focal state six under the uniform-random policy. The action values differ because the three stochastic successors have different subsequent values under the policy.

[00:18:40] The bridge between state-value and action-value is: v sub pi of s equals the sum over actions a of pi of a given s times q sub pi of s, a.
[00:18:52] The state value is the policy-weighted average of the action values. This is the v-q bridge — and segment six will substitute *into* it.

[00:19:04] One misconception to address explicitly: *value functions do not require the optimal policy*. v sub pi is defined for *any* policy pi. The uniform-random policy shown on screen — the one that chooses every action with probability one-quarter — has a perfectly well-defined value function. It just happens to have low values in most states because random actions often lead to holes.
[00:19:27] The next video evaluates this exact policy. If you believe value functions only apply to optimal policies, the next video will seem mysterious. It should not.

---

## Recap Card

[00:21:03] Before we derive the Bellman equation, a brief reset.
[00:21:08] Five objects are in play. Each one on the card:
[00:21:13] *pi* chooses the agent's actions. It is the decision rule, owned by the agent.
[00:21:20] *p* chooses the environment's outcomes. It is the dynamics function, owned by the environment.
[00:21:28] *r* is the immediate scalar reward, received after each action.
[00:21:33] *gamma* discounts future rewards: each additional time step costs one factor of gamma.
[00:21:40] *v sub pi* is the expected discounted return starting from a state, following pi.
[00:21:48] These five objects are connected by an equation that every state must satisfy simultaneously. That equation is what we derive next.

---

## Phase (f) — Bellman Expectation Equation

[00:22:23] Segment six: the Bellman expectation equation. We derive it — we do not state it.
[00:22:31] Start from the recursion highlighted in segment two: G sub t equals R sub t-plus-one plus gamma times G sub t-plus-one.

[00:22:42] Substitute directly into the definition of v sub pi.
[00:22:47] v sub pi of s equals E sub pi of G sub t given S sub t equals s.
[00:22:55] Replace G sub t with R sub t-plus-one plus gamma G sub t-plus-one:
[00:23:02] v sub pi of s equals E sub pi of open-bracket R sub t-plus-one plus gamma G sub t-plus-one close-bracket, given S sub t equals s.

[00:23:15] Now expand the expectation by peeling apart the contributions of the policy and the dynamics.
[00:23:22] The BackupDiagram on the right makes the structure visible. The root is state s — an open circle.

[00:23:31] The first level of branching is the *policy*: from state s, the agent chooses action a with probability pi of a given s. Each branch is labelled with its probability.
[00:23:44] The second level of branching is the *dynamics*: from state s after action a, the environment transitions to successor s-prime with reward r with probability p of s-prime, r given s, a. Each leaf is labelled with its transition tuple.

[00:23:59] At each leaf, the contribution is *r plus gamma times v sub pi of s-prime*. The immediate reward r, plus gamma times the value of the landing state under the same policy.
[00:24:12] This is the recursion: the value at s is expressed in terms of values at the successors s-prime.

[00:24:22] Summing over all actions weighted by the policy, and over all successors weighted by the dynamics, gives the full Bellman expectation equation:
[00:24:33] *v sub pi of s equals the sum over a of pi of a given s, times the sum over s-prime and r of p of s-prime, r given s, a, times open-bracket r plus gamma times v sub pi of s-prime close-bracket.*
[00:24:51] This is Sutton and Barto equation three-point-fourteen.

[00:25:00] Read each piece from the diagram:
[00:25:04] The outer sum over a: that is the policy branching — each action branch contributes.
[00:25:11] The factor pi of a given s: the probability of each policy branch.
[00:25:17] The inner sum over s-prime and r: that is the dynamics branching — each leaf contributes.
[00:25:24] The factor p of s-prime, r given s, a: the probability of each dynamics leaf.
[00:25:31] The bracket r plus gamma v sub pi of s-prime: the payoff at each leaf.

[00:25:41] This equation holds simultaneously at *every* state s in the state set. It is a *consistency condition*: the value at any state must equal what you get by averaging one step's worth of transition and reward plus the discounted value of the landing state.
[00:25:58] v sub pi is the unique function that satisfies this equation at every state. The equation does not compute v sub pi — it *characterises* it.

[00:26:10] Two observations to cement this:
[00:26:14] First: the equation is not trivially satisfied. For an arbitrary function, the left side and the right side will not match. The value function v sub pi is precisely the function for which they do match — at every state simultaneously.
[00:26:28] Second: this derivation required both the policy *and* the dynamics. The Bellman equation is not a property of the policy alone, nor of the environment alone. It belongs to the system.

---

## Closing

[00:27:03] The full Bellman expectation equation is on screen.
[00:27:08] Each term maps to an object introduced in this video: the state set, the action set, the dynamics p, the policy pi, the discount gamma, and the value function v sub pi.
[00:27:20] The equation *exists*. It characterises the value function. It does not compute it.

[00:27:29] In the next video — *dp_policy_eval* — you will turn this equality into an assignment: replace the equals sign with an arrow, and sweep through every state repeatedly until the values stop changing.
[00:27:44] That iterative sweep is *policy evaluation*, and the Bellman equation you just derived is the exact formula inside the loop.

[00:27:54] Takeaway: a finite MDP is the tuple of states, actions, and dynamics p. A policy and a discount factor turn rewards into returns. Value functions measure those returns under any policy. And the Bellman expectation equation expresses each state's value recursively from its successors — the exact equality the next video turns into an algorithm.

---

## Synthesis notes

- All cues are approximate (±2.0 s against visual beat). The synthesiser shifts later
  lines if any clip overruns its window.
- Mathematical terms are spoken in their full English form (e.g. "pi of a given s"
  not "π(a|s)"). The on-screen MathTex renders the symbols; the narration provides
  the spoken reading.
- State indices are always spoken as integers ("state six", "state seven") — never
  "tile six" or "cell seven" after the initial grid introduction.
- "Slippery" and "FrozenLake" are not defined in this video; they were introduced
  in rl_intro. This script may reference them without re-defining.
- The recursion G_t = R_{t+1} + γG_{t+1} is explicitly flagged in Phase (b) for
  reuse — the narration for Phase (f) references it ("the recursion highlighted in
  segment two") to enforce the derivation chain rather than asserting the Bellman
  equation cold.
- No iteration loop, no sweep, no update assignment, no max-over-actions appears
  anywhere in this script. The closing beat names dp_policy_eval and describes the
  loop structure but does not display it.
- The state-6 RIGHT successor states spoken aloud are seven, two, and ten — matching
  the Gate 2 confirmed live Gymnasium values. The old reference scene value of five
  must not appear in narration or captions.
