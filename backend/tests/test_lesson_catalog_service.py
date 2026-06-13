import backend.lesson_registry as _lr
from backend.services.lesson_catalog_service import LessonCatalogService


def test_lesson_catalog_sections_include_frontend_fields(_lesson_registry):
    """Catalog service reads from the DB registry (seeded by conftest fixture)."""
    registry = _lr._registry
    assert registry is not None
    sections = LessonCatalogService(registry=registry).list_lesson_sections()

    assert [section["title"] for section in sections] == [
        "Foundations",
        "Dynamic Programming",
        "Monte Carlo Methods",
        "Temporal Difference",
    ]
    foundation_lesson = sections[0]["lessons"][0]
    assert foundation_lesson["id"] == "rl_mdp_core"
    assert foundation_lesson["starter_code"] == ""
    assert foundation_lesson["backend_enabled"] is False
    assert foundation_lesson["exercise"]["tasks"]
    assert foundation_lesson["exercise"]["success_criteria"]
    assert foundation_lesson["concept_video"]["stream_path"].endswith(".mp4")

    first_lesson = sections[1]["lessons"][0]
    assert first_lesson["id"] == "dp_policy_eval"
    assert first_lesson["required_function"] == "policy_evaluation"
    assert first_lesson["environment_name"] == "FrozenLake"
    assert first_lesson["env_params"]["map_name"] == "4x4"
    assert first_lesson["starter_code"]
    assert first_lesson["backend_enabled"] is True
    assert first_lesson["concept_video"]["stream_path"].startswith("/media/concept-videos/")
    assert first_lesson["concept_video"]["stream_path"].endswith(".mp4")
    assert first_lesson["concept_video"]["summary"]
    assert first_lesson["concept_video"]["theory_equation"]
    assert first_lesson["concept_video"]["takeaway_line"]
    assert first_lesson["concept_video"]["theory_verification"]
    assert first_lesson["exercise"]["tasks"]
    assert first_lesson["exercise"]["template_blanks"]
    assert first_lesson["exercise"]["success_criteria"]
