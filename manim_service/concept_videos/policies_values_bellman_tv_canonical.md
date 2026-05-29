# Technical Validator — canonical values for policies_values_bellman

**Date:** 2026-05-27
**Run:** /Users/ultramarine/.venvs/manim/bin/python — live Gymnasium policy evaluation
**Env:** FrozenLake-v1, is_slippery=True, γ=0.99, equiprobable random π
**Convergence:** 93 sweeps to ||v_{k+1} − v_k||_∞ < 1e-10

## Canonical v_π array (to be hard-coded by Manim Expert)

```python
v_pi = [
    0.012356,  # s=0  (start)
    0.010424,  # s=1
    0.019338,  # s=2
    0.009478,  # s=3
    0.014787,  # s=4
    0.000000,  # s=5  (hole, terminal)
    0.038894,  # s=6
    0.000000,  # s=7  (hole, terminal)
    0.032602,  # s=8
    0.084338,  # s=9
    0.137811,  # s=10
    0.000000,  # s=11 (hole, terminal)
    0.000000,  # s=12 (hole, terminal)
    0.170345,  # s=13
    0.433579,  # s=14
    0.000000,  # s=15 (goal, terminal)
]
```

Full precision (10 decimals):
```python
[0.0123561369, 0.0104244607, 0.0193384356, 0.0094777481,
 0.0147870513, 0.0000000000, 0.0388944493, 0.0000000000,
 0.0326024739, 0.0843376420, 0.1378108544, 0.0000000000,
 0.0000000000, 0.1703448215, 0.4335794415, 0.0000000000]
```

## On-screen display values (3-decimal, used in plan.md heatmap table)

| s | v_π(s) display | s | v_π(s) display | s | v_π(s) display | s | v_π(s) display |
|---|---|---|---|---|---|---|---|
| 0 | 0.012 | 4 | 0.015 | 8 | 0.033 | 12 | 0.000 |
| 1 | 0.010 | 5 | 0.000 | 9 | 0.084 | 13 | 0.170 |
| 2 | 0.019 | 6 | 0.039 | 10 | 0.138 | 14 | 0.434 |
| 3 | 0.009 | 7 | 0.000 | 11 | 0.000 | 15 | 0.000 |

## q_π(14, a) — for S4-P12 bar chart

| Action | q_π(14, a) |
|---|---|
| 0 = LEFT | 0.244773 |
| 1 = DOWN | 0.532628 |
| 2 = RIGHT | 0.521892 |
| 3 = UP | 0.435025 |
| **mean** | **0.433579** ( = v_π(14) ✓) |

## Verified facts (all PASS at machine precision)

- `env.observation_space.n` = 16
- `env.action_space.n` = 4
- `env.unwrapped.P[s][a]` returns list of `(prob, next_state, reward, done)` 4-tuples
- Terminal states {5, 7, 11, 12, 15} all have v_π = 0.0 exactly
- mean(q_π(14, ·)) − v_π(14) = 1.11e−11 (linking identity holds)
- Bellman LHS = RHS at state 6: |diff| = 1.87e−11
- CodeStepper with v_prev = 0, state 6: result = 0.000000 (V-03 hand-off confirmed)

## Narration approximation notes

- "Heatmap value at state 6 ≈ 0.039" (was 0.041; updated 2026-05-27)
- "Value at state 14: 0.434" (was 0.439; updated 2026-05-27)
- "max v_π ≈ 0.43" (was 0.44; updated 2026-05-27)

## Edits applied to artefacts (audit trail)

- plan.md lines 591–594: heatmap table updated to measured values
- plan.md: all `0.041` → `0.039`, `0.439` → `0.434`, `0.44` → `0.43` (replace_all)
- specs.md lines 314–328: heatmap table updated
- specs.md: same number substitutions applied (including 0.014 → 0.012 in references)
- choreo.md: same number substitutions in trace_vector captions and LHS/RHS panels
