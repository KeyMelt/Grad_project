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
    family_id: str
    stage: str
    concept: str
    prompt: str
    options: tuple[str, ...]
    correct_index: int


@dataclass(frozen=True)
class QuizPhaseTemplate:
    id: str
    label: str
    description: str
    triggers_post_study_survey: bool = False
    shows_n_gain: bool = True


@dataclass(frozen=True)
class QuizFamilyTemplate:
    id: str
    label: str
    description: str
    lesson_ids: tuple[str, ...]
    pretest: QuizPhaseTemplate
    posttest: QuizPhaseTemplate


@dataclass(frozen=True)
class QuizCatalog:
    quiz_families: tuple[QuizFamilyTemplate, ...]
    category_section_label: str
    category_section_description: str
    default_quiz_length: int
    minimum_family_stage_questions: int
    questions: tuple[QuizQuestionTemplate, ...]

    @property
    def phase_map(self) -> dict[str, tuple[QuizFamilyTemplate, str, QuizPhaseTemplate]]:
        phases: dict[str, tuple[QuizFamilyTemplate, str, QuizPhaseTemplate]] = {}
        for family in self.quiz_families:
            phases[family.pretest.id] = (family, "pre", family.pretest)
            phases[family.posttest.id] = (family, "post", family.posttest)
        return phases

    @property
    def supported_phases(self) -> frozenset[str]:
        return frozenset(self.phase_map)


@dataclass
class QuizSession:
    session_id: str
    student_id: str
    phase: str
    family_id: str
    stage: str
    question_ids: list[str]
    correct_indices: dict[str, int]
    questions: list[dict[str, Any]]


def load_quiz_catalog(path: Path = _QUIZ_BANK_PATH) -> QuizCatalog:
    with path.open("r", encoding="utf-8") as handle:
        raw = json.load(handle)

    families = tuple(_parse_family(item) for item in raw.get("families", []))
    questions = tuple(_parse_question(item) for item in raw.get("questions", []))
    default_quiz_length = int(raw.get("default_quiz_length", 6))
    minimum_family_stage_questions = int(
        raw.get("minimum_family_stage_questions", max(10, default_quiz_length))
    )
    _validate_catalog(
        families=families,
        questions=questions,
        minimum_family_stage_questions=minimum_family_stage_questions,
        known_lesson_ids=_load_core_lesson_ids(),
    )

    return QuizCatalog(
        quiz_families=families,
        category_section_label=str(
            raw.get("category_section_label") or "Equation family quizzes"
        ),
        category_section_description=str(raw.get("category_section_description") or ""),
        default_quiz_length=default_quiz_length,
        minimum_family_stage_questions=minimum_family_stage_questions,
        questions=questions,
    )


def _parse_family(raw: dict[str, Any]) -> QuizFamilyTemplate:
    family_id = str(raw["id"])
    return QuizFamilyTemplate(
        id=family_id,
        label=str(raw.get("label") or family_id),
        description=str(raw.get("description") or ""),
        lesson_ids=tuple(str(value) for value in raw.get("lesson_ids", [])),
        pretest=_parse_phase(raw.get("pretest") or {}, family_id=family_id, stage="pre"),
        posttest=_parse_phase(
            raw.get("posttest") or {}, family_id=family_id, stage="post"
        ),
    )


def _parse_phase(raw: dict[str, Any], *, family_id: str, stage: str) -> QuizPhaseTemplate:
    default_id = f"{family_id}:{stage}"
    default_label = "Pre-test" if stage == "pre" else "Post-test"
    return QuizPhaseTemplate(
        id=str(raw.get("id") or default_id),
        label=str(raw.get("label") or default_label),
        description=str(raw.get("description") or ""),
        triggers_post_study_survey=bool(raw.get("triggers_post_study_survey", False)),
        shows_n_gain=bool(raw.get("shows_n_gain", True)),
    )


def _parse_question(raw: dict[str, Any]) -> QuizQuestionTemplate:
    options = tuple(str(option) for option in raw.get("options", []))
    return QuizQuestionTemplate(
        id=str(raw["id"]),
        family_id=str(raw["family_id"]),
        stage=str(raw.get("stage") or "both").lower(),
        concept=str(raw["concept"]),
        prompt=str(raw["prompt"]),
        options=options,
        correct_index=int(raw.get("correct_index", 0)),
    )


def _validate_catalog(
    *,
    families: tuple[QuizFamilyTemplate, ...],
    questions: tuple[QuizQuestionTemplate, ...],
    minimum_family_stage_questions: int,
    known_lesson_ids: set[str] | None = None,
) -> None:
    if not families:
        raise ValueError("Quiz catalog must define at least one quiz family.")
    if not questions:
        raise ValueError("Quiz catalog must define at least one question.")

    seen_ids: set[str] = set()
    seen_phase_ids: set[str] = set()
    family_ids = {family.id for family in families}
    for family in families:
        if not family.lesson_ids:
            raise ValueError(f"Quiz family {family.id!r} must define lesson_ids.")
        if known_lesson_ids is not None:
            missing_lessons = [
                lesson_id
                for lesson_id in family.lesson_ids
                if lesson_id not in known_lesson_ids
            ]
            if missing_lessons:
                raise ValueError(
                    f"Quiz family {family.id!r} references unknown lesson_ids: "
                    f"{missing_lessons!r}."
                )
        for phase in (family.pretest, family.posttest):
            if phase.id in seen_phase_ids:
                raise ValueError(f"Duplicate quiz phase id {phase.id!r}.")
            seen_phase_ids.add(phase.id)

    for question in questions:
        if question.id in seen_ids:
            raise ValueError(f"Duplicate quiz question id {question.id!r}.")
        seen_ids.add(question.id)
        if question.family_id not in family_ids:
            raise ValueError(
                f"Quiz question {question.id!r} references unknown family "
                f"{question.family_id!r}."
            )
        if question.stage not in {"pre", "post", "both"}:
            raise ValueError(f"Quiz question {question.id!r} has invalid stage.")
        if len(question.options) < 2:
            raise ValueError(f"Quiz question {question.id!r} needs at least two options.")
        if not 0 <= question.correct_index < len(question.options):
            raise ValueError(f"Quiz question {question.id!r} has an invalid correct_index.")

    for family in families:
        for stage in ("pre", "post"):
            eligible_count = len(
                [
                    question
                    for question in questions
                    if question.family_id == family.id
                    and question.stage in {stage, "both"}
                ]
            )
            if eligible_count < minimum_family_stage_questions:
                raise ValueError(
                    f"Quiz family {family.id!r} {stage!r} stage needs at least "
                    f"{minimum_family_stage_questions} eligible questions."
                )


def _load_core_lesson_ids() -> set[str] | None:
    try:
        from backend.services.lesson_registry_service import _CORE_LESSONS
    except Exception:
        return None
    return {str(lesson["id"]) for lesson in _CORE_LESSONS if lesson.get("id")}


def _family_score(progress: dict[str, Any], family_id: str) -> dict[str, Any]:
    raw_scores = progress.get("family_quiz_scores", {})
    raw_family = raw_scores.get(family_id, {})
    attempts = raw_family.get("attempts", {})
    return {
        "pretest_score": raw_family.get("pretest_score"),
        "posttest_score": raw_family.get("posttest_score"),
        "n_gain": raw_family.get("n_gain"),
        "attempts": {
            "pretest": int(attempts.get("pretest", 0)),
            "posttest": int(attempts.get("posttest", 0)),
        },
    }


def _compute_n_gain(pretest_score: float | None, posttest_score: float | None) -> float | None:
    if pretest_score is None or posttest_score is None:
        return None
    if pretest_score >= 100:
        return 1.0 if posttest_score >= 100 else 0.0
    return round((posttest_score - pretest_score) / (100 - pretest_score), 3)


def is_post_phase_unlocked(
    *,
    dashboard: dict[str, Any],
    family: QuizFamilyTemplate,
) -> bool:
    completed = set(
        str(item)
        for item in dashboard.get("progress", {}).get("completed_lesson_ids", [])
    )
    return all(lesson_id in completed for lesson_id in family.lesson_ids)


def _locked_post_message(family: QuizFamilyTemplate) -> str:
    lesson_text = ", ".join(family.lesson_ids)
    return (
        f"Complete {family.label} lesson work before taking the post-test "
        f"({lesson_text})."
    )


def _question_matches_stage(question: QuizQuestionTemplate, family_id: str, stage: str) -> bool:
    return question.family_id == family_id and question.stage in {stage, "both"}


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
            "assessment_phases": [],
            "category_quizzes": [],
            "quiz_families": [
                self._family_payload(family)
                for family in self._catalog.quiz_families
            ],
        }

    def _family_payload(self, family: QuizFamilyTemplate) -> dict[str, Any]:
        return {
            "id": family.id,
            "label": family.label,
            "description": family.description,
            "lesson_ids": list(family.lesson_ids),
            "pretest": self._phase_payload(family, "pre", family.pretest),
            "posttest": self._phase_payload(family, "post", family.posttest),
        }

    def _phase_payload(
        self,
        family: QuizFamilyTemplate,
        stage: str,
        phase: QuizPhaseTemplate,
    ) -> dict[str, Any]:
        return {
            "id": phase.id,
            "label": phase.label,
            "description": phase.description,
            "question_count": min(
                self.quiz_length,
                len(
                    [
                        question
                        for question in self._catalog.questions
                        if _question_matches_stage(question, family.id, stage)
                    ]
                ),
            ),
            "family_id": family.id,
            "family_label": family.label,
            "stage": stage,
            "lesson_ids": list(family.lesson_ids),
            "requires_lesson_completion": stage == "post",
            "triggers_post_study_survey": phase.triggers_post_study_survey,
            "shows_n_gain": phase.shows_n_gain,
        }

    @property
    def quiz_length(self) -> int:
        raw = os.environ.get("RL_IDE_QUIZ_LENGTH", "").strip()
        if raw.isdigit():
            return int(raw)
        return self._catalog.default_quiz_length

    def start_session(self, student_id: str, phase: str) -> dict[str, Any]:
        dashboard = self._progress_service.get_dashboard(student_id)
        if dashboard is None:
            raise ValueError("Unknown student_id.")
        phase_metadata = self._catalog.phase_map.get(phase)
        if phase_metadata is None:
            raise ValueError(f"Unsupported quiz phase '{phase}'.")
        family, stage, phase_template = phase_metadata
        if stage == "post" and not is_post_phase_unlocked(
            dashboard=dashboard,
            family=family,
        ):
            raise ValueError(_locked_post_message(family))

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
            family_id=family.id,
            stage=stage,
            question_ids=question_ids,
            correct_indices=correct_indices,
            questions=questions,
        )

        return {
            "session_id": session_id,
            "phase": phase,
            "phase_label": phase_template.label,
            "family_id": family.id,
            "family_label": family.label,
            "stage": stage,
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
            family_id=session.family_id,
            stage=session.stage,
        )
        del self._sessions[session_id]

        if dashboard is None:
            raise ValueError("Unknown student_id.")

        return {
            "phase": session.phase,
            "phase_label": self._catalog.phase_map[session.phase][2].label,
            "family_id": session.family_id,
            "family_label": self._catalog.phase_map[session.phase][0].label,
            "stage": session.stage,
            "score": score,
            "total_questions": total_questions,
            "percentage": percentage,
            "n_gain": _family_score(dashboard["progress"], session.family_id)["n_gain"],
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
            configured = configured_questions.get(row.id)
            if configured is None:
                continue
            merged[row.id] = QuizQuestionTemplate(
                id=row.id,
                family_id=configured.family_id,
                stage=configured.stage,
                concept=row.concept,
                prompt=row.prompt,
                options=tuple(json.loads(row.options_json)),
                correct_index=row.correct_index,
            )
        return list(merged.values())

    def _select_questions(self, student_id: str, phase: str) -> list[QuizQuestionTemplate]:
        family, stage, _phase = self._catalog.phase_map[phase]
        all_questions = self._load_all_questions()
        all_questions = [
            question
            for question in all_questions
            if _question_matches_stage(question, family.id, stage)
        ]

        used_question_ids = set(
            self._progress_service.get_question_history(
                student_id,
                family_id=family.id,
                stage=stage,
            )
        )
        unused_templates = [q for q in all_questions if q.id not in used_question_ids]
        used_templates = [q for q in all_questions if q.id in used_question_ids]
        quiz_len = self.quiz_length

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
