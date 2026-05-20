"""Audio synthesis and composition for concept-video narration.

This subpackage owns everything from "Voice & BGM Agent has written a
`narration_script.md`" to "the final MP4 has embedded narration audio".

Public API (entry points used by the pipeline):

- `synthesize.main()` — CLI / module entry; the Voice & BGM agent invokes it
  via `python -m manim_service.audio.synthesize ...`
- `tts.KokoroTTS` — provider-agnostic-named wrapper around kokoro-onnx
- `compose.assemble_timeline(...)` — places synthesised segments at phase
  start timestamps and pads with silence to match the silent MP4's duration
- `mux.mux_audio_into_video(...)` — ffmpeg wrapper

The synthesise-to-timing model is used: each narration line is rendered to
audio independently, then placed at its phase timestamp; silence pads any
gap, and any line that would overrun the next phase is logged as a warning
(not truncated — we always emit the full line).
"""
