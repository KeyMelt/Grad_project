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
    """Return the duration in seconds of an audio or video file via PyAV.

    Falls back to ffprobe if PyAV cannot open the file.
    """
    try:
        import av  # type: ignore
        with av.open(str(path)) as container:
            if container.duration is not None:
                return float(container.duration) / 1_000_000.0
            # duration may be None for some containers; try first stream
            for stream in container.streams:
                if stream.duration is not None and stream.time_base is not None:
                    return float(stream.duration * stream.time_base)
        raise MuxError(f"PyAV could not determine duration of {path}")
    except ImportError:
        pass  # fall through to ffprobe

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
        logger.warning(
            "ffmpeg mux failed (exit %d), falling back to PyAV mux: %s",
            result.returncode, result.stderr[:200],
        )
        try:
            _mux_with_pyav(silent_video_path, narration_wav_path, output_path)
        except Exception as exc:
            raise MuxError(f"PyAV mux fallback failed: {exc}") from exc
    elif not output_path.exists() or output_path.stat().st_size == 0:
        raise MuxError(f"ffmpeg succeeded but output is missing/empty: {output_path}")

    logger.info(
        "Muxed %s + %s -> %s (%.1f MB)",
        silent_video_path.name,
        narration_wav_path.name,
        output_path,
        output_path.stat().st_size / (1024 * 1024),
    )
    return output_path


def _mux_with_pyav(
    silent_video_path: Path,
    narration_wav_path: Path,
    output_path: Path,
) -> None:
    """Fallback mux using PyAV when system ffmpeg is unavailable.

    Copies the video stream and transcodes the WAV to AAC audio.
    If AAC encoder is unavailable, stores audio as FLAC inside an MKV.
    """
    import av  # type: ignore
    import numpy as np  # type: ignore
    import soundfile as sf  # type: ignore

    output_path.parent.mkdir(parents=True, exist_ok=True)

    audio_data, sample_rate = sf.read(str(narration_wav_path), dtype="float32")
    if audio_data.ndim == 1:
        audio_data = audio_data[:, None]  # (N,) → (N, 1)

    vid_src = av.open(str(silent_video_path))
    vid_stream = vid_src.streams.video[0]

    dst = av.open(str(output_path), mode="w")
    out_video = dst.add_stream(template=vid_stream)

    # Try AAC; fall back to pcm_s16le which every container accepts
    try:
        out_audio = dst.add_stream("aac", rate=sample_rate, layout="mono")
    except Exception:
        out_audio = dst.add_stream("pcm_s16le", rate=sample_rate, layout="mono")

    # Copy video packets
    for pkt in vid_src.demux(vid_stream):
        if pkt.dts is None:
            continue
        pkt.stream = out_video
        dst.mux(pkt)
    vid_src.close()

    # Encode audio in chunks
    chunk_size = 1024
    pts = 0
    audio_mono = audio_data[:, 0]
    for i in range(0, len(audio_mono), chunk_size):
        chunk = audio_mono[i : i + chunk_size]
        frame = av.AudioFrame.from_ndarray(
            (chunk * 32767).astype("int16")[None, :], format="s16", layout="mono"
        )
        frame.sample_rate = sample_rate
        frame.pts = pts
        pts += len(chunk)
        for enc_pkt in out_audio.encode(frame):
            dst.mux(enc_pkt)
    for enc_pkt in out_audio.encode(None):
        dst.mux(enc_pkt)

    dst.close()
    logger.info("PyAV mux wrote %s (%.1f MB)", output_path, output_path.stat().st_size / 1024**2)
