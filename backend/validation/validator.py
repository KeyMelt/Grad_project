from dataclasses import dataclass
from typing import Any

from backend.lessons import get_lesson_definition
from backend.lesson_tests import run_lesson_tests
from backend.user_code import load_user_function


@dataclass(frozen=True)
class ValidationResult:
    is_valid: bool
    errors: list[str]
    test_results: list[dict[str, Any]]


class CodeValidator:
    """Validates the mathematical correctness of student submitted code using unit tests."""
    
    def __init__(self):
        # We would ideally load specific tests per lesson here
        pass
        
    def validate_code(self, submitted_code: str, lesson_id: str) -> ValidationResult:
        """
        Executes the submitted code against lesson-specific contract checks.
        """
        lesson = get_lesson_definition(lesson_id)
        if lesson is None:
            return ValidationResult(
                is_valid=False,
                errors=[f"Unknown lesson_id '{lesson_id}'."],
                test_results=[],
            )

        if not submitted_code.strip():
            return ValidationResult(
                is_valid=False,
                errors=["Submitted code is empty."],
                test_results=[],
            )

        try:
            function = load_user_function(submitted_code, lesson.required_function)
            test_results = run_lesson_tests(lesson_id, function)
            failed_results = [
                result for result in test_results if not result["passed"]
            ]
            if failed_results:
                return ValidationResult(
                    is_valid=False,
                    errors=[
                        f"{len(failed_results)} lesson sample test(s) failed.",
                    ],
                    test_results=test_results,
                )

            return ValidationResult(
                is_valid=True,
                errors=[],
                test_results=test_results,
            )
        except Exception as e:
            return ValidationResult(
                is_valid=False,
                errors=[f"{type(e).__name__}: {e}"],
                test_results=[],
            )
