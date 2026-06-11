from __future__ import annotations

# Learning lifecycle
PRE_TEST_START = "pre_test_start"
PRE_TEST_COMPLETE = "pre_test_complete"
LESSON_START = "lesson_start"
LESSON_COMPLETE = "lesson_complete"
POST_TEST_START = "post_test_start"
POST_TEST_COMPLETE = "post_test_complete"
SURVEY_COMPLETE = "survey_complete"

# Code workspace
CODE_SUBMIT_FAILURE = "code_submit_failure"
CODE_SUBMIT_SUCCESS = "code_submit_success"

# Study Buddy interactions
HINT_SHOWN = "hint_shown"
HINT_REQUEST = "hint_request"
RECOMMENDATION_SHOWN = "recommendation_shown"
RECOMMENDATION_CLICK = "recommendation_click"
RECOMMENDATION_COMPLETE = "recommendation_complete"

# Prediction probe
PROBE_SHOWN = "probe_shown"
PROBE_SUBMITTED = "probe_submitted"

# Concept checks
CONCEPT_CHECK_ATTEMPT = "concept_check_attempt"
CONCEPT_CHECK_CORRECT = "concept_check_correct"
CONCEPT_CHECK_WRONG = "concept_check_wrong"

# Component micro-surveys
VIDEO_MICRO_SURVEY_SUBMITTED = "video_micro_survey_submitted"
REPLAY_MICRO_SURVEY_SUBMITTED = "replay_micro_survey_submitted"

ALL_EVENT_TYPES: frozenset[str] = frozenset({
    PRE_TEST_START,
    PRE_TEST_COMPLETE,
    LESSON_START,
    LESSON_COMPLETE,
    POST_TEST_START,
    POST_TEST_COMPLETE,
    SURVEY_COMPLETE,
    CODE_SUBMIT_FAILURE,
    CODE_SUBMIT_SUCCESS,
    HINT_SHOWN,
    HINT_REQUEST,
    RECOMMENDATION_SHOWN,
    RECOMMENDATION_CLICK,
    RECOMMENDATION_COMPLETE,
    PROBE_SHOWN,
    PROBE_SUBMITTED,
    CONCEPT_CHECK_ATTEMPT,
    CONCEPT_CHECK_CORRECT,
    CONCEPT_CHECK_WRONG,
    VIDEO_MICRO_SURVEY_SUBMITTED,
    REPLAY_MICRO_SURVEY_SUBMITTED,
})
