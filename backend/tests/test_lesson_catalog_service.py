from backend.services.lesson_catalog_service import LessonCatalogService


def test_lesson_catalog_sections_include_frontend_fields():
    sections = LessonCatalogService().list_lesson_sections()

    assert [section["title"] for section in sections] == [
        "Dynamic Programming",
        "Monte Carlo Methods",
        "Temporal Difference",
    ]
    first_lesson = sections[0]["lessons"][0]
    assert first_lesson["id"] == "dp_policy_eval"
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
