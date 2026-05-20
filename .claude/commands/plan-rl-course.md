Create or revise the comprehensive RL concept-video course plan before producing
individual videos. This command is for curriculum design, not Manim production.

Invoked as:
  /project:plan-rl-course

Optional arguments:
  repo_intro_path=<absolute path to uploaded repo introduction>
  include_registry=true|false

---

## Purpose

The current six-video lineup is not sufficient as a beginner RL course because
it starts inside dynamic programming / MC / TD methods before teaching all
prerequisites. This command asks a dedicated curriculum agent to research how
beginner RL courses are sequenced, read the local project context, and create a
full prerequisite-aware video syllabus.

The output becomes the backlog that `/project:produce-video lesson_id=<id>` uses
later. It does not render scenes, edit `specs.py`, edit `worker.py`, or register
videos in the backend.

---

## Step 0 — Parse arguments

Read optional arguments:

- `repo_intro_path`: user-uploaded introduction to the repo. If present, the
  Course Architect must read it and incorporate it. If absent, continue but mark
  "repo introduction not provided" as an open decision.
- `include_registry`: if `true`, ask for both Markdown and JSON outputs. Default
  is `false`.

Output targets:

```
/Users/ultramarine/Desktop/grad_support_files/grad_project/manim_service/concept_videos/rl_course_plan.md
/Users/ultramarine/Desktop/grad_support_files/grad_project/manim_service/concept_videos/rl_course_registry.json
```

Create the output directory if needed.

---

## Step 1 — Load local context

Read these local files before spawning the course architect:

- `manim_service/concept_videos/docs/STYLE_BIBLE.md`
- `manim_service/concept_videos/docs/rl_knowledge_base.md`
- `backend/concept_videos/specs.py`
- `manim_service/jobs/worker.py`
- `manim_service/SESSION_LOG.md`
- `repo_intro_path`, if provided

Summarize the relevant constraints:

- Existing videos / known lesson IDs
- Existing render and registry mechanics
- Existing RL knowledge-base scope
- The distinction that `lesson_id` is identity/routing only
- The distinction that `specs.py` is app compatibility metadata only

---

## Step 2 — Spawn RL Course Architect

Spawn an Agent:

```
description: "RL Course Architect — beginner RL video syllabus"
subagent_type: claude
prompt: |
  You are the RL Course Architect for the grad_project RL concept-video pipeline.
  Read your full skill file at:
  .agents/skills/rl-course-architect/SKILL.md

  Task: research and design a comprehensive beginner RL concept-video course.

  Local project context:
  [paste summaries and key excerpts from Step 1]

  User repo introduction:
  [paste repo_intro_path contents if provided, else "Not provided"]

  Output Markdown path:
  /Users/ultramarine/Desktop/grad_support_files/grad_project/manim_service/concept_videos/rl_course_plan.md

  Output JSON registry:
  [if include_registry=true, write to /Users/ultramarine/Desktop/grad_support_files/grad_project/manim_service/concept_videos/rl_course_registry.json; otherwise "not requested"]

  Requirements:
  - First research reputable beginner RL course structures and cite every source.
  - Use Sutton & Barto, David Silver, Spinning Up, and other reputable sources as appropriate.
  - Do not treat the current six-video lineup as sufficient.
  - Do not force the course to fit the current six IDs.
  - There is no hard limit on video count.
  - Each video should teach one core concept fully from A to Z.
  - Build a prerequisite DAG and a beginner watch path.
  - Identify all videos that must exist before the current DP/MC/TD videos.
  - Mark which existing lessons can be kept, moved later, split, or renamed.
  - Keep planning artifacts under /Users/ultramarine/Desktop/grad_support_files, not in the repo.
  - Do not edit runtime files or production scene files.

  Return the final response format from your skill.
```

---

## Step 3 — Report

After the agent completes, print:

```
RL course plan generated.
Plan: [absolute path]
Registry: [absolute path or "not requested"]
Next production step: choose the first Wave 1 lesson_id, then run /project:produce-video lesson_id=<id>
```

If the Course Architect reports that the repo introduction was missing, include:

```
Open input: upload the repo introduction and rerun /project:plan-rl-course repo_intro_path=<path>
```
