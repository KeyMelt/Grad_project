# RL Expert Teaching Spec — `policies_values_bellman`

**Series position:** V-02 of the restructured RL concept-video curriculum
**Authored by:** RL Expert
**Date:** 2026-05-26
**Status:** Advisory — no gate decision required (UNREGISTERED_NEW_LESSON; no prior submission)
**Platform contract:** UNREGISTERED_NEW_LESSON. No entry in
`backend/concept_videos/specs.py` yet. A complete `LessonVideoSpec` is
proposed in §10 for Producer registration at Gate 8.
**Course restructure note:** V-02 covers original course-plan segments
(d) policies, (e) value functions, and (f) Bellman expectation equation —
formerly part of the archived `mdp_foundations` lesson. V-01 (`rl_mdp_core`,
already in the library) covers (a)–(c): RL motivation, MDP framework, return
$G_t$, transition probability. Concepts belonging to V-01 are assumed; concepts
belonging to V-03+ (`dp_policy_eval`, …) are **explicitly excluded** from this
spec.

---

## 1. Concept Definition and Why It Matters

### 1.1 What this video teaches

`policies_values_bellman` delivers three tightly-coupled ideas that together
complete the MDP framework and unlock every algorithm in the rest of the series:

1. **Policy** — $\pi(a \mid s)$ — the probability distribution the agent uses
   to choose actions in each state. Deterministic and stochastic policies are
   two cases of the same object. Normalization: $\sum_a \pi(a \mid s) = 1$
   for every $s$. (S&B §3.5, pp. 58–60.)
2. **Value functions** — $v_\pi(s)$ and $q_\pi(s, a)$ — the expected return
   from state $s$ (or from $(s, a)$) when the agent follows policy $\pi$
   thereafter. The state-value function answers "how good is this state under
   $\pi$?"; the action-value function answers "how good is taking $a$ in $s$
   and then following $\pi$?" (S&B §3.5, eq. (3.12) and (3.13), p. 58.)
3. **The Bellman expectation equation for $v_\pi$** — derived directly from
   the return recursion $G_t = R_{t+1} + \gamma G_{t+1}$ (planted in V-01):
   $$v_\pi(s) = \sum_{a} \pi(a \mid s) \sum_{s', r} p(s', r \mid s, a)\,
   \bigl[\,r + \gamma\, v_\pi(s')\,\bigr].$$
   This equation is the single most important relationship in the rest of the
   course. (S&B eq. (3.14), p. 59.)

### 1.2 Why this matters

Without policies, the agent has no decision-making structure. Without value
functions, the agent has no quantitative comparison between states or actions.
Without the Bellman equation, value functions remain undefined recursive
quantities with no computational handle — every DP method (V-03, V-04, V-05),
every MC method (V-06), and every TD method (V-07, V-08) is *some way of
solving or approximating the Bellman equation*. Producing this lesson with
academic rigor is therefore the load-bearing prerequisite for the entire
downstream pipeline. In particular, V-03 (`dp_policy_eval`, already produced)
takes the Bellman expectation equation derived here and turns it into an
iterative assignment rule:
$v_{k+1}(s) \leftarrow \sum_a \pi(a\mid s) \sum_{s',r} p(s',r\mid s,a)
[r + \gamma v_k(s')]$ — that hand-off must be foreshadowed explicitly in the
closing beat of this video.

---

## 2. Prerequisite Concepts and Series Position

### 2.1 Series DAG position

```
rl_mdp_core (V-01) ← already produced; provides S, A, r, p(s',r|s,a), G_t, γ
    │
    └──► policies_values_bellman (V-02)   ← THIS VIDEO
             │
             └──► dp_policy_eval (V-03)   ← already produced; assumes π, v_π, Bellman eq
                      │
                      ├──► dp_policy_improvement (V-04)
                      │         └──► dp_value_iteration (V-05)
                      └──► mc_first_visit (V-06)
                                └──► td_sarsa (V-07)
                                          └──► td_q_learning (V-08)
```

### 2.2 Prerequisites for this video (from V-01)

All of the following are V-01 outputs and may be used freely in V-02 without
re-introduction:

| Term | Established in V-01 | Notes |
|---|---|---|
| Agent, environment, interaction loop | Segment 1–2 | Reuse the canonical elf-on-FrozenLake visual. |
| State $s$, action $a$, reward $r$ | Segment 2 | Reuse the same color bindings — `STATE_COLOR`, `ACTION_COLOR`, `REWARD_COLOR`. |
| Markov property | Segment 2 | Do not re-derive; one sentence reminder is acceptable. |
| Four-argument dynamics $p(s', r \mid s, a)$ | Segment 3 | The Bellman equation uses this object directly. |
| Normalization $\sum_{s', r} p(s', r \mid s, a) = 1$ | Segment 3 | Cited when deriving Bellman; not re-derived. |
| Return $G_t = \sum_{k=0}^{\infty} \gamma^k R_{t+k+1}$ | Segment 4 | Used as the definition $v_\pi(s) = \mathbb{E}_\pi[G_t \mid S_t = s]$. |
| Recursive return $G_t = R_{t+1} + \gamma G_{t+1}$ | Segment 4 ("the recursion") | **This is the load-bearing identity** used to derive the Bellman equation. The narration must explicitly call this out: "Remember the recursion from V-01? We are about to take its expectation under a policy." |
| Discount factor $\gamma$ boundary cases | Segment 4 | Use $\gamma = 0.99$ consistently with V-01. |
| FrozenLake-v1 (`is_slippery=True`), holes={5,7,11,12}, goal=15, start=0 | Segment 3–4 | Canonical environment for the entire series. |
| `env.unwrapped.P[s][a]` four-tuple convention | Segment 3 CodeStepper | The Gymnasium API binding is unchanged. |

### 2.3 Concepts this video introduces (and must define inline)

| Term | Introduced here | Definition scope |
|---|---|---|
| Policy $\pi(a \mid s)$ | §3 of this video | Full probability-distribution definition; normalization $\sum_a \pi(a\mid s) = 1$ |
| Deterministic vs. stochastic policy | §3 of this video | Two cases of the same object; deterministic = one-hot $\pi$ |
| Equiprobable random policy | §3 of this video | $\pi(a \mid s) = 1/\lvert\mathcal{A}(s)\rvert$ for all $s$; canonical baseline policy |
| State-value function $v_\pi(s)$ | §4 of this video | $v_\pi(s) \doteq \mathbb{E}_\pi[G_t \mid S_t = s]$ |
| Action-value function $q_\pi(s, a)$ | §4 of this video | $q_\pi(s, a) \doteq \mathbb{E}_\pi[G_t \mid S_t = s, A_t = a]$ |
| Bellman expectation equation for $v_\pi$ | §5 of this video | **Derived**, not asserted, from $G_t = R_{t+1} + \gamma G_{t+1}$ |
| Bellman expectation equation for $q_\pi$ | §5 of this video (optional, time-permitting) | $q_\pi(s,a) = \sum_{s',r} p(s',r\mid s,a)[r + \gamma \sum_{a'} \pi(a'\mid s') q_\pi(s', a')]$ |
| Relationship $v_\pi(s) = \sum_a \pi(a\mid s) q_\pi(s, a)$ | §4 of this video | Brief; visual is the bar-stack diagram |
| Backup diagram (one-step lookahead) | §5 of this video | Two-level branching tree: state node → action nodes → (s', r) nodes |

### 2.4 Concepts this video must NOT introduce

The following belong to V-03 and later and must not appear in V-02 — not even
informally:

- **Iterative policy evaluation** (V-03). Do not show $v_{k+1}(s) \leftarrow \ldots$
  assignment form. The Bellman equation is presented here as an *equality* (a
  fixed-point property of $v_\pi$), not yet as an assignment rule. The closing
  forward-tease names V-03 but shows no V-03 equations.
- **Greedy policy / argmax** (V-04). Do not write $\arg\max_a q_\pi(s, a)$.
- **Optimal value $v_*$, optimal action-value $q_*$, optimal policy $\pi_*$**
  (V-05 and onward). Use $v_\pi$ and $q_\pi$ throughout — no asterisks.
- **Bellman optimality equation** (V-05). The expectation form (under a fixed
  $\pi$) is V-02. The optimality form (with $\max_a$) is V-05.
- **Monte Carlo sampling, TD targets, $\epsilon$-greedy** (V-06+).

**Enforcement:** the Script Writer must flag any phase in plan.md that reaches
for "best policy," "argmax," "value iteration," or "policy evaluation
algorithm" and replace with neutral expectation-equation language.

---

## 3. The Canonical Equations

### 3.1 Policy — S&B §3.5, p. 58

$$\pi(a \mid s) \;\doteq\; \Pr\bigl\{A_t = a \mid S_t = s\bigr\}$$

**Normalization** (S&B p. 58):

$$\sum_{a \in \mathcal{A}(s)} \pi(a \mid s) = 1 \quad \forall\, s \in \mathcal{S}$$

**Two cases:**

- **Stochastic policy:** $\pi(a \mid s)$ takes values strictly between 0 and 1
  for at least one $a$ in some $s$. The equiprobable random policy
  $\pi(a \mid s) = 1/|\mathcal{A}(s)|$ is the canonical example used in this
  video and in V-03.
- **Deterministic policy:** for each $s$, exactly one action $a^\dagger(s)$ has
  $\pi(a^\dagger \mid s) = 1$ and all others have $\pi(\cdot \mid s) = 0$.
  Often written $\pi(s) = a^\dagger$ as a shorthand, but the distribution form
  $\pi(a \mid s)$ is the canonical object (S&B p. 58 footnote).

**Acceptable variants in narration:**
- "the agent's behavior under $\pi$"
- "the probability the agent chooses $a$ when in $s$"
- "the agent's strategy"

**Banned variants (would cause downstream confusion):**
- "the optimal policy" (that is $\pi_*$, V-05)
- "the greedy policy" (that is the V-04 construct)
- "the policy that maximizes reward" (conflates policy with optimality)

### 3.2 State-value function — S&B eq. (3.12), p. 58

$$v_\pi(s) \;\doteq\; \mathbb{E}_\pi\bigl[\,G_t \;\big|\; S_t = s\,\bigr]
\;=\; \mathbb{E}_\pi\!\left[\,\sum_{k=0}^{\infty} \gamma^k R_{t+k+1} \;\big|\; S_t = s\,\right]$$

**Interpretation:** $v_\pi(s)$ is the expected total discounted future reward
the agent collects, starting from $s$ and acting according to $\pi$ forever
after. The expectation $\mathbb{E}_\pi$ is taken with respect to both the
policy's randomness ($\pi(a \mid s)$) and the environment's randomness
($p(s', r \mid s, a)$).

**Terminal-state boundary:** $v_\pi(s_{\text{terminal}}) \equiv 0$ for all
$s_{\text{terminal}} \in \mathcal{S}^+ \setminus \mathcal{S}$. There is no
return to collect from a state where the episode has already ended.
(S&B p. 55, terminal-state convention.)

### 3.3 Action-value function — S&B eq. (3.13), p. 58

$$q_\pi(s, a) \;\doteq\; \mathbb{E}_\pi\bigl[\,G_t \;\big|\; S_t = s,\, A_t = a\,\bigr]$$

**Interpretation:** $q_\pi(s, a)$ is the expected total discounted future
reward when the agent takes action $a$ in $s$ *once* (overriding $\pi$ for
that one step) and then follows $\pi$ forever after.

**Identity linking $v_\pi$ and $q_\pi$** (S&B p. 58, derived by conditioning
on $A_t$):

$$v_\pi(s) \;=\; \sum_{a \in \mathcal{A}(s)} \pi(a \mid s)\, q_\pi(s, a)$$

This identity is the algebraic bridge for the Bellman derivation in §3.4
and **must** be shown on-screen — it is one of the two factor expansions the
viewer needs to follow the derivation.

### 3.4 Bellman expectation equation for $v_\pi$ — S&B eq. (3.14), p. 59

**Final form** (this is the equation the rest of the series uses):

$$\boxed{\;v_\pi(s) \;=\; \sum_{a} \pi(a \mid s) \sum_{s', r} p(s', r \mid s, a)\,
\bigl[\,r + \gamma\, v_\pi(s')\,\bigr]\;}$$

**This equation MUST be derived on-screen, not asserted.** The derivation is
the centerpiece of the video. The five-step derivation:

| Step | Algebra | What appears on screen |
|---|---|---|
| 1 | $v_\pi(s) \doteq \mathbb{E}_\pi[G_t \mid S_t = s]$ | Definition of $v_\pi$ (from §3.2) |
| 2 | $= \mathbb{E}_\pi[R_{t+1} + \gamma G_{t+1} \mid S_t = s]$ | Substitute the return recursion (V-01 callback). |
| 3 | $= \sum_a \pi(a \mid s)\, \mathbb{E}_\pi[R_{t+1} + \gamma G_{t+1} \mid S_t=s, A_t=a]$ | Condition on the action $a$ — pull the policy out. **First sum: over actions.** |
| 4 | $= \sum_a \pi(a \mid s) \sum_{s', r} p(s', r \mid s, a)\, \bigl[\,r + \gamma\, \mathbb{E}_\pi[G_{t+1} \mid S_{t+1}=s']\,\bigr]$ | Condition on the next state and reward — pull the environment out. **Second sum: over (s', r).** |
| 5 | $= \sum_a \pi(a \mid s) \sum_{s', r} p(s', r \mid s, a)\, \bigl[\,r + \gamma\, v_\pi(s')\,\bigr]$ | Recognize $\mathbb{E}_\pi[G_{t+1} \mid S_{t+1}=s'] = v_\pi(s')$ — the recursion closes. |

**The "two sums" insight** is the conceptual payoff. The Script Writer must
make the viewer see that:
- **The outer sum (over $a$) is the agent's choice** — its randomness is
  controlled by $\pi$.
- **The inner sum (over $s', r$) is the environment's response** — its
  randomness is controlled by $p$.
- Together, $\pi \otimes p$ describes one full step of MDP dynamics.

This separation is the conceptual cure for the most common Bellman-equation
misconception (see §5, M-3).

### 3.5 Bellman expectation equation for $q_\pi$ — optional, time-permitting

If the segment timing allows, also include:

$$q_\pi(s, a) \;=\; \sum_{s', r} p(s', r \mid s, a)\,
\bigl[\,r + \gamma \sum_{a'} \pi(a' \mid s')\, q_\pi(s', a')\,\bigr]$$

**Pedagogical priority:** the $v_\pi$ Bellman equation is the mandatory
deliverable; the $q_\pi$ form is a nice-to-have only if the runtime budget
allows. If pacing is tight, omit it — V-04 will introduce $q_\pi$ Bellman as
part of the policy improvement derivation. Do not compress the $v_\pi$
derivation to make room for $q_\pi$.

### 3.6 Acceptable equation variants

The following are acceptable rewrites for narration variation but are NOT
acceptable as the canonical on-screen equation:

| Variant form | Status |
|---|---|
| $v_\pi(s) = \mathbb{E}_\pi[R_{t+1} + \gamma v_\pi(S_{t+1}) \mid S_t = s]$ | Acceptable as an intermediate step in the derivation. May appear on screen as Step 4-ish. Must be reduced to the explicit double sum before the final boxed reveal. |
| $v_\pi(s) = \sum_a \pi(a\mid s) q_\pi(s, a)$ | Acceptable as the linking identity. Not a substitute for the full Bellman equation. |
| $V(s) = \sum_a \pi(a\mid s) \sum_{s',r} p(s',r\mid s,a)[r + \gamma V(s')]$ | **Not acceptable** — uppercase $V$ without the $\pi$ subscript drops the policy dependence and conflates with the V-03 iterative estimate. Always use $v_\pi$ with the subscript. |
| $v_\pi(s) = \sum_{a, s', r} \pi(a\mid s)\, p(s',r\mid s,a)\,[r + \gamma v_\pi(s')]$ | **Not acceptable** — collapsing the two sums into one hides the "two sources of randomness" structure. The two separate sums are pedagogically load-bearing. |

---

## 4. Required Worked Examples and Environment

### 4.1 Environment

**FrozenLake-v1 (`is_slippery=True`) throughout the entire video.**
Identical configuration to V-01. No environment change.

Grid layout (standard Gymnasium 4×4):

```
 0  1  2  3
 4  5  6  7
 8  9 10 11
12 13 14 15
```

States: S=0 (start), H={5,7,11,12} (holes), G=15 (goal), all others ice.
Actions: {0=LEFT, 1=DOWN, 2=RIGHT, 3=UP}, $|\mathcal{A}(s)| = 4$ for all $s$.
Discount: $\gamma = 0.99$ (consistent with V-01).

### 4.2 Worked example A — Policy as arrow grid (Segment 2)

**Goal:** make $\pi(a \mid s)$ visible before any algebra.

Show two policies side by side on the same 4×4 grid:

**Policy 1 — deterministic "always RIGHT":**
Every state $s$ has one arrow pointing right with probability 1.
Visualize as a single thick arrow per cell, all pointing right,
in `POLICY_COLOR` (#A78BFA, purple, per the V-01 color binding).

**Policy 2 — equiprobable random:**
Every state $s$ has four arrows, one per action, each labeled with
"1/4" or visually depicted as four quarter-length arrows.
Visualize as four short arrows per cell, all in `POLICY_COLOR`.

The two policies on screen simultaneously is the visual cure for the
"policies are unique" misconception (see §5, M-1).

**Narration intent:** a policy is a *table* that says, for each state, how
likely the agent is to take each action. Not the best table — any table that
satisfies the normalization rule is a valid policy.

### 4.3 Worked example B — Value function as heatmap-grid (Segment 3)

**Goal:** make $v_\pi(s)$ visible as a numerical scalar attached to each state.

Show the 4×4 grid with a numerical value drawn inside each state cell.
Use `VALUE_COLOR` (#FACC15, yellow) for the value labels. Color each
cell with a heatmap shading proportional to its value (lighter = higher).

**Values to display:** the equiprobable-random-policy state-values for
FrozenLake-v1 (`is_slippery=True`) at $\gamma = 0.99$. These are the same
values V-03 computes by iterative policy evaluation, so this video should
**not** compute them step-by-step — they are presented as targets that
$v_\pi$ achieves at fixed-point, motivating why V-03 is needed to compute
them. Approximate values (Technical Validator must run to confirm exact
numbers under the chosen $\theta$):

| State | $v_\pi(s)$ approx | Notes |
|---|---|---|
| 0 (start) | ≈ 0.012 | Long path to goal, mostly random |
| 1 | ≈ 0.010 | |
| 2 | ≈ 0.019 | |
| 3 | ≈ 0.009 | |
| 4 | ≈ 0.015 | |
| 5 (hole) | 0 | Terminal |
| 6 | ≈ 0.039 | |
| 7 (hole) | 0 | Terminal |
| 8 | ≈ 0.033 | |
| 9 | ≈ 0.084 | |
| 10 | ≈ 0.138 | |
| 11 (hole) | 0 | Terminal |
| 12 (hole) | 0 | Terminal |
| 13 | ≈ 0.170 | |
| 14 | ≈ 0.434 | Adjacent to goal |
| 15 (goal) | 0 | Terminal |

**These values must be confirmed by the Technical Validator before any
on-screen number is committed to the scene.** See §11.

**Narration intent:** "Look at state 14, right next to the goal — its value
is highest because even random actions land at the goal often. Look at state
0, far from the goal — its value is tiny because the random walk almost never
makes it. The value function is the heatmap of *expected future success*."

### 4.4 Worked example C — Action-value grid (Segment 3.5, brief)

**Goal:** make $q_\pi(s, a)$ visible as four values per state.

For a single highlighted state — recommend **state 14** (high value, adjacent
to goal) — show the four action-values $q_\pi(14, \text{LEFT})$, $q_\pi(14,
\text{DOWN})$, $q_\pi(14, \text{RIGHT})$, $q_\pi(14, \text{UP})$ as four
labeled bars or as four numbers attached to the four edges of cell 14.
Color: `VALUE_COLOR`.

Then show the identity:
$$v_\pi(14) \;=\; \tfrac{1}{4}\bigl[q_\pi(14, \text{LEFT}) + q_\pi(14, \text{DOWN}) + q_\pi(14, \text{RIGHT}) + q_\pi(14, \text{UP})\bigr]$$

with the four numbers averaging to the $v_\pi(14)$ value already shown on
the heatmap. This is the **mandatory linking visual** between $v_\pi$ and
$q_\pi$.

**Narration intent:** "Each state has one value $v_\pi$ — but also four
action-values $q_\pi$, one per action. The policy averages the four
$q$-values into the single $v$-value, weighted by how often each action is
chosen."

### 4.5 Worked example D — Bellman derivation as a backup diagram (Segment 4)

**Goal:** ground the Bellman algebra in a concrete one-step lookahead tree.

**Use state 6 as the worked example** — already established in V-01 as the
canonical "interesting" state (it has the three-way 1/3 split under action
RIGHT and a hole successor).

**Stage 1 — backup diagram (visual-first, before any algebra):**

Build a two-level branching tree rooted at state 6:

```
                       v_π(6)
                          │
            ┌─────────┬───┴─────┬─────────┐
       π(L|6)    π(D|6)    π(R|6)    π(U|6)
            │         │         │         │
         (LEFT)    (DOWN)    (RIGHT)    (UP)
                              │
                ┌─────────────┼─────────────┐
          p(2|6,R)=1/3   p(7|6,R)=1/3  p(10|6,R)=1/3
            r=0,γv(2)    r=0,γv(7)=0   r=0,γv(10)
```

Show this as a Manim node-edge diagram. Action nodes in `ACTION_COLOR`
(orange); state nodes in `STATE_COLOR` (blue); leaf rewards in `REWARD_COLOR`
(green); transition-probability labels in `POLICY_COLOR` is **NOT correct
here** — transition probabilities are environment quantities, not policy
quantities. Use a neutral panel-text color (`CODE_ACCENT` or unlabeled) for
the $p$ labels. Reserve `POLICY_COLOR` for the $\pi$ labels above.

**Stage 2 — algebra derivation (the five-step substitution from §3.4):**

Animate the five steps of the derivation in sync with the backup diagram:

- Step 1: $v_\pi(s) \doteq \mathbb{E}_\pi[G_t \mid S_t=s]$ — show the root
  node lighting up.
- Step 2: substitute $G_t = R_{t+1} + \gamma G_{t+1}$ — visually mark one
  edge as "$R_{t+1}$" and the subtree below as "$G_{t+1}$".
- Step 3: condition on $A_t = a$, sum over actions — highlight the four
  action nodes; the equation grows $\sum_a \pi(a\mid s) \cdot (\ldots)$.
- Step 4: condition on $(S_{t+1}, R_{t+1})$, sum over $(s', r)$ — highlight
  the three transition branches under RIGHT; the equation grows
  $\sum_{s', r} p(s', r \mid s, a) \cdot (\ldots)$.
- Step 5: close the recursion — the leaf nodes get relabeled
  $v_\pi(s')$, and the boxed Bellman equation appears full-screen-solo.

**Stage 3 — numerical check on state 6:**

Plug the FrozenLake numbers into the Bellman equation for state 6 to
demonstrate the equality (Technical Validator must confirm):

$$v_\pi(6) \;=\; \tfrac{1}{4}\!\left[\sum_a \sum_{s',r} p(s',r\mid 6, a)
\bigl[r + 0.99\, v_\pi(s')\bigr]\right]
\;\approx\; 0.039$$

The right-hand side, computed from the heatmap values, should equal the
left-hand side (the heatmap value at state 6) up to small numerical error.
This is the visual proof that the Bellman equation is an **equality**, not
an assignment. The "value comes back the same" is the punchline.

### 4.6 Closing forward-tease to V-03 — Segment 5

**Mandatory closing beat:**

> "The Bellman equation is an equality — for the true $v_\pi$, the right
> side equals the left side. But what if you don't *know* $v_\pi$? What if
> you only have a guess? Next video: turn the equation into an algorithm.
> Set $v_{k+1}(s)$ equal to the right-hand side using your current guess
> $v_k$, sweep every state, repeat until nothing changes. The fixed point
> is $v_\pi$. That algorithm is called *policy evaluation*."

**Visual constraint:** the closing beat may show the V-02 boxed Bellman
equation with a subtle morph showing $v_\pi \to v_{k+1}$ on the left and
$v_\pi \to v_k$ on the right — but the morph itself must be brief
(≤ 1.5 s) and no V-03 algorithm pseudocode appears.

---

## 5. Common Misconceptions and Boundary Conditions

### 5.1 Misconceptions to address in this video

**M-1: "A policy is a function from states to actions."**

This is the deterministic-policy shorthand. The general definition is a
*distribution* $\pi(a \mid s)$. Even when the policy happens to be
deterministic, the canonical object is the distribution (one-hot for
deterministic, multi-valued for stochastic). Without the distribution
framing, the Bellman equation's outer sum over $a$ looks wrong.
(S&B §3.5 p. 58.)

**Defeat strategy:** show the deterministic and stochastic policies side by
side in Segment 2. Make the equiprobable random policy the working example
for the rest of the video — its non-trivial $\pi(a\mid s) = 1/4$ values force
the viewer to treat $\pi$ as a real distribution.

**M-2: "The value of a state is the reward it gives."**

This is the single most durable misconception in introductory RL. The value
of a state is the *expected future return* — a discounted sum of all rewards
collected from that state onward, averaged over both the policy and the
environment. The immediate reward $r$ at a transition is only the first term.

The boxed equation makes this explicit:
$v_\pi(s) = \mathbb{E}[r + \gamma v_\pi(s') + \ldots]$ — the $r$ on its own
is not $v_\pi(s)$.

**Defeat strategy:** during the heatmap reveal (Segment 3), explicitly call
out that *all* intermediate rewards in FrozenLake are 0, yet most states
have non-zero values. The values come from the *probability of eventually
reaching the goal*, not from immediate rewards. Pair this with a sample
narration line: "State 14 gives reward zero when you step on it. But its
value is 0.43 — because from state 14, random actions often land at the
goal. Value is about the future, not the present."

**M-3: "The Bellman equation has one sum (over next states)."**

The Bellman expectation equation has **two** sums: one over actions
($\sum_a \pi(a\mid s)$) and one over transitions ($\sum_{s', r} p(s', r\mid s, a)$).
The two sums correspond to two sources of randomness:

- **Policy randomness:** the agent's choice of action under $\pi$.
- **Environment randomness:** the environment's response under $p$.

Collapsing the two sums into one (e.g., $\sum_{a, s', r} \pi\, p \,[\ldots]$)
or omitting the policy sum altogether is a frequent error in poor textbook
treatments. It hides the structure that V-04 and V-05 will exploit (policy
improvement modifies the outer sum; value iteration takes the max over the
outer sum).

**Defeat strategy:** the backup diagram (Segment 4 Stage 1) makes the
two-level structure visible *before* the algebra. The two-level tree —
state → action nodes → (s', r) nodes — physically separates the two sums.
Then the algebra in Stage 2 puts a coordinate on each level. The visual is
the cure.

**M-4: "Deterministic policies don't need the sum over actions."**

Technically true (the sum collapses to a single non-zero term), but
*pedagogically dangerous*. Students who learn the Bellman equation only in
the deterministic case stumble on stochastic policies later — and on policy
iteration, where intermediate policies are usually stochastic ties.
(S&B p. 58, the distribution form is canonical.)

**Defeat strategy:** use the equiprobable random policy as the working
example. The sum over $a$ is nontrivial (four equal terms) and the viewer
sees it computed explicitly.

**M-5: "v_π and q_π are unrelated."**

They are tightly linked: $v_\pi(s) = \sum_a \pi(a\mid s) q_\pi(s, a)$, and
conversely $q_\pi(s, a) = \sum_{s', r} p(s', r\mid s, a)[r + \gamma v_\pi(s')]$.
Each can be recovered from the other given $\pi$ and $p$.
(S&B p. 58 — the two are defined back-to-back precisely to emphasize this.)

**Defeat strategy:** §4.4 (the action-value grid for state 14) is the
mandatory visual. The four $q$-values stack and average to the one
$v$-value.

**M-6: "The Bellman equation tells you how to update v."**

Not in this video. The Bellman equation here is an **equality** — a
fixed-point identity that the true $v_\pi$ satisfies. Turning it into an
assignment rule ($v_{k+1} \leftarrow \text{RHS}(v_k)$) is the V-03
contribution (iterative policy evaluation). The viewer must come away from
V-02 with the equation as a *characterization* of $v_\pi$, not yet as an
algorithm. (S&B §3.5 p. 59 presents the equation; §4.1 p. 74 turns it into
an update.)

**Defeat strategy:** the closing forward-tease (Segment 5) explicitly draws
the line between "equation" (V-02) and "algorithm" (V-03). The Stage 3
numerical check in Segment 4 — where the heatmap value at state 6 equals
the right-hand side of the Bellman equation when plugged in — reinforces
that this is a *consistency property*, not an update.

### 5.2 Boundary conditions the Script Writer must not shortcut

| Condition | Correct statement | Source |
|---|---|---|
| Terminal-state value | $v_\pi(s_{\text{terminal}}) \equiv 0$ for all $s_{\text{terminal}} \in \mathcal{S}^+ \setminus \mathcal{S}$. The heatmap must show 0 (not blank, not missing) at states 5, 7, 11, 12, and 15. | S&B §3.3 p. 55 + §3.5 p. 58 |
| Hole and goal both terminal | Both holes (rewards 0) and the goal (reward 1) have $v_\pi = 0$ because the *return from the terminal state* is zero, regardless of the reward earned *arriving* at it. The arriving reward is captured in the $r$ inside the predecessor state's Bellman expansion, not in $v_\pi$ at the terminal. | S&B p. 55 terminal convention |
| Policy normalization | $\sum_a \pi(a \mid s) = 1$ must be checked on every policy displayed. For the equiprobable policy, $4 \times 1/4 = 1$ — show this annotation. | S&B p. 58 |
| Dynamics normalization | $\sum_{s', r} p(s', r \mid s, a) = 1$ — already established in V-01, but cite again briefly during the Bellman derivation. | S&B eq. (3.3) p. 48 |
| Existence of $v_\pi$ | Guaranteed if either $\gamma < 1$ or eventual termination is guaranteed from all $s$ under $\pi$. FrozenLake with the equiprobable policy at $\gamma = 0.99$ satisfies both conditions. | S&B §4.1 p. 74 (boundary citation, do not present V-03 theorem) |
| The Bellman equation is an equality | The "=" sign in eq. (3.14) is an equality, not an assignment. The true $v_\pi$ satisfies it; iteration is V-03. | S&B p. 59 |
| Action set | $\mathcal{A}(s) = \{0, 1, 2, 3\}$ for all $s \in \mathcal{S}$ in FrozenLake. The action set does not depend on $s$ in this environment. (Some MDPs have state-dependent $\mathcal{A}(s)$; FrozenLake does not.) | Gymnasium FrozenLake docs |

---

## 6. Minimum Visual Obligations

### 6.1 Mandatory visual elements (all blocking — QA gates G57/G58 enforce)

| Segment | Required visual | Format |
|---|---|---|
| Seg 1 (V-01 recap) | Reuse V-01 FrozenLake grid; remind state, action, reward, $p$, $G_t$, recursion. Brief — ≤ 60 s. | Reuse `frozenlake_frame()` outputs from V-01; no new geometry |
| Seg 2 (policy) | **Arrow-grid for policy** — two side-by-side 4×4 grids: deterministic "all RIGHT" and equiprobable random. Arrows in `POLICY_COLOR`. | Per-cell `Arrow` mobjects; quarter-length arrows for the random policy |
| Seg 2 (policy) | Full-screen solo reveal of $\pi(a \mid s)$ definition with normalization $\sum_a \pi(a\mid s) = 1$; font_size = 48. | Per STYLE_BIBLE §33.2 |
| Seg 3 (value) | **Heatmap-grid for $v_\pi$** — single 4×4 grid with each state colored by value and numerical label inside. Holes = `PENALTY_COLOR`; goal = `REWARD_COLOR` border with value=0 label; ice cells gradient in `VALUE_COLOR`. | Color-mapped `Square` per cell + value `Text` in `VALUE_COLOR` |
| Seg 3 (value) | Full-screen solo reveal of $v_\pi(s) \doteq \mathbb{E}_\pi[G_t \mid S_t = s]$; font_size = 48. | Per STYLE_BIBLE §33.2 |
| Seg 3.5 (q) | **Action-value display for state 14** — four bars or four edge-labels showing $q_\pi(14, a)$ for $a \in \{\text{L,D,R,U}\}$. | `ActionBarChart` or per-edge `Text` |
| Seg 3.5 (q) | Linking identity $v_\pi(s) = \sum_a \pi(a\mid s) q_\pi(s, a)$ shown with arrow connecting the four $q$-bars to the single $v$-cell. | `TransformMatchingTex` + `Arrow` |
| Seg 4 (Bellman) | **Backup diagram (factor-tree) rooted at state 6** — two-level branching tree as described in §4.5 Stage 1. Action nodes in `ACTION_COLOR`; state nodes in `STATE_COLOR`; $\pi$ labels in `POLICY_COLOR`; $p$ labels in `CODE_ACCENT`. | Manim `VGroup` of nodes + edges |
| Seg 4 (Bellman) | **Five-step derivation animation** — each step appears in sync with the diagram lighting up. | `TransformMatchingTex` per step |
| Seg 4 (Bellman) | Full-screen solo reveal of the final boxed Bellman equation; font_size = 48; hold ≥ 2.0 s. | Per STYLE_BIBLE §33.2 |
| Seg 4 (Bellman) | Numerical consistency check at state 6: heatmap value ≈ RHS computed from neighbors. | Side-by-side LHS/RHS calculation |
| Seg 5 (forward-tease) | Caption naming V-03 and the iterative-assignment transformation, with a brief (≤1.5 s) morph of the boxed Bellman equation showing $v_\pi \to v_{k+1}, v_k$ on the appropriate sides. | Caption + brief `TransformMatchingTex` |

### 6.2 Color bindings for this video

Inherit V-01's palette exactly. New bindings for V-02 concepts:

| On-screen element | Color constant | Notes |
|---|---|---|
| Policy arrows / $\pi$ symbols / $\pi(a\mid s)$ labels | `POLICY_COLOR` (#A78BFA, purple) | Locked in V-01; mandatory here |
| State-value $v_\pi$ / value labels on cells / value heatmap shading | `VALUE_COLOR` (#FACC15, yellow) | Locked in V-01; mandatory here |
| Action-value $q_\pi$ labels and bars | `VALUE_COLOR` | $q$ is still a value quantity — same color as $v$, distinguished by the bar layout (four per state) |
| State labels (0–15), $s$, $s'$, $S_t$, $S_{t+1}$ | `STATE_COLOR` (#38BDF8) | V-01 inheritance |
| Action labels (LEFT/DOWN/RIGHT/UP), $a$, $A_t$, action nodes in backup diagram | `ACTION_COLOR` (#FB923C) | V-01 inheritance |
| Rewards $r$, $R_{t+1}$, reward labels at goal, "reward" text | `REWARD_COLOR` (#34D399, green) | V-01 inheritance — **the reward at the goal must be green, not yellow** (locked in V-01 production) |
| Holes (5, 7, 11, 12), penalty/done-True events | `PENALTY_COLOR` (#F87171) | V-01 inheritance |
| Transition probability labels on the backup diagram ($p(s'\mid 6, a)$) | `CODE_ACCENT` (#64748B, gray) | Environment quantities are neutral; do not co-opt `POLICY_COLOR` for them |
| Discount factor $\gamma$ | `VALUE_COLOR` | V-01 inheritance — $\gamma$ scales values |
| Equality "=" in the Bellman equation | white / default text | No special color; the equality is the punchline |

**Critical color rule (carried from V-01):** the *reward* at the goal square
is `REWARD_COLOR` (green). The *value* at any cell is `VALUE_COLOR` (yellow).
These two must never be the same color in the same frame. The goal cell shows
its reward (green "+1.0" label on entry) and its value (yellow "0.0" inside,
because terminal value is zero) using two different colors simultaneously —
this color pairing is itself a teaching device for misconception M-2.

### 6.3 STYLE_BIBLE §11 dynamics-function exception

The term "dynamics function" is permitted **only** when referring precisely to
the four-argument $p(s', r \mid s, a)$. For all other usage, prefer
"transition probability."

In this video the term "dynamics function" may appear at most twice:
1. Once, briefly, in the V-01 recap as a name for $p(s',r\mid s,a)$.
2. Once, in the Bellman derivation step 4, when conditioning on the
   environment response.

Everywhere else, use "transition probability," "environment response," or
just "$p$."

---

## 7. Narration Philosophy

### 7.1 Core principle (STYLE_BIBLE §29.2)

Every narration line must explain WHY what is happening matters, not describe
WHAT is on screen. The litmus test from V-01 still applies: remove the
visual — does the narration still make sense as standalone audio?

### 7.2 Per-segment narration intentions

**Segment 1 — V-01 recap:**
A one-minute reminder of state, action, reward, transition probability,
return, and the recursion $G_t = R_{t+1} + \gamma G_{t+1}$. Frame as
ingredients we are about to combine: "Last time, we built the kitchen.
Today, we cook."

**Segment 2 — Policy:**
Build the intuition that a policy is a *rule for choosing actions* — not the
best rule, just *a* rule. The agent could follow a great policy or a bad
policy. The Bellman equation will work the same regardless. Use the word
"strategy" as a synonym in narration to lower the cognitive cost; reserve
the technical word "policy" for the equations.

Sample narration register:
> "A policy is the agent's habits. Always go right. Or roll a four-sided die.
> Or anything in between. As long as the probabilities sum to one in every
> state, it is a valid policy. The question is not yet 'is it good?' — only
> 'what does it do?'"

**Segment 3 — Value functions:**
Build the intuition that value is a *number per state* (or per state-action
pair) saying "if I start here and stick with this policy, how much reward do
I expect, all in all?" The heatmap is the visual cure for the
"value = immediate reward" misconception. Hammer the point that all
intermediate rewards are zero, yet values are positive.

Sample narration register:
> "Look at state ten. The reward when you step on it is zero. But the value
> of state ten is fourteen percent. Why? Because from state ten, a random
> walk reaches the goal often enough that the *expected* future reward,
> discounted, is fourteen percent of a single goal. Value lives in the
> future, not the present."

**Segment 4 — Bellman derivation:**
This is the load-bearing segment. The narration must shepherd the viewer
through the algebra one step at a time. The key emotional beat is the
"recursion closes" moment in step 5 — the right-hand side contains $v_\pi$
again, the same object as the left-hand side.

Sample narration register (step 5):
> "And here is the magic. The expected return from the next state — that
> is, by definition, the value of the next state. So we substitute. Now the
> equation has $v_\pi$ on the left, and $v_\pi$ inside the sum on the right.
> The value function is the *fixed point* of this equation. Whatever $v_\pi$
> is, it must satisfy this identity."

**Segment 5 — Forward-tease:**
Land softly. Do not over-explain V-03 — just plant the seed.

Sample narration register:
> "This is an equation. Beautiful, but useless if you cannot solve it. Next
> video, we turn the equation into an algorithm — a way to compute $v_\pi$
> by sweeping the equation across every state, over and over, until it stops
> changing. That algorithm is the foundation of every value-based RL method
> you will see for the rest of this course."

### 7.3 Banned narration patterns for this video

In addition to the STYLE_BIBLE §30.2 global bans and the V-01 inheritance,
the following are specific to V-02:

- Do not say "the optimal policy" or "the best policy." This video evaluates
  a *fixed* policy. Optimality is V-04/V-05 territory.
- Do not say "value iteration" or "policy iteration." Both belong to V-05
  and V-04 respectively.
- Do not say "the Bellman equation tells you how to update $V$." It is an
  equality, not an assignment. Updates are V-03.
- Do not say "argmax." Greediness is V-04.
- Do not say "Q-value" without first saying "action-value function $q_\pi$."
  The shorthand is fine on the second mention but the first mention must
  give the full name + symbol.
- Do not call the equation just "Bellman's equation" without the
  qualifier — say "the Bellman expectation equation for $v_\pi$." V-05
  introduces a different Bellman equation (optimality form) and the viewer
  must learn to distinguish them.

---

## 8. Gymnasium Asset Requirements

### 8.1 Required PNG assets

Inherit V-01's required asset list with no additions:

```python
import gymnasium, os
asset_dir = os.path.join(os.path.dirname(gymnasium.__file__),
                         'envs', 'toy_text', 'img')
required = [
    'ice.png', 'stool.png', 'hole.png', 'goal.png',
    'elf_up.png', 'elf_down.png', 'elf_left.png', 'elf_right.png',
]
missing = [f for f in required if not os.path.exists(os.path.join(asset_dir, f))]
assert not missing, f"MISSING_ASSETS: {missing}"
```

If any asset is missing: stop; report MISSING_ASSETS to Producer; do not
substitute colored rectangles.

### 8.2 Asset usage per segment

| Segment | Asset(s) | Usage |
|---|---|---|
| Seg 1 (recap) | Full V-01 grid composition | Reuse `frozenlake_frame()` |
| Seg 2 (policy arrows) | Full tile set | Background grid; arrows are vector overlays in `POLICY_COLOR` |
| Seg 3 (heatmap) | Full tile set | Background grid; heatmap shading is `Square` overlays in `VALUE_COLOR` gradient |
| Seg 3.5 (q-grid) | State 14 highlighted | `elf_*` sprite at state 14 optional |
| Seg 4 (backup diagram) | State 6 tile + successor tiles (2, 7, 10) | Inset on right panel; backup diagram is the focus on left/center |
| Seg 5 (forward-tease) | Full grid | Brief return to the heatmap |

### 8.3 Method

Use `frozenlake_frame()` per-tile composition for all segments. The arrow-grid
and heatmap overlays are vector mobjects layered on top — do not regenerate
the grid sprites; reuse the V-01 production setup.

---

## 9. CodeStepper Requirements

### 9.1 Segments WITHOUT CodeStepper

Segments 1, 2, and 5 (recap, policy arrow-grid, forward-tease) must NOT use
a CodeStepper. These are geometry-first beats — code would distract.

### 9.2 The single CodeStepper: policy + value sampling (Segment 3 or Segment 4)

**One CodeStepper is mandatory**, placed at the point of maximum
mathematical-to-computational translation. Recommended placement: end of
Segment 3 (after the heatmap and the $v_\pi$ definition), as a bridge into
Segment 4's Bellman derivation.

**Code block (runnable Python, no pseudocode):**

```python
import gymnasium as gym
import numpy as np

env = gym.make("FrozenLake-v1", is_slippery=True)
n_states = env.observation_space.n        # 16
n_actions = env.action_space.n            # 4

# Equiprobable random policy: pi(a|s) = 1/4 for every state-action pair.
pi = np.ones((n_states, n_actions)) / n_actions
assert np.allclose(pi.sum(axis=1), 1.0)   # row sums = 1 (normalization)

# One step of the Bellman expectation equation at state 6, given a v_prev guess.
gamma = 0.99
v_prev = np.zeros(n_states)               # initial guess; in V-02 this is just the RHS evaluator
state = 6
v_new_6 = 0.0
for action in range(n_actions):
    for prob, next_state, reward, done in env.unwrapped.P[state][action]:
        v_new_6 += pi[state, action] * prob * (reward + gamma * v_prev[next_state])
print(f"RHS of Bellman at state 6 with v_prev=0: {v_new_6:.6f}")
```

**Expected output (Technical Validator must confirm):**
```
RHS of Bellman at state 6 with v_prev=0: 0.000000
```

(With `v_prev=0`, the RHS at state 6 is exactly 0 because all rewards from
state 6 are 0 except via state 15, which requires multi-step lookahead.
This is the *first iteration* — and the viewer is shown that one iteration
is not enough. That is the V-03 hand-off.)

**Cross-highlight matrix for CodeStepper (mandatory per STYLE_BIBLE §15.2):**

| Step index | Code line | Geometric target |
|---|---|---|
| 0 | `env = gym.make("FrozenLake-v1", is_slippery=True)` | Full grid reveal (already on canvas from Segment 3) |
| 1 | `pi = np.ones((n_states, n_actions)) / n_actions` | Arrow-grid overlay (equiprobable policy) |
| 2 | `assert np.allclose(pi.sum(axis=1), 1.0)` | "1/4 + 1/4 + 1/4 + 1/4 = 1" annotation at one cell |
| 3 | `gamma = 0.99` | $\gamma$ label flashes; value is locked in V-01 |
| 4 | `v_prev = np.zeros(n_states)` | Heatmap dims to all-zero; tease that this is just a *guess* |
| 5 | `for action in range(n_actions):` | Four action nodes pulse on state 6 |
| 6 | `for prob, next_state, reward, done in env.unwrapped.P[state][action]:` | The three transition branches pulse under one action |
| 7 | `v_new_6 += pi[state, action] * prob * (reward + gamma * v_prev[next_state])` | The boxed Bellman equation appears next to the code; each term in the equation is color-coded to the matching variable in the code |
| 8 | `print(f"...{v_new_6:.6f}")` | The number 0.000000 appears on screen at state 6, followed by the punchline: "One sweep is not enough. To converge, we need V-03." |

**Critical pedagogical note:** the code's `v_prev=0` and the resulting
`v_new_6=0` is the **bridge to V-03**, not a contradiction of the heatmap
shown in Segment 3. The heatmap shows the converged $v_\pi$; the code shows
one iteration starting from zero. The narration must explicitly connect
them: "The heatmap I just showed you is what happens after this code runs
thousands of times. Today, we are looking at the equation. Tomorrow, we run
the algorithm."

---

## 10. App Metadata Proposal (for `backend/concept_videos/specs.py`)

This video is not yet registered (`UNREGISTERED_NEW_LESSON`). The following
is a complete `LessonVideoSpec` entry for insertion into
`LESSON_VIDEO_SPECS` at Gate 8:

```python
"policies_values_bellman": LessonVideoSpec(
    lesson_id="policies_values_bellman",
    title="Policies, Value Functions, and the Bellman Expectation Equation",
    environment_name="FrozenLake",
    theory_equation=(
        r"\pi(a \mid s) \doteq \Pr\{A_t = a \mid S_t = s\};"
        r"\quad v_\pi(s) \doteq \mathbb{E}_\pi[G_t \mid S_t = s];"
        r"\quad v_\pi(s) = \sum_a \pi(a \mid s) \sum_{s', r} p(s', r \mid s, a)[r + \gamma v_\pi(s')]"
    ),
    worked_example=(
        "FrozenLake-v1 4x4 (is_slippery=True), gamma=0.99, equiprobable random policy "
        "pi(a|s) = 1/4. Five segments: (a) V-01 recap of states, actions, rewards, "
        "transition probability, return, and the recursion G_t = R_{t+1} + gamma * G_{t+1}; "
        "(b) policy as arrow-grid - two side-by-side 4x4 policies (deterministic 'all RIGHT' "
        "and equiprobable random) with normalization sum_a pi(a|s) = 1 demonstrated; "
        "(c) state-value heatmap on the 4x4 grid - states 5,7,11,12,15 at value 0 (terminal), "
        "state 14 highest at ~0.43 (adjacent to goal), state 0 lowest non-terminal at ~0.012; "
        "(c.5) action-value q_pi(14, a) for the four actions, averaging to v_pi(14) via "
        "v_pi(s) = sum_a pi(a|s) q_pi(s, a); (d) Bellman expectation equation derived from "
        "the V-01 recursion in five steps, anchored on a backup diagram rooted at state 6; "
        "numerical consistency check at state 6 (LHS = RHS = ~0.039); (e) forward-tease to "
        "V-03 by morphing the equation's '=' into an assignment '<-'."
    ),
    code_focus_lines=(
        "env = gym.make('FrozenLake-v1', is_slippery=True)",
        "pi = np.ones((n_states, n_actions)) / n_actions",
        "assert np.allclose(pi.sum(axis=1), 1.0)",
        "v_new_6 = 0.0",
        "for action in range(n_actions):",
        "    for prob, next_state, reward, done in env.unwrapped.P[6][action]:",
        "        v_new_6 += pi[6, action] * prob * (reward + 0.99 * v_prev[next_state])",
    ),
    misconception_to_prevent=(
        "A policy is a probability distribution pi(a|s), not a function from states to "
        "actions - deterministic policies are the special case where pi is one-hot. "
        "The value of a state is the EXPECTED FUTURE RETURN under pi, not the immediate "
        "reward - states with reward 0 still have positive values when the policy "
        "eventually reaches the goal. The Bellman expectation equation has TWO sums: "
        "one over actions (policy randomness) and one over (s', r) (environment "
        "randomness) - collapsing them hides the structure V-04/V-05 will exploit. "
        "The Bellman equation here is an EQUALITY (a fixed-point identity satisfied "
        "by the true v_pi), not an assignment rule - turning it into an iterative "
        "update is the V-03 (dp_policy_eval) contribution."
    ),
    takeaway_line=(
        "A policy pi(a|s) is the agent's strategy; v_pi(s) is the expected total "
        "discounted reward when following pi from s; and the Bellman expectation "
        "equation v_pi(s) = sum_a pi(a|s) sum_{s',r} p(s',r|s,a)[r + gamma v_pi(s')] "
        "is the fixed-point identity every value-based RL algorithm builds on."
    ),
    pacing_notes=(
        "Segment (a) V-01 recap: ~1:00 hard cap; reuse V-01 visuals; no new geometry.",
        "Segment (b) Policy as arrow-grid: full-screen solo of pi(a|s) definition "
        "(font_size=48, hold >=2.0 s); side-by-side deterministic vs. equiprobable; "
        "hold 3.0 s on the 'sum_a pi(a|s) = 1' annotation. ~3:30.",
        "Segment (c) Value heatmap: full-screen solo of v_pi(s) definition "
        "(font_size=48, hold >=2.0 s); cell-by-cell heatmap reveal taking 4-5 s; "
        "narration explicitly contrasts immediate reward 0 with positive value. ~4:00.",
        "Segment (c.5) Action-value: focused on state 14; four bars + linking identity; "
        "hold on the averaging arrow 2.5 s. ~2:00.",
        "Segment (d) Bellman derivation: backup diagram first (Stage 1, ~1:30); "
        "five-step derivation animation (Stage 2, ~3:30); numerical check at state 6 "
        "(Stage 3, ~1:00); full-screen solo of boxed Bellman equation (font_size=48, "
        "hold >=2.5 s). ~7:00.",
        "Segment (e) Forward-tease to V-03: caption + brief morph of '=' to '<-'; "
        "no V-03 equations. ~1:00. Final hold: 8.0 s on takeaway caption.",
    ),
    target_duration_label="19:00",
    theory_verification=(
        TheoryVerification(
            claim=(
                "A policy pi(a|s) is a probability distribution over actions "
                "conditioned on state, with sum_a pi(a|s) = 1 for every state. "
                "Deterministic policies are the special case where pi is one-hot."
            ),
            source_url="https://incompleteideas.net/book/the-book-2nd.html",
            validation_note=(
                "Sutton and Barto §3.5 p. 58: 'A policy is a mapping from states to "
                "probabilities of selecting each possible action.' Normalization is "
                "the definition of a probability distribution."
            ),
        ),
        TheoryVerification(
            claim=(
                "The state-value function v_pi(s) is the expected return from state s "
                "under policy pi: v_pi(s) = E_pi[G_t | S_t = s]. The action-value "
                "function q_pi(s, a) is the expected return from state s taking action "
                "a then following pi: q_pi(s, a) = E_pi[G_t | S_t = s, A_t = a]. "
                "They are linked by v_pi(s) = sum_a pi(a|s) q_pi(s, a)."
            ),
            source_url="https://incompleteideas.net/book/the-book-2nd.html",
            validation_note=(
                "Sutton and Barto §3.5 p. 58: v_pi defined as eq. (3.12); q_pi defined "
                "as eq. (3.13); linking identity derived by conditioning on A_t."
            ),
        ),
        TheoryVerification(
            claim=(
                "The Bellman expectation equation for v_pi is "
                "v_pi(s) = sum_a pi(a|s) sum_{s', r} p(s', r | s, a) [r + gamma v_pi(s')], "
                "derived by substituting the return recursion G_t = R_{t+1} + gamma G_{t+1} "
                "into the definition of v_pi and conditioning on (A_t, S_{t+1}, R_{t+1})."
            ),
            source_url="https://incompleteideas.net/book/the-book-2nd.html",
            validation_note=(
                "Sutton and Barto eq. (3.14) p. 59. The derivation is the standard one "
                "given on p. 59 - substitution of the return recursion (eq. 3.9 p. 55) "
                "and successive conditioning."
            ),
        ),
        TheoryVerification(
            claim=(
                "For FrozenLake-v1 (is_slippery=True) under the equiprobable random "
                "policy pi(a|s) = 1/4 with gamma=0.99, the state values are approximately "
                "v_pi(0) ~ 0.012, v_pi(6) ~ 0.039, v_pi(14) ~ 0.43, and v_pi(s) = 0 for "
                "s in {5, 7, 11, 12, 15} (the four holes and the goal, all terminal)."
            ),
            source_url="https://gymnasium.farama.org/environments/toy_text/frozen_lake/",
            validation_note=(
                "These are computed by iterative policy evaluation on env.unwrapped.P "
                "with theta=1e-10. Approximate values pending Technical Validator "
                "live re-computation. Exact values depend on theta and may differ in "
                "the trailing decimals."
            ),
            is_inference=True,
        ),
        TheoryVerification(
            claim=(
                "The Bellman expectation equation is an EQUALITY satisfied by the true "
                "v_pi at fixed point, not an iterative assignment rule. The iterative "
                "form v_{k+1}(s) <- sum_a pi(a|s) sum_{s',r} p(s',r|s,a)[r + gamma v_k(s')] "
                "is policy evaluation (S&B §4.1 p. 74), which is the subject of the next "
                "video (dp_policy_eval, V-03)."
            ),
            source_url="https://incompleteideas.net/book/the-book-2nd.html",
            validation_note=(
                "Sutton and Barto p. 59 presents eq. (3.14) as a property satisfied by "
                "v_pi. The iterative-assignment transformation appears in §4.1 p. 74 as "
                "eq. (4.5). The two are distinct and must be presented as such."
            ),
        ),
    ),
),
```

### 10.1 Field notes for the app team

- `theory_equation` contains three equations separated by semicolons:
  policy definition, value function definition, and the Bellman expectation
  equation. The backend should render these as three sequential equations
  in the study card. If single-equation only, prioritize the boxed Bellman
  equation.
- `target_duration_label` is "19:00" based on segment pacing notes:
  ~1:00 + ~3:30 + ~4:00 + ~2:00 + ~7:00 + ~1:00 + 0:30 buffer = ~19:00.
  Estimate only; Voice & BGM Agent narration timing governs the final.
- `code_focus_lines` contains only the CodeStepper lines from Segment 3 end.
  Segments 1, 2, 5 have no code.

### 10.2 Allowed expansions beyond minimum platform contract

The Producer may extend this `LessonVideoSpec` with the following fields if
the backend schema supports them, but they are **not required** for Gate 8:

- `prerequisite_lesson_ids = ("rl_mdp_core",)` — formal prerequisite link.
- `next_lesson_id = "dp_policy_eval"` — forward-link metadata for the app's
  "next video" suggestion.
- `figure_assets = (...)` — references to the rendered backup-diagram and
  heatmap as supplementary static figures in the study card.
- `quiz_questions = (...)` — knowledge-check items aligned with the
  misconceptions in §5 (M-2: "value is immediate reward" makes a good
  multiple-choice distractor).

---

## 11. Technical Validator Candidates

Before any Manim code is written, the Technical Validator should confirm the
following numerical claims from this spec by live Gymnasium computation:

| Claim | Expected value | Source |
|---|---|---|
| `env.action_space.n` for FrozenLake-v1 | 4 | Gymnasium FrozenLake docs |
| `env.observation_space.n` for FrozenLake-v1 4x4 | 16 | Gymnasium FrozenLake docs |
| Equiprobable policy normalization: `np.ones((16, 4)) / 4` row sums | All equal to 1.0 (within float tolerance) | Direct numpy |
| State-value $v_\pi$ at $s=0$, equiprobable random policy, $\gamma=0.99$, $\theta = 10^{-10}$ | ≈ 0.012 (confirm to ≥ 3 decimal places) | Iterative policy evaluation |
| State-value $v_\pi$ at $s=6$, same conditions | ≈ 0.039 | Same |
| State-value $v_\pi$ at $s=10$, same conditions | ≈ 0.142 | Same |
| State-value $v_\pi$ at $s=13$, same conditions | ≈ 0.170 | Same |
| State-value $v_\pi$ at $s=14$, same conditions | ≈ 0.434 | Same |
| State-value $v_\pi$ at terminal states $\{5, 7, 11, 12, 15\}$ | Exactly 0 | Boundary condition |
| Action-value $q_\pi(14, a)$ for $a \in \{0, 1, 2, 3\}$, same conditions | Four values whose mean is $v_\pi(14)$ | Linking identity check |
| Bellman LHS-RHS consistency at state 6: $v_\pi(6) - \sum_a \pi(a\mid 6) \sum_{s',r} p(s',r\mid 6, a)[r + 0.99 v_\pi(s')]$ | $\approx 0$ (within $\theta$) | Direct Bellman check at fixed point |
| CodeStepper output value $v_\text{new\_6}$ with `v_prev=0` | Exactly 0.0 | Direct computation; confirms "one iteration is not enough" |
| State 7 (`done=True`) in `env.unwrapped.P[6][2]` | True | V-01 inheritance |
| Hole states | $\{5, 7, 11, 12\}$ | V-01 inheritance |
| Goal state | 15 | V-01 inheritance |
| Start state | 0 | V-01 inheritance |

**Note:** the exact $v_\pi$ values above are this spec's best estimate. The
Technical Validator's live run is authoritative — if any value differs by
more than 0.005 from the table, this spec is updated, not the validator's
output.

---

## 12. "Do Not Oversimplify" Notes

These are pedagogical no-cuts. The Script Writer must include each item;
the QA Agent and the RL Expert at gates 4, 6, and 7 will check for them.

### 12.1 The Bellman equation MUST be derived, not asserted

The five-step derivation (§3.4) is mandatory. The viewer must see the chain:

$v_\pi(s) \xrightarrow{\text{def}} \mathbb{E}_\pi[G_t \mid \cdot] \xrightarrow{\text{recursion}} \mathbb{E}_\pi[R_{t+1} + \gamma G_{t+1} \mid \cdot] \xrightarrow{\text{cond. on } a} \sum_a \pi \cdot \mathbb{E}[\ldots] \xrightarrow{\text{cond. on } s', r} \sum_a \pi \sum_{s', r} p \cdot [\ldots] \xrightarrow{\text{recognize}} \sum_a \pi \sum_{s', r} p [r + \gamma v_\pi(s')]$

Skipping any step erases the connection between V-01's return recursion and
the Bellman equation — that connection is the conceptual payoff of the
entire video.

### 12.2 Policies MUST be presented as distributions, not action selectors

The deterministic-only framing causes durable confusion at V-04 and V-06.
Use the equiprobable random policy as the working example to force the
viewer to internalize the distributional structure.

### 12.3 The two sums MUST be presented separately

Do not collapse $\sum_a \pi \sum_{s', r} p$ into $\sum_{a, s', r} \pi p$.
The two sums correspond to two distinct sources of randomness (policy and
environment). The backup diagram (Segment 4 Stage 1) makes this visible
before the algebra; the algebra preserves the structure.

### 12.4 The Bellman equation is NOT an algorithm

The equation is presented as an equality / fixed-point identity. Iterative
assignment is V-03. Do not blur the line; the QA Agent will reject any
narration that uses "update" language for the V-02 Bellman equation.

### 12.5 Value is NOT immediate reward

The most durable RL misconception. The heatmap reveal must explicitly call
out that all intermediate FrozenLake rewards are zero, yet most non-terminal
states have positive values. Pair the visual with the verbal: "Value lives
in the future, not the present."

### 12.6 Terminal states have value zero

Hole states (5, 7, 11, 12) and the goal state (15) all have $v_\pi = 0$ on
the heatmap. The goal having $v_\pi = 0$ is **not** an error or a paradox
to be hand-waved — it is the terminal-state convention from S&B p. 55 and
its compatibility with the equation $v_\pi(s_T) = \mathbb{E}_\pi[G_t \mid
S_t = s_T] = 0$ because no rewards are collected after termination. The
reward of $+1$ at the goal lives in the *predecessor's* Bellman expansion,
not in $v_\pi(15)$ itself. State this clearly in narration to forestall the
"but the goal should be valuable!" question.

### 12.7 Foreshadow V-03, but do not pre-empt it

The closing forward-tease (Segment 5) names V-03 and the equation-to-algorithm
transformation, but no V-03 pseudocode, no $v_{k+1} \leftarrow \ldots$ written
out in full, no iteration counter, no convergence theorem. Plant the seed;
let V-03 grow it.

---

## 13. S&B Citation Index for This Spec

All citations are to printed page numbers of Sutton & Barto (2018) 2nd edition.

| Concept | S&B location |
|---|---|
| Policy $\pi(a \mid s)$ definition | §3.5, p. 58 |
| Policy normalization $\sum_a \pi(a \mid s) = 1$ | §3.5, p. 58 |
| Deterministic vs. stochastic policies | §3.5, p. 58 (footnote) |
| State-value function $v_\pi(s)$ — eq. (3.12) | §3.5, p. 58 |
| Action-value function $q_\pi(s, a)$ — eq. (3.13) | §3.5, p. 58 |
| Linking identity $v_\pi = \sum_a \pi\, q_\pi$ | §3.5, p. 58 (derived in text) |
| Bellman expectation equation for $v_\pi$ — eq. (3.14) | §3.5, p. 59 |
| Return recursion $G_t = R_{t+1} + \gamma G_{t+1}$ (V-01 inheritance) | §3.2, p. 55 (eq. 3.9) |
| Four-argument dynamics $p(s', r \mid s, a)$ (V-01 inheritance) | §3.1, p. 48 (eq. 3.2) |
| Backup diagram for $v_\pi$ | §3.5, p. 59 (Figure 3.4) |
| Terminal-state convention $v(s_T) = 0$ | §3.3, p. 55 |
| Existence and uniqueness of $v_\pi$ (boundary citation) | §4.1, p. 74 (do not present V-03 theorem) |

### 13.1 Supplementary sources

- Sutton & Barto errata page: http://incompleteideas.net/book/the-book-2nd.html
- Gymnasium FrozenLake docs: https://gymnasium.farama.org/environments/toy_text/frozen_lake/
- David Silver UCL course, Lecture 2 (MRPs and MDPs): https://www.davidsilver.uk/teaching/
  (covers policies and Bellman expectation equation at the same level of detail)
- Csaba Szepesvári, *Algorithms for Reinforcement Learning* (2010), §2.2:
  https://sites.ualberta.ca/~szepesva/rlbook.html
  (compact formal treatment of $v_\pi$ and $q_\pi$)

---

## 14. Knowledge Base Update Recommendation

After this video is produced and approved by the Producer at Gate 8, the
following new entry should be added to
`manim_service/concept_videos/docs/rl_knowledge_base.md`, slotting between
the existing "Transition Probability" entry (line 28) and the "Policy
Evaluation" entry (line 89):

**Proposed entry header:**
```
## Policies, Value Functions, and the Bellman Expectation Equation (policies_values_bellman)

**S&B Reference:** Chapter 3, Section 3.5 ("Policies and Value Functions"),
pages 58–60. Equation (3.12) for v_pi; equation (3.13) for q_pi;
equation (3.14) for the Bellman expectation equation.
```

Following sections (Key Equations, Intuition, Prerequisites, Common
Misconceptions, Boundary Conditions, Gymnasium Connection, Reputable
Supplementary Sources) follow the established structure of the existing
entries. The Producer should commission the knowledge base update as part
of Gate 8 sign-off; this spec provides the source material.

The Prerequisite Dependency Graph at the bottom of `rl_knowledge_base.md`
(currently lines 542–579) should be updated to include
`policies_values_bellman` as a node between the (implicit) `rl_mdp_core` and
`dp_policy_eval`. Edge: `policies_values_bellman -> dp_policy_eval`.

---

## 15. Spec Summary

**One-paragraph summary for the Script Writer's hook:**
This video gives the agent its first decision-making structure (a policy
$\pi$), its first quantitative measurement of state quality (the value
functions $v_\pi$ and $q_\pi$), and the equation that links them — the
Bellman expectation equation. The return recursion planted in V-01 is
expected under a policy to produce the Bellman equation, presented as a
fixed-point identity that the true $v_\pi$ satisfies. The closing beat
foreshadows V-03 (`dp_policy_eval`), where the equation becomes an
iterative algorithm.

**Spec author:** RL Expert (Claude)
**Spec date:** 2026-05-26
**Spec status:** Advisory — no gate decision. Ready for Script Writer
to draft `policies_values_bellman_plan.md`.
