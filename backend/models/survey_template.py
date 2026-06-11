from __future__ import annotations

from datetime import datetime, timezone
from typing import Optional
from uuid import uuid4

from sqlalchemy import Index
from sqlmodel import Field, SQLModel


class SurveyTemplate(SQLModel, table=True):
    __tablename__ = "survey_templates"
    __table_args__ = (
        Index(
            "ix_survey_templates_context_trigger_active",
            "context_trigger",
            "is_active",
        ),
    )

    id: str = Field(default_factory=lambda: uuid4().hex, primary_key=True)
    name: str
    context_trigger: str  # "post_session" | "post_video" | "post_replay"
    description: str = Field(default="")
    is_active: bool = Field(default=True)
    version: int = Field(default=1)
    created_at_utc: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc),
        nullable=False,
    )
    updated_at_utc: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc),
        nullable=False,
    )


class SurveyTemplateItem(SQLModel, table=True):
    __tablename__ = "survey_template_items"
    __table_args__ = (
        Index(
            "ix_survey_template_items_template_order",
            "survey_template_id",
            "order_index",
        ),
    )

    id: str = Field(default_factory=lambda: uuid4().hex, primary_key=True)
    survey_template_id: str = Field(index=True)
    order_index: int
    question_text: str
    question_type: str = Field(default="likert_5")  # "likert_5" | "text"
    is_standardized: bool = Field(default=False)
    required: bool = Field(default=True)
