# Visualization Module

This module converts RL execution traces into learner-facing replay artifacts.
Concept-video and replay MP4 rendering is owned by `manim_service`; the API
gateway serves media through Spaces/CDN URLs.

## Source Files

- `controller.py`: submits trace render jobs to the Manim service and resolves
  completed media URLs.

## Generated Output

The following directories are generated at runtime:

- `../media/traces/`

They are ignored by `.gitignore` and can be regenerated.
