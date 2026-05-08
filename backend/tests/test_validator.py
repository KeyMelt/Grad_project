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
        self.assertEqual(result.failure_kind, "validation_error")

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
        self.assertEqual(result.unresolved_blanks, [])

    def test_rejects_forbidden_imports(self):
        result = self.validator.validate_code(
            "import os\n\ndef q_learning_update(*args):\n    return []\n",
            "td_q_learning",
        )

        self.assertFalse(result.is_valid)
        self.assertIn("Import", result.errors[0])
        self.assertEqual(result.failure_kind, "validation_error")

    def test_rejects_incomplete_guided_template_expression_blank(self):
        result = self.validator.validate_code(
            (
                "LEARNING_RATE = 0.1\n"
                "DISCOUNT_FACTOR = 0.95\n"
                "def q_learning_update(Q, state, action, reward, next_state, alpha=LEARNING_RATE, gamma=DISCOUNT_FACTOR):\n"
                "    best_next_value = __BLANK_q_learning_best_next__\n"
                "    td_target = reward + gamma * best_next_value\n"
                "    Q[state][action] = Q[state][action] + alpha * (td_target - Q[state][action])\n"
                "    return Q\n"
            ),
            "td_q_learning",
        )

        self.assertFalse(result.is_valid)
        self.assertEqual(result.failure_kind, "incomplete_template")
        self.assertEqual(result.unresolved_blanks, ["q_learning_best_next"])

    def test_rejects_incomplete_guided_template_block_blank(self):
        result = self.validator.validate_code(
            (
                "LEARNING_RATE = 0.1\n"
                "DISCOUNT_FACTOR = 0.95\n"
                "def q_learning_update(Q, state, action, reward, next_state, alpha=LEARNING_RATE, gamma=DISCOUNT_FACTOR):\n"
                "    best_next_value = max(Q[next_state])\n"
                "    td_target = reward + gamma * best_next_value\n"
                '    raise NotImplementedError("TODO: q_learning_update_rule")\n'
                "    return Q\n"
            ),
            "td_q_learning",
        )

        self.assertFalse(result.is_valid)
        self.assertEqual(result.failure_kind, "incomplete_template")
        self.assertEqual(result.unresolved_blanks, ["q_learning_update_rule"])

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

    def test_accepts_policy_improvement_function(self):
        result = self.validator.validate_code(
            (
                "def policy_improvement(V, env, gamma=0.9):\n"
                "    action_count = env.action_space.n\n"
                "    policy = [[0.0 for _ in range(action_count)] for _ in range(len(V))]\n"
                "    for state in range(len(V)):\n"
                "        action_values = []\n"
                "        for action in range(action_count):\n"
                "            action_value = 0.0\n"
                "            for transition_prob, next_state, reward, done in env.P[state][action]:\n"
                "                future = 0.0 if done else V[next_state]\n"
                "                action_value += transition_prob * (reward + gamma * future)\n"
                "            action_values.append(action_value)\n"
                "        best_action = max(range(action_count), key=lambda index: action_values[index])\n"
                "        policy[state][best_action] = 1.0\n"
                "    return policy\n"
            ),
            "dp_policy_improvement",
        )

        self.assertTrue(result.is_valid)
        self.assertEqual(result.errors, [])
        self.assertTrue(all(test["passed"] for test in result.test_results))

    def test_accepts_sarsa_function(self):
        result = self.validator.validate_code(
            (
                "def sarsa_update(Q, state, action, reward, next_state, next_action, alpha=0.1, gamma=0.9):\n"
                "    bootstrap = 0.0 if next_action is None else Q[next_state][next_action]\n"
                "    td_target = reward + gamma * bootstrap\n"
                "    Q[state][action] = Q[state][action] + alpha * (td_target - Q[state][action])\n"
                "    return Q\n"
            ),
            "td_sarsa",
        )

        self.assertTrue(result.is_valid)
        self.assertEqual(result.errors, [])
        self.assertTrue(all(test["passed"] for test in result.test_results))


if __name__ == "__main__":
    unittest.main()
