from __future__ import annotations

from pydantic import BaseModel, Field


class CodeSubmission(BaseModel):
    lesson_id: str
    code: str
    learning_rate: float | None = Field(default=None, gt=0, le=1)
    discount_factor: float | None = Field(default=None, gt=0, le=1)
    exploration_rate: float | None = Field(default=None, ge=0, le=1)
    episode_count: int | None = Field(default=None, ge=1, le=500)
    student_id: str | None = None


class WorkspaceSessionCreateRequest(BaseModel):
    lesson_id: str


class WorkspaceFileUpdateRequest(BaseModel):
    content: str
