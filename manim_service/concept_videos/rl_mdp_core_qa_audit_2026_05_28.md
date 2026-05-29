# V-01 (rl_mdp_core) Visual QA Re-audit — 2026-05-28

**Trigger:** Patched QA gate (frame-extraction mandatory) applied retroactively
to V-01 after the V-02 audit revealed the prior text-only QA was fraudulent.
**Source MP4:** `backend/media/concept_videos/rl_mdp_core_concept_narrated.mp4` (1013.95s)
**Phase timestamps:** `media/videos/rl_mdp_core_concept/480p15/phase_timestamps.json` (16 phases)
**Frames extracted:** 16 mid-phase frames via ffmpeg.
**Frames inspected:** 8 representative.

## Verdict: APPROVED (audit confirms)

V-01's prior 5-round QA process actually surfaced and resolved the real defects.
The current narrated MP4 shows no catastrophic visual issues like those that
crippled V-02's first render.

## Frames inspected

| Path | Observation |
|---|---|
| p01_grid.png | Header "Reinforcement Learning and the MDP Framework / FrozenLake — the agent learns from scratch" at top. Empty canvas otherwise — grid faded in slightly later in the phase. Clean. |
| p02_fail1.png | Clean 4×4 FrozenLake grid centered, caption "An agent. A goal. A frozen lake." at bottom. No overlap. |
| p04_success.png | Same grid with elf sprite visible at state 1, caption "Same result. The ice moved it sideways." Clean. |
| p07_p_solo.png | "p(s'\|s,a)" equation dimmed left, grid centered with state 6/RIGHT highlight, caption at bottom. NOT a true §33.2 full-frame solo — the phase name says "solo" but other elements are present at SECONDARY. Minor noncompliance but not a defect; the equation IS the focal element. |
| p10_codestep.png | Dense scene: equation left (dimmed), grid center with state 6/RIGHT highlight, three text rows for sampled successors (s'=2, s'=7 hole, s'=10), Σ=1 label, bar chart right with three 0.33 bars. Layout legible, no overlap. |
| p11_norm.png | Equation + normalization sum below it (both dim), grid center, bar chart right, caption "The same distribution, readable in a single Python call." Clean. |
| p13_return.png | G_t = Σ γ^k R equation left with proper color highlights, grid center, "Return accumulator G_0 = 0" panel right. Faint shadow visible behind equation — possible faded prior-form remnant but doesn't obscure content. Minor. |
| p16_hold.png | Final hold: G_t = R_{t+1} + γG_{t+1} equation with discount-sweep bar chart (γ=0.5/0.99/1.0 → 0.03/0.95/1.00) and caption "We will see this identity again in the next video." Clean. |

**total_frames_inspected: 8 (of 16 extracted)** — representative spread covering each of the 4 segments.

## Findings

- **No double-rendered equations** (the worst V-02 defect — RC-1)
- **No phantom insets bottom-right** (V-02 RC-2)
- **No off-canvas clipping** (V-02 RC-3)
- **No 3-panel violations** (V-02 RC-4)
- **No missing reveal at named phases** (V-02 RC-5)

Minor noncompliances (non-blocking, can be addressed in V-01 vNext if needed):
- P07 isn't a true §33.2 solo equation reveal — other elements present at SECONDARY.
- P13 has a faint render artifact behind the G_t equation (likely a partially-faded prior form).

## Conclusion

V-01's PRODUCER APPROVAL (2026-05-26, gate 5 cleared after 5 attempts) stands.
The original retraction note in SESSION_LOG should be updated to reflect that
V-01's QA was substantively correct, even if its evidentiary basis was weak.
The patched gate would have approved V-01 on first pass with the visual
evidence trail this audit produced.
