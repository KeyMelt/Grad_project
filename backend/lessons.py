from dataclasses import dataclass
from typing import Optional


@dataclass(frozen=True)
class LessonDefinition:
    id: str
    title: str
    required_function: str
    environment_name: str


LESSON_DEFINITIONS = {
    "dp_policy_eval": LessonDefinition(
        id="dp_policy_eval",
        title="Dynamic Programming: Policy Evaluation",
        required_function="policy_evaluation",
        environment_name="FrozenLake",
    ),
    "mc_first_visit": LessonDefinition(
        id="mc_first_visit",
        title="Monte Carlo: First-Visit Prediction",
        required_function="mc_first_visit_prediction",
        environment_name="FrozenLake",
    ),
    "td_q_learning": LessonDefinition(
        id="td_q_learning",
        title="Temporal Difference: Q-Learning",
        required_function="q_learning_update",
        environment_name="FrozenLake",
    ),
}


def get_lesson_definition(lesson_id: str) -> Optional[LessonDefinition]:
    return LESSON_DEFINITIONS.get(lesson_id)
