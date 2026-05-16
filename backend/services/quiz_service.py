from dataclasses import dataclass
from random import SystemRandom
from uuid import uuid4

from backend.services.student_progress_service import StudentProgressService


@dataclass(frozen=True)
class QuizQuestionTemplate:
    id: str
    concept: str
    prompt: str
    options: tuple[str, ...]
    correct_index: int


@dataclass
class QuizSession:
    session_id: str
    student_id: str
    phase: str
    question_ids: list[str]
    correct_indices: dict[str, int]
    questions: list[dict]


QUESTION_BANK: tuple[QuizQuestionTemplate, ...] = (
    QuizQuestionTemplate(
        id="q_bellman_expectation",
        concept="Dynamic Programming",
        prompt="What does policy evaluation repeatedly update for each state?",
        options=(
            "The expected return under the current policy",
            "The number of available actions",
            "The exploration rate schedule",
            "The animation playback speed",
        ),
        correct_index=0,
    ),
    QuizQuestionTemplate(
        id="q_value_iteration",
        concept="Dynamic Programming",
        prompt="Which operation makes value iteration different from policy evaluation?",
        options=(
            "Taking the maximum over action values",
            "Averaging rewards across every episode",
            "Sampling only the first state in an episode",
            "Replacing gamma with alpha",
        ),
        correct_index=0,
    ),
    QuizQuestionTemplate(
        id="q_policy_improvement",
        concept="Dynamic Programming",
        prompt="What does policy improvement do after state values have been estimated?",
        options=(
            "It chooses the greedy action for each state using the current value table",
            "It averages returns over complete episodes",
            "It replaces the value table with transition probabilities",
            "It resets every Q-value to zero before the next episode",
        ),
        correct_index=0,
    ),
    QuizQuestionTemplate(
        id="q_transition_probability",
        concept="Environment Model",
        prompt="What does a transition probability describe in FrozenLake?",
        options=(
            "How likely the environment is to move to a next state after an action",
            "How many times a state has been visited",
            "The reward assigned to every terminal state",
            "The number of frames rendered per episode",
        ),
        correct_index=0,
    ),
    QuizQuestionTemplate(
        id="q_mc_update_timing",
        concept="Monte Carlo Methods",
        prompt="When does first-visit Monte Carlo prediction update a state's value?",
        options=(
            "After the episode is complete and the first visit return is known",
            "Immediately after every action",
            "Only when the agent reaches the start state again",
            "Before the environment is reset",
        ),
        correct_index=0,
    ),
    QuizQuestionTemplate(
        id="q_mc_first_visit",
        concept="Monte Carlo Methods",
        prompt="Why does first-visit Monte Carlo ignore repeated visits to the same state in one episode?",
        options=(
            "It only keeps the return from the first occurrence of that state",
            "It assumes repeated states are impossible",
            "It wants to maximize the exploration rate",
            "It replaces returns with transition probabilities",
        ),
        correct_index=0,
    ),
    QuizQuestionTemplate(
        id="q_td_target",
        concept="Temporal Difference",
        prompt="What is the TD target used by Q-learning?",
        options=(
            "Reward plus discounted best next-state action value",
            "Reward plus the current state's maximum value",
            "Average episode reward minus epsilon",
            "Discount factor times the previous action probability",
        ),
        correct_index=0,
    ),
    QuizQuestionTemplate(
        id="q_epsilon_greedy",
        concept="Temporal Difference",
        prompt="What is the role of epsilon in epsilon-greedy action selection?",
        options=(
            "It controls how often the agent explores instead of exploiting",
            "It controls the Bellman residual threshold",
            "It scales the animation frame size",
            "It replaces the reward function",
        ),
        correct_index=0,
    ),
    QuizQuestionTemplate(
        id="q_discount_factor",
        concept="Core RL",
        prompt="What does the discount factor gamma primarily control?",
        options=(
            "How much future rewards influence the current estimate",
            "How many episodes are stored in memory",
            "How often the policy is rendered",
            "How many actions the environment exposes",
        ),
        correct_index=0,
    ),
    QuizQuestionTemplate(
        id="q_value_function",
        concept="Core RL",
        prompt="What does a state-value function estimate?",
        options=(
            "The expected long-term return from a state",
            "The immediate reward of the previous action only",
            "The probability that the episode will never end",
            "The number of code lines executed in the update step",
        ),
        correct_index=0,
    ),
    QuizQuestionTemplate(
        id="q_q_learning_off_policy",
        concept="Temporal Difference",
        prompt="Why is Q-learning considered off-policy?",
        options=(
            "It learns from the greedy target even when behavior includes exploration",
            "It requires complete episodes before every update",
            "It evaluates only a fixed stochastic policy",
            "It cannot be used with discrete state spaces",
        ),
        correct_index=0,
    ),
    QuizQuestionTemplate(
        id="q_sarsa_on_policy",
        concept="Temporal Difference",
        prompt="Why is SARSA considered on-policy?",
        options=(
            "Its TD target uses the next action that the behavior policy actually sampled",
            "It waits for the end of the episode before every update",
            "It computes a maximum over all next-state actions",
            "It ignores the discount factor during bootstrapping",
        ),
        correct_index=0,
    ),
    QuizQuestionTemplate(
        id="q_bellman_backup",
        concept="Dynamic Programming",
        prompt="What is a Bellman backup doing conceptually?",
        options=(
            "Recomputing a value estimate from rewards and successor states",
            "Saving model checkpoints to disk",
            "Resetting the environment to the initial state",
            "Copying the previous episode trace into the next one",
        ),
        correct_index=0,
    ),
    QuizQuestionTemplate(
        id="q_terminal_state",
        concept="Environment Model",
        prompt="How is a terminal state typically handled in value updates?",
        options=(
            "Its future value contribution is treated as zero",
            "Its reward is ignored completely",
            "Its transition probabilities are set equal to epsilon",
            "Its action space doubles in size",
        ),
        correct_index=0,
    ),
)


class QuizService:
    """Creates randomized pre-test and post-test quiz sessions in memory."""

    quiz_length = 6

    def __init__(self, progress_service: StudentProgressService) -> None:
        self._progress_service = progress_service
        self._rng = SystemRandom()
        self._sessions: dict[str, QuizSession] = {}

    def start_session(self, student_id: str, phase: str) -> dict:
        if self._progress_service.get_dashboard(student_id) is None:
            raise ValueError("Unknown student_id.")
        if phase not in {"pretest", "posttest"}:
            raise ValueError(f"Unsupported quiz phase '{phase}'.")

        question_templates = self._select_questions(student_id)
        questions: list[dict] = []
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
            "question_count": len(questions),
            "questions": questions,
        }

    def submit_session(
        self,
        student_id: str,
        session_id: str,
        answers: list[dict],
    ) -> dict:
        session = self._sessions.get(session_id)
        if session is None:
            raise ValueError("Unknown quiz session.")
        if session.student_id != student_id:
            raise ValueError("Quiz session does not belong to this student.")

        answer_map = {answer["question_id"]: answer["selected_index"] for answer in answers}
        score = 0
        concept_results: list[dict] = []
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
        percentage = round((score / total_questions) * 100, 2)
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
            "score": score,
            "total_questions": total_questions,
            "percentage": percentage,
            "n_gain": dashboard["progress"]["n_gain"],
            "progress": dashboard["progress"],
            "concept_results": concept_results,
        }

    def _select_questions(self, student_id: str) -> list[QuizQuestionTemplate]:
        used_question_ids = set(self._progress_service.get_question_history(student_id))
        unused_templates = [
            question for question in QUESTION_BANK if question.id not in used_question_ids
        ]
        used_templates = [
            question for question in QUESTION_BANK if question.id in used_question_ids
        ]

        if len(unused_templates) >= self.quiz_length:
            selected = self._rng.sample(unused_templates, self.quiz_length)
        else:
            selected = list(unused_templates)
            remaining_count = self.quiz_length - len(selected)
            if remaining_count > 0:
                selected.extend(self._rng.sample(used_templates, remaining_count))

        self._rng.shuffle(selected)
        return selected
