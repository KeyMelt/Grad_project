# First-Visit Monte Carlo

## Why this concept matters

Every algorithm so far has assumed we *know* the environment's dynamics function $p(s', r \mid s, a)$ — the full distribution over next states and rewards. That assumption is a luxury. Blackjack, for instance, has perfectly definable dynamics (cards, shuffled deck, dealer rule) but the table is so large and the conditional structure so awkward that nobody computes it by hand. The slot machines on the casino floor outside the Blackjack table are even worse: their internals are sealed, and the only thing you can do is play and watch what happens.

First-visit Monte Carlo is the first algorithm in this course that gives up on $p$. It is *model-free*: it never opens the environment's box. Instead, it does what every gambler does — plays an episode end-to-end, watches the final score, and uses that score to revise its estimate of how good each starting situation was. The Bellman expectation equation is still there, lurking underneath, but instead of summing over $(s', r)$ analytically, we *sample* — drawing the random successor by calling `env.step()` and reading the resulting reward — and average many samples over many episodes.

We use Gymnasium's `Blackjack-v1`. A state is the triple $(\text{player sum},\; \text{dealer showing card},\; \text{usable ace})$. Actions are HIT and STICK. Episodes are short — usually $1$ to $5$ steps — and terminate with reward $\{-1, 0, +1\}$ (lose, push, win). The discount $\gamma$ is conventionally $1$ for Blackjack because episodes are guaranteed-finite and short.

![Blackjack-v1: the agent sees its current sum, the dealer's face-up card, and whether it holds a usable ace. Episodes end with reward −1 (lose), 0 (push), or +1 (win).](https://gymnasium.farama.org/_images/blackjack.gif)

## Intuition first

Imagine one episode. The dealer flips a $7$. You start with a player sum of $14$ and no usable ace. You HIT, draw a $5$, now have $19$, and STICK. The dealer flips up cards to reach $18$. You win. Reward $= +1$. Episode over.

The trajectory was

$$
S_0 = (14, 7, F), \; A_0 = \text{HIT}, \; R_1 = 0, \; S_1 = (19, 7, F), \; A_1 = \text{STICK}, \; R_2 = +1.
$$

The return from each step (with $\gamma = 1$) is

$$
G_0 = R_1 + \gamma R_2 = 0 + 1 \cdot 1 = 1, \qquad G_1 = R_2 = 1.
$$

So the data this episode contributes to our value estimates is: *state $(14, 7, F)$ produced return $1$* and *state $(19, 7, F)$ produced return $1$*. We append both to lists keyed by state. The estimate $V(s)$ is the running average of the list for $s$.

Now play 100,000 more episodes. Each one adds at most one return per state (because of the *first-visit* rule — see below). After enough episodes, the running averages converge to $v_\pi(s)$ — the true expected return under whatever policy generated the episodes.

That is the whole idea. The Bellman expectation says $v_\pi(s) = \mathbb{E}_\pi[G_t \mid S_t = s]$. The expectation is a sample mean in disguise. Sample enough returns, average them, get the value.

**The "first-visit" qualifier.** What if state $(14, 7, F)$ appears *twice* in one episode? (It cannot in Blackjack — the player's sum strictly increases. But in other environments, like gridworlds, revisits are common.) The first-visit rule says: count only the return from the *first* time the state appears in the episode. That keeps the samples i.i.d., which is what makes the law of large numbers apply cleanly.

The video shows one Blackjack episode unfolding card by card, with the final reward $+1$ posted on screen. Then it walks the return calculation backward from the terminal step, marking each state with its first-visit return.

## The math

### Return, computed backward

Recall the return from time $t$:

$$
G_t \;=\; R_{t+1} + \gamma R_{t+2} + \gamma^2 R_{t+3} + \cdots + \gamma^{T-t-1} R_T \;=\; \sum_{k=0}^{T-t-1} \gamma^k R_{t+k+1}.
$$

This is the standard discounted return. For Blackjack with $\gamma = 1$, the return from any timestep is just the terminal reward (because all intermediate rewards are $0$). But in general we have to roll the discount forward.

The efficient computation is **backward**: start from $G = 0$ at the terminal step and walk back, accumulating

$$
G \;\leftarrow\; R_{t+1} + \gamma \cdot G.
$$

That is the same return recursion from `mdp_foundations`, used as a *computation* rather than an *equation*.

### First-visit update

For each episode, iterate $t = T-1, T-2, \ldots, 0$ (or equivalently, forward and remember the first visits). For each timestep, check if $S_t$ has been visited earlier in this episode; if not, this is the first visit, and we append $G_t$ to the running list:

$$
\text{if } S_t \notin \{S_0, \ldots, S_{t-1}\}: \quad \text{Returns}(S_t).\text{append}(G_t).
$$

After appending, the estimate is the running average:

$$
\boxed{\;V(s) \;\leftarrow\; \text{mean}(\text{Returns}(s)).\;}
$$

92. Repeated many times across many episodes, $V(s) \to v_\pi(s)$ as the number of first-visit returns at $s$ grows (law of large numbers).

### Symbol glossary

| Symbol | Meaning |
| -------------------- | ------------------------------------------------------------------------ |
| Episode | A finite sequence $(S_0, A_0, R_1, S_1, A_1, R_2, \ldots, R_T)$ |
| $T$ | Terminal timestep — episode ends here |
| $G_t$ | Discounted return from time $t$ |
| $\text{Returns}(s)$ | Running list of first-visit returns for state $s$ across all episodes |
| $V(s)$ | Running estimate — the mean of $\text{Returns}(s)$ |
| $\gamma$ | Discount (Blackjack convention: $1$; lesson default in code: $0.95$) |
| visited_states | Per-episode set tracking which states have already had their first visit |

### Worked numeric example

Consider an artificial episode (not Blackjack — built for illustration) of length $T = 3$ with discount $\gamma = 0.9$:

$$
(S_0=\mathrm{A}, R_1 = 0), (S_1=\mathrm{B}, R_2 = 0), (S_2=\mathrm{A}, R_3 = 1).
$$

State A appears twice (at $t=0$ and $t=2$); state B appears once (at $t=1$).

Compute returns backward starting at $G = 0$:

- $t = 2$: $G \leftarrow R_3 + \gamma \cdot G = 1 + 0.9 \cdot 0 = 1$. So $G_2 = 1$.
- $t = 1$: $G \leftarrow R_2 + \gamma \cdot G = 0 + 0.9 \cdot 1 = 0.9$. So $G_1 = 0.9$.
- $t = 0$: $G \leftarrow R_1 + \gamma \cdot G = 0 + 0.9 \cdot 0.9 = 0.81$. So $G_0 = 0.81$.

First-visit returns:

- State A's first visit is at $t = 0$. Append $G_0 = 0.81$ to $\text{Returns}(\mathrm{A})$.
- State B's first visit is at $t = 1$. Append $G_1 = 0.9$ to $\text{Returns}(\mathrm{B})$.
- State A's revisit at $t = 2$ is *skipped*. (If we used every-visit MC, we would also append $G_2 = 1$.)

After this one episode:

$$
V(\mathrm{A}) = 0.81, \qquad V(\mathrm{B}) = 0.9.
$$

As more episodes accumulate, those single-sample estimates converge to the expected return under the policy that generated them.

## How the code does it

The starter code from `backend/lessons.py`:

```python
DISCOUNT_FACTOR = 0.95
EPISODE_COUNT = 6

def mc_first_visit_prediction(episode, V, returns, gamma=DISCOUNT_FACTOR):
 visited_states = set()
 for index, (state, _action, _reward) in enumerate(episode):
 if __BLANK_mc_first_visit_seen_state__:
 continue
 visited_states.add(state)
 G = 0.0
 discount = 1.0
 # TODO(student): roll the discounted return forward from the first visit.
 raise NotImplementedError("TODO: mc_first_visit_return")
 returns.setdefault(state, []).append(G)
 V[state] = sum(returns[state]) / len(returns[state])
 return V
```

The function processes **one episode** at a time. `episode` is a list of triples $(s, a, r)$ in time order. `V` and `returns` accumulate across episodes — they are the running estimate and the running list of returns per state.

Notice that the starter uses a *forward* scan (the `for index, (state, _action, _reward) in enumerate(episode)` loop walks $t = 0, 1, 2, \ldots, T-1$). The first-visit check is "have I already seen this state earlier in this episode?" The return computation, instead of the backward $G \leftarrow R + \gamma G$ recursion, has to sum forward from $t = \text{index}$ to the end.

Map each piece to the math:

- `visited_states = set()` — the per-episode bookkeeping for the first-visit rule. Reset every episode.
- `for index, (state, _action, _reward) in enumerate(episode):` — walk timesteps forward.

**TODO 1: `mc_first_visit_seen_state`.** The skip condition fires when this state has *already* been visited earlier in this episode. The natural expression is:

```python
state in visited_states
```

If True, `continue` skips this index and we do not append a return. If False, we fall through to the body, which appends the state to `visited_states` and computes the return.

**TODO 2: `mc_first_visit_return`.** We need to compute $G_t = \sum_{k=0}^{T-t-1} \gamma^k R_{t+k+1}$ — the discounted return from the current `index` to the end of the episode. The two variables `G = 0.0` and `discount = 1.0` are pre-initialised for a forward accumulation:

```python
for future_index in range(index, len(episode)):
 _future_state, _future_action, future_reward = episode[future_index]
 G += discount * future_reward
 discount *= gamma
```

Read the loop: starting from the first-visit index, walk forward to the end of the episode, accumulating `discount * reward` at each step, then multiplying `discount` by $\gamma$ for the next step. This computes $G_t = R_{t+1} + \gamma R_{t+2} + \gamma^2 R_{t+3} + \cdots$ as a forward sum. Equivalent to the backward recursion, just the other direction.

After the TODO, the code appends $G$ to `returns[state]` and updates $V[state]$ to the running mean. That last line — `V[state] = sum(returns[state]) / len(returns[state])` — is the literal MC update $V(s) \leftarrow \text{mean}(\text{Returns}(s))$.

### A note on `returns.setdefault`

`returns.setdefault(state, []).append(G)` is shorthand for "if `state` is not yet a key in `returns`, initialise it to `[]`; either way, append $G$ to the list." This means the first time a state is visited (across all episodes), it gets a fresh list; subsequent visits append to it. Standard Pythonic idiom for accumulating per-key lists.

### Why forward instead of backward?

The pseudocode in research is backward. The starter is forward. Both produce the same numbers. The forward formulation is easier to read for students who have not internalised the backward recursion yet, but it costs $O(T^2)$ instead of $O(T)$ per episode (we re-scan the future at each timestep). For Blackjack with $T \leq 5$ this does not matter; for long episodes it would.

## Common pitfalls and misconceptions

**Pitfall 1: "MC bootstraps like DP."**
It does not. The estimate of one state's value never uses the estimate of another state's value during the update — the update is purely the sample mean of *actual* (not estimated) returns. This is the fundamental contrast with both DP and TD. calls this out explicitly: MC "does not bootstrap."

**Pitfall 2: "MC works for any task."**
Monte Carlo methods are only defined for *episodic* tasks — a well-defined return $G$ requires the episode to terminate. On continuing (non-terminating) tasks you need TD methods or a discounting trick.

**Pitfall 3: "First-visit and every-visit MC give different limits."**
Both converge to $v_\pi$. First-visit's samples are i.i.d. (cleaner analysis); every-visit's are not (returns from later visits in the same episode are correlated with returns from earlier visits). Both work; first-visit is the default in introductory treatments because its convergence proof is simpler.

**Pitfall 4: "The episode-by-episode update is online."**
MC is *incremental between episodes* but *not online within an episode*. You cannot update $V(S_3)$ until the episode reaches its terminal step $T$ and the return $G_3$ is known. This is the central difference between MC and TD: TD updates after every transition, MC waits for the episode to end.

**Pitfall 5: "Returns are computed forward."**
The canonical implementation computes returns backward, accumulating $G \leftarrow \gamma G + R_{t+1}$ from $t = T-1$ down to $t = 0$. This is $O(T)$ per episode. The starter code uses a forward $O(T^2)$ implementation for readability; both produce the same numbers. (This is the spec's `misconception_to_prevent`: "Monte Carlo waits for the full episode and does not bootstrap from a next-state estimate.")

## Connection to the bigger picture

**Forward links.**
- `td_sarsa`, `td_q_learning`: TD methods are the "best of both worlds" between DP and MC. Like MC, they sample. Like DP, they bootstrap from a value estimate at the next step. This means they update *online*, after every transition, not after every episode.
- Monte Carlo *control*: extends prediction to learning $Q$ and improving $\pi$ with $\epsilon$-soft policies. We do not cover MC control in this course because TD control supersedes it for online settings.

**Backward links.** `mdp_foundations` (defines $G_t$ and $v_\pi$ — MC just estimates $v_\pi$ by sampling). `dp_policy_eval` (the model-based counterpart that MC replaces with sample averaging — the *target* $v_\pi$ is the same).


## Key takeaways

- Monte Carlo is *model-free*: it does not need $p(s', r \mid s, a)$; it learns from sampled episodes.
- The first-visit rule appends one return per state per episode, keeping samples i.i.d.
- Updates happen *between* episodes, never *during* one — the full return $G_t$ must be known before $V(S_t)$ can be updated.
- The Bellman expectation underneath is unchanged: $v_\pi(s) = \mathbb{E}_\pi[G_t \mid S_t = s]$. MC realises the expectation as a sample mean.
- First-visit Monte Carlo updates a state only after the episode ends, using the full discounted return from its first occurrence.

## Further reading

- Sutton, R. S. and Barto, A. G. (2018). *Reinforcement Learning: An Introduction*, 2nd ed. — Chapter 5, Section 5.1 (pp. 91–94). Algorithm box p. 92; Blackjack example 5.1 p. 93; convergence discussion p. 92. [http://incompleteideas.net/book/the-book-2nd.html](http://incompleteideas.net/book/the-book-2nd.html)
- Gymnasium Blackjack tutorial: [https://gymnasium.farama.org/v0.26.3/tutorials/blackjack_tutorial/](https://gymnasium.farama.org/v0.26.3/tutorials/blackjack_tutorial/)
- Gymnasium Blackjack docs: [https://gymnasium.farama.org/environments/toy_text/blackjack/](https://gymnasium.farama.org/environments/toy_text/blackjack/)
- David Silver's UCL course, Lecture 4 (Model-Free Prediction): [https://www.davidsilver.uk/teaching/](https://www.davidsilver.uk/teaching/)
- Singh, S. P. and Sutton, R. S. (1996). *Reinforcement learning with replacing eligibility traces.* Machine Learning, 22:123–158 — the every-visit MC convergence proof S&B cites.
