# Codex Brief — mdp_foundations — stage: full_pipeline

## Identity
- lesson_id: mdp_foundations
- manim_class: MdpFoundationsScene
- stage: full_pipeline
- python: /Users/ultramarine/.venvs/manim/bin/python
- project_root: /Users/ultramarine/Desktop/grad_project

## What this brief covers
This is a full_pipeline brief. You must complete ALL of the following in a single
session, in order:

  1. Script Writer  → write `mdp_foundations_plan.md`
  2. Visual Director → write `mdp_foundations_choreo.md`
  3. Gate 1 RL Expert review → verdict on plan.md + choreo.md
  4. Gate 2 Technical Validator → live Gymnasium checks + numeric pin
  5. Manim scene_render → generate `mdp_foundations_concept.py` + render silent MP4

Do not stop between steps. Do not ask for confirmation. Run each step to
completion before moving to the next.

---

## Inputs (read these from disk before starting Step 1)

- teaching_spec:  manim_service/concept_videos/mdp_foundations_specs.md   ← PRIMARY authority
- style_bible:    manim_service/concept_videos/docs/STYLE_BIBLE.md
- rl_knowledge:   manim_service/concept_videos/docs/rl_knowledge_base.md
- codex_handoff:  manim_service/concept_videos/docs/CODEX_HANDOFF.md

Skills to read (each has its own SKILL.md):
- Script Writer:        ~/.codex/skills/script-writer/SKILL.md
- Visual Director:      ~/.codex/skills/visual-director/SKILL.md
- RL Expert:            ~/.codex/skills/rl-expert/SKILL.md
- Tech Validator:       ~/.codex/skills/technical-validator/SKILL.md
- Manim style-lock:     ~/.codex/skills/manim-rl-animation-style-lock/SKILL.md

---

## Pre-validated context (carry forward, do not re-derive)

- platform_contract: UNREGISTERED_NEW_LESSON (register at Gate 8, not this stage)
- rl_knowledge_base entries confirmed relevant: `transition_prob`, `dp_policy_eval`
- course_plan: V-02, Wave 1, between rl_intro (V-01, produced) and dp_policy_eval (V-03, produced)
- specs.md RL Expert flags:
  1. NUMERIC BUG — `transition_prob_concept.py` hard-codes state-6 RIGHT as {7,2,5};
     live Gymnasium confirms {7,2,10} — Tech Validator must re-pin and the scene must
     use {7,2,10}. Do NOT reuse the old scene wholesale; patch the constants.
  2. 30-MIN ZERO MARGIN — six segments totalling ~29 min. Plan must honour the split-
     trigger rule: if any single segment overruns its budget by >60s, truncate rather
     than let the video exceed 30 min.
  3. specs.py UNREGISTERED — proposal is already in specs.md §10; no action needed here.
  4. PREREQUISITE TRIPWIRE — closing beat must preview dp_policy_eval by name but must
     NOT show its loop, sweep, or any update assignment.

---

## Step 1 — Script Writer: produce mdp_foundations_plan.md

Read: ~/.codex/skills/script-writer/SKILL.md
Input: mdp_foundations_specs.md (the sole creative authority)
Output: manim_service/concept_videos/mdp_foundations_plan.md

Follow the 3-phase internal workflow from the skill (Pedagogical Architect →
Code Agent → Pacing Linter). The plan must:

- Cover all 10 required plan.md sections from the skill.
- Implement the six-segment spine (a)–(f) from specs.md §3 in order.
- Assign a time budget per segment; the sum must be ≤ 29:00 (hard 30-min ceiling
  minus 60 s buffer).
- Surface G_t = R_{t+1} + γG_{t+1} explicitly in segment (b) so segment (f) can
  reuse it.
- In segment (c) plan: note that the reference scene's {7,2,5} constants must be
  corrected to {7,2,10} before reuse — the Visual Director will choreograph the
  corrected version.
- In segment (f): mandate the full derivation chain from G_t recursion to the
  expanded double-sum Bellman equation (eq. 3.14). No shortcutting.
- Closing beat: name dp_policy_eval; do NOT show its loop.
- Pacing Linter: if any segment exceeds its budget, trim in this order:
  (d) boundary-condition detail, (e) q-bar detail, (c) optional marginals.
  Segments (a), (b) first beat, (f) derivation are load-bearing and cannot be cut.

Write the complete plan.md to:
  manim_service/concept_videos/mdp_foundations_plan.md

---

## Step 2 — Visual Director: produce mdp_foundations_choreo.md

Read: ~/.codex/skills/visual-director/SKILL.md
Inputs: mdp_foundations_specs.md + mdp_foundations_plan.md (just written)
Output: manim_service/concept_videos/mdp_foundations_choreo.md

Produce a complete choreo.md per the output template in the skill. Every
required section must be present:
- Scientific Rigor Declaration
- Pedagogical Strategy Declaration
- Cognitive Load Budget
- Element Lifecycle Matrix
- Motion Choreography table (one row per beat, ALL beats from plan.md)
- Camera Shot List
- Sprite-Math Binding Matrix
- trace_vector pairs
- Hand-off Notes

Critical choreography constraints for this video:
1. The FrozenLake grid is built ONCE in segment (a) and NEVER rebuilt. Each
   subsequent segment adds a layer (labels, arrows, bars, heatmap overlay, etc.)
   on top of the existing grid. Do not destroy/recreate the grid.
2. Segment (c) ActionBarChart: three bars for state-6 RIGHT outcomes, labelled
   with {7, 2, 10} — NOT {7, 2, 5}. Each bar = 1/3. Σp=1 caption beneath.
3. Segment (d): PolicyArrowGrid (deterministic) left, ProbabilityBarPanel right.
   These must be visually distinct from (c)'s environment fan (defeates M1).
4. Segment (e): ValueHeatmap with terminal cells {5,7,11,12,15} shown as 0-value.
   Use a non-optimal policy (uniform-random, each action 0.25) — defeats M4.
5. Segment (f): BackupDiagram with labelled branches. Root=open circle (state s),
   branches weighted by π(a|s), leaves labelled (s',r) weighted by p(s',r|s,a),
   leaf annotation = r + γv_π(s'). Map each branch term-by-term to eq. 3.14.
6. A RECAP CARD is required before segment (f) to reset cognitive load.
7. Apply STYLE_BIBLE §§13-28 strictly. No animation exceeds 2.5 s base duration.
8. Cite the Six Principles from the skill where layout decisions are non-obvious.

Write the complete choreo.md to:
  manim_service/concept_videos/mdp_foundations_choreo.md

---

## Step 3 — Gate 1: RL Expert plan + choreo review

Read: ~/.codex/skills/rl-expert/SKILL.md
Inputs: mdp_foundations_specs.md + mdp_foundations_plan.md + mdp_foundations_choreo.md

Follow the 5-step review protocol from the skill. Evaluate against specs.md as
the scope authority. Record your verdict as:

  GATE_1_VERDICT: PASS | FAIL
  GATE_1_NOTES: <one-line note per issue, or "none">

If FAIL: do NOT stop. Fix the plan.md and/or choreo.md in-place (overwrite the
files) and record what you changed. Then re-issue the verdict. You have 2 attempts.
If still FAIL after 2 attempts, record GATE_1_VERDICT: FAIL and continue to Step 4
but set the final result status to "failed" and include the blocking issues in
errors:.

Key acceptance criteria (from specs.md §11):
- Every term in the Bellman equation is defined earlier in the video.
- The G_t = R_{t+1} + γG_{t+1} recursion is surfaced in segment (b).
- The Bellman equation is derived (not asserted) in segment (f).
- The stochastic three-outcome case is shown (state-6 RIGHT, {7,2,10}).
- v_π is shown for the uniform-random (non-optimal) policy.
- Closing beat names dp_policy_eval without showing its algorithm.
- No term from a later lesson (no optimality, no iteration, no max-over-actions).
- MISCONCEPTIONS M1–M5 all have explicit defeat strategies in the plan or choreo.

---

## Step 4 — Gate 2: Technical Validator

Read: ~/.codex/skills/technical-validator/SKILL.md
Python: /Users/ultramarine/.venvs/manim/bin/python

Run EVERY check from specs.md §8. For each check, print the live output and your
verdict. Record:

  GATE_2_VERDICT: PASS | FAIL
  GATE_2_NOTES: <one line per check: CHECK_NAME: PASS/FAIL actual_value>

Required checks (all BLOCKING unless noted):

1. State-6 RIGHT successor set and probabilities:
   ```python
   import gymnasium as gym
   env = gym.make("FrozenLake-v1", is_slippery=True)
   for t in env.unwrapped.P[6][2]: print(t)
   ```
   Expected: exactly three tuples; successor states = {7, 2, 10}; each prob ≈ 1/3;
   reward = 0.0; done = True only for state 7 (a hole). If the live result differs
   from {7,2,10}, record the actual values — those are the canonical values to use
   in the Manim scene.

2. All rewards on state-6 RIGHT transitions = 0.0. Confirm no transition to state
   15 (goal) from state 6 via action RIGHT.

3. Σp = 1: sum of probabilities over env.unwrapped.P[6][2] = 1.0 (float tolerance).

4. Uniform policy row-sum:
   ```python
   import numpy as np
   n_s = env.observation_space.n; n_a = env.action_space.n
   pi = np.ones((n_s, n_a)) / n_a
   assert np.allclose(pi.sum(axis=1), 1.0)
   assert np.isclose(pi[6][2], 0.25)
   ```

5. γ discounting example: rewards=[0,0,1], γ=0.99 → G = 0 + 0.99·0 + 0.99²·1 = 0.9801.
   Verify the numeric value.

6. Terminal states: confirm holes {5,7,11,12} and goal {15} are done=True in at least
   one transition tuple. Show that v_π(terminal) = 0 is correct (no reward accrues
   after terminal).

7. Map geometry: confirm state 6 = row 1, col 2 in the 4×4 map; neighbours are
   2(up), 10(down), 5(left), 7(right).

8. Plan code lines: the code snippets in plan.md must use env.unwrapped.P (NOT
   env.P), must never call env.step() or env.reset(), and must contain no iteration
   loop / sweep / update assignment.

If any BLOCKING check fails, record GATE_2_VERDICT: FAIL and set final status to
"failed" in the result block, detailing the failure in errors:.

---

## Step 5 — Manim scene_render

Read: ~/.codex/skills/manim-rl-animation-style-lock/SKILL.md
Inputs: mdp_foundations_plan.md + mdp_foundations_choreo.md (both just validated)
Python: /Users/ultramarine/.venvs/manim/bin/python

Generate the Manim scene implementing every row of choreo.md. Write to:
  manim_service/concept_videos/mdp_foundations_concept.py

Scene class name: MdpFoundationsScene

Implementation rules (non-negotiable):
1. Use the exact successor set confirmed by Gate 2 (expected: {7,2,10} each 1/3).
   If Gate 2 returned different values, use the Gate 2 live values — never the
   hard-coded {7,2,5} from the old reference scene.
2. Implement the accreting grid: build once in segment (a), add layers per segment.
   No VGroup.become() calls that wipe the grid.
3. Implement the BackupDiagram in segment (f) with term-by-term labels mapping to
   eq. 3.14.
4. Implement the RECAP CARD before segment (f).
5. Apply STYLE_BIBLE colour tokens: SLATE_900 background, INDIGO_500 primary,
   EMERALD_500 positive, ROSE_500 negative, AMBER_400 accent, SLATE_100 text.
6. Every MathTex string must use raw strings (r"...") and \mathrm{} for multi-letter
   subscripts/superscripts.
7. Animations: Write.animate, FadeIn, Create, ReplacementTransform — no Flash.
8. Do NOT improvise layout. Implement choreo.md exactly. If a beat is missing from
   choreo.md, STOP and write MISSING_CHOREO in the errors: field.

Render dev quality:
  /Users/ultramarine/.venvs/manim/bin/python -m manim -ql \
    manim_service/concept_videos/mdp_foundations_concept.py \
    MdpFoundationsScene

Confirm the silent MP4 exists at:
  backend/media/concept_videos/mdp_foundations_concept.mp4
(or the path manim writes to — record the actual path)

---

## Constraints
- python: /Users/ultramarine/.venvs/manim/bin/python
- render quality: -ql (480p15 dev)
- Implement every choreo.md row; do not improvise. If layout detail is missing,
  report MISSING_CHOREO rather than guessing.
- Do not register in specs.py or worker.py — that is Gate 8 (Claude's job).
- Do not generate the narration script or audio — that is the narrate_mux brief.

---

## Result format

End your run by writing ONLY this block as your final message (fill in actuals):

    STAGE_RESULT
    stage: full_pipeline
    status: {success|failed}
    gate_1_verdict: {PASS|FAIL}
    gate_1_notes: {one line, or "none"}
    gate_2_verdict: {PASS|FAIL}
    gate_2_notes: {CHECK_NAME:PASS/FAIL actual_value, ...}
    state6_right_successors: {actual list from live Gym, e.g. [(0.333,7,0.0,True),(0.333,2,0.0,False),(0.333,10,0.0,False)]}
    plan_md: manim_service/concept_videos/mdp_foundations_plan.md
    choreo_md: manim_service/concept_videos/mdp_foundations_choreo.md
    scene_py: {path or "-"}
    silent_mp4: {path or "-"}
    render_seconds: {int or "-"}
    animations: {int or "-"}
    errors: {short description or "none"}
