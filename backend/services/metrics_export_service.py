from __future__ import annotations

from datetime import datetime, timezone
import io

from openpyxl import Workbook


class MetricsExportService:
    """Builds export artifacts for admin analytics downloads."""

    _headers = (
        "student_id",
        "display_name",
        "pretest_score",
        "posttest_score",
        "n_gain",
        "successful_runs",
        "lessons_completed",
        "quiz_attempts_pretest",
        "quiz_attempts_posttest",
        "last_updated_utc",
    )

    def build_n_gain_export(self, rows: list[dict]) -> tuple[str, bytes]:
        workbook = Workbook()
        sheet = workbook.active
        sheet.title = "NGain Metrics"
        sheet.append(list(self._headers))

        for row in rows:
            sheet.append(
                [
                    row.get("student_id"),
                    row.get("display_name"),
                    row.get("pretest_score"),
                    row.get("posttest_score"),
                    row.get("n_gain"),
                    row.get("successful_runs"),
                    row.get("lessons_completed"),
                    row.get("quiz_attempts_pretest"),
                    row.get("quiz_attempts_posttest"),
                    row.get("last_updated_utc"),
                ]
            )

        content = io.BytesIO()
        workbook.save(content)
        content.seek(0)

        timestamp = datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S")
        filename = f"n_gain_metrics_{timestamp}.xlsx"
        return filename, content.getvalue()
