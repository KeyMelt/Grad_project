from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from backend.models.survey_template import SurveyTemplate, SurveyTemplateItem

# Each entry: (name, context_trigger, description, items)
# Item tuple: (order_index, question_text, question_type, is_standardized, required)

SURVEY_SEEDS: list[tuple[str, str, str, list[tuple[int, str, str, bool, bool]]]] = [
    (
        "Post-session survey",
        "post_session",
        "End-of-session System Usability Scale (Brooke 1996) and Raw NASA-TLX workload assessment.",
        [
            (1,  "I think that I would like to use this system frequently.",                         "likert_5", True, True),
            (2,  "I found the system unnecessarily complex.",                                         "likert_5", True, True),
            (3,  "I thought the system was easy to use.",                                             "likert_5", True, True),
            (4,  "I think I would need the support of a technical person to use this system.",        "likert_5", True, True),
            (5,  "I found the various functions in this system were well integrated.",                "likert_5", True, True),
            (6,  "I thought there was too much inconsistency in this system.",                        "likert_5", True, True),
            (7,  "I would imagine that most people would learn to use this system very quickly.",     "likert_5", True, True),
            (8,  "I found the system very cumbersome to use.",                                        "likert_5", True, True),
            (9,  "I felt very confident using the system.",                                           "likert_5", True, True),
            (10, "I needed to learn a lot of things before I could get going with this system.",      "likert_5", True, True),
            (11, "Mental Demand: How much mental and perceptual activity was required?",              "likert_5", True, True),
            (12, "Physical Demand: How much physical activity was required?",                         "likert_5", True, True),
            (13, "Temporal Demand: How much time pressure did you feel?",                             "likert_5", True, True),
            (14, "Performance: How successful were you in accomplishing what you were asked to do?",  "likert_5", True, True),
            (15, "Effort: How hard did you have to work to accomplish your level of performance?",    "likert_5", True, True),
            (16, "Frustration: How insecure, discouraged, irritated, stressed, and annoyed were you?","likert_5", True, True),
            (17, "What helped you most during this session?",                                         "text",     False, False),
            (18, "What was confusing or unclear?",                                                    "text",     False, False),
            (19, "What should be improved?",                                                          "text",     False, False),
        ],
    ),
    (
        "Post-video micro-survey",
        "post_video",
        "Two-item survey shown immediately after the concept video completes.",
        [
            (1, "The concept video made the algorithm clearer to me.",                    "likert_5", False, True),
            (2, "I would recommend this video to a peer learning this topic.",            "likert_5", False, True),
            (3, "Any comments about this video? (optional)",                              "text",     False, False),
        ],
    ),
    (
        "Post-replay micro-survey",
        "post_replay",
        "Two-item survey shown when the student reaches the last step of the trace replay.",
        [
            (1, "Stepping through the trace helped me understand how the algorithm updates values.", "likert_5", False, True),
            (2, "I would recommend the trace replay to a peer learning this topic.",                 "likert_5", False, True),
            (3, "Any comments about the trace replay? (optional)",                                   "text",     False, False),
        ],
    ),
]
