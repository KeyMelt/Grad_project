from __future__ import annotations

from typing import Any, Optional

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, Field

from backend.auth.dependencies import build_current_principal_dependency, require_roles
from backend.auth.roles import PlatformRole, Principal


# ── Request / response schemas ────────────────────────────────────────────────

class UpdateTemplateRequest(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    is_active: Optional[bool] = None


class AddItemRequest(BaseModel):
    question_text: str = Field(min_length=1)
    question_type: str = Field(default="likert_5")
    order_index: int = Field(ge=0)
    required: bool = Field(default=True)


class UpdateItemRequest(BaseModel):
    question_text: Optional[str] = None
    order_index: Optional[int] = Field(default=None, ge=0)
    required: Optional[bool] = None


class ItemResponsePayload(BaseModel):
    item_id: str
    likert_value: Optional[int] = Field(default=None, ge=1, le=5)
    text_value: Optional[str] = None


class SubmitSurveyResponseRequest(BaseModel):
    study_session_id: str
    condition: str
    responses: list[ItemResponsePayload]


# ── Router factory ────────────────────────────────────────────────────────────

def build_surveys_router(services: Any) -> APIRouter:
    router = APIRouter()
    current_principal = build_current_principal_dependency(
        auth_service=services.auth,
        audit_service=getattr(services, "audit", None),
    )
    student_principal = require_roles(
        current_principal,
        PlatformRole.STUDENT,
        PlatformRole.INSTRUCTOR,
        PlatformRole.ADMIN,
    )
    admin_principal = require_roles(
        current_principal,
        PlatformRole.ADMIN,
    )

    # ── Admin: read ───────────────────────────────────────────────────────────

    @router.get("/admin/surveys", status_code=200)
    def list_surveys(
        principal: Principal = Depends(admin_principal),
    ):
        templates = services.survey_management.list_templates()
        result = []
        for t in templates:
            items = services.survey_management.get_items_for_template(t.id)
            result.append({
                "id": t.id,
                "name": t.name,
                "context_trigger": t.context_trigger,
                "description": t.description,
                "is_active": t.is_active,
                "version": t.version,
                "item_count": len(items),
                "updated_at_utc": t.updated_at_utc.isoformat(),
            })
        return result

    @router.get("/admin/surveys/{template_id}", status_code=200)
    def get_survey(
        template_id: str,
        principal: Principal = Depends(admin_principal),
    ):
        try:
            template, items = services.survey_management.get_template_with_items(template_id)
        except ValueError as exc:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc
        return {
            "id": template.id,
            "name": template.name,
            "context_trigger": template.context_trigger,
            "description": template.description,
            "is_active": template.is_active,
            "version": template.version,
            "updated_at_utc": template.updated_at_utc.isoformat(),
            "items": [
                {
                    "id": item.id,
                    "order_index": item.order_index,
                    "question_text": item.question_text,
                    "question_type": item.question_type,
                    "is_standardized": item.is_standardized,
                    "required": item.required,
                }
                for item in items
            ],
        }

    # ── Admin: write ──────────────────────────────────────────────────────────

    @router.patch("/admin/surveys/{template_id}", status_code=200)
    def update_survey(
        template_id: str,
        request: UpdateTemplateRequest,
        principal: Principal = Depends(admin_principal),
    ):
        try:
            template = services.survey_management.update_template(
                template_id,
                name=request.name,
                description=request.description,
                is_active=request.is_active,
            )
        except ValueError as exc:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc
        return {
            "id": template.id,
            "name": template.name,
            "is_active": template.is_active,
            "version": template.version,
            "updated_at_utc": template.updated_at_utc.isoformat(),
        }

    @router.post("/admin/surveys/{template_id}/items", status_code=201)
    def add_item(
        template_id: str,
        request: AddItemRequest,
        principal: Principal = Depends(admin_principal),
    ):
        try:
            item = services.survey_management.add_item(
                template_id,
                question_text=request.question_text,
                question_type=request.question_type,
                order_index=request.order_index,
                required=request.required,
            )
        except ValueError as exc:
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail=str(exc)
            ) from exc
        return {
            "id": item.id,
            "survey_template_id": item.survey_template_id,
            "order_index": item.order_index,
            "question_text": item.question_text,
            "question_type": item.question_type,
            "is_standardized": item.is_standardized,
            "required": item.required,
        }

    @router.patch("/admin/surveys/{template_id}/items/{item_id}", status_code=200)
    def update_item(
        template_id: str,
        item_id: str,
        request: UpdateItemRequest,
        principal: Principal = Depends(admin_principal),
    ):
        try:
            item = services.survey_management.update_item(
                item_id,
                question_text=request.question_text,
                order_index=request.order_index,
                required=request.required,
            )
        except PermissionError as exc:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=str(exc)) from exc
        except ValueError as exc:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc
        return {
            "id": item.id,
            "order_index": item.order_index,
            "question_text": item.question_text,
            "question_type": item.question_type,
            "is_standardized": item.is_standardized,
            "required": item.required,
        }

    @router.delete("/admin/surveys/{template_id}/items/{item_id}", status_code=204)
    def delete_item(
        template_id: str,
        item_id: str,
        principal: Principal = Depends(admin_principal),
    ):
        try:
            services.survey_management.delete_item(item_id)
        except PermissionError as exc:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=str(exc)) from exc
        except ValueError as exc:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc

    # ── Student: fetch active templates ──────────────────────────────────────

    @router.get("/surveys/active", status_code=200)
    def list_active_surveys(
        principal: Principal = Depends(student_principal),
    ):
        templates = services.survey_management.list_templates()
        result = []
        for t in templates:
            if not t.is_active:
                continue
            items = services.survey_management.get_items_for_template(t.id)
            result.append({
                "id": t.id,
                "name": t.name,
                "context_trigger": t.context_trigger,
                "version": t.version,
                "items": [
                    {
                        "id": item.id,
                        "order_index": item.order_index,
                        "question_text": item.question_text,
                        "question_type": item.question_type,
                        "required": item.required,
                    }
                    for item in items
                ],
            })
        return result

    @router.get("/surveys/active/{context_trigger}", status_code=200)
    def get_active_survey_by_trigger(
        context_trigger: str,
        principal: Principal = Depends(student_principal),
    ):
        template = services.survey_management.get_template_by_trigger(context_trigger)
        if template is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"No active survey for trigger {context_trigger!r}.",
            )
        items = services.survey_management.get_items_for_template(template.id)
        return {
            "id": template.id,
            "name": template.name,
            "context_trigger": template.context_trigger,
            "version": template.version,
            "items": [
                {
                    "id": item.id,
                    "order_index": item.order_index,
                    "question_text": item.question_text,
                    "question_type": item.question_type,
                    "required": item.required,
                }
                for item in items
            ],
        }

    # ── Student: submit response ──────────────────────────────────────────────

    @router.post("/surveys/{template_id}/respond", status_code=201)
    def submit_response(
        template_id: str,
        request: SubmitSurveyResponseRequest,
        principal: Principal = Depends(student_principal),
    ):
        try:
            record = services.survey_response.submit(
                student_id=principal.id,
                study_session_id=request.study_session_id,
                condition=request.condition,
                template_id=template_id,
                responses=[r.model_dump() for r in request.responses],
            )
        except ValueError as exc:
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail=str(exc)
            ) from exc
        return {
            "survey_response_id": record.id,
            "survey_template_id": record.survey_template_id,
            "survey_version": record.survey_version,
            "submitted_at_utc": record.submitted_at_utc.isoformat(),
        }

    return router
