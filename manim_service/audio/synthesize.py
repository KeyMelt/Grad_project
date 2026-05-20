"""Synthesize narration and mux it into a silent MP4.

Invoked by the Voice & BGM agent (after it has written the narration script)
or directly by the worker after the Manim Expert render completes:

    python -m manim_service.audio.synthesize \\
      --narration manim_service/concept_videos/dp_value_iteration_narration_script.md \\
      --silent-mp4 backend/media/concept_videos/dp_value_iteration_concept.mp4 \\
      --output    backend/media/concept_videos/dp_value_iteration_concept_narrated.mp4 \\
      [--voice am_michael]   [--speed 1.0]   \\
      [--phase-timestamps manim_service/_manim_media/.../phase_timestamps.json]

Writes:
- `{output}.audio_report.json` next to the output MP4 — per-line placement,
  duration, and warnings (consumed by the QA agent).
- A scratch WAV in `settings.AUDIO_CACHE_DIR / <lesson>/narration.wav` for
  inspection. Safe to delete at any time.

Exit codes: 0 on success, 2 on user error, 3 on synthesis error.
"""
from __future__ import annotations

import argparse
import json
import logging
import sys
from pathlib import Path

from manim_service import settings
from manim_service.audio.compose import (
    load_phase_windows,
    parse_narration_script,
    synthesize_and_assemble,
    write_wav,
)
from manim_service.audio.mux import (
    MuxError,
    get_media_duration_seconds,
    mux_audio_into_video,
)
from manim_service.audio.tts import KokoroTTS
from manim_service.audio.voices import describe

logger = logging.getLogger("manim_service.audio.synthesize")


def _build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(
        prog="python -m manim_service.audio.synthesize",
        description="Synthesise narration with Kokoro and mux it into a silent MP4.",
    )
    p.add_argument("--narration", type=Path, required=True,
                   help="Path to narration_script.md")
    p.add_argument("--silent-mp4", type=Path, required=True,
                   help="Path to the silent Manim-rendered MP4")
    p.add_argument("--output", type=Path, required=True,
                   help="Path to write the narrated MP4")
    p.add_argument("--phase-timestamps", type=Path, default=None,
                   help="Optional path to phase_timestamps.json (for warnings)")
    p.add_argument("--voice", type=str, default=None,
                   help=f"Kokoro voice id (default: {settings.DEFAULT_NARRATOR_VOICE})")
    p.add_argument("--speed", type=float, default=None,
                   help=f"Synthesis speed multiplier (default: {settings.DEFAULT_NARRATOR_SPEED})")
    p.add_argument("--lesson-id", type=str, default=None,
                   help="Lesson id (used to namespace the audio cache dir)")
    p.add_argument("--keep-cache", action="store_true",
                   help="Keep scratch WAV in AUDIO_CACHE_DIR (default: keep)")
    p.add_argument("--verbose", "-v", action="store_true")
    return p


def main(argv: list[str] | None = None) -> int:
    args = _build_parser().parse_args(argv)

    logging.basicConfig(
        level=logging.DEBUG if args.verbose else logging.INFO,
        format="%(levelname)s %(name)s: %(message)s",
    )

    if not args.narration.exists():
        logger.error("narration script not found: %s", args.narration)
        return 2
    if not args.silent_mp4.exists():
        logger.error("silent MP4 not found: %s", args.silent_mp4)
        return 2

    voice = args.voice or settings.DEFAULT_NARRATOR_VOICE
    logger.info("Voice: %s", describe(voice))

    # Parse the narration script
    lines = parse_narration_script(args.narration)
    if not lines:
        logger.error(
            "no timed lines found in %s — narration script must contain "
            "lines like '[00:00:08] ...'", args.narration,
        )
        return 2
    logger.info("Loaded %d narration lines from %s", len(lines), args.narration.name)

    # Determine target duration from the silent MP4
    try:
        video_duration = get_media_duration_seconds(args.silent_mp4)
    except MuxError as exc:
        logger.error("ffprobe failed on silent MP4: %s", exc)
        return 2
    logger.info("Silent video duration: %.2fs", video_duration)

    # Optional phase windows
    phase_windows = []
    if args.phase_timestamps and args.phase_timestamps.exists():
        phase_windows = load_phase_windows(
            args.phase_timestamps, total_video_seconds=video_duration,
        )
        logger.info("Loaded %d phase windows from %s",
                    len(phase_windows), args.phase_timestamps.name)

    # Synthesise + assemble
    try:
        tts = KokoroTTS()
    except FileNotFoundError as exc:
        logger.error("%s", exc)
        return 3

    try:
        buffer, reports = synthesize_and_assemble(
            narration_lines=lines,
            tts=tts,
            total_duration_seconds=video_duration,
            sample_rate=24000,
            phase_windows=phase_windows,
        )
    except Exception as exc:
        logger.exception("synthesis failed: %s", exc)
        return 3

    # Write the WAV to the cache dir
    lesson_id = args.lesson_id or args.narration.stem.replace("_narration_script", "")
    cache_dir = settings.AUDIO_CACHE_DIR / lesson_id
    wav_path = cache_dir / "narration.wav"
    write_wav(buffer, sample_rate=24000, path=wav_path)
    logger.info("Wrote narration WAV: %s (%.1f MB)",
                wav_path, wav_path.stat().st_size / (1024 * 1024))

    # Mux
    try:
        mux_audio_into_video(
            silent_video_path=args.silent_mp4,
            narration_wav_path=wav_path,
            output_path=args.output,
        )
    except MuxError as exc:
        logger.error("mux failed: %s", exc)
        return 3

    # Write the audio report next to the output
    report_path = args.output.with_name(args.output.stem + ".audio_report.json")
    report = {
        "lesson_id": lesson_id,
        "voice": voice,
        "speed": args.speed or settings.DEFAULT_NARRATOR_SPEED,
        "silent_video_seconds": round(video_duration, 3),
        "narration_seconds": round(len(buffer) / 24000.0, 3),
        "narration_wav": str(wav_path),
        "narrated_mp4": str(args.output),
        "lines": reports,
    }
    report_path.write_text(json.dumps(report, indent=2))
    logger.info("Wrote audio report: %s", report_path)

    # Summary
    n_warnings = sum(len(r["warnings"]) for r in reports)
    logger.info(
        "DONE — %d lines, %d warnings, narrated MP4: %s",
        len(reports), n_warnings, args.output,
    )
    return 0


if __name__ == "__main__":
    sys.exit(main())
