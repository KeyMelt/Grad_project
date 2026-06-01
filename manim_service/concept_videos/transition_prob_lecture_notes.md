# Transition Probabilities

## Why this concept matters

If the MDP lesson assembled the whole machine, this one zooms in on a single gear: the environment's response function. When the elf chooses RIGHT on a slippery tile and lands somewhere unexpected, *that* is what the transition probability function $p(s', r \mid s, a)$ describes. It is the complete, exhaustive specification of "given that the agent did $a$ in $s$, what does the world hand back?" — written as a probability distribution over (next state, reward) pairs.

Why split it out into its own lesson? Because every later algorithm in the course is haunted by this function. Dynamic programming methods (policy evaluation, value iteration, policy improvement) need to *know* $p$ exactly and sum over it explicitly. Model-free methods (Monte Carlo, SARSA, Q-learning) deliberately do *not* know $p$ — they replace the sum with a single sampled transition. In both cases, you have to be crystal-clear about what $p$ actually is before you can decide which family of algorithms applies.

The example we hammer on is FrozenLake-v1 state $6$, action RIGHT. State $6$ is row $1$, column $2$ — one tile north of the hole at state $7$, two tiles east of the start. The slippery dynamics give RIGHT three equally likely outcomes. By the end of this lesson you should be able to write out the full $p(s', r \mid 6, \text{RIGHT})$ table from memory, sum it to $1$, and explain why none of those three probabilities is $0$ or $1$.

![FrozenLake-v1: locate state 6 (row 1, col 2). Choosing RIGHT can land the agent on states 2 (skid up), 7 (intended — a hole), or 10 (skid down), each with probability 1/3.](https://gymnasium.farama.org/_images/frozen_lake.gif)

## Intuition first

Stand on tile $6$. You announce your action: RIGHT. Now close your eyes. The ice underneath you decides what happens. Three things might happen, all equally likely:

- **You actually go right** and land on state $7$. State $7$ is a hole. Reward: $0$. Episode ends.
- **You skid up** and land on state $2$ (the cell above where you started). Reward: $0$. You keep going.
- **You skid down** and land on state $10$ (the cell below). Reward: $0$. You keep going.

That is the whole story. Three outcomes, probability $1/3$ each, summing to $1$. None of them is the agent's fault — the agent's choice was RIGHT. The randomness lives in the environment.

The video presents this as three small arrows lighting up *inside the FrozenLake grid itself*, not as an abstract fork diagram in empty space. The point is to keep the geometry concrete: every probability lives on a real tile you can see, not a node in a tree somewhere.

Two facts the video lingers on:

1. **Non-negativity.** $p(s', r \mid s, a) \geq 0$ always. There are no negative probabilities. (Negative *rewards* are fine — that is a different quantity.)
2. **Normalisation.** The probabilities sum to exactly $1$. $\sum_{s'} \sum_{r} p(s', r \mid s, a) = 1$. If you ever see a transition table that does not sum to $1$, either the environment is bugged or you forgot a successor state.

These two constraints turn $p$ from a generic non-negative function into a *probability distribution*. They are the only thing $p$ has to be.

## The math

### Definition

The four-argument dynamics function is :

$$
p(s', r \mid s, a) \;\doteq\; \Pr\{S_{t+1} = s',\; R_{t+1} = r \mid S_t = s,\; A_t = a\}.
$$

Read aloud: "the probability that the next state is $s'$ and the reward is $r$, given that we are in state $s$ and took action $a$."

The two constraints we listed in the intuition section are exactly:

$$
\boxed{\;p(s', r \mid s, a) \geq 0, \qquad \sum_{s'} \sum_{r} p(s', r \mid s, a) = 1.\;}
$$

These are what *make* $p$ a probability distribution. Everything else — value functions, Bellman equations, policy improvement — is built on top.

### Useful derived quantities

Sometimes you only care about *where* the agent ends up, not what reward it got. Then marginalise over the reward:

$$
p(s' \mid s, a) \;=\; \sum_{r} p(s', r \mid s, a).
$$

Sometimes you want the expected immediate reward:

$$
r(s, a) \;\doteq\; \mathbb{E}[R_{t+1} \mid S_t = s, A_t = a] \;=\; \sum_{r} r \sum_{s'} p(s', r \mid s, a).
$$

For most toy environments — FrozenLake included — the reward for a given $(s, a, s')$ triple is deterministic, so the inner sum over $r$ collapses to a single term. The four-argument form is the canonical object anyway, because the general MDP allows multiple reward values for the same $(s, a, s')$.

### Symbol glossary

| Symbol | Meaning |
| ----------------------- | ---------------------------------------------------------------------------------- |
| $s, s' \in \mathcal{S}$ | Current and next state |
| $a \in \mathcal{A}(s)$ | Action taken in $s$ |
| $r \in \mathcal{R}$ | Reward value (a number, not a distribution) |
| $p(s', r \mid s, a)$ | Joint probability of $(s', r)$ given $(s, a)$ |
| $S_{t+1}, R_{t+1}$ | The random variables whose realised values are $s'$ and $r$ |
| done | Gymnasium flag indicating $s'$ is terminal — relevant for bootstrapping conventions |

### Worked numeric example

Take FrozenLake-v1 with `is_slippery=True`, state $s = 6$, action $a = \text{RIGHT}$ (Gymnasium index $2$). The Technical Validator confirmed the following table by live inspection of `env.unwrapped.P[6][2]`:

| Probability | $s'$ | $r$ | $done$ |
| ----------- | ---- | --- | ------ |
| $1/3$ | $10$ | $0$ | False |
| $1/3$ | $7$ | $0$ | True |
| $1/3$ | $2$ | $0$ | False |

Check normalisation:

$$
\sum_{s', r} p(s', r \mid 6, \text{RIGHT}) \;=\; \tfrac{1}{3} + \tfrac{1}{3} + \tfrac{1}{3} \;=\; 1. \;\checkmark
$$

In summation form
$$
p(s', r \mid 6, \text{RIGHT}) \;=\; \tfrac{1}{3}\,\mathbb{1}[s' = 10, r = 0] + \tfrac{1}{3}\,\mathbb{1}[s' = 7, r = 0] + \tfrac{1}{3}\,\mathbb{1}[s' = 2, r = 0].
$$

A few details worth memorising:

- The slippery convention is "intended direction plus the two *perpendicular* directions, each with probability $1/3$." For RIGHT, the perpendiculars are UP and DOWN. For DOWN, they would be LEFT and RIGHT.
- The intended direction is *not* given a higher probability than the perpendiculars. All three outcomes are equally likely. (A common misconception is that the intended direction gets some boosted probability — it does not in FrozenLake-v1.)
- Every reward here is $0$. The only $+1$ reward in FrozenLake fires on the *transition into* state $15$, not on staying at state $15$. State $15$'s self-loop pays $0$.
- The `done` flag is `True` exactly when $s'$ is a terminal cell — here, $s' = 7$ (a hole). The flag matters for bootstrapping later: when $done$, the future value $v(s')$ is treated as $0$.

For comparison, here is the same query on a *non-slippery* environment, `FrozenLake-v1` with `is_slippery=False`, state $6$, action RIGHT:

| Probability | $s'$ | $r$ | $done$ |
| ----------- | ---- | --- | ------ |
| $1.0$ | $7$ | $0$ | True |

A single deterministic outcome. The four-argument form degenerates to a delta function. This is the structure CliffWalking uses, which is why CliffWalking transitions look so much tidier in the SARSA and Q-learning lessons.

## How the code does it

This lesson ships no starter exercise, but the code snippet from `specs.py` is the canonical incantation for inspecting any tabular environment's dynamics. Read it slowly:

```python
import gymnasium as gym

env = gym.make("FrozenLake-v1", is_slippery=True)

state, action = 6, 2 # state 6, action RIGHT
for prob, next_state, reward, done in env.unwrapped.P[state][action]:
 print(prob, next_state, reward, done)
```

Tie each piece back to the definition:

- **`env.unwrapped.P[state][action]`** is the Python representation of $p(s', r \mid s, a)$. It is a *list* of tuples, one tuple per (state, reward) pair with non-zero probability. The tuple order is `(prob, next_state, reward, done)`.
- **`.unwrapped`** strips off the `OrderEnforcing` and `TimeLimit` wrappers that `gym.make` puts around the raw environment. Those wrappers hide `.P` because it is not part of the public Gym API. Always go through `.unwrapped` when you need the dynamics table.
- Each tuple is one term in the sum $\sum_{s', r} p(s', r \mid s, a)$. The probabilities across all tuples in the list must sum to $1$. (Try `sum(t[0] for t in env.unwrapped.P[6][2])` — it should print `1.0` up to floating-point error.)
- **`done`** is *not* part of the formal $p$ definition. It is Gymnasium's bookkeeping flag indicating whether $s'$ is terminal. Algorithms use it to zero out the bootstrap term, not to compute $p$ itself.

If you wanted to compute the *marginal* state-transition probability $p(s' \mid s, a)$ (summed over rewards), you would aggregate by `next_state`:

```python
from collections import defaultdict

marginal = defaultdict(float)
for prob, next_state, reward, done in env.unwrapped.P[6][2]:
 marginal[next_state] += prob

# marginal == {10: 0.333..., 7: 0.333..., 2: 0.333...}
```

For FrozenLake this aggregation is a no-op because each $(s, a, s')$ triple has a unique reward, but the pattern generalises to environments where the same successor can yield different rewards.

## Common pitfalls and misconceptions

**Pitfall 1: "Transition probability is the probability the agent picks the action."**
This conflates the environment with the agent. $p(s', r \mid s, a)$ is the *environment's* response — it answers "given that the agent did $a$, what does the world produce?" The agent's choice probability is $\pi(a \mid s)$, the *policy*. The Bellman equation has both, multiplied:

$$
v_\pi(s) = \sum_a \underbrace{\pi(a \mid s)}_{\text{agent}} \sum_{s', r} \underbrace{p(s', r \mid s, a)}_{\text{environment}} [r + \gamma v_\pi(s')].
$$

If you ever find yourself summing transition probabilities and getting numbers that depend on whether the agent is exploring, you have mixed up the two distributions.

**Pitfall 2: "A deterministic environment has $p = 1$ for one outcome and $0$ for others."**
Correct for environments like CliffWalking. *Not* correct for FrozenLake-v1 with `is_slippery=True`, where every action has three outcomes with probability $1/3$ each. The slippery FrozenLake has *no* deterministic transitions on any non-terminal cell. If you compute Bellman backups assuming determinism here, you will get wrong values.

**Pitfall 3: "$p(s' \mid s, a)$ and $p(s', r \mid s, a)$ are the same."**
The marginal $p(s' \mid s, a) = \sum_r p(s', r \mid s, a)$ throws away reward information. For FrozenLake all rewards on non-terminal transitions are $0$, so the two carry the same content. But the four-argument form is the canonical one — when you formally write the Bellman equation, you sum over both $s'$ and $r$.

**Pitfall 4: "You need to know $p$ to do RL."**
Dynamic programming does. The whole point of model-free methods (Monte Carlo and TD) is to *avoid* needing $p$ — instead, they call `env.step()` and learn from the resulting (state, reward, next state) samples. That is the central conceptual leap from model-based to model-free RL, and it is why we use the slippery FrozenLake for DP lessons and the model-opaque Blackjack for the first Monte Carlo lesson.

## Connection to the bigger picture

**Forward links.**
- `dp_policy_eval` uses $p(s', r \mid s, a)$ inside the Bellman expectation update — every sweep enumerates the same tuples we printed above.
- `dp_value_iteration` and `dp_policy_improvement` do the same with a $\max_a$ on top.
- `mc_first_visit`, `td_sarsa`, `td_q_learning` deliberately do *not* call `env.unwrapped.P`. They sample from $p$ implicitly through `env.step()`.

**Backward links.** `rl_intro` (agent–environment loop). `mdp_foundations` (where $p$ was introduced as one of three MDP primitives).


## Key takeaways

- $p(s', r \mid s, a) \geq 0$ and $\sum_{s'} \sum_r p(s', r \mid s, a) = 1$. These two constraints turn $p$ into a probability distribution.
- $p$ describes the *environment's* response — it has nothing to do with which action the agent chose.
- On slippery FrozenLake state $6$, action RIGHT, the three outcomes are $\{2, 7, 10\}$, each with probability $1/3$. State $7$ is a hole; all rewards are $0$.
- DP methods consume $p$ directly via `env.unwrapped.P`; model-free methods sample from $p$ via `env.step()` and never see it explicitly.
- $p(s', r \mid s, a)$ is the environment's complete specification: for every state and action it gives the full distribution over successor states and rewards.

## Further reading

- Sutton, R. S. and Barto, A. G. (2018). *Reinforcement Learning: An Introduction*, 2nd ed. — Chapter 3, Section 3.1, eq. 3.2 (p. 48), with derived marginals pp. 48–49. [http://incompleteideas.net/book/the-book-2nd.html](http://incompleteideas.net/book/the-book-2nd.html)
- Gymnasium FrozenLake-v1 documentation (slippery mechanics): [https://gymnasium.farama.org/v0.26.3/environments/toy_text/frozen_lake/](https://gymnasium.farama.org/v0.26.3/environments/toy_text/frozen_lake/)
- Puterman, M. L. (1994). *Markov Decision Processes: Discrete Stochastic Dynamic Programming.* Wiley — formal treatment of the four-argument dynamics function.
