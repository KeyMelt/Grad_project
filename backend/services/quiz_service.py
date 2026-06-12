from __future__ import annotations

import json
import os
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from random import SystemRandom
from threading import Lock
from typing import TYPE_CHECKING, Any
from uuid import uuid4

from sqlmodel import select

from backend.models.quiz_question import QuizQuestion
from backend.services.firebase_progress_service import FirebaseProgressService

if TYPE_CHECKING:
    from backend.persistence import Database


_QUIZ_BANK_PATH = Path(__file__).resolve().parents[1] / "config" / "quiz_bank.json"


@dataclass(frozen=True)
class QuizQuestionTemplate:
    id: str
    concept: str
    prompt: str
    options: tuple[str, ...]
    correct_index: int


@dataclass(frozen=True)
class QuizCatalog:
    assessment_phases: frozenset[str]
    category_phases: dict[str, tuple[str, ...]]
    phase_labels: dict[str, str]
    phase_descriptions: dict[str, str]
    phase_flags: dict[str, dict[str, bool]]
    category_section_label: str
    category_section_description: str
    default_quiz_length: int
    default_category_quiz_length: int
    questions: tuple[QuizQuestionTemplate, ...]

    @property
    def supported_phases(self) -> frozenset[str]:
        return self.assessment_phases | frozenset(self.category_phases)


@dataclass
class QuizSession:
    session_id: str
    student_id: str
    phase: str
    question_ids: list[str]
    correct_indices: dict[str, int]
    questions: list[dict[str, Any]]


def load_quiz_catalog(path: Path = _QUIZ_BANK_PATH) -> QuizCatalog:
    with path.open("r", encoding="utf-8") as handle:
        raw = json.load(handle)

    assessment_phases = frozenset(
        str(phase["id"]) for phase in raw.get("assessment_phases", [])
    )
    category_phases: dict[str, tuple[str, ...]] = {}
    phase_labels: dict[str, str] = {}
    phase_descriptions: dict[str, str] = {}
    phase_flags: dict[str, dict[str, bool]] = {}

    for phase in raw.get("assessment_phases", []):
        phase_id = str(phase["id"])
        phase_labels[phase_id] = str(phase.get("label") or phase_id)
        phase_descriptions[phase_id] = str(phase.get("description") or "")
        phase_flags[phase_id] = {
            "requires_successful_run": bool(phase.get("requires_successful_run", False)),
            "triggers_post_study_survey": bool(
                phase.get("triggers_post_study_survey", False)
            ),
            "shows_n_gain": bool(phase.get("shows_n_gain", False)),
        }

    for quiz in raw.get("category_quizzes", []):
        quiz_id = str(quiz["id"])
        category_phases[quiz_id] = tuple(str(c) for c in quiz.get("concepts", []))
        phase_labels[quiz_id] = str(quiz.get("label") or quiz_id)
        phase_descriptions[quiz_id] = str(quiz.get("description") or "")
        phase_flags[quiz_id] = {
            "requires_successful_run": bool(quiz.get("requires_successful_run", False)),
            "triggers_post_study_survey": bool(
                quiz.get("triggers_post_study_survey", False)
            ),
            "shows_n_gain": bool(quiz.get("shows_n_gain", False)),
        }

    questions = tuple(_parse_question(item) for item in raw.get("questions", []))
    _validate_catalog(
        assessment_phases=assessment_phases,
        category_phases=category_phases,
        questions=questions,
    )

    return QuizCatalog(
        assessment_phases=assessment_phases,
        category_phases=category_phases,
        phase_labels=phase_labels,
        phase_descriptions=phase_descriptions,
        phase_flags=phase_flags,
        category_section_label=str(
            raw.get("category_section_label") or "Category quizzes"
        ),
        category_section_description=str(raw.get("category_section_description") or ""),
        default_quiz_length=int(raw.get("default_quiz_length", 6)),
        default_category_quiz_length=int(raw.get("default_category_quiz_length", 5)),
        questions=questions,
    )


def _parse_question(raw: dict[str, Any]) -> QuizQuestionTemplate:
    options = tuple(str(option) for option in raw.get("options", []))
    return QuizQuestionTemplate(
        id=str(raw["id"]),
        concept=str(raw["concept"]),
        prompt=str(raw["prompt"]),
        options=options,
        correct_index=int(raw.get("correct_index", 0)),
    )


def _validate_catalog(
    *,
    assessment_phases: frozenset[str],
    category_phases: dict[str, tuple[str, ...]],
    questions: tuple[QuizQuestionTemplate, ...],
) -> None:
    if not assessment_phases:
        raise ValueError("Quiz catalog must define at least one assessment phase.")
    if not questions:
        raise ValueError("Quiz catalog must define at least one question.")

    seen_ids: set[str] = set()
    concepts = {question.concept for question in questions}
    for question in questions:
        if question.id in seen_ids:
            raise ValueError(f"Duplicate quiz question id {question.id!r}.")
        seen_ids.add(question.id)
        if len(question.options) < 2:
            raise ValueError(f"Quiz question {question.id!r} needs at least two options.")
        if not 0 <= question.correct_index < len(question.options):
            raise ValueError(f"Quiz question {question.id!r} has an invalid correct_index.")

    for phase, phase_concepts in category_phases.items():
        missing = [concept for concept in phase_concepts if concept not in concepts]
        if missing:
            raise ValueError(
                f"Category quiz {phase!r} references concepts with no questions: {missing!r}."
            )


class QuizService:
    """Creates randomized quiz sessions from the editable quiz catalog."""

    def __init__(
        self,
        progress_service: FirebaseProgressService,
        database: Database | None = None,
        catalog: QuizCatalog | None = None,
    ) -> None:
        self._progress_service = progress_service
        self._database = database
        self._catalog = catalog or load_quiz_catalog()
        self._rng = SystemRandom()
        self._sessions: dict[str, QuizSession] = {}
        self._lock = Lock()
        if database is not None:
            self._ensure_seeded()

    def catalog_payload(self) -> dict[str, Any]:
        return {
            "category_section_label": self._catalog.category_section_label,
            "category_section_description": self._catalog.category_section_description,
            "assessment_phases": [
                {
                    "id": phase,
                    "label": self._catalog.phase_labels.get(phase, phase),
                    "description": self._catalog.phase_descriptions.get(phase, ""),
                    "question_count": self.quiz_length,
                    **self._catalog.phase_flags.get(phase, {}),
                }
                for phase in sorted(self._catalog.assessment_phases)
            ],
            "category_quizzes": [
                {
                    "id": phase,
                    "label": self._catalog.phase_labels.get(phase, phase),
                    "description": self._catalog.phase_descriptions.get(phase, ""),
                    "concepts": list(self._catalog.category_phases[phase]),
                    **self._catalog.phase_flags.get(phase, {}),
                    "question_count": min(
                        self.category_quiz_length,
                        len(
                            [
                                question
                                for question in self._catalog.questions
                                if question.concept in self._catalog.category_phases[phase]
                            ]
                        ),
                    ),
                }
                for phase in self._catalog.category_phases
            ],
        }

    @property
    def quiz_length(self) -> int:
        raw = os.environ.get("RL_IDE_QUIZ_LENGTH", "").strip()
        if raw.isdigit():
            return int(raw)
        return self._catalog.default_quiz_length

    @property
    def category_quiz_length(self) -> int:
        raw = os.environ.get("RL_IDE_CATEGORY_QUIZ_LENGTH", "").strip()
        if raw.isdigit():
            return int(raw)
        return self._catalog.default_category_quiz_length

    def start_session(self, student_id: str, phase: str) -> dict[str, Any]:
        if self._progress_service.get_dashboard(student_id) is None:
            raise ValueError("Unknown student_id.")
        if phase not in self._catalog.supported_phases:
            raise ValueError(f"Unsupported quiz phase '{phase}'.")

        question_templates = self._select_questions(student_id, phase)
        questions: list[dict[str, Any]] = []
        correct_indices: dict[str, int] = {}
        question_ids: list[str] = []

        for template in question_templates:
            option_order = list(range(len(template.options)))
            self._rng.shuffle(option_order)
            reordered_options = [template.options[index] for index in option_order]
            correct_indices[template.id] = option_order.index(template.correct_index)
            question_ids.append(template.id)
            questions.append(
                {
                    "id": template.id,
                    "concept": template.concept,
                    "prompt": template.prompt,
                    "options": reordered_options,
                }
            )

        session_id = uuid4().hex
        self._sessions[session_id] = QuizSession(
            session_id=session_id,
            student_id=student_id,
            phase=phase,
            question_ids=question_ids,
            correct_indices=correct_indices,
            questions=questions,
        )

        return {
            "session_id": session_id,
            "phase": phase,
            "phase_label": self._catalog.phase_labels.get(phase, phase),
            "question_count": len(questions),
            "questions": questions,
        }

    def submit_session(
        self,
        student_id: str,
        session_id: str,
        answers: list[dict[str, int]],
    ) -> dict[str, Any]:
        session = self._sessions.get(session_id)
        if session is None:
            raise ValueError("Unknown quiz session.")
        if session.student_id != student_id:
            raise ValueError("Quiz session does not belong to this student.")

        answer_map = {answer["question_id"]: answer["selected_index"] for answer in answers}
        score = 0
        concept_results: list[dict[str, Any]] = []
        question_by_id = {question["id"]: question for question in session.questions}
        for question_id in session.question_ids:
            correct = answer_map.get(question_id) == session.correct_indices[question_id]
            if correct:
                score += 1
            question = question_by_id.get(question_id, {})
            concept_results.append(
                {
                    "question_id": question_id,
                    "concept": question.get("concept", "Unknown Concept"),
                    "correct": correct,
                }
            )

        total_questions = len(session.question_ids)
        percentage = round((score / total_questions) * 100, 2) if total_questions else 0.0
        dashboard = self._progress_service.record_quiz_result(
            student_id=student_id,
            phase=session.phase,
            percentage=percentage,
            question_ids=session.question_ids,
        )
        del self._sessions[session_id]

        if dashboard is None:
            raise ValueError("Unknown student_id.")

        return {
            "phase": session.phase,
            "phase_label": self._catalog.phase_labels.get(session.phase, session.phase),
            "score": score,
            "total_questions": total_questions,
            "percentage": percentage,
            "n_gain": dashboard["progress"]["n_gain"],
            "progress": dashboard["progress"],
            "concept_results": concept_results,
        }

    def _load_all_questions(self) -> list[QuizQuestionTemplate]:
        if self._database is None:
            return list(self._catalog.questions)
        configured_questions = {
            template.id: template for template in self._catalog.questions
        }
        with self._database.session() as session:
            rows = session.exec(select(QuizQuestion)).all()
        if not rows:
            return list(self._catalog.questions)

        merged = dict(configured_questions)
        for row in rows:
            if row.created_by_user_id == "system" and row.id not in configured_questions:
                continue
            merged[row.id] = QuizQuestionTemplate(
                id=row.id,
                concept=row.concept,
                prompt=row.prompt,
                options=tuple(json.loads(row.options_json)),
                correct_index=row.correct_index,
            )
        return list(merged.values())

    def _select_questions(self, student_id: str, phase: str) -> list[QuizQuestionTemplate]:
        all_questions = self._load_all_questions()
        if phase in self._catalog.category_phases:
            concepts = set(self._catalog.category_phases[phase])
            all_questions = [q for q in all_questions if q.concept in concepts]

        used_question_ids = set(self._progress_service.get_question_history(student_id))
        unused_templates = [q for q in all_questions if q.id not in used_question_ids]
        used_templates = [q for q in all_questions if q.id in used_question_ids]
        quiz_len = (
            self.category_quiz_length
            if phase in self._catalog.category_phases
            else self.quiz_length
        )

        if len(unused_templates) >= quiz_len:
            selected = self._rng.sample(unused_templates, quiz_len)
        else:
            selected = list(unused_templates)
            remaining_count = quiz_len - len(selected)
            if remaining_count > 0 and used_templates:
                selected.extend(
                    self._rng.sample(used_templates, min(remaining_count, len(used_templates)))
                )

        self._rng.shuffle(selected)
        return selected

    def _ensure_seeded(self) -> None:
        assert self._database is not None
        with self._lock:
            with self._database.session() as session:
                existing_rows = {
                    row.id: row for row in session.exec(select(QuizQuestion)).all()
                }
            now = datetime.now(timezone.utc)
            configured_ids = {template.id for template in self._catalog.questions}
            for template in self._catalog.questions:
                with self._database.session() as session:
                    existing = session.get(QuizQuestion, template.id)
                    if existing is None:
                        session.add(
                            QuizQuestion(
                                id=template.id,
                                concept=template.concept,
                                prompt=template.prompt,
                                options_json=json.dumps(list(template.options)),
                                correct_index=template.correct_index,
                                created_by_user_id="system",
                                created_at_utc=now,
                                updated_at_utc=now,
                            )
                        )
                    elif existing_rows[template.id].created_by_user_id == "system":
                        existing.concept = template.concept
                        existing.prompt = template.prompt
                        existing.options_json = json.dumps(list(template.options))
                        existing.correct_index = template.correct_index
                        existing.updated_at_utc = now
                        session.add(existing)
                    session.commit()
            with self._database.session() as session:
                stale_system_rows = [
                    row
                    for row in session.exec(select(QuizQuestion)).all()
                    if row.created_by_user_id == "system"
                    and row.id not in configured_ids
                ]
                for row in stale_system_rows:
                    session.delete(row)
                if stale_system_rows:
                    session.commit()
