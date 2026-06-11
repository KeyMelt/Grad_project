from __future__ import annotations

import pytest

from backend.persistence import Database
from backend.services.survey_management_service import SurveyManagementService


def _make_service(tmp_path):
    db = Database(f"sqlite:///{tmp_path}/test.db")
    db.create_schema()
    return SurveyManagementService(database=db)


# ── Seeding ───────────────────────────────────────────────────────────────────

def test_seed_defaults_creates_three_templates(tmp_path):
    svc = _make_service(tmp_path)
    svc.seed_defaults()
    templates = svc.list_templates()
    assert len(templates) == 3
    triggers = {t.context_trigger for t in templates}
    assert triggers == {"post_session", "post_video", "post_replay"}


def test_seed_defaults_is_idempotent(tmp_path):
    svc = _make_service(tmp_path)
    svc.seed_defaults()
    svc.seed_defaults()
    svc.seed_defaults()
    templates = svc.list_templates()
    assert len(templates) == 3


def test_seed_creates_items_for_each_template(tmp_path):
    svc = _make_service(tmp_path)
    svc.seed_defaults()
    for template in svc.list_templates():
        items = svc.get_items_for_template(template.id)
        assert len(items) > 0


def test_seed_post_session_has_standardized_sus_and_tlx_items(tmp_path):
    svc = _make_service(tmp_path)
    svc.seed_defaults()
    templates = svc.list_templates()
    post_session = next(t for t in templates if t.context_trigger == "post_session")
    items = svc.get_items_for_template(post_session.id)
    standardized = [i for i in items if i.is_standardized]
    assert len(standardized) == 16  # 10 SUS + 6 TLX


def test_seed_micro_survey_items_are_not_standardized(tmp_path):
    svc = _make_service(tmp_path)
    svc.seed_defaults()
    templates = svc.list_templates()
    for template in templates:
        if template.context_trigger in ("post_video", "post_replay"):
            items = svc.get_items_for_template(template.id)
            assert all(not i.is_standardized for i in items)


# ── Update template ───────────────────────────────────────────────────────────

def test_update_template_name_succeeds(tmp_path):
    svc = _make_service(tmp_path)
    svc.seed_defaults()
    template = svc.list_templates()[0]
    updated = svc.update_template(template.id, name="Renamed Survey")
    assert updated.name == "Renamed Survey"


def test_update_template_is_active_succeeds(tmp_path):
    svc = _make_service(tmp_path)
    svc.seed_defaults()
    template = svc.list_templates()[0]
    updated = svc.update_template(template.id, is_active=False)
    assert updated.is_active is False


def test_update_template_bumps_version(tmp_path):
    svc = _make_service(tmp_path)
    svc.seed_defaults()
    template = svc.list_templates()[0]
    original_version = template.version
    updated = svc.update_template(template.id, description="New description")
    assert updated.version == original_version + 1


def test_update_nonexistent_template_raises(tmp_path):
    svc = _make_service(tmp_path)
    with pytest.raises(ValueError, match="not found"):
        svc.update_template("nonexistent-id", name="x")


# ── Update item ───────────────────────────────────────────────────────────────

def test_update_item_text_succeeds_for_non_standardized(tmp_path):
    svc = _make_service(tmp_path)
    svc.seed_defaults()
    templates = svc.list_templates()
    post_video = next(t for t in templates if t.context_trigger == "post_video")
    items = svc.get_items_for_template(post_video.id)
    item = items[0]
    assert not item.is_standardized
    updated = svc.update_item(item.id, question_text="Updated question text.")
    assert updated.question_text == "Updated question text."


def test_update_item_text_raises_for_standardized(tmp_path):
    svc = _make_service(tmp_path)
    svc.seed_defaults()
    templates = svc.list_templates()
    post_session = next(t for t in templates if t.context_trigger == "post_session")
    items = svc.get_items_for_template(post_session.id)
    standardized_item = next(i for i in items if i.is_standardized)
    with pytest.raises(PermissionError):
        svc.update_item(standardized_item.id, question_text="Tampering with SUS.")


def test_update_item_bumps_template_version(tmp_path):
    svc = _make_service(tmp_path)
    svc.seed_defaults()
    templates = svc.list_templates()
    post_video = next(t for t in templates if t.context_trigger == "post_video")
    original_version = post_video.version
    items = svc.get_items_for_template(post_video.id)
    svc.update_item(items[0].id, question_text="Changed.")
    updated_template = svc.get_template(post_video.id)
    assert updated_template.version == original_version + 1


# ── Delete item ───────────────────────────────────────────────────────────────

def test_delete_item_raises_for_standardized(tmp_path):
    svc = _make_service(tmp_path)
    svc.seed_defaults()
    templates = svc.list_templates()
    post_session = next(t for t in templates if t.context_trigger == "post_session")
    items = svc.get_items_for_template(post_session.id)
    standardized_item = next(i for i in items if i.is_standardized)
    with pytest.raises(PermissionError):
        svc.delete_item(standardized_item.id)


def test_delete_item_succeeds_for_non_standardized(tmp_path):
    svc = _make_service(tmp_path)
    svc.seed_defaults()
    templates = svc.list_templates()
    post_video = next(t for t in templates if t.context_trigger == "post_video")
    items_before = svc.get_items_for_template(post_video.id)
    non_std_item = items_before[0]
    svc.delete_item(non_std_item.id)
    items_after = svc.get_items_for_template(post_video.id)
    assert len(items_after) == len(items_before) - 1


# ── Add item ──────────────────────────────────────────────────────────────────

def test_add_item_appends_to_template(tmp_path):
    svc = _make_service(tmp_path)
    svc.seed_defaults()
    templates = svc.list_templates()
    post_replay = next(t for t in templates if t.context_trigger == "post_replay")
    items_before = svc.get_items_for_template(post_replay.id)
    svc.add_item(
        post_replay.id,
        question_text="New custom question.",
        question_type="text",
        order_index=99,
        required=False,
    )
    items_after = svc.get_items_for_template(post_replay.id)
    assert len(items_after) == len(items_before) + 1
    new_item = next(i for i in items_after if i.order_index == 99)
    assert new_item.question_text == "New custom question."
    assert not new_item.is_standardized


def test_add_item_invalid_question_type_raises(tmp_path):
    svc = _make_service(tmp_path)
    svc.seed_defaults()
    template = svc.list_templates()[0]
    with pytest.raises(ValueError, match="question_type"):
        svc.add_item(template.id, question_text="q", question_type="radio", order_index=1)


# ── get_template_by_trigger ───────────────────────────────────────────────────

def test_get_template_by_trigger_returns_active_template(tmp_path):
    svc = _make_service(tmp_path)
    svc.seed_defaults()
    template = svc.get_template_by_trigger("post_video")
    assert template is not None
    assert template.context_trigger == "post_video"


def test_get_template_by_trigger_returns_none_when_inactive(tmp_path):
    svc = _make_service(tmp_path)
    svc.seed_defaults()
    template = svc.get_template_by_trigger("post_video")
    assert template is not None
    svc.update_template(template.id, is_active=False)
    result = svc.get_template_by_trigger("post_video")
    assert result is None
