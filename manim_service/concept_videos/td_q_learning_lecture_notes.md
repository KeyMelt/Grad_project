# Q-Learning

## Why this concept matters

Q-learning is SARSA with one symbol changed — and that single change makes it the most influential algorithm in reinforcement learning. Where SARSA bootstraps from the *sampled* next action $Q(S_{t+1}, A_{t+1})$, Q-learning bootstraps from the *greedy* action $\max_a Q(S_{t+1}, a)$. The behavior policy still uses $\epsilon$-greedy to explore; the *target* uses the max. That makes Q-learning **off-policy**: it learns the optimal action-value function $q_*$ regardless of what behavior policy generated the data, as long as that policy visits every state-action pair infinitely often.

This decoupling is why Q-learning is everywhere: experience replay (DQN), demonstrations, hindsight relabeling — none of these work for on-policy SARSA, all of them work for Q-learning. Watkins's 1989 thesis was the breakthrough; the entire deep-RL revolution is, structurally, Q-learning with a neural network in place of the tabular $Q$.

We now move to **Taxi-v3** — a 5×5 grid world where a taxi cab must navigate to a passenger, pick them up, drive to the destination, and drop them off. The reward structure is simple: $-1$ per step (keep moving), $+20$ for a successful dropoff (terminal), and $-10$ for an illegal pickup or dropoff. The state encodes four pieces of information: the taxi's row and column, the passenger's location (one of four pickup spots R/G/Y/B, or inside the taxi), and the destination (one of the same four spots). That gives $5 \times 5 \times 5 \times 4 = 500$ discrete states and 6 actions (South, North, East, West, Pickup, Dropoff).

Taxi is the canonical Q-learning tutorial environment because its task naturally decomposes into **sub-goals**: navigate to the passenger → Pickup → navigate to the destination → Dropoff. Q-learning's greedy max-bootstrap lets the agent stitch together optimal sub-policies for each sub-goal without an explicit planner — the $+20$ terminal reward propagates backward through the Q-table, pulling the greedy policy toward the optimal route.

## Intuition first

Same setup as SARSA, but now on the Taxi grid. The agent is at $S_t$, samples $A_t$ via $\epsilon$-greedy, takes the step, observes $R_{t+1}$ and $S_{t+1}$. *Now* the algorithms diverge:

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

### Sub-goal composition on Taxi

Taxi illustrates why the greedy max-bootstrap matters. Consider the four sub-goals:

1. **Navigate to passenger** — a sequence of South/North/East/West moves, each paying $-1$.
2. **Pickup** — a single action at the passenger's location, paying $-1$.
3. **Navigate to destination** — more $-1$ moves.
4. **Dropoff** — $+20$, episode ends.

The $+20$ terminal reward starts at the dropoff state and, through repeated Q-learning updates, propagates backward: the states one step before dropoff acquire high Q-values, then two steps before, and so on. The greedy policy ($\arg\max_a Q(s,a)$) chains these sub-goals into the shortest path from any starting configuration. Q-learning does this *without knowing* what the sub-goals are — it just follows the value gradient.

### The SARSA contrast (cross-lesson)

You saw SARSA on CliffWalking in the previous lesson, where SARSA's on-policy bootstrap made it learn a *safer* route that avoided the cliff edge. On Taxi, the environments are different, but **the only code change is the bootstrap**: SARSA uses the *sampled* $Q(S_{t+1}, A_{t+1})$; Q-learning uses $\max_a Q(S_{t+1}, a)$. For a single Taxi transition, both algorithms form a target — the Q-learning target is always at least as high, because the max is always $\geq$ any single sampled action value.

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

The target $\max_a Q(S_{t+1}, a)$ is what $q_*$ satisfies in the Bellman *optimality* equation. So Q-learning's update is a *sampled* version of the Bellman optimality backup — the same equation value iteration iterates analytically. Where value iteration sums over $p(s', r \mid s, a)$ explicitly, Q-learning samples one $(s', r)$ from the environment.

Because the target equation $q_*$ does not depend on the policy, Q-learning's bootstrap does not depend on which policy collected the data. Whence "off-policy."

### Symbol glossary

| Symbol | Meaning |
| ------------------- | ---------------------------------------------------------------------- |
| $Q(s, a)$ | Action-value table (500 rows × 6 columns for Taxi) |
| $S_t, A_t$ | Current state and action — the cell of $Q$ being updated |
| $R_{t+1}$ | Immediate reward ($-1$ per step, $+20$ dropoff, $-10$ illegal) |
| $S_{t+1}$ | Next state |
| $\max_a Q(S_{t+1}, a)$ | Greedy bootstrap — max across the next-state row of $Q$ |
| $\alpha$ | Learning rate (lesson default: $0.10$) |
| $\gamma$ | Discount factor (lesson default: $0.95$) |
| $\epsilon$ | Behavior policy exploration rate (lesson default: $0.20$) |

### Worked numeric example: the +20 dropoff

The taxi has the passenger aboard and is at the destination. State $S_t$ encodes taxi at (0, 0), passenger in taxi, destination R — encoded state 16. The agent takes $A_t = $ Dropoff, receives $R_{t+1} = +20$, and $S_{t+1}$ is terminal (done = True).

With $\alpha = 0.10$, $\gamma = 0.95$, and $Q(16, \text{Dropoff}) = 0$ (initial):

$$
\text{terminal} \Rightarrow \max_a Q(S_{t+1}, a) = 0.
$$

$$
\text{target} = R_{t+1} + \gamma \cdot 0 = 20.
$$

$$
\delta_t = 20 - 0 = 20.
$$

$$
Q(16, \text{Dropoff}) \leftarrow 0 + 0.10 \cdot 20 = 2.0.
$$

The update moves Q a tenth of the way toward the target. After many episodes, $Q(16, \text{Dropoff})$ converges to $20$ (the full undiscounted terminal reward, since the bootstrap is zero).

### Worked navigation step

Now consider a navigation step one cell away from the dropoff. The taxi is at (1, 0), passenger aboard, destination R(0, 0). The agent takes $A_t = $ North, receives $R_{t+1} = -1$, and lands in the state where dropoff is possible. Suppose $Q(S_{t+1}) = [0, 0, 0, 0, 0, 2.0]$ (Dropoff already has value 2.0 from the previous update).

$$
\max_a Q(S_{t+1}, a) = 2.0 \quad \text{(Dropoff)}.
$$

$$
\text{target} = -1 + 0.95 \cdot 2.0 = 0.90.
$$

The $+20$ signal has already started flowing backward: the state one step before the dropoff now has a positive target, pulling the greedy policy toward it. After many episodes, this value flow extends all the way back to the starting configuration.

## How the code does it

The starter code:

```python
# Taxi-v3: 500 states (taxi pos × passenger × dest), 6 actions
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

Compare this signature to `sarsa_update`: there is **no `next_action` parameter**. That is the structural sign that Q-learning is off-policy — the target does not need to know what action the agent will take next.

Map each parameter to the math:

- `Q` — the action-value table (500 rows × 6 columns for Taxi).
- `state, action` — $S_t, A_t$, the cell being updated.
- `reward` — $R_{t+1}$ ($-1$ for steps, $+20$ for legal dropoff, $-10$ for illegal pickup/dropoff).
- `next_state` — $S_{t+1}$.
- `alpha, gamma` — learning rate and discount.

**TODO 1: `q_learning_best_next`.** The bootstrap term is $\max_a Q(S_{t+1}, a)$. In Python this is:

```python
best_next_value = max(Q[next_state])
```

This is the off-policy hook. (If you used `Q[next_state][next_action]` here, with `next_action` from the behavior policy, you would be writing SARSA, not Q-learning.)

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

Compare to the SARSA driver: only one `epsilon_greedy` call, no `next_action` variable, no need to carry the next action into the next iteration.

### A note on maximisation bias

`max(Q[next_state])` is biased when the $Q$ values are noisy. Specifically, $\mathbb{E}[\max_a Q(s', a)] \geq \max_a \mathbb{E}[Q(s', a)]$ — the expected max overestimates the max of the expected values. This is the "maximisation bias," and it is the motivation for *double Q-learning* (van Hasselt 2010), which uses two $Q$ tables and decouples the action selection from the value estimation in the bootstrap. For Taxi, with its deterministic transitions, the bias surfaces only through stochastic exploration and is small.

## Common pitfalls and misconceptions

**Pitfall 1: "Q-learning always outperforms SARSA."**
*Asymptotically*, both converge to the same optimal greedy policy as $\epsilon \to 0$. *Online during training*, SARSA can collect higher cumulative reward because its learned $Q$ accounts for exploration cost. You saw this on CliffWalking, where SARSA learned a safer route. On Taxi, the effect is subtler because there is no cliff — but SARSA's target still reflects exploration detours while Q-learning's target always assumes optimal future behavior.

**Pitfall 2: "Off-policy means the behavior policy doesn't matter."**
It matters in one way: the behavior policy must visit every (state, action) pair infinitely often. Taxi has 500 × 6 = 3,000 state-action pairs — exploration must cover them all for convergence.

**Pitfall 3: "The max is over the policy's action distribution."**
No — the max is over the *full* action set $\mathcal{A}(S_{t+1})$, ignoring the behavior policy. That is exactly what makes the target equivalent to one Bellman-optimality backup.

**Pitfall 4: "Q-learning has no maximisation bias."**
It does, especially when $Q$ values are noisy. Double Q-learning is the standard remedy.

**Pitfall 5: "Q-learning uses the sampled next action in the target."**
It does not. The target's bootstrap is $\max_a Q(S_{t+1}, a)$, not $Q(S_{t+1}, A_{t+1})$. That single replacement is what flips SARSA into Q-learning and on-policy into off-policy.

## Connection to the bigger picture

**Forward links.**
- *Deep Q-Networks (DQN, Mnih et al. 2015)* — Q-learning with a neural network parameterising $Q$, experience replay, and a target network. The same update rule, scaled to Atari.
- *Double Q-learning* — the maximisation-bias fix.
- *$n$-step Q-learning, distributional Q-learning, soft Q-learning, IQN, Rainbow…* — the modern deep-RL extensions all build on the same core off-policy update.

**Backward links.**
- `td_sarsa` — the on-policy cousin on CliffWalking. Q-learning is SARSA with $\max_a Q(S_{t+1}, a)$ in place of $Q(S_{t+1}, A_{t+1})$.
- `dp_value_iteration` — the model-based optimality update. Q-learning is the sample analogue.
- `mdp_foundations` — the Bellman optimality equation for $q_*$ is the equality Q-learning's target estimates.


## Key takeaways

- Q-learning: `Q[s][a] += alpha * (reward + gamma * max(Q[next_state]) - Q[s][a])`.
- The bootstrap is the *greedy* next-state value, independent of which action the behavior policy will actually take.
- That makes Q-learning **off-policy**: it learns $q_*$ regardless of the behavior policy, provided every (state, action) is visited infinitely often.
- On Taxi, the $+20$ dropoff reward propagates backward through the Q-table, composing sub-goals (navigate → pickup → navigate → dropoff) into the greedy policy.
- Q-learning updates one Q-value using a greedy next-state target even when behavior still explores.

## Further reading

- Sutton, R. S. and Barto, A. G. (2018). *Reinforcement Learning: An Introduction*, 2nd ed. — Chapter 6, Section 6.5 (pp. 131–132). Update rule eq. 6.8 p. 131; algorithm box p. 131; maximisation bias §6.7 p. 134. [http://incompleteideas.net/book/the-book-2nd.html](http://incompleteideas.net/book/the-book-2nd.html)
- Gymnasium Taxi documentation: [https://gymnasium.farama.org/environments/toy_text/taxi/](https://gymnasium.farama.org/environments/toy_text/taxi/)
- Watkins, C. J. C. H. (1989). *Learning from Delayed Rewards.* PhD thesis, King's College, Cambridge — original Q-learning thesis.
- Watkins, C. J. C. H. and Dayan, P. (1992). *Q-learning.* Machine Learning, 8:279–292 — convergence proof made rigorous.
- Dietterich, T. G. (2000). *Hierarchical Reinforcement Learning with the MAXQ Value Function Decomposition.* JAIR — Taxi as the canonical hierarchical sub-goal task.
- van Hasselt, H. (2010). *Double Q-learning.* NeurIPS — the maximisation-bias fix.
- Mnih, V. et al. (2015). *Human-level control through deep reinforcement learning.* Nature, 518:529–533 — DQN.
- David Silver's UCL course, Lecture 5 (Model-Free Control): [https://www.davidsilver.uk/teaching/](https://www.davidsilver.uk/teaching/)
