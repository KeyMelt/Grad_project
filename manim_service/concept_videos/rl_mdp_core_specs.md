# RL Expert Teaching Spec — `rl_mdp_core`

**Series position:** V-01 of 10  
**Authored by:** RL Expert  
**Date:** 2026-05-24  
**Status:** Advisory — no gate decision required (new lesson, no prior submission)  
**Course restructure note:** This video combines original lessons 1–4
(`rl_intro`, `mdp_framework`, `rewards_returns`, `transition_prob`) into a
single consolidated foundation video. V-02 (`policies_values_bellman`) covers
lessons 5–7; concepts belonging to V-02 are **explicitly excluded** from this spec.

---

## 1. Concept Definition and Why It Matters

### 1.1 What this video teaches

`rl_mdp_core` delivers the four foundational ideas that every subsequent video
in the series assumes:

1. **The reinforcement learning problem** — an agent acts in an environment,
   receives reward signals, and must learn to act well without a supervisor
   telling it what to do. (S&B Ch. 1, §1.1–1.3, pp. 1–9.)
2. **The Markov Decision Process formalism** — a finite MDP is fully specified
   by a state set $\mathcal{S}$, an action set $\mathcal{A}$, and the
   four-argument dynamics function $p(s', r \mid s, a)$. The Markov property:
   the future depends on the present state alone, not on history. (S&B §3.1,
   pp. 47–53.)
3. **The return** — the agent's goal is to maximize the expected cumulative
   discounted return $G_t$, not just the immediate reward. (S&B §3.2–3.4,
   pp. 53–60.)
4. **Stochastic transition probability** — on slippery FrozenLake, choosing
   an action and arriving at the intended cell are two entirely different
   things. State 6, action RIGHT yields three equally probable outcomes, each
   1/3. (S&B §3.1, pp. 48–49; rl_knowledge_base.md `transition_prob` entry.)

### 1.2 Why this matters

Every DP, MC, and TD method in this series is an algorithm for computing or
approximating value functions over an MDP. Without a precise understanding of
$p(s', r \mid s, a)$ and $G_t$, none of those algorithms makes sense. This
video plants the vocabulary and intuition the rest of the series draws on.

---

## 2. Prerequisite Concepts and Series Position

### 2.1 Series DAG position

```
rl_mdp_core (V-01)                     ← this video; no prerequisites
    │
    └──► policies_values_bellman (V-02)
             │
             └──► dp_policy_eval (V-03)
                      │
                      ├──► dp_policy_improvement (V-04)
                      │         └──► dp_value_iteration (V-05)
                      └──► mc_first_visit (V-06)
                                └──► td_sarsa (V-07)
                                          └──► td_q_learning (V-08)
```

### 2.2 Prerequisites for this video

**None.** This is the opening video of the series. Assume zero prior RL
knowledge. The only prerequisite is comfort with basic probability (joint
probability, conditional probability, summation notation) at the level of an
introductory statistics course.

### 2.3 Concepts this video introduces (and must define inline)

| Term | First introduced here | Definition scope |
|---|---|---|
| agent / environment | §3.1 p. 47 | Full definition required |
| state $s$, action $a$, reward $r$ | §3.1 pp. 47–48 | Full definition required |
| Markov property | §3.1 p. 48 | State only — no need for history |
| $p(s', r \mid s, a)$ | §3.1 pp. 48–49 | Full four-argument form, normalization |
| episode, terminal state | §3.3 p. 55 | Episodic task definition |
| return $G_t$ | §3.2 p. 53 | Full discounted form |
| discount factor $\gamma$ | §3.2 p. 55 | Geometric series intuition + boundary γ=0 and γ→1 |
| episodic vs. continuing tasks | §3.3–3.4 pp. 55–60 | Core distinction, not exhaustive |

### 2.4 Concepts this video must NOT introduce

The following belong to V-02 (`policies_values_bellman`) and must not appear
in `rl_mdp_core` — not even informally:

- Policy $\pi(a \mid s)$ (introduced in V-02)
- State-value function $v_\pi(s)$ (introduced in V-02)
- Action-value function $q_\pi(s, a)$ (introduced in V-02)
- Bellman equation of any kind (introduced in V-02)
- Optimal policy / optimal value (introduced in V-02 foreshadow, fully in V-05)

**Enforcement:** the Script Writer must flag any phase in the plan.md that
reaches for policy, value function, or Bellman language and replace it with
the return $G_t$ framing only.

---

## 3. The Two Key Equations

### 3.1 The dynamics function — S&B eq. (3.2), p. 48

$$p(s', r \mid s, a) \;\doteq\; \Pr\!\bigl\{S_{t+1}=s',\, R_{t+1}=r \;\big|\; S_t=s,\, A_t=a\bigr\}$$

**Normalization constraint** (S&B p. 48):

$$\sum_{s' \in \mathcal{S}^+} \sum_{r \in \mathcal{R}} p(s', r \mid s, a) = 1
\quad \forall\, s \in \mathcal{S},\; a \in \mathcal{A}(s)$$

**Required sub-quantities to derive on-screen** (S&B pp. 48–49):

- State-transition probability: $p(s' \mid s, a) = \sum_{r \in \mathcal{R}} p(s', r \mid s, a)$
- This derivation must be shown as a summation collapse — not stated verbally only.

**What the equation means (narration intent):** $p$ is the environment's
complete answer to "if the agent is in state $s$ and takes action $a$, where
does the environment send it, and what reward does it give?" The agent has no
control over $p$; that is the environment's response law.

**First-time equation reveal:** mandatory full-screen solo per STYLE_BIBLE §33.2.
Font size 48. All other canvas elements at `OPACITY_SECONDARY` or `FadeOut`.

### 3.2 The return — S&B eq. (3.8)/(3.9), pp. 54–55

$$G_t \;=\; R_{t+1} + \gamma R_{t+2} + \gamma^2 R_{t+3} + \cdots \;=\; \sum_{k=0}^{\infty} \gamma^k R_{t+k+1}$$

**Recursive form** (S&B eq. 3.9, p. 55) — must be derived on-screen:

$$G_t \;=\; R_{t+1} + \gamma\, G_{t+1}$$

This recursion is the algebraic bridge to the Bellman equation in V-02. Plant
it here, name it "the recursion," and tell the viewer they will see it again.

**Episodic form (FrozenLake):** for a path of length $T$ ending at terminal
state $s_T$:

$$G_t \;=\; R_{t+1} + \gamma R_{t+2} + \cdots + \gamma^{T-t-1} R_T, \quad G_T = 0$$

**Concrete worked example** (to be animated, see §4):

For FrozenLake, path 0 → 4 → 8 → 9 → 10 → 14 → 15 (goal), all
rewards are 0 except $R$ at step $T$ = 1.0. With $\gamma = 0.99$:

$$G_0 = 0 + 0.99 \cdot 0 + 0.99^2 \cdot 0 + 0.99^3 \cdot 0 + 0.99^4 \cdot 0 + 0.99^5 \cdot 1 \approx 0.951$$

Show the computation term-by-term. The key insight: the reward at the end still
has value, just discounted by distance.

**Discount boundary cases — both must be addressed in narration:**

- $\gamma = 0$: the agent only cares about the next reward — pure myopic greedy.
- $\gamma \to 1$: all future rewards count equally. For FrozenLake (episodic
  with guaranteed termination), $\gamma = 1$ is valid. For infinite-horizon
  tasks without termination, $\gamma < 1$ is required to keep $G_t$ finite.

**First-time equation reveal:** mandatory full-screen solo per STYLE_BIBLE §33.2.

---

## 4. Required Worked Examples and Environments

### 4.1 Environment

**FrozenLake-v1 (`is_slippery=True`) throughout the entire video.** No other
environment is used. The 4×4 grid (16 states) keeps the visual small enough for
full labelling while providing rich enough structure for all four concepts.

Grid layout for reference (standard Gymnasium 4×4):

```
 0  1  2  3
 4  5  6  7
 8  9 10 11
12 13 14 15
```

State roles: S=0 (start), H={5,7,11,12} (holes), G=15 (goal),
all others are ice.

### 4.2 Worked example A — RL problem introduction (Segment 1)

**Goal:** make the viewer feel the RL problem before any formalism.

Show the elf on the grid attempting to reach the goal. Two failed attempts
(fall into holes) followed by a successful path. During each attempt, narration
names the tension: the agent must discover the path through trial and error —
no labels, no supervisor, only the reward signal at the end.

**Concrete path for success attempt:**
State sequence: 0 → 4 → 8 → 9 → 10 → 14 → 15. All intermediate rewards = 0.
Final reward = 1.0 on reaching state 15.

**Hole attempts (canonical):**
- Attempt 1: 0 → 1 → 5 (hole). Reward = 0.
- Attempt 2: 0 → 4 → 8 → 9 → 5 (hole due to slippage). Reward = 0.

**What is shown vs. not shown:** show the agent path and reward signal only.
Do not show any formulas in this segment. Formalism enters in Segment 2.

**Narration intent for this segment:** build the intuition that trial-and-error
is the only way forward when there is no teacher — and that the reward signal
is the only information the agent ever receives.

### 4.3 Worked example B — MDP state-action-reward structure (Segment 2)

**Goal:** ground the abstract MDP components in the concrete grid.

Reveal the grid with state indices visible. Demonstrate one step: the elf in
state 6, the agent chooses RIGHT, the environment responds. Before showing
the outcome, ask rhetorically: "What happens? Does the agent arrive where it
intended?"

Show the Markov property: the environment's response depends only on the
current state (6) and the action (RIGHT), not on how the agent reached state 6.
The full history before state 6 is irrelevant.

**Narration intent:** the Markov property is a simplifying assumption that makes
the problem tractable — not a claim about reality.

### 4.4 Worked example C — Stochastic transition probability, state 6 RIGHT (Segment 3)

**This is the canonical slippery example. Use it exactly.**

State 6, action RIGHT (`action index = 2`). Three outcomes from
`env.unwrapped.P[6][2]` (Technical Validator confirmed values):

| Outcome | Next state | Slippage direction | Probability | Reward | Done |
|---|---|---|---|---|---|
| Slides RIGHT (intended) | 7 | None | 1/3 | 0.0 | True (hole) |
| Slides UP (90° slip) | 2 | UP | 1/3 | 0.0 | False (ice) |
| Slides DOWN (90° slip) | 10 | DOWN | 1/3 | 0.0 | False (ice) |

**Sum check:** 1/3 + 1/3 + 1/3 = 1. The normalization constraint is satisfied.
This must be shown on screen.

**Note on hole at state 7:** the RIGHT outcome (state 7) has `done=True` because
state 7 is a hole. The UP outcome (state 2) and DOWN outcome (state 10) are both
ice; `done=False`.

**What NOT to claim:** do not say the successors are {7, 2, 5}. The correct
successors are {7, 2, 10}. The error {7, 2, 5} appeared in the original
`transition_prob_concept.py` and was corrected by the Technical Validator; this
spec uses the corrected values.

**ActionBarChart requirement:** show three bars, each at height 1/3, labeled
with next-state indices 7, 2, 10. Bars use `POLICY_COLOR` for probability fills
and `STATE_COLOR` for state labels. The "Σ = 1" annotation must be visible.

**Narration intent for state-6 RIGHT:** choosing an action and landing where you
intended are two completely different events on slippery ice. That gap between
intention and outcome is precisely what $p$ captures.

### 4.5 Worked example D — Return computation (Segment 4)

**Goal:** make $G_t$ concrete before introducing the symbolic form.

Use the successful path from example A: 0 → 4 → 8 → 9 → 10 → 14 → 15.
Rewards along path: [0, 0, 0, 0, 0, 1.0].

With $\gamma = 0.99$, animate the return computation term by term:

$$G_0 = 0 + 0.99 \cdot 0 + (0.99)^2 \cdot 0 + (0.99)^3 \cdot 0 + (0.99)^4 \cdot 0 + (0.99)^5 \cdot 1.0 \approx 0.951$$

Show the numeric accumulation: start at 0, add each discounted term,
the value stays near 0 until the final step contributes ≈ 0.951.

**Gamma animation:** show the effect of varying $\gamma$:
- $\gamma = 0.5$: $G_0 = (0.5)^5 = 0.031$ — the agent barely values a future reward 5 steps out.
- $\gamma = 0.99$: $G_0 \approx 0.951$ — the agent values it almost fully.
- $\gamma = 1.0$ (episodic only): $G_0 = 1.0$ — no discounting at all.

This gamma sweep is the visual teaching device for the discount boundary cases.

**Recursive form reveal:** after the explicit sum, derive:
$G_t = R_{t+1} + \gamma G_{t+1}$ by factoring out $\gamma$ from the tail.
Name this "the recursion." State explicitly that V-02 will use this identity.

---

## 5. Common Misconceptions and Boundary Conditions

### 5.1 Misconceptions to address in this video

These are drawn from the `rl_knowledge_base.md` `transition_prob` entry and
from S&B Ch. 1 and Ch. 3.

**M-1: "p(s',r|s,a) is the probability that the agent chooses action a."**

That is the policy $\pi(a \mid s)$ (introduced in V-02). The transition
function $p$ governs the *environment's response* after the action has already
been taken. The agent has no control over $p$.
(rl_knowledge_base.md; S&B p. 48: "the dynamics function $p$ defines the
environment's response".)

**Defeat strategy:** show two separate arrows at state 6 — one labeled
"agent chooses" pointing to the action, one labeled "environment responds"
pointing to the three probability branches. The visual separation of agency
and environment response is the cure.

**M-2: "A deterministic environment has p=1 for one outcome."**

True for deterministic environments (e.g., CliffWalking). FrozenLake with
`is_slippery=True` has three non-zero outcomes each with probability 1/3.
The probabilities are strictly between 0 and 1. Address this when building
the ActionBarChart in Segment 3.

**M-3: "RL is supervised learning with delayed feedback."**

RL has no supervisor and no labeled dataset. The reward signal is a scalar
number the agent discovers through interaction. There is no correct-action
label. (S&B §1.1, p. 2.)

**Defeat strategy:** the two failed-attempt beats in Segment 1 show the
agent receiving zero reward without any indication of *what it should have
done* — that absence of guidance is the RL problem.

**M-4: "The discount factor is needed to prevent infinite rewards."**

This is only required for infinite-horizon (continuing) tasks. FrozenLake is
episodic — it terminates. For episodic tasks, $\gamma = 1$ is perfectly valid
and keeps the return interpretation clean. The reason this series uses
$\gamma = 0.99$ is to smoothly generalize to continuing tasks, not because
$\gamma < 1$ is strictly required here.
(S&B §3.4, p. 57: "If there is a possibility of infinite sequences of time
steps... $\gamma < 1$ is required.")

**Address this briefly when introducing $\gamma$** to prevent the viewer from
forming the wrong mental model before reaching V-06.

**M-5: "The four-argument p and the state-transition probability p(s'|s,a) are the same."**

$p(s' \mid s, a) = \sum_r p(s', r \mid s, a)$ — the state-transition probability
marginalizes over the reward. For deterministic rewards (a unique $r$ per
$(s,a,s')$ triple, as in FrozenLake), they carry the same information, but
the four-argument form is the canonical MDP object.
(S&B p. 48; rl_knowledge_base.md.)

**Address this during the $p$ derivation in Segment 3** when showing the
summation collapse.

### 5.2 Boundary conditions the Script Writer must not shortcut

| Condition | Correct statement | Source |
|---|---|---|
| Terminal state successor | No transitions are taken *from* a terminal state. $G_T = 0$ by definition. | S&B §3.3 p. 55 |
| $\gamma = 1$ validity | Valid for episodic tasks with guaranteed termination. Not valid for continuing tasks unless $G_t$ is bounded by some other means. | S&B §3.4 p. 57 |
| $\gamma = 0$ limit | Reduces the agent to pure myopia: $G_t = R_{t+1}$ only. Pedagogically useful as a boundary check. | S&B §3.2 p. 55 |
| Normalization | $\sum_{s'} \sum_r p(s',r \mid s,a) = 1$ must hold for *all* $(s, a)$ pairs. FrozenLake's three 1/3 outcomes demonstrate this. | S&B eq. (3.3) p. 48 |
| Hole-state done flag | State 7 is a hole: `done=True` in `env.unwrapped.P[6][2]`. States 2 and 10 are ice: `done=False`. | Gymnasium FrozenLake docs |

---

## 6. Minimum Visual Obligations

### 6.1 Mandatory visual elements (all blocking — QA G57/G58 enforce)

| Segment | Required visual | Format |
|---|---|---|
| Seg 1 | FrozenLake grid with Gymnasium PNG sprites, two failure paths, one success path | PNG sprites via `frozenlake_frame()` or native render; no rectangles |
| Seg 2 | Grid with state indices 0–15 visible; elf sprite at state 6; action arrow pointing RIGHT | `frozenlake_frame()` per-tile composition |
| Seg 3 | Three outcome branches from state 6 RIGHT; `ActionBarChart` with three bars at 1/3 each; normalization sum Σ=1 | Chart + grid highlight; `STATE_COLOR` for states, `POLICY_COLOR` for probability bars |
| Seg 3 | Full-screen solo reveal of $p(s', r \mid s, a)$ equation; font_size = 48 | Per STYLE_BIBLE §33.2 |
| Seg 3 | Summation collapse: $p(s' \mid s, a) = \sum_r p(s',r \mid s,a)$ derived on-screen | `TransformMatchingTex` from four-argument to marginalized form |
| Seg 4 | Term-by-term return animation, path highlighted on grid as each reward is added | `ValueTracker` + `always_redraw` for the accumulation |
| Seg 4 | Full-screen solo reveal of $G_t$ equation; font_size = 48 | Per STYLE_BIBLE §33.2 |
| Seg 4 | Gamma sweep: three value bars at γ=0.5, γ=0.99, γ=1.0 showing $G_0$ | `ActionBarChart` with `VALUE_COLOR` bars |
| Seg 4 | Recursive form $G_t = R_{t+1} + \gamma G_{t+1}$ derived from factoring the infinite sum | `TransformMatchingTex` |
| Closing | Forward-tease to V-02: "Next, we give the agent a *strategy* for choosing actions — and ask what each state is worth." | Caption only; no V-02 equations on screen |

### 6.2 Color binding for this video

All colors follow STYLE_BIBLE §13. Specific bindings for `rl_mdp_core`:

| On-screen element | Color constant |
|---|---|
| State labels (0–15), `s`, `s'`, `S_t` | `STATE_COLOR` (#38BDF8) |
| Return value $G_t$, numeric return values | `VALUE_COLOR` (#FACC15) |
| Reward $r$, $R_{t+1}$, goal cell (state 15) | `REWARD_COLOR` (#34D399) |
| Holes (states 5, 7, 11, 12), done=True events | `PENALTY_COLOR` (#F87171) |
| Probability bars in ActionBarChart | `POLICY_COLOR` (#A78BFA) |
| Action arrow (RIGHT at state 6), action index $a$ | `ACTION_COLOR` (#FB923C) |
| $\gamma$ discount factor token | `VALUE_COLOR` (it modifies the return — treat as a value modifier) |

**Note on $\gamma$ color:** the discount factor token $\gamma$ appears inside
the return equation and scales $G_{t+1}$, which is a value quantity. Binding
it to `VALUE_COLOR` makes the color-geometry pairing consistent: every element
that contributes to the return uses `VALUE_COLOR`.

---

## 7. Narration Philosophy

### 7.1 Core principle (STYLE_BIBLE §29.2)

Every narration line must explain WHY what is happening matters, not describe
WHAT is on screen. The viewer can see the animation. The narrator adds meaning.

The litmus test: remove the visual. Does the narration still make sense as a
standalone audio explanation? If yes, it is doing its job.

### 7.2 Per-segment narration intentions

**Segment 1 — RL problem:**
Build the intuition that trial-and-error learning under a sparse reward signal
is both natural and genuinely hard. The elf failing is not a failure of the
video — it is the entire point. The viewer should feel the absence of guidance
as a real constraint, not a limitation of the example.

Sample narration register:
> "The elf has a goal. But no map, no coach, no hints. Just a number that
> appears — sometimes — when it reaches the end. *That number* is all it has."

**Segment 2 — MDP structure:**
Build the intuition that the Markov property is a gift: the environment's
full response is determined by where you are right now, not the winding path
that got you there. This makes the problem tractable.

Sample narration register:
> "The ice does not remember. Whatever happened before state 6 is gone —
> the only thing that determines what happens next is being in state 6 and
> choosing an action."

**Segment 3 — Transition probability:**
Build the intuition that intention and outcome are separated by the environment's
own randomness. The equation $p(s',r \mid s,a)$ is the complete description of
that separation.

Sample narration register:
> "The agent chose right. The environment heard that choice and responded with
> its own probability distribution. Three possibilities, equally likely.
> The agent will never know in advance which one lands."

**Segment 4 — Return and discount:**
Build the intuition that the agent is optimizing for a weighted sum of all
future rewards, not just the next one. The discount factor is the agent's
"patience" — how much a reward 5 steps away is worth to it today.

Sample narration register:
> "A reward five steps from now is worth something. Not as much as a reward
> right now — but something. That 'something' is controlled by gamma. With
> gamma equal to 0.99, arriving at the goal five steps later is worth ninety
> five cents on the dollar."

### 7.3 Banned narration patterns for this video

In addition to the STYLE_BIBLE §30.2 global bans, the following are specific
to `rl_mdp_core`:

- Do not introduce the word "policy" before Segment 2 ends. The Markov property
  and $p$ precede policy in the conceptual order.
- Do not say "value function" at any point in this video. It belongs to V-02.
- Do not say "Bellman equation" at any point in this video. It belongs to V-02.
- Do not describe the recursive form $G_t = R_{t+1} + \gamma G_{t+1}$ as "the
  Bellman equation" — it is the return recursion. The Bellman equation is what
  you get when you take expectations over this recursion under a policy.

---

## 8. Gymnasium Asset Requirements (STYLE_BIBLE §31)

### 8.1 Required PNG assets for FrozenLake-v1

All of the following must exist before any scene is rendered. Asset path:
`gymnasium/envs/toy_text/img/`

```python
import gymnasium, os
asset_dir = os.path.join(os.path.dirname(gymnasium.__file__),
                         'envs', 'toy_text', 'img')
required = [
    'ice.png',        # safe tiles (states 1,2,3,4,6,8,9,10,13,14)
    'stool.png',      # start tile (state 0)
    'hole.png',       # hole tiles (states 5,7,11,12)
    'goal.png',       # goal tile (state 15)
    'elf_up.png',     # agent sprite facing up
    'elf_down.png',   # agent sprite facing down
    'elf_left.png',   # agent sprite facing left
    'elf_right.png',  # agent sprite facing right
]
missing = [f for f in required if not os.path.exists(os.path.join(asset_dir, f))]
assert not missing, f"MISSING_ASSETS: {missing}"
print("ASSET_DIR:", asset_dir)
```

If any asset is missing: **stop; report MISSING_ASSETS to Producer; do not
substitute colored rectangles.**

### 8.2 Asset usage per segment

| Segment | Asset(s) | Usage |
|---|---|---|
| Seg 1 | `stool.png`, `ice.png`, `hole.png`, `goal.png`, `elf_right.png` | Full grid + agent traversal |
| Seg 2 | All tiles + `elf_right.png` | Elf at state 6, action arrow |
| Seg 3 | State 6 (ice tile) + `elf_right.png`, successor state tiles (7=hole, 2=ice, 10=ice) | Outcome branch animation |
| Seg 4 | `stool.png` → `ice.png` × 4 → `goal.png` path | Return computation path highlight |

### 8.3 Method

Use `frozenlake_frame()` per-tile composition for all segments that animate
individual tiles. Use the native Gymnasium `rgb_array` render only if a flat,
static grid reveal is needed.

Wrap all `ImageMobject` instances in the soft container per STYLE_BIBLE §14.

---

## 9. CodeStepper Requirements

### 9.1 Segments WITHOUT CodeStepper

All of Segments 1–3a (RL problem intro, MDP structure, agent-environment loop)
must NOT use a CodeStepper. These are geometry-first, intuition-building beats.
Code would distract from the conceptual teaching at this stage.

**Rationale:** the rl_intro-equivalent content in Segment 1 is entirely
observational — an agent interacting with an environment. Showing code at this
stage plants the wrong model: "RL is a code thing" instead of "RL is a
mathematical framework for decision-making."

### 9.2 The single CodeStepper: transition probability segment (Segment 3b)

**One CodeStepper is mandatory** in Segment 3b, showing `env.unwrapped.P`
inspection. This is the moment when the abstract equation $p(s', r \mid s, a)$
gets grounded in a concrete Gymnasium API call.

**Code block (runnable Python, no pseudocode):**

```python
env = gym.make("FrozenLake-v1", is_slippery=True)
for prob, next_state, reward, done in env.unwrapped.P[6][2]:
    print(f"prob={prob:.3f}  next_state={next_state}  reward={reward}  done={done}")
```

**Expected output (Technical Validator must confirm these values):**
```
prob=0.333  next_state=10  reward=0.0  done=False
prob=0.333  next_state=7   reward=0.0  done=True
prob=0.333  next_state=2   reward=0.0  done=False
```

**Note:** the tuple order in Gymnasium's `P[s][a]` list is
`(transition_prob, next_state, reward, done)`. The variable name `prob` in
the loop matches the `transition_prob` semantics. The Script Writer must
use these exact variable names in the code panel.

**Cross-highlight matrix for CodeStepper (mandatory per STYLE_BIBLE §15.2):**

| Step index | Code line | Geometric target |
|---|---|---|
| 0 | `env = gym.make("FrozenLake-v1", is_slippery=True)` | Full FrozenLake grid reveal (already on canvas) |
| 1 | `for prob, next_state, reward, done in env.unwrapped.P[6][2]:` | State 6 cell highlights; action RIGHT arrow pulses |
| 2 | `print(f"prob={prob:.3f} ...")` — first iteration (next_state=10) | State 10 cell highlights; bar for 1/3 appears on ActionBarChart |
| 2 | `print(...)` — second iteration (next_state=7) | State 7 cell highlights (hole, `PENALTY_COLOR`); second bar appears |
| 2 | `print(...)` — third iteration (next_state=2) | State 2 cell highlights; third bar appears; Σ=1 annotation appears |

---

## 10. App Metadata Proposal (for `backend/concept_videos/specs.py`)

This video is not yet registered. The following is a complete `LessonVideoSpec`
entry for insertion into `LESSON_VIDEO_SPECS`:

```python
"rl_mdp_core": LessonVideoSpec(
    lesson_id="rl_mdp_core",
    title="Reinforcement Learning and the MDP Framework",
    environment_name="FrozenLake",
    theory_equation=(
        r"p(s', r \mid s, a) \doteq \Pr\{S_{t+1}=s', R_{t+1}=r \mid S_t=s, A_t=a\};"
        r"\quad G_t = R_{t+1} + \gamma R_{t+2} + \gamma^2 R_{t+3} + \cdots"
    ),
    worked_example=(
        "FrozenLake-v1 4×4 (is_slippery=True) throughout. "
        "Four segments: (a) two failed elf paths and one success path "
        "(0→4→8→9→10→14→15, reward 1.0) to motivate the RL problem; "
        "(b) state indices 0–15 revealed, Markov property stated via state 6; "
        "(c) state 6 action RIGHT — three slippery outcomes {10,7,2} each "
        "probability 1/3, normalization Σ=1 shown on ActionBarChart, "
        "transition equation p(s',r|s,a) given full-screen solo reveal; "
        "(d) return G_0 computed term-by-term along the success path with γ=0.99 "
        "giving G_0≈0.951, gamma sweep at γ∈{0.5,0.99,1.0}, "
        "recursive form G_t = R_{t+1} + γG_{t+1} derived by factoring."
    ),
    code_focus_lines=(
        "env = gym.make('FrozenLake-v1', is_slippery=True)",
        "for prob, next_state, reward, done in env.unwrapped.P[6][2]:",
        "    print(f'prob={prob:.3f}  next_state={next_state}  reward={reward}  done={done}')",
    ),
    misconception_to_prevent=(
        "p(s',r|s,a) is the environment's response law, not the probability of "
        "choosing action a (that is the policy π, introduced in the next video). "
        "RL is not supervised learning with delayed feedback — there is no supervisor "
        "and no correct-action label. The discount factor γ<1 is required only for "
        "infinite-horizon continuing tasks; episodic tasks like FrozenLake can use γ=1."
    ),
    takeaway_line=(
        "A Markov Decision Process is the environment's contract: from any state "
        "and action, p tells you where you land and what reward you get. "
        "The agent's goal is to maximize G_t — the discounted sum of all future rewards."
    ),
    pacing_notes=(
        "Segment (a) — RL motivation: hold 3.5 s on first grid reveal; "
        "hold 3.5 s after each failed attempt; no formalism, pure intuition. ~4:30.",
        "Segment (b) — MDP structure: reveal state indices once; state Markov "
        "property with one example; do not enumerate all transitions. ~3:00.",
        "Segment (c) — Transition probability: full-screen solo p equation first "
        "(font_size=48, hold ≥2.0 s); then three-branch animation + ActionBarChart; "
        "then CodeStepper. Hold on Σ=1 bar chart before code panel enters. ~6:30.",
        "Segment (d) — Return: full-screen solo G_t equation first (font_size=48, "
        "hold ≥2.0 s); term-by-term path animation; gamma sweep; recursive form. ~6:00.",
        "Closing: forward-tease V-02 by name; no V-02 equations on screen. ~1:00.",
        "Final hold: 8.0 s on takeaway caption. Maintain full duration.",
    ),
    target_duration_label="21:00",
    theory_verification=(
        TheoryVerification(
            claim=(
                "The RL problem is characterized by the agent–environment interaction "
                "loop and the reward hypothesis: all goals can be described as "
                "maximizing expected cumulative reward. RL is distinct from supervised "
                "and unsupervised learning."
            ),
            source_url="https://incompleteideas.net/book/the-book-2nd.html",
            validation_note=(
                "Sutton and Barto Chapter 1, §1.1–1.3 (pp. 1–9): agent-environment "
                "loop defined p. 47; reward hypothesis p. 53; contrast with supervised "
                "learning p. 2."
            ),
        ),
        TheoryVerification(
            claim=(
                "A finite MDP is defined by (S, A, p) where p(s',r|s,a) is the "
                "four-argument dynamics function satisfying normalization "
                "Σ_{s'}Σ_r p(s',r|s,a)=1 for all (s,a)."
            ),
            source_url="https://incompleteideas.net/book/the-book-2nd.html",
            validation_note=(
                "Sutton and Barto §3.1 pp. 47–53: dynamics function p defined as "
                "eq. (3.2) p. 48; normalization as eq. (3.3) p. 48; Markov property "
                "pp. 48–49."
            ),
        ),
        TheoryVerification(
            claim=(
                "The return is G_t = Σ_{k≥0} γ^k R_{t+k+1} with recursive form "
                "G_t = R_{t+1} + γG_{t+1}. For FrozenLake path 0→4→8→9→10→14→15 "
                "with γ=0.99, G_0 = (0.99)^5 × 1.0 ≈ 0.951."
            ),
            source_url="https://incompleteideas.net/book/the-book-2nd.html",
            validation_note=(
                "Sutton and Barto §3.2–3.4 pp. 53–60: return G_t eq. (3.8) p. 55; "
                "recursive form eq. (3.9) p. 55; episodic vs. continuing §3.3–3.4. "
                "Numeric value (0.99)^5 = 0.9509803... ≈ 0.951 — recommend Technical "
                "Validator confirm via live computation."
            ),
            is_inference=True,
        ),
        TheoryVerification(
            claim=(
                "FrozenLake-v1 is_slippery=True: state 6, action RIGHT (index 2) "
                "yields exactly three transitions — to states {10, 7, 2} each with "
                "probability 1/3, reward 0.0, done=True only for state 7 (hole). "
                "Sum of probabilities = 1."
            ),
            source_url="https://gymnasium.farama.org/v0.26.3/environments/toy_text/frozen_lake/",
            validation_note=(
                "Confirmed by Gate 2 Technical Validator via live Gymnasium: "
                "env.unwrapped.P[6][2] = [(0.333,10,0.0,False),(0.333,7,0.0,True),"
                "(0.333,2,0.0,False)]. Corrected from erroneous {7,2,5} in prior "
                "reference scene transition_prob_concept.py."
            ),
            is_inference=False,
        ),
    ),
),
```

### 10.1 Field notes for the app team

- `theory_equation` contains both equations for the video separated by
  semicolons. The app backend renders this as two equations displayed
  sequentially in the study card. If the backend renders only one equation
  per field, split into two separate fields or use only the $p$ equation
  (the $G_t$ form is standard and can be rendered from LaTeX).
- `target_duration_label` is "21:00" based on segment pacing notes:
  ~4:30 + ~3:00 + ~6:30 + ~6:00 + ~1:00 = ~21:00. This is an estimate;
  the Voice & BGM Agent's narration timing governs the final duration.
- `code_focus_lines` contains only the CodeStepper lines (Segment 3b).
  Segments 1–2 have no code; the app should not display code lines for
  those segments.

---

## 11. Technical Validator Candidates

Before any Manim code is written, the Technical Validator should confirm the
following numerical claims from this spec:

| Claim | Expected value | Source |
|---|---|---|
| `env.unwrapped.P[6][2]` tuple list | `[(1/3, 10, 0.0, False), (1/3, 7, 0.0, True), (1/3, 2, 0.0, False)]` (order may vary) | Gymnasium FrozenLake-v1 is_slippery=True |
| Normalization: sum of probabilities for P[6][2] | 1.0 | Computed from above |
| Return G_0 for path [0,0,0,0,0,1.0] at γ=0.99 | (0.99)^5 × 1.0 = 0.9509900498999999 ≈ 0.951 | Direct computation (TV-confirmed 2026-05-24) |
| Return G_0 for same path at γ=0.5 | (0.5)^5 × 1.0 = 0.03125 | Direct computation |
| Return G_0 for same path at γ=1.0 | 1.0 | Direct computation |
| Hole states in 4×4 FrozenLake | {5, 7, 11, 12} | Gymnasium FrozenLake docs |
| Goal state | 15 | Gymnasium FrozenLake docs |
| Start state | 0 | Gymnasium FrozenLake docs |
| State 7 done flag | True (it is a hole) | env.unwrapped.P confirmation |

---

## 12. S&B Citation Index for This Spec

All citations are to printed page numbers of Sutton & Barto (2018) 2nd edition.

| Concept | S&B location |
|---|---|
| RL as third ML paradigm | §1.1, p. 2 |
| Agent-environment interaction loop | §3.1, pp. 47–48 |
| Markov property | §3.1, pp. 48–49 |
| $p(s',r \mid s,a)$ definition — eq. (3.2) | §3.1, p. 48 |
| Normalization of $p$ — eq. (3.3) | §3.1, p. 48 |
| State-transition probability — eq. (3.4) | §3.1, p. 49 |
| Reward signal motivation | §3.2, pp. 53–54 |
| Return $G_t$ — eq. (3.8) | §3.2, p. 55 |
| Recursive return — eq. (3.9) | §3.2, p. 55 |
| Discount factor $\gamma$ boundary cases | §3.2, pp. 54–55 |
| Episodic vs. continuing tasks | §3.3–3.4, pp. 55–60 |
| $G_T = 0$ for terminal states | §3.3, p. 55 |
| $\gamma = 1$ requires episodic/finite sums | §3.4, p. 57 |
