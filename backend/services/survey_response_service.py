from __future__ import annotations

from threading import Lock
from typing import Any

from sqlmodel import select

from backend.models.survey_response import SurveyItemResponse, SurveyResponse
from backend.models.survey_template import SurveyTemplate, SurveyTemplateItem
from backend.persistence import Database


class SurveyResponseService:
    """Handles student submission and retrieval of generic survey responses."""

    def __init__(self, *, database: Database) -> None:
        self._lock = Lock()
        self._database = database
        self._database.create_schema()

    def submit(
        self,
        *,
        student_id: str,
        study_session_id: str,
        condition: str,
        template_id: str,
        responses: list[dict[str, Any]],
    ) -> SurveyResponse:
        """Persist a response to a survey template.

        ``responses`` is a list of dicts, each with:
          - ``item_id`` (str, required)
          - ``likert_value`` (int | None)
          - ``text_value`` (str | None)

        Raises ValueError if:
          - the template does not exist or is inactive
          - a required item has no answer
          - a likert_value is outside [1, 5]
        """
        with self._lock:
            with self._database.session() as session:
                template = session.get(SurveyTemplate, template_id)
                if template is None:
                    raise ValueError(f"Survey template {template_id!r} not found.")
                if not template.is_active:
                    raise ValueError(f"Survey template {template_id!r} is not active.")

                items = session.exec(
                    select(SurveyTemplateItem).where(
                        SurveyTemplateItem.survey_template_id == template_id
                    )
                ).all()

                item_map = {item.id: item for item in items}
                response_map = {r["item_id"]: r for r in responses}

                # Validate required items are answered
                for item in items:
                    if item.required and item.id not in response_map:
                        raise ValueError(
                            f"Required item {item.id!r} ({item.question_text!r}) has no response."
                        )

                # Validate likert range
                for r in responses:
                    lv = r.get("likert_value")
                    if lv is not None:
                        if not isinstance(lv, int) or not (1 <= lv <= 5):
                            raise ValueError(
                                f"likert_value must be an integer in [1, 5], got {lv!r}."
                            )

                survey_response = SurveyResponse(
                    survey_template_id=template_id,
                    survey_version=template.version,
                    study_session_id=study_session_id,
                    student_id=student_id,
                    condition=condition,
                )
                session.add(survey_response)
                session.flush()

                for r in responses:
                    item_response = SurveyItemResponse(
                        survey_response_id=survey_response.id,
                        item_id=r["item_id"],
                        likert_value=r.get("likert_value"),
                        text_value=r.get("text_value"),
                    )
                    session.add(item_response)

                session.commit()
                session.refresh(survey_response)
                session.expunge(survey_response)
                return survey_response

    def list_by_session(self, study_session_id: str) -> list[SurveyResponse]:
        """Return all survey responses for a given study session."""
        with self._lock:
            with self._database.session() as session:
                records = session.exec(
                    select(SurveyResponse).where(
                        SurveyResponse.study_session_id == study_session_id
                    ).order_by(SurveyResponse.submitted_at_utc)
                ).all()
                for r in records:
                    session.expunge(r)
                return list(records)

    def list_by_template_and_condition(
        self,
        template_id: str,
        condition: str | None = None,
    ) -> list[SurveyResponse]:
        """Return survey responses for a template, optionally filtered by condition."""
        with self._lock:
            with self._database.session() as session:
                stmt = select(SurveyResponse).where(
                    SurveyResponse.survey_template_id == template_id
                )
                if condition is not None:
                    stmt = stmt.where(SurveyResponse.condition == condition)
                stmt = stmt.order_by(SurveyResponse.submitted_at_utc)
                records = session.exec(stmt).all()
                for r in records:
                    session.expunge(r)
                return list(records)

    def list_item_responses(
        self, survey_response_id: str
    ) -> list[SurveyItemResponse]:
        """Return item-level responses for a single survey response."""
        with self._lock:
            with self._database.session() as session:
                records = session.exec(
                    select(SurveyItemResponse).where(
                        SurveyItemResponse.survey_response_id == survey_response_id
                    )
                ).all()
                for r in records:
                    session.expunge(r)
                return list(records)

    def list_all_responses_with_items(self) -> list[tuple[SurveyResponse, list[SurveyItemResponse]]]:
        """Return every response with its item responses.  Used by the ALEI export."""
        with self._lock:
            with self._database.session() as session:
                responses = session.exec(
                    select(SurveyResponse).order_by(
                        SurveyResponse.condition,
                        SurveyResponse.student_id,
                        SurveyResponse.submitted_at_utc,
                    )
                ).all()
                result = []
                for resp in responses:
                    item_responses = session.exec(
                        select(SurveyItemResponse).where(
                            SurveyItemResponse.survey_response_id == resp.id
                        )
                    ).all()
                    item_list = list(item_responses)
                    for r in item_list:
                        session.expunge(r)
                    session.expunge(resp)
                    result.append((resp, item_list))
                return result
