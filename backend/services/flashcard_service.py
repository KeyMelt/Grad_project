"""Flashcard catalog service — seeds and serves vocabulary flashcards."""

from __future__ import annotations

from datetime import datetime, timezone
from threading import Lock

from sqlmodel import select

from backend.models.flashcard import Flashcard
from backend.persistence import Database

_BUILTIN_FLASHCARDS: list[dict] = [
    {
        "id": "fc_bellman_expectation",
        "term": "Bellman Expectation",
        "category": "Dynamic Programming",
        "explanation": "Policy evaluation updates each state with an expectation over policy choices and transition probabilities.",
        "sort_order": 0,
    },
    {
        "id": "fc_bellman_optimality",
        "term": "Bellman Optimality",
        "category": "Dynamic Programming",
        "explanation": "Value iteration selects the largest action backup instead of averaging under a fixed policy.",
        "sort_order": 1,
    },
    {
        "id": "fc_policy_improvement",
        "term": "Policy Improvement",
        "category": "Dynamic Programming",
        "explanation": "Policy improvement chooses the greedy action for each state using the current value table.",
        "sort_order": 2,
    },
    {
        "id": "fc_first_visit_return",
        "term": "First-Visit Return",
        "category": "Monte Carlo Methods",
        "explanation": "First-visit Monte Carlo updates a state only once per episode, using the full discounted return from its first occurrence.",
        "sort_order": 3,
    },
    {
        "id": "fc_sarsa",
        "term": "SARSA",
        "category": "Temporal Difference",
        "explanation": "SARSA is on-policy because its TD target uses the next action that the behaviour policy actually sampled.",
        "sort_order": 4,
    },
    {
        "id": "fc_td_target",
        "term": "TD Target",
        "category": "Temporal Difference",
        "explanation": "The Q-learning target is the immediate reward plus gamma times the best next-state value.",
        "sort_order": 5,
    },
    {
        "id": "fc_transition_probability",
        "term": "Transition Probability",
        "category": "Environment Model",
        "explanation": "Transition probability tells us how likely the environment is to move to a particular next state after a chosen action.",
        "sort_order": 6,
    },
    {
        "id": "fc_normalized_gain",
        "term": "Normalized Gain",
        "category": "Assessment",
        "explanation": "N-gain measures conceptual growth as (post - pre) / (100 - pre).",
        "sort_order": 7,
    },
]


class FlashcardService:
    """Seeds built-in flashcards and serves them to the client."""

    def __init__(self, *, database: Database) -> None:
        self._database = database
        self._lock = Lock()
        self._ensure_seeded()

    def list_flashcards(self) -> list[dict]:
        with self._database.session() as session:
            rows = session.exec(
                select(Flashcard).order_by(Flashcard.sort_order, Flashcard.category, Flashcard.term)
            ).all()
        return [
            {
                "id": row.id,
                "term": row.term,
                "category": row.category,
                "explanation": row.explanation,
            }
            for row in rows
        ]

    def _ensure_seeded(self) -> None:
        now = datetime.now(timezone.utc)
        with self._lock:
            with self._database.session() as session:
                existing_ids = {row.id for row in session.exec(select(Flashcard)).all()}
            for card in _BUILTIN_FLASHCARDS:
                if card["id"] in existing_ids:
                    continue
                with self._database.session() as session:
                    session.add(
                        Flashcard(
                            id=card["id"],
                            term=card["term"],
                            category=card["category"],
                            explanation=card["explanation"],
                            sort_order=card["sort_order"],
                            created_by_user_id="system",
                            created_at_utc=now,
                            updated_at_utc=now,
                        )
                    )
                    session.commit()
