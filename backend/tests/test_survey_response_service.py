from __future__ import annotations

import pytest

from backend.persistence import Database
from backend.services.survey_management_service import SurveyManagementService
from backend.services.survey_response_service import SurveyResponseService


def _make_services(tmp_path):
    db = Database(f"sqlite:///{tmp_path}/test.db")
    db.create_schema()
    mgmt = SurveyManagementService(database=db)
    mgmt.seed_defaults()
    response_svc = SurveyResponseService(database=db)
    return mgmt, response_svc


def _get_template(mgmt: SurveyManagementService, trigger: str):
    templates = mgmt.list_templates()
    return next(t for t in templates if t.context_trigger == trigger)


# ── Successful submission ─────────────────────────────────────────────────────

def test_submit_response_persists_record(tmp_path):
    mgmt, svc = _make_services(tmp_path)
    template = _get_template(mgmt, "post_video")
    items = mgmt.get_items_for_template(template.id)

    responses = [
        {"item_id": items[0].id, "likert_value": 4},
        {"item_id": items[1].id, "likert_value": 5},
    ]
    record = svc.submit(
        student_id="stu-1",
        study_session_id="sess-1",
        condition="adaptive",
        template_id=template.id,
        responses=responses,
    )
    assert record.id is not None
    assert record.survey_template_id == template.id
    assert record.student_id == "stu-1"
    assert record.condition == "adaptive"


def test_submit_response_persists_item_responses(tmp_path):
    mgmt, svc = _make_services(tmp_path)
    template = _get_template(mgmt, "post_replay")
    items = mgmt.get_items_for_template(template.id)

    responses = [
        {"item_id": items[0].id, "likert_value": 3},
        {"item_id": items[1].id, "likert_value": 2},
    ]
    record = svc.submit(
        student_id="stu-1",
        study_session_id="sess-1",
        condition="control",
        template_id=template.id,
        responses=responses,
    )
    item_responses = svc.list_item_responses(record.id)
    assert len(item_responses) == 2
    likert_values = {ir.likert_value for ir in item_responses}
    assert likert_values == {3, 2}


def test_submit_snapshots_template_version(tmp_path):
    mgmt, svc = _make_services(tmp_path)
    template = _get_template(mgmt, "post_video")
    items = mgmt.get_items_for_template(template.id)
    original_version = template.version

    record = svc.submit(
        student_id="stu-1",
        study_session_id="sess-1",
        condition="adaptive",
        template_id=template.id,
        responses=[{"item_id": items[0].id, "likert_value": 4},
                   {"item_id": items[1].id, "likert_value": 3}],
    )
    assert record.survey_version == original_version


# ── Validation errors ─────────────────────────────────────────────────────────

def test_submit_required_item_missing_raises(tmp_path):
    mgmt, svc = _make_services(tmp_path)
    template = _get_template(mgmt, "post_video")
    items = mgmt.get_items_for_template(template.id)

    # only provide one of the two required items
    with pytest.raises(ValueError, match="no response"):
        svc.submit(
            student_id="stu-1",
            study_session_id="sess-1",
            condition="adaptive",
            template_id=template.id,
            responses=[{"item_id": items[0].id, "likert_value": 4}],
        )


def test_submit_likert_out_of_range_raises(tmp_path):
    mgmt, svc = _make_services(tmp_path)
    template = _get_template(mgmt, "post_video")
    items = mgmt.get_items_for_template(template.id)

    with pytest.raises(ValueError, match="likert_value"):
        svc.submit(
            student_id="stu-1",
            study_session_id="sess-1",
            condition="adaptive",
            template_id=template.id,
            responses=[
                {"item_id": items[0].id, "likert_value": 6},
                {"item_id": items[1].id, "likert_value": 4},
            ],
        )


def test_submit_inactive_survey_raises(tmp_path):
    mgmt, svc = _make_services(tmp_path)
    template = _get_template(mgmt, "post_video")
    mgmt.update_template(template.id, is_active=False)
    items = mgmt.get_items_for_template(template.id)

    with pytest.raises(ValueError, match="not active"):
        svc.submit(
            student_id="stu-1",
            study_session_id="sess-1",
            condition="adaptive",
            template_id=template.id,
            responses=[
                {"item_id": items[0].id, "likert_value": 4},
                {"item_id": items[1].id, "likert_value": 4},
            ],
        )


def test_submit_nonexistent_template_raises(tmp_path):
    mgmt, svc = _make_services(tmp_path)
    with pytest.raises(ValueError, match="not found"):
        svc.submit(
            student_id="stu-1",
            study_session_id="sess-1",
            condition="adaptive",
            template_id="nonexistent",
            responses=[],
        )


# ── List helpers ─────────────────────────────────────────────────────────────

def test_list_by_session_returns_correct_records(tmp_path):
    mgmt, svc = _make_services(tmp_path)
    template = _get_template(mgmt, "post_video")
    items = mgmt.get_items_for_template(template.id)
    responses = [{"item_id": items[0].id, "likert_value": 3},
                 {"item_id": items[1].id, "likert_value": 4}]

    svc.submit(student_id="stu-1", study_session_id="sess-A", condition="adaptive",
               template_id=template.id, responses=responses)
    svc.submit(student_id="stu-2", study_session_id="sess-B", condition="control",
               template_id=template.id, responses=responses)

    results = svc.list_by_session("sess-A")
    assert len(results) == 1
    assert results[0].student_id == "stu-1"


def test_list_all_responses_with_items_returns_all(tmp_path):
    mgmt, svc = _make_services(tmp_path)
    template = _get_template(mgmt, "post_replay")
    items = mgmt.get_items_for_template(template.id)
    responses = [{"item_id": items[0].id, "likert_value": 5},
                 {"item_id": items[1].id, "likert_value": 4}]

    svc.submit(student_id="stu-1", study_session_id="sess-1", condition="adaptive",
               template_id=template.id, responses=responses)
    svc.submit(student_id="stu-2", study_session_id="sess-2", condition="control",
               template_id=template.id, responses=responses)

    all_responses = svc.list_all_responses_with_items()
    assert len(all_responses) == 2
    for resp, item_resps in all_responses:
        assert len(item_resps) == 2
