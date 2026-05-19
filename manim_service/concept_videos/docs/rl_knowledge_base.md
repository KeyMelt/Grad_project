# RL Knowledge Base

This document is the per-lesson theory map used by the RL Expert agent in lieu of
reciting Sutton & Barto from memory. The Technical Validator also cross-checks
numerical examples against the equations listed here before production.

**Primary source:** Sutton, R. S. and Barto, A. G. (2018). *Reinforcement Learning:
An Introduction.* 2nd edition. The MIT Press. Cambridge, MA. (License: CC BY-NC-ND 2.0.)

All chapter, section, and page references below are to the printed pages of the
2018 second edition. Equation numbers `(4.x)`, `(6.x)`, etc. are S&B's own numbering.

**Notation conventions (consistent with S&B Chapter 3):**

- $s, s' \in \mathcal{S}$ — states; $\mathcal{S}^+$ adds the terminal state for episodic tasks
- $a \in \mathcal{A}(s)$ — actions available in state $s$
- $r \in \mathcal{R}$ — rewards
- $\pi(a\mid s)$ — probability of taking action $a$ in state $s$ under policy $\pi$
- $p(s', r \mid s, a)$ — four-argument dynamics function (the MDP model)
- $v_\pi(s)$ — state-value function under $\pi$; $v_*(s)$ — optimal state value
- $q_\pi(s, a)$ — action-value function under $\pi$; $q_*(s, a)$ — optimal action value
- $\gamma \in [0, 1]$ — discount factor
- $\alpha \in (0, 1]$ — step-size parameter (learning rate)
- $G_t = R_{t+1} + \gamma R_{t+2} + \gamma^2 R_{t+3} + \cdots$ — return from step $t$

---

## Policy Evaluation (dp_policy_eval)

**S&B Reference:** Chapter 4, Section 4.1 ("Policy Evaluation (Prediction)"), pages 74–75.

**Key equation:** Iterative policy evaluation update (S&B eq. 4.5):

$$v_{k+1}(s) \;\doteq\; \mathbb{E}_\pi\!\left[R_{t+1} + \gamma\, v_k(S_{t+1}) \mid S_t = s\right]
\;=\; \sum_{a} \pi(a\mid s) \sum_{s', r} p(s', r \mid s, a)\,[\,r + \gamma\, v_k(s')\,].$$

Pseudocode (S&B p. 75) — sweep every state once per iteration, terminate when
$\max_{s}|v_{k+1}(s) - v_k(s)| < \theta$.

**Intuition:** Policy evaluation answers "*if* the agent follows policy $\pi$ from
every state, how much total discounted reward should it expect?" The Bellman
equation for $v_\pi$ relates each state's value to a one-step lookahead average
over successor states, so we keep applying that lookahead as an assignment until
the values stop changing. The fixed point is $v_\pi$.

**Prerequisites:** (none from this lesson set — but assumes MDP fundamentals from
S&B Chapter 3: states, actions, rewards, $p(s', r \mid s, a)$, return $G_t$,
discount $\gamma$, and the Bellman equation for $v_\pi$.)

**Common misconceptions:**

- **"Policy evaluation finds the *best* policy."** It does not. It computes
  $v_\pi$ for a *given* policy $\pi$, including a deliberately bad one. Finding
  the best policy requires combining evaluation with improvement (policy
  iteration) or skipping straight to value iteration.
- **"You need to wait for $\Delta = 0$ before stopping."** S&B's pseudocode
  stops when $\Delta < \theta$ for a small $\theta > 0$. Exact convergence is
  only asymptotic; in practice the threshold $\theta$ trades accuracy for
  compute. (See S&B p. 75, last paragraph.)
- **"In-place vs. two-array updates give different answers."** Both converge to
  the same $v_\pi$. In-place (Gauss–Seidel style) typically converges *faster*
  because successor states updated earlier in the sweep contribute their new
  values to states updated later (S&B p. 75).
- **"The update averages over actions, so the policy must be stochastic."** Not
  true — if $\pi$ is deterministic, $\pi(a\mid s)$ is a one-hot distribution and
  the sum over $a$ collapses to a single term.

**Boundary conditions:**

- **Terminal states:** $v(\text{terminal}) \equiv 0$ by definition for all $s' \in \mathcal{S}^+ \setminus \mathcal{S}$. The pseudocode initializes them to 0 and never overwrites them.
- **Existence of $v_\pi$:** Guaranteed if either $\gamma < 1$ or eventual termination is guaranteed from all states under $\pi$ (S&B p. 74).
- **$\gamma = 1$ on a non-terminating task:** $v_\pi$ may diverge — the geometric series of rewards is unbounded. S&B's Example 4.1 (4×4 gridworld, undiscounted, $-1$ per step) is safe only because the equiprobable policy still terminates with probability 1.
- **$\gamma = 0$:** Reduces to $v_\pi(s) = \mathbb{E}_\pi[R_{t+1} \mid S_t = s]$ — the immediate expected reward. Useful as a sanity-check limit.

**Gymnasium connection:**

Policy evaluation is a *model-based* method — it requires the full $p(s', r \mid s, a)$
distribution. In Gymnasium's `toy_text` environments (FrozenLake-v1, Taxi-v3,
CliffWalking-v0), this is exposed as `env.unwrapped.P`:

```python
env = gym.make("FrozenLake-v1", is_slippery=True)
# env.unwrapped.P[state][action] returns:
#   list of (transition_prob, next_state, reward, done) tuples
for transition_prob, next_state, reward, done in env.unwrapped.P[state][action]:
    value += action_prob * transition_prob * (reward + gamma * V[next_state])
```

Note: `P` is only available on environments whose model is enumerable. You must
go through `.unwrapped` because `gym.make` returns a wrapped object whose
`OrderEnforcing` / `TimeLimit` wrappers do not surface `P`. The four-tuple
inside `P[s][a]` is precisely the sample-space realization of S&B's
$p(s', r \mid s, a)$ — for a deterministic transition the list has one entry
with `transition_prob = 1.0`.

Policy evaluation itself never calls `env.step()` or `env.reset()` — those are
for sample-based methods. The sweep iterates the Python dictionary `env.unwrapped.P`
directly.

**Reputable supplementary sources:**

- David Silver's UCL course, Lecture 3 (Planning by Dynamic Programming): https://www.davidsilver.uk/teaching/
- *Algorithms for Reinforcement Learning* by Csaba Szepesvári, §3.1 (free PDF): https://sites.ualberta.ca/~szepesva/rlbook.html

---

## Policy Improvement (dp_policy_improvement)

**S&B Reference:** Chapter 4, Section 4.2 ("Policy Improvement"), pages 76–80.

**Key equation:** Greedy policy improvement (S&B eq. 4.9):

$$\pi'(s) \;\doteq\; \arg\max_{a}\,q_\pi(s, a)
\;=\; \arg\max_{a} \sum_{s', r} p(s', r \mid s, a)\,[\,r + \gamma\, v_\pi(s')\,].$$

Backed by the **policy improvement theorem** (S&B eq. 4.7–4.8): if
$q_\pi(s, \pi'(s)) \ge v_\pi(s)$ for all $s$, then $v_{\pi'}(s) \ge v_\pi(s)$ for
all $s$, with strict inequality at any state where eq. 4.7 is strict.

**Intuition:** Once we know how good every state is under $\pi$ (i.e. once we
have $v_\pi$), we can ask, for each state, "what if I deviated just this once,
took action $a$, and then went back to $\pi$ forever?" The answer is
$q_\pi(s, a)$. If some action beats the current $\pi(s)$, switching to it is a
guaranteed improvement — and doing this greedily at every state produces a new
policy that is uniformly at least as good as the old one.

**Prerequisites:** [[dp_policy_eval]] (you need $v_\pi$ before you can compute
$q_\pi(s, a)$ via the one-step lookahead).

**Common misconceptions:**

- **"The new greedy policy is optimal."** No — it is only guaranteed to be *at least as good as* $\pi$. It is optimal only when $v_\pi = v_*$ (S&B p. 79, eq. just before the optimal-policy claim). Generally you alternate evaluation and improvement (policy iteration) until the policy stops changing.
- **"You need exact $v_\pi$ for the improvement step."** The policy improvement *theorem* (eq. 4.7) holds for any value function the policy is greedy with respect to. In practice, truncated evaluation works fine — this is the basis of value iteration.
- **"Ties must be broken deterministically."** S&B explicitly allows stochastic policies with arbitrary apportioning of probability among tied maximizing actions (p. 79, last paragraph), as long as submaximal actions get zero probability. The improvement guarantee still holds.
- **"Each improvement step must change the policy."** A step that leaves $\pi$ unchanged is the termination condition of policy iteration — it indicates $\pi = \pi^*$ (S&B p. 80, pseudocode `policy-stable` flag).

**Boundary conditions:**

- **Terminal states:** $\pi^*(\text{terminal})$ is undefined / irrelevant — no actions are taken from terminal states (rewards and values are 0 there).
- **No improvement possible:** If $v_{\pi'} = v_\pi$, then from $v_{\pi'}(s) = \max_a \sum_{s',r} p(s',r\mid s,a)[r + \gamma v_{\pi'}(s')]$ — the Bellman optimality equation — we conclude $\pi$ is already optimal (S&B p. 79).
- **Stochastic policies:** The theorem and the greedy step both extend; you do not need to reduce to deterministic policies first.
- **Tie-breaking under exploring/$\epsilon$-soft constraints:** With $\epsilon$-soft policies (S&B Exercise 4.6), the greedy step is restricted to policies that give probability $\ge \epsilon/|\mathcal{A}(s)|$ to every action — the argmax claims most of the remaining probability.

**Gymnasium connection:**

Like policy evaluation, this is a *model-based* operation that consumes
`env.unwrapped.P` rather than environment interaction:

```python
for action in range(env.action_space.n):
    action_value = 0.0
    for transition_prob, next_state, reward, done in env.unwrapped.P[state][action]:
        action_value += transition_prob * (reward + gamma * V[next_state])
    action_values[action] = action_value
policy[state] = np.argmax(action_values)
```

`env.action_space.n` provides $|\mathcal{A}(s)|$ for discrete `Discrete` spaces;
for environments where the action set varies with state, S&B's $\mathcal{A}(s)$
becomes a runtime check rather than a fixed range.

The improvement step does *not* depend on the agent ever interacting with the
environment via `env.step()`. The resulting `policy` array is then used to
generate behavior, but improvement itself is pure offline planning.

**Reputable supplementary sources:**

- Sutton & Barto Errata page (for typo corrections to Ch. 4): http://incompleteideas.net/book/the-book-2nd.html
- Bertsekas, *Dynamic Programming and Optimal Control* Vol. 1, §1.3 — proof of the policy improvement theorem in the more general DP setting.

---

## Value Iteration (dp_value_iteration)

**S&B Reference:** Chapter 4, Section 4.4 ("Value Iteration"), pages 82–84.

**Key equation:** Value iteration update (S&B eq. 4.10):

$$v_{k+1}(s) \;\doteq\; \max_{a}\,\mathbb{E}\!\left[R_{t+1} + \gamma\, v_k(S_{t+1}) \mid S_t = s, A_t = a\right]
\;=\; \max_{a} \sum_{s', r} p(s', r \mid s, a)\,[\,r + \gamma\, v_k(s')\,].$$

After convergence, recover an optimal deterministic policy by one final greedy
step: $\pi(s) = \arg\max_a \sum_{s', r} p(s', r \mid s, a)\,[\,r + \gamma\, V(s')\,]$.

**Intuition:** Value iteration is policy iteration with the policy-evaluation
phase truncated to *one* sweep. Equivalently: it turns the Bellman *optimality*
equation (rather than the Bellman equation for a fixed $\pi$) directly into an
update rule. Each sweep folds one step of evaluation and one step of
improvement together, and the sequence $\{v_k\}$ converges to $v_*$.

**Prerequisites:** [[dp_policy_eval]], [[dp_policy_improvement]] (value iteration
is precisely what you get when you fuse one sweep of each into a single
maximum-bearing update).

**Common misconceptions:**

- **"Value iteration is faster than policy iteration."** Sometimes, but not always. Policy iteration often converges in surprisingly few outer iterations (S&B p. 80; Jack's Car Rental example converges in 5). Value iteration takes more sweeps but each sweep is cheaper. In general, *truncated policy iteration* — somewhere between the two — is fastest in practice (S&B p. 83, last paragraph).
- **"You can drop the final argmax — the value function is the answer."** $v_*$ is what value iteration produces directly. The argmax step is still needed to extract a policy, because for downstream use the agent must know *which action* to take, not just the state value.
- **"Sweeps must be synchronous."** S&B's *asynchronous DP* (§4.5) shows that updating one state at a time, in any order, converges as long as every state is updated infinitely often. Both Jacobi and Gauss–Seidel orderings are valid; in-place is usually faster.
- **"$v_k$ converging implies $\pi_k$ has stopped changing."** The greedy policy with respect to $v_k$ can stop changing *before* $v_k$ itself fully converges. In fact, this is the practical termination signal in many implementations (S&B Figure 4.1 — the greedy policy is optimal after $k=3$ while $v_k$ has not yet converged).

**Boundary conditions:**

- **Terminal states:** $V(\text{terminal}) \equiv 0$, fixed throughout. The max is taken only over actions from non-terminal states.
- **$\gamma = 1$ on undiscounted episodic tasks:** Works *if* proper termination is guaranteed under all policies. Gambler's problem (S&B Example 4.3) is undiscounted, episodic, and converges. CliffWalking is also $\gamma = 1$.
- **Stochastic optimal policies:** Eq. 4.10 produces $v_*$ uniquely, but the optimal *policy* is not unique when multiple actions tie for the argmax. S&B's Gambler's Problem produces a whole family of optimal policies (p. 84).
- **Number of iterations:** Formally infinite (asymptotic convergence). In practice, terminated when $\max_s |v_{k+1}(s) - v_k(s)| < \theta$, like policy evaluation.

**Gymnasium connection:**

Value iteration consumes `env.unwrapped.P` exactly like policy evaluation, with
the only difference being the `max` over actions instead of an expectation
under $\pi$:

```python
env = gym.make("FrozenLake-v1", is_slippery=True)
action_count = env.action_space.n
V = np.zeros(env.observation_space.n)
gamma = 0.99

while True:
    delta = 0.0
    for state in range(env.observation_space.n):
        action_values = np.zeros(action_count)
        for action in range(action_count):
            for transition_prob, next_state, reward, done in env.unwrapped.P[state][action]:
                future = 0.0 if done else V[next_state]
                action_values[action] += transition_prob * (reward + gamma * future)
        new_value = max(action_values)
        delta = max(delta, abs(new_value - V[state]))
        V[state] = new_value
    if delta < theta: break
```

Two notes specific to Gymnasium's `toy_text` semantics:

1. The `done` flag from `env.unwrapped.P[s][a]` distinguishes terminal successors. By convention, you should treat `V[next_state]` as 0 when `done` is True — Gymnasium does not necessarily store terminal entries with 0 successor value implicitly, so the `if done` guard is good practice.
2. `env.observation_space.n` is $|\mathcal{S}^+|$ — terminal states are included in the integer state index range.

`env.step()` is never invoked during value iteration — like all DP methods, this
is pure offline planning.

**Reputable supplementary sources:**

- OpenAI Spinning Up — *Intro to RL Part 2* (model-based vs. model-free taxonomy): https://spinningup.openai.com/en/latest/spinningup/rl_intro2.html
- David Silver's UCL course, Lecture 3 slides on value iteration: https://www.davidsilver.uk/teaching/

---

## First-Visit Monte Carlo Prediction (mc_first_visit)

**S&B Reference:** Chapter 5, Section 5.1 ("Monte Carlo Prediction"), pages 91–94.

**Key equation:** First-visit MC estimate (S&B p. 92, algorithm box):

$$V(S_t) \;\leftarrow\; \mathrm{average}\bigl(\,\mathrm{Returns}(S_t)\,\bigr),$$

where $\mathrm{Returns}(S_t)$ accumulates the return $G$ computed backwards from
the episode's terminal step, $G \leftarrow \gamma G + R_{t+1}$, and a return is
appended only on the *first* visit to $S_t$ within an episode:

$$\text{if } S_t \notin \{S_0, S_1, \ldots, S_{t-1}\}\!: \quad \mathrm{Returns}(S_t).\mathrm{append}(G).$$

**Intuition:** Without a model, we can still estimate $v_\pi(s)$ — we simply run
the policy many times and average the returns observed *after* reaching $s$.
The "first-visit" qualifier means each episode contributes at most one sample
per state (the return from the first time $s$ was visited in that episode), so
the samples are i.i.d. and the law of large numbers gives
$V(s) \to v_\pi(s)$ as the visit count grows.

**Prerequisites:** [[dp_policy_eval]] (as the model-based counterpart that MC
methods replace with sample averaging — the *target* $v_\pi$ is the same, only
the means of estimation differs).

**Common misconceptions:**

- **"Every-visit MC is biased and should be avoided."** Both first-visit and every-visit MC converge to $v_\pi$ — first-visit's samples are independent (easier to analyze), every-visit's are not, but every-visit also converges quadratically (Singh & Sutton, 1996, cited on S&B p. 93). Every-visit is in fact preferred when extending to function approximation and eligibility traces (S&B p. 92).
- **"MC bootstraps like DP."** It does *not*. The estimate of one state's value never uses the estimate of any other state's value (S&B p. 95, "do not bootstrap"). This is the fundamental contrast with both DP and TD methods.
- **"MC works for any task."** S&B defines MC methods only for *episodic* tasks (p. 91, second-to-last paragraph) — a well-defined return $G$ requires the episode to terminate. On continuing tasks you need TD or a discounting trick.
- **"The episode-by-episode update is online."** MC is incremental *between* episodes, but within an episode it is not online — values cannot be updated until the episode ends and the return is known (S&B p. 91).
- **"Returns are computed forward."** The pseudocode (p. 92) iterates $t$ from $T-1$ down to $0$ and accumulates $G \leftarrow \gamma G + R_{t+1}$ — backward, because each $G_t$ depends on later rewards. This is the efficient implementation.

**Boundary conditions:**

- **Terminal states:** $V(\text{terminal}) \equiv 0$ — no return is collected for a state where the episode has already ended. (Returns are appended only for states with $t < T$.)
- **States never visited:** $V(s)$ remains at its arbitrary initialization. MC methods do not generalize across states; if a state is never visited under $\pi$, you learn nothing about it. (Compare DP, which updates every state every sweep regardless of the policy's visit distribution.)
- **$\gamma = 1$ on undiscounted episodic tasks:** Standard for Blackjack (S&B Example 5.1) — returns are simply the terminal reward $\{-1, 0, +1\}$. Convergence requires episodes to be guaranteed-finite.
- **First-visit guarantee strength:** Each first-visit return is an i.i.d. unbiased sample of $v_\pi(s)$ with finite variance (S&B p. 93), so the standard deviation of the estimate falls as $1/\sqrt{n}$ where $n$ is the number of returns averaged.

**Gymnasium connection:**

MC methods need *only* episode samples — no `env.P`. They are model-free in the
strict sense:

```python
env = gym.make("Blackjack-v1")
obs, info = env.reset(seed=42)
episode = []                       # list of (state, action, reward) tuples
done = False
while not done:
    action = policy(obs)
    next_obs, reward, terminated, truncated, info = env.step(action)
    episode.append((obs, action, reward))
    obs = next_obs
    done = terminated or truncated

G = 0.0
visited_states = set()
for t in range(len(episode) - 1, -1, -1):  # backward
    state, action, reward = episode[t]
    G = gamma * G + reward
    if state in visited_states: continue   # first-visit check
    visited_states.add(state)
    returns[state].append(G)
    V[state] = mean(returns[state])
```

API specifics worth noting:

1. Gymnasium's `env.step()` returns a 5-tuple `(obs, reward, terminated, truncated, info)`. Episode end is `terminated or truncated`. (The older Gym API used a 4-tuple with a single `done` flag — code targeting modern Gymnasium must handle both.)
2. `env.reset(seed=...)` returns `(obs, info)` — not just `obs`. The reset call begins a new episode.
3. For Blackjack, `obs` is a tuple `(player_sum, dealer_showing, usable_ace)` — a hashable composite state, suitable as a dict key for `returns`.
4. The transition probabilities and dealer policy are *opaque* to the agent — `env.unwrapped.P` for Blackjack would be impractically large even if exposed, which is exactly the case S&B uses MC to motivate (p. 94: "DP methods require... the four-argument function p, and it is not easy to determine this for blackjack").

**Reputable supplementary sources:**

- Gymnasium Blackjack documentation: https://gymnasium.farama.org/environments/toy_text/blackjack/
- David Silver's UCL course, Lecture 4 (Model-Free Prediction): https://www.davidsilver.uk/teaching/
- Singh, S. P. and Sutton, R. S. (1996). *Reinforcement learning with replacing eligibility traces.* Machine Learning, 22:123–158 — the every-visit MC convergence proof S&B cites.

---

## SARSA: On-policy TD Control (td_sarsa)

**S&B Reference:** Chapter 6, Section 6.4 ("Sarsa: On-policy TD Control"), pages 129–131.

**Key equation:** SARSA update (S&B eq. 6.7):

$$Q(S_t, A_t) \;\leftarrow\; Q(S_t, A_t) + \alpha\,\bigl[\,R_{t+1} + \gamma\, Q(S_{t+1}, A_{t+1}) - Q(S_t, A_t)\,\bigr].$$

The name comes from the quintuple $(S_t, A_t, R_{t+1}, S_{t+1}, A_{t+1})$ that
drives one update. If $S_{t+1}$ is terminal, $Q(S_{t+1}, A_{t+1})$ is defined as
zero (S&B p. 129).

**Intuition:** SARSA blends MC's sample-based learning with DP's bootstrapping.
After every single transition, the TD target $R_{t+1} + \gamma Q(S_{t+1}, A_{t+1})$
uses the *currently estimated* $Q$ value of the next state–action pair the agent
*actually chose* (an on-policy sample) instead of waiting for the full return
$G_t$. Each step nudges $Q(S_t, A_t)$ toward this target with step size $\alpha$.

**Prerequisites:** [[mc_first_visit]] (for the idea of learning $Q$ from sampled
experience without a model), [[dp_value_iteration]] (for the idea of
bootstrapping — using current estimates inside the update target).

**Common misconceptions:**

- **"SARSA learns $q_*$."** Not directly. SARSA learns $q_\pi$ for the *behavior policy* $\pi$ it is following. To recover $q_*$, $\pi$ must converge to the greedy policy (e.g., $\epsilon$-greedy with $\epsilon \to 0$, as S&B notes on p. 129: "Sarsa converges with probability 1 to an optimal policy... as long as... the policy converges in the limit to the greedy policy").
- **"On-policy means the policy doesn't change."** On-policy means the policy used to *generate behavior* is the same policy being *evaluated and improved*. The policy itself can — and must — change as $Q$ updates. The contrast is with off-policy methods (Q-learning), which learn about a different policy than the one generating data.
- **"SARSA can't learn during the same episode as the agent is acting."** It can — that is the whole point of being incremental. Updates happen on every step, unlike MC which must wait for episode end (S&B p. 124 on the "online, fully incremental fashion" advantage of TD).
- **"SARSA is always safer than Q-learning."** SARSA's safety on CliffWalking (S&B Example 6.6, p. 132) comes from its $\epsilon$-greedy behavior policy *being the policy it is evaluating* — it accounts for the exploration cost. With $\epsilon \to 0$ both methods converge to the same optimal greedy policy.
- **"The next action $A_{t+1}$ must come from the same policy that selected $A_t$."** Yes, by definition of on-policy — but the policy is implicitly updated each step (because $Q$ is). $A_{t+1}$ is sampled from $\pi(\cdot \mid S_{t+1})$ using whatever $Q$ exists *at that moment*.

**Boundary conditions:**

- **Terminal states:** $Q(\text{terminal}, \cdot) \equiv 0$ — fixed by initialization. When $S_{t+1}$ is terminal, the update reduces to $Q(S_t, A_t) \leftarrow Q(S_t, A_t) + \alpha[R_{t+1} - Q(S_t, A_t)]$.
- **Convergence:** With probability 1 to an optimal policy and action-value function, *if* (1) all state–action pairs are visited infinitely often, and (2) the policy converges in the limit to the greedy policy (S&B p. 129). Both conditions matter — fixed $\epsilon > 0$ gives bounded suboptimality, not optimality.
- **$\alpha$ schedule:** A constant $\alpha$ converges in mean only (small enough $\alpha$); a Robbins–Monro schedule ($\sum \alpha_t = \infty$, $\sum \alpha_t^2 < \infty$) gives almost-sure convergence (S&B p. 124, last paragraph of §6.2). For practice, constant $\alpha$ is the norm.
- **$\gamma = 1$ on undiscounted episodic tasks:** Standard for Windy Gridworld (S&B Example 6.5) and CliffWalking (Example 6.6) — convergence still holds provided episodes terminate.

**Gymnasium connection:**

SARSA is model-free and online — it never touches `env.unwrapped.P`:

```python
env = gym.make("CliffWalking-v0")
Q = np.zeros((env.observation_space.n, env.action_space.n))
gamma, alpha, epsilon = 1.0, 0.5, 0.1

for episode in range(num_episodes):
    state, info = env.reset()
    action = epsilon_greedy(Q, state, epsilon)
    done = False
    while not done:
        next_state, reward, terminated, truncated, info = env.step(action)
        done = terminated or truncated
        next_action = None if done else epsilon_greedy(Q, next_state, epsilon)
        bootstrap = 0.0 if next_action is None else Q[next_state][next_action]
        Q[state][action] += alpha * (reward + gamma * bootstrap - Q[state][action])
        state, action = next_state, next_action
```

Key API points:

1. The "SARSA" quintuple maps one-to-one onto Gymnasium's loop: `(state, action)` from before `step`, `reward` and `next_state` from the `step` return, and `next_action` chosen from the behavior policy on `next_state` *before* the next `step` call. The two action selections per step are what makes it on-policy.
2. Terminal handling: when `terminated` is True, `Q[next_state][next_action]` must contribute zero. The cleanest way is to compute `bootstrap = 0.0` rather than calling `epsilon_greedy` on a terminal state. (`truncated` from `TimeLimit` is conceptually different — the episode was cut off, the next state is not terminal — but for the bootstrap-zero convention both branches collapse.)
3. CliffWalking is deterministic — `env.step()` returns the same successor every time for the same `(state, action)`. The on-policy/off-policy difference still surfaces because the *exploration* randomness comes from the $\epsilon$-greedy policy, which SARSA's target accounts for (S&B's CliffWalking discussion, p. 132).

**Reputable supplementary sources:**

- Gymnasium CliffWalking documentation: https://gymnasium.farama.org/environments/toy_text/cliff_walking/
- Rummery, G. A. and Niranjan, M. (1994). *On-Line Q-Learning Using Connectionist Systems.* Cambridge University Engineering Department. (Original SARSA paper, then called "modified connectionist Q-learning".)
- David Silver's UCL course, Lecture 5 (Model-Free Control): https://www.davidsilver.uk/teaching/

---

## Q-Learning: Off-policy TD Control (td_q_learning)

**S&B Reference:** Chapter 6, Section 6.5 ("Q-learning: Off-policy TD Control"), pages 131–132.

**Key equation:** Q-learning update (S&B eq. 6.8):

$$Q(S_t, A_t) \;\leftarrow\; Q(S_t, A_t) + \alpha\,\Bigl[\,R_{t+1} + \gamma\, \max_{a}\,Q(S_{t+1}, a) - Q(S_t, A_t)\,\Bigr].$$

If $S_{t+1}$ is terminal, $\max_a Q(S_{t+1}, a)$ is defined as zero.

**Intuition:** Q-learning is SARSA with one critical change: the bootstrap term
uses the maximum $Q$ value over *all* actions in $S_{t+1}$, not the value of the
action actually taken next. This makes the target an estimate of $q_*$
directly, independent of the policy used to generate behavior — hence
"off-policy". The behavior policy still matters for *exploration coverage*
(every state–action pair must be visited infinitely often), but it does not
appear in the target.

**Prerequisites:** [[td_sarsa]] (Q-learning differs from SARSA only in
substituting $\max_a Q(S_{t+1}, a)$ for $Q(S_{t+1}, A_{t+1})$ — start from SARSA),
[[dp_value_iteration]] (Q-learning is, structurally, sample-based asynchronous
value iteration on $q_*$).

**Common misconceptions:**

- **"Q-learning always outperforms SARSA."** On CliffWalking with fixed $\epsilon = 0.1$, Q-learning learns the optimal *greedy* policy (walk along the edge of the cliff), but its *online return* is worse than SARSA's because $\epsilon$-greedy exploration occasionally pushes the agent off the cliff. SARSA learns the safer longer route because it factors in exploration cost. With $\epsilon \to 0$ both converge to the same optimum (S&B p. 132).
- **"Off-policy means you can use any behavior policy."** You can use any behavior policy *that visits every state–action pair infinitely often* (S&B p. 131). A purely greedy behavior policy can starve exploration and fail to converge.
- **"The max is over the policy's distribution over actions."** No — the max is over $\mathcal{A}(S_{t+1})$, ignoring the behavior policy entirely. This is what makes the target equivalent to one Bellman-optimality update.
- **"Q-learning has no maximization bias."** It does — using $\max_a Q(S_{t+1}, a)$ as an estimate of $\max_a q_*(s', a)$ is biased upward when $Q$ values are noisy (S&B §6.7, p. 134, "Maximization Bias and Double Learning"). Double Q-learning is the standard remedy.
- **"Q-learning is the same as one-step value iteration."** Conceptually similar, but value iteration uses the full distribution $p(s', r \mid s, a)$ in expectation; Q-learning uses a single sampled transition. The expectation appears only implicitly through repeated sampling.

**Boundary conditions:**

- **Terminal states:** $Q(\text{terminal}, \cdot) \equiv 0$. When $S_{t+1}$ is terminal, the update becomes $Q(S_t, A_t) \leftarrow Q(S_t, A_t) + \alpha[R_{t+1} - Q(S_t, A_t)]$.
- **Convergence:** With probability 1 to $q_*$ under (1) all state–action pairs visited infinitely often, and (2) Robbins–Monro step-size schedule (S&B p. 131). Notably, *unlike SARSA, the behavior policy need not converge to the greedy policy* — only the visitation requirement matters.
- **Greedy behavior policy degenerate case:** With $\epsilon = 0$ and a tie-breaking rule, Q-learning's target equals SARSA's target (because $A_{t+1} = \arg\max_a Q(S_{t+1}, a)$ then), and the two algorithms make identical updates (S&B Exercise 6.12).
- **Stochastic environments:** Q-learning still converges, but the maximization bias is more visible — the $\max_a Q$ term overestimates when there is real noise in transitions. CliffWalking is deterministic, so the bias shows up only through learning noise.

**Gymnasium connection:**

Like SARSA, Q-learning uses only `env.step()` / `env.reset()` — no model:

```python
env = gym.make("CliffWalking-v0")
Q = np.zeros((env.observation_space.n, env.action_space.n))
gamma, alpha, epsilon = 1.0, 0.5, 0.1

for episode in range(num_episodes):
    state, info = env.reset()
    done = False
    while not done:
        action = epsilon_greedy(Q, state, epsilon)
        next_state, reward, terminated, truncated, info = env.step(action)
        done = terminated or truncated
        bootstrap = 0.0 if done else max(Q[next_state])
        Q[state][action] += alpha * (reward + gamma * bootstrap - Q[state][action])
        state = next_state
```

Key contrasts with the SARSA loop:

1. **Only one action selection per step** — not two. The current `action` is chosen from `state`; the bootstrap uses `max(Q[next_state])`, not `Q[next_state][next_action]`. No `next_action` variable exists.
2. **Behavior decoupled from target.** You can change `epsilon_greedy` to any policy that visits all (state, action) pairs — uniform random exploration, Boltzmann exploration, even replay of an old trajectory — and Q-learning still converges to $q_*$. SARSA would learn a different $Q$ for each such behavior policy.
3. `max(Q[next_state])` is the maximum over the action axis of the Q-table. For Gymnasium's `Discrete` action spaces, this is `Q[next_state, :].max()` (a single NumPy reduction); for parameterized action spaces it would require an outer loop.
4. CliffWalking termination semantics: stepping into the cliff returns `terminated=False` and teleports the agent back to start with reward $-100$ — only reaching the goal sets `terminated=True`. Make sure the bootstrap convention matches: as long as `terminated or truncated` correctly identifies absorbing terminal states, the algorithm is correct.

**Reputable supplementary sources:**

- Watkins, C. J. C. H. (1989). *Learning from Delayed Rewards.* PhD thesis, King's College, Cambridge. (Original Q-learning thesis.)
- Watkins, C. J. C. H. and Dayan, P. (1992). *Q-learning.* Machine Learning, 8:279–292. (Convergence proof made rigorous.)
- Hasselt, H. van (2010). *Double Q-learning.* NeurIPS — the maximization-bias fix referenced in S&B §6.7.
- Gymnasium CliffWalking documentation: https://gymnasium.farama.org/environments/toy_text/cliff_walking/

---

## Prerequisite Dependency Graph

A reader should be able to absorb the lessons in any topological order of this
DAG. No cycles.

```
dp_policy_eval
   │
   ├──> dp_policy_improvement
   │       │
   │       └──> dp_value_iteration
   │              │
   │              ├──> td_sarsa
   │              │       │
   │              │       └──> td_q_learning
   │              │
   │              └──> td_q_learning
   │
   └──> mc_first_visit
           │
           └──> td_sarsa
```

Edges (`A -> B` means "B depends on A"):

| From | To |
|------|-----|
| `dp_policy_eval` | `dp_policy_improvement` |
| `dp_policy_eval` | `dp_value_iteration` |
| `dp_policy_eval` | `mc_first_visit` |
| `dp_policy_improvement` | `dp_value_iteration` |
| `dp_value_iteration` | `td_sarsa` |
| `dp_value_iteration` | `td_q_learning` |
| `mc_first_visit` | `td_sarsa` |
| `td_sarsa` | `td_q_learning` |

The graph has 6 nodes and 8 edges. A valid topological order (one of several):
`dp_policy_eval, dp_policy_improvement, dp_value_iteration, mc_first_visit, td_sarsa, td_q_learning`.
