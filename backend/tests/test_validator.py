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

    def test_accepts_value_iteration_function(self):
        result = self.validator.validate_code(
            (
                "def value_iteration(V, env, gamma=0.9, theta=1e-8):\n"
                "    delta = float('inf')\n"
                "    action_count = env.action_space.n\n"
                "    while delta > theta:\n"
                "        delta = 0.0\n"
                "        for state in range(len(V)):\n"
                "            old_value = V[state]\n"
                "            action_values = []\n"
                "            for action in range(action_count):\n"
                "                action_value = 0.0\n"
                "                for transition_prob, next_state, reward, done in env.P[state][action]:\n"
                "                    future = 0.0 if done else V[next_state]\n"
                "                    action_value += transition_prob * (reward + gamma * future)\n"
                "                action_values.append(action_value)\n"
                "            V[state] = max(action_values)\n"
                "            delta = max(delta, abs(old_value - V[state]))\n"
                "    return V\n"
            ),
            "dp_value_iteration",
        )

        self.assertTrue(result.is_valid)
        self.assertEqual(result.errors, [])
        self.assertTrue(all(test["passed"] for test in result.test_results))


if __name__ == "__main__":
    unittest.main()
