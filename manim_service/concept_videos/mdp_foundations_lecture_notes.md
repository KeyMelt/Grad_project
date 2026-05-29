# MDP Foundations: From States to the Bellman Equation

## Why this concept matters

Last time the elf wandered a frozen lake with no labels and only a sparse reward. We could see something *had* to be learned, but we had no language to describe what. This lesson supplies that language. Every later algorithm in the course — policy evaluation, value iteration, SARSA, Q-learning — is a different way of solving (or sampling from) a single equation we are about to derive: the **Bellman expectation equation**. By the end of this lesson, that equation will not appear as an oracle pronouncement. It will *fall out* of the agent–environment loop one symbol at a time.

The Markov decision process (MDP) is the mathematical formalism that lets us write down "an agent acting in an environment" precisely. It has only three primitive pieces — states, actions, and a transition function — plus a discount factor that says how much we care about future rewards. Everything else (policies, returns, value functions) is *derived* from these primitives. Pin the primitives down and the whole edifice follows.

We stay inside FrozenLake-v1 (4×4, `is_slippery=True`) for the entire lesson, which keeps every abstract symbol grounded in a tile you can point at. State indices $0$–$15$ label the cells in row-major order; holes sit at $\{5, 7, 11, 12\}$; the goal is $15$. The slippery dynamics give every action three equally likely outcomes — the *perpendicular* directions to the intended one, each with probability $1/3$. That stochasticity is the whole reason we need an *expectation* in the Bellman equation rather than a single deterministic update.

## Intuition first

The video builds the MDP in six small segments, all on the same accreting grid. We will walk them in the same order so the notes match the video frame-for-frame.

**(a) States and the Markov property.** Label the 16 tiles with integers $0$–$15$. The Markov property says: *the future depends only on the present state, not on how the agent got there*. If two trajectories arrive at state $6$ via different routes, both face the same probabilistic future. This is what makes tabular RL possible — we can attach a single number to each state instead of conditioning on entire histories.

**(b) Returns and the discount $\gamma$.** A trajectory produces a stream of rewards $R_1, R_2, R_3, \ldots$. The agent's job is not to maximise the next reward — it is to maximise the discounted *total*. With $\gamma = 0.99$ and a trajectory that pays $[0, 0, 1]$ over three steps, the return from time $t = 0$ is

$$
G_0 = 0 + 0.99 \cdot 0 + 0.99^2 \cdot 1 = 0.9801.
$$

That $0.9801$ is shown in the video as a single yellow number that the camera lingers on. It is worth remembering: a reward that arrives two steps away is *worth* $0.9801$ today.

**(c) Transition probabilities at state $6$, action RIGHT.** Stand on tile $6$ (row 1, column 2) and pick RIGHT. Because the ice is slippery, three outcomes can happen with probability $1/3$ each:

- Land on state $7$ (the intended right) — a hole.
- Land on state $2$ (one cell up).
- Land on state $10$ (one cell down).

Probabilities sum to $1$. The probabilities are *not* the agent's choice — they are the environment's response.

**(d) Policy.** A *policy* $\pi$ is the agent's strategy. A *deterministic* policy puts one arrow on each cell. The **uniform-random** policy — the one we will evaluate later in `dp_policy_eval` — puts four arrows on each cell, each with weight $1/4$. Two sources of randomness now coexist on the grid: the policy's choice of action and the environment's slippery response.

**(e) Value function.** Once policy and environment are pinned down, every state has a single number: $v_\pi(s)$, the *expected return starting from $s$ and following $\pi$ forever after*. We draw a heatmap: terminal cells ($\{5, 7, 11, 12, 15\}$) are exactly $0$ by definition. Non-terminal cells get warm-coloured numbers — small near the holes, larger near the goal — under whatever non-optimal $\pi$ we are evaluating.

**(f) The Bellman expectation equation.** This is the punchline. The video assembles, term by term, the recursion

> *"the value of $s$ equals the average — over actions you might take and outcomes the environment might produce — of (immediate reward) + (discount × value of the next state)."*

That sentence is the equation in English. The next subsection writes it in symbols.

## The math

We will build the Bellman expectation equation in four moves. None of them are pulled out of a hat — each follows from the previous step.

### Move 1 — The dynamics function

The environment is fully specified by

$$
p(s', r \mid s, a) \;\doteq\; \Pr\{S_{t+1} = s',\; R_{t+1} = r \mid S_t = s,\; A_t = a\}.
$$

This is Sutton & Barto's equation 3.2 (p. 48). For FrozenLake state $6$, action RIGHT (Gymnasium's action index $2$), the Technical Validator confirmed via live `env.unwrapped.P[6][2]`:

$$
p(s', r=0 \mid s=6, a=\text{RIGHT}) = \tfrac{1}{3} \text{ for } s' \in \{2, 7, 10\}, \quad \text{else } 0.
$$

Notice that $\sum_{s'}\sum_{r} p(s', r \mid s, a) = 1$ — this is the *normalisation constraint*, and it is what makes $p$ a probability distribution rather than a generic non-negative function.

### Move 2 — Returns and the recursion

The return from time $t$ is the discounted sum of all future rewards:

$$
G_t \;\doteq\; R_{t+1} + \gamma R_{t+2} + \gamma^2 R_{t+3} + \cdots \;=\; \sum_{k=0}^{\infty} \gamma^k R_{t+k+1}.
$$

This is S&B eq. 3.8 (p. 54). Pull out the first term and notice that what remains is itself a return, just shifted by one step:

$$
\boxed{\;G_t \;=\; R_{t+1} + \gamma\, G_{t+1}\;}
$$

This is S&B eq. 3.9 (p. 55) — the **return recursion**. It is the single most important equation in this lesson, because every Bellman-style equation in the course is what you get when you take the expectation of this recursion under various conditions.

### Move 3 — Value function

For a fixed policy $\pi$, define

$$
v_\pi(s) \;\doteq\; \mathbb{E}_\pi[G_t \mid S_t = s].
$$

This is S&B eq. 3.12 (p. 58). Read aloud: *the value of state $s$ under policy $\pi$ is the expected return when we start in $s$ and follow $\pi$ forever after*.

The subscript $\pi$ on the expectation matters: it means the actions $A_t, A_{t+1}, \ldots$ are *drawn from* $\pi$. The randomness inside the expectation comes from two sources: the policy's action distribution $\pi(a \mid s)$ and the environment's response distribution $p(s', r \mid s, a)$.

### Move 4 — Bellman expectation equation

Substitute the return recursion (Move 2) into the value definition (Move 3) and unfold the expectation over the two sources of randomness:

$$
\boxed{\;v_\pi(s) \;=\; \sum_{a} \pi(a \mid s) \sum_{s', r} p(s', r \mid s, a)\,\bigl[\,r + \gamma\, v_\pi(s')\,\bigr]\;}
$$

This is S&B eq. 3.14 (p. 59) — the **Bellman expectation equation**. It is an *equality*, not an *update rule*. Every algorithm in the course will exploit it differently:

- Treat it as an assignment to compute (`dp_policy_eval`).
- Replace $\sum_a \pi(a\mid s)$ with $\max_a$ to get optimality (`dp_value_iteration`).
- Drop the sum and sample instead (`mc_first_visit`, `td_sarsa`, `td_q_learning`).

### Symbol glossary

| Symbol                  | Meaning                                                                         |
| ----------------------- | ------------------------------------------------------------------------------- |
| $\mathcal{S}$           | Set of states (here, $\{0, 1, \ldots, 15\}$)                                    |
| $\mathcal{A}(s)$        | Actions available in $s$ (here, $\{\text{LEFT}, \text{DOWN}, \text{RIGHT}, \text{UP}\}$) |
| $\pi(a \mid s)$         | Policy — probability of taking $a$ in $s$                                       |
| $p(s', r \mid s, a)$    | Environment dynamics — probability of $(s', r)$ given $(s, a)$                  |
| $R_{t+1}$               | Reward received *after* action $A_t$                                            |
| $G_t$                   | Discounted return from time $t$                                                 |
| $\gamma \in [0, 1]$     | Discount factor                                                                 |
| $v_\pi(s)$              | State-value function under $\pi$                                                |
| $q_\pi(s, a)$           | Action-value function under $\pi$ (introduced in next lessons)                  |

### Worked numeric example

Take FrozenLake state $6$, action RIGHT, under the uniform-random policy $\pi(a \mid s) = 1/4$ for all four actions. Suppose at iteration $k$ the current value table $v_k$ assigns $v_k(s) = 0$ for every cell except the goal-adjacent state $14$, where $v_k(14) = 0.5$, and the goal state $15$ where $v_k(15) = 0$ (terminal). Take $\gamma = 0.99$.

The RIGHT branch contribution to $v_{k+1}(6)$ is, by the Bellman expectation:

$$
\pi(\text{RIGHT}\mid 6) \sum_{(s',r)} p(s',r\mid 6, \text{RIGHT})\,[r + \gamma v_k(s')]
$$

$$
= \tfrac{1}{4} \bigl[\tfrac{1}{3}(0 + 0.99 \cdot 0) + \tfrac{1}{3}(0 + 0.99 \cdot 0) + \tfrac{1}{3}(0 + 0.99 \cdot 0)\bigr] \;=\; 0.
$$

All three RIGHT outcomes land on states $\{2, 7, 10\}$, none of which have non-zero value yet, so this iteration's RIGHT contribution is zero. To get a non-zero contribution, the value would have to propagate up from state $15$ through state $14$ and onwards — which is *exactly* what iterative policy evaluation does. The first few sweeps trickle value backward from the goal one cell at a time, which is why $v_\pi$ takes ~71 sweeps to converge on FrozenLake at $\gamma = 0.99$ (as shown in the iteration counter in the next video).

## How the code does it

There is no starter exercise for this lesson — it is conceptual. But the spec pins down the exact four lines of code you should be able to read fluently before moving on. They are the code-side of every symbol we just derived.

```python
import gymnasium as gym
import numpy as np

env = gym.make("FrozenLake-v1", is_slippery=True)

# Inspect the environment's dynamics function p(s', r | s, a).
# For state 6, action RIGHT (index 2):
for prob, next_state, reward, done in env.unwrapped.P[6][2]:
    print(prob, next_state, reward, done)

# Construct the uniform-random policy π(a|s) = 1/|A| for all (s, a).
policy = np.ones((env.observation_space.n, env.action_space.n)) / env.action_space.n
```

Tie each line back to the equation:

- **`env.unwrapped.P[6][2]`** is exactly $p(s', r \mid s=6, a=\text{RIGHT})$ — stored as a list of $(prob, s', r, done)$ tuples. Running the loop prints three lines, one per outcome, each with `prob = 0.333…`. The `done=True` line corresponds to $s' = 7$, the hole. The `.unwrapped` accessor bypasses Gymnasium's `OrderEnforcing` and `TimeLimit` wrappers, which would otherwise hide `P`.
- **`policy`** is a NumPy array of shape `(16, 4)` storing $\pi(a \mid s)$ for every (state, action) pair. The uniform-random policy is the simplest non-trivial $\pi$ and the one all later DP lessons will evaluate. Each row sums to $1$.
- The action *index* convention is fixed by Gymnasium: $0 = \text{LEFT}$, $1 = \text{DOWN}$, $2 = \text{RIGHT}$, $3 = \text{UP}$. Remember this — it bites when you debug action arrays without labels.

This snippet contains no TODOs because the lesson ships no exercise. But every later starter file assumes you can read these four lines without thinking about them. If you cannot yet, run them and inspect the printed tuples until you can.

## Common pitfalls and misconceptions

**Pitfall 1: "Transition probability is the agent's action choice."**
$p(s', r \mid s, a)$ is the *environment's* response *given* that action $a$ was taken. It says nothing about *whether* the agent chose $a$ — that is $\pi(a \mid s)$. Mixing them is the single most common conceptual error in MDPs. The Bellman expectation equation makes the separation explicit by writing them as two distinct factors inside the double sum.

**Pitfall 2: "$v_\pi$ is only defined for the optimal policy."**
$v_\pi$ is defined for *any* policy. The notation $v_\pi$ is read "value under $\pi$" — feed it a stupid policy and you get a stupid value function; feed it the uniform-random policy and you get the equiprobable-policy value function. Only $v_*$ (with subscript star) is reserved for the optimal value function.

**Pitfall 3: "The slippery outcomes are $\{7, 2, 5\}$."**
This was an error in an earlier reference scene that the Technical Validator caught. The correct successors for state $6$, action RIGHT (slippery) are $\{2, 7, 10\}$ — the intended direction RIGHT plus the two *perpendicular* directions UP and DOWN, each with probability $1/3$. State $5$ is reachable from state $6$ by action LEFT, not RIGHT. Always confirm transitions against `env.unwrapped.P` before trusting them.

**Pitfall 4: "$\gamma$ is a hyperparameter — it doesn't matter much."**
$\gamma$ controls how far into the future the agent cares. At $\gamma = 0$ the agent is myopic and only optimises the next reward (useless on a sparse-reward task like FrozenLake). At $\gamma = 1$ on an undiscounted infinite-horizon task the return can diverge. The course uses $\gamma = 0.95$ or $\gamma = 0.99$ in the DP lessons. The choice changes *both* the value function and the optimal policy.

## Connection to the bigger picture

This lesson is the formal core of the course. Everything downstream is an algorithm for either *computing* the Bellman expectation equation (DP methods) or *sampling* from it (MC and TD methods).

**Forward links.**
- `transition_prob` zooms in on $p(s', r \mid s, a)$ as a standalone object — the same state $6$, action RIGHT example, expanded into a full lesson.
- `dp_policy_eval` treats the Bellman expectation equation as an assignment and iterates it to a fixed point.
- `dp_value_iteration` replaces the $\sum_a \pi(a \mid s)$ with a $\max_a$ to get the **Bellman optimality equation**.
- `dp_policy_improvement` uses the same one-step lookahead, but instead of updating values, it updates the policy.
- `mc_first_visit`, `td_sarsa`, `td_q_learning` all drop the $\sum$ over $(s', r)$ and replace it with a single sampled transition — the model-free turn.

**Backward links.** The agent–environment loop from `rl_intro`. Basic probability (random variables, expectations, conditional distributions).

In Sutton & Barto, this lesson covers Chapter 3 sections 3.1–3.5 (pp. 47–62): the agent–environment interface, dynamics function (eq. 3.2), return (eqs. 3.8, 3.9), value function (eq. 3.12), and Bellman expectation (eq. 3.14).

## Key takeaways

- A finite MDP is fully specified by states $\mathcal{S}$, actions $\mathcal{A}$, and the four-argument dynamics $p(s', r \mid s, a)$.
- A policy $\pi$ plus a discount $\gamma$ turns the reward stream into a single scalar return $G_t$.
- The value function $v_\pi(s)$ measures the expected return under $\pi$ from state $s$ — and is defined for *any* $\pi$.
- The Bellman expectation equation $v_\pi(s) = \sum_a \pi(a \mid s) \sum_{s', r} p(s', r \mid s, a)[r + \gamma v_\pi(s')]$ expresses each state's value recursively in terms of its successors — the exact equality the next video turns into an algorithm.
- A finite MDP is (states, actions, p); a policy plus a discount turns rewards into returns; value functions measure those returns under any policy; and the Bellman expectation equation expresses each state's value recursively from its successors — the exact equality the next video turns into an algorithm.

## Further reading

- Sutton, R. S. and Barto, A. G. (2018). *Reinforcement Learning: An Introduction*, 2nd ed. — Chapter 3: dynamics $p$ (eq. 3.2, p. 48), return $G_t$ (eqs. 3.8–3.9, pp. 54–55), value function (eq. 3.12, p. 58), Bellman expectation (eq. 3.14, p. 59). [http://incompleteideas.net/book/the-book-2nd.html](http://incompleteideas.net/book/the-book-2nd.html)
- Gymnasium FrozenLake-v1 documentation: [https://gymnasium.farama.org/v0.26.3/environments/toy_text/frozen_lake/](https://gymnasium.farama.org/v0.26.3/environments/toy_text/frozen_lake/)
- David Silver's UCL course, Lecture 2 (Markov Decision Processes): [https://www.davidsilver.uk/teaching/](https://www.davidsilver.uk/teaching/)
- Puterman, M. L. (1994). *Markov Decision Processes: Discrete Stochastic Dynamic Programming.* Wiley — the canonical formal reference for MDPs.
