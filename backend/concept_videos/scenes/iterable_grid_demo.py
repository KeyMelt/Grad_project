from __future__ import annotations

try:
    from backend.concept_videos.scenes.helper_demo import IterableGridOrbitDemo as _BaseIterableGridOrbitDemo
except ModuleNotFoundError:
    from helper_demo import IterableGridOrbitDemo as _BaseIterableGridOrbitDemo


class IterableGridOrbitDemo(_BaseIterableGridOrbitDemo):
    pass

__all__ = ["IterableGridOrbitDemo"]
