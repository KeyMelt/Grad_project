from __future__ import annotations

from datetime import datetime
from typing import Any

from pydantic import BaseModel, Field


class CodeSubmission(BaseModel):
    lesson_id: str
    code: str
    learning_rate: float | None = Field(default=None, gt=0, le=1)
    discount_factor: float | None = Field(default=None, gt=0, le=1)
    exploration_rate: float | None = Field(default=None, ge=0, le=1)
    episode_count: int | None = Field(default=None, ge=1, le=500)
    session_id: str | None = None


class StudentSignInRequest(BaseModel):
    display_name: str = Field(default="", max_length=80)
    password: str = Field(default="", max_length=128)
    firebase_id_token: str | None = None


class ProfileUpdateRequest(BaseModel):
    display_name: str = Field(min_length=1, max_length=80)
    rl_experience: str = Field(min_length=1, max_length=50)


class QuizStartRequest(BaseModel):
    phase: str


class QuizAnswer(BaseModel):
    question_id: str
    selected_index: int = Field(ge=0)


class QuizSubmissionRequest(BaseModel):
    session_id: str
    answers: list[QuizAnswer]


class WorkspaceSessionCreateRequest(BaseModel):
    lesson_id: str


class WorkspaceFileUpdateRequest(BaseModel):
    content: str


class TelemetryEventRequest(BaseModel):
    lesson_id: str = Field(min_length=1)
    concept_id: str | None = None
    session_id: str = Field(min_length=1)
    event_type: str = Field(min_length=1)
    occurred_at_utc: datetime
    payload_json: dict[str, Any] = Field(default_factory=dict)
    source_version: str = Field(default="study_buddy_v1", min_length=1)


class TelemetryBatchRequest(BaseModel):
    events: list[TelemetryEventRequest] = Field(min_length=1, max_length=200)


class StudyBuddyInterventionResponseRequest(BaseModel):
    response: str = Field(default="completed")
    response_payload: dict[str, Any] = Field(default_factory=dict)


class StudyBuddyChatMessageRequest(BaseModel):
    role: str = Field(pattern="^(user|assistant)$")
    content: str = Field(min_length=1, max_length=4000)


class StudyBuddyChatRequest(BaseModel):
    lesson_id: str = Field(min_length=1)
    session_id: str = Field(min_length=1)
    message: str = Field(min_length=1, max_length=4000)
    current_code: str | None = Field(default=None, max_length=20000)
    unresolved_blanks: list[str] = Field(default_factory=list, max_length=20)
    failure_kind: str | None = Field(default=None, max_length=100)
    latest_feedback: dict[str, Any] = Field(default_factory=dict)
    history: list[StudyBuddyChatMessageRequest] = Field(
        default_factory=list,
        max_length=12,
    )


class AuthRoleUpdateRequest(BaseModel):
    role: str = Field(min_length=1)


class AuthStatusUpdateRequest(BaseModel):
    status: str = Field(min_length=1)
