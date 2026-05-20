"""Timeline assembly — places synthesised clips at phase timestamps.

The Voice & BGM agent writes a `narration_script.md` with explicit
[HH:MM:SS] cues per line. The Manim Expert emits a `phase_timestamps.json`
sidecar next to the rendered MP4 listing the start time of each phase.

This module:

1. Parses `narration_script.md` into a list of `(timestamp_seconds, text, phase)` tuples.
2. Optionally reads `phase_timestamps.json` and validates that line
   timestamps fall within their phase windows; emits warnings on overlap.
3. Synthesises each line via `KokoroTTS` (caller passes the instance in).
4. Builds a single mono float32 audio buffer with each clip placed at its
   line timestamp, silence-padded to the target total duration.
5. Writes the buffer to `narration.wav`.

No BGM. Single narrator. Synthesise-to-timing — clips are placed at their
declared timestamps; the video length is fixed by the MP4 render.
"""
from __future__ import annotations

import json
import logging
import re
from dataclasses import dataclass
from pathlib import Path

import numpy as np
import soundfile as sf

from manim_service.audio.tts import KokoroTTS, SynthesizedClip

logger = logging.getLogger(__name__)


# ---------------------------------------------------------------------------
# narration_script.md parser
# ---------------------------------------------------------------------------

# Matches lines like:  "[00:00:08] Some narration text..."
# Captures HH, MM, SS, body.
_LINE_RE = re.compile(
    r"^\[(\d{2}):(\d{2}):(\d{2})\]\s+(.*\S)\s*$"
)

# Matches phase headers like:  "## Phase 1 — FrozenLake grid, state 6"
_PHASE_RE = re.compile(r"^##\s+Phase\s+(\d+)")


@dataclass(frozen=True)
class NarrationLine:
    """A single timed narration line parsed from narration_script.md."""

    start_seconds: float
    text: str
    phase: int          # 1-indexed phase number this line falls within, 0 if none


def parse_narration_script(path: Path) -> list[NarrationLine]:
    """Parse a narration_script.md into a list of NarrationLine.

    Lines without timestamps are skipped (assumed to be commentary/headers).
    """
    if not path.exists():
        raise FileNotFoundError(f"narration_script.md not found at {path}")

    lines: list[NarrationLine] = []
    current_phase = 0

    with path.open("r", encoding="utf-8") as f:
        for raw in f:
            phase_match = _PHASE_RE.match(raw)
            if phase_match:
                current_phase = int(phase_match.group(1))
                continue

            line_match = _LINE_RE.match(raw)
            if not line_match:
                continue

            hh, mm, ss, body = line_match.groups()
            start = int(hh) * 3600 + int(mm) * 60 + int(ss)
            # Strip emphasis markers (*emphasised words*) — Kokoro doesn't
            # respect them, and the captions writer has its own copy. We
            # keep the words; we just remove the markers.
            body = body.replace("*", "")
            lines.append(NarrationLine(
                start_seconds=float(start),
                text=body,
                phase=current_phase,
            ))

    lines.sort(key=lambda l: l.start_seconds)
    return lines


# ---------------------------------------------------------------------------
# phase_timestamps.json
# ---------------------------------------------------------------------------

@dataclass(frozen=True)
class PhaseWindow:
    phase: int
    start_seconds: float
    end_seconds: float | None   # None means "to end of video"


def load_phase_windows(
    path: Path,
    *,
    total_video_seconds: float,
) -> list[PhaseWindow]:
    """Load phase windows from phase_timestamps.json.

    Expected schema (emitted by BaseConceptScene):
        {
          "phases": [
            {"phase": 1, "name": "geometry_entry", "start_seconds": 0.0},
            {"phase": 2, "name": "per_action_backup", "start_seconds": 8.4},
            ...
          ],
          "total_duration_seconds": 67.2
        }
    """
    if not path.exists():
        logger.warning(
            "phase_timestamps.json not found at %s — proceeding without "
            "phase-window validation",
            path,
        )
        return []

    with path.open("r", encoding="utf-8") as f:
        data = json.load(f)

    phases = data.get("phases", [])
    if not phases:
        return []

    starts = [(int(p["phase"]), float(p["start_seconds"])) for p in phases]
    starts.sort(key=lambda x: x[1])

    windows: list[PhaseWindow] = []
    for i, (phase_num, start) in enumerate(starts):
        end = starts[i + 1][1] if i + 1 < len(starts) else total_video_seconds
        windows.append(PhaseWindow(phase=phase_num, start_seconds=start, end_seconds=end))
    return windows


# ---------------------------------------------------------------------------
# Timeline assembly
# ---------------------------------------------------------------------------

# Tiny gap between adjacent clips (prevents abrupt waveform discontinuity).
_INTER_CLIP_PAD_SECONDS = 0.08

# Master gain applied to all narration clips (0.9 = -1 dB headroom).
_MASTER_GAIN = 0.9


def synthesize_and_assemble(
    *,
    narration_lines: list[NarrationLine],
    tts: KokoroTTS,
    total_duration_seconds: float,
    sample_rate: int = 24000,
    phase_windows: list[PhaseWindow] | None = None,
) -> tuple[np.ndarray, list[dict]]:
    """Synthesise every line and assemble a mono float32 buffer.

    Returns (audio_buffer, line_reports). `line_reports` is a list of dicts
    (one per line) recording the actual placement, intended start, end,
    duration, and any warnings — useful for the QA agent.
    """
    total_samples = int(round(total_duration_seconds * sample_rate))
    buffer = np.zeros(total_samples, dtype=np.float32)
    reports: list[dict] = []

    # Running cursor — the earliest sample index the next clip is allowed
    # to start at, so a long clip doesn't overlap the next one.
    cursor = 0

    for idx, line in enumerate(narration_lines):
        report: dict = {
            "index": idx,
            "phase": line.phase,
            "intended_start_seconds": line.start_seconds,
            "text_preview": line.text[:80],
            "warnings": [],
        }

        clip = tts.synthesize_line(line.text)
        report["duration_seconds"] = round(clip.duration_seconds, 3)

        if clip.sample_rate != sample_rate:
            report["warnings"].append(
                f"unexpected sample rate {clip.sample_rate}, expected {sample_rate}"
            )

        # Intended placement
        intended_start_sample = int(round(line.start_seconds * sample_rate))

        # Actual placement respects the running cursor so we never overlap
        actual_start_sample = max(intended_start_sample, cursor)
        if actual_start_sample > intended_start_sample:
            shift_seconds = (actual_start_sample - intended_start_sample) / sample_rate
            report["warnings"].append(
                f"shifted {shift_seconds:.2f}s later than intended to avoid overlap with previous clip"
            )

        end_sample = actual_start_sample + len(clip.samples)
        if end_sample > total_samples:
            # The clip runs past the silent MP4's end. We keep the audio
            # (don't truncate) and warn — the muxed output will be slightly
            # longer than the silent MP4. ffmpeg handles this with -shortest
            # or by extending the video by holding the last frame; we use
            # the audio length as the master.
            report["warnings"].append(
                f"clip extends {(end_sample - total_samples) / sample_rate:.2f}s past video end "
                f"(audio will determine final duration)"
            )
            # Grow the buffer to fit
            new_total = end_sample + sample_rate  # +1s margin
            grown = np.zeros(new_total, dtype=np.float32)
            grown[: len(buffer)] = buffer
            buffer = grown
            total_samples = new_total

        # Place the clip
        buffer[actual_start_sample:actual_start_sample + len(clip.samples)] += clip.samples
        report["actual_start_seconds"] = round(actual_start_sample / sample_rate, 3)
        report["actual_end_seconds"] = round(end_sample / sample_rate, 3)

        # Check phase window if available
        if phase_windows:
            window = next((w for w in phase_windows if w.phase == line.phase), None)
            if window and window.end_seconds is not None:
                if report["actual_end_seconds"] > window.end_seconds + 0.5:
                    report["warnings"].append(
                        f"narration crosses phase boundary "
                        f"(phase {line.phase} ends at {window.end_seconds:.2f}s, "
                        f"narration ends at {report['actual_end_seconds']:.2f}s)"
                    )

        # Advance cursor (+ small inter-clip pad)
        cursor = end_sample + int(round(_INTER_CLIP_PAD_SECONDS * sample_rate))

        reports.append(report)

    # Apply master gain and clip to [-1, 1] just in case overlaps occurred
    buffer = buffer * _MASTER_GAIN
    np.clip(buffer, -1.0, 1.0, out=buffer)

    return buffer, reports


def write_wav(buffer: np.ndarray, sample_rate: int, path: Path) -> None:
    """Write a mono float32 buffer to a 16-bit PCM WAV file."""
    path.parent.mkdir(parents=True, exist_ok=True)
    sf.write(str(path), buffer, sample_rate, subtype="PCM_16")
