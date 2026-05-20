"""Kokoro voice catalog and series defaults.

The concept-video series uses a single narrator across all videos for
consistency (STYLE_BIBLE: single-narrator policy). The default is locked
to `am_michael` — measured, professorial American male, the closest fit
to a 3Blue1Brown-style lecture voice in the Kokoro v1.0 catalog.

If you ever want to vary voices (e.g. a separate "Study Buddy" output
type using a different voice), set `DEFAULT_NARRATOR_VOICE` in env or
pass `--voice` to the synthesise CLI.
"""
from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class VoiceProfile:
    """A Kokoro voice with metadata used by the Voice & BGM agent."""

    voice_id: str            # exact Kokoro voice name (e.g. "am_michael")
    display_name: str        # human-readable name for logs/captions
    register: str            # "professorial", "conversational", etc.
    accent: str              # "American", "British"
    sex: str                 # "male", "female"


# Curated subset — only the voices we've actually approved for series use.
# The full Kokoro catalog is larger; gate additions through STYLE_BIBLE.
APPROVED_VOICES: dict[str, VoiceProfile] = {
    "am_michael": VoiceProfile(
        voice_id="am_michael",
        display_name="Michael",
        register="professorial",
        accent="American",
        sex="male",
    ),
    "am_adam": VoiceProfile(
        voice_id="am_adam",
        display_name="Adam",
        register="conversational",
        accent="American",
        sex="male",
    ),
    "bm_george": VoiceProfile(
        voice_id="bm_george",
        display_name="George",
        register="lecturer",
        accent="British",
        sex="male",
    ),
    "af_bella": VoiceProfile(
        voice_id="af_bella",
        display_name="Bella",
        register="warm",
        accent="American",
        sex="female",
    ),
    "bf_emma": VoiceProfile(
        voice_id="bf_emma",
        display_name="Emma",
        register="clear",
        accent="British",
        sex="female",
    ),
}


def is_approved(voice_id: str) -> bool:
    """Return True if the voice is on the approved list for series use."""
    return voice_id in APPROVED_VOICES


def describe(voice_id: str) -> str:
    """Human-readable one-line description for logs."""
    profile = APPROVED_VOICES.get(voice_id)
    if profile is None:
        return f"{voice_id} (not on approved list)"
    return (
        f"{profile.display_name} — {profile.register} {profile.accent} "
        f"{profile.sex} voice ({profile.voice_id})"
    )
