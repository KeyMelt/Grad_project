"""Kokoro-onnx TTS adapter.

Single-class wrapper around `kokoro_onnx.Kokoro` that:

- lazy-loads the model from `settings.KOKORO_MODEL_PATH` (~310 MB on first
  use; cached in process for the rest of the synth run)
- exposes `synthesize_line(text, voice, speed) -> SynthesizedClip`
- returns mono float32 PCM at 24 kHz (Kokoro's native sample rate)

Why a class rather than module-level globals: synthesise.py loads Kokoro
once and reuses it across all narration lines in a single video, which
amortises the ~0.8 s model-load over the ~40–80 lines per video. Don't
construct a fresh instance per line.
"""
from __future__ import annotations

import logging
from dataclasses import dataclass
from pathlib import Path

import numpy as np

from manim_service import settings
from manim_service.audio.voices import is_approved

logger = logging.getLogger(__name__)


@dataclass(frozen=True)
class SynthesizedClip:
    """A single synthesised narration clip."""

    samples: np.ndarray        # float32 mono PCM, range [-1.0, 1.0]
    sample_rate: int           # always 24000 for Kokoro v1.0
    duration_seconds: float    # len(samples) / sample_rate
    text: str                  # the line that was synthesised
    voice: str                 # voice_id used


class KokoroTTS:
    """Lazy-loading wrapper around kokoro-onnx."""

    def __init__(
        self,
        model_path: Path | str | None = None,
        voices_path: Path | str | None = None,
    ) -> None:
        self.model_path = Path(model_path or settings.KOKORO_MODEL_PATH)
        self.voices_path = Path(voices_path or settings.KOKORO_VOICES_PATH)
        self._kokoro = None  # constructed on first call to synthesise

        if not self.model_path.exists():
            raise FileNotFoundError(
                f"Kokoro model not found at {self.model_path}. "
                f"Download from https://github.com/thewh1teagle/kokoro-onnx/releases/download/model-files-v1.0/kokoro-v1.0.onnx"
            )
        if not self.voices_path.exists():
            raise FileNotFoundError(
                f"Kokoro voices file not found at {self.voices_path}. "
                f"Download from https://github.com/thewh1teagle/kokoro-onnx/releases/download/model-files-v1.0/voices-v1.0.bin"
            )

    # ------------------------------------------------------------------
    # Internal: lazy load
    # ------------------------------------------------------------------

    def _ensure_loaded(self) -> None:
        if self._kokoro is not None:
            return
        # Import is deferred so callers can still import this module without
        # kokoro-onnx installed (e.g., for type checking).
        from kokoro_onnx import Kokoro

        logger.info("Loading Kokoro model from %s", self.model_path)
        self._kokoro = Kokoro(str(self.model_path), str(self.voices_path))

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def synthesize_line(
        self,
        text: str,
        *,
        voice: str | None = None,
        speed: float | None = None,
        lang: str = "en-us",
    ) -> SynthesizedClip:
        """Synthesise a single narration line and return a SynthesizedClip.

        `voice` defaults to `settings.DEFAULT_NARRATOR_VOICE`.
        `speed` defaults to `settings.DEFAULT_NARRATOR_SPEED`.

        Empty / whitespace-only text returns a 0-duration clip without
        invoking the model (lets compose.py treat them as silence markers).
        """
        text = text.strip()
        voice = voice or settings.DEFAULT_NARRATOR_VOICE
        speed = speed if speed is not None else settings.DEFAULT_NARRATOR_SPEED

        if not text:
            return SynthesizedClip(
                samples=np.zeros(0, dtype=np.float32),
                sample_rate=24000,
                duration_seconds=0.0,
                text="",
                voice=voice,
            )

        if not is_approved(voice):
            logger.warning(
                "Voice %r is not on the approved list. Synthesising anyway. "
                "Add it to manim_service/audio/voices.APPROVED_VOICES if it "
                "should become part of the series catalog.",
                voice,
            )

        self._ensure_loaded()
        samples, sample_rate = self._kokoro.create(
            text, voice=voice, speed=speed, lang=lang
        )

        # kokoro-onnx returns float32 already; defensive cast in case of
        # version changes.
        samples = np.asarray(samples, dtype=np.float32)
        duration = len(samples) / sample_rate

        logger.debug(
            "Synthesised %d chars → %.2fs (%s, speed=%.2f)",
            len(text), duration, voice, speed,
        )
        return SynthesizedClip(
            samples=samples,
            sample_rate=int(sample_rate),
            duration_seconds=duration,
            text=text,
            voice=voice,
        )
