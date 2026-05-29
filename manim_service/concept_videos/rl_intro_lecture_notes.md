# What Is Reinforcement Learning?

## Why this concept matters

Imagine an elf standing at the top-left corner of a frozen lake. The goal is the glowing tile at the far corner. There is no map, no instructor, no labelled example saying "here is what a good step looks like." There is only the ice — sometimes the elf moves where it intended, sometimes it slips — and a single number that arrives at the end of the attempt: $1$ if it reached the goal, $0$ if it fell into a hole. The elf has to learn, just from that scalar trickle of feedback, how to act. *That* is reinforcement learning.

This is the first lesson of the course because every later equation — Bellman backups, Monte Carlo returns, TD targets — exists to answer one question that arises the moment the elf falls into its first hole: **given a reward signal but no labels, how do we improve?** Supervised learning is not allowed to peek at the answer key here, because there is no answer key. Unsupervised learning has nothing to cluster. We need a third paradigm, one built around *acting, observing consequences, and adjusting* — what Sutton and Barto call "the science of decision-making."

The Gymnasium environment we use throughout the video is `FrozenLake-v1` (4×4, `is_slippery=True`). Holes sit at states $\{5, 7, 11, 12\}$; the goal is state $15$. Reward $1.0$ fires *on arrival* at state $15$ — every other transition pays $0$. That sparse reward is the entire teaching signal. The rest of the course is about extracting maximum information from that trickle.

## Intuition first

Picture three short attempts.

**Attempt 1.** The elf walks east into the open ice — and lands in the hole at state $7$. The screen goes dark. No supervisor whispers "you should have gone south." The episode simply ends with reward $0$.

**Attempt 2.** The elf tries a different route — down, down, right, right — but on a slippery tile it skids sideways and falls into the hole at state $12$. Again: blackout, reward $0$. Still no instruction. Just the consequence.

**Attempt 3.** This time the elf threads the corridor $0 \to 4 \to 8 \to 9 \to 10 \to 14 \to 15$, dodges the holes, and a single $+1$ flashes on the goal tile. That number is the *only* thing the world ever told the agent it did well.

Notice what was *not* present in any of those attempts:

- No oracle saying "the optimal action from state 6 is DOWN."
- No dataset of (state, correct-action) pairs.
- No clusters in the data waiting to be discovered.

What *was* present:

- An **agent** (the elf) that chose actions.
- An **environment** (the lake) that responded with new states and rewards.
- A **reward signal** that was almost always silent and occasionally decisive.

That is the canonical RL loop: at each timestep $t$, the agent observes state $S_t$, picks action $A_t$, and the environment hands back the next state $S_{t+1}$ and reward $R_{t+1}$. Repeat. Learn from what you see. The video closes by drawing this loop as a circle — the **agent–environment interface** — the diagram every subsequent lesson will build on.

Contrast it with the other two paradigms in one diagram:

| Paradigm        | Input                       | Feedback signal             | Goal                       |
| --------------- | --------------------------- | --------------------------- | -------------------------- |
| Supervised      | (input, label) pairs        | "Correct answer was $y$."   | Predict labels for new $x$ |
| Unsupervised    | Unlabelled $x$ only         | None                        | Find structure in $x$      |
| **Reinforcement** | State stream from env       | Scalar reward $R_t$         | Maximize expected return   |

RL is not "supervised learning with delayed labels." Nothing ever tells the elf what the right action *was* — only what happened *because of* the action it took.

## The math

There are no equations in this lesson — that is part of the point. But we do introduce the vocabulary and the loop diagram that every later equation will rest on. Let us name the moving pieces.

At each discrete timestep $t = 0, 1, 2, \ldots$:

$$
\underbrace{S_t}_{\text{state}}\;\longrightarrow\;\underbrace{A_t}_{\text{action}}\;\longrightarrow\;\underbrace{R_{t+1}}_{\text{reward}},\; \underbrace{S_{t+1}}_{\text{next state}}.
$$

A complete **trajectory** (or **episode**, for tasks that end) is the resulting sequence

$$
S_0, A_0, R_1, S_1, A_1, R_2, S_2, A_2, R_3, \ldots, S_T.
$$

The episode in FrozenLake terminates as soon as the elf lands on a hole or the goal. In Attempt 3 above the trajectory is

$$
S_0=0,\; A_0=\text{DOWN},\; R_1=0,\; S_1=4,\; A_1=\text{DOWN},\; R_2=0,\; \ldots,\; R_7=1,\; S_7=15.
$$

| Symbol     | Meaning                                                           |
| ---------- | ----------------------------------------------------------------- |
| $S_t$      | State at time $t$ (an integer $0$–$15$ for FrozenLake)            |
| $A_t$      | Action chosen at time $t$ (one of LEFT, DOWN, RIGHT, UP)          |
| $R_{t+1}$  | Reward received after taking $A_t$ in $S_t$                       |
| $T$        | Terminal time step (the episode ends here)                        |
| Agent      | The decision-maker; in code, the policy that maps $S_t$ to $A_t$  |
| Environment | Everything else; here, the FrozenLake board and its slip dynamics |

A few subtleties worth pinning down now, so that the next video can move quickly:

- **Indexing convention.** $R_{t+1}$ is the reward that arrives *after* action $A_t$. The "+1" emphasises that reward is a consequence, not a property of the state alone. (Sutton & Barto eq. 3.1, p. 48.)
- **Sparse vs. dense.** FrozenLake's reward is *sparse*: zero on every transition except arrival at state $15$. Sparsity is what makes credit assignment hard — when the $+1$ finally arrives, *which* of the seven previous actions deserves credit?
- **Stochasticity lives in the environment.** When the elf chooses RIGHT and slips to a different cell, the *agent's* action was still RIGHT. The randomness is the environment's response. We will formalise this as $p(s', r \mid s, a)$ in the very next video.

## How the code does it

This lesson has no starter exercise — it is conceptual scaffolding. But you can already run a one-page Gymnasium loop and watch the trajectory it produces. This is the snippet every later exercise builds on:

```python
import gymnasium as gym

env = gym.make("FrozenLake-v1", is_slippery=True)
observation, info = env.reset(seed=42)   # S_0 and bookkeeping
terminated = truncated = False

while not (terminated or truncated):
    action = env.action_space.sample()                # random π for now
    next_observation, reward, terminated, truncated, info = env.step(action)
    # (observation, action, reward, next_observation) = (S_t, A_t, R_{t+1}, S_{t+1})
    observation = next_observation

env.close()
```

Read it slowly against the loop diagram:

- `env.reset(...)` returns the *initial state* $S_0$ — the elf at corner $0$.
- `env.action_space.sample()` is a *policy* — for now, the trivial one that picks uniformly at random. Every later lesson is about replacing this with something smarter.
- `env.step(action)` is the *environment* responding: it returns $S_{t+1}$, $R_{t+1}$, and two flags. `terminated=True` means the episode reached a hole or the goal. `truncated=True` means a time limit cut it off. Both mean "stop the loop."
- The five-tuple return is modern Gymnasium (`gym >= 0.26`); older code uses a four-tuple with a single `done` flag. The course standardises on the modern API.

There are no TODOs to fill in here, but make sure you can run that snippet end-to-end before the next lesson. Every later exercise assumes the loop is muscle memory.

## Common pitfalls and misconceptions

**Pitfall 1: "RL is supervised learning with delayed labels."**
People hear "the agent eventually gets feedback" and translate that into "the label just arrives late." It does not. There is no label *anywhere* — no entity ever tells the elf what action it *should* have taken. There is only a scalar reward saying what happened. The agent has to figure out, *by itself*, which past action deserves credit. That credit-assignment problem is the central technical challenge of RL and does not exist in supervised learning.

**Pitfall 2: "Reward is the goal."**
The agent's goal is to maximise *cumulative* reward over an entire trajectory, not the next reward. In FrozenLake, taking the action that gives the highest immediate reward is meaningless — every transition pays $0$ until the very last one. The whole point of value functions (coming next video) is to assign credit to states and actions for the rewards they *eventually* lead to, not the ones they immediately produce.

**Pitfall 3: "Stochasticity means the agent is random."**
When the elf slips, that is the *environment* being stochastic — not the agent. The agent's action was RIGHT; the world's response was to put it somewhere unexpected. We will keep these two sources of randomness strictly separated: $\pi(a \mid s)$ is the agent's policy, $p(s', r \mid s, a)$ is the environment's dynamics. Mixing them is the most common conceptual error in the next three lessons.

**Pitfall 4: "If the reward is $0$ most of the time, the agent learns nothing."**
A zero reward is itself information: it tells the agent "you did not die, but you also did not win." Combined with eventual non-zero outcomes, the agent can back-propagate credit through long chains of zero-reward transitions. *How* it does that is exactly what the rest of the course is about.

## Connection to the bigger picture

This video is the entry point to the entire course DAG. Forward, it opens onto:

- **MDP foundations** (next): formalises the agent–environment loop as a Markov decision process — states, actions, rewards, transition dynamics, and the discounted return $G_t$.
- **Transition probability**: zooms in on the environment's response function $p(s', r \mid s, a)$, with FrozenLake state $6$, action RIGHT as the running example.
- **Dynamic programming** (policy evaluation, value iteration, policy improvement): planning algorithms that exploit a known $p$.
- **Monte Carlo & TD learning** (later): model-free algorithms that drop the assumption that $p$ is known and learn directly from sampled experience.

Backward, this lesson has no prerequisites within the course. Outside the course it touches on:

- Basic probability (random variables, expectations) — needed once we start writing $\mathbb{E}[\cdot]$ in the next video.
- Python and NumPy fluency — needed for every exercise.
- The Gymnasium API — covered in the snippet above.

In the Sutton & Barto narrative, this lesson sits squarely in Chapter 1, §1.1–§1.3: the definition of RL, its distinction from other paradigms, and the agent–environment loop. Chapter 3 begins the formalisation we will adopt in the very next lesson.

## Key takeaways

- RL is a third machine-learning paradigm, distinct from supervised and unsupervised learning: no labels, no clusters, only an interaction loop and a scalar reward.
- Every interaction reduces to four objects: state $S_t$, action $A_t$, reward $R_{t+1}$, next state $S_{t+1}$. This is the only data the agent ever sees.
- The agent's randomness ($\pi$) and the environment's randomness ($p$) are separate sources of stochasticity and must never be conflated.
- FrozenLake-v1 is the running example: a sparse-reward, slippery 4×4 grid where the only $+1$ arrives on arrival at the goal.
- Reinforcement learning is the science of learning to act by trial and error — no labels, just rewards.

## Further reading

- Sutton, R. S. and Barto, A. G. (2018). *Reinforcement Learning: An Introduction*, 2nd ed. — Chapter 1, §1.1–§1.3 (pp. 1–7) for the paradigm comparison; Chapter 3, §3.1 (pp. 47–53) for the agent–environment interface formalisation. [http://incompleteideas.net/book/the-book-2nd.html](http://incompleteideas.net/book/the-book-2nd.html)
- Gymnasium FrozenLake-v1 documentation: [https://gymnasium.farama.org/v0.26.3/environments/toy_text/frozen_lake/](https://gymnasium.farama.org/v0.26.3/environments/toy_text/frozen_lake/)
- David Silver's UCL course, Lecture 1 (Introduction to Reinforcement Learning): [https://www.davidsilver.uk/teaching/](https://www.davidsilver.uk/teaching/)
