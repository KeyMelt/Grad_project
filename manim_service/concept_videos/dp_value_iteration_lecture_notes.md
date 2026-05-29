# Value Iteration

## Why this concept matters

Policy evaluation answered "*given* a policy, how good is each state?" But we don't usually start with a policy we like — we want the *best* policy. One option is to alternate evaluation and improvement (policy iteration), but each evaluation is itself a long fixed-point loop. Value iteration is the shortcut: collapse evaluation and improvement into a single update by replacing the policy-weighted average with a maximum.

Here is the bargain. Instead of asking "what return does $\pi$ expect from state $s$?", value iteration asks "what is the *best* one-step backup I could perform from $s$, assuming I act optimally from $s'$ onwards?" That single switch — from $\sum_a \pi(a \mid s)$ to $\max_a$ — turns the Bellman *expectation* equation into the Bellman *optimality* equation. Iterate that until the values stop changing, and what you get is $v_*$: the optimal value function, the unique fixed point of the optimality equation.

We use FrozenLake-v1 again (`is_slippery=True`, $\gamma = 0.95$). The same heatmap that took ~70 sweeps under the uniform-random policy now converges to a *much brighter* heatmap, because the values are no longer dragged down by the silly random actions — every backup chooses the best action. The video pauses at one specific state and shows all four action backups one at a time so you can watch the $\max$ pick the winner.

## Intuition first

Stand on state $14$ in the FrozenLake grid, with the value table $V$ already partially computed (say, after a few sweeps). The question policy evaluation asks here is "what is the *average* return when I take each of the four actions with probability $1/4$?" The question value iteration asks is "what is the *best* of the four action values I could compute?"

Concretely:

- Compute the Bellman backup for $a = \text{LEFT}$ from state $14$. Call it $Q(14, \text{LEFT})$.
- Compute it for $a = \text{DOWN}$. Call it $Q(14, \text{DOWN})$.
- Compute it for $a = \text{RIGHT}$. Call it $Q(14, \text{RIGHT})$.
- Compute it for $a = \text{UP}$. Call it $Q(14, \text{UP})$.
- Set $V(14) \leftarrow \max\{Q(14, \text{LEFT}), Q(14, \text{DOWN}), Q(14, \text{RIGHT}), Q(14, \text{UP})\}$.

That is the entire mechanism. Repeat for every state, repeat the sweep until $V$ stops changing, and you have $v_*$. Notice three things:

1. **Value iteration does not store a policy.** It only stores $V$. To recover the optimal policy you do one final greedy pass — but during iteration, the only thing being updated is the value table.
2. **The $\max$ inherits the action-value structure even though we never explicitly write a $Q$ table.** Each iteration computes $|\mathcal{A}|$ action-value backups internally, takes their max, and discards them. (The next lesson, `dp_policy_improvement`, will store and use those action values to update a policy.)
3. **Value iteration converges to $v_*$, not just to $v_\pi$ for some specific $\pi$.** The result is *optimal*, no further improvement step needed.

The video freezes one FrozenLake state and shows the four candidate backups stacking up like bars in a chart. The bar that wins is the action the greedy policy would pick. The other three are discarded — and that discarding is the whole point.

## The math

### From Bellman expectation to Bellman optimality

Policy evaluation iterates the Bellman *expectation* equation:

$$
v_{k+1}^\pi(s) \;=\; \sum_a \pi(a \mid s) \sum_{s', r} p(s', r \mid s, a)[r + \gamma v_k^\pi(s')].
$$

Value iteration iterates the Bellman *optimality* equation (S&B eq. 4.10, p. 83):

$$
\boxed{\;V_{k+1}(s) \;\doteq\; \max_a \sum_{s', r} p(s', r \mid s, a)[r + \gamma V_k(s')].\;}
$$

The only difference is one symbol: $\sum_a \pi(a \mid s)$ becomes $\max_a$. But the consequence is profound — the fixed point of this iteration is $v_*$, the *optimal* value function, the same one that would be produced by full policy iteration.

### Extracting the optimal policy

Value iteration produces $V \approx v_*$, but downstream we usually want to *act* — and acting requires a policy, not a value function. After convergence we do one final greedy pass:

$$
\pi_*(s) \;=\; \arg\max_a \sum_{s', r} p(s', r \mid s, a)[r + \gamma V(s')].
$$

That is the same one-step lookahead but recording the argmax instead of the max. We will revisit this in the policy improvement lesson.

### Convergence condition

Same as policy evaluation: stop when $\Delta_k = \max_s |V_{k+1}(s) - V_k(s)| < \theta$. The starter code uses $\theta = 10^{-8}$. Convergence is guaranteed for $\gamma < 1$ or for problems where every policy terminates.

### Symbol glossary

| Symbol         | Meaning                                                          |
| -------------- | ---------------------------------------------------------------- |
| $V_k(s)$       | Value table at iteration $k$                                     |
| $v_*(s)$       | Optimal state-value function, the fixed point of $V_k$           |
| $Q_k(s, a)$    | Action value backup — computed internally, not stored explicitly |
| $p(s', r \mid s, a)$ | Environment dynamics                                       |
| $\gamma$       | Discount factor (lesson default: $0.95$)                         |
| $\theta$       | Convergence threshold (lesson default: $10^{-8}$)                |

### Worked numeric example

Take state $14$ again, on the very first sweep with $V_0 \equiv 0$ everywhere. We compute the four action backups one at a time.

From the `env.unwrapped.P[14]` table (slippery FrozenLake):

**Action $a = 0$ (LEFT):** successors $\{(10, 0, F), (13, 0, F), (14, 0, F)\}$, each $1/3$.

$$
Q_0(14, \text{LEFT}) \;=\; \tfrac{1}{3}(0 + 0.95 \cdot 0) + \tfrac{1}{3}(0 + 0.95 \cdot 0) + \tfrac{1}{3}(0 + 0.95 \cdot 0) \;=\; 0.
$$

**Action $a = 1$ (DOWN):** successors $\{(13, 0, F), (14, 0, F), (15, 1, T)\}$, each $1/3$.

$$
Q_0(14, \text{DOWN}) \;=\; \tfrac{1}{3}(0) + \tfrac{1}{3}(0) + \tfrac{1}{3}(1 + 0.95 \cdot 0) \;=\; \tfrac{1}{3} \approx 0.3333.
$$

**Action $a = 2$ (RIGHT):** successors $\{(14, 0, F), (15, 1, T), (10, 0, F)\}$, each $1/3$. Same arithmetic:

$$
Q_0(14, \text{RIGHT}) \;=\; \tfrac{1}{3} \approx 0.3333.
$$

**Action $a = 3$ (UP):** successors $\{(10, 0, F), (15, 1, T), (13, 0, F)\}$, each $1/3$. Same arithmetic:

$$
Q_0(14, \text{UP}) \;=\; \tfrac{1}{3} \approx 0.3333.
$$

Now apply the max:

$$
V_1(14) \;=\; \max\{0, \tfrac{1}{3}, \tfrac{1}{3}, \tfrac{1}{3}\} \;=\; \tfrac{1}{3} \approx 0.3333.
$$

Compare to policy evaluation's first sweep: $v_1^\pi(14) = 0.25$ under the uniform-random policy, versus $V_1(14) = 0.3333$ under value iteration. Value iteration is already pulling ahead because it has discarded the useless LEFT action.

The picture matters: three of the four actions tie at $1/3$. The optimal policy at state $14$ is not unique on the first sweep — any tie-breaking rule would produce a valid greedy choice. In later sweeps, as value propagates back further, the ties resolve and a unique optimal action emerges per state.

## How the code does it

The starter code in `backend/lessons.py`:

```python
DISCOUNT_FACTOR = 0.95

def value_iteration(V, env, gamma=DISCOUNT_FACTOR, theta=1e-8):
    delta = float("inf")
    action_count = env.action_space.n
    while delta > theta:
        delta = 0.0
        for state in range(len(V)):
            old_value = V[state]
            action_values = []
            for action in range(action_count):
                action_value = 0.0
                # TODO(student): back up one action value from transition branches.
                raise NotImplementedError("TODO: value_iteration_backup")
                action_values.append(action_value)
            V[state] = __BLANK_value_iteration_best_action__
            delta = max(delta, abs(old_value - V[state]))
    return V
```

The structure mirrors policy evaluation, but with one extra inner step and one different reduction at the end. Map each line to the optimality equation $V_{k+1}(s) = \max_a \sum_{s', r} p(s', r \mid s, a)[r + \gamma V_k(s')]$:

- `while delta > theta:` — outer convergence loop, same as policy evaluation.
- `for state in range(len(V)):` — sweep over $s \in \mathcal{S}$.
- `action_values = []` — we are about to compute one number per action and then take the max.
- `for action in range(action_count):` — loop over $a$. There is no `action_prob` to multiply by, because value iteration is *not* policy-weighted.
- `action_value = 0.0` — accumulator for one Bellman backup $\sum_{s', r} p(s', r \mid s, a)[r + \gamma V_k(s')]$.

**TODO 1: `value_iteration_backup`.** The block has to compute that inner sum for the current action. It is the same machinery as policy evaluation but without the $\pi(a \mid s)$ factor:

```python
for transition_prob, next_state, reward, done in env.unwrapped.P[state][action]:
    action_value += transition_prob * (reward + gamma * V[next_state])
```

Read this against the optimality equation: `transition_prob` is $p(s', r \mid s, a)$, `reward + gamma * V[next_state]` is $r + \gamma V_k(s')$. Multiplying and accumulating produces $\sum_{s', r} p(s', r \mid s, a)[r + \gamma V_k(s')]$ — one of the four numbers we need.

**TODO 2: `value_iteration_best_action`.** After the action loop, `action_values` is a list of $|\mathcal{A}|$ numbers — one per action. The Bellman *optimality* update takes the *max* of these:

```python
V[state] = max(action_values)
```

That is the whole difference between value iteration and policy evaluation. Where policy evaluation accumulated a policy-weighted average, value iteration takes a hard max. Everything else — the outer loop, the convergence check, the inner accumulation — is identical.

### A note on `action_values.append`

The starter computes all $|\mathcal{A}|$ action values first and *then* takes the max, instead of running a streaming `max` inside the action loop. Both work. Storing the list is convenient because the next lesson (`dp_policy_improvement`) takes the same list and uses `argmax` instead of `max` — keeping the structure consistent across lessons.

### A note on terminal states

When the loop reaches state $s = 15$ (the goal, terminal) or any of the holes, `env.unwrapped.P[s][a]` returns a self-loop with reward $0$ and `done=True`. The action backup degenerates to $\sum_{s'} 1 \cdot (0 + \gamma \cdot V_k(s)) = \gamma V_k(s)$, which for $V_0 = 0$ stays at $0$ forever. The max also stays at $0$. So terminal cells are effectively fixed at $0$ throughout — a happy accident of the FrozenLake encoding.

## Common pitfalls and misconceptions

**Pitfall 1: "Value iteration averages over a fixed policy."**
It does not. There is no policy in the update — only a $\max$. Confusing the value-iteration update with the policy-evaluation update is the most common error in this lesson, and it produces a value function that is much smaller than $v_*$ (because averaging is bounded above by the max). The spec calls this out explicitly as the misconception to prevent.

**Pitfall 2: "Value iteration is always faster than policy iteration."**
Sometimes, sometimes not. Policy iteration often converges in a startlingly small number of outer iterations — for the Jack's Car Rental problem in S&B p. 80, it converges in $5$. Value iteration takes more sweeps but each sweep is cheaper (no inner evaluation loop). The practical winner is usually *truncated policy iteration*, which is somewhere in between.

**Pitfall 3: "Once $V$ converges, you can drop the policy step."**
You can't *act* without a policy. $V$ tells you how good each state is, but to take an action you need a mapping from states to actions. After convergence, do one final greedy pass: $\pi_*(s) = \arg\max_a \sum_{s', r} p(s', r \mid s, a)[r + \gamma V(s')]$.

**Pitfall 4: "The greedy policy stops changing exactly when $V$ converges."**
The greedy policy with respect to $V_k$ can stop changing *before* $V_k$ itself fully converges. S&B Figure 4.1 makes this point: in the small gridworld example the greedy policy is already optimal after $k = 3$, but $V_k$ keeps moving for many more iterations. In practice some implementations terminate as soon as the greedy policy stops changing, even if $V$ is still drifting.

**Pitfall 5: "Sweeps must be synchronous."**
Asynchronous DP (S&B §4.5) — updating one state at a time in any order — converges as long as every state is updated infinitely often. The starter code uses Gauss–Seidel-style in-place updates, which is a form of asynchronous DP and is usually faster than the strict Jacobi-style two-array version.

## Connection to the bigger picture

**Forward links.**
- `dp_policy_improvement`: uses the same inner machinery (compute $|\mathcal{A}|$ action backups per state) but stores the `argmax` action instead of the `max` value. Combined with policy evaluation, this gives policy iteration.
- `td_q_learning`: Q-learning is *sample-based* value iteration on the action-value function. The $\max_a Q(s', a)$ in the Q-learning target is the sampling analogue of the $\max_a$ here.
- `td_sarsa`: the on-policy cousin that uses $Q(s', a')$ (the actually sampled next action) instead of $\max_a Q(s', a)$. Value iteration is to Q-learning as policy evaluation is to SARSA — keep that mental table.

**Backward links.** `dp_policy_eval` (same inner structure, different reduction). `mdp_foundations` (defines the Bellman optimality equation we are now iterating). `transition_prob` (the $p(s', r \mid s, a)$ table we sum over).

In Sutton & Barto, this lesson is Chapter 4, Section 4.4 (pp. 82–84), eq. 4.10. The relation to truncated policy iteration is discussed on p. 83, last paragraph. Figure 4.1 (the small gridworld example) is essential viewing for the "greedy policy converges before $V$" point.

## Key takeaways

- Value iteration iterates the Bellman *optimality* equation: replace policy-weighted averaging with a $\max$ over actions.
- The fixed point of the iteration is $v_*$, the *optimal* value function — no separate improvement step required during iteration.
- A final greedy pass extracts $\pi_*$ from $V \approx v_*$.
- The code structure is identical to policy evaluation except for two changes: drop the $\pi(a \mid s)$ factor inside the inner loop, and take `max(action_values)` instead of a sum at the end.
- Value iteration replaces the policy-weighted expectation with the best one-step backup.

## Further reading

- Sutton, R. S. and Barto, A. G. (2018). *Reinforcement Learning: An Introduction*, 2nd ed. — Chapter 4, Section 4.4, eq. 4.10 (p. 83). Algorithm box on p. 83; truncated policy iteration discussion on p. 83 last paragraph; Figure 4.1 (p. 77) for the small gridworld convergence picture. [http://incompleteideas.net/book/the-book-2nd.html](http://incompleteideas.net/book/the-book-2nd.html)
- Gymnasium FrozenLake-v1 documentation: [https://gymnasium.farama.org/v0.26.3/environments/toy_text/frozen_lake/](https://gymnasium.farama.org/v0.26.3/environments/toy_text/frozen_lake/)
- David Silver's UCL course, Lecture 3 slides on value iteration: [https://www.davidsilver.uk/teaching/](https://www.davidsilver.uk/teaching/)
- OpenAI Spinning Up — Intro to RL Part 2 (model-based vs. model-free taxonomy): [https://spinningup.openai.com/en/latest/spinningup/rl_intro2.html](https://spinningup.openai.com/en/latest/spinningup/rl_intro2.html)
