# Visualization Module

This module converts RL execution traces into learner-facing replay artifacts.
Pre-rendered concept videos now live under `backend/concept_videos/`.

## Source Files

- `controller.py`: writes a Manim scene from a logged episode and invokes Manim.

## Generated Output

The following directories are generated at runtime or by local rendering scripts:

- `animations/`

They are ignored by `.gitignore` and can be regenerated.
