# Policy Improvement

## Why this concept matters

Policy evaluation answers "how good is this policy?" Value iteration answers "what is the best value table?" Policy improvement answers the question that ties the two together: **given a value table, what is a better policy?** It is the "improvement" half of the policy-iteration cycle, and it is also the algorithm you would use to extract a deployable policy from any value function — including the one value iteration leaves you with.

The mechanism is short enough to state in a single sentence: at each state, look one step ahead under the current value table, score every action by the expected return it would produce, and switch the policy to the highest-scoring action. That is it. The mathematical justification — the **policy improvement theorem** (S&B eq. 4.7–4.8) — is what guarantees the new policy is at least as good as the old one. Iterate evaluation and improvement until the policy stops changing, and you arrive at $\pi_*$.

The environment is FrozenLake-v1, $\gamma = 0.95$. We assume the value table $V$ has already been computed for some policy by `dp_policy_eval` (or is approximately $v_*$ from `dp_value_iteration`). The job of this lesson is to read $V$ and write down the new, greedy policy. The output is a one-hot policy table: one row per state, with $1.0$ on the greedy action and $0.0$ elsewhere.

## Intuition first

Stand on FrozenLake state $14$ — directly left of the goal. Imagine we have already computed $v_\pi$ for the uniform-random policy. The value table looks something like this near the goal (rough numbers, the exact values are from `dp_policy_eval`):

| State | $v_\pi$ |
| ----- | ------- |
| $10$  | $0.27$  |
| $13$  | $0.34$  |
| $14$  | $0.50$  |
| $15$  | $0.00$ (goal, terminal) |

We want to know: from state $14$, which action would give the best return if we then *kept following* $\pi$ afterwards? That hypothetical "deviate for one step, then go back to $\pi$" return is exactly the action-value function

$$
q_\pi(s, a) \;=\; \sum_{s', r} p(s', r \mid s, a)[r + \gamma v_\pi(s')].
$$

Compute $q_\pi(14, \text{LEFT}), q_\pi(14, \text{DOWN}), q_\pi(14, \text{RIGHT}), q_\pi(14, \text{UP})$, pick the largest, and call its action *the* new action for state $14$. That is policy improvement. The theorem says: if you do this at every state and the resulting policy $\pi'$ is anywhere different from $\pi$, then $v_{\pi'} \geq v_\pi$ at every state, with strict inequality somewhere.

If $\pi'$ equals $\pi$ everywhere, you have reached the fixed point — and the fixed point of greedy improvement under the Bellman optimality equation is $\pi_*$. (S&B p. 79.)

The video shows the four action backups computed one at a time as a small bar chart to the right of the focal state, the argmax bar lighting up, and the policy arrow on the grid flipping from a tangle of four equiprobable arrows to a single thick greedy arrow.

## The math

### Greedy policy improvement

The greedy policy with respect to a value function $V$ is

$$
\boxed{\;\pi'(s) \;=\; \arg\max_a \sum_{s', r} p(s', r \mid s, a)[r + \gamma V(s')].\;}
$$

This is S&B eq. 4.9 (p. 79). The inner sum is the action value $q(s, a)$ computed from $V$ via one-step lookahead; the $\arg\max$ picks the action whose action value is largest.

### The policy improvement theorem

Why does greedy improvement work? The theorem (S&B eq. 4.7–4.8, p. 78):

> If $q_\pi(s, \pi'(s)) \geq v_\pi(s)$ for all $s \in \mathcal{S}$, then $v_{\pi'}(s) \geq v_\pi(s)$ for all $s$, with strict inequality at any $s$ where eq. 4.7 is strict.

In words: if the new policy's chosen action is at least as good as $\pi$'s, *evaluated under $\pi$*, then the new policy's full value function is at least as good as $\pi$'s. Since the greedy action is by construction the argmax of $q_\pi(s, \cdot)$, and the argmax is at least as good as $\pi(s)$ (which is one of the actions in the max), the condition is satisfied automatically.

That is what makes the improvement *guaranteed*. It is not a heuristic; it is a theorem with a clean proof (S&B pp. 78–79).

### Symbol glossary

| Symbol             | Meaning                                                                |
| ------------------ | ---------------------------------------------------------------------- |
| $V(s)$             | The given value table (read-only input here)                           |
| $q_\pi(s, a)$      | Action value — one number per (state, action)                          |
| $\pi'(s)$          | The new, improved policy                                               |
| $\arg\max_a$       | The action index that maximises the inner sum                          |
| $p(s', r \mid s, a)$ | Environment dynamics                                                 |
| $\gamma$           | Discount factor (lesson default: $0.95$)                               |

### Worked numeric example

Take state $14$ again, with $V$ set to (rough) values from a previous evaluation pass. For simplicity, assume:

$$
V(10) = 0.27, \quad V(13) = 0.34, \quad V(14) = 0.50, \quad V(15) = 0.
$$

Using the `env.unwrapped.P[14]` table from the previous lessons, compute the action values:

**$a = $ LEFT,** successors $\{(10, 0), (13, 0), (14, 0)\}$ each $1/3$:

$$
q(14, \text{LEFT}) = \tfrac{1}{3}(0 + 0.95 \cdot 0.27) + \tfrac{1}{3}(0 + 0.95 \cdot 0.34) + \tfrac{1}{3}(0 + 0.95 \cdot 0.50) \approx 0.351.
$$

**$a = $ DOWN,** successors $\{(13, 0), (14, 0), (15, 1)\}$ each $1/3$:

$$
q(14, \text{DOWN}) = \tfrac{1}{3}(0.95 \cdot 0.34) + \tfrac{1}{3}(0.95 \cdot 0.50) + \tfrac{1}{3}(1 + 0.95 \cdot 0) \approx 0.599.
$$

**$a = $ RIGHT,** successors $\{(14, 0), (15, 1), (10, 0)\}$ each $1/3$:

$$
q(14, \text{RIGHT}) = \tfrac{1}{3}(0.95 \cdot 0.50) + \tfrac{1}{3}(1) + \tfrac{1}{3}(0.95 \cdot 0.27) \approx 0.577.
$$

**$a = $ UP,** successors $\{(10, 0), (15, 1), (13, 0)\}$ each $1/3$:

$$
q(14, \text{UP}) = \tfrac{1}{3}(0.95 \cdot 0.27) + \tfrac{1}{3}(1) + \tfrac{1}{3}(0.95 \cdot 0.34) \approx 0.526.
$$

Take the argmax:

$$
\pi'(14) = \arg\max \{0.351, 0.599, 0.577, 0.526\} = \text{DOWN} \;(=1).
$$

The improved policy row for state $14$ is $[0, 1, 0, 0]$ — a one-hot pointing at DOWN. Compare this to the uniform-random row $[0.25, 0.25, 0.25, 0.25]$: the policy is *deterministic* now, and it picks DOWN — the action that has the highest chance of landing on the goal directly.

If the next evaluation pass against $\pi'$ produces an even better value table, and we re-run improvement, we may end up flipping more arrows. The process halts when no state's argmax changes — at which point $\pi = \pi_*$.

## How the code does it

The starter code in `backend/lessons.py`:

```python
DISCOUNT_FACTOR = 0.95

def policy_improvement(V, env, gamma=DISCOUNT_FACTOR):
    action_count = env.action_space.n
    policy = [[0.0 for _ in range(action_count)] for _ in range(len(V))]

    for state in range(len(V)):
        action_values = []
        for action in range(action_count):
            action_value = 0.0
            # TODO(student): compute the one-step lookahead return for this action.
            raise NotImplementedError("TODO: policy_improvement_backup")
            action_values.append(action_value)

        best_action = __BLANK_policy_improvement_best_action__
        policy[state][best_action] = 1.0

    return policy
```

The shape is almost identical to `dp_value_iteration` — same outer loop over states, same inner loop over actions, same accumulation of action values. The only differences are:

1. **No outer convergence loop.** Improvement is a single pass: read $V$ once, write a new policy once. (The convergence comes from the outer policy-iteration loop, which alternates evaluation and improvement.)
2. **Different reduction at the end.** Value iteration takes `max(action_values)` and writes it to $V[\text{state}]$. Improvement takes `argmax(action_values)` and writes a one-hot row to `policy[state]`.

Map each line onto the equation $\pi'(s) = \arg\max_a \sum_{s', r} p(s', r \mid s, a)[r + \gamma V(s')]$:

- `policy = [[0.0 for _ in range(action_count)] for _ in range(len(V))]` — initialise a $|\mathcal{S}| \times |\mathcal{A}|$ matrix of zeros. Each row will be a one-hot probability distribution after we fill in the greedy action.
- `for state in range(len(V)):` — outer loop over $s \in \mathcal{S}$.
- `action_values = []` — accumulator for the four (or $|\mathcal{A}|$) action values for this state.
- `for action in range(action_count):` — loop over $a$.
- `action_value = 0.0` — running sum for one action backup.

**TODO 1: `policy_improvement_backup`.** Compute the one-step lookahead for the current action — exactly the same inner block as in value iteration:

```python
for transition_prob, next_state, reward, done in env.unwrapped.P[state][action]:
    action_value += transition_prob * (reward + gamma * V[next_state])
```

`transition_prob` is $p(s', r \mid s, a)$; `reward + gamma * V[next_state]` is $r + \gamma V(s')$. The accumulated `action_value` is $q(s, a) = \sum_{s', r} p(s', r \mid s, a)[r + \gamma V(s')]$ — the action value of $(s, a)$ given the current $V$.

**TODO 2: `policy_improvement_best_action`.** After the action loop, `action_values` is a list of $|\mathcal{A}|$ numbers. We want the *index* of the largest one, not its value:

```python
best_action = int(np.argmax(action_values))
```

(Or, without NumPy, `best_action = max(range(action_count), key=action_values.__getitem__)`.) The subsequent line `policy[state][best_action] = 1.0` writes the one-hot row. Note that the row was already all-zeros from initialisation, so writing $1.0$ on the greedy index gives a valid one-hot distribution.

### Why the policy is one-hot

The mathematics of policy improvement permits *stochastic* greedy policies that split probability arbitrarily across tied maximisers (S&B p. 79, last paragraph). The starter code's success criteria insist on a *deterministic* (one-hot) policy for simplicity — so even if two actions tie, you pick one (`np.argmax` breaks ties by returning the smallest index). For a tabular task with no convergence concerns, this is fine; for tasks where exploration via $\epsilon$-soft policies matters, you would mix in a baseline probability across all actions.

### A note on `np.argmax` versus a manual loop

If you cannot use NumPy in your environment, the same effect:

```python
best_action = 0
best_value = action_values[0]
for a in range(1, action_count):
    if action_values[a] > best_value:
        best_value = action_values[a]
        best_action = a
```

Either form is correct. NumPy is faster and more readable for sane-sized action spaces.

## Common pitfalls and misconceptions

**Pitfall 1: "The new greedy policy is optimal."**
It is only guaranteed to be *at least as good as* the old one. It is optimal exactly when $V \approx v_*$ — which is the case if you fed in the output of value iteration, but *not* generally if you fed in $v_\pi$ for some $\pi \neq \pi_*$. To reach $\pi_*$ from a non-optimal $V$, you have to alternate evaluation and improvement.

**Pitfall 2: "Each improvement must change the policy."**
A pass that produces $\pi' = \pi$ is the *termination condition* for policy iteration — it indicates $\pi$ is already optimal. The Sutton & Barto algorithm box (p. 80) uses a `policy-stable` flag for exactly this.

**Pitfall 3: "You need exact $v_\pi$ for the improvement step."**
The policy improvement theorem (S&B eq. 4.7) holds for any $V$ the new policy is greedy with respect to — not just the exact $v_\pi$. Truncated policy iteration (and value iteration's interleaved improvement) exploits this: you do not have to wait for policy evaluation to fully converge before improving.

**Pitfall 4: "Ties must be broken deterministically."**
S&B explicitly allows stochastic policies with arbitrary apportioning of probability among tied actions (p. 79, last paragraph) — the improvement guarantee still holds. The course code uses `argmax`, which is deterministic and picks the smallest tied index, but the math does not require this.

**Pitfall 5: "Policy improvement updates the value table."**
It does not. The value table $V$ is *read-only* inside `policy_improvement`. Only the policy matrix is written. This is the dual of policy evaluation: there, $\pi$ was read-only and $V$ was written. Both halves together make the cycle.

## Connection to the bigger picture

**Forward links.**
- **Policy iteration.** Alternate `dp_policy_eval` and `dp_policy_improvement` until the policy stops changing. Each iteration outputs a strictly better (or equal) policy. Convergence is guaranteed in a finite number of outer iterations for finite MDPs.
- `dp_value_iteration` is what you get when you collapse one sweep of evaluation and one greedy step into a single update — same machinery, fused for speed.

**Backward links.** `dp_policy_eval` (provides the value table that improvement reads). `mdp_foundations` (defines the action-value function $q_\pi(s, a)$ that improvement implicitly computes). `transition_prob` (the $p(s', r \mid s, a)$ table that the lookahead sums over).

In Sutton & Barto, this lesson is Chapter 4, Section 4.2 (pp. 76–80), eqs. 4.7–4.9. The policy improvement theorem proof is on pp. 78–79; the policy iteration algorithm box is on p. 80.

## Key takeaways

- Greedy policy improvement: $\pi'(s) = \arg\max_a \sum_{s', r} p(s', r \mid s, a)[r + \gamma V(s')]$.
- The policy improvement theorem guarantees $v_{\pi'} \geq v_\pi$ — the new policy is at least as good, often strictly better.
- The value table is read-only during improvement; only the policy is written.
- The inner machinery (computing $|\mathcal{A}|$ action values per state) is shared with value iteration; only the reduction differs (`argmax` here vs. `max` there).
- Policy improvement chooses the greedy action by comparing one-step lookahead returns built from the current value table.

## Further reading

- Sutton, R. S. and Barto, A. G. (2018). *Reinforcement Learning: An Introduction*, 2nd ed. — Chapter 4, Section 4.2 (pp. 76–80). Policy improvement theorem eqs. 4.7–4.8 (p. 78); greedy policy eq. 4.9 (p. 79); policy iteration algorithm box (p. 80). [http://incompleteideas.net/book/the-book-2nd.html](http://incompleteideas.net/book/the-book-2nd.html)
- Gymnasium FrozenLake-v1 documentation: [https://gymnasium.farama.org/v0.26.3/environments/toy_text/frozen_lake/](https://gymnasium.farama.org/v0.26.3/environments/toy_text/frozen_lake/)
- David Silver's UCL course, Lecture 3 (Planning by Dynamic Programming): [https://www.davidsilver.uk/teaching/](https://www.davidsilver.uk/teaching/)
- Bertsekas, D. P. (2017). *Dynamic Programming and Optimal Control* Vol. 1, §1.3 — formal proof of the policy improvement theorem in a more general DP setting.
