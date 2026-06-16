# Video workspaces — segment-based authoring

Each concept video is authored here as a **workspace of independently-renderable
segments**, so a one-line fix re-renders one segment, not the whole video.
(STYLE_BIBLE §37.)

```
<lesson_id>/
    manifest.json            # ordered segments + quality flag
    segments/
        s01_intro.py         # exactly ONE manim Scene subclass per file
        s02_policy.py
        ...
    cache/                   # rendered segment MP4s, content-hash keyed (gitignored)
    <lesson_id>_silent.mp4   # concatenated render product
```

`manifest.json`:

```json
{
  "lesson_id": "policies_values_bellman",
  "quality": "-ql",
  "segments": [
    {"id": "s01_intro",      "file": "segments/s01_intro.py",      "scene": "S01Intro"},
    {"id": "s05_derivation", "file": "segments/s05_derivation.py", "scene": "S05Derivation"}
  ]
}
```

## Authoring rules

1. **One Scene per file.** The `scene` in the manifest is its class name.
2. **Self-contained.** Each segment starts from and ends on the clean dark
   background (fade in from / fade out to black). No mobject/camera/Python state
   crosses segment files — rebuild whatever the segment needs. This is what makes
   segments independently renderable and seamlessly concatenable.
3. **Segment = beat boundary.** Split on narration/teaching-beat seams (the old
   `S<n>` segments are a good guide).
4. **Keep the per-phase `hold_until` timing contract** inside each segment so the
   final concat still aligns with narration.

## Rendering

```bash
PY=/Users/ultramarine/.venvs/manim/bin/python

# render changed segments (cache reuses unchanged) + concat to <id>_silent.mp4
$PY -m manim_service.pipeline.segment_render --lesson-id <id>

# force re-render of one segment
$PY -m manim_service.pipeline.segment_render --lesson-id <id> --segment s05_derivation
```

Editing one segment busts only that segment's cache; editing a shared module
(`manim_service/scenes/*.py`) correctly busts every segment.

## Narration

Voiceover/BGM runs **once**, on the final QA-approved `<id>_silent.mp4` concat —
never per segment, never redone for a visual-only fix unless the concat changed.
(STYLE_BIBLE §37.4.)
