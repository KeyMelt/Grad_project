## RL Expert Review — policies_values_bellman

**Verdict: APPROVED**

**Reviewed:** polished_scene.py + narrated MP4 + narration_script.md — Gate 7 re-check after STYLE_BIBLE §11 terminology patches
**Date:** 2026-05-28

---

### Scope of this re-check

The prior Gate 7 approval (rl_expert_final_v2.md) was granted on the full RL content.
This re-check is **scoped to three patch points only**:

1. `scene.py` line 241 — subtitle "The agent's strategy" → "The agent's decision rule"
2. `narration_script.md` lines 69, 298–299 — "strategy" → "memorised solution"; "value function" → "state-value function"
3. Captions updated to match narration

No RL content (equations, numerical values, derivation structure) changed.

---

### 1. RL content unchanged — verification

**V_PI array (scene.py lines 67–72):**
```python
V_PI = [
    0.012356, 0.010424, 0.019338, 0.009478,
    0.014787, 0.000000, 0.038894, 0.000000,
    0.032602, 0.084338, 0.137811, 0.000000,
    0.000000, 0.170345, 0.433579, 0.000000,
]
```
Matches `tv_canonical.md` to 6 decimal places. ✓

**Key canonical values (S&B §3.5, eq. 3.12):**
- `v_π(14) = 0.433579` → displayed as `0.434` ✓ (narration: "0.434", P7 line 117)
- `v_π(13) = 0.170345` → displayed as `0.170` ✓ (narration: "0.170", consistent with heatmap)
- `v_π(6) = 0.038894` → displayed as `0.039` ✓ (narration line 243: "approximately 0.039")
- `γ = 0.99` — present in `CODE_LINES[3]` ("gamma = 0.99") and legend text ✓

**Q_14 array (scene.py line 74):**
```python
Q_14 = [0.244773, 0.532628, 0.521892, 0.435025]
```
Mean = 0.433579 = v_π(14). Linking identity holds. ✓ (matches tv_canonical.md)

**Bellman equation (scene.py lines 525–526, 543–544, 672–673):**
All three renditions of the boxed equation show:
$$v_\pi(s) = \sum_a \pi(a\mid s) \sum_{s',r} p(s',r\mid s,a)[r + \gamma v_\pi(s')]$$
Matches S&B eq. (3.14), p. 59. ✓

**v_π notation:** consistently `v_\pi(s)` throughout. ✓

---

### 2. Frame inspection (5 frames, 4 from spot-check + 1 subtitle)

**Frame 1 — `frame_subtitle.png` (t=62s, silent MP4, phase S2-P3)**
Header reads: "Policies" / "The agent's decision rule"
The patched subtitle is confirmed on-screen. The framing "decision rule" is precise S&B §3.5 language:
> "A policy is a mapping from states to probabilities of selecting each possible action." (S&B p. 58)
The phrase "decision rule" correctly conveys that π is a state-conditional prescription for action selection, not an executed plan. ✓

**Frame 2 — `frame_t630_S4P12_boundary.png` (t=630.5s, narrated MP4, phase S4-P12 boundary)**
Shows: q_π definition faded left, action-value bar chart right (bars for L/D/R/U at state 14), heatmap bottom-center.
Bar values visible: 0.24, 0.53, 0.52, 0.44 — matches Q_14 to 2 decimal places. ✓
No stale visual artifacts at segment boundary. ✓

**Frame 3 — `frame_t744_S5P15_eq_diss.png` (t=744.9s, narrated MP4, phase S5-P15)**
Shows: derivation step 2 — equation LHS visible as `= E_π[R_{t+1} + γG_{t+1} | S_t = s]`, backup diagram right with R_{t+1} and G_{t+1} labels.
Equation form matches S&B §3.5 derivation structure (return recursion substituted into expectation). ✓
The brace over outcome nodes for G_{t+1} is correct — G_{t+1} is the future return from the successor state, not a single reward. ✓

**Frame 4 — `frame_t1021_S7P21_code_walk.png` (t=1021s, narrated MP4, phase S7-P21)**
Shows: two-panel layout — FrozenLake heatmap left, IDE code panel right.
Code line 4 reads `gamma= 0.99`, line 5 `P = env.unwrapped.P`. ✓
`env.unwrapped.P` access is correct Gymnasium API (bypasses OrderEnforcing/TimeLimit wrappers). ✓
Heatmap values visible: row-0 shows 0.012, 0.010 (partially visible), 0.019, 0.009. Consistent with V_PI. ✓

**Frame 5 — `frame_t1199_S7P23_boundary.png` (t=1199.8s, narrated MP4, phase S7-P23 boundary)**
Shows: full IDE panel with all 12 code lines, heatmap left, caption block bottom.
Caption reads: "Heatmap value: 0.039 / Code RHS from v_prev=0: 0.000000 / One sweep is not enough - V-03 will iterate."
Line 4: `gamma= 0.99` ✓; Line 5: `P = env.unwrapped` (truncated display but correct) ✓
Heatmap values s=13: 0.170, s=14: 0.434. ✓
The "one sweep is not enough" caption correctly motivates V-03 (dp_policy_eval). ✓

---

### 3. Narration §11 terminology patch — RL accuracy scan

**Patch A — line 69:**
> "Notice what this is not — it is not a **memorised solution**, not a plan, not an answer."

**Assessment:** Accurate and improved. The prior "strategy" was too colloquial and carried game-theory connotations. "Memorised solution" correctly distinguishes a policy from a lookup table of optimal actions, which would be a solved MDP, not a policy in the S&B sense. S&B §3.5 p. 58 states the policy is a *mapping* (not a stored solution), and S&B Chapter 4 explicitly reserves "solution" language for the optimal policy/value pair. The phrasing "not a memorised solution" preempts the common misconception that a policy is equivalent to a finished plan or optimal action sequence. ✓

**Patch B — line 298:**
> "A **policy** is a distribution over actions. A **state-value function** is the expected return under that policy."

**Assessment:** "State-value function" is the exact S&B §3.5 terminology (p. 58: "the value function of a state s under a policy π, denoted v_π(s)"). The prior "value function" without qualification was acceptable but ambiguous (could refer to q_π). The patch adds precision with no cost. ✓

**Patch C — line 299:**
> "The Bellman equation is the *self-consistency* the true **state-value function** must satisfy."

**Assessment:** Correct. The Bellman expectation equation for v_π (S&B eq. 3.14) is a self-consistency condition: v_π is the unique fixed point of the Bellman operator T^π. S&B §3.5 p. 59: "the value function v_π is the unique solution to its Bellman equation." The phrase "self-consistency" is an accurate and pedagogically appropriate gloss. ✓

---

### 4. Accuracy notes (non-blocking)

- **Scene.py line 241** — `self.show_header("Policies", "The agent's decision rule")` — subtitle confirmed on-screen at t=62s as "The agent's decision rule". Pedagogically sound per S&B §3.5 framing. ✓
- No new RL inaccuracies introduced by the §11 patches. The three patch points improve terminology precision without altering any mathematical content.

---

### Prerequisite check: PASS

All concepts in the patched regions (policy as distribution, state-value function, Bellman self-consistency) are introduced at or before `policies_values_bellman` in the prerequisite DAG (this video IS the introduction of these concepts). No forward-DAG terms used without inline definition. ✓

---

### Equation accuracy: PASS

| Equation | Location | S&B reference |
|---|---|---|
| $\pi(a\mid s) \doteq \Pr\{A_t=a\mid S_t=s\}$ | scene.py line 243 | S&B §3.5, p. 58 |
| $v_\pi(s) \doteq \mathbb{E}_\pi[G_t \mid S_t=s]$ | scene.py line 304 | S&B §3.5, eq. (3.12), p. 58 |
| $q_\pi(s,a) \doteq \mathbb{E}_\pi[G_t \mid S_t=s, A_t=a]$ | scene.py line 383 | S&B §3.5, eq. (3.13), p. 58 |
| $v_\pi(s) = \sum_a \pi(a\mid s)\sum_{s',r}p(s',r\mid s,a)[r+\gamma v_\pi(s')]$ | scene.py lines 525, 543, 672 | S&B §3.5, eq. (3.14), p. 59 |
| $v_{k+1}(s) \leftarrow \sum_a \pi(a\mid s)\sum_{s',r}p(s',r\mid s,a)[r+\gamma v_k(s')]$ | scene.py line 688 (forward tease) | S&B §4.1, eq. (4.5), p. 75 |

All five equations match S&B exactly. ✓

---

### API fidelity: PASS

| API call | Location | Verdict |
|---|---|---|
| `env.unwrapped.P` | scene.py line 96 / CODE_LINES[4] | Correct — bypasses wrappers per Gymnasium convention ✓ |
| `for p, sp, r, d in P[s][a]:` | scene.py line 101 / CODE_LINES[9] | Correct 4-tuple unpacking from `P[s][a]` ✓ |
| `env.observation_space.n` | scene.py line 93 / CODE_LINES[1] | Correct access for `|S|` ✓ |
| `gym.make('FrozenLake-v1')` | scene.py line 92 / CODE_LINES[0] | Correct; `is_slippery=True` is the default ✓ |

Note: The code deliberately uses the legacy 4-tuple `(p, sp, r, d)` from `env.unwrapped.P[s][a]` rather than `env.step()`. This is correct — `env.unwrapped.P` is a model table, not a step return. The 5-tuple Gymnasium API convention applies only to `env.step()`, which is not called anywhere in this scene's code. ✓

---

### Summary

The three §11 terminology patches improve precision without introducing any RL inaccuracy:
1. "The agent's decision rule" — correct S&B §3.5 framing, confirmed on-screen at t=62s.
2. "Not a memorised solution" — accurately distinguishes policy from lookup table.
3. "State-value function" — exact S&B §3.5 terminology, replacing ambiguous "value function".

All Bellman equations, numerical values (v_π(14)=0.434, v_π(13)=0.170, γ=0.99), and derivation structure are unchanged and verified correct. Five frames inspected (4 spot-check from narrated MP4 + 1 subtitle from silent MP4), all consistent with the approved content.
