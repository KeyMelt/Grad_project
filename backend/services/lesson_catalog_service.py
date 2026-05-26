from typing import Optional

from backend.lessons import (
    LessonDefinition,
    get_lesson_definition,
    list_lesson_definitions,
    serialize_lesson,
)
from backend.concept_videos.specs import LESSON_VIDEO_SPECS

LESSON_SECTION_ORDER = (
    "Dynamic Programming",
    "Monte Carlo Methods",
    "Temporal Difference",
)

CONCEPT_VIDEO_ROUTE_PREFIX = "/media/concept-videos"

PRESENTATION_METADATA: dict[str, dict] = {
    "dp_policy_eval": {
        "title": "Policy Evaluation",
        "concept_video": {
            "stream_path": "/media/concept-videos/dp_policy_eval_concept.mp4",
            "duration_label": "03:30",
            "summary": "A Bellman expectation sweep over FrozenLake, showing how policy probabilities, transition branches, rewards, and discounted future values combine into each state update.",
            "highlights": [
                "How a fixed policy weights each action.",
                "How transition probabilities and discounted future values combine.",
                "Why repeated sweeps converge to stable state values.",
            ],
        },
        "exercise": {
            "title": "Implement iterative policy evaluation",
            "overview": "Complete the Bellman expectation update so each state value is replaced by the expected return under the supplied policy.",
            "tasks": [
                "Fill the expectation TODO block so it accumulates every policy-weighted transition branch.",
                "Replace the convergence placeholder with the updated state-value comparison.",
                "Keep the discounted future value at zero for terminal transitions.",
            ],
            "code_tip": "Set lesson configuration inside the code itself. For this lesson, the main editable constant is DISCOUNT_FACTOR.",
        },
    },
    "dp_value_iteration": {
        "title": "Value Iteration",
        "concept_video": {
            "stream_path": "/media/concept-videos/dp_value_iteration_concept.mp4",
            "duration_label": "03:20",
            "summary": "A FrozenLake optimality backup walkthrough that compares action values and keeps the greedy value for each state.",
            "highlights": [
                "How the environment branches for each action.",
                "Why value iteration keeps the maximum action backup.",
                "How repeated sweeps produce an optimal value table.",
            ],
        },
        "exercise": {
            "title": "Implement Bellman optimality backups",
            "overview": "Update each state by computing every action backup and keeping the maximum action value.",
            "tasks": [
                "Fill the action-backup TODO block for one action at a time.",
                "Replace the best-action placeholder with the maximum over computed action values.",
                "Preserve the convergence check across sweeps.",
            ],
            "code_tip": "Tune DISCOUNT_FACTOR in code if you want to inspect different planning behavior.",
        },
    },
    "dp_policy_improvement": {
        "title": "Policy Improvement",
        "concept_video": {
            "stream_path": "/media/concept-videos/dp_policy_improvement_concept.mp4",
            "duration_label": "03:10",
            "summary": "A greedy policy-improvement pass that converts state values into a one-hot action policy.",
            "highlights": [
                "How one-step lookahead scores each action.",
                "How the argmax action becomes the improved policy.",
                "Why policy rows remain one-hot after improvement.",
            ],
        },
        "exercise": {
            "title": "Implement greedy policy improvement",
            "overview": "Compute each action score from the value table and select the greedy action for every state.",
            "tasks": [
                "Fill the one-step lookahead TODO block.",
                "Replace the best-action placeholder with the greedy action index.",
                "Keep each returned policy row one-hot.",
            ],
            "code_tip": "Use DISCOUNT_FACTOR in code to keep the action lookahead aligned with the lesson configuration.",
        },
    },
    "mc_first_visit": {
        "title": "First-Visit Monte Carlo",
        "concept_video": {
            "stream_path": "/media/concept-videos/mc_first_visit_concept.mp4",
            "duration_label": "03:45",
            "summary": "A Blackjack episode trace showing how first-visit Monte Carlo prediction estimates values from complete sampled returns.",
            "highlights": [
                "Why repeated states are skipped after the first visit.",
                "How discounted returns are accumulated from an episode.",
                "How repeated returns average into a value estimate.",
            ],
        },
        "exercise": {
            "title": "Implement first-visit return updates",
            "overview": "Skip repeated states, compute the discounted return from the first visit, and update the running value estimate.",
            "tasks": [
                "Replace the first-visit condition placeholder.",
                "Fill the return-accumulation TODO block.",
                "Append the return and average all returns for the state.",
            ],
            "code_tip": "EPISODE_COUNT and DISCOUNT_FACTOR are defined in the submitted code so experiments stay visible.",
        },
    },
    "td_sarsa": {
        "title": "SARSA",
        "concept_video": {
            "stream_path": "/media/concept-videos/td_sarsa_concept.mp4",
            "duration_label": "03:35",
            "summary": "An on-policy CliffWalking update showing how SARSA bootstraps from the next sampled action.",
            "highlights": [
                "How SARSA uses the action actually selected by the behavior policy.",
                "How terminal transitions remove the bootstrap term.",
                "How the Q-table changes after a single TD update.",
            ],
        },
        "exercise": {
            "title": "Implement the SARSA update rule",
            "overview": "Complete the on-policy TD update that uses the sampled next action rather than a greedy maximum.",
            "tasks": [
                "Replace the bootstrap placeholder with the sampled next-action value.",
                "Fill the TODO block that performs the incremental SARSA update.",
                "Keep terminal transitions from bootstrapping future value.",
            ],
            "code_tip": "LEARNING_RATE, DISCOUNT_FACTOR, EXPLORATION_RATE, and EPISODE_COUNT are read from the submitted code.",
        },
    },
    "td_q_learning": {
        "title": "Q-Learning",
        "concept_video": {
            "stream_path": "/media/concept-videos/td_q_learning_concept.mp4",
            "duration_label": "03:25",
            "summary": "An off-policy CliffWalking update showing how Q-learning bootstraps from the greedy next-state action value.",
            "highlights": [
                "How Q-learning uses a max over next-state action values.",
                "How the TD target combines reward and discounted bootstrap.",
                "How the selected Q-value moves toward the target.",
            ],
        },
        "exercise": {
            "title": "Implement the Q-learning update rule",
            "overview": "Complete the one-step TD update that adjusts a single Q-value from a sampled transition.",
            "tasks": [
                "Replace the bootstrap placeholder with the greedy next-state value.",
                "Fill the TODO block that performs the incremental TD update.",
                "Keep the TD target expression that combines reward and discounted bootstrap.",
            ],
            "code_tip": "LEARNING_RATE, DISCOUNT_FACTOR, EXPLORATION_RATE, and EPISODE_COUNT are read from the submitted code.",
        },
    },
}


def _serialize_lesson_for_client(lesson: LessonDefinition) -> dict:
    lesson_data = serialize_lesson(lesson)
    presentation = PRESENTATION_METADATA.get(lesson.id, {})
    video_spec = LESSON_VIDEO_SPECS.get(lesson.id)
    exercise = dict(presentation.get("exercise", {}))
    exercise["template_blanks"] = lesson_data["template_blanks"]
    exercise["success_criteria"] = lesson_data["success_criteria"]
    concept_video = dict(
        presentation.get(
            "concept_video",
            {
                "stream_path": "",
                "duration_label": "",
                "summary": "",
                "highlights": [],
            },
        )
    )
    concept_video = _with_backend_video_path(concept_video, lesson.id)
    if video_spec is not None:
        concept_video.update(
            {
                "theory_equation": video_spec.theory_equation,
                "worked_example": video_spec.worked_example,
                "misconception_to_prevent": video_spec.misconception_to_prevent,
                "takeaway_line": video_spec.takeaway_line,
                "theory_verification": [
                    {
                        "claim": verification.claim,
                        "source_url": verification.source_url,
                        "validation_note": verification.validation_note,
                        "is_inference": verification.is_inference,
                    }
                    for verification in video_spec.theory_verification
                ],
            }
        )
    return {
        **lesson_data,
        "title": presentation.get("title", lesson.title),
        "backend_enabled": True,
        "concept_video": concept_video,
        "exercise": exercise,
    }


def _with_backend_video_path(concept_video: dict, lesson_id: str) -> dict:
    """Normalize concept-video metadata to the backend-served media route."""
    updated = dict(concept_video)
    filename = _concept_video_filename(updated, lesson_id)
    updated["stream_path"] = f"{CONCEPT_VIDEO_ROUTE_PREFIX}/{filename}"
    updated["caption_path"] = f"{CONCEPT_VIDEO_ROUTE_PREFIX}/{lesson_id}_captions.vtt"
    return updated


def _concept_video_filename(concept_video: dict, lesson_id: str) -> str:
    stream_path = str(concept_video.get("stream_path") or "")
    if stream_path:
        return stream_path.rstrip("/").rsplit("/", maxsplit=1)[-1]
    return f"{lesson_id}_concept.mp4"


class LessonCatalogService:
    """Service boundary for lesson metadata and starter templates."""

    def list_lessons(self) -> list[dict]:
        return [_serialize_lesson_for_client(lesson) for lesson in list_lesson_definitions()]

    def list_lesson_sections(self) -> list[dict]:
        lessons_by_category: dict[str, list[dict]] = {
            category: [] for category in LESSON_SECTION_ORDER
        }
        for lesson in self.list_lessons():
            lessons_by_category.setdefault(lesson["category"], []).append(lesson)
        return [
            {"title": category, "lessons": lessons}
            for category, lessons in lessons_by_category.items()
            if lessons
        ]

    def get_lesson(self, lesson_id: str) -> Optional[dict]:
        lesson = get_lesson_definition(lesson_id)
        return None if lesson is None else _serialize_lesson_for_client(lesson)
