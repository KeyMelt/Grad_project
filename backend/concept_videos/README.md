# Concept Video Pipeline

This folder contains the Manim source code for the pre-rendered lesson
explanation videos.

## Source Layout

- `scenes/`: one Manim scene module per concept video, plus shared helpers.
- `scenes/helpers.py`: shared visual components used by multiple scenes.
- `specs.py`: lesson video metadata and theory/source-check configuration.
- `render.py`: local render helper that generates all registered concept videos.
- `_manim_media/`: temporary Manim render cache/output. This is generated and ignored.

## Output Target

Rendered MP4 files are copied to:

```text
backend/media/concept_videos/
```

The FastAPI gateway serves those files through:

```text
/media/concept-videos/{filename}.mp4
```

The Flutter frontend receives that route through lesson metadata and plays it as
a backend network video, not as a bundled Flutter asset.

## Render Command

```bash
python -m backend.concept_videos.render
```

Useful environment variables:

```text
RL_IDE_MANIM_PYTHON=/Users/ultramarine/.venvs/manim/bin/python3
RL_IDE_CONCEPT_VIDEO_DIR=backend/media/concept_videos
```
