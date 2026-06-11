from __future__ import annotations

from datetime import datetime, timezone
from threading import Lock

from sqlmodel import select

from backend.config.survey_seeds import SURVEY_SEEDS
from backend.models.survey_template import SurveyTemplate, SurveyTemplateItem
from backend.persistence import Database

_VALID_QUESTION_TYPES = frozenset({"likert_5", "text"})


class SurveyManagementService:
    """Admin-facing CRUD for SurveyTemplate and SurveyTemplateItem records."""

    def __init__(self, *, database: Database) -> None:
        self._lock = Lock()
        self._database = database
        self._database.create_schema()

    # ------------------------------------------------------------------
    # Seeding
    # ------------------------------------------------------------------

    def seed_defaults(self) -> None:
        """Idempotent: creates the three default survey templates if absent.

        Keyed on context_trigger — will not create a duplicate if one already
        exists for a given trigger, even if the name differs.
        """
        with self._lock:
            with self._database.session() as session:
                existing_triggers = {
                    row.context_trigger
                    for row in session.exec(select(SurveyTemplate)).all()
                }

                for name, trigger, description, items in SURVEY_SEEDS:
                    if trigger in existing_triggers:
                        continue

                    template = SurveyTemplate(
                        name=name,
                        context_trigger=trigger,
                        description=description,
                        is_active=True,
                        version=1,
                    )
                    session.add(template)
                    session.flush()  # assigns template.id

                    for order_idx, text, q_type, is_std, required in items:
                        item = SurveyTemplateItem(
                            survey_template_id=template.id,
                            order_index=order_idx,
                            question_text=text,
                            question_type=q_type,
                            is_standardized=is_std,
                            required=required,
                        )
                        session.add(item)

                session.commit()

    # ------------------------------------------------------------------
    # Read
    # ------------------------------------------------------------------

    def list_templates(self) -> list[SurveyTemplate]:
        """Return all templates ordered by context_trigger."""
        with self._lock:
            with self._database.session() as session:
                records = session.exec(
                    select(SurveyTemplate).order_by(SurveyTemplate.context_trigger)
                ).all()
                for r in records:
                    session.expunge(r)
                return list(records)

    def get_template(self, template_id: str) -> SurveyTemplate:
        """Return the template or raise ValueError if not found."""
        with self._lock:
            with self._database.session() as session:
                record = session.get(SurveyTemplate, template_id)
                if record is None:
                    raise ValueError(f"Survey template {template_id!r} not found.")
                session.expunge(record)
                return record

    def get_template_by_trigger(self, context_trigger: str) -> SurveyTemplate | None:
        """Return the active template for the given trigger, or None."""
        with self._lock:
            with self._database.session() as session:
                record = session.exec(
                    select(SurveyTemplate).where(
                        SurveyTemplate.context_trigger == context_trigger,
                        SurveyTemplate.is_active.is_(True),  # type: ignore[attr-defined]
                    )
                ).first()
                if record is not None:
                    session.expunge(record)
                return record

    def get_template_with_items(
        self, template_id: str
    ) -> tuple[SurveyTemplate, list[SurveyTemplateItem]]:
        """Return (template, items) sorted by order_index."""
        with self._lock:
            with self._database.session() as session:
                template = session.get(SurveyTemplate, template_id)
                if template is None:
                    raise ValueError(f"Survey template {template_id!r} not found.")
                items = session.exec(
                    select(SurveyTemplateItem)
                    .where(SurveyTemplateItem.survey_template_id == template_id)
                    .order_by(SurveyTemplateItem.order_index)
                ).all()
                session.expunge(template)
                for item in items:
                    session.expunge(item)
                return template, list(items)

    def get_items_for_template(self, template_id: str) -> list[SurveyTemplateItem]:
        """Return items for the template sorted by order_index."""
        with self._lock:
            with self._database.session() as session:
                items = session.exec(
                    select(SurveyTemplateItem)
                    .where(SurveyTemplateItem.survey_template_id == template_id)
                    .order_by(SurveyTemplateItem.order_index)
                ).all()
                for item in items:
                    session.expunge(item)
                return list(items)

    # ------------------------------------------------------------------
    # Write — template-level
    # ------------------------------------------------------------------

    def update_template(
        self,
        template_id: str,
        *,
        name: str | None = None,
        description: str | None = None,
        is_active: bool | None = None,
    ) -> SurveyTemplate:
        """Update mutable fields on a template.  Bumps version and updated_at_utc."""
        with self._lock:
            with self._database.session() as session:
                record = session.get(SurveyTemplate, template_id)
                if record is None:
                    raise ValueError(f"Survey template {template_id!r} not found.")
                if name is not None:
                    record.name = name
                if description is not None:
                    record.description = description
                if is_active is not None:
                    record.is_active = is_active
                record.version += 1
                record.updated_at_utc = datetime.now(timezone.utc)
                session.add(record)
                session.commit()
                session.refresh(record)
                session.expunge(record)
                return record

    # ------------------------------------------------------------------
    # Write — item-level
    # ------------------------------------------------------------------

    def add_item(
        self,
        template_id: str,
        *,
        question_text: str,
        question_type: str = "likert_5",
        order_index: int,
        required: bool = True,
    ) -> SurveyTemplateItem:
        """Append a new (non-standardized) item to the template."""
        if question_type not in _VALID_QUESTION_TYPES:
            raise ValueError(
                f"question_type must be one of {sorted(_VALID_QUESTION_TYPES)!r}, "
                f"got {question_type!r}"
            )
        with self._lock:
            with self._database.session() as session:
                if session.get(SurveyTemplate, template_id) is None:
                    raise ValueError(f"Survey template {template_id!r} not found.")
                item = SurveyTemplateItem(
                    survey_template_id=template_id,
                    order_index=order_index,
                    question_text=question_text,
                    question_type=question_type,
                    is_standardized=False,
                    required=required,
                )
                session.add(item)
                # bump template version
                template = session.get(SurveyTemplate, template_id)
                if template is not None:
                    template.version += 1
                    template.updated_at_utc = datetime.now(timezone.utc)
                    session.add(template)
                session.commit()
                session.refresh(item)
                session.expunge(item)
                return item

    def update_item(
        self,
        item_id: str,
        *,
        question_text: str | None = None,
        order_index: int | None = None,
        required: bool | None = None,
    ) -> SurveyTemplateItem:
        """Update a non-standardized item.  Raises PermissionError for standardized items."""
        with self._lock:
            with self._database.session() as session:
                item = session.get(SurveyTemplateItem, item_id)
                if item is None:
                    raise ValueError(f"Survey item {item_id!r} not found.")
                if item.is_standardized:
                    raise PermissionError(
                        f"Item {item_id!r} is a standardized instrument item and cannot be edited."
                    )
                if question_text is not None:
                    item.question_text = question_text
                if order_index is not None:
                    item.order_index = order_index
                if required is not None:
                    item.required = required
                session.add(item)
                # bump template version
                template = session.get(SurveyTemplate, item.survey_template_id)
                if template is not None:
                    template.version += 1
                    template.updated_at_utc = datetime.now(timezone.utc)
                    session.add(template)
                session.commit()
                session.refresh(item)
                session.expunge(item)
                return item

    def delete_item(self, item_id: str) -> None:
        """Delete a non-standardized item.  Raises PermissionError for standardized items."""
        with self._lock:
            with self._database.session() as session:
                item = session.get(SurveyTemplateItem, item_id)
                if item is None:
                    raise ValueError(f"Survey item {item_id!r} not found.")
                if item.is_standardized:
                    raise PermissionError(
                        f"Item {item_id!r} is a standardized instrument item and cannot be deleted."
                    )
                template_id = item.survey_template_id
                session.delete(item)
                template = session.get(SurveyTemplate, template_id)
                if template is not None:
                    template.version += 1
                    template.updated_at_utc = datetime.now(timezone.utc)
                    session.add(template)
                session.commit()
