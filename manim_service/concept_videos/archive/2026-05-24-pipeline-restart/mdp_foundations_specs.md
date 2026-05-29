# RL Expert Teaching Spec — mdp_foundations

**lesson_id:** `mdp_foundations`
**Title:** MDP Foundations: From States to the Bellman Equation
**S&B reference:** Chapter 3 in full — §3.1 (agent–environment interface, Markov property, dynamics `p`, pp. 47–53), §3.2 (goals and rewards, reward hypothesis, p. 53), §3.3 (returns, episodic vs. continuing, discounting, pp. 54–57), §3.4 (unified episodic/continuing notation, pp. 57–58), §3.5 (policies and value functions, the Bellman expectation equation, pp. 58–63). Note the **+22 PDF offset** (printed p. N = PDF p. N+22).
**RL Expert status:** DRAFT — advisory spec only. No gate verdict issued.
**Date:** 2026-05-22
**Platform contract:** `UNREGISTERED_NEW_LESSON` (no `specs.py` entry yet — proposal in §App-metadata below)

> **Merged-foundation note.** This single video replaces six former lessons
> (`mdp_framework`, `rewards_returns`, `transition_prob`, `policies`,
> `value_functions`, `bellman_equations`) per explicit user directive. It teaches
> all of S&B Chapter 3 at **unblocking depth** — one worked beat per segment, not
> six full lessons concatenated. Hard production constraint: **30-minute ceiling.**

---

## 1. Concept definition and why it matters

A **finite Markov Decision Process (MDP)** is the formal object that gives every
RL idea a mathematical home. After `rl_intro`, the learner knows the
agent–environment loop *informally* (agent observes, acts, gets reward, repeats).
This video supplies the formalism that the entire DP → MC → TD track is built on:

> An environment is the tuple (𝒮, 𝒜, `p(s',r|s,a)`). The agent's behaviour is a
> policy π(a|s). The agent optimizes the **discounted return** G_t. Value
> functions v_π and q_π measure expected return under π. The **Bellman
> expectation equation** ties each state's value recursively to its successors'
> values — and that recursion *is* the body of the policy-evaluation loop the
> learner meets next.

**Why it matters — the foundation chain.** Each link feeds the next, and the last
link is the literal prerequisite of `dp_policy_eval`:

```
states/actions (a)  →  rewards/returns G_t (b)  →  dynamics p (c)
        →  policies π (d)  →  value functions v_π, q_π (e)
        →  Bellman expectation equation for v_π (f)  →  dp_policy_eval
```

A learner who skips this video meets `v_π(s)`, `π(a|s)`, `p(s',r|s,a)`, `γ`,
`G_t`, and `env.unwrapped.P` all undefined in the very first DP video. This
video closes that entire gap.

**Scope discipline (do not exceed):** This video is a *characterization*, not an
*algorithm*. It states what v_π **is** and derives the equation it **satisfies**.
It does NOT iterate, sweep, or converge anything — that is `dp_policy_eval`. It
does NOT introduce optimality (v_*, q_*, the Bellman *optimality* equation) — that
is the DP videos. Holding this line is what keeps the video under 30 minutes.

---

## 2. Learner entry state and series position

**Series position:** Wave 1, **V-02**, between `rl_intro` (V-01, PRODUCED) and
`dp_policy_eval` (V-03, PRODUCED). It is the only remaining Wave 1 production.

```
rl_intro ──► mdp_foundations ──► dp_policy_eval ──► (all of Wave 2)
```

**The learner has just completed:** `rl_intro`. They can now:
- Describe the agent–environment interaction loop informally (state → action → reward → repeat).
- Recognize FrozenLake-v1 visually: the elf, holes, the goal, +1 reward on reaching the goal.
- State the *goal* of RL — maximize cumulative reward — without yet a formula for "cumulative reward."

**They cannot yet (this video teaches):**
- Any mathematical definition of state set 𝒮, action set 𝒜, the Markov property, the dynamics `p`, the return G_t, discounting γ, a policy π, a value function v_π/q_π, or the Bellman expectation equation.
- How to read `env.unwrapped.P[s][a]` as the realization of S&B's four-argument `p`.

**Prerequisite-DAG compliance:** every term introduced here is either defined in
this video or already established in `rl_intro`. No term from a *later* lesson
(no iteration, no max-over-actions, no model-free sampling, no α step-size, no
optimality) may appear. Any such appearance is a prerequisite violation.

---

## 3. The ordered six-segment spine (S&B Chapter 3 order)

Each segment hands its key object directly to the next; no concept is introduced
that the next segment does not consume. Equations are listed **in S&B order**
with acceptable variants. Per the 30-min ceiling, **each segment is a single
worked beat**, not a survey.

### Segment (a) — MDP framework  ·  S&B §3.1, pp. 47–48

**Teach:** the state set 𝒮, the action set 𝒜(s), and the **Markov property** —
the next state and reward depend only on the current state and action, not on the
full history. Name `p(s',r|s,a)` as "the environment's dynamics" (it is *derived*
in detail in (c); here it is only named).

**Canonical statement (Markov property, S&B p. 48):**
```
Pr{ S_{t+1}=s', R_{t+1}=r | S_0,A_0,...,S_t,A_t }  =  Pr{ S_{t+1}=s', R_{t+1}=r | S_t,A_t }
```
**Acceptable variant:** an informal caption "the present state captures everything
relevant from the past" is acceptable *alongside* the formal statement, not in
place of it.

**Single beat:** label FrozenLake's 16 cells with integer state indices 0–15;
identify the four actions (LEFT/DOWN/RIGHT/UP = 0/1/2/3); state the Markov
property in one caption. Do NOT enumerate all transitions here.

**Boundary note:** include the terminal/absorbing state(s) in 𝒮⁺ — holes
{5, 7, 11, 12} and goal {15} are terminal in FrozenLake-v1. (Used again in (e).)

### Segment (b) — Rewards and returns  ·  S&B §3.2–3.4, pp. 53–57

**Teach:** the single-step reward R_{t+1}, the **reward hypothesis** (S&B p. 53:
"all of what we mean by goals and purposes can be well thought of as the
maximization of the expected value of the cumulative sum of a received scalar
signal"), the **return** G_t, the discount factor γ, and the episodic-vs-continuing
distinction.

**Canonical equations (S&B order):**

Discounted return (S&B eq. 3.8):
```
G_t  =  R_{t+1} + γ R_{t+2} + γ² R_{t+3} + ...  =  Σ_{k=0}^{∞} γ^k R_{t+k+1}
```
Recursive form (S&B eq. 3.9) — **this is the seed of segment (f); show it here:**
```
G_t  =  R_{t+1} + γ G_{t+1}
```
**Acceptable variants:** the finite-horizon episodic form
`G_t = Σ_{k=0}^{T-t-1} γ^k R_{t+k+1}` (S&B §3.4, the unified notation) is an
acceptable equivalent for episodic FrozenLake; either may be shown, but if the
infinite-sum form is shown it must be paired with the note that episodic tasks
terminate (so the sum is effectively finite).

**Single beat:** animate γ **once** (one slider 0 → 0.99, or one numeric example)
showing how a fixed reward stream's return changes. Do not run three γ values.
Show G_t = R_{t+1} + γG_{t+1} explicitly because (f) reuses it.

**Boundary notes (state them):** γ ∈ [0,1]. γ=0 ⇒ G_t = R_{t+1} (myopic).
γ=1 valid only when termination is guaranteed (FrozenLake episodic, so OK).
Episodic tasks have a terminal time T after which no reward accrues.

### Segment (c) — Transition probability  ·  S&B §3.1, pp. 48–49  ·  REUSE existing scene

**Teach:** the **four-argument dynamics function** and its normalization. This is
the segment that reuses the approved `transition_prob_concept.py` wholesale.

**Canonical equations (S&B eq. 3.2 and the normalization):**
```
p(s',r | s,a)  ≐  Pr{ S_{t+1}=s', R_{t+1}=r | S_t=s, A_t=a }
Σ_{s'} Σ_{r} p(s',r | s,a)  =  1     for all s ∈ 𝒮, a ∈ 𝒜(s)
```
**Acceptable derived variants** (optional, only if time allows — not required):
state-transition marginal `p(s'|s,a) = Σ_r p(s',r|s,a)`; expected reward
`r(s,a) = Σ_r r Σ_{s'} p(s',r|s,a)`. These are S&B p. 49 but are *not* needed to
unblock `dp_policy_eval`; include only if under budget.

**Single beat:** the slippery three-outcome fan for **state 6, action RIGHT**,
the ActionBarChart showing three 1/3 bars, and the Σp=1 normalization. This is
exactly what the reference scene already renders.

> **⚠ NUMERICAL FLAG for the Technical Validator (see §8).** The course plan and
> `rl_knowledge_base.md` give state-6 RIGHT outcomes as **{7, 2, 10}**
> (intended-RIGHT 7, perpendicular-UP 2, perpendicular-DOWN 10). The existing
> `transition_prob_concept.py` hard-codes **{7, 2, 5}** (RIGHT 7, UP 2, **LEFT 5**).
> LEFT is the *opposite* direction, not a perpendicular — under the standard
> slippery model the two non-intended outcomes are the two **perpendiculars**, so
> {7, 2, 10} is the model-correct set and {7, 2, 5} appears to be a bug in the
> reference scene's `_TRIAL_OUTCOMES`. The Technical Validator must run live
> Gymnasium and pin the correct successor set before this scene is reused. **Do
> not ship segment (c) until this is resolved.**

### Segment (d) — Policies  ·  S&B §3.5, p. 58

**Teach:** the policy π(a|s) as the agent's decision rule; deterministic vs.
stochastic; the normalization over actions. Contrast sharply with (c): **p is the
environment, π is the agent.**

**Canonical statement (S&B p. 58 definition + the simplex constraint):**
```
π(a|s)  =  Pr{ A_t=a | S_t=s }
π(a|s) ≥ 0,   Σ_a π(a|s) = 1     for all s
```
**Acceptable variant:** a deterministic policy may be written π(s)=a (the
one-hot/Kronecker form). If shown, state that it is the special case where one
action gets probability 1.

**Single beat:** one contrast — a PolicyArrowGrid (deterministic, one arrow per
cell) beside a probability-bar panel for one focal state (stochastic, e.g. the
uniform-random policy with each action 0.25). Do **not** survey a policy
taxonomy. Foreshadow: the uniform-random policy shown here is the exact policy
`dp_policy_eval` evaluates.

### Segment (e) — Value functions  ·  S&B §3.5, pp. 58–60

**Teach:** v_π(s) and q_π(s,a) as expected returns under π; the v–q relationship;
terminal value = 0.

**Canonical equations (S&B eq. 3.12 then 3.13):**
```
v_π(s)   ≐  E_π[ G_t | S_t=s ]                     (S&B eq. 3.12)
q_π(s,a) ≐  E_π[ G_t | S_t=s, A_t=a ]              (S&B eq. 3.13)
```
The v–q relationship (S&B p. 59, used as the bridge to (f)):
```
v_π(s)  =  Σ_a π(a|s) q_π(s,a)
```
**Acceptable variant:** captions may say "expected total discounted reward from s
following π" for v_π. Acceptable as a gloss, not a replacement for the E_π[G_t|·]
form.

**Single beat:** introduce the ValueHeatmap reading (cell colour = v_π(s)); show
q-bars for one focal state; state v_π = Σ_a π(a|s) q_π(s,a) so (f) can substitute
into it. **Terminal states have value 0** — show holes and goal as 0-value cells.

> **MISCONCEPTION TO DEFEAT HERE (new for the merge):** "value functions require
> the optimal policy." No — **v_π is defined for ANY policy π, including the
> uniform-random policy.** This is essential: `dp_policy_eval` evaluates the
> uniform-random policy, so the learner must accept that a non-optimal policy has
> a perfectly well-defined value function.

### Segment (f) — Bellman expectation equation  ·  S&B §3.5, pp. 59 (eq. 3.14)  ·  THE PAYOFF

**Teach:** the recursive self-consistency that v_π satisfies — **derived**, not
asserted. This is the closing concept and the direct `dp_policy_eval` prerequisite.

**The derivation (DO NOT SKIP — see §9 "Do not oversimplify"):**
1. Start from G_t = R_{t+1} + γ G_{t+1}  (the recursion shown in (b), S&B eq. 3.9).
2. Substitute into v_π(s) = E_π[G_t | S_t=s] = E_π[R_{t+1} + γ G_{t+1} | S_t=s].
3. Expand the expectation over the policy π(a|s) and the dynamics p(s',r|s,a),
   and recognize E_π[G_{t+1} | S_{t+1}=s'] = v_π(s').

**Canonical equation (S&B eq. 3.14):**
```
v_π(s)  =  Σ_a π(a|s)  Σ_{s',r} p(s',r | s,a) [ r + γ v_π(s') ]
```
**Acceptable variants:** the compact form `v_π(s) = E_π[R_{t+1} + γ v_π(S_{t+1}) | S_t=s]`
(S&B's intermediate line, p. 59) is an acceptable *bridge* but the fully expanded
double-sum form is mandatory because it is the exact shape of the `dp_policy_eval`
backup. The action-value Bellman equation
`q_π(s,a) = Σ_{s',r} p(s',r|s,a)[r + γ Σ_{a'} π(a'|s') q_π(s',a')]` is optional
and should be omitted unless under budget — it is not needed to unblock V-03.

**Single beat:** ONE BackupDiagram — root node s (open circle), branch to action
nodes weighted by π(a|s), branch to (s',r) leaf nodes weighted by p(s',r|s,a),
leaf value r + γ v_π(s'). Map each branch **term-by-term** onto eq. 3.14. State
the fixed-point character: "v_π is the function that satisfies this equation at
every state." **Closing link (preview, do NOT show the algorithm):** "Next video:
turn this equality into an assignment and apply it until the values stop changing
— that is policy evaluation."

---

## 4. Required worked example and environment

**Environment:** `FrozenLake-v1`, 4×4, `is_slippery=True`, default map. Used
throughout so every visual (grid, state indices, slippery fan, value heatmap,
policy arrows, backup diagram) carries directly into `dp_policy_eval`.

**Anchor worked example:** **state 6** (row 1, col 2) with action **RIGHT**
(action index 2). This is the canonical three-outcome slippery state. It is the
worked beat of segment (c) and the focal state recommended for the q-bars in (e)
and the backup root in (f), so one geometric anchor serves three segments.

**Map layout (FrozenLake-v1 4×4, "4x4" map):**
```
 0  1  2  3        S F F F      S=start(0)  F=frozen
 4  5  6  7        F H F H      H=hole {5,7,11,12}
 8  9 10 11        F F F H      G=goal(15)
12 13 14 15        H F F G
```
State 6 is a frozen tile with all four actions available; its slippery outcomes
expose stochasticity cleanly. **State-6 RIGHT successor set is pending Technical
Validator confirmation — see §3(c) flag and §8.**

---

## 5. Common misconceptions and boundary conditions

| # | Misconception (the false belief) | Correction | Source |
|---|---|---|---|
| M1 | "p(s',r\|s,a) is the probability the agent *chooses* action a." | That is the policy π(a\|s). p is the **environment's** response; the agent does not control it. Defeat by visually separating (c) p-fan from (d) π-arrows. | S&B p. 48 ("the dynamics function p defines the environment's response") |
| M2 | "A deterministic environment has p=1 for one outcome — so transitions are deterministic." | True for deterministic envs (CliffWalking), but FrozenLake slippery has **three outcomes each 1/3**. The video must show the stochastic case so `dp_policy_eval`'s Σ_{s',r} loop is motivated (a single deterministic successor would make the inner sum look pointless). | S&B §3.1; `rl_knowledge_base.md` transition_prob |
| M3 | "You need to know p to do RL." | Only model-based (DP) methods use p; MC/TD do not. Here p **is** needed because this video unblocks the model-based DP track. Flag the model-free contrast for later but do not resolve it here. | S&B Ch. 5–6 (forward reference, do not teach) |
| M4 | "Value functions require knowing the optimal policy." | **v_π is defined for ANY π, including uniform-random.** This is the policy `dp_policy_eval` evaluates. Defeat in (e) by computing v for a deliberately non-optimal policy. | S&B eq. 3.12, p. 58 |
| M5 | "The Bellman equation is just a definition you state." | It is **derived** from G_t's recursion via p. Stating it without the G_t = R_{t+1}+γG_{t+1} substitution plants the misconception that it is arbitrary. | S&B p. 59 derivation of eq. 3.14 |

**Boundary conditions (state these on-screen or in narration):**

| Condition | Behaviour | Source |
|---|---|---|
| Terminal state value | v_π(terminal) ≡ 0 by definition (holes and goal in FrozenLake). Show 0-value cells in the heatmap. | S&B §3.4, p. 57; eq. 3.12 with G_t=0 from terminal |
| γ = 0 | G_t = R_{t+1}; value is one-step expected reward only. | S&B §3.3, p. 55 |
| γ = 1 | Valid only with guaranteed termination; FrozenLake episodic so OK. On a non-terminating task the return diverges. | S&B §3.3–3.4, pp. 55–57 |
| Σ_a π(a\|s) = 1 | Policy is a valid probability distribution over actions at every state. | S&B §3.5, p. 58 |
| Σ_{s',r} p = 1 | Dynamics is a valid distribution over (successor, reward) pairs for every (s,a). | S&B eq. 3.3, p. 48 |
| Characterization, not algorithm | This video states/derives the Bellman equation; it never iterates it. Iteration is `dp_policy_eval`. | scope rule (this spec §1) |

---

## 6. Minimum visual obligations

The "never-rebuilt accreting grid" is the spine: one FrozenLake grid that gains a
layer per segment and is never torn down.

| Segment | Required visual element | Obligation |
|---|---|---|
| (a) | Single FrozenLake grid with **integer state indices 0–15** | Grid is built **once** here and persists through (f). |
| (b) | Reward tokens + a **G_t discounted-sum** build (one γ animation) | Show the recursion G_t = R_{t+1}+γG_{t+1} explicitly. |
| (c) | **ActionBarChart** with three 1/3 bars for the three-outcome fan; Σp=1 caption | Reuse `transition_prob_concept.py` (subject to §8 numeric fix). |
| (d) | **PolicyArrowGrid** (deterministic) beside probability bars (stochastic), one contrast | Visually distinct from (c)'s p-fan to defeat M1. |
| (e) | **ValueHeatmap** (cell colour = v_π); q-bars for the focal state; terminal cells shown as 0 | Defeat M4 with a non-optimal policy's heatmap. |
| (f) | **BackupDiagram** whose branches map one-to-one onto eq. 3.14 terms | Each branch labelled with its equation term (π(a\|s), p(s',r\|s,a), r+γv_π(s')). |

Hard rule: the grid is never rebuilt — each segment adds exactly one layer. An
explicit **recap card** before (f) is required (per the course plan's Pedagogical
Risk mitigation) to reset cognitive load before the Bellman assembly.

---

## 7. Code ideas to connect (NO algorithm / NO iteration loop)

These connect the math to Gymnasium without teaching any algorithm. The only
*runnable* code panel is the segment-(c) reuse from `transition_prob_concept.py`.

**Segment (c) — model access (runnable, reused scene):**
```python
env = gym.make("FrozenLake-v1", is_slippery=True)
# env.unwrapped.P[state][action] -> list of (prob, next_state, reward, done)
for prob, next_state, reward, done in env.unwrapped.P[6][2]:   # state 6, RIGHT
    print(prob, next_state, reward, done)
```

**Segments (d)/(e) — array shapes that `dp_policy_eval` consumes (show as shapes,
do not loop):**
```python
import numpy as np
n_states  = env.observation_space.n     # 16
n_actions = env.action_space.n          # 4
V = np.zeros(n_states)                  # value table, all zeros (terminal stays 0)
policy = np.ones((n_states, n_actions)) / n_actions   # uniform-random π(a|s)=0.25
# policy[state]        -> the action distribution at `state` (sums to 1)
# policy[state][action] -> π(a|s)
```

**Hard prohibition (prerequisite-DAG enforcement):** **no iteration loop, no
sweep, no `while delta > theta`, no `max(action_values)`, no value update
assignment `V[state] = ...`.** Those belong to `dp_policy_eval` /
`dp_value_iteration`. Showing them here is a prerequisite violation that warrants
a REJECTED verdict at the gate review. The closing beat may *name* policy
evaluation as "next," but must not display its loop.

**API fidelity notes:** must use `env.unwrapped.P` (wrappers hide `P`); `P[s][a]`
returns `(prob, next_state, reward, done)` 4-tuples; this video never calls
`env.step()` or `env.reset()` (no sampling — that is the MC/TD track).

---

## 8. Numerical claims the Technical Validator must check

Run live Gymnasium; do not rely on the reference scene's hard-coded constants.

1. **State-6 RIGHT three-outcome set and probabilities (BLOCKING).** Confirm
   `env.unwrapped.P[6][2]` against the **{7, 2, 10}** claim (intended RIGHT 7,
   perpendicular UP 2, perpendicular DOWN 10), each prob ≈ 0.3333. **Resolve the
   conflict with `transition_prob_concept.py`, which hard-codes {7, 2, 5}**
   (`_TRIAL_OUTCOMES = [7, 2, 5]` and the LEFT→5 comment). Standard slippery
   model says the two non-intended outcomes are the two *perpendiculars*, so {7,
   2, 10} is expected and {7, 2, 5} looks wrong. Pin the live values; if the live
   env returns {7, 2, 10}, the reference scene must be corrected before reuse.
2. **All rewards 0 except the goal.** Confirm reward = 0.0 on every state-6 RIGHT
   transition; reward 1.0 fires only on arrival at state 15. (Matches `rl_intro`
   spec's verified claim: holes {5,7,11,12}, goal 15, reward fires on arrival.)
3. **Σp = 1.** Confirm Σ over `env.unwrapped.P[6][2]` probabilities = 1.0 (within
   float tolerance).
4. **Σ_a π = 1 for uniform policy.** Confirm `policy = np.ones((16,4))/4` gives
   each row summing to 1.0 and each entry = 0.25.
5. **γ discounting of a sample return.** Verify one concrete G_t: for a sample
   reward stream (e.g. rewards [0,0,1] at the last three steps, γ=0.99),
   G = 0 + 0.99·0 + 0.99²·1 = 0.9801. Confirm the on-screen number matches.
6. **Terminal value = 0.** Confirm the heatmap shows holes {5,7,11,12} and goal
   {15} at value 0 (terminal absorbing).
7. **Map geometry.** Confirm state 6 = row 1, col 2 in the 4×4 "4x4" map and that
   its four neighbours are 2 (up), 10 (down), 5 (left), 7 (right) — this is what
   makes the {7,2,5} vs {7,2,10} discrepancy a *direction* error, not an
   indexing error.

---

## 9. "Do not oversimplify" notes (mandatory)

- **The Bellman equation MUST be derived, not stated.** Segment (f) must show the
  substitution chain G_t = R_{t+1}+γG_{t+1}  →  v_π(s)=E_π[R_{t+1}+γG_{t+1}|S_t=s]
  →  the expanded double sum (eq. 3.14). Asserting eq. 3.14 as a definition plants
  M5 and makes `dp_policy_eval` look like magic. The recursion G_t=R_{t+1}+γG_{t+1}
  is deliberately surfaced in segment (b) precisely so (f) can reuse it.
- **The stochastic (slippery) case MUST appear.** A deterministic single-successor
  example would collapse the inner sum Σ_{s',r} to one term and make
  `dp_policy_eval`'s loop over successors look pointless. Three 1/3 outcomes are
  required to motivate that loop. (Defeats M2.)
- **v_π must be shown for a NON-optimal policy.** Use the uniform-random policy in
  (e). If only an optimal-looking policy is shown, the learner absorbs M4 and is
  confused when `dp_policy_eval` evaluates uniform-random. (Defeats M4.)
- **p is the environment, π is the agent — keep them visually separate.** (c) and
  (d) must look different (p-fan vs. arrow grid) so M1 cannot form.
- **No optimality, no algorithm.** Do not preview v_*, the max-over-actions
  optimality equation, iteration, sweeps, or convergence. Those are later lessons;
  introducing them here is both a prerequisite violation and a 30-min-budget risk.

---

## 10. App-metadata proposal for `backend/concept_videos/specs.py`

A new `LessonVideoSpec` entry keyed `"mdp_foundations"`. Note: the `specs.py`
schema (single `theory_equation`, single `worked_example`, etc.) is built for
single-concept videos; a six-segment video strains it. Proposal below picks the
**Bellman expectation equation as the headline** (the payoff/handoff concept) and
folds the segment spine into `pacing_notes`. The Producer/Script Writer may
prefer to register the headline as the equation and document the full spine here
in the `.md` spec rather than in `specs.py`.

```python
"mdp_foundations": LessonVideoSpec(
    lesson_id="mdp_foundations",
    title="MDP Foundations: From States to the Bellman Equation",
    environment_name="FrozenLake",
    theory_equation=r"v_{\pi}(s)=\sum_a \pi(a|s)\sum_{s',r}p(s',r|s,a)\left[r+\gamma v_{\pi}(s')\right]",
    worked_example=(
        "Use FrozenLake-v1 4x4 (is_slippery=True) throughout. Build one accreting "
        "grid across six segments: (a) state indices 0-15 + Markov property; "
        "(b) return G_t with one gamma animation; (c) state 6, action RIGHT three "
        "slippery outcomes summing to 1; (d) uniform-random policy arrows vs. "
        "probability bars; (e) value heatmap with terminal=0 for a non-optimal "
        "policy; (f) one backup diagram mapping term-by-term onto the Bellman "
        "expectation equation, derived from G_t = R_{t+1} + gamma*G_{t+1}."
    ),
    code_focus_lines=(
        "env = gym.make('FrozenLake-v1', is_slippery=True)",
        "for prob, next_state, reward, done in env.unwrapped.P[6][2]:",
        "    print(prob, next_state, reward, done)",
        "policy = np.ones((env.observation_space.n, env.action_space.n)) / env.action_space.n",
    ),
    misconception_to_prevent=(
        "The transition function p(s',r|s,a) is the environment's response, not "
        "the agent's action choice (that is the policy pi(a|s)); and v_pi is "
        "defined for ANY policy, including the uniform-random policy, not only the "
        "optimal one."
    ),
    takeaway_line=(
        "A finite MDP is (states, actions, p); the agent's policy and the discount "
        "turn rewards into returns; and the Bellman expectation equation expresses "
        "each state's value recursively from its successors' values."
    ),
    pacing_notes=(
        "Segment (a): build the grid once with state indices; state the Markov property; do not enumerate transitions.",
        "Segment (b): animate gamma exactly once; surface G_t = R_{t+1} + gamma*G_{t+1} for reuse in (f).",
        "Segment (c): reuse the approved transition_prob scene; hold on the three 1/3 bars and the sum-to-one.",
        "Segment (d): one deterministic-vs-stochastic policy contrast; foreshadow the uniform-random policy.",
        "Segment (e): heatmap reading + q-bars; show terminal cells at 0; use a non-optimal policy.",
        "Segment (f): recap card first, then derive the Bellman equation from G_t's recursion via one backup diagram; preview policy evaluation without showing its loop.",
    ),
    target_duration_label="29:00",
    theory_verification=(
        TheoryVerification(
            claim=(
                "A finite MDP is defined by states, actions, and the four-argument "
                "dynamics p(s',r|s,a); the return is the discounted sum of rewards; "
                "and the Bellman expectation equation gives v_pi recursively."
            ),
            source_url="https://incompleteideas.net/book/the-book-2nd.html",
            validation_note=(
                "Sutton and Barto Chapter 3: p(s',r|s,a) eq. 3.2 (p. 48); return "
                "G_t eq. 3.8 and recursion eq. 3.9 (pp. 54-55); v_pi eq. 3.12 and "
                "q_pi eq. 3.13 (p. 58); Bellman expectation equation eq. 3.14 (p. 59)."
            ),
        ),
        TheoryVerification(
            claim=(
                "FrozenLake-v1 with is_slippery=True gives state 6, action RIGHT a "
                "three-outcome distribution (each ~1/3) over the intended and the "
                "two perpendicular successor states, summing to 1; all rewards 0 "
                "except arrival at goal state 15."
            ),
            source_url="https://gymnasium.farama.org/v0.26.3/environments/toy_text/frozen_lake/",
            validation_note=(
                "PENDING Technical Validator: confirm env.unwrapped.P[6][2] "
                "successor set is {7, 2, 10} (RIGHT/UP/DOWN perpendiculars), NOT "
                "{7, 2, 5} as the existing transition_prob_concept.py hard-codes. "
                "Resolve before reusing the segment (c) scene."
            ),
            is_inference=True,
        ),
    ),
),
```

**theory_verification candidates (with S&B page citations) — summary:**
- p(s',r|s,a) — S&B eq. 3.2, §3.1, p. 48.
- Σ_{s',r} p = 1 — S&B eq. 3.3, p. 48.
- Return G_t = Σ γ^k R_{t+k+1} — S&B eq. 3.8, p. 54; recursion eq. 3.9, p. 55.
- Reward hypothesis — S&B §3.2, p. 53.
- Policy π(a|s) — S&B §3.5, p. 58.
- v_π = E_π[G_t|S_t=s] — S&B eq. 3.12, p. 58; q_π — eq. 3.13, p. 58.
- Bellman expectation equation v_π — S&B eq. 3.14, p. 59.
- Terminal value = 0 — S&B §3.4, p. 57.
- FrozenLake state-6 RIGHT dynamics — Gymnasium FrozenLake docs (live-verify).

---

## 11. Must-teach checklist (RL Expert sign-off conditions)

- [ ] Every term in the Bellman equation (π, p, r, γ, v_π, s') is defined earlier in this video.
- [ ] The worked example (state-6 RIGHT) numbers match live Gymnasium (Technical Validator).
- [ ] The code lines are runnable Python; no iteration/sweep/max/update appears.
- [ ] Boundary conditions stated: terminal value 0, γ edge cases, Σp=1, Σ_aπ=1.
- [ ] The Bellman equation is **derived** from G_t's recursion, not asserted.
- [ ] The stochastic (three-outcome) case is shown.
- [ ] v_π is shown for the uniform-random (non-optimal) policy.
- [ ] The closing beat previews `dp_policy_eval` without showing its algorithm.

---

## 12. Takeaway line

> "A finite MDP is (states, actions, p); a policy plus a discount turns rewards
> into returns; value functions measure those returns under any policy; and the
> Bellman expectation equation expresses each state's value recursively from its
> successors — the exact equality the next video turns into an algorithm."

---

## RL Expert sign-off (advisory — no gate verdict)

- [x] Reviewed against S&B 2018 Chapter 3.
- [x] All equations checked against S&B numbering and `rl_knowledge_base.md`.
- [x] Code lines are runnable Python; no algorithm/iteration included.
- [x] Misconceptions M1–M5 addressed with defeat strategies.
- [x] No term used without prior definition; no later-lesson concept introduced.
- [ ] **OPEN — Technical Validator must resolve the state-6 RIGHT {7,2,10} vs {7,2,5} discrepancy before segment (c) is reused.**
