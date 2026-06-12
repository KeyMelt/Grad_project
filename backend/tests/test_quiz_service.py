import unittest
from copy import deepcopy
import json
import os
import tempfile
from pathlib import Path

from backend.models.quiz_question import QuizQuestion
from backend.persistence import Database
from backend.services.quiz_service import QuizService, load_quiz_catalog


class _FakeProgressService:
    def __init__(self) -> None:
        self._dashboards: dict[str, dict] = {}
        self._question_history: dict[str, list[str]] = {}

    def sign_in(self, display_name: str, password: str) -> dict:
        del password
        dashboard = {
            "student": {
                "id": "student-1",
                "display_name": display_name,
            },
            "progress": {
                "completed_lesson_ids": [],
                "successful_runs": 0,
                "latest_lesson_id": None,
                "pretest_score": None,
                "posttest_score": None,
                "n_gain": None,
                "quiz_attempts": {"pretest": 0, "posttest": 0},
                "family_quiz_scores": {},
                "question_history": [],
                "question_history_by_scope": {},
            },
        }
        self._dashboards["student-1"] = dashboard
        self._question_history["student-1"] = []
        return dashboard

    def get_dashboard(self, student_id: str) -> dict | None:
        return self._dashboards.get(student_id)

    def record_quiz_result(
        self,
        student_id: str,
        phase: str,
        percentage: float,
        question_ids: list[str],
        family_id: str | None = None,
        stage: str | None = None,
    ) -> dict | None:
        dashboard = self._dashboards.get(student_id)
        if dashboard is None:
            return None
        progress = dashboard["progress"]
        progress["quiz_attempts"][phase] = int(
            progress["quiz_attempts"].get(phase, 0)
        ) + 1
        if family_id and stage in {"pre", "post"}:
            family_scores = deepcopy(progress.get("family_quiz_scores", {}))
            score = family_scores.get(
                family_id,
                {
                    "pretest_score": None,
                    "posttest_score": None,
                    "n_gain": None,
                    "attempts": {"pretest": 0, "posttest": 0},
                },
            )
            if stage == "pre":
                score["pretest_score"] = percentage
                score["attempts"]["pretest"] += 1
            else:
                score["posttest_score"] = percentage
                score["attempts"]["posttest"] += 1
            score["n_gain"] = self._compute_n_gain(
                score.get("pretest_score"),
                score.get("posttest_score"),
            )
            family_scores[family_id] = score
            progress["family_quiz_scores"] = family_scores
            pre_scores = [
                value["pretest_score"]
                for value in family_scores.values()
                if value.get("pretest_score") is not None
            ]
            post_scores = [
                value["posttest_score"]
                for value in family_scores.values()
                if value.get("posttest_score") is not None
            ]
            progress["pretest_score"] = (
                round(sum(pre_scores) / len(pre_scores), 2) if pre_scores else None
            )
            progress["posttest_score"] = (
                round(sum(post_scores) / len(post_scores), 2) if post_scores else None
            )
        elif phase == "pretest":
            progress["pretest_score"] = percentage
        elif phase == "posttest":
            progress["posttest_score"] = percentage

        progress["n_gain"] = self._compute_n_gain(
            progress.get("pretest_score"),
            progress.get("posttest_score"),
        )
        history = self._question_history.setdefault(student_id, [])
        history.extend(question_ids)
        progress["question_history"].extend(question_ids)
        if family_id and stage:
            scoped_history = progress["question_history_by_scope"].setdefault(
                f"{family_id}:{stage}",
                [],
            )
            scoped_history.extend(question_ids)
        return dashboard

    def record_lesson_completion(self, student_id: str, lesson_id: str) -> dict | None:
        dashboard = self._dashboards.get(student_id)
        if dashboard is None:
            return None
        progress = dashboard["progress"]
        if lesson_id not in progress["completed_lesson_ids"]:
            progress["completed_lesson_ids"].append(lesson_id)
        progress["successful_runs"] += 1
        progress["latest_lesson_id"] = lesson_id
        return dashboard

    def get_question_history(
        self,
        student_id: str,
        family_id: str | None = None,
        stage: str | None = None,
    ) -> list[str]:
        progress = self._dashboards.get(student_id, {}).get("progress", {})
        if family_id and stage:
            return list(
                progress.get("question_history_by_scope", {}).get(
                    f"{family_id}:{stage}",
                    [],
                )
            )
        return list(self._question_history.get(student_id, []))

    @staticmethod
    def _compute_n_gain(pretest_score: float | None, posttest_score: float | None):
        if pretest_score is None or posttest_score is None:
            return None
        if pretest_score >= 100:
            return 1.0 if posttest_score >= 100 else 0.0
        return round((posttest_score - pretest_score) / (100 - pretest_score), 3)


class QuizServiceTest(unittest.TestCase):
    def setUp(self):
        self._old_quiz_length = os.environ.get("RL_IDE_QUIZ_LENGTH")
        os.environ["RL_IDE_QUIZ_LENGTH"] = "4"
        self.progress_service = _FakeProgressService()
        self.quiz_service = QuizService(self.progress_service)
        self.dashboard = self.progress_service.sign_in(
            "Maya Hassan",
            "SecurePass123!",
        )
        self.student_id = self.dashboard["student"]["id"]

    def tearDown(self):
        if self._old_quiz_length is None:
            os.environ.pop("RL_IDE_QUIZ_LENGTH", None)
        else:
            os.environ["RL_IDE_QUIZ_LENGTH"] = self._old_quiz_length

    def test_start_session_returns_randomized_questions_without_answer_key(self):
        session = self.quiz_service.start_session(self.student_id, "dp_policy_eval:pre")

        self.assertEqual(session["phase"], "dp_policy_eval:pre")
        self.assertEqual(session["family_id"], "dp_policy_eval")
        self.assertEqual(session["stage"], "pre")
        self.assertEqual(session["question_count"], self.quiz_service.quiz_length)
        self.assertEqual(len(session["questions"]), self.quiz_service.quiz_length)
        self.assertTrue(all("options" in question for question in session["questions"]))
        self.assertTrue(all("correct_index" not in question for question in session["questions"]))

    def test_posttest_is_locked_until_family_lesson_is_complete(self):
        self.quiz_service.start_session(self.student_id, "dp_policy_eval:pre")

        with self.assertRaisesRegex(ValueError, "Complete Policy Evaluation"):
            self.quiz_service.start_session(self.student_id, "dp_policy_eval:post")

        self.progress_service.record_lesson_completion(
            self.student_id,
            "dp_policy_eval",
        )
        session = self.quiz_service.start_session(self.student_id, "dp_policy_eval:post")

        self.assertEqual(session["phase"], "dp_policy_eval:post")
        self.assertEqual(session["stage"], "post")

    def test_pretest_and_posttest_scores_update_n_gain(self):
        pretest = self.quiz_service.start_session(self.student_id, "dp_policy_eval:pre")
        pretest_session = self.quiz_service._sessions[pretest["session_id"]]
        wrong_answers = []
        for question in pretest["questions"]:
            correct_index = pretest_session.correct_indices[question["id"]]
            wrong_answers.append(
                {
                    "question_id": question["id"],
                    "selected_index": (correct_index + 1) % len(question["options"]),
                }
            )

        pretest_result = self.quiz_service.submit_session(
            self.student_id,
            pretest["session_id"],
            wrong_answers,
        )
        self.assertEqual(pretest_result["percentage"], 0.0)
        self.assertIsNone(pretest_result["n_gain"])

        self.progress_service.record_lesson_completion(
            self.student_id,
            "dp_policy_eval",
        )
        posttest = self.quiz_service.start_session(self.student_id, "dp_policy_eval:post")
        posttest_session = self.quiz_service._sessions[posttest["session_id"]]
        correct_answers = []
        for question in posttest["questions"]:
            correct_answers.append(
                {
                    "question_id": question["id"],
                    "selected_index": posttest_session.correct_indices[question["id"]],
                }
            )

        posttest_result = self.quiz_service.submit_session(
            self.student_id,
            posttest["session_id"],
            correct_answers,
        )
        self.assertEqual(posttest_result["percentage"], 100.0)
        self.assertEqual(posttest_result["n_gain"], 1.0)
        family_score = posttest_result["progress"]["family_quiz_scores"]["dp_policy_eval"]
        self.assertEqual(family_score["pretest_score"], 0.0)
        self.assertEqual(family_score["posttest_score"], 100.0)
        self.assertEqual(family_score["attempts"], {"pretest": 1, "posttest": 1})

    def test_second_quiz_prefers_unused_questions(self):
        first_session = self.quiz_service.start_session(self.student_id, "dp_policy_eval:pre")
        first_question_ids = {question["id"] for question in first_session["questions"]}
        first_session_state = self.quiz_service._sessions[first_session["session_id"]]

        answers = [
            {
                "question_id": question["id"],
                "selected_index": first_session_state.correct_indices[question["id"]],
            }
            for question in first_session["questions"]
        ]
        self.quiz_service.submit_session(
            self.student_id,
            first_session["session_id"],
            answers,
        )

        second_session = self.quiz_service.start_session(self.student_id, "dp_policy_eval:pre")
        second_question_ids = {question["id"] for question in second_session["questions"]}

        self.assertTrue(first_question_ids.isdisjoint(second_question_ids))

    def test_family_quiz_uses_catalog_membership(self):
        session = self.quiz_service.start_session(self.student_id, "td_sarsa:pre")

        self.assertEqual(session["phase"], "td_sarsa:pre")
        self.assertEqual(session["family_id"], "td_sarsa")
        self.assertGreater(len(session["questions"]), 0)
        self.assertTrue(
            all(
                question["id"].startswith("td_sarsa_")
                for question in session["questions"]
            )
        )

    def test_database_seed_removes_stale_system_questions(self):
        database = Database("sqlite://")
        database.create_schema()
        with database.session() as session:
            session.add(
                QuizQuestion(
                    id="q_bellman_backup",
                    concept="Dynamic Programming",
                    prompt="Old hardcoded Bellman backup question.",
                    options_json='["A", "B"]',
                    correct_index=0,
                    created_by_user_id="system",
                )
            )
            session.commit()

        quiz_service = QuizService(self.progress_service, database=database)
        session = quiz_service.start_session(self.student_id, "dp_policy_eval:pre")
        question_ids = {question["id"] for question in session["questions"]}

        self.assertNotIn("q_bellman_backup", question_ids)

    def test_catalog_validation_rejects_bad_family_metadata(self):
        cases = [
            (
                "unknown lesson_ids",
                lambda payload: payload["families"][0].update(
                    {"lesson_ids": ["missing_lesson"]}
                ),
            ),
            (
                "Duplicate quiz question id",
                lambda payload: payload["questions"].__setitem__(
                    1,
                    {**payload["questions"][1], "id": payload["questions"][0]["id"]},
                ),
            ),
            (
                "invalid stage",
                lambda payload: payload["questions"][0].update({"stage": "review"}),
            ),
            (
                "invalid correct_index",
                lambda payload: payload["questions"][0].update({"correct_index": 99}),
            ),
            (
                "needs at least",
                lambda payload: payload.update({"questions": payload["questions"][:2]}),
            ),
        ]

        for message, mutate in cases:
            with self.subTest(message=message):
                payload = _minimal_catalog_payload()
                mutate(payload)
                with tempfile.NamedTemporaryFile(
                    mode="w",
                    suffix=".json",
                    encoding="utf-8",
                    delete=False,
                ) as handle:
                    json.dump(payload, handle)
                    path = Path(handle.name)
                try:
                    with self.assertRaisesRegex(ValueError, message):
                        load_quiz_catalog(path)
                finally:
                    path.unlink(missing_ok=True)

def _minimal_catalog_payload() -> dict:
    questions = [
        {
            "id": f"dp_policy_eval_validation_{index}",
            "family_id": "dp_policy_eval",
            "stage": "both",
            "concept": "Validation",
            "prompt": f"Validation question {index}?",
            "options": ["Correct", "Incorrect"],
            "correct_index": 0,
        }
        for index in range(10)
    ]
    return {
        "default_quiz_length": 6,
        "minimum_family_stage_questions": 10,
        "families": [
            {
                "id": "dp_policy_eval",
                "label": "Policy Evaluation",
                "description": "Validation family.",
                "lesson_ids": ["dp_policy_eval"],
                "pretest": {"label": "Pre"},
                "posttest": {"label": "Post"},
            }
        ],
        "questions": questions,
    }


if __name__ == "__main__":
    unittest.main()
