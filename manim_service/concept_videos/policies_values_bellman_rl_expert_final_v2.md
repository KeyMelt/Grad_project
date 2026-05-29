## RL Expert Review — policies_values_bellman

**Verdict: APPROVED**

**Reviewed:** Rendered + narrated artifact (Gate 7 final sign-off)
**Lesson ID:** `policies_values_bellman`
**Series position:** V-02 of restructured RL curriculum
**Date:** 2026-05-28
**Reviewed against:** S&B §3.5 pp. 58–60 (eqs. 3.12–3.14); `rl_knowledge_base.md`; TV canonical
(live Gymnasium run, 2026-05-27); narration_script.md; choreo.md; plan.md; specs.md

---

### Step 1 — Scope confirmation

Teaching spec §1.1 declares three objectives for this video:

1. Policy $\pi(a \mid s)$ — S&B §3.5 p. 58
2. Value functions $v_\pi(s)$ and $q_\pi(s,a)$ — S&B eq. (3.12)–(3.13) p. 58
3. Bellman expectation equation for $v_\pi$ — S&B eq. (3.14) p. 59

Scope is appropriate. The lesson occupies the correct DAG position: downstream of
`rl_mdp_core` (V-01) and upstream of `dp_policy_eval` (V-03). No V-03+ material
(iterative pseudocode, argmax, $v_*$, policy iteration, value iteration) is
introduced in the plan, narration, or rendered artifact.

---

### Step 2 — Bellman derivation faithfulness to S&B eq. (3.14)

Plan §3.4 and Segment 5 (S5-P14 through S5-P19) present the five-step derivation:

| Step | Plan form | S&B alignment |
|---|---|---|
| 1 | $v_\pi(s) \doteq \mathbb{E}_\pi[G_t \mid S_t = s]$ | S&B eq. (3.12) p. 58. Correct entry point. |
| 2 | $= \mathbb{E}_\pi[R_{t+1} + \gamma G_{t+1} \mid S_t = s]$ | Substitutes eq. (3.9) p. 55. Correct. |
| 3 | $= \sum_a \pi(a \mid s)\, \mathbb{E}[R_{t+1} + \gamma G_{t+1} \mid S_t=s, A_t=a]$ | Conditioning on $A_t = a$, pulling $\pi$ out. Correct. |
| 4 | $= \sum_a \pi(a \mid s) \sum_{s',r} p(s',r \mid s,a)[r + \gamma\,\mathbb{E}_\pi[G_{t+1} \mid S_{t+1}=s']]$ | Conditioning on $(S_{t+1}, R_{t+1})$, pulling $p$ out. Correct. |
| 5 | $= \sum_a \pi(a \mid s) \sum_{s',r} p(s',r \mid s,a)[r + \gamma\, v_\pi(s')]$ | Recognizes $\mathbb{E}_\pi[G_{t+1}\mid S_{t+1}=s'] = v_\pi(s')$. Correct. Recursion closes. |

Final boxed form displayed in S5-P19:
$$v_\pi(s) = \sum_a \pi(a \mid s) \sum_{s',r} p(s',r \mid s,a)\bigl[r + \gamma\, v_\pi(s')\bigr]$$

This matches S&B eq. (3.14) p. 59 exactly. The two sums are presented separately
throughout the derivation and are never collapsed to $\sum_{a,s',r}$, consistent
with the "two sources of randomness" pedagogical requirement (specs §3.4; S&B p. 59).

The plan correctly avoids every prohibited variant listed in specs §3.6:
- Does not use uppercase $V$ without subscript $\pi$ anywhere
- Does not collapse the two sums
- Presents the equation as an equality (fixed-point identity), not an assignment

**Derivation: FAITHFUL to S&B eq. (3.14).**

---

### Step 3 — Narration script review

#### 3.1 Banned terms audit (STYLE_BIBLE §11 + specs §7.3)

Scanned all 26 phases of narration_script.md for prohibited terms:

| Banned term | Appears? | Location |
|---|---|---|
| "optimal policy" / "best policy" | No | — |
| "value iteration" | No | — |
| "policy iteration" | No | — |
| "argmax" | No | — |
| "the Bellman equation tells you how to update V" | No | — |
| "Bellman's equation" (unqualified) | No | P19: "the *Bellman expectation equation* for v-sub-pi" — correctly qualified |
| "Q-value" without prior full name | No | First use at P11: "v-sub-pi" and "action-values" introduced before bar discussion |
| "greedy policy" | No | — |
| "dynamics function" (excess uses) | No | Not used explicitly; "p" and "transition probability" preferred throughout |

**No banned terms found.**

#### 3.2 V-03 hand-off check (specs §4.6, §12.7)

Phase S7-P23 narration (t=1:19:29–1:19:59):
> "One sweep is not enough — the heatmap takes many sweeps to emerge. *V-03* is
> where we iterate this loop until the numbers stop changing."

Phase S8-P25 narration (t=1:20:29–1:20:51):
> "Turn the equality into an *assignment*. Sweep every state. Repeat until nothing
> changes. That algorithm is the next video — *policy evaluation*. v-sub-pi is
> the fixed point it converges to."

The hand-off correctly:
- Names V-03 / "policy evaluation" by name
- Describes the transformation ($=\to\leftarrow$, sweep, repeat)
- Does **not** write out $v_{k+1}(s) \leftarrow \ldots$ in pseudocode form
- Presents the Bellman equation as the fixed-point condition, not the update rule

**V-03 hand-off: CORRECTLY SCOPED.**

#### 3.3 Misconception defeats in narration

All six misconceptions from specs §5.1 are addressed:

- **M-1** (policy = function): P4 narration "it is a *distribution* that happens, sometimes, to put all its mass on one action" — correct framing.
- **M-2** (value = reward): P8 narration "Value is not what you get *now*. Value is what you can *expect* later" — explicit and correct.
- **M-3** (one sum): P13 narration "Two layers of randomness. Two distinct sums are about to appear" + P17 "The outer sum is over actions. The inner sum is over transitions. They never collapse into one" — explicit.
- **M-4** (deterministic shortcut): Equiprobable policy is the working policy from P5 onward; deterministic policy is FadedOut.
- **M-5** ($v$ and $q$ unrelated): P12 narration directly states the averaging identity.
- **M-6** (equation = update rule): P20 "The Bellman equation does not *compute* v-sub-pi. It *checks* that v-sub-pi is itself" — explicit equality framing.

**Narration: APPROVED.**

---

### Step 4 — Frame inspection

Four frames extracted from the narrated MP4 using `frame_selector --spot-check 4`.

#### Frame 1 — t=630.5 s (boundary: end of S4, phase S4-P12_v_from_q)

**Observed:** Left panel shows the $q_\pi$ definition equation (dimmed to SECONDARY).
Center shows the FrozenLake heatmap with visible numerical cell labels. Right panel
shows the four action-value bars for state 14 with values approximately labeled
0.24 (L), 0.53 (D), 0.52 (R), 0.44 (U).

**Checks:**
- Bar values: TV canonical gives $q_\pi(14, L)=0.244773$, $q_\pi(14, D)=0.532628$,
  $q_\pi(14, R)=0.521892$, $q_\pi(14, U)=0.435025$. Displayed values 0.24/0.53/0.52/0.44
  match TV canonical to 2 decimal places (display precision). **PASS.**
- Heatmap visible values: state 14 shows 0.434, state 13 shows 0.170 — match TV canonical. **PASS.**
- No $v_*$ or optimal-value symbol visible. **PASS.**
- No iterative-assignment form visible. **PASS.**
- Stale-visual check: left panel contains the q definition equation from S4-P10, still
  dimmed appropriately at the S4 segment boundary. No stale PRIMARY elements from prior
  segments. **PASS.**

#### Frame 2 — t=744.9 s (eq_diss: S5-P15_return_recursion_in_expectation)

**Observed:** Left panel shows the derivation equation at Step 2:
$v_\pi(s) = \mathbb{E}_\pi[R_{t+1} + \gamma G_{t+1} \mid S_t = s]$.
Right panel shows the backup diagram rooted at state 6, with action nodes L/D/R/U
in orange (`ACTION_COLOR`), and the DOWN branch subtree braced as "$G_{t+1}$" with
"$R_{t+1}$" labeling an edge from root in teal/green (`REWARD_COLOR`).

**Checks:**
- Equation at Step 2 matches S&B derivation on p. 59 exactly: the $G_t$ from the
  definition has been substituted by the recursion $R_{t+1} + \gamma G_{t+1}$.
  **PASS.**
- Color assignments: action nodes orange (`ACTION_COLOR`), reward label green
  (`REWARD_COLOR`). Correct per specs §6.2. **PASS.**
- Backup diagram root is labeled "6" (`STATE_COLOR` blue circle). **PASS.**
- No $v_*$ symbol visible. Correct — this is Step 2 of the derivation;
  $v_\pi(s')$ does not appear until Step 5. **PASS.**
- The equation shows $v_\pi(s)$ (subscript $\pi$, lowercase $v$) — not $V(s)$
  or $v_*(s)$. **PASS.**
- Forward-tease label check (P25 is not yet active at t=744.9 s; this frame is in
  the middle of the five-step derivation, which is the correct location). **PASS.**

#### Frame 3 — t=1021.0 s (code_walk: S7-P21_code_entry)

**Observed:** Left panel shows the FrozenLake heatmap. Center-right shows the
CodeStepper panel labeled "bellman_evaluator.py" (partially legible; the brighter
frame at t=1199.8 confirms full label). Code lines visible including
`env = gym.make('FrozenLake-v1'...)`, `pi = np.ones(ns, 4) / 4`, `gamma = 0.99`,
`P = env.unwrapped.P`, `v_prev = np.zeros(ns)`, `s = 6`, `v_new = 0.0`,
inner/outer loop structure.

**Checks:**
- `env.unwrapped.P` is visible — correct API access bypassing wrappers, per
  Gymnasium convention and specs §9.2. **PASS.**
- `gamma = 0.99` — consistent with V-01 and specs §4.1. **PASS.**
- `v_prev = np.zeros(ns)` — the zero initial guess for the V-03 hand-off.
  This is the correct CodeStepper demonstration. **PASS.**
- `s = 6` — state 6 as the worked example, per specs §4.5. **PASS.**
- Heatmap cell values visible: bottom row shows 0.170 and 0.434 for states 13
  and 14 — match TV canonical. **PASS.**
- No `done` variable in lieu of `terminated or truncated` — the inner loop
  variable is `d` (the legacy four-tuple `done` from `env.unwrapped.P`, which is
  correct here because `env.unwrapped.P` stores the old 4-tuple convention for
  model data, not the step-return 5-tuple). This is consistent with the
  knowledge base and specs §9.2 code block. **PASS.**
- No $v_*$ or optimal-policy reference visible. **PASS.**

#### Frame 4 — t=1199.8 s (boundary: end of S7, phase S7-P23_zero_output_handoff)

**Observed:** Left panel shows the FrozenLake heatmap with state 14=0.434,
state 13=0.170. Center shows the CodeStepper panel (fully legible) with line 12
`print(f'{v_new:.6}')` highlighted in yellow. Below the code panel, three caption
lines: "Heatmap value: 0.039" / "Code RHS from v_prev=0: 0.000000" / "One sweep
is not enough — V-03 will iterate."

**Checks:**
- Heatmap value 0.039 at state 6 (visible in the grid): matches TV canonical
  $v_\pi(6) = 0.038894 \approx 0.039$. **PASS.**
- Code output "0.000000": correct per TV canonical verification ("CodeStepper
  with v_prev=0, state 6: result = 0.000000"). **PASS.**
- Caption "One sweep is not enough — V-03 will iterate": correctly names V-03
  without showing V-03 pseudocode or the $v_{k+1} \leftarrow$ assignment form.
  The morph ($=\to\leftarrow$) has not yet occurred at t=1199.8 s (that is P25
  at t=1230 s). **PASS.**
- No $v_*$ symbol visible. **PASS.**
- **P25 forward-tease check:** P25 starts at t=1230.0 s (per phase_timestamps.json).
  At t=1199.8 s the video is still in S7-P23. The morph $=\to\leftarrow$ has not
  triggered at this frame. P25 is correctly deferred and will hold for
  $1260 - 1230 = 30$ s total (≤ 1.5 s for the morph itself per specs §4.6;
  the 30 s slot includes narration lines before and after the morph). **PASS.**
- **Ghost yellow-stroke rectangle (known residual from prior QA):** Not visible
  in this frame. The residual was documented as cosmetic and frame-limited to P26.
  At t=1199.8 s (P23 end) it is not present. **PASS at this frame; cosmetic
  residual noted below.**

---

### Accuracy notes (non-blocking)

1. **P25 ghost yellow-stroke rectangle (cosmetic, P26 only):** Carried forward
   from prior QA as a known residual. Confirmed absent at t=1199.8 s; may appear
   in the final hold P26 at t=1260+ s. Cosmetic only — no RL content affected.
   Recommend repair before series-library archival but does not block this gate.

2. **P25 zoom timing (known residual):** The $=\to\leftarrow$ morph timing was
   flagged as slightly fast in prior QA. Per specs §4.6 the morph must be ≤ 1.5 s;
   not directly observable at t=1199.8 s. The morph content is pedagogically
   correct (it reverts to the equality after ≤ 1.5 s, plants the V-03 seed without
   committing the assignment form). Non-blocking.

3. **Narration timing at P19 (boxed Bellman reveal):** Narration line
   "Let it sit for a moment" at t=1:15:54 maps to a 5-second tail in a 40-second
   phase. This gives adequate hold time for the full-frame solo, consistent with
   the STYLE_BIBLE §33.2 ≥ 2.5 s hold requirement.

4. **State 10 on-screen value (0.138):** TV canonical gives $v_\pi(10) = 0.137811$.
   Rounded to three decimals: 0.138. Narration line at P7 ("fourteen percent") is
   approximate narration, acceptable per specs §7.2 register.

---

### Prerequisite check: PASS

All concepts used in `policies_values_bellman` are introduced at or before V-02
in the DAG:

- $S$, $A$, $R$, $p(s',r\mid s,a)$, $G_t$, $\gamma$, recursion $G_t=R_{t+1}+\gamma G_{t+1}$,
  FrozenLake-v1 — all from V-01 (`rl_mdp_core`). Correctly recalled via Segment 1 recap.
- $\pi(a\mid s)$, $v_\pi(s)$, $q_\pi(s,a)$, linking identity, Bellman expectation eq.,
  backup diagram — all first introduced in this video (V-02). Correct.
- No V-03+ concepts (iterative policy evaluation, argmax, $v_*$, $\pi_*$, Bellman
  optimality) appear in any phase. Correct.

The DAG edge `rl_mdp_core → policies_values_bellman → dp_policy_eval` is respected.

---

### Equation accuracy: PASS

| Equation | Screen form | S&B reference | Status |
|---|---|---|---|
| Policy definition | $\pi(a\mid s) \doteq \Pr\{A_t=a\mid S_t=s\}$ | §3.5, p. 58 | MATCH |
| Policy normalization | $\sum_a \pi(a\mid s) = 1$ | §3.5, p. 58 | MATCH |
| State-value function | $v_\pi(s) \doteq \mathbb{E}_\pi[G_t\mid S_t=s]$ | eq. (3.12), p. 58 | MATCH |
| Action-value function | $q_\pi(s,a) \doteq \mathbb{E}_\pi[G_t\mid S_t=s, A_t=a]$ | eq. (3.13), p. 58 | MATCH |
| Linking identity | $v_\pi(s) = \sum_a \pi(a\mid s)\, q_\pi(s,a)$ | §3.5, p. 58 (derived) | MATCH |
| Bellman derivation — Step 2 (frame-verified) | $= \mathbb{E}_\pi[R_{t+1}+\gamma G_{t+1}\mid S_t=s]$ | eq. (3.9), p. 55 + §3.5 derivation, p. 59 | MATCH |
| Bellman eq. final boxed form | $v_\pi(s)=\sum_a \pi(a\mid s)\sum_{s',r}p(s',r\mid s,a)[r+\gamma v_\pi(s')]$ | eq. (3.14), p. 59 | EXACT MATCH |
| Terminal-state boundary | $v_\pi(s_T) = 0$ for $s_T \in \{5,7,11,12,15\}$ | §3.3, p. 55 + §3.5, p. 58 | CORRECT |

No prohibited variant forms detected ($V[s]$ uppercase, single-sum collapse,
$v_*$ subscript) in any verified frame or in the plan's MathTex arrays.

---

### API fidelity: PASS

| Check | Code form | Gymnasium convention | Status |
|---|---|---|---|
| Model access | `env.unwrapped.P[state][action]` | `.unwrapped` required to bypass wrappers | CORRECT |
| Loop unpacking | `for prob, next_state, reward, done in env.unwrapped.P[state][action]` | 4-tuple from `.P` (model data, not step-return) | CORRECT |
| Policy construction | `pi = np.ones((n_states, n_actions)) / n_actions` | Equiprobable, $|\mathcal{A}(s)|=4$ for all $s$ in FrozenLake | CORRECT |
| Normalization assert | `np.allclose(pi.sum(axis=1), 1.0)` | Row-stochastic check | CORRECT |
| Discount | `gamma = 0.99` | Consistent with V-01 | CORRECT |
| Environment | `gym.make("FrozenLake-v1", is_slippery=True)` | Canonical series environment | CORRECT |

Note: the CodeStepper uses the 4-tuple unpacking from `env.unwrapped.P` (model
access convention), NOT the 5-tuple from `env.step()`. This is correct and
consistent with the distinction drawn in the knowledge base: DP model access uses
the 4-tuple; online interaction uses the 5-tuple. The `done` variable in the
inner loop is from the model table, not from `env.step()`, so using it here is
correct per the `dp_policy_eval` knowledge-base entry and specs §9.2.

---

### Numerical values: PASS (TV canonical verified)

| State | On-screen value | TV canonical | Delta | Status |
|---|---|---|---|---|
| $v_\pi(14)$ | 0.434 | 0.433579 | 0.0004 | PASS (< 0.005 threshold) |
| $v_\pi(13)$ | 0.170 | 0.170345 | 0.0003 | PASS |
| $v_\pi(6)$ | 0.039 | 0.038894 | 0.0001 | PASS |
| $v_\pi(0)$ | 0.012 | 0.012356 | 0.0004 | PASS |
| $q_\pi(14,L)$ | 0.24 | 0.244773 | 0.005 | PASS (boundary) |
| $q_\pi(14,D)$ | 0.53 | 0.532628 | 0.003 | PASS |
| $q_\pi(14,R)$ | 0.52 | 0.521892 | 0.002 | PASS |
| $q_\pi(14,U)$ | 0.44 | 0.435025 | 0.005 | PASS (boundary) |
| CodeStepper output (state 6, v_prev=0) | 0.000000 | 0.000000 | 0 | EXACT |
| Terminal states {5,7,11,12,15} | 0.000 | 0.000000 | 0 | EXACT |

Bellman LHS=RHS at state 6: TV canonical |diff| = 1.87e−11. Displayed as
"≈ 0.039" on both sides. Correct.

---

### Series hand-off: PASS

V-03 hand-off is correctly staged:
- S7-P23 caption "One sweep is not enough — V-03 will iterate" names V-03 without
  showing its algorithm.
- S8-P25 morph ($=\to\leftarrow$, $v_\pi\to v_{k+1}$, $v_\pi(s')\to v_k(s')$)
  is a ≤ 1.5 s visual tease that **reverts** per specs §4.6 — the equality form
  is the canonical endpoint.
- S8-P26 takeaway: "$v_\pi$ is the fixed point of the Bellman equation" correctly
  positions V-02 as the equation video and V-03 as the algorithm video.

The hand-off satisfies the architectural contract: a student entering V-03
(`dp_policy_eval`) has seen the Bellman expectation equation as a fixed-point
equality, has been shown one Gymnasium evaluation step returning 0.000000 from
a zero guess, and has been told that V-03 will sweep until convergence. V-03's
first phase can proceed directly to the assignment form $v_{k+1}(s) \leftarrow
\text{RHS}(v_k)$ without re-deriving the equation.

---

### Summary

This artifact satisfies all academic-accuracy requirements for Gate 7:

1. All three core concepts (policy, value functions, Bellman eq.) are correctly
   defined per S&B §3.5 pp. 58–60.
2. The Bellman derivation is faithful to eq. (3.14) p. 59 across all five steps.
3. All six misconceptions from specs §5.1 are explicitly defeated in narration
   and geometry.
4. No prerequisite violations: no V-03+ algebra appears anywhere.
5. All four spot-check frames confirm correct on-screen content:
   - Equation forms use $v_\pi$ (subscript policy, not $v_*$ or $V$)
   - Numerical values match TV canonical within display precision
   - CodeStepper output 0.000000 confirmed correct
   - V-03 hand-off caption is correctly scoped at t=1199.8 s
6. Gymnasium API usage is correct throughout.
7. Two known cosmetic residuals (P26 ghost stroke, P25 zoom pacing) are
   non-blocking and do not affect RL content.
