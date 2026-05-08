import unittest

from backend.services.quiz_service import QuizService


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
    ) -> dict | None:
        dashboard = self._dashboards.get(student_id)
        if dashboard is None:
            return None
        progress = dashboard["progress"]
        progress["quiz_attempts"][phase] += 1
        progress[f"{phase}_score"] = percentage
        if phase == "posttest":
            pretest_score = progress.get("pretest_score")
            progress["n_gain"] = (
                None
                if pretest_score is None
                else (
                    round((percentage - pretest_score) / (100 - pretest_score), 3)
                    if pretest_score < 100
                    else 1.0
                )
            )
        self._question_history.setdefault(student_id, []).extend(question_ids)
        return dashboard

    def get_question_history(self, student_id: str) -> list[str]:
        return list(self._question_history.get(student_id, []))


class QuizServiceTest(unittest.TestCase):
    def setUp(self):
        self.progress_service = _FakeProgressService()
        self.quiz_service = QuizService(self.progress_service)
        self.dashboard = self.progress_service.sign_in(
            "Maya Hassan",
            "SecurePass123!",
        )
        self.student_id = self.dashboard["student"]["id"]

    def test_start_session_returns_randomized_questions_without_answer_key(self):
        session = self.quiz_service.start_session(self.student_id, "pretest")

        self.assertEqual(session["phase"], "pretest")
        self.assertEqual(session["question_count"], self.quiz_service.quiz_length)
        self.assertEqual(len(session["questions"]), self.quiz_service.quiz_length)
        self.assertTrue(all("options" in question for question in session["questions"]))
        self.assertTrue(all("correct_index" not in question for question in session["questions"]))

    def test_pretest_and_posttest_scores_update_n_gain(self):
        pretest = self.quiz_service.start_session(self.student_id, "pretest")
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

        posttest = self.quiz_service.start_session(self.student_id, "posttest")
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

    def test_second_quiz_prefers_unused_questions(self):
        first_session = self.quiz_service.start_session(self.student_id, "pretest")
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

        second_session = self.quiz_service.start_session(self.student_id, "posttest")
        second_question_ids = {question["id"] for question in second_session["questions"]}

        self.assertTrue(first_question_ids.isdisjoint(second_question_ids))


if __name__ == "__main__":
    unittest.main()
