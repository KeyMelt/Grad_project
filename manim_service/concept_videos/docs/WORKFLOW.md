# Concept-Video Workflow (canonical)

**Model: single operator + on-demand skills.** One model authors the whole video
directly, leaning on deterministic tooling for QA, and calls the former pipeline agents
as *skills* only when a specific aspect needs bolstering. The autonomous 9-agent relay is
archived (`_archive_pipeline/`).

## Step 0 — Per-lesson design pass (MANDATORY, before any code)

**No one-mold-fits-all.** Never reuse the previous video's template by reflex. Before
authoring, decide — in writing — what THIS lesson specifically needs:

- **Prior art FIRST (any lesson introducing a NEW algorithm) — search the web.** Before
  designing, research how this algorithm is *generally taught*: the canonical worked
  example, the visualizations/diagrams educators actually use (backup diagrams, the
  Blackjack value-surface plot, the CliffWalking path contrast, learning curves…), the
  standard intuitions, and the common pitfalls/misconceptions. Sources: Sutton & Barto
  2018, David Silver's UCL lectures, OpenAI Spinning Up, Gymnasium docs, and reputable
  explainers/videos. Use `WebSearch` / `WebFetch`. Then FOLD the genuinely better ideas
  into these rules / the STYLE_BIBLE before building — improve the playbook each lesson,
  don't reinvent a worse wheel. (This is a standing instruction, not optional.)
- **Environment** — which Gymnasium env does this lesson actually teach with? It is NOT
  always FrozenLake. Known: DP lessons → FrozenLake; **mc_first_visit → Blackjack**;
  **td_sarsa / td_q_learning → CliffWalking**; **td_prediction → TBD** (settle via course
  plan / `rl-course-architect` first). Confirm from the lecture notes, not memory.
- **Visual primitives** — pick the helpers that match that env: FrozenLake →
  `EnvironmentValueHeatmap` / `PolicyArrowGrid` / `FloatingValues` (+ elf);
  Blackjack → `blackjack_panel` / `card_mobject` (cards, hands — no grid, no elf);
  CliffWalking → `cliffwalking_panel` / `EpisodeTrail`. **Probe-render an unfamiliar
  helper first** to confirm it draws real env art, not a stub.
- **Teaching mechanic / structure** — what is the lesson actually *doing*? A converging
  value heatmap (DP sweeps) is a different shape from a sampled episode accumulating a
  return (MC), a TD bootstrap update, or a SARSA-vs-Q trajectory contrast. The segment
  arc, the focal "worked number," and the pacing must fit that mechanic — not the last
  video's.
- **Numbers** — if exact values/odds are quoted, plan a `technical-validator` pass
  against the live env before authoring (sampled returns, transition odds, etc.).

Only after Step 0 do the env-agnostic mandates (real env visuals + on-screen morphing
math + worked focal number) get applied through the env you just chose.

## The build loop (per video)

1. **Spec** — read `*_lecture_notes.md` for the lesson (the teaching authority). No
   separate `plan.md`/`choreo.md` required.
2. **Author segments** — one Scene per file under
   `manim_service/workspaces/<lesson>/segments/`, on a shared `*_base.py`
   (lesson constants + helpers), listed in `manifest.json`. STYLE_BIBLE is the spec.
3. **Render + self-QA each segment** at `-ql`: check for errors, extract 1–2 frames,
   confirm duration.
4. **Deterministic gate (mandatory)** — `quality_gate.py --audit …/layout_audit.json`
   on every 2D segment. Must read `VERDICT: PASS` (0 off-canvas / 0 crowd) before accept.
5. **Narration** — write `narration_script.md` (am_michael, §30.5/§30.6), timed to the
   segment phase windows.
6. **Final render** — `segment_render.py --lesson-id <id> --quality=-qm` → silent concat.
   (Prepend `/Library/TeX/texbin` to PATH so MathTex finds `latex`.)
7. **Mux** — `python -m manim_service.audio.synthesize …` → narrated MP4. Target
   0 placement warnings.
8. **Spot-check** the concat (1 frame) + update memory `project_video_pipeline_status.md`.

## Non-negotiables (see memory mandates)

- Real gymnasium env visuals (`EnvironmentValueHeatmap`), never abstract squares.
- Every grid moment backed by ON-SCREEN math: governing equation + a worked focal number.
- Equations **morph** their pieces into insight (`TexEquation.collapse/expand`), never
  idle `Write`-and-sit.
- Sweeps show the **arithmetic** (ring a cell, value-flow arrow, plug in the real number).
- The **elf sprite** is on the grid in every grid segment.
- Flat-2D grid + floating value numbers; no 3D-iso tilt, no value bars.

## Skills on tap (former pipeline agents — pull when useful)

| Skill | Pull it in when… |
|---|---|
| `rl-expert` | you want a Sutton&Barto correctness sign-off on the teaching/claims |
| `technical-validator` | numbers must be verified against the **live** Gymnasium env (`env.P`) — do this before quoting exact heatmaps/transition odds |
| `transcript-writer` | a shipped video needs `captions.srt` / `.vtt` |
| `voice-bgm` | narration polish or a BGM envelope (§12 palette) |
| `visual-director` | a segment's composition is genuinely hard and a `choreo.md` would help |
| `script-writer` | you want a beat-sheet first instead of going straight to code |
| `qa-agent` | a stricter manual QA pass beyond the deterministic gate |
| `series-continuity` | checking a new video against prior ones for consistency |
| `rl-course-architect` | changing the curriculum / course map |
| `manim-rl-animation-style-lock` | reference for the scene helper API (panels/motion/rl_visuals) |

Use them à la carte. None is a mandatory gate anymore except the deterministic
`quality_gate.py`.
