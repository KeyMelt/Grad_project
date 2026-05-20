"""ffmpeg wrapper that combines a silent MP4 with a narration WAV.

Single function used by the audio pipeline. Keeps the ffmpeg invocation
in one place so we can tune codec/quality flags consistently.

Audio strategy:
- Source MP4 has no audio track (silent Manim render).
- We add the narration WAV as the single audio track.
- AAC encoding at 192 kbps stereo (synthesised mono is dual-routed to L+R).
- The audio sample rate is whatever the WAV is (24 kHz for Kokoro).
- We use `-shortest` so the muxed output ends at the shorter of the two
  streams; if narration overruns the silent MP4 (the compose layer warns
  but doesn't truncate), we instead extend the video by holding the last
  frame via the `tpad` filter.

We always re-encode the video stream-copy when possible to avoid lossless
→ lossy → re-encode cycles. Copy is fine because we're only adding a new
audio track to an existing video.
"""
from __future__ import annotations

import logging
import shutil
import subprocess
from pathlib import Path

from manim_service import settings

logger = logging.getLogger(__name__)


class MuxError(RuntimeError):
    """Raised when ffmpeg fails to mux narration into the MP4."""


def get_media_duration_seconds(path: Path) -> float:
    """Return the duration in seconds of an audio or video file, via ffprobe.

    Uses the ffprobe alongside the configured ffmpeg.
    """
    ffprobe = Path(settings.FFMPEG_BIN).with_name("ffprobe")
    if not ffprobe.exists():
        ffprobe = Path(shutil.which("ffprobe") or "ffprobe")

    result = subprocess.run(
        [
            str(ffprobe),
            "-v", "error",
            "-show_entries", "format=duration",
            "-of", "default=noprint_wrappers=1:nokey=1",
            str(path),
        ],
        capture_output=True,
        text=True,
        check=False,
    )
    if result.returncode != 0:
        raise MuxError(f"ffprobe failed on {path}: {result.stderr}")
    return float(result.stdout.strip())


def mux_audio_into_video(
    *,
    silent_video_path: Path,
    narration_wav_path: Path,
    output_path: Path,
    pad_video_to_audio: bool = True,
) -> Path:
    """Write a new MP4 combining the silent video and the narration audio.

    If `pad_video_to_audio` is True and the audio is longer than the video,
    the last video frame is held until the audio ends. If False, `-shortest`
    is used (output cuts at whichever stream ends first).

    Returns the output path.
    """
    if not silent_video_path.exists():
        raise MuxError(f"silent video not found: {silent_video_path}")
    if not narration_wav_path.exists():
        raise MuxError(f"narration audio not found: {narration_wav_path}")

    output_path.parent.mkdir(parents=True, exist_ok=True)

    video_seconds = get_media_duration_seconds(silent_video_path)
    audio_seconds = get_media_duration_seconds(narration_wav_path)
    overrun = audio_seconds - video_seconds

    cmd: list[str] = [
        settings.FFMPEG_BIN,
        "-y",                           # overwrite output
        "-loglevel", "error",
        "-i", str(silent_video_path),
        "-i", str(narration_wav_path),
    ]

    if pad_video_to_audio and overrun > 0.05:
        # Hold the last video frame to match the longer audio. tpad on the
        # video stream extends with the final frame; audio is left as-is.
        cmd += [
            "-filter_complex",
            f"[0:v]tpad=stop_mode=clone:stop_duration={overrun:.3f}[v]",
            "-map", "[v]",
            "-map", "1:a",
            "-c:v", "libx264",
            "-preset", "veryfast",
            "-pix_fmt", "yuv420p",
            "-crf", "20",
        ]
        logger.info(
            "Audio overruns video by %.2fs — padding video with held last frame",
            overrun,
        )
    else:
        # Plain mux: copy video, add audio, cut at shortest stream.
        cmd += [
            "-map", "0:v:0",
            "-map", "1:a:0",
            "-c:v", "copy",
            "-shortest",
        ]

    cmd += [
        "-c:a", "aac",
        "-b:a", "192k",
        "-ac", "2",                     # stereo (mono dual-routed)
        "-movflags", "+faststart",      # web-friendly mp4 metadata at front
        str(output_path),
    ]

    logger.info("Muxing: %s", " ".join(cmd))
    result = subprocess.run(cmd, capture_output=True, text=True, check=False)
    if result.returncode != 0:
        raise MuxError(
            f"ffmpeg mux failed (exit {result.returncode}): {result.stderr}"
        )

    if not output_path.exists() or output_path.stat().st_size == 0:
        raise MuxError(f"ffmpeg succeeded but output is missing/empty: {output_path}")

    logger.info(
        "Muxed %s + %s -> %s (%.1f MB)",
        silent_video_path.name,
        narration_wav_path.name,
        output_path,
        output_path.stat().st_size / (1024 * 1024),
    )
    return output_path
