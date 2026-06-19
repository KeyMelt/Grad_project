# Narration Script — td_q_learning (V-09)
# Voice: am_michael | Speed: 1.0 | Target: 3:46
# Segment boundaries (re-timed 2026-06-19 after four-element polish):
#   s01=00:00-00:26, s02=00:26-01:09, s03=01:09-01:57,
#   s04=01:57-02:32, s05=02:32-03:14, s06=03:14-03:46

---

## Phase 1 — SARSA to Q-Learning bridge

[00:00:00] SARSA asks: what action will I actually take next?
[00:00:05] It samples that action and bootstraps from it — on-policy.
[00:00:11] Q-learning swaps one symbol: instead of sampling, it takes the max.
[00:00:17] The target is always greedy. The behavior still explores.
[00:00:21] That single swap makes Q-learning off-policy.

---

## Phase 2 — The Taxi MDP

[00:00:27] Five rows, five columns — five hundred states.
[00:00:32] Six actions: four directions, Pickup, and Dropoff.
[00:00:37] Every step costs one. An illegal pickup or dropoff costs ten.
[00:00:43] Legal dropoff: plus twenty — the only terminal reward.
[00:00:49] The task has four sub-goals chained together.
[00:00:54] Get to the passenger. Pick them up. Get to the destination. Drop them off.
[00:01:02] Q-learning will compose all four — with no explicit plan.

---

## Phase 3 — The focal plus-twenty update

[00:01:10] State sixteen: taxi at R, passenger aboard, destination R.
[00:01:16] The agent executes Dropoff. The Q-table starts learning.
[00:01:22] The Q-learning update — TD target times learning rate.
[00:01:28] Terminal step: the bootstrap is zero.
[00:01:34] Target is just the reward — twenty.
[00:01:40] Alpha times TD error: zero-point-one times twenty equals two.
[00:01:46] The Dropoff bar rises to two-point-zero.
[00:01:52] One step back: the target becomes zero-point-nine. The signal spreads.

---

## Phase 4 — Off-policy contrast

[00:01:58] Same transition — SARSA and Q-learning diverge.
[00:02:03] SARSA samples the next action from the behavior policy.
[00:02:08] Say it picks West: target is minus four-point-eight.
[00:02:14] Q-learning ignores the sampled action entirely.
[00:02:19] It asks: what is the best Q in the next state?
[00:02:24] Target: plus zero-point-nine. Same data, opposite conclusion.
[00:02:29] Off-policy means the behavior can be anything — the target stays greedy.

---

## Phase 5 — Value propagation and convergence

[00:02:33] R is the goal. The first dropoff gave it value two.
[00:02:39] One step away: target zero-point-nine. Two steps: point-eight-five.
[00:02:45] Values decay by gamma each hop — point-nine-five.
[00:02:51] The greedy policy arrows emerge — no map was given.
[00:02:57] Greedy episode: navigate to Y, Pickup, drive north to R.
[00:03:03] Dropoff. Plus twenty. Four sub-goals, zero explicit planner.
[00:03:09] Every arrow is the argmax of a converged Q-value row.

---

## Phase 6 — Code walkthrough

[00:03:15] The boxed term — max of Q next-state — is the off-policy hook.
[00:03:20] In the exercise: best_next equals max of Q of next_state.
[00:03:26] That is the entire algorithmic difference from SARSA.
[00:03:31] SARSA needs a sampled next action. Q-learning does not.
[00:03:36] Q-learning is a sampled Bellman optimality backup — no model needed.
[00:03:41] This exact update, scaled to a neural network, is DQN.
