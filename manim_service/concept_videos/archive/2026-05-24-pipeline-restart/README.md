# Archive — 2026-05-24 Pipeline Restart

**Archived by:** Producer  
**Date:** 2026-05-24  
**Reason:** Full pipeline quality overhaul (STYLE_BIBLE §§29-33 added) and curriculum
restructure. Both `rl_intro` and `mdp_foundations` were produced under a pipeline
that violated 8 quality requirements identified by user review. Archived to prevent
bias contamination of new production runs.

## Curriculum change

Old structure (archived):
- `rl_intro` (standalone, V-01): RL intro only
- `mdp_foundations` (standalone, V-02): MDP framework + rewards/returns +
  transition probability + policies + value functions + Bellman equations

New structure (starting fresh):
- `rl_mdp_core` (V-01): RL intro + MDP framework + rewards/returns + transition
  probability (original lessons 1–4)
- `policies_values_bellman` (V-02): policies + value functions + Bellman equations
  (original lessons 5–7)

## Quality defects that caused the restart (all present in both archived videos)

1. Narrator describes the screen instead of explaining meaning
2. Equations narrated but not visible on screen at cue time
3. Narration sounds scripted and monotonous (robotic register)
4. Text too small and illegible
5. Overlaying visual artifacts (stale elements from prior phases)
6. Gymnasium built-in PNG assets not used
7. Explanation not intuitive / doesn't follow 3Blue1Brown demystified approach
8. Codex CLI not used for scene_render stage

## Contents

All pipeline artifacts for `rl_intro` and `mdp_foundations`:
- Specs, plan, choreo, narration script, audio brief, captions files
- Manim scene Python files
- Rendered MP4s (silent and narrated)
- Pipeline state JSON files

Do NOT use these files as reference for new production.
