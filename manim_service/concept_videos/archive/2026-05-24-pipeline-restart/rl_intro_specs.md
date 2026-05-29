# RL Expert Teaching Spec — `rl_intro`

**Title:** What Is Reinforcement Learning?  
**lesson_id:** `rl_intro`  
**Authored by:** RL Expert  
**Date:** 2026-05-21  
**Status:** ADVISORY — no gate verdict required; intended as Script Writer input  
**Series position:** Video 1 of 15. First video in the series. No predecessor.  
**S&B coverage:** Chapter 1, §1.1 ("Reinforcement Learning", pp. 1–3), §1.2 ("Examples", pp. 4–5), §1.3 ("Elements of Reinforcement Learning", pp. 6–7)  
**platform_contract:** UNREGISTERED_NEW_LESSON

---

## 1. Concept Definition and Why It Matters Here

Reinforcement learning is the problem of learning to act by interacting with an environment to maximize a numerical reward signal. The learner is not told which actions to take; it must discover which actions yield the most reward by trying them (S&B §1.1, p. 1). Two features distinguish RL from all other learning paradigms:

1. **Trial-and-error search** — the agent must explore its action space without a supervisor.
2. **Delayed reward** — an action may affect not only the immediate reward but all subsequent rewards; credit must be assigned backward through time.

These two features are S&B's own formulation (§1.1, p. 2: "These two characteristics — trial-and-error search and delayed reward — are the two most important distinguishing features of reinforcement learning"). The spec mandates that both appear on-screen as named, captioned concepts.

**Why this is the right entry point:** Every subsequent video in the series — MDP framework, transition probability, policy evaluation, Q-learning — presupposes that the viewer already understands *why* the RL problem exists and what makes it different. A learner who enters at `dp_policy_eval` without `rl_intro` sees equations without motivation. This video provides the motivational anchor for the entire series.

---

## 2. Prerequisite Concepts

**Prerequisites: None.**

This is the absolute entry point of the series. The viewer is assumed to have:
- Comfort with Python (from the learner profile in `rl_course_plan.md`)
- High-school probability intuition (not required in this video)
- No prior exposure to MDPs, value functions, policies, or any RL algorithm

The video must be self-contained. It must not use any term that requires prior RL knowledge without immediately defining it on screen.

**Series position in the DAG:**

```
rl_intro  ←── THIS VIDEO
   │
   └──► mdp_framework
```

This video is the root of the entire prerequisite DAG. All 14 subsequent videos depend on it transitively.

---

## 3. Must-Teach Points (binding — Script Writer may not drop these)

The following six points must appear as discrete, visually anchored teaching beats. Each must have its own caption line and at least one geometric binding.

### 3.1 What RL is NOT: contrast with supervised and unsupervised learning

S&B §1.1, pp. 2–3 draws explicit, precise distinctions:

- **Supervised learning** learns from labeled examples provided by a knowledgeable external supervisor. Each training example is a (situation, correct-action) pair. RL has no such supervisor and no labeled dataset.
- **Unsupervised learning** finds hidden structure in unlabeled data. RL is not trying to find structure — it is trying to maximize a reward signal. (S&B p. 3: "reinforcement learning is trying to maximize a reward signal instead of trying to find hidden structure.")
- **RL is a third paradigm** alongside the other two (S&B p. 3: "We therefore consider reinforcement learning to be a third machine learning paradigm, alongside supervised learning and unsupervised learning and perhaps other paradigms.").

**Visual obligation:** A three-way classification diagram — three labeled boxes (Supervised, Unsupervised, Reinforcement Learning) with a one-line distinguishing property in each. The RL box must read: "no labels, just rewards." Animate the RL box last, after the other two are established, to emphasize it is *new*.

**Do not oversimplify:** Do NOT say "RL is like supervised learning but with delayed feedback." This is precisely the misconception this beat exists to prevent (see §7). The delay is real, but the deeper distinction is the *absence of a supervisor* and the *need for trial-and-error search*. A system with delayed supervised feedback (e.g., a graded exam) is not RL.

### 3.2 The four loop elements: agent, environment, state, action

The RL loop has four named elements. These are not the same as S&B's §1.3 "four subelements" (which are policy, reward signal, value function, model — those belong to later videos). The loop elements taught here come from S&B §1.1 pp. 1–2 and the agent–environment interface diagram (formally introduced in §3.1, but the informal version belongs here):

| Element | On-screen canonical name | Color binding (STYLE_BIBLE §1) |
|---|---|---|
| Agent | "Agent" — the decision-maker | `POLICY_COLOR` (#A78BFA) — agent acts under a (future) policy |
| Environment | "Environment" — everything outside the agent | `STATE_COLOR` (#38BDF8) — the environment produces states |
| State (observation) | "State / Observation" — what the agent perceives | `STATE_COLOR` (#38BDF8) |
| Action | "Action" — what the agent does | `ACTION_COLOR` (#FB923C) |

**Precise wording:** S&B §1.1 p. 1 says "a learning agent must be able to sense the state of its environment to some extent and must be able to take actions that affect the state." This is the exact relationship to convey: state is perceived, action is chosen, action affects the next state.

**Visual obligation:** An animated two-box loop diagram: LEFT box labeled "Agent" (`POLICY_COLOR`), RIGHT box labeled "Environment" (`STATE_COLOR`). Two labeled arrows between them: the downward arrow carries "Action" (`ACTION_COLOR`), the upward arrow carries "State / Observation" (`STATE_COLOR`). Animate the agent box first, then the environment box, then the arrows one at a time with captions.

### 3.3 The reward signal — scalar feedback

The reward is a single number sent from the environment to the agent on each time step. It is the *only* feedback the agent receives. S&B §1.3 p. 6: "On each time step, the environment sends to the reinforcement learning agent a single number called the reward." The agent's sole objective is to maximize the total reward over the long run.

**Color binding:** Reward arrow in the loop diagram uses `REWARD_COLOR` (#34D399). The FrozenLake goal tile (reward = +1) uses `REWARD_COLOR`. Hole tiles (reward = 0, but terminates the episode negatively) use `PENALTY_COLOR` (#F87171) for the *outcome* visual.

**Precise wording:** The reward is a *signal*, not a label. The agent does not know in advance which actions produce high rewards. This is the trial-and-error aspect.

**Do not oversimplify:** Do NOT say "reward = score." A score implies a fixed external evaluator with full knowledge. The reward signal can be stochastic and is defined by the environment dynamics — the agent does not design it.

### 3.4 The goal: maximize cumulative reward

The agent's goal is not to maximize the reward on the current step but the *total* reward accumulated over time. S&B §1.1 p. 1: "so as to maximize a numerical reward signal." The word "cumulative" or "total over time" must appear on screen. Do NOT introduce the return $G_t$ or the discount factor $\gamma$ — these belong to `rewards_returns`. The idea here is purely intuitive: more reward over the whole episode is better.

**Visual obligation:** In the FrozenLake motivation sequence, show the elf taking different paths. One path reaches the goal (high cumulative reward). One path falls into a hole early (low cumulative reward). Caption: "The agent wants to reach the goal — not just survive the next step."

### 3.5 The RL loop as a repeating cycle

The interaction is not a single shot. It is a cycle that repeats at every time step: the agent observes the state, chooses an action, the environment transitions, and a reward is emitted. S&B §1.1 frames the entire RL problem as this repeating cycle. The loop diagram from beat 3.2 must animate *cyclically* — show the arrows cycling at least twice so the viewer understands it is a loop, not a single exchange.

**Visual obligation:** After the static loop diagram is established, animate one full cycle: agent box highlights → action arrow animates → environment box highlights → state arrow animates → reward arrow animates → agent box highlights again. Run the cycle twice. Caption on second cycle: "This repeats on every time step."

### 3.6 FrozenLake-v1 as concrete motivation

FrozenLake must appear *before* the abstract loop diagram, not after. Teaching pattern is **concrete-to-abstract**: show the specific problem first, then abstract it.

**Sequence obligation:**
1. Show the 4×4 FrozenLake grid with the elf sprite at the start tile (S).
2. Show the goal tile (G) in `REWARD_COLOR`.
3. Show hole tiles in `PENALTY_COLOR`.
4. Animate the elf taking a random walk — falling into a hole on one attempt, reaching the goal on another.
5. Caption: "The elf has to figure out how to reach the goal — no one tells it the right moves."
6. *Then* introduce the abstract loop diagram.

**Asset specification:** Use `frozenlake_frame(state)` helper with `elf_right.png` / `elf_down.png` sprites for directionality. Goal tile uses `goal.png` wrapped in `REWARD_COLOR` border. Hole tiles use `hole.png` wrapped in `PENALTY_COLOR` border. Follow STYLE_BIBLE §14 asset border standards — no raw `ImageMobject` placement.

**This video uses FrozenLake visually only.** No `env.reset()`, no `env.step()`, no `env.unwrapped.P`. No code panel. No `CodeStepper`.

---

## 4. Boundary Conditions — What This Video Explicitly Does NOT Teach

The following concepts must not appear in this video, even informally. If the Script Writer finds that a visual naturally drifts toward one of these, it must stop at the informal level and caption: "We will formalize this in [video title]."

| Concept | Deferred to |
|---|---|
| MDP formalism, state space $\mathcal{S}$, action space $\mathcal{A}$ | `mdp_framework` |
| Transition probability $p(s', r \mid s, a)$ | `transition_prob` |
| Return $G_t$, discount factor $\gamma$, episodic vs. continuing tasks | `rewards_returns` |
| Policy $\pi(a \mid s)$ — formal definition | `policies` |
| Value functions $v_\pi(s)$, $q_\pi(s,a)$ | `value_functions` |
| Bellman equations | `bellman_equations` |
| Any DP, MC, or TD algorithm | respective later videos |
| Exploration vs. exploitation trade-off | S&B §1.1 p. 3 introduces it, but it should be named and acknowledged at most as "a challenge we will return to" — do not teach it; it has no dedicated video slot yet in Wave 1 |
| `env.unwrapped.P`, `env.step()`, `env.reset()` API calls | `mdp_framework` or `transition_prob` |

**S&B §1.3 note:** S&B §1.3 pp. 6–7 introduces four subelements: policy, reward signal, value function, and model. Only the *reward signal* belongs in this video. Policy, value function, and model are deferred. The Script Writer must not accidentally teach S&B's four subelements as if they were the four loop elements — these are different taxonomies.

---

## 5. Misconceptions to Prevent

### Primary misconception (must be explicitly addressed visually)

**"RL is supervised learning with delayed feedback."**

This is the most durable misconception for beginners who arrive with ML background. It must be defeated by the three-way contrast diagram in beat 3.1.

The refutation logic:
- Supervised learning requires a supervisor who *knows the correct action* for every situation and provides it as a label.
- RL has no supervisor and no correct-action labels. The agent must discover which actions are good through trial and error.
- The delay of reward is a *consequence* of the sequential nature of RL, not its defining feature. Even if reward were immediate (as in a one-step bandit problem), RL would still be different from supervised learning because the agent learns *which actions are good*, not *what the correct output is for a given input*.
- S&B §1.1 p. 2: "In uncharted territory — where one would expect learning to be most beneficial — an agent must be able to learn from its own experience."

**Visual defeat strategy:** In the three-box contrast diagram, include a mini-illustration in the Supervised Learning box: a teacher handing a labeled card (situation → correct action). In the RL box: an agent in a grid with a question mark above it and a reward arrow from the environment. The question mark makes the absence of labels visually explicit.

### Secondary misconception (caption-level guard is sufficient)

**"Reward is always a positive number."**

FrozenLake-v1 with default `is_slippery=True` gives reward 0 on every step except reaching the goal (reward 1). Holes terminate the episode with reward 0 — not a negative reward. However, some learners conclude from this that RL always uses non-negative rewards. The video should note in passing: "rewards can be positive, negative, or zero — the exact values depend on the environment." This prevents the misconception without going into detail.

### Tertiary misconception (acknowledge, do not fully address)

**"The agent knows the environment's rules."**

Some learners assume the agent has access to the environment's internals (transition dynamics, reward function formula). Caption guard in the FrozenLake motivation: "The elf doesn't know the rules of the ice — it only sees what happens after each step." This sets up the model-free/model-based distinction for `model_based_vs_free` much later without introducing the terminology now.

---

## 6. Allowed Expansions Beyond platform_contract

The `platform_contract` is UNREGISTERED_NEW_LESSON. The following expansions are explicitly permitted for this video because they deepen the motivation without requiring prerequisite knowledge:

1. **The exploration–exploitation dilemma as a named challenge** — S&B §1.1 p. 3 introduces it at the Chapter 1 level. It may be named in a caption ("the agent faces a choice: try known good actions, or explore new ones") and tagged as a concept for later. It must NOT be animated or formalized.
2. **One additional S&B real-world example beyond FrozenLake** — S&B §1.2 pp. 4–5 gives examples including a chess player, a refinery controller, a mobile robot, and a gazelle calf. One of these may be shown as a static illustration in a CONNECT beat to reinforce that RL is general, not specific to grid games. Recommended: the mobile robot example (close to FrozenLake's structure). Cap at 15 seconds of screen time.
3. **The claim that RL is a third ML paradigm** — this is verbatim S&B §1.1 p. 3 and may be stated as a named fact without proof.

The following are NOT permitted as expansions in this video, regardless of how naturally they arise:
- Any equation in MathTex (no equations in this video)
- Any `CodeStepper` content
- Any reference to $\gamma$, $G_t$, $v_\pi$, $q_\pi$, $\pi(a \mid s)$, or $p(s', r \mid s, a)$

---

## 7. App Metadata Proposal

These fields are proposed for registration in `backend/concept_videos/specs.py` when this lesson is formally onboarded. The Script Writer should treat them as the authoritative identity contract.

```python
LessonVideoSpec(
    lesson_id="rl_intro",
    title="What Is Reinforcement Learning?",
    environment_name="FrozenLake-v1",
    theory_equation="none",           # No equations in this video
    worked_example=(
        "FrozenLake-v1 4×4 grid — agent navigates from start (S) to goal (G) "
        "avoiding holes. Used visually only: no env.step(), no env.unwrapped.P, "
        "no code panel. Demonstrates agent/environment/state/action/reward loop "
        "concretely before abstraction."
    ),
    code_focus_lines=(),              # Empty — no CodeStepper in this video
    misconception_to_prevent=(
        "RL is the same as supervised learning but with delayed feedback. "
        "Refuted by: (1) absence of a supervisor or correct-action labels in RL, "
        "(2) three-way contrast diagram showing Supervised / Unsupervised / RL as "
        "distinct paradigms, (3) S&B §1.1 p. 2–3 citation."
    ),
    takeaway_line=(
        "Reinforcement learning is the science of learning to act by trial and "
        "error — no labels, just rewards."
    ),
    pacing_notes=(
        "Phase 1: FrozenLake concrete motivation (no loop diagram yet). "
        "Phase 2: Three-way ML contrast diagram. "
        "Phase 3: Abstract RL loop diagram — agent box, environment box, "
        "action arrow, state arrow, reward arrow; cycle animated twice. "
        "Phase 4: Four named loop elements with color binding. "
        "Phase 5: Cumulative reward goal — FrozenLake path contrast. "
        "Phase 6: Trial-and-error and delayed reward as named features. "
        "Phase 7: Closing connection to mdp_framework. "
        "No CodeStepper. No equations. No equation_morph calls. "
        "Target duration: 7–10 minutes. A plan under 6 minutes is underspecified."
    ),
)
```

### theory_verification candidates for specs.py

Because this video contains no equations and no Gymnasium API calls, the Technical Validator has a minimal role. Verification candidates are:

| Claim | Verification method |
|---|---|
| FrozenLake-v1 default reward on goal = 1.0 | `env.unwrapped.P[15][any_action]` confirms reward=1.0 on terminal goal state |
| FrozenLake-v1 default reward on non-goal step = 0.0 | `env.unwrapped.P[s][a]` for any non-goal, non-hole s confirms reward=0.0 |
| FrozenLake-v1 is slippery by default (`is_slippery=True`) | `gym.make("FrozenLake-v1").unwrapped.is_slippery` |
| Hole states in 4×4 grid: {5, 7, 11, 12} | Enumerate `env.unwrapped.desc` for `b'H'` bytes |

None of these values appear as on-screen numerics in this video. They are verification candidates only so that any downstream video that references this episode's FrozenLake setup can trace the ground truth back to this spec.

---

## 8. Visual Obligations Summary

The following visual elements are mandatory. The Script Writer's `plan.md` must account for each.

| Visual element | Mandatory? | Color / asset |
|---|---|---|
| FrozenLake 4×4 grid (motivation, Phase 1) | YES | `frozenlake_frame()` with `elf_*.png`, `hole.png`, `goal.png`; STYLE_BIBLE §14 border standard |
| Elf walk animation: one failure (hole), one success (goal) | YES | Sprite motion via `pan_to_follow` or sequential `smooth_move_to` |
| Three-box ML contrast diagram | YES | Plain `RoundedRectangle` panels; RL box in `REWARD_COLOR` border to draw the eye last |
| Abstract RL loop: agent box + environment box | YES | Agent box border `POLICY_COLOR`; environment box border `STATE_COLOR` |
| Action arrow (Agent → Environment) | YES | `ACTION_COLOR` (#FB923C), labeled "Action" |
| State/Observation arrow (Environment → Agent) | YES | `STATE_COLOR` (#38BDF8), labeled "State / Observation" |
| Reward arrow (Environment → Agent) | YES | `REWARD_COLOR` (#34D399), labeled "Reward" |
| Loop animation (full cycle × 2) | YES | Sequential `Indicate` / `Circumscribe` on each node as cycle runs |
| Cumulative reward path contrast (FrozenLake) | YES | Two paths on the grid: one to goal, one to hole |
| "Trial-and-error" and "Delayed reward" as named, captioned concepts | YES | `Text` labels at `OPACITY_PRIMARY` when introduced |
| Closing caption: takeaway line | YES | STYLE_BIBLE §4 caption standard |

**No MathTex.** No `CodeStepper`. No `ValueHeatmap`. No `ActionBarChart`. No `BackupDiagram`. This is a pure motivation and conceptual framing video.

---

## 9. Pacing Notes (advisory)

The STYLE_BIBLE §6 "length policy" applies: content depth determines length; there is no floor shorter than "fully teaches the concept." A 7–10 minute video is the course-plan estimate; the Script Writer should not compress mandatory beats to hit the lower bound.

**Suggested phase structure (7 phases minimum):**

| Phase | Content | Estimated duration |
|---|---|---|
| 1 | FrozenLake motivation — show the problem before naming RL | 1.5–2 min |
| 2 | Three-way ML contrast — what RL is NOT | 1.5 min |
| 3 | Abstract RL loop diagram — agent, environment, arrows | 1.5 min |
| 4 | Cycle animation × 2 — loop as repeating process | 0.75 min |
| 5 | Reward signal and cumulative goal — FrozenLake path contrast | 1.0 min |
| 6 | Trial-and-error + delayed reward as named RL features | 1.0 min |
| 7 | Takeaway line + closing connection to mdp_framework | 0.5 min |

Minimum `self.wait()` values from STYLE_BIBLE §6 apply throughout. The loop diagram reveal (Phase 3) is a "first geometry reveal" — minimum 2.0 s wait after it is complete before any new animation begins.

---

## 10. Series Continuity Notes

**Opening:** This is Video 1. There is no prior video to reference. The opening should frame the series itself: "This is the first video in a series that will take you from this loop all the way to algorithms that solve it."

**Closing connection (mandatory):** The final beat must name `mdp_framework` as the next video and state its purpose: "In the next video, we give this loop a precise mathematical home — the Markov Decision Process." The FrozenLake grid should still be visible at reduced opacity as the connection is made, bridging the two videos visually.

**Terminology lock (STYLE_BIBLE §11):** All canonical terms used in this video must match the series glossary. Specifically:
- Use "state" not "situation" or "observation" as the primary term (note: S&B §1.4 p. 7 uses "state signal" as the formal term; "observation" is acceptable as a synonym when emphasizing partial observability, but this video should prefer "state" for simplicity)
- Use "episode" not "run" or "trial" if the word is used at all (it need not be used in this video)
- Use "reward signal" (compound noun) when referring to the feedback mechanism, as in S&B §1.3

---

## 11. "Do Not Oversimplify" Notes

These are binding constraints on the Script Writer and Manim Expert. Each is traceable to a specific S&B passage.

1. **Do not say "the agent chooses the best action."** At this stage the agent does not know which action is best — that is the entire problem. Correct phrasing: "the agent *tries* an action" or "the agent *chooses* an action." (S&B §1.1 p. 1: "the learner is not told which actions to take, but instead must discover which actions yield the most reward by trying them.")

2. **Do not say "reward = +1 for good, -1 for bad."** FrozenLake-v1 defaults give 0 for every step and 1 for the goal. Holes give 0 and terminate. The reward scheme is environment-specific. Do not imply a universal ±1 convention.

3. **Do not call the reward "the agent's score."** Score implies an external evaluator that has full knowledge of performance. The reward is a signal from the *environment's dynamics*, not from an omniscient judge. (S&B §1.3 p. 6.)

4. **Do not imply the agent has access to the environment's internals.** The FrozenLake elf does not know the ice slip probabilities or the reward function formula. It only receives observations and rewards. The distinction matters because `mdp_framework` will introduce the full dynamics function — presenting the agent as having that knowledge here would create a conceptual contradiction.

5. **Do not say "the agent learns the optimal policy in this video."** This video establishes *what RL is*; it does not show *how RL solves anything*. The elf walk animation shows *the problem* (navigating with trial-and-error), not the solution. The elf in Phase 1 should walk somewhat randomly to make this clear.

6. **Do not conflate "state" and "observation."** For FrozenLake, the state is fully observable (the elf knows which tile it stands on). But the spec uses "State / Observation" as the label on the loop diagram arrow to flag that in general these can differ. The caption should note: "In FrozenLake, the agent sees its exact state — not always the case in RL." This seeds the partial observability concept without teaching it.

---

## 12. S&B Citation Map

All factual claims in the video must trace to one of the following:

| Claim | S&B location |
|---|---|
| RL definition: learning to map situations to actions to maximize reward | §1.1, p. 1 |
| Trial-and-error and delayed reward as RL's two distinguishing features | §1.1, p. 2 |
| RL vs. supervised learning: no labeled examples, no supervisor | §1.1, pp. 2–3 |
| RL vs. unsupervised learning: goal is reward maximization, not finding hidden structure | §1.1, p. 3 |
| RL as a third ML paradigm | §1.1, p. 3 |
| Agent must sense state, take actions that affect state, have a goal | §1.1, p. 2 |
| Reward signal: single number per time step, agent maximizes total over long run | §1.3, p. 6 |
| Four subelements of RL systems: policy, reward signal, value function, model | §1.3, pp. 6–7 (acknowledged as existing; only reward signal taught here) |
| Exploration–exploitation dilemma | §1.1, p. 3 (named only, not taught) |
