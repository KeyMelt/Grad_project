# Policy Evaluation

## Why this concept matters

We finally have an equation that *equals* the value function — the Bellman expectation equation from the MDP foundations lesson — but an equation is not yet an algorithm. Solving $v_\pi$ as a system of linear equations is theoretically possible for tabular MDPs, but it scales as $|\mathcal{S}|^3$ and breaks the moment we leave the tabular world. Policy evaluation is the *iterative* alternative: treat the Bellman equality as an *assignment*, sweep over every state, repeat. The values stop changing when you have found $v_\pi$.

The promise is bigger than just "compute $v_\pi$." Policy evaluation is the first half of **policy iteration**, the algorithm that — combined with policy improvement, the very next lesson — produces optimal policies. It is also the first lesson where you actually *write code*. Every later DP, MC, and TD lesson follows the same code shape: outer convergence loop, inner sweep over states, inner-inner sum over (action, transition) tuples. Get this scaffolding right once and the rest of the course is variations on a theme.

The environment is again FrozenLake-v1 with `is_slippery=True`, and the policy we evaluate is the *uniform-random* one: $\pi(a \mid s) = 1/4$ for every state and action. The discount factor is $\gamma = 0.95$ (the default `DISCOUNT_FACTOR` in the starter code). Under this policy the elf wanders the lake aimlessly, occasionally stumbling onto the goal — so non-terminal cells get small positive values and the heatmap glows faintly. The optimal value function would be much brighter, but that comes in the next two lessons.

![FrozenLake-v1: policy evaluation builds a value heatmap by spreading reward backward from the goal (G) one sweep at a time. Bright tiles = high expected return.](https://gymnasium.farama.org/_images/frozen_lake.gif)

## Intuition first

Picture the FrozenLake grid with all 16 cells initialised to $v_0(s) = 0$. The terminal cells (holes $\{5, 7, 11, 12\}$ and goal $15$) are *fixed* at $0$ — they will never be touched by the algorithm. The other 11 cells will be updated repeatedly.

The video walks you through the very first non-trivial update: state $14$. This is the cell directly to the left of the goal. Under the uniform-random policy, action RIGHT from state $14$ has probability $1/4$ to be chosen. The slippery outcomes for $(s=14, a=\text{RIGHT})$ are $\{13, 15, 10\}$ with probability $1/3$ each. One of those — $s' = 15$ — pays a reward of $1$. So even though every other transition pays $0$, this one branch contributes a positive number to $v_{k+1}(14)$.

Specifically (with $\gamma = 0.95$, $v_0 = 0$ everywhere):

$$
v_1(14) \;=\; \tfrac{1}{4} \cdot \bigl[\tfrac{1}{3} \cdot (0 + 0.95 \cdot 0) + \tfrac{1}{3} \cdot (1 + 0.95 \cdot 0) + \tfrac{1}{3} \cdot (0 + 0.95 \cdot 0)\bigr] \;+\; (\text{contributions from LEFT, DOWN, UP, all zero this iteration})
$$

$$
\;=\; \tfrac{1}{4} \cdot \tfrac{1}{3} \cdot 1 \;=\; \tfrac{1}{12} \;\approx\; 0.0833.
$$

Just one cell lights up — but on the next sweep, *neighbours* of state $14$ start to feel that $0.0833$ through their own backups. By sweep $k = 2$, states $10$ and $13$ are non-zero too. By $k = 71$, every reachable non-terminal cell has stabilised, and the algorithm halts.

That is the whole game: **value trickles backward from the goal, one ring of neighbours per sweep**. The trick of policy evaluation is that the trickle is *deterministic* once $\pi$ is fixed — there is no exploration, no sampling, just enumeration over the transition tuples in `env.unwrapped.P`.

The video shows five snapshots of the value heatmap: $V_0$ (all zero), $V_1$ (just state $14$ lit), $V_2$, $V_5$, $V_{10}$, $V_{71}$ (converged). Watching the warm-coloured front spread outward from the goal is the canonical mental image for DP.

## The math

### The Bellman expectation, rewritten as an update

The Bellman expectation equation for a fixed policy $\pi$ is:

$$
v_\pi(s) \;=\; \sum_{a} \pi(a \mid s) \sum_{s', r} p(s', r \mid s, a)\,[r + \gamma v_\pi(s')].
$$

This is an *equality*. The trick of iterative policy evaluation is to treat it as an *assignment* and iterate. Define a sequence of value tables $v_0, v_1, v_2, \ldots$ by

$$
\boxed{\;v_{k+1}(s) \;\doteq\; \sum_{a} \pi(a \mid s) \sum_{s', r} p(s', r \mid s, a)\,[r + \gamma v_k(s')].\;}
$$

The sequence $\{v_k\}$ converges to $v_\pi$ as $k \to \infty$ — guaranteed if either $\gamma < 1$ or the policy terminates with probability $1$ from every state.

In practice we cannot iterate forever, so we stop when the largest change across the sweep is below a small threshold $\theta$:

$$
\Delta_k \;=\; \max_{s \in \mathcal{S}} |v_{k+1}(s) - v_k(s)| \;<\; \theta.
$$

The starter code uses $\theta = 10^{-8}$, which is well past what you need for the heatmap to look stable.

### Symbol glossary

| Symbol | Meaning |
| ------------------ | --------------------------------------------------------------------------------------------- |
| $v_k(s)$ | Value table at iteration $k$ — one number per non-terminal state, terminal states fixed at 0 |
| $\pi(a \mid s)$ | Policy weights (uniform random: $1/4$ for every $(s, a)$) |
| $p(s', r \mid s, a)$ | Environment dynamics from `env.unwrapped.P[s][a]` |
| $\gamma$ | Discount factor (lesson default: $0.95$) |
| $\theta$ | Convergence threshold (lesson default: $10^{-8}$) |
| $\Delta_k$ | Maximum value change over a sweep — used to detect convergence |

### Worked numeric example

Take the very first sweep starting from $v_0(s) = 0$ for every $s$. We compute $v_1$ for each non-terminal state.

For any state $s$ whose four actions all lead to states with $v_0 = 0$ *and* all reward zero, $v_1(s) = 0$. That covers most cells.

The non-trivial updates happen at states whose transition tuples include the goal at $s' = 15$, where reward $= 1$. Those states are the goal's immediate neighbours: $11$ (a hole — but holes are terminal and never updated), $13$, $14$. Of these only $13$ and $14$ are non-terminal. Let us trace state $14$ carefully.

`env.unwrapped.P[14]` returns, for each action $a$:

| Action $a$ | Slippery successors $(s', r, done)$ each w.p. $1/3$ |
| ------------ | --------------------------------------------------- |
| $0$ = LEFT | $\{(10, 0, F), (13, 0, F), (14, 0, F)\}$ |
| $1$ = DOWN | $\{(13, 0, F), (14, 0, F), (15, 1, T)\}$ |
| $2$ = RIGHT | $\{(14, 0, F), (15, 1, T), (10, 0, F)\}$ |
| $3$ = UP | $\{(10, 0, F), (15, 1, T), (13, 0, F)\}$ |

(Note: slippery transitions from $14$ stay within $\{10, 13, 14, 15\}$; the algorithm does not need to know this — it just enumerates `P`.) Three of the four actions have one branch hitting the goal. Plugging into the Bellman update with $v_0 \equiv 0$:

$$
v_1(14) \;=\; \tfrac{1}{4} \cdot 0 \;+\; \tfrac{1}{4} \cdot \tfrac{1}{3} \;+\; \tfrac{1}{4} \cdot \tfrac{1}{3} \;+\; \tfrac{1}{4} \cdot \tfrac{1}{3} \;=\; \tfrac{1}{4}.
$$

So $v_1(14) = 0.25$. State $13$, by analogous reasoning, gets $v_1(13) = \tfrac{1}{4} \cdot \tfrac{1}{3} = \tfrac{1}{12} \approx 0.0833$ (only one of its action branches reaches the goal). Every other non-terminal state has $v_1 = 0$.

The next sweep ($v_2$) then sees those positive values at $13$ and $14$ as backups into states $9, 10, 12, 14$... and the warm front begins to spread.

(The exact $V_1$ in the video uses an explicit $\Delta = 0.25$ readout — which matches our $v_1(14) = 0.25$ above.)

## How the code does it

Here is the starter code from `backend/lessons.py`, verbatim:

```python
DISCOUNT_FACTOR = 0.95

def policy_evaluation(V, policy, env, gamma=DISCOUNT_FACTOR, theta=1e-8):
 delta = float("inf")
 while delta > theta:
 delta = 0.0
 for state in range(len(V)):
 old_value = V[state]
 new_value = 0.0
 for action, action_prob in enumerate(policy[state]):
 # TODO(student): combine model branches into the expectation for this action.
 raise NotImplementedError("TODO: policy_eval_expectation")
 V[state] = new_value
 delta = max(delta, abs(old_value - __BLANK_policy_eval_delta__))
 return V
```

The skeleton is the Bellman update with two missing pieces. Let us map every line onto the equation $v_{k+1}(s) = \sum_a \pi(a \mid s) \sum_{s', r} p(s', r \mid s, a)[r + \gamma v_k(s')]$:

- `while delta > theta:` is the outer convergence loop. Each iteration of the while loop is one sweep — one increment of $k$ in $v_k \to v_{k+1}$.
- `for state in range(len(V)):` enumerates every $s \in \mathcal{S}$. Note that terminal states are included in the iteration — that is fine, because their entries in `V` are initialised to $0$ and the update happens to also produce $0$ (no transitions are defined out of true terminal states, or they self-loop with $0$ reward).
- `old_value = V[state]` snapshots $v_k(s)$ before we overwrite it. We need this for the convergence check.
- `new_value = 0.0` initialises the accumulator for $v_{k+1}(s)$ — this is the "running sum" of the double sum on the right-hand side.
- `for action, action_prob in enumerate(policy[state]):` loops over $a$. `action_prob` is $\pi(a \mid s)$ — for the uniform-random policy, it equals $0.25$ for every action.

**TODO 1: `policy_eval_expectation`.** The inner block has to accumulate one term of the outer sum: $\pi(a \mid s) \sum_{s', r} p(s', r \mid s, a)[r + \gamma v_k(s')]$. That requires *another* inner loop over the transition tuples:

```python
# Inside the for-action loop, conceptually:
for transition_prob, next_state, reward, done in env.unwrapped.P[state][action]:
 new_value += action_prob * transition_prob * (reward + gamma * V[next_state])
```

Read the multiplication left-to-right and you can see all three sums collapsing into one accumulator: `action_prob` is $\pi(a \mid s)$, `transition_prob` is $p(s', r \mid s, a)$, and `reward + gamma * V[next_state]` is $r + \gamma v_k(s')$. The TODO is just this loop. (A subtle point: `V[next_state]` here is read from the *same* array we are writing to — that is the in-place / Gauss–Seidel variant, which converges to the same answer but typically faster than the strict two-array form. endorses this.)

**TODO 2: `policy_eval_delta`.** The convergence check should compare the *new* value of $V[state]$ against the *old* one we snapshotted. After `V[state] = new_value` has run, the relevant expression is just `V[state]` (which now equals `new_value`). So the blank should be:

```python
delta = max(delta, abs(old_value - V[state]))
```

That keeps $\Delta_k$ as the maximum absolute change across the sweep.

Why these blanks? The two TODOs separate the two distinct ideas in policy evaluation:
1. **What does one Bellman backup compute?** (TODO 1 — the expectation.)
2. **When do we stop?** (TODO 2 — the convergence delta.)

The starter intentionally exposes both so you cannot fake one without understanding the other.

### A note on terminal states

The `done` flag in the transition tuple flags terminal transitions. For policy evaluation specifically, terminal states have $V[\text{terminal}] = 0$ from initialisation and never get rewritten (because no transitions out of terminal cells produce non-zero contributions). You do not need an explicit `if done` guard in policy evaluation. It will matter more in MC and TD lessons, where the bootstrap convention is explicit.

## Common pitfalls and misconceptions

**Pitfall 1: "Policy evaluation finds the *best* policy."**
It does not. It computes $v_\pi$ for *whatever* policy you hand it. Hand it a stupid policy (e.g., "always LEFT") and you get a stupid value function — the heatmap will be uniformly zero, because the agent never reaches the goal. Hand it the optimal policy and you get $v_*$. The whole job of `dp_policy_improvement` (next lesson) is to *change* the policy after each evaluation pass.

**Pitfall 2: "You have to wait for $\Delta = 0$."**
You stop at $\Delta < \theta$ for some small $\theta$. Exact convergence is asymptotic and you would wait forever. The threshold $\theta$ trades accuracy for compute. The starter's $\theta = 10^{-8}$ is much tighter than you need for visual purposes — for the heatmap to look stable, $\theta = 10^{-3}$ would suffice. We use the small number to be safe.

**Pitfall 3: "In-place updates give the wrong answer."**
Both in-place (Gauss–Seidel) and two-array (Jacobi) updates converge to the same $v_\pi$. In-place is usually faster because later states in a sweep benefit from earlier states' updates. The starter code is *in-place* — it writes back to `V[state]` immediately. This is correct and standard.

**Pitfall 4: "Policy evaluation needs `env.step()`."**
It does not. Policy evaluation is *pure planning* — it reads `env.unwrapped.P` and never calls `env.step()` or `env.reset()`. That distinction is what makes it a *model-based* method. Confusing "model-based" with "uses neural networks" is rampant; here it means precisely "uses the four-argument $p$ function."

**Pitfall 5 (the misconception called out in the spec): "Policy evaluation updates the policy too."**
Policy evaluation updates *only the value table*. The policy $\pi$ is read-only inside the function — that is why `policy` is a parameter, not a return value. Updating the policy is a separate step (`dp_policy_improvement`), and combining the two is what produces `policy iteration`.

## Connection to the bigger picture

**Forward links.**
- `dp_policy_improvement`: takes the $v_\pi$ we just computed and produces a *better* policy $\pi'$. Alternating evaluation and improvement gives policy iteration, which converges to $\pi_*$.
- `dp_value_iteration`: fuses one sweep of evaluation with one sweep of improvement by replacing $\sum_a \pi(a \mid s)$ with $\max_a$ inside the backup. Faster per sweep, more sweeps in total.
- `mc_first_visit`, `td_sarsa`, `td_q_learning`: drop the model-based double sum and replace it with sampled transitions. Same goal (estimate value or action-value functions), different machinery.

**Backward links.** `mdp_foundations` (defines the Bellman expectation equation we are now using as an update). `transition_prob` (the $p(s', r \mid s, a)$ table we sum over). `rl_intro` (the agent–environment loop the equation formalises).


## Key takeaways

- Iterative policy evaluation turns the Bellman expectation equality into an assignment and iterates it to a fixed point.
- The update $v_{k+1}(s) = \sum_a \pi(a \mid s) \sum_{s', r} p(s', r \mid s, a)[r + \gamma v_k(s')]$ is a pure sum — no exploration, no sampling.
- Value trickles backward from rewarding cells one sweep at a time; for FrozenLake at $\gamma = 0.95$ under the uniform-random policy, convergence takes on the order of $70$ sweeps.
- The policy is fixed throughout; only the value table changes. To make the policy better, use the *next* lesson.
- Policy evaluation repeatedly recomputes each state from all modeled outcomes under the current policy.

## Further reading

- Sutton, R. S. and Barto, A. G. (2018). *Reinforcement Learning: An Introduction*, 2nd ed. — Chapter 4, Section 4.1, eq. 4.5 (p. 75). The algorithm box on p. 75 is the canonical pseudocode this lesson mirrors. [http://incompleteideas.net/book/the-book-2nd.html](http://incompleteideas.net/book/the-book-2nd.html)
- Gymnasium FrozenLake-v1 documentation: [https://gymnasium.farama.org/v0.26.3/environments/toy_text/frozen_lake/](https://gymnasium.farama.org/v0.26.3/environments/toy_text/frozen_lake/)
- David Silver's UCL course, Lecture 3 (Planning by Dynamic Programming): [https://www.davidsilver.uk/teaching/](https://www.davidsilver.uk/teaching/)
- Szepesvári, C. (2010). *Algorithms for Reinforcement Learning.* §3.1 (free PDF): [https://sites.ualberta.ca/~szepesva/rlbook.html](https://sites.ualberta.ca/~szepesva/rlbook.html)
