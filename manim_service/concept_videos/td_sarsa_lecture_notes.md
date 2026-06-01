# SARSA

## Why this concept matters

Monte Carlo updates wait for the episode to end. That works for Blackjack — five steps and you are done. It is intolerable for CliffWalking, where the agent might thrash for hundreds of steps before reaching the goal (or fall off the cliff, get teleported back to the start, and repeat). The agent is acquiring information on every step. We would like it to *learn* on every step too, not at the end of the episode. SARSA — *State, Action, Reward, State, Action* — is the temporal-difference algorithm that does exactly that.

SARSA's trick is one of the great ideas in RL: instead of waiting for the full return $G_t$, **bootstrap**. Use the agent's current estimate of $Q(S_{t+1}, A_{t+1})$ as a stand-in for the unobserved future return, and update $Q(S_t, A_t)$ toward that estimate plus the immediate reward. This is the same bootstrap trick as DP, but with the model-based $\sum$ over outcomes replaced by a single sampled transition. Every step, every transition, one tiny update — and over thousands of steps, $Q$ converges.

SARSA is **on-policy**: the target uses the action $A_{t+1}$ that the agent *actually chose next*, sampled from the same policy that produced $A_t$. That distinguishes it from Q-learning (next lesson), which uses the *greedy* action in the target. We will use CliffWalking-v0 — the canonical environment for showing why this difference matters.

In CliffWalking, the agent walks a $4 \times 12$ grid from start (bottom-left) to goal (bottom-right). The bottom row between the corners is a cliff: stepping onto it returns reward $-100$ and teleports the agent back to start. Every other step pays reward $-1$. Discount $\gamma = 1$; learning rate $\alpha = 0.10$; exploration rate $\epsilon = 0.20$ (the starter defaults).

![CliffWalking-v0: a 4×12 grid. Start (S) is bottom-left, Goal (G) is bottom-right. The cliff tiles (C) yield −100 and reset to start; every other step costs −1.](https://gymnasium.farama.org/_images/cliff_walking.gif)

## Intuition first

Imagine the agent at state $S_t$. It rolls $\epsilon$-greedy and selects $A_t$. The environment responds: reward $R_{t+1}$, next state $S_{t+1}$. The agent rolls $\epsilon$-greedy *again* and selects $A_{t+1}$. Now it has five things in hand: $S_t, A_t, R_{t+1}, S_{t+1}, A_{t+1}$. The name "SARSA" is literally these five letters in order.

SARSA's question: *what does this quintuple tell me about $Q(S_t, A_t)$?*

The Bellman equation says

$$
Q^\pi(S_t, A_t) = \mathbb{E}[R_{t+1} + \gamma Q^\pi(S_{t+1}, A_{t+1})].
$$

The right-hand side is the target. The agent does not know the expectation — but it has a sample: $R_{t+1} + \gamma Q(S_{t+1}, A_{t+1})$, using its own current estimate $Q$ for the bootstrap. The error between this target and the current estimate $Q(S_t, A_t)$ is the **TD error**:

$$
\delta_t = R_{t+1} + \gamma Q(S_{t+1}, A_{t+1}) - Q(S_t, A_t).
$$

Nudge $Q(S_t, A_t)$ toward the target by a fraction $\alpha$:

$$
Q(S_t, A_t) \leftarrow Q(S_t, A_t) + \alpha \delta_t.
$$

Done. Set $S \leftarrow S_{t+1}$, $A \leftarrow A_{t+1}$, and loop. Every transition produces one update — no waiting, no episode-ending.

**Why "on-policy" matters.** The bootstrap uses $Q(S_{t+1}, A_{t+1})$ where $A_{t+1}$ is *the action the behavior policy actually sampled*. Because the behavior policy is the same as the policy being evaluated, SARSA is learning $Q^\pi$ for the actual $\pi$ it is executing — exploration cost included. On CliffWalking, where exploration occasionally pushes the agent off the cliff, SARSA learns to avoid the cliff edge (the safer, longer route). Q-learning would learn the cliff-edge optimal route, accepting the $\epsilon$-greedy occasional disaster.

The video pauses on the moment $A_{t+1}$ gets sampled — that is the on-policy beat. Then it builds the TD target with that specific $A_{t+1}$ in the bootstrap slot.

## The math

### The SARSA update

The SARSA update rule:

$$
\boxed{\;Q(S_t, A_t) \;\leftarrow\; Q(S_t, A_t) + \alpha\,\bigl[R_{t+1} + \gamma Q(S_{t+1}, A_{t+1}) - Q(S_t, A_t)\bigr].\;}
$$

The name SARSA refers to the quintuple $(S_t, A_t, R_{t+1}, S_{t+1}, A_{t+1})$ that drives the update.

### Terminal handling

If $S_{t+1}$ is terminal, there is no next action — the episode is over. Convention: $Q(S_{t+1}, \cdot) \equiv 0$ at terminal states. The update reduces to

$$
Q(S_t, A_t) \leftarrow Q(S_t, A_t) + \alpha[R_{t+1} - Q(S_t, A_t)].
$$

In code, we usually compute `bootstrap = 0.0 if next_action is None else Q[next_state][next_action]` to handle both branches uniformly.

### Pieces of the update

It helps to name the parts:

$$
\underbrace{R_{t+1} + \gamma Q(S_{t+1}, A_{t+1})}_{\text{TD target}} \;-\; \underbrace{Q(S_t, A_t)}_{\text{current estimate}} \;=\; \underbrace{\delta_t}_{\text{TD error}}.
$$

The update is "move the estimate a fraction $\alpha$ of the way toward the target." The TD error $\delta_t$ measures how far off the estimate was.

### Symbol glossary

| Symbol | Meaning |
| ------------------ | ---------------------------------------------------------------------- |
| $Q(s, a)$ | Action-value table, indexed by (state, action) |
| $S_t, A_t$ | Current state and action — the cell of $Q$ we are about to update |
| $R_{t+1}$ | Immediate reward |
| $S_{t+1}, A_{t+1}$ | Next state and next sampled action |
| $\delta_t$ | TD error |
| $\alpha$ | Learning rate (lesson default: $0.10$) |
| $\gamma$ | Discount factor (lesson default: $0.95$; for CliffWalking convention $1$) |
| $\epsilon$ | $\epsilon$-greedy exploration rate (lesson default: $0.20$) |

### Worked numeric example

Say the agent is at CliffWalking state $S_t = 36$ (start), takes action $A_t = $ UP, receives reward $R_{t+1} = -1$, lands in state $S_{t+1} = 24$. The behavior policy samples $A_{t+1} = $ RIGHT.

The current $Q$ table has:

$$
Q(36, \text{UP}) = -5.0, \qquad Q(24, \text{RIGHT}) = -3.0.
$$

With $\alpha = 0.10$ and $\gamma = 1.0$:

$$
\text{target} = R_{t+1} + \gamma Q(S_{t+1}, A_{t+1}) = -1 + 1.0 \cdot (-3.0) = -4.0.
$$

$$
\delta_t = -4.0 - (-5.0) = 1.0.
$$

$$
Q(36, \text{UP}) \leftarrow -5.0 + 0.10 \cdot 1.0 = -4.9.
$$

So one transition moves $Q(36, \text{UP})$ from $-5.0$ to $-4.9$ — a tenth of the way toward the TD target. Repeat thousands of times, with $\alpha$ either constant or annealed, and $Q$ converges. For a constant $\alpha$ it converges *in mean* to $Q^\pi$, with residual variance; for a Robbins–Monro schedule ($\sum \alpha_t = \infty$, $\sum \alpha_t^2 < \infty$) it converges almost surely.

## How the code does it

The starter code from `backend/lessons.py`:

```python
LEARNING_RATE = 0.10
DISCOUNT_FACTOR = 0.95
EXPLORATION_RATE = 0.20
EPISODE_COUNT = 6

def sarsa_update(
 Q
 state
 action
 reward
 next_state
 next_action
 alpha=LEARNING_RATE
 gamma=DISCOUNT_FACTOR
):
 bootstrap = __BLANK_sarsa_bootstrap__
 td_target = reward + gamma * bootstrap
 # TODO(student): apply the on-policy SARSA update to the selected Q-value.
 raise NotImplementedError("TODO: sarsa_update_rule")
 return Q
```

The function performs *one* update — one SARSA quintuple's worth of work. The outer training loop (in a driver elsewhere) is responsible for stepping the environment, sampling actions with $\epsilon$-greedy, and calling `sarsa_update` once per transition.

Map each parameter to the math:

- `Q` — the table $Q$, mutated in place.
- `state, action` — $S_t, A_t$ (the cell being updated).
- `reward` — $R_{t+1}$.
- `next_state` — $S_{t+1}$.
- `next_action` — $A_{t+1}$, the **sampled** next action. Or `None` if $S_{t+1}$ is terminal.
- `alpha, gamma` — learning rate and discount.

**TODO 1: `sarsa_bootstrap`.** The bootstrap term is $Q(S_{t+1}, A_{t+1})$ on non-terminal transitions and $0$ on terminal ones. The natural expression:

```python
bootstrap = 0.0 if next_action is None else Q[next_state][next_action]
```

This is the on-policy hook. The `next_action` was sampled by the *same* behavior policy that picked `action` — that is what makes SARSA on-policy. (If you used `max(Q[next_state])` here instead, you would be writing Q-learning, not SARSA.)

After the bootstrap line, `td_target = reward + gamma * bootstrap` literally implements $R_{t+1} + \gamma Q(S_{t+1}, A_{t+1})$. No TODO needed there.

**TODO 2: `sarsa_update_rule`.** The actual update — move $Q(S_t, A_t)$ a fraction $\alpha$ toward the target:

```python
Q[state][action] = Q[state][action] + alpha * (td_target - Q[state][action])
```

Or equivalently `Q[state][action] += alpha * (td_target - Q[state][action])`. Either form computes $Q + \alpha\delta$.

That is the whole update. One line. Read it back to the equation:

- `td_target - Q[state][action]` is $\delta_t$, the TD error.
- `alpha * delta_t` is the magnitude of the nudge.
- `Q[state][action] +=...` writes the new estimate back.

### Why `next_action` is a parameter

The driver outside `sarsa_update` is responsible for sampling `next_action` from the behavior policy *before* calling this function. That's the on-policy contract: `next_action` is *the action the agent will actually take next*, not a hypothetical greedy choice. The driver's loop looks roughly like:

```python
state, info = env.reset()
action = epsilon_greedy(Q, state, epsilon)
done = False
while not done:
 next_state, reward, terminated, truncated, info = env.step(action)
 done = terminated or truncated
 next_action = None if done else epsilon_greedy(Q, next_state, epsilon)
 sarsa_update(Q, state, action, reward, next_state, next_action)
 state, action = next_state, next_action
```

Notice the two `epsilon_greedy` calls per step — one for the current action, one for the next action. That second call is what makes the quintuple S-A-R-S-A. Q-learning will have only one `epsilon_greedy` call per step (because Q-learning's target uses $\max$, not a sampled $A_{t+1}$).

### Terminal handling in the driver

When `done` is True, `next_action` is set to `None`, which triggers the `bootstrap = 0.0` branch inside `sarsa_update`. That is the cleanest way to encode "no future Q to bootstrap from."

## Common pitfalls and misconceptions

**Pitfall 1: "SARSA learns $q_*$."**
Not directly. SARSA learns $q_\pi$ for the *behavior policy* $\pi$ it is following. To recover $q_*$, the behavior policy must converge to greedy — e.g., $\epsilon$-greedy with $\epsilon \to 0$ over time. (and the convergence theorem citation) makes this explicit.

**Pitfall 2: "On-policy means the policy doesn't change."**
On-policy means the policy used to *generate behavior* is the same as the policy being *evaluated and improved*. The policy itself must change as $Q$ updates — that is the whole point. The contrast is with off-policy methods (Q-learning), where behavior and target policies are different.

**Pitfall 3: "SARSA can't learn during the same episode the agent is acting in."**
It can — every step. That is the whole advantage of TD over MC. emphasises this "online, fully incremental fashion."

**Pitfall 4: "SARSA is always safer than Q-learning."**
SARSA's safety on CliffWalking comes from a specific structural fact: the behavior policy used for action selection *is the policy being evaluated*, so the value function bakes in the cost of $\epsilon$-greedy exploration. With $\epsilon \to 0$ both SARSA and Q-learning converge to the same optimal greedy policy. With fixed $\epsilon > 0$, SARSA's $Q$ values reflect "the value of being here and continuing to explore $\epsilon$ of the time" — which on CliffWalking means avoiding the cliff edge because exploration steps there are catastrophic.

**Pitfall 5 (the misconception called out in the spec): "SARSA's target uses the optimal next action."**
It does not. The target uses the action that the behavior policy *actually sampled*, which on an exploration step may be a non-greedy action. That is the difference between on-policy and off-policy. If you replaced $Q(S_{t+1}, A_{t+1})$ with $\max_a Q(S_{t+1}, a)$, you would be running Q-learning.

## Connection to the bigger picture

**Forward links.**
- `td_q_learning` — the off-policy cousin. Same structure, but replaces $Q(S_{t+1}, A_{t+1})$ with $\max_a Q(S_{t+1}, a)$. Learns $q_*$ directly, independent of behavior policy.
- *Expected SARSA* — uses the *expected* value of $Q(S_{t+1}, \cdot)$ under the policy, instead of the sampled action. Lower variance than SARSA, still on-policy. Not covered in this course.
- $n$-step TD, TD($\lambda$), and eligibility traces — generalisations that interpolate between TD($0$) and Monte Carlo.

**Backward links.**
- `mc_first_visit` — model-free, sample-based. SARSA inherits the sampling but adds bootstrapping.
- `dp_value_iteration` — the model-based optimality update. SARSA's bootstrap is the sample analogue of DP's Bellman backup.
- `mdp_foundations` — the Bellman equation for $q_\pi$ is the equality SARSA's target estimates.


## Key takeaways

- SARSA does one update per transition: `Q[s][a] += alpha * (reward + gamma * Q[s'][a'] - Q[s][a])`.
- On-policy means the bootstrap action $A_{t+1}$ is the action the behavior policy actually sampled — not the greedy max.
- Terminal transitions zero out the bootstrap: `bootstrap = 0.0 if next_action is None else Q[next_state][next_action]`.
- SARSA learns $q_\pi$ for the behavior policy $\pi$ — to learn $q_*$, drive $\epsilon$ toward $0$.
- SARSA updates one Q-value using the reward plus the discounted value of the next sampled action.

## Further reading

- Sutton, R. S. and Barto, A. G. (2018). *Reinforcement Learning: An Introduction*, 2nd ed. — Chapter 6, Section 6.4 (pp. 129–131). Update rule eq. 6.7 p. 130; algorithm box p. 130; CliffWalking comparison Example 6.6 p. 132. [http://incompleteideas.net/book/the-book-2nd.html](http://incompleteideas.net/book/the-book-2nd.html)
- Gymnasium CliffWalking documentation: [https://gymnasium.farama.org/v0.26.3/environments/toy_text/cliff_walking/](https://gymnasium.farama.org/v0.26.3/environments/toy_text/cliff_walking/)
- Rummery, G. A. and Niranjan, M. (1994). *On-Line Q-Learning Using Connectionist Systems.* Cambridge University Engineering Department — the original SARSA paper (then called "modified connectionist Q-learning").
- David Silver's UCL course, Lecture 5 (Model-Free Control): [https://www.davidsilver.uk/teaching/](https://www.davidsilver.uk/teaching/)
