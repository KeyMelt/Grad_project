# Q-Learning

## Why this concept matters

Q-learning is SARSA with one symbol changed and that single change makes it the most influential algorithm in reinforcement learning. Where SARSA bootstraps from the sampled next action $Q(S_{t+1}, A_{t+1})$, Q-learning bootstraps from the greedy action $\max_a Q(S_{t+1}, a)$. The behavior policy still uses $\epsilon$-greedy to explore; the target uses the max. That makes Q-learning **off-policy**: it learns the optimal action-value function $q_*$ regardless of what behavior policy generated the data, as long as that policy visits every state-action pair infinitely often.

This decoupling is why Q-learning is everywhere: experience replay, demonstrations, hindsight relabeling, and DQN-style target learning all build on it. Watkins's 1989 thesis was the breakthrough; the deep-RL line that followed is structurally Q-learning with a function approximator in place of the tabular $Q$.

We now move to **Taxi-v3**, a 5x5 grid world where a taxi cab must navigate to a passenger, pick them up, drive to the destination, and drop them off. The reward structure is simple: $-1$ per step, $+20$ for a successful dropoff, and $-10$ for an illegal pickup or dropoff. The state encodes four pieces of information: the taxi row, the taxi column, the passenger location (R, G, Y, B, or inside the taxi), and the destination (R, G, Y, or B). That gives $5 \times 5 \times 5 \times 4 = 500$ discrete states and 6 actions.

Taxi is the canonical Q-learning tutorial environment because its task naturally decomposes into sub-goals: navigate to passenger, Pickup, navigate to destination, Dropoff. Q-learning's greedy max-bootstrap lets the agent stitch together optimal sub-policies for each sub-goal without an explicit planner. The terminal $+20$ reward propagates backward through the Q-table and pulls the greedy policy toward the shortest route.

## Intuition first

Same setup as SARSA, but now on the Taxi grid. The agent is at $S_t$, samples $A_t$ via $\epsilon$-greedy, takes the step, observes $R_{t+1}$ and $S_{t+1}$. Now the algorithms diverge:

- **SARSA** says: sample $A_{t+1}$ from the behavior policy and use $Q(S_{t+1}, A_{t+1})$ in the target.
- **Q-learning** says: ignore which action will actually be sampled next. Use the best possible next-state value, $\max_a Q(S_{t+1}, a)$.

The target becomes

$$
R_{t+1} + \gamma \max_a Q(S_{t+1}, a).
$$

The bootstrap term assumes the agent acts optimally from $S_{t+1}$ onward even though the behavior policy still explores. That is the off-policy nature: the target policy is greedy while the behavior policy remains $\epsilon$-greedy.

Two consequences matter immediately:

1. **Q-learning learns $q_*$ directly.** Once $Q$ converges, $\arg\max_a Q(s, a)$ is the optimal policy.
2. **The behavior policy must still explore.** If a state-action pair is never visited, its Q-value never updates.

### Sub-goal composition on Taxi

Taxi makes the max-bootstrap tangible. The agent must:

1. Navigate to the passenger.
2. Execute Pickup.
3. Navigate to the destination.
4. Execute Dropoff.

The $+20$ terminal reward begins at the successful dropoff state. Q-learning then propagates that value backward: states one move before dropoff become valuable, then states two moves away, and so on. The greedy policy ends up chaining the sub-goals into a shortest-path solution from many starting configurations.

### The SARSA contrast

You saw SARSA on CliffWalking in the previous lesson. Here the environment changes, but the core algorithmic distinction is identical: SARSA bootstraps from the sampled next action; Q-learning bootstraps from the maximum next-state action value. For a single Taxi transition, the Q-learning target is always at least as high as any sampled-action bootstrap because the max is always greater than or equal to one selected value.

## The math

### The Q-learning update

$$
\boxed{\;Q(S_t, A_t) \leftarrow Q(S_t, A_t) + \alpha\Bigl[R_{t+1} + \gamma \max_a Q(S_{t+1}, a) - Q(S_t, A_t)\Bigr].\;}
$$

The TD target is $R_{t+1} + \gamma \max_a Q(S_{t+1}, a)$.

### Terminal handling

If $S_{t+1}$ is terminal, the bootstrap is zero:

$$
Q(S_t, A_t) \leftarrow Q(S_t, A_t) + \alpha[R_{t+1} - Q(S_t, A_t)].
$$

In code: `bootstrap = 0.0 if done else max(Q[next_state])`.

### Why off-policy?

The target $\max_a Q(S_{t+1}, a)$ is what the Bellman optimality equation for $q_*$ requires. Q-learning is therefore a sampled version of an optimality backup. Where value iteration sums over the full transition model, Q-learning samples one transition at a time and moves the current estimate toward the optimal target.

### Symbol glossary

| Symbol | Meaning |
| --- | --- |
| $Q(s, a)$ | Action-value table (500 rows x 6 columns for Taxi) |
| $S_t, A_t$ | Current state and action |
| $R_{t+1}$ | Immediate reward |
| $S_{t+1}$ | Next state |
| $\max_a Q(S_{t+1}, a)$ | Greedy bootstrap |
| $\alpha$ | Learning rate |
| $\gamma$ | Discount factor |
| $\epsilon$ | Exploration rate used by the behavior policy |

### Worked dropoff example

Suppose the taxi has the passenger aboard and is already at the destination. State $S_t$ encodes taxi at the destination, passenger in taxi, and the matching destination label. The agent takes Dropoff, receives $R_{t+1} = +20$, and the episode ends.

With $\alpha = 0.10$, $\gamma = 0.95$, and initial $Q(S_t, \text{Dropoff}) = 0$:

$$
\text{bootstrap} = 0
$$

$$
\text{target} = 20
$$

$$
\delta_t = 20 - 0 = 20
$$

$$
Q(S_t, \text{Dropoff}) \leftarrow 0 + 0.10 \cdot 20 = 2.0
$$

That single update already makes the legal dropoff action look better than the rest of the row.

### Worked navigation example

Now consider a move one step before a good dropoff. Suppose the next-state row already contains a valuable Dropoff entry, such as

$$
Q(S_{t+1}) = [0, 0, 0, 0, 0, 2.0].
$$

The taxi takes a movement action, receives reward $-1$, and lands in that next state. Then

$$
\max_a Q(S_{t+1}, a) = 2.0
$$

$$
\text{target} = -1 + 0.95 \cdot 2.0 = 0.90
$$

The terminal reward has started flowing backward. Repeated updates spread that signal through the state space until the greedy policy reliably composes navigation, pickup, navigation, and dropoff.

## How the code does it

The lesson starter code is:

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

Unlike SARSA, there is no `next_action` parameter. That is the structural signature of the off-policy update.

Map the parameters directly to the math:

- `Q`: the action-value table.
- `state, action`: $S_t, A_t$.
- `reward`: $R_{t+1}$.
- `next_state`: $S_{t+1}$.
- `alpha, gamma`: the learning rate and discount.

**TODO 1: `q_learning_best_next`**

```python
best_next_value = max(Q[next_state])
```

This is the off-policy hook. If you used a sampled next action instead, you would be writing SARSA.

**TODO 2: `q_learning_update_rule`**

```python
Q[state][action] = Q[state][action] + alpha * (td_target - Q[state][action])
```

The mechanics of the update are identical to SARSA. The algorithmic difference is entirely in the bootstrap term.

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

Only one action sample is needed per step. There is no sampled `next_action` carried into the update.

### A note on maximization bias

`max(Q[next_state])` can overestimate the true best value when estimates are noisy. This is the maximization bias that motivates double Q-learning. Taxi is simple enough that the bias is usually mild, but the structural issue is already present.

## Common pitfalls and misconceptions

**Pitfall 1: "Q-learning always outperforms SARSA."**
Not necessarily during training. SARSA can collect better online return because its values reflect the cost of exploratory behavior. Q-learning instead targets optimal greedy behavior.

**Pitfall 2: "Off-policy means the behavior policy does not matter."**
It still matters for coverage. The behavior policy must visit enough of the state-action space for learning to occur.

**Pitfall 3: "The max is taken over the sampled policy distribution."**
No. The max is over the full action set in the next state.

**Pitfall 4: "Q-learning uses the sampled next action in the target."**
That is SARSA, not Q-learning.

**Pitfall 5: "Illegal pickup/dropoff is just another move penalty."**
No. Taxi uses a stronger $-10$ penalty to make invalid actions visibly worse than ordinary movement.

## Connection to the bigger picture

Forward links:

- DQN is Q-learning with a neural network.
- Double Q-learning addresses maximization bias.
- Many modern off-policy methods inherit this same greedy bootstrap pattern.

Backward links:

- `td_sarsa` is the on-policy cousin.
- `dp_value_iteration` performs the model-based optimality backup analytically.
- `mdp_foundations` introduces the Bellman optimality equation that Q-learning samples.

## Key takeaways

- Q-learning uses `max(Q[next_state])` in the bootstrap.
- The update remains incremental TD learning on one table entry at a time.
- Taxi makes the reward propagation visible because the greedy policy composes multiple sub-goals from one delayed terminal reward.
