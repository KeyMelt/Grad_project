# Pipeline Skill Ownership Manifest

This file is the **single source of truth** for where each RL concept-video
pipeline skill physically lives, and which agent runtime owns it.

## Canonical location

All pipeline skill definitions are stored **once** under:

```
~/.codex/skills/<skill-name>/SKILL.md
```

Claude Code consumes the same definitions through symlinks under
`~/.claude/skills/<skill-name>` that point back into `~/.codex/skills/`.
There is therefore **no duplicate copy to drift** — editing the canonical
file updates both runtimes simultaneously.

> Do not replace a symlink in `~/.claude/skills/` with a real file. Doing so
> silently forks the skill and reintroduces the drift this manifest exists to
> prevent. Run `check_skill_canon.sh --repair` to restore a symlink.

## Skill inventory

| Skill | Canonical owner runtime | Role in pipeline |
|---|---|---|
| `producer` | Claude Code (orchestrator) | Governs gates, issues briefs, approves library |
| `rl-expert` | Claude Code | RL theory authority, Gate 1 + Gate 7 sign-off |
| `script-writer` | Claude Code | Authors `plan.md` |
| `visual-director` | Claude Code | Authors `choreo.md` |
| `technical-validator` | Claude Code | Gate 2 numerical validation (live Gymnasium) |
| `voice-bgm` | Claude Code (script) + Codex (synthesis) | Narration script; synthesis/mux runs in Codex |
| `qa-agent` | Claude Code | Gate 5 quality review |
| `series-continuity` | Claude Code | Gate 6 cross-series consistency |
| `transcript-writer` | Claude Code | Gate 4 captions |
| `rl-course-architect` | Claude Code | Course-plan authoring |
| `manim-rl-animation-style-lock` | **Codex** | Manim scene code generation + render |

"Canonical owner runtime" names the agent that *executes* the skill in the
sustainable split (see `concept_videos/docs/CODEX_HANDOFF.md`). The file
storage is identical for all skills regardless of owner: one copy in
`~/.codex/skills/`, symlinked into `~/.claude/skills/`.

## Division of labour (summary)

- **Claude Code** runs the reasoning/judgment gates (1–6 advisory + review).
- **Codex** runs the two heavy execution stages: Manim scene generation +
  render, and narration synthesis + mux.

The full protocol, brief format, and result format are in
`manim_service/concept_videos/docs/CODEX_HANDOFF.md`.

## Guard

`manim_service/pipeline/check_skill_canon.sh` verifies every Claude-side entry
is a symlink to the canonical Codex copy. Run it before a production run, or in
CI, to catch drift early. `--repair` recreates any missing/forked symlink.
