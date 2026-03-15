import unittest

from backend.validation.validator import CodeValidator


class CodeValidatorTest(unittest.TestCase):
    def setUp(self):
        self.validator = CodeValidator()

    def test_rejects_unknown_lessons(self):
        result = self.validator.validate_code("def anything():\n    pass\n", "unknown")

        self.assertFalse(result.is_valid)
        self.assertIn("Unknown lesson_id", result.errors[0])

    def test_rejects_missing_required_function(self):
        result = self.validator.validate_code(
            "def helper():\n    return 1\n",
            "td_q_learning",
        )

        self.assertFalse(result.is_valid)
        self.assertIn("q_learning_update", result.errors[0])

    def test_accepts_matching_lesson_function(self):
        result = self.validator.validate_code(
            (
                "def q_learning_update(Q, state, action, reward, next_state, alpha, gamma):\n"
                "    best_next_value = max(Q[next_state])\n"
                "    td_target = reward + gamma * best_next_value\n"
                "    Q[state][action] = Q[state][action] + alpha * (td_target - Q[state][action])\n"
                "    return Q\n"
            ),
            "td_q_learning",
        )

        self.assertTrue(result.is_valid)
        self.assertEqual(result.errors, [])
        self.assertTrue(all(test["passed"] for test in result.test_results))

    def test_rejects_forbidden_imports(self):
        result = self.validator.validate_code(
            "import os\n\ndef q_learning_update(*args):\n    return []\n",
            "td_q_learning",
        )

        self.assertFalse(result.is_valid)
        self.assertIn("Import", result.errors[0])


if __name__ == "__main__":
    unittest.main()
