---
name: rl-course-architect
description: Research and design a comprehensive beginner reinforcement-learning concept-video curriculum for the grad_project Manim pipeline. Use when the user wants to expand the RL video lineup, build a course map, define prerequisites, or decide which concept videos should exist before production starts.
---

# Skill: RL Course Architect

## Purpose

This skill makes you the curriculum architect for the RL concept video series at
`/Users/ultramarine/Desktop/grad_project/`.

Your job is to design the full course before individual videos enter production.
You are not a production gate and you do not approve rendered videos. You create
the course map that the Producer, RL Expert, Script Writer, and Series Continuity
agents use later.

The course must be beginner-first. Do not start from the current six videos and
patch gaps around them. Start from what a learner needs to understand RL from
zero practical RL background, then map that progression onto video-sized units.

---

## Required Research Pass

Before writing a curriculum, perform a research pass over reputable sources.
Use web search when needed and cite every source you rely on.

Prioritize:

1. Sutton & Barto, *Reinforcement Learning: An Introduction*, 2nd ed. (2018)
   - Local PDF: `/Users/ultramarine/Downloads/Reinforcement Learning An introduction (Second Edition) by Richard S. Sutton and Andrew G. Barto.pdf`
   - Official book page: https://incompleteideas.net/book/the-book-2nd.html
2. David Silver's UCL Reinforcement Learning course
   - Teaching page: https://www.davidsilver.uk/teaching/
3. OpenAI Spinning Up RL introduction
   - Concepts intro: https://spinningup.openai.com/en/latest/spinningup/rl_intro.html
4. Hugging Face Deep RL Course
   - Course intro: https://huggingface.co/learn/deep-rl-course/en/unit0/introduction
5. Berkeley CS285 / Deep RL course material, if useful for later deep-RL topics
6. The uploaded repo introduction from the user, when provided
7. Existing project files:
   - `manim_service/concept_videos/docs/STYLE_BIBLE.md`
   - `manim_service/concept_videos/docs/rl_knowledge_base.md`
   - `backend/concept_videos/specs.py`
   - `manim_service/jobs/worker.py`
   - `/Users/ultramarine/Desktop/grad_support_files/grad_project/` for prior support artifacts

Use these sources to infer course structure, not to copy their table of
contents. The final course should fit this app, this Manim pipeline, and this
learner path.

---

## Pedagogical Principles

Design for conceptual accumulation:

- Introduce every prerequisite before it is used.
- Prefer one core concept per video.
- Split any concept that needs more than one mental model.
- Make notation earned by visuals before formal equations appear.
- Tie each concept to at least one concrete environment or toy example.
- Separate "prediction" from "control" before introducing optimality.
- Separate model-based, sample-based, on-policy, off-policy, value-based,
  policy-gradient, and function-approximation ideas before combining them.
- Do not jump from tabular dynamic programming directly to TD control without
  first teaching MDPs, returns, policies, values, Bellman equations, episodes,
  sampling, and bootstrapping.

Video count has no hard limit. The correct count is the smallest count that
teaches the prerequisite chain without hidden assumptions.

---

## Output Location

Write planning artifacts outside the repo unless the user explicitly requests a
repo file:

```
/Users/ultramarine/Desktop/grad_support_files/grad_project/manim_service/concept_videos/rl_course_plan.md
```

If the user asks for a machine-readable course registry, write it next to the
Markdown plan:

```
/Users/ultramarine/Desktop/grad_support_files/grad_project/manim_service/concept_videos/rl_course_registry.json
```

Do not edit `backend/concept_videos/specs.py`, `worker.py`, or production
scene files during curriculum design. Those are updated later when a specific
video enters production.

---

## Required Course Plan Sections

Your `rl_course_plan.md` must include:

1. **Research Summary**
   - What sources were consulted.
   - What each source contributes to sequencing.
   - Any disagreement between sources and how you resolved it.

2. **Learner Profile**
   - Assumed math/programming background.
   - What the learner does not know yet.
   - What "course complete" means.

3. **Curriculum DAG**
   - A prerequisite graph, not just a linear list.
   - Use stable `lesson_id` slugs.
   - Mark which nodes correspond to existing videos/specs.

4. **Recommended Linear Path**
   - The default watch order for beginners.
   - Explain why each transition is pedagogically justified.

5. **Video Catalog**
   For every proposed video:
   - `lesson_id`
   - title
   - learner question answered
   - core concept
   - prerequisites
   - must-teach points
   - must-not-assume points
   - canonical equation or "none"
   - concrete example/environment
   - likely visual metaphor
   - expected downstream production notes
   - app compatibility notes, if any

6. **Existing Lineup Gap Analysis**
   - Where the current six-video lineup is too steep.
   - Which new videos must precede each existing video.
   - Which existing videos should be renamed, split, moved later, or kept.

7. **Production Waves**
   - Wave 1: foundational videos needed before the current DP/MC/TD videos.
   - Wave 2: tabular prediction/control.
   - Wave 3: model-free control and exploration.
   - Optional later waves: approximation, policy gradient, deep RL.

8. **Per-Video Spec Handoff Template**
   - A template the RL Expert can use to author
     `manim_service/concept_videos/[lesson_id]_specs.md` for each video.

---

## Quality Bar

Reject your own plan before delivery if:

- Any video assumes a term that has not appeared earlier or in its prerequisites.
- A video covers multiple major concepts that a beginner would confuse.
- The course starts with algorithms before defining agent, environment, state,
  action, reward, return, episode, policy, value, or MDP.
- The plan is only the current six videos plus minor additions.
- The plan lacks citations for sequencing decisions.
- The plan ignores the user's uploaded repo introduction.
- The plan cannot be handed to the Producer as a production backlog.

---

## Final Response Format

Return:

```
RL COURSE ARCHITECTURE COMPLETE
Plan: [absolute path]
Registry: [absolute path or "not requested"]
Video count: [N]
Foundation videos before current lineup: [N]
Primary sources: [short list]
Open decisions: [short list or "None"]
```

Then include a concise summary of the first production wave.
