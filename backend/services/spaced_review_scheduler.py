from __future__ import annotations

from typing import Any

from backend.config.trigger_config import (
    REVIEW_MASTERY_GAP_WEIGHT,
    REVIEW_MASTERY_THRESHOLD,
    REVIEW_STALENESS_DAYS_THRESHOLD,
    REVIEW_STALENESS_WEIGHT,
    REVIEW_SUPPORT_NEED_WEIGHT,
)


class SpacedReviewScheduler:
    """Selects one transparent review recommendation from latest mastery snapshots."""

    def select(self, snapshots: list[dict[str, Any]]) -> dict[str, Any] | None:
        candidates: list[dict[str, Any]] = []
        for snapshot in snapshots:
            staleness_days = int(snapshot.get("staleness_days") or 0)
            mastery_score = float(snapshot.get("mastery_score") or 0.0)
            support_need_score = float(snapshot.get("support_need_score") or 0.0)
            if (
                staleness_days <= REVIEW_STALENESS_DAYS_THRESHOLD
                or mastery_score >= REVIEW_MASTERY_THRESHOLD
            ):
                continue

            priority = (
                (staleness_days * REVIEW_STALENESS_WEIGHT)
                + (support_need_score * REVIEW_SUPPORT_NEED_WEIGHT)
                + ((1 - mastery_score) * REVIEW_MASTERY_GAP_WEIGHT)
            )
            candidates.append(
                {
                    "concept_id": snapshot.get("concept_id"),
                    "lesson_id": snapshot.get("lesson_id"),
                    "mastery_score": mastery_score,
                    "support_need_score": support_need_score,
                    "confidence_score": float(snapshot.get("confidence_score") or 0.0),
                    "staleness_days": staleness_days,
                    "review_priority": round(priority, 3),
                }
            )

        if not candidates:
            return None
        return max(candidates, key=lambda item: item["review_priority"])
