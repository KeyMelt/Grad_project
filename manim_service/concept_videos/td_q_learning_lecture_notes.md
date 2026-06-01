# Q-Learning

## Why this concept matters

Q-learning is SARSA with one symbol changed — and that single change makes it the most influential algorithm in reinforcement learning. Where SARSA bootstraps from the *sampled* next action $Q(S_{t+1}, A_{t+1})$, Q-learning bootstraps from the *greedy* action $\max_a Q(S_{t+1}, a)$. The behavior policy still uses $\epsilon$-greedy to explore; the *target* uses the max. That makes Q-learning **off-policy**: it learns the optimal action-value function $q_*$ regardless of what behavior policy generated the data, as long as that policy visits every state-action pair infinitely often.

This decoupling is why Q-learning is everywhere: experience replay (DQN), demonstrations, hindsight relabeling — none of these work for on-policy SARSA, all of them work for Q-learning. Watkins's 1989 thesis was the breakthrough; the entire deep-RL revolution is, structurally, Q-learning with a neural network in place of the tabular $Q$.

We stay on CliffWalking-v0 — same $4 \times 12$ grid, same start/goal/cliff layout, same step reward $-1$ and cliff reward $-100$, same $\gamma = 1$ in convention (lesson default in the starter is $\gamma = 0.95$). The point of using the same environment as SARSA is to make the comparison surgical: one symbol changes in the code, and the learned policy changes from "walk safely around the cliff" to "walk along the cliff edge, accepting occasional $\epsilon$-greedy disasters." That contrast is the canonical illustration of on-policy vs. off-policy.

![CliffWalking-v0: SARSA learns the safer upper route (orange); Q-learning learns the optimal cliff-edge route (red). One symbol changes in the code — the $\max$ vs. the sampled next action — and the learned policy changes completely.](https://gymnasium.farama.org/_images/cliff_walking.gif)

## Intuition first

Same setup as SARSA. The agent is at $S_t$, samples $A_t$ via $\epsilon$-greedy, takes the step, observes $R_{t+1}$ and $S_{t+1}$. *Now* the algorithms diverge:

- **SARSA** would say: "Let me also sample $A_{t+1}$ now, and use $Q(S_{t+1}, A_{t+1})$ in the target."
- **Q-learning** says: "I don't care which action I will *actually* take next. The target is the *best possible* next-state value. Use $\max_a Q(S_{t+1}, a)$."

The target becomes

$$
R_{t+1} + \gamma \max_a Q(S_{t+1}, a).
$$

The bootstrap term assumes the agent will act optimally from $S_{t+1}$ onwards — even though, in reality, the agent's *behavior* policy will still occasionally explore. This is the off-policy nature: the *target policy* (greedy) is different from the *behavior policy* ($\epsilon$-greedy).

Two important consequences:

1. **Q-learning learns $q_*$ directly.** Once $Q$ converges, $\arg\max_a Q(s, a)$ is the optimal policy. No annealing of $\epsilon$ to zero is required for the *target* to be correct — only for the agent's *behavior* to match the learned policy at deployment.
2. **The behavior policy must still cover the state-action space.** If your $\epsilon$-greedy never visits state $s$ with action $a$, $Q(s, a)$ never updates. Off-policy frees you from caring about *which* exploration policy you use, but not from caring *whether* it explores.

On CliffWalking, watching both algorithms train side by side is illuminating. Q-learning's learned greedy policy is "walk along the very edge of the cliff, one step from the goal." That is optimal — when followed perfectly, it pays $-13$ per episode. SARSA's learned policy is "take the upper route, two rows away from the cliff." That pays $-17$ per episode when followed perfectly — but it is the *better* policy when you have to keep exploring, because the upper route's $-100$ cliff falls are rare. Online return (i.e., the sum of rewards the agent actually collects while training) is better with SARSA. Asymptotic greedy return is better with Q-learning. Both converge to the same optimal greedy policy as $\epsilon \to 0$.

## The math

### The Q-learning update

The Q-learning update rule:

$$
\boxed{\;Q(S_t, A_t) \;\leftarrow\; Q(S_t, A_t) + \alpha\,\Bigl[R_{t+1} + \gamma \max_a Q(S_{t+1}, a) - Q(S_t, A_t)\Bigr].\;}
$$

The TD target is $R_{t+1} + \gamma \max_a Q(S_{t+1}, a)$ — the same as SARSA but with the sampled $A_{t+1}$ replaced by the action-maximising row max.

### Terminal handling

If $S_{t+1}$ is terminal, $\max_a Q(S_{t+1}, a) \equiv 0$ (terminal Q's are conventionally zero). The update degenerates to

$$
Q(S_t, A_t) \leftarrow Q(S_t, A_t) + \alpha[R_{t+1} - Q(S_t, A_t)].
$$

In code: `bootstrap = 0.0 if done else max(Q[next_state])`.

### Why off-policy?

![Q-table: initially all zeros (left). After training (right), each entry Q(s,a) estimates the optimal expected return for taking action a in state s. The greedy policy reads off the argmax of each row.](https://upload.wikimedia.org/wikipedia/commons/thumb/e/e0/Q-Learning_Matrix_Initialized_and_After_Training.png/500px-Q-Learning_Matrix_Initialized_and_After_Training.png)

The target $\max_a Q(S_{t+1}, a)$ is what $q_*$ satisfies in the Bellman *optimality* equation. So Q-learning's update is a *sampled* version of the Bellman optimality backup — the same equation value iteration iterates analytically. Where value iteration sums over $p(s', r \mid s, a)$ explicitly, Q-learning samples one $(s', r)$ from the environment.

Because the target equation $q_*$ does not depend on the policy, Q-learning's bootstrap does not depend on which policy collected the data. Whence "off-policy."

### Symbol glossary

| Symbol | Meaning |
| ------------------- | ---------------------------------------------------------------------- |
| $Q(s, a)$ | Action-value table |
| $S_t, A_t$ | Current state and action — the cell of $Q$ being updated |
| $R_{t+1}$ | Immediate reward |
| $S_{t+1}$ | Next state |
| $\max_a Q(S_{t+1}, a)$ | Greedy bootstrap — max across the next-state row of $Q$ |
| $\alpha$ | Learning rate (lesson default: $0.10$) |
| $\gamma$ | Discount factor (lesson default: $0.95$) |
| $\epsilon$ | Behavior policy exploration rate (lesson default: $0.20$) |

### Worked numeric example

Same setup as the SARSA example. The agent is at $S_t = 36$ (start), takes $A_t = $ UP, receives $R_{t+1} = -1$, lands in $S_{t+1} = 24$.

Suppose the current $Q$ table has the next-state row:

$$
Q(24, \text{LEFT}) = -4.5, \quad Q(24, \text{DOWN}) = -6.0, \quad Q(24, \text{RIGHT}) = -3.0, \quad Q(24, \text{UP}) = -3.8
$$

and $Q(36, \text{UP}) = -5.0$ (same as before). With $\alpha = 0.10$, $\gamma = 1.0$:

$$
\max_a Q(24, a) = \max\{-4.5, -6.0, -3.0, -3.8\} = -3.0.
$$

$$
\text{target} = R_{t+1} + \gamma \max_a Q(S_{t+1}, a) = -1 + 1.0 \cdot (-3.0) = -4.0.
$$

$$
\delta_t = -4.0 - (-5.0) = 1.0.
$$

$$
Q(36, \text{UP}) \leftarrow -5.0 + 0.10 \cdot 1.0 = -4.9.
$$

In this particular case the answer is the same as SARSA's, because the SARSA sample $A_{t+1} = $ RIGHT happened to coincide with the greedy choice (RIGHT had the highest $Q$). The two algorithms diverge when the sampled $A_{t+1}$ is *not* greedy — which is exactly $\epsilon$ of the time. On those steps, SARSA's bootstrap drags toward the explored (typically worse) action's value, while Q-learning's bootstrap stays on the greedy value.

## How the code does it

The starter code from `backend/lessons.py`:

```python
LEARNING_RATE = 0.10
DISCOUNT_FACTOR = 0.95
EXPLORATION_RATE = 0.20
EPISODE_COUNT = 6

def q_learning_update(Q, state, action, reward, next_state, alpha=LEARNING_RATE, gamma=DISCOUNT_FACTOR):
 best_next_value = __BLANK_q_learning_best_next__
 td_target = reward + gamma * best_next_value
 # TODO(student): apply the one-step TD update to the chosen Q-value.
 raise NotImplementedError("TODO: q_learning_update_rule")
 return Q
```

Compare this signature to `sarsa_update`: there is **no `next_action` parameter**. That is the structural sign that Q-learning is off-policy — the target does not need to know what action the agent will take next. The driver loop is simpler too: only one $\epsilon$-greedy sample per step, not two.

Map each parameter to the math:

- `Q` — the action-value table.
- `state, action` — $S_t, A_t$, the cell being updated.
- `reward` — $R_{t+1}$.
- `next_state` — $S_{t+1}$.
- `alpha, gamma` — learning rate and discount.

**TODO 1: `q_learning_best_next`.** The bootstrap term is $\max_a Q(S_{t+1}, a)$. In Python this is:

```python
best_next_value = max(Q[next_state])
```

Or, if `Q` is a NumPy array, `Q[next_state].max()`. This is the off-policy hook. (If you used `Q[next_state][next_action]` here, with `next_action` from the behavior policy, you would be writing SARSA, not Q-learning.)

For terminal handling, the driver should make sure to either skip the update when done or pass a sentinel that yields zero. A common pattern in the driver:

```python
if done:
 Q[state][action] += alpha * (reward - Q[state][action])
else:
 Q[state][action] += alpha * (reward + gamma * max(Q[next_state]) - Q[state][action])
```

The starter pushes terminal handling out of the function — the success criteria assume the caller passes the correct `next_state` and that the `Q[next_state]` row is zero for terminal states (which is the typical initialisation). For a strict implementation, you would add a `done` flag to the signature and zero out the bootstrap when `done` is True.

After the bootstrap line, `td_target = reward + gamma * best_next_value` literally encodes $R_{t+1} + \gamma \max_a Q(S_{t+1}, a)$. No TODO there.

**TODO 2: `q_learning_update_rule`.** Move $Q(S_t, A_t)$ a fraction $\alpha$ toward the target:

```python
Q[state][action] = Q[state][action] + alpha * (td_target - Q[state][action])
```

Identical in structure to SARSA's update — the only difference between the two algorithms is the bootstrap, not the update mechanics.

### The driver loop

```python
state, info = env.reset()
done = False
while not done:
 action = epsilon_greedy(Q, state, epsilon)
 next_state, reward, terminated, truncated, info = env.step(action)
 done = terminated or truncated
 q_learning_update(Q, state, action, reward, next_state)
 state = next_state
```

Compare to the SARSA driver: only one `epsilon_greedy` call, no `next_action` variable, no need to carry the next action into the next iteration. The update is fired and the agent moves on.

### A note on maximisation bias

`max(Q[next_state])` is biased when the $Q$ values are noisy. Specifically, $\mathbb{E}[\max_a Q(s', a)] \geq \max_a \mathbb{E}[Q(s', a)]$ — the expected max overestimates the max of the expected values. This is the "maximisation bias," and it is the motivation for *double Q-learning* (van Hasselt 2010), which uses two $Q$ tables and decouples the action selection from the value estimation in the bootstrap. For CliffWalking, with its deterministic transitions, the bias surfaces only through stochastic exploration and is small. For noisy environments (Atari, robotics), it matters and double Q-learning fixes it.

## Common pitfalls and misconceptions

**Pitfall 1: "Q-learning always outperforms SARSA."**
*Asymptotically*, both converge to the same optimal greedy policy as $\epsilon \to 0$. *Online during training*, SARSA can collect higher cumulative reward because its learned $Q$ accounts for exploration cost. On CliffWalking with fixed $\epsilon = 0.1$, SARSA's average per-episode online return is around $-17$; Q-learning's hovers around $-25$ because exploration steps occasionally tip the cliff. This performance gap is the canonical illustration of on-policy vs. off-policy trade-offs.

**Pitfall 2: "Off-policy means the behavior policy doesn't matter."**
It matters in one way: the behavior policy must visit every (state, action) pair infinitely often. Otherwise $Q(s, a)$ for unvisited pairs never updates and the algorithm cannot converge. A purely greedy behavior policy ($\epsilon = 0$) can starve exploration and fail.

**Pitfall 3: "The max is over the policy's action distribution."**
No — the max is over the *full* action set $\mathcal{A}(S_{t+1})$, ignoring the behavior policy. That is exactly what makes the target equivalent to one Bellman-optimality backup.

**Pitfall 4: "Q-learning has no maximisation bias."**
It does, especially when $Q$ values are noisy. Double Q-learning is the standard remedy.

**Pitfall 5 (the misconception called out in the spec): "Q-learning uses the sampled next action in the target."**
It does not. The target's bootstrap is $\max_a Q(S_{t+1}, a)$, not $Q(S_{t+1}, A_{t+1})$. That single replacement is what flips SARSA into Q-learning and on-policy into off-policy.

**Pitfall 6: "Q-learning is the same as one-step value iteration."**
Structurally similar — both use a max-bearing Bellman update. The difference: value iteration sums over the full distribution $p(s', r \mid s, a)$ analytically; Q-learning uses a single sampled transition. The expectation appears only implicitly through repeated sampling.

## Connection to the bigger picture

**Forward links.**
- *Deep Q-Networks (DQN, Mnih et al. 2015)* — Q-learning with a neural network parameterising $Q$, experience replay, and a target network. The same update rule, scaled to Atari.
- *Double Q-learning* — the maximisation-bias fix.
- *$n$-step Q-learning, distributional Q-learning, soft Q-learning, IQN, Rainbow…* — the modern deep-RL extensions all build on the same core off-policy update.

**Backward links.**
- `td_sarsa` — the on-policy cousin. Q-learning is SARSA with $\max_a Q(S_{t+1}, a)$ in place of $Q(S_{t+1}, A_{t+1})$.
- `dp_value_iteration` — the model-based optimality update. Q-learning is the sample analogue.
- `mdp_foundations` — the Bellman optimality equation for $q_*$ is the equality Q-learning's target estimates.


## Key takeaways

- Q-learning: `Q[s][a] += alpha * (reward + gamma * max(Q[next_state]) - Q[s][a])`.
- The bootstrap is the *greedy* next-state value, independent of which action the behavior policy will actually take.
- That makes Q-learning **off-policy**: it learns $q_*$ regardless of the behavior policy, provided every (state, action) is visited infinitely often.
- On CliffWalking, Q-learning learns the cliff-edge optimal policy; SARSA learns the safer route. Both converge to the same policy as $\epsilon \to 0$.
- Q-learning updates one Q-value using a greedy next-state target even when behavior still explores.

## Further reading

- Sutton, R. S. and Barto, A. G. (2018). *Reinforcement Learning: An Introduction*, 2nd ed. — Chapter 6, Section 6.5 (pp. 131–132). Update rule eq. 6.8 p. 131; algorithm box p. 131; CliffWalking comparison Example 6.6 p. 132; maximisation bias §6.7 p. 134. [http://incompleteideas.net/book/the-book-2nd.html](http://incompleteideas.net/book/the-book-2nd.html)
- Gymnasium CliffWalking documentation: [https://gymnasium.farama.org/v0.26.3/environments/toy_text/cliff_walking/](https://gymnasium.farama.org/v0.26.3/environments/toy_text/cliff_walking/)
- Watkins, C. J. C. H. (1989). *Learning from Delayed Rewards.* PhD thesis, King's College, Cambridge — original Q-learning thesis.
- Watkins, C. J. C. H. and Dayan, P. (1992). *Q-learning.* Machine Learning, 8:279–292 — convergence proof made rigorous.
- van Hasselt, H. (2010). *Double Q-learning.* NeurIPS — the maximisation-bias fix.
- Mnih, V. et al. (2015). *Human-level control through deep reinforcement learning.* Nature, 518:529–533 — DQN.
- David Silver's UCL course, Lecture 5 (Model-Free Control): [https://www.davidsilver.uk/teaching/](https://www.davidsilver.uk/teaching/)
